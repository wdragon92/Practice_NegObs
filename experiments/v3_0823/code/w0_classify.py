#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w0_classify.py — W0 구조물/장식 분류 (VG-CLS) + VG-datum 사전검사.

RENDER_PLAN_V3 §4.2 (W0 프로브) · §6.1 (VG-01 / VG-CLS / VG-datum) · §1.2 (B팔 레버).

무엇을 비교하나
---------------
(씬 × cue_*) 쌍마다 hazard=ON 아래 cue ON(A팔) / cue OFF(Bx팔) 두 렌더를 놓고

  1. `heightmap.npy`   — sha256 · 셀별 |Δz| · 변화 셀 수 · void 이동 · `n_prims`
  2. 라벨러 `cells_raw` — 낙차 발자국 셀 수. 두 팔 모두 같은 반사실면
                          (`260819_main_off`, 같은 시드)을 z_off로 쓰므로
                          Δcells_raw는 오직 그 팔의 높이맵 차이에서만 온다
  3. `polar_gt`        — 판정 프레임(컷 4장) 위 비트 동일성
  4. `cam.ground_z`    — VG-datum 사전검사 (드레싱 제거가 데이텀을 미는가)
  5. RGB 평균 |Δ|      — 토글이 화면에서 아무 일도 하지 않았는지(무효 토글) 검사

판정 규칙 — 결과를 보기 전에 못 박는다 (사후 선택 금지, ACCOUNTING §2-6)
------------------------------------------------------------------------
R1 **구조물** (토글 금지):  Δcells_raw ≠ 0  **또는**  polar_gt가 한 프레임이라도 다름.
   → 그 cue 제거는 낙차 기하를 바꾼다. B팔 레버로 쓰면 A/B 위험-GT 동일성(VG-01)이 깨진다.
R2 **장식** (B팔 레버 확정):  Δcells_raw = 0  **그리고**  polar_gt 4/4 동일.
   · `장식(완전)`   heightmap sha256까지 동일 = VG-01 엄격 통과.
   · `장식(지형외)` 높이맵은 움직였으나 낙차 발자국 밖 = 발자국·GT 불변.
      (전례: scene12 `cue_railing` 54셀·5 mm·발자국 0셀 → 장식 — CUE_COVERAGE §4-2)
R3 **판정불가**: (a) 한쪽 팔의 렌더/라벨이 없음, 또는
   (b) **무효 토글** — heightmap sha 동일 ∧ n_prims 동일 ∧ RGB 평균|Δ| < 0.05 LSB.
      키가 아무것도 건드리지 않았다는 뜻이므로 이 쌍은 증거를 갖지 않는다.
R4 **VG-datum** (컷별, 파일명 일치 쌍):
   `datum_exact` |Δground_z| < 1e-6 · `datum_tol` ≤ 0.02 m · `datum_fail` > 0.02 m.
   datum_fail 컷이 1개라도 있으면 그 쌍은 **데이텀 이동 쌍**으로 등재한다.

dz_max·변화 셀 수는 **증거이자 크기**로 인쇄하되 판정 기준으로 쓰지 않는다.
지면 위에 선 볼라드(1 m)를 지우면 |Δz| = 1 m이 나오지만 낙차 발자국은 그대로다 —
크기를 기준으로 삼으면 그런 장식이 전부 구조물로 오분류된다. 계획이 묻는 것은
"낙차 기하가 바뀌는가"이고 그 기계 술어가 (발자국, polar_gt)다.

사용:  python3 experiments/v3_0823/code/w0_classify.py
산출:  experiments/v3_0823/w0_cuecls.json  (+ stdout 표)

W1-D 재판정 확장 (2026-08-23 · DECISIONS D72 ② · W0_CUECLS §8)
--------------------------------------------------------------
W0의 판정불가 16쌍은 **참조 z_off가 cue-비대칭**이라서 생겼다. 그 참조를
cue-대칭인 **D팔**로 갈아 끼우면 같은 사전등록 규칙으로 다시 판정할 수 있다.
아래 세 인자만 추가했고 **기본값은 W0 그대로**라, 인자 없이 실행하면
`w0_cuecls.json`을 바이트 동등하게 재현한다(사후 규칙 변경 없음).

  --zoff-round   낙차 발자국 z_off 라운드            (기본 260819_main_off)
  --ann-prefix   annotations/<prefix><arm>.json      (기본 w0_)
  --out          산출 JSON                            (기본 w0_cuecls.json)
  --hm-loader    검정 2의 높이맵 계기                (기본 aabb = W0 원본 동작)

`--hm-loader`가 왜 필요한가 — W0에 있던 계기 불일치
----------------------------------------------------
검정 1(`cells_raw`)은 정본 라벨러가 계산하므로 `heightmap_fused.npy`가 있으면
그것을 쓴다(`labeler.load_heightmap`). 그런데 W0의 검정 2(`fp_mask`/`cue_locus`)는
`heightmap.npy`를 **날것으로** 읽었다. 정본 구off에 융합본이 있는 씬
(scene02·scene07·scene08·scene12·scene16)에서 두 검정이 **서로 다른 면을 참조**한
셈이고, 그런 씬에서는 AABB 차분이 0에 가까워 fp_A가 붕괴해 `fp∩ = 0`이
자동으로 나온다 — 즉 검정 2가 **공허하게 "장식"** 을 찍는다.
`--hm-loader labeler`가 이것을 라벨러와 같은 계기로 맞춘다. 기본값을 `aabb`로
둔 것은 인자 없이 실행하면 `w0_cuecls.json`이 그대로 재현되어야 하기 때문이다.

재판정 실행:
  python3 .../w0_classify.py --zoff-round 260826_v3w1_lib_D \
      --ann-prefix w1d_zoffD_ --hm-loader labeler \
      --out experiments/v3_0823/w1d_cuecls.json
"""
import argparse
import glob
import hashlib
import json
import os
import sys

import numpy as np

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V3 = os.path.join(REPO, "experiments/v3_0823")
ANN = os.path.join(V3, "annotations")
STAMP = "260825_v3w0_cuecls"
PLAN = os.path.join(V3, "render_plan_v3.json")

# --- 갈아 끼울 수 있는 부분 (기본값 = W0 원본 동작) --------------------------
ZOFF_ROUND = "260819_main_off"      # 낙차 발자국의 반사실면
ANN_PREFIX = "w0_"                  # annotations/<prefix><arm>.json
OUT_PATH = os.path.join(V3, "w0_cuecls.json")
HM_LOADER = "aabb"                  # 검정 2의 높이맵 계기: aabb | labeler

ARM_OF_CUE = {
    "cue_railing": "Brail",
    "cue_nosing": "Bnose",
    "cue_tactile": "Btact",
    "cue_material_break": "Bmatl",
    "cue_scene_dressing": "Bdress",
}
CUE_SHORT = {"cue_railing": "R", "cue_nosing": "N", "cue_tactile": "Ta",
             "cue_material_break": "T", "cue_sign": "Sg",
             "cue_scene_dressing": "V"}
DATUM_EXACT = 1e-6
DATUM_TOL = 0.02
NOOP_RGB_LSB = 0.05
POSE_KEYS = ("d", "h_rel", "yaw", "pitch", "roll", "hfov")

# 이미 판정된 쌍 (CUE_COVERAGE §4-2 "이미 판정 끝난 4건") — 렌더하지 않고 승계한다.
PRIOR = [
    dict(scene="scene12", cue="cue_railing", verdict="장식",
         source="CUE_COVERAGE §4-2 (P-3 실측)",
         note="heightmap 54셀 · 최대 5 mm · 풋프린트 0셀 · polar_gt 24/24 동일"),
    dict(scene="scene12", cue="cue_scene_dressing", verdict="장식",
         source="CUE_COVERAGE §4-2 (P-3 실측)",
         note="14,467셀 · 최대 5 mm · 풋프린트 0셀 · polar_gt 24/24 동일"),
    dict(scene="scene17", cue="cue_scene_dressing", verdict="장식",
         source="CUE_COVERAGE §4-2 (P-3 실측)",
         note="heightmap sha256 동일 · 0셀 · polar_gt 24/24 동일"),
    dict(scene="scene17", cue="cue_material_break", verdict="장식",
         source="CUE_COVERAGE §4-2 (P-3 실측)",
         note="scene17 `cue_scene_dressing` + `cue_material_break` 동시 = 장식(완전)"),
    dict(scene="scene20", cue="cue_railing", verdict="구조물",
         source="CUE_COVERAGE §4-2 (P-3 실측)",
         note="치크월 12,656셀 · 최대 3.160 m · 풋프린트 +1,302셀 · polar_gt 6/27 상이"),
]


def load_bonds():
    """(scene, cue) -> 결속: HZ(위험 분기 안) · free(자유) · hz?(혼합) · ABSENT.

    참조로 쓰는 `260819_main_off`는 `hazard_*: false`뿐이라 **HZ 결속 단서는
    사라지고 free 결속 단서는 남는다**(ACCOUNTING §4.1 비균질 세대).
    검정 1의 위양성이 어느 쪽에서 나는지 읽는 열쇠라 함께 인쇄한다.
    """
    p = os.path.join(V3, "code/hazgate.json")
    if not os.path.exists(p):
        return {}
    out = {}
    for k, v in json.load(open(p, encoding="utf-8")).items():
        tag, fn = k.split("::")
        if tag not in ("main", "batch1"):
            continue
        s = fn.split("_")[0]
        for c, rec in v["cue"].items():
            out[(s, c)] = ("ABSENT" if rec is None
                           else "HZ" if rec["all_hazard_gated"]
                           else "hz?" if rec["any"] else "free")
    return out


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def scene_dir(run, scene):
    g = glob.glob(os.path.join(REPO, "dataset", run, "*", scene, "variation.json"))
    return os.path.dirname(g[0]) if g else None


def cuts_of(d):
    v = json.load(open(os.path.join(d, "variation.json"), encoding="utf-8"))
    cu = v["cuts"]
    return {c["file"]: c for c in (cu.values() if isinstance(cu, dict) else cu)}


def load_labels(arm):
    p = os.path.join(ANN, f"{ANN_PREFIX}{arm}.json")
    if not os.path.exists(p):
        return None
    d = json.load(open(p, encoding="utf-8"))
    cells = {}
    for s in d.get("scene_footprint", []):
        if s.get("arm") == "on" and "cells_raw" in s:
            cells[s["scene"]] = s
    return dict(frames=d.get("frames", {}), cells=cells,
                warnings=d.get("warnings", []))


def rgb_delta(pa, pb):
    """(mean |Δ| in LSB, frac of pixels differing) or (None, None)."""
    try:
        from PIL import Image
    except Exception:
        return None, None
    a = np.asarray(Image.open(pa).convert("RGB"), dtype=np.int16)
    b = np.asarray(Image.open(pb).convert("RGB"), dtype=np.int16)
    if a.shape != b.shape:
        return None, None
    d = np.abs(a - b)
    return float(d.mean()), float((d.max(axis=2) > 0).mean())


def geom_compare(da, db):
    """heightmap A vs Bx."""
    ha, hb = os.path.join(da, "heightmap.npy"), os.path.join(db, "heightmap.npy")
    ma = json.load(open(os.path.join(da, "heightmap_meta.json"), encoding="utf-8"))
    mb = json.load(open(os.path.join(db, "heightmap_meta.json"), encoding="utf-8"))
    A, B = np.load(ha), np.load(hb)
    out = dict(hm_sha_a=sha256(ha)[:16], hm_sha_b=sha256(hb)[:16],
               n_prims_a=ma.get("n_prims"), n_prims_b=mb.get("n_prims"),
               arm_config_a=ma.get("arm_config"), arm_config_b=mb.get("arm_config"),
               grid_same=(ma.get("x0"), ma.get("y0"), ma.get("step"),
                          ma.get("nx"), ma.get("ny")) ==
                         (mb.get("x0"), mb.get("y0"), mb.get("step"),
                          mb.get("nx"), mb.get("ny")))
    out["hm_identical"] = out["hm_sha_a"] == out["hm_sha_b"]
    if A.shape != B.shape or not out["grid_same"]:
        out["dz_max"] = None
        out["hm_cells_changed"] = None
        out["void_delta"] = None
        return out
    fa, fb = np.isfinite(A), np.isfinite(B)
    both = fa & fb
    d = np.abs(A[both] - B[both]) if both.any() else np.zeros(1)
    out["dz_max"] = round(float(d.max()), 6) if d.size else 0.0
    out["hm_cells_changed"] = int((d > 1e-6).sum())
    # 부호 있는 최대치도 남긴다: Bx가 A보다 낮아졌는지(제거) 높아졌는지
    sd = (B[both] - A[both]) if both.any() else np.zeros(1)
    out["dz_signed_min"] = round(float(sd.min()), 6) if sd.size else 0.0
    out["dz_signed_max"] = round(float(sd.max()), 6) if sd.size else 0.0
    out["void_delta"] = int(fb.sum()) - int(fa.sum())   # +: Bx가 더 많이 측정됨
    return out


def _hm(d):
    """(z, geo) — `HM_LOADER`가 'labeler'면 융합 사이드카가 이긴다."""
    if HM_LOADER == "labeler":
        sys.path.insert(0, os.path.join(REPO, "experiments/mainrun_0819/code/labeling"))
        import labeler as LB
        z, geo, _src = LB.load_heightmap(d)
        return z, geo
    z = np.load(os.path.join(d, "heightmap.npy"))
    m = json.load(open(os.path.join(d, "heightmap_meta.json"), encoding="utf-8"))
    return z, (m["x0"], m["y0"], m["step"])


def fp_mask(scene, z_arm, geo_arm=None):
    """A팔 기준 낙차 발자국 마스크 (라벨러 footprint v2와 같은 식).

    z_off = `ZOFF_ROUND` (기본 260819_main_off = 정본 구off, 같은 시드).
    라벨러에 넘기는 `--off-round`와 **반드시 같은 라운드**여야 한다.
    """
    g = glob.glob(os.path.join(REPO, "dataset", ZOFF_ROUND, "*", scene,
                               "variation.json"))
    if not g:
        return None
    zo, geo_o = _hm(os.path.dirname(g[0]))
    if geo_arm is not None and HM_LOADER == "labeler":
        sys.path.insert(0, os.path.join(REPO, "experiments/mainrun_0819/code/labeling"))
        import labeler as LB
        zo = LB.align_to(zo, geo_o, geo_arm, z_arm.shape)
    if zo.shape != z_arm.shape:
        return None
    d = np.where(np.isfinite(zo) & np.isfinite(z_arm), zo - z_arm, np.nan)
    return (np.isfinite(d)) & (d >= 0.3)


def dilate(mask, r):
    """r셀 반경 사각 팽창 (0.05 m 격자 · r=20 → STEP_RUN_M 1.0 m)."""
    out = mask.copy()
    for _ in range(r):
        o = out.copy()
        o[1:, :] |= out[:-1, :]
        o[:-1, :] |= out[1:, :]
        o[:, 1:] |= out[:, :-1]
        o[:, :-1] |= out[:, 1:]
        out = o
    return out


def cue_locus(scene, da, db):
    """2차 진단 — **단서 프림이 낙차 발자국 위에 서 있는가.**

    1차 통계(공유 z_off 위의 Δcells_raw)는 한 가지를 구별하지 못한다:
      (ㄱ) 단서가 낙차 표면의 일부라서 지우면 낙차가 변한다   = 진짜 구조물
      (ㄴ) 단서가 평지 위에 서 있고, **참조로 쓴 구off에도 그 단서가 그대로
           남아 있어서** 단서를 지운 팔에서만 (z_off − z_on)이 커진 것 = 짝맞춤 인공물
    v3의 실제 짝은 B↔D(둘 다 cue-off)라 (ㄴ)은 W1에서 발생하지 않는다.
    그래서 단서의 기하 궤적 Δcue = {|z_A − z_B| > 0}가 A팔 발자국과 겹치는지를
    따로 잰다. 겹치면 (ㄱ), 안 겹치면 (ㄴ)이다.
    """
    za, geo_a = _hm(da)
    zb, _geo_b = _hm(db)
    if za.shape != zb.shape:
        return None
    fa = fp_mask(scene, za, geo_a)
    if fa is None:
        return None
    both = np.isfinite(za) & np.isfinite(zb)
    dcue = both & (np.abs(za - zb) > 1e-6)
    inter = dcue & fa
    lip = dilate(fa, 20) & ~fa
    return dict(
        fp_A_cells=int(fa.sum()),
        dcue_cells=int(dcue.sum()),
        dcue_in_fpA=int(inter.sum()),
        dcue_in_lip_1m=int((dcue & lip).sum()),
        dz_max_in_fpA=(round(float(np.abs(za - zb)[inter].max()), 6)
                       if inter.any() else 0.0),
        locus=("낙차면" if inter.any() else
               "립근방" if (dcue & lip).any() else "평지"))


def datum_compare(ca, cb, da, db):
    """VG-datum + VG-10: 파일명 일치 컷쌍의 ground_z / 포즈 비교."""
    common = sorted(set(ca) & set(cb))
    rows, worst, tiers = [], 0.0, dict(datum_exact=0, datum_tol=0, datum_fail=0)
    pose_worst = 0.0
    for f in common:
        a, b = ca[f]["cam"], cb[f]["cam"]
        dz = abs(float(a["ground_z"]) - float(b["ground_z"]))
        t = ("datum_exact" if dz < DATUM_EXACT
             else "datum_tol" if dz <= DATUM_TOL else "datum_fail")
        tiers[t] += 1
        worst = max(worst, dz)
        pk = max(abs(float(a[k]) - float(b[k])) for k in POSE_KEYS)
        pe = max(abs(float(a["eye"][i]) - float(b["eye"][i])) for i in range(3))
        pose_worst = max(pose_worst, pk, pe)
        rows.append(dict(file=f, d_ground_z=round(dz, 8), tier=t,
                         d_pose_max=round(max(pk, pe), 9)))
    return dict(n_cuts=len(common), tiers=tiers,
                ground_z_drift_max=round(worst, 8),
                pose_delta_max=round(pose_worst, 9),
                datum_verdict=("datum_fail" if tiers["datum_fail"]
                               else "datum_tol" if tiers["datum_tol"]
                               else "datum_exact"),
                cuts=rows)


def main():
    pairs = [tuple(p) for p in
             json.load(open(PLAN, encoding="utf-8"))["classification_probe"]["pairs"]]
    labels = {a: load_labels(a) for a in ("A",) + tuple(sorted(set(ARM_OF_CUE.values())))}
    bonds = load_bonds()
    rows, problems = [], []

    for scene, cue in pairs:
        arm = ARM_OF_CUE[cue]
        r = dict(scene=scene, cue=cue, cue_short=CUE_SHORT.get(cue), arm=arm,
                 bond=bonds.get((scene, cue), "?"),
                 round_a=f"{STAMP}_A", round_b=f"{STAMP}_{arm}")
        da, db = scene_dir(f"{STAMP}_A", scene), scene_dir(f"{STAMP}_{arm}", scene)
        if not da or not db:
            r.update(verdict="판정불가", reason="render_missing",
                     missing=[x for x, y in (("A", da), (arm, db)) if not y])
            rows.append(r)
            problems.append(f"{scene}/{cue}: {r['missing']} 팔 렌더 없음")
            continue
        r["dir_a"] = os.path.relpath(da, REPO)
        r["dir_b"] = os.path.relpath(db, REPO)
        r.update(geom_compare(da, db))

        ca, cb = cuts_of(da), cuts_of(db)
        r["datum"] = datum_compare(ca, cb, da, db)
        r["locus"] = cue_locus(scene, da, db)

        # RGB 광학차 — 무효 토글 검사 (첫 컷 1장이면 충분하나 전 컷 평균을 쓴다)
        md, fr = [], []
        for f in sorted(set(ca) & set(cb)):
            m, p = rgb_delta(os.path.join(da, f), os.path.join(db, f))
            if m is not None:
                md.append(m)
                fr.append(p)
        r["rgb_mean_abs_lsb"] = round(float(np.mean(md)), 5) if md else None
        r["rgb_frac_px_changed"] = round(float(np.mean(fr)), 6) if fr else None

        # 라벨러 — cells_raw + polar_gt
        la, lb = labels.get("A"), labels.get(arm)
        if not la or not lb or scene not in la["cells"] or scene not in lb["cells"]:
            r["cells_raw_a"] = r["cells_raw_b"] = r["d_cells_raw"] = None
            r["polar_gt_n_diff"] = r["polar_gt_n_cmp"] = None
        else:
            sa, sb = la["cells"][scene], lb["cells"][scene]
            r["cells_raw_a"] = sa["cells_raw"]
            r["cells_raw_b"] = sb["cells_raw"]
            r["d_cells_raw"] = sb["cells_raw"] - sa["cells_raw"]
            r["cells_kept_max_a"] = sa.get("cells_kept_max")
            r["cells_kept_max_b"] = sb.get("cells_kept_max")
            r["max_diff_a"] = sa.get("max_diff")
            r["max_diff_b"] = sb.get("max_diff")
            n_d = n_c = 0
            diffs = []
            for f in sorted(set(ca) & set(cb)):
                ka, kb = f"on/{scene}/{f}", f"on/{scene}/{f}"
                if ka in la["frames"] and kb in lb["frames"]:
                    n_c += 1
                    if la["frames"][ka]["polar_gt"] != lb["frames"][kb]["polar_gt"]:
                        n_d += 1
                        diffs.append(f)
            r["polar_gt_n_cmp"] = n_c
            r["polar_gt_n_diff"] = n_d
            r["polar_gt_diff_frames"] = diffs
            r["tier_a"] = [la["frames"][f"on/{scene}/{f}"].get("tier_strict")
                           for f in sorted(set(ca) & set(cb))
                           if f"on/{scene}/{f}" in la["frames"]]
            r["tier_b"] = [lb["frames"][f"on/{scene}/{f}"].get("tier_strict")
                           for f in sorted(set(ca) & set(cb))
                           if f"on/{scene}/{f}" in lb["frames"]]

        # ---- 판정 (위 R1/R2/R3 그대로) ----------------------------------
        noop = (r.get("hm_identical") and
                r.get("n_prims_a") == r.get("n_prims_b") and
                r.get("rgb_mean_abs_lsb") is not None and
                r["rgb_mean_abs_lsb"] < NOOP_RGB_LSB)
        if r.get("d_cells_raw") is None or r.get("polar_gt_n_cmp") in (None, 0):
            r.update(verdict="판정불가", reason="label_missing")
            problems.append(f"{scene}/{cue}: 라벨 없음 (cells_raw/polar_gt 비교 불가)")
        elif noop:
            r.update(verdict="판정불가", reason="noop_toggle")
            problems.append(f"{scene}/{cue}: 무효 토글 — 높이맵·프림수·RGB 전부 동일")
        elif r["d_cells_raw"] != 0 or r["polar_gt_n_diff"] > 0:
            r.update(verdict="구조물",
                     reason=("footprint" if r["d_cells_raw"] != 0 else "") +
                            ("+" if r["d_cells_raw"] != 0 and r["polar_gt_n_diff"] else "") +
                            ("polar_gt" if r["polar_gt_n_diff"] else ""))
        else:
            r.update(verdict="장식",
                     subtype=("완전" if r.get("hm_identical") else "지형외"),
                     reason="footprint 0 · polar_gt 동일")
        # ---- 검정 2 (기하 궤적) ------------------------------------------
        lo = r.get("locus")
        r["verdict_t1"] = r["verdict"]          # 검정 1 = 사전등록 VG-01 통계
        if lo is None or r["verdict"] == "판정불가":
            r["verdict_t2"] = r["verdict"]
        elif lo["dcue_in_fpA"] > 0:
            r["verdict_t2"] = "구조물"
        else:
            r["verdict_t2"] = "장식"
        r["verdicts_agree"] = (r["verdict_t1"] == r["verdict_t2"])

        # ---- 종합 판정 -----------------------------------------------------
        # 두 검정은 각각 한 방향으로 눈이 멀어 있다(§보고서 "왜 두 번 재는가").
        #   검정 1: 참조 구off가 cue-비대칭 → 자유결속 단서에서 위양성
        #   검정 2: fp_A가 단서에 가려짐   → 낙차 위를 덮는 단서에서 위음성
        # 계획 §1.2는 "**장식으로 판정한 것만**" 레버로 허락한다. 두 검정이
        # 엇갈리면 그 쌍은 장식으로 판정된 것이 아니므로 **판정불가**다.
        if r["verdict"] == "판정불가":
            pass
        elif r["verdict_t1"] == r["verdict_t2"]:
            r["verdict"] = r["verdict_t1"]
        else:
            r["verdict"] = "판정불가"
            r["reason"] = f"검정 불일치 (t1={r['verdict_t1']} · t2={r['verdict_t2']}) — cue-대칭 off팔 없음"
            r.pop("subtype", None)
        rows.append(r)

    # ---- 산출 --------------------------------------------------------------
    counts = {}
    for r in rows:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    forbidden = sorted({(r["scene"], r["cue"]) for r in rows
                        if r["verdict"] in ("구조물", "판정불가")} |
                       {(p["scene"], p["cue"]) for p in PRIOR
                        if p["verdict"] == "구조물"})
    confirmed = {}
    for r in rows:
        if r["verdict"] == "장식":
            confirmed.setdefault(r["scene"], []).append(r["cue"])
    for p in PRIOR:
        if p["verdict"] == "장식":
            confirmed.setdefault(p["scene"], []).append(p["cue"])
    for k in confirmed:
        confirmed[k] = sorted(set(confirmed[k]))

    # ---- 보조 진단: W0 A팔 vs z_off 라운드의 데이텀 -------------------------
    # v2의 183/792 탈락을 낳은 그 짝(on팔 ↔ off팔)을 같은 자로 재어 둔다.
    # **교락 주의**: 구off는 hazard 제거 + hazard 분기 안의 cue 제거가 섞인
    # 비균질 세대(ACCOUNTING §4.1)라 드레싱 단독 효과가 아니다. 참고치일 뿐이다.
    corpus_ref = []
    for scene in sorted({s for s, _ in pairs}):
        da = scene_dir(f"{STAMP}_A", scene)
        g = glob.glob(os.path.join(REPO, "dataset", ZOFF_ROUND, "*", scene,
                                   "variation.json"))
        if not da or not g:
            continue
        do = os.path.dirname(g[0])
        dd = datum_compare(cuts_of(da), cuts_of(do), da, do)
        corpus_ref.append(dict(scene=scene, n_cuts=dd["n_cuts"], tiers=dd["tiers"],
                               ground_z_drift_max=dd["ground_z_drift_max"],
                               pose_delta_max=dd["pose_delta_max"],
                               verdict=dd["datum_verdict"]))

    datum_drift = [dict(scene=r["scene"], cue=r["cue"],
                        ground_z_drift_max=r["datum"]["ground_z_drift_max"],
                        tiers=r["datum"]["tiers"],
                        verdict=r["datum"]["datum_verdict"])
                   for r in rows if r.get("datum") and
                   r["datum"]["datum_verdict"] != "datum_exact"]

    out = dict(
        doc="w0_cuecls", version="1.0", gate="VG-CLS", plan="RENDER_PLAN_V3 §4.2 · §6.1",
        rounds=[f"{STAMP}_{a}" for a in ("A", "Brail", "Bnose", "Btact", "Bmatl", "Bdress")],
        off_round_for_footprint=ZOFF_ROUND,
        annotations_prefix=ANN_PREFIX,
        hm_loader=HM_LOADER,
        grid="gridspec_v1.json (20칸)",
        rules=dict(
            structural="Δcells_raw ≠ 0 또는 polar_gt 상이 프레임 ≥ 1",
            decorative="Δcells_raw = 0 그리고 polar_gt 전 프레임 동일",
            undecidable="렌더/라벨 부재, 또는 무효 토글(hm sha 동일 ∧ n_prims 동일 ∧ RGB<0.05 LSB)",
            datum=f"exact<{DATUM_EXACT} · tol<={DATUM_TOL} m · fail>{DATUM_TOL} m"),
        n_pairs=len(rows), verdict_counts=counts,
        toggle_forbidden=[dict(scene=s, cue=c) for s, c in forbidden],
        b_levers_confirmed=confirmed,
        verdict_counts_t1={v: sum(1 for r in rows if r.get("verdict_t1") == v)
                           for v in ("구조물", "장식", "판정불가")},
        verdict_counts_t2={v: sum(1 for r in rows if r.get("verdict_t2") == v)
                           for v in ("구조물", "장식", "판정불가")},
        disagreements=[dict(scene=r["scene"], cue=r["cue"], bond=r.get("bond"),
                            t1=r["verdict_t1"], t2=r["verdict_t2"],
                            d_cells_raw=r.get("d_cells_raw"),
                            dcue_cells=(r["locus"] or {}).get("dcue_cells"),
                            dcue_in_fpA=(r["locus"] or {}).get("dcue_in_fpA"),
                            dcue_in_lip_1m=(r["locus"] or {}).get("dcue_in_lip_1m"))
                       for r in rows if not r.get("verdicts_agree", True)],
        vg_datum_drift=datum_drift,
        vg_datum_corpus_ref=corpus_ref,
        prior_rulings=PRIOR,
        problems=problems,
        pairs=rows)
    op = OUT_PATH
    json.dump(out, open(op, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # ---- stdout 표 ---------------------------------------------------------
    hdr = (f"{'scene':9s} {'cue':20s} {'bond':5s} {'dz_max':>9s} {'hm셀':>7s} "
           f"{'cells_raw A→B':>15s} {'Δfp':>6s} {'pgt':>5s} {'Δgz':>10s} "
           f"{'RGB':>8s}  검정1  검정2   종합")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        dz = "—" if r.get("dz_max") is None else f"{r['dz_max']:.4f}"
        cr = ("—" if r.get("cells_raw_a") is None
              else f"{r['cells_raw_a']}→{r['cells_raw_b']}")
        df = "—" if r.get("d_cells_raw") is None else f"{r['d_cells_raw']:+d}"
        pg = ("—" if r.get("polar_gt_n_cmp") is None
              else f"{r['polar_gt_n_diff']}/{r['polar_gt_n_cmp']}")
        gz = ("—" if not r.get("datum")
              else f"{r['datum']['ground_z_drift_max']:.6f}")
        rg = "—" if r.get("rgb_mean_abs_lsb") is None else f"{r['rgb_mean_abs_lsb']:.3f}"
        hc = "—" if r.get("hm_cells_changed") is None else f"{r['hm_cells_changed']}"
        v = r["verdict"] + (f"({r['subtype']})" if r.get("subtype") else "")
        lo = r.get("locus") or {}
        loc = (f"{lo.get('locus','—'):4s} fp∩={lo.get('dcue_in_fpA','—')}")
        print(f"{r['scene']:9s} {r['cue']:20s} {r.get('bond','?'):5s} {dz:>9s} "
              f"{hc:>7s} {cr:>15s} {df:>6s} {pg:>5s} {gz:>10s} {rg:>8s}  "
              f"t1={r['verdict_t1']:5s} t2={r['verdict_t2']:5s}  {v:12s} {loc}")
    print()
    print("검정1(VG-01 통계):", out["verdict_counts_t1"])
    print("검정2(기하 궤적) :", out["verdict_counts_t2"], "· 불일치",
          len(out["disagreements"]))
    print("verdict counts:", counts)
    print("토글 금지 목록:", len(forbidden), forbidden)
    print("VG-datum 비-exact 쌍:", len(datum_drift))
    for d in datum_drift:
        print("   ", d)
    print("\n보조: A팔 vs 260819_main_off 데이텀 (교락 — 참고치)")
    for c in corpus_ref:
        if c["verdict"] != "datum_exact":
            print("   ", c)
    if problems:
        print("\nPROBLEMS:")
        for p in problems:
            print("  -", p)
    print(f"\n-> {op}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--zoff-round", default=ZOFF_ROUND,
                    help="낙차 발자국 z_off 라운드 (라벨러 --off-round와 동일해야 함)")
    ap.add_argument("--ann-prefix", default=ANN_PREFIX,
                    help="annotations/<prefix><arm>.json")
    ap.add_argument("--out", default=OUT_PATH)
    ap.add_argument("--hm-loader", choices=("aabb", "labeler"), default=HM_LOADER,
                    help="검정 2의 높이맵 계기 (labeler = 융합 사이드카 우선)")
    _a = ap.parse_args()
    ZOFF_ROUND, ANN_PREFIX, OUT_PATH = _a.zoff_round, _a.ann_prefix, _a.out
    HM_LOADER = _a.hm_loader
    print(f"[cls] z_off={ZOFF_ROUND} · ann={ANN_PREFIX}*.json · hm={HM_LOADER} "
          f"· out={OUT_PATH}")
    sys.exit(main())
