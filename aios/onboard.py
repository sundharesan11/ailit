"""One-command project onboarding."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .doctor import DoctorCheck, run_doctor
from .inspector import write_detected_context
from .integrations import install_integrations
from .project_init import init_project


@dataclass(frozen=True)
class OnboardResult:
    """Result of onboarding a project."""

    project_root: Path
    context_path: Path
    doctor_checks: list[DoctorCheck]


def onboard_project(
    project_path: str | Path,
    tools: list[str] | None = None,
    overwrite: bool = False,
) -> OnboardResult:
    """Initialize project AI context, inspect project, install integrations, and run doctor."""
    project_root = Path(project_path).expanduser().resolve()
    init_project(project_root, overwrite=False)
    context_path = write_detected_context(project_root, overwrite=overwrite)
    install_integrations(project_root, tools=tools, overwrite=overwrite)
    checks = run_doctor(project_root)
    return OnboardResult(
        project_root=project_root,
        context_path=context_path,
        doctor_checks=checks,
    )
