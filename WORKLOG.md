# Worklog

## 2026-04-28 — bcbs-vt v1.7.0: align skill with 2026 Operating Plan + Affordability Matters

**What changed**: Brought the bcbs-vt skill into alignment with four current source-of-truth BCBS docs that landed in `~/Documents/BCBS/Reference/`: the 2025-10 Brand Style Guide, the Writing and Tone Style Guide (rev. Nov 2021), the 2026-04-15 Brand & Engagement Operating Plan, and the Vermont Healthcare Affordability Guide 2025. Two new strategy reference files capture the operational layer the skill had been entirely blind to: `data/strategy/2026-operating-plan.md` (four operating goals, full audience taxonomy QHP/Med-Sup/Brokers/Employees/Members/Providers/Policymakers, 2026 KPIs, OEP/AEP/QHP/EGWP glossary) and `data/strategy/affordability-matters.md` (19.6%/7.9% headline stat with WalletHub-July-2025 attribution, partner orgs NMC/GMSC/VOI/VDI, talking-point hierarchy, vtaffordablecare.com, Cost Tool URL, full co-branding compliance reminder). SKILL.md surface fixed: replaced the mislabeled `Tagline: "Vermonters Serving Vermonters"` line with five properly-labeled fields (Brand Promise / Vision / Logo Tagline / Voice principle / Brand Personality), each citing its source PDF; clarified DIN-primary/Calibri-secondary/Arial-fallback typography tier with the 11pt-letter vs 12pt-accessibility size reconciliation; added a 2026 Strategic Defaults block pointing at the new strategy files plus a 12-segment audience cheat-sheet; added co-branding fast-check and statistical-claims source-attribution rules; strengthened the Medicare warning to distinguish the still-existing Vermont Blue Advantage entity from the discontinued MA plans; refreshed the Source Documents tree with the four current Reference PDFs and explicit pointers to which `data/` files mirror them. `brand-lint.py` extended with five new rule categories (CORPORATE-FLUFF gated by `_is_about_us`, INTERNET-SLANG, LITERAL-OR-SKIP, RETIRED-TTY, DIRECTIONAL) covering Words-to-Avoid items from Writing & Tone Guide pp. 18–29 that the existing rules didn't catch. `letter-check.py` extended with three new mechanical checks (service-mark presence near Blue Cross brand name, "over" word on multi-page letters with explicit page breaks, signature-block detection via closing keywords). Skill bumped 1.6.0 → 1.7.0; plugin bumped 3.6.2 → 3.6.3 (patch — additive, no breaking changes); `./sync` regenerated both marketplace manifests.

**Decisions made**:
- **Strategy lives in its own directory, not under `marketing/`.** Created `data/strategy/` rather than dropping the operating-plan and affordability-matters files into the existing `data/marketing/` because the strategic context informs every audience and channel, not just marketing campaigns. The new files are surfaced in SKILL.md's Data Files section as a top-tier "Strategy (2026)" group above Marketing.
- **Tagline / Brand Promise / Voice principle were collapsed into one mislabeled field — and the fix was to expand, not rename.** The Brand Style Guide (Oct 2025, p. 1, p. 3) and Writing & Tone Guide (p. 5) define three distinct labels that the prior SKILL.md flattened into "Tagline: Vermonters Serving Vermonters." Replacing the line with all three labels (plus Vision and Brand Personality) restores the source semantics. Cited each line's source PDF page so future edits can verify against canonical text.
- **Conjugation matters for the new lint patterns.** First test pass missed `leveraging` (the rule was `\bleverage\b`) and `crushed it` (rule was `crushing it` only). Followed the existing SELF_REFERENCE_RULES style — `(charge|charging|charges|charged)` — and expanded to `\bleverag(e|es|ed|ing)\b`, `\b(crushing|crushed) it\b`, `\bdisrupt(ing|ed|ion|or)?\b`, `\bincentivi[sz](e|es|ed|ing)\b`. Second test pass caught all 10 expected violations.
- **`_is_about_us` gating on CORPORATE_FLUFF, not on INTERNET_SLANG / RETIRED_TTY / DIRECTIONAL.** Industry-critique drafts can legitimately quote "thought leader" or "disruption" in describing Silicon Valley or competitor framing; gating CORPORATE_FLUFF behind the existing `_is_about_us` heuristic prevents false flags when we're describing them, not us. The other three categories (internet slang, retired TTY number, directional accessibility violations) are always errors regardless of whose voice is speaking, so they're flagged unconditionally.
- **`has_over_word` returns None for single-page docs.** Letter-check's "over" rule applies only to multi-page letters per the Writing & Tone Guide checklist (p. 24). Returning `None` (rendered as PASS with "not applicable" message) instead of FAIL prevents single-page letters from being marked broken for missing a multi-page artifact they don't need. Multi-page detection is conservative — counts only explicit `<w:br w:type="page"/>` breaks, since OOXML doesn't expose Word's automatic pagination.
- **No README / CLAUDE.md / AGENTS.md update.** README's bcbs-vt entry is intentionally generic ("Context and guidance for BCBS VT work"); the changes are within the skill, not to its public surface in the plugin pack inventory. Workflow conventions in CLAUDE.md / AGENTS.md weren't touched.
- **CEO name left unverified.** Operating Plan (p. 5) refers to her as "Beth" only; SKILL.md still says "Beth-Ann Roberts" from a prior session. Flagged as an open question rather than guessed-at — wrong hyphenation in a press-release skill is a real risk.

**Validated by**:
- `python3 scripts/brand-lint.py -` smoke test on a synthetic dirty draft caught 10/10 expected violations; clean draft passed with exit 0.
- `python3 scripts/letter-check.py` against `Hiring/Oliver Ames Cover Letter ...docx` integrated the 3 new checks alongside the existing 6 (signature found via "Sincerely"; ® check warned correctly since the cover letter doesn't have BCBS branding marks; "over" check correctly skipped for single-page).
- `validate-skill plugins/ames-standalone-skills/skills/bcbs-vt/SKILL.md` exit 0.
- All four manifest JSONs validate via `python3 -m json.tool`.
- `./sync` regenerated `.claude-plugin/marketplace.json` (6 plugins) and `.agents/plugins/marketplace.json` (4 plugins, experimental) with `ames-standalone-skills v3.6.3`.
- Pre-edit backups in `.backups/{SKILL.md,brand-lint.py,letter-check.py}.pre-1.7.0` (intentionally untracked per existing `.backups/` convention).

**Left off at**:
- **Resolved this session**: SKILL.md Tagline/Brand Promise mislabel; missing 2026 Operating Plan context (audiences, KPIs, Affordability Matters narrative); brand-lint blind spots on Words-to-Avoid corporate-fluff terms; letter-check missing service-mark/over-word/signature checks; stale Source Documents tree; weak Medicare warning that conflated entity vs MA plan offering.
- **Still open from prior entries** (carried forward, not resolved this session): sync-count auto-regen; publish script; postpublish hooks; `bcbs-wrap-up` cache version mismatch (resolves on marketplace refresh); legacy Asana-tagged items in BCBS notes still need Oliver triage; `ames-connectors` LICENSE; `codex-doctor --only-enabled` flag; the `--tight-bullets` opt-out question; `core.xml` `cp:revision` reset.
- **Untracked residual in `ames-claude`**: `.backups/*.pre-1.7.0` (intentional); `skills/verify-live/` (created earlier today by a separate session per memory `project_verify_live_skill.md`, not mine to ship).
- Commit `c837d3e` pushed to `origin/main`.

**Open questions**:
- **CEO full name spelling** — "Beth-Ann Roberts" (current SKILL.md) vs "Beth" (Operating Plan p. 5) vs "Bethann" / "Beth Ann" / something else? SKILL.md and `data/strategy/2026-operating-plan.md` both flag this for confirmation; a wrong spelling in a press release or memo template is a real failure mode.
- **Affordability Matters voice tone in CEO-attributed content** — the campaign frames affordability as a Vermont issue requiring collaboration ("no one entity or individual can fix the issue alone"). When Beth is the speaker, does she lean into "we as Blue Cross VT are pushing for change" or stay in the collaborative-convener register? `data/strategy/affordability-matters.md` notes the avoid-blame-tone rule but doesn't prescribe the CEO-specific voice.
- **The 2026-operating-plan.md and affordability-matters.md files are static snapshots.** When the Operating Plan refreshes (next quarterly review or 2027 plan), the skill needs an explicit re-sync step. Worth adding a `Last synced from PDF: YYYY-MM-DD` header to both files for staleness checking.

---

## 2026-04-27 — bcbs-vt v1.6.0: route strategy memos to --template=memo by default

**What changed**: Fixed the actual root cause of memo-vs-report misroutes in the bcbs-vt skill. The v1.5.0 work added the `--template=memo` and `--exemplar=PATH` infrastructure plus `clone-exemplar.py`, `build-exemplar-memo.py`, and `memo-check.py`, but the SKILL.md "BCBS Operating Defaults" section still bundled "strategy documents" with the default `proposal-report` template. That single phrase outweighed the better Template decision tree further down, so future sessions kept defaulting to the wrong path. Replaced the muddled pair of bullets with an explicit routing-shape table at the top of the section (TO/FROM/RE routing → memo; standalone reports → default; explicit plain → simple), added a "when in doubt between memo and default, choose memo" rule of thumb, and added a `qlmanage -t` visual-verify step as a forcing function so misroutes get caught on the first build instead of after the user notices. Skill bumped v1.5.0 → v1.6.0; plugin patch-bumped 3.6.0 → 3.6.1 (no new code, docs-only routing fix). `./sync` regenerated both marketplace manifests and pushed.

**Decisions made**: Patch bump (3.6.0 → 3.6.1) rather than minor because no new functionality shipped — the routing infrastructure was already in v1.5.0; this commit only repositions guidance. The Template decision tree (lines 205-229) was kept as-is; it was already correct, just buried.

**Validated by**: BCBS VT Response Management Strategy doc on 2026-04-27 — first build via `build-letterhead.sh` (no flags) produced the wrong presentation-style look; rebuild via cloned V2 exemplar produced the right tight memo style. The skill change makes the second build the default for similar future asks.

**Left off at**: Skill committed and pushed (commit 6231e4a). Marketplace synced via bump-and-sync (commit 826e373). Memory file `feedback_bcbs_memo_reference.md` updated to point future sessions at the skill commands rather than describing the manual python-docx workaround it used to cover.

**Open questions**: None. Pattern is locked in for the next memo-shaped strategy document — should hit `--template=memo` on the first try.

---

## 2026-04-25 — bcbs-vt v1.5.0: memo exemplar pipeline + brand-lint premium rules

**What changed**: Closed the "memo deliverables look wrong" gap in the bcbs-vt skill. Added a sanitized clone of the V2 strategy memo as `data/letterhead/assets/exemplar-proposal-report-memo.docx` so memos in the Proposal Report Portrait family carry the graphic header banner that the existing `reference-proposal-report.docx` had been silently dropping. New `data/letterhead/scripts/build-exemplar-memo.py` regenerates the exemplar from V2 with four sanitization passes (body skeleton replacement, banner text in both `wps:txbx` and `mc:Fallback v:textbox` copies in `header1.xml`, `docProps/core.xml` metadata, `docProps/app.xml` stale page/word counters) plus three augmentation passes (`Title`/`Subtitle`/`FirstParagraph`/`BlockText`/`Compact`/`Table` style injection so pandoc's emitted pStyles resolve correctly, `Normal` rPr forced to 9pt, `ListParagraph` indent and numbering level-0 indent fixed from 720 → 360 with 180 hanging). New `data/letterhead/scripts/clone-exemplar.py` is the per-memo entry point: `pandoc --reference-doc=<exemplar>` with optional `--banner-title="..."` (rewrites both header copies) and `--tight-bullets` (forces every level-0 numbering entry to 360/180 so pandoc's appended bullet entries don't render at the looser Word-default 720/360). `build-letterhead.sh` extended with `--exemplar=PATH`, `--template=memo`, and `--banner-title="..."` flags; the memo and exemplar paths delegate to clone-exemplar.py and auto-pass `--tight-bullets`. New `scripts/memo-check.py` validator runs 7 mechanical checks (graphic banner image-rel present, Title 15pt navy, Subtitle 8pt italic gray, Heading1 navy on light-blue band ALL-CAPS, Normal 9pt, bottom margin 0.5", BlockText callout `#EBF4FA` fill with `#00355E` left border) — letter-check.py was firing false failures on memos because the Letter Checklist expects 11pt with 1.25" sides while memos run 9pt with 1" sides. SKILL.md bumped v1.4.0 → v1.5.0 with a memo visual checklist, three-way template decision tree, page-count caveat (qlmanage > AppleScript), explicit "named references override defaults" rule, and YAML template now includes `author: "Oliver Ames"` so per-memo outputs attribute him via `dc:creator`. `brand-lint.py` extended with two new SELF-REFERENCE patterns (`charge|charging|charges|charged premiums?` and `premium rates?`) gated by the existing `_is_about_us` heuristic so Medicare-context "premiums" stays clean; the SKILL.md table also corrected to clarify that the LINK-TEXT rule is scoped to markdown link brackets specifically (the authoritative writing guide itself uses "learn more" in prose). Plugin bumped 3.5.10 → 3.6.0 (minor — new user-facing capability via `--template=memo` etc.); `./sync` regenerated both marketplace manifests and propagated the version to the Codex-side plugin.json.

**Decisions made**:
- **Pandoc + augmented exemplar > shutil.copy2 + body-rewrite.** Initial verification showed pandoc's `--reference-doc` mechanism preserves the graphic header band byte-for-byte when the reference doc itself carries it (V2 does; the stripped `reference-proposal-report.docx` does not). The body-transplant approach the user originally landed at in their prior session was right for that broken reference but unnecessary once V2 is the input. Pandoc handles markdown → Word translation for free; we only need to ensure V2's styles.xml has the pStyles pandoc emits. Three iterations of UltraReview surfaced three missing pieces: `Compact`, `Table`, and per-pandoc-run numbering patches.
- **Sanitize V2 in-flight rather than ship verbatim.** The exemplar lives in the public ames-claude marketplace; bundling V2 as-is would leak BCBS project-specific content (banner text "Digital Infrastructure Strategy" embedded twice in `header1.xml` plus full content in document body and core.xml metadata). The build-exemplar-memo.py script clones V2 → strips → reinjects placeholder content + Oliver as creator → sanitizes app.xml stats, all in one pass.
- **Tighten docs to match script scope, broaden script only where the brand rule clearly demands.** When verifying brand-lint, the script's LINK-TEXT pattern was scoped to `[click here](url)` markdown link brackets (correct per the authoritative guide which uses "learn more" naturally on line 61) but SKILL.md described it as catching naked "click here" / "learn more" (incorrect). Fixed by clarifying the docs, not by adding FP-prone patterns. The PREMIUM rule was genuinely under-scoped — only `\bour premiums?\b` was matching despite the brand rule extending to "we charge premiums" and "premium rates." Added two patterns gated by `_is_about_us` so Medicare-context use elsewhere doesn't trip.
- **Stale memory inline-update over deferred spawn task.** The memory `feedback_bcbs_default_template.md` (predating v1.4.0) said "default to simple reference.docx" and contradicted the current skill's three-template decision tree. Per the auto-memory contract ("update or remove memories that turn out to be wrong"), updated the memory inline rather than waiting on the spawn task chip. New content preserves the historical "Why" arc but reflects current behavior: default = proposal-report, --template=memo for memos, --template=simple opt-in only.
- **Don't post-process `cp:lastModifiedBy`.** Pandoc rewrites core.xml from scratch on per-memo builds and only includes fields it has YAML values for. lastModifiedBy ends up missing — Word will auto-fill from system user on first save, so injecting it via clone-exemplar.py would be paternalistic and self-correcting anyway.

**Left off at**:
- **Resolved this session**: graphic banner missing on memos (was fixed via V2-as-exemplar); banner-text leak in header1.xml (sanitized in build-exemplar-memo.py); pandoc-bullet 720/360 looseness (fixed via clone-exemplar.py `--tight-bullets`); brand-lint premium under-scoping; brand-lint vs SKILL.md discrepancy on link text; stale `feedback_bcbs_default_template.md` memory; `--tight-bullets` documentation gap in SKILL.md (caught and fixed mid-UltraReview); the prior question "Should build-letterhead.sh validate pandoc-expected styles before running?" — partially resolved: clone-exemplar.py now warns when the exemplar is missing Title/Subtitle/Heading1/FirstParagraph.
- **Still open from prior entries**: sync-count auto-regen, publish script, postpublish hooks, `bcbs-wrap-up` cache version mismatch (resolves on marketplace refresh), legacy Asana-tagged items in BCBS notes still need Oliver triage, `ames-connectors` LICENSE, `codex-doctor --only-enabled` flag.
- **Spawn task open**: brand-lint patterns spec'd for "click here" / "learn more" naked-prose detection in CTA contexts — deferred because the authoritative guide's own example sentence shows "learn more" in legitimate prose, so any naked-phrase pattern would risk false positives. Spawn task documents the FP caveat.

**Open questions**:
- The `--tight-bullets` behavior is auto-applied to all `--exemplar=PATH` builds, including user-supplied references. If a future session names an exemplar with deliberate Word-default 720/360 bullets, the auto-tighten would override that intent without surfacing it. No opt-out flag — should there be a `--no-tight-bullets` escape hatch, or is the memo-family default-everywhere assumption fine?
- Sanitization of `app.xml` zeros the page/word/character counters (Word recalculates on first save) — should `core.xml`'s `cp:revision` field also be reset to 1 in the exemplar? Currently inherits V2's value of 14, which is misleading for a "fresh" template.

---

## 2026-04-24 — bcbs-wrap-up v1.6.0: Phase 5 naming check ported to Python

**What changed**: Replaced the bash `grep -qE` naming convention check in Phase 5 of `bcbs-wrap-up/SKILL.md` with a Python3 `os.walk` implementation. The bash version used `[^–]` in a grep extended-regex character class — macOS's BSD grep handles the en-dash as a multibyte UTF-8 sequence and produces false positives. The Python version uses native `str` Unicode comparisons (`'\u2013'`, `'\u2014'`) and is reliable across shells and locales. Confirmed 0 violations across the full BCBS directory with the new script. Plugin bumped 3.5.9 → 3.5.10; skill bumped v1.5.0 → v1.6.0. `./sync` regenerated both marketplace manifests.

**Decisions made**:
- **Python over fixed bash.** Could have fixed the bash by using `LC_ALL=C grep` or a raw byte check, but Python's unicode string model is the correct tool for filename character-class checks — no encoding surprises.
- **Update skill source, not just memory.** Per CLAUDE.md skill-maintenance rule: the skill is canonical; memory is only a recall cache. Both updated this session.

**Left off at**:
- **Resolved this session**: bash en-dash false-positive in Phase 5 (was open since 2026-04-23 entry).
- **Still open from prior entries**: sync-count auto-regen, publish script, postpublish hooks, legacy Asana-tagged items in BCBS notes still need Oliver triage, `ames-connectors` LICENSE, `codex-doctor --only-enabled` flag.

**Open questions**:
- Should `build-letterhead.sh` validate all expected pandoc styleIds are present in the reference doc before running pandoc?

---

## 2026-04-24 — bcbs-vt: pandoc styleId coverage 0% → 100%, BCBS typography fixed

**What changed**: `style-proposal-report.py` rewritten to cover every pandoc paragraph styleId (`Title`, `Subtitle`, `Author`, `Date`, `Heading1–4`, `BodyText`, `FirstParagraph`, `Compact`, `Caption`, `IntenseQuote`) plus a `Table` table-type style injected via raw XML (python-docx's paragraph-style API can't express table borders or firstRow conditional formatting). Design principle shifted from "preserve template styles, add missing" to "meet pandoc where it writes": the script now upserts each missing styleId by ID so Word never silently falls back to Normal. `Heading1` is left untouched — it's the load-bearing BCBS blue-band visual signature defined in the official `.dotx`. Typography corrected to Calibri 10pt body, navy `#00355E` titles. `SKILL.md` bumped v1.3.0 → v1.4.0 with a new "Canonical markdown shape for BCBS .docx output" section documenting the full pandoc shape contract. `reference-proposal-report.docx` regenerated and verified via Quick Look PNG (blue banner, navy title, blue-band headings, bordered table). Plugin bumped 3.5.8 → 3.5.9.

**Decisions made**:
- **upsert-by-styleId rather than name.** Pandoc looks up styles by their XML `styleId` attribute (e.g. `FirstParagraph`), not by the human-readable name. Matching by ID is the reliable path; matching by name is fragile against localized Word installs.
- **Table style via raw XML.** python-docx exposes no API for `w:tblStylePr` (conditional formatting) or `w:tblBorders`. Direct `lxml` injection is the only path that produces a properly styled header row and full grid borders.
- **Preserve Heading1 unconditionally.** The `.dotx` Heading1 (blue band, bold ALL-CAPS, `#00355E`) is the BCBS visual signature. Overwriting it — even to "fix" typography — would strip the brand identity. The script now documents this explicitly and makes it non-negotiable.

**Left off at**:
- **Still open from prior entries**: sync-count auto-regen, publish script, postpublish hooks, `bcbs-wrap-up` cache still at v3.5.3 (will update on next marketplace refresh), legacy Asana-tagged items in BCBS notes still need Oliver triage.
- **Still open**: bash en-dash check in Phase 5 produces false positives in zsh (UTF-8 multibyte); replace with Python snippet.

**Open questions**:
- Should `build-letterhead.sh` validate that all expected pandoc styleIds are present in the reference doc before running pandoc? A pre-flight check would surface this class of bug instantly.

---

## 2026-04-23 — bcbs-wrap-up skill evergreened: routing rules, dynamic discovery, Jira hygiene defaults

**What changed**: Second update to `bcbs-wrap-up/SKILL.md` in the same day, bumping skill v1.3.0 → v1.5.0 and plugin 3.5.6 → 3.5.8. Five new BCBS Operating Defaults added: (1) route to BAE vs OA by audience (team-facing vs personal); (2) only assign Jira issues to Oliver, never to teammates; (3) JQL duplicate check before creating any issue; (4) Jira descriptions must not reference source recordings, transcripts, or AI generation; (5) additional routing guidance explicitly making `Notes/Meetings/` a last-resort folder. Removed brittleness: replaced the hardcoded BAE workstream list (issue numbers + names) with a live JQL discovery instruction (`project = BAE AND issuetype = Workstream AND status != Done`); replaced the hardcoded evergreen-file list with a `find ~/Documents/BCBS/Notes -maxdepth 1 -name "*.md"` discovery + topic guidance; removed "as of 2026-04" date stamps; softened the "only assign Oliver" rule from naming specific teammates to the general principle (avoids stale names). `./sync` committed and pushed under `1ee91f0 publish: sync sources and update marketplace`. The motivation was a BCBS transcription session that produced 13 Jira issues across BAE and OA — the new defaults codify the lessons from that real-world run.

**Decisions made**:
- **Dynamic discovery over static lists.** The hardcoded workstream list would have been stale within weeks as issues close and new ones open. JQL is the live source of truth; the skill should delegate to it rather than encode a snapshot.
- **No source/recording references in Jira.** Confirmed preference during session: descriptions should read as natural task context indistinguishable from a human note — never reveal they came from a meeting recording.
- **v1.4.0 → v1.5.0 in one session.** Two rounds of edits were needed (1.4 added the new rules, 1.5 removed the brittleness). Separate version bumps keep the changelog readable if the git history is inspected later.

**Left off at**:
- **Still open from prior entry**: sync-count auto-regen, publish script, postpublish hooks, `bcbs-wrap-up` cache still at v3.5.3 (will update on next marketplace refresh), legacy Asana-tagged items in BCBS notes still need Oliver triage.
- **NEW**: The bash naming-convention check script in Phase 5 produces false positives on en-dash detection in zsh — the `[^\xe2]` character class doesn't handle UTF-8 multibyte chars correctly. A Python replacement confirmed 0 real violations. The skill's bash snippet should be rewritten with Python for reliability (or a pre-built script).

**Open questions**:
- Should the naming audit section in Phase 5 be replaced with a Python snippet rather than the fragile bash `grep -qE` approach?

---

## 2026-04-23 — bcbs-wrap-up skill hardened: Jira canonical, never-close rule, legacy-tag migration

**What changed**: Updated `plugins/ames-standalone-skills/skills/bcbs-wrap-up/SKILL.md` from v1.1.0 to v1.2.0 with four new operating rules: (1) Jira is the canonical task system; Asana, Apple Reminders, Todoist, and other systems are not sources of truth; (2) strikethrough without a `(→ Jira: ...)` tag is stale and must be reconciled during wrap-up; (3) legacy `(→ Asana: ...)` and `(→ Reminders: ...)` tags must be migrated into Jira (flag during Phase 3, prompt for confirmation, create the Jira issue, overwrite the local tag); (4) wrap-up never closes a Jira issue — it verifies existence, creates missing, migrates legacy tags, but does not transition anything to Done or toggle local checkboxes to `[x]` based on a same-session deliverable; deliverables get an inline "Draft delivered YYYY-MM-DD at <path>" note with the checkbox left unchecked. Phase 3 rewritten end-to-end to match. Evergreen list updated to move `BCBS VT – Task Tracker.md` into a new "Phased-out files" subsection (do not append new tasks; treat as read-only archive; surface live items during Phase 3). Plugin package bumped 3.5.4 → 3.5.5 on both `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`. `./sync` regenerated `.claude-plugin/marketplace.json` (6 plugins) and `.agents/plugins/marketplace.json` (4 plugins). Both manifests validate as JSON. `validate-skill` passes on the modified skill. Session producer work occurred outside this repo at `~/Documents/BCBS/` (social media strategy deliverables); only the skill source and plugin metadata are in this worklog scope.

**Decisions made**:
- **Edited the iCloud source, not just the plugin cache.** First pass wrote the skill change to `~/.claude/plugins/cache/ames-claude/ames-standalone-skills/3.5.3/skills/bcbs-wrap-up/SKILL.md`, which is a cache that gets overwritten on the next marketplace sync. User caught this and pointed me at the iCloud source path. `cp cache source` brought them into parity; verified with `diff` (zero difference). Memory candidate: when editing any skill, always confirm the change landed in the iCloud source before declaring done — the cache is derivative.
- **Wrap-up-never-closes rule treated as a first-class operating default, not buried in Phase 3.** Earlier draft only mentioned it in the Phase 3 body. Elevating it to the top-level Operating Defaults section makes the rule discoverable to any future edit pass and matches the prominence the user signaled ("no task in Jira should be considered done by this session").
- **Legacy Asana/Reminders migration is a wrap-up responsibility, not a deferred sweep.** Alternative considered: leave legacy tags in place and only flag them in the summary report. Chose active migration because legacy tags accumulate otherwise and silently erode the "strikethrough means Jira" invariant. The skill now names the migration as an in-wrap action with explicit user confirmation.
- **`BCBS VT – Task Tracker.md` deleted from `~/Documents/BCBS/Notes/` per user's option 3.** The file had 220 lines of Asana-tagged items. Skill now flags its absence and routes future live-item surfacing through Phase 3 from whatever notes survive. No backup retained because the user explicitly chose delete-entirely and the content was superseded by Jira.
- **Patch bump 3.5.4 → 3.5.5 rather than minor bump.** No new plugin added, no new skill added, no breaking API change — just a content and rule change inside an existing skill. Patch is the right semver category.

**Left off at**:
- **NEW: Codex cache at `~/.codex/plugins/cache/ames-claude/ames-standalone-skills/3.5.4/` still shows skill v1.1.0.** The iCloud source now has v1.2.0 and the Claude cache at 3.5.3 has v1.2.0. Codex cache will update on next plugin refresh; did not touch directly because cache writes get reverted on sync.
- **NEW: `BCBS VT – Task Tracker.md` removal may leave live Asana-tagged items orphaned.** The tracker had ~30 items tagged `(→ Asana: Content & Brand Strategy)`, `(→ Asana: Platform & Account Setup)`, etc. Per the skill's new migration rule, those items should be re-created in Jira. Handing off to Oliver to triage whether each is still live.
- **NEW: Should `ames-standalone-skills:bcbs-wrap-up` skill version (1.2.0) be tracked in the WORKLOG or just the plugin package version (3.5.5)?** Individual skill versions are not currently rolled up into marketplace.json; only the plugin package version ships. Not a blocker today.
- **Still open from prior entries**: sync-count auto-regen for CLAUDE.md, `publish` script end-to-end, postpublish hooks in meta/sprout/imagerelay/unifi, ImageRelay 1P fallback verification, UniFi 1P item, `bcbs-meeting-notes` real-world run, `~/.config/1Password/ssh/agent.toml` update, icon/logo asset for README header, `ames-connectors` LICENSE, two informational `codex-doctor` cache warnings, `--only-enabled` flag on `codex-doctor`, `sync-sources` retire decision.
- **Resolved this session**: bcbs-wrap-up skill needed explicit Jira-only operating default (was ambiguous between Jira, Asana, Reminders); needed explicit never-close rule; needed legacy-tag migration step; needed to retire the MD task tracker reference.

**Open questions**:
- Does `./sync` need to round-trip skill-level version metadata into marketplace.json alongside the plugin package version, so a skill content bump is visible in the marketplace entry without needing the user to read SKILL.md frontmatter?
- Should the `bcbs-wrap-up` skill grow a dry-run mode that only reports legacy-tag migrations as candidates without creating Jira issues, for sessions where Oliver wants to triage before migration?

---

## 2026-04-22 — Whole-project audit, hygiene sweep, MCP plugin READMEs, Codex marketplace local→Git

**What changed**: Ran a multi-agent audit across 5 dimensions (manifests/parity, skills quality, shell scripts, MCP configs, docs/tidiness), then dispatched 4 Sonnet 4.6 implementation agents in parallel (grouped by file ownership, not severity, to avoid edit conflicts). Script hardening across `sync`, `bump-and-sync`, `codex-doctor`: atomicity via `.bak`+restore-on-sync-failure, `set -euo pipefail`, guarded `json.load`, `is_dir` loop guards, active flat-`.mcp.json` enforcement (converts silent bug-enabler into fail-fast error), tomllib-based TOML parsing with inline-comment-stripping fallback, word-boundary MCP name match (no more `pandoc` matching inside `mcp-pandoc`). Codex marketplace parity: `sync` now propagates `metadata.version` and per-entry `version` to `.agents/plugins/marketplace.json`. Docs reconciliation: `AGENTS.md` 5→6 plugins, `README.md` standalone-skills count drift 28→29, 3 new `CLAUDE.md` gotchas (bump-and-sync atomicity, flat-mcp enforcement, category-casing duality between Claude kebab-case `category` and Codex title-case `interface.category`), expanded Skill convention to cover workspace/state dirs. Relocated `plugins/ames-standalone-skills/skills/.a5c` and `.remember` to plugin root (orphan dot-dirs under `skills/` would trip the Cowork validator). Deleted empty `plugins/.claude/`, `drafts/`, `__pycache__/`. Rewrote `liquid-glass/SKILL.md` description with trigger phrases. Added MIT LICENSE at repo root (previously missing despite every plugin.json declaring MIT). Wrote per-plugin READMEs for `ames-dev-mcps` and `ames-general-mcps` explaining the split-by-use-case rationale, following `readme-style`; patch-bumped both (1.0.0→1.0.1, 3.0.0→3.0.1). Final git: 4 commits (`b0d33ca`, `aee3616`, `3dd6f43`, `025c864`), all on `origin/main`. Separately, migrated `~/.codex/config.toml` `[marketplaces.ames-claude]` from `source_type = "local"` to `source_type = "git"` via `remove` + `add oliverames/ames-claude`; deleted stale cache dirs (`ames-preferred-mcps/2.0.2/`, `ames-ynab/2.0.1/`); removed orphan `[plugins."ames-preferred-mcps@ames-claude"]` section. Backup at `~/.codex/config.toml.backup-20260422-132315-claude-audit-cleanup`. Verified `ames-connectors` was already Git-sourced in both Codex config and Claude's `extraKnownMarketplaces`.

**Decisions made**:
- **Trust-but-verify caught a false positive.** Audit agent flagged `testflight-deployment/SKILL.md` name as display-case; a direct Read showed it was already kebab-case (fixed earlier in `b874ef3`). Skipped the no-op edit. Pattern: always Read the claimed file before acting on an audit finding.
- **Parallel agent dispatch grouped by file ownership, not severity.** Initial A–D priority grouping would have conflicted on `bump-and-sync` and `CLAUDE.md`. Final grouping (scripts / skills / docs / cleanup) each owned a distinct subset; I merged `CLAUDE.md` addenda from three agents post-hoc as one edit.
- **Codex marketplace `version` parity fixed by propagating, not documenting omission.** `codex-doctor` only validates `name`, `interface.displayName`, and `plugins`, so extra fields are accepted. Safer to include `version` for symmetry with the Claude side than to paper over the gap in docs.
- **Converted the dead defensive branch in `sync:99-100` into an active guard.** Original code silently handled a pre-wrapped `mcpServers` in Claude `.mcp.json`; per CLAUDE.md the shape must be flat. New code exits with an error pointing at the convention. "Turn silent bug-enabler into fail-fast" pattern.
- **Declined progressive-disclosure splits for `humanizer` (559 lines) and `1password-vault` (505 lines) SKILL.mds.** Both are procedural (read start-to-finish when fired), not reference-style. Splitting procedural skills breaks reading flow; progressive disclosure pays off when readers jump to a specific section.
- **Declined top-level `CHANGELOG.md`.** `WORKLOG.md` + git log cover narrative for a personal marketplace; revisit if the repo grows external consumers.
- **Auto-enabled nothing on the Codex side.** User's Codex config has 2 of 4 dual-host plugins enabled (`ames-standalone-skills`, `ames-community-skills`); `ames-dev-mcps` and `ames-general-mcps` are not enabled. Left that to explicit user action. Claude side already has all 6 plugins enabled.
- **Codex marketplaces should be Git, not local paths** — user explicitly corrected this mid-session when `codex plugin marketplace upgrade ames-claude` failed. Saved as `feedback_codex_marketplace_git.md` memory. Also saved the `config.toml.backup-YYYYMMDD-HHMMSS-<purpose>` pattern as `feedback_codex_config_backup.md`.

**Left off at**:
- **NEW: Two `codex-doctor` warnings remain, informational only** — "Codex cache for ames-dev-mcps is not at v1.0.1" and "...ames-general-mcps is not at v3.0.1". They fire because those plugins aren't enabled in `~/.codex/config.toml`, so their content isn't cached. To start using them on Codex, add `[plugins."ames-dev-mcps@ames-claude"]` / `[plugins."ames-general-mcps@ames-claude"]` with `enabled = true`.
- **NEW: `ames-connectors` still has no LICENSE file.** `ames-claude` now has one; the sibling repo should match for the same legal-clarity reason (plugin.jsons declare MIT but no LICENSE backs the claim).
- **NEW: `codex-doctor --only-enabled` flag?** The cache-not-at-version warnings are strictly operational — they suggest an action (install) for plugins the user may have deliberately chosen not to install. A flag to suppress would reduce doctor noise.
- **NEW: The `sync-sources` script in `ames-general-mcps` has a refreshed header but the script itself is legacy.** Still earning its keep, or ready for deletion?
- **Still open from prior entries**: sync-count auto-regen for CLAUDE.md, `publish` script end-to-end, postpublish hooks in meta/sprout/imagerelay/unifi, ImageRelay 1P fallback verification, UniFi 1P item, `bcbs-meeting-notes` real-world run, `~/.config/1Password/ssh/agent.toml` update, icon/logo asset for README header.
- **Resolved this session**: `bump-and-sync` retirement-or-not question (now significantly hardened; less urgent to retire), orphan dot-dirs under `skills/` (moved out), stale `ames-preferred-mcps@ames-claude` in Codex config (removed), local→Git marketplace migration for `ames-claude`.

**Open questions**:
- The 2 `codex-doctor` cache warnings are a UX concern — they suggest "install" for plugins the user may have deliberately chosen not to enable. Worth a `--only-enabled` flag on `codex-doctor`, or just leave as informational noise?
- Should future `codex plugin marketplace add` tooling auto-enable replacement plugins when migrating across a rename (e.g. `ames-preferred-mcps` → `ames-dev-mcps` + `ames-general-mcps`), or keep `[marketplaces.*]` and `[plugins.*]` orthogonal?

---

## 2026-04-22 — Split ames-preferred-mcps into ames-dev-mcps + ames-general-mcps

**What changed**: Split the 13-server `ames-preferred-mcps` plugin into two focused plugins based on use-case boundaries. Created new `ames-dev-mcps` (v1.0.0) with 6 development-oriented servers: `apple-docs`, `apple-notifier`, `macos-automator`, `XcodeBuildMCP`, `SimGenie`, and `sosumi`. Renamed `ames-preferred-mcps` → `ames-general-mcps` (bumped 2.0.2 → 3.0.0 for the breaking rename + trimmed content) with 7 day-to-day servers: `drafts`, `excel`, `google-workspace`, `iMCP`, `pandoc`, `peekaboo`, `markitdown`. Used `git mv` (via directory rename) so history follows both `.mcp.json`, `sync-sources`, and `.codex-plugin/mcp.json`. Ran `./sync` to regenerate both marketplace manifests and propagate metadata to the Codex manifests. Updated `CLAUDE.md`: plugin count (5→6), Codex plugin count (3→4), plugin table with the two new rows. Updated `README.md` across ten locations: header count, install examples (declarative settings.json and interactive slash-command), plugins table, `ames-preferred-mcps` section replaced with two sections (`ames-dev-mcps` + `ames-general-mcps`), MCP catalog, architecture host-plugin table, credentials table, enabled-plugins snapshot (flagged stale settings.json key), and credentials runtime note. Validated all 10 JSON manifests parse cleanly. Committed (`b0d8730 split mcps: ames-dev-mcps + ames-general-mcps`) and pushed.

**Decisions made**:
- **Split by use-case, not by technical attribute.** Initial instinct was to group by server type (e.g. stdio vs http, steipete-authored vs other). User redirected twice during the session to refine the split — the final boundary reflects "what will I reach for while coding" vs "what will I reach for day-to-day" rather than anything intrinsic about the servers. `apple-notifier` and `sosumi` ended up in dev because they tend to come up mid-build; `peekaboo` and `iMCP` ended up in general because they're used independent of any coding task.
- **Rename via `git mv` (implicit through directory rename), not delete+create.** Preserved history for `.mcp.json`, `sync-sources`, and `.codex-plugin/mcp.json` — `git status` correctly detected the moves as renames (51–100% similarity). A delete+create would have lost `git log --follow` traceability across the rename.
- **Major version bump for `ames-preferred-mcps` (2.0.2 → 3.0.0) rather than patch.** The plugin name changed and 5 servers were removed; both are breaking for anyone with the plugin installed. New plugin `ames-dev-mcps` started at 1.0.0 as convention for a net-new plugin.
- **Flagged settings.json drift in the README rather than silently fixing it.** The user's `~/.claude/settings.json` still references `ames-preferred-mcps@ames-claude` — I updated the documented snapshot to say "3 of 6" and called out that the stale key needs replacing on the next session, rather than editing settings.json mid-wrap-up (settings.json wasn't my file to modify and the user has their own drift-check ritual).
- **Kept `sync-sources` script with `ames-general-mcps`, not duplicated to `ames-dev-mcps`.** The script is a legacy helper from the pre-1Password-MCP-removal era and carrying it forward as-is through the rename was lower-effort than splitting its contents. A future cleanup can retire or re-scope it.

**Left off at**:
- **NEW: `~/.claude/settings.json` `enabledPlugins` still lists the old `ames-preferred-mcps@ames-claude` key.** Next session should replace with `ames-dev-mcps@ames-claude` and `ames-general-mcps@ames-claude`. The stale key will be inert (plugin no longer exists in the marketplace) but the user's config record in README reflects the drift.
- **NEW: Consider whether `sync-sources` in `ames-general-mcps` still earns its keep.** Ships with the plugin but likely no caller. Audit and retire or document intended use.
- **NEW: Verify installed plugin caches refresh after the rename.** After marketplace auto-update, `~/.claude/plugins/cache/ames-claude/ames-preferred-mcps/` will become orphaned; the `ames-dev-mcps/` and `ames-general-mcps/` caches will populate on next Claude Code launch.
- **Still open from prior entries**: sync-count auto-regen for CLAUDE.md, `bump-and-sync` retirement decision, `publish` script end-to-end, postpublish hooks in meta/sprout/imagerelay/unifi, ImageRelay 1P fallback verification, UniFi 1P item, `bcbs-meeting-notes` real-world run, `~/.config/1Password/ssh/agent.toml` update, LICENSE file decision for ames-connectors, icon/logo asset for README header, `codex marketplace add` CLI syntax verification, shared helper for Codex-derived `update.sh` scripts.

**Open questions**:
- Should the marketplace `metadata.version` (currently 3.5.0) bump to reflect this structural change, or is a per-plugin major bump sufficient signal? Indexers may use metadata.version to re-crawl.
- Is `macos-automator` correctly in `ames-dev-mcps`? It's used as much for general scripting as for dev workflows. Keep an eye on whether day-to-day automation use makes it feel misplaced.

---



**What changed**: Audited both ames-claude and ames-connectors marketplaces against the official Claude Code and Codex plugin schemas. Both were structurally compliant but carried minimal metadata on the Claude side (just `name`/`version`/`description`/`author`). Enriched every Claude plugin.json across both repos with `homepage`, `repository`, `license`, `keywords`, and `category`. Taught `ames-claude/sync` to thread those fields plus `author` from per-plugin manifests into the generated marketplace entry, keeping `.claude-plugin/plugin.json` as the single source of truth. Created a parallel `sync` script at `ames-connectors` root (previously hand-edited `marketplace.json`); it mirrors the ames-claude pattern — version propagation, flat→wrapped MCP wrapping, enriched metadata propagation. Cleaned `ames-preferred-mcps` description (dropped the `sync-sources` implementation leak). Patch-bumped every touched plugin and both marketplace `metadata.version` fields (ames-claude 3.4.0→3.5.0; ames-connectors 1.1.0→1.2.0). Polished both READMEs per `/readme-style`: added missing License badge to ames-claude header, refreshed the plugins version table, documented the new sync-propagation behavior in the Versioning section. For ames-connectors (which was missing install instructions entirely), added a full Quick Start with declarative and interactive install paths for both hosts, an Architecture section documenting the dual-host manifest pattern, a Development section with bump/refresh/add workflows, and a `category` column on the connectors table. Validated 38 JSON files across both repos parse cleanly; confirmed sync is idempotent (second run is a no-op). Also investigated why the plugin browser shows a stale "Codex" card by Oliver Ames with a synthesized "Apple platform development skills ported from..." description: traced it to commit `ca382bf` (before the April 17 split), confirmed no local cache or installed plugin entry references it anymore, concluded it's almost certainly a stale server-side index in Claude's cloud plugin directory. The metadata.version bump is the signal an indexer uses to re-crawl; the push should resolve it on the indexer's next sweep.

**Decisions made**:
- **Enriched plugin.json wins over marketplace-entry-only enrichment.** Could have typed the new fields into marketplace.json directly since the Claude Code schema accepts them there too. Chose plugin.json as the single source and taught sync to propagate, so future edits never touch generated files.
- **Added sync script to ames-connectors rather than leaving marketplace.json hand-edited.** Mirrors the ames-claude pattern. Trivial to maintain once, pays off on every future bump. The ames-connectors `sync` is identical to ames-claude's except for the header string — a deliberate copy, not shared code, since the two repos should stay operationally independent.
- **Patch bumps, not minor.** Per ames-claude version policy (patch = content tweaks), metadata enrichment is a patch. Minor would have been reserved for new skills/commands/MCPs.
- **Minor bump for marketplace metadata.version.** 3.4.0→3.5.0 (ames-claude) and 1.1.0→1.2.0 (ames-connectors). Signals materially-changed metadata to indexers, and marks the boundary between "flat" and "enriched" marketplace content. Plugin-level patches roll up to a marketplace minor.
- **The "Codex" card is a stale index, not UI grouping.** Initial diagnosis was wrong — assumed Claude Code's browser was algorithmically grouping `build-ios-apps-codex` + `build-macos-apps-codex` into a "Codex" card. User pushed back; thorough grep across git history + caches + installed plugins revealed the exact description came from a real, since-retired `plugins/codex/.claude-plugin/plugin.json` at commit `ca382bf`. Lesson: always grep for literal strings before reaching for a UI-behavior explanation.
- **Didn't touch Apple Notes in the Tech folder.** Both `🧰 ames-claude marketplace` and `🛒 Marketplaces` describe the "what" (5 plugins, dual-host layout); today's changes were about the "how" (metadata propagation mechanics). That belongs in CLAUDE.md + README, not the high-level reference notes.

**Left off at**:
- **NEW: Watch Claude's cloud plugin directory for the stale "Codex" card to refresh.** After the push, the indexer should re-crawl on its schedule. If the card persists past a reasonable window, force-refresh via the plugin panel or bump metadata.version again with a dummy change.
- **NEW: Consider extracting the two sync scripts into a shared helper.** ames-claude/sync and ames-connectors/sync are near-identical. If a third marketplace appears, promote to `~/Developer/Scripts/sync-marketplace` with a thin per-repo wrapper.
- **NEW: Teach sync to regenerate CLAUDE.md's top-of-file counts.** Hit the same drift this session as the prior worklog flagged — "5 plugins, 47 skills, 13 MCP servers" was stale before I caught it. Either extend sync or add a `./bump-claude-md-counts` helper.
- **Still open: Run a fresh backup before deleting `ames-claude-backup`.** Carried from prior entry — decide whether to archive or `rm -rf` after next backup sweep confirms parity.
- **Still open: Decide whether `bump-and-sync` in this repo is still earning its keep.** Its only documented caller (ynab-mcp-server postpublish) now targets `ames-connectors`; confirm nothing else chains into it before retiring.
- **Still open: ames-lytho enablement decision** — published in ames-connectors but not enabled at user level.
- **Still open from prior entries**: `publish` script end-to-end, ImageRelay 1P fallback verification, UniFi 1P item, `bcbs-meeting-notes` real-world run, postpublish hooks in meta/sprout/imagerelay/unifi, `~/.config/1Password/ssh/agent.toml` update, LICENSE file decision for ames-connectors (repo has LICENSE but ames-claude doesn't), icon/logo asset for README header, verify `codex marketplace add` CLI syntax, test Claude Code's skill auto-discovery on the promoted `build-ios-apps-codex` / `build-macos-apps-codex` layout, consider a shared helper for the two Codex-derived plugin `update.sh` scripts.
- **Resolved this session**: the "UI grouping" mystery around the Codex card — confirmed stale cloud index, not anything local.

**Open questions**:
- Should the sync scripts additionally verify that `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` stay in lockstep on all propagated fields (not just version)? Today if someone hand-edits Codex-side metadata, sync won't notice. Low probability of occurring given the convention, but worth a one-time lint pass.
- Now that ames-claude's own Claude plugin.json files carry `category`, should the Codex plugin.json files stop duplicating it and instead read through a shared field? Probably no — Codex's schema interprets `category` differently (e.g. uses title-case "Productivity" in `interface.category`), so parallel fields with different casing conventions is the cleanest split.

Part of a broader session that also touched ames-connectors.

---

## 2026-04-21 (audit) — Reconcile after Codex's connector split: divergence fix, orphan cleanup, memory + notes + CLAUDE.md sync

**What changed**: Ran a full audit of plugin marketplace state after Codex reorganized things during the morning rate-limit window. Discovered Codex had split first-party connectors (`ames-ynab`, `ames-lytho`) into a new `ames-connectors` marketplace (github.com/oliverames/ames-connectors), added `build-ios-apps-codex` and `build-macos-apps-codex` to `ames-claude`, registered the `openai-codex` marketplace, and trimmed unused MCPs from `ames-preferred-mcps`. Local `main` had diverged from origin: 1 ahead (a local `./sync` regen commit) / 1 behind (Codex's "Move connector plugins to ames-connectors" commit). Pulled with rebase — clean, no conflicts — and pushed. Deleted orphan `plugins/ames-ynab/` and `plugins/ames-lytho/` directories that iCloud preserved after git removed them. Removed the project-scoped `apple-events` MCP from `~/.claude.json` (the only non-plugin MCP anywhere in the config) via `claude mcp remove apple-events -s local`. Deleted `~/.claude/settings.local.json` (shouldn't exist per convention). Updated four Apple Notes in the `💻 Tech` folder: rewrote `🧰 ames-claude marketplace` for the 5-plugin layout, rewrote `🛒 Marketplaces` with the new 11-marketplace layout grouped by source (Anthropic/Personal/Third-party), patched `🧩 Lytho MCP Server` to point at `ames-connectors/plugins/ames-lytho`, and created a new `💻 Claude Code Setup` note as a comprehensive reference for `~/.claude` configuration. Updated project memory: rewrote `project_ames_claude.md` with the 5-plugin list and connector-split context, created `project_ames_connectors.md` for the new marketplace, updated the `MEMORY.md` index. Patched `CLAUDE.md` in this repo: fixed stale "7 plugins, 46 skills, 15 MCP servers" → "5 plugins, 46 skills, 13 MCP servers", removed `ames-ynab` and `ames-lytho` rows from the plugin table, updated both `bump-and-sync` references to note that the `ynab-mcp-server` postpublish hook now targets `ames-connectors`.

**Decisions made**:
- **Rebase, not merge, for the divergence.** Local had a `./sync` regen commit; origin had the substantive "Move connector plugins" commit. Rebasing the sync on top kept history linear; merge would have added a merge commit for no real reason. Clean rebase with no conflicts meant the marketplace regen didn't touch the removed connector rows.
- **Remove `apple-events` rather than wrap as a plugin.** The project-scoped MCP was registered via `claude mcp add --scope project` at some point and loaded for the whole `~/Developer` tree. User opted to remove. If it's ever needed again, wrap as a plugin under `ames-preferred-mcps` for visibility and version control.
- **Learned: `claude mcp remove -s project` vs `-s local`.** First attempt used `-s project` which looks for `.mcp.json` in the project dir; the right scope for entries in `~/.claude.json`'s `projects.<path>.mcpServers` block is `-s local`. Saved as a feedback memory.
- **Split the memory entry.** `project_ames_claude.md` stays focused on the skills + MCP-bundle repo; new `project_ames_connectors.md` covers the connectors marketplace. Duplicating the connector details in both would rot fast; cross-references keep discoverability.
- **Don't delete `ames-claude-backup` yet.** User wants to run a new backup pass later; leave the 16:41 snapshot in place.
- **New note `💻 Claude Code Setup` rather than padding existing ones.** The existing `🛒 Marketplaces` note was marketplace-centric; stuffing env vars, hooks, and permissions into it would bloat its scope. New note absorbs the broader config reference; `🛒 Marketplaces` stays slim and points at it.
- **Skip skill-level detail in plugin lists.** Per user: "No need to document skills within the plugins." Counting skills rots fast; the repo README is the authoritative skill inventory.

**Left off at**:
- **NEW: Run a fresh backup before deleting `ames-claude-backup`.** User explicitly asked to keep it; decide later whether it merits permanent archival or can be `rm -rf`'d after the next backup sweep confirms parity.
- **NEW: Extend `./sync` to regenerate CLAUDE.md's top-of-file counts.** The plugin/skill/MCP counts drifted again this session because the connector-split bypassed the hand-maintained CLAUDE.md. Either teach `./sync` to regenerate those three lines or add a `./bump-claude-md-counts` helper.
- **NEW: Decide whether `bump-and-sync` in this repo is still earning its keep.** Its only documented caller (ynab-mcp-server postpublish) now targets `ames-connectors`. If nothing else chains into it, retire.
- **Still open: ames-lytho enablement decision** — published in `ames-connectors` but not enabled at user level. Prior worklog flagged this.
- **Still open from prior entries**: `publish` script end-to-end, ImageRelay 1P fallback verification, UniFi 1P item, `bcbs-meeting-notes` real-world run, postpublish hooks in meta/sprout/imagerelay/unifi that still call `bump-and-sync` for removed plugin entries, `~/.config/1Password/ssh/agent.toml` update, LICENSE file decision, icon/logo asset for README header, verify `codex marketplace add` CLI syntax, test Claude Code's skill auto-discovery on the promoted `build-ios-apps-codex` / `build-macos-apps-codex` layout, consider a shared helper for the two Codex-derived plugin `update.sh` scripts.
- **Resolved this session**: dangling `ames-claude-only@ames-claude` key in `~/.claude/settings.json` — no longer present (confirmed via grep), whether Codex cleaned it or a prior session did.

**Open questions**:
- Should `ames-connectors` get a local checkout at `~/Developer/Projects/ames-connectors` for parity with how `ames-claude` lives on disk, or is Codex-only development the intended model? Currently only the Claude Code marketplace cache clone exists locally; the canonical is GitHub.
- Should the new `💻 Claude Code Setup` Apple Note be what the `wrap-up` skill's config-drift check targets instead of (or in addition to) the repo README? Duplication risk if both stay in sync, but Apple Notes is the more mobile-accessible reference.

---

## 2026-04-21 — Trim preferred MCP bundle, keep marketplace replacements parked

**What changed**: Removed `1password`, `docling`, and `shortcuts` from `ames-preferred-mcps`, leaving 13 preferred MCP servers: `apple-docs`, `apple-notifier`, `drafts`, `excel`, `google-workspace`, `macos-automator`, `pandoc`, `peekaboo`, `XcodeBuildMCP`, `iMCP`, `SimGenie`, `sosumi`, and `markitdown`. Removed the `shortcuts-mcp-server` install/update path from `plugins/ames-preferred-mcps/sync-sources`. Bumped `ames-preferred-mcps` from 1.4.0 to 2.0.0 across Claude and Codex plugin manifests, regenerated `.claude-plugin/marketplace.json` with `./sync`, and updated README/CLAUDE/AGENTS counts from 18 to 15 total MCP servers and 16 to 13 preferred MCP servers. Also checked current Claude Code marketplace availability for the remaining preferred MCPs: only `XcodeBuildMCP` had a clear community Claude plugin listing; user explicitly said to ignore that for now.

**Decisions made**: Removal was treated as a major version bump because deleting three MCP servers changes the plugin's public capability surface. Marketplace-generated files were updated via `./sync` rather than hand-edited. The MCP registry findings were not acted on because the user clarified they care about Claude Code plugin marketplaces, not generic MCP directories, and then asked to park the replacement work for now.

**Left off at**: NEW: If/when replacing bundled MCPs with upstream Claude plugin marketplace installs, start with `XcodeBuildMCP`; it was the only exact Claude marketplace hit found this session. Still open from prior entries: `publish` script end-to-end, ImageRelay 1P fallback verification, UniFi 1P item, `bcbs-meeting-notes` real-world run, postpublish hooks in meta/sprout/imagerelay/unifi still call `bump-and-sync` for removed plugin entry, disable `ames-original-connectors` / enable `ames-ynab` in plugin UI, `~/.config/1Password/ssh/agent.toml` update for home-server key id (only if agent path needed), LICENSE file decision, icon/logo asset for README header, verify `codex marketplace add` CLI syntax on next real Codex use. Still open: `ames-lytho` enablement decision. Still open: `~/.claude/settings.json` has a dangling `"ames-claude-only@ames-claude": true` key pointing at a retired plugin. Still open: test Claude Code's skill auto-discovery on the promoted `build-ios-apps-codex` / `build-macos-apps-codex` layout. Still open: consider a shared helper for the two Codex-derived plugin `update.sh` scripts if a third similar plugin appears.

**Open questions**: Should `XcodeBuildMCP` eventually leave `ames-preferred-mcps` in favor of the community Claude marketplace plugin, or stay bundled for consistent config/version control? Should the preferred MCP bundle stay as a Claude-plugin wrapper until each server has a true Claude marketplace entry, even when generic MCP registries already list the server?

---

## 2026-04-17 (evening) — Promote Codex-derived skills to top-level plugins, retire ames-claude-only

**What changed**: Refactored the marketplace layout to fix a nested-skill auto-discovery concern flagged in the afternoon session's review notes. Moved `build-ios-apps-codex` (6 skills) and `build-macos-apps-codex` (11 skills + 3 commands) from nested bundles at `plugins/ames-claude-only/skills/<bundle>/skills/<sub>/` up to top-level plugins at `plugins/<bundle>/skills/<sub>/`. Used `git mv` to preserve per-file history (74 renames tracked as R entries). Deleted the redundant router `SKILL.md` wrappers (~131 lines combined) that sat at each bundle level and only pointed at the sub-skills. Retired the `ames-claude-only` umbrella plugin entirely (`git rm -rf`) — its sole purpose was housing those two bundles. Bumped `.claude-plugin/marketplace.json` `metadata.version` 3.2.0 → 3.4.0. Ran `/simplify` with three parallel review agents (reuse, quality, efficiency), which caught 9+ stale references to `ames-claude-only` in `README.md` I'd missed: install examples, plugin table, dedicated section, architecture table, skill-count summary, gotchas, version, enabled-plugins snapshot, upstream credit. Also caught a stale example in `sync`'s pass-3 comment, a misleading `# Sync skills (skip openai.yaml agent files)` comment in both `update.sh` scripts (loop doesn't actually filter yaml; skips by omission), and drift-risk in the new plugin.json descriptions that enumerated every skill name. Fixed all. Shortened plugin.json descriptions to match `ames-standalone-skills` style. Trimmed the CLAUDE.md plugin-table rows for the two new plugins to match sibling-row terseness. Updated Apple Notes `💻 Tech/🧰 ames-claude marketplace` from "6 plugins, 31 skills" to "7 plugins, 46 skills" with the retirement note. Committed as `2b51... refactor(marketplace): promote Codex-derived skills to top-level plugins` plus a follow-up `2ad0d1f chore(codex-sync): drop misleading "skip openai.yaml" comment` for two `update.sh` edits that slipped past staging because `git mv` captured the rename before the Edit touched content. Pushed both.

**Decisions made**:
- **Promote to top-level, don't fix the wrapper.** Claude Code's skill auto-discovery is shallow (walks `plugins/<name>/skills/<skill>/SKILL.md` one level deep). The previous nested layout put 17 sub-skills at a depth the loader doesn't traverse. Could have preserved the umbrella and added a plugin-level auto-discovery hack; instead, the ecosystem-idiomatic shape is one-plugin-per-bundle. Promotion is lower-drift than pursuing a workaround.
- **Retire `ames-claude-only` entirely rather than repurpose as an empty shell.** Presented three options (delete, keep as placeholder, keep as migration breadcrumb). User chose delete. The CLAUDE.md convention elsewhere is "no empty plugins in the marketplace"; git history preserves the record if it ever needs resurrection.
- **Bump marketplace `metadata.version` to 3.4.0**, not 3.3.0. User decision. The repo's convention for this field is informal (it lagged at 3.2.0 while individual plugin versions advanced), so a two-step bump signals "this is a structural change worth noticing" rather than a patch.
- **Claude-only by design, no `.codex-plugin/plugin.json` on either new plugin.** Their upstream is `openai/plugins` (build-ios-apps, build-macos-apps Codex plugins); republishing back to Codex would collide with the upstream and create a diverged twin. The `sync` script already treats missing `.codex-plugin/` as the "Claude-only" signal, so no code change was needed — just the absence of the file.
- **Descriptions should not enumerate skill names.** The first-draft plugin.json descriptions listed every skill (`ios-app-intents`, `swiftui-liquid-glass`, ...). Agent 1 flagged this as drift risk: when `update.sh` adds/removes an upstream skill, descriptions silently go stale. Changed to count + capability summary per `ames-standalone-skills` precedent.
- **Separate commit for the `update.sh` comment drop** rather than amend. User's CLAUDE.md prefers new commits over amendment. The first commit's body mentioned the comment drop, so the follow-up's subject explicitly notes it as a squash-follow to avoid log-reader confusion.

**Left off at**:
- **Still open from prior entries**: `publish` script end-to-end, ImageRelay 1P fallback verification, UniFi 1P item, `bcbs-meeting-notes` real-world run, postpublish hooks in meta/sprout/imagerelay/unifi still call `bump-and-sync` for removed plugin entry, disable `ames-original-connectors` / enable `ames-ynab` in plugin UI, `~/.config/1Password/ssh/agent.toml` update for home-server key id (only if agent path needed), LICENSE file decision, icon/logo asset for README header, verify `codex marketplace add` CLI syntax on next real Codex use.
- **Still open: `ames-lytho` enablement decision** (from afternoon entry). Published in marketplace but not enabled.
- **NEW: `~/.claude/settings.json` has a dangling `"ames-claude-only@ames-claude": true` key** pointing at a plugin that no longer exists. Either remove it (retiring that row) or replace with `"build-ios-apps-codex@ames-claude": true` and `"build-macos-apps-codex@ames-claude": true` to enable the two new plugins. Out of scope for this session; a future `wrap-up` config-drift pass should reconcile.
- **NEW: Test Claude Code's skill auto-discovery on the new layout.** The refactor's premise was that shallow auto-discovery wasn't finding the nested sub-skills. First real use of, say, `build-ios-apps-codex:swiftui-performance-audit` will confirm the sub-skills are now invocable by their kebab-case names. If not, the layout assumption was wrong and needs revisiting.
- **NEW: Consider a shared helper for `update.sh`**. Agent 1 flagged the two scripts as near-duplicates (~50 lines). Kept duplicated for now because each plugin is self-contained and extracting a `scripts/sync-from-codex-cache.sh` helper would break that property for a ROI of 2 plugins. Revisit if a third Codex-derived plugin ever appears.

**Open questions**:
- **Resolved from afternoon entry**: "When `ames-claude-only`'s upstream OpenAI skills change, what's the right cadence for reconversion?" → Still an open question, but now about `build-ios-apps-codex` and `build-macos-apps-codex` individually. Still no automation; per-plugin `update.sh` at `./plugins/<name>/update.sh` is the manual entrypoint. A `sync-upstream-codex-skills` wrapper that runs both scripts could be useful but adds little over running them individually.
- **Resolved from afternoon entry**: "Should the empty `ames-codex-only` namespace be reinstated later?" → Still hypothetical; no Claude-only-compatible Codex skill has appeared. Leave deleted.
- **NEW**: Is there value in capturing a `memory` entry about the "shallow auto-discovery" assumption? The refactor's correctness depends on it being true. Evidence: the afternoon session's notes flagged "may or may not traverse" and today's review agents concurred. If auto-discovery turns out to traverse arbitrary depth, this whole refactor was unnecessary.

---

## 2026-04-17 (afternoon) — ames-claude consolidation, experimental Codex dual-host, comprehensive config record

**What changed**: Consolidated Oliver's plugin marketplace back to a single repo (`ames-claude`), deleted the `ames-codex` and `ames-marketplace` staging repos. Registered `twostraws/SwiftUI-Agent-Skill` marketplace directly in `~/.claude/settings.json` and installed `swiftui-pro` from upstream (no longer vendored). Created a new `ames-claude-only` plugin for two skills converted from OpenAI's Codex plugins (`build-ios-apps-codex`, `build-macos-apps-codex`); these cannot round-trip to Codex. Shrunk `ames-community-skills` to just `humanizer` (blader), removing the SwiftUI Pro wrapper. Added experimental Codex dual-host support additively: `.agents/plugins/marketplace.json` at repo root plus `.codex-plugin/plugin.json` in 5 of 6 plugins (`ames-claude-only` excluded by design). Zero existing Claude manifests touched. Rewrote `README.md` to `/readme-style` conventions with centered header, Buy Me a Coffee badge, and a comprehensive "My Claude Code configuration" section documenting every setting in `~/.claude/settings.json`: all 15 installed marketplaces with upstream repo links, all 44 enabled plugins grouped by source, env vars (OP excluded), the permissions allowlist, both PostToolUse hooks, status line, and all UI/agent-behavior overrides. Bumped `ames-standalone-skills` 3.2.0 → 3.3.0 across Claude manifest, Codex manifest, and marketplace entry. Bumped `wrap-up` skill 4.2.0 → 4.3.0 with a new config-drift check that detects changes to `~/.claude/settings.json` or plugin enablement and auto-updates the README's config section at session end. Fixed cosmetic drift: updated stale "27 skills" to "28" in two places, added `.remember/` to `.gitignore`. Coordinated the 3.3.0 release with a parallel agent that landed the Path B 1password-vault skill addition (commit `4151094`) on top of my version bump. Also updated `CLAUDE.md` to reflect the new dual-host structure and 6-plugin catalog.

**Decisions made**:
- **Keep `ames-claude` as the canonical single repo** rather than create a new combined marketplace or keep the three-repo pipeline (`ames-claude` → `ames-codex` → `ames-marketplace`). The remote URL was already in use by existing installs; preserving it avoided any client-side churn. The three-repo pipeline was defensive architecture from when Codex packaging was uncertain; the March 2026 official Codex marketplace launch made it overkill.
- **Additive-only Codex support.** Every new file lives in a new namespace (`.agents/` or `.codex-plugin/`). No existing Claude Code manifest was modified. This means existing Claude installs see byte-for-byte identical state; the Codex layer is invisible to them.
- **Exclude `ames-claude-only` from the Codex manifest.** A plugin whose skills were converted from Codex plugins can't honestly claim to be installable in Codex. Omitting preserves the invariant that every plugin in the Codex marketplace actually works there.
- **Unvendor `swiftui-pro`**, keep `humanizer` vendored. `twostraws/SwiftUI-Agent-Skill` publishes a proper Claude-format marketplace, so upstream install gives auto-updates. `blader/humanizer` publishes only a bare `SKILL.md` with no marketplace, so wrapping is still the only installation path for plugin users. Every other bundled community skill is a similar decision: prefer upstream marketplace if it exists, wrap only when necessary.
- **README as rebuilding reference, maintained by wrap-up.** Rather than documenting config in a separate `docs/` file or leaving it implicit, the README now carries a full snapshot of `~/.claude/settings.json` with per-setting explanations. The `wrap-up` skill's config-drift check is what keeps this trustworthy: it runs at end of session and updates the README tables if anything changed.
- **Two-agent coordination via self-contained prompts.** When a parallel agent had the Path B 1password-vault edit in a different working tree, I gave the user a self-contained prompt (explicit `git checkout --`, `git pull --rebase`, exact file paths, draft commit message) rather than trying to merge working trees. The other agent landed its commit cleanly on top with no conflict. This is the right pattern for two-agent hand-offs: each agent commits its scoped work to main, no merge coordination required.
- **Version parity across three manifests is manual but enforced.** Each plugin version now lives in `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` (if present), and the root marketplace entry. The new wrap-up config-drift check catches mismatches.

**Left off at**:
- Still open from prior entries: `publish` script end-to-end, ImageRelay 1P fallback verification, UniFi 1P item, `bcbs-meeting-notes` real-world run, postpublish hooks in meta/sprout/imagerelay/unifi still call `bump-and-sync` for removed plugin entry, disable `ames-original-connectors` / enable `ames-ynab` in plugin UI.
- Still open from earlier today: `~/.config/1Password/ssh/agent.toml` update for the new home-server key id (only if agent path is needed).
- NEW: `ames-lytho` is published in the marketplace but not currently enabled in `~/.claude/settings.json` `enabledPlugins`. Decide whether to enable (and test with `LYTHO_*` env vars) or remove from the marketplace.
- NEW: Consider adding a `LICENSE` file to `ames-claude`. The `/readme-style` skill's badge row expects a license badge, which I omitted because no license file exists. MIT would match the ecosystem convention but requires explicit user approval.
- NEW: Consider an icon/logo asset for the ames-claude README centered header. Currently the header is text-only; a small SVG would strengthen `/readme-style` compliance.
- NEW: Verify `codex marketplace add` actual CLI syntax when Codex is next used in earnest. The docs reference the feature but don't fully document the command surface yet.

**Open questions**:
- When `ames-claude-only`'s upstream OpenAI skills change, what's the right cadence for reconversion? Currently manual; no automation exists. Worth considering a `sync-upstream-codex-skills` script.
- Should the empty `ames-codex-only` namespace be reinstated later if Codex ever ships a skill that can't port to Claude Code? Currently deleted for tidiness.

---

Worklog

## 2026-04-17 — home-server SSH key vaulted; `1password-vault` skill gains Path B

**What changed**: Closed out the open item from yesterday's entry about vaulting the home-server's outbound SSH key. Generated a fresh ED25519 in 1Password (`SSH Key - home-server (ED25519)`, id `5wqjaqb6zgrtqt4xgqscrqaopq`, fingerprint `SHA256:Q14gG5v2Ax0+5h5FaeX3XXfZMdS12skx6ihPQCuakUY`) via `op item create --category=ssh --ssh-generate-key=ed25519`, then piped `op read "op://.../private key?ssh-format=openssh"` through `ssh` stdin to atomically replace home-server's `~/.ssh/id_ed25519`. Prior on-disk key preserved as `id_ed25519.bak-2026-04-17`. `authorized_keys` untouched, inbound verified. `1password-vault` skill gained a **Path B (CLI generate + deploy)** workflow alongside the existing Path A (GUI paste-import), plus a decision rule for picking between them. Caveat #1 expanded with two additional confirmed-failing import paths (`"private key[sshkey]="` assignment statement returns "unsupported field type"; JSON template with `ssh_formats.openssh.value` still produces a malformed item).

**Decisions made**:
- **Path B over Path A** for home-server because nothing external references the old public key (not a deploy key anywhere, not in other hosts' `authorized_keys`). When rotating has zero blast radius, the CLI-only path is a strict win over the GUI click.
- **Key stays on disk on home-server, no 1P SSH agent deployment.** Revisited yesterday's "1P desktop install on home-server" open item and chose to leave it. The Mac Mini runs services under the user account, and requiring 1P-app-unlocked-after-every-reboot is operationally fragile for a server. The disk-copy-plus-1P-backup-record pattern is the right shape.
- **Private key never hit local disk**: `op read | ssh home-server 'cat > ...new && mv ...'`. Backup created on home-server only. Clipboard cleared when done.

**Left off at**:
- Still open from prior entries: most of yesterday's list (publish script, ImageRelay verification, UniFi 1P item, bcbs-meeting-notes real-world run, etc.).
- NEW: Add the new item id `5wqjaqb6zgrtqt4xgqscrqaopq` to `~/.config/1Password/ssh/agent.toml` ONLY if home-server ever needs to use the 1P agent path — not today's architecture.

**Open questions**: none.

---

## 2026-04-16 (evening) — Opus 4.7 config overhaul + new `/go` skill

**What changed**: Migrated `~/.claude/settings.json` to the Anthropic-recommended Opus 4.7 defaults: `effortLevel` high → `xhigh`, `permissions.defaultMode` bypassPermissions → `auto`, added `viewMode: focus` and `skipAutoPermissionPrompt: true`, raised `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` 75 → 85. Added a "First-Message Context (Opus 4.7)" subsection to global `~/.claude/CLAUDE.md` under Engineering Workflow → Planning. Created a new `/go` skill in `ames-standalone-skills` (Phase 0 pre-flight → Phase 1 verify e2e → Phase 2 simplify → Phase 3 ship) that codifies Boris Cherny's recommended Opus 4.7 ship pipeline. Bumped plugin 3.1.1 → 3.2.0, ran `./sync`, committed as `ec6f555`, pushed to `oliverames/ames-claude`. Backup of pre-change settings at `~/.claude/settings.json.bak.20260416-200952`.

**Decisions made**:
- **`auto` mode over `bypassPermissions`** as the default. The Opus 4.7 blog + Boris's thread both frame `auto` (classifier-gated) as the safer replacement for `--dangerously-skip-permissions`. Accepted the behavioral shift from "runs anything" to "runs classifier-approved things" because the productivity win of long autonomous tasks outweighs the occasional pause-for-ambiguous-command.
- **`xhigh` over `max`** as the new default effort. Blog positions `xhigh` as best-of-both (autonomy + intelligence without runaway tokens). `max` reserved for truly hard problems, one-shot via CLI.
- **Raise autocompact threshold to 85%** rather than keep 75. Opus 4.7's longer agentic runs mean earlier compaction fires more often and disrupts cooking sessions; willing to trade higher risk of bumping the wall for fewer mid-task context cuts.
- **`/go` skill structure — Phase 0 pre-flight BEFORE verify** so the skill refuses to ship obviously-incomplete work rather than running a pipeline on it. Phase 3 ship logic branches on context (plugin repo ⇒ `./sync` first; bare repo ⇒ commit+push+PR; non-repo ⇒ local-only report).
- **One-off `--no-gpg-sign` for this commit** at user's explicit "Please proceed" authorization. 1Password SSH agent can't supply Touch ID from headless Bash; skipping signing was the only autonomous path once user authorized. Next-similar-situation default is still: ask before skipping.
- **Kept the 1Password `OP_SERVICE_ACCOUNT_TOKEN` plaintext in `settings.json`** at user confirmation ("op service account is required for auth") — it's a bootstrap token that must load before `.env` refs can resolve, so it can't follow the `op://` convention used elsewhere.

**Left off at**:
- Still open (from previous entry): `publish` script untested end-to-end
- Still open (from previous entry): postpublish hooks in meta/sprout/imagerelay/unifi still call bump-and-sync for removed plugin entry
- Still open (from previous entry): disable ames-original-connectors / enable ames-ynab in plugin UI
- Still open (from previous entry): ImageRelay 1Password fallback verification
- NEW: New settings activate at next Claude Code restart — run `/less-permission-prompts` afterward to tune the `auto` classifier's allowlist based on actual transcript history
- NEW: `/go` skill not yet battle-tested — first real use will reveal whether Phase 1's verification-mode branching is the right cut

**Open questions**:
- Is the bundled skill called `/fewer-permission-prompts` (per Boris's tweet) or `/less-permission-prompts` (what resolves in this session's skill list)? Worth confirming next session by typing each and seeing which autocompletes.
- Does `viewMode: "focus"` persist across sessions or reset? Blog implies it's sticky; worth verifying after first restart.

---

## 2026-04-16 — SSH key audit + rotation; 1password-vault skill rewrite; new shared-terminal-tmux skill

**What changed**: In this repo, `ames-standalone-skills` bumped 3.0.0 → 3.1.1. The `1password-vault` skill got three new sections (SSH Key Handling Caveats, SSH Agent Configuration, Headless SSH Pattern as default for automation, Git Commit Signing via op-ssh-sign) plus a reworded SSH-key vaulting section that replaces the broken JSON-template pattern with `--ssh-generate-key` for fresh keys and GUI-only for imports. A new skill `shared-terminal-tmux` was added for bridging Claude's Bash tool with a Terminal.app session via tmux (covers local setup, remote attach via ttyd/SSH/jumphost, coordination protocol). `./sync` regenerated `marketplace.json`. Part of a broader session that also rotated all SSH keys across MBP, home-server, and UDM Pro; archived 6 obsolete 1P items; configured git commit signing via 1P's op-ssh-sign; decommissioned the reminders-web stack on home-server; updated 2 Tech notes in Apple Notes; and wrote/updated 3 memory files (`feedback_headless_ssh_first.md` new, `feedback_ssh_headless_pattern.md` rewritten, `ref_udm_pro.md` new).

**Decisions made**:
- **Option Y (fresh keys for both MBP and home-server)** over Option X (reassign existing K6Po... key). Extra 5 minutes of work for clean per-machine identity and no residual material across two machines.
- **Additive-then-cleanup rotation** over swap-in-place. New keys added alongside old, verify, then remove old. Prevents lockout and is the pattern to use for any credential rotation.
- **Per-item UUID scoping in `agent.toml`** as the always-correct default. Vault-wide scoping is a MaxAuthTries time bomb. Documented in the skill so this doesn't regress.
- **Headless SSH pattern (temp-key-file from `op read`) is the primary path for Claude Code Bash, not a fallback.** Saved to memory and elevated to a top-level section in the skill. The 1P agent's Touch ID requirement makes it unreliable in non-interactive contexts.
- **UDM Pro `authorized_keys` at `/mnt/data/ssh/` with symlink from `/root/.ssh/`** for firmware-update persistence. Lightweight alternative to installing the full `unifios-utilities` on_boot.d framework.
- **home-server keeps its private key on disk for now** (no 1P desktop installed there yet). Apple Note tracks the pending 1P-on-home-server migration.
- `op item create --category=ssh --ssh-generate-key=ed25519` is the only CLI path that produces correctly-schema'd SSH Key items. JSON template creation produces items that are `op read` / `op item get` unreadable.

**Left off at**:
- Still open: `publish` script untested end-to-end
- Still open: postpublish hooks in meta/sprout/imagerelay/unifi still call bump-and-sync for removed plugin entry
- Still open: disable ames-original-connectors / enable ames-ynab in plugin UI
- Still open: ImageRelay 1Password fallback verification
- Still open: UniFi, create 1Password item to bring online
- Still open: verify iMCP/SimGenie/Sosumi appear in `claude mcp list` under `plugin:ames-preferred-mcps:*`
- Still open: `backup-claude` blind spot on `~/.claude.json`
- Still open: bcbs-meeting-notes first real-world run with actual SmartTranscribe output
- Still open: smart-transcribe description optimization loop (skill-creator Phase 4) not yet run
- Still open: Duplicate chrome-devtools MCP registration, disable one
- Still open: Consider running the kebab-case validator as a pre-commit hook
- Still open: Axiom marketplace is registered but no plugins installed yet
- Still open: humanizer has no `update.sh`, manual sync only
- Still open: verify `create-shortcut` still functions (jelly + raw-plist backends both deleted)
- Still open: ames-lytho needs `LYTHO_CLIENT_SECRET` entered in 1Password and real credentials tested end-to-end
- Still open: npm versions 1.0.0 and 1.0.1 of lytho-mcp-server have broken bin entries, consider deprecating with `npm deprecate`
- **NEW**: Task #47, UDM Pro 1P item `lumhg5afbvusqgdcx33jfdaf5e` GUI schema-fix (CLI-unreadable due to custom-section fields). Delete via GUI, recreate via New Item → SSH Key with pasted material.
- **NEW**: 1P desktop install on home-server, then migrate its on-disk private key into a 1P-agent-served item. Apple Note "Home Server — Pending 1Password Setup Steps" (p8803) has the full checklist.
- **NEW**: Clean up backup files when convenient. `~/.config/1Password/ssh/agent.toml.{bak,pre-A5,pre-A7c}-2026-04-16`, `~/.gitconfig.pre-signing-2026-04-16`, home-server `~/.ssh/id_ed25519.{bak,retired}-2026-04-16`, memory `feedback_ssh_headless_pattern.md.pre-2026-04-16`, home-server `~/Developer/projects/docker-config/reminders-web.decommissioned-2026-04-16/`. None are urgent; all small; all named clearly.
- **NEW**: Consider installing `unifios-utilities` on_boot.d/ on UDM Pro for durable SSH config persistence across firmware updates. Today's symlink in `/root/.ssh/` will get wiped by the next UniFi firmware update.
- **NEW**: Remove the stale `ts-reminders` Tailscale node from the Tailscale admin console (tailnet listing will show it offline since the container was removed).

**Open questions**:
- Should `create-shortcut` be removed too, now that both its backends (jelly, raw-plist) are gone?
- Should the `~/.gitconfig` signing settings also be added to the credentials repo's dotfiles backup? Not automated today.

---

## 2026-04-13 — Add ames-lytho plugin (Lytho Workflow MCP connector)

**What changed**: Added `ames-lytho` plugin to the marketplace. Plugin connects to `@oliverames/lytho-mcp-server` via `npx -y @oliverames/lytho-mcp-server@latest`. Full plugin structure: `.claude-plugin/plugin.json`, `.mcp.json` with three `${LYTHO_*}` env var templates, `update-sources.json`, `sources/lytho-mcp-server/` snapshot. Part of a broader session that also built `oliverames/lytho-mcp-server` from scratch and published it to npm.

**Decisions made**:
- Three env vars required (`LYTHO_CLIENT_ID`, `LYTHO_CLIENT_SECRET`, `LYTHO_TOKEN_URL`) because Lytho uses OAuth 2.0 client credentials (Keycloak), not a simple API key. This differs from ames-ynab which needs only `YNAB_API_TOKEN`.
- Sources snapshot is a manual copy (no `update.sh`) -- consistent with ames-ynab pattern.

**Left off at**:
- Still open: `publish` script untested end-to-end
- Still open: postpublish hooks in meta/sprout/imagerelay/unifi still call bump-and-sync for removed plugin entry
- Still open: disable ames-original-connectors / enable ames-ynab in plugin UI
- Still open: ImageRelay 1Password fallback verification
- Still open: UniFi -- create 1Password item to bring online
- Still open: verify iMCP/SimGenie/Sosumi appear in `claude mcp list` under `plugin:ames-preferred-mcps:*`
- Still open: `backup-claude` blind spot on `~/.claude.json`
- Still open: bcbs-meeting-notes first real-world run with actual SmartTranscribe output
- Still open: smart-transcribe description optimization loop (skill-creator Phase 4) not yet run
- Still open: Duplicate chrome-devtools MCP registration -- disable one
- Still open: Consider running the kebab-case validator as a pre-commit hook
- Still open: Axiom marketplace is registered but no plugins installed yet
- Still open: humanizer has no `update.sh` -- manual sync only
- Still open: verify `create-shortcut` still functions (jelly + raw-plist backends both deleted)
- **NEW**: ames-lytho needs `LYTHO_CLIENT_SECRET` entered in 1Password and real credentials tested end-to-end
- **NEW**: npm versions 1.0.0 and 1.0.1 of lytho-mcp-server have broken bin entries -- consider deprecating with `npm deprecate`

**Open questions**:
- Should `create-shortcut` be removed too, now that both its backends (jelly, raw-plist) are gone?

---

## 2026-04-13 — Plugin split: originals vs community skills, skill cleanup

**What changed**: Split `ames-standalone-skills` into two plugins: `ames-standalone-skills` (26 original skills, v3.0.0) and `ames-community-skills` (4 third-party skills, v1.0.0). Moved humanizer (blader/humanizer by Siqi Chen), swiftui-pro (twostraws), build-ios-apps-codex and build-macos-apps-codex (OpenAI Codex) to the new community plugin. Deleted 6 skills total: jelly (unused), ai-pattern-remover (stale duplicate of humanizer v2.1.1), raw-plist (unused Shortcuts plist generator), xcodegen-project (unused Bitrig XcodeGen reference). Removed the redundant `codex` plugin (v1.0.1, 17 sub-skills) since its content was duplicated by the two codex skills in ames-standalone-skills (now community). Updated CLAUDE.md (structure section, plugin table, skill conventions). Ran `./sync`. Updated Apple Notes "My Tech Stack" to reflect new plugin lineup.

**Decisions made**:
- **Major version bump to 3.0.0** for ames-standalone-skills because skills were removed (breaking change for anyone depending on them).
- **Named the new plugin `ames-community-skills`** rather than `ames-third-party-skills` to match the established naming pattern and because "community" better reflects that these are curated picks from the ecosystem.
- **Kept humanizer in community** despite heavy local customization (v2.5.1 rewrite on Apr 10). Origin is blader/humanizer; the skill arrived pre-versioned at v2.1.1 in the initial commit.
- **ai-pattern-remover was NOT an original** despite initial assumption. It was a frozen copy of humanizer v2.1.1 with the name field changed. Fully redundant.
- **Deleted raw-plist and xcodegen-project** after user review. raw-plist was the Shortcuts plist backend (companion to create-shortcut) but unused. xcodegen-project referenced "Bitrig" JSON format that the user didn't recognize.

**Left off at**:
- Still open: `publish` script untested end-to-end
- Still open: postpublish hooks in meta/sprout/imagerelay/unifi still call bump-and-sync for removed plugin entry
- Still open: disable ames-original-connectors / enable ames-ynab in plugin UI
- Still open: ImageRelay 1Password fallback verification
- Still open: UniFi -- create 1Password item to bring online
- Still open: verify iMCP/SimGenie/Sosumi appear in `claude mcp list` under `plugin:ames-preferred-mcps:*`
- Still open: `backup-claude` blind spot on `~/.claude.json`
- Still open: bcbs-meeting-notes first real-world run with actual SmartTranscribe output
- Still open: smart-transcribe description optimization loop (skill-creator Phase 4) not yet run
- Still open: Duplicate chrome-devtools MCP registration -- disable one
- Still open: Consider running the kebab-case validator as a pre-commit hook
- Still open: Axiom marketplace is registered but no plugins installed yet
- RESOLVED: Redundant `codex` plugin removed (was listed as NEW item last session)
- **NEW**: humanizer has no `update.sh` -- manual sync only. Consider adding one that pulls from blader/humanizer.
- **NEW**: `create-shortcut` skill lost its `raw-plist` backend. It still works via Jelly... wait, Jelly was also deleted. Verify `create-shortcut` still functions or update its routing logic.

**Open questions**:
- Should `create-shortcut` be removed too, now that both its backends (jelly, raw-plist) are gone?

---

## 2026-04-12 — Skill consolidation: swiftui-pro upstream sync, codex skills, renames

**What changed**: Updated `swiftui-pro` skill to upstream v1.0 from `twostraws/SwiftUI-Agent-Skill` (Paul Hudson), replacing the local v1.1 customizations (`coding-rules.md`, extended description) with the canonical source. Added `update.sh` scripts to three skills for ongoing sync. Created two new standalone skills from OpenAI's curated Codex plugins: `build-ios-apps-codex` (6 iOS workflows: App Intents, Liquid Glass, performance audit, UI patterns, view refactor, debugger) and `build-macos-apps-codex` (11 macOS workflows + 3 commands: build/run/debug, AppKit interop, signing, notarization, SwiftPM, telemetry, test triage, window management). Renamed three skills: `shokz-rip` -> `apple-music-rip` (hardware-agnostic), `cmux` -> `cmux-workflows` (descriptive), `humanizer-ames` -> `ai-pattern-remover` (accurate). Cleaned up `.a5c`/`.remember` dev artifacts from `swiftui-pro/` and `smart-transcribe/`. Updated `filesystem-map.md`, CLAUDE.md (30->32 skills), and Apple Notes "My Claude Code Setup" tech note. Ran two rounds of 5-agent Opus review; fixed Shokz body content and stale skill count caught by reviewers. Bumped `ames-standalone-skills` 2.8.2 -> 2.9.0.

**Decisions made**:
- **Replaced local swiftui-pro v1.1 with upstream v1.0** rather than merging. The local `coding-rules.md` addition was custom but upstream is the authoritative source. The `update.sh` script makes re-syncing trivial going forward.
- **Created codex skills as router SKILL.md files** with sub-skills in nested `skills/` directories rather than 17 separate top-level skills. This keeps the skill list clean (2 entries vs 17) while preserving all the Codex content and references.
- **Codex update scripts sync from the local Codex cache** (`~/.codex/plugins/cache/openai-curated/`) rather than cloning from GitHub. This means the user runs `codex plugins update` in Codex first, then runs `./update.sh` to sync to Claude format. Clean separation of concerns.
- **Kept `cmux` in the new name** (`cmux-workflows`) because cmux is the app name; dropping it would obscure what the skill is for.
- **Named `ai-pattern-remover`** (not `writing-naturalizer`) because the skill is generic Wikipedia-based AI pattern detection, not personalized to Oliver's voice. The separate `humanizer` skill (v2.5.1, from another repo) is the more advanced version with voice calibration.

**Left off at**:
- Still open (carried): `publish` script untested end-to-end
- Still open (carried): postpublish hooks in meta/sprout/imagerelay/unifi still call bump-and-sync for removed plugin entry
- Still open (carried): disable ames-original-connectors / enable ames-ynab in plugin UI
- Still open (carried): ImageRelay 1Password fallback verification
- Still open (carried): UniFi -- create 1Password item to bring online
- Still open (carried): verify iMCP/SimGenie/Sosumi appear in `claude mcp list` under `plugin:ames-preferred-mcps:*`
- Still open (carried): `backup-claude` blind spot on `~/.claude.json`
- Still open (carried): bcbs-meeting-notes first real-world run with actual SmartTranscribe output
- Still open (carried): smart-transcribe description optimization loop (skill-creator Phase 4) not yet run
- Still open (carried): Duplicate chrome-devtools MCP registration -- disable one
- Still open (carried): Consider running the kebab-case validator as a pre-commit hook
- **NEW**: Axiom marketplace is registered but no plugins installed yet. Evaluate which Axiom plugins to enable.
- **NEW**: The `codex` plugin (v1.0.1, all 17 skills merged) is redundant now that `build-ios-apps-codex` and `build-macos-apps-codex` exist as standalone skills. Consider removing the `codex` plugin or keeping it for users who want the merged version.
- **NEW**: Paul Hudson's `swiftui-pro` is at v1.0 upstream. Monitor for v1.1+ releases; `update.sh` handles sync.

**Open questions**:
- Are inline credential tokens in settings.json worth migrating to op:// references? (Carried -- no progress)
- MLX path (mlx_audio 0.4.2 quantized conv bug): worth filing upstream? (Carried -- no progress)
- Parakeet subsampling bug: worth filing against huggingface/transformers? (Carried -- no progress)
- What other Cowork validator rules are undocumented? (Carried -- no progress)
- Should `ai-pattern-remover` be consolidated into `humanizer` since they overlap significantly? The generic one may be redundant now that `humanizer` has voice calibration.

---

## 2026-04-11 — Cowork marketplace fix: SKILL.md kebab-case + git history flatten

**What changed**: Debugged and fixed the "Failed to update marketplace" / "Marketplace sync failed" errors that had been preventing `ames-standalone-skills` from loading in Cowork. Root cause was 15 of 30 SKILL.md frontmatters having `name: "1Password Vault"` style display names instead of `name: 1password-vault` kebab-case matching directory — Cowork's marketplace validator rejects the entire plugin with a generic error in this case. Also cleaned up a lot of cruft along the way: removed orphaned `smart-transcribe-workspace/` directory (had no SKILL.md, was a stray eval output workspace), removed tracked `evals/workspace/` run outputs and `.a5c/cache/` AI cache files from smart-transcribe, removed 2 empty iCloud conflict files (`.!*.md`). Flattened git history via orphan branch + force push: GitHub pack went from 85.60 MiB → 1.47 MiB (58× reduction) by purging blobs from renamed/deleted plugins (`ames-preferred-connectors`, `plugins/smart-transcribe` old path, `ames-desktop-extensions`). Bumped `ames-standalone-skills` 2.7.0 → 2.8.2 across the fix commits. Updated CLAUDE.md with the kebab-case requirement and other Cowork validator gotchas so this doesn't recur. Saved two memories: `feedback_validate_schemas_first.md` (validate field values against docs BEFORE chasing theories) and `ref_claude_skill_md_schema.md` (the actual Cowork validator rules). Note: commit `92d9682` adding docling to ames-preferred-mcps came from a parallel Opus session, not this one.

**Decisions made**:
- **Kept toolkit-v63-tools.json and toolkit-v63-types.json (9.5MB) in the distributed plugin** despite their size, per the design intent documented in `TOOLKIT_SNAPSHOT.md` — the raw-plist skill bundles a precomputed ToolKit metadata snapshot so users don't need to extract it from their own SQLite. Confirmed size wasn't the issue (Cowork failed even without them).
- **Flattened git history via orphan branch rather than `git filter-repo`** — simpler, more destructive, but appropriate for a personal marketplace where commit history isn't load-bearing (WORKLOG.md serves as the narrative history). Trade-off: lost `git log` / `git blame` on all files.
- **Kept safety tag `pre-orphan-backup` locally but deleted it from GitHub**. Local reflog + local tag give 90-day recovery window; remote tag was keeping old unreferenced blobs alive on GitHub, defeating the point of the flatten.
- **Fixed the `name` fields rather than removing them** — both approaches work (directory name is canonical), but kebab-case matching is what the docs example shows and what 15 of our already-correct skills use.
- **Removed `strict: true` + explicit `skills` array from sync script output** even though it turned out not to be the validator trigger — it's still redundant with auto-discovery and was generating noise in marketplace.json.
- Process lesson worth internalizing: parse field values against the documented schema with a real parser BEFORE proposing theories about size, auth, network, or structural issues. Spent hours on the wrong theories because "frontmatter starts with `---`" was treated as validation. It's a presence check.

**Left off at**:
- ✅ **Resolved**: `ames-standalone-skills` now loads cleanly in Cowork; all 3 plugins visible with no error banner
- Still open (carried): `publish` script untested end-to-end
- Still open (carried): postpublish hooks in meta/sprout/imagerelay/unifi still call bump-and-sync for removed plugin entry
- Still open (carried): disable ames-original-connectors / enable ames-ynab in plugin UI
- Still open (carried): ImageRelay 1Password fallback verification
- Still open (carried): UniFi — create 1Password item to bring online
- Still open (carried): verify iMCP/SimGenie/Sosumi appear in `claude mcp list` under `plugin:ames-preferred-mcps:*`
- Still open (carried): `backup-claude` blind spot on `~/.claude.json`
- Still open (carried): bcbs-meeting-notes first real-world run with actual SmartTranscribe output
- Still open (carried): smart-transcribe description optimization loop (skill-creator Phase 4) not yet run
- Still open (carried): Duplicate chrome-devtools MCP registration — disable one
- **NEW**: Repo is private and Cowork does work with it now, but if Cowork ever breaks private-repo support again, consider making public after redacting `oliverames@gmail.com` in 2 plugin.json files + Tailscale IP `100.79.211.138` in this WORKLOG
- **NEW**: Consider running the kebab-case validator as a pre-commit hook on `plugins/ames-standalone-skills/skills/*/SKILL.md` to catch regressions on new skills

**Open questions**:
- Are inline credential tokens in settings.json (GITHUB, YNAB, Telegram, Google OAuth) worth migrating to op:// references? (Carried — no progress)
- MLX path (mlx_audio 0.4.2 quantized conv bug): worth filing upstream? (Carried — no progress)
- Parakeet subsampling bug: worth filing against huggingface/transformers? (Carried — no progress)
- What other Cowork validator rules are undocumented? The kebab-case requirement wasn't explicitly spelled out in the docs — there may be others lurking.

---

## 2026-04-10 — config hardening: new CLAUDE.md rules, hooks fixed, draft-comms skill added

**What changed**: Added 5 new global CLAUDE.md rule sections (Safety & Conventions, Problem-Solving Principles, Writing & Communications, Workflow Conventions, Credentials & Secrets). Added PreToolUse/PostToolUse hooks to settings.json with correct Claude Code event names and stdin-JSON input format. Created draft-comms skill under ames-standalone-skills v2.7.0. Ran /doctor: cleared 3 stale babysitter session files, confirmed stop hook healthy (72 invocations, all clean). MCP audit: all 24 servers reachable, one duplicate chrome-devtools registration noted (not fixed).

**Decisions made**:
- Hooks must use Claude Code's actual event names (PreToolUse/PostToolUse/Stop/SessionStart/UserPromptSubmit) — preEdit/postCommit were stored but would never fire
- Hook commands receive tool input as JSON via stdin, not env vars — must parse with python3 or jq
- All new skills go into ames-standalone-skills plugin (plugins/ames-standalone-skills/skills/), never userspace ~/.claude/skills/
- postCommit has no native Claude Code analog; approximated with PostToolUse/Bash + git-commit string detection
- draft-comms skill invokes humanizer-ames for tone, saves to ~/Documents/drafts/, copies approved drafts to clipboard via pbcopy

**Left off at**:
- Still open (carried): `publish` script untested end-to-end
- Still open (carried): postpublish hooks in meta/sprout/imagerelay/unifi still call bump-and-sync for removed plugin entry
- Still open (carried): disable ames-original-connectors / enable ames-ynab in plugin UI
- Still open (carried): ImageRelay 1Password fallback verification
- Still open (carried): UniFi — create 1Password item to bring online
- Still open (carried): verify iMCP/SimGenie/Sosumi appear in `claude mcp list` under `plugin:ames-preferred-mcps:*`
- Still open (carried): `backup-claude` blind spot on `~/.claude.json`
- Still open (carried): bcbs-meeting-notes first real-world run with actual SmartTranscribe output
- Still open (carried): smart-transcribe description optimization loop (skill-creator Phase 4) not yet run
- Duplicate chrome-devtools MCP registration (chrome-devtools-plugins + claude-plugins-official both enabled) — disable one

**Open questions**:
- Are inline credential tokens in settings.json (GITHUB, YNAB, Telegram, Google OAuth) worth migrating to op:// references? Audit flagged as hygiene issue.
- MLX path (mlx_audio 0.4.2 quantized conv bug): worth filing upstream or waiting for a new mlx_audio release?
- Parakeet subsampling bug: worth filing against huggingface/transformers?

---

## 2026-04-10 — smart-transcribe: fix all three default engines, Cohere fully operational

**What changed**: Fixed Cohere Transcribe (local) which was broken in 7 distinct ways. Engine now runs correctly end-to-end on audio of any length including files over 6.7 minutes. Also ran skill-creator eval loop on smart-transcribe skill (4 evals, iteration-1 workspace committed). Humanizer SKILL.md rewritten; humanizer-ames and oliver-tone committed under version control.

**Decisions made**:
- Used `CohereAsrForConditionalGeneration` not `AutoModelForSpeechSeq2Seq` — wrong class was the root cause of garbage output (hallucinated multilingual text)
- Runtime monkey-patch for the Parakeet subsampling shape bug (`permute(0,3,1,2)`) applied both in the venv source and at subprocess startup, so the fix survives a `pip install --upgrade transformers`
- 300s chunk size for long audio — gives ~3750 encoder frames per chunk vs the 5000 hard limit, with comfortable margin
- `repetition_penalty=1.2` chosen as a conservative value that breaks loops without forcing unwanted vocabulary diversity; standard safe range for conformer models
- MLX path silently fails (mlx_audio 0.4.2 bug, conv channel mismatch on quantized models); PyTorch/MPS fallback always activates — acceptable since MPS is fast enough

**Left off at**:
- Still open (carried): `publish` script untested end-to-end
- Still open (carried): postpublish hooks in meta/sprout/imagerelay/unifi still call bump-and-sync for removed plugin entry
- Still open (carried): disable ames-original-connectors / enable ames-ynab in plugin UI
- Still open (carried): ImageRelay 1Password fallback verification
- Still open (carried): UniFi — create 1Password item to bring online
- Still open (carried): verify iMCP/SimGenie/Sosumi appear in `claude mcp list` under `plugin:ames-preferred-mcps:*`
- Still open (carried): `backup-claude` blind spot on `~/.claude.json`
- Still open (carried): bcbs-meeting-notes first real-world run with actual SmartTranscribe output
- smart-transcribe description optimization loop (skill-creator Phase 4) not yet run — generate 20 trigger queries, optimize SKILL.md frontmatter description

**Open questions**:
- MLX path (mlx_audio 0.4.2 quantized conv bug): worth filing upstream or waiting for a new mlx_audio release?
- Parakeet subsampling bug: worth filing against huggingface/transformers? Confirmed unreported per online research.

---

## 2026-04-10 — oliver-tone: em-dash hard ban, fragment rule, clipboard delivery

**What changed**: Strengthened three rules in `oliver-tone/SKILL.md` based on real-world feedback while rewriting BCBS emails. Em-dash rule upgraded from a parenthetical note to a hard ban with explicit coverage of `--` double-dashes. New sentence fragment rule added with concrete examples of the pattern ("On the financial side:" / "Worth looking at."). New Delivery section added at the end with `pbcopy` pattern and "don't ask, just do it" instruction so clipboard copy is automatic going forward. Committed and synced to marketplace (ames-standalone-skills now at 30 skills).

**Decisions made**:
- Fragment rule placed adjacent to the em-dash rule because they stem from the same instinct — clipped, punchy constructions that read as incomplete
- Delivery section uses imperative phrasing ("Do this as the last step... Don't ask — just do it") to prevent clipboard copy from becoming a question each session
- oliver-tone was previously untracked in git; this commit brings it under version control for the first time

**Left off at**:
- Still open (carried): `publish` script untested end-to-end
- Still open (carried): postpublish hooks in meta/sprout/imagerelay/unifi still call bump-and-sync for removed plugin entry
- Still open (carried): disable ames-original-connectors / enable ames-ynab in plugin UI
- Still open (carried): ImageRelay 1Password fallback verification
- Still open (carried): UniFi — create 1Password item to bring online
- Still open (carried): verify iMCP/SimGenie/Sosumi appear in `claude mcp list` under `plugin:ames-preferred-mcps:*`
- Still open (carried): `backup-claude` blind spot on `~/.claude.json`
- Still open (carried): bcbs-meeting-notes first real-world run with actual SmartTranscribe output

**Open questions**: None new.

---

## 2026-04-09 — bcbs-meeting-notes skill v1.2.0; BCBS archive reorganization

**What changed**: Created new `bcbs-meeting-notes` skill in `ames-standalone-skills`. Skill processes SmartTranscribe `.md` transcripts into structured meeting notes with three-pass generation (theme extraction → per-theme elaboration → compile), intelligent routing to Ashley & Oliver Meetings / Projects / Calls, standard file renaming (`YYYY-MM-DD – Name – Transcript.md` / `– Notes.md`), and Jira issue creation for Oliver's action items. Ran full skill-creator eval loop across 3 test cases (Ashley 1:1, project routing, borderline routing). Shipped v1.0 → v1.1.0 → v1.2.0 based on eval findings. Also reorganized entire BCBS archive: zero-padded folder dates, replaced all em dashes and spaced hyphens with en dashes, renamed files to match file-organization conventions throughout Ashley & Oliver Meetings and Projects.

**Decisions made**:
- Ashley & Oliver routing uses a tiebreaker: route to Ashley & Oliver Meetings ONLY if no strong project identity AND they are the sole/primary participants — any project meeting Ashley attends routes to the project
- "Routing context stays out of the notes file" added explicitly after eval found subagent embedding routing metadata in the generated notes
- Notes folder eliminated: notes live alongside their paired transcript (same destination folder), distinguished by `– Notes.md` vs `– Transcript.md` suffix
- Calls/ is "last resort only" — policy documented aggressively in skill to prevent over-routing general calls
- Jira graceful fallback: if MCP auth fails, skip and report — don't abort the whole run
- `Sprout/` project folder created separately (user moved Sprout Social file there intentionally, not Digital Infrastructure)

**Left off at**:
- bcbs-meeting-notes has not yet been deployed via `publish` — it ships as part of the ames-standalone-skills plugin on next publish cycle
- Skill has been tested with synthetic transcripts only; first real-world run will validate real SmartTranscribe output parsing
- Still open (carried): `publish` script untested end-to-end
- Still open (carried): postpublish hooks in meta/sprout/imagerelay/unifi still call bump-and-sync for removed plugin entry
- Still open (carried): disable ames-original-connectors / enable ames-ynab in plugin UI
- Still open (carried): ImageRelay 1Password fallback verification
- Still open (carried): UniFi — create 1Password item to bring online
- Still open (carried): verify iMCP/SimGenie/Sosumi appear in `claude mcp list` under `plugin:ames-preferred-mcps:*`
- Still open (carried): `backup-claude` blind spot on `~/.claude.json`

**Open questions**: Should the skill's three-pass generation be externalized into a shared utility for other note-taking skills, or is this scope creep?

---

## 2026-04-09 — smart-transcribe: 3-engine pipeline, Claude Code headless merge

**What changed**: Major overhaul of `smart-transcribe.py` (v2.5.2 → v2.6.0). Replaced 2-engine AssemblyAI+Mistral default with 3-engine AssemblyAI SLAM-1 + ElevenLabs Scribe v2 + Cohere Transcribe (local). Replaced Gemini/OpenAI/Anthropic-SDK merge paths with a single Claude Code headless call (`claude -p --model opus --effort medium`). Merge prompt now injects per-engine capability profiles (AA-WER, HF-WER, strengths). 1Password-native key resolution replaces `keys.env`. Output folder now co-located with source audio. Also shipped: per-context config, transparency reports, fix-transcript mode, --review mode. Code cleanup: `_flatten_entities()`, `_sanitize_filename()`, `_REPORT_ICONS` constant, `_ASSEMBLYAI_META.clear()`. Verified end-to-end with `Kemp Ave.qta`.

**Decisions made**:
- `claude -p --model opus --effort medium` preferred over direct Anthropic SDK: inherits Claude Code auth, simpler than managing API keys for merge, `--effort medium` enables extended thinking via CLI flag
- Cohere model (~4.5GB) cached at `~/.cache/huggingface/hub/` — not re-downloaded between runs, but subprocess restart means warmup cost per transcription (~30s fan spike)
- Output path changed from `~/Desktop/Transcriptions/` to audio file's parent directory — co-location makes more sense for workflow
- Cohere hallucinated on near-silence (multilingual garbage) — Opus correctly identified and discarded it; this is expected local-model behavior on no-signal audio
- `--model` argparse simplified to `claude` only; Gemini and OpenAI merge options removed

**Left off at**:
- Test with a real recording that has actual speech content — Kemp Ave.qta is nearly silent; all testing validated pipeline but not merge quality on real audio
- Consider a warm-process architecture for Cohere to avoid the 30s model-load penalty per run (e.g., a local HTTP server that stays warm between calls)
- Still open (carried): `publish` script untested end-to-end
- Still open (carried): postpublish hooks in meta/sprout/imagerelay/unifi still call bump-and-sync for removed plugin entry
- Still open (carried): disable ames-original-connectors / enable ames-ynab in plugin UI
- Still open (carried): ImageRelay 1Password fallback verification
- Still open (carried): UniFi — create 1Password item to bring online
- Still open (carried): verify iMCP/SimGenie/Sosumi appear in `claude mcp list` under `plugin:ames-preferred-mcps:*`
- Still open (carried): `backup-claude` blind spot on `~/.claude.json`

**Open questions**: Should Cohere run as a persistent warm server to eliminate the 30s load penalty? Tradeoff: complexity vs. speed for frequent transcription sessions.

---

## 2026-04-09 — Style sync scripts; major Developer/Scripts overhaul

**What changed**: Applied consistent terminal styling to the three ames-claude scripts (`sync`, `bump-and-sync`, `plugins/ames-preferred-mcps/sync-sources`) and added `style.sh` (shared library). Python scripts got inline ANSI color helpers matching the same palette. Part of a broader session that also overhauled all 10 scripts in `Developer/Scripts` (not a git repo — iCloud only).

**Decisions made**: `sync` and `sync-sources` are Python so they can't source `style.sh` — used the same inline color helper pattern established in `redact-keys`. `style.sh` added to the ames-claude root so `bump-and-sync` (bash) can source it. Style is cosmetic only; all logic was preserved.

**Left off at**:
- Still open (carried): `publish` script functionally improved this session (fixed `--prefix` flag, made non-fatal in kitchensync) but end-to-end npm publish flow still untested
- Still open (carried): postpublish hooks in meta-mcp-server, sprout-mcp-server, imagerelay-mcp-server, ames-unifi-mcp still call bump-and-sync for removed plugin entry
- Still open (carried): disable ames-original-connectors@ames-claude / enable ames-ynab@ames-claude in plugin UI after next marketplace refresh
- Still open (carried): ImageRelay 1Password fallback verification
- Still open (carried): UniFi — create 1Password item to bring online
- Still open (carried): verify iMCP/SimGenie/Sosumi appear in `claude mcp list` under `plugin:ames-preferred-mcps:*`
- Still open (carried): `backup-claude` does not back up `~/.claude.json` mcpServers block — blind spot persists (backup-claude was heavily refactored this session but this specific gap was not addressed)

**Open questions**: Developer/Scripts has no git repo — changes are iCloud-only with no version history. The right fix is `git init` + push to a private GitHub repo, then add to `commit-push-all`. Worth doing before the next major Scripts session.

---

## 2026-04-09 — Add iMCP, SimGenie, Sosumi to ames-preferred-mcps

**What changed**: Audited MCP setup and added three new servers to `ames-preferred-mcps` (1.0.2 → 1.1.0): iMCP (stdio, `/Applications/iMCP.app/...`), Sim Genie (stdio, `/Applications/Sim Genie.app/...`), and Sosumi (HTTP, `https://sosumi.ai/mcp`). Updated `sync-sources` to document which servers have no CLI update path (SimGenie, Sosumi). Ran `./sync`, committed, pushed. Cleaned up the now-redundant `iMCP` and `SimGenie` entries from `~/.claude.json` (where `claude mcp add --scope user` had written them). Also fixed the `apple-notes-mcp` marketplace `plugin.json` version (stuck at 1.1.1 while npm package was 1.4.1) and filed sweetrb/apple-notes-mcp#10 about it.

**Decisions made**: Added all three to `ames-preferred-mcps` rather than leaving them in `~/.claude.json` — plugin-managed is backed up, `~/.claude.json` is not. Sosumi uses `"type": "http"` + `"url"` in `.mcp.json` (no command/args). SimGenie has no Homebrew cask and no CLI update path — documented in `sync-sources` as "update via the app itself." Version bumped to 1.1.0 (minor) since three new MCP servers were added. The apple-notes fix was purely a metadata correction — actual running code was already 1.4.1 via unversioned `npx`, confirmed in the npx cache.

**Left off at**:
- Still open (carried): `publish` script untested
- Still open (carried): postpublish hooks in meta-mcp-server, sprout-mcp-server, imagerelay-mcp-server, ames-unifi-mcp still call bump-and-sync for removed plugin entry
- Still open (carried): disable ames-original-connectors@ames-claude / enable ames-ynab@ames-claude in plugin UI after next marketplace refresh
- Still open (carried): ImageRelay 1Password fallback verification
- Still open (carried): UniFi — create 1Password item to bring online
- NEW: After next marketplace refresh, verify iMCP/SimGenie/Sosumi appear in `claude mcp list` under `plugin:ames-preferred-mcps:*` (not `~/.claude.json`)
- NEW: `backup-claude` does not back up `~/.claude.json` — any future `claude mcp add --scope user` calls will write there and be invisible to backup. Consider updating `backup-claude` to extract `mcpServers` from `~/.claude.json` as a safety net.

**Open questions**: Should `backup-claude` extract and save the `mcpServers` block from `~/.claude.json`? Currently a blind spot.

---

## 2026-04-07 — Skill description pass + Telegram teardown

**What changed**: Two work streams. (1) Reviewed and improved skill descriptions for 5 undertriggering skills: `testflight-deployment` (added intent-based triggers like "deploy my app", "distribute to beta testers"), `ios-capabilities` (added framing sentence before trigger list), `xcodegen-project` (same framing fix), `macos-app-icons` (added natural user phrasings), `readme-style` (made proactively self-triggering). Ran `./sync` to push updated descriptions to marketplace. (2) Diagnosed and fixed two Telegram daemon bugs — Layer 4 was killing interactive sessions' bun wrappers (breaking /mcp connection), and missing SIGHUP handler caused bot.stop() to not run on tmux kill-session. Applied both fixes and verified healthy. Then disabled Telegram entirely: `launchctl unload`, killed tmux session, removed the `tg` dot from statusline-command.sh.

**Decisions made**: Skill descriptions updated but skill bodies untouched — the descriptions were the only failure mode (undertriggering). Telegram disabled at the LaunchAgent level, not deleted — all config preserved in the telegram-channel backup repo for easy re-enable. Statusline `tg` dot removed since it's useless when the daemon isn't running (it would always show gray `○`). Layer 4 change in daemon scoped to orphan-only (tty=??) rather than a more nuanced check — simplest fix with no false positives; interactive sessions always have a real tty. SIGHUP handler added alongside existing SIGTERM/SIGINT in a single `shutdown()` call — no behavioral change for the normal path.

**Left off at**: 
- Still open (carried): `publish` script untested
- Still open (carried): postpublish hooks in meta-mcp-server, sprout-mcp-server, imagerelay-mcp-server, ames-unifi-mcp still call bump-and-sync for removed plugin entry — clean up in each upstream repo
- Still open (carried): disable ames-original-connectors@ames-claude / enable ames-ynab@ames-claude in plugin UI after next marketplace refresh
- Still open (carried): ImageRelay 1Password fallback verification
- Still open (carried): UniFi — create 1Password item to bring online
- Re-enable Telegram when wanted: `launchctl load ~/Library/LaunchAgents/com.oliverames.claude-telegram.plist` — then restore statusline tg dot

**Open questions**: None new.

---

## 2026-04-07 — Scope ames-original-connectors down to YNAB, rename to ames-ynab (2.0.0)

**What changed**: Trimmed the connectors bundle to only the actively-used YNAB connector and renamed the plugin `ames-original-connectors` → `ames-ynab` (v1.2.13 → 2.0.0, major per the breaking-rename + scope-reduction rule). Deleted `sources/meta`, `sources/sprout-social`, `sources/imagerelay`, `sources/unifi` — originals still live in their own GitHub repos and remain installable via npm, they just aren't bundled here anymore. Used `git mv` to rename the plugin directory so history is preserved. Updated `.claude-plugin/plugin.json` (name, version, description, keywords), `.mcp.json` (ynab-only), `update-sources.json` (ynab-only), and the plugin's `README.md`. Updated `bump-and-sync` to point at the new path and updated its commit-message string. Updated `CLAUDE.md` plugin table. Also fixed pre-existing staleness in the root `README.md` — it still referenced `ames-preferred-connectors`, `ames-preferred-skills`, and `ames-desktop-extensions` (none of which exist in the tree); replaced with the real three-plugin list. Regenerated `marketplace.json` via `./sync`.

**Decisions made**: 2.0.0 not patch — plugin rename and scope reduction are breaking changes per CLAUDE.md versioning rules, even though there's only one consumer. Used `git mv` for the directory rename to preserve file history across the move. Left historical references to `ames-original-connectors` in `memory/ref_macos_python_ssl.md` and `memory/feedback_layered_credential_contracts.md` alone — those are accurate historical debugging context, not forward-looking references, and rewriting them would be revisionism. Did not hand-edit `~/.claude/settings.json` or `~/.claude/plugins/installed_plugins.json` — chose option (B), will disable old plugin and enable new one via the Claude Code plugin UI after marketplace refresh.

**Left off at**: Still open (carried from 2026-04-07 earlier session): `publish` script untested; description optimization loop for undertriggering skills; telegram daemon-gate verification on next session start; ImageRelay + UniFi 1Password-fallback verification. New: postpublish hooks in `meta-mcp-server`, `sprout-mcp-server`, `imagerelay-mcp-server`, and `ames-unifi-mcp` repos still try to call `bump-and-sync` for a plugin entry that no longer exists — they'll fail silently after npm publish succeeds (npm publish itself is unaffected). Clean those up in each upstream repo separately. New: after marketplace next refresh, disable `ames-original-connectors@ames-claude` and enable `ames-ynab@ames-claude` through the plugin UI. New: memory files `project_ames_claude.md` and `feedback_skills_no_mcp_deps.md` and the `MEMORY.md` index were updated to reflect the new plugin name (3 → 3 plugins, connector bundle now single-purpose).

**Open questions**: None new. Carried forward: checklist-vs-memory question for the layered-credential-contract pattern.

---

## 2026-04-07 — Connector + skill cleanup: ynab consolidation, 1Password contract migration, telegram daemon gate

**What changed**: Three connector/plugin bugs traced to one root-cause family (two layers fighting over credential / exclusivity contracts), all fixed. (1) Deleted lingering `ynab-categorization` skill — `ynab-finance` was already added in the 2026-04-04 audit but never deleted, and the version wasn't bumped, so client caches stayed at the pre-consolidation 2.5.0 snapshot and reported "ynab-finance path not found". Bumped `ames-standalone-skills` 2.5.0 → 2.5.1 (patch, not 3.0.0 — see Decisions). (2) Removed `env` blocks from `imagerelay` and `unifi` entries in `ames-original-connectors/.mcp.json` so each server's runtime 1Password fallback can actually run; previously Claude Code's pre-flight env validation refused to spawn the servers because `${IMAGE_RELAY_API_KEY}` etc. were unresolved in `settings.json`. Bumped connectors 1.2.11 → 1.2.12 manually, then `ames-unifi-mcp` postpublish auto-bumped to 1.2.13. (3) Patched `~/.claude/telegram-patches/server.ts` (the daemon-applied patch source) with a `CLAUDE_TELEGRAM_DAEMON === '1'` gate around the polling IIFE — interactive Claude sessions now register the MCP tools but skip `bot.start()`, so the daemon stops killing them and the channel no longer flaps "offline". Restarted the daemon to redeploy. Fixed stale "27 standalone skills" claim in `CLAUDE.md` and `claude-code-headless/data/filesystem-map.md` (now 26).

**Decisions made**: Bumped standalone-skills as patch (2.5.1) rather than the previous worklog's suggested 3.0.0 — the consolidation was already in 2.5.0's HEAD; only the missed delete is being shipped, and Claude Code's marketplace doesn't enforce semver, so a patch is correct. The 3.0.0 question is dropped as no longer load-bearing. For Telegram, chose env-var gate over self-organizing PID-file lock: the daemon already sets `CLAUDE_TELEGRAM_DAEMON=1` in its tmux command, so the gate is a 3-line patch with zero new state; the elegant alternative (auto-failover when daemon dies) was rejected because the LaunchAgent restarts within ≤60s and `replayPendingMessages()` already catches up. For Image Relay specifically: rather than putting a plaintext key in `settings.json`, deleted the env block entirely so the server's existing op-fallback runs — zero plaintext credentials anywhere in Claude Code config.

**Left off at**: Still open: `ames-preferred-mcps` should still be monitored (carried from 2026-04-04). Still open: `publish` script still untested (carried from 2026-04-04). Still open: description optimization loop for the 5-10 most undertriggering skills (carried from 2026-04-04). New: telegram daemon-gate fix only takes effect for **new** Claude Code sessions started after the daemon restart — the current session was launched before the patch landed and has no telegram MCP tools. Verify the channel comes online cleanly on next session start. New: ImageRelay should resolve via 1Password fallback on next connector refresh — verify by attempting a tool call in a new session. New: UniFi will appear "installed but inactive" with the auth-hint error; create the `UniFi Controller` 1Password item (vault: Development; fields: host, api_key OR username + password) when ready to bring it online.

**Open questions**: Dropped: "Should standalone-skills be bumped to 3.0.0?" — patch chosen instead, see Decisions. Dropped: "Is the marketplace poll interval fast enough?" — confirmed acceptable in practice. New: For new connectors that gain self-resolution capability later, should the `.mcp.json` env-block-removal step be encoded as a checklist somewhere, or is the new `feedback_layered_credential_contracts.md` memory enough? Part of a broader session that also touched ames-unifi-mcp.

---

## 2026-04-04 — Skill audit: 45 → 27, cut generic knowledge, consolidate finance and SwiftUI

**What changed**: Full audit of all 45 standalone skills. Deleted 13 that duplicate Claude's built-in knowledge (github-cli, marketing-mode, senior-frontend, prompt-engineering-expert, linkedin-best-practices, math-helper, self-improving-agent, memory-management, wolfram, task-management, web-design-guidelines, coding-agent, research). Core directives for math/wolfram/research moved to `~/.claude/CLAUDE.md` as one-liners. Merged `swiftui-coding-rules` into `swiftui-pro` as `references/coding-rules.md` (preserving iOS 26 Liquid Glass and Foundation Models content). Consolidated 5 YNAB finance skills into single `ynab-finance` router with 5 reference files. Removed all MCP requirement declarations from remaining skills (skills reference tool names, MCP servers installed separately). Fixed stale skill list in `claude-code-headless/data/filesystem-map.md`. Improved descriptions on 5 skills for better triggering. Updated CLAUDE.md skill count.

**Decisions made**: Skills should only encode knowledge Claude can't derive on its own. Generic frameworks (AIDA, React patterns, gh CLI) waste ~3,000 lines of context. MCP dependencies don't belong in skills since MCP servers are installed via plugins or marketplace, not by skills. The YNAB router pattern (one SKILL.md, 5 reference files) is better than 5 separate skills because it reduces skill-list pollution from 5 descriptions to 1. SwiftUI merge direction was coding-rules INTO swiftui-pro (not the reverse) because swiftui-pro has the comprehensive 9-file reference architecture.

**Left off at**: Still open from previous: `ames-preferred-mcps` should be monitored. Still open: `publish` script untested. New: Description optimization loop (`run_loop.py`) was planned for all 27 skills but deferred — consider running on the 5-10 skills most likely to undertrigger. The `ames-standalone-skills` version is still 2.5.0 and should be bumped to 3.0.0 (major: 18 skills removed/restructured).

**Open questions**: Should the version be bumped to 3.0.0 given the breaking changes (removed skills others may reference)? Is the marketplace poll interval fast enough that users will see the 45→27 change promptly?

---

## 2026-04-03 — Simplify infrastructure: 1Password secrets, new plugin, backup system

**What changed**: Major infrastructure simplification. Replaced the rendered-settings/dotfiles/credentials flow with a single `settings.json` + 1Password integration: `OP_SERVICE_ACCOUNT_TOKEN` in settings.json authenticates `op` CLI, all other secrets are `op://` references in `~/.claude/.env` resolved at shell startup via `op inject`. Deleted `settings.local.json` — `settings.json` is now the sole config source. Created `ames-preferred-mcps` plugin (v1.0.2) bundling 10 third-party MCP servers (apple-docs, apple-notifier, drafts, excel, google-workspace, macos-automator, pandoc, peekaboo, shortcuts, XcodeBuildMCP). Restored Telegram daemon from backup (bot token, access.json, daemon config, typing indicator patch). Created 7 CLI scripts: `backup-claude`, `backup-telegram`, `commit-push-all`, `redact-keys`, `install`, `update`, `publish`. Created private `ames-claude-backup` repo for memory/plans/teams. Rewrote `CLAUDE.md` to match current reality. Updated wrap-up skill to v4.0.0. Updated all memory files. Fixed telegram daemon patch path from stale `~/Developer/dotfiles/` to `~/.claude/telegram-patches/`.

**Decisions made**: 1Password service account is the single secret-management layer — eliminates dotfiles/credentials repos entirely. `settings.json` is the sole config file (no settings.local.json indirection). Scripts live in `Developer/Scripts/` (in PATH, not a git repo), not `~/.local/bin/`. Marketplace sync is just `./sync` (Python), not the old `sync-skills`. Telegram patch lives in `~/.claude/telegram-patches/` rather than a dotfiles directory. The `publish` script handles npm connector releases, while `commit-push-all` handles everything else.

**Left off at**: Previous "left off at" items resolved: connector surface is healthy, `unifi` still needs real credentials to go online. New: `ames-preferred-mcps` is installed but should be monitored on next session — verify all 10 MCPs connect after plugin update. The `publish` script is written but untested with real npm publishes — test on next connector version bump. The `install` script is untested on a fresh machine.

**Open questions**: Dropped: "Should the connector/tool surface be reduced?" — no longer relevant after infrastructure simplification, context usage is acceptable. Dropped: "Should `ames-preferred-skills` expand?" — that plugin was removed, skills stay in `ames-standalone-skills`. New: Should the `publish` script suppress individual `postpublish → bump-and-sync` hooks when batch-publishing multiple connectors, to avoid multiple intermediate commits?

---

## 2026-04-02 — Stabilize live connector runtime and close sync drift

**What changed**: Tightened the live Claude runtime path after the earlier portability refactors. The rendered settings flow now merges both `credentials/env.json` and `credentials/tokens.json`, so Bear and the other secret-bearing connectors no longer depend on legacy direct user config. Removed legacy plugin-managed MCP entries from `~/.claude.json` so the direct user layer is back to the intended DXT-only bridges plus `fantastical`. Relaxed `meta` and `sprout-social` boot-time env requirements, switched `apple-rag` back to HTTP, and reran the marketplace/install path until the preferred/original connector set was healthy again. Updated `sync-skills` so tracked Cowork bundles are rebuilt before the `ames-claude` repo is committed and pushed, which stopped normal `sync` runs from leaving this repo dirty. Added the accepted `xcode` / `iMCP` runtime caveat and the two-file secret merge path to project docs.

**Decisions made**: Plugin-managed `.mcp.json` files are the authoritative Claude Code connector source of truth; `~/.claude.json` should hold only intentional direct user bridges, not shadow copies of the curated plugin set. Saved Cowork bundle artifacts are part of the portable repo surface, so they must be refreshed before the marketplace repo is published rather than as a later side effect. `xcode` and `iMCP` appearing offline during health checks are runtime caveats, not packaging failures, so future reviews should treat them that way.

**Left off at**: Still open: `unifi` remains structurally fixed but will stay offline on this machine until real UniFi credentials are put back in scope. Still open: `claude doctor` still warns about the overall MCP tools context size; reducing that warning would require intentionally pruning the installed connector/tool surface rather than fixing a broken config. New: if future connector manifest changes also affect Cowork packaging, start with `sync-skills` before final `sync` so the tracked `.mcpb` bundle artifacts stay aligned from the start.

**Open questions**: Should the connector/tool surface be reduced enough to quiet the large-context `claude doctor` warning, or is that warning an acceptable tradeoff for keeping the full installed toolset? Should `ames-preferred-skills` stay intentionally curated and small, or grow into a broader vendored third-party bundle over time?

---

## 2026-04-02 — Replace final placeholders with portable source content

**What changed**: Filled the last structural portability gaps. `ames-preferred-skills` now vendors a small real bundle of third-party skills from `anthropic-agent-skills/document-skills` instead of staying empty, with `sources.json` and `sync-sources` as the refresh path. Added `sources/` refresh flows to both connector plugins so `ames-original-connectors` snapshots the local mother repos and `ames-preferred-connectors` snapshots upstream third-party repos or writes explicit source notes for built-in / app-backed connectors like `xcode`, `iMCP`, and `apple-rag`. Updated `sync-skills` to run plugin-local `sync-sources` steps before version bump/publish and fixed its temp-clone fallback so it copies the full repo contents rather than only `plugin.json` files. Switched the `unifi` runtime definition to prefer the local development repo binary before falling back to `npx`, avoiding the broken published launcher path.

**Decisions made**: The plugin bundles now trade a little extra size for a clearer filesystem story. `sources/` is treated as part of the portable artifact, not as disposable build output. For `ames-preferred-skills`, a small curated subset was chosen over a giant imported bundle so the plugin is real without becoming noisy.

**Left off at**: The structural fixes are in place, but live `unifi` health still depends on real UniFi credentials being present on the machine. The source refresh scripts are now the intended maintenance path for keeping these portable snapshots current.

**Open questions**: Should `ames-preferred-skills` expand beyond the current document-workflow bundle, or stay intentionally small? Should more original connectors switch to local-repo-first launchers, or should that remain a targeted fix for packages like `unifi` that need it?

## 2026-04-02 — Tighten Claude config flow and runtime-verify Cowork extensions

**What changed**: Added a shared Claude settings-source resolver so `install-lite`, `install.sh`, and `sync` all honor `CLAUDE_SETTINGS_SOURCE`, then fall back to `~/Desktop/Claude Config Updated.json`, then `dotfiles/claude/settings.source.json`. Tightened the `protect-secrets.js` hook and Claude deny rules so the credentials repo, live `~/.claude/settings.json`, and extension settings files are treated as blocked secret-bearing paths. Simplified `settings.local.json` back to a minimal override file. Moved the canonical Cowork engine into `plugins/ames-desktop-extensions/`, turned `scripts/_mcpb-sync-engine.py` into a compatibility wrapper, and changed the Cowork source files to reference connector plugin manifest entries instead of duplicating runtime commands. Added portable generated launchers inside each built extension, runtime smoke-test verification with a saved health report, and updated `sync` / `install.sh` so the curated Cowork set is included in the normal sync/install path. Removed placeholder-only `.gitkeep` scaffolding from `icons/`, `launchers/`, `bundles/`, and `sources/`, and refreshed docs to match the new lifecycle.

**Decisions made**: The authored Claude config can live outside the repo, but the install path has to resolve it predictably and fail loudly if the required files are missing. Cowork packaging now treats the Claude Code connector manifests as the authoritative runtime definition, while `sources/*.json` stays focused on Desktop-specific display/tool metadata and curation. Runtime verification uses newline-delimited JSON for stdio MCP requests, which matches the installed connector behavior here.

**Left off at**: `sync-cowork-extensions verify` was healthy for 12 of 13 extensions before Oliver fixed `iMCP` locally mid-session; a full rerun after that fix is the remaining confirmation step. The curated extension set is now repo-driven and on the main sync/install path, but any future connector added to the Cowork catalog still needs both a connector manifest entry and a `sources/*.json` reference.

**Open questions**: Should `sync-cowork-extensions` save curated icon PNGs back into `icons/` when it auto-generates them, or keep icons fully ephemeral? If Xcode remains intentionally conditional on the app being open, should that expectation also be captured in the preferred-connectors docs and update checks?

## 2026-04-01 — Make desktop extensions repo-driven and portable

**What changed**: Moved the Claude Desktop extension catalog out of `scripts/_mcpb-sync-engine.py` and into `plugins/ames-desktop-extensions/sources/*.json`. Updated the DXT sync engine to load those files, resolve portable path placeholders, and support a non-interactive `build` mode that refreshes `.mcpb` artifacts in `plugins/ames-desktop-extensions/bundles/` without opening install prompts. Regenerated the saved bundle set. Reduced the most obvious Oliver-specific paths in `ames-preferred-connectors/.mcp.json` by making `things3` and `iMCP` resolve from `$HOME` / standard install locations at runtime. Updated docs to describe `ames-desktop-extensions` as source files plus generated bundles. Added a README to `ames-preferred-skills` clarifying that it is intentionally empty for now.

**Decisions made**: `ames-desktop-extensions` remains outside the Claude Code plugin system, but it is now the source of truth for the Desktop extension catalog rather than a placeholder next to a script-owned catalog. Bundle artifacts stay checked in alongside the source JSON files so the repo can travel with both declarative definitions and ready-to-install `.mcpb` files. Icons still load from the scripts repo for now; the catalog and manifests were the first portability target.

**Left off at**: The repo and build flow are aligned, but the installed Desktop extensions in `~/Library/Application Support/Claude/Claude Extensions/` were not reinstalled in this pass. `scan` still reports some installed extensions as OUTDATED because the local installed manifests have not been refreshed against the new source definitions yet. Updating those requires the normal Claude Desktop approval prompts.

**Open questions**: Should icon assets move from `scripts/mcpb-icons/` into `ames-desktop-extensions/` as well so the Desktop side is fully self-contained? Should `ames-preferred-skills` stay as an intentionally empty placeholder, or should it drop out of the marketplace until it carries real third-party content?

---

## 2026-04-01 — Rename ames-skills → ames-claude, add connector plugins, deprecate family plugins

**What changed**: Completed major repo reorganization across `ames-claude`, `scripts`, and `dotfiles`. Renamed the repo from `ames-skills` to `ames-claude` (already done on GitHub in a prior session). Created four new plugin directories: `ames-original-connectors` (Oliver's own MCPs: meta, sprout-social, ynab-mcp-server, imagerelay, unifi), `ames-preferred-connectors` (curated third-party MCPs with `.mcp.json` and `update-sources.json`), `ames-preferred-skills` (stub), `ames-desktop-extensions` (not a plugin — DXT bundle placeholder). Deprecated `ames-family-finance` and `ynab-categorization` as installable plugins by removing their `.claude-plugin/` directories (content preserved, skills remain in `ames-standalone-skills`). Fixed hardcoded Bear API token in `ames-preferred-connectors/.mcp.json` → `${BEAR_API_TOKEN}`. Rewrote `ames-desktop-extensions/README.md` to accurately describe `_dxt-sync-engine.py` (uses its own hardcoded `MCPS` dict, not a `sources/` directory). Updated `sync-skills` for the `ames-claude` rename and added a one-time migration loop to remove legacy `@ames-skills` plugins. Updated dotfiles `mcp-manifest.json` and removed `apple-ecosystem.json` + `web.json` MCP configs (now bundled in `ames-preferred-connectors`). 3 repos committed and pushed.

**Decisions made**: Deprecated plugins keep their directories and skill content -- only `.claude-plugin/` is removed so `sync-skills` ignores them as installable plugins. This avoids losing content while cleaning up the install surface. Connector MCPs moved from standalone dotfiles JSON files into plugin `.mcp.json` format so they're versioned alongside the plugin and deployed via the same `sync-skills` workflow. `ames-desktop-extensions` stays as a non-plugin directory in the repo purely for organization and version control -- the DXT sync engine remains script-driven.

**Left off at**: Still need two manual Apple Notes edits in "💻 Tech" folder: (1) "💻 My Tech Stack" -- change `ames-skills repo — Plugins and skills marketplace (94 skills across 10 plugins)` → `ames-claude repo — Plugins and skills marketplace (30+ skills across 11 plugins)`; (2) "🔧 My Claude Code Setup" -- change `sync-skills — install plugins/skills from ames-skills repo` → `ames-claude repo`. Still need to add `BEAR_API_TOKEN` to `~/.claude/settings.json` env section. Still need to run `sync-skills` to install the new `@ames-claude` structure locally and trigger the legacy `@ames-skills` cleanup. Still open from previous sessions: Axiom skills interaction verification, swiftui-pro iOS 26 content update.

**Open questions**: Should `ames-preferred-connectors/update-sources.json` feed into an automated check that alerts when upstream MCP versions change? (The `check-connector-updates` script in `~/Developer/scripts/` does this via Telegram notification -- confirm it's working after `sync-skills` runs.) Should `ames-desktop-extensions` eventually become data-driven (MCPS dict → sources/ JSON files) or stay script-hardcoded?

---

## 2026-03-29 — 1Password vault skill + full credential audit

**What changed**: Created `1password-vault` skill (272 lines) for managing credentials via `op` CLI and "Claude's Access" vault. Ran comprehensive credential audit across local MacBook and Mac Mini (home-server), vaulting 12 missing credentials (34 → 46 items): Telegram Bot Token, Cloudflare API Token, Bear Notes API Token, Brrr Webhook URL, Gemini API Key, Google Workspace OAuth (client ID + secret + encryption key), ASC Issuer ID, Audiobookshelf API Key, Google Cloud credentials.db, npm Registry Auth Token. Vaulted Mac Mini SSH key. Updated all `ssh oliverames@100.79.211.138` references to `ssh home-server` across 4 memory files + audible-library skill (HTTP URLs kept as IP since `home-server` doesn't resolve for HTTP). Installed pre-commit hook on claude-code-backup to auto-run `redact-archive-keys`. Verified credentials repo is private on GitHub.

**Decisions made**: Dual storage model — new secrets go to BOTH 1Password vault AND `~/Developer/credentials/` repo. The vault provides secure search/audit/sharing; the credentials repo holds structured config that services read directly. SSH Key items require JSON template pipe (assignment statements don't support SSHKEY field type). HTTP URLs to Mac Mini services must use the Tailscale IP (100.79.211.138) because `home-server` is an SSH config alias that doesn't resolve for HTTP. Excluded non-secret identifiers from vault (APPLE_TEAM_ID, ELEVENLABS_VOICE_IDs, config flags).

**Left off at**: All 39 known credentials verified in vault. Skill installed and synced. Pre-commit hook active. Still open from previous sessions: Axiom skills interaction verification, swiftui-pro iOS 26 content update. NEW: Consider `op run` wrapping for Claude Code launch to eliminate plaintext keys in settings.json (aspirational — needs testing). The `redact-archive-keys` found no keys on this run but the backup repo's git history may still contain them from earlier commits.

**Open questions**: Should `home-server` be added to `/etc/hosts` or Tailscale MagicDNS so HTTP URLs can use the alias too? The `OP_SERVICE_ACCOUNT_TOKEN` in settings.json is the most sensitive credential (grants vault access to everything) — worth investigating if `op run` can replace it. The `sync-skills` output has a benign error: `_output.sh: line 16: s: unbound variable`.

---

## 2026-03-28 — smart-transcribe: ensemble pipeline with host-model merge delegation

**What changed**: Built the complete eight-model ensemble pipeline (`ensemble.py`, ~1900 lines). Eight ASR engines (6 cloud + 2 local) run in parallel/sequential with Rich progress display, Opus 4.6 consensus merge + structural review, and dictionary corrections. Completed a 10-pass sequential code review fixing 14 issues (unused imports, silent exception swallowing, infinite poll loop, dead variables, ANSI guard, GPT-4o elapsed time bug). Tested with 4 models — fixed Mistral model ID (`voxtral-small` → `voxtral-mini-latest`), rewrote Voxtral Mini local engine for mlx-audio's `model.generate()` API + WAV conversion, fixed Cohere MLX fallback. Implemented host-model merge delegation: when `ANTHROPIC_API_KEY` is absent, ensemble.py outputs structured JSON signaling the calling Claude instance to perform merge/review inline. Found and fixed 3 critical bugs in the delegation logic (tri-state return confusion, merge_needed conflation, inaccurate metadata header). Updated transcribe.md with full delegation instructions, SKILL.md with architecture docs, setup.sh for portable dependency installation. Version bumped to 1.2.1.

**Decisions made**: Used tri-state return pattern (`None` = delegation, `""` = failure, truthy = success) instead of exceptions or error tuples — cleanly distinguishes "can't do this" from "tried and failed" using Python's `is None` vs falsy. Mistral transcription endpoint only accepts `voxtral-mini-*` models despite `voxtral-small` being listed in their model catalog — the transcription API is a different endpoint. `review_performed` intentionally reports True on API failure (graceful degradation) since `run_review` falls back to the input text — stderr log shows the failure. Host-model delegation preserves the work directory automatically so raw transcripts are accessible.

**Left off at**: Pipeline is complete and verified (two full verification passes). Cohere Transcribe remains non-functional without HuggingFace auth (`huggingface-cli login` + access approval for gated repo `CohereLabs/cohere-transcribe-03-2026`). Internal model IDs in raw transcript JSON files differ from MODELS keys for 5/8 engines (cosmetic, not harmful). No end-to-end test with real audio + Anthropic API key for the full merge path yet.

**Open questions**: Should the MLX community version of Cohere Transcribe (`mlx-community/cohere-transcribe-03-2026-4bit`) be created/requested? The model ID in ensemble.py references it but it doesn't exist yet. Consider adding a `--dry-run` flag to ensemble.py for testing model selection without running transcriptions.

---

## 2026-03-27 — Apple dev plugin audit: Axiom adoption, skill deduplication, coding-rules trim

**What changed**: Researched 7 Apple HIG/SwiftUI plugins and skills (Axiom, Raintree, claude-swift-engineering, rshankras, Apple-Hig-Designer, mobile-ios-design, MCP Market HIG). Uninstalled Raintree apple-hig-skills (28 stars, stale), installed Axiom (686 stars, actively maintained, 175 skills + 38 agents) as user-level plugin. Removed swiftui-ui-patterns from both plugins (Axiom covers nav/architecture better). Removed testflight-deployment duplicate from standalone (kept in toolkit). Trimmed swiftui-coding-rules from 11 to 7 sections, removing state/nav/accessibility/animation overlap with swiftui-pro. Fixed #Preview contradiction. Bumped versions.

**Decisions made**: Axiom replaces Raintree for HIG coverage but apple-development-toolkit stays as the custom complement — it bundles infrastructure (MCP servers, LSP, hooks) plus unique skills (XcodeGen, ios-capabilities, macos-app-icons, TestFlight CI/CD, swiftui-reviewer agent) that Axiom doesn't cover. swiftui-pro kept as complementary review-time tool (different purpose than Axiom's write-time guidance). swiftui-coding-rules kept but scoped to its unique value: iOS 26 APIs (Liquid Glass, Foundation Models), controls semantics, styling, purpose strings.

**Left off at**: All changes committed and pushed. Axiom is installed but this session hasn't loaded it yet — next session should verify Axiom skills appear and test interaction with remaining custom skills. May want to update swiftui-pro reference files with iOS 26 content (Liquid Glass, Foundation Models) since it currently covers iOS 17-18 era patterns.

**Open questions**: Axiom is labeled "Preview Release" by its author — monitor stability. claude-swift-engineering could be useful if Oliver adopts TCA in a future project. Should swiftui-pro move into apple-development-toolkit to consolidate all Apple skills in one plugin?

---

## 2026-03-24 — Audible-library skill: metadata cleanup section + Apple Notes formatting additions

**What changed**: Added comprehensive metadata cleanup section to `audible-library` skill documenting the ABS PATCH API for fixing book metadata after import. Key addition: documented the `authors`/`narrators` array vs `authorName`/`narratorName` string gotcha (the string fields are read-only and silently no-op). Also added trigger phrases for metadata cleanup to the skill description. Apple Notes formatting skill got GUI formatting and shortcuts reference docs.

**Decisions made**: Used `authors: [{name}]` and `narrators: ["name"]` array format as the canonical API pattern after discovering that `authorName`/`narratorName` silently fail. Documented the non-Libation manual transfer workflow (Author/Title/ folder structure + SCP) as a first-class path alongside `libation-sync`. Noted that parentheses in ABS folder names can cause scan failures.

**Left off at**: Skill is updated and synced. Next session could: (1) add the Audible cover resolution findings to the skill (2000x2000 via `_SL2000_` suffix on Amazon image IDs, best source for square audiobook covers despite badges), (2) consider adding a `libation-sync` enhancement to auto-clean metadata after transfer, (3) run `sync-skills` to install the updated plugin version.

**Open questions**: Libation CLI `liberate` silently fails on some Audible Plus titles with "Validation failed" — no log file found. May need to investigate Libation's log location or file a bug. Heidi (B00BSVS1LU) specifically fails repeatedly.

---
