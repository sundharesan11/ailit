# Gemini CLI Integration

Gemini CLI uses `GEMINI.md` context files by default.

## Project Setup

Install Gemini integration:

```bash
aios integrate --project . --tool gemini
```

This creates:

```text
AGENTS.md
GEMINI.md
```

`GEMINI.md` imports `AGENTS.md` so Gemini CLI sees the shared runtime instructions.

## Runtime Behavior

Before non-trivial work, Gemini must run this command itself:

```bash
aios prepare \
  --task "<current user request>" \
  --project . \
  --tool gemini
```

If `aios` is not on PATH, use `python3 ~/engineering_brain/scripts/aios.py` instead.

Then Gemini must use the returned standards, skills, and project context. Do not ask
the user to run this command during normal chat-driven work.

## Notes

- Keep `GEMINI.md` small.
- Keep shared agent behavior in `AGENTS.md`.
- Use Gemini CLI memory only for concise durable facts.
