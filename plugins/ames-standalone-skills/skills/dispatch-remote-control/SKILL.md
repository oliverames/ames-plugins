---
name: dispatch-remote-control
description: >-
  Starts a new Claude Code session with remote-control activated so Oliver
  can drive it from his phone or a secondary device.
when_to_use: >-
  Oliver asks for a "remote session", "remote Code session", "new
  remote-controllable session", "start a Claude Code session with remote
  access", "dispatch a remote Code session", "session I can drive from my
  phone", "remote handoff session", or any variant of starting a Claude Code
  session he can control from a phone or secondary device.
disable-model-invocation: true
---

# Dispatch Remote-Controllable Code Session

Start a new Claude Code session and immediately activate remote control, so
Oliver can see and drive it from the Claude app on his phone or another
device.

## Why this extra step exists

`remoteControlAtStartup: true` in `~/.claude/settings.json` is supposed to
auto-enable remote control when a session starts. Claude.app-spawned sessions
silently ignore this flag — the BLE transport handler fails to initialize and
the session never registers with Anthropic's remote control backend. The
workaround is to send `/remote-control` to the session immediately after it
starts. Terminal-launched sessions honor the setting correctly; this skill
only matters for Dispatch-launched sessions.

## Steps

1. **Start the Code session** using `mcp__dispatch__start_code_task` as you
   normally would. Use `/Users/oliverames` as the working directory unless
   Oliver specifies a project path. Capture the returned `session_id`.

2. **Activate remote control** by calling `mcp__dispatch__send_message` with:
   - `session_id`: the value from step 1
   - `message`: exactly `/remote-control` — nothing else, no extra text

3. **Relay the URL** — the session will respond with a line like
   `Remote control active · https://claude.ai/code/session_…`. Extract and
   share that URL with Oliver so he can open it on his phone.

## Notes

- Do not modify the message in step 2. `/remote-control` must be sent alone;
  adding context or punctuation prevents it from being recognized as a slash
  command.
- If the session responds with an error about token scope, Oliver needs to
  run `claude auth login` in a terminal to replace the stored setup token
  with a full-scope OAuth token, then retry.
- This skill is a workaround for a known Claude.app bug
  (filed: `anthropics/claude-code`). Remove it once Anthropic fixes session
  initialization to honor `remoteControlAtStartup`.
