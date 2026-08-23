#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w1d_verify.py — W1 D팔 착지 검사 (CPU only).

RENDER_PLAN_V3 §4.2(회계) · §6.1(VG-02 · VG-08 · VG-10 · VG-datum) · §1.4(VG-04)
W0_CUECLS §3(참조 cue-비대칭) · DECISIONS D72.

무엇을 검사하나
---------------
1. **렌더 회계** — 라운드×씬 컷 수 · s/컷 · GPU-h · 디스크. 계획 예산과 대조.
2. **VG-08 세그 사이드카** — 전 컷 `.idseg.npz` 존재.
3. **VG-datum (A,D)** — 컷별 |Δ`ground_z`| 3층 분리
   (`datum_exact` <1e-6 · `datum_tol` ≤0.02 m · `datum_fail` >0.02 m).
   `datum_fail` 쌍은 **격리**하고 쌍 생존율을 인쇄한다.
4. **VG-10 (포즈)** — 같은 컷의 `d·h_rel·yaw·pitch·roll·hfov` + `cam.eye` 최대차.
5. **VG-02 (D팔 전 칸 음성)** — 아래 "왜 두 갈래로 재나" 참조.
6. **VG-04 실증** — D팔 높이맵 sha256이 정본 구off와 같은 씬은 어디인가.
   계획 §1.4는 이것을 `hazgate.json` 문면(CPU)으로만 판정했다. D팔이 실재하는
   지금은 **바이트로** 답할 수 있다.

왜 D팔 "전 칸 음성"을 두 갈래로 재나 — 이 파일에서 가장 중요한 문단
---------------------------------------------------------------------
라벨러 발자국은 `fp = {z_off − z_on ≥ 0.3}`이다. D팔의 정직한 z_off는
"D의 단서 구성(=없음) + 낙차만 있는 면", 즉 **B팔**이고 B는 아직 없다.
D를 D 자신에 대고 재면 diff가 항등적으로 0이라 판정이 순환한다
(라벨러 `label_scene`의 `same` 분기 · `arm=="off"` → `tier="off"`).
D를 구off에 대고 재면 구off가 **cue-비대칭**이라(자유결속 단서를 남긴다)
단서를 지운 자리마다 `z_구off − z_D ≥ 0.3`이 되어 **위양성**이 쏟아진다 —
W0_CUECLS §3이 잰 바로 그 기전이다.

⇒ 그래서 이렇게 나눈다.

  (ㄱ) **구조적 진술 (VG-02 문면)**: 생산 짝 (B,D)에서 D는 off팔이므로
       `polar_gt`는 구성상 올-제로, `tier = "off"`. 계획의 VG-02는 이 진술이며
       본 파일은 그것을 그대로 기록한다 — 측정이 아니라 구성이다.
  (ㄴ) **실질 결함 사냥 (본 파일의 판정)**: "위험 토글이 실제로 낙차를
       지웠는가"만 남는다. 정본 코퍼스의 낙차 발자국
       `fp_corpus = {z_구off − z_A ≥ 0.3}` 안에서, D가 **여전히 꺼져 있는** 셀
       `resid = fp_corpus ∩ {z_구off − z_D ≥ 0.3}`를 센다.
       · D가 낙차를 메웠으면 그 셀에서 `z_D ≈ z_구off` → resid = 0.
       · D에 낙차가 남았으면 `z_D ≈ z_A` → resid ≈ fp_corpus.
       `resid`는 단서 제거에 **면역**이다 — 단서는 지면을 올리지 낙차를 파지
       않으므로 `fp_corpus` 밖에서만 움직인다.
       resid > 0 인 씬은 **씬 결함**으로 격리한다.
       프레임 단위로도 인쇄한다: 정본 라벨러의 `polar_cells`를 그대로 빌려
       resid 발자국을 D팔 각 컷의 폴라 그리드에 투영한다(스텝게이트 없이 =
       보수적). 이 값이 전 컷 0이면 **D팔은 전 칸 음성**이다.

사용:  python3 experiments/v3_0823/code/w1d_verify.py
산출:  experiments/v3_0823/w1d_verify.json  (+ stdout 표)
"""
import glob
import hashlib
import json
import os
import sys

import numpy as np

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V3 = os.path.join(REPO, "experiments/v3_0823")
LABDIR = os.path.join(REPO, "experiments/mainrun_0819/code/labeling")
sys.path.insert(0, LABDIR)
import labeler as LB                                            # noqa: E402

GRID = json.load(open(os.path.join(LABDIR, "gridspec_v1.json"), encoding="utf-8"))
HAZ_DEPTH = float(GRID["hazard_depth_m"])
D = "260826_v3w1_lib_D"

# band -> (D round, corpus A round, corpus old-off round, scenes)
BANDS = {
    "base": (D,          "260819_main_on",      "260819_main_off",
             "scene01 scene02 scene03 scene04 scene06 scene08 scene09 scene10 "
             "scene12 scene16 scene17 scene20 scene21 sceneC1 sceneC4 sceneD1 "
             "sceneD2 sceneD3 sceneN1 sceneN2 sceneN4 sceneN5".split()),
    "h":    (f"{D}_h",   "260820_boost_h_on",   "260820_boost_h_off",
             "scene09 scene17".split()),
    "e":    (f"{D}_e",   "260820_boost_e_on",   "260820_boost_e_off",
             "scene03 scene04 scene08 scene09 scene12 scene17 scene20 sceneC1 "
             "sceneC4".split()),
    "e2":   (f"{D}_e2",  "260820_boost_e2_on",  "260820_boost_e2_off",
             "scene03 scene04 scene12 scene20 sceneC4".split()),
}
DATUM_EXACT, DATUM_TOL = 1e-6, 0.02
POSE_KEYS = ("d", "h_rel", "yaw", "pitch", "roll", "hfov")


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def sdir(run, scene):
    g = glob.glob(os.path.join(REPO, "dataset", run, "*", scene, "variation.json"))
    return os.path.dirname(g[0]) if g else None


def cuts_of(d):
    v = json.load(open(os.path.join(d, "variation.json"), encoding="utf-8"))
    cu = v["cuts"]
    cu = list(cu.values()) if isinstance(cu, dict) else cu
    return {c["file"]: c for c in cu}, v


def hm_of(d):
    """라벨러와 **같은 계기**로 읽는다 — `heightmap_fused.npy`가 있으면 그것이 이긴다.

    이걸 틀리면 scene08 같은 씬에서 낙차가 통째로 사라진다(w1d_fuse.py 참조).
    raw AABB는 sha256 대조(VG-04)용으로 따로 읽는다.
    """
    z, geo, src = LB.load_heightmap(d)
    m = json.load(open(os.path.join(d, "heightmap_meta.json"), encoding="utf-8"))
    return z, geo, src, m


def datum_pose(ca, cd):
    common = sorted(set(ca) & set(cd))
    tiers = dict(datum_exact=0, datum_tol=0, datum_fail=0)
    worst, pose_worst, fails = 0.0, 0.0, []
    for f in common:
        a, b = ca[f]["cam"], cd[f]["cam"]
        dz = abs(float(a["ground_z"]) - float(b["ground_z"]))
        t = ("datum_exact" if dz < DATUM_EXACT
             else "datum_tol" if dz <= DATUM_TOL else "datum_fail")
        tiers[t] += 1
        worst = max(worst, dz)
        if t == "datum_fail":
            fails.append(dict(file=f, d_ground_z=round(dz, 6),
                              a_ground_z=round(float(a["ground_z"]), 6),
                              d_arm_ground_z=round(float(b["ground_z"]), 6)))
        pk = max(abs(float(a[k]) - float(b[k])) for k in POSE_KEYS)
        pe = max(abs(float(a["eye"][i]) - float(b["eye"][i])) for i in range(3))
        pose_worst = max(pose_worst, pk, pe)
    return dict(n_cuts=len(common), tiers=tiers,
                ground_z_drift_max=round(worst, 8),
                pose_delta_max=round(pose_worst, 9),
                verdict=("datum_fail" if tiers["datum_fail"]
                         else "datum_tol" if tiers["datum_tol"] else "datum_exact"),
                fail_cuts=fails)


def main():
    out = dict(doc="w1d_verify", version="1.0",
               plan="RENDER_PLAN_V3 §4.2 · §6.1 · §1.4",
               gates=["VG-02", "VG-04", "VG-08", "VG-10", "VG-datum"],
               rounds={}, scenes=[], problems=[])

    # ---------- 1. 렌더 회계 + VG-08 --------------------------------------
    total_cuts = total_sec = 0
    for band, (drun, _a, _o, scs) in BANDS.items():
        root = os.path.join(REPO, "dataset", drun)
        png = len(glob.glob(os.path.join(root, "*", "*", "*.png")))
        dep = len(glob.glob(os.path.join(root, "*", "*", "*.depth.npy")))
        seg = len(glob.glob(os.path.join(root, "*", "*", "*.idseg.npz")))
        hm = len(glob.glob(os.path.join(root, "*", "*", "heightmap.npy")))
        sec = 0.0
        for s in scs:
            d = sdir(drun, s)
            if not d:
                out["problems"].append(f"{drun}/{s}: 렌더 없음")
                continue
            cu, var = cuts_of(d)
            sec += float(var.get("sec_per_cut") or 0) * len(cu)
        gb = sum(os.path.getsize(os.path.join(dp, f))
                 for dp, _, fs in os.walk(root) for f in fs) / 2**30
        out["rounds"][drun] = dict(band=band, n_scenes=len(scs), png=png,
                                   depth=dep, idseg=seg, heightmap=hm,
                                   expected_cuts=24 * len(scs),
                                   in_process_sec=round(sec, 1),
                                   disk_gb=round(gb, 3),
                                   vg08_pass=(seg == png == dep == 24 * len(scs)))
        total_cuts += png
        total_sec += sec
    out["accounting"] = dict(total_cuts=total_cuts,
                             in_process_gpu_h=round(total_sec / 3600, 4))

    # ---------- 2-5. 씬별 검사 -------------------------------------------
    # 높이맵은 씬 프로세스당 1개이고 카메라 밴드는 기하를 바꾸지 않으므로
    # base 밴드의 높이맵 하나로 전 밴드를 대표한다 — 그 사실 자체도 검증한다.
    seen = {}
    for band, (drun, arun, orun, scs) in BANDS.items():
        for s in scs:
            dd, da, do = sdir(drun, s), sdir(arun, s), sdir(orun, s)
            row = dict(scene=s, band=band, d_round=drun, a_round=arun,
                       off_round=orun)
            if not (dd and da and do):
                row["error"] = "missing round dir"
                out["scenes"].append(row)
                out["problems"].append(f"{band}/{s}: 라운드 디렉터리 없음")
                continue
            zd, gd, srcd, md = hm_of(dd)
            za, ga, srca, ma = hm_of(da)
            zo, go, srco, mo = hm_of(do)
            # 라벨러와 같이 D·구off를 A 격자에 맞춘다 (격자가 같으면 no-op)
            zo = LB.align_to(zo, go, ga, za.shape)
            zd = LB.align_to(zd, gd, ga, za.shape)
            row["hm_instrument"] = dict(A=srca, D=srcd, guoff=srco)
            row["n_prims"] = dict(A=ma.get("n_prims"), D=md.get("n_prims"),
                                  guoff=mo.get("n_prims"))
            row["hm_sha"] = dict(A=sha256(os.path.join(da, "heightmap.npy"))[:16],
                                 D=sha256(os.path.join(dd, "heightmap.npy"))[:16],
                                 guoff=sha256(os.path.join(do, "heightmap.npy"))[:16])
            # VG-04 실증: D팔 높이맵 == 정본 구off 높이맵?
            row["vg04_D_equals_guoff"] = row["hm_sha"]["D"] == row["hm_sha"]["guoff"]

            # 밴드 간 높이맵 동일성 (base가 기준)
            key = (s, "hm")
            if key in seen:
                row["hm_same_as_base_band"] = (row["hm_sha"]["D"] == seen[key])
                if not row["hm_same_as_base_band"]:
                    out["problems"].append(
                        f"{band}/{s}: D 높이맵이 base 밴드와 다르다 — 기하가 밴드에 의존")
            else:
                seen[key] = row["hm_sha"]["D"]
                row["hm_same_as_base_band"] = None

            # ---- VG-datum + VG-10 (A,D) --------------------------------
            ca, _ = cuts_of(da)
            cd, _ = cuts_of(dd)
            row["datum"] = datum_pose(ca, cd)

            # ---- VG-02 실질 검사: 낙차 잔차 -----------------------------
            fin = np.isfinite(za) & np.isfinite(zo) & np.isfinite(zd)
            fp_corpus = fin & ((zo - za) >= HAZ_DEPTH)
            still_low = fin & ((zo - zd) >= HAZ_DEPTH)
            resid = fp_corpus & still_low
            row["negative_gt"] = dict(
                fp_corpus_cells=int(fp_corpus.sum()),
                d_below_guoff_cells=int(still_low.sum()),
                resid_cells=int(resid.sum()),
                artifact_cells_outside_fp=int((still_low & ~fp_corpus).sum()),
                fill_rate=(None if not fp_corpus.any()
                           else round(1.0 - resid.sum() / fp_corpus.sum(), 6)),
                dz_max_in_resid=(round(float((zo - zd)[resid].max()), 4)
                                 if resid.any() else 0.0))

            # 프레임 단위 — 정본 라벨러의 폴라 격자를 그대로 빌린다
            x0, y0, st = ga
            ny, nx = za.shape
            XX, YY = np.meshgrid(x0 + np.arange(nx) * st, y0 + np.arange(ny) * st)
            n_pos_frames, n_pos_cells, pos_frames = 0, 0, []
            if resid.any():
                for f, c in sorted(cd.items()):
                    cell, _ = LB.polar_cells(XX, YY, np.asarray(c["cam"]["eye"], float),
                                             c["cam"]["yaw"], GRID)
                    fc = cell[resid]
                    hit = int((fc >= 0).sum())
                    if hit:
                        cells = sorted(set(int(v) for v in fc[fc >= 0]))
                        n_pos_frames += 1
                        n_pos_cells += len(cells)
                        pos_frames.append(dict(file=f, cells=cells))
            row["negative_gt"].update(n_frames_positive=n_pos_frames,
                                      n_cell_hits=n_pos_cells,
                                      positive_frames=pos_frames[:8])
            row["vg02_all_negative"] = (int(resid.sum()) == 0)
            if not row["vg02_all_negative"]:
                out["problems"].append(
                    f"{band}/{s}: D팔에 낙차 잔차 {int(resid.sum())}셀 "
                    f"({row['negative_gt']['fp_corpus_cells']}셀 중) — 씬 결함, 격리")
            out["scenes"].append(row)

    # ---------- 집계 -------------------------------------------------------
    dat = [r for r in out["scenes"] if "datum" in r]
    tiers = dict(datum_exact=0, datum_tol=0, datum_fail=0)
    for r in dat:
        for k in tiers:
            tiers[k] += r["datum"]["tiers"][k]
    quarantine = sorted({(r["scene"], r["band"]) for r in dat
                         if r["datum"]["verdict"] == "datum_fail"})
    out["vg_datum"] = dict(
        n_pairs=len(dat), cut_tiers=tiers,
        n_cuts=sum(r["datum"]["n_cuts"] for r in dat),
        pair_survival=f"{len(dat) - len(quarantine)}/{len(dat)}",
        pair_survival_rate=round(1 - len(quarantine) / max(len(dat), 1), 4),
        cut_survival=f"{tiers['datum_exact'] + tiers['datum_tol']}/"
                     f"{sum(tiers.values())}",
        quarantine=[dict(scene=s, band=b) for s, b in quarantine],
        drift=[dict(scene=r["scene"], band=r["band"],
                    ground_z_drift_max=r["datum"]["ground_z_drift_max"],
                    tiers=r["datum"]["tiers"], verdict=r["datum"]["verdict"],
                    fail_cuts=r["datum"]["fail_cuts"])
               for r in dat if r["datum"]["verdict"] != "datum_exact"])
    out["vg_10"] = dict(
        pose_delta_max=max((r["datum"]["pose_delta_max"] for r in dat), default=None),
        n_pairs_nonzero=sum(1 for r in dat if r["datum"]["pose_delta_max"] > 0),
        nonzero=[dict(scene=r["scene"], band=r["band"],
                      pose_delta_max=r["datum"]["pose_delta_max"],
                      ground_z_drift_max=r["datum"]["ground_z_drift_max"])
                 for r in dat if r["datum"]["pose_delta_max"] > 0])
    neg = [r for r in out["scenes"] if "negative_gt" in r]
    out["vg_02"] = dict(
        note="구조적 진술: 생산 짝 (B,D)에서 D는 off팔 → polar_gt 올-제로·tier=off. "
             "아래 수치는 그와 독립인 '낙차 잔차' 실측이다.",
        n_scene_band=len(neg),
        n_all_negative=sum(1 for r in neg if r["vg02_all_negative"]),
        defects=[dict(scene=r["scene"], band=r["band"], **r["negative_gt"])
                 for r in neg if not r["vg02_all_negative"]],
        total_fp_corpus_cells=sum(r["negative_gt"]["fp_corpus_cells"] for r in neg),
        total_resid_cells=sum(r["negative_gt"]["resid_cells"] for r in neg),
        total_artifact_cells=sum(r["negative_gt"]["artifact_cells_outside_fp"]
                                 for r in neg))
    base = [r for r in out["scenes"] if r["band"] == "base"]
    out["vg_04"] = dict(
        note="D팔 높이맵 sha256 == 정본 구off 높이맵 sha256 인 씬 = 구off가 실제로 "
             "D팔이었던 씬. 계획 §1.4는 이를 hazgate 문면으로만 예측했다.",
        equal=[r["scene"] for r in base if r.get("vg04_D_equals_guoff")],
        differ=[r["scene"] for r in base if not r.get("vg04_D_equals_guoff")])

    op = os.path.join(V3, "w1d_verify.json")
    json.dump(out, open(op, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # ---------- stdout -----------------------------------------------------
    print("=== 렌더 회계 ===")
    for r, v in out["rounds"].items():
        print(f"  {r:26s} {v['png']:4d}/{v['expected_cuts']:4d} png · depth {v['depth']:4d} "
              f"· idseg {v['idseg']:4d} · hm {v['heightmap']:2d} · {v['disk_gb']:6.2f} GB "
              f"· VG-08 {'PASS' if v['vg08_pass'] else 'FAIL'}")
    print(f"  합계 {out['accounting']['total_cuts']}컷 · in-process "
          f"{out['accounting']['in_process_gpu_h']} GPU-h")
    print("\n=== VG-datum (A,D) 3층 ===")
    print(" ", out["vg_datum"]["cut_tiers"], "· 쌍 생존",
          out["vg_datum"]["pair_survival"], "· 컷 생존", out["vg_datum"]["cut_survival"])
    for d_ in out["vg_datum"]["drift"]:
        print("   ", d_["scene"], d_["band"], d_["verdict"],
              d_["ground_z_drift_max"], d_["tiers"])
    print("  격리:", out["vg_datum"]["quarantine"] or "없음")
    print("\n=== VG-10 (포즈) ===")
    print("  max pose delta", out["vg_10"]["pose_delta_max"],
          "· 0 아닌 쌍", out["vg_10"]["n_pairs_nonzero"])
    print("\n=== VG-02 (D팔 전 칸 음성 — 낙차 잔차 실측) ===")
    print(f"  {out['vg_02']['n_all_negative']}/{out['vg_02']['n_scene_band']} 씬×밴드 통과 · "
          f"코퍼스 발자국 {out['vg_02']['total_fp_corpus_cells']}셀 중 잔차 "
          f"{out['vg_02']['total_resid_cells']}셀 · 단서제거 인공물(발자국 밖) "
          f"{out['vg_02']['total_artifact_cells']}셀")
    for d_ in out["vg_02"]["defects"]:
        print("   DEFECT", d_)
    print("\n=== VG-04 실증 (D == 구off ?) ===")
    print("  같음:", out["vg_04"]["equal"] or "없음")
    print("  다름:", len(out["vg_04"]["differ"]), "씬")
    if out["problems"]:
        print("\nPROBLEMS:")
        for p in out["problems"]:
            print("  -", p)
    print(f"\n-> {op}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
