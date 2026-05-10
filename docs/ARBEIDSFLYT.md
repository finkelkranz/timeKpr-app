# Arbeidsflyt: Git, Cursor, VSCode, CLI

## Git-grunnlag

### Første gang med prosjektet

```bash
# Klon prosjektet
git clone https://github.com/Torgeir/timekpr-app.git
cd timekpr-app

# Oppsett virtuelt miljø
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .\.venv\Scripts\activate  # Windows

# Installer avhengigheter
pip install -e ".[dev]"

# Kopier eksempeleksett
cp .env.example .env
```

### Daglig arbeid

```bash
# Se status
 git status

# Legg til endringer
git add -p  # Interaktivt
# eller
git add .   # Alle endringer

# Commit med god melding
git commit -m "beskrivende melding"

# Push til GitHub
git push
```

## Flere Git-kontoer eller remotes

- **Én konto, én remote**: Vanlig `git remote add origin <url>`.
- **Annen konto eller arbeid/privat**: Bruk **forskjellige SSH-nøkler** og `~/.ssh/config` med `Host github-work` / `Host github-personal` som peker til ulike `IdentityFile` og `HostName github.com`. Klon med den URL-en som matcher riktig host-alias.
- **Flere remotes i samme repo**: `git remote add upstream ...` og `git remote add personal ...`; push/pull med `git push personal branch`.

## Cursor

- Åpne prosjektmappen i Cursor på Windows, Linux eller macOS.
- `AGENTS.md` gir kontekst til AI-funksjoner i dette repoet.

## VSCode med utvidelser

- Installer Python-utvidelse og Pytest-utvidelse.
- Kopier `.vscode/settings.json.example` til `.vscode/settings.json` og tilpass Python-sti:
  - Linux/macOS: `"python.pythonPath": ".venv/bin/python"`
  - Windows: `"python.pythonPath": ".venv\Scripts\python.exe"`

## Ren CLI

```text
git status
git add -p
git commit -m "beskrivende melding"
git push
pytest
```

## Når endringer skjer på GitHub (ikke på din maskin)

Eksempler: du **merger en pull request** i nettleseren, **Dependabot** får merged inn, eller en medarbeider pusher.

Da er **GitHub** oppdatert, men mappen din er det ikke før du henter endringene:

```text
git pull
```

Hvis merge endret **avhengigheter** (`pyproject.toml`), oppdater det virtuelle miljøet etterpå:

```text
pip install -e ".[dev]"
```

Kjør gjerne `pytest` eller `./scripts/check.sh` etter større hopp i biblioteker.

## Dropbox / synk

Unngå å dele `.venv` mellom maskiner via Dropbox — gjenskape med `python -m venv .venv` og `pip install -e ".[dev]"` per maskin for færre rare feil.
