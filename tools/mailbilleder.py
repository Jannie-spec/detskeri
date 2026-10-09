"""Gemmer byernes tegninger som PNG til nyhedsbrevet (static/mail-<by>.png) – mailprogrammer kan ikke vise SVG.
Køres efter ændringer i tegning.py:  python tools/mailbilleder.py   (Gudhjem tages fra ../detskerigudhjem/site/index.html)"""
import sys, pathlib
from playwright.sync_api import sync_playwright
from PIL import Image
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools")); import tegning
OUT = ROOT / "static"
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 600, "height": 400}, device_scale_factor=2)
    for slug in tegning.SCENES:
        svg = tegning.svg(slug).replace('class="town"', 'style="display:block;width:600px;height:190px"')
        pg.set_content(f"<body style='margin:0;background:#e5e9e1'>{svg}</body>")
        pg.locator("svg").screenshot(path=str(OUT / f"mail-{slug}.png"))
    gh = ROOT.parent / "detskerigudhjem" / "site" / "index.html"
    if gh.exists():
        pg.set_viewport_size({"width": 1200, "height": 900}); pg.goto(gh.as_uri()); pg.wait_for_timeout(500)
        pg.locator("svg.town").first.screenshot(path=str(OUT / "mail-gudhjem.png"))
    b.close()
for f in OUT.glob("mail-*.png"):
    Image.open(f).convert("RGB").resize((1200, 380), Image.LANCZOS).save(f, optimize=True)
print("ok")

# Delebilleder til Facebook m.m. (static/del-<by>.png, 1200×630): titel øverst, tegningen nederst
TITLES = {"bornholm": "Det sker<br>på Bornholm", "roenne": "Det sker<br>i Rønne", "svaneke": "Det sker<br>i Svaneke", "allinge": "Det sker<br>i Allinge",
          "nexoe": "Det sker<br>i Nexø", "hasle": "Det sker<br>i Hasle"}
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 630})
    for slug, t in TITLES.items():
        svg = tegning.svg(slug).replace('class="town"', 'style="position:absolute;left:0;bottom:0;width:1200px;height:380px"')
        pg.set_content(f"""<body style="margin:0;width:1200px;height:630px;background:#e5e9e1;position:relative;overflow:hidden">
<div style="position:absolute;left:64px;top:38px;font:400 84px/1 Georgia,'DejaVu Serif',serif;color:#302f2f">{t}</div>
<div style="position:absolute;right:56px;top:52px;font:700 27px 'DejaVu Sans',Arial,sans-serif;color:#5f625e">detskeri.dk</div>{svg}</body>""")
        pg.screenshot(path=str(OUT / f"del-{slug}.png"))
    b.close()
print("delebilleder ok")
