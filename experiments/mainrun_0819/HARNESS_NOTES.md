# HARNESS_NOTES.md — reusing the segmentation-campaign harness for tonight's run

Target: **U-Net + 15-logit polar-grid head, BCEWithLogitsLoss, RGB 512×512 batch 8**, a **depth-input
twin**, and later a **SegFormer-B2 dry run**. Everything below was read out of the campaign tree and,
where marked ✅, executed read-only in `env_seg` this session to confirm the API.

`HARNESS = /home/vislab/Desktop/work_sy/Practice_Segmentation/campaign/harness`

---

## 1. Environment

**Conda env: `env_seg`.** Hard-coded in `common.py:44` as
`PYENV = "/home/vislab/miniconda3/envs/env_seg/bin/python"`. Use that interpreter path directly;
`conda activate` is not needed and the harness never does it.

✅ Verified live (`PYTHONNOUSERSITE=1 <PYENV> -c "import ..."`):

| package | version | why it matters tonight |
|---|---|---|
| torch | **2.5.1+cu124** | pinned; do **not** upgrade (see safetensors note in §6) |
| torchvision | 0.20.1+cu124 | |
| transformers | **5.15.0** | SegFormer/Mask2Former path |
| datasets | 5.0.1 | only used by the `sidewalk` HF dataset loader — irrelevant for our PNG dataset |
| segmentation-models-pytorch | **0.5.0** | U-Net + the classification-head hook we need |
| albumentations | 2.0.8 (+ `albumentations.pytorch.ToTensorV2`) | transform pipeline |
| timm | 1.0.28 | smp encoder backend |
| numpy | 2.2.6 · scipy | scipy **1.15.3** present → `scipy.stats.bootstrap` is available (see §7) |
| huggingface-hub | 1.27.0 · safetensors 0.8.0 · accelerate 1.14.0 | |
| opencv (`cv2`) | 5.0.0 | interpolation flags in `build_transform` |
| **sklearn** | **absent** | intentional — the machine's `~/.local` has a broken old sklearn; do not import it |

**`PYTHONNOUSERSITE=1` is mandatory on every invocation, pip included.** Reason recorded at
`REPORT.md:17`: this machine's `~/.local` user-site is polluted and shadows env packages.
The harness enforces it by injecting `CHILD_ENV` into every spawned process
(`common.py:50–55`): `PYTHONNOUSERSITE=1`, `PYTHONUNBUFFERED=1`, `OMP_NUM_THREADS=8`.

**GPU lock.** Shared with the NegObs scene workflow: `GPU_LOCK = /tmp/negobs_gpu.lock`
(`common.py:45`). The exact spawn line is `runner.py:169–186`:

```
flock -o -w 55 -E 201 /tmp/negobs_gpu.lock  nice -n 5  env PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 \
      /home/vislab/miniconda3/envs/env_seg/bin/python <HARNESS>/run_experiment.py <config.json>
```

- **`-o` is not optional.** Without it a DataLoader worker inherits the lock fd and the lock is never
  released (real incident, 08-11, documented at `runner.py:176–178` and `REPORT.md:22`).
- `-w 55 -E 201` = wait 55 s then exit 201, which the runner treats as "busy, retry quietly".
- Second guard: `run_experiment.guard_gpu_free()` (`run_experiment.py:46–53`) calls
  `common.gpu_busy()` (nvidia-smi compute-apps query) **before touching `torch.cuda`** and exits 202
  if anything else is resident.
- Long runs yield the lock at epoch boundaries: `run_experiment.py:394–397` returns **exit 75** past
  `CHUNK_LIMIT_SEC` after saving `latest.pt`; the runner re-queues the same config. Keeps the scene
  workflow's max wait to one chunk. Tonight's runs are short enough that this will not fire.

---

## 2. Model construction — and the 15-logit seam

### What the campaign actually built

`common.build_model(name, num_labels, from_scratch=False)` — `common.py:1084–1119`. All five models
return a wrapper guaranteeing `forward(x) -> [B, num_labels, H, W]` at input resolution.

```python
# common.py:1093-1097  (the two smp lineages)
if name == "unet-r34":
    return SmpModel(smp.Unet("resnet34", encoder_weights=enc_w, classes=num_labels))
if name == "dlv3p-r50":
    return SmpModel(smp.DeepLabV3Plus("resnet50", encoder_weights=enc_w, classes=num_labels))
```

- **Encoder / weights**: `resnet34`, `encoder_weights="imagenet"` (timm/smp ImageNet weights,
  auto-downloaded and cached). `from_scratch=True` ⇒ `encoder_weights=None`.
  Measured params: **24.44 M**; peak VRAM at 512²/batch 8/fp32 = **4.20–4.29 GB**.
- **Normalisation is ImageNet** (`common.py:109–110`), matching those encoder weights.
- `freeze_encoder(model)` (`common.py:1121`) uses `model.encoder_parameters()` → `net.encoder.parameters()`.

**There is no non-dense-head precedent in the harness.** Every one of the ~1,014 runs is a dense
`[B,C,H,W]` model trained with `CrossEntropyLoss(ignore_index=0)` (`common.build_loss`,
`common.py:1134–1151`, options `ce` / `ce_dice` only) and scored by a GPU confusion matrix
(`common.ConfusionMatrix`, `common.py:1153`). The 15-logit vector head is genuinely new code.

### Does `smp.Unet(classes=15)` give a vector? No — but smp has the exact hook you want ✅

`smp.Unet(classes=15)` returns a **dense** `[B,15,512,512]` mask, not a vector. The right seam is
smp's built-in **`aux_params` classification head**, verified this session:

```python
# segmentation_models_pytorch.base.ClassificationHead  (verified source, smp 0.5.0)
#   AdaptiveAvgPool2d(1) -> Flatten -> Dropout(p) -> Linear(encoder_out_ch, classes) -> Activation
```

and `smp.Unet.__init__` signature (verified) accepts
`(encoder_name, encoder_depth, encoder_weights, ..., in_channels, classes, activation, aux_params)`.

**Recommended minimal path (A) — smp U-Net with `aux_params`, ~5 lines:**

```python
import segmentation_models_pytorch as smp
net = smp.Unet(
    "resnet34", encoder_weights="imagenet",
    in_channels=3,            # depth twin: 1 (or 4 for RGB-D) — smp re-weights conv1 for you
    classes=1,                # dense head kept but unused (see trade-off below)
    aux_params=dict(classes=15, pooling="avg", dropout=0.2, activation=None),  # activation=None => raw logits
)
mask, logits = net(x)         # logits: [B, 15] float, feed straight to BCEWithLogitsLoss
```

- `activation=None` is required — BCEWithLogitsLoss must receive raw logits.
- The head is `Linear(512, 15)` (resnet34 final `out_channels` = 512, ✅ verified
  `get_encoder("resnet34").out_channels == [3,64,64,128,256,512]`).
- **Trade-off**: the U-Net decoder still runs and costs ~half the FLOPs for an output you discard.
  Two ways to spend it well: (i) leave it, and later attach a dense auxiliary target for free;
  (ii) drop it.

**Path (B) — encoder + custom head, no decoder (~10 lines, ≈2× faster/epoch):**

```python
from segmentation_models_pytorch.encoders import get_encoder
enc = get_encoder("resnet34", in_channels=3, depth=5, weights="imagenet")   # ✅ signature verified
head = nn.Sequential(nn.AdaptiveAvgPool2d(1), nn.Flatten(),
                     nn.Dropout(0.2), nn.Linear(enc.out_channels[-1], 15))
logits = head(enc(x)[-1])
```

**Verdict for tonight**: take **path (A)**. It is one constructor call, it keeps `encoder_weights`,
`in_channels`, and `freeze_encoder` semantics identical to the campaign's U-Net (so the epoch-time
and VRAM numbers in §5 transfer directly), and it leaves the door open for a dense auxiliary loss.
Switch to (B) only if epoch time becomes the constraint.

**Depth twin**: `in_channels=1` (or 4). smp calls `encoder.set_in_channels(n, pretrained=True)`
(✅ attribute confirmed present) which re-weights `conv1` from the pretrained RGB kernel instead of
re-initialising it. Two things to change alongside: use depth-appropriate normalisation constants
(ImageNet mean/std are wrong for a depth channel — normalise by your metric range, e.g.
`(d - d_mean)/d_std` computed over the render set), and keep the RGB twin's constants untouched so
the two arms stay comparable.

---

## 3. The lr = 3e-4 evidence

| item | value | provenance |
|---|---|---|
| campaign default for all models | `lr: 6e-05` | `plan_full.py:23` `STD = dict(kind="train", dataset="sidewalk", batch=8, lr=6e-5, seed=42, train_fraction=1.0, freeze_encoder=False, from_scratch=False, img_size=512)` — every queue config inherits this |
| U-Net at the default | mIoU **0.21802** @ ep 18 | `runs/260814_1733_unet-r34_sidewalk_p1/done.json` (`"lr": 6e-05`) |
| **U-Net at 3e-4** | mIoU **0.27465** @ ep 19 (**+0.0566**) | `runs/260814_1827_unet-r34_sidewalk_unet-lr3e4/config.json` → `"lr": 0.0003`; `done.json` → `"best_miou": 0.27465` |
| purpose string in that config | *"LR 보정: CNN 계열에 6e-5 가 불리했는지 3e-4 로 재확인"* | same `config.json` |
| written up as a caveat | REPORT `§6-4` line 60; DIGEST §7 line 88 ("동일조건 비교의 함정 사례") | |

Note the evidence is **single-seed, sidewalk, 20 ep, dense CE**, not a sweep — it establishes
"3e-4 ≫ 6e-5 for resnet34-U-Net" and nothing finer. There is **no** `lr` value validated for a
BCE vector head. Take 3e-4 as the starting point, keep `weight_decay=0.0` (what the harness uses,
`run_experiment.py:247`), and log the loss curve on the first run rather than trusting it.

---

## 4. Data loading — and how a PNG + JSON-manifest dataset plugs in

**Structure** (`common.py`): one tiny class per dataset, all sharing `_SegDatasetBase`
(`common.py:499–538`), dispatched by `build_dataset(dataset, split, ...)` (`common.py:913–941`).
Existing classes: `SidewalkDataset` (540) · `ADE20KDataset` (567) · `PotholeDataset` (689) ·
`ConstructionDataset` (771) · `TerrainDataset` (887). Each implements only `__init__`, `__len__`,
`__getitem__`, and calls `self._apply(img_np, mask_np, i)` — they are plain duck-typed objects,
**not** `torch.utils.data.Dataset` subclasses (`common.py:544` comment says so explicitly).

**Augmentation** (`common.build_transform`, `common.py:375–405`):

```python
standard (train): A.Resize(S, S, INTER_LINEAR, mask_interpolation=INTER_NEAREST)
                  A.HorizontalFlip(p=0.5)
                  A.Normalize(mean=(0.485,0.456,0.406), std=(0.229,0.224,0.225))
                  ToTensorV2()
val / eval      : Resize + Normalize + ToTensorV2   (no flip — augment=False)
strong          : RandomResizedCrop(scale 0.5–1.0) + HFlip + ColorJitter(0.3/0.3/0.3/0.05)
```

Squash resize (aspect not preserved) is deliberate and campaign-wide. **Note for tonight**:
`HorizontalFlip` is only valid for the polar-grid head if you also **permute the 15 bins**
(mirror the sector index). If you do not want to write that permutation, set `augment=False`
for the first run — the campaign's own finding is that strong aug hurts at this data scale
(−0.007, REPORT §6-4) so flip is a small loss.

**Minimum-code plug-in for `PNG frames + JSON manifest with 15-dim binary GT (+ optional depth)`:**
write one ~40-line class; do not touch `_SegDatasetBase` (it is built around a dense mask and an
occlusion hook you do not need).

```python
class PolarSceneDataset:                       # plain object, duck-typed like the others
    def __init__(self, manifest, split, img_size=512, augment=False, depth=False):
        recs = json.load(open(manifest))       # list of {"rgb":..., "depth":..., "y":[15 x 0/1], "scene":..., "cond":...}
        self.items = [r for r in recs if r["split"] == split]
        self.tf = C.build_transform(img_size, augment)          # reuse the campaign pipeline as-is
        self.depth = depth
    def __len__(self): return len(self.items)
    def __getitem__(self, i):
        r = self.items[i]
        img = np.array(Image.open(r["depth" if self.depth else "rgb"]).convert("RGB" if not self.depth else "I;16"))
        x = self.tf(image=img, mask=np.zeros(img.shape[:2], np.uint8))["image"]   # mask arg unused; keeps one code path
        return x, torch.tensor(r["y"], dtype=torch.float32)     # [15] float for BCEWithLogitsLoss
```

Two practical notes. (1) `build_transform` always expects a `mask=` kwarg — passing a zero mask is
cheaper than forking the function. (2) The render pipeline already emits a per-scene
`variation.json` whose `cuts[]` records carry `file`, `cond`, `seed`, `idx`, and a full `cam` block
(`eye`, `ground_z`, `d`, `h_rel`, …) — e.g.
`Practice_NegObs/dataset/260815_datapilot/train/scene04/variation.json`, with a run-level
`dataset/<round>/manifest.json` listing `scenes → {split, out, cuts, done_conds}`. Build tonight's
manifest by walking those two files rather than the filesystem: split, condition and camera pose come
for free and are exactly what you will want for per-condition breakdowns later.

**DataLoader settings the harness uses** (`run_experiment.make_loaders`, `run_experiment.py:100–107`):
`num_workers=4`, `pin_memory=True`, `shuffle=True` for train, and **`drop_last=True`** — the comment
records a real crash: a trailing batch of 1 kills DeepLabV3+'s ASPP global-pool BatchNorm. Keep
`drop_last=True`; with an `AdaptiveAvgPool2d`-based head a batch of 1 is fine, but consistency costs
nothing.

---

## 5. Training loop, checkpoints, timings

**Interface**: `run_experiment.py <config.json>` — a **JSON config file, no CLI flags**
(`run_experiment.main`, `run_experiment.py:430`). Keys read (with `cfg_get` defaults):
`kind` (`train`|`infer_probe`) · `model` · `dataset` · `epochs` · `batch` · `lr` · `seed` ·
`img_size` · `train_fraction` · `freeze_encoder` · `from_scratch` · `loss` · `aug` · `tag` ·
`purpose` · `est_minutes` · `run_dir` · plus `occlude_*` / `oversample_*`. A real example:
`campaign/queue/900_seed507_unet-r34.json`.

Loop (`run_train`, `run_experiment.py:220–427`):
`AdamW(lr, weight_decay=0.0)` → `LambdaLR` **linear decay to 0, no warmup** → per-epoch
train + full val → confusion-matrix mIoU → save on improvement.

- **Early stopping / patience: NOT IMPLEMENTED.** The loop always runs all `epochs` and simply keeps
  the best checkpoint. If you want patience tonight you must add it (≈6 lines around
  `run_experiment.py:383`). The campaign's substitute was reporting `best_epoch`, which is why
  entries like "0.4249 @ ep 77 of 100" appear everywhere.
- **OOM handling** is real and worth keeping: catches `torch.cuda.OutOfMemoryError`, halves the
  batch, rebuilds the loaders, rescales the LR schedule, retries once per epoch, hard-fails after
  4 total events (`run_experiment.py:346–369`).
- **Resume**: `latest.pt` carries model+optim+sched+RNG+`epoch_secs`; `map_location="cpu"` is
  mandatory (a GPU-side RNG ByteTensor broke `set_rng_state`, incident noted at line 261).

**Run-directory layout** (there is **no `metrics.json`** — the brief's assumption is wrong):

| file | content |
|---|---|
| `config.json` | copy of the submitted config |
| `metrics.csv` | one row per epoch per split — `epoch,split,loss,miou,mean_acc,overall_acc,lr,sec` |
| `done.json` | the summary record: `status, best_miou, best_epoch, wall_sec, params_m, peak_vram_mb, sec_per_epoch, epochs, batch, lr, seed, img_size, loss, aug, oom_events` |
| `per_class_iou.json` | per-class IoU **at the best epoch** (rewritten each time best improves) |
| `best.pt` / `final.pt` | weights-only `state_dict` |
| `latest.pt` | full resume state; deleted on clean finish |
| `curve.png`, `console.log`, `probe/` | plots, stdout, probe overlays |

For a 15-logit head, `ConfusionMatrix` does not apply. Minimum useful replacement: per-bin
`BCE`, per-bin AP/recall at a fixed threshold, and exact-match rate — write them into the same
`metrics.csv` schema so `plot_curve` and the reporting code keep working.

**Measured epoch times, RTX 4090, fp32, 512², batch 8** (`done.json → sec_per_epoch`; each figure is
train + full val for that split):

| model | dataset (train/val) | s/epoch | peak VRAM | params |
|---|---|---|---|---|
| **unet-r34** | sidewalk 800/200 | **9.3** (`p1`) · 8.8 (`unet-lr3e4`) · 8.9 (`unet-sat`) | 4.29 GB | 24.44 M |
| **unet-r34** | pothole 1002/250 | **9.5** | 3.74 GB | 24.44 M |
| unet-r34 | construction 415/91 | 4.3 | 4.20 GB | 24.44 M |
| unet-r34 | terrain 176/44 | 2.1 | 3.86 GB | 24.44 M |
| unet-r34 @ **768²** | sidewalk 800/200 | 19.7 | 9.29 GB | 24.44 M |
| segformer-b0 | sidewalk 800/200 | 7.4 | 3.30 GB | 3.72 M |
| dlv3p-r50 | sidewalk 800/200 | 11.0 | 6.30 GB | 26.69 M |
| **segformer-b2** | sidewalk 800/200 | **18.3** | 9.71 GB | 27.37 M |
| mask2former-tiny (batch **2**) | sidewalk 800/200 | 51.9 | 4.32 GB | 47.41 M |

**Estimator for tonight** (U-Net-scale, 512², batch 8, ~99 img/s train, ~220 img/s eval — derived
from the 800/200 rows using `plan_full.py`'s 90/10 train/eval split assumption, `plan_full.py:25–27`):

```
t_epoch ≈ N_train/99 + N_val/220  seconds        (+~1 s fixed dataloader spin-up)
```

e.g. **1,000 train / 250 val ≈ 11 s/epoch → 40 epochs ≈ 7.5 min**;
2,000/500 ≈ 21 s/epoch → 40 ep ≈ 14 min. SegFormer-B2 ≈ **2×** those numbers.
Dropping the U-Net decoder (path B in §2) roughly halves them again. VRAM headroom is ample —
budget ~4.3 GB for the RGB U-Net twin, ~9.7 GB for a B2, on a 24 GB card.

---

## 6. SegFormer-B2 (dry run)

**Loader: HF `transformers`, not smp.** `common.py:1037`
`_SEGFORMER_CKPT = {"segformer-b0": "nvidia/mit-b0", "segformer-b2": "nvidia/mit-b2"}` — i.e. the
**encoder-only ImageNet checkpoint**, with a fresh decode head sized by `num_labels`
(`build_model`, `common.py:1099–1108`, `ignore_mismatched_sizes=True`).

**Local weights** — already converted, no network needed:

```
campaign/data/hf_local/nvidia__mit-b2/{model.safetensors 98.9 MB, config.json, preprocessor_config.json}
campaign/data/hf_local/nvidia__mit-b0/...                                    (14.3 MB)
campaign/data/hf_local/facebook__mask2former-swin-tiny-ade-semantic/...      (190 MB)
campaign/data/hf_local/nvidia__segformer-b0-finetuned-cityscapes-768-768/... (14.9 MB)
```

Why they exist (`common.ensure_safetensors`, `common.py:1042–1082`): **transformers 5.x refuses to
load `pytorch_model.bin` on torch < 2.6** (CVE-2025-32434), and these NVIDIA/Facebook repos ship only
`.bin`. Rather than break the validated torch 2.5.1+cu124 stack, the harness converts once to
safetensors and loads from the local path. `ensure_safetensors(hub_id)` returns the upstream id if
upstream already has safetensors, else the local dir — call it and forget about it.
**Do not upgrade torch to "fix" this.**

**Input size used**: 512×512 everywhere by default; `b2-res768` and `terrain-b2-768` are the 768²
variants. The SegFormer wrapper upsamples the stride-4 logits back to input resolution with
`F.interpolate(..., mode="bilinear")` (`common.py:1069–1071`).

**What a B2-with-15-logit-head dry run needs** — pick one:

- **(i) Zero new model code, recommended for a dry run.** `C.build_model("segformer-b2", 15)` then
  global-average-pool the dense output: `logits = seg_logits.mean(dim=(2,3))` → `[B,15]`.
  Keeps `ensure_safetensors`, keeps the pretrained encoder, and you get a dense 15-channel map for
  free (useful for a spatial sanity check without any attribution machinery). Costs the decode head's
  FLOPs, which at B2 scale is minor.
- **(ii) Cleaner, one import.** ✅ verified available in transformers 5.15.0:
  `SegformerForImageClassification.from_pretrained(<hf_local>/nvidia__mit-b2, num_labels=15,
  problem_type="multi_label_classification", ignore_mismatched_sizes=True)` — MiT encoder + mean-pool
  + `Linear(768,15)`, `forward(pixel_values, labels)` returns logits `[B,15]` and, with that
  `problem_type`, computes BCE-with-logits internally.

Either way: same 512² input, ImageNet normalisation (matches `nvidia/mit-*` pretraining), batch 8,
expect ~2× the U-Net epoch time and ~9.7 GB VRAM.

---

## 7. Bootstrap CI code — **absent**

Searched `/home/vislab/Desktop/work_sy/ExProject_SR_HPE` (the 8/14 Joint SR-HPE paper repo:
15 `.py` files — `train.py`, `model.py`, `dataset.py`, `preprocess.py`, `inference_heatmap.py`,
`check_lr_mapping_all.py`, `smoke_test_17kpt/*`, `backup_13kpt_original/*` — and 0 notebooks) with
case-insensitive `bootstrap|resample|percentile|confidence.?interval|\bci_|paired` over
`*.py *.ipynb *.md`. **Zero hits.** Widening to all of `/home/vislab/Desktop/work_sy` returns hits
only inside `Baseline_NegObs/neg_env/lib/python3.10/site-packages` (torch, pandas, seaborn, networkx
internals). The campaign harness likewise contains no resampling code — its only uncertainty estimate
is the empirical **seed spread ±0.004** from ~450 `anchor-*` filler runs.

**Conclusion: no paired bootstrap exists to copy. It must be written.** Two options, both cheap:

- `scipy.stats.bootstrap` is available (scipy **1.15.3** ✅ in `env_seg`) and supports
  `paired=True`, `method="percentile"|"BCa"`, `n_resamples=...`, `vectorized=...`. For a paired
  comparison of two models over the *same* N samples, pass the per-sample statistic arrays as a
  tuple of two sequences with `paired=True`.
- Or ~20 lines by hand, which is what a paired bootstrap over samples actually is: draw
  `idx = rng.integers(0, N, N)` **once per resample and apply it to both models' per-sample scores**,
  recompute the metric difference, repeat 10k times, report the 2.5/97.5 percentiles of the
  difference. The load-bearing detail is that the resample index is shared — resampling each model
  independently is an unpaired test and will be wider than it should be.

Whichever route, the per-sample scores must be stored (one row per image/cut, not just an aggregate) —
the campaign's `metrics.csv` only stores per-epoch aggregates, so add a per-sample dump tonight if
CIs are wanted in the paper.

---

## 8. Grad-CAM / attribution code — **absent**

Searched both repos for `grad.?cam|gradcam|saliency|attribution|captum|backward hook`.
The single match is the word "Attribution" inside the CC-BY licence text of
`campaign/data/construction/README.md:197`. **No attribution code exists**, and `captum` is not
installed in `env_seg`.

What the campaign used *instead* of attribution, and which is worth reusing because it is stronger
evidence for this problem, is causal ablation rather than gradient attribution:

- `harness/occlusion_reliance.py` — erase the target's evidence (GT dilated 15 px, filled with the
  mean colour computed from outside the cover) and measure what survives, **with a shifted-patch
  control group** to separate "the patch appeared" from "the evidence disappeared". This is what
  produced the 3–29 % retention result and the 0.016→0.859 reversal.
- `harness/negobs_scene_probe.py` — run any run's `best.pt` over the scene renders and report class
  area shares + overlay grid (`--device cpu --limit N` for a smoke test; 13 scenes × 4 models ≈ 25 s CPU).
- `harness/size_band_eval.py` — connected-component size bands with `recall` and **`det@50`**
  (fraction of components at least half-covered), the metric the campaign recommends over mIoU for
  far/small hazards (`size_band_eval.py:27–28`, REPORT §9-3).
- `harness/cross_domain_eval.py` — `resolve_run()` (line 99) and `load_model()` (line 154) are the
  canonical "load a finished run's `best.pt` by tag" helpers; note `resolve_run` prefers an **exact
  `_<tag>` suffix** match, a fix for the 08-17 incident where `ade-full-b2` silently resolved to
  `ctx-ade-full-b2` and published a wrong baseline row.

If Grad-CAM is genuinely wanted for the polar head, a forward+backward hook on the resnet34 stage-5
output (`net.encoder`) is ~30 lines with no new dependency — but for a 15-bin vector head, per-bin
occlusion sensitivity (mask a screen region, watch bin *k*'s logit) is both simpler and more directly
interpretable, and reuses `occlusion_reliance.occl_dilate` / `occl_fill_mean`
(`common.py:408–440`) verbatim.
