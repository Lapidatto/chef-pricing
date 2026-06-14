#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "This script is intended for Linux."
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 was not found."
  exit 1
fi

PYTHON_VERSION="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
if ! python3 -c 'import sys; raise SystemExit(sys.version_info < (3, 12))'; then
  echo "Python 3.12 or later is required. Current version: $PYTHON_VERSION"
  exit 1
fi

if [[ ! -x .venv/bin/python ]] || ! .venv/bin/python -m pip --version >/dev/null 2>&1; then
  rm -rf .venv
  if ! python3 -m venv .venv 2>/dev/null; then
    echo "python3-venv is not installed; using virtualenv as a local fallback."
    python3 -m pip install --user --break-system-packages "virtualenv>=20.26,<21"
    python3 -m virtualenv .venv
  fi
fi

.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e .
.venv/bin/python -m pip install "pytest>=8.2,<10"

if [[ ! -f sample_workspace/data/ingredients.csv ]]; then
  .venv/bin/python scripts/create_sample_workspace.py sample_workspace
fi

.venv/bin/python -m pytest

cat <<EOF

Linux environment prepared successfully.

Run the application:
  ./scripts/run_linux.sh

Or run it manually:
  source .venv/bin/activate
  python -m chef_pricing.main --sample-workspace
EOF
