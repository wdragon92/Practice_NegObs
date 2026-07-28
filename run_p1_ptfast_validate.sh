#!/usr/bin/env bash
# Phase 1-6 — PT 수정 설정을 **실제 프로덕션 씬**에서 검증.
#   ① 화질: 기존 PT(totalSpp 512 / warmup 572) 와 픽셀 비교
#   ② 속도: s/컷
#   ③ Phase 0 부채 해소: 기준선 수치가 새 설정에서 재현되는가
# 대상 = 기준선 3씬 중 capture_pipeline 사용 2씬(scene07·sceneD3).
# scene01 은 자체 캡처 블록이라 PARAMS 오버라이드 경로로 별도 처리한다.
set -u
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 1

unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1

V="preset_h0.3_d2,preset_h0.9_d5,preset_h1.8_d10"

run() {   # $1=씬경로  $2=출력태그  $3=ptfast(0|1)
  local scene="$1" tag="$2" fast="$3"
  echo "=== ${tag} (PT_FAST=${fast}) ==="; date +%s
  NEGOBS_PT_FAST="${fast}" \
  NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_VIEWS="${V}" \
  NEGOBS_CAPTURE_DIR="look_check/$(basename "${tag%%_*}")/${tag}" \
    python "${scene}"
  date +%s
}

run scenes/main/scene07_temple_stone_path.py       scene07_ptlegacy 0
run scenes/main/scene07_temple_stone_path.py       scene07_ptfast   1
run scenes/batch1/sceneD3_drainage_channel.py      sceneD3_ptlegacy 0
run scenes/batch1/sceneD3_drainage_channel.py      sceneD3_ptfast   1

echo "=== 완료 ==="
