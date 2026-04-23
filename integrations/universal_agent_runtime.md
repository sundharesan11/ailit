# Universal Agent Runtime

Use this instruction set for any coding agent that can read project instructions and run shell commands.

## Agent Runtime Contract

Before non-trivial engineering work, the agent must run:

```bash
python3 ~/engineering_brain/scripts/aios.py prepare \
  --task "<current user request>" \
  --project . \
  --tool <current-tool>
```

Read the output before editing files.

Do not ask the user to run this command or paste the output during normal work. The
agent should execute it with the available shell/tool interface. If the host tool cannot
run shell commands, say that the AI OS runtime could not be executed and continue by
reading `AGENTS.md` and the project `ai/` files directly.

Use the tool name when known: `codex`, `cursor`, `claude`, `gemini`, `antigravity`, or `windsurf`.
If unknown, omit `--tool` to use the universal format.

## Use The Returned Context

The context builder may return:

- engineering standards from `~/engineering_brain/standards/`
- matched skills from `~/engineering_brain/skills/`
- project files from `ai/`
- the original task

Use project-specific context over generic assumptions.

## When To Skip Runtime Loading

You may skip runtime loading for:

- tiny factual questions
- direct requests to inspect one file
- tasks where the user explicitly asks not to use tools

For implementation, debugging, refactoring, architecture, review, or test work, use the runtime.

## Working Rules

- Inspect local files before making claims.
- Keep changes scoped to the request.
- Preserve user changes.
- Add or update tests when behavior changes.
- Run focused validation.
- Report validation clearly.
- Ask before persisting new long-term memory unless the user requested it.

## Memory Loop

At the end of meaningful work, decide whether a lesson should be saved:

- project-specific knowledge -> project `ai/`
- reusable engineering knowledge -> `~/engineering_brain/updates/` or a global skill
