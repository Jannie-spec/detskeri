"""Ugentligt Facebook-opslag på "Det sker på Bornholm" og "Det sker i Gudhjem" (torsdag, efter nyhedsbrevet).

    python tools/facebook.py --preview      # viser opslagene, slår intet op
    python tools/facebook.py --post         # slår op via Meta Graph API (kræver hemmelighederne nedenfor)
    python tools/facebook.py --check        # tjekker kun, at tokens virker (viser sidenavnene)

Hemmeligheder (GitHub → Settings → Secrets and variables → Actions):
    FB_PAGE_TOKEN_BORNHOLM   sideadgangstoken til "Det sker på Bornholm"
    FB_PAGE_TOKEN_GUDHJEM    sideadgangstoken til "Det sker i Gudhjem"
En side uden token springes stille over. data/facebook.json husker, hvilke uger der er slået op, så intet kommer to gange.

Stil (Jannies ønske): enkle punkter, STORE dagsoverskrifter, højst én emoji (i overskriften),
Klippens egne arrangementer først, link til siden og til nyhedsbrevet til sidst."""
import os, re, sys, json, datetime, pathlib, urllib.request, urllib.parse, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import build

GRAPH = "https://graph.facebook.com/v26.0"
STATE = ROOT / "data" / "facebook.json"
PAGES = [
    {"slug": "bornholm", "id": "61595319058631", "secret": "FB_PAGE_TOKEN_BORNHOLM", "name": "Bornholm", "in": "på Bornholm", "towns": None,
     "link": "https://detskeri.dk/bornholm/", "foot": "Alt hvad der sker i dag, film og spisesteder med åbent:", "max": 10, "own_ahead": 0},
    {"slug": "gudhjem", "id": "61595158205580", "secret": "FB_PAGE_TOKEN_GUDHJEM", "name": "Gudhjem", "in": "i Gudhjem", "towns": ["Gudhjem"],
     "link": "https://detskerigudhjem.dk/", "foot": "Hele programmet og spisesteder med åbent:", "max": 8, "own_ahead": 10},
]
NEWS = "Få ugens program på mail hver torsdag – gratis:\ndetskeri.dk"
DAYS = ["MANDAG", "TIRSDAG", "ONSDAG", "TORSDAG", "FREDAG", "LØRDAG", "SØNDAG"]
# hvad der helst skal med – film og gudstjenester springes over
NOW = "00:00"        # klokkeslæt nu (sættes i main); dagens arrangementer, der er forbi, kommer ikke med
RANK = {"musik": 0, "teater": 0, "mad": 1, "born": 1, "kunst": 2, "foredrag": 2, "sport": 3, "andet": 3}
# own_ahead: Klippens egne arrangementer nævnes så mange dage frem (0 = kun når de er i weekenden)

def emoji(d):
    m = d.month
    return "🍂" if m in (9, 10, 11) else "❄️" if m in (12, 1, 2) else "🌷" if m in (3, 4, 5) else "☀️"

def _key(t):
    t = re.sub(r"\s*@.*$", "", t.lower())            # "Oktoberfest @ Smedjen" = "Oktoberfest"
    return re.sub(r"[^a-zæøå0-9]", "", t)[:28]

def line(e, many, with_day=False):
    where = e.get("where", "")
    if many and e["town"] and e["town"].lower() not in (where + " " + e["title"]).lower():
        where = f"{where}, {e['town']}" if where else e["town"]
    t = ""
    if e.get("t"):
        t = " kl. " + build.hm(e["t"]) + ("–" + build.hm(e["t2"]) if e.get("t2") else "")
    title = re.sub(r"\s*@.*$", "", e["title"]).strip()
    day = ""
    if with_day:
        d1 = datetime.date.fromisoformat(e["d"]); d2 = datetime.date.fromisoformat(e.get("to") or e["d"])
        mon = build.DAYNAMES["da"][2]
        day = (f"{d1.day}.–{d2.day}. {mon[d2.month - 1][:3]}." if d1.month == d2.month else f"{d1.day}/{d1.month}–{d2.day}/{d2.month}") if d2 != d1 \
            else f"{DAYS[d1.weekday()].lower()[:3]}. {d1.day}. {mon[d1.month - 1][:3]}."
        return f"• {title} – {where}, {day}{t}".replace(" – , ", " – ")
    return f"• {title} – {where}{t}" if where else f"• {title}{t}"

def compose(p, events, today):
    many = p["towns"] is None
    g = {"towns": p["towns"]}
    end = today + datetime.timedelta(days=(6 - today.weekday()) % 7 or 7)      # til og med søndag
    if today.weekday() == 6: end = today
    own_end = max(end, today + datetime.timedelta(days=p["own_ahead"]))
    seen, used = set(), set()
    # 1) Klippens egne arrangementer, der starter eller kører i perioden
    own = [e for e in events if e.get("own") and build.in_guide(e, g)
           and (e.get("to") or e["d"]) >= today.isoformat() and e["d"] <= own_end.isoformat()]
    own.sort(key=lambda e: (e["d"], e.get("t", "")))
    own_lines = []
    for e in own:
        k = _key(e["title"])
        if k in seen: continue
        seen.add(k); used.add(e["id"]); own_lines.append(line(e, many, with_day=True))
    # 2) KultuNaut, dag for dag
    budget = max(p["max"] - len(own_lines), 5)
    per_day = {}
    d = today
    while d <= end:
        cand = []
        for e in events:
            if e["id"] in used or e.get("own") or e.get("long") or not build.in_guide(e, g) or not build.on_day(e, d): continue
            k = build.kind_of(e)
            if k in ("film", "kirke") or not e.get("t"): continue
            if d == today and (e.get("t2") or e["t"]) <= NOW: continue      # allerede forbi i dag
            cand.append((RANK.get(k, 3), e.get("t", ""), e))
        cand.sort(key=lambda x: (x[0], x[1]))
        per_day[d] = [c[2] for c in cand]
        d += datetime.timedelta(days=1)
    # fordel pladserne jævnt over dagene (weekenden først)
    order = sorted(per_day, key=lambda x: (x.weekday() < 4, x))
    picked = {x: [] for x in per_day}
    while budget > 0 and any(per_day.values()):
        for x in order:
            while per_day[x] and budget > 0:
                e = per_day[x].pop(0)
                k = _key(e["title"])
                if k in seen: continue
                seen.add(k); picked[x].append(e); budget -= 1
                break
    blocks = []
    if own_lines: blocks.append("\n".join(own_lines))
    for x in sorted(picked):
        if not picked[x]: continue
        rows = sorted(picked[x], key=lambda e: e.get("t", ""))
        head = "I DAG" if x == today else DAYS[x.weekday()]
        blocks.append(head + "\n" + "\n".join(line(e, many) for e in rows))
    if not blocks: return None
    title = f"Det sker {p['in']} i weekenden {emoji(today)}" if today.weekday() >= 3 else f"Det sker {p['in']} {emoji(today)}"
    return "\n\n".join([title] + blocks + [f"{p['foot']}\n{p['link']}", NEWS])

def post(page_id, token, message, link):
    data = urllib.parse.urlencode({"message": message, "link": link, "access_token": token}).encode()
    req = urllib.request.Request(f"{GRAPH}/me/feed", data=data, method="POST")   # med et sidetoken er "me" siden selv
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Facebook svarede {e.code}: {e.read().decode()[:300]}")

def main():
    args = sys.argv[1:]
    build.LANG = "da"
    events = build.all_events(json.loads((ROOT / "data" / "events.json").read_text(encoding="utf-8"))["events"])
    global NOW
    now = datetime.datetime.now(build.TZ); today = now.date(); NOW = now.strftime("%H:%M")
    if "--dato" in args: today = datetime.date.fromisoformat(args[args.index("--dato") + 1]); NOW = "00:00"
    week = f"{today.isocalendar()[0]}-W{today.isocalendar()[1]:02d}"
    if "--preview" in args:
        for p in PAGES:
            print(f"===== {p['name']} =====\n{compose(p, events, today)}\n")
        return
    if "--check" in args:
        ok = 0
        only = args[args.index("--check") + 1] if len(args) > args.index("--check") + 1 else None
        pages = [p for p in PAGES if not only or p["slug"] == only]
        for p in pages:
            token = os.environ.get(p["secret"])
            if not token: print(p["name"], "– intet token"); continue
            try:
                with urllib.request.urlopen(f"{GRAPH}/me?fields=name&access_token={urllib.parse.quote(token)}", timeout=30) as r:
                    name = json.loads(r.read().decode()).get("name", "")
                    if name.lower() == f"det sker {p['in']}".lower():
                        q = urllib.parse.quote(token)
                        with urllib.request.urlopen(f"{GRAPH}/debug_token?input_token={q}&access_token={q}", timeout=30) as r2:
                            exp = json.loads(r2.read().decode()).get("data", {}).get("expires_at", -1)
                        if exp == 0:
                            print(p["name"], "– token virker for siden og udløber aldrig:", name); ok += 1
                        else:
                            print(p["name"], "– token virker, men UDLØBER", exp, "– lav det fra en forlænget (Extend) nøgle")
                    else:
                        print(p["name"], "– token hører til", repr(name), "og ikke til siden (brug sidens egen access_token fra me/accounts)")
            except urllib.error.HTTPError as e:
                print(p["name"], "– token virker IKKE:", e.code, e.read().decode()[:200])
        sys.exit(0 if ok == len(pages) else 1)
    if "--post" not in args: print(__doc__); return
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    for p in PAGES:
        token = os.environ.get(p["secret"])
        if not token: print(p["name"], "– intet token, springes over"); continue
        if state.get(p["slug"]) == week: print(p["name"], "– allerede slået op", week); continue
        msg = compose(p, events, today)
        if not msg: print(p["name"], "– ingen arrangementer, springes over"); continue
        r = post(p["id"], token, msg, p["link"])
        state[p["slug"]] = week
        STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
        print(p["name"], "– slået op:", r.get("id"))

if __name__ == "__main__":
    main()
