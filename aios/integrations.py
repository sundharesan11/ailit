"""Generate project integration files for AI coding tools."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


SUPPORTED_TOOLS = (
    "codex",
    "cursor",
    "claude",
    "gemini",
    "antigravity",
    "windsurf",
)


UNIVERSAL_AGENT_RUNTIME = """# AGENTS.md

This repository uses the user's Personal AI Engineering OS.

## Agent Runtime Contract

Before non-trivial software engineering work, the agent must run the local AI OS task
preparation command itself:

```bash
python3 ~/engineering_brain/scripts/aios.py prepare \\
  --task "<current user request>" \\
  --project . \\
  --tool <current-tool>
```

Use the tool name when known: `codex`, `cursor`, `claude`, `gemini`, `antigravity`, or `windsurf`.
If the tool is unknown, omit `--tool` to use the universal format.

Do not ask the user to run this command or paste its output during normal work. Run it
with the available shell/tool interface, read the returned context, and then proceed.
If command execution is unavailable in the current host tool, say that the AI OS runtime
could not be executed and continue by reading `AGENTS.md` and the project `ai/` files
directly.

Use the returned context as working guidance. It may include:

- global engineering standards
- matched engineering skills
- project `ai/` context files
- the original user task

## When The Agent Must Use The Runtime

Use the runtime for:

- implementation tasks
- debugging
- refactoring
- architecture/design work
- code review
- test planning
- any change that touches project behavior

For very small factual questions, answer directly after inspecting the relevant local files.

## Project Context

If the `ai/` folder exists, prefer it over assumptions:

- `ai/spec.md`
- `ai/design.md`
- `ai/context.md`
- `ai/decisions.md`
- `ai/tasks.md`
- `ai/lessons.md`

If the `ai/` folder is missing and the task is substantial, suggest:

```bash
python3 ~/engineering_brain/scripts/aios.py init-project --project .
```

Do not overwrite existing project context unless the user explicitly asks.

## Working Rules

- Inspect local files before making implementation claims.
- Keep changes scoped to the user request.
- Use project conventions over generic advice.
- Add or update tests when behavior changes.
- Run the narrowest useful validation first.
- Report commands run and any validation that could not be completed.
- Never discard user changes unless explicitly asked.

## Memory Loop

After a meaningful task, identify whether anything should be saved:

- project-specific fact or decision -> `ai/decisions.md`, `ai/context.md`, or `ai/lessons.md`
- reusable engineering lesson -> `~/engineering_brain/updates/` or a global skill

Ask before writing durable memory unless the user requested it.
"""


CLAUDE_MD = """@AGENTS.md

## Claude Code

Use the shared AI OS runtime instructions from `AGENTS.md`. For non-trivial work, Claude
must run the `prepare` command itself before editing. Do not ask the user to run it.

For large or risky changes, start by planning and identifying the smallest safe validation path.
Keep this file Claude-specific; shared rules belong in `AGENTS.md`.
"""


GEMINI_MD = """@AGENTS.md

## Gemini CLI / Antigravity

Use the shared AI OS runtime instructions from `AGENTS.md`.

When shell access is available, the agent must run the cross-project wrapper itself:

```bash
python3 ~/engineering_brain/scripts/aios.py prepare --task "<current user request>" --project . --tool gemini
```

Do not ask the user to run the command during normal task work.
Keep this file tool-specific; shared rules belong in `AGENTS.md`.
"""


CURSOR_RULE = """---
description: Use the user's Personal AI Engineering OS runtime before engineering work.
alwaysApply: true
---

# Personal AI Engineering OS

This project uses the shared instructions in `AGENTS.md`.

Before non-trivial implementation, debugging, refactoring, architecture, or review work,
Cursor Agent must run this command itself:

```bash
python3 ~/engineering_brain/scripts/aios.py prepare --task "<current user request>" --project . --tool cursor
```

Do not ask the user to run it. Use the returned standards, skills, and project context
while working.

Keep edits scoped, preserve user changes, and report validation clearly.
"""


WINDSURF_RULE = """---
trigger: always_on
description: Use the user's Personal AI Engineering OS runtime before engineering work.
---

# Personal AI Engineering OS

This project uses the shared instructions in `AGENTS.md`.

Before non-trivial implementation, debugging, refactoring, architecture, or review work,
Cascade must run this command itself:

```bash
python3 ~/engineering_brain/scripts/aios.py prepare --task "<current user request>" --project . --tool windsurf
```

Do not ask the user to run it. Use the returned standards, skills, and project context
while working.

Keep edits scoped, preserve user changes, and report validation clearly.
"""


TOOL_FILES: dict[str, dict[str, str]] = {
    "codex": {
        "AGENTS.md": UNIVERSAL_AGENT_RUNTIME,
    },
    "cursor": {
        "AGENTS.md": UNIVERSAL_AGENT_RUNTIME,
        ".cursor/rules/ai-os.mdc": CURSOR_RULE,
    },
    "claude": {
        "AGENTS.md": UNIVERSAL_AGENT_RUNTIME,
        "CLAUDE.md": CLAUDE_MD,
    },
    "gemini": {
        "AGENTS.md": UNIVERSAL_AGENT_RUNTIME,
        "GEMINI.md": GEMINI_MD,
    },
    "antigravity": {
        "AGENTS.md": UNIVERSAL_AGENT_RUNTIME,
        "GEMINI.md": GEMINI_MD,
    },
    "windsurf": {
        "AGENTS.md": UNIVERSAL_AGENT_RUNTIME,
        ".windsurf/rules/ai-os.md": WINDSURF_RULE,
    },
}


@dataclass(frozen=True)
class IntegrationResult:
    """Result of writing integration files."""

    project_root: Path
    tools: list[str]
    created: list[Path]
    skipped: list[Path]
    overwritten: list[Path]


def normalize_tools(tools: list[str] | None) -> list[str]:
    """Normalize requested tools into a unique ordered list."""
    if not tools or "all" in tools:
        return list(SUPPORTED_TOOLS)

    normalized: list[str] = []
    for tool in tools:
        if tool not in SUPPORTED_TOOLS:
            supported = ", ".join(SUPPORTED_TOOLS)
            raise ValueError(f"Unsupported tool {tool!r}. Supported tools: {supported}")
        if tool not in normalized:
            normalized.append(tool)
    return normalized


def integration_files_for_tools(tools: list[str]) -> dict[str, str]:
    """Return files needed for selected tools."""
    files: dict[str, str] = {}
    for tool in tools:
        for path, content in TOOL_FILES[tool].items():
            files.setdefault(path, content)
    return files


def install_integrations(
    project_path: str | Path,
    tools: list[str] | None = None,
    overwrite: bool = False,
) -> IntegrationResult:
    """Install AI tool integration files into a project."""
    project_root = Path(project_path).expanduser().resolve()
    selected_tools = normalize_tools(tools)
    files = integration_files_for_tools(selected_tools)

    created: list[Path] = []
    skipped: list[Path] = []
    overwritten: list[Path] = []

    for relative_path, content in sorted(files.items()):
        path = project_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists() and not overwrite:
            skipped.append(path)
            continue

        if path.exists() and overwrite:
            overwritten.append(path)
        else:
            created.append(path)

        path.write_text(content.strip() + "\n", encoding="utf-8")

    return IntegrationResult(
        project_root=project_root,
        tools=selected_tools,
        created=created,
        skipped=skipped,
        overwritten=overwritten,
    )
