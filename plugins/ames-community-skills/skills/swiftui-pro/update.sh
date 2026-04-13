#!/bin/bash
# update.sh — Pull latest swiftui-pro from twostraws/SwiftUI-Agent-Skill

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$SCRIPT_DIR"
REPO="twostraws/SwiftUI-Agent-Skill"
UPSTREAM_DIR="swiftui-pro"
CLONE_DIR="${TMPDIR:-/tmp}/SwiftUI-Agent-Skill-$$"

source "$HOME/Developer/Scripts/style.sh" 2>/dev/null || {
    header() { echo ""; echo "=== ${1}${2:+ — $2} ==="; echo ""; }
    banner() { echo ""; echo "[ $1 ]"; echo ""; }
    spin()   { local t="$1"; shift; echo "  → $t"; "$@"; }
    warn()   { echo "  ⚠ $1"; }
    error()  { echo "  ✗ $1" >&2; }
}

header "swiftui-pro" "Update from $REPO"

if ! command -v gh &> /dev/null; then
    error "gh (GitHub CLI) is required but not installed"
    exit 1
fi

cleanup() { rm -rf "$CLONE_DIR"; }
trap cleanup EXIT

spin "Cloning $REPO" gh repo clone "$REPO" "$CLONE_DIR" -- --depth 1 --quiet

if [[ ! -d "$CLONE_DIR/$UPSTREAM_DIR" ]]; then
    error "Expected directory '$UPSTREAM_DIR' not found in repo"
    exit 1
fi

# Show version diff
LOCAL_VERSION=$(sed -n 's/.*version:[[:space:]]*"\([^"]*\)".*/\1/p' "$SKILL_DIR/SKILL.md" 2>/dev/null | head -1)
LOCAL_VERSION="${LOCAL_VERSION:-unknown}"
UPSTREAM_VERSION=$(sed -n 's/.*version:[[:space:]]*"\([^"]*\)".*/\1/p' "$CLONE_DIR/$UPSTREAM_DIR/SKILL.md" 2>/dev/null | head -1)
UPSTREAM_VERSION="${UPSTREAM_VERSION:-unknown}"
echo "  Local: v$LOCAL_VERSION  Upstream: v$UPSTREAM_VERSION"

# Sync core files
spin "Updating SKILL.md" cp "$CLONE_DIR/$UPSTREAM_DIR/SKILL.md" "$SKILL_DIR/SKILL.md"

for dir in references agents assets; do
    if [[ -d "$CLONE_DIR/$UPSTREAM_DIR/$dir" ]]; then
        spin "Updating $dir/" bash -c "rm -rf '$SKILL_DIR/$dir' && cp -R '$CLONE_DIR/$UPSTREAM_DIR/$dir' '$SKILL_DIR/$dir'"
    fi
done

banner "swiftui-pro updated to v$UPSTREAM_VERSION"
