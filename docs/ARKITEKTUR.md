# Arkitektur

## Mapper

- `src/mal_prosjekt/` — applikasjonskode (bytt pakkenavn når du lager eget prosjekt).
- `tests/` — pytest-tester; speiler gjerne strukturen i `src/`.
- `.github/workflows/` — CI og sikkerhetsjobber.
- `docs/` — denne dokumentasjonen.

## Avhengigheter

- Kjøretidsavhengigheter står i `pyproject.toml` under `[project]`.
- Utviklerverktøy ligger under `[project.optional-dependencies].dev` og installeres med `pip install -e ".[dev]"`.

## Utvidelse

- Legg nye moduler under `src/mal_prosjekt/`.
- Legg til tester i `tests/` og kjør `pytest`.
- For nye CLI-kommandoer: utvid `argparse` i `cli.py` eller del opp i egne moduler.

## Docker

`Dockerfile` bygger et lite runtime-image og starter `mal-demo`. I produksjon bør du sette miljøvariabler og hemmeligheter via orkestrering (Kubernetes secrets, Azure Key Vault, osv.), ikke ved å bake inn `.env`.
