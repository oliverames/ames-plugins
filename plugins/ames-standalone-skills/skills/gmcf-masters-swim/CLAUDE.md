# GMCF Masters Swim

Skill for fetching/generating Apple Watch `.workout` files from GMCF Masters Swim WODs (SugarWOD).

## Helper Scripts

| Script | Purpose |
|--------|---------|
| `fetch_wod.py` | Fetch today's workout from SugarWOD API |
| `gmcf_masters_wod.sh` | Shell wrapper for fetching WOD |
| `scriptable_wod.js` | Scriptable (iOS) widget for WOD display |

See `SKILL.md` for API endpoint details, response shape, and `.workout` file format spec.

## Oliver's Swimming Profile

- **100 FR PR (zone 5, off the wall, 25yd pool): 1:08 (68 seconds)**
- Base pace: 0.68 s/yd

### Short Butterfly Intervals (25yd) — Watch Detection Issue

The Watch auto-advances 25yd butterfly steps in **2-12 seconds** instead of ~25s — butterfly turbulence makes the Watch misread the pool length as complete before the swimmer even pushes off. This throws the whole workout out of sync.

This is a known Watch limitation. Keep 25yd FL as distance goals (open goals are not preferred). Just be aware the Watch may glitch on these — confirmed by workout CSV analysis on 2026-02-26 (Masters 0228 Fly Free 2).

### Rest Intervals Must Be Divisible by 5

All rest/recovery step durations must be rounded to the nearest 5 seconds.

- 49s → **50s**
- 22s → **20s**
- 28s → **30s**

Apply this rounding as the final step after calculating rest using the formula.

### Rest as Needed / Send-off Estimation Formula

For `rest as needed` or send-off intervals (`@M:SS` without `r`), calculate rest using:

```
estimated_work_time = distance × 0.68 × 1.2 × stroke_factor
rest_seconds = max(15, round(estimated_work_time × 0.30))

stroke_factor: FR=1.0, drill/kick/mixed=1.15, BK=1.25, IM=1.30, FL=1.35, BR=1.35
```

Quick reference (pre-rounded → final):
- 25yd FL → 8s → max(15) → **15s** rest
- 50yd FL/FR → 14s → max(15) → **15s** rest
- 75yd drill/FL → 22s → round to 5 → **20s** rest
- 100yd FR → 25s → **25s** rest
- 200yd FR build → 49s → round to 5 → **50s** rest

For send-off intervals, also cross-check: rest = send-off − estimated work time. Use whichever is more reasonable.

**Why this matters:** Using a flat 20s for all "rest as needed" underestimates rest for long efforts (e.g., 200 build to fast needs ~50s, not 20s) and is fine for short efforts.

### Rest Intervals: `:NNr` vs `@M:SS`

Steve uses two different rest/interval notations and they mean different things:

- **`:NNr` (with `r` suffix)** — Literal rest duration. `:15r` = 15 seconds rest. Use this value exactly.
- **`@M:SS` or `@:NN` (no `r` suffix)** — Send-off interval (total time from start to start). Calculate rest using the formula above.

**Never put raw notation in display names.** Recovery steps should always have `displayName: "Rest"`, with the actual seconds in the time goal. A previous bug showed "Rest @:35" on the Apple Watch — the notation leaked into the display name AND the time defaulted to 15 seconds instead of parsing the actual value.

### A/B/C Lane Differences

The same interval can use different notation systems across lanes. Example from Masters 0226 (Hold Focus):
- A lane: `@:35` (send-off, no `r`)
- B lane: `@45` (send-off)
- C lane: `:15r` (literal rest, has `r`)

These are equivalent patterns with different timing. Always default to A lane for .workout generation unless told otherwise.

### Warmup/Cooldown: Use Blocks, Not Fields

Do NOT use the `warmup` or `cooldown` top-level fields in the workout JSON. Instead, break every component into individual `blocks`. Reasons:

1. **Complex warmups get jumbled** — A warmup like "5 min easy / 200 pull / 4x50 drill" is three distinct exercises. One warmup step can't represent that.
2. **Apple "Work Distance" mismatch** — Apple excludes warmup/cooldown fields from "Work Distance", causing confusion. With everything in blocks, the full yardage shows correctly.
3. **Cooldowns are the same** — Even simple cooldowns go in blocks for consistency.

### Title Format

Steve's titles: `"Masters NNNN - Workout Name"` where NNNN is a sequential workout number (NOT a date). Simplify for the .workout file display name and filename:

```
YYYY-MM-DD [Workout Name] [Yardage] yds
```

The date comes from the API's `scheduledDateInteger`, not the workout number. The Masters number is not included — it's Steve's internal sequencing and not useful on the Watch.

### Workout Numbers vs Dates

Steve's workout numbers (e.g., 0226, 0227) are sequential and roughly correlate with dates but don't match exactly. Masters 0227 might be posted on Feb 25, not Feb 27. Always use the API's scheduled date for the filename/title.

### Validation Is Essential

Always cross-check the generated workout JSON against the source WOD before generating the binary:
- Sum block distances and verify against title yardage
- Verify every `:NNr` has a matching recovery step with exact seconds
- Check block count matches distinct exercises
- Check iteration counts match rep counts

### Interval Display Name Conventions

Two rules for how intervals are named on the Apple Watch:

**1. Don't duplicate the distance in the name.** The Watch already shows the distance below the interval name (e.g., "100yd"), so repeating it wastes space. Exception: when the interval has a subdivision (e.g., "25 Sprint / 25 Easy" for a 50yd block), keep the distances to explain the split.

| Distance | Raw description | displayName |
|----------|----------------|-------------|
| 200yd | 200 Pull | `Pull` |
| 100yd | 100 Zone 3 | `Zone 3` |
| 50yd | 25 Sprint / 25 Easy | `25 Sprint / 25 Easy` (subdivision) |

**2. Prefix every interval with its set label.** This tells the swimmer which section they're in. Format: `"[Set]: [Name]"`.

Set labels: `Warmup:`, `Main:`, `Pre-Set:`, `Drill Set:`, `Cooldown:`

Only add a round number (`Main 1:`, `Main 2:`) when an entire group of intervals repeats identically. If the exercises are different (e.g., Zone 3 in one half vs Zone 2 in the other), they're just different parts of the main set — use `Main:` for all of them.

Examples from Same Difference (0227):
- `Warmup: 5 Min Easy Choice`
- `Warmup: Pull`
- `Warmup: 25 Drill (3/3/2/2/1/1) / 25 Swim`
- `Main: Zone 3`
- `Main: 25 Sprint / 25 Easy`
- `Main: Pull Recovery`
- `Main: Zone 2`
- `Main: 25 Breathe 5 / 25 Easy`
- `Main: Pull Recovery`
- `Cooldown: Easy Choice`

### Common Workout Structures

Steve's workouts typically follow: Warm-up → (optional Pre-Set) → Main Set → Cooldown. Each distinct exercise pattern should be its own block in the .workout file.
