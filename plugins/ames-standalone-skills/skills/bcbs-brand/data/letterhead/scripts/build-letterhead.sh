#!/usr/bin/env bash
# BCBS VT Letterhead Builder
# Usage:
#   build-letterhead.sh [--template=NAME] input.md [output.docx]
#   build-letterhead.sh --exemplar=PATH [--banner-title="..."] input.md [output.docx]
#
# Pick based on what the user asked for:
#   - If Oliver named a specific reference file ("use the Gap Analysis Memo",
#     "clone the strategy memo") → use --exemplar=PATH. Named references
#     ALWAYS override the skill default; never silently substitute.
#   - If Oliver described a memo style without naming a file → use
#     --template=memo, which points at the bundled Proposal Report memo
#     exemplar.
#   - If Oliver asked for a plain letter → --template=simple.
#   - Otherwise (default) → --template=proposal-report for the formal
#     Proposal Report header-banded reference doc.
#
# Templates (built-in reference docs):
#   (default), --template=default,
#   --template=proposal-report
#                          → assets/reference-proposal-report.docx
#                            Formal template with the Proposal Report header
#                            (BCBS logo + title band). Use for reports,
#                            proposals, strategy documents, and polished docs.
#   --template=memo        → assets/exemplar-proposal-report-memo.docx
#                            Memo variant of the Proposal Report family with
#                            the graphic banner preserved. Use for memos.
#   --template=simple,
#   --template=reference    → assets/reference.docx
#                            Plain/simple fallback only when explicitly requested.
#
# Exemplar (user-named reference):
#   --exemplar=PATH         Any .docx to use as the pandoc reference-doc.
#                           Delegates to clone-exemplar.py, which supports
#                           --banner-title rewriting.
#   --banner-title="..."    Only valid with --exemplar or --template=memo.
#                           Rewrites the banner title text in word/header1.xml
#                           (both wps:txbx and mc:Fallback v:textbox copies).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(dirname "$SCRIPT_DIR")"
ASSETS_DIR="$PLUGIN_DIR/assets"

TEMPLATE="proposal-report"
EXEMPLAR=""
BANNER_TITLE=""

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
    --exemplar=*)
      EXEMPLAR="${1#--exemplar=}"
      shift
      ;;
    --exemplar)
      EXEMPLAR="${2:-}"
      shift 2
      ;;
    --banner-title=*)
      BANNER_TITLE="${1#--banner-title=}"
      shift
      ;;
    --banner-title)
      BANNER_TITLE="${2:-}"
      shift 2
      ;;
    -h|--help)
      sed -n '2,46p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
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
  echo "Usage: build-letterhead.sh [--template=NAME | --exemplar=PATH] [--banner-title=...] input.md [output.docx]"
  echo "Templates: default, proposal-report, memo, simple, reference"
  echo "Example:   build-letterhead.sh my-letter.md ~/Desktop/bcbsvt-letter.docx"
  echo "Memo:      build-letterhead.sh --template=memo --banner-title='STRATEGY MEMO' my-memo.md memo.docx"
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

# --- Route: --exemplar or --template=memo → clone-exemplar.py ---
if [[ -n "$EXEMPLAR" || "$TEMPLATE" == "memo" ]]; then
  if [[ -z "$EXEMPLAR" ]]; then
    EXEMPLAR="$ASSETS_DIR/exemplar-proposal-report-memo.docx"
  fi
  if [[ ! -f "$EXEMPLAR" ]]; then
    if [[ "$EXEMPLAR" == "$ASSETS_DIR/exemplar-proposal-report-memo.docx" ]]; then
      echo "Memo exemplar not found at: $EXEMPLAR"
      echo "Rebuilding via: python3 $SCRIPT_DIR/build-exemplar-memo.py"
      python3 "$SCRIPT_DIR/build-exemplar-memo.py" || {
        echo "⚠  Failed to build memo exemplar."
        exit 1
      }
    else
      echo "Error: exemplar '$EXEMPLAR' not found."
      exit 1
    fi
  fi

  echo "Exemplar: $EXEMPLAR"
  echo "Building: $INPUT → $OUTPUT"

  ARGS=(
    --exemplar "$EXEMPLAR"
    --markdown "$INPUT"
    --output "$OUTPUT"
    --tight-bullets
  )
  if [[ -n "$BANNER_TITLE" ]]; then
    ARGS+=(--banner-title "$BANNER_TITLE")
  fi
  python3 "$SCRIPT_DIR/clone-exemplar.py" "${ARGS[@]}"
  echo "✓ Created: $OUTPUT"
  exit 0
fi

if [[ -n "$BANNER_TITLE" ]]; then
  echo "Error: --banner-title only applies with --exemplar or --template=memo."
  exit 1
fi

# --- Resolve template → reference doc ---
case "$TEMPLATE" in
  default|proposal-report|"")
    REFERENCE_DOC="$ASSETS_DIR/reference-proposal-report.docx"
    ;;
  simple|reference)
    REFERENCE_DOC="$ASSETS_DIR/reference.docx"
    ;;
  *)
    echo "Error: Unknown template '$TEMPLATE'. Valid values: default, proposal-report, memo, simple, reference"
    exit 1
    ;;
esac

# --- Check pandoc ---
if ! command -v pandoc &>/dev/null; then
  echo "Error: pandoc is not installed."
  echo "Install with: brew install pandoc"
  exit 1
fi

# --- Check reference doc ---
if [[ ! -f "$REFERENCE_DOC" ]]; then
  echo "Reference doc not found at: $REFERENCE_DOC"
  if [[ "$TEMPLATE" == "proposal-report" || "$TEMPLATE" == "default" || "$TEMPLATE" == "" ]]; then
    echo "Rebuilding via: python3 $SCRIPT_DIR/style-proposal-report.py"
    python3 "$SCRIPT_DIR/style-proposal-report.py" || {
      echo "⚠  Failed to build Proposal Report reference doc."
      exit 1
    }
  else
    echo "Rebuilding via: python3 $SCRIPT_DIR/style-reference-doc.py"
    python3 "$SCRIPT_DIR/style-reference-doc.py" || {
      echo "⚠  Failed to build simple fallback reference doc."
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
