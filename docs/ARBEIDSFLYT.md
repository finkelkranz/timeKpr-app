# Arbeidsflyt: Git, Cursor, VSCode, CLI

## Flere Git-kontoer eller remotes

- **Én konto, én remote**: Vanlig `git remote add origin <url>`.
- **Annen konto eller arbeid/privat**: Bruk **forskjellige SSH-nøkler** og `~/.ssh/config` med `Host github-work` / `Host github-personal` som peker til ulike `IdentityFile` og `HostName github.com`. Klon med den URL-en som matcher riktig host-alias.
- **Flere remotes i samme repo**: `git remote add upstream ...` og `git remote add personal ...`; push/pull med `git push personal branch`.

## Cursor

- Åpne prosjektmappen i Cursor på Windows, Linux eller macOS — samme filer som i VSCode.
- Cursor Web: synkroniser repo via GitHub/GitLab slik plattformen krever; hemmeligheter skal ikke ligge i repoet.
- `AGENTS.md` gir kontekst til AI-funksjoner i dette repoet.

## VSCode med Mistral, GitHub Copilot eller annet

- Installer utvidelser som vanlig; dette repoet er vanlig Python/tekst uten spesielle krav.
- Kopier `.vscode/settings.json.example` til `.vscode/settings.json` og tilpass Python-sti (Linux/macOS: ofte `.venv/bin/python`).

## Ren CLI

```text
git status
git add -p
git commit -m "beskrivende melding"
git push
pip install -e ".[dev]"
pytest
```

## Når endringer skjer på GitHub (ikke på din maskin)

Eksempler: du **merger en pull request** i nettleseren, **Dependabot** får merged inn, eller en medarbeider pusher.

Da er **GitHub** oppdatert, men mappen din er det ikke før du henter endringene:

```text
git pull
```

Hvis merge endret **avhengigheter** (`pyproject.toml` eller tilsvarende), oppdater det virtuelle miljøet etterpå:

```text
pip install -e ".[dev]"
```

Kjør gjerne `pytest` etter større hopp i biblioteker. Konflikter mellom det du har lokalt og det på GitHub løses som vanlig i Git (commit eller stash lokalt før `pull`, eller løs merge-konflikter hvis Git ber om det).

## Dropbox / synk

Repoet ligger under Dropbox i ditt oppsett. Unngå å dele `.venv` mellom maskiner via Dropbox — gjenskape med `python -m venv .venv` og `pip install -e ".[dev]"` per maskin for færre rare feil.
