---
description: Apply QA findings to the Meta/Facebook ad composition built by `meta-ad-build-composition`. Fixes CRITICAL + HIGH issues (vertical safe areas, RTL correctness, caption legibility timing, scrim contrast, delegation balance, hook grip, animation quality), re-runs tsc. Defers MED/LOW.
argument-hint: (no direct arguments — consumes $ARTIFACTS_DIR/qa-findings.md)
---

# Meta/Facebook Ad — Iterate on QA Findings

**Workflow ID**: $WORKFLOW_ID
**Artifacts dir**: $ARTIFACTS_DIR

You are the only node in the `script-to-meta-ad` workflow allowed to edit scene code after the build step. Two skills loaded: `remotion-best-practices` and `visual-diagrams`.

The **repo root is the project root**. All edits happen inside `src/<composition_id>/`. You may also edit files under `src/shared/components/` if a finding specifies a primitive bug — but only if the fix is genuinely needed there. Don't refactor shared code as part of an iteration that could be done in the composition's own folder.

You must NOT touch:
- `src/Root.tsx`
- `src/compositions.gen.ts`
- Other compositions' folders (any `src/<OtherCompId>/`)

---

## Phase 1: LOAD

1. `$ARTIFACTS_DIR/qa-findings.md` — findings, severity-tagged
2. `$ARTIFACTS_DIR/slug.json` — composition_id + fs_slug (authoritative)
3. `$ARTIFACTS_DIR/article.json` — language, aspect ratio, width, height
4. `$ARTIFACTS_DIR/video-plan.md` — structural source of truth
5. `$ARTIFACTS_DIR/captions.json` — on-screen text + per-beat timing
6. `$ARTIFACTS_DIR/durations.json` — per-scene total durations
7. `$ARTIFACTS_DIR/delegation-plan.json` — per-scene `kind` (remotion / ai-clip / hybrid)
8. Audio manifests (if present):
   - `$ARTIFACTS_DIR/audio/sfx-manifest.json`
   - `$ARTIFACTS_DIR/audio/music-manifest.json`
   - (No voice manifest in this workflow.)
9. `.archon/brand.yaml` (if present)
10. Everything under `src/<composition_id>/` in the repo root.
11. Relevant primitives under `src/shared/components/` if a finding flags one (KineticCaption, ComparisonRow, BenefitCardStack, CTAButton, GuaranteeBadge, PhoneFrame, HookPunch, SafeAreaContainer, ClipOverlayBackground, arabic.ts).

Pull skill rule files based on finding categories:
- Caption / typewriter / per-character-opacity findings → `rules/text-animations.md`
- Transition / `<TransitionSeries>` findings → `rules/transitions.md`
- Premount / sequencing findings → `rules/sequencing.md`
- Easing / composed-progress / `[1.0, 1.0]` findings → `rules/timing.md`
- Font / Arabic glyph findings → `rules/fonts.md`
- Clip overlay / `<OffthreadVideo>` findings → `rules/videos.md`
- Diagram / comparison findings → `visual-diagrams` `references/component-patterns.md`

### PHASE_1_CHECKPOINT
- [ ] Findings sorted by severity
- [ ] Plan + slug + captions + durations + delegation-plan + audio manifests read
- [ ] Current code state understood (composition + relevant primitives)

---

## Phase 2: PLAN FIXES

Write `$ARTIFACTS_DIR/iterate-plan.md`:

    # Iterate Plan

    ## Fixing
    - [CRITICAL] <issue> — <file> — <one-line fix intent>
    - [HIGH]     <issue> — <file> — <one-line fix intent>

    ## Deferring
    - [MED]  <issue> — <why skipped for this pass>
    - [LOW]  <issue> — <why skipped for this pass>

**Scope rule**: fix every CRITICAL and every HIGH. Defer MED and LOW unless trivial while you're already editing the same file. Do not add new features. Do not rewrite the script (script text is sacred — captions are verbatim from the user).

Common HIGH/CRITICAL issue shapes in this workflow:

- **Vertical safe-area violation** — persuasion content (CTA, comparison, hook headline) sits above 12% or below 82% of the canvas height. Fix: wrap the offending scene content in `<SafeAreaContainer>`, or reduce its absolute-positioned offset.
- **Missing `direction: rtl` / `unicodeBidi` on Arabic text node** — Fix: replace the inline `style={...}` with `style={arabicTextStyle({...})}` from `src/shared/components/arabic.ts`. If the helper isn't imported, add the import.
- **Loanwords not visually distinguished** — A beat's `loanwords[]` is non-empty but the rendered caption doesn't wrap the loanword in a font-weight-500 span. Fix: split the beat's text on each loanword and wrap the loanwords. Use the `LOANWORD_WEIGHT` constant from `arabic.ts`.
- **Caption stays on screen below the legibility floor** — A beat's `(end_s - start_s)` is shorter than the reading-speaking floor. **Critical: do NOT modify durations.json or captions.json — those are planner output and represent the contract with the user. Instead, flag this as "planner regression" in the iterate report and skip the fix; the user needs to re-run the planner.**
- **Hook scene 1 has no visual hook within first 30 frames** — Fix: wrap scene 1's content in `<HookPunch>` (or apply pattern-interrupt motion if HookPunch isn't appropriate, e.g. for `kind: ai-clip` scenes). For `ai-clip` scene 1, this finding shouldn't fire (the AI clip carries the hook); if it does, double-check the QA logic and flag in iterate report.
- **CTA scene delegated to ai-clip / hybrid** — `delegation-plan.json` says CTA is `ai-clip` or `hybrid`. This is a planner regression; CTA must be `kind: remotion`. Don't fix in iterate — flag for planner re-run.
- **Comparison panel delegated** — same as above, comparison must be `kind: remotion`. Flag for planner re-run.
- **Less than 50% Remotion-native scenes** — planner regression, flag for re-run.
- **Hardcoded raw frame numbers** — replace with `<seconds> * fps` form. Pull `fps` from `useVideoConfig()`.
- **`Easing.linear` on a non-loop animation** — replace with `Easing.bezier(0.16, 1, 0.3, 1)` (entrance) or `Easing.in(Easing.cubic)` (exit) or appropriate curve from the easing palette.
- **Per-character opacity in a typewriter / reveal** — replace with string slicing (`text.slice(0, typedChars)` where `typedChars = Math.floor(progress * text.length)`).
- **Plan-specified transition not implemented** — implement via `<TransitionSeries.Transition presentation={...} timing={linearTiming({...})} />` between the relevant sequences.
- **Music ducking finding** — n/a in this workflow (no voice). If it appears, that's a QA bug — flag and ignore.
- **Scrim missing on a hybrid scene** — Fix: wrap the scene in `<ClipOverlayBackground>` (which provides the scrim) instead of bare `<OffthreadVideo>`.

### PHASE_2_CHECKPOINT
- [ ] `iterate-plan.md` written
- [ ] Every CRITICAL and HIGH has either a "Fixing" line OR a "planner-regression" flag

---

## Phase 3: APPLY FIXES

Edit the files in your plan, scoped strictly to `src/<composition_id>/` (and `src/shared/components/<primitive>.tsx` if a primitive has a genuine bug).

Rules:

- Do not change the `composition_id` (from `slug.json`)
- Do not rename files unless a finding requires it
- Do not change fps / width / height (those come from article.json)
- Do not touch `src/Root.tsx`, `src/compositions.gen.ts`, or any other composition's directory
- Do NOT edit `captions.json`, `durations.json`, or `delegation-plan.json` — those are planner contracts. Findings that imply changes to them = planner regression flag, not iterate fix.
- If a fix changes per-scene timing, **STOP** and flag — durations come from the planner. The composition's `calculateMetadata.ts` reads durations.json verbatim.
- If fixing audio wiring, keep manifest paths exact — they live under the repo's `public/` and are read via `staticFile()`.
- If fixing primitives in `src/shared/components/`, change ONLY the buggy primitive, never refactor surrounding code.
- Keep edits minimal — one fix per finding, not a rewrite.

---

## Phase 4: VERIFY

```bash
npx --yes tsc --noEmit
```

Retry once on failure. If still failing, stop and report.

### PHASE_4_CHECKPOINT
- [ ] `tsc --noEmit` exits 0
- [ ] All CRITICAL + HIGH findings addressed OR documented as planner-regression flags

---

## Phase 5: REPORT

Write `$ARTIFACTS_DIR/iterate-report.md`:

    # Iterate Report

    ## Fixed
    - [CRITICAL] <finding> — <file:line> — <what changed>
    - [HIGH]     <finding> — <file:line> — <what changed>

    ## Deferred
    - [MED] <finding> — <reason>

    ## Planner-regression flags (NOT fixed by iterate — needs planner re-run)
    - <finding> — <reason>

    ## Outcome
    - tsc --noEmit: PASS | FAIL (with error digest)

Final message to the workflow: plain-text summary under 100 words listing count CRITICAL+HIGH fixed, count deferred, count planner-regression flags, tsc result, files touched.
