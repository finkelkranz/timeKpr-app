# Hemmeligheter

**⚠️ KRITISK: Ikke sjekk inn passord, nøkler, tokens eller andre hemmeligheter i Git!**

**⚠️ SIKKERHETSADVARSEL: Før du kjører appen, må du fullføre alle KRITISKE steg i README.md**

## Hvordan håndtere hemmeligheter

### 1. Miljøvariabler (anbefalt)

**KRITISK:** Appen krever nå at `JWT_SECRET` og `ADMIN_PASSWORD_HASH` er satt i miljøvariabler.
Det er **ikke** lenger standardverdier i koden.

Lag en `.env` fil i prosjektroten (står i `.gitignore`):

```bash
cp .env.example .env
# Rediger .env med dine verdier (ALL variabler under must be set!)
```

### 2. `.env.example`

`.env.example` er **sjekket inn** og viser hvilke variabler som trenges, **uten standardverdier** for sikkerhetskritiske innstillinger.

### 3. timekpr_app.config

`timekpr_app.config` laster `.env` fra prosjektroten ved lokal kjøring via `load_dotenv()`.
Dersom `.env` mangler, vil den prøve å lese fra miljøvariabler i systemet.

## Hemmeligheter i dette prosjektet

| Variabel | Beskrivelse | Eksempel (dev) | Produksjon |
|----------|-------------|---------------|------------|
| `JWT_SECRET` | Hemmelighet for JWT-token signing | `dev-secret-change-in-prod!` | **MÅ endres** - bruk lang, tilfeldig streng |
| `ADMIN_PASSWORD_HASH` | BCrypt-hash av admin-passord | Hash av `"admin"` | **MÅ endres** - generer nytt hash |

### Generer ny JWT_SECRET

```bash
# Python
python3 -c "import secrets; print(secrets.token_urlsafe(64))"

# Eller openssl
openssl rand -hex 64
```

### Generer nytt admin-passord hash

```bash
python3 -c "from timekpr_app.auth import hash_password; print(hash_password('mitt_nye_passord'))"
```

## Produksjon

### Docker

I Docker, sett miljøvariabler via:
- `--env` flag: `docker run --env JWT_SECRET=xxx`
- `--env-file`: `docker run --env-file .env.prod`
- Docker secrets (anbefalt for produksjon)

### Kubernetes

Bruk Kubernetes Secrets:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: timekpr-app-secrets
type: Opaque
data:
  JWT_SECRET: <base64-encoded>
  ADMIN_PASSWORD_HASH: <base64-encoded>
```

### Systemd service

I `timekpr-app.service`, sett miljøvariabler med `Environment=` eller `EnvironmentFile=`.

## Hva som IKKE bør sjekkes inn

- `.env` filer (allerede i `.gitignore`)
- `.env.local`
- `.env.prod`
- Eventuelle filer som inneholder hemmeligheter
- Hardkodede passord/nøkler i koden
- API-tokens fra eksterne tjenester

## Sjekkliste før commit

- [ ] Ingen nye hemmeligheter i koden
- [ ] `.env` ikke kommet inn
- [ ] Alle hemmeligheter bruker miljøvariabler
- [ ] `git status` viser ingen uventede filer
