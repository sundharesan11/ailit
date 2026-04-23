"""Shared filesystem paths for the AI OS runtime."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STANDARDS_DIR = ROOT / "standards"
SKILLS_DIR = ROOT / "skills"
REGISTRY_DIR = ROOT / "registry"
REGISTRY_PATH = REGISTRY_DIR / "skills.json"
PLUGINS_DIR = ROOT / "plugins"
PLUGIN_REGISTRY_PATH = REGISTRY_DIR / "plugins.json"
PROVIDER_REGISTRY_PATH = REGISTRY_DIR / "providers.json"
