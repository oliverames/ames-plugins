---
name: 1password-vault
description: >-
  Use when working with API keys, secrets, tokens, credentials, SSH keys, or
  1Password. Triggers for: "vault this key", "store credential", "audit for
  secrets", "scan for API keys", "secure my MCP config", "rotate this token",
  "add to 1Password", "check for exposed credentials", "op://", "read from
  vault", "look up my password", or any task involving credential storage,
  retrieval, rotation, or security auditing. Also use when setting up new
  services that need API keys, when reviewing .env files, or when the user
  mentions their credentials repo. If you encounter a plaintext API key or
  secret during any task, consult this skill before proceeding.
---

# 1Password Vault Management

Oliver's credentials live in the **"Development"** vault in 1Password. You can
manage it via either the **MCP server** (preferred for interactive reads/writes
within a conversation) or the **`op` CLI** (required for scripting, piping, SSH
key templates, document items, and subprocess injection).

Oliver also maintains a `~/Developer/credentials/` repo as a working reference
for deployment configs and env files. **New secrets go to both places**: vault
them in 1Password AND add them to the appropriate file in the credentials repo.
The two systems coexist — 1Password is the secure backing store with search,
audit, and sharing capabilities, while the credentials repo holds structured
config that services and scripts read directly.

The goal: **access without exposure**. Credentials should be injected at runtime,
never stored in plaintext config files, and never passed through your context
window when avoidable.

## Service Account Authentication

A single 1Password service account token (`OP_SERVICE_ACCOUNT_TOKEN`) has full
read/write access to the Development vault. It powers both the MCP server and
the `op` CLI — no separate auth or user prompts needed.

**In Claude Code sessions**, the token is available directly as an env var:

```bash
# Available automatically in Bash tool — no loading needed
op item get "GitHub Personal Access Token" --vault Development --fields credential --reveal
```

**If the env var isn't picked up** (e.g., in a subshell or script), load it explicitly:

```bash
OP_SERVICE_ACCOUNT_TOKEN=$(python3 -c "import json; print(json.load(open('/Users/oliverames/.claude/settings.json'))['env']['OP_SERVICE_ACCOUNT_TOKEN'])")
```

**IMPORTANT:** Always use `--reveal` when reading credential field values. Without
it, `op` returns a placeholder string regardless of auth method:

```bash
# Wrong — returns "[use 'op item get ... --reveal' to reveal]"
op item get "GitHub Personal Access Token" --vault Development --fields credential

# Correct
op item get "GitHub Personal Access Token" --vault Development --fields credential --reveal
```

## 1Password MCP Server

The `@takescake/1password-mcp` MCP server is installed in `settings.json` and
inherits `OP_SERVICE_ACCOUNT_TOKEN` automatically. Use its tools for interactive
credential operations — no shell needed, cleaner than CLI for read/write tasks
inside a conversation.

### Tools

| Tool | Description |
|------|-------------|
| `vault_list` | List all accessible vaults |
| `item_lookup` | Search items by title in a vault |
| `item_delete` | Delete an item from a vault |
| `password_create` | Create a new password/login item |
| `password_read` | Retrieve a password via `op://vault/item/field` or vault+item ID |
| `password_update` | Rotate/update an existing password |
| `password_generate` | Generate a cryptographically secure random password |
| `password_generate_memorable` | Generate a memorable passphrase |

### Guided Prompts (invoke by name)

| Prompt | When to use |
|--------|-------------|
| `generate-secure-password` | Create + store a new secure password in one workflow |
| `credential-rotation` | Read → generate → update → verify rotation sequence |
| `vault-audit` | List vault items, categorize, flag concerns |
| `secret-reference-helper` | Build `op://vault/item/field` references interactively |

### When to prefer MCP vs `op` CLI

| Task | Use |
|------|-----|
| Read a credential value | MCP `password_read` |
| Create or update a credential | MCP `password_create` / `password_update` |
| Generate a password | MCP `password_generate` |
| Look up items by title | MCP `item_lookup` |
| SSH key items | CLI — MCP doesn't support SSH Key category |
| Document items (.p8, .p12, .db) | CLI — use `op document create/get` |
| Pipe a secret into a command | CLI — `op run` or `$(op item get ... --reveal)` |
| Scripting / automation | CLI — more composable |
| Audit for stray secrets | CLI — needs `grep` and filesystem access |
| `op://` reference construction | MCP `secret-reference-helper` prompt |

## settings.json Policy

`~/.claude/settings.json` holds two relevant sections:

**`env` block** — credentials available to Claude Code and all MCP servers:
- `OP_SERVICE_ACCOUNT_TOKEN` — the 1Password service account token (R/W Development vault)
- Plugin-required API keys that MCP servers need at runtime (see table below)
- Claude Code config vars (non-secret tuning knobs)

**`mcpServers` block** — directly registered MCP servers (not via plugins):
- `1password` → `npx -y @takescake/1password-mcp` (inherits `OP_SERVICE_ACCOUNT_TOKEN`)

MCP servers spawned by plugins receive env vars from the `env` block — they do not
inherit the shell environment from `.zshrc`. Any credential a plugin MCP server
needs must be present in the `env` block.

The vault is the **source of truth**. When a credential rotates, update it in
1Password first, then manually update the value in settings.json and run
`/reload-plugins`. To retrieve the current value for updating:

```bash
op item get "Item Title" --vault Development --fields credential --reveal
```

Current MCP credentials in settings.json env block:
- `OP_SERVICE_ACCOUNT_TOKEN` → 1Password service account (R/W Development vault)
- `GITHUB_PERSONAL_ACCESS_TOKEN` → "GitHub Personal Access Token"
- `GOOGLE_WORKSPACE_OAUTH_CLIENT_ID` → "Google Workspace OAuth Client ID"
- `GOOGLE_WORKSPACE_OAUTH_CLIENT_SECRET` → "Google Workspace OAuth Client Secret"
- `YNAB_API_TOKEN` → "YNAB API Token"
- `TELEGRAM_BOT_TOKEN` → "Telegram Bot Token"

## Quick Reference

```bash
# List all items
op item list --vault Development

# Get a specific item
op item get "GitHub Personal Access Token" --vault Development

# Get just the credential value (for piping, NOT for display)
op item get "GitHub Personal Access Token" --vault Development --fields credential --reveal

# Create a new item
op item create --vault Development --category "API Credential" \
  --title "Service Name API Key" \
  "credential=the-key-value" \
  "notesPlain=What this key is for and where it's used"

# Delete an item
op item delete "Item Title" --vault Development
```

## Core Principles

1. **Never display credential values** in conversation output. Use MCP `password_read`
   or `op` to store and retrieve them, piping values directly where needed.
2. **Never `cat` credential files.** Hooks block this. Use `awk -F=`, `grep`, or
   `op` to work with credentials without exposing them.
3. **Prefer `op://` references** over plaintext env vars wherever the consuming
   tool supports them.
4. **Always clean up** temp files containing credentials (`rm -f` after vaulting).

## Workflows

### Audit for Stray Credentials

Scan these locations for plaintext secrets:

| Location | What to look for |
|----------|-----------------|
| `~/.zshrc`, `~/.zprofile` | `export *_KEY=`, `export *_TOKEN=` |
| `~/Developer/**/.env*` | Any `.env`, `.env.local`, `.env.production` |
| `~/.claude/settings.json` | The `env` section |
| `~/Developer/credentials/` | Entire repo — env files, tokens.json |
| `~/.config/` | Files containing API_KEY, SECRET, TOKEN |
| `~/.netrc`, `~/.npmrc` | Embedded credentials |
| `~/Developer/scripts/` | Hardcoded keys in shell scripts |

Use `Grep` patterns to detect key names without reading values:

```bash
# Find env vars that look like real keys (not empty/placeholder)
grep -r "API_KEY\|TOKEN\|SECRET\|PASSWORD" ~/.zshrc ~/.zprofile 2>/dev/null | grep -v "^#" | awk -F= '{print $1}'
```

For each finding, assess risk:
- **HIGH**: Real keys in git-tracked files (especially with remotes)
- **MEDIUM**: Real keys in untracked plaintext files
- **LOW**: Keys in expected locations (settings.json env section)

Cross-reference findings against what's already vaulted:
```bash
op item list --vault Development --format json | python3 -c "import json,sys; [print(i['title']) for i in json.load(sys.stdin)]"
```

### Vault a New Credential

**API keys and tokens:**
```bash
op item create --vault Development --category "API Credential" \
  --title "Descriptive Name" \
  "credential=VALUE" \
  "notesPlain=Purpose, where it's used, when it was created"
```

**SSH keys** have category-specific handling. See "SSH Key Handling Caveats" below for details.

For **freshly generated** keys (1P generates the keypair internally and populates all fields correctly):

```bash
op item create --category=ssh --vault=Development \
  --title "SSH Key - ServerName (ED25519)" \
  --ssh-generate-key=ed25519
```

For **importing existing key material** (key already on disk), use the 1Password desktop GUI. The CLI has no import path, and the JSON template approach silently produces broken items that `op read` cannot address.

**Certificates (.p12, .p8):**
```bash
op document create PATH_TO_FILE \
  --vault Development \
  --title "Certificate Name" \
  --file-name "original-filename.p12"
```

After vaulting in 1Password, also add to the credentials repo:
```bash
# Add to the appropriate env/config file in ~/Developer/credentials/
# Then commit the change
cd ~/Developer/credentials && git add -A && git commit -m "Add: Service Name credential"
```

Always clean up temp files containing credentials:
```bash
rm -f /tmp/temp-credential-file
```

### Vault SSH Keys from Remote Servers

The CLI cannot import existing key material into an SSH Key item (see "SSH Key Handling Caveats" below). Two working approaches, with different tradeoffs:

**Decision rule:** if the existing on-disk public key is already registered elsewhere (GitHub deploy key, other servers' `authorized_keys`, CI system), use **Path A (GUI paste-import)** to preserve the key and avoid a coordinated rotation. If nothing external depends on the key (common for a server that's only an SSH destination, not a client), use **Path B (CLI generate + deploy)** — fully scriptable, no GUI click needed.

**Path A — GUI paste-import (preserves existing key):**

```bash
# Retrieve the key material to clipboard (hooks block direct cat; use ssh + pbcopy)
ssh home-server 'cat ~/.ssh/id_ed25519' | pbcopy
```

Then in 1Password desktop: New Item, SSH Key, paste the private key. 1P derives public key, fingerprint, and key type from the pasted material. After save, verify the item is CLI-readable:

```bash
op item get <new-uuid> --vault Development
# All four fields (public key, fingerprint, private key, key type) should show.
# If any are missing, the item is broken and must be recreated via the GUI.
```

Clear the clipboard when done:

```bash
pbcopy < /dev/null
```

**Path B — CLI generate + deploy (rotates the key, fully scriptable):**

```bash
# 1) Generate the key in 1Password
op item create --category=ssh --ssh-generate-key=ed25519 \
  --title="SSH Key - home-server (ED25519)" --vault=Development --format=json > /tmp/k.json
ITEM_ID=$(python3 -c "import json; print(json.load(open('/tmp/k.json'))['id'])")

# 2) Deploy the new private key to the remote, derive public, atomically replace the current key
op read "op://Development/$ITEM_ID/private key?ssh-format=openssh" | \
  ssh home-server 'umask 077 && cat > ~/.ssh/id_ed25519.new && chmod 600 ~/.ssh/id_ed25519.new && \
    ssh-keygen -y -f ~/.ssh/id_ed25519.new > ~/.ssh/id_ed25519.pub.new && \
    cp -p ~/.ssh/id_ed25519 ~/.ssh/id_ed25519.bak-$(date +%F) && \
    cp -p ~/.ssh/id_ed25519.pub ~/.ssh/id_ed25519.pub.bak-$(date +%F) && \
    mv ~/.ssh/id_ed25519.new ~/.ssh/id_ed25519 && \
    mv ~/.ssh/id_ed25519.pub.new ~/.ssh/id_ed25519.pub && \
    chmod 644 ~/.ssh/id_ed25519.pub'

# 3) Verify on-disk fingerprint matches 1Password's fingerprint
ssh home-server 'ssh-keygen -lf ~/.ssh/id_ed25519'
op item get "$ITEM_ID" --vault Development --fields fingerprint
rm -f /tmp/k.json
```

The private key is piped from `op read` through `ssh` stdin directly to the remote — never written to local disk. The remote derives the public key from the private via `ssh-keygen -y`, so you only transport the private once.

### SSH Key Handling Caveats

The `op` CLI has three hard limitations on SSH Key (`SSH_KEY`) category items, confirmed 2026-04-16 and 2026-04-17:

1. **Creation with existing key material fails silently.** `op item create --category=ssh` with a JSON template containing a `private_key[SSHKEY]` field accepts the input and returns a new item ID, but the resulting item is malformed. Derived fields (public key, fingerprint, key type) are not populated, and `op item get` / `op read` on any field returns `"private_key" isn't a field in the ... item`. Assignment-statement forms (`"private key[sshkey]=$PEM"`) also fail, with `"sshkey" is not a supported field type`. Adding `ssh_formats: {openssh: {value: <PEM>}}` to the template alongside `value` doesn't help either — the server still stores the item in a malformed state. Only `--ssh-generate-key=<type>` produces a valid CLI-readable item. To preserve an existing key, use Path A (GUI paste-import) from "Vault SSH Keys from Remote Servers" above. To create a healthy 1P item via CLI only, use Path B (generate + deploy), accepting a key rotation.

2. **Editing is not supported.** `op item edit <ssh-key-id>` returns `SSH Key item editing in the CLI is not yet supported`. Broken items must be deleted and recreated via GUI.

3. **Service accounts require `--vault` explicitly on every SSH Key operation.** Even when the item UUID is globally unique, service accounts otherwise fail with `a vault query must be provided when this command is called by a service account`. Pass `--vault Development` on `op item get`, `op read`, and `op item delete`.

### SSH Agent Configuration

The 1Password SSH agent reads `~/.config/1Password/ssh/agent.toml`. Two scoping modes exist:

- Vault-wide: `[[ssh-keys]] vault = "<vault-uuid>"` serves every SSH Key item in that vault.
- Per-item: `[[ssh-keys]] item = "<item-uuid>"` serves only that item.

**Always use per-item scoping.** OpenSSH's default `MaxAuthTries=6` means offering too many keys exhausts the budget before the right one is tried. A vault-wide scope on a vault with any non-client-auth keys (such as sshd host keys) will cause silent SSH auth failures that look like "Too many authentication failures" or "signing failed ... communication with agent failed".

**Never serve host keys via the agent.** Files from `/etc/ssh/ssh_host_*` are sshd identities, not client identities; sshd on any remote will reject them. If these accidentally end up in the vault, either delete them or exclude them from agent.toml.

**Reload behavior is inconsistent.** Adding items to agent.toml hot-reloads cleanly. Removing items, and especially transitions between vault-wide and per-item scope, often do not hot-reload. After a scope-type change or removal, quit 1Password fully (menu bar, Quit 1Password) and relaunch. Verify with:

```bash
SSH_AUTH_SOCK=~/Library/Group\ Containers/2BUA8C4S2C.com.1password/t/agent.sock ssh-add -l
```

**Touch ID on signing.** If 1P's Developer settings have "Require authorization to use SSH keys" enabled (default on most Macs), a Touch ID prompt appears on every signing operation. Interactive terminal sessions answer the prompt naturally. Non-interactive Bash contexts (Claude Code Bash tool, scripts, launchd jobs, cron) cannot answer it, and after the prompt times out the signing fails with `sign_and_send_pubkey: signing failed ... communication with agent failed`, followed by `Too many authentication failures`. **Use the headless pattern below as the default for automation**, not as a fallback.

### Headless SSH Pattern (Default for Automation)

**When to use:** any non-interactive SSH from Claude Code Bash, scripts, launchd agents, cron, or CI. Anywhere a Touch ID prompt cannot be answered by a human sitting at the Mac in real time.

**When NOT to use:** interactive terminal sessions where the user is at the keyboard. There the GUI agent works fine and Touch ID is transparent.

**Principle:** bypass the 1P agent entirely; pull the private key from the vault to a short-lived temp file, use it as an explicit `IdentityFile`, then delete it. The key material lives on disk only for the duration of the SSH command.

```bash
# Load service account token if not already in env
export OP_SERVICE_ACCOUNT_TOKEN=$(python3 -c "import json; print(json.load(open('/Users/oliverames/.claude/settings.json'))['env']['OP_SERVICE_ACCOUNT_TOKEN'])")

# Pull the private key from 1P to a locked-down temp file.
# The ?ssh-format=openssh query parameter ensures OpenSSH format.
# Replace <item-uuid> with the 1P item holding the client identity for this host.
KEYFILE=$(mktemp) && chmod 600 "$KEYFILE"
op read "op://Development/<item-uuid>/private key?ssh-format=openssh" > "$KEYFILE"

# SSH with -i pointing at the temp file, and -o IdentityAgent=none so ssh
# does NOT also consult the 1P agent (which would re-trigger the signing
# failure path and exhaust MaxAuthTries).
ssh -i "$KEYFILE" -o IdentitiesOnly=yes -o IdentityAgent=none home-server 'COMMAND HERE'

# Always clean up
rm -f "$KEYFILE"
```

**For repeated operations in one session**, extract the key once and reuse via a shell function:

```bash
KEYFILE=$(mktemp) && chmod 600 "$KEYFILE"
op read "op://Development/<item-uuid>/private key?ssh-format=openssh" > "$KEYFILE"
ssh_hs() { ssh -i "$KEYFILE" -o IdentitiesOnly=yes -o IdentityAgent=none home-server "$@"; }

ssh_hs 'echo step 1'
ssh_hs 'echo step 2'
# ... many commands ...

# At end of session:
rm -f "$KEYFILE"
```

**Diagnostic: you know you hit this when:**
- `ssh` reports `sign_and_send_pubkey: signing failed ... communication with agent failed`
- followed by `Too many authentication failures`
- and `ssh-add -l` against the 1P socket still shows your keys (the agent knows about them; it just can't sign them without Touch ID)

**Why `-o IdentityAgent=none` matters:** without it, `ssh` reads `~/.ssh/config`'s `IdentityAgent` directive (typically pointing at the 1P socket) and tries the agent in addition to the temp-file identity. That re-triggers the Touch ID prompt and burns through `MaxAuthTries` before `-i` is tried.

### Git Commit Signing via 1P

Commit and tag signing route through `/Applications/1Password.app/Contents/MacOS/op-ssh-sign`. Typical `~/.gitconfig`:

```
[gpg]
    format = ssh
[gpg "ssh"]
    program = /Applications/1Password.app/Contents/MacOS/op-ssh-sign
    allowedSignersFile = ~/.config/git/allowed_signers
[user]
    signingkey = ssh-ed25519 AAAAC3...<pubkey>
[commit]
    gpgsign = true
[tag]
    gpgsign = true
```

The `allowedSignersFile` lets `git log --show-signature` verify your own commits locally. Format:

```
oliver@amesvt.com ssh-ed25519 AAAAC3...<pubkey>
```

Smoke test in any throwaway repo:

```bash
git init -q tmp && cd tmp
echo x > f && git add f && git commit -q -m "sig test"
git log --show-signature -1
# Expect: Good "git" signature for <email> with ED25519 key SHA256:...
```

### Retrieve a Credential (for scripts/automation)

When a script or tool needs a credential at runtime:

```bash
# Inject into a single command
op run --env-file=.env -- your-command-here

# Or read a single value
GITHUB_TOKEN=$(op item get "GitHub Personal Access Token" --vault Development --fields credential --reveal)
```

**For .env files with `op://` references:**
```
GITHUB_TOKEN=op://Development/GitHub Personal Access Token/credential
OPENAI_API_KEY=op://Development/OpenAI API Key/credential
```

Then: `op run --env-file=.env -- your-command`

Secrets are decrypted in memory only for that process and vanish when it exits.

## Known Credential Locations

Oliver's credentials are currently spread across:

| Location | Contents | Status |
|----------|----------|--------|
| `~/.claude/settings.json` env | `OP_SERVICE_ACCOUNT_TOKEN` (R/W Development vault) + Claude Code config vars + plugin-required keys | Only service account should be permanent; others injected from vault |
| `~/.claude/settings.json` mcpServers | `1password` server (`@takescake/1password-mcp`) | Inherits token from env block |
| `~/.claude/.env` | `op://` references resolved by `op inject` at shell startup | Used by interactive shell sessions |
| `~/Developer/credentials/` | env files, tokens.json, SSH keys, certs | Git repo with GitHub remote |
| `~/.ssh/` | ED25519 key pair | Standard location |
| Remote: home-server `~/.ssh/` | ED25519 key pair | Vaulted |

## SSH Alias

The Mac Mini server is accessible via `ssh home-server` (configured in
`~/.ssh/config`). Always use this alias, not the raw IP address.

## `op://` Secret Reference Syntax

Format: `op://<vault>/<item>/[section/]<field>[?query]`

- Case-insensitive, supports alphanumeric + hyphens + underscores + periods + spaces
- Whitespace in references requires quoting: `"op://Development/My Item/field"`
- Use item ID instead of title if the title has unsupported characters
- SSH keys: append `?ssh-format=openssh` to get OpenSSH format
- OTP fields: append `?attr=otp` to get the current TOTP code

Examples:
```
op://Development/GitHub Personal Access Token/credential
op://Development/SSH Key - Mac Mini home-server (ED25519)/private key?ssh-format=openssh
```

## `op item create` — Sensitive Values

Command arguments are visible to other processes on the machine. For sensitive
values, prefer the JSON template pipe approach over assignment statements:

```bash
# SAFER: pipe via JSON template (value not visible in process list)
op item template get "API Credential" | python3 -c "
import json, sys
t = json.load(sys.stdin)
t['title'] = 'New Service Key'
for f in t['fields']:
    if f['id'] == 'credential': f['value'] = 'THE_SECRET_VALUE'
    if f['id'] == 'notesPlain': f['value'] = 'Description of this key'
print(json.dumps(t))
" | op item create --vault Development --format json -

# OK for non-sensitive metadata only
op item create --vault Development --category "API Credential" \
  --title "Name" "notesPlain=description"
```

**File attachments** (use `op document create`, not assignment statements):
```bash
op document create /path/to/cert.p12 \
  --vault Development \
  --title "Certificate Name" \
  --file-name "cert.p12"
```

## Safety Rules

- **Never output credential values** to the conversation. If the user asks to
  "show me the key", explain that you can vault it or pipe it to a command, but
  displaying it in chat creates a record in conversation history.
- **Hooks will block** `cat` on files matching credential patterns. This is
  intentional. Work around it with `op`, `awk`, or `scp` + vault workflows.
- **Dual storage: always store in both places.** New secrets go to 1Password
  vault AND `~/Developer/credentials/` repo. The vault provides secure search
  and audit; the credentials repo provides structured config for services.
