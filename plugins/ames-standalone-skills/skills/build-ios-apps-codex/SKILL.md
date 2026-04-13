---
name: build-ios-apps-codex
description: iOS development workflows from OpenAI's curated Codex plugins. Covers App Intents/Shortcuts, SwiftUI UI patterns, Liquid Glass adoption, performance auditing, view refactoring, and simulator debugging. Use when building, refining, or debugging iOS apps with modern SwiftUI and system integration patterns.
---

# Build iOS Apps (Codex)

Converted from OpenAI's curated `build-ios-apps` Codex plugin (v0.1.0, MIT license).

## Available Workflows

Select the workflow that matches your task, then load the corresponding skill file:

### 1. App Intents & Shortcuts
Design and implement App Intents, app entities, and App Shortcuts for system integration (Siri, Spotlight, widgets, controls).
- Load: `skills/ios-app-intents/SKILL.md`
- References: `skills/ios-app-intents/references/`

### 2. SwiftUI UI Patterns
Build production-quality SwiftUI interfaces using idiomatic component patterns for lists, grids, navigation, forms, sheets, overlays, and more.
- Load: `skills/swiftui-ui-patterns/SKILL.md`
- References: `skills/swiftui-ui-patterns/references/` (25+ component guides)

### 3. Liquid Glass (iOS)
Adopt the iOS 26+ Liquid Glass design language, including translucent materials, glass bar customization, and safe-area-aware layouts.
- Load: `skills/swiftui-liquid-glass/SKILL.md`
- References: `skills/swiftui-liquid-glass/references/`

### 4. SwiftUI Performance Audit
Profile and fix SwiftUI performance issues using Instruments, view identity analysis, and code smell detection.
- Load: `skills/swiftui-performance-audit/SKILL.md`
- References: `skills/swiftui-performance-audit/references/` (WWDC session notes, profiling guides)

### 5. SwiftUI View Refactor
Extract, restructure, and decompose SwiftUI views for better reuse, testability, and readability.
- Load: `skills/swiftui-view-refactor/SKILL.md`
- References: `skills/swiftui-view-refactor/references/`

### 6. iOS Debugger Agent
Debug iOS apps on simulators using XcodeBuildMCP workflows: build failures, runtime crashes, UI glitches, and log analysis.
- Load: `skills/ios-debugger-agent/SKILL.md`

## Usage

When the user's task maps to one or more of these workflows, read the relevant `SKILL.md` and follow its instructions. For broad iOS work, start with whichever workflow matches the immediate need; you don't need to load all of them at once.

## Updating

Run `./update.sh` from this skill's directory to pull the latest from the Codex plugin cache.
