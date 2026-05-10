# timekpr-app

En **web-app** for å administrere [timekpr](https://launchpad.net/timekpr) skjermtidskontroll på delt Linux-maskin. Lar administratorer se brukerstatistikk, endre tid og konfigurere innstillinger via en nettside.

## Funksjonalitet

- **Administrator-panel**: Login med JWT-token for å administrere alle brukere
- **Brukeroversikt**: Se alle konfigurerte timekpr-brukere
- **Tidsstatistikk**: Se gjenværende tid (dag, uke, måned) og forbruk
- **Tidsadministrasjon**: Legg til ekstra tid for brukere
- **Konfigurasjon**: Endre tidgrenser, tillatte dager og timer
- **Historisk data**: SQLite-database lagrer historisk statistikk
- **D-Bus integrasjon**: Direkte kommunikasjon med timekprd
- **Fil-basert lesing**: Pålitelig lesing av timekpr-data fra filer (fallback)

## Arkitektur

```
Backend (Python/FastAPI)
├── src/timekpr_app/
│   ├── api/              # FastAPI endpoints
│   │   ├── main.py       # App setup, lifespan
│   │   ├── auth.py       # JWT authentication
│   │   ├── health.py     # Health check
│   │   ├── stats.py      # User statistics
│   │   ├── config.py     # User configuration
│   │   └── stats_history.py # Historical data
│   ├── auth.py           # Password hashing
│   ├── config.py         # Settings from env vars
│   ├── models.py         # Pydantic models
│   ├── timekpr.py        # D-Bus interface to timekprd
│   ├── timekpr_file.py   # File-based reader
│   ├── timekpr_db.py     # SQLite database
│   └── timekpr_mock.py   # Mock interface for testing
│
Frontend (React/Vite)
├── frontend/
│   ├── src/              # React components
│   └── public/           # Static assets
│
Database
└── /var/lib/timekpr-app-data/stats.db  # SQLite history
```

## Forutsetninger

- Python 3.11+
- Node.js 18+ (for frontend)
- timekpr installert og konfigurerte brukere
- D-Bus system bus (timekprd kjører som system service)
- **Root-tilgang** (for å lese timekpr-filer)

### Systemavhengigheter (Debian/Ubuntu)

```bash
sudo apt update && sudo apt install -y libdbus-1-dev pkg-config
```

## Kom i gang

### 1. Backend (Python/FastAPI)

```bash
# Opprett virtuelt miljø
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .\.venv\Scripts\activate  # Windows

# Installer avhengigheter
pip install -e ".[dev]"

# Kopier eksempeleksett .env
cp .env.example .env
# Rediger .env og sett JWT_SECRET og ADMIN_PASSWORD_HASH

# Kjør serveren
./run-server.sh
# Eller manuelt:
uvicorn timekpr_app.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Serveren starter på `http://localhost:8000` med API-dokumentasjon på `http://localhost:8000/docs`.

### 2. Frontend (React/Vite)

```bash
./run-frontend.sh
# Eller manuelt:
cd frontend
npm install
npm run dev
```

Frontend kjører på `http://localhost:5173` og proxyer API-kall til backend.

### 3. CLI-verktøy

Hjelpeverktøy for debugging og administrasjon:

```bash
# Les timekpr-data (krever sudo)
sudo python3 read_timekpr_data.py
sudo python3 read_timekpr_data.py torgeir  # Spesifikk bruker

# Debug D-Bus-kommunikasjon
sudo python3 debug_dbus.py

# Fiks brukerens tid (krever sudo)
sudo python3 fix_timekpr_time.py
sudo python3 fix_timekpr_time.py torgeir --reset 7200  # Sett 2 timer for torgeir
```

## Miljøvariabler

| Variabel | Beskrivelse | Standardverdi |
|----------|-------------|---------------|
| `APP_ENV` | Miljø (development/production) | `development` |
| `HOST` | Server host | `::` |
| `PORT` | Server port | `8000` |
| `JWT_SECRET` | JWT hemmelighet | `dev-secret-change-in-prod!` |
| `JWT_EXPIRE_MINUTES` | JWT utløpstid (minutter) | `1440` (24 timer) |
| `ADMIN_PASSWORD_HASH` | BCrypt-hash av admin-passord | Hash av `"admin"` |

### Generer nytt admin-passord

```bash
python3 -c "from timekpr_app.auth import hash_password; print(hash_password('mitt_nye_passord'))"
```

## Testing

### Enhetstester

```bash
pytest
pytest --cov=timekpr_app --cov-report=term-missing
```

### Linting og type-sjekk

```bash
ruff check src tests
ruff format --check src tests
mypy src/timekpr_app
```

### Full sjekk (skript)

```bash
./scripts/check.sh  # Linux/macOS
# scripts\check.ps1  # Windows
```

## Docker (valgfritt)

```bash
# Bygg og kjør
docker-compose up --build

# Eller manuelt
docker build -t timekpr-app .
docker run -p 8000:8000 --env-file .env timekpr-app
```

**Merk**: Docker krever root-tilgang for å lese timekpr-filer. Konfigurer volum-mount for `/var/lib/timekpr/`.

## 🔒 Sikkerhet (KRITISK - Les dette før bruk!)

### ⚠️ KRITISKE SIKKERHETSINNSTILLINGER

**Før du kjører appen for første gang, må du:**

1. **Bind til localhost (IKKE 0.0.0.0 eller ::)**
   ```bash
   # I .env filen:
   HOST=127.0.0.1
   ```
   **Hvorfor:** Hvis du bruker `::` eller `0.0.0.0`, er serveren tilgjengelig fra hele nettverket ditt og potensielt internett.

2. **Generer sterkt JWT_SECRET**
   ```bash
   # Kjør dette og lim inn i .env:
   openssl rand -hex 64
   # ELLER
   python3 -c "import secrets; print(secrets.token_urlsafe(64))"
   ```

3. **Sett sterkt admin-passord**
   ```bash
   # Generer hash og lim inn i .env:
   python3 -c "from timekpr_app.auth import hash_password; print(hash_password('ditt_sterke_passord'))"
   ```

4. **Blokker port 8000 eksternt**
   ```bash
   sudo ufw deny 8000/tcp
   ```

5. **Deaktiver port forwarding på routeren**
   - Gå inn i router-admin
   - Sjekk at port 8000 IKKE er forwardet til denne maskinen

### 🔐 Andre sikkerhetsinnstillinger

- **Kjør som root**: Appen trenger root for å lese timekpr-filer under `/var/lib/timekpr/`
- **Token utløp**: Standard er nå 15 minutter (var 24 timer)
- **CORS**: Standard er nå `http://localhost:5173` (var alle localhost-porter)
- **HTTPS**: For ekstern tilgang, bruk reverse proxy (nginx, Caddy) med HTTPS

### 🛡️ Sikkerhets-sjekkliste

| Sjekk | Status | Handling |
|-------|--------|----------|
| Server binder til 127.0.0.1 | ⬜ | `HOST=127.0.0.1` i .env |
| JWT_SECRET er satt | ⬜ | Generer med `openssl rand -hex 64` |
| Admin-passord er satt | ⬜ | Generer hash med `hash_password()` |
| Port 8000 blokkert eksternt | ⬜ | `sudo ufw deny 8000/tcp` |
| Ingen port forwarding | ⬜ | Sjekk router-innstillinger |

## Lisens

MIT — se [LICENSE](LICENSE).
