#!/usr/bin/env python3
"""Bytt ut mal-navn (mal-prosjekt / mal_prosjekt / mal-demo) med egne navn. Kjør fra prosjektrot."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "htmlcov"}
TEXT_SUFFIXES = {".py", ".toml", ".md", ".yml", ".yaml", ".ps1", ".sh", ".txt"}
EXACT_NAMES = {"Dockerfile", "LICENSE"}


def is_text_file(path: Path) -> bool:
    if path.name in EXACT_NAMES:
        return True
    return path.suffix.lower() in TEXT_SUFFIXES


def main() -> None:
    parser = argparse.ArgumentParser(description="Gi prosjekt klonet fra mal nye navn.")
    parser.add_argument("--pip-name", required=True, help='f.eks. "mitt-prosjekt" (kebab)')
    parser.add_argument("--package-name", required=True, help='f.eks. "mitt_prosjekt" (Python-modul)')
    parser.add_argument("--cli-name", required=True, help='f.eks. "mitt-app" (kommandolinje)')
    args = parser.parse_args()

    pip_name: str = args.pip_name
    package_name: str = args.package_name
    cli_name: str = args.cli_name

    if not re.match(r"^[a-z][a-z0-9_]*$", package_name):
        print("package-name må være gyldig Python-modulnavn (små bokstaver, tall, understrek).", file=sys.stderr)
        sys.exit(1)

    root = Path(__file__).resolve().parent.parent
    pyproject = root / "pyproject.toml"
    old_pkg = root / "src" / "mal_prosjekt"
    if not pyproject.is_file() or "mal-prosjekt" not in pyproject.read_text(encoding="utf-8"):
        print("Forventer mal-prosjekt i pyproject.toml. Er du i prosjektroten?", file=sys.stderr)
        sys.exit(1)
    if not old_pkg.is_dir():
        print(f"Fant ikke {old_pkg}. Er malen allerede omdøpt?", file=sys.stderr)
        sys.exit(1)

    new_pkg = root / "src" / package_name
    if new_pkg.exists():
        print(f"Mappe finnes allerede: {new_pkg}", file=sys.stderr)
        sys.exit(1)

    shutil.move(str(old_pkg), str(new_pkg))

    def replace_in_content(s: str) -> str:
        s = s.replace("mal_prosjekt", package_name)
        s = s.replace("mal-prosjekt", pip_name)
        s = s.replace("mal-demo", cli_name)
        return s

    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if path.is_dir():
            continue
        if not is_text_file(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        new_text = replace_in_content(text)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8", newline="\n")

    print("Ferdig. Kjør: pip install -e '.[dev]' (eller scripts/setup-dev) og deretter pytest / scripts/check.")


if __name__ == "__main__":
    main()
