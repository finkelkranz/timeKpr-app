# Synkronisere forbedringer tilbake til mal-prosjektet

Når du har **kopiert** malen til et konkret prosjekt og forbedret noe du vil ha i malen igjen (CI, dokumentasjon, skript), kan du bruke én av disse metodene.

## Metode A: Cherry-pick eller manuell patch

1. I det konkrete prosjektet: `git log --oneline` og noter commit-hash for endringen du vil flytte.
2. I mal-repoet: legg til remote mot det andre repoet (`git remote add project <url>`), `git fetch project`.
3. `git cherry-pick <hash>` — løs eventuelle konflikter.
4. Alternativt: lag en patch med `git format-patch` og bruk `git apply` i mal-repoet.

## Metode B: Subtree eller delt historikk (avansert)

For vedvarende deling mellom to repoer kan **git subtree** eller **submodule** vurderes, men det øker kompleksitet. For de fleste holder cherry-pick eller kopiering av konkrete filer med gjennomgang.

## Metode C: Kopier filer manuelt

For små endringer: kopier `fil(er)` fra prosjekt A til mal-repoet, kjør tester og commit med tydelig melding, f.eks. `docs: lånt forbedret CI-sjekk fra prosjekt X`.

## Anbefaling

Hold **mal-repoet** som «oppstrøms» sannhetskilde. Når du lager nye prosjekter fra malen, dokumenter i det nye prosjektet (én linje i README) hvilken mal-versjon eller commit den kom fra — da blir sporbarheten enklere.
