# T14 · Real-world protocol + pilot status — **pre-registered, ZERO data captured**

<!-- LEDGER: experiments/mainrun_0819/realworld/PROTOCOL_SHOOT.md :17-18 status, :41-64 spec, :115-123 azimuth -->
<!-- LEDGER: PROTOCOL_SHOOT.md :125-146 grid + 15/20, :157-160 allocation, :167-170 AUC thresholds -->
<!-- LEDGER: experiments/mainrun_0819/realworld/REALWORLD_GRID_PROTOCOL.md :45-51, :84-106, :113-129, :151-175, :357-382, :403-417 -->
<!-- LEDGER: experiments/weekend_0823/pilot_package/README_PILOT.md :48-55, :74-103, :187-191, :351-366 -->
<!-- LEDGER: experiments/v3_0823/ACCOUNTING.md §4.8 #4 (SCOPE-08 hfov, blocking) -->

- **Corrected-GT status**: **N/A — no measured data exists.** This is a protocol asset, not a result.
- **Provenance**: `experiments/mainrun_0819/realworld/{PROTOCOL_SHOOT.md, REALWORLD_GRID_PROTOCOL.md,
  sites.csv}` · `experiments/weekend_0823/pilot_package/README_PILOT.md`

---

## 0. STATUS — say this plainly in the paper

> **PROTOCOL ONLY. ZERO CAPTURED DATA.** `realworld/` holds exactly three files and no
> subdirectories. `raw/`, `frames/`, `pilot_out/` — **all three do not exist**. `PILOT_READOUT.md`
> does not exist. `sites.csv` is **12 EXAMPLE rows** (all `EX_`-prefixed), zero real rows. **No .jpg
> anywhere.** The protocol says so itself: *"as of 2026-08-23, **0 shots taken** — no rework."*
> The only thing executed is a **CPU smoke test on a synthetic frame** (`max_prob = 0.006475`,
> `fired: none`), and §5.2's AUC snippet was verified on **dummy data**.
> **The pilot shoot is assigned to 승용.**

## 1. Pre-registered readout — fixed before any result

> Frame statistic = `max_cell_prob` over that frame's 20 cells. Hazard group = V·E·H cuts, 12 shots
> (n₁ = 12); control group = N-turn + N-cue cuts, 8 shots (n₂ = 8). Mann–Whitney U, AUC = U/(n₁·n₂).
> **AUC ≥ 0.80 → "sim→real transfer signal present", proceed to the main shoot. 0.60 ≤ AUC < 0.80 →
> hold and redesign. AUC < 0.60 → stop and report.** *This threshold was fixed before seeing pilot
> results and will not be changed after seeing them.*

| ancillary | value |
|---|---|
| U_max | 96 — AUC ≥ 0.80 ⟺ **U ≥ 76.8** |
| complete separation | one-sided p = 1/C(20,8) = **7.9 × 10⁻⁶** |
| primary decision | **median of 3 seeds** (rgb_s42/43/44); all three reported; no cherry-picking |
| ties | `U = Σ[(a>b) + 0.5(a=b)]` |
| N-cue-only AUC (n₁=12, n₂=4), N-turn-only AUC | **reported but NOT gates** |
| pre-declared interpretation | high N-turn AUC + N-cue AUC ≈ 0.5 ⟹ **evidence the cue shortcut survives in the real world**, to be placed beside sim sceneC2's dressing-preserved off-arm FA **.681** |

AUC was chosen precisely because it is **threshold-free**; τ_op stays fixed at 0.5.

## 2. Observation grid — 20 cells registered, **15 observable** (asymmetric by geometry)

Grid `PROVISIONAL-GRID-V1`: **5 sectors A–E × 4 bands**, sector width 12.44° (total ±31.1°), band
edges **0 / 2 / 5 / 8 / 12 m**, `cell = band*5 + sector`, ids `A1..E3b`.

> **At the regulation pose, band 1 (0–2 m) does not enter the frame.** At camera height 1.5–1.8 m,
> pitch [−15°, −3°], 16:9, **only 15 of the 20 cells (bands 2 · 3a · 3b) are ever inside the
> picture**. Band 1 would require a pitch of **−18° to −23°**, which is outside the regulation range
> *and* outside the corpus distribution (min −19.13°). An overlay printing `15/20 wedges fall inside
> the frame` **is correct behaviour**. **Cuts with `dist_m < 2 m` are not made.**

Measured: h = 1.50 m → 15/20, band 1 needs pitch ≤ −18.1° · h = 1.65 → ≤ −20.8° · h = 1.80 → ≤ −23.2°.
Reason: at h = 1.65 m the ground 2 m ahead is **39.5° below the horizon**, but 16:9 at hfov 62.2°
gives only **37.5° of vertical FOV** (half-angle 18.74°).

> **This constraint exists ONLY on the real track.** The sim corpus goes down to h_rel 0.25 m, so
> band 1 is observable there. **15 cells is the real track's effective grid — scoring denominator
> excludes band 1, while model outputs for it still exist.**

## 3. Shoot specification

| item | rule |
|---|---|
| aspect | **16:9, mandatory.** If unavailable, shoot 4:3 and crop **symmetrically top/bottom**; **left/right cropping is forbidden** (changes hfov, shifts sectors) |
| why | training squashes 1920×1080 → 512²; feeding 4:3 makes the net read `tan θ_app = 0.75·tan θ_true`, so **true 8 m appears as 10.7 m — one whole band off** (tan(vfov/2) 0.339 for 16:9 vs 0.452 for 4:3) |
| calibration cut | **1 shot, mandatory, at the start.** Markers at **2/5/8/12 m** on the optical axis + a known-width object. `CALIB__<device>__01.jpg`, **not counted in the 20**. Fits (f, pitch, h) directly, removing the EXIF-FOV + horizon-pitch chain — critical because in urban descending stairs the horizon is usually occluded. ~10 min. Re-shoot on any device/setting change |
| pitch | **[−15°, −3°]** (R2 revision; old spec was −15°~+5°). Upward cuts have **0 instances in the corpus** and are forbidden |
| roll | \|·\| ≤ 3° (corpus p05–p95 = −2.44°–2.63°) |
| height | 1.5–1.8 m · rear main lens · landscape · no ultrawide/tele/digital zoom |
| exposure | auto AE/AWB (manual lock forbidden), HDR / night / beauty **off**; **P-1: no over-exposure, re-shoot blown highlights** (T08) |
| files | EXIF preserved (no messenger transfer), long edge ≥ 1920 px, `site_id__tier__idx.jpg`; annotation copies **hashed for blind coding** |
| bands | assigned from **measured `dist_m`, never read off the photo** — 1° pitch error moves the 12 m edge by **1.523 m**; 2° + 0.1 m height error gives **3.8 m** uncertainty at 12 m = the full width of band 3b |

Corpus pose distribution (n = 2,832): pitch **[−19.13°, −2.02°]** · h_rel [0.25, 1.89] m ·
hfov **[58.12°, 65.92°]** · roll [−4.83°, 4.16°].

## 4. Pilot allocation — 20 shots + 1 calibration

> **V 4 / E 4 / H 4 / N-turn 4 / N-cue 4 = 20.** At least 2 sites, **a descending-stair site is
> mandatory.** Plus **1 calibration cut** (not among the 20).

Rationale: V and E are already strong in sim; the paper's claim rides on **H and FA**. N must be
split in two for the cue shortcut to be measurable at all: **N-cue is the real-world counterpart of
sim's sceneC2 dressing-only control**, where **77 % of the RGB response was attributable to dressing
and the dressing-only arm's FA was .681**. **N-turn alone is insufficient** — a 180° turn yields a
*different scene*, so silence may mean "out of domain", not "low FA".

---

## CAVEAT LINE — must travel with this table

> ⚠ **BLOCKING, must be fixed before shooting (RT-A SCOPE-08).** `infer_photo.py`'s defaults —
> `DEFAULT_PITCH_DEG = 0.0` and, with no EXIF, `DEFAULT_HFOV_DEG = **69.0**` — are values with **0
> instances in the corpus** (corpus hfov range [58.12°, 65.92°]). **Training used 62.2°.** Results
> run at the defaults **are not scored.** If the log prints `hfov=69.0deg (default,no EXIF)` the
> photo lost its EXIF in transit — **that cut is discarded** and the original re-transferred.
> Registered fix: record the training hfov in config + emit an infer warning + state the angle in
> the pilot guide.

> ⚠ **`sites.csv` is STILL UNCORRECTED** as of 2026-08-23, stated in all three documents. The
> canonical azimuth sign is **left = POSITIVE** (`labeler.py:176` `az = atan2(yc, xc)`, and
> `cam_basis`'s `right = (f_y, −f_x, 0)` ⇒ image right = world −y ⇒ +azimuth = image left = sector A).
> The old spec said the opposite. `PROTOCOL_SHOOT.md` is fixed; `sites.csv` still has (a) the **old
> inverted sign**, (b) the **old V0 cell name `C3`** (invalid in V1, which uses `3a`/`3b`), (c) bare
> `N` instead of `N-turn`/`N-cue`/`none_in_fov`, and (d) **none** of the four recommended columns
> (`dist_method`, `aspect`, `pitch_deg`, `calib_shot`). **Approval #6: fix once, immediately before
> shooting.**

> **RGB single-arm only.** `infer_photo.py` calls `model_factory.build("rgb", ...)`; depth and B2
> checkpoints will not load and there is no way to produce real-photo depth. **The real-world track
> is an RGB-only result and this must be stated in the readout and in the paper.**

> **This track does not enter the headline table.** Real-photo n is two-digit; it is **qualitative
> evidence**. The headline stays `SEED_TABLE.md`.

> **No calibration-fitting script exists yet** — manual 3-point least squares is the pilot-scale plan.

> **V2S (10-sector) was rolled back (D43).** Annotate in **V1 only** — V1 → V2S folding is
> derivable, the reverse is not.

> **Approval #7**: the 15-of-20 asymmetry gets an explicit methods-section paragraph. Band
> subdivision and the FOV rule stay as they are; **the near-range solution is the video-propagation
> roadmap**, not a protocol change.
