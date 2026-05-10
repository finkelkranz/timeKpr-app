# For deg som har enkel kode-bakgrunn

Denne teksten er skrevet for deg som kjenner litt grunnleggende programmering, men som tenker å bruke dette prosjektet.

## Hva er timekpr-app?

Dette er en **web-app** for å administrere [timekpr](https://launchpad.net/timekpr) skjermtidskontroll på delt Linux-maskin. Den lar administratorer:
- Se brukerstatistikk (gjenværende tid, forbruk)
- Endre tid for brukere
- Konfigurer timekpr-innstillinger
- Se historisk data

## Hva du trenger å installere

1. **Python 3.11 eller nyere** — fra [python.org](https://www.python.org/downloads/). På Windows: husk å krysse av for «Add Python to PATH».
2. **Git** — fra [git-scm.com](https://git-scm.com/download/win) (Windows). Gir kommandoen `git` i terminal.
3. **Node.js 18+** — for frontend (React/Vite). Fra [nodejs.org](https://nodejs.org/).
4. (Valgfritt) **Cursor** eller **VSCode** — editor med støtte for Python og Git.

## Første gang: klone prosjektet

Når Git er installert, åpne en terminal og kjør:

```bash
git clone https://github.com/Torgeir/timekpr-app.git
cd timekpr-app
```

## Oppsett av utviklingsmiljø

```bash
# Opprett virtuelt Python-miljø
python3 -m venv .venv

# Aktiver miljøet (Linux/macOS)
source .venv/bin/activate

# Aktiver miljøet (Windows)
.\.venv\Scripts\activate

# Installer avhengigheter
pip install -e ".[dev]"

# Kopier eksempeleksett
cp .env.example .env
# Rediger .env med dine innstillinger
```

## Kjør applikasjonen

### Backend (server)

```bash
./run-server.sh
```

Serveren starter på `http://localhost:8000`. API-dokumentasjon finner du på `http://localhost:8000/docs`.

### Frontend (web-grensesnitt)

```bash
./run-frontend.sh
```

Frontend kjører på `http://localhost:5173`.

## Grunnleggende Git-kommander

| Komando | Beskrivelse |
|---------|-------------|
| `git status` | Se hvilke filer som er endret |
| `git add <fil>` | Legg til fil for commit |
| `git add .` | Legg til alle endrede filer |
| `git commit -m "melding"` | Lagre endringer lokalt |
| `git push` | Send endringer til GitHub |
| `git pull` | Hent endringer fra GitHub |
| `git log --oneline` | Se commit-historikk |

## Kjør tester

```bash
# Alle tester
pytest

# Med dekning (coverage)
pytest --cov=timekpr_app --cov-report=term-missing

# Enkle sjekker (lint + type + test)
./scripts/check.sh
```

## Nyttig å vite

- **Kildekode** ligger i `src/timekpr_app/`
- **Tester** ligger i `tests/`
- **Frontend** ligger i `frontend/`
- **Dokumentasjon** ligger i `docs/`
- **`.env`** filen er i `.gitignore` — aldri commit den!
