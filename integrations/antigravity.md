# Antigravity Integration

Antigravity support is kept conservative in this AI OS.

Use the same shared project files used by other coding agents:

```text
AGENTS.md
GEMINI.md
```

## Project Setup

Install Antigravity integration:

```bash
aios integrate --project . --tool antigravity
```

## Runtime Behavior

Before non-trivial work, an Antigravity agent must run this command itself:

```bash
aios prepare \
  --task "<current user request>" \
  --project . \
  --tool antigravity
```

If `aios` is not on PATH, use `python3 ~/engineering_brain/scripts/aios.py` instead.

Then it must use the returned standards, skills, and project context. Do not ask the
user to run this command during normal chat-driven work.

## Notes

- Keep cross-tool rules in `AGENTS.md`.
- Keep Gemini-family instructions in `GEMINI.md`.
- Do not rely on unverified Antigravity-specific rule features for core behavior.
- If Antigravity adds or changes native rule-file behavior, update this integration after checking official docs.
