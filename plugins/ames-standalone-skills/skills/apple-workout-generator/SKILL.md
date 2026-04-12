---
name: apple-workout-generator
description: This skill should be used when the user asks to "create a workout",
  "build a workout file", "generate a .workout file", "make an Apple Watch workout",
  "create a running/cycling/swimming/HIIT workout", or needs to generate .workout
  files that can be imported into Apple Watch via iPhone. Supports creating workouts
  from text descriptions, images of workout plans, or structured specifications.
allowed-tools: Bash, Write, Read
---

# Apple Watch Workout Generator

Generate valid `.workout` files for Apple Watch from text descriptions or images of workout plans.

## How It Works

The user describes a workout in plain language or provides an image of a workout plan. You:

1. Parse the description into a structured JSON workout definition
2. Run the Python generator to produce a `.workout` binary file
3. The user transfers the file to their iPhone (AirDrop, iCloud, etc.) to import it

## Dependencies

**None required.** The generator script (`generate_workout.py`) has zero external dependencies — it implements protobuf binary encoding from scratch using only Python standard library.

- Python 3.8+ (standard library only)

## Quick Reference

```bash
# Generate from JSON file
python3 generate_workout.py workout.json

# Generate with custom output path
python3 generate_workout.py workout.json -o MyWorkout.workout

# Generate from stdin (pipe JSON)
echo '{"displayName":"Quick Run",...}' | python3 generate_workout.py -

# Print example JSON
python3 generate_workout.py --example 5k_intervals

# Validate without generating
python3 generate_workout.py workout.json --validate

# List available examples
python3 generate_workout.py --list-examples

# List all activity types
python3 generate_workout.py --list-activities
```

## Distance Units

**Use consistent units throughout a workout.** All distances in a workout should use the same measurement system (yards OR meters, not a mix).

- When creating a workout from an image or description, use the **same unit system as the source material**
- For swimming workouts: if the workout references a 25-yard pool, all distances should be in yards. If a 25-meter pool, use meters.
- **If the unit system is ambiguous, ask the user whether they swim in a yard or meter pool**
- Common gym pools in the US (like GMCF / Green Mountain Community Fitness) are typically 25-yard pools

Supported distance units: `meters`, `kilometers`, `yards`, `miles`

## Workflow

### Step 1: Build the JSON Definition

Parse the user's request into a JSON workout definition. The schema:

```json
{
  "displayName": "Workout Name",
  "activity": "running",
  "location": "outdoor",
  "warmup": {
    "goal": {"type": "distance", "value": 1.0, "unit": "km"},
    "alert": {"type": "heartRateRange", "min": 120, "max": 140},
    "displayName": "Easy Warmup"
  },
  "blocks": [
    {
      "iterations": 4,
      "steps": [
        {
          "purpose": "work",
          "goal": {"type": "distance", "value": 800, "unit": "meters"},
          "alert": {"type": "pace", "metric": "current", "minPace": "5:00", "maxPace": "4:30"},
          "displayName": "Fast 800m"
        },
        {
          "purpose": "recovery",
          "goal": {"type": "time", "value": 2, "unit": "minutes"},
          "displayName": "Jog Recovery"
        }
      ]
    }
  ],
  "cooldown": {
    "goal": {"type": "time", "value": 5, "unit": "minutes"},
    "displayName": "Cool Down"
  }
}
```

### Step 2: Write JSON to a temp file and generate

```bash
# Write the JSON to a temp file, then generate
python3 ~/.claude/skills/apple-workout-generator/generate_workout.py /tmp/workout.json -o ~/Desktop/MyWorkout.workout
```

### Step 3: Tell the user how to import

Tell the user to transfer the `.workout` file to their iPhone via AirDrop, iCloud Drive, email, or messaging. When opened on iPhone (iOS 17+), it presents a preview and "Add to Watch" button.

## JSON Schema Reference

### Top Level

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `displayName` | string | No | Workout name shown in Apple Watch UI |
| `activity` | string | Yes | Activity type (see below) |
| `location` | string | No | `"indoor"` or `"outdoor"` (default: outdoor) |
| `warmup` | WorkoutStep | No | Optional warmup phase |
| `blocks` | IntervalBlock[] | Yes | Array of interval blocks |
| `cooldown` | WorkoutStep | No | Optional cooldown phase |

### Activity Types

Common activities: `running`, `cycling`, `swimming`, `walking`, `hiking`, `hiit`, `rowing`, `elliptical`, `yoga`, `strength`, `pilates`, `boxing`, `kickboxing`, `stairclimbing`, `pickleball`, `tennis`, `soccer`, `basketball`, `golf`, `climbing`, `skating`, `skiing`, `snowboarding`, `dance`, `core_training`, `flexibility`, `barre`, `tai_chi`, `mixed_cardio`, `surfing`

Aliases are supported: `run` → `running`, `bike`/`cycle` → `cycling`, `swim` → `swimming`, `walk` → `walking`, `hike` → `hiking`, `row` → `rowing`, `intervals` → `hiit`

Run `--list-activities` for the complete list.

### WorkoutStep

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `goal` | Goal | Yes | Step goal |
| `alert` | Alert | No | Optional alert |
| `displayName` | string | No | Step label (shown on watch, watchOS 11+) |

### Goal Types

**Open goal** (user manually advances):
```json
{"type": "open"}
```

**Distance goal:**
```json
{"type": "distance", "value": 5.0, "unit": "km"}
```
Units: `km`, `meters`, `miles`, `yards`

**Time goal:**
```json
{"type": "time", "value": 20, "unit": "minutes"}
```
Units: `seconds`, `minutes`, `hours`

### Alert Types

**Heart rate range:**
```json
{"type": "heartRateRange", "min": 140, "max": 160}
```

**Pace range** (for running/cycling):
```json
{"type": "pace", "metric": "current", "minPace": "5:30", "maxPace": "5:00", "paceUnit": "km"}
```
- `minPace`: slower pace (higher number), `maxPace`: faster pace (lower number)
- `paceUnit`: `"km"` (min/km) or `"mi"` (min/mile). Can also embed in pace: `"7:00/mi"`
- `metric`: `"current"` or `"average"`

**Speed range** (numeric):
```json
{"type": "speedRange", "metric": "current", "minSpeed": 10, "maxSpeed": 15, "speedUnit": "kph"}
```
Units: `mps` (m/s), `kph` (km/h), `mph` (mi/h)

### IntervalBlock

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `iterations` | int | No | Number of repeats (default: 1) |
| `steps` | IntervalStep[] | Yes | Array of work/recovery steps |

### IntervalStep

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `purpose` | string | Yes | `"work"` or `"recovery"` |
| `goal` | Goal | Yes | Step goal |
| `alert` | Alert | No | Optional alert |
| `displayName` | string | No | Step label |

## Example Workouts

### From Text Description

**User says:** "Create a 5K interval workout with 4x800m repeats at 4:30-5:00/km pace with 2 min recovery jogs, plus a 1km warmup and cooldown"

→ Parse into JSON with warmup (1km), block (4 iterations, 800m work + 2min recovery), cooldown (1km)

### From Image

When the user provides an image of a workout plan, read the image and extract:
- Activity type
- Structure (warmup → intervals → cooldown)
- Distances, times, pace targets, heart rate zones
- Number of repetitions
- **Distance unit system** (yards vs meters) — use the same units shown in the source image. If the image shows "200 yd" or "4x100", determine from context whether it's yards or meters. If unclear, ask the user.

Then build the JSON definition and generate.

## Validation Rules

- Distance goals should not be used for non-distance activities (e.g., yoga)
- Pace alerts only make sense for running, cycling, and similar activities
- Heart rate alerts work with all activity types
- Each step can have at most one alert
- `minPace` should be the SLOWER pace (bigger number) and `maxPace` the FASTER pace

## File Format

The `.workout` file is a Protocol Buffer binary with a magic trailer. See [RESEARCH.md](RESEARCH.md) for the full reverse-engineered specification. The file can be opened on any iPhone running iOS 17+ to preview and import to Apple Watch.
