#!/bin/bash
# =============================================================================
# run_w3_text2.sh — **W3 test-ext 본렌더** · 락 입도 개정판
#                   RENDER_PLAN_V3 §3 (D76/D78/D84/D85/D86 개정 반영)
#
# `run_w3_text.sh`(v1)와 **렌더 사양은 한 글자도 다르지 않다.** 바뀐 것은 오직
# **flock 입도**다.
#
# 왜 바꿨나 — v1 스모크 실측 (2026-08-24 02:42–03:0x, 로그 `w3_text_render.log`)
#   컷 1개짜리 스모크의 `[render]`→`[ok]` 델타가 **61 s → 97 s → 226 s → 900 s+** 로
#   단조 증가했다. 렌더 자체는 4 s 다(`variation.json:sec` 3.8). 나머지 전부가
#   **락 대기**다. `flock` 은 FIFO 가 아니라 깨우는 순서가 임의이고, 상대 웨이브
#   (w1c C팔, 24컷 ≈ 4–5분/라운드)가 락을 놓자마자 **자기 다음 라운드로 즉시 재취득**
#   하는 패턴이 반복되면 이쪽이 굶는다. 48회 취득 × 굶주림이면 벽시계가 GPU 시간의
#   3배가 된다.
#
# 개정 — **취득 단위를 (씬, 밴드, 라벨쌍) 으로 올린다**: 한 번의 flock 안에서
#   **한 라벨쌍 2팔**을 연속으로 찍는다. 쌍은 `(A,C)` 와 `(B,D)` — 라벨러가 실제로
#   묶어 도는 단위이자 계기판 ① 의 쌍 규약 그대로다.
#   24컷 × 2팔 ≈ **5–6분 보유** · 취득 **48회 → 24회**.
#   **왜 4팔 일괄이 아닌가**: 4팔이면 11분 보유가 되어 상대 웨이브(24컷 ≈ 4–5분/라운드)
#   보유 시간의 2배를 넘는다. 벽시계는 0.4 h 더 줄지만 그만큼 남의 웨이브를 굶긴다.
#   2팔은 상대와 **같은 보유 시간**이면서 굶주림 대기를 절반으로 줄인다 —
#   *"예의 있게 끼어든다"* 를 **"한 번 잡으면 한 쌍을 끝내고 놓는다"** 로 읽는다.
#
# 산출물 검수는 **락 밖에서** 한다(CPU 작업으로 GPU 를 붙잡지 않는다).
# 그 외 사양 — 팔 레시피 · 밴드 · 조건 L0/L5/L7 · 포즈 8 · 시드 · 사이드카 3종 ·
#   DONE 마커 · "rc 가 아니라 산출물이 판정한다" — 전부 v1 과 동일하다.
#
# 사용
#   bash experiments/v3_0823/code/run_w3_text2.sh smoke
#   bash experiments/v3_0823/code/run_w3_text2.sh prod
#   bash experiments/v3_0823/code/run_w3_text2.sh verify
# =============================================================================
set -u

REPO=/home/vislab/Desktop/work_sy/Practice_NegObs

# 0827 reorg: dataset/ is grouped (dataset/<group>/<round>). A round is
# found by NAME: negobs_round (strict) / negobs_round_or_flat (tolerant).
source "$REPO/scripts/lib/negobs_paths.sh"
LOGDIR="$REPO/experiments/v3_0823/logs"
LOG="$LOGDIR/w3_text_render.log"
MARK="$LOGDIR/w3_markers"
LOCK=/tmp/negobs_gpu.lock
LOCK_WAIT=21600
LOCK_RC=201

SEED=20260823
SEED_B2=20260824
SPLIT=test
CONDS="${CONDS:-L0,L5,L7}"
CAMS="${CAMS:-8}"

STAMP_BASE=260824_v3w3_extbase
STAMP_H=260824_v3w3_exth
STAMP_LAT=260824_v3w3_extlat
STAMP_B2=260824_v3w3_extb2
STAMP_SMOKE=260824_v3w3_extsmoke_A

BAND_H='{"d_min":6,"d_max":12,"h_min":0.25,"h_max":1.0}'
BAND_LAT='{"d_min":3,"d_max":10,"h_min":0.4,"h_max":1.4}'

COMMON12='"cue_railing": false, "cue_tactile": false, "cue_nosing": false, "cue_material_break": false, "cue_sign": false, "cue_scene_dressing": false, "cue_shadow_caster": false, "cue_manhole": false, "cue_tree_grate": false, "cue_slab_joint": false, "cue_drainage": false, "cue_bollard": false'

off_for() {
  case "$1" in
    sceneH1)  echo "$COMMON12"', "cue_delineator": false' ;;
    sceneH2)  echo "$COMMON12"', "cue_planter_edge": false' ;;
    sceneH3)  echo "$COMMON12"', "cue_convex_mirror": false' ;;
    sceneL1)  echo "$COMMON12"', "cue_delineator": false' ;;
    sceneN9)  echo "$COMMON12"', "cue_road_marking": false' ;;
    sceneN11) echo "$COMMON12"', "cue_road_marking": false' ;;
  esac
}
hz_for() {
  case "$1" in
    sceneN9)  echo hazard_platform_edge ;;
    sceneN11) echo hazard_planting_bed ;;
    *)        echo hazard_stairs ;;
  esac
}
cfg_for() {
  local s="$1" arm="$2" hz off
  hz="$(hz_for "$s")"; off="$(off_for "$s")"
  case "$arm" in
    A) echo "{\"$hz\": true}" ;;
    B) echo "{\"$hz\": true, $off}" ;;
    C) echo "{\"$hz\": false, \"keep_dressing\": true}" ;;
    D) echo "{\"$hz\": false, $off}" ;;
  esac
}
bands_for() {
  echo "$STAMP_BASE::$SEED"
  case "$1" in
    sceneH1|sceneH2|sceneH3) echo "$STAMP_H:$BAND_H:$SEED" ;;
    sceneL1)                 echo "$STAMP_LAT:$BAND_LAT:$SEED" ;;
    sceneN9|sceneN11)        echo "$STAMP_B2::$SEED_B2" ;;
  esac
}

MODE="${1:-prod}"
ONLY="${2:-}"
mkdir -p "$LOGDIR" "$MARK"

PRE='cd '"$REPO"' || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1
export NEGOBS_DATA_SIDECARS=1
export NEGOBS_SEG_SIDECAR=1
export NEGOBS_SEG_STRICT=1'

say() { printf '[%s] %s\n' "$(date '+%F %T')" "$*" | tee -a "$LOG"; }

verify_out() {   # verify_out <run> <scene> <want>
  python3 - "$(negobs_round_or_flat "$1")/$SPLIT/$2" "$3" <<'PYEOF'
import glob, hashlib, json, os, sys, zipfile
d, want = sys.argv[1], int(sys.argv[2])
png = glob.glob(os.path.join(d, "*.png"))
dep = glob.glob(os.path.join(d, "*.depth.npy"))
seg = glob.glob(os.path.join(d, "*.idseg.npz"))
stale = glob.glob(os.path.join(d, "*.idseg.STALE"))
hm = glob.glob(os.path.join(d, "heightmap.npy"))
hashes = set()
for f in sorted(seg):
    try:
        with zipfile.ZipFile(f) as z:
            h = hashlib.blake2b(digest_size=8)
            for n in sorted(z.namelist()):
                h.update(z.read(n))
            hashes.add(h.hexdigest())
    except Exception as e:
        hashes.add("ERR:" + repr(e))
ok = (len(png) >= want and len(dep) >= want and len(seg) >= want
      and len(hm) >= 1 and not stale and len(hashes) == len(seg))
print(json.dumps(dict(ok=ok, png=len(png), depth=len(dep), idseg=len(seg),
                      stale=len(stale), hm=len(hm), uniq=len(hashes), want=want)))
sys.exit(0 if ok else 1)
PYEOF
}

# 한 python 호출을 만드는 문자열 (락 안에서 순차 실행된다)
pycall() {  # pycall <scene> <run> <cfg> <band> <seed> <conds> <cams>
  printf "echo '--- %s %s ---'\npython3 experiments/v3_0823/code/h67_probe.py --scene '%s' --run '%s' --conds '%s' --cams %s --seed %s --config '%s' --band '%s'\n" \
    "$1" "$2" "$1" "$2" "$6" "$7" "$5" "$3" "$4"
}

SCENES="sceneH1 sceneH2 sceneH3 sceneL1 sceneN9 sceneN11"
[ -n "$ONLY" ] && SCENES="$ONLY"
WANT=$(( CAMS * $(awk -F, '{print NF}' <<<"$CONDS") ))

T0=$(date +%s)
say "================================================================"
say "run_w3_text2.sh start — mode=$MODE scenes=[$SCENES] conds=$CONDS cams=$CAMS"
say "  락 입도 = (씬,밴드) 단위 4팔 일괄 (v1 의 팔 단위에서 상향 — 굶주림 대책)"
say "================================================================"
FAILS=0

# unit <label> <want> <payload-file>   — 락 한 번, 페이로드 순차 실행
run_unit() {
  local label="$1" pf="$2"
  local t0=$(date +%s)
  say "  [lock-wait] $label"
  flock -o -w "$LOCK_WAIT" -E "$LOCK_RC" "$LOCK" nice -n 5 bash -c "$PRE
$(cat "$pf")" >> "$LOG" 2>&1
  local rc=$?
  local t1=$(date +%s)
  [ "$rc" = "$LOCK_RC" ] && { say "  [LOCK] $label — 락 실패"; return 1; }
  say "  [batch] $label 종료 rc=$rc $(( t1 - t0 ))s"
  return 0
}

case "$MODE" in
  smoke)
    PF=$(mktemp); : > "$PF"; n=0
    for s in $SCENES; do
      [ -f "$MARK/${STAMP_SMOKE}_${s}.done" ] && { say "  [skip] $s smoke"; continue; }
      pycall "$s" "$STAMP_SMOKE" "$(cfg_for "$s" A)" "" "$SEED" L0 1 >> "$PF"
      n=$((n+1))
    done
    if [ "$n" -gt 0 ]; then
      run_unit "smoke ${n}씬 × 1컷" "$PF" || FAILS=$((FAILS+1))
      for s in $SCENES; do
        [ -f "$MARK/${STAMP_SMOKE}_${s}.done" ] && continue
        v=$(verify_out "$STAMP_SMOKE" "$s" 1) \
          && { say "  [ok]   $s smoke · $v"; printf '%s\n' "$v" > "$MARK/${STAMP_SMOKE}_${s}.done"; } \
          || { say "  [FAIL] $s smoke · $v"; FAILS=$((FAILS+1)); }
      done
    fi
    rm -f "$PF"
    ;;
  prod)
    for s in $SCENES; do
      while IFS= read -r spec; do
        pre="${spec%%:*}"; rest="${spec#*:}"
        band="${rest%:*}"; sd="${rest##*:}"
        say "  band=${band:-(기본 CAM_DIST = base)} seed=$sd want=${WANT}/팔"
        # 락 단위 = **라벨쌍** (A,C) → (B,D)
        for pair in "A C" "B D"; do
          PF=$(mktemp); : > "$PF"; n=0; todo=""
          for arm in $pair; do
            if [ -f "$MARK/${pre}_${arm}_${s}.done" ]; then
              say "  [skip] $s ${pre}_${arm} — DONE 마커"; continue
            fi
            pycall "$s" "${pre}_${arm}" "$(cfg_for "$s" "$arm")" "$band" "$sd" \
                   "$CONDS" "$CAMS" >> "$PF"
            todo="$todo $arm"; n=$((n+1))
          done
          if [ "$n" -gt 0 ]; then
            run_unit "$s · $pre · 쌍($(echo $pair | tr ' ' ','))[$todo] · $(( n * WANT ))컷" "$PF" \
              || FAILS=$((FAILS+1))
            for arm in $todo; do
              v=$(verify_out "${pre}_${arm}" "$s" "$WANT") \
                && { say "  [ok]   $s ${pre}_${arm} · $v"
                     printf '%s\n' "$v" > "$MARK/${pre}_${arm}_${s}.done"; } \
                || { say "  [FAIL] $s ${pre}_${arm} · $v"; FAILS=$((FAILS+1)); }
            done
          fi
          rm -f "$PF"
        done
      done < <(bands_for "$s")
    done
    ;;
  verify)
    for s in $SCENES; do
      while IFS= read -r spec; do
        pre="${spec%%:*}"
        for arm in A B C D; do
          [ -d "$(negobs_round_or_flat "${pre}_${arm}")/$SPLIT/$s" ] \
            || { say "  [none] $s ${pre}_${arm}"; FAILS=$((FAILS+1)); continue; }
          v=$(verify_out "${pre}_${arm}" "$s" "$WANT") \
            && say "  [ok]   $s ${pre}_${arm} · $v" \
            || { say "  [FAIL] $s ${pre}_${arm} · $v"; FAILS=$((FAILS+1)); }
        done
      done < <(bands_for "$s")
    done
    ;;
  *) say "[fatal] unknown mode '$MODE'"; exit 2 ;;
esac

T1=$(date +%s)
say "----------------------------------------------------------------"
TOT=0
for pre in "$STAMP_BASE" "$STAMP_H" "$STAMP_LAT" "$STAMP_B2"; do
  for arm in A B C D; do
    d="$(negobs_round_or_flat "${pre}_${arm}")"
    [ -d "$d" ] || continue
    n=$(find "$d" -name '*.png' | wc -l); TOT=$((TOT+n))
    say "  dataset/${pre}_${arm}: $n png · $(find "$d" -name '*.depth.npy' | wc -l) depth · $(find "$d" -name '*.idseg.npz' | wc -l) idseg · $(find "$d" -name '*.idseg.STALE' | wc -l) STALE · $(find "$d" -name 'heightmap.npy' | wc -l) hm"
  done
done
say "누적 컷 $TOT · run_w3_text2.sh($MODE) done in $(( (T1-T0)/60 )) min · 실패 $FAILS"
say "================================================================"
exit $((FAILS > 0))
