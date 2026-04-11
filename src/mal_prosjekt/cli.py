"""Enkel CLI — erstatt eller utvid etter behov."""

from __future__ import annotations

import argparse

from mal_prosjekt import __version__
from mal_prosjekt.config import get_app_env


def main() -> None:
    parser = argparse.ArgumentParser(description="Mal-prosjekt demo-CLI")
    parser.add_argument("--version", action="store_true", help="Vis versjon")
    args = parser.parse_args()
    if args.version:
        print(__version__)
        return
    print(f"Mal-prosjekt kjører (miljø: {get_app_env()}). Bruk --help for valg.")


if __name__ == "__main__":
    main()
