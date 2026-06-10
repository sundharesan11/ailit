# Responsive Layout Examples

## Auto-Fit Card Grid

```css
.projects {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr));
  gap: 1.5rem;
}
```

## Tailwind Mobile-First Section

```html
<section class="px-4 py-12 md:px-8 lg:px-16">
  <div class="mx-auto max-w-5xl grid gap-8 md:grid-cols-2">
    <div>...</div>
    <div>...</div>
  </div>
</section>
```

## Test Cases

- Layout renders without horizontal scroll at 320, 768, 1024, and 1440 px.
- Cards wrap from one column to multiple columns without orphan gaps.
- The hero heading wraps gracefully with a 40-character title.
