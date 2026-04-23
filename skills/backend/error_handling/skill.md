# Skill: Error Handling

Use this skill when designing or fixing error behavior in backend code.

## Core Guidance

- Classify errors as validation, business rule, dependency, infrastructure, or unexpected.
- Preserve original error context while returning safe messages to callers.
- Handle errors at the boundary that can make a meaningful decision.
- Avoid catching broad exceptions unless you re-raise, translate, or record them intentionally.
- Log actionable context, not secrets.
- Make user-facing error contracts stable.

## Agent Checklist

1. Identify where the error originates and where it should be handled.
2. Decide whether to recover, retry, translate, or fail.
3. Keep stack traces or causal context for operators.
4. Add tests for expected error paths.
5. Ensure sensitive values are not logged.

## Pitfalls

- Swallowing exceptions and returning partial success.
- Turning all errors into generic internal errors.
- Leaking credentials or personal data in logs.
- Mixing domain failures with transport exceptions.
