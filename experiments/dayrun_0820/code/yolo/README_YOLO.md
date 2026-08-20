# README_YOLO.md — the YOLOv8n track, end to end

DAYRUN 0820 Phase 5. Everything here lives under
`experiments/dayrun_0820/` and touches nothing outside
`code/yolo/`, `annotations/amodal/`, `yolo_ds/`, `runs/yolo_s*/`, `venv_yolo/`.

The mapping rule and its measured ceiling are in
[`../../METRICS_NOTES_yolo.md`](../../METRICS_NOTES_yolo.md) — **read §3 before
reading any number this track produces.**

---

## 0. Environment — prepend to every command

```bash
cd /home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820
unset PYTHONPATH VIRTUAL_ENV
export PYTHONNOUSERSITE=1                       # this machine's ~/.local shadows envs
export YOLO_CONFIG_DIR=$PWD/venv_yolo/ultralytics_cfg   # keeps ultralytics' settings in-tree
PY=$PWD/venv_yolo/bin/python
```

`venv_yolo` is this track's own interpreter and is **not** `env_seg`. Do not
`conda activate` anything for steps 1–6; step 7 (eval) runs in `env_seg` because
`eval_polar.py` imports the training stack.

| | pinned |
|---|---|
| python | 3.10.12 (`python -m venv`) |
| **ultralytics** | **8.4.123** |
| torch / torchvision | 2.13.0+cu130 / 0.28.0 |
| numpy / scipy / opencv / pillow | 2.2.6 / 1.15.3 / 5.0.0.93 / 12.3.0 |
| weights | `venv_yolo/weights/yolov8n.pt` (COCO, 6.5 MB, vendored — no download at train time) |
| full freeze | `code/yolo/requirements_yolo.txt` (237 packages) |

`scipy` is **not** an ultralytics 8.4 dependency but is installed on purpose:
`labeler.connected_components` falls back to a pure-python union-find without it,
which is unusably slow on the 321×321 heightmaps.

Driver 580.173.02 / CUDA 13.0 matches the `+cu130` wheels. While the render owns
the GPU, add `export CUDA_VISIBLE_DEVICES=""` and pass `--device cpu`.

---

## 1. Amodal masks

```bash
$PY code/yolo/amodal_masks.py \
    --manifest dataset_manifest_v2.json \
    --labels   annotations/labels_v1.json \
    --out      annotations/amodal --workers 4
```
≈ 16 s for 1584 frames. Writes `annotations/amodal/<arm>__<scene>__<file>.png`
(960×540, 0/255) for every on-arm frame with a hazard in view, plus
`annotations/amodal/bboxes.json` — the box contract read by step 2.
Off-arm frames get no PNG and an empty box list.

Self-test (3 frames: scene04 V, scene14 H, scene18 E) — run it whenever the
manifest, the labels or the heightmaps change:

```bash
$PY code/yolo/amodal_masks.py --manifest dataset_manifest_v2.json \
    --labels annotations/labels_v1.json --selftest
```

**If the boost render lands a new manifest**, re-run step 1 against it and then
steps 2–6 again. The boost rounds are twins like the main ones, so nothing else
changes; `--labels` is optional but keep it — it is what proves the projected
footprint is byte-identical to the one the labeler used.

## 2. Ultralytics dataset (symlinks, no copies)

```bash
$PY code/yolo/make_yolo_dataset.py \
    --bboxes annotations/amodal/bboxes.json \
    --split  split_v2.json \
    --out    yolo_ds
```

```
train  912 frames (456 on / 456 off)  3573 boxes  576 background  19 scenes
val    144 frames ( 72 on /  72 off)    96 boxes   72 background   3 scenes
test   336 frames (168 on / 168 off)   948 boxes  192 background   7 scenes
excluded: hold = scene11, scene13, scene19, sceneD4 (192 frames)
```

Add `--dry-run` to print that table without touching the disk.

## 3. CPU sanity fit (proves the pipeline, ~5 s)

```bash
CUDA_VISIBLE_DEVICES="" $PY code/yolo/train_yolo.py --mode sanity --device cpu
```
2 images (one boxed, one background), 1 epoch, imgsz 128. Builds a throwaway dir
under `runs/_sanity_tmp/`, asserts `best.pt` exists, deletes it. `--keep` keeps it.

## 4. Three seed trainings — **GPU, only after the render releases it**

```bash
for S in 42 43 44; do
  $PY code/yolo/train_yolo.py --mode train --seed $S --device 0
done
```
Defaults are the brief's: `yolov8n.pt`, `imgsz 512`, `epochs 60`, `batch 16`,
`deterministic=True`, `patience 15`. Run dir: `runs/yolo_s<seed>/`,
best weights at `runs/yolo_s<seed>/weights/best.pt`.

One job at a time — the GPU guard in this repo is "render first, then one training
job". Nothing here checks that for you.

## 5. Predict on test (and on val, for τ\*)

```bash
for S in 42 43 44; do
  $PY code/yolo/train_yolo.py --mode predict --seed $S --device 0 \
      --subset test --pred-conf 0.05
  $PY code/yolo/train_yolo.py --mode predict --seed $S --device 0 \
      --subset val  --pred-conf 0.05
done
```
Writes `runs/yolo_s<seed>/pred_<subset>/labels/*.txt` with `save_txt=True
save_conf=True`.

> **`--pred-conf` is a floor, not the operating point.** Detections below it are
> never written, so a later sweep down to 0.1 would be a sweep over a truncated
> set. Keep it below the lowest threshold you intend to report.

## 6. Detection → cell

```bash
for S in 42 43 44; do
  for SUB in test val; do
    $PY code/yolo/det2cell.py \
        --pred-labels runs/yolo_s$S/pred_$SUB/labels \
        --subset $SUB --conf 0.05 \
        --out runs/yolo_s$S/det2cell_$SUB
  done
done
```
Produces `runs/yolo_s<seed>/det2cell_<subset>/per_frame.csv` in the exact
`eval_polar` format (`p_<cell>` = the strongest detection confidence claiming that
cell, `g_<cell>` = the manifest's `polar_gt`), for **both arms**.

> **`--conf 0.05`, not 0.25, is deliberate.** `p[c] = max conf over detections
> claiming c`, so `{p[c] ≥ τ}` is exactly `{some detection with conf ≥ τ claims c}`:
> thresholding here and thresholding in `eval_polar` are the *same operation*. Map
> once at the floor and let `eval_polar --tau-op / --tau-sweep` do the whole
> {0.1 … 0.5} sweep from one CSV. Thresholding in both places would silently apply
> `max(τ_conf, τ_op)`.
> `--conf-sweep 0.1,0.2,0.3,0.4,0.5` exists as a cross-check and writes
> `conf_<τ>/per_frame.csv` subdirs; the two routes must agree.

Unit check (no predictions needed, ~2 s):
```bash
$PY code/yolo/det2cell.py --unit-check
```

Mapping-rule ceiling — worth re-running whenever the amodal masks change, because
it is the honest upper bound on everything below:
```bash
$PY code/yolo/det2cell.py --oracle-boxes annotations/amodal/bboxes.json \
    --subset test --out runs/yolo_oracle_ceiling_test
```

## 7. eval_polar + twin_analysis — **`env_seg`, not `venv_yolo`**

```bash
conda activate env_seg
export PYTHONNOUSERSITE=1
cd /home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820
MC=../mainrun_0819/code

for S in 42 43 44; do
  # tau* : fit on VAL cell-F1 first (--tau-star auto needs a --ckpt, which a
  # per-frame-a run has not got, so it must be read off the val sweep by hand)
  python $MC/eval_polar.py --per-frame-a runs/yolo_s$S/det2cell_val/per_frame.csv \
      --grid gridspec_v1.json --out runs/yolo_s$S/eval_val \
      --tau-op 0.25 --tau-star 0.25 \
      --tau-sweep 0.05,0.1,0.15,0.2,0.25,0.3,0.35,0.4,0.45,0.5
  # -> read the tau with the best cell_f1 out of runs/yolo_s$S/eval_val/metrics.json
  #    ("sweep") and pass it as --tau-star below.

  python $MC/eval_polar.py --per-frame-a runs/yolo_s$S/det2cell_test/per_frame.csv \
      --grid gridspec_v1.json --out runs/yolo_s$S/eval_test \
      --tau-op 0.25 --tau-star <the val-fitted tau> \
      --tau-sweep 0.1,0.2,0.25,0.3,0.4,0.5

  # twin: the SAME csv carries both arms, so it is passed twice on purpose
  python $MC/twin_analysis.py \
      --per-frame-on  runs/yolo_s$S/det2cell_test/per_frame.csv \
      --per-frame-off runs/yolo_s$S/det2cell_test/per_frame.csv \
      --manifest dataset_manifest_v2.json --grid gridspec_v1.json \
      --out runs/yolo_s$S/twin_test
done
```

**Table fairness.** Row 4 must be evaluated with the *identical* `eval_polar` /
`twin_analysis` flags as rows 1–3 (`--grid`, `--tau-op`, `--pose-keys`, `--tol`,
`--n-boot`, `--seed`). If Phase 4 settles on a different `--tau-op` or on the D20
`|Δground_z| ≤ 0.15` twin tolerance, change it here too before reporting.

Aggregate the three seeds the way Phase 4 does (mean ± range) —
`$MC/aggregate_seeds.py` if it fits the layout.

---

## 8. Reading the result

The brief's expectation, now measured rather than assumed
(`METRICS_NOTES_yolo.md` §3):

* **H recall ≈ 0 is structural.** With the GT boxes themselves fed in as perfect
  detections, H recall is **0.000** and E recall is **0.000**. So a nonzero H in a
  trained run is not a good result — it is a **mapping leak**, and the first suspects
  are (i) a box whose bottom edge coincidentally lands on a far GT cell, (ii) an
  off-by-one in `frame_id_of_stem`, (iii) a `--grid` mismatch between det2cell and
  eval_polar. Investigate before reporting.
* The whole YOLO row is capped at **frame-detection 0.404 / cell-recall 0.074** by
  the adapter. Report the ceiling row next to the model row, or the table will read
  as "the detector is bad" when it mostly says "the adapter is lossy".
* Frame FA on the off arm is **0.000** at the ceiling, so whatever FA the trained
  model shows is entirely its own — the most informative single number in the row.

---

## 9. Files

| path | what |
|---|---|
| `code/yolo/common.py` | path bootstrap + the only place `labeler`/`gridspec` are imported |
| `code/yolo/amodal_masks.py` | footprint → amodal mask PNG + `bboxes.json` (`--selftest`) |
| `code/yolo/make_yolo_dataset.py` | symlink dataset + `data.yaml` (`--dry-run`) |
| `code/yolo/det2cell.py` | detections → `per_frame.csv` (`--unit-check`, `--oracle-boxes`) |
| `code/yolo/train_yolo.py` | train / predict / sanity wrapper |
| `code/yolo/requirements_yolo.txt` | pip freeze of `venv_yolo` |
| `annotations/amodal/` | 552 mask PNGs + `bboxes.json` (4617 boxes) |
| `yolo_ds/` | images (symlinks) + labels + `data.yaml` + `build_report.json` |
| `../../METRICS_NOTES_yolo.md` | the mapping rule, its properties, its measured ceiling |

No script in this directory re-implements a projection, an unprojection, a
sector/band test or a footprint. All of it is imported from
`mainrun_0819/code/labeling/labeler.py`; if that file changes, re-run
`amodal_masks.py --selftest` and `det2cell.py --unit-check` before trusting
anything here.
