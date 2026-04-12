---
name: BCBS Meeting Notes
description: >
  Use when Oliver provides a SmartTranscribe transcript or recording from a
  BCBS VT meeting and wants it processed into structured notes. Triggers on:
  "process this meeting", "write up notes", "meeting notes for [file]",
  "turn this transcript into notes", "process the transcript", or when a
  .md file from SmartTranscribe is handed over. Also triggers after
  SmartTranscribe finishes if the user says "now process it" or "now do the
  notes". Always invoke this skill for any BCBS meeting transcript — do not
  just summarize ad hoc.
version: 1.2.0
---

# BCBS Meeting Notes

Processes a SmartTranscribe transcript into rich, structured meeting notes,
routes the files to the right BCBS folder, and creates Asana tasks from
action items.

## Input

The transcript is a `.md` file produced by SmartTranscribe. It may be:
- Provided directly by Oliver as a file path
- The most recently modified file in `~/Desktop/Transcriptions/`
- A file Oliver drops into `~/Documents/BCBS/To Transcribe/`

**Parsing SmartTranscribe output:** The file begins with a metadata block
containing fields like `Date:`, `Speakers:`, `Engines:`, and `## Summary`.
Extract date and participants from this block — do not rely on the filename
alone. Priority order for date extraction: (1) date in filename, (2) `Date:`
field in metadata block, (3) file modification timestamp as last resort.

**Speaker labels:** If the transcript uses generic labels (`Speaker A`,
`Speaker B`) rather than names, attempt to resolve them from context clues
(greetings, names mentioned, topics discussed, meeting title). Note any
unresolved speakers in the notes header with a `⚠️ Unresolved speaker` flag.

**Transcript filenames:** SmartTranscribe may save files with inconsistent
naming. Regardless of the original filename, rename the transcript to the
standard pattern during the move in Step 2.

---

## Step 1: Determine Routing

**Routing philosophy:** Be aggressive about routing to Projects and Ashley &
Oliver Meetings. `Notes/Meetings/` is the fallback of last resort — it should
only hold onboarding intros, multi-team events, and calls with genuinely no
project home. When in doubt, route to a project.

Check in this order:

### Ashley & Oliver 1:1

Route here **only** if Ashley and Oliver are the sole or primary participants
AND the meeting has no strong project identity of its own (quick syncs,
weekly check-ins, career discussions). If Ashley joins a multi-person project
meeting (e.g., Ashley + Oliver + Gina on Content Planning Tool), route to
the project folder instead — the project context takes precedence.

Route to:
```
~/Documents/BCBS/Ashley & Oliver Meetings/YYYY-MM-DD/
```
Create the dated folder if it does not exist. Use the recording date (not
today's date), formatted as `YYYY-MM-DD`.

Notes go in the **same folder** as the transcript.

### Project Meeting

Route to a project folder if the meeting's *subject matter* maps to an
existing project — even if the project name never appears in the transcript
title or summary. Read the transcript body to understand what was discussed.

Determine the project by:

1. **Read the transcript for topic signals** — what problem, initiative, or
   deliverable is being discussed? (e.g., a meeting about content intake
   workflows belongs in Content Planning Tool even if that phrase never
   appears.)
2. **Check the Projects folder** — list `~/Documents/BCBS/Projects/` and
   match by topic, not just by exact name.
3. **Search Asana** — first call `mcp__claude_ai_Asana__get_me` to confirm
   the workspace, then use `mcp__claude_ai_Asana__search_objects` to find
   matching projects by keyword.
4. **Err on the side of routing to a project.** If you can make a reasonable
   case that the meeting is about a known project's domain, route it there.

Route to:
```
~/Documents/BCBS/Projects/[Project Name]/
```

If no matching project folder exists yet, **create it** — do not fall back
to `Notes/Meetings`. Use a clear, descriptive Title Case name matching the project's
subject (e.g., "Q2 Content Calendar", "Beth Roberts Executive Social").

Notes go in the **same folder** as the transcript.

### General Meeting (default)

Only use this for: onboarding conversations, multi-team events, Senior
Games-style planning calls, or meetings that genuinely span multiple projects
with no single clear home.
```
~/Documents/BCBS/Notes/Meetings/
```

Notes go in the **same folder** as the transcript.

---

## Step 2: Move and Rename Files

**During the move, rename all files to the standard pattern:**
```
YYYY-MM-DD – [Meeting Name] – Transcript.md   ← the SmartTranscribe output
YYYY-MM-DD – [Meeting Name] – Notes.md        ← generated in Step 3
```
Use Title Case, spaces, and spaced en dashes (`–`). Do this in a single `mv`
command that combines the move and rename — not move-then-rename.

1. **Move and rename the transcript** to the destination folder using the
   standard filename pattern above.
2. **Audio deletion** — Show Oliver the audio file path (`.m4a`, `.mp3`, or
   other format alongside the transcript in `~/Desktop/Transcriptions/`) and
   ask for explicit confirmation before deleting. Do not auto-delete audio.
3. **Clean up** — if the source folder in `~/Desktop/Transcriptions/` or
   `~/Documents/BCBS/To Transcribe/` is empty after the move, delete it.

---

## Step 3: Generate Meeting Notes

Generate the notes file and save it alongside the transcript in the same
destination folder.

### 3a — Theme Extraction (Pass 1)

Read the full transcript. Identify and list all major topics discussed.
Do not write notes yet — just name the themes. This pass ensures you cover
the full transcript before writing.

### 3b — Theme Elaboration (Pass 2)

For each theme, extract detailed notes: specific names, numbers, decisions,
direct quotes, and the narrative thread of that section of the conversation.
Capture nuance — if someone qualified a decision or expressed frustration,
note it.

### 3c — Compile (Pass 3)

Assemble the full document from your per-theme notes using the format below.
Extract decisions, open questions, and action items into their own sections.

This three-pass approach produces 3–5× more useful output than a single
"summarize everything" prompt. Do not skip or collapse passes.

**Section count:** Target 5–12 topic sections for a typical meeting. If you
have more than 12, consolidate thin or closely related topics — a 3-sentence
section about rescheduling a call should be folded into the closest related
section or dropped if it adds no institutional value. Err toward depth in
fewer sections over breadth across many thin ones.

### Notes Format

```markdown
# YYYY-MM-DD – [Meeting Name] – Notes

*Attendee1, Attendee2*
*Source: [transcript filename]*

## Context

[2–4 sentences framing the meeting: what it was, why it happened, what made
it significant. Include who the attendees are, what project was being
discussed, and what the stakes were. Write this like the opening of a memo —
someone picking this up cold should understand the full situation immediately.
Do not just restate the SmartTranscribe summary.]

---

## [Topic 1 Name]

- **Key point:** Detail
- **Sub-point or decision:** Detail
  - Further context or direct quote if important

## [Topic 2 Name]

...

---

## Decisions

- **[Decision]:** [What was decided and the rationale or conditions behind it]

## Open Questions

- **[Question]:** [What remains unresolved and who is expected to resolve it]

---

## Action Items

### Oliver
- [ ] Task description *(→ Asana: [Project Name])*

### [Other Person]
- [ ] Task description

---

## Reference

**Omit this entire section if empty.**
- **Term or resource** — context note worth preserving for future reference
```

### Writing Guidelines

- **Topic sections**: Use the actual topics as headers ("Pride Month Planning",
  "Blog → Social Workflow"). Never use "Topics Discussed" or "Key Points".
- **Decisions ≠ action items**: Decisions are finalized choices. Action items
  are tasks. A decision often spawns action items but they are not the same.
- **Open questions**: Capture anything raised but unresolved — these are the
  most likely things to get lost.
- **Depth over brevity**: If a decision had conditions, capture them. If a
  quote matters, include it verbatim. These notes are institutional memory.
- **En dashes throughout**: Use `–` (en dash) in both filenames and H1
  headers, never `—` (em dash) or `-` (hyphen).
- **Action item completeness**: Capture both explicit commitments ("I'll send
  that over") and implicit ones ("I can look into that", "let me follow up on
  X"). If someone expressed intent to do something, it is an action item.
- **Asana tags on all action items**: Add `*(→ Asana: [Project Name])*` to
  every action item regardless of owner — not just Oliver's. This supports
  handoffs and accountability tracking even for tasks owned by others.
- **Routing context stays out of the notes file**: The notes file should read
  as a clean standalone document. Do not include routing decisions, metadata
  about where the file was moved, or skill execution notes inside it.

---

## Step 4: Create Asana Tasks

For each action item assigned to **Oliver**, create a task in Asana using
`mcp__claude_ai_Asana__create_task_confirm`.

If you haven't already called `mcp__claude_ai_Asana__get_me` in this session,
do so now to confirm the workspace GID before searching or creating.

Match action items to existing Asana projects using
`mcp__claude_ai_Asana__search_objects`. If no matching project exists, create
one that mirrors an existing BCBS project's structure:
- Call `mcp__claude_ai_Asana__get_project` on an existing project for team,
  color, and layout
- Create with `mcp__claude_ai_Asana__create_project_confirm`

For action items assigned to others (Cass, Ashley, etc.), list them in the
notes but do not create Asana tasks unless Oliver asks.

If the Asana MCP is unavailable or throws an auth error, skip task creation,
note it clearly in the Step 5 report, and continue.

---

## Step 5: Report Back

```
Notes:       ~/Documents/BCBS/[path]/YYYY-MM-DD – Meeting Name – Notes.md
Transcript:  ~/Documents/BCBS/[path]/YYYY-MM-DD – Meeting Name – Transcript.md  (moved)
Audio:       [path] — awaiting confirmation to delete / deleted
Asana:       N tasks created in [Project Name] / skipped (auth error)
```

Call out anything ambiguous (routing judgment calls, unresolved speakers,
Asana failures) so Oliver can review.

---

## Folder Reference

| Purpose | Path |
|---------|------|
| Ashley & Oliver 1:1s | `~/Documents/BCBS/Ashley & Oliver Meetings/YYYY-MM-DD/` |
| Project meetings | `~/Documents/BCBS/Projects/[Project Name]/` |
| General meetings | `~/Documents/BCBS/Notes/Meetings/` |
| Incoming transcripts | `~/Desktop/Transcriptions/` |
| To process queue | `~/Documents/BCBS/To Transcribe/` |
