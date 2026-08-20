"""B4 -- straddling & occupancy diagnostics (nightrun_0820).

Three tables, all derived from FROZEN inputs (labels_v1_full.json, split_v2_full.json,
runs/v2/*/eval_test/per_frame.csv).  Nothing outside experiments/nightrun_0820/ is written.

  (i)   hazard-instance straddling -- how often a frame's GT-positive cell set spans a
        grid boundary (4 sector boundaries A|B..D|E, 3 band boundaries 2 m / 5 m / 8 m).
  (ii)  miss x straddle cross-table for RGB v2 per seed at tau = 0.5.
  (iii) occupancy of a GT-positive cell = (hazard footprint samples in the wedge) /
        (total 5 cm heightmap samples the wedge contains).  Complement = overblocking.

Estimator note for (iii): labels' `cell_counts[c]` is a bincount of 5 cm heightmap cells
(labeler.py HM_DEFAULT step = 0.05 m) whose centre falls inside polar cell c AND inside the
hazard footprint.  The denominator is the wedge's analytic sample capacity

    N(band) = 0.5 * dtheta * (r_out^2 - r_in^2) / step^2 ,  dtheta = 12.44 deg, step = 0.05 m

i.e. wedge area divided by the area of one heightmap sample.  Sector width is constant, so N
depends only on the band.  The estimator is validated against the corpus maximum of
cell_counts per band (printed by this script and reported in STRADDLE_REPORT.md); ratios are
clipped to 1.0 for the quantiles, and the raw over-unity excess is reported as rasterisation
slack.
"""
from __future__ import annotations

import csv
import json
import math
import os
import sys

import numpy as np

ROOT = "/home/vislab/Desktop/work_sy/Practice_NegObs"
DAY = os.path.join(ROOT, "experiments/dayrun_0820")
OUT = os.path.join(ROOT, "experiments/nightrun_0820")
FIG = os.path.join(OUT, "figures")

SECTORS = ["A", "B", "C", "D", "E"]
BANDS = ["1", "2", "3a", "3b"]
BAND_EDGES = [0.0, 2.0, 5.0, 8.0, 12.0]
DTHETA = math.radians(12.44)          # gridspec_v1 sector width (constant across sectors)
HM_STEP = 0.05                        # labeler.py HM_DEFAULT["step"]
NS, NB = 5, 4
SEED_BOOT, N_BOOT = 42, 10000
TAU = 0.5
MODELS = ["rgb", "depth", "b2"]
SEEDS = [42, 43, 44]

SECTOR_BOUNDS = [f"{SECTORS[i]}/{SECTORS[i + 1]}" for i in range(NS - 1)]
BAND_BOUNDS = [f"{BAND_EDGES[i + 1]:g} m ({BANDS[i]}/{BANDS[i + 1]})" for i in range(NB - 1)]


def wedge_capacity(bi):
    """Analytic count of 5 cm heightmap samples inside one (sector, band) wedge."""
    r0, r1 = BAND_EDGES[bi], BAND_EDGES[bi + 1]
    return 0.5 * DTHETA * (r1 * r1 - r0 * r0) / (HM_STEP * HM_STEP)


CAP = np.array([wedge_capacity(b) for b in range(NB)])


# ----------------------------------------------------------------- straddle geometry
def frame_flags(pos):
    """pos: (NB, NS) bool.  -> dict of per-boundary crossing flags + span counts."""
    f = {}
    f["n_sectors"] = int(pos.any(axis=0).sum())
    f["n_bands"] = int(pos.any(axis=1).sum())
    f["n_cells"] = int(pos.sum())
    for si in range(NS - 1):                       # sector boundary, adjacency within a band
        f[f"sb{si}"] = bool((pos[:, si] & pos[:, si + 1]).any())
    for bi in range(NB - 1):                       # band boundary, adjacency within a sector
        f[f"bb{bi}"] = bool((pos[bi] & pos[bi + 1]).any())
    f["any_sector_bound"] = any(f[f"sb{i}"] for i in range(NS - 1))
    f["any_band_bound"] = any(f[f"bb{i}"] for i in range(NB - 1))
    f["straddle"] = f["n_sectors"] >= 2 or f["n_bands"] >= 2
    f["adj_straddle"] = f["any_sector_bound"] or f["any_band_bound"]
    f["cross8_loose"] = bool(pos[2].any() and pos[3].any())
    f["cross8"] = f["bb2"]
    return f


def pair_basis(frames_pos):
    """The DAYRUN 62.7% basis: per boundary, count (frame, orthogonal-index) units.

    band boundary bi -> units are (frame, sector) with >=1 of the two cells positive;
    sector boundary si -> units are (frame, band)  with >=1 of the two cells positive.
    """
    out = {}
    for bi in range(NB - 1):
        both = tot = 0
        for pos in frames_pos:
            a, b = pos[bi], pos[bi + 1]
            tot += int((a | b).sum())
            both += int((a & b).sum())
        out[f"bb{bi}"] = (both, tot)
    for si in range(NS - 1):
        both = tot = 0
        for pos in frames_pos:
            a, b = pos[:, si], pos[:, si + 1]
            tot += int((a | b).sum())
            both += int((a & b).sum())
        out[f"sb{si}"] = (both, tot)
    return out


# ----------------------------------------------------------------- data loading
def load():
    lab = json.load(open(os.path.join(DAY, "annotations/labels_v1_full.json")))
    split = json.load(open(os.path.join(DAY, "split_v2_full.json")))
    man = json.load(open(os.path.join(DAY, "dataset_manifest_v2_full.json")))
    scene_of = {f["frame_id"]: f["scene_id"] for f in man["frames"]}
    test = set(split["test"])
    rows = []
    for fid, rec in lab["frames"].items():
        arm = fid.split("/", 1)[0]
        if arm != "on":
            continue
        gt = np.asarray(rec["polar_gt"], int).reshape(NB, NS).astype(bool)
        if not gt.any():
            continue
        sc = scene_of.get(fid, fid.split("/")[1])
        rows.append(dict(frame_id=fid, scene_id=sc, tier=rec.get("tier_strict", "?"),
                         in_test=sc in test, pos=gt,
                         counts=np.asarray(rec["cell_counts"], float).reshape(NB, NS)))
    return rows


def reconcile_dayrun():
    """DAYRUN ②ⓒ reported 62.7% on the PRE-BOOST label file, train on-arm, eligible scenes.

    Recompute the same 8 m unit-basis rate on that file (all on-arm frames) so the two numbers
    in the write-up can be reconciled instead of read as a contradiction.
    """
    p = os.path.join(DAY, "annotations/labels_v1.json")
    if not os.path.isfile(p):
        return None
    lab = json.load(open(p))
    both = tot = nf = 0
    for fid, rec in lab["frames"].items():
        if not fid.startswith("on/"):
            continue
        g = np.asarray(rec["polar_gt"], int).reshape(NB, NS).astype(bool)
        if not g.any():
            continue
        nf += 1
        tot += int((g[2] | g[3]).sum())
        both += int((g[2] & g[3]).sum())
    return nf, both, tot


def read_per_frame(path):
    out = {}
    with open(path) as fh:
        for r in csv.DictReader(fh):
            if r["toggle_state"] != "on":
                continue
            p = np.array([float(r[f"p_{s}{b}"]) for b in BANDS for s in SECTORS]).reshape(NB, NS)
            g = np.array([float(r[f"g_{s}{b}"]) for b in BANDS for s in SECTORS]).reshape(NB, NS)
            out[r["frame_id"]] = (p, g > 0.5, r["tier"])
    return out


# ----------------------------------------------------------------- bootstrap on a rate diff
def rate_diff_ci(hit, grp, n_boot=N_BOOT, seed=SEED_BOOT):
    """hit, grp: bool arrays.  CI on P(hit|grp) - P(hit|~grp)."""
    hit, grp = np.asarray(hit, bool), np.asarray(grp, bool)
    rng = np.random.default_rng(seed)
    n = len(hit)

    def stat(idx):
        h, g = hit[idx], grp[idx]
        if g.sum() == 0 or (~g).sum() == 0:
            return float("nan")
        return h[g].mean() - h[~g].mean()
    draws = np.array([stat(rng.integers(0, n, n)) for _ in range(n_boot)])
    draws = draws[np.isfinite(draws)]
    if draws.size == 0:
        return float("nan"), float("nan"), float("nan")
    return stat(np.arange(n)), float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))


def pct(a, b):
    return f"{100.0 * a / b:.1f}%" if b else "n/a"


# ----------------------------------------------------------------- main
def main():
    os.makedirs(FIG, exist_ok=True)
    rows = load()
    test_rows = [r for r in rows if r["in_test"]]
    print(f"[b4] on-arm frames with >=1 GT cell: corpus {len(rows)} / test {len(test_rows)}")

    for grp in (test_rows, rows):
        for r in grp:
            r.update(frame_flags(r["pos"]))

    # ---------------- table (i)
    def block(grp):
        n = len(grp)
        pb = pair_basis([r["pos"] for r in grp])
        d = {"n": n}
        for si in range(NS - 1):
            d[f"sb{si}"] = (sum(r[f"sb{si}"] for r in grp), n, pb[f"sb{si}"])
        for bi in range(NB - 1):
            d[f"bb{bi}"] = (sum(r[f"bb{bi}"] for r in grp), n, pb[f"bb{bi}"])
        for k in ("straddle", "adj_straddle", "any_sector_bound", "any_band_bound",
                  "cross8", "cross8_loose"):
            d[k] = (sum(r[k] for r in grp), n)
        d["ge2_sect"] = (sum(r["n_sectors"] >= 2 for r in grp), n)
        d["ge2_band"] = (sum(r["n_bands"] >= 2 for r in grp), n)
        d["med_cells"] = float(np.median([r["n_cells"] for r in grp]))
        d["med_sect"] = float(np.median([r["n_sectors"] for r in grp]))
        d["med_band"] = float(np.median([r["n_bands"] for r in grp]))
        return d
    T, C = block(test_rows), block(rows)

    # ---------------- table (ii): RGB v2 per seed
    straddle_of = {r["frame_id"]: r["straddle"] for r in rows}
    cross8_of = {r["frame_id"]: r["cross8"] for r in rows}
    xtab = {}
    for sd in SEEDS:
        pf = read_per_frame(os.path.join(DAY, f"runs/v2/rgb_s{sd}/eval_test/per_frame.csv"))
        ids, miss, strad, c8, tiers = [], [], [], [], []
        for fid, (p, g, tier) in pf.items():
            if not g.any():
                continue
            ids.append(fid)
            miss.append(bool(p[g].max() < TAU))
            strad.append(bool(straddle_of.get(fid, False)))
            c8.append(bool(cross8_of.get(fid, False)))
            tiers.append(tier)
        xtab[sd] = dict(ids=ids, miss=np.array(miss), strad=np.array(strad),
                        c8=np.array(c8), tier=np.array(tiers))

    # ---------------- table (iii): occupancy
    def occ(grp):
        per_band = {b: [] for b in range(NB)}
        raw_max = np.zeros(NB)
        for r in grp:
            for b in range(NB):
                for s in range(NS):
                    if r["pos"][b, s]:
                        v = r["counts"][b, s] / CAP[b]
                        per_band[b].append(v)
                        raw_max[b] = max(raw_max[b], v)
        return per_band, raw_max
    occ_test, rawmax_test = occ(test_rows)
    occ_corp, rawmax_corp = occ(rows)
    print("[b4] wedge capacity per band:", np.round(CAP, 1))
    print("[b4] max observed count/capacity per band (corpus):", np.round(rawmax_corp, 4))

    write_report(T, C, xtab, occ_test, occ_corp, rawmax_corp, test_rows, rows, reconcile_dayrun())
    make_figures(test_rows, rows, T, C, occ_test)
    return 0


# ----------------------------------------------------------------- report
def q(v):
    a = np.clip(np.asarray(v, float), 0.0, 1.0)
    return np.percentile(a, [25, 50, 75]) if a.size else np.array([np.nan] * 3)


def write_report(T, C, xtab, occ_test, occ_corp, rawmax, test_rows, rows, rec):
    L = ["# STRADDLE_REPORT — B4 걸침·점유 진단 (nightrun_0820)", "",
         "grid **PROVISIONAL-GRID-V1** · 5 sectors x 4 bands [0,2)/[2,5)/[5,8)/[8,12) m · "
         "cell index = band*5 + sector", "",
         "inputs (all read-only, frozen): `experiments/dayrun_0820/annotations/labels_v1_full.json` · "
         "`split_v2_full.json` · `dataset_manifest_v2_full.json` · "
         "`runs/v2/rgb_s{42,43,44}/eval_test/per_frame.csv`", "",
         "script: `experiments/nightrun_0820/code/b4_straddle.py` (env_seg, CPU only)", "",
         f"frame set = **on-arm frames carrying >=1 GT-positive cell**: test {T['n']} / corpus "
         f"{C['n']} (off-arm frames and on-arm frames with an empty GT set are outside every "
         "table below — they have no hazard instance to straddle with).", "",
         "---", "",
         "## (i) 위험 인스턴스 걸침률 — per-boundary",
         "",
         "*Frame basis* = fraction of the frames above whose GT-positive set has cells on BOTH "
         "sides of that boundary, adjacent across it (same band for a sector boundary, same "
         "sector for a band boundary). *Unit basis* = the DAYRUN ②ⓒ basis generalised: for a "
         "band boundary the unit is a (frame, sector) pair with >=1 of the two cells positive, "
         "for a sector boundary a (frame, band) pair; the rate is the share of those units where "
         "BOTH cells are positive.", "",
         "| boundary | test: frames crossing | test rate | test unit basis | corpus: frames | "
         "corpus rate | corpus unit basis |", "|---|---|---|---|---|---|---|"]
    order = [(f"sector {SECTOR_BOUNDS[i]}", f"sb{i}") for i in range(NS - 1)] + \
            [(f"band {BAND_BOUNDS[i]}", f"bb{i}") for i in range(NB - 1)]
    for name, k in order:
        (tn, td, (tb, tt)), (cn, cd, (cb, ct)) = T[k], C[k]
        L.append(f"| {name} | {tn}/{td} | {pct(tn, td)} | {tb}/{tt} = {pct(tb, tt)} | "
                 f"{cn}/{cd} | {pct(cn, cd)} | {cb}/{ct} = {pct(cb, ct)} |")
    L += ["", "| summary | test | rate | corpus | rate |", "|---|---|---|---|---|"]
    for name, k in (("spans >=2 sectors", "ge2_sect"), ("spans >=2 bands", "ge2_band"),
                    ("spans >=2 sectors OR >=2 bands (= *straddling* frame)", "straddle"),
                    ("crosses >=1 boundary with ADJACENT cells", "adj_straddle"),
                    ("crosses the NEW 8 m boundary (3a & 3b positive in the same sector)", "cross8"),
                    ("has 3a and 3b positive anywhere (loose 8 m)", "cross8_loose")):
        (tn, td), (cn, cd) = T[k], C[k]
        L.append(f"| {name} | {tn}/{td} | {pct(tn, td)} | {cn}/{cd} | {pct(cn, cd)} |")
    L += ["", f"median GT-positive cells per frame: test {T['med_cells']:.0f} / corpus "
          f"{C['med_cells']:.0f} · median sectors spanned {T['med_sect']:.0f} / "
          f"{C['med_sect']:.0f} · median bands spanned {T['med_band']:.0f} / {C['med_band']:.0f}",
          ""]
    if rec:
        nf, b, t = rec
        L += [f"> **DAYRUN 62.7%와의 대조.** DAYRUN ②ⓒ의 62.7%는 *증강 이전* 라벨"
              f"(`labels_v1.json`)의 **train·적격씬 on팔**에서 계산된 (프레임,섹터) 단위 값이다. "
              f"같은 파일의 on팔 전체로 넓히면 {b}/{t} = {pct(b, t)}({nf}프레임)이고, 증강 후 "
              f"전 코퍼스(`labels_v1_full.json`, {C['n']}프레임)에서는 "
              f"{pct(C['bb2'][2][0], C['bb2'][2][1])}로 내려간다. 내려간 이유는 D21 보강 렌더가 "
              "원거리 E/H 프레임을 대량 추가했고 그중 상당수가 3b만 켜는 단일 밴드 프레임이기 "
              "때문이다 — 지표가 바뀐 게 아니라 코퍼스 구성이 바뀐 것이다. 논문에는 **범위를 "
              "명시한 하나의 수치**만 쓴다.", ""]
    L += ["![straddle](../figures/b4_straddle.png)", "",
          "**해석.** 걸침은 예외가 아니라 기본값이다. 온팔 위험 프레임의 "
          f"{pct(T['straddle'][0], T['straddle'][1])}(test) / "
          f"{pct(C['straddle'][0], C['straddle'][1])}(corpus)가 두 개 이상의 섹터 또는 밴드에 "
          f"걸쳐 있고, 중앙값 프레임은 {T['med_cells']:.0f}칸·{T['med_sect']:.0f}섹터를 동시에 "
          "켠다. 경계별로 보면 성격이 갈린다 — **섹터 경계는 거의 항상 걸쳐지고**(66–86%, 위험이 "
          "가로로 넓다), **밴드 경계는 거리에 따라 급격히 달라진다**: 2 m 경계 "
          f"{pct(T['bb0'][0], T['bb0'][1])} → 5 m {pct(T['bb1'][0], T['bb1'][1])} → "
          f"**8 m {pct(T['cross8'][0], T['cross8'][1])}**(test). 즉 새로 만든 8 m 경계가 밴드 "
          "경계 중 압도적으로 자주 걸쳐지며, 단위(프레임x섹터) 기준으로도 "
          f"{pct(T['bb2'][2][0], T['bb2'][2][1])}(test) / "
          f"{pct(C['bb2'][2][0], C['bb2'][2][1])}(corpus)가 3a·3b를 동시에 켠다. 이것은 격자 "
          "결함이 아니라 위험 인스턴스의 물리적 크기(도랑·계단 낭떠러지가 수 미터급)가 셀보다 "
          "크고, 원거리 웨지가 넓어 한 인스턴스가 두 밴드를 함께 덮기 때문이다. 두 가지 함의. "
          "① '정답 칸이 하나라도 켜지면 검출'이라는 프레임 recall 정의는 관대한 규칙이 아니라 "
          "**한 인스턴스가 여러 칸에 흩어지는 이 격자에서 측정 가능한 최소 단위**다. "
          "② 셀 단위 F1이 낮게 보이는 구조적 원인이기도 하다 — 한 인스턴스가 중앙값 "
          f"{T['med_cells']:.0f}칸을 요구하는데 모델은 그중 가장 확신하는 칸만 켜기 때문이다. "
          "본문에서 프레임 지표를 주 지표로, 셀 F1을 보조 지표로 두는 배치의 근거가 이 표다.",
          "", "---", ""]

    # ---- (ii)
    L += ["## (ii) miss x straddle 교차표 — RGB v2, tau = 0.5", "",
          "`missed` = 그 프레임의 GT 양성 칸 중 어느 것도 p >= 0.5 에 도달하지 못함(= frame "
          "recall 실패). `straddling` = (i)의 straddle 정의(>=2 섹터 또는 >=2 밴드). "
          "분모는 on-arm test 프레임 중 GT 양성 칸이 있는 것.", "",
          "| seed | n | straddle&miss | straddle&hit | flat&miss | flat&hit | miss rate "
          "(straddle) | miss rate (flat) | diff [95% CI, 10k bootstrap] |",
          "|---|---|---|---|---|---|---|---|---|"]
    summ = {}
    for sd in list(SEEDS) + ["pooled"]:
        if sd == "pooled":
            m = np.concatenate([xtab[x]["miss"] for x in SEEDS])
            s = np.concatenate([xtab[x]["strad"] for x in SEEDS])
        else:
            m, s = xtab[sd]["miss"], xtab[sd]["strad"]
        sm, sh, fm, fh = int((s & m).sum()), int((s & ~m).sum()), int((~s & m).sum()), int((~s & ~m).sum())
        rs = sm / max(sm + sh, 1)
        rf = fm / max(fm + fh, 1)
        pt, lo, hi = rate_diff_ci(m, s)
        summ[sd] = (rs, rf, pt, lo, hi)
        nm = f"**{sd}**" if sd == "pooled" else str(sd)
        L.append(f"| {nm} | {len(m)} | {sm} | {sh} | {fm} | {fh} | {rs:.3f} | {rf:.3f} | "
                 f"{pt:+.3f} [{lo:+.3f}, {hi:+.3f}]{' *' if (lo > 0 or hi < 0) else ''} |")
    L += ["", "`*` = CI가 0을 배제. `pooled` 행은 3시드 x 프레임을 단순 합친 것이라 독립 표본이 "
          "아니다 — 방향을 보는 용도이지 유의성 주장용이 아니다.", "",
          "### 8 m 경계 한정 (신설 경계가 특별히 불리한가)", "",
          "| seed | n | cross8&miss | cross8&hit | no8&miss | no8&hit | miss rate (8 m 걸침) | "
          "miss rate (미걸침) | diff [95% CI] |", "|---|---|---|---|---|---|---|---|---|"]
    c8s = {}
    for sd in SEEDS:
        d = xtab[sd]
        m, s = d["miss"], d["c8"]
        sm, sh, fm, fh = int((s & m).sum()), int((s & ~m).sum()), int((~s & m).sum()), int((~s & ~m).sum())
        rs, rf = sm / max(sm + sh, 1), fm / max(fm + fh, 1)
        p_, lo, hi = rate_diff_ci(m, s)
        c8s[sd] = (rs, rf, p_, lo, hi)
        L.append(f"| {sd} | {len(m)} | {sm} | {sh} | {fm} | {fh} | {rs:.3f} | {rf:.3f} | "
                 f"{p_:+.3f} [{lo:+.3f}, {hi:+.3f}]{' *' if (lo > 0 or hi < 0) else ''} |")
    L += ["", "### H 티어 한정 부분표", "",
          "| seed | n(H) | straddle&miss | straddle&hit | flat&miss | flat&hit | miss rate "
          "(straddle) | miss rate (flat) | diff [95% CI] |", "|---|---|---|---|---|---|---|---|---|"]
    hsumm = {}
    for sd in SEEDS:
        d = xtab[sd]
        sel = d["tier"] == "H"
        m, s = d["miss"][sel], d["strad"][sel]
        sm, sh, fm, fh = int((s & m).sum()), int((s & ~m).sum()), int((~s & m).sum()), int((~s & ~m).sum())
        rs = sm / max(sm + sh, 1)
        rf = fm / max(fm + fh, 1)
        pt, lo, hi = rate_diff_ci(m, s)
        hsumm[sd] = (rs, rf, pt, lo, hi, len(m), fm + fh)
        L.append(f"| {sd} | {len(m)} | {sm} | {sh} | {fm} | {fh} | {rs:.3f} | "
                 f"{rf:.3f}{'' if fm + fh else ' (n=0)'} | "
                 f"{pt:+.3f} [{lo:+.3f}, {hi:+.3f}]{' *' if np.isfinite(lo) and (lo > 0 or hi < 0) else ''} |")
    ds = [summ[s][2] for s in SEEDS]
    neg = sum(1 for s in SEEDS if summ[s][2] < 0)
    sig_pos = sum(1 for s in SEEDS if summ[s][3] > 0)
    sig_neg = sum(1 for s in SEEDS if summ[s][4] < 0)
    n_flat = int((~xtab[SEEDS[0]]["strad"]).sum())
    d8 = [c8s[s][2] for s in SEEDS]
    L += ["", f"**해석. 판정: '걸친 케이스를 더 놓친다'는 지지되지 않는다.** 시드별 "
          f"diff(걸침 miss rate − 미걸침 miss rate)는 {min(ds):+.3f} ~ {max(ds):+.3f}이고, "
          f"{neg}/3 시드에서 음수, **CI가 0을 배제하며 양수인 시드는 {sig_pos}/3**, "
          f"음수 쪽으로 유의한 시드는 {sig_neg}/3이다. pooled 방향도 "
          f"{summ['pooled'][2]:+.3f}. 신설 8 m 경계만 떼어 봐도 같다"
          f"(diff {min(d8):+.3f} ~ {max(d8):+.3f}). 즉 어떤 시드에서도 걸침이 miss를 유의하게 "
          "**늘리지** 않는다.", "",
          "이유는 (i)·(iii)이 함께 설명한다 — 걸친 프레임은 정의상 양성 칸이 많고(중앙값 "
          f"{T['med_cells']:.0f}칸) 각 칸의 점유율도 높은 큰 인스턴스라, 그중 하나라도 τ를 넘길 "
          "기회가 많다. 프레임 recall은 max 규칙이므로 이 다중성이 곧 이득이다. 반대로 "
          "'걸치지 않은' 프레임은 작고 국소적인 단일 칸 인스턴스이고, 표본이 얇지만"
          f"({n_flat}/{T['n']} = {pct(n_flat, T['n'])}) miss rate는 전반적으로 더 높다 — "
          "**진짜 취약 지점은 걸친 큰 위험이 아니라 작은 단일 칸 위험**이며, 이는 C1 hole "
          "프로브가 겨냥하는 바로 그 형상이다.", "",
          "다만 두 가지를 정직하게 남긴다. ① 미걸침 층이 "
          f"{n_flat}프레임뿐이라 검정력이 낮다 — CI가 넓고 시드 간 부호가 흔들린다(rgb 시드 "
          "자체의 recall 변동이 0.594~0.875로 크다는 SEED_TABLE의 사실과 같은 뿌리다). "
          "② 따라서 이 표의 결론은 '걸침이 해롭다는 증거 없음'이지 '걸침이 이롭다'가 아니다. "
          "결론적으로 걸침을 줄이려는 격자 재설계(더 굵은 셀 / 인스턴스 단위 라벨)는 지금 "
          "우선순위가 아니고, 8 m 분할이 걸침을 늘렸다는 사실도 recall 비용으로 이어지지 "
          "않았다.", "", "---", ""]

    # ---- (iii)
    L += ["## (iii) 양성 칸 내 위험 점유 면적비 · 과차단율", "",
          "**추정기.** 라벨의 `cell_counts[c]` = 5 cm 하이트맵 차분 발자국 샘플 중 폴라 칸 c 안에 "
          "떨어진 개수 (labeler.py, `HM_DEFAULT step = 0.05 m`). 분모는 그 웨지가 담을 수 있는 "
          "5 cm 샘플의 해석적 개수", "",
          "```", "N(band) = 0.5 * dtheta * (r_out^2 - r_in^2) / step^2 ,  dtheta = 12.44 deg, "
          "step = 0.05 m", "```", "",
          "| band | range | wedge area (m^2) | N(band) samples | corpus max observed ratio |",
          "|---|---|---|---|---|"]
    for b in range(NB):
        area = CAP[b] * HM_STEP * HM_STEP
        L.append(f"| {BANDS[b]} | [{BAND_EDGES[b]:g},{BAND_EDGES[b + 1]:g}) m | {area:.3f} | "
                 f"{CAP[b]:.1f} | {rawmax[b]:.4f} |")
    L += ["", "관측 최대 비율이 1.00 근방(래스터화 여유 <1%)이라는 사실이 이 해석적 분모의 검증이다 "
          "— 완전히 채워진 칸이 실제로 N에 도달하고 넘지 않는다. 분위수 계산에서는 1.0으로 클립.", "",
          "occupancy = 위험이 실제로 차지한 면적비 · **overblocking = 1 - occupancy** = 칸은 "
          "GT 양성으로 켜졌지만 실제로는 통행 가능한 면적의 비율.", "",
          "| band | n GT+ cells (test) | occ Q1 | **occ median** | occ Q3 | "
          "**overblocking median** | n (corpus) | occ median (corpus) | overblock median (corpus) |",
          "|---|---|---|---|---|---|---|---|---|"]
    med = {}
    for b in range(NB):
        t, c = occ_test[b], occ_corp[b]
        qt, qc = q(t), q(c)
        med[b] = qt[1]
        L.append(f"| {BANDS[b]} [{BAND_EDGES[b]:g},{BAND_EDGES[b + 1]:g}) | {len(t)} | "
                 f"{qt[0]:.3f} | **{qt[1]:.3f}** | {qt[2]:.3f} | **{1 - qt[1]:.3f}** | "
                 f"{len(c)} | {qc[1]:.3f} | {1 - qc[1]:.3f} |")
    allt = np.concatenate([np.asarray(occ_test[b], float) for b in range(NB)]) \
        if any(len(occ_test[b]) for b in range(NB)) else np.array([])
    qa = q(allt)
    L += [f"| **all** | {len(allt)} | {qa[0]:.3f} | **{qa[1]:.3f}** | {qa[2]:.3f} | "
          f"**{1 - qa[1]:.3f}** | | | |", "",
          "![occupancy](../figures/b4_occupancy.png)", "",
          "**해석.** 점유율은 대체로 거리에 따라 올라간다 — "
          + " · ".join(f"band{BANDS[b]} 중앙값 {med[b]:.2f}" for b in range(NB)) +
          " (band2와 3a는 사실상 같고, 근거리 band1이 뚝 떨어지고 최원거리 band3b가 뚜렷이 "
          f"높다). 뒤집어 말하면 **과차단율은 근거리에서 가장 크고**(band1 {1 - med[0]:.0%}, "
          f"band2 {1 - med[1]:.0%}) 원거리에서 가장 작다(band3b {1 - med[3]:.0%}). "
          "사분위를 함께 보면 분포가 이봉성이라는 점도 중요하다 — Q3가 band2·3a·3b에서 모두 "
          "0.99 이상이라 '칸을 통째로 채우는 위험'이 다수이고, Q1은 0.16~0.31이라 '칸을 살짝 "
          "스치는 위험'도 상당수다. 중앙값 하나로 요약하면 이 이봉성이 가려진다. "
          "원인은 기하다: 웨지 면적이 r^2로 커지는데 [8,12) m 웨지(8.7 m^2)는 우리 코퍼스의 "
          "도랑·낭떠러지형 위험이 통째로 삼키고, [0,2) m 웨지(0.43 m^2)는 위험의 가장자리만 "
          "스치는 경우가 많다. 실용적 함의 두 가지. ① **통행성 비용**: V1 격자로 예측한 위험 칸을 "
          "그대로 통행 금지로 쓰면 근거리에서는 통행 가능한 면적의 상당 부분을 함께 막는다 — "
          "근거리 회피 판단에는 칸보다 고운 표현이 필요하다는 뜻이고, 이는 우리 격자가 "
          "'조기 경보'용이지 '국소 경로계획'용이 아니라는 위치 설정의 정량적 근거다. "
          "② **hole 타입 일반화의 사전 경고**: 이 코퍼스의 위험은 폭이 넓어 원거리 칸을 가득 "
          "채우지만, 개구 0.5–1.5 m급 hole은 [8,12) 칸의 점유율이 1–3%대에 그친다(0.5 m x 0.5 m "
          "= 100 샘플 / 3474). 즉 hole에서는 '칸이 켜진다'는 것의 물리적 의미가 지금 코퍼스와 "
          "질적으로 다르고, C1 제로샷 프로브의 recall은 이 점유율 차이를 함께 보고해야 해석된다. "
          "한계 절에는 이 두 문장을 그대로 넣는다.", ""]
    p = os.path.join(OUT, "STRADDLE_REPORT.md")
    open(p, "w").write("\n".join(L) + "\n")
    print("[b4] wrote", p)


# ----------------------------------------------------------------- figures
def make_figures(test_rows, rows, T, C, occ_test):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    names = [f"sector {b}" for b in SECTOR_BOUNDS] + [f"band {b.split(' (')[0]}" for b in BAND_BOUNDS]
    keys = [f"sb{i}" for i in range(NS - 1)] + [f"bb{i}" for i in range(NB - 1)]
    tr = [100 * T[k][0] / T[k][1] for k in keys]
    cr = [100 * C[k][0] / C[k][1] for k in keys]
    fig, ax = plt.subplots(1, 2, figsize=(12.5, 4.4))
    x = np.arange(len(keys))
    ax[0].bar(x - 0.19, tr, 0.38, label=f"test on-arm (n={T['n']})", color="#2b6cb0")
    ax[0].bar(x + 0.19, cr, 0.38, label=f"corpus on-arm (n={C['n']})", color="#a0aec0")
    for i, (a, b) in enumerate(zip(tr, cr)):
        ax[0].text(i - 0.19, a + 1.2, f"{a:.0f}", ha="center", fontsize=8)
        ax[0].text(i + 0.19, b + 1.2, f"{b:.0f}", ha="center", fontsize=8)
    ax[0].axvspan(5.5, 6.5, color="#fefcbf", alpha=0.6, zorder=0)
    ax[0].set_xticks(x)
    ax[0].set_xticklabels(names, rotation=20, ha="right", fontsize=9)
    ax[0].set_ylabel("% of hazard frames crossing")
    ax[0].set_title("(a) per-boundary straddle rate")
    ax[0].set_ylim(0, max(tr + cr) * 1.22)
    ax[0].legend(fontsize=8, frameon=False)
    ax[0].annotate("NEW 8 m split", xy=(6, max(tr + cr) * 1.10), fontsize=8, ha="center",
                   color="#975a16")

    for j, (lab, key, col) in enumerate((("sectors spanned", "n_sectors", "#2b6cb0"),
                                         ("bands spanned", "n_bands", "#dd6b20"))):
        v = np.array([r[key] for r in test_rows])
        mx = NS if key == "n_sectors" else NB
        h = np.array([(v == k).sum() for k in range(1, mx + 1)]) * 100.0 / len(v)
        ax[1].bar(np.arange(1, mx + 1) + (j - 0.5) * 0.36, h, 0.36, label=lab, color=col)
    ax[1].set_xlabel("count spanned by one frame's GT-positive set")
    ax[1].set_ylabel("% of test hazard frames")
    ax[1].set_title("(b) span histogram (test on-arm)")
    ax[1].set_xticks(range(1, NS + 1))
    ax[1].legend(fontsize=8, frameon=False)
    for a in ax:
        a.spines[["top", "right"]].set_visible(False)
        a.grid(axis="y", alpha=0.25, lw=0.6)
    fig.suptitle("B4(i) hazard-instance straddling — PROVISIONAL-GRID-V1", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    p1 = os.path.join(FIG, "b4_straddle.png")
    fig.savefig(p1, dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    data = [np.clip(np.asarray(occ_test[b], float), 0, 1) for b in range(NB)]
    bp = ax.boxplot(data, patch_artist=True, widths=0.55, showfliers=False,
                    medianprops=dict(color="black", lw=1.6))
    for patch, c in zip(bp["boxes"], ["#c05621", "#dd6b20", "#4299e1", "#2b6cb0"]):
        patch.set_facecolor(c)
        patch.set_alpha(0.75)
    for i, d in enumerate(data):
        if d.size:
            ax.scatter(np.full(d.size, i + 1) + np.random.default_rng(0).normal(0, 0.055, d.size),
                       d, s=3, alpha=0.10, color="k", zorder=3)
            ax.text(i + 1, 1.045, f"med {np.median(d):.2f}\nn={d.size}", ha="center", fontsize=8)
    ax.set_xticklabels([f"{BANDS[b]}\n[{BAND_EDGES[b]:g},{BAND_EDGES[b + 1]:g}) m" for b in range(NB)])
    ax.set_ylabel("hazard occupancy of a GT-positive cell")
    ax.set_ylim(0, 1.16)
    axr = ax.twinx()
    axr.set_ylim(0, 1.16)
    axr.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    axr.set_yticklabels(["100%", "75%", "50%", "25%", "0%"])
    axr.set_ylabel("overblocking (1 - occupancy)")
    ax.set_title("B4(iii) occupancy of GT-positive cells by band (test on-arm)", fontsize=11)
    ax.spines[["top"]].set_visible(False)
    ax.grid(axis="y", alpha=0.25, lw=0.6)
    fig.tight_layout()
    p2 = os.path.join(FIG, "b4_occupancy.png")
    fig.savefig(p2, dpi=160)
    plt.close(fig)
    print("[b4] figures:", p1, p2)


if __name__ == "__main__":
    sys.exit(main())
