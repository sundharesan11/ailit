"""Project-level AI context loading."""

from __future__ import annotations

from pathlib import Path


PROJECT_CONTEXT_FILES = (
    "spec.md",
    "design.md",
    "context.md",
    "decisions.md",
    "tasks.md",
    "lessons.md",
)


def load_project_context(project_path: str | None) -> str:
    """Load optional project ai/ context files."""
    if not project_path:
        return "No project context provided."

    project_root = Path(project_path).expanduser().resolve()
    ai_dir = project_root / "ai"
    sections: list[str] = []

    for filename in PROJECT_CONTEXT_FILES:
        path = ai_dir / filename
        if path.exists():
            sections.append(
                f"## Project File: ai/{filename}\n\n"
                f"{path.read_text(encoding='utf-8').strip()}"
            )

    if not sections:
        return f"No project context files found under {ai_dir}."

    return "\n\n---\n\n".join(sections)
