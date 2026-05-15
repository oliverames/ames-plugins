#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "mcp[cli]>=1.0",
#   "httpx>=0.27",
# ]
# ///
"""Merriam-Webster Collegiate Dictionary + Thesaurus MCP server.

Wraps the official Merriam-Webster Dictionary API
(https://dictionaryapi.com). Requires two API keys, one each for the
Collegiate Dictionary and Collegiate Thesaurus references.

Environment:
    MW_DICTIONARY_KEY  — Collegiate Dictionary API key
    MW_THESAURUS_KEY   — Collegiate Thesaurus API key

Tools:
    define(word)     — definitions, part of speech, pronunciation, etymology
    synonyms(word)   — synonym groups by sense
    antonyms(word)   — antonym groups by sense
    spell(word)      — spelling suggestions when the word is not in the dictionary
    lookup(word)     — combined define + synonyms in a single call
"""

from __future__ import annotations

import os
import sys
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

DICT_BASE = "https://www.dictionaryapi.com/api/v3/references/collegiate/json/"
THES_BASE = "https://www.dictionaryapi.com/api/v3/references/thesaurus/json/"

_dict_key = os.environ.get("MW_DICTIONARY_KEY")
_thes_key = os.environ.get("MW_THESAURUS_KEY")

if not _dict_key or not _thes_key:
    print(
        "merriam-webster: set MW_DICTIONARY_KEY and MW_THESAURUS_KEY env vars",
        file=sys.stderr,
    )
    sys.exit(1)

DICT_KEY: str = _dict_key
THES_KEY: str = _thes_key

mcp = FastMCP("merriam-webster")


async def _fetch(base: str, word: str, key: str) -> list[Any]:
    """Call the MW API and return parsed JSON. Raises on transport errors."""
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{base}{word}", params={"key": key})
        r.raise_for_status()
        return r.json()


def _is_suggestion_list(data: list[Any]) -> bool:
    """MW returns a list of strings when the word is not found."""
    return bool(data) and isinstance(data[0], str)


def _short_pron(entry: dict) -> str:
    """Pull the first pronunciation from an entry, if present."""
    prs = entry.get("hwi", {}).get("prs", [])
    return prs[0].get("mw", "") if prs else ""


def _etymology(entry: dict) -> str:
    """Pull etymology text. MW etymology is a list of [tag, text] pairs."""
    et = entry.get("et")
    if not et or not isinstance(et, list):
        return ""
    chunks = [c[1] for c in et if isinstance(c, list) and len(c) == 2]
    return " ".join(chunks).strip()


@mcp.tool()
async def define(word: str) -> dict:
    """Look up a word in the Merriam-Webster Collegiate Dictionary.

    Returns definitions, part of speech, pronunciation, and etymology for up
    to the first three matching entries. If the word is not found, returns
    `found: false` plus spelling suggestions.
    """
    data = await _fetch(DICT_BASE, word, DICT_KEY)
    if not data:
        return {"word": word, "found": False, "suggestions": []}
    if _is_suggestion_list(data):
        return {"word": word, "found": False, "suggestions": data[:10]}
    entries = []
    for entry in data[:3]:
        if not isinstance(entry, dict):
            continue
        entries.append({
            "headword": entry.get("hwi", {}).get("hw", ""),
            "part_of_speech": entry.get("fl", ""),
            "pronunciation": _short_pron(entry),
            "definitions": entry.get("shortdef", []),
            "etymology": _etymology(entry),
        })
    return {"word": word, "found": True, "entries": entries}


@mcp.tool()
async def synonyms(word: str) -> dict:
    """Get synonyms for a word from the Merriam-Webster Collegiate Thesaurus.

    Returns synonyms grouped by sense (each sense ships its own synonym
    cluster). If the word is not found, returns `found: false` plus
    spelling suggestions.
    """
    data = await _fetch(THES_BASE, word, THES_KEY)
    if not data:
        return {"word": word, "found": False, "suggestions": []}
    if _is_suggestion_list(data):
        return {"word": word, "found": False, "suggestions": data[:10]}
    entries = []
    for entry in data[:3]:
        if not isinstance(entry, dict):
            continue
        meta = entry.get("meta", {})
        entries.append({
            "headword": entry.get("hwi", {}).get("hw", ""),
            "part_of_speech": entry.get("fl", ""),
            "definitions": entry.get("shortdef", []),
            "synonym_groups": meta.get("syns", []),
        })
    return {"word": word, "found": True, "entries": entries}


@mcp.tool()
async def antonyms(word: str) -> dict:
    """Get antonyms for a word from the Merriam-Webster Collegiate Thesaurus.

    Returns antonyms grouped by sense. Many words have no antonyms in MW;
    in that case `entries` will be empty.
    """
    data = await _fetch(THES_BASE, word, THES_KEY)
    if not data or _is_suggestion_list(data):
        return {"word": word, "found": False}
    entries = []
    for entry in data[:3]:
        if not isinstance(entry, dict):
            continue
        meta = entry.get("meta", {})
        ants = meta.get("ants", [])
        if not ants:
            continue
        entries.append({
            "headword": entry.get("hwi", {}).get("hw", ""),
            "part_of_speech": entry.get("fl", ""),
            "definitions": entry.get("shortdef", []),
            "antonym_groups": ants,
        })
    return {"word": word, "found": bool(entries), "entries": entries}


@mcp.tool()
async def spell(word: str) -> dict:
    """Check the spelling of a word against the Collegiate Dictionary.

    If the word is found, returns `correct: true` and the headword. If not
    found, returns `correct: false` plus up to ten suggested spellings.
    """
    data = await _fetch(DICT_BASE, word, DICT_KEY)
    if not data:
        return {"word": word, "correct": False, "suggestions": []}
    if _is_suggestion_list(data):
        return {"word": word, "correct": False, "suggestions": data[:10]}
    first = data[0]
    headword = first.get("hwi", {}).get("hw", word) if isinstance(first, dict) else word
    return {"word": word, "correct": True, "headword": headword}


@mcp.tool()
async def lookup(word: str) -> dict:
    """Combined dictionary + thesaurus lookup for editorial work.

    Returns definitions, part of speech, pronunciation, and synonym groups
    in a single response. Best for AP-style copy editing where you want
    spelling, meaning, and word-choice alternatives in one round trip.
    """
    dict_result = await define(word)
    thes_result = await synonyms(word)
    return {
        "word": word,
        "dictionary": dict_result,
        "thesaurus": thes_result,
    }


if __name__ == "__main__":
    mcp.run()
