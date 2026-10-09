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
