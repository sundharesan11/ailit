"""Tool-specific prompt adapters."""

from __future__ import annotations

from .integrations import SUPPORTED_TOOLS


SUPPORTED_BUILD_TOOLS = ("universal", *SUPPORTED_TOOLS)


def render_universal(context: dict[str, str | list[str]]) -> str:
    """Render the default AI OS prompt format."""
    selected_skills = context["skill_names"]
    assert isinstance(selected_skills, list)
    skill_label = ", ".join(selected_skills) if selected_skills else "none"

    return f"""# SYSTEM CONTEXT

You are an AI coding assistant using the developer's Personal AI Engineering OS.
Use the provided standards, skills, and project context. Keep the final work scoped
to the user task and report validation clearly.

{context["standards"]}

# SKILLS

Selected skills: {skill_label}

{context["skills"]}

# PROJECT CONTEXT

{context["project_context"]}

# USER TASK

{context["task"]}
"""


def render_codex(context: dict[str, str | list[str]]) -> str:
    """Render context for Codex."""
    return f"""# Codex Task Context

Use this prompt as task-local guidance. Follow repository instructions first, then apply this AI OS context.

## Operating Instructions

- Inspect local files before editing.
- Keep changes scoped to the user task.
- Preserve user changes.
- Add or update tests when behavior changes.
- Run focused validation and report results.

{render_universal(context)}
"""


def render_claude(context: dict[str, str | list[str]]) -> str:
    """Render context for Claude Code."""
    return f"""# Claude Code Task Context

Use the shared project instructions from `CLAUDE.md` and `AGENTS.md`, then apply this AI OS task context.

For risky or broad work, plan first and identify the smallest useful validation path.

{render_universal(context)}
"""


def render_cursor(context: dict[str, str | list[str]]) -> str:
    """Render context for Cursor."""
    return f"""# Cursor Agent Task Context

Use `.cursor/rules/ai-os.mdc` and `AGENTS.md` as persistent project rules. Apply this task-specific AI OS context for the current request.

Prefer precise edits and focused validation.

{render_universal(context)}
"""


def render_gemini(context: dict[str, str | list[str]]) -> str:
    """Render context for Gemini CLI."""
    return f"""# Gemini CLI Task Context

Use `GEMINI.md` and `AGENTS.md` as persistent project context. Apply this task-specific AI OS context for the current request.

Use shell and file tools according to Gemini CLI confirmation policies.

{render_universal(context)}
"""


def render_antigravity(context: dict[str, str | list[str]]) -> str:
    """Render context for Antigravity."""
    return f"""# Antigravity Task Context

Use shared `AGENTS.md` guidance and `GEMINI.md` when available. Apply this AI OS context to the current agent task.

When running multiple agents, keep work isolated by module or file ownership and require human review for risky operations.

{render_universal(context)}
"""


def render_windsurf(context: dict[str, str | list[str]]) -> str:
    """Render context for Windsurf Cascade."""
    return f"""# Windsurf Cascade Task Context

Use `.windsurf/rules/ai-os.md` and `AGENTS.md` as persistent workspace rules. Apply this task-specific AI OS context for the current request.

Prefer version-controlled rules and project `ai/` files for durable knowledge.

{render_universal(context)}
"""


ADAPTERS = {
    "universal": render_universal,
    "codex": render_codex,
    "claude": render_claude,
    "cursor": render_cursor,
    "gemini": render_gemini,
    "antigravity": render_antigravity,
    "windsurf": render_windsurf,
}


def render_for_tool(context: dict[str, str | list[str]], tool: str = "universal") -> str:
    """Render prompt context for a supported tool."""
    if tool not in ADAPTERS:
        supported = ", ".join(SUPPORTED_BUILD_TOOLS)
        raise ValueError(f"Unsupported tool {tool!r}. Supported tools: {supported}")
    return ADAPTERS[tool](context)
