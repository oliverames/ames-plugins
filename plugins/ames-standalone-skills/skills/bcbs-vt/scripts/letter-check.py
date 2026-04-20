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


def body_is_left_aligned(document_xml: str) -> bool:
    """No paragraph in the body should have w:jc val=center/right/both."""
    # Count forbidden alignments.
    forbidden = re.findall(r'<w:jc w:val="(center|right|both)"', document_xml)
    return len(forbidden) == 0


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
