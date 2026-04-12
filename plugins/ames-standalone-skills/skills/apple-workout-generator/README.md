# Apple Watch Workout Generator

A Claude Code skill that generates `.workout` files for Apple Watch from natural language descriptions or images of workout plans.

## What Are .workout Files?

`.workout` files are Apple's format for sharing structured custom workouts. When opened on an iPhone (iOS 17+), they present a preview UI with an "Add to Watch" button that imports the workout directly to the Apple Watch Workout app.

## Dependencies

**None.** The generator is a single self-contained Python script with zero external dependencies. It implements Protocol Buffer binary encoding from scratch using only the Python standard library.

- **Python 3.8+** (standard library only)

## Files

| File | Description |
|------|-------------|
| `SKILL.md` | Claude Code skill definition with JSON schema and usage |
| `generate_workout.py` | The workout generator script |
| `RESEARCH.md` | Research on the .workout file format (protobuf schema, Apple docs) |
| `README.md` | This file |

## Usage

### Generate from JSON

```bash
python3 generate_workout.py workout.json
python3 generate_workout.py workout.json -o ~/Desktop/MyWorkout.workout
```

### Generate from stdin

```bash
echo '{"displayName":"Quick Run","activity":"running","blocks":[{"iterations":1,"steps":[{"purpose":"work","goal":{"type":"distance","value":5,"unit":"km"}}]}]}' | python3 generate_workout.py -
```

### Print example JSON

```bash
python3 generate_workout.py --example 5k_intervals
python3 generate_workout.py --example tempo_run
python3 generate_workout.py --example cycling_intervals
python3 generate_workout.py --example hiit_workout
python3 generate_workout.py --example simple_run
```

### Other commands

```bash
python3 generate_workout.py --list-examples      # Show all examples
python3 generate_workout.py --list-activities     # Show all activity types
python3 generate_workout.py workout.json --validate  # Validate only
```

## Supported Features

### Activity Types (50+)

Running, Cycling, Swimming, Walking, Hiking, HIIT, Rowing, Elliptical, Yoga, Strength Training, Pilates, Boxing, Kickboxing, Stair Climbing, Pickleball, Tennis, Soccer, Basketball, Golf, Climbing, Skating, Skiing, Snowboarding, Dance, Core Training, and many more. Aliases like `run`, `bike`, `swim` are also supported.

### Goal Types

- **Open** — user manually advances
- **Distance** — kilometers, meters, miles, yards
- **Time** — seconds, minutes, hours

### Alert Types

- **Heart rate range** — min/max BPM
- **Pace range** — min:sec per km or per mile (auto-converts)
- **Speed range** — m/s, km/h, or mph

### Workout Structure

```
Warmup (optional)
  └── goal + optional alert
Blocks (1 or more)
  └── iterations (repeat count)
  └── Steps (work / recovery)
      └── goal + optional alert + optional name
Cooldown (optional)
  └── goal + optional alert
```

## How to Import to Apple Watch

1. Transfer the `.workout` file to your iPhone via:
   - AirDrop
   - iCloud Drive
   - Email attachment
   - Messages
   - Any file sharing method
2. Tap the file on your iPhone
3. A preview shows the workout structure
4. Tap "Add to Watch" to import

**Requirements:** iPhone running iOS 17+ paired with Apple Watch running watchOS 10+.

## Technical Details

The `.workout` file format is a serialized Protocol Buffer binary with a 6-byte magic trailer (`C0 3E 01 D0 3E 05`). The protobuf schema was reverse-engineered from Apple's WorkoutKit framework by the [DotnetWorkoutKit](https://github.com/changeforan/DotnetWorkoutKit) project. See `RESEARCH.md` for the complete specification.
