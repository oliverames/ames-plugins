---
name: file-organization
description: Apply Oliver's file naming and organization conventions. Use this skill whenever you are about to create, rename, move, or organize files and folders — not just when the user explicitly asks. Also trigger for "rename files", "organize files", "reorganize a folder", "fix file names", "clean up file names", "batch rename", "naming conventions", "file naming rules", or when the user asks about folder structure. This skill applies to YOUR file operations too, not just user requests.
---

# File Organization Guidelines

## File Naming Rules

### Core Conventions

- **Title Case with spaces** (not underscores or hyphens between words)
- **Target under 60 characters** for Finder/Explorer readability
- **Filenames in English** even if document content is in another language
- **Consistent naming within folders** — all tax receipts follow the same pattern, all passports follow the same pattern

### Date Prefixes

- **YYYY-MM-DD prefix ONLY when date is critical** to the file's purpose or context
- Date based on **original creation/event date** (from file contents), NOT filesystem date
- If no date prefix, use word order: `[Subject/Project] [Document Type] [Descriptor]`
  - Example: "Fairbanks Summer Hours 2016"

### Special Characters

- **En dashes (–)** for year ranges in folder names (e.g., "EastRise 2019–2025")
- **Spaced en dashes** for separating distinct elements (e.g., "Oliver Ames – Media Release")
- Common acronyms acceptable if universally understood (e.g., "POS", "HR", "Q1")

### Versions

- Use: "v2", "Draft", "Final"
- **Never use:** "(2)", "(copy)", "Copy of", "New"

### Examples

✅ Good:
```
2024-03-15 Board Meeting Notes.md
Lawson's Finest Interview Prep.docx
EastRise 2019–2025 Archive
Oliver Ames – Media Release.pdf
Q1 Marketing Report Final.pdf
```

❌ Bad:
```
board_meeting_notes_03-15-24.md
lawsons-finest-interview-prep (2).docx
01 EastRise Archive
media release copy.pdf
Q1 Marketing Report (Final Version).pdf
```

## Folder Naming Rules

- **Do NOT start with numbers** (no "01 Archives", "02 Projects")
- **Exception:** YYYY-MM-DD prefixes are acceptable when chronology is the organizing principle
- Use clear, descriptive names that indicate contents

### Examples

✅ Good:
```
Archives
Projects
2024-01 Tax Documents
EastRise 2019–2025
```

❌ Bad:
```
01 Archives
02 Projects
Tax Docs
Old Stuff
```

## Organization Principles

### Structure

- **No loose files at root level** of main folders — group into appropriate subfolders
- If **multiple files of the same type exist**, they belong in a folder together
- **Match related files together** (e.g., voice memo recordings with their transcripts in dated subfolders)
- Only move files to category folders if **directly relevant**

### Photo Folders

- Large photo collections can be moved as parent folders without renaming individual files
- IMG_XXXX.jpeg files in personal photo folders don't need individual renaming
- Identify photo folders that should remain as-is

### Voice Memos/Recordings

- Keep original audio files alongside their transcripts
- Organize into dated subfolders with matched recording + transcript pairs

### Work Archives

- HR-related conversation records → "HR Documentation" folder
- Financial advisor correspondence → dedicated folders (e.g., "Trust Financial Advisement")
- Severance and separation documents → parent employment folder

## Duplicate Detection

- Find **EXACT duplicates only** using MD5 checksums
- Verify duplicates by **CONTENT, not just filename**
- Move suggested duplicates to a **review folder first**
- Report the full path of each duplicate pair
- Keep the file with the **better/clearer name**; delete the cryptic one
- Files marked "safe to delete" in filename can be removed after verification
- Redownloadable statements (credit cards, banks) can be deleted if duplicates exist

## The Process

When reorganizing files:

1. **Deep analysis first** — examine contents of every file
   - Use OCR/pdftotext for large PDFs that exceed API limits
   - Create temp smaller versions if needed, then delete temp files
2. **Create a reorganization plan** with proposed moves/renames
3. **Get approval** before execution
4. **Execute carefully**, verifying each operation
5. **Verify work** after changes
6. **Track progress** in case of context loss

## Quick Reference

| Element | Rule |
|---------|------|
| Spaces | Yes, use spaces |
| Underscores | No |
| Case | Title Case |
| Date prefix | Only when date matters |
| Date format | YYYY-MM-DD |
| Year ranges | En dash (2019–2025) |
| Versions | v2, Draft, Final |
| Folder numbers | Never (no "01", "02") |
| Max length | ~60 characters |
