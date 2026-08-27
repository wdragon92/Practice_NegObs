#!/usr/bin/env bash
# Phase 2 — 전 33씬 재렌더 (룩 레이어 v1 적용)
#
#   사용법:  bash scripts/rounds/run_p2_all33.sh <라운드태그> [on|off]
#     예:    bash scripts/rounds/run_p2_all33.sh r1 on      # 룩 레이어 ON
#            bash scripts/rounds/run_p2_all33.sh r1 off     # 대조군
#
# 규약:
#   · 렌더는 **PT 수정 설정 단일화**(브리프 개정이력 rev.1 — 원칙4 폐기).
#   · 어두운 씬은 씬별 total_spp 상향(승용 조건①):
#       sceneD4(완전 실내·발광 주도) = 256 필수
#       scene02(지하도) · scene13(지하주차) = 256 권장
#   · scene01 은 리팩터로 capture_pipeline 을 타므로 더 이상 예외가 아니다.
#     단 PARAMS 의 pt_total_spp 는 씬 상수(512)라 오버라이드로 낮춘다.
#   · GPU 1대 — **직렬 실행. 병렬 금지.**
set -u
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 1

unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1

TAG="${1:?라운드 태그를 주십시오 (예: r1)}"
LOOK="${2:-on}"
LOOKV=$([ "$LOOK" = "on" ] && echo 1 || echo 0)
S01_OV='{"render":{"pt_total_spp":64,"pt_max_bounces":8}}'

echo "########## 전 33씬 라운드 ${TAG} · 룩=${LOOK} ##########"
date

render() {   # $1 씬경로  $2 씬키  $3 total_spp(빈값=기본 64)
  local scene="$1" key="$2" tot="${3:-}"
  local t0 t1
  t0=$(date +%s)
  env NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1="${LOOKV}" \
      ${tot:+NEGOBS_PT_TOTAL_SPP=${tot}} \
      NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt \
      NEGOBS_CAPTURE_DIR="look_check/${key}/${TAG}_${LOOK}" \
      NEGOBS_PARAMS_OVERRIDE="${S01_OV}" \
    python "${scene}" > "/tmp/negobs_${TAG}_${key}.log" 2>&1
  t1=$(date +%s)
  local n
  n=$(ls "look_check/${key}/${TAG}_${LOOK}"/pt_*.png 2>/dev/null | wc -l)
  printf "%-10s %3d컷  %4ds  %s\n" "${key}" "${n}" "$((t1-t0))" \
    "$(grep -oE '^\[룩v1\] 재질.*' "/tmp/negobs_${TAG}_${key}.log" | head -1 | cut -c1-90)"
}

# ---- 본편 21씬 ----
render scenes/main/scene01_campus_stairs.py            scene01
render scenes/main/scene02_underpass.py                scene02 256
render scenes/main/scene03_riverbank.py                scene03
render scenes/main/scene04_parktrail.py                scene04
render scenes/main/scene05_amphitheater.py             scene05
render scenes/main/scene06_overpass_spiral.py          scene06
render scenes/main/scene07_temple_stone_path.py        scene07
render scenes/main/scene08_sunken_plaza.py             scene08
render scenes/main/scene09_ghat_riverfront.py          scene09
render scenes/main/scene10_park_deck_switchback.py     scene10
render scenes/main/scene11_footbridge_stairs.py        scene11
render scenes/main/scene12_riverside_deck.py           scene12
render scenes/main/scene13_apartment_parking_entry.py  scene13 256
render scenes/main/scene14_grandstair_illusion.py      scene14
render scenes/main/scene15_alley_labyrinth.py          scene15
render scenes/main/scene16_canopy_shadow.py            scene16
render scenes/main/scene17_ramp_pair_hangang.py        scene17
render scenes/main/scene18_wavy_artstair.py            scene18
render scenes/main/scene19_fan_winder.py               scene19
render scenes/main/scene20_diagonal_oblique.py         scene20
render scenes/main/scene21_monumental_selfocclude.py   scene21

# ---- 배치1 12씬 ----
render scenes/batch1/sceneN1_shadow_band.py            sceneN1
render scenes/batch1/sceneN2_asphalt_patch.py          sceneN2
render scenes/batch1/sceneN3_trompe_loeil.py           sceneN3
render scenes/batch1/sceneN4_downhill_ramp.py          sceneN4
render scenes/batch1/sceneN5_flush_grating.py          sceneN5
render scenes/batch1/sceneC1_snow_stairs.py            sceneC1
render scenes/batch1/sceneC2_leaf_stairs.py            sceneC2
render scenes/batch1/sceneC4_wet_stairs.py             sceneC4
render scenes/batch1/sceneD1_loading_dock.py           sceneD1
render scenes/batch1/sceneD2_floor_opening.py          sceneD2
render scenes/batch1/sceneD3_drainage_channel.py       sceneD3
render scenes/batch1/sceneD4_subway_platform.py        sceneD4 256

echo "########## 완료 ##########"
date
