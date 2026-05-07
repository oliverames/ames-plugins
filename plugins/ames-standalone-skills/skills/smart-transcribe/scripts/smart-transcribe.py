#!/usr/bin/env python3
"""
Smart Transcribe - Multi-Engine Transcription with Agent Merge
==============================================================

Default transcription uses Cohere Transcribe locally plus Mistral Voxtral,
ElevenLabs Scribe v2, and AssemblyAI Universal-3 Pro. Merge uses headless
Claude Code first and falls back to headless Codex when Claude is unavailable
or rate-limited.
"""

import sys
import os
import re
import json
import math
import argparse
import copy
import shutil
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from common import (
    CONTEXTS_DIR, SKILL_CONTEXTS_DIR, MIGRATION_MARKER_DIR,
    VENV_PYTHON, CONFIG_DIR, STATUS_FILE_NAME, RUN_LOG_NAME,
    HTTP_RETRYABLE_SIGNALS, HTTP_NON_RETRYABLE_SIGNALS, HTTP_BACKOFF_DELAYS_S,
    resolve_key, load_dictionary, get_context_terms,
    get_dictionary_paths, flatten_entities, merge_dicts,
    compress_audio, convert_16khz_mono, chunk_audio, get_audio_duration,
    run_engine_text, retry_engine,
    print_runtime_banner, resolve_engine_python, require_supported_python,
    supported_python_string, python_version_supported, resolve_key_status, check_ffmpeg_tools,
    write_status,
)

DEFAULT_ENGINES = ["assemblyai-u3-pro", "scribe-v2", "voxtral-small", "gemini-3-pro"]
DEFAULT_FALLBACK_ENGINE = "gpt4o-mini-transcribe"
LOCAL_ENGINE_IDS = {"voxtral-mini-local", "cohere-transcribe"}
ENGINE_TIMEOUTS = {
    "assemblyai-u3-pro": 3600,
    "scribe-v2": 3600,
    "voxtral-small": 3600,
    "gemini-3-pro": 3600,
    "gpt4o-transcribe": 3600,
    "gpt4o-mini-transcribe": 3600,
    "voxtral-mini-local": 900,
    "cohere-transcribe": 900,
}
CANONICAL_SPEAKER_RE = re.compile(r"Speaker\s+([A-Za-z0-9_-]+)", re.IGNORECASE)
MERGE_RATE_LIMIT_PATTERNS = (
    "rate limit",
    "429",
    "too many requests",
    "overloaded",
    "capacity",
    "try again later",
)

MERGE_OUTPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "metadata": {
            "type": "object",
            "additionalProperties": True,
            "properties": {
                "title": {"type": "string"},
                "speakers": {"type": "array", "items": {"type": "string"}},
                "summary": {"type": "string"},
                "date_mentioned": {"type": "string"},
            },
            "required": ["title", "speakers", "summary", "date_mentioned"],
        },
        "transcript": {"type": "string"},
        "transparency_report": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "applied": {"type": "array", "items": {"type": "string"}},
                "uncertain": {"type": "array", "items": {"type": "string"}},
                "preserved": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["applied", "uncertain", "preserved"],
        },
        "suggestions": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["metadata", "transcript", "transparency_report", "suggestions"],
}

# =============================================================================
# PER-CONTEXT CONFIGURATION
# =============================================================================


_RECORDING_SPECIFIC_PATTERNS = re.compile(
    r"\b(main topic|call between|today'?s? (meeting|call|session)|discussed?|"
    r"this (call|meeting|session|recording)|about:|"
    r"\d{4}-\d{2}-\d{2}|\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b.*\d{4})\b",
    re.IGNORECASE,
)


def _looks_recording_specific(note: str) -> bool:
    """Return True if the note text looks like it describes a specific recording rather than
    general background. Heuristic — false positives are fine since the user can still confirm."""
    return bool(_RECORDING_SPECIFIC_PATTERNS.search(note))


def _run_context_interview(name: str) -> dict:
    """Interactive first-run interview to seed a new named context.

    Asks 3 focused questions and returns a dict in standard dictionary schema.
    """
    print(f"\n🆕 New context '{name}' — quick setup (3 questions):")
    print("   Press Enter to skip any question.\n")

    context: dict = {"corrections": {}, "entities": {}, "speakers": {}, "notes": []}

    # Q1: Recurring proper nouns
    raw = input("   1. Recurring proper nouns often mis-transcribed (comma-separated, e.g. 'Waitsfield, BCBS'):\n   > ").strip()
    if raw:
        terms = [t.strip() for t in raw.split(",") if t.strip()]
        context["entities"]["context_terms"] = terms

    # Q2: Specific corrections
    raw = input("\n   2. Known wrong→right pairs (one per line, format: 'wrong = right'). Blank line when done:\n").strip()
    lines = []
    while True:
        line = input("   > ").strip()
        if not line:
            break
        lines.append(line)
    for line in lines:
        if "=" in line:
            wrong, _, right = line.partition("=")
            wrong, right = wrong.strip().lower(), right.strip()
            if wrong and right:
                context["corrections"][wrong] = right

    # Q3: Context notes — background reference only, never recording-specific
    raw = input(
        "\n   3. Permanent background context (e.g. 'Vermont health insurer; speakers are doctors and admin staff').\n"
        "      ⚠️  Background only — never recording-specific topics. For per-run hints, use --speakers instead.\n"
        "   > "
    ).strip()
    if raw:
        if _looks_recording_specific(raw):
            print(
                f"\n   ⚠️  This note looks recording-specific:\n      \"{raw}\"\n"
                f"   Recording-specific notes will appear in every future '{name}' run."
            )
            confirm = input("   Save it permanently to this context anyway? [y/N] ").strip().lower()
            if confirm != "y":
                print("   Skipped. Per-run context can be passed via --speakers (names) or noted in the merge bundle.")
                raw = ""
        if raw:
            context["notes"].append(raw)

    return context


def _flatten_corrections(corrections: dict) -> dict:
    """Normalise corrections from JSON storage to flat wrong->right.

    Accepts either nested {category: {old: new}} (current format) or already-flat
    {old: new} (legacy/user contexts). Lowercases keys to match load_dictionary().
    """
    if not isinstance(corrections, dict) or not corrections:
        return {}
    first_value = next(iter(corrections.values()), None)
    if isinstance(first_value, dict):
        flat: dict = {}
        for mappings in corrections.values():
            if isinstance(mappings, dict):
                for wrong, right in mappings.items():
                    flat[str(wrong).lower()] = right
        return flat
    return {str(k).lower(): v for k, v in corrections.items()}


def _resolve_context_path(name: str) -> Path | None:
    """Find a context file by name. User-side wins over skill-shipped."""
    user_path = CONTEXTS_DIR / f"{name}.json"
    if user_path.exists():
        return user_path
    skill_path = SKILL_CONTEXTS_DIR / f"{name}.json"
    if skill_path.exists():
        return skill_path
    return None


def _load_context(name: str) -> dict:
    """Load a named context, running the first-run interview if it doesn't exist.

    Resolution order: user contexts dir → skill-shipped contexts dir → interview.
    User-side overlay overrides skill-shipped, so users can extend or replace.

    Returns a dict in standard dictionary schema ready for merge_dicts().
    """
    CONTEXTS_DIR.mkdir(parents=True, exist_ok=True)
    ctx_path = _resolve_context_path(name)

    if ctx_path is not None:
        try:
            data = json.loads(ctx_path.read_text())
            flat_corrections = _flatten_corrections(data.get("corrections", {}))
            flat_entities = flatten_entities(data.get("entities", {}))
            origin = "user" if ctx_path.parent == CONTEXTS_DIR else "shipped"
            print(f"🗂️  Context '{name}' [{origin}]: {len(flat_corrections)} corrections, {len(flat_entities)} entities")
            return {
                "corrections": flat_corrections,
                "entities": flat_entities,
                "speakers": data.get("speakers", {}),
                "notes": data.get("notes", []),
            }
        except (json.JSONDecodeError, TypeError):
            print(f"⚠️  Could not read context '{name}' — re-running interview.")

    # First run: interview
    context = _run_context_interview(name)

    # Persist
    user_path = CONTEXTS_DIR / f"{name}.json"
    user_path.write_text(json.dumps(context, indent=2, ensure_ascii=False) + "\n")
    print(f"\n✅ Context '{name}' saved to {user_path}")

    context["entities"] = flatten_entities(context.get("entities", {}))
    return context


def list_contexts() -> None:
    """Print all saved context names from user dir AND skill-shipped contexts."""
    CONTEXTS_DIR.mkdir(parents=True, exist_ok=True)
    user_contexts = sorted(CONTEXTS_DIR.glob("*.json"))
    skill_contexts = sorted(SKILL_CONTEXTS_DIR.glob("*.json")) if SKILL_CONTEXTS_DIR.exists() else []
    user_names = {p.stem for p in user_contexts}
    if not user_contexts and not skill_contexts:
        print("No saved contexts. Create one with --context <name>.")
        return
    if user_contexts:
        print("User contexts (~/.config/smart-transcribe/contexts):")
        for p in user_contexts:
            print(f"  {p.stem}")
    if skill_contexts:
        print("\nSkill-shipped contexts (read-only, override by saving same name in user dir):")
        for p in skill_contexts:
            tag = " [shadowed by user]" if p.stem in user_names else ""
            print(f"  {p.stem}{tag}")


def _maybe_print_migration_notice(dictionary: dict, dict_path: Path) -> None:
    """Print a one-time notice if user dict still contains pre-4.0 VT/BCBS rules.

    The 2026-05-06 split moved 206 VT-anchored rules into the bcbs-vt context
    overlay. Users who synced before that split have an over-stuffed user dict
    that applies VT corrections globally — exactly the misfire that prompted
    the split. We don't auto-migrate (would clobber user customizations) but we
    do nudge once.
    """
    MIGRATION_MARKER_DIR.mkdir(parents=True, exist_ok=True)
    marker = MIGRATION_MARKER_DIR / "2026-05-bcbs-vt-split.done"
    if marker.exists():
        return
    # Heuristic: if user dict has the old VT category key, it's pre-split.
    corrections = dictionary.get("corrections", {})
    has_vt_categories = any(
        cat in corrections for cat in ("places", "beer_breweries", "beta_aviation", "ski_industry")
    )
    if not has_vt_categories:
        marker.write_text(f"no-action {datetime.now().isoformat()}\n")
        return
    print("─" * 60, file=sys.stderr)
    print("📢 ONE-TIME NOTICE: Dictionary structure changed (v3 → v4)", file=sys.stderr)
    print("─" * 60, file=sys.stderr)
    print(f"Your user dictionary at {dict_path} contains VT/BCBS-specific rules", file=sys.stderr)
    print("(places, breweries, Beta Aviation, etc.) that are now scoped to a", file=sys.stderr)
    print("dedicated context overlay rather than applied globally.", file=sys.stderr)
    print(file=sys.stderr)
    print("Why: a 'mont-royal -> Mont-Royal' rule was misfiring on a Rivian", file=sys.stderr)
    print("service call where Oliver actually said 'Montreal'. Same pattern", file=sys.stderr)
    print("affected 'bar -> Barre' on a 'light bar' reference. Domain-specific", file=sys.stderr)
    print("rules don't belong in the global default.", file=sys.stderr)
    print(file=sys.stderr)
    print("To get the same behavior as before for VT/BCBS recordings:", file=sys.stderr)
    print("    smart-transcribe.py audio.m4a --context bcbs-vt", file=sys.stderr)
    print(file=sys.stderr)
    print("Your existing user dictionary is unchanged. To fully migrate, edit", file=sys.stderr)
    print(f"    {dict_path}", file=sys.stderr)
    print("and remove the VT-specific categories (they live in the shipped", file=sys.stderr)
    print("bcbs-vt context now). This notice will not appear again.", file=sys.stderr)
    print("─" * 60, file=sys.stderr)
    print(file=sys.stderr)
    marker.write_text(f"shown {datetime.now().isoformat()}\n")


# =============================================================================
# TRANSCRIPT FILE PARSERS (for --fix-transcript mode)
# =============================================================================

def parse_srt(path: Path) -> str:
    """Parse an SRT subtitle file into plain dialogue text."""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    dialogue: list[str] = []
    timing_re = re.compile(r"^\d{2}:\d{2}:\d{2}[,\.]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[,\.]\d{3}")
    seq_re = re.compile(r"^\d+\s*$")
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if seq_re.match(stripped):
            continue
        if timing_re.match(stripped):
            continue
        dialogue.append(stripped)
    return " ".join(dialogue)


def parse_vtt(path: Path) -> str:
    """Parse a WebVTT file into plain dialogue text."""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    dialogue: list[str] = []
    timing_re = re.compile(r"\d{2}:\d{2}:\d{2}[\.,]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[\.,]\d{3}")
    # Also match MM:SS.mmm --> MM:SS.mmm (short form)
    timing_short_re = re.compile(r"\d{2}:\d{2}[\.,]\d{3}\s*-->\s*\d{2}:\d{2}[\.,]\d{3}")
    in_note = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("WEBVTT"):
            continue
        if stripped.startswith("NOTE"):
            in_note = True
            continue
        if in_note:
            if not stripped:
                in_note = False
            continue
        if not stripped:
            continue
        if timing_re.search(stripped) or timing_short_re.search(stripped):
            continue
        dialogue.append(stripped)
    return " ".join(dialogue)


def parse_txt(path: Path) -> str:
    """Read a plain text or Markdown transcript as-is."""
    return path.read_text(encoding="utf-8", errors="replace").strip()


def parse_transcript_file(path: Path) -> str:
    """Auto-detect format from extension and parse to plain text."""
    ext = path.suffix.lower()
    if ext == ".srt":
        return parse_srt(path)
    if ext == ".vtt":
        return parse_vtt(path)
    return parse_txt(path)  # .txt, .md, or anything else


# =============================================================================
# TRANSPARENCY REPORT DISPLAY
# =============================================================================

_REPORT_ICONS = {"APPLIED": "✏️ ", "UNCERTAIN": "❓", "PRESERVED": "🛡️ "}
_UNSAFE_FILENAME_RE = re.compile(r'[\\/*?:"<>|]')


def _sanitize_filename(text: str, max_len: int = 50) -> str:
    return _UNSAFE_FILENAME_RE.sub("", text)[:max_len]

def display_transparency_report(report_text: str) -> None:
    """Pretty-print the LLM's transparency report to the terminal."""
    if not report_text or not report_text.strip():
        return

    print("\n" + "=" * 60)
    print("TRANSPARENCY REPORT")
    print("=" * 60)

    # Split into sub-sections on the labels APPLIED / UNCERTAIN / PRESERVED
    section_re = re.compile(r"^(APPLIED|UNCERTAIN|PRESERVED)\s*:?\s*$", re.IGNORECASE | re.MULTILINE)
    parts = section_re.split(report_text.strip())

    if len(parts) == 1:
        # LLM didn't use sub-sections — just print raw
        print(report_text.strip())
    else:
        # parts is: [pre, label, body, label, body, ...]
        i = 1
        while i < len(parts) - 1:
            label = parts[i].upper()
            body = parts[i + 1].strip()
            print(f"\n{_REPORT_ICONS.get(label, '')} {label}:")
            for line in body.splitlines():
                if line.strip():
                    print(f"   {line.strip()}")
            i += 2

    print("=" * 60)


def interactive_corrections_review(report_text: str) -> None:
    """Interactive review of APPLIED corrections from the transparency report.

    For each APPLIED item, prompt [y] keep  [n] dispute  [s] skip.
    Disputed items are written to the suggestions log with status='disputed'.
    """
    if not report_text or not report_text.strip():
        print("No transparency report available for review.")
        return

    # Extract APPLIED section
    applied_re = re.compile(r"APPLIED\s*:?\s*\n(.*?)(?=UNCERTAIN|PRESERVED|$)", re.IGNORECASE | re.DOTALL)
    m = applied_re.search(report_text)
    if not m:
        print("No APPLIED section found in transparency report.")
        return

    applied_lines = [ln.strip() for ln in m.group(1).splitlines() if ln.strip() and not ln.strip().startswith("#")]
    if not applied_lines:
        print("No applied corrections to review.")
        return

    print(f"\n📋 Reviewing {len(applied_lines)} applied correction(s).")
    print("   [y] keep (default)  [n] dispute (log for dict cleanup)  [s] skip\n")

    disputed: list[dict] = []
    for item in applied_lines:
        resp = input(f"   {item}\n   > ").strip().lower()
        if resp == "n":
            # Parse "wrong" → "right" from the item text
            entry: dict = {"raw": item, "status": "disputed", "timestamp": datetime.now().isoformat()}
            arrow = "→" if "→" in item else "->" if "->" in item else None
            if arrow:
                parts = item.split(arrow, 1)
                entry["wrong"] = parts[0].strip().strip('"\'')
                right_part = parts[1].split("(")[0].strip().strip('"\'')
                entry["right"] = right_part
            disputed.append(entry)
            print("   Marked as disputed.\n")
        elif resp == "s":
            print("   Skipped.\n")
        else:
            print("   Kept.\n")

    if disputed:
        _, suggestions_path = get_dictionary_paths()
        suggestions_path.parent.mkdir(parents=True, exist_ok=True)
        with open(suggestions_path, "a") as f:
            for entry in disputed:
                f.write(json.dumps(entry) + "\n")
        print(f"📝 {len(disputed)} disputed correction(s) logged to {suggestions_path.name}")


def parse_engine_python_overrides(raw: str | None) -> dict[str, str]:
    overrides: dict[str, str] = {}
    if not raw:
        return overrides
    for chunk in raw.split(","):
        item = chunk.strip()
        if not item:
            continue
        if "=" not in item:
            raise ValueError(f"Invalid --engine-python item '{item}'. Expected engine=/path/to/python")
        engine_id, path = item.split("=", 1)
        overrides[engine_id.strip()] = path.strip()
    return overrides


def canonical_speaker(label: str | None) -> str | None:
    if not label:
        return None
    match = CANONICAL_SPEAKER_RE.search(label)
    if match:
        return f"Speaker {match.group(1)}"
    return label.strip()


def normalize_segments(raw_segments: list[dict] | None, source_engine: str) -> list[dict]:
    normalized = []
    for segment in raw_segments or []:
        normalized.append({
            "speaker": canonical_speaker(segment.get("speaker") if isinstance(segment, dict) else None),
            "start": segment.get("start") if isinstance(segment, dict) else None,
            "end": segment.get("end") if isinstance(segment, dict) else None,
            "text": segment.get("text", "") if isinstance(segment, dict) else "",
            "confidence": segment.get("confidence") if isinstance(segment, dict) else None,
            "source_engine": source_engine,
        })
    return normalized


def extract_basic_segments(text: str, source_engine: str) -> list[dict]:
    segments: list[dict] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        speaker = None
        segment_text = stripped
        if stripped.startswith("**Speaker ") and ":**" in stripped:
            prefix, segment_text = stripped.split(":**", 1)
            speaker = canonical_speaker(prefix.replace("**", "").strip())
            segment_text = segment_text.strip()
        segments.append({
            "speaker": speaker,
            "start": None,
            "end": None,
            "text": segment_text,
            "confidence": None,
            "source_engine": source_engine,
        })
    return segments


def choose_recommended_base(engine_results: dict[str, dict]) -> str | None:
    preferred = ["AssemblyAI Universal-3 Pro", "ElevenLabs Scribe v2", "Cohere Transcribe (local)", "Mistral Voxtral Small"]
    for label in preferred:
        result = engine_results.get(label)
        if result and result.get("status") == "complete" and result.get("text"):
            return label
    for label, result in engine_results.items():
        if result.get("status") == "complete" and result.get("text"):
            return label
    return None


def emit_manual_merge_bundle(output_dir: Path, engine_results: dict[str, dict]) -> Path:
    bundle_path = output_dir / "comparison-bundle.md"
    recommended = choose_recommended_base(engine_results)
    parts = [
        "# Comparison Bundle",
        "",
        f"Recommended base transcript: {recommended or 'none'}",
        "",
    ]
    for label, result in engine_results.items():
        parts.extend([
            f"## {label}",
            "",
            f"Status: {result.get('status')}",
            f"Failure: {result.get('failure_reason') or 'none'}",
            "",
            result.get("text", "") or "_No transcript produced._",
            "",
        ])
    bundle_path.write_text("\n".join(parts), encoding="utf-8")
    return bundle_path


def _format_engine_status_block(engine_results: dict[str, dict] | None) -> list[str]:
    """Build the **Engine Status** markdown block for the agent-merge bundle.

    Surfaces success/failure/quality concerns at the top so the merging agent
    knows up-front which transcripts to trust, rather than having to dig through
    a separate run.log to learn that (e.g.) Scribe v2 was quota-blocked or
    Cohere produced suspiciously sparse output.
    """
    if not engine_results:
        return []
    lines = ["## Engine Status", ""]
    lines.append("| Engine | Status | Chars | Quality | Notes |")
    lines.append("|---|---|---|---|---|")
    for label, result in engine_results.items():
        status = result.get("status", "unknown")
        char_count = result.get("char_count", len(result.get("text", "") or ""))
        quality = result.get("quality_concern")
        if status == "complete" and quality is None:
            status_icon = "✅ complete"
            quality_str = "OK"
            notes_str = ""
        elif status == "complete" and quality is not None:
            status_icon = "⚠️ complete with concern"
            quality_str = quality.get("flag", "concern")
            notes_str = (
                f"{quality.get('chars_per_minute', '?')} chars/min — "
                f"{quality.get('detail', '')[:120]}"
            )
        else:
            status_icon = "❌ failed"
            quality_str = "n/a"
            notes_str = (result.get("failure_reason") or "")[:120]
        lines.append(
            f"| {label} | {status_icon} | {char_count:,} | {quality_str} | {notes_str} |"
        )
    lines.append("")
    lines.append(
        "> **Trust ranking for merge:** treat ❌ failed engines as absent (do not include in merge); "
        "treat ⚠️ engines with quality concerns as low-confidence (use only as a tiebreaker, never as the spine); "
        "✅ engines are normal-confidence inputs."
    )
    lines.append("")
    return lines


def emit_agent_merge_bundle(
    output_dir: Path,
    transcripts: dict[str, str],
    dictionary: dict,
    source_file: str,
    speakers: list | None = None,
    mode: str = "merge",
    engine_results: dict[str, dict] | None = None,
) -> Path:
    """Write a merge bundle for the current chat agent to consume."""
    output_dir.mkdir(parents=True, exist_ok=True)
    bundle_path = output_dir / "agent-merge-bundle.md"
    corrections = list(dictionary.get("corrections", {}).items())[:200]
    entities = list(dictionary.get("entities", []))[:100]
    notes = list(dictionary.get("notes", []))[:60]

    parts = [
        "# Agent Merge Bundle",
        "",
        "## Instructions For Current Agent",
        "",
        "Merge the source transcript outputs into one accurate Markdown transcript. Apply dictionary corrections conservatively, preserve intentional casual speech, and put uncertain passages in a transparency report instead of guessing.",
        "",
        "Save the final transcript using the **Output Template** below. The structure is mandatory — fields render in a consistent order across runs so future readers and downstream tooling can scan transcripts uniformly.",
        "",
        "### Output Template (mandatory structure)",
        "",
        "````markdown",
        "# {Title} — Transcript",
        "",
        "## Metadata",
        "",
        "- **Source file:** `{path}`",
        "- **Duration:** {hh:mm:ss}",
        "- **Transcribed:** {YYYY-MM-DD}",
        "- **Engines used:** {engine list with success/failure note from Engine Status block above}",
        "- **Verification source:** {if any external --reference or sidecar was provided; else 'none'}",
        "",
        "## Speakers",
        "",
        "- **{Speaker A name or label}** — {role/context if known}",
        "- **{Speaker B name or label}** — {role/context if known}",
        "",
        "## Summary",
        "",
        "{2–4 paragraph plain-prose summary. No bullets. Cover the actual content of the call, not engine performance.}",
        "",
        "---",
        "",
        "## Transcript",
        "",
        "**{Speaker}:** {turn text}",
        "",
        "**{Speaker}:** {turn text}",
        "",
        "...",
        "",
        "---",
        "",
        "## Transparency Report",
        "",
        "### APPLIED corrections",
        "",
        "| Original (engine output) | Corrected | Source / Reason |",
        "|---|---|---|",
        "| {token as engines rendered it} | {corrected form} | {which engine had it right; or which dictionary rule applied; or which reference confirmed} |",
        "",
        "### UNCERTAIN — left as-is, flagged",
        "",
        "- **{passage or token}** — {why it's uncertain; what would resolve it}",
        "",
        "### PRESERVED — intentional casual speech",
        "",
        "- {kept as-spoken: filler words, false starts, profanity, regional phrasing, etc.}",
        "",
        "### Engine-degradation note",
        "",
        "{One short paragraph noting any engine that failed, was skipped, or produced suspect output (per the Engine Status block). Omit this section if all engines succeeded cleanly.}",
        "",
        "### Dictionary suggestions",
        "",
        "- {new proper nouns, recurring mis-corrections, or rule misfires worth adding/removing/scoping}",
        "- Or: 'No new dictionary suggestions from this recording.'",
        "````",
        "",
    ]

    # Engine status block — what succeeded, what failed, what's suspect
    parts.extend(_format_engine_status_block(engine_results))

    parts.extend([
        "## Run Metadata",
        "",
        "```json",
        json.dumps({
            "source_file": source_file,
            "mode": mode,
            "speakers": speakers or [],
            "transcript_sources": list(transcripts.keys()),
        }, indent=2, ensure_ascii=False),
        "```",
        "",
        "## Known Corrections",
        "",
    ])
    if corrections:
        parts.extend(f"- {wrong} -> {right}" for wrong, right in corrections)
    else:
        parts.append("_None_")

    parts.extend(["", "## Known Entities", ""])
    parts.append(", ".join(entities) if entities else "_None_")

    parts.extend(["", "## Context Notes", ""])
    parts.append(
        "> ⚠️ These notes are **background reference from the context file**, not recording-specific."
        " Verify against the actual transcript; do NOT carry them forward verbatim into the merged output."
    )
    parts.append("")
    if notes:
        parts.extend(f"- {note}" for note in notes)
    else:
        parts.append("_None_")

    parts.extend(["", "## Source Transcript Outputs", ""])
    for label, text in transcripts.items():
        parts.extend([f"### {label}", "", text or "_No transcript produced._", ""])

    bundle_path.write_text("\n".join(parts), encoding="utf-8")
    return bundle_path


def build_doctor_report(
    selected_engine_ids: list[str],
    engine_python_overrides: dict[str, str] | None = None,
    use_system_python: bool = False,
) -> dict:
    python_info = {
        "path": sys.executable,
        "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "supported": python_version_supported(sys.version_info),
    }
    keys = {
        key: resolve_key_status(key)
        for key in [
            "ASSEMBLYAI_API_KEY",
            "ELEVENLABS_API_KEY",
            "MISTRAL_API_KEY",
            "GOOGLE_API_KEY",
            "HF_TOKEN",
            "ANTHROPIC_API_KEY",
        ]
    }
    ffmpeg = check_ffmpeg_tools()
    claude_path = shutil.which("claude")
    codex_path = shutil.which("codex")
    engine_checks = {}
    for engine_id in selected_engine_ids:
        try:
            python_bin = resolve_engine_python(engine_id, engine_python_overrides, use_system_python)
            engine_checks[engine_id] = check_engine_runtime(engine_id, python_bin)
        except Exception as exc:
            engine_checks[engine_id] = {"ok": False, "error": str(exc)}
    report = {
        "python": python_info,
        "keys": keys,
        "ffmpeg": ffmpeg,
        "engines": selected_engine_ids,
        "engine_checks": engine_checks,
        "huggingface": {
            "token_resolved": keys["HF_TOKEN"]["resolved"],
            "cohere_model_mlx": "mlx-community/cohere-transcribe-03-2026-mlx-8bit",
            "cohere_model_pytorch": "CohereLabs/cohere-transcribe-03-2026",
            "note": "MLX path tried first (Apple Silicon); falls back to PyTorch if unavailable. Auth assumed when HF_TOKEN resolves.",
        },
        "merge_runners": {
            "primary": {
                "runner": "claude",
                "available": bool(claude_path),
                "path": claude_path,
            },
            "fallback": {
                "runner": "codex",
                "available": bool(codex_path),
                "path": codex_path,
            },
            "manual_merge_available": True,
        },
    }
    return report


# Conversational speech is typically 800-1500 chars/min. Below this threshold
# the engine output is suspect — likely truncation, VAD-less hallucination on
# silence, or a transient API error that returned a partial response. Cohere
# Transcribe in particular has no built-in voice-activity detection and has
# been observed producing 4,674 chars on a 58-minute file (≈80 chars/min) by
# hallucinating word salad through stretches of audio.
COHERENCE_MIN_CHARS_PER_MINUTE = 100.0


def assess_engine_coherence(text: str, audio_duration_s: float | None) -> dict | None:
    """Return a quality-concern dict if engine output looks suspiciously sparse.

    Returns None if everything's normal, or a dict like:
        {"flag": "low_text_density",
         "chars_per_minute": 79.6,
         "expected_min": 100.0,
         "detail": "Output ≪ typical conversational rate; may be truncated or VAD-less hallucination."}
    """
    if not text or not audio_duration_s or audio_duration_s <= 0:
        return None
    minutes = audio_duration_s / 60.0
    if minutes < 0.5:
        return None  # Too short to make a reliable judgment
    chars_per_min = len(text) / minutes
    if chars_per_min < COHERENCE_MIN_CHARS_PER_MINUTE:
        return {
            "flag": "low_text_density",
            "chars_per_minute": round(chars_per_min, 1),
            "expected_min": COHERENCE_MIN_CHARS_PER_MINUTE,
            "detail": (
                f"Engine output is {chars_per_min:.0f} chars/min vs. ~800-1500 typical for "
                "conversational speech. Likely truncation, partial response, or VAD-less "
                "hallucination. Treat as low-confidence in the merge."
            ),
        }
    return None


ENGINE_SDK_PROBES: dict[str, str] = {
    "assemblyai-u3-pro": "import assemblyai; print(getattr(assemblyai, '__version__', 'unknown'))",
    "scribe-v2": "import elevenlabs; print(getattr(elevenlabs, '__version__', 'unknown'))",
    "voxtral-small": "import mistralai; print(getattr(mistralai, '__version__', 'unknown'))",
    "voxtral-mini-local": "import mlx_audio; print(getattr(mlx_audio, '__version__', 'unknown'))",
    "cohere-transcribe": "import transformers; print(getattr(transformers, '__version__', 'unknown'))",
    "gemini-3-pro": "from google import genai; print(getattr(genai, '__version__', 'unknown'))",
    "gpt4o-transcribe": "import openai; print(getattr(openai, '__version__', 'unknown'))",
    "gpt4o-mini-transcribe": "import openai; print(getattr(openai, '__version__', 'unknown'))",
}


def collect_engine_sdk_versions(
    engine_ids: list[str],
    engine_python_overrides: dict[str, str] | None = None,
    use_system_python: bool = False,
) -> dict[str, str]:
    """Return {engine_id: sdk_version} for selected engines.

    Used to record exactly which SDK build produced each engine's output, so
    later sessions can tell whether a transcript was generated by the same
    Voxtral/Scribe/AssemblyAI version. Failures are recorded as
    'unavailable: <reason>' rather than raising — the run continues either way.
    """
    versions: dict[str, str] = {}
    for engine_id in engine_ids:
        probe = ENGINE_SDK_PROBES.get(engine_id)
        if not probe:
            versions[engine_id] = "unknown-engine"
            continue
        try:
            python_bin = resolve_engine_python(engine_id, engine_python_overrides, use_system_python)
            result = subprocess.run(
                [python_bin, "-c", probe],
                capture_output=True, text=True, timeout=8,
            )
            if result.returncode == 0:
                versions[engine_id] = (result.stdout.strip() or "unknown")
            else:
                err = (result.stderr or "").strip().splitlines()[-1] if result.stderr else "probe-failed"
                versions[engine_id] = f"unavailable: {err[:80]}"
        except Exception as exc:
            versions[engine_id] = f"unavailable: {str(exc)[:80]}"
    return versions


def check_engine_runtime(engine_id: str, python_bin: str) -> dict:
    check_scripts = {
        "assemblyai-u3-pro": r"""
import inspect, json
try:
    import assemblyai as aai
    params = list(inspect.signature(aai.TranscriptionConfig).parameters)
    print(json.dumps({
        "ok": hasattr(aai, "Transcriber") and "speech_models" in params and "keyterms_prompt" in params,
        "runtime": "assemblyai",
        "supported_args": [name for name in params if name in ("speech_models", "speaker_labels", "speakers_expected", "keyterms_prompt")],
    }))
except Exception as exc:
    print(json.dumps({"ok": False, "error": str(exc)}))
""",
        "scribe-v2": r"""
import inspect, json
try:
    try:
        from elevenlabs.client import ElevenLabs
    except Exception:
        from elevenlabs import ElevenLabs
    client = ElevenLabs(api_key="test")
    convert = getattr(getattr(client, "speech_to_text", None), "convert", None)
    params = list(inspect.signature(convert).parameters) if convert else []
    print(json.dumps({
        "ok": bool(convert) and any(name in params for name in ("file", "audio")),
        "runtime": "elevenlabs",
        "supported_args": [name for name in params if name in ("file", "audio")],
    }))
except Exception as exc:
    print(json.dumps({"ok": False, "error": str(exc)}))
""",
        "voxtral-small": r"""
import inspect, json
try:
    from mistralai import Mistral
    client = Mistral(api_key="test")
    complete = getattr(getattr(client, "audio", None), "transcriptions", None)
    complete = getattr(complete, "complete", None)
    params = list(inspect.signature(complete).parameters) if complete else []
    print(json.dumps({
        "ok": bool(complete) and "context_bias" in params and "diarize" in params,
        "runtime": "mistralai",
        "supported_args": [name for name in params if name in ("file", "file_id", "file_url", "context_bias", "diarize", "timestamp_granularities")],
    }))
except Exception as exc:
    print(json.dumps({"ok": False, "error": str(exc)}))
""",
        "gemini-3-pro": r"""
import json
try:
    from google import genai  # noqa: F401
    print(json.dumps({"ok": True, "runtime": "google-genai"}))
except Exception as exc:
    print(json.dumps({"ok": False, "error": str(exc)}))
""",
        "gpt4o-transcribe": r"""
import json
try:
    from openai import OpenAI  # noqa: F401
    print(json.dumps({"ok": True, "runtime": "openai"}))
except Exception as exc:
    print(json.dumps({"ok": False, "error": str(exc)}))
""",
        "gpt4o-mini-transcribe": r"""
import json
try:
    from openai import OpenAI  # noqa: F401
    print(json.dumps({"ok": True, "runtime": "openai"}))
except Exception as exc:
    print(json.dumps({"ok": False, "error": str(exc)}))
""",
        "cohere-transcribe": r"""
import json
result = {"ok": False, "runtime": "cohere-local"}
errors = {}
try:
    import mlx_audio  # noqa: F401
    result["mlx_audio"] = True
except Exception as exc:
    errors["mlx_audio"] = str(exc)
try:
    import torch  # noqa: F401
    import transformers  # noqa: F401
    result["torch_transformers"] = True
except Exception as exc:
    errors["torch_transformers"] = str(exc)
result["ok"] = bool(result.get("mlx_audio") or result.get("torch_transformers"))
if errors:
    result["errors"] = errors
print(json.dumps(result))
""",
    }
    script = check_scripts.get(engine_id)
    if not script:
        return {"ok": True, "runtime": "generic", "note": "No specialized self-check for this engine"}
    try:
        result = subprocess.run(
            [python_bin, "-c", script],
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ},
            check=False,
        )
    except Exception as exc:
        return {"ok": False, "error": str(exc), "python": python_bin}
    if result.returncode != 0:
        return {"ok": False, "error": result.stderr.strip() or result.stdout.strip() or "engine check failed"}
    try:
        payload = json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        payload = {"ok": False, "error": "Invalid engine check output", "stdout": result.stdout.strip()}
    payload["python"] = python_bin
    return payload


def _merge_runner_label(runner: str) -> str:
    if runner == "claude":
        return "Claude Code headless"
    if runner == "codex":
        return "Codex headless"
    return runner


def _is_rate_limited_merge_error(message: str) -> bool:
    lowered = (message or "").lower()
    return any(pattern in lowered for pattern in MERGE_RATE_LIMIT_PATTERNS)


def _run_merge_runner(runner: str, prompt_text: str, schema_path: str | None = None) -> tuple[str, str]:
    if runner == "claude":
        cmd = ["claude", "-p", "--model", "opus", "--effort", "medium", "--no-session-persistence"]
        if schema_path:
            cmd.extend(["--json-schema", Path(schema_path).read_text(encoding="utf-8")])
        result = subprocess.run(
            cmd,
            input=prompt_text,
            capture_output=True,
            text=True,
            timeout=300,
            env={**os.environ},
        )
        if result.returncode != 0 or not result.stdout.strip():
            message = result.stderr.strip() or result.stdout.strip() or "empty response"
            raise RuntimeError(message)
        return result.stdout.strip(), ""

    if runner == "codex":
        output_file = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as handle:
                output_file = handle.name
            result = subprocess.run(
                [
                    "codex",
                    "exec",
                    "--skip-git-repo-check",
                    "--sandbox",
                    "read-only",
                    "--ephemeral",
                    "--output-last-message",
                    output_file,
                    *(["--output-schema", schema_path] if schema_path else []),
                    "-",
                ],
                input=prompt_text,
                capture_output=True,
                text=True,
                timeout=420,
                env={**os.environ},
                cwd=str(Path.cwd()),
            )
            output_text = Path(output_file).read_text(encoding="utf-8").strip() if output_file and Path(output_file).exists() else ""
            if result.returncode != 0 or not output_text:
                message = result.stderr.strip() or result.stdout.strip() or output_text or "empty response"
                raise RuntimeError(message)
            return output_text, result.stderr.strip()
        finally:
            if output_file:
                Path(output_file).unlink(missing_ok=True)

    raise RuntimeError(f"Unknown merge runner: {runner}")


def _format_structured_transparency(report: dict | str | None) -> str:
    if isinstance(report, str):
        return report
    if not isinstance(report, dict):
        return ""
    sections = [
        ("APPLIED", report.get("applied") or []),
        ("UNCERTAIN", report.get("uncertain") or []),
        ("PRESERVED", report.get("preserved") or []),
    ]
    lines: list[str] = []
    for label, items in sections:
        lines.append(f"{label}:")
        if items:
            lines.extend(f"- {item}" for item in items if str(item).strip())
        else:
            lines.append("- None")
        lines.append("")
    return "\n".join(lines).strip()


def _coerce_structured_merge(full_text: str) -> tuple[str, list, dict, str] | None:
    """Parse JSON/schema merge output into the legacy return shape."""
    try:
        payload = json.loads(full_text)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(payload, dict):
        return None
    transcript = str(payload.get("transcript") or "").strip()
    metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    suggestions = payload.get("suggestions") if isinstance(payload.get("suggestions"), list) else []
    transparency_report = _format_structured_transparency(payload.get("transparency_report"))
    return transcript, [str(item).strip() for item in suggestions if str(item).strip()], metadata, transparency_report


# =============================================================================
# TRANSCRIPTION ENGINE: ASSEMBLYAI
# =============================================================================

def transcribe_assemblyai(audio_path: str, speaker_labels: bool = True, context_bias: list | None = None,
                         num_speakers: int = 2, python_bin: str | None = None,
                         log_path: Path | None = None) -> str | None:
    """
    Transcribe audio using AssemblyAI's Universal-2 (or Universal-3) model.
    
    AssemblyAI is our PRIMARY engine because it excels at:
    - Speaker diarization (who said what)
    - Punctuation and formatting
    - Overall transcript structure
    
    We enhance accuracy by:
    - Setting speech_model to "best" (latest Universal-3 model)
    - Enabling word_boost with our dictionary terms
    - Setting boost_param to "high" for maximum bias effect
    - Forcing language_code to "en" to prevent misdetection
    - Enabling auto_highlights for key phrase extraction
    - Enabling entity_detection for names/places/organizations
    - Setting speakers_expected hint for better diarization
    
    Args:
        audio_path: Path to the audio file
        speaker_labels: Whether to enable speaker diarization
        context_bias: List of terms to boost recognition for
        
    Returns:
        str: The transcript text, or None if failed
    """
    if not resolve_key("ASSEMBLYAI_API_KEY"):
        print("⚠️  ASSEMBLYAI_API_KEY not set. Skipping AssemblyAI.")
        return None
    
    # Build status message
    diarization_note = " + speaker diarization" if speaker_labels else ""
    bias_note = f" + {len(context_bias)} boost terms" if context_bias else ""
    print(f"🌐 Running AssemblyAI Universal-3 Pro (all features{diarization_note}{bias_note})...")

    script = f'''
import assemblyai as aai
import os, sys, json

aai.settings.api_key = os.environ["ASSEMBLYAI_API_KEY"]
transcriber = aai.Transcriber()

boost_env = os.environ.get("ST_BOOST_TERMS")
boost_terms = json.loads(boost_env) if boost_env and boost_env != "None" else None

config = aai.TranscriptionConfig(
    speech_models=["universal-3-pro"],
    speaker_labels={speaker_labels},
    speakers_expected={num_speakers},
    language_detection=True,
    keyterms_prompt=boost_terms,
    punctuate=True,
    format_text=True,
    # Intelligence features (all enabled for maximum richness)
    auto_highlights=True,          # Key phrases and topics
    entity_detection=True,         # Names, places, organizations
    auto_chapters=False,           # Universal-3 Pro rejects auto_chapters; keep transcript path reliable
    sentiment_analysis=True,       # Per-utterance sentiment (positive/negative/neutral)
    iab_categories=True,           # IAB content category classification
)

audio_file = os.environ["ST_AUDIO_PATH"]
transcript = transcriber.transcribe(audio_file, config)

if transcript.status == aai.TranscriptStatus.error:
    print(f"ERROR: {{transcript.error}}", file=sys.stderr)
    sys.exit(1)

# Build metadata block (chapters, summary, entities, sentiment, IAB categories)
meta = {{}}
if transcript.chapters:
    meta["chapters"] = [
        {{"gist": c.gist, "headline": c.headline, "start_ms": c.start, "end_ms": c.end}}
        for c in transcript.chapters
    ]
if transcript.entities:
    meta["entities"] = [
        {{"text": e.text, "type": str(e.entity_type), "start_ms": e.start, "end_ms": e.end}}
        for e in transcript.entities
    ]
sentiment_results = getattr(transcript, 'sentiment_analysis_results', None) or []
if sentiment_results:
    sentiments = [
        {{"text": s.text, "sentiment": str(s.sentiment), "confidence": s.confidence}}
        for s in sentiment_results
    ]
    meta["sentiment_summary"] = {{
        "positive": sum(1 for s in sentiments if "POSITIVE" in s["sentiment"]),
        "negative": sum(1 for s in sentiments if "NEGATIVE" in s["sentiment"]),
        "neutral":  sum(1 for s in sentiments if "NEUTRAL"  in s["sentiment"]),
    }}
iab_result = getattr(transcript, 'iab_categories_result', None)
iab_summary = getattr(iab_result, 'summary', None) if iab_result else None
if iab_summary:
    meta["iab_categories"] = [
        {{"label": k, "relevance": round(v, 3)}}
        for k, v in sorted(
            iab_summary.items(),
            key=lambda x: x[1], reverse=True
        )[:5]
    ]

# Build transcript text with speaker labels
if {speaker_labels} and transcript.utterances:
    lines = []
    current_speaker = None
    for utterance in transcript.utterances:
        if utterance.speaker != current_speaker:
            current_speaker = utterance.speaker
            lines.append(f"\\n**Speaker {{utterance.speaker}}:** {{utterance.text}}")
        else:
            lines.append(utterance.text)
    text = "\\n".join(lines).strip()
else:
    text = transcript.text or ""

# Output as JSON so caller can extract both transcript and metadata
print(json.dumps({{"text": text, "assemblyai_meta": meta}}))
'''

    # Pass sensitive values via environment variables, not string interpolation
    sub_env = {**os.environ, "ASSEMBLYAI_API_KEY": resolve_key("ASSEMBLYAI_API_KEY"), "ST_AUDIO_PATH": audio_path}
    if context_bias:
        sub_env["ST_BOOST_TERMS"] = json.dumps(context_bias)

    try:
        # Run with 60-minute timeout (long audio files can take a while)
        result = subprocess.run(
            [python_bin or str(VENV_PYTHON), "-c", script],
            capture_output=True,
            text=True,
            timeout=3600,
            env=sub_env
        )
        if log_path:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text(
                f"cmd_python={python_bin or str(VENV_PYTHON)}\nreturncode={result.returncode}\n\n[stdout]\n{result.stdout}\n\n[stderr]\n{result.stderr}\n",
                encoding="utf-8",
            )
        
        if result.returncode != 0:
            err = result.stderr or result.stdout
            print(f"   ❌ Error: {err}")
            return None

        raw = result.stdout.strip()
        asm_meta: dict = {}
        try:
            parsed = json.loads(raw)
            text = parsed.get("text", "")
            asm_meta = parsed.get("assemblyai_meta", {})
        except (json.JSONDecodeError, ValueError):
            text = raw
        print(f"   ✅ Complete ({len(text)} chars)")
        if asm_meta.get("chapters"):
            print(f"      📑 {len(asm_meta['chapters'])} chapters detected")
        if asm_meta.get("entities"):
            print(f"      🏷  {len(asm_meta['entities'])} entities detected")
        if asm_meta.get("iab_categories"):
            print(f"      🗂  IAB categories classified")
        return text or None

    except subprocess.TimeoutExpired:
        print("   ❌ Timeout (60 min)")
        return None
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return None


# =============================================================================
# TRANSCRIPTION ENGINE: MISTRAL VOXTRAL 2
# =============================================================================

def transcribe_mistral(audio_path: str, context_bias: list | None = None,
                       python_bin: str | None = None, log_path: Path | None = None) -> str | None:
    """
    Transcribe audio using Mistral's Voxtral 2 model.
    
    Mistral is one of the default engines because it excels at:
    - Word-level accuracy (often catches words AssemblyAI misses)
    - Technical vocabulary
    - Names and proper nouns
    
    We use voxtral-mini-latest which points to the optimized voxtral-mini-2602
    model designed for high-accuracy batch transcription (not real-time).
    
    Args:
        audio_path: Path to the audio file
        context_bias: List of terms to bias recognition toward
        
    Returns:
        str: The transcript text, or None if failed
    """
    if not resolve_key("MISTRAL_API_KEY"):
        print("⚠️  MISTRAL_API_KEY not set. Skipping Mistral.")
        return None

    valid_bias = [
        term.strip()
        for term in (context_bias or [])
        if isinstance(term, str) and term.strip() and " " not in term and "," not in term
    ][:100]
    print(f"🌊 Running Mistral Voxtral with {len(valid_bias)} single-token context terms...")

    script = f'''
import json, os, sys, time
_RETRYABLE = {repr(HTTP_RETRYABLE_SIGNALS)}
_NON_RETRYABLE = {repr(HTTP_NON_RETRYABLE_SIGNALS)}
BACKOFF = {repr(HTTP_BACKOFF_DELAYS_S)}
try:
    from mistralai import Mistral
    from mistralai.models import File

    content_type_map = {
        "m4a": "audio/m4a", "mp3": "audio/mpeg", "wav": "audio/wav",
        "ogg": "audio/ogg", "flac": "audio/flac", "webm": "audio/webm",
        "qta": "audio/quicktime", "caf": "audio/x-caf", "aif": "audio/aiff",
        "wma": "audio/x-ms-wma",
    }
    audio_file = os.environ["ST_AUDIO_PATH"]
    bias_terms = json.loads(os.environ.get("ST_BIAS_TERMS", "[]"))
    model = os.environ.get("ST_MISTRAL_MODEL", "voxtral-mini-latest")
    client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])
    ext = os.path.splitext(audio_file)[1].lstrip(".").lower()

    response = None
    last_err = None
    for attempt in range(3):
        try:
            with open(audio_file, "rb") as handle:
                file_obj = File(
                    fileName=os.path.basename(audio_file),
                    content=handle,
                    content_type=content_type_map.get(ext, "audio/m4a"),
                )
                response = client.audio.transcriptions.complete(
                    model=model,
                    file=file_obj,
                    diarize=True,
                    timestamp_granularities=["segment"],
                    context_bias=bias_terms or None,
                )
            break
        except Exception as e:
            last_err = str(e)
            err_lower = last_err.lower()
            if any(s in err_lower for s in _NON_RETRYABLE):
                raise
            if any(s in err_lower for s in _RETRYABLE) and attempt < 2:
                delay = BACKOFF[attempt]
                print(f"Mistral transient error (attempt {attempt+1}/3), retrying in {delay}s: {last_err[:120]}", file=sys.stderr)
                time.sleep(delay)
                continue
            raise

    text = getattr(response, "text", None)
    if text is None and isinstance(response, dict):
        text = response.get("text")
    if text is None:
        text = str(response)
    print(json.dumps({"text": text, "metadata": {"model": model}}))
except Exception as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(1)
'''

    sub_env = {
        **os.environ,
        "MISTRAL_API_KEY": resolve_key("MISTRAL_API_KEY"),
        "ST_AUDIO_PATH": audio_path,
        "ST_BIAS_TERMS": json.dumps(valid_bias),
    }
    return run_engine_text(script, sub_env, "Mistral Voxtral", python_bin=python_bin, log_path=log_path)


# =============================================================================
# ADDITIONAL TRANSCRIPTION ENGINES
# =============================================================================

# Engine: ElevenLabs Scribe v2

# ElevenLabs Scribe v2 STT pricing (credits per minute, observed empirically
# from a 58:43 file requiring 4,698 credits per the API's own error message).
ELEVENLABS_STT_CREDITS_PER_MINUTE = 80.0
ELEVENLABS_CREDITS_CACHE = CONFIG_DIR / "elevenlabs-credits.json"
_ELEVENLABS_QUOTA_RE = re.compile(
    r"You have\s+([\d,]+)\s+credits remaining,\s*while\s+([\d,]+)\s+credits are required",
    re.IGNORECASE,
)


def _load_elevenlabs_credits_cache() -> dict | None:
    """Read the last-known {credits_remaining, credits_limit, recorded_at}.

    Returns None if the cache doesn't exist or can't be read; callers fail open.
    """
    if not ELEVENLABS_CREDITS_CACHE.exists():
        return None
    try:
        return json.loads(ELEVENLABS_CREDITS_CACHE.read_text())
    except Exception:
        return None


def _save_elevenlabs_credits_cache(remaining: int, required: int | None = None) -> None:
    """Persist a fresh credits-remaining datapoint, gleaned from a quota_exceeded error."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        ELEVENLABS_CREDITS_CACHE.write_text(json.dumps({
            "credits_remaining": remaining,
            "last_request_required": required,
            "recorded_at": datetime.now().isoformat(),
            "source": "quota_exceeded_error",
        }, indent=2))
    except Exception:
        pass  # Cache is best-effort; never block a run


def _parse_elevenlabs_quota_error(error_text: str) -> tuple[int, int] | None:
    """Extract (remaining, required) from an ElevenLabs quota_exceeded error string."""
    if not error_text:
        return None
    match = _ELEVENLABS_QUOTA_RE.search(error_text)
    if not match:
        return None
    try:
        remaining = int(match.group(1).replace(",", ""))
        required = int(match.group(2).replace(",", ""))
        return remaining, required
    except (TypeError, ValueError):
        return None


def _check_elevenlabs_quota(key: str, audio_path: str, python_bin: str | None = None) -> tuple[bool, str]:
    """Pre-flight: refuse to start a Scribe v2 run if cached credits are insufficient.

    Two-stage check:
    1. Duration-based STT estimate against the cached `credits_remaining` from the
       last `quota_exceeded` error. If we know the account is short, fail fast and
       cheap before burning the other engines' parallel runs.
    2. TTS character pool via client.user.get() (different pool from STT but a
       useful "is this account totally cooked" signal). Catches invalid/expired
       keys, fully depleted TTS allowances, and basic API access failures.

    Returns (sufficient, message). Fails open if neither signal is conclusive —
    the actual transcribe call still parses any quota_exceeded error and updates
    the cache, so we self-heal on the next run.
    """
    # Stage 1: cached-credits check based on audio duration
    try:
        from common import get_audio_duration
        duration_s = get_audio_duration(audio_path)
        if duration_s and duration_s > 0:
            estimated_required = math.ceil(duration_s * ELEVENLABS_STT_CREDITS_PER_MINUTE / 60.0)
            cache = _load_elevenlabs_credits_cache()
            if cache and isinstance(cache.get("credits_remaining"), int):
                cached_remaining = int(cache["credits_remaining"])
                if cached_remaining < estimated_required:
                    return False, (
                        f"ElevenLabs: cached credits insufficient — "
                        f"{cached_remaining:,} remaining, ~{estimated_required:,} needed for "
                        f"{duration_s/60:.1f}-min file (cache from {cache.get('recorded_at', 'unknown')}). "
                        f"Top up at elevenlabs.io or use --engines without scribe-v2."
                    )
    except Exception:
        pass  # Audio duration unavailable; fall through to TTS check

    script = '''
import sys, json, os
try:
    try:
        from elevenlabs.client import ElevenLabs
    except Exception:
        from elevenlabs import ElevenLabs
    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    user = client.user.get()
    sub = getattr(user, "subscription", None)
    if sub is None and isinstance(user, dict):
        sub = user.get("subscription", {})
    info = {}
    for f in ["character_count", "character_limit", "status", "tier"]:
        val = getattr(sub, f, None)
        if val is None and isinstance(sub, dict):
            val = sub.get(f)
        if val is not None:
            info[f] = val
    print(json.dumps({"ok": True, "info": info}))
except Exception as e:
    err = str(e)
    print(json.dumps({"ok": False, "error": err,
                      "quota_exhausted": any(kw in err.lower() for kw in
                                             ["quota", "quota_exceeded", "insufficient"])}))
    sys.exit(1)
'''
    try:
        result = subprocess.run(
            [python_bin or str(VENV_PYTHON), "-c", script],
            capture_output=True, text=True, timeout=10,
            env={**os.environ, "ELEVENLABS_API_KEY": key},
        )
        try:
            data = json.loads(result.stdout.strip())
        except Exception:
            return True, "quota check failed — proceeding"
        if result.returncode != 0 or not data.get("ok"):
            err = data.get("error", "")
            if data.get("quota_exhausted") or "quota" in err.lower():
                return False, f"ElevenLabs: quota exhausted — {err[:200]}"
            return (True, "quota check failed — proceeding") if result.returncode != 0 \
                else (True, f"quota check skipped: {err[:80]}")
        info = data.get("info", {})
        limit = info.get("character_limit")
        used = info.get("character_count")
        if limit is not None and used is not None and limit - used <= 0:
            return False, f"ElevenLabs: character quota exhausted ({used:,}/{limit:,} used)"
        return True, "quota OK"
    except Exception as e:
        return True, f"quota check skipped: {e}"


def transcribe_elevenlabs(audio_path: str, context_bias: list | None = None,
                          python_bin: str | None = None, log_path: Path | None = None) -> str | None:
    key = resolve_key("ELEVENLABS_API_KEY") or ""
    if not key:
        print("⚠️  ELEVENLABS_API_KEY not set. Skipping ElevenLabs.", file=sys.stderr)
        return None
    quota_ok, quota_msg = _check_elevenlabs_quota(key, audio_path, python_bin)
    if not quota_ok:
        print(f"⚠️  Skipping ElevenLabs Scribe v2: {quota_msg}", file=sys.stderr)
        return None
    if quota_msg not in ("quota OK",):
        print(f"  ElevenLabs: {quota_msg}", file=sys.stderr)
    # ElevenLabs: max 4 spaces per keyterm (5+ word phrases rejected by API)
    valid_keyterms = [t for t in (context_bias or []) if isinstance(t, str) and t.count(' ') <= 4][:100]
    keyterms_json = json.dumps(valid_keyterms)
    script = f'''
import json, os, sys, warnings
warnings.filterwarnings("ignore")
try:
    try:
        from elevenlabs.client import ElevenLabs
    except Exception:
        from elevenlabs import ElevenLabs
    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    keyterms = json.loads(os.environ.get("ST_KEYTERMS", "[]"))
    with open(os.environ["ST_AUDIO_PATH"], "rb") as f:
        kwargs = dict(
            model_id="scribe_v2",
            language_code="en",
            diarize=True,
            tag_audio_events=True,
            timestamps_granularity="word",
            keyterms=keyterms if keyterms else None,
        )
        try:
            result = client.speech_to_text.convert(file=f, **kwargs)
        except TypeError:
            f.seek(0)
            result = client.speech_to_text.convert(audio=f, **kwargs)
    text = result.text if hasattr(result, "text") else str(result)
    # Build speaker-labelled text from word-level diarization
    if hasattr(result, "words") and result.words:
        lines, cur_spk, cur_seg = [], None, None
        for w in result.words:
            spk = getattr(w, "speaker_id", None) or getattr(w, "speaker", None)
            wtext = getattr(w, "text", "")
            if spk and spk != cur_spk:
                if cur_seg:
                    lines.append(f"**Speaker {{cur_spk}}:** {{cur_seg}}")
                cur_spk, cur_seg = spk, wtext
            elif cur_seg is not None:
                cur_seg += " " + wtext
            else:
                cur_seg = wtext
        if cur_seg:
            lines.append(f"**Speaker {{cur_spk}}:** {{cur_seg}}")
        if lines:
            text = "\\n".join(lines)
    print(json.dumps({{"text": text}}))
except Exception as e:
    print(json.dumps({{"error": str(e)}}))
    sys.exit(1)
'''
    env = {**os.environ, "ELEVENLABS_API_KEY": key, "ST_AUDIO_PATH": audio_path,
           "ST_KEYTERMS": keyterms_json}
    text = run_engine_text(script, env, "ElevenLabs Scribe v2", python_bin=python_bin, log_path=log_path)
    # If the engine failed due to quota_exceeded, scrape the credits-remaining
    # and credits-required from the engine log and update the cache so the next
    # pre-flight has accurate data without needing a billing API.
    if not text and log_path is not None and log_path.exists():
        try:
            log_text = log_path.read_text(encoding="utf-8", errors="replace")
            parsed = _parse_elevenlabs_quota_error(log_text)
            if parsed is not None:
                remaining, required = parsed
                _save_elevenlabs_credits_cache(remaining, required)
                print(
                    f"  ElevenLabs: cached new credit balance — "
                    f"{remaining:,} remaining (last request needed {required:,}).",
                    file=sys.stderr,
                )
        except Exception:
            pass
    return text


# Engine: Google Gemini audio input
def transcribe_gemini_audio(audio_path: str, context_bias: list | None = None,
                            python_bin: str | None = None, log_path: Path | None = None) -> str | None:
    key = resolve_key("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY", "")
    if not key:
        print("⚠️  GOOGLE_API_KEY not set. Skipping Gemini audio.", file=sys.stderr)
        return None
    script = '''
import json, os, sys
try:
    from google import genai
    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
    uploaded = client.files.upload(file=os.environ["ST_AUDIO_PATH"])
    prompt = """Transcribe this audio verbatim. Output ONLY the transcript.
For multiple speakers use: **Speaker N:** text (on new lines).
Preserve all spoken words exactly."""
    model = os.environ.get("ST_GEMINI_MODEL", "gemini-2.5-flash")
    response = client.models.generate_content(model=model, contents=[prompt, uploaded])
    text = response.text if hasattr(response, "text") else str(response)
    print(json.dumps({"text": text}))
except Exception as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(1)
'''
    env = {**os.environ, "GOOGLE_API_KEY": key, "ST_AUDIO_PATH": audio_path}
    return run_engine_text(script, env, "Gemini audio", python_bin=python_bin, log_path=log_path)


# Engine: OpenAI GPT-4o Transcribe
def transcribe_gpt4o(audio_path: str, context_bias: list | None = None,
                     python_bin: str | None = None, log_path: Path | None = None) -> str | None:
    key = resolve_key("OPENAI_API_KEY") or ""
    if not key:
        print("⚠️  OPENAI_API_KEY not set. Skipping GPT-4o Transcribe.", file=sys.stderr)
        return None
    script = '''
import json, os, sys
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    with open(os.environ["ST_AUDIO_PATH"], "rb") as f:
        prompt = os.environ.get("ST_OPENAI_PROMPT") or None
        resp = client.audio.transcriptions.create(
            model="gpt-4o-transcribe", file=f, language="en", response_format="json", prompt=prompt)
    print(json.dumps({"text": resp.text if hasattr(resp, "text") else str(resp)}))
except Exception as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(1)
'''
    chunks = chunk_audio(audio_path)
    if len(chunks) == 1:
        env = {**os.environ, "OPENAI_API_KEY": key, "ST_AUDIO_PATH": chunks[0]}
        return run_engine_text(script, env, "GPT-4o Transcribe", python_bin=python_bin, log_path=log_path)
    # Multi-chunk: concatenate
    parts: list[str] = []
    for i, chunk in enumerate(chunks):
        print(f"   GPT-4o chunk {i+1}/{len(chunks)}...", file=sys.stderr)
        env = {**os.environ, "OPENAI_API_KEY": key, "ST_AUDIO_PATH": chunk}
        t = run_engine_text(script, env, f"GPT-4o chunk {i+1}", python_bin=python_bin, log_path=log_path)
        if t:
            parts.append(t)
    return " ".join(parts) or None


# Engine: OpenAI GPT-4o Mini Transcribe
def transcribe_gpt4o_mini(audio_path: str, context_bias: list | None = None,
                          python_bin: str | None = None, log_path: Path | None = None) -> str | None:
    key = resolve_key("OPENAI_API_KEY") or ""
    if not key:
        print("⚠️  OPENAI_API_KEY not set. Skipping GPT-4o Mini Transcribe.", file=sys.stderr)
        return None
    script = '''
import json, os, sys
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    with open(os.environ["ST_AUDIO_PATH"], "rb") as f:
        prompt = os.environ.get("ST_OPENAI_PROMPT") or None
        resp = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe", file=f, language="en", response_format="json", prompt=prompt)
    print(json.dumps({"text": resp.text if hasattr(resp, "text") else str(resp)}))
except Exception as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(1)
'''
    chunks = chunk_audio(audio_path)
    if len(chunks) == 1:
        env = {**os.environ, "OPENAI_API_KEY": key, "ST_AUDIO_PATH": chunks[0]}
        return run_engine_text(script, env, "GPT-4o Mini Transcribe", python_bin=python_bin, log_path=log_path)
    parts: list[str] = []
    for i, chunk in enumerate(chunks):
        env = {**os.environ, "OPENAI_API_KEY": key, "ST_AUDIO_PATH": chunk}
        t = run_engine_text(script, env, f"GPT-4o Mini chunk {i+1}", python_bin=python_bin, log_path=log_path)
        if t:
            parts.append(t)
    return " ".join(parts) or None


# Engine: Voxtral Mini Realtime (local, mlx-audio, Apple Silicon)
def transcribe_voxtral_local(audio_path: str, context_bias: list | None = None,
                             python_bin: str | None = None, log_path: Path | None = None) -> str | None:
    wav_path = convert_16khz_mono(audio_path)
    script = '''
import json, os, sys
try:
    from mlx_audio.stt.utils import load
    model = load("mlx-community/Voxtral-Mini-4B-Realtime-2602-4bit")
    result = model.generate(os.environ["ST_AUDIO_PATH"], verbose=False)
    text = result.text if hasattr(result, "text") else str(result)
    print(json.dumps({"text": text}))
except Exception as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(1)
'''
    env = {**os.environ, "ST_AUDIO_PATH": wav_path}
    return run_engine_text(script, env, "Voxtral Mini (local)", timeout=ENGINE_TIMEOUTS["voxtral-mini-local"],
                           python_bin=python_bin, log_path=log_path)


# Engine: Cohere Transcribe (local, PyTorch + MPS / MLX)
def transcribe_cohere(audio_path: str, context_bias: list | None = None,
                      python_bin: str | None = None, log_path: Path | None = None) -> str | None:
    wav_path = convert_16khz_mono(audio_path)
    script = '''
import json, os, sys
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
try:
    # Try MLX community version first (faster on Apple Silicon)
    try:
        from mlx_audio.stt.utils import load
        model = load("mlx-community/cohere-transcribe-03-2026-mlx-8bit")
        result = model.generate(os.environ["ST_AUDIO_PATH"], verbose=False)
        text = result.text if hasattr(result, "text") else str(result)
        print(json.dumps({"text": text}))
        sys.exit(0)
    except Exception:
        pass
    import torch, soundfile as sf
    from transformers import AutoProcessor, CohereAsrForConditionalGeneration
    # Patch parakeet subsampling shape bug present in transformers <= 5.5.x:
    # transpose(1,2) + shape[2] reads the post-transpose dims, putting time at dim 3.
    # permute(0,3,1,2) correctly brings time to dim 1 before flattening channels*height.
    try:
        import torch.nn as nn
        from transformers.models.parakeet import modeling_parakeet as _pm
        def _fixed_subsampling_forward(self, input_features, attention_mask=None):
            hs = input_features.unsqueeze(1)
            current_lengths = attention_mask.sum(-1) if attention_mask is not None else None
            for layer in self.layers:
                hs = layer(hs)
                if isinstance(layer, nn.Conv2d) and attention_mask is not None:
                    current_lengths = self._get_output_length(current_lengths, layer)
                    seq_len = hs.shape[2]
                    mask = torch.arange(seq_len, device=attention_mask.device) < current_lengths[:, None]
                    hs *= mask[:, None, :, None]
            b, c, h, t = hs.shape
            hs = hs.permute(0, 3, 1, 2).reshape(b, t, -1)
            return self.linear(hs)
        _pm.ParakeetEncoderSubsamplingConv2D.forward = _fixed_subsampling_forward
    except Exception:
        pass  # if transformers fixes the bug, this no-ops gracefully
    model_id = "CohereLabs/cohere-transcribe-03-2026"
    processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
    model = CohereAsrForConditionalGeneration.from_pretrained(
        model_id, trust_remote_code=True, device_map="auto",
        torch_dtype=torch.float32,  # bfloat16 default crashes on MPS
    )
    audio, sr = sf.read(os.environ["ST_AUDIO_PATH"])
    # config.max_position_embeddings=5000 limits encoder output to ~400s at 12.5fps.
    # Split into 5-minute chunks so each stays safely under the limit.
    CHUNK_S = 300
    chunk_size = CHUNK_S * sr
    audio_chunks = [audio[i:i + chunk_size] for i in range(0, len(audio), chunk_size)]
    texts = []
    for chunk in audio_chunks:
        chunk_duration_s = len(chunk) / sr
        # Scale token budget: ~150wpm * 1.3 tok/word, min 512, max 8192
        max_tokens = max(512, min(8192, int(chunk_duration_s / 60 * 150 * 1.3) + 256))
        inputs = processor(audio=chunk, sampling_rate=sr, return_tensors="pt", language="en")
        audio_chunk_index = inputs.get("audio_chunk_index")  # keep in inputs for generate()
        inputs.pop("length", None)  # not a generate() kwarg (added in transformers 5.5)
        inputs.to(model.device)
        outputs = model.generate(**inputs, max_new_tokens=max_tokens,
                                  repetition_penalty=1.2)  # prevent stuck loops on hard audio
        result = processor.decode(outputs, skip_special_tokens=True,
                                  audio_chunk_index=audio_chunk_index, language="en")
        chunk_text = result[0] if isinstance(result, list) else result
        texts.append(chunk_text.strip())
    text = " ".join(t for t in texts if t)
    print(json.dumps({"text": text}))
except Exception as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(1)
'''
    hf_token = resolve_key("HF_TOKEN") or ""
    env = {**os.environ, "ST_AUDIO_PATH": wav_path,
           "PYTORCH_ENABLE_MPS_FALLBACK": "1",
           "HF_TOKEN": hf_token,
           "HUGGING_FACE_HUB_TOKEN": hf_token,
           "HUGGINGFACE_TOKEN": hf_token}
    return run_engine_text(script, env, "Cohere Transcribe (local)", timeout=ENGINE_TIMEOUTS["cohere-transcribe"],
                           python_bin=python_bin, log_path=log_path)


# Engine dispatch table — keys match ensemble.py MODELS dict for consistency
ENGINES: dict[str, tuple[str, object]] = {
    "cohere-transcribe":    ("Cohere Transcribe (local)",  transcribe_cohere),
    "voxtral-small":        ("Mistral Voxtral Small",      transcribe_mistral),
    "scribe-v2":            ("ElevenLabs Scribe v2",       transcribe_elevenlabs),
    "assemblyai-u3-pro":    ("AssemblyAI Universal-3 Pro", transcribe_assemblyai),
    "gemini-3-pro":         ("Gemini audio (configurable)", transcribe_gemini_audio),
    "gpt4o-transcribe":     ("GPT-4o Transcribe",          transcribe_gpt4o),
    "gpt4o-mini-transcribe":("GPT-4o Mini Transcribe",     transcribe_gpt4o_mini),
    "voxtral-mini-local":   ("Voxtral Mini (local)",       transcribe_voxtral_local),
}

ENGINE_ALIASES = {
    "assemblyai": "assemblyai-u3-pro",
    "voxtral": "voxtral-small",
    "mistral": "voxtral-small",
    "elevenlabs": "scribe-v2",
    "scribe": "scribe-v2",
    "gemini": "gemini-3-pro",
    "openai": "gpt4o-transcribe",
    "gpt4o": "gpt4o-transcribe",
    "gpt4o-mini": "gpt4o-mini-transcribe",
    "voxtral-local": "voxtral-mini-local",
    "cohere": "cohere-transcribe",
}

def resolve_engine(name: str) -> str | None:
    """Resolve an engine name or alias to its canonical ID."""
    name = name.strip().lower()
    if name in ENGINES:
        return name
    return ENGINE_ALIASES.get(name)


# =============================================================================
# LLM MERGE PHASE
# =============================================================================

def merge_with_llm(
    transcripts: dict,
    dictionary: dict,
    speakers: list | None = None,
    mode: str = "merge",
) -> tuple[str | None, list, dict, str, dict]:
    """
    Merge (or review-and-correct) transcripts using Claude Code headless.

    Modes:
    - "merge": Multi-engine merge (standard audio path). LLM resolves disagreements
               across all engines, weighted by each engine's known strengths.
    - "fix":   Single-source review. LLM corrects an existing transcript against
               the dictionary and its knowledge base (--fix-transcript path).

    The LLM outputs FOUR sections delimited by ---SPLIT---:
      1. Metadata JSON  (title, speakers, summary, date_mentioned)
      2. Corrected transcript (Markdown)
      3. Transparency report  (APPLIED / UNCERTAIN / PRESERVED)
      4. Dictionary suggestions  (one "Wrong → Right (context)" per line)

    Conservative correction policy:
    - Do NOT correct unverifiable product names, version numbers, or model numbers.
    - Do NOT "fix" intentional casual speech (gonna, wanna, yeah).
    - If a word is ambiguous, list it in UNCERTAIN — do not guess.
    - Items left intentionally unchanged go in PRESERVED.

    Args:
        transcripts: Dict mapping source name to transcript text
        dictionary: The loaded (and context-merged) correction dictionary
        speakers: Optional list of known speaker names
        mode: "merge" (multi-engine) or "fix" (single-source correction)

    Returns:
        tuple: (transcript, suggestions, metadata, transparency_report, merge_info)
    """
    # Build transcript sections for the prompt
    transcript_sections = []
    for name, text in transcripts.items():
        if text:
            transcript_sections.append(f"### {name}\n{text}")
    
    if not transcript_sections:
        return None, [], {}, "", {"runner": None, "fallback_reason": None}
    
    # Build dictionary context section
    # We include ALL dictionary entries so the LLM can apply them
    dict_context = ""
    if dictionary.get('corrections'):
        corrections_list = list(dictionary['corrections'].items())[:200]
        dict_context = "\n\n## Known Corrections (apply these strictly):\n" + "\n".join(f"- {k} → {v}" for k, v in corrections_list)
    
    # Add known entities (correct spellings to preserve)
    if dictionary.get('entities'):
        dict_context += "\n\n## Known Entities (preserve exact spelling):\n" + ", ".join(dictionary['entities'][:50])
    
    # Add notes for context
    if dictionary.get('notes'):
        dict_context += "\n\n## Important Notes:\n" + "\n".join(f"- {note}" for note in dictionary['notes'])
    
    # Build speaker identification context
    speaker_context = ""
    
    # Get speaker hints from dictionary if not provided explicitly
    known_speakers = dictionary.get('speakers', {})
    
    if speakers:
        speaker_context = f"\n\n## Known Speakers in this Recording:\n{', '.join(speakers)}\n\nUse context clues (greetings, names mentioned, topics discussed) to identify which Speaker A/B/C corresponds to which person. Replace generic labels with real names."
        
        # Add topic hints for provided speakers
        speaker_hints = []
        for name in speakers:
            if name in known_speakers:
                info = known_speakers[name]
                topics = info.get('topics', [])
                if topics:
                    speaker_hints.append(f"- {name}: often discusses {', '.join(topics[:3])}")
        if speaker_hints:
            speaker_context += "\n\nSpeaker Topic Hints:\n" + "\n".join(speaker_hints)
    else:
        speaker_context = "\n\n## Speaker Identification:\nAnalyze context clues (greetings like 'Hi Oliver', topics, references) to infer speaker identities. If you can confidently identify speakers, replace 'Speaker A/B/C' with their actual names. If uncertain, keep the generic labels."
        
        # Add all known speaker hints
        if known_speakers:
            speaker_hints = []
            for name, info in known_speakers.items():
                topics = info.get('topics', [])
                if topics:
                    speaker_hints.append(f"- {name}: often discusses {', '.join(topics[:3])}")
            if speaker_hints:
                speaker_context += "\n\nKnown Speaker Profiles:\n" + "\n".join(speaker_hints)
    
    # Build mode-specific task instructions
    if mode == "fix":
        task_instructions = """\
## Your Task

You are reviewing a single existing transcript against the correction dictionary and your knowledge base.

1. **Correct** clear transcription errors using the Known Corrections list and your knowledge.
2. **Be conservative:** Do NOT correct unverifiable product names, version numbers, or model numbers
   (e.g. if the speaker says "iPhone 17" don't change it to a known model — you can't verify it).
   Do NOT "fix" intentional casual speech (gonna, wanna, kinda, yeah).
3. **Identify New Terms:** Proper nouns, names, places, or technical terms that appear correctly
   but are not in the Known Corrections list.

### Reliability guidance:
- Trust your knowledge for clearly wrong spellings of real places/names/organisations.
- When uncertain, preserve the original wording and note it in UNCERTAIN.
"""
    else:
        # Build dynamic engine reliability guidance based on which engines are present
        engine_names = list(transcripts.keys())
        has_assemblyai = any("assemblyai" in k.lower() for k in engine_names)
        has_diarization_engine = has_assemblyai or any("scribe" in k.lower() for k in engine_names)

        # Build per-engine profiles based on which engines are present
        engine_profiles: list[str] = []
        for engine_name in engine_names:
            key = engine_name.lower()
            if "assemblyai" in key:
                engine_profiles.append(
                    f"- **{engine_name}** (AssemblyAI Universal-3 Pro, 3.2% AA-WER): "
                    "Best speaker diarization and speaker turn detection. Provides chapters, "
                    "entity tags, and sentiment metadata. Trust speaker labels and paragraph "
                    "structure from this engine. May miss rare proper nouns."
                )
            elif "scribe" in key or "elevenlabs" in key:
                engine_profiles.append(
                    f"- **{engine_name}** (ElevenLabs Scribe v2, 2.3% AA-WER — #1 cloud accuracy): "
                    "Highest word-level accuracy of all cloud engines. Best at proper nouns and "
                    "technical vocabulary. Trust word choices from this engine when they disagree "
                    "with others. Diarizes but less reliable for speaker turn order."
                )
            elif "cohere" in key:
                engine_profiles.append(
                    f"- **{engine_name}** (Cohere Transcribe, 5.42% HF-WER — #1 open-source): "
                    "Runs locally; no keyterm biasing. Fastest engine (524x real-time). "
                    "Use as a tiebreaker between cloud engines. May stumble on rare proper nouns "
                    "not in training data. Good overall accuracy on common vocabulary."
                )
            elif "voxtral" in key or "mistral" in key:
                engine_profiles.append(
                    f"- **{engine_name}** (Mistral Voxtral, 2.9% AA-WER): "
                    "Strong word accuracy; supports context biasing. Use for word-level verification."
                )
            elif "gemini" in key:
                engine_profiles.append(
                    f"- **{engine_name}** (Google Gemini, 2.9% AA-WER): "
                    "Multimodal; strong on context and technical content."
                )
            elif "gpt" in key or "openai" in key:
                engine_profiles.append(
                    f"- **{engine_name}** (OpenAI GPT-4o Transcribe, ~2.5% WER): "
                    "RL-trained ASR; decorrelated errors from other engines."
                )
            else:
                engine_profiles.append(f"- **{engine_name}**: Independent transcription source.")

        engine_reliability = f"""\
### Engine Profiles (merge guidance):
{chr(10).join(engine_profiles)}

### Merge Strategy:
- Use **AssemblyAI** speaker labels and paragraph structure as the structural scaffold.
- Use **ElevenLabs Scribe** word choices as the primary word-accuracy reference.
- Use **Cohere** (if present) as a tiebreaker when the cloud engines disagree.
- When all engines agree on a word, it is almost certainly correct.
- When engines disagree, prefer the engine profile above that specializes in that dimension."""

        task_instructions = f"""\
## Your Task

You have {len(engine_names)} transcript(s) of the same audio from different engines. Merge them into one accurate transcript.

1. **Merge** transcripts, resolving disagreements intelligently.
2. **Apply** dictionary corrections strictly.
3. **Be conservative:** Do NOT correct unverifiable product names, version numbers, or model numbers.
   Do NOT "fix" intentional casual speech (gonna, wanna, yeah). Preserve speaker voice.
4. **Identify New Terms:** Proper nouns/names/places not in the Known Corrections list.

{engine_reliability}
"""

    prompt = f"""You are an expert transcription editor.
Do not use external tools. Work only from the transcript and dictionary content provided below.

## Source Transcript(s)

{chr(10).join(transcript_sections)}
{dict_context}
{speaker_context}

{task_instructions}

### Conservative Correction Policy (important):
- Do NOT change version numbers, model numbers, or product names you cannot independently verify.
- Do NOT alter intentional casual grammar or filler words that reflect the speaker's voice.
- When genuinely uncertain about the correct form, record the passage in UNCERTAIN — do not guess.
- Items you deliberately leave unchanged (casual speech, unverifiable names) go in PRESERVED.

### Output Contract

If the runtime requests structured JSON output, return exactly this object shape:
{{
  "metadata": {{"title": "...", "speakers": ["..."], "summary": "...", "date_mentioned": "YYYY-MM-DD or unknown"}},
  "transcript": "Corrected/merged Markdown transcript with speaker labels.",
  "transparency_report": {{
    "applied": ["wrong form -> Correct Form (brief context snippet)"],
    "uncertain": ["passage you were not sure about, and why"],
    "preserved": ["what you deliberately left unchanged and why"]
  }},
  "suggestions": ["Wrong -> Right (Context)", "Right (Context)"]
}}

If structured JSON output is not available, output EXACTLY four sections separated by the literal string `---SPLIT---` on its own line:
1. Metadata JSON
2. Corrected/merged Markdown transcript with speaker labels
3. Transparency report with APPLIED, UNCERTAIN, and PRESERVED subsections
4. Dictionary suggestions, one per line

Omit corrections already in the Known Corrections list.
"""

    # Write prompt to temp file (avoids shell escaping issues with long text)
    prompt_file = None
    schema_file = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(prompt)
            prompt_file = f.name
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(MERGE_OUTPUT_SCHEMA, f)
            schema_file = f.name

        with open(prompt_file, "r") as pf:
            prompt_text = pf.read()

        merge_info = {"runner": None, "fallback_reason": None}
        try:
            print("🧠 Merging with Claude Code headless (opus + medium effort)...")
            full_text, _ = _run_merge_runner("claude", prompt_text, schema_file)
            merge_info["runner"] = "claude"
        except Exception as exc:
            error_text = str(exc)
            if shutil.which("codex"):
                print(f"   ⚠️  Claude merge unavailable: {error_text[:200]}", file=sys.stderr)
                print("   ↪ Falling back to Codex headless merge...", file=sys.stderr)
                full_text, _ = _run_merge_runner("codex", prompt_text, schema_file)
                merge_info["runner"] = "codex"
                merge_info["fallback_reason"] = error_text
            else:
                print(f"   ❌ Error: {error_text[:300]}")
                return None, [], {}, "", {"runner": None, "fallback_reason": error_text}

        if full_text.strip():
            full_text = full_text.strip()

            # Parse the structured output.
            # Expected 4-part format: metadata | transcript | transparency_report | suggestions
            # Also handles legacy 3-part (metadata | transcript | suggestions)
            # and 2-part (transcript | suggestions) gracefully.
            metadata: dict = {}
            transcript_text = ""
            transparency_report = ""
            suggestions: list = []

            structured = _coerce_structured_merge(full_text)
            if structured:
                transcript_text, suggestions, metadata, transparency_report = structured
            elif "---SPLIT---" in full_text:
                parts = [p.strip() for p in full_text.split("---SPLIT---") if p.strip()]

                if len(parts) >= 4:
                    # 4-part format (new): metadata, transcript, transparency, suggestions
                    metadata_text = parts[0]
                    transcript_text = parts[1]
                    transparency_report = parts[2]
                    suggestions_text = parts[3]
                elif len(parts) == 3:
                    # 3-part legacy: metadata, transcript, suggestions
                    metadata_text = parts[0]
                    transcript_text = parts[1]
                    suggestions_text = parts[2]
                    transparency_report = ""
                else:
                    # 2-part legacy: transcript, suggestions
                    metadata_text = ""
                    transcript_text = parts[0]
                    suggestions_text = parts[1]
                    transparency_report = ""

                # Parse metadata JSON
                if metadata_text:
                    try:
                        mt = metadata_text
                        if "```json" in mt:
                            mt = mt[mt.find("```json") + 7: mt.find("```", mt.find("```json") + 7)].strip()
                        elif "```" in mt:
                            mt = mt[mt.find("```") + 3: mt.find("```", mt.find("```") + 3)].strip()
                        metadata = json.loads(mt)
                    except (json.JSONDecodeError, ValueError):
                        metadata = {}

                # Parse suggestion lines
                suggestions = [
                    ln.strip()
                    for ln in suggestions_text.split("\n")
                    if ln.strip() and not ln.startswith("#")
                ]
            else:
                # LLM ignored the format — treat whole response as transcript
                transcript_text = full_text
                try:
                    stripped = full_text.strip()
                    if stripped.startswith("{") and stripped.endswith("}"):
                        metadata = json.loads(stripped)
                        transcript_text = ""
                except (json.JSONDecodeError, ValueError):
                    pass

            print(f"   ✅ Merge complete ({len(transcript_text)} chars)")
            print(f"   💡 Found {len(suggestions)} new dictionary candidates")
            print(f"   🤖 Merge runner: {_merge_runner_label(merge_info['runner'])}")
            if transparency_report:
                applied_count = transparency_report.upper().count("->") + transparency_report.upper().count("→")
                print(f"   📋 Transparency report: ~{applied_count} correction(s) applied")
            return transcript_text, suggestions, metadata, transparency_report, merge_info
        else:
            print("   ❌ Error: Empty response")
            return None, [], {}, "", {"runner": None, "fallback_reason": "empty response"}

    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return None, [], {}, "", {"runner": None, "fallback_reason": str(e)}
    finally:
        if prompt_file:
            Path(prompt_file).unlink(missing_ok=True)
        if schema_file:
            Path(schema_file).unlink(missing_ok=True)


# =============================================================================
# TITLE GENERATION
# =============================================================================

def generate_title(text: str) -> str:
    """
    Generate a short, descriptive filename for the transcript.
    
    Uses a fast LLM (Gemini Flash) to analyze the transcript content and
    suggest a 3-6 word title suitable for use as a filename.
    
    Args:
        text: The transcript text (first 1000 chars used)
    Returns:
        str: A filename-safe title (max 50 chars)
    """
    prompt = f"""Generate a short, descriptive filename (3-6 words) for this transcript. 
    Do not include date. Do not include extension. 
    Examples: "Board Meeting Notes", "Interview with Sarah", "Project Alpha Brainstorm".
    
    Transcript: {text[:1000]}..."""
    
    if not resolve_key("GOOGLE_API_KEY"):
        # Fallback: use first 5 words of transcript
        return " ".join(text.split()[:5])

    prompt_file = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(prompt)
            prompt_file = f.name

        # Use Gemini Flash for speed (title generation doesn't need heavy reasoning)
        script = '''
import os
from google import genai
with open(os.environ["ST_PROMPT_FILE"], "r") as f:
    prompt = f.read()
client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
response = client.models.generate_content(
    model="gemini-2.0-flash-exp",
    contents=prompt
)
print(response.text.strip())
'''
        sub_env = {**os.environ, "GOOGLE_API_KEY": resolve_key("GOOGLE_API_KEY"), "ST_PROMPT_FILE": prompt_file}
        result = subprocess.run(
            [str(VENV_PYTHON), "-c", script],
            capture_output=True,
            text=True,
            timeout=30,
            env=sub_env
        )
        if result.returncode == 0 and result.stdout.strip():
            title = result.stdout.strip()
            # Remove any characters that are invalid in filenames
            title = re.sub(r'[<>:"/\\|?*]', '', title)
            return title[:50]
    except Exception:
        pass
    finally:
        if prompt_file:
            Path(prompt_file).unlink(missing_ok=True)
        
    return "Transcript"


# =============================================================================
# OUTPUT MANAGEMENT
# =============================================================================

def append_suggestions(suggestions: list, source_file: str | None = None):
    """
    Append suggested dictionary terms to the suggestions file (JSONL format).
    
    Each suggestion is stored as a JSON object with metadata for easy
    programmatic review and merging into the main dictionary.
    
    Args:
        suggestions: List of suggestion strings (format: "Wrong → Right (Context)")
        source_file: Original audio filename for provenance tracking
    """
    if not suggestions:
        return

    _, suggestions_path = get_dictionary_paths()
    timestamp = datetime.now().isoformat()
    suggestions_path.parent.mkdir(parents=True, exist_ok=True)

    with open(suggestions_path, 'a') as f:
        for item in suggestions:
            # Parse the suggestion format
            entry = {
                "raw": item,
                "timestamp": timestamp,
                "source": source_file,
                "status": "pending"
            }
            
            # Try to parse "wrong → right (context)" format
            arrow = "→" if "→" in item else "->" if "->" in item else None
            if arrow:
                parts = item.split(arrow, 1)
                entry["wrong"] = parts[0].strip()
                right_part = parts[1].strip()
                if "(" in right_part:
                    entry["right"] = right_part.split("(")[0].strip()
                    entry["context"] = right_part.split("(")[1].rstrip(")")
                else:
                    entry["right"] = right_part
            
            f.write(json.dumps(entry) + "\n")
    
    print(f"   📝 Appended {len(suggestions)} suggestions to {suggestions_path.name}")


# =============================================================================
# ENGINE RUN SUMMARY
# =============================================================================

def _print_engine_summary(
    engine_results: dict[str, dict],
    selected_engine_ids: list[str],
    bundle_path: Path | None = None,
) -> None:
    """Print a structured summary of engine outcomes after a transcription run.

    Shows: per-engine success/fail with failure reasons, word counts with outlier
    flags, and a HIGH/MODERATE/LOW confidence label based on successful engine ratio.
    """
    total = len(selected_engine_ids)
    n_ok = sum(1 for r in engine_results.values() if r.get("status") == "complete")

    if total == 0:
        return

    # Confidence label
    ratio = n_ok / total
    if ratio >= 1.0:
        confidence = "HIGH"
        conf_icon = "🟢"
    elif ratio >= 0.75:
        confidence = "MODERATE"
        conf_icon = "🟡"
    else:
        confidence = "LOW"
        conf_icon = "🔴"

    print(f"\n{'─' * 60}", file=sys.stderr)
    print(f"📊 Engine summary  {n_ok}/{total} succeeded  |  confidence: {conf_icon} {confidence}", file=sys.stderr)
    print(f"{'─' * 60}", file=sys.stderr)

    # Per-engine word counts (for outlier detection)
    word_counts: dict[str, int] = {}
    for label, r in engine_results.items():
        text = r.get("text") or ""
        word_counts[label] = len(text.split()) if text else 0

    max_wc = max(word_counts.values()) if word_counts else 0

    for label, r in engine_results.items():
        status = r.get("status", "failed")
        wc = word_counts.get(label, 0)
        if status == "complete":
            outlier = max_wc > 0 and wc < max_wc * 0.10
            outlier_flag = "  ⚠️ word count outlier (<10% of max)" if outlier else ""
            print(f"  ✅ {label}: {wc:,} words{outlier_flag}", file=sys.stderr)
        else:
            reason = r.get("failure_reason") or "no transcript produced"
            print(f"  ❌ {label}: {reason}", file=sys.stderr)

    if bundle_path:
        print(f"\n📦 Agent merge bundle ready", file=sys.stderr)
        print(f"📄 {bundle_path}", file=sys.stderr)

    if confidence == "LOW":
        print(
            f"\n⚠️  LOW confidence: only {n_ok}/{total} engines succeeded."
            " Merged transcript may have unresolved word-accuracy gaps."
            " Consider re-running with --resume once upstream errors are resolved.",
            file=sys.stderr,
        )
    print(f"{'─' * 60}\n", file=sys.stderr)


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """
    Main entry point. Parses arguments and orchestrates the pipeline.
    
    Pipeline stages:
    1. Load dictionary
    2. Run default engines: Cohere local, Mistral Voxtral, ElevenLabs Scribe v2, AssemblyAI Universal-3 Pro
    3. Merge transcripts with headless Claude (Codex fallback on rate limits)
    5. Save suggestions for dictionary learning
    6. Generate title if not provided
    7. Create output folder and save files
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Smart Transcribe with LLM Merge",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 smart-transcribe.py recording.m4a
  python3 smart-transcribe.py recording.m4a --merge-mode manual
  python3 smart-transcribe.py recording.m4a -d "Interview with Beth" --context bcbs-vt
  python3 smart-transcribe.py recording.m4a --no-diarization --review
  python3 smart-transcribe.py --fix-transcript transcript.srt --context bcbs-vt
  python3 smart-transcribe.py --context          (list saved contexts)
        """
    )

    # Input: positional audio file OR --fix-transcript (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument("audio_file", nargs="?", help="Audio file to transcribe")
    input_group.add_argument(
        "--fix-transcript",
        metavar="FILE",
        help="Correct an existing transcript file (.srt, .vtt, .txt, .md) — skip transcription engines",
    )

    parser.add_argument("-d", "--description", help="Description for output folder (auto-generated if omitted)")
    parser.add_argument("--no-diarization", action="store_true", help="Disable speaker diarization")
    parser.add_argument("--speakers", help="Comma-separated speaker names (e.g. 'Oliver,Beth')")
    parser.add_argument("--num-speakers", type=int, default=2, help="Expected number of speakers (default: 2)")
    parser.add_argument("--dict", help="Path to dictionary JSON file (default: user dictionary)")
    parser.add_argument(
        "--context",
        metavar="NAME",
        nargs="?",
        const="",  # --context with no value → list mode
        help="Named context overlay (e.g. bcbs-vt). Omit NAME to list saved contexts.",
    )
    parser.add_argument(
        "--model",
        choices=["claude"],
        default="claude",
        help="LLM for merging: claude (default, Claude Code headless opus + medium effort; Codex headless fallback on rate limits)",
    )
    parser.add_argument(
        "--engines",
        metavar="E1,E2,...",
        default=",".join(DEFAULT_ENGINES),
        help=(
            "Comma-separated engine IDs (default: cohere-transcribe,voxtral-small,scribe-v2,assemblyai-u3-pro). "
            f"Available: {', '.join(ENGINES)}"
        ),
    )
    parser.add_argument("--list-engines", action="store_true", help="List available engine IDs and exit")
    parser.add_argument(
        "--output",
        "--output-dir",
        dest="output",
        metavar="DIR",
        help="Output DIRECTORY for the run folder (.smart-transcribe-runs/<audio-stem>/ is created inside DIR). Defaults to the audio file's parent directory. Use --transcripts-out for a custom raw-JSON file path with --transcribe-only.",
    )
    parser.add_argument("--transcribe-only", action="store_true",
                        help="Run transcription only, output raw JSON (no merge)")
    parser.add_argument(
        "--transcripts-out",
        metavar="FILE",
        help="Path for raw transcripts JSON FILE (used with --transcribe-only). Different from --output, which sets the run-directory parent.",
    )
    parser.add_argument("--merge-mode", choices=["agent", "claude", "manual"], default="claude",
                        help="agent writes a merge bundle for the current chat agent; claude uses headless Claude/Codex; manual emits a comparison bundle")
    parser.add_argument("--resume", action="store_true", help="Reuse existing per-engine outputs in the run directory")
    parser.add_argument("--rerun-engine", action="append", default=[],
                        help="Engine ID to rerun even when --resume is set; may be passed multiple times")
    parser.add_argument("--doctor", action="store_true", help="Run environment preflight checks and exit")
    parser.add_argument("--check-engine", metavar="ENGINE_ID", help="Run a startup self-test for one engine and exit")
    parser.add_argument("--use-system-python", action="store_true",
                        help="Use a supported system Python instead of the dedicated engine venvs")
    parser.add_argument("--engine-python", help="Comma-separated per-engine overrides: scribe-v2=/path/to/python")
    parser.add_argument("--warm-cohere", action="store_true",
                        help="Warm Cohere model availability and print expected resource costs before running")
    parser.add_argument(
        "--review",
        action="store_true",
        help="Interactively review applied corrections before saving (dispute false positives)",
    )

    args = parser.parse_args()

    # --list-engines → print engine table and exit
    if args.list_engines:
        print("Available transcription engines:")
        for eid, (label, _) in ENGINES.items():
            print(f"  {eid:<26} {label}")
        print("\nAliases:")
        for alias, target in ENGINE_ALIASES.items():
            print(f"  {alias:<26} → {target}")
        sys.exit(0)

    # --context with no value → list saved contexts and exit
    if args.context == "":
        list_contexts()
        sys.exit(0)

    # Require at least one input unless running a maintenance command
    if not any([args.audio_file, args.fix_transcript, args.doctor, args.check_engine, args.warm_cohere]):
        parser.error("Provide an audio file or --fix-transcript FILE.")

    print_runtime_banner()
    engine_python_overrides = parse_engine_python_overrides(args.engine_python)

    # ==========================================================================
    # STAGE 1: Load Dictionary (+ context overlay)
    # ==========================================================================
    default_dict_path, _ = get_dictionary_paths()
    dict_path = Path(args.dict) if args.dict else default_dict_path
    dictionary = load_dictionary(dict_path)

    # One-time notice if user dict still carries pre-4.0 VT/BCBS categories
    # (the 2026-05-06 split moved 206 VT-anchored rules into bcbs-vt overlay).
    try:
        raw_user = json.loads(dict_path.read_text()) if dict_path.exists() else {}
        _maybe_print_migration_notice(raw_user, dict_path)
    except Exception:
        pass

    if args.context:
        ctx = _load_context(args.context)
        dictionary = merge_dicts(dictionary, ctx)

    context_bias = get_context_terms(dictionary)
    print(f"📚 Loaded {len(dictionary.get('corrections', {}))} correction rules", file=sys.stderr)
    print(file=sys.stderr)

    raw_engine_ids = [e.strip() for e in args.engines.split(",") if e.strip()]
    selected_engine_ids: list[str] = []
    for raw in raw_engine_ids:
        resolved = resolve_engine(raw)
        if not resolved:
            print(f"❌ Unknown engine: '{raw}'. Run --list-engines for valid IDs.", file=sys.stderr)
            sys.exit(1)
        selected_engine_ids.append(resolved)

    if args.doctor:
        report = build_doctor_report(selected_engine_ids, engine_python_overrides, args.use_system_python)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0

    if args.check_engine:
        engine_id = resolve_engine(args.check_engine)
        if not engine_id:
            print(f"❌ Unknown engine for --check-engine: {args.check_engine}", file=sys.stderr)
            sys.exit(1)
        python_bin = resolve_engine_python(engine_id, engine_python_overrides, args.use_system_python)
        print(json.dumps({
            "engine": engine_id,
            "supported_runtime": supported_python_string(),
            "self_test": check_engine_runtime(engine_id, python_bin),
        }, indent=2))
        return 0

    if args.warm_cohere:
        print("Cohere local runtime warmup", file=sys.stderr)
        print("Expected costs: first download can take multiple GB of disk, several GB RAM, and a few minutes.", file=sys.stderr)
        cohere_python = resolve_engine_python("cohere-transcribe", engine_python_overrides, args.use_system_python)
        transcribe_cohere("/dev/null", python_bin=cohere_python)  # warm import path; will fail transcript, but primes dependencies
        return 0

    # Parse speakers list if provided
    speakers_list: list | None = [s.strip() for s in args.speakers.split(",")] if args.speakers else None

    # ==========================================================================
    # FIX-TRANSCRIPT MODE: correct an existing transcript, skip audio engines
    # ==========================================================================
    if args.fix_transcript:
        fix_path = Path(args.fix_transcript).resolve()
        if not fix_path.exists():
            print(f"❌ File not found: {fix_path}")
            sys.exit(1)

        print(f"🔧 Fix-transcript mode: {fix_path.name}", file=sys.stderr)
        if args.merge_mode == "agent":
            print("🧠 Review mode: agent bundle for current chat agent", file=sys.stderr)
        else:
            print("🧠 Review runner: Claude Code headless (Codex fallback if rate-limited)", file=sys.stderr)

        raw_text = parse_transcript_file(fix_path)
        if not raw_text.strip():
            print("❌ Parsed transcript is empty.")
            sys.exit(1)

        print(f"   ✅ Parsed {len(raw_text)} chars from {fix_path.suffix} file", file=sys.stderr)

        if args.merge_mode == "agent":
            base_dir = Path(args.output).expanduser().resolve() if args.output else fix_path.parent
            bundle_dir = base_dir / ".smart-transcribe-runs" / fix_path.stem
            bundle_path = emit_agent_merge_bundle(
                bundle_dir,
                {"Source": raw_text},
                dictionary,
                source_file=str(fix_path),
                speakers=speakers_list,
                mode="fix",
            )
            print("\n📦 Agent review bundle ready")
            print(f"📄 {bundle_path}")
            return str(bundle_path)

        final_text, suggestions, metadata, transparency_report, merge_info = merge_with_llm(
            {"Source": raw_text},
            dictionary,
    
            speakers=speakers_list,
            mode="fix",
        )
        review_runner = _merge_runner_label(merge_info.get("runner")) if merge_info.get("runner") else "Original transcript preserved"

        if not final_text:
            print("⚠️  LLM review failed — saving original text unchanged.")
            final_text = raw_text
            metadata = {}
            transparency_report = ""

        append_suggestions(suggestions, source_file=fix_path.name)

        # Display + optional review
        display_transparency_report(transparency_report)
        if args.review:
            interactive_corrections_review(transparency_report)

        # Output
        title = metadata.get("title") if metadata else None
        description = args.description or title or generate_title(final_text)
        speakers_meta = metadata.get("speakers", [])
        summary = metadata.get("summary", "")
        date_mentioned = metadata.get("date_mentioned")
        file_date = datetime.now().strftime("%Y-%m-%d")
        if date_mentioned:
            try:
                file_date = datetime.strptime(date_mentioned, "%Y-%m-%d").strftime("%Y-%m-%d")
            except ValueError:
                pass

        clean_description = _sanitize_filename(description)
        folder_name = f"{file_date} {clean_description}"
        base_dir = Path(args.output).expanduser().resolve() if args.output else fix_path.parent
        output_dir = base_dir / folder_name
        counter = 2
        while output_dir.exists():
            output_dir = base_dir / f"{folder_name} ({counter})"
            counter += 1
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n📂 Output: {output_dir.name}")

        # Copy original alongside corrected version
        original_copy = output_dir / f"original{fix_path.suffix}"
        shutil.copy2(fix_path, original_copy)

        transcript_filename = f"{file_date} {clean_description}.md"
        final_path = output_dir / transcript_filename
        speakers_str = ", ".join(speakers_meta) if speakers_meta else "Unknown"

        transparency_section = f"\n---\n\n## Transparency\n\n{transparency_report or '_No transparency report generated._'}\n"
        metadata_header = {
            "source_file": str(fix_path),
            "mode": "fix-transcript",
            "review_runner": merge_info.get("runner"),
            "review_fallback_reason": merge_info.get("fallback_reason"),
            "context": args.context or "none",
        }

        md_content = f"""# {description}

```json
{json.dumps(metadata_header, indent=2, ensure_ascii=False)}
```

**Date:** {file_date}
**Speakers:** {speakers_str}
**Corrected:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Source:** {fix_path.name} (original preserved as `{original_copy.name}`)
**Review Runner:** {review_runner}
**Context:** {args.context or "none"}

## Summary

{summary if summary else "_No summary generated._"}

---

## Transcript

---

{final_text}
{transparency_section}"""

        final_path.write_text(md_content)
        sidecar_path = output_dir / f"{file_date} {clean_description}.json"
        sidecar_path.write_text(json.dumps({
            "metadata": metadata_header,
            "summary": summary,
            "transcript_path": str(final_path),
            "original_copy": str(original_copy),
        }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"   📄 Saved {transcript_filename}")
        print()
        print("=" * 50)
        print("DONE")
        print("=" * 50)
        print(f"\n📄 {final_path}")
        return str(final_path)

    # ==========================================================================
    # AUDIO MODE: validate input file and run transcription engines
    # ==========================================================================
    audio_path = Path(args.audio_file).resolve()
    if not audio_path.exists():
        print(f"❌ File not found: {audio_path}")
        sys.exit(1)

    print(f"📁 Transcribing: {audio_path.name}", file=sys.stderr)
    if args.merge_mode == "agent" and not args.transcribe_only:
        print("🧠 Merge mode: agent bundle for current chat agent", file=sys.stderr)
    elif not args.transcribe_only:
        print("🧠 Merge runner: Claude Code headless (Codex fallback if rate-limited)", file=sys.stderr)
    else:
        print("📤 Mode: transcribe-only (raw output)", file=sys.stderr)
    print(file=sys.stderr)

    # ==========================================================================
    # STAGE 1.5: Compress Audio (if needed)
    # ==========================================================================
    upload_path = compress_audio(audio_path)

    if len(selected_engine_ids) < 2:
        print(f"❌ At least 2 engines required (got {len(selected_engine_ids)}). "
              f"Use --engines E1,E2", file=sys.stderr)
        sys.exit(1)

    output_root = Path(args.output).expanduser().resolve() if args.output else audio_path.parent
    run_dir = output_root / f".smart-transcribe-runs" / audio_path.stem
    run_dir.mkdir(parents=True, exist_ok=True)
    # Audio duration is needed for the coherence sanity check (chars/minute) and
    # for ElevenLabs credit estimation. Compute once via ffprobe; harmless if 0.
    try:
        audio_duration_seconds = float(get_audio_duration(audio_path))
    except Exception:
        audio_duration_seconds = 0.0
    status_path = run_dir / STATUS_FILE_NAME
    run_log_path = run_dir / RUN_LOG_NAME
    if not run_log_path.exists():
        run_log_path.write_text("", encoding="utf-8")
    with run_log_path.open("a", encoding="utf-8") as fh:
        fh.write(f"{datetime.now().isoformat()} start source={audio_path} engines={','.join(selected_engine_ids)} merge_mode={args.merge_mode}\n")

    # Capture SDK versions per engine venv so run.log records exactly which
    # build of each engine produced the output. Useful when re-running months
    # later or diagnosing an engine-specific regression.
    engine_sdk_versions = collect_engine_sdk_versions(
        selected_engine_ids, engine_python_overrides, args.use_system_python
    )
    with run_log_path.open("a", encoding="utf-8") as fh:
        fh.write(
            f"{datetime.now().isoformat()} engine_sdk_versions "
            + " ".join(f"{eid}={ver}" for eid, ver in engine_sdk_versions.items())
            + "\n"
        )

    write_status(status_path, {
        "source_file": str(audio_path),
        "selected_engines": selected_engine_ids,
        "engine_sdk_versions": engine_sdk_versions,
        "merge_mode": args.merge_mode,
        "state": "starting",
        "updated_at": datetime.now().isoformat(),
    })

    # ==========================================================================
    # STAGE 2 & 3: Run Transcription Engines
    # ==========================================================================
    transcripts: dict = {}
    engine_results: dict[str, dict] = {}
    use_diarization = not args.no_diarization
    local_engine_ids = LOCAL_ENGINE_IDS
    rerun_engine_ids = {resolve_engine(item) or item for item in args.rerun_engine}

    def _run_one_engine(engine_id: str) -> tuple[str, dict]:
        label, func = ENGINES[engine_id]
        engine_slug = engine_id
        engine_log = run_dir / f"{engine_slug}.log"
        normalized_path = run_dir / f"{engine_slug}.normalized.json"
        raw_response_path = run_dir / f"{engine_slug}.raw.json"
        if args.resume and engine_id not in rerun_engine_ids and normalized_path.exists():
            cached = json.loads(normalized_path.read_text())
            return label, cached

        python_bin = resolve_engine_python(engine_id, engine_python_overrides, args.use_system_python)

        _scan_kw = ("error", "quota") + HTTP_RETRYABLE_SIGNALS

        def _attempt_once() -> dict:
            if engine_id == "assemblyai-u3-pro":
                t = transcribe_assemblyai(
                    str(upload_path),
                    speaker_labels=use_diarization,
                    context_bias=context_bias,
                    num_speakers=args.num_speakers,
                    python_bin=python_bin,
                    log_path=engine_log,
                )
            elif engine_id == "voxtral-small":
                t = transcribe_mistral(
                    str(upload_path),
                    context_bias,
                    python_bin=python_bin,
                    log_path=engine_log,
                )
            else:
                t = func(str(upload_path), context_bias, python_bin=python_bin, log_path=engine_log)  # type: ignore[operator]
            if t:
                return {"status": "complete", "text": t, "error": None}
            err = f"{label} returned no transcript"
            if engine_log.exists():
                try:
                    with open(engine_log, encoding="utf-8", errors="replace") as _lf:
                        for line in _lf:
                            if any(kw in line.lower() for kw in _scan_kw):
                                err = line.strip()[:200]
                                break
                except Exception:
                    pass
            return {"status": "failed", "text": "", "error": err}

        retry_result = retry_engine(_attempt_once)
        text = retry_result.get("text") or ""
        status = retry_result["status"]
        failure_reason: str | None = retry_result.get("error") if not text else None
        coherence = assess_engine_coherence(text, audio_duration_seconds)
        result = {
            "engine_id": engine_id,
            "label": label,
            "status": status,
            "failure_reason": failure_reason,
            "python": python_bin,
            "text": text or "",
            "segments": normalize_segments(extract_basic_segments(text or "", engine_id), engine_id),
            "metadata": {"source_engine": engine_id},
            "raw_response_path": str(raw_response_path),
            "char_count": len(text or ""),
            "quality_concern": coherence,
        }
        if coherence is not None:
            print(
                f"⚠️  {label}: {coherence['detail']} "
                f"({coherence['chars_per_minute']} chars/min)",
                file=sys.stderr,
            )
        normalized_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        if text:
            raw_response_path.write_text(json.dumps({"text": text}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return label, result

    # Cloud engines in parallel, local engines sequentially after
    cloud_ids = [eid for eid in selected_engine_ids if eid not in local_engine_ids]
    local_ids = [eid for eid in selected_engine_ids if eid in local_engine_ids]

    if cloud_ids:
        with ThreadPoolExecutor(max_workers=len(cloud_ids)) as executor:
            futures = {executor.submit(_run_one_engine, eid): eid for eid in cloud_ids}
            for future in as_completed(futures):
                label, result = future.result()
                engine_results[label] = result
                transcripts[label] = result.get("text")
                write_status(status_path, {
                    "source_file": str(audio_path),
                    "selected_engines": selected_engine_ids,
                    "state": "running",
                    "updated_at": datetime.now().isoformat(),
                    "engines": engine_results,
                })
                with run_log_path.open("a", encoding="utf-8") as fh:
                    fh.write(f"{datetime.now().isoformat()} engine={label} status={result.get('status')}\n")

    for eid in local_ids:
        label, result = _run_one_engine(eid)
        engine_results[label] = result
        transcripts[label] = result.get("text")
        write_status(status_path, {
            "source_file": str(audio_path),
            "selected_engines": selected_engine_ids,
            "state": "running",
            "updated_at": datetime.now().isoformat(),
            "engines": engine_results,
        })
        with run_log_path.open("a", encoding="utf-8") as fh:
            fh.write(f"{datetime.now().isoformat()} engine={label} status={result.get('status')}\n")

    successful = {k: v for k, v in transcripts.items() if v}

    if not successful:
        print("\n❌ All transcription engines failed.")
        sys.exit(1)

    if len(successful) < 2:
        if DEFAULT_FALLBACK_ENGINE in ENGINES and DEFAULT_FALLBACK_ENGINE not in selected_engine_ids:
            label, result = _run_one_engine(DEFAULT_FALLBACK_ENGINE)
            engine_results[label] = result
            transcripts[label] = result.get("text")
            if result.get("text"):
                successful[label] = result["text"]
        if len(successful) < 2:
            failed = [k for k, v in transcripts.items() if not v]
            print(f"\n❌ Only {len(successful)} engine(s) succeeded.")
            print(f"   Failed: {', '.join(failed)}")
            sys.exit(1)

    if args.merge_mode != "agent":
        _print_engine_summary(engine_results, selected_engine_ids)
    if len(successful) < len(DEFAULT_ENGINES) and set(selected_engine_ids) == set(DEFAULT_ENGINES):
        print(f"⚠️  default engine set degraded: used {len(successful)}/{len(DEFAULT_ENGINES)} engines", file=sys.stderr)

    # ==========================================================================
    # TRANSCRIBE-ONLY MODE: Output raw transcripts and exit
    # ==========================================================================
    if args.transcribe_only:
        output_data = {
            "source_file": str(audio_path),
            "source_name": audio_path.name,
            "transcripts": successful,
            "engine_results": engine_results,
            "engines_used": list(successful.keys()),
            "diarization": use_diarization,
        }
        json_output = json.dumps(output_data, indent=2, ensure_ascii=False)
        if args.transcripts_out:
            out_path = Path(args.transcripts_out)
            out_path.write_text(json_output)
            print(f"📄 Raw transcripts saved to: {out_path}", file=sys.stderr)
        else:
            print(json_output)
        sys.exit(0)

    if args.merge_mode == "agent":
        bundle_path = emit_agent_merge_bundle(
            run_dir,
            successful,
            dictionary,
            source_file=str(audio_path),
            speakers=speakers_list,
            mode="merge",
            engine_results=engine_results,
        )
        write_status(status_path, {
            "source_file": str(audio_path),
            "selected_engines": selected_engine_ids,
            "state": "needs_agent_merge",
            "updated_at": datetime.now().isoformat(),
            "engines": engine_results,
            "agent_merge_bundle": str(bundle_path),
        })
        with run_log_path.open("a", encoding="utf-8") as fh:
            fh.write(f"{datetime.now().isoformat()} needs_agent_merge bundle={bundle_path}\n")
        _print_engine_summary(engine_results, selected_engine_ids, bundle_path=bundle_path)
        return str(bundle_path)

    # ==========================================================================
    # STAGE 4: LLM Merge
    # ==========================================================================
    if args.merge_mode == "manual":
        final_text = successful.get(choose_recommended_base(engine_results) or "", "") or list(successful.values())[0]
        suggestions = []
        metadata = {
            "title": generate_title(final_text),
            "summary": "Manual merge bundle generated; Claude merge skipped by request.",
            "speakers": speakers_list or [],
        }
        transparency_report = "PRESERVED\nManual merge mode requested. Review the comparison bundle and recommended base transcript."
        merge_info = {"runner": "manual", "fallback_reason": None}
    else:
        final_text, suggestions, metadata, transparency_report, merge_info = merge_with_llm(
            successful,
            dictionary,
            speakers=speakers_list,
            mode="merge",
        )

        if not final_text:
            print("⚠️  Merge failed, using recommended base transcript")
            final_text = successful.get(choose_recommended_base(engine_results) or "", "") or list(successful.values())[0]
            metadata = {}
            transparency_report = ""
            merge_info = {"runner": "fallback transcript", "fallback_reason": merge_info.get("fallback_reason")}

    # ==========================================================================
    # STAGE 5: Save Dictionary Suggestions
    # ==========================================================================
    append_suggestions(suggestions, source_file=audio_path.name)

    # ==========================================================================
    # STAGE 5.5: Display Transparency Report + Optional Interactive Review
    # ==========================================================================
    display_transparency_report(transparency_report)
    if args.review:
        interactive_corrections_review(transparency_report)

    # ==========================================================================
    # STAGE 6: Generate Title and Extract Metadata
    # ==========================================================================
    title = metadata.get("title") if metadata else None
    description = args.description or title or generate_title(final_text)

    speakers_meta: list = metadata.get("speakers", []) if metadata else []
    summary = metadata.get("summary", "") if metadata else ""
    date_mentioned = metadata.get("date_mentioned") if metadata else None

    file_date = datetime.now().strftime("%Y-%m-%d")
    if date_mentioned:
        try:
            file_date = datetime.strptime(date_mentioned, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            pass

    # ==========================================================================
    # STAGE 7: Create Output
    # ==========================================================================
    clean_description = re.sub(r'[\\/*?:"<>|]', "", description)[:50]
    folder_name = f"{file_date} {clean_description}"
    base_dir = output_root
    output_dir = base_dir / folder_name
    counter = 2
    while output_dir.exists():
        output_dir = base_dir / f"{folder_name} ({counter})"
        counter += 1
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n📂 Output: {output_dir.name}")

    audio_filename = f"{file_date} {clean_description} \u2013 Audio{audio_path.suffix}"
    shutil.copy2(audio_path, output_dir / audio_filename)

    transcript_filename = f"{file_date} {clean_description}.md"
    final_path = output_dir / transcript_filename

    speakers_str = ", ".join(speakers_meta) if speakers_meta else "Unknown"

    transparency_section = f"\n---\n\n## Transparency\n\n{transparency_report or '_No transparency report generated._'}\n"

    context_note = f"\n**Context:** {args.context}" if args.context else ""
    metadata_header = {
        "source_file": str(audio_path),
        "run_dir": str(run_dir),
        "engines_requested": selected_engine_ids,
        "engines_completed": [label for label, result in engine_results.items() if result.get("status") == "complete"],
        "merge_mode": args.merge_mode,
        "merge_runner": merge_info.get("runner"),
        "merge_fallback_reason": merge_info.get("fallback_reason"),
        "degraded": len(successful) < len(selected_engine_ids),
    }

    merge_runner_label = (
        "Manual comparison bundle"
        if merge_info.get("runner") == "manual"
        else _merge_runner_label(merge_info.get("runner")) if merge_info.get("runner") else "Fallback transcript"
    )

    md_content = f"""# {description}

```json
{json.dumps(metadata_header, indent=2, ensure_ascii=False)}
```

**Date:** {file_date}
**Speakers:** {speakers_str}
**Transcribed:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Source:** {audio_filename}
**Engines:** {', '.join(successful.keys())}
**Merge Runner:** {merge_runner_label}{context_note}

## Summary

{summary if summary else "_No summary generated._"}

---

## Transcript

---

{final_text}
{transparency_section}"""

    final_path.write_text(md_content)
    print(f"   📄 Saved {transcript_filename}")

    sidecar = {
        "metadata": metadata_header,
        "engine_results": engine_results,
        "summary": summary,
        "transcript_path": str(final_path),
    }
    sidecar_path = output_dir / f"{file_date} {clean_description}.json"
    sidecar_path.write_text(json.dumps(sidecar, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if args.merge_mode == "manual":
        emit_manual_merge_bundle(output_dir, engine_results)

    write_status(status_path, {
        "source_file": str(audio_path),
        "selected_engines": selected_engine_ids,
        "state": "complete",
        "updated_at": datetime.now().isoformat(),
        "engines": engine_results,
        "output_dir": str(output_dir),
        "transcript_path": str(final_path),
        "sidecar_path": str(sidecar_path),
    })
    with run_log_path.open("a", encoding="utf-8") as fh:
        fh.write(f"{datetime.now().isoformat()} complete output={final_path}\n")

    print()
    print("=" * 50)
    print("DONE")
    print("=" * 50)
    print(f"\n📄 {final_path}")

    return str(final_path)


if __name__ == "__main__":
    main()
