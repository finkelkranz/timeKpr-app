# Mal-prosjekt

Et **startpunkt** for egne prosjekter: du kopierer eller kloner mappen, legger inn din egen kode, og beholder verktøy for testing og sikkerhet.

**Er du ny på Python eller Git?** Les [docs/BEGINNER.md](docs/BEGINNER.md) først — den forklarer dette i enklere språk og sammenligner med det du kanskje kjenner fra C, Java og PHP.

**Skal du lage et helt nytt prosjekt fra malen** (ny maskin, ny jobb-PC, to måneder senere)? Les [docs/NY-PROSJEKT-FRA-MAL.md](docs/NY-PROSJEKT-FRA-MAL.md) — der står klon/template, **automatisert navnebytte** (`scripts/new-from-mal`) og sjekklisten «minste mulig manuelt».

## Git-repo: ja — slik gjør du

Kildekoden er **laget for å ligge i et vanlig Git-repository** (versjonskontroll), slik at du kan ta sikkerhetskopi, jobbe på flere maskiner og dele med andre.

- **Første gang på din maskin:** installer [Git](https://git-scm.com/downloads), stå i denne mappen og kjør `scripts\init-git.ps1` (Windows) eller `scripts/init-git.sh` (Linux/macOS). Da opprettes et lokalt repo med første commit.
- **På GitHub:** opprett et nytt repo og følg [docs/BEGINNER.md](docs/BEGINNER.md) for å koble `git push`. Da kan **andre** hente alt med `git clone` — det er den vanlige måten å gjøre et eksempel-prosjekt «tilgjengelig som git-repo» på.

Uten Git er det fortsatt bare filer i en mappe; med Git og eventuelt GitHub blir det et **offisielt** eksempel andre kan kopiere likt hver gang.

## Hva som følger med

| Område | Innhold (enkelt forklart) |
|--------|---------------------------|
| Kode | Python 3.11+, programfiler i `src/`, liten demo-kommando `mal-demo` |
| Tester | Automatiske sjekker som kjører når du kjører `pytest` |
| Kodekvalitet | Verktøyene `ruff` og `mypy` finner skrivefeil og uvaner i koden |
| Hemmeligheter | Passord og nøkler hører ikke inn i Git — se [docs/HEMMELIGHETER.md](docs/HEMMELIGHETER.md) |
| CI | Når du bruker GitHub: tester kjører automatisk når du pusher (se `.github/workflows/`) |
| Sikkerhet | Planlagte sjekker av biblioteker og lekkasjer — [docs/SIKKERHET.md](docs/SIKKERHET.md) |
| Oppdateringer | Forslag til nyere biblioteker (Dependabot); etter merge på GitHub: `git pull` lokalt — [docs/ARBEIDSFLYT.md](docs/ARBEIDSFLYT.md) |
| Kjøring i sky / server | [Dockerfile](Dockerfile) og [docker-compose.yml](docker-compose.yml) som eksempel |
| Før commit (valgfritt) | `pre-commit` kan kjøre sjekker automatisk |

## Kom i gang

### 1. Backend (Python/FastAPI)

```bash
# Opprett virtuelt miljø
python3 -m venv .venv
source .venv/bin/activate

# Installer avhengigheter
pip install fastapi uvicorn pydantic pydantic-settings python-dotenv pyjwt bcrypt python-multipart

# Installer system-avhengigheter for D-Bus
sudo apt update && sudo apt install -y libdbus-1-dev pkg-config
pip install dbus-python

# Kjør serveren
./run-server.sh
```

Serveren starter på `http://localhost:8000` med API-dokumentasjon på `http://localhost:8000/docs`.

### 2. Frontend (React/Vite)

```bash
# Kjør frontend
./run-frontend.sh
# Eller manuelt:
cd frontend
npm run dev
```

Frontend kjører på `http://localhost:5173` og proxyer API-kall til backend.

4. **Git:** Når Git er installert, kjør `scripts\init-git.ps1` eller følg [docs/BEGINNER.md](docs/BEGINNER.md).

5. **Eget prosjekt fra malen:** Se [docs/NY-PROSJEKT-FRA-MAL.md](docs/NY-PROSJEKT-FRA-MAL.md). Kort: klon eller bruk GitHub **Use this template**, kjør `scripts\new-from-mal.ps1` (eller `python scripts/new_from_mal.py ...`) for å bytte `mal-prosjekt` til dine navn, deretter `setup-dev` og `check`.

## Dokumentasjon

| Fil | Tema |
|-----|------|
| [docs/NY-PROSJEKT-FRA-MAL.md](docs/NY-PROSJEKT-FRA-MAL.md) | **Nytt prosjekt fra scratch**, ny maskin, GitHub template |
| [docs/BEGINNER.md](docs/BEGINNER.md) | **Start her** om du er ny på Python/Git |
| [docs/ARKITEKTUR.md](docs/ARKITEKTUR.md) | Mapper og hvordan du utvider |
| [docs/HEMMELIGHETER.md](docs/HEMMELIGHETER.md) | Hemmeligheter uten å sjekke inn passord |
| [docs/ARBEIDSFLYT.md](docs/ARBEIDSFLYT.md) | Git, Cursor, VSCode, flere maskiner |
| [docs/CI-OG-TESTER.md](docs/CI-OG-TESTER.md) | Automatiske tester og GitHub Actions |
| [docs/SIKKERHET.md](docs/SIKKERHET.md) | Sikkerhetsskanning |
| [docs/SYNK-MAL.md](docs/SYNK-MAL.md) | Flytte forbedringer tilbake til malen |
| [AGENTS.md](AGENTS.md) | Retningslinjer for AI-hjelp i Cursor |

## Lisens

MIT — se [LICENSE](LICENSE).
