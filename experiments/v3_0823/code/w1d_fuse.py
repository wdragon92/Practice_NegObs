#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w1d_fuse.py — W1 D팔의 계기(instrument) 정렬: 깊이-융합 높이맵 사이드카.

왜 필요한가 — W1-D 렌더 중에 실측으로 걸린 것
-----------------------------------------------
`heightmap.npy`는 하늘에서 아래로 쏘는 AABB 광선 1개다. 그런데 토글이 프림을
**지우지 않고 보이지 않게만** 만드는 씬에서는 off팔의 AABB가 **없앤 낙차를
계속 읽는다**(`fuse_heightmap.py` 헤더: *"the AABB ray ... reads ... a prim that
the toggle only made INVISIBLE rather than deleted ... the actual reason
scene07/08 differenced to zero"*). 정본 코퍼스는 그래서 그 씬들의 off팔에
`heightmap_fused.npy`(깊이 재투영 p5)를 얹어 두었고, `labeler.load_heightmap`은
융합본이 있으면 그것을 쓴다.

D팔은 off팔이다. 같은 병에 걸린다. 스모크 1컷으로 이미 보였다:

    scene08  z_A [-4.501, 0.300] · z_D(AABB) [-4.501, 0.006]  → fp(z_off=D) = 0
             z_구off(fused) [-0.001, 0.006]                    → fp(z_off=구off) = 66,547

즉 **D를 AABB로 재면 scene08의 낙차가 통째로 사라진다.** 그 상태로 VG-CLS를
재판정하면 A와 Bx가 둘 다 `cells_raw = 0`이 되어 Δ = 0 → **전부 "장식"** 이라는
거짓 판정이 나온다. 계기를 맞추는 것이 판정보다 먼저다.

채택 규칙 (기계)
----------------
**정본 구off팔이 그 씬에서 융합을 쓰면 D도 융합을 쓴다.** D는 구off를 대체하는
z_off이므로 계기를 코퍼스와 맞춘다 — `fuse_heightmap.py`의 scene12 교훈이
"계기를 섞으면 9,532칸의 유령 발자국"이다. 규칙 밖인데 감사 |Δ| 중앙값이
코퍼스의 "일치" 대역(≤ 0.01 m)을 넘는 (라운드, 씬)은 **쓰지 않고 보고만** 한다 —
계기 교체는 GT를 바꾸므로 기계가 조용히 결정할 일이 아니다.

밴드 라운드는 G7_RELABEL의 **정본 변형 B(g7fixM) 원칙**을 따른다: 밴드는 카메라만
바꾸고 지오메트리는 같으므로, 밴드별로 다시 융합하지 않고 **base 밴드의 융합본을
복사**한다(커버리지 최대). 복사 전에 두 밴드의 **AABB 높이맵 sha256이 같은지**를
확인해 "지오메트리 동일" 전제를 실증한다.

사용:  python3 experiments/v3_0823/code/w1d_fuse.py [--write]
산출:  experiments/v3_0823/w1d_fuse_audit.json  (+ stdout 표)
"""
import argparse
import glob
import hashlib
import json
import os
import shutil
import sys

import numpy as np

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V3 = os.path.join(REPO, "experiments/v3_0823")
LABDIR = os.path.join(REPO, "experiments/mainrun_0819/code/labeling")
sys.path.insert(0, LABDIR)
import fuse_heightmap as FH                                     # noqa: E402

D = "260826_v3w1_lib_D"
BASE_SCENES = ("scene01 scene02 scene03 scene04 scene06 scene08 scene09 scene10 "
               "scene12 scene16 scene17 scene20 scene21 sceneC1 sceneC4 sceneD1 "
               "sceneD2 sceneD3 sceneN1 sceneN2 sceneN4 sceneN5").split()
# 밴드 -> (D 라운드, 정본 구off 라운드 후보(계기 권위), 씬)
BOOST = {
    "h":  (f"{D}_h", ["260820_boost_h_off_g7fixM", "260820_boost_h_off_g7fix",
                      "260820_boost_h_off"], "scene09 scene17".split()),
    "e":  (f"{D}_e", ["260820_boost_e_off_g7fixM", "260820_boost_e_off_g7fix",
                      "260820_boost_e_off"],
           "scene03 scene04 scene08 scene09 scene12 scene17 scene20 sceneC1 "
           "sceneC4".split()),
    "e2": (f"{D}_e2", ["260820_boost_e2_off_g7fixM", "260820_boost_e2_off_g7fix",
                       "260820_boost_e2_off"],
           "scene03 scene04 scene12 scene20 sceneC4".split()),
}
BASE_OFFS = ["260819_main_off"]
AGREE_BAND_M = 0.01          # 코퍼스의 "두 계기가 일치" 대역 (실측 0.0005 ~ 0.006)


def sdir(run, scene):
    g = glob.glob(os.path.join(REPO, "dataset", run, "*", scene, "variation.json"))
    return os.path.dirname(g[0]) if g else None


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def corpus_uses_fused(off_runs, scene):
    """정본 구off팔이 그 씬에서 융합 계기를 쓰는가 (사이드카 존재 = 스위치)."""
    for r in off_runs:
        d = sdir(r, scene)
        if d and os.path.isfile(os.path.join(d, "heightmap_fused.npy")):
            return True, r
    return False, None


def main(write):
    rows, wrote, flagged, problems = [], [], [], []

    # ---- base 밴드: 전 씬 융합 감사 + 선택 기록 --------------------------
    base_dirs = {}
    for s in BASE_SCENES:
        d = sdir(D, s)
        row = dict(band="base", round=D, scene=s)
        if not d:
            row["error"] = "D 렌더 없음"
            problems.append(f"base/{s}: D 렌더 없음")
            rows.append(row)
            continue
        base_dirs[s] = d
        want, src = corpus_uses_fused(BASE_OFFS, s)
        row.update(corpus_off_fused=want, corpus_off_round=src)
        try:
            hm, meta = FH.fuse_scene_arm(d)
        except Exception as e:
            row["error"] = f"{type(e).__name__}: {e}"
            problems.append(f"base/{s}: 융합 실패 {e}")
            rows.append(row)
            continue
        ab = np.load(os.path.join(d, "heightmap.npy")).astype(np.float64)
        both = np.isfinite(hm) & np.isfinite(ab)
        dif = np.abs(hm[both] - ab[both]) if both.any() else np.zeros(1)
        row.update(n_views=meta["n_views"],
                   fused_finite=int(np.isfinite(hm).sum()),
                   aabb_finite=int(np.isfinite(ab).sum()), both=int(both.sum()),
                   med_abs=round(float(np.median(dif)), 4),
                   p90_abs=round(float(np.percentile(dif, 90)), 4),
                   max_abs=round(float(dif.max()), 4),
                   fused_z=[round(float(np.nanmin(hm)), 3), round(float(np.nanmax(hm)), 3)],
                   aabb_z=[round(float(np.nanmin(ab)), 3), round(float(np.nanmax(ab)), 3)])
        if want:
            row["action"] = "write" if write else "would-write"
            if write:
                FH.write_pair(d, hm, meta)
                wrote.append(f"{D}/{s}")
        elif row["med_abs"] > AGREE_BAND_M:
            row["action"] = "FLAG (계기 불일치 — 쓰지 않음, 보고만)"
            flagged.append(dict(round=D, scene=s, med_abs=row["med_abs"],
                                p90_abs=row["p90_abs"], max_abs=row["max_abs"]))
        else:
            row["action"] = "keep aabb"
        rows.append(row)

    # ---- 밴드 라운드: base 융합본 복사 (G7 정본 변형 B 원칙) --------------
    for band, (drun, offs, scs) in BOOST.items():
        for s in scs:
            d = sdir(drun, s)
            row = dict(band=band, round=drun, scene=s)
            if not d:
                row["error"] = "D 렌더 없음"
                problems.append(f"{band}/{s}: D 렌더 없음")
                rows.append(row)
                continue
            want, src = corpus_uses_fused(offs, s)
            row.update(corpus_off_fused=want, corpus_off_round=src)
            bd = base_dirs.get(s)
            if not want:
                row["action"] = "keep aabb"
                rows.append(row)
                continue
            if not bd:
                row["error"] = "base 밴드 D 렌더 없음 — 복사 불가"
                problems.append(f"{band}/{s}: base 밴드가 없어 융합본 복사 불가")
                rows.append(row)
                continue
            same = sha(os.path.join(bd, "heightmap.npy")) == \
                sha(os.path.join(d, "heightmap.npy"))
            row["aabb_sha_equals_base_band"] = same
            if not same:
                row["error"] = "AABB 높이맵이 base 밴드와 다르다 — 지오메트리 동일 전제 붕괴"
                problems.append(f"{band}/{s}: AABB 높이맵이 base와 불일치, 융합본 복사 보류")
                rows.append(row)
                continue
            row["action"] = "copy-from-base" if write else "would-copy-from-base"
            if write:
                srcf = os.path.join(bd, "heightmap_fused.npy")
                srcm = os.path.join(bd, "heightmap_fused_meta.json")
                if not os.path.isfile(srcf):
                    row["error"] = "base 융합본이 아직 없다 (--write 순서 문제)"
                    problems.append(f"{band}/{s}: base 융합본 없음")
                    rows.append(row)
                    continue
                shutil.copy2(srcf, os.path.join(d, "heightmap_fused.npy"))
                m = json.load(open(srcm, encoding="utf-8"))
                m["copied_from"] = os.path.relpath(bd, REPO)
                m["copy_rule"] = ("G7_RELABEL 정본 변형 B — 밴드는 카메라만 바꾸고 "
                                  "지오메트리는 같으므로 base 밴드 융합본을 쓴다 "
                                  "(AABB sha256 동일로 실증)")
                json.dump(m, open(os.path.join(d, "heightmap_fused_meta.json"),
                                  "w", encoding="utf-8"), ensure_ascii=False, indent=1)
                wrote.append(f"{drun}/{s} (copy)")
            rows.append(row)

    out = dict(doc="w1d_fuse_audit", version="1.0",
               rule="정본 구off팔이 융합을 쓰는 (라운드,씬)에만 D팔 융합 사이드카를 쓴다. "
                    "밴드 라운드는 base 밴드 융합본을 복사한다(AABB sha 동일 확인 후).",
               agree_band_m=AGREE_BAND_M, wrote=wrote, flagged=flagged,
               problems=problems, rows=rows)
    op = os.path.join(V3, "w1d_fuse_audit.json")
    json.dump(out, open(op, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    hdr = (f"{'band':5s} {'scene':9s} {'구off융합':9s} {'med|Δ|':>8s} {'p90':>8s} "
           f"{'max':>9s} {'fused z':>17s} {'aabb z':>17s}  action")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        if "error" in r:
            print(f"{r['band']:5s} {r['scene']:9s}  ERROR {r['error']}")
            continue
        f = lambda k, w, p: (f"{r[k]:{w}.{p}f}" if k in r else " " * w)
        print(f"{r['band']:5s} {r['scene']:9s} {str(r.get('corpus_off_fused')):9s} "
              f"{f('med_abs', 8, 4)} {f('p90_abs', 8, 4)} {f('max_abs', 9, 4)} "
              f"{str(r.get('fused_z', '')):>17s} {str(r.get('aabb_z', '')):>17s}  "
              f"{r.get('action')}")
    print(f"\n사이드카 기록: {len(wrote)} — {wrote}")
    print(f"계기 불일치 플래그(미기록): {len(flagged)}")
    for x in flagged:
        print("   ", x)
    if problems:
        print("PROBLEMS:")
        for p in problems:
            print("  -", p)
    print(f"-> {op}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true",
                    help="사이드카를 실제로 쓴다 (없으면 감사만)")
    sys.exit(main(ap.parse_args().write))
