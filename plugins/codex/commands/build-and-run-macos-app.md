---
name: build-and-run-macos-app
description: Create or update the project-local build_and_run.sh script, then build and launch the macOS app. Use when you need to set up or run the standard kill/build/launch entrypoint for a macOS Xcode or SwiftPM project.
allowed-tools: Bash, Read, Write, Edit, Glob
---

# /build-and-run-macos-app

Create or update the project-local macOS `build_and_run.sh` script, then use
that script as the default build/run entrypoint.

## Arguments

- `scheme`: Xcode scheme name (optional)
- `workspace`: path to `.xcworkspace` (optional)
- `project`: path to `.xcodeproj` (optional)
- `product`: SwiftPM executable product name (optional)
- `mode`: `run`, `debug`, `logs`, `telemetry`, or `verify` (optional, default: `run`)
- `app_name`: process/app name to stop before relaunching (optional)

## Workflow

1. Detect whether the repo uses an Xcode workspace, Xcode project, or SwiftPM package.
2. If the workspace is not inside a git repo yet, run `git init` at the project root before building.
3. Create or update `script/build_and_run.sh` so it always stops the current app, builds the macOS target, and launches the fresh result.
3. For SwiftPM, keep raw executable launch only for true CLI tools; for AppKit/SwiftUI GUI apps, create a project-local `.app` bundle and launch it with `/usr/bin/open -n`.
4. Support optional script flags for `--debug`, `--logs`, `--telemetry`, and `--verify`.
5. Run the script in the requested mode and summarize any build, script, or launch failure.

## Guardrails

- Do not initialize a nested git repo inside an existing parent checkout.
- Keep the no-flag script path simple: kill, build, run.
- Do not leave stale references pointing at old script paths.
- Use `--debug`, `--logs`, `--telemetry`, or `--verify` only when the user asks for those modes.
