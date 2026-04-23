"""Skill matching runtime."""

from __future__ import annotations

import json
import re
from typing import Any

from .registry import load_registry


TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
AUTO_LOAD_TRUST_LEVELS = {"local", "reviewed", "vendor"}


def effective_trust_level(skill: dict[str, Any]) -> str:
    """Return the trust level used for matching."""
    if "trust_level" in skill:
        return str(skill["trust_level"])
    status = str(skill.get("status", "local"))
    if status in {"untrusted", "disabled"}:
        return status
    return "local"


def tokenize(text: str) -> set[str]:
    """Return normalized keyword tokens from text."""
    return set(TOKEN_PATTERN.findall(text.lower().replace("_", " ")))


def skill_search_text(skill: dict[str, Any]) -> str:
    """Return a searchable text blob for a skill."""
    parts = [
        str(skill.get("name", "")),
        str(skill.get("title", "")),
        str(skill.get("description", "")),
        " ".join(skill.get("tags", [])),
        " ".join(skill.get("aliases", [])),
        " ".join(skill.get("keywords", [])),
    ]
    return " ".join(parts)


def score_skill(user_request: str, skill: dict[str, Any]) -> tuple[int, list[str]]:
    """Score a skill for a user request and return matched terms."""
    request_tokens = tokenize(user_request)
    if not request_tokens:
        return 0, []

    name = str(skill.get("name", "")).lower()
    title = str(skill.get("title", "")).lower()
    description = str(skill.get("description", "")).lower()
    tags = {str(tag).lower() for tag in skill.get("tags", [])}
    aliases = {str(alias).lower() for alias in skill.get("aliases", [])}
    keywords = {str(keyword).lower() for keyword in skill.get("keywords", [])}

    searchable_tokens = tokenize(skill_search_text(skill))
    matched_terms = sorted(request_tokens & searchable_tokens)
    score = 0

    normalized_request = " ".join(sorted(request_tokens))
    normalized_name = " ".join(sorted(tokenize(name)))

    if name and name.replace("_", " ") in user_request.lower():
        score += 20
    if normalized_name and normalized_name == normalized_request:
        score += 15

    for term in request_tokens:
        if term in tokenize(name):
            score += 6
        if term in tags:
            score += 5
        if term in aliases:
            score += 5
        if term in keywords:
            score += 4
        if term in tokenize(title):
            score += 3
        if term in tokenize(description):
            score += 1

    return score, matched_terms


def match_skills(user_request: str) -> list[dict[str, Any]]:
    """Return skills ranked by relevance to a user request."""
    registry = load_registry()
    matches: list[dict[str, Any]] = []

    for skill in registry.get("skills", []):
        trust_level = effective_trust_level(skill)
        if trust_level not in AUTO_LOAD_TRUST_LEVELS:
            continue

        score, matched_terms = score_skill(user_request, skill)
        if score <= 0:
            continue

        match = dict(skill)
        match["score"] = score
        match["matched_terms"] = matched_terms
        matches.append(match)

    return sorted(
        matches,
        key=lambda item: (-int(item["score"]), str(item.get("name", ""))),
    )


def matches_as_json(user_request: str, limit: int = 5) -> str:
    """Return matched skills as formatted JSON."""
    matches = match_skills(user_request)
    if limit > 0:
        matches = matches[:limit]
    return json.dumps(matches, indent=2, ensure_ascii=False)
