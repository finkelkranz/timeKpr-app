#!/usr/bin/env bash
# Oppretter .venv og installerer prosjektet med dev-avhengigheter.
set -euo pipefail
cd "$(dirname "$0")/.."
if ! command -v python3 >/dev/null 2>&1; then
  echo "Installer Python 3.11+ (python3)." >&2
  exit 1
fi
if [ ! -d .venv ]; then
  echo "Oppretter .venv ..."
  python3 -m venv .venv
fi
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/pip install -e ".[dev]"
echo ""
echo "Ferdig. Aktiver: source .venv/bin/activate"
