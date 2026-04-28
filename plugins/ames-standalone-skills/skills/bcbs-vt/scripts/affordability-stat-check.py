#!/usr/bin/env python3
"""
BCBS VT Affordability-Statistic Attribution Check

Per `data/strategy/affordability-matters.md` and SKILL.md, any external
draft that quotes the Vermont affordability headline statistic
(19.6% / 7.9%) MUST carry the WalletHub-July-2025 attribution within
nearby reading distance. This script enforces that mechanically.

Triggers a check on any of:
- "19.6%" or "19.6 percent"
- "7.9%" or "7.9 percent"
- "highest in the country" (the campaign tagline)

For each match, looks within ~300 characters (forward AND backward) for
the four required attribution components:
- "WalletHub"
- "July 2025" (or "Jul 2025")
- "Census" (US Census Bureau)
- "Kaiser" (Kaiser Family Foundation, often abbreviated KFF)

Reports:
- PASS  — claim is fully attributed (all four components found near the claim).
- WARN  — claim is partially attributed (at least one component, but not all).
- FAIL  — claim has zero attribution components nearby.

Usage:
    python3 affordability-stat-check.py path/to/draft.md
    python3 affordability-stat-check.py - < draft.md     # stdin

Exit codes:
    0  no FAIL violations (PASS or WARN only)
    1  one or more FAIL violations
    2  usage error / missing file
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


WINDOW = 300  # chars on each side of the claim

CLAIM_PATTERNS = [
    re.compile(r"\b19\.6\s*%"),
    re.compile(r"\b19\.6\s+percent\b", re.IGNORECASE),
    re.compile(r"\b7\.9\s*%"),
    re.compile(r"\b7\.9\s+percent\b", re.IGNORECASE),
    re.compile(r"highest\s+in\s+the\s+country", re.IGNORECASE),
]

ATTRIBUTION_COMPONENTS = [
    ("WalletHub", re.compile(r"\bWallet\s*Hub\b", re.IGNORECASE)),
    ("July 2025", re.compile(r"\b(July|Jul\.?)\s+2025\b", re.IGNORECASE)),
    ("Census",    re.compile(r"\bCensus\b", re.IGNORECASE)),
    ("Kaiser",    re.compile(r"\bKaiser\b|\bKFF\b", re.IGNORECASE)),
]


@dataclass
class Finding:
    status: str        # PASS / WARN / FAIL
    line: int
    col: int
    claim: str
    components_found: list[str]
    components_missing: list[str]

    def render(self, source_name: str) -> str:
        where = f"{source_name}:{self.line}:{self.col}"
        if self.status == "PASS":
            tail = "fully attributed (WalletHub + July 2025 + Census + Kaiser)."
        elif self.status == "WARN":
            tail = (
                f"partial attribution. Found: {', '.join(self.components_found) or 'none'}. "
                f"Missing: {', '.join(self.components_missing)}."
            )
        else:
            tail = (
                "no attribution found within ±300 chars. Required: "
                'Source: "Based on data from the U.S. Census Bureau and Kaiser '
                'Family Foundation, published in a July 2025 WalletHub report."'
            )
        icon = {"PASS": "✓", "WARN": "!", "FAIL": "✗"}[self.status]
        return f"  {icon} [{self.status}] {where}\n    claim: {self.claim}\n    {tail}"


def find_claims(text: str) -> list[tuple[int, int, str, int]]:
    """Return list of (line_number, col, claim_text, abs_offset)."""
    results = []
    line_starts = [0]
    for i, ch in enumerate(text):
        if ch == "\n":
            line_starts.append(i + 1)

    for pattern in CLAIM_PATTERNS:
        for m in pattern.finditer(text):
            offset = m.start()
            line = next(i for i in range(len(line_starts) - 1, -1, -1) if line_starts[i] <= offset)
            col = offset - line_starts[line] + 1
            results.append((line + 1, col, m.group(0), offset))
    results.sort(key=lambda r: r[3])
    return results


def assess_attribution(text: str, offset: int, claim_len: int) -> tuple[list[str], list[str]]:
    start = max(0, offset - WINDOW)
    end = min(len(text), offset + claim_len + WINDOW)
    window = text[start:end]
    found = [name for name, rx in ATTRIBUTION_COMPONENTS if rx.search(window)]
    missing = [name for name, _ in ATTRIBUTION_COMPONENTS if name not in found]
    return found, missing


def check_text(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for line, col, claim, offset in find_claims(text):
        found, missing = assess_attribution(text, offset, len(claim))
        if not missing:
            status = "PASS"
        elif not found:
            status = "FAIL"
        else:
            status = "WARN"
        findings.append(Finding(
            status=status, line=line, col=col, claim=claim,
            components_found=found, components_missing=missing,
        ))
    return findings


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("source", help='Path to the draft file. Use "-" for stdin.')
    ap.add_argument("--quiet", "-q", action="store_true",
                    help="Suppress output. Exit code only (0 if no FAIL, 1 otherwise).")
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

    findings = check_text(text)
    fail_count = sum(1 for f in findings if f.status == "FAIL")

    if args.quiet:
        sys.exit(1 if fail_count else 0)

    if not findings:
        print(f"✓ {name}: no affordability statistic claims detected — nothing to attribute.")
        sys.exit(0)

    pass_count = sum(1 for f in findings if f.status == "PASS")
    warn_count = sum(1 for f in findings if f.status == "WARN")

    print(f"{name}: {len(findings)} claim(s) — {pass_count} pass, {warn_count} warn, {fail_count} fail\n")
    for f in findings:
        print(f.render(name))
        print()
    sys.exit(1 if fail_count else 0)


if __name__ == "__main__":
    main()
