---
name: go
description: Use when the user ends a prompt with "/go" or says "go" as a shorthand for "ship it". Runs the full end-to-end verification-and-ship pipeline before declaring a task done. Triggers on "/go", "ship this", "take it home", "finish it up", or appended "/go" at the end of any implementation request.
---

# /go — Verify, Simplify, Ship

Oliver uses `/go` as a terminal instruction on implementation prompts. It means: "you have autonomy to finish this — run through my standard pre-ship pipeline before you hand back."

Invoke this skill when `/go` appears at the end of a request, or when the user asks to "ship it", "take it home", or "finish it up". Do NOT invoke on read-only / research / question-style prompts.

## The pipeline

Run these phases in order. Stop at the first phase that surfaces a real problem, report it, and ask before continuing.

### Phase 1 — Verify end-to-end

Prove the code works at runtime. Compile success and unit tests passing are NOT enough (see Oliver's `feedback_verify_ui_before_done` memory).

Pick the verification mode that fits the change:

- **Backend / CLI / scripts** — actually invoke the entry point with real input. Check exit code, logs, and output. If there's a dev server, start it and hit the relevant endpoint.
- **Frontend / web** — use the `mcp__claude-in-chrome__*` tools (or the `chrome-devtools-mcp` plugin) to load the page and exercise the feature. Take a screenshot of the rendered state.
- **SwiftUI / AppKit / iOS / macOS app** — build, launch in simulator or locally, and screenshot the rendered UI. Compile success alone is insufficient.
- **Pure library / data transform** — run the test suite AND write at least one new test that exercises the change you just made. Don't rely solely on existing tests.

Report what you ran and what you observed — concrete output, not "seems to work."

### Phase 2 — Simplify

Invoke the `simplify` skill (top-level, bundled with Claude Code). It reviews the diff for unnecessary complexity, dead code, premature abstractions, and duplication, and applies fixes.

If the diff is trivial (one-line fix, config tweak, version bump), skip this phase and say "Skipped simplify — trivial change."

### Phase 3 — Ship

Decide the shipping path based on what you changed:

- **Inside a git repo with a remote and uncommitted changes** — invoke `commit-commands:commit-push-pr` to commit, push, and open a PR.
- **Inside a git repo but the branch is `main`/`master` with unpushed commits** — commit + push only (no PR); confirm with user first if anything looks risky.
- **Plugin or skill changes in `~/Developer/Projects/ames-claude`** — run `./sync` first to regenerate `marketplace.json`, THEN commit + push. The marketplace won't update without sync.
- **Outside a git repo or local-only config files** — just report what changed and where. No git action.

## Phase 0 — pre-flight (quick checks before Phase 1)

Before running the pipeline, do a 10-second sanity pass:

1. **Is anything actually done?** If the implementation is incomplete or stubbed, stop and finish the work first. `/go` ships finished work; it does not paper over half-done work.
2. **Are there obvious issues in the diff?** A quick `git diff` scan catches accidentally-committed debug prints, leftover TODOs, or secrets.
3. **Did you introduce new files that should be in `.gitignore`?** `.claude/settings.local.json`, `.env`, log files, etc.

If any of these fail, fix them before Phase 1.

## When NOT to use /go

- Read-only or research tasks — nothing to ship.
- Destructive git operations requested by the user (force-push, reset --hard) — `/go` stops at commit+push+PR, never rewrites history.
- Operations across shared infrastructure — per Oliver's CLAUDE.md, pause and confirm before shared-state changes regardless of `/go`.

## Reporting

When the pipeline completes, report in this shape:

```
✅ Verified: <what you ran, what you observed>
✅ Simplified: <what simplify changed, or "skipped — trivial">
✅ Shipped: <PR URL, commit hash, or "local only — no git">
```

If any phase fails or needs judgment, stop there and ask. Do not silently skip phases.
