# Sikkerhetsskanning og vurderinger

## Automatisert (i repoet)

| Tiltak | Beskrivelse |
|--------|-------------|
| **Dependabot** | Forslag til oppdateringer av avhengigheter |
| **`security.yml`** | Planlagt ukentlig: `pip-audit` mot installerte pakker, **Gitleaks** for hemmeligheter i historikk |
| **CI** | Tester og statisk analyse på hver PR |

## Manuelt eller med jevne mellomrom

- Gå gjennom **Dependabot-PR-er** og release notes for breaking changes.
- Kjør lokalt: `pip install pip-audit` og `pip-audit` etter å ha installert prosjektet.
- Vurder **GitHub CodeQL** (repo → Security → Code scanning) for dypere analyse — aktiveres i GitHub-innstillingene.

## Tredjepartsbibliotek

- Minimer antall avhengigheter.
- Foretrekk vedlikeholdte pakker med tydelig lisens.

## Hendelseshåndtering

Ved kjent sårbarhet i avhengighet: oppdater versjon, kjør tester, deploy raskt til miljøer som er berørt, og dokumenter kort hva som ble gjort.
