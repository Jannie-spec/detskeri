"""Ugentligt nyhedsbrev: én mail pr. Brevo-liste (hele Bornholm, fem byer og Gudhjem) med de næste syv dages arrangementer.

    python tools/nyhedsbrev.py --preview out/   # skriver HTML-filerne, sender intet
    python tools/nyhedsbrev.py --send            # opretter og sender kampagnerne via Brevo (kræver BREVO_API_KEY)

Lister uden tilmeldte springes over. data/nyhedsbrev.json husker, hvilke uger der er sendt, så intet sendes to gange.
Film springes over (de kører hver dag); på øbrevet også gudstjenester. Teksten er på dansk."""
import os, sys, json, html, datetime, pathlib, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "tools"))
import build, tilmeld

API = "https://api.brevo.com/v3"
SENDER = {"name": "Det sker på Bornholm", "email": "nyhedsbrev@detskeri.dk"}
REPLY_TO = "jannie@hotelklippen.dk"      # svar på nyhedsbrevet lander her (afsenderadressen har ingen postkasse)
STATE = ROOT / "data" / "nyhedsbrev.json"
GUDHJEM = {"slug": "gudhjem", "name": "Gudhjem", "towns": ["Gudhjem"], "url": "https://detskerigudhjem.dk/"}   # egen side: detskerigudhjem.dk
PER_DAY = {"bornholm": 30}            # højst så mange pr. dag i øbrevet; resten ligger på siden
E = lambda s: html.escape(str(s or ""), quote=True)
C = {"coral": "#e37b5b", "bg": "#f3f5f0", "ink": "#302f2f", "muted": "#5f625e", "brick": "#b4533a", "line": "#dde3d9", "sage": "#e5e9e1", "deep": "#3f6670"}

def items(g, events, d):
    many = g["towns"] is None
    out = []
    for e in events:
        if e.get("long") or not build.in_guide(e, g) or not build.on_day(e, d): continue
        k = build.kind_of(e)
        if k == "film" or (many and k == "kirke"): continue
        t = build.hm(e["t"]) + ("–" + build.hm(e["t2"]) if e.get("t2") else "") if e.get("t") else "Hele dagen"
        out.append({"own": bool(e.get("own")), "k": k, "t": t, "s": e.get("t") or "99", "title": e["title"], "where": e.get("where", ""), "town": e.get("town", "") if many else "",
                    "url": e.get("rurl") or e["url"], "reg": build.REGTXT.get(e.get("reg"), "")})
    out.sort(key=lambda x: (not x["own"], x["s"], x["title"]))
    return out

KIND = {"musik": ("Musik", "#f6e3da", "#b4533a"), "teater": ("Teater", "#f3dfe0", "#9c4a55"), "born": ("Børn", "#fbe9c9", "#a5701c"),
        "foredrag": ("Foredrag", "#e4ebe9", "#3f6670"), "kunst": ("Kunst", "#f3dfe0", "#9c4a55"), "mad": ("Mad", "#f6e3da", "#b4533a"),
        "sport": ("Sport", "#dfe9e4", "#3f6a55"), "kirke": ("Kirke", "#efe9df", "#8a6d45"), "andet": ("", "", "")}
SERIF = "Georgia,'Times New Roman',serif"

def render(g, events, start):
    wd, wds, mon = build.DAYNAMES["da"]
    end = start + datetime.timedelta(days=6)
    url = (g.get("url") or build.BASE + g["path"]) + "?utm_source=nyhedsbrev&utm_medium=email"
    img = f"{build.BASE}mail-{g['slug']}.png"
    ttl = build.title_of(g)
    days, total = [], 0
    for i in range(7):
        d = start + datetime.timedelta(days=i)
        its = items(g, events, d); total += len(its)
        cap = PER_DAY.get(g["slug"], 999)
        rows = []
        for x in its[:cap]:
            meta = ", ".join(p for p in (x["where"], x["town"]) if p)
            lab, bg, fg = KIND.get(x["k"], KIND["andet"])
            pill = f'<span style="display:inline-block;background:{bg};color:{fg};font-size:11px;font-weight:bold;border-radius:999px;padding:2px 8px;margin-right:6px">{E(lab)}</span>' if lab else ""
            reg = f'<br><span style="font-size:12px;font-weight:bold;color:{C["brick"]}">{E(x["reg"])}</span>' if x["reg"] else ""
            rows.append(f'<tr><td width="74" valign="top" style="padding:10px 0;border-top:1px solid {C["line"]};font-size:14px;color:{C["muted"]}">{E(x["t"])}</td>'
                        f'<td valign="top" style="padding:10px 0;border-top:1px solid {C["line"]};font-size:16px;line-height:1.35">'
                        f'<a href="{E(x["url"])}" style="color:{C["ink"]};font-weight:bold;text-decoration:none">{E(x["title"])}</a>'
                        f'<br><span style="font-size:13px;color:{C["muted"]}">{pill}{E(meta)}</span>{reg}</td></tr>')
        if not its:
            rows.append(f'<tr><td colspan="2" style="padding:10px 0;border-top:1px solid {C["line"]};color:{C["muted"]};font-size:15px">Intet i kalenderen endnu – kig forbi siden, der kommer løbende mere til.</td></tr>')
        if len(its) > cap:
            rows.append(f'<tr><td colspan="2" style="padding:10px 0;border-top:1px solid {C["line"]};font-size:14px"><a href="{E(url)}" style="color:{C["brick"]};font-weight:bold">+ {len(its) - cap} mere på detskeri.dk</a></td></tr>')
        leaf = (f'<table role="presentation" cellpadding="0" cellspacing="0" width="58" style="border:1px solid {C["line"]};border-radius:10px;background:{C["bg"]};text-align:center">'
                f'<tr><td style="background:{C["coral"] if i else C["brick"]};color:#fff;font-size:12px;font-weight:bold;padding:3px 0;border-radius:9px 9px 0 0">{wds[d.weekday()].capitalize()}</td></tr>'
                f'<tr><td style="font:400 26px/1.1 {SERIF};padding-top:3px;color:{C["ink"]}">{d.day}</td></tr>'
                f'<tr><td style="font-size:12px;color:{C["muted"]};padding-bottom:4px">{mon[d.month - 1][:3]}</td></tr></table>')
        days.append(f'<tr><td style="padding:0 0 14px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:18px">'
                    f'<tr><td style="padding:18px 18px 6px"><table role="presentation" cellpadding="0" cellspacing="0"><tr><td valign="top">{leaf}</td>'
                    f'<td valign="middle" style="padding-left:14px"><div style="font:400 24px/1.1 {SERIF};color:{C["ink"]}">{wd[d.weekday()].capitalize()}</div>'
                    f'<div style="font-size:14px;color:{C["muted"]};margin-top:2px">{d.day}. {mon[d.month - 1]} · {len(its)} {"arrangement" if len(its) == 1 else "arrangementer"}</div></td></tr></table></td></tr>'
                    f'<tr><td style="padding:4px 18px 10px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0">{"".join(rows)}</table></td></tr></table></td></tr>')
    period = f"{start.day}. {mon[start.month - 1]} – {end.day}. {mon[end.month - 1]}"
    pre = f"{total} arrangementer {build.g_in(g)} {period}. God fornøjelse!"
    body = f"""<!doctype html><html lang="da"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(ttl)}</title></head>
<body style="margin:0;background:{C['bg']};font-family:Helvetica,Arial,sans-serif;color:{C['ink']}">
<div style="display:none;max-height:0;overflow:hidden">{E(pre)}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{C['bg']}"><tr><td align="center" style="padding:16px 10px">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px">
<tr><td style="background:{C['sage']};border-radius:20px 20px 0 0;padding:26px 24px 6px">
<div style="font:400 15px {SERIF};color:{C['ink']}">detskeri.dk</div>
<div style="font:400 38px/1.02 {SERIF};color:{C['ink']};margin-top:14px">{E(ttl[: len(ttl) - len(build.g_in(g))].strip())}<br>{E(build.g_in(g))}</div>
<div style="font-size:15px;color:#4a4d49;margin-top:12px">Ugens program {E(period)} – {total} arrangementer. God fornøjelse!</div></td></tr>
<tr><td style="background:{C['sage']};line-height:0;font-size:0"><a href="{E(url)}"><img src="{img}" width="600" alt="" style="display:block;width:100%;max-width:600px;height:auto;border:0"></a></td></tr>
<tr><td style="background:{C['bg']};padding:16px 0 0"><table role="presentation" width="100%" cellpadding="0" cellspacing="0">{''.join(days)}</table></td></tr>
<tr><td style="padding:8px 24px 22px" align="center"><a href="{E(url)}" style="display:inline-block;background:{C['brick']};color:#ffffff;text-decoration:none;font-weight:bold;padding:13px 24px;border-radius:999px">Se det hele – også film og spisesteder</a></td></tr>
<tr><td style="padding:0 24px 26px;font-size:12px;line-height:1.55;color:{C['muted']}" align="center">Arrangementer fra KultuNaut. Tider kan ændre sig – tjek arrangørens side, før du tager af sted.<br>
Holder du selv et arrangement? <a href="{build.BASE}tilfoej/" style="color:{C['brick']}">Fortæl os om det</a>.<br>
Du får denne mail, fordi du har tilmeldt dig på detskeri.dk. <a href="{{{{ unsubscribe }}}}" style="color:{C['muted']}">Afmeld</a></td></tr>
</table></td></tr></table></body></html>"""
    body = body.replace('<a href="', '<a target="_blank" href="')
    subject = f"{ttl[0].upper() + ttl[1:]} {period}"
    return subject, body, total

def api(method, path, key, data=None):
    req = urllib.request.Request(API + path, method=method, data=json.dumps(data).encode() if data is not None else None,
                                 headers={"api-key": key, "accept": "application/json", "content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            txt = r.read().decode()
            return json.loads(txt) if txt else {}
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{method} {path}: {e.code} {e.read().decode()[:300]}")

def main():
    args = sys.argv[1:]
    build.LANG = "da"
    events = build.all_events(json.loads((ROOT / "data" / "events.json").read_text(encoding="utf-8"))["events"])
    start = datetime.datetime.now(build.TZ).date()
    week = f"{start.isocalendar()[0]}-W{start.isocalendar()[1]:02d}"
    lists = dict(tilmeld.LISTS)
    guides = [g for g in build.GUIDES + [GUDHJEM] if g["slug"] in lists]
    if "--preview" in args:
        out = pathlib.Path(args[args.index("--preview") + 1]); out.mkdir(parents=True, exist_ok=True)
        for g in guides:
            s, b, n = render(g, events, start)
            (out / f"{g['slug']}.html").write_text(b, encoding="utf-8"); print(g["slug"], n, "|", s)
        return
    if "--send" not in args: print(__doc__); return
    key = os.environ.get("BREVO_API_KEY")
    if not key: print("BREVO_API_KEY mangler – intet sendt."); return
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    for g in guides:
        lid = lists[g["slug"]]
        if state.get(g["slug"]) == week: print(g["slug"], "allerede sendt", week); continue
        info = api("GET", f"/contacts/lists/{lid}", key)
        subs = info.get("uniqueSubscribers", info.get("totalSubscribers", 0))
        if not subs: print(g["slug"], "ingen tilmeldte"); continue
        s, b, n = render(g, events, start)
        if n == 0: print(g["slug"], "ingen arrangementer – springes over"); continue
        c = api("POST", "/emailCampaigns", key, {"name": f"Det sker – {g['name']} – {week}", "subject": s, "sender": SENDER,
                                                   "htmlContent": b, "recipients": {"listIds": [lid]}, "inlineImageActivation": False, "replyTo": REPLY_TO})
        api("POST", f"/emailCampaigns/{c['id']}/sendNow", key)
        state[g["slug"]] = week
        STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
        print(g["slug"], "sendt til", subs, "–", s)

if __name__ == "__main__":
    main()
