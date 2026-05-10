"""Shared solution registry indexing and validation."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Any

from .paths import ROOT, SOLUTION_REGISTRY_PATH, SOLUTIONS_DIR


REQUIRED_FIELDS = {
    "title",
    "slug",
    "status",
    "owner",
    "created",
    "updated",
    "tags",
    "stack",
    "summary",
    "source_type",
    "source_refs",
    "trust",
    "review_status",
}

ALLOWED_STATUS = {"draft", "active", "deprecated", "archived"}
ALLOWED_TRUST = {"draft", "reviewed", "vendor", "untrusted"}
ALLOWED_REVIEW_STATUS = {"draft", "needs_review", "reviewed"}
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
STALE_AFTER_DAYS = 90
LIST_FIELDS = {"tags", "stack", "source_refs"}


def tokenize_text(text: str) -> list[str]:
    """Return lowercase tokens from text."""
    return TOKEN_PATTERN.findall(text.lower().replace("_", " ").replace("-", " "))


def parse_iso_date(value: str) -> date | None:
    """Parse an ISO date string when valid."""
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def solution_age_days(updated: str) -> int | None:
    """Return age in days from the updated field."""
    parsed = parse_iso_date(updated)
    if parsed is None:
        return None
    return (date.today() - parsed).days


def is_stale(updated: str, stale_after_days: int = STALE_AFTER_DAYS) -> bool:
    """Return whether a solution should be considered stale."""
    age_days = solution_age_days(updated)
    if age_days is None:
        return False
    return age_days > stale_after_days


def markdown_title(text: str) -> str | None:
    """Return the first markdown H1 title, if present."""
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def parse_frontmatter(text: str) -> dict[str, Any]:
    """Parse a small YAML subset used by solution docs."""
    if not text.startswith("---"):
        return {}

    lines = text.splitlines()
    metadata: dict[str, Any] = {}
    current_list_key: str | None = None

    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            break

        if current_list_key and stripped.startswith("- "):
            metadata.setdefault(current_list_key, []).append(stripped[2:].strip().strip("\"'"))
            continue

        if not stripped:
            current_list_key = None
            continue

        if ":" not in line:
            current_list_key = None
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        if not value:
            metadata[key] = [] if key in LIST_FIELDS else ""
            current_list_key = key if key in LIST_FIELDS else None
            continue

        current_list_key = None
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            metadata[key] = [part.strip().strip("\"'") for part in inner.split(",") if part.strip()]
            continue

        metadata[key] = value.strip("\"'")

    return metadata


def solution_doc_paths() -> list[Path]:
    """Return shared solution markdown docs, excluding helper files."""
    paths: list[Path] = []
    for path in sorted(SOLUTIONS_DIR.rglob("*.md")):
        rel = path.relative_to(SOLUTIONS_DIR)
        if rel.name in {"README.md", "_template.md"}:
            continue
        paths.append(path)
    return paths


def normalize_solution(path: Path) -> dict[str, Any]:
    """Convert a solution markdown file into a registry entry."""
    text = path.read_text(encoding="utf-8")
    metadata = parse_frontmatter(text)
    rel_path = path.relative_to(ROOT).as_posix()
    body_title = markdown_title(text)

    title = str(metadata.get("title") or body_title or path.stem.replace("-", " ").title())
    slug = str(metadata.get("slug") or path.stem)
    tags = [str(value) for value in metadata.get("tags", [])]
    stack = [str(value) for value in metadata.get("stack", [])]
    source_refs = [str(value) for value in metadata.get("source_refs", [])]
    summary = str(metadata.get("summary", "")).strip()

    keywords = sorted(
        set(
            tokenize_text(title)
            + tokenize_text(slug)
            + tokenize_text(summary)
            + [token for item in tags + stack for token in tokenize_text(item)]
        )
    )

    return {
        "title": title,
        "slug": slug,
        "path": rel_path,
        "status": str(metadata.get("status", "draft")),
        "owner": str(metadata.get("owner", "")),
        "created": str(metadata.get("created", "")),
        "updated": str(metadata.get("updated", "")),
        "tags": tags,
        "stack": stack,
        "summary": summary,
        "source_type": str(metadata.get("source_type", "")),
        "source_refs": source_refs,
        "trust": str(metadata.get("trust", "draft")),
        "review_status": str(metadata.get("review_status", "draft")),
        "reviewed_by": str(metadata.get("reviewed_by", "")).strip(),
        "last_reviewed": str(metadata.get("last_reviewed", "")).strip(),
        "stale_after_days": STALE_AFTER_DAYS,
        "age_days": solution_age_days(str(metadata.get("updated", ""))),
        "is_stale": is_stale(str(metadata.get("updated", ""))),
        "keywords": keywords,
    }


def build_solution_registry() -> dict[str, Any]:
    """Build the in-memory shared solution registry."""
    solutions = [normalize_solution(path) for path in solution_doc_paths()]
    return {
        "schema_version": "0.1",
        "description": (
            "Shared solution registry for the Personal AI Engineering OS. "
            "Generated by aios.solution_registry."
        ),
        "solution_source": {
            "path": SOLUTIONS_DIR.resolve().as_posix(),
            "solution_count": len(solutions),
            "stale_after_days": STALE_AFTER_DAYS,
        },
        "solutions": sorted(solutions, key=lambda item: item["slug"]),
    }


def _validation_error_text(errors_by_path: dict[str, list[str]]) -> str:
    """Format validation errors for exception messages."""
    lines = ["Solution validation failed:"]
    for path, errors in errors_by_path.items():
        lines.append(f"- {path}")
        for error in errors:
            lines.append(f"  - {error}")
    return "\n".join(lines)


def index_solutions() -> int:
    """Write registry/solutions.json and return the number of indexed solutions."""
    errors_by_path = validate_all_solutions()
    if errors_by_path:
        raise ValueError(_validation_error_text(errors_by_path))
    registry = build_solution_registry()
    SOLUTION_REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SOLUTION_REGISTRY_PATH.write_text(
        json.dumps(registry, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return len(registry["solutions"])


def refresh_solution_registry(registry_path: Path = SOLUTION_REGISTRY_PATH) -> dict[str, Any]:
    """Refresh registry/solutions.json from docs/solutions."""
    errors_by_path = validate_all_solutions()
    if errors_by_path:
        raise ValueError(_validation_error_text(errors_by_path))
    registry = build_solution_registry()
    serialized = json.dumps(registry, indent=2, ensure_ascii=False) + "\n"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    if not registry_path.exists() or registry_path.read_text(encoding="utf-8") != serialized:
        registry_path.write_text(serialized, encoding="utf-8")
    return registry


def load_solution_registry(
    registry_path: Path = SOLUTION_REGISTRY_PATH,
    refresh: bool = True,
) -> dict[str, Any]:
    """Load the solution registry JSON document."""
    if refresh:
        return refresh_solution_registry(registry_path)
    return json.loads(registry_path.read_text(encoding="utf-8"))


def solution_registry_by_slug(registry: dict[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    """Return solutions keyed by slug."""
    registry = registry or load_solution_registry()
    return {solution["slug"]: solution for solution in registry.get("solutions", [])}


def validate_solution(solution_path: Path) -> list[str]:
    """Return a list of validation errors for a shared solution doc."""
    errors: list[str] = []
    solution_path = solution_path.expanduser().resolve()

    if not solution_path.exists():
        return [f"Solution document does not exist: {solution_path}"]
    if not solution_path.is_file():
        return [f"Solution path is not a file: {solution_path}"]

    try:
        rel_path = solution_path.relative_to(ROOT)
    except ValueError:
        return ["Solution document must live inside the AIlit repository."]

    if not rel_path.as_posix().startswith("docs/solutions/"):
        errors.append("Solution document must live under docs/solutions/.")

    text = solution_path.read_text(encoding="utf-8")
    metadata = parse_frontmatter(text)
    if not metadata:
        errors.append("Missing YAML frontmatter.")
        return errors

    missing_fields = sorted(REQUIRED_FIELDS - set(metadata))
    if missing_fields:
        errors.append(f"Missing frontmatter fields: {', '.join(missing_fields)}")

    title = markdown_title(text)
    if not title:
        errors.append("Missing markdown H1 title.")

    if metadata.get("title") and title and str(metadata["title"]).strip() != title.strip():
        errors.append("Frontmatter title and markdown H1 title should match.")

    for field_name in ("tags", "stack", "source_refs"):
        value = metadata.get(field_name)
        if not isinstance(value, list):
            errors.append(f"frontmatter.{field_name} must be a list")

    status = metadata.get("status")
    if status is not None and str(status) not in ALLOWED_STATUS:
        supported = ", ".join(sorted(ALLOWED_STATUS))
        errors.append(f"frontmatter.status must be one of: {supported}")

    trust = metadata.get("trust")
    if trust is not None and str(trust) not in ALLOWED_TRUST:
        supported = ", ".join(sorted(ALLOWED_TRUST))
        errors.append(f"frontmatter.trust must be one of: {supported}")

    review_status = metadata.get("review_status")
    if review_status is not None and str(review_status) not in ALLOWED_REVIEW_STATUS:
        supported = ", ".join(sorted(ALLOWED_REVIEW_STATUS))
        errors.append(f"frontmatter.review_status must be one of: {supported}")

    slug = str(metadata.get("slug", ""))
    expected_slug = solution_path.stem
    if slug and slug != expected_slug:
        errors.append(f"frontmatter.slug should match the filename stem {expected_slug!r}")

    if "summary" in metadata and not str(metadata["summary"]).strip():
        errors.append("frontmatter.summary must not be blank")

    if "owner" in metadata and not str(metadata["owner"]).strip():
        errors.append("frontmatter.owner must not be blank")

    for field_name in ("created", "updated"):
        if field_name in metadata and parse_iso_date(str(metadata[field_name])) is None:
            errors.append(f"frontmatter.{field_name} must be an ISO date like YYYY-MM-DD")

    if "last_reviewed" in metadata and str(metadata.get("last_reviewed", "")).strip():
        if parse_iso_date(str(metadata["last_reviewed"])) is None:
            errors.append("frontmatter.last_reviewed must be an ISO date like YYYY-MM-DD")

    trust_value = str(metadata.get("trust", "draft"))
    review_value = str(metadata.get("review_status", "draft"))
    reviewed_by = str(metadata.get("reviewed_by", "")).strip()
    last_reviewed = str(metadata.get("last_reviewed", "")).strip()

    if trust_value in {"reviewed", "vendor"} and review_value != "reviewed":
        errors.append("frontmatter.review_status must be reviewed when trust is reviewed or vendor")
    if review_value == "reviewed" and not reviewed_by:
        errors.append("frontmatter.reviewed_by is required when review_status is reviewed")
    if review_value == "reviewed" and not last_reviewed:
        errors.append("frontmatter.last_reviewed is required when review_status is reviewed")

    return errors


def validate_all_solutions() -> dict[str, list[str]]:
    """Validate all shared solution docs and return errors by path."""
    results: dict[str, list[str]] = {}
    for path in solution_doc_paths():
        errors = validate_solution(path)
        if errors:
            results[path.relative_to(ROOT).as_posix()] = errors
    return results
