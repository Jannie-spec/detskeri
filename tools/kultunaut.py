"""Henter arrangementer for Bornholms byer fra KultuNaut → data/events.json.

Køres hver morgen af GitHub Actions (kræver Playwright + Chromium):
    python tools/kultunaut.py
Hver by hentes for sig (postby), så hvert arrangement får sin by. Et år frem.
Tilmelding/billet på forhånd læses fra arrangementets egen side for de nærmeste 45 dage
og gemmes i data/reg.json, så hver side kun hentes én gang.
"""
import re, json, datetime, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "events.json"
REGF = ROOT / "data" / "reg.json"
LIST = "https://www.kultunaut.dk/perl/arrlist2/type-nynaut?startnr={start}&Area={area}&antal=300&"
MORE = "https://www.kultunaut.dk/perl/arrmore/type-nynaut?ArrNr={nr}"
# postby på KultuNaut → bynavn
TOWNS = {"R%F8nne-postby": "Rønne", "Aakirkeby-postby": "Aakirkeby", "Nex%F8-postby": "Nexø", "Svaneke-postby": "Svaneke",
         "%D8stermarie-postby": "Østermarie", "Gudhjem-postby": "Gudhjem", "Allinge-postby": "Allinge",
         "Klemensker-postby": "Klemensker", "Hasle-postby": "Hasle"}
DAYS_AHEAD = 366
REG_DAYS = 45
MON = {"jan":1,"feb":2,"mar":3,"apr":4,"maj":5,"jun":6,"jul":7,"aug":8,"sep":9,"okt":10,"nov":11,"dec":12}
WD = {"søn":0,"man":1,"tir":2,"ons":3,"tor":4,"fre":5,"lør":6}
D = r"(?:man|tir|ons|tor|fre|lør|søn)\.\s+(\d{1,2})\.(?:\s+(?!til\b)([a-zæøå]{3})\.?)?(?:\s+(\d{4}))?"

JS = """() => [...document.querySelectorAll('div.product[data-arrnr]')].map(p => [
  p.dataset.arrnr, (p.querySelector('.genre_cat')||{}).textContent||'', (p.querySelector('h3')||{}).textContent||'',
  ((p.querySelector('time')||{}).textContent||'').replace(/\\s+/g,' ')])"""

def hhmm(s):
    h, _, m = s.replace(":", ".").partition(".")
    return f"{int(h):02d}:{(m or '00'):0>2}"

def parse_one(nr, genre, title, when, town):
    when = when.strip(); title = re.sub(r"\s+", " ", title).strip(); genre = genre.strip()
    if "," not in when: return None
    w, where = when.rsplit(",", 1); where = where.strip()
    m = re.match(rf"{D}(?:\s+til\s+{D})?(.*)$", w.strip(), re.I)
    if not m: return None
    d1, mo1, y1, d2, mo2, y2, rest = m.groups()
    if not (y2 or y1):      # intet årstal: nærmeste kommende forekomst
        t = datetime.date.today(); mo = MON[(mo2 or mo1).lower()[:3]]
        y1 = str(t.year + (1 if mo < t.month else 0))
    y_end = int(y2 or y1); mo_end = MON[(mo2 or mo1).lower()[:3]]
    end = datetime.date(y_end, mo_end, int(d2)) if d2 else None
    mo_s = MON[(mo1 or mo2).lower()[:3]]; y_s = int(y1 or y2)
    if end and (mo_s > mo_end): y_s = y_end - 1
    start = datetime.date(y_s, mo_s, int(d1))
    if end is None: end = start
    ev = {"id": nr, "d": start.isoformat(), "title": title, "where": where.split(" - ")[0].strip(), "town": town,
          "url": MORE.format(nr=nr), "g": genre}
    if end != start: ev["to"] = end.isoformat()
    if (end - start).days > 10: ev["long"] = 1        # udstillinger o.l.: kun i "Længere frem"
    rest = rest.strip()
    days = re.match(r"(man|tir|ons|tor|fre|lør|søn)-(man|tir|ons|tor|fre|lør|søn)", rest, re.I)
    if days:
        a, b = WD[days.group(1).lower()], WD[days.group(2).lower()]
        ev["wd"] = [x % 7 for x in range(a, b + (7 if b < a else 0) + 1)]
    t = re.search(r"kl\.\s*(\d{1,2}(?:[.:]\d{2})?)(?:-(\d{1,2}(?:[.:]\d{2})?))?", rest)
    if t:
        ev["t"] = hhmm(t.group(1))
        if t.group(2): ev["t2"] = hhmm(t.group(2))
    return ev

def parse(rows, today=None):
    today = today or datetime.date.today()
    last = (today + datetime.timedelta(days=DAYS_AHEAD)).isoformat(); t0 = today.isoformat()
    out, seen = [], set()
    for r in rows:
        try:
            ev = parse_one(*r)
        except Exception as e:
            print("Sprang over:", r[3][:60], e, file=sys.stderr); continue
        if not ev or (ev.get("to") or ev["d"]) < t0 or ev["d"] > last: continue
        k = (ev["d"], ev.get("t"), ev["title"], ev["where"])
        if k in seen: continue
        seen.add(k); out.append(ev)
    out.sort(key=lambda e: (e["d"], e.get("t", ""), e["title"]))
    return out

def fetch(pg, area, town):
    rows, ids, start = [], set(), 1
    while start < 5000:
        pg.goto(LIST.format(start=start, area=area), wait_until="domcontentloaded", timeout=60000)
        got = pg.evaluate(JS)
        new = [r for r in got if r[0] not in ids]
        if not new: break
        for r in new: ids.add(r[0]); rows.append(r + [town])
        start += len(got)
    return rows

REG = re.compile(r"forhånds?tilmeld|tilmelding\s+(?:på forhånd|er nødvendig|nødvendig|påkrævet|kræves|senest)|kræver\s+(?:forhånds)?tilmelding|skal\s+tilmeldes|tilmeld(?:ing)?\s+(?:dig\s+)?(?:på|via|hos|til)\b|billet(?:ter)?\s+(?:købes|bestilles|skal købes)\s+på forhånd", re.I)
SOME = re.compile(r"\bnogle\b|\benkelte\b", re.I)
JS_MORE = """() => { const a = document.querySelector('article'); if (!a) return null;
  const links = [...a.querySelectorAll('a[href^="http"]')].map(x => x.href).filter(h => !/kultunaut\\.dk|facebook\\.com\\/sharer/.test(h));
  const bil = [...a.querySelectorAll('a')].find(x => /bestil billet|køb billet/i.test(x.textContent));
  return [a.innerText || a.textContent || '', links[0] || '', bil ? bil.href : ''] }"""

def registration(pg, events, cache, today, budget=300):
    """reg: 1 = kræver tilmelding, 2 = tilmelding til nogle aktiviteter, 3 = billet på forhånd. Gemmes i cache pr. arrangement."""
    limit = (today + datetime.timedelta(days=REG_DAYS)).isoformat()
    for ev in events:
        if ev["d"] > limit or ev["id"] in cache or budget <= 0: continue
        budget -= 1
        try:
            pg.goto(ev["url"], wait_until="domcontentloaded", timeout=30000)
            r = pg.evaluate(JS_MORE)
        except Exception:
            continue
        res = [0, ""]
        if r:
            txt, link, billet = r
            for sent in re.split(r"(?<=[.!?\n])", txt):
                if REG.search(sent):
                    res = [2 if SOME.search(sent) else 1, billet or link or ev["url"]]; break
            else:
                if billet: res = [3, billet]
        cache[ev["id"]] = res
    for ev in events:
        r = cache.get(ev["id"])
        if r and r[0]:
            ev["reg"], ev["rurl"] = r
    return events

def main():
    from playwright.sync_api import sync_playwright
    today = datetime.date.today()
    cache = json.loads(REGF.read_text(encoding="utf-8")) if REGF.exists() else {}
    rows, ok = [], 0
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(locale="da-DK")
        for area, town in TOWNS.items():
            try:
                r = fetch(pg, area, town); rows += r; ok += 1
                print(town, len(r))
            except Exception as e:
                print("Fejl ved", town, e, file=sys.stderr)
        events = parse(rows, today)
        if ok < len(TOWNS) - 1 or len(events) < 100:
            print("For få data – beholder de gamle", file=sys.stderr); sys.exit(1)
        registration(pg, events, cache, today)
        b.close()
    keep = {e["id"] for e in events}
    cache = {k: v for k, v in cache.items() if k in keep}
    OUT.write_text(json.dumps({"generated": datetime.datetime.now().isoformat(timespec="minutes"), "events": events},
                              ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    REGF.write_text(json.dumps(cache, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print("Arrangementer:", len(events))

if __name__ == "__main__":
    main()
