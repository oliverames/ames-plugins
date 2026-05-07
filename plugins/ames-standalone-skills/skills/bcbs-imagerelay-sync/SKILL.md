---
name: bcbs-imagerelay-sync
description: >
  Syncs a folder of downloaded ImageRelay files into the BCBS directory,
  mapping each file to its correct local counterpart and handling 1:1
  replacements, one-to-many splits (compilation → per-event files), and
  many-to-one consolidations (single guide → audience-specific variants).
when_to_use: >
  Triggers on: "sync imagerelay download", "update BCBS files from imagerelay",
  "I downloaded from imagerelay", "these are the final files from imagerelay",
  "imagerelay download", "update files from the download folder", or when
  Oliver hands over a Desktop folder named imagerelay-download-YYYY-MM-DD.
version: 1.0.0
---

# BCBS ImageRelay Sync

Moves final documents downloaded from ImageRelay into the correct locations
in `~/Documents/BCBS/`, resolving filename mismatches and handling structural
differences between the ImageRelay naming convention and BCBS local conventions.

## What this skill covers

ImageRelay uses hyphenated-lowercase filenames (`2026-Medicare-101-Social-Media-Plan.docx`).
The BCBS directory uses spaced names with en-dashes (`2026 Medicare 101 Social Media Plan - Revised 2026-04-23.docx`).
ImageRelay may combine content that lives in separate project folders locally
(compilation), or split a single local file into audience-specific variants.
This skill handles all three cases without manual renaming.

---

## Phase 0: Locate the download folder

The default drop location is `~/Desktop/imagerelay-download-YYYY-MM-DD/`.
If Oliver names the folder differently, use the path he provides.

```bash
ls ~/Desktop/imagerelay-download-*/
```

List the files. Note file sizes — they matter for verification later.

---

## Phase 1: Map each ImageRelay file to its local counterpart

For each file in the download folder, use **markitdown** to read its content,
then compare against the BCBS directory to find the matching local file.

```
mcp: markitdown → convert_to_markdown(uri="file:///path/to/desktop/file.docx")
```

Matching signals to check, in order:

1. **Name similarity** — strip hyphens and lowercase both sides for a fuzzy
   compare (e.g., `BCBS-Digital-Infrastructure-Strategy-Memo---V2` matches
   `BCBS Digital Infrastructure Strategy Memo - V2`).
2. **Content headings** — the first H1 in the file usually matches the local
   file's title or the document's main topic.
3. **File size ballpark** — local file should be within ~20% of the desktop
   file (desktop is usually slightly larger due to ImageRelay edits).

Use `find ~/Documents/BCBS -name "*.docx" -o -name "*.pptx"` to get the
local candidate list. Read any ambiguous local file with markitdown to confirm.

---

## Phase 2: Classify each mapping

**1:1 (direct replacement)** — one desktop file maps cleanly to one local file
with the same content domain. Most files fall here.

**Consolidation (many desktop → derived from one local)** — the local
directory had one file that was split into multiple audience variants for
ImageRelay. The desktop now has two files; the single local file should be
replaced by two properly named files.

Example: `Photo-Shoot-Appearance-Guide--Executive-Team-.docx` and
`Photo-Shoot-Appearance-Guide--General-.docx` both derive from
`BCBS VT Photo Shoot Appearance Guide.docx`.

Action: copy both desktop files into the same folder with BCBS-convention
names (see Naming Rules below), then delete the original single file.

**Compilation (one desktop → content from multiple local files)** — one
desktop file contains content from two or more separate local project files.
Read the desktop file with markitdown and identify the H1 boundary where one
project's content ends and another begins. Split the desktop file at that
boundary using python-docx (see Split Technique below).

---

## Phase 3: Present plan to Oliver before executing

State each operation explicitly:

```
Planned operations:
  REPLACE  Projects/Wellness Revolution/.../2026-04-01 – Wellness Revolution Registration Facebook Ads.docx
  REPLACE  Projects/Medicare Seminars/2026 Medicare 101 Social Media Plan - Revised 2026-04-23.docx
  CREATE   Photography/BCBS VT Photo Shoot Appearance Guide – Executive Team.docx
  CREATE   Photography/BCBS VT Photo Shoot Appearance Guide – General.docx
  DELETE   Photography/BCBS VT Photo Shoot Appearance Guide.docx   (replaced by two variants)
  SPLIT→   Projects/Mountain Days/2026/2026-03-30 – Mountain Days Social Posts.docx
  SPLIT→   Projects/Wellness Revolution/.../2026-03-30 – Wellness Revolution Social Posts.docx

Stale originals kept as record (not overwritten):
  Projects/Medicare Seminars/2026 Medicare 101 Social Media Plan.docx
```

Flag any file where the mapping is uncertain and ask Oliver before proceeding.

---

## Phase 4: Execute in safe order

Run operations in this order to minimize blast radius if something fails:

1. **Simple `cp` replacements first** — lowest risk, easy to verify by size.
2. **Consolidation splits** (create new variants, delete original) — moderate
   risk; verify both files exist before deleting original.
3. **Compilation splits** (python-docx) — highest complexity; run last.

### 1:1 replacement

```bash
cp "/path/to/desktop/File-Name.docx" \
   "/Users/oliverames/Documents/BCBS/path/to/Local File Name.docx"
```

Verify: `ls -la` the target and confirm byte count matches the desktop source.

### Consolidation (one local → two variant files)

```bash
cp "/path/to/desktop/Photo-Shoot-Appearance-Guide--Executive-Team-.docx" \
   "/Users/oliverames/Documents/BCBS/Photography/BCBS VT Photo Shoot Appearance Guide – Executive Team.docx"
cp "/path/to/desktop/Photo-Shoot-Appearance-Guide--General-.docx" \
   "/Users/oliverames/Documents/BCBS/Photography/BCBS VT Photo Shoot Appearance Guide – General.docx"
# Only delete the original AFTER confirming both new files exist:
rm "/Users/oliverames/Documents/BCBS/Photography/BCBS VT Photo Shoot Appearance Guide.docx"
```

### Compilation split (python-docx)

Use this pattern when one desktop file contains content from multiple local
project files. Find the H1 heading that marks the boundary, split there.

```python
from docx import Document
from docx.oxml.ns import qn

COMP  = "/path/to/desktop/compilation.docx"
OUT_A = "/path/to/local/Project A/file-a.docx"
OUT_B = "/path/to/local/Project B/file-b.docx"
SPLIT_HEADING = "Exact Heading Text At Boundary"

# Find split index
probe = Document(COMP)
body_children = [c for c in probe.element.body if c.tag != qn('w:sectPr')]
split_idx = None
for i, child in enumerate(body_children):
    if child.tag == qn('w:p'):
        text = ''.join(t.text or '' for t in child.iter(qn('w:t')))
        if SPLIT_HEADING in text:
            split_idx = i
            break

if split_idx is None:
    raise RuntimeError(f"Could not find split heading: {SPLIT_HEADING!r}")

# File A: everything before the split heading
doc_a = Document(COMP)
body_a = doc_a.element.body
children_a = [c for c in body_a if c.tag != qn('w:sectPr')]
for child in children_a[split_idx:]:
    body_a.remove(child)
doc_a.save(OUT_A)

# File B: the split heading and everything after
doc_b = Document(COMP)
body_b = doc_b.element.body
children_b = [c for c in body_b if c.tag != qn('w:sectPr')]
for child in children_b[:split_idx]:
    body_b.remove(child)
doc_b.save(OUT_B)

print(f"Split at index {split_idx}: A={len(children_a[:split_idx])} children, B={len(children_b[split_idx:])} children")
```

Key: `w:sectPr` is always excluded from manipulation — it carries the page
setup and header link from the source document. Never remove it.

For compilations with more than two sections (A, B, C), find two split
indices and apply the same technique with three output files.

---

## Phase 5: Verify

### Simple copies
Compare byte counts between desktop source and local target:

```bash
ls -la "/Desktop/source.docx" "/BCBS/target.docx"
```

Sizes should be identical (cp is byte-perfect).

### Split outputs
Run qlmanage thumbnails and visually confirm:
- Correct content in each file (right headings, no bleed between sections)
- Formatting intact (branded headings, no garbled text)

```bash
qlmanage -t -s 1600 -o /tmp "/BCBS/path/file-a.docx" "/BCBS/path/file-b.docx"
# Then Read the .png files to view them
```

---

## Naming rules

Local BCBS filenames follow these conventions (enforced by CLAUDE.md):

- **Prefix:** `BCBS VT` for Photography assets; project-specific for content
- **Separator:** en-dash ` – ` (U+2013, with spaces) between date, topic, and suffix
- **Never:** hyphens as word separators, colons, double-hyphens from ImageRelay format
- **Audience variants:** append ` – Executive Team` or ` – General` (en-dash)
  to the base name, not a parenthetical or suffix like `-exec`
- **Revised files:** append ` - Revised YYYY-MM-DD` when a revision exists
  alongside an original; keep both (original = historical record)

---

## Original/Revised preservation rule

When the BCBS directory contains both an original and a revised version of the
same document, the ImageRelay final always updates **only the revised file**.
The original is preserved as a historical record.

Example:
```
2026 Medicare 101 Social Media Plan.docx           ← keep, do not touch
2026 Medicare 101 Social Media Plan - Revised 2026-04-23.docx  ← overwrite this one
```

If you are unsure which file is the "revised" target (e.g., there is only one
local file), overwrite it and report the action. Do not delete originals silently.

---

## Stale file flag

After all operations, report any files that appear to be superseded but were
not explicitly handled. Example: if the revised file was updated, mention the
original file and ask Oliver whether to keep or delete it. Never silently
delete a file that was not part of the planned operations.
