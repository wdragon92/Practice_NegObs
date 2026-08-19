#!/usr/bin/env python3
"""Ground-truth test of the camera convention on REAL cuts.

Reprojects the depth sidecar to world and checks that bottom-centre pixels land
on the camera's own standing ground (cam.ground_z).  PASS = median |dz| < 0.10 m.
On failure it re-runs the whole grid of yaw/pitch/roll sign flips and reports
which variant fits best -- SUGGESTION ONLY, nothing is auto-applied.
"""
import argparse, itertools, json, os
import numpy as np
from labeler import unproject, W_IMG, H_IMG, CAM_SRC

TOL = 0.10
Y_LO, Y_HI = 0.82, 1.00     # bottom band  (fraction of image height)
X_LO, X_HI = 0.40, 0.60     # centre band  (fraction of image width)
APPROACH_X = -0.15          # drop edge is at x=0; only x < this is standing ground
DS = 4


MIN_N = 200


def band_dz(dep, cam, eye, approach_only=True):
    """|reconstructed z - cam.ground_z| over bottom-centre pixels.  With
    approach_only, keep just the pixels that land BEFORE the drop edge (x=0) --
    rays that fall into the drop are off the standing ground by construction and
    would otherwise swamp the median with the scene's own drop depth.  If the
    bottom band holds too few such pixels the band is grown upward once."""
    P, good = unproject(dep, eye, cam, DS)
    h, w = P.shape[:2]
    xs = slice(int(X_LO * w), int(X_HI * w))
    out = np.array([])
    for lo in (Y_LO, 0.55):
        ys = slice(int(lo * h), max(int(Y_HI * h), int(lo * h) + 1))
        sub, g = P[ys, xs], good[ys, xs].copy()
        if approach_only:
            g &= sub[..., 0] < APPROACH_X
        z = sub[..., 2][g]
        out = np.abs(z - cam["ground_z"]) if z.size else np.array([])
        if out.size >= MIN_N:
            break
    return out


def flip(cam, sy, sp, sr):
    c = dict(cam); c["yaw"] *= sy; c["pitch"] *= sp; c["roll"] *= sr
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene-dir", required=True)
    ap.add_argument("--n", type=int, default=3)
    a = ap.parse_args()

    v = json.load(open(os.path.join(a.scene_dir, "variation.json")))
    cu = v["cuts"]
    cuts = [c for c in (cu.values() if isinstance(cu, dict) else cu)
            if c.get("ok", True) and os.path.isfile(
                os.path.join(a.scene_dir, os.path.splitext(c["file"])[0] + ".depth.npy"))]
    if not cuts:
        print("FAIL: no cut with a .depth.npy sidecar in", a.scene_dir); return 2
    cuts = cuts[:max(a.n, 1)]
    print(f"# verify_reprojection  scene={v.get('scene')}  cuts={len(cuts)}")
    print(f"# camera convention source: {CAM_SRC}")

    fails, skipped, agg = 0, 0, {}
    for c in cuts:
        cam, eye = c["cam"], np.asarray(c["cam"]["eye"], float)
        dep = np.load(os.path.join(a.scene_dir,
                                   os.path.splitext(c["file"])[0] + ".depth.npy")).astype(np.float64)
        e = band_dz(dep, cam, eye)
        raw = band_dz(dep, cam, eye, approach_only=False)
        if e.size == 0:
            print(f"{c['file']}: SKIP (inconclusive) — this cut's bottom-centre rays all "
                  f"land past the drop edge, so it has no standing ground to check "
                  f"(raw n={raw.size}, raw median="
                  f"{float(np.median(raw)) if raw.size else float('nan'):.4f})")
            skipped += 1
            continue
        med, p25, frac = float(np.median(e)), float(np.percentile(e, 25)), float((e < TOL).mean())
        ok = med < TOL
        fails += (not ok)
        print(f"{c['file']}: median|dz|={med:.4f} p25={p25:.4f} frac<{TOL}={frac:.3f} "
              f"n={e.size} (raw-band median={float(np.median(raw)):.4f} n={raw.size}) "
              f"yaw={cam['yaw']:+.3f} pitch={cam['pitch']:+.3f} "
              f"roll={cam['roll']:+.3f} hfov={cam['hfov']:.3f} gz={cam['ground_z']:.4f} "
              f"-> {'PASS' if ok else 'FAIL'}")
        for sy, sp, sr in itertools.product((1, -1), repeat=3):
            ee = band_dz(dep, flip(cam, sy, sp, sr), eye)
            agg.setdefault((sy, sp, sr), []).append(
                float(np.median(ee)) if ee.size else float("nan"))

    print("\n# sign-variant diagnostics (median of per-cut median |dz|)")
    rank = sorted(((float(np.nanmedian(v_)) if np.any(np.isfinite(v_)) else float("inf"), k)
                   for k, v_ in agg.items()))
    for m, (sy, sp, sr) in rank:
        tag = " <- AS-IMPLEMENTED" if (sy, sp, sr) == (1, 1, 1) else ""
        val = "no approach-side samples" if not np.isfinite(m) else f"{m:.4f}"
        print(f"  yaw*{sy:+d} pitch*{sp:+d} roll*{sr:+d} : {val}{tag}")
    rank = [r for r in rank if np.isfinite(r[0])]
    if fails and rank and rank[0][1] != (1, 1, 1):
        sy, sp, sr = rank[0][1]
        print(f"\nSUGGESTION (not applied): best fit is yaw*{sy:+d} pitch*{sp:+d} "
              f"roll*{sr:+d} (median {rank[0][0]:.4f}). Patch labeler.cam_basis only "
              f"after confirming against CAM_CONVENTION.md / driver code.")
    concl = len(cuts) - skipped
    print(f"\nRESULT: {concl - fails}/{concl} conclusive cuts pass (tol {TOL} m); "
          f"{skipped} skipped as inconclusive")
    print(f"NOTE: the gate uses only bottom-centre pixels reconstructing to x < {APPROACH_X} "
          "(the camera's own standing ground, before the x=0 drop edge). A cut aimed wholly "
          "past the edge is SKIPped, not failed.")
    print("NOTE: the z-residual discriminates the PITCH sign strongly; yaw and roll sign "
          "errors barely move z over flat ground, so treat their rows as weak evidence.")
    if concl == 0:
        print("INCONCLUSIVE: no cut had standing ground in frame — rerun with a larger --n "
              "or a scene whose cameras stand further back.")
        return 2
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
