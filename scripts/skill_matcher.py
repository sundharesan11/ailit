#!/usr/bin/env python3
"""Compatibility wrapper for aios match."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aios.matcher import match_skills  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Match a request to relevant skills.")
    parser.add_argument("request", help="User request to match against the skill registry.")
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum number of matches to print. Use 0 for all matches.",
    )
    args = parser.parse_args()

    matches = match_skills(args.request)
    if args.limit > 0:
        matches = matches[: args.limit]

    print(json.dumps(matches, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
