#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""W3 L20 — report crops: scene20's pilot round against **G1**, and pre/post.

Each sheet answers one question, because a whole frame sends the eye to the largest
contrast and it misses the thing that was asked (`crops_260730_w2d.py` doctrine).

  1  h0.3 d2 / d5 / d10, bottom 2/3, beside the same band of G1
       -> does the judged near band read like the target image
  2  walk_axis_front + oblique_overview pre vs post
       -> the environment question: is there sky above the roofline now
  3  the three GRAZE edge bands, pre vs post, at the rows the detector named
       -> the adjudication the regression report says it cannot make automatically
  4  bollard + planter macro from oblique_overview, pre vs post
       -> C6 dome/plate/band read, and the bed off the judged eye

Output: `Docs/reports/_w3_l20_crops/` (the `_w3_s01_crops` precedent — report crops
live beside the report, never in the scene round directory).

usage: python3 scripts/rounds/crops_260731_w3_l20.py
GPU 0 · PIL only.
"""
from __future__ import annotations

import os

from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LC = os.path.join(REPO, "look_check", "scene20")
OUT = os.path.join(REPO, "Docs", "reports", "_w3_l20_crops")
G1 = os.path.join(REPO, "Docs", "reference_photos", "Generated Image - Scene01.jpg")
POST, PRE = "260731_w3_l20c", "260730_w2d_fix"
FONT_P = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"

# (cut, edge-band y0, y1, drop-row y) exactly as regression_check reported them
GRAZE = [("preset_h0.3_d2", 170, 312, 249),
         ("preset_h0.3_d5", 131, 212, 174),
         ("low_grazing", 237, 297, 270)]


def _font(sz):
    try:
        return ImageFont.truetype(FONT_P, sz)
    except Exception:
        return ImageFont.load_default()


def _open(round_id, cut):
    p = os.path.join(LC, round_id, f"pt_noon_{cut}.png")
    if not os.path.isfile(p):
        p = os.path.join(LC, round_id, f"pt_{cut}.png")
    return Image.open(p).convert("RGB")


def _label(img, text, sz=22):
    d = ImageDraw.Draw(img)
    f = _font(sz)
    d.rectangle([0, 0, img.width, sz + 12], fill=(0, 0, 0))
    d.text((8, 5), text, fill=(255, 255, 255), font=f)
    return img


def _sheet(path, tiles, cols=1, gap=8):
    if not tiles:
        return
    w = max(t.width for t in tiles)
    rows = (len(tiles) + cols - 1) // cols
    hs = []
    for r in range(rows):
        hs.append(max(t.height for t in tiles[r * cols:(r + 1) * cols]))
    W = cols * w + (cols + 1) * gap
    H = sum(hs) + (rows + 1) * gap
    sheet = Image.new("RGB", (W, H), (24, 24, 24))
    y = gap
    for r in range(rows):
        x = gap
        for t in tiles[r * cols:(r + 1) * cols]:
            sheet.paste(t, (x, y))
            x += w + gap
        y += hs[r] + gap
    sheet.save(path)
    print("  wrote", os.path.relpath(path, REPO))


def main():
    os.makedirs(OUT, exist_ok=True)

    # 1 — judged near band vs G1 -------------------------------------------
    tiles = []
    for cut in ("preset_h0.3_d2", "preset_h0.3_d5", "preset_h0.3_d10"):
        im = _open(POST, cut)
        im = im.crop((0, im.height // 3, im.width, im.height))
        tiles.append(_label(im, f"scene20 {POST}  {cut}  (bottom 2/3)"))
    g = Image.open(G1).convert("RGB")
    g = g.crop((0, g.height // 3, g.width, g.height))
    g = g.resize((tiles[0].width, int(g.height * tiles[0].width / g.width)))
    tiles.append(_label(g, "G1 target — granite plaza, low risers, open sky"))
    _sheet(os.path.join(OUT, "1_near_band_vs_G1.png"), tiles)

    # 2 — the horizon, pre vs post -----------------------------------------
    tiles = []
    for cut in ("walk_axis_front", "oblique_overview", "preset_h1.8_d10"):
        for rid, tag in ((PRE, "PRE  (260730_w2d_fix)"), (POST, "POST (260731_w3_l20)")):
            im = _open(rid, cut)
            tiles.append(_label(im.crop((0, 0, im.width, im.height // 2)),
                                f"{cut} — {tag}  [upper half]"))
    _sheet(os.path.join(OUT, "2_horizon_pre_post.png"), tiles, cols=2)

    # 3 — the GRAZE edge bands, at the detector's own rows ------------------
    tiles = []
    for cut, y0, y1, ydrop in GRAZE:
        for rid, tag in ((PRE, "PRE"), (POST, "POST")):
            im = _open(rid, cut)
            sy = im.height / 540.0            # detector works at 540 rows
            b = im.crop((0, int(y0 * sy), im.width, int(y1 * sy)))
            d = ImageDraw.Draw(b)
            yr = int(ydrop * sy) - int(y0 * sy)
            d.line([(0, yr), (b.width, yr)], fill=(255, 64, 64), width=2)
            tiles.append(_label(
                b, f"{cut} {tag} — edge band y{y0}..{y1}/540, drop row y{ydrop} (red)"))
    _sheet(os.path.join(OUT, "3_graze_bands.png"), tiles, cols=2)

    # 4 — bollard + bed macro ----------------------------------------------
    tiles = []
    for rid, tag in ((PRE, "PRE"), (POST, "POST")):
        im = _open(rid, "oblique_overview")
        w, h = im.width, im.height
        tiles.append(_label(im.crop((0, int(h * 0.35), int(w * 0.45), h)),
                            f"oblique_overview {tag} — west flank (bed + bollard row)"))
    _sheet(os.path.join(OUT, "4_bed_bollard_macro.png"), tiles, cols=2)


if __name__ == "__main__":
    main()
