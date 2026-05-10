"""Memory capture for project and global AI OS knowledge."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from .paths import ROOT, SOLUTIONS_DIR


@dataclass(frozen=True)
class MemoryWriteResult:
    """Result of writing a memory entry."""

    path: Path
    entry_title: str


@dataclass(frozen=True)
class LessonEntry:
    """A parsed lesson entry from ai/lessons.md."""

    title: str
    date: str
    situation: str
    lesson: str
    applies_to: str
    reusable_globally: bool


@dataclass(frozen=True)
class KnowledgeListResult:
    """Combined knowledge list result."""

    project_root: Path | None
    skills: list[dict[str, Any]]
    solutions: list[dict[str, Any]]
    decisions: list[str]
    lessons: list[LessonEntry]
    tasks: list[str]


def today() -> str:
    """Return today's ISO date."""
    return date.today().isoformat()


def slugify_title(title: str) -> str:
    """Return a filesystem-safe slug for a title."""
    slug = re.sub(r"[^a-zA-Z0-9_ -]+", "", title).strip().lower()
    slug = re.sub(r"[\s-]+", "-", slug)
    return slug or "update"


def parse_markdown_sections(path: Path, heading_prefix: str = "### ") -> list[tuple[str, str]]:
    """Return markdown sections split by repeated headings."""
    if not path.exists():
        return []

    sections: list[tuple[str, str]] = []
    current_heading: str | None = None
    current_lines: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(heading_prefix):
            if current_heading is not None:
                sections.append((current_heading, "\n".join(current_lines).strip()))
            current_heading = line[len(heading_prefix):].strip()
            current_lines = []
            continue
        if current_heading is not None:
            current_lines.append(line)
    if current_heading is not None:
        sections.append((current_heading, "\n".join(current_lines).strip()))
    return sections


def extract_field(block: str, label: str, default: str = "") -> str:
    """Extract a bold markdown field value from a section body."""
    pattern = re.compile(rf"^\*\*{re.escape(label)}:\*\*\s*(.*)$", re.MULTILINE)
    match = pattern.search(block)
    return match.group(1).strip() if match else default


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


def write_solution_document(
    *,
    title: str,
    summary: str,
    problem: str,
    context: str,
    root_cause: str,
    solution: str,
    owner: str,
    slug: str | None = None,
    status: str = "draft",
    tags: list[str] | None = None,
    stack: list[str] | None = None,
    source_type: str = "project",
    source_refs: list[str] | None = None,
    trust: str = "draft",
    review_status: str = "draft",
    reviewed_by: str = "",
    last_reviewed: str = "",
    tradeoffs: str = "",
    verification: str = "",
    reuse_guidance: str = "",
    do_not_reuse_when: str = "",
    follow_up: str = "",
) -> MemoryWriteResult:
    """Create or overwrite a shared solution document."""
    slug_value = slugify_title(slug or title)
    path = SOLUTIONS_DIR / f"{slug_value}.md"
    tags = tags or []
    stack = stack or []
    source_refs = source_refs or []

    def list_block(items: list[str], fallback: str) -> str:
        values = items or [fallback]
        return "\n".join(f"  - {item}" for item in values)

    content = f"""---
title: {title}
slug: {slug_value}
status: {status}
owner: {owner}
created: {today()}
updated: {today()}
tags:
{list_block(tags, "general")}
stack:
{list_block(stack, "unknown")}
summary: {summary}
source_type: {source_type}
source_refs:
{list_block(source_refs, "not-recorded")}
trust: {trust}
review_status: {review_status}
reviewed_by: {reviewed_by}
last_reviewed: {last_reviewed}
---

# {title}

## Problem

{problem}

## Context

{context}

## Root Cause

{root_cause or "Not recorded yet."}

## Solution

{solution}

## Tradeoffs

{tradeoffs or "Not recorded."}

## Verification

{verification or "Not recorded."}

## Reuse Guidance

{reuse_guidance or "Not recorded."}

## Do Not Reuse When

{do_not_reuse_when or "Not recorded."}

## Follow-Up

{follow_up or "None."}
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    return MemoryWriteResult(path=path, entry_title=title)


def load_project_lessons(project_path: str | Path) -> list[LessonEntry]:
    """Parse project lessons from ai/lessons.md."""
    path = project_ai_path(project_path, "lessons.md")
    lessons: list[LessonEntry] = []
    for heading, body in parse_markdown_sections(path):
        raw_date, _, raw_title = heading.partition(":")
        title = raw_title.strip() or heading
        lessons.append(
            LessonEntry(
                title=title,
                date=raw_date.strip(),
                situation=extract_field(body, "Situation", "Not recorded."),
                lesson=extract_field(body, "Lesson", "Not recorded."),
                applies_to=extract_field(body, "Applies To", "Project-specific."),
                reusable_globally=extract_field(body, "Reusable Globally", "No").lower().startswith("y"),
            )
        )
    return lessons


def find_project_lesson(project_path: str | Path, title: str) -> LessonEntry:
    """Find a project lesson by exact title."""
    for lesson in load_project_lessons(project_path):
        if lesson.title == title:
            return lesson
    available = ", ".join(lesson.title for lesson in load_project_lessons(project_path))
    raise KeyError(f"Lesson {title!r} not found. Available lessons: {available}")


def promote_lesson_to_solution(
    *,
    project_path: str | Path,
    lesson_title: str,
    owner: str,
    summary: str,
    solution: str,
    slug: str | None = None,
    tags: list[str] | None = None,
    stack: list[str] | None = None,
    root_cause: str = "",
    tradeoffs: str = "",
    verification: str = "",
    reuse_guidance: str = "",
    do_not_reuse_when: str = "",
    follow_up: str = "",
    trust: str = "draft",
    status: str = "draft",
    review_status: str = "draft",
    reviewed_by: str = "",
    last_reviewed: str = "",
) -> MemoryWriteResult:
    """Promote one project lesson into a shared solution document."""
    lesson = find_project_lesson(project_path, lesson_title)
    source_ref = f"ai/lessons.md#{slugify_title(lesson.date + '-' + lesson.title)}"
    return write_solution_document(
        title=lesson.title,
        slug=slug,
        owner=owner,
        summary=summary,
        problem=lesson.situation,
        context=lesson.applies_to,
        root_cause=root_cause,
        solution=solution,
        tags=tags or [],
        stack=stack or [],
        source_type="project_lesson",
        source_refs=[source_ref],
        trust=trust,
        review_status=review_status,
        reviewed_by=reviewed_by,
        last_reviewed=last_reviewed,
        status=status,
        tradeoffs=tradeoffs,
        verification=verification,
        reuse_guidance=reuse_guidance or lesson.lesson,
        do_not_reuse_when=do_not_reuse_when,
        follow_up=follow_up,
    )


def list_project_decisions(project_path: str | Path) -> list[str]:
    """Return project decision headings."""
    return [heading for heading, _ in parse_markdown_sections(project_ai_path(project_path, "decisions.md"))]


def list_project_tasks(project_path: str | Path) -> list[str]:
    """Return task titles from ai/tasks.md."""
    path = project_ai_path(project_path, "tasks.md")
    if not path.exists():
        return []
    tasks: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"- \[[ xX]\] Task:\s*(.+)$", line.strip())
        if match:
            tasks.append(match.group(1).strip())
    return tasks


def list_knowledge(
    *,
    project_path: str | Path | None,
    skills: list[dict[str, Any]],
    solutions: list[dict[str, Any]],
) -> KnowledgeListResult:
    """Return a combined knowledge view for local runtime inspection."""
    project_root = Path(project_path).expanduser().resolve() if project_path else None
    decisions: list[str] = []
    lessons: list[LessonEntry] = []
    tasks: list[str] = []

    if project_root:
        decisions = list_project_decisions(project_root)
        lessons = load_project_lessons(project_root)
        tasks = list_project_tasks(project_root)

    return KnowledgeListResult(
        project_root=project_root,
        skills=skills,
        solutions=solutions,
        decisions=decisions,
        lessons=lessons,
        tasks=tasks,
    )
