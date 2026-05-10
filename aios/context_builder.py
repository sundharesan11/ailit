"""Prompt context assembly."""

from __future__ import annotations

from .adapters import render_for_tool
from .loader import load_skills
from .matcher import match_skills
from .project_context import load_project_context
from .solution_loader import load_solutions
from .solution_matcher import match_solutions
from .standards import load_standards


def select_skill_names(task: str, limit: int) -> list[str]:
    """Select relevant skill names for a task."""
    matches = match_skills(task)
    if limit > 0:
        matches = matches[:limit]
    return [match["name"] for match in matches]


def select_solution_slugs(task: str, limit: int) -> list[str]:
    """Select relevant solution slugs for a task."""
    matches = match_solutions(task)
    if limit > 0:
        matches = matches[:limit]
    return [match["slug"] for match in matches]


def build_context_parts(
    task: str,
    project: str | None = None,
    skill_limit: int = 5,
    solution_limit: int = 3,
) -> dict[str, str | list[str]]:
    """Build structured prompt parts for an AI coding assistant."""
    skill_names = select_skill_names(task, skill_limit)
    solution_slugs = select_solution_slugs(task, solution_limit)
    skills_context = (
        load_skills(skill_names)
        if skill_names
        else "No matching skills found. Use the standards and project context only."
    )
    solutions_context = (
        load_solutions(solution_slugs)
        if solution_slugs
        else "No matching reusable solutions found."
    )

    return {
        "task": task,
        "skill_names": skill_names,
        "solution_slugs": solution_slugs,
        "standards": load_standards(),
        "skills": skills_context,
        "solutions": solutions_context,
        "project_context": load_project_context(project),
    }


def build_context(
    task: str,
    project: str | None = None,
    skill_limit: int = 5,
    solution_limit: int = 3,
    tool: str = "universal",
) -> str:
    """Build the final prompt context for an AI coding assistant."""
    context = build_context_parts(task, project, skill_limit, solution_limit)
    return render_for_tool(context, tool)
