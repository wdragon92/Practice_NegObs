# METRICS_NOTES_yolo.md — the YOLOv8n track's detection→cell mapping

`PROVISIONAL-GRID-V1` · DAYRUN 0820 Phase 5 · code in `code/yolo/`
Written 2026-08-20 by the Phase-5 PREP pass (before any training run).
Copy the §1 rule into `METRICS.md` when the night's table is assembled — the brief
(Phase 5.4) asks for the rule to be spelled out next to the numbers.

---

## 0. What the row in the paper table means

Rows 1–3 of the headline table are polar-grid classifiers: they emit a probability
for each of the 20 cells directly. Row 4 (YOLOv8n) is a **detector**: it emits boxes
in image space and has no idea the polar grid exists. Everything in this file is the
adapter that turns row 4 into a row-1-shaped row, and every property of that adapter
is a property of **the adapter**, not of YOLOv8n.

The output is `per_frame.csv` in the exact `eval_polar.write_per_frame` format —
`frame_id, scene_id, tier, toggle_state, p_<cell>×20, g_<cell>×20`, cell ids taken
from `gridspec.load(...).cell_ids` — so `eval_polar --per-frame-a` and
`twin_analysis` consume it unmodified. `gt` is copied straight out of
`dataset_manifest_v2.json`: the YOLO row is scored against **the same labels** as
every other row.

---

## 1. The mapping rule (`code/yolo/det2cell.py`)

```text
for each frame F with camera cam = (h_rel, yaw, pitch, roll, hfov):
    prob[c] = 0 for every cell c of the gridspec
    for each detection (box, conf) of F with conf >= tau_conf:

        # 1. the bottom edge of the box, in continuous full-res pixels
        x0, x1 = (box.xc -+ box.w/2) * W          # W, H = 1920, 1080
        y_b    = (box.yc + box.h/2) * H
        pts_px = [(x0, y_b), (x1, y_b), ((x0 + x1)/2, y_b)]   # 2 ends + centre

        # 2. ground-project each of them with the LABELER camera model
        #    (labeler.cam_basis / labeler.focal_px — the exact inverse of
        #     labeler.project, so this is the same optics the GT was built with)
        for (u, v) in pts_px:
            xn  = (u - W/2) / f_px ;  yn = (v - H/2) / f_px
            dir = xn*right + yn*(-up) + fwd
            if dir.z >= 0:  continue              # at or above the horizon
            t   = (cam.ground_z - eye.z) / dir.z  # == -h_rel / dir.z
            if t <= 0:      continue
            P   = eye + t*dir                     # the plane z = cam.ground_z

        # 3. (azimuth, range) of P about the eye, then the cell
            az, rng = labeler.polar_cells(P.x, P.y, eye, cam.yaw, grid)
            cell    = band(rng)*n_sectors + sector(az)   # -1 = outside the grid

        # 4. the detection CLAIMS the SET of cells its bottom-edge points fell
        #    into (deduped; cell == -1 dropped)
            claimed |= {cell}

        # 5. frame-level cell prediction = union over detections, scored by the
        #    strongest detection that claimed the cell
        for c in claimed:
            prob[c] = max(prob[c], conf)

    gt[c] = manifest.polar_gt[c]        # unchanged: same grid, same labels
    emit row (frame_id, scene_id, tier, toggle_state, prob[...], gt[...])
```

Frames with no detection file, or with no detection above `tau_conf`, still emit an
all-zero row — the false-alarm and twin denominators must count them.

**Threshold discipline.** `tau_conf` is applied *here*, at mapping time. The
ultralytics `predict` call must therefore run at a confidence floor **below the
lowest sweep value** (`--pred-conf 0.05` in the README), otherwise "sweeping down to
0.1" would be sweeping over detections that were never written to disk.

**Why no `eye`.** `dataset_manifest_v2.json`'s `cam` block carries
`d, h_rel, yaw, pitch, roll, hfov, ground_z` but **no `eye`** — the absolute world
(x, y) of the camera is not in the manifest. It is also not needed: the ray depends
on (yaw, pitch, roll, hfov); the plane offset is `ground_z − eye.z = −h_rel`; and
`polar_cells` uses only `P − eye`. `common.synth_eye` therefore places the eye at
the origin of its own ground frame, and the mapping is exact. Verified: pixel →
ground → `labeler.project` round trip, max error **5.3e-15 m** over 371 in-frame
points (`det2cell.py --unit-check`).

---

## 2. Known properties of the rule — report them, do not silently "fix" them

**(a) Three points per box cap cell recall.** A detection claims at most 3 cells; a
hazard frame's GT routinely spans 8–15. `--bottom-samples N` relaxes this and is
reported as a sweep, never as the headline.

**(b) The amodal box includes the drop interior, so the bottom edge back-projects
too near.** The lowest image row of an amodal box is the wall base *below* the lip,
not the lip; intersecting that ray with the plane `z = cam.ground_z` lands **nearer
than the true lip** — for a 0.6 m drop at 4 m with a 0.4 m eye height, ~2.4 m nearer.
The mapping is therefore biased toward the near bands. It is the brief's rule and is
kept exactly as specified; this bias is why a YOLO row can look near-band-heavy next
to the polar heads.

**(c) H recall is structurally ~0.** A visibility-trained detector cannot fire on a
hazard with zero visible pixels. **A nonzero H recall is a mapping leak to
investigate, not a win** (brief Phase 5.5).

---

## 3. Measured ceiling of the rule — before any training

`det2cell.py --oracle-boxes annotations/amodal/bboxes.json --subset test` feeds the
**amodal GT boxes themselves** in as conf-1.0 detections. This is what a *flawless*
detector would score under this mapping. It is a diagnostic, never a model number.

| bottom-edge samples | frame det rate | recall V | recall E | recall H | cell recall | frame FA (off) |
|---|---|---|---|---|---|---|
| **3 (the brief's rule)** | **0.404** | **0.514** | **0.000** | **0.000** | **0.074** | **0.000** |
| 5 | 0.404 | 0.514 | 0.000 | 0.000 | 0.132 | 0.000 |
| 9 | 0.404 | 0.514 | 0.000 | 0.000 | 0.181 | 0.000 |
| 33 | 0.404 | 0.514 | 0.000 | 0.000 | 0.185 | 0.000 |

test subset, τ_conf = 0.25, 141 hazard frames (V 111 / E 9 / H 21), 168 off frames.

Three things follow, and they matter for how the night's table is read:

1. **The YOLO row is capped at ≈ 0.40 frame detection rate and ≈ 0.07 cell recall by
   the adapter alone.** Denser bottom-edge sampling lifts cell recall (0.074 → 0.185)
   but leaves the frame detection rate untouched at 0.404 — the cap is property (b),
   the near-bias of the bottom-edge projection, not the sampling density.
2. **E and H recall are 0 at the ceiling.** So the brief's expectation is stronger
   than "we expect ~0": under this mapping, E and H recall *cannot* be nonzero from
   correct behaviour. Any nonzero E/H in the trained runs is a leak — the first place
   to look is a box whose bottom edge happens to fall on a far GT cell for reasons
   unrelated to the hazard.
3. **Frame FA on the off arm is 0 at the ceiling** by construction (off-arm frames
   have no GT boxes). The trained model's FA is therefore entirely earned, which
   makes it the most informative number in the YOLO row.

**Claims landing outside the grid: 471 / 1032 (46 %)** at the 3-point rule. Those are
bottom-edge points whose ground projection falls past 12 m, inside 0 m, or outside
±31.1° of azimuth. They are dropped, not clipped to the nearest cell — clipping would
manufacture exactly the kind of leak §2(c) is watching for.

---

## 4. The amodal GT the boxes come from (`code/yolo/amodal_masks.py`)

Boxes are the per-component bounding boxes of an **amodal** mask: the post-gate
heightmap footprint projected through the frame's camera **ignoring occlusion**.

* Footprint = `labeler`'s own `z_off − z_on ≥ 0.30 m` twin difference + the D10 step
  gate, recomputed per frame through `labeler.step_gate`. Cross-checked against
  `labels_v1.json`'s `footprint.cells_kept` on **all 792 on-arm frames: 0 mismatches.**
* What is projected is the hazard **prism** [z_on, z_off] over that footprint —
  top surface, bottom surface, and the walls at the footprint perimeter — so the mask
  is the image silhouette of the opening *and* its interior.
* Rasterisation: depth-adaptive square splat, radius = one heightmap cell at that
  sample's depth (`ceil(f_px·0.05/z)`), power-of-two bucketed, exact separable binary
  dilation. numpy only, no morphological close (the splat already closes the 5 cm
  lattice, and a close would bridge genuinely separate components).
* Masks are 960×540; boxes are normalised, hence valid for the 1920×1080 images the
  dataset symlinks point at.

Coverage tier by tier (on arm, 792 frames): V 438/438, E 36/36, H 45/45, H_weak
12/12 all carry a non-empty mask. The only empty on-arm masks are 240 of the 261
`none_in_fov` frames — the hazard is outside the grid, which is what that tier means.
The other 21 `none_in_fov` frames do get a mask (hazard visible in the image but
outside the polar wedge); their detections almost always ground-project to `cell = −1`
and are dropped, but they are a known small source of GT-less boxes in training.

**One honest ugliness.** When the hazard contributes zero pixels of its own surface, the
amodal box necessarily covers whatever stands in front of it — in `scene14` the box spans the building facade behind
which the drop hides. That is what "amodal" means and it is the correct target for an
aux pixel loss (Phase 6), but it is also why asking a detector to reproduce it is a
strange task, and part of why §3 row 1 is what it is.

---

## 5. Provenance

| item | value |
|---|---|
| grid | `mainrun_0819/code/labeling/gridspec_v1.json` — `PROVISIONAL-GRID-V1`, 20 cells |
| geometry | `mainrun_0819/code/labeling/labeler.py` (imported, never re-derived) |
| camera contract | `mainrun_0819/CAM_CONVENTION.md` §2/§3/§6 |
| labels | `dayrun_0820/annotations/labels_v1.json`, manifest `dataset_manifest_v2.json` |
| split | `dayrun_0820/split_v2.json` (scene-level; `hold` excluded) |
| ultralytics | 8.4.123 · torch 2.13.0+cu130 · numpy 2.2.6 (`code/yolo/requirements_yolo.txt`) |
