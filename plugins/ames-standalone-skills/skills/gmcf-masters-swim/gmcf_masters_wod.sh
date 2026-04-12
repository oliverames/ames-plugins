#!/bin/bash
# GMCF Masters Swim WOD Fetcher
#
# Usage: ./gmcf_masters_wod.sh           → today's workout
#        ./gmcf_masters_wod.sh 20260226  → specific date (YYYYMMDD)

AFFILIATE_ID="EI3YKIBca5"
DATE="${1:-$(date +%Y%m%d)}"
URL="https://app.sugarwod.com/public/api/v1/affiliates/${AFFILIATE_ID}/workouts/${DATE}?tracks=%5B%22Masters%20Swim%22%5D"

echo "GMCF Masters Swim — $(date -jf '%Y%m%d' "$DATE" '+%A, %B %-d, %Y' 2>/dev/null || date -d "$DATE" '+%A, %B %-d, %Y' 2>/dev/null || echo "$DATE")"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 - "$URL" << 'PYTHON'
import sys, json
from urllib.request import Request, urlopen

url = sys.argv[1]
req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
data = json.loads(urlopen(req).read())

if not data.get("success") or not data.get("data"):
    print("No Masters Swim workout found for this date.")
    sys.exit(0)

for w in data["data"]:
    print(f"\n{w['title']}")
    print("-" * 40)
    print(w["description"])
PYTHON
