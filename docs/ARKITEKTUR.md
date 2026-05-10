# Arkitektur

## Mapper og struktur

```
timeKpr-app/
├── src/timekpr_app/          # Hovedapplikasjonen
│   ├── api/                  # FastAPI endpoints
│   │   ├── main.py           # App oppsett, lifespan, routing
│   │   ├── auth.py           # JWT autentiserings-endepunkter
│   │   ├── health.py         # Helse-sjekk endpoint
│   │   ├── stats.py          # Brukerstatistikk endpoints
│   │   ├── config.py         # Konfigurasjons-endepunkter
│   │   └── stats_history.py  # Historisk data endpoints
│   ├── __init__.py           # Pakke init, versjon
│   ├── auth.py               # Passord hashing (bcrypt)
│   ├── config.py             # Instillinger fra miljøvariabler
│   ├── models.py             # Pydantic modeller for request/response
│   ├── timekpr.py            # D-Bus interface til timekprd
│   ├── timekpr_file.py       # Fil-basert leser for timekpr-data
│   ├── timekpr_db.py         # SQLite database for historisk data
│   └── timekpr_mock.py       # Mock interface for testing
├── frontend/                 # React/Vite frontend
│   ├── src/                  # React komponenter
│   └── public/               # Statiske filer
├── tests/                    # Automatiske tester
│   ├── test_api.py           # Enkle API-tester
│   ├── test_api_full.py      # Fullstendige API-tester med mock
│   ├── test_auth.py          # Autentiseringstester
│   ├── test_config.py        # Konfigurasjonstester
│   └── test_timekpr.py       # timekpr modul-tester
├── scripts/                  # Hjelpeskript
│   ├── check.sh              # Full sjekk (lint, type, test)
│   ├── check.ps1             # Full sjekk for Windows
│   └── ...                   # Andre utviklerskript
└── .github/workflows/        # CI/CD workflows
    └── ci.yml                # GitHub Actions workflow
```

## Avhengigheter

### Kjøretid (runtime)
- Python 3.11+
- FastAPI + Uvicorn (web server)
- Pydantic + Pydantic Settings (konfigurasjon)
- dbus-python (D-Bus kommunikasjon)
- PyJWT (JWT token generering/validering)
- bcrypt (passord hashing)
- python-multipart (fil-opplastinger)
- python-dotenv (.env support)

### Utvikling (dev)
- pytest + pytest-cov (testing)
- pytest-asyncio (async test support)
- ruff (linting)
- mypy (type checking)
- httpx (async HTTP client for testing)

## Utvidelse

### Ny modul
1. Lag ny fil i `src/timekpr_app/` (f.eks. `ny_modul.py`)
2. Importer i `__init__.py` om nødvendig
3. Lag tilsvarende test i `tests/test_ny_modul.py`
4. Kjør `pytest` for å verifisere

### Ny API endpoint
1. Lag ny router i `src/timekpr_app/api/` (f.eks. `ny_router.py`)
2. Registrer routeren i `main.py` med `app.include_router()`
3. Lag tester i `tests/`

### Ny timekpr-funksjonalitet
1. Utvid `timekpr.py` (D-Bus) eller `timekpr_file.py` (fil-basert)
2. Lag passende modeller i `models.py`
3. Eksponer via API endpoint

## Docker

`Dockerfile` bygger et runtime-image og starter FastAPI-serveren. I produksjon bør miljøvariabler settes via Docker secrets, Kubernetes secrets, eller orchestreringsverktøy — ikke ved å bake inn `.env`.

Se `docker-compose.yml` for eksempeloppsett.
