#!/usr/bin/env python3
"""
Batch Transcribe — Process all audio files in a folder using smart-transcribe.

Usage:
    python3 batch-transcribe-folder.py /path/to/audio/files
    python3 batch-transcribe-folder.py /path/to/audio/files --model claude
"""
import argparse
import os
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
    parser = argparse.ArgumentParser(description="Batch transcribe audio files in a folder")
    parser.add_argument("source_dir", help="Directory containing audio files")
    parser.add_argument("--model", choices=["claude"], default="claude",
                        help="LLM for merging (default: claude)")
    parser.add_argument("--output", help="Output directory (default: alongside source files)")
    parser.add_argument("--no-diarization", action="store_true", help="Disable speaker diarization")
    parser.add_argument("--resume", action="store_true", help="Reuse completed engine outputs")
    parser.add_argument("--rerun-engine", action="append", default=[], help="Rerun one engine while resuming")
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

    extra_args = ["--model", args.model]
    if args.output:
        extra_args += ["--output", args.output]
    if args.no_diarization:
        extra_args.append("--no-diarization")
    if args.resume:
        extra_args.append("--resume")
    for engine in args.rerun_engine:
        extra_args += ["--rerun-engine", engine]

    succeeded = 0
    failed = 0
    for f in files:
        if process_file(f, extra_args):
            succeeded += 1
        else:
            failed += 1

    print(f"\n{'='*60}")
    print(f"Batch complete: {succeeded} succeeded, {failed} failed out of {len(files)}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
