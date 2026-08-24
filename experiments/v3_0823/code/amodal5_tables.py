#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""amodal5_tables.py — GPU-5 아모달 판독의 집계 (CPU 전용 · 새 추론 0).

    PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES= \
      python3 experiments/v3_0823/code/amodal5_tables.py

입력  experiments/v3_0823/amodal5/{records.npz, index.json}
산출  experiments/v3_0823/amodal5/tables.json  (+ 표준출력에 전 표)

[격리·진단] 두 aux 체크포인트 모두 훼손된 학습이다. 어떤 수도 PREREG A/B 판정에 쓰지 않는다.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

ROOT = "/home/vislab/Desktop/work_sy/Practice_NegObs"
OUTD = os.path.join(ROOT, "experiments/v3_0823/amodal5")
NPIX = 512 * 512
FLOOR = 0.05                      # (b) 「작은 바닥」 — GT 영역 평균확률 하한
GENS = ("v2gen", "v3gen")
GENKR = dict(v2gen="v2세대 rgb_s42_aux", v3gen="v3세대(격리) rgb_s42_aux")


def ms(v):
    v = np.asarray(v, float)
    v = v[np.isfinite(v)]
    if v.size == 0:
        return (float("nan"),) * 3
    return float(v.mean()), float(v.std(ddof=1)) if v.size > 1 else 0.0, float(np.median(v))


def ap_auc(score, y):
    """평균정밀도(AP) + ROC-AUC. sklearn 미의존 (동점은 평균 순위)."""
    s, y = np.asarray(score, float), np.asarray(y, float)
    ok = np.isfinite(s)
    s, y = s[ok], y[ok]
    P, N = y.sum(), (1 - y).sum()
    if P == 0 or N == 0:
        return float("nan"), float("nan")
    o = np.argsort(-s, kind="mergesort")
    ys = y[o]
    tp = np.cumsum(ys)
    prec = tp / np.arange(1, len(ys) + 1)
    ap = float((prec * ys).sum() / P)
    r = np.empty(len(s))
    order = np.argsort(s, kind="mergesort")
    ss = s[order]
    i = 0
    rk = np.arange(1, len(s) + 1, dtype=float)
    while i < len(ss):
        j = i
        while j + 1 < len(ss) and ss[j + 1] == ss[i]:
            j += 1
        rk[i:j + 1] = (i + j + 2) / 2.0
        i = j + 1
    r[order] = rk
    auc = float((r[y == 1].sum() - P * (P + 1) / 2) / (P * N))
    return ap, auc


def ece_brier(prob, y, bins=15):
    p, y = np.asarray(prob, float), np.asarray(y, float)
    ok = np.isfinite(p)
    p, y = p[ok], y[ok]
    if p.size == 0:
        return float("nan"), float("nan")
    edges = np.linspace(0, 1, bins + 1)
    e = 0.0
    for k in range(bins):
        m = (p >= edges[k]) & (p < edges[k + 1] if k < bins - 1 else p <= 1.0)
        if m.sum():
            e += m.mean() * abs(p[m].mean() - y[m].mean())
    return float(e), float(((p - y) ** 2).mean())


def matched_rate(score, y, n_fire):
    """직접 헤드가 켠 칸 수와 **같은 수**만 켰을 때의 recall/precision."""
    s, y = np.asarray(score, float), np.asarray(y, float)
    ok = np.isfinite(s)
    s, y = s[ok], y[ok]
    n_fire = int(min(max(n_fire, 0), len(s)))
    if n_fire == 0:
        return 0.0, float("nan")
    thr = np.sort(s)[::-1][n_fire - 1]
    f = s >= thr
    return float(y[f].sum() / max(y.sum(), 1)), float(y[f].mean())


def main():
    d = np.load(os.path.join(OUTD, "records.npz"))
    idx = json.load(open(os.path.join(OUTD, "index.json")))
    rows = idx["rows"]
    n = len(rows)
    # 집합 소속은 frames.json 원본에서 읽는다 — panel 4장은 core_H/core_E 와 **겹치므로**
    # 추론은 한 번만 했지만(dup 접기) 집계에서는 두 집합 모두에 들어가야 한다.
    memb = {}
    for r in json.load(open(os.path.join(OUTD, "frames.json")))["frames"]:
        memb.setdefault(r["key"], set()).add(r["group"])
    keyv = [r["key"] for r in rows]

    def inset(name):
        return np.array([name in memb[k] for k in keyv])

    grp = np.array([r["group"] for r in rows])
    fid = np.array([r["frame_id"] for r in rows])
    scene = np.array([r["scene"] for r in rows])
    arm = np.array([r["arm"] for r in rows])
    gtc = np.array([r["polar_gt"] for r in rows], float)
    has = np.array([r["has_gt"] for r in rows])
    a_gt, a_ring, a_mir, a_occ = d["a_gt"], d["a_ring"], d["a_mir"], d["a_occ"]
    cellv = d["cell_valid"] & (d["a_cell"] > 0)

    def dens(g, region):
        m, ar = d[f"{g}__mass_{region}"], dict(in_=a_gt, ring=a_ring, mir=a_mir, occ=a_occ)[
            {"in": "in_"}.get(region, region)]
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(ar > 0, m / np.maximum(ar, 1), np.nan)

    def dens_rest(g):
        rest_m = (d[f"{g}__mass_tot"] - d[f"{g}__mass_in"] - d[f"{g}__mass_ring"]
                  - d[f"{g}__mass_occ"])
        rest_a = NPIX - a_gt - a_ring - a_occ
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(rest_a > 0, rest_m / np.maximum(rest_a, 1), np.nan)

    def dens_out(g):
        with np.errstate(invalid="ignore", divide="ignore"):
            return (d[f"{g}__mass_tot"] - d[f"{g}__mass_in"]) / np.maximum(NPIX - a_gt, 1)

    T = {}

    # ============================================================ (a) 마스크 품질
    print("\n" + "=" * 100)
    print("(a) 마스크 품질 — 아모달 GT 가 있는 프레임만 · [훈련 결함 주의: 아래 표 머리 참조]")
    print("=" * 100)
    SETS = [("core_V", "test-core V (보임)"), ("core_E", "test-core E (테두리)"),
            ("core_H", "test-core H (엄격 은닉)"), ("ext_H", "test-ext H (A팔 · v3세대)"),
            ("core_Htwin", "[대조] test-core H 의 off팔 트윈(낙차 없음)")]
    T["a"] = {}
    hdr = (f"{'집합':38s} {'n':>3s} {'세대':6s} {'IoU@.5':>7s} {'덮음@.5':>8s} {'정밀@.5':>8s} "
           f"{'GT내평균p':>9s} {'GT면적비':>8s} {'예측면적비':>9s} {'전칠IoU':>8s}")
    print(hdr)
    for key, name in SETS:
        m = inset(key) & has
        if not m.any():
            continue
        for g in GENS:
            inter, pred = d[f"{g}__inter50"][m], d[f"{g}__pred50"][m]
            iou = inter / np.maximum(a_gt[m] + pred - inter, 1)
            cov = inter / np.maximum(a_gt[m], 1)
            with np.errstate(invalid="ignore", divide="ignore"):
                pr = np.where(pred > 0, inter / np.maximum(pred, 1), np.nan)
            meanp = d[f"{g}__mass_in"][m] / np.maximum(a_gt[m], 1)
            af = a_gt[m] / NPIX
            pf = pred / NPIX
            rec = dict(n=int(m.sum()), iou=ms(iou), cov=ms(cov), prec=ms(pr),
                       mean_in=ms(meanp), area_frac=ms(af), pred_frac=ms(pf),
                       iou_paint_all=ms(af))
            T["a"][f"{key}|{g}"] = rec
            print(f"{name if g == GENS[0] else '':38s} {int(m.sum()):3d} {g:6s} "
                  f"{rec['iou'][0]:7.3f} {rec['cov'][0]:8.3f} {rec['prec'][0]:8.3f} "
                  f"{rec['mean_in'][0]:9.3f} {rec['area_frac'][0]:8.3f} "
                  f"{rec['pred_frac'][0]:9.3f} {rec['iou_paint_all'][0]:8.3f}")

    # ============================================================ (b) THE QUESTION
    print("\n" + "=" * 100)
    print("(b) H 프레임에서 은닉 낙차를 그리는가 — 질량 배치 · 대조군 포함")
    print("=" * 100)
    T["b"] = {}
    for key, name in (("core_H", "test-core H 96장"), ("ext_H", "test-ext H(A팔) 72장"),
                      ("core_Htwin", "[대조] off팔 트윈 96장")):
        m = inset(key) & has
        for g in GENS:
            di, do = dens(g, "in")[m], dens_out(g)[m]
            dr, dm = dens(g, "ring")[m], dens(g, "mir")[m]
            docc, dres = dens(g, "occ")[m], dens_rest(g)[m]
            fin = d[f"{g}__mass_in"][m] / np.maximum(d[f"{g}__mass_tot"][m], 1e-9)
            af = a_gt[m] / NPIX
            with np.errstate(invalid="ignore", divide="ignore"):
                enr = di / do
            rec = dict(n=int(m.sum()),
                       frac_in=ms(fin), area_frac=ms(af),
                       frac_over_area=ms(fin / np.maximum(af, 1e-9)),
                       dens_in=ms(di), dens_ring=ms(dr), dens_occ=ms(docc),
                       dens_mir=ms(dm), dens_rest=ms(dres), dens_out=ms(do),
                       enrich=ms(enr),
                       p_floor=float(np.mean(di >= FLOOR)),
                       p_floor20=float(np.mean(di >= 0.20)),
                       p_pmax50=float(np.mean(d[f"{g}__pmax_in"][m] >= 0.5)),
                       p_enrich_gt1=float(np.nanmean(enr > 1.0)))
            T["b"][f"{key}|{g}"] = rec
            print(f"\n{name}  ·  {GENKR[g]}  (n={rec['n']})")
            print(f"   질량 안쪽 비중 frac_in {rec['frac_in'][0]:.3f} (중앙값 {rec['frac_in'][2]:.3f})"
                  f"  vs  GT 면적 비중 {rec['area_frac'][0]:.3f}"
                  f"   → 비 {rec['frac_over_area'][0]:.3f}")
            print(f"   밀도  R1 GT아모달 {rec['dens_in'][0]:.4f} | R2 경계링24px "
                  f"{rec['dens_ring'][0]:.4f} | R_occ 가림물근사 {rec['dens_occ'][0]:.4f} | "
                  f"R3 그 외 {rec['dens_rest'][0]:.4f} | 거울대조 {rec['dens_mir'][0]:.4f}")
            print(f"   농축 enrich = R1/바깥 {rec['enrich'][0]:.3f} "
                  f"(중앙값 {rec['enrich'][2]:.3f}) · enrich>1 프레임 {rec['p_enrich_gt1']:.3f}")
            print(f"   바닥 통과   평균p≥{FLOOR} {rec['p_floor']:.3f} · ≥0.20 "
                  f"{rec['p_floor20']:.3f} · GT안 최대p≥0.5 {rec['p_pmax50']:.3f}")

    # ---- 트윈 짝 비교 (같은 컷 · 낙차만 제거) ------------------------------
    print("\n" + "-" * 100)
    print("(b-트윈) 같은 컷에서 낙차만 뺐을 때 GT 아모달 영역(반사실)의 밀도가 내려가는가")
    print("-" * 100)
    twin_of = {r["frame_id"]: r.get("twin_of") for r in rows}
    pos = {f: i for i, f in enumerate(fid)}
    pairs = [(pos[twin_of[f]], i) for i, f in enumerate(fid)
             if twin_of[f] and twin_of[f] in pos]
    T["b_twin"] = dict(n_pairs=len(pairs))
    for g in GENS:
        di = dens(g, "in")
        on = np.array([di[a] for a, _ in pairs])
        off = np.array([di[b] for _, b in pairs])
        tot_on = np.array([d[f"{g}__mass_tot"][a] for a, _ in pairs]) / NPIX
        tot_off = np.array([d[f"{g}__mass_tot"][b] for _, b in pairs]) / NPIX
        rec = dict(dens_on=ms(on), dens_off=ms(off), delta=ms(on - off),
                   ratio=ms(on / np.maximum(off, 1e-9)),
                   frac_on_gt_off=float(np.mean(on > off)),
                   mass_on=ms(tot_on), mass_off=ms(tot_off))
        T["b_twin"][g] = rec
        print(f"   {GENKR[g]:26s} n={len(pairs)}  "
              f"R1밀도 on {rec['dens_on'][0]:.4f} → off {rec['dens_off'][0]:.4f}  "
              f"Δ {rec['delta'][0]:+.4f} (중앙 {rec['delta'][2]:+.4f}) · "
              f"on>off {rec['frac_on_gt_off']:.3f} · 비 {rec['ratio'][2]:.3f}(중앙)")
        print(f"   {'':26s}     전체 마스크 면적비 on {rec['mass_on'][0]:.3f} → "
              f"off {rec['mass_off'][0]:.3f}")

    # ---- 교란 정면 대면: 트윈이 광학적으로 조용한가 -------------------------
    print("\n" + "-" * 100)
    print("(b-교란) 트윈이 「낙차만」 다른가 — 광학 차이 실측 · 차이 사분위별 농축")
    print("-" * 100)
    td = json.load(open(os.path.join(OUTD, "twin_delta.json")))
    tds = td["core_H_summary"]
    dmap = {c["on"]: c for c in td["core_H"]}
    print(f"   test-core H 96짝: frac(|ΔI|>8) 전체 {tds['frac_gt8_mean']:.4f} "
          f"(중앙 {tds['frac_gt8_median']:.4f} · 최대 {tds['frac_gt8_max']:.4f}) · "
          f"zero-info(<0.001) {tds['n_zero_info']}/96")
    print(f"   같은 차이를 GT 아모달 안/밖으로 쪼개면 안 {tds['frac_gt8_in_mean']:.4f} · "
          f"밖 {tds['frac_gt8_out_mean']:.4f} → 안이 "
          f"{tds['frac_gt8_in_mean'] / max(tds['frac_gt8_out_mean'], 1e-9):.1f}배")
    T["b_confound"] = dict(summary=tds, quartiles={})
    mH = inset("core_H") & has
    dI = np.array([dmap[f]["frac_gt8_in"] if f in dmap else np.nan for f in fid])
    sel = np.where(mH & np.isfinite(dI))[0]
    q = np.quantile(dI[sel], [0, .25, .5, .75, 1.0])
    print(f"\n   {'ΔI(안) 사분위':22s} {'n':>3s} " +
          " ".join(f"{g + ' 농축':>12s} {g + ' 트윈Δ':>12s}" for g in GENS))
    for k in range(4):
        lo, hi = q[k], q[k + 1]
        s = sel[(dI[sel] >= lo) & (dI[sel] <= hi if k == 3 else dI[sel] < hi)]
        cells, rec = [], dict(lo=float(lo), hi=float(hi), n=int(len(s)))
        for g in GENS:
            di_all = dens(g, "in")
            with np.errstate(invalid="ignore", divide="ignore"):
                e = di_all[s] / dens_out(g)[s]
            dl = np.array([di_all[i] - di_all[pos["off/" + fid[i].split("/", 1)[1]]]
                           for i in s])
            rec[g] = dict(enrich=ms(e), twin_delta=ms(dl))
            cells.append(f"{np.nanmean(e):12.3f} {np.nanmean(dl):+12.4f}")
        T["b_confound"]["quartiles"][f"Q{k + 1}"] = rec
        print(f"   Q{k + 1} [{lo:.3f},{hi:.3f}]{'':4s} {len(s):3d} " + " ".join(cells))
    print("   Q1 = 트윈이 가장 조용한 사분위. 여기서도 농축이 살아 있으면 「광학 흔적 읽기」"
          "만으로는 설명되지 않는다.")

    # ============================================================ (d) 파생 vs 직접
    print("\n" + "=" * 100)
    print("(d) 마스크→그리드 파생 vs 직접 그리드 헤드 — 같은 forward · 같은 프레임 · 같은 GT칸")
    print("=" * 100)
    T["d"] = {}
    print(f"{'집합':30s} {'n칸':>6s} {'세대':6s} {'AP파생':>7s} {'AP직접':>7s} {'AUC파생':>8s} "
          f"{'AUC직접':>8s} {'ECE파생':>8s} {'ECE직접':>8s} {'동수recall':>10s} {'직접recall':>10s}")
    for key, name in (("core_V", "test-core V"), ("core_E", "test-core E"),
                      ("core_H", "test-core H"), ("ext_H", "test-ext H(A팔)")):
        m = inset(key)
        if not m.any():
            continue
        vm = cellv[m]
        y = gtc[m][vm]
        for g in GENS:
            q = d[f"{g}__q"][m][vm]
            p = d[f"{g}__p"][m][vm]
            apq, aucq = ap_auc(q, y)
            app, aucp = ap_auc(p, y)
            eq, bq = ece_brier(q, y)
            ep, bp = ece_brier(p, y)
            nfire = int((p >= 0.5).sum())
            rq, pq = matched_rate(q, y, nfire)
            rp = float(y[p >= 0.5].sum() / max(y.sum(), 1))
            pp = float(y[p >= 0.5].mean()) if nfire else float("nan")
            rho = []
            for i in np.where(m)[0]:
                v = cellv[i]
                if v.sum() >= 5:
                    a1, a2 = d[f"{g}__q"][i][v], d[f"{g}__p"][i][v]
                    r1 = np.argsort(np.argsort(a1)); r2 = np.argsort(np.argsort(a2))
                    if r1.std() > 0 and r2.std() > 0:
                        rho.append(float(np.corrcoef(r1, r2)[0, 1]))
            rec = dict(n_cells=int(vm.sum()), n_pos=int(y.sum()), ap_q=apq, ap_p=app,
                       auc_q=aucq, auc_p=aucp, ece_q=eq, ece_p=ep, brier_q=bq, brier_p=bp,
                       recall_matched_q=rq, prec_matched_q=pq, recall_p50=rp, prec_p50=pp,
                       n_fire_p50=nfire, spearman=ms(rho))
            T["d"][f"{key}|{g}"] = rec
            print(f"{name if g == GENS[0] else '':30s} {int(vm.sum()):6d} {g:6s} "
                  f"{apq:7.3f} {app:7.3f} {aucq:8.3f} {aucp:8.3f} {eq:8.3f} {ep:8.3f} "
                  f"{rq:10.3f} {rp:10.3f}")
        print(f"{'':30s} {'':6s} {'ρ(파생,직접) 프레임내 순위상관 ' + GENS[0]:>10s} "
              f"{T['d'][key + '|' + GENS[0]]['spearman'][0]:.3f} · "
              f"{GENS[1]} {T['d'][key + '|' + GENS[1]]['spearman'][0]:.3f}")

    # ============================================================ (c) CUE-OFF 팔
    print("\n" + "=" * 100)
    print("(c) CUE-OFF 팔별 마스크 반응 — test-ext sceneH1/H2/H3 · A/B/C/D 4팔")
    print("=" * 100)
    T["c"] = {}
    m0 = inset("cueoff")
    dAC = {}
    for r in td["ext"]:
        dAC[r["frame_id"]] = r
    print("[전체 마스크 면적비 = 마스크 평균확률 · 발화 = p≥.5 면적비]")
    print(f"{'씬':10s} {'세대':6s} " + " ".join(f"{a:>15s}" for a in "ABCD") + "   A−B      A−C")
    for sc in sorted(set(scene[m0])):
        for g in GENS:
            cells, mm = [], {}
            for ar in "ABCD":
                m = m0 & (scene == sc) & (arm == ar)
                mass = d[f"{g}__mass_tot"][m] / NPIX
                fire = d[f"{g}__pred50"][m] / NPIX
                mm[ar] = float(mass.mean())
                T["c"][f"{sc}|{ar}|{g}"] = dict(n=int(m.sum()), mass_frac=ms(mass),
                                                fire_frac=ms(fire))
                cells.append(f"{mass.mean():.3f}/{fire.mean():.3f}({int(m.sum())})")
            print(f"{sc:10s} {g:6s} " + " ".join(f"{c:>15s}" for c in cells) +
                  f"  {mm['A'] - mm['B']:+.3f}   {mm['A'] - mm['C']:+.3f}")
    print("   A = 단서 有·낙차 有 · B = 단서 OFF·낙차 有 · C = 단서 有·낙차 無 · D = 둘 다 無")

    print("\n   [반사실 아모달 영역 안 밀도] — A팔 H 프레임의 아모달 GT 를 4팔에 그대로 붙여 비교")
    print(f"{'씬':10s} {'세대':6s} {'n':>4s} " + " ".join(f"{a:>9s}" for a in "ABCD") +
          "   광학 frac(|ΔI|>8) A-C / A-B")
    T["c_cf"] = {}
    for sc in sorted(set(scene[m0])):
        ms_ac = np.mean([dAC[k]["AC"]["frac_gt8"] for k in dAC
                         if dAC[k]["scene"] == sc and dAC[k]["AC"]])
        ms_ab = np.mean([dAC[k]["AB"]["frac_gt8"] for k in dAC
                         if dAC[k]["scene"] == sc and dAC[k]["AB"]])
        for g in GENS:
            di_all = dens(g, "in")
            cells, nn = [], 0
            for ar in "ABCD":
                m = m0 & (scene == sc) & (arm == ar) & has
                v = di_all[m]
                nn = int(m.sum())
                T["c_cf"][f"{sc}|{ar}|{g}"] = dict(n=nn, dens_in=ms(v))
                cells.append(f"{np.nanmean(v):9.4f}")
            print(f"{sc:10s} {g:6s} {nn:4d} " + " ".join(cells) +
                  f"      {ms_ac:.4f} / {ms_ab:.4f}")
    print("   sceneH3 는 A-C 광학차 ≈ 0 (완전 은닉) — 「볼 것이 없으면 A와 C가 같아야」 정상.")

    json.dump(T, open(os.path.join(OUTD, "tables.json"), "w"), indent=1)
    print(f"\n[done] -> {os.path.join(OUTD, 'tables.json')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
