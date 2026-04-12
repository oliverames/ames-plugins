# Apple Notes — Full Tool Reference

Use Apple Notes tools for all operations.

## Notes — CRUD

- `create-note` — Create with title, content (plaintext or html), optional tags
- `get-note-content` — Read note body (by id or title)
- `get-note-markdown` — Read note body as markdown
- `get-note-by-id` — Get note metadata by id
- `get-note-details` — Get note metadata by title
- `update-note` — Update content and/or rename (`newTitle`) a note (by id or title). **Warning:** Overwrites attachments — see Limitations in SKILL.md.
- `delete-note` — Delete a single note
- `batch-delete-notes` — Delete multiple notes by id array

## Notes — Organization

- `move-note` — Move a note to a different folder (by id or title)
- `batch-move-notes` — Move multiple notes by id array
- `search-notes` — Search by title or content, with folder/account/date filters
- `list-notes` — List notes with folder/account/date/limit filters
- `list-shared-notes` — List notes shared via iCloud collaboration

## Folders

- `create-folder` — Create a new folder
- `delete-folder` — Delete a folder
- `list-folders` — List all folders

## Attachments & Checklists

- `list-attachments` — List attachments on a note (by id or title)
- `get-checklist-state` — Get checkbox states from a note with checklists

## Accounts & Diagnostics

- `list-accounts` — List all note accounts (iCloud, On My Mac, etc.)
- `get-notes-stats` — Note counts and folder stats
- `get-sync-status` — iCloud sync status
- `health-check` — Verify the connector is working
- `export-notes-json` — Export all notes as JSON
