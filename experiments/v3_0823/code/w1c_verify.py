#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w1c_verify.py — W1-C (C팔) 착지 검사 (CPU only).

무엇을 검사하나
---------------
1. **렌더 회계** — 라운드 × 씬 컷 수 · s/컷 · GPU-h · 디스크.
2. **VG-01-AC** (PREREG_V3 §7.2 `AC-INSTR-1` **C3-7**) — (A,C) 3층 격리 술어.
3. **VG-datum (A,C)** — `w1c_datum.py` 로 위임 (구 계기 + **REPAIR-3 계기**).
4. **C팔 연속성 게이트** (D58) — 단서·드레싱 마스크 A↔C 불변 + 변화 픽셀의
   지형 국소성.
5. **(A,C) 광학차 로그** — 계기판① 영정보 층화 입력 (PREREG §2.1 · D76 VG-07).

C팔 GT — 라벨러를 돌리지 않는다 (C3-2)
--------------------------------------
2×2 사양상 C·D 는 **전 칸 음성**이다.  그러므로 C 에 라벨러를 돌려 나온
`polar_gt` 는 **채택하지 않고 0 으로 고정**한다.  C 의 높이맵은
(ⓐ) A 의 발자국을 만드는 z_off 참조와 (ⓑ) VG-02 검사 입력으로만 쓴다.
⇒ C 의 융합 시점 의존은 **C 의 라벨을 오염시킬 수 없다.**  오직 A 의 발자국
크기와 게이트 판정에만 나타난다.  이 파일은 그 진술을 코드로 집행한다:
C 의 GT 는 `spec_constant_all_negative` 로 **인쇄**되고 어떤 라벨러 출력도
그 자리에 들어가지 않는다.

VG-01-AC 의 계수 영역 — as-built 판정 (이 런이 확정한 것, 보고 의무)
---------------------------------------------------------------------
C3-7 의 문면 세 층은 `h12_gates.gate_vg01`(A/B 축)의 층 이름을 그대로 빌려
왔는데, 그 축에서 "발자국 안 불일치 = 실패" 가 성립하는 이유는 **A 와 B 가
발자국 안에서 같아야 하기 때문**이다.  (A,C) 축은 그렇지 않다 — C 는 발자국을
**메우는** 팔이라 발자국 안에서 A 와 다른 것이 **정상**이고, 그 문면을 글자
그대로 옮기면 게이트가 전 씬을 실패로 읽는다(D76 이 VG 정의 결함 4건에서
겪은 것과 같은 종류의 오독).

그러므로 (A,C) 축의 "발자국 안 불일치" 를 다음으로 **조작적 정의**한다:

    fp_corpus = finite(A) ∧ finite(구off) ∧ (z_구off − z_A ≥ 0.30)
                  ← 팔 무관 · 카메라 무관 (W1-D 계보, w1d_verify.py:274)
    fp_AC     = finite(A) ∧ finite(C) ∧ finite(D) ∧ (z_C − z_A ≥ 0.30)
                  ← C3-3 문자 그대로
    mismatch  = |fp_corpus \\ fp_AC|
                  ← 코퍼스 계기가 낙차라고 말하는데 C 가 **들어올리지 못한** 셀

`mismatch > 0` 이면 그 (밴드,씬) 의 (A,C) 쌍을 **계기판① 모집단에서 제외**하고
**제외 쌍 수를 인쇄**한다(C3-7 후단 그대로 · 격리 자체는 벌점이 아니고
**인쇄 누락만이 위반**이다).  3층:

    hm_exact         mismatch = 0 ∧ 대칭차 = 0   (C 가 코퍼스 발자국을 정확히 재현)
    hm_tol_offprint  mismatch = 0, fp_AC 에 여분 셀 (발자국 밖 시점 의존)
    hm_fail          mismatch > 0

부수로 **발자국 밖 A↔C 셀차**(순수 시점 의존량, C3-8 `refuse_vs_A` 의 축소판)
도 인쇄한다 — 두 독법 어느 쪽으로 읽든 숫자가 표에 있게 하기 위해서다.

사용:  python3 experiments/v3_0823/code/w1c_verify.py
산출:  experiments/v3_0823/w1c_verify.json  (+ stdout 표)
"""
import argparse
import glob
import hashlib
import io
import json
import os
import re
import sys

import numpy as np

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V3 = os.path.join(REPO, "experiments/v3_0823")
LABDIR = os.path.join(REPO, "experiments/mainrun_0819/code/labeling")
sys.path.insert(0, LABDIR)
import labeler as LB                                            # noqa: E402

GRID = json.load(open(os.path.join(LABDIR, "gridspec_v1.json"), encoding="utf-8"))
HAZ_DEPTH = float(GRID["hazard_depth_m"])

C = "260827_v3w1_lib_C"
D = "260826_v3w1_lib_D"
# band -> (C round, A corpus round, old-off round, D round, scenes)
BANDS = {
    "base": (C, "260819_main_on", "260819_main_off", D,
             "scene01 scene02 scene03 scene04 scene06 scene08 scene09 scene10 "
             "scene12 scene16 scene17 scene20 scene21 sceneC1 sceneC4 sceneD1 "
             "sceneD2 sceneD3".split()),
    "h":    (f"{C}_h", "260820_boost_h_on", "260820_boost_h_off", f"{D}_h",
             "scene09 scene17".split()),
    "e":    (f"{C}_e", "260820_boost_e_on", "260820_boost_e_off", f"{D}_e",
             "scene03 scene04 scene08 scene09 scene12 scene17 scene20 sceneC1 "
             "sceneC4".split()),
    "e2":   (f"{C}_e2", "260820_boost_e2_on", "260820_boost_e2_off", f"{D}_e2",
             "scene03 scene04 scene12 scene20 sceneC4".split()),
}
# g7fixM 오버레이 (계기 권위 · w1b_fuse.A_ROUNDS 와 동일해야 한다)
A_OVERRIDE = {("e", "scene08"): "260820_boost_e_on_g7fixM",
              ("e", "scene12"): "260820_boost_e_on_g7fixM",
              ("e2", "scene12"): "260820_boost_e2_on_g7fixM"}

# --- C팔 연속성 게이트 — 등록 문턱 (사전 등록 · 사후 조정 금지) -------------
CUE_IOU_MIN = 0.50        # 포즈별 단서 마스크 A↔C IoU 하한
CUE_MASS_MIN = 0.20       # 포즈별 단서 픽셀질량 잔존 하한 (C/A)
LOCALITY_MIN = 0.50       # 변화 픽셀 중 "지형(비단서)" 비율의 상한 판정용
# 단서·드레싱으로 읽는 프림 경로 토큰.  prims2.json 의 `guards[].prims` 에서
# 기계 추출한 것을 기본으로 하고, 아래 토큰은 그 추출이 비는 씬의 백스톱이다
# (추출/백스톱 어느 쪽이 쓰였는지 행마다 인쇄한다).
CUE_TOKENS = ("rail", "guard", "handrail", "baluster", "newel", "nosing",
              "tactile", "sign", "bollard", "bench", "tree", "hedge", "reed",
              "streetlight", "lamp", "litter", "planter", "shrub", "grass",
              "dressing", "band", "bikeline", "bikeroad", "parapet", "canopy",
              "skyline", "farbuilding", "bridge", "pergola", "gauge", "debris",
              "yard", "props", "nature", "facade", "planting", "leaf", "snow",
              "stripe", "bumper", "culvert", "overhang", "arcade")


def dilate(mask, r):
    out = mask.copy()
    for _ in range(r):
        o = out.copy()
        o[1:, :] |= out[:-1, :]
        o[:-1, :] |= out[1:, :]
        o[:, 1:] |= out[:, :-1]
        o[:, :-1] |= out[:, 1:]
        out = o
    return out


def sdir(run, scene):
    g = glob.glob(os.path.join(REPO, "dataset", run, "*", scene, "variation.json"))
    return os.path.dirname(g[0]) if g else None


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def cuts_of(d):
    v = json.load(open(os.path.join(d, "variation.json"), encoding="utf-8"))
    cu = v["cuts"]
    cu = list(cu.values()) if isinstance(cu, dict) else cu
    return {c["file"]: c for c in cu}, v


def hm_of(d):
    z, geo, src = LB.load_heightmap(d)
    return z, geo, src


def a_round(band, scene, plain):
    return A_OVERRIDE.get((band, scene), plain)


# --------------------------------------------------------------------------- #
# 단서 프림 경로 분류
# --------------------------------------------------------------------------- #
_PRIMS2 = None


def cue_path_patterns(scene):
    """prims2.json 의 `cue_*` 가드가 만드는 프림 경로 조각 (기계 추출)."""
    global _PRIMS2
    if _PRIMS2 is None:
        p = os.path.join(V3, "code", "prims2.json")
        _PRIMS2 = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    out = set()
    for k, v in _PRIMS2.items():
        if not k.split("::")[-1].startswith(scene + "_"):
            continue
        for key, info in (v.get("keys") or {}).items():
            if not key.startswith("cue_"):
                continue
            for g in info.get("guards") or []:
                for pr in g.get("prims") or []:
                    frag = re.sub(r"\{[^}]*\}", "", pr).strip("/")
                    frag = frag.split("/")[-1] if frag else ""
                    # `prims` 에는 f-string 포맷 조각(한글 인쇄문 등)이 섞여
                    # 들어온다.  프림 경로 세그먼트로 읽히는 것만 받는다 —
                    # 여분 토큰은 마스크를 **넓히기만** 하므로, 쓰레기 토큰을
                    # 받으면 지형 프림이 단서로 오분류돼 게이트가 무의미해진다.
                    if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{2,}", frag):
                        out.add(frag.lower())
    return out


def is_cue_path(path, extra):
    p = path.lower()
    return any(t in p for t in CUE_TOKENS) or any(t and t in p for t in extra)


def load_idseg(d, cut):
    p = os.path.join(d, os.path.splitext(cut)[0] + ".idseg.npz")
    if not os.path.isfile(p):
        return None, None
    try:
        z = np.load(p, allow_pickle=False)
        a = z["idseg"]
        lab = json.loads(str(z["idToLabels"]))
    except Exception:
        return None, None
    return a, lab


def cue_mask(a, lab, extra):
    """프림 경로 정규화 기반 단서 마스크 (D75 ② · C-6: **해시 비교 금지**).

    인스턴스 ID 는 평가마다 재부여되므로 ID 로 비교하면 같은 장면에서도
    불일치가 난다.  그래서 ID -> 경로 -> "단서인가" 로 내려간 뒤 픽셀 집합을
    만든다.  경로가 같으면 ID 가 달라도 같은 마스크가 나온다.
    """
    if a is None or lab is None:
        return None
    m = np.zeros(a.shape, bool)
    for k, v in lab.items():
        path = v if isinstance(v, str) else (v or {}).get("class", "")
        if not is_cue_path(str(path), extra):
            continue
        try:
            m |= (a == int(k))
        except (TypeError, ValueError):
            continue
    return m


def png_gray(p, step=2):
    try:
        from PIL import Image
    except ImportError:
        return None
    if not os.path.isfile(p):
        return None
    with Image.open(p) as im:
        g = np.asarray(im.convert("L"), dtype=np.float32)
    return g[::step, ::step]


# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(V3, "w1c_verify.json"))
    ap.add_argument("--scenes", default="")
    ap.add_argument("--bands", default="")
    ap.add_argument("--no-optical", action="store_true")
    a = ap.parse_args()
    sf = [x for x in a.scenes.split(",") if x] or None
    bf = [x for x in a.bands.split(",") if x] or None

    out = dict(
        wave="W1-C", arm="C",
        plan="RENDER_PLAN_V3 §1.2 · §4.2 · §6.1 · PREREG_V3 §7.2 AC-INSTR-1",
        gates=["VG-01-AC", "VG-datum(A,C)", "C-arm continuity (D58)",
               "(A,C) optical difference (VG-07 계보)"],
        c_arm_gt="spec_constant_all_negative (AC-INSTR-1 C3-2 — 라벨러 출력 "
                 "미채택, C의 polar_gt는 20칸 전부 0으로 고정)",
        vg01_ac_counting_domain=(
            "fp_corpus = finite(A)∧finite(구off)∧(z_구off − z_A ≥ 0.30) · "
            "fp_AC = finite(A)∧finite(C)∧finite(D)∧(z_C − z_A ≥ 0.30) · "
            "mismatch = |fp_corpus \\ fp_AC| (as-built 판정, 본 보고서 §참조)"),
        thresholds=dict(haz_depth=HAZ_DEPTH, cue_iou_min=CUE_IOU_MIN,
                        cue_mass_min=CUE_MASS_MIN),
        rows=[], problems=[])

    for band, (cr, ar, orr, dr, scs) in BANDS.items():
        if bf and band not in bf:
            continue
        for s in scs:
            if sf and s not in sf:
                continue
            arun = a_round(band, s, ar)
            dc, da, do, dd = sdir(cr, s), sdir(arun, s), sdir(orr, s), sdir(dr, s)
            row = dict(band=band, scene=s, c_round=cr, a_round=arun,
                       have=dict(C=bool(dc), A=bool(da), guoff=bool(do), D=bool(dd)))
            if not dc:
                row["error"] = "C 렌더 없음"
                out["problems"].append(f"{band}/{s}: C 렌더 없음")
                out["rows"].append(row); continue
            cc, vc = cuts_of(dc)
            row["n_cuts"] = len(cc)
            row["n_ok"] = sum(1 for c in cc.values() if c.get("ok"))
            row["sec_per_cut"] = vc.get("sec_per_cut")
            row["n_idseg"] = sum(1 for c in cc.values() if c.get("idseg"))
            row["n_stale_marker"] = len(glob.glob(os.path.join(dc, "*.idseg.STALE")))
            row["n_idseg_stale_rec"] = sum(1 for c in cc.values()
                                           if c.get("idseg_stale"))
            row["n_idseg_retry"] = sum(1 for c in cc.values() if c.get("idseg_retry"))
            try:
                m = json.load(open(os.path.join(dc, "heightmap_meta.json"),
                                   encoding="utf-8"))
                row["n_prims_C"] = m.get("n_prims")
                row["arm_config_C"] = m.get("arm_config")
            except Exception:
                row["n_prims_C"] = None
            row["c_polar_gt"] = "all_negative_spec_constant"
            # C 가 D 가 되지 않았음을 **프림 수**로 먼저 본다 (가장 싼 반증).
            #   이식이 없으면 `hazard=false` 가 단서까지 지워 C ≡ D 가 된다
            #   (=구off, 계획 §1.2).  C 의 프림이 D 와 같거나 적으면 그 씬의
            #   (A,C) 반사실은 통째로 무효다.
            for tag, dd_ in (("A", da), ("D", dd)):
                try:
                    mm = json.load(open(os.path.join(dd_, "heightmap_meta.json"),
                                        encoding="utf-8"))
                    row[f"n_prims_{tag}"] = mm.get("n_prims")
                except Exception:
                    row[f"n_prims_{tag}"] = None
            if (row.get("n_prims_C") and row.get("n_prims_D")
                    and row["n_prims_C"] <= row["n_prims_D"]):
                out["problems"].append(
                    f"{band}/{s}: **C 프림 {row['n_prims_C']} ≤ D 프림 "
                    f"{row['n_prims_D']}** — 이식이 듣지 않았다(C ≡ D = 구off)")

            # ---------- VG-01-AC --------------------------------------------
            if da and do and dd:
                zA, gA, srcA = hm_of(da)
                zC, gC, srcC = hm_of(dc)
                zO, gO, _ = hm_of(do)
                zD, gD, _ = hm_of(dd)
                zC = LB.align_to(zC, gC, gA, zA.shape)
                zO = LB.align_to(zO, gO, gA, zA.shape)
                zD = LB.align_to(zD, gD, gA, zA.shape)
                row["hm_instrument"] = dict(A=srcA, C=srcC)
                finAO = np.isfinite(zA) & np.isfinite(zO)
                fp_corpus = finAO & ((zO - zA) >= HAZ_DEPTH)
                fin3 = np.isfinite(zA) & np.isfinite(zC) & np.isfinite(zD)
                fp_ac = fin3 & ((zC - zA) >= HAZ_DEPTH)
                miss = fp_corpus & ~fp_ac
                extra = fp_ac & ~fp_corpus
                finAC = np.isfinite(zA) & np.isfinite(zC)
                dif = np.where(finAC, np.abs(zA - zC), 0.0)
                offp = (dif > 0) & ~fp_corpus & ~fp_ac
                # **C3-1 하드 실패** — 계기는 코퍼스 A팔에서 상속하며 팔별로
                #   재선택하지 않는다.  A 가 `fused` 인데 C 가 `aabb` 면 두
                #   높이맵이 **다른 자로 잰 것**이라 어떤 셀 비교도 의미가 없다
                #   (스모크에서 실제로 잡혔다: scene02 A=fused / C=aabb 상태로
                #   재면 144셀 "불일치" 가 나오는데 그건 계기차지 팔차가 아니다).
                #   처방은 `W1B_ARM=C w1b_fuse.py --write` 를 verify **전에**
                #   돌리는 것이고, 그때까지는 게이트가 판정을 거부한다.
                if srcA != srcC:
                    tier = "instrument_mismatch"
                    out["problems"].append(
                        f"{band}/{s}: **계기 불일치** A={srcA} C={srcC} — "
                        f"C3-1(계기 상속) 위반. `W1B_ARM=C w1b_fuse.py --write` "
                        f"를 먼저 돌릴 것. 이 행의 셀 수치는 판정에 쓰지 않는다")
                else:
                    tier = ("hm_exact" if (miss.sum() == 0 and extra.sum() == 0)
                            else "hm_tol_offprint" if miss.sum() == 0 else "hm_fail")
                row["vg01_ac"] = dict(
                    tier=tier,
                    ok=(None if tier == "instrument_mismatch"
                        else tier != "hm_fail"),
                    instrument_A=srcA, instrument_C=srcC,
                    fp_corpus_cells=int(fp_corpus.sum()),
                    fp_AC_cells=int(fp_ac.sum()),
                    mismatch_cells=int(miss.sum()),
                    extra_cells=int(extra.sum()),
                    reproduction=(round(float((fp_corpus & fp_ac).sum())
                                        / float(fp_corpus.sum()), 6)
                                  if fp_corpus.any() else None),
                    offprint_diff_cells=int(offp.sum()),
                    offprint_max_abs_dz=round(float(dif[offp].max()), 6)
                    if offp.any() else 0.0,
                    void_equal=bool((~np.isfinite(zA) == ~np.isfinite(zC)).all()),
                    hm_sha_A=sha(os.path.join(da, "heightmap.npy"))[:12],
                    hm_sha_C=sha(os.path.join(dc, "heightmap.npy"))[:12])
                if tier == "hm_fail":
                    out["problems"].append(
                        f"{band}/{s}: VG-01-AC hm_fail — 발자국 안 불일치 "
                        f"{int(miss.sum())}셀 (계기판① 모집단 제외)")
            else:
                row["vg01_ac"] = dict(tier="no_reference", ok=None,
                                      why="A/구off/D 중 하나가 없다")

            # ---------- C팔 연속성 게이트 (D58) ------------------------------
            if da:
                ca, _ = cuts_of(da)
                extra_tok = cue_path_patterns(s)
                common = sorted(set(ca) & set(cc))
                ious, masses, locs, n_seg = [], [], [], 0
                for f in common:
                    aA, lA = load_idseg(da, f)
                    aC, lC = load_idseg(dc, f)
                    mA_ = cue_mask(aA, lA, extra_tok)
                    mC_ = cue_mask(aC, lC, extra_tok)
                    if mA_ is None or mC_ is None or mA_.shape != mC_.shape:
                        continue
                    n_seg += 1
                    inter = float((mA_ & mC_).sum())
                    uni = float((mA_ | mC_).sum())
                    ious.append(inter / uni if uni else 1.0)
                    masses.append(float(mC_.sum()) / float(mA_.sum())
                                  if mA_.sum() else None)
                    # 변화 픽셀의 지형 국소성: 두 팔의 마스크가 다른 픽셀 중
                    # **단서가 아닌 쪽**(=지형/구조)의 비율.  낙차를 메운 팔이므로
                    # 변화는 지형에서 나야 정상이다.
                    ch = mA_ ^ mC_
                    locs.append(float(ch.sum()) / float(mA_.size))
                masses = [x for x in masses if x is not None]
                row["continuity"] = dict(
                    n_pose=len(common), n_pose_with_seg=n_seg,
                    cue_path_patterns=sorted(extra_tok)[:12],
                    iou_min=round(min(ious), 4) if ious else None,
                    iou_med=round(float(np.median(ious)), 4) if ious else None,
                    mass_ratio_min=round(min(masses), 4) if masses else None,
                    mass_ratio_med=round(float(np.median(masses)), 4)
                    if masses else None,
                    changed_frac_med=round(float(np.median(locs)), 6)
                    if locs else None,
                    # 세그 쌍이 하나도 없으면 **미측정**(None)이지 실패가 아니다.
                    #   A팔 세그 백필은 696/816 이고 격리 5유닛이 있다
                    #   (`W1B2_SEGFILL_REPORT` §2.4: scene08 base·e 깊이 씬 고유
                    #   불일치 2 + stale 3).  그 유닛을 실패로 부르면 백필의
                    #   기지 한계를 C팔의 결함으로 오기록하게 된다.
                    ok=(None if not ious else
                        (min(ious) >= CUE_IOU_MIN and bool(masses)
                         and min(masses) >= CUE_MASS_MIN)),
                    threshold=dict(iou_min=CUE_IOU_MIN, mass_min=CUE_MASS_MIN))
                if row["continuity"]["ok"] is False:
                    out["problems"].append(
                        f"{band}/{s}: C팔 연속성 — cue IoU min "
                        f"{min(ious):.3f} · mass min "
                        f"{min(masses) if masses else float('nan'):.3f}")
                if masses and max(masses) == 0.0:
                    out["problems"].append(
                        f"{band}/{s}: **C팔에 단서 픽셀이 0** — C가 D와 같아졌다")

                # ---------- (A,C) 광학차 --------------------------------------
                if not a.no_optical:
                    ds = []
                    for f in common:
                        gA_ = png_gray(os.path.join(da, f))
                        gC_ = png_gray(os.path.join(dc, f))
                        if gA_ is None or gC_ is None or gA_.shape != gC_.shape:
                            continue
                        d_ = np.abs(gA_ - gC_)
                        ds.append((float(d_.mean()),
                                   float((d_ > 8).mean()),
                                   float(np.sqrt((d_ ** 2).mean()))))
                    if ds:
                        mad = [x[0] for x in ds]
                        frac = [x[1] for x in ds]
                        rms = [x[2] for x in ds]
                        row["optical_ac"] = dict(
                            n_pairs=len(ds),
                            mad_med=round(float(np.median(mad)), 4),
                            mad_p10=round(float(np.percentile(mad, 10)), 4),
                            mad_p90=round(float(np.percentile(mad, 90)), 4),
                            mad_min=round(min(mad), 4), mad_max=round(max(mad), 4),
                            rms_med=round(float(np.median(rms)), 4),
                            changed_frac_med=round(float(np.median(frac)), 6),
                            zero_info_pairs=int(sum(1 for m in mad if m < 0.5)),
                            note="grayscale |A−C|, 2x subsample; "
                                 "zero_info = mean abs diff < 0.5/255 levels")
                        if row["optical_ac"]["zero_info_pairs"]:
                            out["problems"].append(
                                f"{band}/{s}: (A,C) 영정보 쌍 "
                                f"{row['optical_ac']['zero_info_pairs']}개 "
                                f"(계기판① 층화 입력)")
            out["rows"].append(row)

    # ---------------- 집계 ---------------------------------------------------
    rows = [r for r in out["rows"] if "error" not in r]
    out["accounting"] = dict(
        n_units=len(rows),
        n_cuts=sum(r.get("n_cuts", 0) for r in rows),
        n_ok=sum(r.get("n_ok", 0) for r in rows),
        n_idseg=sum(r.get("n_idseg", 0) for r in rows),
        n_stale_markers=sum(r.get("n_stale_marker", 0) for r in rows),
        n_idseg_retry=sum(r.get("n_idseg_retry", 0) for r in rows),
        sec_per_cut=[r.get("sec_per_cut") for r in rows if r.get("sec_per_cut")])
    spc = [x for x in out["accounting"]["sec_per_cut"] if x]
    if spc:
        out["accounting"]["gpu_hours"] = round(
            sum(float(x) * r.get("n_cuts", 0)
                for x, r in zip(spc, rows)) / 3600.0, 4)
        out["accounting"]["sec_per_cut_med"] = round(float(np.median(spc)), 3)
    del out["accounting"]["sec_per_cut"]
    t = {}
    for r in rows:
        t[r.get("vg01_ac", {}).get("tier", "n/a")] = \
            t.get(r.get("vg01_ac", {}).get("tier", "n/a"), 0) + 1
    excl = [f"{r['scene']}/{r['band']}" for r in rows
            if r.get("vg01_ac", {}).get("tier") == "hm_fail"]
    mism = [f"{r['scene']}/{r['band']}" for r in rows
            if r.get("vg01_ac", {}).get("tier") == "instrument_mismatch"]
    out["vg01_ac_summary"] = dict(
        tiers=t, n_units=len(rows),
        dashboard1_excluded_pairs=len(excl), excluded=excl,
        instrument_mismatch_pairs=len(mism), instrument_mismatch=mism,
        rule="C3-7 — hm_fail 인 (밴드,씬)의 (A,C) 쌍은 계기판① 모집단에서 "
             "제외하고 제외 쌍 수를 인쇄한다. 격리는 벌점이 아니며 인쇄 "
             "누락만이 위반이다.")
    cg = [r["continuity"] for r in rows if "continuity" in r]
    if cg:
        judged = [c for c in cg if c.get("ok") is not None]
        okn = sum(1 for c in judged if c["ok"])
        ious = [c["iou_min"] for c in cg if c.get("iou_min") is not None]
        out["continuity_summary"] = dict(
            n_units=len(cg), n_judged=len(judged), n_pass=okn,
            n_fail=len(judged) - okn, n_unmeasured=len(cg) - len(judged),
            iou_min_overall=round(min(ious), 4) if ious else None,
            units_without_seg=[f"{r['scene']}/{r['band']}" for r in rows
                               if r.get("continuity", {}).get("n_pose_with_seg") == 0],
            note="세그 쌍 0 유닛은 미측정(A팔 백필 696/816 · 격리 5유닛) — "
                 "실패가 아니다")
    op = [r["optical_ac"] for r in rows if "optical_ac" in r]
    if op:
        allmed = [o["mad_med"] for o in op]
        out["optical_summary"] = dict(
            n_units=len(op),
            n_pairs=sum(o["n_pairs"] for o in op),
            mad_med_of_units=round(float(np.median(allmed)), 4),
            mad_med_min=round(min(allmed), 4), mad_med_max=round(max(allmed), 4),
            zero_info_pairs=sum(o["zero_info_pairs"] for o in op),
            spread_ratio=round(max(allmed) / max(min(allmed), 1e-9), 2),
            note="계기판① 영정보 층화 입력 — D76 이 sceneH2/H1 3.2배로 "
                 "계열별 층화 필요를 실측한 그 양의 (A,C) 판")
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    ac = out["accounting"]
    print(f"\n=== W1-C 회계 ===\n  유닛 {ac['n_units']} · 컷 {ac['n_cuts']} "
          f"(ok {ac['n_ok']}) · idseg {ac['n_idseg']} · "
          f"STALE 마커 {ac['n_stale_markers']} · 재페치 {ac['n_idseg_retry']} · "
          f"GPU {ac.get('gpu_hours')} h · {ac.get('sec_per_cut_med')} s/컷")
    v = out["vg01_ac_summary"]
    print(f"\n=== VG-01-AC (AC-INSTR-1 C3-7) ===\n  층 {v['tiers']}")
    print(f"  계기판① 제외 쌍 **{v['dashboard1_excluded_pairs']}**: "
          f"{v['excluded'] or '없음'}")
    if "continuity_summary" in out:
        c = out["continuity_summary"]
        print(f"\n=== C팔 연속성 게이트 (D58) ===\n  통과 {c['n_pass']}/"
              f"{c['n_units']} · 최소 cue IoU {c['iou_min_overall']}"
              f" (문턱 {CUE_IOU_MIN})")
        if c["units_without_seg"]:
            print(f"  세그 부재 유닛: {c['units_without_seg']}")
    if "optical_summary" in out:
        o = out["optical_summary"]
        print(f"\n=== (A,C) 광학차 ===\n  쌍 {o['n_pairs']} · 유닛 중앙값 "
              f"{o['mad_med_of_units']} (min {o['mad_med_min']} / max "
              f"{o['mad_med_max']} · 배율 {o['spread_ratio']}배) · "
              f"영정보 쌍 {o['zero_info_pairs']}")
    if out["problems"]:
        print(f"\n=== 문제 {len(out['problems'])}건 ===")
        for p in out["problems"][:30]:
            print("  ·", p)
    print(f"\n-> {a.out}")


if __name__ == "__main__":
    main()
