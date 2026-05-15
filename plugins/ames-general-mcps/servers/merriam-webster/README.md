# Merriam-Webster MCP server

A self-contained MCP server that wraps the [Merriam-Webster Dictionary API](https://dictionaryapi.com/) and exposes the Collegiate Dictionary and Collegiate Thesaurus references as tools.

## What it provides

| Tool | Purpose |
|------|---------|
| `define(word)` | Definitions, part of speech, pronunciation, etymology (Collegiate Dictionary) |
| `synonyms(word)` | Synonym groups by sense (Collegiate Thesaurus) |
| `antonyms(word)` | Antonym groups by sense (Collegiate Thesaurus) |
| `spell(word)` | Spelling check with suggestions if the word isn't in the dictionary |
| `lookup(word)` | Combined dictionary + thesaurus reply in one round trip |

Use cases: AP-style copy editing, BCBS writing review, spell-checking unfamiliar terms, finding non-AI-sounding synonyms, verifying word choice and part-of-speech before commitments like headlines.

## How it runs

The server is a single Python file with [PEP 723](https://peps.python.org/pep-0723/) inline dependencies. It's launched by `uv run --script`, which materializes the dependency env on demand — no install step required.

```text
uv run --script servers/merriam-webster/server.py
```

The plugin's `.mcp.json` points Claude Code at this path via `${CLAUDE_PLUGIN_ROOT}/servers/merriam-webster/server.py` and forwards two env vars.

## Configuration

| Env var | Value | Source |
|---------|-------|--------|
| `MW_DICTIONARY_KEY` | Collegiate Dictionary API key | 1Password Development vault: *Merriam-Webster Collegiate Dictionary API Key* |
| `MW_THESAURUS_KEY` | Collegiate Thesaurus API key | 1Password Development vault: *Merriam-Webster Collegiate Thesaurus API Key* |

Wired into `~/.claude/settings.json` env block (plaintext for Claude Code's MCP launcher) and mirrored in `~/.claude/.env` as `op://` references (for backup parity).

## Quota

Merriam-Webster's free API tier allows 1,000 queries per day per key under their noncommercial-use terms. Two keys (Dictionary + Thesaurus) give two separate quotas. Commercial use requires written approval from MW.

## Upstream

Inspired by [tannmaycoding/Dictionary-MCP](https://github.com/tannmaycoding/Dictionary-MCP). This implementation is a rewrite that:

- Supports both Dictionary AND Thesaurus (upstream is Dictionary-only)
- Uses async `httpx` rather than blocking `requests`
- Uses PEP 723 inline deps rather than a separate venv
- Adds a combined `lookup` tool for one-shot editorial queries
- Returns structured dicts rather than printed strings, so tool results stay parseable

## Pairs with

`ames-standalone-skills:ap-style` — the AP Style skill references this server's `define` and `synonyms` tools for word verification during editorial work.
