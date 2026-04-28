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
    (re.compile(r"\btransgendered\b", re.IGNORECASE),
     "INCLUSIVE-LANGUAGE",
     'Use "transgender" (never "transgendered"). Writing & Tone Guide p. 9.'),
]

# `health care` (the action) vs `healthcare` (the system). Writing & Tone
# Guide p. 28: "health care" describes actions of providers and patients;
# "healthcare" describes the system/industry/field. Flag `healthcare`
# followed by action words; leave system/industry/market/reform alone.
HEALTH_CARE_ACTION = [
    (re.compile(
        r"\bhealthcare\s+(provider|providers|professional|professionals|"
        r"worker|workers|team|teams|appointment|appointments|"
        r"visit|visits|services|service|access|delivery|coverage|"
        r"choice|choices|decision|decisions|plan|plans)\b",
        re.IGNORECASE,
     ),
     "HEALTH-CARE-TWO-WORDS",
     '"health care" (two words) is the action of providers/patients; "healthcare" (one word) is only the system/industry. Use "health care" here.'),
]

# Mechanical grammar and formatting.
MECHANICS = [
    (re.compile(r"(\w+) -- (\w+)"),
     "DASH",
     'Use a true em dash ("—") without spaces, not "--".'),
    (re.compile(r"\s+—\s+"),
     "DASH-SPACING",
     'Use a true em dash without spaces around it: "word—word", not "word — word" (Writing & Tone Guide p. 16).'),
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
     'Use bluecrossvt.org. The bcbsvt.com domain is deprecated and now 301-redirects to bluecrossvt.org for both web and email signatures.'),
    (re.compile(r"\bwell\s+being\b", re.IGNORECASE),
     "HYPHEN",
     'Use "well-being" (hyphenated). Writing & Tone Guide word list p. 28.'),
    (re.compile(r"\bwellbeing\b", re.IGNORECASE),
     "HYPHEN",
     'Use "well-being" (hyphenated). Writing & Tone Guide word list p. 28.'),
]

# Corporate fluff / Silicon Valley clichés the Writing & Tone Guide explicitly
# tells us not to use (Word List → Words to Avoid, p. 29). Gated by
# _is_about_us so industry critique that quotes these terms isn't flagged.
CORPORATE_FLUFF = [
    (re.compile(r"\bfunnel\b", re.IGNORECASE),
     "CORPORATE-FLUFF",
     'Avoid "funnel" in our voice. Plain English alternatives: "the steps customers take," "the path to coverage."'),
    (re.compile(r"\bincentivi[sz](e|es|ed|ing)\b", re.IGNORECASE),
     "CORPORATE-FLUFF",
     'Avoid "incentivize." Use "encourage," "reward," or just say what we offer.'),
    (re.compile(r"\bleverag(e|es|ed|ing)\b", re.IGNORECASE),
     "CORPORATE-FLUFF",
     'Avoid "leverage." Use "use," "apply," or "build on."'),
    (re.compile(r"\bdisrupt(ing|ed|ion|or)?\b", re.IGNORECASE),
     "CORPORATE-FLUFF",
     'Avoid "disrupt" / "disruption" / "disruptor" — Silicon Valley cliché. Be specific about what is changing.'),
    (re.compile(r"\bthought leader(ship)?\b", re.IGNORECASE),
     "CORPORATE-FLUFF",
     'Avoid "thought leader." Be specific (e.g., "Beth Roberts, our CEO, on affordability").'),
    (re.compile(r"\blearnings\b", re.IGNORECASE),
     "CORPORATE-FLUFF",
     'Avoid "learnings." Use "what we learned," "lessons," or "findings."'),
    (re.compile(r"\b(crushing|crushed) it\b", re.IGNORECASE),
     "CORPORATE-FLUFF",
     'Avoid "crushing it" / "crushed it." Pick a specific, concrete description.'),
    (re.compile(r"\b(killing|killed) it\b", re.IGNORECASE),
     "CORPORATE-FLUFF",
     'Avoid "killing it" / "killed it." Pick a specific, concrete description.'),
    (re.compile(r"\bbest[\s-]in[\s-]breed\b", re.IGNORECASE),
     "CORPORATE-FLUFF",
     'Avoid "best-in-breed." Use "best," "leading," or describe the actual capability.'),
    (re.compile(r"\brise and grind\b", re.IGNORECASE),
     "CORPORATE-FLUFF",
     'Avoid "rise and grind" — Silicon Valley cliché.'),
    (re.compile(r"\b(a|the|big|small|main|huge)\s+ask\b", re.IGNORECASE),
     "CORPORATE-FLUFF",
     '"Ask" as a noun is corporate-speak. Use "request," "favor," or "what we need."'),
    # Money colloquialisms forbidden by Writing & Tone Guide p. 14.
    (re.compile(r"\bgreenbacks?\b", re.IGNORECASE),
     "CORPORATE-FLUFF",
     'Avoid "greenback(s)" — colloquial. Use "dollars" or "money."'),
    (re.compile(r"\bfive[-\s]and[-\s]dime\b", re.IGNORECASE),
     "CORPORATE-FLUFF",
     'Avoid "five-and-dime" — colloquial money slang.'),
    (re.compile(r"\bc[-\s]notes?\b", re.IGNORECASE),
     "CORPORATE-FLUFF",
     'Avoid "c-note(s)" — colloquial money slang.'),
]

# Internet slang variations explicitly forbidden (Word List → Words to Avoid).
INTERNET_SLANG = [
    (re.compile(r"\binternets\b", re.IGNORECASE),
     "INTERNET-SLANG",
     'Use "internet" (singular). The Writing & Tone Guide forbids "internets/interwebs."'),
    (re.compile(r"\binterwebs\b", re.IGNORECASE),
     "INTERNET-SLANG",
     'Use "internet." The Writing & Tone Guide forbids "interwebs."'),
]

# "Ninja/rockstar/wizard" — only flag if not literal. We can't tell from a
# regex whether someone is literally a ninja, so this is a WARN-level rule.
LITERAL_OR_SKIP = [
    (re.compile(r"\b(ninja|rockstar|wizard)\b", re.IGNORECASE),
     "LITERAL-OR-SKIP",
     'Don\'t call someone a "ninja," "rockstar," or "wizard" unless they literally are one (Writing & Tone Guide, p. 18).'),
]

# The previous toll-free TTY line (800-535-2227) is no longer functional.
# Per Writing & Tone Guide p. 22, refer customers to 711 instead. Hard error.
RETIRED_TTY = [
    (re.compile(r"\b800[-.\s]?535[-.\s]?2227\b"),
     "RETIRED-TTY",
     'The 800-535-2227 TTY number is retired. Refer customers to the federal public service: TTY/TDD: 711.'),
]

# Accessibility: avoid directional language (Writing & Tone Guide, p. 20).
DIRECTIONAL = [
    (re.compile(r"\b(left|right) sidebar\b", re.IGNORECASE),
     "DIRECTIONAL",
     'Avoid directional language (layout shifts on mobile). Describe the option by name, not its position.'),
    (re.compile(r"\bin the (right|left) (column|panel|pane|section)\b", re.IGNORECASE),
     "DIRECTIONAL",
     'Avoid directional language. Describe the option by name, not its position on the page.'),
    (re.compile(r"\b(at the bottom|at the top|on the right|on the left) of (the|this) (page|screen)\b", re.IGNORECASE),
     "DIRECTIONAL",
     'Avoid directional language. Describe the option by name, not its position.'),
]

# Mechanical word-list rules from Writing & Tone Guide p. 28-29.
# These are exact-casing violations that are always wrong in BCBS voice.
WORD_LIST = [
    (re.compile(r"\be-mail\b", re.IGNORECASE),
     "WORD-LIST",
     'Use "email" (never hyphenate or capitalize). Writing & Tone Guide p. 28.'),
    # Internet / Website / Online — only flag when capitalized mid-sentence.
    # Match a capital I/W/O preceded by lowercase or a comma/space-not-period.
    (re.compile(r"(?<=[a-z\s,])\bInternet\b"),
     "WORD-LIST",
     'Use "internet" (lowercase, except sentence-start). Writing & Tone Guide p. 28.'),
    (re.compile(r"(?<=[a-z\s,])\bWebsite\b"),
     "WORD-LIST",
     'Use "website" (lowercase, except sentence-start). Writing & Tone Guide p. 28.'),
    (re.compile(r"(?<=[a-z\s,])\bOnline\b"),
     "WORD-LIST",
     'Use "online" (lowercase, except sentence-start). Writing & Tone Guide p. 28.'),
]

# Partner-name typos (legacy or wrong forms) — Affordability Matters site.
# Source: vtaffordablecare.com, current 2026 partner names.
PARTNER_NAMES = [
    (re.compile(r"\bVermont\s+OPEN\s+MRI\b", re.IGNORECASE),
     "PARTNER-NAME",
     'Use "Vermont OPEN Imaging" (rebranded from the legacy "Vermont OPEN MRI"). The vtopenmri.com URL still resolves but the company name is now Vermont OPEN Imaging.'),
    (re.compile(r"\bGreen\s+Mountain\s+Surgical\s+Center\b", re.IGNORECASE),
     "PARTNER-NAME",
     'Use "Green Mountain Surgery Center" (the company is named "Surgery Center," not "Surgical Center").'),
    (re.compile(r"\bNorthwestern\s+Hospital\b", re.IGNORECASE),
     "PARTNER-NAME",
     'Use "Northwestern Medical Center" (NMC). The St. Albans facility is a medical center, not a hospital.'),
]

# Company-as-"it" rule (Writing & Tone Guide p. 7): refer to a company or
# product as "it," not "they." Heuristic: flag a partner/competitor name
# followed within ~80 chars by "they" or "their" referring to it.
COMPANY_AS_IT = [
    (re.compile(
        r"\b(Northwestern Medical Center|NMC|Green Mountain Surgery Center|GMSC|"
        r"Vermont OPEN Imaging|Vermont Diagnostic Imaging|VDI|"
        r"Cigna|Aetna|United\s*Health\s*Care|UnitedHealthcare|UHC|MVP)\b"
        r"[^.!?\n]{0,80}\b(they|their|they're)\b",
        re.IGNORECASE,
     ),
     "COMPANY-AS-IT",
     'Refer to a company or product as "it," not "they" (Writing & Tone Guide p. 7). Rewrite the sentence to use "it" or restructure.'),
]

# Oxford-comma WARN — heuristic only. Flags `X, Y and Z` patterns that
# look like a 3-item list missing the serial comma. Excludes common
# "Name, Title and Title" appositive patterns where the word after the
# comma is a job-title word (President, CEO, Director, etc.) since
# those are role descriptions, not list items.
OXFORD_COMMA_WARN = [
    (re.compile(
        r"\b\w+,\s+"
        r"(?!(?:President|CEO|COO|CFO|CTO|CMO|VP|Vice|Director|Manager|"
        r"Officer|Coordinator|Specialist|Counsel|Chief|Founder|Owner|"
        r"Senior|Junior|Executive|Principal|Head|Chair|Chairman|Chairwoman|"
        r"Editor|Producer|Engineer|Designer|Architect|Analyst|Strategist|"
        r"Consultant|Advisor|Lead|Member|Trustee|Partner|Associate)\b)"
        r"\w+\s+and\s+\w+\b"
     ),
     "OXFORD-COMMA-WARN",
     'Possible missing serial (Oxford) comma. Writing & Tone Guide p. 16: use a serial comma in lists. Verify manually.'),
]


# ---------------------------------------------------------------------------
# Phone-number / TTY rule
# ---------------------------------------------------------------------------
#
# Any phone number like "(800) 247-2583" should be followed (within ~60 chars
# on the same line OR the next line) by a TTY/TDD annotation. Flag any phone
# number that lacks one.

PHONE_PATTERN = re.compile(r"(?<!\w)(?:\(\d{3}\)\s*|\d{3}[-.])\d{3}[-.]\d{4}(?!\w)")
TTY_PATTERN   = re.compile(r"TTY/TDD[:\s]+711|TTY[:\s]+711", re.IGNORECASE)
RETIRED_NUMBER_NORMALIZED = "8005352227"


def _normalize_phone(s: str) -> str:
    return re.sub(r"\D", "", s)


def check_phone_tty(lines):
    """Yield Violation for each phone number missing a TTY/TDD annotation nearby.

    Skips the retired 800-535-2227 number — the RETIRED_TTY rule already fires
    on it; we don't want to double-count one phone as both PHONE-TTY and
    RETIRED-TTY.
    """
    for i, line in enumerate(lines, start=1):
        for m in PHONE_PATTERN.finditer(line):
            if _normalize_phone(m.group(0)) == RETIRED_NUMBER_NORMALIZED:
                continue
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


def _is_about_us_window(lines: list[str], index: int, span: int = 1) -> bool:
    """Cross-line gating: returns True if THIS line or the previous `span`
    lines refer to BCBS VT. Catches subject-spanning prose like:

        Vermonters can now choose from three new policies. We've been working
        on these for two years.

    where the singular "policies" wouldn't be flagged with single-line gating
    even though the two-line context makes the BCBS-subject reference clear.
    """
    start = max(0, index - span)
    return any(_is_about_us(lines[j]) for j in range(start, index + 1))


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

        # Self-reference rules — broader gating: this line OR previous line
        # references BCBS VT. Catches subject-spanning prose where the
        # noun-of-concern is on a different line from the subject pronoun.
        if _is_about_us_window(lines, i - 1, span=1):
            for rx, rule, fix in SELF_REFERENCE_RULES:
                for m in rx.finditer(line):
                    violations.append(Violation(
                        rule=rule, line=i, col=m.start() + 1,
                        snippet=m.group(0), fix=fix,
                    ))
            # Corporate fluff — same gating. Industry critique that quotes
            # "thought leader" or "disruption" is fine; using it ourselves isn't.
            for rx, rule, fix in CORPORATE_FLUFF:
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

        # health care vs healthcare (Writing & Tone Guide p. 28).
        for rx, rule, fix in HEALTH_CARE_ACTION:
            for m in rx.finditer(line):
                violations.append(Violation(
                    rule=rule, line=i, col=m.start() + 1,
                    snippet=m.group(0), fix=fix,
                ))

        # Internet slang (always — never appropriate in BCBS voice).
        for rx, rule, fix in INTERNET_SLANG:
            for m in rx.finditer(line):
                violations.append(Violation(
                    rule=rule, line=i, col=m.start() + 1,
                    snippet=m.group(0), fix=fix,
                ))

        # "Ninja/rockstar/wizard" — flagged unconditionally. The fix message
        # explicitly says "unless they literally are one" so the human can
        # accept the false positive when the term is literal.
        for rx, rule, fix in LITERAL_OR_SKIP:
            for m in rx.finditer(line):
                violations.append(Violation(
                    rule=rule, line=i, col=m.start() + 1,
                    snippet=m.group(0), fix=fix,
                ))

        # Retired TTY number (hard error — never publish the old line).
        for rx, rule, fix in RETIRED_TTY:
            for m in rx.finditer(line):
                violations.append(Violation(
                    rule=rule, line=i, col=m.start() + 1,
                    snippet=m.group(0), fix=fix,
                ))

        # Directional language (accessibility — layout shifts on mobile).
        for rx, rule, fix in DIRECTIONAL:
            for m in rx.finditer(line):
                violations.append(Violation(
                    rule=rule, line=i, col=m.start() + 1,
                    snippet=m.group(0), fix=fix,
                ))

        # Mechanical word-list rules (e-mail, Internet, Website, Online).
        for rx, rule, fix in WORD_LIST:
            for m in rx.finditer(line):
                violations.append(Violation(
                    rule=rule, line=i, col=m.start() + 1,
                    snippet=m.group(0), fix=fix,
                ))

        # Partner-name typos (legacy / wrong forms).
        for rx, rule, fix in PARTNER_NAMES:
            for m in rx.finditer(line):
                violations.append(Violation(
                    rule=rule, line=i, col=m.start() + 1,
                    snippet=m.group(0), fix=fix,
                ))

        # Company-as-"it" (companies + "they" pattern within ~80 chars).
        for rx, rule, fix in COMPANY_AS_IT:
            for m in rx.finditer(line):
                violations.append(Violation(
                    rule=rule, line=i, col=m.start() + 1,
                    snippet=m.group(0), fix=fix,
                ))

        # Oxford comma — WARN-level heuristic (false positives common).
        for rx, rule, fix in OXFORD_COMMA_WARN:
            for m in rx.finditer(line):
                violations.append(Violation(
                    rule=rule, line=i, col=m.start() + 1,
                    snippet=m.group(0), fix=fix,
                ))

    violations.extend(check_phone_tty(lines))
    violations.sort(key=lambda v: (v.line, v.col))
    return violations


def _reading_level_report(text: str) -> str | None:
    """Optional reading-level report. Returns None if textstat isn't installed.

    Writing & Tone Guide p. 4 specifies sixth-grade reading level. We use
    Flesch-Kincaid grade as the most common single number. WARN if > 7.
    """
    try:
        import textstat  # type: ignore[import-untyped]
    except ImportError:
        return (
            "  ! [READING-LEVEL] textstat is not installed. "
            "Run: python3 -m pip install textstat"
        )
    try:
        grade = textstat.flesch_kincaid_grade(text)
    except Exception as exc:
        return f"  ! [READING-LEVEL] textstat error: {exc}"
    icon = "✓" if grade <= 7 else "!"
    status = "PASS" if grade <= 7 else "WARN"
    target = "Target ≤ 6 (sixth-grade reading level)."
    return f"  {icon} [{status}] Flesch-Kincaid grade: {grade:.1f}. {target}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", help='Path to the draft file. Use "-" for stdin.')
    ap.add_argument("--quiet", "-q", action="store_true",
                    help="Suppress output. Exit code only (0 clean, 1 violations).")
    ap.add_argument("--reading-level", action="store_true",
                    help="Also report Flesch-Kincaid reading level (requires the textstat package).")
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

    if violations:
        print(f"✗ {name}: {len(violations)} violation(s)\n")
        for v in violations:
            print(v.render(name))
            print()
    else:
        print(f"✓ {name}: no brand-lint violations.")

    if args.reading_level:
        print()
        report = _reading_level_report(text)
        if report:
            print(report)

    sys.exit(1 if violations else 0)


if __name__ == "__main__":
    main()
