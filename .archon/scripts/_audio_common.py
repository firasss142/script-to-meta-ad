# /// script
# requires-python = ">=3.11"
# ///
"""
Shared helpers for the audio-generation scripts
(generate_voiceover.py, generate_music.py, generate_sfx.py).

Intentionally stdlib-only so the helper doesn't force uv to solve an env
just to source it. Each script declares its own PEP 723 deps.
"""
from __future__ import annotations

import os
from pathlib import Path


def load_project_env(root: Path) -> None:
    """Load .archon/.env into process env if present.

    Archon loads `~/.archon/.env` automatically and (as of recent versions)
    project-level `.archon/.env`, but we keep this as a safety net so the
    scripts are runnable outside Archon too (e.g. for local debugging).
    Never overrides an already-set env var.
    """
    env_file = root / ".archon" / ".env"
    if not env_file.exists():
        return
    for raw in env_file.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def read_brand_yaml(root: Path) -> dict:
    """Return the brand config as a dict, or an empty dict if absent/invalid.

    We avoid a hard YAML dep — the file is tiny and only needs a handful of
    string keys. If a user writes a malformed file we silently fall back to
    defaults rather than failing the whole workflow on an optional feature.
    """
    path = root / ".archon" / "brand.yaml"
    if not path.exists():
        return {}
    try:
        import yaml  # Optional — PyYAML ships with most Pythons, but not all
    except ImportError:
        return {}
    try:
        data = yaml.safe_load(path.read_text()) or {}
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def slug_from_composition_id(composition_id: str) -> str:
    """Defensive — return the composition_id unchanged. We treat the planner's
    chosen composition_id as authoritative; callers pass it through."""
    return composition_id


def read_scene_timing(artifacts_dir: Path) -> dict:
    """Return the scene-timing source of truth for the current run.

    Priority:
      1. `durations.json` — emitted by `script-to-meta-ad`'s `plan-video` for
         the no-TTS workflow. This is the authoritative source when present.
      2. `narration.json` — emitted by `remotion-idea-to-video`'s `plan-video`
         for the TTS workflow. Same shape modulo a per-scene `text` field
         that we don't need here.

    Returned shape (normalized — callers can rely on these keys):
        {
          "composition_id": str,
          "fps": int,
          "scenes": [{"id": str, "duration_s": float | None}, ...],
          "total_duration_s": float | None,
        }

    Raises FileNotFoundError if neither artifact is on disk.
    """
    import json

    durations_path = artifacts_dir / "durations.json"
    if durations_path.exists():
        data = json.loads(durations_path.read_text())
        scenes = [
            {"id": s["id"], "duration_s": s.get("duration_s")}
            for s in (data.get("scenes") or [])
        ]
        return {
            "composition_id": data.get("composition_id") or "",
            "fps": int(data.get("fps") or 30),
            "scenes": scenes,
            "total_duration_s": data.get("total_duration_s"),
        }

    narration_path = artifacts_dir / "narration.json"
    if narration_path.exists():
        data = json.loads(narration_path.read_text())
        # narration.json doesn't carry per-scene durations — voice timing is
        # derived later by generate_voiceover.py via mp3 probing.
        scenes = [{"id": s["id"], "duration_s": None} for s in (data.get("scenes") or [])]
        return {
            "composition_id": data.get("composition_id") or "",
            "fps": int(data.get("fps") or 30),
            "scenes": scenes,
            "total_duration_s": None,
        }

    raise FileNotFoundError(
        f"No timing source found in {artifacts_dir} — expected durations.json "
        f"(no-TTS workflows) or narration.json (TTS workflows)."
    )
