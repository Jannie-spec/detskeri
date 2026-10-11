"""Dagligt Facebook-opslag på "Det sker på Bornholm" og "Det sker i Gudhjem": et billede med dagens program
i samme stil som nyhedsbrevet (byens tegning, dagens dato, arrangementerne) og en kort tekst, der sender folk
videre til hjemmesiden og nyhedsbrevet for at se længere frem.

    python tools/facebook.py --preview [mappe]   # skriver billeder + tekster (standard: out/facebook), slår intet op
    python tools/facebook.py --post              # slår dagens opslag op via Meta Graph API
    python tools/facebook.py --check [side]      # tjekker kun, at tokens virker og ikke udløber
    --dato ÅÅÅÅ-MM-DD                            # lav opslaget for en anden dag (til test)

Hemmeligheder (GitHub → Settings → Secrets and variables → Actions):
    FB_PAGE_TOKEN_BORNHOLM   sideadgangstoken til "Det sker på Bornholm"
    FB_PAGE_TOKEN_GUDHJEM    sideadgangstoken til "Det sker i Gudhjem"
En side uden token springes over. data/facebook.json husker, hvilke dage der er slået op, så intet kommer to gange.

Stil (Jannies ønske): enkel tekst, højst én emoji, Klippens egne arrangementer først."""
import os, sys, json, html, uuid, datetime, pathlib, urllib.request, urllib.parse, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "tools"))
import build, nyhedsbrev

GRAPH = "https://graph.facebook.com/v26.0"
STATE = ROOT / "data" / "facebook.json"
PAGES = [
    {"slug": "bornholm", "secret": "FB_PAGE_TOKEN_BORNHOLM", "name": "Bornholm", "in": "på Bornholm",
     "guide": build.GUIDES[0], "link": "https://detskeri.dk/bornholm/"},
    {"slug": "gudhjem", "secret": "FB_PAGE_TOKEN_GUDHJEM", "name": "Gudhjem", "in": "i Gudhjem",
     "guide": nyhedsbrev.GUDHJEM, "link": "https://detskerigudhjem.dk/"},
]
NEWS = "https://detskeri.dk/#nyhedsbrev"
MAX_ROWS = 6                       # flere end det står som "+ N mere på detskeri.dk"
C = nyhedsbrev.C
E = lambda s: html.escape(str(s or ""), quote=True)
SERIF = "Georgia,'DejaVu Serif',serif"
SANS = "Helvetica,Arial,'DejaVu Sans',sans-serif"

def emoji(d):
    m = d.month
    return "🍂" if m in (9, 10, 11) else "❄️" if m in (12, 1, 2) else "🌷" if m in (3, 4, 5) else "☀️"

def day_items(p, events, d):
    build.LANG = "da"
    return [x for x in nyhedsbrev.items(p["guide"], events, d) if x["k"] != "kirke"]     # gudstjenester fylder for meget på Facebook

def card_html(p, its, d):
    """Billedet: samme farver, skrift og tegning som nyhedsbrevet – kort til Facebook (1080 bredt)."""
    wd, wds, mon = build.DAYNAMES["da"]
    rows = []
    for x in its[:MAX_ROWS]:
        meta = ", ".join(q for q in (x["where"], x["town"]) if q)
        lab, bg, fg = nyhedsbrev.KIND.get(x["k"], nyhedsbrev.KIND["andet"])
        pill = f'<span class="pill" style="background:{bg};color:{fg}">{E(lab)}</span>' if lab else ""
        rows.append(f'<tr><td class="t">{E(x["t"])}</td><td><div class="ti">{E(x["title"])}</div>'
                    f'<div class="m">{pill}{E(meta)}</div></td></tr>')
    more = len(its) - MAX_ROWS
    if more > 0:
        rows.append(f'<tr><td></td><td class="more">+ {more} mere på detskeri.dk</td></tr>')
    img = (ROOT / "static" / f"mail-{p['slug']}.png").as_uri()
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box}} body{{margin:0;width:1080px;background:{C['bg']};font-family:{SANS};color:{C['ink']}}}
.top{{background:{C['sage']};padding:36px 52px 14px}} .brand{{font:400 26px {SERIF};display:flex;justify-content:space-between;color:{C['ink']}}}
.h{{font:400 72px/1.0 {SERIF};margin-top:18px}} .sub{{font-size:28px;color:#4a4d49;margin-top:16px}}
.draw{{background:{C['sage']};line-height:0}} .draw{{overflow:hidden}} .draw img{{width:1080px;display:block;margin-top:-18px}}
.card{{background:#fff;border-radius:30px;margin:24px 36px 0;padding:24px 36px 12px}}
.day{{display:flex;align-items:center;gap:24px;margin-bottom:8px}}
.leaf{{width:96px;border:2px solid {C['line']};border-radius:16px;background:{C['bg']};text-align:center;overflow:hidden}}
.leaf .w{{background:{C['brick']};color:#fff;font-size:20px;font-weight:bold;padding:5px 0}} .leaf .n{{font:400 44px/1.1 {SERIF};padding-top:4px}}
.leaf .mo{{font-size:19px;color:{C['muted']};padding-bottom:6px}}
.dn{{font:400 42px/1.1 {SERIF}}} .dc{{font-size:24px;color:{C['muted']};margin-top:4px}}
table{{width:100%;border-collapse:collapse}} td{{border-top:2px solid {C['line']};padding:12px 0;vertical-align:top}}
td.t{{width:150px;font-size:24px;color:{C['muted']}}} .ti{{font-size:29px;font-weight:bold;line-height:1.25}}
.m{{font-size:22px;color:{C['muted']};margin-top:6px}} .pill{{display:inline-block;font-size:18px;font-weight:bold;border-radius:999px;padding:3px 13px;margin-right:10px}}
.more{{font-size:25px;font-weight:bold;color:{C['brick']}}}
.foot{{text-align:center;padding:24px 40px 30px}} .btn{{display:inline-block;background:{C['brick']};color:#fff;font-weight:bold;font-size:28px;padding:20px 40px;border-radius:999px}}
.small{{font-size:22px;color:{C['muted']};margin-top:18px}}
</style></head><body>
<div class="top"><div class="brand"><span>detskeri.dk</span><span>{d.day}. {mon[d.month - 1]}</span></div>
<div class="h">Det sker<br>{E(p['in'])} i dag</div>
</div>
<div class="draw"><img src="{img}"></div>
<div class="card"><div class="day"><div class="leaf"><div class="w">{wds[d.weekday()].capitalize()}</div><div class="n">{d.day}</div><div class="mo">{mon[d.month - 1][:3]}</div></div>
<div><div class="dn">{wd[d.weekday()].capitalize()}</div><div class="dc">{d.day}. {mon[d.month - 1]} · {len(its)} {"arrangement" if len(its) == 1 else "arrangementer"}</div></div></div>
<table>{''.join(rows)}</table></div>
<div class="foot"><span class="btn">Se hele ugen på {E(p['link'].split('//')[1].rstrip('/').split('/')[0])}</span>
<div class="small">Få ugens program på mail hver torsdag – gratis</div></div>
</body></html>"""

def caption(p, its, d):
    wd, _, mon = build.DAYNAMES["da"]
    lines = [f"Det sker {p['in']} i dag – {wd[d.weekday()]} {d.day}. {mon[d.month - 1]} {emoji(d)}", ""]
    own = [x for x in its if x["own"]]
    for x in own[:3]:
        where = f" – {x['where']}" if x["where"] else ""
        lines.append(f"• {x['title']}{where} kl. {x['t']}" if x["t"] != "Hele dagen" else f"• {x['title']}{where}")
    if own: lines.append("")
    n = len(its)
    lines.append(f"{n} {'arrangement' if n == 1 else 'arrangementer'} i dag – hele dagens program står på billedet.")
    lines += ["", "Se hvad der sker resten af ugen, film og spisesteder med åbent:", p["link"],
              "", "Få ugens program på mail hver torsdag – gratis:", NEWS]
    return "\n".join(lines)

def render_png(page_html, path):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 800})
        tmp = path.with_suffix(".html"); tmp.write_text(page_html, encoding="utf-8")
        pg.goto(tmp.as_uri()); pg.wait_for_timeout(300)
        pg.screenshot(path=str(path), full_page=True)
        b.close()

def post_photo(token, png, message):
    """Billede + tekst som ét opslag (multipart-upload til me/photos; med et sidetoken er "me" siden selv)."""
    bnd = uuid.uuid4().hex
    parts = []
    for k, v in (("message", message), ("published", "true"), ("access_token", token)):
        parts.append(f'--{bnd}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    parts.append(f'--{bnd}\r\nContent-Disposition: form-data; name="source"; filename="dagens-program.png"\r\nContent-Type: image/png\r\n\r\n'.encode()
                 + png.read_bytes() + b"\r\n")
    parts.append(f"--{bnd}--\r\n".encode())
    req = urllib.request.Request(f"{GRAPH}/me/photos", data=b"".join(parts), method="POST",
                                 headers={"Content-Type": f"multipart/form-data; boundary={bnd}"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Facebook svarede {e.code}: {e.read().decode()[:300]}")

def check(args):
    only = args[args.index("--check") + 1] if len(args) > args.index("--check") + 1 and not args[args.index("--check") + 1].startswith("--") else None
    pages = [p for p in PAGES if not only or p["slug"] == only]
    ok = 0
    for p in pages:
        token = os.environ.get(p["secret"])
        if not token: print(p["name"], "– intet token"); continue
        q = urllib.parse.quote(token)
        try:
            with urllib.request.urlopen(f"{GRAPH}/me?fields=name&access_token={q}", timeout=30) as r:
                name = json.loads(r.read().decode()).get("name", "")
            if name.lower() != f"det sker {p['in']}".lower():
                print(p["name"], "– token hører til", repr(name), "og ikke til siden (brug sidens egen access_token fra me/accounts)"); continue
            with urllib.request.urlopen(f"{GRAPH}/debug_token?input_token={q}&access_token={q}", timeout=30) as r2:
                exp = json.loads(r2.read().decode()).get("data", {}).get("expires_at", -1)
            if exp == 0: print(p["name"], "– token virker for siden og udløber aldrig:", name); ok += 1
            else: print(p["name"], "– token virker, men UDLØBER", exp, "– lav det fra en forlænget (Extend) nøgle")
        except urllib.error.HTTPError as e:
            print(p["name"], "– token virker IKKE:", e.code, e.read().decode()[:200])
    sys.exit(0 if ok == len(pages) else 1)

def main():
    args = sys.argv[1:]
    if "--check" in args: return check(args)
    build.LANG = "da"
    events = build.all_events(json.loads((ROOT / "data" / "events.json").read_text(encoding="utf-8"))["events"])
    d = datetime.datetime.now(build.TZ).date()
    if "--dato" in args: d = datetime.date.fromisoformat(args[args.index("--dato") + 1])
    out = ROOT / "out" / "facebook"
    if "--preview" in args:
        i = args.index("--preview")
        if len(args) > i + 1 and not args[i + 1].startswith("--"): out = pathlib.Path(args[i + 1])
    out.mkdir(parents=True, exist_ok=True)
    if "--preview" in args:
        for p in PAGES:
            its = day_items(p, events, d)
            print(f"===== {p['name']} ({len(its)} arrangementer) =====\n{caption(p, its, d)}\n")
            if its: render_png(card_html(p, its, d), out / f"{p['slug']}.png")
        print("Billeder i", out); return
    if "--post" not in args: print(__doc__); return
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    for p in PAGES:
        token = os.environ.get(p["secret"])
        if not token: print(p["name"], "– intet token, springes over"); continue
        if state.get(p["slug"]) == d.isoformat(): print(p["name"], "– allerede slået op i dag"); continue
        its = day_items(p, events, d)
        if not its: print(p["name"], "– ingen arrangementer i dag, springes over"); continue
        png = out / f"{p['slug']}.png"
        render_png(card_html(p, its, d), png)
        r = post_photo(token, png, caption(p, its, d))
        state[p["slug"]] = d.isoformat()
        STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
        print(p["name"], "– slået op:", r.get("post_id") or r.get("id"))

if __name__ == "__main__":
    main()
