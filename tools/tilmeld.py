"""Tilmeldingsboks til det ugentlige nyhedsbrev (Brevo-formular "Det sker – tilmelding").

Formularen sender direkte til Brevo (sibforms). Listerne i Brevo:
  3 hele Bornholm · 4 Rønne · 5 Svaneke · 6 Allinge · 7 Nexø · 8 Hasle · 9 Gudhjem
LIVE styrer, om boksen vises på siden. DOI = Brevo sender en bekræftelsesmail (dobbelt opt-in)."""
import html

LIVE = True           # dobbelt opt-in slået til i Brevo 9/10
DOI = True            # teksten efter tilmelding: "tjek din mail" (True) eller "du er tilmeldt" (False)
ACTION = ("https://7dd9bd3f.sibforms.com/serve/MUIFAL1aatqD4WwYCobN5j4T_i8IGq2GKOvrQW93gEcBMHdCpYr23ZQAevsFQr7bIIzDzqHO8rMX9vzdLrrouAhSiqc1LmMy5yTcH5_"
          "ZqTKVCtOHqWYQhVc_RCBn2tDd-vHVTScPIS74sQbF_AyV29TenlHx6SwRUWE6qQYCc4RDNAy_5rXE9E4pyOrz8jZ78_Fn67AmcIBV9WLHfw==")
FIELD = "lists_28[]"
LISTS = [("bornholm", 3), ("roenne", 4), ("svaneke", 5), ("allinge", 6), ("nexoe", 7), ("hasle", 8), ("gudhjem", 9)]
NAMES = {"bornholm": {"da": "Hele Bornholm", "en": "All of Bornholm", "de": "Ganz Bornholm", "sv": "Hela Bornholm"},
         "roenne": "Rønne", "svaneke": "Svaneke", "allinge": "Allinge", "nexoe": "Nexø", "hasle": "Hasle", "gudhjem": "Gudhjem"}
T = {
    "da": ["Få ugens program på mail", "Hver torsdag: hvad der sker de næste syv dage. Vælg hele Bornholm eller de byer, du vil følge.",
           "Din e-mail", "Tilmeld", "Vælg mindst én.", "Skriv en gyldig e-mail.",
           "Tak! Tjek din mail og bekræft tilmeldingen.", "Tak! Du er tilmeldt.",
           "Gratis. Din e-mail bruges kun til nyhedsbrevet, som sendes via Brevo. Afmeld når som helst via linket i mailen.", "", "Hver torsdag · gratis · vælg selv byerne"],
    "en": ["Get the week's programme by email", "Every Thursday: what's on in the next seven days. Choose all of Bornholm or the towns you want to follow.",
           "Your email", "Subscribe", "Choose at least one.", "Enter a valid email.",
           "Thank you! Check your inbox and confirm.", "Thank you! You're subscribed.",
           "Free. Your email is only used for the newsletter, sent via Brevo. Unsubscribe any time from the link in the email.", "The newsletter is in Danish.", "Every Thursday · free · pick your towns"],
    "de": ["Das Wochenprogramm per E-Mail", "Jeden Donnerstag: was in den nächsten sieben Tagen los ist. Wählen Sie ganz Bornholm oder die Orte, die Sie interessieren.",
           "Ihre E-Mail", "Anmelden", "Bitte mindestens eins wählen.", "Bitte eine gültige E-Mail eingeben.",
           "Danke! Bitte prüfen Sie Ihr Postfach und bestätigen Sie.", "Danke! Sie sind angemeldet.",
           "Kostenlos. Ihre E-Mail wird nur für den Newsletter genutzt, der über Brevo verschickt wird. Abmelden jederzeit über den Link in der E-Mail.", "Der Newsletter ist auf Dänisch.", "Jeden Donnerstag · kostenlos · Orte selbst wählen"],
    "sv": ["Få veckans program på mejl", "Varje torsdag: vad som händer de kommande sju dagarna. Välj hela Bornholm eller de orter du vill följa.",
           "Din e-post", "Prenumerera", "Välj minst en.", "Skriv en giltig e-postadress.",
           "Tack! Kolla din mejl och bekräfta.", "Tack! Du prenumererar nu.",
           "Gratis. Din e-post används bara för nyhetsbrevet, som skickas via Brevo. Avsluta när som helst via länken i mejlet.", "Nyhetsbrevet är på danska.", "Varje torsdag · gratis · välj orterna själv"],
}
E = lambda s: html.escape(str(s or ""), quote=True)

CSS = """
/* smal stribe lige under toppen; byvalg og småt foldes ud, når man klikker i feltet */
.news{background:var(--deep);color:#fff;border-radius:18px;padding:14px 16px;margin:0 0 18px;display:grid;grid-template-columns:auto 1fr;gap:10px 16px;align-items:center}
.news .nic{width:40px;height:40px;border-radius:50%;background:var(--coral);display:grid;place-items:center}
.news .nic svg{width:22px;height:22px;fill:none;stroke:#fff;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.news .nt{display:flex;flex-wrap:wrap;align-items:center;gap:8px 16px}
.news h2{font:400 1.25rem/1.15 var(--serif);margin:0;color:#fff}
.news .nsub{margin:2px 0 0;font-size:.85rem;color:#cfe0e2}
.news .nrow{display:flex;gap:6px;flex:1 1 300px;max-width:440px;margin-left:auto}
.news input[type=email]{flex:1 1 auto;font:inherit;font-size:.95rem;border:0;border-radius:999px;padding:9px 15px;color:var(--ink);min-width:0}
.news button{font:inherit;font-size:.95rem;font-weight:700;border:0;border-radius:999px;padding:9px 18px;background:var(--coral);color:#fff;cursor:pointer;white-space:nowrap}
.news button:disabled{opacity:.6}
.news .more{grid-column:1/-1;display:none}
.news:focus-within .more,.news.open .more{display:block}
.news .nl{display:flex;flex-wrap:wrap;gap:6px;margin:2px 0 0;padding:0;border:0}
.news .nl label{display:inline-flex;align-items:center;gap:6px;background:rgba(255,255,255,.12);border-radius:999px;padding:4px 11px 4px 8px;font-size:.85rem;font-weight:600;cursor:pointer}
.news .nl input{accent-color:var(--coral);width:15px;height:15px;margin:0}
.news .nmsg{grid-column:1/-1;margin:0;font-weight:600}
.news .nmsg:empty{display:none}
.news .nfine{margin:8px 0 0;font-size:.76rem;color:#c0d5d8}
.news .hp{position:absolute;left:-9999px}
@media (max-width:620px){.news{grid-template-columns:minmax(0,1fr)}.news .nic{display:none}.news .nt{display:block}.news .nrow{max-width:none;margin:10px 0 0}}
.news .nt,.news .nrow{min-width:0}
"""

JS = """
<script>
document.querySelectorAll("form.news").forEach(f => f.addEventListener("submit", async e => {
  e.preventDefault();
  const m = f.querySelector(".nmsg"), em = f.querySelector("input[type=email]"), b = f.querySelector("button");
  f.classList.add("open");
  if (!f.querySelector(".nl input:checked")) { m.textContent = f.dataset.pick; return; }
  if (!em.checkValidity()) { m.textContent = f.dataset.bad; return; }
  f.classList.add("open"); b.disabled = true;
  try { localStorage.setItem("nlang", document.documentElement.lang || "da"); } catch (x) {}
  try { await fetch(f.action, { method: "POST", body: new FormData(f), mode: "no-cors" }); f.querySelector(".nrow").remove(); f.querySelector(".more").remove(); m.textContent = f.dataset.ok; }
  catch (x) { b.disabled = false; m.textContent = f.dataset.err; }
}));
</script>"""

ERR = {"da": "Noget gik galt – prøv igen.", "en": "Something went wrong – please try again.", "de": "Etwas ist schiefgelaufen – bitte erneut versuchen.", "sv": "Något gick fel – försök igen."}

def box(slug, lang):
    """HTML-boksen; slug = den side, man står på (den by er valgt på forhånd)."""
    if not LIVE: return ""
    t = T[lang]
    opts = []
    for s, lid in LISTS:
        n = NAMES[s][lang] if isinstance(NAMES[s], dict) else NAMES[s]
        opts.append(f'<label><input type="checkbox" name="{FIELD}" value="{lid}"{" checked" if s == slug else ""}> {E(n)}</label>')
    fine = t[8] + (" " + t[9] if t[9] else "")
    ic = '<span class="nic" aria-hidden="true"><svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg></span>'
    return (f'<form class="news" id="nyhedsbrev" action="{E(ACTION)}" method="post" data-pick="{E(t[4])}" data-bad="{E(t[5])}" data-ok="{E(t[6] if DOI else t[7])}" data-err="{E(ERR[lang])}">'
            f'{ic}<div class="nt"><div><h2>{E(t[0])}</h2><p class="nsub">{E(t[10])}</p></div>'
            f'<div class="nrow"><input type="email" name="EMAIL" required autocomplete="email" placeholder="{E(t[2])}" aria-label="{E(t[2])}">'
            f'<button type="submit">{E(t[3])}</button></div></div>'
            f'<div class="more"><fieldset class="nl">{"".join(opts)}</fieldset><p class="nfine">{E(fine)}</p></div>'
            f'<input class="hp" type="text" name="email_address_check" value="" tabindex="-1" autocomplete="off" aria-hidden="true">'
            f'<input type="hidden" name="locale" value="{lang}"><input type="hidden" name="html_type" value="simple">'
            f'<p class="nmsg" role="status"></p></form>')

def assets():
    """CSS + script, der kun skal med, når boksen vises."""
    return (f"<style>{CSS}</style>", JS) if LIVE else ("", "")

TAK = {"da": ("Tak – du er tilmeldt", "Du får ugens program hver torsdag. Du kan altid afmelde dig via linket nederst i mailen.", "Se hvad der sker i dag"),
       "en": ("Thank you – you're subscribed", "You'll get the week's programme every Thursday (in Danish). Unsubscribe any time from the link in the email.", "See what's on today"),
       "de": ("Danke – Sie sind angemeldet", "Sie bekommen das Wochenprogramm jeden Donnerstag (auf Dänisch). Abmelden jederzeit über den Link in der E-Mail.", "Was ist heute los"),
       "sv": ("Tack – du prenumererar nu", "Du får veckans program varje torsdag (på danska). Avsluta när som helst via länken i mejlet.", "Se vad som händer i dag")}

def tak_page(lang):
    """Takkesiden (/tak/, /en/tak/ …). Brevo sender altid til /tak/; den danske side skifter selv til det sprog,
    man tilmeldte sig på (husket i browseren ved tilmelding), ellers browserens sprog."""
    h, b, c = TAK[lang]
    home = "/" if lang == "da" else f"/{lang}/"
    redirect = ""
    if lang == "da":
        redirect = """<script>(function(){var l=null;try{l=localStorage.getItem("nlang")}catch(e){}
if(!l){l=(navigator.language||"da").slice(0,2)}
if(l==="en"||l==="de"||l==="sv")location.replace("/"+l+"/tak/");})();</script>"""
    return f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
{redirect}<title>{E(h)} – detskeri.dk</title><meta name="robots" content="noindex"><link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Young+Serif&family=Figtree:wght@400;600;700&display=swap">
<style>body{{margin:0;background:#e5e9e1;color:#302f2f;font:400 17px/1.5 Figtree,system-ui,sans-serif}}main{{max-width:640px;margin:0 auto;padding:40px 16px 60px}}
.brand{{font:400 1.05rem Georgia,serif;color:#302f2f;text-decoration:none}}section{{background:#fff;border-radius:22px;padding:26px 22px;margin:18px 0}}
h1{{font:400 clamp(1.9rem,6vw,2.6rem)/1.1 "Young Serif",Georgia,serif;margin:0 0 10px}}p{{margin:0 0 16px}}
.btn{{display:inline-block;background:#b4533a;color:#fff;text-decoration:none;font-weight:700;padding:10px 18px;border-radius:999px}}</style></head>
<body><main><a class="brand" href="{home}">detskeri.dk</a><section><h1>{E(h)}</h1><p>{E(b)}</p><a class="btn" href="{home}">{E(c)}</a></section></main></body></html>"""
