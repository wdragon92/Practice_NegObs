#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""W3 S01 — report crops: the new round against **G1**, and pre/post against itself.

Each sheet answers exactly one question, because a whole frame makes the eye go to the
largest contrast and miss the thing that was asked about (the `crops_260730_w2d.py`
doctrine, reused).

  1  h0.3 d2 / d5 / d10, bottom 2/3, beside the same band of G1
       -> does the judged near band read like the target image
  2  lower_lookback pre vs post
       -> the environment question: is the horizon open, is there sky over the roofline
  3  beauty_overview pre vs post
       -> the flank question: kerbed lawn + bench line + tree row vs a boxed brick corridor
  4  kerb macro from beauty_overview
       -> does the 1 m joint rhythm survive, is the face a face and not paint

Output: `Docs/reports/_w3_s01_crops/` (the `_w3_s16_crops` precedent — report crops live
beside the report, never in the scene round directory).

usage: python3 scripts/rounds/crops_260731_w3_s01.py
GPU 0 · PIL only.
"""
from __future__ import annotations

import os

from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LC = os.path.join(REPO, "look_check", "scene01")
OUT = os.path.join(REPO, "Docs", "reports", "_w3_s01_crops")
G1 = os.path.join(REPO, "Docs", "reference_photos", "Generated Image - Scene01.jpg")
POST, PRE = "260731_w3_s01", "260731_w3_s01_pre"
FONT_P = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"


def _font(sz):
    try:
        return ImageFont.truetype(FONT_P, sz)
    except Exception:
        return ImageFont.load_default()


def _label(img, text, sz=26):
    d = ImageDraw.Draw(img)
    pad = 8
    f = _font(sz)
    tw = d.textlength(text, font=f)
    d.rectangle([0, 0, tw + 2 * pad, sz + 2 * pad], fill=(0, 0, 0))
    d.text((pad, pad), text, fill=(255, 255, 255), font=f)
    return img


def _band(path, y0=0.34, y1=1.0):
    """Bottom band of a frame — GATE-3's protocol crops the sky out before comparing."""
    im = Image.open(path).convert("RGB")
    w, h = im.size
    return im.crop((0, int(h * y0), w, int(h * y1)))


def _stack(imgs, labels, w=1400):
    scaled = []
    for im, lb in zip(imgs, labels):
        r = w / im.width
        s = im.resize((w, max(1, int(im.height * r))), Image.LANCZOS)
        scaled.append(_label(s, lb))
    H = sum(s.height for s in scaled) + 6 * (len(scaled) - 1)
    out = Image.new("RGB", (w, H), (24, 24, 24))
    y = 0
    for s in scaled:
        out.paste(s, (0, y))
        y += s.height + 6
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    made = []

    # --- 1. h0.3 judged band vs G1 ------------------------------------------
    g1 = _band(G1, 0.40, 1.0)
    for d in ("d2", "d5", "d10"):
        p = os.path.join(LC, POST, f"pt_noon_preset_h0.3_{d}.png")
        if not os.path.isfile(p):
            continue
        sheet = _stack([_band(p), g1],
                       [f"scene01 · {POST} · pt_noon_preset_h0.3_{d} (bottom 2/3)",
                        "G1 target · Generated Image - Scene01.jpg (bottom 3/5)"])
        fp = os.path.join(OUT, f"s01_h0.3_{d}_vs_G1.png")
        sheet.save(fp)
        made.append(fp)

    # --- 2 / 3. pre vs post on the two cuts that answer the directive -------
    for view, tag in (("lower_lookback", "environment"),
                      ("beauty_overview", "flanks")):
        a = os.path.join(LC, PRE, f"pt_noon_{view}.png")
        b = os.path.join(LC, POST, f"pt_noon_{view}.png")
        if not (os.path.isfile(a) and os.path.isfile(b)):
            continue
        sheet = _stack([Image.open(a).convert("RGB"), Image.open(b).convert("RGB")],
                       [f"BEFORE · {PRE} · {view}  ({tag})",
                        f"AFTER · {POST} · {view}  ({tag})"])
        fp = os.path.join(OUT, f"s01_{tag}_{view}_before_after.png")
        sheet.save(fp)
        made.append(fp)

    # --- 4. kerb macro ------------------------------------------------------
    b = os.path.join(LC, POST, "pt_noon_beauty_overview.png")
    if os.path.isfile(b):
        im = Image.open(b).convert("RGB")
        w, h = im.size
        crop = im.crop((int(w * 0.30), int(h * 0.18), int(w * 0.90), int(h * 0.52)))
        crop = crop.resize((crop.width * 2, crop.height * 2), Image.LANCZOS)
        fp = os.path.join(OUT, "s01_lawn_kerb_macro.png")
        _label(crop, "lawn kerb · 1 m unit blocks + 6 mm joints · top flush with the walk").save(fp)
        made.append(fp)

    for f in made:
        print(os.path.relpath(f, REPO))
    print(f"[crops] {len(made)} sheets -> {os.path.relpath(OUT, REPO)}")


if __name__ == "__main__":
    main()
