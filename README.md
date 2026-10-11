# detskeri.dk

Daglige guider til, hvad der sker på Bornholm og i Rønne, Svaneke, Allinge, Nexø og Hasle – på dansk, engelsk, tysk og svensk.
Gudhjem har sin egen side: detskerigudhjem.dk.

- **Arrangementer** hentes hver morgen kl. 8 fra KultuNaut (`tools/kultunaut.py`) → `data/events.json`.
- **Steder uden for KultuNaut** (Bornholmertårnet ved Dueodde, Dideriks Veranda/Hotel Sandvig Havn) hentes hver morgen direkte fra stedernes egne sider (`tools/steder.py`) → `data/steder.json`. Finder tolkeren ingen datoer, beholdes sidste resultat, og stedet får `changed`. Test uden net: `python tools/steder.py --test`.
- **Spisesteder** med åbningstider står i `data/places/<by>.json` (med kilder i `src`). Ret her, når en tid ændrer sig.
- `python build.py` bygger siden til `site/`. GitHub Actions (`.github/workflows/byg.yml`) bygger og udgiver på GitHub Pages.
- **Facebook**: hver morgen ca. kl. 9.40 lægger `tools/facebook.py` et opslag med et billede af dagens program (samme stil som nyhedsbrevet) på siderne *Det sker på Bornholm* og *Det sker i Gudhjem* (`.github/workflows/facebook.yml`). Kræver hemmelighederne `FB_PAGE_TOKEN_BORNHOLM` og `FB_PAGE_TOKEN_GUDHJEM`. Se opslagene uden at poste: `python tools/facebook.py --preview`.
