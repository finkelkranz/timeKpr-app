# Team Charter - timeKpr-app

**Versjon:** 1.0  
**Opprettet:** 21.08.2026  
**Oppdatert:** 21.08.2026  
**Ansvarlig:** [Scrum Master]

---

## 📋 Team Medlemmer & Roller

| Rolle | Prefiks | Primæransvar | Sekundæransvar |
|-------|---------|--------------|----------------|
| **Produkteier (PO)** | - | Krav, prioritering, endelige beslutninger | Budsjett, visjon |
| **Scrum Master** | `[Scrum Master]` | Oppgaveledelse, team-koordinering | Linear-administrasjon |
| **UX Designer** | `[UX]` | Brukeropplevelse, design, WCAG | Frontend-veiledning |
| **Fullstack** | `[Fullstack]` | Koding (frontend + backend) | Arkitektur |
| **DevOps** | `[DevOps]` | Miljø, CI/CD, infrastruktur | Deploy |
| **Security** | `[Security]` | Sikkerhetsanalyse, OWASP | Risk assessment |
| **QA** | `[QA]` | Testing, automatisering | Kvalitetssikring |

---

## 🎯 Team Mål

- **Lokalt fokus:** Prosjektet kjører alltid med en lokal komponent på denne maskinen
- **Kvalitet:** Kode som er testet, sikret og dokumentert
- **Samarbeid:** Klar kommunikasjon og sporbarhet i Linear
- **Effektivitet:** Minimal overhead, maksimal produktivitet

---

## 🔄 Arbeidsflyt (Kanban)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────┐     ┌─────────────┐
│   Backlog    │────▶│    Ready     │────▶│   In Progress    │────▶│  Testing    │
└─────────────┘     └─────────────┘     └─────────────────┘     └─────────────┘
                                                                       │
                                    ┌──────────────────────────────────────┘
                                    ▼
┌─────────────────────────────┐     ┌─────────────┐
│      Production (Local)       │◀────│   Icebox     │
└─────────────────────────────┘     └─────────────┘
```

### Statusbeskrivelser

| Status | Beskrivelse | Krav for å flytte hit |
|--------|-------------|----------------------|
| **Backlog** | Alle ideer, krav, bugrapporter | - |
| **Ready** | Klar for arbeid | Fullt spesifisert, prioritert, avhengigheter løst |
| **In Progress** | Aktivt arbeid | Tildelt til rolle, kapasitet tilgjengelig |
| **Testing** | Kvalitetssikring | Kode ferdig, lokalt testet av utvikler |
| **Production** | Kjører på lokal maskin | **QA PASS + Security OK** (se DoD) |
| **Icebox** | Arkiv | Oppgave irrelevant eller utsatt |

---

## ✅ Definition of Done (DoD)

En oppgave er **ferdig** og kan flyttes til **Production** når:

### 🎨 UX
- [ ] Designspesifikasjon fullført
- [ ] Tailwind CSS-klasser dokumentert
- [ ] WCAG-retningslinjer fulgt (kontrast, tastaturnavigasjon)
- [ ] Godkjent av Scrum Master

### 💻 Fullstack
- [ ] Kode følger kodestandard (DRY, SOLID, type hints)
- [ ] Ingen hardkodede hemmeligheter
- [ ] Lokalt testet uten errors
- [ ] Feilhåndtering implementert
- [ ] Dokumentasjon oppdatert

### 🔒 Security
- [ ] Sikkerhetsanalyse gjennomført
- [ ] Status: 🟢 OK (eller 🟡 Merknader med PO-avgjørelse)
- [ ] OWASP Top 10 sjekket
- [ ] Ingen kritiske sårbarheter

### 🧪 QA
- [ ] Automatiske tester skrevet og passer
- [ ] Manuell testing fullført
- [ ] Alle akseptansekriterier verifisert
- [ ] Testrapport: PASS

### ⚙️ DevOps
- [ ] Miljøkonfigurasjon oppdatert
- [ ] Deploy-skript testet
- [ ] Kjører stabilt på lokal maskin

**📌 Viktig:** Bare **DevOps** eller **Scrum Master** kan flytte oppgaver til Production.

---

## 🔀 Oppgaveflyt & Ansvar

| Flyt | Ansvarlig | Betingelse |
|------|-----------|------------|
| Backlog → Ready | Scrum Master | Full spesifikasjon, prioritet satt |
| Ready → In Progress | Rolleinnehaver | Kapasitet, ingen blokkeringer |
| In Progress → Testing | Utvikler | Kode ferdig, lokalt verifisert |
| Testing → In Progress | QA | Feil funnet (med beskrivelse) |
| Testing → Production | DevOps / Scrum Master | **DoD oppfylt** (QA PASS + Security OK) |
| * → Icebox | Scrum Master | Oppgave irrelevant/utsatt |

---

## 🚦 Blokkeringer & Avhengigheter

### Håndtering av blokkeringer
1. **Identifiser blokkering:** Rolle markerer oppgave med `blocked` label
2. **Dokumenter:** Kommentar i Linear med:
   ```
   [Rolle] BLOKKERT: [Årsak]
   Avventer: [Hva som trenges]
   ```
3. **Escalation:** Scrum Master prioriterer blokkerte oppgaver
4. **Timeout for PO:** Hvis PO ikke svarer på spørsmål innen **24 timer**, legges det inn en automatisk kommentar:
   ```
   [Scrum Master] TIMEOUT: Oppgave avventer avklaring av PO i >24 timer
   ```

### Avhengigheter mellom oppgaver
- Oppgave B som avhenger av Oppgave A: Merk i beskrivelsen:
  ```
  Avhengigheter: #123 (Oppgave A)
  ```
- Oppgave B **kan ikke** flyttes til Ready før Oppgave A er i Production
- Scrum Master oppdaterer status automatisk

---

## 💬 Kommunikasjonsregler

### ⭐ Generelle regler
- **Alt samarbeid** skjer i **Linear** (kommentarer på oppgaver)
- **Ingen private meldinger** om prosjektet (alt må være sporbart)
- **Engelsk terminologi** i prefikser for konsistens

### 📝 Kommentarformat
Alle kommentarer starter med rolle-prefiks:
```
[UX] Spørsmål om design: Skal profilbilde være sirkel eller firkant?

[Fullstack] Svar: Vi bruker sirkel, matcher Tailwind-komponenten.

[Security] Merknad: Pass på at bilde-URLer valideres for XSS.
```

### 🏷️ Label-bruk
- `ai-generated`: Alle oppgaver opprettet av AI (obligatorisk)
- `priority:*`: Sett av Scrum Master basert på PO-input
- `blocked`: Oppgave kan ikke fortsette
- Komponent-labels (`backend`, `frontend`, etc.): Sett av rolleinnehaver

---

## 🔐 Sikkerhetsbeslutninger

### Prosess for sikkerhetsrelaterte trade-offs
1. **Security identifiserer:** `[Security]` peker på potensielt problem
2. **Analyse:** Security dokumenterer:
   - Risiko
   - Potensielle løsninger
   - Trade-offs (f.eks. sikkerhet vs. brukervennlighet)
3. **PO avgjør:** Produkteier tar **endelig beslutning** basert på:
   - Risikonivå
   - Business-behov
   - Tidsrammer
4. **Dokumentasjon:** PO kommenterer:
   ```
   [PO] Beslutning: [Valgt løsning]
   Begrunnelse: [Hvorfor]
   ```

**⚠️ Viktig:** Security har **plikt til å påpeke** risiko, men **ikke veto** (med mindre det er kritisk lovbrudd).

---

## 🎯 Prioriteringsregler

| Prioritet | Kriterier | Håndtering |
|-----------|-----------|------------|
| `priority:critical` | Sikkerhetshull, systemnedetid | Umiddelbar handling |
| `priority:high` | Blokker andre oppgaver | Neste oppgave |
| `priority:medium` | Normal funksjonalitet | Standard flyt |
| `priority:low` | Forbedringer, refactoring | Når tid |

**Spesialtilfelle:** `security` label + `priority:high` = **Må håndteres innen 24 timer**

---

## 📊 Rapportmaler

### Daglig Statusoppdatering (Async)
```markdown
[Rolle] Status - DD.MM.ÅÅÅÅ
- **I går:** [Hva ble gjort]
- **I dag:** [Hva jobbes med]
- **Blokkeringer:** [Hva hindrer fremgang]
- **Spørsmål til PO:** [Spørsmål som trenger avklaring]
```

### Ukentlig Retrospektiv
Ledes av Scrum Master, holdes i Linear:
```markdown
[Scrum Master] Retrospektiv - Uke XX

**Gikk bra:**
- [Teammedlem] [Hva fungerte]

**Forbedringspunkter:**
- [Teammedlem] [Hva kan gjøres bedre]

**Handling:**
- [Oppgave] [Hva skal gjøres]
```

---

## 🛠️ Verktøy & Integrasjoner

| Verktøy | Formål | Ansvarlig |
|---------|--------|-----------|
| **Linear** | Oppgavestyring, dokumentasjon | Scrum Master |
| **GitHub** | Kode, PR, Issues | DevOps |
| **D-Bus** | timekpr-kommunikasjon | Fullstack |
| **Local Server** | Kjørende instans | DevOps |

---

## 📅 Møter & Synkronisering

- **Daglig:** Asynkron statusoppdatering i Linear
- **Ukentlig:** Retrospektiv (ledet av Scrum Master)
- **Ad-hoc:** Samlinger i Linear-kommentarer
- **Timeout:** 24 timer for PO-spørsmål (automatisk eskalering)

---

## 📞 Kontakt & Escalation

| Spørsmål type | Hvem kontakte | Kanal |
|---------------|--------------|-------|
| Tekniske spørsmål | Fullstack / DevOps | Linear-kommentar |
| Design spørsmål | UX | Linear-kommentar |
| Sikkerhets spørsmål | Security | Linear-kommentar |
| Prioritering | PO | Linear-kommentar |
| Blokkeringer | Scrum Master | Linear-kommentar |
| Urgent ( < 2 timer) | PO (direkte) | Linear + direkte melding |

---

## ✨ Team Verdier

1. **Åpenhet:** Alt arbeid og beslutninger er synlig i Linear
2. **Kvalitet:** Vi leverer bare kode som oppfyller DoD
3. **Samarbeid:** Vi hjelper hverandre for å nå team-mål
4. **Forbedring:** Vi lære av feil og optimaliserer prosesser
5. **Respekt:** Vi verdsetter hverandres ekspertise

---

## 📝 Revisjonslogg

| Dato | Endring | Ansvarlig |
|------|---------|-----------|
| 21.08.2026 | Opprettet charter | [Scrum Master] |
| 21.08.2026 | Justert Security-rolle | [Scrum Master] |
