#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verdict_panels.py — v3-A VERDICT 웨이브의 **의무 정성 패널 4종** (CPU 전용).

    PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES= \
      /home/vislab/miniconda3/envs/env_seg/bin/python \
      experiments/v3_0823/code/verdict_panels.py [--force]

산출 → `experiments/v3_0823/panels/verdict/`

  (a) panel_a_fourarm.png        2(v2·v3-A) × 4(A·B·C·D) 한 컷 4팔 + 확률 히트 오버레이
  (b) panel_b_dash1_exemplars.png 계기판① 대표 짝 3행 (트윈-조건부 적중 vs 무조건 발화)
  (c) panel_c_ncue_trap.png       N-cue 함정 3행 (C·D팔 · GT 전 칸 음성 ⇒ 전부 오경보)
  (d) panel_d_before_after.png    계기판 ①②③ before/after 막대·산점

**규약 (동결 사전등록 `PREREG_V3.md` 에서 옴 — 하나도 완화하지 않는다)**

  1. 모든 패널 한국어 라벨.
  2. 모든 패널에 **출처 푸터**: 읽은 원장 파일 · 런/시드 집합 · 운용점 · 분모 · 날짜.
  3. `sceneH3` 는 **완전-은닉 층**(§2.1 층화 3)이라 계기판① 풀링 층에 **절대** 넣지 않는다.
  4. recall 은 **FA 동반 인쇄 없이 찍지 않는다** (§6-5).
  5. **단일 축 인쇄 금지** — recall·FA 비교에는 프레임축과 칸축이 **둘 다** 나온다 (§6-6).
  6. C·D팔 GT 는 **사양 상수 전 칸 음성** (AC-INSTR-1 C3-2) — 그리는 자리마다 명시한다.
  7. PNG 1장 ≤ 2 MB — `save()` 규율.
  8. 재추론 0 · 재렌더 0 · GPU 0 · git 무접촉. 모든 확률은 이미 덤프된 CSV 에서 읽는다.

**`make_panels_v3.py` 재사용**: 폰트 등록 · 색 사전 `C` · `footer()` · `save()` ·
`cam_of()` · `wedge_px()` 는 `experiments/v3_0823/code/make_panels_v3.py` 의 것을
**그대로 복사**했다(투영 수식 한 줄도 바꾸지 않음). import 가 원칙이지만 그 파일은
`if __name__ == "__main__"` 가드가 없는 **순수 스크립트**라 import 하는 순간 기존
`panels/*.png` 4장을 다시 써버린다 — 본 작업의 "기존 파일 무편집" 제약과 충돌하므로
복사 + 출처 주석으로 처리한다.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
from matplotlib import font_manager, rcParams          # noqa: E402

ROOT = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V3 = os.path.join(ROOT, "experiments/v3_0823")
OUT = os.path.join(V3, "panels/verdict")
os.makedirs(OUT, exist_ok=True)

# ---- [복사: make_panels_v3.py L26-43] 폰트 · 색 · 날짜 ----------------------
_FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
for _i in (0, 1, 2, 3, 4):                      # KR face inside the TTC
    try:
        font_manager.fontManager.addfont(_FONT)
        break
    except Exception:
        pass
rcParams["font.family"] = ["Noto Sans CJK KR", "Noto Sans CJK JP", "DejaVu Sans"]
# addfont() 는 .ttc 의 **첫 face 만** 등록한다(이 파일은 JP). KR·JP·SC 는 같은 Source Han
# 글리프 집합이라 한글은 JP face 로 정상 렌더되지만, 없는 이름을 남겨두면 findfont 경고가
# 도배된다 — 실제로 등록된 이름만 남긴다(폰트 자체는 바뀌지 않는다).
_have = {f.name for f in font_manager.fontManager.ttflist}
rcParams["font.family"] = [n for n in rcParams["font.family"] if n in _have] or ["DejaVu Sans"]
rcParams["axes.unicode_minus"] = False
rcParams["savefig.facecolor"] = "white"
rcParams["figure.facecolor"] = "white"

# brand-neutral, colour-blind-safe: rgb / depth / b2
C = dict(rgb="#4C6FBF", depth="#D97C2B", b2="#7E8794",
         pub="#B9C2D0", cor="#2F4B7C", ok="#2E7D5B", bad="#B03A48",
         grid="#DDE1E6", ink="#1F2429", mute="#5C6672")

DATE = "2026-08-24"
V2COL, V3COL = "#B9C2D0", "#2F4B7C"     # before(v2) / after(v3-A)
GTCOL = "#12C2E9"                       # GT-양성 칸 윤곽 (히트 램프와 충돌 없음)


def footer(fig, text, y=0.012):
    """[복사: make_panels_v3.py L45-47] 출처 푸터."""
    fig.text(0.5, y, text, ha="center", va="bottom", fontsize=7.4,
             color=C["mute"], family=rcParams["font.family"], linespacing=1.55)


def save(fig, name, dpi=130):
    """[복사: make_panels_v3.py L49-59] 저장 + 2 MB 규율."""
    p = os.path.join(OUT, name)
    fig.savefig(p, dpi=dpi, bbox_inches="tight", pad_inches=0.22)
    import PIL.Image as I
    sz = os.path.getsize(p)
    if sz > 2_000_000:                          # size discipline: <= 2 MB / PNG
        im = I.open(p).convert("RGB")
        im.quantize(colors=256, method=I.MEDIANCUT).save(p, optimize=True)
        sz = os.path.getsize(p)
    dim = I.open(p).size
    print(f"  {name:30s} {sz/1024:8.0f} KB  {dim}")
    return p, sz, dim


import numpy as np                                     # noqa: E402
import matplotlib.pyplot as plt                        # noqa: E402
from matplotlib.patches import Polygon                  # noqa: E402
from matplotlib.lines import Line2D                     # noqa: E402
from PIL import Image                                   # noqa: E402

sys.path.insert(0, os.path.join(ROOT, "experiments/mainrun_0819/code"))
sys.path.insert(0, os.path.join(ROOT, "experiments/mainrun_0819/code/labeling"))
import gridspec                                        # noqa: E402
import labeler as L                                    # noqa: E402

GRID = gridspec.load("gridspec_v1.json")                # PROVISIONAL-GRID-V1 · 20칸
GSPEC = json.load(open(GRID.path))
CELLS = list(GRID.cell_ids)
NS, NB = GSPEC["n_sectors"], GSPEC["n_bands"]
ASC = GSPEC["sector_edges_deg"][::-1]                    # ascending azimuth edges
BND = GSPEC["band_edges_m"]
assert GRID.version == "PROVISIONAL-GRID-V1" and GRID.n_cells == 20, GRID.summary()


# ---- [복사: make_panels_v3.py L101-132] 투영 -------------------------------
def cam_of(fr):
    sdir, fn = os.path.dirname(fr["rgb"]), os.path.basename(fr["rgb"])
    cuts = json.load(open(os.path.join(sdir, "variation.json")))["cuts"]
    if isinstance(cuts, dict):
        cuts = list(cuts.values())
    return next(c["cam"] for c in cuts if c["file"] == fn)


def wedge_px(cell, cam, n=36):
    """Ground wedge of `cell` -> image polygon (px, py) at the frame's ground_z.

    Inverse of labeler.polar_cells: si = NS-1-k  =>  az in [ASC[NS-1-si], ASC[NS-si]).
    """
    i = CELLS.index(cell)
    b, si = i // NS, i % NS
    k = NS - 1 - si
    a0, a1 = math.radians(ASC[k]), math.radians(ASC[k + 1])
    r0, r1 = BND[b], BND[b + 1]
    eye = np.asarray(cam["eye"], dtype=np.float64)
    yaw = math.radians(cam["yaw"])
    cy, sy = math.cos(yaw), math.sin(yaw)
    ring = ([(r1, a) for a in np.linspace(a0, a1, n)] +
            [(r0, a) for a in np.linspace(a1, a0, n)])
    pts = []
    for r, a in ring:
        xc, yc = r * math.cos(a), r * math.sin(a)
        pts.append([eye[0] + xc * cy - yc * sy,
                    eye[1] + xc * sy + yc * cy,
                    float(cam["ground_z"])])
    px, py, zc, inb = L.project(np.asarray(pts), eye, cam)
    front = zc > 0.05
    return px, py, front, inb
# ---- [복사 끝] --------------------------------------------------------------


# ============================================================== 원장 읽기 ===
RUNS = ["rgb_s42", "rgb_s43", "rgb_s44"]
TAU = 0.5
POOL_SCENES = ("sceneH1", "sceneH2")            # 계기판① 풀링 층 (H3 절대 제외)
HIDDEN_SCENE = "sceneH3"                        # 완전-은닉 층 — 별도 행
NCUE_SCENES = ("sceneN9", "sceneN11")
ARM_ROUND = dict(A="on", B="on", C="off", D="off")
PANE = dict(A="ac", B="bd", C="ac", D="bd")

LEDGER_PF = ("experiments/v3_0823/eval_v3textext/{rgb_s42,rgb_s43,rgb_s44}/"
             "{,bd/}per_frame.csv (v2)  ·  experiments/v3_0823/eval_v3a_textext/"
             "{rgb_s42,rgb_s43,rgb_s44}/{,bd/}per_frame.csv (v3-A)")
LEDGER_MAN = ("experiments/v3_0823/dataset_manifest_v3_textext.json (A·C) + "
              "…_bd.json (B·D)")
SEEDSET = "런 rgb_s42 · rgb_s43 · rgb_s44 (3시드) — 표기 확률은 **3시드 평균**"
GRIDSTR = ("격자 experiments/mainrun_0819/code/labeling/gridspec_v1.json "
           "(PROVISIONAL-GRID-V1 · 4밴드 × 5섹터 = 20칸)")
CD_GT = "C·D팔 GT = **사양 상수 전 칸 음성** (AC-INSTR-1 C3-2)"


def read_pf(path):
    """per_frame.csv -> {(band_round, scene, file): rec}.  frame_id = band/arm/scene/file."""
    out = {}
    with open(path) as f:
        rd = csv.DictReader(f)
        cols = [c[2:] for c in (rd.fieldnames or []) if c.startswith("p_")]
        if cols != CELLS:
            raise SystemExit(f"[fatal] {path}: 칸 목록 불일치 {cols[:3]}… vs {CELLS[:3]}…")
        for r in rd:
            band, arm, sc, fn = r["frame_id"].split("/", 3)
            out[(band, sc, fn, r["toggle_state"])] = dict(
                scene=r["scene_id"], tier=r["tier"],
                p=np.array([float(r[f"p_{c}"]) for c in CELLS]),
                g=np.array([float(r[f"g_{c}"]) for c in CELLS]))
    return out


def load_arms(evdir):
    """평가 디렉터리 -> {arm: {(band,scene,file): {tier,g,P[3],pm}}}, arm ∈ A B C D."""
    out = {a: {} for a in "ABCD"}
    for run in RUNS:
        ac = read_pf(os.path.join(V3, evdir, run, "per_frame.csv"))
        bd = read_pf(os.path.join(V3, evdir, run, "bd", "per_frame.csv"))
        for src, (on_arm, off_arm) in ((ac, ("A", "C")), (bd, ("B", "D"))):
            for (band, sc, fn, tog), r in src.items():
                arm = on_arm if tog == "on" else off_arm
                d = out[arm].setdefault((band, sc, fn),
                                        dict(tier=r["tier"], g=r["g"], P=[]))
                d["P"].append(r["p"])
    for a in out:
        for v in out[a].values():
            if len(v["P"]) != len(RUNS):
                raise SystemExit(f"[fatal] {evdir}: 시드 수 {len(v['P'])} != {len(RUNS)}")
            v["pm"] = np.mean(np.stack(v["P"]), axis=0)
    return out


def load_manifests():
    man = {}
    for pane, fn in (("ac", "dataset_manifest_v3_textext.json"),
                     ("bd", "dataset_manifest_v3_textext_bd.json")):
        d = json.load(open(os.path.join(V3, fn)))
        if d["meta"]["grid_version"] != GRID.version:
            raise SystemExit(f"[fatal] {fn}: grid {d['meta']['grid_version']}")
        for fr in d["frames"]:
            band, arm, sc, f = fr["frame_id"].split("/", 3)
            man[(pane, band, sc, f, arm)] = fr
    return man


def frame_of(MAN, arm, key):
    """(A|B|C|D, (band,scene,file)) -> 매니페스트 레코드."""
    band, sc, fn = key
    return MAN[(PANE[arm], band, sc, fn, ARM_ROUND[arm])]


# ============================================================== 컷 선택 =====
def pool_keys(V2A):
    """paired-H (A팔·B팔 둘 다 strict-H) ∩ {sceneH1, sceneH2} — H3 는 원천 배제."""
    ph = [k for k in V2A["A"]
          if V2A["A"][k]["tier"] == "H" and V2A["B"][k]["tier"] == "H"]
    return sorted([k for k in ph if k[1] in POOL_SCENES]), sorted(
        [k for k in ph if k[1] == HIDDEN_SCENE])


def select_a(V2A, V3A, keys):
    """(a) 4팔 컷 = 풀링 strict-H 중 v3 트윈-조건부 적중 칸이 가장 많은 컷.

    동점은 GT-양성 칸의 최대 (p_A − p_C) 마진 → 키 사전순으로 깬다 (완전 결정적)."""
    rank = []
    for k in keys:
        g = V2A["A"][k]["g"] > 0.5
        if not g.any():
            continue
        pa, pc = V3A["A"][k]["pm"], V3A["C"][k]["pm"]
        twin = int((g & (pa >= TAU) & (pc < TAU)).sum())
        margin = float((pa[g] - pc[g]).max())
        rank.append((-twin, -margin, k))
    rank.sort()
    if not rank:
        raise SystemExit("[fatal] (a) 후보 없음")
    return rank[0][2], -rank[0][0], -rank[0][1]


def select_b(V2A, V3A, keys, n_want=3):
    """(b) 계기판① 대표 짝.

    규칙(등록): 풀링 층(H1+H2, H3 제외)의 컷 중 τ=0.5·3시드 평균 확률에서
      · v3-A 가 GT-양성 칸 c 에 대해 A팔 발화 ∧ C팔 미발화  (트윈-조건부 적중)
      · **동시에** v2 가 같은 칸 c 에 대해 A팔·C팔 **둘 다** 발화 (무조건 발화)
    인 (컷, 칸) 을 모두 찾고, 컷마다 마진 (p3_A − p3_C) 이 최대인 칸을 결정 칸으로
    삼아 마진 내림차순 → 키 사전순으로 정렬해 위에서 n_want 개를 취한다."""
    hits = {}
    for k in keys:
        g = V2A["A"][k]["g"] > 0.5
        if not g.any():
            continue
        p3a, p3c = V3A["A"][k]["pm"], V3A["C"][k]["pm"]
        p2a, p2c = V2A["A"][k]["pm"], V2A["C"][k]["pm"]
        ok = g & (p3a >= TAU) & (p3c < TAU) & (p2a >= TAU) & (p2c >= TAU)
        idx = np.where(ok)[0]
        if not len(idx):
            continue
        cells = [dict(cell=CELLS[i], p3a=float(p3a[i]), p3c=float(p3c[i]),
                      p2a=float(p2a[i]), p2c=float(p2c[i]),
                      margin=float(p3a[i] - p3c[i])) for i in idx]
        cells.sort(key=lambda d: (-d["margin"], d["cell"]))
        hits[k] = cells
    order = sorted(hits, key=lambda k: (-hits[k][0]["margin"], k))
    return [(k, hits[k]) for k in order[:n_want]], len(order), len(
        [c for k in hits for c in hits[k]]), hits


def select_c(V2A, V3A, n_want=3):
    """(c) N-cue 함정 컷.

    규칙(등록): sceneN9·sceneN11 (GT 전 칸 음성) 컷을 τ=0.5·3시드 평균에서
    **v2 의 C팔 발화 칸 수** 내림차순 → C팔 최대확률 내림차순 → 키 사전순으로 세우고,
    (씬, 밴드라운드) 조합이 겹치지 않게 위에서 탐욕적으로 n_want 개를 뽑는다."""
    rows = []
    for k in sorted(V2A["C"]):
        if k[1] not in NCUE_SCENES:
            continue
        p2c, p2d = V2A["C"][k]["pm"], V2A["D"][k]["pm"]
        p3c, p3d = V3A["C"][k]["pm"], V3A["D"][k]["pm"]
        rows.append(dict(key=k, n2c=int((p2c >= TAU).sum()), n2d=int((p2d >= TAU).sum()),
                         n3c=int((p3c >= TAU).sum()), n3d=int((p3d >= TAU).sum()),
                         max2c=float(p2c.max()), max3c=float(p3c.max()),
                         top2c=CELLS[int(np.argmax(p2c))]))
    rows.sort(key=lambda d: (-d["n2c"], -d["max2c"], d["key"]))
    picked, seen = [], set()
    for r in rows:
        tag = (r["key"][1], r["key"][0])
        if tag in seen:
            continue
        seen.add(tag)
        picked.append(r)
        if len(picked) == n_want:
            break
    return picked, rows


# ============================================================== 오버레이 ====
CMAP = plt.get_cmap("inferno")
IMW, IMH = 640, 360                     # 타일 픽셀 (원본 1920×1080 의 1/3)


def draw_tile(ax, fr, probs, gt, *, tau=TAU, mark=None, mark_lbl=None,
              title=None, title_col=None, sub=None, badge=None, badge_col=None):
    """한 컷 + 20칸 확률 히트 오버레이.  probs/gt 는 CELLS 순서 길이-20 배열."""
    cam = cam_of(fr)
    img = Image.open(fr["rgb"]).convert("RGB").resize((IMW, IMH), Image.LANCZOS)
    sx, sy = IMW / L.W_IMG, IMH / L.H_IMG
    ax.imshow(np.asarray(img))
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlim(0, IMW); ax.set_ylim(IMH, 0)

    hidden_hot = []
    for i in np.argsort(probs):                 # 낮은 확률부터 → 높은 칸이 위로
        cell = CELLS[i]
        px, py, front, inb = wedge_px(cell, cam)
        if not front.all():
            if probs[i] >= tau or gt[i] > 0.5:
                hidden_hot.append(cell)
            continue
        X, Y = px * sx, py * sy
        if X.max() < 0 or X.min() > IMW or Y.max() < 0 or Y.min() > IMH:
            continue
        xy = np.c_[X, Y]
        p = float(probs[i])
        ax.add_patch(Polygon(xy, closed=True, fc=CMAP(p), ec="none",
                             alpha=0.12 + 0.52 * p, zorder=2))
        if p >= tau:
            ax.add_patch(Polygon(xy, closed=True, fc="none", ec="white",
                                 lw=1.5, zorder=3))
        else:
            ax.add_patch(Polygon(xy, closed=True, fc="none", ec="white",
                                 lw=0.5, alpha=.30, zorder=3))
        if gt[i] > 0.5:                          # GT-양성 칸 = 별도 윤곽
            ax.add_patch(Polygon(xy, closed=True, fc="none", ec="black",
                                 lw=3.4, zorder=4))
            ax.add_patch(Polygon(xy, closed=True, fc="none", ec=GTCOL,
                                 lw=1.9, zorder=5))
        if mark is not None and cell == mark:    # 결정 칸
            ax.add_patch(Polygon(xy, closed=True, fc="none", ec="black",
                                 lw=4.6, zorder=6))
            ax.add_patch(Polygon(xy, closed=True, fc="none", ec="white",
                                 lw=2.2, ls=(0, (5, 3)), zorder=7))
            cx, cy = float(xy[:, 0].mean()), float(xy[:, 1].mean())
            ax.text(np.clip(cx, 46, IMW - 46), np.clip(cy, 16, IMH - 12),
                    mark_lbl or cell, ha="center", va="center", fontsize=8.6,
                    color="white", fontweight="bold", zorder=8,
                    bbox=dict(fc="#000000", ec="white", lw=.9, alpha=.80, pad=1.9))

    if title:
        ax.set_title(title, fontsize=10.6, color=title_col or C["ink"], pad=5,
                     fontweight="bold")
    if sub:
        ax.text(.012, .020, sub, transform=ax.transAxes, ha="left", va="bottom",
                fontsize=7.8, color="white", zorder=9,
                bbox=dict(fc="#000000", ec="none", pad=2.2, alpha=.60))
    if badge:
        ax.text(.012, .975, badge, transform=ax.transAxes, ha="left", va="top",
                fontsize=8.2, color="white", fontweight="bold", zorder=9,
                bbox=dict(fc=badge_col or C["cor"], ec="none", pad=2.4, alpha=.94))
    if hidden_hot:
        ax.text(.988, .975, "칸이 카메라 뒤 · 미표시: " + ",".join(hidden_hot),
                transform=ax.transAxes, ha="right", va="top", fontsize=7.0,
                color="white", zorder=9,
                bbox=dict(fc="#000000", ec="none", pad=2.0, alpha=.55))
    for s in ax.spines.values():
        s.set_color(C["grid"]); s.set_linewidth(1.0)


def add_ramp(fig, rect, label):
    """확률 램프 컬러바 (τ=0.5 눈금 표시)."""
    cax = fig.add_axes(rect)
    grad = np.linspace(0, 1, 256).reshape(1, -1)
    cax.imshow(grad, aspect="auto", cmap=CMAP, extent=(0, 1, 0, 1))
    cax.set_yticks([])
    cax.set_xticks([0, .25, .5, .75, 1])
    cax.set_xticklabels(["0", ".25", ".50", ".75", "1"], fontsize=7.6)
    cax.axvline(.5, color="white", lw=1.6)
    cax.tick_params(length=2, pad=1.5)
    cax.set_title(label, fontsize=8.0, color=C["mute"], pad=3)
    for s in cax.spines.values():
        s.set_color(C["grid"])
    return cax


def legend_handles(with_gt=True, with_mark=True):
    h = [Line2D([], [], color="white", lw=1.5, marker="s", ms=9,
                markerfacecolor=CMAP(.8), markeredgecolor="white",
                label=f"발화 칸 (p ≥ {TAU:g}) — 흰 테두리")]
    if with_gt:
        h.append(Line2D([], [], color=GTCOL, lw=2.4, label="GT-양성 칸 (하늘색 이중 윤곽)"))
    if with_mark:
        h.append(Line2D([], [], color="white", lw=2.2, ls=(0, (5, 3)),
                        label="결정 칸 (흰 점선)"))
    return h


# ============================================================ 숫자 원장 =====
def ledger_tables():
    d2 = json.load(open(os.path.join(V3, "v2_textext_tables.json")))
    d3 = json.load(open(os.path.join(V3, "v3a_textext_tables.json")))
    dd = json.load(open(os.path.join(V3, "verdict_dash2.json")))
    dc = json.load(open(os.path.join(V3, "verdict_core.json")))
    o2 = {o["name"]: o for o in d2["summary"]["rgb"]["ops"]}
    o3 = {o["name"]: o for o in d3["raw"]["summary"]["v3a_rgb"]["ops"]}
    if d2["summary"]["rgb"]["runs"] != RUNS or d3["raw"]["summary"]["v3a_rgb"]["runs"] != RUNS:
        raise SystemExit("[fatal] 원장 런 집합이 rgb_s42/43/44 가 아니다")
    return d2, d3, dd, dc, o2, o3


def m(op, key):
    return float(op[key]["mean"])


def s(op, key):
    v = op[key].get("sd")
    return 0.0 if v is None or not np.isfinite(v) else float(v)


def diff_stat(op, ka, kb):
    """FA_C − FA_D 를 **시드별로** 뺀 뒤 mean/sd(ddof=1)."""
    a, b = op[ka], op[kb]
    if a.get("n") == len(RUNS) and b.get("n") == len(RUNS):
        d = np.array(a["vals"], float) - np.array(b["vals"], float)
        return float(d.mean()), float(d.std(ddof=1))
    return m(op, ka) - m(op, kb), float("nan")


OP8 = ["F@0.359", "F@0.200", "F@0.100", "F@0.050",
       "C@0.046732", "C@0.026035", "C@0.013017", "C@0.006509"]
OP9 = ["tau_op"] + OP8
OPLBL = {"tau_op": "τ_op\n0.5", "F@0.359": "F@.359", "F@0.200": "F@.200",
         "F@0.100": "F@.100", "F@0.050": "F@.050", "C@0.046732": "C@.04673",
         "C@0.026035": "C@.02604", "C@0.013017": "C@.01302",
         "C@0.006509": "C@.00651"}


def grouped(ax, names, v2v, v2s, v3v, v3s, ylab, title, sub=None,
            fa2=None, fa3=None, falab="FA_D", title_pad=21, sub_y=1.008):
    x = np.arange(len(names)); w = .36
    ax.bar(x - w / 2, v2v, w, color=V2COL, edgecolor="white", lw=1.1,
           label="v2 (레시피 동결 체크포인트)", zorder=3)
    ax.bar(x + w / 2, v3v, w, color=V3COL, edgecolor="white", lw=1.1,
           label="v3-A", zorder=3)
    ax.errorbar(x - w / 2, v2v, yerr=v2s, fmt="none", ecolor=C["mute"],
                elinewidth=1.1, capsize=3, zorder=4)
    ax.errorbar(x + w / 2, v3v, yerr=v3s, fmt="none", ecolor=C["ink"],
                elinewidth=1.1, capsize=3, zorder=4)
    top = max(max(np.array(v2v) + np.array(v2s)), max(np.array(v3v) + np.array(v3s)), 1e-6)
    for i in range(len(names)):
        ax.text(i - w / 2, v2v[i] + .015 * top, f"{v2v[i]:.3f}".lstrip("0"),
                ha="center", va="bottom", fontsize=7.3, color=C["mute"], zorder=5)
        ax.text(i + w / 2, v3v[i] + .015 * top, f"{v3v[i]:.3f}".lstrip("0"),
                ha="center", va="bottom", fontsize=7.3, color=V3COL,
                fontweight="bold", zorder=5)
    lbl = []
    for i, n in enumerate(names):
        t = OPLBL[n]
        if fa2 is not None:
            t += f"\n{falab} {fa2[i]:.3f}|{fa3[i]:.3f}".replace("0.", ".")
        lbl.append(t)
    ax.set_xticks(x); ax.set_xticklabels(lbl, fontsize=7.6)
    ax.set_ylim(0, top * 1.30)
    ax.set_ylabel(ylab, fontsize=9.6)
    ax.set_title(title, fontsize=11.6, fontweight="bold", color=C["ink"], pad=title_pad)
    if sub:
        ax.text(.5, sub_y, sub, transform=ax.transAxes, ha="center", va="bottom",
                fontsize=8.4, color=C["mute"])
    ax.grid(axis="y", color=C["grid"], lw=.8, zorder=0); ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


# ================================================================= 패널 ====
def panel_a(V2A, V3A, MAN, key, n_twin, margin):
    band, sc, fn = key
    H = 9.9
    def Y(t):                                       # 위에서 t인치 내려온 figure 좌표
        return 1 - t / H
    fig = plt.figure(figsize=(18.6, H))
    gs = fig.add_gridspec(2, 4, left=.058, right=.995, top=Y(3.05), bottom=.055,
                          hspace=.150, wspace=.020)
    colspec = [("A", "A 팔 (위험 ON · 단서 유지)", C["bad"]),
               ("B", "B 팔 (위험 ON · 단서 제거)", "#8C5A2B"),
               ("C", "C 팔 (위험 OFF · 단서 유지)", C["cor"]),
               ("D", "D 팔 (위험 OFF · 단서 제거)", C["ok"])]
    rows = [("v2", V2A, "v2 (레시피 동결 체크포인트)"), ("v3", V3A, "v3-A")]
    for r, (tag, DAT, rowlbl) in enumerate(rows):
        for c, (arm, collbl, ccol) in enumerate(colspec):
            rec = DAT[arm][key]
            fr = frame_of(MAN, arm, key)
            gt = rec["g"]
            nf = int((rec["pm"] >= TAU).sum())
            hit = int(((rec["pm"] >= TAU) & (gt > 0.5)).sum())
            ax = fig.add_subplot(gs[r, c])
            gtn = int((gt > 0.5).sum())
            sub = (f"발화 {nf}칸 · GT-양성 {gtn}칸 · 적중 {hit}칸"
                   if gtn else f"발화 {nf}칸 · GT 전 칸 음성(사양 상수) ⇒ 모두 오경보")
            draw_tile(ax, fr, rec["pm"], gt,
                      title=(collbl if r == 0 else None), title_col=ccol,
                      sub=sub,
                      badge=f"{'v2' if tag == 'v2' else 'v3-A'} · p_max {rec['pm'].max():.3f}",
                      badge_col=(V2COL if tag == "v2" else V3COL))
            if r == 0:
                ax.title.set_color(ccol)
            for spn in ax.spines.values():
                spn.set_color(ccol); spn.set_linewidth(2.0)
        pos = gs[r, 0].get_position(fig)             # 축을 새로 만들지 않는다
        fig.text(.024, (pos.y0 + pos.y1) / 2, rowlbl, rotation=90, ha="center",
                 va="center", fontsize=12.4, fontweight="bold",
                 color=(C["mute"] if tag == "v2" else V3COL))

    fig.suptitle(f"한 포즈 · 네 팔 — {sc} / {band} 밴드 / {fn}", fontsize=19.5,
                 fontweight="bold", color=C["ink"], y=Y(0.42))
    fig.text(.058, Y(1.02),
             "같은 씬·같은 카메라 포즈를 위험(ON/OFF) × 단서(유지/제거) 로 2×2 재렌더한 "
             "바이트-쌍 컷이다.", fontsize=10.6, color=C["mute"], ha="left", va="top")
    fig.text(.058, Y(1.34),
             "위 줄 = v2, 아래 줄 = v3-A · 색칠된 쐐기 = 그 모델이 그 칸에 준 확률(3시드 평균).",
             fontsize=10.6, color=C["mute"], ha="left", va="top")
    fig.text(.058, Y(1.72),
             f"이 컷의 v3-A 트윈-조건부 적중 칸 {n_twin}칸 · "
             f"GT-양성 칸 최대 마진 (p_A − p_C) = {margin:.3f}.",
             fontsize=10.2, color=C["ink"], ha="left", va="top")
    fig.text(.058, Y(2.02),
             "A팔·B팔 GT 는 동일(VG-01) · " + CD_GT + " — C·D팔에서 색이 보이면 그건 전부 오경보다.",
             fontsize=10.2, color=C["ink"], ha="left", va="top", fontweight="bold")
    fig.text(.058, Y(2.40),
             "쐐기는 variation.json 의 cam(eye·yaw·pitch·roll·hfov·ground_z) 과 gridspec_v1 의 "
             "sector_edges_deg / band_edges_m 에서\nlabeler.project 로 되투영 — "
             "새 렌더·새 추론 없음.",
             fontsize=9.2, color=C["mute"], ha="left", va="top", linespacing=1.55)
    add_ramp(fig, [.845, Y(1.22), .140, .0130], "칸 확률 p (3시드 평균) · 흰 선 = τ_op 0.5")
    fig.legend(handles=legend_handles(with_mark=False), loc="upper right",
               bbox_to_anchor=(.995, Y(1.72)), fontsize=9.0, frameon=False, ncol=1)
    footer(fig,
           "원장  " + LEDGER_PF + "\n"
           "이미지·cam  " + LEDGER_MAN + " → frames[].rgb / dataset/<group>/<round>/test/<scene>/variation.json  ·  " + GRIDSTR + "\n"
           + SEEDSET + "  ·  운용점 τ_op = 0.5 (PREREG §2.1 참고 병기 전용)  ·  "
           f"분모 = 이 컷 1장 × 20칸 (팔마다)  ·  {CD_GT}  ·  " + DATE, y=.010)
    return save(fig, "panel_a_fourarm.png", dpi=112), fig


def panel_b(V2A, V3A, MAN, picks, n_cuts, n_pairs):
    n = len(picks)
    H = 3.55 * n + 4.55
    def Y(t):
        return 1 - t / H
    fig = plt.figure(figsize=(18.6, H))
    gs = fig.add_gridspec(n, 4, left=.098, right=.995, top=Y(3.95), bottom=.052,
                          hspace=.230, wspace=.020)
    colspec = [("v2", "A", "v2 · A 팔 (위험 ON · 단서 유지)", C["mute"]),
               ("v2", "C", "v2 · C 팔 (위험 OFF · 단서 유지)", C["mute"]),
               ("v3", "A", "v3-A · A 팔 (위험 ON · 단서 유지)", V3COL),
               ("v3", "C", "v3-A · C 팔 (위험 OFF · 단서 유지)", V3COL)]
    DATA = dict(v2=V2A, v3=V3A)
    for r, (key, cells) in enumerate(picks):
        band, sc, fn = key
        dec = cells[0]
        for c, (tag, arm, collbl, ccol) in enumerate(colspec):
            rec = DATA[tag][arm][key]
            fr = frame_of(MAN, arm, key)
            gt = DATA[tag]["A"][key]["g"] if arm == "A" else rec["g"]
            p = float(rec["pm"][CELLS.index(dec["cell"])])
            fire = "발화" if p >= TAU else "미발화"
            ax = fig.add_subplot(gs[r, c])
            gtn = int((gt > 0.5).sum())
            sub = (f"GT-양성 {gtn}칸 · 발화 {int((rec['pm'] >= TAU).sum())}칸"
                   if arm == "A" else
                   f"GT 전 칸 음성(사양 상수) · 발화 {int((rec['pm'] >= TAU).sum())}칸")
            draw_tile(ax, fr, rec["pm"], gt, mark=dec["cell"],
                      mark_lbl=f"{dec['cell']}  p={p:.3f}  {fire}",
                      title=(collbl if r == 0 else None), title_col=ccol, sub=sub,
                      badge=("✔ 트윈-조건부 적중" if (tag == "v3" and arm == "A") else
                             ("✔ 낙차 지우니 꺼짐" if (tag == "v3" and arm == "C") else
                              "✘ 무조건 발화")),
                      badge_col=(C["ok"] if tag == "v3" else C["bad"]))
            for spn in ax.spines.values():
                spn.set_color(ccol); spn.set_linewidth(1.8)
            if c == 0:
                ax.text(-.078, .5, f"{sc} / {band} 밴드\n{fn}\n결정 칸 {dec['cell']}",
                        transform=ax.transAxes, rotation=90, ha="center", va="center",
                        fontsize=8.6, color=C["ink"], fontweight="bold",
                        linespacing=1.75)

    enough = n >= 3
    fig.suptitle("계기판 ① 대표 짝 — v3-A 는 낙차가 있을 때만 켠다, v2 는 낙차와 무관하게 켠다",
                 fontsize=19.0, fontweight="bold", color=C["ink"], y=Y(0.48))
    fig.text(.058, Y(1.12),
             "선택 규칙(등록): 풀링 층(sceneH1 + sceneH2, **sceneH3 완전-은닉 층은 원천 제외**)의 "
             "paired-H 컷에서 τ=0.5·3시드 평균 확률으로 —",
             fontsize=10.4, color=C["mute"], ha="left", va="top")
    fig.text(.058, Y(1.44),
             "① v3-A 가 GT-양성 칸에서 A팔 발화 ∧ C팔 미발화 (트윈-조건부 적중)   ∧   "
             "② 같은 칸에서 v2 는 A팔·C팔 **둘 다** 발화 (무조건 발화).",
             fontsize=10.4, color=C["mute"], ha="left", va="top")
    fig.text(.058, Y(1.88),
             f"규칙을 만족하는 컷 **{n_cuts}개** · (컷,칸) 짝 **{n_pairs}개**"
             + (f"  →  마진 (p3_A − p3_C) 상위 {n}컷을 인쇄한다."
                if enough else
                f"  →  **3개 미만이므로 존재하는 {n}개만 인쇄한다** (규칙을 완화하지 않았다)."),
             fontsize=11.0, color=(C["ink"] if enough else C["bad"]),
             ha="left", va="top", fontweight="bold")
    fig.text(.058, Y(2.28),
             "선택된 컷 / 결정 칸\n" + "\n".join(
                 f"   {k[1]} / {k[0]} / {k[2]}  →  {cs[0]['cell']}   "
                 f"v3-A  A {cs[0]['p3a']:.3f} / C {cs[0]['p3c']:.3f}   ·   "
                 f"v2  A {cs[0]['p2a']:.3f} / C {cs[0]['p2c']:.3f}"
                 for k, cs in picks),
             fontsize=8.6, color=C["ink"], ha="left", va="top", linespacing=1.65)
    fig.text(.058, Y(3.30),
             "C팔은 낙차만 지운 반사실 팔이다 — 단서(레일·경고선·재질)는 그대로 있다. " + CD_GT
             + " 이므로\nC팔에서 켜지는 칸은 정의상 전부 오경보이며, 그 칸이 A팔에서도 켜졌다면 "
             "그 발화는 낙차가 아니라 **단서를 본 것**이다.",
             fontsize=9.6, color=C["mute"], ha="left", va="top", linespacing=1.55)
    add_ramp(fig, [.845, Y(1.22), .140, 0.13 / H],
             "칸 확률 p (3시드 평균) · 흰 선 = τ_op 0.5")
    fig.legend(handles=legend_handles(), loc="upper right",
               bbox_to_anchor=(.995, Y(1.72)), fontsize=8.8, frameon=False)
    footer(fig,
           "원장  " + LEDGER_PF + "\n"
           "이미지·cam  " + LEDGER_MAN + "  ·  " + GRIDSTR + "\n"
           + SEEDSET + "  ·  운용점 τ = 0.5  ·  "
           "선택 모집단 = paired-H(A팔·B팔 둘 다 strict-H) ∩ {sceneH1, sceneH2} = **51프레임 / 393칸** "
           "(sceneH3 21프레임은 완전-은닉 층 — PREREG §2.1 층화 3 에 따라 제외)  ·  "
           + CD_GT + "  ·  " + DATE, y=.010)
    return save(fig, "panel_b_dash1_exemplars.png", dpi=112), fig


def panel_c(V2A, V3A, MAN, picks):
    n = len(picks)
    H = 3.55 * n + 4.45
    def Y(t):
        return 1 - t / H
    fig = plt.figure(figsize=(18.6, H))
    gs = fig.add_gridspec(n, 4, left=.092, right=.995, top=Y(3.85), bottom=.052,
                          hspace=.230, wspace=.020)
    colspec = [("v2", "C", "v2 · C 팔 (단서 있음 · 위험 없음)", C["mute"]),
               ("v2", "D", "v2 · D 팔 (단서 없음 · 위험 없음)", C["mute"]),
               ("v3", "C", "v3-A · C 팔 (단서 있음 · 위험 없음)", V3COL),
               ("v3", "D", "v3-A · D 팔 (단서 없음 · 위험 없음)", V3COL)]
    DATA = dict(v2=V2A, v3=V3A)
    for r, pk in enumerate(picks):
        key = pk["key"]; band, sc, fn = key
        for c, (tag, arm, collbl, ccol) in enumerate(colspec):
            rec = DATA[tag][arm][key]
            fr = frame_of(MAN, arm, key)
            assert (rec["g"] > 0.5).sum() == 0, "N-cue GT 는 전 칸 음성이어야 한다"
            nf = int((rec["pm"] >= TAU).sum())
            ax = fig.add_subplot(gs[r, c])
            draw_tile(ax, fr, rec["pm"], rec["g"],
                      mark=(pk["top2c"] if arm == "C" else None),
                      mark_lbl=f"{pk['top2c']}  p={rec['pm'][CELLS.index(pk['top2c'])]:.3f}",
                      title=(collbl if r == 0 else None), title_col=ccol,
                      sub=f"GT 전 칸 음성 ⇒ 발화 {nf}칸 = 오경보 {nf}건 "
                          f"(p_max {rec['pm'].max():.3f})",
                      badge=("오경보 " + str(nf) + "칸" if nf else "오경보 0칸"),
                      badge_col=(C["bad"] if nf else C["ok"]))
            for spn in ax.spines.values():
                spn.set_color(ccol); spn.set_linewidth(1.8)
            if c == 0:
                ax.text(-.062, .5, f"{sc} / {band} 밴드\n{fn}",
                        transform=ax.transAxes, rotation=90, ha="center", va="center",
                        fontsize=8.6, color=C["ink"], fontweight="bold",
                        linespacing=1.75)

    fig.suptitle("계기판 ③ N-cue 함정 — 위험이 아예 없는 씬에서 단서만 켜 두었다",
                 fontsize=19.0, fontweight="bold", color=C["ink"], y=Y(0.48))
    fig.text(.058, Y(1.10),
             "sceneN9 · sceneN11 은 **낙차가 설계상 존재하지 않는 씬**이다. "
             "네 팔 어디에도 GT-양성 칸이 없고(전 팔 0칸 실측),",
             fontsize=10.4, color=C["bad"], ha="left", va="top", fontweight="bold")
    fig.text(.058, Y(1.42),
             "C팔에는 단서(레일·경고선·재질)만 남겨 두었다. 따라서 "
             "**이 패널에서 색이 칠해진 모든 쐐기는 오경보다** — 하나도 예외가 없다.",
             fontsize=10.4, color=C["bad"], ha="left", va="top", fontweight="bold")
    fig.text(.058, Y(1.84),
             "C팔 − D팔 = **단서-유발 오경보 몫**, D팔 = 순수 씬-연합(단서 없는 배경만으로 나는 발화)의 "
             "직접 게이지다 (PREREG §2.3).",
             fontsize=9.8, color=C["mute"], ha="left", va="top")
    fig.text(.058, Y(2.12), CD_GT + " — 이 두 씬은 A·B팔도 GT 전 칸 음성이다.",
             fontsize=9.8, color=C["mute"], ha="left", va="top")
    fig.text(.058, Y(2.52),
             "선택 규칙(등록): τ=0.5·3시드 평균에서 **v2 의 C팔 발화 칸 수** 내림차순 → "
             "C팔 최대확률 내림차순 → 키 사전순, (씬, 밴드라운드) 조합 비중복 탐욕 3컷.\n선택   "
             + "   ·   ".join(f"{p['key'][1]} / {p['key'][0]} / {p['key'][2]} "
                              f"(v2 C {p['n2c']}칸 · v3-A C {p['n3c']}칸)" for p in picks),
             fontsize=8.6, color=C["ink"], ha="left", va="top", linespacing=1.65)
    add_ramp(fig, [.845, Y(1.20), .140, 0.13 / H],
             "칸 확률 p (3시드 평균) · 흰 선 = τ_op 0.5")
    fig.legend(handles=[legend_handles()[0],
                        Line2D([], [], color="white", lw=2.2, ls=(0, (5, 3)),
                               label="v2 최대확률 칸 (흰 점선)"),
                        Line2D([], [], color=GTCOL, lw=2.4, ls=":",
                               label="GT-양성 칸 없음 (전 팔 0칸)")],
               loc="upper right", bbox_to_anchor=(.995, Y(1.70)),
               fontsize=8.8, frameon=False)
    footer(fig,
           "원장  " + LEDGER_PF + "\n"
           "이미지·cam  " + LEDGER_MAN + "  ·  " + GRIDSTR + "\n"
           + SEEDSET + "  ·  운용점 τ_op = 0.5  ·  "
           "이 패널의 모집단 = sceneN9 + sceneN11, 팔마다 **96프레임 / 1,920칸** "
           "(계기판③의 **씬군 분해** — 등록 헤드라인 분모는 C·D팔 전량 288프레임 / 5,760칸, PREREG §2.3)  ·  "
           + CD_GT + " — 이 두 씬은 A·B팔도 GT 전 칸 음성  ·  " + DATE, y=.010)
    return save(fig, "panel_c_ncue_trap.png", dpi=112), fig


ANN_OFF = {   # ② 산점 라벨의 점별 고정 오프셋 (겹침 방지 · 결정적)
    "vs_cue_count": {("sceneH1", "base"): (11, -19, "left"),
                     ("sceneH1", "h"): (11, 8, "left"),
                     ("sceneH2", "h"): (-13, 7, "right"),
                     ("sceneH3", "h"): (11, 11, "left"),
                     ("sceneH3", "base"): (-13, 9, "right")},
    "vs_optical_mean": {("sceneH1", "base"): (11, -21, "left"),
                        ("sceneH1", "h"): (11, 10, "left"),
                        ("sceneH2", "h"): (-13, 7, "right"),
                        ("sceneH3", "h"): (7, -23, "left"),
                        ("sceneH3", "base"): (13, 8, "left")},
}


def panel_d(o2, o3, dd, dc):
    HD = 24.6                                       # figure 높이(inch)
    def Yd(t):                                      # 위에서 t인치 내려온 figure 좌표
        return 1 - t / HD
    fig = plt.figure(figsize=(17.4, HD))
    gs = fig.add_gridspec(4, 2, left=.062, right=.982, top=.890, bottom=.058,
                          hspace=.760, wspace=.185,
                          height_ratios=[1.0, 1.0, 1.0, 1.0])

    # ---------------------------------------------------------------- ① ----
    fa2f = [m(o2[n], "FA_D_frame") for n in OP8]
    fa3f = [m(o3[n], "FA_D_frame") for n in OP8]
    fa2c = [m(o2[n], "FA_D_cell") for n in OP8]
    fa3c = [m(o3[n], "FA_D_cell") for n in OP8]
    ax = fig.add_subplot(gs[0, 0])
    grouped(ax, OP8,
            [m(o2[n], "pooled_frame_recall_twin") for n in OP8],
            [s(o2[n], "pooled_frame_recall_twin") for n in OP8],
            [m(o3[n], "pooled_frame_recall_twin") for n in OP8],
            [s(o3[n], "pooled_frame_recall_twin") for n in OP8],
            "트윈-조건부 recall (프레임축)",
            "① 프레임 축 — 분모 51프레임",
            "FA-정합 8지점 · 기준 팔 = D팔 · 오차막대 = σ(ddof=1, 3시드)",
            fa2f, fa3f)
    ax = fig.add_subplot(gs[0, 1])
    grouped(ax, OP8,
            [m(o2[n], "pooled_cell_recall_twin") for n in OP8],
            [s(o2[n], "pooled_cell_recall_twin") for n in OP8],
            [m(o3[n], "pooled_cell_recall_twin") for n in OP8],
            [s(o3[n], "pooled_cell_recall_twin") for n in OP8],
            "트윈-조건부 recall (칸축)",
            "① 칸 축 — 분모 393칸",
            "같은 8지점 · 같은 컷 집합 — 축만 바뀐다 (§6-6 단일 축 인쇄 금지)",
            fa2c, fa3c)
    ax.legend(loc="upper right", fontsize=8.6, frameon=False)

    # ---------------------------------------------------------------- ② ----
    units = dd["per_run"][RUNS[0]]["ops"][0]["units"]
    ukeys = [(u["scene"], u["band"]) for u in units]
    live = [i for i, u in enumerate(units) if not u["void"]]
    void = [i for i, u in enumerate(units) if u["void"]]
    ff = np.zeros((len(RUNS), len(units)))
    cc = np.zeros((len(RUNS), len(units)))
    for j, r in enumerate(RUNS):
        us = dd["per_run"][r]["ops"][0]["units"]
        if [(u["scene"], u["band"]) for u in us] != ukeys:
            raise SystemExit("[fatal] verdict_dash2 단위 순서 불일치")
        ff[j] = [u["fa_frame_B"] for u in us]
        cc[j] = [u["fa_cell_B"] for u in us]
    ffm, ccm = ff.mean(0), cc.mean(0)
    ffs, ccs = ff.std(0, ddof=1), cc.std(0, ddof=1)
    reg = {k: {kk: dict(
        slope=float(np.mean([dd["per_run"][r]["ops"][0]["reg"][k][kk]["slope"] for r in RUNS])),
        icpt=float(np.mean([dd["per_run"][r]["ops"][0]["reg"][k][kk]["intercept"] for r in RUNS])),
        r2m=float(np.mean([dd["per_run"][r]["ops"][0]["reg"][k][kk]["r2"] for r in RUNS])),
        r2s=float(np.std([dd["per_run"][r]["ops"][0]["reg"][k][kk]["r2"] for r in RUNS], ddof=1)))
        for kk in ("vs_cue_count", "vs_optical_mean")}
        for k in ("fa_frame_B", "fa_cell_B")}

    for c, (xk, regk, xlab, ttl) in enumerate([
            ("cue_count_removed", "vs_cue_count",
             "A→B 에서 제거된 정본 단서 키 수 (개)", "② 단서 개수 축"),
            ("optical_mean_abs", "vs_optical_mean",
             "(A,B) 광학 변화량  mean|ΔI|  (0–255)", "② 광학 질량 축")]):
        ax = fig.add_subplot(gs[1, c])
        ax2 = ax.twinx()
        x = np.array([dd["unit_static"][f"{a}|{b}"][xk] for a, b in ukeys])
        for i in live:
            dx, dy, ha = ANN_OFF[regk][ukeys[i]]
            ax.errorbar(x[i], ffm[i], yerr=ffs[i], fmt="o", ms=9, color=V3COL,
                        ecolor=V3COL, elinewidth=1.2, capsize=3, zorder=5)
            ax2.errorbar(x[i], ccm[i], yerr=ccs[i], fmt="^", ms=8.5, color=C["depth"],
                         ecolor=C["depth"], elinewidth=1.2, capsize=3, zorder=5)
            ax.annotate(f"{ukeys[i][0].replace('scene', '')}|{ukeys[i][1]}"
                        f" (n={units[i]['n_paired']})",
                        (x[i], ffm[i]), textcoords="offset points", xytext=(dx, dy),
                        fontsize=8.0, color=C["ink"], ha=ha, zorder=6,
                        bbox=dict(fc="white", ec="none", alpha=.80, pad=1.2))
        for i in void:
            dx, dy, ha = ANN_OFF[regk][ukeys[i]]
            ax.plot(x[i], ffm[i], marker="x", ms=10, mew=2.2, color=C["mute"], zorder=5)
            ax.annotate(f"{ukeys[i][0].replace('scene', '')}|{ukeys[i][1]} VOID "
                        f"({units[i]['void_reason']}) — 회귀 제외",
                        (x[i], ffm[i]), textcoords="offset points", xytext=(dx, dy),
                        fontsize=7.8, color=C["mute"], ha=ha, zorder=6,
                        bbox=dict(fc="white", ec="none", alpha=.80, pad=1.2))
        xs = np.linspace(x[live].min(), x[live].max(), 32)
        rf, rc = reg["fa_frame_B"][regk], reg["fa_cell_B"][regk]
        ax.plot(xs, rf["slope"] * xs + rf["icpt"], color=V3COL, lw=2.0, zorder=4,
                label=f"프레임축 적합  기울기 {rf['slope']:+.4f} · r² {rf['r2m']:.3f}±{rf['r2s']:.3f}")
        ax2.plot(xs, rc["slope"] * xs + rc["icpt"], color=C["depth"], lw=2.0, ls="--",
                 zorder=4,
                 label=f"칸축 적합  기울기 {rc['slope']:+.4f} · r² {rc['r2m']:.3f}±{rc['r2s']:.3f}")
        ax.set_xlabel(xlab, fontsize=9.6)
        ax.set_ylabel("FA_B  (프레임축 · ●, 왼쪽 눈금)", fontsize=9.4, color=V3COL)
        ax2.set_ylabel("FA_B  (칸축 · ▲, 오른쪽 눈금)", fontsize=9.4, color=C["depth"])
        ax.tick_params(axis="y", colors=V3COL)
        ax2.tick_params(axis="y", colors=C["depth"])
        ax.set_title(ttl, fontsize=11.6, fontweight="bold", color=C["ink"], pad=9)
        ax.grid(color=C["grid"], lw=.8, zorder=0); ax.set_axisbelow(True)
        for sp in ("top",):
            ax.spines[sp].set_visible(False); ax2.spines[sp].set_visible(False)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        ax.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=8.0, frameon=False)
    # ② 경고는 그 행이 소유한 **한 줄**로, 두 x축 라벨 **아래**에 (열마다 겹쳐 찍지 않는다)
    p0, p1 = gs[1, 0].get_position(fig), gs[1, 1].get_position(fig)
    fig.text((p0.x0 + p1.x1) / 2, p0.y0 - 1.02 / HD,
             "⚠ 계기판 ② 에는 **v2 팔이 없다** (PREREG §2.2 주의) — B팔이 v3 훈련팔이라 v2 체크포인트의 "
             "before 가 성립하지 않는다. 따라서 ② 는 **v3-A 단독 절대값 + 층별 기울기**이며 "
             "before/after 비교가 아니다.",
             ha="center", va="top", fontsize=9.6, color=C["bad"], fontweight="bold")

    # ---------------------------------------------------------------- ③ ----
    # 등록 분모(PREREG §2.3) = **C팔 전량 288프레임 / 5,760칸**, D팔 동일.
    # N9+N11 은 그 아래의 **씬군 분해**이지 헤드라인 분모가 아니다 → 겹쳐 찍는 표식으로.
    for c, (ax_key, unit, ttl, sub) in enumerate([
            ("frame", "288프레임", "③ 프레임 축 — 등록 분모 C팔/D팔 각 288프레임",
             "FA_C = 단서 있음·위험 없음 · FA_D = 단서 없음·위험 없음 · 낮을수록 선"),
            ("cell", "5,760칸", "③ 칸 축 — 등록 분모 C팔/D팔 각 5,760칸",
             "같은 팔·같은 운용점 — 축만 바뀐다 (§6-6). 칸축에서는 긴축 지점에서 v3-A 가 더 나쁘다")]):
        ax = fig.add_subplot(gs[2, c])
        x = np.arange(len(OP9)); w = .20
        kc, kd = f"FA_C_{ax_key}", f"FA_D_{ax_key}"          # ← 전량 팔 (등록 분모)
        nc, nd = f"ncue_FA_C_{ax_key}", f"ncue_FA_D_{ax_key}"  # ← N9+N11 씬군 분해
        series = [("v2 · FA_C", [m(o2[n], kc) for n in OP9], [s(o2[n], kc) for n in OP9],
                   V2COL, None),
                  ("v3-A · FA_C", [m(o3[n], kc) for n in OP9], [s(o3[n], kc) for n in OP9],
                   V3COL, None),
                  ("v2 · FA_D", [m(o2[n], kd) for n in OP9], [s(o2[n], kd) for n in OP9],
                   V2COL, "///"),
                  ("v3-A · FA_D", [m(o3[n], kd) for n in OP9], [s(o3[n], kd) for n in OP9],
                   V3COL, "///")]
        for j, (lab, v, e, col, ht) in enumerate(series):
            off = (j - 1.5) * w
            ax.bar(x + off, v, w, color=col, edgecolor="white", lw=.9, hatch=ht,
                   label=lab, zorder=3)
            ax.errorbar(x + off, v, yerr=e, fmt="none", ecolor=C["ink"],
                        elinewidth=.9, capsize=2, zorder=4)
        # 씬군 분해 (N9+N11, 96프레임 / 1,920칸) — FA_C 막대 위에 겹쳐 찍는 부차 표식
        strat = "96프레임" if ax_key == "frame" else "1,920칸"
        ax.plot(x - 1.5 * w, [m(o2[n], nc) for n in OP9], ls="none", marker="s",
                ms=5.4, mfc="none", mec=C["mute"], mew=1.5, zorder=6,
                label=f"v2 · FA_C — N9+N11 씬군 분해 ({strat})")
        ax.plot(x - 0.5 * w, [m(o3[n], nc) for n in OP9], ls="none", marker="D",
                ms=5.0, mfc="none", mec=C["bad"], mew=1.5, zorder=6,
                label=f"v3-A · FA_C — N9+N11 씬군 분해 ({strat})")
        top = max(max(np.array(v) + np.array(e)) for _, v, e, _, _ in series)
        for j in (0, 1):
            lab, v, e, col, _ = series[j]
            for i in range(len(OP9)):
                ax.text(x[i] + (j - 1.5) * w, v[i] + e[i] + .012 * top,
                        f"{v[i]:.3f}".lstrip("0"), ha="center", va="bottom",
                        fontsize=6.6, color=col, rotation=90, zorder=7)
        ax.set_xticks(x)
        ax.set_xticklabels([OPLBL[n].replace("\n", " ") for n in OP9], fontsize=7.6)
        top = max(top, max(m(o2[n], nc) for n in OP9), max(m(o3[n], nc) for n in OP9))
        ax.set_ylim(0, top * 1.20)
        ax.set_ylabel(f"계기판③ FA ({'프레임' if ax_key == 'frame' else '칸'}축)"
                      f"\n등록 분모 = 팔 전량 {unit}", fontsize=9.4)
        ax.set_title(ttl, fontsize=11.6, fontweight="bold", color=C["ink"], pad=60)
        ax.text(.5, 1.170, sub, transform=ax.transAxes, ha="center", va="bottom",
                fontsize=8.4, color=C["mute"])
        ax.grid(axis="y", color=C["grid"], lw=.8, zorder=0); ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.legend(loc="lower center", bbox_to_anchor=(.5, 1.012), ncol=3,
                  fontsize=7.6, frameon=False)

        # ---- ③-2 : FA_C − FA_D (단서-유발 오경보 몫) ------------------------
        axd = fig.add_subplot(gs[3, c])
        dk = f"FA_diff_{ax_key}"
        grouped(axd, OP9, [m(o2[n], dk) for n in OP9], [s(o2[n], dk) for n in OP9],
                [m(o3[n], dk) for n in OP9], [s(o3[n], dk) for n in OP9],
                f"FA_C − FA_D ({'프레임' if ax_key == 'frame' else '칸'}축) · 분모 {unit}",
                f"③-2 단서-유발 오경보 몫 — {'프레임' if ax_key == 'frame' else '칸'} 축 (등록 분모)",
                "시드별로 뺀 뒤 mean · σ(ddof=1) — 부호만으로 개선을 선언하지 않는다 (PREREG §2.3)",
                title_pad=46, sub_y=1.110)
        d2n = [diff_stat(o2[n], nc, nd) for n in OP9]
        d3n = [diff_stat(o3[n], nc, nd) for n in OP9]
        axd.plot(x - 0.18, [a for a, _ in d2n], ls="none", marker="s", ms=5.4,
                 mfc="none", mec=C["mute"], mew=1.5, zorder=6,
                 label=f"v2 — N9+N11 씬군 분해 ({strat})")
        axd.plot(x + 0.18, [a for a, _ in d3n], ls="none", marker="D", ms=5.0,
                 mfc="none", mec=C["bad"], mew=1.5, zorder=6,
                 label=f"v3-A — N9+N11 씬군 분해 ({strat})")
        axd.set_ylim(0, max(axd.get_ylim()[1] / 1.30,
                            max(a for a, _ in d2n), max(a for a, _ in d3n)) * 1.20)
        axd.axhline(0, color=C["ink"], lw=1.0, zorder=2)
        axd.legend(loc="lower center", bbox_to_anchor=(.5, 1.012), ncol=4,
                   fontsize=7.6, frameon=False)

    # ---------------------------------------------------------------- 머리 ----
    fig.suptitle("계기판 ①②③ — before(v2) / after(v3-A)", fontsize=21.5,
                 fontweight="bold", color=C["ink"], y=Yd(0.46))
    fig.text(.058, Yd(0.98),
             "무대 = test-ext 4팔 (v2·v3-A 모두 미학습) · 쌍 = 계기판① (A,C) / 계기판② (A,B) / "
             "계기판③ 팔별 단독 FA(C·D) · 시드 rgb_s42·s43·s44 · 오차막대 = σ(ddof=1, n=3).",
             fontsize=11.0, color=C["mute"], ha="left", va="top")
    fig.text(.058, Yd(1.32),
             "계기판①의 풀링 층은 **sceneH1 + sceneH2 = 51프레임 / 393칸**이다. "
             "**sceneH3(21프레임)는 완전-은닉 층이라 여기에 절대 들어가지 않는다** "
             "(PREREG §2.1 층화 3 — 그 층의 보고량은 recall 이 아니라 Δp 분포다).",
             fontsize=11.0, color=C["bad"], ha="left", va="top", fontweight="bold")
    fig.text(.058, Yd(1.64),
             "계기판③의 **등록 분모는 C팔·D팔 전량 288프레임 / 5,760칸**이다 (PREREG §2.3 · AC §4.10, "
             "void 버킷 공집합). N9+N11 은 그 아래의 **씬군 분해**이므로 막대 위 표식으로만 겹쳐 찍었다.",
             fontsize=10.4, color=C["ink"], ha="left", va="top", fontweight="bold")
    ct = {}
    for side, tag in (("v2", "v2"), ("v3", "v3-A")):
        o = {r["name"]: r for r in dc[side]["ops"]}["tau_op"]
        ct[side] = (m(o, "frame_recall_H"), m(o, "cell_recall_H"),
                    m(o, "frame_fa_off"), m(o, "cell_fpr_off"))
    fig.text(.058, Yd(1.98),
             "참고 · **계기판이 아님 · 무대가 다름** (test-core / 교정 GT · verdict_core.json) — "
             f"τ_op 0.5 H recall  v2 프레임 {ct['v2'][0]:.3f} / 칸 {ct['v2'][1]:.3f} "
             f"@ FA 프레임 {ct['v2'][2]:.3f} / 칸 {ct['v2'][3]:.4f}   ↔   "
             f"v3-A 프레임 {ct['v3'][0]:.3f} / 칸 {ct['v3'][1]:.3f} "
             f"@ FA 프레임 {ct['v3'][2]:.3f} / 칸 {ct['v3'][3]:.4f}.  "
             "PREREG §6-11(무대 위반) 때문에 이 수치는 위 계기판 어느 축에도 들어가지 않는다.",
             fontsize=9.2, color=C["mute"], ha="left", va="top")
    footer(fig,
           "원장  ① ③  experiments/v3_0823/v2_textext_tables.json → summary.rgb.ops[]  ·  "
           "experiments/v3_0823/v3a_textext_tables.json → raw.summary.v3a_rgb.ops[]  "
           "(③ 전량 = FA_{C,D}_{frame,cell} · FA_diff_* / 씬군 분해 = ncue_FA_*)\n"
           "       ②  experiments/v3_0823/verdict_dash2.json → unit_static · per_run[*].ops[0].units/reg · summary.v3a_rgb.ops[]  "
           "(v2 팔 없음 — v2_reference.why_no_v2_arm)\n"
           "       참고행  experiments/v3_0823/verdict_core.json → v2.ops[] / v3.ops[] (test-core · 계기판 아님)  ·  " + GRIDSTR + "\n"
           + SEEDSET.replace("표기 확률은 **3시드 평균**", "집계 = 3시드 mean ± σ(ddof=1)")
           + "  ·  운용점 τ_op 0.5 + FA-정합 이중축 8지점 (정합 기준 팔 = D팔)  ·  "
           "분모  ① 51프레임 / 393칸  ②  단위 = (씬 × 밴드), 살아있는 4단위 (n_paired ≥ 10)  "
           "③ **팔 전량 288프레임 / 5,760칸** (씬군 분해 표식은 N9+N11 96프레임 / 1,920칸)  ·  "
           + CD_GT + "  ·  " + DATE, y=.008)
    return save(fig, "panel_d_before_after.png", dpi=118), fig


# ================================================================= 색인 ====
def write_index(res, picks_b, nb_cuts, nb_pairs, picks_c, key_a, na_twin, na_margin, allb):
    def kfmt(k):
        return f"`{k[1]}` / 밴드 `{k[0]}` / `{k[2]}`"
    lines = []
    lines.append("# PANELS_VERDICT — v3-A VERDICT 웨이브 의무 정성 패널 4종\n")
    lines.append(f"- **작성** Claude Code · {DATE} · **CPU 전용 · 새 렌더 0 · 새 추론 0 · GPU 0 · git 무접촉**")
    lines.append("- **생성기** `experiments/v3_0823/code/verdict_panels.py`")
    lines.append("  ```bash\n  PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES= \\\n"
                 "    /home/vislab/miniconda3/envs/env_seg/bin/python \\\n"
                 "    experiments/v3_0823/code/verdict_panels.py            # 약 6초 · 4장 전부\n"
                 "  #  --force  이미 있는 PNG 도 다시 그린다 (기본은 이어그리기 · resume-safe)\n"
                 "  #  --only a|b|c|d  한 장만\n  ```")
    lines.append("- **결정성**: 난수 없음 · 선택 규칙은 모두 전순서 정렬 — 재실행하면 PNG 가 **바이트 동일**하다 (실측).")
    lines.append("- **격자** `gridspec_v1.json` (`PROVISIONAL-GRID-V1` · 4밴드 × 5섹터 = **20칸**)")
    lines.append("- **시드** `rgb_s42` · `rgb_s43` · `rgb_s44` — 오버레이 확률은 **3시드 평균**, "
                 "막대의 오차막대는 **σ(ddof=1, n=3)**")
    lines.append("- **동결 규약 준수** (`PREREG_V3.md`): 한국어 라벨 · 패널마다 출처 푸터 · "
                 "`sceneH3`(완전-은닉 층) 계기판① 풀링 제외 · recall 은 FA 동반 인쇄 · "
                 "프레임축·칸축 **동시** 인쇄 · C·D팔 GT 는 사양 상수 전 칸 음성 명시 · PNG ≤ 2 MB\n")
    lines.append("---\n")
    lines.append("## 0. 한눈에\n")
    lines.append("| 파일 | 무엇을 보이나 | 고른 컷 / 키 | 원장 |")
    lines.append("|---|---|---|---|")
    rows = [
        ("panel_a_fourarm.png",
         "한 포즈를 A/B/C/D 네 팔로 재렌더한 바이트-쌍 컷 위에 v2(위)·v3-A(아래)의 20칸 확률 히트를 되투영. "
         "GT-양성 칸은 하늘색 이중 윤곽.",
         kfmt(key_a) + f" — v3-A 트윈 적중 {na_twin}칸 · 최대 마진 {na_margin:.3f}",
         "`eval_v3textext/*` · `eval_v3a_textext/*` · `dataset_manifest_v3_textext{,_bd}.json` · `gridspec_v1.json`"),
        ("panel_b_dash1_exemplars.png",
         "계기판① 대표 짝 — v3-A 는 A팔에서 켜고 C팔에서 끄는데(트윈-조건부 적중) 같은 칸에서 v2 는 A·C 둘 다 켠다.",
         " · ".join(kfmt(k) + f" → 결정 칸 **{cs[0]['cell']}**" for k, cs in picks_b),
         "위와 동일"),
        ("panel_c_ncue_trap.png",
         "N-cue 함정 — `sceneN9`/`sceneN11` 은 GT 전 칸 음성이라 색칠된 쐐기가 **전부 오경보**. C팔(단서 있음) vs D팔(단서 없음).",
         " · ".join(kfmt(p["key"]) + f" (v2 C {p['n2c']}칸 · v3 C {p['n3c']}칸)" for p in picks_c),
         "위와 동일"),
        ("panel_d_before_after.png",
         "계기판 ①②③ before(v2)/after(v3-A) 막대·산점. ① 트윈-조건부 recall (프레임축+칸축, FA-정합 8지점), "
         "② CUE-OFF 용량-반응 (v3 단독), ③ N-cue 함정 FA_C·FA_D·차 (프레임축+칸축).",
         "수치 전용 — 컷 선택 없음",
         "`v2_textext_tables.json` · `v3a_textext_tables.json` · `verdict_dash2.json` · `verdict_core.json`(참고행)"),
    ]
    for (fn, what, cut, led), r in zip(rows, res):
        (path, sz, dim) = r
        lines.append(f"| **`{fn}`**<br>{dim[0]}×{dim[1]} px · {sz/1024:.0f} KB | {what} | {cut} | {led} |")
    lines.append("")
    lines.append("---\n")

    lines.append("## 1. `panel_a_fourarm.png` — 한 포즈 · 네 팔\n")
    lines.append(f"- **고른 컷**: {kfmt(key_a)}  (A·B·C·D 네 라운드가 같은 밴드라운드·같은 파일 이름을 "
                 "공유하는 바이트-쌍 포즈)")
    lines.append("- **선택 규칙(결정적)**: 풀링 strict-H 층(paired-H ∩ {sceneH1, sceneH2}) 중 "
                 "v3-A 의 트윈-조건부 적중 칸 수 최대 → GT-양성 칸의 최대 마진 (p_A − p_C) → 키 사전순.")
    lines.append(f"  선택된 컷의 적중 칸 **{na_twin}칸**, 최대 마진 **{na_margin:.3f}**.")
    lines.append("- **열 라벨**: `A 팔 (위험 ON · 단서 유지)` · `B 팔 (위험 ON · 단서 제거)` · "
                 "`C 팔 (위험 OFF · 단서 유지)` · `D 팔 (위험 OFF · 단서 제거)`. "
                 "행 라벨: `v2 (레시피 동결 체크포인트)` / `v3-A`.")
    lines.append("- **오버레이**: 칸마다 `inferno` 램프로 확률을 칠하고(투명도도 확률에 비례) "
                 "τ_op 0.5 이상이면 흰 테두리를 두른다. GT-양성 칸은 검정+하늘색 이중 윤곽.")
    lines.append("- **A·B팔 GT 는 동일**(VG-01), **C·D팔 GT 는 사양 상수 전 칸 음성**(AC-INSTR-1 C3-2) — "
                 "C·D 타일에서 보이는 색은 전부 오경보다.\n")

    lines.append("## 2. `panel_b_dash1_exemplars.png` — 계기판① 대표 짝\n")
    lines.append("- **선택 규칙(등록 · 완화 없음)**: 풀링 층(`sceneH1`+`sceneH2`, **`sceneH3` 원천 제외**)의 "
                 "paired-H 컷에서 τ=0.5·3시드 평균 확률으로")
    lines.append("  1. v3-A 가 **GT-양성 칸**에서 **A팔 발화 ∧ C팔 미발화** (트윈-조건부 적중)")
    lines.append("  2. **같은 칸**에서 v2 는 **A팔·C팔 둘 다 발화** (무조건 발화)")
    lines.append(f"- **결과**: 규칙을 만족하는 컷 **{nb_cuts}개**, (컷,칸) 짝 **{nb_pairs}개**. "
                 f"마진 (p3_A − p3_C) 상위 **{len(picks_b)}컷**을 인쇄했다"
                 + ("." if nb_cuts >= 3 else " (3개 미만이라 존재분만 인쇄 — 규칙 완화 없음)."))
    import collections as _c
    _sc = _c.Counter(k[1] for k in allb)
    lines.append("- **씬 분포 (실측 · 특기)**: 규칙을 만족하는 컷의 씬 분포는 "
                 + " · ".join(f"`{a}` {b}개" for a, b in sorted(_sc.items()))
                 + " 이다. 즉 **`sceneH1`(둔덕형, 33프레임)에서는 이 조건을 만족하는 컷이 "
                   "하나도 없었다** — H1 은 (A,C) 광학차 자체가 작은 층이라(mean|ΔI| 중앙값 "
                   "H2 7.67 vs H1 2.43, PREREG §2.1 층화 1) v3-A 가 A/C 를 가를 여지가 적다. "
                   "패널 3행이 모두 `sceneH2` 인 것은 선택 편향이 아니라 **후보 집합 자체가 그렇기 때문**이다.")
    lines.append("")
    lines.append("| 행 | 컷 | 결정 칸 | v3-A A팔 | v3-A C팔 | v2 A팔 | v2 C팔 |")
    lines.append("|---|---|---|---|---|---|---|")
    for i, (k, cs) in enumerate(picks_b, 1):
        c0 = cs[0]
        lines.append(f"| {i} | {kfmt(k)} | **{c0['cell']}** | {c0['p3a']:.3f} (발화) | "
                     f"{c0['p3c']:.3f} (미발화) | {c0['p2a']:.3f} (발화) | {c0['p2c']:.3f} (발화) |")
    lines.append("")
    lines.append("- **분모**: paired-H ∩ {sceneH1, sceneH2} = **51프레임 / 393칸** "
                 "(`sceneH3` 21프레임은 완전-은닉 층이라 제외 — PREREG §2.1 층화 3).")
    lines.append("- 열은 `v2·A팔` / `v2·C팔` / `v3-A·A팔` / `v3-A·C팔` 4칸이고 행은 컷이다 (3×4 이미지 격자).\n")

    lines.append("## 3. `panel_c_ncue_trap.png` — N-cue 함정\n")
    lines.append("- **씬**: `sceneN9` · `sceneN11` — **네 팔 모두 GT 전 칸 음성**(실측 0칸). "
                 "따라서 이 패널에서 **색칠된 모든 쐐기는 오경보**다.")
    lines.append("- **열**: `C 팔 (단서 있음 · 위험 없음)` / `D 팔 (단서 없음 · 위험 없음)` 을 v2·v3-A 각각 (3×4 격자).")
    lines.append("- **선택 규칙(결정적)**: τ=0.5·3시드 평균에서 v2 의 C팔 발화 칸 수 내림차순 → "
                 "C팔 최대확률 내림차순 → 키 사전순, (씬, 밴드라운드) 조합 비중복 탐욕 3컷.")
    lines.append("")
    lines.append("| 행 | 컷 | v2 C팔 발화 | v3-A C팔 발화 | v2 D팔 | v3-A D팔 | v2 C팔 최대 p (칸) |")
    lines.append("|---|---|---|---|---|---|---|")
    for i, p in enumerate(picks_c, 1):
        lines.append(f"| {i} | {kfmt(p['key'])} | {p['n2c']}칸 | {p['n3c']}칸 | {p['n2d']}칸 | "
                     f"{p['n3d']}칸 | {p['max2c']:.3f} ({p['top2c']}) |")
    lines.append("")
    lines.append("- **분모**: 이 패널은 `sceneN9`+`sceneN11` = 팔마다 **96프레임 / 1,920칸** — "
                 "계기판③의 **씬군 분해**다. 등록된 헤드라인 분모는 **C·D팔 전량 288프레임 / 5,760칸** "
                 "(PREREG §2.3 · AC §4.10, void 버킷 공집합)이며 `panel_d` 가 그것을 주 막대로 인쇄한다.")
    lines.append("- `FA_C − FA_D` = **단서-유발 오경보 몫**, `FA_D` = 순수 씬-연합의 직접 게이지 (PREREG §2.3).\n")

    lines.append("## 4. `panel_d_before_after.png` — 계기판 ①②③ before/after\n")
    lines.append("| 블록 | 무엇 | 축 | 원장 키 |")
    lines.append("|---|---|---|---|")
    lines.append("| **①** | 트윈-조건부 recall, 풀링 H1+H2 (n=51프레임 / 393칸), FA-정합 8지점에서 v2 vs v3-A | "
                 "**프레임축 + 칸축 둘 다** (각 x눈금 아래에 동반 `FA_D` 를 `v2\\|v3` 로 병기 — §6-5 FA 동반 의무) | "
                 "`v2_textext_tables.json::summary.rgb.ops[].pooled_{frame,cell}_recall_twin` · "
                 "`v3a_textext_tables.json::raw.summary.v3a_rgb.ops[]` 동일 키 |")
    lines.append("| **②** | CUE-OFF 용량-반응 — 살아있는 **4단위**(씬×밴드, `n_paired ≥ 10`) 산점 + 적합선. "
                 "x = 제거된 단서 키 수 / 광학 `mean\\|ΔI\\|`, y = `FA_B` | "
                 "**프레임축(●, 왼쪽 눈금) + 칸축(▲, 오른쪽 눈금)** 동시 | "
                 "`verdict_dash2.json::unit_static` · `per_run[*].ops[0].units` · `…reg` · `summary.v3a_rgb.ops[]` |")
    lines.append("| **③** | N-cue 함정 FA — `FA_C` · `FA_D` 막대(빗금 = D팔)와 별도 행의 `FA_C − FA_D`, "
                 "τ_op + FA-정합 8지점. **주 막대 = 등록 분모(C·D팔 전량 288프레임 / 5,760칸)**, "
                 "그 위에 겹친 표식 = **N9+N11 씬군 분해**(96프레임 / 1,920칸) | **프레임축 + 칸축 둘 다** | "
                 "양 표의 `FA_{C,D}_{frame,cell}` · `FA_diff_{frame,cell}` (전량) 와 "
                 "`ncue_FA_{C,D}_{frame,cell}` (씬군 분해 · 차는 **시드별로 뺀 뒤** mean·σ) |")
    lines.append("")
    lines.append("- **② 에는 v2 팔이 없다** — B팔이 v3 훈련팔이라 v2 체크포인트의 before 가 성립하지 않는다 "
                 "(`PREREG_V3.md` §2.2 **주의** · `verdict_dash2.json::v2_reference.why_no_v2_arm`). "
                 "그래서 ② 는 **v3-A 단독 절대값 + 층별 기울기**이며 before/after 비교가 아니다. 패널에 그대로 인쇄돼 있다.")
    lines.append("- `sceneH3|base` 단위는 `n_paired 3 < 10` 으로 **VOID** — 회귀에서 빼고 ✕ 로 표시한 뒤 사유를 붙였다 "
                 "(VG-void: void ≠ 음성).")
    lines.append("- `verdict_core.json` 은 **test-core** 헤드라인이라 계기판 어느 축에도 넣지 않았다 "
                 "(PREREG §6-11 무대 위반). 머리글에 참고 한 줄로만 적었고, 그 줄도 recall 과 FA 를 "
                 "프레임축·칸축 모두 병기했다.\n")
    lines.append("---\n")
    lines.append("## 5. 무결성 자기점검\n")
    lines.append("| 규약 | 확인 |")
    lines.append("|---|---|")
    lines.append("| 한국어 라벨 | 4/4 패널 제목·축·범례 전부 한국어 |")
    lines.append("| 출처 푸터 (원장 · 런/시드 · 운용점 · 분모 · 날짜) | 4/4 패널 |")
    lines.append("| `sceneH3` 풀링 금지 | 계기판① 풀링 = H1+H2 51프레임 (코드에서 `HIDDEN_SCENE` 을 선택 모집단에서 제외) |")
    lines.append("| recall 에 FA 동반 | ① 의 x눈금마다 `FA_D` 병기 + ③ 이 같은 그림 안에 있음 |")
    lines.append("| 프레임축·칸축 동시 | ① ② ③ 전부 두 축을 인쇄 |")
    lines.append("| C·D팔 GT = 사양 상수 전 칸 음성 | (a)(b)(c) 타일 캡션과 4개 푸터 전부에 명시 |")
    lines.append("| PNG ≤ 2 MB | " + " · ".join(f"{r[0].split('/')[-1]} {r[1]/1024:.0f} KB" for r in res) + " |")
    lines.append("")
    p = os.path.join(OUT, "PANELS_VERDICT.md")
    open(p, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"  {'PANELS_VERDICT.md':30s} {os.path.getsize(p)/1024:8.0f} KB")
    return p


# ================================================================== main ===
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true",
                    help="이미 있는 PNG 도 다시 그린다 (기본은 이어그리기 · resume-safe)")
    ap.add_argument("--only", default=None, help="a|b|c|d 중 하나만")
    a = ap.parse_args(argv)

    print(f"[grid] {GRID.summary()}")
    print("[load] 확률 원장 (CSV 12개, 재추론 없음) …")
    V2A = load_arms("eval_v3textext")
    V3AA = load_arms("eval_v3a_textext")
    MAN = load_manifests()
    print(f"       v2 {sum(len(V2A[x]) for x in 'ABCD')}행 · "
          f"v3-A {sum(len(V3AA[x]) for x in 'ABCD')}행 · 매니페스트 {len(MAN)}행")

    # 게이트: A/B GT 동일 · C/D GT 전 칸 음성 · N-cue 전 팔 음성
    assert all(np.array_equal(V2A["A"][k]["g"], V2A["B"][k]["g"]) for k in V2A["A"]), "VG-01"
    assert sum(int(V2A[x][k]["g"].sum()) for x in "CD" for k in V2A[x]) == 0, "VG-02"
    assert sum(int(V2A[x][k]["g"].sum()) for x in "ABCD" for k in V2A[x]
               if k[1] in NCUE_SCENES) == 0, "N-cue GT 는 전 팔 음성이어야 한다"
    for x in "ABCD":
        assert set(V2A[x]) == set(V3AA[x]), "v2/v3 컷 집합 불일치"

    pk, hidden = pool_keys(V2A)
    print(f"[stratum] paired-H 풀링 {len(pk)}프레임 (H1+H2) · "
          f"완전-은닉 sceneH3 {len(hidden)}프레임 = 풀링에서 제외")
    if len(pk) != 51:
        raise SystemExit(f"[fatal] 풀링 층 {len(pk)} != 51 (PREREG §2.1 as-built)")

    key_a, na_twin, na_margin = select_a(V2A, V3AA, pk)
    picks_b, nb_cuts, nb_pairs, allb = select_b(V2A, V3AA, pk)
    picks_c, allc = select_c(V2A, V3AA)
    print(f"[select] (a) {key_a}  트윈 {na_twin}칸 · 마진 {na_margin:.3f}")
    print(f"[select] (b) 규칙 만족 컷 {nb_cuts} · (컷,칸) 짝 {nb_pairs} → 인쇄 {len(picks_b)}컷")
    for k, cs in picks_b:
        print(f"          {k} → {cs[0]['cell']}  v3 A/C {cs[0]['p3a']:.3f}/{cs[0]['p3c']:.3f}"
              f"  v2 A/C {cs[0]['p2a']:.3f}/{cs[0]['p2c']:.3f}")
    print(f"[select] (c) N-cue 후보 {len(allc)}컷 → 인쇄 {len(picks_c)}컷")
    for p in picks_c:
        print(f"          {p['key']}  v2C {p['n2c']}칸 · v3C {p['n3c']}칸 · "
              f"v2D {p['n2d']}칸 · v3D {p['n3d']}칸")

    d2, d3, dd, dc, o2, o3 = ledger_tables()

    jobs = [("a", "panel_a_fourarm.png", lambda: panel_a(V2A, V3AA, MAN, key_a, na_twin, na_margin)),
            ("b", "panel_b_dash1_exemplars.png", lambda: panel_b(V2A, V3AA, MAN, picks_b, nb_cuts, nb_pairs)),
            ("c", "panel_c_ncue_trap.png", lambda: panel_c(V2A, V3AA, MAN, picks_c)),
            ("d", "panel_d_before_after.png", lambda: panel_d(o2, o3, dd, dc))]
    res = []
    print("[draw]")
    for tag, name, fn in jobs:
        p = os.path.join(OUT, name)
        if a.only and a.only != tag:
            import PIL.Image as I
            res.append((p, os.path.getsize(p), I.open(p).size) if os.path.isfile(p) else None)
            continue
        if os.path.isfile(p) and not a.force:
            import PIL.Image as I
            sz, dim = os.path.getsize(p), I.open(p).size
            print(f"  {name:30s} {sz/1024:8.0f} KB  {dim}   [skip · 이미 있음 (--force 로 재생성)]")
            res.append((p, sz, dim))
            continue
        r, fig = fn()
        plt.close(fig)
        res.append(r)
    if all(x is not None for x in res):
        write_index(res, picks_b, nb_cuts, nb_pairs, picks_c, key_a, na_twin, na_margin, allb)
    print("[done]", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
