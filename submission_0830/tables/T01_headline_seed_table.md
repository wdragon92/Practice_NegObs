# T01 · Headline table — recipe v2, 4 main rows (τ_op = 0.5)

<!-- LEDGER: experiments/dayrun_0820/runs/v2/SEED_TABLE.md:11-15 (rows 1-3), :58-60 (row 4 YOLO) -->
<!-- LEDGER: experiments/dayrun_0820/runs/v2/SEED_TABLE.md:9 (mandatory reading banner) -->
<!-- LEDGER: experiments/dayrun_0820/runs/yolo_s{42,43,44}/eval_test/metrics.json block point.op -->
<!-- NO NUMBER IN THIS FILE WAS RECOMPUTED. Values transcribed verbatim from SEED_TABLE.md. -->

- **Corrected-GT status**: **OLD GT (published)**. H / E / off-arm columns are **byte-identical**
  under corrected GT (D59 ①, D65 ④). **The V column moves** under corrected GT — see T06.
- **Provenance**: `experiments/dayrun_0820/runs/v2/SEED_TABLE.md` §1 + §4 (정본, banner included)
- **Population**: test-core 816 frames · 408 on / 408 off · 7 scenes · grid PROVISIONAL-GRID-V1 (20 cells)
- **Spread convention**: `mean ± range/2` over 3 seeds. **This is seed variability, not a CI.**
  RT-B note: for n = 3, range/2 under-estimates σ by ~15 %; v3 pre-registration switches to sample sd
  (ddof = 1) — `experiments/v3_0823/ACCOUNTING.md` §4.9-1.

---

## 1. Main table (4 rows)

| model | n seeds | frame_recall_H | frame_recall_E | frame_recall_V | frame_det_rate | frame_fa_off | cell_fpr_off | cell_f1 | cell_recall | cell_precision |
|---|---|---|---|---|---|---|---|---|---|---|
| rgb | 3 | 0.688 ± 0.141 | 0.556 ± 0.378 | 0.796 ± 0.164 | 0.730 ± 0.179 | 0.359 ± 0.127 | 0.047 ± 0.016 | 0.450 ± 0.102 | 0.385 ± 0.125 | 0.566 ± 0.021 |
| depth | 3 | 0.438 ± 0.031 | 0.600 ± 0.000 | 0.917 ± 0.042 | 0.716 ± 0.014 | 0.042 ± 0.029 | 0.009 ± 0.008 | 0.677 ± 0.031 | 0.652 ± 0.031 | 0.705 ± 0.031 |
| b2 | 3 | 0.229 ± 0.156 | 0.178 ± 0.267 | 0.730 ± 0.111 | 0.499 ± 0.148 | 0.238 ± 0.143 | 0.035 ± 0.029 | 0.340 ± 0.075 | 0.276 ± 0.121 | 0.527 ± 0.108 |
| yolov8n @ **τ 0.25** | 3 | **0.000 ± 0.000** | **0.000 ± 0.000** | 0.150 ± 0.028 | 0.083 ± 0.015 | 0.024 ± 0.018 | 0.0015 ± 0.0010 | 0.026 ± 0.002 | 0.014 ± 0.001 | 0.472 ± 0.110 |

Distance-band columns (same rows, same seeds):

| model | band1_cell_recall | band2_cell_recall | band3_cell_recall | band4_cell_recall | band1_cell_fpr_off | band2_cell_fpr_off | band3_cell_fpr_off | band4_cell_fpr_off |
|---|---|---|---|---|---|---|---|---|
| rgb | **0.000 ± 0.000** | 0.265 ± 0.097 | 0.297 ± 0.103 | 0.511 ± 0.206 | 0.000 ± 0.000 | 0.010 ± 0.004 | 0.041 ± 0.021 | 0.136 ± 0.064 |
| depth | 0.188 ± 0.064 | 0.579 ± 0.032 | 0.671 ± 0.110 | 0.701 ± 0.051 | 0.000 ± 0.000 | 0.011 ± 0.015 | 0.013 ± 0.013 | 0.012 ± 0.006 |
| b2 | **0.000 ± 0.000** | 0.160 ± 0.071 | 0.244 ± 0.134 | 0.354 ± 0.138 | 0.000 ± 0.000 | 0.009 ± 0.010 | 0.033 ± 0.040 | 0.097 ± 0.066 |
| yolov8n | 0.123 ± 0.030 | 0.056 ± 0.007 | 0.001 ± 0.001 | 0.000 ± 0.001 | — | — | — | — |

## 2. Twin on−off delta + τ*

| model | n seeds | twin Δ (all) | twin Δ (H tier) | τ* | best epoch |
|---|---|---|---|---|---|
| rgb | 3 | 0.314 ± 0.007 | 0.285 ± 0.094 | 0.55 ± 0.20 | 19.0 ± 8.0 |
| depth | 3 | 0.608 ± 0.078 | 0.407 ± 0.037 | 0.39 ± 0.20 | 16.0 ± 13.5 |
| b2 | 3 | 0.234 ± 0.038 | 0.110 ± 0.059 | 0.45 ± 0.00 | 5.7 ± 3.5 |

---

## CAVEAT LINE — must be printed with this table, without exception

> **The H column is not a model comparison.** rgb 0.688 and depth 0.438 are read at **different
> operating points**: off-arm FA 0.359 vs 0.042, an **8.6×** gap. At matched FA, **Depth ≥ RGB at
> every point** (FA .359 → .781 vs .729 · FA .10 → .510 vs .326 · FA .05 → .479 vs .243), and the
> **cell axis strengthens the same ordering** (Δ +0.32–+0.43). Any citation of the H column must
> carry the **dual-axis** FA-matched table (T02). — `SEED_TABLE.md:9`, `ACCOUNTING.md` §4.8 #1 / §4.9-2

> **The YOLO row's E/H = 0 is a property of our `det2cell` adapter, not of detection.** The
> adapter-free, twin-conditional statement is in T12. — `SEED_TABLE.md:75-84`, `METRICS.md` §RT.3

> **twin Δ (H tier) rests on 2 scenes** (scene14 n = 60 · scene15 n = 36); scene14 carries the
> effect and scene15 is indistinguishable from zero. **No CI is reportable for H or E** (T11).
> — `SEED_TABLE.md:25`, `METRICS.md` §RT.5

> **§5 of `SEED_TABLE.md` (aux ablation, rgb_s42) is APPENDIX ONLY** and must not enter this table
> (approval #2). Its `cell_recall_H +0.3546` significance is **withdrawn** (T11).
> Additionally, **all 9 main-table runs are aux OFF** — do not describe the main models as having
> trained aux heads. — `ACCOUNTING.md` §4.9-4 (N-5, D64)
