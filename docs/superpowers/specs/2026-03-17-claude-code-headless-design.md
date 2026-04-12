# Claude Code Headless Skill — Design Spec

**Date:** 2026-03-17
**Status:** Reviewed
**Author:** Oliver + Claude

## Problem

CoWork (Anthropic's desktop agent) needs to programmatically interact with Oliver's local Claude Code instance at `/Users/oliverames/.claude`. Currently there's no structured knowledge teaching CoWork how to:
- Inspect Claude Code's state (plugins, settings, memory, sessions)
- Dispatch headless tasks against arbitrary directories
- Modify Claude Code configuration
- Manage long-running sessions

## Solution

A standalone skill (`claude-code-headless`) that teaches any agent — primarily CoWork — how to fully orchestrate a local Claude Code installation. Organized as a decision-tree operator guide with on-demand reference files.

## Skill Identity

- **Name:** `claude-code-headless`
- **Location:** `skills/claude-code-headless/SKILL.md` + `data/` reference files
- **Installed via:** `ames-claude` bundle (synced by `sync-skills`)
- **Target consumer:** CoWork on macOS; also usable by any Claude Code session

**Trigger description:**
> Use when the user asks to "interact with Claude Code", "check Claude Code status", "dispatch a task to Claude Code", "run something in Claude Code", "check installed plugins", "manage Claude Code settings", "continue a Claude Code session", "read Claude Code memory", or needs to programmatically control, inspect, or configure a local Claude Code instance. Also triggers for "headless Claude Code", "Claude Code CLI", "what plugins are installed", "update Claude Code settings", "launch Claude Code to do X".

## File Layout

```
skills/claude-code-headless/
├── SKILL.md                          # Main skill — decision-tree operator guide (~300-400 lines)
└── data/
    ├── cli-reference.md              # Complete CLI flags & usage patterns
    ├── filesystem-map.md             # Full directory structure & JSON schemas
    └── safety-guardrails.md          # What not to touch, dangerous operations, hook system
```

## Environment

- **Absolute path:** `/Users/oliverames/.claude`
- **Platform:** macOS only, local instance
- **Default dispatch mode:** Headless (`-p`) + tmux (`--tmux`)
- **Home directory:** `/Users/oliverames/`
- **Important:** Always use absolute paths. Never use `~` — it may not resolve correctly outside a shell context.

## SKILL.md Content Architecture

### Section 1: Environment

Establishes the absolute paths, platform assumptions, and default dispatch pattern (headless + tmux for all CoWork-triggered work).

### Section 2: Introspection (Read State)

*"What's going on in Claude Code?"*

Teaches CoWork to inspect Claude Code state by reading files directly:

| What to check | How |
|----------------|-----|
| Installed plugins | Read `/Users/oliverames/.claude/plugins/installed_plugins.json` |
| Settings & permissions | Read `/Users/oliverames/.claude/settings.json` |
| Enabled plugins | Check `enabledPlugins` in settings.json |
| Project memory | Read `/Users/oliverames/.claude/projects/<url-encoded-path>/memory/` |
| Project instructions | Read `/Users/oliverames/.claude/projects/<url-encoded-path>/CLAUDE.md` |
| Recent sessions | Read session files in projects directory |
| Hook configuration | Check `hooks` object in settings.json |
| Environment variables | **Do not read the `env` object.** It contains plaintext API keys and secrets. If you need to know whether a specific key exists, check for the key name only — never read, print, forward, or include `env` values in any output or dispatched prompt. |

Each item includes: what to read, how to interpret the data, and example patterns.

Pointer to `data/filesystem-map.md` for full directory structure and JSON schemas.

### Section 3: Task Dispatch (Run Work)

*"Go do something in Claude Code."*

#### Directory Selection (Mandatory Pre-Step)

Before dispatching any task, CoWork must determine and confirm the working directory:

```
Is this a general/non-project task?
  → Use /Users/oliverames/
Is this Claude Code self-management?
  → Use /Users/oliverames/ (note: this loads the home-directory CLAUDE.md and project context)
Is this project-specific?
  → Do I know the directory?
      → Yes → Confirm with user: "I'd like to launch Claude Code in <path>. Sound right?"
      → No → Ask permission to search the Mac for relevant directories
             → Search (e.g., find directories matching project name)
             → Present options to user
             → User confirms
             → Proceed
```

**CoWork must always confirm the directory with the user before launching.** Never assume — the wrong directory means wrong CLAUDE.md, wrong git context, wrong MCP servers.

#### Tiered Dispatch Patterns

**Fire-and-forget** — Simple tasks that don't need result capture:
```bash
cd /Users/oliverames/Developer/some-project && claude -p "Fix the typo in README.md" --tmux --permission-mode dontAsk
```

**Capture result** — Tasks where CoWork needs the output (no `--tmux` — stdout must go to the shell):
```bash
cd /Users/oliverames/ && claude -p "List all TODO comments in the codebase" --output-format json --permission-mode dontAsk > /tmp/cc-result-$(date +%s).json
```
Then read `/tmp/cc-result-*.json` to get the result.

Note: `--tmux` and stdout redirect are incompatible — tmux detaches the process, so `>` would capture nothing. For tasks that need both persistence and result capture, dispatch with `--tmux` and read the session output from the project's session files afterward.

**Session management** — Long-running or multi-step work:
```bash
cd /Users/oliverames/Developer/some-project && claude -p "Refactor the auth module" --tmux --session-id <uuid> --permission-mode dontAsk
```
`--session-id <uuid>` assigns a deterministic session ID so CoWork can resume later with `claude --resume <uuid>`. If you omit `--session-id`, Claude Code generates one automatically — discover it afterward by reading the most recently created session file in `/Users/oliverames/.claude/projects/<url-encoded-path>/`.

To continue later: `claude --resume <uuid>` or `claude --continue` (picks up most recent session in that directory).

#### Dispatch Defaults

All CoWork-triggered Claude Code sessions use:
- `--tmux` — Always. Sessions persist and can be monitored.
- `--permission-mode dontAsk` — Uses Oliver's pre-configured allow list.
- `-p` — Headless/non-interactive mode.

#### Optional Flags (Use When Appropriate)

| Flag | When to use |
|------|-------------|
| `--model sonnet` | Simpler tasks, cost-conscious |
| `--worktree` | Parallel tasks or risky changes needing git isolation |
| `--allowedTools "Read,Grep,Glob"` | Read-only tasks (research, analysis) |
| `--max-budget-usd 1.00` | Cost-capped exploratory tasks |
| `--system-prompt "..."` | Specialized behavior for the dispatched session |
| `--append-system-prompt "..."` | Add context without replacing default prompt |
| `--fallback-model sonnet` | Use a fallback if primary model is overloaded |
| `--output-format stream-json` | Real-time streaming output |
| `--add-dir /path` | Grant access to additional directories |

Pointer to `data/cli-reference.md` for complete flag documentation.

### Section 4: Configuration (Modify State)

*"Change Claude Code's setup."*

| What to change | How | Caution level |
|----------------|-----|---------------|
| Permissions (allow/deny) | Edit `settings.json` → `permissions` object | Medium — test after editing |
| Environment variables | Edit `settings.json` → `env` object | Medium — never log values |
| Install a plugin | Add entry to `installed_plugins.json` + place files in cache + create `.install-manifests/<name>@<source>.json` | High — follow exact v2 format, all 3 artifacts required |
| Remove a plugin | Remove from `installed_plugins.json` + `enabledPlugins` | Medium |
| Enable/disable plugin | Edit `settings.json` → `enabledPlugins` | Low |
| Project memory | Write to `projects/<encoded-path>/memory/` | Low |
| Project CLAUDE.md | Edit `projects/<encoded-path>/CLAUDE.md` | Low |
| Hook scripts | **Do not modify directly** — use settings.json hook config | High |

**After any settings.json edit:** Validate JSON syntax before saving. A malformed settings.json will break Claude Code startup.

Pointer to `data/safety-guardrails.md` for full guardrail documentation.

### Section 5: Session Management

*"Check on or continue previous work."*

| Action | Command |
|--------|---------|
| Continue most recent session | `claude --continue` |
| Resume by session ID | `claude --resume <session-id>` |
| Resume with interactive picker | `claude --resume` (no ID) |
| Fork a session (new branch of conversation) | `claude --resume <id> --fork-session` |
| Resume from a PR | `claude --from-pr <number-or-url>` |
| List tmux sessions | `tmux list-sessions` |
| Attach to tmux session | `tmux attach -t <session-name>` |
| Monitor session output | `tmux capture-pane -t <session-name> -p` |

### Section 6: Safety & Guardrails

Quick reference (full detail in `data/safety-guardrails.md`):

**Always safe to read:** Everything in `/Users/oliverames/.claude/` — **except** the `env` object in `settings.json` (contains plaintext secrets)
**Safe to write with care:** `settings.json`, `installed_plugins.json`, project memory files, project CLAUDE.md files
**Never write directly:** Hook scripts in `hooks/`, plugin cache files (use install flow instead), session files
**Never read, print, forward, or include in prompts:** Values from `settings.json` → `env` (API keys, tokens, secrets). Check key names only if needed. Never read `settings.json` in full — use targeted reads of specific fields.

**Active hooks that may block operations:**
- `block-dangerous-commands.js` — Blocks destructive bash commands (rm ~/, force push to main, etc.)
- `protect-secrets.js` — Blocks reading/exfiltrating secret files (.env, SSH keys, AWS creds, etc.)

## Reference Files

### data/cli-reference.md

Complete `claude` CLI documentation organized by category:
- Execution modes (-p, -c, -r, --session-id, --fork-session, --from-pr)
- Output format (--output-format text|json|stream-json, --input-format, --include-partial-messages)
- Permissions (--permission-mode, --allowedTools, --disallowedTools, --tools, --dangerously-skip-permissions)
- Model selection (--model, --fallback-model, --betas)
- System prompt & context (--system-prompt, --append-system-prompt, --agent, --agents)
- Directory & project (--add-dir, --plugin-dir, --worktree, --tmux)
- Settings (--settings, --setting-sources, --disable-slash-commands, --effort)
- Debugging (--debug, --debug-file, --verbose)
- Subcommands (mcp, plugin, auth, doctor, update)
- Copy-paste-ready examples for each flag

### data/filesystem-map.md

Complete directory structure of `/Users/oliverames/.claude/`:
- Top-level files: settings.json, settings.local.json, keybindings.json, statsig/
- plugins/: installed_plugins.json (v2 format schema), cache/<source>/<name>/<version>/ structure, .install-manifests/<name>@<source>.json for provenance tracking
- projects/: URL-encoded absolute path subdirectories, per-project CLAUDE.md, memory/, sessions
- hooks/: block-dangerous-commands.js, protect-secrets.js, auto-stage.js, notify-brrr.js
- skills/: Installed standalone skills
- JSON schemas for settings.json and installed_plugins.json with field-level documentation

### data/safety-guardrails.md

- Complete hook system documentation
- block-dangerous-commands.js: All 50+ patterns across critical/high/strict levels
- protect-secrets.js: All 40+ file patterns and 38+ command patterns
- File safety matrix (read/write/never-touch)
- Recovery steps if settings.json gets corrupted
- Permission model explanation (dontAsk mode, allow/deny lists, how hooks interact)

## Design Decisions

1. **Skill, not plugin** — The core value is knowledge/instructions. No slash commands or agents needed yet. Can promote to plugin later.
2. **Hardcoded absolute paths** — CoWork may not resolve `~`. Eliminates ambiguity.
3. **Headless + tmux as default** — All CoWork-triggered sessions persist and can be monitored asynchronously.
4. **Directory confirmation required** — CoWork must confirm the target directory with the user before launching. Wrong directory = wrong context cascade.
5. **Reference files in data/** — Keeps SKILL.md focused on decision-making. Full reference loaded on-demand to manage token usage.
6. **Home directory as default** — General tasks and Claude Code self-management both launch from `/Users/oliverames/`.

## Success Criteria

- CoWork can inspect any aspect of Claude Code's state without guidance
- CoWork can dispatch headless tasks to arbitrary directories with appropriate flags
- CoWork can modify Claude Code configuration safely
- CoWork can manage long-running sessions (start, monitor, resume, fork)
- CoWork always confirms directory with user before dispatching
- No accidental exposure of API keys or secrets
- No corruption of settings.json or installed_plugins.json

## Out of Scope (For Now)

- Remote/SSH Claude Code instances
- Multiple Claude Code installations
- Automated plugin development workflow (covered by existing plugin-dev skills)
- Claude Code update/upgrade management
