# Component Patterns — Before/After Upgrade Guide

Detailed patterns for upgrading each shared diagram component from wireframe-quality
to professional YouTube-grade visuals.

## Universal Style Constants

Every diagram component uses these shared visual constants. These are built into the
upgraded components via the `DIAGRAM_STYLES` export from `src/shared/components/constants/index.ts`.

```typescript
// Node visual treatment — applied to ALL diagram nodes
export const DIAGRAM_STYLES = {
  /** Multi-layer shadow for depth + glow */
  nodeShadow: (color: string) =>
    `0 4px 20px ${color}30, 0 0 40px ${color}15, inset 0 1px 0 rgba(255,255,255,0.05)`,

  /** Gradient fill for nodes (replaces flat transparent fills) */
  nodeGradient: (color: string) =>
    `linear-gradient(145deg, ${color}28, ${color}0A)`,

  /** Thick accent border (replaces 1px transparent borders) */
  nodeBorder: (color: string, width = 2) =>
    `${width}px solid ${color}55`,

  /** Top accent stripe */
  nodeAccentTop: (color: string) =>
    `3px solid ${color}`,

  /** Connection line glow (duplicate blurred line behind main line) */
  connectionGlowWidth: 8,
  connectionGlowOpacity: 0.12,

  /** Main connection line */
  connectionWidth: 2.5,
  connectionOpacity: 0.6,

  /** Minimum node dimensions */
  minNodeWidth: 160,
  minNodeHeight: 100,
  minHubSize: 180,

  /** Node border radius */
  borderRadius: 14,
  hubBorderRadius: 20,
} as const;
```

---

## HubAndSpoke — Before/After

### BEFORE (wireframe)
```tsx
// Tiny 120px spoke circles, 1px transparent border, no shadow
<div style={{
  width: 120, height: 120,
  border: `1px solid ${color}44`,
  borderRadius: '50%',
  background: 'rgba(255,255,255,0.03)',
}}>
  <div style={{ fontSize: 32 }}>{'⚡'}</div>  {/* emoji icon */}
  <div style={{ fontSize: 20 }}>Label</div>
</div>

// Thin 2px lines with no glow
<line stroke="rgba(255,255,255,0.15)" strokeWidth={2} />
```

### AFTER (professional)
```tsx
// 180px spoke with gradient fill, multi-shadow, brand logo
<div style={{
  width: 180, height: 180,
  border: `2px solid ${color}55`,
  borderRadius: 20,
  background: `linear-gradient(145deg, ${color}28, ${color}0A)`,
  boxShadow: `0 4px 20px ${color}30, 0 0 40px ${color}15,
              inset 0 1px 0 rgba(255,255,255,0.05)`,
}}>
  <Img src={staticFile('images/comp/logo.png')}
       style={{ width: 44, height: 44, objectFit: 'contain' }} />
  <div style={{ fontSize: 24, fontWeight: 700 }}>Label</div>
  <div style={{ fontSize: 20, color: textSecondary }}>Subtitle</div>
</div>

// Glowing connection with blur layer
<line stroke={color} strokeWidth={8} opacity={0.12}
      filter="url(#connectionGlow)" />
<line stroke={color} strokeWidth={2.5} opacity={0.6}
      strokeDasharray={len} strokeDashoffset={dashOff} />
```

### Key Changes
1. **Spoke shape**: `borderRadius: '50%'` (circle) changed to `borderRadius: 20` (rounded rect) — circles waste space for text labels
2. **Spoke size**: 120px -> 180px minimum
3. **Hub size**: 160px -> 200px minimum
4. **Icon**: Unicode emoji -> brand logo `<Img>` or styled letter badge
5. **Background**: Flat rgba -> gradient fill
6. **Shadow**: None -> multi-layer (tight shadow + wide glow + inner highlight)
7. **Border**: 1px 26% opacity -> 2px 33% opacity
8. **Connections**: Single thin line -> glow layer + main line with dash animation

---

## FlowDiagram — Before/After

### BEFORE (wireframe)
```tsx
// 180x100 flat glass card, thin top border
<div style={{
  width: 180, height: 100,
  backgroundColor: 'rgba(255,255,255,0.03)',
  border: `2px solid ${color}44`,
  borderTop: `3px solid ${color}`,
  borderRadius: 12,
}}>
  <div style={{ fontSize: 32 }}>{'◆'}</div>
  <div style={{ fontSize: 24 }}>Process</div>
</div>

// Plain SVG arrow
<line stroke="rgba(255,255,255,0.25)" strokeWidth={2.5} />
<polygon fill="rgba(255,255,255,0.25)" />
```

### AFTER (professional)
```tsx
// 220x120 gradient card with depth
<div style={{
  width: 220, height: 120,
  background: `linear-gradient(145deg, ${color}28, ${color}0A)`,
  border: `2px solid ${color}55`,
  borderTop: `3px solid ${color}`,
  borderRadius: 14,
  boxShadow: `0 4px 20px ${color}30, 0 0 40px ${color}15,
              inset 0 1px 0 rgba(255,255,255,0.05)`,
}}>
  <Img src={logo} style={{ width: 40, height: 40, objectFit: 'contain' }} />
  <div style={{ fontSize: 26, fontWeight: 700 }}>Process</div>
  <div style={{ fontSize: 20 }}>Subtitle</div>
</div>

// Glowing arrow with proper arrowhead
<line stroke={color} strokeWidth={6} opacity={0.12}
      filter="url(#connectionGlow)" />
<line stroke={color} strokeWidth={2.5} opacity={0.6}
      markerEnd="url(#arrowhead)" />
```

### Key Changes
1. **Node size**: 180x100 -> 220x120
2. **Background**: Flat glass -> gradient fill with depth shadow
3. **Arrow styling**: Flat white -> colored glow + matching arrowhead
4. **Icon support**: Character -> image with fallback

---

## LayeredArchitecture — Before/After

### BEFORE (wireframe)
```tsx
// 100px tall bar with 1px border, 4px left accent
<div style={{
  height: 100,
  backgroundColor: 'rgba(255,255,255,0.03)',
  border: `1px solid ${color}33`,
  borderLeft: `4px solid ${color}`,
  borderRadius: 12,
}}>
```

### AFTER (professional)
```tsx
// 110px tall bar with gradient fill, shadow, accent stripe
<div style={{
  height: 110,
  background: `linear-gradient(90deg, ${color}18, ${color}06)`,
  border: `2px solid ${color}33`,
  borderLeft: `4px solid ${color}`,
  borderRadius: 14,
  boxShadow: `0 2px 12px ${color}20, inset 0 1px 0 rgba(255,255,255,0.03)`,
}}>
```

### Key Changes
1. **Height**: 100 -> 110px for more breathing room
2. **Background**: Flat glass -> horizontal gradient (stronger near left accent)
3. **Shadow**: None -> subtle depth + inner highlight
4. **Border**: 1px -> 2px for visibility
5. **Item badges**: Plain text -> gradient-filled mini badges

---

## ComparisonDiagram — Before/After

### BEFORE (wireframe)
```tsx
// Glass panel with thin top accent
<div style={{
  backgroundColor: 'rgba(255,255,255,0.03)',
  border: `1px solid ${color}33`,
  borderTop: `3px solid ${color}`,
  borderRadius: 16,
}}>
```

### AFTER (professional)
```tsx
// Rich panel with gradient header zone
<div style={{
  background: `linear-gradient(180deg, ${color}15 0%, ${color}04 30%, transparent 100%)`,
  border: `2px solid ${color}33`,
  borderTop: `3px solid ${color}`,
  borderRadius: 16,
  boxShadow: `0 4px 24px ${color}20, inset 0 1px 0 rgba(255,255,255,0.04)`,
}}>
```

### Key Changes
1. **Background**: Flat glass -> vertical gradient (stronger at top near accent)
2. **Shadow**: None -> depth shadow matching accent color
3. **Item rows**: Flat background -> subtle gradient with hover-like treatment
4. **VS divider**: Plain circle -> glowing circle with pulsing animation

---

## Styled Letter Badge (Icon Fallback)

When no brand logo image is available, use a styled letter badge instead of Unicode:

```tsx
// Styled letter badge — used when logo image unavailable
<div style={{
  width: 44, height: 44,
  borderRadius: 10,
  background: `linear-gradient(135deg, ${color}, ${color}88)`,
  display: 'flex', alignItems: 'center', justifyContent: 'center',
  boxShadow: `0 2px 8px ${color}40`,
}}>
  <div style={{
    fontSize: 22, fontWeight: 900,
    color: '#ffffff',
    display: 'block',
  }}>
    {label.charAt(0).toUpperCase()}
  </div>
</div>
```

This produces a colored rounded square with the first letter — much more professional
than a raw Unicode symbol.
