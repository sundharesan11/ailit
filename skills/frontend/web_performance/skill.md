# Skill: Web Performance

Use this skill when building or optimizing web pages where load speed, interactivity, and Core Web Vitals matter.

## Core Guidance

- Serve images responsively: modern formats (WebP/AVIF), explicit width and height, `srcset` for densities, lazy-load below the fold.
- Never lazy-load the largest above-the-fold image; it drives Largest Contentful Paint.
- Reserve space for images, embeds, and ads to keep Cumulative Layout Shift near zero.
- Self-host fonts with `font-display: swap` and preload only the one or two faces used above the fold.
- Ship less JavaScript: prefer static rendering, defer non-critical scripts, code-split routes.
- Cache aggressively: immutable hashed assets, sensible HTML cache headers or static hosting.
- Measure before and after with Lighthouse or PageSpeed Insights; do not optimize blind.

## Agent Checklist

1. Identify the LCP element and make sure it loads early (preload, no lazy attribute).
2. Add explicit dimensions or aspect-ratio to every image and embed.
3. Audit third-party scripts; remove or defer anything not essential to first paint.
4. Check the framework's image and font primitives are used (for Next.js: `next/image`, `next/font`).
5. Run Lighthouse and record the scores in the validation notes.
6. Re-check after content or dependency changes; budgets drift quietly.

## Pitfalls

- A 2 MB hero image behind a perfect-looking dev server.
- Lazy-loading everything, including the hero.
- Font flashes from loading four weights when two are used.
- Measuring only on fast hardware and broadband.
