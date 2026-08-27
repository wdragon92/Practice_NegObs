#!/usr/bin/env python3
"""Batch driver for simple_edge: run label_frame over whole scenes and build
contact sheets of 24 tiles (4 rows x 6 cols).  Usage:
  simple_edge_batch.py --mask v2 --out _simple_batch ROUND:SCENE [ROUND:SCENE ...]
Every cut of each scene (all tiers, all indices) is labelled.

--mask picks the drop-mask definition and DEFAULTS TO v2 (the surfaces you would
land on).  v1 is the rejected "everything below 0.3 m" rule and is kept only so
the two can be regenerated side by side; --bridge applies to v1 alone, because
v2 uses no bridge constant at all.  Whichever ran is printed on every sheet
caption, so a sheet can never be mistaken for the other definition."""
import argparse, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import simple_edge as S
import e1_data as D
import e1_const as C

def cuts_of(round_name, scene_id):
    sdir = D.scene_dir(round_name, scene_id)
    out = []
    for c in D.list_cuts(sdir):
        f = c["file"]                       # e.g. L5__s20260819__0003.png
        parts = f[:-4].split("__")
        if len(parts) == 3:
            out.append((parts[0], parts[2]))
    return sorted(set(out))

def sheet(records, out_jpg, cols=6, rows=4, tile_w=480, note=""):
    from PIL import Image, ImageDraw
    fnt = S._font(22); small = S._font(16)
    lab_h = 30
    tiles = [(S.render_overlay(r["_rgb"], r, r["_drop"], tile_w=tile_w), r) for r in records]
    th = max(t.height for t, _ in tiles)
    img = Image.new("RGB", (cols * tile_w, rows * (th + lab_h) + 34), (18, 18, 18))
    dr = ImageDraw.Draw(img)
    for i, (t, rec) in enumerate(tiles):
        cx, cy = i % cols, i // cols
        x0, y0 = cx * tile_w, cy * (th + lab_h)
        m = rec["meta"]
        name = "%s %s/%s  [%s]  %s" % (m["scene"], rec["frame"].split("__")[2], rec["frame"].split("__")[-1],
                                       rec["tier_hint"], ("--" if rec["min_edge_dist_m"] is None else "%.1f m" % rec["min_edge_dist_m"]))
        dr.text((x0 + 6, y0 + 5), name, font=fnt, fill=(255, 255, 255))
        img.paste(t, (x0, y0 + lab_h))
    dr.text((8, rows * (th + lab_h) + 8), note, font=small, fill=(200, 200, 200))
    img.save(out_jpg, quality=82, optimize=True)
    return out_jpg

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scenes", nargs="+", help="ROUND:SCENE")
    ap.add_argument("--mask", choices=("v1", "v2"), default=None,
                    help="drop-mask definition; default %s" % C.MASK_VERSION_DEFAULT)
    ap.add_argument("--bridge", type=int, default=None,
                    help="EDGE_BRIDGE_PX override; mask v1 only")
    ap.add_argument("--out", default=None,
                    help="output subfolder; defaults to _simple_batch_<mask>")
    a = ap.parse_args()
    mv = S.MASK_CHOICES[a.mask or C.MASK_VERSION_DEFAULT]
    out = a.out or ("_simple_batch_%s" % ("v1" if mv == S.MASK_V1 else "v2"))
    ov = os.path.join(HERE, "..", "overlays", out); an = os.path.join(HERE, "..", "annotations", out)
    os.makedirs(ov, exist_ok=True); os.makedirs(an, exist_ok=True)
    from PIL import Image
    t0 = time.time(); n = 0; counts = {}; sheets = []
    for spec in a.scenes:
        rn, sc = spec.split(":")
        recs = []
        for tier, idx in cuts_of(rn, sc):
            try:
                rec, drop, kept, rgb = S.label_frame(rn, sc, tier, idx,
                                                     edge_bridge_px=a.bridge,
                                                     mask_version=mv)
            except Exception as e:
                print("[batch] SKIP %s %s %s %s: %s" % (rn, sc, tier, idx, e)); continue
            stem = rec["frame"]
            S.dump_json(rec, os.path.join(an, stem + ".simple_edge.json"))
            Image.fromarray((drop.astype(np.uint8) * 255)).save(os.path.join(ov, stem + ".dropmask.png"))
            rec["_rgb"], rec["_drop"] = rgb, drop
            recs.append(rec); n += 1; counts[rec["tier_hint"]] = counts.get(rec["tier_hint"], 0) + 1
            print("[batch] %-44s edge=%5.0f px mask=%8d px dist=%s %s" % (stem, rec["edge_len_px"], rec["mask_area_px"],
                  ("--" if rec["min_edge_dist_m"] is None else "%.2f" % rec["min_edge_dist_m"]), rec["tier_hint"]))
        for k in range(0, len(recs), 24):
            chunk = recs[k:k + 24]
            if not chunk: continue
            outp = os.path.join(ov, "sheet_%s_%s_%s_%02d.jpg" % (rn, sc, "v1" if mv == S.MASK_V1 else "v2", k // 24 + 1))
            sheet(chunk, outp, note="simple_edge  mask=%s  DROP_MIN_M=%.2f  R_RUN_M=%.1f  RAMP_MAX_SLOPE=1/12  LANDING_MIN_M=%.2f  RISER_MAX_M=%.2f%s  (same rule for every frame, no per-scene tuning)"
                  % (mv, C.DROP_MIN_M, C.R_RUN_M, C.LANDING_MIN_M, C.RISER_MAX_M,
                     ("  EDGE_BRIDGE_PX=%s" % (a.bridge if a.bridge is not None else C.EDGE_BRIDGE_PX))
                     if mv == S.MASK_V1 else ""))
            sheets.append(outp)
    print("[batch] %d frames in %.0f s (%.2f s/frame)  tiers=%s" % (n, time.time() - t0, (time.time() - t0) / max(n, 1), counts))
    for s in sheets: print("[batch] sheet", s, "%.2f MB" % (os.path.getsize(s) / 1e6))

if __name__ == "__main__":
    main()
