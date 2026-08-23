#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w2_val_yield.py — **val strict-H ≥ 30** 회계 (RENDER_PLAN_V3 §3.5 · RT-B gap #2).

계획 §3.5 의 요구는 하나다 — *"DZ §4.3-3 의 선택지표 수리는 val strict-H ≥ 30 을 전제한다"*.
교정 GT 기준 현 val strict-H 는 **6**(scene20 단독)이고, 그것이 D52 가 잡은 "6문제 시험"의
물리적 정체다. sceneH6·H7 이 그 유일한 공급원이다.

이 스크립트는 **실측만** 한다:
  · A팔 strict-H (밴드별·씬별) — 선택지표의 H 항 분모에 들어가는 수
  · paired-H (A·B 둘 다 strict-H) — 참고 병기
  · 계획 §3.5 기대치(H6 33.6 · H7 19.2)와 대조, 수율 모형 붕괴 시나리오 재계산

    python3 experiments/v3_0823/code/w2_val_yield.py
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
V3 = os.path.join(REPO, "experiments", "v3_0823")
ANN = os.path.join(V3, "annotations")

# (tag, stamp, band, scenes) — run_w2_h67.sh 의 밴드 draw 와 1:1
ROUNDS = [("base", "260824_v3w2_h67base", "base", ["sceneH6", "sceneH7"]),
          ("h", "260824_v3w2_h67h", "H", ["sceneH6", "sceneH7"]),
          ("h2", "260824_v3w2_h67h2", "H", ["sceneH6"])]
# 계획 §3.5 표
PLAN_EXPECT = {"sceneH6": 33.6, "sceneH7": 19.2}
PLAN_ACUTS = {"sceneH6": 72, "sceneH7": 48}
YIELD_MODEL = dict(H=0.60, base=0.20)
# 계획 §3.5 표의 기존 공급원 — **본 웨이브에서 재측정하지 않는다**(계획 등재 실측치).
SCENE20_STRICT_H = 6
TARGET = 30


def load_tiers(path, arm="on"):
    if not os.path.isfile(path):
        return None
    L = json.load(open(path, encoding="utf-8"))
    out = collections.defaultdict(dict)
    for k, v in L["frames"].items():
        a, scene, fn = k.split("/", 2)
        if a == arm:
            out[scene][fn] = v.get("tier_strict")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(V3, "w2_val_yield.json"))
    a = ap.parse_args(argv)

    rows, missing = [], []
    for tag, stamp, band, scenes in ROUNDS:
        ta = load_tiers(os.path.join(ANN, f"w2_{tag}_ac_labels.json"), "on")
        tb = load_tiers(os.path.join(ANN, f"w2_{tag}_bd_labels.json"), "on")
        if ta is None:
            missing.append(tag)
            continue
        for sc in scenes:
            A = ta.get(sc, {})
            B = (tb or {}).get(sc, {})
            n = len(A)
            hA = sum(1 for v in A.values() if v == "H")
            hB = sum(1 for v in B.values() if v == "H")
            ph = sum(1 for f, v in A.items() if v == "H" and B.get(f) == "H")
            rows.append(dict(tag=tag, stamp=stamp, band=band, scene=sc, n_A=n,
                             strict_H_A=hA, strict_H_B=hB, paired_H=ph,
                             yield_A=(hA / n if n else None),
                             model=YIELD_MODEL[band],
                             tiers=dict(collections.Counter(A.values()))))

    print("=" * 84)
    print("W2-lite val strict-H 회계 — 계획 §3.5")
    print("=" * 84)
    if missing:
        print(f"  [주의] 라벨 미착지 밴드: {missing}")
    print(f"\n{'밴드':<6}{'씬':<10}{'n_A':<6}{'strict-H(A)':<13}{'수율':<9}"
          f"{'모형':<7}{'게이트(60%)':<12}{'strict-H(B)':<13}{'paired-H':<9}")
    for r in rows:
        gate = 0.60 * r["model"]
        mark = ("가정이상" if r["yield_A"] >= r["model"] else
                "게이트통과" if r["yield_A"] >= gate else "**미달**")
        print(f"{r['tag']:<6}{r['scene']:<10}{r['n_A']:<6}{r['strict_H_A']:<13}"
              f"{r['yield_A']:<9.3f}{r['model']:<7.2f}{mark:<12}"
              f"{r['strict_H_B']:<13}{r['paired_H']:<9}")

    by_scene = collections.defaultdict(lambda: dict(n=0, h=0, ph=0))
    for r in rows:
        s = by_scene[r["scene"]]
        s["n"] += r["n_A"]; s["h"] += r["strict_H_A"]; s["ph"] += r["paired_H"]

    print(f"\n{'씬':<10}{'A컷':<7}{'strict-H':<11}{'계획 기대':<11}{'대비':<8}{'paired-H':<9}")
    tot_h = tot_n = tot_ph = 0
    for sc in ["sceneH6", "sceneH7"]:
        s = by_scene.get(sc)
        if not s:
            continue
        exp = PLAN_EXPECT[sc]
        print(f"{sc:<10}{s['n']:<7}{s['h']:<11}{exp:<11.1f}"
              f"{s['h'] / exp:<8.2f}{s['ph']:<9}")
        tot_h += s["h"]; tot_n += s["n"]; tot_ph += s["ph"]

    total = tot_h + SCENE20_STRICT_H
    print(f"\n{'합계 (H6+H7)':<10} A컷 {tot_n} · strict-H **{tot_h}** · paired-H {tot_ph}")
    print(f"{'+ scene20 (계획 등재 실측)':<10} {SCENE20_STRICT_H}")
    print(f"{'⇒ val strict-H 총계':<10} **{total}**  (목표 ≥ {TARGET}) — "
          + ("**충족**" if total >= TARGET else "**미달 — 톱업 발동**")
          + f" · 여유 {total / TARGET:.2f} 배")
    print(f"   계획 §3.5 기대 58.8 대비 {total / 58.8:.2f} 배")
    print("\n   ※ 판정 분모는 **A팔 컷**이다(계획 §3.5 표의 'A팔 컷' 열). "
          "paired-H 는 참고 병기이며 선택지표 H 항의 분모가 아니다.")

    doc = dict(doc="val strict-H ≥ 30 회계 (RENDER_PLAN_V3 §3.5)",
               target=TARGET, rounds=rows,
               by_scene={k: dict(v) for k, v in by_scene.items()},
               scene20_strict_H=SCENE20_STRICT_H,
               total_strict_H=total, plan_expect_total=58.8,
               ok=bool(total >= TARGET), missing_rounds=missing)
    json.dump(doc, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\n[out] {a.out}")
    return 0 if total >= TARGET and not missing else 1


if __name__ == "__main__":
    sys.exit(main())
