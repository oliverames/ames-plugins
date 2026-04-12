# Claude Code Filesystem Map

Reference for `/Users/oliverames/.claude/` — the Claude Code user data directory.

---

## 1. Directory Tree

```
/Users/oliverames/.claude/
├── settings.json                     — Global user config (permissions, hooks, plugins, env)
├── CLAUDE.md                         — Global user instructions injected into every session
├── statusline-command.sh             — Shell script providing the status bar content
│
├── hooks/                            — Node.js hook scripts (run on tool use events)
│   ├── auto-stage.js                 — PostToolUse: git-stages files after Edit/Write
│   ├── block-dangerous-commands.js   — PreToolUse: blocks destructive Bash patterns
│   ├── notify-brrr.js                — Stop/Notification: sends push notifications via brrr.now
│   └── protect-secrets.js            — PreToolUse: blocks access to sensitive files
│
├── hooks-logs/                       — Runtime logs written by hook scripts (auto-created)
│
├── plugins/
│   ├── installed_plugins.json        — v2 registry of all installed plugins
│   ├── cache/                        — Extracted plugin content, keyed by source/name/version
│   │   ├── claude-plugins-official/  — Official Anthropic plugins
│   │   ├── ames-claude/              — Personal plugins from ames-claude repo
│   │   ├── apple-hig-skills/         — Apple HIG skills plugin
│   │   └── anthropic-agent-skills/   — Anthropic agent skills
│   └── .install-manifests/           — Per-plugin install manifests (file hashes for integrity)
│
├── skills/                           — Standalone skill directory (currently empty)
│   └── (empty — all skills are delivered via the ames-standalone-skills plugin)
│
├── projects/                         — Per-project data, keyed by URL-encoded working directory
│   └── <encoded-path>/               — One directory per project (see Section 6)
│       ├── memory/                   — Project-specific memory files (MEMORY.md, etc.)
│       └── <session-uuid>/           — One directory per conversation session
│           └── subagents/            — Subagent JSONL conversation logs
│               └── agent-<id>.jsonl  — Individual subagent message stream
│
├── todos/                            — Per-session todo/task lists
│   └── <session-uuid>-agent-<uuid>.json
│
├── telemetry/                        — Failed telemetry event backfill queue
│   └── 1p_failed_events.<session>.<id>.json
│
└── shell-snapshots/                  — Saved shell environment snapshots
    └── snapshot-zsh-<timestamp>-<id>.sh
```

---

## 2. settings.json Schema

Full path: `/Users/oliverames/.claude/settings.json`

All fields are top-level keys in a JSON object.

| Field | Type | Description |
|-------|------|-------------|
| `env` | object | **Contains secrets — never read or log key names or values.** Runtime environment variables injected into every Claude Code session (API keys, tokens, feature flags). |
| `permissions` | object | Tool access control — see sub-fields below. |
| `permissions.allow` | string[] | Allowlist of tool patterns. Supports wildcards: `"Bash(git *)"`, `"mcp__apple-docs__*"`. |
| `permissions.deny` | string[] | Denylist overrides — takes precedence over allow. E.g., `"Read(./.env)"`. |
| `permissions.defaultMode` | string | `"dontAsk"` — skips permission prompts for allowed tools. Other values: `"ask"`, `"auto"`. |
| `hooks` | object | Event-based hook configuration — see sub-fields below. |
| `hooks.PreToolUse` | array | Hook entries run before a tool executes. Each entry: `{ matcher, hooks: [{ type, command, timeout?, async? }] }`. |
| `hooks.PostToolUse` | array | Hook entries run after a tool completes. Same structure as PreToolUse. |
| `hooks.Notification` | array | Hook entries run on notification events (e.g., `"permission_prompt"`). |
| `hooks.Stop` | array | Hook entries run when Claude finishes a response. |
| `enabledPlugins` | object | Map of `"<name>@<source>": true/false`. Controls which installed plugins are active. |
| `enableAllProjectMcpServers` | boolean | When `true`, automatically enables MCP servers defined in project-level configs. |
| `statusLine` | object | `{ type: "command", command: "<shell command>" }` — shell command whose stdout appears in the Claude Code status bar. |
| `alwaysThinkingEnabled` | boolean | When `true`, extended thinking is always on. |
| `autoUpdatesChannel` | string | Which release channel to auto-update from. `"latest"` is the stable channel. |
| `skipDangerousModePermissionPrompt` | boolean | When `true`, suppresses the dangerous-mode confirmation dialog. |
| `remoteControlAtStartup` | boolean | When `true`, enables remote control / orchestration features on launch. |
| `cleanupPeriodDays` | number | Number of days after which old session data is eligible for cleanup. |

### Hook entry schema

```json
{
  "matcher": "Bash",
  "hooks": [
    {
      "type": "command",
      "command": "node ~/.claude/hooks/block-dangerous-commands.js",
      "timeout": 10,
      "async": false
    }
  ]
}
```

- `matcher`: tool name or `|`-separated list (e.g., `"Edit|Write"`, `"AskUserQuestion"`)
- `type`: always `"command"` currently
- `command`: shell command string (runs in user's shell environment)
- `timeout`: optional seconds before the hook is killed (default varies)
- `async`: optional boolean — when `true`, hook runs in background without blocking tool execution

---

## 3. installed_plugins.json Schema

Full path: `/Users/oliverames/.claude/plugins/installed_plugins.json`

### Top-level structure

```json
{
  "version": 2,
  "plugins": {
    "<name>@<source>": [ <InstallRecord>, ... ]
  }
}
```

- `version`: always `2` for the current format
- `plugins`: object keyed by `"<plugin-name>@<source-id>"` — each value is an array (supports multiple installed versions, though typically one entry)

### InstallRecord schema

```json
{
  "scope": "user",
  "installPath": "/Users/oliverames/.claude/plugins/cache/claude-plugins-official/github/6b70f99f769f",
  "version": "6b70f99f769f",
  "installedAt": "2026-03-04T01:45:36.436Z",
  "lastUpdated": "2026-03-18T00:03:36.316Z",
  "gitCommitSha": "205b6e0b30366a969412d9aab7b99bea99d58db1"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `scope` | string | Always `"user"` for user-level installs (project-level scope is also possible). |
| `installPath` | string | Absolute path to the extracted plugin content directory. |
| `version` | string | Semver string (e.g., `"1.0.3"`) or 12-character git commit hash (e.g., `"6b70f99f769f"`). |
| `installedAt` | string | ISO 8601 timestamp of initial install. |
| `lastUpdated` | string | ISO 8601 timestamp of most recent update. |
| `gitCommitSha` | string | Full 40-character SHA of the git commit the plugin was built from. Absent for locally-installed plugins (e.g., `ames-claude`). |

### Version formats

- **Semver** (`"1.0.3"`): used by plugins that explicitly declare a version in `plugin.json`
- **Short commit hash** (`"6b70f99f769f"`): used by registry-sourced plugins that don't pin a version — represents the 12-char prefix of the git commit SHA

---

## 4. Plugin Cache Structure

Base path: `/Users/oliverames/.claude/plugins/cache/`

Layout:
```
/Users/oliverames/.claude/plugins/cache/
└── <source>/
    └── <plugin-name>/
        └── <version>/
            ├── .claude-plugin/
            │   ├── plugin.json        — Plugin metadata (name, version, description, author, keywords)
            │   └── marketplace.json   — Marketplace listing metadata (optional)
            ├── commands/
            │   └── <command-name>.md  — Slash command definitions with frontmatter
            ├── skills/
            │   └── <skill-name>/
            │       └── SKILL.md       — Skill definition with frontmatter
            ├── agents/
            │   └── <agent-name>.md    — Agent definitions (optional)
            └── README.md              — Human-readable plugin docs (optional)
```

### Known source identifiers

| Source ID | Origin |
|-----------|--------|
| `claude-plugins-official` | Official Anthropic plugin registry |
| `ames-claude` | Personal plugins from `github.com/oliverames/ames-claude` |
| `apple-hig-skills` | Apple HIG skills (third-party registry) |
| `anthropic-agent-skills` | Anthropic agent skills registry |

The source ID in the cache path always matches the `@<source>` suffix in the plugin key in `installed_plugins.json` and `enabledPlugins`.

---

## 5. Install Manifests

Base path: `/Users/oliverames/.claude/plugins/.install-manifests/`

Filename pattern: `<plugin-name>@<source>.json`

Example: `/Users/oliverames/.claude/plugins/.install-manifests/firecrawl@claude-plugins-official.json`

### Manifest schema

```json
{
  "pluginId": "firecrawl@claude-plugins-official",
  "createdAt": "2026-02-28T19:21:18.666Z",
  "files": {
    "relative/path/to/file": "<sha256-hex>",
    "commands/skill-gen.md": "9f80eed0cfc820ae4a0a08255be1f3f17ce0553b1884ca43c729bad85ee04442",
    "skills/firecrawl-cli/SKILL.md": "766678660c07a5b116525e545ef882089d7bf56e801c04f50e43913681a337d9"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `pluginId` | string | Full plugin key (`"<name>@<source>"`). |
| `createdAt` | string | ISO 8601 timestamp of when the manifest was created (initial install). |
| `files` | object | Map of relative file path → SHA-256 hex digest. Covers all tracked plugin files including `.git/` internals. Used for integrity checking and detecting modifications. |

**Purpose:** Install manifests allow Claude Code to detect if a plugin's cached files have been tampered with or corrupted since installation. They are also used during updates to determine which files changed.

---

## 6. Projects Directory

Base path: `/Users/oliverames/.claude/projects/`

### Path encoding convention

Each project directory is named by transforming the absolute working directory path:

1. Take the absolute path, e.g.: `/Users/oliverames/Library/Mobile Documents/com~apple~CloudDocs/Developer/bcbsvt`
2. Replace `/`, spaces, and `~` with `-`
3. Strip the leading `-` to get the directory name

Result: `-Users-oliverames-Library-Mobile-Documents-com-apple-CloudDocs-Developer-bcbsvt`

**Key rules:**
- Forward slashes `/` become hyphens `-`
- The leading `/` becomes a leading `-` (then the leading `-` is kept — the name starts with `-`)
- Spaces in path components become hyphens (e.g., `Mobile Documents` → `Mobile-Documents`)
- Tildes `~` also become hyphens (e.g., `com~apple~CloudDocs` → `com-apple-CloudDocs`)
- The encoding replaces `/`, spaces, and `~` with `-` — not URL percent-encoding

**Decoding:** To reconstruct the original path, prepend `/` and replace all `-` that are path separators with `/`. In practice, look at the encoded string and recognize macOS path components.

### Example encoded names

| Encoded directory name | Original path |
|------------------------|---------------|
| `-Users-oliverames` | `/Users/oliverames` |
| `-Users-oliverames-Library-Mobile-Documents-com-apple-CloudDocs-Developer-bcbsvt` | `/Users/oliverames/Library/Mobile Documents/com~apple~CloudDocs/Developer/bcbsvt` |
| `-Users-oliverames-conductor-workspaces-bcbsvt-kingston` | `/Users/oliverames/conductor-workspaces/bcbsvt-kingston` |

### Per-project structure

```
/Users/oliverames/.claude/projects/<encoded-path>/
├── memory/                           — Persistent memory files for this project
│   └── MEMORY.md                     — Main project memory (free-form markdown)
│   └── <other-notes>.md              — Additional named memory files
└── <session-uuid>/                   — One directory per conversation session (UUID v4)
    └── subagents/                    — Subagent message logs
        └── agent-<id>.jsonl          — JSONL stream of subagent messages
```

- `memory/` persists across sessions — contents are injected as project context
- Session UUIDs are random v4 UUIDs assigned when a conversation starts
- Subagent IDs use a shorter hex prefix format: `agent-<7-hex>` for full agents, `agent-acompact-<6-hex>` for compact agents

---

## 7. Hooks Directory

Full path: `/Users/oliverames/.claude/hooks/`

All hooks are Node.js scripts executed by Claude Code's hook runner. They read a JSON payload from stdin describing the triggering event and write a JSON response to stdout.

| Script | Trigger | Purpose |
|--------|---------|---------|
| `block-dangerous-commands.js` | PreToolUse: Bash | Inspects Bash commands against a blocklist of dangerous patterns (e.g., `rm -rf /`, force-push to main, credential-writing commands) and exits with an error to abort execution. |
| `protect-secrets.js` | PreToolUse: Read, Edit, Write, Bash | Blocks operations targeting sensitive files and directories (SSH keys, `.env` files, credential stores). Classifies threats by severity level. |
| `auto-stage.js` | PostToolUse: Edit, Write | Runs `git add <file>` on any file that Claude Code just modified, so `git status` always reflects exactly what was changed in the session. |
| `notify-brrr.js` | Stop, Notification (permission_prompt), PreToolUse (AskUserQuestion) | Sends push notifications to the user's device via the brrr.now service. Strips markdown, checks idle time to avoid notification spam, and sends structured JSON payloads with context about the event. |

Hooks log their activity to `/Users/oliverames/.claude/hooks-logs/` (auto-created on first run).

---

## 8. Skills Directory

Base path: `/Users/oliverames/.claude/skills/`

**Currently empty.** All 26 skills are delivered via the `ames-standalone-skills` plugin (installed in `~/.claude/plugins/cache/ames-claude/ames-standalone-skills/<version>/skills/`). Skills are accessed through the plugin system, not as standalone directories here.

### Skill structure (inside plugin cache)

```
~/.claude/plugins/cache/ames-claude/ames-standalone-skills/<version>/skills/<skill-name>/
├── SKILL.md                          — Required: skill definition with YAML frontmatter
└── <supporting files>/               — Optional: scripts, reference data, assets
```

### SKILL.md frontmatter schema

```yaml
---
name: skill-name
description: One-line description shown in the skills browser
version: 1.0.0  # optional
---
```

The body of SKILL.md contains the full skill instructions in markdown — injected as system-level context when the skill is invoked.

### Skills list (as of 2026-04-07)

26 skills in `ames-standalone-skills`: 1password-vault, apple-notes-formatting, apple-workout-generator, audible-library, bcbs-vt, claude-code-headless, cmux, create-shortcut, file-organization, generate-image, gmcf-masters-swim, humanizer, ios-capabilities, jelly, macos-app-icons, new, obsidian-notes, raw-plist, readme-style, shokz-rip, smart-transcribe, swiftui-pro, testflight-deployment, wrap-up, xcodegen-project, ynab-finance.

Source: `plugins/ames-standalone-skills/skills/` in the `ames-claude` repo. Edit there, then run `sync-skills` to publish and install.
