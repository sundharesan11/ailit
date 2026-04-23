#!/usr/bin/env python3
"""Compatibility wrapper for aios build."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aios.context_builder import build_context  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an AI coding prompt.")
    parser.add_argument("--task", required=True, help="User task to build context for.")
    parser.add_argument(
        "--project",
        default=None,
        help="Optional project root containing ai/spec.md, ai/design.md, ai/context.md.",
    )
    parser.add_argument(
        "--skill-limit",
        type=int,
        default=5,
        help="Maximum number of matched skills to load. Use 0 for all matches.",
    )
    parser.add_argument(
        "--tool",
        default="universal",
        help="Prompt adapter to use. Defaults to universal.",
    )
    args = parser.parse_args()

    print(build_context(args.task, args.project, args.skill_limit, args.tool))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
