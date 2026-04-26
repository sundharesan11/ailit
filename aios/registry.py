"""Skill registry indexing, external discovery, and validation."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from .paths import REGISTRY_PATH, ROOT, SKILLS_DIR


REQUIRED_FIELDS = {
    "name",
    "title",
    "description",
    "path",
    "tags",
    "version",
    "status",
    "entrypoint",
}

TRUST_LEVELS = {"local", "reviewed", "vendor", "untrusted", "disabled"}
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
DEFAULT_EXTERNAL_SKILL_SOURCE_PATHS = (
    Path.home() / ".agents" / "skills",
    Path.home() / ".codex" / "skills",
)


def slugify_name(value: str) -> str:
    """Return a filesystem-safe, registry-safe skill name."""
    slug = re.sub(r"[^a-zA-Z0-9_:+ -]+", "", value).strip().lower()
    slug = slug.replace(":", "_")
    slug = re.sub(r"[\s-]+", "_", slug)
    return slug or "skill"


def default_title(name: str) -> str:
    """Convert a skill name into a readable title."""
    return " ".join(part.capitalize() for part in name.split("_"))


def home_relative_label(path: Path) -> str:
    """Return a stable label for a path."""
    try:
        return f"~/{path.resolve().relative_to(Path.home()).as_posix()}"
    except ValueError:
        return path.resolve().as_posix()


def parse_frontmatter(text: str) -> dict[str, str]:
    """Parse a simple YAML frontmatter block from a SKILL.md file."""
    if not text.startswith("---"):
        return {}

    lines = text.splitlines()
    metadata: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if not line or line.startswith((" ", "\t")) or ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip().strip("\"'")
        metadata[key.strip()] = value
    return metadata


def markdown_title(text: str) -> str | None:
    """Return the first markdown H1 title, if present."""
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip().lstrip("/").strip()
    return None


def configured_external_skill_sources() -> list[Path]:
    """Return configured external skill roots.

    `AIOS_SKILL_SOURCES` overrides the defaults when set. Use the platform path
    separator to provide multiple roots.
    """
    raw = os.getenv("AIOS_SKILL_SOURCES")
    if raw:
        paths = [Path(part).expanduser().resolve() for part in raw.split(os.pathsep) if part.strip()]
    else:
        paths = [path.expanduser().resolve() for path in DEFAULT_EXTERNAL_SKILL_SOURCE_PATHS]

    unique: list[Path] = []
    for path in paths:
        if path not in unique:
            unique.append(path)
    return unique


def source_label_for_root(source_root: Path) -> str:
    """Return a short provider label for an external skill root."""
    parts = {part.lstrip(".") for part in source_root.parts}
    if "agents" in parts:
        return "agents"
    if "codex" in parts:
        return "codex"
    return slugify_name(source_root.name)


def source_kind_for_root(source_root: Path) -> str:
    """Return a source kind for an external skill root."""
    parts = {part.lstrip(".") for part in source_root.parts}
    if "agents" in parts:
        return "agents_installed"
    if "codex" in parts:
        return "codex_installed"
    return "external_installed"


def tokenize_text(text: str) -> list[str]:
    """Return lowercase tokens from text."""
    return TOKEN_PATTERN.findall(text.lower().replace("_", " ").replace("-", " "))


def local_skill_count() -> int:
    """Return the number of local AI OS skills with metadata."""
    return len(list(SKILLS_DIR.glob("**/metadata.json")))


def external_skill_markdown_paths(source_root: Path) -> list[Path]:
    """Return discovered SKILL.md paths under an external source root."""
    if not source_root.exists():
        return []
    return sorted(path for path in source_root.rglob("SKILL.md") if path.is_file())


def external_skill_source_statuses() -> list[dict[str, Any]]:
    """Return status records for configured external skill roots."""
    statuses: list[dict[str, Any]] = []
    for source_root in configured_external_skill_sources():
        skill_count = len(external_skill_markdown_paths(source_root))
        statuses.append(
            {
                "label": source_label_for_root(source_root),
                "path": source_root.resolve().as_posix(),
                "display_path": home_relative_label(source_root),
                "exists": source_root.exists(),
                "skill_count": skill_count,
                "source_kind": source_kind_for_root(source_root),
            }
        )
    return statuses


def load_registry(registry_path: Path = REGISTRY_PATH, refresh: bool = True) -> dict[str, Any]:
    """Load the skill registry JSON document.

    By default this refreshes the registry first so newly installed external
    skills are visible without a manual reindex step.
    """
    if refresh:
        return refresh_registry(registry_path)
    return json.loads(registry_path.read_text(encoding="utf-8"))


def registry_by_name(registry: dict[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    """Return registry skills keyed by skill name."""
    registry = registry or load_registry()
    return {skill["name"]: skill for skill in registry.get("skills", [])}


def load_local_skill_metadata() -> list[dict[str, Any]]:
    """Load all local AI OS skill metadata files under skills/."""
    skills: list[dict[str, Any]] = []

    for metadata_path in sorted(SKILLS_DIR.glob("**/metadata.json")):
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        skill_dir = metadata_path.parent
        metadata["path"] = skill_dir.relative_to(ROOT).as_posix()
        metadata["source"] = metadata.get("source", "local")
        metadata["source_type"] = metadata.get("source_type", "local")
        skills.append(metadata)

    return sorted(skills, key=lambda item: item["name"])


def normalize_external_skill(source_root: Path, skill_md_path: Path) -> dict[str, Any]:
    """Convert an installed external SKILL.md into registry metadata."""
    text = skill_md_path.read_text(encoding="utf-8", errors="ignore")
    frontmatter = parse_frontmatter(text)
    raw_name = frontmatter.get("name") or skill_md_path.parent.name
    name = slugify_name(raw_name)
    title = markdown_title(text) or default_title(name)
    description = frontmatter.get("description") or f"Installed skill from {source_label_for_root(source_root)}."
    source_label = source_label_for_root(source_root)
    display_path = home_relative_label(skill_md_path.parent)

    tag_tokens = set(tokenize_text(raw_name))
    if title:
        tag_tokens.update(tokenize_text(title))
    tag_tokens.update({"external", source_label})

    aliases = []
    for alias in (raw_name, skill_md_path.parent.name):
        if alias and alias not in aliases:
            aliases.append(alias)

    return {
        "name": name,
        "title": title,
        "description": description,
        "path": display_path,
        "source_path": skill_md_path.parent.resolve().as_posix(),
        "source_root": source_root.resolve().as_posix(),
        "source": "external",
        "source_type": source_kind_for_root(source_root),
        "provider": source_label,
        "tags": sorted(tag_tokens),
        "aliases": aliases,
        "keywords": [],
        "version": frontmatter.get("version", "external"),
        "status": "active",
        "trust_level": "reviewed",
        "entrypoint": "SKILL.md",
    }


def ensure_unique_skill_names(skills: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Ensure registry skill names are unique, preferring earlier entries."""
    used_names: set[str] = set()
    unique_skills: list[dict[str, Any]] = []

    for skill in skills:
        candidate = str(skill["name"])
        if candidate not in used_names:
            used_names.add(candidate)
            unique_skills.append(skill)
            continue

        updated = dict(skill)
        aliases = list(updated.get("aliases", []))
        if candidate not in aliases:
            aliases.append(candidate)
        prefix = slugify_name(str(updated.get("provider", updated.get("source_type", "external"))))
        candidate = f"{prefix}_{candidate}"
        suffix = 2
        while candidate in used_names:
            candidate = f"{prefix}_{skill['name']}_{suffix}"
            suffix += 1
        updated["name"] = candidate
        updated["aliases"] = aliases
        used_names.add(candidate)
        unique_skills.append(updated)

    return unique_skills


def load_external_skill_metadata() -> list[dict[str, Any]]:
    """Load installed external skills from configured source roots."""
    skills: list[dict[str, Any]] = []
    for source_root in configured_external_skill_sources():
        for skill_md_path in external_skill_markdown_paths(source_root):
            skills.append(normalize_external_skill(source_root, skill_md_path))
    return sorted(ensure_unique_skill_names(skills), key=lambda item: item["name"])


def build_registry() -> dict[str, Any]:
    """Build the in-memory skill registry."""
    local_skills = load_local_skill_metadata()
    external_skills = load_external_skill_metadata()
    all_skills = ensure_unique_skill_names(local_skills + external_skills)
    return {
        "schema_version": "1.1",
        "description": (
            "Skill registry for the Personal AI Engineering OS. "
            "Generated by aios.registry."
        ),
        "skill_sources": {
            "local": {
                "path": SKILLS_DIR.resolve().as_posix(),
                "display_path": home_relative_label(SKILLS_DIR),
                "skill_count": len(local_skills),
            },
            "external": external_skill_source_statuses(),
        },
        "skills": sorted(all_skills, key=lambda item: item["name"]),
    }


def index_skills() -> int:
    """Write registry/skills.json and return the number of indexed skills."""
    registry = build_registry()
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(
        json.dumps(registry, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return len(registry["skills"])


def refresh_registry(registry_path: Path = REGISTRY_PATH) -> dict[str, Any]:
    """Refresh registry/skills.json from current local and external sources."""
    registry = build_registry()
    serialized = json.dumps(registry, indent=2, ensure_ascii=False) + "\n"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    if not registry_path.exists() or registry_path.read_text(encoding="utf-8") != serialized:
        registry_path.write_text(serialized, encoding="utf-8")
    return registry


def find_brain_root(path: Path) -> Path:
    """Return the nearest engineering_brain root for a path."""
    current = path.resolve()
    if current.is_file():
        current = current.parent

    for candidate in [current, *current.parents]:
        if candidate.name == "engineering_brain":
            return candidate

    raise ValueError("Path is not inside an engineering_brain directory")


def validate_skill(skill_dir: Path) -> list[str]:
    """Return a list of validation errors for a skill directory."""
    errors: list[str] = []
    skill_dir = skill_dir.expanduser().resolve()

    if not skill_dir.exists():
        return [f"Skill directory does not exist: {skill_dir}"]
    if not skill_dir.is_dir():
        return [f"Skill path is not a directory: {skill_dir}"]

    metadata_path = skill_dir / "metadata.json"
    skill_path = skill_dir / "skill.md"

    if not metadata_path.exists():
        errors.append("Missing metadata.json")
    if not skill_path.exists():
        errors.append("Missing skill.md")

    if errors:
        return errors

    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"metadata.json is invalid JSON: {exc}"]

    missing_fields = sorted(REQUIRED_FIELDS - set(metadata))
    if missing_fields:
        errors.append(f"Missing metadata fields: {', '.join(missing_fields)}")

    if metadata.get("entrypoint") != "skill.md":
        errors.append("metadata.entrypoint should be skill.md")

    trust_level = metadata.get("trust_level")
    if trust_level is not None and trust_level not in TRUST_LEVELS:
        supported = ", ".join(sorted(TRUST_LEVELS))
        errors.append(f"metadata.trust_level must be one of: {supported}")

    status = metadata.get("status")
    if status in TRUST_LEVELS and trust_level is not None and status != trust_level:
        errors.append("metadata.status and metadata.trust_level should match")

    tags = metadata.get("tags")
    if tags is not None and not isinstance(tags, list):
        errors.append("metadata.tags must be a list")

    try:
        brain_root = find_brain_root(skill_dir)
        expected_path = skill_dir.relative_to(brain_root).as_posix()
        if metadata.get("path") != expected_path:
            errors.append(
                f"metadata.path should be {expected_path!r}, got {metadata.get('path')!r}"
            )
    except ValueError as exc:
        errors.append(str(exc))

    return errors


def skill_dirs() -> list[Path]:
    """Return all skill directories that contain metadata."""
    return sorted(metadata_path.parent for metadata_path in SKILLS_DIR.glob("**/metadata.json"))


def validate_all_skills() -> dict[str, list[str]]:
    """Validate all indexed skill directories and return errors by path."""
    results: dict[str, list[str]] = {}
    for skill_dir in skill_dirs():
        errors = validate_skill(skill_dir)
        if errors:
            results[skill_dir.relative_to(ROOT).as_posix()] = errors
    return results
