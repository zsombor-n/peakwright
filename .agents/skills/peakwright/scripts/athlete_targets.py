#!/usr/bin/env python3
"""Calculate athlete calorie, macro, and training-load targets.

This helper is intentionally simple and dependency-free. It produces planning
anchors, not medical advice.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from typing import Literal


Sex = Literal["male", "female"]
Goal = Literal["performance", "fat_loss", "muscle_gain", "recomposition"]
Load = Literal["low", "moderate", "high", "elite"]
Phase = Literal["base", "build", "peak", "competition", "deload"]


@dataclass(frozen=True)
class MacroDay:
    calories: int
    protein_g: int
    carbs_g: int
    fat_g: int
    protein_g_per_kg: float
    carbs_g_per_kg: float
    fat_percent: int


@dataclass(frozen=True)
class Targets:
    bmr: int
    estimated_tdee: int
    training_day: MacroDay
    rest_day: MacroDay
    weekly_focus: str
    deload_rule: str
    cautions: tuple[str, ...]


ACTIVITY_MULTIPLIERS: dict[Load, float] = {
    "low": 1.45,
    "moderate": 1.6,
    "high": 1.75,
    "elite": 1.9,
}

CARB_RANGES: dict[Load, tuple[float, float]] = {
    "low": (3.0, 5.0),
    "moderate": (5.0, 7.0),
    "high": (6.0, 10.0),
    "elite": (8.0, 12.0),
}

GOAL_CALORIE_OFFSETS: dict[Goal, int] = {
    "performance": 0,
    "fat_loss": -400,
    "muscle_gain": 250,
    "recomposition": -150,
}

PHASE_FOCUS: dict[Phase, str] = {
    "base": "Build aerobic capacity, movement quality, tissue tolerance, and general strength.",
    "build": "Increase sport-specific strength, power, intensity, and workload while protecting recovery.",
    "peak": "Preserve intensity, reduce excess volume, sharpen sport-specific outputs, and arrive fresh.",
    "competition": "Maintain strength and power with low fatigue; prioritize skill, tactics, and recovery.",
    "deload": "Reduce volume 30-50%, keep light technique work, and restore sleep, appetite, and readiness.",
}


def mifflin_st_jeor(weight_kg: float, height_cm: float, age: int, sex: Sex) -> float:
    sex_offset = 5 if sex == "male" else -161
    return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + sex_offset


def protein_per_kg(goal: Goal, load: Load) -> float:
    if goal == "fat_loss":
        return 2.0
    if goal == "muscle_gain":
        return 1.9
    if goal == "recomposition":
        return 1.9
    return 1.7 if load in {"high", "elite"} else 1.6


def calorie_target(tdee: float, goal: Goal, load: Load) -> float:
    offset = GOAL_CALORIE_OFFSETS[goal]
    if goal == "fat_loss" and load in {"high", "elite"}:
        offset = -300
    return tdee + offset


def carb_target_per_kg(load: Load, phase: Phase, is_rest_day: bool) -> float:
    low, high = CARB_RANGES[load]
    midpoint = (low + high) / 2
    phase_adjustment = {
        "base": -0.5,
        "build": 0.0,
        "peak": 0.5,
        "competition": 0.25,
        "deload": -1.0,
    }[phase]
    rest_adjustment = -1.5 if is_rest_day else 0.0
    return max(2.0, min(high, midpoint + phase_adjustment + rest_adjustment))


def macro_day(
    calories: float,
    weight_kg: float,
    goal: Goal,
    load: Load,
    phase: Phase,
    is_rest_day: bool,
) -> MacroDay:
    protein_g_per_kg = protein_per_kg(goal, load)
    carbs_g_per_kg = carb_target_per_kg(load, phase, is_rest_day)
    protein_g = protein_g_per_kg * weight_kg
    carbs_g = carbs_g_per_kg * weight_kg
    fat_kcal = calories - (protein_g * 4) - (carbs_g * 4)
    minimum_fat_kcal = calories * 0.2

    if fat_kcal < minimum_fat_kcal:
        adjusted_carbs_g = max(1.5 * weight_kg, (calories - minimum_fat_kcal - (protein_g * 4)) / 4)
        carbs_g = adjusted_carbs_g
        carbs_g_per_kg = carbs_g / weight_kg
        fat_kcal = calories - (protein_g * 4) - (carbs_g * 4)

    fat_g = max(0.0, fat_kcal / 9)
    fat_percent = int(round((fat_g * 9 / calories) * 100)) if calories else 0

    return MacroDay(
        calories=int(round(calories)),
        protein_g=int(round(protein_g)),
        carbs_g=int(round(carbs_g)),
        fat_g=int(round(fat_g)),
        protein_g_per_kg=round(protein_g_per_kg, 2),
        carbs_g_per_kg=round(carbs_g_per_kg, 2),
        fat_percent=fat_percent,
    )


def cautions(goal: Goal, load: Load, sessions_per_week: int, training_day: MacroDay) -> tuple[str, ...]:
    base = ()
    volume_warning = (
        "High training volume plus an energy deficit raises low-energy-availability risk; monitor sleep, libido, mood, performance, and injury symptoms.",
    )
    fat_warning = (
        "Fat target is near the lower boundary; avoid chronic intakes below about 20% of energy unless supervised.",
    )
    session_warning = (
        "Seven or more sessions weekly should include planned low-intensity recovery work and at least one low-load day.",
    )
    with_volume = base + volume_warning if goal == "fat_loss" and load in {"high", "elite"} else base
    with_fat = with_volume + fat_warning if training_day.fat_percent <= 20 else with_volume
    with_sessions = with_fat + session_warning if sessions_per_week >= 7 else with_fat
    return with_sessions


def calculate_targets(
    weight_kg: float,
    height_cm: float,
    age: int,
    sex: Sex,
    goal: Goal,
    load: Load,
    sessions_per_week: int,
    phase: Phase,
) -> Targets:
    bmr = mifflin_st_jeor(weight_kg, height_cm, age, sex)
    tdee = bmr * ACTIVITY_MULTIPLIERS[load]
    training_calories = calorie_target(tdee, goal, load)
    rest_calories = training_calories - (200 if goal != "muscle_gain" else 100)
    training_day = macro_day(training_calories, weight_kg, goal, load, phase, False)
    rest_day = macro_day(rest_calories, weight_kg, goal, load, phase, True)
    return Targets(
        bmr=int(round(bmr)),
        estimated_tdee=int(round(tdee)),
        training_day=training_day,
        rest_day=rest_day,
        weekly_focus=PHASE_FOCUS[phase],
        deload_rule="Deload after 3-5 hard weeks or sooner if performance drops for 2 sessions, soreness persists, or sleep/readiness declines.",
        cautions=cautions(goal, load, sessions_per_week, training_day),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weight-kg", type=float, required=True)
    parser.add_argument("--height-cm", type=float, required=True)
    parser.add_argument("--age", type=int, required=True)
    parser.add_argument("--sex", choices=("male", "female"), required=True)
    parser.add_argument("--goal", choices=("performance", "fat_loss", "muscle_gain", "recomposition"), required=True)
    parser.add_argument("--training-load", choices=("low", "moderate", "high", "elite"), required=True)
    parser.add_argument("--sessions-per-week", type=int, required=True)
    parser.add_argument("--phase", choices=("base", "build", "peak", "competition", "deload"), default="build")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of Markdown.")
    return parser.parse_args()


def markdown(targets: Targets) -> str:
    lines = (
        f"BMR: {targets.bmr} kcal/day",
        f"Estimated TDEE: {targets.estimated_tdee} kcal/day",
        "",
        "Training day:",
        f"- {targets.training_day.calories} kcal",
        f"- Protein: {targets.training_day.protein_g} g ({targets.training_day.protein_g_per_kg} g/kg)",
        f"- Carbs: {targets.training_day.carbs_g} g ({targets.training_day.carbs_g_per_kg} g/kg)",
        f"- Fat: {targets.training_day.fat_g} g ({targets.training_day.fat_percent}% kcal)",
        "",
        "Rest day:",
        f"- {targets.rest_day.calories} kcal",
        f"- Protein: {targets.rest_day.protein_g} g ({targets.rest_day.protein_g_per_kg} g/kg)",
        f"- Carbs: {targets.rest_day.carbs_g} g ({targets.rest_day.carbs_g_per_kg} g/kg)",
        f"- Fat: {targets.rest_day.fat_g} g ({targets.rest_day.fat_percent}% kcal)",
        "",
        f"Weekly focus: {targets.weekly_focus}",
        f"Deload rule: {targets.deload_rule}",
    )
    caution_lines = tuple(f"- {warning}" for warning in targets.cautions)
    return "\n".join(lines + (("", "Cautions:") + caution_lines if caution_lines else ()))


def main() -> None:
    args = parse_args()
    targets = calculate_targets(
        weight_kg=args.weight_kg,
        height_cm=args.height_cm,
        age=args.age,
        sex=args.sex,
        goal=args.goal,
        load=args.training_load,
        sessions_per_week=args.sessions_per_week,
        phase=args.phase,
    )
    if args.json:
        print(json.dumps(asdict(targets), indent=2))
        return
    print(markdown(targets))


if __name__ == "__main__":
    main()
