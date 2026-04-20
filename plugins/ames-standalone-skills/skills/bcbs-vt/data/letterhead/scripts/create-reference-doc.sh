#!/usr/bin/env bash
# BCBS VT Reference Doc Creator (compatibility shim)
#
# This script is kept for backward compatibility. It delegates to the
# authoritative Python stylers:
#
#   style-reference-doc.py        → assets/reference.docx (default)
#   style-proposal-report.py      → assets/reference-proposal-report.docx (opt-in)
#
# To regenerate the default reference doc directly:
#   python3 scripts/style-reference-doc.py
#
# To regenerate the opt-in Proposal Report reference doc directly:
#   python3 scripts/style-proposal-report.py

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

TARGET="${1:-default}"

case "$TARGET" in
  default|reference)
    echo "Regenerating default reference.docx via style-reference-doc.py..."
    exec python3 "$SCRIPT_DIR/style-reference-doc.py"
    ;;
  proposal-report)
    echo "Regenerating reference-proposal-report.docx via style-proposal-report.py..."
    exec python3 "$SCRIPT_DIR/style-proposal-report.py"
    ;;
  *)
    echo "Usage: create-reference-doc.sh [default|proposal-report]"
    echo "       (omit argument to regenerate the default)"
    exit 1
    ;;
esac
