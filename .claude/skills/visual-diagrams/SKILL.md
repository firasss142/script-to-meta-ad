---
name: visual-diagrams
description: >
  Professional diagram and architecture visualization design system for Remotion video
  compositions. Use when building: architecture diagrams, hub-and-spoke layouts, flowcharts,
  pipeline visualizations, comparison panels, layered stacks, data flow diagrams, or any
  scene with connected boxes/nodes/arrows. Ensures YouTube-grade visual quality with gradient
  fills, depth shadows, glow effects, brand logo icons, and animated connections. Triggers on:
  "diagram", "architecture", "flowchart", "pipeline", "hub and spoke", "data flow",
  "system diagram", "connected boxes", "infrastructure layout", "tech stack visualization".
---

# Visual Diagrams Design System

Professional-grade diagram components for Remotion explainer videos. Replaces wireframe-quality
boxes-and-lines with YouTube-grade visuals: gradient fills, depth shadows, animated glowing
connections, brand logo images, and layered visual hierarchy.

## When to Use This Skill

- Phase 4 scene building when the plan calls for architecture/system diagrams
- Any scene showing relationships between components (hub-spoke, flow, layers)
- Infrastructure/tech stack visualizations
- Before/after or comparison layouts
- Data flow or pipeline diagrams

## The Problem This Solves

Without this skill, sub-agents produce **wireframe-quality diagrams**:
- Thin 1-2px borders on transparent boxes
- Unicode characters as "icons" (invisible in headless Chromium)
- No shadows, no depth, no visual hierarchy
- Tiny nodes that look like developer sketches
- Thin dashed connection lines with no glow or energy

## Quick Reference: Which Component to Use

| Visual Need | Component | When to Use |
|---|---|---|
| **Multi-stage process (PREFERRED)** | `InfographicFlow` | Pipelines, workflows, how-it-works, stage-by-stage explanations — enterprise-grade pastel bands with Lucide icons |
| Central element + surrounding services | `HubAndSpoke` | Tech stacks, service architectures, API ecosystems |
| Sequential process/pipeline | `FlowDiagram` | Simple 3-5 node pipelines, build chains |
| Stacked layers (UI > API > DB) | `LayeredArchitecture` | Software architecture, network stacks, abstraction layers |
| Side-by-side comparison | `ComparisonDiagram` | Before/after, old vs new, competitor analysis |
| Git workflow visualization | `GitBranching` | Branching strategies, CI/CD flows, merge patterns |

## Icon Library: lucide-react

All diagram components support Lucide icons (1000+ professional SVG icons). Import directly:

```tsx
import { Search, Brain, Cpu, Database, Shield, Send, Package, Puzzle } from 'lucide-react';

// Use in InfographicFlow stages
{ label: 'Discovery', icon: Search, nodes: [...] }

// Use in DiagramIcon wrapper
<DiagramIcon icon={Search} color="#2E7D32" bg="#C8E6C9" size={48} />
```

Browse all icons: https://lucide.dev/icons

### DiagramIcon Wrapper

`DiagramIcon` wraps any Lucide icon in a colored circle/rounded background with shadow:

```tsx
import { DiagramIcon } from '../shared/components/diagrams';

<DiagramIcon icon={Brain} color="#1565C0" bg="#BBDEFB" size={52} variant="circle" />
<DiagramIcon icon={Database} color="#E65100" bg="#FFE0B2" size={48} variant="rounded" />
<DiagramIcon imageSrc={staticFile('images/comp/logo.png')} color="#333" size={48} />
<DiagramIcon letter="A" color="#7B1FA2" bg="#E1BEE7" size={44} />
```

Priority: Lucide icon > brand logo image > styled letter badge.

## InfographicFlow — Enterprise-Grade Stage Diagrams

The flagship component. Produces pastel-banded row layouts like enterprise infographics
(Anthropic, Google, DailyDoseofDS style).

```tsx
import { InfographicFlow } from '../shared/components/diagrams';
import { Search, Brain, Zap } from 'lucide-react';

<InfographicFlow
  title="How It Works"
  subtitle="A 5-stage pipeline"
  mode="light"  // or "dark"
  stages={[
    {
      label: 'Discovery',
      icon: Search,
      nodes: [
        { label: 'Scan', icon: Search },
        { label: 'Match', icon: Brain },
      ],
      connector: 'arrow',  // or '+' or custom string
      description: 'Finds relevant items',
    },
    // ... more stages
  ]}
/>
```

### Light vs Dark Mode

- **Light mode** (`mode="light"`): White background, pastel-colored bands (green, blue, orange,
  purple, yellow, cyan, red, indigo). Enterprise infographic style.
- **Dark mode** (`mode="dark"`): `#0B1120` background, subtle tinted bands. Matches existing
  video dark theme.

Both modes use the same component — just flip the `mode` prop.

### Palette System

Custom palettes available via `getDiagramPalette()` and `getStagePalette()`:

```tsx
import { getDiagramPalette, getStagePalette } from '../shared/components/diagrams';

const palette = getDiagramPalette('light');
const stage0Colors = getStagePalette(palette, 0); // green band
// stage0Colors.band, .accent, .iconBg, .text, .textMuted
```

## Design Principles

### 1. Gradient Fills Over Flat Colors

Every node/box MUST use a subtle gradient fill, not a flat color. Gradients create depth and
make elements feel three-dimensional.

```tsx
// WRONG - flat transparent fill (wireframe look)
backgroundColor: `${color}22`

// CORRECT - gradient fill with depth
background: `linear-gradient(135deg, ${color}25, ${color}08)`
```

### 2. Multi-Layer Shadows for Depth

Every node MUST have at least a 2-layer box shadow: a tight inner shadow for definition
and a wider outer glow for atmosphere.

```tsx
// WRONG - no shadow (flat, floats in void)
// (no boxShadow property)

// CORRECT - depth + glow
boxShadow: `0 4px 20px ${color}30, 0 0 40px ${color}15, inset 0 1px 0 rgba(255,255,255,0.05)`
```

### 3. Thick Borders with Gradient Feel

Use 2-3px borders minimum. 1px borders disappear on YouTube at 720p. Use the node's
accent color at 40-60% opacity for borders (not 20%).

```tsx
// WRONG - too thin, too transparent
border: `1px solid ${color}22`

// CORRECT - visible at YouTube resolution
border: `2px solid ${color}66`
borderTop: `3px solid ${color}`  // accent top edge
```

### 4. Brand Logo Images Instead of Unicode Icons

When referencing known tools/services (GitHub, Docker, AWS, Cloudflare, etc.), use actual
brand logo images downloaded to `public/images/<composition>/`. Unicode symbols and emoji
render as black glyphs in headless Chromium.

```tsx
// WRONG - invisible in rendered video
<div style={{ fontSize: 36 }}>{'🐳'}</div>

// CORRECT - actual brand logo
<Img src={staticFile('images/mycomp/docker-logo.png')}
     style={{ width: 40, height: 40, objectFit: 'contain' }} />
```

**Image acquisition**: During Phase 4 scene building, if a brand logo is needed:
1. Check if it already exists in `public/images/<composition>/`
2. If not, download from GitHub avatars: `https://github.com/<org>.png?size=128`
3. Or use the scene's `screenshots.json` manifest for batch capture
4. Fall back to a **styled letter badge** (colored circle + first letter) — never Unicode emoji

### 5. Generous Node Sizing

Nodes must be large enough to be instantly readable at 720p. Minimum sizes:

| Element | Minimum Size | Recommended |
|---|---|---|
| Hub/center node | 180x120px | 200x140px |
| Spoke/satellite node | 160x100px | 180x110px |
| Flow diagram node | 200x100px | 220x120px |
| Layer bar height | 90px | 100-120px |
| Icon/logo inside node | 36x36px | 40-48px |
| Node label font | 24px | 26-28px |
| Sub-label font | 20px | 22px |

### 6. Animated Glowing Connections

Connection lines between nodes must have:
- Minimum 2.5px stroke width (not 1-2px)
- A subtle glow via SVG filter or duplicate line with blur
- Animated draw-on via strokeDasharray/strokeDashoffset
- Color matching the source or target node's accent

```tsx
// WRONG - thin invisible line
<line stroke={color} strokeWidth={1} strokeDasharray="4 4" />

// CORRECT - visible glowing connection
<>
  {/* Glow layer */}
  <line stroke={color} strokeWidth={6} opacity={0.15}
        filter="url(#connectionGlow)" />
  {/* Main line */}
  <line stroke={color} strokeWidth={2.5} opacity={0.7}
        strokeDasharray={len} strokeDashoffset={dashOff} />
</>
```

### 7. SVG Glow Filter (Add to Every Diagram SVG)

```tsx
<svg>
  <defs>
    <filter id="connectionGlow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="4" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
    <marker id="arrowhead" markerWidth="12" markerHeight="8"
            refX="11" refY="4" orient="auto">
      <polygon points="0 0, 12 4, 0 8" fill={COLORS.primary} />
    </marker>
  </defs>
</svg>
```

### 8. Background Atmosphere

Diagram scenes should include subtle background elements for depth:
- `ProceduralNoise` with low opacity (0.08-0.12) for organic movement
- Subtle radial gradient centered on the diagram's focal point
- Optional grid pattern at very low opacity (0.03-0.05)

```tsx
{/* Atmospheric background */}
<div style={{
  position: 'absolute', inset: 0,
  background: `radial-gradient(ellipse at ${CENTER_X}px ${CENTER_Y}px,
    ${COLORS.primary}08 0%, transparent 60%)`,
}} />
<ProceduralNoise seed="diagram" color={COLORS.primary}
                 count={12} opacity={0.08} speed={0.004} />
```

## Component Upgrade Patterns

See `references/component-patterns.md` for detailed before/after code patterns for each
shared component (HubAndSpoke, FlowDiagram, LayeredArchitecture, ComparisonDiagram).

See `references/icon-strategy.md` for the complete icon/logo acquisition and fallback strategy.

See `references/animation-choreography.md` for connection line animation, node entrance
sequencing, and SpotlightFocus patterns for multi-phase diagrams.

## Integration with Phase 4

When Phase 4 encounters a scene plan that calls for an architecture diagram or connected
component visualization:

1. **Load this skill** for design guidance
2. **Check shared components** — use `HubAndSpoke`, `FlowDiagram`, `LayeredArchitecture`,
   `ComparisonDiagram`, or `GitBranching` as the foundation
3. **Download brand logos** if the diagram references known tools/services
4. **Use the component's props** — all components accept `nodeStyle`, `connectionStyle`,
   and `iconSrc` overrides for professional visual treatment
5. **Add background atmosphere** — ProceduralNoise + radial gradient behind the diagram
6. **Run `/validate-scene`** after building to catch visual quality issues

## Rulecheck Integration

The visual scanner (`rulecheck-scanner-visual`) checks for these diagram-specific violations:

| Rule | Pattern | Fix |
|---|---|---|
| Wireframe node (no gradient/shadow) | `backgroundColor: '${color}` + hex ≤ 2 chars opacity, no `boxShadow` | Add gradient fill + multi-layer shadow |
| Thin border on diagram node | `border: '1px` on diagram container | Minimum 2px border |
| Missing connection glow | SVG `<line>` without glow filter or duplicate blur line | Add glow layer or SVG filter |
| Unicode emoji as diagram icon | Emoji char in node content div | Replace with brand logo image or styled letter badge |
| Undersized diagram node | Node width < 160px or height < 100px | Increase to minimum sizes |
| Flat connection lines | `strokeWidth` < 2.5 on connection lines | Increase to 2.5px minimum |
