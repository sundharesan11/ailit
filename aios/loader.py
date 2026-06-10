"""Skill loading runtime."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .paths import ROOT
from .registry import load_registry, registry_by_name


LOADABLE_TRUST_LEVELS = {"local", "reviewed", "vendor"}

# Cap applied when skill content is inlined into assembled context.
# Mirrors MAX_SOLUTION_CHARS in solution_loader. Direct `aios load`
# calls stay untruncated so the load-on-demand escape hatch always
# returns full content.
MAX_SKILL_CHARS = 2200


def effective_trust_level(skill: dict[str, Any]) -> str:
    """Return the trust level used for loading."""
    if "trust_level" in skill:
        return str(skill["trust_level"])
    status = str(skill.get("status", "local"))
    if status in {"untrusted", "disabled"}:
        return status
    return "local"


def load_skill_content(skill: dict[str, Any], max_chars: int | None = None) -> str:
    """Load one skill's entrypoint content, optionally truncated."""
    if skill.get("source_path"):
        skill_path = Path(skill["source_path"]).expanduser().resolve()
    else:
        skill_path = ROOT / str(skill["path"])
    entrypoint = skill.get("entrypoint", "skill.md")
    content_path = skill_path / entrypoint

    if not content_path.exists():
        raise FileNotFoundError(f"Missing skill entrypoint: {content_path}")

    content = content_path.read_text(encoding="utf-8").strip()
    if max_chars is not None and len(content) > max_chars:
        content = (
            content[: max_chars - 4].rstrip()
            + "\n..."
            + f"\n\n(Truncated. Full content: aios load {skill['name']})"
        )
    title = skill.get("title", skill["name"])
    return f"## Skill: {title}\n\nSource: {skill['path']}/{entrypoint}\n\n{content}"


def load_skills(
    skill_names: list[str],
    max_chars: int | None = None,
    registry: dict[str, Any] | None = None,
) -> str:
    """Return combined Markdown context for selected skill names.

    Content is untruncated by default; context assembly passes a cap.
    """
    registry = registry if registry is not None else load_registry()
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
        sections.append(load_skill_content(skill, max_chars))

    if missing:
        raise KeyError(
            f"Unknown skill(s): {', '.join(missing)}. The skill may have been "
            "renamed or uninstalled since it was matched. Run `aios list-skills "
            f"--query {missing[0]}` to find the current name."
        )

    return "\n\n---\n\n".join(sections)
