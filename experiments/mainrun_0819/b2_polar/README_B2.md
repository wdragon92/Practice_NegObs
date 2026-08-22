# SegFormer-B2 polar arm (b2_polar/)

MiT-B2 encoder + `Linear(512, n_cells)` multi-label head, loaded OFFLINE from `campaign/data/hf_local/nvidia__mit-b2` (safetensors; transformers 5.15 refuses `.bin` on torch 2.5.1 — do not upgrade torch). Everything else is `../code/` unchanged: same manifest contract, `[B,n_cells]` logits, `BCEWithLogitsLoss`, and the same **recipe v2** flags (`--grid --hflip --oversample-h --bias-init`, checkpoint selection on `0.5*val_F1 + 0.5*val_H_recall`) — table fairness demands all three models share them. The cell count comes from `../code/gridspec.py`; `--grid gridspec_v1.json` gives the 20-cell head, and `build(..., classes=N)` is the only knob.

**Dry run (CPU, no GPU, no network)** — GREEN 2026-08-19 @15 cells (24.204 M params, 1.31 s/step); re-GREEN 2026-08-20 @**20 cells** (24.207 M params, 2.13 s/step CPU, route `imgcls`, only `classifier.{weight,bias}` re-initialised):
```bash
cd b2_polar && CUDA_VISIBLE_DEVICES="" PYTHONNOUSERSITE=1 HF_HUB_OFFLINE=1 \
  /home/vislab/miniconda3/envs/env_seg/bin/python dryrun.py [--grid gridspec_v1.json]
```
**Real run (tomorrow, once `../dataset_manifest_v1.json` + `../split_v1.json` exist)** — caller holds the GPU lock:
```bash
flock -o -w 55 -E 201 /tmp/negobs_gpu.lock nice -n 5 env PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 HF_HUB_OFFLINE=1 \
  /home/vislab/miniconda3/envs/env_seg/bin/python train_b2_polar.py --input rgb \
  --manifest ../dataset_manifest_v1.json --split ../split_v1.json --out ../runs/b2_rgb
# then: python eval_b2_polar.py --ckpt ../runs/b2_rgb/best.pt --manifest ../dataset_manifest_v1.json --split ../split_v1.json --input rgb --out ../runs/b2_rgb/eval
```
Defaults match `train_polar.py` except `--lr 6e-5` (transformer convention; `--lr` still overridable). `--route {auto,imgcls,semseg-gap}` selects the head.

**VRAM / time (HARNESS_NOTES §5, RTX 4090 fp32 512² batch 8):** ≤9.71 GB peak, ~18.3 s/epoch on 800/200 — i.e. `t_epoch ≈ 2·(N_train/99 + N_val/220)` s, ~2× the U-Net arm. 9.71 GB is the 27.37 M seg variant; the default 24.20 M classification head is under that. Fits a 24 GB 4090 **alone** (~14 GB headroom) — it does **not** co-exist with a render.
