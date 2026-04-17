# ames-claude

Oliver Ames' personal plugin marketplace for AI coding agents. Ships 6 plugins containing 30+ skills and 18 MCP servers. Primary target is **Claude Code**; **Codex support is experimental** and included as an additive layer.

- **Repository:** https://github.com/oliverames/ames-claude
- **Marketplace name:** `ames-claude`
- **Current version:** 3.2.0

## Architecture

ames-claude is a **dual-host marketplace**. The same directory tree serves two plugin hosts with incompatible manifest formats:

| Host | Marketplace manifest | Per-plugin manifest |
|------|----------------------|---------------------|
| Claude Code | `.claude-plugin/marketplace.json` | `plugins/<name>/.claude-plugin/plugin.json` |
| Codex (experimental) | `.agents/plugins/marketplace.json` | `plugins/<name>/.codex-plugin/plugin.json` |

Both hosts read the same `plugins/<name>/skills/<skill>/SKILL.md` skill files (the SKILL.md format is portable across hosts per Anthropic's Agent Skills spec and OpenAI's Codex Skills spec) and the same `plugins/<name>/.mcp.json` MCP configs.

```
ames-claude/
├── .claude-plugin/marketplace.json        # Claude Code marketplace manifest
├── .agents/plugins/marketplace.json       # Codex marketplace manifest (experimental)
└── plugins/
    └── <plugin-name>/
        ├── .claude-plugin/plugin.json     # Claude Code plugin manifest
        ├── .codex-plugin/plugin.json      # Codex plugin manifest (experimental)
        ├── .mcp.json                      # MCP server config (optional, portable)
        └── skills/<skill-name>/SKILL.md   # Skill files (optional, portable)
```

**The Claude Code layer is authoritative and production.** The Codex layer is experimental, reflecting that Codex's official plugin marketplace launched in March 2026 and its CLI commands are still stabilizing. Both manifest sets are kept in sync when plugin content changes.

### Why one repo serves both hosts

The SKILL.md format is identical across Claude Code and Codex; only the wrapper (plugin manifest and marketplace manifest) differs. Vendoring the same skill content twice would double the maintenance burden. Keeping both manifest namespaces in one repo lets a single `git push` update both hosts.

### What does not cross the boundary

- **`ames-claude-only`** is Claude Code only by design. It houses skills that were converted from Codex-native plugins (e.g., OpenAI's iOS/macOS build plugins) and therefore cannot be installed back into Codex. This plugin is absent from the Codex marketplace manifest.
- **Third-party marketplaces that don't publish dual manifests** are out of scope for ames-claude to solve. If an upstream like `blader/humanizer` publishes only a bare skill or only a Claude-format marketplace, there's nothing ames-claude can do to make it installable in Codex. Users should install those upstream wherever the author supports.

## Installation

### Claude Code (primary)

**Declarative (preferred).** Add to `~/.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "ames-claude": {
      "source": { "source": "github", "repo": "oliverames/ames-claude" },
      "autoUpdate": true
    }
  }
}
```

Then register enabled plugins:

```json
{
  "enabledPlugins": {
    "ames-standalone-skills@ames-claude": true,
    "ames-preferred-mcps@ames-claude": true,
    "ames-ynab@ames-claude": true,
    "ames-lytho@ames-claude": true,
    "ames-community-skills@ames-claude": true,
    "ames-claude-only@ames-claude": true
  }
}
```

**Interactive.** Alternatively use slash commands:

```
/plugin marketplace add oliverames/ames-claude
/plugin install ames-standalone-skills@ames-claude
```

### Codex (experimental)

Codex's plugin marketplace launched March 2026. Install via:

```
codex marketplace add https://github.com/oliverames/ames-claude
```

Then install plugins through Codex's plugin UI. `ames-claude-only` is not available on Codex by design.

> **Status:** Codex CLI surface is still evolving. Verify exact command syntax with `codex --help` or the published Codex docs before scripting. The Codex manifests in this repo are maintained best-effort; file an issue if they fall out of spec.

## Plugins

### `ames-claude-only` (Claude Code only)

Claude-only skill bundle for content that has no Claude-compatible upstream marketplace. Currently ships two skills converted from OpenAI's Codex plugins:

- **`build-ios-apps-codex`** — iOS development workflows covering SwiftUI, App Intents, debugger agents, Liquid Glass patterns, performance auditing, UI patterns, and view refactoring. Contains nested sub-skills: `ios-app-intents`, `ios-debugger-agent`, `swiftui-liquid-glass`, `swiftui-performance-audit`, `swiftui-ui-patterns`, `swiftui-view-refactor`.
- **`build-macos-apps-codex`** — macOS development workflows covering AppKit interop, build/run/debug loops, Liquid Glass, packaging/notarization, signing/entitlements, SwiftPM, SwiftUI patterns, telemetry, test triage, view refactoring, and window management. Contains nested sub-skills: `appkit-interop`, `build-run-debug`, `liquid-glass`, `packaging-notarization`, `signing-entitlements`, `swiftpm-macos`, `swiftui-patterns`, `telemetry`, `test-triage`, `view-refactor`, `window-management`.

Both skills originated in [openai/plugins](https://github.com/openai/plugins) and were adapted for Claude Code, which is why they cannot round-trip to Codex without reconversion.

### `ames-community-skills`

Third-party skills that ship as bare SKILL.md files with no upstream marketplace, curated and wrapped for installation as a Claude Code plugin.

- **`humanizer`** — Remove signs of AI-generated writing from text. Originally by [blader](https://github.com/blader/humanizer).

### `ames-lytho`

Lytho Workflow MCP connector built and maintained by Oliver Ames. Activates the `lytho-mcp-server` MCP, providing full read/write access to Lytho work requests, tasks, proofs, projects, campaigns, and preferences via the Lytho Open API.

**Required environment variables:** `LYTHO_CLIENT_ID`, `LYTHO_CLIENT_SECRET`, `LYTHO_TOKEN_URL`

### `ames-preferred-mcps`

Curated third-party MCP servers packaged as a single plugin. Ships 16 MCP servers covering Apple platform integration, document conversion, productivity apps, and local tooling:

| MCP | Purpose |
|-----|---------|
| `1password` | 1Password credential lookup and password generation |
| `apple-docs` | Apple Developer documentation search and WWDC session lookup |
| `apple-notifier` | Native macOS notifications, speech, and screen capture |
| `docling` | Document parsing and conversion (Docling) |
| `drafts` | Drafts.app integration for note capture and editing |
| `excel` | Excel workbook manipulation |
| `google-workspace` | Gmail, Calendar, Drive, Docs, Sheets, Tasks, Meet |
| `iMCP` | Generic Apple event bridge (calendars, reminders) |
| `macos-automator` | Execute AppleScript/JXA via osascript |
| `markitdown` | Convert files to Markdown |
| `pandoc` | Universal document conversion |
| `peekaboo` | macOS UI automation and screen capture |
| `shortcuts` | List and run Apple Shortcuts |
| `SimGenie` | iOS Simulator helpers |
| `sosumi` | Apple documentation fetcher |
| `XcodeBuildMCP` | Xcode build/run/test for simulator and device workflows |

Some servers depend on locally installed apps or additional credentials. See individual server READMEs in `plugins/ames-preferred-mcps/sources/` where applicable.

### `ames-standalone-skills`

Oliver's original Claude Code skills covering writing, development, automation, finance, and AI tools. Currently 28 skills (see full catalog below).

### `ames-ynab`

YNAB (You Need A Budget) MCP connector built and maintained by Oliver Ames. Activates the `ynab-mcp-server` MCP, providing full read/write access to YNAB budgets, transactions, categories, scheduled transactions, and payees.

**Required environment variables:** `YNAB_API_TOKEN`

## Skills catalog

Full list of skills bundled in `ames-standalone-skills` (28 total):

**Writing and comms:**
- `oliver-tone` — Apply Oliver Ames' writing voice to drafts, emails, blog posts, announcements
- `draft-comms` — Draft follow-up communications from meeting notes, transcripts, or action lists
- `readme-style` — Apply Oliver's README conventions when creating or editing repo READMEs
- `resume-style` — Oliver-inspired resume typography and layout guidance
- `obsidian-notes` — Format .md notes to match Oliver's preferred Obsidian/vault style

**Apple and media:**
- `apple-music-rip` — Download DRM-free Apple Music tracks
- `audible-library` — Download and back up Audible audiobooks
- `apple-notes-formatting` — Format content for Apple Notes with proper structure
- `apple-workout-generator` — Create `.workout` files for Apple Watch
- `macos-app-icons` — Extract high-resolution app icons from macOS .app bundles
- `smart-transcribe` — Transcribe audio with cleanup and speaker attribution
- `generate-image` — Generate and edit images via AI tools
- `create-shortcut` — Build Apple Shortcuts using Jelly or raw plist
- `ios-capabilities` — Reference for iOS/macOS entitlements and Info.plist keys
- `testflight-deployment` — Deploy iOS apps to TestFlight with CI/CD setup

**Finance:**
- `ynab-finance` — Household finance management via YNAB (monthly reviews, reconciliation, reporting)

**BCBS VT (work-specific):**
- `bcbs-vt` — Context and guidance for anything BCBS VT related
- `bcbs-meeting-notes` — Structure BCBS VT meeting transcripts into notes with action items
- `bcbs-wrap-up` — End-of-session wrap-up for BCBS work, syncs to Asana

**Workflow and tooling:**
- `go` — End-to-end verify/simplify/ship pipeline, triggered by `/go`
- `wrap-up` — Session wrap-up with state persistence
- `claude-code-headless` — Interact with Claude Code from other contexts
- `cmux-workflows` — Tooling for cmux (workspace/progress/browser automation)
- `shared-terminal-tmux` — Shared interactive terminal both user and agent can drive
- `auto-web-search` — Automatic web search triggers when stuck on a problem
- `file-organization` — Apply Oliver's file naming and organization conventions

**Context and integrations:**
- `1password-vault` — Store, retrieve, and rotate credentials in 1Password
- `gmcf-masters-swim` — Daily GMCF masters swim workout lookup

Plus the skills in `ames-claude-only` (2 parent skills with 17 nested sub-skills) and `ames-community-skills` (1: humanizer).

## MCP servers catalog

Total across three plugins:

| Plugin | Server | Package |
|--------|--------|---------|
| `ames-lytho` | `lytho-mcp-server` | `@oliverames/lytho-mcp-server` (npm) |
| `ames-ynab` | `ynab-mcp-server` | `@oliverames/ynab-mcp-server` (npm) |
| `ames-preferred-mcps` | 16 third-party servers | See table above |

## Versioning

Versions live in two places per plugin:

1. `plugins/<name>/.claude-plugin/plugin.json` — `version` field (authoritative)
2. `plugins/<name>/.codex-plugin/plugin.json` — `version` field (mirror, must match)
3. Root `.claude-plugin/marketplace.json` — top-level `metadata.version` (marketplace version) and per-plugin `version` (must match per-plugin manifests)

The repo uses workflow scripts at the root (`sync`, `bump-and-sync`) to keep these aligned. After content changes, run the appropriate script to bump versions and regenerate the marketplace manifest before committing.

## Security

Plugins that bundle MCP servers inherit whatever access those MCPs have. Credentials in this repo are never stored directly; all MCPs reference environment variables (`${YNAB_API_TOKEN}`, `${LYTHO_CLIENT_ID}`, etc.) that must be populated at runtime. The `ames-preferred-mcps` plugin includes a `1password` MCP which is the intended backing credential store.

## Related

| Thing | Role |
|-------|------|
| `oliverames/dotfiles` | Shell config, install script, system-wide hooks |
| `oliverames/scripts` | CLI tools including sync utilities |
| `oliverames/claude-code-backup` | Mirror of `~/.claude/` with secrets redacted |
| [openai/plugins](https://github.com/openai/plugins) | Upstream source for skills in `ames-claude-only` |
| [twostraws/SwiftUI-Agent-Skill](https://github.com/twostraws/SwiftUI-Agent-Skill) | Recommended companion marketplace for SwiftUI Pro (installed separately) |
| [blader/humanizer](https://github.com/blader/humanizer) | Upstream source for `humanizer` in `ames-community-skills` |
