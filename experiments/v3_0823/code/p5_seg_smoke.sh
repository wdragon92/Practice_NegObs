#!/bin/bash
# =============================================================================
# p5_seg_smoke.sh — v3 P-5 : ONE 1-frame render proving the id-mask sidecar.
#
# Purpose (D58 (9)): the ID-mask (seg) sidecar was promoted to load-bearing —
# DZ §12-5's cue-pixel threshold k and D58 (1)(b)'s edge-ownership gate both
# require it. This is the feasibility proof, nothing else. 1 cut, 1 scene,
# 1 condition. Not a round; its output is evidence, not corpus.
#
# Invocation pattern copied verbatim from scripts/rounds/run_260820_boost.sh
# (PRE preamble :158-163, flock render :302).
# =============================================================================
set -u
REPO=/home/vislab/Desktop/work_sy/Practice_NegObs
LOCK=/tmp/negobs_gpu.lock
RUN=260823_v3p5_segsmoke_A
SCENE=scene01
OUT="$REPO/experiments/v3_0823/logs/p5_seg_smoke.log"
mkdir -p "$(dirname "$OUT")"

PRE='cd '"$REPO"' || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1'

echo "[$(date '+%F %T')] p5 seg smoke start — run=$RUN scene=$SCENE" | tee -a "$OUT"

flock -o -w 2400 -E 201 "$LOCK" nice -n 5 bash -c "$PRE
export NEGOBS_DATA_SIDECARS=1
export NEGOBS_SEG_SIDECAR=1
export NEGOBS_SCENE_CONFIG='{\"hazard_stairs\": true}'
python3 scripts/run_data_render.py --run '$RUN' --scenes '$SCENE' \
        --conds L0 --cams 1 --seed 20260823" >> "$OUT" 2>&1
rc=$?
echo "[$(date '+%F %T')] p5 seg smoke rc=$rc" | tee -a "$OUT"

# ---- verdict: did an .idseg.npz land, and does it decode to prim paths? -----
bash -c "$PRE
python3 - <<'PY' 2>&1 | tee -a '$OUT'
import glob, json, os
import numpy as np
d = '$REPO/dataset/$RUN'
npz = sorted(glob.glob(os.path.join(d, '*', '*', '*.idseg.npz')))
png = sorted(glob.glob(os.path.join(d, '*', '*', '*.png')))
print('=== P5 SEG SMOKE VERDICT ===')
print('pngs      :', len(png), [os.path.basename(p) for p in png])
print('idseg npz :', len(npz), [os.path.basename(p) for p in npz])
if not npz:
    print('RESULT: FAIL — no id-mask sidecar written')
    raise SystemExit(1)
z = np.load(npz[0], allow_pickle=False)
a = z['idseg']
lab = json.loads(str(z['idToLabels']))
print('shape', a.shape, 'dtype', a.dtype, 'unique ids', len(np.unique(a)))
print('npz bytes', os.path.getsize(npz[0]))
print('idToLabels entries', len(lab))
items = list(lab.items())[:12]
for k, v in items:
    print('   ', k, '->', v)
cue = [v for v in lab.values() if isinstance(v, str)
       and ('Rail' in v or 'Nosing' in v or 'Tactile' in v or 'Sign' in v)]
print('cue-ish prim paths found:', len(cue), cue[:6])
print('RESULT: PASS' if len(np.unique(a)) > 1 else 'RESULT: DEGENERATE (1 id)')
PY"
