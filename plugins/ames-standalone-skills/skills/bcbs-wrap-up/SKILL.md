---
name: bcbs-wrap-up
version: 1.6.0

description: >
  BCBS session wrap-up that runs end-to-end: updates evergreen notes, verifies
  action items are tracked in Jira (the canonical task system for BCBS),
  migrates any legacy Asana or Apple Reminders references into Jira, audits
  naming conventions, ensures directory organization is clean, then commits,
  writes a worklog, persists memory, and backs up.
when_to_use: >
  Oliver says "BCBS wrap up", "wrap up BCBS", "close out BCBS", "BCBS session
  done", "done with BCBS", "BCBS end of day", or invokes /bcbs-wrap-up. Run
  at the end of any BCBS working session.
disable-model-invocation: true
---

# BCBS Session Wrap-Up

End the session in a way that leaves Oliver's BCBS work trustworthy and easy
to resume. This skill is self-contained: it runs BCBS-specific cleanup (notes,
Jira, file placement, naming), then closes out with git commits, worklog,
memory, and backups — no chaining to `/wrap-up` needed.

## Prime Directive

Run a deterministic preflight first, then execute only the phases that are
valid for the current host and directory state. Missing optional tools are not
failures. Skip them, say why, and keep closing the session.

Locate the bundled preflight helper from the wrap-up skill and run it:

```bash
WUP=$(find ~/.claude/plugins -name "wrap-up-preflight.py" 2>/dev/null | head -1)
[ -n "$WUP" ] && python3 "$WUP" --host auto --json || echo "preflight helper unavailable, continuing manually"
```

If the helper is missing, continue manually using the checks listed below
and report that the helper was unavailable.

## Safety Rules

- Never read or print secret values. For `~/.claude/settings.json`, read only
  targeted non-secret fields such as `enabledPlugins`, `extraKnownMarketplaces`,
  `permissions`, `hooks`, and top-level behavior keys. Do not read `env`.
- Do not blindly run destructive or catch-all commands. `commit-push-all` is a
  final safety net only when preflight and git status show expected repos and
  no unrelated dirty work.
- Before editing skills, configs, or user documents during wrap-up, rely on git,
  iCloud, and Time Machine for revert protection. Do not create `.bak` files. If
  making an irreversible change to a file with uncommitted edits, stage or commit
  the current state first.
- Preserve user changes. If a repo already has unrelated dirty files, work
  around them and mention the residual state instead of staging everything.

## BCBS Operating Defaults

- **Jira is the canonical task system. Period.** Use the Blue Cross VT
  Jira workspace (`bluecrossvt.atlassian.net`) and structured
  Jira/Atlassian MCP tools for projects, issue search, issue creation, and
  issue updates. Do not rely on Asana, Apple Reminders, Todoist, or any
  other task system as a source of truth, and never defer a Jira action to
  those systems. If Oliver explicitly asks for a different system in the
  current request, follow that request and flag it as an exception.
- **Verify Jira before acting.** Confirm the accessible Jira workspace and
  destination project before creating or updating issues. Prefer structured
  project and JQL tools over generic search when available.
- **Strikethrough means tracked in Jira.** A struck-through action item
  with a `*(→ Jira: ISSUE-123)*` tag is the local note signal that the task
  exists in Jira. Strikethrough without a Jira tag is stale and should be
  reconciled during wrap-up.
- **Legacy Asana or Apple Reminders tags must be migrated.** Any item
  tagged `*(→ Asana: ...)*` or `*(→ Reminders: ...)*` in notes or trackers
  represents a task that should be re-created in Jira. Flag each legacy tag
  encountered during wrap-up. Do not silently treat an Asana or Reminders
  tag as equivalent to a Jira tag. Prompt Oliver to confirm migration, then
  create the Jira issue and update the local tag to `*(→ Jira: ISSUE-123)*`.
- **Wrap-up never closes a Jira issue.** This skill verifies existence,
  creates missing issues, and migrates legacy tags. It does not transition
  a Jira issue to Done, Resolved, or any terminal status, and it does not
  mark an action item checkbox complete based on a deliverable produced in
  the same session. Closing happens only when Oliver (or the designated
  reviewer) confirms the work meets the acceptance criteria for that
  ticket. If a local tracker uses checkboxes, leave items unchecked and
  append a "Draft delivered YYYY-MM-DD at <path>" note instead.
- **Route tasks to the correct Jira project.** Team tasks go in **BAE**
  (Brand & Engagement) — visible to the team, has due dates, or affects
  others. Personal or research tasks that only Oliver needs to see go in
  **OA** (Oliver's Space). Rule of thumb: if Ashley or a teammate would
  act on it or track it, it is BAE; if it is a personal reminder or
  research item, it is OA.
- **Only assign Jira issues to Oliver.** Never assign issues to other
  team members during automated task creation. If an action item belongs
  to someone else, capture their name in the task description rather than
  assigning the Jira issue to them.
- **Check for duplicates before creating.** Before creating a Jira issue,
  run a JQL search (e.g. `project = BAE AND summary ~ "..."`) to confirm
  no matching issue already exists. Reference the existing key instead of
  creating a duplicate.
- **Jira descriptions must not reveal their source.** Do not include
  "Source: [meeting name]", "from a recording", "transcript", "from
  audio", or any AI-generation references in Jira descriptions. Write
  descriptions as natural task context indistinguishable from a human
  note — the kind that could appear in any team sprint review.

Run phases in order. Auto-apply all actions without asking unless a step
says otherwise. Use subagents for parallel work where noted.

---

## Phase 0: Preflight

1. Run the preflight helper if available (see Prime Directive).
2. Identify touched paths:
   - Start with `~/Documents/BCBS/` using `find ~/Documents/BCBS -mtime -1`
     to surface files modified today.
   - Add any git repos clearly modified or discussed in the session.
   - For recent Claude Code sessions, prefer fresh `WORKLOG.md` entries and
     `~/.claude/projects/*/*.jsonl` summaries over old memories.
3. Classify scope:
   - **Trivial**: one small note update, no Jira actions needed, no file moves.
   - **Standard**: one meeting processed, action items tracked, typical notes.
   - **Deep**: multiple projects touched, Jira project sync, large file
     organization, naming audits, or significant new context added.

Stop and re-plan if preflight finds a real contradiction: missing expected
files, malformed notes, failed required Jira verification, or dirty git state
that would be unsafe to stage.

---

## Phase 1: Identify Session Work

Scan the conversation history and recent file modifications to determine
what was worked on this session:

1. List all files modified today in `~/Documents/BCBS/` (use `find -mtime -1`)
2. Identify which transcripts were processed, which notes were written or
   edited, and which projects were touched
3. Build a working list of files that need wrap-up attention

---

## Phase 2: Update Evergreen Notes

The evergreen reference documents in `~/Documents/BCBS/Notes/` must stay
current. These are NOT meeting notes; they are living knowledge bases.

**Discovering evergreen files:**
The evergreen file list changes over time. Do not assume any fixed set of
filenames. Instead, discover what actually exists:

```bash
find ~/Documents/BCBS/Notes -maxdepth 1 -name "*.md" -not -name "Meetings" | sort
```

Review the returned files against today's session content. Update any
file whose coverage area was touched — people, tools, decisions, strategy.
Skip files whose topic area was not touched this session.

**Common evergreen topics** (file names vary):
- People, roles, and contacts
- Working context and org dynamics
- Social media strategy and tool access
- Platform audit and blockers
- Expenses and purchasing process
- File organization decisions

**Phased-out files (do not treat as active evergreens):**
- `BCBS VT – Task Tracker.md` — phased out as of 2026-04-23. Jira is the
  live home for open tasks. Do not append new tasks here. If the file
  still exists, treat it as a read-only archive; surface any items in it
  that are still live as candidates for Jira creation in Phase 3.

For each file:
1. Read the current content
2. Cross-reference with any transcripts or notes created/modified this session
3. If new information exists (people, dates, decisions, status changes), add
   it in the appropriate section matching the file's existing style
4. Do NOT rewrite sections; append or update specific entries

---

## Phase 3: Jira Task Verification

Jira is the only task system checked. Asana and Apple Reminders tags
encountered in notes must be migrated to Jira during this phase.

For every meeting note, tracker, or evergreen file modified this session:

1. Read the Action Items section (or equivalent).
2. For each action item that has a Jira issue tag such as
   `*(→ Jira: ISSUE-123)*`:
   - Verify the issue still exists in Jira using the structured
     Atlassian/Jira MCP tools.
   - Verify the item text is struck through: `~~item text~~`. If not
     struck through, add the strikethrough.
   - Do **not** transition the Jira issue to Done, Resolved, or any
     terminal status during wrap-up. Do not toggle a local checkbox to
     `[x]`. Wrap-up verifies capture; closure is a separate reviewer
     action.
3. For action items tagged with a legacy system (`*(→ Asana: ...)*`,
   `*(→ Reminders: ...)*`, or any non-Jira tag):
   - Flag each legacy tag in the wrap-up summary.
   - Determine whether the task is still live. If it is, confirm the
     Blue Cross VT Jira workspace, find the matching project, verify
     the issue type, and re-create the issue in Jira using structured
     Atlassian/Jira tools (visible-project lookup, JQL issue search,
     issue type metadata, issue creation, issue edit/update). In Codex,
     the Atlassian Rovo tools are the preferred path; in other hosts,
     use the equivalent Jira MCP tools discovered through the available
     tool surface.
   - Update the local tag to the new Jira key:
     `- [ ] ~~Task text~~ *(→ Jira: ISSUE-123)*`. Do not delete the
     original tag history from commits or version-controlled notes;
     overwriting in-place is fine for the working file.
   - If the task is stale or obsolete, note "(deprecated — no Jira
     equivalent needed)" and leave it unchecked.
4. For action items that do not have any routing tag:
   - Determine if they should be in Jira (non-trivial, owned by
     Oliver).
   - If yes, create the Jira issue as above and add the strikethrough
     and tag to the note.
   - Route to the correct Jira project based on content and visible
     Jira projects. Use local `~/Documents/BCBS/Projects/` folder names
     as search seeds when matching project names.

**Conventions:**

- A strikethrough on an action item means it is tracked in Jira. Items
  without a `(→ Jira: ...)` tag after wrap-up are not considered captured.
- Wrap-up never marks a Jira ticket done. Deliverables produced during
  the session get a "Draft delivered YYYY-MM-DD at <path>" inline note
  on the local item, with the checkbox left unchecked.

---

## Phase 4: File Placement Audit

Check that all files are in the correct location:

### Ashley & Oliver Meetings
Any meeting where Ashley and Oliver were the only participants (including
general one-on-ones) must be in:
```
~/Documents/BCBS/Ashley & Oliver Meetings/YYYY-MM-DD/
```
Both the transcript AND notes go in the same date folder.

### Project Files
Transcripts and notes about a specific project should be in:
```
~/Documents/BCBS/Projects/[Project Name]/
```
Route to a project folder if the meeting's subject matter maps to an
existing project — even if the project name never appears in the meeting
title. Read the transcript content to determine the subject. When in
doubt, route to a project rather than to Notes/Meetings.

### General Meetings (last resort)
Use `Notes/Meetings/` only when the meeting genuinely spans multiple
projects with no single clear home, or is an onboarding intro, all-hands,
or external multi-team call. This is the fallback of last resort; do not
default to it when a project folder is a reasonable fit.

### Social Folder
General Social folder files stay in Social. If posts or strategies are
project-specific, they should be moved to Projects.

---

## Phase 5: Naming Convention Audit

All `.md`, `.txt`, and `.docx` files with date prefixes must follow:
```
YYYY-MM-DD – [Description] – [Type].ext
```
Where `–` is an en-dash (U+2013), not a hyphen (-) or em-dash (U+2014).

Run this check (Python — the bash `grep -qE` approach produces false positives on macOS for multibyte Unicode):
```bash
python3 - << 'EOF'
import os, re

BCBS = os.path.expanduser("~/Documents/BCBS")
EM_DASH = '\u2014'
EN_DASH = '\u2013'
date_prefix = re.compile(r'^\d{4}-\d{2}-\d{2} ')

em_dash_files = []
missing_en_dash = []

for root, dirs, files in os.walk(BCBS):
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    for f in files:
        if not f.endswith(('.md', '.txt', '.docx')):
            continue
        if EM_DASH in f:
            em_dash_files.append(os.path.join(root, f))
        if date_prefix.match(f) and not f[11:].startswith(EN_DASH):
            missing_en_dash.append(os.path.join(root, f))

print("=== EM-DASH violations ===")
for p in em_dash_files: print(p)
print(f"\n=== MISSING EN-DASH violations ({len(missing_en_dash)}) ===")
for p in missing_en_dash: print(p)
EOF
```

Fix any violations by renaming with `mv`. Replace hyphens and em-dashes
with en-dashes in the separator positions.

You can also reference the "file-organization" skill.

---

## Phase 6: Jira Project Sync

Quick check that the local `Projects/` folder and Jira are in sync:

1. List `~/Documents/BCBS/Projects/` subdirectories
2. Confirm the Blue Cross VT Jira workspace, then list visible Jira projects
   with structured Jira/Atlassian tools
3. Flag any new local folders without Jira projects (and vice versa)
4. Report mismatches but do NOT auto-create projects without confirmation

---

## Phase 7: Verify And Ship

For each touched git repo:

1. Run `git status --short --branch`.
2. Review the diff for accidental secrets, debug leftovers, unrelated files,
   generated cache files, or changes made by someone else.
3. Run verification appropriate to the change:
   - **Skill/plugin**: run `validate-skill` when available, run repo `./sync`
     when marketplace manifests depend on it, and validate changed JSON.
   - **Docs only**: re-read the modified files and check links/paths/counts.
   - **CLI/script**: invoke the changed entry point with representative input.
4. Commit only intended changes in each repo. Use a clear message with the
   local convention (`fix:`, `docs:`, `chore:`, `worklog:`, etc.).
5. Push only after verification passes. If push fails, report the exact failure
   and leave the local commit in place.

### ames-plugins Plugin Special Case

When the session changed `~/Developer/Projects/ames-plugins` or its iCloud
resolved path:

1. Keep `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, and the
   regenerated marketplace entries in version parity.
2. Run `./sync` from the repo root after plugin version changes.
3. Validate both host manifests:
   ```bash
   python3 -m json.tool .claude-plugin/marketplace.json >/dev/null
   python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
   ```
4. Do not hand-edit generated marketplace JSON except to recover from a failed
   sync.

---

## Phase 8: Documentation Drift

Update documentation only when the session changed behavior, setup, public
commands, plugin layout, API surface, or config.

Check in this order:

1. `README.md`: user-facing capabilities, setup commands, tool counts, paths,
   examples, env var names, and plugin or MCP inventories.
2. `CLAUDE.md`: Claude Code workflow conventions, plugin hygiene, settings
   expectations, and host-specific notes.
3. `AGENTS.md`: Codex workflow conventions, plugin manifests, Codex settings,
   and host-specific notes.
4. Project-specific docs: only the section made stale by this session.

For config-record drift:

- **Claude Code**: if `~/.claude/settings.json`, Claude plugins, MCPs,
  marketplaces, hooks, permissions, model defaults, or UI behavior changed,
  update the repo's Claude Code config reference. Use targeted reads and do not
  expose `env` values. If Apple Notes tools are available, also consider the
  `💻 Claude Code Setup` note or related `💻 Tech` notes.
- If a docs target is intentionally duplicated in README and Apple Notes,
  update both only when the required tool is available. Otherwise update the
  repo source of truth and report the skipped note update.

---

## Phase 9: Worklog

Write a `WORKLOG.md` entry for every project repo with meaningful work. Skip
for one-off config-only sessions unless the config lives in a project repo and
future context would otherwise be lost.

Before writing:

1. Read the latest existing entry.
2. Check whether carried items were resolved, still open, or obsolete.
3. Use `git log --oneline -10`, `git diff --stat`, and the session context to
   avoid inventing a narrative.

Entry format:

```markdown
## YYYY-MM-DD - Brief summary

**What changed**: ...

**Decisions made**: ...

**Left off at**: ...

**Open questions**: ...

---
```

Rules:

- Put concrete verification in the entry when the project changed code.
- Distinguish `NEW`, `Still open`, and `Resolved this session`.
- Carry forward unresolved prior items explicitly, do not silently drop them.
- For multi-repo sessions, write one entry per repo and mention the related
  repos in prose.
- Prefer concise, factual entries over blow-by-blow logs.

---

## Phase 10: Memory, Notes, And Self-Improvement

Persist only knowledge that will matter in future sessions.

Scan for:

- user corrections or durable preferences,
- project setup quirks,
- commands that failed and their working replacements,
- new external URLs or dashboard locations,
- validated approaches that should be repeated.

Apply by host:

- **Claude Code**: use the available project/global memory mechanism, local
  `CLAUDE.local.md`, project `CLAUDE.md`, or `.claude/rules/` as appropriate.
- **Apple Notes**: before declaring the tool unavailable, discover the current
  tool surface. If Apple Notes write tools exist, route content through
  `apple-notes-formatting` first. If not, skip with a clear reason.

When a skill's documented command failed in practice, update the skill source
during the session if it is safe and in scope. The skill is canonical; memory is
only a recall cache.

---

## Phase 11: Backups And Final Sweep

Run only available and relevant commands:

1. `backup-claude`: run when Claude Code memory/config changed and the command
   exists.
2. `commit-push-all`: use only after verifying the repos it would touch are
   expected. If the script supports a dry run, run that first. If it does not,
   prefer explicit repo commits unless this was a deep multi-repo cleanup.

Then run a final status pass for every touched repo and note any residual dirty
files that are unrelated or intentionally left open.

---

## Final Report

Keep the report short and concrete. Include only lines that apply:

```text
Session complete

Verified: <commands and observed results>
Shipped: <commits/pushes or "local changes only">
Worklog: <repos updated or skipped>
Docs: <files/notes updated or skipped>
Memory: <saved, candidates, or nothing new>
Backup: <commands run or skipped reason>
Residual: <known dirty files or blockers>
BCBS: <evergreen files updated, Jira actions taken, naming fixes applied>
```

If the session was trivial:

```text
Committed and pushed. Backup complete.
```

After the report, stop. Do not run an exit command.

---

## Reference

### Naming Convention
- Date prefix: `YYYY-MM-DD`
- Separator: space-en-dash-space (` – ` with U+2013)
- Title Case for descriptions
- Suffixes: `– Transcript`, `– Notes` for meeting files

### Jira Projects

| Project | Key | Use for |
|---------|-----|---------|
| Brand & Engagement | BAE | All team-facing tasks; workstreams, events, campaigns, social, content |
| Oliver's Space | OA | Personal/research tasks not ready for team visibility |
| Photography | PICS | Photo shoots, headshots, event photography logistics |

**Do not hardcode workstream names or issue numbers in this skill.**
Workstreams are added and archived regularly. Always discover the current
list at runtime before creating a task:

```jql
project = BAE AND issuetype = Workstream AND status != Done ORDER BY created DESC
```

Match the new task's subject matter against the returned workstream
summaries. If no match is obvious, create the task directly under BAE
without a parent and note the ambiguity in the wrap-up report.

### Directory Structure (this may have been updated)
```
~/Documents/BCBS/
  Ashley & Oliver Meetings/YYYY-MM-DD/
  Benefits/
  Graphics/
  Hiring/
  Metrics/
  Notes/
    Meetings/          <- general meetings only
    [evergreen files]  <- reference docs
  Onboarding/
  Photography/
  Projects/
    [Project Name]/    <- project-specific files
  Reference/
  Social/
    Posts/Sent/
    Profile Assets/
    Sprout/
  Templates/
  Temporary/
  To Transcribe/
```
