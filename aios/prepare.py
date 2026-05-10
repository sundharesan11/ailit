"""Prepare a task prompt with readiness warnings."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .adapters import render_for_tool
from .context_builder import build_context_parts
from .doctor import DoctorCheck, run_doctor


def readiness_warnings(checks: list[DoctorCheck]) -> list[str]:
    """Return warnings and failures from doctor checks."""
    return [
        f"{check.status} {check.name} - {check.detail}"
        for check in checks
        if check.status in {"WARN", "FAIL"}
    ]


def append_prepare_audit(
    project_root: Path,
    *,
    task: str,
    tool: str,
    skill_names: list[str],
    solution_slugs: list[str],
    warning_count: int,
) -> None:
    """Append a lightweight prepare audit entry under project ai/usage.log."""
    ai_dir = project_root / "ai"
    if not ai_dir.exists():
        return

    log_path = ai_dir / "usage.log"
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    task_preview = " ".join(task.strip().split())
    if len(task_preview) > 120:
        task_preview = task_preview[:117] + "..."
    skills = ",".join(skill_names) or "-"
    solutions = ",".join(solution_slugs) or "-"
    entry = (
        f"{timestamp} | command=prepare | tool={tool} | warnings={warning_count} "
        f"| skills={skills} | solutions={solutions} | task={task_preview}\n"
    )
    existing = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
    log_path.write_text(existing + entry, encoding="utf-8")


def prepare_task(
    task: str,
    project: str | Path = ".",
    tool: str = "universal",
    skill_limit: int = 5,
    solution_limit: int = 3,
    include_doctor: bool = True,
) -> str:
    """Build a task prompt with project readiness warnings."""
    project_root = Path(project).expanduser().resolve()
    checks = run_doctor(project_root) if include_doctor else []
    warnings = readiness_warnings(checks)
    context = build_context_parts(task, str(project_root), skill_limit, solution_limit)
    prompt = render_for_tool(context, tool)

    skill_names = context.get("skill_names", [])
    solution_slugs = context.get("solution_slugs", [])
    assert isinstance(skill_names, list)
    assert isinstance(solution_slugs, list)
    append_prepare_audit(
        project_root,
        task=task,
        tool=tool,
        skill_names=skill_names,
        solution_slugs=solution_slugs,
        warning_count=len(warnings),
    )

    if not warnings:
        return prompt

    warning_text = "\n".join(f"- {warning}" for warning in warnings)
    return f"""# AI OS READINESS WARNINGS

The project has readiness warnings. Use the task context, but be careful with assumptions.

{warning_text}

---

{prompt}
"""
