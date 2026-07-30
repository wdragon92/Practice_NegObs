#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Procure the coastal (beach) textures scene18 needs. **CC0 1.0 only.**

Why this file exists
────────────────────
`scene18` was swapped from a hillside mural stair to a Haeundae/Gwangalli beach
promenade (`Docs/surveys/w3_intake_v2_images.md` §2 scene18 + §7 ruling 3). The
sand field is the second-largest surface in the target image `G18` and the
library had **no sand role at all** — the closest existing roles are `gravel`
(pebbles) and `sandstone` (a cut building stone), neither of which reads as
beach sand. `scene_common.TEX` belongs to another lane this window, so the role
is NOT registered there: `scene18` builds the material from these absolute
paths itself.

Licence
───────
ambientCG publishes every asset under **CC0 1.0** (public domain dedication),
which is inside the project's redistribution tier T1 — the same tier as the
Poly Haven material already sitting in `assets/urban_cc0/`. No attribution is
required; `Docs/CREDITS.md` records it anyway.

What is fetched
───────────────
`Ground080` — "beach / brown / ground / sand / yellow", PBRPhotogrammetry.
  [measured, this download] 2048x2048 · sRGB mean (0.726, 0.618, 0.446) ·
  linear albedo **0.3235** · pixels above 0.8 = **0.02 %** (so the §4
  "no large areas of pure white" rule is satisfied with margin).
  Real dry quartz beach sand sits at 0.25-0.40 albedo, so the map is
  physically in band and needs no tint to be legal.

  **Tile size is NOT published** — the ambientCG v2 API returns
  `dimensionX = dimensionY = 0` for this asset, and the page carries no
  physical-size line. `scale_m` is therefore an `[estimate]` derived from
  feature size, not a measurement: the backwash ripple wavelength in the map is
  0.02-0.05 of the tile, and real backwash ripples on a Korean sand beach are
  20-80 mm, so a **1.0 m** tile puts them at 20-50 mm. scene18 states the same
  derivation at its binding site.

  Rejected alternative, recorded so the choice is auditable:
  `Ground055S` **does** publish a measured 150 x 150 mm tile (the repo's
  preferred basis, cf. the Grass001 note in `scene_common.TEX`), but it
  measures sRGB (0.620, 0.591, 0.503) — a grey-beige with B/R = 0.81 against
  Ground080's 0.61. G18's sand is golden, and colour was judged the harder
  property to fake than tile size: a wrong tile is a scale error inside one
  order of magnitude, a wrong hue is the identity of the surface.

usage:
    python3 assets/coastal/download_coastal_assets.py
    python3 assets/coastal/download_coastal_assets.py --verify
Re-runnable: an existing file of non-zero size is skipped.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import os
import sys
import urllib.request
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "curl/8.5.0"}          # ambientCG 403s the urllib default
TIMEOUT = 240

# canonical name -> (ambientCG asset id, {suffix in zip: local file name})
ASSETS = {
    "beach_sand": ("Ground080", {
        "_Color.jpg":     "beach_sand_diff.jpg",
        "_NormalDX.jpg":  "beach_sand_nor_dx.jpg",
        "_Roughness.jpg": "beach_sand_rough.jpg",
    }),
}
LICENCE = "CC0 1.0 (ambientCG)"


def fetch_zip(asset_id: str) -> bytes:
    url = f"https://ambientcg.com/get?file={asset_id}_2K-JPG.zip"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true",
                    help="only report what is on disk, download nothing")
    args = ap.parse_args()

    rc = 0
    for name, (asset_id, members) in ASSETS.items():
        want = [os.path.join(HERE, v) for v in members.values()]
        have = [p for p in want if os.path.isfile(p) and os.path.getsize(p) > 0]
        if args.verify or len(have) == len(want):
            for p in want:
                ok = p in have
                if not ok:
                    rc = 1
                sz = os.path.getsize(p) if ok else 0
                md5 = ""
                if ok:
                    with open(p, "rb") as f:
                        md5 = hashlib.md5(f.read()).hexdigest()[:12]
                print(f"  [{'OK  ' if ok else 'MISS'}] {os.path.basename(p)} "
                      f"{sz:>9} B  md5:{md5}")
            if len(have) == len(want) and not args.verify:
                print(f"[skip] {name} ({asset_id}) — 이미 있음")
            continue
        print(f"[get ] {name} <- ambientCG {asset_id} ({LICENCE})")
        blob = fetch_zip(asset_id)
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            names = z.namelist()
            for suffix, dest in members.items():
                hit = [n for n in names if n.endswith(suffix)]
                if not hit:
                    print(f"  [FAIL] {suffix} 가 zip 안에 없다: {names}")
                    rc = 1
                    continue
                data = z.read(hit[0])
                with open(os.path.join(HERE, dest), "wb") as f:
                    f.write(data)
                print(f"  [save] {dest} {len(data)} B")
    return rc


if __name__ == "__main__":
    sys.exit(main())
