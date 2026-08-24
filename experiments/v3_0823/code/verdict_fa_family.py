#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verdict_fa_family.py — V-3 이행 · step 2
**계기판② FA 5가족 층화** (PREREG §2.2 「층화」행 · P-12) 를 **test-ext 무대**에서
v2(9런) · v3-A(3런) 양 세대에 대해 산출한다.

등록 문면 (PREREG §2.2)
  「층화 | FA 5가족 {장식·지형통계·조명·대리선·경계칸}, 경계칸형의 **방사 절반**만
   지형통계형 하위 서명으로 접는다 `[해소: P-12]`」

무대·단위·층
  · 1 FA 사건 = (세대, 런, **팔**, 프레임, 칸) — `score ≥ τ_op(0.5)` ∧ `GT == 0`
  · 층 = **팔**. B·C·D 를 **절대 합산하지 않는다**(분모·의미가 다르다). A 는 참고행.
      C = 단서 O · 위험 X (FA_C)   D = 단서 X · 위험 X (FA_D)
      B = 단서 X · 위험 O (GT 음성칸만)  A = 단서 O · 위험 O (GT 음성칸만 · 참고)
  · 세대 비교는 **rgb 대 rgb (3런 대 3런)**. v2 9런 풀링은 별도 블록으로만 인쇄한다
    — 9런과 3런을 같은 칸에 넣으면 노출이 3배 차이 나는 수를 비교하게 된다.

가족 규칙 (test-core 센서스 `FA_CENSUS §3.1` 의 이식 · 방법 태그 유지)
  경계칸형  [기계]      band == '3b' OR sector ∈ {A,E}  (반경/방위 성분 분해 보고)
  조명형    [휴리스틱]  칸 lum_median < 0.60 × 프레임 lum_median  (0.50/0.70 병기)
  대리선형  [휴리스틱]  칸 line_frac ≥ P90(**test-ext 가시칸 분포**, 재산출)
                        GT 양성칸 인접 시 제외(A·B팔만 해당) → `surrogate_weak`
  지형통계형 [기계]+[휴리스틱] unseen(가시화소 0) OR prior_saturated(그 씬 프레임의 ≥80 %)
  장식형    **[기계·이식판]** 칸의 설치-단서 프림 화소 ≥ 20 (DS4 화소 = 원본 320화소)
            ← test-core 는 `[수동]` 2씬 오버레이였다. **계측기가 다르므로 두 무대의
              장식형 수치를 나란히 놓지 않는다.** 근거 = VG-09 키별 r 원장과 같은 귀속기.

P-12 접기 (등록 정본)
  지형통계형⁺ = 지형통계형 ∪ **경계칸 반경 성분(band 3b)**
  경계칸형⁻   = **방위 성분(sector A/E)만**
  원 5가족(접기 전)도 같은 표에 병기한다.

출력 experiments/v3_0823/verdict_fa_family.json
     experiments/v3_0823/fa_events_textext.csv
CPU 전용 · 재추론 0 · 재렌더 0 · GPU 0 · git 무접촉.
"""
from __future__ import annotations

import csv
import json
import os
import sys
from collections import Counter, defaultdict
from itertools import combinations

import numpy as np

ROOT = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V3 = os.path.join(ROOT, "experiments/v3_0823")
GRIDSPEC = os.path.join(ROOT, "experiments/mainrun_0819/code/labeling/gridspec_v1.json")
PHOTO = os.path.join(V3, "cell_photometry_textext.csv")
OUTJSON = os.path.join(V3, "verdict_fa_family.json")
OUTCSV = os.path.join(V3, "fa_events_textext.csv")
DATE = "2026-08-24"

LIGHT_RATIO = 0.60
LIGHT_SENS = (0.50, 0.70)
SAT_RATE = 0.80
DECO_PX = 20                       # DS4 화소 (원본 320화소)
DECO_SENS = (5, 80)
TAU_EXPECTED = 0.5

# 세대 × 런 등록부.  aux 는 §8 격리 런 — **판정·표 미산입**, 별도 블록.
GEN = {
    "v2": dict(dir=os.path.join(V3, "eval_v3textext"),
               runs=[f"{m}_s{s}" for m in ("rgb", "depth", "b2") for s in (42, 43, 44)],
               label="v2 (9런)"),
    "v3a": dict(dir=os.path.join(V3, "eval_v3a_textext"),
                runs=[f"rgb_s{s}" for s in (42, 43, 44)],
                label="v3-A (3런)"),
}
AUX = ("v3a", "rgb_s42_aux")
ARMS = ("A", "B", "C", "D")
JUDGE_ARMS = ("B", "C", "D")       # 과업 등록 층 — 용량-반응 축
FAMS = ("장식형", "지형통계형", "조명형", "대리선형", "경계칸형")
FAMKEY = dict(장식형="deco", 지형통계형="terr", 조명형="light",
              대리선형="surr", 경계칸형="bnd")
# 배타 귀속 우선순위 — **결과를 보기 전에 고정**한다.  더 구체적·내용적인 가족이
# 더 일반적·기하학적인 가족을 이긴다(경계/지형은 규칙상 격자의 절반 이상을 칠한다).
PRIORITY = ("장식형", "대리선형", "조명형", "지형통계형", "경계칸형")

G = json.load(open(GRIDSPEC))
NS = G["n_sectors"]
BANDS, SECTORS = G["band_names"], G["sector_names"]
CELL_IDS = [f"{s}{b}" for b in BANDS for s in SECTORS]
BI = {b: i for i, b in enumerate(BANDS)}
SI = {s: i for i, s in enumerate(SECTORS)}
EDGE_SECTORS = {SECTORS[0], SECTORS[-1]}
OUTER_BAND = BANDS[-1]


def adjacent(c1, c2):
    """[복사: fa_census_analyze.py L66-70] (밴드,섹터) 격자 4근방 · 자기 자신 포함."""
    return abs(BI[c1[1:]] - BI[c2[1:]]) + abs(SI[c1[0]] - SI[c2[0]]) <= 1


def mean_sd(xs):
    xs = [float(x) for x in xs]
    if not xs:
        return None, None
    m = float(np.mean(xs))
    s = float(np.std(xs, ddof=1)) if len(xs) > 1 else 0.0
    return m, s


# ---------------------------------------------------------------- 원장 읽기
def load_photo():
    ph = {}
    for r in csv.DictReader(open(PHOTO)):
        ph[(r["arm"], r["frame_id"], r["cell"])] = r
    return ph


def dump_rows(gen, run):
    """한 런의 4팔 행.  AC 덤프 on=A/off=C · BD 덤프 on=B/off=D."""
    d = os.path.join(GEN[gen]["dir"], run)
    out = {}
    for sub, (on_arm, off_arm) in (("", ("A", "C")), ("bd", ("B", "D"))):
        base = os.path.join(d, sub) if sub else d
        mj = json.load(open(os.path.join(base, "metrics.json")))
        rows = list(csv.DictReader(open(os.path.join(base, "per_frame.csv"))))
        out[(on_arm, off_arm)] = (mj, rows)
    return out


# ---------------------------------------------------------------- 사건 추출
def extract(ph):
    """FA 사건 + 팔별 검산.  반환 (events, recon, gt, frames_of)."""
    events, recon = [], {}
    gt = {}                       # (arm, frame_id) -> set(GT 양성칸)
    frames_of = defaultdict(set)  # (arm, scene) -> frames
    meta_rows = {}                # (arm, frame_id) -> row meta

    for gen, cfg in GEN.items():
        runs = list(cfg["runs"]) + ([AUX[1]] if gen == AUX[0] else [])
        for run in runs:
            model = run.split("_s")[0]
            seed = run.split("_s")[1]
            for (on_arm, off_arm), (mj, rows) in dump_rows(gen, run).items():
                tau = float(mj["tau_op"])
                assert abs(tau - TAU_EXPECTED) < 1e-12, (run, on_arm, tau)
                cnt = dict(off_frames=0, off_fired_frames=0, off_fired_cells=0,
                           off_cells=0, off_gt_nonzero=0,
                           on_frames=0, on_neg_cells=0, on_neg_fired=0)
                for r in rows:
                    arm = off_arm if r["toggle_state"] == "off" else on_arm
                    fid, sc, tier = r["frame_id"], r["scene_id"], r["tier"]
                    pos = {c for c in CELL_IDS if int(r["g_" + c])}
                    k = (arm, fid)
                    if k in gt:
                        assert gt[k] == pos, f"GT drift {k} {run}"
                    gt[k] = pos
                    frames_of[(arm, sc)].add(fid)
                    meta_rows[k] = dict(scene_id=sc, tier=tier)
                    fired_any = False
                    for cid in CELL_IDS:
                        p = float(r["p_" + cid])
                        g = int(r["g_" + cid])
                        if arm == off_arm:
                            cnt["off_cells"] += 1
                            cnt["off_gt_nonzero"] += (g != 0)
                            if p >= tau:
                                fired_any = True
                                cnt["off_fired_cells"] += 1
                        else:
                            if g == 0:
                                cnt["on_neg_cells"] += 1
                                cnt["on_neg_fired"] += (p >= tau)
                        if p >= tau and g == 0:
                            events.append(dict(
                                gen=gen, run=run, model=model, seed=seed, arm=arm,
                                frame_id=fid, scene_id=sc, tier=tier,
                                band_round=ph[(arm, fid, cid)]["band_round"],
                                cell=cid, sector=cid[0], band=cid[1:],
                                score=round(p, 6)))
                    if arm == off_arm:
                        cnt["off_frames"] += 1
                        cnt["off_fired_frames"] += fired_any
                    else:
                        cnt["on_frames"] += 1
                pub = mj["point"]["op"]
                rc = dict(tau_op=tau, arm_off=off_arm, arm_on=on_arm, **cnt)
                rc["recount_frame_fa_off"] = cnt["off_fired_frames"] / cnt["off_frames"]
                rc["recount_cell_fpr_off"] = cnt["off_fired_cells"] / cnt["off_cells"]
                rc["recount_cell_fpr_on_neg"] = (cnt["on_neg_fired"] /
                                                 cnt["on_neg_cells"])
                for kk in ("frame_fa_off", "cell_fpr_off", "cell_fpr_on_neg"):
                    rc["pub_" + kk] = pub[kk]
                    rc["match_" + kk] = abs(rc["recount_" + kk] - pub[kk]) < 1e-9
                recon[f"{gen}|{run}|{on_arm}{off_arm}"] = rc
    return events, recon, gt, frames_of, meta_rows


# ---------------------------------------------------------------- 가족 분류
def classify(events, ph, gt, frames_of):
    vis_lf = [float(r["line_frac"]) for r in ph.values()
              if int(r["n_px"]) > 0 and r["line_frac"] != ""]
    P90 = float(np.percentile(vis_lf, 90))
    P75 = float(np.percentile(vis_lf, 75))
    P95 = float(np.percentile(vis_lf, 95))

    # prior-saturation: 세대 × 모델 × 팔 × 씬 × 칸, 시드 다수결(≥2/3) 위에서
    cnt_ms = defaultdict(Counter)
    for e in events:
        if e["run"] == AUX[1]:
            continue
        cnt_ms[(e["gen"], e["model"])][(e["arm"], e["frame_id"], e["cell"])] += 1
    major = {k: {kk for kk, v in c.items() if v >= 2} for k, c in cnt_ms.items()}
    fire = Counter()
    for (gen, model), S in major.items():
        for arm, fid, cell in S:
            sc = None
            for (a, s), fs in frames_of.items():
                if a == arm and fid in fs:
                    sc = s
                    break
            fire[(gen, model, arm, sc, cell)] += 1
    satur = set()
    for k, n in fire.items():
        gen, model, arm, sc, cell = k
        den = len(frames_of[(arm, sc)])
        if den and n / den >= SAT_RATE:
            satur.add(k)

    out = []
    for e in events:
        arm, fid, cell = e["arm"], e["frame_id"], e["cell"]
        p = ph[(arm, fid, cell)]
        n_px = int(p["n_px"])
        unseen = n_px == 0
        lum, fl = p["lum_median"], p["frame_lum_median_all"]
        ratio = (float(lum) / float(fl)) if (lum and fl and float(fl) > 0) else None
        lf = float(p["line_frac"]) if p["line_frac"] else None
        deco_px = int(p["cue_px_install"])

        bnd_band = e["band"] == OUTER_BAND
        bnd_sector = e["sector"] in EDGE_SECTORS
        f_bnd = bnd_band or bnd_sector
        f_light = bool(ratio is not None and ratio < LIGHT_RATIO)
        line_hit = bool(lf is not None and lf >= P90)
        bleed = any(adjacent(cell, q) for q in gt[(arm, fid)])
        f_surr = line_hit and not bleed
        f_deco = deco_px >= DECO_PX
        sat = (e["gen"], e["model"], arm, e["scene_id"], cell) in satur
        f_terr = unseen or sat

        fams = [f for f, v in (("장식형", f_deco), ("지형통계형", f_terr),
                               ("조명형", f_light), ("대리선형", f_surr),
                               ("경계칸형", f_bnd)) if v]
        # P-12 접기
        f_terr_p12 = f_terr or bnd_band
        f_bnd_p12 = bnd_sector
        fams_p12 = [f for f, v in (("장식형", f_deco), ("지형통계형", f_terr_p12),
                                   ("조명형", f_light), ("대리선형", f_surr),
                                   ("경계칸형", f_bnd_p12)) if v]
        methods = []
        if f_bnd:
            methods.append("기계")
        if f_terr and unseen:
            methods.append("기계")
        if f_deco:
            methods.append("기계")
        if f_light or f_surr or (f_terr and not unseen):
            methods.append("휴리스틱")
        method = "+".join(dict.fromkeys(methods)) or "미분류"

        prim = next((f for f in PRIORITY if f in fams_p12), "미분류")
        out.append(dict(
            **e, n_px=n_px, unseen=int(unseen),
            lum_ratio=(round(ratio, 4) if ratio is not None else ""),
            line_frac=(round(lf, 4) if lf is not None else ""),
            cue_px_install=deco_px, cue_px_ground=int(p["cue_px_ground"]),
            cue_px_shadow=int(p["cue_px_shadow"]),
            fam_deco=int(f_deco), fam_terr=int(f_terr), fam_light=int(f_light),
            fam_surr=int(f_surr), fam_bnd=int(f_bnd),
            fam_terr_p12=int(f_terr_p12), fam_bnd_p12=int(f_bnd_p12),
            bnd_band=int(bnd_band), bnd_sector=int(bnd_sector),
            bnd_corner=int(bnd_band and bnd_sector),
            surrogate_weak=int(line_hit and bleed),
            light_50=int(ratio is not None and ratio < LIGHT_SENS[0]),
            light_70=int(ratio is not None and ratio < LIGHT_SENS[1]),
            deco_5=int(deco_px >= DECO_SENS[0]), deco_80=int(deco_px >= DECO_SENS[1]),
            prior_saturated=int(sat),
            n_families=len(fams_p12), families="|".join(fams_p12),
            families_raw="|".join(fams), primary=prim, method=method))
    return out, dict(LINE_P90=round(P90, 4), LINE_P75=round(P75, 4),
                     LINE_P95=round(P95, 4))


# ---------------------------------------------------------------- 노출 원장
def exposure(ph, gt, P90):
    """팔 × 칸의 **위험 노출** 원장 + 정적 가족 소속 (세대 무관).

    prior_saturated 는 모델의 거동이라 노출 쪽 짝이 없다 — 지형통계형의 lift 는
    test-core 센서스와 같이 **unseen 성분만**으로 잰다(접기판은 unseen ∪ 3b).
    """
    risk = defaultdict(list)
    for (arm, fid, cell), p in ph.items():
        pos = gt.get((arm, fid))
        if pos is None or cell in pos:
            continue                                   # GT 양성칸은 노출 아님
        n_px = int(p["n_px"])
        lum, fl = p["lum_median"], p["frame_lum_median_all"]
        ratio = (float(lum) / float(fl)) if (lum and fl and float(fl) > 0) else None
        lf = float(p["line_frac"]) if p["line_frac"] else None
        bleed = any(adjacent(cell, q) for q in pos)
        bb = cell[1:] == OUTER_BAND
        bs = cell[0] in EDGE_SECTORS
        risk[arm].append(dict(
            frame_id=fid, cell=cell, scene=p["scene_id"], tier=p["tier"],
            deco=int(int(p["cue_px_install"]) >= DECO_PX),
            terr=int(n_px == 0), light=int(ratio is not None and ratio < LIGHT_RATIO),
            surr=int(lf is not None and lf >= P90 and not bleed),
            bnd=int(bb or bs), bnd_band=int(bb), bnd_sector=int(bs),
            terr_p12=int((n_px == 0) or bb), bnd_p12=int(bs)))
    return risk


# ---------------------------------------------------------------- 표
def main():
    ph = load_photo()
    events, recon, gt, frames_of, _meta = extract(ph)
    ev, params = classify(events, ph, gt, frames_of)
    params.update(LIGHT_RATIO=LIGHT_RATIO, LIGHT_SENS=list(LIGHT_SENS),
                  DECO_PX=DECO_PX, DECO_SENS=list(DECO_SENS), SAT_RATE=SAT_RATE,
                  tau_op=TAU_EXPECTED, outer_band=OUTER_BAND,
                  edge_sectors=sorted(EDGE_SECTORS), priority=list(PRIORITY))
    risk = exposure(ph, gt, params["LINE_P90"])

    with open(OUTCSV, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(ev[0].keys()))
        w.writeheader()
        w.writerows(ev)

    T = dict(
        doc="계기판② FA 5가족 층화 (V-3 이행) — test-ext 4팔 · v2 9런 / v3-A 3런",
        obligation="PREREG_V3 §2.2 「층화」행 · P-12 · VERDICT_V3 §13 V-3",
        stage="test-ext (평가 전용 4팔) · 576+576 컷 · 학습 미노출",
        unit="1 FA 사건 = (세대, 런, 팔, 프레임, 칸) · score ≥ τ_op 0.5 ∧ GT == 0",
        strata="팔 = 층. B·C·D 절대 합산 금지. A 는 참고행(판정 미산입).",
        generations_comparable="rgb 대 rgb (3런 대 3런). v2 9런 풀링은 별도 블록.",
        date=DATE, params=params, recon=recon)

    # ---- 검산 요약 -------------------------------------------------------
    KEYS3 = ("match_frame_fa_off", "match_cell_fpr_off", "match_cell_fpr_on_neg")
    n_ok = sum(bool(r[k]) for r in recon.values() for k in KEYS3)
    T["recon_summary"] = dict(
        n_dumps=len(recon),
        n_mismatch=sum(1 for r in recon.values()
                       if not all(r[k] for k in KEYS3)),
        off_gt_nonzero_total=sum(r["off_gt_nonzero"] for r in recon.values()),
        n_checks=3 * len(recon), n_checks_matched=n_ok)

    # ---- 노출 분모 -------------------------------------------------------
    T["exposure"] = {}
    for a in ARMS:
        R = risk[a]
        T["exposure"][a] = dict(
            n_cells=len(R), n_frames=len(R) // 20 if len(R) % 20 == 0 else None,
            **{f"n_{k}": sum(r[k] for r in R) for k in
               ("deco", "terr", "light", "surr", "bnd", "bnd_band", "bnd_sector",
                "terr_p12", "bnd_p12")})

    # ---- 표 A: 가족 × 팔 × 세대 (물량 · 몫 · lift · 노출정규화 발화율) ----
    def block(sel_runs, gen, tag):
        o = {}
        nrun = len(sel_runs)
        for a in ARMS:
            R = risk[a]
            nR = len(R)
            sel = [e for e in ev if e["gen"] == gen and e["run"] in sel_runs
                   and e["arm"] == a]
            nE = len(sel)
            row = dict(n_runs=nrun, n_events=nE, n_risk_cells=nR,
                       fa_rate=nE / (nR * nrun) if nR else None,
                       n_frames_fired=len({(e["run"], e["frame_id"]) for e in sel}),
                       unclassified=sum(1 for e in sel if e["n_families"] == 0),
                       multi=sum(1 for e in sel if e["n_families"] >= 2),
                       mean_families=(sum(e["n_families"] for e in sel) / nE)
                       if nE else None, fams={})
            for fam in FAMS:
                fk = FAMKEY[fam]
                ek = f"fam_{fk}_p12" if fk in ("terr", "bnd") else f"fam_{fk}"
                rk = f"{fk}_p12" if fk in ("terr", "bnd") else fk
                # lift 분모: 지형통계형은 unseen(∪3b) 성분만 — prior_saturated 는
                # 모델 거동이라 노출 쪽 짝이 없다(test-core 센서스와 동일 처분).
                nfa = sum(e[ek] for e in sel)
                nrisk = sum(r[rk] for r in R)
                row["fams"][fam] = dict(
                    n=nfa, p_fa=nfa / nE if nE else None,
                    n_risk=nrisk, p_risk=nrisk / nR if nR else None,
                    lift=((nfa / nE) / (nrisk / nR)) if (nE and nrisk) else None,
                    rate=nfa / (nrisk * nrun) if nrisk else None,
                    n_raw=sum(e[f"fam_{fk}"] for e in sel),
                    primary=sum(1 for e in sel if e["primary"] == fam))
            row["primary_unclassified"] = sum(1 for e in sel
                                              if e["primary"] == "미분류")
            row["bnd_band"] = sum(e["bnd_band"] for e in sel)
            row["bnd_sector"] = sum(e["bnd_sector"] for e in sel)
            row["surrogate_weak"] = sum(e["surrogate_weak"] for e in sel)
            row["prior_saturated"] = sum(e["prior_saturated"] for e in sel)
            row["unseen"] = sum(e["unseen"] for e in sel)
            row["sens"] = dict(light_50=sum(e["light_50"] for e in sel),
                               light_70=sum(e["light_70"] for e in sel),
                               deco_5=sum(e["deco_5"] for e in sel),
                               deco_80=sum(e["deco_80"] for e in sel))
            o[a] = row
        return o

    RGB3 = [f"rgb_s{s}" for s in (42, 43, 44)]
    T["tableA"] = {
        "v2_rgb": block(RGB3, "v2", "v2·rgb"),
        "v3a_rgb": block(RGB3, "v3a", "v3-A·rgb"),
        "v2_all9": block(GEN["v2"]["runs"], "v2", "v2·9런"),
        "v2_depth": block([f"depth_s{s}" for s in (42, 43, 44)], "v2", "v2·depth"),
        "v2_b2": block([f"b2_s{s}" for s in (42, 43, 44)], "v2", "v2·b2"),
        "v3a_aux_isolated": block([AUX[1]], "v3a", "v3-A aux (격리)"),
    }

    # ---- 표 B: v2→v3 가족 이동 (rgb 대 rgb · 노출정규화 발화율 Δ) ---------
    T["tableB_shift"] = {}
    for a in ARMS:
        b2, b3 = T["tableA"]["v2_rgb"][a], T["tableA"]["v3a_rgb"][a]
        row = dict(fa_rate_v2=b2["fa_rate"], fa_rate_v3a=b3["fa_rate"],
                   d_fa_rate=b3["fa_rate"] - b2["fa_rate"],
                   n_events_v2=b2["n_events"], n_events_v3a=b3["n_events"], fams={})
        for fam in FAMS:
            f2, f3 = b2["fams"][fam], b3["fams"][fam]
            r2, r3 = f2["rate"], f3["rate"]
            row["fams"][fam] = dict(
                rate_v2=r2, rate_v3a=r3,
                d_rate=(r3 - r2) if (r2 is not None and r3 is not None) else None,
                ratio=(r3 / r2) if (r2 not in (None, 0) and r3 is not None) else None,
                lift_v2=f2["lift"], lift_v3a=f3["lift"],
                n_v2=f2["n"], n_v3a=f3["n"],
                p_fa_v2=f2["p_fa"], p_fa_v3a=f3["p_fa"])
        T["tableB_shift"][a] = row

    # ---- 표 B2: 시드 산포 (σ ddof=1) — 이동이 시드 잡음인지 -------------
    T["tableB_seed"] = {}
    for a in ARMS:
        R = risk[a]
        nR = len(R)
        o = {}
        for fam in FAMS:
            fk = FAMKEY[fam]
            ek = f"fam_{fk}_p12" if fk in ("terr", "bnd") else f"fam_{fk}"
            rk = f"{fk}_p12" if fk in ("terr", "bnd") else fk
            nrisk = sum(r[rk] for r in R) or 1
            per = {}
            for gen in ("v2", "v3a"):
                vals = []
                for run in RGB3:
                    n = sum(e[ek] for e in ev if e["gen"] == gen and e["run"] == run
                            and e["arm"] == a)
                    vals.append(n / nrisk)
                m, s = mean_sd(vals)
                per[gen] = dict(mean=m, sd=s, per_seed=[round(v, 6) for v in vals])
            d = per["v3a"]["mean"] - per["v2"]["mean"]
            sig = max(per["v2"]["sd"], per["v3a"]["sd"])
            o[fam] = dict(**{f"{k}_{g}": per[g][k] for g in ("v2", "v3a")
                             for k in ("mean", "sd")},
                          per_seed_v2=per["v2"]["per_seed"],
                          per_seed_v3a=per["v3a"]["per_seed"],
                          delta=d, sigma_max=sig,
                          exceeds_sigma=bool(abs(d) > sig) if sig is not None else None)
        T["tableB_seed"][a] = o

    # ---- 표 C: 칸/FA프레임 가족 분해 ("넓게 칠함" 귀속) -------------------
    # 배타 귀속(primary)이므로 가족 몫의 합 = 전체 칸/FA프레임.  시드 합산 정본.
    #
    # **경고 (이 표를 잘못 읽는 유일한 방법)**: 칸/FA프레임은 비율이고, v3-A 는
    # 분모(FA 프레임 수)를 크게 줄였다.  따라서 어떤 가족도 절대 칸 수가 늘지
    # 않았는데 전 가족의 몫이 동시에 오를 수 있다.  가족별 Δ 를 **shift-share** 로
    # 두 항으로 가른다 (합 = Δ, 항등):
    #    규모항 = n_f(v2) × (1/F₃ − 1/F₂)   ← 프레임 분모가 줄어서 생긴 몫
    #    조성항 = (n_f(v3) − n_f(v2)) / F₃  ← 그 가족의 칸이 실제로 늘어서 생긴 몫
    ALLFAM = list(FAMS) + ["미분류"]
    T["tableC_paint"] = {}
    for a in ARMS:
        o = {}
        for gen, runs in (("v2", RGB3), ("v3a", RGB3)):
            sel = [e for e in ev if e["gen"] == gen and e["run"] in runs
                   and e["arm"] == a]
            nf = len({(e["run"], e["frame_id"]) for e in sel})
            per = {f: sum(1 for e in sel if e["primary"] == f) for f in ALLFAM}
            o[gen] = dict(n_fa_frames=nf, n_cells=len(sel),
                          cells_per_alarm=(len(sel) / nf) if nf else None,
                          per_family_cells=per,
                          per_family_share={k: (v / len(sel) if sel else None)
                                            for k, v in per.items()},
                          per_family_cells_per_alarm={
                              k: (v / nf if nf else None) for k, v in per.items()})
        F2, F3 = o["v2"]["n_fa_frames"], o["v3a"]["n_fa_frames"]
        d, scale, comp, dshare = {}, {}, {}, {}
        for k in ALLFAM:
            n2 = o["v2"]["per_family_cells"][k]
            n3 = o["v3a"]["per_family_cells"][k]
            if not (F2 and F3):
                d[k] = scale[k] = comp[k] = dshare[k] = None
                continue
            d[k] = n3 / F3 - n2 / F2
            scale[k] = n2 * (1.0 / F3 - 1.0 / F2)
            comp[k] = (n3 - n2) / F3
            s2 = o["v2"]["per_family_share"][k]
            s3 = o["v3a"]["per_family_share"][k]
            dshare[k] = (s3 - s2) if (s2 is not None and s3 is not None) else None
        tot = ((o["v3a"]["cells_per_alarm"] - o["v2"]["cells_per_alarm"])
               if (o["v2"]["cells_per_alarm"] and o["v3a"]["cells_per_alarm"])
               else None)
        o["delta_per_family"] = d
        o["delta_scale_term"] = scale
        o["delta_composition_term"] = comp
        o["delta_share_pp"] = dshare
        o["delta_total"] = tot
        o["delta_total_scale"] = (sum(v for v in scale.values() if v is not None)
                                  if F2 and F3 else None)
        o["delta_total_composition"] = (sum(v for v in comp.values()
                                            if v is not None) if F2 and F3 else None)
        o["share_of_delta"] = ({k: (v / tot if tot else None)
                                for k, v in d.items()} if tot else None)
        o["identity_check"] = (abs((o["delta_total_scale"] or 0)
                                   + (o["delta_total_composition"] or 0)
                                   - (tot or 0)) < 1e-9) if tot else None
        T["tableC_paint"][a] = o

    # ---- 표 C2: 미분류 사건의 정체 (프로파일 · 인쇄 의무) ----------------
    T["tableC2_unclassified"] = {}
    for a in JUDGE_ARMS:
        o = {}
        for gen in ("v2", "v3a"):
            sel = [e for e in ev if e["gen"] == gen and e["run"] in RGB3
                   and e["arm"] == a and e["primary"] == "미분류"]
            o[gen] = dict(n=len(sel),
                          band=dict(Counter(e["band"] for e in sel).most_common()),
                          sector=dict(Counter(e["sector"] for e in sel).most_common()),
                          cell=dict(Counter(e["cell"] for e in sel).most_common(6)),
                          scene=dict(Counter(e["scene_id"] for e in sel).most_common()))
        T["tableC2_unclassified"][a] = o

    # ---- 표 D: 씬 × 가족 (이상치 탐색) ----------------------------------
    T["tableD_scene"] = {}
    for a in JUDGE_ARMS:
        R = risk[a]
        o = {}
        for sc in sorted({r["scene"] for r in R}):
            nR = sum(1 for r in R if r["scene"] == sc)
            rec = dict(n_risk=nR)
            for gen in ("v2", "v3a"):
                sel = [e for e in ev if e["gen"] == gen and e["run"] in RGB3
                       and e["arm"] == a and e["scene_id"] == sc]
                rec[gen] = dict(
                    n=len(sel), rate=len(sel) / (nR * 3) if nR else None,
                    fams={f: sum(1 for e in sel if e["primary"] == f)
                          for f in list(FAMS) + ["미분류"]})
            rec["d_rate"] = ((rec["v3a"]["rate"] - rec["v2"]["rate"])
                             if (rec["v2"]["rate"] is not None) else None)
            o[sc] = rec
        T["tableD_scene"][a] = o

    # ---- 표 E: 밴드 반경 법칙 (경계칸 반경 성분이 인공물인가) ------------
    T["tableE_radial"] = {}
    for a in JUDGE_ARMS:
        R = risk[a]
        o = {}
        for b in BANDS:
            nR = sum(1 for r in R if r["cell"][1:] == b)
            rec = dict(n_risk=nR)
            for gen in ("v2", "v3a"):
                n = sum(1 for e in ev if e["gen"] == gen and e["run"] in RGB3
                        and e["arm"] == a and e["band"] == b)
                rec[gen] = dict(n=n, rate=n / (nR * 3) if nR else None)
            o[b] = rec
        # ln-ln 기울기 (R_mid = 밴드 중점) — FA_CENSUS §3.3 의 R^1.98 재검
        mids = {"1": 1.0, "2": 3.5, "3a": 6.5, "3b": 10.0}
        for gen in ("v2", "v3a"):
            xs, ys = [], []
            for b in BANDS:
                r = o[b][gen]["rate"]
                if r and r > 0:
                    xs.append(np.log(mids[b]))
                    ys.append(np.log(r))
            o[f"loglog_slope_{gen}"] = (float(np.polyfit(xs, ys, 1)[0])
                                        if len(xs) >= 2 else None)
        T["tableE_radial"][a] = o

    # ---- 표 F: 가족 동시발생 · 다중소속 ----------------------------------
    T["tableF_cooccurrence"] = {}
    for a in JUDGE_ARMS:
        o = {}
        for gen in ("v2", "v3a"):
            sel = [e for e in ev if e["gen"] == gen and e["run"] in RGB3
                   and e["arm"] == a]
            co = {}
            for f1, f2 in combinations(FAMS, 2):
                k1 = FAMKEY[f1]
                k2 = FAMKEY[f2]
                e1 = f"fam_{k1}_p12" if k1 in ("terr", "bnd") else f"fam_{k1}"
                e2 = f"fam_{k2}_p12" if k2 in ("terr", "bnd") else f"fam_{k2}"
                co[f"{f1}×{f2}"] = sum(1 for e in sel if e[e1] and e[e2])
            o[gen] = dict(n=len(sel), pairs=co)
        T["tableF_cooccurrence"][a] = o

    # ---- 표 G: 팔 × 씬 × 단서키 화소 원장 (기계 검산 · 이상치 후보) ------
    keyagg = defaultdict(Counter)
    for (arm, fid, cell), p in ph.items():
        if not p["cue_keys"]:
            continue
        for kv in p["cue_keys"].split("|"):
            k, v = kv.split(":")
            keyagg[(arm, p["scene_id"])][k] += int(v)
    T["tableG_cue_px"] = {f"{a}|{s}": dict(c.most_common())
                          for (a, s), c in sorted(keyagg.items())}

    # 이상치 원장 — **기계 산출**.  서술은 §15 본문, 여기는 수치만.
    out_notes = []
    for (a, s), c in sorted(keyagg.items()):
        if a in ("B", "D") and sum(c.values()) > 0:
            out_notes.append(dict(
                kind="cue_residual_in_off_arm", arm=a, scene=s,
                px=sum(c.values()), keys=dict(c.most_common()),
                ref_C_px=sum(keyagg[("C", s)].values()),
                frac_of_C=(sum(c.values()) / sum(keyagg[("C", s)].values())
                           if sum(keyagg[("C", s)].values()) else None)))
    for s in sorted({s for (a, s) in keyagg if a == "A"}):
        ca, cc = keyagg[("A", s)], keyagg[("C", s)]
        for k in sorted(set(ca) | set(cc)):
            if ca[k] and cc[k] and abs(cc[k] - ca[k]) / max(ca[k], 1) > 0.02:
                out_notes.append(dict(kind="AC_cue_px_mismatch", scene=s, key=k,
                                      A_px=ca[k], C_px=cc[k],
                                      rel=(cc[k] - ca[k]) / ca[k]))
            elif bool(ca[k]) != bool(cc[k]):
                out_notes.append(dict(kind="AC_cue_key_presence", scene=s, key=k,
                                      A_px=ca[k], C_px=cc[k], rel=None))
    # 씬별 부호 역전 — C팔에서 v2→v3 가 오른 씬
    for a in JUDGE_ARMS:
        for sc, r in T["tableD_scene"][a].items():
            if r["d_rate"] is not None and r["v2"]["n"] + r["v3a"]["n"] >= 30 \
                    and r["d_rate"] > 0:
                out_notes.append(dict(kind="scene_rate_up", arm=a, scene=sc,
                                      rate_v2=r["v2"]["rate"],
                                      rate_v3a=r["v3a"]["rate"], d=r["d_rate"],
                                      top_family_v3a=max(
                                          r["v3a"]["fams"].items(),
                                          key=lambda kv: kv[1])[0]))
    T["outliers"] = out_notes

    # ---- σ 요약 (판정 축이 아니라 인쇄 의무임을 명시) --------------------
    T["sigma_summary"] = dict(
        rule="Δ(가족 발화율) 의 |Δ| > max(σ_v2, σ_v3) · σ = ddof=1 · 3시드",
        note=("본 절은 PREREG §2.2 「층화」 = **인쇄 의무**이지 판정 축이 아니다. "
              "σ 초과 여부는 서술의 강도를 규율하기 위해 함께 인쇄한다."),
        exceed=[f"{a}|{f}" for a in JUDGE_ARMS for f in FAMS
                if T["tableB_seed"][a][f]["exceeds_sigma"]],
        n_tested=len(JUDGE_ARMS) * len(FAMS))

    json.dump(T, open(OUTJSON, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    # ---------------------------------------------------------------- 콘솔
    print(json.dumps(params, ensure_ascii=False))
    print(f"events {len(ev)} -> {os.path.relpath(OUTCSV, ROOT)}")
    print("검산:", json.dumps(T["recon_summary"], ensure_ascii=False))
    print("\n노출(칸):", {a: T['exposure'][a]['n_cells'] for a in ARMS})
    for a in JUDGE_ARMS:
        print(f"\n=== 팔 {a} === 노출 {T['exposure'][a]['n_cells']}칸")
        b = T["tableB_shift"][a]
        print(f"  FA율 v2 {b['fa_rate_v2']:.4f} → v3-A {b['fa_rate_v3a']:.4f} "
              f"(Δ {b['d_fa_rate']:+.4f})")
        for f in FAMS:
            x = b["fams"][f]
            sd = T["tableB_seed"][a][f]
            r2 = x["rate_v2"]
            r3 = x["rate_v3a"]
            if r2 is None or r3 is None:
                print(f"  {f:6s} n/a")
                continue
            print(f"  {f:6s} rate {r2:.4f} → {r3:.4f} (Δ{r3-r2:+.4f}"
                  f"{'  σ초과' if sd['exceeds_sigma'] else '        '}) "
                  f"lift {x['lift_v2']:.2f} → {x['lift_v3a']:.2f}  "
                  f"n {x['n_v2']:>5} → {x['n_v3a']:>5}")
        c = T["tableC_paint"][a]
        print(f"  칸/FA프레임 {c['v2']['cells_per_alarm']:.3f} → "
              f"{c['v3a']['cells_per_alarm']:.3f} (Δ {c['delta_total']:+.3f}"
              f" = 규모 {c['delta_total_scale']:+.3f} + 조성 "
              f"{c['delta_total_composition']:+.3f} · 항등 "
              f"{'OK' if c['identity_check'] else 'FAIL'})")
        for k in list(FAMS) + ["미분류"]:
            if c["delta_per_family"][k] is None or abs(c["delta_per_family"][k]) < 1e-9:
                continue
            print(f"    {k:6s} Δ{c['delta_per_family'][k]:+.3f} "
                  f"(규모{c['delta_scale_term'][k]:+.3f} 조성"
                  f"{c['delta_composition_term'][k]:+.3f}) 칸 "
                  f"{c['v2']['per_family_cells'][k]:>5}→"
                  f"{c['v3a']['per_family_cells'][k]:<5} 몫 "
                  f"{c['v2']['per_family_share'][k]:.3f}→"
                  f"{c['v3a']['per_family_share'][k]:.3f}")
    print("\nσ 초과 가족:", T["sigma_summary"]["exceed"] or "없음 (0/15)")
    print(f"이상치 원장 {len(T['outliers'])}건")
    print(f"\n→ {os.path.relpath(OUTJSON, ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
