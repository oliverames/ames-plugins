---
name: wrap-up
version: 4.2.0
description: This skill should be used when the user says "wrap up", "close
  session", "end session", "wrap things up", "close out this task", or invokes
  /wrap-up, "done for the day", or "session complete". Runs an end-of-session
  checklist covering shipping, memory, and self-improvement.
---

# Session Wrap-Up

Based on [jonathanmalkin's self-improvement loop](https://www.reddit.com/r/ClaudeCode/comments/1r89084/selfimprovement_loop_my_favorite_claude_code_skill/).

**Convention for session start** (not auto-triggered by this skill): When
beginning work in a project repo, check for `WORKLOG.md` and read the most
recent entry to orient on where the last session left off. Especially
valuable when switching between projects or picking up after days away.

---

## Phase 0: Triage

Assess what happened this session before running phases:

- **Trivial** (typo fix, config tweak, single small commit): Run Phase 1
  commit + push only, then Phase 4 reminder. Skip everything else. Say
  "Quick session — committed and pushed."
- **Standard** (single repo, clear scope, meaningful changes): Run all
  phases.
- **Deep** (multi-repo, major feature, audit, or architecture session): Run
  all phases. Pay extra attention to Phase 1.5 (multiple repos may need
  worklogs) and Phase 2 (more likely to have learnings worth persisting).

Classify based on: number of repos touched, number of commits, whether
the session involved decisions or just execution, and overall duration
implied by the conversation length.

---

Run phases in order. Each phase is conversational and inline — no separate
documents. Auto-apply all actions without asking.

## Phase 1: Ship It

**Commit:**
1. Run `git status` in each repo directory that was touched during the session
2. If uncommitted changes exist, auto-commit to main with a descriptive message
3. Push to remote

**File placement check:**
4. If any **document-type files** (.md, .docx, .pdf, .xlsx, .pptx, media
   files) were created or saved outside of source code directories:
   - Invoke the `file-organization` skill to verify naming conventions
   - Auto-fix naming violations by renaming the file
   - Move misplaced files to their correct location
5. Skip for source code files — those follow language/project conventions,
   not document naming rules

**README check:**
6. If the session made significant changes (new features, renamed things,
   changed APIs, added/removed tools), check if `README.md` is stale:
   - Compare what the README claims (feature counts, tool lists, config
     options, usage examples) against the actual current state
   - If stale, update the affected sections to match reality
   - Common staleness: tool/feature counts, config tables missing new env
     vars, outdated usage examples, architecture sections missing new files
7. Skip if changes were purely internal (bug fixes, refactors) with no
   user-facing impact

**CLAUDE.md freshness check:**
8. If the session made changes that affect project conventions, structure,
   or workflows: check if `CLAUDE.md` in the affected repo is stale
9. Update any sections that no longer match reality
10. CLAUDE.md files can become very stale — if you notice significant drift,
    flag it and fix it

**Apple Notes "💻 Tech" check:**
11. Use the `apple-notes` MCP to search notes in the "💻 Tech" folder that
    are related to what was worked on this session (search by project name,
    tool name, or key terms from the session)
12. For each matching note found, evaluate whether its content is stale or
    incomplete given the session's changes:
    - New setup steps added, removed, or changed?
    - Config values, paths, or commands that have changed?
    - Gotchas or workarounds that have been resolved?
    - New gotchas or learnings that aren't yet captured?
13. If a note needs updating, **invoke the `apple-notes-formatting` skill
    first** to produce correctly-styled content (headings, checklists,
    code blocks, spacing per the user's canonical rules), then use
    `apple-notes` to write the update. Never write raw markdown or
    model-default formatting — always route through the formatting skill
14. If a new topic was covered that warrants a new note (e.g. a tool or
    workflow not yet documented), draft the body through
    `apple-notes-formatting` first, then create it in the "💻 Tech" folder
15. Report what was found and changed (or "No matching Tech notes")
16. Skip this step for trivial sessions (Phase 0 triage)

**Deploy:**
17. Check if the project has a deploy skill or script
18. If one exists, run it
19. If not, skip deployment entirely — do not ask about manual deployment

**Publish:**
20. If `package.json` exists in the project root:
    - Run `npm view <package-name> version` to get the published version
    - Compare against the local `package.json` version
    - If the local version is newer (bumped during this session), run
      `npm publish` to push the new version
    - If the versions match, skip — nothing to publish
    - If no published version exists (404), this is a new package — ask
      the user before first publish
21. If no `package.json` exists, skip entirely

**Task cleanup:**
22. Check the task list for in-progress or stale items
23. Mark completed tasks as done, flag orphaned ones

## Phase 1.5: WORKLOG.md

If this session worked in a project repo (not just `~/.claude/` or standalone
scripts), generate a worklog entry:

1. **Read the previous WORKLOG entry** (if one exists). Check:
   - Were any "Left off at" items completed this session? Note them as
     resolved.
   - Are any "Left off at" items still undone? Carry them forward explicitly
     in the new entry's "Left off at" rather than re-inventing them.
   - Have any "Open questions" been answered? Note the resolution.
   - Have any "Open questions" appeared in 3+ consecutive entries without
     progress? Either promote them to a GitHub issue / Things task, or
     explicitly drop them with a note ("Dropped — not worth pursuing
     because...").
2. Run `git log --oneline -10` and `git diff HEAD~5..HEAD --stat` (or similar)
   to review what changed during this session
3. Generate an entry with four fields:
   - **What changed** — human-readable summary of the session's changes
   - **Decisions made** — key decisions and WHY (the things git log doesn't capture)
   - **Left off at** — where to pick up next session. **This is the most
     valuable field** — be specific about what the next session should start
     with. Clearly distinguish:
     - NEW items from this session
     - CARRIED items from the previous entry (prefix with "Still open:")
   - **Open questions** — parking lot for things to revisit
4. Prepend the entry to `WORKLOG.md` in the project root. If the file doesn't
   exist, create it starting with `# Worklog\n\n`
5. Use this format:
   ```
   ## YYYY-MM-DD — [Brief summary]

   **What changed**: ...

   **Decisions made**: ...

   **Left off at**: ...

   **Open questions**: ...

   ---
   ```
6. Commit the entry: `git add WORKLOG.md && git commit -m "worklog: [brief summary]"`

**Multi-repo sessions**: If this session made meaningful changes in
multiple project repos:
- Write a worklog entry in each project repo that had substantive changes
- Each entry should cover only what changed in THAT repo
- Add a cross-reference line: "Part of a broader session that also
  touched [list other repos]"
- `Developer/Scripts` doesn't need a worklog — it's not a git repo

**Skip this phase** if the session only touched config files, memory, or
non-project work.

## Phase 2: Remember It

Scan the conversation for knowledge worth persisting. This is a structured
review, not a vague pass.

**Step 1 — Scan for these specific signals:**
- User corrections ("no, that's wrong", "don't do it that way", "actually...")
- User confirmations of non-obvious approaches ("yes exactly", "perfect",
  accepting an unusual choice)
- Facts about project setup, architecture, or quirks that weren't
  previously known
- External system locations (URLs, API endpoints, dashboard links)
- Preferences expressed (tool choices, style opinions, workflow preferences)

**Step 2 — Classify each finding:**
- Already documented somewhere? → Skip
- Permanent project convention? → CLAUDE.md or `.claude/rules/`
- Scoped to specific file types/paths? → `.claude/rules/` with `paths:`
- Pattern or insight Claude discovered? → Auto memory
- Personal/ephemeral context? → `CLAUDE.local.md`
- Duplicating content from another file? → `@import` instead

**Step 3 — Apply and report:**
Write the applicable items. Report in one line per item:

```
Memory: Saved 2, updated 1, skipped 3 (already known)
- [NEW] feedback: user prefers X over Y
- [NEW] reference: dashboard URL for service Z
- [UPDATED] project: added new teammate info
```

If nothing worth persisting was learned, say "Nothing new to remember"
and move on.

## Phase 3: Review & Apply

Analyze the conversation for self-improvement findings. If the session was
short or routine with nothing notable, say "Nothing to improve" and proceed
to Phase 4.

Auto-apply all actionable findings immediately — do not ask for approval on
each one. Apply the changes, commit them, then present a summary.

**Finding categories:**
- **Skill gap** — Things Claude struggled with, got wrong, or needed multiple
  attempts
- **Friction** — Repeated manual steps, things user had to ask for explicitly
  that should have been automatic
- **Knowledge** — Facts about projects, preferences, or setup that Claude
  didn't know but should have
- **Automation** — Repetitive patterns that could become skills, hooks, or
  scripts
- **Validated approach** — Things that worked well and should be repeated
  in similar situations. These are easy to miss because success is quiet.
  Look for: approaches the user confirmed, techniques that found real bugs,
  workflows that were efficient.

**Action types:**
- **CLAUDE.md** — Edit the relevant project or global CLAUDE.md
- **Rules** — Create or update a `.claude/rules/` file
- **Auto memory** — Save an insight for future sessions
- **Skill / Hook** — Document a new skill or hook spec for implementation
- **CLAUDE.local.md** — Create or update per-project local memory

Present a summary after applying, in two sections — applied items first,
then no-action items:

```
Findings (applied):

1. done Skill gap: Cost estimates were wrong multiple times
   -> [CLAUDE.md] Added token counting reference table

2. done Validated approach: Parallel subagents cut review time by 60%
   -> [Memory] Saved: Use parallel agents for large code reviews

---
No action needed:

3. Knowledge: Discovered X works this way
   Already documented in CLAUDE.md
```

## Phase 4: Backup & Sign Off

**Run backups:**
1. Run `backup-claude` to back up memory, plans, and teams to the private repo
2. Run `backup-telegram` if any Telegram config was changed this session
3. Run `commit-push-all` to catch any remaining uncommitted repos

**Print a brief session report and exit. Format:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Session complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Commits:  3 across 2 repos
  Memory:   1 new, 1 updated
  Worklog:  Written to sprout-mcp-server
  Notes:    Updated 1 Tech note, created 0
  Backup:   Memory backed up

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Adapt the stats to what actually happened. Omit lines for phases that
had nothing to report (e.g., no memory changes = no Memory line). For
trivial sessions (Phase 0 triage), keep it to two lines:

```
Committed and pushed. Backup complete.
```

After printing the report, stop. Do not run any exit command.
