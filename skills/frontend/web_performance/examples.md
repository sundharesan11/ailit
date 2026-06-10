# Web Performance Examples

## Responsive Hero Image

```html
<img
  src="hero-1200.webp"
  srcset="hero-600.webp 600w, hero-1200.webp 1200w, hero-2000.webp 2000w"
  sizes="100vw"
  width="1200"
  height="640"
  fetchpriority="high"
  alt="Workspace with laptop showing the portfolio homepage"
/>
```

## Deferred Analytics

```html
<script defer src="/analytics.js"></script>
```

## Test Cases

- Lighthouse performance score stays at or above the project budget.
- No layout shift when images and fonts finish loading.
- The page is interactive on a simulated mid-range phone within budget.
