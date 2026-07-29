#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sky HDRI photometry — measures the constants the condition catalogue needs.

Why this exists
  `variation_kit.CONDITIONS` does not hardcode dome/sun intensities. It computes
  them from the spec's physical model

      E_phys(h, cloud) = 128000 * sin(h)^1.15 * cloud                 [lux]
      sun_intensity(c) = 2450 / f_dir_ref * E_rel(c) * f_dir(c)
      dome_intensity(c)= 1000 * E_rel(c) * (1-f_dir(c))/(1-f_dir_ref)
                              * Esky_ref / Esky(c)

  (`Docs/briefs/lighting_camera_variation_spec_v1.md` §4.3), and that model needs
  three **measured** per-sky numbers: the sun elevation, the direct fraction
  `f_dir`, and the sky-only horizontal irradiance `Esky`. The spec published
  elevation and `f_dir` for 15 skies but `Esky` for the reference sky only, so the
  three skies procured for L3/L4/L5 have no published `Esky` at all and their dome
  intensity is not derivable from the document. This tool measures all of them.

Method — spec §4.2, reproduced
  1. Solid-angle-weighted centroid of the top 0.01 % luminance pixels -> sun
     direction (robust where a plain argmax is not: a single hot pixel in a hazy
     sky moves argmax by tens of degrees, which is exactly how the spec's table
     got its "(오검출)" entries).
  2. p90 luminance of the ring at angular radius [cap, cap+0.4] deg -> `cap`.
  3. Direct component = pixels inside `cap` whose luminance exceeds `cap`;
     everything else is sky.
  4. Horizontal irradiance = cos-weighted upper-hemisphere integral,
     dw = sin(theta) * (pi/h) * (2pi/w), weight cos(theta), theta from zenith.
  5. Sun gate (`Docs/reports/sky_procurement_v1.md` §3.2):
     `peak/cap >= 50` AND `E(<2.5 deg) / E_total >= 5 %`. SOFT skies must be used
     with `lookfix=False` and a sunless / soft-direct profile (spec §4.6).

GPU 0. Writes `assets/sky_photometry.json` (tracked - it is the provenance for
the catalogue's numbers; the EXRs themselves are gitignored).

usage:
    python3 scripts/measure_sky.py                 # every sky the catalogue uses
    python3 scripts/measure_sky.py <file.exr> ...  # named files
    python3 scripts/measure_sky.py --check         # re-measure + diff vs stored
"""
from __future__ import annotations

import json
import math
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(REPO, "assets")
OUT = os.path.join(ASSETS, "sky_photometry.json")

# The skies the 8-condition catalogue actually binds (spec §4.3).
CATALOGUE_SKIES = [
    "qwantani_noon_puresky_4k.exr",                     # L0 ref
    "kloofendal_48d_partly_cloudy_puresky_4k.exr",      # L1 cumulus
    "sunflowers_puresky_4k.exr",                        # L2 stratocumulus
    "kloofendal_38d_partly_cloudy_puresky_4k.exr",      # L3 autumn_noon
    "kloofendal_28d_misty_puresky_4k.exr",              # L4 winter_noon
    "qwantani_late_afternoon_puresky_4k.exr",           # L5 low_sun
    "farm_field_puresky_4k.exr",                        # L6 overcast_bright
    "kloofendal_overcast_4k.exr",                       # L7 overcast
]

CAP_DEG = 0.6            # = scene_common._SUN_CAP_DEG_DEFAULT (W2)
RING_W = 0.4             # ring is [CAP_DEG, CAP_DEG + RING_W]
TOP_FRAC = 1e-4          # top 0.01 % luminance for the centroid
GATE_PEAK_RATIO = 50.0
GATE_SUN_E_PCT = 5.0
GATE_SUN_DEG = 2.5

# Spec §4.2 published values, for cross-checking this tool against the design
# session's independent measurement. Key -> (elev, f_dir); `None` = the spec
# reported a misdetection and the value is not comparable.
SPEC_TABLE = {
    "qwantani_noon_puresky_4k.exr": (49.83, 0.912),
    "kloofendal_48d_partly_cloudy_puresky_4k.exr": (47.87, 0.659),
    "sunflowers_puresky_4k.exr": (43.01, 0.662),
    "kloofendal_38d_partly_cloudy_puresky_4k.exr": (37.96, 0.438),
    "kloofendal_28d_misty_puresky_4k.exr": (28.50, 0.049),
    "qwantani_late_afternoon_puresky_4k.exr": (19.07, 0.645),
    "farm_field_puresky_4k.exr": (None, 0.000),
    "kloofendal_overcast_4k.exr": (None, 0.000),
}


def measure(path):
    os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")
    import cv2
    import numpy as np

    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise IOError(f"cv2 could not read {path}")
    # BGR(A) -> RGB. The [..., :3] slice first is load-bearing: most PolyHaven
    # puresky EXRs are 4-channel and `[..., ::-1]` on RGBA yields [A,R,G,B]
    # (the same bug `scene_common.ensure_noon_lookfix` was patched for in W2).
    rgb = img[..., :3][..., ::-1].astype(np.float64)
    lum = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
    h, w = lum.shape

    v = (np.arange(h) + 0.5) / h
    theta = math.pi * v                       # 0 = zenith, pi = nadir
    phi = 2.0 * math.pi * (np.arange(w) + 0.5) / w
    st, ct = np.sin(theta)[:, None], np.cos(theta)[:, None]
    dx = st * np.cos(phi)[None, :]
    dy = st * np.sin(phi)[None, :]
    dz = np.broadcast_to(ct, (h, w))

    dw = st * (math.pi / h) * (2.0 * math.pi / w)      # solid angle per pixel
    upper = dz > 0.0
    wcos = np.where(upper, dw * dz, 0.0)              # cos-weighted, upper hemi
    E_tot = float((lum * wcos).sum())

    # --- 1. sun direction: solid-angle-weighted centroid of the top 0.01 % ---
    k = max(1, int(round(TOP_FRAC * lum.size)))
    thr = np.partition(lum.ravel(), -k)[-k]
    hot = (lum >= thr) & upper
    wt = (lum * dw) * hot
    tw = float(wt.sum())
    if tw <= 0.0:
        raise RuntimeError("no upper-hemisphere energy")
    sx = float((dx * wt).sum() / tw)
    sy = float((dy * wt).sum() / tw)
    sz = float((dz * wt).sum() / tw)
    n = math.sqrt(sx * sx + sy * sy + sz * sz)
    sx, sy, sz = sx / n, sy / n, sz / n
    elev = math.degrees(math.asin(max(-1.0, min(1.0, sz))))
    phi_sun = math.degrees(math.atan2(sy, sx)) % 360.0
    rotz = (90.0 - phi_sun) % 360.0

    # --- 2. ring p90 -> cap -------------------------------------------------
    cosang = np.clip(dx * sx + dy * sy + dz * sz, -1.0, 1.0)
    ang = np.degrees(np.arccos(cosang))
    ring = (ang > CAP_DEG) & (ang < CAP_DEG + RING_W)
    cap = float(np.percentile(lum[ring], 90)) if ring.any() else float("nan")
    peak = float(lum[upper].max())

    # --- 3/4. direct vs sky split ------------------------------------------
    disc = (ang < CAP_DEG) & (lum > cap) & upper
    E_dir = float((lum * wcos * disc).sum())
    E_sky = E_tot - E_dir
    f_dir = E_dir / E_tot if E_tot > 0 else 0.0
    sun_e_pct = 100.0 * float((lum * wcos * ((ang < GATE_SUN_DEG) & upper)).sum()
                              ) / E_tot if E_tot > 0 else 0.0

    gate = (peak / cap >= GATE_PEAK_RATIO if cap > 0 else False) \
        and sun_e_pct >= GATE_SUN_E_PCT
    return dict(
        file=os.path.basename(path), w=int(w), h=int(h),
        channels=int(img.shape[2]) if img.ndim == 3 else 1,
        sun_elev=round(elev, 2), sun_phi=round(phi_sun, 2),
        hdri_sun_rotz_offset=round(rotz, 2),
        peak=round(peak, 3), cap=round(cap, 4),
        peak_over_cap=round(peak / cap, 1) if cap > 0 else None,
        E_total=round(E_tot, 4), E_dir=round(E_dir, 4), Esky=round(E_sky, 4),
        f_dir=round(f_dir, 4), sun_E_pct=round(sun_e_pct, 2),
        gate="PASS" if gate else "SOFT",
        cap_deg=CAP_DEG,
    )


def main(argv):
    check = "--check" in argv
    names = [a for a in argv if not a.startswith("--")]
    files = names or [os.path.join(ASSETS, n) for n in CATALOGUE_SKIES]

    stored = {}
    if os.path.isfile(OUT):
        try:
            stored = {r["file"]: r for r in json.load(open(OUT))["skies"]}
        except Exception:
            stored = {}

    rows, missing = [], []
    for p in files:
        if not os.path.isfile(p):
            missing.append(os.path.basename(p))
            print(f"  MISS {os.path.basename(p)}")
            continue
        r = measure(p)
        rows.append(r)
        sp = SPEC_TABLE.get(r["file"])
        note = ""
        if sp:
            de = ("     " if sp[0] is None
                  else f"dElev {r['sun_elev'] - sp[0]:+.2f}")
            note = f"  [spec {de}  df_dir {r['f_dir'] - sp[1]:+.4f}]"
        print(f"  {r['file']:48s} elev {r['sun_elev']:6.2f}  phi {r['sun_phi']:6.2f}"
              f"  rotz {r['hdri_sun_rotz_offset']:6.2f}  f_dir {r['f_dir']:.4f}"
              f"  Esky {r['Esky']:8.4f}  {r['gate']}{note}")
        if check and r["file"] in stored:
            old = stored[r["file"]]
            for k in ("sun_elev", "f_dir", "Esky", "hdri_sun_rotz_offset"):
                if abs(float(r[k]) - float(old[k])) > 1e-3:
                    print(f"    ! {k}: stored {old[k]} -> measured {r[k]}")

    if check:
        print(f"\n[check] {len(rows)} skies re-measured, nothing written.")
        return 1 if missing else 0

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(dict(
            method=("solid-angle-weighted centroid of top 0.01% luminance; "
                    f"cap = p90 of ring [{CAP_DEG}, {CAP_DEG + RING_W}] deg; "
                    "E = cos-weighted upper-hemisphere integral "
                    "(spec lighting_camera_variation_spec_v1.md §4.2)"),
            cap_deg=CAP_DEG, skies=rows, missing=missing), f,
            ensure_ascii=False, indent=1)
    print(f"\n-> {OUT}  ({len(rows)} skies, {len(missing)} missing)")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
