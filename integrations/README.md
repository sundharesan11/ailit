# AI Tool Integrations

This folder documents how coding agents should use the Personal AI Engineering OS.

The main rule is simple:

```text
Use AGENTS.md as the shared project instruction file.
Use tool-native files only to bridge each tool into AGENTS.md and the AI OS runtime.
```

## Install Project Integrations

From any project:

```bash
python3 ~/engineering_brain/scripts/aios.py integrate --project .
```

This creates the shared and tool-specific instruction files that are safe to commit:

```text
AGENTS.md
CLAUDE.md
GEMINI.md
.cursor/rules/ai-os.mdc
.windsurf/rules/ai-os.md
```

Existing files are skipped by default. To deliberately recreate them:

```bash
python3 ~/engineering_brain/scripts/aios.py integrate --project . --overwrite
```

## Install For Specific Tools

```bash
python3 ~/engineering_brain/scripts/aios.py integrate --project . --tool codex
python3 ~/engineering_brain/scripts/aios.py integrate --project . --tool claude cursor
python3 ~/engineering_brain/scripts/aios.py integrate --project . --tool gemini antigravity windsurf
```

## Runtime Contract

For non-trivial engineering tasks, the agent must run this command itself:

```bash
python3 ~/engineering_brain/scripts/aios.py prepare \
  --task "<current user request>" \
  --project . \
  --tool <current-tool>
```

Then it must use the returned standards, skills, and project context while working.
The developer should not need to manually run `prepare` during normal chat-driven work.
Manual commands are mainly for setup, debugging, inspection, and verification.

If the host tool cannot run shell commands, the agent should say that the AI OS runtime
could not be executed and fall back to reading `AGENTS.md` and the project `ai/` files
directly.

Supported adapter names:

- `universal`
- `codex`
- `cursor`
- `claude`
- `gemini`
- `antigravity`
- `windsurf`

## Files

- `universal_agent_runtime.md` is the shared rule used by `AGENTS.md`.
- `codex.md` explains Codex usage.
- `claude.md` explains Claude Code usage.
- `gemini.md` explains Gemini CLI usage.
- `cursor.md` explains Cursor usage.
- `windsurf.md` explains Windsurf/Cascade usage.
- `antigravity.md` explains the conservative Antigravity setup.

## Source Notes

This integration layer uses the most stable overlap across tools:

- `AGENTS.md` for shared agent instructions.
- `CLAUDE.md` for Claude Code.
- `GEMINI.md` for Gemini CLI and Gemini-family tools.
- `.cursor/rules/*.mdc` for Cursor project rules.
- `.windsurf/rules/*.md` for Windsurf workspace rules.
