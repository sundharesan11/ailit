# Skill: Accessibility Basics

Use this skill when building or reviewing web pages, components, or forms so they work for keyboard and assistive-technology users.

## Core Guidance

- Use semantic HTML first: headings in order, lists for lists, buttons for actions, links for navigation.
- Every interactive element must be reachable and operable by keyboard alone.
- Keep visible focus styles; never remove outlines without an equal replacement.
- Give images meaningful `alt` text, or empty `alt` when decorative.
- Label every form control; placeholder text is not a label.
- Meet contrast ratios: 4.5:1 for body text, 3:1 for large text and UI parts.
- Use ARIA only when semantic HTML cannot express the behavior.
- Announce dynamic changes (toasts, validation errors) with live regions when they matter.

## Agent Checklist

1. Check the heading hierarchy is sequential and unique per page.
2. Tab through the page mentally: confirm order, focus visibility, and no traps.
3. Confirm form fields have associated labels and clear error text.
4. Verify color is never the only signal for state or meaning.
5. Check touch targets are at least 44x44 px on mobile layouts.
6. Run an automated check (Lighthouse or axe) when tooling is available.

## Pitfalls

- Div-and-onClick buttons that keyboards cannot reach.
- ARIA roles that contradict the native element semantics.
- Auto-playing motion without a reduced-motion fallback.
- Modal dialogs that do not trap and restore focus.
