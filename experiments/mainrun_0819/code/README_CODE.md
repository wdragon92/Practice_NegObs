# README_CODE — polar hazard grid (15 cells = band*5 + sector; A-E x 1-3, band 1=near)
`polar_dataset.py` manifest→tensor (512² squash, imagenet norm / depth clip 10 m, photometric-only aug, `flip_with_permutation` implemented but OFF) · `model_factory.py` smp.Unet-r34 + aux head → `[B,15]` logits · `bootstrap.py` percentile + paired CIs (no scipy)
`train_polar.py` AdamW+BCEWithLogits fp32, early-stop on val cell-F1@0.5 · `eval_polar.py` per_frame.csv + tier recall + FA + bands + tau* + CIs + `--compare` · `make_split.py` scene-unit split + PROOF report · `make_viz.py` 12 qualitative panels · `twin_analysis.py` on−off delta on pose-matched twin pairs (CPU, no GPU lock) · `smoke_test.py` CPU end-to-end · RESERVE (not run tonight): `train_oversample.py` (`--oversample-strict-h 4`), `aug_photometric.yaml` (all blocks `enabled: false`)
```bash
PY="env PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 /home/vislab/miniconda3/envs/env_seg/bin/python"   # PYTHONNOUSERSITE=1 mandatory
W=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/mainrun_0819; CODE=$W/code; M=$W/dataset_manifest_v1.json; S=$W/split_v1.json
FLOCK="flock -o -w 55 -E 201 /tmp/negobs_gpu.lock nice -n 5"   # -o mandatory; exit 201 = lock busy, 202 = <6 GB free
PYTHONNOUSERSITE=1 /home/vislab/miniconda3/envs/env_seg/bin/python $CODE/smoke_test.py            # CPU only, ~40 s
$PY $CODE/make_split.py --manifest $M --out $S --report $W/SPLIT_PROPOSAL.md --seed 42 --hard-negatives sceneN3
$FLOCK $PY $CODE/train_polar.py --manifest $M --split $S --input rgb   --out $W/run_rgb   --seed 42 --max-epochs 150 --patience 15 --batch 8 --lr 3e-4
$FLOCK $PY $CODE/train_polar.py --manifest $M --split $S --input depth --out $W/run_depth --seed 42 --max-epochs 150 --patience 15 --batch 8 --lr 3e-4
$FLOCK $PY $CODE/eval_polar.py --manifest $M --split $S --subset test --input rgb   --ckpt $W/run_rgb/best.pt   --out $W/eval_rgb   --tau-op 0.5 --tau-star auto --tau-sweep 0.3,0.5,0.7
$FLOCK $PY $CODE/eval_polar.py --manifest $M --split $S --subset test --input depth --ckpt $W/run_depth/best.pt --out $W/eval_depth --tau-op 0.5 --tau-star auto --tau-sweep 0.3,0.5,0.7
$FLOCK $PY $CODE/eval_polar.py --manifest $M --split $S --subset test --input rgb   --ckpt $W/run_rgb/best.pt   --out $W/eval_cmp --compare $W/eval_depth/per_frame.csv   # paired RGB−depth CIs
$PY $CODE/make_viz.py --per-frame $W/eval_rgb/per_frame.csv --manifest $M --out $W/viz_rgb --n 4
$PY $CODE/twin_analysis.py --per-frame-on $W/eval_rgb/per_frame.csv --per-frame-off $W/eval_rgb/per_frame.csv --manifest $M --out $W/twin_rgb   # one test CSV carries BOTH arms; rows are picked by the frame_id prefix (pass two files only if the arms were evaluated separately). Default pose filter includes cam.ground_z -> drops the 183 rejection-resample pairs; --pose-keys d,h_rel,yaw,pitch reverts to the brief's four keys.
```
