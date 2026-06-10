"""Shared solution loading runtime."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .paths import ROOT
from .registry import strip_frontmatter
from .solution_registry import load_solution_registry, solution_registry_by_slug


LOADABLE_TRUST_LEVELS = {"draft", "reviewed", "vendor"}
MAX_SOLUTION_CHARS = 2200


def truncate_text(text: str, limit: int = MAX_SOLUTION_CHARS) -> str:
    """Return a bounded text excerpt, closing any unbalanced code fence."""
    normalized = text.strip()
    if len(normalized) <= limit:
        return normalized
    cut = normalized[: max(limit - 4, 0)].rstrip()
    if cut.count("```") % 2 == 1:
        cut += "\n```"
    return cut + "\n..."


def load_solution_content(solution: dict[str, str], max_chars: int = MAX_SOLUTION_CHARS) -> str:
    """Load one shared solution document."""
    solution_path = ROOT / str(solution["path"])
    if not solution_path.exists():
        raise FileNotFoundError(f"Missing solution document: {solution_path}")

    raw = solution_path.read_text(encoding="utf-8")
    content = truncate_text(strip_frontmatter(raw), max_chars)
    title = solution.get("title", solution["slug"])
    summary = solution.get("summary", "")
    return (
        f"## Solution: {title}\n\n"
        f"Slug: {solution['slug']}\n"
        f"Path: {solution['path']}\n"
        f"Summary: {summary}\n\n"
        f"{content}"
    )


def load_solutions(
    solution_slugs: list[str],
    max_chars_per_solution: int = MAX_SOLUTION_CHARS,
    registry: dict[str, Any] | None = None,
) -> str:
    """Return combined Markdown context for selected solution slugs."""
    registry = registry if registry is not None else load_solution_registry()
    solutions = solution_registry_by_slug(registry)
    sections: list[str] = []
    missing: list[str] = []

    for slug in solution_slugs:
        solution = solutions.get(slug)
        if solution is None:
            missing.append(slug)
            continue
        trust = str(solution.get("trust", "draft"))
        if trust not in LOADABLE_TRUST_LEVELS:
            raise PermissionError(
                f"Solution {slug!r} has trust {trust!r} and is not loadable."
            )
        sections.append(load_solution_content(solution, max_chars_per_solution))

    if missing:
        available = ", ".join(sorted(solutions))
        raise KeyError(f"Unknown solution(s): {', '.join(missing)}. Available solutions: {available}")

    return "\n\n---\n\n".join(sections)
