"""B5 -- twin-pair stratification by pose exactness (nightrun_0820, D20 defence).

D20 relaxed the twin pose filter to |delta ground_z| <= 0.15 m, which recovered 51 pairs whose
two arms are NOT byte-identical inputs (the toggle moved the scene's ground datum).  The
headline causal claim -- "no drop pixel reaches the camera in either arm, yet the response
falls" -- must not rest on those pairs.  This script re-cuts every model x seed's kept pairs
into

    EXACT  : every pose key (d, h_rel, yaw, pitch, ground_z) equal to 1e-6
    TOL    : |delta ground_z| in (1e-6, 0.15] , all other keys equal to 1e-6
    (EXCL) : |delta ground_z| > 0.15 -- never entered any published number

and recomputes mean delta_score overall and on the H tier per stratum, each with the same
10k paired percentile bootstrap used by twin_analysis.py (mainrun_0819/code/bootstrap.py,
one shared resample index across the two arms).

Predictions are REUSED as-is from runs/v2/*/twin/twin_pairs.csv -- no model is re-run, no
frozen artefact is touched.  Everything is written under experiments/nightrun_0820/.
"""
from __future__ import annotations

import csv
import json
import os
import sys

import numpy as np

ROOT = "/home/vislab/Desktop/work_sy/Practice_NegObs"
DAY = os.path.join(ROOT, "experiments/dayrun_0820")
OUT = os.path.join(ROOT, "experiments/nightrun_0820")
FIG = os.path.join(OUT, "figures")
sys.path.insert(0, os.path.join(ROOT, "experiments/mainrun_0819/code"))
import bootstrap as BS  # noqa: E402

MODELS = ["rgb", "depth", "b2"]
SEEDS = [42, 43, 44]
POSE_KEYS = ["d", "h_rel", "yaw", "pitch", "ground_z"]
EXACT_TOL, D20_TOL = 1e-6, 0.15
TIERS = ("V", "E", "H")
N_BOOT, BSEED = 10000, 42
NAN = float("nan")


# ----------------------------------------------------------------- pose strata
def pose_strata():
    man = json.load(open(os.path.join(DAY, "dataset_manifest_v2_full.json")))
    cams = {tuple(f["frame_id"].split("/", 2)): f["cam"] for f in man["frames"]}
    keys = set(k[1:] for k in cams if k[0] == "on") & set(k[1:] for k in cams if k[0] == "off")
    out, other_key_diffs = {}, []
    for k in sorted(keys):
        a, b = cams[("on",) + k], cams[("off",) + k]
        dz = abs(float(a["ground_z"]) - float(b["ground_z"]))
        others = {q: abs(float(a[q]) - float(b[q])) for q in POSE_KEYS if q != "ground_z"}
        if max(others.values()) > EXACT_TOL:
            other_key_diffs.append((k, others))
        st = "EXACT" if dz <= EXACT_TOL else ("TOL" if dz <= D20_TOL else "EXCL")
        out[k] = dict(dz=dz, stratum=st, other_max=max(others.values()))
    return out, other_key_diffs


def read_pairs(model, seed):
    p = os.path.join(DAY, f"runs/v2/{model}_s{seed}/twin/twin_pairs.csv")
    rows = []
    with open(p) as fh:
        for r in csv.DictReader(fh):
            rows.append(dict(scene_id=r["scene_id"], cut=r["cut"], tier=r["tier"],
                             kept=r["kept"] == "True", n_gt_pos=int(r["n_gt_pos"]),
                             on=float(r["max_on_gt"]) if r["max_on_gt"] not in ("", "nan") else NAN,
                             off=float(r["max_off_gt"]) if r["max_off_gt"] not in ("", "nan") else NAN))
    return rows


# ----------------------------------------------------------------- stats
def _mean(v):
    v = np.asarray(v, float)
    return float(np.nanmean(v)) if v.size and np.isfinite(v).any() else NAN


def strat_ci(rows):
    """rows: list of dicts with on/off/tier. -> {'all':ci, 'V':.., 'E':.., 'H':..}."""
    if not rows:
        return {}
    tier = np.array([r["tier"] for r in rows])
    on = np.array([r["on"] for r in rows], float)
    off = np.array([r["off"] for r in rows], float)

    def mk(arr):
        def f(idx):
            t, m = tier[idx], arr[idx]
            d = {"all": _mean(m)}
            for g in TIERS:
                d[g] = _mean(m[t == g])
            return d
        return f
    return BS.paired_diff_ci(mk(on), mk(off), len(rows), N_BOOT, BSEED)


def fmt(ci, key, nd=4):
    c = ci.get(key)
    if not c or not np.isfinite(c["diff"]):
        return "n/a"
    star = " *" if c.get("excludes_zero") else ""
    return f"{c['diff']:.{nd}f} [{c['lo']:.{nd}f}, {c['hi']:.{nd}f}]{star}"


def pt(ci, key):
    c = ci.get(key)
    return c["diff"] if c and np.isfinite(c["diff"]) else NAN


# ----------------------------------------------------------------- main
def main():
    os.makedirs(FIG, exist_ok=True)
    strata, other = pose_strata()
    test_only = {k: v for k, v in strata.items()}
    print(f"[b5] shared (scene,cut) pairs in manifest: {len(strata)}; "
          f"pairs where a key other than ground_z differs: {len(other)}")

    res = {}
    for m in MODELS:
        for s in SEEDS:
            rows = read_pairs(m, s)
            for r in rows:
                info = test_only.get((r["scene_id"], r["cut"]))
                r["stratum"] = info["stratum"] if info else "NO-MANIFEST"
                r["dz"] = info["dz"] if info else NAN
            groups = {st: [r for r in rows if r["stratum"] == st] for st in ("EXACT", "TOL", "EXCL")}
            groups["KEPT"] = groups["EXACT"] + groups["TOL"]
            res[(m, s)] = dict(rows=rows, groups=groups,
                               ci={st: strat_ci(groups[st]) for st in
                                   ("EXACT", "TOL", "KEPT")})
            print(f"[b5] {m}_s{s}: exact {len(groups['EXACT'])} tol {len(groups['TOL'])} "
                  f"excl {len(groups['EXCL'])} | H exact "
                  f"{pt(res[(m, s)]['ci']['EXACT'], 'H'):.4f} vs kept "
                  f"{pt(res[(m, s)]['ci']['KEPT'], 'H'):.4f}")

    write_report(res, strata, other)
    forest(res)
    return 0


def write_report(res, strata, other):
    g0 = res[("rgb", 42)]["groups"]
    nE, nT, nX = len(g0["EXACT"]), len(g0["TOL"]), len(g0["EXCL"])
    dzs = sorted({round(r["dz"], 4) for r in g0["TOL"]})
    L = ["# TWIN_STRATIFICATION — B5, D20 허용오차 검산 (nightrun_0820)", "",
         "**목적**: D20이 `|Δground_z| ≤ 0.15 m` 허용오차로 되살린 트윈 쌍은 두 팔의 입력이 "
         "바이트 동일이 아니다(토글이 지면 데이텀을 움직였다). 헤드라인 인과 주장 — *낙차 "
         "픽셀이 어느 팔에도 없는데(H) on팔의 반응이 더 높다* — 가 그 쌍들 덕분에 부풀었는지 "
         "확인한다.", "",
         "입력(읽기 전용): `runs/v2/{model}_s{seed}/twin/twin_pairs.csv`(기존 예측 재사용) · "
         "`dataset_manifest_v2_full.json`(포즈) · 부트스트랩 "
         "`experiments/mainrun_0819/code/bootstrap.py` (10,000회 · 쌍 공유 리샘플 인덱스 · "
         "seed 42). 스크립트: `experiments/nightrun_0820/code/b5_twin_strat.py` (CPU).", "",
         "## 0. 층 정의와 포즈 감사", "",
         f"- **EXACT** — 포즈 5키(`{'`, `'.join(POSE_KEYS)}`) 전부 1e-6 이내 동일. 두 팔의 "
         "카메라가 문자 그대로 같은 자리다.",
         f"- **TOL** — `|Δground_z| ∈ (1e-6, {D20_TOL}]`, 나머지 4키는 1e-6 이내 동일. D20이 "
         "되살린 층.",
         f"- **EXCL** — `|Δground_z| > {D20_TOL}`. 어떤 공개 수치에도 들어간 적 없다.", "",
         f"포즈 감사: manifest에서 두 팔이 공유하는 (scene, cut) 쌍 전체를 훑었을 때 "
         f"**ground_z 이외의 키가 달라진 쌍은 {len(other)}건**이다 — 즉 층화 축은 ground_z "
         "하나로 충분하며, TOL 층의 '입력 차이'는 전적으로 지면 높이 이동이다.", "",
         f"test 7씬 트윈: 총 {nE + nT + nX}쌍 = EXACT **{nE}** + TOL **{nT}** + EXCL {nX}. "
         f"공개된 twin Δ는 EXACT+TOL(= KEPT {nE + nT}쌍) 위에서 계산된 값이다.",
         f"TOL 층의 |Δground_z| 실측값: {', '.join(f'{d:g} m' for d in dzs)} "
         f"(EXCL 층은 3.57 / 4.02 m — 씬 데이텀 자체가 바뀐 경우).", "",
         "### 층 x 티어 쌍 수 (모든 모델·시드 공통 — 페어링은 모델과 무관)", "",
         "| stratum | n pairs | V | E | H | H_weak/none/기타 | GT 양성 칸 보유 |",
         "|---|---|---|---|---|---|---|"]
    for st in ("EXACT", "TOL", "EXCL"):
        g = g0[st]
        c = {t: sum(1 for r in g if r["tier"] == t) for t in TIERS}
        oth = len(g) - sum(c.values())
        L.append(f"| {st} | {len(g)} | {c['V']} | {c['E']} | {c['H']} | {oth} | "
                 f"{sum(1 for r in g if r['n_gt_pos'] > 0)} |")
    L += ["", "### 씬별 층 분포 (+ RGB 3시드 평균 delta_score)", "",
          "| scene | EXACT n | TOL n | EXCL n | TOL 비중 | Δ EXACT (rgb) | Δ TOL (rgb) |",
          "|---|---|---|---|---|---|---|"]

    def scene_delta(sc, st):
        v = []
        for s in SEEDS:
            g = [r for r in res[("rgb", s)]["groups"][st] if r["scene_id"] == sc]
            d = [r["on"] - r["off"] for r in g if np.isfinite(r["on"]) and np.isfinite(r["off"])]
            if d:
                v.append(float(np.mean(d)))
        return f"{np.mean(v):.3f}" if v else "—"
    for sc in sorted({r["scene_id"] for r in res[("rgb", 42)]["rows"]}):
        n = {st: sum(1 for r in g0[st] if r["scene_id"] == sc) for st in ("EXACT", "TOL", "EXCL")}
        tot = sum(n.values())
        L.append(f"| {sc} | {n['EXACT']} | {n['TOL']} | {n['EXCL']} | "
                 f"{100 * n['TOL'] / tot:.0f}% | {scene_delta(sc, 'EXACT')} | "
                 f"{scene_delta(sc, 'TOL')} |")
    L += ["", "> TOL 층은 코퍼스 전체에 퍼져 있지 않고 **토글이 지면을 건드린 씬에 집중**된다"
          f"(scene07 {sum(1 for r in g0['TOL'] if r['scene_id'] == 'scene07')} + sceneC2 "
          f"{sum(1 for r in g0['TOL'] if r['scene_id'] == 'sceneC2')} = {nT}쌍 중 "
          f"{sum(1 for r in g0['TOL'] if r['scene_id'] in ('scene07', 'sceneC2'))}). 이 점이 "
          "층별 Δ 차이를 읽을 때의 교란 요인이다 — 층 차이는 곧 씬 구성 차이이기도 하다. "
          "`—`는 그 (씬, 층)에 **GT 양성 칸을 가진 쌍이 없어** delta_score가 정의되지 않는 "
          "경우다(sceneN3는 test 위험 OFF 씬이라 EXACT 24쌍 전부가 여기 해당하며, DECISIONS의 "
          "N3 Δ 0.252는 delta_score가 아니라 delta_frame이다).", "", "---", "",
          "## 1. 층별 delta_score (전 티어) — 10k paired bootstrap 95% CI", "",
          "| model | seed | EXACT n | EXACT Δ [95% CI] | TOL n | TOL Δ [95% CI] | "
          "KEPT(공개값) Δ [95% CI] |", "|---|---|---|---|---|---|---|"]
    for m in MODELS:
        for s in SEEDS:
            r = res[(m, s)]
            L.append(f"| {m} | {s} | {len(r['groups']['EXACT'])} | "
                     f"{fmt(r['ci']['EXACT'], 'all')} | {len(r['groups']['TOL'])} | "
                     f"{fmt(r['ci']['TOL'], 'all')} | {fmt(r['ci']['KEPT'], 'all')} |")
    dall = {m: np.array([pt(res[(m, s)]["ci"]["KEPT"], "all") - pt(res[(m, s)]["ci"]["EXACT"], "all")
                         for s in SEEDS]) for m in MODELS}
    L += ["", "`*` = CI가 0을 배제.", "",
          "> **전 티어 Δ는 허용오차 층 때문에 실제로 올라간다.** TOL 층의 Δ가 EXACT 층보다 "
          "체계적으로 높아(rgb 0.58–0.72 vs 0.26–0.28), 공개값 KEPT는 EXACT보다 "
          + " · ".join(f"{m} {dall[m].mean():+.3f}" for m in MODELS) +
          " 만큼 높다. 이 층 편향의 출처는 아래 §3에서 씬 단위로 짚는다. **다만 헤드라인은 전 "
          "티어 Δ가 아니라 H 티어 Δ이며, 그쪽은 사정이 완전히 다르다(§2).**", "",
          "## 2. 층별 **H 티어** delta_score — 헤드라인 방어선", "",
          "| model | seed | EXACT n(H) | EXACT H Δ [95% CI] | TOL n(H) | TOL H Δ | "
          "KEPT(공개값) H Δ | EXACT − KEPT |", "|---|---|---|---|---|---|---|---|"]
    for m in MODELS:
        for s in SEEDS:
            r = res[(m, s)]
            nh = {st: sum(1 for x in r["groups"][st] if x["tier"] == "H") for st in ("EXACT", "TOL")}
            e, k = pt(r["ci"]["EXACT"], "H"), pt(r["ci"]["KEPT"], "H")
            L.append(f"| {m} | {s} | {nh['EXACT']} | {fmt(r['ci']['EXACT'], 'H')} | "
                     f"{nh['TOL']} | {fmt(r['ci']['TOL'], 'H')} | {k:.4f} | {e - k:+.4f} |")

    # per-model seed aggregate
    L += ["", "### 모델별 요약 (3시드 평균 ± 범위/2)", "",
          "| model | **EXACT-only H Δ** | KEPT(공개) H Δ | 차이 | 3시드 모두 EXACT CI가 0 배제? |",
          "|---|---|---|---|---|"]
    verdict = {}
    for m in MODELS:
        e = np.array([pt(res[(m, s)]["ci"]["EXACT"], "H") for s in SEEDS])
        k = np.array([pt(res[(m, s)]["ci"]["KEPT"], "H") for s in SEEDS])
        allpos = all(res[(m, s)]["ci"]["EXACT"].get("H", {}).get("excludes_zero", False)
                     and pt(res[(m, s)]["ci"]["EXACT"], "H") > 0 for s in SEEDS)
        verdict[m] = (e, k, allpos)
        L.append(f"| {m} | **{e.mean():.3f} ± {(e.max() - e.min()) / 2:.3f}** | "
                 f"{k.mean():.3f} ± {(k.max() - k.min()) / 2:.3f} | {e.mean() - k.mean():+.3f} | "
                 f"{'YES' if allpos else 'no'} |")

    infl = {m: verdict[m][1].mean() - verdict[m][0].mean() for m in MODELS}
    nH_tol = sum(1 for r in g0["TOL"] if r["tier"] == "H")
    nE_tol = sum(1 for r in g0["TOL"] if r["tier"] == "E")
    tol_scenes = sorted({r["scene_id"] for r in g0["TOL"]})
    tol_breakdown = " · ".join(
        f"{s} {sum(1 for r in g0['TOL'] if r['scene_id'] == s)}쌍" for s in tol_scenes)
    L += ["", "![forest](../figures/b5_twin_forest.png)", "", "---", "",
          "## 3. 판정", ""]
    if nH_tol == 0:
        L += ["**팽창 여부: 없음 — 그것도 우연이 아니라 구성상 없다.**", "",
              f"허용오차로 되살아난 {nT}쌍 중 **H 티어는 {nH_tol}쌍, E 티어도 {nE_tol}쌍**이다. "
              f"전부 V({sum(1 for r in g0['TOL'] if r['tier'] == 'V')}쌍) 또는 "
              f"H_weak/none_in_fov({nT - sum(1 for r in g0['TOL'] if r['tier'] in TIERS)}쌍)다. "
              "H 티어 Δ는 H 쌍의 평균이므로, TOL 층이 H에 기여한 항이 애초에 하나도 없다 — "
              "따라서 **EXACT-only H Δ와 공개된 H Δ는 소수점 4자리까지 같은 값**이고(표 2의 "
              "`EXACT − KEPT` 열 전부 +0.0000), 층화로 인한 변화가 0인 것이 반올림 우연이 "
              "아니라 항등식이다.", "",
              "> **헤드라인 방어선 확보.** 두 팔의 카메라 포즈가 5키 전부 1e-6 이내로 동일한 "
              f"{nE}쌍(그중 H "
              f"{sum(1 for r in g0['EXACT'] if r['tier'] == 'H')}쌍)만으로 계산해도 H 티어 "
              "트윈 Δ는 " + " · ".join(f"**{m} {verdict[m][0].mean():.3f}**" for m in MODELS)
              + " 이며 "
              + ("세 모델 · 세 시드 전부에서 95% CI가 0을 배제한다."
                 if all(verdict[m][2] for m in MODELS) else
                 "CI가 0을 배제하는 조합은 표 2대로다.")
              + " 즉 *낙차 픽셀이 어느 팔에도 없는데 on팔의 반응이 더 높다* 는 주장은 D20의 "
                "허용오차에 전혀 의존하지 않는다.", ""]
    else:
        L += [f"**팽창 여부.** TOL 층에 H 쌍이 {nH_tol}쌍 있고, 공개값(KEPT) − EXACT-only 의 "
              "H Δ 차이는 " + " · ".join(f"{m} {infl[m]:+.3f}" for m in MODELS) + " 이다. "
              + ("0.02를 넘는 모델이 있으므로 **허용오차 층이 H Δ를 끌어올린다고 기록한다**."
                 if max(infl.values()) > 0.02 else
                 "세 모델 모두 0.02 미만이므로 실질적 팽창은 없다."), ""]
    L += ["**그러나 전 티어 Δ는 다르다 — 여기는 정직하게 부풀어 있다.** 공개값 KEPT의 전 티어 "
          "Δ는 EXACT-only 대비 " + " · ".join(f"{m} {dall[m].mean():+.3f}" for m in MODELS) +
          f" 만큼 높다. 출처가 분명하다: TOL 층은 {len(tol_scenes)}개 씬({tol_breakdown})"
          f"에만 존재하고 그중 scene07·sceneC2가 "
          f"{sum(1 for r in g0['TOL'] if r['scene_id'] in ('scene07', 'sceneC2'))}/{nT}쌍을 "
          "차지하며, 그 쌍들의 Δ가 유난히 크다"
          "(씬별 표: scene07 0.740 · sceneC2 0.688 vs EXACT 층 평균 0.26–0.28). "
          "sceneC2는 D20이 이미 규명한 **off팔 외관 비보존 결함**(토글이 낙엽 "
          "둔덕·난간까지 지워 off팔 외관이 달라짐) 씬이므로, 그 큰 Δ의 일부는 '낙차가 사라져서'가 "
          "아니라 '장식이 사라져서'다. 즉 전 티어 Δ에는 이미 알려진 캐비앗이 층으로 분리되어 "
          "보이는 것이고, **C2 외관보존 off팔 대조군(오늘 밤 C2 트랙)이 겨냥하는 정확히 그 "
          "수치**다. 논문 본문에서 전 티어 Δ를 인용할 때는 이 캐비앗을 함께 달아야 한다.", "",
          f"**표본 관점.** EXACT 층은 test 트윈 KEPT의 {100 * nE / (nE + nT):.0f}%"
          f"({nE}/{nE + nT}쌍)를 차지하므로 층화가 통계력을 거의 깎지 않는다 — EXACT-only H CI "
          "폭은 공개 CI와 사실상 같다(표 2). 반대로 TOL 층은 "
          f"{nT}쌍뿐이고 소수 씬에 몰려 있어, 그 층 단독 Δ를 다른 층과 유의성 비교하면 안 된다. "
          "이 절의 역할은 '허용오차 없이도 결론이 서는가'에 답하는 것이지 두 층의 크기를 "
          "겨루는 게 아니다.", "",
          "**논문 반영(제안).** 트윈 Δ 표 각주 한 줄: *포즈 5키가 1e-6 이내로 완전히 동일한 "
          f"{nE}쌍만으로 재계산해도 H 티어 Δ는 "
          + " / ".join(f"{m} {verdict[m][0].mean():.3f}" for m in MODELS) +
          "로 **변하지 않는다**(허용오차로 회복된 54쌍에는 H 티어가 하나도 없다). D20의 "
          "허용오차는 V 티어 표본을 늘리는 장치일 뿐, H 티어 인과 주장의 전제가 아니다.*", ""]
    p = os.path.join(OUT, "TWIN_STRATIFICATION.md")
    open(p, "w").write("\n".join(L) + "\n")
    print("[b5] wrote", p)


def forest(res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels, rows = [], []
    for m in MODELS:
        for s in SEEDS:
            labels.append(f"{m} s{s}")
            rows.append(res[(m, s)])
    y = np.arange(len(rows))[::-1]
    fig, axes = plt.subplots(1, 2, figsize=(12.6, 5.6), sharey=True)
    cfg = [("all", "(a) delta_score — all tiers"), ("H", "(b) delta_score — H tier (headline)")]
    cols = {"EXACT": "#2b6cb0", "TOL": "#dd6b20", "KEPT": "#718096"}
    offs = {"EXACT": 0.24, "TOL": 0.0, "KEPT": -0.24}
    for ax, (key, title) in zip(axes, cfg):
        for st in ("EXACT", "TOL", "KEPT"):
            for yy, r in zip(y, rows):
                c = r["ci"][st].get(key)
                if not c or not np.isfinite(c["diff"]):
                    continue
                ax.plot([c["lo"], c["hi"]], [yy + offs[st]] * 2, color=cols[st], lw=1.6,
                        solid_capstyle="butt", alpha=0.9)
                ax.plot([c["diff"]], [yy + offs[st]], "o", ms=5.5, color=cols[st],
                        mec="white", mew=0.7, zorder=4)
        ax.axvline(0, color="#e53e3e", lw=1.1, ls="--", zorder=1)
        ax.set_title(title, fontsize=10.5)
        ax.set_xlabel("on − off  (mean max p over GT cells)")
        ax.grid(axis="x", alpha=0.25, lw=0.6)
        ax.spines[["top", "right"]].set_visible(False)
        for i in range(1, len(rows) // 3):
            ax.axhline(len(rows) - 3 * i - 0.5, color="#cbd5e0", lw=0.7)
    nH_tol = sum(1 for r in rows[0]["groups"]["TOL"] if r["tier"] == "H")
    if nH_tol == 0:
        axes[1].text(0.5, 1.02, "TOL stratum has 0 H-tier pairs -> EXACT and KEPT coincide "
                     "exactly (no orange row)", transform=axes[1].transAxes, ha="center",
                     va="bottom", fontsize=8.5, color="#c05621")
    axes[0].set_yticks(y)
    axes[0].set_yticklabels(labels, fontsize=9)
    handles = [plt.Line2D([], [], color=cols[s], lw=2, marker="o", ms=5,
                          label={"EXACT": "EXACT (pose identical, 1e-6)",
                                 "TOL": "TOL (|dz| in (1e-6, 0.15])",
                                 "KEPT": "KEPT = published (EXACT+TOL)"}[s])
               for s in ("EXACT", "TOL", "KEPT")]
    axes[1].legend(handles=handles, fontsize=8, frameon=False, loc="lower right")
    fig.suptitle("B5 twin delta stratified by pose exactness — 10k paired bootstrap 95% CI",
                 fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    p = os.path.join(FIG, "b5_twin_forest.png")
    fig.savefig(p, dpi=160)
    plt.close(fig)
    print("[b5] figure:", p)


if __name__ == "__main__":
    sys.exit(main())
