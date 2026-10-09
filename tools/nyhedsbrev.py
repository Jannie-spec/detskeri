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
STATE = ROOT / "data" / "nyhedsbrev.json"
GUDHJEM = {"slug": "gudhjem", "name": "Gudhjem", "towns": ["Gudhjem"], "url": "https://detskerigudhjem.dk/"}   # egen side: detskerigudhjem.dk
PER_DAY = {"bornholm": 30}            # højst så mange pr. dag i øbrevet; resten ligger på siden
E = lambda s: html.escape(str(s or ""), quote=True)
C = {"bg": "#f3f5f0", "ink": "#302f2f", "muted": "#5f625e", "brick": "#b4533a", "line": "#dde3d9", "sage": "#e5e9e1", "deep": "#3f6670"}

def items(g, events, d):
    many = g["towns"] is None
    out = []
    for e in events:
        if e.get("long") or not build.in_guide(e, g) or not build.on_day(e, d): continue
        k = build.kind_of(e)
        if k == "film" or (many and k == "kirke"): continue
        t = build.hm(e["t"]) + ("–" + build.hm(e["t2"]) if e.get("t2") else "") if e.get("t") else "Hele dagen"
        out.append({"t": t, "s": e.get("t") or "99", "title": e["title"], "where": e.get("where", ""), "town": e.get("town", "") if many else "",
                    "url": e.get("rurl") or e["url"], "reg": build.REGTXT.get(e.get("reg"), "")})
    out.sort(key=lambda x: (x["s"], x["title"]))
    return out

def render(g, events, start):
    wd, _, mon = build.DAYNAMES["da"]
    end = start + datetime.timedelta(days=6)
    url = (g.get("url") or build.BASE + g["path"]) + "?utm_source=nyhedsbrev&utm_medium=email"
    ttl = build.title_of(g)
    rows, total = [], 0
    for i in range(7):
        d = start + datetime.timedelta(days=i)
        its = items(g, events, d); total += len(its)
        cap = PER_DAY.get(g["slug"], 999)
        rows.append(f'<tr><td style="padding:22px 0 6px;font:400 20px/1.2 Georgia,serif;color:{C["ink"]};border-bottom:2px solid {C["brick"]}">'
                    f'{wd[d.weekday()].capitalize()} {d.day}. {mon[d.month - 1]}</td></tr>')
        if not its:
            rows.append(f'<tr><td style="padding:10px 0;color:{C["muted"]};font-size:15px">Intet i kalenderen endnu.</td></tr>')
        for x in its[:cap]:
            meta = ", ".join(p for p in (x["where"], x["town"]) if p)
            reg = f' <span style="font-size:12px;font-weight:bold;color:{C["brick"]}">· {E(x["reg"])}</span>' if x["reg"] else ""
            rows.append(f'<tr><td style="padding:9px 0;border-bottom:1px solid {C["line"]}"><table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>'
                        f'<td width="96" valign="top" style="font-size:14px;color:{C["muted"]};padding-top:2px">{E(x["t"])}</td>'
                        f'<td valign="top" style="font-size:16px;line-height:1.35"><a href="{E(x["url"])}" style="color:{C["ink"]};font-weight:bold;text-decoration:none">{E(x["title"])}</a>{reg}'
                        f'<br><span style="font-size:14px;color:{C["muted"]}">{E(meta)}</span></td></tr></table></td></tr>')
        if len(its) > cap:
            rows.append(f'<tr><td style="padding:10px 0;font-size:14px"><a href="{E(url)}" style="color:{C["brick"]}">+ {len(its) - cap} mere på detskeri.dk</a></td></tr>')
    period = f"{start.day}. {mon[start.month - 1]}" + f" – {end.day}. {mon[end.month - 1]}"
    pre = f"{total} arrangementer {build.g_in(g)} {period}."
    body = f"""<!doctype html><html lang="da"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(ttl)}</title></head>
<body style="margin:0;background:{C['bg']};font-family:Helvetica,Arial,sans-serif;color:{C['ink']}">
<div style="display:none;max-height:0;overflow:hidden">{E(pre)}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{C['bg']}"><tr><td align="center" style="padding:20px 12px">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;background:#ffffff;border-radius:18px">
<tr><td style="background:{C['sage']};border-radius:18px 18px 0 0;padding:26px 24px 20px">
<div style="font:400 15px Georgia,serif;color:{C['muted']}">detskeri.dk · ugens program</div>
<div style="font:400 32px/1.05 Georgia,serif;color:{C['ink']};margin-top:8px">{E(ttl)}</div>
<div style="font-size:15px;color:{C['muted']};margin-top:8px">{E(period)} · {total} arrangementer</div></td></tr>
<tr><td style="padding:4px 24px 10px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0">{''.join(rows)}</table></td></tr>
<tr><td style="padding:18px 24px 26px" align="center"><a href="{E(url)}" style="display:inline-block;background:{C['brick']};color:#ffffff;text-decoration:none;font-weight:bold;padding:12px 22px;border-radius:999px">Se det hele – også film og spisesteder</a></td></tr>
<tr><td style="padding:0 24px 24px;font-size:12px;line-height:1.5;color:{C['muted']}">Arrangementer fra KultuNaut. Tider kan ændre sig – tjek arrangørens side før du tager af sted.<br>
Du får denne mail, fordi du har tilmeldt dig på detskeri.dk. <a href="{{{{ unsubscribe }}}}" style="color:{C['muted']}">Afmeld</a></td></tr>
</table></td></tr></table></body></html>"""
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
    events = json.loads((ROOT / "data" / "events.json").read_text(encoding="utf-8"))["events"]
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
                                                   "htmlContent": b, "recipients": {"listIds": [lid]}, "inlineImageActivation": False})
        api("POST", f"/emailCampaigns/{c['id']}/sendNow", key)
        state[g["slug"]] = week
        STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
        print(g["slug"], "sendt til", subs, "–", s)

if __name__ == "__main__":
    main()
