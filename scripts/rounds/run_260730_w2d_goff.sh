#!/bin/bash
# =============================================================================
# W2-D GRAZE 판정용 ON/OFF 트윈 — `NEGOBS_GKIT=0` 팔 (round = 260730_w2d_goff)
#   ground_kit_spec §7.5 A3 결재: "GRAZE 침묵은 에지 무결성의 증거가 아니다.
#   증거는 **같은 세션·같은 HEAD 의 지면키트 ON/OFF A/B** 의 OCCL 판독 + 육안."
#   r2_on 기준선은 W2 커밋 20여 건을 사이에 두고 있어 GRAZE 발화를 키트에 귀속할 수
#   없다 — 이 팔이 그 귀속을 만든다(W2-C 가 D2 를 닫은 것과 같은 방법).
#   출력은 씬 루트가 아니라 `_experiments/twins/` (look_check/README §1).
# =============================================================================
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1

ROUND=260730_w2d_goff
LOG=look_check/logs/${ROUND}.log
: > $LOG

run () {   # $1 stem  $2 subdir  $3 views
  s=$1; n=${s%%_*}
  out=look_check/_experiments/twins/${n}/${ROUND}
  mkdir -p $out
  export NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_CAPTURE_DIR=$out
  export NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1=1
  export NEGOBS_DETAIL_SCALE=2 NEGOBS_DETAIL_ROUGH_GAIN=0
  export NEGOBS_GKIT=0 NEGOBS_VIEWS="$3"
  t0=$(date +%s.%N)
  python scenes/$2/$s.py >> $LOG 2>&1
  rc=$?
  t1=$(date +%s.%N)
  echo "$n exit=$rc cuts=$(ls $out/*.png 2>/dev/null|wc -l) $(echo "$t1-$t0"|bc)s" | tee -a $LOG
  python3 scripts/stamp_round.py $out $ROUND "$n" >> $LOG 2>&1
  unset NEGOBS_GKIT NEGOBS_VIEWS
}

P3="preset_h0.3_d2,preset_h0.3_d5,preset_h0.3_d10"
run scene14_grandstair_illusion  main   "$P3"
run scene16_canopy_shadow        main   "$P3"
run scene20_diagonal_oblique     main   "$P3,low_grazing"
run scene21_monumental_selfocclude main "$P3,crown_graze"
run sceneC4_wet_stairs           batch1 "$P3,grazing_mirror"
run sceneN3_trompe_loeil         batch1 "$P3"
echo "[$ROUND] done" | tee -a $LOG
