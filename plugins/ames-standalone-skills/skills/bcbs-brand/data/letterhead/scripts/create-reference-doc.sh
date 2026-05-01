#!/usr/bin/env bash
# BCBS VT Reference Doc Creator (compatibility shim)
#
# This script is kept for backward compatibility. It delegates to the
# authoritative Python stylers:
#
#   style-proposal-report.py      → assets/reference-proposal-report.docx (default)
#   style-reference-doc.py        → assets/reference.docx (simple fallback)
#
# To regenerate the default Proposal Report Portrait reference doc directly:
#   python3 scripts/style-proposal-report.py
#
# To regenerate the simple fallback reference doc directly:
#   python3 scripts/style-reference-doc.py

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

TARGET="${1:-proposal-report}"

case "$TARGET" in
  default|proposal-report)
    echo "Regenerating reference-proposal-report.docx via style-proposal-report.py..."
    exec python3 "$SCRIPT_DIR/style-proposal-report.py"
    ;;
  simple|reference)
    echo "Regenerating simple fallback reference.docx via style-reference-doc.py..."
    exec python3 "$SCRIPT_DIR/style-reference-doc.py"
    ;;
  *)
    echo "Usage: create-reference-doc.sh [default|proposal-report|simple|reference]"
    echo "       (omit argument to regenerate the Proposal Report Portrait default)"
    exit 1
    ;;
esac
