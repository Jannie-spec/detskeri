"""Siden "Tilføj dit arrangement" (/tilfoej/ på fire sprog).

Arrangører udfylder en formular; ved afsendelse åbnes deres eget mailprogram med en færdig mail til modtageren.
Ingen server og ingen tredjepart. Adressen samles først i browseren, så den ikke står ligefrem i HTML'en (mod spam-robotter)."""
import html

TO = ("jannie", "hotelklippen.dk")
E = lambda s: html.escape(str(s or ""), quote=True)
TOWNS = ["Rønne", "Svaneke", "Allinge-Sandvig", "Nexø", "Hasle", "Gudhjem", "Aakirkeby", "Østermarie", "Klemensker", "Andet sted på Bornholm"]

T = {
    "da": {"title": "Tilføj dit arrangement", "link": "Tilføj dit arrangement",
           "lead": "Holder du en koncert, et marked, en rundvisning eller noget helt fjerde på Bornholm? Fortæl os om det, så kommer det med i kalenderen og i ugens nyhedsbrev.",
           "f": ["Hvad hedder arrangementet?", "Dato", "Slutdato (hvis flere dage)", "Klokkeslæt", "Sted (navn og adresse)", "By", "Link til mere information eller billetter", "Kort beskrivelse", "Dit navn", "Din e-mail eller dit telefonnummer"],
           "send": "Send forslag", "note": "Når du trykker “Send forslag”, åbner dit mailprogram med en færdig mail til os. Du skal bare trykke send. Virker det ikke, så skriv direkte til",
           "req": "Udfyld navn, dato og sted.", "subject": "Nyt arrangement", "back": "Tilbage til kalenderen"},
    "en": {"title": "Add your event", "link": "Add your event",
           "lead": "Hosting a concert, a market, a guided tour or something else on Bornholm? Tell us about it and we'll add it to the calendar and the weekly newsletter.",
           "f": ["Name of the event", "Date", "End date (if several days)", "Time", "Venue (name and address)", "Town", "Link to more information or tickets", "Short description", "Your name", "Your email or phone number"],
           "send": "Send suggestion", "note": "When you press “Send suggestion”, your email program opens with a ready-made email to us. Just press send. If that doesn't work, write directly to",
           "req": "Please fill in name, date and venue.", "subject": "New event", "back": "Back to the calendar"},
    "de": {"title": "Veranstaltung eintragen", "link": "Veranstaltung eintragen",
           "lead": "Sie veranstalten ein Konzert, einen Markt, eine Führung oder etwas anderes auf Bornholm? Erzählen Sie uns davon, dann kommt es in den Kalender und in den wöchentlichen Newsletter.",
           "f": ["Name der Veranstaltung", "Datum", "Enddatum (bei mehreren Tagen)", "Uhrzeit", "Ort (Name und Adresse)", "Ort/Stadt", "Link zu weiteren Infos oder Tickets", "Kurze Beschreibung", "Ihr Name", "Ihre E-Mail oder Telefonnummer"],
           "send": "Vorschlag senden", "note": "Wenn Sie auf „Vorschlag senden“ drücken, öffnet sich Ihr E-Mail-Programm mit einer fertigen E-Mail an uns. Sie müssen nur noch senden. Falls das nicht klappt, schreiben Sie direkt an",
           "req": "Bitte Name, Datum und Ort ausfüllen.", "subject": "Neue Veranstaltung", "back": "Zurück zum Kalender"},
    "sv": {"title": "Lägg till ditt evenemang", "link": "Lägg till ditt evenemang",
           "lead": "Ordnar du en konsert, en marknad, en guidad tur eller något annat på Bornholm? Berätta för oss så kommer det med i kalendern och i veckans nyhetsbrev.",
           "f": ["Vad heter evenemanget?", "Datum", "Slutdatum (om flera dagar)", "Klockslag", "Plats (namn och adress)", "Ort", "Länk till mer information eller biljetter", "Kort beskrivning", "Ditt namn", "Din e-post eller ditt telefonnummer"],
           "send": "Skicka förslag", "note": "När du trycker på ”Skicka förslag” öppnas ditt e-postprogram med ett färdigt mejl till oss. Du behöver bara trycka skicka. Fungerar det inte, skriv direkt till",
           "req": "Fyll i namn, datum och plats.", "subject": "Nytt evenemang", "back": "Tillbaka till kalendern"},
}
KEYS = ["navn", "dato", "slut", "tid", "sted", "by", "link", "beskrivelse", "arrangoer", "kontakt"]
TYPES = ["text", "date", "date", "text", "text", "select", "url", "textarea", "text", "text"]

def link_text(lang): return T[lang]["link"]

def page(lang, up, home, langs_html, hreflang, canon):
    t = T[lang]
    fields = []
    for k, ty, lab in zip(KEYS, TYPES, t["f"]):
        req = " required" if k in ("navn", "dato", "sted") else ""
        if ty == "select":
            ctl = f'<select id="{k}" name="{k}"><option value=""></option>' + "".join(f"<option>{E(x)}</option>" for x in TOWNS) + "</select>"
        elif ty == "textarea":
            ctl = f'<textarea id="{k}" name="{k}" rows="5"></textarea>'
        else:
            ph = ' placeholder="19.30"' if k == "tid" else ""
            ctl = f'<input id="{k}" name="{k}" type="{ty}"{req}{ph}>'
        fields.append(f'<label for="{k}">{E(lab)}{" *" if req else ""}</label>{ctl}')
    labels = dict(zip(KEYS, ["Arrangement", "Dato", "Slutdato", "Tid", "Sted", "By", "Link", "Beskrivelse", "Arrangør", "Kontakt"]))   # mailen er til os: altid dansk
    import json
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(t["title"])} – detskeri.dk</title>
<meta name="description" content="{E(t["lead"])}">
<link rel="canonical" href="{canon}">
{hreflang}
<meta name="theme-color" content="#e5e9e1">
<link rel="icon" href="{up}favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Young+Serif&family=Figtree:wght@400;500;600;700&display=swap">
<style>
:root{{--bg:#f3f5f0;--surface:#fff;--sage:#e5e9e1;--coral:#e37b5b;--brick:#b4533a;--ink:#302f2f;--muted:#5f625e;--line:#dde3d9;
  --serif:"Young Serif",Georgia,serif;--sans:"Figtree",system-ui,-apple-system,"Segoe UI",sans-serif}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:400 17px/1.5 var(--sans)}}
a{{color:var(--brick);text-underline-offset:3px}}
.wrap{{max-width:680px;margin:0 auto;padding:0 16px}}
header{{background:var(--sage);padding:30px 0 26px}}
.toprow{{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;margin:0 0 16px}}
.brand{{font:400 1.05rem/1 var(--serif);color:var(--ink);text-decoration:none}}
.langs{{display:flex;gap:4px}}
.langs a{{font-size:.82rem;font-weight:700;text-decoration:none;color:var(--muted);padding:5px 8px;border-radius:999px}}
.langs a[aria-current="true"]{{background:#fff;color:var(--brick)}}
h1{{font:400 clamp(2.2rem,8vw,3.4rem)/1 var(--serif);margin:0}}
header p{{margin:12px 0 0;max-width:34em;color:#4a4d49}}
form{{background:var(--surface);border-radius:22px;padding:22px 20px;margin:22px 0;box-shadow:0 1px 0 var(--line);display:grid;gap:6px}}
label{{font-weight:600;font-size:.95rem;margin-top:10px}}
input,select,textarea{{font:inherit;width:100%;border:1px solid var(--line);border-radius:12px;padding:10px 12px;background:var(--bg);color:var(--ink)}}
input:focus,select:focus,textarea:focus{{outline:2px solid var(--coral);outline-offset:1px}}
button{{justify-self:start;margin-top:16px;font:inherit;font-weight:700;border:0;border-radius:999px;padding:11px 22px;background:var(--brick);color:#fff;cursor:pointer}}
.msg{{margin:8px 0 0;font-weight:600;color:var(--brick)}}
.msg:empty{{display:none}}
.note{{font-size:.88rem;color:var(--muted);margin:10px 0 0}}
footer{{padding:6px 0 50px;font-size:.9rem}}
</style>
<script src="{up}samtykke.js" data-ga="G-WW4MDXMEJS" defer></script>
</head>
<body>
<header><div class="wrap">
<div class="toprow"><a class="brand" href="{home}">detskeri.dk</a><nav class="langs" aria-label="Sprog / Language">{langs_html}</nav></div>
<h1>{E(t["title"])}</h1>
<p>{E(t["lead"])}</p>
</div></header>
<main class="wrap">
<form id="tilfoej" novalidate>
{"".join(fields)}
<button type="submit">{E(t["send"])}</button>
<p class="msg" role="status"></p>
<p class="note">{E(t["note"])} <a class="to" href="#"></a>.</p>
</form>
</main>
<footer class="wrap"><a href="{home}">{E(t["back"])}</a> · <a href="#" class="cookie-valg">Cookie</a></footer>
<script>
(function(){{
  const to = {json.dumps(TO[0])} + "@" + {json.dumps(TO[1])};
  const a = document.querySelector("a.to"); a.textContent = to; a.href = "mailto:" + to;
  const L = {json.dumps(labels, ensure_ascii=False)}, f = document.getElementById("tilfoej"), m = f.querySelector(".msg");
  f.addEventListener("submit", e => {{
    e.preventDefault();
    if (!f.navn.value.trim() || !f.dato.value || !f.sted.value.trim()) {{ m.textContent = {json.dumps(t["req"], ensure_ascii=False)}; return; }}
    m.textContent = "";
    const body = Object.keys(L).map(k => f[k].value.trim() ? L[k] + ": " + f[k].value.trim() : "").filter(Boolean).join("\\n\\n");
    location.href = "mailto:" + to + "?subject=" + encodeURIComponent({json.dumps(t["subject"], ensure_ascii=False)} + ": " + f.navn.value.trim()) + "&body=" + encodeURIComponent(body + "\\n\\n– sendt fra detskeri.dk");
  }});
}})();
</script>
</body>
</html>
"""
