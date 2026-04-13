---
name: apple-music-rip
version: 0.2.3
description: This skill should be used when the user asks to "download Apple Music tracks", "rip Apple Music", "download songs", "get DRM-free music", "download music for my headphones", or asks anything about the apple-music-rip workflow or Apple Music AAC downloads.
---

## Overview

The apple-music-rip skill downloads Apple Music content as DRM-free 256kbps AAC files using gamdl. Output is compatible with any device that plays AAC/M4A.

**Workflow:** Apple Music URL → gamdl (256kbps AAC download) → `~/Music/Swimming Files/`

## Installed Locations

| Component | Path |
|-----------|------|
| gamdl | Homebrew (`brew install gamdl`) |
| Config | `~/.gamdl/config.ini` |
| Cookies | `~/.gamdl/cookies.txt` |
| Output | `~/Music/Swimming Files/` |

## Plugin Commands

| Command | Description |
|---------|-------------|
| `/apple-music-rip:setup` | One-time setup (install gamdl, configure, export cookies) |
| `/apple-music-rip:download <url>` | Download a song, album, or playlist |

## Shokz OpenSwim Pro Format Support

The OpenSwim Pro supports MP3, AAC, FLAC, and WAV. gamdl downloads 256kbps AAC (.m4a) which plays natively — no conversion needed.

## Running Downloads

```bash
gamdl "https://music.apple.com/us/album/..."
```

gamdl reads config from `~/.gamdl/config.ini` and cookies from `~/.gamdl/cookies.txt`.

## Cookie Setup & Refresh

Cookies are extracted automatically using `@steipete/sweet-cookie` (npm). The user just needs to:

1. Log in to https://music.apple.com in any browser (Chrome, Firefox, Edge, or Safari)
2. Tell Claude which browser they used

Claude then runs sweet-cookie to extract the cookies and writes them to `~/.gamdl/cookies.txt`:

```bash
npx @steipete/sweet-cookie --url "https://music.apple.com" --browser chrome --format netscape > ~/.gamdl/cookies.txt
```

Adjust `--browser` to match what the user logged in with: `chrome`, `firefox`, `edge`, or `safari`.

Cookies expire periodically — if downloads start failing with auth errors, ask the user to log in again and re-run the extraction.

## Troubleshooting

**Auth/cookie errors** — Ask the user to log in to music.apple.com again, then re-extract cookies with sweet-cookie.

**Track not available** — May not be in your storefront region.

**gamdl not found** — `brew install gamdl`

**sweet-cookie fails** — Ensure Node ≥22. Install with `npm i -g @steipete/sweet-cookie` if npx isn't working.
