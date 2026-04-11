# Retningslinjer for AI-agenter og assistenter

Dette repoet er et **mal-prosjekt**: hold endringer fokuserte, dokumenter nye avhengigheter, og ikke legg hemmeligheter i kode eller commits.

## Konvensjoner

- **Språk**: Python 3.11+, `src/`-layout, pakke `mal_prosjekt` (bytt navn når du kopierer til eget prosjekt).
- **Lint/format**: `ruff` (sjekk med `ruff check src tests`).
- **Tester**: `pytest`; nye funksjoner bør ha tester under `tests/`.
- **Hemmeligheter**: Kun via miljøvariabler eller plattformens secret store — se `docs/HEMMELIGHETER.md`.

## Nyttige kommandoer

```text
scripts\setup-dev.ps1
pip install -e ".[dev]"
ruff check src tests
pytest
mal-demo --version
```

Nytt prosjekt fra mal (etter klon): `scripts\new-from-mal.ps1` / `python scripts/new_from_mal.py` — se `docs/NY-PROSJEKT-FRA-MAL.md`.

## Hva du ikke skal gjøre

- Committe `.env`, API-nøkler, eller tokens.
- Slette sikkerhets- eller CI-filer uten at brukeren ber om det.
