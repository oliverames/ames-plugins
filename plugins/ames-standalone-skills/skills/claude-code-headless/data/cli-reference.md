# Claude Code CLI Reference

Complete reference for all Claude Code CLI flags, options, and subcommands.
Generated from `claude --help` — verify with `claude --version` if behavior changes.

---

## 1. Execution Modes

Control how Claude Code runs: interactive vs. non-interactive, session continuation, and branching.

| Flag | Short | Description |
|------|-------|-------------|
| `--print` | `-p` | Non-interactive mode: print response and exit. Enables piping. Skips workspace trust dialog. |
| `--continue` | `-c` | Continue the most recent conversation in the current directory. |
| `--resume [value]` | `-r` | Resume a session by session ID, or open interactive picker with optional search term. |
| `--fork-session` | | When resuming, create a new session ID instead of reusing the original. Use with `--resume` or `--continue`. |
| `--from-pr [value]` | | Resume a session linked to a PR by PR number or URL; opens interactive picker if no value given. |
| `--session-id <uuid>` | | Use a specific UUID as the session ID for this conversation. |

### Examples

```bash
# One-shot print mode: ask a question, get output, exit
claude -p "What is the current date?" --permission-mode dontAsk

# Continue most recent session in project
claude --continue --permission-mode dontAsk

# Resume a specific session by ID
claude --resume a1b2c3d4-e5f6-7890-abcd-ef1234567890 --permission-mode dontAsk

# Fork a session on resume (creates a new session ID, leaving original intact)
claude --resume a1b2c3d4-e5f6-7890-abcd-ef1234567890 --fork-session --permission-mode dontAsk

# Resume session linked to a GitHub PR
claude --from-pr 42 --permission-mode dontAsk

# Force a specific UUID for the new session
claude -p "Hello" --session-id 00000000-0000-0000-0000-000000000001 --permission-mode dontAsk
```

---

## 2. Output Format

Control how Claude's responses are emitted: plain text, JSON objects, or streaming JSON.

| Flag | Description |
|------|-------------|
| `--output-format <format>` | Output format (only with `--print`): `text` (default), `json` (single result), `stream-json` (realtime streaming). |
| `--input-format <format>` | Input format (only with `--print`): `text` (default), `stream-json` (realtime streaming input). |
| `--include-partial-messages` | Include partial message chunks as they arrive (only with `--print` and `--output-format=stream-json`). |
| `--replay-user-messages` | Re-emit user messages from stdin back on stdout for acknowledgment (only with `--input-format=stream-json` and `--output-format=stream-json`). |

### Examples

```bash
# Get a single JSON result object
claude -p "Summarize this file" --output-format json --permission-mode dontAsk

# Stream JSON chunks as they arrive
claude -p "Write a long essay" --output-format stream-json --permission-mode dontAsk

# Streaming input + streaming output (for real-time bidirectional use)
echo '{"type":"user","message":{"role":"user","content":"Hello"}}' | \
  claude -p --input-format stream-json --output-format stream-json --permission-mode dontAsk

# Include partial chunks for streaming output
claude -p "Explain quantum computing" \
  --output-format stream-json \
  --include-partial-messages \
  --permission-mode dontAsk

# Round-trip: replay user messages back on stdout alongside assistant output
claude -p --input-format stream-json --output-format stream-json --replay-user-messages --permission-mode dontAsk
```

---

## 3. Permissions & Tool Control

Control which tools Claude can use and what permission checks are enforced.

| Flag | Description |
|------|-------------|
| `--permission-mode <mode>` | Permission mode: `acceptEdits`, `bypassPermissions`, `default`, `dontAsk`, `plan`, `auto`. |
| `--allowedTools <tools...>` | Whitelist specific tools. Comma or space-separated. Supports patterns like `Bash(git:*)`. |
| `--disallowedTools <tools...>` | Blacklist specific tools. Same format as `--allowedTools`. |
| `--tools <tools...>` | Set the exact list of available built-in tools. Use `""` to disable all, `"default"` for all, or list names. |
| `--dangerously-skip-permissions` | Bypass ALL permission checks. For sandboxes with no internet access only. |
| `--allow-dangerously-skip-permissions` | Enable bypassing permissions as an option (not default). For sandboxed environments. |

### Permission Mode Values

| Mode | Behavior |
|------|----------|
| `default` | Standard interactive prompts for sensitive operations. |
| `acceptEdits` | Auto-approve file edits; prompt for other sensitive ops. |
| `dontAsk` | Skip most permission prompts (still enforces tool allow/deny lists). |
| `plan` | Claude plans actions but does not execute them. |
| `bypassPermissions` | Skip all permission prompts (similar to `dangerously-skip-permissions`). |
| `auto` | Automatically determine permission level based on context. |

### Examples

```bash
# Run with no permission prompts (headless-safe)
claude -p "List files in this directory" --permission-mode dontAsk

# Allow only specific tools
claude -p "Run tests" --allowedTools "Bash(npm:*)" --permission-mode dontAsk

# Allow git operations and file reads only
claude -p "Check git status" \
  --allowedTools "Bash(git:*)" "Read" \
  --permission-mode dontAsk

# Block file editing tools entirely
claude -p "Analyze this codebase" \
  --disallowedTools "Edit" "Write" \
  --permission-mode dontAsk

# Disable all built-in tools (LLM-only response)
claude -p "What is 2+2?" --tools "" --permission-mode dontAsk

# Bypass all permissions — only in a sandboxed environment
claude -p "Run setup script" --dangerously-skip-permissions
```

---

## 4. Model Selection

Choose which Claude model to use for the session.

| Flag | Description |
|------|-------------|
| `--model <model>` | Model alias (e.g., `sonnet`, `opus`) or full model ID (e.g., `claude-sonnet-4-6`). |
| `--fallback-model <model>` | Fallback model if the primary is overloaded (only with `--print`). |
| `--betas <betas...>` | Beta headers to include in API requests (API key users only). |

### Examples

```bash
# Use the latest Sonnet model
claude -p "Write a haiku" --model sonnet --permission-mode dontAsk

# Use Opus for complex reasoning
claude -p "Architect a distributed system" --model opus --permission-mode dontAsk

# Use a specific full model ID
claude -p "Hello" --model claude-sonnet-4-6 --permission-mode dontAsk

# With a fallback if the primary model is overloaded
claude -p "Generate a report" --model opus --fallback-model sonnet --permission-mode dontAsk

# Enable a beta feature (API key users only)
claude -p "Try beta feature" --betas interleaved-thinking-2025-05-14 --permission-mode dontAsk
```

---

## 5. System Prompt & Context

Customize the assistant's behavior and inject context for the session.

| Flag | Description |
|------|-------------|
| `--system-prompt <prompt>` | Replace the default system prompt with a custom one. |
| `--append-system-prompt <prompt>` | Append additional instructions to the default system prompt. |
| `--agent <agent>` | Specify a named agent for the session (overrides the `agent` config setting). |
| `--agents <json>` | JSON object defining custom inline agents. |

### Examples

```bash
# Override the system prompt entirely
claude -p "Summarize this text" \
  --system-prompt "You are a concise technical writer. Be brief and precise." \
  --permission-mode dontAsk

# Append extra context without replacing the default prompt
claude -p "Review this PR" \
  --append-system-prompt "Always check for security vulnerabilities first." \
  --permission-mode dontAsk

# Use a named agent defined in settings
claude -p "Check code quality" --agent reviewer --permission-mode dontAsk

# Define a custom inline agent with JSON
claude -p "Review this code" \
  --agents '{"reviewer":{"description":"Reviews code","prompt":"You are a senior code reviewer. Focus on readability and correctness."}}' \
  --permission-mode dontAsk
```

---

## 6. Directory & Project

Control file system access and project context for the session.

| Flag | Description |
|------|-------------|
| `--add-dir <directories...>` | Grant tool access to additional directories beyond the current working directory. |
| `--plugin-dir <path>` | Load plugins from a directory for this session only. Repeatable. |
| `--worktree [name]` | Create a new git worktree for this session. Optionally specify a name. |
| `--tmux` | Create a tmux session for the worktree (requires `--worktree`). Uses iTerm2 native panes when available. Use `--tmux=classic` for standard tmux. |

### Examples

```bash
# Grant access to a second project directory
claude -p "Compare these two projects" \
  --add-dir /Users/oliverames/Developer/project-b \
  --permission-mode dontAsk

# Load a local plugin directory for this session only
claude -p "Run the custom command" \
  --plugin-dir /Users/oliverames/Developer/my-local-plugin \
  --permission-mode dontAsk

# Create a worktree for isolated work
claude --worktree feature-branch --permission-mode dontAsk

# Create a worktree with a tmux session
claude --worktree feature-branch --tmux --permission-mode dontAsk

# Use classic tmux layout instead of iTerm2 panes
claude --worktree feature-branch --tmux=classic --permission-mode dontAsk
```

---

## 7. Settings & Misc

Session configuration, budget limits, and miscellaneous flags.

| Flag | Description |
|------|-------------|
| `--settings <file-or-json>` | Path to a settings JSON file, or an inline JSON string for additional settings. |
| `--setting-sources <sources>` | Comma-separated list of setting sources to load: `user`, `project`, `local`. |
| `--disable-slash-commands` | Disable all skills (slash commands). |
| `--effort <level>` | Set thinking/effort level: `low`, `medium`, `high`, `max`. |
| `--json-schema <schema>` | JSON Schema for structured output validation. |
| `--max-budget-usd <amount>` | Maximum USD to spend on API calls (only with `--print`). |
| `--name <name>` | Set a display name for this session (shown in `/resume` and terminal title). |
| `--no-session-persistence` | Disable session persistence — sessions are not saved to disk (only with `--print`). |
| `--mcp-config <configs...>` | Load MCP servers from JSON files or strings (space-separated). |
| `--strict-mcp-config` | Only use MCP servers from `--mcp-config`, ignoring all other MCP configurations. |
| `--file <specs...>` | File resources to download at startup. Format: `file_id:relative_path`. |
| `--brief` | Enable `SendUserMessage` tool for agent-to-user communication. |
| `--ide` | Automatically connect to IDE on startup if exactly one valid IDE is available. |

### Examples

```bash
# Load additional settings from a JSON file
claude -p "Run analysis" \
  --settings /Users/oliverames/.claude/headless-settings.json \
  --permission-mode dontAsk

# Use only user-level settings (ignore project and local)
claude -p "Run analysis" --setting-sources user --permission-mode dontAsk

# Disable all skills for a clean session
claude -p "Answer without skills" --disable-slash-commands --permission-mode dontAsk

# Set effort level to max for complex tasks
claude -p "Design a full system architecture" --effort max --permission-mode dontAsk

# Enforce structured JSON output matching a schema
claude -p "Extract name and age from: John is 30 years old" \
  --output-format json \
  --json-schema '{"type":"object","properties":{"name":{"type":"string"},"age":{"type":"number"}},"required":["name","age"]}' \
  --permission-mode dontAsk

# Cap API spend at $0.50
claude -p "Process this large document" --max-budget-usd 0.50 --permission-mode dontAsk

# Name a session for easy resumption
claude -p "Start a named session" --name "refactor-auth-module" --permission-mode dontAsk

# Ephemeral session — no disk persistence
claude -p "One-off query" --no-session-persistence --permission-mode dontAsk

# Load a custom MCP config and ignore all others
claude -p "Use only my MCP tools" \
  --mcp-config /Users/oliverames/.claude/custom-mcp.json \
  --strict-mcp-config \
  --permission-mode dontAsk
```

---

## 8. Debugging

Capture logs, filter debug output, and diagnose issues.

| Flag | Description |
|------|-------------|
| `--debug [filter]` | Enable debug mode. Optional filter string (e.g., `"api,hooks"`) or negation (e.g., `"!1p,!file"`). |
| `--debug-file <path>` | Write debug logs to a file. Implicitly enables debug mode. |
| `--verbose` | Override the verbose mode setting from config (enables verbose output). |
| `--mcp-debug` | **DEPRECATED.** Use `--debug` instead. Previously enabled MCP debug mode. |

### Debug Category Filtering

The `--debug` flag accepts a comma-separated category filter:
- `api` — API request/response logs
- `hooks` — hook invocations
- `file` — file system operations
- `1p` — first-party tool calls
- Prefix with `!` to **exclude** a category (e.g., `!file` hides file logs)

### Examples

```bash
# Enable all debug output to stderr
claude -p "Hello" --debug --permission-mode dontAsk

# Debug only API and hooks categories
claude -p "Run tests" --debug "api,hooks" --permission-mode dontAsk

# Debug everything except file operations and 1p tools
claude -p "Run tests" --debug "!file,!1p" --permission-mode dontAsk

# Write debug logs to a specific file (debug mode implicitly enabled)
claude -p "Debug this run" \
  --debug-file /Users/oliverames/Library/Logs/claude-debug.log \
  --permission-mode dontAsk

# Combine debug-file with category filtering
claude -p "Trace API calls" \
  --debug "api" \
  --debug-file /Users/oliverames/Library/Logs/claude-api-trace.log \
  --permission-mode dontAsk

# Enable verbose output
claude -p "Build project" --verbose --permission-mode dontAsk
```

---

## 9. Subcommands

Claude Code includes several subcommands for managing MCP servers, plugins, auth, and updates.

### `mcp` — Manage MCP Servers

```
claude mcp [subcommand]
```

| Subcommand | Description |
|------------|-------------|
| `mcp list` | List all configured MCP servers. |
| `mcp add <name> [args...]` | Add a new MCP server. |
| `mcp get <name>` | Show details for a specific MCP server. |
| `mcp remove <name>` | Remove an MCP server by name. |

```bash
# List all MCP servers
claude mcp list

# Add a local MCP server
claude mcp add my-server -- node /Users/oliverames/Developer/my-mcp/index.js

# Get details for a specific server
claude mcp get my-server

# Remove an MCP server
claude mcp remove my-server
```

### `plugin` / `plugins` — Manage Plugins

```
claude plugin [subcommand]
```

Manage Claude Code plugins: list installed, install from marketplace or local path, remove.

```bash
# List installed plugins
claude plugin list

# Install a plugin from the marketplace
claude plugin install my-plugin

# Install from a local directory
claude plugin install "/Users/oliverames/Library/Mobile Documents/com~apple~CloudDocs/Developer/projects/ames-claude"

# Remove a plugin
claude plugin remove my-plugin
```

### `auth` — Manage Authentication

```
claude auth [subcommand]
```

Manage authentication credentials and tokens.

```bash
# Check current auth status
claude auth status

# Log in (opens browser)
claude auth login

# Log out
claude auth logout
```

### `setup-token` — Long-lived Auth Token

```
claude setup-token
```

Set up a long-lived authentication token. Requires a Claude subscription.

```bash
claude setup-token
```

### `doctor` — Health Check

```
claude doctor
```

Check the health of the Claude Code auto-updater and installation.

```bash
claude doctor
```

### `update` / `upgrade` — Update Claude Code

```
claude update
```

Check for updates and install if available.

```bash
claude update
```

### `install` — Install Native Build

```
claude install [target]
```

Install Claude Code native build. Target can be `stable`, `latest`, or a specific version string.

```bash
# Install the stable native build
claude install stable

# Install the latest build
claude install latest

# Install a specific version
claude install 1.2.3
```

### `agents` — List Configured Agents

```
claude agents [options]
```

List all agents configured for the current session or globally.

```bash
claude agents
```

---

## 10. Interactive Slash Commands

Commands available inside an interactive Claude Code session. Type `/` to
see the full menu. Skills (user-defined slash commands) also appear in the
menu but are not listed here.

### Session Control

| Command | Alias | Description |
|---------|-------|-------------|
| `/exit` | `/quit` | Exit the CLI. |
| `/clear` | `/reset`, `/new` | Clear conversation history and free up context. |
| `/compact [instructions]` | | Compact conversation with optional focus instructions. |
| `/context` | | Visualize current context usage as a colored grid. |
| `/copy [N]` | | Copy last assistant response to clipboard. |
| `/cost` | | Show token usage statistics. |
| `/diff` | | Open interactive diff viewer for uncommitted changes. |
| `/export [filename]` | | Export conversation as plain text. |
| `/rewind` | `/checkpoint` | Rewind conversation/code to a previous point. |
| `/branch [name]` | `/fork` | Create a branch of the conversation. |
| `/resume [session]` | `/continue` | Resume a conversation. |
| `/rename [name]` | | Rename the current session. |

### Configuration

| Command | Alias | Description |
|---------|-------|-------------|
| `/config` | `/settings` | Open Settings interface. |
| `/color [color\|default]` | | Set the prompt bar color for the current session. |
| `/effort [low\|medium\|high\|max\|auto]` | | Set model effort level. |
| `/fast [on\|off]` | | Toggle fast mode (same model, faster output). |
| `/model [model]` | | Select or change the AI model. |
| `/permissions` | `/allowed-tools` | View or update permissions. |
| `/sandbox` | | Toggle sandbox mode. |
| `/statusline` | | Configure the status line. |
| `/theme` | | Change color theme. |
| `/vim` | | Toggle Vim editing mode. |
| `/keybindings` | | Open keybindings configuration file. |
| `/terminal-setup` | | Configure terminal keybindings (only in terminals that need it). |

### Project & Tools

| Command | Alias | Description |
|---------|-------|-------------|
| `/add-dir <path>` | | Add a new working directory to the current session. |
| `/init` | | Initialize project with CLAUDE.md. |
| `/memory` | | Edit CLAUDE.md memory files. |
| `/mcp` | | Manage MCP server connections. |
| `/hooks` | | View hook configurations. |
| `/plugin` | | Manage plugins. |
| `/reload-plugins` | | Reload all active plugins. |
| `/agents` | | Manage agent configurations. |
| `/skills` | | List available skills. |
| `/tasks` | | List and manage background tasks. |
| `/plan [description]` | | Enter plan mode. |

### Account & Info

| Command | Alias | Description |
|---------|-------|-------------|
| `/help` | | Show help and available commands. |
| `/status` | | Show version, model, account, and connectivity info. |
| `/usage` | | Show plan usage limits and rate limit status. |
| `/extra-usage` | | Configure extra usage for rate limits. |
| `/login` | | Sign in to Anthropic account. |
| `/logout` | | Sign out from Anthropic account. |
| `/doctor` | | Diagnose and verify Claude Code installation. |
| `/release-notes` | | View the full changelog. |
| `/feedback [report]` | `/bug` | Submit feedback. |
| `/stats` | | Visualize daily usage, session history, and streaks. |
| `/insights` | | Generate a report analyzing your Claude Code sessions. |

### Platform & Integration

| Command | Alias | Description |
|---------|-------|-------------|
| `/desktop` | `/app` | Continue session in Claude Code Desktop app (macOS/Windows). |
| `/mobile` | `/ios`, `/android` | Show QR code for mobile app. |
| `/ide` | | Manage IDE integrations. |
| `/chrome` | | Configure Claude in Chrome settings. |
| `/remote-control` | `/rc` | Enable remote control from claude.ai. |
| `/remote-env` | | Configure default remote environment. |
| `/voice` | | Toggle push-to-talk voice dictation. |

### Other

| Command | Alias | Description |
|---------|-------|-------------|
| `/btw <question>` | | Ask a quick side question without adding to the conversation. |
| `/install-github-app` | | Set up Claude GitHub Actions app. |
| `/install-slack-app` | | Install the Claude Slack app. |
| `/pr-comments [PR]` | | Fetch GitHub PR comments. |
| `/privacy-settings` | | View/update privacy settings (Pro/Max only). |
| `/schedule [description]` | | Create/manage cloud scheduled tasks. |
| `/security-review` | | Analyze pending changes for security vulnerabilities. |
| `/upgrade` | | Open upgrade page (Pro/Max only). |
| `/passes` | | Share a free week of Claude Code (if eligible). |
| `/stickers` | | Order Claude Code stickers. |

---

## Quick Reference: Most Common Headless Invocation Patterns

```bash
# Minimal headless: one-shot, no prompts, plain text output
claude -p "Your prompt here" --permission-mode dontAsk

# Headless with JSON output for programmatic parsing
claude -p "Extract data" --output-format json --permission-mode dontAsk

# Headless with capped budget and no session persistence
claude -p "Process this" \
  --max-budget-usd 1.00 \
  --no-session-persistence \
  --permission-mode dontAsk

# Headless with specific model and effort
claude -p "Hard problem" \
  --model opus \
  --effort max \
  --permission-mode dontAsk

# Headless with tool restriction (read-only)
claude -p "Analyze codebase" \
  --allowedTools "Read" "Glob" "Grep" \
  --permission-mode dontAsk

# Headless with debug logging to file
claude -p "Debug this run" \
  --debug-file /Users/oliverames/Library/Logs/claude-debug.log \
  --permission-mode dontAsk

# Resume last session non-interactively
claude --continue -p "Continue where we left off" --permission-mode dontAsk
```
