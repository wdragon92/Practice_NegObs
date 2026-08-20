# README_CODE — polar hazard grid (N cells = band*n_sectors + sector, from a **gridspec**)
`gridspec.py` **the only place the cell count lives**: `--grid` loads `labeling/gridspec_v0.json` (5 sectors x 3 bands = 15, the default so 0819 runs reproduce) or `gridspec_v1.json` (5 x 4 = 20, bands [0,2)/[2,5)/[5,8)/[8,12)); a bare filename is resolved against `code/labeling`, `code/`, `mainrun_0819/`, `dayrun_0820/`. Derives `n_cells`, `cell_ids` (A1..E4), `band_of`, `flip_perm`, band labels; fails loudly on a spec/manifest mismatch. Nothing else may hard-code 15 or 20.
`polar_dataset.py` manifest→tensor (512² squash, imagenet norm / depth clip 10 m, photometric aug, **hflip+sector permutation p=0.5**, `positive_rate()` for the bias prior) · `model_factory.py` smp.Unet-r34 + aux head → `[B,n_cells]` (+`final_classifier()`) · `bootstrap.py` percentile + paired CIs (no scipy)
`train_polar.py` **recipe v2**: AdamW+BCEWithLogits fp32; checkpoint/early-stop on `sel_score = 0.5*val_cell_F1 + 0.5*val_H_frame_recall` (loud fallback to F1 if val has no H frame); `--bias-init prior` sets the final bias to the per-cell train log-odds; `--hflip on`; `--oversample-h 4` (strict-H WeightedRandomSampler, folded in from `train_oversample.py`, now a shim) · `eval_polar.py` per_frame.csv + tier recall + **frame_det_rate** (V0↔V1 continuity) + per-band recall **and FA** + tau* + CIs + `--compare` · `make_split.py` scene-unit split + PROOF report + **`--move-h-scene-to-val`** (split v2) · `make_viz.py` panels with an n_bands-row heatmap · `twin_analysis.py` on−off delta by tier, **by band, and band×H** · `split_per_frame.py` on/off halves of a per_frame.csv · `aggregate_seeds.py` mean±range across seeds · `run_queue_v2.sh` the 9-run queue · `smoke_test.py` CPU end-to-end at **both** 15 and 20 cells
```bash
PY="env PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 /home/vislab/miniconda3/envs/env_seg/bin/python"   # PYTHONNOUSERSITE=1 mandatory
W=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/mainrun_0819; CODE=$W/code; M=$W/dataset_manifest_v1.json; S=$W/split_v1.json
FLOCK="flock -o -w 55 -E 201 /tmp/negobs_gpu.lock nice -n 5"   # -o mandatory; exit 201 = lock busy, 202 = <6 GB free
PYTHONNOUSERSITE=1 /home/vislab/miniconda3/envs/env_seg/bin/python $CODE/smoke_test.py            # CPU only, ~3 min, runs 15-cell AND 20-cell
# split v2 (val gains H so the selector can see the headline metric; test untouched)
$PY $CODE/make_split.py --manifest $M --out $W/../dayrun_0820/split_v2.json --report $W/../dayrun_0820/SPLIT_PROPOSAL_v2.md \
    --seed 42 --hard-negatives sceneN3 --force-test scene14 --exclude-scenes @$W/annotations/hold_scenes.json --move-h-scene-to-val
# the whole v2 queue (rgb,depth,b2 x seeds 42,43,44; one GPU-lock hold per run; abort-safe)
bash $CODE/run_queue_v2.sh $M $W/../dayrun_0820/split_v2.json $W/runs/v2 gridspec_v1.json
# or one run at a time
$FLOCK $PY $CODE/train_polar.py --manifest $M --split $S --input rgb --out $W/run_rgb --seed 42 --max-epochs 150 --patience 15 \
       --batch 8 --lr 3e-4 --grid gridspec_v1.json --hflip on --oversample-h 4 --bias-init prior
$FLOCK $PY $CODE/eval_polar.py --manifest $M --split $S --subset test --input rgb --ckpt $W/run_rgb/best.pt --out $W/eval_rgb \
       --tau-op 0.5 --tau-star auto --tau-sweep 0.3,0.5,0.7 --grid gridspec_v1.json
$PY $CODE/split_per_frame.py --per-frame $W/eval_rgb/per_frame.csv --out-dir $W/eval_rgb
$PY $CODE/twin_analysis.py --per-frame-on $W/eval_rgb/per_frame_on.csv --per-frame-off $W/eval_rgb/per_frame_off.csv \
       --manifest $M --out $W/twin_rgb --grid gridspec_v1.json
$PY $CODE/make_viz.py --per-frame $W/eval_rgb/per_frame.csv --manifest $M --out $W/viz_rgb --n 4 --grid gridspec_v1.json
$PY $CODE/aggregate_seeds.py --root $W/runs/v2 --models rgb,depth,b2 --seeds 42,43,44 --out $W/runs/v2/SEED_TABLE.md --grid gridspec_v1.json
```
## `infer_photo.py` — real-world pilot inference (Phase 7, **PROVISIONAL**)
Phone photo → EXIF-upright → letterbox 512² (gray pad) + ImageNet norm → the same `model_factory` U-Net sized by `--grid` (the checkpoint's own cell count is cross-checked; a mismatch aborts) → sigmoid → `overlay.png` = the photo carrying a translucent ground-wedge fan (labeler camera convention, assumed height/pitch/hfov) beside the `make_viz` probability grid, with the assumption line watermarked onto the image. `--hfov auto` reads EXIF `FocalLengthIn35mmFilm` (36 mm side in landscape, 24 mm in portrait) and degrades to 69°, stamping `default,no EXIF` in the watermark. Uses `$PY`/`$CODE`/`$W` from the block above; CPU is fine.
```bash
$PY $CODE/infer_photo.py --image photo.jpg --ckpt $W/runs/rgb_s42/best.pt --grid gridspec_v1.json --out $W/realworld/overlay.png          # defaults h=1.65 m · hfov auto→69° · pitch 0
$PY $CODE/infer_photo.py --image photo.jpg --ckpt $W/runs/rgb_s42/best.pt --grid gridspec_v1.json --out o.png --height 1.70 --hfov 63 --pitch -15 --json o.json   # known pose instead of the defaults
$PY $CODE/infer_photo.py --image sim.png   --ckpt $W/runs/rgb_s42/best.pt --grid gridspec_v0.json --out o.png --fit squash               # --fit squash = training geometry (letterbox is the default)
```
Caveat worth knowing before quoting a number: training **squashes** to 512² (`polar_dataset.py`) while this tool **letterboxes** by default, and the two disagree — on the self-test frame `on/scene14/L0__s20260819__0003.png` with `runs/rgb_s42/best.pt` at `--grid gridspec_v0.json`, max p is 0.759 (letterbox) vs 0.821 (squash); the squash path reproduces `eval_test/per_frame.csv` to 1.6e-4 (CPU-vs-GPU float). At `--pitch 0` the near bands project *below* the frame (10/15 V0 wedges visible), which is a property of the assumed pose, not of the model — pass a realistic `--pitch` for a hand-held shot.

Notes. One test per_frame.csv carries BOTH arms; `split_per_frame.py` writes the halves (twin_analysis also accepts the same file twice — rows are picked by the frame_id prefix). Twin's default pose filter includes `cam.ground_z`, dropping the 183 rejection-resample pairs; `--pose-keys d,h_rel,yaw,pitch` reverts to the brief's four keys. Every output stamps its grid version, and a 15-cell CSV/checkpoint under a 20-cell `--grid` (or the reverse) aborts instead of producing a plausible wrong table.
