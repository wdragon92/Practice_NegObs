#!/usr/bin/env python3
"""[진단·서술용, 판정 비인용] v2 vs v3-A side-by-side on the frozen GAZEBO_TRACK §4 read-out.

Reads the two CSVs written by tools/collect_csv.py (out/ = v2 six models, out_v3/ = v3-A three
rgb seeds) and re-derives §4.1 / §4.2 / §4.3 with FULL precision, plus the inversion count that
is the headline of this re-run.  Adds NO new read-out rule: NEG_VIEWS, TAU, EXPECT_BAND and the
tier ladder expectation all come from collect_csv.py itself (imported, not copied).

    python3 tools/compare_v2_v3.py            # -> out_v3/compare_v2_v3.json + stdout tables
    python3 tools/compare_v2_v3.py --panel    # + out_v3/panel_ladder_v2_vs_v3.png
"""
import csv
import json
import os
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import collect_csv as CC  # frozen read-out rules: NEG_VIEWS, PAIRS, TAU, EXPECT_BAND

GZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V2_CSV = os.path.join(GZ, "out", "gazebo_zeroshot.csv")
V3_CSV = os.path.join(GZ, "out_v3", "gazebo_zeroshot.csv")
OUTJSON = os.path.join(GZ, "out_v3", "compare_v2_v3.json")
PANEL = os.path.join(GZ, "out_v3", "panel_ladder_v2_vs_v3.png")

VIEWS = CC.NEG_VIEWS                       # presets-7, rs_* excluded (§4 / §6)
BASES = [b for b, _ in CC.PAIRS]           # gz_drop1..4, in §4.3 column order
RGB = ["rgb_s42", "rgb_s43", "rgb_s44"]


def read(path):
    """(model, world, view) -> row dict with the numeric fields cast."""
    out = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            if r["view"] not in VIEWS:
                continue
            r["max_prob"] = float(r["max_prob"])
            r["fired"] = int(r["fired"])
            r["band_hit"] = int(r["band_hit"])
            out[(r["model"], r["world"], r["view"])] = r
    return out


def headline(rows, models):
    """§4.1: pooled over 4 hazard worlds x 7 presets = 28 frames per arm."""
    per, pool_h, pool_c, pool_d = {}, [], [], []
    for m in models:
        h = [rows[(m, b, v)] for b in BASES for v in VIEWS]
        c = [rows[(m, b + "_ctrl", v)] for b in BASES for v in VIEWS]
        d = [a["max_prob"] - z["max_prob"] for a, z in zip(h, c)]
        per[m] = dict(n=len(h),
                      haz_fire=st.mean(x["fired"] for x in h),
                      ctl_fire=st.mean(x["fired"] for x in c),
                      haz_maxp=st.mean(x["max_prob"] for x in h),
                      ctl_maxp=st.mean(x["max_prob"] for x in c),
                      twin_delta=st.mean(d))
        pool_h += h
        pool_c += c
        pool_d += d
    fam = dict(n=len(pool_h),
               haz_fire=st.mean(x["fired"] for x in pool_h),
               ctl_fire=st.mean(x["fired"] for x in pool_c),
               haz_maxp=st.mean(x["max_prob"] for x in pool_h),
               ctl_maxp=st.mean(x["max_prob"] for x in pool_c),
               twin_delta=st.mean(pool_d),
               twin_delta_seedmean=st.mean(per[m]["twin_delta"] for m in models))
    return per, fam


def bands(rows, models):
    """§4.2: hazard-arm band-hit rate and the share of frames whose top cell is in band 3b."""
    per, ph, p3b = {}, [], []
    for m in models:
        h = [rows[(m, b, v)] for b in BASES for v in VIEWS]
        hits = [x["band_hit"] for x in h]
        b3b = [int(x["top_band"] == "3b") for x in h]
        per[m] = dict(n=len(h), band_hit=st.mean(hits), top3b=st.mean(b3b))
        ph += hits
        p3b += b3b
    return per, dict(n=len(ph), band_hit=st.mean(ph), top3b=st.mean(p3b))


def ladder(rows, models):
    """§4.3: hazard-arm mean max-p per world + the inversion the re-run is asking about.

    HEADLINE inversion (§4.3 as corrected 0823 D49 ①): the zero-hazard-pixel H world gz_drop3
    scoring ABOVE the wide-open V world gz_drop2.  Also reported: the full pre-registered order
    p(drop2) >= p(drop1) > p(drop4) > p(drop3), the drop3-vs-drop4 pair, and where drop3 ranks
    among the four worlds (1 = highest, 4 = the pre-registered position).
    """
    per = {}
    for m in models:
        mu = {b: st.mean(rows[(m, b, v)]["max_prob"] for v in VIEWS) for b in BASES}
        order = sorted(BASES, key=lambda b: -mu[b])
        per[m] = dict(
            mu=mu,
            inv_d3_gt_d2=bool(mu["gz_drop3"] > mu["gz_drop2"]),
            inv_d3_gt_d4=bool(mu["gz_drop3"] > mu["gz_drop4"]),
            order_holds=bool(mu["gz_drop2"] >= mu["gz_drop1"] > mu["gz_drop4"] > mu["gz_drop3"]),
            drop3_rank=order.index("gz_drop3") + 1,
            desc_order=order)
    fam = dict(
        n_models=len(models),
        inv_d3_gt_d2=sum(per[m]["inv_d3_gt_d2"] for m in models),
        inv_d3_gt_d4=sum(per[m]["inv_d3_gt_d4"] for m in models),
        order_holds=sum(per[m]["order_holds"] for m in models),
        drop3_rank_mean=st.mean(per[m]["drop3_rank"] for m in models),
        mu={b: st.mean(per[m]["mu"][b] for m in models) for b in BASES})
    return per, fam


def drop3_fa(rows, models):
    """§4.4: gz_drop3 is 0 hazard pixels -> the ctrl arm's firing rate IS the false-alarm rate."""
    per, ph, pc = {}, [], []
    for m in models:
        h = [rows[(m, "gz_drop3", v)]["fired"] for v in VIEWS]
        c = [rows[(m, "gz_drop3_ctrl", v)]["fired"] for v in VIEWS]
        per[m] = dict(haz=st.mean(h), ctl_fa=st.mean(c), pooled=st.mean(h + c))
        ph += h
        pc += c
    return per, dict(haz=st.mean(ph), ctl_fa=st.mean(pc), pooled=st.mean(ph + pc))


def block(rows, models, tag):
    hp, hf = headline(rows, models)
    bp, bf = bands(rows, models)
    lp, lf = ladder(rows, models)
    dp, df = drop3_fa(rows, models)
    return dict(tag=tag, models=models,
                headline=dict(per_model=hp, family=hf),
                bands=dict(per_model=bp, family=bf),
                ladder=dict(per_model=lp, family=lf),
                drop3=dict(per_model=dp, family=df))


def make_panel(res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager

    # This box has no Nanum/KR-named font; the Hangul it does have lives inside the pan-CJK
    # .ttc collections, which matplotlib registers under the collection's FIRST face name
    # ("Noto Sans CJK JP").  Same glyph set -- Hangul renders correctly from it.
    for p in ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
              "/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc"):
        if os.path.exists(p):
            try:
                font_manager.fontManager.addfont(p)
            except Exception:
                pass
    have = {f.name for f in font_manager.fontManager.ttflist}
    for cand in ("NanumGothic", "Noto Sans CJK KR", "Noto Sans CJK JP", "Noto Sans KR",
                 "NanumBarunGothic", "UnDotum", "Baekmuk Gulim", "DejaVu Sans"):
        if cand in have:
            plt.rcParams["font.family"] = cand
            print(f"[panel] font = {cand}")
            break
    plt.rcParams["axes.unicode_minus"] = False

    lab = {"gz_drop1": "gz_drop1\n(V·개방)", "gz_drop2": "gz_drop2\n(V·개방, 단서 적음)",
           "gz_drop3": "gz_drop3\n(H·위험 0픽셀)", "gz_drop4": "gz_drop4\n(V/E)"}
    v2 = [res["v2_rgb"]["ladder"]["family"]["mu"][b] for b in BASES]
    v3 = [res["v3_rgb"]["ladder"]["family"]["mu"][b] for b in BASES]
    x = range(len(BASES))
    w = 0.38

    fig, ax = plt.subplots(figsize=(9.6, 5.6), dpi=150)
    b1 = ax.bar([i - w / 2 for i in x], v2, w, label="v2 rgb 평균 (3시드)",
                color="#8a8f98", edgecolor="#4a4e55", linewidth=0.8)
    b2 = ax.bar([i + w / 2 for i in x], v3, w, label="v3-A rgb 평균 (3시드)",
                color="#2f6fb5", edgecolor="#1d4675", linewidth=0.8)
    for bars in (b1, b2):
        ax.bar_label(bars, fmt="%.3f", fontsize=9, padding=2)

    i2, i3 = BASES.index("gz_drop2"), BASES.index("gz_drop3")
    for i in (i2, i3):
        ax.axvspan(i - 0.5, i + 0.5, color="#d9534f", alpha=0.06, zorder=0)
    ax.set_xticks(list(x))
    ax.set_xticklabels([lab[b] for b in BASES], fontsize=10)
    ax.set_ylabel("하자드 팔 프레임 max-p 평균 (7프리셋 × 3시드)", fontsize=10)
    ax.set_title("티어 사다리 — v2 vs v3-A (Gazebo 제로샷, rgb 계열)\n"
                 "사전 기대  p(drop2) ≳ p(drop1) > p(drop4) > p(drop3)", fontsize=12)
    ax.set_ylim(0, max(v2 + v3) * 1.28)
    ax.grid(axis="y", alpha=0.25, linewidth=0.6)
    ax.set_axisbelow(True)

    n2 = res["v2_rgb"]["ladder"]["family"]["inv_d3_gt_d2"]
    n3 = res["v3_rgb"]["ladder"]["family"]["inv_d3_gt_d2"]
    ax.legend(loc="upper right", fontsize=9, framealpha=0.95)
    ax.text(0.012, 0.965,
            f"음영 = 헤드라인 역전 쌍 (drop3 > drop2)\n"
            f"역전 시드 수:  v2 rgb {n2}/3  →  v3-A rgb {n3}/3",
            transform=ax.transAxes, va="top", ha="left", fontsize=9.5,
            bbox=dict(boxstyle="round,pad=0.45", fc="#fdf6e3", ec="#c9a227", lw=0.9))

    fig.text(0.008, 0.012,
             "[진단·서술용, 판정 비인용] · 출처: experiments/weekend_0823/gazebo/"
             "{out,out_v3}/gazebo_zeroshot.csv · 프레임 216장 sha256 검증 · "
             "판독 기준 GAZEBO_TRACK.md §4 (캡처 전 동결, 무변경 재사용): presets-7, rs_* 제외, "
             "--fit squash --tau 0.5, _000 프레임 1장 · CPU 추론",
             fontsize=6.6, color="#555", wrap=True)
    fig.tight_layout(rect=(0, 0.045, 1, 1))
    fig.savefig(PANEL)
    print(f"[panel] {PANEL}")


def show(res, key, title):
    r = res[key]
    print(f"\n===== {title}  ({r['tag']}) =====")
    print(f"{'model':<10}{'HAZfire':>9}{'CTLfire':>9}{'HAZmaxp':>9}{'CTLmaxp':>9}{'twinD':>9}"
          f"{'bandhit':>9}{'top3b':>8}{'d3>d2':>7}{'d3rank':>8}")
    for m in r["models"]:
        h, b, l = r["headline"]["per_model"][m], r["bands"]["per_model"][m], r["ladder"]["per_model"][m]
        print(f"{m:<10}{h['haz_fire']:>9.3f}{h['ctl_fire']:>9.3f}{h['haz_maxp']:>9.3f}"
              f"{h['ctl_maxp']:>9.3f}{h['twin_delta']:>+9.3f}{b['band_hit']:>9.3f}"
              f"{b['top3b']:>8.3f}{'YES' if l['inv_d3_gt_d2'] else 'no':>7}{l['drop3_rank']:>8}")
    h, b, l = r["headline"]["family"], r["bands"]["family"], r["ladder"]["family"]
    print(f"{'FAMILY':<10}{h['haz_fire']:>9.3f}{h['ctl_fire']:>9.3f}{h['haz_maxp']:>9.3f}"
          f"{h['ctl_maxp']:>9.3f}{h['twin_delta']:>+9.3f}{b['band_hit']:>9.3f}{b['top3b']:>8.3f}"
          f"{str(l['inv_d3_gt_d2']) + '/' + str(l['n_models']):>7}{l['drop3_rank_mean']:>8.2f}")
    print(f"  ladder mean max-p: " + "  ".join(f"{k.replace('gz_','')}={l['mu'][k]:.3f}" for k in BASES))
    print(f"  full pre-reg order holds: {l['order_holds']}/{l['n_models']}   "
          f"drop3>drop4: {l['inv_d3_gt_d4']}/{l['n_models']}")
    d = r["drop3"]["family"]
    print(f"  gz_drop3 (위험 0px): HAZ fire {d['haz']:.3f} · CTL fire (=FA) {d['ctl_fa']:.3f} · "
          f"pooled {d['pooled']:.3f}")


def main():
    v2 = read(V2_CSV)
    v3 = read(V3_CSV)
    v2_models = sorted({k[0] for k in v2})
    res = {
        "v2_all": block(v2, [m for m in ["rgb_s42", "rgb_s43", "rgb_s44",
                                         "b2_s42", "b2_s43", "b2_s44"] if m in v2_models], "v2 6모델"),
        "v2_rgb": block(v2, RGB, "v2 rgb 3시드"),
        "v3_rgb": block(v3, RGB, "v3-A rgb 3시드"),
    }
    res["provenance"] = dict(
        v2_csv=V2_CSV, v3_csv=V3_CSV, views=VIEWS, tau=CC.TAU,
        note="[진단·서술용, 판정 비인용] read-out rules imported from collect_csv.py unchanged")
    show(res, "v2_all", "v2 · 6모델 (GAZEBO_TRACK §4 원본 모집단)")
    show(res, "v2_rgb", "v2 · rgb 3시드 (v3와 가족 정합 비교용)")
    show(res, "v3_rgb", "v3-A · rgb 3시드 (재주행)")

    a, b = res["v2_rgb"]["ladder"]["family"], res["v3_rgb"]["ladder"]["family"]
    print(f"\n>>> 역전(drop3>drop2)  v2 rgb {a['inv_d3_gt_d2']}/3 -> v3-A rgb {b['inv_d3_gt_d2']}/3 "
          f"(v2 전체 6모델 {res['v2_all']['ladder']['family']['inv_d3_gt_d2']}/6)")
    with open(OUTJSON, "w") as f:
        json.dump(res, f, indent=1, ensure_ascii=False)
    print(f"[json] {OUTJSON}")
    if "--panel" in sys.argv:
        make_panel(res)


if __name__ == "__main__":
    main()
