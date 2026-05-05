---
description: Build a vertical Meta/Facebook ad composition for the `script-to-meta-ad` workflow. Writes a self-contained `src/<CompId>/` folder, vendors persuasion-UI primitives into `src/shared/components/` on first run, wires SFX/music/AI-clips, applies brand overlay. Captions drive everything (no TTS). Encodes vertical safe areas, Arabic RTL handling, Meta-ad persuasion patterns, and clip-overlay layering — gaps the remotion-best-practices skill doesn't cover.
argument-hint: (no direct arguments — consumes artifacts at $ARTIFACTS_DIR/ and the repo's public/ assets)
---

# Meta/Facebook Ad — Build Composition

**Workflow ID**: $WORKFLOW_ID
**Artifacts dir**: $ARTIFACTS_DIR

You are the builder node of the `script-to-meta-ad` workflow. You take a finished Tunisian Darija ad script (already segmented into scenes + reveal beats by the planner) and produce a vertical, muted-autoplay-native Remotion composition optimized for Facebook feed / Reels / Stories.

Two skills loaded:
- `remotion-best-practices` — always consult; covers compositions, fonts, animations, transitions, video overlay
- `visual-diagrams` — consult only if a scene's `visual` field calls for a `ComparisonDiagram`

**This workflow has different rules than `remotion-build-composition`. Read the rules below carefully before pulling skill files. Specifically: this workflow is vertical, Arabic RTL, no TTS (captions are the on-screen text AND the spoken script), and supports per-scene AI-generated video clips for delegated scenes.**

---

## Phase 1: LOAD

The **repo root is your project root**. Archon runs you from there.

Read these in order:

1. `$ARTIFACTS_DIR/slug.json` — authoritative `composition_id` and `fs_slug`. Use the `composition_id` string verbatim.
2. `$ARTIFACTS_DIR/article.json` — language tag, aspect ratio, width, height, source script path.
3. `$ARTIFACTS_DIR/article-body.md` — the script verbatim (for reference; do NOT extract text from it — captions.json is the source of truth).
4. `$ARTIFACTS_DIR/video-plan.md` — scene structure, rhetorical roles, animation choreography, transition specs.
5. `$ARTIFACTS_DIR/captions.json` — **the on-screen text source of truth.** Per-scene reveal beats with start_s, end_s, is_punch, loanwords. There is NO `narration.json` in this workflow. Captions are spoken by the user later in post-production over the silent render.
6. `$ARTIFACTS_DIR/durations.json` — per-scene total durations (already calibrated for max(reading time, speaking time, min legibility) + buffers). **Use these durations verbatim — do not re-derive timing from caption beats. The planner has already done that math.**
7. `$ARTIFACTS_DIR/delegation-plan.json` — per-scene `kind: remotion | ai-clip | hybrid`. For `ai-clip` and `hybrid` scenes, the corresponding video file is at `public/clips/<CompId>/<sceneId>.mp4` (the `clip-readiness-check` node has already verified existence — you can `staticFile()` it directly).
8. **Probe which audio assets exist** — read each manifest if present:
   - `$ARTIFACTS_DIR/audio/sfx-manifest.json`
   - `$ARTIFACTS_DIR/audio/music-manifest.json`
   - There is **no voice-manifest.json** in this workflow. Voice gets recorded by the user in post-production.
9. `.archon/brand.yaml` (optional) — pull `arabic_font`, `accent_red`, `accent_green`, `colors.bg`, `logo_url`. Defaults documented in this file (see Phase 2 → Brand defaults).
10. `package.json` — confirm Remotion version. If any of `@remotion/transitions`, `@remotion/google-fonts`, `@remotion/media`, `lucide-react` are missing, install via `pnpm add ...`.
11. `src/Root.tsx` and `src/compositions.gen.ts` — **DO NOT EDIT EITHER FILE.** A downstream node regenerates the registry by scanning `src/<name>/index.ts`.
12. `src/shared/components/` — if it doesn't exist, you'll create it in Phase 2 with the persuasion-UI primitives this workflow expects. If it does exist (because a prior run created it), reuse what's there; only add new primitives if missing.

Then from the skills, always read:
- `rules/compositions.md`
- `rules/timing.md`
- `rules/sequencing.md`
- `rules/text-animations.md`
- `rules/animations.md`
- `rules/fonts.md`
- `rules/transitions.md`
- `rules/videos.md` — relevant for clip-overlay scenes (`<OffthreadVideo>`)

If `delegation-plan.json` has any scene where the script's plan calls for a comparison panel and that scene is `kind: remotion`, also read:
- `visual-diagrams` SKILL.md
- `references/component-patterns.md` (specifically `ComparisonDiagram`)

### PHASE_1_CHECKPOINT
- [ ] `composition_id` + `fs_slug` captured from slug.json
- [ ] Aspect ratio + width/height read from article.json
- [ ] captions.json + durations.json + delegation-plan.json all loaded
- [ ] Audio manifests probed (sfx, music)
- [ ] Brand config loaded OR defaults selected
- [ ] Skill rules read
- [ ] `public/clips/<CompId>/` confirmed to contain mp4s for every delegated scene

---

## Phase 2: IMPLEMENT

### Composition layout

Use the dimensions from `article.json`. Default 1080×1920 @ 30fps. For 4:5: 1080×1350. For 1:1: 1080×1080.

Create a single self-contained directory: `src/<CompositionId>/` in the repo root.

```
src/<COMPOSITION_ID>/
  index.ts                 — default-exports composition meta (REQUIRED)
  <COMPOSITION_ID>.tsx     — top-level composition, <TransitionSeries>, audio, clip overlays
  calculateMetadata.ts     — derives total duration from durations.json
  constants.ts             — fps, dimensions, palette, typography, safe-area insets, clip mode flag
  scenes/Scene1.tsx        — per-scene component
  scenes/SceneN.tsx
```

Plus, on first workflow run only (or if missing), create reusable persuasion-UI primitives:

```
src/shared/components/
  KineticCaption.tsx       — Arabic-aware reveal animations (typewriter / word-cluster / punch)
  BenefitCardStack.tsx     — staggered card entrance for benefit lists
  ComparisonRow.tsx        — red ✗ / green ✓ rows for "biometric? Excel? Notebook?" panels
  CTAButton.tsx            — kinetic CTA with scale-pulse loop and brand color
  GuaranteeBadge.tsx       — ribbon-style overlay for risk-reversal lines
  PhoneFrame.tsx           — 3D-perspective phone bezel SVG wrapping screen content
  HookPunch.tsx            — opening 1-3s pattern interrupt template
  SafeAreaContainer.tsx    — wraps every scene with FB UI safe-area padding
  ClipOverlayBackground.tsx — `<OffthreadVideo>` + scrim + safe-area wrapper for hybrid scenes
  arabic.ts                — RTL helpers: `wrapMixedScript()`, `arabicTextStyle()`
```

### `src/<CompId>/index.ts` — registration contract

```tsx
import { <CompId> } from './<CompId>';
import { calculateMetadata } from './calculateMetadata';

export default {
  id: '<CompId>',
  component: <CompId>,
  width: <from article.json>,
  height: <from article.json>,
  fps: 30,
  durationInFrames: 1800,   // placeholder; calculateMetadata overrides with the real value
  calculateMetadata,
};
```

If `index.ts` is missing or mistyped, `Root.tsx` won't register the composition — that's a CRITICAL failure.

### Brand defaults (if `.archon/brand.yaml` is absent)

```ts
export const PALETTE = {
  bg: '#0B1120',
  bgGradientTop: '#1E1B4B',
  bgGradientBottom: '#0B1120',
  primary: '#7C3AED',
  secondary: '#06B6D4',
  accentRed: '#DC2626',
  accentGreen: '#10B981',
  textPrimary: '#FFFFFF',
  textMuted: '#94A3B8',
  scrim: 'rgba(0, 0, 0, 0.45)',
};
export const ARABIC_FONT_FAMILY = 'Cairo';
export const FALLBACK_FONT_STACK = `${ARABIC_FONT_FAMILY}, Tajawal, "Noto Sans Arabic", system-ui, sans-serif`;
```

If `brand.yaml` is present, override `accentRed`, `accentGreen`, `arabic_font`, etc., from it. Watermark / logo handling: same as the existing workflow's brand overlay rules.

### Vertical safe-area insets

Facebook feed / Reels / Stories overlay UI on top of every video. Reserve space:

```ts
// src/<CompId>/constants.ts
export const SAFE_AREA = {
  topInsetPct: 0.12,    // 12% — profile pic, channel name, "..." menu, sometimes a sponsored tag
  bottomInsetPct: 0.18, // 18% — caption truncation, like/comment/share/save buttons
  sideInsetPct: 0.04,   // 4% each side — for in-feed UI clipping safety
};
```

The `SafeAreaContainer` primitive (vendored — see below) enforces these. **All persuasion-critical content (hook text, comparison panels, CTA, captions) lives in the middle 70%.** Background art, scrim gradients, and AI-clip footage can extend to the full canvas (they look fine clipped by Meta UI).

### Arabic RTL handling — `src/shared/components/arabic.ts`

Vendor this helper (idempotent — only create if missing):

```ts
import { CSSProperties } from 'react';

/**
 * Returns the style object every Arabic-containing text node MUST use.
 * `unicodeBidi: 'plaintext'` lets the bidi algorithm pick base direction
 * per paragraph from the first strong character — this is what makes
 * inline French loanwords render in their original Latin order without
 * us having to wrap them.
 */
export function arabicTextStyle(extra: CSSProperties = {}): CSSProperties {
  return {
    direction: 'rtl',
    unicodeBidi: 'plaintext',
    textAlign: 'right',
    fontFeatureSettings: '"calt", "liga", "mark"',
    ...extra,
  };
}

/**
 * For headline / hero text where you want center alignment with bidi
 * still respected.
 */
export function arabicHeroStyle(extra: CSSProperties = {}): CSSProperties {
  return {
    ...arabicTextStyle({ textAlign: 'center', ...extra }),
  };
}

/**
 * The font weight pairing convention for this workflow:
 *   - Arabic glyphs at weight 700 (body) or 800 (display)
 *   - Latin loanwords (pointeuse, maintenance à vie, etc.) at weight 500
 * Same family, different weight = visual distinction without italic.
 *
 * To apply weight 500 only to Latin glyphs inline, use this CSS trick:
 * the `font-synthesis: none` + `font-feature-settings` keeps Arabic at
 * the parent's declared weight while Latin chars inherit a child <span>
 * weight. In practice we just wrap loanwords in a <span> when the
 * planner has flagged them in the `loanwords` array of the beat.
 */
export const LOANWORD_WEIGHT = 500;
export const ARABIC_BODY_WEIGHT = 700;
export const ARABIC_DISPLAY_WEIGHT = 800;
```

When rendering a caption beat with non-empty `loanwords[]`, split the string at each loanword and wrap each loanword in `<span style={{ fontWeight: LOANWORD_WEIGHT }}>`. The Arabic surrounding text uses `ARABIC_BODY_WEIGHT` (or `ARABIC_DISPLAY_WEIGHT` for hero text).

### Font loading

In `src/<CompId>/constants.ts`:

```ts
import { loadFont as loadCairo } from '@remotion/google-fonts/Cairo';
import { loadFont as loadTajawal } from '@remotion/google-fonts/Tajawal';
import { loadFont as loadNotoSansArabic } from '@remotion/google-fonts/NotoSansArabic';

// Load all three in parallel — fallback chain handles missing glyphs.
loadCairo('normal', { weights: ['500', '700', '800'], subsets: ['arabic', 'latin'] });
loadTajawal('normal', { weights: ['500', '700'], subsets: ['arabic', 'latin'] });
loadNotoSansArabic('normal', { weights: ['500', '700'], subsets: ['arabic'] });
```

If `brand.yaml` overrides `arabic_font`, swap the primary `loadCairo` import to that family and adjust `FALLBACK_FONT_STACK` to put it first.

### Persuasion-UI primitives

Vendor each into `src/shared/components/` only if missing. Don't refactor existing copies. Each must be styled with the primitives' own constants (no hardcoded brand colors — accept color props with sensible defaults pulled from `PALETTE`).

#### `<SafeAreaContainer>`

Wraps a scene with the Meta safe-area insets. All content inside is clipped to the inner 70% safe zone.

```tsx
import { AbsoluteFill } from 'remotion';
import React from 'react';
import { SAFE_AREA } from '../../<CompId>/constants';

export const SafeAreaContainer: React.FC<{
  children: React.ReactNode;
  width: number;
  height: number;
}> = ({ children, width, height }) => {
  const top = height * SAFE_AREA.topInsetPct;
  const bottom = height * SAFE_AREA.bottomInsetPct;
  const side = width * SAFE_AREA.sideInsetPct;
  return (
    <AbsoluteFill
      style={{
        paddingTop: top,
        paddingBottom: bottom,
        paddingLeft: side,
        paddingRight: side,
      }}
    >
      {children}
    </AbsoluteFill>
  );
};
```

#### `<KineticCaption>`

Renders a `captions.json` scene's beats in sequence. For each beat, picks one of three reveal modes based on `is_punch`:
- **`is_punch: true`** — scale-pop entrance (0.6 → 1.05 → 1.0 spring), color flash on first frame, Arabic at `ARABIC_DISPLAY_WEIGHT`
- **`is_punch: false`, short (< 4 words)** — fade-up + slight scale entrance (`opacity 0→1`, `translateY 30→0`, `scale 0.96→1` from a single composed progress over `0.5 * fps`)
- **`is_punch: false`, long (≥ 4 words)** — word-cluster reveal: split into 2-3 word chunks, each chunk fades up with a 6-frame stagger

All modes derive multiple animated values from a single normalized progress variable. NO per-character opacity. NO `[1.0, 1.0]` no-op interpolations. Always use `Easing.bezier(0.16, 1, 0.3, 1)` for entrances.

The component renders captions over an optional video clip background — if rendered inside a `<ClipOverlayBackground>`, the caption text gets a `text-shadow: 0 4px 16px rgba(0,0,0,0.8)` AND sits on top of a partial scrim. If on a solid bg scene, no scrim needed.

Loanwords wrapping: when a beat's `loanwords[]` array is non-empty, find each loanword in the beat's `text` and wrap it in `<span style={{ fontWeight: LOANWORD_WEIGHT }}>`. Robust string-replace using the literal loanword (case-sensitive — matches what the planner emitted).

Required props:
- `beats: Array<{ text: string; start_s: number; end_s: number; is_punch: boolean; loanwords: string[] }>`
- `fps: number`
- `width: number` (for line-wrap calculation)
- `colors: { textPrimary: string; textShadow?: string }`

#### `<ComparisonRow>`

For the "biometric? لا. Excel? لا. Xshift? ✓" panel. Each row is one comparison. Stacked vertically with stagger.

Visual rules:
- Loser rows: 60% opacity, `accentRed` `Ban` icon (lucide-react), strikethrough on the label
- Winner row: 100% opacity, `accentGreen` `Check` icon, subtle green halo (box-shadow)
- Each row entrance staggered 0.18s after the previous one
- Final winner row gets a brief scale-pop (0.97 → 1.04 → 1.0 spring) on its entrance to draw the eye

Use the `visual-diagrams` skill's `ComparisonDiagram` for the panel framing if the plan flags `Diagram: comparison`. Otherwise vendor a simpler stack of `<ComparisonRow>` instances.

#### `<BenefitCardStack>`

For listed benefits (e.g. AD-COPY-3's "ما عادش تستحق تسأل / ما عادش تستحق تحسب / ما عادش تقلق" trio). Vertical stack, 0.15s stagger entrance, each card derives its progress from a single normalized variable + per-card start offset. Card style: rounded 16px, semi-transparent fill (rgba `bg` at 0.6), 1.5px border in `primary`, padding 28px, shadow 0 4px 24px rgba(0,0,0,0.4).

#### `<CTAButton>`

Final scene. Big rounded button (radius 999, accent-green fill, white text), with:
- Spring-driven entrance (scale 0.5 → 1.0 with mild overshoot)
- Subtle scale-pulse loop after entrance: 1.0 → 1.04 → 1.0 over 1.2s, looping (use `interpolate(frame % (1.2*fps), [0, 0.6*fps, 1.2*fps], [1, 1.04, 1])`)
- Arrow chevron icon from lucide-react (`ChevronLeft` for RTL — the arrow points toward where the user "goes", which in RTL context is leftward)
- Below the button, smaller text repeating the script's CTA line ("التوصيل في 24 ساعة") in muted color

#### `<GuaranteeBadge>`

Ribbon-style overlay for risk-reversal moments ("paiement à la livraison"). Fixed position bottom-right of safe area. Green ribbon with white text + check icon. Slides in from offscreen-right with spring.

#### `<PhoneFrame>`

For app-demo scenes (the GPS verification, "appareil non autorisée" notification). 3D-perspective bezel:
- Outer rounded rect (radius 60px, 1080×1920 aspect at 0.6 scale), fill `#1F2937`, 8px inner stroke `#0F172A`
- Inner screen area: rounded 48px, accepts a children prop where the demo content sits
- Light specular highlight on the top-left edge (linear gradient overlay)
- Subtle drop shadow `0 30px 60px rgba(0,0,0,0.6)`
- Optional `tilt` prop (degrees) — apply via `transform: rotate(${tilt}deg) perspective(1200px) rotateY(${tilt/2}deg)` for a 3D feel

#### `<HookPunch>`

Wraps scene 1's content with a pattern-interrupt opening:
- First 6 frames: zoom from 1.4 → 1.0 with slight rotation (-2deg → 0)
- Frames 0-3: full-canvas color flash (white → transparent, 50ms feel)
- Optional camera-shake on first 12 frames: tiny x/y sin offset (±4px)
- After frame 30: stable, hands off to the scene's normal animation

Used by ALL scene 1 content unless that scene's `kind: ai-clip` (in which case the AI clip carries the hook).

#### `<ClipOverlayBackground>`

For `kind: hybrid` scenes:

```tsx
import { AbsoluteFill, OffthreadVideo, staticFile } from 'remotion';
import React from 'react';

export const ClipOverlayBackground: React.FC<{
  clipPath: string;
  children: React.ReactNode;
  scrimStrength?: number;   // 0..1, default 0.7
  bottomScrimOnly?: boolean; // true: gradient only at the bottom 40% (preserves cinematic top half)
}> = ({ clipPath, children, scrimStrength = 0.7, bottomScrimOnly = true }) => {
  const gradient = bottomScrimOnly
    ? `linear-gradient(180deg, transparent 60%, rgba(0,0,0,${scrimStrength}) 100%)`
    : `linear-gradient(180deg, rgba(0,0,0,${scrimStrength * 0.3}) 0%, rgba(0,0,0,${scrimStrength}) 100%)`;
  return (
    <AbsoluteFill>
      <OffthreadVideo src={staticFile(clipPath)} />
      <AbsoluteFill style={{ background: gradient }} />
      {children}
    </AbsoluteFill>
  );
};
```

### Per-scene rendering rules

For each scene in `delegation-plan.json`:

| `kind` | Composition layer order |
|---|---|
| `remotion` | `<SafeAreaContainer>` → scene content (KineticCaption, ComparisonRow, BenefitCardStack, CTAButton, etc., per the plan) |
| `ai-clip` | `<OffthreadVideo src={staticFile('clips/<CompId>/<sceneId>.mp4')} />` + optional small caption overlay if the planner specified one |
| `hybrid` | `<ClipOverlayBackground clipPath="clips/<CompId>/<sceneId>.mp4">` → `<SafeAreaContainer>` → `<KineticCaption beats={...} />` |

Scene durations come **verbatim** from `durations.json`. Don't re-derive them. The planner has already computed `max(reading, speaking, min legibility) + buffer` per scene.

### Scene boundaries — `<TransitionSeries>`

Same as the existing workflow. The plan's `Transition out:` field maps to a `<TransitionSeries.Transition>` between consecutive sequences. `hard-cut` = no transition between those two sequences (adjacent `<TransitionSeries.Sequence>`s produce a hard cut).

Plan → preset mapping (RTL note: directional slides should be MIRRORED for an Arabic audience — the eye expects motion right-to-left as the "forward" direction):
- `fade` → `fade()`
- `slide-left` → `slide({ direction: "from-right" })` — content enters from right (forward in RTL)
- `slide-right` → `slide({ direction: "from-left" })` — content enters from left (backward in RTL — use sparingly)
- `slide-up` → `slide({ direction: "from-bottom" })`
- `slide-down` → `slide({ direction: "from-top" })`
- `wipe` → `wipe({ direction: "from-right" })` (RTL-natural wipe)
- `clock-wipe` → `clockWipe({ width, height })`
- `flip` → `flip()`
- `hard-cut` → no transition

Transition durations 0.35–0.5s (stay snappy — Meta-feed pacing, not editorial-explainer pacing). Subtract transition durations from the total comp length in `calculateMetadata.ts`.

### `calculateMetadata.ts` (no audio, durations from JSON)

```ts
import { CalculateMetadataFunction, staticFile } from 'remotion';
import durations from '../../public/durations/<CompId>.json'; // OR fetch via staticFile + parse

export const calculateMetadata: CalculateMetadataFunction<...> = async ({ props }) => {
  // durations.json is in $ARTIFACTS_DIR — copy it into public/durations/<CompId>.json
  // during the build phase OR import it relative to the source tree if you
  // place a copy into src/<CompId>/.
  const totalSec = durations.total_duration_s;
  const fps = durations.fps;
  const transitionOverlapFrames = countTransitions * Math.round(0.4 * fps);
  return {
    durationInFrames: Math.round(totalSec * fps) - transitionOverlapFrames,
    fps,
    width: <from props or constants>,
    height: <from props or constants>,
  };
};
```

**Where to read `durations.json` from**: the cleanest pattern is to copy it into the composition's own folder during the build step. Have your `index.ts` import the json directly via TypeScript's resolveJsonModule. Alternatively place it under `public/durations/<CompId>.json` and load via `fetch(staticFile(...))` inside `calculateMetadata`. Either works — pick whichever makes tsc happiest given the project's tsconfig. (If `resolveJsonModule` isn't enabled in `tsconfig.json`, enable it — it's cheap and idiomatic.)

### Audio layers (no voice — captions ARE the script)

- **No voice manifest, no voice `<Audio>` elements.** Don't synthesize any. The renderer outputs a SILENT mp4 (or one with only SFX/music). The user records voice in post.
- **Music** (if `music-manifest.json` exists): single composition-level `<Audio>` at root, `volume={musicManifest.volume}` (typically 0.2 — but with NO voice ducking concern, you can leave it at the manifest value or ramp).
- **SFX** (if `sfx-manifest.json` exists): same as existing workflow. `intro_whoosh` at frame 0, `outro_stinger` at end, `transition_N` at scene boundaries (offset = end-frame of `from_scene` minus ~3 frames to lead the cut).

### Critical authoring rules (preserved from existing workflow)

- Composition ID = exact `composition_id` from slug.json
- Scene IDs stable: `scene1`, `scene2`, …
- **No TailwindCSS.** Inline styles or style objects.
- All `interpolate()` calls set `extrapolateLeft: "clamp"` and `extrapolateRight: "clamp"`.
- **Durations in seconds × fps**, not raw frame counts: `const FADE_IN = 0.6 * fps;` not `const FADE_IN = 18;`.
- **Premount every `<Sequence>`** / `<TransitionSeries.Sequence>`: `premountFor={fps}`.
- **Never per-character opacity** for text animation.
- **No CSS transitions / animations.** All motion through `interpolate()` + `useCurrentFrame()` / `spring()`.
- **Repo isolation**: do NOT edit files outside `src/<CompId>/` and `src/shared/components/` (and only ADD to shared if missing — never refactor existing shared code).
- **Easing palette** from `rules/timing.md`:
  - Enter motions: `Easing.bezier(0.16, 1, 0.3, 1)` or `Easing.out(Easing.cubic)`
  - Exits: `Easing.in(...)`
  - Editorial fades (rare in Meta ads — they need punch): `Easing.bezier(0.45, 0, 0.55, 1)`
  - Pop / overshoot (use sparingly): `Easing.bezier(0.34, 1.56, 0.64, 1)` or `spring()`
  - **Never `Easing.linear` for non-loop motion.**
- **Composed-progress pattern** for any scene animating 2+ properties on the same beat — derive them from one normalized 0→1 progress variable.

### PHASE_2_CHECKPOINT
- [ ] `src/<CompId>/` populated, including `index.ts` default-export
- [ ] `src/Root.tsx` AND `src/compositions.gen.ts` UNTOUCHED
- [ ] `src/shared/components/` populated with the 10 primitives (or reused if pre-existing)
- [ ] All scenes wrapped in `<TransitionSeries>` per the plan's transitions
- [ ] All `<Sequence>` / `<TransitionSeries.Sequence>` use `premountFor`
- [ ] Hybrid + ai-clip scenes wired to `staticFile('clips/<CompId>/<sceneId>.mp4')`
- [ ] All Arabic text containers use `arabicTextStyle()` or `arabicHeroStyle()`
- [ ] Loanwords wrapped in `<span style={{ fontWeight: LOANWORD_WEIGHT }}>` per beat's `loanwords[]`
- [ ] Fonts loaded via `@remotion/google-fonts` (Cairo, Tajawal, NotoSansArabic) with weights + subsets
- [ ] `calculateMetadata.ts` reads from durations.json (NOT audio probing)
- [ ] If music: composition-level `<Audio volume>` from manifest
- [ ] If SFX: cues wired at correct offsets from manifest
- [ ] No TailwindCSS, no CSS transitions, no per-character opacity
- [ ] No on-screen text references the user / "the prompt" / "as you asked" / etc. (script text is sacred and verbatim)

---

## Phase 3: SELF-CHECK

```bash
npx --yes tsc --noEmit
```

Fix errors. Retry up to two times. If still failing, stop and report.

### PHASE_3_CHECKPOINT
- [ ] `tsc --noEmit` exits 0
- [ ] `src/<CompId>/index.ts` and `src/<CompId>/<CompId>.tsx` present
- [ ] `src/shared/components/` populated with all 10 primitives
- [ ] `src/Root.tsx` unchanged from what you read in Phase 1

---

## Phase 4: REPORT

Final message (plain text, no code fences, no file dumps):

- Composition ID
- Aspect ratio + dimensions
- Modes: music=<bool> sfx=<bool>; delegated_scenes=<count> remotion_scenes=<count>
- Duration source (durations.json — total seconds)
- Scenes implemented (one line each: `sceneN — kind=remotion|ai-clip|hybrid — name — start..end frames`)
- Files written (paths relative to repo root)
- `tsc --noEmit` result (PASS or error summary)

No other text.
