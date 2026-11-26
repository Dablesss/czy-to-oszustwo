# Obrazy do podglądu linku (Open Graph) 1200x630 PNG: static/img/og/<nazwa>.png
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from articles_content import ARTICLES  # noqa: E402
from render import render  # noqa: E402

R = Path(sys.argv[1])
S = Path(__file__).parent
ILL = R / "static" / "img" / "artykuly"
OG = R / "static" / "img" / "og"
OG.mkdir(parents=True, exist_ok=True)
LOGO = """<svg width="44" height="44" viewBox="0 0 32 32"><path d="M16 3 27 7v8.5c0 6.6-4.6 11.6-11 13.5C9.6 27.1 5 22.1 5 15.5V7Z" fill="#1f4fa3"/><path d="m11 16 3.5 3.5L21.5 12" fill="none" stroke="#fff" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/></svg>"""


def page(label, title, right):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
  body {{ margin:0; width:1200px; height:630px; font-family:"Segoe UI Variable Display","Segoe UI",Roboto,sans-serif;
         background:#ffffff; color:#16191d; display:flex; align-items:center; box-sizing:border-box; padding:0 56px; gap:48px; }}
  .txt {{ width:520px; display:flex; flex-direction:column; gap:22px; }}
  .label {{ display:inline-block; align-self:flex-start; padding:8px 18px; border-radius:999px; background:#edf2fb; color:#1f4fa3;
           font-size:26px; font-weight:600; }}
  h1 {{ margin:0; font-size:54px; line-height:1.08; letter-spacing:-0.03em; font-weight:800; }}
  .brand {{ display:flex; align-items:center; gap:14px; font-size:28px; font-weight:800; color:#16191d; margin-top:12px; }}
  .img img {{ width:540px; height:284px; border-radius:28px; border:2px solid #e3e7ec; display:block; }}
  .grid {{ display:grid; grid-template-columns:270px 270px; gap:10px; }}
  .grid img {{ width:270px; height:142px; border-radius:18px; border:2px solid #e3e7ec; display:block; }}
  </style></head><body>
  <div class="txt"><span class="label">{label}</span><h1>{title}</h1><div class="brand">{LOGO}Czy to oszustwo?</div></div>
  {right}
</body></html>"""


jobs = []


def add(name, label, title, right):
    src = S / f"og_{name}.html"
    src.write_text(page(label, title, right), encoding="utf-8")
    jobs.append((str(src), str(OG / f"{name}.png"), 1200, 630))


for a in ARTICLES:
    add(a["slug"], "Poradnik", a["h1"], f'<div class="img"><img src="{(ILL / (a["slug"] + ".svg")).as_uri()}"></div>')
four = ["sms-doplata-do-paczki", "oszustwo-na-blik-od-znajomego", "falszywy-pracownik-banku", "falszywe-kody-qr"]
grid = '<div class="grid">' + "".join(f'<img src="{(ILL / (x + ".svg")).as_uri()}">' for x in four) + "</div>"
add("poradniki", "8 poradników", "Jak rozpoznać oszustwo SMS i w internecie", grid)
add("strona-glowna", "Bezpłatnie, w kilka sekund", "Sprawdź podejrzany SMS albo link",
    f'<div class="img"><img src="{(ILL / "sms-doplata-do-paczki.svg").as_uri()}"></div>')
render(jobs)
