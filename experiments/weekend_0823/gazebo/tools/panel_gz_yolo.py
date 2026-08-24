#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""panel_gz_yolo.py — 「다른 시뮬레이터에서도 같은가」 (CPU 전용, 재추론 0).

    PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES= python3 tools/panel_gz_yolo.py [--force]

산출 → `out_yolo/panel_gz_yolo.png`

2행 × 3열.  두 행은 **같은 눈높이(h 0.9 m)** 의 서로 다른 월드다 (행별 뷰 선택 규칙은 ROWS 주석).
  1행  gz_drop2 (V · preset_h0.9_d2) — 수직 0.80 m 단차, 낙차가 훤히 보이는 월드
  2행  gz_drop3 (H · preset_h0.9_d5) — 0.72 m 피트가 앞의 화단벽에 완전히 가려 위험 기여 픽셀 0

  (1) 입력 + 낙차 영역   — 원본 컷 + 낙차 프리즘의 투영 윤곽(초록 파선)
  (2) 검출기의 눈 (YOLO) — 동결 yolo_s42 상자 (τ_conf 0.25).  상자가 없으면
                          panel_f(D99)와 같은 문법의 좌상단 칩만 — 중앙 대형 낙관 금지.
  (3) 본 접근의 눈       — 동결 rgb_s42(v2)의 20칸 확률 (inferno 램프, 흰 실선 = p ≥ 0.5)

폰트·색·footer()·save()·_chip()·자기점검 규율은
`experiments/v3_0823/code/verdict_panel_detvsours.py` 의 것을 그대로 따른다.
새 렌더 0 · 새 추론 0 · GPU 0 · git 무접촉.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
from matplotlib import font_manager, rcParams          # noqa: E402

ROOT = "/home/vislab/Desktop/work_sy/Practice_NegObs"
GZ = os.path.join(ROOT, "experiments/weekend_0823/gazebo")
OUT = os.path.join(GZ, "out_yolo")
sys.path.insert(0, os.path.join(GZ, "tools"))
import gz_yolo_readout as R                            # noqa: E402

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
GTCOL = "#25E07A"
BOXCOL = "#D97C2B"
TIERCOL = dict(V="#2F4B7C", H="#B03A48", E="#C08400")
TIERKR = dict(V="보이는 낙차", H="숨은 낙차", E="테두리만")
DATE = "2026-08-24"

import numpy as np                                     # noqa: E402
import matplotlib.pyplot as plt                        # noqa: E402
from matplotlib.patches import Polygon, Rectangle      # noqa: E402
from matplotlib.lines import Line2D                    # noqa: E402
from PIL import Image                                  # noqa: E402

CMAP = plt.get_cmap("inferno")
IMW, IMH = 720, 405
TAU_SEG, TAU_YOLO = 0.5, 0.25
SEED = 42
# 행 선택 규칙 (결정적):
#   1행 gz_drop2 — 3시드 216컷 중 **하자드 팔 gz_drop2 에서 상자가 나온 유일한 컷**
#                  (yolo_s42 · preset_h0.9_d2 · conf 0.293).  다른 뷰를 골랐다면 검출은
#                  0건이 되므로, 이 컷은 검출기에게 **가장 유리한** 선택이다.
#   2행 gz_drop3 — GAZEBO_TRACK.md §8 이 이미 동결해 둔 H 대표 컷
#                  (`out/panels/b2_s42__gz_drop3__preset_h0.9_d5.png` 와 같은 뷰).
ROWS = [
    dict(world="gz_drop2", tier="V", view="preset_h0.9_d2",
         note="수직 0.80 m 단차 · 난간은 +Y 한쪽뿐",
         pick="3시드 216컷 중 gz_drop2 하자드 팔에 상자가 나온 유일한 컷"),
    dict(world="gz_drop3", tier="H", view="preset_h0.9_d5",
         note="0.72 m 피트가 0.61 m 화단벽 뒤 · 위험 기여 픽셀 0 (본문 §3)",
         pick="GAZEBO_TRACK §8 이 동결한 H 대표 뷰"),
]


def footer(fig, text, y=0.012):
    fig.text(0.5, y, text, ha="center", va="bottom", fontsize=7.6,
             color=C["mute"], family=rcParams["font.family"], linespacing=1.55)


def save(fig, name, dpi=130):
    p = os.path.join(OUT, name)
    fig.savefig(p, dpi=dpi, bbox_inches="tight", pad_inches=0.22)
    import PIL.Image as I
    sz = os.path.getsize(p)
    if sz > 2_000_000:
        im = I.open(p).convert("RGB")
        im.quantize(colors=256, method=I.MEDIANCUT).save(p, optimize=True)
        sz = os.path.getsize(p)
    dim = I.open(p).size
    return p, sz, dim


def _chip(ax, x, y, txt, fc, *, ha="left", va="top", fs=9.5, tc="white", z=9, pad=3.2):
    ax.text(x, y, txt, transform=ax.transAxes, ha=ha, va=va, fontsize=fs,
            color=tc, fontweight="bold", zorder=z,
            bbox=dict(fc=fc, ec="none", pad=pad, alpha=.94))


def _note(ax, x, y, txt, *, ha="left", fs=8.4, fc="#000000", alpha=.62):
    ax.text(x, y, txt, transform=ax.transAxes, ha=ha, va="bottom", fontsize=fs,
            color="white", zorder=9, bbox=dict(fc=fc, ec="none", pad=2.6, alpha=alpha))


def _blank(ax, img):
    if not (isinstance(img, np.ndarray) and img.ndim == 3 and float(img.std()) > 1.0):
        raise SystemExit("[fatal] 컷 이미지가 비었거나 단색이다 (imshow 전 게이트)")
    ax.imshow(img)
    ax.set_xticks([]); ax.set_yticks([])
    ax.tick_params(length=0)
    ax.set_xlim(0, IMW); ax.set_ylim(IMH, 0)
    for s in ax.spines.values():
        s.set_color(C["grid"]); s.set_linewidth(1.0)


def wedge_xy(cell, v):
    """gridspec 셀의 지면 쐐기 -> 패널 좌표 (infer_photo.wedge_polygons 와 같은 산식)."""
    b, s = cell // R.NS, cell % R.NS
    asc = np.asarray(R.ASC, float)
    az = np.radians(np.linspace(asc[R.NS - 1 - s], asc[R.NS - s], 24))
    r0, r1 = max(R.BND[b], 0.10), R.BND[b + 1]
    ring = np.concatenate([np.stack([r1 * np.cos(az), r1 * np.sin(az)], 1),
                           np.stack([r0 * np.cos(az[::-1]), r0 * np.sin(az[::-1])], 1)])
    pts = np.concatenate([ring, np.zeros((len(ring), 1))], 1)
    px, py, _ = R.project(pts, v["h"], v["pitch"], v["hfov"], v["W"], v["H"])
    ok = np.isfinite(px) & np.isfinite(py)
    if ok.sum() < 3:
        return None
    X, Y = px[ok] * (IMW / v["W"]), py[ok] * (IMH / v["H"])
    if X.max() < 0 or X.min() > IMW or Y.max() < 0 or Y.min() > IMH:
        return None
    return np.c_[X, Y]


def build():
    fig = plt.figure(figsize=(16.4, 9.6))
    gs = fig.add_gridspec(2, 3, left=.048, right=.988, top=.722, bottom=.170,
                          hspace=.055, wspace=.014)
    pos = lambda k, j: gs[k, j].get_position(fig)
    tiles, meta = [], []

    for k, r in enumerate(ROWS):
        w, VIEW = r["world"], r["view"]
        v = R.VIEWS[VIEW]
        img = np.asarray(Image.open(os.path.join(
            GZ, "frames", w, f"{w}_cap_{VIEW}_000.png")).convert("RGB")
            .resize((IMW, IMH), Image.LANCZOS))
        reg = R.region(w, VIEW, True)
        yj = json.load(open(os.path.join(OUT, "pred", f"yolo_s{SEED}", "json",
                                         f"{w}__{VIEW}__000.json")))
        boxes = [b for b in yj["boxes"] if b["conf"] >= TAU_YOLO]
        yc = json.load(open(os.path.join(OUT, "pred", f"yolo_s{SEED}", "json",
                                         f"{w}_ctrl__{VIEW}__000.json")))
        nctl = len([b for b in yc["boxes"] if b["conf"] >= TAU_YOLO])
        seg = json.load(open(os.path.join(GZ, "out", "json",
                                          f"rgb_s{SEED}__{w}__{VIEW}.json")))
        assert seg["cell_ids"] == R.CELLS and abs(seg["height_m"] - v["h"]) < 1e-9
        p = np.asarray(seg["probs"], float)
        pc = np.asarray(json.load(open(os.path.join(
            GZ, "out", "json", f"rgb_s{SEED}__{w}_ctrl__{VIEW}.json")))["probs"], float)
        gt = reg["gt_cells"]
        meta.append(dict(row=r, reg=reg, boxes=boxes, p=p, gt=gt, n_ctl_box=nctl, pc=pc))

        # ---- (1) 입력 + 낙차 영역 -----------------------------------------
        ax = fig.add_subplot(gs[k, 0]); _blank(ax, img)
        m = np.asarray(Image.fromarray((reg["mask"] * 255).astype(np.uint8))
                       .resize((IMW, IMH), Image.NEAREST), float) / 255.0
        ax.imshow(np.dstack([np.ones_like(m), np.ones_like(m), np.ones_like(m), m * .11])
                  * np.array([.145, .878, .478, 1.0]), zorder=2)
        cs = ax.contour(m, levels=[.5], colors="black", linewidths=3.4, zorder=3)
        cs2 = ax.contour(m, levels=[.5], colors=[GTCOL], linewidths=1.9,
                         linestyles=[(0, (5, 3))], zorder=4)
        _chip(ax, .014, .968, f"  {r['tier']}  ·  {TIERKR[r['tier']]}  ",
              TIERCOL[r["tier"]], fs=11.5, pad=4.4)
        _chip(ax, .986, .968, f"낙차 영역 {100.0 * reg['n_px'] / (v['W'] * v['H']):.0f}% 화면 "
                              f"·  정답 칸 {len(gt)}/20", "#000000", ha="right", fs=8.8)
        _note(ax, .014, .028, r["note"])
        _note(ax, .986, .028, VIEW.replace("preset_", "").replace("_", " · "),
              ha="right", fs=7.4, alpha=.55)
        tiles.append((k, 0, ax))

        # ---- (2) 검출기의 눈 ------------------------------------------------
        ax = fig.add_subplot(gs[k, 1]); _blank(ax, img)
        sx, sy = IMW / v["W"], IMH / v["H"]
        nhit = 0
        for b in boxes:
            x0, y0 = b["x0"] * sx, b["y0"] * sy
            ww, hh = (b["x1"] - b["x0"]) * sx, (b["y1"] - b["y0"]) * sy
            ax.add_patch(Rectangle((x0, y0), ww, hh, fill=False, ec="black", lw=4.2, zorder=3))
            ax.add_patch(Rectangle((x0, y0), ww, hh, fill=False, ec=BOXCOL, lw=2.4, zorder=4))
            cxp, cyp = int((b["x0"] + b["x1"]) / 2), int((b["y0"] + b["y1"]) / 2)
            nhit += int(0 <= cyp < v["H"] and 0 <= cxp < v["W"] and bool(reg["mask"][cyp, cxp]))
            ax.text(np.clip(x0 + 5, 4, IMW - 150), np.clip(y0 + 5, 42, IMH - 24),
                    f"낙차  conf {b['conf']:.2f}", ha="left", va="top", fontsize=9.0,
                    color="white", fontweight="bold", zorder=5,
                    bbox=dict(fc=BOXCOL, ec="black", lw=.9, pad=2.6, alpha=.96))
        if boxes:
            cells = set()
            for b in boxes:
                cells |= R.box_cells(b, v)
            _chip(ax, .014, .968, f"검출 {len(boxes)}건  ·  영역 중심 적중 {nhit}  "
                                  f"·  정답칸 {len(cells & set(gt))}", BOXCOL, fs=9.2)
            _note(ax, .014, .028, f"상자 면적 {100.0 * boxes[0]['w'] * boxes[0]['h']:.0f}% 화면 "
                                  f"— 낙차를 집은 게 아니라 장면을 통째로 감쌌다  ·  "
                                  f"대조군 트윈 상자 {nctl}개", fs=7.8)
        else:
            _chip(ax, .014, .968, "검출 0건  ·  상자 없음", BOXCOL, fs=9.6)
            _note(ax, .014, .028, f"τ_conf 0.25 이상 상자 0개  ·  이 시드는 gz_drop3 7뷰 "
                                  f"전부 0건  ·  대조군 트윈도 {nctl}개", fs=7.8)
        _chip(ax, .986, .968, f"yolo_s{SEED} · τ 0.25", "#000000", ha="right", fs=8.0)
        tiles.append((k, 1, ax))

        # ---- (3) 본 접근의 눈 ------------------------------------------------
        ax = fig.add_subplot(gs[k, 2]); _blank(ax, img)
        hid = []
        for i in np.argsort(p):
            xy = wedge_xy(int(i), v)
            if xy is None:
                if p[i] >= TAU_SEG:
                    hid.append(R.CELLS[i])
                continue
            pv = float(p[i])
            ax.add_patch(Polygon(xy, closed=True, fc=CMAP(pv), ec="none",
                                 alpha=0.06 + 0.56 * pv, zorder=2))
            ax.add_patch(Polygon(xy, closed=True, fc="none", ec="white",
                                 lw=1.7 if pv >= TAU_SEG else 0.5,
                                 alpha=1.0 if pv >= TAU_SEG else .30, zorder=3))
            if int(i) in gt:
                ax.add_patch(Polygon(xy, closed=True, fc="none", ec="black", lw=3.0, zorder=4))
                ax.add_patch(Polygon(xy, closed=True, fc="none", ec=GTCOL, lw=1.7,
                                     ls=(0, (5, 3)), zorder=5))
        fired = [R.CELLS[i] for i in np.where(p >= TAU_SEG)[0]]
        hit = [R.CELLS[i] for i in np.where(p >= TAU_SEG)[0] if int(i) in gt]
        _chip(ax, .014, .968, f"발화 {len(fired)}칸  ·  정답칸 적중 {len(hit)}칸"
                              + (f"  ·  헛발 {len(fired) - len(hit)}칸"
                                 if len(fired) - len(hit) else ""), C["cor"], fs=9.6)
        _chip(ax, .986, .968, f"정답칸 최대 p {(p[gt].max() if gt else float('nan')):.2f}",
              "#000000", ha="right", fs=8.8)
        nfc = int((pc >= TAU_SEG).sum())
        _note(ax, .014, .028,
              ("낙차가 보이는 월드 — 확률이 켜진다" if r["tier"] == "V"
               else "위험 픽셀이 0인데도 켜진다 (단서 단독 발화 · §4.4)")
              + f"   |   대조군 트윈도 {nfc}칸 발화 (최대 p {pc.max():.2f}) — 판별은 못 한다",
              fs=7.8)
        if hid:
            _note(ax, .986, .028, "칸이 화면 밖 · 미표시: " + ",".join(hid), ha="right",
                  fs=6.8, alpha=.55)
        meta[-1]["fired"], meta[-1]["hit"], meta[-1]["nhit_box"] = fired, hit, nhit
        meta[-1]["n_ctl_fire"] = nfc
        tiles.append((k, 2, ax))

        bb = pos(k, 0)
        fig.text(.022, (bb.y0 + bb.y1) / 2,
                 f"{k + 1}행  ·  {w}  ({r['tier']}  {TIERKR[r['tier']]})",
                 rotation=90, ha="center", va="center", fontsize=11.5,
                 fontweight="bold", color=TIERCOL[r["tier"]])

    # ---- 열 머리글 ----------------------------------------------------------
    heads = [("입력 + 낙차 영역", "초록 파선 = 월드 기하에서 투영한 낙차 프리즘 (가림 무시)",
              C["ink"]),
             ("검출기의 눈  (YOLO)", "상자 = 동결 예측 그대로 · τ_conf 0.25", BOXCOL),
             ("본 접근의 눈  (칸 확률)", "20칸 확률 · 흰 실선 = 발화(p ≥ 0.5)", C["cor"])]
    for j, (t, s, col) in enumerate(heads):
        bb = pos(0, j)
        xc = (bb.x0 + bb.x1) / 2
        fig.text(xc, .7420, t, ha="center", va="bottom", fontsize=14.5,
                 fontweight="bold", color=col)
        fig.text(xc, .7290, s, ha="center", va="bottom", fontsize=9.2, color=C["mute"])

    # ---- 제목 ---------------------------------------------------------------
    fig.text(.048, .992, "다른 시뮬레이터에서도 같은가 — Gazebo 제로샷", fontsize=25,
             fontweight="bold", color=C["ink"], ha="left", va="top")
    fig.text(.048, .9540,
             "두 행은 같은 눈높이(h 0.9 m · hFOV 60°)에서 찍은 서로 다른 월드다 — 위는 낙차가 "
             "보이는 월드, 아래는 화단벽에 완전히 가려 위험 픽셀이 0인 월드.  "
             "두 시스템 모두 Isaac 렌더로만 학습했고 Gazebo는 처음 본다 (양쪽 다 제로샷).",
             fontsize=12.2, color=C["mute"], ha="left", va="top")

    # ---- 상단 집계 표 --------------------------------------------------------
    RJ = json.load(open(os.path.join(OUT, "readout.json")))
    row = {(d["tier"], d["family"]): d for d in RJ["combined"]}
    XC = [.400, .560, .720, .880]
    ytab = .9330
    fig.text(.048, ytab, "하자드 팔 · 3시드 pooled · negobs 프리셋 7뷰",
             fontsize=10.4, color=C["ink"], ha="left", va="top", fontweight="bold")
    for x, h in zip(XC, ["V  발화율", "V  정답칸 정합", "H  발화율", "H  정답칸 정합"]):
        fig.text(x, ytab, h, fontsize=10.4, color=C["mute"], ha="center", va="top",
                 fontweight="bold")
    for i, (lab, fam, col) in enumerate([("검출기 YOLO  (τ_conf 0.25)", "YOLO(검출)", BOXCOL),
                                         ("본 접근 v2 rgb  (τ 0.5)", "v2 rgb", C["cor"]),
                                         ("본 접근 v2 b2  (τ 0.5)", "v2 b2", C["pub"])]):
        yy = .9110 - i * .0210
        fig.text(.048, yy, lab, fontsize=10.4, color=col, ha="left", va="top",
                 fontweight="bold")
        for x, (t, k) in zip(XC, [("V", "fire"), ("V", "hit"), ("H", "fire"), ("H", "hit")]):
            val = row[(t, fam)][k]
            zero = (val == 0.0)
            fig.text(x, yy, "0.000" if zero else f"{val:.3f}", fontsize=10.8,
                     ha="center", va="top", color=C["bad"] if zero else C["ink"],
                     fontweight="bold" if zero else "normal")
    fig.text(.048, .8450,
             "분모  V = gz_drop1·gz_drop2 7뷰 + gz_drop4 근·중거리 5뷰 (57)  ·  "
             "H = gz_drop3 7뷰 (21).  「정답칸 정합」 = 20칸 격자에서 낙차 발자국이 덮는 칸을 "
             "적어도 하나 켰는가 (검출은 det2cell 규칙으로 상자→칸 변환).",
             fontsize=9.2, color=C["mute"], ha="left", va="top")
    fig.text(.048, .8290,
             "검출기의 H 정답칸 정합 0.000 은 3시드 전부의 실측이다 — 상자가 아예 없어서가 "
             "아니라(s43·s44는 상자를 낸다) 그 상자가 대조군 트윈에서 IoU 0.99–1.00 으로 "
             "똑같이 재현되기 때문이다 (위험이 없어도 같은 상자가 나온다).",
             fontsize=9.2, color=C["bad"], ha="left", va="top")

    # ---- 확률 램프 -----------------------------------------------------------
    cax = fig.add_axes([.878, .8010, .110, .0090])
    cax.imshow(np.linspace(0, 1, 256).reshape(1, -1), aspect="auto", cmap=CMAP,
               extent=(0, 1, 0, 1))
    cax.set_yticks([]); cax.set_xticks([0, .5, 1])
    cax.set_xticklabels(["0", ".50", "1"], fontsize=7.4)
    cax.axvline(.5, color="white", lw=1.6)
    cax.tick_params(length=2, pad=1.2)
    for s in cax.spines.values():
        s.set_color(C["grid"])
    fig.text(.872, .8055, "칸 확률 램프  ·  흰 선 τ 0.5", ha="right", va="center",
             fontsize=8.2, color=C["mute"])

    fig.legend(handles=[
        Line2D([], [], color=GTCOL, lw=2.2, ls=(0, (5, 3)), label="낙차 프리즘 투영 윤곽"),
        Line2D([], [], color=BOXCOL, lw=2.6, label="YOLO 동결 상자 (τ 0.25)"),
        Line2D([], [], color="white", lw=1.8, marker="s", ms=9,
               markerfacecolor=CMAP(.85), markeredgecolor="white",
               label="본 접근 발화 칸 (p ≥ 0.5)"),
        Line2D([], [], color="none", marker="s", ms=9, markerfacecolor=CMAP(.18),
               markeredgecolor="#BBBBBB", label="미발화 칸 (p < 0.5)")],
        loc="upper left", bbox_to_anchor=(.048, .8080), ncol=4, frameon=False,
        fontsize=9.2, handlelength=2.2, columnspacing=1.5)

    # ---- 하단 주석 띠 ---------------------------------------------------------
    fig.add_artist(plt.Rectangle((.048, .0640), .940, .0740, transform=fig.transFigure,
                                 fc="#F3F5F8", ec=C["grid"], lw=1.2, zorder=0))
    import csv as _csv
    _bx = [r for r in _csv.DictReader(open(os.path.join(OUT, "boxes.csv")))
           if r["idx"] == "000"]
    _nh = sum(1 for r in _bx if r["hazard"] == "1")
    _nc = len(_bx) - _nh
    fig.text(.518, .1140,
             f"Gazebo 8월드 · 216컷 · 3시드에서 검출기가 τ 0.25 이상으로 낸 상자는 전부 "
             f"{len(_bx)}개다 — 하자드 팔 {_nh}개, 위험이 아예 없는 대조군 팔 {_nc}개.",
             ha="center", va="center", fontsize=13.4, fontweight="bold", color=C["ink"])
    fig.text(.518, .0865,
             "검출의 E/H 침묵은 우리 Isaac 씬에서만 나타나는 성질이 아니다 (방향성 서술 · "
             "단일 런 · σ 없음).  단, 본 접근의 발화도 여기서는 낙차와 대조군을 거의 "
             "가르지 못한다 — GAZEBO_TRACK §4.1 트윈 Δ +0.019.",
             ha="center", va="center", fontsize=10.6, color=C["bad"])

    footer(fig,
           "컷  " + "  ·  ".join(
               f"{r['tier']}행 frames/{r['world']}/{r['world']}_cap_{r['view']}_000.png "
               f"({r['pick']})" for r in ROWS)
           + "  — sha256 216/216 검증 · 재캡처 0\n"
           f"원장  검출 out_yolo/pred/yolo_s{SEED}/json/*.json  "
           f"(동결 dayrun_0820/runs/yolo_s{SEED}/weights/best.pt · imgsz 512 · 예측 바닥 conf 0.05 "
           f"· 판독 τ_conf 0.25)  ·  집계 out_yolo/readout.json\n"
           f"칸 확률  out/json/rgb_s{SEED}__<world>__<view>.json  "
           f"(GAZEBO_TRACK.md §4 동결 덤프 · infer_photo.py --fit squash --tau 0.5, 새 추론 0)  ·  "
           f"격자 gridspec_v1.json (PROVISIONAL-GRID-V1 · 4밴드 × 5섹터)\n"
           f"낙차 영역  make_worlds.py 의 프리즘 리터럴(x·y·깊이)을 manifest 실측 포즈로 투영 — "
           f"amodal_masks.py 규약(가림 무시)과 동일, 격자 반경 12 m 로 클립.  "
           f"[진단·서술용 · 사전등록 계기판 비인용]  ·  " + DATE,
           y=.006)

    selfcheck(fig, tiles, cax, meta)
    return save(fig, "panel_gz_yolo.png", dpi=124)


def selfcheck(fig, tiles, cax, meta):
    """저장 직전 기계 자기점검 — 빈 타일·대형 낙관 회귀 차단 (panel_f 규율)."""
    from matplotlib.image import AxesImage
    from matplotlib.text import Text
    if len(tiles) != 6:
        raise SystemExit(f"[fatal] 타일 {len(tiles)}개 != 6")
    if len(fig.axes) != 7:
        raise SystemExit(f"[fatal] 축 {len(fig.axes)}개 != 7 — 빈 축이 타일을 덮었을 수 있다")
    if set(fig.axes) != set(a for _, _, a in tiles) | {cax}:
        raise SystemExit("[fatal] 정체 불명의 축이 그림에 있다")
    for k, j, ax in tiles:
        ims = [a for a in ax.get_children() if isinstance(a, AxesImage)]
        need_im = 2 if j == 0 else 1                    # 1열은 사진 + 영역 오버레이
        if len(ims) != need_im:
            raise SystemExit(f"[fatal] 타일({k},{j}) 이미지 {len(ims)}장 != {need_im}")
        arr = np.asarray(ims[0].get_array(), dtype=np.float64)
        if arr.shape[:2] != (IMH, IMW) or float(arr.std()) <= 1.0:
            raise SystemExit(f"[fatal] 타일({k},{j}) 이 비었다 "
                             f"(shape {arr.shape} std {float(arr.std()):.3f})")
        m = meta[k]
        if j == 0 and m["reg"]["n_px"] <= 0:
            raise SystemExit(f"[fatal] 타일({k},0) 낙차 영역이 0 px")
        if j == 1:
            nrect = sum(isinstance(a, Rectangle) and a.get_fill() is False
                        for a in ax.get_children())
            if nrect != 2 * len(m["boxes"]):
                raise SystemExit(f"[fatal] 타일({k},1) 상자 사각형 {nrect} "
                                 f"!= {2 * len(m['boxes'])}")
            txt = [a.get_text() for a in ax.get_children()
                   if isinstance(a, Text) and a.get_text().strip()]
            if not m["boxes"] and not any(t.startswith("검출 0건") for t in txt):
                raise SystemExit(f"[fatal] 타일({k},1) 「검출 0건」 칩이 없다")
            if m["boxes"] and not any(t.startswith("검출 ") for t in txt):
                raise SystemExit(f"[fatal] 타일({k},1) 검출 칩이 없다")
        if j == 2 and sum(isinstance(a, Polygon) for a in ax.get_children()) < 4:
            raise SystemExit(f"[fatal] 타일({k},2) 쐐기 폴리곤이 너무 적다")
        big = [(a.get_text(), a.get_fontsize()) for a in ax.get_children()
               if isinstance(a, Text) and a.get_text().strip() and a.get_fontsize() > 12]
        if big:
            raise SystemExit(f"[fatal] 타일({k},{j}) 대형 낙관이 되살아났다: {big}")
    print(f"[gate] 자기점검 통과 — 6/6 타일 실사 + 열별 오버레이 (축 {len(fig.axes)} = 6 + 램프 1)")
    for k, m in enumerate(meta):
        print(f"   {k + 1}행 {m['row']['world']:10s} {m['row']['tier']}  "
              f"낙차영역 {m['reg']['n_px']:>8d} px · 정답칸 {len(m['gt']):2d}  |  "
              f"YOLO 상자 {len(m['boxes'])}개"
              + (f" (conf {m['boxes'][0]['conf']:.3f}, 중심적중 {m['nhit_box']})"
                 if m["boxes"] else "")
              + f"  |  rgb_s42 발화 {len(m['fired'])}칸 / 정답칸 적중 {len(m['hit'])}칸")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    dst = os.path.join(OUT, "panel_gz_yolo.png")
    if os.path.exists(dst) and not a.force:
        print(f"  이미 있음 (resume-safe): {dst}  — 다시 그리려면 --force")
        sys.exit(0)
    p, sz, dim = build()
    print(f"\n[done] {p}  {sz / 1024:.0f} KB  {dim[0]}×{dim[1]} px  "
          f"(2 MB 규율 {'통과' if sz <= 2_000_000 else '위반'})")
