# Windsurf Integration

Windsurf Cascade supports workspace rules under `.windsurf/rules/` and can also use `AGENTS.md`.

## Project Setup

Install Windsurf integration:

```bash
aios integrate --project . --tool windsurf
```

This creates:

```text
AGENTS.md
.windsurf/rules/ai-os.md
```

## Runtime Behavior

Before non-trivial work, Cascade must run this command itself:

```bash
aios prepare \
  --task "<current user request>" \
  --project . \
  --tool windsurf
```

If `aios` is not on PATH, use `python3 ~/engineering_brain/scripts/aios.py` instead.

Then Cascade must use the returned standards, skills, and project context. Do not ask
the user to run this command during normal chat-driven work.

## Notes

- Prefer version-controlled rules or `AGENTS.md` for durable team knowledge.
- Use Windsurf memories for local one-off facts, not core project policy.
- Keep the workspace rule concise.
