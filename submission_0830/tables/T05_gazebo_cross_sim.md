# T05 · Gazebo cross-simulator transfer — the one INDEPENDENT corroboration

<!-- LEDGER: experiments/weekend_0823/gazebo/GAZEBO_TRACK.md — :10 headline, :38-52 capture, :53-90 leak check -->
<!-- LEDGER: GAZEBO_TRACK.md :100-113 twin collapse, :128-157 ladder inversion, :159-180 gz_drop3, :201-221 E geometry -->
<!-- LEDGER: GAZEBO_TRACK.md :236-249 §7-1/§7-2/§7-5 claim boundary, :273-285 panels -->

- **Corrected-GT status**: **N/A — outside the corrected-GT surface.** This track uses Gazebo worlds
  and frozen v2 checkpoints; it reads no Isaac corpus label. Nothing here moves under the G7 repair.
- **Provenance**: `experiments/weekend_0823/gazebo/GAZEBO_TRACK.md` · panels `gazebo/out/panels/`
- **Setup**: frozen v2 checkpoints (6 models) run **zero-shot** in Gazebo — a different renderer and
  a different scene generator. 8 worlds × 27 PNG × 9 views × 3 frames = **216/216 captures, rc 0**.
  Static check `gz sdf -k worlds/*.world` → 8/8. Inference: 6 × 8 × 9 = **432**, `--grid
  gridspec_v1.json --fit squash --tau 0.5`, CPU 2 m 10 s. **No robot appears in any frame.**

---

## 1. Leak check — the zero-pixel claim is verified, not assumed

Renderer noise floor is **exactly 0** (`_000` vs `_001` pixel-identical on all 9 views, `#px>0 = 0`).

| row band | 250–350 (sky/far) | **350–490 (hazard band)** | 700–1080 (near deck) |
|---|---|---|---|
| `gz_drop3` H vs C | 63 px | **0 px** | 2,970 px |
| `gz_drop1` H vs C | 79 px | **54,808 px** | 1,792 px |

The residual elsewhere is deck tessellation (hazard arm splits the deck into 4 meshes, control uses
1): amplitude ≤ 52/255, ≤ 0.22 % of pixels. **Verdict: occlusion is genuine; `gz_drop3`'s H label
stands.**

## 2. Firing at ZERO hazard pixels — `gz_drop3`

| family | HAZ arm fire | **CTL arm fire (= FA)** | pooled | mean max-p | fired cells/frame |
|---|---|---|---|---|---|
| rgb | 0.571 (12/21) | **0.524** (11/21) | 0.548 | 0.591 | 2.9 |
| b2 | 0.905 (19/21) | **0.905** (19/21) | 0.905 | 0.811 | 4.6 |

Per-seed pooled FA: rgb .429 / .714 / .500 · b2 .857 / **1.000** / .857.
Twin Δ is 0 by construction and measures 0: max |Δ| = 0.090 across all model × view, 6-model mean
Δ ∈ [−0.015, +0.009].
**Same direction as CUE-OFF arm C** (scene12 rgb FA 1.000, b2 1.000, depth 0.333).

## 3. Tier-ladder inversion — **5 of 6**, and the ladder follows fixtures, not geometry

Expected `p(drop2) ≳ p(drop1) > p(drop4) > p(drop3)`. Hazard-arm mean max-p:

| model | gz_drop1 (V) | gz_drop2 (V) | **gz_drop3 (H)** | gz_drop4 (V/E) | order OK? |
|---|---|---|---|---|---|
| rgb_s42 | 0.690 | 0.594 | 0.441 | 0.443 | NO |
| rgb_s43 | 0.510 | 0.428 | **0.769** | 0.611 | NO |
| rgb_s44 | 0.227 | 0.030 | **0.567** | 0.216 | NO |
| b2_s42 | 0.890 | 0.717 | **0.839** | 0.627 | NO |
| b2_s43 | 0.761 | 0.683 | **0.772** | 0.678 | NO |
| b2_s44 | 0.879 | 0.628 | **0.807** | 0.654 | NO |

**5 of 6 models score the world where the hazard contributes ZERO pixels (`gz_drop3`, H) HIGHER
than the world whose drop interior is plainly visible (`gz_drop2`, V).** `gz_drop2` has a railing on
one side only and **no** warning block; `gz_drop3` shows warning block + railing + planter wall.
**The ladder follows the order of fixtures placed in the scene, not the order of the geometry.**

> ⚠ **Correction on the record: 5/6, not 4/6.** D48's "4/6" was a miscount. The five are rgb_s43
> (0.769 > 0.428), rgb_s44 (0.567 > 0.030), b2_s42 (0.839 > 0.717), b2_s43 (0.772 > 0.683),
> b2_s44 (0.807 > 0.628); the only non-inverted model is rgb_s42 (0.441 < 0.594).

## 4. Twin discrimination collapses in transfer

| model | HAZ fire | CTL fire | **Gazebo twin Δ** | in-sim twin Δ |
|---|---|---|---|---|
| rgb mean | 0.452 | 0.405 | **+0.019** | +0.314 |
| b2 mean | 0.881 | 0.821 | **+0.057** | +0.234 |

Twin Δ shrinks to **6 % (rgb) / 24 % (b2)** of its in-sim value — while the *firing rate itself*
goes **up** (b2 hazard 0.881 / control 0.821).

---

## CAVEAT LINE — must travel with this table

> **ONLY TWO CLAIMS ARE SAFE FROM THIS TRACK (§7-2).** (1) **firing where the hazard contributes
> zero pixels**, and (2) **the ladder follows fixture order, not geometry**. The twin collapse itself
> is **confounded with the sim2sim domain gap**: Gazebo primitives + stock `Gazebo/*` materials are
> far simpler than the Isaac corpus, so a pit interior renders as a nearly uniform black face (no
> shadowing, no AO, no interior texture) and the visual evidence for "drop geometry" is itself
> impoverished. **Do not attribute the twin collapse entirely to "the model only reads cues."**

> **This is the paper's only INDEPENDENT corroboration of the scene-association conclusion.** CUE-OFF
> and sceneC2 re-read the pixels of the *same* renderer; Gazebo does not. Frame it as **"two
> renderers, three geometries, one behaviour."**

> **E-tier geometry, established here and generalised in the limitations section.** Back-calculating
> from `gz_drop4`: at d ≤ 2 m, an E tier (rim visible, interior hidden) requires an aperture of
> **1–3 cm** — physically a crack, not a drop. Tier coverage over the 7 negobs views is **V 14 /
> E 2 / H 7**; E holds only at d = 10. **No statistics were attached to 12 cuts. "E is a far-field
> phenomenon only."** (approval #11)

> **The depth arm is missing, and it is the arm that mattered.** `infer_photo` is RGB-only and the
> worlds were generated without `--depth`, so `*_depth.npy` = 0 files. **Depth was the only arm with
> a low FA in CUE-OFF (0.333) and it is absent here.** Listed as the track's largest hole (§9,
> §7-5); the fix is `make_worlds.py --depth` + a depth-side `infer_photo` equivalent. (caveat C6)

> **Panel figures are TRACKABLE (6 files, `gazebo/out/panels/`).** The full 432-overlay set (76 MB)
> was deliberately **not** committed; regenerate with `OVR=<dir> ./infer_run.sh`.
