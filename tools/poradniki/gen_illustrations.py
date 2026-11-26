# Generuje ilustracje SVG do poradników (static/img/artykuly/<slug>.svg).
# Styl: płaskie, minimalistyczne, bez tekstu (znaczenie niesie atrybut alt).
import sys
from pathlib import Path

OUT = Path(sys.argv[1]) / "static" / "img" / "artykuly"
OUT.mkdir(parents=True, exist_ok=True)

NAVY = "#1f4fa3"
INK = "#16191d"
RED = "#d93a2b"
WHITE = "#ffffff"
GREY = "#d5dae1"


def phone(bubble_accent):
    """Telefon po lewej z dymkiem SMS-a, linkiem i czerwonym wykrzyknikiem."""
    return f"""
  <g transform="translate(150 70)">
    <rect x="0" y="0" width="300" height="490" rx="44" fill="{INK}"/>
    <rect x="14" y="14" width="272" height="462" rx="32" fill="{WHITE}"/>
    <rect x="115" y="30" width="70" height="10" rx="5" fill="{GREY}"/>
    <rect x="40" y="110" width="220" height="150" rx="22" fill="#eef1f5"/>
    <rect x="62" y="136" width="150" height="14" rx="7" fill="{GREY}"/>
    <rect x="62" y="164" width="176" height="14" rx="7" fill="{GREY}"/>
    <rect x="62" y="192" width="120" height="14" rx="7" fill="{GREY}"/>
    <rect x="62" y="222" width="150" height="14" rx="7" fill="{bubble_accent}"/>
    <rect x="40" y="290" width="160" height="60" rx="22" fill="#eef1f5"/>
    <rect x="62" y="313" width="110" height="14" rx="7" fill="{GREY}"/>
    <circle cx="262" cy="104" r="34" fill="{RED}"/>
    <rect x="257" y="84" width="10" height="26" rx="5" fill="{WHITE}"/>
    <circle cx="262" cy="122" r="6" fill="{WHITE}"/>
  </g>"""


def frame(bg, glyph, accent=NAVY):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630" role="img">
  <rect width="1200" height="630" fill="{bg}"/>
  <circle cx="860" cy="315" r="220" fill="{WHITE}" opacity="0.7"/>{phone(accent)}
  <g transform="translate(710 165)">{glyph}
  </g>
</svg>
"""


GLYPHS = {
    # Karton z taśmą
    "sms-doplata-do-paczki": ("#e8f0fe", """
    <polygon points="150,30 275,92 150,154 25,92" fill="#e3b06a"/>
    <polygon points="25,92 150,154 150,280 25,218" fill="#c98f45"/>
    <polygon points="150,154 275,92 275,218 150,280" fill="#b57b37"/>
    <polygon points="88,61 213,123 213,150 88,88" fill="#f6dcae"/>"""),
    # Okienko z 6-cyfrowym kodem i kłódką
    "oszustwo-na-blik-od-znajomego": ("#fdeceb", f"""
    <rect x="20" y="110" width="260" height="130" rx="28" fill="{NAVY}"/>
    <g fill="{WHITE}">
      <circle cx="62" cy="175" r="13"/><circle cx="97" cy="175" r="13"/><circle cx="132" cy="175" r="13"/>
      <circle cx="168" cy="175" r="13"/><circle cx="203" cy="175" r="13"/><circle cx="238" cy="175" r="13"/>
    </g>
    <path d="M110 110 V78 a40 40 0 0 1 80 0 V110" fill="none" stroke="{INK}" stroke-width="20" stroke-linecap="round"/>"""),
    # Dwa dymki rozmowy, w jednym znak zapytania
    "mamo-to-moj-nowy-numer": ("#efe9fb", f"""
    <path d="M20 40 h200 a30 30 0 0 1 30 30 v90 a30 30 0 0 1 -30 30 h-120 l-50 40 v-40 h-30 a30 30 0 0 1 -30 -30 v-90 a30 30 0 0 1 30 -30z" fill="{NAVY}"/>
    <g fill="{WHITE}"><circle cx="80" cy="115" r="13"/><circle cx="125" cy="115" r="13"/><circle cx="170" cy="115" r="13"/></g>
    <path d="M140 170 h110 a30 30 0 0 1 30 30 v50 a30 30 0 0 1 -30 30 h-10 v34 l-40 -34 h-60 a30 30 0 0 1 -30 -30 v-50 a30 30 0 0 1 30 -30z" fill="#7b5ccf"/>
    <path d="M178 212 a17 17 0 1 1 26 14 c-8 5 -9 9 -9 16" fill="none" stroke="{WHITE}" stroke-width="10" stroke-linecap="round"/>
    <circle cx="195" cy="262" r="7" fill="{WHITE}"/>"""),
    # Budynek banku i słuchawka
    "falszywy-pracownik-banku": ("#e6f3ec", f"""
    <polygon points="150,20 280,90 20,90" fill="{NAVY}"/>
    <rect x="30" y="98" width="240" height="18" rx="4" fill="{NAVY}"/>
    <g fill="#3d6fc4"><rect x="48" y="124" width="28" height="100"/><rect x="104" y="124" width="28" height="100"/>
    <rect x="168" y="124" width="28" height="100"/><rect x="224" y="124" width="28" height="100"/></g>
    <rect x="20" y="230" width="260" height="22" rx="4" fill="{NAVY}"/>
    <path d="M196 232 a54 54 0 0 1 98 0" fill="none" stroke="{INK}" stroke-width="12"/>
    <rect x="186" y="228" width="22" height="40" rx="9" fill="{INK}"/>
    <rect x="282" y="228" width="22" height="40" rx="9" fill="{INK}"/>"""),
    # Błyskawica i płomień
    "sms-odciecie-pradu-gazu": ("#fff4d6", """
    <polygon points="140,20 50,170 120,170 90,290 220,120 145,120 190,20" fill="#f2b705"/>
    <path d="M250 290 c-50 0 -70 -40 -55 -80 c10 -26 30 -38 30 -70 c30 20 55 55 55 95 c0 30 -10 55 -30 55z" fill="#e8662c"/>
    <path d="M250 290 c-22 0 -30 -18 -24 -36 c5 -14 15 -18 17 -34 c16 12 26 28 26 44 c0 16 -6 26 -19 26z" fill="#ffd36b"/>"""),
    # Metka z ceną i monety
    "olx-vinted-odbierz-platnosc": ("#e0f4f4", f"""
    <path d="M40 60 h130 l110 110 a20 20 0 0 1 0 28 l-90 90 a20 20 0 0 1 -28 0 l-110 -110 v-110 a8 8 0 0 1 8 -8z" fill="#1d8a87"/>
    <circle cx="90" cy="110" r="18" fill="#e0f4f4"/>
    <circle cx="60" cy="250" r="40" fill="#f2b705"/><circle cx="60" cy="250" r="26" fill="none" stroke="#d99a00" stroke-width="6"/>
    <circle cx="130" cy="272" r="30" fill="#f2b705"/><circle cx="130" cy="272" r="18" fill="none" stroke="#d99a00" stroke-width="6"/>"""),
    # Dokument z pieczątką
    "falszywy-zwrot-podatku-mandat": ("#eef1f5", f"""
    <path d="M40 20 h150 l70 70 v200 a12 12 0 0 1 -12 12 h-208 a12 12 0 0 1 -12 -12 v-258 a12 12 0 0 1 12 -12z" fill="{WHITE}" stroke="{GREY}" stroke-width="4"/>
    <path d="M190 20 v58 a12 12 0 0 0 12 12 h58" fill="{GREY}"/>
    <g fill="{GREY}"><rect x="62" y="70" width="100" height="14" rx="7"/><rect x="62" y="110" width="170" height="14" rx="7"/>
    <rect x="62" y="140" width="150" height="14" rx="7"/><rect x="62" y="170" width="170" height="14" rx="7"/></g>
    <circle cx="190" cy="240" r="48" fill="none" stroke="{RED}" stroke-width="10"/>
    <circle cx="190" cy="240" r="26" fill="{RED}" opacity="0.85"/>"""),
}


def qr():
    # Prosty, deterministyczny wzór kodu QR (nie jest prawdziwym kodem do zeskanowania).
    cells = []
    size, n, x0, y0 = 16, 13, 40, 40
    pattern = 0x5A3C9E7
    for r in range(n):
        for c in range(n):
            finder = (r < 4 and c < 4) or (r < 4 and c > n - 5) or (r > n - 5 and c < 4)
            if finder:
                continue
            pattern = (pattern * 1103515245 + 12345) & 0x7FFFFFFF
            if pattern % 3 == 0:
                cells.append(f'<rect x="{x0 + c * size}" y="{y0 + r * size}" width="{size}" height="{size}"/>')
    finders = ""
    for fx, fy in [(x0, y0), (x0 + (n - 4) * size, y0), (x0, y0 + (n - 4) * size)]:
        finders += (f'<rect x="{fx}" y="{fy}" width="64" height="64" rx="8" fill="{INK}"/>'
                    f'<rect x="{fx + 10}" y="{fy + 10}" width="44" height="44" rx="4" fill="{WHITE}"/>'
                    f'<rect x="{fx + 20}" y="{fy + 20}" width="24" height="24" rx="2" fill="{INK}"/>')
    return f"""
    <rect x="20" y="20" width="248" height="248" rx="20" fill="{WHITE}" stroke="{GREY}" stroke-width="4"/>
    <g fill="{INK}">{''.join(cells)}</g>{finders}
    <g transform="rotate(-8 230 230)">
      <rect x="160" y="160" width="130" height="130" rx="14" fill="{WHITE}" stroke="{RED}" stroke-width="8" stroke-dasharray="18 10"/>
      <g fill="{RED}"><rect x="185" y="185" width="28" height="28"/><rect x="237" y="185" width="28" height="28"/>
      <rect x="185" y="237" width="28" height="28"/><rect x="225" y="225" width="16" height="16"/></g>
    </g>"""


GLYPHS["falszywe-kody-qr"] = ("#fdeceb", qr())

for slug, (bg, glyph) in GLYPHS.items():
    (OUT / f"{slug}.svg").write_text(frame(bg, glyph), encoding="utf-8", newline="\n")
print("OK", len(GLYPHS), "ilustracji")
