#!/usr/bin/env bash
# Eksempel: ./scripts/new-from-mal.sh mitt-prosjekt mitt_prosjekt mitt-app
set -euo pipefail
cd "$(dirname "$0")/.."
if [ "$#" -ne 3 ]; then
  echo "Bruk: $0 <pip-navn-kebab> <pakke_snake_case> <cli-navn>" >&2
  exit 1
fi
exec python scripts/new_from_mal.py --pip-name "$1" --package-name "$2" --cli-name "$3"
