"""Bygger detskeri.dk: daglige byguider for Bornholm (hele øen + Rønne, Svaneke, Allinge, Nexø, Hasle) på fire sprog.

Data:  data/events.json   arrangementer fra KultuNaut (tools/kultunaut.py, hver morgen)
       data/places/*.json  spisesteder, caféer, barer og is med åbningstider (håndholdt, med kilder)
       data/tr.json        oversættelser af faste tekster (fra Klippens gæsteapp)
Ud:    site/  (GitHub Pages)
"""
import json, html, datetime, pathlib, re, shutil, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "tools"))
import tegning, tilmeld, tilfoej
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parent
TZ = ZoneInfo("Europe/Copenhagen")
BASE = "https://detskeri.dk/"
DAYS = 7
LATER_DAYS = 366
E = lambda s: html.escape(str(s or ""), quote=True)
LANGS = ["da", "en", "de", "sv"]
LANG = "da"
DTR = {}

DAYNAMES = {
    "da": (["mandag","tirsdag","onsdag","torsdag","fredag","lørdag","søndag"], ["man","tir","ons","tor","fre","lør","søn"], ["januar","februar","marts","april","maj","juni","juli","august","september","oktober","november","december"]),
    "en": (["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"], ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"], ["January","February","March","April","May","June","July","August","September","October","November","December"]),
    "de": (["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"], ["Mo","Di","Mi","Do","Fr","Sa","So"], ["Januar","Februar","März","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember"]),
    "sv": (["måndag","tisdag","onsdag","torsdag","fredag","lördag","söndag"], ["mån","tis","ons","tor","fre","lör","sön"], ["januari","februari","mars","april","maj","juni","juli","augusti","september","oktober","november","december"]),
}

# ---------- guiderne ----------
# "in": stednavnet med forholdsord på hvert sprog; "towns": KultuNaut-byer der hører med; "places": spisestedsfiler
GUIDES = [
    {"slug": "bornholm", "path": "bornholm/", "name": "Bornholm", "in": {"da": "på Bornholm", "en": "on Bornholm", "de": "auf Bornholm", "sv": "på Bornholm"},
     "towns": None, "places": ["roenne", "svaneke", "allinge", "nexoe", "hasle"]},
    {"slug": "roenne", "path": "bornholm/roenne/", "name": "Rønne", "towns": ["Rønne"], "places": ["roenne"]},
    {"slug": "svaneke", "path": "bornholm/svaneke/", "name": "Svaneke", "towns": ["Svaneke"], "places": ["svaneke"]},
    {"slug": "allinge", "path": "bornholm/allinge/", "name": "Allinge", "towns": ["Allinge"], "places": ["allinge"], "alt": "Allinge-Sandvig"},
    {"slug": "nexoe", "path": "bornholm/nexoe/", "name": "Nexø", "towns": ["Nexø"], "places": ["nexoe"]},
    {"slug": "hasle", "path": "bornholm/hasle/", "name": "Hasle", "towns": ["Hasle"], "places": ["hasle"]},
]
PLACE_TOWN = {"roenne": "Rønne", "svaneke": "Svaneke", "allinge": "Allinge", "nexoe": "Nexø", "hasle": "Hasle"}
GUDHJEM = "https://detskerigudhjem.dk/"
LANG_PRE = {"da": "", "en": "en/", "de": "de/", "sv": "sv/"}

def g_in(g):
    if "in" in g: return g["in"][LANG]
    return {"da": "i ", "en": "in ", "de": "in ", "sv": "i "}[LANG] + g["name"]

def title_of(g):
    return {"da": "Det sker ", "en": "What's on ", "de": "Was ist los ", "sv": "Det händer "}[LANG] + g_in(g)


# ---------- SEO: kort, unik tekst om hver by (da, en, de, sv) ----------
ABOUT = {
    "bornholm": ["Bornholm er Danmarks solskinsø i Østersøen med klipper, sandstrande, rundkirker og hyggelige havnebyer. Her samler vi, hvad der sker over hele øen – koncerter, teater, film, kirke, markeder og børneaktiviteter – og hvilke spisesteder der har åbent.",
                 "Bornholm is Denmark's sunshine island in the Baltic Sea, with cliffs, sandy beaches, round churches and charming harbour towns. Here we gather what's on across the island – concerts, theatre, films, church, markets and things for children – and which restaurants are open.",
                 "Bornholm ist Dänemarks Sonneninsel in der Ostsee mit Felsen, Sandstränden, Rundkirchen und gemütlichen Hafenstädten. Hier findest du, was auf der ganzen Insel los ist – Konzerte, Theater, Filme, Kirche, Märkte und Kinderaktivitäten – und welche Restaurants geöffnet haben.",
                 "Bornholm är Danmarks solskensö i Östersjön med klippor, sandstränder, rundkyrkor och mysiga hamnstäder. Här samlar vi vad som händer på hela ön – konserter, teater, film, kyrka, marknader och barnaktiviteter – och vilka matställen som har öppet."],
    "roenne": ["Rønne er Bornholms største by og øens port med færgehavnen. Byen har teater, musikhus, biograf og museer og et gammelt centrum med brostensgader og bindingsværkshuse. Her kan du se, hvad der sker i Rønne i dag og de næste dage.",
               "Rønne is Bornholm's largest town and the island's gateway with the ferry harbour. The town has a theatre, a concert venue, a cinema and museums, and an old centre with cobbled streets and half-timbered houses. See what's on in Rønne today and the next few days.",
               "Rønne ist die größte Stadt Bornholms und mit dem Fährhafen das Tor zur Insel. Es gibt Theater, Musikhaus, Kino und Museen und eine Altstadt mit Kopfsteinpflaster und Fachwerkhäusern. Hier siehst du, was heute und in den nächsten Tagen in Rønne los ist.",
               "Rønne är Bornholms största stad och öns port med färjehamnen. Staden har teater, musikhus, bio och museer och en gammal stadskärna med kullerstensgator och korsvirkeshus. Här ser du vad som händer i Rønne i dag och de närmaste dagarna."],
    "svaneke": ["Svaneke på Bornholms østkyst er kendt for de okkergule huse, røgeriet, bryghuset og byens mange kunsthåndværkere. Om sommeren er der marked på torvet og liv ved den lille havn. Her kan du se, hvad der sker i Svaneke i dag og de næste dage.",
                "Svaneke on Bornholm's east coast is known for its ochre houses, the smokehouse, the brewery and the town's many craftspeople. In summer there is a market on the square and life by the little harbour. See what's on in Svaneke today and the next few days.",
                "Svaneke an der Ostküste Bornholms ist bekannt für seine ockergelben Häuser, die Räucherei, die Brauerei und viele Kunsthandwerker. Im Sommer gibt es Markt auf dem Platz und Leben am kleinen Hafen. Hier siehst du, was heute und in den nächsten Tagen in Svaneke los ist.",
                "Svaneke på Bornholms östkust är känt för de ockragula husen, röken, bryggeriet och stadens många konsthantverkare. På sommaren är det marknad på torget och liv vid den lilla hamnen. Här ser du vad som händer i Svaneke i dag och de närmaste dagarna."],
    "allinge": ["Allinge og Sandvig ligger på Bornholms nordkyst tæt på Hammeren og Hammershus, Nordeuropas største borgruin. Byen er kendt for røgerierne, klipperne ved havnen og Folkemødet hver sommer. Her kan du se, hvad der sker i Allinge i dag og de næste dage.",
                "Allinge and Sandvig lie on Bornholm's north coast close to Hammeren and Hammershus, the largest castle ruin in Northern Europe. The town is known for its smokehouses, the rocks by the harbour and the Folkemødet festival every summer. See what's on in Allinge today and the next few days.",
                "Allinge und Sandvig liegen an der Nordküste Bornholms nahe Hammeren und Hammershus, der größten Burgruine Nordeuropas. Bekannt sind die Räuchereien, die Felsen am Hafen und das Folkemødet jeden Sommer. Hier siehst du, was heute und in den nächsten Tagen in Allinge los ist.",
                "Allinge och Sandvig ligger på Bornholms nordkust nära Hammeren och Hammershus, Nordeuropas största borgruin. Staden är känd för rökerierna, klipporna vid hamnen och Folkemødet varje sommar. Här ser du vad som händer i Allinge i dag och de närmaste dagarna."],
    "nexoe": ["Nexø er Bornholms næststørste by og har øens største fiskerihavn. Herfra er der kort til Paradisbakkerne, Balka Strand og Snogebæk. Her kan du se, hvad der sker i Nexø i dag og de næste dage.",
              "Nexø is Bornholm's second largest town and has the island's biggest fishing harbour. It is a short trip to Paradisbakkerne, Balka beach and Snogebæk. See what's on in Nexø today and the next few days.",
              "Nexø ist die zweitgrößte Stadt Bornholms und hat den größten Fischereihafen der Insel. Paradisbakkerne, der Strand von Balka und Snogebæk sind ganz in der Nähe. Hier siehst du, was heute und in den nächsten Tagen in Nexø los ist.",
              "Nexø är Bornholms näst största stad och har öns största fiskehamn. Härifrån är det nära till Paradisbakkerne, Balka strand och Snogebæk. Här ser du vad som händer i Nexø i dag och de närmaste dagarna."],
    "hasle": ["Hasle på Bornholms vestkyst er kendt for røgeriet, havnen og solnedgangene over havet, og der er kort til Rubinsøen og Jons Kapel. Her kan du se, hvad der sker i Hasle i dag og de næste dage.",
              "Hasle on Bornholm's west coast is known for its smokehouse, the harbour and the sunsets over the sea, and Rubinsøen and Jons Kapel are close by. See what's on in Hasle today and the next few days.",
              "Hasle an der Westküste Bornholms ist bekannt für die Räucherei, den Hafen und die Sonnenuntergänge über dem Meer; Rubinsøen und Jons Kapel liegen ganz in der Nähe. Hier siehst du, was heute und in den nächsten Tagen in Hasle los ist.",
              "Hasle på Bornholms västkust är känt för röken, hamnen och solnedgångarna över havet, och det är nära till Rubinsøen och Jons Kapel. Här ser du vad som händer i Hasle i dag och de närmaste dagarna."],
}

def seo_title(g):
    if LANG == "da": return f"Det sker {g_in(g)} i dag – arrangementer, film og spisesteder"
    if LANG == "en": return f"What's on {g_in(g)} today – events, films and restaurants"
    if LANG == "de": return f"Was ist los {g_in(g)} heute – Veranstaltungen, Filme und Restaurants"
    return f"Det händer {g_in(g)} i dag – evenemang, film och matställen"

def seo_desc(g, n_today, n_week):
    place = g["name"]
    if LANG == "da": return f"Se hvad der sker {g_in(g)} i dag og de næste dage: {n_week} arrangementer – koncerter, film, teater, kirke og børneaktiviteter – og spisesteder med åbent. Opdateres hver morgen."
    if LANG == "en": return f"See what's on {g_in(g)} today and the next few days: {n_week} events – concerts, films, theatre, church and things for children – and restaurants that are open. Updated every morning."
    if LANG == "de": return f"Was ist heute und in den nächsten Tagen {g_in(g)} los: {n_week} Veranstaltungen – Konzerte, Filme, Theater, Kirche und Kinderaktivitäten – und geöffnete Restaurants. Jeden Morgen aktualisiert."
    return f"Se vad som händer {g_in(g)} i dag och de närmaste dagarna: {n_week} evenemang – konserter, film, teater, kyrka och barnaktiviteter – och matställen som har öppet. Uppdateras varje morgon."

def render_about(g, depth):
    i = LANGS.index(LANG)
    head = {"da": "Om ", "en": "About ", "de": "Über ", "sv": "Om "}[LANG] + g["name"]
    also = {"da": "Se også", "en": "See also", "de": "Siehe auch", "sv": "Se även"}[LANG]
    links = [f'<a href="{"../" * depth}{LANG_PRE[LANG]}{o["path"]}">{E(title_of(o))}</a>' for o in GUIDES if o is not g]
    links.append(f'<a href="{GUDHJEM}{LANG_PRE[LANG]}" rel="noopener">{E(title_of({"name": "Gudhjem"}))}</a>')
    return f'<section class="about"><h2>{E(head)}</h2><p>{E(ABOUT[g["slug"]][i])}</p><p class="also"><b>{also}:</b> ' + " · ".join(links) + '</p></section>'

def breadcrumbs(g):
    items = [{"@type": "ListItem", "position": 1, "name": "detskeri.dk", "item": BASE + LANG_PRE[LANG]}]
    if g["slug"] != "bornholm":
        items.append({"@type": "ListItem", "position": 2, "name": "Bornholm", "item": BASE + LANG_PRE[LANG] + "bornholm/"})
    items.append({"@type": "ListItem", "position": len(items) + 1, "name": g["name"], "item": BASE + LANG_PRE[LANG] + g["path"]})
    return {"@type": "BreadcrumbList", "itemListElement": items}

# ---------- sidens egne tekster: dansk → [en, de, sv] ----------
U = {
    "Hele dagen": ["All day", "Ganztägig", "Hela dagen"],
    "I dag": ["Today", "Heute", "I dag"], "I morgen": ["Tomorrow", "Morgen", "I morgon"],
    "Ingen arrangementer i kalenderen endnu.": ["Nothing in the calendar yet.", "Noch nichts im Kalender.", "Inget i kalendern ännu."],
    "Spisesteder, barer og is, der har åbent": ["Restaurants, bars and ice cream – open", "Geöffnete Restaurants, Bars und Eisdielen", "Matställen, barer och glass som har öppet"],
    "Tjek selv åbningstiden": ["Check opening hours yourself", "Öffnungszeiten bitte selbst prüfen", "Kolla öppettiderna själv"],
    "Se stedets side": ["See the venue's website", "Siehe Website des Lokals", "Se ställets webbplats"],
    "Længere frem": ["Coming up", "Demnächst", "Längre fram"],
    "Det, der allerede står i kalenderen det næste år. Der kommer flere arrangementer til løbende.": [
        "What is already in the calendar for the coming year. More events are added all the time.",
        "Was für das kommende Jahr schon im Kalender steht. Laufend kommen weitere Veranstaltungen dazu.",
        "Det som redan står i kalendern det kommande året. Fler evenemang tillkommer löpande."],
    "Intet i kalenderen længere frem endnu.": ["Nothing further ahead in the calendar yet.", "Noch nichts Weiteres im Kalender.", "Inget längre fram i kalendern ännu."],
    "til": ["until", "bis", "till"],
    "Kræver tilmelding": ["Booking required", "Anmeldung erforderlich", "Kräver anmälan"],
    "Tilmelding til nogle aktiviteter": ["Booking for some activities", "Anmeldung für einige Aktivitäten", "Anmälan till vissa aktiviteter"],
    "Billet på forhånd": ["Tickets in advance", "Tickets im Voraus", "Biljett i förväg"],
    "Film": ["Film", "Film", "Film"], "Kirke": ["Church", "Kirche", "Kyrka"], "Musik": ["Music", "Musik", "Musik"],
    "Børn og familie": ["Children and family", "Kinder und Familie", "Barn och familj"], "Foredrag": ["Talk", "Vortrag", "Föredrag"],
    "Kunst og kultur": ["Art and culture", "Kunst und Kultur", "Konst och kultur"], "Mad og drikke": ["Food and drink", "Essen und Trinken", "Mat och dryck"],
    "Arrangement": ["Event", "Veranstaltung", "Evenemang"], "Teater": ["Theatre", "Theater", "Teater"], "Sport": ["Sport", "Sport", "Sport"],
    "Byer": ["Towns", "Orte", "Orter"], "Hele øen": ["Whole island", "Ganze Insel", "Hela ön"],
    "Byens kalender: koncerter, film, teater, kirke, børneaktiviteter og spisesteder med åbent – samlet ét sted og opdateret hver morgen.": [
        "The town calendar: concerts, films, theatre, church, things for children and restaurants that are open – in one place, updated every morning.",
        "Der Kalender der Stadt: Konzerte, Filme, Theater, Kirche, Kinderaktivitäten und geöffnete Restaurants – an einem Ort, jeden Morgen aktualisiert.",
        "Stadens kalender: konserter, film, teater, kyrka, barnaktiviteter och matställen som har öppet – samlat på ett ställe och uppdaterat varje morgon."],
    "Øens kalender: koncerter, film, teater, kirke, børneaktiviteter og spisesteder med åbent i alle byerne – samlet ét sted og opdateret hver morgen.": [
        "The island calendar: concerts, films, theatre, church, things for children and restaurants that are open in every town – in one place, updated every morning.",
        "Der Kalender der Insel: Konzerte, Filme, Theater, Kirche, Kinderaktivitäten und geöffnete Restaurants in allen Orten – an einem Ort, jeden Morgen aktualisiert.",
        "Öns kalender: konserter, film, teater, kyrka, barnaktiviteter och matställen som har öppet i alla orter – samlat på ett ställe och uppdaterat varje morgon."],
    "Åbningstiderne er vores bedste bud ud fra stedernes egne sider, men de kan ændre sig – især uden for sæsonen. Tjek altid stedet, før du går.": [
        "Opening hours are our best guess based on the venues' own websites, but they can change – especially outside the season. Always check before you go.",
        "Die Öffnungszeiten sind unsere beste Einschätzung nach den Websites der Lokale, können sich aber ändern – besonders außerhalb der Saison. Bitte vorher prüfen.",
        "Öppettiderna är vår bästa bedömning utifrån ställenas egna webbplatser, men de kan ändras – särskilt utanför säsongen. Kolla alltid innan du går."],
    "tid usikker": ["time uncertain", "Zeit unsicher", "osäker tid"],
    "Opdateret": ["Updated", "Aktualisiert", "Uppdaterad"],
    "Arrangementer fra": ["Events from", "Veranstaltungen von", "Evenemang från"],
    "Åbningstider er hentet fra stedernes egne sider og kan ændre sig – tjek altid stedet, før du går.": [
        "Opening hours are taken from the venues' own websites and may change – always check before you go.",
        "Die Öffnungszeiten stammen von den Websites der Lokale und können sich ändern – bitte vorher prüfen.",
        "Öppettiderna kommer från ställenas egna webbplatser och kan ändras – kolla alltid innan du går."],
    "Mangler der noget, eller er en tid forkert? Skriv til": ["Something missing or a time wrong? Write to", "Fehlt etwas oder stimmt eine Zeit nicht? Schreib an", "Saknas något eller är en tid fel? Skriv till"],
    "Vælg dag": ["Choose day", "Tag wählen", "Välj dag"],
    "Hvad sker der i dag?": ["What's on today?", "Was ist heute los?", "Vad händer i dag?"],
    "Se dagens arrangementer, film og spisesteder med åbent i hver by.": ["See today's events, films and open restaurants in each town.", "Veranstaltungen, Filme und geöffnete Restaurants von heute in jedem Ort.", "Se dagens evenemang, film och öppna matställen i varje ort."],
    "Cookie-valg": ["Cookie settings", "Cookie-Einstellungen", "Cookieval"],
    "i dag og de næste dage": ["today and the next few days", "heute und in den nächsten Tagen", "i dag och de närmaste dagarna"],
    "arrangementer i dag": ["events today", "Veranstaltungen heute", "evenemang i dag"],
}

def L(s):
    if LANG == "da" or not s: return s
    i = LANGS.index(LANG) - 1
    if s in U: return U[s][i]
    if s in DTR: return DTR[s][i]
    return s

def hm(s):
    h, m = s.split(":")[:2]
    return f"{int(h)}" + (f".{m}" if m != "00" else "") if LANG != "en" else (f"{int(h)}:{m}")

def tmin(s):
    h, m = s.split(":")[:2]
    return int(h) * 60 + int(m)

def span(sl):
    return ", ".join(f"{hm(a)}–{hm(b)}" for a, b in sl)

def slots_on(p, d):
    if not p: return []
    if p.get("closedMonths") and d.month in p["closedMonths"]: return []
    sched = p.get("hours")
    if p.get("seasons"):
        md = f"{d.month:02d}-{d.day:02d}"
        se = next((s for s in p["seasons"] if s["from"] <= md <= s["to"]), None)
        if not se: return []
        sched = se["hours"]
    if not sched: return []
    wd = (d.weekday() + 1) % 7
    return sched.get("all") or sched.get(str(wd)) or []

# ---------- arrangementernes art ----------
def kind_of(e):
    t = " ".join([e.get("g", ""), e.get("title", ""), e.get("where", "")]).lower()
    if " bio" in " " + e.get("where", "").lower() or "film" in e.get("g", "").lower() or "biograf" in t: return "film"
    for k, words in (("kirke", ("gudstjeneste", "kirke", "messe", "højmesse", "andagt")), ("musik", ("musik", "koncert", "jazz", "sang", "kor")),
                     ("teater", ("teater", "revy", "forestilling", "stand-up", "standup")),
                     ("born", ("børn", "famili", "halloween", "karamel", "disco")), ("foredrag", ("foredrag", "rundvisning", "salon", "fortælling", "guidet")),
                     ("kunst", ("kunst", "museum", "udstilling", "historisk", "galleri")), ("mad", ("gastronomi", "smagning", "middag", "marked", "street food")),
                     ("sport", ("sport", "løb", "fodbold", "håndbold", "cykel", "vandring", "yoga"))):
        if any(w in t for w in words): return k
    return "andet"

ICON = {
    "film": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M7 5v14M17 5v14M3 9h4M3 15h4M17 9h4M17 15h4"/>',
    "kirke": '<path d="M12 2v5M10 4h4"/><path d="M6 21V11l6-4 6 4v10"/><path d="M10 21v-4a2 2 0 0 1 4 0v4"/>',
    "musik": '<path d="M9 18V5l11-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="17" cy="16" r="3"/>',
    "teater": '<path d="M4 4h16v6a8 8 0 0 1-16 0z"/><path d="M8 9h.01M16 9h.01M9 13c1.5 1.3 4.5 1.3 6 0"/>',
    "born": '<circle cx="12" cy="8" r="5"/><path d="M12 13l-1 3h2l-1-3M12 16c0 2-2 3-2 5"/>',
    "foredrag": '<path d="M4 5h16v10H9l-5 4z"/><path d="M8 9h8M8 12h5"/>',
    "kunst": '<path d="M12 3a9 9 0 1 0 0 18c1.5 0 2-1 2-2s-1-1.5-1-2.5 1-1.5 2-1.5h2a4 4 0 0 0 4-4c0-4.4-4-8-9-8z"/><circle cx="7.5" cy="11" r="1"/><circle cx="10" cy="7" r="1"/><circle cx="15" cy="7" r="1"/>',
    "mad": '<path d="M7 3v8a2 2 0 0 0 4 0V3M9 11v10"/><path d="M17 3c-2 2-2 6 0 8v10"/>',
    "sport": '<circle cx="12" cy="12" r="9"/><path d="M12 3v18M3 12h18"/>',
    "andet": '<path d="M12 3l2.6 5.6 6.1.7-4.5 4.2 1.2 6L12 16.6 6.6 19.5l1.2-6L3.3 9.3l6.1-.7z"/>',
}
KIND_LABEL = {"film": "Film", "kirke": "Kirke", "musik": "Musik", "teater": "Teater", "born": "Børn og familie", "foredrag": "Foredrag",
              "kunst": "Kunst og kultur", "mad": "Mad og drikke", "sport": "Sport", "andet": "Arrangement"}
REGTXT = {1: "Kræver tilmelding", 2: "Tilmelding til nogle aktiviteter", 3: "Billet på forhånd"}

def icon(kind):
    return f'<span class="ic ic-{kind}" title="{E(L(KIND_LABEL.get(kind, "")))}"><svg viewBox="0 0 24 24" aria-hidden="true">{ICON.get(kind, ICON["andet"])}</svg></span>'

def link(text, url):
    return f'<a href="{E(url)}" rel="noopener">{E(text)}</a>' if url else E(text)

# ---------- data ----------
def load():
    ev = json.loads((ROOT / "data" / "events.json").read_text(encoding="utf-8"))
    places = {}
    for f in sorted((ROOT / "data" / "places").glob("*.json")):
        for p in json.loads(f.read_text(encoding="utf-8")):
            p.setdefault("town", PLACE_TOWN.get(f.stem, ""))
            p["file"] = f.stem
            places[f.stem + ":" + p["id"]] = p
    tr = json.loads((ROOT / "data" / "tr.json").read_text(encoding="utf-8"))
    tf = ROOT / "data" / "tider.json"
    tider = json.loads(tf.read_text(encoding="utf-8")) if tf.exists() else {}
    for k, p in places.items():
        if tider.get(k, {}).get("changed"):
            p["sure"] = False          # stedets side er ændret siden sidste gennemgang
    return ev, places, tr

def in_guide(e, g):
    return g["towns"] is None or e["town"] in g["towns"]

def on_day(e, d):
    iso = d.isoformat()
    if not (e["d"] <= iso <= (e.get("to") or e["d"])): return False
    return not e.get("wd") or ((d.weekday() + 1) % 7) in e["wd"]

def pdesc(p):
    return p.get("desc_" + LANG) or p.get("desc", "") if LANG != "da" else p.get("desc", "")

def build_day(g, events, places, d):
    many = g["towns"] is None
    items = []
    for e in events:
        if e.get("long") or not in_guide(e, g) or not on_day(e, d): continue
        k = kind_of(e)
        if e.get("t"):
            tt = hm(e["t"]) + (("–" + hm(e["t2"])) if e.get("t2") else "")
            s, end = tmin(e["t"]), tmin(e.get("t2") or e["t"]) + (0 if e.get("t2") else 90)
        else:
            tt, s, end = L("Hele dagen"), -1, None
        where = e.get("where", "") + ((", " + e["town"]) if many and e["town"].lower() not in e.get("where", "").lower() else "")
        items.append({"s": s, "time": tt, "title": L(e["title"]), "where": where, "url": e.get("rurl") or e.get("url"), "end": end,
                      "kind": k, "reg": L(REGTXT.get(e.get("reg"), "")), "town": e["town"]})
    items.sort(key=lambda x: (x["s"], x["title"]))
    food, unknown = [], []
    for p in places.values():
        if p["file"] not in g["places"] or p.get("cat") not in ("mad", "is"): continue
        sl = slots_on(p, d)
        if sl:
            food.append({"name": p["name"], "hours": span(sl), "cat": p["cat"], "desc": pdesc(p), "url": p.get("url"), "town": p.get("town", ""), "sure": p.get("sure", True)})
        elif not p.get("hours") and not p.get("seasons") and not (p.get("closedMonths") and d.month in p["closedMonths"]):
            unknown.append({"name": p["name"], "url": p.get("url"), "town": p.get("town", ""), "desc": pdesc(p)})
    food.sort(key=lambda f: (f["town"] if many else "", f["cat"] != "mad", f["name"]))
    unknown.sort(key=lambda f: (f["town"] if many else "", f["name"]))
    return {"iso": d.isoformat(), "d": d, "items": items, "food": food, "unknown": unknown}

def render_day(g, x, i):
    d = x["d"]; many = g["towns"] is None
    wd_, wds_, mon_ = DAYNAMES[LANG]
    rel = L("I dag") if i == 0 else L("I morgen") if i == 1 else wd_[d.weekday()].capitalize()
    datetxt = f"{wd_[d.weekday()]}, {mon_[d.month - 1]} {d.day}" if LANG == "en" else f"{wd_[d.weekday()]}, {d.day}. {mon_[d.month - 1]}" if LANG == "de" else f"{wd_[d.weekday()]} {d.day}" + (". " if LANG == "da" else " ") + mon_[d.month - 1]
    h = [f'<section class="day" id="d-{x["iso"]}" data-date="{x["iso"]}">',
         f'<header class="dayhead"><div class="leaf" aria-hidden="true"><span class="lw">{wds_[d.weekday()]}</span><span class="ln">{d.day}</span><span class="lm">{mon_[d.month - 1][:3]}</span></div>'
         f'<h2><span class="big" data-rel="{i}">{E(rel)}</span><span class="date">{E(datetxt)}</span></h2></header>']
    if x["items"]:
        if many:
            towns = sorted({it["town"] for it in x["items"]})
            h.append('<div class="tfilter" role="group" aria-label="' + E(L("Byer")) + '"><button type="button" class="on" data-t="">' + E(L("Hele øen")) + '</button>'
                     + "".join(f'<button type="button" data-t="{E(t)}">{E(t)}</button>' for t in towns) + '</div>')
        h.append('<ol class="times">')
        for it in x["items"]:
            end = f' data-end="{it["end"]}"' if it["end"] else ""
            reg = ('<a class="reg" href="' + E(it["url"]) + '" rel="noopener">' + E(it["reg"]) + ' ↗</a>') if it.get("reg") else ""
            h.append(f'<li{end} data-town="{E(it["town"])}">{icon(it["kind"])}<span class="t">{E(it["time"])}</span><span class="what"><b>{link(it["title"], it["url"])}</b><span class="where">{E(it["where"])}</span>{reg}</span></li>')
        h.append("</ol>")
    else:
        h.append(f'<p class="quiet">{L("Ingen arrangementer i kalenderen endnu.")}</p>')
    if x["food"] or x["unknown"]:
        h.append(f'<details class="food"><summary>{icon("mad")}<span>{L("Spisesteder, barer og is, der har åbent")} <b>{len(x["food"])}</b></span></summary>'
                 '<ul>')
        last = None
        for f in x["food"]:
            if many and f["town"] != last:
                h.append(f'<li class="fhead">{E(f["town"])}</li>'); last = f["town"]
            unsure = f' <span class="unsure">{L("tid usikker")}</span>' if not f.get("sure", True) else ""
            h.append(f'<li><span class="what"><b>{link(f["name"], f["url"])}{unsure}</b><small>{E(f["desc"])}</small></span><span class="t">{E(f["hours"])}</span></li>')
        h.append("</ul>")
        if x["unknown"]:
            h.append(f'<p class="unk"><b>{L("Tjek selv åbningstiden")}:</b> ' + ", ".join(link(u["name"], u["url"]) + (f' ({E(u["town"])})' if many else "") for u in x["unknown"]) + "</p>")
        h.append('</details>')
    h.append("</section>")
    return "\n".join(h)

def build_later(g, events, today):
    start, end = today + datetime.timedelta(days=DAYS), today + datetime.timedelta(days=LATER_DAYS)
    many = g["towns"] is None
    rows = []
    for e in events:
        if not in_guide(e, g): continue
        d1 = datetime.date.fromisoformat(e["d"]); d2 = datetime.date.fromisoformat(e.get("to") or e["d"])
        k = kind_of(e)
        if k == "film" or (many and k == "kirke"): continue      # film planlægges ikke langt frem; gudstjenester fylder for meget på øsiden
        if e.get("long"):
            if d2 < start or d1 > end: continue
        elif d1 < start or d1 > end: continue
        tt = (hm(e["t"]) + (("–" + hm(e["t2"])) if e.get("t2") else "")) if e.get("t") else ""
        where = e.get("where", "") + ((", " + e["town"]) if many and e["town"].lower() not in e.get("where", "").lower() else "")
        rows.append({"d": d1, "to": d2, "time": tt, "title": L(e["title"]), "where": where, "url": e.get("rurl") or e.get("url"),
                     "kind": k, "reg": L(REGTXT.get(e.get("reg"), "")), "long": bool(e.get("long")), "k": max(d1, start)})
    rows.sort(key=lambda r: (r["k"], not r["long"], r["time"], r["title"]))
    months = []
    for r in rows:
        key = (r["k"].year, r["k"].month)
        if not months or months[-1]["k"] != key: months.append({"k": key, "rows": []})
        months[-1]["rows"].append(r)
    return months

def render_later(months, today):
    wd_, wds_, mon_ = DAYNAMES[LANG]
    h = ['<section class="later" id="senere">', f'<h2 class="lhead">{L("Længere frem")}</h2>',
         f'<p class="lsub">{L("Det, der allerede står i kalenderen det næste år. Der kommer flere arrangementer til løbende.")}</p>']
    if not months:
        h.append(f'<p class="quiet">{L("Intet i kalenderen længere frem endnu.")}</p>')
    for i, m in enumerate(months):
        y, mo = m["k"]
        h.append(f'<details class="month"{" open" if i == 0 else ""}><summary><span class="mn">{E(mon_[mo - 1].capitalize())}</span>'
                 f'{("<span class=my>" + str(y) + "</span>") if y != today.year else ""}<b>{len(m["rows"])}</b></summary><ol class="lrows">')
        for r in m["rows"]:
            d, t = r["d"], r["to"]
            per = ""
            if r["long"]:
                dd, wtxt = f"{t.day}/{t.month}", L("til")
                f = lambda x: (f"{x.day}. {mon_[x.month - 1][:3]}" if LANG != "en" else f"{mon_[x.month - 1][:3]} {x.day}")
                per = f"{f(d)} – {f(t)}" + (f" {t.year}" if t.year != d.year else "")
            elif t != d:
                dd = (f"{d.day}.–{t.day}." if LANG != "en" else f"{d.day}–{t.day}") if t.month == d.month else f"{d.day}/{d.month}–{t.day}/{t.month}"
                wtxt = f"{wds_[d.weekday()]}–{wds_[t.weekday()]}"
            else:
                dd = f"{d.day}." if LANG in ("da", "de") else str(d.day)
                wtxt = wds_[d.weekday()]
            reg = ('<a class="reg" href="' + E(r["url"]) + '" rel="noopener">' + E(r["reg"]) + ' ↗</a>') if r["reg"] else ""
            where = " · ".join(x for x in (r["where"], per, r["time"]) if x)
            h.append(f'<li><span class="ld"><span class="lwd">{E(wtxt)}</span><span class="ldn">{E(dd)}</span></span>'
                     f'<span class="what"><b>{link(r["title"], r["url"])}</b><span class="where">{E(where)}</span>{reg}</span></li>')
        h.append('</ol></details>')
    h.append('</section>')
    return "\n".join(h)

def jsonld(g, days, later):
    evs = [{"@type": "WebPage", "name": seo_title(g), "url": BASE + LANG_PRE[LANG] + g["path"], "inLanguage": LANG,
            "about": {"@type": "Place", "name": g["name"], "address": {"@type": "PostalAddress", "addressLocality": g["name"], "addressRegion": "Bornholm", "addressCountry": "DK"}},
            "isPartOf": {"@type": "WebSite", "name": "detskeri.dk", "url": BASE}}, breadcrumbs(g)]
    def ev(name, start, where, town, url, endd=None):
        return {"@type": "Event", "name": name, "startDate": start, **({"endDate": endd} if endd else {}), "eventStatus": "https://schema.org/EventScheduled",
                "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
                "location": {"@type": "Place", "name": where or town, "address": {"@type": "PostalAddress", "addressLocality": town, "addressCountry": "DK"}},
                **({"url": url} if url else {})}
    for x in days:
        for it in x["items"]:
            if it["s"] < 0 or it["kind"] in ("film", "kirke"): continue
            st = datetime.datetime.combine(x["d"], datetime.time(it["s"] // 60, it["s"] % 60), TZ).isoformat()
            evs.append(ev(it["title"], st, it["where"], it["town"], it["url"]))
    for m in later:
        for r in m["rows"]:
            evs.append(ev(r["title"], r["d"].isoformat(), r["where"], g["name"], r["url"], r["to"].isoformat() if r["to"] != r["d"] else None))
    return json.dumps({"@context": "https://schema.org", "@graph": evs[:151]}, ensure_ascii=False).replace("</", "<\\/")

def guide_nav(g, depth):
    """Menu over guiderne (relative links)."""
    up = "../" * depth
    out = []
    for o in GUIDES:
        label = L("Hele øen") if o["slug"] == "bornholm" else o["name"]
        cur = ' aria-current="page"' if o is g else ""
        out.append(f'<a href="{up}{LANG_PRE[LANG]}{o["path"]}"{cur}>{E(label)}</a>')
    out.append(f'<a href="{GUDHJEM}{LANG_PRE[LANG]}" rel="noopener">Gudhjem ↗</a>')
    return "".join(out)

def main():
    global LANG, DTR
    evdata, places, DTR = load()
    events = evdata["events"]
    today = datetime.datetime.now(TZ).date()
    tpl0 = (ROOT / "template.html").read_text(encoding="utf-8")
    site = ROOT / "site"
    if site.exists(): shutil.rmtree(site)
    site.mkdir()
    sitemap = []
    for g in GUIDES:
        for LANG in LANGS:
            path = LANG_PRE[LANG] + g["path"]
            depth = path.count("/")
            wd_, wds_, mon_ = DAYNAMES[LANG]
            days = [build_day(g, events, places, today + datetime.timedelta(days=i)) for i in range(DAYS)]
            later = build_later(g, events, today)
            nav = "".join(f'<a href="#d-{x["iso"]}" data-date="{x["iso"]}">{L("I dag") if i == 0 else L("I morgen") if i == 1 else wds_[x["d"].weekday()].capitalize() + " " + str(x["d"].day) + ("." if LANG in ("da", "de") else "")}</a>' for i, x in enumerate(days))
            nav += f'<a href="#senere" class="latr">{L("Længere frem")}</a>'
            body = "\n".join(render_day(g, x, i) for i, x in enumerate(days)) + "\n" + render_later(later, today) + "\n" + render_about(g, depth)
            n_week = sum(len(x["items"]) for x in days)
            hreflang = "\n".join(f'<link rel="alternate" hreflang="{l}" href="{BASE}{LANG_PRE[l]}{g["path"]}">' for l in LANGS) + f'\n<link rel="alternate" hreflang="x-default" href="{BASE}{g["path"]}">'
            langs = "".join(f'<a href="{"../" * depth}{LANG_PRE[l]}{g["path"]}" hreflang="{l}" lang="{l}" aria-current="{str(l == LANG).lower()}">{l.upper()}</a>' for l in LANGS)
            upd = f"{mon_[today.month - 1]} {today.day}, {today.year}" if LANG == "en" else f"{today.day}. {mon_[today.month - 1]} {today.year}"
            many = g["towns"] is None
            lead = L("Øens kalender: koncerter, film, teater, kirke, børneaktiviteter og spisesteder med åbent i alle byerne – samlet ét sted og opdateret hver morgen.") if many else \
                   L("Byens kalender: koncerter, film, teater, kirke, børneaktiviteter og spisesteder med åbent – samlet ét sted og opdateret hver morgen.")
            ttl = title_of(g)
            h1 = E(ttl[: len(ttl) - len(g_in(g))].strip()) + "<br>" + E(g_in(g))
            out = (tpl0.replace("– i dag og de næste dage", "– " + L("i dag og de næste dage")).replace("{{LANG}}", LANG).replace("<title>{{TITLE}} – i dag og de næste dage</title>", "<title>" + E(seo_title(g)) + "</title>").replace("{{DESC}}", E(seo_desc(g, 0, n_week)))
                   .replace("{{OGIMG}}", f"del-{g['slug']}.png").replace("{{TITLE}}", E(ttl)).replace("{{H1}}", h1).replace("{{LEAD}}", E(lead))
                   .replace("{{CANON}}", BASE + path).replace("{{HREFLANG}}", hreflang).replace("{{LANGS}}", langs)
                   .replace("{{GUIDES}}", guide_nav(g, depth)).replace("{{TOWN}}", tegning.svg(g["slug"])).replace("{{NAV}}", nav).replace("{{DAYS}}", body)
                   .replace("{{JSONLD}}", jsonld(g, days, later)).replace("{{UPDATED}}", f'{L("Opdateret")} {upd}.')
                   .replace("{{SRC}}", L("Arrangementer fra")).replace("{{TODAY}}", L("I dag")).replace("{{TOMORROW}}", L("I morgen"))
                   .replace("{{FIX}}", L("Mangler der noget, eller er en tid forkert? Skriv til")).replace("{{UP}}", "../" * depth).replace("{{COOKIE}}", L("Cookie-valg"))
                   .replace("{{ADDURL}}", "../" * depth + LANG_PRE[LANG] + "tilfoej/").replace("{{ADD}}", tilfoej.link_text(LANG)).replace("{{NEWS}}", tilmeld.box(g["slug"], LANG)).replace("{{NEWSCSS}}", tilmeld.assets()[0]).replace("{{NEWSJS}}", tilmeld.assets()[1])
                   .replace("{{VALGDAG}}", L("Vælg dag")).replace("{{OGLOCALE}}", {"da": "da_DK", "en": "en_GB", "de": "de_DE", "sv": "sv_SE"}[LANG]))
            out = re.sub(r"<title>.*?</title>", lambda _m: "<title>" + E(seo_title(g)) + "</title>", out, count=1)
            dst = site / path; dst.mkdir(parents=True, exist_ok=True)
            (dst / "index.html").write_text(out, encoding="utf-8")
            sitemap.append(BASE + path)
    # forsiden: én side pr. sprog, der viser vej til guiderne
    for LANG in LANGS:
        depth = LANG_PRE[LANG].count("/")
        cards = []
        for g in GUIDES:
            n = sum(1 for e in events if not e.get("long") and in_guide(e, g) and on_day(e, today))
            cards.append(f'<a class="card{" big" if g["towns"] is None else ""}" href="{"../" * depth}{LANG_PRE[LANG]}{g["path"]}"><span class="cn">{E(title_of(g))}</span><span class="cc">{n} {E(L("arrangementer i dag"))}</span></a>')
        cards.append(f'<a class="card" href="{GUDHJEM}{LANG_PRE[LANG]}" rel="noopener"><span class="cn">{E(title_of({"name": "Gudhjem"}))} ↗</span><span class="cc">detskerigudhjem.dk</span></a>')
        langs = "".join(f'<a href="{"../" * depth}{LANG_PRE[l]}" hreflang="{l}" lang="{l}" aria-current="{str(l == LANG).lower()}">{l.upper()}</a>' for l in LANGS)
        hreflang = "\n".join(f'<link rel="alternate" hreflang="{l}" href="{BASE}{LANG_PRE[l]}">' for l in LANGS) + f'\n<link rel="alternate" hreflang="x-default" href="{BASE}">'
        ttl = {"da": "Det sker i …", "en": "What's on in …", "de": "Was ist los in …", "sv": "Det händer i …"}[LANG]
        out = ((ROOT / "forside.html").read_text(encoding="utf-8").replace("{{LANG}}", LANG).replace("{{TITLE}}", E(ttl))
               .replace("{{H2}}", E(L("Hvad sker der i dag?"))).replace("{{LEAD}}", E(L("Se dagens arrangementer, film og spisesteder med åbent i hver by.")))
               .replace("{{CARDS}}", "".join(cards)).replace("{{TOWN}}", tegning.svg("bornholm")).replace("{{LANGS}}", langs).replace("{{HREFLANG}}", hreflang).replace("{{CANON}}", BASE + LANG_PRE[LANG])
               .replace("{{UP}}", "../" * depth).replace("{{COOKIE}}", L("Cookie-valg"))
               .replace("{{ADDURL}}", "../" * depth + LANG_PRE[LANG] + "tilfoej/").replace("{{ADD}}", tilfoej.link_text(LANG)).replace("{{NEWS}}", tilmeld.box("bornholm", LANG)).replace("{{NEWSCSS}}", tilmeld.assets()[0]).replace("{{NEWSJS}}", tilmeld.assets()[1]))
        dst = site / LANG_PRE[LANG]; dst.mkdir(parents=True, exist_ok=True)
        (dst / "index.html").write_text(out, encoding="utf-8")
        sitemap.append(BASE + LANG_PRE[LANG])
    # "Tilføj dit arrangement"
    for LANG in LANGS:
        path = LANG_PRE[LANG] + "tilfoej/"; depth = path.count("/"); up = "../" * depth
        langs = "".join(f'<a href="{up}{LANG_PRE[l]}tilfoej/" hreflang="{l}" lang="{l}" aria-current="{str(l == LANG).lower()}">{l.upper()}</a>' for l in LANGS)
        hreflang = "\n".join(f'<link rel="alternate" hreflang="{l}" href="{BASE}{LANG_PRE[l]}tilfoej/">' for l in LANGS)
        dst = site / path; dst.mkdir(parents=True, exist_ok=True)
        (dst / "index.html").write_text(tilfoej.page(LANG, up, up + LANG_PRE[LANG], langs, hreflang, BASE + path), encoding="utf-8")
        sitemap.append(BASE + path)
    (site / "tak").mkdir(exist_ok=True); (site / "tak" / "index.html").write_text(tilmeld.tak_page(), encoding="utf-8")
    LANG = "da"
    for f in (ROOT / "static").glob("*"):
        shutil.copy(f, site / f.name)
    (site / "CNAME").write_text("detskeri.dk\n", encoding="utf-8")
    (site / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n", encoding="utf-8")
    urls = "".join(f"<url><loc>{u}</loc><lastmod>{today.isoformat()}</lastmod><changefreq>daily</changefreq></url>" for u in sorted(set(sitemap)))
    (site / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n', encoding="utf-8")
    print("Bygget:", len(sitemap), "sider")

if __name__ == "__main__":
    main()
