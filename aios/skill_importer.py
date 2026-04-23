"""Import external skills into the Engineering Brain."""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .paths import ROOT, SKILLS_DIR
from .registry import index_skills, validate_skill


TRUST_LEVELS = ("local", "reviewed", "vendor", "untrusted", "disabled")
AUTO_LOAD_TRUST_LEVELS = {"local", "reviewed", "vendor"}


@dataclass(frozen=True)
class ImportResult:
    """Result of importing a skill."""

    skill_name: str
    destination: Path
    trust_level: str
    indexed_count: int
    validation_errors: list[str]
    overwritten: bool


@dataclass(frozen=True)
class TrustUpdateResult:
    """Result of updating a skill trust level."""

    skill_name: str
    metadata_path: Path
    old_trust_level: str | None
    new_trust_level: str
    indexed_count: int
    validation_errors: list[str]


def slugify(value: str) -> str:
    """Return a filesystem-safe skill name."""
    slug = re.sub(r"[^a-zA-Z0-9_ -]+", "", value).strip().lower()
    slug = re.sub(r"[\s-]+", "_", slug)
    return slug or "imported_skill"


def read_metadata(source: Path) -> dict[str, Any]:
    """Read source metadata.json when it exists."""
    metadata_path = source / "metadata.json"
    if metadata_path.exists():
        return json.loads(metadata_path.read_text(encoding="utf-8"))
    return {}


def default_title(name: str) -> str:
    """Convert a skill name into a readable title."""
    return " ".join(part.capitalize() for part in name.split("_"))


def normalize_metadata(
    source: Path,
    destination: Path,
    provider: str,
    trust_level: str,
    source_url: str | None,
    name_override: str | None,
) -> dict[str, Any]:
    """Return normalized metadata for an imported skill."""
    metadata = read_metadata(source)
    source_name = name_override or metadata.get("name") or source.name
    name = slugify(str(source_name))

    metadata["name"] = name
    metadata.setdefault("title", default_title(name))
    metadata.setdefault("description", f"Imported skill from {provider}.")
    metadata.setdefault("tags", ["imported", provider])
    metadata.setdefault("version", "0.1.0")
    metadata["status"] = trust_level
    metadata["entrypoint"] = metadata.get("entrypoint", "skill.md")
    metadata["path"] = destination.relative_to(ROOT).as_posix()
    metadata["provider"] = provider
    metadata["trust_level"] = trust_level
    metadata["source"] = metadata.get("source", "imported")
    if source_url:
        metadata["source_url"] = source_url

    return metadata


def ensure_skill_entrypoint(destination: Path, metadata: dict[str, Any]) -> None:
    """Ensure the imported skill has a skill.md entrypoint."""
    entrypoint = metadata.get("entrypoint", "skill.md")
    entrypoint_path = destination / entrypoint
    if entrypoint_path.exists():
        return

    readme_path = destination / "README.md"
    if readme_path.exists():
        shutil.copy2(readme_path, entrypoint_path)
        return

    title = metadata.get("title", metadata["name"])
    description = metadata.get("description", "")
    entrypoint_path.write_text(
        f"# Skill: {title}\n\n{description}\n",
        encoding="utf-8",
    )


def copy_skill_source(source: Path, destination: Path, overwrite: bool) -> bool:
    """Copy source skill directory to destination and return whether it overwrote."""
    if destination.exists():
        if not overwrite:
            raise FileExistsError(
                f"Destination already exists: {destination}. Use --overwrite to replace it."
            )
        shutil.rmtree(destination)
        overwritten = True
    else:
        overwritten = False

    shutil.copytree(source, destination)
    return overwritten


def import_skill(
    source_path: str | Path,
    provider: str = "community",
    trust_level: str = "untrusted",
    source_url: str | None = None,
    name: str | None = None,
    overwrite: bool = False,
) -> ImportResult:
    """Import an external skill directory into skills/vendor/<provider>/."""
    if trust_level not in TRUST_LEVELS:
        supported = ", ".join(TRUST_LEVELS)
        raise ValueError(f"Unsupported trust level {trust_level!r}. Supported: {supported}")

    source = Path(source_path).expanduser().resolve()
    if not source.exists():
        raise FileNotFoundError(f"Skill source does not exist: {source}")
    if not source.is_dir():
        raise NotADirectoryError(f"Skill source must be a directory: {source}")

    metadata = read_metadata(source)
    skill_name = slugify(str(name or metadata.get("name") or source.name))
    safe_provider = slugify(provider)
    destination = SKILLS_DIR / "vendor" / safe_provider / skill_name

    overwritten = copy_skill_source(source, destination, overwrite)
    normalized = normalize_metadata(
        source=source,
        destination=destination,
        provider=safe_provider,
        trust_level=trust_level,
        source_url=source_url,
        name_override=skill_name,
    )
    ensure_skill_entrypoint(destination, normalized)
    (destination / "metadata.json").write_text(
        json.dumps(normalized, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    validation_errors = validate_skill(destination)
    indexed_count = index_skills()

    return ImportResult(
        skill_name=normalized["name"],
        destination=destination,
        trust_level=trust_level,
        indexed_count=indexed_count,
        validation_errors=validation_errors,
        overwritten=overwritten,
    )


def update_skill_trust(skill_name: str, trust_level: str) -> TrustUpdateResult:
    """Update a skill's trust_level and status metadata."""
    if trust_level not in TRUST_LEVELS:
        supported = ", ".join(TRUST_LEVELS)
        raise ValueError(f"Unsupported trust level {trust_level!r}. Supported: {supported}")

    matches = sorted(SKILLS_DIR.glob(f"**/{skill_name}/metadata.json"))
    if not matches:
        raise FileNotFoundError(f"No skill metadata found for {skill_name!r}")
    if len(matches) > 1:
        paths = ", ".join(path.relative_to(ROOT).as_posix() for path in matches)
        raise ValueError(f"Multiple skill metadata files found for {skill_name!r}: {paths}")

    metadata_path = matches[0]
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    old_trust_level = metadata.get("trust_level", metadata.get("status"))
    metadata["trust_level"] = trust_level
    metadata["status"] = trust_level

    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    validation_errors = validate_skill(metadata_path.parent)
    indexed_count = index_skills()

    return TrustUpdateResult(
        skill_name=metadata["name"],
        metadata_path=metadata_path,
        old_trust_level=old_trust_level,
        new_trust_level=trust_level,
        indexed_count=indexed_count,
        validation_errors=validation_errors,
    )
