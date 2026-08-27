# -*- coding: utf-8 -*-
"""e1_overlay.py -- the inspection PNG (brief v6 §4 Phase 1-2).

RGB frame with, drawn on top:
  * route (a) visible edge polylines, one colour per instance
  * the visible interior mask OUTLINE (outline, not a fill -- a fill hides the
    pixels 승용 is being asked to judge)
  * an H_cand mark, and a separate UNRESOLVED mark when the occluder test could
    not be answered (no sidecar / unapproved prim). The two must not look the
    same: one is a finding, the other is a missing input.
  * per instance: dist_m {min, median}, int px, (a)-(b) deviation

Every number drawn comes from the record, so the overlay cannot disagree with
the json. Colours and stroke widths are the only constants here and they are
cosmetic (ledger: OVERLAY_LINE_PX, OVERLAY_FONT_PX).
"""

import os

import numpy as np
from PIL import Image, ImageDraw

import e1_const as C

PALETTE = [tuple(c) for c in C.OVERLAY_PALETTE]


def _outline(mask):
    """Boundary pixels of a boolean mask (4-neighbour erosion difference)."""
    m = np.asarray(mask, dtype=bool)
    er = m.copy()
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        er &= np.roll(np.roll(m, dy, axis=0), dx, axis=1)
    return m & ~er


def draw(record, extras, out_path):
    rgb = Image.open(extras["assets"]["rgb_path"]).convert("RGB")
    ov = rgb.copy()
    dr = ImageDraw.Draw(ov)
    lw = C.OVERLAY_LINE_PX
    arr = np.array(ov)

    for i, (edge, item) in enumerate(zip(record.edges, extras["kept"])):
        col = PALETTE[i % len(PALETTE)]
        if item["int_mask"] is not None and edge.int_area_px > 0:
            ob = _outline(item["int_mask"])
            arr[ob] = col
    ov = Image.fromarray(arr)
    dr = ImageDraw.Draw(ov)

    y_text = 8
    for i, edge in enumerate(record.edges):
        col = PALETTE[i % len(PALETTE)]
        for run in edge.polyline_px:
            if len(run) >= 2:
                dr.line([tuple(p) for p in run], fill=col, width=lw)
            elif run:
                x, y = run[0]
                dr.ellipse([x - lw, y - lw, x + lw, y + lw], outline=col)
        flag = edge.occluder.flag
        mark = ("H_cand" if flag is True else
                "occl:UNRESOLVED" if flag is None else "no-ext-occl")
        txt = ("%s  dist %s/%s m  int %s px (h%s w%s)  a-b %s/%s/%s px  %s"
               % (edge.edge_id,
                  _f(edge.dist_m.min), _f(edge.dist_m.median),
                  edge.int_area_px, edge.int_h_px, edge.int_w_px,
                  _f(edge.src_disagree_px.mean), _f(edge.src_disagree_px.median),
                  _f(edge.src_disagree_px.p90), mark))
        dr.text((8, y_text), txt, fill=col)
        y_text += C.OVERLAY_FONT_PX

    dr.text((8, y_text), "tier_now=%s  edges=%d  %s"
            % (record.tier_now, len(record.edges), record.frame_id),
            fill=(255, 255, 255))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    ov.save(out_path)
    return out_path


def _f(v):
    return "-" if v is None else ("%.2f" % v)
