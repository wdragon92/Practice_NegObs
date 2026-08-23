#!/usr/bin/env python3
"""G7 repair, step 2b — the per-arm instrument audit README_LABELING.md demands
before a fused map is adopted.

For each affected (round, scene) it prints
  (a) median |fused - aabb| per arm over the cells BOTH instruments fill,
  (b) the raw twin-diff footprint (cells with z_off - z_on >= hazard_depth_m)
      under all four pairings, so a mixed pairing that manufactures phantom
      cells is visible before it is adopted,
  (c) coverage of each instrument.
The main round's adopted pairing (fuse_heightmap.py docstring) is printed beside
it, because the AABB map is camera-independent: it is byte-identical between the
main round and the boost rounds, so the main round's reason for fusing carries
over unchanged and only the FUSED map has to be re-measured per round.
"""
import json, os, sys
import numpy as np

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
DS = os.path.join(REPO, "dataset")
HZ = 0.3
MAIN_RULE = {"scene02": "fused/fused", "scene07": "fused/fused",
             "scene08": "aabb ON / fused OFF", "scene12": "fused/fused",
             "scene16": "fused/fused"}


def sdir(round_name, scene):
    for split in sorted(os.listdir(os.path.join(DS, round_name))):
        d = os.path.join(DS, round_name, split, scene)
        if os.path.isfile(os.path.join(d, "variation.json")):
            return d
    return None


def load(d, base):
    p = os.path.join(d, base + ".npy")
    return np.load(p).astype(np.float64) if os.path.isfile(p) else None


def fp_cells(on, off):
    if on is None or off is None:
        return None
    void = ~np.isfinite(on) | ~np.isfinite(off)
    diff = np.where(void, np.nan, off - on)
    return int(((~void) & (diff >= HZ)).sum())


def run(band, scenes):
    ron, roff = f"260820_boost_{band}_on_g7fix", f"260820_boost_{band}_off_g7fix"
    mon, moff = "260819_main_on", "260819_main_off"
    print(f"\n=== boost_{band} ===")
    for sc in scenes:
        do, df = sdir(ron, sc), sdir(roff, sc)
        a_on, a_off = load(do, "heightmap"), load(df, "heightmap")
        f_on, f_off = load(do, "heightmap_fused"), load(df, "heightmap_fused")
        # AABB identity check against the main round (camera-independent instrument)
        m_on, m_off = load(sdir(mon, sc), "heightmap"), load(sdir(moff, sc), "heightmap")
        ident = (np.array_equal(np.nan_to_num(a_on, nan=-999), np.nan_to_num(m_on, nan=-999))
                 and np.array_equal(np.nan_to_num(a_off, nan=-999), np.nan_to_num(m_off, nan=-999)))
        med = {}
        for arm, a, f in (("on", a_on, f_on), ("off", a_off, f_off)):
            b = np.isfinite(a) & np.isfinite(f)
            med[arm] = float(np.median(np.abs(f[b] - a[b]))) if b.any() else None
            med[arm + "_p90"] = float(np.percentile(np.abs(f[b] - a[b]), 90)) if b.any() else None
        print(f"  {sc}  aabb==main:{ident}  "
              f"med|f-a| on {med['on']:.4f} (p90 {med['on_p90']:.2f}) / "
              f"off {med['off']:.4f} (p90 {med['off_p90']:.2f})  "
              f"cover fused on {np.isfinite(f_on).mean():.3f} off {np.isfinite(f_off).mean():.3f}")
        print(f"     raw footprint cells:  aabb/aabb {fp_cells(a_on, a_off):7d}   "
              f"fused/fused {fp_cells(f_on, f_off):7d}   "
              f"aabbON/fusedOFF {fp_cells(a_on, f_off):7d}   "
              f"fusedON/aabbOFF {fp_cells(f_on, a_off):7d}"
              f"    [main-round adopted: {MAIN_RULE.get(sc, '-')}]")


if __name__ == "__main__":
    run("e", ["scene07", "scene08", "scene12"])
    run("e2", ["scene07", "scene12"])
