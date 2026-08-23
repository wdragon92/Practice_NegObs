#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w1b_verify.py — W1 B팔 착지 검사. **VG-01이 이 웨이브의 중심 게이트다.**

무엇을 검사하나
---------------
1. **렌더 회계** — 라운드×씬 컷 수 · s/컷 · GPU-h · 디스크 · D74 스킵 168컷 명시.
2. **VG-01 (A/B 위험-GT 동일성)** — 계획 §6.1. 3층으로 잰다:
   (ㄱ) **바이트층**: `sha256(B/heightmap.npy) == sha256(A/heightmap.npy)`.
        `heightmap_meta.json`은 `arm_config`·`n_prims`가 **구성상 달라야** 하므로
        (B는 레버를 껐다) 바이트 동일을 요구할 수 없다 — 기하 필드
        (x0·y0·step·nx·ny·n_finite·n_total·z_min·z_max)만 대조한다.
   (ㄴ) **씬층**: 라벨러 `cells_raw`(A) == `cells_raw`(B).
   (ㄷ) **프레임층**: `polar_gt` 비트 동일 · `polar_gt_pregate` · `gate_excluded`.
   하나라도 어긋나면 그 (밴드, 씬)의 B팔은 **격리**한다. 계획 §6.1의 문면 그대로:
   *"그 `cue_*`는 구조물 → 토글 금지 목록 등재, 그 씬의 B팔 폐기"*.
   이것이 장식 분류 전체의 **실증 뒷받침**이다 — W0·W1-D는 A와 Bx 렌더로 분류를
   내렸지만, 그 분류를 실제 생산 레시피(여러 레버 동시 제거)에 적용했을 때도
   낙차가 불변인지는 여기서 처음 실측된다.
3. **코퍼스 이전 대조** — 본 드라이버로 다시 잰 A가 정본 코퍼스
   (`dataset_manifest_v2corr.json`, 240프레임 `g7fix-B` 교정 포함)의 `polar_gt`를
   재현하는가. 재현하면 2의 판정이 훈련 GT로 그대로 이전된다. 재현하지 않으면
   그 씬의 VG-01 판정은 **내 파이프라인 기준**이라고 명시해야 한다.
3-b. **z_off 규약** — 게이트 라벨의 z_off는 **D팔**이다(cue-대칭 · B의 생산 짝).
   정본 구off는 `hazard_*: false`만 준 팔이라 자유결속 단서를 남기므로, B가 그
   드레싱을 지운 자리에서 **유령 발자국**이 생긴다(W0_CUECLS §3). 실측으로
   sceneD2 3,129셀 · sceneD3 2,644셀 · scene21 298셀 · sceneD1 66셀이 그렇게
   생겼고, z_off를 D팔로 바꾸면 넷 다 **정확히 0**이 된다. 구off 기준 값은
   `hm_diff_guoff_ref`에 진단으로만 남긴다.

4. **VG-datum (A,B)** — 컷별 |Δ`ground_z`| 3층(exact <1e-6 · tol ≤0.02 m ·
   fail >0.02 m). fail 쌍은 격리. D74 ②가 남긴 기지 위반자(s02·s10·sN1)를 예상.
5. **VG-10 (포즈)** — 같은 컷의 `d·h_rel·yaw·pitch·roll·hfov` + `cam.eye` 최대차.
6. **VG-08 + per-cut 세그 판별성** — 사이드카 존재 + **컷마다 다른 마스크**.
   D73 ①이 확정한 `idseg_fetch="t0"` stale 결함의 사후 실증이다. D74 ④가
   제안한 per-cut 절을 그대로 판정한다: 씬 프로세스 안에서 `.idseg.npz`의
   sha256 고유 개수 == 컷 수여야 한다.

사용:  python3 experiments/v3_0823/code/w1b_verify.py
산출:  experiments/v3_0823/w1b_verify.json  (+ stdout 표)
"""
import glob
import hashlib
import json
import os
import sys

import numpy as np

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V3 = os.path.join(REPO, "experiments/v3_0823")
ANN = os.path.join(V3, "annotations")
LABDIR = os.path.join(REPO, "experiments/mainrun_0819/code/labeling")
sys.path.insert(0, LABDIR)
import labeler as LB                                            # noqa: E402

GRID = json.load(open(os.path.join(LABDIR, "gridspec_v1.json"), encoding="utf-8"))
HAZ_DEPTH = float(GRID["hazard_depth_m"])

# --- W1-B2 보충 웨이브 스위치 (DECISIONS D75 ③ · W1B_REPORT §8.1) ----------
# `W1B_ARM=B`  (기본)  → 착지한 `260826_v3w1_lib_B*` · 산출 `w1b_*`  (W1-B 재현 그대로)
# `W1B_ARM=B2`         → T레버 보충본 `260826_v3w1_lib_B2*` · **12씬만** · 산출 `w1b2_*`
# 어느 쪽이든 코퍼스 A팔·D팔·구off 참조와 게이트 술어는 **한 글자도 다르지 않다**.
# --- W1-B3 보충 웨이브 스위치 (DECISIONS **D90 ①** · 세그 3차 `w1d_seg3.json`) ---
# `W1B_ARM=B3` → 레버 추가 재렌더 `260827_v3w1_lib_B3*` · **5씬만** · 산출 `w1b3_*`
# 게이트 술어·A팔·D팔 참조는 B/B2 와 **한 글자도 다르지 않다**(계기 동일성).
ARM = os.environ.get("W1B_ARM", "B")
if ARM not in ("B", "B2", "B3"):
    raise SystemExit(f"W1B_ARM must be B, B2 or B3, got {ARM!r}")
TAG = {"B": "w1b", "B2": "w1b2", "B3": "w1b3"}[ARM]
B2_SCENES = set("scene02 scene08 scene09 scene12 scene16 scene17 scene20 "
                "scene21 sceneC1 sceneC4 sceneD1 sceneD3".split())
B3_SCENES = set("scene01 scene09 scene21 sceneC1 sceneC4".split())


def _sel(ss):
    """B2 는 T레버 보충 12씬 · B3 는 레버 추가 5씬만 다시 찍었다."""
    if ARM == "B":
        return list(ss)
    return [s for s in ss if s in (B2_SCENES if ARM == "B2" else B3_SCENES)]

B = ("260827_v3w1_lib_B3" if ARM == "B3"
     else f"260826_v3w1_lib_{ARM}")
BANDS = {
    "base": (B, "260819_main_on",
             _sel("scene01 scene02 scene06 scene08 scene09 scene12 scene16 scene17 "
                  "scene20 scene21 sceneC1 sceneC4 sceneD1 sceneD2 sceneD3".split())),
    "h":    (f"{B}_h", "260820_boost_h_on", _sel("scene09 scene17".split())),
    "e":    (f"{B}_e", "260820_boost_e_on",
             _sel("scene08 scene09 scene12 scene17 scene20 sceneC1 sceneC4".split())),
    "e2":   (f"{B}_e2", "260820_boost_e2_on", _sel("scene12 scene20 sceneC4".split())),
}
A_OVERLAY = {("e", "scene08"): "260820_boost_e_on_g7fixM",
             ("e", "scene12"): "260820_boost_e_on_g7fixM",
             ("e2", "scene12"): "260820_boost_e2_on_g7fixM"}
DD = "260826_v3w1_lib_D"
# 게이트 z_off = 밴드가 맞는 D팔 (cue-대칭 · B의 생산 짝). 구off는 진단용으로만.
D_ROUND = dict(base=DD, h=f"{DD}_h", e=f"{DD}_e", e2=f"{DD}_e2")
OFF_PLAIN = dict(base="260819_main_off", h="260820_boost_h_off",
                 e="260820_boost_e_off", e2="260820_boost_e2_off")
OFF_OVERLAY = {("e", "scene08"): "260820_boost_e_off_g7fixM",
               ("e", "scene12"): "260820_boost_e_off_g7fixM",
               ("e2", "scene12"): "260820_boost_e2_off_g7fixM"}
SUFFIX = dict(base="", h="::boost_h", e="::boost_e", e2="::boost_e2")
SKIPPED_D74 = {"scene03": 72, "scene04": 72, "scene10": 24}     # = 168컷
DATUM_EXACT, DATUM_TOL = 1e-6, 0.02
POSE_KEYS = ("d", "h_rel", "yaw", "pitch", "roll", "hfov")
GEO_KEYS = ("x0", "y0", "step", "nx", "ny", "n_finite", "n_total", "z_min", "z_max")


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def sdir(run, scene):
    g = glob.glob(os.path.join(REPO, "dataset", run, "*", scene, "variation.json"))
    return os.path.dirname(g[0]) if g else None


def a_dir(band, scene):
    r = A_OVERLAY.get((band, scene), BANDS[band][1])
    return sdir(r, scene), r


def off_dir(band, scene):
    """진단용 구off (코퍼스 규약)."""
    r = OFF_OVERLAY.get((band, scene), OFF_PLAIN[band])
    return sdir(r, scene), r


def gate_off_dir(band, scene):
    """게이트 z_off = D팔. 구off는 cue-비대칭이라 B에 유령 발자국을 만든다."""
    r = D_ROUND[band]
    return sdir(r, scene), r


def cuts_of(d):
    v = json.load(open(os.path.join(d, "variation.json"), encoding="utf-8"))
    cu = v["cuts"]
    cu = list(cu.values()) if isinstance(cu, dict) else cu
    return {c["file"]: c for c in cu}, v


def datum_pose(ca, cb):
    common = sorted(set(ca) & set(cb))
    tiers = dict(datum_exact=0, datum_tol=0, datum_fail=0)
    worst, pose_worst, fails = 0.0, 0.0, []
    for f in common:
        a, b = ca[f]["cam"], cb[f]["cam"]
        dz = abs(float(a["ground_z"]) - float(b["ground_z"]))
        t = ("datum_exact" if dz < DATUM_EXACT
             else "datum_tol" if dz <= DATUM_TOL else "datum_fail")
        tiers[t] += 1
        worst = max(worst, dz)
        if t == "datum_fail":
            fails.append(dict(file=f, d_ground_z=round(dz, 6),
                              a_ground_z=round(float(a["ground_z"]), 6),
                              b_ground_z=round(float(b["ground_z"]), 6)))
        pk = max(abs(float(a[k]) - float(b[k])) for k in POSE_KEYS)
        pe = max(abs(float(a["eye"][i]) - float(b["eye"][i])) for i in range(3))
        pose_worst = max(pose_worst, pk, pe)
    return dict(n_cuts=len(common), n_a=len(ca), n_b=len(cb), tiers=tiers,
                ground_z_drift_max=round(worst, 8),
                pose_delta_max=round(pose_worst, 9),
                verdict=("datum_fail" if tiers["datum_fail"]
                         else "datum_tol" if tiers["datum_tol"] else "datum_exact"),
                fail_cuts=fails[:8], n_fail_cuts=len(fails))


def seg_audit(d, cuts):
    """VG-08 + per-cut 판별성 — **포즈 기준**으로 잰다 (D74 ④ per-cut 절).

    올바른 술어를 먼저 못 박는다. 컷 24개는 `조건 3 × 카메라 8`이고, **조건은
    조명만 바꾼다**. 인스턴스-ID 세그는 조명 불변이므로 같은 포즈의 세 컷은
    마스크가 **같아야 정상**이다. "컷마다 전부 다른 마스크"를 요구하면 정상
    라운드가 떨어진다.

    **판정(hard)**: 서로 다른 포즈가 같은 마스크를 공유하면 실패다 —
    `포즈 간 충돌 0` 이고 `고유 마스크 수 ≥ 고유 포즈 수`. D73 ①이 잡은 stale의
    지문(`고유 마스크 1개 / 포즈 8개` · `idseg_n_ids` 상수)이 정확히 이 조건에
    걸린다.

    **관찰(soft)**: `고유 마스크 수 > 고유 포즈 수`는 stale의 **반대**다 — 같은
    포즈인데 조건마다 바이트가 갈렸다는 뜻이다. 실패로 찍지 않고 사유와 함께 세고,
    `prim_normalized_check()`로 무해함을 실증한다.

    **원인은 규명됐다 — 인스턴스 ID 재번호다.** `B_h scene09`의 한 포즈(L0/L5/L7)를
    프림 경로로 정규화해 열어 보면 `idToLabels` 항목 수 89,437 · 고유 ID 수 30,992 ·
    화면에 잡힌 프림 경로 474개 · **경로별 픽셀 수까지 완전 동일**인데 파일
    sha256만 셋 다 다르다. 어노테이터가 평가할 때마다 `id → 프림` 번호를 새로
    매기기 때문이다. `sceneC1`의 별도 프로세스(L4)도 같은 기전이다.

    ⇒ **VG-03을 `.idseg.npz` 해시로 구현하면 안 된다.** 프림 경로로 정규화한 뒤
    경로별 픽셀 집합을 비교해야 한다. 반대로 **stale 검출은 바이트 해시가 옳다** —
    재번호는 바이트를 *다르게* 만들 뿐이라 stale(다른 포즈가 **같은 바이트**)을
    위장할 수 없다.
    """
    PK = ("d", "h_rel", "yaw", "pitch", "roll", "hfov")
    hs, nid, fetch, pose_of = {}, set(), set(), {}
    missing = 0
    for f, c in sorted(cuts.items()):
        cam = c["cam"]
        pose_of[f] = (tuple(round(float(cam[k]), 6) for k in PK) +
                      tuple(round(float(x), 6) for x in cam["eye"]))
        p = os.path.join(d, os.path.splitext(f)[0] + ".idseg.npz")
        if not os.path.isfile(p):
            missing += 1
            continue
        hs.setdefault(sha256(p), []).append(f)
        if c.get("idseg_n_ids") is not None:
            nid.add(int(c["idseg_n_ids"]))
        if c.get("idseg_fetch"):
            fetch.add(c["idseg_fetch"])
    n = len(cuts)
    poses = {p_ for p_ in pose_of.values()}
    # 포즈 간 충돌: 한 마스크가 두 개 이상의 포즈에 걸침
    collide = {h[:12]: sorted({pose_of[f] for f in v})[:2]
               for h, v in hs.items() if len({pose_of[f] for f in v}) > 1}
    # 조명 의존: 한 포즈 안에서 마스크가 갈림
    per_pose = {}
    for h, v in hs.items():
        for f in v:
            per_pose.setdefault(pose_of[f], set()).add(h)
    light_dep = sum(1 for v in per_pose.values() if len(v) > 1)
    stale_signature = (len(poses) > 1 and len(hs) == 1)
    return dict(n_cuts=n, n_sidecars=n - missing, missing=missing,
                n_poses=len(poses), n_unique_masks=len(hs),
                n_ids_distinct=sorted(nid), fetch=sorted(fetch),
                distinct=(missing == 0 and not collide and len(hs) >= len(poses)),
                n_pose_collisions=len(collide), n_light_dependent_poses=light_dep,
                over_discriminating=(len(hs) > len(poses)),
                stale_signature=stale_signature,
                collide_examples=collide)


# --------------------------------------------------------------------------
# T2-seg — 세그 3차 소유권으로 설명되는 `cells_raw` 갈림 (DECISIONS **D90 ①**)
# --------------------------------------------------------------------------
# **문제.** 낙차를 위에서 덮는 단서(난간 상판·데크형 드레싱)를 지우면 하향 광선이
# 그 아래의 **원래 있던** 낙차를 새로 읽는다. 그래서 씬 전역 `cells_raw` 는 갈리는데
# **훈련 라벨 `polar_gt` 는 비트 동일**하다. 높이맵 계기만으로는 이것과 "레버가
# 지면을 진짜로 팠다"를 구별할 수 없다 — 두 검정이 같은 하향 광선을 공유하기 때문.
#
# **세그가 가른다.** `w1d_seg3.json` 의 규칙 S4(덮개)는 갈린 셀의 **과반이 그 단서
# 자신의 픽셀**임을 컷별 ID 마스크로 실증한 쌍에만 붙는다. 그 경우 Δ는 가림
# 인공물이고 낙차 기하는 불변이다.
#
# **본 파일은 판정을 바꾸지 않는다.** `vg01_pass` 의 의미는 한 글자도 건드리지 않고
# (기본 = 보수적 격리), `vg01_t2seg` · `vg01_pass_seg3` · `quarantine_if_seg3_admitted`
# 를 **추가로 계산해 인쇄**한다. 어느 쪽을 코퍼스에 쓸지는 결재 사안이다
# (`build_corpus_v3.py --admit-seg3`).
def _seg3_released():
    """(scene, cue) -> seg3 판정 행. 없으면 빈 dict."""
    p3 = os.path.join(V3, "w1d_seg3.json")
    if not os.path.exists(p3):
        return {}
    d = json.load(open(p3, encoding="utf-8"))
    return {(r["scene"], r["cue"]): r for r in d["pairs"]}


def _added_levers(scene):
    """B3 레시피가 **직전 웨이브 대비 새로 끈** cue 키 목록."""
    rc = os.path.join(V3, "render_configs_v3")
    cur = os.path.join(rc, f"{scene}_B3.json")
    if not os.path.exists(cur):
        return None
    new = json.load(open(cur, encoding="utf-8"))
    prev = {}
    for suf in ("_B2", "_B"):
        q = os.path.join(rc, f"{scene}{suf}.json")
        if os.path.exists(q):
            prev = json.load(open(q, encoding="utf-8"))
            break
    return sorted(k for k, v in new.items()
                  if k.startswith("cue_") and v is False and prev.get(k) is not False)


def t2seg_verdict(scene, hd, gt_ok, cells_ok, SEG3):
    """T2-seg 자격 판정 — 네 조건 **전부**."""
    if ARM != "B3":
        return None
    add = _added_levers(scene)
    if add is None:
        return None
    ok_gt = bool(gt_ok) and not bool(cells_ok)
    pure_add = (hd or {}).get("fp_only_A") == 0
    per_cue, all_ok = [], True
    for c in add:
        r = SEG3.get((scene, c)) or {}
        rule = (r.get("t3_rule") or "")[:2]
        rel = (r.get("final") == "장식")
        dcell = r.get("d_cells_raw")
        # Δ에 기여하지 않는 키(Δcells_raw = 0)는 규칙과 무관하게 무해하다.
        good = rel and (dcell == 0 or rule == "S4")
        all_ok = all_ok and good
        per_cue.append(dict(cue=c, seg3_final=r.get("final"), rule=rule,
                            own_S=r.get("own_S"), d_cells_raw=dcell, ok=good))
    return dict(added_levers=add, per_cue=per_cue,
                polar_gt_identical=bool(gt_ok), cells_raw_identical=bool(cells_ok),
                fp_only_A=(hd or {}).get("fp_only_A"),
                fp_only_B=(hd or {}).get("fp_only_B"),
                pure_addition=bool(pure_add),
                eligible=bool(ok_gt and pure_add and all_ok and add),
                rule="polar_gt 비트동일 ∧ cells_raw 갈림 ∧ fp_only_A = 0(순증) ∧ "
                     "추가 레버 전부가 seg3 해제(S4 덮개 또는 Δcells_raw = 0)")


def hm_diff(da, db, do):
    """A·B 높이맵의 차이가 **위험 GT에 닿는가**를 계기 그대로 재는 진단.

    왜 필요한가 — scene06이 가르쳐 준 것
    -------------------------------------
    계획 §6.1의 VG-01 문면은 `heightmap.npy` + `heightmap_meta.json` **바이트
    동일**을 요구한다. 그런데 `heightmap_meta.json`은 `arm_config`가 들어 있어
    **어떤 B팔에서도 바이트 동일이 불가능**하다(B는 정의상 레버를 껐다). 즉
    문면 그대로는 만족 불가능한 조건이고, 실질 내용은 뒤의 두 절
    (`cells_raw` 동일 · `polar_gt` 비트 동일)에 있다.

    scene06 실측이 그 차이를 눈에 보이게 만들었다. AABB 높이맵이 1,605셀에서
    0.3 m 이상 갈리는데, **갈리는 셀의 A값이 전부 정확히 z = 6.100**이었다 —
    하늘에서 쏜 광선이 제거된 드레싱(수관·상판)의 **꼭대기**를 읽던 자리다.
    z_off는 그 자리에서 −0.15 m라 `z_off − z_on ≥ 0.3`이 성립할 수 없고,
    실제로 `fp_A = fp_B = 0`(대칭차 0)이다. **보행면 위쪽에서만 갈렸다.**

    그래서 3층으로 판정한다.
      T1        높이맵 바이트 동일 + GT 동일   — 레버가 GT를 건드릴 수 없음(구성적)
      T2        바이트는 다르나 GT 동일         — 차이가 보행면 위 / 서브밀리
      T3-instr  **원 AABB는 GT 규모로 불변**인데 라벨이 갈림 — 융합 계기의 시점 의존
      T3-geom   원 AABB가 위험 GT 안에서 움직임 — **레버가 구조물** → 격리

    T3-geom만 계획 §7.4의 "VG-01 실패" 대응(그 키만 금지 + 남은 키로 재렌더)에 건다.
    T3-instr의 처방은 레버가 아니라 **쌍의 GT 계기 확정**이다(상신).
    """
    # --- 원(raw) AABB 층: **시점 무관**. T3의 원인을 가르는 것이 이 층이다. ------
    #  융합본은 깊이 유래라 단서(=가림막) 제거만으로 새 셀이 보인다. AABB는
    #  하늘에서 쏜 광선이라 프림에만 의존한다. 그래서 "레버가 지면 기하를
    #  건드렸는가"는 AABB로만 정직하게 물을 수 있다 — 단, AABB는 수관·상판을
    #  읽으므로 **위험깊이 문턱**을 걸어 보행면 위의 차이를 걸러 낸다.
    aa = np.load(os.path.join(da, "heightmap.npy")).astype(np.float64)
    ab_ = np.load(os.path.join(db, "heightmap.npy")).astype(np.float64)
    ao = np.load(os.path.join(do, "heightmap.npy")).astype(np.float64)
    fin_ab = np.isfinite(aa) & np.isfinite(ab_)
    dab = np.where(fin_ab, np.abs(aa - ab_), 0.0)
    fpaa = np.isfinite(aa) & np.isfinite(ao) & ((ao - aa) >= HAZ_DEPTH)
    fpab = np.isfinite(ab_) & np.isfinite(ao) & ((ao - ab_) >= HAZ_DEPTH)
    aabb = dict(bytes_equal=bool(np.array_equal(aa, ab_, equal_nan=True)),
                n_cells_diff=int((dab > 0).sum()),
                n_cells_diff_ge_hz=int((dab >= HAZ_DEPTH).sum()),
                max_abs_diff=round(float(dab.max()), 4) if dab.size else 0.0,
                fp_A=int(fpaa.sum()), fp_B=int(fpab.sum()),
                fp_symdiff=int((fpaa ^ fpab).sum()),
                geometry_gt_invariant=bool((dab >= HAZ_DEPTH).sum() == 0
                                           or (fpaa ^ fpab).sum() == 0))

    za, ga, sa = LB.load_heightmap(da)
    zb, gb, sb = LB.load_heightmap(db)
    zo, go, so = LB.load_heightmap(do)
    zb = LB.align_to(zb, gb, ga, za.shape)
    zo = LB.align_to(zo, go, ga, za.shape)
    fin = np.isfinite(za) & np.isfinite(zb)
    d = np.where(fin, np.abs(za - zb), 0.0)
    ge = d >= HAZ_DEPTH
    finA = np.isfinite(za) & np.isfinite(zo)
    finB = np.isfinite(zb) & np.isfinite(zo)
    fpA = finA & ((zo - za) >= HAZ_DEPTH)
    fpB = finB & ((zo - zb) >= HAZ_DEPTH)
    sym = fpA ^ fpB
    out = dict(aabb=aabb,
               instrument=dict(A=sa, B=sb, off=so, matched=(sa == sb)),
               n_cells_diff=int((d > 0).sum()),
               n_cells_diff_ge_hz=int(ge.sum()),
               max_abs_diff=round(float(d.max()), 4) if d.size else 0.0,
               fp_A=int(fpA.sum()), fp_B=int(fpB.sum()),
               fp_symdiff=int(sym.sum()),
               fp_only_A=int((fpA & ~fpB).sum()), fp_only_B=int((fpB & ~fpA).sum()),
               diff_inside_fp_union=int((ge & (fpA | fpB)).sum()),
               void_A=int((~np.isfinite(za)).sum()), void_B=int((~np.isfinite(zb)).sum()))
    if ge.any():
        out["A_z_in_diff_cells"] = [round(float(za[ge].min()), 3),
                                    round(float(za[ge].max()), 3),
                                    round(float(np.median(za[ge])), 3)]
        out["B_z_in_diff_cells"] = [round(float(zb[ge].min()), 3),
                                    round(float(zb[ge].max()), 3),
                                    round(float(np.median(zb[ge])), 3)]
        out["A_above_B_frac"] = round(float(((za - zb)[ge] > 0).mean()), 4)
    return out


def prim_normalized_check(d, cuts, max_groups=1):
    """`마스크 > 포즈`가 무해한지 **프림 경로로 정규화**해 확인한다.

    인스턴스 ID는 어노테이터가 평가할 때마다 새로 매겨진다. 그래서 같은 포즈·같은
    장면인데도 `.idseg.npz` 바이트가 갈린다. 내용이 정말 같은지는 `idToLabels`로
    `id → 프림 경로`를 되돌린 뒤 **경로별 픽셀 수**를 비교해야 안다.

    이 함수의 결과가 곧 **VG-03의 구현 규약**이다 — 계획 §6.1의 VG-03("cue 프림
    픽셀 집합이 A와 동일")을 바이트 해시로 구현하면 같은 장면에서도 불일치가 난다.
    """
    PK = ("d", "h_rel", "yaw", "pitch", "roll", "hfov")
    groups = {}
    for f, c in sorted(cuts.items()):
        cam = c["cam"]
        k = (tuple(round(float(cam[x]), 6) for x in PK) +
             tuple(round(float(x), 6) for x in cam["eye"]))
        groups.setdefault(k, []).append(f)
    out = []
    for g in [v for v in groups.values() if len(v) > 1][:max_groups]:
        per, err = [], None
        for f in g:
            p = os.path.join(d, os.path.splitext(f)[0] + ".idseg.npz")
            if not os.path.isfile(p):
                err = "사이드카 없음"
                break
            try:
                z = np.load(p, allow_pickle=True)
                lab = json.loads(z["idToLabels"].item())
                arr = z["idseg"]
                ids, cnt = np.unique(arr, return_counts=True)
                m = {}
                for i, c_ in zip(ids.tolist(), cnt.tolist()):
                    path = lab.get(str(i), f"<unmapped:{i}>")
                    m[path] = m.get(path, 0) + int(c_)
                per.append(m)
            except Exception as e:
                err = f"{type(e).__name__}: {e}"
                break
        if err:
            out.append(dict(cuts=g, error=err))
            continue
        base = per[0]
        same_paths = all(set(x) == set(base) for x in per[1:])
        same_counts = all(x == base for x in per[1:])
        out.append(dict(cuts=g, n_paths_visible=len(base),
                        prim_path_sets_equal=same_paths,
                        per_prim_pixel_counts_equal=same_counts,
                        n_labels=len(lab)))
    return out


def lever_fired(da, db, ca, cb):
    """레버가 **실제로 발화했는가** — VG-01이 원리적으로 볼 수 없는 실패 모드.

    VG-01은 "A와 B의 위험 GT가 같다"를 요구한다. 그런데 **토글이 아예 안 걸려
    B가 A의 복제본이 되면 VG-01은 만점으로 통과한다.** 그리고 그것이야말로
    D74 ⑤가 s03·s04·s10을 스킵한 이유의 바로 그 해악(학습 이중 가중)이다.
    그래서 반대 방향의 증거를 따로 잰다 — **B는 A와 달라야 한다**, 단 화면에서만.

    세 지표를 같이 본다(하나만 보면 속는다).
      · `n_prims` 델타 — 프림을 지우는 레버(R·N·Sg·V)는 여기서 반드시 움직인다.
      · RGB 델타 — 재질만 바꾸는 레버(T)는 프림 수가 그대로라 **여기서만** 보인다.
      · `idseg_n_ids` 델타 — 프림 삭제의 세그 쪽 확증(A팔에 사이드카가 있을 때만).

    W0가 "토글 발화 39/39"를 잰 것과 같은 종류의 확인이되, 이번에는 **생산
    레시피(여러 레버 동시)** 위에서 잰다.
    """
    try:
        from PIL import Image
    except Exception:
        return dict(error="PIL 없음")
    common = sorted(set(ca) & set(cb))[:6]
    dif, frac = [], []
    for f in common:
        pa, pb = os.path.join(da, f), os.path.join(db, f)
        if not (os.path.isfile(pa) and os.path.isfile(pb)):
            continue
        a = np.asarray(Image.open(pa).convert("RGB"), dtype=np.int16)
        b = np.asarray(Image.open(pb).convert("RGB"), dtype=np.int16)
        if a.shape != b.shape:
            continue
        d = np.abs(a - b)
        dif.append(float(d.mean()))
        frac.append(float((d.max(axis=2) > 2).mean()))
    ma = json.load(open(os.path.join(da, "heightmap_meta.json"), encoding="utf-8"))
    mb = json.load(open(os.path.join(db, "heightmap_meta.json"), encoding="utf-8"))
    npa, npb = ma.get("n_prims"), mb.get("n_prims")
    ida = sorted({c.get("idseg_n_ids") for c in ca.values()
                  if c.get("idseg_n_ids") is not None})
    idb = sorted({c.get("idseg_n_ids") for c in cb.values()
                  if c.get("idseg_n_ids") is not None})
    return dict(n_cuts_sampled=len(dif),
                rgb_mean_abs=round(float(np.mean(dif)), 4) if dif else None,
                rgb_frac_changed=round(float(np.mean(frac)), 5) if frac else None,
                rgb_max_of_means=round(float(max(dif)), 4) if dif else None,
                n_prims=dict(A=npa, B=npb,
                             delta=(None if npa is None or npb is None else npb - npa)),
                idseg_n_ids=dict(A=ida or None, B=idb or None),
                fired=bool((npa is not None and npb is not None and npb != npa)
                           or (dif and max(dif) > 0.05)))


def load_corpus():
    """정본 코퍼스 A 라벨: (round, scene, file+suffix) -> polar_gt."""
    p = os.path.join(V3, "dataset_manifest_v2corr.json")
    out, src = {}, {}
    for f in json.load(open(p, encoding="utf-8"))["frames"]:
        if f["toggle_state"] != "on":
            continue
        out[(f["round"], f["scene_id"], f["frame_id"].split("/")[-1])] = f["polar_gt"]
        src[(f["round"], f["scene_id"])] = f.get("label_source")
    return out, src


def main():
    SEG3 = _seg3_released()
    labA = os.path.join(ANN, f"{TAG}_A.json")
    labB = os.path.join(ANN, f"{TAG}_B.json")
    labAC = os.path.join(ANN, f"{TAG}_Acorpus.json")
    have_labels = os.path.exists(labA) and os.path.exists(labB)
    LA = json.load(open(labA, encoding="utf-8")) if have_labels else None
    LB_ = json.load(open(labB, encoding="utf-8")) if have_labels else None
    LAC = json.load(open(labAC, encoding="utf-8")) if os.path.exists(labAC) else None
    corpus, corpus_src = load_corpus()

    out = dict(doc=f"{TAG}_verify", version="1.0", arm=ARM, b_round=B,
               plan="RENDER_PLAN_V3 §4.2 · §6.1 (VG-01·VG-08·VG-10·VG-datum) · D74",
               gates=["VG-01", "VG-08", "VG-10", "VG-datum"],
               have_labels=have_labels, rounds={}, scenes=[], problems=[])

    # ---------- 1. 렌더 회계 ---------------------------------------------
    total_cuts = total_sec = 0
    for band, (brun, _a, scs) in BANDS.items():
        root = os.path.join(REPO, "dataset", brun)
        png = len(glob.glob(os.path.join(root, "*", "*", "*.png")))
        dep = len(glob.glob(os.path.join(root, "*", "*", "*.depth.npy")))
        segn = len(glob.glob(os.path.join(root, "*", "*", "*.idseg.npz")))
        hm = len(glob.glob(os.path.join(root, "*", "*", "heightmap.npy")))
        sec = 0.0
        for s in scs:
            d = sdir(brun, s)
            if not d:
                out["problems"].append(f"{brun}/{s}: 렌더 없음")
                continue
            cu, var = cuts_of(d)
            sec += float(var.get("sec_per_cut") or 0) * len(cu)
        gb = sum(os.path.getsize(os.path.join(dp, f))
                 for dp, _, fs in os.walk(root) for f in fs) / 2**30 \
            if os.path.isdir(root) else 0.0
        out["rounds"][brun] = dict(band=band, n_scenes=len(scs), png=png, depth=dep,
                                   idseg_files=segn, heightmap=hm,
                                   expected_cuts=24 * len(scs),
                                   in_process_sec=round(sec, 1), disk_gb=round(gb, 3),
                                   vg08_pass=(segn == png == dep == 24 * len(scs)))
        total_cuts += png
        total_sec += sec
    out["accounting"] = dict(
        total_cuts=total_cuts, in_process_gpu_h=round(total_sec / 3600, 4),
        planned_cuts=(648 if ARM == "B" else 576), plan_table_b_arm=816,
        wave=ARM,
        skipped_d74=dict(scenes=SKIPPED_D74, cuts=sum(SKIPPED_D74.values()),
                         why="레버 0 → B ≡ A 바이트 동일 (DECISIONS D74 ⑤)"),
        note="계획 §1.2 표의 B팔 '합(프레임) 792'는 scene06 보류(24컷)를 뺀 값. "
             "D72 ③이 보류를 해제해 분모는 816이고, D74 ⑤ 스킵 168을 빼 648이 예산.")

    # ---------- 2-6. (밴드, 씬)별 -----------------------------------------
    for band, (brun, _arun, scs) in BANDS.items():
        sfx = SUFFIX[band]
        for s in scs:
            db = sdir(brun, s)
            da, arun = a_dir(band, s)
            row = dict(scene=s, band=band, b_round=brun, a_round=arun)
            if not (db and da):
                row["error"] = "missing round dir"
                out["scenes"].append(row)
                out["problems"].append(f"{band}/{s}: 라운드 디렉터리 없음")
                continue
            # --- VG-01 (ㄱ) 바이트층 -------------------------------------
            ha = sha256(os.path.join(da, "heightmap.npy"))
            hb = sha256(os.path.join(db, "heightmap.npy"))
            ma = json.load(open(os.path.join(da, "heightmap_meta.json"), encoding="utf-8"))
            mb = json.load(open(os.path.join(db, "heightmap_meta.json"), encoding="utf-8"))
            geo_same = all(ma.get(k) == mb.get(k) for k in GEO_KEYS)
            geo_diff = {k: [ma.get(k), mb.get(k)] for k in GEO_KEYS
                        if ma.get(k) != mb.get(k)}
            row["vg01_bytes"] = dict(
                hm_sha_A=ha[:16], hm_sha_B=hb[:16], hm_bytes_equal=(ha == hb),
                meta_geo_equal=geo_same, meta_geo_diff=geo_diff,
                n_prims=dict(A=ma.get("n_prims"), B=mb.get("n_prims")),
                arm_config=dict(A=ma.get("arm_config"), B=mb.get("arm_config")),
                fused_A=os.path.isfile(os.path.join(da, "heightmap_fused.npy")),
                fused_B=os.path.isfile(os.path.join(db, "heightmap_fused.npy")))
            fa = os.path.join(da, "heightmap_fused.npy")
            fb = os.path.join(db, "heightmap_fused.npy")
            if os.path.isfile(fa) and os.path.isfile(fb):
                row["vg01_bytes"]["fused_sha_A"] = sha256(fa)[:16]
                row["vg01_bytes"]["fused_sha_B"] = sha256(fb)[:16]
                row["vg01_bytes"]["fused_bytes_equal"] = sha256(fa) == sha256(fb)

            # --- VG-01 진단층: 차이가 위험 GT에 닿는가 --------------------
            dg, grun = gate_off_dir(band, s)
            do_, orun = off_dir(band, s)
            row["gate_off_round"] = grun
            row["off_round"] = orun
            if dg:
                try:
                    row["hm_diff"] = hm_diff(da, db, dg)
                except Exception as e:
                    row["hm_diff"] = dict(error=f"{type(e).__name__}: {e}")
            else:
                row["hm_diff"] = dict(error=f"게이트 z_off(D팔 {grun}) 없음")
            # 진단 병기 — 구off를 z_off로 쓰면 얼마나 유령이 생기는가
            if do_:
                try:
                    gh = hm_diff(da, db, do_)
                    row["hm_diff_guoff_ref"] = {k: gh[k] for k in
                                                ("fp_A", "fp_B", "fp_symdiff",
                                                 "fp_only_A", "fp_only_B")}
                except Exception as e:
                    row["hm_diff_guoff_ref"] = dict(error=f"{type(e).__name__}: {e}")

            # --- VG-datum + VG-10 ---------------------------------------
            ca, _ = cuts_of(da)
            cb, vb = cuts_of(db)
            row["datum"] = datum_pose(ca, cb)

            # --- 레버 발화 (VG-01의 맹점 반대편) --------------------------
            try:
                row["lever"] = lever_fired(da, db, ca, cb)
            except Exception as e:
                row["lever"] = dict(error=f"{type(e).__name__}: {e}")
            row["lever"]["levers"] = sorted(
                k.replace("cue_", "") for k, v in
                json.load(open(os.path.join(V3, "render_configs_v3",
                                            f"{s}_{ARM}.json"), encoding="utf-8")).items()
                if v is False)
            if row["lever"].get("fired") is False:
                out["problems"].append(
                    f"{band}/{s}: **레버 미발화** — B가 A의 복제본이다. "
                    f"D74 ⑤가 스킵한 것과 같은 학습 이중 가중 해악.")

            # --- VG-08 per-cut 판별성 ------------------------------------
            row["seg"] = seg_audit(db, cb)
            if row["seg"]["over_discriminating"]:
                # 무해함을 프림 경로 정규화로 실증한다 (VG-03 구현 규약의 근거)
                row["seg"]["prim_normalized"] = prim_normalized_check(db, cb)
            if not row["seg"]["distinct"]:
                out["problems"].append(
                    f"{band}/{s}: per-cut ID 마스크 판별성 실패 — "
                    f"{row['seg']['n_unique_masks']}/{row['seg']['n_cuts']} 고유")

            # --- VG-01 (ㄴ)(ㄷ) 라벨러층 ----------------------------------
            if have_labels:
                sa = next((x for x in LA["scene_footprint"]
                           if x["scene"] == s and x.get("band") == band), None)
                sb = next((x for x in LB_["scene_footprint"]
                           if x["scene"] == s and x.get("band") == band), None)
                if sa is None or sb is None or "error" in (sa or {}) or "error" in (sb or {}):
                    row["vg01_labeler"] = dict(error="라벨 레코드 없음/오류",
                                               a=sa, b=sb)
                else:
                    keys = sorted(k for k in LB_["frames"]
                                  if k.startswith(f"on/{s}/") and
                                  (k.endswith(sfx) if sfx else "::" not in k))
                    nfr, ngt, npre, ngate = 0, 0, 0, 0
                    bad = []
                    for k in keys:
                        fa_ = LA["frames"].get(k)
                        fb_ = LB_["frames"].get(k)
                        if fa_ is None:
                            bad.append(dict(frame=k, why="A 라벨 없음"))
                            continue
                        nfr += 1
                        gt_ok = fa_["polar_gt"] == fb_["polar_gt"]
                        pr_ok = fa_["polar_gt_pregate"] == fb_["polar_gt_pregate"]
                        ge_ok = fa_["gate_excluded"]["cells"] == fb_["gate_excluded"]["cells"]
                        ngt += gt_ok
                        npre += pr_ok
                        ngate += ge_ok
                        if not (gt_ok and pr_ok):
                            bad.append(dict(frame=k,
                                            A_gt=fa_["polar_gt"], B_gt=fb_["polar_gt"],
                                            A_pre=fa_["polar_gt_pregate"],
                                            B_pre=fb_["polar_gt_pregate"]))
                    row["vg01_labeler"] = dict(
                        cells_raw=dict(A=sa["cells_raw"], B=sb["cells_raw"],
                                       equal=(sa["cells_raw"] == sb["cells_raw"]),
                                       delta=sb["cells_raw"] - sa["cells_raw"]),
                        max_diff=dict(A=sa.get("max_diff"), B=sb.get("max_diff")),
                        hm_source=dict(A=sa.get("hm_source"), B=sb.get("hm_source"),
                                       off_A=sa.get("hm_source_off"),
                                       off_B=sb.get("hm_source_off"),
                                       matched=(sa.get("hm_source") == sb.get("hm_source")
                                                and sa.get("hm_source_off") == sb.get("hm_source_off"))),
                        void=dict(A=sa.get("void_total"), B=sb.get("void_total"),
                                  equal=(sa.get("void_total") == sb.get("void_total"))),
                        n_frames=nfr, polar_gt_equal=ngt,
                        polar_gt_pregate_equal=npre, gate_excluded_equal=ngate,
                        all_frames_equal=(nfr > 0 and ngt == nfr and npre == nfr),
                        mismatches=bad[:6], n_mismatch=len(bad))

                # --- 코퍼스 이전 대조 (freshA vs v2corr) -------------------
                cr = A_OVERLAY.get((band, s))
                corp_round = BANDS[band][1]         # v2corr는 평 라운드 이름을 쓴다
                n_c, n_eq, miss = 0, 0, 0
                src = LAC or LA           # 코퍼스 규약(구off) 라벨이 있으면 그것으로
                for k in sorted(k for k in src["frames"]
                                if k.startswith(f"on/{s}/") and
                                (k.endswith(sfx) if sfx else "::" not in k)):
                    fn = k.split("/")[-1]
                    g = corpus.get((corp_round, s, fn))
                    if g is None:
                        miss += 1
                        continue
                    n_c += 1
                    n_eq += (g == src["frames"][k]["polar_gt"])
                row["corpus_tie"] = dict(
                    corpus_round=corp_round, a_overlay=cr,
                    label_used=("w1b_Acorpus(구off 기준)" if LAC else
                                "w1b_A(D팔 기준 — 규약 불일치, 참고치)"),
                    label_source=corpus_src.get((corp_round, s)),
                    n_compared=n_c, n_equal=n_eq, n_missing_in_corpus=miss,
                    reproduces=(n_c > 0 and n_eq == n_c))
                if n_c and n_eq != n_c:
                    out["problems"].append(
                        f"{band}/{s}: 재라벨 A가 코퍼스 polar_gt를 {n_eq}/{n_c}만 재현 "
                        f"— 이 씬의 VG-01은 '내 파이프라인 기준'으로 읽어야 한다")

            # --- 종합 판정 ------------------------------------------------
            v = row.get("vg01_labeler") or {}
            byte_ok = bool(row["vg01_bytes"]["hm_bytes_equal"]
                           and row["vg01_bytes"]["meta_geo_equal"])
            hd = row.get("hm_diff") or {}
            gt_ok_hm = ("error" not in hd) and hd.get("fp_symdiff") == 0
            geo_inv = bool((hd.get("aabb") or {}).get("geometry_gt_invariant"))
            if not have_labels:
                # 라벨러층 없이 PASS를 찍지 않는다 — 바이트층만으로는 게이트가 반쪽이다.
                row["vg01_tier"] = None
                row["vg01_pass"] = None
                row["vg01_state"] = "PENDING(라벨 미착지) · 바이트 " + \
                                    ("OK" if byte_ok else "FAIL") + " · fp대칭차 " + \
                                    str(hd.get("fp_symdiff"))
            else:
                # 계획 §6.1은 두 절을 함께 건다 — `cells_raw` 동일 **그리고**
                # `polar_gt` 비트 동일. 둘은 다른 것을 잰다:
                #   cells_raw = 씬 전역 높이맵 발자국 (격자 103,041셀)
                #   polar_gt  = **실제 훈련 라벨** (컷별 폴라 20칸)
                # 발자국이 폴라 격자 밖이나 칸 판정을 안 바꾸는 자리에서만 갈리면
                # cells_raw는 달라도 polar_gt는 비트 동일할 수 있다. 그 경우를
                # 눈에 보이게 따로 기록한다 — 판정은 보수적으로 두되(격리),
                # "훈련 라벨은 불변"이라는 사실을 보고서가 인용할 수 있게.
                cells_ok = bool((v.get("cells_raw", {}) or {}).get("equal"))
                gt_ok = bool(v.get("all_frames_equal"))
                row["training_gt_identical"] = gt_ok
                row["scene_footprint_identical"] = cells_ok
                lab_ok = cells_ok and gt_ok
                # T3의 원인을 가른다 — 처방이 다르기 때문이다.
                #   AABB 높이맵은 **기하 유래**(하늘에서 쏜 광선) → 프림에만 의존.
                #   융합 높이맵은 **깊이 유래** → 무엇이 보이는가에 의존하므로,
                #   단서 프림을 지우면 지면이 같아도 가려졌던 자리가 새로 채워진다.
                # 그래서 "AABB는 바이트 동일한데 라벨이 갈린다"면 기하는 불변이고
                # 갈린 것은 **계기의 시점 의존성**이다 — 레버 문제가 아니다.
                if byte_ok and lab_ok:
                    tier = "T1"          # 높이맵 바이트 동일 + GT 동일 — 구성적 보증
                elif lab_ok and gt_ok_hm:
                    tier = "T2"          # 바이트는 갈리나 GT 불변 (보행면 위 / 서브밀리)
                elif geo_inv:
                    # 원 AABB(시점 무관)에서 위험깊이 이상 차이가 0셀이거나 발자국
                    # 대칭차가 0 = 지면 기하는 GT 규모로 불변. 갈린 것은 융합 계기다.
                    tier = "T3-instr"
                else:
                    tier = "T3-geom"     # 기하가 GT 안에서 움직였다 = 레버가 구조물
                row["vg01_tier"] = tier
                row["vg01_pass"] = tier in ("T1", "T2")
                row["vg01_state"] = tier + ("" if row["vg01_pass"] else " → 격리")
                # --- T2-seg: 판정은 그대로, 자격만 추가로 계산·인쇄 (D90 ①) ---
                t2s = t2seg_verdict(s, hd, gt_ok, cells_ok, SEG3)
                if t2s is not None:
                    row["vg01_t2seg"] = t2s
                    row["vg01_pass_seg3"] = bool(row["vg01_pass"] or t2s["eligible"])
                else:
                    row["vg01_pass_seg3"] = row["vg01_pass"]
            if have_labels and row["vg01_pass"] is False:
                rx = ("계획 §7.4: 실패한 키만 금지 + 남은 키로 씬당 1회 재렌더"
                      if row["vg01_tier"] == "T3-geom" else
                      "원 AABB는 GT 규모로 불변 — 레버가 아니라 **융합 계기의 시점 "
                      "의존성**이 원인. 처방은 레버 변경이 아니라 쌍의 GT 계기 확정 "
                      "(상신 대상)")
                out["problems"].append(
                    f"{band}/{s}: **VG-01 {row['vg01_tier']} 실패** — B팔 격리. {rx}")
            out["scenes"].append(row)

    # ---------- 집계 -------------------------------------------------------
    sc = [r for r in out["scenes"] if "vg01_bytes" in r]
    q = [dict(scene=r["scene"], band=r["band"],
              hm_bytes_equal=r["vg01_bytes"]["hm_bytes_equal"],
              cells_raw=(r.get("vg01_labeler") or {}).get("cells_raw"),
              n_mismatch=(r.get("vg01_labeler") or {}).get("n_mismatch"))
         for r in sc if r.get("vg01_pass") is False]
    out["vg_01"] = dict(
        n_pairs=len(sc), n_pass=sum(1 for r in sc if r.get("vg01_pass")),
        n_pending=sum(1 for r in sc if r.get("vg01_pass") is None),
        tiers={t: sum(1 for r in sc if r.get("vg01_tier") == t)
               for t in ("T1", "T2", "T3-instr", "T3-geom")},
        tier_legend=dict(
            T1="높이맵 바이트 동일 — 레버가 GT를 건드릴 수 없음(구성적 보증)",
            T2="바이트는 갈리나 fp 대칭차 0 · cells_raw·polar_gt 동일 — "
               "차이가 보행면 **위**에만 있음(AABB가 제거된 수관/상판을 읽던 자리)",
            **{"T3-instr": "원 AABB(시점 무관)에서 위험깊이 이상 차이 0셀 또는 발자국 "
                           "대칭차 0 = 지면 기하가 GT 규모로 불변인데 라벨이 갈림 — "
                           "**융합(깊이) 계기의 시점 의존성**이 원인. 처방은 레버 "
                           "변경이 아니라 쌍의 GT 계기 확정",
               "T3-geom": "AABB 기하가 위험 GT 안에서 움직임 — 그 레버는 구조물. "
                          "계획 §7.4: 그 키만 금지 + 남은 키로 재렌더"}),
        plan_text_note=("계획 §6.1 VG-01 문면의 `heightmap_meta.json 바이트 동일`은 "
                        "**어떤 B팔에서도 만족 불가능**하다 — `arm_config`가 정의상 "
                        "다르기 때문이다. 실질 조건은 `cells_raw`·`polar_gt` 두 절이며 "
                        "본 판정은 그 둘을 조작적 기준으로 삼고, 바이트 동일은 "
                        "더 강한 충분조건(T1)으로 별도 인쇄한다. 계획 문면 정정 대상."),
        n_hm_bytes_equal=sum(1 for r in sc if r["vg01_bytes"]["hm_bytes_equal"]),
        n_meta_geo_equal=sum(1 for r in sc if r["vg01_bytes"]["meta_geo_equal"]),
        n_frames=sum((r.get("vg01_labeler") or {}).get("n_frames", 0) for r in sc),
        n_frames_gt_equal=sum((r.get("vg01_labeler") or {}).get("polar_gt_equal", 0)
                              for r in sc),
        n_training_gt_identical=sum(1 for r in sc if r.get("training_gt_identical")),
        n_scene_footprint_identical=sum(1 for r in sc
                                        if r.get("scene_footprint_identical")),
        gt_only_pass=[dict(scene=r["scene"], band=r["band"], tier=r.get("vg01_tier"),
                           cells_raw=(r.get("vg01_labeler") or {}).get("cells_raw"))
                      for r in sc if r.get("training_gt_identical")
                      and r.get("scene_footprint_identical") is False],
        quarantine=q,
        n_pass_seg3=sum(1 for r in sc if r.get("vg01_pass_seg3")),
        t2seg_eligible=[dict(scene=r["scene"], band=r["band"],
                             tier=r.get("vg01_tier"), **r["vg01_t2seg"])
                        for r in sc if (r.get("vg01_t2seg") or {}).get("eligible")],
        quarantine_if_seg3_admitted=[
            dict(scene=r["scene"], band=r["band"]) for r in sc
            if r.get("vg01_pass_seg3") is False],
        seg3_note="T2-seg 는 **판정을 바꾸지 않는다** — `quarantine` 은 종전 의미 그대로다. "
                  "`quarantine_if_seg3_admitted` 는 D90 ① 결재 시의 목록이며 "
                  "`build_corpus_v3.py --admit-seg3` 가 그것을 읽는다.",
        note="바이트층은 계기와 무관한 구성적 진술이다. 라벨러층은 그 위에 "
             "정본 GT 산술을 얹은 것 — 둘 다 통과해야 PASS.")
    out["corpus_tie"] = dict(
        n_pairs=sum(1 for r in sc if r.get("corpus_tie")),
        n_reproduce=sum(1 for r in sc if (r.get("corpus_tie") or {}).get("reproduces")),
        deviating=[dict(scene=r["scene"], band=r["band"], **r["corpus_tie"])
                   for r in sc if r.get("corpus_tie")
                   and not r["corpus_tie"]["reproduces"]])
    dat = [r for r in sc if "datum" in r]
    tiers = dict(datum_exact=0, datum_tol=0, datum_fail=0)
    for r in dat:
        for k in tiers:
            tiers[k] += r["datum"]["tiers"][k]
    quarantine = sorted({(r["scene"], r["band"]) for r in dat
                         if r["datum"]["verdict"] == "datum_fail"})
    out["vg_datum"] = dict(
        n_pairs=len(dat), cut_tiers=tiers,
        n_cuts=sum(r["datum"]["n_cuts"] for r in dat),
        pair_survival=f"{len(dat) - len(quarantine)}/{len(dat)}",
        pair_survival_rate=round(1 - len(quarantine) / max(len(dat), 1), 4),
        cut_survival=f"{tiers['datum_exact'] + tiers['datum_tol']}/{sum(tiers.values())}",
        quarantine=[dict(scene=s_, band=b_) for s_, b_ in quarantine],
        drift=[dict(scene=r["scene"], band=r["band"],
                    ground_z_drift_max=r["datum"]["ground_z_drift_max"],
                    tiers=r["datum"]["tiers"], verdict=r["datum"]["verdict"],
                    n_fail_cuts=r["datum"]["n_fail_cuts"],
                    fail_cuts=r["datum"]["fail_cuts"])
               for r in dat if r["datum"]["verdict"] != "datum_exact"])
    out["vg_10"] = dict(
        pose_delta_max=max((r["datum"]["pose_delta_max"] for r in dat), default=None),
        n_pairs_nonzero=sum(1 for r in dat if r["datum"]["pose_delta_max"] > 0),
        nonzero=[dict(scene=r["scene"], band=r["band"],
                      pose_delta_max=r["datum"]["pose_delta_max"])
                 for r in dat if r["datum"]["pose_delta_max"] > 0])
    lv_ = [r for r in sc if "lever" in r and "error" not in r["lever"]]
    out["lever_firing"] = dict(
        note="VG-01은 '토글이 아예 안 걸려 B가 A의 복제본'인 실패를 만점으로 "
             "통과시킨다. 반대 방향 증거를 따로 잰다 — 프림 수 델타 · RGB 델타 · "
             "idseg n_ids 델타.",
        n_pairs=len(lv_), n_fired=sum(1 for r in lv_ if r["lever"]["fired"]),
        not_fired=[dict(scene=r["scene"], band=r["band"], **r["lever"])
                   for r in lv_ if not r["lever"]["fired"]],
        rows=[dict(scene=r["scene"], band=r["band"],
                   levers=r["lever"].get("levers"),
                   d_prims=r["lever"]["n_prims"]["delta"],
                   rgb_mean_abs=r["lever"]["rgb_mean_abs"],
                   rgb_frac_changed=r["lever"]["rgb_frac_changed"])
              for r in lv_])

    sg = [r for r in sc if "seg" in r]
    out["vg_08"] = dict(
        n_pairs=len(sg), n_distinct=sum(1 for r in sg if r["seg"]["distinct"]),
        n_cuts=sum(r["seg"]["n_cuts"] for r in sg),
        n_unique_masks=sum(r["seg"]["n_unique_masks"] for r in sg),
        n_missing_sidecars=sum(r["seg"]["missing"] for r in sg),
        n_poses=sum(r["seg"]["n_poses"] for r in sg),
        n_stale_signature=sum(1 for r in sg if r["seg"]["stale_signature"]),
        n_pose_collisions=sum(r["seg"]["n_pose_collisions"] for r in sg),
        n_light_dependent=sum(r["seg"]["n_light_dependent_poses"] for r in sg),
        n_over_discriminating=sum(1 for r in sg if r["seg"]["over_discriminating"]),
        predicate="판정(hard) = 포즈 간 충돌 0 이고 고유 마스크 수 ≥ 고유 포즈 수. "
                  "조건은 조명만 바꾸므로 같은 포즈의 컷은 마스크가 같은 것이 정상이고, "
                  "**다른 포즈가 같은 마스크를 쓰면** stale이다. "
                  "관찰(soft) = 마스크 > 포즈 (조건이 프림 집합을 건드림 / "
                  "치환 조건이 별도 프로세스라 인스턴스 ID가 재부여됨)",
        over_discriminating=[dict(scene=r["scene"], band=r["band"],
                                  n_unique_masks=r["seg"]["n_unique_masks"],
                                  n_poses=r["seg"]["n_poses"],
                                  n_light_dependent_poses=r["seg"]["n_light_dependent_poses"],
                                  prim_normalized=r["seg"].get("prim_normalized"))
                             for r in sg if r["seg"]["over_discriminating"]],
        prim_normalization_verdict=(
            "인스턴스 ID는 평가마다 재번호된다. `마스크 > 포즈`인 단위를 프림 경로로 "
            "정규화해 확인한 결과 경로 집합과 경로별 픽셀 수가 전부 동일하면 무해하다. "
            "**VG-03은 바이트 해시가 아니라 이 정규화로 구현해야 한다.**"),
        fetch_paths=sorted({f for r in sg for f in r["seg"]["fetch"]}),
        n_ids_range=[min((min(r["seg"]["n_ids_distinct"]) for r in sg
                          if r["seg"]["n_ids_distinct"]), default=None),
                     max((max(r["seg"]["n_ids_distinct"]) for r in sg
                          if r["seg"]["n_ids_distinct"]), default=None)],
        failures=[dict(scene=r["scene"], band=r["band"], **r["seg"])
                  for r in sg if not r["seg"]["distinct"]])

    op = os.path.join(V3, f"{TAG}_verify.json")
    json.dump(out, open(op, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # ---------- stdout -----------------------------------------------------
    print("=== 렌더 회계 ===")
    for r, v in out["rounds"].items():
        print(f"  {r:26s} {v['png']:4d}/{v['expected_cuts']:4d} png · depth {v['depth']:4d} "
              f"· idseg {v['idseg_files']:4d} · hm {v['heightmap']:2d} · {v['disk_gb']:6.2f} GB "
              f"· VG-08 {'PASS' if v['vg08_pass'] else 'FAIL'}")
    a = out["accounting"]
    print(f"  합계 {a['total_cuts']}컷 / 예산 {a['planned_cuts']}컷 · in-process "
          f"{a['in_process_gpu_h']} GPU-h")
    print(f"  **D74 ⑤ 스킵 {a['skipped_d74']['cuts']}컷** — {a['skipped_d74']['scenes']} "
          f"({a['skipped_d74']['why']})")

    print("\n=== VG-01 A/B 위험-GT 동일성 (중심 게이트) ===")
    v1 = out["vg_01"]
    print(f"  {v1['n_pass']}/{v1['n_pairs']} 씬×밴드 PASS (보류 {v1['n_pending']}) "
          f"· 층 {v1['tiers']} · 높이맵 바이트 동일 "
          f"{v1['n_hm_bytes_equal']}/{v1['n_pairs']} · 메타 기하 동일 "
          f"{v1['n_meta_geo_equal']}/{v1['n_pairs']} · polar_gt 동일 프레임 "
          f"{v1['n_frames_gt_equal']}/{v1['n_frames']}")
    hdr = (f"  {'band':5s} {'scene':9s} {'hm바이트':8s} {'hm차≥0.3':>9s} {'fp대칭차':>9s} "
           f"{'AABB≥hz':>8s} {'cells_raw A':>12s} {'B':>10s} {'Δ':>7s} {'gt동일':>9s} {'계기':>11s}  판정")
    print(hdr)
    for r in sc:
        lv = r.get("vg01_labeler") or {}
        cr = lv.get("cells_raw") or {}
        hd = r.get("hm_diff") or {}
        print(f"  {r['band']:5s} {r['scene']:9s} "
              f"{str(r['vg01_bytes']['hm_bytes_equal']):8s} "
              f"{str(hd.get('n_cells_diff_ge_hz')):>9s} {str(hd.get('fp_symdiff')):>9s} "
              f"{str((hd.get('aabb') or {}).get('n_cells_diff_ge_hz')):>8s} "
              f"{str(cr.get('A')):>12s} {str(cr.get('B')):>10s} "
              f"{str(cr.get('delta')):>7s} "
              f"{str(lv.get('polar_gt_equal')) + '/' + str(lv.get('n_frames')):>9s} "
              f"{str((lv.get('hm_source') or {}).get('A')) + '/' + str((lv.get('hm_source') or {}).get('B')):>11s}  "
              f"{r.get('vg01_state')}")
    for t, why in v1["tier_legend"].items():
        print(f"    {t} ({v1['tiers'][t]}): {why}")
    print(f"    훈련 라벨(polar_gt) 비트 동일 씬×밴드 {v1['n_training_gt_identical']}/"
          f"{v1['n_pairs']} · 씬 전역 발자국(cells_raw) 동일 "
          f"{v1['n_scene_footprint_identical']}/{v1['n_pairs']}")
    for g in v1["gt_only_pass"]:
        print(f"    [주의] {g['scene']} {g['band']} {g['tier']} — cells_raw는 갈리나 "
              f"(A {g['cells_raw']['A']} / B {g['cells_raw']['B']}) "
              f"**polar_gt는 전 프레임 비트 동일**")
    if v1["quarantine"]:
        print("  격리:", v1["quarantine"])
    else:
        print("  격리: 없음")

    print("\n=== 코퍼스 이전 대조 (구off 기준 A 재라벨 vs dataset_manifest_v2corr) ===")
    ct = out["corpus_tie"]
    print(f"  {ct['n_reproduce']}/{ct['n_pairs']} 씬×밴드에서 polar_gt 완전 재현")
    for d_ in ct["deviating"]:
        print("   ", d_["scene"], d_["band"], f"{d_['n_equal']}/{d_['n_compared']}",
              "label_source:", d_["label_source"], "missing:", d_["n_missing_in_corpus"])

    print("\n=== VG-datum (A,B) 3층 ===")
    print(" ", out["vg_datum"]["cut_tiers"], "· 쌍 생존", out["vg_datum"]["pair_survival"],
          "· 컷 생존", out["vg_datum"]["cut_survival"])
    for d_ in out["vg_datum"]["drift"]:
        print("   ", d_["scene"], d_["band"], d_["verdict"],
              d_["ground_z_drift_max"], d_["tiers"], f"fail컷 {d_['n_fail_cuts']}")
    print("  격리:", out["vg_datum"]["quarantine"] or "없음")

    print("\n=== VG-10 (포즈) ===")
    print("  max pose delta", out["vg_10"]["pose_delta_max"],
          "· 0 아닌 쌍", out["vg_10"]["n_pairs_nonzero"], out["vg_10"]["nonzero"][:4])

    print("\n=== 레버 발화 (VG-01 맹점의 반대편) ===")
    lf = out["lever_firing"]
    print(f"  {lf['n_fired']}/{lf['n_pairs']} 씬×밴드에서 레버 발화 실증")
    print(f"  {'band':5s} {'scene':9s} {'레버':34s} {'Δprims':>7s} {'RGB|Δ|':>8s} {'변화픽셀':>9s}")
    for r in lf["rows"]:
        print(f"  {r['band']:5s} {r['scene']:9s} {','.join(r['levers'] or []):34s} "
              f"{str(r['d_prims']):>7s} {str(r['rgb_mean_abs']):>8s} "
              f"{str(r['rgb_frac_changed']):>9s}")
    if lf["not_fired"]:
        print("  **미발화**:", [(x["scene"], x["band"]) for x in lf["not_fired"]])

    print("\n=== VG-08 · per-cut 세그 판별성 (D74 ④ per-cut 절) ===")
    v8 = out["vg_08"]
    print(f"  {v8['n_distinct']}/{v8['n_pairs']} 씬×밴드 통과 · 고유 마스크 "
          f"{v8['n_unique_masks']} / 고유 포즈 {v8['n_poses']} / 컷 {v8['n_cuts']} "
          f"· 누락 사이드카 {v8['n_missing_sidecars']} · stale 지문 "
          f"{v8['n_stale_signature']} · 포즈충돌 {v8['n_pose_collisions']} · "
          f"조명의존 {v8['n_light_dependent']} · 과판별 씬×밴드 "
          f"{v8['n_over_discriminating']} · fetch {v8['fetch_paths']} · "
          f"n_ids 범위 {v8['n_ids_range']}")
    print(f"  술어: {v8['predicate']}")
    for o_ in v8["over_discriminating"]:
        pn = (o_.get("prim_normalized") or [{}])[0]
        print(f"   [관찰] {o_['scene']} {o_['band']} 마스크 {o_['n_unique_masks']} > "
              f"포즈 {o_['n_poses']} (조명의존 포즈 {o_['n_light_dependent_poses']}) "
              f"· 프림경로 정규화: 경로집합 동일 {pn.get('prim_path_sets_equal')} · "
              f"경로별 픽셀수 동일 {pn.get('per_prim_pixel_counts_equal')} "
              f"(가시 경로 {pn.get('n_paths_visible')})")
    for f_ in v8["failures"]:
        print("   FAIL", f_["scene"], f_["band"], f_["n_unique_masks"], "마스크 /",
              f_["n_poses"], "포즈 /", f_["n_cuts"], "컷", f_["fetch"],
              "stale" if f_["stale_signature"] else "", f_["collide_examples"])

    if out["problems"]:
        print("\nPROBLEMS:")
        for p_ in out["problems"]:
            print("  -", p_)
    print(f"\n-> {op}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
