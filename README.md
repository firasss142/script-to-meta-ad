# script-to-meta-ad

Archon workflow that turns a finished ad script (Tunisian Darija + French
loanwords, or any RTL/LTR script) into a vertical Meta/Facebook ad creative —
muted-autoplay-native, kinetic captions, persuasion UI, with optional sound
effects and music. Renders an mp4 with chapter markers per scene so you can
record your own voice in post.

## What it does

Takes a script .md file via `$ARGUMENTS` and produces a vertical Remotion
composition + rendered mp4:

- `script <path-to-md>` — defaults to 9:16 (1080×1920) for Reels/Stories
- `script <path-to-md> 9:16` — explicit Reels/Stories
- `script <path-to-md> 4:5` — in-feed 1080×1350
- `script <path-to-md> 1:1` — square 1080×1080

Each run drops a self-contained composition under `src/<CompId>/`, optional
audio under `public/{music,sfx}/`, and an mp4 archive at
`videos/<date>-<slug>/<slug>.mp4` with embedded chapter markers.

## Why this exists

For direct-response Meta ads (Facebook feed, Reels, Stories), the dominant
viewing mode is sound-off autoplay. The conversion-driving layer is therefore
**kinetic captions + persuasion UI**, not narration. This workflow is built
around four constraints that don't fit a generic Remotion pipeline:

1. **Words are sacred** — script narration text is verbatim, never rewritten
   by the planner. The workflow's job is visual interpretation, not copy.
2. **No TTS** — voice is recorded by you in post over the silent render.
   Caption durations are calibrated to accommodate **both** muted-autoplay
   reading pace AND post-production voice delivery (reading time and
   speaking time, whichever is longer + a tail buffer).
3. **Vertical, RTL-first** — Arabic + French loanwords inline, RTL layout,
   safe areas reserved for Meta UI overlays (top 12%, bottom 18%).
4. **Moderate AI-video delegation** — Remotion is great at kinetic typography
   and persuasion UI; structurally weak at cinematic b-roll. The planner
   classifies each scene as `remotion | ai-clip | hybrid`, emits tool-agnostic
   prompts (start frame + end frame + motion prompt) for delegated scenes,
   and the workflow halts cleanly at a gate where you generate clips manually
   with Veo / Kling / Sora / Runway and drop them in `public/clips/<CompId>/`.
   Hard floors: ≥ 50% of scenes Remotion-native; CTA + comparison panels
   MUST be Remotion (legibility-critical, can't trust generative AI for
   structured UI/text).

## Quick start

**Easiest path: have a coding agent do the setup.** This README is written so
any agent can read it end-to-end and bring the repo to a runnable state.

1. Open Claude Code (or your preferred coding agent — Codex, Pi work too)
   inside this repo.
2. Tell it: *"Read `README.md` and set up this repo so I can run the
   `script-to-meta-ad` workflow."*
3. When it asks about your SFX/Music provider, answer (ElevenLabs is the
   only currently-supported provider for both — both layers are opt-in).
4. When the agent reports verified, run the workflow (see [Run](#run)).

### Which coding agent?

We've tested with [Claude Code](https://claude.ai/code). Archon also supports
**Codex** and **Pi** via `DEFAULT_AI_ASSISTANT=claude|codex|pi` in
`.archon/.env`. Setup steps below assume Claude Code; swap the install
command for the equivalent assistant CLI if you're using something else.

> **Note for the coding agent reading this**: walk through
> [Prerequisites checklist](#prerequisites-checklist) →
> [Verify what's already installed](#verify-whats-already-installed) →
> [Install (per requirement)](#install-per-requirement) → [Run](#run) in
> order. Don't invent commands not in this file.

---

## Prerequisites checklist

Six things must be present.

| # | Requirement | Why |
|---|---|---|
| 1 | **Archon CLI** (`archon` on PATH) | Runs the workflow DAG |
| 2 | **Claude Code CLI** (`claude` on PATH) | Drives `command`/`prompt` nodes (planner, builder, QA) |
| 3 | **Remotion skill** at `.claude/skills/remotion-best-practices/SKILL.md` | First node (`check-skill`) hard-fails without it |
| 4 | **System tooling**: Node 20+, pnpm, Python 3.11+, uv, jq, ffmpeg | Used by scripts, scaffolding, audio gen, rendering, chapter-marker mux |
| 5 | **`.archon/.env`** (you create it) | Holds assistant auth + API keys; not committed; copy from `.env.example` |
| 6 | **No mandatory TTS key** | This workflow doesn't synthesize voice — you record it in post. SFX/Music keys are optional. |

### Verify what's already installed

```bash
archon --version
claude --version
ls .claude/skills/remotion-best-practices/SKILL.md \
   .agents/skills/remotion-best-practices/SKILL.md \
   "$HOME/.claude/skills/remotion-best-practices/SKILL.md" 2>/dev/null
node --version           # >= v20
pnpm --version
python --version         # >= 3.11
uv --version
jq --version
ffmpeg -version
test -f .archon/.env && echo "ok" || echo "missing"
```

PowerShell (Windows): replace `ls ... 2>/dev/null` with `Get-ChildItem ...`,
`test -f` with `Test-Path`.

---

## Install (per requirement)

### 1. Archon CLI

```bash
# macOS / Linux
curl -fsSL https://archon.diy/install | bash

# Windows (PowerShell)
irm https://archon.diy/install.ps1 | iex
```

Docs: https://archon.diy/docs.

### 2. Claude Code CLI

```bash
# macOS / Linux
curl -fsSL https://claude.ai/install.sh | bash

# Windows (PowerShell)
irm https://claude.ai/install.ps1 | iex
```

Then **`claude /login`** once. The workflow uses `CLAUDE_USE_GLOBAL_AUTH=true`
which reuses this session — you don't need `ANTHROPIC_API_KEY`.

### 3. Remotion skill (already bundled)

The repo bundles the `remotion-best-practices`, `visual-diagrams`, and
`archon` skills under `.agents/skills/` and `.claude/skills/`. The
`check-skill` node will find them. If you ever need to refresh them:

```bash
npx skills add remotion-dev/skills --yes
```

### 4. System tooling

| Tool | Install |
|---|---|
| **Node 20+** | nvm: `nvm install 20 && nvm use 20` |
| **pnpm** | `npm install -g pnpm` |
| **Python 3.11+** | macOS: `brew install python@3.11`. Linux: distro pkg. Windows: https://www.python.org/downloads/ |
| **uv** | macOS/Linux: `curl -LsSf https://astral.sh/uv/install.sh \| sh`. Windows: `irm https://astral.sh/uv/install.ps1 \| iex` |
| **jq** | macOS: `brew install jq`. Linux: `apt install jq`. Windows: `winget install jqlang.jq` |
| **ffmpeg** | macOS: `brew install ffmpeg`. Linux: `apt install ffmpeg`. Windows: `winget install Gyan.FFmpeg` |

### 5. Create `.archon/.env`

```bash
# macOS / Linux
cp .env.example .archon/.env

# Windows (PowerShell)
Copy-Item .env.example .archon/.env
```

Defaults work for most users:

```env
CLAUDE_USE_GLOBAL_AUTH=true     # use `claude /login` session (recommended)
DEFAULT_AI_ASSISTANT=claude     # claude | codex | pi
```

### 6. Optional audio: configure SFX and/or Music (ElevenLabs)

Both layers are **opt-in** — no audio happens without explicit env signals.

- **SFX** (intro whoosh, transition ticks, outro stinger):

  ```env
  ELEVENLABS_API_KEY=sk_...
  SFX_PROVIDER=elevenlabs
  ```

- **Music** (background bed, paid ElevenLabs tier required):

  ```env
  ELEVENLABS_API_KEY=sk_...
  MUSIC_PROVIDER=elevenlabs
  ```

Both unset ⇒ silent mp4 (you add audio in your editor along with your voice).

---

## Run

Drop your script .md somewhere reachable from the repo root, then:

```bash
# Default 9:16 vertical (Reels/Stories/feed)
archon workflow run script-to-meta-ad --no-worktree \
  "script ./scripts/my-ad-copy.md"

# 4:5 in-feed
archon workflow run script-to-meta-ad --no-worktree \
  "script ./scripts/my-ad-copy.md 4:5"

# 1:1 square
archon workflow run script-to-meta-ad --no-worktree \
  "script ./scripts/my-ad-copy.md 1:1"
```

First run scaffolds the Remotion project (`package.json`, `src/`,
`remotion.config.ts`, etc.) into the repo root automatically. Subsequent
runs detect the existing project and skip scaffolding — **don't scaffold
manually.**

### The clip-readiness gate (expect this to fire on most runs)

If the planner classifies any scene as `kind: ai-clip` or `kind: hybrid`,
the workflow halts at the `clip-readiness-check` node and writes
`videos/<date>-<slug>/CLIPS-NEEDED.md` listing each delegated scene with:

- A target file path (`public/clips/<CompId>/sceneN.mp4`)
- A target duration (in seconds)
- A target aspect ratio
- **Three tool-agnostic prompts**: start frame, end frame, motion

Generate the clips with whatever tool fits per shot:
- **Veo 3** — text-to-video, single-paragraph prompts; great for cinematic moments
- **Kling AI** — image-to-video; takes start frame + end frame + motion prompt
- **Sora**, **Runway Gen-3**, **Pika** — pick per scene

Save each result to the exact path shown, then **resume with the same
`workflow_run_id`** (printed in the failed-run output):

```bash
archon workflow run script-to-meta-ad --no-worktree \
  "script ./scripts/my-ad-copy.md" \
  --run-id <run-id-from-the-failed-run>
```

Archon caches `plan-video` and audio nodes per `(workflow_run_id, node_id)`,
so resuming with the same run-id continues from the gate without
re-prompting Claude (which would risk producing different prompts than the
ones already in `CLIPS-NEEDED.md`).

### Recording your voice over the silent render

Once the workflow completes:

1. The mp4 at `videos/<date>-<slug>/<slug>.mp4` is silent (or has only
   SFX/music if those layers were enabled).
2. **Chapter markers per scene are embedded** — open the mp4 in CapCut /
   Premiere / DaVinci / Final Cut, and chapters appear in the timeline.
3. Record your voice over the silent track using your editor's voiceover
   tool. Captions are calibrated to accommodate natural delivery pace —
   you shouldn't feel rushed.
4. Mix and export.

---

## Optional env (in `.archon/.env`)

| Variable | Purpose |
|---|---|
| `SFX_PROVIDER=elevenlabs` | Opt in to sound effects |
| `MUSIC_PROVIDER=elevenlabs` | Opt in to background music (paid tier) |
| `MUSIC_VOLUME=0.2` | Music volume (0–1; 0.5+ jarring on muted autoplay) |
| `MUSIC_MIN_SECONDS=30` / `MUSIC_MAX_SECONDS=120` | Clamp music length |
| `RENDER_ENABLED=false` | Skip mp4 render + archive |
| `CLAUDE_BIN_PATH=/path/to/claude` | If Archon can't find the `claude` binary |
| `ALLOW_FALLBACK_HOOK=1` | Substitute a Remotion-rendered hook scene when the AI clip is missing (default off — forces explicit clip generation) |

---

## Output

- **mp4 archive**: `./videos/<YYYY-MM-DD>-<slug>/<slug>.mp4` (gitignored)
  with chapter markers per scene
- **Composition source**: `./src/<CompositionId>/` (committable — accumulates)
- **Audio assets**: `./public/{music,sfx}/...` (gitignored)
- **AI clips**: `./public/clips/<CompId>/sceneN.mp4` (gitignored)
- **Preview every video together**: `npx remotion studio`

---

## Optional: brand overlay

```bash
cp .archon/brand.example.yaml .archon/brand.yaml
```

Edit `arabic_font` (Cairo / Tajawal / IBM Plex Sans Arabic / Almarai),
`accent_red` and `accent_green` for ❌ / ✅ comparison rows, palette,
default aspect ratio, watermark logo. Missing file ⇒ neutral defaults.

---

## Troubleshooting

### `FATAL: the remotion-best-practices skill is not installed`
Run `npx skills add remotion-dev/skills --yes` from the repo root.

### `command not found: claude` (during a `command` node)
Set `CLAUDE_BIN_PATH=/full/path/to/claude` in `.archon/.env`.

### Workflow halts saying "delegated clip(s) missing"
This is **not an error** — it's the gate. Generate the clips per
`videos/<date>-<slug>/CLIPS-NEEDED.md`, drop into `public/clips/<CompId>/`,
re-run with the same `--run-id`.

### Workflow says "Skipped (prior_success)" on a fresh run
You're resuming a prior run, not starting fresh. Use a new workflow run-id
(omit `--run-id`), or clear the matching row from `archon.db`.

### `archon validate` errors
Run `archon validate workflows` and `archon validate commands` after any
edits to `.archon/workflows/*.yaml` or `.archon/commands/*.md`.

### Captions feel too short / too long for natural voice delivery
The planner's per-caption duration formula assumes ~0.45s per Arabic word
+ 0.25s per loanword + 0.4s breath + 0.5s tail. If your delivery pace is
materially different (e.g. you speak much faster), you can edit
`captions.json` between the planner run and the build run by checking out
the artifact under `archon-runs/<run-id>/captions.json` (Archon will pick
up edits on resume). For a permanent change, edit the formula constants
in `.archon/workflows/script-to-meta-ad.yaml` (in the `plan-video` node's
prompt).

---

## Anatomy

```
.archon/
├── workflows/script-to-meta-ad.yaml   # 15-node DAG: parse → plan → audio → gate → build → QA → render
├── commands/
│   ├── meta-ad-build-composition.md   # builder contract: vertical/RTL/persuasion-UI/clip-overlay rules
│   └── meta-ad-iterate.md             # fixer contract: scoped to CRITICAL+HIGH findings
├── scripts/
│   ├── _audio_common.py               # shared helpers (env loader, brand reader, scene-timing source)
│   ├── generate_sfx.py                # ElevenLabs SFX (opt-in)
│   └── generate_music.py              # ElevenLabs Music (opt-in)
├── brand.example.yaml                 # palette, Arabic font, accent red/green, default AR
├── config.yaml                        # repo-level archon config
└── .env                               # API keys (gitignored)

.claude/skills/
├── remotion-best-practices/           # path-pointer to .agents/skills/...
├── visual-diagrams/                   # comparison panels, etc.
└── archon/                            # workflow-authoring docs
```

The DAG: `check-skill → parse-script + ensure-remotion-project →
derive-slug → plan-video → (generate-sfx + generate-music) →
clip-readiness-check (gate) → build-composition → regenerate-registry →
qa-review →? iterate → verify → archive-render → summarize`.

### Per-run artifacts (under `$ARTIFACTS_DIR/`)

- `article.json` — language, aspect ratio, source script path
- `article-body.md` — script verbatim
- `slug.json` — composition_id, fs_slug
- `video-plan.md` — scene structure, animation choreography
- `captions.json` — per-scene reveal beats, start/end timing, is_punch flag, loanwords list
- `durations.json` — per-scene durations (timing source of truth)
- `delegation-plan.json` — per-scene `kind` + AI-clip prompts
- `audio/sfx-manifest.json` — SFX cues (if SFX enabled)
- `audio/music-manifest.json` — music bed (if music enabled)
- `qa-findings.md` — QA findings, severity-tagged

---

## Credit

This workflow is derived from
[`coleam00/archon-video-generation-workflow`](https://github.com/coleam00/archon-video-generation-workflow)
by [Cole Medin](https://github.com/coleam00) — an Archon workshop example
that takes a URL or idea and produces a landscape TTS-driven Remotion
explainer. The DAG topology, the bash node patterns, the
`ensure-remotion-project` scaffold dance, the `regenerate-registry` static
import pattern, and the QA → iterate → verify → archive flow all originate
there. Read the upstream
[WORKSHOP.md](https://github.com/coleam00/archon-video-generation-workflow/blob/main/WORKSHOP.md)
for the design rationale and the failure-mode catalogue that shaped both
workflows.

This sibling adapts the pattern for a different content shape:
**finished script → vertical → muted-autoplay → no-TTS → AI-clip-delegation**
optimized for direct-response Meta/Facebook ads.
