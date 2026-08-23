#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w1d_readjudicate.py — W0 판정(z_off = 구off) vs W1-D 재판정(z_off = D팔) 대조.

DECISIONS D72 ② · W0_CUECLS §8 · RENDER_PLAN_V3 §6.1 VG-CLS.

판정 규칙은 **바뀌지 않았다**. `w0_classify.py` 헤더의 사전등록 R1/R2/R3를
그대로 쓰고, 오직 **참조 z_off만** 갈아 끼웠다(구off → D팔). 이 파일은 두
산출물을 읽어 이동을 인쇄할 뿐 새 규칙을 만들지 않는다.

사용:  python3 experiments/v3_0823/code/w1d_readjudicate.py
산출:  experiments/v3_0823/w1d_readjudication.json (+ stdout 마크다운 표)

────────────────────────────────────────────────────────────────────────────
세그 3차 검정 (`--mode seg3`) — 2026-08-24 · DECISIONS **D90 ①** / W1-D §6.4 · §10 W1D-5
────────────────────────────────────────────────────────────────────────────
**왜 세 번째 계기가 필요한가.** W1-D는 참조 비대칭(구off → D팔)을 고쳤지만 검정 2의
**눈먼 방향**은 남겼다. `fp_A` 는 단서가 **있는** 높이맵에서 계산되므로, 낙차를 **위에서
덮는** 단서(난간 상판·노징 오버행·데크형 드레싱)는 자기가 덮은 셀을 fp_A 에서 스스로
지운다. 그 결과 (ㄱ) 검정 1은 "지우면 발자국이 커진다 = 구조물"이라 하고 (ㄴ) 검정 2는
"단서 궤적이 발자국과 안 겹친다 = 장식"이라 한다. 높이맵 계기만으로는 이 엇갈림을
닫을 수 없다 — 두 검정이 같은 하향 광선 하나를 공유하기 때문이다.

**세그가 답하는 물음은 다르다: 그 셀들의 표면은 *누구 것인가*.** 컷별 ID 마스크
(`.idseg.npz` · `instance_id_segmentation`)는 픽셀마다 프림 경로를 돌려주고,
`depth` 사이드카는 그 픽셀의 월드 좌표를 돌려준다. 둘을 합치면 **단서 프림의 픽셀이
낙차 발자국의 상공에 있는가(오버행)** 를 카메라 광선으로 — 하향 광선과 **독립인
계기로** — 직접 잰다. 프림 → 단서 키 귀속은 `cue_extent_audit.Attributor`
(declared > empirical > lexical · CUE_EXTENT_AUDIT §"귀속")를 **그대로** 재사용한다.

측정 (씬마다 A팔 정본 컷 전부 · step 2 다운샘플)
  z_A  = 프로브 A팔 높이맵(정본 A팔과 **바이트 동일**, 기계 확인)
  z_B  = 프로브 Bx팔 높이맵 (그 단서만 OFF)
  z_D  = D팔 높이맵 (cue-대칭 참조 · W1-D 확정 참조면), A 격자로 align_to
  FP_A = (z_D − z_A ≥ 0.3)      FP_B = (z_D − z_B ≥ 0.3)      S = FP_B \ FP_A
      → **S = 단서가 fp_A 에서 스스로 지운 셀** = 검정 1의 Δfp 그 자체
  픽셀 p 의 월드 (x,y) → 격자 셀. CUE = 그 프레임에서 **그 단서 키**로 귀속된 픽셀.
      own_S   = |CUE ∩ proj(S)|  / |proj(S)|      (지워진 셀의 소유율)
      cover_A = |CUE ∩ proj(FP_A)| / |proj(FP_A)| (낙차면 자체의 소유율)
      over_B  = |CUE ∩ proj(FP_B)| / |CUE|        (단서가 낙차 상공에 있는 비율)

판정 규칙 — **결과를 보기 전에 못 박는다** (사후 선택 금지 · ACCOUNTING §2-6)
  S0 **적용 범위**: 세그 검정은 **검정 1·2가 엇갈린 `판정불가` 쌍에만** 발동한다.
     두 검정이 이미 일치한 쌍(구조물 4 · 장식)은 분쟁이 아니므로 3차 검정을 걸지
     않는다. 이 규칙 때문에 금지 목록은 **분쟁 집합 안에서만** 줄어들 수 있다.
  S1 **VG-01 경성 조항 (번복 불가)**: `polar_gt` 가 한 프레임이라도 다르면 → **구조물**.
     세그가 무엇을 말하든 A/B GT 항등식이 실제로 깨지므로 레버가 될 수 없다.
  S2 **계기 침묵**: 그 씬 전 컷에서 그 키로 귀속된 픽셀이 200 미만이면 → **기권**
     (증거 없음). 사전 판정을 그대로 둔다(= 판정불가 유지 · 보수).
  S3 **구조물(면소유)**: `cover_A ≥ 0.5` (proj(FP_A) ≥ 500px 일 때만 정의) —
     낙차면의 과반이 단서 프림 자신의 표면이다 = 단서가 낙차면을 **이룬다**.
  S4 **장식(덮개)**: S 가 비어 있지 않고 `own_S ≥ 0.5` — 지워진 셀의 과반이 단서
     자신의 픽셀이다 = Δfp 는 **가림 인공물**이고 낙차는 그 아래 그대로 있다.
  S5 **장식(이격)**: `over_B < 0.005` — 단서가 낙차 발자국 상공에 사실상 없다.
  S6 **장식(상재)**: 그 밖 — 단서가 낙차 위/안에 서 있으나 낙차면을 소유하지 않고
     발자국도 바꾸지 않는다.
  최종: S1 > S2 > S3 → 구조물 / 기권,  S4·S5·S6 → **장식(레버 해제)**.

`--mode seg3` 는 기존 산출물을 **덮어쓰지 않는다**. `w1d_seg3.json` 을 새로 쓰고
`w1d_readjudication.json` 에는 `seg3` 블록만 **덧붙인다**(additive).

사용:  python3 experiments/v3_0823/code/w1d_readjudicate.py --mode seg3
산출:  experiments/v3_0823/w1d_seg3.json
**CPU 전용 · Isaac 미기동 · GPU 미사용 · 정본 파일 무수정.**
"""
import argparse
import collections
import glob
import json
import os
import sys

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V3 = os.path.join(REPO, "experiments/v3_0823")
SHORT = {"cue_railing": "R", "cue_nosing": "N", "cue_tactile": "Ta",
         "cue_material_break": "T", "cue_sign": "Sg", "cue_scene_dressing": "V"}


def vstr(r):
    return r["verdict"] + (f"({r['subtype']})" if r.get("subtype") else "")


def mode_compare():
    a = json.load(open(os.path.join(V3, "w0_cuecls.json"), encoding="utf-8"))
    b = json.load(open(os.path.join(V3, "w1d_cuecls.json"), encoding="utf-8"))
    A = {(r["scene"], r["cue"]): r for r in a["pairs"]}
    B = {(r["scene"], r["cue"]): r for r in b["pairs"]}
    keys = list(A)

    rows, moved, resolved, new_disputes = [], [], [], []
    trans = {}
    for k in keys:
        ra, rb = A[k], B[k]
        row = dict(scene=k[0], cue=k[1], short=SHORT.get(k[1]),
                   bond=ra.get("bond"),
                   before=dict(verdict=vstr(ra), t1=ra.get("verdict_t1"),
                               t2=ra.get("verdict_t2"),
                               cells_raw_a=ra.get("cells_raw_a"),
                               cells_raw_b=ra.get("cells_raw_b"),
                               d_cells_raw=ra.get("d_cells_raw"),
                               polar_gt_n_diff=ra.get("polar_gt_n_diff"),
                               fp_A=(ra.get("locus") or {}).get("fp_A_cells"),
                               dcue_in_fpA=(ra.get("locus") or {}).get("dcue_in_fpA"),
                               locus=(ra.get("locus") or {}).get("locus")),
                   after=dict(verdict=vstr(rb), t1=rb.get("verdict_t1"),
                              t2=rb.get("verdict_t2"),
                              cells_raw_a=rb.get("cells_raw_a"),
                              cells_raw_b=rb.get("cells_raw_b"),
                              d_cells_raw=rb.get("d_cells_raw"),
                              polar_gt_n_diff=rb.get("polar_gt_n_diff"),
                              fp_A=(rb.get("locus") or {}).get("fp_A_cells"),
                              dcue_in_fpA=(rb.get("locus") or {}).get("dcue_in_fpA"),
                              locus=(rb.get("locus") or {}).get("locus")),
                   changed=(ra["verdict"] != rb["verdict"]))
        rows.append(row)
        t = (ra["verdict"], rb["verdict"])
        trans[t] = trans.get(t, 0) + 1
        if row["changed"]:
            moved.append(row)
        if ra["verdict"] == "판정불가" and rb["verdict"] != "판정불가":
            resolved.append(row)
        if ra["verdict"] != "판정불가" and rb["verdict"] == "판정불가":
            new_disputes.append(row)

    out = dict(
        doc="w1d_readjudication", version="1.0",
        before=dict(source="w0_cuecls.json", z_off=a["off_round_for_footprint"],
                    counts=a["verdict_counts"],
                    n_forbidden=len(a["toggle_forbidden"])),
        after=dict(source="w1d_cuecls.json", z_off=b["off_round_for_footprint"],
                   counts=b["verdict_counts"],
                   n_forbidden=len(b["toggle_forbidden"])),
        rule_unchanged=(a["rules"] == b["rules"]),
        transitions={f"{x}->{y}": n for (x, y), n in sorted(trans.items())},
        n_moved=len(moved), n_resolved=len(resolved),
        n_new_disputes=len(new_disputes),
        resolved=[dict(scene=r["scene"], cue=r["cue"],
                       before=r["before"]["verdict"], after=r["after"]["verdict"])
                  for r in resolved],
        new_disputes=[dict(scene=r["scene"], cue=r["cue"],
                           before=r["before"]["verdict"], after=r["after"]["verdict"])
                      for r in new_disputes],
        toggle_forbidden_final=b["toggle_forbidden"],
        b_levers_final=b["b_levers_confirmed"],
        pairs=rows)
    op = os.path.join(V3, "w1d_readjudication.json")
    if os.path.exists(op):          # `--mode seg3` 가 덧붙인 블록을 지우지 않는다
        prev = json.load(open(op, encoding="utf-8"))
        if "seg3" in prev:
            out["seg3"] = prev["seg3"]
    json.dump(out, open(op, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # ---- stdout 마크다운 --------------------------------------------------
    print(f"규칙 동일: {out['rule_unchanged']} · z_off {out['before']['z_off']} "
          f"-> {out['after']['z_off']}")
    print(f"판정 집계  before {out['before']['counts']}  ->  after {out['after']['counts']}")
    print(f"이동 {out['n_moved']}쌍 · 분쟁 해소 {out['n_resolved']} · "
          f"새 분쟁 {out['n_new_disputes']}")
    print("전이:", out["transitions"])
    print()
    print("| 씬 | cue | 결속 | Δfp (구off) | fp∩ (구off) | **Δfp (D)** | **fp∩ (D)** "
          "| 궤적(D) | 판정 (구off) | **판정 (D)** | 이동 |")
    print("|---|---|---|---:|---:|---:|---:|---|---|---|---|")
    for r in rows:
        bf, af = r["before"], r["after"]
        f = lambda v: "—" if v is None else (f"{v:+d}" if isinstance(v, int) else str(v))
        print(f"| {r['scene']} | `{r['cue']}` | {r['bond']} | "
              f"{f(bf['d_cells_raw'])} | {bf['dcue_in_fpA']} | "
              f"**{f(af['d_cells_raw'])}** | **{af['dcue_in_fpA']}** | {af['locus']} | "
              f"{bf['verdict']} | **{af['verdict']}** | "
              f"{'→' if r['changed'] else '='} |")
    print(f"\n토글 금지 목록: {out['before']['n_forbidden']} -> "
          f"{out['after']['n_forbidden']}쌍")
    print(f"-> {op}")
    return 0


# ==========================================================================
# --mode seg3 — 세그 3차 검정 (소유권)
# ==========================================================================
HAZ_DEPTH = 0.3                 # gridspec_v1.json::hazard_depth_m
DS = 2                          # 이미지 다운샘플 (960x540) — 면적비만 쓰므로 충분
MIN_CUE_PX = 200                # S2 계기 침묵 문턱 (다운샘플 픽셀)
MIN_FPA_PX = 500                # cover_A 를 정의하기 위한 최소 낙차면 픽셀
OWN_MAJ = 0.5                   # S3·S4 과반 문턱
CLEAR_FRAC = 0.005              # S5 이격 문턱

A_ROUND = "260819_main_on"                  # 정본 A팔 (백필 세그 · depth)
D_ROUND = "260826_v3w1_lib_D"               # cue-대칭 참조면
PROBE_A = "260825_v3w0_cuecls_A"            # W0 프로브 A (z_A · 정본과 바이트 동일)
PROBE_B = "260825_v3w0_cuecls_B{arm}"       # W0 프로브 Bx (z_B)
ARM_OF_CUE = {"cue_railing": "rail", "cue_nosing": "nose", "cue_tactile": "tact",
              "cue_material_break": "matl", "cue_scene_dressing": "dress"}


def _sdir(rnd, scene):
    g = glob.glob(os.path.join(REPO, "dataset", rnd, "*", scene, "variation.json"))
    return os.path.dirname(g[0]) if g else None


def _raw_hm(d):
    """날 `heightmap.npy` + 격자. 세 팔을 **같은 계기**로 읽는다 (융합 사이드카가
    프로브 라운드에 없어서 팔마다 계기가 갈리는 것을 막는다 — W1-D §2.4 교훈)."""
    import numpy as np
    z = np.load(os.path.join(d, "heightmap.npy")).astype(np.float64)
    m = json.load(open(os.path.join(d, "heightmap_meta.json"), encoding="utf-8"))
    return z, (float(m["x0"]), float(m["y0"]), float(m["step"]))


def _load_labeler():
    sys.path.insert(0, os.path.join(REPO, "experiments/mainrun_0819/code/labeling"))
    import labeler as LB
    return LB


def _attributor():
    sys.path.insert(0, os.path.join(V3, "code"))
    import cue_extent_audit as CEA
    att = json.load(open(os.path.join(V3, "logs/cue_extent_attrib.json"),
                         encoding="utf-8"))
    return CEA.Attributor(att)


def _cuts_with_seg(d):
    """`variation.json` 순서대로, idseg + depth 가 **둘 다** 실재하는 컷만."""
    v = json.load(open(os.path.join(d, "variation.json"), encoding="utf-8"))
    cu = v["cuts"]
    cu = list(cu.values()) if isinstance(cu, dict) else cu
    out = []
    for c in cu:
        stem = os.path.splitext(c["file"])[0]
        s = os.path.join(d, stem + ".idseg.npz")
        dp = os.path.join(d, stem + ".depth.npy")
        if os.path.isfile(s) and os.path.isfile(dp):
            out.append((stem, c, s, dp))
    return out


def _scene_pixels(scene, keys, cuts, geo, shape):
    """씬 한 번 순회로 **모든 관심 키**의 픽셀 마스크·셀 좌표를 만든다.

    yield (stem, cellsel, valid, keymask) — keymask[key] = 그 키 픽셀 bool.
    """
    import numpy as np
    LB = _load_labeler()
    att = _attributor()
    x0, y0, st = geo
    ny, nx = shape
    for stem, c, segp, depp in cuts:
        cam = c["cam"]
        dep = np.load(depp).astype(np.float64)
        P, good = LB.unproject(dep, np.asarray(cam["eye"], float), cam, DS)
        ix = np.rint((P[..., 0] - x0) / st).astype(np.int64)
        iy = np.rint((P[..., 1] - y0) / st).astype(np.int64)
        valid = good & (ix >= 0) & (ix < nx) & (iy >= 0) & (iy < ny)
        ixc = np.clip(ix, 0, nx - 1)
        iyc = np.clip(iy, 0, ny - 1)
        z = np.load(segp, allow_pickle=True)
        a = z["idseg"][::DS, ::DS]
        lab = json.loads(str(z["idToLabels"]))
        km = {k: np.zeros(a.shape, bool) for k in keys}
        for sid in np.unique(a):
            prim = lab.get(str(sid))
            if not prim:
                continue
            k = att.key_of(scene, prim)
            if k in km:
                km[k] |= (a == sid)
        yield stem, ixc, iyc, valid, km, P[..., 2]


def mode_seg3(argv):
    import numpy as np
    ap = argparse.ArgumentParser(prog="w1d_readjudicate --mode seg3")
    ap.add_argument("--cls", default=os.path.join(V3, "w1d_cuecls.json"))
    ap.add_argument("--out", default=os.path.join(V3, "w1d_seg3.json"))
    ap.add_argument("--extra", default="sceneC1:cue_tactile,sceneC4:cue_tactile",
                    help="분쟁은 아니나 결재 보류(held_pending_ruling)라 증거가 "
                         "필요한 쌍 — 판정에는 S0 범위 밖으로 표기한다")
    a = ap.parse_args(argv)

    LB = _load_labeler()
    cls = json.load(open(a.cls, encoding="utf-8"))
    P = {(r["scene"], r["cue"]): r for r in cls["pairs"]}
    PRIOR = {(r["scene"], r["cue"]): r for r in cls.get("prior_rulings", [])}
    forb = [(r["scene"], r["cue"]) for r in cls["toggle_forbidden"]]
    FORB = set(forb)
    extra = [tuple(x.split(":")) for x in a.extra.split(",") if x]
    targets = list(dict.fromkeys(forb + extra))

    by_scene = collections.defaultdict(list)
    for sc, cue in targets:
        by_scene[sc].append(cue)

    rows = []
    for scene in sorted(by_scene):
        cues = by_scene[scene]
        keys = {SHORT[c] for c in cues if c in SHORT}
        da = _sdir(PROBE_A, scene) or _sdir(A_ROUND, scene)
        dd = _sdir(D_ROUND, scene)
        dimg = _sdir(A_ROUND, scene)
        if not (da and dd and dimg):
            for cue in cues:
                rows.append(dict(scene=scene, cue=cue, key=SHORT.get(cue),
                                 t3="기권", t3_reason="라운드 부재",
                                 n_cuts=0))
            continue
        zA, geoA = _raw_hm(da)
        zD, geoD = _raw_hm(dd)
        zDa = LB.align_to(zD, geoD, geoA, zA.shape)
        fpA = np.isfinite(zDa) & np.isfinite(zA) & ((zDa - zA) >= HAZ_DEPTH)

        # 큐마다 z_B (프로브 Bx) → FP_B · S
        cuemask = {}
        for cue in cues:
            arm = ARM_OF_CUE.get(cue)
            db = _sdir(PROBE_B.format(arm=arm), scene) if arm else None
            if not db:
                cuemask[cue] = None
                continue
            zB, geoB = _raw_hm(db)
            zBa = LB.align_to(zB, geoB, geoA, zA.shape)
            fpB = np.isfinite(zDa) & np.isfinite(zBa) & ((zDa - zBa) >= HAZ_DEPTH)
            cuemask[cue] = dict(fpB=fpB, S=(fpB & ~fpA),
                                n_fpB=int(fpB.sum()), n_S=int((fpB & ~fpA).sum()),
                                probe=os.path.relpath(db, REPO))

        cuts = _cuts_with_seg(dimg)
        acc = {cue: collections.Counter() for cue in cues}
        for stem, ixc, iyc, valid, km, _pz in _scene_pixels(
                scene, keys, cuts, geoA, zA.shape):
            inA = valid & fpA[iyc, ixc]
            for cue in cues:
                k = SHORT.get(cue)
                cm = km.get(k)
                if cm is None:
                    continue
                m = cuemask[cue]
                acc[cue]["cue_px"] += int(cm.sum())
                acc[cue]["fpA_px"] += int(inA.sum())
                acc[cue]["cue_in_fpA"] += int((cm & inA).sum())
                if m is not None:
                    inB = valid & m["fpB"][iyc, ixc]
                    inS = valid & m["S"][iyc, ixc]
                    acc[cue]["fpB_px"] += int(inB.sum())
                    acc[cue]["S_px"] += int(inS.sum())
                    acc[cue]["cue_in_fpB"] += int((cm & inB).sum())
                    acc[cue]["cue_in_S"] += int((cm & inS).sum())

        for cue in cues:
            t = acc[cue]
            m = cuemask[cue]
            pr = P.get((scene, cue), {})
            prior = pr.get("verdict") or (
                PRIOR.get((scene, cue), {}).get("verdict") and
                PRIOR[(scene, cue)]["verdict"] + "(기판정)")
            gtdiff = pr.get("polar_gt_n_diff")
            in_scope = (prior == "판정불가")           # S0
            cover_A = (t["cue_in_fpA"] / t["fpA_px"]) if t["fpA_px"] >= MIN_FPA_PX else None
            own_S = (t["cue_in_S"] / t["S_px"]) if t["S_px"] > 0 else None
            over_B = (t["cue_in_fpB"] / t["cue_px"]) if t["cue_px"] else None
            # ---- 사전등록 규칙 S1..S6 -----------------------------------
            if gtdiff:
                t3, why = "구조물", "S1 VG-01 경성 — polar_gt %d프레임 상이" % gtdiff
            elif t["cue_px"] < MIN_CUE_PX:
                t3, why = "기권", "S2 계기 침묵 — 귀속 픽셀 %d < %d" % (
                    t["cue_px"], MIN_CUE_PX)
            elif cover_A is not None and cover_A >= OWN_MAJ:
                t3, why = "구조물", "S3 면소유 cover_A=%.3f ≥ %.2f" % (cover_A, OWN_MAJ)
            elif (m is not None and m["n_S"] > 0 and own_S is not None
                  and own_S >= OWN_MAJ):
                t3, why = "장식", "S4 덮개 own_S=%.3f ≥ %.2f (S=%d셀)" % (
                    own_S, OWN_MAJ, m["n_S"])
            elif over_B is not None and over_B < CLEAR_FRAC:
                t3, why = "장식", "S5 이격 over_B=%.4f < %.3f" % (over_B, CLEAR_FRAC)
            else:
                t3, why = "장식", "S6 상재 — cover_A=%s · over_B=%s · Δfp=%s" % (
                    "—" if cover_A is None else "%.3f" % cover_A,
                    "—" if over_B is None else "%.3f" % over_B,
                    pr.get("d_cells_raw"))
            rows.append(dict(
                scene=scene, cue=cue, key=SHORT.get(cue),
                prior_verdict=prior, prior_t1=pr.get("verdict_t1"),
                prior_t2=pr.get("verdict_t2"),
                d_cells_raw=pr.get("d_cells_raw"),
                fp_A_cells=(pr.get("locus") or {}).get("fp_A_cells"),
                dcue_in_fpA=(pr.get("locus") or {}).get("dcue_in_fpA"),
                polar_gt_n_diff=gtdiff,
                in_scope_S0=in_scope,
                n_cuts=len(cuts), ds=DS,
                probe_b=(m or {}).get("probe"),
                n_S_cells=(m or {}).get("n_S"),
                n_fpB_cells=(m or {}).get("n_fpB"),
                n_fpA_cells_hm=int(fpA.sum()),
                px=dict(cue=t["cue_px"], fpA=t["fpA_px"], fpB=t["fpB_px"],
                        S=t["S_px"], cue_in_fpA=t["cue_in_fpA"],
                        cue_in_fpB=t["cue_in_fpB"], cue_in_S=t["cue_in_S"]),
                cover_A=(None if cover_A is None else round(cover_A, 4)),
                own_S=(None if own_S is None else round(own_S, 4)),
                over_B=(None if over_B is None else round(over_B, 4)),
                t3=t3, t3_rule=why))
            print("  %-9s %-20s prior=%-6s t3=%-5s %s"
                  % (scene, cue, str(prior), t3, why), flush=True)

    # ---- 최종 판정 = 세 검정 합성 -----------------------------------------
    final, released, kept = [], [], []
    for r in rows:
        if not r["in_scope_S0"]:
            r["final"] = r["prior_verdict"]
            r["final_basis"] = "S0 범위 밖 — 검정 1·2 일치, 3차 미발동"
        elif r["t3"] == "기권":
            r["final"] = "판정불가"
            r["final_basis"] = "S2 기권 — 사전 판정 유지(보수)"
        elif r["t3"] == "구조물":
            r["final"] = "구조물"
            r["final_basis"] = r["t3_rule"]
        else:
            r["final"] = "장식"
            r["final_basis"] = r["t3_rule"]
        final.append(r)
        if (r["scene"], r["cue"]) in FORB:
            (released if r["final"] == "장식" else kept).append(r)

    forb_new = [dict(scene=r["scene"], cue=r["cue"], reason=r["final_basis"])
                for r in final
                if (r["scene"], r["cue"]) in FORB and r["final"] != "장식"]
    # 영구 금지(계획 §1.2 · 프로브 없음)는 별도 승계
    out = dict(
        doc="w1d_seg3", version="1.0", gate="VG-CLS 3차 (세그 소유권)",
        authority="DECISIONS D90 ① · W1-D §6.4 · §10 W1D-5(b)",
        created=__import__("datetime").datetime.now().isoformat(timespec="seconds"),
        instrument=dict(
            a_round=A_ROUND, d_round=D_ROUND, probe_a=PROBE_A,
            hm="raw heightmap.npy (세 팔 동일 계기)", hazard_depth_m=HAZ_DEPTH,
            downsample=DS, attribution="cue_extent_audit.Attributor "
                                       "(declared > empirical > lexical)"),
        rules=dict(S0="분쟁(판정불가) 쌍에만 발동", S1="polar_gt 상이 → 구조물(번복 불가)",
                   S2="귀속 픽셀 < %d → 기권" % MIN_CUE_PX,
                   S3="cover_A ≥ %.2f → 구조물(면소유)" % OWN_MAJ,
                   S4="own_S ≥ %.2f → 장식(덮개)" % OWN_MAJ,
                   S5="over_B < %.3f → 장식(이격)" % CLEAR_FRAC,
                   S6="그 밖 → 장식(상재)"),
        n_pairs=len(final),
        n_released=len(released), n_kept_structural=len(forb_new),
        released=[dict(scene=r["scene"], cue=r["cue"], key=r["key"],
                       basis=r["final_basis"]) for r in released],
        toggle_forbidden_after=forb_new,
        pairs=final)
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # ---- 원장 덧붙이기 (additive · 기존 필드 무수정) ------------------------
    lp = os.path.join(V3, "w1d_readjudication.json")
    if os.path.exists(lp):
        led = json.load(open(lp, encoding="utf-8"))
        led["seg3"] = dict(
            source=os.path.relpath(a.out, REPO), created=out["created"],
            authority=out["authority"], rules=out["rules"],
            n_released=out["n_released"], released=out["released"],
            toggle_forbidden_after=out["toggle_forbidden_after"],
            note="검정 3(세그 소유권)은 **판정불가 쌍에만** 발동한다(S0). "
                 "`toggle_forbidden_final`(W1-D 15쌍)은 원문 그대로 두고 "
                 "이 블록이 그 뒤의 상태를 기록한다.")
        json.dump(led, open(lp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"-> {lp} (seg3 블록 추가)")

    print("\n| 씬 | cue | 사전 판정 | Δfp(D) | fp∩(D) | S셀 | own_S | cover_A | "
          "over_B | **T3** | **최종** |")
    print("|---|---|---|---:|---:|---:|---:|---:|---:|---|---|")
    for r in final:
        f = lambda v: "—" if v is None else ("%.3f" % v if isinstance(v, float) else str(v))
        print("| %s | `%s` | %s | %s | %s | %s | %s | %s | %s | %s | **%s** |"
              % (r["scene"], r["cue"], r["prior_verdict"], f(r.get("d_cells_raw")),
                 f(r.get("dcue_in_fpA")), f(r.get("n_S_cells")), f(r.get("own_S")),
                 f(r.get("cover_A")), f(r.get("over_B")), r["t3"], r["final"]))
    print(f"\n해제 {len(released)}쌍 · 구조물 유지 {len(forb_new)}쌍")
    print(f"-> {a.out}")
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    mode = "compare"
    if "--mode" in argv:
        i = argv.index("--mode")
        mode = argv[i + 1]
        del argv[i:i + 2]
    if mode == "seg3":
        return mode_seg3(argv)
    return mode_compare()


if __name__ == "__main__":
    sys.exit(main())
