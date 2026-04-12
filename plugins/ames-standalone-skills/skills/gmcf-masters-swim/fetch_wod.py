#!/usr/bin/env python3
"""
GMCF Masters Swim WOD Fetcher

Fetches the Masters Swim workout from SugarWOD's public API.
Zero external dependencies — uses only Python standard library.

Usage:
    python3 fetch_wod.py              # Today's workout
    python3 fetch_wod.py 20260225     # Specific date (YYYYMMDD)
    python3 fetch_wod.py --json       # Output raw JSON
    python3 fetch_wod.py --next       # Next swim day's workout
"""

import argparse
import json
import re
import sys
import textwrap
from datetime import datetime, timedelta
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

AFFILIATE_ID = "EI3YKIBca5"
TRACK = "Masters Swim"
BASE_URL = "https://app.sugarwod.com/public/api/v1/affiliates"
SWIM_DAYS = {1, 2, 3}  # Monday=0 .. Sunday=6 → Tue=1, Wed=2, Thu=3
USER_AGENT = "Mozilla/5.0"

# --- Swim abbreviation glossary (for display) ---

STROKE_ABBREVS = {
    "FR": "Freestyle",
    "BK": "Backstroke",
    "BR": "Breaststroke",
    "FL": "Butterfly",
    "IM": "Individual Medley",
    "DPS": "Distance Per Stroke",
}


def fetch_workout(date_str: str) -> dict | None:
    """Fetch the Masters Swim WOD for a given date (YYYYMMDD string).

    Returns the raw API response dict, or None on failure.
    """
    tracks_param = quote(json.dumps([TRACK]))
    url = f"{BASE_URL}/{AFFILIATE_ID}/workouts/{date_str}?tracks={tracks_param}"

    req = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except HTTPError as e:
        print(f"HTTP error {e.code}: {e.reason}", file=sys.stderr)
        return None
    except URLError as e:
        print(f"Network error: {e.reason}", file=sys.stderr)
        return None

    return data


def get_next_swim_date() -> datetime:
    """Return the next swim day (Tue/Wed/Thu). If today is a swim day, return today."""
    today = datetime.now()
    for offset in range(7):
        candidate = today + timedelta(days=offset)
        if candidate.weekday() in SWIM_DAYS:
            return candidate
    return today  # fallback


def parse_date_arg(arg: str) -> str:
    """Validate and return a YYYYMMDD string."""
    if not re.match(r"^\d{8}$", arg):
        print(f"Invalid date format: {arg}. Expected YYYYMMDD.", file=sys.stderr)
        sys.exit(1)
    return arg


def format_workout(workout: dict) -> str:
    """Format a single workout entry for terminal display."""
    title = workout.get("title", "Untitled")
    description = workout.get("description", "")
    date_display = workout.get("scheduledDateDisplay", "")

    # Extract total yardage from title if present, e.g. "Hold Focus (2500)"
    yard_match = re.search(r"\((\d+)\)", title)
    total_yards = yard_match.group(1) if yard_match else None

    lines = []
    lines.append(f"  {title}")
    if date_display:
        lines.append(f"  {date_display}")
    if total_yards:
        lines.append(f"  Total: {total_yards} yards")
    lines.append("")

    # Format the description with light section highlighting
    for line in description.split("\n"):
        stripped = line.strip()
        if not stripped:
            lines.append("")
            continue

        # Detect section headers (Warm-up, Set N, Cool Down, etc.)
        is_header = bool(
            re.match(r"^(warm.?up|cool.?down|set\s*\d|main\s*set|pre.?set|workout)", stripped, re.IGNORECASE)
        )

        if is_header:
            lines.append(f"  --- {stripped} ---")
        else:
            lines.append(f"  {stripped}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Fetch GMCF Masters Swim WOD from SugarWOD")
    parser.add_argument("date", nargs="?", help="Date in YYYYMMDD format (default: today)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON response")
    parser.add_argument("--next", action="store_true", help="Fetch the next swim day's workout")
    args = parser.parse_args()

    if args.next:
        target = get_next_swim_date()
        date_str = target.strftime("%Y%m%d")
    elif args.date:
        date_str = parse_date_arg(args.date)
    else:
        date_str = datetime.now().strftime("%Y%m%d")

    # Friendly date display
    try:
        dt = datetime.strptime(date_str, "%Y%m%d")
        friendly_date = dt.strftime("%A, %B %-d, %Y")
    except ValueError:
        friendly_date = date_str

    data = fetch_workout(date_str)

    if data is None:
        sys.exit(1)

    if args.json:
        print(json.dumps(data, indent=2))
        return

    if not data.get("success") or not data.get("data"):
        weekday = dt.weekday() if 'dt' in dir() else -1
        print(f"GMCF Masters Swim -- {friendly_date}")
        print()
        if weekday not in SWIM_DAYS:
            print(f"  No workout expected — Masters Swim meets Tue/Wed/Thu.")
        else:
            print(f"  No workout posted yet. Steve usually posts the evening before or morning of practice.")
        return

    # Header
    print(f"GMCF Masters Swim -- {friendly_date}")
    sep = "-" * 50
    print(sep)

    for workout in data["data"]:
        print(format_workout(workout))

    print(sep)


if __name__ == "__main__":
    main()
