#!/bin/bash
# ============================================================================
# 부분 재렌더 r4 — 07-27 PT 판정 후 잔여 수정분만 (scene06은 사용자 결정 대기로 제외)
#   수정: scene08 bank_front 남뱅크 플립 / scene10 계곡 흙틴트 / scene15 beauty 재선정
#         scene17 far_bank y±40 확폭 / scene19 접근성 v2(코드 기반영, 재캡처만)
#   ① scene19 RT 확인 렌더(entry_gate 포함, look_check/scene19/r4)
#   ② 5씬 PT 512spp → look_check/sceneNN/final_pt_r2 (기존 final_pt 보존, 전후 비교용)
#   실행: bash run_partial_r4.sh   (약 15~25분)
# ============================================================================
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1
LOG=look_check/logs/partial_r4.log
: > $LOG

echo "== [1/2] scene19 접근성 v2 RT 확인 렌더 ==" | tee -a $LOG
NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=rt NEGOBS_CAPTURE_DIR=look_check/scene19/r4 \
  python scene19_fan_winder.py >> $LOG 2>&1
echo "scene19_fan_winder RT_EXIT=$? FILES=$(ls look_check/scene19/r4 2>/dev/null | wc -l)" | tee -a $LOG

echo "== [2/2] 수정 5씬 PT 재캡처 ==" | tee -a $LOG
for s in scene08_stepwell_lattice scene10_switchback_cliff scene15_alley_labyrinth \
         scene17_ramp_pair_hangang scene19_fan_winder; do
  n=${s%%_*}
  NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_CAPTURE_DIR=look_check/${n}/final_pt_r2 \
    python $s.py >> $LOG 2>&1
  echo "$s PT_EXIT=$? FILES=$(ls look_check/${n}/final_pt_r2 2>/dev/null | wc -l)" | tee -a $LOG
done
echo "r4 완료. 판정 대상: 08 bank_front 밝기 / 10 계곡 틴트·난간 / 15 beauty 프레이밍 / 17 far_bank 부유 해소 / 19 진입 동선(entry_gate)." | tee -a $LOG
