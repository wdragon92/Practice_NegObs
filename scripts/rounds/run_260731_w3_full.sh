#!/bin/bash
# =============================================================================
# W3 최종 리뷰 라운드 — 갤러리 v2 원본 — 33씬 전 컷 PT (round = 260731_w3_full)
#   look_check/README.md §2 명명규약: <yymmdd>_<wave>_<purpose>
#   재질 팔: LOOK_V1=1 (=MTL 1 · GEO 1) · DETAIL_SCALE=2.0 · DETAIL_ROUGH_GAIN=0
#            (w2c_merge_t1_v1.md §7 GO 항목 1 — 스윕 최적값, rough_gain 은 노이즈)
#   GPU 전용·순차·단일 인스턴스. 인자로 씬 이름을 주면 그 씬만 돈다.
# =============================================================================
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1

ROUND=260731_w3_full
LOG=look_check/logs/${ROUND}.log
TIMES=look_check/logs/${ROUND}_times.tsv
mkdir -p look_check/logs

MAIN="scene01_campus_stairs scene02_underpass scene03_riverbank scene04_parktrail \
scene05_amphitheater scene06_overpass_spiral scene07_temple_stone_path \
scene08_sunken_plaza scene09_ghat_riverfront scene10_park_deck_switchback \
scene11_footbridge_stairs scene12_riverside_deck scene13_apartment_parking_entry \
scene14_grandstair_illusion scene15_alley_labyrinth scene16_canopy_shadow \
scene17_ramp_pair_hangang scene18_wavy_artstair scene19_fan_winder \
scene20_diagonal_oblique scene21_monumental_selfocclude"
BATCH1="sceneC1_snow_stairs sceneC2_leaf_stairs sceneC4_wet_stairs \
sceneD1_loading_dock sceneD2_floor_opening sceneD3_drainage_channel \
sceneD4_subway_platform sceneN1_shadow_band sceneN2_asphalt_patch \
sceneN3_trompe_loeil sceneN4_downhill_ramp sceneN5_flush_grating"

SEL="$*"
if [ -z "$SEL" ]; then
  : > $LOG
  printf "scene\tsec\tcuts\texit\n" > $TIMES
fi

run_one () {                       # $1 = file stem, $2 = subdir
  s=$1; sub=$2
  n=${s%%_*}
  [ -n "$SEL" ] && case " $SEL " in *" $n "*) ;; *) return;; esac
  out=look_check/${n}/${ROUND}
  mkdir -p $out
  # export 로 두는 이유: 렌더 뒤 stamp_round.py 가 같은 NEGOBS_* 팔을 읽어 기록한다
  export NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_CAPTURE_DIR=$out
  export NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1=1
  export NEGOBS_DETAIL_SCALE=2 NEGOBS_DETAIL_ROUGH_GAIN=0
  python3 scripts/stamp_round.py --capture-env $out >> $LOG 2>&1
  t0=$(date +%s.%N)
  python scenes/${sub}/$s.py >> $LOG 2>&1
  rc=$?
  t1=$(date +%s.%N)
  dt=$(echo "$t1 - $t0" | bc)
  cuts=$(ls $out/*.png 2>/dev/null | wc -l)
  printf "%s\t%.1f\t%d\t%d\n" "$n" "$dt" "$cuts" "$rc" | tee -a $TIMES
  python3 scripts/stamp_round.py $out $ROUND "$n" >> $LOG 2>&1
}

for s in $MAIN;   do run_one $s main;   done
for s in $BATCH1; do run_one $s batch1; done
echo "[$ROUND] done" | tee -a $LOG
