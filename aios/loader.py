"""Skill loading runtime."""

from __future__ import annotations

from typing import Any

from .paths import ROOT
from .registry import load_registry, registry_by_name


LOADABLE_TRUST_LEVELS = {"local", "reviewed", "vendor"}


def effective_trust_level(skill: dict[str, Any]) -> str:
    """Return the trust level used for loading."""
    if "trust_level" in skill:
        return str(skill["trust_level"])
    status = str(skill.get("status", "local"))
    if status in {"untrusted", "disabled"}:
        return status
    return "local"


def load_skill_content(skill: dict[str, Any]) -> str:
    """Load one skill's entrypoint content."""
    skill_path = ROOT / skill["path"]
    entrypoint = skill.get("entrypoint", "skill.md")
    content_path = skill_path / entrypoint

    if not content_path.exists():
        raise FileNotFoundError(f"Missing skill entrypoint: {content_path}")

    content = content_path.read_text(encoding="utf-8").strip()
    title = skill.get("title", skill["name"])
    return f"## Skill: {title}\n\nSource: {skill['path']}/{entrypoint}\n\n{content}"


def load_skills(skill_names: list[str]) -> str:
    """Return combined Markdown context for selected skill names."""
    registry = load_registry()
    skills = registry_by_name(registry)
    sections: list[str] = []
    missing: list[str] = []

    for name in skill_names:
        skill = skills.get(name)
        if skill is None:
            missing.append(name)
            continue
        trust_level = effective_trust_level(skill)
        if trust_level not in LOADABLE_TRUST_LEVELS:
            raise PermissionError(
                f"Skill {name!r} has trust_level/status {trust_level!r} and is not loadable. "
                "Set trust_level to reviewed, vendor, or local after review."
            )
        sections.append(load_skill_content(skill))

    if missing:
        available = ", ".join(sorted(skills))
        raise KeyError(
            f"Unknown skill(s): {', '.join(missing)}. Available skills: {available}"
        )

    return "\n\n---\n\n".join(sections)
