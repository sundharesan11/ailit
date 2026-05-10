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
from .memory import list_knowledge, promote_lesson_to_solution, write_solution_document
from .plugins import import_plugin, index_plugins
from .prepare import prepare_task
from .project_init import init_project
from .registry import index_skills, load_registry, validate_all_skills
from .solution_registry import index_solutions, load_solution_registry, validate_all_solutions
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
    results.append(run_step("index solutions", lambda: f"{index_solutions()} solution(s)"))
    results.append(
        run_step(
            "validate solutions",
            lambda: "all solutions valid" if not validate_all_solutions() else "solution errors found",
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
            if "Codex Task Context" in build_context("add retry logic", None, 1, 1, "codex")
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
        results.append(run_step("memory lesson", lambda: capture_lesson(project, "Self Test Lesson", "Situation", "Lesson").path))
        results.append(run_step("memory task", lambda: add_task(project, "Task", "Goal").path))
        results.append(
            run_step(
                "capture solution",
                lambda: write_solution_document(
                    title="Self Test Retry Solution",
                    summary="Reusable retry handling pattern from self-test.",
                    problem="Retry failures in a worker caused duplicate processing.",
                    context="Python queue worker processing",
                    root_cause="Root cause",
                    solution="Use idempotency guards with bounded retries.",
                    owner="self-test",
                    tags=["retry", "worker"],
                    stack=["python"],
                    source_refs=["ai/lessons.md"],
                ).path,
            )
        )
        results.append(
            run_step(
                "promote lesson",
                lambda: promote_lesson_to_solution(
                    project_path=project,
                    lesson_title="Self Test Lesson",
                    owner="self-test",
                    summary="Promoted from lesson.",
                    solution="Use the lesson as a reusable pattern.",
                    slug="self-test-lesson",
                ).path,
            )
        )
        results.append(
            run_step(
                "list knowledge",
                lambda: f"{len(list_knowledge(project_path=project, skills=[], solutions=[]).lessons)} lesson(s)",
            )
        )
        results.append(
            run_step(
                "prepare with solutions",
                lambda: (
                    "Selected solutions:"
                    if "Selected solutions: self-test-retry-solution" in prepare_task(
                        task="add retry logic to worker",
                        project=project,
                        tool="codex",
                        skill_limit=1,
                        solution_limit=2,
                        include_doctor=False,
                    )
                    else (_ for _ in ()).throw(ValueError("missing reusable solutions"))
                ),
            )
        )
        results.append(
            run_step(
                "prepare audit log",
                lambda: (project / "ai" / "usage.log").read_text(encoding="utf-8")
                if (project / "ai" / "usage.log").exists()
                else "missing usage.log",
            )
        )

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

    solution_dir = Path(__file__).resolve().parents[1] / "docs" / "solutions"
    solution_paths = [
        solution_dir / "_self_test_solution.md",
        solution_dir / "self-test-retry-solution.md",
        solution_dir / "self-test-lesson.md",
    ]
    solution_paths[0].write_text(
        "---\n"
        "title: Self Test Solution\n"
        "slug: _self_test_solution\n"
        "status: draft\n"
        "owner: self-test\n"
        "created: 2025-01-01\n"
        "updated: 2025-01-01\n"
        "tags:\n"
        "  - selftest\n"
        "stack:\n"
        "  - python\n"
        "summary: Temporary solution for self-test coverage.\n"
        "source_type: test\n"
        "source_refs:\n"
        "  - docs/tracking/README.md\n"
        "trust: reviewed\n"
        "review_status: reviewed\n"
        "reviewed_by: self-test-reviewer\n"
        "last_reviewed: 2026-05-11\n"
        "---\n\n"
        "# Self Test Solution\n\n"
        "## Problem\n\nTemporary.\n",
        encoding="utf-8",
    )
    try:
        results.append(
            run_step(
                "index test solution",
                lambda: next(
                    solution["slug"]
                    for solution in load_solution_registry(refresh=True).get("solutions", [])
                    if solution.get("slug") == "_self_test_solution"
                ),
            )
        )
        results.append(
            run_step(
                "stale solution detection",
                lambda: "stale"
                if next(
                    solution
                    for solution in load_solution_registry(refresh=True).get("solutions", [])
                    if solution.get("slug") == "_self_test_solution"
                ).get("is_stale", False)
                else (_ for _ in ()).throw(ValueError("expected stale solution flag")),
            )
        )
    finally:
        for path in solution_paths:
            path.unlink(missing_ok=True)

    # Remove temporary imported artifacts from global registries after tempdir cleanup.
    import shutil

    shutil.rmtree(Path(__file__).resolve().parents[1] / "skills" / "vendor" / "aios_self_test", ignore_errors=True)
    shutil.rmtree(Path(__file__).resolve().parents[1] / "plugins" / "vendor" / "aios_self_test", ignore_errors=True)
    results.append(run_step("reindex skills cleanup", lambda: f"{index_skills()} skill(s)"))
    results.append(run_step("reindex solutions cleanup", lambda: f"{index_solutions()} solution(s)"))
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
