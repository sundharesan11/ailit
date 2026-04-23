#!/usr/bin/env python3
"""Compatibility wrapper for aios load."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aios.loader import load_skills  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Load skill context by skill name.")
    parser.add_argument("skill_names", nargs="+", help="Skill names to load.")
    args = parser.parse_args()

    print(load_skills(args.skill_names))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
