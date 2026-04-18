#!/bin/bash
# update.sh — Sync build-ios-apps-codex from local Codex plugin cache

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$SCRIPT_DIR"
CODEX_CACHE="$HOME/.codex/plugins/cache/openai-curated/build-ios-apps"
PLUGIN_NAME="build-ios-apps"

source "$HOME/Developer/Scripts/style.sh" 2>/dev/null || {
    header() { echo ""; echo "=== ${1}${2:+ — $2} ==="; echo ""; }
    banner() { echo ""; echo "[ $1 ]"; echo ""; }
    spin()   { local t="$1"; shift; echo "  → $t"; "$@"; }
    warn()   { echo "  ⚠ $1"; }
    error()  { echo "  ✗ $1" >&2; }
}

header "$PLUGIN_NAME" "Sync from Codex cache"

# Find the latest cached version (content-addressed hash dir)
if [[ ! -d "$CODEX_CACHE" ]]; then
    error "Codex cache not found: $CODEX_CACHE"
    echo "  Make sure the $PLUGIN_NAME plugin is installed in Codex."
    exit 1
fi

CACHE_DIR=$(find "$CODEX_CACHE" -mindepth 1 -maxdepth 1 -type d ! -name ".*" | head -1)
if [[ -z "$CACHE_DIR" ]]; then
    error "No cached version found in $CODEX_CACHE"
    exit 1
fi

# Show version
CODEX_VERSION=$(python3 -c "import json; print(json.load(open('$CACHE_DIR/.codex-plugin/plugin.json'))['version'])" 2>/dev/null || echo "unknown")
echo "  Codex cache version: v$CODEX_VERSION"
echo "  Cache path: $CACHE_DIR"

if [[ ! -d "$CACHE_DIR/skills" ]]; then
    error "No skills directory found in cache"
    exit 1
fi

for skill_dir in "$CACHE_DIR/skills"/*/; do
    skill_name=$(basename "$skill_dir")
    dest="$SKILL_DIR/skills/$skill_name"

    spin "Syncing $skill_name" bash -c "
        mkdir -p '$dest'
        cp '$skill_dir/SKILL.md' '$dest/SKILL.md' 2>/dev/null || true
        if [[ -d '$skill_dir/references' ]]; then
            rm -rf '$dest/references'
            cp -R '$skill_dir/references' '$dest/references'
        fi
    "
done

# Remove local skills that no longer exist upstream
for local_skill in "$SKILL_DIR/skills"/*/; do
    skill_name=$(basename "$local_skill")
    if [[ ! -d "$CACHE_DIR/skills/$skill_name" ]]; then
        warn "Removing $skill_name (no longer in upstream)"
        rm -rf "$local_skill"
    fi
done

banner "build-ios-apps-codex synced from Codex v$CODEX_VERSION"
