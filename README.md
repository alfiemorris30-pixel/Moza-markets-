# MOZA Markets — Instagram cards

Public image hosting for MOZA Markets Instagram posts (@mozamarkets), published through Buffer.
Pipeline: MOZA research → Social Engine → card JPEG → this repo → public link → Buffer → Instagram
(Master System Section 50.19).

- `cards/` — one JPEG per post (1080×1350, 4:5). Instagram's publishing API accepts JPEG only.
- `tools/render_card.py` — renders a card in the locked design from a JSON spec of verified facts.
- `tools/check_caption.py` — caption check (max 5 hashtags, length, banned hype wording).
- `assets/profile.jpg` — optional MOZA profile picture for the circular profile area
  (the MOZA monogram is used until it is added).

Image link format used by Buffer:
`https://raw.githubusercontent.com/alfiemorris30-pixel/Moza-markets-/main/cards/<file>.jpg`

Locked design: near-black background, X-style MOZA Markets post card (profile picture area, name,
@mozamarkets, Global Market Intelligence, three-dot menu), market label, large capitalised
headline, quote block, market-data tiles, time context. Market context colour is RED (bearish) or
GREEN (bullish); MOZA orange is branding only. The MOZA eToro catch-line appears only for a position
confirmed by live eToro data and is always GREEN. No source line, no engagement numbers, no
verification badge, no third-party photos or news imagery.

Market intelligence only, not investment advice.
