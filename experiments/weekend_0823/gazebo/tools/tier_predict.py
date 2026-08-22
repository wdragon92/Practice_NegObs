#!/usr/bin/env python3
"""Per-preset V/E/H prediction for the gz_drop* worlds, against the labeler's real thresholds.

Pure arithmetic on the world geometry -- imports make_worlds.py, launches nothing.
Re-run it after changing --d3-occ / --d4-lat to regenerate worlds/README.md §8.

labeling/labeler.py:  DS = 4 (depth downsampled x4 before int_px is counted)
                      TAU_INT_DEF = 50, TAU_EDGE_DEF = 0.05
                      tier_of: int_px==0 and edge_vis==0 -> H
                               int_px >= tau_int         -> V
                               edge_ratio >= tau_edge    -> E
                               else                      -> H_weak
So the pixel budget is 50 pixels ON THE /4 GRID  ==  800 full-resolution pixels.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from make_worlds import (build_cameras, X_LIP, DROP1, DROP2, NOTCH_HY, DECK_HY,
                         D3_PIT_X0, D3_PIT_X1, D3_PIT_HY, D3_DROP,
                         D3_OCC_X0, D3_OCC_X1, D3_OCC_HY, D3_OCC_BODY_H, D3_OCC_CAP_H,
                         D4_W, D4_HY, D4_DROP)

DS = 4
TAU_INT, TAU_EDGE = 50, 0.05
OCC_H = D3_OCC_BODY_H + D3_OCC_CAP_H


def optics(c):
    w, h = c["res"]
    vfov = 2 * math.atan(math.tan(c["hfov"] / 2) * h / w)
    return dict(w=w, h=h, vfov=vfov,
                rad_row=vfov / h, rad_col=c["hfov"] / w)


def px_ds(area_full):
    return area_full / (DS * DS)


def tier(int_px, edge_vis, edge_ratio):
    if int_px == 0 and edge_vis == 0:
        return "H"
    if int_px >= TAU_INT:
        return "V"
    if edge_ratio is not None and edge_ratio >= TAU_EDGE:
        return "E"
    return "H_weak"


def far_wall_case(c, D, F, half_lat, label):
    """Bounded hazard: opening of width F (along X) and lateral half-width `half_lat`.

    Sight line grazes the near lip and descends at h/d; at the far wall it sits at depth
    F*h/d, so the exposed far-wall band is min(D, F*h/d).  The floor only shows past
    x_vis = D*d/h, which for these narrow openings is always beyond F.
    """
    o = optics(c)
    d = X_LIP - c["x"]
    h = c["z"]
    band = min(D, F * h / d)
    x_vis = D * d / h
    R = d + F
    rows = band / R / o["rad_row"]
    cols = min(2 * half_lat / R / o["rad_col"], o["w"])
    full = rows * cols
    return dict(view=c["view"], d=d, h=h, band=band, x_vis=x_vis, R=R,
                rows=rows, cols=cols, full=full, ds=px_ds(full),
                tier=tier(px_ds(full), 1, 1.0), label=label)


def open_plane_case(c, D, x_end, label):
    """Unbounded lower level: everything past x_vis down to the world edge is interior."""
    o = optics(c)
    d = X_LIP - c["x"]
    h = c["z"]
    x_vis = D * d / h
    if x_vis >= x_end:
        return dict(view=c["view"], d=d, h=h, band=0.0, x_vis=x_vis, R=d + x_vis,
                    rows=0.0, cols=0.0, full=0.0, ds=0.0,
                    tier=tier(0, 1, 1.0), label=label)
    s1, s2 = d + x_vis, d + x_end
    rows = (math.atan((h + D) / s1) - math.atan((h + D) / s2)) / o["rad_row"]
    cols = o["w"]
    full = rows * cols
    return dict(view=c["view"], d=d, h=h, band=D, x_vis=x_vis, R=s1,
                rows=rows, cols=cols, full=full, ds=px_ds(full),
                tier=tier(px_ds(full), 1, 1.0), label=label)


def drop3_case(c):
    """Occluded pit.  Returns the clearance of the sight line above the two things that
    must stay hidden: the rim (z=0 at x=X_LIP) and the pit's far wall top (z=0 at D3_PIT_X1).
    Positive clearance = hidden."""
    o = optics(c)
    d = X_LIP - c["x"]
    h, xe = c["z"], c["x"]
    if h < OCC_H:                      # eye below the parapet: near-top edge is the silhouette
        xs, mode = D3_OCC_X0, "up"
    else:                              # eye above it: far-top edge is the silhouette
        xs, mode = D3_OCC_X1, "down"
    a = xs - xe
    slope = (OCC_H - h) / a            # dz/dx of the grazing ray beyond the silhouette

    def z_at(x):
        return OCC_H + slope * (x - xs)

    cl_rim = z_at(X_LIP)               # >0 => rim hidden
    cl_far = z_at(D3_PIT_X1)           # >0 => pit far wall (top at z=0) hidden
    # lateral: the parapet's shadow half-width at a given x
    def shadow_hw(x):
        return D3_OCC_HY * (x - xe) / (xs - xe)
    lat_near = shadow_hw(X_LIP) - D3_PIT_HY
    lat_far = shadow_hw(D3_PIT_X1) - D3_PIT_HY
    hidden = cl_rim > 0 and cl_far > 0 and lat_near > 0 and lat_far > 0
    # how many pixels of margin at the tightest vertical point
    R = d + (D3_PIT_X1 - X_LIP)
    marg_px = min(cl_rim, cl_far) / R / o["rad_row"]
    return dict(view=c["view"], d=d, h=h, mode=mode, cl_rim=cl_rim, cl_far=cl_far,
                lat_near=lat_near, lat_far=lat_far, marg_px=marg_px,
                tier="H" if hidden else "LEAK(V/E)")


def table(title, rows, cols):
    print(f"\n### {title}")
    hdr = "".join(f"{c[0]:<{c[1]}}" for c in cols)
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        print("".join(f"{c[2](r):<{c[1]}}" for c in cols))


negobs = [c for c in build_cameras() if c["family"] == "negobs"]
rs = [c for c in build_cameras() if c["family"] == "rs"]
order = {"extra_h0.3_d1.2": 0, "preset_h0.3_d2": 1, "preset_h0.3_d5": 2, "preset_h0.3_d10": 3,
         "preset_h0.9_d2": 4, "preset_h0.9_d5": 5, "preset_h0.9_d10": 6}
negobs.sort(key=lambda c: order[c["view"]])

C = [("view", 20, lambda r: r["view"]),
     ("h/d", 9, lambda r: f"{r['h']/r['d']:.3f}"),
     ("band m", 10, lambda r: f"{r['band']:.4f}"),
     ("R m", 8, lambda r: f"{r['R']:.2f}"),
     ("rows px", 10, lambda r: f"{r['rows']:.1f}"),
     ("cols px", 10, lambda r: f"{r['cols']:.0f}"),
     ("int_px full", 14, lambda r: f"{r['full']:,.0f}"),
     ("int_px /4grid", 15, lambda r: f"{r['ds']:,.0f}"),
     ("tier", 6, lambda r: r["tier"])]

print("=" * 100)
print("labeler thresholds: TAU_INT_DEF=50 on a DS=4 depth map (= 800 full-res px), "
      "TAU_EDGE_DEF=0.05")
print("=" * 100)

table("gz_drop4  -- narrow trench  %.2f m (X) x %.2f m (lat) x %.2f m deep"
      % (D4_W, 2 * D4_HY, D4_DROP),
      [far_wall_case(c, D4_DROP, D4_W, D4_HY, "d4") for c in negobs], C)
table("gz_drop4  -- rs cameras (baseline RealSense optics)",
      [far_wall_case(c, D4_DROP, D4_W, D4_HY, "d4") for c in rs], C)

table("gz_drop1  -- stair + pit (far wall %.1f m past lip, D=%.2f)" % (8.0, DROP1),
      [far_wall_case(c, DROP1, 8.0, NOTCH_HY, "d1") for c in negobs], C)
table("gz_drop2  -- open platform edge (lower plane runs to x=120)",
      [open_plane_case(c, DROP2, 108.0, "d2") for c in negobs], C)

C3 = [("view", 20, lambda r: r["view"]),
      ("eye vs top", 12, lambda r: r["mode"]),
      ("rim clear m", 14, lambda r: f"{r['cl_rim']:+.3f}"),
      ("far-wall clear m", 18, lambda r: f"{r['cl_far']:+.3f}"),
      ("lat margin near", 17, lambda r: f"{r['lat_near']:+.3f}"),
      ("lat margin far", 16, lambda r: f"{r['lat_far']:+.3f}"),
      ("min margin px", 15, lambda r: f"{r['marg_px']:.0f}"),
      ("tier", 6, lambda r: r["tier"])]
table("gz_drop3  -- pit %.2f m deep behind a %.2f m parapet (clearance > 0 = hidden)"
      % (D3_DROP, OCC_H),
      [drop3_case(c) for c in negobs + rs], C3)

print("\n### summary")
for name, rows in [("gz_drop1", [far_wall_case(c, DROP1, 8.0, NOTCH_HY, "") for c in negobs]),
                   ("gz_drop2", [open_plane_case(c, DROP2, 108.0, "") for c in negobs]),
                   ("gz_drop3", [drop3_case(c) for c in negobs]),
                   ("gz_drop4", [far_wall_case(c, D4_DROP, D4_W, D4_HY, "") for c in negobs])]:
    t = [r["tier"] for r in rows]
    print(f"  {name}: " + "  ".join(f"{k}={t.count(k)}" for k in ("V", "E", "H", "LEAK(V/E)")
                                    if t.count(k)))

print("\n### where E dies: minimum opening area that still clears TAU_INT at each preset")
print(f"{'view':<20}{'max opening area m2 for E':<28}{'(W x lat) if W=0.25':<24}")
for c in negobs:
    o = optics(c)
    d, h = X_LIP - c["x"], c["z"]
    R = d + D4_W
    k = (h / d) / (R * R * o["rad_row"] * o["rad_col"] * DS * DS)   # int_px_ds per m^2
    amax = TAU_INT / k
    print(f"{c['view']:<20}{amax:<28.3f}{'lat < %.2f m' % (amax / D4_W):<24}")
