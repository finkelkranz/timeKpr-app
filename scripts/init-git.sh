#!/usr/bin/env bash
# Oppretter lokalt Git-repo (første gang). Krever git.
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v git >/dev/null 2>&1; then
  echo "Installer git og kjør skriptet igjen." >&2
  exit 1
fi

if [ -d .git ]; then
  echo "Det finnes allerede en .git-mappe her. Ingen endring."
  exit 0
fi

git init
git add .
git commit -m "Første versjon av mal-prosjekt"
echo "Ferdig: lokalt Git-repo opprettet. Neste steg: docs/BEGINNER.md"
