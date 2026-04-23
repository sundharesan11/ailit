# Skill: Test-Driven Development

Use this skill when adding behavior or fixing bugs where tests can define the desired outcome.

## Core Guidance

- Write the smallest failing test that captures the behavior.
- Make the test name describe the expected behavior.
- Implement only enough code to pass.
- Refactor after the test passes.
- Prefer domain-level tests for business behavior and boundary tests for integrations.
- Keep mocks at real external boundaries.

## Agent Checklist

1. State the behavior to prove.
2. Add or update the focused test.
3. Confirm the test would fail without the change when practical.
4. Implement the smallest change.
5. Run focused tests and report the command.

## Pitfalls

- Testing implementation details.
- Writing broad tests that obscure the failure reason.
- Mocking internal collaborators too aggressively.
- Skipping the regression test for a bug fix.
