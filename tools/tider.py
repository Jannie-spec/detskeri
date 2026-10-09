"""Daglig, stille kontrol af spisestedernes åbningstider.

For hvert sted åbnes kilden (src[0], ellers url). Linjer, der ligner åbningstider (klokkeslæt, ugedage,
"åben/lukket"), samles og sammenlignes med sidste kørsel. Er de ændret, får stedet `changed` med datoen,
og siden viser "tid usikker", indtil tiderne er gennemgået (mandagsgennemgangen sletter `changed`).
Ingen mails – resultatet ligger i data/tider.json. Kræver Playwright (køres i GitHub Actions)."""
import json, re, hashlib, datetime, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "tider.json"
TIME = re.compile(r"\b\d{1,2}[.:]\d{2}\b|\b\d{1,2}\s*[-–]\s*\d{1,2}\b|kl\.\s*\d", re.I)
WORDS = re.compile(r"mandag|tirsdag|onsdag|torsdag|fredag|lørdag|søndag|\bman\b|\btir\b|\bons\b|\btor\b|\bfre\b|\blør\b|\bsøn\b|"
                   r"åben|åbent|lukket|åbningstid|sæson|monday|tuesday|wednesday|thursday|friday|saturday|sunday|open|closed", re.I)

def relevant(text):
    lines = [re.sub(r"\s+", " ", l).strip() for l in text.splitlines()]
    keep = [l for l in lines if l and len(l) < 200 and TIME.search(l) and WORDS.search(l)]
    return "\n".join(dict.fromkeys(keep))          # uden dubletter, rækkefølge bevaret

def main():
    from playwright.sync_api import sync_playwright
    today = datetime.date.today().isoformat()
    state = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    places = []
    for f in sorted((ROOT / "data" / "places").glob("*.json")):
        for p in json.loads(f.read_text(encoding="utf-8")):
            src = [u for u in (p.get("src") or []) if u.startswith("http") and "facebook.com" not in u] or ([p["url"]] if p.get("url") else [])
            if src: places.append((f"{f.stem}:{p['id']}", p["name"], src[0]))
    changed = 0
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(locale="da-DK")
        for key, name, url in places:
            try:
                pg.goto(url, wait_until="domcontentloaded", timeout=30000); pg.wait_for_timeout(1500)
                txt = relevant(pg.evaluate("document.body ? document.body.innerText : ''"))
            except Exception as e:
                print("Kunne ikke hente", name, url, e, file=sys.stderr); continue
            if not txt: continue
            h = hashlib.sha1(txt.encode()).hexdigest()[:16]
            old = state.get(key)
            if old and old.get("hash") != h:
                old.update(hash=h, changed=today, url=url, text=txt[:1500]); changed += 1
                print("Ændret:", name)
            elif not old:
                state[key] = {"hash": h, "url": url, "text": txt[:1500]}
            old = state.get(key); old["checked"] = today
        b.close()
    OUT.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
    print("Tjekket:", len(places), "steder, ændret:", changed)

if __name__ == "__main__":
    main()
