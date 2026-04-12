---
name: obsidian-notes
description: Use when creating or updating .md files that should match the user's preferred note formatting style — the same visual structure used in their Apple Notes (emoji titles, bold labels, structured sections) but as clean Obsidian-compatible markdown. Trigger when writing markdown notes, converting Apple Notes content to markdown, creating meeting notes, brainstorm notes, reference docs, or task trackers as .md files. Also use for "create a note", "write this up as markdown", "format as a note", "meeting notes template", "write up this brainstorm", or references to the BCBS Notes folder. Use this skill any time you're writing a .md note that isn't code documentation.
---

# Obsidian-Compatible Note Formatting

This skill defines the user's preferred markdown formatting for notes — mirroring the structure and visual style of their Apple Notes but using clean, Obsidian-compatible markdown with no HTML tags.

## Core Rules

- **No HTML.** Everything must be valid markdown. No `<div>`, `<br>`, `<b>`, `<ul>`, etc.
- **Emoji titles are standard.** Every note starts with an emoji that reflects its content.
- **Use blank lines for spacing.** Where Apple Notes uses `<div><br></div>`, use a single blank line.
- **Bold labels for key-value pairs.** Use `**Label:** value` for structured data.
- **No decorative separators.** Don't use `---` horizontal rules, dashes, or Unicode box-drawing characters between sections. Use headings and blank lines for structure instead.
- **Prefer bold labels over tables.** For relationship data or key-value pairs, use `**Name** — description` rather than markdown tables. Tables are OK for genuinely tabular data (budgets, schedules) but not for simple lists of people or settings.
- **Inline lists in prose.** For simple lists within a sentence, don't use bullet points — just write them inline: "Key skills include: Python, JavaScript, and SQL."

## Formatting Reference

| Apple Notes HTML | Obsidian Markdown |
|---|---|
| `<h1>Title</h1>` | `# Title` |
| `<h2>Section</h2>` | `## Section` |
| `<h3>Subsection</h3>` | `### Subsection` |
| `<b>text</b>` | `**text**` |
| `<i>text</i>` | `*text*` |
| `<ul><li>item</li></ul>` | `- item` |
| `<ol><li>item</li></ol>` | `1. item` |
| `<tt>code</tt>` | `` `code` `` |
| `<a href="url">text</a>` | `[text](url)` |
| `<div><br></div>` | blank line |
| `<s>text</s>` | `~~text~~` |

## Preferred Structure

### Title Format

Every note starts with an emoji + h1 title:

```markdown
# 📋 Note Title Here
```

Choose an emoji that reflects the note's content:
- 📋 plans, trackers, lists
- 📅 meetings, events, check-ins
- ⚠️ issues, warnings, incidents
- 🎯 audits, goals, strategy
- 💳 expenses, purchasing, finance
- 👥 people, contacts
- 🗒 reference, context, background
- 🔧 tools, setup, technical
- 📱 apps, platforms
- 🗂️ organization, planning
- 💡 ideas

### Subtitle / Date Line

Immediately after the title, add an italic line with context (participants, date, source):

```markdown
# 📅 2026-03-20 — Meeting Title

*Oliver, Ashley, Cass, Kathy (Community Events/Wellness)*
```

For notes with a last-updated date or status:

```markdown
# 📋 Task Tracker

*Last updated: March 20, 2026*
```

### Sections and Subsections

Use `##` for major sections, `###` for subsections within them:

```markdown
## Action Items

### Immediate (This Week)

- [ ] First task
- [ ] Second task

### Near-Term (Next 1-2 Weeks)

- [ ] Another task
```

### Bold Labels for Key-Value Data

For structured reference data (contacts, tools, settings), use bold labels:

```markdown
**Title:** Social Media Strategist
**Reports to:** Ashley Legacy
**Start date:** March 11, 2026
```

For people/contact entries with descriptions:

```markdown
**Ashley Legacy** — Manager, Digital Communications & Engagement. Values autonomy and collaboration. Weekly 1-on-1s (Wednesdays preferred).

**Cass Lang** — Digital Communications Strategist. Background in marketing, PR, and graphic design. Currently in burnout recovery — be mindful of transition pace.
```

### Task Lists

Use GitHub-flavored markdown checkboxes:

```markdown
- [ ] Open task
- [x] Completed task — DONE: details about completion
```

For completed tasks, use a checked checkbox (`[x]`) and add resolution details after an em dash. Do not use strikethrough on completed tasks — the checkbox is sufficient.

### Spacing Rules

- **After a heading to content:** One blank line (standard markdown)
- **Between list items that have descriptions:** No blank line needed within the list
- **After a list:** One blank line before the next section
- **Between people entries or reference blocks:** One blank line
- **Between sections:** One blank line

### Links

Provide context for links — never use generic text:

```markdown
[YouTube: "Learning to Fly" — FlightChops (126K views)](https://youtube.com/...)
```

### Special Characters

Use `&` directly in markdown (no HTML entities needed). Use `→` for arrows/flows:

```markdown
Facebook bill → Jerry Couture (billing) → Bonnie (accounting) → receipt from me
```

## Note Type Patterns

### Meeting Note

```markdown
# 📅 2026-03-20 — Meeting Title

*Participants: Oliver, Ashley, Cass*

## Context

Brief background on what this meeting was about.

## Action Items

- [ ] **Task name** — details and context
- [ ] **Another task** — more details

## Learnings

- Key insight from the meeting
- Another important takeaway

## People

**Name** — Role; relevant context from the meeting
```

### Reference Note

```markdown
# 🗒 Reference Title

*Description of what this note contains. Updated as needed.*
*Last updated: March 20, 2026*

## Section

**Key:** Value
**Another key:** Value

## Another Section

- Bullet point with context
- Another point
```

### Task Tracker

```markdown
# 📋 Task Tracker

*Last updated: March 20, 2026*

## 🔥 Immediate — Week of March 24

- [ ] **Task name** — details
- [ ] **Another task** — details
- [x] Completed task — DONE: resolution details

## Upcoming

- [ ] **Future task** — details

## Events Calendar

- **March 30** — Event name
- **April 10** — Another event
```

### Idea / Concept Note

```markdown
# 🎯 Concept Title

The core idea or observation — what it is and why it matters.
```

### Strategy / Planning Note

```markdown
# 📋 Campaign or Project Name

## Research To Do

**1. Talk to Danielle**
- What do they need most on the battery assembly line?
- What's their biggest limiting factor?

## The Strategy

Interview successful graduates about why they chose BETA...
```

### Brainstorm Capture Note

When reformatting someone's voice notes or stream-of-consciousness:

- **Preserve original language and voice** — don't paraphrase away distinctive phrasing or tone
- **Keep the nuance and detail** — structure for clarity, but don't compress into generic bullet points
- **Preserve specific names, questions, and action items** exactly as stated
- **Keep emotional/tonal content** — if they said something emphatically, keep that emphasis

The goal is organization, not compression. A well-structured long note is better than an over-summarized short one that loses the original thinking.

Example — preserve this kind of voice:
```markdown
What if we could model the look of SpaceX — but not made by a dick — made by working class Americans.
```

Don't flatten it to: "Consider SpaceX aesthetic for blue-collar positioning."

### Quick Note

```markdown
# 💡 Short Idea or Observation

Brief content — one or two lines explaining the idea or thing to remember.
```
