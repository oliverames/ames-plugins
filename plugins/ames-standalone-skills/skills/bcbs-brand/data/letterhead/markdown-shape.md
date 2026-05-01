# Canonical Markdown Shape for BCBS `.docx` Output

The reference doc is tuned so pandoc-to-docx produces BCBS-branded output
automatically. Follow this shape in the markdown you pass to
`build-letterhead.sh` — the shape is what makes the output look right, not
extra formatting hints in the prompt.

## YAML front matter (required for a cover block)

```yaml
---
title: "Proposal: Short descriptive title"
subtitle: "Team name | Prepared by Oliver Ames | Absolute Date"
author: "Oliver Ames"
---
```

`title:` renders as bold dark-navy Calibri 15pt (styleId `Title`).
`subtitle:` renders as a small gray byline (styleId `Subtitle`).
`author:` populates `dc:creator` in the output's `docProps/core.xml`, so
File → Properties attributes the memo to Oliver. Without it, pandoc clears
`dc:creator` to empty — attribution silently disappears from the document
metadata. Override only when authoring on someone else's behalf.
Do not use both a YAML `title:` and an inline `# Title` — pick one.

## Section headings

Use a single `#` per section. The reference memo
(`BCBS Digital Infrastructure Strategy Memo - V2.docx`) and the Jira
One-Sheet both use only one level of heading: `EXECUTIVE SUMMARY`,
`DECISIONS NEEDED`, etc. Each `# Heading` renders on a light-blue shading
band in all caps, which is the BCBS visual signature.

Only reach for `##` when a section genuinely needs a subheading. `##`
renders as bold dark-navy Calibri 12pt (no band). `###` and `####` are
available as BCBS-primary-blue accents but should be rare.

## Tables

Pipe-tables convert cleanly. The table style `Table` in the reference doc
gives every cell a light-gray (`#BFBFBF`) 0.5pt border and puts the header
row in bold navy on a light-blue tint.

## Body paragraphs

Plain prose. Body text inherits Calibri 10pt 1.15 line-spacing from the
template's Normal style — do not add direct font formatting. Bulleted and
numbered lists work as expected.

## Quote callouts

`> text` renders as an intense quote in italic navy (styleId `IntenseQuote`).

## Captions

Use pandoc's image caption syntax or a line starting with `Caption:` —
renders italic gray 9pt.

## What NOT to put in the markdown

- No inline HTML for colors, fonts, or sizes. The reference doc handles it.
- No `<br/>` or hard line breaks for spacing. Use paragraph breaks.
- No Heading 1 ALL-CAPS in the markdown itself — write `# Executive Summary`;
  the Heading1 style applies the caps transform automatically.
- No page breaks inside the body. Let the reference doc's margins and the
  template's page frame do the work.
