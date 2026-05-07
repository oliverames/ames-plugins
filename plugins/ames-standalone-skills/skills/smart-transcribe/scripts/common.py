"""
Smart Transcribe - Shared Utilities
====================================

Common code used by smart-transcribe.py, ensemble.py, and batch-transcribe-folder.py.
Consolidates: constants, venv resolution, API key resolution (env + 1Password + keys.env),
dictionary loading, audio preprocessing, engine subprocess runners, and regex corrections.
"""

import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any


# =============================================================================
# PATHS AND CONSTANTS
# =============================================================================

PLUGIN_ROOT = Path(__file__).parent.parent
SCRIPT_DIR = Path(__file__).parent


def get_config_dir() -> Path:
    xdg_data_home = os.getenv("XDG_DATA_HOME")
    if xdg_data_home:
        return Path(xdg_data_home).expanduser() / "smart-transcribe"
    return Path.home() / ".config" / "smart-transcribe"


CONFIG_DIR = get_config_dir()
KEYS_FILE = CONFIG_DIR / "keys.env"
CONFIG_FILE = CONFIG_DIR / "config.json"
SEED_DICTIONARY = PLUGIN_ROOT / "data" / "transcription-dictionary.json"
SKILL_CONTEXTS_DIR = PLUGIN_ROOT / "data" / "contexts"
OUTPUT_DIR = Path.home() / "Desktop" / "Transcriptions"
CONTEXTS_DIR = CONFIG_DIR / "contexts"
MIGRATION_MARKER_DIR = CONFIG_DIR / ".migrations"
RUNTIME_DIR = CONFIG_DIR / "runtimes"
STATUS_FILE_NAME = "status.json"
RUN_LOG_NAME = "run.log"

NATIVE_FORMATS = {".m4a", ".mp3", ".wav", ".ogg", ".flac", ".webm"}
MAX_UPLOAD_MB = 35
SUPPORTED_PYTHON_MIN = (3, 13)
SUPPORTED_PYTHON_MAX = (99, 99)  # no upper bound — use latest available
DEFAULT_ENGINE_PYTHONS = {
    "scribe-v2": "python3",
    "assemblyai-u3-pro": "python3",
    "cohere-transcribe": "python3",
    "voxtral-small": "python3",
    "gemini-3-pro": "python3",
    "gpt4o-transcribe": "python3",
    "gpt4o-mini-transcribe": "python3",
    "voxtral-mini-local": "python3",
}


# =============================================================================
# VENV RESOLUTION
# =============================================================================

def supported_python_string() -> str:
    return f"{SUPPORTED_PYTHON_MIN[0]}.{SUPPORTED_PYTHON_MIN[1]}+"


def python_version_supported(version_info: Any) -> bool:
    major = int(version_info[0])
    minor = int(version_info[1])
    return (major, minor) >= SUPPORTED_PYTHON_MIN and (major, minor) <= SUPPORTED_PYTHON_MAX


def format_python_version(version_info: Any) -> str:
    major = int(version_info[0])
    minor = int(version_info[1])
    micro = int(version_info[2]) if len(version_info) > 2 else 0
    return f"{major}.{minor}.{micro}"


def require_supported_python(python_path: str | Path | None = None) -> None:
    if python_path is None:
        version_info = sys.version_info
        executable = sys.executable
    else:
        info = inspect_python(str(python_path))
        if not info["exists"]:
            raise RuntimeError(f"Python interpreter not found: {python_path}")
        version_info = tuple(info["version_info"])
        executable = info["path"]
    if not python_version_supported(version_info):
        raise RuntimeError(
            f"Unsupported Python runtime at {executable}: {format_python_version(version_info)}. "
            f"Use Python {supported_python_string()}.x."
        )


def inspect_python(python_path: str) -> dict[str, Any]:
    path = Path(python_path).expanduser()
    if not path.exists():
        resolved = shutil.which(str(python_path))
        if resolved:
            path = Path(resolved)
    info: dict[str, Any] = {"path": str(path), "exists": path.exists()}
    if not path.exists():
        return info
    try:
        result = subprocess.run(
            [str(path), "-c", "import json,platform,sys; print(json.dumps({'version_info': list(sys.version_info[:3]), 'version': platform.python_version(), 'executable': sys.executable}))"],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        info["returncode"] = result.returncode
        if result.returncode == 0 and result.stdout.strip():
            info.update(json.loads(result.stdout))
            info["supported"] = python_version_supported(info["version_info"])
        else:
            info["stderr"] = result.stderr.strip()
    except Exception as exc:
        info["error"] = str(exc)
    return info


def find_python_command(preferred: str | None = None) -> str | None:
    candidates = [preferred] if preferred else []
    # Probe newest-first so new installs pick up the latest Python automatically
    candidates.extend([f"python3.{m}" for m in range(20, 12, -1)])
    candidates.append("python3")
    seen = set()
    for candidate in candidates:
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        resolved = shutil.which(candidate)
        if not resolved:
            continue
        info = inspect_python(resolved)
        if info.get("supported"):
            return resolved
    return None


def find_venv_python(engine_id: str | None = None) -> Path:
    """Find the engine venv Python, preferring per-engine runtimes."""
    candidates = []
    if engine_id:
        candidates.append(RUNTIME_DIR / engine_id / "venv" / "bin" / "python")
    candidates.extend([
        CONFIG_DIR / "venv" / "bin" / "python",
        SCRIPT_DIR / "venv" / "bin" / "python",
    ])
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


VENV_PYTHON = find_venv_python()


def create_engine_venv(engine_id: str, python_command: str | None = None) -> Path:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    engine_root = RUNTIME_DIR / engine_id
    venv_python = engine_root / "venv" / "bin" / "python"
    if venv_python.exists():
        require_supported_python(venv_python)
        return venv_python

    python_bin = find_python_command(python_command or DEFAULT_ENGINE_PYTHONS.get(engine_id))
    if not python_bin:
        raise RuntimeError(
            f"Could not find a supported Python interpreter for {engine_id}. "
            f"Install Python {supported_python_string()} and rerun setup."
        )

    engine_root.mkdir(parents=True, exist_ok=True)
    subprocess.run([python_bin, "-m", "venv", str(engine_root / "venv")], check=True, timeout=120)
    require_supported_python(venv_python)
    return venv_python


def resolve_engine_python(
    engine_id: str,
    engine_python_overrides: dict[str, str] | None = None,
    use_system_python: bool = False,
) -> str:
    overrides = engine_python_overrides or {}
    if engine_id in overrides:
        require_supported_python(overrides[engine_id])
        return str(Path(overrides[engine_id]).expanduser())
    if use_system_python:
        python_bin = find_python_command(DEFAULT_ENGINE_PYTHONS.get(engine_id))
        if not python_bin:
            raise RuntimeError(
                f"No supported system Python found for {engine_id}. Need Python {supported_python_string()}.x."
            )
        require_supported_python(python_bin)
        return python_bin
    return str(find_venv_python(engine_id))


def print_runtime_banner(label: str = "smart-transcribe") -> None:
    version = platform.python_version()
    print(
        f"[runtime] {label}: python={sys.executable} version={version} platform={platform.platform()}",
        file=sys.stderr,
    )
    require_supported_python()


# =============================================================================
# API KEY RESOLUTION (env -> 1Password -> keys.env)
# =============================================================================

# 1Password vault + item names for each API key
_OP_ITEMS: dict[str, tuple[str, str]] = {
    "ASSEMBLYAI_API_KEY": ("Development", "AssemblyAI API Key"),
    "ELEVENLABS_API_KEY": ("Development", "ElevenLabs API Key"),
    "MISTRAL_API_KEY":    ("Development", "Mistral API Key"),
    "OPENAI_API_KEY":     ("Development", "OpenAI API Key"),
    "ANTHROPIC_API_KEY":  ("Development", "Anthropic API Key"),
    "GOOGLE_API_KEY":     ("Development", "Google API Key"),
    "HF_TOKEN":           ("Development", "Hugging Face API Key"),
}


def _op_command() -> str | None:
    """Find the 1Password CLI even when Codex launches with a minimal PATH."""
    candidates = [
        shutil.which("op"),
        "/opt/homebrew/bin/op",
        "/usr/local/bin/op",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(candidate)
    return None


def _op_env() -> dict[str, str]:
    """Build an op subprocess env, loading Claude's service token if needed."""
    env = {**os.environ}
    if env.get("OP_SERVICE_ACCOUNT_TOKEN"):
        return env
    settings_path = Path.home() / ".claude" / "settings.json"
    if not settings_path.exists():
        return env
    try:
        settings = json.loads(settings_path.read_text())
        token = settings.get("env", {}).get("OP_SERVICE_ACCOUNT_TOKEN")
    except Exception:
        token = None
    if token:
        env["OP_SERVICE_ACCOUNT_TOKEN"] = token
    return env


def resolve_key(env_var: str) -> str | None:
    """Resolve an API key lazily: env var -> 1Password -> keys.env. Caches in os.environ."""
    val = os.getenv(env_var)
    if val:
        return val

    if env_var in _OP_ITEMS:
        vault, item = _OP_ITEMS[env_var]
        op_cmd = _op_command()
        try:
            if not op_cmd:
                raise FileNotFoundError("op CLI not found")
            result = subprocess.run(
                [op_cmd, "item", "get", item, "--vault", vault,
                 "--fields", "label=credential", "--reveal"],
                capture_output=True, text=True, timeout=10,
                env=_op_env(),
            )
            if result.returncode == 0:
                val = result.stdout.strip()
                if val and not val.startswith("["):
                    os.environ[env_var] = val
                    return val
        except Exception:
            pass

    if KEYS_FILE.exists():
        for line in KEYS_FILE.read_text().splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                if k.strip() == env_var and v.strip():
                    os.environ[env_var] = v.strip()
                    return v.strip()
    return None


def resolve_key_status(env_var: str) -> dict[str, str | bool]:
    if os.getenv(env_var):
        return {"name": env_var, "resolved": True, "source": "env"}
    if env_var in _OP_ITEMS:
        vault, item = _OP_ITEMS[env_var]
        op_cmd = _op_command()
        try:
            if not op_cmd:
                raise FileNotFoundError("op CLI not found")
            result = subprocess.run(
                [op_cmd, "item", "get", item, "--vault", vault, "--fields", "label=credential", "--reveal"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
                env=_op_env(),
            )
            if result.returncode == 0 and result.stdout.strip() and not result.stdout.strip().startswith("["):
                return {"name": env_var, "resolved": True, "source": "1password"}
        except Exception:
            pass
    if KEYS_FILE.exists():
        for line in KEYS_FILE.read_text().splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                if k.strip() == env_var and v.strip():
                    return {"name": env_var, "resolved": True, "source": "keys.env"}
    return {"name": env_var, "resolved": False, "source": "missing"}


# =============================================================================
# DICTIONARY LOADING
# =============================================================================

def _resolve_dictionary_paths() -> tuple[Path, Path]:
    """Resolve dictionary and suggestions paths from config.json or seed fallback.

    On first run, copies the seed dictionary to the config dir.
    """
    if CONFIG_FILE.exists():
        try:
            config = json.loads(CONFIG_FILE.read_text())
            dict_path_str = config.get("dictionary_path", "")
            sugg_path_str = config.get("suggestions_log", "")
            if dict_path_str and Path(dict_path_str).exists():
                dict_path = Path(dict_path_str)
                sugg_path = Path(sugg_path_str) if sugg_path_str else CONFIG_DIR / "suggested-additions.jsonl"
                return dict_path, sugg_path
        except (json.JSONDecodeError, TypeError):
            pass

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    user_dict = CONFIG_DIR / "transcription-dictionary.json"
    user_sugg = CONFIG_DIR / "suggested-additions.jsonl"

    if not user_dict.exists() and SEED_DICTIONARY.exists():
        import shutil
        shutil.copy2(SEED_DICTIONARY, user_dict)
        print(f"Initialized user dictionary from seed -> {user_dict}", file=sys.stderr)

    config = {
        "dictionary_path": str(user_dict),
        "suggestions_log": str(user_sugg),
    }
    CONFIG_FILE.write_text(json.dumps(config, indent=2) + "\n")
    return user_dict, user_sugg


# Lazily initialized on first call to get_dictionary_paths()
_dict_paths: tuple[Path, Path] | None = None


def get_dictionary_paths() -> tuple[Path, Path]:
    """Get (dictionary_path, suggestions_path), initializing on first call."""
    global _dict_paths
    if _dict_paths is None:
        _dict_paths = _resolve_dictionary_paths()
    return _dict_paths


def load_dictionary(path: Path | None = None) -> dict:
    """Load the correction dictionary from a JSON file.

    Returns dict with 'corrections' (flat wrong->right), 'entities' (list),
    'speakers' (dict), and 'notes' (list).
    """
    if path is None:
        path, _ = get_dictionary_paths()

    result: dict = {"corrections": {}, "entities": [], "speakers": {}, "notes": []}
    if not path.exists():
        return result

    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as e:
        print(f"[ERROR] Could not read dictionary: {e}", file=sys.stderr)
        return result

    if "corrections" in data:
        for _cat, mappings in data["corrections"].items():
            if isinstance(mappings, dict):
                for wrong, right in mappings.items():
                    result["corrections"][wrong.lower()] = right
    if "entities" in data:
        for _cat, items in data["entities"].items():
            if isinstance(items, list):
                result["entities"].extend(items)
    if "speakers" in data:
        result["speakers"] = data["speakers"]
    if "notes" in data:
        result["notes"] = data["notes"]
    return result


def get_context_terms(dictionary: dict, limit: int = 500) -> list[str]:
    """Extract unique correct terms from dictionary for engine context biasing."""
    terms: set[str] = set()
    if dictionary.get("corrections"):
        terms.update(dictionary["corrections"].values())
    if dictionary.get("entities"):
        terms.update(dictionary["entities"])
    if dictionary.get("speakers"):
        terms.update(dictionary["speakers"].keys())
    return sorted(terms)[:limit]


def flatten_entities(entities: dict | list) -> list:
    """Normalise entities from JSON storage (dict of lists) to flat list."""
    if isinstance(entities, dict):
        result: list = []
        for items in entities.values():
            result.extend(items)
        return result
    return list(entities)


def merge_dicts(base: dict, overlay: dict) -> dict:
    """Deep-merge overlay onto base dict (context takes precedence)."""
    result = {
        "corrections": dict(base.get("corrections", {})),
        "entities": list(base.get("entities", [])),
        "speakers": dict(base.get("speakers", {})),
        "notes": list(base.get("notes", [])),
    }
    if overlay.get("corrections"):
        result["corrections"].update(overlay["corrections"])
    if overlay.get("entities"):
        seen = set(result["entities"])
        for item in overlay["entities"]:
            if item not in seen:
                result["entities"].append(item)
                seen.add(item)
    if overlay.get("speakers"):
        result["speakers"].update(overlay["speakers"])
    if overlay.get("notes"):
        seen_notes = set(result["notes"])
        for note in overlay["notes"]:
            if note not in seen_notes:
                result["notes"].append(note)
    return result


# =============================================================================
# AUDIO PREPROCESSING
# =============================================================================

def get_audio_duration(audio_path: str | Path) -> float:
    """Get audio duration in seconds via ffprobe."""
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(audio_path)],
            capture_output=True, text=True, timeout=30,
        )
        if r.returncode == 0 and r.stdout.strip():
            return float(r.stdout.strip())
    except Exception:
        pass
    return 0


def format_duration(seconds: float) -> str:
    """Format seconds as M:SS or H:MM:SS."""
    seconds = int(seconds)
    if seconds < 3600:
        return f"{seconds // 60}:{seconds % 60:02d}"
    return f"{seconds // 3600}:{(seconds % 3600) // 60:02d}:{seconds % 60:02d}"


def compress_audio(audio_path: Path) -> Path:
    """Compress audio to mono AAC .m4a if needed for reliable engine upload.

    Returns the original path unchanged if no conversion is needed,
    or a path to a cached temporary .m4a file.
    """
    ext = audio_path.suffix.lower()
    size_mb = audio_path.stat().st_size / (1024 * 1024)

    if ext in NATIVE_FORMATS and size_mb <= MAX_UPLOAD_MB:
        return audio_path

    reason = f"unsupported format ({ext})" if ext not in NATIVE_FORMATS else f"too large ({size_mb:.0f}MB > {MAX_UPLOAD_MB}MB)"
    print(f"Compressing audio ({reason})...", file=sys.stderr)

    tmp_path = Path(tempfile.gettempdir()) / f"st-{audio_path.stem}-{ext.lstrip('.')}.m4a"
    if tmp_path.exists() and tmp_path.stat().st_mtime >= audio_path.stat().st_mtime:
        compressed_mb = tmp_path.stat().st_size / (1024 * 1024)
        print(f"  Reusing cached conversion ({compressed_mb:.1f}MB)", file=sys.stderr)
        return tmp_path

    try:
        result = subprocess.run(
            ["ffmpeg", "-i", str(audio_path), "-c:a", "aac", "-b:a", "64k",
             "-ac", "1", "-y", str(tmp_path)],
            capture_output=True, text=True, timeout=300,
        )
        if result.returncode != 0:
            print(f"  ffmpeg conversion failed (exit {result.returncode}), using original", file=sys.stderr)
            return audio_path

        compressed_mb = tmp_path.stat().st_size / (1024 * 1024)
        if compressed_mb == 0:
            print("  ffmpeg produced empty file. Using original.", file=sys.stderr)
            return audio_path
        print(f"  Compressed: {size_mb:.0f}MB -> {compressed_mb:.1f}MB", file=sys.stderr)
        return tmp_path

    except FileNotFoundError:
        print("  ffmpeg not found. Install via 'brew install ffmpeg'. Using original.", file=sys.stderr)
        return audio_path
    except subprocess.TimeoutExpired:
        print("  ffmpeg timed out after 5 minutes. Using original.", file=sys.stderr)
        return audio_path


def convert_16khz_mono(audio_path: str) -> str:
    """Convert to 16kHz mono WAV for local models (Cohere, Voxtral-local)."""
    tmp = Path(tempfile.gettempdir()) / f"st-16k-{Path(audio_path).stem}.wav"
    src = Path(audio_path)
    if tmp.exists() and tmp.stat().st_mtime >= src.stat().st_mtime:
        return str(tmp)
    try:
        subprocess.run(
            ["ffmpeg", "-i", audio_path, "-ar", "16000", "-ac", "1", "-y", str(tmp)],
            capture_output=True, text=True, timeout=120,
        )
        if tmp.exists() and tmp.stat().st_size > 0:
            return str(tmp)
    except Exception:
        pass
    return audio_path


def chunk_audio(audio_path: str, max_mb: float = 24.0, overlap_seconds: int = 5) -> list[str]:
    """Split audio into <=max_mb chunks for models with file size limits (OpenAI: 25MB)."""
    path = Path(audio_path)
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb <= max_mb:
        return [audio_path]

    duration = get_audio_duration(audio_path)
    if duration <= 0:
        return [audio_path]

    chunk_dur = max(60, int(duration * (max_mb / size_mb) * 0.85))
    run_id = uuid.uuid4().hex[:8]
    chunks: list[str] = []
    start = 0
    idx = 0
    while start < duration:
        chunk_path = Path(tempfile.gettempdir()) / f"st-chunk-{run_id}-{idx:03d}.m4a"
        try:
            subprocess.run(
                ["ffmpeg", "-i", audio_path, "-ss", str(start),
                 "-t", str(chunk_dur + overlap_seconds),
                 "-c:a", "aac", "-b:a", "64k", "-ac", "1", "-y", str(chunk_path)],
                capture_output=True, text=True, timeout=120,
            )
            if chunk_path.exists() and chunk_path.stat().st_size > 0:
                chunks.append(str(chunk_path))
        except Exception:
            pass
        start += chunk_dur
        idx += 1
    return chunks or [audio_path]


# =============================================================================
# ENGINE SUBPROCESS RUNNERS
# =============================================================================

def make_engine_result(model_id: str, transcript: str = "", segments: list | None = None,
                       diarization: bool = False, duration: float = 0, elapsed: float = 0,
                       error: str | None = None, metadata: dict | None = None,
                       raw_response_path: str | None = None) -> dict:
    """Construct a normalized engine result dict."""
    from datetime import datetime
    return {
        "model": model_id,
        "timestamp": datetime.now().isoformat(),
        "duration_seconds": duration,
        "processing_time_seconds": round(elapsed),
        "status": "complete" if not error else "failed",
        "transcript": transcript,
        "segments": segments or [],
        "word_timestamps": [],
        "diarization": diarization,
        "error": error,
        "metadata": metadata or {},
        "raw_response_path": raw_response_path,
    }


def run_engine(model_id: str, script: str, env: dict, timeout: int = 3600,
               python_bin: str | None = None, log_path: Path | None = None,
               raw_output_path: Path | None = None) -> dict:
    """Run an engine subprocess, parse JSON output, return normalized result dict."""
    start = time.time()
    try:
        r = subprocess.run(
            [python_bin or str(VENV_PYTHON), "-c", script],
            capture_output=True, text=True, timeout=timeout, env=env,
        )
        elapsed = time.time() - start
        if log_path:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text(
                f"cmd_python={python_bin or str(VENV_PYTHON)}\nreturncode={r.returncode}\n\n[stdout]\n{r.stdout}\n\n[stderr]\n{r.stderr}\n"
            )

        if r.returncode != 0:
            err = r.stderr.strip()[:500] if r.stderr else "Non-zero exit"
            return make_engine_result(model_id, error=err, elapsed=elapsed)

        stdout = r.stdout.strip()
        if not stdout:
            return make_engine_result(model_id, error="Empty output", elapsed=elapsed)

        try:
            data = json.loads(stdout)
        except json.JSONDecodeError:
            return make_engine_result(model_id, transcript=stdout, elapsed=elapsed)
        if raw_output_path:
            raw_output_path.parent.mkdir(parents=True, exist_ok=True)
            raw_output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

        if "error" in data and data["error"]:
            return make_engine_result(model_id, error=str(data["error"]), elapsed=elapsed)

        return make_engine_result(
            model_id,
            transcript=data.get("text", ""),
            segments=data.get("segments", []),
            diarization=data.get("diarization", False),
            elapsed=elapsed,
            metadata=data.get("metadata", {}),
            raw_response_path=str(raw_output_path) if raw_output_path else None,
        )

    except subprocess.TimeoutExpired:
        return make_engine_result(model_id, error=f"Timeout after {timeout}s",
                                  elapsed=time.time() - start)
    except Exception as e:
        return make_engine_result(model_id, error=str(e), elapsed=time.time() - start)


def run_engine_text(script: str, env: dict, label: str, timeout: int = 3600,
                    python_bin: str | None = None, log_path: Path | None = None) -> str | None:
    """Run a transcription subprocess, parse JSON output, return transcript text."""
    print(f"Running {label}...", file=sys.stderr)
    try:
        result = subprocess.run(
            [python_bin or str(VENV_PYTHON), "-c", script],
            capture_output=True, text=True, timeout=timeout, env=env,
        )
        if log_path:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text(
                f"cmd_python={python_bin or str(VENV_PYTHON)}\nreturncode={result.returncode}\n\n[stdout]\n{result.stdout}\n\n[stderr]\n{result.stderr}\n"
            )
        stdout = result.stdout.strip()
        if result.returncode != 0:
            err_msg = result.stderr.strip()
            if not err_msg and stdout:
                try:
                    parsed = json.loads(stdout)
                    err_msg = parsed.get("error", stdout)
                except json.JSONDecodeError:
                    err_msg = stdout
            print(f"  Error: {err_msg[:400]}", file=sys.stderr)
            return None
        if not stdout:
            print("  Empty response", file=sys.stderr)
            return None
        try:
            data = json.loads(stdout)
            if data.get("error"):
                print(f"  {data['error']}", file=sys.stderr)
                return None
            text = data.get("text", "")
        except json.JSONDecodeError:
            text = stdout
        print(f"  Complete ({len(text)} chars)", file=sys.stderr)
        return text or None
    except subprocess.TimeoutExpired:
        print(f"  Timeout ({timeout // 60} min)", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  Exception: {e}", file=sys.stderr)
        return None


HTTP_RATE_LIMIT_SIGNALS = ("rate", "429", "limit", "overloaded", "capacity", "too many requests")
HTTP_SERVER_ERROR_SIGNALS = ("500", "502", "503", "504", "service unavailable",
                             "internal server error", "bad gateway", "gateway timeout",
                             "408", "request timeout")
HTTP_NON_RETRYABLE_SIGNALS = ("401", "403", "quota_exceeded", "quota exhausted",
                              "unauthorized", "forbidden", "invalid api key")
HTTP_RETRYABLE_SIGNALS = HTTP_RATE_LIMIT_SIGNALS + HTTP_SERVER_ERROR_SIGNALS
HTTP_BACKOFF_DELAYS_S = [10, 30, 90]


def retry_engine(func, max_retries: int = 3) -> dict:
    """Retry an engine function with exponential backoff on transient errors.

    Retryable conditions (3 attempts, 10s → 30s → 90s backoff):
    - HTTP 429 / rate limit / overloaded / capacity
    - HTTP 5xx server errors (500, 502, 503, 504, service unavailable)
    - HTTP 408 (request timeout)
    Non-retryable errors (auth failures, quota exhaustion) return immediately.
    """
    result = None
    for attempt in range(max_retries):
        result = func()
        if result["status"] == "complete":
            return result
        err = (result.get("error") or "").lower()
        if any(sig in err for sig in HTTP_NON_RETRYABLE_SIGNALS):
            return result
        is_rate_limit = any(sig in err for sig in HTTP_RATE_LIMIT_SIGNALS)
        is_server_error = any(sig in err for sig in HTTP_SERVER_ERROR_SIGNALS)
        if (is_rate_limit or is_server_error) and attempt < max_retries - 1:
            wait = HTTP_BACKOFF_DELAYS_S[attempt]
            category = "rate-limited" if is_rate_limit else "server error"
            print(f"  {category} (attempt {attempt + 1}/{max_retries}), retrying in {wait}s...",
                  file=sys.stderr)
            time.sleep(wait)
            continue
        return result
    return result  # type: ignore[return-value]


# =============================================================================
# DICTIONARY CORRECTIONS (pre-compiled regex)
# =============================================================================

_compiled_corrections: list[tuple[re.Pattern, str]] | None = None
_compiled_corrections_key: tuple[tuple[str, str], ...] | None = None


def compile_corrections(dictionary: dict) -> list[tuple[re.Pattern, str]]:
    """Pre-compile regex patterns for all dictionary corrections."""
    patterns = []
    for wrong, right in dictionary.get("corrections", {}).items():
        pattern = re.compile(r"\b" + re.escape(wrong) + r"\b", re.IGNORECASE)
        patterns.append((pattern, right))
    return patterns


def apply_dictionary_corrections(text: str, dictionary: dict) -> str:
    """Apply dictionary corrections using pre-compiled regex patterns."""
    global _compiled_corrections, _compiled_corrections_key
    if not dictionary.get("corrections"):
        return text
    corrections_key = tuple(sorted((str(k), str(v)) for k, v in dictionary.get("corrections", {}).items()))
    if _compiled_corrections is None or _compiled_corrections_key != corrections_key:
        _compiled_corrections = compile_corrections(dictionary)
        _compiled_corrections_key = corrections_key
    for pattern, replacement in _compiled_corrections:
        text = pattern.sub(replacement, text)
    return text


# =============================================================================
# LOGGING
# =============================================================================

def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def log_error(msg: str) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)


def check_ffmpeg_tools() -> dict[str, bool]:
    return {
        "ffmpeg": shutil.which("ffmpeg") is not None,
        "ffprobe": shutil.which("ffprobe") is not None,
    }


def write_status(status_path: Path, payload: dict[str, Any]) -> None:
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
