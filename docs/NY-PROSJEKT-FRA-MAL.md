# Nytt prosjekt fra malen (fra scratch)

Denne siden er ment når du skal **starte et helt nytt prosjekt** ut fra malen — for eksempel om noen måneder på en **annen maskin** (jobb-PC), når du ikke husker detaljene fra i dag.

## Hva du trenger på forhånd

- [Python 3.11+](https://www.python.org/downloads/) og [Git](https://git-scm.com/downloads) installert.
- Tilgang til **mal-repoet på GitHub** (ditt `mal-prosjekt` eller det du har pushet dit).

## Tre måter å få mal-koden inn i en ny mappe

### A) Anbefalt: «Use this template» på GitHub (minst manuelt)

1. Åpne mal-repoet på GitHub (f.eks. `finkelkranz/mal-prosjekt`).
2. Hvis eieren har slått på **Settings → General → Template repository**: trykk **Use this template** → **Create a new repository**.
3. Gi det **nye** repoet et navn (f.eks. `mitt-arbeidsprosjekt`). Da får du et **nytt** repo med samme filer, uten felles historikk med malen.
4. Klon det nye repoet på maskinen:

   ```text
   git clone https://github.com/DITT-BRUKERNAVN/mitt-arbeidsprosjekt.git
   cd mitt-arbeidsprosjekt
   ```

5. Gå til [Gi prosjektet ditt egne navn](#gi-prosjektet-ditt-egne-navn) nedenfor.

### B) Vanlig klon av malen, så nytt repo

1. Klon malen til en **ny mappe** (eller kopier repo-URL fra GitHub):

   ```text
   git clone https://github.com/DITT-BRUKERNAVN/mal-prosjekt.git mitt-nye-navn
   cd mitt-nye-navn
   ```

2. Fjern koblingen til mal-repoet og koble til et **nytt** tomt repo på GitHub (eller behold lokalt uten remote):

   ```text
   git remote remove origin
   git remote add origin https://github.com/DITT-BRUKERNAVN/nytt-repo.git
   git push -u origin main
   ```

   (Bytt `main` til `master` hvis du bruker det.)

3. Gå til [Gi prosjektet ditt egne navn](#gi-prosjektet-ditt-egne-navn).

### C) Kun filer (uten Git-historikk)

1. Last ned **ZIP** fra GitHub (**Code → Download ZIP**) eller kopier mappen manuelt.
2. Pakk ut / lim inn der du vil ha prosjektet.
3. Kjør `git init` og eventuelt `scripts\init-git.ps1` (Windows) eller `scripts/init-git.sh` — se [BEGINNER.md](BEGINNER.md).
4. Gå til [Gi prosjektet ditt egne navn](#gi-prosjektet-ditt-egne-navn).

## Gi prosjektet ditt egne navn

Malen bruker tre typer navn du bør bytte ut:

| Type | Eksempel (mal) | Ditt valg |
|------|----------------|-----------|
| **Pip-/prosjektnavn** (med bindestrek) | `mal-prosjekt` | f.eks. `mitt-prosjekt` |
| **Python-pakke** (understrek, lovlig modulnavn) | `mal_prosjekt` | f.eks. `mitt_prosjekt` |
| **CLI-kommando** | `mal-demo` | f.eks. `mitt-app` |

**Automatisk (anbefalt på Windows):** fra prosjektmappen:

```powershell
.\scripts\new-from-mal.ps1 -PipName "mitt-prosjekt" -PackageName "mitt_prosjekt" -CliName "mitt-app"
```

Skriptet bytter navn på `src/mal_prosjekt/`, oppdaterer `pyproject.toml`, tester, CI, Dockerfile og referanser i dokumentasjon. Les utdata nøye; kjør deretter tester.

**Manuelt:** følg samme tabell og søk/erstatt i hele repoet (inkl. `pyproject.toml`, `src/`, `tests/`, `.github/workflows/`, `Dockerfile`, `AGENTS.md`). Det er mer arbeid og lettere å gjøre feil — bruk skriptet hvis du kan.

## Færrest mulig manuelle steg på *denne* eller en *ny* maskin

Når filene ligger der du skal jobbe:

1. **Oppsett av Python-miljø** (venv + installasjon av avhengigheter):

   ```powershell
   .\scripts\setup-dev.ps1
   ```

   På Linux/macOS: `chmod +x scripts/setup-dev.sh && ./scripts/setup-dev.sh`

2. **Verifiser:**

   ```powershell
   .\scripts\check.ps1
   ```

3. **Hemmeligheter:** kopier `.env.example` til `.env` hvis du trenger det — se [HEMMELIGHETER.md](HEMMELIGHETER.md).

Det er den faste «rutinen»: clone/template → (evt.) `new-from-mal.ps1` → `setup-dev` → `check`.

## Sjekkliste: «Om to måneder på jobb-PC»

1. Installer Python og Git.
2. Klon **ditt** prosjekt (eller mal via template) — se avsnitt A–C over.
3. Kjør `setup-dev` → `check`.
4. Hvis dette er en **fersk kopi av malen** som fortsatt heter `mal-prosjekt`: kjør `new-from-mal.ps1` med dine navn.
5. Åpne mappen i Cursor/VSCode og les `README.md` og `AGENTS.md`.

## Slå på «template» på GitHub (én gang)

Eier av mal-repoet: **Settings → General** → kryss av for **Template repository**. Da vises **Use this template** for alle som skal spawne nye repoer uten å kopiere manuelt.

## Se også

- [ARBEIDSFLYT.md](ARBEIDSFLYT.md) — `git pull` etter endringer på GitHub
- [SYNK-MAL.md](SYNK-MAL.md) — flytte forbedringer tilbake til malen
