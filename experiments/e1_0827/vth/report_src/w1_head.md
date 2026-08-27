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

