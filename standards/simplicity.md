# Standard: Simplicity

Use this standard when designing, reviewing, or implementing any engineering change.

## Purpose

Simplicity keeps systems easier to understand, test, change, and debug. AI agents should prefer the smallest design that satisfies the current requirement without blocking likely near-term evolution.

## Principles

- Solve the actual problem before adding optional flexibility.
- Prefer boring, well-understood technology.
- Keep modules small and named after their responsibility.
- Remove dead paths, unused abstractions, and duplicate logic.
- Make data flow explicit instead of relying on hidden global state.

## AI Agent Instructions

When applying this standard:

1. State the simplest viable approach.
2. Identify any abstraction being introduced and why it is justified.
3. Avoid speculative extension points unless the current system already needs them.
4. Prefer code that can be explained in a few sentences.
5. Call out complexity that should be deferred.

## Review Checklist

- Can a new developer understand the change without reading unrelated files?
- Is every new layer pulling its weight?
- Are names specific and honest?
- Can the behavior be tested without excessive setup?
- Did the implementation avoid solving future imaginary requirements?

## Common Pitfalls

- Building a framework when a function would work.
- Adding configuration before there are multiple real configurations.
- Hiding business rules behind generic names.
- Keeping code because it might be useful later.
