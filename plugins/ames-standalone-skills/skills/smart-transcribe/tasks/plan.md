# Implementation Plan: smart-transcribe Enhancements

Inspired by Matt Birchler's podcast-transcript-fixer and Federico Viticci's MacStories workflow.

## Overview

Four vertical features added to `smart-transcribe.py` (1340 lines) and `SKILL.md`:

1. **Per-context configuration** (`--context NAME`) — per-project dict overlay with first-run interview
2. **Transparency report** — LLM self-reports what it changed, flagged uncertainties, deliberately preserved
3. **Applied corrections display** — human reviews LLM's change log before save; can dispute entries
4. **Fix-transcript mode** (`--fix-transcript FILE`) — skip transcription, correct an existing SRT/VTT/TXT

## Architecture Decisions

- **No deterministic pre-pass for corrections.** Ambiguous dict entries like `"neck" → "Northeast Kingdom"` require context. The LLM already applies corrections with context; we extend its output to self-report them rather than adding a brittle regex layer.
- **4-part `---SPLIT---` format.** Extend the existing delimiter scheme: `metadata | transcript | transparency_report | suggestions`. Parser updated to handle both old (2-part, 3-part) and new (4-part) format — backwards compatible with `--transcribe-only` + `ensemble.py` paths.
- **Context dict merges on top of global.** Per-context corrections/entities/speakers/notes are deep-merged at load time. The user dict is never modified by context merge — contexts are additive overlays.
- **Fix-transcript reuses `merge_with_llm()`** with a single-source dict (`{"Source": text}`) and a modified system instruction. No new LLM call path needed.
- **Interactive corrections review is optional.** Default behavior displays the report and saves. Pass `--review` to get interactive y/n/skip on disputed items.

## Dependency Graph

```
Feature 2: per-context config
    (new _load_context(), merge_dicts(), --context arg)
    │
    ├── Feature 1: fix-transcript (needs context overlay, single-source merge)
    │
Feature 3: transparency report
    (updated merge prompt, 4-part parser, return type change)
    │
    └── Feature 4: applied corrections display
            (display function, --review interactive mode, MD output section)
```

Implementation order: **2 → 3 → 4 → 1** (context first, transparency second, display third, fix-transcript last)

---

## Phase 1: Per-Context Configuration

### Task 1: Per-context config layer

**Description:** Add `--context NAME` flag. On first use of a named context, run a short interview to gather context-specific terms (recurring proper nouns, hosts/speakers, domain notes). Store in `~/.config/smart-transcribe/contexts/<name>.json`. On subsequent uses, load and deep-merge over the global user dictionary — same schema as the main dictionary.

**Acceptance criteria:**
- [ ] `--context bcbs-vt` loads `~/.config/smart-transcribe/contexts/bcbs-vt.json` if it exists
- [ ] First run with a new context name triggers 3-question interview (recurring names, terms, notes)
- [ ] Interview output is saved to the context file in the standard dict schema
- [ ] Context corrections/entities/speakers/notes are deep-merged onto the base dict before any use
- [ ] `--context` with no name arg prints list of saved contexts and exits cleanly
- [ ] Existing runs without `--context` are unaffected

**Verification:**
- [ ] `python3 smart-transcribe.py audio.m4a --context test-ctx` prompts interview on first run
- [ ] Second run with same `--context` skips interview and shows "Loaded context: test-ctx"
- [ ] Dict merge: if global has `"corrections": {"a": "A"}` and context has `"corrections": {"b": "B"}`, result has both

**Dependencies:** None

**Files touched:**
- `scripts/smart-transcribe.py` — `_load_context()`, `_run_context_interview()`, `merge_dicts()`, `--context` argparse, STAGE 1 dict load

**Scope:** Medium (4 new functions, ~80 lines)

---

## Checkpoint: After Task 1

- [ ] `--context` round-trips (create → load → merge) without errors
- [ ] Existing tests / normal invocation unaffected

---

## Phase 2: Transparency Report

### Task 2: Extended LLM output format (4-part)

**Description:** Update `merge_with_llm()` to request a 4-part output: metadata, transcript, transparency report, suggestions. The transparency report section has three sub-sections: `APPLIED` (corrections used), `UNCERTAIN` (passages where correct form is unknowable), and `PRESERVED` (things left intentionally untouched). Update the `---SPLIT---` parser to handle 2/3/4 parts gracefully. Return the transparency report string alongside existing return values.

**Acceptance criteria:**
- [ ] Merge prompt instructs LLM to output 4 `---SPLIT---` sections in exact order
- [ ] Prompt explicitly instructs: do not correct unverifiable product names/version numbers; preserve casual speech; list uncertainties in the report
- [ ] `merge_with_llm()` returns `(transcript, suggestions, metadata, transparency_report)` — 4-tuple
- [ ] Old 2/3-part responses still parse without crash (transparency_report = "" in that case)
- [ ] All three call sites in `main()` updated to unpack 4-tuple

**Verification:**
- [ ] Run with `--model opus` or `--model gemini`, verify output contains all 4 `---SPLIT---` sections
- [ ] Verify APPLIED / UNCERTAIN / PRESERVED sub-sections appear in report text

**Dependencies:** None (independent of Task 1)

**Files touched:**
- `scripts/smart-transcribe.py` — `merge_with_llm()` prompt, parser block, return type, `main()` unpack

**Scope:** Medium (prompt rewrite ~40 lines, parser update ~20 lines)

---

### Task 3: Display transparency report + include in output MD

**Description:** After merge, print the transparency report to the terminal in a readable format (grouped by APPLIED / UNCERTAIN / PRESERVED). Append the report as a collapsible `## Transparency Report` section at the end of the saved `.md` file. No interactivity yet — just display and record.

**Acceptance criteria:**
- [ ] Terminal output shows structured report after merge, before "DONE" banner
- [ ] APPLIED section lists each correction as `"wrong" → "Right" (context snippet)`
- [ ] UNCERTAIN section lists passages the LLM wasn't sure about
- [ ] PRESERVED section lists things intentionally left alone
- [ ] Output `.md` includes `## Transparency Report` section after the transcript

**Verification:**
- [ ] Run a real transcription and confirm all three sub-sections appear in terminal output
- [ ] Open saved `.md` — scroll to bottom, verify Transparency Report section is present

**Dependencies:** Task 2

**Files touched:**
- `scripts/smart-transcribe.py` — new `display_transparency_report()` function, `main()` output stage

**Scope:** Small (new display function ~30 lines, MD output change ~10 lines)

---

## Checkpoint: After Tasks 2–3

- [ ] Full pipeline produces 4-section output from LLM
- [ ] Terminal report is legible and grouped
- [ ] `.md` output includes Transparency Report
- [ ] Human review: report content is accurate and useful

---

## Phase 3: Interactive Corrections Review

### Task 4: `--review` mode for disputed corrections

**Description:** Add `--review` flag. When set, after displaying the transparency report, prompt the user interactively for each item in the APPLIED section: `[y] keep  [n] remove from dict  [s] skip`. Items marked `n` are written to the suggestions log as `status: "disputed"` with the wrong→right mapping, allowing future dict cleanup. Without `--review`, behavior is unchanged (display only, no prompts).

**Acceptance criteria:**
- [ ] `--review` flag is documented in `--help`
- [ ] With `--review`, each APPLIED item is presented with a snippet and `[y/n/s]` prompt
- [ ] `n` writes a `{status: "disputed", wrong: ..., right: ...}` entry to suggestions log
- [ ] `s` skips the item without writing anything
- [ ] After review loop, save proceeds normally
- [ ] Without `--review`, no prompts appear (existing behavior preserved)

**Verification:**
- [ ] Run `python3 smart-transcribe.py audio.m4a --review`, step through prompts
- [ ] After marking an item `n`, confirm entry appears in `~/.config/smart-transcribe/suggested-additions.jsonl` with `"status": "disputed"`

**Dependencies:** Tasks 2, 3

**Files touched:**
- `scripts/smart-transcribe.py` — new `interactive_corrections_review()` function, `--review` argparse, `main()`

**Scope:** Small (~40 lines)

---

## Checkpoint: After Task 4

- [ ] Full pipeline with `--review` works end-to-end
- [ ] Disputed entries logged correctly
- [ ] Without `--review` no behavior change

---

## Phase 4: Fix-Transcript Mode

### Task 5: SRT/VTT/TXT parsers

**Description:** Add three pure-Python parsers: `parse_srt(path)`, `parse_vtt(path)`, `parse_txt(path)`. Each returns plain text (stripped of timestamps and cue headers). SRT and VTT are the formats produced by Whisper, YouTube, Riverside, and Descript. All three should be robust to missing/malformed timing lines.

**Acceptance criteria:**
- [ ] `parse_srt()` strips sequence numbers, `HH:MM:SS,ms --> HH:MM:SS,ms` lines, blank separators; returns dialogue text
- [ ] `parse_vtt()` strips `WEBVTT` header, `NOTE` blocks, `HH:MM:SS.ms --> HH:MM:SS.ms` lines; returns dialogue text
- [ ] `parse_txt()` returns file content as-is (no-op, for plain text input)
- [ ] All three handle empty files without crashing
- [ ] Auto-detection from file extension

**Verification:**
- [ ] Feed a sample `.srt` file; verify output is clean dialogue only (no timestamps)
- [ ] Feed a sample `.vtt` file; same verification

**Dependencies:** None

**Files touched:**
- `scripts/smart-transcribe.py` — 3 new functions (~50 lines total)

**Scope:** Small

---

### Task 6: `--fix-transcript` mode wired into main()

**Description:** Add `--fix-transcript FILE` as a mutually-exclusive alternative to the positional `audio_file` argument. When set: skip compression, skip transcription phases, parse the input file, run single-source `merge_with_llm()` (with adapted system prompt: "review and correct" not "merge two engines"), apply context overlay if `--context` provided, display transparency report, optionally run `--review` loop, save corrected transcript to output dir alongside a copy of the original. Never modifies the source file.

**Acceptance criteria:**
- [ ] `python3 smart-transcribe.py --fix-transcript transcript.srt` works with no audio file
- [ ] `--fix-transcript` and positional `audio_file` are mutually exclusive (argparse enforces)
- [ ] Input formats accepted: `.srt`, `.vtt`, `.txt`, `.md`
- [ ] LLM prompt for fix mode says "review and correct" not "merge two engines"
- [ ] Output dir contains: corrected `.md` transcript + `original.<ext>` copy
- [ ] Transparency report and `--review` work the same as in audio mode
- [ ] `--context` overlay works in fix mode

**Verification:**
- [ ] Run on a real `.srt` from Whisper; inspect corrected output vs. original
- [ ] Confirm original file is copied, not modified
- [ ] Run with `--context bcbs-vt`; verify context terms appear in corrections

**Dependencies:** Tasks 1, 2, 3, 4, 5

**Files touched:**
- `scripts/smart-transcribe.py` — `main()` argument parsing, new fix-mode branch, prompt variant

**Scope:** Medium (~80 lines in main + prompt update)

---

### Task 7: SKILL.md documentation update

**Description:** Update `SKILL.md` to document all four new capabilities: `--context`, `--review`, `--fix-transcript`, and the Transparency Report output. Add a "Fix-Transcript Mode" section. Update the Usage, Modes, and Architecture sections.

**Acceptance criteria:**
- [ ] `--fix-transcript FILE` documented with input format list
- [ ] `--context NAME` documented with first-run interview description
- [ ] `--review` documented in Usage section
- [ ] Transparency Report documented in Architecture section
- [ ] Accepted input formats for fix mode listed

**Dependencies:** Tasks 1–6 complete

**Files touched:**
- `SKILL.md`

**Scope:** Small (~30 lines added/updated)

---

## Checkpoint: Complete

- [ ] All 7 tasks pass their acceptance criteria
- [ ] Full pipeline (audio → fix-transcript) works with `--context` + `--review`
- [ ] SKILL.md reflects all new capabilities
- [ ] `./sync` run in ames-claude to update marketplace.json

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM doesn't reliably produce 4-part output | Med | Fallback to 3-part parser; transparency_report = "" |
| Ambiguous dict entries cause noisy APPLIED list | Low | LLM self-filters based on context; noisy entries show in UNCERTAIN |
| SRT/VTT format variations from different tools | Med | Regex-based parsers with liberal whitespace handling |
| Context deep-merge key collisions | Low | Context takes precedence over global (overlay semantics) |

## Open Questions

- Should `--fix-transcript` support URLs (YouTube transcript links)? Defer for now.
- Should disputed corrections trigger automatic dict pruning, or just flag for manual review? Flag only for now.
