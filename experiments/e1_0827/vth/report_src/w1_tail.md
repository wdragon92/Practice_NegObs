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

