# W1_CAPTURE — warehouse RGB-D capture for the YOLO detection-limit experiment

Stage W1 of the V-threshold experiment (`Docs/briefs/edge_relabel_brief_v6.md` §7, warehouse
A-track). Scope fence, unchanged: **the YOLO stage's detection limit only** — no navigation,
no depth-strip validation, no LiDAR fusion, no training. This stage produces frames and
ground-truth scene geometry; W2 measures visible-hole pixels and W3 runs the detector.

Everything under `Baseline_NegObs/src/negativeobstacleavoidandance/` was opened **read-only**.
Every world used for rendering is a COPY under `vth/worlds/`.

---

## 1. What the hazard actually is (measured, not assumed)

`bumperbot_description/models/large_holed_floor/meshes/large_holed_floor.stl`
(binary STL, 21,834 triangles, sha256 `ab75bc68feb3adae…`) is one perforated plate:

| quantity | value |
|---|---|
| plate size | 41.65 × 62.52 m (model-local x [−6.990, 34.660], y [−52.048, 10.472]) |
| plate thickness | **0.12432 m** (top z = 0.12432, bottom z = 0.0 in model frame) |
| solid area (holes removed) | 2557.07 m² |
| openings ≥ 25 cm² | **270** |
| opening area range | 0.0049 – 0.7351 m² |
| pose in **both** worlds | (−13.56098, 20.2009, 0, 0, 0, 0) — byte-identical placement |
| walking surface (world z) | **0.12432 m** |

Method: rasterise the plate's up-facing top-surface triangles at **1 cm** (the same raster
`gazebo_wh_0824/tools/project_hole.py` used), 4-connect the empty cells, and keep the
components that do not touch the grid border. Border-connected empties are the outside of
the plate, not holes. Components under 25 cells (25 cm²) are mesh-seam raster noise.

**The two hole families the paper describes fall straight out of the measurement.**
Rectangularity (opening area ÷ bbox area) is 0.785 for a disc and 1.00 for a square:

| family | count | size |
|---|---:|---|
| circle | 135 | diameter 0.136 – 0.967 m (**radius 0.068 – 0.484 m**) |
| square | 121 | area 0.0090 – 0.6862 m² |
| slot (aspect > 1.3, neither family) | 14 | e.g. 1.07 × 0.32 m |

The paper states "circular radius 0.05–0.8 m, square ≤ 0.8 m²"; the mesh gives
radius 0.068–0.484 m and square area ≤ 0.686 m². Consistent, and now numeric.

### What is under the plate — the two worlds differ, and it matters

| world | below the opening | drop depth |
|---|---|---|
| `eworld2` | **nothing.** `model://ground_plane` is commented out (line 11) and no floor asset exists | bottomless — rays exit the scene, depth = +inf, RGB = the `<background>` grey (178,178,178) |
| `expandedworld` | `aws_robomaker_warehouse_GroundB_01_001` at pose z = −0.090092, top surface z = **0.0344**, but only over x [−6.990, 7.010], y [−10.453, 10.468] | **0.0899 m** inside that footprint; bottomless outside it |

Of the target openings used here (9 distinct openings across the two worlds), only
`H60` (2.16, −3.78) sits over the GroundB slab. Everything else is bottomless in both
worlds.

**"Bottomless" does not mean "the whole opening is empty sky".** Measured on all 79
`eworld2` frames of `H60` (`tools/measure_void.py`), of the pixels whose sight line passes
through the opening's footprint:

| what the ray hits | share | depth |
|---|---:|---|
| the plate's own **cut face** (the 0.1243 m inner wall of the opening) | **82.3 %** | finite, hit z between 0.02 and 0.11 m below the walking surface (median 0.05 m) |
| the open void beyond | 17.7 % | `+inf` |

(The footprint test has to be the disc, not its bounding box — 1 − π/4 = 21.5 % of a
circular opening's bbox is bright floor, and using the bbox quietly mixes floor pixels into
every "interior" number. This was caught by an inside-the-hole saturation reading of
exactly 0.212 and fixed; both `tools/measure_void.py` and the report generator now use the
disc.)

The wall/void split is size-dependent: the same measurement on the largest opening,
`H00` (⌀0.97 m), gives **51.1 % void / 48.9 % cut face** instead of `H60`'s 17.7 / 82.3 —
a big opening lets more rays clear the lip. W2 cannot assume a fixed ratio.

The same 79 poses rendered in `expandedworld` give the control: **0.0 % bottomless**, every
interior ray finite, and the deepest hits pile up at z = **0.0342 m** — the GroundB slab,
whose top the mesh AABB predicted at 0.0344 m. Agreement to **0.2 mm**, so the 0.0899 m
drop depth read out of the world file is confirmed by the render, not just asserted.

So the visible interior of a warehouse opening is *a 0.124 m lip plus a hole through it* —
which is exactly what the contact sheet shows (dark inner wall, background-grey centre).
The **physical** drop is unbounded (nothing to land on); the **visible** geometry is only
0.124 m of wall. W2 and W3 must not confuse the two.

⚠ **This collides with the stair corpus's definition of 속** (brief §5: "pixels of a surface
≥ 0.3 m below the walking surface"). The plate is 0.124 m thick, so applied literally that
rule returns **zero interior pixels for every warehouse opening, including bottomless
ones**. For the warehouse, "interior" has to mean *pixels inside the opening's footprint*
(cut face + void) and the report has to say so. Flagging, not deciding — this is a
definition question for the owner (§9-❓ territory), not something W1 settles.

### Other differences between the two worlds

| item | `eworld2` | `expandedworld` |
|---|---|---|
| light sources | `model://sun` + 1 point light (0, −17, 8.5, diffuse 0.5) | **none at all** — zero `<light>`, no sun |
| `<scene>` ambient / shadows | 0.2 / false | 0.4 / true |
| models with geometry | 48 + plate | 53 + plate |
| walls | none (`WallB_01` commented out) | `WallB_01AB`, x [−12.7, 1.3], y [−10.7, 10.2], 9.0 m tall |
| SDF version | 1.6 | 1.7 |

Nothing above was changed. The lighting asymmetry is the paper's own and is left alone
(P2); it is logged here because it will show up as a domain gap in W3.

### One log message that looks alarming and is not

`eworld2` includes its 48 warehouse assets by full Ignition-Fuel URL, and the local Fuel
cache holds SDF **1.9** copies that Gazebo 11 (sdformat 9, max 1.7) cannot convert. Each
include therefore prints `Error [Converter.cc:113] Unable to convert from SDF version 1.9
to 1.7` — 48 of them per load. **The assets still load**: Gazebo falls back to
`GAZEBO_MODEL_PATH`, where `bumperbot_description/models/` carries SDF 1.6 copies of the
same assets. Verified geometrically rather than by eye — in `H00_xp_d15_h15_pm15` the
predicted near face of `aws_robomaker_warehouse_Bucket_01_020` is at 5.05 m and the
rendered depth at that pixel is **5.04 m**. `expandedworld` has zero Fuel URLs (its assets
are inlined) and logs no such error.

---

## 2. Camera and pose grid

The camera is the paper's own simulated RealSense D435, copied field by field from
`bumperbot_description/urdf/realsense2.urdf.xacro` (lines 102–129): hfov **1.2043 rad
(69.00°)**, **1280 × 720**, clip 0.1 / 100 m, and **no `<noise>` element** — the paper's
depth is noiseless and so is ours (recorded because §6-⑲ needs the noise setting to
interpret deviation statistics across domains).

One difference, deliberate: we declare a single `type="depth"` sensor per camera instead of
the paper's separate colour and depth sensors. A depth sensor emits both `image_raw` and
`depth/image_raw` from **one** rendering, so RGB and depth are the same pixels by
construction rather than by calibration. Measured confirmation is in §4.

Pose band from brief §7 (identical to the stair corpus): height **0.3–2.0 m above the
walking surface**, pitch **−15°…+5°** (negative = nose down). Grid:

| axis | values |
|---|---|
| standoff to the **near rim** (m) | 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0 |
| height above plate top (m) | 0.3, 0.6, 1.0, 1.5, 2.0 |
| pitch (deg) | −15, −5, +5 |
| approach directions per hole | 1 (of ±x, ±y — the one with the most usable stations) |

Target openings are a **size ladder** so that W3 can stratify by physical size and separate
the size↔distance confound (brief §6-⑱). Seven bands were requested per world:

| band | eworld2 | expandedworld |
|---|---|---|
| L1 0.70–0.80 m² | H00 circle ⌀0.97, 0.735 m² | H00 (same opening) |
| L2 0.55–0.65 m² | H18 square 0.79×0.79, 0.624 m² | H21 square 0.78×0.73, 0.569 m² |
| M1 0.30–0.36 m² | H30 circle ⌀0.66, 0.340 m² | H30 (same opening) |
| M2 0.19–0.26 m² | **H45 lost** (see below) → supplement H42 | H42 square 0.49×0.50, 0.245 m² |
| S1 0.13–0.17 m² | H60 circle ⌀0.41, 0.132 m² | H60 (same opening) |
| S2 0.055–0.070 m² | H98 square 0.25×0.25, 0.0625 m² | H98 (same opening) |
| T1 0.0085–0.0105 m² | H227 square 0.10×0.10, 0.010 m² | H259 square 0.09×0.10, 0.009 m² |

**The M2 band in `eworld2` had to be re-picked.** The first M2 candidate, `H45`
(a 0.26 × 1.07 m slot at −6.80, 5.57), turns out to sit right beside
`aws_robomaker_warehouse_ShelfF_01_001`: all 65 of its approach poses were rejected with
`sightline_blocked_by`, so the band produced nothing. `tools/plan_supp.py` re-picks that
band with two extra rules — the opening itself must not lie inside a blocker's footprint,
and the candidate has to actually yield poses — and lands on `H42` (0.49 × 0.50 m square),
the same opening `expandedworld` uses for M2. Those frames were rendered as a separate set
of world copies (`eworld2_s00…s02`) and are in the manifest like any other; the failure and
the 65 rejections stay in `holes.json` rather than being quietly dropped.

⚠ **Memorisation caveat, measured (brief ⑰).** The plate is the same mesh at the same pose
in both worlds, so H00 / H30 / H60 / H98 are *literally the same openings* in the training
and the evaluation world. That is a property of the paper's scenes, not a choice we made,
and W3 must print it as a limitation next to any world-split result.

**Pose validity.** Each planned pose is tested against the world's real geometry before it
is rendered, and every rejection is logged in `holes.json → worlds.<w>.skips`:

| rule | rejection reason |
|---|---|
| every cell within 0.25 m of the camera's footprint must be solid plate | `camera_not_over_solid_plate` (the camera would stand in another opening or off the plate) |
| camera must not be inside an asset's AABB (+0.20 m) | `camera_inside_asset:<model>` |
| the opening's projected top rim must put ≥ 1 px inside the frame | `hole_outside_fov` |
| for the main set, no asset may cross the sight line | `sightline_blocked_by:<model>` |
| for the occlusion set, an asset **must** cross the sight line | `no_occluder_on_sightline` |

Asset shapes come from each model's collision mesh (COLLADA/STL) reduced to its local AABB
and rotated by the model yaw — deliberately conservative, never smaller than the asset.

**Occlusion set (expandedworld only, `occlusion_intended=true`).** For each target opening,
every blocker whose centre is 0.8–7.0 m away is used as a screen: the camera is put on the
far side of it at 0.6 / 1.2 / 2.0 m clearance, at 4 heights and 2 pitches, and the pose is
kept only if the sight line to the opening really does cross that asset. 96 such poses were
sampled evenly from the candidates. No scene edit was made to create them (brief ㉖).

---

## 3. Capture — what was actually rendered

Headless `gzserver` (never `gzclient`), one world copy per batch of 30 static cameras, one RGB + one depth frame per camera, then torn down.

| | value |
|---|---|
| frames captured | **1231** |
| &nbsp;&nbsp;`eworld2` | 561 |
| &nbsp;&nbsp;`expandedworld` | 670 |
| &nbsp;&nbsp;of which `occlusion_intended` | 96 |
| poses planned (main + supplement) | 1147 + 84 = 1231 |
| manifest entries == files on disk | YES |
| poses skipped by the geometry rules (main plan; the supplement rejected 66 more) | 1709 |
| world loads (batches) | 42 |
| per-batch wall time (median) | load 13 s · grab 14 s · total 27 s |
| total wall time | 1349 s (22.5 min) |
| disk | 4.58 GiB (3.8 MiB per frame: 1280×720 PNG + 3.5 MiB float32 depth) |

### Coverage of the kept frames

**eworld2** — 561 approach frames

| axis | counts |
|---|---|
| standoff m | 0.3: 17 · 0.5: 24 · 0.7: 30 · 1.0: 39 · 1.5: 51 · 2.0: 65 · 3.0: 70 · 4.0: 91 · 6.0: 99 · 8.0: 75 |
| height m | 0.3: 186 · 0.6: 146 · 1.0: 105 · 1.5: 72 · 2.0: 52 |
| pitch deg | -15.0: 235 · -5.0: 194 · 5.0: 132 |
| size band | L1: 82 · L2: 94 · M1: 90 · M2: 84 · S1: 83 · S2: 68 · T1: 60 |
| target hole | H00: 82 · H18: 94 · H227: 60 · H30: 90 · H42: 84 · H60: 83 · H98: 68 |
| skipped (reason: n) | hole_outside_fov: 448 · sightline_blocked_by: 65 · camera_not_over_solid_plate: 45 · camera_inside_asset: 15 |

**expandedworld** — 574 approach frames + 96 occlusion frames

| axis | counts |
|---|---|
| standoff m | 0.3: 16 · 0.5: 24 · 0.7: 30 · 1.0: 39 · 1.5: 51 · 2.0: 64 · 3.0: 70 · 4.0: 91 · 6.0: 99 · 8.0: 90 |
| height m | 0.3: 188 · 0.6: 149 · 1.0: 108 · 1.5: 75 · 2.0: 54 |
| pitch deg | -15.0: 239 · -5.0: 199 · 5.0: 136 |
| size band | L1: 82 · L2: 92 · M1: 90 · M2: 84 · S1: 83 · S2: 68 · T1: 75 |
| target hole | H00: 82 · H21: 92 · H259: 75 · H30: 90 · H42: 84 · H60: 83 · H98: 68 |
| skipped (reason: n) | camera_inside_asset: 588 · hole_outside_fov: 446 · camera_not_over_solid_plate: 102 |

### Per-frame image facts

| | eworld2 | expandedworld |
|---|---|---|
| RGB mean (0–255) | min 136.2 · med 182.0 · max 230.4 | min 29.7 · med 42.0 · max 91.5 |
| fully saturated pixel fraction | min 0.0000 · med 0.1059 · max 0.7806 | min 0.0000 · med 0.0000 · max 0.0000 |
| finite-depth pixel fraction | min 0.364 · med 0.796 · max 0.997 | min 0.622 · med 0.971 · max 1.000 |
| depth min m | min 0.47 · med 1.27 · max 6.72 | min 0.23 · med 1.01 · max 6.72 |
| depth max m | min 13.2 · med 33.3 · max 42.6 | min 0.7 · med 35.5 · max 51.7 |

---

## 4. Verification

### 4.1 Depth is metric — checked in closed form, not by eyeball

The plate top is a known plane, so for every pixel the expected 32FC1 value is computable
with no free parameter: the camera-frame ray is `d = (1, −(u−cx)/f, −(v−cy)/f)`, Gazebo's
depth is the forward component, i.e. exactly the ray parameter `t` solving
`eye_z + t·(R d)_z = plate_top`. Pixels whose ray lands on **solid** plate are compared
against that (a 0.25 m gate removes pixels where an asset stands in the way, then the
median of the remainder is reported).

**The true nadir is never inside the frame in this pose band** — the steepest ray is
pitch + vfov/2 = 15° + 21.1° = **36.1° below horizontal**, nowhere near 90°. So the
single-pixel "known distance" check is done at the *bottom-centre* pixel, the steepest ray
that exists, and the plane check above (thousands of pixels per frame) is reported as the
stronger evidence.

### 4.2 RGB and depth are the same pixels — measured, not assumed

In `eworld2` nothing exists under the plate, so a ray that clears an opening's inner wall
leaves the scene: depth becomes `+inf` and RGB becomes the flat `<background>` grey (the
rays that hit the wall stay finite, which is why the void mask is smaller than the
opening). Those two masks are
produced by different code paths inside Gazebo, so their agreement is a direct
co-registration measurement:

    void = ¬isfinite(depth)  ·  bg = |RGB − modal void colour| ≤ 6 per channel  →  IoU, centroid offset

### 4.3 Exposure — the 08-24 blown-out floor recurs, and is reported, not fixed

The white concrete floor clips (all three channels ≥ 250) over part of many frames. **No
lighting, material, `<scene>` or exposure value was changed** (P2); the number is printed
below as it came out.

The clipping lands on the floor, not on the target. Splitting each frame into "inside the
opening" (pixels whose sight line passes through the target opening's disc) and "everything
else" gives the numbers below: the interior's median clipped fraction is **0**, because the
void renders at the background grey 178 and the visible inner wall is darker still. The
small non-zero maxima belong to distant sub-0.1 m² openings whose whole interior is a
handful of rim-blended pixels — restrict to frames whose interior is at least 500 sampled
pixels and the worst case falls to ~1 %. The hole-vs-floor contrast a detector needs is
intact; what is lost is floor texture detail, which matters for realism claims, not for
this experiment.

### 4.1 result — depth is metric

| check | frames | result |
|---|---:|---|
| plane check, per-frame median \|measured − expected\| | 1135 | median **0.0100 mm**, p99 0.0400 mm, **max 0.0500 mm** (median 7910 floor pixels per frame) |
| steepest-ray pixel (nadir substitute) | 901 | median **0.0100 mm**, **max 0.0300 mm** |
| true nadir pixel inside frame | 0 | geometrically impossible in this pose band (36.1° max) |

Gate was ≤ 20 mm; over the 1135 non-occlusion frames **not one frame exceeds 0.05 mm** — nearly three orders of magnitude inside the gate. The depth image is metres, unscaled.

The 91 `occlusion_intended` frames are reported separately because the test does not apply to them: their floor is deliberately behind a shelf, so the pixel the check samples is the shelf, not the floor. There the same statistic reads median 0.0100 mm with 6 of 91 frames over 20 mm (plane check) and 33 of 94 (steepest ray) — an occluder count, not a depth error.

### 4.2 result — RGB and depth are the same pixels

Over 200 `eworld2` frames with ≥ 500 void pixels: **IoU(void, background-RGB) median 0.9826**, p10 0.9644, min 0.4293 (that minimum is a single frame of the 0.10 × 0.10 m opening at 3 m, where the whole opening is a few thousand antialiased pixels); centroid offset **|dx| median 1.72 px, |dy| median 0.72 px** (p90 4.8 / 4.1 px). The residual is the antialiased rim (RGB blends it, depth does not) plus the odd surface elsewhere that happens to sit within 6 counts of grey 178, which is also what moves the centroid tail. A systematic RGB↔depth shift of more than a couple of pixels would cap the IoU well below 0.98 on the large-opening frames; it does not. The modal void colour is [178, 178, 178], i.e. the world's `<background>0.7` = 178 — so the part of the opening that is not inner wall really is open scene, and the two images agree on where it is.

### 4.3 result — exposure

| | value |
|---|---|
| frames with ≥ 2 % fully-saturated pixels | 453 / 1231 |
| frames with ≥ 20 % | 203 / 1231 |
| worst frame | 78.1 % of pixels clipped |
| saturated fraction **inside** the target opening | median **0.000000**, max 0.0741 over 57 sampled eworld2 frames |
| &nbsp;&nbsp;same, frames whose interior is ≥ 500 sampled pixels | median **0.000000**, max **0.012493** (26 frames) |
| saturated fraction **outside** it | median 0.093, max 0.768 |

---

## 5. Hand-off — what W2 and W3 must know

1. **Per-frame files.** `frames/<world>/<pose_id>.png` (RGB uint8), `.depth.npy`
   (float32 metres, `+inf` where a ray left the scene), `.pose.json` (the exact pose and
   per-frame image facts). `capture_manifest.json` is the index; `frames/SHA256SUMS.txt`
   pins every artefact.
2. **The projection model is exact.** Static camera models mean the poses in the manifest
   are ground truth, not estimates, and §4.1 shows the closed-form projection reproduces
   the rendered depth to a hundredth of a millimetre. W2 can compute the visible-hole mask
   analytically and cross-check it against the depth discontinuity (brief §7 (a′) vs (b)).
3. **`+inf` is signal, but it is not the whole interior.** A pixel inside an opening is
   `+inf` only if its ray clears the plate's cut face; measured on `eworld2` `H60`, that is
   **18 %** of interior pixels — the other **82 %** hit the 0.124 m inner wall and come back
   finite (hit z 0.02–0.11 m below the walking surface). "Interior mask" must therefore be
   *inside the opening's footprint*, not *non-finite depth*, or W2 undercounts by ~5×.
   And the footprint of a circular opening is the **disc, not its bbox** — 21.5 % of that
   bbox is bright floor (this stage hit that bug and fixed it; see §1). Over
   the GroundB slab (`expandedworld`, `H60` only) the far end of the interior is the floor
   at 0.09 m below the plate instead of open void.
4. **The plate is densely perforated** — 270 openings over 41 × 62 m, roughly one every
   2.5 m. At standoffs of 4–8 m several non-target openings are in frame. The GT for a
   frame is the **target** opening (`hole_id` in the manifest); other openings in the same
   frame are real negative obstacles that the detector may legitimately fire on, so W3's
   match rule must be stated explicitly, or those detections will be scored as false
   positives.
5. **Memorisation.** H00 / H30 / H60 / H98 are the same physical openings in both worlds
   (§2). Any world-split result must print this next to it.
6. **The occlusion frames are a separate population** (`occlusion_intended=true`,
   `occluder` names the asset actually first on the sight line, `occluder_planned` the one
   the pose was built around). They belong to the occlusion-axis experiment (brief ㉖),
   never to the size-axis curve that the V/E boundary is read from.
   ⚠ `standoff_m` means "to the near rim along the approach axis" only for the approach
   poses; for the occlusion poses it is an approximation. Use the manifest's
   `dist_cam_to_hole_centre_m` / `..._xy_m`, which are recomputed from the pose.
7. **Nothing in the baseline repo was touched.** The sha256 census in §6 is the proof.
8. **The YOLO environment is already built.** `vth/venv` (gitignored) holds
   python 3.10.12 · **torch 2.13.0+cu130** (CUDA sees the RTX 4090) · torchvision 0.28.0 ·
   **ultralytics 8.4.123** · numpy 2.2.6 · opencv 5.0.0 — every version is the pin from
   `experiments/dayrun_0820/code/yolo/requirements_yolo.txt`, which as a whole is a
   `pip freeze` of the ROS environment and cannot be installed verbatim. Versions are in
   `vth/venv_versions.json`. Do **not** use this venv to load the paper's own `best.pt`:
   that needs `Baseline_NegObs/neg_env` with its pinned torch 2.5.1.
9. **What "interior" means in this scene** — see §1: 0.124 m of cut face plus open void, and
   the stair corpus's 0.3 m rule does not transfer. Settle this before W2 counts pixels.
10. **The boundary is not ours to pick.** This stage reports geometry and frames only.

---

## 6. Integrity of the read-only baseline

Checked at the start of the stage and again at the end (`tools/verify_baseline.sh`).

**(a) The published table.** The six world/model hashes in `P0_BASELINE_DIFF.md` all match:

| file | sha256[:16] | start | end |
|---|---|:-:|:-:|
| `worlds/eworld2.world` | `9cb2a2c028cfaace` | OK | OK |
| `worlds/expandedworld.world` | `2a1956d3ea564a4f` | OK | OK |
| `worlds/smallest_world.world` | `5c88e743b07eb8f6` | OK | OK |
| `worlds/eworld.world` | `dc8b7a19f9895a72` | OK | OK |
| `models/large_holed_floor/model.sdf` | `c2751bac52bcd5dd` | OK | OK |
| `models/large_holed_floor/meshes/large_holed_floor.stl` | `ab75bc68feb3adae` | OK | OK |

**(b) A full census.** Six files is a narrow test, so this stage also snapshotted
sha256 of **every** file in the clone before starting
(`logs/BASELINE_SHA256_START.txt`, 769 files) and re-ran it at the end
(`logs/BASELINE_SHA256_END.txt`). **Differing entries: 0.**

**(c) `git` (read-only).** HEAD `408f023`; the only tracked-file modification is the
documented `bumperbot_localization/launch/nav.launch.py` one-word fix from 08-19.

**(d) 42 world copies.** `tools/verify_copies.py` strips the added camera block from every
copy and compares the remaining bytes to the source world: **42 checked, 0 deviations.**

### ⚠ One finding to hand to the owner, not to fix here

`P0_BASELINE_DIFF.md` itself is sitting **inside the baseline clone**, at

    Baseline_NegObs/src/negativeobstacleavoidandance/experiments/e1_0827/reports/P0_BASELINE_DIFF.md

(written 2026-08-28 01:10; it shows up as the untracked `experiments/` in `git status`).
It was clearly meant for `Practice_NegObs/experiments/e1_0827/reports/`, where it does not
exist — which is why the path this stage was handed did not resolve. The document's own
rule is "never edit upstream files in place", so having our report land in that tree is a
hygiene break, and moving or deleting it would itself be a write into the protected tree.
**Left exactly where it is; the owner decides.** It adds no tracked change and does not
affect any render.

---

## 7. The one thing that could break the experiment's reading

`eworld2` has `model://sun` plus a point light; `expandedworld` has **no light source at
all**, only `<scene><ambient>0.4`. The measured consequence, from the frames themselves:

Exact figures are the "Per-frame image facts" table in §3: `eworld2` frames sit around an
RGB mean of ~180 with frequent floor clipping, `expandedworld` frames around ~45 with no
clipping observed at all.

That is roughly a **4× brightness gap between the training world and the evaluation
world**. The brief's world-split (train `eworld2` / evaluate `expandedworld`, or the
reverse, §7 3-3, ❓-4) therefore does not isolate "does the detector generalise across
scenes" — it also swaps the illumination regime. W3 must either print this next to any
cross-world number, or the split direction has to be decided with it in view. **Not a
thing this stage fixes**: changing a light would edit the paper's world (P2), and the
owner has not been asked. Recorded, measured, handed up.
