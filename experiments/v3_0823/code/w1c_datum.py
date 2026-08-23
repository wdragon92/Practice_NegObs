#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w1c_datum.py — **REPAIR 3**: 쌍짓기 데이텀의 *계기* 수리 (D82 ② 승인분).

무엇이 고장났나 (W1D_REPORT §3)
--------------------------------
VG-datum 은 같은 컷 이름의 두 팔에서 `cam.ground_z` 를 비교한다.  그런데
`cam.ground_z` 는 `pre.ground_z(-d, y)`, 즉 **그 렌더의 카메라 스트립 AABB
탐침**이다.  카메라 데이텀 스트립(x<0 · |y| ≤ 0.90 · d ∈ [1.2,12]) 안에
단서/드레싱 프림이 서 있으면 그 프림의 상면이 곧 "지면"이 되고, 팔에서 그
프림을 지우면 지면이 무너지며 카메라가 같이 내려앉는다.  W1-D 실측:

    scene02 base  Δ 2.8236 m  (A 2.8400 → D 0.0164)   9/24 컷
    scene10 base  Δ 0.2500 m  (A −0.0050 → D −0.2550) 3/24 컷
    sceneN1 base  Δ 12.8000 m (A 12.8000 → D 0.0000)  3/24 컷  ← 관측 최대

세 건 모두 **카메라 한 자리**의 문제다(같은 컷 인덱스가 세 조명 조건에
공유되므로 3컷씩 걸린다).  v2 에서 (A,C) 트윈 183/792 을 날린 기전과 같다.

왜 씬 기하를 고치지 않는가
---------------------------
"드레싱 프림을 스트립 밖으로 옮긴다"는 씬-기하 수리는 **A 팔과의 연속성을
깬다**.  v3 의 A 팔은 `260819_main_on` 등을 **전량 재활용**하고(계획 §1.2
"신규 컷 0"), 그 프레임들은 프림이 지금 있는 자리에 있을 때 찍혔다.  프림을
옮기면 재활용 A 팔은 더 이상 같은 씬의 산물이 아니다.  그러므로 수리는
**계기 층**에서 해야 한다 — 재는 자를 바꾸는 것이지 재는 대상을 옮기는 것이
아니다.

수리 — 팔-불변 보행면 기준 (`instrument` 모드)
----------------------------------------------
W1-D 가 이미 **단서가 하나도 없는 팔**에서 보행면을 재는 계기를 갖고 있다
(`w1d_verify.py:274-282`):

    ring   = dilate(fp_corpus, 20셀=1.0 m) − fp_corpus − ¬finite(z_D)
    walk_z = median(z_D[ring])                (ring < 50셀이면 grid median)

`z_D` 는 D 팔 높이맵이고 D 팔에는 단서가 **하나도 없다**.  그러므로 `walk_z`
는 (a) 카메라와 무관하고 (b) 어느 팔의 단서 구성과도 무관한 **씬 수준 상수**
다.  이것을 쌍짓기의 기준면으로 삼으면 물음이 바뀐다:

    (구) |ground_z_A − ground_z_X| ≤ tol ?      ← 두 팔이 서로를 판정한다
    (신) |ground_z_A − walk_z| ≤ tol  AND
         |ground_z_X − walk_z| ≤ tol ?          ← 팔-불변 기준이 각 팔을 판정한다

(신) 은 (구) 가 못 하는 두 가지를 한다.
① **결함을 팔과 카메라 자리에 국소화한다.**  sceneN1 컷 0004 에서 (구) 는
   "쌍이 깨졌다"만 말한다.  (신) 은 "A 팔의 카메라가 보행면보다 12.80 m 위
   프림 위에 서 있었다"고 말한다 — W1-D 가 **손으로** 알아낸 그 사실이다.
② **C 팔에서 쌍을 되살린다.**  C 는 드레싱을 **남기므로** 스트립 프림도
   남는다.  두 팔이 같은 프림 위에 서 있으면 (구) 는 통과하지만, 그 통과는
   "둘 다 같은 오차를 갖는다"는 통과다.  (신) 은 그 경우 `both_off` 로
   **양쪽 다 보행면 위가 아님**을 인쇄하므로, 쌍은 살리되 사실은 숨기지 않는다.

**모드는 옵트인이다.**  `mode="camera"` 가 기본이고 그 경로는
`w1b_verify.datum_pose` / `w1d_verify.datum_pose` 와 층 정의·문턱이 같다
(`datum_exact` < 1e-6 · `datum_tol` ≤ 0.02 m · `datum_fail` > 0.02 m).
`instrument` 모드는 **cue/dressing 제거가 스트립을 건드리는 팔** 에서만 켠다.

사용
----
  python3 experiments/v3_0823/code/w1c_datum.py                  # 전 밴드
  python3 experiments/v3_0823/code/w1c_datum.py --mode camera    # 구 계기만
  python3 experiments/v3_0823/code/w1c_datum.py --scenes scene02,scene10,sceneN1
산출: experiments/v3_0823/w1c_datum.json
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V3 = os.path.join(REPO, "experiments/v3_0823")
LABDIR = os.path.join(REPO, "experiments/mainrun_0819/code/labeling")
sys.path.insert(0, LABDIR)
import labeler as LB                                            # noqa: E402

GRID = json.load(open(os.path.join(LABDIR, "gridspec_v1.json"), encoding="utf-8"))
HAZ_DEPTH = float(GRID["hazard_depth_m"])

DATUM_EXACT, DATUM_TOL = 1e-6, 0.02          # W1-B/W1-D 와 동일 (변경 금지)
RING_CELLS = 20                              # 0.05 m 격자 × 20 = 1.0 m
RING_MIN = 50                                # w1d_verify.py:277

C = "260827_v3w1_lib_C"
D = "260826_v3w1_lib_D"
# band -> (C round, A corpus round, old-off corpus round, D round, scenes)
BANDS = {
    "base": (C, "260819_main_on", "260819_main_off", D,
             "scene01 scene02 scene03 scene04 scene06 scene08 scene09 scene10 "
             "scene12 scene16 scene17 scene20 scene21 sceneC1 sceneC4 sceneD1 "
             "sceneD2 sceneD3".split()),
    "h":    (f"{C}_h", "260820_boost_h_on", "260820_boost_h_off", f"{D}_h",
             "scene09 scene17".split()),
    "e":    (f"{C}_e", "260820_boost_e_on", "260820_boost_e_off", f"{D}_e",
             "scene03 scene04 scene08 scene09 scene12 scene17 scene20 sceneC1 "
             "sceneC4".split()),
    "e2":   (f"{C}_e2", "260820_boost_e2_on", "260820_boost_e2_off", f"{D}_e2",
             "scene03 scene04 scene12 scene20 sceneC4".split()),
}
# W1D_REPORT §3 의 데이텀 결함 3건 — 이 계기가 존재하는 이유
DATUM_DEFECT = {("scene02", "base"): 2.8236,
                ("scene10", "base"): 0.2500,
                ("sceneN1", "base"): 12.8000}


def dilate(mask, r):
    """r셀 반경 사각 팽창 — `w1d_verify.dilate` 와 같은 구현(같은 답 보증)."""
    out = mask.copy()
    for _ in range(r):
        o = out.copy()
        o[1:, :] |= out[:-1, :]
        o[:-1, :] |= out[1:, :]
        o[:, 1:] |= out[:, :-1]
        o[:, :-1] |= out[:, 1:]
        out = o
    return out


def sdir(run, scene):
    g = glob.glob(os.path.join(REPO, "dataset", run, "*", scene, "variation.json"))
    return os.path.dirname(g[0]) if g else None


def cuts_of(d):
    v = json.load(open(os.path.join(d, "variation.json"), encoding="utf-8"))
    cu = v["cuts"]
    cu = list(cu.values()) if isinstance(cu, dict) else cu
    return {c["file"]: c for c in cu}


def hm_of(d):
    z, geo, src = LB.load_heightmap(d)
    return z, geo, src


# --------------------------------------------------------------------------- #
# (구) 계기 — 두 팔이 서로를 판정한다.  기본 모드.
# --------------------------------------------------------------------------- #
def datum_camera(ca, cx, x_tag="C"):
    """`w1b_verify.datum_pose` / `w1d_verify.datum_pose` 와 **같은 판정**."""
    common = sorted(set(ca) & set(cx))
    tiers = dict(datum_exact=0, datum_tol=0, datum_fail=0)
    fails, worst = [], 0.0
    for f in common:
        a, b = ca[f].get("cam") or {}, cx[f].get("cam") or {}
        if "ground_z" not in a or "ground_z" not in b:
            continue
        dz = abs(float(a["ground_z"]) - float(b["ground_z"]))
        t = ("datum_exact" if dz < DATUM_EXACT
             else "datum_tol" if dz <= DATUM_TOL else "datum_fail")
        tiers[t] += 1
        worst = max(worst, dz)
        if t == "datum_fail":
            fails.append(dict(file=f, d_ground_z=round(dz, 6),
                              a_ground_z=round(float(a["ground_z"]), 6),
                              x_ground_z=round(float(b["ground_z"]), 6)))
    return dict(mode="camera", other_arm=x_tag, n_cuts=len(common), tiers=tiers,
                ground_z_drift_max=round(worst, 8),
                n_fail_cuts=len(fails), fail_cuts=fails[:8],
                verdict=("datum_fail" if tiers["datum_fail"]
                         else "datum_tol" if tiers["datum_tol"]
                         else "datum_exact"))


# --------------------------------------------------------------------------- #
# (신) 계기 — 팔-불변 보행면이 각 팔을 판정한다.  옵트인 모드.
# --------------------------------------------------------------------------- #
def walk_level(za, zo, zd):
    """D팔 높이맵의 **발자국 둘레 링 중앙값** = 팔-불변 보행면 높이.

    `w1d_verify.py:274-282` 의 계보를 그대로 쓴다.  fp_corpus 는 코퍼스 A팔과
    정본 구off 로 만든 발자국(카메라 등장 이전 · 팔 무관)이고, ring 은 그
    발자국을 1.0 m 팽창시킨 뒤 발자국 자신을 뺀 띠다.  D 팔에는 단서가 하나도
    없으므로 이 중앙값은 어떤 단서 구성에도 오염되지 않는다.
    """
    fin = np.isfinite(za) & np.isfinite(zo) & np.isfinite(zd)
    fp = fin & ((zo - za) >= HAZ_DEPTH)
    finD = np.isfinite(zd)
    ring = dilate(fp, RING_CELLS) & ~fp & finD
    if int(ring.sum()) >= RING_MIN:
        return float(np.median(zd[ring])), "ring_1m", int(ring.sum()), int(fp.sum())
    wz = float(np.median(zd[finD])) if finD.any() else float("nan")
    return wz, "grid_median", int(ring.sum()), int(fp.sum())


def strip_level(zd, geo):
    """**카메라 데이텀 스트립 자체**의 D팔 중앙값 — 링 중앙값의 짝 기준.

    왜 두 기준이 필요한가 (본 웨이브의 실측 소득).  링 중앙값은 **발자국 둘레**
    의 양이다.  발자국 둘레와 카메라 스트립이 같은 레벨인 씬(대부분)에서는 그것이
    곧 보행면이지만, `scene10`(갈지자 데크)처럼 **발자국 둘레가 하부 공원이고
    카메라는 상부 트레일에 서는** 씬에서는 두 레벨이 1.4 m 넘게 다르다.  그러면
    링 기준은 두 팔을 똑같이 `both_off` 로 부르는데, 그것은 팔의 결함이 아니라
    **기준의 정의역이 어긋난 것**이다.

    그래서 `cam.ground_z` 를 판정할 때의 올바른 정의역은 `pre.ground_z(-d, y)`
    가 실제로 훑는 영역, 즉 **스트립**(x ∈ [−12, −1.2] · |y| ≤ 0.90) 이다.
    D팔에서 재므로 팔-불변성은 그대로다.  두 값을 **함께 인쇄**해서 어느
    기준으로 읽든 숫자가 표에 있게 한다.
    """
    x0, y0, st = geo[0], geo[1], geo[2]
    ny, nx = zd.shape
    xs = x0 + st * np.arange(nx)[None, :]
    ys = y0 + st * np.arange(ny)[:, None]
    strip = (xs >= -12.0) & (xs <= -1.2) & (np.abs(ys) <= 0.90) & np.isfinite(zd)
    n = int(strip.sum())
    if n < 20:
        return float("nan"), n
    return float(np.median(zd[strip])), n


def datum_instrument(ca, cx, walk_z, x_tag="C", tol=DATUM_TOL):
    """각 팔의 `cam.ground_z` 를 **팔-불변 보행면**에 대고 잰다.

    층
      `instr_exact`    두 팔 모두 |ground_z − walk_z| ≤ tol
                       → 두 카메라가 진짜 보행면 위에 있다. 쌍 유효.
      `instr_one_off`  정확히 한 팔만 벗어난다
                       → **결함이 그 팔·그 카메라 자리로 국소화된다.**
      `instr_both_off` 두 팔 모두 벗어난다
                       → 두 카메라가 같은 프림 위에 서 있거나(=C팔의 정상
                         모습) 링 기준이 그 자리를 대표하지 못한다.
                         쌍은 살리되 사실을 인쇄한다.
    """
    common = sorted(set(ca) & set(cx))
    tiers = dict(instr_exact=0, instr_one_off=0, instr_both_off=0)
    rows, worst_a, worst_x = [], 0.0, 0.0
    if not np.isfinite(walk_z):
        return dict(mode="instrument", other_arm=x_tag, n_cuts=len(common),
                    walk_z=None, tiers=tiers, verdict="no_reference")
    for f in common:
        a, b = ca[f].get("cam") or {}, cx[f].get("cam") or {}
        if "ground_z" not in a or "ground_z" not in b:
            continue
        da_ = abs(float(a["ground_z"]) - walk_z)
        dx_ = abs(float(b["ground_z"]) - walk_z)
        worst_a, worst_x = max(worst_a, da_), max(worst_x, dx_)
        off = (da_ > tol) + (dx_ > tol)
        t = ("instr_exact" if off == 0
             else "instr_one_off" if off == 1 else "instr_both_off")
        tiers[t] += 1
        if off:
            rows.append(dict(file=f, arm_off=("A" if da_ > tol and dx_ <= tol
                                              else x_tag if dx_ > tol and da_ <= tol
                                              else "both"),
                             a_ground_z=round(float(a["ground_z"]), 6),
                             x_ground_z=round(float(b["ground_z"]), 6),
                             walk_z=round(walk_z, 6),
                             d_a=round(da_, 6), d_x=round(dx_, 6)))
    return dict(mode="instrument", other_arm=x_tag, n_cuts=len(common),
                walk_z=round(walk_z, 6), tol=tol, tiers=tiers,
                max_dev_A=round(worst_a, 6), max_dev_X=round(worst_x, 6),
                n_off_cuts=len(rows), off_cuts=rows[:8],
                verdict=("instr_exact" if tiers["instr_one_off"] == 0
                         and tiers["instr_both_off"] == 0
                         else "instr_one_off" if tiers["instr_one_off"]
                         else "instr_both_off"))


def run(mode="both", scenes_filter=None, bands_filter=None, other="C"):
    """other="C" 면 (A,C) 축, other="D" 면 (A,D) 축.

    (A,D) 축이 필요한 이유: **sceneN1 은 무낙차 씬이라 C팔이 on팔 재활용**
    (계획 §1.2 `24*`)이고 (A,C) 쌍이 정의상 자기 자신이다.  W1D_REPORT §3 의
    데이텀 결함 3건 중 sceneN1(12.8 m, 관측 최대)은 그러므로 (A,D) 축에서만
    잴 수 있다.  REPAIR-3 계기의 **국소화 능력**은 바로 그 사례에서 증명된다.
    """
    out = dict(repair="REPAIR-3 pairing-datum instrument (D82 ②)",
               lineage="w1d_verify.py:274-282 ring-median walk level",
               thresholds=dict(datum_exact=DATUM_EXACT, datum_tol=DATUM_TOL,
                               ring_cells=RING_CELLS, ring_min=RING_MIN),
               known_datum_defects={f"{k[0]}/{k[1]}": v
                                    for k, v in DATUM_DEFECT.items()},
               mode=mode, rows=[], problems=[])
    for band, (cr, ar, orr, dr, scs) in BANDS.items():
        if bands_filter and band not in bands_filter:
            continue
        if other == "D":
            # (A,D) 축: D 라운드의 씬 목록을 쓴다 (무낙차 4씬 포함)
            scs = sorted(set(scs) | {"sceneN1", "sceneN2", "sceneN4", "sceneN5"}) \
                if band == "base" else scs
        for s in scs:
            if scenes_filter and s not in scenes_filter:
                continue
            xr = dr if other == "D" else cr
            dc, da, do, dd = (sdir(xr, s), sdir(ar, s), sdir(orr, s), sdir(dr, s))
            row = dict(band=band, scene=s, other_arm=other, other_round=xr,
                       have={other: dc is not None, "A": da is not None,
                             "guoff": do is not None, "D": dd is not None})
            if not (dc and da):
                row["skip"] = f"{other} or A arm missing"
                out["rows"].append(row); continue
            ca, cx = cuts_of(da), cuts_of(dc)
            if mode in ("camera", "both"):
                row["camera"] = datum_camera(ca, cx, other)
            if mode in ("instrument", "both"):
                if not (do and dd):
                    row["instrument"] = dict(mode="instrument",
                                             verdict="no_reference",
                                             why="guoff or D arm missing")
                else:
                    za, ga, _ = hm_of(da)
                    zo, go, _ = hm_of(do)
                    zd, gd, _ = hm_of(dd)
                    zo = LB.align_to(zo, go, ga, za.shape)
                    zd = LB.align_to(zd, gd, ga, za.shape)
                    wz, src, nring, nfp = walk_level(za, zo, zd)
                    inst = datum_instrument(ca, cx, wz, other)
                    inst.update(walk_z_source=src, ring_cells=nring,
                                fp_corpus_cells=nfp)
                    # 짝 기준 — 스트립 자체의 D팔 중앙값
                    sz, nstrip = strip_level(zd, ga)
                    inst["walk_z_strip"] = (None if not np.isfinite(sz)
                                            else round(sz, 6))
                    inst["strip_cells"] = nstrip
                    if np.isfinite(sz):
                        si = datum_instrument(ca, cx, sz, other)
                        inst["strip_tiers"] = si["tiers"]
                        inst["strip_verdict"] = si["verdict"]
                        inst["strip_max_dev_A"] = si.get("max_dev_A")
                        inst["strip_max_dev_X"] = si.get("max_dev_X")
                        inst["strip_off_cuts"] = si.get("off_cuts", [])[:8]
                        inst["strip_n_off_cuts"] = si.get("n_off_cuts")
                        inst["ring_vs_strip_m"] = round(abs(wz - sz), 6)
                    row["instrument"] = inst
            if (s, band) in DATUM_DEFECT:
                row["datum_defect_scene"] = DATUM_DEFECT[(s, band)]
            out["rows"].append(row)
    # --- 집계 ---------------------------------------------------------------
    cam = [r["camera"] for r in out["rows"] if "camera" in r]
    ins = [r["instrument"] for r in out["rows"]
           if "instrument" in r and "tiers" in r["instrument"]]
    if cam:
        t = dict(datum_exact=0, datum_tol=0, datum_fail=0)
        for c in cam:
            for k in t:
                t[k] += c["tiers"][k]
        out["camera_summary"] = dict(
            n_pairs=len(cam), cut_tiers=t,
            pair_survival=f"{sum(1 for c in cam if c['verdict'] != 'datum_fail')}/{len(cam)}",
            cut_survival=f"{t['datum_exact'] + t['datum_tol']}/{sum(t.values())}",
            quarantine=[f"{r['scene']}/{r['band']}" for r in out["rows"]
                        if r.get("camera", {}).get("verdict") == "datum_fail"])
    if ins:
        t = dict(instr_exact=0, instr_one_off=0, instr_both_off=0)
        for c in ins:
            for k in t:
                t[k] += c["tiers"][k]
        out["instrument_summary"] = dict(
            n_pairs=len(ins), cut_tiers=t,
            pair_clean=f"{sum(1 for c in ins if c['verdict'] == 'instr_exact')}/{len(ins)}",
            localised=[dict(scene=r["scene"], band=r["band"],
                            arms=sorted({o["arm_off"] for o
                                         in r["instrument"].get("off_cuts", [])}),
                            n_off=r["instrument"]["n_off_cuts"],
                            walk_z=r["instrument"]["walk_z"],
                            max_dev_A=r["instrument"]["max_dev_A"],
                            max_dev_X=r["instrument"]["max_dev_X"])
                       for r in out["rows"]
                       if r.get("instrument", {}).get("n_off_cuts")])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="both",
                    choices=["camera", "instrument", "both"],
                    help="camera = 기본(구 계기) · instrument = REPAIR-3 옵트인")
    ap.add_argument("--scenes", default="")
    ap.add_argument("--bands", default="")
    ap.add_argument("--other", default="C")
    ap.add_argument("--out", default=os.path.join(V3, "w1c_datum.json"))
    a = ap.parse_args()
    out = run(a.mode,
              [x for x in a.scenes.split(",") if x] or None,
              [x for x in a.bands.split(",") if x] or None,
              a.other)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    if "camera_summary" in out:
        cs = out["camera_summary"]
        print(f"\n=== VG-datum (A,{a.other}) — 구 계기(카메라 스트립) ===")
        print(" ", cs["cut_tiers"], "· 쌍 생존", cs["pair_survival"],
              "· 컷 생존", cs["cut_survival"])
        print("  격리:", cs["quarantine"] or "없음")
    if "instrument_summary" in out:
        it = out["instrument_summary"]
        print(f"\n=== VG-datum (A,{a.other}) — REPAIR-3 계기(D팔 링 중앙값) ===")
        print(" ", it["cut_tiers"], "· 청정 쌍", it["pair_clean"])
        for l in it["localised"]:
            print(f"  {l['scene']}/{l['band']}: off {l['n_off']}컷 · 팔 {l['arms']}"
                  f" · walk_z {l['walk_z']} · devA {l['max_dev_A']}"
                  f" devX {l['max_dev_X']}")
        if not it["localised"]:
            print("  국소화된 결함 없음 — 두 팔의 카메라가 전부 보행면 위")
        print("\n  --- 짝 기준: 카메라 스트립 자체의 D팔 중앙값 ---")
        for r in out["rows"]:
            i = r.get("instrument") or {}
            if "strip_verdict" not in i:
                continue
            if i["strip_verdict"] == "instr_exact" and i["verdict"] == "instr_exact":
                continue
            print(f"  {r['scene']}/{r['band']}: strip walk_z {i['walk_z_strip']}"
                  f" (링과 {i.get('ring_vs_strip_m')} m 차) · {i['strip_tiers']}"
                  f" · devA {i.get('strip_max_dev_A')} devX "
                  f"{i.get('strip_max_dev_X')} · {i['strip_verdict']}")
    print(f"\n-> {a.out}")


if __name__ == "__main__":
    main()
