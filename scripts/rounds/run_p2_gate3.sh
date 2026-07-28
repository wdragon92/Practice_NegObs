#!/usr/bin/env bash
# Phase 2 게이트 — 대표 3씬(01 캠퍼스 / 07 석재 / D3 측구) 룩 레이어 A/B.
#   OFF = 현행, ON = NEGOBS_LOOK_V1=1
# 두 조건 모두 **PT 수정 설정**으로 렌더해 렌더러 변인을 통제한다.
# scene01 은 capture_pipeline 을 안 쓰므로(자체 캡처 블록) PARAMS 오버라이드로
# 같은 PT 설정을 만든다: totalSpp 64 + rtSubframes 8(boot에서) + warmup 8.
set -u
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 1

unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1

TAG="${1:-g1}"
S01_OV='{"render":{"pt_total_spp":64,"pt_max_bounces":8}}'

run() {   # $1 씬경로  $2 씬키  $3 look(0|1)  [$4 추가 env]
  local scene="$1" key="$2" look="$3"
  local label; label=$([ "$look" = "1" ] && echo "on" || echo "off")
  echo "=== ${key} look=${label} ==="; date +%s
  env NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1="${look}" \
      NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt \
      NEGOBS_CAPTURE_DIR="look_check/${key}/p2${TAG}_${label}" \
      ${4:-FOO=bar} \
    python "${scene}"
  date +%s
}

run scenes/main/scene01_campus_stairs.py      scene01 0 "NEGOBS_PARAMS_OVERRIDE=${S01_OV} NEGOBS_WARMUP=8"
run scenes/main/scene01_campus_stairs.py      scene01 1 "NEGOBS_PARAMS_OVERRIDE=${S01_OV} NEGOBS_WARMUP=8"
run scenes/main/scene07_temple_stone_path.py  scene07 0
run scenes/main/scene07_temple_stone_path.py  scene07 1
run scenes/batch1/sceneD3_drainage_channel.py sceneD3 0
run scenes/batch1/sceneD3_drainage_channel.py sceneD3 1

echo "=== 완료 ==="
