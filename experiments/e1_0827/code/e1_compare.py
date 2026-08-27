# -*- coding: utf-8 -*-
"""e1_compare.py -- per-instance route (a) vs route (b) deviation, in pixels.

For every VISIBLE projected point of an (a) instance, the distance to the
nearest route-(b) edge pixel. Computed with a Euclidean distance transform on
the complement of the (b) mask, so the answer is exact to the pixel grid and
costs one pass regardless of how many instances there are.

Reported as {mean, median, p90} into `src_disagree_px` (§5). There is no pass
line: brief §4 Phase 1 says the deviation is a number to print, and the judgement
is 결재.

Asymmetry is deliberate and must be read as such: this measures "how far is (a)
from the nearest (b)", not the reverse. A route-(b) line with no (a) counterpart
(an object silhouette) does not show up here at all -- it shows up as the
component count gap printed alongside.
"""

import numpy as np
import scipy.ndimage as ndi


def distance_field(b_mask):
    """Distance in px from every pixel to the nearest True pixel of `b_mask`."""
    if not np.any(b_mask):
        return None
    return ndi.distance_transform_edt(~np.asarray(b_mask, dtype=bool))


def deviation(dist_field, px, py, visible, shape):
    """{mean, median, p90} px for one instance's visible projected points."""
    if dist_field is None or not np.any(visible):
        return {"mean": None, "median": None, "p90": None}, 0
    H, W = shape
    xi = np.clip(np.round(np.asarray(px)[visible] - 0.5).astype(np.int64), 0, W - 1)
    yi = np.clip(np.round(np.asarray(py)[visible] - 0.5).astype(np.int64), 0, H - 1)
    d = dist_field[yi, xi]
    if d.size == 0:
        return {"mean": None, "median": None, "p90": None}, 0
    return ({"mean": float(np.mean(d)), "median": float(np.median(d)),
             "p90": float(np.percentile(d, 90))}, int(d.size))
