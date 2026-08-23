#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w1b_tables.py — W1B_REPORT의 측정 표를 기계 산출물에서 그대로 찍어 낸다.

손으로 옮겨 적으면 반드시 어딘가에서 숫자가 어긋난다. 표는 `w1b_verify.json`·
`w1b_rimpact.json`·`w1b_fuse_audit.json`에서만 읽고, 이 파일이 찍은 것을
보고서에 붙인다.

사용:  python3 experiments/v3_0823/code/w1b_tables.py > /tmp/w1b_tables.md
"""
import json
import os

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V3 = os.path.join(REPO, "experiments/v3_0823")


def J(n):
    p = os.path.join(V3, n)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def n(x):
    return "—" if x is None else (f"{x:,}" if isinstance(x, int) else str(x))


V = J("w1b_verify.json")
R = J("w1b_rimpact.json")
F = J("w1b_fuse_audit.json")

# ---------- §1 렌더 회계 ----------------------------------------------------
print("### 1.1 컷 회계\n")
print("| 라운드 | 밴드 | 씬 | 컷 | 시드 | 카메라 밴드 |")
print("|---|---|---:|---:|---:|---|")
SEED = dict(base=20260819, h=20260820, e=20260820, e2=20260821)
CAM = dict(base="—", h="d[6,12] h[0.25,1.0]", e="d[6,12] h[1.2,1.9]",
           e2="d[4,9] h[0.3,0.9]")
tot = 0
for r, v in V["rounds"].items():
    b = v["band"]
    print(f"| `{r}` | {b} | {v['n_scenes']} | **{v['png']}** | {SEED[b]} | {CAM[b]} |")
    tot += v["png"]
a = V["accounting"]
print(f"| **소계** | | | **{tot}** | | |")
print(f"| `260826_v3w1_lib_B_smoke` | base | 15 | 15 | 20260819 | — (씬당 1컷) |")
print()
print(f"**예산 {a['planned_cuts']}컷 = 계획 표 B팔 {a['plan_table_b_arm']}컷 − "
      f"D74 ⑤ 스킵 {a['skipped_d74']['cuts']}컷** "
      f"({', '.join(f'{k} {v}' for k, v in a['skipped_d74']['scenes'].items())})\n")
print(f"in-process **{a['in_process_gpu_h']} GPU-h** · 디스크 "
      f"**{sum(v['disk_gb'] for v in V['rounds'].values()):.2f} GB**\n")

# ---------- §3 VG-01 --------------------------------------------------------
v1 = V["vg_01"]
print("\n### 3.1 VG-01 — 씬×밴드별\n")
print("| 밴드 | 씬 | 레버 | hm 바이트 | AABB ≥0.3 | fp 대칭차 | cells_raw A | B | Δ | polar_gt 동일 | 계기 A/B | 층 |")
print("|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---|")
for r in V["scenes"]:
    if "vg01_bytes" not in r:
        continue
    lv = r.get("vg01_labeler") or {}
    cr = lv.get("cells_raw") or {}
    hd = r.get("hm_diff") or {}
    ab = hd.get("aabb") or {}
    hs = lv.get("hm_source") or {}
    lev = ",".join((r.get("lever") or {}).get("levers") or [])
    print(f"| {r['band']} | {r['scene']} | {lev} | "
          f"{'동일' if r['vg01_bytes']['hm_bytes_equal'] else '다름'} | "
          f"{n(ab.get('n_cells_diff_ge_hz'))} | {n(hd.get('fp_symdiff'))} | "
          f"{n(cr.get('A'))} | {n(cr.get('B'))} | {n(cr.get('delta'))} | "
          f"{lv.get('polar_gt_equal')}/{lv.get('n_frames')} | "
          f"{hs.get('A')}/{hs.get('B')} | **{r.get('vg01_tier')}** |")
print()
print(f"**{v1['n_pass']}/{v1['n_pairs']} 통과** · 층 {v1['tiers']} · "
      f"프레임 `polar_gt` 동일 **{v1['n_frames_gt_equal']}/{v1['n_frames']}** · "
      f"높이맵 바이트 동일 {v1['n_hm_bytes_equal']}/{v1['n_pairs']}\n")
if v1["quarantine"]:
    print("**격리**: " + ", ".join(f"{q['scene']}/{q['band']}" for q in v1["quarantine"]))
else:
    print("**격리 없음**")

ct = V.get("corpus_tie") or {}
print(f"\n**코퍼스 이전**: 구off 기준 A 재라벨이 `dataset_manifest_v2corr`의 "
      f"`polar_gt`를 **{ct.get('n_reproduce')}/{ct.get('n_pairs')}** 씬×밴드에서 완전 재현.")
for d in ct.get("deviating", []):
    print(f"  - {d['scene']} {d['band']}: {d['n_equal']}/{d['n_compared']} "
          f"(label_source {d['label_source']})")

# ---------- §4 VG-datum / VG-10 --------------------------------------------
vd = V["vg_datum"]
print("\n\n### 4.1 VG-datum (A,B)\n")
print(f"컷 3층 {vd['cut_tiers']} · **쌍 생존 {vd['pair_survival']} "
      f"({vd['pair_survival_rate']:.4f})** · 컷 생존 {vd['cut_survival']}\n")
if vd["drift"]:
    print("| 씬 | 밴드 | 판정 | max \\|Δground_z\\| | exact/tol/fail |")
    print("|---|---|---|---:|---|")
    for d in vd["drift"]:
        t = d["tiers"]
        print(f"| {d['scene']} | {d['band']} | {d['verdict']} | {d['ground_z_drift_max']} | "
              f"{t['datum_exact']}/{t['datum_tol']}/{t['datum_fail']} |")
print(f"\n**격리**: {vd['quarantine'] or '없음'}")
print(f"\n**VG-10**: max pose delta **{V['vg_10']['pose_delta_max']}** · "
      f"0이 아닌 쌍 {V['vg_10']['n_pairs_nonzero']}")

# ---------- §5 VG-08 --------------------------------------------------------
v8 = V["vg_08"]
print("\n\n### 5.1 VG-08 · per-cut 세그 판별성\n")
print(f"**{v8['n_distinct']}/{v8['n_pairs']} 통과** · 고유 마스크 {v8['n_unique_masks']} / "
      f"고유 포즈 {v8['n_poses']} / 컷 {v8['n_cuts']} · 누락 사이드카 "
      f"{v8['n_missing_sidecars']} · **stale 지문 {v8['n_stale_signature']}** · "
      f"포즈 간 충돌 {v8['n_pose_collisions']} · fetch 경로 {v8['fetch_paths']}\n")
if v8.get("over_discriminating"):
    print("| 씬 | 밴드 | 마스크/포즈 | 가시 프림 경로 | 경로 집합 | 경로별 픽셀 수 |")
    print("|---|---|---:|---:|---|---|")
    for o in v8["over_discriminating"]:
        pn = (o.get("prim_normalized") or [{}])[0]
        print(f"| {o['scene']} | {o['band']} | {o['n_unique_masks']}/{o['n_poses']} | "
              f"{n(pn.get('n_paths_visible'))} | "
              f"{'동일' if pn.get('prim_path_sets_equal') else '다름'} | "
              f"{'**동일**' if pn.get('per_prim_pixel_counts_equal') else '다름'} |")

# ---------- §6 레버 발화 ----------------------------------------------------
lf = V.get("lever_firing") or {}
print("\n\n### 6.1 레버 발화\n")
print(f"**{lf.get('n_fired')}/{lf.get('n_pairs')} 씬×밴드에서 발화 실증**\n")
print("| 밴드 | 씬 | 레버 | Δn_prims | RGB 평균 \\|Δ\\| (LSB) | 변화 픽셀 비율 |")
print("|---|---|---|---:|---:|---:|")
for r in lf.get("rows", []):
    print(f"| {r['band']} | {r['scene']} | {','.join(r['levers'] or [])} | "
          f"{n(r['d_prims'])} | {r['rgb_mean_abs']} | {r['rgb_frac_changed']} |")

# ---------- §7 키별 r -------------------------------------------------------
if R:
    print("\n\n### 7.1 키별 \\|r\\|\n")
    P = R["policies"]
    KEYS = ("R", "Ta", "N", "T", "Sg", "V")
    NAME = {"R": "`cue_railing`", "Ta": "`cue_tactile`", "N": "`cue_nosing`",
            "T": "`cue_material_break`", "Sg": "`cue_sign`",
            "V": "`cue_scene_dressing`"}
    print("| 키 | 단서 | 씬 수 | W1-D P1 (계획 B팔) | **PB 실측** | PB(격리 반영) | "
          "PB(hazgate 모집단) | PB+T (사각지대 수리 가정) |")
    print("|---|---|---:|---:|---:|---:|---:|---:|")
    for k in KEYS:
        m = "✅" if P["PB_gated"][k]["r"] <= 0.2 else "❌"
        m2 = "✅" if P["PB_plusT"][k]["r"] <= 0.2 else "❌"
        print(f"| **{k}** | {NAME[k]} | {P['P1_plan'][k]['n_scenes']} | "
              f"{P['P1_plan'][k]['r']:.4f} | **{P['PB_asbuilt'][k]['r']:.4f}** | "
              f"**{P['PB_gated'][k]['r']:.4f}** {m} | "
              f"{P['PB_hazgate'][k]['r']:.4f} ({P['PB_hazgate'][k]['n_scenes']}씬) | "
              f"{P['PB_plusT'][k]['r']:.4f} {m2} |")
    print()
    for p in ("P1_plan", "PB_asbuilt", "PB_gated", "PB_plusT"):
        bad = [k for k in KEYS if P[p][k]["r"] > 0.2]
        print(f"- `{p}`: r > 0.2 인 키 **{bad or '없음'}** · 최대 r "
              f"{max(P[p][k]['r'] for k in KEYS):.4f}")
    print(f"\n**D74 ⑤ '스킵해도 r 불변' 검산** — 스킵 168컷을 되살렸을 때의 Δr: "
          f"{R['d74_skip_check']['delta_r']}")
    print("\n**a/b/c/d (PB_gated)**: " + " · ".join(
        f"{k} {P['PB_gated'][k]['a']}/{P['PB_gated'][k]['b']}/"
        f"{P['PB_gated'][k]['c']}/{P['PB_gated'][k]['d']}" for k in KEYS))

# ---------- 계기 ------------------------------------------------------------
if F:
    print("\n\n### 계기 결정 (w1b_fuse_audit)\n")
    print(f"기록: {F['wrote']}\n")
    print("| 밴드 | 씬 | 코퍼스 A팔 융합 | 처분 |")
    print("|---|---|---|---|")
    for r in F["rows"]:
        if "error" in r and r.get("action") is None:
            continue
        if r.get("action") in (None, "keep aabb"):
            continue
        print(f"| {r['band']} | {r['scene']} | {r.get('corpus_on_fused')} | "
              f"{r.get('action')} |")
    if F.get("flagged"):
        print("\n**계기 불일치 플래그(미기록)**: " +
              ", ".join(f"{x['scene']}({x['why']} med {x['med_abs']} p90 {x['p90_abs']})"
                        for x in F["flagged"]))
