#!/usr/bin/env python3
"""
Apple .workout file generator.

Generates valid .workout files (protobuf binary) that can be imported
into Apple Watch via iPhone. Accepts a JSON workout definition and
outputs a .workout file.

Usage:
    python3 generate_workout.py workout.json
    python3 generate_workout.py workout.json -o MyWorkout.workout
    python3 generate_workout.py --example > example.json
    echo '{"displayName":"Quick Run",...}' | python3 generate_workout.py -

Binary format: Protocol Buffers with a 6-byte magic trailer.
Reverse-engineered from Apple's WorkoutKit framework by DotnetWorkoutKit.
"""

import argparse
import io
import json
import re
import struct
import sys
import uuid


# ============================================================================
# Protobuf wire-format encoder (no external dependency needed)
# ============================================================================

WIRE_VARINT = 0
WIRE_FIXED64 = 1
WIRE_LENGTH_DELIMITED = 2


def _encode_varint(value):
    """Encode an unsigned integer as a protobuf varint."""
    parts = []
    while value > 0x7F:
        parts.append((value & 0x7F) | 0x80)
        value >>= 7
    parts.append(value & 0x7F)
    return bytes(parts)


def _encode_tag(field_number, wire_type):
    """Encode a protobuf field tag."""
    return _encode_varint((field_number << 3) | wire_type)


def _encode_string(field_number, value):
    """Encode a string field."""
    if not value:
        return b""
    encoded = value.encode("utf-8")
    return _encode_tag(field_number, WIRE_LENGTH_DELIMITED) + _encode_varint(len(encoded)) + encoded


def _encode_uint32(field_number, value):
    """Encode a uint32 field as varint."""
    if value == 0:
        return b""
    return _encode_tag(field_number, WIRE_VARINT) + _encode_varint(value)


def _encode_enum(field_number, value):
    """Encode an enum field (same as varint)."""
    if value == 0:
        return b""
    return _encode_tag(field_number, WIRE_VARINT) + _encode_varint(value)


def _encode_double(field_number, value):
    """Encode a double (fixed64) field."""
    if value == 0.0:
        return b""
    return _encode_tag(field_number, WIRE_FIXED64) + struct.pack("<d", value)


def _encode_message(field_number, data):
    """Encode a sub-message field."""
    if not data:
        return b""
    return _encode_tag(field_number, WIRE_LENGTH_DELIMITED) + _encode_varint(len(data)) + data


# ============================================================================
# Activity type mapping (HKWorkoutActivityType raw values)
# ============================================================================

ACTIVITY_TYPES = {
    "americanfootball": 1,
    "archery": 2,
    "australianfootball": 3,
    "badminton": 4,
    "baseball": 5,
    "basketball": 6,
    "bowling": 7,
    "boxing": 8,
    "climbing": 9,
    "cricket": 10,
    "crosstraining": 11,
    "curling": 12,
    "cycling": 13,
    "elliptical": 16,
    "fencing": 19,
    "fishing": 20,
    "functionalstrengthtraining": 21,
    "golf": 22,
    "gymnastics": 23,
    "handball": 24,
    "hiking": 25,
    "hockey": 26,
    "hunting": 27,
    "lacrosse": 28,
    "martialarts": 29,
    "mindandbody": 30,
    "paddlesports": 31,
    "play": 32,
    "racquetball": 34,
    "rowing": 35,
    "rugby": 36,
    "running": 37,
    "sailing": 38,
    "skatingsports": 39,
    "snowsports": 40,
    "soccer": 41,
    "softball": 42,
    "squash": 43,
    "stairclimbing": 44,
    "surfingsports": 45,
    "swimming": 46,
    "tableTennis": 47,
    "tennis": 48,
    "trackandfield": 49,
    "traditionalstrengthtraining": 50,
    "volleyball": 51,
    "walking": 52,
    "waterfitness": 53,
    "waterpolo": 54,
    "watersports": 55,
    "wrestling": 56,
    "yoga": 57,
    "barre": 58,
    "coretraining": 59,
    "crosscountryskiing": 60,
    "downhillskiing": 61,
    "flexibility": 62,
    "highintensityintervaltraining": 63,
    "hiit": 63,
    "jumpRope": 64,
    "kickboxing": 65,
    "pilates": 66,
    "snowboarding": 67,
    "stairs": 68,
    "steptraining": 69,
    "wheelchairwalkpace": 70,
    "wheelchairrunpace": 71,
    "taiChi": 72,
    "mixedcardio": 73,
    "handcycling": 74,
    "discSports": 75,
    "fitnessGaming": 76,
    "cardioDance": 77,
    "socialDance": 78,
    "pickleball": 79,
    "cooldown": 80,
    "swimbikerun": 82,
    "transition": 83,
    "underwaterdiving": 84,
}

# Common aliases
ACTIVITY_ALIASES = {
    "run": "running",
    "bike": "cycling",
    "cycle": "cycling",
    "swim": "swimming",
    "walk": "walking",
    "hike": "hiking",
    "row": "rowing",
    "elliptical": "elliptical",
    "strength": "traditionalstrengthtraining",
    "strengthtraining": "traditionalstrengthtraining",
    "functionalstrength": "functionalstrengthtraining",
    "crossfit": "highintensityintervaltraining",
    "intervals": "highintensityintervaltraining",
    "yoga": "yoga",
    "pilates": "pilates",
    "kickboxing": "kickboxing",
    "boxing": "boxing",
    "stairclimber": "stairclimbing",
    "stairs": "stairclimbing",
    "jumprope": "jumpRope",
    "skierg": "crosscountryskiing",
    "skiing": "downhillskiing",
    "snowboard": "snowboarding",
    "skatingsports": "skatingsports",
    "skating": "skatingsports",
    "pickleball": "pickleball",
    "tennis": "tennis",
    "soccer": "soccer",
    "basketball": "basketball",
    "outdoor_rowing": "rowing",
    "outdoor_skating": "skatingsports",
    "pool_swim": "swimming",
    "open_water_swim": "swimming",
    "dance": "cardioDance",
    "mixed_cardio": "mixedcardio",
    "core": "coretraining",
    "core_training": "coretraining",
    "flexibility": "flexibility",
    "barre": "barre",
    "tai_chi": "taiChi",
    "surfing": "surfingsports",
    "golf": "golf",
    "climbing": "climbing",
}

LOCATION_TYPES = {
    "indoor": 2,
    "outdoor": 3,
}


# ============================================================================
# Pace parsing utilities
# ============================================================================

def parse_pace_to_mps(pace_str, unit="km"):
    """
    Parse pace string to meters per second.

    Formats:
        "5:00" or "5'00\"" → 5 min 0 sec per km (or per mile)
        "4:30/km" → 4 min 30 sec per km
        "7:00/mi" → 7 min 0 sec per mile

    Args:
        pace_str: Pace string
        unit: "km" or "mi" (default unit if not specified in string)

    Returns:
        Speed in meters per second
    """
    pace_str = str(pace_str).strip()

    # Detect unit in string
    if "/mi" in pace_str.lower() or "per mile" in pace_str.lower():
        unit = "mi"
        pace_str = re.sub(r"\s*/\s*mi(le)?", "", pace_str, flags=re.IGNORECASE)
    elif "/km" in pace_str.lower() or "per km" in pace_str.lower():
        unit = "km"
        pace_str = re.sub(r"\s*/\s*km", "", pace_str, flags=re.IGNORECASE)

    # Parse time component
    # Format: "5'30\"" or "5:30" or "5.5" (minutes)
    pace_str = pace_str.strip().strip('"').strip("'")

    match = re.match(r"(\d+)[:'′](\d+)[\"″]?", pace_str)
    if match:
        minutes = int(match.group(1))
        seconds = int(match.group(2))
    elif ":" in pace_str:
        parts = pace_str.split(":")
        minutes = int(parts[0])
        seconds = int(parts[1]) if len(parts) > 1 else 0
    else:
        try:
            minutes = float(pace_str)
            seconds = 0
        except ValueError:
            raise ValueError(f"Cannot parse pace: {pace_str}")

    total_seconds = minutes * 60 + seconds
    if total_seconds <= 0:
        raise ValueError(f"Pace must be positive: {pace_str}")

    # Convert to m/s
    distance_meters = 1000.0 if unit == "km" else 1609.344
    return distance_meters / total_seconds


def parse_speed_to_mps(speed_val, unit="mps"):
    """
    Parse speed value to meters per second.

    Args:
        speed_val: Numeric speed value
        unit: "mps" (m/s), "kph" (km/h), "mph" (mi/h)

    Returns:
        Speed in meters per second
    """
    speed_val = float(speed_val)
    if unit in ("mps", "m/s", "meters_per_second"):
        return speed_val
    elif unit in ("kph", "km/h", "kmh", "kilometers_per_hour"):
        return speed_val / 3.6
    elif unit in ("mph", "mi/h", "miles_per_hour"):
        return speed_val * 0.44704
    else:
        raise ValueError(f"Unknown speed unit: {unit}")


# ============================================================================
# Protobuf message encoders
# ============================================================================

def encode_wrap_double(field_num, value):
    """Encode a WrapDouble message (field 1 = double value)."""
    inner = _encode_double(1, value)
    return _encode_message(field_num, inner)


def encode_heart_rate_range_alert(min_bpm, max_bpm):
    """
    Encode HeartRateRangeAlert protobuf message.

    HeartRateRangeAlert:
        field 2: ClosedRange (heart_rate_range)
            field 1: WrapDouble (lower_bound)
            field 2: WrapDouble (upper_bound)
    """
    lower = encode_wrap_double(1, float(min_bpm))
    upper = encode_wrap_double(2, float(max_bpm))
    closed_range = lower + upper
    return _encode_message(2, closed_range)


def encode_speed_bound(speed_mps):
    """
    Encode a SpeedBound message.

    SpeedBound:
        field 1: Speed { field 1: unit (METERS_PER_SECOND=1), field 2: speed (double) }
        field 2: Unknown { field 1: uint32(1), field 2: double(1.0) }
    """
    speed_msg = _encode_enum(1, 1) + _encode_double(2, speed_mps)  # METERS_PER_SECOND=1
    unknown_msg = _encode_uint32(1, 1) + _encode_double(2, 1.0)
    return _encode_message(1, speed_msg) + _encode_message(2, unknown_msg)


def encode_speed_range_alert(min_speed_mps, max_speed_mps):
    """
    Encode SpeedAlert protobuf message.

    SpeedAlert:
        field 2: SpeedRangeAlert
            field 1: SpeedBound (lower_bound)
            field 2: SpeedBound (upper_bound)
    """
    lower = _encode_message(1, encode_speed_bound(min_speed_mps))
    upper = _encode_message(2, encode_speed_bound(max_speed_mps))
    speed_range = lower + upper
    return _encode_message(2, speed_range)


def encode_workout_alert(alert_def):
    """
    Encode a WorkoutAlert protobuf message from a JSON alert definition.

    WorkoutAlert:
        field 1: AlertMetricEnum (alert_metric)
        field 2: uint32 (unknown, 2 = range)
        field 4: SpeedAlert (speed_alert)
        field 7: HeartRateRangeAlert (heart_rate_range_alert)
    """
    if alert_def is None:
        return b""

    alert_type = alert_def.get("type", "").lower().replace("_", "").replace("-", "")
    data = b""

    if alert_type in ("heartraterange", "heartrate", "hr"):
        min_bpm = alert_def.get("min", alert_def.get("minBpm", alert_def.get("lower", 120)))
        max_bpm = alert_def.get("max", alert_def.get("maxBpm", alert_def.get("upper", 160)))
        # AlertMetric: COUNT_PER_MINUTE = 5
        data += _encode_enum(1, 5)
        data += _encode_uint32(2, 2)  # range type
        data += _encode_message(7, encode_heart_rate_range_alert(min_bpm, max_bpm))

    elif alert_type in ("speedrange", "speed", "pace", "pacerange"):
        metric_str = alert_def.get("metric", "current").lower()
        metric_val = 2 if metric_str == "current" else 1  # CURRENT=2, AVERAGE=1

        # Handle pace format (min:sec/km or min:sec/mi)
        if "minPace" in alert_def or "maxPace" in alert_def or "min_pace" in alert_def or "max_pace" in alert_def:
            pace_unit = alert_def.get("paceUnit", alert_def.get("pace_unit", "km"))
            min_pace = alert_def.get("minPace", alert_def.get("min_pace"))
            max_pace = alert_def.get("maxPace", alert_def.get("max_pace"))
            # Note: slower pace = lower speed, faster pace = higher speed
            # min_pace is the SLOWER pace (lower speed), max_pace is FASTER (higher speed)
            min_speed = parse_pace_to_mps(min_pace, pace_unit) if min_pace else 0
            max_speed = parse_pace_to_mps(max_pace, pace_unit) if max_pace else 0
            # Ensure min_speed < max_speed (slower pace = numerically bigger string = lower m/s)
            if min_speed > max_speed:
                min_speed, max_speed = max_speed, min_speed
        elif "minSpeed" in alert_def or "maxSpeed" in alert_def or "min_speed" in alert_def or "max_speed" in alert_def:
            speed_unit = alert_def.get("speedUnit", alert_def.get("speed_unit", "mps"))
            min_speed = parse_speed_to_mps(
                alert_def.get("minSpeed", alert_def.get("min_speed", 0)), speed_unit
            )
            max_speed = parse_speed_to_mps(
                alert_def.get("maxSpeed", alert_def.get("max_speed", 0)), speed_unit
            )
        else:
            raise ValueError("Speed alert requires minPace/maxPace or minSpeed/maxSpeed")

        data += _encode_enum(1, metric_val)
        data += _encode_uint32(2, 2)  # range type
        data += _encode_message(4, encode_speed_range_alert(min_speed, max_speed))

    else:
        raise ValueError(f"Unsupported alert type: {alert_def.get('type')}. "
                         f"Supported: heartRateRange, speedRange/pace")

    return data


def encode_workout_goal(goal_def):
    """
    Encode a WorkoutGoal protobuf message.

    WorkoutGoal:
        field 1: GoalType enum
        field 2: TimeGoal { field 1: TimeUnitType, field 2: double }
        field 4: DistanceGoal { field 1: DistanceUnitType, field 2: double }
    """
    if goal_def is None:
        # Default to open goal
        return _encode_enum(1, 4)  # OPEN = 4

    goal_type = goal_def.get("type", "open").lower()

    if goal_type == "open":
        return _encode_enum(1, 4)  # OPEN = 4

    elif goal_type in ("distance", "dist"):
        value = float(goal_def.get("value", 0))
        unit_str = goal_def.get("unit", "meters").lower()

        if unit_str in ("km", "kilometers", "kilometre", "kilometres"):
            unit_val = 2  # KILOMETERS
        elif unit_str in ("m", "meters", "metres", "meter", "metre"):
            unit_val = 1  # METERS
        elif unit_str in ("mi", "miles", "mile"):
            unit_val = 3  # MILES (unverified — no reference file to confirm)
        elif unit_str in ("yd", "yards", "yard"):
            unit_val = 4  # YARDS (confirmed via Apple-generated reference file)
        else:
            unit_val = 1  # Default METERS

        distance_goal = _encode_enum(1, unit_val) + _encode_double(2, value)
        return _encode_enum(1, 3) + _encode_message(4, distance_goal)  # DISTANCE = 3

    elif goal_type in ("time", "duration"):
        value = float(goal_def.get("value", 0))
        unit_str = goal_def.get("unit", "minutes").lower()

        if unit_str in ("s", "sec", "secs", "second", "seconds"):
            unit_val = 1  # SECONDS
        elif unit_str in ("m", "min", "mins", "minute", "minutes"):
            unit_val = 2  # MINUTES
        elif unit_str in ("h", "hr", "hrs", "hour", "hours"):
            unit_val = 3  # HOURS
        else:
            unit_val = 2  # Default MINUTES

        time_goal = _encode_enum(1, unit_val) + _encode_double(2, value)
        return _encode_enum(1, 1) + _encode_message(2, time_goal)  # TIME = 1

    else:
        raise ValueError(f"Unsupported goal type: {goal_type}. Supported: open, distance, time")


def encode_workout_step(step_def):
    """
    Encode a WorkoutStep protobuf message.

    WorkoutStep:
        field 1: WorkoutGoal
        field 2: WorkoutAlert (optional)
        field 3: display_name (optional string)
    """
    if step_def is None:
        return b""

    data = b""

    # Goal (field 1)
    goal = step_def.get("goal")
    goal_data = encode_workout_goal(goal)
    data += _encode_message(1, goal_data)

    # Alert (field 2, optional)
    alert = step_def.get("alert")
    if alert:
        alert_data = encode_workout_alert(alert)
        data += _encode_message(2, alert_data)

    # Display name (field 3, optional)
    name = step_def.get("displayName", step_def.get("display_name", step_def.get("name")))
    if name:
        data += _encode_string(3, name)

    return data


def encode_interval_step(step_def):
    """
    Encode an IntervalStep protobuf message.

    IntervalStep:
        field 1: IntervalPurpose enum (WORK=1, RECOVERY=2)
        field 2: WorkoutStep
    """
    purpose_str = step_def.get("purpose", "work").lower()
    if purpose_str in ("work", "w"):
        purpose_val = 1
    elif purpose_str in ("recovery", "recover", "rest", "r"):
        purpose_val = 2
    else:
        purpose_val = 1  # Default to work

    data = _encode_enum(1, purpose_val)

    # Build a WorkoutStep from the interval step fields
    workout_step_def = {
        "goal": step_def.get("goal"),
        "alert": step_def.get("alert"),
        "displayName": step_def.get("displayName", step_def.get("display_name", step_def.get("name"))),
    }
    ws_data = encode_workout_step(workout_step_def)
    data += _encode_message(2, ws_data)

    return data


def encode_interval_block(block_def):
    """
    Encode an IntervalBlock protobuf message.

    IntervalBlock:
        field 1: repeated IntervalStep
        field 2: uint32 iterations
    """
    data = b""

    steps = block_def.get("steps", [])
    for step in steps:
        step_data = encode_interval_step(step)
        data += _encode_message(1, step_data)

    iterations = int(block_def.get("iterations", block_def.get("repeats", 1)))
    data += _encode_uint32(2, iterations)

    return data


def encode_custom_workout(workout_def):
    """
    Encode a CustomWorkout protobuf message.

    CustomWorkout:
        field 1: ActivityType enum
        field 2: LocationType enum
        field 3: display_name (optional string)
        field 4: warmup WorkoutStep (optional)
        field 5: repeated IntervalBlock
        field 6: cooldown WorkoutStep (optional)
    """
    data = b""

    # Activity type (field 1)
    activity_str = workout_def.get("activity", "running").lower().replace(" ", "").replace("_", "")
    activity_str = ACTIVITY_ALIASES.get(activity_str, activity_str)
    activity_val = ACTIVITY_TYPES.get(activity_str)
    if activity_val is None:
        raise ValueError(
            f"Unknown activity type: {workout_def.get('activity')}. "
            f"Supported: {', '.join(sorted(set(list(ACTIVITY_TYPES.keys()) + list(ACTIVITY_ALIASES.keys()))))}"
        )
    data += _encode_enum(1, activity_val)

    # Location type (field 2)
    location_str = workout_def.get("location", "outdoor").lower()
    location_val = LOCATION_TYPES.get(location_str, 3)  # Default outdoor
    data += _encode_enum(2, location_val)

    # Display name (field 3)
    name = workout_def.get("displayName", workout_def.get("display_name", workout_def.get("name", "")))
    if name:
        data += _encode_string(3, name)

    # Warmup (field 4, optional)
    warmup = workout_def.get("warmup", workout_def.get("warmUp"))
    if warmup:
        ws_data = encode_workout_step(warmup)
        data += _encode_message(4, ws_data)

    # Interval blocks (field 5, repeated)
    blocks = workout_def.get("blocks", [])
    for block in blocks:
        block_data = encode_interval_block(block)
        data += _encode_message(5, block_data)

    # Cooldown (field 6, optional)
    cooldown = workout_def.get("cooldown", workout_def.get("coolDown"))
    if cooldown:
        ws_data = encode_workout_step(cooldown)
        data += _encode_message(6, ws_data)

    return data


def encode_workout_binary(workout_def):
    """
    Encode a full WorkoutBinary protobuf message.

    WorkoutBinary:
        field 9: GUID (string)
        field 11: CustomWorkout (message)
    """
    guid = workout_def.get("guid", str(uuid.uuid4()).upper())
    custom_workout_data = encode_custom_workout(workout_def)

    data = b""
    data += _encode_string(9, guid)
    data += _encode_message(11, custom_workout_data)

    return data


# Magic trailer bytes required at end of .workout file
MAGIC_TRAILER = bytes([0xC0, 0x3E, 0x01, 0xD0, 0x3E, 0x05])


def generate_workout_file(workout_def):
    """
    Generate a complete .workout file from a workout definition dict.

    Returns:
        bytes: The complete .workout file content
    """
    protobuf_data = encode_workout_binary(workout_def)
    return protobuf_data + MAGIC_TRAILER


# ============================================================================
# Example workout definitions
# ============================================================================

EXAMPLES = {
    "5k_intervals": {
        "displayName": "5K Interval Training",
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
                        "alert": {
                            "type": "pace",
                            "metric": "current",
                            "minPace": "5:00",
                            "maxPace": "4:30",
                            "paceUnit": "km"
                        },
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
            "goal": {"type": "distance", "value": 1.0, "unit": "km"},
            "alert": {"type": "heartRateRange", "min": 110, "max": 130},
            "displayName": "Cool Down"
        }
    },
    "tempo_run": {
        "displayName": "Tempo Run",
        "activity": "running",
        "location": "outdoor",
        "warmup": {
            "goal": {"type": "time", "value": 10, "unit": "minutes"},
            "displayName": "Easy Warmup"
        },
        "blocks": [
            {
                "iterations": 1,
                "steps": [
                    {
                        "purpose": "work",
                        "goal": {"type": "time", "value": 20, "unit": "minutes"},
                        "alert": {
                            "type": "pace",
                            "metric": "current",
                            "minPace": "4:45",
                            "maxPace": "4:15",
                            "paceUnit": "km"
                        },
                        "displayName": "Tempo Effort"
                    }
                ]
            }
        ],
        "cooldown": {
            "goal": {"type": "time", "value": 10, "unit": "minutes"},
            "displayName": "Cool Down"
        }
    },
    "cycling_intervals": {
        "displayName": "Cycling Intervals",
        "activity": "cycling",
        "location": "outdoor",
        "warmup": {
            "goal": {"type": "time", "value": 10, "unit": "minutes"},
            "displayName": "Spin Up"
        },
        "blocks": [
            {
                "iterations": 6,
                "steps": [
                    {
                        "purpose": "work",
                        "goal": {"type": "time", "value": 3, "unit": "minutes"},
                        "alert": {
                            "type": "heartRateRange",
                            "min": 155,
                            "max": 170
                        },
                        "displayName": "Hard Effort"
                    },
                    {
                        "purpose": "recovery",
                        "goal": {"type": "time", "value": 2, "unit": "minutes"},
                        "displayName": "Easy Spin"
                    }
                ]
            }
        ],
        "cooldown": {
            "goal": {"type": "time", "value": 10, "unit": "minutes"},
            "displayName": "Cool Down"
        }
    },
    "hiit_workout": {
        "displayName": "30-20-10 HIIT",
        "activity": "hiit",
        "location": "indoor",
        "warmup": {
            "goal": {"type": "time", "value": 5, "unit": "minutes"},
            "displayName": "Warmup"
        },
        "blocks": [
            {
                "iterations": 5,
                "steps": [
                    {
                        "purpose": "work",
                        "goal": {"type": "time", "value": 30, "unit": "seconds"},
                        "displayName": "Easy Pace"
                    },
                    {
                        "purpose": "work",
                        "goal": {"type": "time", "value": 20, "unit": "seconds"},
                        "displayName": "Moderate Pace"
                    },
                    {
                        "purpose": "work",
                        "goal": {"type": "time", "value": 10, "unit": "seconds"},
                        "displayName": "All Out Sprint"
                    },
                    {
                        "purpose": "recovery",
                        "goal": {"type": "time", "value": 60, "unit": "seconds"},
                        "displayName": "Rest"
                    }
                ]
            }
        ],
        "cooldown": {
            "goal": {"type": "time", "value": 5, "unit": "minutes"},
            "displayName": "Cooldown"
        }
    },
    "simple_run": {
        "displayName": "Easy 5K Run",
        "activity": "running",
        "location": "outdoor",
        "blocks": [
            {
                "iterations": 1,
                "steps": [
                    {
                        "purpose": "work",
                        "goal": {"type": "distance", "value": 5.0, "unit": "km"},
                        "alert": {"type": "heartRateRange", "min": 130, "max": 150}
                    }
                ]
            }
        ]
    },
    "pool_swim_yards": {
        "displayName": "Pool Swim Intervals (Yards)",
        "activity": "swimming",
        "location": "indoor",
        "warmup": {
            "goal": {"type": "distance", "value": 200, "unit": "yards"},
            "displayName": "Warmup"
        },
        "blocks": [
            {
                "iterations": 4,
                "steps": [
                    {
                        "purpose": "work",
                        "goal": {"type": "distance", "value": 100, "unit": "yards"},
                        "displayName": "Fast 100"
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
                        "displayName": "Sprint 50"
                    },
                    {
                        "purpose": "recovery",
                        "goal": {"type": "time", "value": 20, "unit": "seconds"},
                        "displayName": "Rest"
                    }
                ]
            }
        ],
        "cooldown": {
            "goal": {"type": "distance", "value": 200, "unit": "yards"},
            "displayName": "Cooldown"
        }
    },
}


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate Apple .workout files from JSON definitions.",
        epilog="See RESEARCH.md for format details and JSON schema reference."
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="JSON file path, or '-' for stdin. Omit with --example."
    )
    parser.add_argument(
        "-o", "--output",
        help="Output .workout file path (default: <displayName>.workout)"
    )
    parser.add_argument(
        "--example",
        nargs="?",
        const="5k_intervals",
        metavar="NAME",
        help=f"Print example JSON to stdout. Names: {', '.join(EXAMPLES.keys())}"
    )
    parser.add_argument(
        "--list-examples",
        action="store_true",
        help="List all available example workout names"
    )
    parser.add_argument(
        "--list-activities",
        action="store_true",
        help="List all supported activity types"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate JSON without generating file"
    )

    args = parser.parse_args()

    if args.list_examples:
        for name, workout in EXAMPLES.items():
            print(f"  {name:25s} - {workout.get('displayName', name)}")
        return

    if args.list_activities:
        print("Activity types (use any of these in the 'activity' field):\n")
        seen = set()
        for name in sorted(ACTIVITY_TYPES.keys()):
            if name not in seen:
                print(f"  {name}")
                seen.add(name)
        print("\nAliases:")
        for alias, target in sorted(ACTIVITY_ALIASES.items()):
            print(f"  {alias:30s} → {target}")
        return

    if args.example:
        name = args.example
        if name not in EXAMPLES:
            print(f"Unknown example: {name}. Available: {', '.join(EXAMPLES.keys())}", file=sys.stderr)
            sys.exit(1)
        print(json.dumps(EXAMPLES[name], indent=2))
        return

    if not args.input:
        parser.print_help()
        sys.exit(1)

    # Read input
    if args.input == "-":
        raw = sys.stdin.read()
    else:
        with open(args.input, "r") as f:
            raw = f.read()

    workout_def = json.loads(raw)

    # Validate
    if args.validate:
        try:
            generate_workout_file(workout_def)
            name = workout_def.get("displayName", workout_def.get("display_name", "unnamed"))
            print(f"Valid workout definition: {name}")
        except Exception as e:
            print(f"Validation error: {e}", file=sys.stderr)
            sys.exit(1)
        return

    # Generate
    workout_bytes = generate_workout_file(workout_def)

    # Determine output path
    output_path = args.output
    if not output_path:
        name = workout_def.get("displayName", workout_def.get("display_name", "workout"))
        # Sanitize filename
        safe_name = re.sub(r"[^\w\s-]", "", name).strip().replace(" ", "_")
        output_path = f"{safe_name}.workout"

    with open(output_path, "wb") as f:
        f.write(workout_bytes)

    print(f"Generated: {output_path} ({len(workout_bytes)} bytes)")


if __name__ == "__main__":
    main()
