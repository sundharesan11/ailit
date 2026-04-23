"""Memory capture for project and global AI OS knowledge."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .paths import ROOT


@dataclass(frozen=True)
class MemoryWriteResult:
    """Result of writing a memory entry."""

    path: Path
    entry_title: str


def today() -> str:
    """Return today's ISO date."""
    return date.today().isoformat()


def slugify_title(title: str) -> str:
    """Return a filesystem-safe slug for a title."""
    slug = re.sub(r"[^a-zA-Z0-9_ -]+", "", title).strip().lower()
    slug = re.sub(r"[\s-]+", "-", slug)
    return slug or "update"


def append_section(path: Path, content: str) -> MemoryWriteResult:
    """Append a Markdown section to a file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    separator = "\n\n" if existing.strip() else ""
    path.write_text(existing.rstrip() + separator + content.strip() + "\n", encoding="utf-8")
    first_line = content.strip().splitlines()[0].lstrip("# ").strip()
    return MemoryWriteResult(path=path, entry_title=first_line)


def project_ai_path(project_path: str | Path, filename: str) -> Path:
    """Return a path under project/ai."""
    project_root = Path(project_path).expanduser().resolve()
    return project_root / "ai" / filename


def log_decision(
    project_path: str | Path,
    title: str,
    context: str,
    decision: str,
    reasoning: str,
    consequences: str = "",
    review_date: str = "",
) -> MemoryWriteResult:
    """Append a project decision entry."""
    entry = f"""### {today()}: {title}

**Context:** {context}

**Decision:** {decision}

**Reasoning:** {reasoning}

**Consequences:** {consequences or "Not recorded."}

**Review Date:** {review_date or "Not set."}
"""
    return append_section(project_ai_path(project_path, "decisions.md"), entry)


def capture_lesson(
    project_path: str | Path,
    title: str,
    situation: str,
    lesson: str,
    applies_to: str = "",
    reusable_globally: bool = False,
) -> MemoryWriteResult:
    """Append a project lesson entry."""
    entry = f"""### {today()}: {title}

**Situation:** {situation}

**Lesson:** {lesson}

**Applies To:** {applies_to or "Project-specific."}

**Reusable Globally:** {"Yes" if reusable_globally else "No"}
"""
    return append_section(project_ai_path(project_path, "lessons.md"), entry)


def add_task(
    project_path: str | Path,
    title: str,
    goal: str,
    context: str = "",
    validation: str = "",
    section: str = "Next",
) -> MemoryWriteResult:
    """Append a project task to ai/tasks.md."""
    entry = f"""## Added {today()} - {section}

- [ ] Task: {title}
  - Goal: {goal}
  - Context: {context or "Not recorded."}
  - Validation: {validation or "Not recorded."}
"""
    return append_section(project_ai_path(project_path, "tasks.md"), entry)


def capture_global_update(
    title: str,
    context: str,
    change: str,
    reason: str,
    follow_up: str = "",
) -> MemoryWriteResult:
    """Create a reusable global update entry under engineering_brain/updates."""
    filename = f"{today()}-{slugify_title(title)}.md"
    path = ROOT / "updates" / filename
    entry = f"""# {today()}: {title}

## Context

{context}

## Change

{change}

## Reason

{reason}

## Follow-Up

{follow_up or "None."}
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(entry.strip() + "\n", encoding="utf-8")
    return MemoryWriteResult(path=path, entry_title=f"{today()}: {title}")
