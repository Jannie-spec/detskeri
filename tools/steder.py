"""Henter arrangementer direkte fra steder, der ikke (altid) ligger på KultuNaut → data/steder.json.

Køres hver morgen af GitHub Actions efter KultuNaut (kræver Playwright, fordi nogle sider er Wix):
    python tools/steder.py            # hent og gem
    python tools/steder.py --test     # kør tolkningen på de gemte testtekster i tools/steder_test/ uden net

Hvert sted har sin egen lille tolker (PARSERS), som læser datoer ud af stedets egen tekst.
- Findes der ikke noget brugbart (siden er lavet om, eller hentningen fejler), beholdes sidste gode resultat,
  og stedet får "changed" med datoen, så det kan efterses.
- Arrangementer længere end 10 dage (fx en hel sæson) får "long" og vises kun under "Længere frem".
Stederne står i SOURCES nedenfor. Tilføj et nyt sted ved at skrive en tolker og en linje i SOURCES."""
import json, re, hashlib, datetime, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "steder.json"
TESTDIR = pathlib.Path(__file__).resolve().parent / "steder_test"

MONTHS = {"januar": 1, "februar": 2, "marts": 3, "april": 4, "maj": 5, "juni": 6, "juli": 7, "august": 8,
          "september": 9, "oktober": 10, "november": 11, "december": 12}
MON_RE = "(" + "|".join(MONTHS) + r")"

def _year_for(month, today, years):
    """Årstal: står der et årstal på siden, bruges det; ellers nærmeste kommende forekomst."""
    if years: return max(years)
    return today.year + (1 if month < today.month - 1 else 0)

def _ev(sid, d1, d2, title, where, town, url, t=None, t2=None, text=""):
    ev = {"id": f"{sid}-{d1.isoformat()}", "d": d1.isoformat(), "title": title, "where": where, "town": town, "url": url, "src": sid}
    if d2 and d2 != d1: ev["to"] = d2.isoformat()
    if d2 and (d2 - d1).days > 10: ev["long"] = 1
    if t: ev["t"] = t
    if t2: ev["t2"] = t2
    if text: ev["text"] = text
    return ev

def _hh(h): return f"{int(h):02d}:00"

# ---------- Bornholmertårnet (Dueodde) ----------
def parse_bornholmertaarnet(text, today, src):
    flat = re.sub(r"\s+", " ", text)
    low = flat.lower()
    years = [int(y) for y in re.findall(r"\b(20\d\d)\b", flat) if today.year - 1 <= int(y) <= today.year + 1]
    out = []
    # rundvisninger: "rundvisninger kl. 11 og 13"
    tours = re.search(r"rundvisning(?:er)?\s+kl\.?\s*(\d{1,2})(?:[.:]\d\d)?(?:\s*(?:og|,|&)\s*(\d{1,2}))?", low)
    tour_txt = ("rundvisning kl. " + tours.group(1) + (" og " + tours.group(2) if tours.group(2) else "")) if tours else ""
    # sidste åbningsdag: "søndag den 18. oktober er sidste åbningsdag"
    last = re.search(r"(\d{1,2})\.?\s+" + MON_RE + r"[^.]{0,20}sidste åbningsdag", low)
    cap = None
    if last:
        m = MONTHS[last.group(2)]; cap = datetime.date(_year_for(m, today, years), m, int(last.group(1)))
    seen = set()
    # perioder med åbningstid foran: "10-16 fra d. 10 – 18 oktober" / "10-17 fra d. 20. juni – d. 15. august"
    pat = re.compile(r"(?:kl\.\s*)?(\d{1,2})\s*[-–]\s*(\d{1,2})\s+(?:fra\s+)?(?:d\.\s*)?(\d{1,2})\.?\s*(?:" + MON_RE + r"\s*)?"
                     r"(?:[-–]|til)\s*(?:d\.\s*)?(\d{1,2})\.?\s*" + MON_RE)
    for m in pat.finditer(low):
        h1, h2, a, ma, b, mb = m.groups()
        mb_ = MONTHS[mb]; ma_ = MONTHS[ma] if ma else mb_
        y = _year_for(mb_, today, years)
        try:
            d1 = datetime.date(y if ma_ <= mb_ else y - 1, ma_, int(a)); d2 = datetime.date(y, mb_, int(b))
        except ValueError:
            continue
        if not (6 <= int(h1) < int(h2) <= 23): continue
        key = (d1, d2)
        if key in seen: continue
        seen.add(key)
        short = (d2 - d1).days <= 10
        title = ("Bornholmertårnet: familiedage" + (f" og {tour_txt}" if tour_txt else "")) if short else "Bornholmertårnet har åbent"
        out.append(_ev("bornholmertaarnet", d1, d2, title, "Bornholmertårnet, Dueodde", "Nexø", src, _hh(h1), _hh(h2)))
    # sæson i hele måneder: "åbent fra kl. 10-14 alle ugens dage i september & oktober"
    for m in re.finditer(r"kl\.\s*(\d{1,2})\s*[-–]\s*(\d{1,2})[^.]{0,40}?\bi\s+" + MON_RE + r"(?:\s*(?:&|og|til|[-–])\s*" + MON_RE + ")?", low):
        h1, h2, m1, m2 = m.groups()
        a, b = MONTHS[m1], MONTHS[m2 or m1]
        y = _year_for(b, today, years)
        d1 = datetime.date(y, a, 1)
        d2 = (datetime.date(y + (b == 12), b % 12 + 1, 1) - datetime.timedelta(days=1))
        if (d1, d2) in seen: continue
        seen.add((d1, d2))
        out.append(_ev("bornholmertaarnet", d1, d2, "Bornholmertårnet har åbent", "Bornholmertårnet, Dueodde", "Nexø", src, _hh(h1), _hh(h2)))
    if cap:
        for e in out:
            if (e.get("to") or e["d"]) > cap.isoformat(): e["to"] = cap.isoformat()
        out = [e for e in out if e["d"] <= cap.isoformat()]
        for e in out:
            if e.get("to") == e["d"]: e.pop("to")
            e.pop("long", None)
            if e.get("to") and (datetime.date.fromisoformat(e["to"]) - datetime.date.fromisoformat(e["d"])).days > 10: e["long"] = 1
    # en lang sæson, hvis resterende dage allerede dækkes af en kort periode (fx efterårsferien), droppes
    t0 = today.isoformat()
    shorts = [e for e in out if not e.get("long")]
    def covered(e):
        start, end = max(e["d"], t0), e.get("to") or e["d"]
        return any(s["d"] <= start and (s.get("to") or s["d"]) >= end for s in shorts)
    return [e for e in out if not (e.get("long") and covered(e))]

# ---------- Dideriks Veranda / Hotel Sandvig Havn (Sandvig) ----------
SANDVIG_TITLES = {"halloween": "Halloween-spøgelsestur på Dideriks Veranda"}
def parse_sandvig(text, today, src):
    lines = [re.sub(r"\s+", " ", l).strip(" ​") for l in text.splitlines()]
    lines = [l for l in lines if l]
    date = re.compile(r"(\d{1,2})(?:\s*[-–]\s*(\d{1,2}))?/(\d{1,2})-(20\d\d)")
    out = []
    for i, l in enumerate(lines):
        m = date.search(l)
        if not m: continue
        title = l[:m.start()].strip(" :–-")
        if not title and i: title = lines[i - 1].strip(" :–-")
        if not title or len(title) > 90: continue
        if "udsolgt" in (title + l).lower(): continue          # udsolgte arrangementer vises ikke
        a, b, mo, y = m.groups()
        try:
            d1 = datetime.date(int(y), int(mo), int(a)); d2 = datetime.date(int(y), int(mo), int(b)) if b else d1
        except ValueError:
            continue
        title = SANDVIG_TITLES.get(title.lower(), title)
        out.append(_ev("sandvighavn", d1, d2, title, "Dideriks Veranda, Hotel Sandvig Havn", "Allinge", src))
    return out

# id, navn, sider der hentes (teksten lægges sammen), tolker
SOURCES = [
    ("bornholmertaarnet", "Bornholmertårnet", ["https://www.bornholmertaarnet.dk/", "https://www.bornholmertaarnet.dk/efterarsferie/"], parse_bornholmertaarnet),
    ("sandvighavn", "Dideriks Veranda / Hotel Sandvig Havn", ["https://www.hotelsandvighavn.com/team-1"], parse_sandvig),
]

def run(texts, today):
    state = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {"sources": {}}
    srcs = state.setdefault("sources", {})
    t0 = today.isoformat()
    for sid, name, urls, fn in SOURCES:
        old = srcs.get(sid, {})
        txt = texts.get(sid)
        if not txt:
            print(f"{name}: kunne ikke hentes – bruger sidste gode resultat", file=sys.stderr)
            continue
        h = hashlib.sha1(txt.encode()).hexdigest()[:16]
        try:
            evs = fn(txt, today, urls[-1] if sid == "bornholmertaarnet" else urls[0])
        except Exception as e:
            print(f"{name}: tolkning fejlede: {e}", file=sys.stderr); evs = []
        evs = [e for e in evs if (e.get("to") or e["d"]) >= t0]
        if evs:
            srcs[sid] = {"name": name, "url": urls[0], "hash": h, "ok": t0, "events": evs}
            print(f"{name}: {len(evs)} arrangement(er)")
        else:
            keep = [e for e in old.get("events", []) if (e.get("to") or e["d"]) >= t0]
            srcs[sid] = {**old, "name": name, "url": urls[0], "hash": h, "events": keep}
            if old.get("hash") != h:
                srcs[sid]["changed"] = t0
                print(f"{name}: siden er ændret, men der blev ikke fundet datoer – tjek {urls[0]}", file=sys.stderr)
    state["generated"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
    return state

def fetch():
    from playwright.sync_api import sync_playwright
    texts = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(locale="da-DK")
        for sid, name, urls, fn in SOURCES:
            parts = []
            for u in urls:
                try:
                    pg.goto(u, wait_until="domcontentloaded", timeout=45000); pg.wait_for_timeout(2500)
                    parts.append(pg.evaluate("document.body ? document.body.innerText : ''"))
                except Exception as e:
                    print("Kunne ikke hente", u, e, file=sys.stderr)
            texts[sid] = "\n".join(p for p in parts if p).strip()
        b.close()
    return texts

def main():
    if "--test" in sys.argv:
        today = datetime.date(2026, 10, 11)
        texts = {sid: (TESTDIR / f"{sid}.txt").read_text(encoding="utf-8") for sid, *_ in SOURCES if (TESTDIR / f"{sid}.txt").exists()}
        print(json.dumps(run(texts, today)["sources"], ensure_ascii=False, indent=1))
        return
    state = run(fetch(), datetime.date.today())
    OUT.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")

if __name__ == "__main__":
    main()
