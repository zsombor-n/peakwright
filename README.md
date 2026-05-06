# PeakWright

> Most AI fitness plans are generic. They sound confident, but they do not coach.

I wanted a skill that makes Codex and Claude Code behave more like a real performance staff: a strength coach who understands programming, a nutrition planner who can turn macros into food, and a careful assistant who knows when not to guess.

**PeakWright is that skill.** It turns an AI agent into an evidence-informed trainer and meal-planning assistant for serious training. Not a magic transformation plan. Not a random list of exercises. A structured coaching workflow: intake, constraints, goals, training phase, workout calendar, session details, macros, meals, grocery list, recovery monitoring, and adjustment rules.

The point is simple: if you already ask AI for workouts or meal plans, this makes the answer much better.

It gives the agent a process.

## Quick Start

Ask your agent:

```text
Use $peakwright to build me a complete training and meal plan.
```

Or give it a real profile:

```text
Use $peakwright to create a 4-week recomposition plan.

I am 27, male, 184 cm, 82 kg. I play soccer twice a week, lift 3 days,
have a full gym, want to get faster and leaner, prefer Mediterranean food,
and have no current injuries.
```

The skill will gather missing details, screen for red flags, calculate planning targets, and produce a coach-style plan instead of a generic prompt response.

## Install

Requirements:

- Codex or Claude Code
- Git
- Python 3 if you want to run the included calculators directly

### Codex

Install the skill folder into Codex:

```bash
mkdir -p ~/.codex/skills
cp -R .agents/skills/peakwright ~/.codex/skills/
```

Then invoke:

```text
$peakwright
```

### Claude Code

Install the same skill folder into Claude Code:

```bash
mkdir -p ~/.claude/skills
cp -R .agents/skills/peakwright ~/.claude/skills/
```

Then invoke:

```text
$peakwright
```

### Team Repo Mode

Keep this repository layout if you want teammates or other agents to use the skill from the project:

```text
.agents/skills/peakwright
.claude/skills/peakwright
```

This repo uses `.agents/skills/peakwright` as the canonical skill and `.claude/skills/peakwright` as a pointer to it.

## See It Work

```text
You:    Use $peakwright. Build a weekly plan for a field athlete.
        27, male, 184 cm, 82 kg, full gym, 6 sessions/week,
        performance goal, Mediterranean diet.

Agent:  Athlete snapshot:
        - Goal: field/court performance
        - Phase: build
        - Training load: high
        - Estimated TDEE: 3220 kcal/day

        Weekly training:
        Monday: lower strength + acceleration
        Tuesday: tempo aerobic + mobility
        Wednesday: upper strength + change of direction
        Thursday: repeated sprint conditioning
        Friday: total-body power
        Saturday: skill + recovery
        Sunday: rest

        Nutrition:
        Training day: 3220 kcal, 139 g protein, 505 g carbs, 72 g fat
        Rest day: 3020 kcal, 139 g protein, 465 g carbs, 67 g fat

        Meals:
        Breakfast: Greek yogurt, oats, berries, walnuts
        Lunch: chicken or chickpea grain bowl with olive oil
        Dinner: fish, potatoes, Greek salad
        Snack: fruit, kefir or hummus with pita

        Adjustment rule:
        Deload after 3-5 hard weeks or sooner if performance drops,
        soreness persists, or sleep/readiness declines.
```

The exact plan changes based on the athlete, sport, training phase, equipment, food preferences, and constraints.

## What Makes It Different

Most workout prompts produce isolated advice:

- a few exercises
- a rough macro target
- a motivational paragraph
- no progression
- no recovery logic
- no intake
- no safety boundary

PeakWright gives the agent a coaching system:

| Part | What it does |
|------|--------------|
| `SKILL.md` | The main coaching workflow: intake, safety, planning rules, output format |
| `planning-models.md` | Training models for strength, hypertrophy, endurance, field/court, combat, and hybrid athletes |
| `meal-planning.md` | Macro planning, meal timing, diet styles, substitutions, grocery list structure |
| `evidence.md` | Source map for sports nutrition, training guidelines, APIs, and related open-source projects |
| `athlete_targets.py` | Dependency-free BMR, TDEE, training-day, and rest-day macro calculator |
| `plan_builder.py` | Deterministic first-draft weekly training and meal plan generator |

## Who This Is For

- Athletes who want more structured plans from AI
- Coaches who want faster first drafts
- Trainers building client templates
- Founders building fitness, nutrition, or coaching products
- Codex and Claude Code users who want a real domain skill, not just another prompt
- Anyone tired of generic AI workout plans

## What It Can Build

Training plans:

- Strength
- Hypertrophy
- Endurance
- Field and court sports
- Combat sports
- Hybrid training
- Recomposition
- Fat loss while preserving performance
- Muscle gain
- Deload weeks
- Return-to-training drafts

Nutrition plans:

- Training-day and rest-day macros
- Omnivore meal plans
- Mediterranean meal plans
- Pescatarian meal plans
- Vegetarian meal plans
- Vegan meal plans
- Grocery lists
- Meal substitutions
- Workout fueling
- Recovery-focused nutrition

## The Workflow

The skill follows the same order a good coach would:

**Intake -> Screen -> Calculate -> Program -> Feed -> Monitor -> Adjust**

1. Intake: age, sex, height, weight, sport, schedule, equipment, goal, diet, constraints
2. Screen: injuries, medical issues, eating disorder history, aggressive weight-loss requests
3. Calculate: BMR, estimated TDEE, protein, carbs, fats, training/rest day targets
4. Program: weekly calendar, session details, intensity, progression, deload rules
5. Feed: meal timing, food choices, grocery list, substitutions
6. Monitor: bodyweight trend, RPE, sleep, soreness, appetite, mood, performance
7. Adjust: calories, volume, intensity, exercise selection, recovery

## Included Scripts

The skill works as instructions alone, but the scripts give the agent deterministic anchors.

### Calculate Athlete Targets

```bash
python3 .agents/skills/peakwright/scripts/athlete_targets.py \
  --weight-kg 82 \
  --height-cm 184 \
  --age 27 \
  --sex male \
  --goal performance \
  --training-load high \
  --sessions-per-week 6 \
  --phase build
```

### Generate A Weekly Plan Draft

```bash
python3 .agents/skills/peakwright/scripts/plan_builder.py \
  --sport field-court \
  --weight-kg 82 \
  --height-cm 184 \
  --age 27 \
  --sex male \
  --goal performance \
  --training-load high \
  --sessions-per-week 6 \
  --phase build \
  --diet mediterranean \
  --session-min 75
```

Supported options:

| Option | Values |
|--------|--------|
| `--sport` | `strength`, `hypertrophy`, `endurance`, `field-court`, `combat`, `hybrid` |
| `--goal` | `performance`, `fat_loss`, `muscle_gain`, `recomposition` |
| `--training-load` | `low`, `moderate`, `high`, `elite` |
| `--phase` | `base`, `build`, `peak`, `competition`, `deload` |
| `--diet` | `omnivore`, `mediterranean`, `pescatarian`, `vegetarian`, `vegan` |
