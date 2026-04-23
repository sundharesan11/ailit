"""Engineering standards loading."""

from __future__ import annotations

from .paths import STANDARDS_DIR


def load_standards() -> str:
    """Load all engineering standards as Markdown context."""
    sections: list[str] = []
    for path in sorted(STANDARDS_DIR.glob("*.md")):
        sections.append(
            f"## Standard: {path.stem}\n\nSource: standards/{path.name}\n\n"
            f"{path.read_text(encoding='utf-8').strip()}"
        )
    return "\n\n---\n\n".join(sections)
