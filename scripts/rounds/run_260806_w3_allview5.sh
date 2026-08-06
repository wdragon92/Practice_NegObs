#!/bin/bash
# =============================================================================
# 33씬 통람 4뷰 라운드 (round = 260806_w3_allview5) — GT-72~88 착지 후 재통람
#   근거: 08-06 사용자 요청 — 씬당 대표 4뷰를 고품질로 재렌더 후 씬별 2×2 합성
#   재질 팔: 260805_w3_doctrine 과 동일 (LOOK_V1=1 · DETAIL_SCALE=2 · ROUGH_GAIN=0)
#   품질: NEGOBS_PT_TOTAL_SPP=256 (통상 갤러리 64 의 4배) — 뷰 4개뿐이라 시간 상쇄
#   렌더 전용 라운드 — 씬 코드·GT 무변경 (ledger 선신고 대상 아님)
#   사용법: bash run_260806_w3_allview5.sh [scene01 sceneD2 ...]  (무인자 = 33씬 전부)
# =============================================================================
cd /home/vislab/Desktop/work_sy/Practice_NegObs || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1

ROUND=260806_w3_allview5
LOG=look_check/logs/${ROUND}.log
mkdir -p look_check/logs
touch $LOG

declare -A SCENES=(
  [scene01]=main/scene01_campus_stairs
  [scene02]=main/scene02_underpass
  [scene03]=main/scene03_riverbank
  [scene04]=main/scene04_parktrail
  [scene05]=main/scene05_amphitheater
  [scene06]=main/scene06_overpass_spiral
  [scene07]=main/scene07_temple_stone_path
  [scene08]=main/scene08_sunken_plaza
  [scene09]=main/scene09_ghat_riverfront
  [scene10]=main/scene10_park_deck_switchback
  [scene11]=main/scene11_footbridge_stairs
  [scene12]=main/scene12_riverside_deck
  [scene13]=main/scene13_apartment_parking_entry
  [scene14]=main/scene14_grandstair_illusion
  [scene15]=main/scene15_alley_labyrinth
  [scene16]=main/scene16_canopy_shadow
  [scene17]=main/scene17_ramp_pair_hangang
  [scene18]=main/scene18_wavy_artstair
  [scene19]=main/scene19_fan_winder
  [scene20]=main/scene20_diagonal_oblique
  [scene21]=main/scene21_monumental_selfocclude
  [sceneC1]=batch1/sceneC1_snow_stairs
  [sceneC2]=batch1/sceneC2_leaf_stairs
  [sceneC4]=batch1/sceneC4_wet_stairs
  [sceneD1]=batch1/sceneD1_loading_dock
  [sceneD2]=batch1/sceneD2_floor_opening
  [sceneD3]=batch1/sceneD3_drainage_channel
  [sceneD4]=batch1/sceneD4_subway_platform
  [sceneN1]=batch1/sceneN1_shadow_band
  [sceneN2]=batch1/sceneN2_asphalt_patch
  [sceneN3]=batch1/sceneN3_trompe_loeil
  [sceneN4]=batch1/sceneN4_downhill_ramp
  [sceneN5]=batch1/sceneN5_flush_grating
)
# 씬당 4뷰 — 정체성(overview/beauty) 1 + 진입 1 + 낙차·단서 2 (manifest·소스 대조 검증됨)
declare -A VIEWS=(
  [scene01]=beauty_overview,lower_lookback,edge_closeup,amphi_view
  [scene02]=approach,pit_edge,inside_looking_up,beauty_overview
  [scene03]=levee_walk,stair_down,across_river,bank_oblique
  [scene04]=trail_approach,step_detail,below_lookup,canopy_anchor
  [scene05]=plaza_approach,rim_view,stage_lookup,side_arc
  [scene06]=overview,spiral_up,deck_entry,ground_approach
  [scene07]=gate_frame,temple_walk,stone_rhythm,side_slope
  [scene08]=beauty_overview,pit_edge,stair_south,facade_court
  [scene09]=park_vista,ghat_walk,waterline,across_river
  [scene10]=reversal,through_treads,leaf_edge,from_below
  [scene11]=overview,deck_walk,sidewalk_approach,stair_head
  [scene12]=beauty_overview,edge_void,deck_walk,stair_join
  [scene13]=beauty_overview,entry_approach,bollard_walk,stair_head
  [scene14]=beauty_overview,terrace_read,side_reveal,lower_lookup
  [scene15]=beauty_overview,top_compress,bend_landing,narrow_up
  [scene16]=beauty_overview,approach,shadow_band,under_canopy
  [scene17]=pair_compare,levee_walk,ramp_run,across_river
  [scene18]=color_front,wave_raking,oblique_down,sea_beauty
  [scene19]=roof_skyline,entry_gate,upper_approach,winder_mid
  [scene20]=oblique_overview,walk_axis_front,along_diagonal,low_grazing
  [scene21]=facade_front,oblique,crown_graze,railing_line
  [sceneC1]=approach,grazing_top,rail_side,lower_lookback
  [sceneC2]=approach_walk,buried_edge,rail_cue,beauty_side
  [sceneC4]=approach,grazing_mirror,film_closeup,lower_lookback
  [sceneD1]=beauty_overview,edge_approach,bay_corner,edge_walk
  [sceneD2]=beauty_overview,approach,brink,graze
  [sceneD3]=culvert_far,channel_reveal,verge_walk,oblique_cross
  [sceneD4]=tunnel_vista,track_reveal,edge_approach,edge_graze
  [sceneN1]=beauty_oblique,approach,band_grazing,band_edge_close
  [sceneN2]=beauty_oblique,approach,patch_confusion,patch_grazing
  [sceneN3]=beauty_overview,design_eye,off_axis,joint_cross
  [sceneN4]=beauty_overview,ramp_head,wall_run,landing_lookback
  [sceneN5]=beauty_oblique,approach,grating_close,manhole_pair
)
ORDER=(scene01 scene02 scene03 scene04 scene05 scene06 scene07 scene08 scene09
       scene10 scene11 scene12 scene13 scene14 scene15 scene16 scene17 scene18
       scene19 scene20 scene21 sceneC1 sceneC2 sceneC4 sceneD1 sceneD2 sceneD3
       sceneD4 sceneN1 sceneN2 sceneN3 sceneN4 sceneN5)
KEYS=("${@:-${ORDER[@]}}")

for n in "${KEYS[@]}"; do
  rel=${SCENES[$n]}
  if [ -z "$rel" ]; then echo "[$ROUND] unknown scene $n" | tee -a $LOG; continue; fi
  out=look_check/${n}/${ROUND}
  mkdir -p $out
  python3 scripts/stamp_round.py --capture-env $out >> $LOG 2>&1
  t0=$(date +%s.%N)
  env NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_CAPTURE_DIR=$out \
      NEGOBS_VIEWS=${VIEWS[$n]} NEGOBS_PT_TOTAL_SPP=256 \
      NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1=1 \
      NEGOBS_DETAIL_SCALE=2 NEGOBS_DETAIL_ROUGH_GAIN=0 \
      python scenes/${rel}.py >> $LOG 2>&1
  rc=$?
  t1=$(date +%s.%N)
  dt=$(echo "$t1 - $t0" | bc)
  cuts=$(ls $out/*.png 2>/dev/null | wc -l)
  printf "%s\t%.1f\t%d\t%d\n" "$n" "$dt" "$cuts" "$rc" | tee -a $LOG
  python3 scripts/stamp_round.py $out $ROUND "$n" >> $LOG 2>&1
done
echo "[$ROUND] done (${KEYS[*]})" | tee -a $LOG
