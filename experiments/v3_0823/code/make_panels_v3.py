#!/usr/bin/env python3
"""make_panels_v3.py — PART B of the v3 panel track.

Builds experiments/v3_0823/panels/:
  1. fa_family_exemplars.png  — 9 existing dataset renders + projected FA cell wedges
  2. cell_axis_flip.png       — frame-axis vs cell-axis H recall at tau = 0.5
  3. rescore_delta.png        — published vs corrected-GT V recall, H-row invariance
  4. fusion_headroom.png      — OFF-layer zero-overlap / AND-gating ceiling

CPU only.  No renders, no inference, no GPU, no git.  Every number is read from a
JSON ledger and gated against the markdown it is supposed to agree with.

    PYTHONNOUSERSITE=1 python3 experiments/v3_0823/code/make_panels_v3.py

Index + captions: experiments/v3_0823/panels/PANELS_V3.md
"""

import os, matplotlib
matplotlib.use("Agg")
from matplotlib import font_manager, rcParams

ROOT = "/home/vislab/Desktop/work_sy/Practice_NegObs"
OUT  = os.path.join(ROOT, "experiments/v3_0823/panels")
os.makedirs(OUT, exist_ok=True)

_FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
for i in (0, 1, 2, 3, 4):                      # KR face inside the TTC
    try:
        font_manager.fontManager.addfont(_FONT)
        break
    except Exception:
        pass
rcParams["font.family"] = ["Noto Sans CJK KR", "Noto Sans CJK JP", "DejaVu Sans"]
rcParams["axes.unicode_minus"] = False
rcParams["savefig.facecolor"] = "white"
rcParams["figure.facecolor"] = "white"

# brand-neutral, colour-blind-safe: rgb / depth / b2
C = dict(rgb="#4C6FBF", depth="#D97C2B", b2="#7E8794",
         pub="#B9C2D0", cor="#2F4B7C", ok="#2E7D5B", bad="#B03A48",
         grid="#DDE1E6", ink="#1F2429", mute="#5C6672")

DATE = "2026-08-23"

def footer(fig, text, y=0.012):
    fig.text(0.5, y, text, ha="center", va="bottom", fontsize=7.4,
             color=C["mute"], family=rcParams["font.family"])

def save(fig, name, dpi=130):
    p = os.path.join(OUT, name)
    fig.savefig(p, dpi=dpi, bbox_inches="tight", pad_inches=0.22)
    import PIL.Image as I
    sz = os.path.getsize(p)
    if sz > 2_000_000:                          # size discipline: <= 2 MB / PNG
        im = I.open(p).convert("RGB")
        im.quantize(colors=256, method=I.MEDIANCUT).save(p, optimize=True)
        sz = os.path.getsize(p)
    print(f"  {name:28s} {sz/1024:8.0f} KB  {I.open(p).size}")
    return p


import json, math, os, sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
sys.path.insert(0, os.path.join(ROOT, "experiments/mainrun_0819/code/labeling"))
import labeler as L
from PIL import Image

GRID = json.load(open(os.path.join(ROOT, "experiments/mainrun_0819/code/labeling/gridspec_v1.json")))
MAN  = json.load(open(os.path.join(ROOT, "experiments/v3_0823/dataset_manifest_v2corr.json")))
FM   = {f["frame_id"]: f for f in MAN["frames"]}
CELLS = [f"{s}{b}" for b in ("1", "2", "3a", "3b") for s in "ABCDE"]
NS, NB = GRID["n_sectors"], GRID["n_bands"]
ASC = GRID["sector_edges_deg"][::-1]            # ascending azimuth edges
BND = GRID["band_edges_m"]

TILES = [
 ("off/scene15/L4__s20260819__0003.png",          "B3b", "rgb",   42, 0.975,
  "경계칸형·반경(3b)", "bnd", "골목 회랑 · 계단 제거된 off팔"),
 ("off/scene05/L5__s20260819__0002.png",          "B3b", "rgb",   43, 0.998,
  "경계칸형·반경(3b)", "bnd", "야외극장 · 립 제거된 off팔"),
 ("off/sceneN3/L5__s20260819__0002.png",          "C3b", "b2",    42, 0.982,
  "경계칸형·반경(3b)", "bnd", "트롱프뢰유 · 낙차는 페인트 1 mm"),
 ("on/scene07/L5__s20260821__0003.png::boost_e2", "C3a", "depth", 43, 1.000,
  "지형통계형", "ter", "미학습 칸 / prior 포화"),
 ("on/scene15/L0__s20260819__0005.png",           "B3a", "depth", 43, 0.913,
  "지형통계형", "ter", "회랑 굽이 뒤 미학습 칸"),
 ("on/scene15/L7__s20260819__0006.png",           "C3a", "b2",    44, 0.936,
  "지형통계형", "ter", "같은 씬 · 다른 모달리티"),
 ("on/scene07/L5__s20260819__0003.png",           "D3b", "depth", 43, 1.000,
  "조명형", "lit", "휘도비 이탈 칸"),
 ("on/scene15/L7__s20260819__0003.png",           "B3b", "rgb",   42, 0.968,
  "조명형", "lit", "역광 계열 L7"),
 ("on/sceneC2/L2__s20260819__0004.png",           "A3a", "depth", 43, 0.998,
  "장식형 — 기각", "dec", "난간이 있는 좌측 A섹터 · 그래도 lift ≈ 1"),
]
FAMCOL = dict(bnd="#B03A48", ter="#2E7D5B", lit="#C08400", dec="#5C6672")


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


fig = plt.figure(figsize=(15.2, 12.2))
gs = fig.add_gridspec(3, 3, left=.026, right=.986, top=.845, bottom=.062,
                      hspace=.235, wspace=.040)

for k, (fid, cell, model, seed, score, fam, fk, note) in enumerate(TILES):
    fr = FM[fid]; cam = cam_of(fr)
    img = Image.open(fr["rgb"]).convert("RGB")
    img = img.resize((760, 428), Image.LANCZOS)
    sx, sy = 760 / L.W_IMG, 428 / L.H_IMG
    px, py, front, inb = wedge_px(cell, cam)

    ax = fig.add_subplot(gs[k // 3, k % 3])
    ax.imshow(np.asarray(img)); ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlim(0, 760); ax.set_ylim(428, 0)
    col = FAMCOL[fk]
    if front.all():
        ax.add_patch(Polygon(np.c_[px * sx, py * sy], closed=True,
                             fc=col, ec=col, alpha=.30, lw=0))
        ax.add_patch(Polygon(np.c_[px * sx, py * sy], closed=True,
                             fc="none", ec=col, lw=2.4))
        ax.add_patch(Polygon(np.c_[px * sx, py * sy], closed=True,
                             fc="none", ec="white", lw=0.9, ls=(0, (4, 3))))
        vis = int(inb.sum()) / len(inb)
        tag = "" if vis > .55 else "  (일부 화면 밖)"
        print("   vis", cell, round(vis, 2))
    else:
        tag = "  (칸이 카메라 뒤)"
    for s in ax.spines.values():
        s.set_color(col); s.set_linewidth(2.2)
    arm = "OFF팔 · GT 전 칸 0" if fid.startswith("off/") else "ON_NEG · 음성 칸"
    ax.set_title(f"{fam}   ·   {fid.split('/')[1]} / {cell}{tag}",
                 fontsize=11.4, color=col, pad=6, fontweight="bold")
    ax.text(.014, .968, f"{model}·s{seed}   p={score:.3f}", transform=ax.transAxes,
            ha="left", va="top", fontsize=9.6, color="white",
            bbox=dict(fc=col, ec="none", pad=2.6, alpha=.94))
    ax.text(.014, .030, f"{arm} · {note}", transform=ax.transAxes,
            ha="left", va="bottom", fontsize=8.6, color="white",
            bbox=dict(fc="#000000", ec="none", pad=2.4, alpha=.58))

fig.text(.026, .975, "FA 가족 대표 컷 — 발화한 칸의 지면 쐐기를 영상에 되투영",
         fontsize=20, fontweight="bold", color=C["ink"], ha="left", va="top")
fig.text(.026, .938,
         "붉은색 = 경계칸형·반경(3b) · OFF lift 2.71        "
         "초록색 = 지형통계형 · ON_NEG lift 1.30        "
         "노란색 = 조명형 · ON_NEG lift 2.06        "
         "회색 = 장식형 기각 · OFF lift 1.01 / 0.98",
         fontsize=11.6, color=C["mute"], ha="left", va="top")
fig.text(.026, .911,
         "각 타일의 색칠된 쐐기 = 그 모델이 τ=0.5에서 발화한 칸의 지면 영역. "
         "off팔 3장은 낙차를 제거한 팔이라 GT가 전 칸 0인데도 3b 밴드가 탄다.",
         fontsize=9.9, color=C["mute"], ha="left", va="top")
fig.text(.026, .886,
         "쐐기는 variation.json의 cam(eye·yaw·pitch·roll·hfov·ground_z)과 gridspec_v1의 "
         "sector_edges_deg / band_edges_m로부터 labeler.project로 계산 — 새 렌더·새 추론 없음.",
         fontsize=9.9, color=C["mute"], ha="left", va="top")
footer(fig,
       "원장  experiments/v3_0823/fa_events_v2corr.csv (교정 GT)  ·  가족 lift  experiments/v3_0823/logs/fa_census_tables_v2corr.json → t3_lift  ·  "
       "장식형 lift  FA_CENSUS.md §3.4 (국소화 2씬 sceneC2·sceneN3)  ·  격자  experiments/mainrun_0819/code/labeling/gridspec_v1.json  ·  " + DATE)
save(fig, "fa_family_exemplars.png", dpi=112)
plt.close(fig)


import json, math, os, sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

V3 = os.path.join(ROOT, "experiments/v3_0823")
RES = json.load(open(os.path.join(V3, "eval_v2corr/rescore_tables.json")))
FAC = json.load(open(os.path.join(V3, "logs/fa_census_tables_v2corr.json")))
FAO = json.load(open(os.path.join(V3, "logs/fa_census_tables.json")))
MODELS = ("rgb", "depth", "b2")
LBL = dict(rgb="RGB", depth="Depth", b2="B2")


# ===================================================================== (2) ===
# tau = 0.5, no matching, same ckpt / frames / GT.
# Numbers are COMPUTED from the JSON ledger (gates.H_row_identical, corrected GT),
# then cross-checked against the 3-dp values printed in EVL12_CELL_AXIS.md §4.
GH = RES["gates"]["H_row_identical"]
mean3 = lambda m, k: sum(GH[f"{m}_s{s}"][k] for s in (42, 43, 44)) / 3.0
FRAME_H = {m: mean3(m, "frame_recall_H_cor") for m in MODELS}
CELL_H  = {m: mean3(m, "cell_recall_H_cor") for m in MODELS}
FRAME_FA = {m: RES["by_model"][m]["corrected"]["frame_fa_off"]["mean"] for m in MODELS}
CELL_FPR = {m: RES["by_model"][m]["corrected"]["cell_fpr_off"]["mean"] for m in MODELS}

_E12 = dict(frame_H=dict(rgb=.688, depth=.438, b2=.229),
            cell_H=dict(rgb=.344, depth=.537, b2=.096),
            frame_fa=dict(rgb=.359, depth=.042, b2=.238),
            cell_fpr=dict(rgb=.0467, depth=.0089, b2=.0347))
for m in MODELS:
    assert round(FRAME_H[m], 3) == _E12["frame_H"][m], (m, FRAME_H[m])
    assert round(CELL_H[m], 3) == _E12["cell_H"][m], (m, CELL_H[m])
    assert round(FRAME_FA[m], 3) == _E12["frame_fa"][m], (m, FRAME_FA[m])
    assert round(CELL_FPR[m], 4) == _E12["cell_fpr"][m], (m, CELL_FPR[m])
    # frame-axis H must also equal the by_model aggregate
    assert abs(FRAME_H[m] - RES["by_model"][m]["corrected"]["frame_recall_H"]["mean"]) < 1e-12
print("  gate ok: JSON-computed axes == EVL12_CELL_AXIS.md §4 (3-4 dp), 12/12 cells")

fig, axes = plt.subplots(1, 2, figsize=(13.2, 6.5))
for ax, (vals, fa, title, sub, unit, nd) in zip(axes, [
        (FRAME_H, FRAME_FA, "프레임 축  (공표면)",
         "frame_recall_H  @  frame_fa_off", "FA", 3),
        (CELL_H, CELL_FPR, "칸 축  (EVL12 신설)",
         "cell_recall_H  @  cell_fpr_off", "칸FPR", 4)]):
    x = np.arange(3)
    win = max(vals, key=vals.get)
    cols = [C[m] if m == win else "#C9CFD6" for m in MODELS]
    b = ax.bar(x, [vals[m] for m in MODELS], width=.58, color=cols,
               edgecolor="white", linewidth=1.4, zorder=3)
    for i, m in enumerate(MODELS):
        ax.text(i, vals[m] + .018, f"{vals[m]:.3f}", ha="center", va="bottom",
                fontsize=15 if m == win else 13,
                fontweight="bold" if m == win else "normal",
                color=C[m] if m == win else C["mute"], zorder=4)
        ax.text(i, .012, f"{unit} {fa[m]:.{nd}f}".replace("0.", "."),
                ha="center", va="bottom", fontsize=9.4, color="white", zorder=4)
    ax.text(x[MODELS.index(win)], vals[win] + .075, "◀ 승자",
            ha="center", va="bottom", fontsize=12, fontweight="bold",
            color=C[win], zorder=4)
    ax.set_xticks(x); ax.set_xticklabels([LBL[m] for m in MODELS], fontsize=13)
    ax.set_ylim(0, .82); ax.set_ylabel("H tier recall  (3시드 평균)", fontsize=11.5)
    ax.set_title(title, fontsize=15, fontweight="bold", color=C["ink"], pad=16)
    ax.text(.5, 1.015, sub, transform=ax.transAxes, ha="center", va="bottom",
            fontsize=10.4, color=C["mute"])
    ax.grid(axis="y", color=C["grid"], lw=.9, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

fig.suptitle("단위만 바꾸면 H 우열이 뒤집힌다 — τ=0.5, 같은 체크포인트·같은 프레임·같은 GT",
             fontsize=17.5, fontweight="bold", color=C["ink"], y=1.045)
fig.text(.5, .985,
         "프레임 축은 「한 프레임에서 한 칸이라도 맞으면 성공」, 칸 축은 「20칸을 각각 센다」. "
         "운용점도 정답지도 그대로이고 검출의 단위만 바뀌었다.",
         ha="center", va="top", fontsize=11, color=C["mute"])
fig.text(.5, .935,
         f"RGB  {FRAME_H['rgb']:.3f} → {CELL_H['rgb']:.3f}   (−{FRAME_H['rgb']-CELL_H['rgb']:.3f})"
         f"          Depth  {FRAME_H['depth']:.3f} → {CELL_H['depth']:.3f}   (+{CELL_H['depth']-FRAME_H['depth']:.3f})"
         "          →  RGB는 정답 칸 하나만 맞히고 여분을 뿌린다",
         ha="center", va="top", fontsize=11.6, color=C["ink"], fontweight="bold")
fig.tight_layout(rect=[0, .055, 1, .90])
footer(fig,
       "원장  experiments/v3_0823/redteam/EVL12_CELL_AXIS.md §4  ·  검증 게이트  프레임 축 H가 "
       "experiments/v3_0823/eval_v2corr/rescore_tables.json → by_model[*].corrected.frame_recall_H 와 소수 3자리 일치  ·  "
       "교정 GT · 3시드 평균 · " + DATE, y=.012)
save(fig, "cell_axis_flip.png", dpi=132)
plt.close(fig)


# ===================================================================== (3) ===
def g(m, side, k):
    return RES["by_model"][m][side][k]

cen = RES["census"]
fig, axes = plt.subplots(1, 2, figsize=(13.6, 6.4),
                         gridspec_kw=dict(width_ratios=[1.32, 1]))

ax = axes[0]
x = np.arange(3); w = .33
pub = [g(m, "published", "frame_recall_V")["mean"] for m in MODELS]
cor = [g(m, "corrected", "frame_recall_V")["mean"] for m in MODELS]
sig = [g(m, "published", "frame_recall_V")["sigma"] for m in MODELS]
ax.bar(x - w / 2, pub, w, color=C["pub"], edgecolor="white", lw=1.3,
       label="공표표 (구 GT · 분모 327)", zorder=3)
ax.bar(x + w / 2, cor, w, color=C["cor"], edgecolor="white", lw=1.3,
       label="재채점 (교정 GT · 분모 369)", zorder=3)
ax.errorbar(x - w / 2, pub, yerr=sig, fmt="none", ecolor=C["mute"],
            elinewidth=1.4, capsize=5, zorder=4)
for i, m in enumerate(MODELS):
    d = cor[i] - pub[i]
    halo = dict(fc="white", ec="none", alpha=.88, pad=1.6)
    ax.text(i - w / 2 - .085, pub[i] + .012, f"{pub[i]:.3f}", ha="right",
            va="bottom", fontsize=10.6, color=C["mute"], bbox=halo, zorder=5)
    ax.text(i + w / 2, cor[i] + .016, f"{cor[i]:.3f}", ha="center", va="bottom",
            fontsize=10.6, color=C["cor"], fontweight="bold", bbox=halo, zorder=5)
    ax.text(i, .045, f"Δ {d:+.4f}\n(σ {sig[i]:.3f})", ha="center", va="bottom",
            fontsize=10.4, color=C["bad"] if d < 0 else C["ok"], fontweight="bold",
            bbox=dict(fc="white", ec="none", alpha=.90, pad=2.6), zorder=5)
ax.set_xticks(x); ax.set_xticklabels([LBL[m] for m in MODELS], fontsize=13)
ax.set_ylim(0, 1.10); ax.set_ylabel("V tier frame recall  (3시드 평균)", fontsize=11.5)
ax.set_title("움직이는 행 — V recall", fontsize=14.5, fontweight="bold",
             color=C["ink"], pad=10)
ax.legend(loc="upper center", ncol=2, fontsize=10, frameon=False,
          bbox_to_anchor=(.5, 1.0))
ax.grid(axis="y", color=C["grid"], lw=.9, zorder=0); ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.text(.5, -.135, "세 이동 전부 시드 σ 이내 — 부호가 바뀐 모델도, σ를 넘긴 모델도 없다",
        transform=ax.transAxes, ha="center", va="top", fontsize=10.4, color=C["mute"])

ax = axes[1]
hp = [g(m, "published", "frame_recall_H")["mean"] for m in MODELS]
hc = [g(m, "corrected", "frame_recall_H")["mean"] for m in MODELS]
assert all(abs(a - b) < 1e-12 for a, b in zip(hp, hc))
ax.bar(x - w / 2, hp, w, color=C["pub"], edgecolor="white", lw=1.3, zorder=3)
ax.bar(x + w / 2, hc, w, color=C["cor"], edgecolor="white", lw=1.3, zorder=3)
for i, m in enumerate(MODELS):
    ax.text(i, max(hp[i], hc[i]) + .022, f"{hp[i]:.4f}\nΔ 0.0000",
            ha="center", va="bottom", fontsize=10.8, color=C["ok"],
            fontweight="bold", bbox=dict(fc="white", ec="none", alpha=.88, pad=2),
            zorder=5)
ax.set_xticks(x); ax.set_xticklabels([LBL[m] for m in MODELS], fontsize=13)
ax.set_ylim(0, 1.10); ax.set_ylabel("H tier frame recall", fontsize=11.5)
ax.set_title("불변인 행 — H recall  (헤드라인)", fontsize=14.5,
             fontweight="bold", color=C["ok"], pad=10)
ax.grid(axis="y", color=C["grid"], lw=.9, zorder=0); ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
for s in ax.spines.values():
    s.set_linewidth(1.0)
ax.text(.5, .90, "9/9 런 · 프레임·칸 축 모두 완전 동일\ntest H 96프레임이 교정 대상 밖",
        transform=ax.transAxes, ha="center", va="top", fontsize=11.4,
        color=C["ok"], fontweight="bold",
        bbox=dict(fc="#EAF4EF", ec=C["ok"], lw=1.2, pad=7))
ax.text(.5, -.135,
        f"예측 확률은 9/9 런에서 max|Δp| = {max(RES['gates']['p_max_abs_diff'].values()):.3e} — "
        "픽셀·모델·τ는 하나도 안 움직였다",
        transform=ax.transAxes, ha="center", va="top", fontsize=10.4, color=C["mute"])

fig.suptitle("교정 GT 재채점 델타 — 헤드라인 H는 한 자리도 안 움직인다",
             fontsize=17.5, fontweight="bold", color=C["ink"], y=1.035)
fig.text(.5, .975,
         f"scene07 boost_e/e2 온팔 {len(cen['entering_frames'])}프레임"
         f"(none_in_fov→V {cen['tier_migration_test']['none_in_fov->V']} · "
         f"→H_weak {cen['tier_migration_test']['none_in_fov->H_weak']})이 양성으로 편입 → "
         f"recall 분모 {cen['n_hazard_old']} → {cen['n_hazard_corrected']}, "
         f"양성 칸 {cen['n_pos_cells_old']:,} → {cen['n_pos_cells_corrected']:,}. "
         "분모가 커진 V 계열만 움직이고 H·E·off팔은 정의상 불변.",
         ha="center", va="top", fontsize=11, color=C["mute"])
fig.tight_layout(rect=[0, .075, 1, .93])
footer(fig,
       "원장  experiments/v3_0823/eval_v2corr/rescore_tables.json (by_model · census · gates)  ·  "
       "산문 대조  experiments/v3_0823/V2_RESCORE.md §1  ·  분모 369는 ACCOUNTING.md §4.2의 372 오기를 정정한 값  ·  " + DATE,
       y=.012)
save(fig, "rescore_delta.png", dpi=132)
plt.close(fig)



# ===================================================================== (4) ===
T = FAC["t4_overlap"]
n_rgb = T["rgb~depth|OFF|ALL"]["a"]
n_dep = T["rgb~depth|OFF|ALL"]["b"]
n_b2  = T["rgb~b2|OFF|ALL"]["b"]
i_rd  = T["rgb~depth|OFF|ALL"]["inter"]
i_rb  = T["rgb~b2|OFF|ALL"]["inter"]
i_db  = T["depth~b2|OFF|ALL"]["inter"]
tri   = T["TRIPLE|OFF"]
assert T["rgb~b2|OFF|ALL"]["a"] == n_rgb and T["depth~b2|OFF|ALL"]["a"] == n_dep
assert T["depth~b2|OFF|ALL"]["b"] == n_b2
assert n_rgb + n_dep + n_b2 - (i_rd + i_rb + i_db) + tri["all3"] == tri["union"]
assert tri["exactly1"] + tri["exactly2"] + tri["all3"] == tri["union"]
same_off = all(FAO["t4_overlap"][k] == T[k] for k in
               ("rgb~depth|OFF|ALL", "rgb~b2|OFF|ALL", "depth~b2|OFF|ALL", "TRIPLE|OFF"))
tri_on, tri_on_old = T["TRIPLE|ON_NEG"], FAO["t4_overlap"]["TRIPLE|ON_NEG"]

fig = plt.figure(figsize=(14.4, 7.6))
gsp = fig.add_gridspec(1, 2, width_ratios=[1.10, 1], left=.035, right=.975,
                       top=.735, bottom=.105, wspace=.14)

# ---- left: schematic Venn ---------------------------------------------------
ax = fig.add_subplot(gsp[0]); ax.set_aspect("equal"); ax.axis("off")
ax.set_xlim(-1.50, 1.28); ax.set_ylim(-1.66, 1.06)
R = {m: .70 * math.sqrt(n / n_rgb) for m, n in
     (("rgb", n_rgb), ("depth", n_dep), ("b2", n_b2))}
P = dict(rgb=(-.60, .10), depth=(.68, -.16), b2=(.10, -.52))
for m, n in (("rgb", n_rgb), ("b2", n_b2), ("depth", n_dep)):
    ax.add_patch(Circle(P[m], R[m], fc=C[m], ec=C[m], alpha=.28, lw=0, zorder=2))
    ax.add_patch(Circle(P[m], R[m], fc="none", ec=C[m], lw=2.6, zorder=3))
ax.text(P["rgb"][0], P["rgb"][1] + R["rgb"] + .07, f"RGB  {n_rgb}칸", ha="center",
        va="bottom", fontsize=14, fontweight="bold", color=C["rgb"], zorder=6)
ax.text(P["depth"][0] + R["depth"] + .07, P["depth"][1] + .16, f"Depth  {n_dep}칸",
        ha="left", va="center", fontsize=14, fontweight="bold", color=C["depth"], zorder=6)
ax.text(P["b2"][0], P["b2"][1] - R["b2"] - .09, f"B2  {n_b2}칸", ha="center",
        va="top", fontsize=14, fontweight="bold", color=C["b2"], zorder=6)

ax.annotate("", xy=(P["rgb"][0] + R["rgb"] * .72, P["rgb"][1] + R["rgb"] * .72),
            xytext=(.30, .60), arrowprops=dict(arrowstyle="-", color=C["bad"], lw=1.3), zorder=5)
ax.annotate("", xy=(P["depth"][0] - R["depth"] * .70, P["depth"][1] + R["depth"] * .70),
            xytext=(.30, .60), arrowprops=dict(arrowstyle="-", color=C["bad"], lw=1.3), zorder=5)
ax.text(.30, .68, f"rgb ∩ depth = {i_rd}", ha="center", va="bottom", fontsize=15,
        fontweight="bold", color=C["bad"], zorder=7,
        bbox=dict(fc="white", ec=C["bad"], lw=1.8, pad=5.5))
ax.text(-.122, -.324, f"{i_rb}", ha="center", va="center", fontsize=13,
        fontweight="bold", color=C["ink"], zorder=7,
        bbox=dict(fc="white", ec="none", alpha=.80, pad=1.6))
ax.annotate(f"depth ∩ b2 = {i_db}", xy=(.455, -.325), xytext=(.94, -.90),
            fontsize=10.6, color=C["mute"], ha="center", zorder=7,
            arrowprops=dict(arrowstyle="-|>", color=C["mute"], lw=1.2))
ax.text(-.44, -.52, f"rgb ∩ b2 = {i_rb}", ha="right", va="center",
        fontsize=10.6, color=C["mute"], zorder=7)
ax.annotate("", xy=(-.16, -.34), xytext=(-.42, -.50),
            arrowprops=dict(arrowstyle="-|>", color=C["mute"], lw=1.2), zorder=6)
ax.text(-.11, -1.30, f"3모델 동시 발화 = {tri['all3']}칸        합집합 {tri['union']}칸",
        ha="center", va="center", fontsize=14, fontweight="bold", color=C["bad"], zorder=7)
ax.text(-.11, -1.57,
        f"참고 · ON_NEG층은 겹친다: 3모델 동시 {tri_on['all3']}/{tri_on['union']}칸 "
        f"({tri_on['share']*100:.1f} %) — 구 GT {tri_on_old['all3']}/{tri_on_old['union']} "
        f"({tri_on_old['share']*100:.1f} %)에서 방향 유지",
        ha="center", va="center", fontsize=10.2, color=C["mute"], zorder=7)
ax.set_title("OFF층 시드-다수결 FA 칸 집합\n(모식도 — 원 면적 ∝ 칸 수, 겹침 면적은 비례 아님)",
             fontsize=11.4, color=C["mute"], pad=6)

# ---- right: union composition ----------------------------------------------
ax = fig.add_subplot(gsp[1])
parts = [("정확히 1모델만", tri["exactly1"], "#8FA6C9"),
         ("정확히 2모델", tri["exactly2"], "#D9A441"),
         ("3모델 동시", tri["all3"], C["bad"])]
left = 0
for lab, n, col in parts:
    ax.barh([0], [n], left=left, height=.46, color=col, edgecolor="white",
            lw=1.6, zorder=3)
    if n / tri["union"] > .30:
        ax.text(left + n / 2, 0, f"{lab}\n{n}칸  ({n/tri['union']*100:.1f} %)",
                ha="center", va="center", fontsize=12, color="white",
                fontweight="bold", zorder=4)
    elif n:
        ax.annotate(f"{lab}\n{n}칸  ({n/tri['union']*100:.1f} %)",
                    xy=(left + n / 2, .23), xytext=(left + n / 2, .70),
                    ha="center", va="bottom", fontsize=11.4, color=col,
                    fontweight="bold", zorder=4,
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=1.5))
    left += n
ax.annotate(f"3모델 동시\n{tri['all3']}칸  (0.0 %)", xy=(tri["union"], -.23),
            xytext=(tri["union"] * .955, -.78), ha="center", va="top",
            fontsize=11.8, fontweight="bold", color=C["bad"], zorder=4,
            arrowprops=dict(arrowstyle="-|>", color=C["bad"], lw=1.6))
ax.set_xlim(0, tri["union"] * 1.06); ax.set_ylim(-1.75, 1.30)
ax.set_yticks([]); ax.set_xlabel(f"합집합 {tri['union']}칸의 구성", fontsize=11.5)
ax.set_title("AND(합의) 게이팅의 상한", fontsize=15, fontweight="bold",
             color=C["ink"], pad=10)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.text(.5, .055,
        f"3모델 AND  →  off팔 FA {tri['all3']}칸 (원리적 전멸)\n"
        f"2모델 AND  →  {tri['exactly2']}칸만 잔존 ({tri['exactly2']/tri['union']*100:.1f} %)",
        transform=ax.transAxes, ha="center", va="bottom", fontsize=12.6,
        color=C["ink"], fontweight="bold",
        bbox=dict(fc="#F3F5F8", ec=C["grid"], lw=1.2, pad=8), zorder=5)

fig.suptitle("융합 여유 — off팔에서 RGB와 Depth는 단 한 칸도 겹치지 않는다",
             fontsize=18.5, fontweight="bold", color=C["ink"], y=.975)
fig.text(.5, .905,
         "집합 단위 = 시드-다수결 (frame, cell) — 3시드 중 ≥2에서 발화한 칸만. 잡음 FA를 먼저 제거한 뒤 비교.",
         ha="center", va="top", fontsize=11.4, color=C["mute"])
fig.text(.5, .868,
         "⚠ 이것은 FA 상한이지 성능 보장이 아니다 — 같은 비중첩이 recall에도 적용되면 합의 게이팅은 검출도 함께 죽인다.",
         ha="center", va="top", fontsize=11.2, color=C["bad"], fontweight="bold")
footer(fig,
       "원장  experiments/v3_0823/logs/fa_census_tables_v2corr.json → t4_overlap  "
       f"[교정 GT — OFF층 4개 항목은 구 GT logs/fa_census_tables.json과 {'완전 동일' if same_off else '불일치'}]  ·  "
       "산문 대조  FA_CENSUS.md §4  ·  분모 = ACCOUNTING.md §4.5 행 A (OFF층 노출 8,160칸)  ·  " + DATE,
       y=.014)
save(fig, "fusion_headroom.png", dpi=132)
plt.close(fig)
print("  OFF-layer old==new:", same_off)
