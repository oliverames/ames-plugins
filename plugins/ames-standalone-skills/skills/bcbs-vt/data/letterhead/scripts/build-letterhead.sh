#!/usr/bin/env bash
# BCBS VT Letterhead Builder
# Usage: build-letterhead.sh [--template=NAME] input.md [output.docx]
# Converts markdown to a branded Blue Cross VT .docx document.
#
# Templates (choose the pandoc reference-doc used):
#   (default)              → assets/reference.docx
#                            Simple Blue Cross VT letterhead — best for
#                            letters, member communications, short-form docs.
#   --template=proposal-report
#                          → assets/reference-proposal-report.docx
#                            Formal template with the Proposal Report header
#                            (BCBS logo + title band). Use for reports,
#                            proposals, strategy documents.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(dirname "$SCRIPT_DIR")"
ASSETS_DIR="$PLUGIN_DIR/assets"

TEMPLATE="default"

# --- Argument parsing ---
POSITIONAL=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --template=*)
      TEMPLATE="${1#--template=}"
      shift
      ;;
    --template)
      TEMPLATE="${2:-}"
      shift 2
      ;;
    -h|--help)
      sed -n '2,15p' "${BASH_SOURCE[0]}" | sed 's/^# //'
      exit 0
      ;;
    *)
      POSITIONAL+=("$1")
      shift
      ;;
  esac
done
set -- "${POSITIONAL[@]}"

if [[ $# -lt 1 ]]; then
  echo "Usage: build-letterhead.sh [--template=NAME] input.md [output.docx]"
  echo "Templates: default, proposal-report"
  echo "Example:   build-letterhead.sh my-letter.md ~/Desktop/bcbsvt-letter.docx"
  exit 1
fi

INPUT="$1"

if [[ ! -f "$INPUT" ]]; then
  echo "Error: Input file '$INPUT' not found."
  exit 1
fi

# --- Resolve template → reference doc ---
case "$TEMPLATE" in
  default|"")
    REFERENCE_DOC="$ASSETS_DIR/reference.docx"
    ;;
  proposal-report)
    REFERENCE_DOC="$ASSETS_DIR/reference-proposal-report.docx"
    ;;
  *)
    echo "Error: Unknown template '$TEMPLATE'. Valid values: default, proposal-report"
    exit 1
    ;;
esac

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
  if [[ "$TEMPLATE" == "proposal-report" ]]; then
    echo "Rebuilding via: python3 $SCRIPT_DIR/style-proposal-report.py"
    python3 "$SCRIPT_DIR/style-proposal-report.py" || {
      echo "⚠  Failed to build Proposal Report reference doc."
      exit 1
    }
  else
    echo "Rebuilding via: python3 $SCRIPT_DIR/style-reference-doc.py"
    python3 "$SCRIPT_DIR/style-reference-doc.py" || {
      echo "⚠  Failed to build default reference doc."
      exit 1
    }
  fi
fi

# --- Build ---
echo "Template:  $TEMPLATE"
echo "Building:  $INPUT → $OUTPUT"

pandoc "$INPUT" \
  --reference-doc="$REFERENCE_DOC" \
  --from=markdown \
  --to=docx \
  --output="$OUTPUT" \
  --syntax-highlighting=tango \
  2>&1

echo "✓ Created: $OUTPUT"
