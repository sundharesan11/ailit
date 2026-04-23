"""Project health checks for AI OS readiness."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .context_builder import build_context
from .paths import PLUGIN_REGISTRY_PATH, PROVIDER_REGISTRY_PATH, REGISTRY_PATH
from .project_init import PROJECT_TEMPLATES
from .registry import validate_all_skills


@dataclass(frozen=True)
class DoctorCheck:
    """A single doctor check result."""

    status: str
    name: str
    detail: str


PROJECT_AI_FILES = (
    "spec.md",
    "design.md",
    "context.md",
    "decisions.md",
    "tasks.md",
    "lessons.md",
)


def is_template_like(path: Path) -> bool:
    """Return whether a project AI file still looks mostly like a template."""
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8", errors="ignore")
    template = PROJECT_TEMPLATES.get(path.name, "")
    if template and text.strip() == template.strip():
        return True
    markers = (
        "Describe the product",
        "Workflow 1:",
        "Language:",
        "Things agents should always do:",
        "YYYY-MM-DD: Decision Title",
    )
    return any(marker in text for marker in markers)


def run_doctor(project_path: str | Path) -> list[DoctorCheck]:
    """Run AI OS readiness checks for a project."""
    root = Path(project_path).expanduser().resolve()
    checks: list[DoctorCheck] = []

    ai_dir = root / "ai"
    checks.append(
        DoctorCheck("PASS" if ai_dir.exists() else "FAIL", "project ai/ directory", str(ai_dir))
    )
    for filename in PROJECT_AI_FILES:
        path = ai_dir / filename
        if path.exists():
            status = "WARN" if is_template_like(path) else "PASS"
            detail = "exists but still looks template-like" if status == "WARN" else "exists"
        else:
            status = "FAIL"
            detail = "missing"
        checks.append(DoctorCheck(status, f"ai/{filename}", detail))

    agents_path = root / "AGENTS.md"
    if agents_path.exists():
        agents_text = agents_path.read_text(encoding="utf-8", errors="ignore")
        if "aios.py prepare" in agents_text:
            checks.append(DoctorCheck("PASS", "AGENTS.md", "exists with AI OS runtime contract"))
        else:
            checks.append(DoctorCheck("WARN", "AGENTS.md", "exists but does not mention aios.py prepare"))
    else:
        checks.append(DoctorCheck("WARN", "AGENTS.md", "missing"))

    tool_files = (
        "CLAUDE.md",
        "GEMINI.md",
        ".cursor/rules/ai-os.mdc",
        ".windsurf/rules/ai-os.md",
    )
    for relative in tool_files:
        path = root / relative
        checks.append(
            DoctorCheck(
                "PASS" if path.exists() else "WARN",
                relative,
                "exists" if path.exists() else "missing",
            )
        )

    for path, name in (
        (REGISTRY_PATH, "registry/skills.json"),
        (PLUGIN_REGISTRY_PATH, "registry/plugins.json"),
        (PROVIDER_REGISTRY_PATH, "registry/providers.json"),
    ):
        checks.append(DoctorCheck("PASS" if path.exists() else "FAIL", name, str(path)))

    skill_errors = validate_all_skills()
    checks.append(
        DoctorCheck(
            "PASS" if not skill_errors else "FAIL",
            "skill validation",
            "all skills valid" if not skill_errors else f"{len(skill_errors)} skill(s) invalid",
        )
    )

    try:
        build_context("doctor smoke test", str(root), 1, "universal")
        checks.append(DoctorCheck("PASS", "context builder", "smoke test passed"))
    except Exception as exc:  # noqa: BLE001 - doctor reports any failure
        checks.append(DoctorCheck("FAIL", "context builder", str(exc)))

    return checks


def format_doctor(checks: list[DoctorCheck]) -> str:
    """Format doctor checks for CLI output."""
    lines = []
    for check in checks:
        lines.append(f"{check.status} {check.name} - {check.detail}")
    failures = sum(1 for check in checks if check.status == "FAIL")
    warnings = sum(1 for check in checks if check.status == "WARN")
    lines.append("")
    lines.append(f"Summary: {failures} fail, {warnings} warn, {len(checks) - failures - warnings} pass")
    return "\n".join(lines)


def doctor_exit_code(checks: list[DoctorCheck]) -> int:
    """Return CLI exit code for doctor checks."""
    return 1 if any(check.status == "FAIL" for check in checks) else 0
