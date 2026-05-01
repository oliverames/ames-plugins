---
name: bcbs-brand
description: >
  Apply Blue Cross and Blue Shield of Vermont (BCBS VT) brand and
  writing standards to drafting, brand-linting, letterhead and memo
  .docx builds, customer-support triage, and employee benefits
  questions. Triggers: "BCBS VT", "Blue Cross VT", "brand-lint this",
  "check brand voice", "create a memo", "build a letterhead doc",
  "draft a press release", "triage a ticket", "my Blue Cross benefits",
  "remote work policy", "campaign plan", "content calendar".
version: 1.9.0
---

# Blue Cross and Blue Shield of Vermont

Apply Blue Cross VT's authoritative brand and writing standards to any BCBS VT task — drafting, reviewing, linting, letterhead building, or customer support. Consolidates brand, marketing, customer support, benefits, social media, and letterhead resources.

## Authoritative Sources (READ FIRST for brand/voice questions)

Two files under `data/brand/` are the canonical sources of truth, sourced verbatim from the internal BCBS VT reference PDFs in `~/Documents/BCBS/Reference/`. Where any other file in this skill conflicts with these two, **these two win**:

| File | Supersedes | Covers |
|------|-----------|--------|
| `data/brand/authoritative-brand-style-guide-2025-10.md` | Anything about visual identity | Brand story, tone attributes, approved/unapproved names, logos, colors (exact hex/PMS/CMYK/RGB), typography, photography, accessibility, co-branding, derivative marks. Source: Brand Style Guide (October 2025). |
| `data/brand/authoritative-writing-and-tone-guide.md` | Anything about writing, grammar, or voice | Writing goals, voice vs. tone, inclusive-language lists (people, age, gender, heritage, etc.), grammar mechanics, letter/email checklists, word list (insurance/policy/premium exceptions, healthcare vs. health care). Source: Writing and Tone Style Guide (rev. November 2021). |
| `data/brand/oliver-voice-layer.md` | Claude's drafting defaults; supplements (and in three documented places overrides) the authoritative files | Tonal modes, channel rules, anchor phrases, AI-tell don't-list, formatting preferences, CEO voice profile, workflow defaults. Apply by default for any prose Claude produces or edits. Where it conflicts with the authoritative files, the conflict table at the bottom of the file says which one wins for which audience. Source: Oliver's stated voice preferences. |

**Key authoritative rules that override legacy data files:**

- Approved names: **"Blue Cross and Blue Shield of Vermont"** and **"Blue Cross VT"** only. Never "BCBSVT," "BCBS Vermont," "Blue Cross Vermont," or "Blue Cross of Vermont."
- Primary color is **Blue Cross VT Blue `#0077C8` (PMS 3005 C)** — must be the dominant color, with other colors as accents.
- Writing at a **sixth-grade reading level**; single-space, left-align.
- **Typography tier (Brand Style Guide Oct 2025, p. 6):** **DIN** is the primary marketing/external font. **Calibri** is the secondary internal font for tools that don't render DIN (Word, PowerPoint, Excel). **Arial** is a fallback. The Letter Checklist (Writing & Tone Guide, p. 24) accepts any of the three at 11 pt body / 12 pt Medicare; brand-general digital and accessibility-focused use targets 12 pt minimum (14–18 pt for poor-vision audiences).
- **Never refer to ourselves as an "insurance company"** — we're a **"health service organization."** We sell **subscriptions** (not policies); we charge **subscription rates** (not premiums); externally, "rates" works.
- Letter checklist format: 11 pt (12 pt for Medicare), single-spaced, 1" top/bottom, **1.25" left/right** margins, logo on page one, include "over" on multi-page letters.
- **Co-branded asset?** (any draft that pairs Blue Cross VT with a partner like NMC, GMSC, VOI, VDI, or another vendor.) Stop and load `data/brand/authoritative-brand-style-guide-2025-10.md` § Co-Branding before proceeding. Quick checklist (full rules in the mirror, Brand Style Guide Oct 2025, p. 11):

  | # | Rule | Enforcement |
  |---|---|---|
  | 1 | **Lead time:** build **6–8 weeks** for BCBSA approval; approval valid for 3 years; submit samples within 6 months of use | Schedule check |
  | 2 | **Prominence:** Blue Cross VT must be **equal to or more prominent** than partner names/logos in size, color, placement, visual weight | Visual check |
  | 3 | **Disclosure:** include the partner's independent-status disclosure: *"[Partner] is an independent company providing [service] on behalf of Blue Cross and Blue Shield of Vermont."* | Text check |
  | 4 | **Forbidden language:** never imply "endorsed by," "in partnership with," "endorsement," "sponsorship," or that the partner is a BCBSA licensee or Blue System affiliate | Manual review (these phrases are only forbidden in co-branding contexts; not lintable without the co-brand signal) |
- **Statistical claims need source attribution.** Any number (percentages, rankings, "lowest/highest in the country") must carry a primary-source citation with a date — same standard as Oliver's `Professional Standards → Sources` rule. The Affordability Matters 19.6%/7.9% stat traces to WalletHub, July 2025, citing US Census Bureau and Kaiser Family Foundation.

## BCBS Operating Defaults

- **Task tracking is Jira.** For BCBS action items, use the Blue Cross VT Jira
  workspace (`bluecrossvt.atlassian.net`) and structured Jira/Atlassian MCP
  tools. Do not use another task system unless Oliver explicitly asks for it in
  the current request.
- **Word deliverables: pick the right path FIRST, before drafting.** The
  default is not always right. Misrouting produces a doc that looks like a
  presentation handout (wrong) instead of a tight Blue Cross VT memo (right).
  Use this routing test:

  | Content shape | Path | Output style |
  |---|---|---|
  | TO/FROM/DATE/RE routing, action items, recommendations, decision tables, **strategy documents that read like memos** (response management, ownership plans, gap analyses, escalation paths) | `--template=memo` | 15pt navy Title, 8pt gray Subtitle, 9pt body, 0.5" bottom margin, graphic banner, dense memo look |
  | Reports, proposals, formal internal write-ups, **standalone reference documents** without routing or recommendations | default (no flag) | Formal title band, no graphic banner, report look |
  | Plain/simple — only when Oliver explicitly asks | `--template=simple` | Letter-style minimal |
  | **Ambiguous between memo and default — internal strategy doc, no clear shape signal** | `--template=memo` | **When in doubt, choose memo.** Most BCBS internal strategy documents are memo-shaped. The default path is for outward-facing reports and standalone proposals only. |

  **Backstop rule (also embedded in the table above):** When in doubt
  between memo and default, choose memo. Most BCBS internal strategy
  documents Oliver writes are memo-shaped; the default is for
  outward-facing reports and standalone proposals.

- **Named references override skill defaults.** If Oliver names a specific
  existing document ("use the Gap Analysis Memo", "clone the V2 strategy
  memo", "match that onboarding letter"), clone THAT file via
  `build-letterhead.sh --exemplar=PATH`. Do not silently substitute the
  default template for a named reference — the named file already carries the
  target visual family, and the default often won't.

- **Visual-verify before delivering any `.docx`.** Render a thumbnail and
  compare to the canonical reference for the chosen path. The pandoc-built
  default and the V2 memo exemplar look noticeably different at a glance —
  catch the misroute on the first build, not after the user notices.

  ```bash
  qlmanage -t -s 1600 -o /tmp "path/to/output.docx"
  open "/tmp/output.docx.png"
  ```

  Reference for memo path: `~/Documents/BCBS/Projects/Digital Infrastructure Strategy/BCBS Digital Infrastructure Strategy Memo - V2.docx`
  (render its thumbnail the same way and compare side-by-side).

## Canonical markdown shape for BCBS `.docx` output

Before drafting any markdown intended for `build-letterhead.sh`, load
**`data/letterhead/markdown-shape.md`**. It covers the YAML front matter
(`title:` / `subtitle:` / `author:`), heading levels, table style, body
paragraphs, quote callouts, captions, and the "what NOT to include" list
(no inline HTML, no `<br/>`, no manual page breaks). Following the shape
is what makes the output look right — the reference doc handles all
visual styling automatically; extra formatting hints in the markdown
fight the template.

## Before Delivering Any Draft — Run the Linter

Run the mechanical brand checks **before** returning a draft to the user. These rules are not judgment calls.

```bash
python3 scripts/brand-lint.py path/to/draft.md
# or via stdin
echo "$draft" | python3 scripts/brand-lint.py -
```

The linter flags: forbidden names (BCBSVT, BCBS Vermont, etc.), forbidden self-references ("insurance company," "our policy," "our premiums," "we charge premiums," "premium rates"), phones missing the TTY/TDD: 711 annotation, `--` instead of em dash, double-space between sentences, `!!`, generic link text **inside markdown link brackets** (`[click here](url)`, `[learn more](url)` — naked-prose uses like "called to learn more" are intentionally not flagged because the authoritative guide itself uses that phrasing), wrong domain (bcbsvt.com vs bluecrossvt.org), and top inclusive-language violations ("the elderly," "hearing impaired," etc.).

Exit code `0` means the draft passes; `1` means there are violations to fix before returning it. For judgment-based checks (reading level, tone, inclusiveness beyond the top-confidence phrases), load `data/brand/authoritative-writing-and-tone-guide.md` and review manually.

### Quick brand lint (always loaded)

| ❌ Never write | ✅ Write instead |
|---------------|-----------------|
| BCBSVT, BCBS Vermont, Blue Cross Vermont, Blue Cross of Vermont | Blue Cross and Blue Shield of Vermont (first use) / Blue Cross VT |
| insurance company (for us) | health service organization |
| policy / policies (for our products) | subscription(s) |
| premium(s) (for us, external) | rate(s) |
| "we charge premiums" / "premium rates" | "we charge rates" / "subscription rates" |
| the elderly | older adults, older Vermonters |
| hearing impaired | deaf, hard of hearing |
| `--` (double-hyphen) | `—` (true em dash) |
| `[click here](url)`, `[learn more](url)` (markdown link text) | `[Find a doctor](url)` — descriptive link text |
| (802) 555-1234 alone | (802) 555-1234 (TTY/TDD: 711) |

## Verifying a Letter's Format

For any `.docx` that must pass the authoritative Letter Checklist (formal letters, member communications, compliance-sensitive outputs), run:

```bash
python3 scripts/letter-check.py path/to/letter.docx             # 11pt expected
python3 scripts/letter-check.py --medicare path/to/letter.docx  # 12pt expected
```

The checker reports pass/fail for: approved font family (Calibri / DIN 2014 / Arial), point size, single-spacing, 1" top/bottom + 1.25" left/right margins, left-justification, and logo-bearing header presence. Exit code `0` means all mechanical checks pass.

**Don't run letter-check.py on memos.** The Letter Checklist expects 11pt
body with 1.25" side margins; memos in the Proposal Report family run 9pt
with 1" side margins and a 0.5" bottom margin. Letter-check will "fail"
memos that are correct conformance to the memo template. Use
`memo-check.py` instead.

## Verifying a Memo's Format

For any `.docx` built from the Proposal Report memo exemplar, run:

```bash
python3 scripts/memo-check.py path/to/memo.docx
```

Checks: graphic header banner is present (header1.xml references an image
relationship), Title is 15pt bold navy `#00355E`, Subtitle is 8pt italic
gray `#595959`, Heading1 is navy on light-blue `#99D6EA` band with
ALL-CAPS, Normal body is 9pt, page bottom margin is 720 twips (0.5"), and
BlockText callout (if present) has pale-blue `#EBF4FA` fill with navy
`#00355E` left border. Exit code `0` means all mechanical checks pass.

### Memo visual checklist

A correctly built BCBS memo in the Proposal Report family has:

| Element | Expected |
|---------|----------|
| Header | Graphic banner (logo + title band) with short uppercase subject |
| Title | 15pt bold navy `#00355E`, left-aligned, directly below banner |
| Subtitle / tagline | 8pt italic gray `#595959`, pipe-separated (Team \| Author \| Date) |
| Routing | TO / FROM / DATE / RE rows at 9pt |
| Section headings | Heading1: ALL-CAPS navy on `#99D6EA` light-blue band |
| Body | 9pt black Calibri, 1.15 line spacing |
| Callouts | BlockText: pale-blue `#EBF4FA` fill, navy `#00355E` left border |
| Page | 1" top + sides, **0.5" bottom**, 0.5" header distance |

### Template decision tree

1. **Oliver named a specific reference file?** → Clone that file directly.
   ```bash
   bash data/letterhead/scripts/build-letterhead.sh \
     --exemplar=/path/to/named-reference.docx \
     --banner-title="..." input.md output.docx
   ```
   Never silently substitute a default for a named reference.
2. **Oliver described a memo** (TO/FROM/RE, action items, routing)?
   → Use the bundled memo exemplar.
   ```bash
   bash data/letterhead/scripts/build-letterhead.sh \
     --template=memo --banner-title="STRATEGY MEMO" input.md output.docx
   ```
3. **Oliver described a report, proposal, or polished formal doc?**
   → Default Proposal Report Portrait template.
   ```bash
   bash data/letterhead/scripts/build-letterhead.sh input.md output.docx
   ```
4. **Oliver explicitly asked for plain / simple?** → Simple fallback.
   ```bash
   bash data/letterhead/scripts/build-letterhead.sh \
     --template=simple input.md output.docx
   ```

### Page-count caveat

Don't sink time into programmatic page counting for one-off memos. The
macOS Word AppleScript `count of pages of active document` returns 0 before
pagination is computed, and `repaginate` doesn't reliably force it. For
visual verification, `qlmanage -t` thumbnails give a fast first-page check.
Memos that need two pages to breathe are fine; don't squeeze content to
hit an artificial one-page target.

## Organization Quick Reference

- **Full name:** Blue Cross and Blue Shield of Vermont
- **Short name:** Blue Cross VT
- **Founded:** 1989 (Brand Style Guide Oct 2025, p. 2 — "Born in Vermont in 1989")
- **Headquarters:** Berlin, Vermont
- **Structure:** Local, not-for-profit health plan; BCBSA licensee; affiliated with BCBS Michigan
- **Employees:** ~400
- **CEO (2026):** Beth Roberts (formal: Beth-Ann Roberts, MBA — used in HR/announcement copy only; brand voice and public-facing copy use "Beth Roberts," matching her bio at bluecrossvt.org/beth-roberts)
- **Brand & Engagement Director:** Teresa Anderson (Brand, Reputation, Engagement & Experience division — owns the 2026 Operating Plan)
- **Mission:** "We are committed to the health of Vermonters, outstanding member experiences and responsible cost management for all the people whose lives we touch."
- **Brand Promise:** "Vermonters making healthcare work better for Vermonters." (Brand Style Guide Oct 2025, p. 1)
- **Vision:** "Together, we can build a transformed health care system in which every Vermonter has healthcare coverage and receives timely, effective, affordable care." (Brand Style Guide Oct 2025, p. 1)
- **Logo Tagline (required on most uses):** "An Independent Licensee of the Blue Cross and Blue Shield Association." (Brand Style Guide Oct 2025, p. 3)
- **Voice principle (writing only, NOT a tagline):** "We're Vermonters serving Vermonters." (Writing & Tone Guide, p. 5)
- **Brand Personality:** The Everyman Caregiver. All for one and one for all.
- **Website:** bluecrossvt.org | **Social:** @bluecrossvt

## Brand Voice Summary

**Authoritative 6-attribute framework** (Brand Style Guide Oct 2025, p. 2):

| Attribute | Means |
|---|---|
| **Clear and Direct** | Plain-spoken, jargon-free, sixth-grade reading level |
| **Truthful** | Accurate, source-attributed, never overpromise |
| **Friendly and Polite** | Warm, neighborly, respectful — never condescending |
| **Empathetic** | Acknowledges Vermonters' lived experience with care |
| **Inspiring** | Affirms agency and choice; never paternalistic |
| **Uniquely Vermont** | Community-rooted, place-aware, locally specific |

**Quick mental model** (4-dimension shorthand — full framework above):

| Dimension | Is | Is NOT |
|-----------|-----|--------|
| Tone | Warm, approachable, knowledgeable | Cold, corporate, jargon-heavy |
| Perspective | Vermont-first, community-rooted | National, generic |
| Style | Plain-spoken, practical, empowering | Condescending, vague |
| Authority | Trusted local expert | Distant insurer |

**Core principles:** Vermont-first always, nonprofit heart, plain language, empowering not paternalistic, warm but grounded, collaborative not competitive.

**Key vocabulary:** "Vermonters" (not customers), "health plan" (not insurance policy), "health care" (two words; the activity) vs. "healthcare" (one word; the system), community, local, neighbors, well-being.

## Writing Rules Quick Reference

These rules are in `data/brand/authoritative-writing-and-tone-guide.md` (the source of truth) but bear repeating where the agent will see them every load:

- **Title case for headlines, section headings, letters, PowerPoints, articles, press releases.** Sentence case is the markdown norm but **not** BCBS style. (Writing & Tone Guide p. 13.) Convert sentence case to title case before delivery.
- **Refer to a company or product as "it," not "they."** "Cigna says it has the lowest rates" — not "Cigna says they have." Same rule for partners (NMC, GMSC, VOI, VDI). (Writing & Tone Guide p. 7.) `brand-lint.py` flags partner-name + "they" within 80 chars.
- **Use "they" as a singular pronoun** when gender is unknown or unspecified. (Writing & Tone Guide p. 9.)
- **Don't add "Vermont" or "VT" to a county or town reference.** "Members in Chittenden County" — not "Chittenden County, Vermont." (Writing & Tone Guide p. 19.)
- **No underline formatting. No combinations of italic + bold + caps + underline.** Italic alone for emphasis. (Writing & Tone Guide p. 12.)
- **Use the serial (Oxford) comma in 3+ lists.** "Members, providers, and policymakers" — not "members, providers and policymakers." (Writing & Tone Guide p. 16.) `brand-lint.py` flags WARN-level on the missing-comma pattern.
- **Em dash without spaces:** "Vermonters—our neighbors" — not "Vermonters — our neighbors." (Writing & Tone Guide p. 16.) `brand-lint.py` flags ` — ` with spaces.
- **No directional language** ("left sidebar," "at the bottom of the page") — layout shifts on mobile. Describe options by name. (Writing & Tone Guide p. 20.)

## 2026 Strategic Defaults

When drafting any external content for 2026, anchor it to the team's operating plan. See `data/strategy/` for the full reference; quick rules:

- **Affordability Matters is 2026's organizing thrust.** When relevant, the headline framing is: Vermonters spend 19.6% of income on healthcare vs. 7.9% national average (source: WalletHub, July 2025, citing US Census Bureau and Kaiser Family Foundation). See `data/strategy/affordability-matters.md`.
- **CEO Brand Building.** Beth Roberts is positioned as the affordability thought leader for 2026. CEO-attributed content should reflect her voice and the affordability narrative.
- **Medicare 101 seminars (May–September).** Anything Medicare-related during this window should reference or support the seminar series. Audiences: Med-Sup Age-In + Switchers (specifically targeting UHC members).
- **Cigna → Blue Cross VT** is an explicit 2026 conversion play for Large Group Non-Jumbo. Competitor framing is allowed for this segment.
- **Vermont Blue Advantage Medicare Advantage plans are discontinued.** Do NOT reference MA availability. The "Vermont Blue Advantage" entity itself still exists as an affiliate.
- **2026 KPIs:** NPS goal 9 (Brand Strength Measure), web intercept >−35, 75% Likely-to-Renew, 50% consumer / 65% member affordability perception.
- See `data/strategy/2026-operating-plan.md` for the full audience taxonomy, all four operating goals, and the OEP/AEP/QHP/EGWP acronym glossary.

### Audience cheat-sheet (2026, top segments)

The five most-frequently-drafted-against segments are below. For the full
12-segment audience taxonomy (including Blue Edge Business, Large Group
Non-Jumbo, Brokers, Members, Providers, Policymakers) plus the four
operating goals and the OEP/AEP/QHP/EGWP glossary, load
**`data/strategy/2026-operating-plan.md`** — that file is the canonical
source for any 2026-attributed audience or KPI claim.

| Segment | Mode | Tone / CTA default |
|---|---|---|
| QHP Individual | Growth + Retention | Plain-spoken, planning-oriented; CTA = compare plans / get a quote |
| QHP Small Group | Growth + Retention | Practical, value-focused; CTA = explore plans / talk to broker |
| Med-Sup Age-In | Growth | Warm, navigational; CTA = Medicare 101 seminars (May–Sept) |
| Med-Sup Switchers | Growth | Comparative (target UHC); CTA = Medicare 101 seminars + switch carriers |
| Employees | Run | Internal voice ("Blue Cross," "our company"); CEO/Affordability education |

## Oliver's Employment

| Benefit | Details |
|---------|---------|
| Role | Social Media Strategist |
| Salary | $80,000 |
| Bonus | 5% (~$4,000) if company hits goals; first eligible April 2027 |
| PTO | 20 days + 10 holidays |
| Healthcare | High deductible; BCBS contributes $4,000/yr |
| 401(k) | 12.6% total at 6% employee contribution |
| Start Date | March 2026 |

## Scripts

Operational tools live in `scripts/` at the skill root. Run them — don't reinvent their checks in-line.

| File | Purpose |
|------|---------|
| `scripts/brand-lint.py` | Flag forbidden names, self-references, phone-without-TTY, em-dash mis-use, and top inclusive-language violations in draft markdown or plain text. Run before delivering any draft. |
| `scripts/letter-check.py` | Verify a built `.docx` against the authoritative Letter Checklist format section (font, size, line spacing, margins, alignment, logo). For **letters**, not memos. |
| `scripts/memo-check.py` | Verify a memo `.docx` built from the Proposal Report memo exemplar (graphic banner, 15pt navy Title, 8pt gray Subtitle, 9pt body, 0.5" bottom margin, navy-on-band Heading1, pale-blue callout). For **memos**, not letters. |

## Data Files

All reference data lives in `data/` next to this file. Load as needed — don't load everything upfront.

### Brand & Voice
| File | Contents |
|------|----------|
| **`data/brand/authoritative-brand-style-guide-2025-10.md`** | **AUTHORITATIVE. Visual identity, colors, logos, typography, co-branding, derivative marks (from the Oct 2025 Brand Style Guide PDF).** |
| **`data/brand/authoritative-writing-and-tone-guide.md`** | **AUTHORITATIVE. Voice, tone, grammar mechanics, inclusive-language lists, letter/email checklists, word list (from the Writing and Tone Style Guide PDF).** |
| **`data/brand/oliver-voice-layer.md`** | **Oliver's personal voice layer. Tonal modes, channel rules, anchor phrases, AI-tell don't-list, formatting preferences, CEO voice profile. Apply by default for any prose Claude produces or edits in BCBS work; defer to authoritative files for member-facing finished deliverables where flagged.** |
| `data/brand/brand-voice.md` | Legacy — full writing guide with verbatim examples. Use for historical context; defer to authoritative file for rules. |
| `data/brand/visual-identity.md` | Legacy — earlier colors/typography/logo usage. Defer to authoritative brand style guide for exact values. |
| `data/brand/content-by-channel.md` | Channel-specific rules (web, email, social, print, press) |
| `data/brand/messaging-pillars.md` | Key messages by audience with do/don't comparisons |
| `data/brand/social-content-archive.md` | Real captions with engagement data, top-performing patterns |
| `data/brand/verbatim-content-library.md` | Blog articles, CEO letters, press releases, financial data |
| `data/brand/before-after-examples.md` | Brand voice transformation examples |
| `data/brand/voice-constant-tone-flexes.md` | How tone adjusts across contexts |
| `data/brand/bcbsvt-voice-attributes.md` | Voice attribute definitions |
| `data/brand/bcbsvt-content-guide.md` | Content creation guidelines |

### Benefits & HR
| File | Contents |
|------|----------|
| `data/benefits/benefits-2026.md` | Complete 2026 benefits breakdown |
| `data/benefits/hr-policies.md` | Remote work, onboarding, culture norms |

### Customer Support
| File | Contents |
|------|----------|
| `data/customer-support/bcbsvt-website-content.md` | Website content reference |
| `data/customer-support/bcbsvt-kb-context.md` | Knowledge base context |
| `data/customer-support/bcbsvt-research-context.md` | Research sources and context |
| `data/customer-support/bcbsvt-faqs-help.md` | FAQs and help content |
| `data/customer-support/bcbsvt-member-support.md` | Member support reference |
| `data/customer-support/bcbsvt-triage-context.md` | Ticket triage categories and routing |

### Strategy (2026)
| File | Contents |
|------|----------|
| **`data/strategy/2026-operating-plan.md`** | **2026 Brand & Engagement Operating Plan: four operating goals, audience taxonomy (QHP / Med-Sup / Brokers / Employees / Members / Providers / Policymakers), Affordability Matters campaign tactics, Medicare 101 seminars, KPIs, OEP/AEP/EGWP glossary. Source: 2026-04-15 Operating Plan PDF.** |
| **`data/strategy/affordability-matters.md`** | **Affordability Matters campaign reference: 19.6%/7.9% headline stat with WalletHub-July-2025 attribution, partner orgs (NMC/GMSC/VOI/VDI), talking points, vtaffordablecare.com, Cost Tool URL, co-branding compliance reminder.** |

### Marketing & Campaigns
| File | Contents |
|------|----------|
| `data/marketing/bcbsvt-campaigns.md` | Campaign planning context |

### Social Media
| File | Contents |
|------|----------|
| `data/social/annual-themes.md` | Annual content calendar: health observances, seasonal themes, events |

### Letterhead

Three references are available. Pick via the template decision tree above.

| File | Role | Contents |
|------|------|----------|
| `data/letterhead/assets/reference-proposal-report.docx` | **DEFAULT** (reports/proposals) | Formal template with the Proposal Report header band (BCBS logo + title area). Use for reports, proposals, strategy documents, formal internal documents, and polished `.docx` outputs that aren't memos. Built by `style-proposal-report.py` from the .dotx below. Covers every styleId pandoc emits (`Title`, `Subtitle`, `Author`, `Date`, `Heading1-4`, `BodyText`, `FirstParagraph`, `Compact`, `Caption`, `IntenseQuote`, and the `Table` table style). |
| `data/letterhead/assets/exemplar-proposal-report-memo.docx` | **Memo exemplar** | Memo variant of the Proposal Report family, sanitized and safe to ship. Carries the graphic header banner (with `PROPOSAL MEMO` placeholder text — rewrite per-memo via `--banner-title`), 15pt navy Title, 8pt gray Subtitle, 9pt Normal body, 0.5" bottom margin, and the augmented pandoc-expected styles (Title, Subtitle, FirstParagraph, BlockText). Built by `build-exemplar-memo.py` from the private V2 memo at `~/Documents/BCBS/Projects/Digital Infrastructure Strategy/BCBS Digital Infrastructure Strategy Memo - V2.docx`. |
| `data/letterhead/assets/proposal-report-template.dotx` | Source | Authoritative Blue Cross VT Proposal Report Portrait Template (Word .dotx). Copy of the canonical file at `/Users/oliverames/Library/CloudStorage/OneDrive-Personal/Documents/BCBS/Templates/Proposal Report Portrait Template.dotx` and `~/Documents/BCBS/Templates/Proposal Report Portrait Template.dotx`. Do not edit directly; regenerate the reference docx via `style-proposal-report.py`. |
| `data/letterhead/assets/reference.docx` | Simple fallback | Simple Blue Cross VT pandoc reference for plain/simple documents only when Oliver explicitly asks for that style. Built by `style-reference-doc.py`. |
| `data/letterhead/scripts/build-letterhead.sh` | Build entry point | Top-level builder. Accepts `--template={default,memo,simple}`, `--exemplar=PATH` for a user-named reference file, and `--banner-title="..."` (memo/exemplar paths only). Delegates memo/exemplar builds to `clone-exemplar.py`. |
| `data/letterhead/scripts/clone-exemplar.py` | Pandoc + banner rewrite + bullet tighten | Invoked by build-letterhead.sh for memo and exemplar builds. Runs `pandoc --reference-doc=<exemplar>`. Optional flags: `--banner-title="..."` rewrites header1.xml's banner text in both the `wps:txbx` and `mc:Fallback` `v:textbox` copies; `--tight-bullets` rewrites every level-0 numbering entry to `left=360 hanging=180` so pandoc-appended bullet entries don't render at the looser Word-default 720/360. `build-letterhead.sh` auto-passes `--tight-bullets` for memo and exemplar paths because the Proposal Report family expects tight bullets; pass `--exemplar=PATH` directly to `clone-exemplar.py` (bypassing build-letterhead.sh) if you want to opt out for a non-memo exemplar. Warns if the exemplar is missing pandoc-expected styles (Title, Subtitle, Heading1, FirstParagraph). |
| `data/letterhead/scripts/build-exemplar-memo.py` | Regenerate memo exemplar | Clones V2, sanitizes `document.xml`, `header1.xml` (banner text → `PROPOSAL MEMO`), and `docProps/core.xml` metadata; augments `styles.xml` with Title/Subtitle/FirstParagraph/BlockText; fixes ListParagraph indent (720 → 360/180) and numbering level-0 `ind`. Re-run when V2 changes or the sanitization rules change. |
| `data/letterhead/scripts/style-proposal-report.py` | Regenerate default | Python+lxml script that converts the .dotx to .docx, strips the placeholder body (keeping the header banner and margins), **preserves the template's Normal and Heading1 styles untouched** (Heading1 is the BCBS blue-band signature), **upserts every other pandoc-expected paragraph styleId** by styleId (so Word doesn't silently fall back to Normal), injects a `Table` table-type style with BCBS gray gridlines and a bold-navy header row, and writes the Independent Licensee footer. Re-run after any brand-palette change. |
| `data/letterhead/scripts/style-reference-doc.py` | Regenerate simple fallback | Python script that styles `reference.docx` with Blue Cross VT colors, fonts, and margins. |

**Letterhead usage:**

```bash
# Default report / proposal / strategy doc:
bash data/letterhead/scripts/build-letterhead.sh input.md output.docx

# Memo (graphic banner + routing table + 9pt body):
bash data/letterhead/scripts/build-letterhead.sh \
  --template=memo --banner-title="STRATEGY MEMO" input.md memo.docx

# User named a specific reference file — clone it:
bash data/letterhead/scripts/build-letterhead.sh \
  --exemplar=/path/to/named-reference.docx \
  --banner-title="CAMPAIGN BRIEF" input.md out.docx

# Plain/simple (only when Oliver explicitly asks):
bash data/letterhead/scripts/build-letterhead.sh \
  --template=simple input.md output.docx
```

All outputs inherit Calibri body text, navy Blue Cross VT headings, and the
Independent Licensee footer disclosure (when the chosen reference doc carries
it). The default Proposal Report reference carries the formal title band;
the memo exemplar carries the graphic banner ribbon.

**Header-banner details (memo path):** the banner title text lives in
`word/header1.xml` **twice** — once inside the modern `<wps:txbx>` shape and
once inside the `<mc:Fallback><v:textbox>` legacy-Word construct. Both copies
get rewritten together when `--banner-title` is supplied. The exemplar ships
with `PROPOSAL MEMO` as the placeholder string so clone-exemplar.py can find
and replace it.

**To regenerate any reference doc** (after brand changes or a template update):
```bash
python3 data/letterhead/scripts/style-proposal-report.py        # default
python3 data/letterhead/scripts/style-reference-doc.py          # simple fallback
python3 data/letterhead/scripts/build-exemplar-memo.py          # memo exemplar
```

## Source Documents on Disk

For the directory listing of `~/Documents/BCBS/` (Benefits, Calls, Hiring,
Onboarding, Reference) and which mirrors in `data/` are sourced from
which PDF, see **`data/source-documents-on-disk.md`**. Read source PDFs
for additional context as needed; never move or modify them.

## Content Pillars & Mix

1. **Health & Wellness** (35%) — Preventive care, mental health, nutrition, seasonal tips
2. **Community** (30%) — Events, grants, partnerships, youth programs, volunteering
3. **Coverage Education** (20%) — How insurance works, cost transparency, benefit explanations
4. **Corporate** (10%) — Awards, leadership, culture, workplace wellness
5. **Advocacy** (5%) — Affordability, access, system reform

## Social Media Posting Cadence

| Platform | Frequency | Hashtags | Emoji |
|----------|-----------|----------|-------|
| Instagram | 4-5x/week | 5-7 in first comment, never in post body | 1-3 contextual |
| Facebook | 3-4x/week | 3-5 | Yes |
| LinkedIn | 3x/week | **0** (zero) | Sparse |
| YouTube | 2x/month | — | — |

LinkedIn posts run two to four sentences, include one external link, and use zero hashtags. Instagram CTA convention is "at the link in our bio"; hashtags go in the first comment, never inline. Always include `#BlueCrossVT #Vermont` on Facebook and Instagram (first-comment placement on Instagram).

## Medicare Warning (2026)

**Vermont Blue Advantage discontinued all Medicare Advantage plans.** Do NOT reference MA availability or write copy that suggests we still sell MA. Current offerings: Vermont Medigap Blue, Vermont Blue 65 Supplement, Blue MedicareRx (Part D).

**The "Vermont Blue Advantage" entity itself still exists.** Per the Writing & Tone Guide (p. 7), Blue Cross VT manages two affiliates: Vermont Blue Advantage and The Vermont Health Plan. The Vermont Health Plan (TVHP) is the BCBS VT subsidiary that sells Vermont Medigap Blue (Brand Style Guide p. 10). Don't conflate "no MA plans" with "the entity is gone."

**Medicare 101 seminars run May–September 2026.** Any Medicare-related draft in that window should reference or support the seminar series. See `data/strategy/2026-operating-plan.md` for the Med-Sup Age-In and Switchers audience definitions, and the explicit "target United Health Care members to switch carriers" play.
