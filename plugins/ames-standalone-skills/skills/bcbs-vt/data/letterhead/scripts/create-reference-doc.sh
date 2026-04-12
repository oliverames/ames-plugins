#!/usr/bin/env bash
# BCBS VT Reference Doc Creator
# Generates a branded pandoc reference.docx with Blue Cross VT styles
# Uses a styled markdown intermediate to produce the reference document

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT="$PLUGIN_DIR/assets/reference.docx"
TMPDIR_LOCAL="$(mktemp -d)"

trap 'rm -rf "$TMPDIR_LOCAL"' EXIT

# --- Check pandoc ---
if ! command -v pandoc &>/dev/null; then
  echo "Error: pandoc not installed. Run: brew install pandoc"
  exit 1
fi

echo "Generating BCBS VT reference.docx..."

# Step 1: Generate a default pandoc reference doc
echo "" > "$TMPDIR_LOCAL/empty.md"
if pandoc --print-default-data-file reference.docx > "$OUTPUT" 2>/dev/null; then
  echo "  Using pandoc default reference doc"
else
  pandoc "$TMPDIR_LOCAL/empty.md" -o "$OUTPUT" 2>/dev/null || true
fi

echo ""
echo "✓ Created base reference.docx at: $OUTPUT"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  NEXT STEP: Apply BCBS VT brand styles in Word"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Open: $OUTPUT"
echo ""
echo "Apply these styles in Word's Style Gallery:"
echo ""
echo "  Heading 1:  DIN 2014 Bold (or Arial Bold), 28pt, #003867 (Dark Blue)"
echo "  Heading 2:  DIN 2014 Demi (or Arial Bold), 20pt, #0075c9 (Primary Blue)"
echo "  Heading 3:  DIN 2014 Regular (or Arial), 14pt, #003867"
echo "  Normal:     Droid Sans (or Calibri), 12pt, #1a1a1a"
echo "  Header:     Background #003867, white text, BCBS VT logo left"
echo "  Footer:     Arial, 9pt, gray, licensee statement"
echo ""
echo "Margins: 1 inch all sides (1.25 inch left for formal letters)"
echo ""
echo "Save & close Word. The reference.docx is ready for pandoc."
echo ""
echo "For automated styling, install python-docx:"
echo "  pip install python-docx"
echo "  Then run: python3 scripts/style-reference-doc.py"
