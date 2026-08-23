#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w1c_hashgate.py — `keep_dressing` 이식 15건의 **기본값 무변경 증명** (D82 ②).

무엇을 증명하는가
-----------------
D82 ② 는 additive 옵트인 키를 *"기본값 무변경 해시게이트 증명 조건"* 으로
승인했다.  즉 이식 **전**과 **후**의 정본 씬이, **같은 시드·같은 포즈·같은
기본 설정**에서 같은 것을 만들어야 한다.

기준 — **"PNG 바이트 동일" 이 아니다**
--------------------------------------
D79 ② (`W1B2_SEGFILL_REPORT.md` §2.2) 가 실증한 대로 그 기준은 **만족
불가능**하다: 세그 변경이 0인 **대조군에서도 PNG 0/76**이 일치했다
(PathTracing RGB 는 비트 재현되지 않는다).  D74·D75 의 "PNG 바이트 동일"
문면은 그때 정정됐고, 채택된 정본 기준은 **기하 대응**이다:

    heightmap.npy sha256  ∧  heightmap_meta.n_prims  ∧  포즈 Δ = 0
                          ∧  컷별 depth .npy sha256

이 넷은 "마스크와 기하가 의존하는 모든 것"을 비트로 묶고, 의존하지 않는 것
(경로추적 몬테카를로 잡음)만 푼다.

BEFORE 를 어디서 얻는가 — **재렌더가 아니라 출하된 코퍼스**
------------------------------------------------------------
BEFORE 는 이식 이전 씬 파일로 실제로 찍힌 **A팔 정본 라운드**
(`260819_main_on`) 다.  이것이 이식 전 코드의 산물임은 파일 mtime 이 아니라
계보로 보증된다: 그 라운드는 08-19 에 찍혔고 이식은 08-24 다.  BEFORE 를
재렌더하지 않으므로 (a) GPU 가 절반이고 (b) 대조가 **실제 출하물**이라 더
강한 증명이다 — 이식 후의 씬이 코퍼스를 재현하지 못하면 그것이 곧 결함이다.

AFTER 는 같은 씬·같은 시드(20260819)·같은 조건(L0)·`--cams 1` 이므로
`vk.sample_camera(scene, 0, seed)` 가 코퍼스의 컷 `L0__s20260819__0000` 과
**같은 포즈**를 준다.

기지 예외 (사전 선언)
---------------------
`scene08` 은 깊이가 컷당 수백~1만 px, 최대 47.9 m 갈리는 **씬 고유의 깊이
비결정성**을 갖는다 (B2-3, `w1b2_segfill.json`).  무변경 대조군에서도 갈렸다.
그 씬은 depth sha 를 **면제**하고 heightmap sha ∧ n_prims ∧ 포즈로 판정하며,
면제 사실을 표에 인쇄한다.  면제를 확대 적용하지 않는다.
"""
import argparse
import glob
import hashlib
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(REPO, "experiments", "v3_0823", "w1c_hashgate.json")

PORTED = ["scene02", "scene03", "scene06", "scene08", "scene10", "scene12",
          "scene16", "scene17", "scene20", "scene21", "sceneC1", "sceneC4",
          "sceneD1", "sceneD2", "sceneD3"]
BEFORE_RUN = "260819_main_on"
AFTER_RUN = "260827_v3w1c_hashgate"
CUT = "L0__s20260819__0000.png"
# sceneC1's L0 is refused (declared substitution L4) — the corpus cut is L4.
CUT_OVERRIDE = {"sceneC1": "L4__s20260819__0000.png"}
DEPTH_EXEMPT = {"scene08": "B2-3 · scene-intrinsic depth non-determinism "
                           "(also split in the no-change control)"}
POSE_KEYS = ("d", "h_rel", "yaw", "pitch", "roll", "hfov", "ground_z")


def sha(p):
    if not os.path.isfile(p):
        return None
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def unit_dir(run, scene):
    mf = os.path.join(REPO, "dataset", run, "manifest.json")
    try:
        rec = json.load(open(mf, encoding="utf-8"))["scenes"][scene]
    except Exception:
        return None
    return os.path.join(REPO, rec["out"])


def cam_of(d, cut):
    p = os.path.join(d, "variation.json")
    if not os.path.isfile(p):
        return None
    v = json.load(open(p, encoding="utf-8"))
    cu = v.get("cuts")
    cu = list(cu.values()) if isinstance(cu, dict) else (cu or [])
    for c in cu:
        if c.get("file") == cut:
            return c.get("cam")
    return None


def judge(scene):
    cut = CUT_OVERRIDE.get(scene, CUT)
    row = dict(scene=scene, cut=cut)
    db = unit_dir(BEFORE_RUN, scene)
    da = unit_dir(AFTER_RUN, scene)
    if db is None or da is None:
        row.update(verdict="MISSING",
                   why=f"before={db is not None} after={da is not None}")
        return row
    hb, ha = sha(os.path.join(db, "heightmap.npy")), sha(os.path.join(da, "heightmap.npy"))
    row["hm_sha_before"] = (hb or "")[:12]
    row["hm_sha_after"] = (ha or "")[:12]
    row["hm_equal"] = bool(hb and ha and hb == ha)
    try:
        mb = json.load(open(os.path.join(db, "heightmap_meta.json"), encoding="utf-8"))
        ma = json.load(open(os.path.join(da, "heightmap_meta.json"), encoding="utf-8"))
    except Exception as e:
        row.update(verdict="MISSING", why=f"meta unreadable: {type(e).__name__}")
        return row
    row["n_prims_before"] = mb.get("n_prims")
    row["n_prims_after"] = ma.get("n_prims")
    row["n_prims_equal"] = mb.get("n_prims") == ma.get("n_prims")
    row["n_finite_before"] = mb.get("n_finite")
    row["n_finite_after"] = ma.get("n_finite")
    stem = os.path.splitext(cut)[0]
    dpb = sha(os.path.join(db, stem + ".depth.npy"))
    dpa = sha(os.path.join(da, stem + ".depth.npy"))
    row["depth_sha_before"] = (dpb or "")[:12]
    row["depth_sha_after"] = (dpa or "")[:12]
    row["depth_equal"] = bool(dpb and dpa and dpb == dpa)
    row["depth_exempt"] = scene in DEPTH_EXEMPT
    if row["depth_exempt"]:
        row["depth_exempt_why"] = DEPTH_EXEMPT[scene]
    cb, ca = cam_of(db, cut), cam_of(da, cut)
    if cb and ca:
        deltas = {k: round(abs(float(cb.get(k, 0)) - float(ca.get(k, 0))), 9)
                  for k in POSE_KEYS}
        row["pose_delta"] = deltas
        row["pose_delta_max"] = max(deltas.values())
        row["pose_equal"] = row["pose_delta_max"] == 0.0
    else:
        row["pose_equal"] = False
        row["pose_delta_max"] = None
    need_depth = not row["depth_exempt"]
    ok = (row["hm_equal"] and row["n_prims_equal"] and row["pose_equal"]
          and (row["depth_equal"] or not need_depth))
    row["verdict"] = "PASS" if ok else "FAIL"
    if not ok:
        bad = [k for k, v in (("heightmap_sha", row["hm_equal"]),
                              ("n_prims", row["n_prims_equal"]),
                              ("pose", row["pose_equal"]),
                              ("depth_sha", row["depth_equal"] or not need_depth))
               if not v]
        row["why"] = "differs: " + ", ".join(bad)
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenes", default="", help="comma list (default: the 15)")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    scenes = [s for s in a.scenes.split(",") if s] or PORTED
    rows = [judge(s) for s in scenes]
    npass = sum(1 for r in rows if r["verdict"] == "PASS")
    out = dict(
        criterion="geometric correspondence (D79 ② / B2-1): heightmap sha256 "
                  "∧ n_prims ∧ pose Δ=0 ∧ per-cut depth sha256. "
                  "RGB PNG byte-identity is UNSATISFIABLE (control: 0/76).",
        before_run=BEFORE_RUN, after_run=AFTER_RUN,
        depth_exempt=DEPTH_EXEMPT,
        n_scenes=len(rows), n_pass=npass, n_fail=len(rows) - npass,
        rows=rows)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    hdr = (f"{'scene':10s} {'hm sha (before/after)':30s} {'n_prims':13s} "
           f"{'depth sha':26s} {'poseΔ':>9s}  verdict")
    print(hdr); print("-" * len(hdr))
    for r in rows:
        if r["verdict"] == "MISSING":
            print(f"{r['scene']:10s} {r.get('why', ''):<80s} MISSING"); continue
        hm = f"{r['hm_sha_before']}/{r['hm_sha_after']}"
        npm = f"{r['n_prims_before']}/{r['n_prims_after']}"
        dp = f"{r['depth_sha_before']}/{r['depth_sha_after']}"
        if r["depth_exempt"]:
            dp += "*"
        pd = ("%.1e" % r["pose_delta_max"]) if r["pose_delta_max"] is not None else "n/a"
        print(f"{r['scene']:10s} {hm:30s} {npm:13s} {dp:26s} {pd:>9s}  "
              f"{r['verdict']}{'  ' + r.get('why', '') if r['verdict'] == 'FAIL' else ''}")
    print(f"\n{npass}/{len(rows)} PASS   (* = depth sha exempt, see json)")
    print(f"-> {a.out}")
    sys.exit(0 if npass == len(rows) else 1)


if __name__ == "__main__":
    main()
