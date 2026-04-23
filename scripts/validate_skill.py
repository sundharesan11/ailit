#!/usr/bin/env python3
"""Compatibility wrapper for aios validate."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aios.registry import validate_skill  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate one Engineering Brain skill directory."
    )
    parser.add_argument("skill_path", help="Skill directory to validate.")
    args = parser.parse_args()

    skill_path = Path(args.skill_path)
    if not skill_path.is_absolute():
        skill_path = ROOT / skill_path

    errors = validate_skill(skill_path)
    if errors:
        print("Skill validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    try:
        display_path = skill_path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        display_path = str(skill_path)
    print(f"Skill validation passed: {display_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
