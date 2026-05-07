#!/usr/bin/env python3
"""
Batch Transcribe — Process all audio files in a folder using smart-transcribe.

Usage:
    python3 batch-transcribe-folder.py /path/to/audio
    python3 batch-transcribe-folder.py /path/to/audio --merge-mode agent --context bcbs-brand
    python3 batch-transcribe-folder.py /path/to/audio --manifest /path/to/manifest.json

Manifest (optional JSON), keyed by filename relative to the source dir:
    {
      "5 Kemp Ave.m4a":   {"description": "Interview with Beth", "speakers": "Oliver,Beth"},
      "Team Standup.m4a": {"description": "Daily standup",       "speakers": "Alice,Bob"}
    }

Per-file manifest entries override the global --description / --speakers flags.
Files not in the manifest fall back to the global flags (or auto-generated).
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from common import supported_python_string

SCRIPT_DIR = Path(__file__).parent
SMART_TRANSCRIBE = SCRIPT_DIR / "smart-transcribe.py"
PYTHON_BIN = shutil.which("python3.13") or shutil.which("python3")

AUDIO_EXTENSIONS = {'.m4a', '.mp3', '.wav', '.ogg', '.flac', '.webm', '.qta', '.caf', '.aif', '.wma'}


def get_audio_files(source_dir: Path) -> list[Path]:
    files = [
        f for f in source_dir.iterdir()
        if f.suffix.lower() in AUDIO_EXTENSIONS and not f.name.startswith("._")
    ]
    return sorted(files)


def load_manifest(path: Path) -> dict[str, dict]:
    """Read a JSON manifest mapping filename → per-file overrides.

    Returns {} on any failure with a warning, so a malformed manifest doesn't
    abort a 6-file batch — the user still gets the global-flag defaults.
    """
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"⚠️  Manifest not loaded ({path}): {exc}", file=sys.stderr)
        return {}
    if not isinstance(raw, dict):
        print(f"⚠️  Manifest at {path} is not a JSON object — ignoring", file=sys.stderr)
        return {}
    return raw


def build_per_file_args(
    audio_path: Path,
    manifest: dict[str, dict],
    fallback_description: str | None,
    fallback_speakers: str | None,
) -> list[str]:
    """Produce the per-file --description / --speakers arguments.

    Manifest entry wins when present; otherwise the global flag value is used.
    Either field can be omitted in either source — the resulting list only
    contains flags that have a real value.
    """
    entry = manifest.get(audio_path.name) or manifest.get(str(audio_path)) or {}
    description = entry.get("description") or fallback_description
    speakers = entry.get("speakers") or fallback_speakers
    args: list[str] = []
    if description:
        args += ["-d", description]
    if speakers:
        args += ["--speakers", speakers]
    return args


def process_file(audio_path: Path, extra_args: list[str]) -> bool:
    print(f"\n{'='*60}")
    print(f"Processing: {audio_path.name}")
    print(f"{'='*60}")

    cmd = [str(PYTHON_BIN), str(SMART_TRANSCRIBE), str(audio_path)] + extra_args

    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        if result.returncode != 0:
            print(f"Error processing {audio_path.name}")
            return False
        return True
    except Exception as e:
        print(f"Failed on {audio_path.name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Batch transcribe audio files in a folder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("source_dir", help="Directory containing audio files")
    parser.add_argument("--output", help="Output directory (default: alongside source files)")
    parser.add_argument(
        "--merge-mode",
        choices=["agent", "claude", "manual"],
        default="claude",
        help="agent: emit per-file merge bundle; claude: headless Claude/Codex merge; manual: comparison bundle (default: claude)",
    )
    parser.add_argument("--context", metavar="NAME",
                        help="Named context overlay (e.g. bcbs-brand) forwarded to every file")
    parser.add_argument("-d", "--description", metavar="STR",
                        help="Default description for files not in the manifest")
    parser.add_argument("--speakers", metavar="STR",
                        help="Default speakers (comma-separated) for files not in the manifest")
    parser.add_argument(
        "--manifest", metavar="FILE",
        help=("JSON file mapping audio filename → {description, speakers}. "
              "Per-file values override --description and --speakers."),
    )
    parser.add_argument("--no-diarization", action="store_true", help="Disable speaker diarization")
    parser.add_argument("--resume", action="store_true", help="Reuse completed engine outputs")
    parser.add_argument("--rerun-engine", action="append", default=[],
                        help="Rerun one engine while resuming (may be repeated)")
    parser.add_argument(
        "--engines", metavar="E1,E2,...",
        help="Comma-separated engine IDs forwarded to smart-transcribe (default: keep its default set)",
    )
    # Legacy: --model claude was the old way to pick the merge runner. Kept as
    # a no-op accept so existing scripts don't break, but --merge-mode is the
    # canonical flag now.
    parser.add_argument("--model", choices=["claude"], help=argparse.SUPPRESS)
    args = parser.parse_args()

    source_dir = Path(args.source_dir).resolve()
    if not source_dir.is_dir():
        print(f"Error: {source_dir} is not a directory")
        sys.exit(1)

    if not PYTHON_BIN:
        print(f"Error: no Python {supported_python_string()} interpreter found")
        print("Run the smart-transcribe setup first")
        sys.exit(1)

    files = get_audio_files(source_dir)
    if not files:
        print(f"No audio files found in {source_dir}")
        sys.exit(0)

    print(f"Found {len(files)} audio file(s) in {source_dir}")

    manifest: dict[str, dict] = {}
    if args.manifest:
        manifest_path = Path(args.manifest).expanduser().resolve()
        if not manifest_path.exists():
            print(f"Error: manifest not found: {manifest_path}")
            sys.exit(1)
        manifest = load_manifest(manifest_path)
        print(f"Loaded manifest with {len(manifest)} entr{'y' if len(manifest) == 1 else 'ies'}")

    # Global args sent to every file. Per-file --description / --speakers are
    # appended later inside the loop so manifest overrides land last.
    common_args = ["--merge-mode", args.merge_mode]
    if args.output:
        common_args += ["--output", args.output]
    if args.context:
        common_args += ["--context", args.context]
    if args.engines:
        common_args += ["--engines", args.engines]
    if args.no_diarization:
        common_args.append("--no-diarization")
    if args.resume:
        common_args.append("--resume")
    for engine in args.rerun_engine:
        common_args += ["--rerun-engine", engine]

    succeeded = 0
    failed = 0
    for f in files:
        per_file = build_per_file_args(f, manifest, args.description, args.speakers)
        if process_file(f, common_args + per_file):
            succeeded += 1
        else:
            failed += 1

    print(f"\n{'='*60}")
    print(f"Batch complete: {succeeded} succeeded, {failed} failed out of {len(files)}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
