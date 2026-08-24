#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""amodal5_panel_g.py — panel (g) 「아모달 헤드는 무엇을 그리는가」 (CPU 전용 · 새 추론 0).

    PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES= \
      python3 experiments/v3_0823/code/amodal5_panel_g.py [--force]

산출 → `experiments/v3_0823/panels/verdict/panel_g_amodal.png`

행 = panel_f 와 **같은 4컷** (PANELS_VERDICT §7.1). 열 = 세 시선.
  (1) 입력 + GT 아모달 윤곽(투영)   — 원본 컷 + 아모달 GT 마스크 경계(초록 실선)
  (2) v2세대 예측 마스크            — 같은 컷 + 픽셀 확률 히트(inferno) + 같은 초록 윤곽
  (3) v3세대(격리) 예측 마스크      — 동일

**규약** (panel_f 와 같은 문법 — `verdict_panel_detvsours.py` 에서 폰트·색·footer·save 복사)
  1. 한국어 라벨  2. 출처 푸터  3. 좌상단 칩 + 좌하단 주석 + 우하단 출처의 3점 배치
  4. 타일 안 대형 글씨 금지(D99)  5. 기계 자기점검 통과해야 저장  6. PNG ≤ 2 MB
  7. **[격리·진단] 배너** — 두 체크포인트 모두 훼손된 학습이라는 사실을 그림 안에 인쇄한다.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
from matplotlib import font_manager, rcParams          # noqa: E402

ROOT = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V3 = os.path.join(ROOT, "experiments/v3_0823")
DAY = os.path.join(ROOT, "experiments/dayrun_0820")
OUT = os.path.join(V3, "panels/verdict")
A5 = os.path.join(V3, "amodal5")
os.makedirs(OUT, exist_ok=True)

# ---- [복사: verdict_panel_detvsours.py L58-81] 폰트 · 색 --------------------
_FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
for _i in (0, 1, 2, 3, 4):
    try:
        font_manager.fontManager.addfont(_FONT)
        break
    except Exception:
        pass
rcParams["font.family"] = ["Noto Sans CJK KR", "Noto Sans CJK JP", "DejaVu Sans"]
_have = {f.name for f in font_manager.fontManager.ttflist}
rcParams["font.family"] = [n for n in rcParams["font.family"] if n in _have] or ["DejaVu Sans"]
rcParams["axes.unicode_minus"] = False
rcParams["savefig.facecolor"] = "white"
rcParams["figure.facecolor"] = "white"

C = dict(rgb="#4C6FBF", depth="#D97C2B", b2="#7E8794", pub="#B9C2D0", cor="#2F4B7C",
         ok="#2E7D5B", bad="#B03A48", grid="#DDE1E6", ink="#1F2429", mute="#5C6672")
DATE = "2026-08-24"
GTCOL = "#25E07A"
TIERCOL = dict(V="#2F4B7C", H="#B03A48", E="#C08400")
TIERKR = dict(V="보이는 낙차", H="숨은 낙차", E="테두리만")
GENCOL = dict(v2gen="#7E5BB8", v3gen="#1E8C86")
GENKR = dict(v2gen="v2세대  rgb_s42_aux", v3gen="v3세대(격리)  rgb_s42_aux")


def footer(fig, text, y=0.012):
    """[복사: verdict_panels.py L76-79]"""
    fig.text(0.5, y, text, ha="center", va="bottom", fontsize=7.4,
             color=C["mute"], family=rcParams["font.family"], linespacing=1.55)


def save(fig, name, dpi=130):
    """[복사: verdict_panels.py L82-95] 저장 + 2 MB 규율."""
    p = os.path.join(OUT, name)
    fig.savefig(p, dpi=dpi, bbox_inches="tight", pad_inches=0.22)
    import PIL.Image as I
    sz = os.path.getsize(p)
    if sz > 2_000_000:
        im = I.open(p).convert("RGB")
        im.quantize(colors=256, method=I.MEDIANCUT).save(p, optimize=True)
        sz = os.path.getsize(p)
    dim = I.open(p).size
    print(f"  {name:30s} {sz / 1024:8.0f} KB  {dim}")
    return p, sz, dim


import numpy as np                                     # noqa: E402
import matplotlib.pyplot as plt                        # noqa: E402
from matplotlib.lines import Line2D                     # noqa: E402
from PIL import Image                                   # noqa: E402

IMW, IMH = 640, 360
CMAP = plt.get_cmap("inferno")
GENS = ("v2gen", "v3gen")

ROWS = [
    dict(fid="on/scene14/L7__s20260819__0002.png", tier="V",
         note="같은 광장 · 낙차의 몸체가 보이는 시점",
         read="보이는 층 — 여기서 잘 그리는 것은 「추론」의 증거가 아니다"),
    dict(fid="on/scene14/L5__s20260819__0006.png", tier="H",
         note="같은 광장(scene14) · 지평선 뒤로 몸체가 사라진 시점",
         read="몸체가 0픽셀인데도 마스크가 그 자리에 실린다"),
    dict(fid="on/scene15/L0__s20260820__0006.png::boost_h", tier="H",
         note="골목 회랑(scene15) · 굽이 뒤에 낙차",
         read="아모달 영역이 작다(3.5%) — 농축이 낮으면 우연과 구분이 안 된다"),
    dict(fid="on/scene18/L7__s20260821__0000.png::boost_e2", tier="E",
         note="해안 테라스(scene18) · 테두리만 지평선에 걸린 시점",
         read="E 층에서는 두 세대 모두 사실상 침묵한다 (덮음 0.007)"),
]


def _blank(ax, img):
    if not (isinstance(img, np.ndarray) and img.ndim == 3 and float(img.std()) > 1.0):
        raise SystemExit("[fatal] 컷 이미지가 비었거나 단색이다 (imshow 전 게이트)")
    ax.imshow(img)
    ax.set_xticks([]); ax.set_yticks([])
    ax.tick_params(length=0)
    ax.set_xlim(0, IMW); ax.set_ylim(IMH, 0)
    for s in ax.spines.values():
        s.set_color(C["grid"]); s.set_linewidth(1.0)


def _chip(ax, x, y, txt, fc, *, ha="left", va="top", fs=9.0, tc="white", z=9, pad=3.0):
    ax.text(x, y, txt, transform=ax.transAxes, ha=ha, va=va, fontsize=fs,
            color=tc, fontweight="bold", zorder=z,
            bbox=dict(fc=fc, ec="none", pad=pad, alpha=.94))


def _note(ax, x, y, txt, *, ha="left", fs=8.4, alpha=.62):
    ax.text(x, y, txt, transform=ax.transAxes, ha=ha, va="bottom", fontsize=fs,
            color="white", zorder=9, bbox=dict(fc="#000000", ec="none", pad=2.4, alpha=alpha))


def gt_outline(ax, gt):
    """GT 아모달 마스크 경계 — 검정 밑선 + 초록 실선 (1·2·3열 공통 문법)."""
    cs0 = ax.contour(gt.astype(float), levels=[0.5], colors="black", linewidths=3.2, zorder=6)
    cs1 = ax.contour(gt.astype(float), levels=[0.5], colors=GTCOL, linewidths=1.8, zorder=7)
    return cs0, cs1


def build(force):
    rec = np.load(os.path.join(A5, "records.npz"))
    idx = json.load(open(os.path.join(A5, "index.json")))
    pm = np.load(os.path.join(A5, "panel_masks.npz"))
    T = json.load(open(os.path.join(A5, "tables.json")))
    frames = {r["key"]: r for r in json.load(open(os.path.join(A5, "frames.json")))["frames"]}
    pos = {r["frame_id"]: i for i, r in enumerate(idx["rows"])}
    NPIX = 512 * 512

    # ---- 행별 수치 재계산 (원장에서 직접) ---------------------------------
    for r in ROWS:
        i = pos[r["fid"]]
        row = idx["rows"][i]
        if row["tier"] != r["tier"]:
            raise SystemExit(f"[fatal] 층 불일치 {r['fid']}: {row['tier']} != {r['tier']}")
        fr = frames[r["fid"]]
        r["rgb"] = fr["rgb"]
        r["gt_path"] = fr["gt_mask"]
        r["a_gt"] = float(rec["a_gt"][i])
        r["area_frac"] = r["a_gt"] / NPIX
        for g in GENS:
            mt = float(rec[f"{g}__mass_tot"][i])
            mi = float(rec[f"{g}__mass_in"][i])
            din = mi / max(r["a_gt"], 1)
            dout = (mt - mi) / max(NPIX - r["a_gt"], 1)
            r[g] = dict(frac_in=mi / max(mt, 1e-9), dens_in=din, dens_out=dout,
                        enrich=din / max(dout, 1e-9), pmax_in=float(rec[f"{g}__pmax_in"][i]),
                        cov=float(rec[f"{g}__inter50"][i]) / max(r["a_gt"], 1),
                        fire_frac=float(rec[f"{g}__pred50"][i]) / NPIX)
        if r["fid"] not in [k.split("|", 1)[1] for k in pm.files]:
            raise SystemExit(f"[fatal] 패널 마스크 덤프에 없음: {r['fid']}")
    print("[gate] 행 검산 통과")
    for r in ROWS:
        print(f"   {r['tier']}  {r['fid']}\n      GT 아모달 면적 {r['area_frac']:.3f} · "
              + " · ".join(f"{g} 농축 {r[g]['enrich']:.2f} 안쪽질량 {r[g]['frac_in']:.2f} "
                           f"덮음 {r[g]['cov']:.2f}" for g in GENS))

    # ---- 그림 -------------------------------------------------------------
    fig = plt.figure(figsize=(15.8, 17.2))
    gs = fig.add_gridspec(4, 3, left=.043, right=.988, top=.767, bottom=.126,
                          hspace=.055, wspace=.014)
    pos_of = lambda k, j: gs[k, j].get_position(fig)   # noqa: E731  (D99: add_subplot 금지)
    tiles = []
    contours = []

    for k, r in enumerate(ROWS):
        img = np.asarray(Image.open(r["rgb"]).convert("RGB").resize((IMW, IMH), Image.LANCZOS))
        gt = np.asarray(Image.open(r["gt_path"]).convert("L").resize((IMW, IMH), Image.NEAREST),
                        np.uint8) > 127
        for j in range(3):
            ax = fig.add_subplot(gs[k, j])
            _blank(ax, img)
            if j == 0:
                contours.append(gt_outline(ax, gt))
                t = r["tier"]
                _chip(ax, .014, .972, f"  {t}  ·  {TIERKR[t]}  ", TIERCOL[t], fs=12.0, pad=4.4)
                _chip(ax, .986, .972, f"아모달 GT 면적 {r['area_frac'] * 100:.1f}%",
                      "#000000", ha="right", fs=9.0)
                _note(ax, .014, .030, r["note"])
                _note(ax, .986, .030, "GT = 가림 무시 프리즘 실루엣", ha="right", fs=7.2, alpha=.55)
            else:
                g = GENS[j - 1]
                mp = pm[f"{g}|{r['fid']}"].astype(np.float32)
                mp = np.asarray(Image.fromarray(mp, mode="F").resize((IMW, IMH), Image.BILINEAR),
                                np.float32)
                rgba = CMAP(np.clip(mp, 0, 1))
                rgba[..., 3] = 0.06 + 0.72 * np.clip(mp, 0, 1)
                ax.imshow(rgba, zorder=2)
                contours.append(gt_outline(ax, gt))
                s = r[g]
                _chip(ax, .014, .972,
                      f"윤곽 안 질량 {s['frac_in'] * 100:.0f}%  ·  농축 {s['enrich']:.1f}배",
                      GENCOL[g], fs=10.0)
                _chip(ax, .986, .972, f"윤곽 안 최대 p {s['pmax_in']:.2f}", "#000000",
                      ha="right", fs=9.0)
                _note(ax, .014, .030,
                      f"안 평균확률 {s['dens_in']:.3f} · 밖 {s['dens_out']:.3f} · "
                      f"덮음@0.5 {s['cov']:.2f}")
                _note(ax, .986, .030, f"{g} · best.pt", ha="right", fs=7.2, alpha=.55)
            tiles.append((k, j, ax))
        bb = pos_of(k, 0)
        fig.text(.019, (bb.y0 + bb.y1) / 2, f"{k + 1}행  ·  {r['tier']}  {TIERKR[r['tier']]}",
                 rotation=90, ha="center", va="center", fontsize=12.0,
                 fontweight="bold", color=TIERCOL[r["tier"]])

    # ---- 열 머리글 ---------------------------------------------------------
    heads = [("입력 + 정답 아모달 윤곽", "초록 실선 = 가림을 무시한 낙차의 투영 실루엣", C["ink"]),
             ("v2세대 aux 마스크", "타깃 57.8%가 거짓 공백으로 학습된 런", GENCOL["v2gen"]),
             ("v3세대(격리) aux 마스크", "train 2,598 중 648장만 마스크를 받은 런", GENCOL["v3gen"])]
    for j, (t, s, col) in enumerate(heads):
        bb = pos_of(0, j)
        xc = (bb.x0 + bb.x1) / 2
        fig.text(xc, .7855, t, ha="center", va="bottom", fontsize=16.0,
                 fontweight="bold", color=col)
        fig.text(xc, .7740, s, ha="center", va="bottom", fontsize=9.4, color=C["mute"])

    # ---- 제목 + 격리 배너 --------------------------------------------------
    fig.text(.043, .991, "아모달 헤드는 무엇을 그리는가", fontsize=27, fontweight="bold",
             color=C["ink"], ha="left", va="top")
    fig.add_artist(plt.Rectangle((.043, .9455), .945, .0225, transform=fig.transFigure,
                                 fc="#FBE9EC", ec=C["bad"], lw=1.2, zorder=0))
    fig.text(.0555, .9568,
             "[격리 · 진단]   두 체크포인트 모두 「훼손된 학습」이다 — 본 A/B 판정에 혼입하지 "
             "않는다 (PREREG §5.6 · D82 ③ · RT_LEDGER_B N-5).  약한 마스크는 "
             "「아모달은 불가능」의 증거가 아니고, 좋은 마스크는 제대로 학습했을 때의 하한이다.",
             fontsize=10.2, color=C["bad"], ha="left", va="center", fontweight="bold")

    # ---- 상단 집계 표 ------------------------------------------------------
    b = T["b"]
    ytab = .9215
    fig.text(.043, ytab, "test-core H 96장 (엄격 은닉 · 낙차 0픽셀) 집계",
             fontsize=10.6, color=C["ink"], ha="left", va="top", fontweight="bold")
    XC = [.360, .500, .640, .790, .930]
    for x, h in zip(XC, ["윤곽 안 농축", "농축>1 프레임", "안 평균p ≥ .05 프레임",
                         "트윈 Δ(on−off)", "on>off 프레임"]):
        fig.text(x, ytab, h, fontsize=10.2, color=C["mute"], ha="center", va="top",
                 fontweight="bold")
    for i, g in enumerate(GENS):
        yy = .9010 - i * .0205
        r1, tw = b[f"core_H|{g}"], T["b_twin"][g]
        fig.text(.043, yy, GENKR[g], fontsize=10.6, color=GENCOL[g], ha="left", va="top",
                 fontweight="bold")
        for x, v in zip(XC, [f"{r1['enrich'][0]:.2f}배", f"{r1['p_enrich_gt1']:.3f}",
                             f"{r1['p_floor']:.3f}", f"{tw['delta'][0]:+.3f}",
                             f"{tw['frac_on_gt_off']:.3f}"]):
            fig.text(x, yy, v, fontsize=10.6, ha="center", va="top", color=C["ink"],
                     fontweight="bold")
    fig.text(.043, .8570,
             "농축 = 윤곽 안 평균확률 ÷ 윤곽 밖 평균확률 (1.0 = 아무 데나 칠한 것과 구분 불가).  "
             "트윈 Δ = 같은 컷에서 낙차만 뺐을 때 윤곽 안 평균확률의 감소분 (96짝).",
             fontsize=9.4, color=C["mute"], ha="left", va="top")
    fig.text(.043, .8435,
             "정직 병기 — 그 트윈은 광학적으로 조용하지 않다: 96짝 전부 frac(|ΔI|>8) ≥ 0.001 "
             "(평균 0.075, 윤곽 안에서는 0.278).  즉 이 그림은 「안 보이는 것을 추론했다」와 "
             "「보이는 광학 흔적을 읽었다」를 갈라주지 못한다.",
             fontsize=9.4, color=C["bad"], ha="left", va="top")

    # ---- 확률 램프 ---------------------------------------------------------
    cax = fig.add_axes([.878, .8145, .110, .0080])
    cax.imshow(np.linspace(0, 1, 256).reshape(1, -1), aspect="auto", cmap=CMAP,
               extent=(0, 1, 0, 1))
    cax.set_yticks([]); cax.set_xticks([0, .5, 1])
    cax.set_xticklabels(["0", ".50", "1"], fontsize=7.4)
    cax.axvline(.5, color="white", lw=1.6)
    cax.tick_params(length=2, pad=1.2)
    for s in cax.spines.values():
        s.set_color(C["grid"])
    fig.text(.872, .8185, "픽셀 확률 램프  ·  흰 선 0.5", ha="right", va="center",
             fontsize=8.4, color=C["mute"])

    # ---- 범례 --------------------------------------------------------------
    fig.legend(handles=[
        Line2D([], [], color=GTCOL, lw=2.4, label="정답 아모달 윤곽 (가림 무시 투영)"),
        Line2D([], [], color="none", marker="s", ms=9, markerfacecolor=CMAP(.85),
               markeredgecolor="#BBBBBB", label="예측 픽셀 확률 높음"),
        Line2D([], [], color="none", marker="s", ms=9, markerfacecolor=CMAP(.18),
               markeredgecolor="#BBBBBB", label="예측 픽셀 확률 낮음")],
        loc="upper left", bbox_to_anchor=(.043, .8265), ncol=3, frameon=False,
        fontsize=9.6, handlelength=2.2, columnspacing=1.5)

    # ---- 하단 주석 띠 ------------------------------------------------------
    fig.add_artist(plt.Rectangle((.043, .0525), .945, .0625, transform=fig.transFigure,
                                 fc="#F3F5F8", ec=C["grid"], lw=1.2, zorder=0))
    a = T["a"]
    fig.text(.5155, .0985,
             "H 층에서는 마스크가 윤곽 안에 실린다 (농축 "
             f"{b['core_H|v2gen']['enrich'][0]:.1f}배 / {b['core_H|v3gen']['enrich'][0]:.1f}배)   "
             "→   그러나 처음 보는 씬(test-ext H)에서는 농축 "
             f"{b['ext_H|v2gen']['enrich'][0]:.1f}배 / {b['ext_H|v3gen']['enrich'][0]:.1f}배 로 "
             "무너진다",
             ha="center", va="center", fontsize=14.0, fontweight="bold", color=C["ink"])
    fig.text(.5155, .0690,
             f"IoU@0.5 는 test-core H 에서 {a['core_H|v2gen']['iou'][0]:.3f} / "
             f"{a['core_H|v3gen']['iou'][0]:.3f} (전면 도포 기준선 "
             f"{a['core_H|v2gen']['iou_paint_all'][0]:.3f}) · "
             f"V 층 {a['core_V|v2gen']['iou'][0]:.3f} / {a['core_V|v3gen']['iou'][0]:.3f} "
             f"(기준선 {a['core_V|v2gen']['iou_paint_all'][0]:.3f} — 기준선 이하) · "
             f"E 층 {a['core_E|v2gen']['iou'][0]:.3f} / {a['core_E|v3gen']['iou'][0]:.3f}"
             "   ·   마스크 품질 자체는 낮다",
             ha="center", va="center", fontsize=10.4, color=C["bad"])

    # ---- 출처 푸터 ---------------------------------------------------------
    fids = "  ·  ".join(f"{r['tier']}행 {r['fid']}" for r in ROWS)
    footer(fig,
           "컷  " + fids + "  (panel_f 와 동일한 4컷 · PANELS_VERDICT §7.1)\n"
           "체크포인트  experiments/dayrun_0820/runs/v2/rgb_s42_aux/best.pt (ep6) · "
           "experiments/v3_0823/runs/v3a/rgb_s42_aux/best.pt (ep8)  —  "
           "model_factory use_mask_head=True 로 재구축, dense 출력에 sigmoid\n"
           "아모달 GT  experiments/dayrun_0820/annotations/amodal/*.png "
           "(가림 무시 프리즘 실루엣 · 960×540 · amodal_masks.py) · "
           "전처리는 polar_dataset._load_x 와 동일 (512² BILINEAR squash + ImageNet 정규화)\n"
           "수치 원장  experiments/v3_0823/amodal5/{records.npz, tables.json, twin_delta.json}  ·  "
           "생성기 experiments/v3_0823/code/amodal5_panel_g.py  ·  "
           "새 학습 0 · 새 렌더 0 · git 무접촉  ·  " + DATE,
           y=.008)

    selfcheck(fig, tiles, cax, contours)
    return save(fig, "panel_g_amodal.png", dpi=120)


def selfcheck(fig, tiles, cax, contours):
    """저장 직전 기계 자기점검 (D99 강화판) — 백지 타일·대형 낙관·윤곽 누락을 전부 막는다."""
    from matplotlib.image import AxesImage
    from matplotlib.text import Text
    if len(tiles) != 12:
        raise SystemExit(f"[fatal] 타일 {len(tiles)}개 != 12")
    if len(fig.axes) != 13:
        raise SystemExit(f"[fatal] 축 {len(fig.axes)}개 != 13 — 빈 축이 타일을 덮었을 수 있다")
    if set(fig.axes) != {a for _, _, a in tiles} | {cax}:
        raise SystemExit("[fatal] 정체 불명의 축이 그림에 있다")
    if len(contours) != 12:
        raise SystemExit(f"[fatal] GT 윤곽 {len(contours)}쌍 != 12")
    for cs0, cs1 in contours:
        if not len(cs1.get_paths()):
            raise SystemExit("[fatal] GT 윤곽이 비었다 (경로 0개)")
    for k, j, ax in tiles:
        ims = [a for a in ax.get_children() if isinstance(a, AxesImage)]
        need_n = 1 if j == 0 else 2
        if len(ims) != need_n:
            raise SystemExit(f"[fatal] 타일({k},{j}) 이미지 {len(ims)}장 != {need_n}")
        base = np.asarray(ims[0].get_array(), np.float64)
        if base.shape[:2] != (IMH, IMW) or float(base.std()) <= 1.0:
            raise SystemExit(f"[fatal] 타일({k},{j}) 실사 이미지가 비었다 "
                             f"(shape {base.shape} std {float(base.std()):.3f})")
        if j > 0:
            heat = np.asarray(ims[1].get_array(), np.float64)
            if heat.shape != (IMH, IMW, 4):
                raise SystemExit(f"[fatal] 타일({k},{j}) 히트 오버레이 shape {heat.shape}")
            if float(heat[..., 3].max()) <= 0.06 + 1e-9:
                raise SystemExit(f"[fatal] 타일({k},{j}) 히트가 전부 투명 (마스크 미적재?)")
        txts = [a for a in ax.get_children() if isinstance(a, Text) and a.get_text().strip()]
        if len(txts) < 4:
            raise SystemExit(f"[fatal] 타일({k},{j}) 칩/주석 {len(txts)}개 < 4")
        big = [(a.get_text(), a.get_fontsize()) for a in txts if a.get_fontsize() > 12]
        if big:
            raise SystemExit(f"[fatal] 타일({k},{j}) 대형 낙관 금지 위반: {big}")
    print(f"[gate] 자기점검 통과 — 12/12 타일 실사+오버레이+윤곽 (축 {len(fig.axes)}개)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    dst = os.path.join(OUT, "panel_g_amodal.png")
    if os.path.exists(dst) and not a.force:
        print(f"  이미 있음 (resume-safe): {dst}   — 다시 그리려면 --force")
        sys.exit(0)
    p, sz, dim = build(a.force)
    print(f"\n[done] {p}  {sz / 1024:.0f} KB  {dim[0]}×{dim[1]} px  "
          f"(2 MB 규율 {'통과' if sz <= 2_000_000 else '위반'})")
