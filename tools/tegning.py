"""Tegner byernes panorama (set fra havet) som flad SVG, 1200×380 – samme stil som Gudhjem-tegningen.
Hver by er en liste af vartegn med vandret placering. Ret rækkefølgen i SCENES nederst."""
import random

W, H, SEA = 1200, 380, 304
C = dict(white="#ffffff", cream="#f6f3ec", yellow="#f2dfa8", ochre="#efc95a", sand="#efe3c8", red="#b4533a", coral="#e37b5b",
         brick="#a9442f", roof="#4c5553", stone="#bfc3bf", grey="#8f9592", deep="#3f6670", sea="#c6d8d9", hill="#c3cfc0",
         hill2="#9fb09b", rock="#a8998e", rockline="#8a7b70", green="#7f9a7a", dark="#3b3f3e", sol="#f2c46b", ink="#302f2f")

def win(x, y, w=10, h=11):
    return f'<rect x="{x:.0f}" y="{y:.0f}" width="{w}" height="{h}" fill="{C["deep"]}"/>'

def house(x, gy, w=46, h=32, wall="cream", roof="coral", n=1):
    s = f'<rect x="{x:.0f}" y="{gy - h:.0f}" width="{w}" height="{h}" fill="{C[wall]}"/>'
    s += f'<path d="M{x - 5:.0f} {gy - h + 2:.0f} L{x + w / 2:.0f} {gy - h - 20:.0f} L{x + w + 5:.0f} {gy - h + 2:.0f}Z" fill="{C[roof]}"/>'
    step = w / (n + 1)
    for i in range(n):
        s += win(x + step * (i + 1) - 5, gy - h + 9)
    return s

def houses(x0, x1, gy, seed=1, tall=False):
    r = random.Random(seed); s = ""; x = x0
    walls, roofs = ["cream", "yellow", "sand", "white", "ochre"], ["coral", "red", "red", "coral", "roof"]
    while x < x1 - 30:
        w = r.choice([40, 46, 50, 56]); h = r.choice([28, 32, 34]) + (8 if tall else 0)
        s += house(x, gy + r.choice([0, 2, 4]), w, h, r.choice(walls), r.choice(roofs), 1 if w < 50 else 2)
        x += w + r.choice([6, 10, 14])
    return s

def halftimber(x, gy, w=120, h=40):
    s = f'<rect x="{x}" y="{gy - h}" width="{w}" height="{h}" fill="{C["ochre"]}"/>'
    s += f'<path d="M{x - 4} {gy - h + 2} L{x + 14} {gy - h - 22} L{x + w - 14} {gy - h - 22} L{x + w + 4} {gy - h + 2}Z" fill="{C["red"]}"/>'
    s += f'<g stroke="{C["ink"]}" stroke-width="2.5">' + "".join(f'<line x1="{x + i}" y1="{gy - h}" x2="{x + i}" y2="{gy}"/>' for i in range(0, w + 1, 20)) + \
         f'<line x1="{x}" y1="{gy - h / 2}" x2="{x + w}" y2="{gy - h / 2}"/></g>'
    return s

def church(x, gy, wall="white", roof="red", tower="spire", s=1.0, towerwall=None):
    """Langhus med tårn i venstre ende. x = tårnets midte."""
    tw, th = 30 * s, 92 * s
    nave_w, nave_h = 104 * s, 46 * s
    o = f'<rect x="{x + tw / 2 - 2:.0f}" y="{gy - nave_h:.0f}" width="{nave_w:.0f}" height="{nave_h:.0f}" fill="{C[wall]}"/>'
    o += f'<path d="M{x + tw / 2 - 6:.0f} {gy - nave_h + 2:.0f} L{x + tw / 2 + 10:.0f} {gy - nave_h - 24 * s:.0f} L{x + tw / 2 + nave_w - 12:.0f} {gy - nave_h - 24 * s:.0f} L{x + tw / 2 + nave_w + 4:.0f} {gy - nave_h + 2:.0f}Z" fill="{C[roof]}"/>'
    for i in range(3):
        o += f'<rect x="{x + tw / 2 + 18 * s + i * 28 * s:.0f}" y="{gy - nave_h + 14 * s:.0f}" width="{8 * s:.0f}" height="{18 * s:.0f}" rx="{4 * s:.0f}" fill="{C["deep"]}"/>'
    o += f'<rect x="{x - tw / 2:.0f}" y="{gy - th:.0f}" width="{tw:.0f}" height="{th:.0f}" fill="{C[towerwall or wall]}"/>'
    o += f'<rect x="{x - 4 * s:.0f}" y="{gy - th + 16 * s:.0f}" width="{8 * s:.0f}" height="{12 * s:.0f}" rx="{4 * s:.0f}" fill="{C["deep"]}"/>'
    top = gy - th
    if tower == "spire":
        o += f'<path d="M{x - tw / 2 - 3:.0f} {top + 1:.0f} L{x:.0f} {top - 46 * s:.0f} L{x + tw / 2 + 3:.0f} {top + 1:.0f}Z" fill="{C["roof"]}"/>'
        o += f'<path d="M{x:.0f} {top - 46 * s:.0f} V{top - 58 * s:.0f}" stroke="{C["roof"]}" stroke-width="3"/>'
    elif tower == "pyramid":
        o += f'<path d="M{x - tw / 2 - 3:.0f} {top + 1:.0f} L{x:.0f} {top - 22 * s:.0f} L{x + tw / 2 + 3:.0f} {top + 1:.0f}Z" fill="{C[roof]}"/>'
    elif tower == "copper":
        o += f'<path d="M{x - tw / 2 - 3:.0f} {top + 1:.0f} L{x:.0f} {top - 50 * s:.0f} L{x + tw / 2 + 3:.0f} {top + 1:.0f}Z" fill="#6f9a8a"/>'
    elif tower == "octagon":
        o += f'<path d="M{x - tw / 2 - 3:.0f} {top + 1:.0f} L{x - 6 * s:.0f} {top - 40 * s:.0f} L{x + 6 * s:.0f} {top - 40 * s:.0f} L{x + tw / 2 + 3:.0f} {top + 1:.0f}Z" fill="{C["roof"]}"/>'
    return o

def roundchurch(x, gy, s=1.0):
    o = f'<rect x="{x - 46 * s:.0f}" y="{gy - 100 * s:.0f}" width="{92 * s:.0f}" height="{100 * s:.0f}" fill="{C["white"]}"/>'
    o += f'<path d="M{x - 56 * s:.0f} {gy:.0f} L{x - 46 * s:.0f} {gy - 40 * s:.0f} L{x - 46 * s:.0f} {gy:.0f}Z M{x + 56 * s:.0f} {gy:.0f} L{x + 46 * s:.0f} {gy - 40 * s:.0f} L{x + 46 * s:.0f} {gy:.0f}Z" fill="#e9e6de"/>'
    o += f'<path d="M{x - 52 * s:.0f} {gy - 98 * s:.0f} L{x:.0f} {gy - 172 * s:.0f} L{x + 52 * s:.0f} {gy - 98 * s:.0f}Z" fill="{C["roof"]}"/>'
    for dx in (-24, 0, 24):
        o += f'<rect x="{x + dx * s - 4 * s:.0f}" y="{gy - 74 * s:.0f}" width="{8 * s:.0f}" height="{16 * s:.0f}" rx="{4 * s:.0f}" fill="{C["deep"]}"/>'
    o += f'<rect x="{x - 10 * s:.0f}" y="{gy - 28 * s:.0f}" width="{20 * s:.0f}" height="{28 * s:.0f}" rx="{10 * s:.0f}" fill="{C["deep"]}"/>'
    return o

def lighthouse_sq(x, gy, h=96, body="brick"):
    o = f'<path d="M{x - 13} {gy} L{x - 10} {gy - h} L{x + 10} {gy - h} L{x + 13} {gy}Z" fill="{C[body]}"/>'
    o += f'<rect x="{x - 12}" y="{gy - h - 4}" width="24" height="5" fill="{C["dark"]}"/><rect x="{x - 8}" y="{gy - h - 22}" width="16" height="18" fill="{C["white"]}"/>'
    o += f'<path d="M{x - 10} {gy - h - 22} L{x} {gy - h - 32} L{x + 10} {gy - h - 22}Z" fill="{C["red"]}"/>'
    return o

def lighthouse_tall(x, gy, h=190):
    o = f'<path d="M{x - 15} {gy} L{x - 9} {gy - h} L{x + 9} {gy - h} L{x + 15} {gy}Z" fill="{C["white"]}"/>'
    o += f'<rect x="{x - 12}" y="{gy - h - 4}" width="24" height="5" fill="{C["dark"]}"/><rect x="{x - 7}" y="{gy - h - 20}" width="14" height="16" fill="{C["sol"]}"/>'
    o += f'<path d="M{x - 9} {gy - h - 20} L{x} {gy - h - 30} L{x + 9} {gy - h - 20}Z" fill="{C["dark"]}"/>'
    for i in range(1, 4):
        o += f'<rect x="{x - 2}" y="{gy - h * i / 4 - 6:.0f}" width="4" height="10" fill="{C["deep"]}"/>'
    return o

def smokehouse(x, gy, n=3, h=64):
    o = f'<rect x="{x - 8}" y="{gy - 26}" width="{n * 30 + 12}" height="26" fill="{C["cream"]}"/>'
    for i in range(n):
        cx = x + i * 30
        o += f'<path d="M{cx} {gy - 20} L{cx + 7} {gy - h} L{cx + 19} {gy - h} L{cx + 26} {gy - 20}Z" fill="{C["white"]}"/>'
    o += f'<path d="M{x + 13} {gy - h - 2} C{x + 6} {gy - h - 20} {x + 30} {gy - h - 26} {x + 22} {gy - h - 44}" fill="none" stroke="{C["white"]}" stroke-width="6" stroke-linecap="round" opacity=".9"/>'
    return o

def watertower(x, gy, h=150):
    """Utzons vandtårn: pyramide på tre ben, mørk træbeklædning."""
    o = f'<path d="M{x - 34} {gy} L{x} {gy - h} L{x + 34} {gy}" fill="none" stroke="{C["stone"]}" stroke-width="7"/>'
    o += f'<path d="M{x} {gy} L{x} {gy - h}" stroke="{C["stone"]}" stroke-width="5"/>'
    o += f'<path d="M{x - 20} {gy - h * .42} L{x} {gy - h - 6} L{x + 20} {gy - h * .42}Z" fill="#5b4a3c"/>'
    o += f'<g stroke="#7a6654" stroke-width="2">' + "".join(f'<line x1="{x - 18 + i * 6}" y1="{gy - h * .44}" x2="{x - 18 + i * 6 + (18 - i * 6) * 0.95:.0f}" y2="{gy - h + 2}"/>' for i in range(1, 6)) + '</g>'
    return o

def dutchmill(x, gy, s=1.0):
    o = f'<path d="M{x - 20 * s:.0f} {gy:.0f} L{x - 13 * s:.0f} {gy - 66 * s:.0f} L{x + 13 * s:.0f} {gy - 66 * s:.0f} L{x + 20 * s:.0f} {gy:.0f}Z" fill="{C["white"]}"/>'
    o += f'<path d="M{x - 15 * s:.0f} {gy - 66 * s:.0f} C{x - 15 * s:.0f} {gy - 84 * s:.0f} {x + 15 * s:.0f} {gy - 84 * s:.0f} {x + 15 * s:.0f} {gy - 66 * s:.0f}Z" fill="{C["roof"]}"/>'
    cy = gy - 74 * s
    o += f'<g transform="translate({x:.0f} {cy:.0f}) rotate(22)" fill="{C["cream"]}" stroke="{C["grey"]}" stroke-width="2">' + \
         "".join(f'<rect x="-5" y="-62" width="10" height="56" transform="rotate({a})"/>' for a in (0, 90, 180, 270)) + '</g>'
    o += f'<rect x="{x - 6 * s:.0f}" y="{gy - 22 * s:.0f}" width="{12 * s:.0f}" height="{22 * s:.0f}" fill="{C["red"]}"/>'
    return o

def stubmill(x, gy):
    o = f'<path d="M{x} {gy} L{x} {gy - 40}" stroke="{C["grey"]}" stroke-width="5"/><path d="M{x - 16} {gy} L{x} {gy - 26} L{x + 16} {gy}" fill="none" stroke="{C["grey"]}" stroke-width="3"/>'
    o += f'<rect x="{x - 16}" y="{gy - 76}" width="32" height="38" fill="{C["red"]}"/><path d="M{x - 18} {gy - 74} L{x} {gy - 92} L{x + 18} {gy - 74}Z" fill="{C["roof"]}"/>'
    o += f'<g transform="translate({x - 18} {gy - 60}) rotate(30)" fill="{C["cream"]}" stroke="{C["grey"]}" stroke-width="2">' + \
         "".join(f'<rect x="-4" y="-54" width="8" height="48" transform="rotate({a})"/>' for a in (0, 90, 180, 270)) + '</g>'
    return o

def ruin(x, gy, s=1.0):
    """Hammershus: grå granitmure med det firkantede Manteltårn."""
    o = f'<path d="M{x - 90 * s:.0f} {gy:.0f} V{gy - 30 * s:.0f} h{14 * s:.0f} v{-8 * s:.0f} h{10 * s:.0f} v{8 * s:.0f} h{40 * s:.0f} V{gy - 44 * s:.0f} h{12 * s:.0f} v{10 * s:.0f} h{60 * s:.0f} v{-6 * s:.0f} h{12 * s:.0f} v{6 * s:.0f} h{30 * s:.0f} V{gy:.0f}Z" fill="#9aa09c"/>'
    o += f'<path d="M{x - 18 * s:.0f} {gy:.0f} V{gy - 108 * s:.0f} l{8 * s:.0f} {-8 * s:.0f} l{6 * s:.0f} {6 * s:.0f} l{10 * s:.0f} {-10 * s:.0f} l{8 * s:.0f} {8 * s:.0f} l{10 * s:.0f} {-4 * s:.0f} V{gy:.0f}Z" fill="#878d89"/>'
    for i in range(3):
        o += f'<rect x="{x - 4 * s:.0f}" y="{gy - (88 - i * 26) * s:.0f}" width="{8 * s:.0f}" height="{12 * s:.0f}" rx="{4 * s:.0f}" fill="{C["dark"]}"/>'
    o += f'<rect x="{x - 60 * s:.0f}" y="{gy - 22 * s:.0f}" width="{8 * s:.0f}" height="{12 * s:.0f}" rx="{4 * s:.0f}" fill="{C["dark"]}"/><rect x="{x + 50 * s:.0f}" y="{gy - 26 * s:.0f}" width="{8 * s:.0f}" height="{12 * s:.0f}" rx="{4 * s:.0f}" fill="{C["dark"]}"/>'
    return o

def kastellet(x, gy):
    """Rundt, lavt fæstningstårn med kegletag."""
    return (f'<path d="M{x - 32} {gy} V{gy - 50} Q{x} {gy - 58} {x + 32} {gy - 50} V{gy} Q{x} {gy + 6} {x - 32} {gy}Z" fill="{C["sand"]}"/>'
            f'<path d="M{x - 38} {gy - 50} L{x} {gy - 96} L{x + 38} {gy - 50} Q{x} {gy - 42} {x - 38} {gy - 50}Z" fill="{C["red"]}"/>'
            f'<rect x="{x - 4}" y="{gy - 36}" width="8" height="12" rx="4" fill="{C["deep"]}"/>')

def silos(x, gy, n=3):
    o = ""
    for i in range(n):
        o += f'<rect x="{x + i * 26}" y="{gy - 84}" width="24" height="84" fill="#d9dcd8"/><path d="M{x + i * 26} {gy - 84} q12 -10 24 0Z" fill="#c4c8c4"/>'
    return o

def crane(x, gy):
    return (f'<g stroke="{C["coral"]}" stroke-width="5" fill="none"><path d="M{x} {gy} V{gy - 100} H{x + 70}"/><path d="M{x} {gy - 80} L{x + 40} {gy - 100}"/>'
            f'<path d="M{x + 60} {gy - 100} V{gy - 62}" stroke-width="2"/></g>')

def museum(x, gy):
    return (f'<rect x="{x}" y="{gy - 44}" width="80" height="44" fill="#e3c9a0"/><path d="M{x - 4} {gy - 42} L{x + 40} {gy - 62} L{x + 84} {gy - 42}Z" fill="{C["red"]}"/>'
            + win(x + 14, gy - 32) + win(x + 35, gy - 32) + win(x + 56, gy - 32))

def chimney(x, gy, h=150):
    return f'<path d="M{x - 9} {gy} L{x - 6} {gy - h} L{x + 6} {gy - h} L{x + 9} {gy}Z" fill="{C["stone"]}"/><rect x="{x - 7}" y="{gy - h}" width="14" height="10" fill="{C["red"]}"/>'

def trees(x0, x1, gy, seed=3):
    r = random.Random(seed); o = ""
    x = x0
    while x < x1:
        rr = r.choice([16, 20, 24]); o += f'<circle cx="{x}" cy="{gy - rr}" r="{rr}" fill="{r.choice(["#7f9a7a", "#8aa585", "#6f8a6b"])}"/>'
        x += rr * 1.3
    return o

def knoll(x0, x1, gy, peak):
    m = (x0 + x1) / 2
    return (f'<path d="M{x0} {gy} C{x0 + 40} {gy - peak * .6} {m - 60} {gy - peak} {m} {gy - peak} C{m + 60} {gy - peak} {x1 - 40} {gy - peak * .6} {x1} {gy}Z" fill="{C["hill2"]}"/>'
            f'<path d="M{x0 + 20} {gy} C{x0 + 50} {gy - peak * .4} {m - 40} {gy - peak * .7} {m + 10} {gy - peak * .72} C{m + 50} {gy - peak * .7} {x1 - 60} {gy - peak * .4} {x1 - 30} {gy}Z" fill="{C["rock"]}" opacity=".55"/>')

def ferry(x, y, s=1.0):
    return (f'<g transform="translate({x} {y}) scale({s})"><path d="M0 18 L150 18 L136 38 L12 38Z" fill="{C["white"]}"/><rect x="0" y="28" width="146" height="5" fill="#2c4f6b"/>'
            f'<rect x="28" y="0" width="90" height="18" fill="{C["white"]}"/><g fill="{C["deep"]}">' + "".join(f'<rect x="{36 + i * 14}" y="6" width="8" height="6"/>' for i in range(6)) +
            f'</g><rect x="64" y="-12" width="12" height="12" fill="#2c4f6b"/></g>')

def boat(x, y, color="red", sail=True):
    o = f'<path d="M{x} {y + 10} L{x + 56} {y + 10} L{x + 47} {y + 22} L{x + 8} {y + 22}Z" fill="{C[color]}"/>'
    if sail:
        o += f'<rect x="{x + 26}" y="{y - 14}" width="4" height="24" fill="{C["ink"]}"/><path d="M{x + 30} {y - 12} L{x + 47} {y + 6} L{x + 30} {y + 6}Z" fill="{C["cream"]}"/>'
    else:
        o += f'<rect x="{x + 18}" y="{y - 2}" width="20" height="12" fill="{C["cream"]}"/><rect x="{x + 34}" y="{y - 22}" width="3" height="32" fill="{C["ink"]}"/>'
    return o

def mole(x0, x1, y=SEA - 8):
    return f'<g fill="#8e9f8b"><rect x="{x0}" y="{y}" width="12" height="40"/><rect x="{x0}" y="{y + 30}" width="{x1 - x0}" height="10"/><rect x="{x1 - 12}" y="{y - 6}" width="12" height="46"/></g>'

def ground(profile, color, extra=""):
    pts = " ".join(f"L{x} {y}" for x, y in profile)
    return f'<path d="M0 {SEA + 10} {pts} L1200 {SEA + 10} Z" fill="{C[color]}"/>' + extra

def frame(body, front="", hills=True, sunx=1100):
    s = [f'<circle cx="{sunx}" cy="70" r="40" fill="{C["sol"]}" opacity=".75"/>']
    if hills:
        s.append(f'<path d="M0 230 C140 205 270 175 400 160 C500 148 560 112 630 108 C710 104 770 140 860 140 C960 140 1060 150 1200 175 L1200 380 L0 380Z" fill="{C["hill"]}"/>')
    s.append(body)
    s.append(f'<path d="M0 {SEA} C200 {SEA + 8} 400 {SEA - 6} 600 {SEA + 2} C800 {SEA + 12} 1000 {SEA - 2} 1200 {SEA + 6} L1200 380 L0 380Z" fill="{C["sea"]}"/>')
    s.append(front)
    return "\n".join(s)

WAVES = f'<g fill="none" stroke="{C["deep"]}" stroke-width="3" stroke-linecap="round" opacity=".55"><path d="M60 344 q14 -8 28 0 t28 0"/><path d="M330 356 q14 -8 28 0 t28 0"/><path d="M960 356 q14 -8 28 0 t28 0"/><path d="M1090 346 q14 -8 28 0 t28 0"/></g>'

# ---------- byerne (venstre → højre, set fra havet) ----------
def roenne():
    gy = 286
    land = ground([(0, 270), (300, 266), (700, 270), (1200, 266)], "hill2")
    b = land; f = ""
    b += houses(20, 200, gy, 11)                                     # Nørrekås
    f += boat(140, SEA - 4, "deep", sail=False)
    b += church(330, gy - 6, "white", "red", "spire", 1.05)          # Sankt Nicolai Kirke
    b += lighthouse_sq(440, gy - 2, 70, "white")                     # Rønne Fyr
    b += houses(470, 640, gy, 12)
    f += mole(560, 900)
    f += ferry(640, SEA - 12, 1.25)                                  # færgehavnen
    b += crane(900, gy)
    b += chimney(1000, gy, 160)                                      # kraftværket
    b += houses(1040, 1080, gy, 13)
    b += kastellet(1130, gy - 2)                                     # Kastellet
    return frame(b, f) + WAVES

def svaneke():
    gy = 280
    land = ground([(0, 284), (120, 262), (260, 250), (420, 262), (560, 276), (720, 270), (880, 250), (1040, 262), (1200, 276)], "hill2",
                  f'<path d="M0 {SEA + 6} C40 288 100 282 150 {SEA + 6}Z" fill="{C["rock"]}"/>')
    b = land; f = ""
    b += church(170, 254, "red", "red", "octagon", 1.0, towerwall="stone")   # Svaneke Kirke
    b += lighthouse_sq(330, 266, 92)                                         # Svaneke Fyr
    b += houses(240, 300, 250, 23, tall=True)
    b += houses(380, 560, 268, 21); b += houses(420, 540, 240, 24)
    b += houses(640, 760, 266, 25)
    f += mole(560, 760)
    f += boat(610, SEA - 4, "red")
    b += halftimber(770, 272, 110, 38)
    b += watertower(920, 252, 156)                                           # Utzons vandtårn
    b += stubmill(1010, 256)
    b += smokehouse(1080, 272, 3)                                            # røgeriet
    return frame(b, f, sunx=60) + WAVES

def allinge():
    gy = 282
    f = ""
    b = ground([(0, 280), (200, 274), (400, 262), (600, 272), (760, 276), (900, 280), (1200, 280)], "hill2")
    b += knoll(860, 1200, 290, 150)                                          # Hammeren
    b += smokehouse(40, gy, 4)                                               # Allinge Røgeri
    f += mole(190, 330)
    f += boat(230, SEA - 4, "deep", sail=False)
    b += houses(330, 420, 270, 31)
    b += church(440, 262, "yellow", "red", "spire", 0.95)                    # Allinge Kirke
    b += houses(580, 640, 274, 32)
    b += f'<path d="M640 {SEA + 4} C680 270 760 266 800 {SEA + 4}Z" fill="{C["rock"]}"/>'     # Madsebakke
    b += houses(800, 900, 280, 33)                                           # Sandvig
    b += lighthouse_sq(1010, 152, 64, "stone")                               # Hammer Fyr
    b += ruin(1130, 210, 0.7)                                                # Hammershus (silhuet)
    return frame(b, f) + WAVES

def nexoe():
    gy = 286
    f = ""
    b = ground([(0, 290), (240, 284), (600, 282), (1200, 280)], "hill2",
               f'<path d="M0 {SEA + 6} L0 292 C80 290 170 294 240 {SEA + 6}Z" fill="#eadfc6"/>')
    b += trees(900, 1200, 210, 7)                                            # Paradisbakkerne
    b += f'<path d="M820 290 C900 220 1040 196 1200 206 L1200 290Z" fill="{C["hill2"]}"/>'
    b += church(330, gy - 4, "white", "red", "copper", 1.05)                 # Nexø Kirke
    b += museum(470, gy)                                                     # Nexø Museum
    b += houses(560, 640, gy, 41)
    f += mole(600, 900)
    f += boat(650, SEA - 4, "deep", sail=False); f += boat(730, SEA - 2, "red", sail=False)
    b += crane(820, gy)
    b += silos(900, gy, 3)
    return frame(b, f) + WAVES

def hasle():
    gy = 286
    f = ""
    b = ground([(0, 282), (400, 280), (800, 276), (1200, 270)], "hill2")
    b += f'<path d="M700 280 C780 236 840 210 900 206 C960 204 1020 226 1080 270 L1080 290 L700 290Z" fill="#b3c2ae"/>'
    b += church(870, 212, "white", "red", "pyramid", 0.7)                    # Ruts Kirke på bakken
    b += trees(1040, 1200, 276, 9)                                           # Hasle Lystskov
    b += trees(20, 160, 282, 5)
    b += church(380, gy - 2, "white", "red", "pyramid", 1.0)                 # Hasle Kirke
    b += houses(180, 330, gy, 51); b += houses(520, 600, gy, 52)
    f += mole(600, 820)
    f += boat(660, SEA - 4, "red")
    b += smokehouse(980, gy - 4, 3, 70)                                      # Hasle Røgeri (syd for havnen)
    return frame(b, f) + WAVES

def bornholm():
    f = ""
    b = ground([(0, 284), (140, 280), (260, 230), (360, 236), (460, 268), (560, 250), (700, 262), (820, 270), (960, 266), (1080, 286), (1200, 292)], "hill2",
               f'<path d="M1020 {SEA + 6} C1060 290 1140 288 1200 290 L1200 {SEA + 6}Z" fill="#eadfc6"/>')
    b += church(70, 282, "white", "red", "spire", 0.7)                       # Rønne
    f += ferry(30, SEA - 6, 0.6)
    b += f'<path d="M180 {SEA + 6} C200 250 240 232 300 228 C340 226 360 240 380 {SEA + 6}Z" fill="{C["rock"]}"/>'
    b += ruin(290, 232, 0.75)                                                # Hammershus
    b += houses(430, 520, 262, 61)
    b += dutchmill(540, 252, 0.8)                                            # Gudhjem Mølle
    b += roundchurch(660, 264, 0.75)                                         # Østerlars rundkirke
    b += f'<path d="M760 {SEA - 2} q20 -16 46 -4 q14 6 8 {6}Z" fill="{C["rock"]}"/>'      # Christiansø
    b += watertower(890, 268, 120)                                           # Svaneke vandtårn
    b += houses(930, 1010, 270, 62)
    b += lighthouse_tall(1120, 290, 180)                                     # Dueodde Fyr
    return frame(b, f, sunx=770) + WAVES

SCENES = {"bornholm": bornholm, "roenne": roenne, "svaneke": svaneke, "allinge": allinge, "nexoe": nexoe, "hasle": hasle}

def svg(slug, cls="town"):
    return f'<svg class="{cls}" viewBox="0 0 1200 380" preserveAspectRatio="xMidYMax meet" aria-hidden="true">\n{SCENES[slug]()}\n</svg>'

if __name__ == "__main__":
    import pathlib
    out = pathlib.Path(__file__).resolve().parent.parent / "site" / "_tegninger.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text("<body style='margin:0;background:#e5e9e1'>" + "".join(f"<h3 style='font-family:sans-serif;margin:16px'>{k}</h3>" + svg(k) for k in SCENES), encoding="utf-8")
    print(out)
