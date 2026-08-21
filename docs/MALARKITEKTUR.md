# Målarkitektur - timeKpr-app

**Versjon:** 1.0  
**Opprettet:** 22.08.2026  
**Oppdatert:** 22.08.2026  
**Ansvarlig:** [Scrum Master]  
**Status:** Under implementering

---

## 🎯 Visjon

> **Modulær arkitektur som muliggjør fremtidig flytting av frontend til sky eller mobil-apper, samtidig som vi opprettholder full lokal funksjonalitet og sikkerhet.**

---

## 🏗️ Nåværende Arkitektur (Baseline)

```
┌─────────────────────────────────────────────────────────────────┐
│                    LOCAL MACHINE (Trusted, Root)                      │
│                                                                  │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────────┐   │
│  │  Frontend    │◄───▶│   Backend    │◄───▶│    timekprd      │   │
│  │  React/Vite  │     │  FastAPI     │     │   (D-Bus)        │   │
│  │  :5173      │     │  :8000      │     │   (root)         │   │
│  └─────────────┘     └─────────────┘     └─────────────────┘   │
│          ▲                  ▲                              ▲      │
│          │                  │                              │      │
│  ┌──────┴──────┐    ┌──────┴──────┐               ┌──────┴──────┐ │
│  │ CORS         │    │ Data Access │               │ Logs        │ │
│  │ localhost    │    │ Root Req.   │               │ System      │ │
│  └──────────────┘    │ - D-Bus      │               └─────────────┘ │
│                     │ - Files       │                              │
│                     └──────┬──────┘                              │
│                            │                                     │
│                     ┌──────▼──────┐                              │
│                     │ /var/lib/    │                              │
│                     │ timekpr/    │                              │
│                     └─────────────┘                              │
└─────────────────────────────────────────────────────────────────┘
```

### Komponenter

| Komponent | Type | Tilgang | Port | Beskrivelse |
|-----------|------|---------|------|-------------|
| Frontend | React/Vite | Browser | 5173 | Brukergrensesnitt |
| Backend | FastAPI | Lokalt | 8000 | API + Forretningslogikk |
| timekprd | D-Bus Daemon | SystemBus | - | timekpr core (root) |
| Data | Filer | `/var/lib/timekpr/` | - | Konfig + Usage (root) |
| Database | SQLite | Lokalt | - | Historisk data |

---

## 🎯 Målarkitektur (Target State)

```
┌─────────────────────────────────────────────────────────────────┐
│                    FREMTIDIG STAT (Modulær)                         │
│                                                                  │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────────┐   │
│  │  Frontend    │     │   Backend    │     │  Data Providers  │   │
│  │  (React)     │◄───▶│  (FastAPI)    │◄───▶│  (Abstrakt lag)   │   │
│  │  Anywhere*   │     │  Anywhere*   │     │                 │   │
│  └─────────────┘     └─────────────┘     │  ┌─────────────┐ │   │
│                                                 │  │ DBus       │ │   │
│                                                 │  │ Provider   │ │   │
│                                                 │  └─────────────┘ │   │
│                                                 │  ┌─────────────┐ │   │
│                                                 │  │ File       │ │   │
│                                                 │  │ Provider   │ │   │
│                                                 │  └─────────────┘ │   │
│                                                 │  ┌─────────────┐ │   │
│                                                 │  │ Remote     │ │   │
│                                                 │  │ Provider   │ │   │
│                                                 │  └─────────────┘ │   │
│                                                 └─────────────────┘   │
│                                                              │
│  *Frontend kan flyttes til sky/mobil                      │
│  *Backend kan flyttes til sky (med Remote Provider)       │
│  *Lokal timekprd forbli på lokal maskin                   │
└─────────────────────────────────────────────────────────────────┘
```

### Nøkkelprinsipper

1. **Separation of Concerns:** Data-tilgang adskilt fra forretningslogikk
2. **Dependency Injection:** Providers injiseres, ikke hardkodet
3. **Miljøuavhengighet:** Samme kode fungerer lokalt og i sky
4. **Sikkerhet:** Alle data-tilganger valideres og autoriseres
5. **Testbarhet:** Mock-providers for enhetstesting

---

## 🔧 Arkitekturendringer (Slagplan)

### Phase 1: Sikkerhetsfundament ✅ (Prioritet: CRITICAL)

**Mål:** Sikre nåværende lokal installasjon

| Oppgave | Beskrivelse | Impact |
|--------|-------------|--------|
| S-1 | Full kodebase audit for hardkodede hemmeligheter | 🔴 Eliminere sikkerhetshull |
| S-2 | Pydantic input-validering for alle API-endepunkter | 🔴 Forhindre injection |
| S-3 | Rate-limiting middleware | 🔴 Beskytt mot brute-force |
| S-4 | Sikker CORS-konfigurasjon | 🔴 Forhindre uautorisert tilgang |
| S-5 | JWT-implementasjonsgjennomgang | 🔴 Sikre autentisering |

**Resultat:** Sikker lokal installasjon klar for produksjonsbruk

---

### Phase 2: Modularisering 🔄 (Prioritet: HIGH)

**Mål:** Abstrahere data-tilgang for fremtidig fleksibilitet

#### 2.1: Provider Interface

```python
# Ny fil: src/timekpr_app/providers/base.py

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

@runtime_checkable
class TimekprDataProvider(Protocol):
    """Interface for timekpr data access."""
    
    @abstractmethod
    def get_user_list(self) -> list[str]:
        """Get list of configured users."""
        pass
    
    @abstractmethod
    def get_user_config(self, username: str) -> dict:
        """Get user configuration."""
        pass
    
    @abstractmethod
    def get_time_left(self, username: str) -> dict:
        """Get remaining time for user."""
        pass
    
    @abstractmethod
    def set_time_left(self, username: str, seconds: int, period: str) -> bool:
        """Set remaining time."""
        pass
```

#### 2.2: Konkrete Implementasjoner

```
┌─────────────────────────────────────────────┐
│  TimekprDataProvider (Interface)               │
│  │                                                 │
│  ├── DBusTimekprProvider                        │
│  │   └── Bruker: timekpr.py (nåværende)          │
│  │   └── Miljø: Lokal maskin (root)             │
│  │                                                 │
│  ├── FileTimekprProvider                         │
│  │   └── Bruker: timekpr_file.py (nåværende)     │
│  │   └── Miljø: Lokal maskin (root)             │
│  │                                                 │
│  └── RemoteTimekprProvider (Fremtidig)          │
│      └── Bruker: HTTP/JSON API                   │
│      └── Miljø: Sky ↔ Lokal (secure tunnel)     │
└─────────────────────────────────────────────┘
```

#### 2.3: Refaktorering

- `timekpr.py` → `providers/dbus_provider.py`
- `timekpr_file.py` → `providers/file_provider.py`
- Opprett `providers/remote_provider.py` (stub for fremtidig)
- Opprett `providers/__init__.py` med factory-funksjon

**Oppgaver:**

| Oppgave | Beskrivelse | Impact |
|--------|-------------|--------|
| M-1 | Design TimekprDataProvider interface | ⭐⭐⭐ Grunnlag for alt |
| M-2 | Implementer DBusTimekprProvider | ⭐⭐⭐ Beholder eksisterende |
| M-3 | Implementer FileTimekprProvider | ⭐⭐⭐ Beholder eksisterende |
| M-4 | Refaktor timekpr.py til provider | ⭐⭐⭐ Modulariser |
| M-5 | Refaktor timekpr_file.py til provider | ⭐⭐⭐ Modulariser |
| M-6 | Opprett provider factory & DI | ⭐⭐⭐ Enkel bytting |
| M-7 | Oppdater all kode til å bruke providers | ⭐⭐⭐ Full integrasjon |

**Resultat:** Modulær arkitektur klar for fremtidige endringer

---

### Phase 3: Core Forbedringer 🧩 (Prioritet: HIGH/MEDIUM)

**Mål:** Forbedre kodekvalitet og støtte for fremtidig sky

| Oppgave | Beskrivelse | Impact |
|--------|-------------|--------|
| C-1 | Multi-user autentisering (JWT per bruker) | ⭐⭐⭐ Sky-klar |
| C-2 | Forbedret Docker-oppsett | ⭐⭐ Produksjonsklar |
| C-3 | Fullstendig .env.example | ⭐⭐ Dokumentasjon |
| C-4 | Enhetstester for providers | ⭐⭐ Kvalitetssikring |
| C-5 | Sikkerhetsgjennomgang av ny arkitektur | ⭐⭐⭐ Validering |

**Resultat:** Robust kodebase klar for skala

---

### Phase 4: Fremtidssikring 🚀 (Prioritet: LOW)

**Mål:** Forberede for sky/mobil (NÅ IKKE PRIORITERT)

| Oppgave | Beskrivelse | Impact |
|--------|-------------|--------|
| F-1 | Design sky-arkitektur | ⭐⭐ Planlegging |
| F-2 | Implementer RemoteTimekprProvider | ⭐⭐ Sky-støtte |
| F-3 | HTTPS-konfigurasjon | ⭐⭐ Sikkerhet |
| F-4 | Admin-dashboard (UX) | ⭐⭐ Brukeradministrasjon |
| F-5 | Admin-dashboard (Backend) | ⭐⭐ API |
| F-6 | Admin-dashboard (Frontend) | ⭐⭐ UI |

**Resultat:** Full sky-støtte (for fremtidig evaluering)

---

## 📊 Implementeringsplan (Linear)

### Epics

1. **Epic: Sikkerhetsfundament** (Phase 1)
   - 5 oppgaver
   - Prioritet: CRITICAL
   - Estimert: ~18 timer
   - Mål: Sikker lokal installasjon

2. **Epic: Arkitekturmodularisering** (Phase 2)
   - 7 oppgaver
   - Prioritet: HIGH
   - Estimert: ~24 timer
   - Mål: Modulær kodebase

3. **Epic: Core Forbedringer** (Phase 3)
   - 5 oppgaver
   - Prioritet: HIGH/MEDIUM
   - Estimert: ~20 timer
   - Mål: Produksjonsklar kode

4. **Epic: Fremtidssikring** (Phase 4)
   - 6 oppgaver
   - Prioritet: LOW
   - Estimert: ~29 timer
   - Mål: Klar for sky/mobil

### Totalt: 23 oppgaver, ~91 timer

---

## 🎯 Beslutningspunkter (PO)

### ✅ Allerede avgjort:

1. **Modularitet er målet** - Ikke aktiv sky-planlegging
2. **Frontend kan flyttes til sky senere** - Arkitekturen skal støtte dette
3. **Backend forbli lokalt inntil videre** - Men skal være sky-klar
4. **Sikkerhet prioriteres først** - FASE 1 må fullføres før FASE 2

### 📋 Åpent for diskusjon:

1. **Skal vi implementere RemoteTimekprProvider nå?**
   - **For:** Fremtidssikring
   - **Imot:** Ikke nødvendig for lokal bruk
   - **Beslutning:** ❌ **Nei** - Bare interface + stub

2. **Skal vi støtte mobil-app?**
   - **For:** Fremtidig fleksibilitet
   - **Imot:** Ekstra kompleksitet
   - **Beslutning:** ⚠️ **Kan diskuteres** - Arkitekturen støtter det uansett

---

## 📚 Referanser

- [Team Charter](../.prompts/99_team_charter.md) - Team regler
- [Sikkerhet](../SIKKERHET.md) - Sikkerhetsretningslinjer
- [CI og Tester](../CI-OG-TESTER.md) - Teststrategi
- [Arbeidsflyt](../ARBEIDSFLYT.md) - Utviklingsprosess

---

## 📝 Revisjonslogg

| Dato | Endring | Ansvarlig |
|------|---------|-----------|
| 22.08.2026 | Opprettet dokument | [Scrum Master] |
| 22.08.2026 | Definert 4-fasers plan | [Scrum Master] |
