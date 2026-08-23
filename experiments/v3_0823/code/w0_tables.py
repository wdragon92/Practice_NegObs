#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w0_tables.py — w0_cuecls.json → W0_CUECLS.md 본문 표(마크다운) 생성."""
import json
import os

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
J = os.path.join(REPO, "experiments/v3_0823/w0_cuecls.json")
d = json.load(open(J, encoding="utf-8"))
rows = d["pairs"]

ORDER = ["cue_railing", "cue_nosing", "cue_tactile", "cue_material_break",
         "cue_scene_dressing"]


def f(x, n=4, dash="—"):
    return dash if x is None else (f"{x:.{n}f}" if isinstance(x, float) else str(x))


print("### 표 1 — 쌍별 실측 (39쌍)\n")
print("| 씬 | cue | 결속 | dz_max (m) | Δ높이맵 셀 | n_prims A→B | cells_raw A→B | Δ풋프린트 | "
      "polar_gt 상이 | Δground_z (m) | RGB 평균\\|Δ\\| | 단서 궤적 (Δcue∩fp_A) | 검정1 | 검정2 | **판정** |")
print("|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|")
for cue in ORDER:
    for r in [x for x in rows if x["cue"] == cue]:
        v = r["verdict"] + (f"({r['subtype']})" if r.get("subtype") else "")
        gz = r["datum"]["ground_z_drift_max"] if r.get("datum") else None
        np_ = (f"{r.get('n_prims_a')}→{r.get('n_prims_b')}"
               if r.get("n_prims_a") is not None else "—")
        cr = (f"{r['cells_raw_a']}→{r['cells_raw_b']}"
              if r.get("cells_raw_a") is not None else "—")
        dfp = f"{r['d_cells_raw']:+d}" if r.get("d_cells_raw") is not None else "—"
        pg = (f"{r['polar_gt_n_diff']}/{r['polar_gt_n_cmp']}"
              if r.get("polar_gt_n_cmp") is not None else "—")
        lo = r.get("locus") or {}
        lc = f"{lo.get('locus','—')} ({lo.get('dcue_in_fpA','—')})"
        print(f"| {r['scene']} | `{cue}` | {r.get('bond','?')} | {f(r.get('dz_max'))} | "
              f"{f(r.get('hm_cells_changed'))} | {np_} | {cr} | {dfp} | {pg} | "
              f"{f(gz,6)} | {f(r.get('rgb_mean_abs_lsb'),3)} | {lc} | "
              f"{r.get('verdict_t1')} | {r.get('verdict_t2')} | **{v}** |")

print("\n### 표 2 — VG-datum 3층 (전 39쌍)\n")
print("| 씬 | cue | exact | tol | fail | max \\|Δground_z\\| | 최대 포즈차 | 판정 |")
print("|---|---|---:|---:|---:|---:|---:|---|")
for cue in ORDER:
    for r in [x for x in rows if x["cue"] == cue and x.get("datum")]:
        t = r["datum"]["tiers"]
        print(f"| {r['scene']} | `{cue}` | {t['datum_exact']} | {t['datum_tol']} | "
              f"{t['datum_fail']} | {r['datum']['ground_z_drift_max']:.6f} | "
              f"{r['datum']['pose_delta_max']:.6f} | {r['datum']['datum_verdict']} |")

print("\n### 표 3 — 씬별 확정 B 레버\n")
print("| 씬 | 장식 확정 (레버 가능) | 구조물/판정불가 (금지) |")
print("|---|---|---|")
scenes = sorted({r["scene"] for r in rows} |
                {p["scene"] for p in d["prior_rulings"]})
for s in scenes:
    good = sorted({r["cue"] for r in rows if r["scene"] == s and r["verdict"] == "장식"} |
                  {p["cue"] for p in d["prior_rulings"]
                   if p["scene"] == s and p["verdict"] == "장식"})
    bad = sorted({r["cue"] for r in rows if r["scene"] == s and r["verdict"] != "장식"} |
                 {p["cue"] for p in d["prior_rulings"]
                  if p["scene"] == s and p["verdict"] == "구조물"})
    print(f"| {s} | {', '.join('`'+c+'`' for c in good) or '—'} | "
          f"{', '.join('`'+c+'`' for c in bad) or '—'} |")

print("\n### 표 4 — 토글 금지 목록\n")
print("| 씬 | cue | 사유 |")
print("|---|---|---|")
for e in d["toggle_forbidden"]:
    m = [r for r in rows if r["scene"] == e["scene"] and r["cue"] == e["cue"]]
    if m:
        r = m[0]
        why = (f"Δ풋프린트 {r['d_cells_raw']:+d}셀 · polar_gt "
               f"{r['polar_gt_n_diff']}/{r['polar_gt_n_cmp']} 상이"
               if r["verdict"] == "구조물" else f"판정불가({r.get('reason')})")
    else:
        p = [x for x in d["prior_rulings"]
             if x["scene"] == e["scene"] and x["cue"] == e["cue"]][0]
        why = f"{p['note']} ({p['source']})"
    print(f"| {e['scene']} | `{e['cue']}` | {why} |")

print("\n판정 집계:", d["verdict_counts"])
print("금지 목록 크기:", len(d["toggle_forbidden"]))
