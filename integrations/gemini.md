# Gemini CLI Integration

Gemini CLI uses `GEMINI.md` context files by default.

## Project Setup

Install Gemini integration:

```bash
python3 ~/engineering_brain/scripts/aios.py integrate --project . --tool gemini
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
python3 ~/engineering_brain/scripts/aios.py prepare \
  --task "<current user request>" \
  --project . \
  --tool gemini
```

Then Gemini must use the returned standards, skills, and project context. Do not ask
the user to run this command during normal chat-driven work.

## Notes

- Keep `GEMINI.md` small.
- Keep shared agent behavior in `AGENTS.md`.
- Use Gemini CLI memory only for concise durable facts.
