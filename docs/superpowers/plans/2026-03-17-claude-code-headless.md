# Claude Code Headless Skill — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a standalone skill that teaches CoWork (and other agents) how to fully orchestrate Oliver's local Claude Code instance — inspecting state, dispatching headless tasks, modifying configuration, and managing sessions.

**Architecture:** Single SKILL.md (~300-400 lines) organized as a decision-tree operator guide, with three reference files in `data/` loaded on-demand. All paths hardcoded to `/Users/oliverames/.claude`. Default dispatch pattern: headless + tmux.

**Tech Stack:** Markdown skill files, no code. References Claude Code CLI and `~/.claude` filesystem internals.

**Spec:** `docs/superpowers/specs/2026-03-17-claude-code-headless-design.md`

> **Parallelization:** Tasks 1, 2, and 3 are independent reference files and can be implemented in parallel. Task 4 (SKILL.md) depends on all three being complete. Tasks 5 and 6 depend on Task 4.

---

### Task 1: Create `data/cli-reference.md` — Complete CLI Flag Documentation

**Files:**
- Create: `skills/claude-code-headless/data/cli-reference.md`

This is a pure reference file. Build it from the `claude --help` output gathered during design.

- [ ] **Step 1: Create the CLI reference file**

Write `skills/claude-code-headless/data/cli-reference.md` with the following sections. Each section lists every flag with a one-line description and a copy-paste-ready example.

```markdown
# Claude Code CLI Reference

Complete reference for the `claude` command. All examples use absolute paths.

## Execution Modes

| Flag | Description |
|------|-------------|
| `-p, --print` | Non-interactive mode — print response and exit. Required for headless dispatch. |
| `-c, --continue` | Continue the most recent conversation in the current directory. |
| `-r, --resume [value]` | Resume a conversation by session ID, or open interactive picker. |
| `--fork-session` | When resuming, create a new session ID instead of reusing the original. Use with --resume or --continue. |
| `--from-pr [value]` | Resume a session linked to a PR by number/URL, or open interactive picker. |
| `--session-id <uuid>` | Use a specific session ID for the conversation (must be a valid UUID). |

### Examples

Fire-and-forget task:
\`\`\`bash
cd /Users/oliverames/Developer/my-project && claude -p "Fix the typo in README.md" --tmux --permission-mode dontAsk
\`\`\`

Continue most recent session:
\`\`\`bash
cd /Users/oliverames/Developer/my-project && claude --continue
\`\`\`

Resume a specific session:
\`\`\`bash
claude --resume abc123-def456
\`\`\`

Resume and fork (new conversation branch):
\`\`\`bash
claude --resume abc123-def456 --fork-session
\`\`\`

## Output Format

| Flag | Description |
|------|-------------|
| `--output-format <format>` | "text" (default), "json" (single result), or "stream-json" (realtime streaming). --print only. |
| `--input-format <format>` | "text" (default) or "stream-json" (realtime streaming input). --print only. |
| `--include-partial-messages` | Include partial message chunks as they arrive. --print + --output-format=stream-json only. |
| `--replay-user-messages` | Re-emit user messages from stdin back on stdout. --input-format=stream-json + --output-format=stream-json only. |

### Examples

Capture JSON result (no --tmux):
\`\`\`bash
cd /Users/oliverames/ && claude -p "List installed plugins" --output-format json --permission-mode dontAsk > /tmp/cc-result.json
\`\`\`

Stream JSON output:
\`\`\`bash
cd /Users/oliverames/ && claude -p "Analyze this codebase" --output-format stream-json --permission-mode dontAsk
\`\`\`

## Permissions & Tool Control

| Flag | Description |
|------|-------------|
| `--permission-mode <mode>` | "acceptEdits", "bypassPermissions", "default", "dontAsk", "plan", or "auto". |
| `--allowedTools <tools...>` | Comma or space-separated list of tool names to allow (e.g. "Bash(git:*) Edit"). |
| `--disallowedTools <tools...>` | Comma or space-separated list of tool names to deny. |
| `--tools <tools...>` | Specify available tools: "" (disable all), "default" (all), or specific names. |
| `--dangerously-skip-permissions` | Bypass all permission checks. Sandboxes with no internet only. |

### Examples

Read-only research task:
\`\`\`bash
cd /Users/oliverames/Developer/my-project && claude -p "Summarize the architecture" --tmux --permission-mode dontAsk --allowedTools "Read,Grep,Glob"
\`\`\`

Full edit access with Oliver's pre-configured permissions:
\`\`\`bash
cd /Users/oliverames/Developer/my-project && claude -p "Refactor auth module" --tmux --permission-mode dontAsk
\`\`\`

## Model Selection

| Flag | Description |
|------|-------------|
| `--model <model>` | Model alias ("sonnet", "opus") or full name ("claude-sonnet-4-6"). |
| `--fallback-model <model>` | Automatic fallback when default model is overloaded. --print only. |
| `--betas <betas...>` | Beta headers for API requests. API key users only. |

### Examples

Cost-conscious task:
\`\`\`bash
cd /Users/oliverames/ && claude --model sonnet -p "Add docstrings to all public functions" --tmux --permission-mode dontAsk
\`\`\`

With fallback:
\`\`\`bash
cd /Users/oliverames/ && claude -p "Complex refactor" --fallback-model sonnet --tmux --permission-mode dontAsk
\`\`\`

## System Prompt & Context

| Flag | Description |
|------|-------------|
| `--system-prompt <prompt>` | Override the default system prompt entirely. |
| `--append-system-prompt <prompt>` | Append to the default system prompt (preserves defaults). |
| `--agent <agent>` | Agent for the current session. Overrides the "agent" setting. |
| `--agents <json>` | JSON object defining custom agents. |

### Examples

Specialized task with custom context:
\`\`\`bash
cd /Users/oliverames/ && claude -p "Draft a blog post about SwiftUI" --append-system-prompt "Write in Oliver's voice. Keep it concise and technical." --tmux --permission-mode dontAsk
\`\`\`

## Directory & Project

| Flag | Description |
|------|-------------|
| `--add-dir <directories...>` | Additional directories to allow tool access to. |
| `--plugin-dir <path>` | Load plugins from a directory for this session only (repeatable). |
| `-w, --worktree [name]` | Create a new git worktree for this session. |
| `--tmux` | Create a tmux session for the worktree. Uses iTerm2 native panes when available. |

### Examples

Task needing git isolation:
\`\`\`bash
cd /Users/oliverames/Developer/my-project && claude -p "Experimental refactor of the database layer" --worktree --tmux --permission-mode dontAsk
\`\`\`

Task needing access to multiple directories:
\`\`\`bash
cd /Users/oliverames/Developer/frontend && claude -p "Update API types to match backend" --add-dir /Users/oliverames/Developer/backend --tmux --permission-mode dontAsk
\`\`\`

## Settings & Misc

| Flag | Description |
|------|-------------|
| `--settings <file-or-json>` | Path to settings JSON file or JSON string for additional settings. |
| `--setting-sources <sources>` | Comma-separated setting sources to load (user, project, local). |
| `--disable-slash-commands` | Disable all skills. |
| `--effort <level>` | Effort level: low, medium, high, max. |
| `--json-schema <schema>` | JSON Schema for structured output validation. |
| `--max-budget-usd <amount>` | Maximum dollar amount for API calls. --print only. |
| `-n, --name <name>` | Display name for this session (shown in /resume and terminal title). |
| `--no-session-persistence` | Disable session persistence. --print only. |

### Examples

Budget-capped exploration:
\`\`\`bash
cd /Users/oliverames/ && claude -p "Research best practices for X" --max-budget-usd 1.00 --permission-mode dontAsk
\`\`\`

Named session for easy identification:
\`\`\`bash
cd /Users/oliverames/Developer/my-project && claude -p "Fix auth bug" --tmux --name "auth-fix" --permission-mode dontAsk
\`\`\`

## Debugging

| Flag | Description |
|------|-------------|
| `-d, --debug [filter]` | Debug mode with optional category filtering (e.g. "api,hooks"). |
| `--debug-file <path>` | Write debug logs to a specific file (implicitly enables debug). |
| `--verbose` | Override verbose mode setting from config. |

### Examples

Debug a failing task with log capture:
\`\`\`bash
cd /Users/oliverames/Developer/my-project && claude -p "Why is the build failing?" --debug-file /tmp/cc-debug.log --permission-mode dontAsk
\`\`\`

Debug with category filtering:
\`\`\`bash
cd /Users/oliverames/Developer/my-project && claude -p "Fix test failures" --debug "api,hooks" --tmux --permission-mode dontAsk
\`\`\`

## Subcommands

| Command | Description |
|---------|-------------|
| `claude mcp list` | List configured MCP servers. |
| `claude mcp add <name> <cmd> [args]` | Add an MCP server. |
| `claude mcp get <name>` | Get MCP server details. |
| `claude mcp remove <name>` | Remove an MCP server. |
| `claude plugin` | Manage plugins. |
| `claude auth` | Manage authentication. |
| `claude doctor` | Check auto-updater health. |
| `claude update` | Check for and install updates. |
```

- [ ] **Step 2: Review the file**

Read the file back and verify:
- Every flag from `claude --help` is documented
- All examples use absolute paths (no `~`)
- Examples use `--permission-mode dontAsk` where appropriate
- No secrets or env values appear in examples

- [ ] **Step 3: Commit**

```bash
git add skills/claude-code-headless/data/cli-reference.md
git commit -m "feat(claude-code-headless): add CLI reference doc"
```

---

### Task 2: Create `data/filesystem-map.md` — Directory Structure & JSON Schemas

**Files:**
- Create: `skills/claude-code-headless/data/filesystem-map.md`

Reference file documenting the complete `~/.claude` directory structure. Build from the exploration data gathered during design.

- [ ] **Step 1: Gather current directory structure**

Read the following files to extract current schemas and structure:
- `/Users/oliverames/.claude/settings.json` — read the `permissions`, `hooks`, `enabledPlugins`, and `statusLine` sections (skip `env` values)
- `/Users/oliverames/.claude/plugins/installed_plugins.json` — read to document v2 format
- Glob `/Users/oliverames/.claude/hooks/*` — list hook scripts
- Glob `/Users/oliverames/.claude/projects/*` — understand project directory encoding
- Glob `/Users/oliverames/.claude/plugins/.install-manifests/*` — document manifest format

- [ ] **Step 2: Write the filesystem map**

Write `skills/claude-code-headless/data/filesystem-map.md` with these sections:

1. **Directory Tree** — ASCII tree of `/Users/oliverames/.claude/` with one-line purpose for each entry
2. **settings.json Schema** — Field-by-field documentation of every top-level key. For `env`, document only that it exists and contains secrets — never list key names or values.
3. **installed_plugins.json Schema** — v2 format with example entry structure (version, scope, installPath, installedAt, lastUpdated, gitCommitSha)
4. **Plugin Cache Structure** — `/Users/oliverames/.claude/plugins/cache/<source>/<name>/<version>/` layout, sources (claude-plugins-official, ames-claude, apple-hig-skills, anthropic-agent-skills)
5. **Install Manifests** — `.install-manifests/<name>@<source>.json` format and purpose
6. **Projects Directory** — URL-encoded path convention, per-project structure (CLAUDE.md, memory/, sessions)
7. **Hooks Directory** — List of hook scripts with one-line descriptions (do not include full source)
8. **Skills Directory** — Structure of installed standalone skills

- [ ] **Step 3: Review the file**

Read back and verify:
- No secret values appear anywhere
- All paths are absolute
- JSON schema examples are accurate to the real files
- URL-encoding convention for project paths is explained

- [ ] **Step 4: Commit**

```bash
git add skills/claude-code-headless/data/filesystem-map.md
git commit -m "feat(claude-code-headless): add filesystem map reference"
```

---

### Task 3: Create `data/safety-guardrails.md` — Hook System & Safety Reference

**Files:**
- Create: `skills/claude-code-headless/data/safety-guardrails.md`

Reference file documenting safety boundaries. Build from the hook script analysis gathered during design.

- [ ] **Step 1: Read the hook scripts for current patterns**

Read:
- `/Users/oliverames/.claude/hooks/block-dangerous-commands.js` — extract pattern categories and safety levels
- `/Users/oliverames/.claude/hooks/protect-secrets.js` — extract file patterns and command patterns
- `/Users/oliverames/.claude/hooks/auto-stage.js` — extract trigger type (PostToolUse) and purpose
- `/Users/oliverames/.claude/hooks/notify-brrr.js` — extract trigger type (Notification/Stop) and purpose

- [ ] **Step 2: Write the safety guardrails file**

Write `skills/claude-code-headless/data/safety-guardrails.md` with these sections:

1. **File Safety Matrix** — Table with columns: Path/Pattern, Safe to Read?, Safe to Write?, Notes
2. **Hook System Overview** — How hooks work (PreToolUse, PostToolUse, Notification, Stop), configured in settings.json
3. **block-dangerous-commands.js** — Three safety levels (critical, high, strict) with pattern categories (not full regex). What gets blocked at the current "high" level.
4. **protect-secrets.js** — File patterns and bash command patterns that trigger blocks. What the allowlist is (*.example, *.sample, etc.).
5. **Permission Model** — How dontAsk mode works, allow/deny lists, how hooks interact with permissions
6. **Recovery** — What to do if settings.json gets corrupted (restore from backup, use `claude doctor`)
7. **Rules for CoWork** — Summary list of do's and don'ts:
   - Never read `settings.json` → `env` values
   - Never read settings.json in full (use targeted field reads)
   - Never modify hook scripts directly
   - Validate JSON after any settings.json edit
   - Never include secrets in dispatched prompts
   - Never force-push to main/master

- [ ] **Step 3: Review the file**

Read back and verify:
- No actual regex patterns are exposed (use category descriptions instead)
- No secrets or key names listed
- Recovery steps are accurate
- Rules are clear and actionable

- [ ] **Step 4: Commit**

```bash
git add skills/claude-code-headless/data/safety-guardrails.md
git commit -m "feat(claude-code-headless): add safety guardrails reference"
```

---

### Task 4: Create `SKILL.md` — Main Skill File

**Files:**
- Create: `skills/claude-code-headless/SKILL.md`

This is the core deliverable — the decision-tree operator guide that gets loaded when the skill triggers.

- [ ] **Step 1: Write the SKILL.md frontmatter and environment section**

```markdown
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

Operate Oliver's local Claude Code instance programmatically. This skill teaches you
how to inspect state, dispatch headless tasks, modify configuration, and manage sessions.

## Environment

- **Claude Code config:** `/Users/oliverames/.claude/`
- **Home directory:** `/Users/oliverames/`
- **Platform:** macOS (local only)
- **Default dispatch:** All tasks run headless (`-p`) with tmux (`--tmux`)
- **Always use absolute paths.** Never use `~` — it may not resolve outside a shell.
```

- [ ] **Step 2: Write Section 2 — Introspection (Read State)**

The introspection table from the spec, with how-to instructions for each item. Include a note to read `data/filesystem-map.md` for full directory structure details.

Key items:
- Installed plugins → `Read /Users/oliverames/.claude/plugins/installed_plugins.json`
- Settings & permissions → `Read /Users/oliverames/.claude/settings.json` (targeted fields only — skip `env`)
- Enabled plugins → Check `enabledPlugins` in settings.json
- Project memory → `Read /Users/oliverames/.claude/projects/<url-encoded-path>/memory/MEMORY.md`
- Project instructions → `Read /Users/oliverames/.claude/projects/<url-encoded-path>/CLAUDE.md`
- Recent sessions → Read session files in `/Users/oliverames/.claude/projects/<url-encoded-path>/`
- Hook configuration → Check `hooks` object in settings.json
- **env values → DO NOT READ.** Contains plaintext API keys. Check key names only if needed.

- [ ] **Step 3: Write Section 3 — Task Dispatch**

The directory selection decision tree, tiered dispatch patterns, defaults, and optional flags. This is the longest section.

Must include:
- Directory selection decision tree with mandatory user confirmation
- Directory search pattern (ask permission, search, present options, confirm)
- Fire-and-forget pattern (with `--tmux`)
- Capture-result pattern (without `--tmux`, with `> /tmp/` redirect)
- Session management pattern (with `--session-id` or discovery)
- Incompatibility note: `--tmux` + stdout redirect don't mix
- Default flags table
- Optional flags table
- Pointer to `data/cli-reference.md`

- [ ] **Step 4: Write Section 4 — Configuration (Modify State)**

The configuration table from the spec with caution levels. Include:
- Plugin install requires 3 artifacts (installed_plugins.json + cache + .install-manifests)
- JSON validation warning after settings.json edits
- Never modify hook scripts directly
- Pointer to `data/safety-guardrails.md`

- [ ] **Step 5: Write Section 5 — Session Management**

The session management table from the spec. Include:
- `--continue`, `--resume`, `--fork-session`, `--from-pr`
- tmux session monitoring: `tmux list-sessions`, `tmux capture-pane`
- Session ID discovery from project session files
- Pointer to `data/cli-reference.md`

- [ ] **Step 6: Write Section 6 — Safety & Guardrails**

Quick-reference safety rules:
- What's safe to read (everything except env values)
- What's safe to write (settings.json with care, memory, project CLAUDE.md)
- What's never safe to write (hook scripts, plugin cache directly, session files)
- Secret handling rules
- Active hooks summary
- Pointer to `data/safety-guardrails.md`

- [ ] **Step 7: Review the complete SKILL.md**

Read the full file and verify:
- Frontmatter is valid YAML
- Description triggers match the spec
- All paths are absolute (no `~`)
- No secrets or env values anywhere
- Decision trees are clear and unambiguous
- Tiered dispatch patterns are correct (especially tmux vs. redirect)
- File is ~300-400 lines
- Data file pointers use correct relative paths

- [ ] **Step 8: Commit**

```bash
git add skills/claude-code-headless/SKILL.md
git commit -m "feat(claude-code-headless): add main skill file"
```

---

### Task 5: Update Project Files

**Files:**
- Modify: `CLAUDE.md` (add skill to skills table/count)

- [ ] **Step 1: Update CLAUDE.md**

Read `CLAUDE.md` and update:
- Increment the skills count (currently "20 personal skills")
- Add `claude-code-headless` to the skills description if there's a list

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add claude-code-headless skill to project docs"
```

---

### Task 6: Verification

- [ ] **Step 1: Verify file structure**

Glob `skills/claude-code-headless/**` and confirm:
```
skills/claude-code-headless/
├── SKILL.md
└── data/
    ├── cli-reference.md
    ├── filesystem-map.md
    └── safety-guardrails.md
```

- [ ] **Step 2: Verify SKILL.md frontmatter**

Read the first 15 lines of `skills/claude-code-headless/SKILL.md` and confirm:
- `name:` is "Claude Code Headless"
- `description:` contains trigger phrases
- YAML is valid (no tabs, proper quoting)

- [ ] **Step 3: Verify no secrets leaked**

Search all 4 files for patterns that might be secrets:
```bash
grep -r "API_KEY\|TOKEN\|SECRET\|PASSWORD\|sk-\|ghp_" skills/claude-code-headless/
```
Expected: no matches (or only references to key names in safety docs, never values)

- [ ] **Step 4: Verify data file references**

Read SKILL.md and confirm every `data/` pointer references an existing file.

- [ ] **Step 5: Final commit if any fixes needed**

```bash
git add -A skills/claude-code-headless/
git commit -m "fix(claude-code-headless): verification fixes"
```
