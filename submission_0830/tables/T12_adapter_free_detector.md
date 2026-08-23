# T12 · Detector baseline — adapter-scoped ceiling vs adapter-free twin-conditional rate

<!-- LEDGER: experiments/mainrun_0819/METRICS.md :1071-1100 (§RT.3) -->
<!-- LEDGER: experiments/dayrun_0820/runs/v2/SEED_TABLE.md :75-99 (§4.2 + two honest footnotes) -->
<!-- LEDGER: experiments/mainrun_0819/RESULTS_DRAFT.md RT-D (:539-543) -->
<!-- LEDGER: experiments/dayrun_0820/METRICS_NOTES_yolo.md §0, §2, §3, §4 -->
<!-- Script: rt_response/code/f3_adapter_free_yolo.py, 3 seeds -->

- **Corrected-GT status**: **OLD GT.** The E/H = 0 result is logically invariant (H/E denominators do
  not move), but the **V rows and `none_in_fov` rows move** and **the YOLO runs have NOT been
  rescored** — see INDEX §재발행 필요 목록.
- **Provenance**: `experiments/mainrun_0819/METRICS.md` §RT.3
- **Method**: remove the adapter. A hazard-ON frame is an **image-space hit** iff some stored
  detection (conf ≥ τ_conf) has IoU > t with some amodal GT box of that frame — no grid, no ground
  projection.

---

## 1. Adapter-free image-space hit rate (τ_conf = 0.25)

| tier | n | any detection | **IoU > 0** | IoU > 0.1 | IoU > 0.3 | mean best IoU |
|---|---|---|---|---|---|---|
| V | 180 | 0.393 ± 0.103 | **0.378 ± 0.086** | 0.356 | 0.317 | 0.239 |
| E | 45 | 0.259 ± 0.233 | **0.259 ± 0.233** | 0.259 | 0.259 | 0.182 |
| **H** | **96** | 0.167 ± 0.094 | **0.066 ± 0.036** | 0.052 | 0.031 | 0.016 |
| H_weak | 6 | 0.167 ± 0.250 | 0.167 ± 0.250 | 0.000 | 0.000 | 0.003 |
| none_in_fov | 81 | 0.214 ± 0.136 | 0.012 ± 0.012 | 0.008 | 0.000 | 0.002 |

**The H rate is not zero.** The bound is recovered only by adding the hazard-blind control.

## 2. The hazard-blind control — score the OFF twin's detections against the ON frame's GT boxes

| tier | n | on-arm IoU>0 | off-twin IoU>0 | on − off | **twin-conditional IoU>0** |
|---|---|---|---|---|---|
| *τ_conf = 0.25* | | | | | |
| V | 180 | 0.378 | 0.041 | **+0.337** | **0.346 ± 0.064** |
| E | 45 | 0.259 | 0.148 | +0.111 | 0.170 ± 0.156 |
| **H** | **96** | 0.066 | **0.076** | **−0.010** | **0.038 ± 0.010** |
| *τ_conf = 0.05 (storage floor)* | | | | | |
| V | 180 | 0.615 | 0.156 | +0.459 | 0.487 ± 0.008 |
| E | 45 | 0.593 | 0.422 | +0.170 | 0.311 ± 0.022 |
| **H** | **96** | 0.302 | 0.233 | +0.069 | **0.142 ± 0.062** |

## 3. The two bounds — never conflate them

| # | bound | scope | number |
|---|---|---|---|
| (i) | **our `det2cell` adapter** cannot map a box to an E- or H-tier cell at all | the adapter | E = H = **0.000**, fixed by the oracle-box diagnostic **before any training** |
| (ii) | adapter removed, pure image space | the detector | H IoU>0 = 0.066, off-twin 0.076 ⇒ **twin-conditional −0.010**, against **+0.337** on V |

**(ii) is the defensible statement, and it is the stronger one.** An **amodal-trained** detector —
taught to draw boxes over hazards it cannot see — still produces nothing conditional on the hazard
when the hazard contributes no pixels.

---

## CAVEAT LINE — must travel with this table

> **The published "E = H = 0.000" is a property of OUR adapter, not of detection.** The original
> claim — *"any method whose output is a bounding box over visible hazard pixels has an identically
> zero ceiling on the E and H tiers, independent of detector quality"* — generalises to a paradigm
> and is **withdrawn**. `METRICS_NOTES_yolo.md` §0: *"every property of that adapter is a property of
> the adapter."* Feeding the amodal GT boxes in as confidence-1.0 detections yields E = H = 0.000
> before training. A nonzero value in the table would have been a **mapping-leak alarm**, and the
> alarm did not fire.

> **Sub-operating-threshold footnote (must travel if the sweep is shown).** At τ = 0.10 — *below*
> the operating point — seeds 42 and 44 each show `frame_recall_H` = 0.0104 = **1 hazard frame of
> 96** (cell recall 0.0021 / 0.0064); s43 stays 0.000. At τ = 0.25, 0.50 and above, all three are
> exactly 0. Attribution: one low-confidence box landing in a near band via the mapping's documented
> near-band bias — not H-tier perception.

> **Do not over-read the V column.** V recall 0.150 at cell precision 0.472 is a floor, not "YOLO
> cannot see". The row's argument is about the E/H columns.

> **State our own baseline's limitation first.** For a hazard contributing zero pixels of its own
> surface, the amodal box is **not determined by the image** — in scene14 it spans the building
> facade the drop hides behind. The detector was given a partly unlearnable target. Report the
> τ_conf = 0.05 twin-conditional H rate (**0.142**) alongside the operating-point value.

> **Parameter counts are asymmetric and should be stated**: yolov8n **3.2 M** · ResNet34-U-Net
> **24.4 M** · SegFormer-B2 **≈ 27 M**.

> **Seed spread is the FA story**: `frame_fa_off` runs 0.005 → 0.025 → 0.042 — an **8-fold range on
> 3 seeds**. Report as ± range/2 and claim no difference against any U-Net arm on its strength.
