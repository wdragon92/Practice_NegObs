#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w0_rimpact.py — VG-CLS 결과가 §4.4.4 키별 r에 미치는 영향.

`build_render_plan.py:444 per_key()`의 정의를 **그대로** 옮겨 세 정책을 비교한다.
  P0 계획 가정 (maximal)  — s20/R만 빼고 전 키 제거 가능
  P1 VG-CLS 확정만        — 그 판정표가 **장식으로 판정한 쌍만** 제거 (계획 §1.2 문면)
  P2 판정불가를 장식으로  — 판정불가가 전부 장식으로 풀렸을 때의 상한

인자 (2026-08-23 확장 · D72 ②):
  --cls <path>   판정 원장 (기본 w0_cuecls.json).
                 W1-D 재판정 뒤에는 `w1d_cuecls.json`을 넣는다. 그때의 **P1이
                 확정 정책**이고 P2는 (판정불가가 남아 있다면) 그 상한이다.
"""
import argparse
import collections
import json
import math
import os
import sys

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V3 = os.path.join(REPO, "experiments/v3_0823")
KEYS = ("R", "Ta", "N", "T", "Sg", "V")
CUE2KEY = {"cue_railing": "R", "cue_tactile": "Ta", "cue_nosing": "N",
           "cue_material_break": "T", "cue_sign": "Sg", "cue_scene_dressing": "V"}

_ap = argparse.ArgumentParser()
_ap.add_argument("--cls", default=os.path.join(V3, "w0_cuecls.json"))
_args = _ap.parse_args()

plan = json.load(open(os.path.join(V3, "render_plan_v3.json"), encoding="utf-8"))
cls = json.load(open(_args.cls, encoding="utf-8"))
print(f"[rimpact] 판정 원장 = {os.path.relpath(_args.cls, REPO)}")

verdict = {(r["scene"], r["cue"]): r["verdict"] for r in cls["pairs"]}
for p in cls["prior_rulings"]:
    verdict[(p["scene"], p["cue"])] = p["verdict"]

# 모집단은 `build_render_plan.py:387`과 **동일**하게 train+val로 잡는다.
tr = [s for s in plan["scenes"] if s.get("role") in ("train", "val")]


# ONWIRED 대장은 재구성하지 않고 계획 정본에서 **그대로 가져온다**
# (build_render_plan.py:90 — 재구성하면 §4.4.4 표와 비교가 성립하지 않는다).
sys.path.insert(0, os.path.join(V3, "code"))
from build_render_plan import ONWIRED, onwired            # noqa: E402


def phi(a, b, c, d):
    den = math.sqrt((a + b) * (c + d) * (a + c) * (b + d))
    return 0.0 if den == 0 else (a * d - b * c) / den


def removable(policy, scene, key):
    """B팔이 그 씬에서 그 키를 끌 수 있나."""
    if policy == "P0":
        return not (scene == "scene20" and key == "R")
    cue = [c for c, k in CUE2KEY.items() if k == key][0]
    v = verdict.get((scene, cue))
    if v is None:
        # W0이 재지 않은 (씬, 키): 신규 씬은 표준 장비라 제거 가능,
        # 기존 씬의 미측정 키(주로 Sg)는 계획 가정을 유지한다.
        return not (scene == "scene20" and key == "R")
    if v == "장식":
        return True
    if v == "구조물":
        return False
    return policy == "P2"          # 판정불가


def per_key(policy):
    out = {}
    for k in KEYS:
        t = collections.Counter()
        for s in tr:
            if k not in onwired(s["scene"]):
                continue
            for arm, v in s["arms"].items():
                f = v["frames"]
                haz = arm in ("A", "B")
                if arm == "D":
                    x = 0
                elif arm == "B":
                    x = 0 if removable(policy, s["scene"], k) else 1
                else:
                    x = 1
                t[(haz, x)] += f
        a, b = t[(True, 1)], t[(True, 0)]
        c, d = t[(False, 1)], t[(False, 0)]
        out[k] = dict(a=a, b=b, c=c, d=d, r=round(abs(phi(a, b, c, d)), 4))
    return out


P = {p: per_key(p) for p in ("P0", "P1", "P2")}
print("| 키 | 단서 | 씬 수 | 계획 가정 P0 | **VG-CLS 확정 P1** | 분쟁 해제 시 P2 |")
print("|---|---|---:|---:|---:|---:|")
NAME = {"R": "`cue_railing`", "Ta": "`cue_tactile`", "N": "`cue_nosing`",
        "T": "`cue_material_break`", "Sg": "`cue_sign`", "V": "`cue_scene_dressing`"}
for k in KEYS:
    n = sum(1 for s in tr if k in onwired(s["scene"]))
    m = "✅" if P["P1"][k]["r"] <= 0.2 else "❌"
    print(f"| **{k}** | {NAME[k]} | {n} | {P['P0'][k]['r']:.4f} | "
          f"**{P['P1'][k]['r']:.4f}** {m} | {P['P2'][k]['r']:.4f} |")
print()
for p in ("P0", "P1", "P2"):
    bad = [k for k in KEYS if P[p][k]["r"] > 0.2]
    print(f"{p}: r>0.2 인 키 {bad or '없음'} · 최대 r "
          f"{max(P[p][k]['r'] for k in KEYS):.4f}")
print("\na/b/c/d (P1):")
for k in KEYS:
    v = P["P1"][k]
    print(f"  {k:3s} {v['a']}/{v['b']}/{v['c']}/{v['d']}")
