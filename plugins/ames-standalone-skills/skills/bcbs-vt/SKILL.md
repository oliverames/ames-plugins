---
name: bcbs-vt
description: >
  Use when the user asks anything about Blue Cross and Blue Shield of Vermont (BCBS VT):
  "write something for Blue Cross", "draft BCBS VT content", "check brand voice",
  "create a social post", "plan social posts", "build a content calendar",
  "write in the Blue Cross Vermont style", "draft a press release", "write marketing copy",
  "review content for brand accuracy", "create a letterhead document", "make a .docx letterhead",
  "my benefits", "Blue Cross VT employee benefits", "how much PTO do I have",
  "401k at Blue Cross", "health insurance at Blue Cross VT", "remote work policy",
  "triage a ticket", "draft a customer response", "write a KB article",
  "campaign plan for Blue Cross", "BCBS VT", "Blue Cross Vermont".
version: 1.0.0
---

# Blue Cross and Blue Shield of Vermont

Comprehensive reference for Oliver Ames's work at BCBS VT. This skill consolidates brand, marketing, customer support, benefits, social media, and letterhead resources.

## Organization Quick Reference

- **Full name:** Blue Cross and Blue Shield of Vermont
- **Short name:** Blue Cross VT
- **Headquarters:** Berlin, Vermont
- **Structure:** Local, not-for-profit health plan; BCBSA licensee; affiliated with BCBS Michigan
- **Employees:** ~400
- **CEO (2026):** Beth-Ann Roberts
- **Mission:** "We are committed to the health of Vermonters, outstanding member experiences and responsible cost management for all the people whose lives we touch."
- **Tagline:** "Vermonters Serving Vermonters"
- **Website:** bluecrossvt.org | **Social:** @bluecrossvt

## Brand Voice Summary

| Dimension | Is | Is NOT |
|-----------|-----|--------|
| Tone | Warm, approachable, knowledgeable | Cold, corporate, jargon-heavy |
| Perspective | Vermont-first, community-rooted | National, generic |
| Style | Plain-spoken, practical, empowering | Condescending, vague |
| Authority | Trusted local expert | Distant insurer |

**Core principles:** Vermont-first always, nonprofit heart, plain language, empowering not paternalistic, warm but grounded, collaborative not competitive.

**Key vocabulary:** "Vermonters" (not customers), "health plan" (not insurance policy), "health care" (two words, AP style), community, local, neighbors, well-being.

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

## Data Files

All reference data lives in `data/` next to this file. Load as needed — don't load everything upfront.

### Brand & Voice
| File | Contents |
|------|----------|
| `data/brand/brand-voice.md` | Full writing guide with verbatim examples |
| `data/brand/visual-identity.md` | Colors, typography, logo usage |
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

### Marketing & Campaigns
| File | Contents |
|------|----------|
| `data/marketing/bcbsvt-campaigns.md` | Campaign planning context |

### Social Media
| File | Contents |
|------|----------|
| `data/social/annual-themes.md` | Annual content calendar: health observances, seasonal themes, events |

### Letterhead
| File | Contents |
|------|----------|
| `data/letterhead/assets/reference.docx` | Branded pandoc reference template |
| `data/letterhead/scripts/build-letterhead.sh` | Build script for branded .docx |
| `data/letterhead/scripts/style-reference-doc.py` | Python script to regenerate reference.docx |

**Letterhead usage:**
```bash
pandoc input.md --reference-doc=data/letterhead/assets/reference.docx -o output.docx
```

## Source Documents on Disk

The `~/Documents/BCBS/` folder contains original documents organized by category. Read these for additional context as needed — do not move or modify them.

### ~/Documents/BCBS/
```
├── 2026-03-16 Blue Cross VT Social Media Strategy Plan.pdf
├── Benefits/
│   ├── 2026 Benefit Packet.pdf
│   ├── 2026 BlueCross BlueShield of Vermont New Hire Benefits Summary.pdf
│   ├── Blue Cross - Culture Values Benefits - 2026.pdf
│   ├── Health Insurance Comparison — BCBS vs VEHI Gold CDHP.md
│   ├── Health Insurance Scenario Planner.xlsx
│   └── Benefits Presentation/ (20 screenshot PNGs from benefits walkthrough)
├── Calls/
│   ├── 2026-03-13 Call with Ashley.md
│   ├── 2026-03-13 Call with Cass Lang.md
│   ├── 2026-03-13 Call with Kristina Massari.md
│   ├── 2026-03-13 Onboarding Call with Gina Brittain.md
│   └── 2026-03-13 Senior Games Planning Call.md
├── Hiring/
│   ├── 2025-12-02 Call with BCBS VT.md
│   ├── 2026-02-02 Blue Cross Offer Call.md
│   ├── 2026-02-05 Job Offer Acceptance - Oliver & Beth/ (audio + transcript)
│   ├── 2026-02-09 BlueCross BlueShield Vermont Offer Letter.pdf
│   └── Oliver Ames Cover Letter - Marketing - BCBSVT.docx
├── Onboarding/
│   ├── 2026 BlueCross BlueShield of Vermont Remote Work Policy.pdf
│   ├── Blue Cross - What to Expect (onsite).pdf
│   ├── Blue Cross VT Remote Access Authorization.pdf
│   └── (i-9, W-4, relocation agreement, Outlook setup, etc.)
└── Reference/
    ├── 2025-11 Social Media Strategist Position Description.docx
    └── 2026-03 BlueCross VT Brand and Engagement Team Welcome Deck.pdf
```

## Content Pillars & Mix

1. **Health & Wellness** (35%) — Preventive care, mental health, nutrition, seasonal tips
2. **Community** (30%) — Events, grants, partnerships, youth programs, volunteering
3. **Coverage Education** (20%) — How insurance works, cost transparency, benefit explanations
4. **Corporate** (10%) — Awards, leadership, culture, workplace wellness
5. **Advocacy** (5%) — Affordability, access, system reform

## Social Media Posting Cadence

| Platform | Frequency | Hashtags | Emoji |
|----------|-----------|----------|-------|
| Instagram | 4-5x/week | 5-7 | Yes |
| Facebook | 3-4x/week | 3-5 | Yes |
| LinkedIn | 3x/week | 3-4 | Sparse |
| YouTube | 2x/month | — | — |

Always include: #BlueCrossVT #Vermont

## Medicare Warning (2026)

Vermont Blue Advantage discontinued all Medicare Advantage plans. Do NOT reference MA availability. Current offerings: Vermont Medigap Blue, Vermont Blue 65 Supplement, Blue MedicareRx (Part D).
