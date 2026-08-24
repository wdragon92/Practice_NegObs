#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verdict_panel_family.py — V-3 이행 · step 3
`panels/verdict/panel_e_family_strata.png` — 계기판② FA 5가족 층화의 before/after.

읽는 법 (패널 안에도 적는다)
  상단 3칸 = 팔 B·C·D **각각**. 세로축은 **노출 정규화 발화율**
    rate_f = FA(f) / (그 가족의 위험노출 칸 수 × 런 수) — 가족마다 분모가 다르므로
    물량 막대가 아니라 **같은 축에서 비교 가능한 비율**이다. 오차막대 = σ(ddof=1, 3시드).
  하단 좌·중 = 「칸/FA프레임」 Δ 의 **shift-share** 분해.
    규모항 = FA 프레임 수가 줄어 생긴 몫 · 조성항 = 그 가족의 칸이 실제로 늘어 생긴 몫.
  하단 우 = 밴드 반경 법칙(log-log). `FA_CENSUS §3.3` 의 R^1.98 이 미학습 무대에서
    재현되는지, v3-A 가 그 기울기를 눕히는지.

CPU · 재추론 0 · 재렌더 0 · GPU 0 · git 무접촉.
"""
from __future__ import annotations

import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
from matplotlib import font_manager, rcParams          # noqa: E402

ROOT = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V3 = os.path.join(ROOT, "experiments/v3_0823")
OUT = os.path.join(V3, "panels/verdict")
os.makedirs(OUT, exist_ok=True)

# ---- [복사: verdict_panels.py L52-68 ← make_panels_v3.py L26-43] -------------
_FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
try:
    font_manager.fontManager.addfont(_FONT)
except Exception:
    pass
rcParams["font.family"] = ["Noto Sans CJK KR", "Noto Sans CJK JP", "DejaVu Sans"]
_have = {f.name for f in font_manager.fontManager.ttflist}
rcParams["font.family"] = [n for n in rcParams["font.family"] if n in _have] or ["DejaVu Sans"]
rcParams["axes.unicode_minus"] = False
rcParams["savefig.facecolor"] = "white"
rcParams["figure.facecolor"] = "white"

C = dict(pub="#B9C2D0", cor="#2F4B7C", ok="#2E7D5B", bad="#B03A48",
         grid="#DDE1E6", ink="#1F2429", mute="#5C6672")
DATE = "2026-08-24"
V2COL, V3COL = "#B9C2D0", "#2F4B7C"
SCALECOL, COMPCOL = "#C9B79C", "#5C7F8A"     # 규모항 / 조성항

import numpy as np                                     # noqa: E402
import matplotlib.pyplot as plt                        # noqa: E402
from matplotlib.patches import Patch                   # noqa: E402
from matplotlib.lines import Line2D                    # noqa: E402

FAMS = ("장식형", "지형통계형", "조명형", "대리선형", "경계칸형")
ARMLAB = {"B": "B팔 — 단서 X · 위험 O\n(GT 음성칸)",
          "C": "C팔 — 단서 O · 위험 X\n(FA_C · 전 칸 GT 음성)",
          "D": "D팔 — 단서 X · 위험 X\n(FA_D · 전 칸 GT 음성)"}


def footer(fig, text, y=0.006):
    """[복사: make_panels_v3.py L45-47] 출처 푸터."""
    fig.text(0.5, y, text, ha="center", va="bottom", fontsize=7.0,
             color=C["mute"], family=rcParams["font.family"], linespacing=1.6)


def save(fig, name, dpi=140):
    """[복사: make_panels_v3.py L49-59] 저장 + 2 MB 규율."""
    p = os.path.join(OUT, name)
    fig.savefig(p, dpi=dpi, bbox_inches="tight", pad_inches=0.24)
    import PIL.Image as I
    sz = os.path.getsize(p)
    if sz > 2_000_000:
        im = I.open(p).convert("RGB")
        im.quantize(colors=256, method=I.MEDIANCUT).save(p, optimize=True)
        sz = os.path.getsize(p)
    dim = I.open(p).size
    print(f"  {name:34s} {sz/1024:8.0f} KB  {dim}")
    return p, sz, dim


def main():
    T = json.load(open(os.path.join(V3, "verdict_fa_family.json"), encoding="utf-8"))
    fig = plt.figure(figsize=(15.8, 11.4))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 1.0], hspace=0.60, wspace=0.245,
                          left=0.058, right=0.985, top=0.815, bottom=0.125)

    # ---------------- 상단: 팔별 가족 발화율 before/after ------------------
    for j, arm in enumerate("BCD"):
        ax = fig.add_subplot(gs[0, j])
        sh = T["tableB_shift"][arm]
        sd = T["tableB_seed"][arm]
        x = np.arange(len(FAMS))
        w = 0.37
        r2 = [sh["fams"][f]["rate_v2"] for f in FAMS]
        r3 = [sh["fams"][f]["rate_v3a"] for f in FAMS]
        e2 = [sd[f]["sd_v2"] for f in FAMS]
        e3 = [sd[f]["sd_v3a"] for f in FAMS]
        nrisk = [T["tableA"]["v2_rgb"][arm]["fams"][f]["n_risk"] for f in FAMS]
        ax.bar(x - w / 2, [v or 0 for v in r2], w, yerr=[v or 0 for v in e2],
               color=V2COL, edgecolor="#8D97A5", linewidth=0.6, label="v2 (rgb 3시드)",
               error_kw=dict(elinewidth=1.0, ecolor="#7A8492", capsize=2.6))
        ax.bar(x + w / 2, [v or 0 for v in r3], w, yerr=[v or 0 for v in e3],
               color=V3COL, edgecolor="#1B3352", linewidth=0.6, label="v3-A (rgb 3시드)",
               error_kw=dict(elinewidth=1.0, ecolor="#1B3352", capsize=2.6))
        hi = max([(v or 0) + (e or 0) for v, e in
                  zip(r2 + r3, e2 + e3)] + [1e-4])
        ax.set_ylim(0, hi * 1.24)
        for i, f in enumerate(FAMS):
            if not nrisk[i]:
                ax.text(i, hi * 0.06, "노출 0\n(정의상 0)", ha="center", va="bottom",
                        fontsize=7.2, color=C["bad"], linespacing=1.4)
                continue
            a, b = r2[i] or 0.0, r3[i] or 0.0
            if a == 0 and b == 0:
                ax.text(i, hi * 0.04, "사건 0", ha="center", va="bottom",
                        fontsize=7.2, color=C["mute"])
                continue
            d = b - a
            col = C["ok"] if d < 0 else C["bad"]
            y = min(max(a + (e2[i] or 0), b + (e3[i] or 0)) + hi * 0.025, hi * 1.13)
            ax.text(i, y, f"{d:+.3f}", ha="center", va="bottom", fontsize=7.8,
                    color=col, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels(FAMS, fontsize=8.4)
        ax.set_ylabel("노출 정규화 발화율\nFA(가족) / (노출칸 × 런)", fontsize=8.6)
        ax.set_title(ARMLAB[arm], fontsize=10.4, fontweight="bold",
                     color=C["ink"], pad=7, linespacing=1.35)
        ax.grid(axis="y", color=C["grid"], linewidth=0.7, zorder=0)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        nr = ("가족 노출칸 (분모): " + " · ".join(
            f"{f[:2]} {n:,}" for f, n in zip(FAMS, nrisk))
            + f"   |   팔 전체 노출 {T['exposure'][arm]['n_cells']:,}칸 × 3런")
        ax.text(0.5, -0.155, nr, transform=ax.transAxes, ha="center", va="top",
                fontsize=6.9, color=C["mute"])
        if j == 0:
            ax.legend(fontsize=8.2, frameon=False, loc="upper left")

    # ---------------- 하단 좌·중: 칸/FA프레임 shift-share ------------------
    for j, arm in enumerate("CD"):
        ax = fig.add_subplot(gs[1, j])
        c = T["tableC_paint"][arm]
        keys = list(FAMS) + ["미분류"]
        x = np.arange(len(keys))
        sc = [c["delta_scale_term"][k] or 0.0 for k in keys]
        cm = [c["delta_composition_term"][k] or 0.0 for k in keys]
        ax.bar(x, sc, 0.62, color=SCALECOL, edgecolor="#9C8A6E", linewidth=0.6,
               label="규모항 (FA 프레임 수 변화)")
        ax.bar(x, cm, 0.62, bottom=sc, color=COMPCOL, edgecolor="#3E5F69",
               linewidth=0.6, label="조성항 (그 가족의 칸 수 변화)")
        lo = min([0.0] + [min(s, s + m) for s, m in zip(sc, cm)])
        up = max([0.0] + [max(s, s + m) for s, m in zip(sc, cm)])
        rng = (up - lo) or 1.0
        ax.set_ylim(lo - rng * 0.17, up + rng * (0.30 if j == 0 else 0.17))
        for i, k in enumerate(keys):
            tot = sc[i] + cm[i]
            ax.plot([i - 0.37, i + 0.37], [tot, tot], color=C["ink"],
                    linewidth=1.6, zorder=6)
            ax.text(i, tot + (rng * 0.028 if tot >= 0 else -rng * 0.028),
                    f"{tot:+.2f}", ha="center",
                    va="bottom" if tot >= 0 else "top", fontsize=7.8,
                    fontweight="bold", color=C["ink"], zorder=7)
        ax.axhline(0, color=C["ink"], linewidth=0.9)
        ax.set_xticks(x)
        ax.set_xticklabels([f"{k}\n{c['v2']['per_family_cells'][k]}→"
                            f"{c['v3a']['per_family_cells'][k]}" for k in keys],
                           fontsize=8.0, linespacing=1.5)
        ax.set_ylabel("칸/FA프레임 Δ (v3-A − v2)", fontsize=8.6)
        ax.set_title(f"{arm}팔 「넓게 칠함」 분해 — 총 Δ {c['delta_total']:+.3f} "
                     f"= 규모 {c['delta_total_scale']:+.3f} + 조성 "
                     f"{c['delta_total_composition']:+.3f}\n"
                     f"칸/FA프레임 {c['v2']['cells_per_alarm']:.3f} → "
                     f"{c['v3a']['cells_per_alarm']:.3f}  ·  FA 프레임 "
                     f"{c['v2']['n_fa_frames']} → {c['v3a']['n_fa_frames']}",
                     fontsize=9.6, fontweight="bold", color=C["ink"], pad=7,
                     linespacing=1.4)
        ax.grid(axis="y", color=C["grid"], linewidth=0.7, zorder=0)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        if j == 0:
            ax.legend(fontsize=7.8, frameon=False, loc="upper left", ncol=1)
        ax.text(0.5, -0.215, "가족명 아래 숫자 = 그 가족의 절대 칸 수 v2 → v3-A "
                "(시드 합산 · 배타 귀속)", transform=ax.transAxes, ha="center",
                va="top", fontsize=6.9, color=C["mute"])

    # ---------------- 하단 우: 밴드 반경 법칙 ------------------------------
    ax = fig.add_subplot(gs[1, 2])
    mids = {"1": 1.0, "2": 3.5, "3a": 6.5, "3b": 10.0}
    R = T["tableE_radial"]["C"]
    for gen, col, lab in (("v2", V2COL, "v2"), ("v3a", V3COL, "v3-A")):
        xs = [mids[b] for b in ("1", "2", "3a", "3b") if R[b][gen]["rate"]]
        ys = [R[b][gen]["rate"] for b in ("1", "2", "3a", "3b") if R[b][gen]["rate"]]
        ax.plot(xs, ys, "o-", color=col, linewidth=2.0, markersize=6.4,
                markeredgecolor="#1B3352" if gen == "v3a" else "#8D97A5",
                label=f"{lab}  기울기 {R['loglog_slope_' + gen]:+.2f}")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks([1, 3.5, 6.5, 10])
    ax.set_xticklabels(["밴드1\n1.0 m", "밴드2\n3.5 m", "밴드3a\n6.5 m",
                        "밴드3b\n10.0 m"], fontsize=7.8)
    ax.set_xlabel("밴드 중점 거리 R (log)", fontsize=8.6)
    ax.set_ylabel("칸 발화율 (log)", fontsize=8.6)
    ax.set_title("C팔 반경 법칙 — 경계칸 「반경 성분」은 인공물인가\n"
                 "FA_CENSUS §3.3 의 test-core R^1.98 ↔ 본 무대 재현",
                 fontsize=9.6, fontweight="bold", color=C["ink"], pad=7,
                 linespacing=1.4)
    ax.grid(True, which="both", color=C["grid"], linewidth=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(fontsize=8.2, frameon=False, loc="upper left")
    sl2, sl3 = R["loglog_slope_v2"], R["loglog_slope_v3a"]
    ax.text(0.5, -0.215,
            f"미학습 무대에서 v2 기울기 {sl2:+.2f} = test-core 적합 R^1.98 의 독립 재현.\n"
            f"v3-A 는 {sl3:+.2f} 로 눕지만 σ 판정 축이 아니다 (층화 = 인쇄 의무).",
            transform=ax.transAxes, ha="center", va="top", fontsize=6.9,
            color=C["mute"], linespacing=1.6)

    # ---------------- 제목 · 푸터 -----------------------------------------
    fig.suptitle("계기판 ② FA 5가족 층화 — test-ext 4팔 · v2 → v3-A "
                 "(V-3 이행 · PREREG §2.2 「층화」 · P-12 접기 적용)",
                 fontsize=16.4, fontweight="bold", color=C["ink"], y=0.978)
    ex = T["sigma_summary"]["exceed"]
    fig.text(0.5, 0.945,
             "가족 = {장식 · 지형통계 · 조명 · 대리선 · 경계칸} · 다중 소속 허용 · "
             "P-12 등록 접기 적용 (경계칸의 반경 성분 band 3b → 지형통계형 하위 서명 · "
             "경계칸은 방위 성분 sector A/E 만)\n"
             "B · C · D 는 층이며 절대 합산하지 않는다 · 세대 비교는 rgb 대 rgb (3런 대 3런) · "
             f"σ(ddof=1) 초과 가족 {len(ex)} / {T['sigma_summary']['n_tested']} — "
             "본 절은 인쇄 의무이지 판정 축이 아니다",
             ha="center", va="top", fontsize=9.6, color=C["mute"], linespacing=1.8)
    p = T["params"]
    rs = T["recon_summary"]
    footer(fig,
           "원장 experiments/v3_0823/verdict_fa_family.json · fa_events_textext.csv · "
           "cell_photometry_textext.csv   |   점수 덤프 eval_v3textext/<run>/{,bd/} "
           "(v2 9런 중 rgb 3런 사용) · eval_v3a_textext/rgb_s{42,43,44}/{,bd/} (v3-A 3런)"
           f"   |   운용점 τ_op = {p['tau_op']} · 공표치 대조 "
           f"{rs['n_checks_matched']}/{rs['n_checks']} 일치 · 불일치 덤프 "
           f"{rs['n_mismatch']}\n"
           "분모 C·D팔 각 5,760칸 (288프레임 × 20칸 · 전 칸 GT 음성) · B팔 4,560 GT-음성칸 · "
           "A팔은 참고행 (패널 미표시)   |   가족 임계 조명 "
           f"{p['LIGHT_RATIO']} (0.50/0.70 병기) · 대리선 P90 = {p['LINE_P90']} "
           f"(test-ext 가시칸 재산출) · 장식 ≥ {p['DECO_PX']} DS4화소 (5/80 병기)\n"
           "장식형은 test-ext 에서 .idseg.npz + VG-09 키별 귀속기로 [기계] — test-core 센서스의 "
           "[수동] 2씬 오버레이와 계측기가 다르므로 두 무대 수치를 나란히 놓지 않는다"
           f"   |   CPU 전용 · 재추론 0 · 재렌더 0 · GPU 0 · 측정 {DATE}")

    save(fig, "panel_e_family_strata.png")
    plt.close(fig)


if __name__ == "__main__":
    sys.exit(main())
