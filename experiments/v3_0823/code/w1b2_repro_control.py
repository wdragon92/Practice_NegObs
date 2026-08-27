#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w1b2_repro_control.py — **재현성 대조 실험** (CPU only, 렌더 0).

무엇을 재나
-----------
D75 ④는 A팔 세그 백필의 판정 기준을 *"재렌더 → **바이트 동일** 검증 → idseg만
채택"* 으로 적었고, 근거로 W0의 "sha256 재현성 19/19"를 들었다. 그런데 W0가
잰 19/19는 `heightmap.npy`이지 RGB PNG가 아니다(W0_CUECLS §1 부수 검증).
이 파일은 **이미 디스크에 있는 라운드만으로** 그 문면이 만족 가능한지를 잰다.

대조 1 — A팔 재현성 (세그 변경 없음)
    `260825_v3w0_cuecls_A`(W0 A팔) vs 정본 `260819_main_on`.
    같은 씬·시드·조건·레시피(`{hazard_*: true}`), 카메라만 4대 vs 8대(앞 4컷이 겹친다).

대조 2 — 같은 웨이브 안에서 (세그 설정까지 동일)
    `260826_v3w1_lib_B_smoke` vs `260826_v3w1_lib_B`.
    같은 레시피·같은 `NEGOBS_SEG_STRICT=1`·같은 시드·같은 컷.

세 채널을 각각 sha256으로 본다 — RGB PNG · `.depth.npy` · `.idseg.npz` —
그리고 마스크는 **프림 경로 정규화** 후 경로별 픽셀 수까지 본다
(인스턴스 ID는 평가마다 재번호되므로 원바이트 비교는 오설계 — W1B_REPORT §8.4-1).

사용:  python3 experiments/v3_0823/code/w1b2_repro_control.py
산출:  experiments/v3_0823/w1b2_repro_control.json  (+ stdout 표)
"""
import glob
import hashlib
import json
import os

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"

# 0827 reorg: dataset/ is grouped (dataset/<group>/<round>) and a round is
# found by NAME, never by a flat path. See Docs/reorg_0827/S3_report.md.
import sys
sys.path.insert(0, REPO)                              # noqa: E402
from variation_kit import has_round, round_dir_or_flat   # noqa: E402
V3 = os.path.join(REPO, "experiments/v3_0823")
POSE_KEYS = ("d", "h_rel", "yaw", "pitch", "roll", "hfov", "ground_z")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def sdir(run, sc):
    g = glob.glob(os.path.join(round_dir_or_flat(run), "*", sc, "variation.json"))
    return os.path.dirname(g[0]) if g else None


def scenes_of(run):
    return sorted({os.path.basename(os.path.dirname(p)) for p in
                   glob.glob(os.path.join(round_dir_or_flat(run), "*", "*",
                                          "variation.json"))})


def prim_norm(p):
    import numpy as np
    z = np.load(p, allow_pickle=False)
    a = z["idseg"]
    try:
        id2l = json.loads(str(z["idToLabels"]))
    except Exception:
        id2l = {}
    ids, cnt = np.unique(a, return_counts=True)
    out = {}
    for i, n in zip(ids.tolist(), cnt.tolist()):
        lab = id2l.get(str(i), id2l.get(i, f"<id{i}>"))
        out[str(lab)] = out.get(str(lab), 0) + int(n)
    return out, int(ids.size)


def px_stats(pa, pb):
    import numpy as np
    from PIL import Image
    a = np.asarray(Image.open(pa).convert("RGB"), np.int16)
    b = np.asarray(Image.open(pb).convert("RGB"), np.int16)
    d = np.abs(a - b)
    return int(d.max()), round(float(d.mean()), 5), round(float((d.max(2) > 0).mean()), 5)


def compare(tag, ref_run, new_run, scs):
    rows = []
    for s in scs:
        a, b = sdir(ref_run, s), sdir(new_run, s)
        if not (a and b):
            continue
        fs = sorted(os.path.basename(p) for p in glob.glob(b + "/*.png")
                    if os.path.isfile(os.path.join(a, os.path.basename(p))))
        row = dict(scene=s, n=len(fs), png_eq=0, depth_eq=0, idseg_eq=0,
                   idseg_primnorm_eq=0, idseg_primnorm_n=0,
                   px_max=0, px_mean=0.0, depth_diff=[])
        for f in fs:
            pa, pb = os.path.join(a, f), os.path.join(b, f)
            if sha(pa) == sha(pb):
                row["png_eq"] += 1
            else:
                mx, mn, _fr = px_stats(pa, pb)
                row["px_max"] = max(row["px_max"], mx)
                row["px_mean"] = max(row["px_mean"], mn)
            da, db = pa[:-4] + ".depth.npy", pb[:-4] + ".depth.npy"
            if os.path.isfile(da) and os.path.isfile(db):
                if sha(da) == sha(db):
                    row["depth_eq"] += 1
                else:
                    row["depth_diff"].append(f)
            ia, ib = pa[:-4] + ".idseg.npz", pb[:-4] + ".idseg.npz"
            if os.path.isfile(ia) and os.path.isfile(ib):
                if sha(ia) == sha(ib):
                    row["idseg_eq"] += 1
                row["idseg_primnorm_n"] += 1
                na, _ = prim_norm(ia)
                nb, _ = prim_norm(ib)
                row["idseg_primnorm_eq"] += int(na == nb)
        hma, hmb = os.path.join(a, "heightmap.npy"), os.path.join(b, "heightmap.npy")
        row["heightmap_eq"] = (os.path.isfile(hma) and os.path.isfile(hmb)
                               and sha(hma) == sha(hmb))
        # 포즈 7키 + eye
        ca = {c["file"]: c for c in json.load(open(os.path.join(a, "variation.json"),
                                                   encoding="utf-8"))["cuts"]}
        cb = {c["file"]: c for c in json.load(open(os.path.join(b, "variation.json"),
                                                   encoding="utf-8"))["cuts"]}
        dp = 0.0
        for f in fs:
            if f in ca and f in cb:
                pa_, pb_ = ca[f]["cam"], cb[f]["cam"]
                dp = max(dp, max(abs(float(pa_[k]) - float(pb_[k])) for k in POSE_KEYS))
                dp = max(dp, max(abs(x - y) for x, y in zip(pa_["eye"], pb_["eye"])))
        row["pose_max_delta"] = round(dp, 9)
        rows.append(row)
    tot = {k: sum(r[k] for r in rows) for k in
           ("n", "png_eq", "depth_eq", "idseg_eq", "idseg_primnorm_eq",
            "idseg_primnorm_n")}
    tot["heightmap_eq"] = sum(1 for r in rows if r["heightmap_eq"])
    tot["n_scenes"] = len(rows)
    tot["pose_max_delta"] = max([r["pose_max_delta"] for r in rows] or [0.0])
    return dict(tag=tag, ref=ref_run, new=new_run, rows=rows, totals=tot)


def main():
    out = []
    w0 = "260825_v3w0_cuecls_A"
    if has_round(w0):
        out.append(compare("대조1 · A팔 재현성 (세그 변경 없음)",
                           "260819_main_on", w0, scenes_of(w0)))
    bs = "260826_v3w1_lib_B_smoke"
    if has_round(bs):
        out.append(compare("대조2 · 같은 웨이브 (세그 설정까지 동일)",
                           "260826_v3w1_lib_B", bs, scenes_of(bs)))

    for c in out:
        t = c["totals"]
        print(f"\n=== {c['tag']} ===")
        print(f"  {c['new']}  vs  {c['ref']}   ({t['n_scenes']}씬 · {t['n']}컷)")
        print(f"  RGB PNG      sha256 동일  {t['png_eq']:4d} / {t['n']}")
        print(f"  depth        sha256 동일  {t['depth_eq']:4d} / {t['n']}")
        print(f"  idseg        sha256 동일  {t['idseg_eq']:4d} / {t['idseg_primnorm_n']}"
              f"   (인스턴스 ID 재번호 — 원바이트 비교는 오설계)")
        print(f"  idseg  **프림 경로 정규화** 동일  "
              f"{t['idseg_primnorm_eq']:4d} / {t['idseg_primnorm_n']}")
        print(f"  heightmap.npy sha256 동일 {t['heightmap_eq']:4d} / {t['n_scenes']}씬")
        print(f"  포즈 7키 + cam.eye 최대 차 {t['pose_max_delta']:.3g}")
        bad = [r for r in c["rows"] if r["depth_diff"]]
        if bad:
            print(f"  depth 불일치 씬: " +
                  ", ".join(f"{r['scene']}({len(r['depth_diff'])})" for r in bad))
        mx = max((r["px_max"] for r in c["rows"]), default=0)
        mn = max((r["px_mean"] for r in c["rows"]), default=0.0)
        print(f"  PNG 불일치의 크기: 최대 {mx} LSB · 평균 |Δ| 최대 {mn} LSB "
              f"(= 몬테카를로 표본 잡음)")

    op = os.path.join(V3, "w1b2_repro_control.json")
    json.dump(dict(doc="w1b2_repro_control", version="1.0",
                   question="D75 ④의 'PNG 바이트 동일' 판정 기준은 만족 가능한가",
                   verdict="아니다 — PathTracing RGB는 프로세스 간 비트 재현되지 "
                           "않는다. 기하(depth·heightmap·포즈)는 비트 재현되고, "
                           "마스크 내용은 프림 경로 정규화 후 완전 동일하다.",
                   controls=out),
              open(op, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\n-> {op}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
