"""Skill matching runtime and shared scoring primitives."""

from __future__ import annotations

import json
import re
from typing import Any

from .registry import load_registry


TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
AUTO_LOAD_TRUST_LEVELS = {"local", "reviewed", "vendor"}

# Request-side stopwords only. Skill-side tags, keywords, and aliases are
# never filtered, so curated terms like "landing" or "page" keep matching.
STOPWORDS = frozenset(
    {
        # articles, pronouns, prepositions, conjunctions, auxiliaries
        "a", "an", "the", "my", "our", "your", "his", "her", "its", "their",
        "i", "we", "you", "it", "me", "us", "them", "this", "that", "these",
        "those", "for", "to", "of", "in", "on", "at", "by", "with", "from",
        "into", "onto", "and", "or", "but", "so", "as", "if", "then", "than",
        "is", "are", "was", "were", "be", "been", "being", "do", "does",
        "did", "doing", "have", "has", "had", "can", "could", "should",
        "would", "will", "shall", "may", "might", "must",
        # generic task verbs and filler that appear in nearly every request
        "use", "using", "used", "make", "making", "made", "build", "building",
        "create", "creating", "created", "add", "adding", "write", "writing",
        "implement", "implementing", "improve", "improving", "get", "getting",
        "set", "setting", "up", "out", "all", "any", "some", "new", "want",
        "wants", "need", "needs", "help", "please", "also", "when", "what",
        "how", "where", "which", "who", "why", "user", "users", "task",
        "work", "project", "thing", "things", "personal",
    }
)

# Description hits are the weakest signal: verbose external skill
# descriptions are full of generic trigger phrases, so their total
# contribution per skill is capped.
DESCRIPTION_HIT_SCORE = 1
DESCRIPTION_SCORE_CAP = 3

# Minimum integral score a skill needs to count as relevant. Deliberately
# set just above DESCRIPTION_SCORE_CAP so description-only overlap can
# never clear the threshold on its own; at least one name, tag, keyword,
# alias, or title hit is required.
MIN_MATCH_SCORE = 4


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
    return set(TOKEN_PATTERN.findall(text.lower().replace("_", " ").replace("-", " ")))


def request_tokens_for(text: str) -> set[str]:
    """Return request tokens with stopwords removed."""
    return {token for token in tokenize(text) if token not in STOPWORDS}


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
    request_tokens = request_tokens_for(user_request)
    if not request_tokens:
        return 0, []

    name = str(skill.get("name", "")).lower()
    title = str(skill.get("title", "")).lower()
    description = str(skill.get("description", "")).lower()
    tags = {str(tag).lower() for tag in skill.get("tags", [])}
    keywords = {str(keyword).lower() for keyword in skill.get("keywords", [])}

    name_tokens = tokenize(name)
    title_tokens = tokenize(title)
    description_tokens = tokenize(description)
    alias_tokens = tokenize(" ".join(str(alias) for alias in skill.get("aliases", [])))

    searchable_tokens = tokenize(skill_search_text(skill))
    matched_terms = sorted(request_tokens & searchable_tokens)
    score = 0

    normalized_request = " ".join(sorted(request_tokens))
    normalized_name = " ".join(sorted(name_tokens))

    if name and name.replace("_", " ") in user_request.lower():
        score += 20
    if normalized_name and normalized_name == normalized_request:
        score += 15

    description_score = 0
    for term in request_tokens:
        if term in name_tokens:
            score += 6
        if term in tags:
            score += 5
        if term in alias_tokens:
            score += 5
        if term in keywords:
            score += 4
        if term in title_tokens:
            score += 3
        if term in description_tokens:
            description_score += DESCRIPTION_HIT_SCORE
    score += min(description_score, DESCRIPTION_SCORE_CAP)

    return score, matched_terms


def match_skills(
    user_request: str,
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Return relevant skills ranked by score.

    Skills scoring below MIN_MATCH_SCORE are excluded entirely, so an
    unrelated request returns fewer (or zero) matches instead of the
    highest-scoring noise.
    """
    registry = registry if registry is not None else load_registry()
    matches: list[dict[str, Any]] = []

    for skill in registry.get("skills", []):
        trust_level = effective_trust_level(skill)
        if trust_level not in AUTO_LOAD_TRUST_LEVELS:
            continue

        score, matched_terms = score_skill(user_request, skill)
        if score < MIN_MATCH_SCORE:
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
