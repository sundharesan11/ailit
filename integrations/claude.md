# Claude Code Integration

Claude Code uses `CLAUDE.md` for persistent project instructions.

## Project Setup

Install Claude integration:

```bash
python3 ~/engineering_brain/scripts/aios.py integrate --project . --tool claude
```

This creates:

```text
AGENTS.md
CLAUDE.md
```

`CLAUDE.md` imports `AGENTS.md`, so shared rules stay in one place.

## Runtime Behavior

Before non-trivial work, Claude must run this command itself:

```bash
python3 ~/engineering_brain/scripts/aios.py prepare \
  --task "<current user request>" \
  --project . \
  --tool claude
```

Then Claude must use the returned standards, skills, and project context. Do not ask
the user to run this command during normal chat-driven work.

## Notes

- Keep Claude-only guidance in `CLAUDE.md`.
- Keep cross-tool guidance in `AGENTS.md`.
- Use project `ai/` files for architecture, commands, decisions, and lessons.
