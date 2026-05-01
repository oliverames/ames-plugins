import json
import tempfile
import unittest
import importlib.util
from pathlib import Path
from unittest import mock

import sys

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import common  # noqa: E402

spec = importlib.util.spec_from_file_location("smart_transcribe", SCRIPT_DIR / "smart-transcribe.py")
smart_transcribe = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(smart_transcribe)


class SmartTranscribeTests(unittest.TestCase):
    def test_default_engine_set(self):
        self.assertEqual(
            smart_transcribe.DEFAULT_ENGINES,
            ["assemblyai-u3-pro", "scribe-v2", "voxtral-small", "gemini-3-pro"],
        )

    def test_python_version_supported(self):
        self.assertTrue(common.python_version_supported((3, 13, 0)))
        self.assertTrue(common.python_version_supported((3, 14, 0)))
        self.assertFalse(common.python_version_supported((3, 12, 9)))

    def test_parse_engine_python_overrides(self):
        overrides = smart_transcribe.parse_engine_python_overrides("scribe-v2=/tmp/py,cohere-transcribe=/usr/bin/python3.13")
        self.assertEqual(overrides["scribe-v2"], "/tmp/py")
        self.assertEqual(overrides["cohere-transcribe"], "/usr/bin/python3.13")

    def test_normalize_segments(self):
        normalized = smart_transcribe.normalize_segments(
            [{"speaker": "Speaker A", "start": 1.0, "end": 2.0, "text": "hello", "confidence": 0.9}],
            "scribe-v2",
        )
        self.assertEqual(normalized[0]["speaker"], "Speaker A")
        self.assertEqual(normalized[0]["source_engine"], "scribe-v2")

    def test_manual_merge_bundle_generation(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            bundle = smart_transcribe.emit_manual_merge_bundle(output_dir, {
                "AssemblyAI Universal-3 Pro": {"status": "complete", "text": "alpha"},
                "ElevenLabs Scribe v2": {"status": "failed", "text": "", "failure_reason": "boom"},
            })
            text = bundle.read_text()
            self.assertIn("Recommended base transcript: AssemblyAI Universal-3 Pro", text)
            self.assertIn("boom", text)

    def test_agent_merge_bundle_generation(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            bundle = smart_transcribe.emit_agent_merge_bundle(
                output_dir,
                {"Cohere Transcribe (local)": "hello", "Mistral Voxtral Small": "hallo"},
                {"corrections": {"hallo": "hello"}, "entities": ["Cohere"], "notes": ["test note"]},
                source_file="/tmp/audio.m4a",
                mode="merge",
            )
            text = bundle.read_text()
            self.assertIn("Agent Merge Bundle", text)
            self.assertIn("hallo -> hello", text)
            self.assertIn("Cohere Transcribe (local)", text)

    def test_rate_limit_detection(self):
        self.assertTrue(smart_transcribe._is_rate_limited_merge_error("429 rate limit exceeded"))
        self.assertTrue(smart_transcribe._is_rate_limited_merge_error("service overloaded, try again later"))
        self.assertFalse(smart_transcribe._is_rate_limited_merge_error("invalid prompt format"))

    def test_structured_merge_output_parser(self):
        payload = {
            "metadata": {
                "title": "Budget Call",
                "speakers": ["Oliver", "Beth"],
                "summary": "Budget discussion.",
                "date_mentioned": "2026-04-21",
            },
            "transcript": "**Oliver:** Hello",
            "transparency_report": {
                "applied": ["assemblee ai -> AssemblyAI"],
                "uncertain": [],
                "preserved": ["yeah"],
            },
            "suggestions": ["AssemblyAI (company name)"],
        }
        parsed = smart_transcribe._coerce_structured_merge(json.dumps(payload))
        self.assertIsNotNone(parsed)
        transcript, suggestions, metadata, transparency = parsed
        self.assertEqual(transcript, "**Oliver:** Hello")
        self.assertEqual(metadata["title"], "Budget Call")
        self.assertIn("AssemblyAI", suggestions[0])
        self.assertIn("APPLIED:", transparency)

    @mock.patch.object(smart_transcribe.shutil, "which")
    @mock.patch.object(smart_transcribe, "_run_merge_runner")
    def test_merge_falls_back_to_codex_on_rate_limit(self, mock_run_merge_runner, mock_which):
        mock_which.side_effect = lambda name: f"/usr/bin/{name}"
        mock_run_merge_runner.side_effect = [
            RuntimeError("429 rate limit exceeded"),
            ('{"title":"T","speakers":[],"summary":"S","date_mentioned":"2026-04-09"}\n---SPLIT---\nMerged transcript\n---SPLIT---\nAPPLIED:\n- None\n---SPLIT---\nNone', ""),
        ]
        transcript, suggestions, metadata, transparency, merge_info = smart_transcribe.merge_with_llm(
            {"AssemblyAI Universal-3 Pro": "hello world"},
            {"corrections": {}, "entities": [], "speakers": {}, "notes": []},
        )
        self.assertEqual(transcript, "Merged transcript")
        self.assertEqual(metadata["title"], "T")
        self.assertEqual(merge_info["runner"], "codex")
        self.assertIn("429", merge_info["fallback_reason"])

    @mock.patch.object(smart_transcribe, "check_engine_runtime")
    @mock.patch.object(smart_transcribe, "resolve_engine_python")
    @mock.patch.object(smart_transcribe, "resolve_key_status")
    @mock.patch.object(smart_transcribe, "check_ffmpeg_tools")
    def test_doctor_report(self, mock_ffmpeg, mock_key_status, mock_resolve_engine_python, mock_check_engine_runtime):
        mock_ffmpeg.return_value = {"ffmpeg": True, "ffprobe": True}
        mock_key_status.side_effect = lambda key: {"name": key, "resolved": True, "source": "env"}
        mock_resolve_engine_python.side_effect = lambda engine_id, *_: f"/tmp/{engine_id}-python"
        mock_check_engine_runtime.side_effect = lambda engine_id, python_bin: {"ok": True, "python": python_bin}
        report = smart_transcribe.build_doctor_report(["scribe-v2", "assemblyai-u3-pro"])
        self.assertEqual(report["engines"], ["scribe-v2", "assemblyai-u3-pro"])
        self.assertTrue(report["ffmpeg"]["ffmpeg"])
        self.assertIn("primary", report["merge_runners"])
        self.assertTrue(report["engine_checks"]["scribe-v2"]["ok"])


if __name__ == "__main__":
    unittest.main()
