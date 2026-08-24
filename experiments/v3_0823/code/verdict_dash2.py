#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verdict_dash2.py — 계기판 ② CUE-OFF 용량-반응 (PREREG §2.2 · CPU 전용)

**재는 양**: 단서를 끌 때 오경보가 **단서 개수**를 따르는가, 화면의 **광학 변화량**을
따르는가. 두 회귀 기울기를 함께 인쇄하고 **어느 쪽이 지배하는가**를 판정한다.

  · 무대  = test-ext 4팔 (PREREG §2.2 무대 행 · AC §2-9)
  · 쌍    = **(A,B)** (AC §2-2) — A = 위험 ON·단서 기본값 / B = 위험 ON·`cue_*` 최대 제거
  · 모집단 = 프레임 수준에서 **양 팔 모두 strict-H 인 paired 프레임**만.
             단위(= 씬 × 밴드)별 `n_paired` **하한 10** — 미달 단위는 VOID 로 인쇄만.
  · 운용점 = τ_op 0.5(참고) + FA-정합 이중축 8점 (기울기는 **운용점마다** 산출)
  · 부호   = 광학 변화량 추종 기울기 **↓** ∧ 단서 개수 추종 기울기 **↑** (§3.4 ②)
  · v2 쪽  = **여기서 돌릴 수 없다** (PREREG §2.2 주의 · V2_TEXTEXT_BASELINE §4).
             v2 기준점은 등록된 원장 행을 인용만 한다 → `v2_reference` 블록.

**단서 개수의 정의 (§2.2)**: "A팔 대비 B팔의 단서 개수는 §4.4 VG-09 의 키별 r 원장과
**같은 정의**를 쓴다(별도 계수 금지)" ⇒ 정본 6키 R·Ta·N·T·Sg·V 의 프림 픽셀 귀속
원장(`logs/cue_extent_frames.json`)에서 **A 에 있고 B 에 없는 키의 수**를 센다.
**T(cue_material_break)는 면적 계기가 원리적으로 못 보는 키**(재질 재바인딩)이므로
`declared` 레버 수를 함께 인쇄한다 — 두 수를 같은 칸에 넣지 않는다.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
V3 = os.path.join(REPO, "experiments", "v3_0823")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "experiments", "mainrun_0819", "code"))

import gridspec                    # noqa: E402
import v2_textext_tables as T2     # noqa: E402

KEYS6 = ("R", "Ta", "N", "T", "Sg", "V")
CUE2KEY = {"cue_railing": "R", "cue_tactile": "Ta", "cue_nosing": "N",
           "cue_material_break": "T", "cue_sign": "Sg", "cue_scene_dressing": "V"}
RUNS = ["rgb_s42", "rgb_s43", "rgb_s44"]
AUX = ["rgb_s42_aux"]
N_PAIRED_FLOOR = 10                # PREREG §2.2 판정 모집단
FRAME_PX = 1920 * 1080

# 등록된 v2 기준점 — 인용만 한다 (PREREG §2.2 v2 기준점 행 · ab_table_shells §2.4)
V2_REFERENCE = dict(
    headline="광학 질량 추종 (scene17 역설)",
    dose_rows=[dict(optical_pct=58.35, fa=1.000), dict(optical_pct=36.60, fa=1.000),
               dict(optical_pct=13.09, fa=0.361), dict(optical_pct=1.02, fa=0.042)],
    grid_fixed_slope_range=[-0.058, 0.387],
    dressing_lift=[1.01, 0.98],
    census="primary leg · 전 블록 30칸 중 판정 가능 12칸 (40.0 %) · 접음 21칸 중 9 (42.9 %)",
    cue_evidence=0,
    caveat=("v2 개입은 판정 후 **유효 씬 1개(s17)** 였고, 병목은 strict-H 가용성이지 "
            "토글 배선이 아니었다. v2 팔에서 '단서'와 '화면의 1/3'은 완전 교락돼 있었다."),
    why_no_v2_arm=("PREREG §2.2 주의 · V2_TEXTEXT_BASELINE §4 — ② 는 v2 위에서 돌릴 수 "
                   "없으므로 **v3 단독 절대값 + 층별 기울기**로 보고한다(등록된 처분)."),
)


# ---------------------------------------------------------------- ledgers
def cue_ledger():
    """(round, scene, stem) -> {key: px}  — VG-09 키별 r 원장과 같은 계기."""
    p = os.path.join(V3, "logs", "cue_extent_frames.json")
    d = json.load(open(p, encoding="utf-8"))
    out = {}
    for r in d["probe"] + d["corpus"]:
        out[(r["round"], r["scene"], r["stem"])] = r
    return out


def declared_levers():
    """run_w3_text.sh 의 B팔 레시피 — **선언된** 제거 키 (T 포함)."""
    sh = open(os.path.join(HERE, "run_w3_text.sh"), encoding="utf-8").read()
    common = re.search(r"COMMON12='([^']*)'", sh).group(1)
    out = {}
    for m in re.finditer(r"^(H1|H2|H3|L1|N9|N11)_OFF=\"\$COMMON12\"'([^']*)'", sh, re.M):
        scene = "scene" + m.group(1)
        keys = set()
        for blob in (common, m.group(2)):
            for c in re.findall(r'"(cue_[a-z_]+)"\s*:\s*false', blob):
                keys.add(c)
        out[scene] = keys
    return out


def optical_ab(pairs, workers=12):
    """(scene,band,stem) -> mean|ΔI| · frac(|ΔI|>8) · frac(|ΔI|>32)  — A↔B."""
    import build_corpus_v3 as BC
    cache_p = os.path.join(V3, "logs", "verdict_optical_ab.json")
    cache = {}
    if os.path.exists(cache_p):
        cache = json.load(open(cache_p, encoding="utf-8")).get("pairs", {})
    todo = {k: v for k, v in pairs.items() if "|".join(k) not in cache}
    if todo:
        from concurrent.futures import ProcessPoolExecutor
        keys = list(todo)
        print(f"[optical] (A,B) {len(keys)}쌍 측정 …")
        with ProcessPoolExecutor(max_workers=workers) as ex:
            for k, (r, err) in zip(keys, ex.map(BC._optical_one,
                                                [todo[k] for k in keys], chunksize=8)):
                if r:
                    cache["|".join(k)] = r
        json.dump(dict(doc="verdict_optical_ab",
                       predicate="같은 계기 (그레이스케일 2x2 서브샘플, |ΔI| 0-255)",
                       pairs=cache), open(cache_p, "w", encoding="utf-8"),
                  ensure_ascii=False)
    return {tuple(k.split("|")): v for k, v in cache.items()}


# ---------------------------------------------------------------- stats
def ols(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    if len(x) < 3 or np.allclose(x, x[0]):
        return dict(n=int(len(x)), slope=None, intercept=None, r2=None, r=None,
                    slope_std=None, reason=("n<3" if len(x) < 3 else "x 상수(퇴화)"))
    b, a = np.polyfit(x, y, 1)
    yh = a + b * x
    ss = float(((y - y.mean()) ** 2).sum())
    r2 = float(1 - ((y - yh) ** 2).sum() / ss) if ss > 0 else None
    r = float(np.corrcoef(x, y)[0, 1]) if (x.std() > 0 and y.std() > 0) else None
    sx, sy = float(x.std(ddof=1)), float(y.std(ddof=1))
    return dict(n=int(len(x)), slope=float(b), intercept=float(a), r2=r2, r=r,
                slope_std=(float(b) * sx / sy if sy > 0 else None),
                x_mean=float(x.mean()), y_mean=float(y.mean()))


def agg(v):
    v = [x for x in v if x is not None and np.isfinite(x)]
    if not v:
        return dict(mean=None, sd=None, n=0)
    a = np.asarray(v, float)
    return dict(mean=float(a.mean()), sd=(float(a.std(ddof=1)) if len(a) > 1 else 0.0),
                n=len(a), vals=[float(x) for x in a])


# ---------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval-dir", default=os.path.join(V3, "eval_v3a_textext"))
    ap.add_argument("--out", default=os.path.join(V3, "verdict_dash2.json"))
    a = ap.parse_args(argv)

    grid = gridspec.load("gridspec_v1.json")
    man_ac = json.load(open(os.path.join(V3, "dataset_manifest_v3_textext.json"),
                            encoding="utf-8"))
    man_bd = json.load(open(os.path.join(V3, "dataset_manifest_v3_textext_bd.json"),
                            encoding="utf-8"))
    rounds_ac = man_ac["meta"]["band_rounds"]
    rounds_bd = man_bd["meta"]["band_rounds"]
    a_path = {(f["band_round"], f["scene_id"],
               os.path.basename(f["rgb"])[:-4]): f["rgb"]
              for f in man_ac["frames"] if f["toggle_state"] == "on"}
    b_path = {(f["band_round"], f["scene_id"],
               os.path.basename(f["rgb"])[:-4]): f["rgb"]
              for f in man_bd["frames"] if f["toggle_state"] == "on"}
    pairs = {k: (a_path[k], b_path[k]) for k in a_path if k in b_path}
    OPT = optical_ab(pairs)
    CUE = cue_ledger()
    DECL = declared_levers()

    # ---- 팔별 단서 키 존재 (정본 6키 · 프림 픽셀 원장) ----------------------
    def keys_present(band, scene, stem, arm):
        rnd = (rounds_ac if arm in ("A", "C") else rounds_bd)[band]
        rnd = rnd["on"] if arm in ("A", "B") else rnd["off"]
        r = CUE.get((rnd, scene, stem))
        if r is None:
            return None
        return {k for k in KEYS6 if int((r.get("area") or {}).get(k, 0)) > 0}

    # ---- 계기판 무대 재채점 덤프 -------------------------------------------
    out_runs = {}
    unit_static = {}
    for run in RUNS + AUX:
        ac = T2.read_pf(os.path.join(a.eval_dir, run, "per_frame.csv"), grid)
        bd = T2.read_pf(os.path.join(a.eval_dir, run, "bd", "per_frame.csv"), grid)
        A_map, A_idx = T2.arm_view(ac, "on")
        B_map, B_idx = T2.arm_view(bd, "on")
        D_map, D_idx = T2.arm_view(bd, "off")

        paired = [k for k, i in A_map.items()
                  if ac["tier"][i] == "H" and k in B_map and bd["tier"][B_map[k]] == "H"]
        by_unit = defaultdict(list)
        for k in paired:
            by_unit[(k[1], k[0])].append(k)          # (scene, band)

        # 운용점 — v3 런의 D팔 덤프에서 다시 잡는다 (PREREG §2.1 절차)
        dfs = bd["probs"][D_idx].max(1)
        dcs = bd["probs"][D_idx].ravel()
        ops = [dict(name="tau_op", axis="ref", tau=0.5)]
        for t in T2.FRAME_TARGETS:
            tau, ach = T2.tau_for_target(dfs, t)
            ops.append(dict(name=f"F@{t:.3f}", axis="frame", target=t, tau=tau, achieved=ach))
        for t in T2.CELL_TARGETS:
            tau, ach = T2.tau_for_target(dcs, t)
            ops.append(dict(name=f"C@{t:.6f}", axis="cell", target=t, tau=tau, achieved=ach))

        rows = []
        for op in ops:
            tau = op["tau"]
            urows = []
            for (scene, band), keys in sorted(by_unit.items()):
                n_paired = len(keys)
                fa_a_fr = fa_b_fr = 0
                nz_a = nz_b = fz_a = fz_b = 0
                opt_m, opt8, opt32, ncue, ndecl = [], [], [], [], []
                for k in keys:
                    stem = k[2][:-4] if k[2].endswith(".png") else k[2]
                    ia, ib = A_map[k], B_map[k]
                    neg = ~(ac["gt"][ia] > 0.5)          # A·B 는 GT 동일 (VG-01)
                    fa = ac["probs"][ia] >= tau
                    fb = bd["probs"][ib] >= tau
                    fa_a_fr += int((fa & neg).any()); fa_b_fr += int((fb & neg).any())
                    nz_a += int(neg.sum()); nz_b += int(neg.sum())
                    fz_a += int((fa & neg).sum()); fz_b += int((fb & neg).sum())
                    o = OPT.get((band, scene, stem))
                    if o:
                        opt_m.append(o["mean_abs"]); opt8.append(o["frac_gt8"])
                        opt32.append(o["frac_gt32"])
                    ka = keys_present(band, scene, stem, "A")
                    kb = keys_present(band, scene, stem, "B")
                    if ka is not None and kb is not None:
                        ncue.append(len(ka - kb))
                    ndecl.append(len(DECL.get(scene, set()) & set(CUE2KEY)))
                urows.append(dict(
                    scene=scene, band=band, n_paired=n_paired,
                    void=(n_paired < N_PAIRED_FLOOR),
                    void_reason=(f"n_paired {n_paired} < {N_PAIRED_FLOOR}"
                                 if n_paired < N_PAIRED_FLOOR else None),
                    cue_count_removed=(float(np.mean(ncue)) if ncue else None),
                    cue_count_declared=(float(np.mean(ndecl)) if ndecl else None),
                    optical_mean_abs=(float(np.mean(opt_m)) if opt_m else None),
                    optical_frac_gt8=(float(np.mean(opt8)) if opt8 else None),
                    optical_frac_gt32=(float(np.mean(opt32)) if opt32 else None),
                    fa_frame_A=fa_a_fr / n_paired, fa_frame_B=fa_b_fr / n_paired,
                    fa_cell_A=(fz_a / nz_a if nz_a else None),
                    fa_cell_B=(fz_b / nz_b if nz_b else None),
                    d_fa_frame=(fa_b_fr - fa_a_fr) / n_paired,
                    d_fa_cell=((fz_b - fz_a) / nz_a if nz_a else None),
                ))
            live = [u for u in urows if not u["void"]]
            reg = {}
            for yname in ("fa_frame_B", "fa_cell_B", "d_fa_frame", "d_fa_cell"):
                y = [u[yname] for u in live]
                reg[yname] = dict(
                    vs_cue_count=ols([u["cue_count_removed"] for u in live], y),
                    vs_optical_mean=ols([u["optical_mean_abs"] for u in live], y),
                    vs_optical_frac32=ols([u["optical_frac_gt32"] for u in live], y),
                )
            # --- 비등록 보조: 프레임 수준 회귀 (판정 불사용 · 검정력 참고용) ---
            fx1, fx2, fy = [], [], []
            for (scene, band), kk in sorted(by_unit.items()):
                if len(kk) < N_PAIRED_FLOOR:
                    continue
                for k in kk:
                    stem = k[2][:-4] if k[2].endswith(".png") else k[2]
                    ib = B_map[k]
                    neg = ~(ac["gt"][A_map[k]] > 0.5)
                    o = OPT.get((band, scene, stem))
                    ka = keys_present(band, scene, stem, "A")
                    kb = keys_present(band, scene, stem, "B")
                    if o is None or ka is None or kb is None:
                        continue
                    fx1.append(len(ka - kb)); fx2.append(o["mean_abs"])
                    fy.append(float(((bd["probs"][ib] >= tau) & neg).any()))
            companion = dict(n=len(fy),
                             vs_cue_count=ols(fx1, fy), vs_optical_mean=ols(fx2, fy),
                             note="비등록 보조 — 프레임 단위. 판정에 쓰지 않는다.")
            rows.append(dict(op=op, units=urows, n_units=len(urows),
                             n_units_live=len(live), reg=reg, companion_frame=companion))
        out_runs[run] = dict(ops=rows, n_paired_total=len(paired),
                             units={f"{s}|{b}": len(v) for (s, b), v in sorted(by_unit.items())})
        if not unit_static:
            unit_static = {f"{u['scene']}|{u['band']}": {
                k: u[k] for k in ("n_paired", "void", "void_reason", "cue_count_removed",
                                  "cue_count_declared", "optical_mean_abs",
                                  "optical_frac_gt8", "optical_frac_gt32")}
                for u in rows[0]["units"]}
        print(f"  [{run}] paired-H(A∧B) {len(paired)} · 단위 {len(rows[0]['units'])} "
              f"(유효 {rows[0]['n_units_live']})")

    # ---- 3시드 집계 --------------------------------------------------------
    summary = {}
    for arm, rr in (("v3a_rgb", RUNS), ("v3a_rgb_aux_isolated", AUX)):
        rs = [out_runs[r] for r in rr if r in out_runs]
        if not rs:
            continue
        agg_ops = []
        for i in range(len(rs[0]["ops"])):
            e = dict(op=rs[0]["ops"][i]["op"]["name"],
                     axis=rs[0]["ops"][i]["op"]["axis"],
                     tau=agg([r["ops"][i]["op"]["tau"] for r in rs]),
                     n_units_live=rs[0]["ops"][i]["n_units_live"])
            for yname in ("fa_frame_B", "fa_cell_B", "d_fa_frame", "d_fa_cell"):
                for xname in ("vs_cue_count", "vs_optical_mean", "vs_optical_frac32"):
                    for stat in ("slope", "r2", "r", "slope_std"):
                        e[f"{yname}|{xname}|{stat}"] = agg(
                            [r["ops"][i]["reg"][yname][xname][stat] for r in rs])
            # 지배 판정 — |표준화 기울기| 비교 (같은 단위로 놓기)
            dom = []
            for r in rs:
                c = r["ops"][i]["reg"]["fa_frame_B"]["vs_cue_count"]["slope_std"]
                o = r["ops"][i]["reg"]["fa_frame_B"]["vs_optical_mean"]["slope_std"]
                dom.append(None if (c is None or o is None)
                           else ("cue_count" if abs(c) > abs(o) else "optical_mass"))
            e["dominant_fa_frame_B"] = dom
            for xn in ("vs_cue_count", "vs_optical_mean"):
                for st in ("slope", "r2", "r", "slope_std"):
                    e[f"companion|{xn}|{st}"] = agg(
                        [r["ops"][i]["companion_frame"][xn][st] for r in rs])
            e["companion_n"] = rs[0]["ops"][i]["companion_frame"]["n"]
            e["unit_values"] = {f"{u['scene']}|{u['band']}":
                                agg([r["ops"][i]["units"][j]["fa_frame_B"] for r in rs])
                                for j, u in enumerate(rs[0]["ops"][i]["units"])}
            agg_ops.append(e)
        summary[arm] = dict(runs=[r for r in rr if r in out_runs], ops=agg_ops)

    doc = dict(doc="계기판 ② CUE-OFF 용량-반응 — v3-A 단독 (PREREG §2.2)",
               stage="test-ext 4팔", pair="(A,B)",
               population=(f"양 팔 모두 strict-H 인 paired 프레임 · 단위 = (씬 × 밴드) · "
                           f"n_paired 하한 {N_PAIRED_FLOOR}"),
               cue_count_definition=("정본 6키(R·Ta·N·T·Sg·V) 프림 픽셀 원장에서 "
                                     "A 에 있고 B 에 없는 키 수 (logs/cue_extent_frames.json). "
                                     "T 는 재질 재바인딩이라 면적 계기가 원리적으로 못 본다 "
                                     "⇒ declared 레버 수를 별도 열로 병기."),
               optical_definition="그레이스케일 |ΔI| (0-255) · mean · frac(>8) · frac(>32)",
               direction="광학 변화량 기울기 ↓ ∧ 단서 개수 기울기 ↑ (PREREG §3.4 ②)",
               v2_reference=V2_REFERENCE, unit_static=unit_static,
               per_run=out_runs, summary=summary)
    json.dump(doc, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[out] {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
