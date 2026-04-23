"""Project inspection for AI OS onboarding."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectInspection:
    """Detected project facts."""

    project_root: Path
    languages: list[str]
    package_managers: list[str]
    frameworks: list[str]
    test_commands: list[str]
    lint_commands: list[str]
    format_commands: list[str]
    source_paths: list[str]
    test_paths: list[str]
    ci_files: list[str]
    docker_files: list[str]
    database_hints: list[str]


def exists(root: Path, relative: str) -> bool:
    """Return whether a relative path exists."""
    return (root / relative).exists()


def detect_languages(root: Path) -> list[str]:
    """Detect project languages from common files."""
    languages: list[str] = []
    markers = {
        "Python": ("pyproject.toml", "requirements.txt", "setup.py"),
        "Node/TypeScript": ("package.json", "tsconfig.json"),
        "Go": ("go.mod",),
        "Rust": ("Cargo.toml",),
        "Java": ("pom.xml", "build.gradle", "settings.gradle"),
        "Ruby": ("Gemfile",),
    }
    for language, files in markers.items():
        if any(exists(root, file) for file in files):
            languages.append(language)
    return languages


def detect_package_managers(root: Path) -> list[str]:
    """Detect package managers from lockfiles."""
    managers: list[str] = []
    markers = {
        "uv": "uv.lock",
        "poetry": "poetry.lock",
        "pip": "requirements.txt",
        "npm": "package-lock.json",
        "pnpm": "pnpm-lock.yaml",
        "yarn": "yarn.lock",
        "cargo": "Cargo.lock",
        "go": "go.mod",
        "maven": "pom.xml",
        "gradle": "build.gradle",
    }
    for manager, marker in markers.items():
        if exists(root, marker):
            managers.append(manager)
    return managers


def package_json(root: Path) -> dict:
    """Read package.json when available."""
    path = root / "package.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def detect_frameworks(root: Path) -> list[str]:
    """Detect common frameworks."""
    frameworks: list[str] = []
    package = package_json(root)
    deps = {
        **package.get("dependencies", {}),
        **package.get("devDependencies", {}),
    }
    dependency_markers = {
        "Next.js": "next",
        "React": "react",
        "Vue": "vue",
        "Vite": "vite",
        "Express": "express",
    }
    for framework, dep in dependency_markers.items():
        if dep in deps:
            frameworks.append(framework)

    if exists(root, "manage.py"):
        frameworks.append("Django")
    if exists(root, "app.py") or exists(root, "main.py"):
        text = ""
        for file in ("app.py", "main.py"):
            path = root / file
            if path.exists():
                text += path.read_text(encoding="utf-8", errors="ignore")[:5000]
        if "FastAPI" in text:
            frameworks.append("FastAPI")
        if "Flask" in text:
            frameworks.append("Flask")

    return sorted(set(frameworks))


def detect_commands(root: Path) -> tuple[list[str], list[str], list[str]]:
    """Detect likely test, lint, and format commands."""
    tests: list[str] = []
    lint: list[str] = []
    fmt: list[str] = []

    package = package_json(root)
    scripts = package.get("scripts", {})
    for name in scripts:
        if name in {"test", "test:unit", "test:e2e"}:
            tests.append(f"npm run {name}")
        if "lint" in name:
            lint.append(f"npm run {name}")
        if name in {"format", "fmt", "prettier"} or "format" in name:
            fmt.append(f"npm run {name}")

    if exists(root, "pyproject.toml") or exists(root, "pytest.ini"):
        tests.append("python3 -m pytest")
    if exists(root, "uv.lock"):
        tests.insert(0, "uv run pytest")
    if exists(root, "go.mod"):
        tests.append("go test ./...")
        fmt.append("gofmt")
    if exists(root, "Cargo.toml"):
        tests.append("cargo test")
        lint.append("cargo clippy")
        fmt.append("cargo fmt")

    return dedupe(tests), dedupe(lint), dedupe(fmt)


def detect_paths(root: Path) -> tuple[list[str], list[str]]:
    """Detect common source and test paths."""
    source_candidates = ("src", "app", "lib", "packages", "services")
    test_candidates = ("tests", "test", "__tests__", "spec", "e2e")
    sources = [path for path in source_candidates if exists(root, path)]
    tests = [path for path in test_candidates if exists(root, path)]
    return sources, tests


def detect_file_groups(root: Path) -> tuple[list[str], list[str], list[str]]:
    """Detect CI, Docker, and database hints."""
    ci: list[str] = []
    docker: list[str] = []
    db: list[str] = []

    for candidate in (".github/workflows", ".gitlab-ci.yml", "circle.yml"):
        if exists(root, candidate):
            ci.append(candidate)
    for candidate in ("Dockerfile", "docker-compose.yml", "compose.yml"):
        if exists(root, candidate):
            docker.append(candidate)
    for candidate in ("migrations", "prisma", "drizzle", "alembic", "db", "database"):
        if exists(root, candidate):
            db.append(candidate)
    return ci, docker, db


def dedupe(items: list[str]) -> list[str]:
    """Return items with stable order and no duplicates."""
    result: list[str] = []
    for item in items:
        if item not in result:
            result.append(item)
    return result


def inspect_project(project_path: str | Path) -> ProjectInspection:
    """Inspect a project root and return detected facts."""
    root = Path(project_path).expanduser().resolve()
    test_commands, lint_commands, format_commands = detect_commands(root)
    source_paths, test_paths = detect_paths(root)
    ci_files, docker_files, database_hints = detect_file_groups(root)
    return ProjectInspection(
        project_root=root,
        languages=detect_languages(root),
        package_managers=detect_package_managers(root),
        frameworks=detect_frameworks(root),
        test_commands=test_commands,
        lint_commands=lint_commands,
        format_commands=format_commands,
        source_paths=source_paths,
        test_paths=test_paths,
        ci_files=ci_files,
        docker_files=docker_files,
        database_hints=database_hints,
    )


def inspection_to_markdown(inspection: ProjectInspection) -> str:
    """Render detected facts as Markdown."""
    def bullet(items: list[str]) -> str:
        if not items:
            return "- Not detected."
        return "\n".join(f"- {item}" for item in items)

    commands = [
        "# Detected Project Context",
        "",
        "## Tech Stack",
        "",
        f"**Languages**\n\n{bullet(inspection.languages)}",
        "",
        f"**Frameworks**\n\n{bullet(inspection.frameworks)}",
        "",
        f"**Package Managers**\n\n{bullet(inspection.package_managers)}",
        "",
        "## Commands",
        "",
        f"**Tests**\n\n{bullet(inspection.test_commands)}",
        "",
        f"**Lint**\n\n{bullet(inspection.lint_commands)}",
        "",
        f"**Format**\n\n{bullet(inspection.format_commands)}",
        "",
        "## Paths",
        "",
        f"**Source Paths**\n\n{bullet(inspection.source_paths)}",
        "",
        f"**Test Paths**\n\n{bullet(inspection.test_paths)}",
        "",
        "## Operations",
        "",
        f"**CI Files**\n\n{bullet(inspection.ci_files)}",
        "",
        f"**Docker Files**\n\n{bullet(inspection.docker_files)}",
        "",
        f"**Database Hints**\n\n{bullet(inspection.database_hints)}",
    ]
    return "\n".join(commands).strip() + "\n"


def write_detected_context(project_path: str | Path, overwrite: bool = False) -> Path:
    """Write detected context to ai/context.md."""
    inspection = inspect_project(project_path)
    path = inspection.project_root / "ai" / "context.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    detected = inspection_to_markdown(inspection)

    if path.exists() and not overwrite:
        existing = path.read_text(encoding="utf-8")
        marker = "\n\n---\n\n"
        path.write_text(existing.rstrip() + marker + detected, encoding="utf-8")
    else:
        path.write_text(detected, encoding="utf-8")
    return path
