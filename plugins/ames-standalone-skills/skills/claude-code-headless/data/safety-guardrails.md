# Safety Guardrails — Hook System & Configuration Boundaries

Reference for CoWork agents interacting with a local Claude Code installation. Follow these rules exactly to avoid breaking the installation or leaking secrets.

---

## 1. File Safety Matrix

| Path / Pattern | Safe to Read? | Safe to Write? | Notes |
|---|---|---|---|
| `/Users/oliverames/.claude/settings.json` (full file) | No | With care | Contains plaintext API keys in the `env` object. Never read the full file. Use targeted field reads only. Always validate JSON before saving. |
| `/Users/oliverames/.claude/settings.json` → `env` object | No | No | Contains all API keys. Never read or modify this field. |
| `/Users/oliverames/.claude/plugins/installed_plugins.json` | Yes | With care | Plugin registry. Safe to read. Edits must be valid JSON; malformed JSON will break plugin loading. |
| `/Users/oliverames/.claude/hooks/*.js` | Yes | No | Hook scripts. Read to understand behavior. Never modify directly — configure hooks via `settings.json` instead. |
| `/Users/oliverames/.claude/plugins/cache/ames-plugins/**` | Yes | No | Plugin cache. Read-only. Content is managed by sync-skills. |
| `/Users/oliverames/.claude/projects/**` (project memory) | Yes | With care | Per-project memory files. Safe to read. Edits should be plain text additions, not destructive replacements. |
| `CLAUDE.md` files in project directories | Yes | Yes | Project-scoped instructions. Safe to read and update. |
| `/Users/oliverames/.claude/sessions/**` | Yes | No | Session logs. Read-only. Do not modify. |
| `/Users/oliverames/.claude/.install-manifests/**` | Yes | No | Sync manifests. Read-only. Managed by sync script. |

---

## 2. Hook System Overview

Hooks are scripts that Claude Code runs automatically at defined lifecycle points. They are configured in the `hooks` object of `/Users/oliverames/.claude/settings.json`.

**Four event types:**

| Event | When it fires | Can block tool execution? |
|---|---|---|
| `PreToolUse` | Before a tool runs | Yes — hook can return `permissionDecision: "deny"` |
| `PostToolUse` | After a tool completes | No — informational only |
| `Notification` | On system notifications (e.g., permission prompts) | No |
| `Stop` | When a Claude Code session ends | No |

**Hook configuration structure (in settings.json):**
Each hook entry specifies: the event type to match, an optional tool matcher, the command to execute (the script path), and optional timeout and async settings.

**Hook execution:** Hooks run as Node.js scripts. They receive a JSON payload on stdin describing the event, and write a JSON response to stdout. For PreToolUse hooks, a `permissionDecision: "deny"` response blocks the tool call and surfaces the reason to Claude.

**Log location:** All hook activity is logged to `/Users/oliverames/.claude/hooks-logs/` as daily `.jsonl` files.

---

## 3. block-dangerous-commands.js

**Event:** `PreToolUse` — runs before every `Bash` tool call.
**Current safety level:** `high` — critical and high patterns block; strict patterns are not active.

### Critical (blocks at all safety levels)
Operations that are catastrophic and unrecoverable:
- `rm` targeting the home directory, `$HOME`, root filesystem (`/`), or system directories (`/etc`, `/usr`, `/var`, etc.)
- `rm` deleting current directory contents (`.` or `*`)
- `dd` writing directly to a disk device
- `mkfs` formatting a disk partition
- Fork bomb shell patterns

### High (blocks at "high" and "strict" levels — currently active)
Operations with significant risk of data loss or security exposure:
- Piping a URL directly into a shell (remote code execution risk)
- `git push --force` to `main` or `master` (without `--force-with-lease`)
- `git reset --hard` (loses uncommitted work)
- `git clean -f` (deletes untracked files)
- `chmod 777` on any path (security risk)
- Reading `.env` files via shell commands
- Reading credential or key files via shell commands
- Dumping all environment variables (`printenv`, bare `env`)
- Echoing secret-named variables to stdout
- Docker volume deletion or pruning
- Deleting SSH keys

### Strict (not active at current "high" level — logged only)
Operations that are context-dependent and cautionary:
- `git push --force` to any branch (without `--force-with-lease`)
- `git checkout .` (discards all working directory changes)
- `sudo rm` (elevated privilege deletion)
- Docker system or image pruning
- `crontab -r` (removes all cron jobs)

---

## 4. protect-secrets.js

**Event:** `PreToolUse` — runs before `Read`, `Edit`, `Write`, and `Bash` tool calls.
**Current safety level:** `high` — critical and high patterns block; strict patterns are not active.

### Allowlist (always permitted, even if pattern matches)
Template and example env files are explicitly safe:
- `.env.example`, `.env.sample`, `.env.template`, `.env.schema`, `.env.defaults`
- `env.example`, `example.env`

### File path patterns (for Read, Edit, Write tools)

**Critical — blocks at all safety levels:**
- `.env` files and `.envrc` (direnv)
- SSH private key files (`~/.ssh/id_*`, files named `id_rsa`, `id_ed25519`, `id_ecdsa`, `id_dsa`)
- SSH `authorized_keys`
- AWS credentials and config files (`~/.aws/credentials`, `~/.aws/config`)
- Kubernetes config (`~/.kube/config`)
- PEM, `.key`, PKCS12 (`.p12`, `.pfx`) key files

**High — blocks at "high" and "strict" levels (currently active):**
- Generic `credentials.json` files
- Secrets configuration files (JSON, YAML, TOML named `secrets` or `credentials`)
- GCP service account JSON files
- GCloud credentials and token files
- Azure credentials and access token files
- Docker config (may contain registry auth)
- `.netrc`, `.npmrc`, `.pypirc`, `.gem/credentials`
- Vault token files
- Java keystores (`.keystore`, `.jks`)
- `.htpasswd` and `.pgpass` password files
- MySQL config files (`.my.cnf`)

**Strict — not active at current "high" level:**
- Database config files that may contain passwords
- SSH `known_hosts` (reveals infrastructure)
- `.gitconfig` (may contain credentials)
- `.curlrc` (may contain auth)

### Bash command patterns (for Bash tool)

**Critical — blocks at all safety levels:**
- Reading `.env` files via `cat`, `less`, `head`, `tail`, `more`, `bat`, or `view`
- Reading SSH private key files via shell commands
- Reading AWS credentials via shell commands

**High — blocks at "high" and "strict" levels (currently active):**
- Dumping all environment variables (`printenv`, bare `env`)
- `echo` or `printf` of variables with secret-like names (SECRET, KEY, TOKEN, PASSWORD, CREDENTIAL, API_KEY, AUTH, PRIVATE)
- Reading secrets/credentials config files (JSON, YAML, TOML) via shell commands
- Reading `.netrc` or `.npmrc` via shell commands
- Sourcing `.env` files (loads secrets into the shell)
- Exporting secrets from `.env` via command substitution
- Uploading secrets via `curl` (`-d @file`, `--data @file`, `-F @file`)
- POSTing secrets via `curl` or `wget`
- Copying secrets via `scp` or `rsync` to a remote host
- Exfiltrating secrets via `netcat`
- Copying, moving, or deleting `.env` files, SSH keys, or AWS credentials
- Truncating secrets files
- Reading `/proc/*/environ` (process environment)
- Reading `.env` via `xargs` or `find -exec`

**Strict — not active at current "high" level:**
- Recursive `grep` for password, secret, API key, token, or credential strings
- Base64 encoding of secrets files

---

## 5. Permission Model

Claude Code supports a `dontAsk` (auto-approve) permission mode configured via the `projects` section of `settings.json`.

**How it works:**
- The `allow` list in the project config enumerates tools and patterns that are pre-approved.
- When `dontAsk` mode is active and a tool call matches an allow pattern, it executes immediately without prompting.
- If a tool call does NOT match any allow pattern, it is denied without an interactive prompt — there is no fallback to asking the user.
- Hooks run BEFORE the permission check for `PreToolUse` events. A hook can deny a tool call even if it would otherwise be allowed by the permission config.

**Implication for headless/CoWork use:** The agent must know which tools are in the allow list before dispatching tasks. Attempting an unapproved tool will silently fail.

---

## 6. Recovery

### If settings.json becomes corrupted (malformed JSON)
- Claude Code will not start properly or will fail to load the affected configuration.
- Fix: open `/Users/oliverames/.claude/settings.json` in a text editor, locate the syntax error (look for missing commas, unmatched braces, trailing commas), and correct it.
- Validate: run `node -e "JSON.parse(require('fs').readFileSync('/Users/oliverames/.claude/settings.json', 'utf8'))"` — no output means valid JSON.

### Backup
- Run `backup-claude` (in PATH via `~/Developer/scripts/`) to back up `~/.claude/projects/`, plans, and teams to `~/Developer/archive/claude-code-backup/`.
- If the local config is severely broken, restore from the most recent backup commit in that repo.

### Diagnostics
- `claude doctor` checks auto-updater health. It is not a settings validator but is a useful first diagnostic when Claude Code behaves unexpectedly.
- Hook logs at `/Users/oliverames/.claude/hooks-logs/` show exactly what was blocked and why. Check the current day's `.jsonl` file first.

---

## 7. Rules for CoWork

### Never do these

- **Never read `settings.json` in full.** It contains plaintext API keys in the `env` object.
- **Never read or reference the `env` field** in `settings.json` under any circumstance.
- **Never modify hook scripts directly.** Configure hook behavior via `settings.json` only.
- **Never force-push to `main` or `master`.** The `block-dangerous-commands` hook will block it anyway, but do not attempt it.
- **Never include secrets, key values, or tokens in dispatched prompts or task output.**
- **Never assume the working directory.** Always confirm the target project directory with the user before dispatching a Claude Code task.

### Always do these

- **Validate JSON** after any edit to `settings.json` or `installed_plugins.json` before saving.
- **Use targeted field reads** when inspecting `settings.json` — read only the specific key needed (e.g., `hooks`, `projects.<name>.allow`), not the whole file.
- **Check hook logs** at `/Users/oliverames/.claude/hooks-logs/` if a tool call is unexpectedly blocked.
- **Bump plugin versions** in `.claude-plugin/plugin.json` whenever plugin content changes — the sync script reads the version to detect updates.
- **Run `sync-skills`** after any plugin or skill change to install locally and push to the marketplace.
