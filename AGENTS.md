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

---

## 🎯 Modus-Valg System

Prosjektet støtter **to moduser** for fleksibilitet:

### 🔧 Modus 1: Vibe Native (Anbefalt for Vibe CLI)
- **Aktiveres ved:** `/agent <rolle>` kommando **eller** `.vibe/mode` = `vibe_native`
- **Egnet for:** Vibe CLI
- **Funksjoner:**
  - Rollebytte: `/agent devops`
  - Linear: `linear_list_issues`, `linear_update_issue`
  - Filer: `read_file`, `edit`, `grep`
  - Prefiks: Automatisk (hentet fra agent)
  - Integrasjoner: MCP (Linear, GitHub, etc.)

### 🌐 Modus 2: Generic (For Copilot, Ollama, etc.)
- **Aktiveres ved:** Manuell prefiks `[Rolle]` **eller** `.vibe/mode` = `generic`
- **Egnet for:** Copilot, Ollama, lokal CLI, andre AI-verktøy
- **Funksjoner:**
  - Rollebytte: Manuell prefiks `[DevOps]`
  - Linear: `curl` API-kall (se .prompts/ for detaljer)
  - Filer: Standard verktøy (les fra .prompts/)
  - Prefiks: Manuell (`[Rolle]`)
  - Integrasjoner: Ingen MCP

---

### 📋 Modus-Konfigurasjon

#### Automatisk Deteksjon (Standard)
```bash
# Hvis du bruker /agent-kommando:
/agent scrum_master  # → Vibe Native Modus aktiveres

# Hvis du bruker manuell prefiks:
[Scrum Master] ...    # → Generic Modus aktiveres
```

#### Manuell Override
Opprett `.vibe/mode` fil for å tvinge en spesiell modus:
```bash
# Tving Vibe Native Modus (uavhengig av kommandoer)
echo "vibe_native" > .vibe/mode

# Tving Generic Modus (for Copilot/Ollama)
echo "generic" > .vibe/mode

# Bruk automatisk deteksjon (standard)
rm .vibe/mode
```

#### Sjekk aktiv modus
```bash
cat .vibe/mode  # Viser: vibe_native | generic
```

---

### 📊 Modus-Sammenligning

| **Funksjon**               | **Vibe Native**               | **Generic**                     |
|----------------------------|-------------------------------|--------------------------------|
| Rollebytte                | `/agent devops`               | `[DevOps] prefix`              |
| Linear-operasjoner        | `linear_list_issues`          | `curl` API-kall                |
| Filoperasjoner             | `read_file`, `edit`           | Standard verktøy              |
| Prefiks                    | Automatisk                    | Manuell `[Rolle]`            |
| MCP-Integrasjoner          | ✅ Full støtte                | ❌ Ikke tilgjengelig           |
| Kompatibilitet             | Vibe only                     | Alle AI-verktøy               |
| Læringskurve               | Medium                        | Lav                          |
| Effektivitet               | ✅✅✅ Høy                    | ⚠️ Medium                     |

---

## 🤖 Vibe Agent System (Native Vibe Setup)

Prosjektet bruker **Vibe Agents** for optimal workflow. Se `.vibe/README.md` for full dokumentasjon.

### Tilgjengelige Agenter

| Agent | Rolle | Prefiks | Beskrivelse |
|-------|------|--------|-------------|
| `scrum_master` | Scrum Master | [Scrum Master] | Team koordinering, Linear management |
| `devops` | DevOps | [DevOps] | Infrastruktur, CI/CD, miljø |
| `fullstack` | Fullstack Developer | [Fullstack] | Backend & frontend implementering |
| `security` | Security Specialist | [Security] | Sikkerhetsanalyse, OWASP |
| `qa` | QA Engineer | [QA] | Testing, automatisering |
| `ux` | UX Designer | [UX] | Design, accessibility |

### Bruksmåte

```text
# Start som Scrum Master
/agent scrum_master

# Bytt til DevOps
/agent devops

# Bytt til Security
/agent security

# Bytt til QA
/agent qa
```

### MCP Servere

- **Linear**: Konfigurert for issue management (`linear_*` verktøy)

### Fordeler med Native Setup

✅ **Raskere workflow**: Øyeblikkelig agent-bytting
✅ **Bedre integrasjon**: Native MCP-verktøy for Linear
✅ **Kontekstbevaring**: Vibe husker kontekst mellom agenter
✅ **Umiddelbare oppdateringer**: Hver agent oppdaterer Linear umiddelbart

### Hybrid Setup

Du kan bruke **begge systemer samtidig**:
- `.prompts/` - For **dokumentasjon** (universell, fungerer med alle AI-verktøy)
- `.vibe/agents/` - For **Vibe-optimering** (native integrasjoner)

Dette gir full effektivitet i Vibe, mens dokumentasjonen forblir tilgjengelig for Copilot, Ollama, etc.

### Tilbake til Generisk Oppsett

Se `.vibe/README.md` for instruksjoner om hvordan deaktivere Vibe-spesifikk konfigurasjon.

---

## 🏗️ Tverrfaglig Team Prosess (DoD - Definition of Done)

**ALLE oppgaver MÅ gjennomføre alle roller før Production:**

### Workflow
```
Backlog → Ready → In Progress → Testing → Production
         (Scrum Master)   (Rolle)     (Rolle)   (DevOps/Scrum Master)
```

### Rolleansvar

| Rolle | Ansvar | Leveranse | DoD-krav |
|-------|--------|-----------|----------|
| **Fullstack** | Implementer kode | Kode, dokumentasjon | ✅ IMPLEMENTERT |
| **QA** | Test koden | Testrapport | ✅ PASS |
| **Security** | Sikkerhetsanalyse | Sikkerhetsrapport | ✅ OK/APPROVED |
| **DevOps** | Miljøverifisering | Driftsrapport | ✅ OK |

### ⚠️ KRITISK REGEL
**Bare DevOps eller Scrum Master kan flytte en oppgave til Production**

Når en utvikler (Fullstack, UX, etc.) er ferdig:
1. Sett status til **Testing** (IKKE Production!)
2. Assignee beholdes (foreløpig Tøgge T)
3. Legg til kommentar: "[Rolle] Ferdig. Klar for QA."

Scrum Master koordinerer deretter:
1. Delegere til QA
2. QA tester → PASS/FAIL
3. Hvis PASS: Delegere til Security
4. Security analyserer → OK/Merknader
5. Hvis OK: Delegere til DevOps
6. DevOps verifiserer → OK
7. **DevOps/Scrum Master** flytter til Production

### DoD Checklist (MÅ oppfylles)
- [ ] Fullstack: Kode implementert og lokalt testet
- [ ] QA: Automatiske tester skrevet og passer
- [ ] Security: Sikkerhetsanalyse OK, ingen kritiske funn
- [ ] DevOps: Miljøkonfigurasjon OK

---

Se `.vibe/README.md` for instruksjoner om hvordan deaktivere Vibe-spesifikk konfigurasjon.

---

## 🎭 Rollehåndtering (for AI-agent)

- **Én rolle av gangen**: Svar alltid med det aktuelle rolleprefikset ([Scrum Master], [Fullstack], [UX], [DevOps], [Security], [QA])
- **Overlevering**: Når en oppgave er ferdig, skriv:
  ```
  [Rolle] Ferdig med [oppgave]. Overlever til [NesteRolle].
  ```
  Så bytter du prefiks i neste melding.
- **Kontekst**: Les `.prompts/99_scrum_status.md` ved sesjonsstart for å vite hvilken rolle som er aktiv.
- **Linear-sync**: Oppdater alltid Linear-status og `.prompts/99_scrum_status.md` ved overlevering.

### 📋 Lineær Oppfølgingsprotokoll (Kritisk)

**Alle agenter MÅ følge denne workflow:**

#### Når Scrum Master delegere en oppgave:
1. `linear_save_issue`: Sett `state="In Progress"`, `assignee="Tøgge T"`
2. `linear_save_comment`: Legg til "[Scrum Master] Delegert til [Rolle]. Eier: @Tøgge T"
3. Oppdater `.prompts/99_scrum_status.md` med aktiv oppgave

#### Når en Agent starter på en oppgave:
1. `linear_save_issue`: Sett `state="In Progress"`, `assignee="Tøgge T"`
2. `linear_save_comment`: Legg til "[Rolle] Startet arbeid med [Issue-ID]"
3. Oppdater `.prompts/99_scrum_status.md`

#### Når en Agent fullfører en oppgave:
1. `linear_save_issue`: Sett `state="Production"` (eller "Testing" om QA kreves)
2. `linear_save_comment`: Fullstendig rapport med alle endringer, commit-hash, etc.
3. Oppdater `.prompts/99_scrum_status.md`
4. Bytt tilbake: "[Rolle] Ferdig med [Issue-ID]. Overlever til [Scrum Master]."

**Merk:** Foreløpig brukes "Tøgge T" som assignee for alle agenter. Når vi har dedikerte agent-brukerkontoer i Linear, oppdateres dette.

---

## ⚡ Token/credit-optimalisering

- **Fillesing**: Bruk `read_file` med `limit` for store filer (maks 2000 linjer). Prefér `grep` for søk.
- **Batch**: Samle alle endringer i én `edit` per fil. Bruk `replace_all: true` for repetitive endringer.
- **Verktøy**: Sett alltid `timeout` på `bash`-kommandoer (maks 30s, unntak: 120s for setup).
- **Caching**: Ikke re-les filer du allerede har i kontekst i samme sesjon.
- **Subagenter**: Bruk `task` (explore) kun for komplekse utforskninger, ikke for enkle filendringer.
