# Cursor Integration

Cursor supports project rules under `.cursor/rules/`.

## Project Setup

Install Cursor integration:

```bash
aios integrate --project . --tool cursor
```

This creates:

```text
AGENTS.md
.cursor/rules/ai-os.mdc
```

## Runtime Behavior

Before non-trivial work, Cursor Agent must run this command itself:

```bash
aios prepare \
  --task "<current user request>" \
  --project . \
  --tool cursor
```

If `aios` is not on PATH, use `python3 ~/engineering_brain/scripts/aios.py` instead.

Then Cursor must use the returned standards, skills, and project context. Do not ask
the user to run this command during normal chat-driven work.

## Notes

- Keep broad shared behavior in `AGENTS.md`.
- Use `.cursor/rules/` for Cursor-specific activation behavior.
- Keep rules concise so they do not crowd the model context.
