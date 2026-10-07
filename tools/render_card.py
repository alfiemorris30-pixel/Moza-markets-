#!/usr/bin/env python3
"""MOZA Markets Instagram card renderer (Section 50.19).

Usage: python3 render_card.py spec.json out.png

spec.json fields (text only, every fact must come from verified MOZA research):
  format_label  e.g. "🇺🇸 US MARKETS"           (format marker from Section 50.4)
  headline      e.g. "STOCKS SLIP FROM RECORD HIGHS" (rendered in capitals)
  subhead       one sentence, the key catalyst
  stats         optional list of {"label": "S&P 500", "value": "−0.59%", "dir": "down"|"up"|"flat"} (max 4)
  context       one or two short sentences of market context
  asof          time context, e.g. "As of ~10:00 ET · 7 Oct 2026"
  source        e.g. "Yahoo Finance · eToro"
Brand text card only: typography on black, no photos, no charts, no logos of other
organisations, no engagement counts, no verified badge.
"""
import html
import json
import sys

from playwright.sync_api import sync_playwright

W, H = 1080, 1350  # 4:5 portrait, Instagram feed


def esc(s):
    return html.escape(s or "")


def build_html(spec):
    stats = spec.get("stats") or []
    stat_html = ""
    if stats:
        cells = []
        for s in stats[:4]:
            cls = {"down": "down", "up": "up"}.get(s.get("dir"), "flat")
            cells.append(
                f'<div class="stat"><div class="sl">{esc(s.get("label"))}</div>'
                f'<div class="sv {cls}">{esc(s.get("value"))}</div></div>'
            )
        stat_html = f'<div class="stats">{"".join(cells)}</div>'
    context = f'<p class="ctx">{esc(spec.get("context"))}</p>' if spec.get("context") else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
:root {{ --bg:#000; --card:#0b0b0c; --line:#26282b; --text:#f2f3f4; --muted:#8a9199;
         --accent:#ff7a1a; --up:#22c55e; --down:#f04444; }}
* {{ box-sizing:border-box; margin:0; padding:0; }}
html,body {{ width:{W}px; height:{H}px; background:var(--bg); }}
body {{ font-family:'Inter','Noto Color Emoji',sans-serif; color:var(--text);
        display:flex; flex-direction:column; align-items:center; justify-content:center; }}
.card {{ width:930px; background:var(--card); border:1.5px solid var(--line); border-radius:34px;
         padding:58px 62px 52px; }}
.head {{ display:flex; align-items:center; gap:24px; }}
.av {{ width:92px; height:92px; border-radius:50%; flex:none; display:flex; align-items:center;
       justify-content:center; background:#000; border:3px solid var(--accent);
       font-family:'Inter Display','Inter'; font-weight:900; font-size:46px; color:var(--accent); }}
.who .n {{ font-weight:800; font-size:35px; letter-spacing:-0.3px; }}
.who .h {{ font-size:25px; color:var(--muted); margin-top:4px; }}
.fmt {{ margin-top:52px; font-weight:700; font-size:27px; letter-spacing:2.5px; color:var(--accent);
        font-family:'Inter','Noto Color Emoji'; }}
h1 {{ margin-top:20px; font-family:'Inter Display','Inter','Noto Color Emoji'; font-weight:900;
      font-size:78px; line-height:1.02; letter-spacing:-1px; word-spacing:8px; text-transform:uppercase; }}
.sub {{ margin-top:30px; font-size:36px; line-height:1.3; font-weight:500; color:#e3e5e8; }}
.stats {{ margin-top:42px; display:flex; border-top:1.5px solid var(--line); border-bottom:1.5px solid var(--line); }}
.stat {{ flex:1; padding:26px 0 24px; text-align:center; }}
.stat + .stat {{ border-left:1.5px solid var(--line); }}
.sl {{ font-size:22px; font-weight:600; letter-spacing:1.8px; color:var(--muted); text-transform:uppercase; }}
.sv {{ margin-top:8px; font-size:42px; font-weight:800; letter-spacing:-0.5px; }}
.sv.up {{ color:var(--up); }} .sv.down {{ color:var(--down); }} .sv.flat {{ color:var(--text); }}
.ctx {{ margin-top:36px; font-size:29px; line-height:1.42; color:#c9cdd2; }}
.foot {{ margin-top:40px; font-size:21px; color:var(--muted); line-height:1.5; }}
.brand {{ margin-top:46px; font-size:20px; font-weight:700; letter-spacing:6px; color:#5d636a; }}
</style></head><body>
<div class="card">
  <div class="head"><div class="av">M</div>
    <div class="who"><div class="n">MOZA Markets</div><div class="h">@mozamarkets · Global Market Intelligence</div></div></div>
  <div class="fmt">{esc(spec.get("format_label"))}</div>
  <h1>{esc(spec.get("headline"))}</h1>
  <p class="sub">{esc(spec.get("subhead"))}</p>
  {stat_html}
  {context}
  <div class="foot">{esc(spec.get("asof"))}<br>Source: {esc(spec.get("source"))}</div>
</div>
<div class="brand">MOZA MARKETS · GLOBAL MARKET INTELLIGENCE</div>
</body></html>"""


def main():
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        pg.set_content(build_html(spec), wait_until="networkidle")
        overflow = pg.evaluate("document.documentElement.scrollHeight > %d" % H)
        if out.lower().endswith((".jpg", ".jpeg")):
            # Instagram's publishing API accepts JPEG only.
            pg.screenshot(path=out, type="jpeg", quality=92, full_page=False)
        else:
            pg.screenshot(path=out, type="png", full_page=False)
        b.close()
    if overflow:
        print("WARNING: content taller than the canvas — shorten the text", file=sys.stderr)
        sys.exit(2)
    print(out)


if __name__ == "__main__":
    main()
