---
name: horizon-vdi-control
description: Control Windows VDI sessions running inside Omnissa Horizon Client with Computer Use. Use when Codex needs to click, type, search, or draft content inside a Horizon remote desktop, especially Outlook Web or Chrome in a VDI where the remote desktop appears as an opaque RemoteControlHost rather than accessible native UI elements.
---

# Horizon VDI Control

## Core Model

Treat the VDI area as a remote video surface, not a native Mac app UI. Omnissa Horizon exposes its own toolbar controls as accessibility elements, but Windows, Chrome, Outlook, and other apps inside the VDI are usually one opaque `RemoteControlHost`. For VDI content, Computer Use is coordinate-driven.

Use `mcp__computer_use__` tools. Start every assistant turn that controls Horizon with `get_app_state` for `Omnissa Horizon Client`, then verify after each meaningful click or key press.

## Click Behavior

Expect these behaviors:

- Keyboard input works reliably once Horizon is active. `Ctrl+Esc` opened Windows Start during testing.
- A click targeted at Horizon may bring Horizon to the foreground before the VDI receives it.
- Do not assume true background clicking works for VDI content. In testing, app-targeted clicks activated Horizon.
- Native Horizon controls such as `Ctrl+Alt+Del`, `USB Devices`, `Minimize`, `Fullscreen`, and `Disconnect` are accessibility nodes. VDI content is not.
- The first click after switching to Horizon may only focus or capture the remote surface. A second click may be the one that actually affects Windows or Outlook.

## Safe Operating Sequence

1. Call `get_app_state` for `Omnissa Horizon Client`.
2. If the user is actively using the Mac, warn that VDI coordinate clicks can steal foreground focus.
3. Use one harmless click inside the remote desktop content area to establish focus/capture.
4. Click the intended VDI target using screenshot coordinates.
5. Re-query `get_app_state` or inspect the returned screenshot after every state-changing click.
6. If a click lands wrong, stop and repair the visible state before continuing.

Prefer keyboard shortcuts when the target is unambiguous:

- `Ctrl+Esc` for Windows Start.
- `Esc` to dismiss menus or overlays, though it may not always dismiss Start in Horizon.
- Browser Back can recover when a Chrome tab navigates away from Outlook.

## VDI Email Drafting

When drafting replies in Outlook Web inside the VDI:

- Use the humanizer skill for reply prose when available.
- Do not click `Send` unless the user explicitly asks to send.
- Avoid the `New mail` button unless creating a new message is the task.
- Prefer replying from the original message so Outlook saves the response as a draft in the right thread.
- After opening `Reply`, type only into the message body. Stay away from the Send button area.
- Outlook Web usually autosaves drafts. Verify by checking the compose surface or Drafts folder, but do not send a test message.

To find flagged mail in Outlook Web:

1. Click the Outlook search field near the top of the page.
2. Search for `flagged:yes`.
3. Press Return.
4. If Outlook shows filter chips, use the `Flagged` chip if needed.
5. Open results one at a time, read the visible thread, and draft only when there is enough context to respond responsibly.

## Recovery Notes From Testing

- `Ctrl+E` in the VDI can focus Chrome address/search instead of Outlook search if Chrome has focus. If this happens, use Browser Back or return to the Outlook tab.
- Clicking near the bottom tab strip or message pane can accidentally open a blank Outlook compose pane. Close or navigate away before continuing.
- The VDI can show sensitive email content. Minimize quoted details in status updates and final summaries.
- Do not use the Horizon `Disconnect` toolbar control unless the user asks.

## Completion Checklist

Before saying the task is done:

- Confirm Horizon is showing the expected app or thread.
- Confirm no unintended compose pane, menu, or browser tab is left open.
- For email drafting, confirm drafts were created and no messages were sent.
- Summarize what was changed in plain terms, without exposing unnecessary email content.
