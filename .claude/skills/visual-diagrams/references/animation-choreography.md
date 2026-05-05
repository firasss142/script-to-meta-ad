# Animation Choreography for Diagrams

## Entrance Sequence

Diagram elements should appear in this order, synced to narration:

1. **Background atmosphere** — fade in during AUDIO_OFFSET (frames 0-10)
2. **Hub/center node** — spring entrance at first mention (`wordToFrame`)
3. **Connection lines** — draw-on starting 8 frames after hub
4. **Spoke/satellite nodes** — each at its spoken word timestamp
5. **Labels and sublabels** — appear with their parent node (staggered 5 frames)

```tsx
// Choreography example
const hubFrame = wordToFrame(hubTimestamp, OFFSET);

// Hub enters first
const hubScale = spring({
  frame: Math.max(0, frame - hubFrame),
  fps, config: SPRINGS.entrance,
  durationRestThreshold: 0.001,
});

// Lines start drawing 8 frames after hub
const lineProgress = spring({
  frame: Math.max(0, frame - hubFrame - 8),
  fps, config: SPRINGS.smooth,
  durationRestThreshold: 0.001,
});

// Each spoke at its own spoken word
const spokeScale = spring({
  frame: Math.max(0, frame - spokeTimestamp),
  fps, config: SPRINGS.bouncy,
  durationRestThreshold: 0.001,
});
```

## Connection Line Animation

### Draw-On Effect (Preferred)

Lines "draw" from source to target using strokeDasharray:

```tsx
const dx = targetX - sourceX;
const dy = targetY - sourceY;
const lineLength = Math.sqrt(dx * dx + dy * dy);

// Shorten lines to stop at node edges
const dist = lineLength;
const ux = dx / dist;
const uy = dy / dist;
const SOURCE_MARGIN = 90;  // hub half-size + gap
const TARGET_MARGIN = 80;  // spoke half-size + gap
const sx = sourceX + ux * SOURCE_MARGIN;
const sy = sourceY + uy * SOURCE_MARGIN;
const ex = targetX - ux * TARGET_MARGIN;
const ey = targetY - uy * TARGET_MARGIN;
const visibleLength = Math.sqrt((ex-sx)**2 + (ey-sy)**2);

const dashOffset = interpolate(lineProgress, [0, 1], [visibleLength, 0], {
  extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
});

// Glow layer (renders behind)
<line x1={sx} y1={sy} x2={ex} y2={ey}
  stroke={color} strokeWidth={8} opacity={0.12}
  filter="url(#connectionGlow)" />

// Main line with draw-on
<line x1={sx} y1={sy} x2={ex} y2={ey}
  stroke={color} strokeWidth={2.5} opacity={0.6}
  strokeDasharray={visibleLength}
  strokeDashoffset={dashOffset}
  strokeLinecap="round" />
```

### Pulse Effect (For Active Connections)

After draw-on completes, add a subtle pulse to show "data flow":

```tsx
const pulse = 0.5 + 0.2 * Math.sin((frame / 20) * Math.PI);

<line stroke={color} strokeWidth={2.5} opacity={pulse}
      strokeDasharray="8 16"
      strokeDashoffset={-frame * 0.8}  // flowing dots
      strokeLinecap="round" />
```

## SpotlightFocus for Multi-Phase Diagrams

When narration moves through different parts of a diagram, use SpotlightFocus to
highlight the active section:

```tsx
// Phase A: Hub + first 2 spokes active
const isPhaseA = frame < PHASE_B_START;
const isPhaseB = frame >= PHASE_B_START && frame < PHASE_C_START;
const isPhaseC = frame >= PHASE_C_START;

{nodes.map(node => {
  const isActive =
    (isPhaseA && PHASE_A_NODES.includes(node.id)) ||
    (isPhaseB && PHASE_B_NODES.includes(node.id)) ||
    isPhaseC;  // all active in final phase

  return (
    <SpotlightFocus key={node.id} active={isActive} dimOpacity={0.25}>
      <DiagramNode {...node} />
    </SpotlightFocus>
  );
})}
```

## Arrowhead Definitions

Always include this SVG `<defs>` block in diagram SVGs:

```tsx
<svg style={{ position: 'absolute', inset: 0, width: '100%', height: '100%' }}>
  <defs>
    {/* Glow filter for connection lines */}
    <filter id="connectionGlow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="4" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>

    {/* Arrowhead marker */}
    <marker id="arrowhead" markerWidth="12" markerHeight="8"
            refX="11" refY="4" orient="auto">
      <polygon points="0 0, 12 4, 0 8" fill={COLORS.primary} />
    </marker>

    {/* Color-specific arrowheads (generate per node color) */}
    {nodeColors.map(color => (
      <marker key={color} id={`arrow-${color.replace('#','')}`}
              markerWidth="12" markerHeight="8" refX="11" refY="4" orient="auto">
        <polygon points="0 0, 12 4, 0 8" fill={color} />
      </marker>
    ))}
  </defs>
  {/* ... lines ... */}
</svg>
```

## Orthogonal (Right-Angle) Paths

For flowcharts and layered diagrams, use L-shaped or Z-shaped paths:

```tsx
const createOrthogonalPath = (
  from: { x: number; y: number },
  to: { x: number; y: number }
) => {
  const midX = (from.x + to.x) / 2;
  return `M ${from.x} ${from.y} H ${midX} V ${to.y} H ${to.x}`;
};

<path
  d={createOrthogonalPath(source, target)}
  stroke={color}
  strokeWidth={2.5}
  fill="none"
  markerEnd="url(#arrowhead)"
  strokeLinecap="round"
  strokeLinejoin="round"
/>
```

## SFX Pairing for Diagram Animations

Every major diagram entrance should have matching SFX in Composition.tsx:

| Animation Event | SFX | Volume | Offset |
|---|---|---|---|
| Hub/center node entrance | `cinematic-whoosh.mp3` | 0.35 | At hub triggerFrame |
| Each spoke/node pop-in | `pop.mp3` | 0.3 | At each node triggerFrame |
| Connection line draw-on | `ui-switch` (`@remotion/sfx`) | 0.2 | At line start |
| Full diagram reveal | `spring-pop.mp3` | 0.4 | When last element appears |
| SpotlightFocus shift | `page-turn` (`@remotion/sfx`) | 0.2 | At phase boundary |
