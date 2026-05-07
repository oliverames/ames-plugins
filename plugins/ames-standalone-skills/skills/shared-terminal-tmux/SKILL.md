---
name: shared-terminal-tmux
description: >-
  Bridges a Terminal.app window and Claude's Bash tool onto the same tmux
  pane so both Claude and the user can read and write in real time.
  Enables human-in-the-loop interaction (passwords, Touch ID, SSH
  interactive auth, live debugging).
when_to_use: >-
  User wants a shared interactive terminal both Claude and the user can
  see. Triggers for: "open a terminal we can both use", "shared terminal",
  "can you see my terminal", "give me a terminal you can drive", "I need
  to type a password and you watch", "interactive handoff", "tmux bridge",
  "attach to my session", or any task that needs human-in-the-loop
  interaction. Also use when a Bash tool call can't proceed because it
  would need to answer an interactive prompt.
---

# Shared Terminal via tmux

Bridges a Terminal.app window and Claude's Bash tool onto the same tmux pane.
The user types normally, Claude drives via `tmux send-keys` and reads via
`tmux capture-pane`. Neither side is more "real" than the other; both are
tmux clients.

## When to use

- The user needs to enter a password or answer a Touch ID / 2FA prompt that
  Claude's non-interactive Bash tool can't satisfy.
- SSH to a host that only accepts keyboard-interactive auth (no pre-placed
  key). Example: UniFi OS devices, new VPS provisioning flows.
- Claude needs to "watch" the user perform a GUI-adjacent task and react
  (e.g., user runs a long-running build, Claude reads the failure output and
  suggests the next step).
- Claude wants to dictate exact commands for the user to review and run
  without copy-paste friction.

## When NOT to use

- The command works non-interactively (just run it via Bash directly).
- The user wants pure automation with no human input (keep using Bash).
- The task is sensitive enough that Claude writing into the user's live
  terminal is a footgun (Claude injects keystrokes exactly as if the user
  typed them). Confirm intent before driving destructive commands.

## Prerequisites

tmux must be installed. On macOS:

```bash
brew install tmux
tmux -V   # expect 3.x+
```

## Setup

```bash
# Kill any stale session with the same name
tmux kill-session -t shared 2>/dev/null

# Create detached session (size is a starting hint; tmux auto-resizes to the
# smallest attached client, so this just affects the initial pane)
tmux new-session -d -s shared -x 180 -y 48

# Send a banner the user will see on attach
tmux send-keys -t shared "clear && echo '=== shared tmux session ==='" Enter

# Pop a Terminal.app window attached to the session
osascript <<'OSA'
tell application "Terminal"
    activate
    do script "tmux attach -t shared"
end tell
OSA
```

## Claude's interaction

```bash
# Send a command (include Enter to execute, omit to leave text on prompt)
tmux send-keys -t shared "ls -la" Enter

# Read current pane contents
tmux capture-pane -t shared -p

# Read with full scrollback (useful after long-running commands)
tmux capture-pane -t shared -S - -p

# Send only control keys (no Enter needed)
tmux send-keys -t shared C-c          # Ctrl-C
tmux send-keys -t shared C-d          # Ctrl-D / EOF
tmux send-keys -t shared Escape       # ESC
```

After any `send-keys` call that runs a command, sleep briefly (0.3-1.0 s
depending on command speed) before `capture-pane` so the output has time to
land. Very fast commands can need as little as 0.2 s; network calls or builds
need much longer.

## User's interaction

User types normally in the Terminal.app window. Nothing special needed.
Anything Claude sends shows up as if typed at the prompt. Anything the user
types is visible to Claude via `capture-pane`.

## Remote attach (from other machines)

Any process running as the same UNIX user on the same host can attach to
the session. The socket lives at `/private/tmp/tmux-$UID/default` and is
keyed to UID, not TTY or terminal emulator. That means many additional
clients (browser, phone, other laptop, jumphost) can join the same pane.

### Via ttyd (web, if provisioned)

If the host runs ttyd behind a tunnel (example: Oliver's
`terminal.amesvt.com` via Cloudflare Tunnel, ttyd LaunchAgent on MBP,
password in 1Password as "ttyd terminal — Mac"; see
`ref_infrastructure.md`):

1. Browse to the ttyd URL.
2. Authenticate.
3. At the shell prompt: `tmux attach -t shared`

Works from any device with a browser. No firewall holes, no key material
needed on the client.

### Via SSH (Tailscale or LAN)

```bash
# Attach in one command; -t forces a PTY so tmux has a TTY
ssh -t oliverames@<host> tmux attach -t shared
```

Or interactively:

```bash
ssh oliverames@<host>
tmux attach -t shared
```

### Via a jumphost

```bash
# From inside the jumphost shell
ssh -t oliverames@<mbp-host> tmux attach -t shared
```

### Remote-client gotchas

- **Pane clips to the smallest client.** A 60x30 iPhone browser shrinks
  the entire pane (including Claude's view) to 60x30 until it detaches.
  Resize the narrower terminal first, or detach it.
- **`attach` shares, `attach -d` evicts.** Plain `tmux attach -t shared`
  adds another client peer-style. `tmux attach -dt shared` detaches every
  other client first; useful for clearing a half-disconnected SSH ghost
  that's still holding the pane small.
- **Clean detach.** `Ctrl-b d` detaches one client without killing the
  session. Only `tmux kill-session -t shared` tears it down for everyone.
- **UID must match.** SSHing in as a different user lands on a different
  tmux socket path; `-t shared` won't find the session. Log in as the
  same user that created it.

## Coordination protocol

tmux send-keys injects as if the attached TTY typed them, which races with
anything the user is actively typing. Avoid simultaneous input:

- **Claude-driven mode:** Claude sends commands, user watches and confirms.
  Best for "let me show you what to run."
- **User-driven mode:** User types, Claude watches via periodic
  capture-pane. Best for "you're debugging, I'll narrate."
- **Handoff mode:** Alternate explicitly. "Your turn" / "my turn."

Never interleave without explicit handoff; keystrokes will interleave and
produce garbage command lines.

## Inspecting session state

```bash
# All tmux sessions + attached client count
tmux list-sessions

# Clients attached to 'shared' (TTY + window size)
tmux list-clients -t shared

# Current pane dimensions (useful when output looks wrapped)
tmux display-message -t shared -p '#{pane_width}x#{pane_height}'
```

If the user wants wider output, they resize the Terminal.app window; tmux
auto-resizes the pane on the next refresh.

## Teardown

Either side can kill the session:

```bash
tmux kill-session -t shared
```

User's Terminal.app window will then show `[exited]` and can be closed.

## Gotchas

- **Pane size clips to smallest client.** If Claude's setup used 180x48 but
  the user's Terminal.app window is 80x24, the pane runs at 80x24. Resize
  the window if you need more columns.
- **Scrollback is limited** (default 2000 lines). For a persistent log, run
  `script /tmp/session.log` inside the pane, or bump scrollback in the
  setup: `tmux new-session -d -s shared \; set-option -g history-limit 50000`.
- **ANSI escape codes in capture.** `capture-pane -p` strips colors by
  default; pass `-e` to preserve them if needed. Usually cleaner without.
- **Send-keys escape rules.** `$`, backticks, and `"` inside the quoted
  command need proper shell escaping since the string is evaluated twice
  (once by your shell, once by tmux). Prefer single quotes for literal
  strings, or heredocs via an intermediate file.
- **Multiple windows/panes.** This skill assumes one pane in one window.
  If the user splits or creates new windows in the session, target specific
  panes with `-t shared:<window>.<pane>` instead of `-t shared`.
- **Don't drive destructive commands without confirmation.** Claude can
  type `rm -rf` just as easily as `ls`. Treat shared-terminal driving the
  same as other risky-action rules: confirm before destructive operations,
  especially with the same mental model you'd apply if you were running the
  command yourself.
- **tmux socket ownership.** Sessions live in `/private/tmp/tmux-$(id -u)/`
  and are per-user. Both sides must be running as the same user for the
  `-t shared` shortcut to find the session.

## Example: SSH to a password-only host

User needs to add an SSH key to a UniFi UDM Pro which only accepts
interactive password auth. Claude can't type the password; user shouldn't
have to retype every key-append command.

```
Claude: sets up shared session, opens Terminal.app
User:   in Terminal.app, types: ssh root@192.168.1.1
        Enters password interactively
User:   "I'm in, go ahead"
Claude: tmux send-keys -t shared "echo 'ssh-ed25519 AAAA...foo SSH Key - MacBook Pro' >> /mnt/data/ssh/authorized_keys" Enter
Claude: capture-pane, reads exit status
Claude: "confirmed, try the second one now" (or continues driving)
User:   "done" / "looks good"
Claude: tmux kill-session -t shared
```

The user retains full control; Claude is a second pair of hands with the
exact command strings pre-loaded.
