"""Prompt context assembly."""

from __future__ import annotations

from .adapters import render_for_tool
from .loader import load_skills
from .matcher import match_skills
from .project_context import load_project_context
from .standards import load_standards


def select_skill_names(task: str, limit: int) -> list[str]:
    """Select relevant skill names for a task."""
    matches = match_skills(task)
    if limit > 0:
        matches = matches[:limit]
    return [match["name"] for match in matches]


def build_context_parts(
    task: str,
    project: str | None = None,
    skill_limit: int = 5,
) -> dict[str, str | list[str]]:
    """Build structured prompt parts for an AI coding assistant."""
    skill_names = select_skill_names(task, skill_limit)
    skills_context = (
        load_skills(skill_names)
        if skill_names
        else "No matching skills found. Use the standards and project context only."
    )

    return {
        "task": task,
        "skill_names": skill_names,
        "standards": load_standards(),
        "skills": skills_context,
        "project_context": load_project_context(project),
    }


def build_context(
    task: str,
    project: str | None = None,
    skill_limit: int = 5,
    tool: str = "universal",
) -> str:
    """Build the final prompt context for an AI coding assistant."""
    context = build_context_parts(task, project, skill_limit)
    return render_for_tool(context, tool)
