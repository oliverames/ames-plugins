---
name: cmux
description: >-
  Use when running inside cmux and performing tasks that benefit from workspace management,
  progress tracking, browser automation, or multi-pane workflows. Triggers when the user
  asks to "show progress", "open a browser", "split the pane", "open markdown", "use cmux",
  "show status", "notify me when done", or when performing batch operations, long-running
  tasks, or web lookups that benefit from cmux's built-in browser. Also triggers when the
  user mentions "cmux", "sidebar", "workspace", or "pane". Use this proactively for any
  batch operation (archiving emails, processing files, deploying) where a progress bar and
  completion notification would improve the user's experience — even if they don't ask for it.
allowed-tools: Bash
---

# cmux — Terminal Multiplexer for Claude Code

cmux provides workspace management, sidebar status, a built-in browser, and pane control.
Only available when running inside cmux (check for `CMUX_WORKSPACE_ID` env var).

## Conceptual Model

cmux organizes your environment in a five-level hierarchy:

```
Window (macOS window — ⌘⇧N to open more)
└── Workspace (sidebar tab — ⌘N to create)
    └── Pane (split region — ⌘D right, ⌘⇧D down)
        └── Surface (tab within pane — ⌘T to create)
            └── Panel (terminal or browser content)
```

Everything is referenced by short refs like `workspace:1`, `pane:2`, `surface:3`.
Use `cmux tree` to see the full hierarchy. Use `cmux identify` to see where you are.

**Note on "tab"**: The word "tab" is overloaded in cmux. In the sidebar UI and keyboard
shortcuts, "tab" means **workspace**. In pane tab bars, "tab" means **surface**. The
socket API and env vars always use the precise terms (workspace, surface).

## Quick Reference

### Environment

```bash
$CMUX_WORKSPACE_ID    # Current workspace UUID (auto-set)
$CMUX_SURFACE_ID      # Current surface UUID (auto-set)
$CMUX_SOCKET_PATH     # Unix socket path
```

### Introspection

```bash
cmux identify                    # Show caller vs focused surface/pane/workspace
cmux tree                        # Full layout tree
cmux list-workspaces             # All workspace tabs
cmux list-panes                  # Panes in current workspace
cmux list-pane-surfaces          # Surfaces per pane
cmux sidebar-state               # Full sidebar metadata dump
cmux capabilities                # Available socket methods and access mode
```

## Sidebar Status

Update the sidebar to show task progress, status, and logs — visible at a glance
without cluttering the conversation.

```bash
# Key-value status pills (icon and color are optional)
# --icon accepts named icons ("hammer") or emoji ("🧪")
cmux set-status <key> <value> [--icon <name|emoji>] [--color <#hex>]
cmux clear-status <key>
cmux list-status

# Progress bar (0.0 to 1.0)
cmux set-progress <float> [--label <text>]
cmux clear-progress

# Log entries (levels: info, progress, success, warning, error)
cmux log [--level <level>] [--source <name>] [-- ] <message>
cmux list-log [--limit <n>]
cmux clear-log
```

Use `--` before the message if it starts with a dash. Always clean up when done:
`cmux clear-status <key> && cmux clear-progress`

### When to use sidebar status

- **Batch operations**: Set progress as you iterate (archiving emails, processing files)
- **Multi-step tasks**: Update status key with current step name
- **Background monitoring**: Log events as they happen

## Notifications

```bash
cmux notify --title <text> [--subtitle <text>] [--body <text>]
cmux list-notifications
cmux clear-notifications
```

Desktop alerts are suppressed when the cmux window is focused and the sending
workspace is active — so notifications won't interrupt the user mid-flow.

Keyboard shortcuts: `⌘⇧I` opens notification panel, `⌘⇧U` jumps to most recent unread.

## Built-in Browser

Opens a browser pane inside cmux. The user sees it alongside their terminal —
great for looking up docs, previewing HTML, or debugging web apps together.

For headless scraping or automated testing, use the Playwright plugin instead.

### Essentials

```bash
# Open
cmux browser open                                    # new browser pane
cmux browser open https://example.com                # with initial URL
cmux browser open-split https://example.com          # opens as a split

# Targeting — positional and flag forms are equivalent
cmux browser surface:2 navigate https://example.org
cmux browser --surface surface:2 navigate https://example.org

# Navigate
cmux browser surface:2 back
cmux browser surface:2 forward
cmux browser surface:2 reload

# Read page
cmux browser surface:2 get url
cmux browser surface:2 get title
cmux browser surface:2 get text "h1"                 # text of a selector
cmux browser surface:2 snapshot                       # DOM tree with [ref=eN] handles
cmux browser surface:2 snapshot --interactive --compact  # just interactive elements
cmux browser surface:2 screenshot --out /tmp/page.png

# Interact (use refs from snapshot, or CSS selectors)
cmux browser surface:2 click e3                       # click by snapshot ref
cmux browser surface:2 click "button[type='submit']" --snapshot-after
cmux browser surface:2 fill "#email" --text "user@example.com"
cmux browser surface:2 press Enter
cmux browser surface:2 scroll --dy 800

# Wait for dynamic content
cmux browser surface:2 wait --load-state complete --timeout-ms 15000
cmux browser surface:2 wait --selector "#result"
cmux browser surface:2 wait --text "Success"

# Cleanup
cmux close-surface --surface surface:2
```

### Extracting the surface ref

`cmux browser open` returns `OK surface=surface:6 pane=pane:5 placement=split`.

```bash
ref=$(cmux browser open | awk -F'surface=' '{print $2}' | awk '{print $1}')
```

### Full browser reference

For advanced features — tabs, frames, dialogs, downloads, cookies, storage,
state save/load, JS injection, `find` by role/label/testid, `is` checks,
and `get` for html/value/attr/count/box/styles — read `references/browser.md`.

### cmux browser vs Playwright plugin

| | cmux browser | Playwright plugin |
|---|---|---|
| Visibility | User sees it in a pane | Headless, invisible |
| Login state | Fresh (no cookies) | Fresh (no cookies) |
| Best for | Collaborative browsing, showing the user something | Automated testing, scraping |
| Interaction | Element refs from `snapshot` or CSS selectors | CSS selectors |

## Pane & Workspace Management

```bash
# Workspaces (sidebar tabs)
cmux new-workspace [--cwd <path>] [--command <text>]
cmux select-workspace --workspace <ref>
cmux rename-workspace <title>
cmux close-workspace --workspace <ref>

# Panes (splits within a workspace)
cmux new-split <left|right|up|down>
cmux new-pane [--type terminal|browser] [--direction <dir>]
cmux focus-pane --pane <ref>
cmux resize-pane --pane <ref> (-L|-R|-U|-D) [--amount <n>]
cmux swap-pane --pane <ref> --target-pane <ref>

# Surfaces (tabs within a pane)
cmux new-surface [--type terminal|browser] [--pane <ref>]
cmux close-surface [--surface <ref>]
cmux move-surface --surface <ref> [--pane <ref>]

# Cross-pane interaction
cmux read-screen [--surface <ref>] [--lines <n>]     # read another terminal's output
cmux send [--surface <ref>] <text>                    # type into a terminal
cmux send-key [--surface <ref>] <key>                 # send keypress (enter, tab, escape, etc.)
```

## Markdown Viewer

Opens a formatted, live-reloading markdown panel. Edits to the file update
the viewer automatically.

```bash
cmux markdown <path>              # opens viewer panel (returns surface ref)
```

## Buffers (Clipboard)

```bash
cmux set-buffer [--name <name>] <text>
cmux list-buffers
cmux paste-buffer [--name <name>] [--surface <ref>]
```

## Patterns

### Batch task with full observability

```bash
cmux set-status "task" "Archiving emails" --icon "📧"
cmux log --level info --source "email" -- "Starting batch archive"
total=20
for i in $(seq 1 $total); do
  # ... do work ...
  cmux set-progress $(awk "BEGIN{printf \"%.2f\", $i/$total}") --label "Archiving $i/$total"
  cmux log --level success --source "email" -- "Archived: $subject"
done
cmux clear-status task
cmux clear-progress
cmux notify --title "Email cleanup done" --body "Archived $total messages"
```

### Show a plan while working

```bash
cat > /tmp/plan.md << 'EOF'
# Implementation Plan
1. **Step one** — description
2. **Step two** — description
EOF
cmux markdown /tmp/plan.md
# ... do work, update the file as steps complete ...
```

### Quick web lookup

```bash
ref=$(cmux browser open | awk -F'surface=' '{print $2}' | awk '{print $1}')
cmux browser $ref navigate "https://developer.apple.com/documentation/swiftui"
cmux browser $ref snapshot --interactive --compact
# ... read the snapshot, extract what you need ...
cmux close-surface --surface $ref
```
