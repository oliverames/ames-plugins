#!/bin/bash
# Smart Transcribe - Runtime installer

set -euo pipefail

if [[ -n "${XDG_DATA_HOME:-}" ]]; then
  CONFIG_DIR="$XDG_DATA_HOME/smart-transcribe"
else
  CONFIG_DIR="$HOME/.config/smart-transcribe"
fi
RUNTIME_DIR="$CONFIG_DIR/runtimes"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="$(dirname "$SCRIPT_DIR")"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"
ENGINES=("voxtral-small" "scribe-v2" "assemblyai-u3-pro" "gemini-3-pro")

# Find the highest available Python >= 3.13 on PATH
find_python() {
  for minor in 20 19 18 17 16 15 14 13; do
    local cmd="python3.$minor"
    if command -v "$cmd" >/dev/null 2>&1; then
      local ver; ver=$("$cmd" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
      local ok; ok=$("$cmd" -c 'import sys; print(int(sys.version_info >= (3,13)))')
      if [[ "$ok" == "1" ]]; then
        echo "$cmd"
        return 0
      fi
    fi
  done
  return 1
}

PYTHON_BIN="${SMART_TRANSCRIBE_PYTHON:-$(find_python)}"

echo "Smart Transcribe - Setup"
echo "========================"
echo "Config directory:  $CONFIG_DIR"
echo "Runtime directory: $RUNTIME_DIR"
echo "Required Python:   3.13+"
echo

if [[ -z "$PYTHON_BIN" ]]; then
  echo "Error: no supported Python (3.13+) found."
  echo "Install Python 3.13 or later, then rerun setup."
  exit 1
fi

PY_VERSION="$("$PYTHON_BIN" -c 'import platform; print(platform.python_version())')"
echo "Bootstrap interpreter: $PYTHON_BIN ($PY_VERSION)"
echo

mkdir -p "$CONFIG_DIR" "$RUNTIME_DIR"

for ENGINE in "${ENGINES[@]}"; do
  VENV_DIR="$RUNTIME_DIR/$ENGINE/venv"
  echo "Preparing runtime for $ENGINE"
  if [[ ! -x "$VENV_DIR/bin/python" ]]; then
    "$PYTHON_BIN" -m venv "$VENV_DIR"
  fi
  "$VENV_DIR/bin/python" -c 'import platform,sys; assert sys.version_info >= (3,13), f"Unsupported Python {platform.python_version()} (need 3.13+)"; print(f"  active: {sys.executable} ({platform.python_version()})")'
  "$VENV_DIR/bin/pip" install --upgrade pip -q
  "$VENV_DIR/bin/pip" install -q -r "$REQUIREMENTS_FILE"
  echo
done

echo "Checking system dependencies..."
if command -v ffmpeg >/dev/null 2>&1; then
  echo "  ffmpeg: $(ffmpeg -version 2>&1 | head -1)"
else
  echo "  ffmpeg: NOT FOUND (brew install ffmpeg)"
fi

if command -v ffprobe >/dev/null 2>&1; then
  echo "  ffprobe: OK"
else
  echo "  ffprobe: NOT FOUND"
fi

if command -v claude >/dev/null 2>&1; then
  echo "  claude: $(command -v claude)"
else
  echo "  claude: NOT FOUND (manual merge mode will still work)"
fi

if [[ -f "$PLUGIN_ROOT/data/transcription-dictionary.json" && ! -f "$CONFIG_DIR/transcription-dictionary.json" ]]; then
  cp "$PLUGIN_ROOT/data/transcription-dictionary.json" "$CONFIG_DIR/transcription-dictionary.json"
fi

cat > "$CONFIG_DIR/config.json" <<CONF
{
  "dictionary_path": "$CONFIG_DIR/transcription-dictionary.json",
  "suggestions_log": "$CONFIG_DIR/suggested-additions.jsonl"
}
CONF

echo
echo "Setup complete."
echo "Default engines: AssemblyAI Universal-3 Pro + ElevenLabs Scribe v2 + Mistral Voxtral + Google Gemini"
echo "Doctor check: $PYTHON_BIN $SCRIPT_DIR/smart-transcribe.py --doctor"
