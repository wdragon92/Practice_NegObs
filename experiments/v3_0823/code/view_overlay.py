#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""view_overlay.py — 렌더된 프레임 한 장 위에 **폴라 격자(20칸)** 를 얹어 보여 준다.

왜 이 파일이 있나
-----------------
격자를 이미지에 투영하는 코드는 이미 여럿 있지만(`make_panels_v3.py` ·
`verdict_panels.py` · `weekend_0823/rt_response/code/wedge_util.py`) 전부
**특정 논문 그림 전용**이라 프레임 ID·칸 이름이 파일 안에 박혀 있고, 임의의 PNG
한 장을 인자로 받는 것이 하나도 없다. 이 스크립트는 그 한 가지만 한다:

    PNG 한 장  →  같은 폴더의 `variation.json` 에서 그 컷의 카메라를 찾고
                 →  gridspec_v1 의 20칸 쐐기를 지면(z = cam.ground_z)에 그리고
                 →  옆에 `_grid.png` 로 저장.

투영은 **정본** `experiments/mainrun_0819/code/labeling/labeler.py` 의
`project()` / `cam_basis()` 를 그대로 import 한다 — 카메라 규약을 다시 유도하지
않는다(라벨러가 쓴 것과 같은 격자여야 의미가 있다).

사용
----
    python3 experiments/v3_0823/code/view_overlay.py \
            dataset/misc/260827_handson/val/scene01/L0__s20260827__0000.png

    # 특정 칸만 강조 (칸 이름 = 섹터 A~E + 밴드 1/2/3a/3b)
    python3 experiments/v3_0823/code/view_overlay.py <PNG> --cells B3b,C3a

    # 라벨 매니페스트가 있으면 그 프레임의 GT 양성 칸을 자동 강조
    python3 experiments/v3_0823/code/view_overlay.py <PNG> --gt <manifest.json>

칸 이름 규약 (gridspec_v1)
    섹터 A B C D E = 화면 왼쪽 → 오른쪽 (A = +방위 = 진행방향 왼쪽)
    밴드  1 = 0–2 m · 2 = 2–5 m · 3a = 5–8 m · 3b = 8–12 m
    cell_index = band*5 + sector
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
LABDIR = os.path.join(REPO, "experiments", "mainrun_0819", "code", "labeling")
sys.path.insert(0, LABDIR)
import labeler as L                                              # noqa: E402

GRID_PATH = os.path.join(LABDIR, "gridspec_v1.json")


def load_grid(path=GRID_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def cell_names(grid):
    """cell_index 순서(band*ns + sector)와 **같은 순서**의 이름 리스트."""
    return [f"{s}{b}" for b in grid["band_names"] for s in grid["sector_names"]]


def cam_of(png):
    """PNG 옆 `variation.json` 에서 그 컷의 cam 블록을 꺼낸다."""
    sdir, fn = os.path.dirname(os.path.abspath(png)), os.path.basename(png)
    vj = os.path.join(sdir, "variation.json")
    if not os.path.isfile(vj):
        raise SystemExit(
            f"[view_overlay] {vj} 가 없다 — 이 PNG 는 데이터 렌더 산출물이 아닌 것 같다.\n"
            f"  (룩체크 캡처에는 카메라 사이드카가 없다. dataset/<group>/<run>/<split>/<scene>/ "
            f"아래의 PNG 를 쓰자.)")
    with open(vj, encoding="utf-8") as f:
        cuts = json.load(f)["cuts"]
    if isinstance(cuts, dict):
        cuts = list(cuts.values())
    for c in cuts:
        if c.get("file") == fn:
            return c["cam"]
    have = ", ".join(sorted(c.get("file", "?") for c in cuts)[:6])
    raise SystemExit(f"[view_overlay] variation.json 에 {fn} 컷이 없다 (있는 것: {have} …)")


def wedge_px(idx, cam, grid, n=48):
    """cell_index → 이미지 폴리곤 (px, py, 전부 카메라 앞인가).

    `labeler.polar_cells` 의 역: si = ns-1-k ⇒ az ∈ [ASC[ns-1-si], ASC[ns-si]).
    """
    ns = int(grid["n_sectors"])
    asc = grid["sector_edges_deg"][::-1]          # 오름차순 방위 경계
    bnd = grid["band_edges_m"]
    b, si = idx // ns, idx % ns
    k = ns - 1 - si
    a0, a1 = math.radians(asc[k]), math.radians(asc[k + 1])
    r0, r1 = bnd[b], bnd[b + 1]
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
    px, py, zc, _inb = L.project(np.asarray(pts), eye, cam)
    return px, py, bool(np.all(zc > 0.05))


def gt_cells_from_manifest(png, manifest, grid):
    """라벨 매니페스트에서 이 PNG 의 polar_gt(0/1 벡터) → 양성 칸 이름."""
    with open(manifest, encoding="utf-8") as f:
        man = json.load(f)
    ap = os.path.abspath(png)
    names = cell_names(grid)
    for fr in man.get("frames", []):
        rgb = fr.get("rgb", "")
        cand = rgb if os.path.isabs(rgb) else os.path.join(REPO, rgb)
        if os.path.abspath(cand) == ap:
            gt = fr.get("polar_gt") or []
            return [names[i] for i, v in enumerate(gt) if v]
    raise SystemExit(f"[view_overlay] 매니페스트에 이 프레임이 없다: {png}")


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="렌더 프레임 위에 폴라 격자(20칸)를 얹는다",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("png", help="dataset/<group>/<run>/<split>/<scene>/*.png  "
                                "(그룹은 dataset/ROUNDS.json · variation_kit.round_dir 가 알려준다)")
    ap.add_argument("-o", "--out", default=None,
                    help="출력 경로 (기본: 입력 옆 <stem>_grid.png)")
    ap.add_argument("--cells", default="",
                    help="강조할 칸, 쉼표로 (예: B3b,C3a)")
    ap.add_argument("--gt", default="",
                    help="라벨 매니페스트 json — 이 프레임의 GT 양성 칸을 강조")
    ap.add_argument("--grid", default=GRID_PATH, help="gridspec json")
    ap.add_argument("--no-labels", action="store_true", help="칸 이름 숨김")
    a = ap.parse_args(argv)

    grid = load_grid(a.grid)
    names = cell_names(grid)
    cam = cam_of(a.png)

    hot = set()
    if a.cells:
        for c in (x.strip() for x in a.cells.split(",")):
            if not c:
                continue
            if c not in names:
                raise SystemExit(f"[view_overlay] 칸 이름 {c!r} 없음 — 가능: {names}")
            hot.add(c)
    if a.gt:
        hot |= set(gt_cells_from_manifest(a.png, a.gt, grid))

    img = Image.open(a.png).convert("RGB")
    if img.size != (L.W_IMG, L.H_IMG):
        print(f"[view_overlay] 경고: 이미지 {img.size} ≠ 렌더 규격 "
              f"({L.W_IMG}×{L.H_IMG}) — 격자가 어긋날 수 있다")
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
    except Exception:
        font = ImageFont.load_default()

    LINE = (255, 235, 60, 200)          # 격자선 - 노랑
    HOT_F = (220, 40, 60, 90)           # 강조 칸 채움 - 빨강
    HOT_L = (255, 70, 90, 235)
    drawn = skipped = 0
    for i, nm in enumerate(names):
        px, py, ok = wedge_px(i, cam, grid)
        if not ok:                       # 일부가 카메라 뒤 → 투영이 무의미
            skipped += 1
            continue
        poly = list(zip(px.tolist(), py.tolist()))
        if nm in hot:
            dr.polygon(poly, fill=HOT_F, outline=HOT_L)
            dr.line(poly + [poly[0]], fill=HOT_L, width=5)
        else:
            dr.line(poly + [poly[0]], fill=LINE, width=2)
        drawn += 1
        if not a.no_labels:
            cx, cy = float(np.mean(px)), float(np.mean(py))
            if 0 <= cx < L.W_IMG and 0 <= cy < L.H_IMG:
                col = HOT_L if nm in hot else LINE
                dr.text((cx, cy), nm, fill=col, font=font, anchor="mm",
                        stroke_width=3, stroke_fill=(0, 0, 0, 200))

    out = a.out or (os.path.splitext(a.png)[0] + "_grid.png")
    Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB").save(out)
    print(f"[view_overlay] {os.path.basename(a.png)} · 칸 {drawn} 그림"
          + (f" · {skipped} 칸은 카메라 뒤라 생략" if skipped else "")
          + (f" · 강조 {sorted(hot)}" if hot else ""))
    print(f"[view_overlay] cam d={cam['d']:.2f} m · h_rel={cam['h_rel']:.2f} m · "
          f"yaw={cam['yaw']:.2f}° · pitch={cam['pitch']:.2f}° · "
          f"hfov={cam['hfov']:.2f}° · ground_z={cam['ground_z']:.3f}")
    print(f"[view_overlay] → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
