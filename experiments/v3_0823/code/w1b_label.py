#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w1b_label.py — W1 B팔 라벨링 + **같은 드라이버로 A팔 재라벨링** (CPU only).

z_off를 무엇으로 두는가 — 이 파일에서 가장 중요한 결정
--------------------------------------------------------
라벨러 발자국은 `fp = {z_off − z_on ≥ 0.3}`이다. A와 B에 **같은** z_off를 주면
차이는 오직 `z_A vs z_B`에서 나온다 — 그러니 어떤 z_off든 대조 자체는 성립한다.
그런데 **정본 구off(`260819_main_off`)를 쓰면 B에 유령 발자국이 생긴다.**

구off는 `hazard_*: false`만 준 팔이라 **위험결속 단서는 사라지고 자유결속 단서는
남는다**(W0_CUECLS §3의 cue-비대칭). B가 그 자유결속 드레싱을 지우면 그 자리에서
`z_구off`(드레싱 있음, 높음) − `z_B`(드레싱 없음, 낮음) ≥ 0.3이 되어 **낙차가
아닌 셀이 발자국으로 잡힌다.** 실측:

| 씬 | 구off 기준 fp_A / fp_B / 대칭차 | **D팔 기준** fp_A / fp_B / 대칭차 |
|---|---|---|
| scene21  | 14,456 / 14,754 / **298**   | 14,456 / 14,456 / **0** |
| sceneD1  | 94,647 / 94,713 / **66**    | 94,647 / 94,647 / **0** |
| sceneD2  | 1,160 / 4,289 / **3,129**   | 1,160 / 1,160 / **0** |
| sceneD3  | 2,520 / 5,164 / **2,644**   | 2,520 / 2,520 / **0** |

왼쪽 열은 W1D_REPORT §6.3의 "구off 참조 Δ풋프린트" 표(sceneD2 V = +3,129)를
**그대로 재현**한다. 즉 구off를 쓰면 W1-D가 이미 진단하고 폐기한 그 위양성을
VG-01에서 다시 만들어 내게 된다.

⇒ **게이트 라벨의 z_off는 D팔이다.** D는 cue-대칭 off팔이고(단서 6키 전부 off),
B의 **생산 짝**이기도 하다(계획 §1.2: B의 off 트윈 = D). 밴드도 맞춘다
(`260826_v3w1_lib_D{,_h,_e,_e2}`).

**코퍼스 대조용으로는 구off를 그대로 쓴다** — 코퍼스 A 라벨이 그 규약으로
만들어졌으므로, 내 파이프라인이 코퍼스를 재현하는지 보려면 같은 z_off를 써야 한다.

왜 A도 다시 라벨링하는가
-----------------------
이 웨이브의 중심 게이트(VG-01)는 "**A와 B의 `cells_raw`·`polar_gt`가 프레임
단위로 같은가**"다. 그 비교가 뜻을 가지려면 두 팔이 **같은 코드 · 같은 격자 ·
같은 z_off · 같은 계기**로 재어져야 한다. 코퍼스 A 라벨을 그대로 쓰면 비교가
"B 레시피의 효과"가 아니라 "내 파이프라인과 코퍼스 파이프라인의 차이"를
섞어 재게 된다.

그래서 3층으로 나눈다.
  (1) **A 게이트 라벨** — z_off = D팔  → `annotations/w1b_A.json`
  (2) **B 게이트 라벨** — z_off = D팔  → `annotations/w1b_B.json`   (VG-01은 이 둘)
  (3) **A 코퍼스 라벨** — z_off = 구off → `annotations/w1b_Acorpus.json`
      (3)이 정본 코퍼스(`dataset_manifest_v2corr.json`)의 `polar_gt`를 재현하면
      **내 파이프라인이 코퍼스와 같은 산술을 돌린다**는 뜻이고, (1)(2)의 판정이
      훈련 GT로 이전된다. `w1b_verify.py`가 이 대조를 인쇄한다.

왜 라벨러 CLI가 아니라 드라이버인가
-----------------------------------
라벨러 CLI는 `--on-round` / `--off-round`를 **라운드 트리 단위**로 받는다.
그런데 코퍼스의 계기 권위는 (밴드, 씬)마다 다르다 — E 밴드의 scene08·scene12는
`g7fixM` 트리(융합 사이드카를 얹은 심링크본)가 정본이고 나머지 씬은 평 트리다.
라운드 단위 인자로는 이 혼합을 표현할 수 없다. 그래서 정본 `labeler.label_scene`을
**그대로 호출**하되 (sdir, off_dir)만 씬별로 고른다. 라벨링 산술은 1행도 바꾸지 않는다.

키 규약
-------
H 밴드와 E 밴드는 시드가 같아(20260820) 컷 파일명이 **글자 그대로 같다**.
코퍼스는 이것을 `...png::boost_h` / `::boost_e` 접미사로 풀었다(실측:
`labels_v1_full_g7fix.json`의 scene09 키). 같은 규약을 쓴다 — base는 접미사 없음,
밴드는 `::boost_{h,e,e2}`. 이것이 D23 파일명 충돌 교훈의 라벨 쪽 대응물이다.

사용:  python3 experiments/v3_0823/code/w1b_label.py [--workers 8] [--force]
산출:  experiments/v3_0823/annotations/w1b_A.json · w1b_B.json
"""
import argparse
import glob
import json
import os
import sys

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V3 = os.path.join(REPO, "experiments/v3_0823")
ANN = os.path.join(V3, "annotations")
LABDIR = os.path.join(REPO, "experiments/mainrun_0819/code/labeling")
sys.path.insert(0, LABDIR)
import labeler as LB                                            # noqa: E402

GRID_PATH = os.path.join(LABDIR, "gridspec_v1.json")
# --- W1-B2 보충 웨이브 스위치 (DECISIONS D75 ③ · W1B_REPORT §8.1) ----------
# `W1B_ARM=B`  (기본)  → 착지한 `260826_v3w1_lib_B*` · 산출 `w1b_*`  (W1-B 재현 그대로)
# `W1B_ARM=B2`         → T레버 보충본 `260826_v3w1_lib_B2*` · **12씬만** · 산출 `w1b2_*`
# 어느 쪽이든 코퍼스 A팔·D팔·구off 참조와 게이트 술어는 **한 글자도 다르지 않다**.
ARM = os.environ.get("W1B_ARM", "B")
if ARM not in ("B", "B2"):
    raise SystemExit(f"W1B_ARM must be B or B2, got {ARM!r}")
TAG = "w1b" if ARM == "B" else "w1b2"
B2_SCENES = set("scene02 scene08 scene09 scene12 scene16 scene17 scene20 "
                "scene21 sceneC1 sceneC4 sceneD1 sceneD3".split())


def _sel(ss):
    """B2 웨이브는 T레버를 보충한 12씬만 다시 찍었다."""
    return [s for s in ss if ARM == "B" or s in B2_SCENES]

B = f"260826_v3w1_lib_{ARM}"

D = "260826_v3w1_lib_D"
BANDS = {
    "base": (B, _sel("scene01 scene02 scene06 scene08 scene09 scene12 scene16 scene17 "
                     "scene20 scene21 sceneC1 sceneC4 sceneD1 sceneD2 sceneD3".split())),
    "h":    (f"{B}_h", _sel("scene09 scene17".split())),
    "e":    (f"{B}_e", _sel("scene08 scene09 scene12 scene17 scene20 sceneC1 "
                            "sceneC4".split())),
    "e2":   (f"{B}_e2", _sel("scene12 scene20 sceneC4".split())),
}
# 게이트용 z_off = 밴드가 맞는 D팔 라운드 (cue-대칭 · B의 생산 짝)
D_ROUND = dict(base=D, h=f"{D}_h", e=f"{D}_e", e2=f"{D}_e2")
# (밴드) -> (평 A 라운드, 평 구off 라운드, {씬: (A 오버레이, off 오버레이)})
CORPUS = {
    "base": ("260819_main_on", "260819_main_off", {}),
    "h":    ("260820_boost_h_on", "260820_boost_h_off", {}),
    "e":    ("260820_boost_e_on", "260820_boost_e_off",
             {"scene08": ("260820_boost_e_on_g7fixM", "260820_boost_e_off_g7fixM"),
              "scene12": ("260820_boost_e_on_g7fixM", "260820_boost_e_off_g7fixM")}),
    "e2":   ("260820_boost_e2_on", "260820_boost_e2_off",
             {"scene12": ("260820_boost_e2_on_g7fixM", "260820_boost_e2_off_g7fixM")}),
}
SUFFIX = dict(base="", h="::boost_h", e="::boost_e", e2="::boost_e2")


def sdir(run, scene):
    g = glob.glob(os.path.join(REPO, "dataset", run, "*", scene, "variation.json"))
    return os.path.dirname(g[0]) if g else None


def rounds_of(band, scene):
    a, o, over = CORPUS[band]
    a2, o2 = over.get(scene, (a, o))
    return a2, o2


def build_tasks():
    """(팔, 밴드, 씬, sdir, off_dir) — 없는 것은 사유와 함께 되돌린다."""
    tasks, missing = [], []
    for band in ("base", "h", "e", "e2"):
        brun, scs = BANDS[band]
        drun = D_ROUND[band]
        for s in scs:
            arun, orun = rounds_of(band, s)
            db, da = sdir(brun, s), sdir(arun, s)
            do, dd = sdir(orun, s), sdir(drun, s)
            if not dd:
                missing.append(f"{band}/{s}: 게이트 z_off(D팔 {drun}) 없음")
                continue
            if da:
                tasks.append(("A", band, s, da, dd, arun, drun))          # 게이트
                if do:
                    tasks.append(("Acorpus", band, s, da, do, arun, orun))  # 코퍼스 대조
                else:
                    missing.append(f"{band}/{s}: 코퍼스 z_off {orun} 없음")
            else:
                missing.append(f"{band}/{s}: A 라운드 {arun} 없음")
            if db:
                tasks.append(("B", band, s, db, dd, brun, drun))          # 게이트
            else:
                missing.append(f"{band}/{s}: B 렌더 없음 ({brun})")
    return tasks, missing


def _work(t):
    arm, band, s, sd, od, run, orun = t
    try:
        fr, sm, wn = LB.label_scene("on", s, sd, od, json.load(open(GRID_PATH)))
    except Exception as e:
        return arm, band, s, {}, dict(scene=s, arm="on", band=band,
                                      error=f"{type(e).__name__}: {e}"), \
            [f"{arm}/{band}/{s}: FAILED {type(e).__name__}: {e}"]
    sm.update(band=band, round=run, off_round=orun,
              sdir=os.path.relpath(sd, REPO), off_dir=os.path.relpath(od, REPO))
    return arm, band, s, fr, sm, wn


def main(workers, force):
    os.makedirs(ANN, exist_ok=True)
    outs = {a: os.path.join(ANN, f"{TAG}_{a}.json") for a in ("A", "B", "Acorpus")}
    if not force and all(os.path.exists(p) for p in outs.values()):
        print(f"[skip] {list(outs.values())} 이미 존재 — --force 로 덮어쓴다")
        return 0

    tasks, missing = build_tasks()
    for m in missing:
        print("[hold]", m)
    nb = sum(1 for t in tasks if t[0] == "B")
    want_b = sum(len(v[1]) for v in BANDS.values())
    if nb != want_b:
        print(f"[hold] B 렌더 {nb}/{want_b} 씬×밴드만 존재 — 부분 렌더 위에서 "
              f"게이트를 열지 않는다.")
        return 2

    grid = json.load(open(GRID_PATH))
    if workers > 1:
        import multiprocessing as mp
        with mp.Pool(workers) as p:
            res = p.map(_work, tasks, chunksize=1)
    else:
        res = [_work(t) for t in tasks]

    acc = {a: dict(frames={}, sv=[], warns=[]) for a in ("A", "B", "Acorpus")}
    for arm, band, s, fr, sm, wn in res:
        sfx = SUFFIX[band]
        for k, v in fr.items():
            acc[arm]["frames"][k + sfx] = v
        acc[arm]["sv"].append(sm)
        acc[arm]["warns"] += [f"{band}/{w}" for w in wn]

    for arm, p in outs.items():
        a = acc[arm]
        json.dump(dict(grid=grid, cam_convention_source=LB.CAM_SRC,
                       doc=f"{TAG}_{arm}", version="1.0", arm_wave=ARM,
                       driver="experiments/v3_0823/code/w1b_label.py",
                       note=("A·B 게이트 라벨은 z_off = **D팔**(cue-대칭 · B의 생산 짝). "
                             "Acorpus는 z_off = 구off로, 코퍼스 재현 대조 전용. "
                             "구off를 게이트에 쓰면 자유결속 드레싱 자리에서 B에 "
                             "유령 발자국이 생긴다(W0_CUECLS §3 · W1D §6.3)."),
                       meta=dict(gt_source=LB.gt_source_of(grid),
                                 tier_source=LB.TIER_SOURCE,
                                 footprint=LB.FOOTPRINT_VERSION,
                                 n_cells=LB.n_cells(grid),
                                 interior_margin_m=LB.INTERIOR_MARGIN_M,
                                 rim_tol_m=LB.RIM_TOL_M,
                                 lip_max_pts=LB.LIP_MAX_PTS,
                                 step_run_m=LB.STEP_RUN_M,
                                 gate_policy=LB.GATE_POLICY),
                       gt_source=LB.gt_source_of(grid),
                       footprint=LB.FOOTPRINT_VERSION,
                       tau_strict=dict(tau_int=LB.TAU_INT_DEF, tau_edge=LB.TAU_EDGE_DEF),
                       scene_void=a["sv"], scene_footprint=a["sv"],
                       warnings=a["warns"] + missing, frames=a["frames"]),
                  open(p, "w"), indent=1)
        errs = [s for s in a["sv"] if "error" in s]
        print(f"[{TAG}_label] {arm}: {len(a['frames'])} frames · {len(a['sv'])} 씬×밴드 "
              f"· 오류 {len(errs)} · 경고 {len(a['warns'])} -> {p}")
        for e in errs[:5]:
            print("   ERROR", e["scene"], e.get("band"), e["error"])
    print("W1B_LABEL_DONE")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    sys.exit(main(a.workers, a.force))
