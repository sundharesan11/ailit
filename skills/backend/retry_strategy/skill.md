# Skill: Retry Strategy

Use this skill when adding retries around network calls, queues, jobs, APIs, or transient infrastructure failures.

## Core Guidance

- Retry only failures that are likely to be transient.
- Use bounded retries with exponential backoff and jitter.
- Make side-effecting operations idempotent before retrying.
- Use deadlines or timeouts so retries do not extend forever.
- Stop retrying on validation, authorization, or permanent business errors.
- Route exhausted attempts to a clear failure path such as a dead-letter queue or visible error state.

## Agent Checklist

1. Classify retryable and non-retryable errors.
2. Confirm idempotency or add an idempotency key.
3. Choose max attempts, backoff, jitter, and timeout.
4. Preserve useful error context after retries fail.
5. Add tests for success after retry and final failure.
6. Add logging or metrics where the project already has observability patterns.

## Pitfalls

- Retrying every exception.
- Retrying non-idempotent writes.
- Coordinated retries without jitter.
- Hiding repeated failures from callers and operators.
