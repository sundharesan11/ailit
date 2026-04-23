# Cursor Integration

Cursor supports project rules under `.cursor/rules/`.

## Project Setup

Install Cursor integration:

```bash
python3 ~/engineering_brain/scripts/aios.py integrate --project . --tool cursor
```

This creates:

```text
AGENTS.md
.cursor/rules/ai-os.mdc
```

## Runtime Behavior

Before non-trivial work, Cursor Agent must run this command itself:

```bash
python3 ~/engineering_brain/scripts/aios.py prepare \
  --task "<current user request>" \
  --project . \
  --tool cursor
```

Then Cursor must use the returned standards, skills, and project context. Do not ask
the user to run this command during normal chat-driven work.

## Notes

- Keep broad shared behavior in `AGENTS.md`.
- Use `.cursor/rules/` for Cursor-specific activation behavior.
- Keep rules concise so they do not crowd the model context.
