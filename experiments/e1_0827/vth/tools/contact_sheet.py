#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""contact_sheet.py -- W1_samples.jpg: one hole, 8 standoffs, RGB only, labelled."""
from __future__ import annotations

import argparse
import json
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--world", default="eworld2")
    ap.add_argument("--hole", default="H00")
    ap.add_argument("--height", default="06")
    ap.add_argument("--pitch", default="pm15")
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--tile-w", type=int, default=640)
    ap.add_argument("--out", default=os.path.join(HERE, "W1_samples.jpg"))
    a = ap.parse_args()

    man = json.load(open(os.path.join(HERE, "capture_manifest.json")))
    sel = [f for f in man["frames"]
           if f["world"] == a.world and f["hole_id"] == a.hole
           and f["pose_id"].endswith(f"_h{a.height}_{a.pitch}")]
    sel.sort(key=lambda f: f["standoff_m"])
    if len(sel) > 8:
        step = len(sel) / 8.0
        sel = [sel[int(i * step)] for i in range(8)]
    if not sel:
        raise SystemExit("[fatal] no frames matched")

    tw = a.tile_w
    th = int(round(tw * 720 / 1280))
    band = 46
    cols = a.cols
    rows = (len(sel) + cols - 1) // cols
    W = cols * tw
    H = rows * (th + band) + 52
    sheet = Image.new("RGB", (W, H), (18, 18, 20))
    dr = ImageDraw.Draw(sheet)
    f_big = ImageFont.truetype(FONT, 25)
    f_lab = ImageFont.truetype(FONT, 19)

    hole = next(h for h in json.load(open(os.path.join(HERE, "holes.json")))
                ["holes"] if h["hole_id"] == a.hole)
    dr.text((14, 12),
            f"W1 sanity — {a.world} · {a.hole} ({hole['w_m']:.2f}×{hole['h_m']:.2f} m, "
            f"{hole['area_m2']:.3f} m²) · height {int(a.height)/10:.1f} m · "
            f"pitch {sel[0]['pitch_deg']:+.0f}° · RGB only "
            f"— interior visible up close, edge-only far away",
            font=f_big, fill=(235, 235, 235))

    for i, fr in enumerate(sel):
        im = Image.open(os.path.join(HERE, fr["rgb"])).convert("RGB").resize(
            (tw, th), Image.BILINEAR)
        cx = (i % cols) * tw
        cy = 52 + (i // cols) * (th + band)
        sheet.paste(im, (cx, cy))
        dr.rectangle([cx, cy + th, cx + tw - 1, cy + th + band - 1], fill=(30, 30, 34))
        dr.text((cx + 10, cy + th + 12),
                f"standoff {fr['standoff_m']:.1f} m   ·   cam→hole "
                f"{fr['dist_cam_to_hole_centre_m']:.2f} m   ·   RGB mean {fr['rgb_mean']:.0f}",
                font=f_lab, fill=(228, 228, 228))
        dr.rectangle([cx, cy, cx + tw - 1, cy + th + band - 1], outline=(70, 70, 76))
    sheet.save(a.out, quality=88)
    print(f"-> {a.out}  ({sheet.size[0]}x{sheet.size[1]}, "
          f"{os.path.getsize(a.out)/1024:.0f} kB, {len(sel)} tiles)")


if __name__ == "__main__":
    main()
