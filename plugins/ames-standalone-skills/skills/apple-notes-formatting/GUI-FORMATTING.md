# Apple Notes GUI Formatting (Computer Use Supplement)

This skill supplements the main Apple Notes API formatting skill. Use it when you need to apply formatting that the Apple Notes API connector **cannot** create programmatically. These formats require controlling the Notes app GUI via computer use.

## When to Use This Skill

Use GUI formatting when the user needs any of the following in an Apple Note:

- **Checklists** (interactive checkboxes)
- **Block quotes** (yellow sidebar)
- **Collapsible headings** (API-created headings render visually but don't collapse)
- **Dashed lists** (en-dash markers, distinct from bulleted lists)
- **Text highlighting** (colored background)
- **Duplicate title cleanup** (API connector sometimes creates a small body-text title above the real h1 title)

## Prerequisites

Before using any GUI formatting:

1. **Request computer use access** to the Notes app
2. **Create or update the note** via the Apple Notes API connector first (for all content the API can handle)
3. **Open the note** in Notes app via `open_application("Notes")` and navigate to the note
4. **Clean up duplicate title**: If the note has a small body-text title line above the actual h1 title, delete the small one so the note starts with the big title. Select the small title line and press Delete.
5. **Place your cursor** before applying any format — click on the target line or select the target text

## Text Selection Rules

**CRITICAL — these rules prevent formatting from cascading to unintended lines:**

- **Single line**: Click anywhere on the line. For paragraph-level formats (checklist, block quote, dashed list), the cursor just needs to be on the line — no selection needed.
- **Multiple specific lines**: Click at the start of the first line, then **shift-click** at the end of the last line. Do NOT use shift+down arrow for multi-line selection — it can over-select.
- **One line at a time for checklists**: Apply format to each line individually (click line, ⇧⌘L, click next line, ⇧⌘L). Multi-line checklist application can cascade to all lines below. Dashed lists (⇧⌘8) and block quotes (Aa menu) are safe for multi-line selection.
- **Never press Return after applying a list format** to the last item — it creates a stray blank list item.

## Format Reference

### Block Quote (GUI Only — No API Support)

**Visual**: Yellow/orange vertical sidebar on the left edge of the text.

**How to apply via Aa menu (RECOMMENDED)**:
1. Click on the target line (or select multiple lines via click + shift-click)
2. Click the **Aa** button in the Notes toolbar (formatting bar above the note content, center-left)
3. In the Aa panel: paragraph styles at top (Title, Heading, Subheading, Body, Monostyled), list styles below (Bulleted, Dashed, Numbered), and **Block Quote** at the bottom. Click Block Quote.

**Keyboard shortcut**: ⌘' (Command + apostrophe) — listed in Format menu but **do NOT use via computer use** — it inserts an emoji instead. Always use the Aa menu.

**To remove**: Click on the block-quoted line, open Aa menu, click "Body" to revert.

### Checklist (GUI Only — No API Support)

**Visual**: Interactive circular checkboxes. Unchecked = empty circle. Checked = yellow/orange filled circle with checkmark.

**How to apply**:
1. Click on a single line
2. Press **⇧⌘L** (Shift+Command+L)
3. Repeat for each line that should be a checklist item

**To check/uncheck an item**: Click the circular checkbox, or use **⇧⌘U** (Shift+Command+U) with cursor on the line.

**Important behaviors**:
- Checked items automatically reorder to the bottom of the checklist group
- Apply one line at a time to avoid cascading to subsequent lines
- Do NOT press Return after applying to the last item

### Dashed List (GUI Only — No API Support)

**Visual**: En-dash (–) markers instead of bullet dots. Distinct from bulleted lists (•).

**How to apply**:
1. Select the target lines (click start, shift-click end)
2. Press **⇧⌘8** (Shift+Command+8)

**Or via Aa menu**: Click Aa, then click "Dashed List" in the panel.

**Important**: Do not press Return after applying to the last item — it creates a blank dashed line.

**To remove**: Select the dashed lines and press ⇧⌘B (Body) to revert. Multi-line selection is safe for removal.

### Text Highlight (GUI Only for Background Color)

**Visual**: Colored background behind text. Available colors: purple, pink, orange, turquoise, blue.

**How to apply via keyboard shortcut (RECOMMENDED)**:
1. Select the text to highlight (click start, shift-click end)
2. Press **⇧⌘E** (Shift+Command+E)

**How to apply via Aa menu (alternative)**:
1. Select the text to highlight (click start, shift-click end)
2. Click the **Aa** button in the Notes toolbar
3. In the top icon row (B I U S | pencil | dot), click the **pencil icon** (highlight tool)

**To change highlight color**: Click the **colored dot** next to the pencil icon and choose from 5 colors.

**To remove highlight**: Select the highlighted text, click Aa, click the pencil icon again (toggles off).

**Note**: The API connector supports `<span style="color: red;">` for text color, but NOT background highlighting. Highlight is a distinct feature that applies a colored background band.

### Collapsible Headings (API Creates Visual Style, GUI Enables Collapse)

**The problem**: API-created headings (h1/h2/h3) render with correct visual styling (Title/Heading/Subheading) but lack the internal metadata that enables the collapse arrow. Users cannot collapse sections under API-created headings.

**The fix**: Re-apply the heading style via GUI. This converts it to a true native heading with collapse support.

**How to fix via keyboard shortcuts (CONFIRMED WORKING)**:
1. Click on the API-created heading text (or click start, shift-click end to select it)
2. Press **⇧⌘B** (Shift+Command+B) to toggle to Body
3. Immediately press the heading shortcut to re-apply:
   - **⇧⌘T** for Title (h1)
   - **⇧⌘H** for Heading (h2)
   - **⇧⌘J** for Subheading (h3)

**How to fix via Aa menu**:
1. Click on the heading text
2. Click the **Aa** button in the toolbar
3. Click the appropriate style (Title, Heading, or Subheading)

**Verification**: Hover over the heading text — a collapse chevron (˅) should appear on its left edge. Click it to collapse; click the right chevron (›) to expand.

**Collapse hierarchy**:
- Collapsing a **Title** hides everything until the next Title
- Collapsing a **Heading** hides everything until the next Title or Heading
- Collapsing a **Subheading** hides everything until the next Title, Heading, or Subheading

**Collapse/expand shortcuts**:
- Collapse section: ⌥⌘← (Option+Command+Left Arrow)
- Expand section: ⌥⌘→ (Option+Command+Right Arrow)
- Collapse all: ⌥⇧⌘←
- Expand all: ⌥⇧⌘→

### Duplicate Title Cleanup

**The problem**: The `create-note` title parameter renders as small body text at the top, duplicating the `<h1>` in the content.

**Preferred fix (API)**: Use the post-edit trick from SKILL.md — `update-note` with `newTitle: " "` and the same content. This strips the metadata line without GUI.

**GUI fix** (if the note already exists with the duplicate):
1. Triple-click the small duplicate title line to select it
2. Press Delete to remove it
3. The note should now start with the large h1 title

## API Connector vs GUI: Complete Comparison

| Feature | API Connector | GUI Required | Notes |
|---------|:---:|:---:|-------|
| Title (h1) | ✅ | Fix collapse | Re-apply via GUI for collapse arrow |
| Heading (h2) | ✅ | Fix collapse | Re-apply via GUI for collapse arrow |
| Subheading (h3) | ✅ | Fix collapse | Re-apply via GUI for collapse arrow |
| Body text | ✅ | — | |
| Bold | ✅ | — | `<b>` tag |
| Italic | ✅ | — | `<i>` tag |
| Underline | ✅ | — | `<u>` tag |
| Strikethrough | ✅ | — | `<s>` tag |
| Monostyled | ✅ | — | `<tt>` tag |
| Bulleted list | ✅ | — | `<ul><li>` tags |
| Numbered list | ✅ | — | `<ol><li>` tags |
| Nested lists | ✅ | — | Nested `<ul>` tags |
| Links | ✅ | — | `<a href>` tag |
| Tables | ✅ | — | `<table>` HTML |
| Text color | ✅ | — | `<span style="color:">` |
| Font size | ✅ | — | `<span style="font-size:">` |
| **Checklist** | ❌ | ✅ | ⇧⌘L per line |
| **Block quote** | ❌ | ✅ | Aa menu → Block Quote |
| **Dashed list** | ❌ | ✅ | ⇧⌘8 |
| **Highlight** | ❌ | ✅ | ⇧⌘E |
| **Collapsible headings** | ❌ | ✅ | Re-apply style via ⇧⌘B then ⇧⌘H/J/T |
| Drawings/scans | ❌ | ❌ | Cannot be created via GUI automation |
| Attachments | ❌ | ❌ | Cannot be added via API; manual only |

## Recommended Workflow

For notes that need GUI-only formatting:

1. **Create the note** via API with all content the connector supports (headings, bold, italic, lists, links, tables, etc.)
2. **Open Notes** via computer use and navigate to the note
3. **Clean up duplicate title** if present — delete the small body-text title line
4. **Fix collapsible headings** — select each heading, ⇧⌘B then re-apply (⇧⌘T/H/J)
5. **Apply block quotes** — click line, Aa menu → Block Quote
6. **Apply checklists** — click each line, ⇧⌘L
7. **Apply dashed lists** — select lines, ⇧⌘8
8. **Apply highlights** — select text, ⇧⌘E or Aa menu → pencil icon
9. **Verify** — scroll through the note and visually confirm each format

## Keyboard Shortcuts Quick Reference

Full Apple Notes keyboard shortcuts: `references/shortcuts.md`

| Format | Shortcut | Reliable via Computer Use? |
|--------|----------|:---:|
| Title | ⇧⌘T | ✅ |
| Heading | ⇧⌘H | ✅ |
| Subheading | ⇧⌘J | ✅ |
| Body | ⇧⌘B | ✅ |
| Monostyled | ⇧⌘M | ✅ |
| Bulleted List | ⇧⌘7 | ✅ |
| Dashed List | ⇧⌘8 | ✅ |
| Numbered List | ⇧⌘9 | ✅ |
| Block Quote | ⌘' | ❌ Use Aa menu |
| Checklist | ⇧⌘L | ✅ |
| Mark as Checked | ⇧⌘U | ✅ |
| Highlight | ⇧⌘E | ✅ |
| Bold | ⌘B | ✅ |
| Italic | ⌘I | ✅ |
| Underline | ⌘U | ✅ |
| Strikethrough | (none listed) | Use Aa menu → S icon |
| Indent | ⌘] | ✅ |
| Outdent | ⌘[ | ✅ |
| Soft return (new line in same list item) | ⇧Return | ✅ |
| Move list item up | ⌃⌘↑ | ✅ |
| Move list item down | ⌃⌘↓ | ✅ |
| Insert table | ⌥⌘T | ✅ |
| Collapse section | ⌥⌘← | ✅ |
| Expand section | ⌥⌘→ | ✅ |
| Collapse all | ⌥⇧⌘← | ✅ |
| Expand all | ⌥⇧⌘→ | ✅ |
