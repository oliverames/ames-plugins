---
name: readme-style
description: >-
  Use when creating or updating README.md files for Oliver's public repositories.
  Apply this skill any time you are about to write or edit a README — even if
  the user just says "document this", "add a README", or you're creating a new
  public-facing project. Also triggers for "write a README", "update the README",
  "improve README", "make the README better", "brand the repo", "add docs to
  this repo", or "make this look professional on GitHub". Provides Oliver's
  personal brand identity, structure conventions, and quality bar for GitHub READMEs.
---

# README Style Guide

Oliver's public GitHub READMEs serve as marketing pages. They should feel
professional, strategic, and branded — like they could be an official product
page for the service they interface with, while clearly being Oliver's work.

## Brand Identity

**Who**: Oliver Ames — content strategist, software tinkerer, and video
producer in Montpelier, Vermont.

**Site**: [ames.consulting](https://ames.consulting)

**Voice**: Professional but approachable. Technically deep but accessible.
Explain the "why" behind decisions, not just the "what." Show strategic
thinking. Never generic or corporate-bland.

**Visual brand** (from ames.consulting):
- Accent color: amber/orange (`#f5a542`) — use for badges and highlights
- Tone: warm, confident, clean
- Fonts can't be controlled on GitHub, but mirror the feel: clear hierarchy,
  generous whitespace, concise prose

**Support link**: `https://www.buymeacoffee.com/oliverames`

**Social links**:
- GitHub: `https://github.com/oliverames`
- LinkedIn: `https://linkedin.com/in/oliverames`
- Bluesky: `https://bsky.app/profile/oliverames.bsky.social`
- Site: `https://ames.consulting`

## README Structure

Every public repo README should follow this structure. Adapt section depth
to the project — a 310-tool MCP server warrants more detail than a simple
utility script.

### 1. Header Block (centered HTML)

```html
<p align="center">
  <!-- Icon or logo for the product/service this project integrates with -->
  <img src="icon.png" width="80" height="80" alt="Project Name">
</p>

<h1 align="center">Project Name</h1>

<p align="center">
  <strong>One-line value proposition — what it does and why it matters</strong>
</p>

<p align="center">
  <code>key stat</code> &bull;
  <code>key stat</code> &bull;
  <code>key stat</code>
</p>
```

Use the official icon/logo of the product the project interfaces with (Meta,
UniFi, YNAB, etc.) when available. For original projects, use the project's
own icon.

### 2. Badge Row (centered)

Always include these badges in this order:

```html
<p align="center">
  <a href="https://www.npmjs.com/package/PACKAGE_NAME">
    <img src="https://img.shields.io/npm/v/PACKAGE_NAME?style=flat-square&color=f5a542" alt="npm">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-f5a542?style=flat-square" alt="License">
  </a>
  <a href="https://www.buymeacoffee.com/oliverames">
    <img src="https://img.shields.io/badge/Buy_Me_a_Coffee-support-f5a542?style=flat-square&logo=buy-me-a-coffee&logoColor=white" alt="Buy Me a Coffee">
  </a>
</p>
```

Rules:
- Use `color=f5a542` (Oliver's brand amber) for all badge colors
- Use `style=flat-square` for all badges
- Include npm version badge if published to npm
- Always include the Buy Me a Coffee badge — this is required on every repo
- Include license badge
- Add other relevant badges (build status, coverage) only if they exist

### 3. Horizontal Rule + Opening Paragraph

```markdown
---

Brief description (2-3 sentences). What the project does, who it's for, and
what makes it different from alternatives. Lead with value, not implementation.
```

### 4. Why This Exists

Frame the project strategically. Not "I built this because I wanted to" but
rather what problem it solves and the thinking behind the approach. Show
the strategic reasoning — this is what separates Oliver's repos from generic
open source projects.

For MCP servers: explain why an AI assistant needs deep access to this
particular service, and what becomes possible.

For apps: explain the user problem and why existing solutions fail.

### 5. Quick Start

Immediately actionable. For MCP servers, this is the JSON config block. For
apps, it's the install command. For libraries, it's the import + first call.

### 6. Core Content

This varies by project type but should show **depth and breadth**:

**For MCP servers:**
- Tool coverage table (categories, counts, representative tool names)
- API layer coverage (which API versions/endpoints are supported)
- Architecture decisions (lazy mode, confirm gate, version detection, etc.)
- Usage examples showing natural language → tool flow

**For apps:**
- Feature walkthrough with screenshots
- Technical approach (why this solution works better)
- Configuration options

**For libraries/utilities:**
- API reference
- Examples
- Design decisions

### 7. Configuration / Reference

Tables for environment variables, config options, CLI flags. Use this format:

```markdown
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VAR` | Yes | — | What it does |
```

### 8. Architecture (optional, for complex projects)

File tree with annotations. Show the design thinking.

### 9. Building / Development

How to build, test, and contribute.

### 10. Footer (centered HTML)

```html
---

<p align="center">
  <a href="https://www.buymeacoffee.com/oliverames">
    <img src="https://img.shields.io/badge/Buy_Me_a_Coffee-support-f5a542?style=for-the-badge&logo=buy-me-a-coffee&logoColor=white" alt="Buy Me a Coffee">
  </a>
</p>

<p align="center">
  <sub>
    Built by <a href="https://ames.consulting">Oliver Ames</a> in Vermont
    &bull; <a href="https://github.com/oliverames">GitHub</a>
    &bull; <a href="https://linkedin.com/in/oliverames">LinkedIn</a>
    &bull; <a href="https://bsky.app/profile/oliverames.bsky.social">Bluesky</a>
  </sub>
</p>
```

The footer Buy Me a Coffee badge uses `style=for-the-badge` (larger) vs
the header badges which use `style=flat-square` (compact).

## Quality Bar

Before shipping a README, verify:

- [ ] Header has centered icon + name + tagline + key stats
- [ ] Badge row includes npm (if applicable), license, and Buy Me a Coffee
- [ ] "Why This Exists" section frames the project strategically
- [ ] Quick start is immediately actionable (copy-paste ready)
- [ ] Core content shows both breadth (what it covers) and depth (how it works)
- [ ] Configuration is in a clean table
- [ ] Footer has Buy Me a Coffee + social links
- [ ] Tone is professional but warm — not generic, not overly casual
- [ ] No broken links or placeholder text
- [ ] Feels like it could be an official product page for the service it
  integrates with

## Anti-Patterns

- Generic "awesome project" language with no substance
- Wall of text with no visual hierarchy
- Missing the "why" — just listing features without context
- Corporate jargon or buzzword soup
- Promising features that don't exist
- Screenshots or examples that are out of date
- No Buy Me a Coffee link (required on every public repo)

## Product-Specific Branding

When the project integrates with a specific product (Meta, UniFi, YNAB,
Sprout Social, Image Relay), the README should feel native to that ecosystem:

- Use the product's official icon in the header
- Reference the product's terminology correctly
- Structure the README the way that product's developer docs would
- But maintain Oliver's voice and brand — it's clearly his work, styled
  to complement the product's identity
