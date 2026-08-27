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

