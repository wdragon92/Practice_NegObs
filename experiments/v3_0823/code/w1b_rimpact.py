#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w1b_rimpact.py — 키별 |r| 재계산: **B팔이 실재로 착지한 뒤**.

`w0_rimpact.py`의 확장이다. 정의(`build_render_plan.py:444 per_key()`)·모집단
(train+val)·φ 산술은 1행도 바꾸지 않는다. 바뀌는 것은 **입력 세 가지**뿐이다.

  ① B팔 프레임 수 — 계획 표의 숫자가 아니라 **디스크에 실제로 있는 컷 수**.
     D74 ⑤가 s03·s04·s10의 B팔을 스킵했으므로 그 세 씬의 B 프레임은 **0**이다.
     D74는 "r 불변(removable() 기모델링)"이라 적었는데, 그 문장은 *판정*이
     안 바뀐다는 뜻이고 **분할표 칸 a는 실제로 줄어든다**. 본 파일이 그 차이를
     숫자로 확정한다.
  ② removable(씬, 키) — 판정 원장을 다시 해석하는 대신 **실제로 찍은 B팔
     설정 파일**(`render_configs_v3/{scene}_B.json`)을 읽는다. 이것이 그 씬에서
     무엇이 꺼졌는지의 최종 사실이다.
  ③ VG-01 격리 — 게이트가 어떤 (씬, 밴드)의 B팔을 폐기했다면 그 프레임도 뺀다.

정책 표
-------
  P1_plan      `w0_rimpact.py --cls w1d_cuecls.json`의 P1 재현.  ← 비교 기준(V=0.1824)
  PB_asbuilt   ①+② (계획 ONWIRED 유지 — 키 모집단을 고정해 P1과 직접 비교 가능)
  PB_hazgate   ①+② + ONWIRED를 `hazgate.json` 실측으로 교체
  PB_gated     ①+②+③ (VG-01 격리 반영). 격리가 없으면 PB_asbuilt와 동일.
  PB_plusT     **가정 정책(미렌더)** — 아래의 사각지대를 메웠을 때의 r.

`hazgate.json`의 사각지대 — 이 파일이 새로 잰 것
-------------------------------------------------
`hazgate.py`는 cue 배선을 **`if` 문의 조건절에서만** 수집한다(`ast.If`의 test).
그래서 삼항식으로 읽는 자리는 통째로 안 보인다. 예:

    scene12:1849  mtl = M["deckwood"] if cfg["cue_material_break"] else M["gravel"]
    scene20:866   lower_mtl = M["lower"] if cfg["cue_material_break"] else M["upper"]
    sceneC1:578   tactile=("stair_top",) if SCENE_CONFIG["cue_tactile"] else ()

이 자리들은 `hazgate.json`에서 `cue[k] = null`("배선無")로 기록되고, W1D_REPORT
§6.6의 `ON·배선` 열이 그것을 그대로 물려받았으며, 본 웨이브의 레버 집합도
그 열에서 나왔다. **AST 사각지대가 렌더 레시피까지 전파된 것이다.**
본 파일이 소스를 직접 스캔해 그 크기를 잰다(`blind_spot`).

`PB_plusT`는 "그 사각지대를 메워 `cue_material_break`를 레버에 넣었다면"의 r다.
그 자리들이 전부 **재질 재바인딩 전용(프림 불변)** 이라 계획 §1.2의 바닥 규칙
그대로 VG-01을 구성상 통과한다 — 즉 값싸고 안전한 수리다. 실제로 찍지는
않았으므로 **가정치**로만 인쇄한다.

C팔은 아직 안 찍혔다(사용자 결재 대기). C 프레임은 **계획값**을 쓰고 그 사실을
출력에 명시한다 — C가 바뀌면 이 표도 다시 낸다.

사용:  python3 experiments/v3_0823/code/w1b_rimpact.py [--cls ...] [--verify ...]
산출:  experiments/v3_0823/w1b_rimpact.json  (+ stdout 표)
"""
import argparse
import ast
import collections
import glob
import json
import math
import os
import sys

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V3 = os.path.join(REPO, "experiments/v3_0823")
KEYS = ("R", "Ta", "N", "T", "Sg", "V")
CUE2KEY = {"cue_railing": "R", "cue_tactile": "Ta", "cue_nosing": "N",
           "cue_material_break": "T", "cue_sign": "Sg", "cue_scene_dressing": "V"}
KEY2CUE = {v: k for k, v in CUE2KEY.items()}
NAME = {"R": "`cue_railing`", "Ta": "`cue_tactile`", "N": "`cue_nosing`",
        "T": "`cue_material_break`", "Sg": "`cue_sign`", "V": "`cue_scene_dressing`"}
B_ROUNDS = ["260826_v3w1_lib_B", "260826_v3w1_lib_B_h",
            "260826_v3w1_lib_B_e", "260826_v3w1_lib_B_e2"]
BAND_OF_ROUND = {"260826_v3w1_lib_B": "base", "260826_v3w1_lib_B_h": "h",
                 "260826_v3w1_lib_B_e": "e", "260826_v3w1_lib_B_e2": "e2"}

ap = argparse.ArgumentParser()
ap.add_argument("--cls", default=os.path.join(V3, "w1d_cuecls.json"))
ap.add_argument("--verify", default=os.path.join(V3, "w1b_verify.json"))
args = ap.parse_args()

plan = json.load(open(os.path.join(V3, "render_plan_v3.json"), encoding="utf-8"))
cls = json.load(open(args.cls, encoding="utf-8"))
sys.path.insert(0, os.path.join(V3, "code"))
from build_render_plan import ONWIRED as PLAN_ONWIRED           # noqa: E402

verdict = {(r["scene"], r["cue"]): r["verdict"] for r in cls["pairs"]}
for p in cls.get("prior_rulings", []):
    verdict[(p["scene"], p["cue"])] = p["verdict"]

tr = [s for s in plan["scenes"] if s.get("role") in ("train", "val")]
EXISTING = {s["scene"] for s in plan["scenes"] if s.get("origin") == "existing"}


# ---------- ① 실측 B 프레임 --------------------------------------------------
landed = collections.Counter()
landed_band = collections.defaultdict(set)
for r in B_ROUNDS:
    for p in glob.glob(os.path.join(REPO, "dataset", r, "*", "*", "*.png")):
        sc = os.path.basename(os.path.dirname(p))
        landed[sc] += 1
        landed_band[sc].add(BAND_OF_ROUND[r])

# ---------- ② 실측 레버 (찍은 설정 파일 그대로) -------------------------------
built = {}
for p in sorted(glob.glob(os.path.join(V3, "render_configs_v3", "*_B.json"))):
    sc = os.path.basename(p).replace("_B.json", "")
    cfg = json.load(open(p, encoding="utf-8"))
    built[sc] = {CUE2KEY[k] for k, v in cfg.items() if k in CUE2KEY and v is False}

# ---------- ③ VG-01 격리 ------------------------------------------------------
quarantine = collections.defaultdict(set)          # scene -> {band}
vg01_ready = False
if os.path.exists(args.verify):
    vv = json.load(open(args.verify, encoding="utf-8"))
    vg01_ready = bool(vv.get("have_labels"))
    for q in vv.get("vg_01", {}).get("quarantine", []):
        quarantine[q["scene"]].add(q["band"])

# ---------- hazgate ONWIRED --------------------------------------------------
HZ_ONWIRED = {}
for k, v in json.load(open(os.path.join(V3, "code/hazgate.json"),
                           encoding="utf-8")).items():
    tag, fn = k.split("::")
    if tag not in ("main", "batch1"):
        continue
    d, cue = v["defaults"], v["cue"]
    HZ_ONWIRED[fn.split("_")[0]] = {CUE2KEY[c] for c, r in cue.items()
                                    if r is not None and d.get(c) is True
                                    and c in CUE2KEY}


# ---------- hazgate 사각지대: 소스가 실제로 읽는 cue 자리 -------------------
def _cs(n):
    return n.value if isinstance(n, ast.Constant) and isinstance(n.value, str) else None


def _bn(n):
    return n.id if isinstance(n, ast.Name) else (n.attr if isinstance(n, ast.Attribute) else None)


def source_reads():
    """씬 -> 소스가 실제로 읽는 cue 키 (if문·삼항식·표현식 전부)."""
    hzj = json.load(open(os.path.join(V3, "code/hazgate.json"), encoding="utf-8"))
    out, blind = {}, []
    for k, v in hzj.items():
        tag, fn = k.split("::")
        if tag not in ("main", "batch1"):
            continue
        s_ = fn.split("_")[0]
        d = os.path.join(REPO, "scenes", "main" if tag == "main" else "batch1", fn)
        if not os.path.isfile(d):
            continue
        tree = ast.parse(open(d, encoding="utf-8", errors="replace").read())
        reads = {}
        for x in ast.walk(tree):
            key = None
            if isinstance(x, ast.Subscript) and _cs(x.slice) in CUE2KEY and \
                    _bn(x.value) in ("cfg", "SCENE_CONFIG"):
                key = _cs(x.slice)
            elif isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute) and \
                    x.func.attr == "get" and x.args and _cs(x.args[0]) in CUE2KEY and \
                    _bn(x.func.value) in ("cfg", "SCENE_CONFIG"):
                key = _cs(x.args[0])
            if key:
                reads.setdefault(key, []).append(x.lineno)
        on = {CUE2KEY[c] for c in reads if v["defaults"].get(c) is True}
        out[s_] = on
        for c, ls in sorted(reads.items()):
            if v["defaults"].get(c) is True and v["cue"].get(c) is None:
                blind.append(dict(scene=s_, cue=c, n_sites=len(ls), lines=ls[:3]))
    return out, blind


SRC_READS, BLIND = source_reads()
BLIND_PAIRS = {(b["scene"], CUE2KEY[b["cue"]]) for b in BLIND}


def phi(a, b, c, d):
    den = math.sqrt((a + b) * (c + d) * (a + c) * (b + d))
    return 0.0 if den == 0 else (a * d - b * c) / den


def onwired_of(policy, scene):
    if policy == "PB_hazgate" and scene in HZ_ONWIRED:
        return HZ_ONWIRED[scene]
    return PLAN_ONWIRED.get(scene, set(KEYS))


def removable(policy, scene, key):
    if policy == "P1_plan" or scene not in EXISTING:
        # 계획 P1 문면, 그리고 아직 안 찍은 신규 19씬(표준 장비 가정 유지)
        cue = KEY2CUE[key]
        v = verdict.get((scene, cue))
        if v is None:
            return not (scene == "scene20" and key == "R")
        return v == "장식"
    if policy == "PB_plusT" and (scene, key) in BLIND_PAIRS and key == "T":  # noqa
        # 사각지대를 메웠다면 — 그 자리는 전부 재질 재바인딩(프림 불변)이라
        # 레버에 넣는 것이 계획 §1.2의 바닥 규칙 그대로다.
        return True
    return key in built.get(scene, set())          # 실제로 끈 것만


def b_frames(policy, scene, planned):
    if policy == "P1_plan" or scene not in EXISTING:
        return planned
    n = landed.get(scene, 0)
    if policy == "PB_noskip" and n == 0:
        # D74 ⑤의 "r 불변" 주장을 직접 검산한다 — 스킵한 168컷을 되살렸을 때의 r.
        return planned
    if policy == "PB_gated" and scene in quarantine:
        n -= 24 * len(quarantine[scene] & landed_band.get(scene, set()))
    return max(n, 0)


def per_key(policy):
    out = {}
    for k in KEYS:
        t = collections.Counter()
        nsc = 0
        for s in tr:
            if k not in onwired_of(policy, s["scene"]):
                continue
            nsc += 1
            for arm, v in s["arms"].items():
                f = v["frames"]
                if arm == "B":
                    f = b_frames(policy, s["scene"], f)
                    if f == 0:
                        continue
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
        out[k] = dict(n_scenes=nsc, a=a, b=b, c=c, d=d,
                      r=round(abs(phi(a, b, c, d)), 4))
    return out


POLICIES = ("P1_plan", "PB_asbuilt", "PB_hazgate", "PB_gated", "PB_plusT", "PB_noskip")
P = {p: per_key(p) for p in POLICIES}

n_land = sum(landed.values())
skipped = {s: 0 for s in ("scene03", "scene04", "scene10")}
out = dict(doc="w1b_rimpact", version="1.0",
           cls_ledger=os.path.relpath(args.cls, REPO),
           b_landed_cuts=n_land, b_landed_by_scene=dict(sorted(landed.items())),
           b_skipped_d74=dict(scene03=72, scene04=72, scene10=24, cuts=168),
           built_levers={k: sorted(v) for k, v in sorted(built.items())},
           vg01_quarantine={k: sorted(v) for k, v in sorted(quarantine.items())},
           vg01_ready=vg01_ready,
           c_arm_note="C팔 미렌더 — C 프레임은 계획값. keep_dressing 결재 후 재계산 필요.",
           hazgate_blind_spot=dict(
               what="hazgate.py는 cue 배선을 `if` 문 조건절에서만 수집한다(ast.If). "
                    "삼항식/표현식 자리는 cue[k]=null로 기록되고, W1D §6.6의 "
                    "ON·배선 열과 본 웨이브 레버 집합이 그것을 물려받았다.",
               n_pairs=len(BLIND), pairs=BLIND),
           threshold=0.2, d_wave_v_r=0.1824,
           d74_skip_check=dict(
               claim="D74 ⑤: 중복 168컷 스킵은 'r 불변 (removable() 기모델링)'",
               method="PB_noskip = PB_asbuilt + 스킵 3씬의 B 프레임을 계획값으로 복원",
               delta_r={}),
           policies={p: P[p] for p in POLICIES})
out["d74_skip_check"]["delta_r"] = {
    k: round(P["PB_noskip"][k]["r"] - P["PB_asbuilt"][k]["r"], 4) for k in KEYS}
op = os.path.join(V3, "w1b_rimpact.json")
json.dump(out, open(op, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print(f"[w1b_rimpact] 판정 원장 = {out['cls_ledger']} · B 실측 {n_land}컷 "
      f"(스킵 168) · VG-01 격리 {dict(out['vg01_quarantine']) or '없음'}"
      f"{'' if vg01_ready else ' · (VG-01 라벨 미착지 — PB_gated = PB_asbuilt)'}")
print()
print("| 키 | 단서 | 씬 수 | **W1-D P1 (계획 B팔)** | **PB 실측(as-built)** | "
      "PB(격리 반영) | PB(hazgate 모집단) | PB+T(가정) |")
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
d74 = {k: round(P["PB_noskip"][k]["r"] - P["PB_asbuilt"][k]["r"], 4) for k in KEYS}
print(f"D74 ⑤ '스킵해도 r 불변' 검산 — 스킵 168컷을 되살렸을 때의 Δr: {d74}")
print()
print(f"hazgate 사각지대: {len(BLIND)}쌍 — " +
      ", ".join(f"{b['scene']}/{b['cue'].replace('cue_','')}" for b in BLIND))
print()
for p in POLICIES:
    bad = [k for k in KEYS if P[p][k]["r"] > 0.2]
    print(f"{p:12s}: r>0.2 인 키 {bad or '없음'} · 최대 r "
          f"{max(P[p][k]['r'] for k in KEYS):.4f}")
print("\na/b/c/d (PB_gated):")
for k in KEYS:
    v = P["PB_gated"][k]
    print(f"  {k:3s} {v['a']}/{v['b']}/{v['c']}/{v['d']}  (n_scenes {v['n_scenes']})")
print(f"\n-> {op}")
