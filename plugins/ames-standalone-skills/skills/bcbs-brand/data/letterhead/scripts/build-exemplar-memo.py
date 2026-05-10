#!/usr/bin/env python3
"""
Regenerate data/letterhead/assets/exemplar-proposal-report-memo.docx
from the canonical BCBS Proposal Report memo exemplar (the strategy memo).

The exemplar is the gold-standard "memo in Proposal Report Portrait family"
that clone-exemplar.py / build-letterhead.sh use as pandoc's --reference-doc
for memo-style outputs. It carries:

- The graphic header band (preserved byte-for-byte from the source memo because
  word/media and word/header1.xml are copied untouched by zipfile round-trip).
- The Independent Licensee footer.
- Letter page size with 1" top, 1" left/right, 0.5" bottom margins and
  0.5" header distance — matching the source memo verbatim.
- Paragraph styles Title (15pt bold navy #00355E), Subtitle (8pt italic gray
  #595959), Heading1 (ALL-CAPS navy on light-blue band), FirstParagraph
  (9pt black body), BlockText (callout box, pale-blue #EBF4FA fill,
  navy #00355E left border). These are what pandoc emits.
- Normal with 9pt default run size so body paragraphs render at the source's
  actual body size, not the 10pt default.

The body content is a minimal sanitized skeleton so the file is useful when
opened in Word for reference, but ships no BCBS-specific material. The header
banner title (which lives as real text in header1.xml, **twice** — once in
<wps:txbx> and once in the <mc:Fallback><v:textbox> legacy-Word construct),
the docProps/core.xml metadata (title/subject/creator), and the ListParagraph
bullet indent (the source ships with 720-twip indent and a level-0 numbering
entry that has no ind pPr, producing huge bullet tabs) are all sanitized /
fixed here.

Source is the private strategy memo on Oliver's disk; the script sanitizes
before bundling, so the output can safely live in the public ames-claude
marketplace.
"""
from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

from lxml import etree  # type: ignore[import-not-found]

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NSMAP = {"w": W_NS}


def w(tag: str) -> str:
    return f"{{{W_NS}}}{tag}"


DEFAULT_SOURCE = Path(
    "/Users/oliverames/Documents/BCBS/Projects/"
    "Digital Infrastructure Strategy/"
    "BCBS Digital Infrastructure Strategy Memo.docx"
)

DEFAULT_TARGET = (
    Path(__file__).resolve().parents[1]
    / "assets"
    / "exemplar-proposal-report-memo.docx"
)


SANITIZED_BODY_XML = """\
<w:body xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:p>
    <w:pPr><w:pStyle w:val="Title"/></w:pPr>
    <w:r><w:t xml:space="preserve">Proposal: [Short descriptive title]</w:t></w:r>
  </w:p>
  <w:p>
    <w:pPr><w:pStyle w:val="Subtitle"/></w:pPr>
    <w:r><w:t xml:space="preserve">[Team name] | Prepared by [Author] | [Absolute date]</w:t></w:r>
  </w:p>
  <w:p>
    <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
    <w:r><w:t xml:space="preserve">Example Section</w:t></w:r>
  </w:p>
  <w:p>
    <w:pPr><w:pStyle w:val="FirstParagraph"/></w:pPr>
    <w:r><w:t xml:space="preserve">This is the body paragraph style. Calibri 9pt black, single-column, 1.15 line spacing. Replace this text when you author a memo against this exemplar; the pandoc pipeline does this automatically when you run build-letterhead.sh with --exemplar.</w:t></w:r>
  </w:p>
  <w:p>
    <w:pPr><w:pStyle w:val="BlockText"/></w:pPr>
    <w:r><w:t xml:space="preserve">This is the callout / intense-quote style. Pale blue #EBF4FA fill with a navy #00355E left border. Use markdown &gt; to emit it.</w:t></w:r>
  </w:p>
  <w:sectPr>
    <w:headerReference w:type="default" r:id="rId12"/>
    <w:footerReference w:type="default" r:id="rId13"/>
    <w:pgSz w:w="12240" w:h="15840" w:code="1"/>
    <w:pgMar w:top="1440" w:right="1440" w:bottom="720" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/>
    <w:cols w:space="720"/>
    <w:docGrid w:linePitch="360"/>
  </w:sectPr>
</w:body>
"""


STYLE_FRAGMENTS = {
    # Title: 15pt bold navy #00355E, after=40
    "Title": """<w:style xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:uiPriority w:val="10"/><w:qFormat/><w:pPr><w:spacing w:before="0" w:after="40" w:line="259" w:lineRule="auto"/></w:pPr><w:rPr><w:b/><w:color w:val="00355E"/><w:sz w:val="30"/><w:szCs w:val="30"/></w:rPr></w:style>""",
    # Subtitle: 8pt italic gray #595959, after=80
    "Subtitle": """<w:style xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:uiPriority w:val="11"/><w:qFormat/><w:pPr><w:spacing w:before="0" w:after="80" w:line="259" w:lineRule="auto"/></w:pPr><w:rPr><w:i/><w:color w:val="595959"/><w:sz w:val="16"/><w:szCs w:val="16"/></w:rPr></w:style>""",
    # FirstParagraph: inherits from Normal (9pt body, see Normal rPr patch).
    "FirstParagraph": """<w:style xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:type="paragraph" w:styleId="FirstParagraph"><w:name w:val="First Paragraph"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:uiPriority w:val="1"/><w:qFormat/><w:pPr><w:spacing w:before="0" w:after="80" w:line="259" w:lineRule="auto"/></w:pPr></w:style>""",
    # BlockText: pale-blue #EBF4FA fill, navy #00355E left border 12pt, navy italic body
    "BlockText": """<w:style xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:type="paragraph" w:styleId="BlockText"><w:name w:val="Block Text"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:uiPriority w:val="9"/><w:qFormat/><w:pPr><w:pBdr><w:left w:val="single" w:sz="24" w:space="8" w:color="00355E"/></w:pBdr><w:shd w:val="clear" w:color="auto" w:fill="EBF4FA"/><w:spacing w:before="80" w:after="120" w:line="259" w:lineRule="auto"/><w:ind w:left="240"/></w:pPr><w:rPr><w:i/><w:color w:val="00355E"/></w:rPr></w:style>""",
    # Compact: tight-spacing style pandoc applies to list items. Without this
    # defined, pandoc bullets fall back to Normal and inherit its
    # before=100 after=200 spacing — noticeable air between bullets.
    "Compact": """<w:style xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:type="paragraph" w:styleId="Compact"><w:name w:val="Compact"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:uiPriority w:val="2"/><w:qFormat/><w:pPr><w:spacing w:before="0" w:after="0" w:line="276" w:lineRule="auto"/></w:pPr></w:style>""",
    # Table: table-style pandoc references via <w:tblStyle val="Table"/>. Mirrors
    # the one style-proposal-report.py injects into the report reference doc:
    # BCBS gray #BFBFBF gridlines, bold-navy first-row header on light-blue
    # #E6F2FA shading, 9pt Calibri (sz=20 half-points), tight cell padding.
    "Table": """<w:style xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:type="table" w:styleId="Table"><w:name w:val="Table"/><w:basedOn w:val="TableNormal"/><w:uiPriority w:val="59"/><w:qFormat/><w:pPr><w:spacing w:before="40" w:after="40" w:line="240" w:lineRule="auto"/></w:pPr><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:cs="Calibri"/><w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr><w:tblPr><w:tblBorders><w:top w:val="single" w:sz="4" w:space="0" w:color="BFBFBF"/><w:left w:val="single" w:sz="4" w:space="0" w:color="BFBFBF"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="BFBFBF"/><w:right w:val="single" w:sz="4" w:space="0" w:color="BFBFBF"/><w:insideH w:val="single" w:sz="4" w:space="0" w:color="BFBFBF"/><w:insideV w:val="single" w:sz="4" w:space="0" w:color="BFBFBF"/></w:tblBorders><w:tblCellMar><w:top w:w="80" w:type="dxa"/><w:left w:w="120" w:type="dxa"/><w:bottom w:w="80" w:type="dxa"/><w:right w:w="120" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblStylePr w:type="firstRow"><w:rPr><w:b/><w:color w:val="00355E"/></w:rPr><w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="E6F2FA"/></w:tcPr></w:tblStylePr></w:style>""",
}


def ensure_body_replaced(document_xml: bytes) -> bytes:
    """Strip the source body and replace with the sanitized skeleton."""
    tree = etree.fromstring(document_xml)
    body = tree.find(w("body"))
    if body is None:
        raise SystemExit("document.xml has no <w:body> — unexpected source shape")

    parent = body.getparent()
    idx = parent.index(body)
    new_body = etree.fromstring(SANITIZED_BODY_XML)
    parent.remove(body)
    parent.insert(idx, new_body)

    return etree.tostring(tree, xml_declaration=True, encoding="UTF-8", standalone=True)


def ensure_styles_patched(styles_xml: bytes) -> bytes:
    """Inject pandoc-expected styles if absent; patch Normal to 9pt body."""
    tree = etree.fromstring(styles_xml)
    root = tree  # <w:styles>

    existing = {
        s.get(w("styleId"))
        for s in root.findall(w("style"))
    }

    for style_id, fragment in STYLE_FRAGMENTS.items():
        if style_id in existing:
            continue
        root.append(etree.fromstring(fragment))

    # Patch Normal: set default run size to 18 half-points (9pt) so body
    # text inherits 9pt without direct-formatting on every run.
    for style in root.findall(w("style")):
        if style.get(w("styleId")) != "Normal":
            continue
        rpr = style.find(w("rPr"))
        if rpr is None:
            rpr = etree.SubElement(style, w("rPr"))
        # Remove any existing sz / szCs and add canonical 18 half-point pair
        for sz_tag in ("sz", "szCs"):
            for existing_sz in rpr.findall(w(sz_tag)):
                rpr.remove(existing_sz)
        sz = etree.SubElement(rpr, w("sz"))
        sz.set(w("val"), "18")
        sz_cs = etree.SubElement(rpr, w("szCs"))
        sz_cs.set(w("val"), "18")
        break

    return etree.tostring(tree, xml_declaration=True, encoding="UTF-8", standalone=True)


BANNER_PLACEHOLDER = "PROPOSAL MEMO"

# Any string that appears in header1.xml as banner text on the source and
# must be scrubbed before shipping. Keep exact so we don't over-replace.
BANNER_SOURCE_STRINGS = (
    "Digital Infrastructure Strategy",
)


def sanitize_banner(header_xml: bytes) -> bytes:
    """Replace banner title text (in both wps:txbx and mc:Fallback v:textbox)."""
    text = header_xml.decode("utf-8")
    for src in BANNER_SOURCE_STRINGS:
        text = text.replace(src, BANNER_PLACEHOLDER)
    return text.encode("utf-8")


EXEMPLAR_AUTHOR = "Oliver Ames"


def sanitize_core(core_xml: bytes) -> bytes:
    """Replace identifying metadata with author + generic placeholders.

    Title/subject get placeholder strings (pandoc overwrites these from YAML
    front matter on per-memo builds; standalone, the exemplar shows
    "[Memo Title]" in Word's File → Properties). Creator stays as Oliver
    because this exemplar is his — bundled in his public marketplace — and
    showing "Oliver Ames" in File → Properties is the right attribution.
    On per-memo pandoc builds, pandoc clears dc:creator unless the markdown
    YAML sets `author:`; attribute downstream memos by setting that field.
    """
    import re as _re

    text = core_xml.decode("utf-8")
    replacements = {
        "title": "[Memo Title]",
        "subject": "[Memo Subject]",
        "creator": EXEMPLAR_AUTHOR,
        "lastModifiedBy": EXEMPLAR_AUTHOR,
        "description": "",
    }
    for tag, value in replacements.items():
        text = _re.sub(
            rf"<(dc:|cp:)?{tag}>[^<]*</(dc:|cp:)?{tag}>",
            lambda m, v=value, t=tag: f"<{m.group(1) or ''}{t}>{v}</{m.group(2) or ''}{t}>",
            text,
        )
    return text.encode("utf-8")


def sanitize_app(app_xml: bytes) -> bytes:
    """Reset stale page/word counters that the source carried in docProps/app.xml.

    Pandoc rewrites app.xml with fresh counts on per-memo builds, but the
    bundled exemplar opened standalone in Word would otherwise show the source's
    "Pages: 6, Words: 2635, Characters: 15021" — misleading because the
    exemplar body is ~1 page of placeholder content. Word recalculates
    these counters on first save, so zeros are fine as a starting state.
    """
    import re as _re

    text = app_xml.decode("utf-8")
    for tag in ("TotalTime", "Pages", "Words", "Characters",
                "Lines", "Paragraphs", "CharactersWithSpaces"):
        text = _re.sub(
            rf"<{tag}>[^<]*</{tag}>",
            f"<{tag}>0</{tag}>",
            text,
        )
    # Pages should be at least 1 to render sensibly in File → Properties.
    text = _re.sub(r"<Pages>0</Pages>", "<Pages>1</Pages>", text)
    return text.encode("utf-8")


def fix_bullet_indent(styles_xml: bytes) -> bytes:
    """Patch ListParagraph from 720-twip indent to 360 left with 180 hanging.

    The source memo (and reference-proposal-report.docx) ship with a 0.5" left indent on
    ListParagraph AND level-0 numbering entries that lack pPr/ind, so bullets
    render with a huge tab between the dash and the text. Pulling the style
    indent in to 360 with a 180-twip hanging gives the visually tight bullet
    most memos actually want.
    """
    tree = etree.fromstring(styles_xml)
    for style in tree.findall(w("style")):
        if style.get(w("styleId")) != "ListParagraph":
            continue
        ppr = style.find(w("pPr"))
        if ppr is None:
            ppr = etree.SubElement(style, w("pPr"))
        for existing in ppr.findall(w("ind")):
            ppr.remove(existing)
        ind = etree.SubElement(ppr, w("ind"))
        ind.set(w("left"), "360")
        ind.set(w("hanging"), "180")
        break
    return etree.tostring(tree, xml_declaration=True, encoding="UTF-8", standalone=True)


def fix_numbering_indent(numbering_xml: bytes) -> bytes:
    """Ensure every level-0 entry has pPr/ind with left=360 hanging=180.

    Without this, Word uses the ListParagraph 720 indent and inserts a huge
    tab between the bullet glyph and the text. Parallel to fix_bullet_indent
    at the style layer.
    """
    tree = etree.fromstring(numbering_xml)
    for lvl in tree.iter(w("lvl")):
        if lvl.get(w("ilvl")) != "0":
            continue
        ppr = lvl.find(w("pPr"))
        if ppr is None:
            ppr = etree.SubElement(lvl, w("pPr"))
        existing_ind = ppr.find(w("ind"))
        if existing_ind is not None:
            # Respect authored indent if present and sane (<=480).
            left_val = existing_ind.get(w("left"), "0")
            try:
                left_int = int(left_val)
            except ValueError:
                left_int = 0
            if left_int <= 480:
                continue
            ppr.remove(existing_ind)
        ind = etree.SubElement(ppr, w("ind"))
        ind.set(w("left"), "360")
        ind.set(w("hanging"), "180")
    return etree.tostring(tree, xml_declaration=True, encoding="UTF-8", standalone=True)


def build(source: Path, target: Path) -> None:
    if not source.exists():
        raise SystemExit(f"source memo not found at {source}")

    target.parent.mkdir(parents=True, exist_ok=True)

    # Write to a temp path then atomically replace target
    tmp = target.with_suffix(".docx.tmp")
    if tmp.exists():
        tmp.unlink()

    with zipfile.ZipFile(source, "r") as src_zip, zipfile.ZipFile(
        tmp, "w", compression=zipfile.ZIP_DEFLATED
    ) as out_zip:
        for info in src_zip.infolist():
            data = src_zip.read(info.filename)
            if info.filename == "word/document.xml":
                data = ensure_body_replaced(data)
            elif info.filename == "word/styles.xml":
                data = ensure_styles_patched(data)
                data = fix_bullet_indent(data)
            elif info.filename == "word/numbering.xml":
                data = fix_numbering_indent(data)
            elif info.filename == "word/header1.xml":
                data = sanitize_banner(data)
            elif info.filename == "docProps/core.xml":
                data = sanitize_core(data)
            elif info.filename == "docProps/app.xml":
                data = sanitize_app(data)
            out_zip.writestr(info, data)

    tmp.replace(target)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help=f"strategy memo on disk (default: {DEFAULT_SOURCE})",
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=DEFAULT_TARGET,
        help=f"output path (default: {DEFAULT_TARGET})",
    )
    args = parser.parse_args()

    build(args.source, args.target)
    size = args.target.stat().st_size
    print(f"Wrote {args.target} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
