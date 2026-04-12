#!/usr/bin/env bash
# BCBS VT Letterhead Builder
# Usage: build-letterhead.sh input.md [output.docx]
# Converts markdown to a branded Blue Cross VT .docx document

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(dirname "$SCRIPT_DIR")"
REFERENCE_DOC="$PLUGIN_DIR/assets/reference.docx"

# --- Argument handling ---
if [[ $# -lt 1 ]]; then
  echo "Usage: build-letterhead.sh input.md [output.docx]"
  echo "Example: build-letterhead.sh my-letter.md ~/Desktop/bcbsvt-letter.docx"
  exit 1
fi

INPUT="$1"

if [[ ! -f "$INPUT" ]]; then
  echo "Error: Input file '$INPUT' not found."
  exit 1
fi

# Default output name: input filename with .docx extension, in same directory
if [[ $# -ge 2 ]]; then
  OUTPUT="$2"
else
  BASENAME="$(basename "$INPUT" .md)"
  OUTPUT="$(dirname "$INPUT")/${BASENAME}.docx"
fi

# --- Check pandoc ---
if ! command -v pandoc &>/dev/null; then
  echo "Error: pandoc is not installed."
  echo "Install with: brew install pandoc"
  exit 1
fi

# --- Check reference doc ---
if [[ ! -f "$REFERENCE_DOC" ]]; then
  echo "Reference doc not found at: $REFERENCE_DOC"
  echo "Generating a bare reference doc (no brand styles)..."
  bash "$SCRIPT_DIR/create-reference-doc.sh"
  echo ""
  echo "⚠  Warning: The generated reference.docx has no BCBS VT brand styles."
  echo "   For branded output, run: python3 $SCRIPT_DIR/style-reference-doc.py"
  echo "   Then re-run this script."
  echo ""
fi

# --- Build ---
echo "Building: $INPUT → $OUTPUT"

pandoc "$INPUT" \
  --reference-doc="$REFERENCE_DOC" \
  --from=markdown \
  --to=docx \
  --output="$OUTPUT" \
  --syntax-highlighting=tango \
  2>&1

echo "✓ Created: $OUTPUT"
