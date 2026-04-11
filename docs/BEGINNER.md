# For deg som har enkel kode-bakgrunn, men ikke Python/Git fra før

Denne teksten er skrevet for deg som kjenner litt grunnleggende programmering, men som tenker å vibe-kode deg videre.

## Hva er dette prosjektet?

- **Kildekode** ligger i en mappe, som i gamle dager — bare at strukturen er litt mer ryddig (`src/` for programkode, `tests/` for tester).
- **Python** er et språk som minner om det du kjenner: du skriver tekstfiler, og en **tolk** kjører dem (litt som at PHP kjøres av en server, men her kjører du ofte alt på din egen maskin). Du trenger ikke kompilere som i C/Java for å få noe som fungerer.
- **Git** er et program som lagrer **versjoner** av filene dine: hvem som endret hva, og når. Det er som «angre»-historikk for hele prosjektet, og det gjør det trygt å prøve seg frem.
- **GitHub** (eller annen tjeneste) er et **lagringssted på nett** for Git-repoet ditt. Da kan du hente prosjektet på en annen maskin, eller dele med andre.

**Kort sagt:** Python er språket, Git er historikk, GitHub (valgfritt) er kopien på nett.

## Hva du trenger å installere

1. **Python 3.11 eller nyere** — fra [python.org](https://www.python.org/downloads/). På Windows: husk å krysse av for «Add Python to PATH» hvis installasjonen spør om det.
2. **Git** — fra [git-scm.com](https://git-scm.com/download/win) (Windows). Det gir deg kommandoen `git` i et terminalvindu.
3. (Valgfritt) **Cursor** eller **VSCode** — editor med støtte for Python og Git.

## Første gang: gjør mappen til et Git-repo

Når Git er installert, åpne en terminal **i prosjektmappen** (`Mal-prosjekt`) og kjør:

```text
git init
git add .
git commit -m "Første versjon av mal-prosjekt"
```

Da har du et **lokalt Git-repo** — historikk lagres i en skjult mappe som heter `.git` (ikke rør den manuelt).

**Enklere:** på Windows kan du kjøre `scripts\init-git.ps1` (høyreklikk → Kjør med PowerShell, eller åpne PowerShell i mappen og skriv `.\scripts\init-git.ps1`).

## Legge prosjektet på GitHub (slik at andre kan klone det)

1. Opprett en **nytt tomt repo** på [github.com](https://github.com) (uten README, uten .gitignore — du har allerede filer lokalt).
2. GitHub viser deg kommandoer; typisk ser det slik ut (bytt `DITT-BRUKERNAVN` og `REPO-NAVN`):

   ```text
   git remote add origin https://github.com/DITT-BRUKERNAVN/REPO-NAVN.git
   git branch -M main
   git push -u origin main
   ```

3. **Andre** kan nå laste ned hele prosjektet med:

   ```text
   git clone https://github.com/DITT-BRUKERNAVN/REPO-NAVN.git
   ```

Da er det **samme mal** som du har, bare hentet fra nettet.

## Når du merger på GitHub (Dependabot, andre PR-er)

Det som skjer på GitHub (merge, Dependabot som oppdaterer pakker) **oppdaterer ikke automatisk** filene på PC-en din. Du må hente dem:

```text
git pull
```

Hvis `pyproject.toml` ble endret (nye versjoner av biblioteker), kjør etterpå med aktivt virtuelt miljø:

```text
pip install -e ".[dev]"
```

Mer om dette: [ARBEIDSFLYT.md](ARBEIDSFLYT.md) (seksjon om synk med GitHub).

## Kjøre eksempel-koden på din maskin

Se hovedfilen [README.md](../README.md) — seksjonen «Kom i gang» (Python-miljø, `pip install`, `pytest`).

## Ordliste (kort)

| Ord | Betydning |
|-----|--------|
| **Repo** | Hele prosjektmappen med Git-historikk |
| **Commit** | Et «lagringspunkt» i historikken med en melding |
| **Clone** | Kopiere et repo fra nett (eller annen disk) |
| **Push** | Sende dine commits til GitHub |
| **Pull** | Hente endringer fra GitHub |

## Mer detaljer

- [NY-PROSJEKT-FRA-MAL.md](NY-PROSJEKT-FRA-MAL.md) — helt nytt prosjekt fra malen (annen maskin, GitHub template)
- [ARBEIDSFLYT.md](ARBEIDSFLYT.md) — flere Git-kontoer, Cursor, VSCode
- [ARKITEKTUR.md](ARKITEKTUR.md) — hvordan mapper henger sammen
