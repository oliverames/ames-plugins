---
name: apple-notes-formatting
description: This skill should be used when the user asks to "create an Apple
  Note", "format for Apple Notes", "write to Apple Notes", "save this to Notes",
  "add to my notes", "make a note", "update my note", "edit that note", "search
  my notes", "find a note about", "read that note", or needs to create, read,
  update, search, or format notes via the Apple Notes MCP tools. Also use when
  the user asks to "add a checklist", "make it collapsible", "add block quotes",
  "highlight text in Notes", "add a dashed list", or any GUI-only Apple Notes
  formatting. Provides HTML structure, formatting rules, spacing guidelines, and
  known limitations for the Apple Notes API.
---

# Apple Notes Formatting

## Tools

Use Apple Notes tools (`create-note`, `update-note`, `get-note-content`, `search-notes`, `move-note`, `delete-note`) for all Apple Notes operations. Full tool reference (23 tools): `references/tools.md`.

### Tool Tips

- **Always prefer `id` over `title`** when both are available — IDs are unique, titles can collide.
- **Use `format: "html"`** on create and update for rich formatting (see below).
- **`searchContent: true`** on `search-notes` searches body text, not just titles.
- **`modifiedSince`** on `search-notes` and `list-notes` filters by ISO 8601 date — useful for large collections.
- **`create-note` has no folder parameter** — notes are created in the default location. To place in a specific folder, create first then call `move-note`.

## Critical Rules

**Plain text with newlines does NOT work.** Apple Notes collapses all line breaks.

**Use HTML tags for structure.** Apple Notes renders HTML properly.

**Do NOT use CDATA sections.** Wrapping content in `<![CDATA[...]]>` causes `]]>` to render literally.

**No decorative separators.** Don't use horizontal lines, dashes, or Unicode box-drawing characters (―――) between sections. Use spacing and headers instead.

## Preferred Structure

Use `<div>` tags for body text. Use `<div><br></div>` for spacing between elements.

### Native Heading Tags

Heading tags work both bare and wrapped in `<div>`. Prefer bare tags — they're cleaner and render identically:

```html
<h1>Title Text</h1>
<h2>Heading Text</h2>
<h3>Subheading Text</h3>
```

`<div><h2>...</h2></div>` also works but is unnecessary nesting.

| Tag | Apple Notes Style | Visual Appearance |
|-----|-------------------|-------------------|
| `<h1>` | Title | Large bold text |
| `<h2>` | Heading | Medium bold text |
| `<h3>` | Subheading | Smaller bold text |

**Important:** API-created headings render correctly but are NOT collapsible. See Known Limitations.

### Title Format

The `title` parameter sets the note's metadata name (shown in the sidebar list) AND renders as small body text at the top of the note. To get a clean big heading without a duplicate small line, use the **post-edit trick**:

1. `create-note` with `title` set to your desired name + `<h1>` in content
2. Immediately `update-note` with `newTitle: " "` (single space) and the same content

This strips the metadata title line from the body while keeping the styled `<h1>`.

**Step 1** — `create-note` with `title: "🎯 Note Title Here"` and content starting with `<h1>🎯 Note Title Here</h1>`, format `html`

**Step 2** — `update-note` with the returned note `id`, `newTitle: " "`, and the same `newContent`, format `html`

Choose an emoji that reflects the note's content (🔧 for tools, 📋 for plans, 🎬 for video/content, 💬 for communication, ✈️ for aviation, etc.)

**Note:** The list view will show the `<h1>` text as the title (Apple Notes uses the first line of the body when the metadata name is blank/space). So the sidebar stays correct.

### Section Headers

Use h2 for major sections and h3 for subsections:

```html
<h2>Section Name</h2>
<h3>Subsection Name</h3>
```

### Spacing Rules

- **Header to Content:** No line break needed (flow naturally).
- **Header to List:** No line break needed.
- **Header to Bold Text:** **Add** `<div><br></div>` if the line following the header is completely bolded.
- **After List:** Always add `<div><br></div>` (lists don't create trailing space).
- **Between Sections:** Use `<div><br></div>`.

✅ **Header -> List (No break):**
```html
<h2>My List</h2>
<ul>
<li>Item 1</li>
<li>Item 2</li>
</ul>
```

✅ **Header -> Text (No break):**
```html
<h2>My Section</h2>
<div>This is the content.</div>
```

✅ **Header -> Bold (Add break):**
```html
<h2>My Section</h2>
<div><br></div>
<div><b>Critical Warning</b></div>
```

## Supported HTML Tags

| Tag | Use |
|-----|-----|
| `<div>` | All content blocks |
| `<h1>` | Title style (bare, no div needed) |
| `<h2>` | Heading style (bare, no div needed) |
| `<h3>` | Subheading style (bare, no div needed) |
| `<b>` | Bold text |
| `<i>` | Italic text |
| `<u>` | Underline |
| `<s>` | Strikethrough |
| `<tt>` | Monostyled text (gray background, monospace) |
| `<table>` | Tables (functional but render with limited styling) |
| `<span style="...">` | Inline styling (font-size, font-family, color) |
| `<a href="url">` | Links |
| `<br>` | Line break (use inside `<div>` for spacing) |
| `<ul>` | Unordered (bullet) list container |
| `<ol>` | Ordered (numbered) list container |
| `<li>` | List item (use inside `<ul>` or `<ol>`) |

## Special Characters

Use HTML entities for special characters in note content:
- Ampersand: `&amp;` (required — raw `&` can break rendering)
- Less than: `&lt;`
- Greater than: `&gt;`

Plain text arrows (→ or ->) work fine and don't need entities.

## Technical Content

For terminal commands, codes, API keys, or any technical strings, use the native monostyled tag:

```html
<div><tt>your command here</tt></div>
```

For inline code within a sentence:

```html
<div>Run: <tt>sudo sfltool resetbtm</tt></div>
```

This renders with a gray background, matching Apple Notes' native Monostyled format.

## Links

**Always provide context for links.** Never use generic text like "YouTube Short" or "Reference Link."

✅ Good:
```html
<div><a href="https://youtube.com/...">YouTube: "Learning to Fly Alia: No Feet?!" — FlightChops (126K views)</a></div>
```

❌ Bad:
```html
<div><a href="https://youtube.com/...">YouTube Short</a></div>
```

If you have a URL, look up the actual content and describe what it is.

## Lists

### Native Bullet Lists

Use `<ul><li>` tags for native Apple Notes bullets. **Critical: Always add `<div><br></div>` AFTER the closing `</ul>` tag** — lists don't create trailing space automatically.

```html
<div><b>Shopping List</b></div>
<ul>
<li>Milk</li>
<li>Eggs</li>
<li>Bread</li>
</ul>
<div><br></div>
<div>Next section starts here...</div>
```

### Native Numbered Lists

Use `<ol><li>` tags for native numbered lists. Same spacing rule applies — add `<div><br></div>` after `</ol>`.

```html
<div><b>Steps to Complete</b></div>
<ol>
<li>First step</li>
<li>Second step</li>
<li>Third step</li>
</ol>
<div><br></div>
<div>Next section starts here...</div>
```

### Inline Formatting in Lists

You can use `<b>`, `<i>`, and other inline tags inside `<li>`:

```html
<ul>
<li><b>Important item:</b> Description here</li>
<li><i>Optional item:</i> Another description</li>
</ul>
<div><br></div>
```

### When NOT to Use Native Lists

For simple inline lists within prose, plain text is cleaner:

```html
<div>Key skills include: Python, JavaScript, and SQL.</div>
```

## Tables

Apple Notes supports HTML tables, but they render clunky. For simple relationship data or connection maps, plain text is cleaner:

✅ Prefer for relationships/connections:
```html
<div><b>Amanda Seeholzer</b> → Ryan Seeholzer</div>
<div><b>Emily Stockwell</b> → Danielle Price</div>
```

❌ Avoid complex tables when simple lists suffice.

## Note Type Patterns

### Simple Reference Note

All examples use the post-edit trick: `create-note` with title + h1, then `update-note` with `newTitle: " "`.

```
title: "🔧 Content Inspiration: Stuff Made Here"
```
```html
<h1>🔧 Content Inspiration: Stuff Made Here</h1>
<div><br></div>
<div>The guy who made the gun-powered baseball bat — that maker/engineer energy is a good angle for recruitment content.</div>
<div><br></div>
<div><a href="https://youtube.com/@StuffMadeHere">YouTube: Stuff Made Here — engineering/maker projects</a></div>
```

### Idea/Concept Note

```
title: "🎯 BETA Employee Vibe"
```
```html
<h1>🎯 BETA Employee Vibe</h1>
<div><br></div>
<div>The people at the job fair looked like my science teacher's radio club crowd. That's the maker/tinkerer persona to target in recruitment.</div>
```

### Note with Subtitle

```
title: "📋 Q1 Marketing Strategy"
```
```html
<h1>📋 Q1 Marketing Strategy</h1>
<div><i>Draft — last updated January 2026</i></div>
<div><br></div>
<div>Main body content begins here...</div>
```

### Strategy/Planning Note

```
title: "📋 Workforce Development Campaign"
```
```html
<h1>📋 Workforce Development Campaign</h1>
<div><br></div>
<h2>Research To Do</h2>
<div><b>1. Talk to Danielle</b></div>
<ul>
<li>What do they need most on the battery assembly line?</li>
<li>What's their biggest limiting factor?</li>
</ul>
<div><br></div>
<h2>The Strategy</h2>
<div>Interview successful graduates about why they chose BETA...</div>
```

### Brainstorm Capture Note

When reformatting someone's voice notes or stream-of-consciousness:

- **Preserve original language and voice** — don't paraphrase away distinctive phrasing or tone
- **Keep the nuance and detail** — structure for clarity, but don't compress into generic bullet points
- **Preserve specific names, questions, and action items** exactly as stated
- **Keep emotional/tonal content** — if they said something emphatically, keep that emphasis
- **Ask yourself: "Did we capture all the nuance?"** before finishing

The goal is organization, not compression. A well-structured long note is better than an over-summarized short one that loses the original thinking.

Example — preserve this kind of voice:
```html
<div>What if we could model the look of SpaceX — but not made by a dick — made by working class Americans.</div>
```

Don't flatten it to: "Consider SpaceX aesthetic for blue-collar positioning."

## GUI-Only Formatting (Computer Use Required)

Some Apple Notes formatting features cannot be created via the API. For these, use the companion skill file `GUI-FORMATTING.md` in this folder, which provides instructions for applying formats via computer use control of the Notes app.

**GUI-only features include:**
- Checklists (interactive checkboxes) — ⇧⌘L per line
- Block quotes (yellow sidebar) — Aa menu → Block Quote
- Dashed lists (en-dash markers) — ⇧⌘8
- Text highlighting (colored background) — ⇧⌘E
- Collapsible headings fix — re-apply heading style: ⇧⌘B then ⇧⌘T/H/J

**Important**: Always read `GUI-FORMATTING.md` before attempting GUI formatting. It contains critical rules about text selection and gotchas that prevent formatting from cascading to unintended lines.

**Duplicate title cleanup**: If a note has a duplicate small title above the h1, run `update-note` with `newTitle: " "` and the same content to strip the metadata line. Or delete the small line manually in Notes.

## Known Limitations

### Headings Are Not Collapsible

**API-created headings (h1/h2/h3) render with correct styling but lack native collapsible functionality.** This is an API limitation — the internal metadata that enables collapse arrows isn't set when creating notes programmatically.

**Workaround:** To make a heading collapsible, select the heading text in Notes, tap the Aa format button, and re-apply the Heading/Subheading style. This converts it to a true native heading with collapse support.

### Other Limitations

- **Checkboxes:** Cannot be created via the API — use native bullet lists instead (but `get-checklist-state` can read existing checklists)
- **Block quotes:** The yellow sidebar quote style cannot be created via API
- **Attachments:** Cannot be added via the API (images, audio, PDFs must be added manually in Notes)

### Title Handling

- **`create-note`:** The `title` parameter renders as small body text at the top AND sets the sidebar list name. Including `<h1>` in content creates a duplicate. Use the **post-edit trick** (see Title Format above) to strip the metadata line.
- **`update-note`:** Sets body content directly. Include `<h1>` in your content for the styled heading. Use `newTitle: " "` to clear the metadata title line.
- **List view:** When metadata title is a space, Apple Notes uses the first line of the body (the `<h1>` text) as the sidebar title automatically.

### Updating vs. Creating

- **Text-Only Notes:** **Prefer editing** the existing note ID to keep history clean.
- **Notes with Attachments:** **Create a NEW note.** Updating a note with attachments via API will **wipe the attachments**.

### Attachments (Images, Audio, PDFs)

Attachments cannot be added via the API, and notes with attachments require special handling.

**How to detect a note has an attachment:**
- Note body returns **empty** despite having a title in the list
- API returns **"stdout maxBuffer length exceeded"** error
- Tool result is **too large for context window**

**Critical: Do NOT update notes with attachments** — you will overwrite and lose the attachment.

Instead:
- Create a **new note** with the formatted text content
- Tell the user to manually delete the old one if desired
- Or tell the user to manually add the emoji to the existing note's title

### Truncated Titles

If a note title is very long (paragraph-length), the API list truncates it. The API cannot find notes by partial/truncated title.

Options:
- Ask the user for the full exact title
- Create a new note with a proper short title instead
- Tell the user to rename the note manually first

### Title Lookup Fails When Title Contains `&`

The `get-note-content`, `update-note`, and `delete-note` tools all fail with "Note not found" when the note's title contains an `&` character, even when passing the exact title string. This is a limitation in how the underlying AppleScript `note "name"` resolver handles the ampersand.

**Workaround:** First call `search-notes` with a query that omits the `&` (e.g., search for "Asana MCP" instead of "Asana MCP — Gotchas & Reliable Patterns"), extract the note's `id` from the result, then call the operation using the `id` parameter instead of `title`.

Example:
```
1. search-notes query="macOS Shell Config" → returns id x-coredata://.../p8756
2. update-note id="x-coredata://.../p8756" newContent="..." format="html"
```

### Internal Storage Format (Not What You Input)

Apple Notes transforms HTML on save. The output of `get-note-content` shows the **stored** format, which differs from what you submit. These transformations render correctly in the Notes app — they are NOT bugs:

| Input HTML | Stored / `get-note-content` output |
|-----------|-------------------------------------|
| `<h1>Title</h1>` | `<div><b><span style="font-size: 24px">Title</span></b></div>` |
| `<h2>Section</h2>` | `<div><b><span style="font-size: 18px">Section</span></b></div>` |
| `<tt>code</tt>` | `<font face="Courier"><tt>code</tt></font>` or `<font face="Courier"><span style="font-size: 12px">code</span></font>` |
| `<i><tt>path</tt></i>` | `<font face="Courier-Oblique">path</font>` (can't be reverted) |
| `&amp;` | `&amp` (no trailing `;` in output — but stored correctly) |

**Do NOT "fix" these in `update-note` calls** — you will be chasing ghosts. The skill's input conventions (`<h1>`, `<tt>`, `&amp;`) remain correct; Apple Notes normalizes them internally.

### Verifying Rendered Output

`get-note-content` returns stored HTML, which can look wrong even when rendering is correct (see above). For true verification of what the user sees, use AppleScript to fetch the note's `plaintext` property:

```bash
osascript -e 'tell application "Notes" to return plaintext of note "🧩 Lytho MCP Server"'
```

This returns the rendered text as shown in the Notes app — the reliable oracle for "does this actually render as expected." Use it whenever `get-note-content` output looks suspicious or after fixing broken entities/nested lists.

### `<a href>` Anchor Tags Stripped on Update

The `update-note` tool strips `<a href="url">text</a>` tags on save, keeping only the inner text. Real hyperlinks cannot be inserted via this tool.

**Workaround:** Submit the bare URL as plain text. Apple Notes auto-detects URLs on render and makes them clickable:

```html
<!-- Submit this -->
<div>Calendar sync: https://calendar.google.com/calendar/u/0/syncselect</div>

<!-- Apple Notes auto-links the URL on render -->
```

Do NOT use `<a href>` in `update-note` content — it will be silently dropped.

### Nested Lists Don't Work (`<ul>` inside `<ol>`)

Apple Notes does NOT render `<ul>` nested inside `<ol>` as a true nested list. Either:
- The nested `<ul>` renders as a sibling list (orphaning substeps from their parent numbered step)
- Or the structure collapses unpredictably

**Fix:** Inline sub-bullets into the parent `<li>` using `<br>` + bullet entity:

```html
<!-- Bad: orphans substeps -->
<ol>
  <li>Step 3: Enable SSH agent</li>
  <ul><li>Substep A</li><li>Substep B</li></ul>
  <li>Step 4: ...</li>
</ol>

<!-- Good: substeps stay inside parent step -->
<ol>
  <li>Step 3: Enable SSH agent<br>&#8226; Substep A<br>&#8226; Substep B</li>
  <li>Step 4: ...</li>
</ol>
```

Use `&#8226;` for the bullet character (safer than raw `•`).
