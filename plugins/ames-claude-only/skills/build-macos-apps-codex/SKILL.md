---
name: build-macos-apps-codex
description: macOS development workflows from OpenAI's curated Codex plugins. Covers building/running/debugging desktop apps, SwiftUI patterns, AppKit interop, Liquid Glass, code signing, packaging/notarization, SwiftPM, telemetry, test triage, view refactoring, and window management. Use when building, shipping, or debugging macOS apps.
---

# Build macOS Apps (Codex)

Converted from OpenAI's curated `build-macos-apps` Codex plugin (v0.1.2, MIT license).

## Available Workflows

Select the workflow that matches your task, then load the corresponding skill file:

### 1. Build, Run & Debug
Discover projects, build with xcodebuild, run in the debugger, and resolve common desktop build errors.
- Load: `skills/build-run-debug/SKILL.md`
- References: `skills/build-run-debug/references/`

### 2. SwiftUI Patterns (macOS)
macOS-specific SwiftUI scenes, windows, toolbars, settings, menu bar extras, split views, and inspectors.
- Load: `skills/swiftui-patterns/SKILL.md`
- References: `skills/swiftui-patterns/references/`

### 3. AppKit Interop
Bridge SwiftUI and AppKit: NSViewRepresentable, responder chain, menus, drag-and-drop, pasteboard, and window/panel management.
- Load: `skills/appkit-interop/SKILL.md`
- References: `skills/appkit-interop/references/`

### 4. Liquid Glass (macOS)
Adopt the macOS Tahoe Liquid Glass design system for toolbars, sidebars, and window chrome.
- Load: `skills/liquid-glass/SKILL.md`

### 5. Code Signing & Entitlements
Inspect, fix, and configure code signing identities, entitlements, and provisioning for macOS apps.
- Load: `skills/signing-entitlements/SKILL.md`

### 6. Packaging & Notarization
Package apps for distribution (DMG, installer), notarize with Apple, and handle stapling.
- Load: `skills/packaging-notarization/SKILL.md`

### 7. SwiftPM for macOS
Build, run, and manage Swift Package Manager projects targeting macOS.
- Load: `skills/swiftpm-macos/SKILL.md`

### 8. Telemetry (OSLog)
Add lightweight, structured logging with os.Logger for diagnostics and telemetry.
- Load: `skills/telemetry/SKILL.md`

### 9. Test Triage
Triage and debug XCTest and Swift Testing failures for macOS targets.
- Load: `skills/test-triage/SKILL.md`

### 10. View Refactor
Decompose and restructure macOS SwiftUI views for better state ownership and reuse.
- Load: `skills/view-refactor/SKILL.md`

### 11. Window Management
Manage macOS windows programmatically: multi-window apps, window groups, and restoration.
- Load: `skills/window-management/SKILL.md`

## Commands

Three pre-built command workflows are available in `commands/`:
- `build-and-run-macos-app.md` -- Wire up a build-and-run script for the project
- `fix-codesign-error.md` -- Diagnose and fix code signing errors
- `test-macos-app.md` -- Run and triage macOS test suites

## Usage

When the user's task maps to one or more of these workflows, read the relevant `SKILL.md` and follow its instructions. For broad macOS work, start with whichever workflow matches the immediate need.

## Updating

Run `./update.sh` from this skill's directory to pull the latest from the Codex plugin cache.
