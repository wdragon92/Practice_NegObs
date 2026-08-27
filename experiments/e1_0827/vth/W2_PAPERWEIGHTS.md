# W2_PAPERWEIGHTS — how many visible hole pixels does the paper's own YOLO need?

Stage W2 of the V-threshold experiment (`Docs/briefs/edge_relabel_brief_v6.md` §7, warehouse
A-track). Scope fence, unchanged: **the YOLO stage's detection limit only** — no navigation,
no depth-strip validation, no LiDAR fusion, no training, no re-labelling by hand.

Input: the 1231 RGB-D frames of W1 (`W1_CAPTURE.md`). Output: `labels.csv` (one analytic
ground-truth row per frame), `runs/yolo_paper/detections.json` (the paper's released
weights run on every frame), the tables below and `plots/*.png`.

**P1 stands: this stage does not choose the boundary.** Everything below is "what was
measured"; the V/E tier cut is the owner's.

---

## 0. The three numbers that matter

1. **The label works.** For every frame the visible hole interior was computed from the
   depth image + the exact camera pose + the 1 cm footprint raster of the plate mesh — no
   hand annotation. It agrees with a closed-form projection of the opening polygon to
   **−0.47 % (median, p5..p95 ±2.7 %)** over the 633 frames where the whole opening is
   inside the image.
2. **The paper's released detector is far weaker on this corpus than its published
   val mAP50 0.935 suggests** — and the reason is measurable: it is **pose-bound**. Pooled
   over the whole brief pose band (0.3–2.0 m camera height) it fires on the hole in
   **6.9 %** of frames (conf ≥ 0.25). Restricted to the pose closest to the paper's own
   robot (camera **0.125 m** up, **14.95°** nose-down → grid point 0.3 m / −15°) it reaches
   **0.86** at 0.5–0.7 m standoff in the training world, and **0.00** beyond 3 m.
3. **A usable transition exists, and it is a floor, not a ceiling.** In the paper-pose
   subset the detector never once fired on a hole whose visible interior was below
   **2515 px** (46 frames, conf ≥ 0.25) or whose GT box was shorter than **19 px**. Pooled
   over all poses the same never-fires ceiling is **707 px / 10 px** (321 / 315 frames).

---

## 1. The label — what "visible hole interior" means here and how it was computed

W1 §5-9 left this open (`VTH_CONST` ❓W1-4): the stair corpus defines 속 as "a surface
≥ 0.3 m below the walking surface", and the warehouse plate is only 0.12432 m thick, so
that rule returns **zero interior pixels for every warehouse opening**. This stage used the
warehouse substitution W1 proposed, and states it plainly:

> **interior = the pixels whose sight ray passes through the opening's footprint and whose
> back-projected 3D point is below the walking surface.** Cut face and open void both count.

Operationally, per pixel:

| step | rule | tag |
|---|---|---|
| a | ray → the `z = plate_top` plane; the crossing point must fall inside the target opening's exact 1 cm footprint raster | [방법] |
| b | and the depth must be `+inf` (the ray left the scene) **or** back-project to `z < plate_top − 0.01 m` | [방법] `INT_Z_MARGIN` |

(a) alone is the **analytic footprint** `foot_area_px` (unoccluded, geometry only);
(a)+(b) is the **visible interior** `int_area_px`. From the mask: `int_w_px`, `int_h_px`,
the GT box `gt_x0..gt_y1`, and `void_frac` (share of the interior that is `+inf`).

**Why the xy test is done at the plane crossing and not at the hit point.** 18–82 % of
interior rays (size-dependent, W1 §1) land on the plate's vertical **cut face**, whose xy
lies exactly *on* the footprint boundary — a 1 cm raster lookup there is a coin flip, and
over the GroundB slab the hit point is displaced up to 0.36 m from where the ray entered.
Measured: the hit-point variant agrees with the plane-crossing variant only to
**IoU median 0.626, p10 0.037** on near frames, i.e. it silently throws away most of the
cut face. The plane crossing is where the ray *enters* the opening and is the stable test.

**Why a footprint pixel can fail to be interior — the two causes are separated.**

| column | meaning | measured |
|---|---|---|
| `occ_above_px` / `occ_frac_asset` | the ray was stopped **above** the walking surface → a real occluder | **0.0000 on all 1135 size-axis frames** (max 0.0000); median **1.000** on the occlusion set |
| `graze_px` | it hit the far cut face within `INT_Z_MARGIN` of the top (a shallow grazing ray) | median 11.6 % of the footprint on size-axis frames — a geometric artefact of the 1 cm margin, **not** occlusion |

`occluded_frac = 1 − int/foot` therefore mixes the two and must not be read as occlusion;
`occ_frac_asset` is the occlusion measure.

**rim_visible (E-like frames).** The footprint polygon is projected to pixels and stroked
±2 px [방법]; a rim pixel counts as visible when its measured depth matches the closed-form
plate-plane depth within **0.05 m** [방법]. `rim_visible = any such pixel`.

**Other openings.** The plate carries 270 openings, so 24–61 non-target openings (median 30)
project into a typical frame. `labels_otherholes.json.gz` stores their projected boxes per
frame so a detection on one of them is scored `other_hole`, not `background`.

**Verification of the label**

| check | result |
|---|---|
| rows in `labels.csv` == frames in the manifest | **1231 == 1231** |
| the bbox crop of the 1 cm raster == each opening's measured cell count | **270 / 270 openings, 0 mismatches** |
| `foot_area_px` vs the closed-form shoelace area of the projected polygon (633 fully-in-frame frames) | median **−0.47 %**, p5 −2.7 %, p95 +2.7 % |
| masks non-empty on near frames | min `int_area_px` at 0.3 m standoff = **1259 px**; 0 zero-interior frames at ≤ 0.3 m |
| mask overlays (12 PNGs, `runs/masks/`) | opened and checked; the mask covers cut face + void and stops at the rim |

---

## 2. The detector — the paper's own weights, the paper's own input pipeline

| item | value | tag |
|---|---|---|
| weights | `Baseline_NegObs/.../bot_camera/model/best.pt`, **read in place, never copied** | [문헌] |
| sha256 | `f95126cee2b348acfa68da2f7f4da40eb253b790a37055c58f25ee29c6e5f1b6` | [실측] |
| classes | `nc=1`, `{0: negative_obstacle}` | [실측] |
| environment | `Baseline_NegObs/neg_env` — python 3.10.12, torch **2.5.1+cu124**, ultralytics **8.0.196**, RTX 4090 | [기존값] |
| imgsz | 640 (the weights' own train setting) | [문헌] |
| conf floor at predict | 0.05, thresholds applied at read time | [방법] |
| operating thresholds | **0.25** (= ultralytics' predict default, i.e. what `self.model(image)` uses), plus 0.10 and 0.50 | [도구기본값 + 2] |
| match rule | box IoU ≥ **0.50** | [문헌 PASCAL VOC / COCO] |
| wall time | 22 s for 1231 frames × 3 arms on the GPU (under `flock`) | [실측] |

**The input pipeline replicates `bot_camera/bot_camera/clean_yolo.py::_process_image` step
for step**, including one step the 08-24 track missed:

```
frame  = bgr8 image                                   (cv_bridge  -> here cv2.imread)
verts  = create_trapezium_vertices(1280, 720)         TOP 0.20 W / BOTTOM 0.80 W / H 0.7 H
                                                      -> (512,216) (768,216) (1152,720) (128,720)
cv2.polylines(frame, [verts], True, (0,255,0), 2)     <- the node DRAWS THE ROI ON THE FRAME
mask   = fillPoly(zeros, [verts], 255)
roi    = cv2.bitwise_and(frame, frame, mask=mask)     <- YOLO sees the MASKED frame
results= self.model(roi)                              <- ultralytics defaults (conf 0.25)
keep only boxes whose CENTRE is inside the trapezium  (cv2.pointPolygonTest >= 0)
```

Three arms, one image load each:

| arm | what the network was shown | boxes at the 0.05 floor |
|---|---|---|
| `roi` | node-exact: green outline drawn, then masked — **primary** | 1262 |
| `roi_nopoly` | masked, outline **not** drawn (what `gazebo_wh_0824/tools/yolo_paper.py` ran) | 2597 |
| `full` | unmasked frame (fairness control) | 6454 |

The centre-in-ROI rule is applied to every arm, so the arms differ only in the network's input.

---

## 3. The finding that forces two match criteria

At IoU ≥ 0.50 the pooled detection rate is 2.5 % — but the detector is visibly finding
holes at 0.8+ confidence (see `W2_samples.jpg`). The boxes are simply **too tall**: on the
75 size-axis frames where a box's centre lands inside the GT box, the median detected box is
**1.60×** the GT height (but only 1.13× its width), and **29 of 75** start within 12 px of
the ROI mask's top edge at y = 216. The black masked-out region above the trapezium merges
with the dark hole and drags the box up. Median IoU on those frames is **0.465** — just
under the bar.

So every curve below is reported twice:

| criterion | rule | tag |
|---|---|---|
| `iou50` | IoU ≥ 0.50 — **primary** | [문헌 PASCAL/COCO] |
| `centre` | the box centre falls inside the GT box: "did it point at the hole at all", localisation-free | [방법] |

`iou25` (IoU ≥ 0.25) is computed too and sits between them; it is in the CSV-level results
but omitted from the tables to keep them readable.

**Read the centre curve for "does the detector see the hazard"; read the IoU-0.50 curve for
"is the box good enough to act on".** They differ by ~5× on this corpus and that gap is
itself a result.

---

## 4. Headline: the paper-pose subset is where the curve is readable

The paper's robot carries the camera at **0.125 m** above the walking surface
(`bumperbot.urdf.xacro`: base_footprint→base_link 0.033 + base_link→camera_link 0.092)
tilted **0.261 rad = 14.95° nose-down** [실측]. The brief's pose band starts at 0.3 m, so
the closest grid point is **height 0.3 m / pitch −15°** — the tilt matches to 0.05°, the
height is 2.4× too high. Rate collapses with camera height (§3b table, `p11`), so the
pooled curve is dominated by poses this detector was never trained for.

In that subset (124 frames with a GT box), conf ≥ 0.25, arm `roi`, centre-hit:

| standoff | 0.3 | 0.5 | 0.7 | 1.0 | 1.5 | 2.0 | 3.0 | 4.0 | 6.0 | 8.0 |
|---|---|---|---|---|---|---|---|---|---|---|
| rate (both worlds) | 0.333 | 0.643 | 0.571 | 0.500 | 0.357 | 0.143 | **0.000** | 0.000 | 0.000 | 0.000 |
| median int_area_px | 224436 | 141229 | 68039 | 29566 | 10718 | 4881 | 1999 | 753 | 195 | 68 |
| `eworld2` only | 0.50 | **0.86** | **0.86** | 0.57 | 0.57 | 0.29 | 0.00 | 0.00 | 0.00 | 0.00 |

The world split is large and confounded with the 4× brightness gap W1 §7 flagged
(`eworld2` has a sun, `expandedworld` has **no light source at all**): at 100k–500k visible
px the paper-pose rate is **0.818 in `eworld2` vs 0.455 in `expandedworld`**, and below
3162 px `expandedworld` is 0.000 everywhere. `eworld2` is also the world whose openings the
model most plausibly trained on. **Any cross-world reading must carry both caveats.**

---

## 5. False positives

At conf ≥ 0.25, arm `roi`, over the 1135 size-axis frames: **75 hits on the target** against
**569 background boxes** and **0** boxes matching another opening's projected footprint.
On the 45 frames with no visible interior at all, 15 still produce a box. The `roi_nopoly`
arm (no green outline drawn) produces ~2× the boxes of the node-exact arm at every
threshold — drawing the ROI outline before masking measurably suppresses detections, which
is worth reporting back because the 08-24 track ran the un-drawn variant.

`other_hole` staying at 0 does not mean the detector never fires on a non-target opening —
it means such a box rarely reaches IoU ≥ 0.5 with that opening's **full analytic** footprint
(the visible part is smaller). Treat the split as a lower bound on `other_hole`.

---

## 6. Occlusion subset (brief ㉖) — a separate population, and it is silent

96 frames, `expandedworld` only, 11 distinct real occluders, no scene edit. 62 of 96 have
**zero** visible interior (`occ_frac_asset` = 1.000). Of the 34 with any visible interior,
the detector scored **0 hits under either criterion at every threshold**. There is no
occlusion *curve* here — only the fact that partial occlusion of an already-small opening
in the dark world puts it entirely below the detector's floor. The per-occluder table is
in §6 below.

---

## 7. Gates

| gate | result |
|---|---|
| `labels.csv` rows == frames | **1231 == 1231** — PASS |
| masks non-empty on near frames | min 1259 px at 0.3 m standoff; 0 empty masks below 0.5 m — PASS |
| inference ran on all frames | 1231 / 1231 × 3 arms, `runs/yolo_paper/run.json` — PASS |
| plots exist | 11 PNGs in `plots/` (552 KiB total) — PASS |

## 8. Plot list

| file | what it shows |
|---|---|
| `p1_rate_vs_area.png` | rate vs `int_area_px`, 3 conf thresholds × 2 match criteria — the main curve |
| `p2_rate_vs_h.png` | rate vs `int_h_px` (GT box height) |
| `p3_rate_vs_w.png` | rate vs `int_w_px` (GT box width) |
| `p4_rate_vs_standoff.png` | rate vs standoff to the near rim |
| `p5_bysize.png` | stratified small / medium / large by equivalent radius |
| `p6_byworld.png` | stratified `eworld2` vs `expandedworld` (carries the brightness gap) |
| `p7_byarm.png` | node ROI vs mask-without-outline vs full frame |
| `p8_area_vs_standoff.png` | the label distribution itself, `int_area_px` vs standoff |
| `p9_occlusion.png` | occlusion subset — not one detection in any bin |
| `p10_paperpose.png` | **the paper-pose subset — the readable curve** |
| `p11_pose_dependence.png` | rate vs camera height and pitch; the paper's own 0.125 m marked |
| `W2_samples.jpg` | 8 frames of `eworld2` H00 at the paper pose, 0.5 → 6 m, GT green / model red |

## 9. Open items handed to the owner (not decided here)

| # | item |
|---|---|
| ❓W2-1 | The warehouse redefinition of 속 (footprint interior = cut face + void) is now *used*, not just proposed. Approve or replace — every number in this file rests on it (❓W1-4). |
| ❓W2-2 | `INT_Z_MARGIN = 0.01 m` costs a median 11.6 % of the analytic footprint as a grazing band at the far rim on low, distant poses. Accept, or drop the margin? |
| ❓W2-3 | Report the boundary axis on the **pooled** pose band (brief §7's band, rate ≤ 0.46 everywhere) or on the **paper-pose** subset (rate up to 0.86, but n = 124)? They give ceilings of 707 px and 2515 px respectively. |
| ❓W2-4 | The paper's robot camera is at 0.125 m; the brief's band starts at 0.3 m. Nothing in this corpus matches the deployed geometry. Add a 0.125 m row to the capture grid in a later stage? |
| ❓W2-5 | The `roi` vs `roi_nopoly` gap (drawing the green ROI outline halves the boxes) means the 08-24 track and this stage ran different pipelines. Which is canonical for the paper comparison? |
| ❓W2-6 | The `eworld2` / `expandedworld` gap is confounded three ways (brightness, memorised openings H00/H30/H60/H98, wall geometry). Keep the world split at all (❓W1-5)? |

---

# Tables

populations: all 1231 | size-axis (occlusion_intended=false) 1135, with a GT box 1090 | occlusion set 96, with a GT box 34

## 1. Visible interior pixels vs standoff (size-axis population)

| standoff m | n | min | p25 | median | p75 | max | int_area_px = 0 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.3 | 33 | 1259 | 22534 | 96788 | 191732 | 408443 | 0 |
| 0.5 | 48 | 0 | 23637 | 62968 | 144067 | 265826 | 1 |
| 0.7 | 60 | 1435 | 22459 | 42818 | 83234 | 171993 | 0 |
| 1 | 78 | 362 | 10774 | 30710 | 60768 | 106058 | 0 |
| 1.5 | 102 | 270 | 5670 | 12585 | 24043 | 64652 | 0 |
| 2 | 129 | 0 | 2635 | 7866 | 14778 | 43439 | 2 |
| 3 | 140 | 0 | 1563 | 3934 | 7890 | 21694 | 6 |
| 4 | 182 | 0 | 536 | 1527 | 3792 | 11953 | 7 |
| 6 | 198 | 0 | 147 | 525 | 1272 | 4198 | 14 |
| 8 | 165 | 0 | 59 | 176 | 494 | 1886 | 15 |

**median int_area_px by size band x standoff** (blank = no frame)

| band | r_eq m | 0.3 m | 0.5 m | 0.7 m | 1 m | 1.5 m | 2 m | 3 m | 4 m | 6 m | 8 m |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| L1 | 0.484 | 119918 | 102574 | 95444 | 67926 | 24193 | 23329 | 8746 | 6306 | 2106 |  |
| L2 | 0.446 | 149433 | 117695 | 88419 | 61139 | 23342 | 21132 | 7766 | 5308 | 1833 | 792 |
| M1 | 0.329 | 96788 | 97216 | 77367 | 37504 | 13121 | 12619 | 4412 | 3103 | 1003 | 436 |
| M2 | 0.279 | 124044 | 91350 | 67653 | 30138 | 15760 | 9523 | 3347 | 2315 | 800 | 332 |
| S1 | 0.205 | 69766 | 57137 | 39506 | 16799 | 8566 | 5216 | 1866 | 1237 | 378 | 153 |
| S2 | 0.141 | 52006 | 36034 | 22459 | 8984 | 4430 | 2635 |  | 603 | 189 | 59 |
| T1 | 0.053 |  | 8772 | 3666 | 1252 | 548 | 290 | 86 | 22 | 14 | 0 |

**E-like frames** — int_area_px == 0 while the rim line IS visible: **49** of 107 zero-interior frames (size-axis 45, occlusion 4).

| world | band | n int=0 | n rim_visible |
|---|---|---:|---:|
| eworld2 | S2 | 4 | 4 |
| eworld2 | T1 | 14 | 14 |
| expandedworld | L1 | 9 | 0 |
| expandedworld | L2 | 12 | 1 |
| expandedworld | M1 | 12 | 0 |
| expandedworld | M2 | 12 | 0 |
| expandedworld | S1 | 15 | 2 |
| expandedworld | S2 | 7 | 6 |
| expandedworld | T1 | 22 | 22 |

## 2. Why two criteria — the detector's boxes run tall

On the 75 size-axis frames where a kept box's centre lands inside the GT box (arm roi, tau 0.25):

| quantity | median | p10 | p90 |
|---|---:|---:|---:|
| det box height / GT height | 1.60 | 0.81 | 2.78 |
| det box width / GT width | 1.13 | 0.69 | 1.51 |
| det box top − ROI top edge (px) | 75 | -6 | 316 |
| IoU with GT | 0.465 | 0.172 | 0.597 |

29 of 75 of those boxes start within 12 px of the ROI mask's top edge (y = 216) — the box is dragged up to the black mask boundary. That is why the IoU-0.50 rate and the centre rate differ by ~5x below.

## 3. Detection rate vs visible pixels — arm `roi` (node-exact)


**int_area_px · conf ≥ 0.10**

| bin px | n frames | IoU≥0.50 | rate | centre-hit | rate |
|---|---:|---:|---:|---:|---:|
| 1–10 | 0 | 0 |  | 0 |  |
| 10–32 | 37 | 0 | 0.000 | 0 | 0.000 |
| 32–100 | 63 | 0 | 0.000 | 0 | 0.000 |
| 100–316 | 110 | 0 | 0.000 | 0 | 0.000 |
| 316–1000 | 167 | 0 | 0.000 | 2 | 0.012 |
| 1000–3162 | 182 | 0 | 0.000 | 9 | 0.049 |
| 3162–10000 | 206 | 4 | 0.019 | 21 | 0.102 |
| 10000–31623 | 170 | 9 | 0.053 | 22 | 0.129 |
| 31623–100000 | 105 | 10 | 0.095 | 24 | 0.229 |
| 100000–500000 | 50 | 9 | 0.180 | 23 | 0.460 |

**int_area_px · conf ≥ 0.25**

| bin px | n frames | IoU≥0.50 | rate | centre-hit | rate |
|---|---:|---:|---:|---:|---:|
| 1–10 | 0 | 0 |  | 0 |  |
| 10–32 | 37 | 0 | 0.000 | 0 | 0.000 |
| 32–100 | 63 | 0 | 0.000 | 0 | 0.000 |
| 100–316 | 110 | 0 | 0.000 | 0 | 0.000 |
| 316–1000 | 167 | 0 | 0.000 | 1 | 0.006 |
| 1000–3162 | 182 | 0 | 0.000 | 6 | 0.033 |
| 3162–10000 | 206 | 3 | 0.015 | 15 | 0.073 |
| 10000–31623 | 170 | 9 | 0.053 | 15 | 0.088 |
| 31623–100000 | 105 | 8 | 0.076 | 19 | 0.181 |
| 100000–500000 | 50 | 7 | 0.140 | 19 | 0.380 |

**int_area_px · conf ≥ 0.50**

| bin px | n frames | IoU≥0.50 | rate | centre-hit | rate |
|---|---:|---:|---:|---:|---:|
| 1–10 | 0 | 0 |  | 0 |  |
| 10–32 | 37 | 0 | 0.000 | 0 | 0.000 |
| 32–100 | 63 | 0 | 0.000 | 0 | 0.000 |
| 100–316 | 110 | 0 | 0.000 | 0 | 0.000 |
| 316–1000 | 167 | 0 | 0.000 | 1 | 0.006 |
| 1000–3162 | 182 | 0 | 0.000 | 5 | 0.027 |
| 3162–10000 | 206 | 2 | 0.010 | 11 | 0.053 |
| 10000–31623 | 170 | 8 | 0.047 | 12 | 0.071 |
| 31623–100000 | 105 | 8 | 0.076 | 18 | 0.171 |
| 100000–500000 | 50 | 5 | 0.100 | 17 | 0.340 |

**int_h_px · conf ≥ 0.10**

| bin px | n frames | IoU≥0.50 | rate | centre-hit | rate |
|---|---:|---:|---:|---:|---:|
| 1–2 | 49 | 0 | 0.000 | 0 | 0.000 |
| 2–4 | 84 | 0 | 0.000 | 0 | 0.000 |
| 4–8 | 117 | 0 | 0.000 | 0 | 0.000 |
| 8–16 | 187 | 0 | 0.000 | 4 | 0.021 |
| 16–32 | 179 | 0 | 0.000 | 5 | 0.028 |
| 32–64 | 202 | 6 | 0.030 | 29 | 0.144 |
| 64–128 | 161 | 9 | 0.056 | 27 | 0.168 |
| 128–256 | 95 | 15 | 0.158 | 27 | 0.284 |
| 256–512 | 16 | 2 | 0.125 | 9 | 0.562 |
| 512–1281 | 0 | 0 |  | 0 |  |

**int_h_px · conf ≥ 0.25**

| bin px | n frames | IoU≥0.50 | rate | centre-hit | rate |
|---|---:|---:|---:|---:|---:|
| 1–2 | 49 | 0 | 0.000 | 0 | 0.000 |
| 2–4 | 84 | 0 | 0.000 | 0 | 0.000 |
| 4–8 | 117 | 0 | 0.000 | 0 | 0.000 |
| 8–16 | 187 | 0 | 0.000 | 2 | 0.011 |
| 16–32 | 179 | 0 | 0.000 | 4 | 0.022 |
| 32–64 | 202 | 5 | 0.025 | 19 | 0.094 |
| 64–128 | 161 | 8 | 0.050 | 20 | 0.124 |
| 128–256 | 95 | 12 | 0.126 | 21 | 0.221 |
| 256–512 | 16 | 2 | 0.125 | 9 | 0.562 |
| 512–1281 | 0 | 0 |  | 0 |  |

**int_h_px · conf ≥ 0.50**

| bin px | n frames | IoU≥0.50 | rate | centre-hit | rate |
|---|---:|---:|---:|---:|---:|
| 1–2 | 49 | 0 | 0.000 | 0 | 0.000 |
| 2–4 | 84 | 0 | 0.000 | 0 | 0.000 |
| 4–8 | 117 | 0 | 0.000 | 0 | 0.000 |
| 8–16 | 187 | 0 | 0.000 | 2 | 0.011 |
| 16–32 | 179 | 0 | 0.000 | 2 | 0.011 |
| 32–64 | 202 | 4 | 0.020 | 16 | 0.079 |
| 64–128 | 161 | 7 | 0.043 | 16 | 0.099 |
| 128–256 | 95 | 10 | 0.105 | 20 | 0.211 |
| 256–512 | 16 | 2 | 0.125 | 8 | 0.500 |
| 512–1281 | 0 | 0 |  | 0 |  |

**int_w_px · conf ≥ 0.10**

| bin px | n frames | IoU≥0.50 | rate | centre-hit | rate |
|---|---:|---:|---:|---:|---:|
| 1–2 | 0 | 0 |  | 0 |  |
| 2–4 | 0 | 0 |  | 0 |  |
| 4–8 | 0 | 0 |  | 0 |  |
| 8–16 | 24 | 0 | 0.000 | 0 | 0.000 |
| 16–32 | 63 | 0 | 0.000 | 0 | 0.000 |
| 32–64 | 170 | 0 | 0.000 | 1 | 0.006 |
| 64–128 | 244 | 1 | 0.004 | 11 | 0.045 |
| 128–256 | 277 | 6 | 0.022 | 24 | 0.087 |
| 256–512 | 198 | 11 | 0.056 | 31 | 0.157 |
| 512–1281 | 114 | 14 | 0.123 | 34 | 0.298 |

**int_w_px · conf ≥ 0.25**

| bin px | n frames | IoU≥0.50 | rate | centre-hit | rate |
|---|---:|---:|---:|---:|---:|
| 1–2 | 0 | 0 |  | 0 |  |
| 2–4 | 0 | 0 |  | 0 |  |
| 4–8 | 0 | 0 |  | 0 |  |
| 8–16 | 24 | 0 | 0.000 | 0 | 0.000 |
| 16–32 | 63 | 0 | 0.000 | 0 | 0.000 |
| 32–64 | 170 | 0 | 0.000 | 0 | 0.000 |
| 64–128 | 244 | 1 | 0.004 | 7 | 0.029 |
| 128–256 | 277 | 5 | 0.018 | 18 | 0.065 |
| 256–512 | 198 | 9 | 0.045 | 21 | 0.106 |
| 512–1281 | 114 | 12 | 0.105 | 29 | 0.254 |

**int_w_px · conf ≥ 0.50**

| bin px | n frames | IoU≥0.50 | rate | centre-hit | rate |
|---|---:|---:|---:|---:|---:|
| 1–2 | 0 | 0 |  | 0 |  |
| 2–4 | 0 | 0 |  | 0 |  |
| 4–8 | 0 | 0 |  | 0 |  |
| 8–16 | 24 | 0 | 0.000 | 0 | 0.000 |
| 16–32 | 63 | 0 | 0.000 | 0 | 0.000 |
| 32–64 | 170 | 0 | 0.000 | 0 | 0.000 |
| 64–128 | 244 | 0 | 0.000 | 5 | 0.020 |
| 128–256 | 277 | 4 | 0.014 | 14 | 0.051 |
| 256–512 | 198 | 9 | 0.045 | 19 | 0.096 |
| 512–1281 | 114 | 10 | 0.088 | 26 | 0.228 |

**standoff m · conf ≥ 0.10**

| standoff m | n frames | IoU≥0.50 | rate | centre-hit | rate |
|---:|---:|---:|---:|---:|---:|
| 0.3 | 33 | 1 | 0.030 | 6 | 0.182 |
| 0.5 | 47 | 5 | 0.106 | 10 | 0.213 |
| 0.7 | 60 | 9 | 0.150 | 16 | 0.267 |
| 1 | 78 | 7 | 0.090 | 19 | 0.244 |
| 1.5 | 102 | 5 | 0.049 | 17 | 0.167 |
| 2 | 127 | 3 | 0.024 | 14 | 0.110 |
| 3 | 134 | 1 | 0.007 | 9 | 0.067 |
| 4 | 175 | 1 | 0.006 | 7 | 0.040 |
| 6 | 184 | 0 | 0.000 | 3 | 0.016 |
| 8 | 150 | 0 | 0.000 | 0 | 0.000 |

**standoff m · conf ≥ 0.25**

| standoff m | n frames | IoU≥0.50 | rate | centre-hit | rate |
|---:|---:|---:|---:|---:|---:|
| 0.3 | 33 | 1 | 0.030 | 4 | 0.121 |
| 0.5 | 47 | 5 | 0.106 | 10 | 0.213 |
| 0.7 | 60 | 7 | 0.117 | 12 | 0.200 |
| 1 | 78 | 5 | 0.064 | 15 | 0.192 |
| 1.5 | 102 | 5 | 0.049 | 14 | 0.137 |
| 2 | 127 | 3 | 0.024 | 9 | 0.071 |
| 3 | 134 | 1 | 0.007 | 6 | 0.045 |
| 4 | 175 | 0 | 0.000 | 4 | 0.023 |
| 6 | 184 | 0 | 0.000 | 1 | 0.005 |
| 8 | 150 | 0 | 0.000 | 0 | 0.000 |

**standoff m · conf ≥ 0.50**

| standoff m | n frames | IoU≥0.50 | rate | centre-hit | rate |
|---:|---:|---:|---:|---:|---:|
| 0.3 | 33 | 0 | 0.000 | 3 | 0.091 |
| 0.5 | 47 | 4 | 0.085 | 9 | 0.191 |
| 0.7 | 60 | 7 | 0.117 | 11 | 0.183 |
| 1 | 78 | 5 | 0.064 | 14 | 0.179 |
| 1.5 | 102 | 4 | 0.039 | 13 | 0.127 |
| 2 | 127 | 3 | 0.024 | 7 | 0.055 |
| 3 | 134 | 0 | 0.000 | 4 | 0.030 |
| 4 | 175 | 0 | 0.000 | 3 | 0.017 |
| 6 | 184 | 0 | 0.000 | 0 | 0.000 |
| 8 | 150 | 0 | 0.000 | 0 | 0.000 |

### stratified by physical hole size (conf ≥ 0.25, arm roi, centre-hit / IoU≥0.50)

| int_area_px bin | large | medium | small |
|---|---|---|---|
| 1–10 | – | – | – |
| 10–32 | n=2 0.00 / 0.00 | n=4 0.00 / 0.00 | n=31 0.00 / 0.00 |
| 32–100 | – | n=26 0.00 / 0.00 | n=37 0.00 / 0.00 |
| 100–316 | n=6 0.00 / 0.00 | n=50 0.00 / 0.00 | n=54 0.00 / 0.00 |
| 316–1000 | n=24 0.00 / 0.00 | n=104 0.01 / 0.00 | n=39 0.00 / 0.00 |
| 1000–3162 | n=60 0.03 / 0.00 | n=96 0.04 / 0.00 | n=26 0.00 / 0.00 |
| 3162–10000 | n=84 0.05 / 0.00 | n=96 0.07 / 0.02 | n=26 0.15 / 0.04 |
| 10000–31623 | n=80 0.06 / 0.04 | n=80 0.12 / 0.07 | n=10 0.00 / 0.00 |
| 31623–100000 | n=55 0.18 / 0.04 | n=46 0.20 / 0.13 | n=4 0.00 / 0.00 |
| 100000–500000 | n=38 0.37 / 0.11 | n=12 0.42 / 0.25 | – |

### stratified by world (conf ≥ 0.25, arm roi, centre-hit / IoU≥0.50)

| int_area_px bin | eworld2 | expandedworld |
|---|---|---|
| 1–10 | – | – |
| 10–32 | n=15 0.00 / 0.00 | n=22 0.00 / 0.00 |
| 32–100 | n=32 0.00 / 0.00 | n=31 0.00 / 0.00 |
| 100–316 | n=56 0.00 / 0.00 | n=54 0.00 / 0.00 |
| 316–1000 | n=82 0.01 / 0.00 | n=85 0.00 / 0.00 |
| 1000–3162 | n=90 0.07 / 0.00 | n=92 0.00 / 0.00 |
| 3162–10000 | n=105 0.14 / 0.03 | n=101 0.00 / 0.00 |
| 10000–31623 | n=84 0.15 / 0.10 | n=86 0.02 / 0.01 |
| 31623–100000 | n=54 0.24 / 0.15 | n=51 0.12 / 0.00 |
| 100000–500000 | n=25 0.52 / 0.28 | n=25 0.24 / 0.00 |

### centre-hit rate by size band and standoff (conf ≥ 0.25, arm roi)

| band | 0.3 m | 0.5 m | 0.7 m | 1 m | 1.5 m | 2 m | 3 m | 4 m | 6 m | 8 m |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| L1 | 0.20 | 0.17 | 0.25 | 0.33 | 0.17 | 0.10 | 0.04 | 0.08 | 0.03 |  |
| L2 | 0.00 | 0.33 | 0.17 | 0.33 | 0.17 | 0.05 | 0.04 | 0.04 | 0.00 | 0.00 |
| M1 | 0.17 | 0.25 | 0.20 | 0.25 | 0.06 | 0.11 | 0.00 | 0.00 | 0.00 | 0.00 |
| M2 | 0.00 | 0.17 | 0.12 | 0.00 | 0.08 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| S1 | 0.25 | 0.17 | 0.25 | 0.25 | 0.50 | 0.22 | 0.18 | 0.04 | 0.00 | 0.00 |
| S2 | 0.00 | 0.00 | 0.00 | 0.10 | 0.00 | 0.00 |  | 0.00 | 0.00 | 0.00 |
| T1 |  | 0.50 | 0.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |

### centre-hit rate by camera height x pitch (conf ≥ 0.25, arm roi) — n in brackets

| height above walking surface | pitch −15° | pitch −5° | pitch +5° |
|---:|---:|---:|---:|
| 0.3 m | 0.282 (124) | 0.085 (118) | 0.010 (103) |
| 0.6 m | 0.119 (118) | 0.030 (99) | 0.000 (66) |
| 1 m | 0.085 (94) | 0.014 (70) | 0.000 (46) |
| 1.5 m | 0.014 (71) | 0.000 (51) | 0.000 (25) |
| 2 m | 0.037 (54) | 0.000 (38) | 0.000 (13) |

The paper's own camera sits **0.125 m** above the walking surface at **14.95°** nose-down (bumperbot.urdf.xacro, [실측]). The closest point of the brief's pose grid is height 0.3 m / pitch -15° — the tilt matches to 0.05°, the height is 2.4x too high. Rate falls off hard with camera height, so the aggregate rate above is dominated by poses this detector was never trained for.

### PAPER-POSE SUBSET — height 0.3 m, pitch -15° (124 frames with a GT box)

This is the subset whose camera geometry is closest to the paper's own robot; read the detection limit here, not off the pooled curve.

| int_area_px bin | n | centre-hit | rate | IoU≥0.50 | rate | eworld2 rate | expandedworld rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| 10–32 | 2 | 0 | 0.000 | 0 | 0.000 | 0.000 (n=1) | 0.000 (n=1) |
| 32–100 | 10 | 0 | 0.000 | 0 | 0.000 | 0.000 (n=5) | 0.000 (n=5) |
| 100–316 | 12 | 0 | 0.000 | 0 | 0.000 | 0.000 (n=6) | 0.000 (n=6) |
| 316–1000 | 10 | 0 | 0.000 | 0 | 0.000 | 0.000 (n=5) | 0.000 (n=5) |
| 1000–3162 | 16 | 1 | 0.062 | 0 | 0.000 | 0.125 (n=8) | 0.000 (n=8) |
| 3162–10000 | 16 | 3 | 0.188 | 1 | 0.062 | 0.375 (n=8) | 0.000 (n=8) |
| 10000–31623 | 18 | 6 | 0.333 | 4 | 0.222 | 0.556 (n=9) | 0.111 (n=9) |
| 31623–100000 | 18 | 11 | 0.611 | 5 | 0.278 | 0.778 (n=9) | 0.444 (n=9) |
| 100000–500000 | 22 | 14 | 0.636 | 5 | 0.227 | 0.818 (n=11) | 0.455 (n=11) |

| standoff m | n | centre-hit | rate | IoU≥0.50 | rate | median int_area_px |
|---:|---:|---:|---:|---:|---:|---:|
| 0.3 | 12 | 4 | 0.333 | 1 | 0.083 | 224436 |
| 0.5 | 14 | 9 | 0.643 | 5 | 0.357 | 141229 |
| 0.7 | 14 | 8 | 0.571 | 4 | 0.286 | 68039 |
| 1 | 14 | 7 | 0.500 | 1 | 0.071 | 29566 |
| 1.5 | 14 | 5 | 0.357 | 3 | 0.214 | 10718 |
| 2 | 14 | 2 | 0.143 | 1 | 0.071 | 4881 |
| 3 | 10 | 0 | 0.000 | 0 | 0.000 | 1999 |
| 4 | 12 | 0 | 0.000 | 0 | 0.000 | 753 |
| 6 | 12 | 0 | 0.000 | 0 | 0.000 | 195 |
| 8 | 8 | 0 | 0.000 | 0 | 0.000 | 68 |

### Zero-detection ceiling [방법] — the largest value below which NO frame was ever detected

| population | axis | criterion | conf | ceiling | n frames below it |
|---|---|---|---:|---:|---:|
| all size-axis | int_area_px | centre | 0.10 | 385 | 245 |
| all size-axis | int_area_px | centre | 0.25 | 707 | 321 |
| all size-axis | int_area_px | iou50 | 0.10 | 4605 | 636 |
| all size-axis | int_area_px | iou50 | 0.25 | 4605 | 636 |
| all size-axis | int_h_px | centre | 0.10 | 9 | 280 |
| all size-axis | int_h_px | centre | 0.25 | 10 | 315 |
| all size-axis | int_h_px | iou50 | 0.10 | 42 | 707 |
| all size-axis | int_h_px | iou50 | 0.25 | 42 | 707 |
| all size-axis | int_w_px | centre | 0.10 | 60 | 240 |
| all size-axis | int_w_px | centre | 0.25 | 88 | 331 |
| all size-axis | int_w_px | iou50 | 0.10 | 106 | 405 |
| all size-axis | int_w_px | iou50 | 0.25 | 106 | 405 |
| paper-pose (h 0.3, p -15) | int_area_px | centre | 0.10 | 1236 | 36 |
| paper-pose (h 0.3, p -15) | int_area_px | centre | 0.25 | 2515 | 46 |
| paper-pose (h 0.3, p -15) | int_area_px | iou50 | 0.10 | 8892 | 63 |
| paper-pose (h 0.3, p -15) | int_area_px | iou50 | 0.25 | 8892 | 63 |
| paper-pose (h 0.3, p -15) | int_h_px | centre | 0.10 | 15 | 42 |
| paper-pose (h 0.3, p -15) | int_h_px | centre | 0.25 | 19 | 48 |
| paper-pose (h 0.3, p -15) | int_h_px | iou50 | 0.10 | 42 | 66 |
| paper-pose (h 0.3, p -15) | int_h_px | iou50 | 0.25 | 42 | 66 |
| paper-pose (h 0.3, p -15) | int_w_px | centre | 0.10 | 85 | 19 |
| paper-pose (h 0.3, p -15) | int_w_px | centre | 0.25 | 117 | 33 |
| paper-pose (h 0.3, p -15) | int_w_px | iou50 | 0.10 | 157 | 45 |
| paper-pose (h 0.3, p -15) | int_w_px | iou50 | 0.25 | 157 | 45 |

## 4. Crossing table [방법] — where the rate first reaches each level (arm roi)

_Report-only. The boundary is NOT chosen here._

| axis | criterion | conf | 0.25 | 0.50 | 0.75 | 0.90 |
|---|---|---:|---:|---:|---:|---:|
| int_area_px | centre | 0.10 | 63901 | never | never | never |
| int_area_px | centre | 0.25 | 90773 | never | never | never |
| int_area_px | centre | 0.50 | 107009 | never | never | never |
| int_area_px | iou50 | 0.10 | never | never | never | never |
| int_area_px | iou50 | 0.25 | never | never | never | never |
| int_area_px | iou50 | 0.50 | never | never | never | never |
| int_h_px | centre | 0.10 | 148 | 310 | never | never |
| int_h_px | centre | 0.25 | 192 | 319 | never | never |
| int_h_px | centre | 0.50 | 199 | 362 | never | never |
| int_h_px | iou50 | 0.10 | never | never | never | never |
| int_h_px | iou50 | 0.25 | never | never | never | never |
| int_h_px | iou50 | 0.50 | never | never | never | never |
| int_w_px | centre | 0.10 | 616 | never | never | never |
| int_w_px | centre | 0.25 | 791 | never | never | never |
| int_w_px | centre | 0.50 | never | never | never | never |
| int_w_px | iou50 | 0.10 | never | never | never | never |
| int_w_px | iou50 | 0.25 | never | never | never | never |
| int_w_px | iou50 | 0.50 | never | never | never | never |
| int_area_px · PAPER-POSE | centre | 0.25 | 9210 | 35481 | never | never |
| int_area_px · PAPER-POSE | iou50 | 0.25 | 31623 | never | never | never |
| int_h_px · PAPER-POSE | centre | 0.25 | 32.22 | 90.51 | never | never |
| int_h_px · PAPER-POSE | iou50 | 0.25 | 119 | never | never | never |
| int_w_px · PAPER-POSE | centre | 0.25 | 300 | 549 | never | never |
| int_w_px · PAPER-POSE | iou50 | 0.25 | 650 | never | never | never |

_The standoff axis runs downhill (rate falls with distance) so an upward-crossing value is meaningless for it; read it off the standoff table in §3._

## 5. Arms, thresholds and false positives (size-axis population)

| arm | conf | detected IoU≥0.50 | rate | detected centre | rate | mean best IoU | FP other_hole | FP background |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| roi | 0.10 | 32 | 0.029 | 101 | 0.093 | 0.057 | 1 | 825 |
| roi | 0.25 | 27 | 0.025 | 75 | 0.069 | 0.047 | 0 | 569 |
| roi | 0.50 | 23 | 0.021 | 64 | 0.059 | 0.038 | 0 | 369 |
| roi_nopoly | 0.10 | 34 | 0.031 | 133 | 0.122 | 0.068 | 0 | 1641 |
| roi_nopoly | 0.25 | 29 | 0.027 | 98 | 0.090 | 0.055 | 0 | 1080 |
| roi_nopoly | 0.50 | 24 | 0.022 | 68 | 0.062 | 0.040 | 0 | 669 |
| full | 0.10 | 25 | 0.023 | 78 | 0.072 | 0.042 | 0 | 556 |
| full | 0.25 | 16 | 0.015 | 55 | 0.050 | 0.030 | 0 | 268 |
| full | 0.50 | 11 | 0.010 | 34 | 0.031 | 0.018 | 0 | 93 |

**Frames with NO GT box** (int_area_px == 0): every kept box is a false positive

| population | arm | conf | n frames | frames with ≥1 box | other_hole boxes | background boxes |
|---|---|---:|---:|---:|---:|---:|
| size-axis | roi | 0.10 | 45 | 20 | 0 | 35 |
| size-axis | roi | 0.25 | 45 | 15 | 0 | 23 |
| size-axis | roi | 0.50 | 45 | 12 | 0 | 17 |
| size-axis | roi_nopoly | 0.10 | 45 | 43 | 0 | 69 |
| size-axis | roi_nopoly | 0.25 | 45 | 36 | 0 | 47 |
| size-axis | roi_nopoly | 0.50 | 45 | 32 | 0 | 40 |
| size-axis | full | 0.10 | 45 | 16 | 0 | 29 |
| size-axis | full | 0.25 | 45 | 8 | 0 | 10 |
| size-axis | full | 0.50 | 45 | 3 | 0 | 4 |
| occlusion | roi | 0.10 | 62 | 6 | 1 | 7 |
| occlusion | roi | 0.25 | 62 | 4 | 0 | 5 |
| occlusion | roi | 0.50 | 62 | 1 | 0 | 1 |
| occlusion | roi_nopoly | 0.10 | 62 | 21 | 0 | 30 |
| occlusion | roi_nopoly | 0.25 | 62 | 13 | 0 | 13 |
| occlusion | roi_nopoly | 0.50 | 62 | 3 | 0 | 3 |
| occlusion | full | 0.10 | 62 | 8 | 0 | 10 |
| occlusion | full | 0.25 | 62 | 4 | 0 | 4 |
| occlusion | full | 0.50 | 62 | 1 | 0 | 1 |

## 6. Occlusion subset (occlusion_intended = true, expandedworld only)

96 frames, 34 with any visible interior. `occ_frac` = the share of the opening's analytic footprint whose ray is stopped ABOVE the walking surface by a real asset, measured from the depth image (0.000 on all 1135 size-axis frames).

| occ_frac bin | n frames | n with GT | median int_area_px | centre-hit | IoU≥0.50 |
|---|---:|---:|---:|---:|---:|
| 0–0.01 | 12 | 11 | 85 | 0 (0.000) | 0 (0.000) |
| 0.01–0.5 | 19 | 18 | 88 | 0 (0.000) | 0 (0.000) |
| 0.5–0.9 | 5 | 5 | 53 | 0 (0.000) | 0 (0.000) |
| 0.999–1 | 59 | 0 | 0 | – | – |

| occluder asset | n frames | n with GT | centre-hit (conf ≥ 0.25) |
|---|---:|---:|---:|
| aws_robomaker_warehouse_ShelfE_01_002 | 27 | 11 | 0 |
| aws_robomaker_warehouse_ClutteringA_01_016 | 19 | 3 | 0 |
| aws_robomaker_warehouse_ShelfE_01_001 | 18 | 9 | 0 |
| aws_robomaker_warehouse_ShelfE_01_003_clone_0 | 8 | 4 | 0 |
| aws_robomaker_warehouse_ClutteringC_01_028 | 6 | 0 | 0 |
| aws_robomaker_warehouse_ClutteringC_01_029_clone | 5 | 0 | 0 |
| aws_robomaker_warehouse_ShelfD_01_002 | 5 | 3 | 0 |
| aws_robomaker_warehouse_ClutteringC_01_027 | 3 | 0 | 0 |
| aws_robomaker_warehouse_PalletJackB_01_001 | 3 | 3 | 0 |
| aws_robomaker_warehouse_ClutteringC_01_029 | 1 | 0 | 0 |
| aws_robomaker_warehouse_WallB_01AB | 1 | 1 | 0 |
