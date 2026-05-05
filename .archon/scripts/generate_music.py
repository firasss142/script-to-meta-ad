# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "httpx>=0.27",
#   "mutagen>=1.47",
#   "pyyaml>=6.0",
# ]
# ///
"""
Background music generator for the `remotion-idea-to-video` workflow.

Reads the video plan + (optional) brand.yaml to craft an ElevenLabs Music
prompt, synthesizes a single instrumental bed sized to cover the voiceover
(or nominal plan duration), writes it under the Remotion project's
`public/music/` dir, and emits a manifest.

Opt-in: no-op unless `MUSIC_PROVIDER=elevenlabs` (explicit) or
`MUSIC_PROVIDER` is unset AND `ENABLE_MUSIC=true` AND an ElevenLabs key is
present. Default behaviour with no env set is "skip" — we don't spend money
without an explicit signal.

Usage:
    uv run .archon/scripts/generate_music.py <artifacts-dir>

Environment:
    MUSIC_PROVIDER           'elevenlabs' | 'none'   (default: 'none')
    ELEVENLABS_API_KEY       required when provider resolves to elevenlabs
    ELEVENLABS_MUSIC_MODEL   optional override (ElevenLabs Music doesn't
                             currently expose a model_id param; this is kept
                             for forward-compat)
    MUSIC_DURATION_PAD_SEC   seconds of padding beyond the timing source's
                             total duration (default: 2.0). Ignored when no
                             timing source is available.
    MUSIC_MIN_SECONDS        floor on music length (default: 30.0 — ElevenLabs
                             charges per second; short clips sound abrupt).
    MUSIC_MAX_SECONDS        cap on music length (default: 120.0).

Output:
    $ARTIFACTS_DIR/project/public/music/<composition_id>.mp3
    $ARTIFACTS_DIR/audio/music-manifest.json
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import httpx
from mutagen.mp3 import MP3

# Force UTF-8 stdout/stderr so non-ASCII chars (e.g. "—", "→") don't crash on Windows cp1252.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))
from _audio_common import load_project_env, read_brand_yaml, read_scene_timing  # noqa: E402


DEFAULT_MOOD = "understated, upbeat tech-explainer bed, no drums, no vocals, cinematic, subtle"
DEFAULT_MIN_SECONDS = 30.0
DEFAULT_MAX_SECONDS = 120.0
DEFAULT_PAD_SECONDS = 2.0


def resolve_provider() -> str:
    """Music is OPT-IN only — default is 'none' even if keys are present."""
    explicit = (os.environ.get("MUSIC_PROVIDER") or "").strip().lower()
    if explicit in {"elevenlabs", "none"}:
        if explicit == "elevenlabs" and not os.environ.get("ELEVENLABS_API_KEY"):
            sys.exit("FATAL: MUSIC_PROVIDER=elevenlabs but ELEVENLABS_API_KEY is not set")
        return explicit
    if explicit:
        sys.exit(f"FATAL: unknown MUSIC_PROVIDER={explicit!r} (expected elevenlabs|none)")
    return "none"


def compute_duration_ms(artifacts_dir: Path) -> int:
    """Decide music length.

    Priority:
      1. durations.json total + pad   (no-TTS workflow)
      2. voice-manifest total + pad   (TTS workflow)
      3. fallback constant            (silent / unknown)
    Clamp to [MUSIC_MIN_SECONDS, MUSIC_MAX_SECONDS].
    """
    min_s = float(os.environ.get("MUSIC_MIN_SECONDS", DEFAULT_MIN_SECONDS))
    max_s = float(os.environ.get("MUSIC_MAX_SECONDS", DEFAULT_MAX_SECONDS))
    pad_s = float(os.environ.get("MUSIC_DURATION_PAD_SEC", DEFAULT_PAD_SECONDS))

    durations_path = artifacts_dir / "durations.json"
    if durations_path.exists():
        try:
            total_s = float(json.loads(durations_path.read_text())["total_duration_s"])
            target = max(min_s, min(max_s, total_s + pad_s))
            return int(target * 1000)
        except Exception:
            pass

    voice_manifest = artifacts_dir / "audio" / "voice-manifest.json"
    if voice_manifest.exists():
        try:
            total_s = float(json.loads(voice_manifest.read_text())["total_duration_s"])
            target = max(min_s, min(max_s, total_s + pad_s))
            return int(target * 1000)
        except Exception:
            pass

    # Fallback: 45s — middle of our 30–60s silent target.
    target = max(min_s, min(max_s, 45.0))
    return int(target * 1000)


def build_prompt(artifacts_dir: Path, repo_root: Path) -> str:
    """Compose the music prompt from the plan's mood + brand music_mood."""
    brand = read_brand_yaml(repo_root)
    brand_mood = (brand.get("music_mood") or "").strip() if isinstance(brand, dict) else ""

    # Read article title for topical flavor; silently tolerate missing file.
    article_title = ""
    article_path = artifacts_dir / "article.json"
    if article_path.exists():
        try:
            article_title = json.loads(article_path.read_text()).get("title", "") or ""
        except Exception:
            pass

    mood = brand_mood or DEFAULT_MOOD
    if article_title:
        return f"{mood}. Topic: {article_title}"
    return mood


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("usage: generate_music.py <artifacts-dir>")

    artifacts_dir = Path(sys.argv[1]).resolve()
    if not artifacts_dir.is_dir():
        sys.exit(f"FATAL: artifacts dir not found: {artifacts_dir}")

    load_project_env(Path.cwd())

    provider = resolve_provider()
    if provider == "none":
        print("Music: not enabled — skipping (set MUSIC_PROVIDER=elevenlabs to turn on).")
        return

    try:
        timing = read_scene_timing(artifacts_dir)
    except FileNotFoundError as e:
        sys.exit(f"FATAL: {e}")

    composition_id = timing["composition_id"] or "HnStory"

    music_ms = compute_duration_ms(artifacts_dir)
    prompt = build_prompt(artifacts_dir, Path.cwd())

    print(f"Music: provider={provider}, duration={music_ms}ms")
    print(f"Music prompt: {prompt}")

    api_key = os.environ["ELEVENLABS_API_KEY"]
    body = {
        "prompt": prompt,
        "music_length_ms": music_ms,
    }

    with httpx.Client(timeout=300.0) as client:
        resp = client.post(
            "https://api.elevenlabs.io/v1/music",
            headers={
                "xi-api-key": api_key,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg",
            },
            json=body,
        )
    if resp.status_code != 200:
        sys.exit(
            f"FATAL: ElevenLabs Music returned {resp.status_code}: "
            f"{resp.text[:500]}"
        )

    project_root = Path.cwd()
    out_dir = project_root / "public" / "music"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{composition_id}.mp3"
    out_path.write_bytes(resp.content)

    duration_s = float(MP3(out_path).info.length)
    fps = timing["fps"]
    duration_frames = round(duration_s * fps)

    manifest = {
        "provider": "elevenlabs",
        "composition_id": composition_id,
        "fps": fps,
        "path": f"music/{composition_id}.mp3",
        "duration_s": round(duration_s, 4),
        "duration_frames": duration_frames,
        "prompt": prompt,
        "volume": float(os.environ.get("MUSIC_VOLUME", 0.2)),
    }

    manifest_path = artifacts_dir / "audio" / "music-manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

    print(
        f"Music: {out_path.name} — {duration_s:.2f}s ({duration_frames}f), "
        f"volume={manifest['volume']}"
    )
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
