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
from .registry import index_skills, load_registry, parse_frontmatter, registry_by_name, validate_all_skills
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


def external_frontmatter_lists_check() -> str:
    """Verify external SKILL.md list frontmatter reaches the registry."""
    skills = registry_by_name(load_registry(refresh=True))
    entry = skills["external_smoke"]
    tags = set(entry.get("tags", []))
    expected_tags = {"smoketag", "landing", "page"}
    if not expected_tags.issubset(tags):
        raise ValueError(f"missing tags: {sorted(expected_tags - tags)}")
    keywords = set(entry.get("keywords", []))
    expected_keywords = {"portfolio", "hero"}
    if not expected_keywords.issubset(keywords):
        raise ValueError(f"missing keywords: {sorted(expected_keywords - keywords)}")
    scalar = parse_frontmatter("---\nallowed-tools: Read, Write\n---\n").get("allowed-tools")
    if scalar != "Read, Write":
        raise ValueError(f"comma scalar mangled: {scalar!r}")
    return "tags and keywords captured"


def nested_frontmatter_map_check() -> str:
    """Verify nested frontmatter maps are skipped and list descriptions coerced."""
    skills = registry_by_name(load_registry(refresh=True))
    entry = skills["nested_map_smoke"]
    tags = set(entry.get("tags", []))
    if "pre" in tags or "echo" in tags:
        raise ValueError("nested map leaked into tags")
    if "nested" not in tags:
        raise ValueError("block list after nested map not captured")
    if entry.get("description") != "First line Second line":
        raise ValueError(f"description not coerced: {entry.get('description')!r}")
    return "nested map skipped"


def overlay_enrichment_check() -> str:
    """Verify overlay tags and keywords merge into both provider copies."""
    skills = registry_by_name(load_registry(refresh=True))
    entry = skills["external_smoke"]
    if "overlayterm" not in set(entry.get("tags", [])):
        raise ValueError("overlay tags not merged")
    if "overlaykey" not in set(entry.get("keywords", [])):
        raise ValueError("overlay keywords not merged")
    duplicate = next(
        (skill for name, skill in skills.items() if name.endswith("_external_smoke")),
        None,
    )
    if duplicate is None:
        raise ValueError("provider duplicate missing from registry")
    if "overlayterm" not in set(duplicate.get("tags", [])):
        raise ValueError("overlay not applied to provider duplicate")
    return "overlay merged for both provider copies"


def overlay_unmatched_check() -> str:
    """Verify unmatched overlay keys are reported in registry sources."""
    status = load_registry(refresh=True).get("skill_sources", {}).get("overlay", {})
    unmatched = status.get("unmatched_keys", [])
    if "ghost_skill" not in unmatched:
        raise ValueError(f"expected ghost_skill unmatched, got {unmatched}")
    return "unmatched overlay key reported"


def overlay_malformed_check(malformed_path: Path) -> str:
    """Verify a malformed overlay never breaks a registry build."""
    old_overlay = os.environ.get("AIOS_SKILL_OVERLAY")
    os.environ["AIOS_SKILL_OVERLAY"] = str(malformed_path)
    try:
        status = load_registry(refresh=True).get("skill_sources", {}).get("overlay", {})
        if status.get("valid", True):
            raise ValueError("malformed overlay not flagged as invalid")
    finally:
        if old_overlay is None:
            os.environ.pop("AIOS_SKILL_OVERLAY", None)
        else:
            os.environ["AIOS_SKILL_OVERLAY"] = old_overlay
    return "malformed overlay ignored safely"


def eval_portfolio_relevance_check() -> str:
    """Eval: a realistic portfolio task matches the UI fixture, not the distractor."""
    matches = match_skills(
        "build the hero section and projects grid for my personal portfolio "
        "website using Next.js and Tailwind"
    )
    names = [match["name"] for match in matches]
    if "eval_ui_craft" not in names:
        raise ValueError(f"correct skill missing from matches: {names[:5]}")
    if "eval_workflow_research" in names:
        raise ValueError("verbose-description distractor cleared the relevance threshold")
    return "correct skill matched, distractor excluded"


def eval_landing_page_check() -> str:
    """Eval: stopword filtering must not break short web tasks."""
    names = [match["name"] for match in match_skills("build a landing page")]
    if "eval_ui_craft" not in names:
        raise ValueError(f"landing page task no longer matches: {names[:5]}")
    return "landing page task still matches"


def eval_overlay_driven_check() -> str:
    """Eval: overlay terms alone can make a metadata-poor skill matchable."""
    names = [match["name"] for match in match_skills("portfolio hero section for my website")]
    if "eval_bare_design" not in names:
        raise ValueError(f"overlay-driven skill missing: {names[:5]}")
    return "overlay terms drive the match"


def eval_off_domain_check() -> str:
    """Eval: web fixtures must not match an off-domain task."""
    names = [match["name"] for match in match_skills("set up kafka consumer retries")]
    leaked = {"eval_ui_craft", "eval_bare_design"} & set(names)
    if leaked:
        raise ValueError(f"web fixtures matched an off-domain task: {sorted(leaked)}")
    return "web fixtures stay quiet off-domain"


def eval_no_match_check() -> str:
    """Eval: a nonsense task returns an empty result without raising."""
    matches = match_skills("qwzxnotaword flibberzap")
    if matches:
        raise ValueError(f"expected no matches, got {[match['name'] for match in matches]}")
    return "empty result handled"


def match_retry_strategy_check() -> str:
    """Verify the canonical retry-strategy match still works."""
    matches = match_skills("design retry strategy")
    if not matches:
        raise ValueError("no matches for 'design retry strategy'")
    return matches[0]["name"]


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
    results.append(run_step("match skills", match_retry_strategy_check))
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
            "tags:\n"
            "  - smoketag\n"
            "  - landing-page\n"
            "keywords: [portfolio, hero]\n"
            "allowed-tools: Read, Write\n"
            "---\n\n"
            "# External Smoke\n",
            encoding="utf-8",
        )
        nested_skill = external_root / "nested-map-smoke"
        nested_skill.mkdir(parents=True)
        (nested_skill / "SKILL.md").write_text(
            "---\n"
            "name: nested-map-smoke\n"
            "description:\n"
            "  - First line\n"
            "  - Second line\n"
            "hooks:\n"
            "  pre: echo hi\n"
            "  post: echo bye\n"
            "tags:\n"
            "  - nested\n"
            "---\n\n"
            "# Nested Map Smoke\n",
            encoding="utf-8",
        )
        second_root = Path(tmp) / "external_skills_dup"
        duplicate_skill = second_root / "external-smoke"
        duplicate_skill.mkdir(parents=True)
        (duplicate_skill / "SKILL.md").write_text(
            "---\n"
            "name: external-smoke\n"
            "description: Duplicate provider copy\n"
            "---\n\n"
            "# External Smoke Duplicate\n",
            encoding="utf-8",
        )
        overlay_path = Path(tmp) / "overlay.json"
        overlay_path.write_text(
            '{"skills": {"external_smoke": {"tags": ["overlayterm"], "keywords": ["overlaykey"]}, '
            '"ghost_skill": {"tags": ["ghost"]}}}',
            encoding="utf-8",
        )
        malformed_overlay_path = Path(tmp) / "overlay_malformed.json"
        malformed_overlay_path.write_text('{"skills": [', encoding="utf-8")
        old_skill_sources = os.environ.get("AIOS_SKILL_SOURCES")
        old_skill_overlay = os.environ.get("AIOS_SKILL_OVERLAY")
        os.environ["AIOS_SKILL_SOURCES"] = os.pathsep.join([str(external_root), str(second_root)])
        os.environ["AIOS_SKILL_OVERLAY"] = str(overlay_path)
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
            results.append(
                run_step(
                    "parse external list frontmatter",
                    lambda: external_frontmatter_lists_check(),
                )
            )
            results.append(
                run_step(
                    "skip nested frontmatter map",
                    lambda: nested_frontmatter_map_check(),
                )
            )
            results.append(run_step("overlay enrichment", overlay_enrichment_check))
            results.append(run_step("overlay unmatched key report", overlay_unmatched_check))
            results.append(
                run_step(
                    "overlay malformed file safety",
                    lambda: overlay_malformed_check(malformed_overlay_path),
                )
            )
        finally:
            if old_skill_sources is None:
                os.environ.pop("AIOS_SKILL_SOURCES", None)
            else:
                os.environ["AIOS_SKILL_SOURCES"] = old_skill_sources
            if old_skill_overlay is None:
                os.environ.pop("AIOS_SKILL_OVERLAY", None)
            else:
                os.environ["AIOS_SKILL_OVERLAY"] = old_skill_overlay

        # Matcher eval fixtures: a well-tagged "correct" skill, a verbose
        # trigger-list distractor shaped like installed ce-* skills, and a
        # metadata-poor skill that only the overlay makes matchable.
        # The live registry/skills.json is temporarily rewritten with this
        # fixture-only external set; it self-heals on the next refresh.
        eval_root = Path(tmp) / "match_eval_skills"
        eval_ui = eval_root / "eval-ui-craft"
        eval_ui.mkdir(parents=True)
        (eval_ui / "SKILL.md").write_text(
            "---\n"
            "name: eval-ui-craft\n"
            "description: Production-grade frontend interfaces with strong UX. For web pages, landing pages, dashboards, and UI components.\n"
            "tags:\n"
            "  - frontend\n"
            "  - website\n"
            "  - ui\n"
            "  - landing\n"
            "  - page\n"
            "  - hero\n"
            "keywords: [portfolio, tailwind, nextjs, next, js, responsive, grid, section]\n"
            "---\n\n"
            "# Eval UI Craft\n",
            encoding="utf-8",
        )
        eval_distractor = eval_root / "eval-workflow-research"
        eval_distractor.mkdir(parents=True)
        (eval_distractor / "SKILL.md").write_text(
            "---\n"
            "name: eval-workflow-research\n"
            "description: Use this when the user wants to build something, create a page, design a section, make a website update, add a grid, improve a portfolio, write a hero block, start a project, plan work, research options, debug an issue, review code, or asks for help with any personal task using common tools.\n"
            "---\n\n"
            "# Eval Workflow Research\n",
            encoding="utf-8",
        )
        eval_bare = eval_root / "eval-bare-design"
        eval_bare.mkdir(parents=True)
        (eval_bare / "SKILL.md").write_text(
            "---\n"
            "name: eval-bare-design\n"
            "description: General guidance.\n"
            "---\n\n"
            "# Eval Bare Design\n",
            encoding="utf-8",
        )
        eval_overlay_path = Path(tmp) / "match_eval_overlay.json"
        eval_overlay_path.write_text(
            '{"skills": {"eval_bare_design": {"tags": ["portfolio", "hero", "website", "section"]}}}',
            encoding="utf-8",
        )
        old_skill_sources = os.environ.get("AIOS_SKILL_SOURCES")
        old_skill_overlay = os.environ.get("AIOS_SKILL_OVERLAY")
        os.environ["AIOS_SKILL_SOURCES"] = str(eval_root)
        os.environ["AIOS_SKILL_OVERLAY"] = str(eval_overlay_path)
        try:
            results.append(run_step("eval portfolio task relevance", eval_portfolio_relevance_check))
            results.append(run_step("eval landing page stopword safety", eval_landing_page_check))
            results.append(run_step("eval overlay driven match", eval_overlay_driven_check))
            results.append(run_step("eval off-domain exclusion", eval_off_domain_check))
            results.append(run_step("eval no-match empty result", eval_no_match_check))
        finally:
            if old_skill_sources is None:
                os.environ.pop("AIOS_SKILL_SOURCES", None)
            else:
                os.environ["AIOS_SKILL_SOURCES"] = old_skill_sources
            if old_skill_overlay is None:
                os.environ.pop("AIOS_SKILL_OVERLAY", None)
            else:
                os.environ["AIOS_SKILL_OVERLAY"] = old_skill_overlay

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
