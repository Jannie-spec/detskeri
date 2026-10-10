# detskeri.dk

Daglige guider til, hvad der sker på Bornholm og i Rønne, Svaneke, Allinge, Nexø og Hasle – på dansk, engelsk, tysk og svensk.
Gudhjem har sin egen side: detskerigudhjem.dk.

- **Arrangementer** hentes hver morgen kl. 8 fra KultuNaut (`tools/kultunaut.py`) → `data/events.json`.
- **Spisesteder** med åbningstider står i `data/places/<by>.json` (med kilder i `src`). Ret her, når en tid ændrer sig.
- `python build.py` bygger siden til `site/`. GitHub Actions (`.github/workflows/byg.yml`) bygger og udgiver på GitHub Pages.
- **Facebook**: hver torsdag kl. ca. 11 lægger `tools/facebook.py` et opslag på siderne *Det sker på Bornholm* og *Det sker i Gudhjem* (`.github/workflows/facebook.yml`). Kræver hemmelighederne `FB_PAGE_TOKEN_BORNHOLM` og `FB_PAGE_TOKEN_GUDHJEM`. Se opslagene uden at poste: `python tools/facebook.py --preview`.
