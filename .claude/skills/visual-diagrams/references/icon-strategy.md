# Icon & Logo Strategy for Diagram Nodes

## Priority Order

When a diagram node represents a known tool, service, or technology:

### 1. Brand Logo Image (Best)

Download to `public/images/<composition>/` and use `<Img>` from `remotion`:

```tsx
import { Img, staticFile } from 'remotion';

<Img
  src={staticFile('images/mycomp/docker-logo.png')}
  style={{ width: 44, height: 44, objectFit: 'contain' }}
/>
```

**Where to get logos:**
- GitHub organization avatars: `https://github.com/<org>.png?size=128`
  - `https://github.com/docker.png?size=128` -> Docker whale
  - `https://github.com/cloudflare.png?size=128` -> Cloudflare logo
  - `https://github.com/vercel.png?size=128` -> Vercel triangle
  - `https://github.com/openai.png?size=128` -> OpenAI logo
  - `https://github.com/anthropics.png?size=128` -> Anthropic logo
- Simple Icons CDN: `https://cdn.simpleicons.org/<name>/<color>`
  - Works for 3000+ brands
  - Returns SVG that can be saved as `.svg`
- Product websites: `/favicon.ico` or `/logo.png`

**Naming convention:** `<tool-lowercase>-logo.png` (e.g., `docker-logo.png`, `cloudflare-logo.png`)

**Size:** Download at 128x128px minimum. Display at 40-48px in nodes.

### 2. Styled Letter Badge (Good Fallback)

When logo isn't available or would take too long to acquire:

```tsx
const LetterBadge: React.FC<{ label: string; color: string; size?: number }> = ({
  label, color, size = 44
}) => (
  <div style={{
    width: size, height: size,
    borderRadius: size * 0.22,
    background: `linear-gradient(135deg, ${color}, ${color}88)`,
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    boxShadow: `0 2px 8px ${color}40`,
  }}>
    <div style={{
      fontSize: size * 0.5, fontWeight: 900,
      color: '#ffffff', display: 'block',
    }}>
      {label.charAt(0).toUpperCase()}
    </div>
  </div>
);
```

### 3. Unicode Text Symbols (Minimal Fallback)

ONLY these symbols are safe (they respect CSS `color` in headless Chromium):

**Safe:** `▸` `▹` `●` `○` `◆` `◇` `■` `□` `▣` `▲` `△` `▷` `◁` `★` `☆`
`✓` `✕` `→` `←` `↑` `↓` `⟲` `⟳` `⚐` `⊕` `⊖` `⊗`

**NEVER use emoji:** `🐳` `🔧` `⚡` `🗄` `📦` `🌐` `☁️` `🔒` `🚀` — these render as
black glyphs in headless Chromium and are invisible on dark backgrounds.

## Per-Component Icon Props

All diagram components accept an `iconSrc` prop on their nodes. When provided, it renders
an `<Img>` element. When absent, falls back to the `icon` string prop (rendered as a styled
letter badge if it's a single character, or as a Unicode symbol).

```tsx
// With brand logo
<HubAndSpoke
  hub={{ label: 'Docker', iconSrc: staticFile('images/comp/docker-logo.png'), color: '#2496ED' }}
  spokes={[
    { label: 'Redis', iconSrc: staticFile('images/comp/redis-logo.png'), color: '#DC382D', triggerFrame: 30 },
    { label: 'Postgres', icon: 'P', color: '#4169E1', triggerFrame: 60 },  // letter badge fallback
  ]}
/>
```

## Batch Logo Acquisition

During Phase 4, if a diagram needs multiple brand logos:

1. Create a list of needed logos with GitHub org names
2. Download all at once:
   ```bash
   for org in docker cloudflare vercel redis; do
     curl -sL "https://github.com/${org}.png?size=128" \
       -o "public/images/<composition>/${org}-logo.png"
   done
   ```
3. Verify each downloaded file is a valid image (not a 404 HTML page)
4. Reference in scene code via `staticFile('images/<composition>/<org>-logo.png')`
