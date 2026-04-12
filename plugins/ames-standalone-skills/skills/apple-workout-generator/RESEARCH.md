# Apple .workout File Format Research

Research for building a Claude Code skill that generates `.workout` files for Apple Watch.

---

## Executive Summary

Apple's `.workout` files are **Protocol Buffer (protobuf) binary files** used by the WorkoutKit framework (iOS 17+ / watchOS 10+) to define structured custom workouts. These files can be shared via AirDrop or other means, and when opened on an iPhone, they present a preview UI that lets users import the workout to their Apple Watch.

**Key finding:** The binary format has been reverse-engineered by the [DotnetWorkoutKit](https://github.com/changeforan/DotnetWorkoutKit) project. The format is well-understood protobuf, making it feasible to generate `.workout` files with a Python script (no Apple SDK required).

---

## WorkoutKit Framework Overview

WorkoutKit (introduced WWDC23, expanded WWDC24) supports four workout composition types:

| Type | Description |
|------|-------------|
| **CustomWorkout** | Structured interval workouts with warmup, work/recovery blocks, cooldown, goals, and alerts |
| **SingleGoalWorkout** | Simple workouts with one goal (distance, energy, or time) |
| **PacerWorkout** | Cover a specific distance in a given time |
| **SwimBikeRunWorkout** | Multisport triathlon-style workouts |

The `.workout` file format wraps these into a `WorkoutPlan` for sharing/import.

### Official Apple Documentation

- [WorkoutKit Framework](https://developer.apple.com/documentation/workoutkit/)
- [CustomWorkout](https://developer.apple.com/documentation/workoutkit/customworkout)
- [IntervalBlock](https://developer.apple.com/documentation/workoutkit/intervalblock)
- [WorkoutGoal](https://developer.apple.com/documentation/workoutkit/workoutgoal)
- [WorkoutAlert](https://developer.apple.com/documentation/workoutkit/workoutalert)
- [WWDC23 - Build custom workouts with WorkoutKit](https://developer.apple.com/videos/play/wwdc2023/10016/)
- [WWDC24 - Build custom swimming workouts](https://developer.apple.com/videos/play/wwdc2024/10084/)

---

## Binary Format Details

### Format: Protocol Buffers (proto3)

The `.workout` file is a **serialized protobuf message** with a 6-byte magic trailer appended.

#### Top-Level Structure

```
[protobuf WorkoutBinary message bytes] + [0xC0 0x3E 0x01 0xD0 0x3E 0x05]
```

The magic trailer bytes `C0 3E 01 D0 3E 05` must be appended after the protobuf data.

### Reconstructed Protobuf Schema

The complete schema (reverse-engineered by DotnetWorkoutKit):

```protobuf
// WorkoutFile.proto
syntax = "proto3";

message WorkoutBinary {
    string GUID = 9;                    // UUID string (e.g., "A1B2C3D4-E5F6-...")
    CustomWorkout custom_workout = 11;  // The workout definition
}
```

```protobuf
// CustomWorkout.proto
syntax = "proto3";

message CustomWorkout {
    enum ActivityType {
        UNSPECIFIED_ActivityType = 0;
        RUNNING = 37;
        // Other activity types map to HKWorkoutActivityType raw values
        // e.g., CYCLING = 13, SWIMMING = 46, HIIT = 63, etc.
    }

    enum LocationType {
        UNSPECIFIED_LocationType = 0;
        INDOOR = 2;
        OUTDOOR = 3;
    }

    ActivityType activity_type = 1;
    LocationType location_type = 2;
    optional string display_name = 3;
    optional WorkoutStep warmup = 4;
    repeated IntervalBlock interval_blocks = 5;
    optional WorkoutStep cooldown = 6;
}
```

```protobuf
// WorkoutStep.proto
syntax = "proto3";

message WorkoutStep {
    WorkoutGoal workout_goal = 1;
    optional WorkoutAlert workout_alert = 2;
    optional string display_name = 3;
}
```

```protobuf
// WorkoutGoal.proto
syntax = "proto3";

message WorkoutGoal {
    enum GoalType {
        UNSPECIFIED = 0;
        TIME = 1;
        DISTANCE = 3;
        OPEN = 4;
    }

    GoalType goal_type = 1;
    TimeGoal time_goal = 2;
    DistanceGoal distance_goal = 4;

    message TimeGoal {
        enum TimeUnitType {
            UNSPECIFIED = 0;
            SECONDS = 1;
            MINUTES = 2;
            HOURS = 3;
        }
        TimeUnitType unit_type = 1;
        double unit_value = 2;
    }

    message DistanceGoal {
        enum DistanceUnitType {
            UNSPECIFIED = 0;
            METERS = 1;
            KILOMETERS = 2;
            MILES = 3;       // Unverified — no reference file to confirm
            YARDS = 4;       // Confirmed via Apple-generated reference file (Power Pyramid .workout)
        }
        DistanceUnitType unit_type = 1;
        double unit_value = 2;
    }
}
```

```protobuf
// IntervalBlock.proto
syntax = "proto3";

message IntervalBlock {
    repeated IntervalStep interval_steps = 1;
    uint32 iterations = 2;

    message IntervalStep {
        enum IntervalPurpose {
            UNSPECIFIED = 0;
            WORK = 1;
            RECOVERY = 2;
        }
        IntervalPurpose purpose = 1;
        WorkoutStep workout_step = 2;
    }
}
```

```protobuf
// WorkoutAlert.proto
syntax = "proto3";

message WorkoutAlert {
    enum AlertMetricEnum {
        UNSPECIFIED = 0;
        AVERAGE = 1;
        CURRENT = 2;
        COUNT_PER_MINUTE = 5;
    }

    AlertMetricEnum alert_metric = 1;
    uint32 unknown = 2;            // Always 2 for range alerts
    SpeedAlert speed_alert = 4;
    HeartRateRangeAlert heart_rate_range_alert = 7;
}
```

```protobuf
// SpeedAlert.proto
syntax = "proto3";

message SpeedAlert {
    SpeedRangeAlert speed_range_alert = 2;

    message SpeedRangeAlert {
        SpeedBound lower_bound = 1;
        SpeedBound upper_bound = 2;
    }

    message SpeedBound {
        Speed speed = 1;
        Unknown_WrapUInt32_Fixed64 unknown = 2;  // Always {first: 1, second: 1.0}

    }

    message Speed {
        enum SpeedUnitEnum {
            UNSPECIFIED = 0;
            METERS_PER_SECOND = 1;
        }
        SpeedUnitEnum unit = 1;
        double speed = 2;   // Speed in meters/second
    }

    message Unknown_WrapUInt32_Fixed64 {
        uint32 first = 1;   // Always 1
        double second = 2;  // Always 1.0
    }
}
```

```protobuf
// HeartRateRangeAlert.proto
syntax = "proto3";

message HeartRateRangeAlert {
    ClosedRange heart_rate_range = 2;

    message ClosedRange {
        WrapDouble lower_bound = 1;
        WrapDouble upper_bound = 2;
    }

    message WrapDouble {
        double value = 1;   // BPM value
    }
}
```

---

## WorkoutKit Data Model (from Apple Docs)

### CustomWorkout Structure

```
CustomWorkout
├── activity: HKWorkoutActivityType     (running, cycling, swimming, HIIT, etc.)
├── location: HKWorkoutSessionLocationType  (indoor, outdoor)
├── displayName: String?                 (workout name shown in UI)
├── warmup: WorkoutStep?                 (optional warmup phase)
├── blocks: [IntervalBlock]              (repeatable work/recovery blocks)
│   └── IntervalBlock
│       ├── steps: [IntervalStep]        (work and recovery steps)
│       │   └── IntervalStep
│       │       ├── purpose: .work | .recovery
│       │       └── step: WorkoutStep
│       │           ├── goal: WorkoutGoal
│       │           ├── alert: WorkoutAlert?
│       │           └── displayName: String?  (watchOS 11+)
│       └── iterations: Int              (number of repetitions)
└── cooldown: WorkoutStep?               (optional cooldown phase)
```

### Goal Types

| Goal | Parameters | Notes |
|------|-----------|-------|
| `.open` | None | User manually advances |
| `.distance` | value, UnitLength | km, m, mi |
| `.time` | value, UnitDuration | seconds, minutes, hours |
| `.energy` | value, UnitEnergy | kcal, kJ |
| `.poolSwimDistanceWithTime` | distance, time | Swimming-specific (watchOS 11+) |

### Alert Types

| Alert | Parameters | Description |
|-------|-----------|-------------|
| `CadenceRangeAlert` | range, unit | Cadence range (e.g., 170-180 spm) |
| `CadenceThresholdAlert` | threshold, unit | Cadence threshold |
| `HeartRateRangeAlert` | range, unit | HR range (e.g., 140-160 bpm) |
| `HeartRateZoneAlert` | zone (Int) | HR zone (1-5) |
| `PowerRangeAlert` | range, unit, metric? | Power range (e.g., 200-250W) |
| `PowerThresholdAlert` | threshold, unit, metric? | Power threshold |
| `PowerZoneAlert` | zone (Int) | Power zone |
| `SpeedRangeAlert` | range, unit, metric | Speed/pace range |
| `SpeedThresholdAlert` | threshold, unit, metric | Speed/pace threshold |

**WorkoutAlertMetric:** `.average` or `.current`

### Activity Types (known to work with CustomWorkout)

These map to `HKWorkoutActivityType` raw values. Confirmed/mentioned types:
- Running (indoor/outdoor) - proto value `37`
- Cycling (indoor/outdoor) - proto value `13`
- Swimming (pool) - watchOS 11+
- Walking
- Hiking
- Elliptical
- HIIT
- Strength Training
- Rowing (outdoor, watchOS 11+)
- Skating (outdoor, watchOS 11+)

Use `CustomWorkout.supportsActivity(_:)` to check programmatically.

### Validation Rules

- Distance goals should not be used for non-distance-based activities
- Pace alerts should not be applied to activities that don't support pace (e.g., elliptical)
- Indoor running supports pace alerts from watchOS 11+
- Energy goals are supported by WorkoutKit but NOT in the reverse-engineered protobuf schema (may need field 3 in WorkoutGoal)

---

## Existing Implementations

### 1. DotnetWorkoutKit (.NET/C#)
- **URL:** https://github.com/changeforan/DotnetWorkoutKit
- **Language:** C#/.NET
- **Status:** Working, reverse-engineered the protobuf binary format
- **Limitations:** Only Running/Outdoor activity; HeartRate and Speed alerts only
- **Key insight:** Contains the actual `.proto` schema files

### 2. flutter-workoutkit (Flutter/Dart)
- **URL:** https://github.com/adamk22/flutter-workoutkit
- **Language:** Dart (wraps native Apple WorkoutKit SDK)
- **Status:** Requires iOS/macOS to run (uses native SDK)

### 3. Third-party apps
- **WatchFit** - Can import `.workout` files
- **Workout Builder** (matthewpalmer.net) - Creates custom workouts for Apple Watch

---

## Implementation Strategy for Claude Code Skill

### Approach: Python script using `protobuf` library

Since the binary format is protobuf, we can generate `.workout` files with pure Python:

1. **Define the protobuf schema** in `.proto` files (already reverse-engineered above)
2. **Compile to Python** using `protoc` compiler
3. **Or use raw protobuf encoding** without compilation (the `protobuf` Python package supports dynamic message construction)

### Simpler Alternative: Manual protobuf encoding

Python's `protobuf` library or even raw byte construction can produce valid files without needing `protoc`. The message structure is straightforward enough that a standalone Python script can encode the protobuf manually.

### JSON Intermediate Format

For the skill, users would describe workouts in natural language, and the skill would:
1. Parse the description into a structured workout definition
2. Generate the protobuf binary
3. Append the magic trailer
4. Save as `.workout` file

### JSON Schema (for intermediate representation)

```json
{
  "displayName": "5K Training Run",
  "activity": "running",
  "location": "outdoor",
  "warmup": {
    "goal": { "type": "distance", "value": 1.0, "unit": "kilometers" },
    "alert": { "type": "heartRateRange", "min": 120, "max": 140 },
    "displayName": "Easy Warmup"
  },
  "blocks": [
    {
      "iterations": 4,
      "steps": [
        {
          "purpose": "work",
          "goal": { "type": "distance", "value": 800, "unit": "meters" },
          "alert": { "type": "speedRange", "metric": "current", "minPace": "5:00", "maxPace": "4:30" }
        },
        {
          "purpose": "recovery",
          "goal": { "type": "time", "value": 2, "unit": "minutes" }
        }
      ]
    }
  ],
  "cooldown": {
    "goal": { "type": "distance", "value": 1.0, "unit": "kilometers" },
    "displayName": "Cool Down"
  }
}
```

### Pace-to-Speed Conversion

Pace format (min'sec"/km or min'sec"/mi) needs conversion to meters/second:
- `5'00"` per km = 1000m / 300s = 3.333 m/s
- `8'00"` per mile = 1609.34m / 480s = 3.353 m/s

### File Delivery

The generated `.workout` file can be:
- Saved to the user's Desktop or specified path
- AirDropped to iPhone
- Shared via iCloud Drive, email, or messaging
- Opened directly on iPhone to preview and import to Apple Watch

---

## Distance Unit Encoding (Yards & Miles)

The original DotnetWorkoutKit reverse-engineering only documented METERS=1 and KILOMETERS=2 for the `DistanceUnitType` enum. However, Apple's WorkoutKit Swift API supports yards and miles natively via `UnitLength.yards` and `UnitLength.miles`, and the WWDC24 swimming session explicitly demonstrates pool swim workouts with distance goals.

**Problem:** Encoding yards as converted meters (200yd → 182.88m) produces ugly decimal values on the Apple Watch display.

**Resolution (confirmed Feb 2026):** By decoding an Apple-generated `.workout` file (`Power Pyramid .workout`, created via the WorkoutKit Workout app on iPhone), we confirmed:
- **YARDS = 4** — every distance goal in the reference file uses `DistanceUnitType = 4` with raw yard values (50, 200).
- **MILES = 3** — still unverified (no reference file with miles). This is an educated guess based on the remaining gap in the enum sequence.
- Our original guess of YARDS=3 was wrong — enum value 3 falls through to displaying as "Meters" on iPhone, confirming it's not YARDS.

The reference file was a pool swim workout (ActivityType=46, LocationType=INDOOR) with 50-yard work steps and 200-yard warmup/cooldown, all encoded as `DistanceUnitType=4` with clean yard values.

---

## Apple "Work Distance" Behavior

Apple's workout summary screen shows a **"Work Distance"** metric that only counts distance from **interval blocks** (field 5). It does **not** include distance from the separate warmup (field 4) or cooldown (field 6) steps.

For example, a swim workout with:
- Warmup: 600 yards
- Blocks total: 1,700 yards
- Cooldown: 200 yards

...will show **"Work Distance: 1,700 yd"** on the iPhone preview, even though the full workout is 2,500 yards. This is expected Apple behavior — "Work Distance" specifically means the interval block distance.

This is the correct and intentional protobuf structure. Use the official warmup/cooldown fields; the total yardage in the workout title communicates the true total.

---

## Known Limitations & Gaps

1. **Activity type mapping:** The DotnetWorkoutKit only mapped Running (37). Other activity type protobuf values need to be determined (likely match `HKWorkoutActivityType` raw values)
2. **Energy goals:** Not present in reverse-engineered schema; the protobuf field number is unknown
3. **Power/Cadence alerts:** Not reverse-engineered in DotnetWorkoutKit
4. **Heart rate zone alerts:** Not reverse-engineered (only range alerts)
5. **SingleGoalWorkout/PacerWorkout/SwimBikeRunWorkout:** Binary format not reverse-engineered; only CustomWorkout is known
6. **watchOS version compatibility:** Newer features (step names, swimming, expanded activities) may require additional protobuf fields

---

## References

- [Apple WorkoutKit Documentation](https://developer.apple.com/documentation/workoutkit/)
- [WWDC23 Session 10016 - Build custom workouts with WorkoutKit](https://developer.apple.com/videos/play/wwdc2023/10016/)
- [WWDC24 Session 10084 - Build custom swimming workouts](https://developer.apple.com/videos/play/wwdc2024/10084/)
- [DotnetWorkoutKit (GitHub)](https://github.com/changeforan/DotnetWorkoutKit) - Reverse-engineered binary format
- [flutter-workoutkit (GitHub)](https://github.com/adamk22/flutter-workoutkit) - Flutter wrapper for native SDK
- [Apple Developer Forums - How to generate .workout files](https://developer.apple.com/forums/thread/750557)
- [Apple Developer Forums - Export workout plan as JSON](https://developer.apple.com/forums/thread/769885)
- [HKWorkoutActivityType Reference](https://developer.apple.com/documentation/healthkit/hkworkoutactivitytype)
