#!/usr/bin/env bash
# Phase 2 조건① — PT 수정 설정 어두운 씬 노이즈 스팟 체크 (승용 승인 조건)
#   대상: scene02 지하도 · scene13 아파트 지하주차 진입부 · sceneD4 승강장(완전 실내)
#   sceneD4 는 dome 8.0 / sun 0.0 = 발광 패널 간접광만 → PT 수렴 최난이도.
#   기존 워밍업 900 씬이므로 legacy 기준선도 900 으로 잡는다.
# 각 씬을 legacy / fast / fast+total256 세 조건으로 렌더해 수렴 추이를 본다.
set -u
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 1

unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1

V="preset_h0.3_d2,preset_h0.9_d5,preset_h1.8_d10"

# $1 씬경로  $2 씬키  $3 라벨  $4 PT_FAST  $5 WARMUP(빈값=기본)  $6 total_spp override
run() {
  local scene="$1" key="$2" label="$3" fast="$4" warm="$5" tot="$6"
  echo "=== ${key} / ${label} (FAST=${fast} WARMUP=${warm:-default} TOT=${tot:-default}) ==="
  date +%s
  env NEGOBS_PT_FAST="${fast}" \
      ${warm:+NEGOBS_WARMUP=${warm}} \
      ${tot:+NEGOBS_PT_TOTAL_SPP=${tot}} \
      NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_VIEWS="${V}" \
      NEGOBS_CAPTURE_DIR="look_check/${key}/p2dark_${label}" \
    python "${scene}"
  date +%s
}

run scenes/main/scene02_underpass.py            scene02 legacy 0 ""    ""
run scenes/main/scene02_underpass.py            scene02 fast64 1 ""    ""
run scenes/main/scene02_underpass.py            scene02 fast256 1 16   256

run scenes/main/scene13_apartment_parking_entry.py scene13 legacy 0 ""  ""
run scenes/main/scene13_apartment_parking_entry.py scene13 fast64 1 ""  ""
run scenes/main/scene13_apartment_parking_entry.py scene13 fast256 1 16 256

run scenes/batch1/sceneD4_subway_platform.py    sceneD4 legacy 0 900  ""
run scenes/batch1/sceneD4_subway_platform.py    sceneD4 fast64 1 ""    ""
run scenes/batch1/sceneD4_subway_platform.py    sceneD4 fast256 1 16   256

echo "=== 완료 ==="
