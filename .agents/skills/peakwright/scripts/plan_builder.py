#!/usr/bin/env python3
"""Build a first-draft weekly elite training and meal plan.

The output is a coaching draft that should be individualized by the agent.
It is deterministic and dependency-free so the skill has a reliable baseline.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Literal

from athlete_targets import Goal, Load, Phase, Sex, Targets, calculate_targets


Sport = Literal["strength", "hypertrophy", "endurance", "field-court", "combat", "hybrid"]
Diet = Literal["omnivore", "mediterranean", "pescatarian", "vegetarian", "vegan"]


@dataclass(frozen=True)
class Session:
    day: str
    title: str
    stress: str
    priority: int
    details: tuple[str, ...]


@dataclass(frozen=True)
class MealTemplate:
    breakfast: str
    lunch: str
    dinner: str
    snack: str


DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


SESSION_BANK: dict[Sport, tuple[tuple[str, str, int, tuple[str, ...]], ...]] = {
    "strength": (
        ("Squat strength + posterior chain", "high", 1, ("Back squat 4x3-5 @ RPE 7-8", "Romanian deadlift 3x6-8", "Split squat 3x8/side", "Loaded carry 4x30 m")),
        ("Bench strength + upper back", "moderate", 2, ("Bench press 4x3-5 @ RPE 7-8", "Weighted pull-up or row 4x5-8", "Incline DB press 3x8-10", "Face pull 3x15")),
        ("Recovery aerobic + mobility", "low", 6, ("Zone 2 bike or walk 30-45 min", "Hips, t-spine, ankles 12 min", "Easy trunk circuit 2 rounds")),
        ("Deadlift strength + trunk", "high", 3, ("Deadlift 4x2-4 @ RPE 7-8", "Front squat 3x5", "Hamstring curl 3x10-12", "Anti-rotation press 3x12/side")),
        ("Overhead press + hypertrophy", "moderate", 4, ("Overhead press 4x4-6", "Chest-supported row 4x8-10", "Dips or push-ups 3x8-12", "Arms 2-3x10-15")),
        ("Conditioning + prehab", "low", 5, ("Sled push or incline walk intervals 8-10 rounds", "Shoulder and hip prehab 15 min", "Easy mobility cooldown")),
        ("Rest", "rest", 7, ("Full rest or 20-30 min easy walk",)),
    ),
    "hypertrophy": (
        ("Push hypertrophy", "moderate", 1, ("Press variation 4x6-10", "Incline press 3x8-12", "Lateral raise 4x12-20", "Triceps 3x10-15")),
        ("Pull hypertrophy", "moderate", 2, ("Pull-up or pulldown 4x6-10", "Row 4x8-12", "Rear delt 3x15-20", "Biceps 3x10-15")),
        ("Leg hypertrophy", "high", 3, ("Squat or leg press 4x6-10", "Hip hinge 3x8-12", "Leg curl 3x10-15", "Calves 4x8-15")),
        ("Recovery", "low", 6, ("Zone 2 25-40 min", "Mobility 15 min", "Optional weak-point pump 2 easy sets")),
        ("Upper specialization", "moderate", 4, ("Weak-point press/pull superset 4 rounds", "Upper back 4x10-15", "Delts/arms 4x12-20")),
        ("Lower specialization", "moderate", 5, ("Single-leg squat 3x8-12/side", "Glute bridge 4x8-12", "Hamstring curl 3x12-15", "Core 3 rounds")),
        ("Rest", "rest", 7, ("Full rest or easy walk",)),
    ),
    "endurance": (
        ("Strength foundation", "moderate", 3, ("Trap-bar deadlift or squat 3x3-5", "Step-up 3x6/side", "Row 3x8", "Calf/foot strength 3x12")),
        ("Threshold intervals", "high", 1, ("Warm-up 15 min", "3-5 x 6-10 min threshold with 2-3 min easy", "Cooldown 10 min")),
        ("Zone 2 aerobic", "low", 4, ("Zone 2 45-75 min", "Strides 4-6 x 15 sec if running", "Mobility 10 min")),
        ("Strength maintenance + mobility", "moderate", 5, ("Squat pattern 3x5", "Hinge 3x6", "Pull 3x8", "Mobility 15 min")),
        ("VO2 or hills", "high", 2, ("Warm-up 15 min", "5-8 x 2-4 min hard with equal easy recovery", "Cooldown 10 min")),
        ("Long aerobic", "moderate", 6, ("Long zone 2 session 75-150 min", "Fuel during if >75 min", "Post-session carb/protein meal")),
        ("Rest", "rest", 7, ("Full rest or gentle walk",)),
    ),
    "field-court": (
        ("Lower strength + acceleration", "high", 1, ("Acceleration 6-10 x 10-20 m full rest", "Trap-bar deadlift 4x3-5", "Rear-foot elevated split squat 3x6/side", "Nordic or hamstring curl 3x5-8")),
        ("Tempo aerobic + mobility", "low", 5, ("Tempo runs or bike 25-40 min", "Adductor/hip mobility 12 min", "Foot/ankle prep 8 min")),
        ("Upper strength + change of direction", "moderate", 3, ("COD technique 6-8 reps/side", "Bench or push press 4x4-6", "Pull-up/row 4x6-10", "Anti-rotation core 3x10/side")),
        ("Repeated sprint conditioning", "high", 2, ("Warm-up and sprint drills", "2-3 sets of 5 x 20-30 m with controlled rest", "Cooldown walk and mobility")),
        ("Total-body power", "moderate", 4, ("Jumps 4x3", "Med-ball throws 5x3", "Front squat 3x3 @ crisp speed", "Lateral lunge 3x8/side")),
        ("Skill + recovery", "low", 6, ("Low-intensity skill 30-45 min", "Zone 2 20-30 min optional", "Mobility 15 min")),
        ("Rest", "rest", 7, ("Full rest",)),
    ),
    "combat": (
        ("Lower strength + alactic power", "high", 1, ("Jumps 4x3", "Front squat 4x3-5", "Hip hinge 3x5-8", "Loaded carry 5x20-30 m")),
        ("Skill volume + zone 2", "moderate", 4, ("Technical drilling 45-75 min", "Zone 2 20-40 min", "Mobility 10 min")),
        ("Upper strength + grip", "moderate", 3, ("Weighted pull-up 4x3-6", "Press variation 4x4-6", "Rows 3x8-10", "Grip finisher 4 rounds")),
        ("Intervals", "high", 2, ("Assault bike/rower 6-10 x 45 sec hard / 75 sec easy", "Neck/trunk circuit 3 rounds", "Cooldown")),
        ("Total-body power", "moderate", 5, ("Med-ball throws 6x3", "Kettlebell swing 4x8", "Split squat 3x6/side", "Rotational core 3x10/side")),
        ("Sparring or technical practice", "high", 6, ("Sparring/rolling as programmed", "Keep strength accessories low", "Post-session refuel priority")),
        ("Rest", "rest", 7, ("Full rest",)),
    ),
    "hybrid": (
        ("Full-body strength", "high", 1, ("Squat or trap-bar deadlift 4x3-5", "Press 4x4-6", "Pull 4x6-8", "Carry 4x30 m")),
        ("Zone 2 aerobic", "low", 4, ("Zone 2 40-60 min", "Mobility 10-15 min")),
        ("Power + speed", "high", 2, ("Jumps 4x3", "Sprints 6-8 x 10-20 m", "Olympic-lift derivative or swing 5x3", "Core 3 rounds")),
        ("Hypertrophy support", "moderate", 5, ("Single-leg 3x8/side", "Upper push/pull 3x8-12", "Posterior chain 3x10", "Prehab 10 min")),
        ("Conditioning intervals", "high", 3, ("Warm-up", "6-10 x 1 min hard / 1-2 min easy", "Cooldown")),
        ("Skill or recovery", "low", 6, ("Sport skill or easy aerobic 30-45 min", "Mobility 15 min")),
        ("Rest", "rest", 7, ("Full rest",)),
    ),
}


MEALS: dict[Diet, tuple[MealTemplate, ...]] = {
    "omnivore": (
        MealTemplate("Greek yogurt, oats, berries, honey", "Chicken rice bowl with vegetables and olive oil", "Lean beef or turkey, potatoes, salad", "Cottage cheese, banana, nuts"),
        MealTemplate("Eggs, toast, fruit", "Turkey wrap, rice cakes, vegetables", "Salmon, rice, greens", "Whey or yogurt smoothie"),
    ),
    "mediterranean": (
        MealTemplate("Greek yogurt, oats, berries, walnuts", "Chicken or chickpea grain bowl with olive oil", "Fish, potatoes, Greek salad", "Fruit, kefir or hummus with pita"),
        MealTemplate("Eggs, sourdough, tomatoes", "Tuna or lentil rice bowl", "Turkey meatballs or tofu, pasta, vegetables", "Yogurt, honey, nuts"),
    ),
    "pescatarian": (
        MealTemplate("Eggs, oats, fruit", "Tuna rice bowl with vegetables", "Salmon, potatoes, salad", "Greek yogurt or soy yogurt, berries"),
        MealTemplate("Greek yogurt, granola, fruit", "Shrimp pasta with vegetables", "Tofu stir-fry with rice", "Protein smoothie"),
    ),
    "vegetarian": (
        MealTemplate("Greek yogurt, oats, berries", "Tofu or egg rice bowl", "Lentil pasta with vegetables", "Cottage cheese, fruit, nuts"),
        MealTemplate("Egg scramble, toast, fruit", "Tempeh grain bowl", "Bean chili with rice", "Protein smoothie"),
    ),
    "vegan": (
        MealTemplate("Soy yogurt, oats, berries, seeds", "Tofu rice bowl with vegetables", "Lentil pasta or bean chili", "Pea/rice protein smoothie"),
        MealTemplate("Tofu scramble, toast, fruit", "Tempeh quinoa bowl", "Seitan or TVP tacos with potatoes", "Soy milk smoothie with banana"),
    ),
}


GROCERIES: dict[Diet, tuple[str, ...]] = {
    "omnivore": ("chicken/turkey", "eggs", "Greek yogurt/cottage cheese", "fish", "lean beef", "rice/oats/potatoes/pasta", "fruit", "vegetables", "olive oil", "nuts"),
    "mediterranean": ("fish", "chicken or legumes", "Greek yogurt", "eggs", "rice/oats/potatoes/whole grains", "fruit", "vegetables", "olive oil", "nuts", "hummus"),
    "pescatarian": ("fish", "shrimp", "eggs", "Greek yogurt or soy yogurt", "tofu/tempeh", "rice/oats/potatoes/pasta", "fruit", "vegetables", "olive oil", "nuts"),
    "vegetarian": ("eggs", "Greek yogurt/cottage cheese", "tofu/tempeh", "lentils/beans", "seitan", "rice/oats/potatoes/pasta", "fruit", "vegetables", "olive oil", "nuts"),
    "vegan": ("tofu", "tempeh", "seitan or TVP", "lentils/beans", "soy milk/yogurt", "rice/oats/potatoes/pasta", "fruit", "vegetables", "olive oil", "nuts/seeds"),
}


def week_for(sport: Sport, sessions_per_week: int) -> tuple[Session, ...]:
    selected = tuple(
        Session(
            day=DAYS[index],
            title=title if priority <= sessions_per_week or stress == "rest" else "Recovery / mobility",
            stress=stress if priority <= sessions_per_week or stress == "rest" else "low",
            priority=priority,
            details=details if priority <= sessions_per_week or stress == "rest" else ("Easy walk or bike 20-40 min", "Mobility 10-15 min", "No hard conditioning"),
        )
        for index, (title, stress, priority, details) in enumerate(SESSION_BANK[sport])
    )
    return selected


def meal_line(index: int, day: Session, diet: Diet, targets: Targets) -> tuple[str, ...]:
    template = MEALS[diet][index % len(MEALS[diet])]
    macro_day = targets.training_day if day.stress in {"high", "moderate"} else targets.rest_day
    fueling_by_stress = {
        "high": "Add pre-session carbs and post-session protein/carbs.",
        "moderate": "Add a carb serving before or after training based on session timing.",
        "low": "Keep carbs moderate and focus on protein, produce, and hydration.",
        "rest": "No special workout fueling; keep protein steady and hydrate.",
    }
    return (
        f"Target: {macro_day.calories} kcal, P {macro_day.protein_g} g, C {macro_day.carbs_g} g, F {macro_day.fat_g} g.",
        f"Breakfast: {template.breakfast}.",
        f"Lunch: {template.lunch}.",
        f"Dinner: {template.dinner}.",
        f"Snack: {template.snack}.",
        f"Fueling: {fueling_by_stress[day.stress]}",
    )


def progression_line(day: Session) -> str:
    if day.stress == "rest":
        return "- Recovery target: protect sleep, steps, hydration, and appetite."
    return "- Progression: keep quality high; progress one variable next week if target RPE and technique are stable."


def format_plan(
    sport: Sport,
    goal: Goal,
    load: Load,
    phase: Phase,
    diet: Diet,
    session_min: int,
    sessions_per_week: int,
    targets: Targets,
) -> str:
    week = week_for(sport, sessions_per_week)
    header = (
        "# Elite Training And Meal Plan Draft",
        "",
        f"Sport profile: {sport}",
        f"Goal: {goal}",
        f"Phase: {phase}",
        f"Training load: {load}",
        f"Session length target: {session_min} min",
        f"Weekly focus: {targets.weekly_focus}",
        "",
        "## Calorie And Macro Targets",
        f"Estimated BMR: {targets.bmr} kcal/day",
        f"Estimated TDEE: {targets.estimated_tdee} kcal/day",
        f"Training day: {targets.training_day.calories} kcal | P {targets.training_day.protein_g} g | C {targets.training_day.carbs_g} g | F {targets.training_day.fat_g}",
        f"Rest day: {targets.rest_day.calories} kcal | P {targets.rest_day.protein_g} g | C {targets.rest_day.carbs_g} g | F {targets.rest_day.fat_g}",
        "",
        "## Weekly Training Calendar",
    )
    training_lines = tuple(
        line
        for day in week
        for line in (
            f"### {day.day}: {day.title} ({day.stress})",
            *(f"- {detail}" for detail in day.details),
            progression_line(day),
            "",
        )
    )
    meal_header = ("## Meal Plan",)
    meal_lines = tuple(
        line
        for index, day in enumerate(week)
        for line in (
            f"### {day.day}",
            *meal_line(index, day, diet, targets),
            "",
        )
    )
    grocery_lines = (
        "## Grocery List",
        *(f"- {item}" for item in GROCERIES[diet]),
        "- electrolytes or sports drink for long/hot/high-output sessions",
        "",
        "## Adjustment Rules",
        f"- {targets.deload_rule}",
        "- If bodyweight trend misses the goal for 2 weeks, adjust calories by 150-250 kcal/day.",
        "- If two similar sessions regress, reduce accessory volume 10-20% and protect sleep.",
        "- If pain changes movement quality, replace the exercise and seek qualified review.",
    )
    caution_lines = ("", "## Cautions", *(f"- {warning}" for warning in targets.cautions)) if targets.cautions else ()
    return "\n".join(header + training_lines + meal_header + meal_lines + grocery_lines + caution_lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sport", choices=("strength", "hypertrophy", "endurance", "field-court", "combat", "hybrid"), required=True)
    parser.add_argument("--weight-kg", type=float, required=True)
    parser.add_argument("--height-cm", type=float, required=True)
    parser.add_argument("--age", type=int, required=True)
    parser.add_argument("--sex", choices=("male", "female"), required=True)
    parser.add_argument("--goal", choices=("performance", "fat_loss", "muscle_gain", "recomposition"), required=True)
    parser.add_argument("--training-load", choices=("low", "moderate", "high", "elite"), required=True)
    parser.add_argument("--sessions-per-week", type=int, required=True)
    parser.add_argument("--phase", choices=("base", "build", "peak", "competition", "deload"), default="build")
    parser.add_argument("--diet", choices=("omnivore", "mediterranean", "pescatarian", "vegetarian", "vegan"), default="mediterranean")
    parser.add_argument("--session-min", type=int, default=75)
    return parser.parse_args()


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
    print(
        format_plan(
            sport=args.sport,
            goal=args.goal,
            load=args.training_load,
            phase=args.phase,
            diet=args.diet,
            session_min=args.session_min,
            sessions_per_week=args.sessions_per_week,
            targets=targets,
        )
    )


if __name__ == "__main__":
    main()
