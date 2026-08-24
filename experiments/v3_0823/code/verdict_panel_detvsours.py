#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verdict_panel_detvsours.py — panel (f) 「같은 프레임, 두 시스템의 눈」 (CPU 전용).

    PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES= \
      python3 experiments/v3_0823/code/verdict_panel_detvsours.py [--force]

산출 → `experiments/v3_0823/panels/verdict/panel_f_det_vs_ours.png`

한 프레임을 세 열로 나란히 놓는다.

  (1) 입력 + 정답(GT)      — 원본 컷 + GT-양성 칸의 지면 쐐기(초록 파선) + 층(V/H/E) 배지
  (2) 검출기의 눈 (YOLO)   — 같은 컷 + **동결 예측 상자** (τ_conf 0.25) 그대로.
                             상자가 없으면 아무것도 그리지 않고 「검출 0건」 칩만 찍는다.
  (3) 본 접근의 눈 (칸 확률) — 같은 컷 + 20칸 확률 히트 (inferno 램프),
                             발화 칸(p ≥ 0.5) 흰 실선, GT 칸 초록 파선.

행 = 프레임 1장.
  1행 V  — 낙차의 몸체가 보이는 컷. **검출기도 맞힌다** (정직성 + 설득력의 축).
  2행 H  — 같은 씬(scene14) · 몸체가 지평 뒤로 사라진 컷. 검출은 상자 0개.
  3행 H  — scene15 골목 회랑. 검출은 상자 0개.
  4행 E  — 테두리만 보이는 컷(scene18 해안 테라스). 검출은 상자 0개.

**규약 (`PREREG_V3.md` 동결 — 하나도 완화하지 않는다)**
  1. 한국어 라벨.
  2. 출처 푸터: 읽은 원장 파일 · 런/시드 · 운용점 · 분모 · 날짜.
  3. recall 은 FA 동반 인쇄 없이 찍지 않는다 (§6-5) — 상단 표에 off팔 FA 병기.
  4. 재추론 0 · 재렌더 0 · GPU 0 · git 무접촉. 확률도 상자도 **이미 덤프된 파일**에서 읽는다.
  5. PNG ≤ 2 MB.

**세대 정합**: 본 접근은 **v2 rgb_s42** (YOLO 베이스라인과 **같은 세대 · 같은 test-core ·
같은 매니페스트 세대**)를 쓴다. v3-A 덤프를 쓰면 세대가 어긋나 헤드라인 비교가 불공정해진다.

**폰트 · 색 · footer() · save() · cam_of() · wedge_px()** 는
`experiments/v3_0823/code/verdict_panels.py` (원 출처 `make_panels_v3.py` L26-59, L101-132) 의
것을 **그대로 복사**했다 — 투영 수식 한 줄도 바꾸지 않았다.
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
DAY = os.path.join(ROOT, "experiments/dayrun_0820")
OUT = os.path.join(V3, "panels/verdict")
os.makedirs(OUT, exist_ok=True)

# ---- [복사: verdict_panels.py L52-73] 폰트 · 색 · 날짜 ----------------------
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

C = dict(rgb="#4C6FBF", depth="#D97C2B", b2="#7E8794",
         pub="#B9C2D0", cor="#2F4B7C", ok="#2E7D5B", bad="#B03A48",
         grid="#DDE1E6", ink="#1F2429", mute="#5C6672")

DATE = "2026-08-24"
GTCOL = "#25E07A"            # GT 칸 = 초록 파선 (1열·3열 공통)
BOXCOL = "#D97C2B"           # YOLO 상자 = 주황 (검출기의 어휘)
TIERCOL = dict(V="#2F4B7C", H="#B03A48", E="#C08400")
TIERKR = dict(V="보이는 낙차", H="숨은 낙차", E="테두리만")


def footer(fig, text, y=0.012):
    """[복사: verdict_panels.py L76-79]"""
    fig.text(0.5, y, text, ha="center", va="bottom", fontsize=7.6,
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
from matplotlib.patches import Polygon, Rectangle       # noqa: E402
from matplotlib.lines import Line2D                     # noqa: E402
from PIL import Image                                   # noqa: E402

sys.path.insert(0, os.path.join(ROOT, "experiments/mainrun_0819/code"))
sys.path.insert(0, os.path.join(ROOT, "experiments/mainrun_0819/code/labeling"))
import labeler as L                                    # noqa: E402

GRIDPATH = os.path.join(ROOT, "experiments/mainrun_0819/code/labeling/gridspec_v1.json")
GSPEC = json.load(open(GRIDPATH))
assert GSPEC["version"] == "PROVISIONAL-GRID-V1", GSPEC["version"]
CELLS = [f"{s}{b}" for b in GSPEC["band_names"] for s in GSPEC["sector_names"]]
NS, NB = GSPEC["n_sectors"], GSPEC["n_bands"]
ASC = GSPEC["sector_edges_deg"][::-1]
BND = GSPEC["band_edges_m"]
assert NS * NB == 20 and len(CELLS) == 20


# ---- [복사: verdict_panels.py L125-153] 투영 -------------------------------
def cam_of(fr):
    sdir, fn = os.path.dirname(fr["rgb"]), os.path.basename(fr["rgb"])
    cuts = json.load(open(os.path.join(sdir, "variation.json")))["cuts"]
    if isinstance(cuts, dict):
        cuts = list(cuts.values())
    return next(c["cam"] for c in cuts if c["file"] == fn)


def wedge_px(cell, cam, n=36):
    """Ground wedge of `cell` -> image polygon (px, py) at the frame's ground_z."""
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
TAU_OURS = 0.5            # 본 접근 운용점 (rgb v2 metrics.json → tau_op)
TAU_YOLO = 0.25           # 검출기 동결 운용점 (yolo metrics.json → tau_op)
SEED_OURS = 42            # 헤드라인 오버레이 시드 (세대 = v2, YOLO 와 동일)
SEEDS = (42, 43, 44)

MANP = os.path.join(V3, "dataset_manifest_v2corr.json")
MAN = json.load(open(MANP))
FM = {f["frame_id"]: f for f in MAN["frames"]}

YOLO_LBL = os.path.join(DAY, "runs/yolo_s42/pred_test/labels")
YOLO_PF = os.path.join(DAY, "runs/yolo_s42/eval_test/per_frame.csv")
OURS_PF = os.path.join(DAY, f"runs/v2/rgb_s{SEED_OURS}/eval_test/per_frame_on.csv")


def read_pf(path):
    out = {}
    with open(path) as f:
        rd = csv.DictReader(f)
        cols = [c[2:] for c in (rd.fieldnames or []) if c.startswith("p_")]
        if cols != CELLS:
            raise SystemExit(f"[fatal] {path}: 칸 목록 불일치 {cols[:3]}… vs {CELLS[:3]}…")
        for r in rd:
            out[r["frame_id"]] = dict(
                scene=r["scene_id"], tier=r["tier"], toggle=r["toggle_state"],
                p=np.array([float(r[f"p_{c}"]) for c in CELLS]),
                g=np.array([float(r[f"g_{c}"]) for c in CELLS]))
    return out


YO = read_pf(YOLO_PF)
OU = read_pf(OURS_PF)


def label_stem(fid):
    """frame_id -> pred_test/labels 파일 stem (라운드 접미 `::boost_x` 포함)."""
    return fid.replace(".png::", "__").replace(".png", "").replace("/", "__")


# stem() 이 라벨 파일 전부를 덮는지 게이트 (매핑 오류로 상자를 '없다'고 잘못 찍는 사고 방지)
_files = {f[:-4] for f in os.listdir(YOLO_LBL) if f.endswith(".txt")}
_unreach = _files - {label_stem(f) for f in YO}
if _unreach:
    raise SystemExit(f"[fatal] 라벨 파일 {len(_unreach)}개가 frame_id 로 매핑 안 됨: "
                     f"{sorted(_unreach)[:3]}")


def yolo_boxes(fid, tau=TAU_YOLO):
    """동결 YOLO txt -> [(cx, cy, w, h, conf)] (정규화 · τ 이상 · 중복 줄 제거).

    ultralytics 는 검출이 하나도 없으면 txt 자체를 쓰지 않는다 -> 파일 없음 = 검출 0건.
    """
    p = os.path.join(YOLO_LBL, label_stem(fid) + ".txt")
    if not os.path.exists(p):
        return 0, []
    raw = [ln.split() for ln in open(p).read().split("\n") if ln.strip()]
    for r in raw:
        if len(r) != 6:
            raise SystemExit(f"[fatal] {p}: 줄 필드 {len(r)} != 6 (class cx cy w h conf)")
    uniq = sorted({tuple(float(v) for v in r[1:6]) for r in raw})
    return len(raw), [b for b in uniq if b[4] >= tau]


# ============================================================== 행 선택 =====
# 선택 규칙(결정적 · 아래 verify() 가 재현 검산한다)
#   V행 : test-core V 프레임 중 yolo_s42 가 **GT-양성 칸에 정합된 상자**를 낸 21장에서
#         최대 conf 상위 → 같은 씬을 2행과 공유하는 컷 우선 (scene14) → 키 사전순.
#   H행 : 씬별로 「rgb_s42 가 τ0.5 에서 GT-양성 칸을 ≥1 적중」 ∧ 「yolo_s42 상자 0개」
#         후보 중 적중 칸 수 최대 → GT 칸 최대확률 → 키 사전순.
#   E행 : 같은 규칙을 tier E 에 적용 (씬 scene18 만 후보가 존재).
ROWS = [
    dict(fid="on/scene14/L7__s20260819__0002.png",              tier="V",
         note="같은 광장 · 낙차의 몸체가 보이는 시점",
         read="검출기가 상자를 그린다 — 몸체 픽셀이 있으니까"),
    dict(fid="on/scene14/L5__s20260819__0006.png",              tier="H",
         note="같은 광장(scene14) · 지평선 뒤로 몸체가 사라진 시점",
         read="상자 0개 — 그릴 픽셀이 없다. 본 접근은 3b 밴드를 예고한다"),
    dict(fid="on/scene15/L0__s20260820__0006.png::boost_h",     tier="H",
         note="골목 회랑(scene15) · 굽이 뒤에 낙차",
         read="상자 0개. 본 접근은 회랑 끝 칸을 켠다"),
    dict(fid="on/scene18/L7__s20260821__0000.png::boost_e2",    tier="E",
         note="해안 테라스(scene18) · 테두리만 지평선에 걸린 시점",
         read="상자 0개 — 3시드 전부 E 45장 중 0장. 본 접근은 3a·3b 전 폭을 켠다"),
]


def verify():
    """모든 행의 층·상자·발화를 원장에서 재계산해 하드코딩과 대조한다."""
    rep = []
    for r in ROWS:
        fid = r["fid"]
        if fid not in FM:
            raise SystemExit(f"[fatal] 매니페스트에 없음: {fid}")
        if fid not in YO or fid not in OU:
            raise SystemExit(f"[fatal] 평가 덤프에 없음: {fid}")
        mt, yt, ot = FM[fid]["tier"], YO[fid]["tier"], OU[fid]["tier"]
        if not (mt == yt == ot == r["tier"]):
            raise SystemExit(f"[fatal] 층 불일치 {fid}: 매니페스트 {mt} / yolo {yt} / "
                             f"ours {ot} / 선언 {r['tier']}")
        if not np.array_equal(YO[fid]["g"] > .5, OU[fid]["g"] > .5):
            raise SystemExit(f"[fatal] GT 불일치(두 덤프) {fid}")
        nraw, bs = yolo_boxes(fid)
        g = OU[fid]["g"] > .5
        p = OU[fid]["p"]
        fired = p >= TAU_OURS
        r["n_raw"] = nraw
        r["boxes"] = bs
        r["gt_cells"] = [CELLS[i] for i in np.where(g)[0]]
        r["fired_cells"] = [CELLS[i] for i in np.where(fired)[0]]
        r["hit_cells"] = [CELLS[i] for i in np.where(g & fired)[0]]
        r["pmax_gt"] = float(p[g].max()) if g.any() else float("nan")
        # YOLO 의 칸-정합 (det2cell 규칙으로 이미 덤프된 값)
        r["yolo_hit_cells"] = [CELLS[i] for i in np.where(g & (YO[fid]["p"] >= TAU_YOLO))[0]]
        if r["tier"] == "V":
            if not bs:
                raise SystemExit(f"[fatal] V행인데 상자 0개: {fid}")
            if not r["yolo_hit_cells"]:
                raise SystemExit(f"[fatal] V행 상자가 GT 칸에 정합 안 됨: {fid}")
        else:
            if bs:
                raise SystemExit(f"[fatal] {r['tier']}행인데 상자 {len(bs)}개: {fid}")
        if not r["hit_cells"]:
            raise SystemExit(f"[fatal] 본 접근이 GT 칸을 하나도 못 맞힘: {fid}")
        rep.append(f"   {r['tier']}  {fid}\n"
                   f"      GT {len(r['gt_cells']):2d}칸 · YOLO 상자 {len(bs)}개"
                   f"(raw {nraw}줄) · YOLO 정합칸 {len(r['yolo_hit_cells'])}"
                   f" · rgb_s42 발화 {len(r['fired_cells']):2d}칸 / 적중 {len(r['hit_cells']):2d}칸"
                   f" · GT칸 최대 p {r['pmax_gt']:.3f}")
    print("[gate] 행 검산 통과")
    print("\n".join(rep))


# ============================================================== 집계 표 =====
def agg():
    """상단 표 — 두 시스템의 3시드 프레임축 recall @ off팔 FA (같은 세대 · 같은 분모)."""
    def rows(fmt):
        out = {}
        for k in ("frame_recall_V", "frame_recall_E", "frame_recall_H", "frame_fa_off"):
            v = []
            for s in SEEDS:
                m = json.load(open(fmt.format(s=s)))
                v.append(m["point"]["op"][k])
            out[k] = (sum(v) / len(v), (max(v) - min(v)) / 2.0, v)
        m = json.load(open(fmt.format(s=SEEDS[0])))
        out["_tau"] = m["tau_op"]
        out["_n"] = (m["counts"]["n_V"], m["counts"]["n_E"], m["counts"]["n_H"],
                     m["counts"]["n_off"])
        return out
    y = rows(os.path.join(DAY, "runs/yolo_s{s}/eval_test/metrics.json"))
    o = rows(os.path.join(DAY, "runs/v2/rgb_s{s}/eval_test/metrics.json"))
    assert y["_n"] == o["_n"], (y["_n"], o["_n"])          # 같은 분모 게이트
    assert y["_tau"] == TAU_YOLO and o["_tau"] == TAU_OURS
    assert max(y["frame_recall_H"][2]) == 0.0 and max(y["frame_recall_E"][2]) == 0.0, \
        "YOLO H/E 가 0 이 아니다 — 문안을 고쳐야 한다"
    # 교정 GT 재채점 원장과의 H행 대조 (H 는 교정 대상 밖이라 완전 동일해야 한다)
    RS = json.load(open(os.path.join(V3, "eval_v2corr/rescore_tables.json")))
    hc = RS["by_model"]["rgb"]["corrected"]["frame_recall_H"]
    assert abs(hc["mean"] - o["frame_recall_H"][0]) < 1e-12, (hc["mean"], o["frame_recall_H"][0])
    assert abs(hc["half_range"] - o["frame_recall_H"][1]) < 1e-12
    print(f"[gate] 집계 표 검산 통과 — 분모 V/E/H/off = {y['_n']}, "
          f"본 접근 H {o['frame_recall_H'][0]:.4f}±{o['frame_recall_H'][1]:.4f} "
          f"= eval_v2corr/rescore_tables.json 의 교정 GT 값")
    return y, o


# ============================================================== 그리기 ======
CMAP = plt.get_cmap("inferno")
IMW, IMH = 640, 360


def _frame_img(fr):
    return np.asarray(Image.open(fr["rgb"]).convert("RGB").resize((IMW, IMH), Image.LANCZOS))


def _blank(ax, img):
    if not (isinstance(img, np.ndarray) and img.ndim == 3 and float(img.std()) > 1.0):
        raise SystemExit("[fatal] 컷 이미지가 비었거나 단색이다 (imshow 전 게이트)")
    ax.imshow(img)
    ax.set_xticks([]); ax.set_yticks([])
    ax.tick_params(length=0)
    ax.set_xlim(0, IMW); ax.set_ylim(IMH, 0)
    for s in ax.spines.values():
        s.set_color(C["grid"]); s.set_linewidth(1.0)


def _wedge_xy(cell, cam):
    px, py, front, inb = wedge_px(cell, cam)
    if not front.all():
        return None
    sx, sy = IMW / L.W_IMG, IMH / L.H_IMG
    X, Y = px * sx, py * sy
    if X.max() < 0 or X.min() > IMW or Y.max() < 0 or Y.min() > IMH:
        return None
    return np.c_[X, Y]


def _chip(ax, x, y, txt, fc, *, ha="left", va="top", fs=9.0, tc="white", z=9, pad=3.0):
    ax.text(x, y, txt, transform=ax.transAxes, ha=ha, va=va, fontsize=fs,
            color=tc, fontweight="bold", zorder=z,
            bbox=dict(fc=fc, ec="none", pad=pad, alpha=.94))


def col_input(ax, r, fr, cam, img):
    """(1) 입력 + GT — GT 칸의 지면 쐐기를 초록 파선으로."""
    _blank(ax, img)
    off = []
    for cell in r["gt_cells"]:
        xy = _wedge_xy(cell, cam)
        if xy is None:
            off.append(cell); continue
        ax.add_patch(Polygon(xy, closed=True, fc=GTCOL, ec="none", alpha=.11, zorder=2))
        ax.add_patch(Polygon(xy, closed=True, fc="none", ec="black", lw=3.0, zorder=3))
        ax.add_patch(Polygon(xy, closed=True, fc="none", ec=GTCOL, lw=1.9,
                             ls=(0, (5, 3)), zorder=4))
    t = r["tier"]
    _chip(ax, .014, .972, f"  {t}  ·  {TIERKR[t]}  ", TIERCOL[t], fs=13.0, pad=4.6)
    _chip(ax, .986, .972, f"정답 칸 {len(r['gt_cells'])} / 20", "#000000",
          ha="right", fs=9.0, pad=3.0)
    ax.text(.014, .030, r["note"], transform=ax.transAxes, ha="left", va="bottom",
            fontsize=8.6, color="white", zorder=9,
            bbox=dict(fc="#000000", ec="none", pad=2.6, alpha=.62))
    if off:
        ax.text(.986, .030, "칸이 카메라 뒤 · 미표시: " + ",".join(off),
                transform=ax.transAxes, ha="right", va="bottom", fontsize=6.8,
                color="white", zorder=9,
                bbox=dict(fc="#000000", ec="none", pad=2.0, alpha=.55))


def col_yolo(ax, r, fr, cam, img):
    """(2) 검출기의 눈 — 동결 상자만. 없으면 「검출 0건」."""
    _blank(ax, img)
    for (cx, cy, w, h, cf) in r["boxes"]:
        x0, y0 = (cx - w / 2) * IMW, (cy - h / 2) * IMH
        ax.add_patch(Rectangle((x0, y0), w * IMW, h * IMH, fill=False,
                               ec="black", lw=4.2, zorder=3))
        ax.add_patch(Rectangle((x0, y0), w * IMW, h * IMH, fill=False,
                               ec=BOXCOL, lw=2.4, zorder=4))
        ax.text(np.clip(x0 + 5, 4, IMW - 120), np.clip(y0 + 5, 4, IMH - 22),
                f"낙차  conf {cf:.2f}", ha="left", va="top", fontsize=9.2,
                color="white", fontweight="bold", zorder=5,
                bbox=dict(fc=BOXCOL, ec="black", lw=.9, pad=2.6, alpha=.96))
    if r["boxes"]:
        _chip(ax, .014, .972, f"검출 {len(r['boxes'])}건  ·  정답칸 정합 "
                              f"{len(r['yolo_hit_cells'])}칸", BOXCOL, fs=10.0)
    else:
        ax.text(.5, .50, "검출 0건", transform=ax.transAxes, ha="center", va="center",
                fontsize=25, color="white", fontweight="bold", zorder=9,
                bbox=dict(fc="#000000", ec=BOXCOL, lw=2.6, pad=11, alpha=.80))
        ax.text(.5, .335, "동결 예측 파일 없음  ·  τ_conf 0.25 이상 상자 0개",
                transform=ax.transAxes, ha="center", va="center", fontsize=8.8,
                color="white", zorder=9,
                bbox=dict(fc="#000000", ec="none", pad=3.2, alpha=.62))
    ax.text(.986, .030, "yolo_s42 · pred_test 동결 · τ_conf 0.25",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=7.2,
            color="white", zorder=9,
            bbox=dict(fc="#000000", ec="none", pad=2.2, alpha=.55))


def col_ours(ax, r, fr, cam, img):
    """(3) 본 접근의 눈 — 20칸 확률 히트."""
    _blank(ax, img)
    p, g = OU[r["fid"]]["p"], OU[r["fid"]]["g"] > .5
    hidden = []
    for i in np.argsort(p):                       # 낮은 확률부터 → 높은 칸이 위로
        cell = CELLS[i]
        xy = _wedge_xy(cell, cam)
        if xy is None:
            if p[i] >= TAU_OURS or g[i]:
                hidden.append(cell)
            continue
        pv = float(p[i])
        ax.add_patch(Polygon(xy, closed=True, fc=CMAP(pv), ec="none",
                             alpha=0.06 + 0.56 * pv, zorder=2))
        if pv >= TAU_OURS:
            ax.add_patch(Polygon(xy, closed=True, fc="none", ec="white", lw=1.7, zorder=3))
        else:
            ax.add_patch(Polygon(xy, closed=True, fc="none", ec="white", lw=0.5,
                                 alpha=.30, zorder=3))
        if g[i]:
            ax.add_patch(Polygon(xy, closed=True, fc="none", ec="black", lw=3.0, zorder=4))
            ax.add_patch(Polygon(xy, closed=True, fc="none", ec=GTCOL, lw=1.7,
                                 ls=(0, (5, 3)), zorder=5))
    nfa = len(r["fired_cells"]) - len(r["hit_cells"])
    _chip(ax, .014, .972,
          f"발화 {len(r['fired_cells'])}칸  ·  정답칸 적중 {len(r['hit_cells'])}칸"
          + (f"  ·  헛발 {nfa}칸" if nfa else ""), C["cor"], fs=10.0)
    _chip(ax, .986, .972, f"GT칸 최대 p {r['pmax_gt']:.2f}", "#000000",
          ha="right", fs=9.0)
    ax.text(.014, .030, r["read"], transform=ax.transAxes, ha="left", va="bottom",
            fontsize=8.6, color="white", zorder=9,
            bbox=dict(fc="#000000", ec="none", pad=2.6, alpha=.62))
    if hidden:
        ax.text(.986, .030, "칸이 카메라 뒤 · 미표시: " + ",".join(hidden),
                transform=ax.transAxes, ha="right", va="bottom", fontsize=6.8,
                color="white", zorder=9,
                bbox=dict(fc="#000000", ec="none", pad=2.0, alpha=.55))


# ============================================================== 조립 ========
def build():
    verify()
    Y, O = agg()

    fig = plt.figure(figsize=(15.8, 17.6))
    gs = fig.add_gridspec(4, 3, left=.043, right=.988, top=.775, bottom=.126,
                          hspace=.055, wspace=.014)
    # NOTE: 위치는 SubplotSpec.get_position(fig) 로 읽는다 — add_subplot 으로 읽으면
    # 이미 그린 타일 위에 **빈 축**이 하나 더 생겨 그림을 덮어버린다 (08-24 사고).
    pos = lambda k, j: gs[k, j].get_position(fig)
    tiles = []                                            # (row, col, ax) 자기점검용

    for k, r in enumerate(ROWS):
        fr = FM[r["fid"]]
        cam = cam_of(fr)
        img = _frame_img(fr)
        for j, fn in enumerate((col_input, col_yolo, col_ours)):
            ax = fig.add_subplot(gs[k, j])
            fn(ax, r, fr, cam, img)
            tiles.append((k, j, ax))
        bb = pos(k, 0)                                   # 왼쪽 여백의 층 배지 (행 라벨)
        fig.text(.019, (bb.y0 + bb.y1) / 2, f"{k + 1}행  ·  {r['tier']}  {TIERKR[r['tier']]}",
                 rotation=90, ha="center", va="center", fontsize=12.0,
                 fontweight="bold", color=TIERCOL[r["tier"]])

    # ---- 열 머리글 ---------------------------------------------------------
    heads = [("입력 + 정답 (GT)", "초록 파선 = 진짜 낙차가 놓인 지면 칸", C["ink"]),
             ("검출기의 눈  (YOLO)", "상자 = 동결 예측 그대로 · τ_conf 0.25", BOXCOL),
             ("본 접근의 눈  (칸 확률)", "20칸 확률 · 흰 실선 = 발화(p ≥ 0.5)", C["cor"])]
    for j, (t, s, col) in enumerate(heads):
        bb = pos(0, j)
        xc = (bb.x0 + bb.x1) / 2
        fig.text(xc, .7930, t, ha="center", va="bottom", fontsize=16.5,
                 fontweight="bold", color=col)
        fig.text(xc, .7815, s, ha="center", va="bottom", fontsize=9.6, color=C["mute"])

    # ---- 제목 --------------------------------------------------------------
    fig.text(.043, .991, "같은 프레임, 두 시스템의 눈", fontsize=27, fontweight="bold",
             color=C["ink"], ha="left", va="top")
    fig.text(.043, .9605,
             "검출기는 낙차의 몸체 픽셀이 있어야 상자를 그린다.  본 접근은 지면 격자 20칸에 "
             "확률을 내보낸다 — 몸체가 안 보여도 주변 단서로.",
             fontsize=13.2, color=C["mute"], ha="left", va="top")

    # ---- 상단 집계 표 ------------------------------------------------------
    XC = [.330, .490, .650, .818]
    ytab = .9330
    fig.text(.043, ytab, "프레임축 recall  (정답 칸과 정합된 검출만 성공)",
             fontsize=10.6, color=C["ink"], ha="left", va="top", fontweight="bold")
    for x, h in zip(XC, ["V  보임", "E  테두리만", "H  숨음", "off팔 FA"]):
        fig.text(x, ytab, h, fontsize=10.6, color=C["mute"], ha="center", va="top",
                 fontweight="bold")
    nV, nE, nH, nOFF = Y["_n"]
    for i, (lab, D, col, tau) in enumerate([
            ("검출기 YOLO  (3시드)", Y, BOXCOL, TAU_YOLO),
            ("본 접근 RGB  (3시드)", O, C["cor"], TAU_OURS)]):
        yy = .9120 - i * .0205
        fig.text(.043, yy, f"{lab}   τ_op {tau}", fontsize=10.8, color=col,
                 ha="left", va="top", fontweight="bold")
        for x, k in zip(XC, ("frame_recall_V", "frame_recall_E",
                             "frame_recall_H", "frame_fa_off")):
            m, hr, _ = D[k]
            zero = (m == 0.0 and k.startswith("frame_recall"))
            fig.text(x, yy, "0.000  (3시드 전부)" if zero else f"{m:.3f} ±{hr:.3f}",
                     fontsize=11.4 if zero else 10.8, ha="center", va="top",
                     color=C["bad"] if zero else C["ink"],
                     fontweight="bold" if zero or k == "frame_recall_H" else "normal")
    fig.text(.043, .8655,
             f"±는 3시드 반폭(half-range).  분모는 두 시스템이 동일 — test-core V {nV} · "
             f"E {nE} · H {nH} · off팔 {nOFF}장, 같은 정답지 세대.  "
             "recall 은 FA 동반 인쇄 (PREREG §6-5).",
             fontsize=9.5, color=C["mute"], ha="left", va="top")
    fig.text(.043, .8520,
             "검출기의 H·E 0.000 은 시드 3개 전부의 실측이다 — 문턱을 낮춰서 되는 문제가 아니라 "
             "그릴 픽셀이 없다는 뜻이다 (H 96장 중 상자가 하나라도 나온 18장도 정답 칸에는 "
             "단 하나도 정합되지 않았다).",
             fontsize=9.5, color=C["bad"], ha="left", va="top")

    # ---- 확률 램프 (범례 줄 오른쪽 끝 · 다른 아티스트와 겹치지 않는 자리) ----
    cax = fig.add_axes([.878, .8250, .110, .0080])
    cax.imshow(np.linspace(0, 1, 256).reshape(1, -1), aspect="auto", cmap=CMAP,
               extent=(0, 1, 0, 1))
    cax.set_yticks([]); cax.set_xticks([0, .5, 1])
    cax.set_xticklabels(["0", ".50", "1"], fontsize=7.4)
    cax.axvline(.5, color="white", lw=1.6)
    cax.tick_params(length=2, pad=1.2)
    for s in cax.spines.values():
        s.set_color(C["grid"])
    fig.text(.872, .8290, "칸 확률 램프  ·  흰 선 τ_op 0.5", ha="right", va="center",
             fontsize=8.4, color=C["mute"])

    # ---- 범례 --------------------------------------------------------------
    fig.legend(handles=[
        Line2D([], [], color=GTCOL, lw=2.2, ls=(0, (5, 3)), label="정답(GT) 칸의 지면 쐐기"),
        Line2D([], [], color=BOXCOL, lw=2.6, label="YOLO 동결 상자 (τ 0.25)"),
        Line2D([], [], color="white", lw=1.8, marker="s", ms=9,
               markerfacecolor=CMAP(.85), markeredgecolor="white",
               label="본 접근 발화 칸 (p ≥ 0.5)"),
        Line2D([], [], color="none", marker="s", ms=9, markerfacecolor=CMAP(.18),
               markeredgecolor="#BBBBBB", label="미발화 칸 (p < 0.5)")],
        loc="upper left", bbox_to_anchor=(.043, .8355), ncol=4, frameon=False,
        fontsize=9.6, handlelength=2.2, columnspacing=1.5)

    # ---- 하단 주석 띠 ------------------------------------------------------
    fig.add_artist(plt.Rectangle((.043, .0525), .945, .0625, transform=fig.transFigure,
                                 fc="#F3F5F8", ec=C["grid"], lw=1.2, zorder=0))
    fig.text(.5155, .0985,
             "보이는 낙차(V): 두 시스템 모두 잡는다   →   안 보이는 낙차(H): "
             "검출은 원리적으로 침묵(몸체 픽셀이 없다), 본 접근은 단서로 예고한다",
             ha="center", va="center", fontsize=14.6, fontweight="bold", color=C["ink"])
    fig.text(.5155, .0690,
             "YOLO 박스는 동결 예측(τ 0.25) 그대로 · 본 접근 τ_op 0.5 · "
             "recall 주장은 FA와 병기(본문 표 참조) · H에서 본 접근도 놓치는 프레임이 있다"
             "(전체 표가 정본)",
             ha="center", va="center", fontsize=11.0, color=C["bad"])

    # ---- 출처 푸터 ---------------------------------------------------------
    fids = "  ·  ".join(f"{r['tier']}행 {r['fid']}" for r in ROWS)
    footer(fig,
           "컷  " + fids + "\n"
           "원장  검출 상자 experiments/dayrun_0820/runs/yolo_s42/pred_test/labels/*.txt "
           "(class cx cy w h conf · 정규화 · 중복 줄 제거 · τ_conf 0.25)  ·  "
           "검출 집계 runs/yolo_s{42,43,44}/eval_test/metrics.json → point.op  ·  "
           "칸 확률 runs/v2/rgb_s42/eval_test/per_frame_on.csv (p_* · g_*)  ·  "
           "본 접근 집계 runs/v2/rgb_s{42,43,44}/eval_test/metrics.json → point.op\n"
           "층·카메라  experiments/v3_0823/dataset_manifest_v2corr.json (교정 GT · tier) + "
           "각 라운드 variation.json 의 cam(eye·yaw·pitch·roll·hfov·ground_z)  ·  "
           "격자 experiments/mainrun_0819/code/labeling/gridspec_v1.json "
           "(PROVISIONAL-GRID-V1 · 4밴드 × 5섹터 = 20칸)  ·  "
           "쐐기는 labeler.project 로 되투영 — 새 렌더·새 추론 0 · GPU 0\n"
           "세대 정합  오버레이·집계 모두 v2 세대(YOLO 베이스라인과 동일 세대·동일 "
           "test-core·동일 분모)로 통일했다. v3-A 덤프는 쓰지 않았다.  ·  "
           "H행 recall 0.688±0.141 은 eval_v2corr/rescore_tables.json 의 교정 GT 값과 "
           "완전 일치(H 층은 교정 대상 밖).  ·  " + DATE,
           y=.008)

    selfcheck(fig, tiles, cax)
    return save(fig, "panel_f_det_vs_ours.png", dpi=123)


def selfcheck(fig, tiles, cax):
    """저장 직전 기계 자기점검 — 빈 타일이 그림처럼 위장하는 사고를 막는다.

    12칸 전부에 (a) 분산 있는 실사 이미지, (b) 그 열이 요구하는 오버레이 아티스트가
    있어야 한다.  하나라도 어기면 저장하지 않고 죽는다.
    """
    from matplotlib.image import AxesImage
    if len(tiles) != 12:
        raise SystemExit(f"[fatal] 타일 {len(tiles)}개 != 12")
    if len(fig.axes) != 13:                 # 12 타일 + 램프 1
        raise SystemExit(f"[fatal] 축 {len(fig.axes)}개 != 13 — 빈 축이 타일을 덮었을 수 있다")
    if set(fig.axes) != set(a for _, _, a in tiles) | {cax}:
        raise SystemExit("[fatal] 정체 불명의 축이 그림에 있다")
    for k, j, ax in tiles:
        ims = [a for a in ax.get_children() if isinstance(a, AxesImage)]
        if len(ims) != 1:
            raise SystemExit(f"[fatal] 타일({k},{j}) 이미지 {len(ims)}장 != 1")
        arr = np.asarray(ims[0].get_array(), dtype=np.float64)
        if arr.shape[:2] != (IMH, IMW) or float(arr.std()) <= 1.0:
            raise SystemExit(f"[fatal] 타일({k},{j}) 이 비었다 "
                             f"(shape {arr.shape} std {float(arr.std()):.3f})")
        npoly = sum(isinstance(a, Polygon) for a in ax.get_children())
        nrect = sum(isinstance(a, Rectangle) and a.get_fill() is False
                    for a in ax.get_children())
        r = ROWS[k]
        need = {0: 3 * len(r["gt_cells"]),         # GT 칸마다 면+검정+초록 3장
                1: 2 * len(r["boxes"]),            # 상자마다 검정+주황 2장
                2: 2}[j]                           # 최소한 몇 칸은 그려진다
        got = nrect if j == 1 else npoly
        if got < need:
            raise SystemExit(f"[fatal] 타일({k},{j}) 오버레이 부족 {got} < {need}")
        if j == 1 and not r["boxes"] and nrect:
            raise SystemExit(f"[fatal] 타일({k},{j}) 상자 0개여야 하는데 {nrect}개 그렸다")
    print(f"[gate] 자기점검 통과 — 12/12 타일에 실사 이미지 + 열별 오버레이 존재 "
          f"(축 {len(fig.axes)}개 = 타일 12 + 램프 1)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    dst = os.path.join(OUT, "panel_f_det_vs_ours.png")
    if os.path.exists(dst) and not a.force:
        print(f"  이미 있음 (resume-safe): {dst}   — 다시 그리려면 --force")
        sys.exit(0)
    p, sz, dim = build()
    print(f"\n[done] {p}  {sz / 1024:.0f} KB  {dim[0]}×{dim[1]} px  "
          f"(2 MB 규율 {'통과' if sz <= 2_000_000 else '위반'})")
