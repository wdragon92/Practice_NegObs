#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""h67_yield.py — sceneH6/H7 프로브의 **실측 strict-H 수율**을 계획 §3.5 기대치와 대조한다.

입력  labels JSON (labeler.py 산출) · 대상 라운드 쌍
산출  씬별 tier 분포 · strict-H 수율 · 계획 대비 pro-rata 비율 · VG-datum 3층 · 트윈 포즈 일치

사용
    PY=/home/vislab/miniconda3/envs/env_seg/bin/python
    cd experiments/mainrun_0819/code/labeling
    $PY labeler.py --on-round  $D/260823_v3p5_h67probe_A \
                   --off-round $D/260823_v3p5_h67probe_C \
                   --grid gridspec_v1.json \
                   --out $E/annotations/h67_probe_labels.json --workers 4
    python3 experiments/v3_0823/code/h67_yield.py \
            --labels experiments/v3_0823/annotations/h67_probe_labels.json \
            --on dataset/260823_v3p5_h67probe_A --off dataset/260823_v3p5_h67probe_C
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import sys

# 계획 §3.5 의 수율 가정과 씬별 A팔 컷 배분
PLAN = {
    "sceneH6": dict(bands=dict(base=24, H=24, H2=24), a_cuts=72, expect=33.6),
    "sceneH7": dict(bands=dict(base=24, H=24), a_cuts=48, expect=19.2),
}
YIELD_MODEL = dict(H=0.60, base=0.20)      # 계획의 보수적 수율 모형


def variation_of(round_dir, scene):
    hits = glob.glob(os.path.join(round_dir, "*", scene, "variation.json"))
    return json.load(open(hits[0], encoding="utf-8")) if hits else None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", required=True)
    ap.add_argument("--on", required=True)
    ap.add_argument("--off", required=True)
    ap.add_argument("--band", default="H", choices=["H", "base"],
                    help="이 프로브가 뽑은 밴드 — pro-rata 기대치의 기준")
    a = ap.parse_args(argv)

    L = json.load(open(a.labels, encoding="utf-8"))
    frames = L["frames"]
    print("=" * 78)
    print("h67 프로브 — strict-H 실측 대 계획 §3.5 기대")
    print(f"  labels   {a.labels}")
    print(f"  grid     {L['grid'].get('version')} · footprint {L.get('footprint')}")
    print(f"  tau      {L.get('tau_strict')}")
    if L.get("warnings"):
        print(f"  warnings {len(L['warnings'])}: {L['warnings'][:4]}")
    print("=" * 78)

    by = collections.defaultdict(list)
    for k, v in frames.items():
        arm, scene, fn = k.split("/", 2)
        by[(arm, scene)].append((fn, v))

    ok_all = True
    for scene in sorted({s for _, s in by}):
        on = by.get(("on", scene), [])
        off = by.get(("off", scene), [])
        if not on:
            print(f"\n[{scene}] on팔 프레임 0 — 라벨 실패")
            ok_all = False
            continue
        tiers = collections.Counter(v["tier_strict"] for _, v in on)
        n = len(on)
        n_h = tiers.get("H", 0)
        p_h = n_h / n
        plan = PLAN.get(scene, dict(expect=0.0, a_cuts=n))
        pro = YIELD_MODEL[a.band]
        gate = 0.60 * pro                       # "pro-rata 기대의 60 % 미만이면 개정"
        print(f"\n[{scene}]  n_on={n}  n_off={len(off)}")
        print("  tier 분포 : " + " · ".join(f"{k}={v}" for k, v in sorted(tiers.items())))
        print(f"  strict-H  : {n_h}/{n} = **{p_h:.3f}**  "
              f"(계획 {a.band} 밴드 수율 가정 {pro:.2f} · 게이트 {gate:.2f})")
        print(f"  판정      : " + ("통과 — 계획 가정 이상" if p_h >= pro else
                                   "통과 — 게이트(60 %) 이상, 가정 미달"
                                   if p_h >= gate else "**미달 — 씬 기하 개정 필요**"))
        if p_h < gate:
            ok_all = False
        # 계획 밴드 배분으로 외삽한 A팔 기대
        pb = plan.get("bands", {})
        if pb:
            est = sum(cnt * (p_h if b != "base" else min(p_h, 1.0))
                      for b, cnt in pb.items())
            print(f"  외삽      : A팔 {plan['a_cuts']}컷 → strict-H ≈ {est:.1f} "
                  f"(계획 기대 {plan['expect']}) · 배분 {pb}")
            print("              ※ 이 외삽은 base 밴드에 H 밴드 수율을 그대로 쓴 **상한**이다 — "
                  "base 는 근거리 컷이 섞여 실제로는 낮다(씬 파일의 CPU 모형 참조).")
        # raw_vis 요약 — H 가 왜 깨졌는지 한 줄로
        vis = [(fn, v["raw_vis"], v["cam"] if "cam" in v else None)
               for fn, v in on if v["tier_strict"] != "H"]
        for fn, rv, _ in vis[:6]:
            print(f"    non-H {fn}: int_px={rv['int_px']} edge_vis={rv['edge_visible']} "
                  f"edge_proj={rv['edge_projected']} ratio={rv['edge_ratio']}")

        # VG-datum 3층 — 트윈 쌍의 `cam.ground_z` 차
        von = variation_of(a.on, scene)
        vof = variation_of(a.off, scene)
        if von and vof:
            co = {c["file"]: c for c in von["cuts"]}
            cf = {c["file"]: c for c in vof["cuts"]}
            ex = tol = fail = 0
            worst = 0.0
            for f, c in co.items():
                if f not in cf:
                    continue
                d = abs(c["cam"]["ground_z"] - cf[f]["cam"]["ground_z"])
                worst = max(worst, d)
                if d < 1e-6:
                    ex += 1
                elif d <= 0.02:
                    tol += 1
                else:
                    fail += 1
            print(f"  VG-datum  : datum_exact {ex} · datum_tol {tol} · "
                  f"datum_fail {fail} · 최대 |Δground_z| {worst:.6f} m")
            if fail:
                ok_all = False
            # VG-10 포즈 게이트 (5키 < 1e-6)
            bad = []
            for f, c in co.items():
                if f not in cf:
                    continue
                for k in ("d", "h_rel", "yaw", "pitch", "roll", "hfov"):
                    if abs(c["cam"][k] - cf[f]["cam"][k]) > 1e-6:
                        bad.append((f, k))
            print(f"  VG-10 포즈: 불일치 {len(bad)}건" + (f" {bad[:3]}" if bad else " · OK"))
            if bad:
                ok_all = False
            # VG-08 세그 사이드카
            seg = sum(1 for c in von["cuts"] if c.get("idseg"))
            print(f"  VG-08 세그: {seg}/{len(von['cuts'])} 컷에 .idseg.npz · "
                  f"fetch={sorted({c.get('idseg_fetch') for c in von['cuts']})}")
            if seg != len(von["cuts"]):
                ok_all = False

        # VG-void — heightmap 커버리지
        for tag, rd in (("on", a.on), ("off", a.off)):
            hm = glob.glob(os.path.join(rd, "*", scene, "heightmap_meta.json"))
            if hm:
                m = json.load(open(hm[0], encoding="utf-8"))
                cov = m["n_finite"] / m["n_total"]
                print(f"  VG-void {tag:3s}: 커버리지 {cov:.4f} "
                      f"({m['n_finite']}/{m['n_total']}) · z [{m['z_min']}, {m['z_max']}]")
                if cov < 1.0:
                    ok_all = False

        # 발자국 규모
        fp = next((v["footprint"] for _, v in on), None)
        if fp:
            print(f"  발자국    : cells_raw {fp['cells_raw']} · cells_kept "
                  f"{fp['cells_kept']} · max_diff {fp['max_diff']} m")

    print("\n" + "=" * 78)
    print("종합 판정: " + ("통과" if ok_all else "미달 항목 있음"))
    print("=" * 78)
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
