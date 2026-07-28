#!/bin/bash
# ============================================================================
# 씬 라이브러리 v3 마무리 스크립트 (재부팅 후 1회 실행)
#   ① scene14/17 r3 확인 렌더(RT)  ② 신규 16씬(scene06~21) PT 512spp 파이널
#   실행: bash run_finalize_v3.sh   (약 60~75분, look_check/sceneNN/{r3,final_pt})
#   작성: 2026-07-25 감독 세션 (VS Code 크래시로 GPU 재부팅 대기 중 중단된 잔여분)
# ============================================================================
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1
LOG=look_check/finalize_v3.log
: > $LOG

echo "== [1/2] scene14/17 r3 확인 렌더 ==" | tee -a $LOG
for s in scene14_grandstair_illusion scene17_ramp_pair_hangang; do
  n=${s%%_*}
  NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=rt NEGOBS_CAPTURE_DIR=look_check/${n}/r3 python $s.py >> $LOG 2>&1
  echo "$s RT_EXIT=$? FILES=$(ls look_check/${n}/r3 2>/dev/null | wc -l)" | tee -a $LOG
done

echo "== [2/2] 신규 16씬 PT 파이널 ==" | tee -a $LOG
for s in scene06_spiral_towerstone scene07_wornstone_temple scene08_stepwell_lattice \
         scene09_ghat_riverfront scene10_switchback_cliff scene11_grating_fireescape \
         scene12_cliff_plankwalk scene13_helical_parkingramp scene14_grandstair_illusion \
         scene15_alley_labyrinth scene16_canopy_shadow scene17_ramp_pair_hangang \
         scene18_wavy_artstair scene19_fan_winder scene20_diagonal_oblique \
         scene21_monumental_selfocclude; do
  n=${s%%_*}
  NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_CAPTURE_DIR=look_check/${n}/final_pt python $s.py >> $LOG 2>&1
  echo "$s PT_EXIT=$? FILES=$(ls look_check/${n}/final_pt 2>/dev/null | wc -l)" | tee -a $LOG
done
echo "완료. 판정 대상: scene06 나선 내부·scene08 우물 내부·scene13 지하(PT 다중바운스 밝기), scene14/17 접지·수면." | tee -a $LOG
