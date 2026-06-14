#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -x .venv/bin/python ]]; then
  echo "Virtual environment is missing. Run first: ./scripts/setup_linux.sh"
  exit 1
fi

if [[ -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ]]; then
  echo "No graphical session was detected (DISPLAY/WAYLAND_DISPLAY)."
  echo "Run this command from within your Linux desktop session."
  exit 1
fi

exec .venv/bin/python -m chef_pricing.main --sample-workspace "$@"
