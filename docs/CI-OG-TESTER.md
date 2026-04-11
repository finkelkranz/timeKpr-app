# CI/CD og tester

## GitHub Actions

- **`ci.yml`**: Kjører ved push og PR mot `main`/`master`. Utfører `ruff`, `ruff format --check`, `mypy`, `pytest` med dekning på Ubuntu og Windows med Python 3.11 og 3.12.
- **Codecov**: Steget laster opp `coverage.xml` hvis du kobler Codecov til repoet (valgfritt; feil der blokkerer ikke CI).

## Nye tester

1. Legg filer under `tests/`, gjerne `test_<modul>.py`.
2. Bruk funksjonsnavn som starter med `test_`.
3. Kjør lokalt: `pytest` eller `pytest tests/test_foo.py -v`.

## Utvide CI

- Legg steg i `.github/workflows/ci.yml` (f.eks. bygg av Docker-image, publisering til registry).
- Hold hemmeligheter i *GitHub repository secrets*, referert med `${{ secrets.NAVN }}`.

## Dependabot

`.github/dependabot.yml` foreslår ukentlige oppdateringer for pip og GitHub Actions. Juster `schedule` etter behov.

Etter at du **merger** en Dependabot-PR på GitHub: kjør `git pull` lokalt, og `pip install -e ".[dev]"` hvis avhengigheter ble endret — se [ARBEIDSFLYT.md](ARBEIDSFLYT.md).

## Pre-commit

Installer med:

```text
pip install pre-commit
pre-commit install
```

Da kjøres blant annet ruff før hver commit lokalt.
