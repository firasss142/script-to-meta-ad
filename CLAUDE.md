# Repo guide for coding agents

You are a coding agent helping a user set up or run this repo. **`README.md` is the single source of truth** — full setup instructions, prerequisite checks, install commands, env configuration, run commands, and troubleshooting all live there.

## What this repo is

`script-to-meta-ad` — an Archon workflow that turns a finished ad script (Tunisian Darija + French loanwords, or any RTL/LTR script) into a vertical Meta/Facebook ad creative. Muted-autoplay-native, kinetic captions, persuasion UI. **No TTS** — the user records their own voice in post over the silent render.

Some scenes delegate to AI video tools (Veo / Kling / Sora / Runway) for cinematic moments Remotion can't produce well. The workflow halts cleanly at a `clip-readiness-check` gate when delegated clips are missing, writes copy-paste-ready prompts to `videos/<date>-<slug>/CLIPS-NEEDED.md`, and resumes from the gate when re-run with the same `--run-id`.

## When the user asks you to set up the repo

Read `README.md` end-to-end first, then work through it in this order:

1. **Verify** — run the commands under *Verify what's already installed* to detect what's present.
2. **Install** — for each missing prerequisite, run the matching command from *Install (per requirement)*. Use the OS-specific variant (macOS / Linux / Windows) the user is on.
3. **Create `.archon/.env`** — the file does **not** exist by default. Copy from `.env.example`.
4. **Configure audio (BOTH OPTIONAL)** — ask the user whether they want SFX and/or background music. Both are opt-in. If yes to either, the user needs an ElevenLabs API key. Music requires their paid tier; SFX works on free.
5. **Run** — invoke the workflow per the *Run* section only after every prerequisite check passes. Confirm with the user the script path and the aspect ratio (9:16 default for Reels/Stories; 4:5 for in-feed; 1:1 for square).

## When the workflow halts at `clip-readiness-check`

This is **expected behavior**, not a failure. The planner has classified one or more scenes as needing AI-generated video clips. The workflow has written `videos/<date>-<slug>/CLIPS-NEEDED.md` listing each delegated scene with three prompts (start frame, end frame, motion).

Walk the user through:

1. Open `CLIPS-NEEDED.md` and review the missing scenes
2. For each scene, generate a clip with whatever AI video tool fits the shot (Veo for cinematic; Kling for image-to-video with start+end frames; Sora; Runway; etc. — the prompts are tool-agnostic prose)
3. Save each result to the exact `public/clips/<CompId>/<sceneN>.mp4` path shown
4. Resume the workflow with the **same `--run-id`** printed in the failed-run output:
   ```
   archon workflow run script-to-meta-ad --no-worktree "<original args>" --run-id <run-id>
   ```

**Do NOT** start a fresh run after generating clips — that would re-prompt the planner and risk producing different prompts than what's already in `CLIPS-NEEDED.md`. Use the same run-id.

## When something fails at runtime

The *Troubleshooting* section in `README.md` covers the known failure modes. Match the error to a heading there before improvising. Common ones:

- Missing `remotion-best-practices` skill → `npx skills add remotion-dev/skills --yes`
- `claude` not on PATH → set `CLAUDE_BIN_PATH=` in `.archon/.env`
- "Skipped (prior_success)" on what should be a fresh run → user is resuming an old run-id; either omit `--run-id` for a fresh run, or use the matching run-id intentionally
- Captions feel mistimed for natural voice delivery → edit `archon-runs/<run-id>/captions.json` between planner and build, OR adjust the per-caption duration formula constants in the `plan-video` node prompt for a permanent change

## Assistant choice

The user may be on Claude Code (recommended and tested), Codex, or Pi — Archon supports all three via `DEFAULT_AI_ASSISTANT` in `.archon/.env`. If the user isn't using Claude Code, swap the `claude` install command for the equivalent assistant CLI; the rest of the flow is identical.

## Don'ts

- Don't invent install commands not in `README.md`.
- Don't skip the prerequisite verification step — installing unconditionally wastes time and may overwrite the user's config.
- Don't pick an audio provider for the user. Ask. Both SFX and Music are opt-in by design — silent output is a valid happy path.
- Don't scaffold the Remotion project manually — the workflow's `ensure-remotion-project` node does it on first run.
- Don't rewrite the user's script. **Words are sacred** — captions are verbatim from the script. The planner segments and times the words; it never paraphrases them.
- Don't suggest TTS as a fallback when audio looks "missing." The silent mp4 (or SFX/music-only mp4) is the intended deliverable. Voice is added by the user in post.
- Don't bypass the `clip-readiness-check` gate by editing `delegation-plan.json` to mark all scenes `kind: remotion`. The planner classified scenes as delegation-eligible for a reason (cinematic shots Remotion can't produce). Either generate the clips, or accept fallback behavior via `ALLOW_FALLBACK_HOOK=1` (hook scenes only).
- Don't commit `public/clips/`, `public/music/`, `public/sfx/`, `videos/`, or `.archon/.env` — all are in `.gitignore`.
