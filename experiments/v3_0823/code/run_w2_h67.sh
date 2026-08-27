#!/bin/bash
# =============================================================================
# run_w2_h67.sh — **W2-lite 본렌더** · sceneH6 / sceneH7 (훈련측 val 공급)
#                 RENDER_PLAN_V3 §3.5 (val strict-H ≥ 30 회계)
#
# 무엇을 찍나 — 계획 §3.5 의 밴드 구조를 그대로 이행한다
#   sceneH6_berm_levee2 : base + H + **H2** = 3 밴드 draw → 팔당 72컷
#   sceneH7_bend_walk2  : base + H          = 2 밴드 draw → 팔당 48컷
#     · 조건 = L0 · L5 · L7 (계획 `conds`)  · 포즈 = 8 (계획 `cams`)
#     · 밴드당 3조건 × 8포즈 = 24컷
#     · H  = bands.H = d[6,12] h[0.25,1.0]
#     · H2 = **같은 H 밴드의 2차 draw**(시드만 다르다). 계획 `val_strict_h` 의
#            수율 모형이 H·H2 에 동일한 0.60 을 주므로 밴드 사양이 아니라
#            재추출이다 — W3 의 N9/N11 `base2` 와 같은 규약.
#   4팔 × (72 + 48) = **480컷**.
#
# 팔 (계획 `arms` — 훈련 씬도 A/B/C/D 4팔 사양)
#   A = hazard ON  · 단서 씬 기본값
#   B = hazard ON  · cue_* 최대 제거      (D77)
#   C = hazard OFF · keep_dressing ON     ((A,C))
#   D = hazard OFF · cue_* 전부 OFF       ((C,D))
#
# W3 와 같은 실행 규율
#   · flock 입도 = **(씬, 밴드, 라벨쌍)** — 한 번 잡으면 (A,C) 또는 (B,D) 두 팔을
#     연속으로 찍고 놓는다 (run_w3_text2.sh 개정판의 굶주림 대책 승계)
#   · unset PYTHONPATH VIRTUAL_ENV · conda env_isaaclab · PYTHONNOUSERSITE=1
#   · NEGOBS_DATA_SIDECARS=1 · NEGOBS_SEG_SIDECAR=1 · NEGOBS_SEG_STRICT=1
#   · 밴드마다 **다른 라운드 = 다른 디렉터리** (REG_AUDIT §8.4 (b))
#   · resume-safe DONE 마커 · 스모크 먼저 · **rc 가 아니라 산출물이 판정**
#   · 정본 씬·kit·드라이버 파일은 한 바이트도 고치지 않는다
#
# **검수기 수리 반영 (W3_REPORT §10-1)**: 세그 신선도 기준은 `고유 마스크 == 컷 수`
#   가 아니라 **`고유 마스크 == 포즈 수`** 다. ID 마스크는 조명 무관이므로 24컷
#   라운드의 정상값은 **8**이다. W3 러너는 이 기준을 놓쳐 48/48 라운드를 전부
#   오탐했다 — 여기서는 처음부터 정본 기준으로 판정한다.
#
# 사용
#   bash experiments/v3_0823/code/run_w2_h67.sh smoke
#   bash experiments/v3_0823/code/run_w2_h67.sh prod
#   bash experiments/v3_0823/code/run_w2_h67.sh prod sceneH6
#   bash experiments/v3_0823/code/run_w2_h67.sh verify
# =============================================================================
set -u

REPO=/home/vislab/Desktop/work_sy/Practice_NegObs

# 0827 reorg: dataset/ is grouped (dataset/<group>/<round>). A round is
# found by NAME: negobs_round (strict) / negobs_round_or_flat (tolerant).
source "$REPO/scripts/lib/negobs_paths.sh"
LOGDIR="$REPO/experiments/v3_0823/logs"
LOG="$LOGDIR/w2_h67_render.log"
MARK="$LOGDIR/w2_markers"
LOCK=/tmp/negobs_gpu.lock
LOCK_WAIT=21600
LOCK_RC=201

SEED=20260823          # base / H draw
SEED_H2=20260824       # H2 = 같은 H 밴드의 2차 draw (시드만 다르다)
SPLIT=val              # H6·H7 은 val 배정 (h67_probe.SCENE_FILE)
CONDS="${CONDS:-L0,L5,L7}"
CAMS="${CAMS:-8}"

STAMP_BASE=260824_v3w2_h67base
STAMP_H=260824_v3w2_h67h
STAMP_H2=260824_v3w2_h67h2
STAMP_SMOKE=260824_v3w2_h67smoke_A

BAND_H='{"d_min":6,"d_max":12,"h_min":0.25,"h_max":1.0}'

# ── 팔 레시피 ────────────────────────────────────────────────────────────────
#   B·D 는 그 씬이 실제로 가진 13 cue 키를 **전부** 끈다. 키 목록은 각 씬 파일의
#   SCENE_CONFIG 와 기계 대조했다 (2026-08-24):
#     H6 = 공통 12 + `cue_delineator`      (16키 = cue 13 + hazard 1 + 팔제어 2)
#     H7 = 공통 12 + `cue_level_handrail`  (동상)
COMMON12='"cue_railing": false, "cue_tactile": false, "cue_nosing": false, "cue_material_break": false, "cue_sign": false, "cue_scene_dressing": false, "cue_shadow_caster": false, "cue_manhole": false, "cue_tree_grate": false, "cue_slab_joint": false, "cue_drainage": false, "cue_bollard": false'

off_for() {
  case "$1" in
    sceneH6) echo "$COMMON12"', "cue_delineator": false' ;;
    sceneH7) echo "$COMMON12"', "cue_level_handrail": false' ;;
  esac
}
cfg_for() {   # cfg_for <scene> <arm>   — 두 씬 다 hazard 키는 hazard_stairs
  local s="$1" arm="$2" off
  off="$(off_for "$s")"
  case "$arm" in
    A) echo '{"hazard_stairs": true}' ;;
    B) echo "{\"hazard_stairs\": true, $off}" ;;
    C) echo '{"hazard_stairs": false, "keep_dressing": true}' ;;
    D) echo "{\"hazard_stairs\": false, $off}" ;;
  esac
}
bands_for() {   # "<stamp>:<band-json>:<seed>" 씬별 밴드 draw 목록
  echo "$STAMP_BASE::$SEED"
  echo "$STAMP_H:$BAND_H:$SEED"
  [ "$1" = sceneH6 ] && echo "$STAMP_H2:$BAND_H:$SEED_H2"
  return 0
}

MODE="${1:-smoke}"
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

# 산출물 검수 — rc 가 아니라 **이것이 판정한다**
#   want = 컷 수 · poses = 서로 다른 카메라 포즈 수 (= CAMS). 세그 고유 해시는
#   포즈 수와 같아야 한다 (W3_REPORT §10-1 · h12_gates.gate_vg08 과 같은 기준).
verify_out() {   # verify_out <run> <scene> <want> <poses>
  python3 - "$(negobs_round_or_flat "$1")/$SPLIT/$2" "$3" "$4" <<'PYEOF'
import glob, hashlib, json, os, sys, zipfile
d, want, poses = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
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
# 정본 기준: 고유 마스크 수 == 포즈 수 (컷 수가 아니다 — 조명 3종은 포즈를 공유)
ok = (len(png) >= want and len(dep) >= want and len(seg) >= want
      and len(hm) >= 1 and not stale and len(hashes) == min(poses, len(seg)))
print(json.dumps(dict(ok=ok, png=len(png), depth=len(dep), idseg=len(seg),
                      stale=len(stale), hm=len(hm), uniq=len(hashes),
                      poses=poses, want=want)))
sys.exit(0 if ok else 1)
PYEOF
}

pycall() {  # pycall <scene> <run> <cfg> <band> <seed> <conds> <cams>
  printf "echo '--- %s %s ---'\npython3 experiments/v3_0823/code/h67_probe.py --scene '%s' --run '%s' --conds '%s' --cams %s --seed %s --config '%s' --band '%s'\n" \
    "$1" "$2" "$1" "$2" "$6" "$7" "$5" "$3" "$4"
}

run_unit() {  # run_unit <label> <payload-file>
  local label="$1" pf="$2" t0 t1 rc
  t0=$(date +%s)
  say "  [lock-wait] $label"
  flock -o -w "$LOCK_WAIT" -E "$LOCK_RC" "$LOCK" nice -n 5 bash -c "$PRE
$(cat "$pf")" >> "$LOG" 2>&1
  rc=$?; t1=$(date +%s)
  [ "$rc" = "$LOCK_RC" ] && { say "  [LOCK] $label — 락 실패"; return 1; }
  say "  [batch] $label 종료 rc=$rc $(( t1 - t0 ))s"
  return 0
}

SCENES="sceneH6 sceneH7"
[ -n "$ONLY" ] && SCENES="$ONLY"
WANT=$(( CAMS * $(awk -F, '{print NF}' <<<"$CONDS") ))

T0=$(date +%s)
say "================================================================"
say "run_w2_h67.sh start — mode=$MODE scenes=[$SCENES] conds=$CONDS cams=$CAMS want=$WANT/팔·밴드"
say "================================================================"
FAILS=0

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
        v=$(verify_out "$STAMP_SMOKE" "$s" 1 1) \
          && { say "  [ok]   $s smoke · $v"; printf '%s\n' "$v" > "$MARK/${STAMP_SMOKE}_${s}.done"; } \
          || { say "  [FAIL] $s smoke · $v"; FAILS=$((FAILS+1)); }
      done
    fi
    rm -f "$PF"
    ;;
  prod)
    for s in $SCENES; do
      while IFS= read -r spec; do
        [ -z "$spec" ] && continue
        pre="${spec%%:*}"; rest="${spec#*:}"
        band="${rest%:*}"; sd="${rest##*:}"
        say "  ── $s · $pre · band=${band:-(기본 CAM_DIST = base)} seed=$sd"
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
              v=$(verify_out "${pre}_${arm}" "$s" "$WANT" "$CAMS") \
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
        [ -z "$spec" ] && continue
        pre="${spec%%:*}"
        for arm in A B C D; do
          [ -d "$(negobs_round_or_flat "${pre}_${arm}")/$SPLIT/$s" ] \
            || { say "  [none] $s ${pre}_${arm}"; FAILS=$((FAILS+1)); continue; }
          v=$(verify_out "${pre}_${arm}" "$s" "$WANT" "$CAMS") \
            && say "  [ok]   $s ${pre}_${arm} · $v" \
            || { say "  [FAIL] $s ${pre}_${arm} · $v"; FAILS=$((FAILS+1)); }
        done
      done < <(bands_for "$s")
    done
    ;;
  *) say "[fatal] unknown mode '$MODE' (smoke|prod|verify)"; exit 2 ;;
esac

T1=$(date +%s)
say "----------------------------------------------------------------"
TOT=0
for pre in "$STAMP_BASE" "$STAMP_H" "$STAMP_H2"; do
  for arm in A B C D; do
    d="$(negobs_round_or_flat "${pre}_${arm}")"
    [ -d "$d" ] || continue
    n=$(find "$d" -name '*.png' | wc -l); TOT=$((TOT+n))
    say "  dataset/${pre}_${arm}: $n png · $(find "$d" -name '*.depth.npy' | wc -l) depth · $(find "$d" -name '*.idseg.npz' | wc -l) idseg · $(find "$d" -name '*.idseg.STALE' | wc -l) STALE · $(find "$d" -name 'heightmap.npy' | wc -l) hm"
  done
done
say "누적 컷 $TOT · run_w2_h67.sh($MODE) done in $(( (T1-T0)/60 )) min · 실패 $FAILS"
say "================================================================"
exit $((FAILS > 0))
