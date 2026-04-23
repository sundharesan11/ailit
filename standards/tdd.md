# Standard: Test-Driven Development

Use this standard when adding behavior, fixing bugs, or changing contracts.

## Purpose

TDD keeps the work anchored to observable behavior. Tests should describe what the system must do and give agents fast feedback while editing.

## Cycle

1. Write or update a failing test that captures the desired behavior.
2. Implement the smallest change that passes the test.
3. Refactor while keeping tests green.
4. Add edge cases when risk justifies them.

## AI Agent Instructions

When applying this standard:

1. Start by identifying the behavior under test.
2. Prefer focused tests over broad snapshots.
3. Cover regression cases when fixing bugs.
4. Run the narrowest useful test first, then broader checks if needed.
5. Report any tests that could not be run.

## Review Checklist

- Does the test fail for the right reason before the fix?
- Does the test assert behavior rather than implementation details?
- Are edge cases covered where failure would be costly?
- Are mocks limited to real external boundaries?
- Is the test name clear enough to document the expected behavior?

## Common Pitfalls

- Writing tests after the fact that only mirror the implementation.
- Overusing mocks inside the domain.
- Adding brittle snapshot tests for dynamic output.
- Skipping regression tests for production bugs.
