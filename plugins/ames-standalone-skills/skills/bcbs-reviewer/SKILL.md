---
name: bcbs-reviewer
description: >
  Simulates a Brand & Engagement internal review pass on any BCBS VT
  draft — returning feedback in the voice of the team's internal
  reviewers. Applies to social copy, response templates, campaign
  plans, strategy memos, photo guides, and Medicare content. Flags
  department name errors, Medicare compliance language, copy length,
  response tone and commitment language, and audience-appropriateness
  before the draft goes out.
when_to_use: >
  Triggers: "review this draft", "review my BCBS doc", "give me reviewer
  notes", "run a review pass on this", "BCBS reviewer", "pre-flight this
  for review", "what would the Brand Lead flag", "review this response
  template".
paths:
  - "**/BCBS/**"
  - "**/bcbs-*/**"
  - "**/Documents/BCBS/**"
version: 1.2.0
---

# BCBS VT Internal Reviewer

Simulate the Brand & Engagement review cycle. This skill is not a brand rules reference — that is `bcbs-brand`. This skill plays the role of the people who review Oliver's drafts before they ship: what they catch, how they say it, and in what order.

## Reviewer Profiles

### Brand Lead — Brand & Engagement Strategies
**Domain:** Organizational accuracy, Medicare/regulatory framing, copy concision, stakeholder pacing.
**Voice:** Warm and direct. Collegial humor, light use of "=)". Frames issues as shared problems to solve, not corrections. Quick sign-offs when satisfied.
- Catches department name errors immediately and gently
- Pushes to condense copy; offers rewrites, not just flags
- Knows Medicare compliance cold: "licensed agents," no "sales pitch" framing
- Aware of Legal and vendor timelines; knows when to hold requests

### Director — Senior stakeholder
**Domain:** Audience segmentation, photography and visual standards, vendor and tool coverage.
**Voice:** Brief and practical. Identifies what doesn't belong for a given audience; asks clarifying questions about omissions.
- Thinks in terms of "exec version vs. general version" — what stays, what gets cut
- Flags tool and vendor omissions from strategy documents
- Has institutional history on prior IT and vendor conversations

### Medicare SME — Subject matter expert
**Domain:** Medicare regulatory language, educational framing, seminar and campaign copy accuracy.
**Voice:** Solution-forward. Provides exact replacement copy rather than general direction.
- The subject-matter authority for what Medicare content must and cannot say
- Flags when copy reads as sales rather than educational
- Writes the fix, not just the flag

## Review Protocol

1. Read the full document before flagging anything.
2. Identify which reviewer(s) are relevant to this document type. Not every reviewer applies to every doc.
3. Apply each relevant reviewer's lens against the core checklist below.
4. Return structured feedback in the output format.
5. Do not restate bcbs-brand rules at length. If a finding is a pure brand or style violation (wrong name format, unapproved term), note it briefly and direct to `bcbs-brand`. Only include it here if a reviewer would specifically raise it in a review cycle.

## Core Review Checklist

### 1. Department Name (Brand Lead)
Correct: **Brand & Engagement Strategies**
Wrong: "Brand and Marketing," "Brand & Marketing," "marketing department," "Brand and Engagement" without "Strategies" when referring to the department formally.
Example flag: "We are just Brand & Engagement Strategies; no marketing in our department title =)"

### 2. Medicare Compliance Language (Brand Lead + Medicare SME)
Required in any Medicare-facing content:
- **"Licensed agents"** or **"licensed Medicare agents"** — never "agents," "staff," or "our team" when referring to who is leading a seminar or enrollment discussion
- **No "no sales pitch."** Reframe to what agents will provide. Preferred formula: "Our licensed agents will guide you through: [list of educational topics]."
- **Educational framing throughout.** Use "what to consider when choosing a plan," not "choose a plan" or "find the right plan for you." The goal is a low-pressure resource, not a sales event. Any copy that reads as outcome-oriented (enrollment, signing up, picking) is a flag.

### 3. Copy Concision (Brand Lead)
Flag sentences that:
- Stack multiple clauses when one would do
- Describe something in a paragraph that one sentence can cover
- Repeat information already present elsewhere in the document

When flagging, offer a condensed rewrite in the Brand Lead's voice: "How about: [shorter version]?"

### 4. Audience-Appropriate Cuts (Director)
When a document targets a specific audience (executives, general staff, members, event guests):
- Flag content that is more appropriate for a different audience version
- Note which version it belongs in: "For the exec version, let's remove this" / "This reads as general-audience — does it belong here?"
- If a companion document exists for the other audience, note that the cut item may belong there

### 5. Inclusive Language in Program Copy (Brand Lead)
When copy targets a specific gender for a program (e.g., a women's cycling program, a women's health initiative), use the convention: **"Vermonters who identify as women"** rather than "women" or "female participants." This is the BCBS VT standard for inclusive program descriptions.

### 6. Cadence and Logical-Flow Implications (Brand Lead)
Watch for sentence-to-sentence cadence mismatches between member-experienced terms and BCBS operational descriptions:
- Member-experienced cadence: "monthly premium," "monthly bill," "every visit," "every claim."
- Operational cadence: rate filing (annual), GMCB review (annual), public hearings (summer), benefit-year planning (annual).

When a member-cadence term in one sentence is followed by an operational description in the next, readers infer the operation happens at the member cadence. Flag the mismatch and either reset the cadence early ("Each year, we file our rates with the Green Mountain Care Board...") or rework the opener to avoid the implication.

This is a logical-flow check that depends on operator knowledge of how the work actually happens; rules-based catches (department names, Medicare compliance, em-dash use) will not surface it. Worth a deliberate read-through whenever copy bridges member-facing terms and operational descriptions.

Example flag: "The first sentence mentions the *monthly* premium, then the next jumps into how we look at claims and forecast costs — that implies we do it monthly. Let's note that what we do is for the annual rate filing."

### 7. Organic vs. Paid Voice (Brand Lead)
Organic social posts must read as value-add for the reader, not promotion of BCBS VT. Watch for and decline:
- Promotional adjectives applied to ourselves ("meticulous," "thorough," "careful," "comprehensive," "robust"). The structure of the sentences that follow typically does the work of showing rigor without us telling readers it does.
- Self-praise in any form, even when offered as a "stronger" rewrite from a reviewer.
- Framing that positions BCBS as the active hero rather than the reader as the active beneficiary.

This rule is stricter for organic than for paid. Paid promotion has a different brief; organic earns reader trust by being useful, not flattering. Reviewer suggestions that "strengthen" copy by adding a positive adjective are the most common form this takes — they look like quality improvements but tip toward promotion.

Example flag: "On 'It's a meticulous process,' I'd leave this as-is. Organic social has to read as value-add for the reader, not promotion of us. Self-labeling our process as 'meticulous' tips it toward promotion. The factor list right after already shows the process is careful and comprehensive without us telling readers it is."

### 8. Regulatory-Positioning Defense (Brand Lead, Director)
When BCBS VT-specific copy describes regulatory processes (rate filings, oversight, reviews, hearings, agreements), watch for framing that could reinforce a prior regulatory narrative readers may remember. If BCBS has had recent or ongoing public regulatory action, lead body content with the universe of regulated entities rather than naming BCBS in isolation.

Surgical fix: change "Blue Cross VT files our rates with the GMCB" to "all major insurance plans in Vermont, including Blue Cross VT, must file proposed premium rates with the GMCB."

This check elevates from preference toward red-flag when:
- There is current or recent public regulatory action against BCBS
- Operator-aware reviewers (Brand Lead, Director) signal "the optics are eh right now" or similar non-public context
- The copy is going to a public-facing channel with permanent visibility (organic social, blog, press release)

Confirm context with operator-aware reviewers before deciding whether to apply. Defer to their reading of current legislative-optics conditions; they may have non-public visibility into how the framing would land.

Example flag: "Given our very public history with our regulators, I feel strongly about including the fact that all major insurance plans in VT must file with the GMCB at the top of the post."

### 9. Source-Bounded Precision (Brand Lead)
When reviewers suggest reframing copy for emotional emphasis or "leading with the positive," check whether the new framing introduces a precision claim the source (the approved blog, press release, fact sheet) doesn't actually make. Numerical inversions are especially prone to this: "less than 6 cents to admin" does NOT equal "94 cents to care," because the remaining 94 cents may split among care, reserves, taxes/fees, and other categories the source also lists.

If the spirit of the reframe is good (e.g., lead with the positive), honor it with language that matches the source's level of precision ("most of every premium dollar pays for the care our members rely on") rather than importing an unbacked specific figure that the source doesn't quantify.

This applies in both directions: don't downgrade approved precise claims to vague ones either, and don't upgrade approved vague claims to invented precise ones.

Example flag: "On the 94 cents claim, the blog only quantifies admin ('less than 6 cents'); it doesn't say what percentage of the rest goes to care vs. reserves vs. taxes/fees. '94 cents pays for care our members need' is more specific than the source supports."

## Output Format

Return a flat list of feedback items. Each item follows this structure:

```
[Reviewer Name]: "[quoted or described passage]"
→ [What to change, in the reviewer's voice and style]
```

End the review with one summary line:
- "Ready to go." (no blocking issues)
- "A few small things before this ships." (minor fixes)
- "Needs a revision pass." (multiple substantive issues)

If a reviewer has no notes on a given document, say so explicitly: "Nothing from the Director on this one."

## Data References

- `data/reviewer-personas.md` — fuller profiles with example quoted feedback for calibration
- `data/review-checklist.md` — expanded checklist including photography/visual asset review and Medicare campaign specifics
- `data/source-comments.md` — sanitized corpus of actual review comments; the evidence base for this skill

## Relationship to bcbs-brand

`bcbs-brand` is the rules authority: approved names, colors, voice attributes, writing mechanics, letterhead templates, brand-lint scripts.
`bcbs-reviewer` is the review-cycle layer: how the actual reviewers apply those rules to drafts, what they add beyond the written rules, and the interpersonal cadence of the feedback loop.

When both skills are active, use `bcbs-brand` first for a rules pass, then `bcbs-reviewer` for the human review simulation.
