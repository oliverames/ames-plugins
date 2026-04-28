#!/usr/bin/env python3
"""
BCBS VT Letter Format Checklist

Automates the format section of the authoritative Letter Checklist
(Writing and Tone Style Guide §Letter Guidelines → Format).

Checks a `.docx` and reports pass/fail for each mechanical format item:

  [ ] The font Calibri, Din 2014, or Arial
  [ ] The font point size 11 (or 12 for Medicare)
  [ ] Document is single-spaced (1.0)
  [ ] Margins: top=1", bottom=1", left=1.25", right=1.25"
  [ ] Text is left-justified
  [ ] Logo appears on page one (inferred from header + embedded media)

The CONTENT section of the Letter Checklist (jargon, call-to-action
placement, signature, "over" on multi-page, etc.) is reviewer-judged and
not automated here.

Usage:
    python3 letter-check.py path/to/letter.docx
    python3 letter-check.py --medicare path/to/letter.docx   # expects 12pt

Exit codes:
    0  all checks pass
    1  at least one check fails
    2  usage error / file not found / not a .docx
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path
from typing import NoReturn


APPROVED_FONTS = {"Calibri", "DIN 2014", "Arial"}

# OOXML margin values are in twentieths of a point (1440 twips = 1 inch).
TARGET_MARGIN_TWIPS = {
    "top":    1440,   # 1"
    "bottom": 1440,   # 1"
    "left":   1800,   # 1.25"
    "right":  1800,   # 1.25"
}


def die(msg: str, code: int = 2) -> NoReturn:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def load_docx(path: Path) -> zipfile.ZipFile:
    if not path.exists():
        die(f"file not found: {path}")
    if path.suffix.lower() != ".docx":
        die(f"not a .docx file: {path}")
    try:
        return zipfile.ZipFile(path)
    except zipfile.BadZipFile:
        die(f"not a valid Word document: {path}")


def get_normal_style(styles_xml: str) -> tuple[str | None, float | None]:
    """Return (font, size_pt) from the Normal style, or (None, None)."""
    m = re.search(r'<w:style[^>]*w:styleId="Normal"[\s\S]*?</w:style>', styles_xml)
    if not m:
        return None, None
    block = m.group(0)
    fonts = re.findall(r'w:ascii="([^"]+)"', block)
    sizes = re.findall(r'<w:sz w:val="(\d+)"', block)
    # w:sz is in half-points.
    font = fonts[0] if fonts else None
    size = (int(sizes[0]) / 2.0) if sizes else None
    return font, size


def get_margins(document_xml: str) -> dict[str, int] | None:
    m = re.search(r'<w:pgMar\b([^/]*)/>', document_xml)
    if not m:
        return None
    attrs = m.group(1)
    out = {}
    for side in ("top", "bottom", "left", "right"):
        mm = re.search(rf'w:{side}="(\d+)"', attrs)
        if mm:
            out[side] = int(mm.group(1))
    return out


def is_single_spaced(styles_xml: str) -> bool:
    """Check the Normal style's line-spacing rule.

    Absent w:spacing line=... means Word's default (single).  If set, w:line
    is in twentieths of a point and w:lineRule is "auto" for multiples.
    Single-spaced is w:line="240" + w:lineRule="auto", OR nothing at all.
    """
    m = re.search(r'<w:style[^>]*w:styleId="Normal"[\s\S]*?</w:style>', styles_xml)
    if not m:
        return True  # unable to determine → don't fail noisily
    block = m.group(0)
    line_match = re.search(r'<w:spacing[^/]*\bw:line="(\d+)"', block)
    if not line_match:
        return True
    line_twips = int(line_match.group(1))
    rule_match = re.search(r'w:lineRule="(\w+)"', block)
    rule = rule_match.group(1) if rule_match else "auto"
    if rule == "auto":
        return line_twips == 240  # 240 = 1.0 line
    return False


def has_header_with_logo(z: zipfile.ZipFile) -> bool:
    """Page-one logo check: header1.xml exists and at least one image is in media/."""
    names = z.namelist()
    has_header = any(n.startswith("word/header") and n.endswith(".xml") for n in names)
    has_image  = any(n.startswith("word/media/") for n in names)
    return has_header and has_image


# Brand Style Guide (Oct 2025, p. 1, 3) requires the Independent Licensee
# tagline somewhere on the document — body, header, or footer. We
# concatenate text from all three locations before checking.
INDEPENDENT_LICENSEE_PATTERN = re.compile(
    r"Independent\s+Licensee\s+of\s+the\s+Blue\s+Cross\s+and\s+Blue\s+Shield\s+Association",
    re.IGNORECASE,
)


def has_independent_licensee_tagline(z: zipfile.ZipFile) -> bool:
    """Search body + headers + footers for the Independent Licensee tagline."""
    parts = []
    for name in z.namelist():
        if (
            name == "word/document.xml"
            or (name.startswith("word/header") and name.endswith(".xml"))
            or (name.startswith("word/footer") and name.endswith(".xml"))
        ):
            try:
                xml = z.read(name).decode("utf-8", errors="replace")
            except KeyError:
                continue
            parts.append(TAG_RX.sub(" ", xml))
    combined = re.sub(r"\s+", " ", " ".join(parts))
    return bool(INDEPENDENT_LICENSEE_PATTERN.search(combined))


def body_is_left_aligned(document_xml: str) -> bool:
    """No paragraph in the body should have w:jc val=center/right/both."""
    # Count forbidden alignments.
    forbidden = re.findall(r'<w:jc w:val="(center|right|both)"', document_xml)
    return len(forbidden) == 0


# Strip OOXML tags to get the plain-text body. Used for content checks
# (® presence, "over" word, signature block) that don't care about formatting.
TAG_RX = re.compile(r"<[^>]+>")


def extract_text(document_xml: str) -> str:
    """Return the document body text with OOXML tags stripped and whitespace normalized."""
    text = TAG_RX.sub("", document_xml)
    # Collapse runs of whitespace; OOXML often inserts newlines mid-run.
    text = re.sub(r"\s+", " ", text).strip()
    return text


def has_service_marks(text: str) -> bool:
    """Check for at least one ® or ℠ on a Blue Cross brand name in the body.

    The Brand Style Guide (Oct 2025, p. 2) requires the registration indicia
    on the first or most-prominent appearance of a mark. Header logos count
    visually but the body text should still carry the symbol on a name use.
    """
    # Find any "Blue Cross" mention, then check if ® or ℠ is within ~30 chars.
    for m in re.finditer(r"Blue\s*Cross", text, flags=re.IGNORECASE):
        window = text[m.start(): m.end() + 30]
        if "®" in window or "℠" in window:
            return True
    return False


def estimate_page_count(document_xml: str) -> int:
    """Return a conservative page count based on explicit page breaks.

    Counts <w:br w:type="page"/> + 1. Word's automatic pagination isn't visible
    in OOXML, so this only catches docs the author explicitly broke. A "1"
    answer means "no manual breaks present" — the doc may still flow to two+
    pages naturally. For mechanical checks this is acceptable: we only enforce
    "over" on docs the author KNOWS are multi-page.
    """
    breaks = re.findall(r'<w:br[^/]*w:type="page"', document_xml)
    return len(breaks) + 1


def has_over_word(text: str, page_count: int) -> bool | None:
    """Return True/False if the doc is multi-page and includes "over"; None otherwise.

    Per the Letter Checklist (Writing & Tone Guide, p. 24): include the word
    "over" on multi-page letters so the reader knows to turn the page.
    """
    if page_count < 2:
        return None  # not applicable
    return bool(re.search(r"\bover\b", text, flags=re.IGNORECASE))


def has_signature_block(text: str) -> bool:
    """Heuristic: look for either a closing word OR a clear title near the end.

    Two accept paths:
      1. A closing word ("Sincerely,", "Thank you,", "Regards," etc.) within
         the last ~400 chars. Classic letter signature.
      2. A common professional title ("President," "CEO," "Director,"
         "Strategist," etc.) within the last ~250 chars, even without a
         closing word. Many BCBS letters close with name + title only —
         the warmth has already been done in the body, so a closing word
         would feel redundant. This path keeps the linter from WARN'ing
         on those correct letters.

    We can't validate the actual handwritten signature image from text alone;
    this checks for the textual sign-off only.
    """
    tail = text[-400:] if len(text) > 400 else text
    closings = (
        r"\bSincerely,?\b",
        r"\bThank you,?\b",
        r"\bRegards,?\b",
        r"\bBest,?\b",
        r"\bWith\s+(thanks|appreciation|gratitude),?\b",
        r"\bRespectfully,?\b",
        r"\bWarmly,?\b",
    )
    if any(re.search(rx, tail, flags=re.IGNORECASE) for rx in closings):
        return True

    # Fallback: name + title pattern. We look at a slightly tighter tail to
    # reduce false-positives from body prose that happens to mention a title.
    title_tail = text[-250:] if len(text) > 250 else text
    title_pattern = re.compile(
        r"\b("
        r"President(?:\s+(?:and|&)\s+CEO)?"
        r"|CEO|COO|CFO|CTO|CMO"
        r"|Chief\s+\w+(?:\s+\w+)?\s+Officer"
        r"|Vice\s+President|VP"
        r"|Director(?:\s+of\s+\w+(?:\s+\w+){0,2})?"
        r"|Senior\s+Director|Executive\s+Director"
        r"|Manager(?:\s+of\s+\w+(?:\s+\w+){0,2})?"
        r"|Strategist|Specialist|Coordinator|Analyst"
        r"|Counsel|General\s+Counsel"
        r")\b",
        flags=re.IGNORECASE,
    )
    return bool(title_pattern.search(title_tail))


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("docx", help="Path to the .docx to check.")
    ap.add_argument("--medicare", action="store_true",
                    help="Expect 12pt body (Medicare-related communications).")
    args = ap.parse_args()

    path = Path(args.docx)
    z = load_docx(path)
    styles_xml   = z.read("word/styles.xml").decode("utf-8", errors="replace")
    document_xml = z.read("word/document.xml").decode("utf-8", errors="replace")

    expected_body_size = 12.0 if args.medicare else 11.0
    font, size = get_normal_style(styles_xml)
    margins = get_margins(document_xml)
    single_spaced = is_single_spaced(styles_xml)
    left_aligned = body_is_left_aligned(document_xml)
    logo_present = has_header_with_logo(z)

    body_text = extract_text(document_xml)
    page_count = estimate_page_count(document_xml)
    service_marks_ok = has_service_marks(body_text)
    over_word_ok = has_over_word(body_text, page_count)
    signature_ok = has_signature_block(body_text)
    independent_licensee_ok = has_independent_licensee_tagline(z)

    checks = []

    # Font family
    if font in APPROVED_FONTS:
        checks.append(("PASS", f"Font is {font} (approved: Calibri / DIN 2014 / Arial)"))
    elif font is None:
        checks.append(("WARN", "Could not detect Normal-style font — inspect manually."))
    else:
        checks.append(("FAIL", f"Font is '{font}' — must be Calibri, DIN 2014, or Arial."))

    # Font size
    if size is None:
        checks.append(("WARN", "Could not detect Normal-style font size — inspect manually."))
    elif size == expected_body_size:
        label = "12pt (Medicare)" if args.medicare else "11pt"
        checks.append(("PASS", f"Body size is {size:g}pt ({label})."))
    else:
        label = "12pt" if args.medicare else "11pt"
        checks.append(("FAIL", f"Body size is {size:g}pt — should be {label}."))

    # Line spacing
    if single_spaced:
        checks.append(("PASS", "Document is single-spaced (1.0)."))
    else:
        checks.append(("FAIL", "Document is not single-spaced."))

    # Margins
    if margins is None:
        checks.append(("WARN", "Could not detect page margins — inspect manually."))
    else:
        margin_ok = all(margins.get(k) == v for k, v in TARGET_MARGIN_TWIPS.items())
        if margin_ok:
            checks.append(("PASS", 'Margins are 1" top/bottom, 1.25" left/right.'))
        else:
            def twips_to_inches(t):
                return f"{t/1440:.2f}\""
            got = {k: twips_to_inches(v) for k, v in margins.items()}
            want = {k: twips_to_inches(v) for k, v in TARGET_MARGIN_TWIPS.items()}
            checks.append(("FAIL", f"Margins {got} — should be {want}."))

    # Alignment
    if left_aligned:
        checks.append(("PASS", "Body text is left-justified (no centered or right-aligned paragraphs)."))
    else:
        checks.append(("FAIL", "Found centered or right-aligned paragraphs — body must be left-justified."))

    # Logo on page one
    if logo_present:
        checks.append(("PASS", "Header with embedded image present (logo likely on page one)."))
    else:
        checks.append(("WARN", "No header or embedded image found — verify logo appears on page one."))

    # Service marks on Blue Cross brand name in body text
    if service_marks_ok:
        checks.append(("PASS", "Service mark (® or ℠) detected near a Blue Cross brand name."))
    else:
        checks.append(("WARN", "No ® or ℠ found near a Blue Cross brand name in the body text. Brand Style Guide (p. 2) requires the registration indicia on the first or most-prominent appearance — verify that header/logo coverage is sufficient."))

    # "over" word on multi-page letters
    if over_word_ok is None:
        checks.append(("PASS", 'Single-page letter — "over" check not applicable.'))
    elif over_word_ok:
        checks.append(("PASS", 'Multi-page letter includes the word "over" to direct the reader.'))
    else:
        checks.append(("FAIL", 'Multi-page letter is missing the word "over" — required by the Letter Checklist (Writing & Tone Guide, p. 24).'))

    # Signature block presence
    if signature_ok:
        checks.append(("PASS", 'Closing detected (e.g., "Sincerely,") — signature block present.'))
    else:
        checks.append(("WARN", 'No standard closing (Sincerely / Thank you / Regards / Best / Warmly / Respectfully) found near the end. Verify a signature block is present.'))

    # Independent Licensee tagline presence (Brand Style Guide p. 1, 3)
    if independent_licensee_ok:
        checks.append(("PASS", 'Independent Licensee tagline present (body, header, or footer).'))
    else:
        checks.append(("FAIL", 'Independent Licensee tagline missing — Brand Style Guide (Oct 2025, p. 1, 3) requires "An Independent Licensee of the Blue Cross and Blue Shield Association" somewhere on the document (body, header, or footer).'))

    # Render
    pass_count = sum(1 for s, _ in checks if s == "PASS")
    fail_count = sum(1 for s, _ in checks if s == "FAIL")

    icons = {"PASS": "✓", "FAIL": "✗", "WARN": "!"}
    print(f"Letter Checklist — {path.name}")
    print("=" * 60)
    for status, msg in checks:
        print(f"  {icons[status]} {msg}")
    print("-" * 60)
    print(f"  {pass_count} pass, {fail_count} fail, {len(checks) - pass_count - fail_count} warn")

    sys.exit(1 if fail_count else 0)


if __name__ == "__main__":
    main()
