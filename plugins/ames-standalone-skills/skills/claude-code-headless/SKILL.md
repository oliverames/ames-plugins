---
name: Claude Code Headless
description: >-
  Use when the user asks to "interact with Claude Code", "check Claude Code
  status", "dispatch a task to Claude Code", "run something in Claude Code",
  "check installed plugins", "manage Claude Code settings", "continue a
  Claude Code session", "read Claude Code memory", or needs to programmatically
  control, inspect, or configure a local Claude Code instance. Also triggers
  for "headless Claude Code", "Claude Code CLI", "what plugins are installed",
  "update Claude Code settings", "launch Claude Code to do X".
---

# Claude Code Headless

Operator guide for programmatically controlling a local Claude Code installation. All operations use Bash, Read, Edit, Write, Glob, and Grep tools that CoWork already has access to.

## 1. Environment

| Constant | Value |
|----------|-------|
| Claude Code config | `/Users/oliverames/.claude/` |
| Home directory | `/Users/oliverames/` |
| Developer projects | `/Users/oliverames/Developer/` and `/Users/oliverames/Library/Mobile Documents/com~apple~CloudDocs/Developer/` |
| Platform | macOS (local only) |
| Default dispatch | All tasks run headless (`-p`) with tmux (`--tmux`) |
| Sync script | `sync-skills` (in PATH via `~/Developer/scripts/`) |

**Rule:** Always use absolute paths. Never use `~` or relative paths. Claude Code resolves all paths from the working directory, so absolute paths prevent ambiguity.

---

## 2. Introspection (Read State)

Use these to answer "what's going on in Claude Code?"

| What to check | How to check | Notes |
|---|---|---|
| Installed plugins | Read `/Users/oliverames/.claude/plugins/installed_plugins.json` | Lists all plugins with versions and install paths |
| Settings & permissions | Read `/Users/oliverames/.claude/settings.json` — targeted fields only | **Skip the `env` object.** Read only the specific key needed (e.g., `permissions`, `hooks`). |
| Enabled plugins | Check `enabledPlugins` in settings.json | Map of `"name@source": true/false` |
| Project memory | Read `/Users/oliverames/.claude/projects/<encoded-path>/memory/MEMORY.md` | Path encoding: replace `/` with `-`, keep leading `-` |
| Project instructions | Read `/Users/oliverames/.claude/projects/<encoded-path>/CLAUDE.md` | Project-scoped instructions injected into sessions |
| Recent sessions | List session directories in `/Users/oliverames/.claude/projects/<encoded-path>/` | Each session is a UUID-named directory |
| Hook configuration | Check `hooks` object in settings.json | Four event types: PreToolUse, PostToolUse, Notification, Stop |
| Environment variables | **DO NOT READ the `env` object.** It contains plaintext API keys. | Check key names only if strictly needed via targeted extraction. |

### Path Encoding for Project Lookups

Project data lives under `/Users/oliverames/.claude/projects/<encoded-path>/`. The encoding rule: replace every `/` with `-` and keep the leading `-`.

Examples:

| Original path | Encoded directory name |
|---|---|
| `/Users/oliverames` | `-Users-oliverames` |
| `/Users/oliverames/Developer/my-app` | `-Users-oliverames-Developer-my-app` |
| `/Users/oliverames/Library/Mobile Documents/com~apple~CloudDocs/Developer/projects/ames-claude` | `-Users-oliverames-Library-Mobile-Documents-com-apple-CloudDocs-Developer-projects-ames-claude` |

Note: spaces become hyphens, tildes stay as-is.

### Reading settings.json Safely

Never read the full file. Use targeted extraction:

```bash
# Read only the permissions object
node -e "const s=JSON.parse(require('fs').readFileSync('/Users/oliverames/.claude/settings.json','utf8')); console.log(JSON.stringify(s.permissions,null,2))"

# Read only enabledPlugins
node -e "const s=JSON.parse(require('fs').readFileSync('/Users/oliverames/.claude/settings.json','utf8')); console.log(JSON.stringify(s.enabledPlugins,null,2))"

# Read only hooks configuration
node -e "const s=JSON.parse(require('fs').readFileSync('/Users/oliverames/.claude/settings.json','utf8')); console.log(JSON.stringify(s.hooks,null,2))"
```

For full directory structure and JSON schemas, read `data/filesystem-map.md`.

---

## 3. Task Dispatch (Run Work)

Use these to "go do something in Claude Code." This is the primary workflow.

### 3a. Directory Selection (Mandatory Pre-Step)

**You MUST confirm the directory with the user before launching.** Wrong directory means wrong CLAUDE.md, wrong git context, and wrong MCP servers.

Decision tree:

```
Is this a general/non-project task?
  -> Use /Users/oliverames/

Is this Claude Code self-management?
  -> Use /Users/oliverames/
     (loads home-directory CLAUDE.md and project context)

Is this project-specific?
  -> Do I know the directory?
      -> Yes: Confirm with user:
         "I'd like to launch Claude Code in <path>. Sound right?"
      -> No: Ask user permission to search the Mac
         -> Search (e.g., find directories matching project name)
         -> Present options to user
         -> User confirms
         -> Proceed
```

**Never assume a directory. Always confirm.**

### 3b. Tiered Dispatch Patterns

**Pattern 1: Fire-and-forget** — Simple tasks, no result capture needed:

```bash
cd /Users/oliverames/Developer/some-project && claude -p "Fix the typo in README.md" --tmux --permission-mode dontAsk
```

Use when: bug fixes, code changes, git operations, file edits -- anything where the user does not need CoWork to process the output.

**Pattern 2: Capture result** — CoWork needs the output to continue its own work:

```bash
cd /Users/oliverames/ && claude -p "List all TODO comments" --output-format json --permission-mode dontAsk > /tmp/cc-result-$(date +%s).json
```

Then read `/tmp/cc-result-*.json` to get the result.

Use when: research questions, data extraction, analysis that CoWork will summarize or act on.

**IMPORTANT: `--tmux` and `>` redirect are incompatible.** tmux detaches the process, so stdout redirect captures nothing. Choose one:
- Need persistence? Use `--tmux`. Read session output from project session files afterward.
- Need captured output? Omit `--tmux`. Use `>` redirect or `--output-format json`.
- Need both? Use `--tmux`, then after the session completes, read the session data from `/Users/oliverames/.claude/projects/<encoded-path>/<session-uuid>/`.

**Pattern 3: Session management** — Long-running or multi-step work:

```bash
cd /Users/oliverames/Developer/some-project && claude -p "Refactor the auth module" --tmux --session-id 550e8400-e29b-41d4-a716-446655440000 --permission-mode dontAsk
```

`--session-id <uuid>` assigns a deterministic ID for later resume. Generate a UUID with `uuidgen` before dispatching. If omitted, discover the generated ID from the most recent session directory in `/Users/oliverames/.claude/projects/<encoded-path>/`.

To continue a managed session later:

```bash
cd /Users/oliverames/Developer/some-project && claude --resume 550e8400-e29b-41d4-a716-446655440000 -p "Now add tests for the refactored module" --tmux --permission-mode dontAsk
```

### 3c. Practical Examples

```bash
# Read-only research task (cost-capped, no file writes)
cd /Users/oliverames/Developer/my-app && claude -p "Analyze the dependency tree and identify unused packages" \
  --allowedTools "Read,Grep,Glob,Bash(npm:*)" \
  --max-budget-usd 0.50 \
  --output-format json \
  --permission-mode dontAsk > /tmp/cc-deps-$(date +%s).json

# Complex refactor with git isolation
cd /Users/oliverames/Developer/my-app && claude -p "Refactor all API routes to use the new middleware pattern" \
  --tmux \
  --worktree \
  --name "api-refactor" \
  --permission-mode dontAsk

# Quick fix with cheaper model
cd /Users/oliverames/Developer/my-app && claude -p "Fix the lint errors in src/utils.ts" \
  --tmux \
  --model sonnet \
  --permission-mode dontAsk

# Multi-directory task
cd /Users/oliverames/Developer/frontend && claude -p "Update API client to match the new backend endpoints" \
  --add-dir /Users/oliverames/Developer/backend \
  --tmux \
  --permission-mode dontAsk
```

### 3d. Dispatch Defaults

All CoWork-triggered sessions use these flags:

| Flag | Purpose |
|------|---------|
| `-p` | Headless/non-interactive mode |
| `--tmux` | Session persists in tmux (unless capturing output) |
| `--permission-mode dontAsk` | Uses Oliver's pre-configured allow list |

### 3e. Optional Flags

| Flag | When to use |
|------|-------------|
| `--model sonnet` | Simpler tasks, cost-conscious |
| `--worktree` | Parallel tasks or risky changes needing git isolation |
| `--allowedTools "Read,Grep,Glob"` | Read-only tasks (research, analysis) |
| `--max-budget-usd 1.00` | Cost-capped exploratory tasks |
| `--system-prompt "..."` | Replace default system prompt with specialized behavior |
| `--append-system-prompt "..."` | Add context without replacing defaults |
| `--fallback-model sonnet` | Fallback if primary model is overloaded |
| `--output-format stream-json` | Real-time streaming output |
| `--add-dir /path` | Grant access to additional directories |
| `--name "task-name"` | Named session for easy identification in resume picker |

For complete CLI flag documentation, read `data/cli-reference.md`.

---

## 4. Configuration (Modify State)

Use these to "change Claude Code's setup."

| What to change | How | Caution |
|---|---|---|
| Permissions | Edit settings.json -> `permissions` | Medium |
| Environment variables | Edit settings.json -> `env` | Medium -- never log values |
| Install plugin | 3 artifacts: `installed_plugins.json` entry + cache files in `plugins/cache/` + `.install-manifests/<name>@<source>.json` | High |
| Remove plugin | Remove entry from `installed_plugins.json` + remove from `enabledPlugins` | Medium |
| Enable/disable plugin | Edit settings.json -> `enabledPlugins` | Low |
| Project memory | Write to `projects/<encoded-path>/memory/` | Low |
| Project CLAUDE.md | Edit `projects/<encoded-path>/CLAUDE.md` | Low |
| Hook scripts | **Never modify directly** -- use settings.json `hooks` config | High |

**Warning:** After any settings.json edit, validate JSON syntax before saving. Malformed JSON will break Claude Code startup.

Validation command:

```bash
node -e "JSON.parse(require('fs').readFileSync('/Users/oliverames/.claude/settings.json', 'utf8'))"
```

No output means valid JSON.

### Plugin Installation Checklist

Installing a plugin requires three coordinated changes:

1. **Add entry to `installed_plugins.json`** — key format: `"<name>@<source>"`, value: array with one InstallRecord object containing `scope`, `installPath`, `version`, `installedAt`, `lastUpdated`.
2. **Place plugin files in cache** — at `/Users/oliverames/.claude/plugins/cache/<source>/<name>/<version>/` with `.claude-plugin/plugin.json` and command/skill/agent files.
3. **Create install manifest** — at `/Users/oliverames/.claude/plugins/.install-manifests/<name>@<source>.json` with SHA-256 hashes of all files.

For most cases, prefer running the sync script instead of manual installation:

```bash
sync-skills
```

### Enabling/Disabling a Plugin

To toggle a plugin without uninstalling, edit the `enabledPlugins` field in settings.json. The key format is `"<name>@<source>"` and the value is `true` or `false`.

For full safety reference, read `data/safety-guardrails.md`.

---

## 5. Session Management

Use these to "check on or continue previous work."

| Action | Command |
|--------|---------|
| Continue most recent session | `claude --continue --permission-mode dontAsk` |
| Resume by session ID | `claude --resume <session-id> --permission-mode dontAsk` |
| Resume with interactive picker | `claude --resume` (no ID -- interactive, not headless) |
| Fork a session | `claude --resume <id> --fork-session --permission-mode dontAsk` |
| Resume from a PR | `claude --from-pr <number-or-url> --permission-mode dontAsk` |
| List tmux sessions | `tmux list-sessions` |
| Attach to tmux session | `tmux attach -t <session-name>` |
| Monitor session output | `tmux capture-pane -t <session-name> -p` |

**Session ID discovery:** If you launched with `--tmux` and did not specify `--session-id`, find the generated ID by listing session directories in `/Users/oliverames/.claude/projects/<encoded-path>/` and sorting by modification time. The most recent UUID directory is the latest session.

**Named sessions:** Use `--name "descriptive-name"` at launch to make sessions easier to identify in the resume picker.

### Monitoring a Running tmux Session

To check on a fire-and-forget task that is still running:

```bash
# List all active tmux sessions
tmux list-sessions

# Capture the last 100 lines of output from a session
tmux capture-pane -t <session-name> -p -S -100

# Check if a session is still active (exit code 0 = running)
tmux has-session -t <session-name> 2>/dev/null && echo "running" || echo "finished"
```

### Worktree Sessions

When `--worktree` is used, Claude Code creates a git worktree (an isolated working copy on a separate branch). This is useful for parallel tasks or risky changes. The worktree is created under the project directory and cleaned up when the session ends.

```bash
# Launch with worktree for isolated work
cd /Users/oliverames/Developer/my-app && claude -p "Try a different approach to the caching layer" \
  --tmux \
  --worktree \
  --name "cache-experiment" \
  --permission-mode dontAsk
```

---

## 6. Safety & Guardrails

Quick-reference rules. Full detail is in `data/safety-guardrails.md`.

**Safe to read:**
- Everything in `/Users/oliverames/.claude/` EXCEPT the `env` object in settings.json
- Plugin cache, hook scripts, project memory, session directories

**Safe to write (with care):**
- `settings.json` (targeted fields only -- validate JSON after every edit)
- `installed_plugins.json` (validate JSON after every edit)
- Project memory files (`projects/<encoded-path>/memory/`)
- Project `CLAUDE.md` files

**Never write:**
- Hook scripts in `/Users/oliverames/.claude/hooks/` (configure via settings.json instead)
- Plugin cache files directly (managed by sync script)
- Session files (read-only)

**Never read/print/forward:**
- Values from settings.json -> `env` (contains plaintext API keys)
- Never read settings.json in full -- always use targeted field reads

**Active hooks:**
- `block-dangerous-commands.js` -- blocks destructive Bash patterns (rm home, force-push main, etc.)
- `protect-secrets.js` -- blocks access to `.env`, SSH keys, credentials files
- `auto-stage.js` -- git-stages files after Edit/Write
- `notify-brrr.js` -- sends push notifications on session events

For complete hook documentation and safety matrix, read `data/safety-guardrails.md`.
