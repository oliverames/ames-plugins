#!/usr/bin/env python3
"""
Build a BCBS memo .docx by cloning a Word exemplar and letting pandoc fill
the body from markdown.

This is the right tool when Oliver names a specific reference file
("use the Gap Analysis Memo", "clone the V2 strategy memo"). The exemplar
carries all the non-style visuals — the graphic header band, page
dimensions, footer, fonts — and pandoc's --reference-doc mechanism
preserves them automatically. Named references override the skill's default
template; never silently substitute the default for a named reference.

Usage:
    python3 clone-exemplar.py \\
        --exemplar <path.docx> \\
        --markdown <path.md> \\
        --output <path.docx> \\
        [--banner-title "EXAMPLE TITLE"] \\
        [--tight-bullets]

When --banner-title is supplied, word/header1.xml in the output is patched so
the banner text reads the new title instead of the exemplar's placeholder
(e.g. "PROPOSAL MEMO" for the bundled Proposal Report exemplar). The text
lives twice in header1.xml — once in <wps:txbx> (modern Word) and once in
<mc:Fallback><v:textbox> (legacy VML). Both get rewritten.

When --tight-bullets is supplied, every level-0 abstractNum entry in
word/numbering.xml is rewritten to left=360, hanging=180. Pandoc appends
its own numbering entries for lists it sees in the markdown, at the
Word-default left=720 hanging=360, which looks loose in a memo. The flag
enforces the tighter V2-style bullet indent across both exemplar-provided
and pandoc-appended entries.

Returns non-zero if pandoc is missing, the exemplar doesn't look like a
pandoc reference-doc (no Title/Heading1 styles), or any step fails.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

REQUIRED_PANDOC_STYLES = ("Title", "Subtitle", "Heading1", "FirstParagraph")

# Banner placeholders the bundled exemplar(s) use. If the exemplar was built
# by build-exemplar-memo.py, the placeholder is "PROPOSAL MEMO".
KNOWN_BANNER_PLACEHOLDERS = (
    "PROPOSAL MEMO",
)


def check_pandoc() -> None:
    if shutil.which("pandoc") is None:
        raise SystemExit("pandoc not on PATH — install with `brew install pandoc`")


def check_exemplar_has_styles(exemplar: Path) -> None:
    """Warn (but don't hard-fail) if the exemplar is missing styles pandoc emits."""
    try:
        with zipfile.ZipFile(exemplar, "r") as z:
            styles = z.read("word/styles.xml").decode("utf-8", errors="replace")
    except (KeyError, zipfile.BadZipFile) as exc:
        raise SystemExit(f"exemplar {exemplar} is not a valid .docx: {exc}")

    missing = [
        s for s in REQUIRED_PANDOC_STYLES
        if f'w:styleId="{s}"' not in styles
    ]
    if missing:
        print(
            f"warning: exemplar {exemplar.name} is missing styles that pandoc "
            f"will emit: {', '.join(missing)}. These paragraphs will fall back "
            f"to Normal. Consider running build-exemplar-memo.py (or equivalent) "
            f"to augment the exemplar's style set.",
            file=sys.stderr,
        )


def run_pandoc(markdown: Path, output: Path, exemplar: Path) -> None:
    cmd = [
        "pandoc",
        str(markdown),
        "-o", str(output),
        "--reference-doc", str(exemplar),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(
            f"pandoc failed (exit {result.returncode}):\n{result.stderr}"
        )


def force_tight_bullets(output: Path) -> None:
    """Rewrite every level-0 abstractNum ind to left=360 hanging=180.

    Pandoc appends new abstractNum entries for lists it finds in the markdown,
    at the Word-default left=720 hanging=360 — looser than the V2 memo bullet.
    This pass closes that gap so every bullet in the output indents tightly,
    regardless of whether it's mapped to an exemplar-provided numbering entry
    or a pandoc-appended one.
    """
    with zipfile.ZipFile(output, "r") as z:
        try:
            numbering = z.read("word/numbering.xml").decode("utf-8")
        except KeyError:
            return  # no numbering part, nothing to patch
        other_contents = {
            n: z.read(n) for n in z.namelist() if n != "word/numbering.xml"
        }

    # Replace ind within every <w:lvl w:ilvl="0"> block. Use a regex that
    # tolerates attribute order / whitespace variations lxml re-serializes.
    def patch_lvl(match: "re.Match[str]") -> str:
        block = match.group(0)
        new_ind = '<w:ind w:left="360" w:hanging="180"/>'
        if re.search(r"<w:ind\b[^/]*/>", block):
            block = re.sub(r"<w:ind\b[^/]*/>", new_ind, block)
        else:
            # No ind at all — wrap/create pPr.
            if "<w:pPr>" in block:
                block = block.replace("<w:pPr>", f"<w:pPr>{new_ind}", 1)
            else:
                block = block.replace(">", f"><w:pPr>{new_ind}</w:pPr>", 1)
        return block

    patched = re.sub(
        r'<w:lvl\b[^>]*w:ilvl="0"[^>]*>.*?</w:lvl>',
        patch_lvl,
        numbering,
        flags=re.DOTALL,
    )

    tmp = output.with_suffix(".docx.tmp")
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as z_out:
        with zipfile.ZipFile(output, "r") as src:
            for info in src.infolist():
                if info.filename == "word/numbering.xml":
                    z_out.writestr(info, patched.encode("utf-8"))
                else:
                    z_out.writestr(info, other_contents[info.filename])
    tmp.replace(output)


def replace_banner_title(output: Path, new_title: str) -> None:
    """Rewrite banner text in word/header1.xml.

    We look for any known banner placeholder string and substitute it. If none
    of the placeholders are present, the exemplar's banner may already carry
    real content; in that case we surface an error rather than guessing at
    which text to replace.
    """
    with zipfile.ZipFile(output, "r") as z:
        try:
            header = z.read("word/header1.xml").decode("utf-8")
        except KeyError:
            raise SystemExit(
                "output has no word/header1.xml — exemplar may not have a "
                "header part; --banner-title is not meaningful here"
            )
        other_names = [n for n in z.namelist() if n != "word/header1.xml"]
        others = {n: z.read(n) for n in other_names}

    placeholder_found = None
    for placeholder in KNOWN_BANNER_PLACEHOLDERS:
        if placeholder in header:
            placeholder_found = placeholder
            break

    if placeholder_found is None:
        raise SystemExit(
            f"could not find a known banner placeholder in header1.xml. "
            f"Known placeholders: {KNOWN_BANNER_PLACEHOLDERS}. Rebuild the "
            f"exemplar with a known placeholder, or omit --banner-title."
        )

    new_header = header.replace(placeholder_found, new_title)

    # Re-write the zip with the patched header.
    tmp = output.with_suffix(".docx.tmp")
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as z:
        # Preserve original order + compression settings where we can.
        with zipfile.ZipFile(output, "r") as src:
            for info in src.infolist():
                if info.filename == "word/header1.xml":
                    z.writestr(info, new_header.encode("utf-8"))
                else:
                    z.writestr(info, others[info.filename])
    tmp.replace(output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exemplar", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--banner-title",
        help="rewrite the exemplar's header-banner title text in the output",
    )
    parser.add_argument(
        "--tight-bullets",
        action="store_true",
        help="force all level-0 numbering entries to left=360 hanging=180",
    )
    args = parser.parse_args()

    if not args.exemplar.exists():
        raise SystemExit(f"exemplar not found: {args.exemplar}")
    if not args.markdown.exists():
        raise SystemExit(f"markdown not found: {args.markdown}")

    check_pandoc()
    check_exemplar_has_styles(args.exemplar)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    run_pandoc(args.markdown, args.output, args.exemplar)

    if args.banner_title:
        replace_banner_title(args.output, args.banner_title)

    if args.tight_bullets:
        force_tight_bullets(args.output)

    size = args.output.stat().st_size
    print(f"Wrote {args.output} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
