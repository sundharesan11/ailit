#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN_DIR="${HOME}/.local/bin"
TARGET="${BIN_DIR}/aios"

mkdir -p "${BIN_DIR}"
ln -sf "${ROOT}/scripts/aios.py" "${TARGET}"
chmod +x "${ROOT}/scripts/aios.py"

echo "Installed aios -> ${TARGET}"
echo "Run: aios --help"
