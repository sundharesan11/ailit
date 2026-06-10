"""Shared solution matching runtime.

Scoring primitives (tokenization, stopwords, caps, threshold) are shared
with the skill matcher in aios.matcher so the two cannot silently drift.
"""

from __future__ import annotations

import json
from typing import Any

from .matcher import (
    DESCRIPTION_HIT_SCORE,
    DESCRIPTION_SCORE_CAP,
    MIN_MATCH_SCORE,
    request_tokens_for,
    tokenize,
)
from .solution_registry import load_solution_registry


AUTO_LOAD_TRUST_LEVELS = {"draft", "reviewed", "vendor"}
AUTO_LOAD_STATUSES = {"draft", "active"}


def effective_trust(solution: dict[str, Any]) -> str:
    """Return the trust level used for solution matching."""
    return str(solution.get("trust", "draft"))


def effective_status(solution: dict[str, Any]) -> str:
    """Return the status used for solution matching."""
    return str(solution.get("status", "draft"))


def solution_search_text(solution: dict[str, Any]) -> str:
    """Return a searchable text blob for a solution."""
    parts = [
        str(solution.get("slug", "")),
        str(solution.get("title", "")),
        str(solution.get("summary", "")),
        " ".join(solution.get("tags", [])),
        " ".join(solution.get("stack", [])),
        " ".join(solution.get("keywords", [])),
        " ".join(solution.get("source_refs", [])),
    ]
    return " ".join(parts)


def score_solution(user_request: str, solution: dict[str, Any]) -> tuple[int, list[str]]:
    """Score a solution for a user request and return matched terms."""
    request_tokens = request_tokens_for(user_request)
    if not request_tokens:
        return 0, []

    slug = str(solution.get("slug", "")).lower()
    title = str(solution.get("title", "")).lower()
    summary = str(solution.get("summary", "")).lower()
    tags = {str(tag).lower() for tag in solution.get("tags", [])}
    stack = {str(tag).lower() for tag in solution.get("stack", [])}
    keywords = {str(keyword).lower() for keyword in solution.get("keywords", [])}

    slug_tokens = tokenize(slug)
    title_tokens = tokenize(title)
    summary_tokens = tokenize(summary)

    searchable_tokens = tokenize(solution_search_text(solution))
    matched_terms = sorted(request_tokens & searchable_tokens)
    score = 0

    normalized_request = " ".join(sorted(request_tokens))
    normalized_slug = " ".join(sorted(slug_tokens))

    if slug and slug.replace("-", " ") in user_request.lower():
        score += 20
    if normalized_slug and normalized_slug == normalized_request:
        score += 15

    summary_score = 0
    for term in request_tokens:
        if term in slug_tokens:
            score += 6
        if term in tags:
            score += 5
        if term in stack:
            score += 5
        if term in keywords:
            score += 4
        if term in title_tokens:
            score += 3
        if term in summary_tokens:
            summary_score += DESCRIPTION_HIT_SCORE
    score += min(summary_score, DESCRIPTION_SCORE_CAP)

    return score, matched_terms


def match_solutions(user_request: str) -> list[dict[str, Any]]:
    """Return relevant shared solutions ranked by score.

    Solutions scoring below MIN_MATCH_SCORE are excluded entirely, matching
    the skill matcher's relevance contract.
    """
    registry = load_solution_registry()
    matches: list[dict[str, Any]] = []

    for solution in registry.get("solutions", []):
        if effective_trust(solution) not in AUTO_LOAD_TRUST_LEVELS:
            continue
        if effective_status(solution) not in AUTO_LOAD_STATUSES:
            continue

        score, matched_terms = score_solution(user_request, solution)
        if score < MIN_MATCH_SCORE:
            continue

        match = dict(solution)
        match["score"] = score
        match["matched_terms"] = matched_terms
        matches.append(match)

    return sorted(matches, key=lambda item: (-int(item["score"]), str(item.get("slug", ""))))


def matches_as_json(user_request: str, limit: int = 5) -> str:
    """Return matched solutions as formatted JSON."""
    matches = match_solutions(user_request)
    if limit > 0:
        matches = matches[:limit]
    return json.dumps(matches, indent=2, ensure_ascii=False)
