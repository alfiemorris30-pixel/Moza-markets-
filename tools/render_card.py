#!/usr/bin/env python3
"""MOZA Markets Instagram card renderer — locked design (Master System Section 50.19).

Usage:  python3 tools/render_card.py spec.json out.jpg
Prints the output path. Exits non-zero with a reason if the spec breaks a rule or the text
does not fit the card (shorten it and try again).

spec.json (verified facts only; never invent figures, quotes or positions):
{
  "context":  "bearish" | "bullish",          # RED or GREEN market-context colour
  "label":    "US MARKETS · FED",             # market / category label
  "headline": "Fed minutes point to [another hike]",   # [brackets] = words shown in the context colour
  "quote":    {"text": "...", "by": "Most Fed officials · FOMC minutes, Sept 2026"},  # verbatim, verified
  "stats":    [{"label": "Dow", "value": "-0.66%", "dir": "down"}],  # 0-4 tiles; dir up|down|flat
  "note":     "Optional one-line context.",
  "asof":     "At the close · Wednesday 7 October 2026",   # time context for every figure (Section 50.6)
  "trade":    {"catchline": "I'M INVESTED. FOLLOW THE JOURNEY.", "etoro_position_id": "..."}
              # ONLY for a position confirmed by live eToro data; catch-line is always green
}
Rules enforced here: no source/news-provider line on the card, no engagement numbers, no
verification badge, catch-line must be one of the three exact MOZA lines and needs a confirmed
eToro position id. Profile picture: assets/profile.jpg or assets/profile.png if present,
otherwise the MOZA monogram.
"""
import base64
import html
import json
import os
import re
import sys

from playwright.sync_api import sync_playwright

W, H = 1080, 1350
RED, GREEN = "#ef4444", "#22c55e"
CATCHLINES = (
    "I'M INVESTED. FOLLOW THE JOURNEY.",
    "MOZA IS INVESTED. ARE YOU FOLLOWING?",
    "THIS ISN'T JUST MARKET TALK. MOZA IS INVESTED.",
)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fail(msg):
    sys.exit("CARD ERROR: " + msg)


def norm_quotes(s):
    return (s or "").replace("’", "'").replace("‘", "'").strip()


def esc(s):
    return html.escape(s or "")


def headline_html(text):
    # [words] -> context-coloured emphasis
    parts = re.split(r"(\[[^\]]+\])", text.upper())
    out = []
    for p in parts:
        if p.startswith("[") and p.endswith("]"):
            out.append('<span class="hl">' + esc(p[1:-1]) + "</span>")
        else:
            out.append(esc(p))
    return "".join(out)


def avatar_html(size, ring):
    for name in ("profile.jpg", "profile.jpeg", "profile.png"):
        p = os.path.join(ROOT, "assets", name)
        if os.path.exists(p):
            mime = "image/png" if name.endswith("png") else "image/jpeg"
            data = base64.b64encode(open(p, "rb").read()).decode()
            return (f'<div class="av" style="width:{size}px;height:{size}px;border-color:{ring}">'
                    f'<img src="data:{mime};base64,{data}" alt=""></div>')
    return (f'<div class="av mono" style="width:{size}px;height:{size}px;border-color:{ring};'
            f'font-size:{int(size * 0.5)}px">M</div>')


def build(spec):
    ctx = spec.get("context")
    if ctx not in ("bearish", "bullish"):
        fail('"context" must be "bearish" or "bullish"')
    C = RED if ctx == "bearish" else GREEN
    arrow = "▼" if ctx == "bearish" else "▲"
    for key in ("label", "headline", "asof"):
        if not spec.get(key):
            fail(f'"{key}" is required')
    blob = json.dumps(spec).lower()
    if re.search(r"\bsource\s*:", blob):
        fail("no source line on the card (sources go in the caption)")
    if re.search(r"\b(likes?|followers?|views?|reposts?|retweets?)\b\s*[:=]", blob):
        fail("no engagement numbers on the card")

    quote = spec.get("quote") or {}
    quote_html = ""
    if quote.get("text"):
        by = f'<div class="qby">— {esc(quote.get("by", ""))}</div>' if quote.get("by") else ""
        quote_html = (f'<div class="quote"><div class="qm">&ldquo;</div>'
                      f'<div class="qt">{esc(quote["text"])}</div>{by}</div>')

    tiles = []
    for s in (spec.get("stats") or [])[:4]:
        d = s.get("dir", "flat")
        col = {"up": GREEN, "down": RED}.get(d, "#f2f3f4")
        a = {"up": "▲ ", "down": "▼ "}.get(d, "")
        tiles.append(f'<div class="tile"><div class="tl">{esc(s.get("label"))}</div>'
                     f'<div class="tv" style="color:{col}">{a}{esc(s.get("value"))}</div></div>')
    stats_html = f'<div class="tiles">{"".join(tiles)}</div>' if tiles else ""
    note_html = f'<p class="note">{esc(spec["note"])}</p>' if spec.get("note") else ""

    trade_html = ""
    trade = spec.get("trade")
    if trade:
        line = norm_quotes(trade.get("catchline")).upper()
        if line not in CATCHLINES:
            fail("catch-line must be one of the three exact MOZA catch-lines")
        if not str(trade.get("etoro_position_id") or "").strip():
            fail("a catch-line needs a position confirmed by live eToro data (etoro_position_id)")
        trade_html = (f'<div class="trade">{avatar_html(64, GREEN)}'
                      f'<div class="catch">{esc(line)}</div></div>')

    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
* {{ box-sizing:border-box; margin:0; padding:0; }}
html,body {{ width:{W}px; height:{H}px; background:#030303; }}
body {{ font-family:'Inter','Noto Color Emoji',sans-serif; color:#f2f3f4;
        display:flex; flex-direction:column; align-items:center; justify-content:center; }}
.card {{ width:960px; background:#0b0c0d; border:1.5px solid {C}55; border-radius:34px; padding:52px 58px 50px; }}
.head {{ display:flex; align-items:center; gap:22px; }}
.av {{ border-radius:50%; border:3px solid; overflow:hidden; flex:none; background:#000;
       display:flex; align-items:center; justify-content:center; }}
.av img {{ width:100%; height:100%; object-fit:cover; }}
.av.mono {{ color:#ff7a1a; font-family:'Inter Display','Inter'; font-weight:900; }}
.who {{ flex:1; }}
.who .n {{ font-weight:800; font-size:33px; letter-spacing:-0.3px; }}
.who .h {{ font-size:23px; color:#8a9199; margin-top:4px; }}
.dots {{ font-size:40px; color:#8a9199; letter-spacing:2px; line-height:1; margin-top:-18px; }}
.label {{ margin-top:44px; font-weight:800; font-size:25px; letter-spacing:3px; color:{C}; }}
h1 {{ margin-top:16px; font-family:'Inter Display','Inter',sans-serif; font-weight:900; font-size:80px;
      line-height:1.0; letter-spacing:-1px; word-spacing:10px; text-transform:uppercase; }}
h1 .hl {{ color:{C}; }}
.quote {{ position:relative; margin-top:38px; padding:30px 34px 28px 92px; border:1.5px solid {C}88;
          border-left:6px solid {C}; border-radius:18px; background:{C}12; }}
.qm {{ position:absolute; left:24px; top:2px; font-family:Georgia,serif; font-size:120px; line-height:1; color:{C}; }}
.qt {{ font-size:33px; line-height:1.32; font-weight:600; color:#f5f6f7; }}
.qby {{ margin-top:16px; font-size:20px; font-weight:700; letter-spacing:1.6px; color:#9aa1a8; text-transform:uppercase; }}
.tiles {{ margin-top:30px; display:flex; gap:14px; }}
.tile {{ flex:1; border:1.5px solid #26282b; border-radius:16px; padding:20px 10px 18px; text-align:center; background:#08090a; }}
.tl {{ font-size:20px; font-weight:700; letter-spacing:1.8px; color:#8a9199; text-transform:uppercase; }}
.tv {{ margin-top:8px; font-size:38px; font-weight:800; letter-spacing:-0.5px; }}
.note {{ margin-top:26px; font-size:27px; line-height:1.4; color:#c9cdd2; }}
.asof {{ margin-top:24px; font-size:20px; color:#7c838a; }}
.trade {{ margin-top:30px; padding-top:28px; border-top:1.5px solid #26282b; display:flex; align-items:center; gap:20px; }}
.catch {{ flex:1; color:{GREEN}; font-family:'Inter Display','Inter'; font-weight:900; font-size:34px;
          line-height:1.1; letter-spacing:0; word-spacing:9px; }}
.brand {{ margin-top:34px; font-size:18px; font-weight:700; letter-spacing:6px; color:#565c62; }}
.brand b {{ color:#ff7a1a; font-weight:700; }}
</style></head><body>
<div class="card">
  <div class="head">{avatar_html(88, "#ff7a1a")}
    <div class="who"><div class="n">MOZA Markets</div><div class="h">@mozamarkets · Global Market Intelligence</div></div>
    <div class="dots">···</div></div>
  <div class="label">{arrow} {esc(spec["label"].upper())}</div>
  <h1>{headline_html(spec["headline"])}</h1>
  {quote_html}
  {stats_html}
  {note_html}
  <div class="asof">{esc(spec["asof"])}</div>
  {trade_html}
</div>
<div class="brand"><b>●</b> MOZA MARKETS · GLOBAL MARKET INTELLIGENCE</div>
</body></html>"""


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    if not out.lower().endswith((".jpg", ".jpeg")):
        fail("output must be .jpg (Instagram accepts JPEG only)")
    page_html = build(spec)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        pg.set_content(page_html, wait_until="networkidle")
        too_tall = pg.evaluate(f"document.body.scrollHeight > {H} || "
                               f"document.querySelector('.card').getBoundingClientRect().top < 24")
        pg.screenshot(path=out, type="jpeg", quality=92, full_page=False)
        b.close()
    if too_tall:
        os.remove(out)
        fail("text does not fit the card — shorten the headline, quote or note")
    print(out)


if __name__ == "__main__":
    main()
