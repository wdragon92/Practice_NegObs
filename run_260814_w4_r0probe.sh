#!/usr/bin/env bash
# 260814_w4_r0probe — R0 측정 기반 확정 (GT-113 부속 프로브 라운드)
# (a) PT-fast 등가성 실측: legacy 512 vs fast(16/64/8) vs fast 반복 — md5 로
#     스파이크의 "3종 전부 동일" 사고 재현 여부 확정.
# (b) PT AA filterRadius / OptiX 디노이저 실효값 덤프 + 각 1팔 스윕.
# 대상: scene04(품질 기준씬 — slope 실측용) 2컷. 판정 라운드 아님(probe).
# GPU: flock -o 아래 직렬. 다른 세션과의 조율은 flock 대기열로.
set -euo pipefail
cd /home/vislab/Desktop/work_sy/Practice_NegObs
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1

SCENE=scenes/main/scene04_parktrail.py
BASE=look_check/scene04/260814_w4_r0probe
VIEWS="preset_h0.3_d5,step_detail"
DUMP="/rtx/pathtracing/aa/op;/rtx/pathtracing/aa/filterRadius;/rtx/pathtracing/optixDenoiser/enabled;/rtx/pathtracing/optixDenoiser/blendFactor;/rtx/pathtracing/spp;/rtx/pathtracing/totalSpp;/rtx/post/aa/op"

arm () {  # name, extra env...
  local name="$1"; shift
  echo "=== [R0] arm ${name} ==="
  env NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_LOOK_V1=1 \
      NEGOBS_VIEWS="$VIEWS" NEGOBS_CAPTURE_DIR="$BASE/$name" \
      NEGOBS_RTX_DUMP="$DUMP" "$@" \
      python scripts/probe_render_settings.py "$SCENE" 2>&1 \
      | grep -E "R0-DUMP|R0-SET|캡처|룩v1" || true
}

arm a512                                            # legacy PT 512 (PT_FAST 미설정)
arm bfast  NEGOBS_PT_FAST=1                         # fast 16/64/8
arm bfast2 NEGOBS_PT_FAST=1                         # fast 반복(별도 부팅) — 결정성
arm cfr05  NEGOBS_PT_FAST=1 NEGOBS_RTX_SET="/rtx/pathtracing/aa/filterRadius=0.5"
arm dnoden NEGOBS_PT_FAST=1 NEGOBS_RTX_SET="/rtx/pathtracing/optixDenoiser/enabled=false"

echo "=== [R0] md5 ==="
md5sum "$BASE"/*/pt_noon_*.png | sort
for a in a512 bfast bfast2 cfr05 dnoden; do
  python3 scripts/stamp_round.py "$BASE/$a" 260814_w4_r0probe scene04 || true
done
echo "=== [R0] done ==="
