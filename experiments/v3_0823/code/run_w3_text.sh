#!/bin/bash
# =============================================================================
# ⚠ **초판 — 본렌더에는 `run_w3_text2.sh` 를 쓴다.** 이 파일은 스모크 6씬을 찍고
#   물러났다. 두 가지가 후속판에서 고쳐졌다:
#   ① flock 입도 — 팔 단위(48회 취득)에서 **라벨쌍 단위**(24회)로. 실측 근거는
#      이 파일이 남긴 스모크 로그다(1컷 라운드의 벽시계 61→97→226→162 s, 렌더 자체는 4 s).
#   ② **검수기 결함** — `verify_out()` 이 세그 신선도를 `고유 마스크 == 컷 수` 로 본다.
#      본렌더 한 밴드 = 8포즈 × 3조건 = 24컷이고 ID 마스크는 조명 무관이므로 **정상값은
#      8**이다. 이 기준은 정상 라운드를 전부 오탐한다. 정본 기준(`포즈 수`)으로 다시
#      판정하는 것은 `w3_verify.py` 이며, 마커도 그쪽이 기록한다.
#      (v2 도 같은 결함을 물려받았다 — 렌더 중 편집이 위험해 살려 두고 우회했다.)
# =============================================================================
# run_w3_text.sh — **W3 test-ext 본렌더** (평가 전용 · 4팔 완비)
#                  RENDER_PLAN_V3 §3 (as amended by D76/D78/D84/D85/D86)
#
# 게이트 개방 근거: D86 — "규정 감사 트랙 완결 — W3 본렌더 게이트 개방".
#
# 무엇을 찍나 — 계획 §3.2 의 **팔당 48프레임**을 그대로 이행한다
#   팔당 48컷 = **밴드 2 × (조건 3 × 포즈 8)** = 2 × 24
#     · 조건 = L0 · L5 · L7   (계획 `conds`, §2.0 "생산 3종")
#     · 포즈 = 8              (계획 `cams`. 두 조건은 같은 시드·같은 카메라
#                              인덱스를 쓰므로 CAMS 가 곧 포즈 수다)
#     · 밴드 = 씬별로 계획 `bands` 가 지정한 2개
#         H1·H2·H3 : base + H     (bands.H  = d[6,12] h[0.25,1.0])
#         L1       : base + LAT   (bands.LAT= d[3,10] h[0.4,1.4])
#         N9·N11   : base + base2 (base2 = 같은 지지집합의 2차 draw, 시드만 다름)
#
#   as-built 6씬 × 4팔 × 48 = **1,152컷**. 계획 §3.2 의 9씬 1,728컷 중
#   B안 대기 3씬(H4·L2·N12) 576컷은 **씬 파일이 없으므로 미렌더**로 인쇄한다.
#
# 팔 (test-ext 는 A·B·C·D 완비가 의무 — §3.1)
#   A = hazard ON  · 단서 씬 기본값        (기준 팔)
#   B = hazard ON  · cue_* **최대 제거**   (§1.2 B팔 레버 · D77 최대 제거 채택)
#   C = hazard OFF · keep_dressing ON      (계기판 ① 의 반사실 짝 · (A,C))
#   D = hazard OFF · cue_* 전부 OFF        (순수 씬-연합 게이지 · (C,D))
#
# **밴드가 라운드명 안에 있어야 하는 이유** (D23 의 확장)
#   D85 ⑦ / REG_AUDIT §8.4 (b) 실측: **산출물 디렉터리가 이미 있으면 세그 경로가
#   재생성되지 않는다.** 한 씬의 두 밴드를 같은 스탬프로 찍으면 두 번째 밴드가
#   첫 밴드의 `.idseg.npz` 를 물려받고, VG-06(모서리 소속)과 DZ §12-5 의 단서
#   임계 k 가 조용히 거짓이 된다. ⇒ 밴드마다 **다른 라운드 = 다른 디렉터리**.
#
# 규율
#   · **씬 프로세스마다** flock -o /tmp/negobs_gpu.lock (C 웨이브와 GPU 공유 —
#     24컷 단위로 끊어 상대를 굶기지 않는다)
#   · unset PYTHONPATH VIRTUAL_ENV · conda env_isaaclab · PYTHONNOUSERSITE=1
#   · NEGOBS_DATA_SIDECARS=1 · NEGOBS_SEG_SIDECAR=1 · **NEGOBS_SEG_STRICT=1**
#   · resume-safe DONE 마커 — 완성된 (라운드,씬)은 건너뛴다
#   · **종료코드로 판정하지 않는다.** Isaac 의 사이드카 팔은 `os._exit(0)` 로 끝나
#     씬이 죽어도 rc=0 이다(REG_AUDIT §8.4). **산출물이 판정한다** —
#     png/depth/idseg 개수 + heightmap + **컷별 마스크 고유성**.
#   · 정본 씬·kit·드라이버 파일은 한 바이트도 고치지 않는다
#
# 사용
#   bash experiments/v3_0823/code/run_w3_text.sh smoke
#   bash experiments/v3_0823/code/run_w3_text.sh prod
#   bash experiments/v3_0823/code/run_w3_text.sh prod sceneH1     # 한 씬만
#   bash experiments/v3_0823/code/run_w3_text.sh verify           # 렌더 없이 검수만
# =============================================================================
set -u

REPO=/home/vislab/Desktop/work_sy/Practice_NegObs
LOGDIR="$REPO/experiments/v3_0823/logs"
LOG="$LOGDIR/w3_text_render.log"
MARK="$REPO/experiments/v3_0823/logs/w3_markers"
LOCK=/tmp/negobs_gpu.lock
LOCK_WAIT=14400
LOCK_RC=201

SEED=20260823                 # base / H / LAT draw
SEED_B2=20260824              # base2 = 같은 지지집합의 2차 draw (시드만 다르다)
SPLIT=test                    # 6씬 전부 test-ext → `vk.split_of` 가 test 를 준다
CONDS="${CONDS:-L0,L5,L7}"    # 계획 `conds` — 생산 3종
CAMS="${CAMS:-8}"             # 계획 `cams` — = 포즈 수. × 3조건 = 밴드당 24컷

STAMP_BASE=260824_v3w3_extbase
STAMP_H=260824_v3w3_exth
STAMP_LAT=260824_v3w3_extlat
STAMP_B2=260824_v3w3_extb2
STAMP_SMOKE=260824_v3w3_extsmoke_A

BAND_H='{"d_min":6,"d_max":12,"h_min":0.25,"h_max":1.0}'
BAND_LAT='{"d_min":3,"d_max":10,"h_min":0.4,"h_max":1.4}'

# ── 팔 레시피 ────────────────────────────────────────────────────────────────
#   B·D 는 그 씬이 실제로 가진 13 cue 키를 **전부** 끈다(기본 OFF 키도 명시한다 —
#   레시피는 선언이지 추론이 아니다). 키 목록은 각 씬 파일의 SCENE_CONFIG 와
#   기계 대조했다(2026-08-24, D85/D86 판).
COMMON12='"cue_railing": false, "cue_tactile": false, "cue_nosing": false, "cue_material_break": false, "cue_sign": false, "cue_scene_dressing": false, "cue_shadow_caster": false, "cue_manhole": false, "cue_tree_grate": false, "cue_slab_joint": false, "cue_drainage": false, "cue_bollard": false'
H1_OFF="$COMMON12"', "cue_delineator": false'
H2_OFF="$COMMON12"', "cue_planter_edge": false'
H3_OFF="$COMMON12"', "cue_convex_mirror": false'
L1_OFF="$COMMON12"', "cue_delineator": false'
N9_OFF="$COMMON12"', "cue_road_marking": false'
N11_OFF="$COMMON12"', "cue_road_marking": false'

hz_for() {
  case "$1" in
    sceneN9)  echo hazard_platform_edge ;;
    sceneN11) echo hazard_planting_bed ;;
    *)        echo hazard_stairs ;;
  esac
}

off_for() {
  case "$1" in
    sceneH1)  echo "$H1_OFF" ;;
    sceneH2)  echo "$H2_OFF" ;;
    sceneH3)  echo "$H3_OFF" ;;
    sceneL1)  echo "$L1_OFF" ;;
    sceneN9)  echo "$N9_OFF" ;;
    sceneN11) echo "$N11_OFF" ;;
  esac
}

cfg_for() {   # cfg_for <scene> <arm>
  local s="$1" arm="$2" hz off
  hz="$(hz_for "$s")"; off="$(off_for "$s")"
  case "$arm" in
    A) echo "{\"$hz\": true}" ;;
    B) echo "{\"$hz\": true, $off}" ;;
    C) echo "{\"$hz\": false, \"keep_dressing\": true}" ;;
    D) echo "{\"$hz\": false, $off}" ;;
  esac
}

# 씬의 두 밴드 = "<stamp-prefix>:<band-json>:<seed>" 두 줄
bands_for() {   # bands_for <scene>
  echo "$STAMP_BASE::$SEED"
  case "$1" in
    sceneH1|sceneH2|sceneH3) echo "$STAMP_H:$BAND_H:$SEED" ;;
    sceneL1)                 echo "$STAMP_LAT:$BAND_LAT:$SEED" ;;
    sceneN9|sceneN11)        echo "$STAMP_B2::$SEED_B2" ;;
  esac
}

MODE="${1:-smoke}"
ONLY="${2:-}"

mkdir -p "$LOGDIR" "$MARK"

PRE='cd '"$REPO"' || exit 9
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1'

say() { printf '[%s] %s\n' "$(date '+%F %T')" "$*" | tee -a "$LOG"; }

# ── 산출물 검수 — **rc 가 아니라 이것이 판정한다** ──────────────────────────
# 1) png / depth / idseg 개수 ≥ want   2) heightmap 1개
# 3) `.idseg.STALE` 마커 0             4) **컷별 마스크 고유 해시 = 컷 수**
#    (4)는 D85 ⑦ 이 노출한 "첫 컷 마스크 복제" 를 라운드 밖에서 다시 잡는 그물이다.
verify_out() {   # verify_out <run> <scene> <want>
  local run="$1" scene="$2" want="$3"
  local d="$REPO/dataset/$run/$SPLIT/$scene"
  python3 - "$d" "$want" <<'PYEOF'
import glob, hashlib, json, os, sys, zipfile
d, want = sys.argv[1], int(sys.argv[2])
png = glob.glob(os.path.join(d, "*.png"))
dep = glob.glob(os.path.join(d, "*.depth.npy"))
seg = glob.glob(os.path.join(d, "*.idseg.npz"))
stale = glob.glob(os.path.join(d, "*.idseg.STALE"))
hm = glob.glob(os.path.join(d, "heightmap.npy"))
# npz 는 zip 이라 타임스탬프가 섞인다 → **압축 해제된 멤버 바이트**를 해싱한다.
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
                      stale=len(stale), hm=len(hm), uniq=len(hashes),
                      want=want)))
sys.exit(0 if ok else 1)
PYEOF
}

# render <scene> <run> <config-json> <band-json|""> <seed> <conds> <cams>
render() {
  local scene="$1" run="$2" cfg="$3" band="$4" sd="$5"
  local cds="${6:-$CONDS}" cms="${7:-$CAMS}"
  local want=$(( cms * $(awk -F, '{print NF}' <<<"$cds") ))
  local done_mark="$MARK/${run}_${scene}.done"
  if [ -f "$done_mark" ]; then
    say "  [skip] $scene $run — DONE 마커"
    return 0
  fi
  say "  [render] $scene run=$run conds=$cds cams=$cms seed=$sd (want $want)"
  say "           cfg=$cfg"
  say "           band=${band:-(기본 CAM_DIST = base)}"
  local t0=$(date +%s)
  flock -o -w "$LOCK_WAIT" -E "$LOCK_RC" "$LOCK" nice -n 5 bash -c "$PRE
export NEGOBS_DATA_SIDECARS=1
export NEGOBS_SEG_SIDECAR=1
export NEGOBS_SEG_STRICT=1
python3 experiments/v3_0823/code/h67_probe.py \
        --scene '$scene' --run '$run' --conds '$cds' --cams $cms \
        --seed $sd --config '$cfg' --band '$band'" >> "$LOG" 2>&1
  local rc=$?
  local t1=$(date +%s)
  if [ "$rc" = "$LOCK_RC" ]; then
    say "  [LOCK] $scene $run — ${LOCK_WAIT}s 안에 GPU 락 실패"
    return 1
  fi
  local v
  v=$(verify_out "$run" "$scene" "$want")
  local vrc=$?
  if [ "$vrc" = 0 ]; then
    say "  [ok]   $scene $run rc=$rc $(( t1 - t0 ))s · $v"
    printf '%s\n' "$v" > "$done_mark"
    return 0
  fi
  say "  [FAIL] $scene $run rc=$rc $(( t1 - t0 ))s · $v"
  return 1
}

SCENES="sceneH1 sceneH2 sceneH3 sceneL1 sceneN9 sceneN11"
[ -n "$ONLY" ] && SCENES="$ONLY"

T0=$(date +%s)
say "================================================================"
say "run_w3_text.sh start — mode=$MODE scenes=[$SCENES] conds=$CONDS cams=$CAMS"
say "================================================================"

FAILS=0
case "$MODE" in
  smoke)
    # 씬 프로세스당 1프레임. 프림 위생·SdfPath·사이드카를 본렌더 전에 확인한다.
    for s in $SCENES; do
      render "$s" "$STAMP_SMOKE" "$(cfg_for "$s" A)" "" $SEED L0 1 \
        || FAILS=$((FAILS+1))
    done
    ;;
  prod)
    for s in $SCENES; do
      while IFS= read -r spec; do
        pre="${spec%%:*}"; rest="${spec#*:}"
        band="${rest%:*}"; sd="${rest##*:}"
        for arm in A B C D; do
          render "$s" "${pre}_${arm}" "$(cfg_for "$s" "$arm")" "$band" "$sd" \
            || FAILS=$((FAILS+1))
        done
      done < <(bands_for "$s")
    done
    ;;
  verify)
    for s in $SCENES; do
      while IFS= read -r spec; do
        pre="${spec%%:*}"
        for arm in A B C D; do
          d="$REPO/dataset/${pre}_${arm}/$SPLIT/$s"
          [ -d "$d" ] || { say "  [none] $s ${pre}_${arm}"; FAILS=$((FAILS+1)); continue; }
          v=$(verify_out "${pre}_${arm}" "$s" $(( CAMS * 3 )))
          [ $? = 0 ] && say "  [ok]   $s ${pre}_${arm} · $v" \
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
for pre in "$STAMP_BASE" "$STAMP_H" "$STAMP_LAT" "$STAMP_B2"; do
  for arm in A B C D; do
    d="$REPO/dataset/${pre}_${arm}"
    [ -d "$d" ] || continue
    n=$(find "$d" -name '*.png' | wc -l)
    TOT=$((TOT+n))
    say "  dataset/${pre}_${arm}: $n png · $(find "$d" -name '*.depth.npy' | wc -l) depth · $(find "$d" -name '*.idseg.npz' | wc -l) idseg · $(find "$d" -name '*.idseg.STALE' | wc -l) STALE · $(find "$d" -name 'heightmap.npy' | wc -l) hm"
  done
done
say "누적 컷 $TOT · run_w3_text.sh done in $(( (T1-T0)/60 )) min · 실패 $FAILS"
say "================================================================"
exit $((FAILS > 0))
