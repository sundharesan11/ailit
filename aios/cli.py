"""Command line interface for the Personal AI Engineering OS."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .adapters import SUPPORTED_BUILD_TOOLS
from .context_builder import build_context
from .doctor import doctor_exit_code, format_doctor, run_doctor
from .integrations import SUPPORTED_TOOLS, install_integrations
from .inspector import inspect_project, inspection_to_markdown, write_detected_context
from .loader import load_skills
from .matcher import match_skills
from .memory import (
    add_task,
    capture_global_update,
    capture_lesson,
    list_knowledge,
    log_decision,
    promote_lesson_to_solution,
    write_solution_document,
)
from .onboard import onboard_project
from .paths import ROOT
from .plugins import (
    import_plugin,
    index_plugins,
    load_plugin_registry,
    load_provider_registry,
    update_plugin_trust,
)
from .project_init import init_project
from .registry import (
    external_skill_source_statuses,
    index_skills,
    load_registry,
    skill_dirs,
    validate_all_skills,
    validate_skill,
)
from .solution_registry import (
    index_solutions,
    load_solution_registry,
    solution_doc_paths,
    validate_all_solutions,
    validate_solution,
)
from .prepare import prepare_task
from .self_test import format_self_test, run_self_test, self_test_exit_code
from .skill_importer import TRUST_LEVELS, import_skill, update_skill_trust


def print_match(args: argparse.Namespace) -> int:
    """Handle the match command."""
    matches = match_skills(args.request)
    if args.limit > 0:
        matches = matches[: args.limit]
    print(json.dumps(matches, indent=2, ensure_ascii=False))
    return 0


def print_load(args: argparse.Namespace) -> int:
    """Handle the load command."""
    print(load_skills(args.skill_names))
    return 0


def print_build(args: argparse.Namespace) -> int:
    """Handle the build command."""
    print(build_context(args.task, args.project, args.skill_limit, args.solution_limit, args.tool))
    return 0


def print_index(_: argparse.Namespace) -> int:
    """Handle the index command."""
    count = index_skills()
    print(f"Indexed {count} skill(s) into registry/skills.json")
    return 0


def print_index_solutions(_: argparse.Namespace) -> int:
    """Handle the index-solutions command."""
    count = index_solutions()
    print(f"Indexed {count} solution(s) into registry/solutions.json")
    return 0


def print_list_skills(args: argparse.Namespace) -> int:
    """Handle the list-skills command."""
    registry = load_registry()
    skills = registry.get("skills", [])

    if args.source != "all":
        skills = [skill for skill in skills if skill.get("source", "local") == args.source]

    if args.query:
        query = args.query.lower()
        skills = [
            skill
            for skill in skills
            if query in str(skill.get("name", "")).lower()
            or query in str(skill.get("title", "")).lower()
            or query in str(skill.get("description", "")).lower()
            or query in str(skill.get("path", "")).lower()
        ]

    if args.json:
        print(json.dumps(skills, indent=2, ensure_ascii=False))
        return 0

    if not skills:
        print("No skills matched.")
        return 0

    for skill in skills:
        print(
            f"{skill['name']} | source={skill.get('source', 'local')} "
            f"| provider={skill.get('provider', 'local')} "
            f"| trust={skill.get('trust_level', skill.get('status', 'unknown'))} "
            f"| path={skill.get('path', '')}"
        )
    return 0


def print_list_solutions(args: argparse.Namespace) -> int:
    """Handle the list-solutions command."""
    registry = load_solution_registry()
    solutions = registry.get("solutions", [])

    if args.status != "all":
        solutions = [item for item in solutions if item.get("status", "draft") == args.status]

    if args.trust != "all":
        solutions = [item for item in solutions if item.get("trust", "draft") == args.trust]

    if args.review_status != "all":
        solutions = [item for item in solutions if item.get("review_status", "draft") == args.review_status]

    if args.stale != "all":
        want_stale = args.stale == "only"
        solutions = [item for item in solutions if bool(item.get("is_stale", False)) is want_stale]

    if args.query:
        query = args.query.lower()
        solutions = [
            item
            for item in solutions
            if query in str(item.get("slug", "")).lower()
            or query in str(item.get("title", "")).lower()
            or query in str(item.get("summary", "")).lower()
            or query in str(item.get("path", "")).lower()
            or any(query in str(tag).lower() for tag in item.get("tags", []))
            or any(query in str(tag).lower() for tag in item.get("stack", []))
        ]

    if args.json:
        print(json.dumps(solutions, indent=2, ensure_ascii=False))
        return 0

    if not solutions:
        print("No solutions matched.")
        return 0

    for solution in solutions:
        print(
            f"{solution['slug']} | status={solution.get('status', 'draft')} "
            f"| trust={solution.get('trust', 'draft')} "
            f"| review={solution.get('review_status', 'draft')} "
            f"| stale={'yes' if solution.get('is_stale', False) else 'no'} "
            f"| owner={solution.get('owner', '')} "
            f"| path={solution.get('path', '')}"
        )
    return 0


def print_list_skill_sources(args: argparse.Namespace) -> int:
    """Handle the list-skill-sources command."""
    sources = external_skill_source_statuses()
    if args.json:
        print(json.dumps(sources, indent=2, ensure_ascii=False))
        return 0

    print(
        f"local | exists=yes | skill_count={len(skill_dirs())} "
        f"| path={ROOT / 'skills'}"
    )
    for source in sources:
        exists = "yes" if source["exists"] else "no"
        print(
            f"{source['label']} | exists={exists} | skill_count={source['skill_count']} "
            f"| path={source['display_path']}"
        )

    overlay = load_registry().get("skill_sources", {}).get("overlay") or {}
    if overlay:
        exists = "yes" if overlay.get("exists") else "no"
        valid = "yes" if overlay.get("valid", True) else "no"
        unmatched = ",".join(overlay.get("unmatched_keys", [])) or "none"
        print(
            f"overlay | exists={exists} | valid={valid} "
            f"| entries={overlay.get('entry_count', 0)} | unmatched={unmatched} "
            f"| path={overlay.get('display_path', '')}"
        )
    return 0


def print_validate(args: argparse.Namespace) -> int:
    """Handle the validate command."""
    if args.all or not args.skill_path:
        errors_by_path = validate_all_skills()
        if errors_by_path:
            print("Skill validation failed:")
            for path, errors in errors_by_path.items():
                print(f"- {path}")
                for error in errors:
                    print(f"  - {error}")
            return 1

        print(f"Skill validation passed: {len(skill_dirs())} skill(s)")
        return 0

    skill_path = Path(args.skill_path)
    if not skill_path.is_absolute():
        skill_path = ROOT / skill_path

    errors = validate_skill(skill_path)
    if errors:
        print("Skill validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    try:
        display_path = skill_path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        display_path = str(skill_path)
    print(f"Skill validation passed: {display_path}")
    return 0


def print_validate_solutions(args: argparse.Namespace) -> int:
    """Handle the validate-solutions command."""
    if args.all or not args.solution_path:
        errors_by_path = validate_all_solutions()
        if errors_by_path:
            print("Solution validation failed:")
            for path, errors in errors_by_path.items():
                print(f"- {path}")
                for error in errors:
                    print(f"  - {error}")
            return 1

        print(f"Solution validation passed: {len(solution_doc_paths())} solution(s)")
        return 0

    solution_path = Path(args.solution_path)
    if not solution_path.is_absolute():
        solution_path = ROOT / solution_path

    errors = validate_solution(solution_path)
    if errors:
        print("Solution validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    try:
        display_path = solution_path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        display_path = str(solution_path)
    print(f"Solution validation passed: {display_path}")
    return 0


def print_capture_solution(args: argparse.Namespace) -> int:
    """Handle the capture-solution command."""
    source_refs = list(args.source_ref or [])
    if args.project:
        project_root = Path(args.project).expanduser().resolve()
        relative_project = project_root.name if project_root.name else "."
        source_refs.append(f"{relative_project}/ai/lessons.md")

    result = write_solution_document(
        title=args.title,
        slug=args.slug,
        summary=args.summary,
        problem=args.problem,
        context=args.context,
        root_cause=args.root_cause,
        solution=args.solution,
        owner=args.owner,
        status=args.status,
        trust=args.trust,
        tags=args.tag or [],
        stack=args.stack or [],
        source_type=args.source_type,
        source_refs=source_refs,
        tradeoffs=args.tradeoffs,
        verification=args.verification,
        reuse_guidance=args.reuse_guidance,
        do_not_reuse_when=args.do_not_reuse_when,
        follow_up=args.follow_up,
        review_status=args.review_status,
        reviewed_by=args.reviewed_by,
        last_reviewed=args.last_reviewed,
    )
    count = index_solutions()
    print(f"Captured solution: {result.entry_title}")
    print(f"Path: {result.path}")
    print(f"Solution registry count: {count}")
    return 0


def print_promote_lesson(args: argparse.Namespace) -> int:
    """Handle the promote-lesson command."""
    result = promote_lesson_to_solution(
        project_path=args.project,
        lesson_title=args.title,
        owner=args.owner,
        summary=args.summary,
        solution=args.solution,
        slug=args.slug,
        tags=args.tag or [],
        stack=args.stack or [],
        root_cause=args.root_cause,
        tradeoffs=args.tradeoffs,
        verification=args.verification,
        reuse_guidance=args.reuse_guidance,
        do_not_reuse_when=args.do_not_reuse_when,
        follow_up=args.follow_up,
        trust=args.trust,
        status=args.status,
        review_status=args.review_status,
        reviewed_by=args.reviewed_by,
        last_reviewed=args.last_reviewed,
    )
    count = index_solutions()
    print(f"Promoted lesson to solution: {result.entry_title}")
    print(f"Path: {result.path}")
    print(f"Solution registry count: {count}")
    return 0


def print_list_knowledge(args: argparse.Namespace) -> int:
    """Handle the list-knowledge command."""
    skills = load_registry().get("skills", [])
    solutions = load_solution_registry().get("solutions", [])

    if args.query:
        query = args.query.lower()
        skills = [
            skill for skill in skills
            if query in str(skill.get("name", "")).lower()
            or query in str(skill.get("title", "")).lower()
            or query in str(skill.get("description", "")).lower()
        ]
        solutions = [
            solution for solution in solutions
            if query in str(solution.get("slug", "")).lower()
            or query in str(solution.get("title", "")).lower()
            or query in str(solution.get("summary", "")).lower()
            or any(query in str(tag).lower() for tag in solution.get("tags", []))
            or any(query in str(tag).lower() for tag in solution.get("stack", []))
        ]

    combined = list_knowledge(project_path=args.project, skills=skills, solutions=solutions)

    if args.json:
        print(
            json.dumps(
                {
                    "project_root": str(combined.project_root) if combined.project_root else None,
                    "skills": combined.skills,
                    "solutions": combined.solutions,
                    "decisions": combined.decisions,
                    "lessons": [lesson.__dict__ for lesson in combined.lessons],
                    "tasks": combined.tasks,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0

    print(f"skills: {len(combined.skills)}")
    print(f"solutions: {len(combined.solutions)}")
    if combined.project_root:
        print(f"project: {combined.project_root}")
        print(f"decisions: {len(combined.decisions)}")
        print(f"lessons: {len(combined.lessons)}")
        print(f"tasks: {len(combined.tasks)}")

    if args.show_items:
        if combined.skills:
            print("\n[skills]")
            for skill in combined.skills[: args.limit]:
                print(f"- {skill['name']}: {skill.get('description', '')}")
        if combined.solutions:
            print("\n[solutions]")
            for solution in combined.solutions[: args.limit]:
                print(f"- {solution['slug']}: {solution.get('summary', '')}")
        if combined.lessons:
            print("\n[lessons]")
            for lesson in combined.lessons[: args.limit]:
                print(f"- {lesson.title}: {lesson.lesson}")
        if combined.decisions:
            print("\n[decisions]")
            for decision in combined.decisions[: args.limit]:
                print(f"- {decision}")
        if combined.tasks:
            print("\n[tasks]")
            for task in combined.tasks[: args.limit]:
                print(f"- {task}")
    return 0


def print_init_project(args: argparse.Namespace) -> int:
    """Handle the init-project command."""
    result = init_project(args.project, overwrite=args.overwrite)

    print(f"Initialized project AI context: {result.project_root / 'ai'}")

    if result.created:
        print("Created:")
        for path in result.created:
            print(f"- {path.relative_to(result.project_root)}")

    if result.overwritten:
        print("Overwritten:")
        for path in result.overwritten:
            print(f"- {path.relative_to(result.project_root)}")

    if result.skipped:
        print("Skipped existing files:")
        for path in result.skipped:
            print(f"- {path.relative_to(result.project_root)}")

    return 0


def print_integrate(args: argparse.Namespace) -> int:
    """Handle the integrate command."""
    result = install_integrations(
        args.project,
        tools=args.tool,
        overwrite=args.overwrite,
    )

    print(f"Installed AI tool integrations for: {', '.join(result.tools)}")
    print(f"Project: {result.project_root}")

    if result.created:
        print("Created:")
        for path in result.created:
            print(f"- {path.relative_to(result.project_root)}")

    if result.overwritten:
        print("Overwritten:")
        for path in result.overwritten:
            print(f"- {path.relative_to(result.project_root)}")

    if result.skipped:
        print("Skipped existing files:")
        for path in result.skipped:
            print(f"- {path.relative_to(result.project_root)}")

    return 0


def print_import_skill(args: argparse.Namespace) -> int:
    """Handle the import-skill command."""
    result = import_skill(
        source_path=args.source,
        provider=args.provider,
        trust_level=args.trust_level,
        source_url=args.source_url,
        name=args.name,
        overwrite=args.overwrite,
    )

    print(f"Imported skill: {result.skill_name}")
    print(f"Destination: {result.destination}")
    print(f"Trust level: {result.trust_level}")
    print(f"Registry skill count: {result.indexed_count}")
    if result.overwritten:
        print("Existing destination was overwritten.")

    if result.validation_errors:
        print("Validation warnings:")
        for error in result.validation_errors:
            print(f"- {error}")
        return 1

    if result.trust_level in {"untrusted", "disabled"}:
        print("Note: this skill is indexed but will not be auto-matched or loaded until reviewed.")

    return 0


def print_trust_skill(args: argparse.Namespace) -> int:
    """Handle the trust-skill command."""
    result = update_skill_trust(args.skill_name, args.trust_level)
    print(f"Updated skill trust: {result.skill_name}")
    print(f"Metadata: {result.metadata_path}")
    print(f"Trust level: {result.old_trust_level} -> {result.new_trust_level}")
    print(f"Registry skill count: {result.indexed_count}")

    if result.validation_errors:
        print("Validation warnings:")
        for error in result.validation_errors:
            print(f"- {error}")
        return 1

    return 0


def print_import_plugin(args: argparse.Namespace) -> int:
    """Handle the import-plugin command."""
    result = import_plugin(
        source_path=args.source,
        provider=args.provider,
        trust_level=args.trust_level,
        source_url=args.source_url,
        name=args.name,
        overwrite=args.overwrite,
    )

    print(f"Imported plugin: {result.plugin_name}")
    print(f"Destination: {result.destination}")
    print(f"Provider: {result.provider}")
    print(f"Trust level: {result.trust_level}")
    print(f"Plugin registry count: {result.plugin_count}")
    print(f"Provider registry count: {result.provider_count}")
    if result.overwritten:
        print("Existing destination was overwritten.")
    if result.trust_level in {"untrusted", "disabled"}:
        print("Note: this plugin is registered but should not be executed until reviewed.")
    return 0


def print_index_plugins(_: argparse.Namespace) -> int:
    """Handle the index-plugins command."""
    plugin_count, provider_count = index_plugins()
    print(f"Indexed {plugin_count} plugin(s) and {provider_count} provider(s).")
    return 0


def print_list_plugins(args: argparse.Namespace) -> int:
    """Handle the list-plugins command."""
    registry = load_plugin_registry()
    plugins = registry.get("plugins", [])
    if args.json:
        print(json.dumps(plugins, indent=2, ensure_ascii=False))
        return 0

    if not plugins:
        print("No plugins registered.")
        return 0

    for plugin in plugins:
        capabilities = ", ".join(plugin.get("capabilities", [])) or "none"
        print(
            f"{plugin['name']} | provider={plugin.get('provider', 'unknown')} "
            f"| trust={plugin.get('trust_level', plugin.get('status', 'unknown'))} "
            f"| capabilities={capabilities}"
        )
    return 0


def print_list_providers(args: argparse.Namespace) -> int:
    """Handle the list-providers command."""
    registry = load_provider_registry()
    providers = registry.get("providers", [])
    if args.json:
        print(json.dumps(providers, indent=2, ensure_ascii=False))
        return 0

    if not providers:
        print("No providers registered.")
        return 0

    for provider in providers:
        trust_levels = ", ".join(provider.get("trust_levels", [])) or "none"
        plugins = ", ".join(provider.get("plugins", [])) or "none"
        print(
            f"{provider['name']} | plugin_count={provider.get('plugin_count', 0)} "
            f"| trust_levels={trust_levels} | plugins={plugins}"
        )
    return 0


def print_trust_plugin(args: argparse.Namespace) -> int:
    """Handle the trust-plugin command."""
    result = update_plugin_trust(args.plugin_name, args.trust_level)
    print(f"Updated plugin trust: {result.plugin_name}")
    print(f"Metadata: {result.metadata_path}")
    print(f"Trust level: {result.old_trust_level} -> {result.new_trust_level}")
    print(f"Plugin registry count: {result.plugin_count}")
    print(f"Provider registry count: {result.provider_count}")
    return 0


def print_log_decision(args: argparse.Namespace) -> int:
    """Handle the log-decision command."""
    result = log_decision(
        project_path=args.project,
        title=args.title,
        context=args.context,
        decision=args.decision,
        reasoning=args.reasoning,
        consequences=args.consequences,
        review_date=args.review_date,
    )
    print(f"Logged decision: {result.entry_title}")
    print(f"Path: {result.path}")
    return 0


def print_capture_lesson(args: argparse.Namespace) -> int:
    """Handle the capture-lesson command."""
    result = capture_lesson(
        project_path=args.project,
        title=args.title,
        situation=args.situation,
        lesson=args.lesson,
        applies_to=args.applies_to,
        reusable_globally=args.reusable_globally,
    )
    print(f"Captured lesson: {result.entry_title}")
    print(f"Path: {result.path}")
    return 0


def print_add_task(args: argparse.Namespace) -> int:
    """Handle the add-task command."""
    result = add_task(
        project_path=args.project,
        title=args.title,
        goal=args.goal,
        context=args.context,
        validation=args.validation,
        section=args.section,
    )
    print(f"Added task: {result.entry_title}")
    print(f"Path: {result.path}")
    return 0


def print_capture_update(args: argparse.Namespace) -> int:
    """Handle the capture-update command."""
    result = capture_global_update(
        title=args.title,
        context=args.context,
        change=args.change,
        reason=args.reason,
        follow_up=args.follow_up,
    )
    print(f"Captured global update: {result.entry_title}")
    print(f"Path: {result.path}")
    return 0


def print_doctor(args: argparse.Namespace) -> int:
    """Handle the doctor command."""
    checks = run_doctor(args.project)
    print(format_doctor(checks))
    return doctor_exit_code(checks) if args.strict else 0


def print_inspect_project(args: argparse.Namespace) -> int:
    """Handle the inspect-project command."""
    inspection = inspect_project(args.project)
    if args.write:
        path = write_detected_context(args.project, overwrite=args.overwrite)
        print(f"Wrote detected project context: {path}")
    print(inspection_to_markdown(inspection))
    return 0


def print_onboard(args: argparse.Namespace) -> int:
    """Handle the onboard command."""
    result = onboard_project(args.project, tools=args.tools, overwrite=args.overwrite)
    print(f"Onboarded project: {result.project_root}")
    print(f"Detected context: {result.context_path}")
    print("")
    print(format_doctor(result.doctor_checks))
    return 0


def print_prepare(args: argparse.Namespace) -> int:
    """Handle the prepare command."""
    print(
        prepare_task(
            task=args.task,
            project=args.project,
            tool=args.tool,
            skill_limit=args.skill_limit,
            solution_limit=args.solution_limit,
            include_doctor=not args.no_doctor,
        )
    )
    return 0


def print_self_test(_: argparse.Namespace) -> int:
    """Handle the self-test command."""
    results = run_self_test()
    print(format_self_test(results))
    return self_test_exit_code(results)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="aios",
        description="Personal AI Engineering OS runtime.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    match_parser = subparsers.add_parser(
        "match",
        help="Match a request to skills. Skills below the relevance threshold are omitted.",
    )
    match_parser.add_argument("request", help="User request to match.")
    match_parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help=(
            "Maximum number of matches to print. Use 0 for all matches. "
            "Only skills above the relevance threshold are returned, so "
            "fewer (or zero) results than the limit is normal."
        ),
    )
    match_parser.set_defaults(func=print_match)

    load_parser = subparsers.add_parser("load", help="Load skill context by name.")
    load_parser.add_argument("skill_names", nargs="+", help="Skill names to load.")
    load_parser.set_defaults(func=print_load)

    build_parser_ = subparsers.add_parser("build", help="Build an AI coding prompt.")
    build_parser_.add_argument("--task", required=True, help="User task.")
    build_parser_.add_argument(
        "--project",
        default=None,
        help="Optional project root containing ai/spec.md, ai/design.md, ai/context.md.",
    )
    build_parser_.add_argument(
        "--skill-limit",
        type=int,
        default=5,
        help="Maximum number of matched skills to load. Use 0 for all matches.",
    )
    build_parser_.add_argument(
        "--solution-limit",
        type=int,
        default=3,
        help="Maximum number of matched solutions to load. Use 0 for all matches.",
    )
    build_parser_.add_argument(
        "--tool",
        choices=SUPPORTED_BUILD_TOOLS,
        default="universal",
        help="Prompt adapter to use. Defaults to universal.",
    )
    build_parser_.set_defaults(func=print_build)

    index_parser = subparsers.add_parser("index", help="Rebuild the skill registry.")
    index_parser.set_defaults(func=print_index)

    index_solutions_parser = subparsers.add_parser(
        "index-solutions",
        help="Rebuild the shared solution registry.",
    )
    index_solutions_parser.set_defaults(func=print_index_solutions)

    list_skills_parser = subparsers.add_parser(
        "list-skills",
        help="List indexed skills from local and external sources.",
    )
    list_skills_parser.add_argument(
        "--source",
        choices=("all", "local", "external"),
        default="all",
        help="Filter by source type. Defaults to all.",
    )
    list_skills_parser.add_argument(
        "--query",
        default=None,
        help="Optional case-insensitive substring filter.",
    )
    list_skills_parser.add_argument(
        "--json",
        action="store_true",
        help="Print raw skill registry JSON entries.",
    )
    list_skills_parser.set_defaults(func=print_list_skills)

    list_skill_sources_parser = subparsers.add_parser(
        "list-skill-sources",
        help="List configured external skill source roots.",
    )
    list_skill_sources_parser.add_argument(
        "--json",
        action="store_true",
        help="Print raw source status JSON.",
    )
    list_skill_sources_parser.set_defaults(func=print_list_skill_sources)

    list_solutions_parser = subparsers.add_parser(
        "list-solutions",
        help="List indexed shared solutions.",
    )
    list_solutions_parser.add_argument(
        "--query",
        default=None,
        help="Optional case-insensitive substring filter.",
    )
    list_solutions_parser.add_argument(
        "--status",
        choices=("all", "draft", "active", "deprecated", "archived"),
        default="all",
        help="Filter by solution status. Defaults to all.",
    )
    list_solutions_parser.add_argument(
        "--trust",
        choices=("all", "draft", "reviewed", "vendor", "untrusted"),
        default="all",
        help="Filter by trust level. Defaults to all.",
    )
    list_solutions_parser.add_argument(
        "--review-status",
        choices=("all", "draft", "needs_review", "reviewed"),
        default="all",
        help="Filter by review status. Defaults to all.",
    )
    list_solutions_parser.add_argument(
        "--stale",
        choices=("all", "only", "fresh"),
        default="all",
        help="Filter stale vs fresh solutions. Defaults to all.",
    )
    list_solutions_parser.add_argument(
        "--json",
        action="store_true",
        help="Print raw solution registry JSON entries.",
    )
    list_solutions_parser.set_defaults(func=print_list_solutions)

    validate_parser = subparsers.add_parser("validate", help="Validate skills.")
    validate_parser.add_argument(
        "skill_path",
        nargs="?",
        help="Optional skill directory path. Defaults to all skills.",
    )
    validate_parser.add_argument(
        "--all",
        action="store_true",
        help="Validate all skills.",
    )
    validate_parser.set_defaults(func=print_validate)

    validate_solutions_parser = subparsers.add_parser(
        "validate-solutions",
        help="Validate shared solution documents.",
    )
    validate_solutions_parser.add_argument(
        "solution_path",
        nargs="?",
        help="Optional solution document path. Defaults to all solutions.",
    )
    validate_solutions_parser.add_argument(
        "--all",
        action="store_true",
        help="Validate all solutions.",
    )
    validate_solutions_parser.set_defaults(func=print_validate_solutions)

    capture_solution_parser = subparsers.add_parser(
        "capture-solution",
        help="Create a shared solution document under docs/solutions/.",
    )
    capture_solution_parser.add_argument("--title", required=True, help="Solution title.")
    capture_solution_parser.add_argument("--owner", required=True, help="Owner for this solution.")
    capture_solution_parser.add_argument("--summary", required=True, help="One-paragraph summary.")
    capture_solution_parser.add_argument("--problem", required=True, help="Problem statement.")
    capture_solution_parser.add_argument("--context", required=True, help="System or project context.")
    capture_solution_parser.add_argument("--solution", required=True, help="Chosen solution.")
    capture_solution_parser.add_argument("--root-cause", default="", help="Root cause summary.")
    capture_solution_parser.add_argument("--tradeoffs", default="", help="Tradeoffs or constraints.")
    capture_solution_parser.add_argument("--verification", default="", help="How the solution was verified.")
    capture_solution_parser.add_argument("--reuse-guidance", default="", help="When this should be reused.")
    capture_solution_parser.add_argument("--do-not-reuse-when", default="", help="When this should not be reused.")
    capture_solution_parser.add_argument("--follow-up", default="", help="Optional follow-up work.")
    capture_solution_parser.add_argument("--slug", default=None, help="Optional filename slug override.")
    capture_solution_parser.add_argument(
        "--status",
        choices=("draft", "active", "deprecated", "archived"),
        default="draft",
        help="Solution lifecycle status.",
    )
    capture_solution_parser.add_argument(
        "--trust",
        choices=("draft", "reviewed", "vendor", "untrusted"),
        default="draft",
        help="Trust level for the solution.",
    )
    capture_solution_parser.add_argument(
        "--review-status",
        choices=("draft", "needs_review", "reviewed"),
        default="draft",
        help="Review status for the solution.",
    )
    capture_solution_parser.add_argument(
        "--reviewed-by",
        default="",
        help="Reviewer name when the solution is reviewed.",
    )
    capture_solution_parser.add_argument(
        "--last-reviewed",
        default="",
        help="Last review date in YYYY-MM-DD format.",
    )
    capture_solution_parser.add_argument(
        "--source-type",
        default="project",
        help="Source type label for this solution.",
    )
    capture_solution_parser.add_argument(
        "--project",
        default=None,
        help="Optional project root used as a source reference.",
    )
    capture_solution_parser.add_argument(
        "--tag",
        action="append",
        default=[],
        help="Tag to add. Repeat for multiple tags.",
    )
    capture_solution_parser.add_argument(
        "--stack",
        action="append",
        default=[],
        help="Stack label to add. Repeat for multiple values.",
    )
    capture_solution_parser.add_argument(
        "--source-ref",
        action="append",
        default=[],
        help="Explicit source reference. Repeat for multiple values.",
    )
    capture_solution_parser.set_defaults(func=print_capture_solution)

    promote_lesson_parser = subparsers.add_parser(
        "promote-lesson",
        help="Turn a project lesson into a shared solution document.",
    )
    promote_lesson_parser.add_argument("--project", default=".", help="Project root.")
    promote_lesson_parser.add_argument("--title", required=True, help="Exact lesson title to promote.")
    promote_lesson_parser.add_argument("--owner", required=True, help="Owner for this solution.")
    promote_lesson_parser.add_argument("--summary", required=True, help="One-paragraph summary.")
    promote_lesson_parser.add_argument("--solution", required=True, help="Chosen solution writeup.")
    promote_lesson_parser.add_argument("--root-cause", default="", help="Root cause summary.")
    promote_lesson_parser.add_argument("--tradeoffs", default="", help="Tradeoffs or constraints.")
    promote_lesson_parser.add_argument("--verification", default="", help="How the solution was verified.")
    promote_lesson_parser.add_argument("--reuse-guidance", default="", help="When this should be reused.")
    promote_lesson_parser.add_argument("--do-not-reuse-when", default="", help="When this should not be reused.")
    promote_lesson_parser.add_argument("--follow-up", default="", help="Optional follow-up work.")
    promote_lesson_parser.add_argument("--slug", default=None, help="Optional filename slug override.")
    promote_lesson_parser.add_argument(
        "--status",
        choices=("draft", "active", "deprecated", "archived"),
        default="draft",
        help="Solution lifecycle status.",
    )
    promote_lesson_parser.add_argument(
        "--trust",
        choices=("draft", "reviewed", "vendor", "untrusted"),
        default="draft",
        help="Trust level for the solution.",
    )
    promote_lesson_parser.add_argument(
        "--review-status",
        choices=("draft", "needs_review", "reviewed"),
        default="draft",
        help="Review status for the solution.",
    )
    promote_lesson_parser.add_argument(
        "--reviewed-by",
        default="",
        help="Reviewer name when the solution is reviewed.",
    )
    promote_lesson_parser.add_argument(
        "--last-reviewed",
        default="",
        help="Last review date in YYYY-MM-DD format.",
    )
    promote_lesson_parser.add_argument(
        "--tag",
        action="append",
        default=[],
        help="Tag to add. Repeat for multiple tags.",
    )
    promote_lesson_parser.add_argument(
        "--stack",
        action="append",
        default=[],
        help="Stack label to add. Repeat for multiple values.",
    )
    promote_lesson_parser.set_defaults(func=print_promote_lesson)

    list_knowledge_parser = subparsers.add_parser(
        "list-knowledge",
        help="List visible skills, solutions, and optional project-local knowledge.",
    )
    list_knowledge_parser.add_argument(
        "--project",
        default=None,
        help="Optional project root for decisions, lessons, and tasks.",
    )
    list_knowledge_parser.add_argument(
        "--query",
        default=None,
        help="Optional case-insensitive filter across skills and solutions.",
    )
    list_knowledge_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of entries per section when showing items.",
    )
    list_knowledge_parser.add_argument(
        "--show-items",
        action="store_true",
        help="Print example entries from each knowledge section.",
    )
    list_knowledge_parser.add_argument(
        "--json",
        action="store_true",
        help="Print raw combined knowledge JSON.",
    )
    list_knowledge_parser.set_defaults(func=print_list_knowledge)

    init_project_parser = subparsers.add_parser(
        "init-project",
        help="Create project-level ai/ context files.",
    )
    init_project_parser.add_argument(
        "--project",
        default=".",
        help="Project root to initialize. Defaults to the current directory.",
    )
    init_project_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing ai/ files instead of skipping them.",
    )
    init_project_parser.set_defaults(func=print_init_project)

    integrate_parser = subparsers.add_parser(
        "integrate",
        help="Create AI tool instruction files for a project.",
    )
    integrate_parser.add_argument(
        "--project",
        default=".",
        help="Project root to update. Defaults to the current directory.",
    )
    integrate_parser.add_argument(
        "--tool",
        nargs="+",
        choices=("all", *SUPPORTED_TOOLS),
        default=["all"],
        help="Tools to support. Defaults to all.",
    )
    integrate_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing integration files instead of skipping them.",
    )
    integrate_parser.set_defaults(func=print_integrate)

    import_skill_parser = subparsers.add_parser(
        "import-skill",
        help="Import an external skill directory into skills/vendor/.",
    )
    import_skill_parser.add_argument(
        "--source",
        required=True,
        help="Path to the external skill directory.",
    )
    import_skill_parser.add_argument(
        "--provider",
        default="community",
        help="Provider namespace for the imported skill. Defaults to community.",
    )
    import_skill_parser.add_argument(
        "--trust-level",
        choices=TRUST_LEVELS,
        default="untrusted",
        help="Trust level for the imported skill. Defaults to untrusted.",
    )
    import_skill_parser.add_argument(
        "--source-url",
        default=None,
        help="Optional URL where the skill came from.",
    )
    import_skill_parser.add_argument(
        "--name",
        default=None,
        help="Optional skill name override.",
    )
    import_skill_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite an existing imported skill with the same provider/name.",
    )
    import_skill_parser.set_defaults(func=print_import_skill)

    trust_skill_parser = subparsers.add_parser(
        "trust-skill",
        help="Update an imported skill trust level and rebuild the registry.",
    )
    trust_skill_parser.add_argument("skill_name", help="Skill name to update.")
    trust_skill_parser.add_argument(
        "--trust-level",
        required=True,
        choices=TRUST_LEVELS,
        help="New trust level for the skill.",
    )
    trust_skill_parser.set_defaults(func=print_trust_skill)

    import_plugin_parser = subparsers.add_parser(
        "import-plugin",
        help="Import a plugin pack into plugins/vendor/.",
    )
    import_plugin_parser.add_argument(
        "--source",
        required=True,
        help="Path to the plugin pack directory.",
    )
    import_plugin_parser.add_argument(
        "--provider",
        default="community",
        help="Provider namespace for the imported plugin. Defaults to community.",
    )
    import_plugin_parser.add_argument(
        "--trust-level",
        choices=TRUST_LEVELS,
        default="untrusted",
        help="Trust level for the imported plugin. Defaults to untrusted.",
    )
    import_plugin_parser.add_argument(
        "--source-url",
        default=None,
        help="Optional URL where the plugin came from.",
    )
    import_plugin_parser.add_argument(
        "--name",
        default=None,
        help="Optional plugin name override.",
    )
    import_plugin_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite an existing imported plugin with the same provider/name.",
    )
    import_plugin_parser.set_defaults(func=print_import_plugin)

    index_plugins_parser = subparsers.add_parser(
        "index-plugins",
        help="Rebuild plugin and provider registries.",
    )
    index_plugins_parser.set_defaults(func=print_index_plugins)

    list_plugins_parser = subparsers.add_parser(
        "list-plugins",
        help="List registered plugins.",
    )
    list_plugins_parser.add_argument(
        "--json",
        action="store_true",
        help="Print raw plugin registry JSON.",
    )
    list_plugins_parser.set_defaults(func=print_list_plugins)

    list_providers_parser = subparsers.add_parser(
        "list-providers",
        help="List registered providers.",
    )
    list_providers_parser.add_argument(
        "--json",
        action="store_true",
        help="Print raw provider registry JSON.",
    )
    list_providers_parser.set_defaults(func=print_list_providers)

    trust_plugin_parser = subparsers.add_parser(
        "trust-plugin",
        help="Update a plugin trust level and rebuild plugin registries.",
    )
    trust_plugin_parser.add_argument("plugin_name", help="Plugin name to update.")
    trust_plugin_parser.add_argument(
        "--trust-level",
        required=True,
        choices=TRUST_LEVELS,
        help="New trust level for the plugin.",
    )
    trust_plugin_parser.set_defaults(func=print_trust_plugin)

    decision_parser = subparsers.add_parser(
        "log-decision",
        help="Append a durable project decision to ai/decisions.md.",
    )
    decision_parser.add_argument("--project", default=".", help="Project root.")
    decision_parser.add_argument("--title", required=True, help="Decision title.")
    decision_parser.add_argument("--context", required=True, help="Decision context.")
    decision_parser.add_argument("--decision", required=True, help="Decision made.")
    decision_parser.add_argument("--reasoning", required=True, help="Why this decision fits.")
    decision_parser.add_argument("--consequences", default="", help="Consequences or trade-offs.")
    decision_parser.add_argument("--review-date", default="", help="Optional review date.")
    decision_parser.set_defaults(func=print_log_decision)

    lesson_parser = subparsers.add_parser(
        "capture-lesson",
        help="Append a project lesson to ai/lessons.md.",
    )
    lesson_parser.add_argument("--project", default=".", help="Project root.")
    lesson_parser.add_argument("--title", required=True, help="Lesson title.")
    lesson_parser.add_argument("--situation", required=True, help="What happened.")
    lesson_parser.add_argument("--lesson", required=True, help="What to remember.")
    lesson_parser.add_argument("--applies-to", default="", help="Where this applies.")
    lesson_parser.add_argument(
        "--reusable-globally",
        action="store_true",
        help="Mark the lesson as reusable beyond this project.",
    )
    lesson_parser.set_defaults(func=print_capture_lesson)

    task_parser = subparsers.add_parser(
        "add-task",
        help="Append an AI-assisted task to ai/tasks.md.",
    )
    task_parser.add_argument("--project", default=".", help="Project root.")
    task_parser.add_argument("--title", required=True, help="Task title.")
    task_parser.add_argument("--goal", required=True, help="Task goal.")
    task_parser.add_argument("--context", default="", help="Task context.")
    task_parser.add_argument("--validation", default="", help="Expected validation.")
    task_parser.add_argument("--section", default="Next", help="Backlog section label.")
    task_parser.set_defaults(func=print_add_task)

    update_parser = subparsers.add_parser(
        "capture-update",
        help="Create a reusable global update under engineering_brain/updates/.",
    )
    update_parser.add_argument("--title", required=True, help="Update title.")
    update_parser.add_argument("--context", required=True, help="Where the lesson came from.")
    update_parser.add_argument("--change", required=True, help="What should change.")
    update_parser.add_argument("--reason", required=True, help="Why this improves future work.")
    update_parser.add_argument("--follow-up", default="", help="Optional follow-up.")
    update_parser.set_defaults(func=print_capture_update)

    doctor_parser = subparsers.add_parser(
        "doctor",
        help="Check whether a project is AI OS ready.",
    )
    doctor_parser.add_argument("--project", default=".", help="Project root.")
    doctor_parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when any doctor check fails.",
    )
    doctor_parser.set_defaults(func=print_doctor)

    inspect_parser = subparsers.add_parser(
        "inspect-project",
        help="Detect project stack, commands, and paths.",
    )
    inspect_parser.add_argument("--project", default=".", help="Project root.")
    inspect_parser.add_argument(
        "--write",
        action="store_true",
        help="Append detected context to ai/context.md.",
    )
    inspect_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite ai/context.md when used with --write.",
    )
    inspect_parser.set_defaults(func=print_inspect_project)

    onboard_parser = subparsers.add_parser(
        "onboard",
        help="Initialize, inspect, integrate, and doctor a project.",
    )
    onboard_parser.add_argument("--project", default=".", help="Project root.")
    onboard_parser.add_argument(
        "--tools",
        nargs="+",
        choices=("all", *SUPPORTED_TOOLS),
        default=["all"],
        help="Tool integrations to install. Defaults to all.",
    )
    onboard_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite detected context and integration files.",
    )
    onboard_parser.set_defaults(func=print_onboard)

    prepare_parser = subparsers.add_parser(
        "prepare",
        help="Run readiness checks and build a tool-specific task prompt.",
    )
    prepare_parser.add_argument("--task", required=True, help="User task.")
    prepare_parser.add_argument("--project", default=".", help="Project root.")
    prepare_parser.add_argument(
        "--tool",
        choices=SUPPORTED_BUILD_TOOLS,
        default="universal",
        help="Prompt adapter to use.",
    )
    prepare_parser.add_argument(
        "--skill-limit",
        type=int,
        default=5,
        help=(
            "Maximum number of matched skills considered after the relevance "
            "threshold. Use 0 for all matches above the threshold. The top "
            "matches are inlined in full; the rest become one-line pointers "
            "loadable with `aios load <name>`."
        ),
    )
    prepare_parser.add_argument(
        "--solution-limit",
        type=int,
        default=3,
        help="Maximum number of matched solutions to load.",
    )
    prepare_parser.add_argument(
        "--no-doctor",
        action="store_true",
        help="Skip readiness warnings.",
    )
    prepare_parser.set_defaults(func=print_prepare)

    self_test_parser = subparsers.add_parser(
        "self-test",
        help="Run dependency-free AI OS runtime smoke tests.",
    )
    self_test_parser.set_defaults(func=print_self_test)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the AI OS CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
