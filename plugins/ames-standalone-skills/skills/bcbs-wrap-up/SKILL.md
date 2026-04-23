---
name: bcbs-wrap-up
version: 1.2.0
description: >
  BCBS session wrap-up that updates evergreen notes, verifies action items
  are tracked in Jira (the canonical task system for BCBS), migrates any
  legacy Asana or Apple Reminders references into Jira, audits naming
  conventions, and ensures directory organization is clean. Use when Oliver
  says "BCBS wrap up", "wrap up BCBS", "close out BCBS", "BCBS session
  done", "done with BCBS", "BCBS end of day", or invokes /bcbs-wrap-up. Run
  at the end of any BCBS working session.
---

# BCBS Session Wrap-Up

End-of-session checklist for the BCBS project directory at
`~/Documents/BCBS`. Ensures all notes, files, Jira tasks, and naming
conventions are current and consistent.

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

Run phases in order. Auto-apply all actions without asking unless a step
says otherwise. Use subagents for parallel work where noted.

**Relationship to general wrap-up:** This skill handles BCBS-specific
cleanup. After completing all phases, invoke the general `/wrap-up` skill
for commits, memory persistence, worklog, and backups.

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

**Evergreen files to check:**
- `Key People & Contacts.md` -- names, titles, roles, departments
- `Working Context & Background.md` -- org dynamics, strategy, priorities
- `BCBS Social Media Handoff – Reference Notes.md` -- social strategy, tools
- `Social Media Audit.md` -- platform status, tool access, blockers
- `Sprout Social – Audience Groups to Create.md` -- audience targeting
- `Expenses, Reimbursements & Purchasing.md` -- financial processes
- `Data Organization Planning.md` -- file organization decisions

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
  without a `(→ Jira: ...)` tag after wrap-up are not considered
  captured.
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
Not in `Notes/Meetings/` unless the meeting is genuinely general-purpose
(onboarding intro, multi-team event, no single project home).

### Social Folder
General Social folder files stay in Social. If posts or strategies are project specific, they should be moved to Projects. 

---

## Phase 5: Naming Convention Audit

All `.md`, `.txt`, and `.docx` files with date prefixes must follow:
```
YYYY-MM-DD – [Description] – [Type].ext
```
Where `–` is an en-dash (U+2013), not a hyphen (-) or em-dash (U+2014).

Run this check:
```bash
find ~/Documents/BCBS -not -path '*/.a5c/*' -not -path '*/.codex-tasks/*' \
  -not -path '*/.remember/*' \( -name '*.md' -o -name '*.txt' -o -name '*.docx' \) \
  -type f | while read f; do
    b=$(basename "$f")
    if echo "$b" | grep -q $'\u2014'; then echo "EM-DASH: $f"; fi
    if echo "$b" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [^–]'; then echo "MISSING EN-DASH: $f"; fi
  done
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

## Phase 7: Verification

Run a final verification:

1. Confirm all files modified this session exist at their expected paths
2. Spot-check 2-3 evergreen files for the updates made in Phase 2
3. Spot-check 2-3 meeting notes for correct strikethrough in Phase 3
4. Report a summary:
   - Files touched this session
   - Evergreen files updated
   - Action items struck through
   - Naming violations fixed
   - Jira sync status

---

## Reference

### Naming Convention
- Date prefix: `YYYY-MM-DD`
- Separator: space-en-dash-space (` – ` with U+2013)
- Title Case for descriptions
- Suffixes: `– Transcript`, `– Notes` for meeting files

### Jira Project Search Seeds (as of 2026-04)
- Platform & Account Setup
- Content Calendar Tool Evaluation
- Content & Brand Strategy
- Q2 Content Calendar (2026)
- Strategic Initiatives (Q3-Q4 2026)
- Relationship Building & Onboarding
- Reporting
- BeWell at Work
- Beth Roberts Executive Social
- Beth Roberts CEO Brand Building / Q3 / Q4 / (2026)

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
