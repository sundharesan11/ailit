"""Dependency-free self-test suite for the AI OS runtime."""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .context_builder import build_context
from .doctor import run_doctor
from .inspector import inspect_project, write_detected_context
from .integrations import install_integrations
from .loader import load_skills
from .matcher import match_skills
from .memory import add_task, capture_lesson, log_decision
from .plugins import import_plugin, index_plugins
from .project_init import init_project
from .registry import index_skills, load_registry, validate_all_skills
from .skill_importer import import_skill


@dataclass(frozen=True)
class SelfTestResult:
    """A single self-test result."""

    status: str
    name: str
    detail: str


def run_step(name: str, fn) -> SelfTestResult:
    """Run a self-test step and capture exceptions."""
    try:
        detail = fn()
        return SelfTestResult("PASS", name, str(detail or "ok"))
    except Exception as exc:  # noqa: BLE001 - self-test reports any failure
        return SelfTestResult("FAIL", name, str(exc))


def run_self_test() -> list[SelfTestResult]:
    """Run runtime smoke tests without external dependencies."""
    results: list[SelfTestResult] = []

    results.append(run_step("index skills", lambda: f"{index_skills()} skill(s)"))
    results.append(
        run_step(
            "validate skills",
            lambda: "all skills valid" if not validate_all_skills() else "skill errors found",
        )
    )
    results.append(
        run_step("match skills", lambda: match_skills("design retry strategy")[0]["name"])
    )
    results.append(run_step("load skill", lambda: load_skills(["retry_strategy"])[:40]))
    results.append(
        run_step(
            "build context",
            lambda: "Codex Task Context"
            if "Codex Task Context" in build_context("add retry logic", None, 1, "codex")
            else "missing codex adapter",
        )
    )

    with tempfile.TemporaryDirectory(prefix="aios-self-test-") as tmp:
        project = Path(tmp) / "project"
        project.mkdir()
        (project / "pyproject.toml").write_text("[project]\nname = 'demo'\n", encoding="utf-8")
        (project / "src").mkdir()
        (project / "tests").mkdir()

        results.append(run_step("init project", lambda: init_project(project).project_root))
        results.append(run_step("inspect project", lambda: inspect_project(project).languages))
        results.append(run_step("write detected context", lambda: write_detected_context(project)))
        results.append(run_step("install integrations", lambda: install_integrations(project).project_root))
        results.append(run_step("doctor", lambda: f"{len(run_doctor(project))} checks"))
        results.append(run_step("memory decision", lambda: log_decision(project, "Decision", "Context", "Decision", "Reason").path))
        results.append(run_step("memory lesson", lambda: capture_lesson(project, "Lesson", "Situation", "Lesson").path))
        results.append(run_step("memory task", lambda: add_task(project, "Task", "Goal").path))

        skill_source = Path(tmp) / "skill"
        skill_source.mkdir()
        (skill_source / "metadata.json").write_text(
            '{"name":"self_test_skill","title":"Self Test Skill","description":"Temporary skill","tags":["selftest"],"version":"0.1.0","status":"active","entrypoint":"skill.md"}',
            encoding="utf-8",
        )
        (skill_source / "skill.md").write_text("# Skill: Self Test Skill\n", encoding="utf-8")
        results.append(
            run_step(
                "import untrusted skill",
                lambda: import_skill(skill_source, provider="aios_self_test", overwrite=True).trust_level,
            )
        )

        external_root = Path(tmp) / "external_skills"
        external_skill = external_root / "external-smoke"
        external_skill.mkdir(parents=True)
        (external_skill / "SKILL.md").write_text(
            "---\n"
            "name: external-smoke\n"
            "description: Temporary external skill\n"
            "---\n\n"
            "# External Smoke\n",
            encoding="utf-8",
        )
        old_skill_sources = os.environ.get("AIOS_SKILL_SOURCES")
        os.environ["AIOS_SKILL_SOURCES"] = str(external_root)
        try:
            results.append(
                run_step(
                    "index external skills",
                    lambda: next(
                        skill["name"]
                        for skill in load_registry(refresh=True).get("skills", [])
                        if skill.get("source") == "external"
                    ),
                )
            )
            results.append(
                run_step(
                    "load external skill",
                    lambda: load_skills(["external_smoke"])[:40],
                )
            )
        finally:
            if old_skill_sources is None:
                os.environ.pop("AIOS_SKILL_SOURCES", None)
            else:
                os.environ["AIOS_SKILL_SOURCES"] = old_skill_sources

        plugin_source = Path(tmp) / "plugin"
        plugin_source.mkdir()
        (plugin_source / "plugin.json").write_text(
            '{"name":"self_test_plugin","title":"Self Test Plugin","description":"Temporary plugin","version":"0.1.0"}',
            encoding="utf-8",
        )
        results.append(
            run_step(
                "import plugin",
                lambda: import_plugin(plugin_source, provider="aios_self_test", overwrite=True).plugin_name,
            )
        )

    # Remove temporary imported artifacts from global registries after tempdir cleanup.
    import shutil

    shutil.rmtree(Path(__file__).resolve().parents[1] / "skills" / "vendor" / "aios_self_test", ignore_errors=True)
    shutil.rmtree(Path(__file__).resolve().parents[1] / "plugins" / "vendor" / "aios_self_test", ignore_errors=True)
    results.append(run_step("reindex skills cleanup", lambda: f"{index_skills()} skill(s)"))
    results.append(run_step("reindex plugins cleanup", lambda: index_plugins()))
    return results


def format_self_test(results: list[SelfTestResult]) -> str:
    """Format self-test results."""
    lines = [f"{result.status} {result.name} - {result.detail}" for result in results]
    failures = sum(1 for result in results if result.status == "FAIL")
    lines.append("")
    lines.append(f"Summary: {failures} fail, {len(results) - failures} pass")
    return "\n".join(lines)


def self_test_exit_code(results: list[SelfTestResult]) -> int:
    """Return CLI exit code for self-test results."""
    return 1 if any(result.status == "FAIL" for result in results) else 0
