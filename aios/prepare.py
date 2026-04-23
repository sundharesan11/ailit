"""Prepare a task prompt with readiness warnings."""

from __future__ import annotations

from pathlib import Path

from .context_builder import build_context
from .doctor import DoctorCheck, run_doctor


def readiness_warnings(checks: list[DoctorCheck]) -> list[str]:
    """Return warnings and failures from doctor checks."""
    return [
        f"{check.status} {check.name} - {check.detail}"
        for check in checks
        if check.status in {"WARN", "FAIL"}
    ]


def prepare_task(
    task: str,
    project: str | Path = ".",
    tool: str = "universal",
    skill_limit: int = 5,
    include_doctor: bool = True,
) -> str:
    """Build a task prompt with project readiness warnings."""
    project_root = Path(project).expanduser().resolve()
    checks = run_doctor(project_root) if include_doctor else []
    warnings = readiness_warnings(checks)
    prompt = build_context(task, str(project_root), skill_limit, tool)

    if not warnings:
        return prompt

    warning_text = "\n".join(f"- {warning}" for warning in warnings)
    return f"""# AI OS READINESS WARNINGS

The project has readiness warnings. Use the task context, but be careful with assumptions.

{warning_text}

---

{prompt}
"""
