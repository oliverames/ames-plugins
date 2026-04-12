---
name: create-shortcut
description: Create Apple Shortcuts (iOS/macOS automations) using Jelly language or raw plist. Use this skill whenever the user asks to "create a shortcut", "build a shortcut", "automate with Shortcuts", "make a Shortcuts workflow", or wants to build any iOS/macOS automation — even if they don't say "shortcut" explicitly. Always use this when the task involves Shortcuts.app actions, Tailscale device pickers, SSH over Shortcuts, Notes automation, photo actions, or any Apple ecosystem workflow.
allowed-tools: Write, Bash, Read
---

# Apple Shortcuts — Create a Shortcut

**Goal: deliver a real, signed `.shortcut` file every time.**

## Choose Your Approach

**Start with Jelly.** Then check if any required actions fall outside Jelly's ~300 supported actions. If so, use raw plist for those pieces.

### When to use Jelly
- Actions in Jelly's supported list (text, web requests, clipboard, notifications, menus, if/else, repeat, weather, notes, photos, shell scripts, SSH, etc.)
- Readable source code matters
- Read `the **jelly** skill` for full Jelly instructions

### When to use Raw Plist
- Actions Jelly can't compile (`is.workflow.actions.filter.photos` with predicates, third-party AppIntents like Tailscale, complex WFContentItemFilter predicates)
- You need an exact action structure you can inspect from `~/Library/Shortcuts/Shortcuts.sqlite`
- Read `the **raw-plist** skill` for raw plist instructions

### Hybrid approach
Build the Jelly-supported actions in Jelly, and hand-craft only the unsupported pieces as raw plist actions. Both can coexist: Jelly passes through raw WF plist blocks.

## Quick Decision Guide

| Need | Use |
|------|-----|
| Text, web, clipboard, menus, if/else, repeat | Jelly |
| Notifications, SSH, shell scripts | Jelly |
| Notes (create, append), Photos (basic picker) | Jelly |
| Photo filtering by dimensions/size predicates | Raw plist |
| Tailscale device picker (AppIntent) | Raw plist |
| Base64 encode/decode, file save/rename | Raw plist |
| Complex variable aggrandizements (e.g. `.ipv4Address`) | Raw plist |

## Reading Installed Shortcuts

To inspect an existing shortcut as reference (requires Full Disk Access):

```python
import sqlite3, plistlib, json, os

conn = sqlite3.connect(os.path.expanduser('~/Library/Shortcuts/Shortcuts.sqlite'))
cur = conn.cursor()
cur.execute("SELECT ZNAME, ZACTIONS FROM ZSHORTCUT WHERE ZNAME = ?", ("My Shortcut",))
name, actions_id = cur.fetchone()
cur.execute("SELECT ZDATA FROM ZSHORTCUTACTIONS WHERE Z_PK = ?", (actions_id,))
actions = plistlib.loads(cur.fetchone()[0])
print(json.dumps(actions, indent=2, default=str))
```

## Compile & Sign

```bash
# Jelly
jelly MyShortcut.jelly --export --out MyShortcut.shortcut
shortcuts sign --mode anyone --input MyShortcut.shortcut --output MyShortcut.shortcut

# Raw plist
python3 script_that_writes_plist.py  # writes binary plist
shortcuts sign --mode anyone --input MyShortcut.shortcut --output MyShortcut.shortcut
```
