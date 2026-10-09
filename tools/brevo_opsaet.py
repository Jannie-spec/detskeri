"""Opsætning i Brevo via API (køres af .github/workflows/brevo-opsaet.yml med BREVO_API_KEY).

1) Bekræftelsesmailen (dobbelt opt-in, skabelon 1): dansk tekst med kort engelsk/tysk/svensk linje, afsender nyhedsbrev@detskeri.dk.
2) Sender et prøve-nyhedsbrev (hele Bornholm) til PROEVE, så det kan ses i en rigtig indbakke."""
import os, sys, json, pathlib, datetime
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "tools"))
import build, nyhedsbrev

PROEVE = "jannie@hotelklippen.dk"
DOI_TEMPLATE = 1

DOI_HTML = """<!doctype html><html lang="da"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;background:#f3f5f0;font-family:Helvetica,Arial,sans-serif;color:#302f2f">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:24px 12px">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;background:#fff;border-radius:18px">
<tr><td style="background:#e5e9e1;border-radius:18px 18px 0 0;padding:24px">
<div style="font:400 15px Georgia,serif;color:#5f625e">detskeri.dk</div>
<div style="font:400 28px/1.1 Georgia,serif;margin-top:6px">Bekræft din tilmelding</div></td></tr>
<tr><td style="padding:22px 24px 8px;font-size:16px;line-height:1.5">
Tak fordi du vil have ugens program fra Bornholm. Tryk på knappen for at bekræfte – så får du nyhedsbrevet hver torsdag.</td></tr>
<tr><td style="padding:14px 24px 20px"><a href="{{ doubleoptin }}" style="display:inline-block;background:#b4533a;color:#fff;text-decoration:none;font-weight:bold;padding:12px 22px;border-radius:999px">Ja, tilmeld mig</a></td></tr>
<tr><td style="padding:0 24px 22px;font-size:13px;line-height:1.5;color:#5f625e">
Please confirm your subscription with the button above (the newsletter is in Danish).<br>
Bitte bestätigen Sie Ihre Anmeldung mit dem Knopf oben (der Newsletter ist auf Dänisch).<br>
Bekräfta din prenumeration med knappen ovan (nyhetsbrevet är på danska).<br><br>
Har du ikke bedt om det, kan du se bort fra mailen – så sker der ingenting.</td></tr>
</table></td></tr></table></body></html>"""

def main():
    key = os.environ.get("BREVO_API_KEY")
    if not key: print("BREVO_API_KEY mangler"); return
    api = lambda m, p, d=None: nyhedsbrev.api(m, p, key, d)
    api("PUT", f"/smtp/templates/{DOI_TEMPLATE}", {"sender": nyhedsbrev.SENDER, "subject": "Bekræft din tilmelding til Det sker på Bornholm",
                                                   "htmlContent": DOI_HTML, "isActive": True})
    print("Bekræftelsesmail opdateret")
    build.LANG = "da"
    events = build.all_events(json.loads((ROOT / "data" / "events.json").read_text(encoding="utf-8"))["events"])
    g = build.GUIDES[0]
    s, b, n = nyhedsbrev.render(g, events, datetime.datetime.now(build.TZ).date())
    b = b.replace("{{ unsubscribe }}", "https://detskeri.dk/")      # prøven sendes uden for en liste
    api("POST", "/smtp/email", {"sender": nyhedsbrev.SENDER, "to": [{"email": PROEVE}], "subject": "PRØVE: " + s, "htmlContent": b})
    print("Prøvebrev sendt:", s, n, "arrangementer")

if __name__ == "__main__":
    main()
