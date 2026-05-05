# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "httpx>=0.27",
#   "mutagen>=1.47",
#   "pyyaml>=6.0",
# ]
# ///
"""
Sound-effects generator for the `remotion-idea-to-video` workflow.

Generates a small, fixed set of editorial SFX via ElevenLabs Sound Generation:
  - intro_whoosh    (fires at composition start, scene1)
  - outro_stinger   (fires at composition end, last scene)
  - transition_tick (one between each adjacent scene, N-1 total)

This gives a predictable, conservative SFX layer that matches short editorial
pacing without the LLM having to hand-pick anchors. If a brand.yaml declares
a `sfx_style`, that hint is appended to each prompt.

Opt-in: no-op unless `SFX_PROVIDER=elevenlabs` is set. Default: skip.

Usage:
    uv run .archon/scripts/generate_sfx.py <artifacts-dir>

Environment:
    SFX_PROVIDER             'elevenlabs' | 'none'  (default 'none')
    ELEVENLABS_API_KEY       required when provider resolves to elevenlabs

Output:
    $ARTIFACTS_DIR/project/public/sfx/<composition_id>/*.mp3
    $ARTIFACTS_DIR/audio/sfx-manifest.json
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import httpx
from mutagen.mp3 import MP3

# Force UTF-8 stdout/stderr so non-ASCII chars (e.g. "→") don't crash on Windows cp1252.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))
from _audio_common import load_project_env, read_brand_yaml, read_scene_timing  # noqa: E402


INTRO_PROMPT = "Futuristic digital power-up, AI system initializing, rising electronic swoosh, punchy and energetic"
OUTRO_PROMPT = "Satisfying digital completion chime, workflow success, clean futuristic resolution, uplifting"
TRANSITION_PROMPT = "Quick digital swoosh, fast data transfer sound, sharp and modern, energetic scene cut"


def resolve_provider() -> str:
    explicit = (os.environ.get("SFX_PROVIDER") or "").strip().lower()
    if explicit in {"elevenlabs", "none"}:
        if explicit == "elevenlabs" and not os.environ.get("ELEVENLABS_API_KEY"):
            sys.exit("FATAL: SFX_PROVIDER=elevenlabs but ELEVENLABS_API_KEY is not set")
        return explicit
    if explicit:
        sys.exit(f"FATAL: unknown SFX_PROVIDER={explicit!r} (expected elevenlabs|none)")
    return "none"


def synthesize_sfx(
    client: httpx.Client, api_key: str, text: str, out_path: Path, duration_s: float
) -> None:
    body = {"text": text, "duration_seconds": duration_s, "prompt_influence": 0.6}
    resp = client.post(
        "https://api.elevenlabs.io/v1/sound-generation",
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        json=body,
    )
    if resp.status_code != 200:
        sys.exit(
            f"FATAL: ElevenLabs SFX returned {resp.status_code} "
            f"for prompt {text!r}: {resp.text[:300]}"
        )
    out_path.write_bytes(resp.content)


def with_style(prompt: str, style: str) -> str:
    return f"{prompt}. Style: {style}" if style else prompt


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("usage: generate_sfx.py <artifacts-dir>")

    artifacts_dir = Path(sys.argv[1]).resolve()
    if not artifacts_dir.is_dir():
        sys.exit(f"FATAL: artifacts dir not found: {artifacts_dir}")

    load_project_env(Path.cwd())

    provider = resolve_provider()
    if provider == "none":
        print("SFX: not enabled — skipping (set SFX_PROVIDER=elevenlabs to turn on).")
        return

    try:
        timing = read_scene_timing(artifacts_dir)
    except FileNotFoundError as e:
        sys.exit(f"FATAL: {e}")

    composition_id = timing["composition_id"] or "HnStory"
    fps = timing["fps"]
    scenes = timing["scenes"]
    if not scenes:
        sys.exit("FATAL: timing source has no scenes[]")

    brand = read_brand_yaml(Path.cwd())
    style = (brand.get("sfx_style") or "").strip() if isinstance(brand, dict) else ""

    project_root = Path.cwd()
    out_dir = project_root / "public" / "sfx" / composition_id
    out_dir.mkdir(parents=True, exist_ok=True)

    api_key = os.environ["ELEVENLABS_API_KEY"]

    anchors = [
        {
            "id": "intro_whoosh",
            "fires_at": "composition_start",
            "duration_s": 1.2,
            "prompt": with_style(INTRO_PROMPT, style),
            "path_rel": f"sfx/{composition_id}/intro_whoosh.mp3",
        },
        {
            "id": "outro_stinger",
            "fires_at": "composition_end",
            "duration_s": 1.5,
            "prompt": with_style(OUTRO_PROMPT, style),
            "path_rel": f"sfx/{composition_id}/outro_stinger.mp3",
        },
    ]
    # One transition tick between each adjacent scene pair (N-1 entries).
    for i in range(len(scenes) - 1):
        from_scene = scenes[i]["id"]
        to_scene = scenes[i + 1]["id"]
        anchors.append(
            {
                "id": f"transition_{i + 1}",
                "fires_at": "scene_boundary",
                "from_scene": from_scene,
                "to_scene": to_scene,
                "duration_s": 0.7,
                "prompt": with_style(TRANSITION_PROMPT, style),
                "path_rel": f"sfx/{composition_id}/transition_{i + 1}.mp3",
            }
        )

    print(f"SFX: provider={provider}, composition={composition_id}, cues={len(anchors)}")

    results = []
    with httpx.Client(timeout=120.0) as client:
        for cue in anchors:
            out_path = project_root / "public" / cue["path_rel"]
            print(f"  → {cue['id']}: {cue['prompt']}")
            synthesize_sfx(client, api_key, cue["prompt"], out_path, cue["duration_s"])
            actual = float(MP3(out_path).info.length)
            results.append(
                {
                    **cue,
                    "duration_s": round(actual, 4),
                    "duration_frames": round(actual * fps),
                }
            )
            print(f"    wrote {out_path.name} — {actual:.2f}s")

    manifest = {
        "provider": "elevenlabs",
        "composition_id": composition_id,
        "fps": fps,
        "cues": results,
    }
    manifest_path = artifacts_dir / "audio" / "sfx-manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

    print(f"SFX: {len(results)} cues written")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
