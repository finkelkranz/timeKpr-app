# Hemmeligheter

**Ikke sjekk inn passord, nøkler, tokens eller andre hemmeligheter i Git!**

## Hvordan håndtere hemmeligheter

### 1. Miljøvariabler (anbefalt)

Lag en `.env` fil i prosjektroten (står i `.gitignore`):

```bash
cp .env.example .env
# Rediger .env med dine verdier
```

Eksempel `.env`:
```
APP_ENV=development
JWT_SECRET=sterk-hemmelig-nøkkel-here
ADMIN_PASSWORD_HASH=$2b$12$...bcrypt-hash...
HOST=0.0.0.0
PORT=8000
```

### 2. `.env.example`

`.env.example` er **sjekket inn** og viser hvilke variabler som trenges, men med standardverdier som fungerer for lokal utvikling.

### 3. timekpr_app.config

`timekpr_app.config` laster valgfritt en `.env` fra prosjektroten ved lokal kjøring via `load_dotenv()`.

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
