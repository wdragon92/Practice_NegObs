#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w1b_fuse.py — W1 B팔의 계기(instrument) 정렬: 깊이-융합 높이맵 사이드카.

D팔과 규칙이 **뒤집힌다** — 그 이유를 먼저 적는다
--------------------------------------------------
`w1d_fuse.py`의 규칙은 "**정본 구off팔**이 그 씬에서 융합을 쓰면 D도 융합을
쓴다"였다. D는 off팔이고, 코퍼스에서 off팔이 융합을 쓰는 이유는 토글이 프림을
지우지 않고 **보이지 않게만** 만들어 AABB 광선이 없앤 낙차를 계속 읽기
때문이다(`fuse_heightmap.py` 헤더의 scene07/08 사례).

**B팔은 on팔이다.** 위험도 켜져 있고 금지 cue도 켜져 있다. 그러므로 B의 계기
짝은 구off가 아니라 **코퍼스 A팔**이다. 그리고 이 웨이브의 중심 게이트가
"A와 B의 `cells_raw`·`polar_gt`가 같은가"이므로, 계기가 어긋나면 **판정 자체가
계기 차이를 측정**하게 된다 — `fuse_heightmap.py`의 scene12 교훈(계기 혼합 =
9,532칸 유령 발자국)이 그대로 재현된다.

그래서 규칙은 이것 하나다:

    코퍼스 A팔이 (밴드, 씬)에서 `heightmap_fused.npy`를 쓰면 B팔도 쓴다.

그런데 **B를 독립 재융합하면 안 된다** (렌더 착지 후 실측으로 드러난 것)
---------------------------------------------------------------------
융합 높이맵은 깊이 재투영이라 **카메라가 본 것만** 잰다. 단서 프림은 지면을
가리는 가림막이기도 하므로, 그것을 지우면 **지면이 한 톨도 안 변해도** 새로
보이는 셀이 생긴다. scene02 실측 (A팔 융합 vs B팔 재융합):

    유한셀 40,557 → 41,617 · 중앙값 |Δ| 4.4e-10 · **fp 대칭차 262셀**

AABB 높이맵은 **바이트 동일**인데(= 기하 불변 실증) 융합본에서만 낙차
발자국이 갈린다. 즉 재융합은 A와 B에 **원리적으로 다른 위험 GT**를 주고,
2×2 설계의 전제("A와 B는 위험 GT를 공유한다")를 무너뜨린다.

**그래서 어떻게 하는가 — 기본은 "재융합하고 게이트에 맡긴다"이다.**
"A팔 융합본을 B에 공유"하면 그 씬의 VG-01은 **구성상 통과**해 버린다(같은 높이맵 →
같은 fp → 같은 `polar_gt`). 그것은 GT를 정하는 결정이고, 중심 게이트를 스스로
무력화하는 결정이기도 하다. **에이전트가 단독으로 내릴 일이 아니다.**

⇒ 기본 동작: **B를 독립 재융합**하고 VG-01이 말하게 둔다. 갈리면 격리하고,
`aabb` 진단(시점 무관)으로 원인을 T3-instr / T3-geom으로 가른 뒤 상신한다.
공유 규칙은 `--share-when-geom-identical` 플래그 뒤에 두었다 — 결재가 나면
AABB 바이트 동일인 (밴드, 씬)에만 적용된다(`g7fixM`의 밴드 간 공유 패턴을
팔 축으로 넓힌 것). 어느 쪽이든 `refuse_vs_A`에 재융합본과 A의 차이를 남긴다.

실측 적용 대상 (`labels_v1_full_g7fix.json`·`labels_boost_*_g7fixM.json`의
`hm_source` 열 그대로):

    base : scene02 · scene12 · scene16     (scene08은 on=aabb / off=fused — off만)
    e    : scene12                          (scene07은 test-core라 B팔 없음)
    e2   : scene12
    h    : 없음

`w1d_fuse_audit.json`도 읽어서 **D팔 감사가 그 씬을 어떻게 봤는지** 같은 표에
인쇄한다(과제 지시). 두 열이 다른 씬(scene08)은 그 자체가 기록 대상이다 —
같은 씬에서 on팔과 off팔의 계기가 다른 것이 코퍼스의 실제 상태다.

밴드 라운드는 D팔과 같은 원칙: 카메라만 바뀌고 지오메트리는 같으므로 base
밴드의 융합본을 복사하되, **AABB 높이맵 sha256 동일**로 그 전제를 실증한다.

사용:  python3 experiments/v3_0823/code/w1b_fuse.py [--write]
산출:  experiments/v3_0823/w1b_fuse_audit.json  (+ stdout 표)
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

# --- W1-B2 보충 웨이브 스위치 (DECISIONS D75 ③ · W1B_REPORT §8.1) ----------
# `W1B_ARM=B`  (기본)  → 착지한 `260826_v3w1_lib_B*` · 산출 `w1b_*`  (W1-B 재현 그대로)
# `W1B_ARM=B2`         → T레버 보충본 `260826_v3w1_lib_B2*` · **12씬만** · 산출 `w1b2_*`
# 어느 쪽이든 코퍼스 A팔·D팔·구off 참조와 게이트 술어는 **한 글자도 다르지 않다**.
# --- W1-C 웨이브 스위치 (DECISIONS D82 ② · PREREG_V3 §7.2 `AC-INSTR-1`) ------
# `W1B_ARM=C`          → C팔 `260827_v3w1_lib_C*` · 18씬 · 산출 `w1c_*`
# **C3-1 (계기 상속 · 팔 무관)**: (밴드,씬)의 계기 선택은 코퍼스 A팔에서
#   상속하고 팔별로 재선택하지 않는다 — 아래 `corpus_on_fused()` 가 그것이고
#   B/B2 와 **한 글자도 다르지 않다**.
# **C3-5 (공유 금지 · 재융합 기본)**: A팔 융합본을 C에 공유하지 않는다.
#   공유하면 그 씬의 VG-01/02 가 구성상 통과해 게이트가 무력화된다. C 는
#   독립 재융합하고 게이트가 말하게 둔다. (`SHARE` 는 결재로만 열린다.)
# **C3-4 (동일-시점 융합 강제)**: 같은 포즈 집합·같은 `n_views` — VG-10 과
#   VG-datum 이 강제 장치이며 팔 간 `n_views` 불일치는 하드 실패다.
ARM = os.environ.get("W1B_ARM", "B")
if ARM not in ("B", "B2", "C"):
    raise SystemExit(f"W1B_ARM must be B, B2 or C, got {ARM!r}")
TAG = {"B": "w1b", "B2": "w1b2", "C": "w1c"}[ARM]
B2_SCENES = set("scene02 scene08 scene09 scene12 scene16 scene17 scene20 "
                "scene21 sceneC1 sceneC4 sceneD1 sceneD3".split())


def _sel(ss):
    """B2 웨이브는 T레버를 보충한 12씬만 다시 찍었다."""
    return [s for s in ss if ARM != "B2" or s in B2_SCENES]


B = ("260827_v3w1_lib_C" if ARM == "C" else f"260826_v3w1_lib_{ARM}")
# 밴드 -> (팔 라운드, 그 밴드의 씬)
if ARM == "C":
    # 계획 §1.2 C열 — B팔에 없는 s03·s04·s10 이 들어오고 s06 이 살아 있다
    # (C 는 레버가 아니라 `hazard=False + keep_dressing` 이라 T 보류와 무관).
    BANDS = {
        "base": (B, "scene01 scene02 scene03 scene04 scene06 scene08 scene09 "
                    "scene10 scene12 scene16 scene17 scene20 scene21 sceneC1 "
                    "sceneC4 sceneD1 sceneD2 sceneD3".split()),
        "h":    (f"{B}_h", "scene09 scene17".split()),
        "e":    (f"{B}_e", "scene03 scene04 scene08 scene09 scene12 scene17 "
                           "scene20 sceneC1 sceneC4".split()),
        "e2":   (f"{B}_e2", "scene03 scene04 scene12 scene20 sceneC4".split()),
    }
else:
    BANDS = {
        "base": (B, _sel("scene01 scene02 scene06 scene08 scene09 scene12 scene16 scene17 "
                         "scene20 scene21 sceneC1 sceneC4 sceneD1 sceneD2 sceneD3".split())),
        "h":    (f"{B}_h", _sel("scene09 scene17".split())),
        "e":    (f"{B}_e", _sel("scene08 scene09 scene12 scene17 scene20 sceneC1 "
                                "sceneC4".split())),
        "e2":   (f"{B}_e2", _sel("scene12 scene20 sceneC4".split())),
    }
# 코퍼스 A팔 라운드 (계기 권위). g7fixM 트리는 융합 사이드카를 얹은 심링크본이라
# 그 씬에서는 M이 이긴다 (G7_RELABEL 정본 = 변형 B).
A_ROUNDS = {
    "base": (["260819_main_on"], {}),
    "h":    (["260820_boost_h_on"], {}),
    "e":    (["260820_boost_e_on"],
             {"scene08": "260820_boost_e_on_g7fixM",
              "scene12": "260820_boost_e_on_g7fixM"}),
    "e2":   (["260820_boost_e2_on"], {"scene12": "260820_boost_e2_on_g7fixM"}),
}
AGREE_BAND_M = 0.01
FLAG_P90_M = 0.30


def sdir(run, scene):
    g = glob.glob(os.path.join(REPO, "dataset", run, "*", scene, "variation.json"))
    return os.path.dirname(g[0]) if g else None


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def a_round_of(band, scene):
    plain, over = A_ROUNDS[band]
    return over.get(scene, plain[0])


def corpus_on_fused(band, scene):
    """코퍼스 A팔이 그 (밴드, 씬)에서 융합 계기를 쓰는가."""
    r = a_round_of(band, scene)
    d = sdir(r, scene)
    if d and os.path.isfile(os.path.join(d, "heightmap_fused.npy")):
        return True, r
    return False, r


SHARE = False        # --share-when-geom-identical 로만 켠다 (기본은 재융합)


def main(write):
    daudit = {}
    p = os.path.join(V3, "w1d_fuse_audit.json")
    if os.path.exists(p):
        for r in json.load(open(p, encoding="utf-8"))["rows"]:
            daudit[(r["band"], r["scene"])] = r

    rows, wrote, flagged, problems = [], [], [], []
    base_dirs = {}
    for band in ("base", "h", "e", "e2"):
        brun, scs = BANDS[band]
        for s in scs:
            d = sdir(brun, s)
            row = dict(band=band, round=brun, scene=s)
            dr = daudit.get((band, s)) or daudit.get(("base", s)) or {}
            row["d_wave_audit"] = dict(corpus_off_fused=dr.get("corpus_off_fused"),
                                       action=dr.get("action"),
                                       med_abs=dr.get("med_abs"),
                                       p90_abs=dr.get("p90_abs"))
            if not d:
                row["error"] = "B 렌더 없음"
                problems.append(f"{band}/{s}: B 렌더 없음")
                rows.append(row)
                continue
            want, arun = corpus_on_fused(band, s)
            row.update(corpus_on_fused=want, corpus_a_round=arun)

            if band != "base":
                # 밴드는 base 융합본을 복사한다 (지오메트리 동일을 sha로 실증)
                bd = base_dirs.get(s)
                if not want:
                    row["action"] = "keep aabb"
                    rows.append(row)
                    continue
                if not bd:
                    row["error"] = "base 밴드 B 렌더 없음 — 복사 불가"
                    problems.append(f"{band}/{s}: base 밴드가 없어 융합본 복사 불가")
                    rows.append(row)
                    continue
                same = sha(os.path.join(bd, "heightmap.npy")) == \
                    sha(os.path.join(d, "heightmap.npy"))
                row["aabb_sha_equals_base_band"] = same
                if not same:
                    row["error"] = "AABB 높이맵이 base 밴드와 다르다 — 지오메트리 동일 전제 붕괴"
                    problems.append(f"{band}/{s}: AABB 높이맵이 base와 불일치, 복사 보류")
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
                    wrote.append(f"{brun}/{s} (copy)")
                rows.append(row)
                continue

            # ---- base 밴드: 전 씬 융합 감사 ----------------------------------
            base_dirs[s] = d
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
                # ---- 융합 계기는 **시점 의존**이다 — 여기서 규칙이 갈린다 -----
                # 융합 높이맵은 깊이 재투영이라 "카메라가 본 것"만 잰다. 단서
                # 프림은 가림막이기도 하므로, 그것을 지우면 **지면이 그대로여도**
                # 새로 보이는 셀이 생긴다. scene02 실측(A팔 융합 vs B팔 재융합):
                #   유한셀 40,557 → 41,617 · 중앙값 |Δ| 4.4e-10 · fp 대칭차 262셀
                # 즉 재융합하면 A와 B가 **원리적으로** 다른 낙차 GT를 갖게 되고,
                # 2×2 설계의 전제("A와 B는 위험 GT를 공유한다")가 무너진다.
                #
                # 그래서 **AABB 높이맵이 바이트 동일할 때에만** — 즉 기하가
                # 시점과 무관하게 같다는 것이 증명됐을 때에만 — A팔 융합본을
                # 그대로 B에 **공유**한다. 코퍼스가 이미 쓰는 패턴이다:
                # `g7fixM` 트리는 밴드별로 재융합하지 않고 base 밴드 융합본을
                # 심링크한다("기하가 같으니 GT도 같다"). 그 원칙을 팔 축으로 확장한다.
                #
                # 정직성 장치: 재융합본도 계산해 A와의 차이를 **원장에 남긴다**.
                # 이 씬들에서는 VG-01의 라벨러층이 독립 검사가 아니게 되므로
                # (같은 높이맵 → 같은 fp), 판정 근거는 **AABB 바이트층**이다.
                ad = sdir(arun, s)
                same_geom = bool(ad) and (
                    sha(os.path.join(ad, "heightmap.npy")) ==
                    sha(os.path.join(d, "heightmap.npy")))
                af = os.path.join(ad, "heightmap_fused.npy") if ad else None
                row["aabb_sha_equals_A_arm"] = same_geom
                if af and os.path.isfile(af):
                    fa_ = np.load(af).astype(np.float64)
                    bo = np.isfinite(fa_) & np.isfinite(hm)
                    dd = np.abs(fa_[bo] - hm[bo]) if bo.any() else np.zeros(1)
                    row["refuse_vs_A"] = dict(
                        A_fused_finite=int(np.isfinite(fa_).sum()),
                        B_refused_finite=int(np.isfinite(hm).sum()),
                        med_abs=float(f"{np.median(dd):.3e}"),
                        p90_abs=float(f"{np.percentile(dd, 90):.3e}"),
                        max_abs=round(float(dd.max()), 4))
                if SHARE and same_geom and af and os.path.isfile(af):
                    row["action"] = ("share-A-fused" if write
                                     else "would-share-A-fused")
                    row["rule"] = ("AABB 바이트 동일 ⇒ 기하 불변 실증 ⇒ A팔 융합본을 "
                                   "쌍의 공유 GT로 쓴다 (재융합은 시점 의존이라 "
                                   "A/B가 원리적으로 갈린다)")
                    if write:
                        shutil.copy2(af, os.path.join(d, "heightmap_fused.npy"))
                        am = os.path.join(ad, "heightmap_fused_meta.json")
                        m = (json.load(open(am, encoding="utf-8"))
                             if os.path.isfile(am) else {})
                        m["shared_from_arm"] = os.path.relpath(ad, REPO)
                        m["share_rule"] = row["rule"]
                        m["b_refuse_divergence"] = row.get("refuse_vs_A")
                        json.dump(m, open(os.path.join(d, "heightmap_fused_meta.json"),
                                          "w", encoding="utf-8"),
                                  ensure_ascii=False, indent=1)
                        wrote.append(f"{brun}/{s} (A팔 융합본 공유)")
                else:
                    row["action"] = "write(refuse)" if write else "would-write(refuse)"
                    row["rule"] = (("AABB 바이트가 갈리므로 공유 불가 — " if not same_geom
                                    else "공유 옵션 꺼짐(기본) — ") +
                                   "B를 독립 재융합하고 VG-01의 판정에 맡긴다")
                    if write:
                        FH.write_pair(d, hm, meta)
                        wrote.append(f"{brun}/{s} (재융합)")
            elif row["med_abs"] > AGREE_BAND_M or row["p90_abs"] > FLAG_P90_M:
                why = ("median" if row["med_abs"] > AGREE_BAND_M else "") + \
                      ("+" if row["med_abs"] > AGREE_BAND_M and row["p90_abs"] > FLAG_P90_M else "") + \
                      ("p90>위험깊이" if row["p90_abs"] > FLAG_P90_M else "")
                row["action"] = f"FLAG:{why} (계기 불일치 — 쓰지 않음, 보고만)"
                flagged.append(dict(round=brun, scene=s, why=why, med_abs=row["med_abs"],
                                    p90_abs=row["p90_abs"], max_abs=row["max_abs"],
                                    fused_z=row["fused_z"], aabb_z=row["aabb_z"]))
            else:
                row["action"] = "keep aabb"
            rows.append(row)

    out = dict(doc=f"{TAG}_fuse_audit", version="1.0", arm=ARM, b_round=B,
               rule="코퍼스 **A팔**이 융합을 쓰는 (밴드,씬)에만 B팔 융합 사이드카를 쓴다 "
                    "— B는 on팔이고 중심 게이트가 A/B 동일성이므로 계기 짝이 A다. "
                    "그리고 **재융합하지 않는다**: 융합은 시점 의존이라 단서(=가림막) "
                    "제거만으로 fp가 갈린다(scene02 실측 262셀). AABB 바이트 동일로 "
                    "기하 불변이 증명된 (밴드,씬)에 한해 **A팔 융합본을 공유**한다. "
                    "밴드 라운드는 base 융합본 복사(AABB sha 동일 확인 후).",
               share_rule_caveat="공유한 씬에서는 VG-01 라벨러층이 독립 검사가 아니다 "
                                 "— 판정 근거는 AABB 바이트층. refuse_vs_A에 "
                                 "재융합본과 A의 차이를 남긴다.",
               divergence_from_w1d=("w1d_fuse.py는 구off팔을 계기 권위로 삼았다(D가 off팔이므로). "
                                    "scene08이 두 규칙이 갈리는 유일한 씬이다 — 코퍼스에서 "
                                    "on=aabb · off=fused."),
               agree_band_m=AGREE_BAND_M, flag_p90_m=FLAG_P90_M,
               wrote=wrote, flagged=flagged, problems=problems, rows=rows)
    op = os.path.join(V3, f"{TAG}_fuse_audit.json")
    json.dump(out, open(op, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    hdr = (f"{'band':5s} {'scene':9s} {'A팔융합':8s} {'D감사off':9s} {'med|Δ|':>8s} "
           f"{'p90':>8s} {'max':>9s}  action")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        if "error" in r:
            print(f"{r['band']:5s} {r['scene']:9s}  ERROR {r['error']}")
            continue
        f = lambda k, w, p: (f"{r[k]:{w}.{p}f}" if k in r else " " * w)
        print(f"{r['band']:5s} {r['scene']:9s} {str(r.get('corpus_on_fused')):8s} "
              f"{str(r['d_wave_audit'].get('corpus_off_fused')):9s} "
              f"{f('med_abs', 8, 4)} {f('p90_abs', 8, 4)} {f('max_abs', 9, 4)}  "
              f"{r.get('action')}")
    print(f"\n사이드카 기록: {len(wrote)} — {wrote}")
    print(f"계기 불일치 플래그(미기록): {len(flagged)}")
    for x in flagged:
        print("   ", x)
    if problems:
        print("PROBLEMS:")
        for p_ in problems:
            print("  -", p_)
    print(f"-> {op}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--share-when-geom-identical", action="store_true",
                    help="AABB 바이트 동일인 (밴드,씬)에서 A팔 융합본을 B에 공유한다. "
                         "**기본 꺼짐** — GT를 정하는 결정이라 게이트가 먼저 말하게 둔다.")
    a = ap.parse_args()
    SHARE = a.share_when_geom_identical
    sys.exit(main(a.write))
