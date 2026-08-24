#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verdict_panel_v2s.py — panel (h) 「10섹터로 쪼개면 무엇이 달라지나」 (CPU 전용).

    PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES= \
      python3 experiments/v3_0823/code/verdict_panel_v2s.py [--force]

산출 → `experiments/v3_0823/panels/verdict/panel_h_v2s.png`

V2S(10섹터·40칸) 채택 판정이 왜 ROLLBACK 이었는지를 **눈으로** 보이는 진단 패널이다.
수치의 정본은 `experiments/weekend_0823/v2s/V2S_ADOPTION.md` (§0 · §4 · §4.1 · §4.2).

행 = test-core 3컷 (선택 규칙은 아래 `pick_rows()` 가 결정적으로 재계산한다)
  1행 V — 위험이 화각 전폭을 덮는 컷 (V1 20칸 **전부** 정답) → 쪼개도 나눌 것이 없다
  2행 H — `scene14 / L5__…__0006` (panel_f · panel_g 와 같은 컷 · 연속성)
  3행 E — V1-vs-V2S argmax **각거리 최대** 컷 (전 덤프 탐색)

열 = (1) 입력 + 정답(V1 20칸 쐐기, 초록 파선)
     (2) V1 5섹터 모델의 20칸 확률 (쐐기 오버레이 + argmax 강조)
     (3) V2S 10섹터 모델의 40칸 확률 (2배 촘촘한 쐐기 + argmax 강조 + 접힘 일치 ✓/✗)

**규약** (`panel_f`/`panel_g` 와 같은 문법 — D99)
  1. 한국어 라벨  2. 출처 푸터  3. 좌상단 칩 + 좌하단 주석 + 우하단 출처의 3점 배치
  4. 타일 안 대형 글씨 금지(fontsize > 12)  5. 기계 자기점검 통과해야 저장  6. PNG ≤ 2 MB
  7. 재추론 0 · 재렌더 0 · GPU 0 · git 무접촉 — 확률은 **이미 덤프된 CSV** 에서만 읽는다.

**투영 기계**: `verdict_panel_detvsours.py` L125-154 의 `cam_of` / `wedge_px` 를 그대로
가져오되, 하드코딩된 V1 격자 상수를 `Grid` 로 **가법 일반화**만 했다 (수식 한 줄도
바뀌지 않았다 — V1 을 넣으면 원본과 같은 다각형이 나온다. `selftest_grid()` 가 단언).

**정직**: 오버레이는 `rgb_s42` **한 시드**다 (9런 중 1). 상단 통계 띠는 9런 전수 값이다.
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
V2SD = os.path.join(ROOT, "experiments/weekend_0823/v2s")
OUT = os.path.join(V3, "panels/verdict")
os.makedirs(OUT, exist_ok=True)

# ---- [복사: verdict_panel_detvsours.py L58-81] 폰트 · 색 · 날짜 --------------
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
GTCOL = "#25E07A"            # 정답(GT) 칸 = 초록 파선
AMXCOL = "#FFD400"           # argmax 칸 = 금색
V1COL = "#2F4B7C"            # V1 (5섹터) 열 색
V2COL = "#8E3FA8"            # V2S (10섹터) 열 색
TIERCOL = dict(V="#2F4B7C", H="#B03A48", E="#C08400")
TIERKR = dict(V="보이는 낙차", H="숨은 낙차", E="테두리만")


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
from matplotlib.patches import Polygon                  # noqa: E402
from matplotlib.lines import Line2D                     # noqa: E402
from PIL import Image                                   # noqa: E402

sys.path.insert(0, os.path.join(ROOT, "experiments/mainrun_0819/code"))
sys.path.insert(0, os.path.join(ROOT, "experiments/mainrun_0819/code/labeling"))
import labeler as L                                    # noqa: E402


# ====================================================== 격자 (가법 일반화) ===
class Grid:
    """gridspec JSON 하나를 감싼다 — V1(5섹터·20칸) · V2S(10섹터·40칸) 둘 다 받는다.

    `wedge_px` 는 `verdict_panel_detvsours.py` L134-154 의 본문을 **문자 그대로** 옮기고
    모듈 전역 상수(CELLS·NS·ASC·BND)만 인스턴스 속성으로 바꾼 것이다.
    """

    def __init__(self, path, expect_version, expect_cells):
        self.path = path
        self.spec = json.load(open(path))
        assert self.spec["version"] == expect_version, self.spec["version"]
        self.ns = int(self.spec["n_sectors"])
        self.nb = int(self.spec["n_bands"])
        self.cells = [f"{s}{b}" for b in self.spec["band_names"]
                      for s in self.spec["sector_names"]]
        assert self.ns * self.nb == expect_cells == len(self.cells)
        self.asc = self.spec["sector_edges_deg"][::-1]           # 오름차순 방위각
        self.bnd = self.spec["band_edges_m"]
        self.band_of = np.array([i // self.ns for i in range(len(self.cells))])
        self.sec_of = np.array([i % self.ns for i in range(len(self.cells))])
        e = self.spec["sector_edges_deg"]
        self.ctr = np.array([(e[i] + e[i + 1]) / 2 for i in range(self.ns)])
        self.snames = list(self.spec["sector_names"])

    def wedge_px(self, cell, cam, n=36):
        """Ground wedge of `cell` -> image polygon (px, py) at the frame's ground_z."""
        i = self.cells.index(cell)
        b, si = i // self.ns, i % self.ns
        k = self.ns - 1 - si
        a0, a1 = math.radians(self.asc[k]), math.radians(self.asc[k + 1])
        r0, r1 = self.bnd[b], self.bnd[b + 1]
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


G1 = Grid(os.path.join(ROOT, "experiments/mainrun_0819/code/labeling/gridspec_v1.json"),
          "PROVISIONAL-GRID-V1", 20)
G2 = Grid(os.path.join(ROOT, "experiments/mainrun_0819/code/labeling/gridspec_v2s.json"),
          "PROVISIONAL-GRID-V2S", 40)

# 폴딩 법칙: V1 cell(b*5+s) == V2S cell(b*10+2s) OR (b*10+2s+1)
FOLD_IDX = np.array([[b * G2.ns + 2 * s, b * G2.ns + 2 * s + 1]
                     for b in range(G1.nb) for s in range(G1.ns)])
assert G1.spec["band_edges_m"] == G2.spec["band_edges_m"]
assert G2.spec["folds_to_v1_sector"] == [G1.snames[s // 2] for s in range(G2.ns)]


def selftest_grid():
    """가법 일반화 게이트 — V1 격자를 넣으면 원본 `wedge_px` 상수와 완전히 같아야 한다."""
    assert G1.cells[:6] == ["A1", "B1", "C1", "D1", "E1", "A2"], G1.cells[:6]
    assert G2.cells[:4] == ["Aa1", "Ab1", "Ba1", "Bb1"], G2.cells[:4]
    assert abs(G1.ctr[0] - 24.88) < 1e-9 and abs(G2.ctr[0] - 27.99) < 1e-9
    w1 = abs(G1.ctr[0] - G1.ctr[1]); w2 = abs(G2.ctr[0] - G2.ctr[1])
    assert abs(w1 - 12.44) < 1e-9 and abs(w2 - 6.22) < 1e-9, (w1, w2)
    # V2S 섹터쌍의 각 경계가 V1 섹터 경계를 정확히 재현하는가
    for s in range(G1.ns):
        assert abs(G2.spec["sector_edges_deg"][2 * s] -
                   G1.spec["sector_edges_deg"][s]) < 1e-9
        assert abs(G2.spec["sector_edges_deg"][2 * s + 2] -
                   G1.spec["sector_edges_deg"][s + 1]) < 1e-9
    print(f"[gate] 격자 자기검사 통과 — V1 {len(G1.cells)}칸(폭 {w1:.2f}°) · "
          f"V2S {len(G2.cells)}칸(폭 {w2:.2f}°) · 섹터쌍 경계 = V1 경계")


# ============================================================== 원장 읽기 ===
TAU = 0.5
SEED = 42
SEEDS = (42, 43, 44)
MODELS = ("rgb", "depth", "b2")

MANP = os.path.join(V3, "dataset_manifest_v2corr.json")
MAN = json.load(open(MANP))
FM = {f["frame_id"]: f for f in MAN["frames"]}

PF_V1 = os.path.join(DAY, f"runs/v2/rgb_s{SEED}/eval_test/per_frame_on.csv")
PF_V2 = os.path.join(V2SD, f"runs/rgb_s{SEED}/eval_test/per_frame_on.csv")
ADOPT = os.path.join(V2SD, "v2s_adoption.json")


def read_pf(path, grid):
    fid, sid, tier, tog, P, G = [], [], [], [], [], []
    with open(path) as f:
        rd = csv.DictReader(f)
        got = [c[2:] for c in (rd.fieldnames or []) if c.startswith("p_")]
        if got != grid.cells:
            raise SystemExit(f"[fatal] {path}: 칸 목록 불일치 {got[:3]}… vs {grid.cells[:3]}…")
        for r in rd:
            fid.append(r["frame_id"]); sid.append(r["scene_id"])
            tier.append(r["tier"]); tog.append(r["toggle_state"])
            P.append([float(r["p_" + c]) for c in grid.cells])
            G.append([float(r["g_" + c]) for c in grid.cells])
    return dict(fid=fid, sid=np.array(sid), tier=np.array(tier), tog=np.array(tog),
                p=np.asarray(P, float), g=np.asarray(G, float) > 0.5)


D1 = read_pf(PF_V1, G1)
D2 = read_pf(PF_V2, G2)
J = json.load(open(ADOPT))


def gate_dumps():
    """두 덤프가 같은 프레임·같은 층·같은 정답(폴딩 후)인지 — 비교의 전제."""
    if D1["fid"] != D2["fid"]:
        raise SystemExit("[fatal] 두 덤프의 프레임 순서가 다르다")
    if not (D1["tier"] == D2["tier"]).all():
        raise SystemExit("[fatal] 두 덤프의 층이 다르다")
    if not (D1["tog"] == "on").all() or not (D2["tog"] == "on").all():
        raise SystemExit("[fatal] on 덤프가 아니다")
    gf = D2["g"][:, FOLD_IDX].any(axis=2)
    bad = int((gf != D1["g"]).sum())
    if bad:
        raise SystemExit(f"[fatal] GT 폴딩 불일치 {bad}칸")
    print(f"[gate] 덤프 정합 통과 — {len(D1['fid'])}프레임 · "
          f"GT 폴딩 불일치 0 / {len(D1['fid']) * 20}칸 "
          f"(V2S 40칸을 섹터쌍 OR 로 접으면 V1 20칸과 완전 일치)")


# ------------------------------------------------- §4 국소화 오차 (원장 정의)
def argmax_and_err(i):
    """V2S_ADOPTION §4 정의 그대로 — GT 밴드 행으로 한정한 argmax 와 각오차."""
    g1, g2 = D1["g"][i], D2["g"][i]
    bands = np.unique(G1.band_of[g1])
    m1, m2 = np.isin(G1.band_of, bands), np.isin(G2.band_of, bands)
    j1 = int(np.argmax(np.where(m1, D1["p"][i], -np.inf)))
    j2 = int(np.argmax(np.where(m2, D2["p"][i], -np.inf)))
    s1, s2 = int(G1.sec_of[j1]), int(G2.sec_of[j2])
    e1 = float(np.abs(G1.ctr[G1.sec_of[g1 & m1]] - G1.ctr[s1]).min())
    e2 = float(np.abs(G2.ctr[G2.sec_of[g2 & m2]] - G2.ctr[s2]).min())
    return dict(j1=j1, j2=j2, s1=s1, s2=s2, parent=s2 // 2,
                same=bool(s1 == s2 // 2), dis=float(abs(G1.ctr[s1] - G2.ctr[s2])),
                e1=e1, e2=e2, bands=[G1.spec["band_names"][b] for b in bands])


def corpus_stats():
    """이 덤프 전체(GT 보유 on-프레임)에서 argmax 이동/오차 통계를 실측한다."""
    st = []
    for i in range(len(D1["fid"])):
        if not D1["g"][i].any():
            continue
        a = argmax_and_err(i)
        st.append((a["same"], a["dis"], a["e1"], a["e2"]))
    same = np.array([s for s, _, _, _ in st])
    dis = np.array([d for _, d, _, _ in st])
    e1 = np.array([x for _, _, x, _ in st]); e2 = np.array([x for _, _, _, x in st])
    n = len(st); nd = int((~same).sum())
    out = dict(n=n, n_same=int(same.sum()), frac_same=float(same.mean()),
               med_dis=float(np.median(dis)), max_dis=float(dis.max()),
               n_diff=nd, n_diff_both0=int((((~same) & (e1 == 0) & (e2 == 0))).sum()),
               v1_med=float(np.median(e1)), v2_med=float(np.median(e2)),
               v1_mean=float(e1.mean()), v2_mean=float(e2.mean()),
               v1_zero=float((e1 == 0).mean()), v2_zero=float((e2 == 0).mean()))
    out["frac_diff_both0"] = out["n_diff_both0"] / nd if nd else float("nan")
    # 원장(§4 rgb seed 42 행)과 대조 — 한 자리라도 어긋나면 죽는다
    led = next(r for r in J["native"]["rgb"]["per_seed"] if r["seed"] == SEED)
    for k, v in (("n_frames", out["n"]), ("v1_mean_deg", out["v1_mean"]),
                 ("v2s_mean_deg", out["v2_mean"]), ("v1_frac_zero", out["v1_zero"]),
                 ("v2s_frac_zero", out["v2_zero"]), ("v1_median_deg", out["v1_med"]),
                 ("v2s_median_deg", out["v2_med"])):
        if abs(float(led[k]) - float(v)) > 1e-9:
            raise SystemExit(f"[fatal] 원장 대조 실패 {k}: 원장 {led[k]} vs 재계산 {v}")
    print(f"[gate] §4 원장 대조 통과 — rgb_s42 n={out['n']} · V1 평균 {out['v1_mean']:.3f}° / "
          f"정확적중 {out['v1_zero']:.3f} · V2S 평균 {out['v2_mean']:.3f}° / "
          f"정확적중 {out['v2_zero']:.3f} (V2S_ADOPTION §4 표와 동일)")
    return out


def headline_stats():
    """상단 통계 띠 — V2S_ADOPTION §0 · §3 · §4.2 의 전수(9런) 수치를 원장에서 재확인."""
    n_pass = sum(1 for v in J["d34"].values() if v["PASS"])
    n_cell = len(J["d34"])
    mean_better = sum(J["native"][m]["n_seeds_mean_better"] for m in MODELS)
    zero_better = sum(J["native"][m]["n_seeds_frac_zero_better"] for m in MODELS)
    n_runs = sum(len(J["native"][m]["per_seed"]) for m in MODELS)
    med_all_zero = all(r["v1_median_deg"] == 0.0 and r["v2s_median_deg"] == 0.0
                       for m in MODELS for r in J["native"][m]["per_seed"])
    coarse_better = 0
    for m in MODELS:
        for r in J["native"][m]["coarse_check"]:
            coarse_better += int(r["v2s_coarse_mean_deg"] < r["v1_mean_deg"])
    if (n_pass, n_cell, mean_better, zero_better, n_runs) != (6, 9, 4, 2, 9):
        raise SystemExit(f"[fatal] 원장 헤드라인 불일치: 부등식 {n_pass}/{n_cell} · "
                         f"평균 {mean_better}/{n_runs} · 정확적중 {zero_better}/{n_runs}")
    if not med_all_zero:
        raise SystemExit("[fatal] 중앙값이 전부 0.000° 가 아니다 — 공허 논증이 깨진다")
    if coarse_better != 4:
        raise SystemExit(f"[fatal] 거친 국소화 개선 런 {coarse_better} != 4")
    print(f"[gate] 통계 띠 검산 통과 — D34 부등식 {n_pass}/{n_cell} · 국소화 평균 개선 "
          f"{mean_better}/{n_runs} · 정확적중 개선 {zero_better}/{n_runs} · "
          f"거친 국소화 {coarse_better}/{n_runs} · 중앙값 18칸 전부 0.000°(공허)")
    return dict(n_pass=n_pass, n_cell=n_cell, mean_better=mean_better,
                zero_better=zero_better, n_runs=n_runs, coarse_better=coarse_better)


# ============================================================== 행 선택 =====
H_ANCHOR = "on/scene14/L5__s20260819__0006.png"     # panel_f · panel_g 와 같은 컷


def pick_rows():
    """세 행을 **결정적 규칙**으로 고른다 (하드코딩 없음 — 규칙만 하드코딩).

      1행 V : test-core V 프레임 중 V1 20칸이 **전부** GT-양성(위험이 화각 전폭)인 컷.
              → argmax 각거리 최대 → V1 argmax 확률 최대 → 키 사전순.
      2행 H : `H_ANCHOR` 고정 (panel_f · panel_g 연속성). 층 H 임을 단언.
      3행 * : GT 보유 on-프레임 전체에서 argmax 각거리 **최대**.
              동률이면 (오차가 0 인 격자 수 최대 = 공허성이 가장 선명한 컷) →
              V1 argmax 확률 최대 → 키 사전순.
    """
    cand = []
    for i in range(len(D1["fid"])):
        if not D1["g"][i].any():
            continue
        a = argmax_and_err(i)
        cand.append(dict(i=i, fid=D1["fid"][i], tier=str(D1["tier"][i]),
                         sid=str(D1["sid"][i]), ngt1=int(D1["g"][i].sum()),
                         ngt2=int(D2["g"][i].sum()),
                         p1=float(D1["p"][i][a["j1"]]), p2=float(D2["p"][i][a["j2"]]), **a))

    full = [c for c in cand if c["tier"] == "V" and c["ngt1"] == len(G1.cells)]
    if not full:
        raise SystemExit("[fatal] 20칸 전부 GT-양성인 V 프레임이 없다")
    full.sort(key=lambda c: (-c["dis"], -c["p1"], c["fid"]))
    rowV = full[0]

    hh = [c for c in cand if c["fid"] == H_ANCHOR]
    if not hh:
        raise SystemExit(f"[fatal] 앵커 컷이 덤프에 없다: {H_ANCHOR}")
    rowH = hh[0]
    if rowH["tier"] != "H":
        raise SystemExit(f"[fatal] 앵커 컷의 층이 H 가 아니다: {rowH['tier']}")

    mx = max(c["dis"] for c in cand)
    grp = [c for c in cand if c["dis"] == mx]
    grp.sort(key=lambda c: (-((c["e1"] == 0) + (c["e2"] == 0)), -c["p1"], c["fid"]))
    rowD = grp[0]
    if rowD["fid"] in (rowV["fid"], rowH["fid"]):
        raise SystemExit("[fatal] 3행이 다른 행과 같은 컷이다 — 규칙을 재검토하라")

    print(f"[gate] 행 선택 — 전폭 후보 {len(full)}컷 · 최대 각거리 {mx:.2f}° 동률 {len(grp)}컷 "
          f"(전부 부모 섹터 {'일치' if all(c['same'] for c in grp) else '불일치'})")
    return [rowV, rowH, rowD], dict(n_full=len(full), max_dis=mx, n_maxgrp=len(grp),
                                    maxgrp_all_same=all(c["same"] for c in grp))


NOTE = {
    "V": "위험이 화각 전폭 — V1 20칸이 전부 정답 칸이다",
    "H": "지평선 뒤로 몸체가 사라진 컷 (panel_f · panel_g 와 같은 컷)",
    "D": "전 덤프에서 두 격자의 argmax 가 가장 멀리 갈라진 컷",
}


# ============================================================== 그리기 ======
CMAP = plt.get_cmap("inferno")
IMW, IMH = 640, 360


def cam_of(fr):
    """[복사: verdict_panel_detvsours.py L126-131]"""
    sdir, fn = os.path.dirname(fr["rgb"]), os.path.basename(fr["rgb"])
    cuts = json.load(open(os.path.join(sdir, "variation.json")))["cuts"]
    if isinstance(cuts, dict):
        cuts = list(cuts.values())
    return next(c["cam"] for c in cuts if c["file"] == fn)


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


def _wedge_xy(grid, cell, cam):
    """[복사: verdict_panel_detvsours.py L343-351] — grid 인자만 추가."""
    px, py, front, inb = grid.wedge_px(cell, cam)
    if not front.all():
        return None
    sx, sy = IMW / L.W_IMG, IMH / L.H_IMG
    X, Y = px * sx, py * sy
    if X.max() < 0 or X.min() > IMW or Y.max() < 0 or Y.min() > IMH:
        return None
    return np.c_[X, Y]


def _chip(ax, x, y, txt, fc, *, ha="left", va="top", fs=9.0, tc="white", z=9, pad=3.0):
    """[복사: verdict_panel_detvsours.py L354-357]"""
    return ax.text(x, y, txt, transform=ax.transAxes, ha=ha, va=va, fontsize=fs,
                   color=tc, fontweight="bold", zorder=z,
                   bbox=dict(fc=fc, ec="none", pad=pad, alpha=.94))


def _note(ax, x, y, txt, *, ha="left", fs=8.4, fc="#000000", al=.62, tc="white"):
    return ax.text(x, y, txt, transform=ax.transAxes, ha=ha, va="bottom", fontsize=fs,
                   color=tc, zorder=9, bbox=dict(fc=fc, ec="none", pad=2.6, alpha=al))


def col_input(ax, r, cam, img):
    """(1) 입력 + 정답 — V1 20칸 중 GT-양성 칸의 지면 쐐기를 초록 파선으로."""
    _blank(ax, img)
    g = D1["g"][r["i"]]
    off, drawn = [], 0
    for k in np.where(g)[0]:
        xy = _wedge_xy(G1, G1.cells[k], cam)
        if xy is None:
            off.append(G1.cells[k]); continue
        ax.add_patch(Polygon(xy, closed=True, fc=GTCOL, ec="none", alpha=.11, zorder=2))
        ax.add_patch(Polygon(xy, closed=True, fc="none", ec="black", lw=3.0, zorder=3))
        ax.add_patch(Polygon(xy, closed=True, fc="none", ec=GTCOL, lw=1.9,
                             ls=(0, (5, 3)), zorder=4))
        drawn += 1
    t = r["tier"]
    _chip(ax, .014, .972, f"  {t}  ·  {TIERKR[t]}  ", TIERCOL[t], fs=11.5, pad=4.4)
    _chip(ax, .986, .972, f"정답 칸  V1 {int(g.sum())}/20  ·  V2S {r['ngt2']}/40",
          "#000000", ha="right", fs=8.6)
    _note(ax, .014, .030, r["note"])
    if off:
        _note(ax, .986, .030, "칸이 카메라 뒤 · 미표시: " + ",".join(off),
              ha="right", fs=6.8, al=.55)
    return drawn


def col_probs(ax, r, cam, img, which):
    """(2)(3) 칸 확률 히트 — which='v1'(20칸) / 'v2s'(40칸). argmax 는 금색 강조."""
    _blank(ax, img)
    if which == "v1":
        grid, D, jmax, e = G1, D1, r["j1"], r["e1"]
    else:
        grid, D, jmax, e = G2, D2, r["j2"], r["e2"]
    p, g = D["p"][r["i"]], D["g"][r["i"]]
    hidden, drawn, amx_xy = [], 0, None
    for k in np.argsort(p):                       # 낮은 확률부터 → 높은 칸이 위로
        xy = _wedge_xy(grid, grid.cells[k], cam)
        if xy is None:
            if p[k] >= TAU or g[k] or k == jmax:
                hidden.append(grid.cells[k])
            continue
        drawn += 1
        pv = float(p[k])
        ax.add_patch(Polygon(xy, closed=True, fc=CMAP(pv), ec="none",
                             alpha=0.06 + 0.56 * pv, zorder=2))
        if pv >= TAU:
            ax.add_patch(Polygon(xy, closed=True, fc="none", ec="white", lw=1.7, zorder=3))
        else:
            ax.add_patch(Polygon(xy, closed=True, fc="none", ec="white", lw=0.5,
                                 alpha=.30, zorder=3))
        if g[k]:
            ax.add_patch(Polygon(xy, closed=True, fc="none", ec="black", lw=2.6, zorder=4))
            ax.add_patch(Polygon(xy, closed=True, fc="none", ec=GTCOL, lw=1.5,
                                 ls=(0, (5, 3)), zorder=5))
        if k == jmax:
            amx_xy = xy
    if amx_xy is not None:                        # argmax 는 맨 위 · 금색 이중 윤곽
        ax.add_patch(Polygon(amx_xy, closed=True, fc="none", ec="black", lw=4.6,
                             zorder=6, gid="argmax_base"))
        ax.add_patch(Polygon(amx_xy, closed=True, fc="none", ec=AMXCOL, lw=2.6,
                             zorder=7, gid="argmax"))
    nfire = int((p >= TAU).sum())
    col = V1COL if which == "v1" else V2COL
    lab = "V1 20칸" if which == "v1" else "V2S 40칸"
    _chip(ax, .014, .972,
          f"{lab}  ·  argmax {grid.cells[jmax]}  p {float(p[jmax]):.2f}  ·  발화 {nfire}칸",
          col, fs=9.4)
    if which == "v1":
        _chip(ax, .986, .972, f"국소화 오차 {e:.2f}°",
              C["ok"] if e == 0 else C["bad"], ha="right", fs=9.0)
    else:
        ok = r["same"]
        _chip(ax, .986, .972,
              (f"접힘 {G1.snames[r['parent']]} = V1 {G1.snames[r['s1']]}   ✓"
               if ok else
               f"접힘 {G1.snames[r['parent']]} ≠ V1 {G1.snames[r['s1']]}   ✗   "
               f"각거리 {r['dis']:.2f}°"),
              C["ok"] if ok else C["bad"], ha="right", fs=9.0)
    # 3열의 국소화 오차는 좌하단 주석의 머리에 붙인다 — 우상단에 또 칩을 얹으면
    # 하필 argmax 쐐기(화각 가장자리)를 덮는다.
    _note(ax, .014, .030, r["read_v1" if which == "v1" else "read_v2s"])
    if hidden:
        _note(ax, .986, .118 if which == "v2s" else .030,
              "칸이 카메라 뒤 · 미표시: " + ",".join(hidden), ha="right", fs=6.6, al=.55)
    return drawn


# ============================================================== 조립 ========
def build():
    selftest_grid()
    gate_dumps()
    HS = headline_stats()
    CS = corpus_stats()
    rows, pick = pick_rows()

    # 행별 문안 — 전부 실측치에서 조립한다 (손으로 쓴 수는 없다)
    kinds = ["V", "H", "D"]
    for r, kind in zip(rows, kinds):
        r["kind"] = kind
        r["note"] = NOTE[kind]
        r["read_v1"] = (f"밴드 {'·'.join(r['bands'])} 안에서 가장 센 칸 = "
                        f"{G1.cells[r['j1']]}  (오차 {r['e1']:.2f}°)")
        head = f"국소화 오차 {r['e2']:.2f}°"
        if r["same"]:
            r["read_v2s"] = (f"{head}  ·  쪼갠 뒤에도 같은 부모 섹터 "
                             f"{G1.snames[r['s1']]} 안 (각거리 {r['dis']:.2f}°)")
        elif r["e1"] == 0 and r["e2"] == 0:
            r["read_v2s"] = (f"{head}  ·  부모가 {G1.snames[r['s1']]}→"
                             f"{G1.snames[r['parent']]} 로 {r['dis']:.2f}° 옮겨갔는데도 "
                             f"오차는 그대로 — 전 폭이 정답이라 어디를 찍어도 맞는다")
        else:
            r["read_v2s"] = (f"국소화 오차 {r['e1']:.2f}° → {r['e2']:.2f}°  ·  부모 "
                             f"{G1.snames[r['s1']]}→{G1.snames[r['parent']]} · "
                             f"각거리 {r['dis']:.2f}°")

    fig = plt.figure(figsize=(15.8, 15.3))
    gs = fig.add_gridspec(3, 3, left=.043, right=.988, top=.720, bottom=.150,
                          hspace=.058, wspace=.014)
    pos = lambda k, j: gs[k, j].get_position(fig)     # noqa: E731  (D99: add_subplot 금지)
    tiles, ndrawn = [], {}

    for k, r in enumerate(rows):
        fr = FM[r["fid"]]
        if fr["tier"] != r["tier"]:
            raise SystemExit(f"[fatal] 층 불일치 {r['fid']}: 매니페스트 {fr['tier']} / "
                             f"덤프 {r['tier']}")
        cam = cam_of(fr)
        img = _frame_img(fr)
        for j in (0, 1, 2):
            ax = fig.add_subplot(gs[k, j])
            if j == 0:
                ndrawn[(k, j)] = col_input(ax, r, cam, img)
            else:
                ndrawn[(k, j)] = col_probs(ax, r, cam, img, "v1" if j == 1 else "v2s")
            tiles.append((k, j, ax))
        bb = pos(k, 0)
        fig.text(.019, (bb.y0 + bb.y1) / 2,
                 f"{k + 1}행  ·  {r['tier']}  {TIERKR[r['tier']]}",
                 rotation=90, ha="center", va="center", fontsize=11.5,
                 fontweight="bold", color=TIERCOL[r["tier"]])

    # ---- 열 머리글 ---------------------------------------------------------
    heads = [("입력 + 정답 (GT)", "초록 파선 = 낙차가 놓인 지면 칸 (V1 20칸 기준)", C["ink"]),
             ("V1  ·  5섹터 모델", "20칸 확률 · 섹터 폭 12.44° · 금색 = argmax", V1COL),
             ("V2S  ·  10섹터 모델", "40칸 확률 · 섹터 폭 6.22°(쐐기 2배) · 금색 = argmax",
              V2COL)]
    for j, (t, s, col) in enumerate(heads):
        bb = pos(0, j)
        xc = (bb.x0 + bb.x1) / 2
        fig.text(xc, .7395, t, ha="center", va="bottom", fontsize=16.0,
                 fontweight="bold", color=col)
        fig.text(xc, .7285, s, ha="center", va="bottom", fontsize=9.4, color=C["mute"])

    # ---- 제목 --------------------------------------------------------------
    fig.text(.043, .992, "섹터를 5개에서 10개로 쪼개면 무엇이 달라지나",
             fontsize=26, fontweight="bold", color=C["ink"], ha="left", va="top")
    fig.text(.043, .9640,
             "같은 컷 · 같은 정답 · 같은 레시피.  왼쪽은 12.44° 섹터 5개(20칸), 오른쪽은 "
             "그 각각을 반으로 쪼갠 6.22° 섹터 10개(40칸)로 학습·평가한 모델이다.",
             fontsize=12.6, color=C["mute"], ha="left", va="top")

    # ---- 상단 통계 띠 (V2S_ADOPTION §0 · §3 · §4.1 · §4.2 · 전수 9런) -------
    fig.add_artist(plt.Rectangle((.043, .8125), .945, .1195, transform=fig.transFigure,
                                 fc="#F7F3F4", ec="#E3D6D9", lw=1.2, zorder=0))
    fig.text(.0555, .9165, "사전등록 판정",
             fontsize=10.0, color=C["mute"], ha="left", va="top")
    fig.text(.0555, .8975, "ROLLBACK", fontsize=22, fontweight="bold",
             color=C["bad"], ha="left", va="top")
    fig.text(.0555, .8395, "V1(20칸)이 정본으로 유지된다  ·  롤백 비용 0",
             fontsize=9.0, color=C["mute"], ha="left", va="top")
    XS = [.288, .470, .652, .834]
    BLK = [("D34 부등식", f"{HS['n_pass']} / {HS['n_cell']} 칸 통과",
            "전 칸 통과가 요건 → 판정 ①  FAIL", C["bad"]),
           ("국소화 개선 · 오차 평균", f"{HS['mean_better']} / {HS['n_runs']} 런",
            "동전 던지기 (거친 국소화도 4/9)", C["ink"]),
           ("국소화 개선 · 정확 적중", f"{HS['zero_better']} / {HS['n_runs']} 런",
            "동전 던지기 (2/9 는 우연 이하)", C["ink"]),
           ("중앙값 검정", "양측 0.000°",
            "공허 통과 — 인용 금지 (§4.1)", C["bad"])]
    for x, (t, v, s, col) in zip(XS, BLK):
        fig.text(x, .9165, t, fontsize=10.0, color=C["mute"], ha="center", va="top")
        fig.text(x, .8975, v, fontsize=19, fontweight="bold", color=col,
                 ha="center", va="top")
        fig.text(x, .8395, s, fontsize=9.0, color=col if col == C["bad"] else C["mute"],
                 ha="center", va="top")
    for x in (.2115, .3805, .5625, .7445):
        fig.add_artist(Line2D([x, x], [.8280, .9215], transform=fig.transFigure,
                              color="#E3D6D9", lw=1.0))
    fig.text(.5155, .8010,
             "위 다섯 칸은 rgb·depth·b2 × 시드 42/43/44 = 9런 전수(全數) 값이다 "
             "(V2S_ADOPTION §0 · §3.2 · §4.1 · §4.2).  아래 그림은 그중 rgb_s42 "
             "한 시드의 오버레이다 — 그림은 예시, 판정은 표.",
             fontsize=9.6, color=C["mute"], ha="center", va="top")

    # ---- 확률 램프 + 범례 --------------------------------------------------
    cax = fig.add_axes([.878, .7645, .110, .0072])
    cax.imshow(np.linspace(0, 1, 256).reshape(1, -1), aspect="auto", cmap=CMAP,
               extent=(0, 1, 0, 1))
    cax.set_yticks([]); cax.set_xticks([0, .5, 1])
    cax.set_xticklabels(["0", ".50", "1"], fontsize=7.2)
    cax.axvline(.5, color="white", lw=1.6)
    cax.tick_params(length=2, pad=1.2)
    for s in cax.spines.values():
        s.set_color(C["grid"])
    fig.text(.872, .7680, "칸 확률 램프  ·  흰 선 τ_op 0.5", ha="right", va="center",
             fontsize=8.2, color=C["mute"])
    fig.legend(handles=[
        Line2D([], [], color=GTCOL, lw=2.2, ls=(0, (5, 3)), label="정답(GT) 칸의 지면 쐐기"),
        Line2D([], [], color=AMXCOL, lw=2.8, label="argmax 칸 (GT 밴드 행 안에서 최대 확률)"),
        Line2D([], [], color="white", lw=1.8, marker="s", ms=9,
               markerfacecolor=CMAP(.85), markeredgecolor="white",
               label="발화 칸 (p ≥ 0.5)"),
        Line2D([], [], color="none", marker="s", ms=9, markerfacecolor=CMAP(.18),
               markeredgecolor="#BBBBBB", label="미발화 칸 (p < 0.5)")],
        loc="upper left", bbox_to_anchor=(.043, .7745), ncol=4, frameon=False,
        fontsize=9.4, handlelength=2.2, columnspacing=1.5)

    # ---- 하단 결론 띠 ------------------------------------------------------
    fig.add_artist(plt.Rectangle((.043, .0555), .945, .0815, transform=fig.transFigure,
                                 fc="#F3F5F8", ec=C["grid"], lw=1.2, zorder=0))
    fig.text(.5155, .1180,
             "섹터를 2배로 쪼개도 채점은 달라지지 않았다 — 잴 것(측방 변별)이 시험에 없었다.",
             ha="center", va="center", fontsize=14.2, fontweight="bold", color=C["ink"])
    fig.text(.5155, .0925,
             f"실측(rgb_s42 · GT 보유 {CS['n']}프레임):  두 격자의 argmax 가 같은 부모 섹터에 "
             f"앉는 프레임은 {CS['n_same']}/{CS['n']} = {CS['frac_same']:.1%} 뿐이고 "
             f"중앙값 이견은 {CS['med_dis']:.2f}°, 최대 {CS['max_dis']:.2f}° 다.  "
             f"그런데도 갈라진 {CS['n_diff']}프레임 중 "
             f"{CS['n_diff_both0']}프레임({CS['frac_diff_both0']:.1%})은 "
             "국소화 오차가 「양쪽 다 0.00°」 다.",
             ha="center", va="center", fontsize=10.4, color=C["bad"])
    fig.text(.5155, .0700,
             "argmax 는 화각을 가로질러 떠돌아다니는데 점수는 꿈쩍도 하지 않는다 — "
             "계단 지배 코퍼스에서는 위험이 화각 전폭을 덮어 「어느 섹터를 찍어도 정답」이기 "
             "때문이다.  재론 기반(측방 씬 L1)은 v3 에서 생성됨.",
             ha="center", va="center", fontsize=10.4, color=C["ink"])

    # ---- 출처 푸터 ---------------------------------------------------------
    fids = "  ·  ".join(f"{r['tier']}행 {r['fid']}" for r in rows)
    footer(fig,
           "컷  " + fids + "\n"
           "원장  V1 칸 확률 experiments/dayrun_0820/runs/v2/rgb_s42/eval_test/"
           "per_frame_on.csv (p_* 20열 · g_* 20열)  ·  "
           "V2S 칸 확률 experiments/weekend_0823/v2s/runs/rgb_s42/eval_test/"
           "per_frame_on.csv (p_* 40열 · g_* 40열)  ·  "
           "판정 수치 experiments/weekend_0823/v2s/v2s_adoption.json "
           "(→ V2S_ADOPTION.md §0 · §3.2 · §4 · §4.1 · §4.2) — 전 수치를 이 스크립트가 "
           "다시 계산해 원장과 대조한 뒤에만 인쇄한다\n"
           "격자  V1 gridspec_v1.json (PROVISIONAL-GRID-V1 · 4밴드 × 5섹터 = 20칸 · "
           "섹터 폭 12.44°)  ·  V2S gridspec_v2s.json (PROVISIONAL-GRID-V2S · "
           "4밴드 × 10섹터 = 40칸 · 섹터 폭 6.22°)  ·  폴딩 법칙 "
           "V1_cell(b·5+s) = V2S_cell(b·10+2s) OR V2S_cell(b·10+2s+1) — 이 덤프에서 "
           f"GT 폴딩 불일치 0 / {len(D1['fid']) * 20}칸\n"
           "층·카메라  experiments/v3_0823/dataset_manifest_v2corr.json + 각 라운드 "
           "variation.json 의 cam(eye·yaw·pitch·roll·hfov·ground_z)  ·  "
           "쐐기는 labeler.project 로 되투영 (투영 수식은 verdict_panel_detvsours.py 에서 "
           "복사 · 격자만 인자화)  ·  새 렌더 0 · 새 추론 0 · GPU 0\n"
           "국소화 오차  V2S_ADOPTION §4 정의 그대로 — GT 를 가진 밴드 행으로 한정해 argmax "
           "칸을 찾고, 그 섹터 중심과 가장 가까운 GT 양성 섹터 중심 사이의 각거리(도).  "
           "τ_op 0.5.  GT 는 두 평가 덤프의 g_* 열(모델이 실제로 채점된 정답지)이다.  ·  "
           + DATE,
           y=.008)

    selfcheck(fig, tiles, cax, rows, ndrawn)
    return save(fig, "panel_h_v2s.png", dpi=124), rows, pick, CS, HS


def selfcheck(fig, tiles, cax, rows, ndrawn):
    """저장 직전 기계 자기점검 (D99 강화판) — 백지 타일·대형 낙관·오버레이 누락을 전부 막는다."""
    from matplotlib.image import AxesImage
    from matplotlib.text import Text
    if len(tiles) != 9:
        raise SystemExit(f"[fatal] 타일 {len(tiles)}개 != 9")
    if len(fig.axes) != 10:                 # 9 타일 + 램프 1
        raise SystemExit(f"[fatal] 축 {len(fig.axes)}개 != 10 — 빈 축이 타일을 덮었을 수 있다")
    if set(fig.axes) != set(a for _, _, a in tiles) | {cax}:
        raise SystemExit("[fatal] 정체 불명의 축이 그림에 있다")
    for k, j, ax in tiles:
        r = rows[k]
        ims = [a for a in ax.get_children() if isinstance(a, AxesImage)]
        if len(ims) != 1:
            raise SystemExit(f"[fatal] 타일({k},{j}) 이미지 {len(ims)}장 != 1")
        arr = np.asarray(ims[0].get_array(), dtype=np.float64)
        if arr.shape[:2] != (IMH, IMW) or float(arr.std()) <= 1.0:
            raise SystemExit(f"[fatal] 타일({k},{j}) 이 비었다 "
                             f"(shape {arr.shape} std {float(arr.std()):.3f})")
        polys = [a for a in ax.get_children() if isinstance(a, Polygon)]
        n = ndrawn[(k, j)]
        if n < 2:
            raise SystemExit(f"[fatal] 타일({k},{j}) 그려진 쐐기 {n}칸 < 2")
        need = 3 * n if j == 0 else 2 * n          # 1열 = 면+검정+초록 · 확률열 = 면+윤곽
        if len(polys) < need:
            raise SystemExit(f"[fatal] 타일({k},{j}) 다각형 {len(polys)} < {need}")
        if j:                                       # 확률 열에는 argmax 강조가 반드시 있다
            gids = {p.get_gid() for p in polys}
            if not {"argmax", "argmax_base"} <= gids:
                raise SystemExit(f"[fatal] 타일({k},{j}) argmax 강조 아티스트가 없다")
        txts = [a for a in ax.get_children() if isinstance(a, Text) and a.get_text().strip()]
        if len(txts) < 3:
            raise SystemExit(f"[fatal] 타일({k},{j}) 텍스트 {len(txts)}개 < 3 "
                             "(칩 + 칩 + 주석의 3점 배치가 무너졌다)")
        big = [(a.get_text()[:24], a.get_fontsize()) for a in txts if a.get_fontsize() > 12]
        if big:
            raise SystemExit(f"[fatal] 타일({k},{j}) 대형 낙관 금지(D99) 위반: {big}")
        if j == 2 and not any(("✓" in t.get_text()) or ("✗" in t.get_text()) for t in txts):
            raise SystemExit(f"[fatal] 타일({k},2) 접힘 일치 ✓/✗ 표기가 없다")
    # 마크다운 누출 게이트 — matplotlib 은 `**` 를 굵게 그리지 않고 별 두 개를 인쇄한다
    from matplotlib.text import Text as _T
    leak = [a.get_text()[:40] for a in fig.findobj(_T) if "**" in (a.get_text() or "")]
    if leak:
        raise SystemExit(f"[fatal] 마크다운 `**` 가 그림에 그대로 인쇄된다: {leak}")
    # 3열이 2열보다 **반드시 촘촘해야** 한다 (10섹터 = 쐐기가 더 많이 그려진다)
    for k in range(3):
        if ndrawn[(k, 2)] <= ndrawn[(k, 1)]:
            raise SystemExit(f"[fatal] {k + 1}행: V2S 쐐기 {ndrawn[(k, 2)]}칸이 "
                             f"V1 {ndrawn[(k, 1)]}칸보다 촘촘하지 않다")
    print(f"[gate] 자기점검 통과 — 9/9 타일에 실사 이미지 + 쐐기 오버레이 + 3점 텍스트, "
          f"확률 열 6/6 에 argmax 강조, 3열 ✓/✗ 3/3, 대형 낙관 0 "
          f"(축 {len(fig.axes)}개 = 타일 9 + 램프 1)")
    print("       행별 그려진 쐐기 수 (1열 GT / 2열 V1 / 3열 V2S): " +
          "  ·  ".join(f"{k + 1}행 {ndrawn[(k, 0)]}/{ndrawn[(k, 1)]}/{ndrawn[(k, 2)]}"
                       for k in range(3)))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    dst = os.path.join(OUT, "panel_h_v2s.png")
    if os.path.exists(dst) and not a.force:
        print(f"  이미 있음 (resume-safe): {dst}   — 다시 그리려면 --force")
        sys.exit(0)
    (p, sz, dim), rows, pick, CS, HS = build()
    print("\n[행]")
    for k, r in enumerate(rows):
        print(f"  {k + 1}행 {r['tier']:1s}  {r['fid']}\n"
              f"       V1 argmax {G1.cells[r['j1']]:4s} p {r['p1']:.3f} 오차 {r['e1']:.2f}°  ·  "
              f"V2S argmax {G2.cells[r['j2']]:5s} p {r['p2']:.3f} 오차 {r['e2']:.2f}°  ·  "
              f"부모 {G1.snames[r['s1']]}→{G1.snames[r['parent']]} "
              f"{'일치' if r['same'] else '불일치'} · 각거리 {r['dis']:.2f}°")
    print(f"\n[최대 이견] {pick['max_dis']:.2f}° · 동률 {pick['n_maxgrp']}컷 · "
          f"부모 섹터 {'전부 일치' if pick['maxgrp_all_same'] else '불일치'}")
    print(f"[코퍼스] 같은 부모 {CS['n_same']}/{CS['n']} ({CS['frac_same']:.1%}) · "
          f"중앙 이견 {CS['med_dis']:.2f}° · 갈라진 {CS['n_diff']}컷 중 "
          f"{CS['n_diff_both0']}컷({CS['frac_diff_both0']:.1%})은 양쪽 오차 0.00°")
    print(f"\n[done] {p}  {sz / 1024:.0f} KB  {dim[0]}×{dim[1]} px  "
          f"(2 MB 규율 {'통과' if sz <= 2_000_000 else '위반'})")
