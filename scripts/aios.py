#!/usr/bin/env python3
"""Cross-project entry point for the AI OS CLI.

This wrapper lets agents call the runtime from any working directory:

    python3 ~/engineering_brain/scripts/aios.py prepare --task "..." --project . --tool codex
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aios.cli import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
