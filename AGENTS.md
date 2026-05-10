# Retningslinjer for AI-agenter og assistenter

Dette prosjektet er **timekpr-app**: en web-app for å administrere timekpr-skjermtidskontroll.

## Konvensjoner

- **Språk**: Python 3.11+, `src/`-layout, pakke `timekpr_app`
- **Lint/format**: `ruff` (sjekk med `ruff check src tests`)
- **Tester**: `pytest`; nye funksjoner bør ha tester under `tests/`
- **Hemmeligheter**: Kun via miljøvariabler eller plattformens secret store — se `docs/HEMMELIGHETER.md`

## Nyttige kommandoer

```text
scripts/setup-dev.sh
pip install -e ".[dev]"
ruff check src tests
pytest
python -c "from timekpr_app.api.main import app; print('OK')"
```

## Hva du ikke skal gjøre

- Committe `.env`, API-nøkler, eller tokens
- Slette sikkerhets- eller CI-filer uten at brukeren ber om det
- Endre `src/timekpr_app/` struktur uten å oppdatere tester

## Prosjekt-spesifikke notater

- Appen trenger **root-tilgang** for å lese timekpr-filer under `/var/lib/timekpr/`
- Backend: FastAPI på port 8000 (konfigurerbart)
- Frontend: React/Vite på port 5173 (konfigurerbart)
- Database: SQLite i `/var/lib/timekpr-app-data/stats.db`
- D-Bus: Kommuniserer med `com.timekpr.server` via system bus
