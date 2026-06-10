"""Prompt context assembly."""

from __future__ import annotations

from typing import Any

from .adapters import render_for_tool
from .loader import MAX_SKILL_CHARS, load_skills
from .matcher import match_skills
from .project_context import load_project_context
from .registry import load_registry
from .solution_loader import load_solutions
from .solution_matcher import match_solutions
from .solution_registry import load_solution_registry
from .standards import load_standards


# Only the top-scoring matches are inlined in full; remaining matches above
# the relevance threshold become one-line pointers the agent can load on
# demand with `aios load <name>`.
INLINE_SKILL_CAP = 2
POINTER_DESCRIPTION_CHARS = 140


def select_skill_names(task: str, limit: int) -> list[str]:
    """Select relevant skill names for a task."""
    return [match["name"] for match in select_skill_matches(task, limit)]


def select_skill_matches(
    task: str,
    limit: int,
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Select relevant skill matches for a task, bounded by limit."""
    matches = match_skills(task, registry)
    if limit > 0:
        matches = matches[:limit]
    return matches


def select_solution_slugs(
    task: str,
    limit: int,
    registry: dict[str, Any] | None = None,
) -> list[str]:
    """Select relevant solution slugs for a task."""
    matches = match_solutions(task, registry)
    if limit > 0:
        matches = matches[:limit]
    return [match["slug"] for match in matches]


def skill_pointer_line(match: dict[str, Any]) -> str:
    """Return a one-line load-on-demand pointer for a matched skill."""
    description = " ".join(str(match.get("description", "")).split())
    if len(description) > POINTER_DESCRIPTION_CHARS:
        description = description[: POINTER_DESCRIPTION_CHARS - 3].rstrip() + "..."
    return f"- {match['name']}: {description} (load with: aios load {match['name']})"


def build_context_parts(
    task: str,
    project: str | None = None,
    skill_limit: int = 5,
    solution_limit: int = 3,
) -> dict[str, str | list[str]]:
    """Build structured prompt parts for an AI coding assistant.

    Pipeline: relevance threshold (inside match_skills) -> truncate to
    skill_limit (0 = unlimited) -> inline the first INLINE_SKILL_CAP in
    full (capped at MAX_SKILL_CHARS each) -> pointer lines for the rest.
    """
    registry = load_registry()
    solution_registry = load_solution_registry()

    matches = select_skill_matches(task, skill_limit, registry)
    inline_cap = INLINE_SKILL_CAP if skill_limit <= 0 else min(INLINE_SKILL_CAP, skill_limit)
    inline_matches = matches[:inline_cap]
    pointer_matches = matches[inline_cap:]
    inline_names = [match["name"] for match in inline_matches]
    pointer_names = [match["name"] for match in pointer_matches]

    solution_slugs = select_solution_slugs(task, solution_limit, solution_registry)

    if inline_names:
        skills_context = load_skills(inline_names, MAX_SKILL_CHARS, registry)
        if pointer_matches:
            pointer_lines = "\n".join(skill_pointer_line(match) for match in pointer_matches)
            skills_context += (
                "\n\n### More relevant skills (load on demand)\n\n" + pointer_lines
            )
    else:
        skills_context = "No matching skills found. Use the standards and project context only."

    solutions_context = (
        load_solutions(solution_slugs, registry=solution_registry)
        if solution_slugs
        else "No matching reusable solutions found."
    )

    return {
        "task": task,
        "skill_names": inline_names + pointer_names,
        "inline_skill_names": inline_names,
        "pointer_skill_names": pointer_names,
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
