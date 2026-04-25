#!/usr/bin/env python3
"""
BCBS VT Brand Lint

Flags draft copy for mechanical, high-confidence violations of the two
authoritative style documents:
- 2025-10 Blue Cross Vermont Brand Style Guide
- Writing and Tone Style Guide (rev. Nov 2021)

Usage:
    python3 brand-lint.py path/to/draft.md
    python3 brand-lint.py - < draft.md           # stdin
    python3 brand-lint.py --quiet draft.md       # exit code only

Exit codes:
    0  no violations
    1  one or more violations
    2  usage error / missing file

Checks are deliberately mechanical. This script does NOT evaluate tone,
reading level, or inclusiveness judgments that require human review — it
catches the low-hanging violations that should never reach a draft.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Violation:
    rule: str
    line: int
    col: int
    snippet: str
    fix: str

    def render(self, source_name: str) -> str:
        where = f"{source_name}:{self.line}:{self.col}"
        return f"  [{self.rule}] {where}\n    found: {self.snippet}\n    fix:   {self.fix}"


# ---------------------------------------------------------------------------
# Rule definitions
# ---------------------------------------------------------------------------
#
# Each rule is (id, pattern, fix, optional context filter). The pattern is a
# compiled regex. The fix is a short human-readable instruction. The context
# filter is an optional callable returning True to KEEP a match (useful for
# rules that need to ignore quoted or code contexts — not used yet).

NAME_FORBIDDEN = [
    # Forbidden per Brand Style Guide §Names
    (re.compile(r"\bBCBSVT\b"),
     "FORBIDDEN-NAME",
     'Use "Blue Cross VT" or "Blue Cross and Blue Shield of Vermont."'),
    (re.compile(r"\bBCBS Vermont\b"),
     "FORBIDDEN-NAME",
     'Use "Blue Cross and Blue Shield of Vermont" (first use) or "Blue Cross VT."'),
    (re.compile(r"\bBlue Cross Vermont\b"),
     "FORBIDDEN-NAME",
     'Use "Blue Cross and Blue Shield of Vermont" (first use) or "Blue Cross VT."'),
    (re.compile(r"\bBlue Cross of Vermont\b"),
     "FORBIDDEN-NAME",
     'Use "Blue Cross and Blue Shield of Vermont" (first use) or "Blue Cross VT."'),
]

# Forbidden self-references per Writing and Tone Style Guide §Word List → Words to avoid.
# Matches are case-insensitive but only flagged when they appear to describe BCBS VT itself
# (heuristic: within 120 chars of "Blue Cross," "we," or "our" in the same line).
SELF_REFERENCE_RULES = [
    (re.compile(r"\binsurance company\b", re.IGNORECASE),
     "SELF-REFERENCE",
     'Use "health service organization." We do not describe ourselves as an insurance company.'),
    (re.compile(r"\bour polic(y|ies)\b", re.IGNORECASE),
     "SELF-REFERENCE",
     'Use "subscription(s)." We sell subscriptions, not policies.'),
    (re.compile(r"\bour premiums?\b", re.IGNORECASE),
     "SELF-REFERENCE",
     'Use "subscription rates" (internal) or "rates" (external). We do not charge premiums.'),
    # We don't say "we charge premiums" — same rule, broader phrasing.
    # Gated by _is_about_us so Medicare-context use elsewhere isn't flagged.
    (re.compile(r"\b(charge|charging|charges|charged)\s+(?:a\s+|the\s+|monthly\s+|annual\s+)?premiums?\b", re.IGNORECASE),
     "SELF-REFERENCE",
     'Use "rate(s)" — we charge subscription rates, not premiums.'),
    (re.compile(r"\bpremium\s+rates?\b", re.IGNORECASE),
     "SELF-REFERENCE",
     '"Premium" and "rate" describe the same thing for us — pick one. Prefer "rate(s)."'),
]

# People-first / inclusive-language hotspots — only the highest-confidence
# violations (exact phrases) so this script never mis-flags legitimate quotes.
INCLUSIVE_LANGUAGE = [
    (re.compile(r"\bthe elderly\b", re.IGNORECASE),
     "INCLUSIVE-LANGUAGE",
     'Use "older adults" or "older Vermonters."'),
    (re.compile(r"\bthe blind\b", re.IGNORECASE),
     "INCLUSIVE-LANGUAGE",
     'Use "people who are blind" or "people with low vision."'),
    (re.compile(r"\bhearing impaired\b", re.IGNORECASE),
     "INCLUSIVE-LANGUAGE",
     'Use "deaf," "hard of hearing," or "people with hearing loss."'),
    (re.compile(r"\bhomeless people\b", re.IGNORECASE),
     "INCLUSIVE-LANGUAGE",
     'Use "people experiencing homelessness."'),
]

# Mechanical grammar and formatting.
MECHANICS = [
    (re.compile(r"(\w+) -- (\w+)"),
     "DASH",
     'Use a true em dash ("—") without spaces, not "--".'),
    (re.compile(r"\.  +[A-Z]"),
     "DOUBLE-SPACE",
     'Use one space between sentences, never two.'),
    (re.compile(r"!{2,}"),
     "EXCLAMATION",
     'Use exclamation points sparingly. Never more than one at a time.'),
    (re.compile(r"\[(click here|learn more|read more|here)\]", re.IGNORECASE),
     "LINK-TEXT",
     'Use descriptive link text (e.g., "Find a doctor"), not generic "click here" / "learn more."'),
    (re.compile(r"\b(www\.)?bcbsvt\.com\b", re.IGNORECASE),
     "DOMAIN",
     'The public domain is bluecrossvt.org, not bcbsvt.com. (bcbsvt.com is used only for email.)'),
]


# ---------------------------------------------------------------------------
# Phone-number / TTY rule
# ---------------------------------------------------------------------------
#
# Any phone number like "(800) 247-2583" should be followed (within ~60 chars
# on the same line OR the next line) by a TTY/TDD annotation. Flag any phone
# number that lacks one.

PHONE_PATTERN = re.compile(r"\(\d{3}\)\s*\d{3}-\d{4}")
TTY_PATTERN   = re.compile(r"TTY/TDD[:\s]+711|TTY[:\s]+711", re.IGNORECASE)


def check_phone_tty(lines):
    """Yield Violation for each phone number missing a TTY/TDD annotation nearby."""
    for i, line in enumerate(lines, start=1):
        for m in PHONE_PATTERN.finditer(line):
            # Look in the same line and the next two lines for TTY/TDD: 711.
            window = line[m.end():] + "\n" + \
                     (lines[i]     if i     < len(lines) else "") + "\n" + \
                     (lines[i + 1] if i + 1 < len(lines) else "")
            if not TTY_PATTERN.search(window):
                yield Violation(
                    rule="PHONE-TTY",
                    line=i,
                    col=m.start() + 1,
                    snippet=m.group(0),
                    fix='Add "(TTY/TDD: 711)" after the phone number.',
                )


def _is_about_us(line: str) -> bool:
    """Heuristic: does this line refer to BCBS VT as the subject?"""
    subjects = (
        r"\bblue cross\b", r"\bbcbsvt\b", r"\bwe\b", r"\bour\b", r"\bus\b",
    )
    return any(re.search(p, line, re.IGNORECASE) for p in subjects)


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def lint_text(text: str) -> list[Violation]:
    lines = text.splitlines()
    violations: list[Violation] = []

    for i, line in enumerate(lines, start=1):
        # Forbidden names — always flag regardless of context.
        for rx, rule, fix in NAME_FORBIDDEN:
            for m in rx.finditer(line):
                violations.append(Violation(
                    rule=rule, line=i, col=m.start() + 1,
                    snippet=m.group(0), fix=fix,
                ))

        # Self-reference rules — only flag when the line looks like it's
        # talking about BCBS VT itself (avoid false positives on quotes from
        # competitors or general industry commentary).
        if _is_about_us(line):
            for rx, rule, fix in SELF_REFERENCE_RULES:
                for m in rx.finditer(line):
                    violations.append(Violation(
                        rule=rule, line=i, col=m.start() + 1,
                        snippet=m.group(0), fix=fix,
                    ))

        # Inclusive language.
        for rx, rule, fix in INCLUSIVE_LANGUAGE:
            for m in rx.finditer(line):
                violations.append(Violation(
                    rule=rule, line=i, col=m.start() + 1,
                    snippet=m.group(0), fix=fix,
                ))

        # Mechanics.
        for rx, rule, fix in MECHANICS:
            for m in rx.finditer(line):
                violations.append(Violation(
                    rule=rule, line=i, col=m.start() + 1,
                    snippet=m.group(0), fix=fix,
                ))

    violations.extend(check_phone_tty(lines))
    violations.sort(key=lambda v: (v.line, v.col))
    return violations


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", help='Path to the draft file. Use "-" for stdin.')
    ap.add_argument("--quiet", "-q", action="store_true",
                    help="Suppress output. Exit code only (0 clean, 1 violations).")
    args = ap.parse_args()

    if args.source == "-":
        text = sys.stdin.read()
        name = "<stdin>"
    else:
        path = Path(args.source)
        if not path.exists():
            print(f"error: file not found: {path}", file=sys.stderr)
            sys.exit(2)
        text = path.read_text(encoding="utf-8")
        name = str(path)

    violations = lint_text(text)

    if args.quiet:
        sys.exit(1 if violations else 0)

    if not violations:
        print(f"✓ {name}: no brand-lint violations.")
        sys.exit(0)

    print(f"✗ {name}: {len(violations)} violation(s)\n")
    for v in violations:
        print(v.render(name))
        print()
    sys.exit(1)


if __name__ == "__main__":
    main()
