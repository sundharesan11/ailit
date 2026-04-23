#!/usr/bin/env python3
"""Compatibility wrapper for aios index."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aios.registry import index_skills  # noqa: E402


def main() -> int:
    count = index_skills()
    print(f"Indexed {count} skill(s) into registry/skills.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
