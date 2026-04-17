<h1 align="center">ames-claude</h1>

<p align="center">
  <strong>Personal plugin marketplace for Claude Code, with experimental Codex support</strong>
</p>

<p align="center">
  <code>6 plugins</code> &bull;
  <code>31 skills</code> &bull;
  <code>18 MCP servers</code> &bull;
  <code>dual-host</code>
</p>

<p align="center">
  <a href="https://www.buymeacoffee.com/oliverames">
    <img src="https://img.shields.io/badge/Buy_Me_a_Coffee-support-f5a542?style=flat-square&logo=buy-me-a-coffee&logoColor=white" alt="Buy Me a Coffee">
  </a>
</p>

---

A single repo that ships Oliver Ames' personal plugin catalog to two AI coding agents at once: **Claude Code** (official, supported) and **Codex** (experimental). The same plugin tree carries both manifest formats side by side, so one `git push` updates both hosts.

## Why this exists

Running two agents without duplicating content is a real problem. Claude Code and Codex both adopted a plugin/skill model in early 2026, but they publish incompatible marketplace manifests at different paths (`.claude-plugin/` vs `.agents/plugins/`) and different schemas. Most marketplaces ship only one. That forces users to either pick an agent or maintain parallel forks.

ames-claude takes the additive route. One tree, two manifest namespaces, identical skill and MCP content underneath. Skills are portable by spec (the SKILL.md format is shared across hosts per Anthropic's Agent Skills and OpenAI's Codex Skills). Only the plugin and marketplace manifests differ, and both sit in the same repo. The cost is a small amount of duplicated JSON; the benefit is a single source of truth for an otherwise split ecosystem.

**Claude Code support is production.** **Codex support is experimental**, since Codex's plugin marketplace launched March 2026 and its CLI surface is still stabilizing.

## Quick start

### Claude Code (official, supported)

**Declarative install.** Add to `~/.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "ames-claude": {
      "source": { "source": "github", "repo": "oliverames/ames-claude" },
      "autoUpdate": true
    }
  },
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

Restart Claude Code. The marketplace registers, plugins install, and `autoUpdate` keeps them current on each launch.

**Interactive install.** Or run:

```
/plugin marketplace add oliverames/ames-claude
/plugin install ames-standalone-skills@ames-claude
/plugin install ames-preferred-mcps@ames-claude
/plugin install ames-ynab@ames-claude
/plugin install ames-lytho@ames-claude
/plugin install ames-community-skills@ames-claude
/plugin install ames-claude-only@ames-claude
```

### Codex (experimental)

```
codex marketplace add https://github.com/oliverames/ames-claude
```

Then install plugins through Codex's plugin UI or CLI. `ames-claude-only` is intentionally absent from the Codex side (see below).

> **Heads-up:** Codex's marketplace commands are still stabilizing. Verify exact syntax with `codex --help` before scripting. File an issue if any Codex manifest in this repo falls out of spec.

## Plugins

Six plugins ship in this marketplace:

| Plugin | Hosts | Version | Summary |
|--------|-------|---------|---------|
| [`ames-standalone-skills`](plugins/ames-standalone-skills/) | Claude + Codex | 3.2.0 | Oliver's original skill pack (28 skills) |
| [`ames-preferred-mcps`](plugins/ames-preferred-mcps/) | Claude + Codex | 1.4.0 | 16 curated third-party MCP servers |
| [`ames-ynab`](plugins/ames-ynab/) | Claude + Codex | 2.0.0 | Custom YNAB MCP connector |
| [`ames-lytho`](plugins/ames-lytho/) | Claude + Codex | 1.0.0 | Custom Lytho Workflow MCP connector |
| [`ames-community-skills`](plugins/ames-community-skills/) | Claude + Codex | 2.0.0 | Third-party skills without upstream marketplaces |
| [`ames-claude-only`](plugins/ames-claude-only/) | **Claude only** | 1.0.0 | Skills converted from Codex plugins, non-reversible |

### `ames-standalone-skills`

Oliver's original Claude Code skills covering writing, development, automation, finance, and Apple platform work. 28 skills organized by theme (see [Skills catalog](#skills-catalog)).

### `ames-preferred-mcps`

A single plugin that activates 16 curated third-party MCP servers:

| MCP | Purpose |
|-----|---------|
| `1password` | 1Password credential lookup and password generation |
| `apple-docs` | Apple Developer documentation search and WWDC lookup |
| `apple-notifier` | Native macOS notifications, speech, screen capture |
| `docling` | Document parsing and conversion |
| `drafts` | Drafts.app integration for note capture |
| `excel` | Excel workbook manipulation |
| `google-workspace` | Gmail, Calendar, Drive, Docs, Sheets, Tasks, Meet |
| `iMCP` | Apple event bridge (calendars, reminders) |
| `macos-automator` | AppleScript and JXA via osascript |
| `markitdown` | Convert files to Markdown |
| `pandoc` | Universal document conversion |
| `peekaboo` | macOS UI automation and screen capture |
| `shortcuts` | List and run Apple Shortcuts |
| `SimGenie` | iOS Simulator helpers |
| `sosumi` | Apple documentation fetcher |
| `XcodeBuildMCP` | Xcode build/run/test for simulators and devices |

Some servers depend on locally installed apps or additional credentials.

### `ames-ynab`

Activates `ynab-mcp-server` (published as `@oliverames/ynab-mcp-server` on npm) for read and write access to YNAB budgets, transactions, categories, scheduled transactions, and payees.

**Required env:** `YNAB_API_TOKEN`

### `ames-lytho`

Activates `lytho-mcp-server` (published as `@oliverames/lytho-mcp-server` on npm) for read and write access to Lytho work requests, tasks, proofs, projects, campaigns, and preferences through the Lytho Open API.

**Required env:** `LYTHO_CLIENT_ID`, `LYTHO_CLIENT_SECRET`, `LYTHO_TOKEN_URL`

### `ames-community-skills`

A wrapper for third-party skills that ship as bare `SKILL.md` files with no upstream marketplace of their own. Currently one skill:

- [`humanizer`](plugins/ames-community-skills/skills/humanizer/) — Remove signs of AI-generated writing from text. Originally by [blader](https://github.com/blader/humanizer).

When an upstream author publishes their own marketplace (as [twostraws](https://github.com/twostraws/SwiftUI-Agent-Skill) did with SwiftUI Pro), that upstream is preferred and the skill leaves this plugin.

### `ames-claude-only`

Claude Code only. Houses skills converted from Codex-native plugins that cannot round-trip to Codex without reconversion. Currently two:

- [`build-ios-apps-codex`](plugins/ames-claude-only/skills/build-ios-apps-codex/) — iOS workflows: App Intents, debugger agents, Liquid Glass, performance auditing, SwiftUI UI patterns, view refactoring. Contains nested sub-skills.
- [`build-macos-apps-codex`](plugins/ames-claude-only/skills/build-macos-apps-codex/) — macOS workflows: AppKit interop, build/run/debug, packaging and notarization, signing, SwiftPM, SwiftUI patterns, telemetry, test triage, window management. Contains nested sub-skills.

Both originated in [openai/plugins](https://github.com/openai/plugins) and were adapted for Claude Code. They are omitted from the Codex marketplace manifest by design, since installing them in Codex would re-import already-diverged skills.

## Skills catalog

28 skills in `ames-standalone-skills`, grouped by theme:

**Writing and communications**
- [`oliver-tone`](plugins/ames-standalone-skills/skills/oliver-tone/) — Apply Oliver's writing voice to drafts, emails, blog posts, announcements
- [`draft-comms`](plugins/ames-standalone-skills/skills/draft-comms/) — Turn meeting notes, transcripts, or action lists into follow-up messages
- [`readme-style`](plugins/ames-standalone-skills/skills/readme-style/) — Apply Oliver's README conventions (used to author this very file)
- [`resume-style`](plugins/ames-standalone-skills/skills/resume-style/) — Ames-inspired resume typography and layout
- [`obsidian-notes`](plugins/ames-standalone-skills/skills/obsidian-notes/) — Format Markdown notes to match Oliver's vault style

**Apple platform and media**
- [`apple-music-rip`](plugins/ames-standalone-skills/skills/apple-music-rip/) — Download DRM-free Apple Music tracks
- [`audible-library`](plugins/ames-standalone-skills/skills/audible-library/) — Download and back up Audible audiobooks
- [`apple-notes-formatting`](plugins/ames-standalone-skills/skills/apple-notes-formatting/) — Format content for Apple Notes
- [`apple-workout-generator`](plugins/ames-standalone-skills/skills/apple-workout-generator/) — Create `.workout` files for Apple Watch
- [`macos-app-icons`](plugins/ames-standalone-skills/skills/macos-app-icons/) — Extract high-res app icons from `.app` bundles
- [`smart-transcribe`](plugins/ames-standalone-skills/skills/smart-transcribe/) — Transcribe audio with cleanup and speaker attribution
- [`generate-image`](plugins/ames-standalone-skills/skills/generate-image/) — Generate and edit images via AI tools
- [`create-shortcut`](plugins/ames-standalone-skills/skills/create-shortcut/) — Build Apple Shortcuts via Jelly or raw plist
- [`ios-capabilities`](plugins/ames-standalone-skills/skills/ios-capabilities/) — Reference for entitlements and Info.plist keys
- [`testflight-deployment`](plugins/ames-standalone-skills/skills/testflight-deployment/) — Deploy iOS apps to TestFlight with CI/CD

**Finance**
- [`ynab-finance`](plugins/ames-standalone-skills/skills/ynab-finance/) — Household finance via YNAB (reviews, reconciliation, reporting)

**BCBS VT (work-specific)**
- [`bcbs-vt`](plugins/ames-standalone-skills/skills/bcbs-vt/) — Context and guidance for BCBS VT work
- [`bcbs-meeting-notes`](plugins/ames-standalone-skills/skills/bcbs-meeting-notes/) — Structure BCBS VT transcripts into notes with action items
- [`bcbs-wrap-up`](plugins/ames-standalone-skills/skills/bcbs-wrap-up/) — End-of-session wrap-up, syncs to Asana

**Workflow and tooling**
- [`go`](plugins/ames-standalone-skills/skills/go/) — End-to-end verify/simplify/ship pipeline, triggered by `/go`
- [`wrap-up`](plugins/ames-standalone-skills/skills/wrap-up/) — Session wrap-up with state persistence
- [`claude-code-headless`](plugins/ames-standalone-skills/skills/claude-code-headless/) — Interact with Claude Code from other contexts
- [`cmux-workflows`](plugins/ames-standalone-skills/skills/cmux-workflows/) — Tooling for cmux workspaces
- [`shared-terminal-tmux`](plugins/ames-standalone-skills/skills/shared-terminal-tmux/) — Shared interactive terminal for user and agent
- [`auto-web-search`](plugins/ames-standalone-skills/skills/auto-web-search/) — Automatic web search when stuck on a problem
- [`file-organization`](plugins/ames-standalone-skills/skills/file-organization/) — Oliver's file naming and organization conventions

**Context and integrations**
- [`1password-vault`](plugins/ames-standalone-skills/skills/1password-vault/) — Store, retrieve, and rotate credentials in 1Password
- [`gmcf-masters-swim`](plugins/ames-standalone-skills/skills/gmcf-masters-swim/) — Daily GMCF masters swim workout lookup

Plus 2 parent skills in `ames-claude-only` (with 17 nested sub-skills) and 1 in `ames-community-skills`.

## MCP servers catalog

18 MCP servers across three plugins:

| Plugin | Server | Package |
|--------|--------|---------|
| `ames-lytho` | `lytho-mcp-server` | [`@oliverames/lytho-mcp-server`](https://www.npmjs.com/package/@oliverames/lytho-mcp-server) |
| `ames-ynab` | `ynab-mcp-server` | [`@oliverames/ynab-mcp-server`](https://www.npmjs.com/package/@oliverames/ynab-mcp-server) |
| `ames-preferred-mcps` | 16 third-party servers | See [plugin table](#ames-preferred-mcps) above |

## Architecture

The repo carries two parallel manifest namespaces under a shared plugin tree:

```
ames-claude/
├── .claude-plugin/marketplace.json        # Claude Code marketplace (authoritative)
├── .agents/plugins/marketplace.json       # Codex marketplace (experimental)
└── plugins/
    └── <plugin-name>/
        ├── .claude-plugin/plugin.json     # Claude Code plugin manifest
        ├── .codex-plugin/plugin.json      # Codex plugin manifest (if applicable)
        ├── .mcp.json                      # MCP server config (portable across hosts)
        └── skills/<skill-name>/SKILL.md   # Skill files (portable across hosts)
```

| Host | Marketplace manifest | Per-plugin manifest | Plugins |
|------|----------------------|---------------------|---------|
| Claude Code | `.claude-plugin/marketplace.json` | `.claude-plugin/plugin.json` | 6 |
| Codex (experimental) | `.agents/plugins/marketplace.json` | `.codex-plugin/plugin.json` | 5 (excludes `ames-claude-only`) |

### What crosses the boundary

- **Skill content** (`SKILL.md` and bundled resources) is portable by spec
- **MCP configs** (`.mcp.json`) use the same shape on both hosts
- **Plugin content** structurally matches on both sides

### What does not

- **Plugin and marketplace manifests** differ in location and schema; they live side by side in the same repo
- **`ames-claude-only`** is Claude Code only by design (converted-from-Codex skills can't round-trip cleanly)
- **Third-party marketplaces that publish only one manifest format** can't be rewrapped by ames-claude. Install those from upstream wherever the author supports

## Configuration

Per-plugin environment requirements:

| Plugin | Variable | Required | Purpose |
|--------|----------|----------|---------|
| `ames-ynab` | `YNAB_API_TOKEN` | Yes | YNAB Personal Access Token |
| `ames-lytho` | `LYTHO_CLIENT_ID` | Yes | Lytho OAuth client ID |
| `ames-lytho` | `LYTHO_CLIENT_SECRET` | Yes | Lytho OAuth client secret |
| `ames-lytho` | `LYTHO_TOKEN_URL` | Yes | Lytho OAuth token endpoint |
| `ames-preferred-mcps` | varies | varies | Some servers require their own credentials or apps |

Credentials are never stored in the repo. All MCPs reference environment variables at runtime, and `ames-preferred-mcps` includes a `1password` MCP for credential resolution via `op read`.

## Versioning

Each plugin's version lives in three places that must stay in sync:

1. `plugins/<name>/.claude-plugin/plugin.json` — Claude-side authoritative
2. `plugins/<name>/.codex-plugin/plugin.json` — Codex mirror (must match 1)
3. Root `.claude-plugin/marketplace.json` — per-plugin `version` (must match 1)

The marketplace itself has a separate version at `.claude-plugin/marketplace.json`'s top-level `metadata.version`, currently `3.2.0`.

Workflow scripts at the repo root (`sync`, `bump-and-sync`) help keep these aligned after content changes. Always run one of those before committing version-bearing changes.

## Development

### Adding a new skill

1. Create `plugins/ames-standalone-skills/skills/<skill-name>/SKILL.md` with YAML frontmatter (`name`, `description`)
2. Add supporting files (references, scripts) in subdirectories as needed
3. Run `bump-and-sync` from the repo root
4. Commit and push; Claude Code users with `autoUpdate` pick it up on next launch

### Adding a new plugin

1. Create `plugins/<plugin-name>/.claude-plugin/plugin.json` with `name`, `version`, `description`, `author`
2. For dual-host support, also create `plugins/<plugin-name>/.codex-plugin/plugin.json` mirroring the Claude manifest with Codex-specific `interface` and `category` fields
3. Add the plugin entry to both `.claude-plugin/marketplace.json` and `.agents/plugins/marketplace.json`
4. Add content (skills, commands, MCPs) at the plugin root per spec
5. Run `bump-and-sync` and commit

## My Claude Code configuration

A snapshot of Oliver's full Claude Code setup alongside ames-claude, kept here as a rebuilding reference. If this machine died tomorrow, the tables below plus `~/.claude/settings.json` would reconstruct the environment.

### Installed third-party marketplaces

14 marketplaces registered in `~/.claude/settings.json` via `extraKnownMarketplaces`. All have `autoUpdate: true`.

| Marketplace | Source | Purpose |
|-------------|--------|---------|
| `ames-claude` | [`oliverames/ames-claude`](https://github.com/oliverames/ames-claude) | This marketplace (Oliver's personal) |
| `claude-plugins-official` | [`anthropics/claude-plugins-official`](https://github.com/anthropics/claude-plugins-official) | Anthropic's official curated plugin directory |
| `claude-community` | [`anthropics/claude-plugins-community`](https://github.com/anthropics/claude-plugins-community) | Anthropic-stewarded community plugins |
| `anthropic-agent-skills` | [`anthropics/skills`](https://github.com/anthropics/skills) | Anthropic's open-source Agent Skills repo |
| `knowledge-work-plugins` | [`anthropics/knowledge-work-plugins`](https://github.com/anthropics/knowledge-work-plugins) | Anthropic's knowledge-work-focused plugins |
| `apple-notes-mcp` | [`sweetrb/apple-notes-mcp`](https://github.com/sweetrb/apple-notes-mcp) | Apple Notes MCP integration |
| `axiom-marketplace` | [`CharlesWiltgen/Axiom`](https://github.com/CharlesWiltgen/Axiom) | Axiom plugin marketplace |
| `claudeskillz` | [`tsilva/claudeskillz`](https://github.com/tsilva/claudeskillz) | Community skill pack (output stylers, README authors) |
| `addy-agent-skills` | [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) | Addy Osmani's curated agent skills |
| `claude-code-workflows` | [`wshobson/agents`](https://github.com/wshobson/agents) | Workflow-oriented agent pack |
| `claude-code-plugins-plus` | [`jeremylongshore/claude-code-plugins`](https://github.com/jeremylongshore/claude-code-plugins) | Additional community plugins |
| `skill-codex` | [`skills-directory/skill-codex`](https://github.com/skills-directory/skill-codex) | Codex CLI interop skill |
| `a5c.ai` | [`a5c-ai/babysitter`](https://github.com/a5c-ai/babysitter) | Babysitter workflow orchestration |
| `karpathy-skills` | [`forrestchang/andrej-karpathy-skills`](https://github.com/forrestchang/andrej-karpathy-skills) | Karpathy-inspired coding guidelines |
| `swiftui-agent-skill` | [`twostraws/SwiftUI-Agent-Skill`](https://github.com/twostraws/SwiftUI-Agent-Skill) | Paul Hudson's SwiftUI Pro skill (replaced previously vendored copy) |

### Enabled plugins

Currently enabled in `~/.claude/settings.json` via `enabledPlugins`, grouped by marketplace:

**From `claude-plugins-official` (Anthropic official, 24 plugins):**
`frontend-design`, `superpowers`, `context7`, `github`, `feature-dev`, `playwright`, `skill-creator`, `ralph-loop`, `claude-md-management`, `typescript-lsp`, `security-guidance`, `commit-commands`, `claude-code-setup`, `pyright-lsp`, `explanatory-output-style`, `plugin-dev`, `learning-output-style`, `chrome-devtools-mcp`, `firecrawl`, `swift-lsp`, `remember`, `imessage`, `mcp-server-dev`, `gopls-lsp`

**From `ames-claude` (this repo, 6 plugins):**
`ames-standalone-skills`, `ames-preferred-mcps`, `ames-ynab`, `ames-lytho`, `ames-community-skills`, `ames-claude-only`

**From `knowledge-work-plugins` (3 plugins):**
`adspirer-ads-agent`, `pdf-viewer`, `searchfit-seo`

**From `claudeskillz` (4 plugins):**
`bash-output-styler`, `project-readme-author`, `project-spec-extractor`, `python-output-styler`

**From `anthropic-agent-skills` (2 plugins):**
`claude-api`, `document-skills`

**From `apple-notes-mcp` (1):** `apple-notes`
**From `addy-agent-skills` (1):** `agent-skills`
**From `skill-codex` (1):** `skill-codex`
**From `a5c.ai` (1):** `babysitter`
**From `karpathy-skills` (1):** `andrej-karpathy-skills`
**From `swiftui-agent-skill` (1):** `swiftui-pro`

### Environment variables

Required at Claude Code launch (non-credential values omitted for clarity; 1Password service account token intentionally not documented here):

| Variable | Used by | Purpose |
|----------|---------|---------|
| `YNAB_API_TOKEN` | `ames-ynab` | YNAB Personal Access Token, created at https://app.ynab.com/settings/developer |
| `LYTHO_CLIENT_ID` | `ames-lytho` | Lytho OAuth client ID |
| `LYTHO_CLIENT_SECRET` | `ames-lytho` | Lytho OAuth client secret |
| `LYTHO_TOKEN_URL` | `ames-lytho` | Lytho OAuth token endpoint |
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | Claude Code | Enable experimental agent teams feature (set to `1`) |
| `ENABLE_TOOL_SEARCH` | Claude Code | Enable deferred-tool search via `ToolSearch` (set to `1`) |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | Claude Code | Context auto-compact threshold percent (set to `85`) |
| `CLAUDE_CODE_NO_FLICKER` | Claude Code | Suppress terminal flicker during rendering (set to `1`) |
| `BASH_MAX_OUTPUT_LENGTH` | Claude Code | Max Bash output length in bytes (set to `200000`) |

Additional plugin-specific credentials (for `ames-preferred-mcps` servers and some third-party plugins) are resolved at runtime through the `1password` MCP rather than exported environment variables.

### Claude Code settings overrides

Non-default `~/.claude/settings.json` values that shape Oliver's experience:

| Setting | Value | Effect |
|---------|-------|--------|
| `cleanupPeriodDays` | `45` | Longer retention for conversation history |
| `outputStyle` | `Explanatory` | Use the explanatory output style (educational insights) |
| `alwaysThinkingEnabled` | `true` | Extended thinking on for every turn |
| `effortLevel` | `xhigh` | Maximum effort tier |
| `viewMode` | `focus` | Focused UI mode |
| `autoUpdatesChannel` | `latest` | Subscribe to bleeding-edge Claude Code releases |
| `autoDreamEnabled` | `true` | Background reflection between turns |
| `voiceEnabled` | `true` | Voice I/O on |
| `remoteControlAtStartup` | `true` | Accept remote-control connections at launch |
| `teammateMode` | `auto` | Auto-spawn teammate agents when the workflow calls for it |
| `skipAutoPermissionPrompt` | `true` | Suppress repeat permission prompts |
| `skipDangerousModePermissionPrompt` | `true` | Suppress dangerous-mode warning |
| `feedbackSurveyRate` | `0` | Disable feedback surveys |
| `permissions.defaultMode` | `auto` | Auto-allow tools on the allowlist |
| `enableAllProjectMcpServers` | `true` | Project-level MCPs load automatically |

Hooks wired up: a `PostToolUse` hook for `Bash` commits (logs a success line after `git commit`), and a `PostToolUse` hook for `Edit|Write` that runs the `validate-skill` shell script. Status line is customized via `~/.claude/statusline-command.sh`.

## Related

| Thing | Role |
|-------|------|
| `oliverames/dotfiles` | Shell config, install script, system-wide hooks |
| `oliverames/scripts` | CLI tools including sync utilities |
| `oliverames/claude-code-backup` | Mirror of `~/.claude/` with secrets redacted |
| [openai/plugins](https://github.com/openai/plugins) | Upstream for `ames-claude-only` converted skills |
| [twostraws/SwiftUI-Agent-Skill](https://github.com/twostraws/SwiftUI-Agent-Skill) | Recommended companion marketplace for SwiftUI Pro |
| [blader/humanizer](https://github.com/blader/humanizer) | Upstream for `humanizer` in `ames-community-skills` |

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
