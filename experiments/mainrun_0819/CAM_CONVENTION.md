# CAM_CONVENTION.md — the exact camera math of the data channel

Repo `/home/vislab/Desktop/work_sy/Practice_NegObs`, branch `feat/realism-v1`, HEAD `8c814db`
plus tonight's sidecar patch to `scripts/run_data_render.py`. Every line number below is the
**post-patch** line number of the file as it stands now.

Purpose: a downstream reprojection labeler must be able to take
`<cut>.depth.npy` + the `cam` block of `variation.json` and recover the world point behind
every pixel, with no access to Isaac. §6 is that recipe; §1–§5 are the derivation, §7 is the
verification that was actually run.

**World frame** (`scene_common.py:13`): *Z-up, metres, travel axis +X, drop start edge x = 0.*

---

## 1. What the sampler produces, and what each number means

Per cut, `variation_kit.sample_camera` (`variation_kit.py:606-626`) draws
`d, h_rel, y, yaw, pitch, roll, hfov`; `run_data_render.py:444-445` turns them into an eye:

```python
# scripts/run_data_render.py:444-445
gz  = pre.ground_z(-s["d"], s["y"])          # AabbPrefilter.ground_z, variation_kit.py:781
eye = (-s["d"], s["y"], gz + s["h_rel"])
```

| `cam` key | Meaning — exactly |
|---|---|
| `d` | **Standoff behind the drop-start edge along the travel axis.** `eye.x = -d`, always. It is *not* a range to the hazard and *not* a range to anything visible. LogU(1.2, 12.0) m (`variation_kit.py:581,615`). |
| `eye` | `[-d, y, ground_z + h_rel]`, world metres. `y` is the sampled lateral offset about the scene's own walk axis `gy` (`variation_kit.py:618`). |
| `ground_z` | **Absolute world z of the ground under the eye's (x, y)**, from a downward ray cast from z = +60 over the world AABBs of every Gprim (`variation_kit.py:781-785`). It is the *first* thing hit from above, so where a deck or bridge overhangs `(x, y)`, this is the deck's top, not the terrain's. Boxes larger than 400 m in any axis (sky domes, infinite planes) are excluded from the set (`variation_kit.py:754`). |
| `h_rel` | Eye height **above that ground**, U(0.25, 1.90) m (U(0.25, 1.20) on the four CAM-2 scenes). `eye.z = ground_z + h_rel` — the sampled height is never an absolute z. |
| `yaw`, `pitch`, `roll` | Degrees. Signs and axes in §2. |
| `hfov` | Horizontal field of view, degrees, N(62.2, 1.5) truncated [58, 66]. |
| `focal`, `aperture` | The USD attributes actually authored, §4. |
| `tier` | `CAM-1` / `CAM-2` / `CAM-3` (`variation_kit.py:592-594`), a sampler-band label only. |

`stage1.ground_below` (`variation_kit.py:796-797`) is a **different** ray: it is cast
**downward from the eye**, and its value is the distance from the eye to the first AABB hit
below it. Because the eye was placed at `ground_z + h_rel`, `ground_below == h_rel` — and
`check_data_run.py:210-213` asserts `|ground_below − h_rel| < 0.02` on every cut precisely to
prove the ground-relative placement landed. Read it as *"clearance under the camera"*, not as
an absolute height, and note it is the height above whatever surface is directly under the eye —
which is the same surface `ground_z` measured, from the other side.

**None of the three is a hazard distance.** The camera is never aimed at anything: there is no
look-at target and no target prim (`run_data_render.py:455-458` sets the matrix from
yaw/pitch/roll alone).

---

## 2. Rotation: order, axes, signs

`variation_kit.py:629-632`:

```python
def dir_of(yaw_deg, pitch_deg):
    """Unit view direction. Scenes look along +X; yaw rotates about +Z."""
    y, p = math.radians(yaw_deg), math.radians(pitch_deg)
    return (math.cos(p) * math.cos(y), math.cos(p) * math.sin(y), math.sin(p))
```

* **forward** `f = (cos p · cos y, cos p · sin y, sin p)`, a world unit vector.
* **yaw** rotates about **world +Z**. `yaw = 0` ⇒ forward is **+X**, the travel axis.
  Positive yaw turns toward **+Y** (counter-clockwise seen from above, i.e. to the camera's
  *left*).
* **pitch** is the elevation of the forward vector above the horizontal plane.
  **Negative pitch = looking down** (`sin p < 0`). The sampler only ever produces
  `pitch ∈ [−20, −2]`°, so the data channel is always tilted downward.
* **There is no rotation order to get wrong.** yaw and pitch are not applied as sequential
  Euler rotations — they are the two spherical parameters of a single direction vector, and
  roll is then a rotation *about that direction*. SP-7 chose this precisely to delete the
  question (`variation_kit.py:637-640`); measured roll error ≤ 0.005°, hFOV error ≤ 0.047°.

`variation_kit.py:635-654` builds the basis:

```python
r  = normalize(cross(f, +Z))          # = normalize(( f_y, −f_x, 0 ))
u  = cross(r, f)
r2 = r·cos ρ + u·sin ρ                # ρ = roll, radians
u2 = −r·sin ρ + u·cos ρ
rows = [(*r2, 0), (*u2, 0), (−f_x, −f_y, −f_z, 0), (eye_x, eye_y, eye_z, 1)]
```

* **right** `r = (f_y, −f_x, 0)/‖·‖` — horizontal, no z component before roll. At `yaw = 0`
  this is `(0, −1, 0)`: **the camera's right is world −Y**. (Verified numerically, §7.)
* **up** `u = r × f`. At `yaw = 0, pitch = 0` this is `(0, 0, 1)` = world +Z. At
  `pitch = −10°` it is `(0.1736, 0, 0.9848)` — the up axis leans forward as the camera tilts
  down, as it must.
* **roll** rotates the (right, up) pair by +ρ **inside the image plane**, about the forward
  axis. Concretely: world **+Z** projects to the image direction `(sin ρ, cos ρ)` in
  (right, up) components, so **a positive roll tilts the world vertical clockwise by ρ in the
  displayed frame**. At `roll = +5°`, `r2 = (0, −0.9962, +0.0872)`.
* **No flips anywhere.** No axis is negated beyond the single `−f` that USD requires (§3), the
  principal point is the exact frame centre, and `RES_W × RES_H = 1920 × 1080` is never
  transposed.

---

## 3. The USD xform

The camera is authored as **one** `xformOp:transform` (`run_data_render.py:374`
`AddTransformOp()`; set per cut at `:457` `c_m.Set(Gf.Matrix4d(*rows_flat))`) — deliberately
not `rotateXYZ`, which is what removes every rotation-order question.

`rows` above is **row-major, USD row-vector convention**, so the matrix is the camera's
**local-to-world** transform and its rows are the camera's basis expressed in world:

```
row 0 = camera +X (right) = r2
row 1 = camera +Y (up)    = u2
row 2 = camera +Z         = −f
row 3 = translation       = eye
```

USD's camera convention is that a camera looks down its **local −Z** with +X right and +Y up.
Row 2 being `−f` is exactly that: `−(camera +Z) = f`. The basis is right-handed and orthonormal
(verified to 6.7e-16, §7).

Forward map: `P_world = x_c·r2 + y_c·u2 + z_c·(−f) + eye`.
Inverse map: `x_c = (P−eye)·r2`, `y_c = (P−eye)·u2`, `z_c = −(P−eye)·f`.

---

## 4. Focal length, aperture, pixels

`variation_kit.py:42-43` — `RES_W, RES_H = 1920, 1080`, `APERTURE = 20.955`.
`run_data_render.py:369-371`:

```python
cam.CreateHorizontalApertureAttr(vk.APERTURE)                    # 20.955
cam.CreateVerticalApertureAttr(vk.APERTURE * vk.RES_H / vk.RES_W)  # 11.7871875
cam.CreateClippingRangeAttr(Gf.Vec2f(0.01, 1000.0))
```

`run_data_render.py:458` sets, per cut, `focalLength = vk.focal_for_hfov(hfov)`
(`variation_kit.py:598-603`):

```
focal = APERTURE / (2 · tan(hfov/2))
```

Because the vertical aperture is the horizontal one scaled by exactly `H/W`, the pixels are
**square** and the two focal lengths in pixels are *identical*:

```
f_px = focal / APERTURE_h · W = W / (2 · tan(hfov/2))
     = focal / APERTURE_v · H = H / (2 · tan(vfov/2))
```

| hfov | focalLength | vFOV | **f_px** |
|---|---|---|---|
| 58.0 | 18.90191 | 34.63484 | 1731.8858 |
| 62.2 (nominal, measured IMX219) | 17.36875 | 37.48638 | 1591.4102 |
| 66.0 | 16.13394 | 40.13367 | 1478.2704 |

The aperture's nominal unit (tenths of a mm in USD) never matters — only the ratio
`aperture : focal` sets the FOV, so no unit conversion exists anywhere in the pipeline.
`check_data_run.py:245-248` re-asserts `focal == focal_for_hfov(hfov)` to 1e-4 on every cut.

**Principal point is the exact frame centre**, `(W/2, H/2) = (960.0, 540.0)` in continuous pixel
coordinates. No `horizontalApertureOffset` / `verticalApertureOffset` is ever authored
(grep: they appear nowhere in the repo), so both are 0. There is no distortion model: the render
is an ideal pinhole.

---

## 5. What `.depth.npy` holds

Written by tonight's opt-in patch (`run_data_render.py:_depth_write`, gated on
`NEGOBS_DATA_SIDECARS=1`) from the Replicator annotator **`distance_to_image_plane`**:

* shape `(1080, 1920)`, dtype **float16**, row 0 = **top** of the image, column 0 = **left**;
* value = **`−z_c`**, i.e. the perpendicular distance from the **image plane through the eye** to
  the surface, measured along the forward axis `f`. It is *not* the radial range
  (`distance_to_camera`) — a pixel `θ` off-axis has `range = depth / cos θ`;
* metres, same units and same world scale as everything else;
* **no hit (sky, void) = `+inf`.** Anything non-finite from the annotator, and anything beyond
  float16 range (65504 m), is normalised to `+inf` before saving. Test with
  `np.isfinite`, never with `> 0`;
* float16 quantisation is `2^-10` relative ⇒ ≈ 1 cm at 10 m, ≈ 5 mm at 5 m — an order of
  magnitude below the 0.30 m hazard threshold;
* the file is fetched **after** `cap()` returns, i.e. after the PathTracing accumulation for
  that PNG has settled, so the depth and the RGB are the same frame. The cut record carries
  `"depth": "<stem>.depth.npy"` and `"depth_fetch"`, the escalation step that produced it.

---

## 6. Reprojection recipe (this is the contract)

Given a cut record `c` and its depth array `D` (shape `(H, W) = (1080, 1920)`):

```python
import math, numpy as np

W, H = 1920, 1080
eye  = np.array(c["cam"]["eye"], float)
yaw, pitch, roll = (math.radians(c["cam"][k]) for k in ("yaw", "pitch", "roll"))

# forward / right / up  — variation_kit.py:629-654, reproduced exactly
f = np.array([math.cos(pitch)*math.cos(yaw),
              math.cos(pitch)*math.sin(yaw),
              math.sin(pitch)])
r = np.array([f[1], -f[0], 0.0]); r /= np.linalg.norm(r)
u = np.cross(r, f)
cr, sr = math.cos(roll), math.sin(roll)
r2 =  r*cr + u*sr
u2 = -r*sr + u*cr

f_px = W / (2.0 * math.tan(math.radians(c["cam"]["hfov"]) / 2.0))   # == 1591.41 at 62.2 deg

# pixel (col j, row i) -> world.  Pixel CENTRES are at (+0.5, +0.5).
j, i = np.meshgrid(np.arange(W), np.arange(H))
xn = (j + 0.5 - W / 2.0) / f_px          # right-positive
yn = (H / 2.0 - (i + 0.5)) / f_px        # up-positive (image row grows DOWNWARD)

D = np.load(path).astype(np.float64)     # +inf = sky
P = eye[None, None, :] + D[..., None] * (f[None, None, :]
                                         + xn[..., None] * r2[None, None, :]
                                         + yn[..., None] * u2[None, None, :])
valid = np.isfinite(D)
```

Forward direction (world point → pixel), for projecting a heightmap cell into the frame:

```python
v  = P - eye
xc, yc = v @ r2, v @ u2
Dp = v @ f                               # = distance_to_image_plane; behind camera if <= 0
u_px = W / 2.0 + f_px * (xc / Dp)
v_px = H / 2.0 - f_px * (yc / Dp)
```

Cross-checks a labeler should assert on real data:

* `P[..., 2] ≈ cam.ground_z − h_rel + h_rel` at the eye — trivially, `P` at the exact frame
  centre pixel with `D = Dp` reproduces `eye + D·f`;
* the drop-start edge is `x = 0` in every scene (`scene_common.py:13`), so ground pixels with
  `P[...,0] < 0` are on the near, standing side;
* the ground plane the camera stands on is `z = cam.ground_z`; a pixel is *below the standing
  ground by δ* when `cam.ground_z − P[...,2] ≥ δ`. The repo's declared hazard threshold is
  **δ = 0.30 m** (doc constant, never a code constant — SPEC_EXTRACTED (g)).

Companion sidecar: `heightmap.npy` in the same scene directory is a `(ny, nx) = (321, 321)`
float32 field indexed `z[y_idx, x_idx]`, with `x = −2 + 0.05·x_idx`, `y = −8 + 0.05·y_idx`,
NaN where nothing was hit; `heightmap_meta.json` carries those constants, the hazard arm
(`arm_config`) and whether a per-scene exact oracle replaced the AABB read (`solid_at_used`,
`oracle`). It is the same world frame and the same metres, so heightmap → §6 forward map is a
direct projection.

---

## 7. Verification actually run

`python3` over `variation_kit.look_at_rows`, 2000 random poses drawn from the sampler's own
truncation bands (`h_rel`, `yaw ∈ [−20,20]`, `pitch ∈ [−20,−2]`, `roll ∈ [−5,5]`,
`hfov ∈ [58,66]`), one random world point in front of each:

```
basis orthonormality + det=1 worst error   6.66e-16
project -> unproject round trip, worst     1.07e-14 m
f_px from hFOV == f_px from vFOV           exact at 58 / 62.2 / 66 deg
```

Sign spot-checks (rows of `look_at_rows`, printed):

```
yaw 0, pitch 0, roll 0   right (0,−1,0)          up (0,0,1)          −f (−1,0,0)
yaw +10                  right (0.1736,−0.9848,0)                    −f (−0.9848,−0.1736,0)
pitch −10                right (0,−1,0)          up (0.1736,0,0.9848) −f (−0.9848,0,0.1736)
roll +5                  right (0,−0.9962,0.0872) up (0,0.0872,0.9962)
```

### The empirical half — real frames, 08-19 patch probe

`260819_patchprobe_on` / `_off`, scene04, 8 twin cuts each. For the bottom-centre pixel
(`row 1079, col 960`) the §6 recipe was used to reconstruct the world point from
`<cut>.depth.npy`, and compared against the ground the camera is standing on
(`z = cam.ground_z`, flat for `x < 0` in every scene):

| cut | where the bottom-centre ray lands | recovered `z` | independent check |
|---|---|---|---|
| 6 of 8 | `x < 0`, the standing side | 0.001 – 0.006 | `cam.ground_z` 0.002 – 0.006 → **agreement ≤ 5 mm** |
| idx 1 | `x = +0.06`, just past the edge | 0.001 | heightmap 0.001 → **0 mm** |
| idx 5, hazard **ON** | `x = +2.39`, inside the drop | **−0.629** | heightmap **−0.610** → **19 mm** |
| idx 5, hazard **OFF** | `x = +1.26`, flat control | **0.000** | heightmap 0.000 → **0 mm** |

Predicted-vs-measured depth at that pixel, taking the ground as flat, is
**0.01 – 0.39 % (mean 0.13 %) over all 8 cuts of the hazard-OFF arm**, where the ground really
is flat. In the hazard-ON arm the same test is 0.01 – 0.39 % for the seven cuts that land on
`x < 0` and **35.7 % for idx 5** — because idx 5 is the one ray that falls into the drop and a
flat-ground prediction is simply the wrong model there. The 19 mm agreement with the heightmap
at that same point is what closes it: depth, heightmap and this document are three independent
routes to the same world coordinate, and they meet to ~2 cm.
