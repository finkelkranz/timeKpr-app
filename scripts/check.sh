#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m ruff check src tests
python -m ruff format --check src tests
python -m mypy src/timekpr_app
python -m pytest -q
echo "OK: ruff, mypy, pytest"
