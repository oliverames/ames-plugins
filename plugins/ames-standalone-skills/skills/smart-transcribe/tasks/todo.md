# smart-transcribe Enhancement Tasks

## Phase 1: Per-Context Configuration
- [x] Task 1: Per-context config layer (`--context NAME`, interview, merge)

## Checkpoint 1
- [x] `--context` round-trips without errors; existing behavior unaffected

## Phase 2: Transparency Report
- [x] Task 2: Extended LLM output format (4-part `---SPLIT---`, prompt rewrite, return type)
- [x] Task 3: Display transparency report + append to output `.md`

## Checkpoint 2
- [x] Full pipeline produces structured transparency report in terminal and saved `.md`

## Phase 3: Interactive Corrections Review
- [x] Task 4: `--review` interactive mode (y/n/s per APPLIED item, disputed log)

## Checkpoint 3
- [x] `--review` works end-to-end; disputed entries logged; without flag, no behavior change

## Phase 4: Fix-Transcript Mode
- [x] Task 5: SRT/VTT/TXT parsers (pure Python, strip timestamps)
- [x] Task 6: `--fix-transcript FILE` wired into `main()` (new code path, prompt variant, output)
- [x] Task 7: SKILL.md documentation update

## Checkpoint 4 (Final)
- [x] All acceptance criteria met
- [ ] `./sync` run in ames-claude repo (run when ready to publish)

## 2026-04-09 Runtime Hardening Follow-Up
- [x] Default transcription trio locked to `assemblyai-u3-pro`, `scribe-v2`, and `cohere-transcribe`
- [x] Headless merge aligned to `claude -p` with automatic `codex exec` fallback
- [x] `--doctor` and `--check-engine` updated to inspect engine runtimes instead of the launcher interpreter
- [x] Fix-transcript output aligned with the main output contract (metadata header, transparency section, sidecar JSON)
- [x] `XDG_DATA_HOME` handling corrected so config lives under `smart-transcribe/`
- [ ] Full live end-to-end transcription against external APIs still pending
