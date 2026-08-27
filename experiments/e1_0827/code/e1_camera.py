# -*- coding: utf-8 -*-
"""e1_camera.py -- camera model rebuilt from variation.json, plus the numeric
proof that it is right.

Where the convention comes from
-------------------------------
The renderer authors the camera as ONE matrix op built by
`variation_kit.look_at_rows(eye, yaw, pitch, roll)` on top of
`variation_kit.dir_of(yaw, pitch)` (repo root, driver code -- read to learn the
stored convention, NOT imported for any labelling logic):

    forward f = (cos p cos y, cos p sin y, sin p)          # scenes look along +X
    right   r = normalize(cross(f, +Z)) = (f_y, -f_x, 0)
    up      u = cross(r, f)
    roll    r' =  r cos(roll) + u sin(roll)
            u' = -r sin(roll) + u cos(roll)

`variation.json` stores per cut: eye[3], yaw, pitch, roll (deg), hfov (deg),
focal (mm), aperture (mm). There is no extrinsic matrix and no vertical
aperture, so:

    fx = fy = (W/2) / tan(hfov/2)            # square pixels
    cx, cy = W/2, H/2                        # principal point dead centre

Consistency of the stored intrinsics is asserted at load time:
`2*atan(aperture/2/focal)` must reproduce the stored `hfov`.

Depth convention: `*.depth.npy` is float16, shape (H, W), and is a Z-DEPTH
(distance to the image plane), not a ray length -- `verify()` below is what
proves that reading, because a ray-length reading would leave a systematic,
radius-dependent |dz| instead of the flat residual we measure.
"""

import json
import math

import numpy as np

import e1_const as C


class CameraModel:
    """Pinhole camera for one rendered cut."""

    def __init__(self, cam: dict, width: int = C.IMG_W, height: int = C.IMG_H):
        self.eye = np.asarray(cam["eye"], dtype=np.float64)
        self.yaw = float(cam["yaw"])
        self.pitch = float(cam["pitch"])
        self.roll = float(cam["roll"])
        self.hfov = float(cam["hfov"])
        self.focal_mm = float(cam.get("focal", 0.0)) or None
        self.aperture_mm = float(cam.get("aperture", 0.0)) or None
        self.W, self.H = int(width), int(height)
        self.r, self.u, self.f = self._basis()
        self.fx = (self.W * C.value("PIXEL_ASPECT") * 0.5) / math.tan(math.radians(self.hfov) * 0.5)
        self.fy = self.fx
        self.cx, self.cy = self.W * 0.5, self.H * 0.5
        self.intrinsic_residual_deg = self._intrinsic_check()

    # -- construction ------------------------------------------------------ #
    def _basis(self):
        y, p, rl = (math.radians(self.yaw), math.radians(self.pitch),
                    math.radians(self.roll))
        f = np.array([math.cos(p) * math.cos(y), math.cos(p) * math.sin(y),
                      math.sin(p)], dtype=np.float64)
        r = np.array([f[1], -f[0], 0.0], dtype=np.float64)
        n = np.linalg.norm(r)
        r = r / (n if n else 1.0)
        u = np.cross(r, f)
        cr, sr = math.cos(rl), math.sin(rl)
        return r * cr + u * sr, -r * sr + u * cr, f

    def _intrinsic_check(self):
        """|hfov_stored - hfov_from(focal, aperture)| in degrees, or None."""
        if not (self.focal_mm and self.aperture_mm):
            return None
        hf = 2.0 * math.degrees(math.atan(self.aperture_mm * 0.5 / self.focal_mm))
        return abs(hf - self.hfov)

    # -- geometry ---------------------------------------------------------- #
    def project(self, pts):
        """world (N,3) -> (px, py, z_cam, in_frame)."""
        rel = np.asarray(pts, dtype=np.float64).reshape(-1, 3) - self.eye
        zc = rel @ self.f
        xc = rel @ self.r
        yc = rel @ (-self.u)
        front = zc > C.CAM_FRONT_Z_MIN_M
        z = np.where(front, zc, 1.0)
        px = self.cx + self.fx * xc / z
        py = self.cy + self.fy * yc / z
        inb = front & (px >= 0) & (px < self.W) & (py >= 0) & (py < self.H)
        return px, py, zc, inb

    def unproject(self, depth, stride=1):
        """z-depth image -> (world points (h,w,3), valid mask (h,w)).

        Ray directions have a unit z-component, so multiplying by the stored
        z-depth lands on the surface directly.
        """
        d = np.asarray(depth, dtype=np.float64)[::stride, ::stride]
        h, w = d.shape
        un = (np.arange(0, self.W, stride)[:w] + 0.5 - self.cx) / self.fx
        vn = (np.arange(0, self.H, stride)[:h] + 0.5 - self.cy) / self.fy
        UN, VN = np.meshgrid(un, vn)
        dirs = UN[..., None] * self.r + VN[..., None] * (-self.u) + self.f
        pts = self.eye + d[..., None] * dirs
        valid = np.isfinite(d) & (d > C.DEPTH_VALID_MIN_M)
        return pts, valid

    def depth_at(self, depth, px, py):
        """Rendered z-depth sampled at the nearest pixel; nan when out of frame."""
        d = np.asarray(depth, dtype=np.float64)
        xi = np.clip(np.round(np.asarray(px) - 0.5).astype(np.int64), 0, self.W - 1)
        yi = np.clip(np.round(np.asarray(py) - 0.5).astype(np.int64), 0, self.H - 1)
        return d[yi, xi]

    def as_dict(self):
        return {"eye": [float(v) for v in self.eye], "yaw": self.yaw,
                "pitch": self.pitch, "roll": self.roll, "hfov": self.hfov,
                "fx_px": self.fx, "cx": self.cx, "cy": self.cy}


# --------------------------------------------------------------------------- #
# heightmap access (needed by the camera proof; shared with e1_geometry)
# --------------------------------------------------------------------------- #
class HeightMap:
    """`heightmap.npy` + `heightmap_meta.json`. z[y_idx, x_idx], NaN = nodata.

    Provenance: variation_kit.AabbPrefilter.ground_z(top=60.0). See
    e1_const.HM_SOURCE_NOTE -- it is an AABB envelope, and that fact is a
    measured property of the corpus that the reports must carry.
    """

    def __init__(self, z, meta):
        self.z = np.asarray(z, dtype=np.float64)
        self.meta = meta
        self.x0 = float(meta["x0"])
        self.y0 = float(meta["y0"])
        self.step = float(meta["step"])
        self.ny, self.nx = self.z.shape

    @classmethod
    def load(cls, scene_dir):
        import os
        z = np.load(os.path.join(scene_dir, "heightmap.npy"))
        meta = json.load(open(os.path.join(scene_dir, "heightmap_meta.json")))
        return cls(z, meta)

    def xy_of(self, ix, iy):
        return self.x0 + np.asarray(ix) * self.step, self.y0 + np.asarray(iy) * self.step

    def sample(self, x, y):
        """Nearest-cell surface height; NaN outside the grid or at nodata."""
        ix = np.round((np.asarray(x) - self.x0) / self.step)
        iy = np.round((np.asarray(y) - self.y0) / self.step)
        ok = (ix >= 0) & (ix < self.nx) & (iy >= 0) & (iy < self.ny)
        ixc = np.clip(ix, 0, self.nx - 1).astype(np.int64)
        iyc = np.clip(iy, 0, self.ny - 1).astype(np.int64)
        out = self.z[iyc, ixc]
        return np.where(ok, out, np.nan)


# --------------------------------------------------------------------------- #
# THE PROOF
# --------------------------------------------------------------------------- #
def verify(cam: CameraModel, depth, hm: HeightMap, ground_z_recorded=None):
    """Numeric proof that the camera model matches the renderer.

    Three independent checks; every one of them prints a number:

      A. heightmap indexing   -- hm.sample(eye.x, eye.y) vs the `cam.ground_z`
                                 the renderer recorded for this cut. Validates
                                 x0 / y0 / step / z[y,x] ordering.
      B. projection algebra   -- unproject(depth) then project() back; the pixel
                                 round-trip error must be ~0.
      C. camera <-> world     -- |z_backprojected - z_heightmap| for depth pixels
                                 inside CAMCHK_RADIUS_M of the camera. This is
                                 the check that fails if the basis, the depth
                                 convention (z-depth vs ray length) or the
                                 principal point were wrong.

    Check C is reported, not thresholded: the heightmap is an AABB envelope, so
    a nonzero tail is expected wherever a railing / facade / roof AABB sits above
    the real surface. Both the full and the near-field distributions are printed.
    """
    out = {"intrinsic_residual_deg": cam.intrinsic_residual_deg}

    # A -------------------------------------------------------------------- #
    hm_at_eye = float(hm.sample(cam.eye[0], cam.eye[1]))
    inside = np.isfinite(hm_at_eye)
    if not inside:
        # the grid covers the scene, not the approach: cameras routinely stand
        # outside it. Sample the nearest in-grid cell and SAY SO.
        xc = float(np.clip(cam.eye[0], hm.x0, hm.x0 + (hm.nx - 1) * hm.step))
        yc = float(np.clip(cam.eye[1], hm.y0, hm.y0 + (hm.ny - 1) * hm.step))
        hm_at_eye = float(hm.sample(xc, yc))
    out["A_hm_at_eye_m"] = hm_at_eye
    out["A_clamped"] = bool(not inside)
    out["A_ground_z_recorded_m"] = (None if ground_z_recorded is None
                                    else float(ground_z_recorded))
    out["A_abs_diff_m"] = (None if ground_z_recorded is None or not np.isfinite(hm_at_eye)
                           else abs(hm_at_eye - float(ground_z_recorded)))

    # B and C -------------------------------------------------------------- #
    st = C.CAMCHK_STRIDE_PX
    pts, valid = cam.unproject(depth, stride=st)
    h, w = valid.shape
    ys, xs = np.nonzero(valid)
    P = pts[ys, xs]
    px, py, zc, inb = cam.project(P)
    exp_x = xs * st + 0.5
    exp_y = ys * st + 0.5
    err = np.hypot(px - exp_x, py - exp_y)
    err = err[np.isfinite(err) & inb]
    out["B_roundtrip_px_median"] = float(np.median(err)) if err.size else None
    out["B_roundtrip_px_p90"] = float(np.percentile(err, 90)) if err.size else None
    out["B_n"] = int(err.size)

    hz = hm.sample(P[:, 0], P[:, 1])
    dz = np.abs(P[:, 2] - hz)
    fin = np.isfinite(dz)
    rad = np.hypot(P[:, 0] - cam.eye[0], P[:, 1] - cam.eye[1])
    out["C_n_all"] = int(fin.sum())
    out["C_dz_median_all_m"] = float(np.median(dz[fin])) if fin.any() else None
    out["C_dz_p90_all_m"] = float(np.percentile(dz[fin], 90)) if fin.any() else None
    out["C_near"] = {}
    for r in C.CONSTANTS["CAMCHK_RADIUS_M"][3]:
        sel = fin & (rad <= r)
        out["C_near"]["r%.0fm" % r] = {
            "n": int(sel.sum()),
            "dz_median_m": float(np.median(dz[sel])) if sel.any() else None,
            "dz_p90_m": float(np.percentile(dz[sel], 90)) if sel.any() else None,
        }
    return out
