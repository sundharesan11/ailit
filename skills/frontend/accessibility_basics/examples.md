# Accessibility Basics Examples

## Form Field

```html
<label for="email">Email address</label>
<input id="email" type="email" autocomplete="email" required />
<p id="email-error" role="alert" hidden>Enter a valid email address.</p>
```

## Decorative Vs Informative Images

```html
<img src="divider.svg" alt="" />
<img src="chart-q3.png" alt="Q3 revenue grew 18 percent over Q2" />
```

## Test Cases

- Every page section is reachable with Tab and Shift+Tab in a sensible order.
- Submitting an invalid form moves focus to the first error message.
- The page is usable at 200 percent zoom without horizontal scrolling.
- Animations respect the `prefers-reduced-motion` media query.
