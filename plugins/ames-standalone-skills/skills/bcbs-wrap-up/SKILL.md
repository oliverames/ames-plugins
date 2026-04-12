---
name: bcbs-wrap-up
version: 1.0.0
description: >
  BCBS session wrap-up that updates evergreen notes, verifies meeting tasks
  are in Asana with strikethrough in the notes files when a task IS in Asana, audits naming conventions, and ensures directory organization is clean. Use when Oliver says "BCBS wrap up",
  "wrap up BCBS", "close out BCBS", "BCBS session done", "done with BCBS",
  "BCBS end of day", or invokes /bcbs-wrap-up. Run at the end of any BCBS
  working session.
---

# BCBS Session Wrap-Up

End-of-session checklist for the BCBS project directory at
`~/Documents/BCBS`. Ensures all notes, files, Asana tasks, and naming
conventions are current and consistent.

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
- `BCBS VT – Task Tracker.md` -- dates, deadlines, project status
- `Key People & Contacts.md` -- names, titles, roles, departments
- `Working Context & Background.md` -- org dynamics, strategy, priorities
- `BCBS Social Media Handoff – Reference Notes.md` -- social strategy, tools
- `Social Media Audit.md` -- platform status, tool access, blockers
- `Sprout Social – Audience Groups to Create.md` -- audience targeting
- `Expenses, Reimbursements & Purchasing.md` -- financial processes
- `Data Organization Planning.md` -- file organization decisions

For each file:
1. Read the current content
2. Cross-reference with any transcripts or notes created/modified this session
3. If new information exists (people, dates, decisions, status changes), add
   it in the appropriate section matching the file's existing style
4. Do NOT rewrite sections; append or update specific entries

---

## Phase 3: Asana Task Verification

For every meeting note file modified this session:

1. Read the Action Items section
2. For each action item that has an Asana routing tag and has been put in Asana`*(-> Asana: [Project])*`:
   - Verify the item text is struck through: `~~item text~~`
   - If not struck through, add strikethrough
3. For action items that do NOT have Asana routing:
   - Determine if they should be in Asana (non-trivial, owned by Oliver)
   - If yes, first call `mcp__claude_ai_Asana__get_me` to confirm the
     workspace, then create the task with `mcp__claude_ai_Asana__create_task_preview`
     followed by `mcp__claude_ai_Asana__create_task_confirm`. After creation,
     use `mcp__claude_ai_Asana__update_tasks` with `add_projects` to ensure
     the task is properly assigned to the project (create_task_confirm can
     orphan tasks). Add the routing tag + strikethrough to the note.
   - Route to the correct Asana project based on content:
     - Event/content tasks -> Q2 Content Calendar (2026)
     - Strategy/brand tasks -> Content & Brand Strategy
     - Relationship/onboarding tasks -> Relationship Building & Onboarding
     - Tool evaluation tasks -> Content Calendar Tool Evaluation
     - Platform/IT tasks -> Platform & Account Setup

**Convention:** A strikethrough on an action item means it is tracked in
Asana. This is the single source of truth for whether a task has been
captured.

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

## Phase 6: Asana Project Sync

Quick check that the local `Projects/` folder and Asana are in sync:

1. List `~/Documents/BCBS/Projects/` subdirectories
2. Call `mcp__claude_ai_Asana__get_me` to confirm workspace, then
   `mcp__claude_ai_Asana__get_projects` to list Asana projects
3. Flag any new local folders without Asana projects (and vice versa)
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
   - Asana sync status

---

## Reference

### Naming Convention
- Date prefix: `YYYY-MM-DD`
- Separator: space-en-dash-space (` – ` with U+2013)
- Title Case for descriptions
- Suffixes: `– Transcript`, `– Notes` for meeting files

### Asana Projects (as of 2026-04)
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
