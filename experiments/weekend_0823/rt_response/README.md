# rt_response — RED-TEAM RESPONSE workroom (D35)

New analyses answering `experiments/weekend_0823/redteam/{R1_novelty,R2_method,R3_repro}.md`.
**CPU only · GPU untouched (the V2S queue owns it) · every input is a frozen artefact ·
no canonical file edited in place.**  The two canonical documents were extended by
**append-only** blocks (`METRICS.md` §RT.1–RT.8, `RESULTS_DRAFT.md` §RT-A–RT-F); the staged
copies of those blocks are `APPEND_METRICS.md` and `APPEND_RESULTS_DRAFT.md` here.
The consolidated 지적→대응→잔여리스크 ledger is
`../redteam/REDTEAM_0823.md`.

## Deliverables

| # | question | report | data | figure |
|---|---|---|---|---|
| F1 | Does the H-tier ordering survive matched false alarms? | `F1_FA_MATCHED.md` | `f1_fa_matched.json` | `figs/fig_f1_recall_vs_fa.png` / `.pdf` |
| F2 | How much of each arm's H recall is hazard-conditional? | `F2_TWIN_CONDITIONAL.md` | `f2_twin_conditional.json` | — |
| F3 | Does the detector fire near hidden hazards without our adapter? | `F3_ADAPTER_FREE_YOLO.md` | `f3_adapter_free_yolo.json` | — |
| F4 | How loud is the tier that is in no denominator? | `F4_NONE_IN_FOV.md` | `f4_none_in_fov.json` | — |
| F5 | Which confidence intervals survive scene clustering? | `F5_CLUSTER_CI.md` | `f5_cluster_ci.json` | — |
| F7 | What is still visible in a strict-H twin pair? | `F7_HPAIR_PIXDIFF.md` | `f7_hpair_pixdiff.json`, `f7b_noisefloor.json` | `panels/h_diff_contact_sheet.png` + 6 panels |

## Headline results

- **F1** — R1's published FA-matched table reproduces to three decimals (12/12 values).  At every
  matched FA, Depth ≥ RGB on the H tier; the gap grows from +0.052 at FA 0.359 to +0.236 at FA 0.05.
  Claim downgraded from "RGB leads" to "RGB is not zero" (0.326 ± 0.229 at FA 0.10).
- **F2** — Twin-conditional H recall: RGB 0.688 → **0.375**, Depth 0.438 → **0.438**, B2 0.229 →
  **0.122**.  Depth's H response is 100 % hazard-conditional (0/96 pairs fire on the deleted twin,
  all three seeds); 44.7 % of RGB's H firings are unconditional.
- **F3** — Without the adapter, H IoU>0 = 0.066, i.e. **not** the constructive zero the draft
  claims — but the hazard-blind twin baseline is 0.076, so the **twin-conditional rate is −0.010**
  against **+0.337** on V.  The paradigm claim survives only in twin-conditional form, and only at
  the operating confidence (at the 0.05 storage floor it is +0.142).
- **F4** — `FA_in-scene` on the 81 uncounted frames: RGB **0.798**, Depth **0.494**, B2 **0.638**,
  against reported off-arm FA of 0.359 / 0.042 / 0.238.  sceneN3's null control is saturated for
  RGB (0.75–1.00 on both arms) and genuinely quiet for Depth (0.000–0.125).
- **F5** — Cluster CIs widen FA by ×1.7–5.6; H (2 clusters) and E (1 cluster) get no CI at all.
  The aux `cell_f1` gain dies ([0.0001, 0.0786] → [−0.258, 0.205]) **and so does `cell_recall_H`**
  (+0.3546 → [−0.143, 0.463]), which `SEED_TABLE` §5.2 calls the largest confirmed effect.
- **F7** — **0 of 96 strict-H pairs are optically identical.**  Median residual 4.5 % of the frame
  at ≥ 32/255 (renderer noise floor at that level: 50 px, measured on a geometrically identical
  render pair).  scene14's residual is 22× scene15's — the same split that carries the twin Δ.

## Reproduce

```bash
unset PYTHONPATH VIRTUAL_ENV
export PYTHONNOUSERSITE=1
PY=/home/vislab/miniconda3/envs/env_seg/bin/python
cd /home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/rt_response/code
$PY f1_fa_matched.py && $PY f2_twin_conditional.py && $PY f3_adapter_free_yolo.py \
  && $PY f4_none_in_fov.py && $PY f5_cluster_ci.py \
  && $PY f7b_noisefloor.py && $PY f7_hpair_pixdiff.py && $PY f7_report.py \
  && $PY fig_f1_curves.py && $PY fig_f7_panels.py
$PY make_appends.py      # idempotent: refuses to append a second time
```

`code/common_rt.py` holds the shared dump loaders; `code/wedge_util.py` rasterises the polar
wedges and the amodal silhouette using the canonical `labeling/labeler.py` camera model
(imported, never re-derived).

## Inputs (all read-only)

`experiments/dayrun_0820/runs/v2/*/eval_test/per_frame.csv` ·
`experiments/dayrun_0820/runs/v2/*/twin/twin_pairs.csv` ·
`experiments/dayrun_0820/runs/yolo_s{42,43,44}/pred_test/labels/` ·
`experiments/dayrun_0820/annotations/amodal/{bboxes.json,*.png}` ·
`experiments/dayrun_0820/{dataset_manifest_v2_full.json,split_v2_full.json}` ·
`experiments/mainrun_0819/code/labeling/{labeler.py,gridspec_v1.json}` ·
`dataset/v2_corpus/260819_main_{on,off}/` · `dataset/v2_probes/260820_ctrloff/`.

Figure colours are slots 1–3 of the dataviz reference palette (blue `#2a78d6` / orange `#eb6834` /
aqua `#1baf7a`), used unchanged — the documented all-pairs-validated subset in both modes — plus
that palette's single-hue blue ramp for the sequential difference maps.  Every series is also
directly labelled, so identity is never carried by colour alone.
