<h1 align="center">ames-claude</h1>

<p align="center">
  <strong>Personal plugin marketplace for Claude Code, with experimental Codex support</strong>
</p>

<p align="center">
  <code>6 plugins</code> &bull;
  <code>47 skills</code> &bull;
  <code>13 MCP servers</code> &bull;
  <code>dual-host</code>
</p>

<p align="center">
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-f5a542?style=flat-square" alt="License">
  </a>
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
    },
    "ames-connectors": {
      "source": { "source": "github", "repo": "oliverames/ames-connectors" },
      "autoUpdate": true
    }
  },
  "enabledPlugins": {
    "ames-standalone-skills@ames-claude": true,
    "ames-dev-mcps@ames-claude": true,
    "ames-general-mcps@ames-claude": true,
    "ames-ynab@ames-connectors": true,
    "ames-community-skills@ames-claude": true,
    "build-ios-apps-codex@ames-claude": true,
    "build-macos-apps-codex@ames-claude": true
  }
}
```

Restart Claude Code. The marketplace registers, plugins install, and `autoUpdate` keeps them current on each launch.

**Interactive install.** Or run:

```
/plugin marketplace add oliverames/ames-claude
/plugin marketplace add oliverames/ames-connectors
/plugin install ames-standalone-skills@ames-claude
/plugin install ames-dev-mcps@ames-claude
/plugin install ames-general-mcps@ames-claude
/plugin install ames-ynab@ames-connectors
/plugin install ames-community-skills@ames-claude
/plugin install build-ios-apps-codex@ames-claude
/plugin install build-macos-apps-codex@ames-claude
```

### Codex (experimental)

```
codex plugin marketplace add oliverames/ames-claude
codex plugin marketplace upgrade ames-claude
```

Then install plugins through Codex's plugin UI or CLI. `build-ios-apps-codex` and `build-macos-apps-codex` are intentionally absent from the Codex side (see below).

> **Heads-up:** Codex's marketplace commands are still stabilizing. Verify exact syntax with `codex plugin marketplace --help` before scripting. File an issue if any Codex manifest in this repo falls out of spec.

## Plugins

Six plugins ship in this marketplace:

Custom first-party MCP connectors moved to [ames-connectors](https://github.com/oliverames/ames-connectors), which now owns `ames-ynab` and `ames-lytho`.

| Plugin | Hosts | Version | Summary |
|--------|-------|---------|---------|
| [`ames-standalone-skills`](plugins/ames-standalone-skills/) | Claude + Codex | 3.5.3 | Oliver's original skill pack (29 skills) |
| [`ames-dev-mcps`](plugins/ames-dev-mcps/) | Claude + Codex | 1.0.0 | 6 development-focused MCP servers for iOS/macOS workflows |
| [`ames-general-mcps`](plugins/ames-general-mcps/) | Claude + Codex | 3.0.0 | 7 day-to-day general-purpose MCP servers |
| [`ames-community-skills`](plugins/ames-community-skills/) | Claude + Codex | 2.0.1 | Third-party skills without upstream marketplaces |
| [`build-ios-apps-codex`](plugins/build-ios-apps-codex/) | **Claude only** | 1.0.1 | 6 iOS dev skills converted from OpenAI's Codex plugin |
| [`build-macos-apps-codex`](plugins/build-macos-apps-codex/) | **Claude only** | 1.0.1 | 11 macOS dev skills + 3 commands converted from OpenAI's Codex plugin |

### `ames-standalone-skills`

Oliver's original Claude Code skills covering writing, development, automation, finance, and Apple platform work. 28 skills organized by theme (see [Skills catalog](#skills-catalog)).

### `ames-dev-mcps`

Development-focused MCP servers for iOS and macOS workflows:

| MCP | Purpose |
|-----|---------|
| `apple-docs` | Apple Developer documentation search and WWDC lookup |
| `apple-notifier` | Native macOS notifications, speech, screen capture |
| `macos-automator` | AppleScript and JXA via osascript |
| `SimGenie` | iOS Simulator helpers |
| `sosumi` | Apple documentation fetcher |
| `XcodeBuildMCP` | Xcode build/run/test for simulators and devices |

### `ames-general-mcps`

Day-to-day general-purpose MCP servers (formerly `ames-preferred-mcps`):

| MCP | Purpose |
|-----|---------|
| `drafts` | Drafts.app integration for note capture |
| `excel` | Excel workbook manipulation |
| `google-workspace` | Gmail, Calendar, Drive, Docs, Sheets, Tasks, Meet |
| `iMCP` | Apple event bridge (calendars, reminders) |
| `markitdown` | Convert files to Markdown |
| `pandoc` | Universal document conversion |
| `peekaboo` | macOS UI automation and screen capture |

Some servers depend on locally installed apps or additional credentials.

### `ames-community-skills`

A wrapper for third-party skills that ship as bare `SKILL.md` files with no upstream marketplace of their own. Currently one skill:

- [`humanizer`](plugins/ames-community-skills/skills/humanizer/) — Remove signs of AI-generated writing from text. Originally by [blader](https://github.com/blader/humanizer).

When an upstream author publishes their own marketplace (as [twostraws](https://github.com/twostraws/SwiftUI-Agent-Skill) did with SwiftUI Pro), that upstream is preferred and the skill leaves this plugin.

### `build-ios-apps-codex`

Claude Code only. 6 iOS development skills converted from OpenAI's [`build-ios-apps`](https://github.com/openai/plugins/tree/main/plugins/build-ios-apps) Codex plugin (MIT): `ios-app-intents`, `ios-debugger-agent`, `swiftui-liquid-glass`, `swiftui-performance-audit`, `swiftui-ui-patterns`, `swiftui-view-refactor`. Each lives at [`plugins/build-ios-apps-codex/skills/<name>/`](plugins/build-ios-apps-codex/skills/). Run [`./plugins/build-ios-apps-codex/update.sh`](plugins/build-ios-apps-codex/update.sh) to resync from the local Codex plugin cache.

### `build-macos-apps-codex`

Claude Code only. 11 macOS development skills plus 3 commands converted from OpenAI's [`build-macos-apps`](https://github.com/openai/plugins/tree/main/plugins/build-macos-apps) Codex plugin (MIT): `appkit-interop`, `build-run-debug`, `liquid-glass`, `packaging-notarization`, `signing-entitlements`, `swiftpm-macos`, `swiftui-patterns`, `telemetry`, `test-triage`, `view-refactor`, `window-management`. Commands: `build-and-run-macos-app`, `fix-codesign-error`, `test-macos-app`. Run [`./plugins/build-macos-apps-codex/update.sh`](plugins/build-macos-apps-codex/update.sh) to resync from the local Codex plugin cache.

Both plugins originated in [openai/plugins](https://github.com/openai/plugins) and were adapted for Claude Code. They are omitted from the Codex marketplace manifest by design, since installing them in Codex would re-import already-diverged skills.

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
- [`bcbs-wrap-up`](plugins/ames-standalone-skills/skills/bcbs-wrap-up/) — End-of-session wrap-up, verifies Jira-tracked action items

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

Plus 6 skills in `build-ios-apps-codex`, 11 skills (+ 3 commands) in `build-macos-apps-codex`, and 1 in `ames-community-skills` (humanizer).

## MCP servers catalog

13 MCP servers split across two plugins:

| Plugin | Server count | Details |
|--------|--------------|---------|
| `ames-dev-mcps` | 6 development-focused servers | See [plugin table](#ames-dev-mcps) above |
| `ames-general-mcps` | 7 day-to-day servers | See [plugin table](#ames-general-mcps) above |

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
        ├── .codex-plugin/mcp.json         # Generated Codex MCP wrapper (if applicable)
        ├── .mcp.json                      # Claude Code MCP config, source for Codex wrapper
        └── skills/<skill-name>/SKILL.md   # Skill files (portable across hosts)
```

| Host | Marketplace manifest | Per-plugin manifest | Plugins |
|------|----------------------|---------------------|---------|
| Claude Code | `.claude-plugin/marketplace.json` | `.claude-plugin/plugin.json` | 6 |
| Codex (experimental) | `.agents/plugins/marketplace.json` | `.codex-plugin/plugin.json` | 4 (excludes `build-ios-apps-codex`, `build-macos-apps-codex`, and first-party connectors now in `ames-connectors`) |

### What crosses the boundary

- **Skill content** (`SKILL.md` and bundled resources) is portable by spec
- **MCP server inventory** is shared; Claude Code keeps the root `.mcp.json`, while `./sync` generates Codex's `.codex-plugin/mcp.json` wrapper
- **Plugin content** structurally matches on both sides

### What does not

- **Plugin and marketplace manifests** differ in location and schema; they live side by side in the same repo
- **Claude Code's marketplace implementation** is not reshaped to satisfy Codex. Codex support stays additive and isolated in `.agents/` and `.codex-plugin/`
- **`build-ios-apps-codex` and `build-macos-apps-codex`** are Claude Code only by design (converted-from-Codex skills can't round-trip cleanly, since they already exist upstream in `openai/plugins`)
- **Third-party marketplaces that publish only one manifest format** can't be rewrapped by ames-claude. Install those from upstream wherever the author supports

## Configuration

Per-plugin environment requirements:

| Plugin | Variable | Required | Purpose |
|--------|----------|----------|---------|
| `ames-dev-mcps` | varies | varies | Some servers require their own credentials or apps |
| `ames-general-mcps` | varies | varies | Some servers require their own credentials or apps |

Credentials are never stored in the repo. MCPs reference environment variables at runtime, with secrets resolved from the user's local configuration.

## Versioning

Each plugin's version lives in three places that must stay in sync:

1. `plugins/<name>/.claude-plugin/plugin.json` — Claude-side authoritative
2. `plugins/<name>/.codex-plugin/plugin.json` — Codex mirror (must match 1)
3. Root `.claude-plugin/marketplace.json` — per-plugin `version` (must match 1)

The marketplace itself has a separate version at `.claude-plugin/marketplace.json`'s top-level `metadata.version`, currently `3.5.0`.

Workflow scripts at the repo root (`sync`, `bump-and-sync`, `codex-doctor`) help keep these aligned after content changes. `./sync` propagates `version` and shared metadata from `.claude-plugin/plugin.json` into the matching `.codex-plugin/plugin.json`, threads enriched metadata fields into the generated marketplace entry, and refreshes Codex MCP wrappers. Use `./sync --check-codex` for generated-file and cache validation, and `./codex-doctor --live` when you also want live `codex mcp list` verification. Always run one of those before committing version-bearing changes.

## Development

### Adding a new skill

1. Create `plugins/ames-standalone-skills/skills/<skill-name>/SKILL.md` with YAML frontmatter (`name`, `description`)
2. Add supporting files (references, scripts) in subdirectories as needed
3. Run `bump-and-sync` from the repo root
4. Commit and push; Claude Code users with `autoUpdate` pick it up on next launch

### Adding a new plugin

1. Create `plugins/<plugin-name>/.claude-plugin/plugin.json` with `name`, `version`, `description`, `author`
2. For dual-host support, also create `plugins/<plugin-name>/.codex-plugin/plugin.json` mirroring the Claude manifest with Codex-specific `interface` and `category` fields
3. Run `./sync` to regenerate `.claude-plugin/marketplace.json` and `.agents/plugins/marketplace.json`
4. Add content (skills, commands, MCPs) at the plugin root per spec
5. Run `./codex-doctor --live` for Codex-facing plugins, then `bump-and-sync` and commit

## My Claude Code configuration

A complete snapshot of `~/.claude/settings.json`, documented here so this repo doubles as a rebuilding reference. **Kept in sync by the `wrap-up` skill**: any session that changes `~/.claude/settings.json` or installs or removes a plugin also updates the tables below and commits the result. If this machine died tomorrow, these tables plus a fresh `~/.claude/settings.json` would reconstruct the environment.

### Installed marketplaces (16 total)

15 marketplaces declared in `extraKnownMarketplaces` (all with `autoUpdate: true`), plus `claude-plugins-official` as the built-in default.

| Marketplace | Source | Why it's installed |
|-------------|--------|--------------------|
| `claude-plugins-official` | [`anthropics/claude-plugins-official`](https://github.com/anthropics/claude-plugins-official) | Built-in default. Anthropic's official curated plugin directory |
| `ames-claude` | [`oliverames/ames-claude`](https://github.com/oliverames/ames-claude) | This repo. Oliver's personal skill and workflow marketplace |
| `ames-connectors` | [`oliverames/ames-connectors`](https://github.com/oliverames/ames-connectors) | Oliver's first-party MCP connector marketplace |
| `claude-community` | [`anthropics/claude-plugins-community`](https://github.com/anthropics/claude-plugins-community) | Anthropic-stewarded community plugins |
| `anthropic-agent-skills` | [`anthropics/skills`](https://github.com/anthropics/skills) | Anthropic's open-source Agent Skills (Claude API, document skills) |
| `knowledge-work-plugins` | [`anthropics/knowledge-work-plugins`](https://github.com/anthropics/knowledge-work-plugins) | Anthropic's knowledge-work plugins (PDF viewer, SEO, ads) |
| `apple-notes-mcp` | [`sweetrb/apple-notes-mcp`](https://github.com/sweetrb/apple-notes-mcp) | Apple Notes MCP integration |
| `axiom-marketplace` | [`CharlesWiltgen/Axiom`](https://github.com/CharlesWiltgen/Axiom) | Axiom plugin marketplace (registered but no plugins enabled) |
| `claudeskillz` | [`tsilva/claudeskillz`](https://github.com/tsilva/claudeskillz) | Output stylers and README authoring skills |
| `addy-agent-skills` | [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) | Addy Osmani's curated agent skills |
| `claude-code-workflows` | [`wshobson/agents`](https://github.com/wshobson/agents) | Workflow-oriented agent pack (registered but no plugins enabled) |
| `claude-code-plugins-plus` | [`jeremylongshore/claude-code-plugins`](https://github.com/jeremylongshore/claude-code-plugins) | Additional community plugins (registered but no plugins enabled) |
| `skill-codex` | [`skills-directory/skill-codex`](https://github.com/skills-directory/skill-codex) | Codex CLI interop skill |
| `a5c.ai` | [`a5c-ai/babysitter`](https://github.com/a5c-ai/babysitter) | Babysitter workflow orchestration |
| `karpathy-skills` | [`forrestchang/andrej-karpathy-skills`](https://github.com/forrestchang/andrej-karpathy-skills) | Karpathy-inspired coding guidelines |
| `swiftui-agent-skill` | [`twostraws/SwiftUI-Agent-Skill`](https://github.com/twostraws/SwiftUI-Agent-Skill) | Paul Hudson's SwiftUI Pro (replaced previously vendored copy) |

### Enabled plugins (43 total)

Grouped by source marketplace. Each `plugin@marketplace` key in `enabledPlugins` is listed below with its purpose.

**`claude-plugins-official` (24 plugins):**

| Plugin | Purpose |
|--------|---------|
| `frontend-design` | Production-quality UI component generation |
| `superpowers` | Core skill framework (brainstorming, debugging, TDD, code review, git worktrees, etc.) |
| `context7` | Real-time library documentation lookup |
| `github` | GitHub issue, PR, and release management |
| `feature-dev` | Guided feature development workflow |
| `playwright` | Browser automation via Playwright |
| `skill-creator` | Scaffold and validate new Agent Skills |
| `ralph-loop` | Loop-based iterative workflow |
| `claude-md-management` | Audit and maintain `CLAUDE.md` files |
| `typescript-lsp` | TypeScript language server |
| `security-guidance` | Security review and hardening prompts |
| `commit-commands` | Conventional git commit workflow |
| `claude-code-setup` | Recommend Claude Code automations for a codebase |
| `pyright-lsp` | Python language server |
| `explanatory-output-style` | Sets the "Explanatory" output style |
| `plugin-dev` | Plugin scaffolding and development tools |
| `learning-output-style` | Learning-oriented output style option |
| `chrome-devtools-mcp` | Chrome DevTools Protocol integration |
| `firecrawl` | Web search, scraping, and skill generation from URLs |
| `swift-lsp` | Swift language server |
| `remember` | Session state persistence |
| `imessage` | iMessage send/receive integration |
| `mcp-server-dev` | Build MCP servers and apps |
| `gopls-lsp` | Go language server |

**`ames-claude` (6 of 6 available enabled):** `ames-standalone-skills`, `ames-dev-mcps`, `ames-general-mcps`, `ames-community-skills`, `build-ios-apps-codex`, `build-macos-apps-codex`. All plugins from this marketplace are currently enabled at the user level.

**`ames-connectors` (1 of 2 available enabled):** `ames-ynab`. `ames-lytho` is available in the connector marketplace but not currently enabled at the user level.

**`knowledge-work-plugins` (3):** `adspirer-ads-agent` (ad campaign analytics), `pdf-viewer` (interactive PDF), `searchfit-seo` (SEO audits and content strategy)

**`claudeskillz` (4):** `bash-output-styler`, `python-output-styler`, `project-readme-author`, `project-spec-extractor`

**`anthropic-agent-skills` (1):** `document-skills` (pptx, docx, xlsx, pdf, frontend-design, mcp-builder)

**`apple-notes-mcp` (1):** `apple-notes` — Apple Notes MCP
**`addy-agent-skills` (1):** `agent-skills` — Addy Osmani's agent skills pack
**`skill-codex` (1):** `skill-codex` — Codex CLI interop for code analysis and refactoring
**`a5c.ai` (1):** `babysitter` — Workflow orchestration via `@babysitter`
**`karpathy-skills` (1):** `andrej-karpathy-skills` — Anti-overengineering coding guidelines
**`swiftui-agent-skill` (1):** `swiftui-pro` — Paul Hudson's SwiftUI review skill

### Environment variables

Defined in `env` block of `~/.claude/settings.json` and at session launch. `OP_SERVICE_ACCOUNT_TOKEN` is intentionally omitted from this record.

**Claude Code runtime:**

| Variable | Value | Why |
|----------|-------|-----|
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | `1` | Opt into experimental agent teams feature for multi-agent workflows |
| `ENABLE_TOOL_SEARCH` | `1` | Enable deferred-tool search via the `ToolSearch` tool, keeping the initial tool list short |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | `85` | Auto-compact context at 85% of window rather than the default 95%, for more headroom before compression |
| `CLAUDE_CODE_NO_FLICKER` | `1` | Suppress terminal redraw flicker during streaming output |
| `BASH_MAX_OUTPUT_LENGTH` | `200000` | Raise the Bash output truncation limit to 200KB for long-running commands (tests, builds) |

**Plugin credentials (set in shell, not in settings.json):**

Connector-specific credentials now live with [ames-connectors](https://github.com/oliverames/ames-connectors). Other plugin-specific credentials (for servers in `ames-dev-mcps`, `ames-general-mcps`, and some third-party plugins) are resolved at runtime through local configuration rather than stored in the repo.

### Permissions

`permissions.defaultMode` is `auto` (auto-allow tools on the allowlist without prompting). The allowlist covers core file I/O, search, language tooling, skills, agents, and teamwork primitives so those never interrupt flow:

`Read`, `Edit`, `Write`, `Glob`, `Grep`, `NotebookEdit`, `TaskCreate`, `TaskUpdate`, `TaskList`, `TaskGet`, `TaskStop`, `LSP`, `Agent`, `Skill`, `ToolSearch`, `ListMcpResourcesTool`, `ReadMcpResourceTool`, `EnterWorktree`, `TeamCreate`, `TeamDelete`, `SendMessage`

`deny` is empty. Tools outside the allowlist still require explicit approval. Two additional flags suppress specific prompts: `skipAutoPermissionPrompt: true` (no repeated prompts for the same tool) and `skipDangerousModePermissionPrompt: true` (no warning when entering dangerous mode).

### Hooks

Two `PostToolUse` hooks, both in `hooks.PostToolUse`:

| Matcher | Command | Effect |
|---------|---------|--------|
| `Bash` | Python one-liner that checks if the bash command contained `git commit`, and if so prints `✅ Committed` and the latest commit summary | Lightweight confirmation that a commit actually landed, useful during multi-commit sessions |
| `Edit\|Write` | `bash ~/Library/Mobile Documents/com~apple~CloudDocs/Developer/Scripts/validate-skill` | Runs the `validate-skill` shell script after any file edit or write, to catch skill authoring errors (malformed frontmatter, broken references) at write time |

### Status line

`statusLine.command` runs `bash ~/.claude/statusline-command.sh`, which renders a custom status line.

### UI and agent behavior

| Setting | Value | Why |
|---------|-------|-----|
| `model` | `sonnet` | Main-thread model. The `sonnet` family alias auto-resolves to the latest Sonnet (currently 4.6); keeps me on the best cost-per-capability tier without manual migration when a new Sonnet ships |
| `advisorModel` | `opus` | Family alias for the `advisor` tool; auto-resolves to the latest Opus (currently 4.7). The advisor's job is to be the *stronger* reviewer, so it stays on Opus even when the main thread is Sonnet |
| `outputStyle` | `Explanatory` | Default to the explanatory style, which surfaces educational insights alongside changes. Useful when the point of a session is learning as much as shipping |
| `alwaysThinkingEnabled` | `true` | Extended thinking on for every turn, not just complex ones. Modern Claude models use the thinking budget adaptively, so leaving it on is almost free on easy turns |
| `effortLevel` | `medium` | Balanced tier. Applies to both main-thread and advisor calls (there is no separate advisor effort key). Lower tiers ship faster; higher tiers burn more tokens verifying. Medium is the default compromise |
| `autoDreamEnabled` | `true` | Background reflection between turns (experimental) |
| `teammateMode` | `auto` | Auto-spawn teammate agents when the workflow obviously benefits from parallelism |
| `viewMode` | `focus` | Focused UI mode: hide non-essential chrome |
| `voiceEnabled` | `true` | Voice I/O on for spoken prompts and replies |
| `remoteControlAtStartup` | `true` | Accept remote-control connections from other clients at launch |

### Miscellaneous

| Setting | Value | Why |
|---------|-------|-----|
| `cleanupPeriodDays` | `45` | Keep conversation history for 45 days instead of the default, since some projects span weeks |
| `autoUpdatesChannel` | `latest` | Track the bleeding-edge Claude Code release channel |
| `feedbackSurveyRate` | `0` | Disable in-product feedback surveys |
| `enableAllProjectMcpServers` | `true` | Project-level MCP servers from `.mcp.json` load automatically without per-project opt-in |

### Keeping this section current

The `wrap-up` skill runs a config-drift check at end of session. If any of these change during a session, the wrap-up flow updates this section and commits the change:

- New plugin enabled or disabled in `~/.claude/settings.json`
- New marketplace added to `extraKnownMarketplaces`
- New env variable added to `env`
- Any top-level settings value changes
- Any hook added, removed, or modified

This is what makes the configuration record trustworthy: it doesn't go stale because the wrap-up ritual won't let it.

## Related

| Thing | Role |
|-------|------|
| `oliverames/dotfiles` | Shell config, install script, system-wide hooks |
| `oliverames/scripts` | CLI tools including sync utilities |
| `oliverames/claude-code-backup` | Mirror of `~/.claude/` with secrets redacted |
| [openai/plugins](https://github.com/openai/plugins) | Upstream for `build-ios-apps-codex` and `build-macos-apps-codex` converted skills |
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
