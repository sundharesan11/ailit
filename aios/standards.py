"""Engineering standards loading."""

from __future__ import annotations

from pathlib import Path

from .matcher import request_tokens_for
from .paths import STANDARDS_DIR
from .registry import frontmatter_terms, parse_frontmatter, strip_frontmatter


# Standards that load for every task regardless of relevance, so the
# output never contains zero standards.
ALWAYS_ON_STANDARDS = ("simplicity",)


def standard_matches_task(task_tokens: set[str], raw_text: str) -> bool:
    """Return whether a standard's frontmatter tags match the task.

    frontmatter_terms accepts block lists, flow lists, and comma scalars,
    so all tag spellings behave the same as skill and overlay tags.
    """
    frontmatter = parse_frontmatter(raw_text)
    return bool(task_tokens & set(frontmatter_terms(frontmatter, "tags")))


def standard_section(path: Path, raw_text: str) -> str:
    """Render one standard as a context section without frontmatter."""
    return (
        f"## Standard: {path.stem}\n\nSource: standards/{path.name}\n\n"
        f"{strip_frontmatter(raw_text).strip()}"
    )


def load_standards(
    task: str | None = None,
    recommended: list[str] | None = None,
) -> str:
    """Load engineering standards as Markdown context.

    Without a task, all standards load (back-compat for direct callers).
    With a task, the always-on baseline loads plus standards whose
    frontmatter tags match the task or that selected skills recommend.
    """
    task_tokens = request_tokens_for(task) if task else set()
    recommended_names = set(recommended or [])
    sections: list[str] = []
    for path in sorted(STANDARDS_DIR.glob("*.md")):
        raw_text = path.read_text(encoding="utf-8")
        include = (
            task is None
            or path.stem in ALWAYS_ON_STANDARDS
            or path.stem in recommended_names
            or standard_matches_task(task_tokens, raw_text)
        )
        if include:
            sections.append(standard_section(path, raw_text))
    return "\n\n---\n\n".join(sections)
