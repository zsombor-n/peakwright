# Evidence And Source Map

Use this reference for source-backed planning, repo recommendations, and API choices. The skill can generate practical plans without loading this file, but load it when the user asks why, asks for installation options, or needs a serious long-term plan.

## Best Skill And Repo Leads

- `nousresearch/hermes-agent`, `optional-skills/health/fitness-nutrition`: best direct skill to install if the user wants ready-made exercise lookup, USDA nutrition lookup, BMI/TDEE/1RM/macro calculators, and no Python package dependencies. Marketplace page: https://skillsauth.com/skills/nousresearch/fitness-nutrition. Source: https://github.com/NousResearch/hermes-agent/tree/main/optional-skills/health/fitness-nutrition
- `ddarmon/llmn`: meal-planning skill around a CLI optimizer. Strong if the user wants constraint-based plans by calories, protein, diet style, and food exclusions. Source: https://github.com/ddarmon/llmn/blob/main/.claude/skills/llmn/SKILL.md
- `gtapps/claude-code-hermit`, `claude-code-fitness-hermit`: Strava-oriented Claude Code plugin for activity deep dives, weekly load review, anomalies, and planning suggestions. Strong for endurance athletes with Strava history; heavier setup. Source: https://github.com/gtapps/claude-code-hermit/tree/main/plugins/claude-code-fitness-hermit
- `wger-project/wger`: open-source workout, fitness, and nutrition manager with exercise data and API. Useful as an exercise library and self-hosted tracker. Source: https://github.com/wger-project/wger
- `simonoppowa/OpenNutriTracker`: privacy-focused open calorie tracker with custom meals, meal planning, barcode scanning, and no ads. Useful product reference, less directly useful as an agent skill. Source: https://github.com/simonoppowa/OpenNutriTracker
- `kcal-app/kcal`: self-hosted nutrition journal with recipes, foods, macros, multiple goals, and training/rest day style calorie goals. Useful for meal-plan data modeling. Source: https://github.com/kcal-app/kcal

## Skill Format

Anthropic's public skills repo describes skills as folders containing instructions, scripts, and resources, with a required `SKILL.md` file and YAML frontmatter. Source: https://github.com/anthropics/skills

## Data Sources And APIs

- wger public endpoints such as exercise and ingredient lists can be accessed without authentication; user-owned objects require authentication. Add `?format=json` when JSON is needed. Docs: https://wger.readthedocs.io/en/latest/api/api.html
- USDA FoodData Central API provides REST access for nutrient data. Main endpoints include `/food/{fdcId}`, `/foods`, `/foods/list`, and `/foods/search`. A data.gov API key is expected; `DEMO_KEY` works for initial exploration with lower limits. Docs: https://fdc.nal.usda.gov/api-guide
- USDA FoodData Central data is public domain / CC0. Attribute USDA FoodData Central when using its data in published outputs. Docs: https://fdc.nal.usda.gov/api-guide
- Open Food Facts is useful for packaged-food barcode/product data. The project warns that voluntarily contributed data may be incomplete or inaccurate, so prefer USDA for generic ingredients and use Open Food Facts for branded products with caveats. Docs: https://openfoodfacts.github.io/openfoodfacts-server/api/

## Training Guidelines

- ACSM's 2026 resistance training update emphasizes consistency, individualization, and all major muscle groups at least twice weekly for most healthy adults. It gives useful anchors: strength around heavier loads near 80% 1RM for 2-3 sets; hypertrophy around roughly 10 weekly sets per muscle group; power with moderate loads around 30-70% 1RM moved quickly. Source: https://acsm.org/resistance-training-guidelines-update-2026/
- ACSM notes that advanced methods such as training to failure, exact equipment type, and complex periodization are often optional for average healthy adults; athletes and advanced trainees still need sport-specific planning. Source: https://acsm.org/resistance-training-guidelines-update-2026/
- NSCA preparatory-period guidance frames hypertrophy/strength-endurance phases as lower to moderate intensity, higher volume work, often around 50-75% 1RM for 3-6 sets of 8-20 reps, then moving toward heavier, more sport-specific work. Source: https://www.nsca.com/education/articles/kinetic-select/preparatory-period/
- For advanced athletes, periodization should serve the sport calendar: base general capacity first, build toward force/power/sport specificity, peak by preserving intensity and reducing fatigue, then deload/taper.

## Sports Nutrition Guidelines

- ACSM/Academy of Nutrition and Dietetics/Dietitians of Canada position stand gives carbohydrate targets by training demand: about 3-5 g/kg/day for low-intensity or skill-based light training, 5-7 g/kg/day for moderate training, 6-10 g/kg/day for high-volume endurance or intense training, and 8-12 g/kg/day for very high commitments. It also suggests 1-4 g/kg carbohydrate 1-4 hours pre-event, 30-60 g/hour during 1-2.5 hour endurance sessions, and up to 90 g/hour for ultra-endurance with multiple transportable carbohydrates. Source: https://www.federvolley.it/sites/default/files/Settore%20Tecnico%20%2B%20Scuola%20%2B%20Antidoping/2016%20ACSM_Nutrition%20and%20Athletic%20Performance.pdf
- The same position stand places athlete protein needs commonly around 1.2-2.0 g/kg/day, with higher intakes sometimes useful during intensified training or energy restriction. It recommends regular high-quality protein across the day and around strenuous training sessions. Source: same ACSM nutrition PDF.
- ISSN's protein position stand gives 1.4-2.0 g/kg/day for most exercising individuals, 0.25 g/kg or 20-40 g high-quality protein per serving, and even distribution every 3-4 hours. Source: https://link.springer.com/article/10.1186/s12970-017-0177-8
- ACSM nutrition guidance discourages chronic fat intake below 20% of energy; common athlete eating patterns often land around 20-35% of energy from fat. Source: same ACSM nutrition PDF.
- Prefer whole foods first. Supplements are optional and should be conservative, third-party tested, and matched to a clear problem. Avoid supplement protocols that conflict with sport anti-doping rules.

## Practical Defaults

Only use defaults when the user has not provided more specific data:

- Protein: 1.6-2.2 g/kg/day for strength, hypertrophy, or fat loss phases; 1.4-1.8 g/kg/day for endurance-focused phases unless energy restriction or injury risk calls for more.
- Carbohydrate: 3-5 g/kg/day for light training, 5-7 for moderate, 6-10 for hard endurance/team sport blocks, 8-12 for extreme volume.
- Fat: fill remaining calories after protein and carbohydrate, usually no lower than 20% of total energy.
- Calorie deficit: keep performance athletes conservative, often 250-500 kcal/day or about 5-15% below maintenance. Avoid aggressive deficits during high-volume blocks.
- Lean gaining: start around 150-300 kcal/day above maintenance and adjust by weekly bodyweight trend.
- Deload: every 3-5 hard weeks or when performance and recovery markers decline.

## Red Flags

Recommend professional review before detailed planning if there is: current injury pain, cardiac symptoms, fainting, pregnancy, diabetes, kidney disease, GI disease, eating disorder history, rapid weight-loss request, dehydration/sauna cutting, or use of prescription medication that affects nutrition or training tolerance.
