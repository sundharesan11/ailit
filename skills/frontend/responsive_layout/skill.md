# Skill: Responsive Layout

Use this skill when building page layouts, grids, navigation, or sections that must work across mobile, tablet, and desktop.

## Core Guidance

- Design mobile-first: start with the narrow layout, then enhance at wider breakpoints.
- Prefer intrinsic layout (flexbox, grid, `minmax`, `auto-fit`) over per-device pixel tweaking.
- Use a small, consistent breakpoint set; avoid one-off breakpoints per component.
- Use relative units (`rem`, `%`, viewport units) for sizing; reserve pixels for borders and hairlines.
- Constrain reading width: long text lines should stay near 60 to 80 characters.
- Let content define height; avoid fixed heights that clip or overflow with real content.
- Test with long words, long names, and translated strings, not just ideal content.

## Agent Checklist

1. Identify the layout regions (header, hero, content grid, footer) and how each reflows.
2. Pick breakpoints from the project's existing system (for Tailwind: `sm`, `md`, `lg`, `xl`).
3. Verify navigation works at narrow widths (collapse, wrap, or menu pattern).
4. Check images scale with `max-width: 100%` and explicit aspect ratios to avoid layout shift.
5. Confirm no horizontal scrollbar appears between 320 px and the widest design width.
6. Re-test after content changes; real text breaks layouts that lorem ipsum survives.

## Pitfalls

- Desktop-first CSS overridden by a pile of max-width exceptions.
- Hiding important content on mobile instead of redesigning the flow.
- Grids that work at exactly three widths and break in between.
- Fixed-position elements covering content on short viewports.
