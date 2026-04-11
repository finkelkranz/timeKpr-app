# Hemmeligheter — beste praksis

## Prinsipper

1. **Aldri** commit til Git: API-nøkler, passord, private tokens, SSH-nøkler eller hele `.env`-filer med sanne verdier.
2. **Eksempelverdier** hører hjemme i `.env.example` (uten sanne hemmeligheter).
3. **Lokal utvikling**: Bruk en `.env`-fil som er listet i `.gitignore`, eller operativsystemets nøkkelring der verktøyet støtter det.
4. **CI/CD**: Bruk hemmeligheter i plattformen (GitHub Actions *Secrets*, GitLab CI *Variables*, osv.), ikke hardkodet i workflow-filer.
5. **Produksjon**: Bruk dedikerte mekanismer (Kubernetes Secrets, sky-leverandørens secret manager, HashiCorp Vault, osv.).

## I dette repoet

- `mal_prosjekt.config` laster valgfritt en `.env` fra prosjektroten ved lokal kjøring.
- `docker-compose.yml` kan peke på `env_file: .env` når du aktiverer det — filen skal ikke committes.

## Leakage-beskyttelse

- Gitleaks kjører i `.github/workflows/security.yml` for å fange opp typiske mønstre.
- Vurder [git-secrets](https://github.com/awslabs/git-secrets) eller tilsvarende lokalt hvis du jobber med flere repoer.

## Rotasjon

Når en nøkkel har vært eksponert: roter den hos leverandøren, oppdater alle miljøer, og fjern den gamle fra historikk kun om nødvendig (gjen-skriving av historikk krever koordinering med team).
