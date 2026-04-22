#!/usr/bin/env python3
"""Host-aware preflight for the wrap-up skill.

The script prints a secret-safe snapshot of the current environment so the
agent can decide which wrap-up phases are valid. It intentionally reports
structure and availability, not secret values.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


COMMANDS = [
    "git",
    "rg",
    "jq",
    "node",
    "npm",
    "pnpm",
    "python3",
    "op",
    "validate-skill",
    "backup-claude",
    "backup-telegram",
    "commit-push-all",
]


def run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
            check=False,
        )
    except Exception as exc:  # pragma: no cover - defensive shell boundary
        return 1, "", str(exc)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def git_root(cwd: Path) -> str | None:
    code, out, _ = run(["git", "rev-parse", "--show-toplevel"], cwd)
    return out if code == 0 and out else None


def git_status(root: str | None) -> dict[str, Any] | None:
    if not root:
        return None
    root_path = Path(root)
    branch_code, branch, _ = run(["git", "status", "--short", "--branch"], root_path)
    porcelain_code, porcelain, _ = run(["git", "status", "--porcelain"], root_path)
    return {
        "root": root,
        "status_available": branch_code == 0,
        "branch": branch.splitlines()[0] if branch else "",
        "dirty_count": len(porcelain.splitlines()) if porcelain_code == 0 and porcelain else 0,
        "porcelain": porcelain.splitlines()[:30] if porcelain else [],
    }


def safe_json_keys(path: Path, skip_keys: set[str] | None = None) -> dict[str, Any]:
    """Scan formatted JSON settings without parsing or reporting secret values."""
    skip_keys = skip_keys or set()
    if not path.exists():
        return {"exists": False}
    top_level: set[str] = set()
    section_keys: dict[str, set[str]] = {
        "enabledPlugins": set(),
        "extraKnownMarketplaces": set(),
        "hooks": set(),
        "permissions": set(),
    }
    current_section: str | None = None
    current_depth = 0
    try:
        handle = path.open()
    except OSError as exc:
        return {"exists": True, "parse_error": str(exc)}
    with handle:
        for raw in handle:
            stripped = raw.strip()
            if not stripped:
                continue
            if current_section:
                if (
                    current_section != "__skip__"
                    and raw.startswith("    ")
                    and not raw.startswith("      ")
                ):
                    nested = extract_json_key(stripped)
                    if nested:
                        section_keys[current_section].add(nested)
                current_depth += stripped.count("{") - stripped.count("}")
                if current_depth <= 0:
                    current_section = None
                    current_depth = 0
                continue
            if not raw.startswith("  ") or raw.startswith("    "):
                continue
            key = extract_json_key(stripped)
            if not key:
                continue
            top_level.add(key)
            if key == "env" or key in skip_keys:
                current_section = "__skip__"
                current_depth = stripped.count("{") - stripped.count("}")
            elif key in section_keys:
                current_section = key
                current_depth = stripped.count("{") - stripped.count("}")
            if current_depth <= 0:
                current_section = None
                current_depth = 0
    result: dict[str, Any] = {"exists": True, "top_level_keys": sorted(top_level)}
    for key, values in section_keys.items():
        if key in top_level and key not in skip_keys:
            result[f"{key}_count"] = len(values)
            result[f"{key}_keys"] = sorted(values)[:50]
    return result


def extract_json_key(stripped_line: str) -> str | None:
    if not stripped_line.startswith('"') or '":' not in stripped_line:
        return None
    return stripped_line.split('":', 1)[0].strip('"')


def safe_toml_keys(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False}
    try:
        import tomllib  # Python 3.11+

        data = tomllib.loads(path.read_text())
    except Exception as exc:
        keys = fallback_toml_keys(path)
        if keys:
            return {
                "exists": True,
                "top_level_keys": keys["top_level_keys"],
                "table_count": keys["table_count"],
                "parser": "fallback",
            }
        return {"exists": True, "parse_error": str(exc)}
    return {
        "exists": True,
        "top_level_keys": sorted(data.keys()),
        "table_count": len([v for v in data.values() if isinstance(v, dict)]),
        "parser": "tomllib",
    }


def fallback_toml_keys(path: Path) -> dict[str, Any] | None:
    """Extract top-level TOML keys without reading values."""
    top_level: set[str] = set()
    table_count = 0
    try:
        lines = path.read_text().splitlines()
    except OSError:
        return None
    in_table = False
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            in_table = True
            table_count += 1
            table_name = line.strip("[]").split(".", 1)[0].strip().strip('"')
            if table_name:
                top_level.add(table_name)
            continue
        if "=" in line and not in_table and not raw.startswith((" ", "\t")):
            key = line.split("=", 1)[0].strip().strip('"')
            if key:
                top_level.add(key)
    return {"top_level_keys": sorted(top_level), "table_count": table_count}


def find_ames_claude(home: Path) -> str | None:
    candidates = [
        home / "Developer" / "Projects" / "ames-claude",
        home
        / "Library"
        / "Mobile Documents"
        / "com~apple~CloudDocs"
        / "Developer"
        / "Projects"
        / "ames-claude",
    ]
    for candidate in candidates:
        if candidate.exists():
            try:
                return str(candidate.resolve())
            except OSError:
                return str(candidate)
    return None


def infer_host(requested: str, env: dict[str, str], home: Path) -> dict[str, Any]:
    path = env.get("PATH", "")
    codex_markers = [
        any(k.startswith("CODEX") for k in env),
        "Codex.app" in path,
        (home / ".codex").exists(),
    ]
    claude_markers = [
        any(k.startswith("CLAUDE") for k in env),
        (home / ".claude" / "settings.json").exists(),
        (home / ".claude" / "projects").exists(),
    ]
    if requested in {"claude", "codex"}:
        host = requested
        confidence = "explicit"
    elif codex_markers[0] or codex_markers[1]:
        host = "codex"
        confidence = "medium"
    elif claude_markers[0]:
        host = "claude"
        confidence = "medium"
    elif sum(codex_markers) > sum(claude_markers):
        host = "codex"
        confidence = "low"
    elif sum(claude_markers) > sum(codex_markers):
        host = "claude"
        confidence = "low"
    else:
        host = "ambiguous"
        confidence = "low"
    return {
        "host": host,
        "confidence": confidence,
        "codex_markers": codex_markers,
        "claude_markers": claude_markers,
    }


def collect(host: str) -> dict[str, Any]:
    home = Path.home()
    cwd = Path.cwd()
    env = dict(os.environ)
    root = git_root(cwd)
    ames_claude = find_ames_claude(home)
    command_paths = {cmd: shutil.which(cmd) for cmd in COMMANDS}
    return {
        "cwd": str(cwd),
        "host_inference": infer_host(host, env, home),
        "commands": command_paths,
        "paths": {
            "claude_settings": str(home / ".claude" / "settings.json"),
            "claude_projects": str(home / ".claude" / "projects"),
            "codex_config": str(home / ".codex" / "config.toml"),
            "codex_sessions": str(home / ".codex" / "sessions"),
            "codex_memories": str(home / ".codex" / "memories"),
            "ames_claude": ames_claude,
        },
        "settings": {
            "claude_settings_safe": safe_json_keys(
                home / ".claude" / "settings.json", skip_keys={"env"}
            ),
            "codex_config_safe": safe_toml_keys(home / ".codex" / "config.toml"),
        },
        "git": {
            "current": git_status(root),
            "ames_claude": git_status(ames_claude) if ames_claude else None,
        },
        "warnings": warnings(command_paths, root, ames_claude),
    }


def warnings(command_paths: dict[str, str | None], root: str | None, ames_claude: str | None) -> list[str]:
    notes: list[str] = []
    if not root:
        notes.append("Current directory is not inside a git repo.")
    if not ames_claude:
        notes.append("Could not locate ames-claude source repo.")
    for cmd in ["backup-telegram", "validate-skill"]:
        if not command_paths.get(cmd):
            notes.append(f"Optional command not found: {cmd}.")
    if not command_paths.get("git"):
        notes.append("Required command not found: git.")
    if not command_paths.get("python3"):
        notes.append("Required command not found: python3.")
    return notes


def print_markdown(data: dict[str, Any]) -> None:
    host = data["host_inference"]
    print("# wrap-up preflight")
    print()
    print(f"- cwd: `{data['cwd']}`")
    print(f"- host: `{host['host']}` ({host['confidence']})")
    current = data["git"]["current"]
    if current:
        print(f"- current repo: `{current['root']}`")
        print(f"- current branch: `{current['branch']}`")
        print(f"- current dirty files: {current['dirty_count']}")
    ames = data["git"]["ames_claude"]
    if ames:
        print(f"- ames-claude dirty files: {ames['dirty_count']}")
    missing = [cmd for cmd, path in data["commands"].items() if not path]
    print(f"- missing optional/required commands: {', '.join(missing) if missing else 'none'}")
    if data["warnings"]:
        print()
        print("## warnings")
        for note in data["warnings"]:
            print(f"- {note}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", choices=["auto", "claude", "codex"], default="auto")
    parser.add_argument("--json", action="store_true", help="print JSON instead of markdown")
    args = parser.parse_args(argv)
    data = collect(args.host)
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print_markdown(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
