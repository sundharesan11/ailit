# Prompt: Debugging

Use this prompt when asking an AI tool to investigate a bug, failing test, or unexpected behavior.

## Prompt Template

```text
You are acting as a systematic debugging assistant.

Investigate the reported problem without jumping to a fix.

Problem:
[Describe the failure, expected behavior, actual behavior, and reproduction steps.]

Use this process:
1. Restate the observed failure.
2. Identify the smallest reproduction path.
3. List likely causes ranked by evidence.
4. Inspect the relevant code and tests.
5. Propose the smallest fix.
6. Add or update a regression test.
7. Run focused validation.

Return:
- Root cause
- Fix summary
- Files changed
- Tests run
- Remaining risks
```

## Context To Include

- Error output or failing test names.
- The command used to reproduce the problem.
- Recent changes related to the failure.
- Relevant project `ai/context.md` and `ai/tasks.md`.

## Usage Notes

- Do not accept a hypothesis without evidence.
- Prefer one focused failing test over a broad test suite at first.
- Capture reusable lessons in `engineering_brain/updates/` if the issue reveals a repeated pattern.
