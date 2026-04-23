# Skill: Debugging Strategy

Use this skill when a test fails, behavior is unexpected, or a bug report needs investigation.

## Core Guidance

- Reproduce the failure before changing code.
- Separate observation from hypothesis.
- Narrow the problem with the smallest reliable test or command.
- Inspect recent changes and boundary conditions.
- Fix the root cause, not only the symptom.
- Add a regression test when the bug represents expected future behavior.

## Agent Checklist

1. State expected and actual behavior.
2. Capture the reproduction command or steps.
3. Rank likely causes by evidence.
4. Inspect the smallest relevant code path.
5. Implement the smallest defensible fix.
6. Run focused validation, then broader validation if risk requires it.

## Pitfalls

- Guessing before reproducing.
- Editing multiple possible fixes at once.
- Ignoring flaky or environment-specific signals.
- Leaving no regression coverage.
