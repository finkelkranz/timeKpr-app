"""Tester for CLI."""

from unittest.mock import patch

from mal_prosjekt.cli import main


def test_cli_version(capsys: object) -> None:
    with patch("sys.argv", ["mal-demo", "--version"]):
        main()
    captured = capsys.readouterr()
    assert captured.out.strip()
