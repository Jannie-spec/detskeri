"""Tilmeldingsboks til det ugentlige nyhedsbrev (Brevo-formular "Det sker – tilmelding").

Formularen sender direkte til Brevo (sibforms). Listerne i Brevo:
  3 hele Bornholm · 4 Rønne · 5 Svaneke · 6 Allinge · 7 Nexø · 8 Hasle
LIVE styrer, om boksen vises på siden. DOI = Brevo sender en bekræftelsesmail (dobbelt opt-in)."""
import html

LIVE = False          # sæt True, når Brevo-kontoen er aktiveret og dobbelt opt-in er slået til
DOI = True            # teksten efter tilmelding: "tjek din mail" (True) eller "du er tilmeldt" (False)
ACTION = ("https://7dd9bd3f.sibforms.com/serve/MUIFAL1aatqD4WwYCobN5j4T_i8IGq2GKOvrQW93gEcBMHdCpYr23ZQAevsFQr7bIIzDzqHO8rMX9vzdLrrouAhSiqc1LmMy5yTcH5_"
          "ZqTKVCtOHqWYQhVc_RCBn2tDd-vHVTScPIS74sQbF_AyV29TenlHx6SwRUWE6qQYCc4RDNAy_5rXE9E4pyOrz8jZ78_Fn67AmcIBV9WLHfw==")
FIELD = "lists_28[]"
LISTS = [("bornholm", 3), ("roenne", 4), ("svaneke", 5), ("allinge", 6), ("nexoe", 7), ("hasle", 8)]
NAMES = {"bornholm": {"da": "Hele Bornholm", "en": "All of Bornholm", "de": "Ganz Bornholm", "sv": "Hela Bornholm"},
         "roenne": "Rønne", "svaneke": "Svaneke", "allinge": "Allinge", "nexoe": "Nexø", "hasle": "Hasle"}
T = {
    "da": ["Få ugens program på mail", "Hver torsdag: hvad der sker de næste syv dage. Vælg hele Bornholm eller de byer, du vil følge.",
           "Din e-mail", "Tilmeld", "Vælg mindst én.", "Skriv en gyldig e-mail.",
           "Tak! Tjek din mail og bekræft tilmeldingen.", "Tak! Du er tilmeldt.",
           "Gratis. Din e-mail bruges kun til nyhedsbrevet, som sendes via Brevo. Afmeld når som helst via linket i mailen.", ""],
    "en": ["Get the week's programme by email", "Every Thursday: what's on in the next seven days. Choose all of Bornholm or the towns you want to follow.",
           "Your email", "Subscribe", "Choose at least one.", "Enter a valid email.",
           "Thank you! Check your inbox and confirm.", "Thank you! You're subscribed.",
           "Free. Your email is only used for the newsletter, sent via Brevo. Unsubscribe any time from the link in the email.", "The newsletter is in Danish."],
    "de": ["Das Wochenprogramm per E-Mail", "Jeden Donnerstag: was in den nächsten sieben Tagen los ist. Wählen Sie ganz Bornholm oder die Orte, die Sie interessieren.",
           "Ihre E-Mail", "Anmelden", "Bitte mindestens eins wählen.", "Bitte eine gültige E-Mail eingeben.",
           "Danke! Bitte prüfen Sie Ihr Postfach und bestätigen Sie.", "Danke! Sie sind angemeldet.",
           "Kostenlos. Ihre E-Mail wird nur für den Newsletter genutzt, der über Brevo verschickt wird. Abmelden jederzeit über den Link in der E-Mail.", "Der Newsletter ist auf Dänisch."],
    "sv": ["Få veckans program på mejl", "Varje torsdag: vad som händer de kommande sju dagarna. Välj hela Bornholm eller de orter du vill följa.",
           "Din e-post", "Prenumerera", "Välj minst en.", "Skriv en giltig e-postadress.",
           "Tack! Kolla din mejl och bekräfta.", "Tack! Du prenumererar nu.",
           "Gratis. Din e-post används bara för nyhetsbrevet, som skickas via Brevo. Avsluta när som helst via länken i mejlet.", "Nyhetsbrevet är på danska."],
}
E = lambda s: html.escape(str(s or ""), quote=True)

CSS = """
.news{background:var(--deep);color:#fff;border-radius:22px;padding:22px 20px 18px;margin:0 0 4px}
.news h2{font:400 clamp(1.5rem,5vw,1.9rem)/1.1 var(--serif);margin:0 0 6px;color:#fff}
.news p{margin:0 0 12px;color:#e3eeef;max-width:34em}
.news .nl{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 12px;padding:0;border:0}
.news .nl label{display:inline-flex;align-items:center;gap:6px;background:rgba(255,255,255,.12);border-radius:999px;padding:5px 12px 5px 8px;font-size:.9rem;font-weight:600;cursor:pointer}
.news .nl input{accent-color:var(--coral);width:16px;height:16px;margin:0}
.news .nrow{display:flex;gap:8px;flex-wrap:wrap}
.news input[type=email]{flex:1 1 220px;font:inherit;border:0;border-radius:999px;padding:10px 16px;color:var(--ink);min-width:0}
.news button{font:inherit;font-weight:700;border:0;border-radius:999px;padding:10px 20px;background:var(--coral);color:#fff;cursor:pointer}
.news button:disabled{opacity:.6}
.news .nmsg{margin:10px 0 0;font-weight:600}
.news .nmsg:empty{display:none}
.news .nfine{margin:10px 0 0;font-size:.8rem;color:#c9dcde}
.news .hp{position:absolute;left:-9999px}
"""

JS = """
<script>
document.querySelectorAll("form.news").forEach(f => f.addEventListener("submit", async e => {
  e.preventDefault();
  const m = f.querySelector(".nmsg"), em = f.querySelector("input[type=email]"), b = f.querySelector("button");
  if (!f.querySelector(".nl input:checked")) { m.textContent = f.dataset.pick; return; }
  if (!em.checkValidity()) { m.textContent = f.dataset.bad; return; }
  b.disabled = true;
  try { await fetch(f.action, { method: "POST", body: new FormData(f), mode: "no-cors" }); f.querySelector(".nrow").remove(); f.querySelector(".nl").remove(); m.textContent = f.dataset.ok; }
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
    return (f'<form class="news" action="{E(ACTION)}" method="post" data-pick="{E(t[4])}" data-bad="{E(t[5])}" data-ok="{E(t[6] if DOI else t[7])}" data-err="{E(ERR[lang])}">'
            f'<h2>{E(t[0])}</h2><p>{E(t[1])}</p>'
            f'<fieldset class="nl">{"".join(opts)}</fieldset>'
            f'<div class="nrow"><input type="email" name="EMAIL" required autocomplete="email" placeholder="{E(t[2])}" aria-label="{E(t[2])}">'
            f'<button type="submit">{E(t[3])}</button></div>'
            f'<input class="hp" type="text" name="email_address_check" value="" tabindex="-1" autocomplete="off" aria-hidden="true">'
            f'<input type="hidden" name="locale" value="{lang}"><input type="hidden" name="html_type" value="simple">'
            f'<p class="nmsg" role="status"></p><p class="nfine">{E(fine)}</p></form>')

def assets():
    """CSS + script, der kun skal med, når boksen vises."""
    return (f"<style>{CSS}</style>", JS) if LIVE else ("", "")
