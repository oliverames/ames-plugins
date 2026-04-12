---
name: gmcf-masters-swim
description: This skill should be used when the user asks about "today's swim workout",
  "masters WOD", "GMCF swim", "what's the workout today", "pull the WOD",
  "Steve's workout", "masters swim practice", or wants to fetch, display, or
  generate .workout files from the GMCF Masters Swim program posted on SugarWOD.
allowed-tools: Bash, Write, Read
---

# GMCF Masters Swim — SugarWOD Fetcher

Fetch and display the GMCF Masters Swim workout of the day from SugarWOD's public API. Optionally convert it into a downloadable `.workout` file for Apple Watch.

## How It Works

Coach Steve Maas posts Masters Swim workouts to SugarWOD under the **"Masters Swim"** track at the GMCF affiliate. This skill fetches that data via an unauthenticated public API endpoint and presents it in a readable format.

## API Details

| Field | Value |
|-------|-------|
| Affiliate ID | `EI3YKIBca5` |
| Track | `Masters Swim` |
| Swim days | Tuesday, Wednesday, Thursday |
| Pool | 25-yard, 6-lane (GMCF / Green Mountain Community Fitness) |
| Base URL | `https://app.sugarwod.com/public/api/v1/affiliates/{id}/workouts/{YYYYMMDD}` |
| Track filter | `?tracks=["Masters Swim"]` (URL-encoded) |
| Required header | `User-Agent: Mozilla/5.0` (any non-empty UA; bare requests get 403) |

### Response Shape

```json
{
  "success": true,
  "data": [
    {
      "title": "Hold Focus (2500)",
      "description": "Warm-up: (400)\n6x50 Kick @:15r\n...",
      "scheduledDateDisplay": "Tuesday, February 25",
      "track": "Masters Swim"
    }
  ]
}
```

- `success: false` or empty `data` array means no workout posted for that date.
- `title` often includes total yardage in parentheses, e.g. `"Descending 100 Ladder (2700)"`.
- `description` is the full workout text, newline-delimited.

## Dependencies

**None required.** The fetch script uses only Python standard library (`urllib`, `json`).

## Usage

### Fetch and Display

```bash
# Today's workout
python3 ~/.claude/skills/gmcf-masters-swim/fetch_wod.py

# Specific date
python3 ~/.claude/skills/gmcf-masters-swim/fetch_wod.py 20260225

# Output raw JSON (for piping to other tools)
python3 ~/.claude/skills/gmcf-masters-swim/fetch_wod.py --json

# Specific date as JSON
python3 ~/.claude/skills/gmcf-masters-swim/fetch_wod.py 20260225 --json
```

### Fetch + Generate .workout File

After fetching and displaying the workout, you can convert it into an Apple Watch `.workout` file using the `apple-workout-generator` skill:

1. Fetch the WOD with `--json` to get the raw description
2. Parse the description into the workout JSON schema (see mapping rules below)
3. **Validate** the workout JSON against the parsed WOD (see Step 4 below)
4. Determine the output path:
   - **macOS (not `CLAUDE_CODE_REMOTE=true`):** Save to `~/Documents/Masters Swimming/<filename>.workout` (create the directory if it doesn't exist)
   - **Linux/cloud:** Save to `/tmp/<filename>.workout` and offer the file to the user
5. Write the JSON to a temp file and run `python3 ~/.claude/skills/apple-workout-generator/generate_workout.py /tmp/workout.json -o <output_path>`

## Workflow

When the user asks for the masters swim workout:

### Step 1: Fetch the WOD

Run the fetch script for today (or the user's requested date):

```bash
python3 ~/.claude/skills/gmcf-masters-swim/fetch_wod.py
```

If no workout is posted yet, tell the user. Steve usually posts workouts the evening before or morning of practice.

### Step 2: Display the Workout

Present the workout to the user in a clean, readable format. The fetch script already formats output, but you should also:

- Highlight the total yardage from the title
- Break out warm-up, sets, and cooldown visually
- Note any pace/interval targets

### Step 3 (Optional): Generate .workout File

If the user wants a `.workout` file for their Apple Watch, parse the WOD description into the `apple-workout-generator` JSON schema.

Break the full workout into blocks — one per distinct exercise pattern. Do NOT use the `warmup` or `cooldown` fields; put everything in `blocks` so all yardage is counted.

### Step 4: Validate Against the Parsed WOD

Before generating the binary file, cross-check the workout JSON against the fetched WOD data:

- **Total yardage:** Sum all block distances (iterations × step distances). Must match the A-lane total from the WOD title.
- **Rest intervals:** Every `:NNr` notation has a matching recovery step with the exact NN seconds. Display name is `"Rest"` — never raw notation.
- **All sections present:** Every warmup component, main set exercise, and cooldown is represented as a block.
- **Block count:** Verify the number of blocks matches the number of distinct exercises in the WOD.
- **Iteration counts:** Each block's `iterations` matches the rep count from the WOD (e.g., `4x100` → iterations: 4).

If any mismatch is found, fix the JSON before generating.

**Title format:** Steve's titles follow the pattern `"Masters NNNN - Workout Name"`. Simplify for the .workout file display name and filename:

```
YYYY-MM-DD [Workout Name] [Yardage] yds
```

Example: `"Masters 0227 - Same Difference"` on Feb 25 with A-lane yardage 2200 → `"2026-02-25 Same Difference 2200 yds"`

The Masters number is not included — it's Steve's internal sequencing and not useful on the Watch. Use the scheduled date from the API response. For total yardage, use the A-lane total (warmup + main set + cooldown) unless the user specifies a different lane.

**Do NOT use warmup/cooldown fields.** Put everything in `blocks`. This way Apple's "Work Distance" includes the full workout yardage (no confusing mismatch where warmup/cooldown are excluded). Each distinct exercise pattern — including each warmup component and the cooldown — becomes its own block.

**Mapping rules for Steve's format:**

| SugarWOD format | Workout JSON |
|----------------|-------------|
| `Warm-up: (400)` / `Warm Up (400)` | One or more **blocks** — one per component exercise (see below) |
| `6x50 Kick @:15r` | Block: 6 iterations, 50yd work step + **15s** recovery step |
| `4x100 FR @1:45` | Block: 4 iterations, 100yd work step + recovery step (see rest rules) |
| `Cool Down (200)` / `Cooldown (200)` | **Block** (not cooldown field) with appropriate distance goal |
| `Set 1: (600)` | One or more blocks totaling 600 yards |
| `200 Pull` (single effort) | Block: 1 iteration, 200yd work step, no recovery |

**Rest interval rules (CRITICAL — get these right):**

| Notation | Meaning | Recovery step |
|----------|---------|---------------|
| `:15r` or `@:15r` | 15 seconds rest | `"value": 15, "unit": "seconds"` |
| `:20r` or `@:20r` | 20 seconds rest | `"value": 20, "unit": "seconds"` |
| `:30r` | 30 seconds rest | `"value": 30, "unit": "seconds"` |
| `:NNr` (any number with `r`) | NN seconds rest (exact) | `"value": NN, "unit": "seconds"` |
| `@1:45` (no `r` suffix) | Send-off interval (1 min 45 sec total) | Calculate rest using formula below |
| `@M:SS` (no `r` suffix) | Send-off interval | Calculate rest using formula below |
| `rest as needed` | No specified rest | Calculate rest using formula below |

The `r` suffix means **rest duration** — use the exact value. Without `r`, it's a **send-off** (total time from start to start); calculate actual rest using the formula below.

### Rest as Needed / Send-off Estimation Formula

Oliver's 100 FR PR (zone 5, off the wall, 25yd pool): **1:08 (68 seconds)**

```
base_pace = 68 / 100 = 0.68 s/yd

stroke_factor:
  FR (freestyle):           1.0
  Drill / mixed / kick:     1.15
  BK (backstroke):          1.25
  IM (individual medley):   1.30
  FL (butterfly):           1.35
  BR (breaststroke):        1.35

estimated_work_time = distance × 0.68 × 1.2 × stroke_factor
rest_seconds = max(15, round(estimated_work_time × 0.30))
rest_seconds = round(rest_seconds / 5) * 5  # round to nearest 5s
```

**Examples for common distances:**

| Interval | Stroke | Est. work | Calculated rest |
|----------|--------|-----------|-----------------|
| 25yd | FL | 29s | **15s** |
| 50yd | FL/FR | 39–41s | **15s** |
| 75yd | drill/FL | 74s | **20s** |
| 100yd | FR | 82s | **25s** |
| 200yd | FR (build) | 163s | **50s** |

For send-off intervals (`@M:SS`), also cross-check: rest = send-off time − estimated work time. Use whichever is more reasonable.

**Recovery step display name must always be `"Rest"`** — never include the raw SugarWOD notation like `@:35` or `:15r` in the display name.

**Critical:** All distances are in **yards** (GMCF is a 25-yard pool). Set `"unit": "yards"` on all distance goals.

The activity type is always `"swimming"` with `"location": "indoor"`.

### Breaking Out Warmups and Cooldowns

Complex warmups with multiple components (e.g., "200 Choice + 4x50 Kick @:15r") must be split into **separate blocks** — one per distinct exercise. This prevents everything from getting lumped into one unreadable step. Same for cooldowns.

Example: A warmup of "5 min choice easy / 200 pull / 4x50 as 25 drill, 25 swim" becomes **three** blocks:

1. Block (1 iter): time goal 5 min — "Warmup: 5 Min Easy"
2. Block (1 iter): 200yd — "Warmup: Pull"
3. Block (4 iter): 50yd work step — "Warmup: 25 Drill / 25 Swim"

### Set Clarity

Each distinct exercise pattern becomes its own block. When a main set contains multiple exercises (e.g., 4x100 + 4x50 + 200 recovery), create **separate blocks** for each — don't combine them.

### Interval Display Name Conventions

Two rules for interval names on the Apple Watch:

**1. Don't duplicate the distance in the name.** The Watch already shows the distance below the interval name (e.g., "100yd"), so repeating it wastes space. Exception: when the interval has a subdivision (e.g., "25 Sprint / 25 Easy" for a 50yd block), keep the distances to explain the split.

| Distance | Raw description | displayName |
|----------|----------------|-------------|
| 200yd | 200 Pull | `Pull` |
| 100yd | 100 Zone 3 | `Zone 3` |
| 50yd | 25 Sprint / 25 Easy | `25 Sprint / 25 Easy` (subdivision) |

**2. Prefix every interval with its set label.** This tells the swimmer which section they're in. Format: `"[Set]: [Name]"`.

Set labels: `Warmup:`, `Main:`, `Pre-Set:`, `Drill Set:`, `Cooldown:`

Only add a round number (`Main 1:`, `Main 2:`) when an entire group of intervals repeats identically. If the exercises are different (e.g., Zone 3 in one half vs Zone 2 in the other), they're just different parts of the main set — use `Main:` for all of them.

Examples:
- `"Warmup: Choice Easy"` (not "200 Choice Easy")
- `"Main: Zone 3"` (not "100 Zone 3")
- `"Main: 25 Sprint / 25 Easy"` (subdivision — distances kept)
- `"Main: Pull Recovery"` (not "200 Pull Recovery")
- `"Cooldown: Easy Choice"` (not "200 Easy Choice")

### Example Conversion

**SugarWOD text:**
```
Masters 0220 - Speed Ladder (2200)

Warm-up
200 Choice easy
4x50 Kick @:15r

Main Set (1600)
4x100 FR zone 3 :15r
4x50 as 25 sprint, 25 easy :20r
200 pull recovery
4x100 FR zone 2 :30r
4x50 as 25 build, 25 easy :10r
200 pull recovery

Cooldown
200 Easy choice
```

**Workout JSON (A lane):**
```json
{
  "displayName": "2026-02-20 Speed Ladder 2200 yds",
  "activity": "swimming",
  "location": "indoor",
  "blocks": [
    {
      "iterations": 1,
      "steps": [
        {
          "purpose": "work",
          "goal": {"type": "distance", "value": 200, "unit": "yards"},
          "displayName": "Warmup: Choice Easy"
        }
      ]
    },
    {
      "iterations": 4,
      "steps": [
        {
          "purpose": "work",
          "goal": {"type": "distance", "value": 50, "unit": "yards"},
          "displayName": "Warmup: Kick"
        },
        {
          "purpose": "recovery",
          "goal": {"type": "time", "value": 15, "unit": "seconds"},
          "displayName": "Rest"
        }
      ]
    },
    {
      "iterations": 4,
      "steps": [
        {
          "purpose": "work",
          "goal": {"type": "distance", "value": 100, "unit": "yards"},
          "displayName": "Main: Zone 3"
        },
        {
          "purpose": "recovery",
          "goal": {"type": "time", "value": 15, "unit": "seconds"},
          "displayName": "Rest"
        }
      ]
    },
    {
      "iterations": 4,
      "steps": [
        {
          "purpose": "work",
          "goal": {"type": "distance", "value": 50, "unit": "yards"},
          "displayName": "Main: 25 Sprint / 25 Easy"
        },
        {
          "purpose": "recovery",
          "goal": {"type": "time", "value": 20, "unit": "seconds"},
          "displayName": "Rest"
        }
      ]
    },
    {
      "iterations": 1,
      "steps": [
        {
          "purpose": "work",
          "goal": {"type": "distance", "value": 200, "unit": "yards"},
          "displayName": "Main: Pull Recovery"
        }
      ]
    },
    {
      "iterations": 4,
      "steps": [
        {
          "purpose": "work",
          "goal": {"type": "distance", "value": 100, "unit": "yards"},
          "displayName": "Main: Zone 2"
        },
        {
          "purpose": "recovery",
          "goal": {"type": "time", "value": 30, "unit": "seconds"},
          "displayName": "Rest"
        }
      ]
    },
    {
      "iterations": 4,
      "steps": [
        {
          "purpose": "work",
          "goal": {"type": "distance", "value": 50, "unit": "yards"},
          "displayName": "Main: 25 Build / 25 Easy"
        },
        {
          "purpose": "recovery",
          "goal": {"type": "time", "value": 10, "unit": "seconds"},
          "displayName": "Rest"
        }
      ]
    },
    {
      "iterations": 1,
      "steps": [
        {
          "purpose": "work",
          "goal": {"type": "distance", "value": 200, "unit": "yards"},
          "displayName": "Main: Pull Recovery"
        }
      ]
    },
    {
      "iterations": 1,
      "steps": [
        {
          "purpose": "work",
          "goal": {"type": "distance", "value": 200, "unit": "yards"},
          "displayName": "Cooldown: Easy Choice"
        }
      ]
    }
  ]
}
```

Notice: no `warmup` or `cooldown` fields — everything is in `blocks`. Each warmup component, each main set exercise, and the cooldown are separate blocks. Rest display names are always `"Rest"` with the actual seconds from the `:NNr` notation. Display names are prefixed with set labels (`Warmup:`, `Main:`, `Cooldown:`) and distances are omitted when the Watch already shows them (except for subdivisions like "25 Sprint / 25 Easy").

## Parsing Steve's Workout Format

Steve's workouts follow a consistent structure. Key patterns:

### Section Headers
- `Warm-up: (DISTANCE)` or `Warm Up (DISTANCE)`
- `Set N: DESCRIPTION (DISTANCE)` or `Set N (DISTANCE)`
- `Pre-Set: (DISTANCE)`
- `Main Set: (DISTANCE)`
- `Cool Down: (DISTANCE)` or `Cooldown (DISTANCE)`

### Interval Lines
- `NxDISTANCE STROKE @INTERVAL` — e.g., `6x50 Kick @:15r`, `4x100 FR @1:45`
- `NxDISTANCE STROKE` — no specified interval
- `DISTANCE STROKE` — single effort, e.g., `400 Choice`, `200 IM`

### A/B/C Lane Options
Steve's workouts frequently offer three lanes (A = fastest/most yardage, B = middle, C = least). These can vary by **pace**, **distance**, **reps**, or all three:

**Pace options only:**
```
4x100 FR
A: @1:30
B: @1:45
C: @2:00
```

**Distance/rep variations per lane:**
```
Warm-up (A: 600, B: 500, C: 400)
200 Choice easy	(B: 150, C: 100)
4x50 Kick choice	(B: 3x50 C: 2x50)
```

**Full set variations per lane:**
```
Main Set (A: 1200, B: 1000, C: 800)
- 5x25 FR AFAP A: @:25  B: @35  C: :15r
- FR Steady: A: 1x175  B: 1x125  C: 1x75
```

**When generating a `.workout` file from an A/B/C workout:** Default to the **A lane** unless the user specifies otherwise, since A matches the total yardage shown in the workout title. If the user doesn't specify, briefly note which lane was used.

### Common Abbreviations
| Abbreviation | Meaning |
|-------------|---------|
| FR | Freestyle |
| BK | Backstroke |
| BR | Breaststroke |
| FL | Butterfly |
| IM | Individual Medley (Fly-Back-Breast-Free) |
| Choice | Swimmer's choice of stroke |
| Kick | Kick with board |
| Pull | Pull with buoy |
| Drill | Technique drill |
| DPS | Distance Per Stroke |
| AFAP | As Fast As Possible (sprint) |
| r | Rest (as in `@:15r` = 15 seconds rest) |
| RI | Rest Interval |
| Descend | Get faster each repeat |
| Build | Increase speed within each repeat |
| Easy | Recovery pace |
| Fast | Sprint/race pace |
| Moderate | Aerobic pace |

## Scriptable (iOS) Integration

A full Scriptable.app JavaScript implementation exists for iOS Shortcuts integration. It:
- Fetches the WOD from SugarWOD
- Parses the workout structure (sections, intervals, options)
- Generates formatted HTML for PDF export via Shortcuts
- Returns structured JSON for `.workout` file generation
- Auto-targets the next swim day (Tue/Wed/Thu) when run outside swim days

See `scriptable_wod.js` in this skill directory for the complete implementation.

## Troubleshooting

| Issue | Solution |
|-------|---------|
| 403 Forbidden | Ensure `User-Agent` header is set to a non-empty string |
| Empty response | No workout posted for that date; Steve posts Tue/Wed/Thu |
| Wrong track | Verify the track filter is `["Masters Swim"]` (case-sensitive) |
| API changed | Check if `https://app.sugarwod.com/public/api/v1/` still resolves; the endpoint is undocumented and could change |
