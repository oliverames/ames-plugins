#!/usr/bin/env python3
"""
Smart Transcribe - Ensemble Pipeline
======================================

Eight-model ensemble transcription with Opus 4.6 consensus merge and review.

Phases:
  1. Transcription (parallel cloud + sequential local)
  2. Merge (Opus 4.6 consensus with speaker scaffolding)
  3. Review (Opus 4.6 structural/flow correction)
  4. Format (apply dictionary corrections + output layout)

Usage:
  python3 ensemble.py audio.m4a
  python3 ensemble.py audio.m4a --preset standard
  python3 ensemble.py audio.m4a --preset full
  python3 ensemble.py audio.m4a --models scribe-v2,voxtral-small,assemblyai-u3-pro

Author: Oliver Ames
Last Updated: 2026-03-28
"""

import json
import os
import sys
import re
import time
import shutil
import subprocess
import tempfile
import argparse
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from common import (
    CONFIG_DIR, OUTPUT_DIR, NATIVE_FORMATS, MAX_UPLOAD_MB, VENV_PYTHON,
    resolve_key, load_dictionary, get_context_terms,
    compress_audio, convert_16khz_mono, chunk_audio,
    get_audio_duration, format_duration,
    make_engine_result, run_engine, retry_engine,
    apply_dictionary_corrections, log,
)

# Rich progress display (optional)
try:
    from rich.console import Console
    from rich.live import Live
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    HAS_RICH = True
    console = Console(stderr=True)
except ImportError:
    HAS_RICH = False
    console = None


# ===========================================================================
# CONFIGURATION
# ===========================================================================

ENSEMBLE_CONFIG_PATH = CONFIG_DIR / "ensemble-config.json"


# ===========================================================================
# MODEL DEFINITIONS
# ===========================================================================

MODELS = {
    "scribe-v2": {
        "name": "ElevenLabs Scribe v2",
        "type": "cloud",
        "env_key": "ELEVENLABS_API_KEY",
        "cost_per_hour": "$0.50",
        "accuracy": "2.3% AA-WER (best)",
        "order": 1,
    },
    "voxtral-small": {
        "name": "Mistral Voxtral Small",
        "type": "cloud",
        "env_key": "MISTRAL_API_KEY",
        "cost_per_hour": "$0.30",
        "accuracy": "2.9% AA-WER",
        "order": 2,
    },
    "gemini-3-pro": {
        "name": "Google Gemini 3 Pro",
        "type": "cloud",
        "env_key": "GOOGLE_API_KEY",
        "cost_per_hour": "$0.40",
        "accuracy": "2.9% AA-WER",
        "order": 3,
    },
    "assemblyai-u3-pro": {
        "name": "AssemblyAI Universal-3 Pro",
        "type": "cloud",
        "env_key": "ASSEMBLYAI_API_KEY",
        "cost_per_hour": "$0.65",
        "accuracy": "Best diarization",
        "order": 4,
    },
    "gpt4o-transcribe": {
        "name": "OpenAI GPT-4o Transcribe",
        "type": "cloud",
        "env_key": "OPENAI_API_KEY",
        "cost_per_hour": "$0.60",
        "accuracy": "RL-trained ASR",
        "order": 5,
    },
    "gpt4o-mini-transcribe": {
        "name": "OpenAI GPT-4o Mini Trans.",
        "type": "cloud",
        "env_key": "OPENAI_API_KEY",
        "cost_per_hour": "$0.30",
        "accuracy": "Decorrelated errors",
        "order": 6,
    },
    "voxtral-mini-local": {
        "name": "Voxtral Mini Realtime",
        "type": "local",
        "runtime": "mlx-audio",
        "cost_per_hour": "Free (local)",
        "accuracy": "4B params, 4-bit",
        "order": 7,
    },
    "cohere-transcribe": {
        "name": "Cohere Transcribe",
        "type": "local",
        "runtime": "pytorch-mps",
        "cost_per_hour": "Free (local)",
        "accuracy": "2B params, Conformer",
        "order": 8,
    },
}

PRESETS = {
    "quick": {
        "name": "Quick (1 model)",
        "models": ["voxtral-small"],
        "description": "Best accuracy/simplicity balance",
    },
    "standard": {
        "name": "Standard (3 models)",
        "models": ["scribe-v2", "voxtral-small", "assemblyai-u3-pro"],
        "description": "Good ensemble, low cost",
    },
    "full": {
        "name": "Full (all 8)",
        "models": list(MODELS.keys()),
        "description": "Maximum accuracy, all models",
    },
}


# Aliases for backward compat within this file
_log = log


# ===========================================================================
# ENSEMBLE CONFIG
# ===========================================================================

DEFAULT_CONFIG = {
    "default_profile": "standard",
    "last_models_used": ["scribe-v2", "voxtral-small", "assemblyai-u3-pro"],
    "local_models": {
        "voxtral_mini": {
            "enabled": True,
            "model_id": "mlx-community/Voxtral-Mini-4B-Realtime-2602-4bit",
            "runtime": "mlx-audio",
        },
        "cohere_transcribe": {
            "enabled": True,
            "model_id": "CohereLabs/cohere-transcribe-03-2026",
            "runtime": "pytorch-mps",
            "fallback_to_cpu": True,
            "check_for_mlx": True,
        },
    },
    "transcription_dictionary_path": "",
    "output_directory": "",
    "merge_model": "claude-opus-4-6-20250414",
    "review_model": "claude-opus-4-6-20250414",
    "keep_raw_transcripts": False,
    "keep_work_directory": False,
}


def load_ensemble_config():
    if ENSEMBLE_CONFIG_PATH.exists():
        try:
            saved = json.loads(ENSEMBLE_CONFIG_PATH.read_text())
            config = {**DEFAULT_CONFIG, **saved}
            return config
        except (json.JSONDecodeError, TypeError):
            pass
    return dict(DEFAULT_CONFIG)


def save_ensemble_config(config):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    ENSEMBLE_CONFIG_PATH.write_text(json.dumps(config, indent=2) + "\n")


# ===========================================================================
# DEPENDENCY CHECKS
# ===========================================================================

def check_api_keys(selected_models):
    """Returns list of (model_id, key_name) for missing keys."""
    missing = []
    seen_keys = set()
    for mid in selected_models:
        model = MODELS[mid]
        if model["type"] != "cloud":
            continue
        key_name = model["env_key"]
        if key_name in seen_keys:
            continue
        seen_keys.add(key_name)
        if not resolve_key(key_name):
            missing.append((mid, key_name))
    return missing


def check_local_deps(selected_models):
    """Returns list of (model_id, issue_description) for missing deps."""
    issues = []
    for mid in selected_models:
        model = MODELS[mid]
        if model["type"] != "local":
            continue
        runtime = model.get("runtime", "")
        if runtime == "mlx-audio":
            try:
                r = subprocess.run(
                    [str(VENV_PYTHON), "-c", "from mlx_audio.stt.utils import load; print('ok')"],
                    capture_output=True, text=True, timeout=15,
                )
                if r.returncode != 0:
                    issues.append((mid, "mlx-audio not installed (pip install mlx-audio)"))
            except Exception:
                issues.append((mid, "Could not check mlx-audio"))
        elif runtime == "pytorch-mps":
            try:
                r = subprocess.run(
                    [str(VENV_PYTHON), "-c",
                     "import torch, transformers, soundfile, librosa; "
                     "print('mps' if torch.backends.mps.is_available() else 'cpu')"],
                    capture_output=True, text=True, timeout=15,
                )
                if r.returncode != 0:
                    issues.append((mid, "Missing deps: torch, transformers, soundfile, librosa"))
                elif "cpu" in r.stdout:
                    _log(f"  Note: {mid} will use CPU fallback (MPS not available)")
            except Exception:
                issues.append((mid, "Could not check PyTorch deps"))
    return issues


# Aliases for common functions used throughout this file
_make_result = make_engine_result
_run_engine = run_engine
_retry_engine = retry_engine


# ===========================================================================
# ENGINE 1: ElevenLabs Scribe v2
# ===========================================================================

def transcribe_elevenlabs(audio_path, context_terms, **kwargs):
    key = resolve_key("ELEVENLABS_API_KEY") or ""
    if not key:
        return _make_result("elevenlabs-scribe-v2", error="ELEVENLABS_API_KEY not set")

    script = '''
import json, os, sys
try:
    from elevenlabs import ElevenLabs
    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    with open(os.environ["ST_AUDIO_PATH"], "rb") as f:
        result = client.speech_to_text.convert(
            audio=f,
            model_id="scribe_v2",
            language_code="en",
            diarize=True,
            tag_audio_events=True,
        )
    text = result.text if hasattr(result, "text") else str(result)
    segments = []
    diarization = False
    if hasattr(result, "words") and result.words:
        cur_speaker = None
        cur_seg = None
        for w in result.words:
            spk = getattr(w, "speaker_id", None) or getattr(w, "speaker", None)
            wtext = getattr(w, "text", "")
            wstart = getattr(w, "start", 0)
            wend = getattr(w, "end", 0)
            if spk != cur_speaker:
                if cur_seg:
                    segments.append(cur_seg)
                cur_speaker = spk
                cur_seg = {"start": wstart, "end": wend, "speaker": str(spk or ""), "text": wtext}
                diarization = bool(spk)
            elif cur_seg:
                cur_seg["text"] += " " + wtext
                cur_seg["end"] = wend
        if cur_seg:
            segments.append(cur_seg)
    print(json.dumps({"text": text, "segments": segments, "diarization": diarization}))
except Exception as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(1)
'''
    env = {**os.environ, "ELEVENLABS_API_KEY": key, "ST_AUDIO_PATH": audio_path}
    return _retry_engine(lambda: _run_engine("elevenlabs-scribe-v2", script, env))


# ===========================================================================
# ENGINE 2: Mistral Voxtral Small (cloud)
# ===========================================================================

def transcribe_voxtral_small(audio_path, context_terms, **kwargs):
    key = resolve_key("MISTRAL_API_KEY") or ""
    if not key:
        return _make_result("mistral-voxtral-small", error="MISTRAL_API_KEY not set")

    filtered = [t for t in context_terms if " " not in t and "," not in t][:100]

    script = '''
import json, os, sys, time
try:
    from mistralai import Mistral
    from mistralai.models import File
    client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])
    audio_file = os.environ["ST_AUDIO_PATH"]
    bias = json.loads(os.environ.get("ST_BIAS", "[]"))
    with open(audio_file, "rb") as f:
        content = f.read()
    ext = os.path.splitext(audio_file)[1].lstrip(".").lower()
    ct = {"m4a":"audio/m4a","mp3":"audio/mpeg","wav":"audio/wav","ogg":"audio/ogg","flac":"audio/flac","webm":"audio/webm"}.get(ext, "audio/m4a")
    fobj = File(fileName=os.path.basename(audio_file), content=content, content_type=ct)

    # Use file upload for large files
    size_mb = len(content) / (1024*1024)
    if size_mb > 40:
        uploaded = client.files.upload(file=fobj)
        for _poll in range(120):  # 2-minute timeout
            ret = client.files.retrieve(file_id=uploaded.id)
            if ret.status == "processed":
                break
            elif ret.status == "error":
                raise RuntimeError(f"Upload failed: {ret.status_details}")
            time.sleep(1)
        else:
            raise RuntimeError("Upload timed out after 120s")
        resp = client.audio.transcriptions.complete(
            file_id=uploaded.id, model="voxtral-mini-latest", language="en",
            diarize=True, timestamp_granularities=["segment"], context_bias=bias)
        try:
            client.files.delete(file_id=uploaded.id)
        except Exception:
            pass
    else:
        resp = client.audio.transcriptions.complete(
            file=fobj, model="voxtral-mini-latest", language="en",
            diarize=True, timestamp_granularities=["segment"], context_bias=bias)

    segs = []
    diar = False
    if hasattr(resp, "segments") and resp.segments:
        for s in resp.segments:
            seg = {"start": getattr(s,"start",0), "end": getattr(s,"end",0),
                   "text": getattr(s,"text",""), "speaker": getattr(s,"speaker","")}
            if seg["speaker"]:
                diar = True
            segs.append(seg)
    print(json.dumps({"text": resp.text, "segments": segs, "diarization": diar}))
except Exception as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(1)
'''
    env = {**os.environ, "MISTRAL_API_KEY": key, "ST_AUDIO_PATH": audio_path,
           "ST_BIAS": json.dumps(filtered)}
    return _retry_engine(lambda: _run_engine("mistral-voxtral-small", script, env))


# ===========================================================================
# ENGINE 3: Google Gemini 3 Pro (audio input)
# ===========================================================================

def transcribe_gemini(audio_path, context_terms, **kwargs):
    key = resolve_key("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY", "")
    if not key:
        return _make_result("google-gemini-3-pro", error="GOOGLE_API_KEY not set")

    script = '''
import json, os, sys, re
try:
    from google import genai

    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
    audio_file = os.environ["ST_AUDIO_PATH"]

    # Upload audio file
    uploaded = client.files.upload(file=audio_file)

    prompt = """Transcribe this audio recording verbatim. Output ONLY the transcript text.
If there are multiple speakers, label them as Speaker 1, Speaker 2, etc. on separate lines.
Format: **Speaker N:** text
Preserve all spoken words exactly. Do not summarize or paraphrase."""

    response = client.models.generate_content(
        model="gemini-3-pro",
        contents=[prompt, uploaded],
    )
    text = response.text if hasattr(response, "text") else str(response)

    # Parse speaker labels from the text
    segments = []
    diar = False
    lines = text.strip().split("\\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Check for speaker label pattern
        m = re.match(r"\\*\\*(?:Speaker\\s+)?(\\w+(?:\\s+\\w+)?):\\*\\*\\s*(.*)", line)
        if m:
            diar = True
            segments.append({"start": 0, "end": 0, "speaker": m.group(1), "text": m.group(2)})
        elif segments:
            segments[-1]["text"] += " " + line
        else:
            segments.append({"start": 0, "end": 0, "speaker": "", "text": line})

    print(json.dumps({"text": text, "segments": segments, "diarization": diar}))
except Exception as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(1)
'''
    env = {**os.environ, "GOOGLE_API_KEY": key, "ST_AUDIO_PATH": audio_path}
    return _retry_engine(lambda: _run_engine("google-gemini-3-pro", script, env))


# ===========================================================================
# ENGINE 4: AssemblyAI Universal-3 Pro
# ===========================================================================

def transcribe_assemblyai(audio_path, context_terms, num_speakers=2, **kwargs):
    key = resolve_key("ASSEMBLYAI_API_KEY") or ""
    if not key:
        return _make_result("assemblyai-u3-pro", error="ASSEMBLYAI_API_KEY not set")

    boost_json = json.dumps(context_terms[:300])

    script = f'''
import json, os, sys
try:
    import assemblyai as aai
    aai.settings.api_key = os.environ["ASSEMBLYAI_API_KEY"]
    transcriber = aai.Transcriber()
    boost = json.loads(os.environ.get("ST_BOOST", "[]")) or None

    config = aai.TranscriptionConfig(
        speech_model=aai.SpeechModel.best,
        speaker_labels=True,
        speakers_expected={num_speakers},
        language_code="en",
        word_boost=boost,
        boost_param="high",
        auto_highlights=True,
        entity_detection=True,
        punctuate=True,
        format_text=True,
    )

    transcript = transcriber.transcribe(os.environ["ST_AUDIO_PATH"], config)

    if transcript.status == aai.TranscriptStatus.error:
        print(json.dumps({{"error": transcript.error}}))
        sys.exit(1)

    segments = []
    diar = False
    full_text = ""

    if transcript.utterances:
        diar = True
        for u in transcript.utterances:
            segments.append({{
                "start": u.start / 1000.0 if u.start else 0,
                "end": u.end / 1000.0 if u.end else 0,
                "speaker": f"Speaker {{u.speaker}}",
                "text": u.text,
            }})
        # Build full text with speaker labels
        cur_spk = None
        parts = []
        for u in transcript.utterances:
            if u.speaker != cur_spk:
                cur_spk = u.speaker
                parts.append(f"\\n**Speaker {{u.speaker}}:** {{u.text}}")
            else:
                parts.append(u.text)
        full_text = "\\n".join(parts).strip()
    else:
        full_text = transcript.text or ""

    print(json.dumps({{"text": full_text, "segments": segments, "diarization": diar}}))
except Exception as e:
    print(json.dumps({{"error": str(e)}}))
    sys.exit(1)
'''
    env = {**os.environ, "ASSEMBLYAI_API_KEY": key, "ST_AUDIO_PATH": audio_path,
           "ST_BOOST": boost_json}
    return _retry_engine(lambda: _run_engine("assemblyai-u3-pro", script, env))


# ===========================================================================
# ENGINE 5: OpenAI GPT-4o Transcribe
# ===========================================================================

def transcribe_gpt4o(audio_path, context_terms, **kwargs):
    key = resolve_key("OPENAI_API_KEY") or ""
    if not key:
        return _make_result("openai-gpt4o-transcribe", error="OPENAI_API_KEY not set")

    # Chunk audio if > 25MB
    chunks = chunk_audio(audio_path, max_mb=25)

    script = '''
import json, os, sys
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    audio_file = os.environ["ST_AUDIO_PATH"]
    with open(audio_file, "rb") as f:
        resp = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=f,
            language="en",
            response_format="verbose_json",
        )
    text = resp.text if hasattr(resp, "text") else str(resp)
    segments = []
    if hasattr(resp, "segments") and resp.segments:
        for s in resp.segments:
            segments.append({
                "start": getattr(s, "start", 0),
                "end": getattr(s, "end", 0),
                "speaker": "",
                "text": getattr(s, "text", ""),
            })
    print(json.dumps({"text": text, "segments": segments, "diarization": False}))
except Exception as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(1)
'''

    if len(chunks) == 1:
        env = {**os.environ, "OPENAI_API_KEY": key, "ST_AUDIO_PATH": chunks[0]}
        return _retry_engine(lambda: _run_engine("openai-gpt4o-transcribe", script, env))
    else:
        # Multi-chunk: transcribe each, concatenate
        all_text = []
        chunk_start = time.time()
        for i, chunk_path in enumerate(chunks):
            _log(f"  GPT-4o chunk {i+1}/{len(chunks)}...")
            env = {**os.environ, "OPENAI_API_KEY": key, "ST_AUDIO_PATH": chunk_path}
            result = _retry_engine(lambda: _run_engine("openai-gpt4o-transcribe", script, env))
            if result["status"] == "complete" and result["transcript"]:
                all_text.append(result["transcript"])
            elif result["error"]:
                return result
        # Join chunks (simple concatenation; overlap alignment is approximate)
        joined = " ".join(all_text)
        return _make_result("openai-gpt4o-transcribe", transcript=joined,
                            elapsed=time.time() - chunk_start)


# ===========================================================================
# ENGINE 6: OpenAI GPT-4o Mini Transcribe
# ===========================================================================

def transcribe_gpt4o_mini(audio_path, context_terms, **kwargs):
    key = resolve_key("OPENAI_API_KEY") or ""
    if not key:
        return _make_result("openai-gpt4o-mini-transcribe", error="OPENAI_API_KEY not set")

    chunks = chunk_audio(audio_path, max_mb=25)

    script = '''
import json, os, sys
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    with open(os.environ["ST_AUDIO_PATH"], "rb") as f:
        resp = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=f,
            language="en",
            response_format="verbose_json",
        )
    text = resp.text if hasattr(resp, "text") else str(resp)
    segments = []
    if hasattr(resp, "segments") and resp.segments:
        for s in resp.segments:
            segments.append({
                "start": getattr(s, "start", 0),
                "end": getattr(s, "end", 0),
                "speaker": "",
                "text": getattr(s, "text", ""),
            })
    print(json.dumps({"text": text, "segments": segments, "diarization": False}))
except Exception as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(1)
'''
    if len(chunks) == 1:
        env = {**os.environ, "OPENAI_API_KEY": key, "ST_AUDIO_PATH": chunks[0]}
        return _retry_engine(lambda: _run_engine("openai-gpt4o-mini-transcribe", script, env))
    else:
        all_text = []
        chunk_start = time.time()
        for i, chunk_path in enumerate(chunks):
            _log(f"  GPT-4o Mini chunk {i+1}/{len(chunks)}...")
            env = {**os.environ, "OPENAI_API_KEY": key, "ST_AUDIO_PATH": chunk_path}
            result = _retry_engine(lambda: _run_engine("openai-gpt4o-mini-transcribe", script, env))
            if result["status"] == "complete" and result["transcript"]:
                all_text.append(result["transcript"])
            elif result["error"]:
                return result
        return _make_result("openai-gpt4o-mini-transcribe", transcript=" ".join(all_text),
                            elapsed=time.time() - chunk_start)


# ===========================================================================
# ENGINE 7: Voxtral Mini Realtime (local, mlx-audio)
# ===========================================================================

def transcribe_voxtral_mini_local(audio_path, context_terms, **kwargs):
    # Convert to WAV - soundfile (used by mlx-audio) can't read m4a/aac
    wav_path = convert_16khz_mono(audio_path)

    script = '''
import json, os, sys
try:
    from mlx_audio.stt.utils import load
    model_id = "mlx-community/Voxtral-Mini-4B-Realtime-2602-4bit"
    model = load(model_id)
    audio_file = os.environ["ST_AUDIO_PATH"]
    result = model.generate(audio_file, verbose=False)
    # STTOutput has .text and .segments attributes
    text = result.text if hasattr(result, "text") else str(result)
    segments = []
    if hasattr(result, "segments") and result.segments:
        for s in result.segments:
            seg = s if isinstance(s, dict) else {}
            segments.append({
                "start": seg.get("start", 0),
                "end": seg.get("end", 0),
                "speaker": "",
                "text": seg.get("text", ""),
            })
    print(json.dumps({"text": text, "segments": segments, "diarization": False}))
except Exception as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(1)
'''
    env = {**os.environ, "ST_AUDIO_PATH": wav_path}
    return _run_engine("voxtral-mini-local", script, env, timeout=600)


# ===========================================================================
# ENGINE 8: Cohere Transcribe (local, PyTorch + MPS)
# ===========================================================================

def transcribe_cohere_local(audio_path, context_terms, **kwargs):
    # Convert to 16kHz mono as required by Cohere
    wav_path = convert_16khz_mono(audio_path)

    script = '''
import json, os, sys
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
try:
    import torch
    import soundfile as sf
    from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq

    model_id = "CohereLabs/cohere-transcribe-03-2026"

    # Check for MLX community conversion first
    try:
        from mlx_audio.stt.utils import load
        model = load("mlx-community/cohere-transcribe-03-2026-4bit")
        result = model.generate(os.environ["ST_AUDIO_PATH"], verbose=False)
        text = result.text if hasattr(result, "text") else str(result)
        print(json.dumps({"text": text, "segments": [], "diarization": False}))
        sys.exit(0)
    except Exception:
        pass  # MLX version not available, use PyTorch

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
    model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id, trust_remote_code=True).to(device)

    audio, sr = sf.read(os.environ["ST_AUDIO_PATH"])

    # Resample if not 16kHz
    if sr != 16000:
        import librosa
        audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
        sr = 16000

    inputs = processor(audio, sampling_rate=sr, return_tensors="pt").to(device)
    with torch.no_grad():
        ids = model.generate(**inputs, max_new_tokens=4096)
    text = processor.batch_decode(ids, skip_special_tokens=True)[0]
    print(json.dumps({"text": text, "segments": [], "diarization": False}))
except Exception as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(1)
'''
    env = {**os.environ, "ST_AUDIO_PATH": wav_path, "PYTORCH_ENABLE_MPS_FALLBACK": "1"}
    return _run_engine("cohere-transcribe", script, env, timeout=600)


# ===========================================================================
# ENGINE DISPATCH
# ===========================================================================

ENGINE_FUNCS = {
    "scribe-v2": transcribe_elevenlabs,
    "voxtral-small": transcribe_voxtral_small,
    "gemini-3-pro": transcribe_gemini,
    "assemblyai-u3-pro": transcribe_assemblyai,
    "gpt4o-transcribe": transcribe_gpt4o,
    "gpt4o-mini-transcribe": transcribe_gpt4o_mini,
    "voxtral-mini-local": transcribe_voxtral_mini_local,
    "cohere-transcribe": transcribe_cohere_local,
}


# ===========================================================================
# PROGRESS DISPLAY
# ===========================================================================

class ProgressTracker:
    """Tracks and displays progress for all engines."""

    def __init__(self, selected_models, audio_name, audio_duration):
        self.models = selected_models
        self.audio_name = audio_name
        self.audio_duration = audio_duration
        self.statuses = {m: "queued" for m in selected_models}
        self.times = {m: 0 for m in selected_models}
        self.start_time = time.time()
        self._live = None

    def update(self, model_id, status, elapsed=0):
        self.statuses[model_id] = status
        if elapsed:
            self.times[model_id] = elapsed

    def _build_display(self):
        cloud = [m for m in self.models if MODELS[m]["type"] == "cloud"]
        local = [m for m in self.models if MODELS[m]["type"] == "local"]
        completed = sum(1 for s in self.statuses.values() if s in ("complete", "failed"))
        total_elapsed = time.time() - self.start_time

        if HAS_RICH:
            return self._build_rich(cloud, local, completed, total_elapsed)
        return self._build_plain(cloud, local, completed, total_elapsed)

    def _status_icon(self, status):
        icons = {
            "queued": "waiting",
            "running": "........",
            "complete": "==========",
            "failed": "FAILED",
        }
        return icons.get(status, status)

    def _build_rich(self, cloud, local, completed, total_elapsed):
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column(width=12)
        table.add_column(width=30)
        table.add_column(width=20)

        if cloud:
            table.add_row(Text("Cloud Models", style="bold"), "", "")
            for m in cloud:
                s = self.statuses[m]
                name = MODELS[m]["name"]
                if s == "complete":
                    bar = Text(f"[{'=' * 10}]", style="green")
                    info = Text(f"Complete ({format_duration(self.times[m])})", style="green")
                elif s == "failed":
                    bar = Text("[FAILED   ]", style="red bold")
                    info = Text("Failed", style="red")
                elif s == "running":
                    ticks = min(8, int((time.time() - self.start_time) / 10))
                    bar = Text(f"[{'=' * ticks}{' ' * (10 - ticks)}]", style="yellow")
                    info = Text("Processing...", style="yellow")
                else:
                    bar = Text("[waiting   ]", style="dim")
                    info = Text("Queued", style="dim")
                table.add_row(bar, Text(name), info)

        if local:
            table.add_row("", "", "")
            table.add_row(Text("Local Models (sequential)", style="bold"), "", "")
            for m in local:
                s = self.statuses[m]
                name = MODELS[m]["name"]
                if s == "complete":
                    bar = Text(f"[{'=' * 10}]", style="green")
                    info = Text(f"Complete ({format_duration(self.times[m])})", style="green")
                elif s == "failed":
                    bar = Text("[FAILED   ]", style="red bold")
                    info = Text("Failed", style="red")
                elif s == "running":
                    ticks = min(8, int((time.time() - self.start_time) / 10))
                    bar = Text(f"[{'=' * ticks}{' ' * (10 - ticks)}]", style="yellow")
                    info = Text("Processing...", style="yellow")
                else:
                    bar = Text("[waiting   ]", style="dim")
                    info = Text("Queued", style="dim")
                table.add_row(bar, Text(name), info)

        summary = f"Completed: {completed}/{len(self.models)} | Elapsed: {format_duration(total_elapsed)}"
        header = f"Smart Transcribe - Ensemble Pipeline\n" \
                 f"Audio: {self.audio_name} ({format_duration(self.audio_duration)})\n" \
                 f"Models: {len(self.models)} selected ({len([m for m in self.models if MODELS[m]['type']=='cloud'])} cloud, " \
                 f"{len([m for m in self.models if MODELS[m]['type']=='local'])} local)"

        return Panel(
            table,
            title=header,
            subtitle=summary,
            border_style="blue",
        )

    def _build_plain(self, cloud, local, completed, total_elapsed):
        lines = [
            f"\nSmart Transcribe - Ensemble Pipeline",
            f"Audio: {self.audio_name} ({format_duration(self.audio_duration)})",
            f"Models: {len(self.models)} selected",
            "",
        ]
        for section, label in [(cloud, "Cloud Models"), (local, "Local Models (sequential)")]:
            if section:
                lines.append(f"  {label}")
                for m in section:
                    s = self.statuses[m]
                    name = MODELS[m]["name"][:28].ljust(28)
                    if s == "complete":
                        lines.append(f"  [==========] {name} Complete ({format_duration(self.times[m])})")
                    elif s == "failed":
                        lines.append(f"  [FAILED    ] {name} Failed")
                    elif s == "running":
                        lines.append(f"  [====      ] {name} Processing...")
                    else:
                        lines.append(f"  [waiting   ] {name} Queued")
                lines.append("")
        lines.append(f"  Completed: {completed}/{len(self.models)} | Elapsed: {format_duration(total_elapsed)}")
        return "\n".join(lines)

    def print_snapshot(self):
        """Print current state (plain text mode)."""
        display = self._build_display()
        if isinstance(display, str):
            if sys.stderr.isatty():
                # Clear screen and reprint (basic ANSI)
                line_count = display.count("\n") + 1
                sys.stderr.write(f"\033[{line_count}A\033[J")
            sys.stderr.write(display + "\n")
            sys.stderr.flush()


# ===========================================================================
# PHASE 1: ORCHESTRATION
# ===========================================================================

def run_transcription(selected_models, audio_path, context_terms, num_speakers=2,
                      work_dir=None):
    """Run all selected engines. Cloud in parallel, local sequentially."""
    audio_name = Path(audio_path).name
    duration = get_audio_duration(audio_path)
    tracker = ProgressTracker(selected_models, audio_name, duration)

    cloud_models = [m for m in selected_models if MODELS[m]["type"] == "cloud"]
    local_models = [m for m in selected_models if MODELS[m]["type"] == "local"]

    results = {}

    # Print initial state
    if HAS_RICH and console:
        _log("")  # Spacer
    else:
        # Print blank lines for plain-text overwrite
        blank_lines = 6 + len(selected_models) + (2 if local_models else 0)
        sys.stderr.write("\n" * blank_lines)

    # Run cloud models in parallel
    if cloud_models:
        with ThreadPoolExecutor(max_workers=len(cloud_models)) as executor:
            futures = {}
            for mid in cloud_models:
                tracker.update(mid, "running")
                func = ENGINE_FUNCS[mid]
                future = executor.submit(func, audio_path, context_terms,
                                         num_speakers=num_speakers)
                futures[future] = mid

            if HAS_RICH and console:
                with Live(tracker._build_display(), console=console, refresh_per_second=2) as live:
                    # Poll for cloud completions
                    while futures:
                        done = {f for f in futures if f.done()}
                        for f in done:
                            mid = futures.pop(f)
                            try:
                                result = f.result()
                                tracker.update(mid, result["status"],
                                               result.get("processing_time_seconds", 0))
                                results[mid] = result
                            except Exception as e:
                                tracker.update(mid, "failed")
                                results[mid] = _make_result(mid, error=str(e))
                            live.update(tracker._build_display())
                        time.sleep(0.5)

                    # Now run local models within the same live display
                    for mid in local_models:
                        tracker.update(mid, "running")
                        live.update(tracker._build_display())
                        func = ENGINE_FUNCS[mid]
                        result = func(audio_path, context_terms, num_speakers=num_speakers)
                        tracker.update(mid, result["status"],
                                       result.get("processing_time_seconds", 0))
                        results[mid] = result
                        live.update(tracker._build_display())
            else:
                # Plain text mode: poll and update
                tracker.print_snapshot()
                while futures:
                    done = {f for f in futures if f.done()}
                    for f in done:
                        mid = futures.pop(f)
                        try:
                            result = f.result()
                            tracker.update(mid, result["status"],
                                           result.get("processing_time_seconds", 0))
                            results[mid] = result
                        except Exception as e:
                            tracker.update(mid, "failed")
                            results[mid] = _make_result(mid, error=str(e))
                        tracker.print_snapshot()
                    time.sleep(1)

                # Local models (plain text)
                for mid in local_models:
                    tracker.update(mid, "running")
                    tracker.print_snapshot()
                    func = ENGINE_FUNCS[mid]
                    result = func(audio_path, context_terms, num_speakers=num_speakers)
                    tracker.update(mid, result["status"],
                                   result.get("processing_time_seconds", 0))
                    results[mid] = result
                    tracker.print_snapshot()
    else:
        # Only local models selected
        for mid in local_models:
            tracker.update(mid, "running")
            _log(f"  Running {MODELS[mid]['name']}...")
            func = ENGINE_FUNCS[mid]
            result = func(audio_path, context_terms, num_speakers=num_speakers)
            tracker.update(mid, result["status"],
                           result.get("processing_time_seconds", 0))
            results[mid] = result

    # Save raw transcripts to work dir
    if work_dir:
        raw_dir = Path(work_dir) / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        for mid in selected_models:
            if mid in results:
                order = MODELS[mid]["order"]
                name_slug = mid.replace("-", "_")
                out_path = raw_dir / f"{order:02d}-{name_slug}.json"
                out_path.write_text(json.dumps(results[mid], indent=2, ensure_ascii=False) + "\n")

    # Summary
    succeeded = sum(1 for r in results.values() if r["status"] == "complete")
    failed = [mid for mid, r in results.items() if r["status"] == "failed"]
    _log(f"\n  Phase 1 complete: {succeeded}/{len(selected_models)} succeeded")
    if failed:
        for mid in failed:
            _log(f"  FAILED: {MODELS[mid]['name']} - {results[mid].get('error', 'unknown')[:100]}")

    return results


# ===========================================================================
# PHASE 2: MERGE (Opus 4.6 Consensus)
# ===========================================================================

def find_scaffolding_transcript(results, selected_models):
    """Find the best diarization transcript for speaker scaffolding.
    Priority: AssemblyAI > ElevenLabs > GPT-4o > none."""
    priority = ["assemblyai-u3-pro", "scribe-v2", "gpt4o-transcribe"]
    for mid in priority:
        if mid in results and results[mid]["status"] == "complete" and results[mid].get("diarization"):
            return mid
    # Fallback: any model with diarization
    for mid in selected_models:
        if mid in results and results[mid]["status"] == "complete" and results[mid].get("diarization"):
            return mid
    return None


def run_merge(results, selected_models, dictionary):
    """Phase 2: Opus 4.6 consensus merge of all transcripts."""
    anthropic_key = resolve_key("ANTHROPIC_API_KEY") or ""
    if not anthropic_key:
        _log("  ANTHROPIC_API_KEY not set. Delegating merge to host model.")
        return None, []  # None signals "merge not performed"

    # Find scaffolding transcript
    scaffold_id = find_scaffolding_transcript(results, selected_models)
    scaffold_transcript = ""
    if scaffold_id:
        scaffold_transcript = results[scaffold_id]["transcript"]
        _log(f"  Speaker scaffolding: {MODELS[scaffold_id]['name']}")
    else:
        _log("  No diarization available - treating as single speaker")

    # Build the other transcripts
    other_transcripts = []
    for mid in selected_models:
        if mid == scaffold_id:
            continue
        if mid in results and results[mid]["status"] == "complete" and results[mid]["transcript"]:
            other_transcripts.append(f"### {MODELS[mid]['name']}\n{results[mid]['transcript']}")

    if not other_transcripts and not scaffold_transcript:
        return "", []

    # Build dictionary context sections (only include non-empty ones)
    dict_sections = []
    if dictionary.get("corrections"):
        entries = list(dictionary["corrections"].items())[:200]
        dict_context = "\n".join(f"- {k} -> {v}" for k, v in entries)
        dict_sections.append(f"KNOWN CORRECTIONS (apply these strictly):\n{dict_context}")

    entities = dictionary.get("entities", [])[:100]
    if entities:
        dict_sections.append(f"KNOWN ENTITIES (preserve exact spelling):\n{', '.join(entities)}")

    notes = dictionary.get("notes", [])
    if notes:
        notes_str = "\n".join(f"- {n}" for n in notes)
        dict_sections.append(f"IMPORTANT NOTES:\n{notes_str}")

    dict_block = "\n\n".join(dict_sections) if dict_sections else ""

    # Merge prompt (from plan)
    prompt = f"""You are performing a consensus merge of multiple automatic speech recognition (ASR) transcripts of the same audio recording. Your goal is to produce the single most accurate transcript possible.

SPEAKER STRUCTURE:
The following speaker-diarized transcript provides the structural scaffolding. Use its speaker labels and segment boundaries as the framework. Do not change speaker assignments unless multiple other transcripts clearly disagree.

{scaffold_transcript if scaffold_transcript else "(No diarized transcript available - treat as single speaker)"}

ADDITIONAL TRANSCRIPTS FOR CONSENSUS:
The following transcripts were produced by different ASR models with different architectures. They will have different errors. Where they agree, confidence is high. Where they disagree, use majority vote. Where there is no clear majority, use the version that is most grammatically coherent and contextually plausible.

{chr(10).join(other_transcripts)}

{dict_block}

MERGE RULES:
1. For each segment, compare the word choices across all available transcripts.
2. Where all transcripts agree: use that text exactly.
3. Where a majority agrees: use the majority version.
4. Where there is no majority: choose the version that best fits the surrounding context, grammar, and plausibility. Note these as low-confidence passages by wrapping them in [[double brackets]].
5. Proper nouns: if ANY transcript capitalizes or formats a word as a proper noun and the context supports it, prefer the proper noun version.
6. Numbers and acronyms: prefer the most specific/formatted version (e.g., "$4,500" over "four thousand five hundred", "BCBS" over "B C B S").
7. Preserve natural speech patterns: keep "um", "uh", filler words ONLY if a majority of transcripts include them. Remove if a majority omit them.
8. Do not add, invent, or hallucinate any words not present in at least one source transcript.
9. Maintain the speaker labels from the scaffolding transcript throughout.

OUTPUT:
Produce the merged transcript with speaker labels. After the transcript, add a section called "Merge Notes" listing:
- Total low-confidence passages (count of [[double bracket]] segments)
- Any passages where models strongly disagreed
- Any proper nouns that appeared in inconsistent forms across models"""

    _log("  Phase 2: Consensus Merge (Opus 4.6)...")

    prompt_file = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(prompt)
            prompt_file = f.name

        script = '''
import os, sys, json
try:
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    with open(os.environ["ST_PROMPT_FILE"], "r") as f:
        prompt = f.read()
    response = client.messages.create(
        model="claude-opus-4-6-20250414",
        max_tokens=16384,
        thinking={"type": "enabled", "budget_tokens": 10000},
        messages=[{"role": "user", "content": prompt}],
    )
    parts = [b.text for b in response.content if hasattr(b, "text")]
    print("\\n".join(parts))
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
'''
        env = {**os.environ, "ANTHROPIC_API_KEY": anthropic_key, "ST_PROMPT_FILE": prompt_file}
        r = subprocess.run(
            [str(VENV_PYTHON), "-c", script],
            capture_output=True, text=True, timeout=600, env=env,
        )

        if r.returncode == 0 and r.stdout.strip():
            merged = r.stdout.strip()
            # Split out merge notes if present
            notes = []
            if "Merge Notes" in merged:
                parts = merged.split("Merge Notes", 1)
                merged = parts[0].strip()
                if len(parts) > 1:
                    for line in parts[1].strip().splitlines():
                        line = line.strip().lstrip("-").lstrip("*").strip()
                        if line:
                            notes.append(line)
            _log(f"  Merge complete ({len(merged)} chars)")
            return merged, notes
        else:
            err = r.stderr.strip()[:200] if r.stderr else "Empty response"
            _log(f"  Merge failed: {err}")
            # Retry once
            _log("  Retrying merge...")
            r2 = subprocess.run(
                [str(VENV_PYTHON), "-c", script],
                capture_output=True, text=True, timeout=600, env=env,
            )
            if r2.returncode == 0 and r2.stdout.strip():
                merged = r2.stdout.strip()
                if "Merge Notes" in merged:
                    merged = merged.split("Merge Notes", 1)[0].strip()
                return merged, []
            # Fallback to best single transcript
            _log("  Merge failed twice. Using best single transcript as fallback.")
            for mid in ["scribe-v2", "voxtral-small", "assemblyai-u3-pro"]:
                if mid in results and results[mid]["status"] == "complete":
                    return results[mid]["transcript"], []
            return "", []

    except subprocess.TimeoutExpired:
        _log("  Merge timed out (10 min)")
        return "", []
    except Exception as e:
        _log(f"  Merge exception: {e}")
        return "", []
    finally:
        if prompt_file:
            Path(prompt_file).unlink(missing_ok=True)


# ===========================================================================
# PHASE 3: REVIEW (Opus 4.6 Structural Pass)
# ===========================================================================

def run_review(merged_transcript):
    """Phase 3: Opus structural/flow review pass."""
    anthropic_key = resolve_key("ANTHROPIC_API_KEY") or ""
    if not anthropic_key:
        _log("  ANTHROPIC_API_KEY not set. Delegating review to host model.")
        return None  # None signals "review not performed"

    if not merged_transcript:
        return merged_transcript

    prompt = f"""You are performing a final review pass on a merged transcript. This transcript was already produced by consensus from multiple different ASR models. The words are likely correct.

Your job is ONLY to fix:
1. Sentence boundaries: Insert periods, question marks, or other punctuation where sentences clearly end but the ASR models ran them together.
2. Paragraph breaks: Add paragraph breaks at natural topic shifts or speaker turn continuations that are too long.
3. Capitalization: Fix capitalization after sentence boundaries you corrected.
4. Obvious grammatical artifacts: If an ASR merge produced a grammatically impossible construction (e.g., repeated articles "the the", dangling conjunctions at segment joins), fix them.
5. Remove any remaining [[double bracket]] markers, applying your best judgment to resolve them.

DO NOT:
- Change word choices (the merge already resolved those)
- Remove filler words or verbal tics (those were intentionally preserved if present)
- Alter speaker labels
- Add or remove content
- "Clean up" casual speech to sound more formal

TRANSCRIPT:
{merged_transcript}

OUTPUT:
The reviewed transcript with all corrections applied. After the transcript, provide a brief "Review Notes" section listing the number and types of corrections made."""

    _log("  Phase 3: Structural Review (Opus 4.6)...")

    prompt_file = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(prompt)
            prompt_file = f.name

        script = '''
import os, sys
try:
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    with open(os.environ["ST_PROMPT_FILE"], "r") as f:
        prompt = f.read()
    response = client.messages.create(
        model="claude-opus-4-6-20250414",
        max_tokens=16384,
        thinking={"type": "enabled", "budget_tokens": 8000},
        messages=[{"role": "user", "content": prompt}],
    )
    parts = [b.text for b in response.content if hasattr(b, "text")]
    print("\\n".join(parts))
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
'''
        env = {**os.environ, "ANTHROPIC_API_KEY": anthropic_key, "ST_PROMPT_FILE": prompt_file}
        r = subprocess.run(
            [str(VENV_PYTHON), "-c", script],
            capture_output=True, text=True, timeout=600, env=env,
        )

        if r.returncode == 0 and r.stdout.strip():
            reviewed = r.stdout.strip()
            # Strip review notes section
            if "Review Notes" in reviewed:
                reviewed = reviewed.split("Review Notes", 1)[0].strip()
            _log(f"  Review complete ({len(reviewed)} chars)")
            return reviewed
        else:
            _log(f"  Review failed, using merged transcript as-is")
            return merged_transcript

    except subprocess.TimeoutExpired:
        _log("  Review timed out")
        return merged_transcript
    except Exception as e:
        _log(f"  Review exception: {e}")
        return merged_transcript
    finally:
        if prompt_file:
            Path(prompt_file).unlink(missing_ok=True)


# ===========================================================================
# PHASE 4: FORMAT AND OUTPUT
# ===========================================================================


def save_output(transcript, audio_path, results, selected_models,
                description=None, output_dir=None, pipeline_desc=None):
    """Save the final transcript and audio to a dated folder."""
    audio_path = Path(audio_path)
    file_date = datetime.now().strftime("%Y-%m-%d")

    # Generate title from first 200 chars if not provided
    if not description:
        words = transcript.split()[:8]
        description = " ".join(words)
        # Clean for filename
        description = re.sub(r'[\\/*?:"<>|]', "", description)[:50]
        if not description:
            description = "Transcript"

    clean_desc = re.sub(r'[\\/*?:"<>|]', "", description)[:50]
    folder_name = f"{file_date} {clean_desc}"

    base_dir = Path(output_dir) if output_dir else OUTPUT_DIR
    out_dir = base_dir / folder_name
    counter = 2
    while out_dir.exists():
        out_dir = base_dir / f"{folder_name} ({counter})"
        counter += 1
    out_dir.mkdir(parents=True, exist_ok=True)

    # Copy audio
    audio_filename = f"{file_date} {clean_desc} - Audio{audio_path.suffix}"
    shutil.copy2(audio_path, out_dir / audio_filename)

    # Build engine summary
    succeeded = [mid for mid in selected_models
                 if mid in results and results[mid]["status"] == "complete"]
    failed = [mid for mid in selected_models
              if mid in results and results[mid]["status"] == "failed"]
    engines_str = ", ".join(MODELS[m]["name"] for m in succeeded)

    # Build metadata header
    md_content = f"""# {description}

**Date:** {file_date}
**Transcribed:** {datetime.now().strftime("%Y-%m-%d %I:%M %p")}
**Source:** {audio_filename}
**Engines:** {engines_str} ({len(succeeded)} succeeded{f', {len(failed)} failed' if failed else ''})
**Pipeline:** {pipeline_desc or f"Ensemble ({len(selected_models)} models)"}

---

## Transcript

{transcript}
"""

    transcript_filename = f"{file_date} {clean_desc}.md"
    final_path = out_dir / transcript_filename
    final_path.write_text(md_content)

    return str(final_path), str(out_dir)


# ===========================================================================
# WORK DIRECTORY & ERROR LOG
# ===========================================================================

def create_work_dir():
    """Create a temporary work directory for raw transcripts and logs."""
    work_dir = Path(tempfile.gettempdir()) / f"smart-transcribe-work-{int(time.time())}"
    work_dir.mkdir(parents=True, exist_ok=True)
    return str(work_dir)


def log_error(work_dir, model_id, error_msg):
    """Append error to the work directory error log."""
    if not work_dir:
        return
    log_path = Path(work_dir) / "error.log"
    timestamp = datetime.now().isoformat()
    with open(log_path, "a") as f:
        f.write(f"[{timestamp}] {model_id}: {error_msg}\n")


# ===========================================================================
# CLI AND MAIN
# ===========================================================================

def select_models_interactive(config):
    """Display model selection and return list of selected model IDs."""
    _log("\n  Model Selection")
    _log("  ---------------")
    _log("")

    # Show presets
    for key, preset in PRESETS.items():
        marker = " *" if key == config.get("default_profile") else ""
        _log(f"  [{key}] {preset['name']}: {preset['description']}{marker}")
    _log(f"  [custom] Pick individual models")
    _log(f"  [last] Reuse last selection: {', '.join(config.get('last_models_used', []))}")
    _log("")

    # In non-interactive mode (piped), use default
    if not sys.stdin.isatty():
        profile = config.get("default_profile", "standard")
        _log(f"  Non-interactive mode: using '{profile}' preset")
        return PRESETS.get(profile, PRESETS["standard"])["models"]

    # Show model table
    _log("  Available Models:")
    _log(f"  {'#':<4} {'Name':<30} {'Type':<8} {'Cost/hr':<12} {'Accuracy'}")
    _log(f"  {'-'*4} {'-'*30} {'-'*8} {'-'*12} {'-'*20}")
    for mid, info in sorted(MODELS.items(), key=lambda x: x[1]["order"]):
        _log(f"  {info['order']:<4} {info['name']:<30} {info['type']:<8} {info['cost_per_hour']:<12} {info['accuracy']}")
    _log("")

    return config.get("last_models_used", PRESETS["standard"]["models"])


def main():
    parser = argparse.ArgumentParser(
        description="Smart Transcribe - Ensemble Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("audio_file", help="Audio file to transcribe")
    parser.add_argument("--preset", choices=["quick", "standard", "full", "custom", "last"],
                        help="Model selection preset")
    parser.add_argument("--models", help="Comma-separated model IDs (overrides preset)")
    parser.add_argument("-d", "--description", help="Title for output folder")
    parser.add_argument("--num-speakers", type=int, default=2,
                        help="Expected number of speakers (default: 2)")
    parser.add_argument("--output", help="Output directory")
    parser.add_argument("--keep-work-dir", action="store_true",
                        help="Keep raw transcripts and work directory")
    parser.add_argument("--skip-merge", action="store_true",
                        help="Skip Phase 2 merge (use best single transcript)")
    parser.add_argument("--skip-review", action="store_true",
                        help="Skip Phase 3 review pass")
    args = parser.parse_args()

    # Validate venv
    if not VENV_PYTHON.exists():
        _log(f"ERROR: Python venv not found at {VENV_PYTHON}")
        _log("Run /smart-transcribe:setup first.")
        sys.exit(1)

    # Validate audio file
    audio_path = Path(args.audio_file).resolve()
    if not audio_path.exists():
        _log(f"ERROR: File not found: {audio_path}")
        sys.exit(1)

    # Load config
    config = load_ensemble_config()

    # Determine selected models
    if args.models:
        selected = [m.strip() for m in args.models.split(",")]
        invalid = [m for m in selected if m not in MODELS]
        if invalid:
            _log(f"ERROR: Unknown models: {', '.join(invalid)}")
            _log(f"Available: {', '.join(MODELS.keys())}")
            sys.exit(1)
    elif args.preset:
        if args.preset == "last":
            selected = config.get("last_models_used", PRESETS["standard"]["models"])
        elif args.preset == "custom":
            selected = select_models_interactive(config)
        else:
            selected = PRESETS[args.preset]["models"]
    else:
        selected = select_models_interactive(config)

    # Check dependencies
    missing_keys = check_api_keys(selected)
    if missing_keys:
        _log("ERROR: Missing API keys:")
        for mid, key_name in missing_keys:
            _log(f"  {MODELS[mid]['name']}: {key_name}")
        sys.exit(1)

    local_issues = check_local_deps(selected)
    if local_issues:
        for mid, issue in local_issues:
            _log(f"WARNING: {MODELS[mid]['name']}: {issue}")
            selected.remove(mid)
        if not selected:
            _log("ERROR: No models available after dependency check")
            sys.exit(1)

    # Save selection for next time
    config["last_models_used"] = selected
    save_ensemble_config(config)

    # Setup
    dictionary = load_dictionary()
    context_terms = get_context_terms(dictionary)
    upload_path = compress_audio(audio_path)
    work_dir = create_work_dir()

    _log(f"\n  Audio: {audio_path.name}")
    _log(f"  Dictionary: {len(dictionary.get('corrections', {}))} corrections, "
         f"{len(dictionary.get('entities', []))} entities")
    _log(f"  Models: {len(selected)} ({', '.join(MODELS[m]['name'] for m in selected)})")

    # ======================================================================
    # PHASE 1: TRANSCRIPTION
    # ======================================================================
    results = run_transcription(selected, str(upload_path), context_terms,
                                num_speakers=args.num_speakers, work_dir=work_dir)

    # Log errors
    for mid, result in results.items():
        if result["status"] == "failed":
            log_error(work_dir, mid, result.get("error", "unknown"))

    succeeded = {mid: r for mid, r in results.items() if r["status"] == "complete"}
    if not succeeded:
        _log("\nERROR: All engines failed. Check error log:")
        _log(f"  {work_dir}/error.log")
        sys.exit(1)

    # ======================================================================
    # PHASE 2: MERGE
    # ======================================================================
    merge_performed = False
    merge_delegated = False
    if len(succeeded) > 1 and not args.skip_merge:
        merged, merge_notes = run_merge(results, selected, dictionary)
        if merged is None:
            # None = no API key, delegate to host model
            merge_delegated = True
        elif merged:
            # Non-empty string = merge succeeded
            merge_performed = True
        # else: empty string = merge attempted but failed, fall through
    else:
        merged = None
        merge_notes = []

    # If merge didn't produce a usable result, use best single transcript
    if not merged:
        for mid in ["scribe-v2", "voxtral-small", "assemblyai-u3-pro"]:
            if mid in succeeded:
                merged = succeeded[mid]["transcript"]
                break
        else:
            merged = list(succeeded.values())[0]["transcript"]

    if not merged:
        _log("ERROR: No transcript produced")
        sys.exit(1)

    # ======================================================================
    # PHASE 3: REVIEW
    # ======================================================================
    review_performed = False
    review_delegated = False
    if not args.skip_review and len(succeeded) > 1 and merge_performed:
        reviewed = run_review(merged)
        if reviewed is None:
            review_delegated = True
            final_text = merged
        elif reviewed:
            final_text = reviewed
            review_performed = True
        else:
            final_text = merged
    elif not args.skip_review and merge_delegated:
        # If merge is delegated, review is also delegated
        review_delegated = True
        final_text = merged
    else:
        final_text = merged

    # ======================================================================
    # PHASE 4: FORMAT
    # ======================================================================
    _log("  Phase 4: Formatting...")
    final_text = apply_dictionary_corrections(final_text, dictionary)

    # Determine pipeline description for header
    merge_needed = merge_delegated and len(succeeded) > 1
    if merge_performed and review_performed:
        pipeline_desc = f"Ensemble ({len(selected)} models) with Opus 4.6 merge + review"
    elif merge_performed:
        pipeline_desc = f"Ensemble ({len(selected)} models) with Opus 4.6 merge"
    elif merge_needed:
        pipeline_desc = f"Ensemble ({len(selected)} models), merge pending (host model)"
    else:
        pipeline_desc = f"Ensemble ({len(selected)} models)"

    transcript_path, output_folder = save_output(
        final_text, audio_path, results, selected,
        description=args.description,
        output_dir=args.output,
        pipeline_desc=pipeline_desc,
    )

    # If merge was delegated, auto-keep work dir so host model can read transcripts
    if merge_needed:
        _log(f"  Work directory preserved for host-model merge: {work_dir}")
    elif not args.keep_work_dir and not config.get("keep_work_directory"):
        shutil.rmtree(work_dir, ignore_errors=True)
        work_dir = None

    # Final summary
    succeeded_count = len(succeeded)
    failed_count = len(results) - succeeded_count
    total_time = sum(r.get("processing_time_seconds", 0) for r in results.values())

    _log("")
    _log("  Pipeline complete.")
    _log(f"  Models used: {len(selected)} ({succeeded_count} succeeded"
         f"{f', {failed_count} failed' if failed_count else ''})")
    _log(f"  Total time: {format_duration(total_time)}")
    _log(f"  Output: {transcript_path}")
    if merge_needed:
        _log("  Merge/review: delegated to host model")
    _log("")

    # Output JSON status to stdout (for command integration)
    status = {
        "transcript_path": transcript_path,
        "output_dir": output_folder,
        "work_dir": work_dir,
        "merge_performed": merge_performed,
        "review_performed": review_performed,
        "merge_needed": merge_needed,
        "models_succeeded": list(succeeded.keys()),
        "scaffold_model": find_scaffolding_transcript(results, selected),
    }
    print(json.dumps(status))
    return status


if __name__ == "__main__":
    main()
