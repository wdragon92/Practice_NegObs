#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w3_verify.py — W3 라운드 산출물 검수 (**러너 내장 검수기의 결함 수리판**)

**왜 별도 파일인가 — 러너가 틀렸다.**
`run_w3_text{,2}.sh` 의 `verify_out()` 은 세그 신선도를 **`고유 마스크 해시 수 ==
컷 수`** 로 판정한다. 프로브(조건 2종)에서는 눈에 띄지 않았지만 **본렌더에서는 전
라운드를 오탐한다**:

  본렌더 한 밴드 draw = **8포즈 × 3조건 = 24컷**. 세 조건은 같은 시드·같은 카메라
  인덱스를 쓰므로 **포즈가 동일**하고, ID 마스크는 **조명에 의존하지 않는다**.
  ⇒ 정상 라운드의 고유 마스크는 24개가 아니라 **8개**다.

정본 게이트 `h12_gates.gate_vg08` 은 이미 옳게 쓰여 있다 — *"기준은 컷 수가 아니라
서로 다른 카메라 포즈 수다 … 컷 수로 비교하면 정상 라운드를 stale 로 오판한다"*
(`h12_gates.py:437-440`). 러너의 검수기만 그 교훈을 놓쳤다. 이 스크립트는 **정본
게이트와 같은 기준**(`n_distinct_hashes == n_poses`)으로 다시 판정하고, 통과한
(라운드,씬)에 DONE 마커를 **소급 기록**한다.

렌더 자체는 무해하다 — 오탐은 마커를 안 쓸 뿐 프레임을 버리지 않는다. 남는 위험은
**재개 시 재렌더**(= GPU 낭비)뿐이고, 이 스크립트가 그것을 막는다.

사용
    python3 experiments/v3_0823/code/w3_verify.py            # 검수 + 마커 기록
    python3 experiments/v3_0823/code/w3_verify.py --no-mark  # 검수만
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import h12_gates as G                                        # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
MARK = os.path.join(REPO, "experiments", "v3_0823", "logs", "w3_markers")

SCENES = ["sceneH1", "sceneH2", "sceneH3", "sceneL1", "sceneN9", "sceneN11"]
BANDS = {
    "sceneH1": ["extbase", "exth"], "sceneH2": ["extbase", "exth"],
    "sceneH3": ["extbase", "exth"], "sceneL1": ["extbase", "extlat"],
    "sceneN9": ["extbase", "extb2"], "sceneN11": ["extbase", "extb2"],
}
PRE = "260824_v3w3_"
SPLIT = "test"


def check(run, scene, want):
    d = os.path.join(REPO, "dataset", run, SPLIT, scene)
    if not os.path.isdir(d):
        return dict(ok=False, note="디렉터리 없음")
    var = G.load_variation(d)
    if not var:
        return dict(ok=False, note="variation.json 없음")
    cuts = G.cuts_of(var)
    png = glob.glob(os.path.join(d, "*.png"))
    dep = glob.glob(os.path.join(d, "*.depth.npy"))
    seg = glob.glob(os.path.join(d, "*.idseg.npz"))
    stale = glob.glob(os.path.join(d, "*.idseg.STALE"))
    hm = glob.glob(os.path.join(d, "heightmap.npy"))
    vg08 = G.gate_vg08(d, var)          # **정본 기준** — 해시 수 vs 포즈 수
    void = G.gate_vg_void(d)
    ok = (len(png) >= want and len(dep) >= want and len(seg) >= want
          and len(hm) >= 1 and not stale and len(cuts) >= want
          and vg08["ok"] and void.get("ok", False))
    return dict(ok=ok, png=len(png), depth=len(dep), idseg=len(seg),
                stale=len(stale), hm=len(hm), n_cuts=len(cuts),
                n_poses=vg08["n_poses"], uniq_mask=vg08["n_distinct_hashes"],
                fetch=vg08["fetch"], seg_fresh=vg08["per_cut_fresh"],
                void_cov=void.get("coverage"), want=want,
                sec=var.get("sec"), sec_per_cut=var.get("sec_per_cut"))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--want", type=int, default=24)
    ap.add_argument("--no-mark", action="store_true")
    ap.add_argument("--out", default="")
    a = ap.parse_args(argv)
    os.makedirs(MARK, exist_ok=True)

    rep, n_ok, n_bad, n_missing, cuts = {}, 0, 0, 0, 0
    for sc in SCENES:
        for b in BANDS[sc]:
            for arm in "ABCD":
                run = f"{PRE}{b}_{arm}"
                r = check(run, sc, a.want)
                rep[f"{run}/{sc}"] = r
                if r.get("note") == "디렉터리 없음":
                    n_missing += 1
                    continue
                cuts += r.get("png", 0)
                flag = "ok  " if r["ok"] else "FAIL"
                print(f"  [{flag}] {sc:<9s} {run:<26s} png {r.get('png')}/{a.want} · "
                      f"seg {r.get('idseg')} · STALE {r.get('stale')} · "
                      f"포즈 {r.get('n_poses')} vs 고유마스크 {r.get('uniq_mask')} · "
                      f"fetch {r.get('fetch')} · void {r.get('void_cov')}")
                if r["ok"]:
                    n_ok += 1
                    if not a.no_mark:
                        with open(os.path.join(MARK, f"{run}_{sc}.done"), "w") as f:
                            json.dump(r, f, ensure_ascii=False)
                else:
                    n_bad += 1
    print(f"\n검수: 통과 {n_ok} · 미달 {n_bad} · 미착지 {n_missing} · 누적 PNG {cuts}")
    if a.out:
        json.dump(rep, open(a.out, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print(f"[out] {a.out}")
    return 0 if n_bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
