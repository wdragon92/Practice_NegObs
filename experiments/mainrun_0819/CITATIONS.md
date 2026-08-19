# CITATIONS.md — recovered campaign numbers with provenance

Recon pass, 2026-08-19 night. Read-only. Every number below was re-read from the campaign
tree (and, where possible, re-verified against the raw `runs/*/` artifacts rather than the prose).

**Source root** `CAMPAIGN = /home/vislab/Desktop/work_sy/Practice_Segmentation/campaign`

| short name | absolute path | what it is |
|---|---|---|
| REPORT | `CAMPAIGN/REPORT.md` | hand-written §1–§9 + auto leaderboard (1171 lines) |
| DIGEST | `CAMPAIGN/analysis/negobs_digest.html` | "NegObs 방향 결정용 다이제스트", **§0–§8** (101 lines) |
| PROBE | `CAMPAIGN/analysis/negobs_probe.md` (+ `negobs_probe.json`) | user-scene probe, 13 scenes × 5 models |
| OCCL | `CAMPAIGN/analysis/occlusion_reliance.md` (+ `.json`) | occlusion-reliance measurement |
| WEB | `CAMPAIGN/analysis/final_report.html` | web report "낙차는 보이지 않는다" (holds tables that exist nowhere else) |
| SIZE | `CAMPAIGN/analysis/size_band.md`, `res512ep20/size_band.md`, `res768/size_band.md` | size-band IoU / recall / det@50 |
| GAP | `CAMPAIGN/analysis/domain_gap.md` (+ `.json`) | 8-shared-concept cross-domain IoU |
| RUNS | `CAMPAIGN/runs/<run>/{config.json,done.json,per_class_iou.json,metrics.csv}` | per-run ground truth |

## 0. Section-numbering key (read this first)

The brief's §-labels are **DIGEST numbering**, except §8/§9 which are **REPORT numbering**.
The two documents number differently and both exist; citing "§6" without naming the document is ambiguous.

| brief label | resolves to | REPORT equivalent |
|---|---|---|
| "§0-3 transfer 0.57/0.61" | DIGEST §0 item 3 (line 29) | REPORT §9-1 final bullet (line 127) |
| "§6 probe" | DIGEST §6 (lines 74–80) | REPORT §7-13 (line 92); primary source = PROBE |
| "§1 pit collapse" | DIGEST §1 (lines 33–41) | REPORT §7-1 (lines 66–74), §8 table (line 103) |
| "§7 caveats" | DIGEST §7 (lines 82–89) | scattered: REPORT §9-1 "정직한 한계" (line 126) |
| "§8 synthesis" | REPORT §8 (lines 96–116) | mirrored in DIGEST §1–§5 |
| "§9 capstone" | REPORT §9 (lines 118–129) | mirrored in DIGEST §0, §3 |

**Recommendation for the paper**: cite the run directory name, not a section number. Run dirs are
immutable; both narrative documents were edited in place during the campaign (one published table row
was wrong for ~8 h — see §4 caveat C6).

---

## 1. "§0-3 transfer 0.57 / 0.61" — artificial-patch supervision does not transfer

**Claim**: a model trained with context-forcing occlusion, probed on real self-occluding synthetic
scenes, marks drop hazards no better than an untreated baseline.

**Metric — not IoU.** These renders have **no GT masks** (PROBE line 11), so the measure is
*predicted area of drop-related classes as a percentage of all image pixels*, averaged over a scene
group. Denominator = every pixel of the resized 512² render; n = 4 images (one per scene).

- **drop class set** (PROBE §1 header, line 37): ADE vocab `{stairs, stairway, step, escalator}`;
  sidewalk vocab `{construction-stairs, flat-curb}`; pothole vocab `{pothole}`.
- **scene group "본편 하행(실제 낙하)", n=4**: `scene01, scene03, scene08, scene14`.

| number | model / tag | run dir | source |
|---|---|---|---|
| **0.57 %** | `occl-ade-b2-stair50` (context-trained) | `260816_2159_segformer-b2_ade20k_occl-ade-b2-stair50` | PROBE §3 line 77 (last column) |
| **0.61 %** | `ade-full-b2` (untreated baseline) | `260815_1025_segformer-b2_ade20k_ade-full-b2` | PROBE §3 line 77 (first column) |

Training config of the 0.57 model (`config.json`, verified): segformer-b2, ade20k, `ade_subset 4000`,
20 ep, batch 8, lr 6e-5, seed 42, img 512, `occlude_class 60` (= ADE `stairway`), `occlude_p 0.5`,
`occlude_mode class`; best mIoU 0.34680 @ ep 19.
Baseline: ADE full 20,210 imgs, 20 ep, same optimizer; best mIoU 0.4445 @ ep 18.

Supporting numbers in the same row (PROBE §3, line 77): `b2-sat100` 0.18 %, `m2f-sat40` 0.45 %.
The context model still false-fires on the trompe-l'œil: `stairs` **2.9 %** on sceneN3
(PROBE §1 row `N3`, line 47; §4 line 90). Restated in REPORT line 127 and WEB line 633.

**How to phrase it**: "context-forced supervision on synthetic grey patches raised occluded-stairway
IoU 53× in-distribution, yet on true self-occlusion its drop-marking area (0.57 % of image) was
indistinguishable from the untreated baseline (0.61 %)."

---

## 2. "§6 probe" — the user-scene probe

Generator: `CAMPAIGN/harness/negobs_scene_probe.py`, run 2026-08-17T12:36:21, device cuda.
Machine-readable: `analysis/negobs_probe.json`. Regenerable in minutes
(`PYTHONNOUSERSITE=1 python harness/negobs_scene_probe.py --device cpu`; 13 scenes × 4 models ≈ 25 s CPU).

### 2a. The 13-scene list (PROBE §0, lines 21–33)

View rule: `preset_h1.8_d5` (pedestrian eye 1.8 m, 5 m back = the viewpoint at which a descent
self-occludes). One image per scene. All paths under
`/home/vislab/Desktop/work_sy/Practice_NegObs/look_check/<scene>/<round>/pt_noon_preset_h1.8_d5.png`.

| # | scene | group | description | round |
|---|---|---|---|---|
| 1 | `scene01` | main | campus descending stair (reference scene) | `260816_w4_final33_on` |
| 2 | `scene03` | main | levee — slope fall, not a stair | `260817_w4_regfix` |
| 3 | `scene08` | main | sunken plaza — large pit inside a flat plaza | `260816_w4_final33_on` |
| 4 | `scene14` | main | grand stair — worst self-occlusion | `260816_w4_final33_on` |
| 5 | `sceneN1` | hard-neg | shadow band — dark stripe, flat ground | `260816_w4_final33_on` |
| 6 | `sceneN2` | hard-neg | asphalt patch — colour differs only | `260816_w4_final33_on` |
| 7 | `sceneN3` | hard-neg | trompe-l'œil — painted depth | `260816_w4_final33_on` |
| 8 | `sceneN4` | hard-neg | downhill ramp — descends but continuous | `260816_w4_final33_on` |
| 9 | `sceneN5` | hard-neg | flush grating — looks like holes, is flat | `260816_w4_final33_on` |
| 10 | `sceneD1` | drop | loading dock — real fall, not a stair | `260816_w4_final33_on` |
| 11 | `sceneD2` | drop | floor opening — real fall | `260816_w4_final33_on` |
| 12 | `sceneC1` | cond | condition variant: snow covers the edge | `260816_w4_final33_on` |
| 13 | `sceneC2` | cond | condition variant: leaves cover the edge | `260816_w4_final33_on` |

Group sizes used for the averages: main downhill 4 · non-stair drop 2 (`D1,D2`) · hard-negative 5
(`N1–N5`) · condition variant 2 (`C1,C2`).

### 2b. The 5 probe models (PROBE appendix, lines 128–134)

| tag | run dir (= where the weights came from) | arch | train domain | img |
|---|---|---|---|---|
| `ade-full-b2` | `260815_1025_segformer-b2_ade20k_ade-full-b2` | segformer-b2 | ADE20K 20,210 | 512 |
| `b2-sat100` | `260815_1411_segformer-b2_sidewalk_b2-sat100` | segformer-b2 | sidewalk 1,000 | 512 |
| `m2f-sat40` | `260815_1443_mask2former-tiny_sidewalk_m2f-sat40` | mask2former-tiny | sidewalk 1,000 | 512 |
| `pothole-b2` | `260815_1652_segformer-b2_pothole_pothole-b2` | segformer-b2 | PaveBench 1,252 | 512 |
| `occl-ade-b2-stair50` | `260816_2159_segformer-b2_ade20k_occl-ade-b2-stair50` | segformer-b2 | ADE20K 4k, p=0.5 occl | 512 |

Weights are each run's `best.pt` (weights-only `state_dict`, saved at best-mIoU epoch).
**None of the five ever saw a synthetic render** — everything here is cross-domain reading, which
is why PROBE deliberately reports *area share*, not IoU (PROBE line 9).

### 2c. The four numbers

| number | exact meaning | value & source |
|---|---|---|
| **0.2 ~ 0.6 %** | mean drop-class area over the 4 main downhill scenes, across the three *standard* models | `b2-sat100` **0.18**, `m2f-sat40` **0.45**, `ade-full-b2` **0.61** — PROBE §3 line 77. `pothole-b2` (22.45) is excluded on purpose: §4b line 102 shows **62 % of its "pothole" pixels land off-ground** (up to 98 % on scene14), so its area is texture response, not detection. |
| **21 %** | largest single-cell guard-cue (railing/fence) area — "the cue *is* segmented, the inference is not made" | sceneN4: `b2-sat100` `construction-fenceguardrail` **21.5 %**, `m2f-sat40` **21.4 %** — PROBE §1 row `N4` line 48. Group means for guard: 1.57 / 6.88 / 3.25 / 0.00 / 1.70 (PROBE §3). **Do not confuse** with REPORT §7-13 ④ (line 92), which separately cites m2f `void-ground` **21 %** on sceneD2 — a different quantity of coincidentally equal size. |
| **5.4 %** | trompe-l'œil false fire: `ade-full-b2` predicts `stairs` on a *painted* stair | PROBE §1 row `N3` line 47; adjudicated as 헛불 in §4 line 90. |
| **≈ 1 %** | the *real*, occluded stair the same model does read: scene01 `ade-full-b2` `stairs` **1.2 %** (+ `stairway` 1.2 %) | PROBE §1 row `s01` line 41. DIGEST's "5×" = 5.4 / 1.2 ≈ **4.5×**; against the 4-scene mean (0.61 %) it is 8.9×. **Safest paper phrasing**: "5.4 % of the frame on a painted fake stair versus 1.2 % on a real, partly occluded one — same model, same render pipeline." |

Additional separations worth citing (PROBE §6-3, line 122): (main drop% − hard-negative drop%) =
`ade-full-b2` **−0.48 %p**, `b2-sat100` −0.14, `m2f-sat40` +0.10, `occl-ade-b2-stair50` −0.08.
Negative ⇒ the model reacts to *surface appearance*, not to falls.

---

## 3. "§1 pit collapse" — U-Net collapses to exactly 0.0, reproduced on two seeds

Dataset: `manojkarnekar/construction-traversability-dataset` (CC-BY-NC-4.0), 506 pairs measured =
**415 train / 91 val**, 29 labels incl. `ignore=0`. Conditions identical across the four models:
512² squash + HFlip, ImageNet norm, AdamW lr 6e-5, batch 8, fp32, seed 42, CE with `ignore_index=0`,
ImageNet-pretrained encoder, 120 ep (m2f 60).

**Denominator (verified this session, not quoted):** scanning
`CAMPAIGN/data/construction/class_index.json` with `common.CONSTRUCTION_NAMES.index('pit') == 14`
gives **pit present in 12 of 415 train images and 3 of 91 val images (15 of 506 total)**.
REPORT says "15장" (dataset-wide) and DIGEST says "학습 이미지 12장" (train split) — both correct,
different denominators. Cite as *"12 of 415 training images"*.

| model | run dir | seed | `pit` IoU | best mIoU @ ep |
|---|---|---|---|---|
| **unet-r34** | `260816_0251_unet-r34_construction_constr-unet` | 42 | **0.0** (exact) | 0.41243 @ 111 |
| **unet-r34** | `260816_0511_unet-r34_construction_constr-unet-s43` | 43 | **0.0** (exact) | 0.38959 @ 90 |
| segformer-b0 | `260816_0330_segformer-b0_construction_constr-b0` | 42 | 0.6231 | 0.51811 @ 111 |
| segformer-b2 | `260815_2359_segformer-b2_construction_constr-b2` | 42 | 0.7365 | 0.56437 @ 112 |
| segformer-b2 | `260816_0337_..._constr-b2-s43` / `260816_0453_..._constr-b2-s44` | 43 / 44 | 0.7148 / 0.7255 | 0.57177 / 0.57553 |
| mask2former-tiny | `260816_0018_mask2former-tiny_construction_constr-m2f` | 42 | 0.7214 | 0.58978 @ 31 |

All `pit` values read directly from `runs/<run>/per_class_iou.json` (written at the best-mIoU epoch,
`run_experiment.py` ~line 388). The U-Net values are literal `0.0` in JSON, not rounded.
Headline: **B0 has 3.7 M params vs U-Net's 24.44 M and still recovers → architecture, not capacity**
(REPORT §8 table line 103; `params_m` from each `done.json`).

Oversampling recovery curve (U-Net, `pit` exposure ×N — REPORT §9-2 line 128):

| exposure | run dir | `pit` IoU | mIoU |
|---|---|---|---|
| ×1 | `260816_0251_..._constr-unet` | 0.0 | 0.41243 |
| ×2 | `260816_2236_unet-r34_construction_over-unet-x2` | 0.0 | 0.43523 |
| ×4 | `260816_2246_unet-r34_construction_over-unet-x4` | **0.6005** | 0.44531 |
| ×8 | `260816_2257_unet-r34_construction_over-unet-x8` | 0.5837 | 0.48266 |
| B2 ×4 | `260816_2309_segformer-b2_construction_over-b2-x4` | 0.7618 | 0.57806 |

Reading: threshold unlock between 2× and 4×, then a plateau below the newer-generation ceiling.
Directly relevant to tonight's scene budget: **rare drop variants need ≥ 4× exposure**.

Also from this dataset, cited in DIGEST §3: `not_visible` (occlusion itself as a label) is learnable at
IoU **0.4898 / 0.4647 / 0.5846 / 0.5006** (unet / b0 / b2 / m2f), n = 113 train / 21 val images.

---

## 4. "§7 caveats" — verbatim

DIGEST §7, `analysis/negobs_digest.html` lines 82–89. Quoted verbatim (Korean), gloss in italics.

> **캐비앗 (AI와 논의 시 오독 방지용)**
> - **C1** 시드 오차: sidewalk ±0.004(3시드), 소규모 정렬셋 ±0.01~0.02(3시드). pit 붕괴(0.0)는 2시드 재현. 그 외 다수는 단일 시드.
> - **C2** 가림 실험의 recall류 수치는 덮개 모양 누출로 부풀 수 있음 — 절대 IoU로 판독할 것(본 문서 수치는 IoU).
> - **C3** 크기 밴드 경계는 픽셀 고정이라 해상도 간 밴드 직접 비교는 참고용.
> - **C4** 도메인: sidewalk=벨기에 보행 시점 1천 장, ADE=실내외 혼합 2만 장, PaveBench=도로면 근접, ZJU=캠퍼스 헤드마운트 220장 — 결론의 이식 범위는 도메인 조건부.
> - **C5** 비교 조건: 전 모델 동일 LR(6e-5)·batch 8·512² — U-Net은 LR 3e-4에서 +0.06 상승(동일조건 비교의 함정 사례).

*C1 seed error: sidewalk ±0.004 (3 seeds), small aligned sets ±0.01–0.02 (3 seeds); the pit collapse
(0.0) is reproduced on 2 seeds; most other numbers are single-seed. C2 recall-type numbers in the
occlusion experiments can be inflated by cover-shape leak — read absolute IoU. C3 size-band edges are
fixed in pixels, so band-to-band comparison across resolutions is indicative only. C4 conclusions are
domain-conditional. C5 all models were compared at one LR (6e-5); U-Net gains +0.06 at 3e-4 — a
documented instance of the equal-conditions trap.*

Three further caveats that live outside DIGEST §7 and matter just as much:

- **C6 (integrity, `OCCL` line 60)** — *"이 버전의 표에서 `ade-full-b2` 행은 태그 부분일치 버그로
  `ctx-ade-full-b2` 와 동일한(잘못된) 값이 찍혀 있다. **진짜 기준선은 0.432 → 0.030 (유지율 7%)**"*.
  The published `occlusion_reliance.md` table row for `ade-full-b2` (line 20: 0.441 → 0.838) is
  **wrong**; the true B2 baseline is **0.432 → 0.030, retention 7 %**. Fixed in
  `cross_domain_eval.resolve_run` (exact-suffix first, `cross_domain_eval.py:99–113`).
  **Never quote that md row.**
- **C7 (`OCCL` line 126 / REPORT §9-1 "정직한 한계")** — *"평균색 덮개의 텍스처 자체가 인공 단서일 수
  있음(실제 자기폐색은 회색 패치가 아님)."* The mean-colour cover may itself be an artificial cue.
- **C8 (`PROBE` lines 7–11)** — the scene probe is a snapshot of a look-calibration-in-progress render
  round, is a *cross-domain read* not a performance evaluation, and has **no GT** (hence area %, not IoU).

---

## 5. "§8 synthesis" — headline numbers with run provenance

REPORT §8 (lines 96–116), mirrored in DIGEST §1–§5. All values re-verified from `runs/*/done.json`
and `per_class_iou.json` this session.

**Generation gap is a function of task type**

| task | numbers | runs |
|---|---|---|
| multi-class scene parsing (sidewalk 1k, converged) | U-Net **0.3289** / DeepLabv3+ **0.3717** / B0 **0.3416** / B2 **0.4249** / M2F **0.4738** | `260815_1304_unet-sat`(100ep,ep97) · `260815_1319_dlv3p-sat`(ep95) · `260815_1338_b0-sat`(ep94) · `260815_1411_b2-sat100`(ep77) · `260815_1443_m2f-sat40`(40ep,ep18) |
| common binary hazard (pothole, 1,252 imgs = 1002 train/250 val) | `pothole` IoU U-Net **0.6971** / B0 **0.6979** / B2 **0.7007** / M2F **0.7160** | `260815_1720_pothole-unet` · `260815_1642_pothole-b0` · `260815_1652_pothole-b2` · `260815_1834_pothole-m2f` |
| **rare hazard (pit, 12 train imgs)** | **0.0 / 0.6231 / 0.7365 / 0.7214** | see §3 above |
| boundary structure (curb) | distance-dependent: far (sidewalk) 0.5366→0.6568, near (ZJU) 0.70–0.75 | `flat-curb` from the sat runs above; ZJU from REPORT §7-1 line 70 |

**Other §8/§9 anchors**

| claim | numbers | provenance |
|---|---|---|
| pretrained representation supplies >½ of performance | B0 full **0.2774** / encoder-frozen **0.19275** / from-scratch **0.13602** | `260814_1722_..._p1` · `260814_1740_..._frozen` · `260814_1743_..._scratch` (all 20 ep, sidewalk) |
| data scale never saturates | B0 **0.2023 / 0.2668 / 0.3131 / 0.3416**, B2 **0.2971 / 0.3442 / 0.3893 / 0.4249** at 80/200/400/800 imgs (100 ep) | `s100-b0-f10/f25/f50` + `b0-sat`; `s100-b2-f10/f25/f50` + `b2-sat100` |
| diversity governs transfer (8 shared concepts, same arch b2) | sidewalk-trained: in 0.860 → cross 0.626 (**73 %**); ADE-trained: in 0.818 → cross 0.737 (**90 %**) | `GAP` lines 9–12, 18–19; runs `b2-sat100` / `ade-full-b2`; n = 200 sidewalk val, 2000 ADE val |
| resolution is a transformer-only lever (512→768, 20 ep) | B0 +0.030 (0.2774→0.30695) · B2 +0.031 (0.3615→0.39316) · dlv3p +0.014 · **U-Net −0.023** (0.21802→0.19502) | `260814_1815_res768` · `260815_1350_b2-res768` · `260815_1610_dlv3p-res768` · `260815_1635_unet-res768` |
| generation gap is largest on *large* objects | mean Δ IoU: large **+0.323**, mid +0.158, small **+0.144** | `SIZE` line 63 |
| small band (<1 % of frame ≈ far) is a cross-generation weakness | ADE stairs small: b0 IoU 0.010, rec 1 %, det@50 0 % | `SIZE` line 46 |
| resolution does lift the small band, but only for the new arch (curb, 20 ep) | B2 small **0.078 → 0.187** (det@50 **0 % → 8 %**), overall 0.401 → 0.580; U-Net at 768 **0.000 everywhere** | `analysis/res512ep20/size_band.md` lines 25–28 vs `analysis/res768/size_band.md` lines 25–28 |
| seed noise | B0 20 ep, seeds 42/43/44 = **0.2774 / 0.28128 / 0.28020** → **±0.004** | `260814_1722_p1` · `260814_1833_b0-s43` · `260814_1835_b0-s44` |
| loss tricks are useless on rare classes | CE+Dice on the rare-10 class set: **+0.000**; strong aug **−0.007** | REPORT §7-7 line 86, `analysis/rare_class.md` |
| **LR trap (this is also the tonight-relevant one)** | U-Net sidewalk 20 ep: lr 6e-5 → **0.21802**, lr 3e-4 → **0.27465** (**+0.0566**) | `260814_1733_unet-r34_sidewalk_p1` vs `260814_1827_unet-r34_sidewalk_unet-lr3e4` |

---

## 6. "§9 capstone" — the elimination chain

REPORT §9 (lines 118–129) and DIGEST §0 (lines 25–31). Four links:

### 6a. Link ①: standard segmentation cannot read an occluded hazard

Erase the target's evidence pixels (GT dilated 15 px, filled with the image mean colour computed from
*outside* the cover) → target IoU retention **3–29 %**, and the vacated area is confidently filled
with flat-ground classes. Measured by `harness/occlusion_reliance.py`; table `OCCL` lines 17–23.

| model (run) | target | n | IoU clean → occluded | IoU retention | control retention |
|---|---|---|---|---|---|
| `unet-sat` (`260815_1304`) | sidewalk `flat-curb` | 146 | 0.5625 → 0.0644 | **11 %** | 99.8 % |
| `b2-sat100` (`260815_1411`) | `flat-curb` | 146 | 0.6542 → 0.0437 | **7 %** | 99.3 % |
| `m2f-sat40` (`260815_1443`) | `flat-curb` | 146 | 0.6776 → 0.1965 | **29 %** | 102.7 % |
| `m2f-ade` (`260815_1733`) | ADE `stairway` | 44 | 0.528 → **0.016** | **3 %** | 108 % |
| `ade-full-b2` (`260815_1025`) | ADE `stairway` | 44 | **0.432 → 0.030** | **7 %** | — (corrected value, see caveat C6) |

Where the vacated pixels go (`OCCL` lines 36–42): `b2-sat100` fills **73 % of the erased curb with
`flat-road`**. The failure is not a miss, it is a confident "safe flat ground".
Denominators: 146 sidewalk val images with ≥0.2 % `flat-curb` (scanned 200); 44 ADE val images with
≥0.2 % `stairway` (scanned 2000). Cover/GT area ratio 3.65× (curb), 1.8× (stairway).

### 6b. Link ②: the mechanism can be installed — 0.016 → 0.859 (53×)

Train with the same occlusion applied to the **input only, labels untouched, train split only**
(`common.py` `_SegDatasetBase._setup_occlusion`, contract at `common.py:113–124`).

| model | occlusion at train | occluded-stairway IoU | clean full mIoU |
|---|---|---|---|
| `m2f-ade` = `260815_1733_mask2former-tiny_ade20k_m2f-ade` | none (baseline) | **0.016** | 0.4652 |
| `ctx-ade-full-m2f` = `260817_1558_mask2former-tiny_ade20k_ctx-ade-full-m2f` | p=0.5, target position | **0.859** | **0.4724** |
| `ade-full-b2` = `260815_1025_segformer-b2_ade20k_ade-full-b2` | none (baseline) | **0.030** | 0.4445 |
| `ctx-ade-full-b2` = `260817_1318_segformer-b2_ade20k_ctx-ade-full-b2` | p=0.5, target position | **0.838** | **0.4464** |

- **53× = 0.859 / 0.016 = 53.7**. Evaluation set identical for both rows: the 44 occluded ADE val
  images. Source: WEB lines 498–516; `OCCL` line 23; REPORT §9-1 line 122; DIGEST §0-2 line 28.
- Both ctx runs: `occlude_class 60` (`stairway`), `occlude_mode class`, `ade_subset 20210`, lr 6e-5,
  512², seed 42; b2 20 ep batch 8 (2 chunks), m2f 14 ep batch 2 (4 chunks), `expected_fragile: true`.
- **Clean cost is zero at scale**: full-val mIoU went *up* (b2 0.4445→0.4464, m2f 0.4652→0.4724).
  The −0.1 cost seen on small data is absorbed by data volume (REPORT line 122, WEB line 541).

### 6c. Link ②′: the 10 % mixing curve (the number the supervision design turns on)

sidewalk `flat-curb` (class id 7), SegFormer-B2, 40 ep. **Both columns are absolute IoU measured on
the 146 curb-positive val images** by `occlusion_reliance.py` — *not* the full-val `per_class_iou.json`
numbers (see the warning below). Source: WEB lines 528–537; REPORT §9-1 line 125; DIGEST §3 line 53.

| train-time occlusion | clean IoU | occluded IoU | run dir |
|---|---|---|---|
| p = 0 (baseline) | 0.654 | 0.044 | `260815_1411_segformer-b2_sidewalk_b2-sat100` |
| **p = 0.10** | **0.591** | **0.696** | `260817_1237_segformer-b2_sidewalk_ctx-b2-p10` |
| p = 0.25 | 0.551 | 0.736 | `260817_1251_segformer-b2_sidewalk_ctx-b2-p25` |
| p = 0.50 | 0.530 | 0.771 | `260816_2045_segformer-b2_sidewalk_occl-b2-p50` |
| p = 0.75 | 0.458 | 0.795 | `260817_1304_segformer-b2_sidewalk_ctx-b2-p75` |
| **control: p=0.50 at random positions** | 0.606 | **0.004** | `260816_2111_segformer-b2_sidewalk_occl-b2-rnd50` |
| extreme: p = 1.0 (always occluded) | **0.000** | **0.813** | `260816_2058_segformer-b2_sidewalk_occl-b2-p100` |
| M2F at p = 0.5 | 0.598 | 0.860 | `260816_2124_mask2former-tiny_sidewalk_occl-m2f-p50` |

Readings for the paper: **10 % mixing installs most of the ability (0.044 → 0.696) at a clean cost of
−0.06**; diminishing returns after. The **random-position control collapsing to 0.004** is the
mechanism-specificity proof: the model did not learn "fill grey patches", it learned
*this position + this context → this class* (WEB line 545; REPORT line 123 states the same as "1 %"
retention — same fact, different unit). p = 1.0 is the strongest single result: a model that **never
saw a curb in the clear** scores 0.000 on clean curbs and **0.813** on occluded ones.

> **Denominator warning.** The full-val `per_class_iou.json` `flat-curb` values for the same runs are
> 0.6343 / 0.5749 / 0.5365 / 0.5160 / 0.4469 (p = 0/0.10/0.25/0.50/0.75), 0.5912 (rnd50), 0.000 (p=1.0).
> These are *different denominators* (all 200 val images, not the 146 positives). Do not mix the two
> series in one table.

### 6d. Link ③ + ④

③ = §1 of this document (0.57 % vs 0.61 %, no transfer).
④ = the conclusion: only real occlusion geometry **plus GT for the occluded region** can supply this
supervision, and only synthetic scenes can produce that pair (DIGEST §0-4 line 30; REPORT line 127).

---

## 7. NOT FOUND

- **Machine-readable per-p mixing-curve rows** — NOT FOUND. `analysis/occlusion_reliance.json` holds
  only the final 2026-08-17T20:40:50 invocation (7 rows: 3 curb models + 4 stairway models); the
  earlier invocation that produced the p = 0.10/0.25/0.50/0.75 and control rows was overwritten.
  The values survive only as prose/tables in `REPORT.md:125`, `negobs_digest.html:53`, and
  `final_report.html:528–537`. (Searched: `analysis/*.json`, `campaign/**/*.json` for the literals
  `0.696 0.591 0.736 0.795`, `logs/runs.log`.) Re-derivable by re-running
  `harness/occlusion_reliance.py` against the seven surviving `best.pt` files.
- **Paired-bootstrap / confidence-interval implementation** — NOT FOUND anywhere in
  `/home/vislab/Desktop/work_sy/ExProject_SR_HPE` (15 .py files, 0 notebooks) or in the campaign.
  Searched case-insensitively for `bootstrap|resample|percentile|confidence interval|ci_|paired`
  across `*.py *.ipynb *.md`; the only hits in the whole of `work_sy` are inside
  `Baseline_NegObs/neg_env/lib/.../site-packages` (torch/pandas/seaborn internals). See HARNESS_NOTES §7.
- **Grad-CAM / attribution code** — NOT FOUND. Searched `grad.?cam|gradcam|saliency|attribution|captum`
  over both repos; the single hit is the word "Attribution" in the CC-BY licence text of
  `campaign/data/construction/README.md`. See HARNESS_NOTES §8.
- **A "§0-3"-labelled section inside REPORT.md** — does not exist; REPORT has no §0. The label belongs
  to `negobs_digest.html`. (Resolved, not missing — see §0 numbering key.)
