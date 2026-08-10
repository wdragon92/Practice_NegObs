#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scene13 유리 31프림 — 낙차 경계 차폐 여부 전수 검사 (08-10 사용자 지시 '체크좀 해줘').

방법: geom_invariance_check 의 fake-USD 하네스로 scene13 을 CPU 조립 → 유리 프림
world AABB 추출 → (판정 눈 → 낙차 경계/보이드 샘플) 선분과 slab 교차 전수 검사.
유리 프림이 어떤 판정 시선의 경계 샘플도 가리지 않으면 '낙차 정보 무관'.
"""
import importlib.util
import json
import math
import os
import sys
from unittest.mock import MagicMock

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(REPO, "scenes", "main"))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "scripts"))

import geom_invariance_check as gic

_fake = {}
exec(compile(gic._FAKE, "<fakeusd>", "exec"), _fake)
_fake["_install"]()

import scene_common as sc
sc.boot = lambda headless=True: MagicMock()
sc.capture_pipeline = lambda *a, **k: None
sc.ensure_noon_lookfix = lambda p: p
sc.check_assets = lambda *a, **k: None
os.environ["NEGOBS_CAPTURE"] = "1"

path = os.path.join(REPO, "scenes", "main", "scene13_apartment_parking_entry.py")
spec = importlib.util.spec_from_file_location("negobs_scene13", path)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)
if hasattr(mod, "check_assets"):
    mod.check_assets = lambda *a, **k: None
_fake["reset"]()
import random
random.seed(0)
mod.main()
PRIMS = _fake["_PRIMS"]
print(f"[조립] 프림 {len(PRIMS)}개")

# ── 1. 유리 프림 수집 + world AABB ──────────────────────────────────────────
GLASS_PAT = ("Glass", "DoorTransom", "DoorSidelight")   # Leaf_Glass 는 'Glass' 매치


def world_aabb(rec):
    """리프 프림 직접 배치(부모 Xform 무변환 확인됨): T ± S·size/2, RZ는 AABB 확장."""
    tx = ty = tz = 0.0
    rot = 0.0
    sx = sy = sz = 1.0
    for k, v in rec["ops"]:
        if k == "T":
            tx, ty, tz = v
        elif k == "S":
            sx, sy, sz = v
        elif k in ("RZ", "RotZ"):
            rot = float(v if not isinstance(v, (tuple, list)) else v[0])
    size = float(rec["attrs"].get("size", 2.0))
    hx, hy, hz = sx * size / 2.0, sy * size / 2.0, sz * size / 2.0
    if abs(rot % 360.0) > 1e-6:                 # 회전 프림: 회전 사각형의 AABB
        c, s = abs(math.cos(math.radians(rot))), abs(math.sin(math.radians(rot)))
        hx, hy = c * hx + s * hy, s * hx + c * hy
    return (tx - hx, ty - hy, tz - hz, tx + hx, ty + hy, tz + hz)


glass = {}
for p, rec in PRIMS.items():
    base = p.split("/")[-1]
    if base.startswith("GlassPost"):            # 금속 멀리언 포스트 — 유리 아님
        continue
    if any(base.startswith(g) or g in base for g in GLASS_PAT):
        if rec["type"] in ("Cube",):
            glass[p] = world_aabb(rec)
print(f"[유리] 매치 {len(glass)}개")
for p in sorted(glass):
    b = glass[p]
    print(f"  {p.replace('/World/Scene13/', ''):42s} "
          f"x[{b[0]:6.2f},{b[3]:6.2f}] y[{b[1]:6.2f},{b[4]:6.2f}] z[{b[2]:5.2f},{b[5]:5.2f}]")

# ── 2. 판정 눈 ──────────────────────────────────────────────────────────────
views = mod.build_views()
eyes = {k: tuple(v["eye"]) for k, v in views.items()}
print(f"[눈] {len(eyes)}개: {', '.join(sorted(eyes))}")

# ── 3. 낙차 경계/보이드 샘플 ────────────────────────────────────────────────
P = mod.PARAMS
rp, st, sh = P["ramp"], P["stair"], P["shaft"]
portal_x = P["portal"]["x"]


def lin(a, b, n):
    return [(a[0] + (b[0] - a[0]) * i / (n - 1),
             a[1] + (b[1] - a[1]) * i / (n - 1),
             a[2] + (b[2] - a[2]) * i / (n - 1)) for i in range(n)]


samples = {}
# 트렌치 양측 코핑 라인(낙차 에지, z=0) — 크레스트 x≈0 부근에서 포털 24까지
samples["트렌치 북측 에지"] = lin((0.5, rp["y1"], 0.0), (portal_x, rp["y1"], 0.0), 13)
samples["트렌치 남측 에지"] = lin((0.5, rp["y0"], 0.0), (portal_x, rp["y0"], 0.0), 13)
# 램프 바닥(보이드 내부) 중앙선 — 하강면 자체
samples["램프 하강면"] = lin((2.0, 0.0, -0.2), (portal_x, 0.0, -3.7), 10)
# 계단 샤프트 림 4변 (z=0) — 동측 x_head 가 주 낙차 에지(도어 가드)
samples["샤프트 동측 에지"] = lin((sh["x1"], sh["y0"], 0.0), (sh["x1"], sh["y1"], 0.0), 7)
samples["샤프트 서측 에지"] = lin((sh["x0"], sh["y0"], 0.0), (sh["x0"], sh["y1"], 0.0), 5)
samples["샤프트 남측 에지"] = lin((sh["x0"], sh["y0"], 0.0), (sh["x1"], sh["y0"], 0.0), 7)
samples["샤프트 북측 에지"] = lin((sh["x0"], sh["y1"], 0.0), (sh["x1"], sh["y1"], 0.0), 7)
# 계단 보이드 내부(디딤면 하강 샘플: 플라이트1 + 미드랜딩 + 플라이트2)
samples["계단 하강면"] = (lin((11.05, 4.25, -0.165), (7.75, 4.25, -1.98), 6)
                          + [(6.40, 5.10, -1.98)]
                          + lin((7.75, 5.95, -2.145), (11.05, 5.95, -3.96), 6))

n_smp = sum(len(v) for v in samples.values())
print(f"[경계] {len(samples)}묶음 {n_smp}샘플")


# ── 4. 선분-AABB 교차(slab) ─────────────────────────────────────────────────
def seg_hits_aabb(a, b, box, eps=1e-9):
    (x0, y0, z0, x1, y1, z1) = box
    t0, t1 = 0.0, 1.0
    for i, (lo, hi) in enumerate(((x0, x1), (y0, y1), (z0, z1))):
        d = b[i] - a[i]
        if abs(d) < eps:
            if a[i] < lo or a[i] > hi:
                return False
            continue
        ta, tb = (lo - a[i]) / d, (hi - a[i]) / d
        if ta > tb:
            ta, tb = tb, ta
        t0, t1 = max(t0, ta), min(t1, tb)
        if t0 > t1:
            return False
    return True


hits = {p: [] for p in glass}
for vn, eye in eyes.items():
    for sn, pts in samples.items():
        for q in pts:
            for p, box in glass.items():
                # 눈이 박스 안이면(스킵) — stair_head 눈이 박스 내부에 있는 경우
                if (box[0] <= eye[0] <= box[3] and box[1] <= eye[1] <= box[4]
                        and box[2] <= eye[2] <= box[5]):
                    continue
                if seg_hits_aabb(eye, q, box):
                    tag = f"{vn}→{sn}"
                    if tag not in hits[p]:
                        hits[p].append(tag)

# ── 5. 판정 출력 ────────────────────────────────────────────────────────────
print("\n" + "=" * 78)
print("판정 — 낙차 경계/보이드 차폐 여부 (판정 눈 × 경계 샘플 전수)")
print("=" * 78)
rel, irrel = [], []
for p in sorted(glass):
    short = p.replace("/World/Scene13/", "")
    if hits[p]:
        rel.append(short)
        srcs = sorted(set(h.split("→")[0] for h in hits[p]))
        tgts = sorted(set(h.split("→")[1] for h in hits[p]))
        print(f"[차폐 O] {short:40s} 눈={','.join(srcs)}")
        print(f"          경계={', '.join(tgts)}")
    else:
        irrel.append(short)
print("-" * 78)
for s in irrel:
    print(f"[차폐 X] {s}")
print("-" * 78)
print(f"합계: 경계 차폐 {len(rel)} · 무관 {len(irrel)} / 유리 {len(glass)}")
