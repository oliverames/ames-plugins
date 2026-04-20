#!/usr/bin/env python3
"""
BCBS VT Proposal Report Reference-Doc Builder

Builds ``data/letterhead/assets/reference-proposal-report.docx`` from the
authoritative Blue Cross VT Proposal Report Portrait Template
(``proposal-report-template.dotx``). This is the **opt-in** reference doc
for formal reports, proposals, and strategy decks.

For everyday letters and short-form letterhead, use the default
``reference.docx`` produced by ``style-reference-doc.py``.

### Design principle: preserve the official template

The ``.dotx`` is already official brand material. This script treats it as
canonical and is deliberately non-destructive:

- Margins are not changed — the template sets 1" on all sides.
- Styles the template already defines (Normal, Heading 1, Header, Footer,
  ListParagraph) are NOT modified.
- Only styles pandoc needs that the template does NOT define (Heading 2-4,
  Title, Author, Date, Body Text, Caption, Intense Quote) are added, styled
  to match the template's existing palette.
- A centered "Independent Licensee" footer is added because the template
  defines the Footer style but ships with an empty footer part — every page
  of an official document should carry the required disclosure.
- The placeholder body is stripped so pandoc can fill in real content.

Usage: python3 style-proposal-report.py
Requires: pip install python-docx
"""

import io
import sys
import zipfile
from pathlib import Path

try:
    from docx import Document
    from docx.enum.style import WD_STYLE_TYPE
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Pt, RGBColor
except ImportError:
    print("Error: python-docx not installed.")
    print("Run: pip install python-docx")
    sys.exit(1)


# --- BCBS VT brand palette (2025-10 Brand Style Guide) ---
# Used only for the styles we ADD; the template's own styles are left alone.
BLUE_CROSS_VT_BLUE = RGBColor(0x00, 0x77, 0xC8)  # PMS 3005 C
WEB_DARK_BLUE      = RGBColor(0x00, 0x46, 0x7B)  # H1/Title emphasis
DARK_GRAY          = RGBColor(0x63, 0x66, 0x6A)  # Cool Gray 10 C
BLACK              = RGBColor(0x1A, 0x1A, 0x1A)
SOFT_GRAY          = RGBColor(0x66, 0x66, 0x66)

# --- Typography for added styles only ---
# Matches the authoritative Writing and Tone Style Guide (Calibri/DIN 2014/Arial).
BODY_FONT    = "Calibri"
HEADING_FONT = "Arial"

SCRIPT_DIR  = Path(__file__).parent
ASSETS_DIR  = SCRIPT_DIR.parent / "assets"
SOURCE_DOTX = ASSETS_DIR / "proposal-report-template.dotx"
OUTPUT_PATH = ASSETS_DIR / "reference-proposal-report.docx"


def dotx_to_docx_bytes(dotx_path):
    """Rewrite the .dotx package as a .docx package (bytes).

    Swaps the single content-type override for ``word/document.xml`` from
    ``...template.main+xml`` to ``...document.main+xml``. All other parts —
    header, footer, media, styles, theme, settings — are copied verbatim.
    """
    template_ct = (
        "application/vnd.openxmlformats-officedocument."
        "wordprocessingml.template.main+xml"
    )
    document_ct = (
        "application/vnd.openxmlformats-officedocument."
        "wordprocessingml.document.main+xml"
    )
    out_buf = io.BytesIO()
    with zipfile.ZipFile(dotx_path, "r") as zin:
        with zipfile.ZipFile(out_buf, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == "[Content_Types].xml":
                    data = data.replace(
                        template_ct.encode("utf-8"),
                        document_ct.encode("utf-8"),
                    )
                zout.writestr(item, data)
    return out_buf.getvalue()


def strip_placeholder_body(doc):
    """Remove the .dotx placeholder body so pandoc fills in real content."""
    body = doc.element.body
    for child in list(body):
        tag = child.tag.rsplit("}", 1)[-1]
        if tag in ("p", "tbl"):
            body.remove(child)
    doc.add_paragraph()


def add_style_if_missing(doc, name, font_name, size_pt, *, bold=False,
                         color=None, space_before=None, space_after=None):
    """Add a paragraph style IF the template doesn't already define it.

    If the style already exists (i.e. the official template defines it),
    this function is a no-op — the template's styling is authoritative.
    """
    try:
        doc.styles[name]
        print(f"  — kept:  {name:20s} (already defined in official template)")
        return
    except KeyError:
        pass

    style = doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
    font = style.font
    font.name = font_name
    font.size = Pt(size_pt)
    font.bold = bold
    if color is not None:
        font.color.rgb = color

    pf = style.paragraph_format
    if space_before is not None:
        pf.space_before = Pt(space_before)
    if space_after is not None:
        pf.space_after = Pt(space_after)

    print(f"  ✓ added: {name:20s} ({font_name} {size_pt}pt)")


def set_footer_if_empty(doc, text):
    """Write the Independent Licensee disclosure to every empty section footer.

    The template defines the Footer style but ships with no footer text.
    This fills in the required disclosure without overwriting any pre-
    existing footer content.
    """
    for section in doc.sections:
        footer = section.footer
        # If the template already has footer text, leave it alone.
        existing = "".join(p.text for p in footer.paragraphs).strip()
        if existing:
            print(f"  — footer already populated; leaving untouched")
            continue
        footer.is_linked_to_previous = False
        if footer.paragraphs:
            p = footer.paragraphs[0]
        else:
            p = footer.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.font.name = BODY_FONT
        run.font.size = Pt(8)
        run.font.color.rgb = SOFT_GRAY
        print(f"  ✓ footer added (centered, 8pt Calibri)")


def main():
    print("BCBS VT Proposal Report Reference-Doc Builder")
    print("=" * 50)
    print("(Non-destructive: preserves the official template's margins,")
    print(" Normal, Heading 1, Header, Footer, and ListParagraph styles.)")

    if not SOURCE_DOTX.exists():
        print(f"\nError: source template missing: {SOURCE_DOTX}")
        sys.exit(1)

    print(f"\nSource template: {SOURCE_DOTX.name}")
    docx_bytes = dotx_to_docx_bytes(SOURCE_DOTX)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_bytes(docx_bytes)
    print(f"  ✓ Package converted: .dotx → .docx")

    doc = Document(str(OUTPUT_PATH))

    print("\nStripping placeholder body content...")
    strip_placeholder_body(doc)

    print("\nAdding styles pandoc needs (only if missing)...")
    # Normal and Heading 1 are defined in the template — do NOT touch.
    add_style_if_missing(doc, "Normal", BODY_FONT, 11, color=BLACK,
                         space_after=6)
    add_style_if_missing(doc, "Heading 1", HEADING_FONT, 24, bold=True,
                         color=WEB_DARK_BLUE, space_before=12, space_after=6)
    # These are generally NOT in the template and will be added:
    add_style_if_missing(doc, "Heading 2", HEADING_FONT, 18, bold=True,
                         color=BLUE_CROSS_VT_BLUE,
                         space_before=10, space_after=4)
    add_style_if_missing(doc, "Heading 3", HEADING_FONT, 14, bold=True,
                         color=BLUE_CROSS_VT_BLUE,
                         space_before=8, space_after=4)
    add_style_if_missing(doc, "Heading 4", HEADING_FONT, 12, bold=True,
                         color=BLUE_CROSS_VT_BLUE,
                         space_before=6, space_after=2)
    add_style_if_missing(doc, "Title", HEADING_FONT, 28, bold=True,
                         color=WEB_DARK_BLUE, space_before=0, space_after=4)
    add_style_if_missing(doc, "Author", BODY_FONT, 11, color=DARK_GRAY,
                         space_after=2)
    add_style_if_missing(doc, "Date", BODY_FONT, 11, color=DARK_GRAY,
                         space_after=12)
    add_style_if_missing(doc, "Body Text", BODY_FONT, 11, color=BLACK,
                         space_after=6)
    add_style_if_missing(doc, "Caption", BODY_FONT, 10, color=DARK_GRAY)
    add_style_if_missing(doc, "Intense Quote", BODY_FONT, 11,
                         color=BLUE_CROSS_VT_BLUE,
                         space_before=8, space_after=8)

    print("\nMargins: untouched (template sets 1\" all sides).")

    print("\nPopulating footer with Independent Licensee disclosure...")
    footer_text = (
        "Blue Cross and Blue Shield of Vermont is an independent licensee "
        "of the Blue Cross and Blue Shield Association.  |  "
        "bluecrossvt.org  |  Berlin, Vermont"
    )
    set_footer_if_empty(doc, footer_text)

    doc.save(str(OUTPUT_PATH))
    print(f"\n✓ Saved: {OUTPUT_PATH}")
    print()
    print("Use with: build-letterhead.sh --template=proposal-report input.md [output.docx]")


if __name__ == "__main__":
    main()
