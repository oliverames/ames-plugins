#!/usr/bin/env python3
"""
BCBS VT Memo Format Checklist

Complements letter-check.py. Memos in the Proposal Report Portrait family
run at a different scale than the formal Letter Checklist expects (9pt body
vs 11pt, 1" side margins vs 1.25", 0.5" bottom vs 1"). Running letter-check
on a memo fires "failures" that are actually correct conformance to the memo
template. This script is the one to use for those.

Checks a `.docx` built from the Proposal Report memo exemplar and reports
pass/fail for each mechanical item:

  [ ] word/header1.xml is present AND references an image relationship
      (the graphic header band rode along).
  [ ] The Title style is 15pt bold, color #00355E.
  [ ] The Subtitle style is 8pt italic, color #595959.
  [ ] Heading1 carries navy #00355E text on light-blue #99D6EA shading,
      ALL-CAPS.
  [ ] Normal run size is 9pt (half-points = 18).
  [ ] Page bottom margin is 720 twips (0.5").
  [ ] BlockText style, if present, has pale-blue #EBF4FA fill and navy
      #00355E left border.

Usage:
    python3 memo-check.py path/to/memo.docx

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


NAVY = "00355E"
LIGHT_BLUE_BAND = "99D6EA"
GRAY_SUBTITLE = "595959"
CALLOUT_FILL = "EBF4FA"
APPROVED_FONTS = {"Calibri", "DIN 2014", "Arial"}

# Brand Style Guide (Oct 2025, p. 1, 3) requires the Independent Licensee
# tagline somewhere on the document — body, header, or footer.
TAG_RX = re.compile(r"<[^>]+>")
INDEPENDENT_LICENSEE_PATTERN = re.compile(
    r"Independent\s+Licensee\s+of\s+the\s+Blue\s+Cross\s+and\s+Blue\s+Shield\s+Association",
    re.IGNORECASE,
)


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


def read_or_none(z: zipfile.ZipFile, name: str) -> str | None:
    try:
        return z.read(name).decode("utf-8", errors="replace")
    except KeyError:
        return None


def extract_style_block(styles_xml: str, style_id: str) -> str | None:
    m = re.search(
        rf'<w:style\b[^>]*w:styleId="{re.escape(style_id)}"[\s\S]*?</w:style>',
        styles_xml,
    )
    return m.group(0) if m else None


def find_attr(block: str, pattern: str) -> str | None:
    m = re.search(pattern, block)
    return m.group(1) if m else None


# ---------------------------------------------------------------------------

def check_header_has_image(z: zipfile.ZipFile) -> tuple[str, str]:
    header = read_or_none(z, "word/header1.xml")
    if header is None:
        return "FAIL", "word/header1.xml is missing — no header banner."
    rels = read_or_none(z, "word/_rels/header1.xml.rels")
    if rels is None:
        return "FAIL", "word/_rels/header1.xml.rels is missing — header has no rels."
    if 'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"' in rels:
        return "PASS", "Header banner graphic is present (image relationship found)."
    return "FAIL", "Header has no image relationship — the graphic banner was dropped."


def check_title_style(styles_xml: str) -> tuple[str, str]:
    block = extract_style_block(styles_xml, "Title")
    if block is None:
        return "FAIL", "Title style is not defined — pandoc titles will fall back to Normal."
    sz = find_attr(block, r'<w:sz w:val="(\d+)"')
    color = find_attr(block, r'<w:color w:val="([0-9A-Fa-f]{6})"')
    bold = "<w:b/>" in block or "<w:b " in block
    problems = []
    if sz != "30":
        problems.append(f"size is {sz}/2 pt, expected 15pt (sz=30)")
    if (color or "").upper() != NAVY:
        problems.append(f"color is #{color}, expected #{NAVY}")
    if not bold:
        problems.append("not bold")
    if problems:
        return "FAIL", "Title style: " + "; ".join(problems)
    return "PASS", "Title style is 15pt bold navy #00355E."


def check_subtitle_style(styles_xml: str) -> tuple[str, str]:
    block = extract_style_block(styles_xml, "Subtitle")
    if block is None:
        return "WARN", "Subtitle style is not defined — subtitles will fall back to Normal."
    sz = find_attr(block, r'<w:sz w:val="(\d+)"')
    color = find_attr(block, r'<w:color w:val="([0-9A-Fa-f]{6})"')
    italic = "<w:i/>" in block or "<w:i " in block
    problems = []
    if sz != "16":
        problems.append(f"size is {sz}/2 pt, expected 8pt (sz=16)")
    if (color or "").upper() != GRAY_SUBTITLE:
        problems.append(f"color is #{color}, expected #{GRAY_SUBTITLE}")
    if not italic:
        problems.append("not italic")
    if problems:
        return "FAIL", "Subtitle style: " + "; ".join(problems)
    return "PASS", "Subtitle style is 8pt italic gray #595959."


def check_heading1_band(styles_xml: str) -> tuple[str, str]:
    block = extract_style_block(styles_xml, "Heading1")
    if block is None:
        return "FAIL", "Heading1 style is not defined."
    color = find_attr(block, r'<w:color w:val="([0-9A-Fa-f]{6})"')
    fill = find_attr(block, r'<w:shd\b[^/]*w:fill="([0-9A-Fa-f]{6})"')
    caps = "<w:caps/>" in block or "<w:caps " in block
    problems = []
    if (color or "").upper() != NAVY:
        problems.append(f"color is #{color}, expected navy #{NAVY}")
    if (fill or "").upper() != LIGHT_BLUE_BAND:
        problems.append(f"band fill is #{fill}, expected #{LIGHT_BLUE_BAND}")
    if not caps:
        problems.append("no all-caps transform")
    if problems:
        return "FAIL", "Heading1: " + "; ".join(problems)
    return "PASS", "Heading1 is navy on light-blue band, ALL-CAPS."


def check_normal_body_size(styles_xml: str) -> tuple[str, str]:
    block = extract_style_block(styles_xml, "Normal")
    if block is None:
        return "FAIL", "Normal style is not defined — unexpected."
    sz = find_attr(block, r'<w:sz w:val="(\d+)"')
    if sz == "18":
        return "PASS", "Normal body size is 9pt (sz=18)."
    if sz is None:
        return "WARN", "Normal has no explicit size — memo body may default to 10pt."
    return "FAIL", f"Normal body size is {sz}/2 pt, expected 9pt (sz=18)."


def check_bottom_margin(document_xml: str) -> tuple[str, str]:
    m = re.search(r'<w:pgMar\b([^/]*)/>', document_xml)
    if not m:
        return "WARN", "No w:pgMar found — inspect margins manually."
    attrs = m.group(1)
    bottom = re.search(r'w:bottom="(\d+)"', attrs)
    if not bottom:
        return "WARN", "No bottom margin attribute — inspect manually."
    twips = int(bottom.group(1))
    if twips == 720:
        return "PASS", 'Bottom margin is 0.5" (720 twips).'
    return "FAIL", f'Bottom margin is {twips/1440:.2f}" ({twips} twips), expected 0.5".'


def check_normal_font(styles_xml: str) -> tuple[str, str]:
    """Verify the Normal style declares Calibri (or another approved font)."""
    block = extract_style_block(styles_xml, "Normal")
    if block is None:
        return "WARN", "Normal style is not defined — cannot verify font."
    font = find_attr(block, r'w:ascii="([^"]+)"')
    if font is None:
        return "WARN", "Normal style has no w:ascii font attribute — inspect manually."
    if font in APPROVED_FONTS:
        return "PASS", f"Normal font is {font} (approved: Calibri / DIN 2014 / Arial)."
    return "FAIL", f"Normal font is '{font}' — must be Calibri, DIN 2014, or Arial."


def check_independent_licensee(z: zipfile.ZipFile) -> tuple[str, str]:
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
    if INDEPENDENT_LICENSEE_PATTERN.search(combined):
        return "PASS", "Independent Licensee tagline present (body, header, or footer)."
    return "FAIL", 'Independent Licensee tagline missing — Brand Style Guide (Oct 2025, p. 1, 3) requires "An Independent Licensee of the Blue Cross and Blue Shield Association" somewhere on the document.'


def check_blocktext_callout(styles_xml: str) -> tuple[str, str]:
    block = extract_style_block(styles_xml, "BlockText")
    if block is None:
        return "WARN", "BlockText style absent — `> quote` callouts won't render."
    fill = find_attr(block, r'<w:shd\b[^/]*w:fill="([0-9A-Fa-f]{6})"')
    border = find_attr(
        block,
        r'<w:pBdr>[\s\S]*?<w:left\b[^/]*w:color="([0-9A-Fa-f]{6})"',
    )
    problems = []
    if (fill or "").upper() != CALLOUT_FILL:
        problems.append(f"fill is #{fill}, expected pale blue #{CALLOUT_FILL}")
    if (border or "").upper() != NAVY:
        problems.append(f"left border is #{border}, expected navy #{NAVY}")
    if problems:
        return "FAIL", "BlockText: " + "; ".join(problems)
    return "PASS", "BlockText callout: pale-blue fill, navy left border."


# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("docx", help="Path to the memo .docx to check.")
    args = ap.parse_args()

    path = Path(args.docx)
    z = load_docx(path)
    styles_xml = z.read("word/styles.xml").decode("utf-8", errors="replace")
    document_xml = z.read("word/document.xml").decode("utf-8", errors="replace")

    checks = [
        check_header_has_image(z),
        check_title_style(styles_xml),
        check_subtitle_style(styles_xml),
        check_heading1_band(styles_xml),
        check_normal_body_size(styles_xml),
        check_normal_font(styles_xml),
        check_bottom_margin(document_xml),
        check_blocktext_callout(styles_xml),
        check_independent_licensee(z),
    ]

    icons = {"PASS": "✓", "FAIL": "✗", "WARN": "!"}
    print(f"Memo Checklist — {path.name}")
    print("=" * 60)
    for status, msg in checks:
        print(f"  {icons[status]} {msg}")
    print("-" * 60)
    pass_count = sum(1 for s, _ in checks if s == "PASS")
    fail_count = sum(1 for s, _ in checks if s == "FAIL")
    warn_count = len(checks) - pass_count - fail_count
    print(f"  {pass_count} pass, {fail_count} fail, {warn_count} warn")

    sys.exit(1 if fail_count else 0)


if __name__ == "__main__":
    main()
