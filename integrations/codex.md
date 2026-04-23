# Codex Integration

Codex should use the project `AGENTS.md` file as the shared instruction entry point.

## Project Setup

Install shared project instructions:

```bash
python3 ~/engineering_brain/scripts/aios.py integrate --project . --tool codex
```

This creates:

```text
AGENTS.md
```

## Runtime Behavior

Before non-trivial work, Codex must run this command itself:

```bash
python3 ~/engineering_brain/scripts/aios.py prepare \
  --task "<current user request>" \
  --project . \
  --tool codex
```

Then Codex must use the returned standards, skills, and project context. Do not ask
the user to run this command during normal chat-driven work.

## Notes

- Keep `AGENTS.md` concise.
- Put project facts in `ai/`.
- Put reusable engineering guidance in `~/engineering_brain`.
- Use Codex approvals normally for writes and commands.
