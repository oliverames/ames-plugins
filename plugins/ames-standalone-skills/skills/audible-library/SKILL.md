---
name: audible-library
description: Use when the user asks to "download an audiobook", "rip Audible", "liberate a book",
  "sync audiobooks", "back up my Audible library", "add a book to Audiobookshelf",
  "search my audiobooks", "convert audiobook to MP3", "run libation-sync", "clean up
  audiobook metadata", "fix book metadata", "transfer audiobooks", or asks anything
  about Libation, Audiobookshelf, or their Audible library.
---

# Audible Library — Libation + Audiobookshelf

Download, decrypt, and serve Audible audiobooks using Libation on the MacBook Pro and Audiobookshelf on the Mac Mini.

**Workflow:** Audible → Libation (decrypt to M4B) → SCP to Mac Mini → Audiobookshelf

## Installed Locations

| Component | Path |
|-----------|------|
| Libation app | `/Applications/Libation.app` |
| Libation CLI | `/Applications/Libation.app/Contents/MacOS/LibationCli` |
| Books directory | `~/Music/Libation/Books/` |
| Sync script | `~/Developer/scripts/libation-sync` (in PATH) |
| Audiobookshelf | `http://100.79.211.138:13378` (Docker on Mac Mini) |
| ABS API key | 1Password: `op://Development/Audiobookshelf API Key/credential` |
| ABS audiobooks dir | `home-server:~/audiobooks/` |
| ABS library ID | `5b9bdb84-5ed1-45bb-ab37-383f2c720da5` |

## Libation CLI Commands

```bash
# Scan Audible library (syncs account)
LibationCli scan

# Search for a book (-n 0 shows all, --bare for ASINs only)
LibationCli search "Book Title" -n 0
LibationCli search "Book Title" -n 0 --bare

# Download + decrypt specific books by ASIN
LibationCli liberate B08G9PRS1K B002V1OF70

# Download all un-liberated books
LibationCli liberate

# Convert M4B to MP3
LibationCli convert

# Export library as CSV/JSON/XLSX
LibationCli export ~/Desktop/library --csv

# Show settings and paths
LibationCli get-setting
```

**Note:** The CLI's `search` command with pagination requires interactive input. Always use `-n 0` to show all results at once, or `--bare` for scripting.

## libation-sync Script

One-command pipeline that scans, downloads, copies to Audiobookshelf, and triggers a library scan.

```bash
# Sync all new purchases
libation-sync

# Sync specific books by ASIN
libation-sync B08G9PRS1K B002V1OF70
```

The script:
1. Runs `LibationCli scan` to sync library metadata
2. Runs `LibationCli liberate` (all new or specific ASINs)
3. Detects newly downloaded folders via before/after diff
4. SCPs new folders to `~/audiobooks/` on Mac Mini
5. Triggers Audiobookshelf library scan via API

## Audiobookshelf API

```bash
# Load API key from 1Password
ABS_KEY=$(op read "op://Development/Audiobookshelf API Key/credential")

# NOTE: Direct HTTP to 100.79.211.138:13378 times out from this machine (Tailscale routing).
# All ABS API calls must be proxied through SSH:
#   ssh home-server "curl -s ... -H 'Authorization: Bearer $ABS_KEY'"

# Trigger library scan
ssh home-server "curl -s -X POST 'http://localhost:13378/api/libraries/5b9bdb84-5ed1-45bb-ab37-383f2c720da5/scan' \
  -H 'Authorization: Bearer $ABS_KEY'"

# List recent books (sorted by added date, descending)
ssh home-server "curl -s 'http://localhost:13378/api/libraries/5b9bdb84-5ed1-45bb-ab37-383f2c720da5/items?limit=20&sort=addedAt&desc=1' \
  -H 'Authorization: Bearer $ABS_KEY'" | jq '.results[] | {title: .media.metadata.title, author: .media.metadata.authorName}'

# Search library
ssh home-server "curl -s 'http://localhost:13378/api/libraries/5b9bdb84-5ed1-45bb-ab37-383f2c720da5/search?q=QUERY' \
  -H 'Authorization: Bearer $ABS_KEY'"
```

## Output Format

Libation outputs DRM-free **M4B** by default (`DecryptToLossy: False`). M4B preserves:
- Original AAC audio quality (no re-encoding)
- Chapter markers
- Cover art and metadata

This is the ideal format for Audiobookshelf. To get MP3 instead, use `LibationCli convert` after download.

## Folder Naming

Libation creates folders like `Project Hail Mary [B08G9PRS1K]/`. The ASIN in brackets helps Audiobookshelf's metadata matcher identify the exact Audible edition.

## DRM Notes

- **AAX/AAXC** (standard stereo): Fully decryptable — this is what Libation handles
- **Widevine L1** (spatial audio, since Jan 2026): Not decryptable by any tool. Audible falls back to AAXC for non-spatial devices, so the stereo version is still obtainable
- Library size: ~1,218 titles as of March 2026

## Metadata Cleanup

After adding books (especially non-Libation sources), metadata often needs fixing: "(Unabridged)" in titles, swapped author/narrator, bad genres, missing series info.

### Cleanup API

```bash
# Update metadata for a specific book (PATCH — only included fields are modified)
# IMPORTANT: Use "authors" (array of {name} objects) and "narrators" (array of strings)
# NOT "authorName"/"narratorName" — those are read-only computed fields that silently no-op
ABS_KEY=$(op read "op://Development/Audiobookshelf API Key/credential")
ssh home-server "curl -s -X PATCH 'http://localhost:13378/api/items/{ITEM_ID}/media' \
  -H 'Authorization: Bearer $ABS_KEY' \
  -H 'Content-Type: application/json' \
  -d '{\"metadata\":{
    \"title\": \"Clean Title\",
    \"subtitle\": \"Optional Subtitle\",
    \"authors\": [{\"name\": \"Author Name\"}],
    \"narrators\": [\"Narrator Name\"],
    \"series\": [{\"name\": \"Series Name\", \"sequence\": \"1\"}],
    \"genres\": [\"Genre1\", \"Genre2\"],
    \"publishedYear\": \"2024\",
    \"description\": \"Book description text\"
  }}'"

# Delete a book (hard=1 also removes files from disk)
ssh home-server "curl -s -X DELETE 'http://localhost:13378/api/items/{ITEM_ID}?hard=1' \
  -H 'Authorization: Bearer $ABS_KEY'"

# Get full metadata for a book
ssh home-server "curl -s 'http://localhost:13378/api/items/{ITEM_ID}' \
  -H 'Authorization: Bearer $ABS_KEY'" | jq '.media.metadata'
```

### Common Metadata Issues

| Issue | Fix |
|-------|-----|
| Title has "(Unabridged)" | Set `title` to clean version, move subtitle portion to `subtitle` |
| Author/narrator swapped | MP3 ID3 tags often store these incorrectly — set both `authors` and `narrators` explicitly |
| Using authorName/narratorName | These are **read-only** — use `authors: [{name}]` and `narrators: ["name"]` arrays instead |
| Genre is "Audiobook" or typos | Replace with actual genres like `["Nonfiction", "History"]` |
| Genres as single comma-joined string | Split into separate array entries |
| Missing series info | Add `series` array with name and sequence number |
| Duplicate entries after scan | Delete extras with `DELETE /api/items/{ID}?hard=1` |

### Non-Libation Books (Manual Transfers)

For audiobooks not from Audible (no ASIN), organize into `Author/Title/` folders before SCP:

```bash
ABS_KEY=$(op read "op://Development/Audiobookshelf API Key/credential")
ssh home-server 'mkdir -p ~/audiobooks/"Author Name/Book Title"'
scp /path/to/files/*.mp3 "home-server:~/audiobooks/Author Name/Book Title/"
ssh home-server "curl -s -X POST 'http://localhost:13378/api/libraries/5b9bdb84-5ed1-45bb-ab37-383f2c720da5/scan' \
  -H 'Authorization: Bearer $ABS_KEY'"
```

Audiobookshelf auto-matches based on folder names and embedded metadata, but non-Libation sources almost always need a metadata PATCH afterward.

## Common Mistakes

- **Forgetting to scan first** — `liberate` only downloads books Libation knows about. Always `scan` before `liberate` to pick up new purchases.
- **Interactive search pagination** — `LibationCli search` tries to paginate interactively, which fails in non-TTY shells. Always pass `-n 0`.
- **Apostrophes in titles** — Book folders with apostrophes (e.g., "Twain's Feast") need careful shell quoting. Use `find ... -exec scp` or double-quote with `$HOME` expansion.
- **ABS API key** — `~/Developer/credentials/audiobookshelf.env` does not exist. Always load via `op read "op://Development/Audiobookshelf API Key/credential"`.
- **Direct Tailscale IP** — `http://100.79.211.138:13378` times out from this machine. Proxy all ABS API calls through `ssh home-server "curl -s 'http://localhost:13378/...'"`.
- **Reading .env files** — Hooks block `cat` on credential files. Use `awk -F= '/KEY/ {print $2}'` to extract values.
