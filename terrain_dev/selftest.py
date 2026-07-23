# -*- coding: utf-8 -*-
"""
selftest.py — negobs_terrain 모듈 자가 검증.

실행:
  python selftest.py            # 지형 생성 → metrics.json + preview_*.png
  python selftest.py --plot-only  # (폴백용) 저장된 npz로 플롯만 다시 그림

플로팅 우선순위: env_isaaclab matplotlib → base python3 matplotlib → PIL.
"""

import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

METRICS_PATH = os.path.join(HERE, "metrics.json")
NPZ_PATH = os.path.join(HERE, "_plot_cache.npz")
PREVIEWS = dict(
    hillshade=os.path.join(HERE, "preview_hillshade_full.png"),
    zoom=os.path.join(HERE, "preview_ditch_zoom.png"),
    cross=os.path.join(HERE, "preview_cross_sections.png"),
    faces=os.path.join(HERE, "preview_face_class.png"),
    long=os.path.join(HERE, "preview_long_profile.png"),
)


# ---------------------------------------------------------------------------
# 계측
# ---------------------------------------------------------------------------
def _station_frame(cl, s_target):
    """호길이 s_target에서 중심선 위치와 단위 법선벡터."""
    s = cl["s"]
    k = int(np.clip(np.searchsorted(s, s_target), 1, len(s) - 2))
    p = np.array([cl["x"][k], cl["y"][k]])
    tang = np.array([cl["x"][k + 1] - cl["x"][k - 1],
                     cl["y"][k + 1] - cl["y"][k - 1]])
    tang /= np.linalg.norm(tang)
    nrm = np.array([-tang[1], tang[0]])
    return k, p, nrm


def _cross_section(tr, s_target, half_span=3.0, num=601):
    """station의 법선 방향 단면: (offset w, height, carve, base_low@center)."""
    k, p, nrm = _station_frame(tr["centerline"], s_target)
    w = np.linspace(-half_span, half_span, num)
    px = p[0] + w * nrm[0]
    py = p[1] + w * nrm[1]
    from negobs_terrain import bilinear_sample
    h = bilinear_sample(tr["heights"], tr["xs"], tr["ys"], px, py)
    cv = bilinear_sample(tr["carve"], tr["xs"], tr["ys"], px, py)
    b0 = float(bilinear_sample(tr["base_low"], tr["xs"], tr["ys"],
                               np.array([p[0]]), np.array([p[1]]))[0])
    return w, h, cv, b0


def _measure_top_width(tr, s_target, thresh=0.02):
    """단면에서 carve > thresh(2cm)인, 중심선(w=0)을 포함한 연속 구간의 폭.

    법선 단면이 사행 굽이에서 도랑을 한 번 더 스치는 경우가 있으므로
    첫~끝 교차가 아니라 w=0을 포함하는 연속 런만 잰다.
    """
    w, _h, cv, _ = _cross_section(tr, s_target)
    on = cv > thresh
    k0 = len(w) // 2                      # w = 0
    if not on[k0]:
        return 0.0
    lo = k0
    while lo > 0 and on[lo - 1]:
        lo -= 1
    hi = k0
    while hi < len(w) - 1 and on[hi + 1]:
        hi += 1
    return float(w[hi] - w[lo])


def _measure_lip_carve(tr, s_target):
    """립 라인의 카빙량 — 붕괴 지점에서 0.1~0.2m로 상승.

    붕괴 구간에서는 둑이 물러나므로(상단반폭 +widen) 실효 립 위치에서 잰다.
    """
    cl = tr["centerline"]
    k, p, nrm = _station_frame(cl, s_target)
    wt = cl["w_top_half"][k] + cl["collapse_c"][k] * tr["collapse"]["widen"]
    from negobs_terrain import bilinear_sample
    vals = []
    for sgn in (+1.0, -1.0):
        px = np.array([p[0] + sgn * wt * nrm[0]])
        py = np.array([p[1] + sgn * wt * nrm[1]])
        vals.append(float(bilinear_sample(tr["carve"], tr["xs"], tr["ys"],
                                          px, py)[0]))
    return max(vals)


def _blend_S(t, dp):
    """단면 프로파일 — 배포 코드의 profile_S를 그대로 사용 (측정 일관성)."""
    from negobs_terrain import profile_S
    return profile_S(t, dp)


def _boundary_band(tr, a_cls, b_cls):
    """a↔b 경계 면들의, 무디더 기대 경계 대비 거리 잔차 산포 → 밴드폭 [m].

    TOP/WALL  : 기대 경계 d = w_top          → 잔차 = d - w_top
    WALL/BOTTOM: 기대 경계 ratio(1-S)=0.85   → 잔차 = (t - t*)*(w_top - w_bot)
    양끝 테이퍼 구간은 제외 (경계가 d 도메인이 아니라 s 도메인이므로).
    """
    A = tr["face_class"][..., 0]  # tri-A 격자만 써도 통계는 동일
    dA = tr["face_d"][..., 0]
    wtA = tr["face_wt"][..., 0]
    wbA = tr["face_wb"][..., 0]
    sA = tr["face_s"][..., 0]
    tl = tr["derived"]["end_taper_len"]
    L_arc = tr["centerline"]["arc_length"]
    interior = (sA > tl + 0.5) & (sA < L_arc - tl - 0.5)

    if a_cls == 0:                      # TOP/WALL
        resid = dA - wtA
    else:                               # WALL/BOTTOM
        dp = tr["params"]["ditch"]
        tg = np.linspace(0.0, 1.0, 4001)
        Sg = _blend_S(tg, dp)
        t_star = float(np.interp(1.0 - tr["params"]["material"]
                                 ["bottom_depth_ratio"], Sg, tg))
        # 프로파일 t 정규화는 lip_round 확장 반폭(span) 기준 (배포 코드와 동일)
        span = np.maximum(wtA + dp["lip_round"] - wbA, 0.2)
        t_face = np.clip((dA - wbA) / span, 0, 1)
        resid = (t_face - t_star) * span

    res = []
    for ax in (0, 1):
        c1 = A.take(range(A.shape[ax] - 1), axis=ax)
        c2 = A.take(range(1, A.shape[ax]), axis=ax)
        m = (((c1 == a_cls) & (c2 == b_cls)) |
             ((c1 == b_cls) & (c2 == a_cls))) & \
            interior.take(range(A.shape[ax] - 1), axis=ax)
        res.append(resid.take(range(A.shape[ax] - 1), axis=ax)[m])
    res = np.concatenate(res)
    if len(res) < 10:
        return 0.0, 0
    lo, hi = np.percentile(res, [2.5, 97.5])
    return float(hi - lo), int(len(res))


def compute_metrics(tr, tr2):
    p = tr["params"]
    cl = tr["centerline"]
    h = tr["heights"]
    L_arc = cl["arc_length"]
    tl = tr["derived"]["end_taper_len"]
    interior = (cl["s"] > tl + 0.5) & (cl["s"] < L_arc - tl - 0.5)

    from negobs_terrain import bilinear_sample
    depth_cl = bilinear_sample(tr["carve"], tr["xs"], tr["ys"],
                               cl["x"], cl["y"])

    # 상단폭 실측 station: 내부 후보 25곳 중, 단면선이 붕괴 함몰(XY 가우시안)
    # 중심의 2σ 안을 지나는 station 제외 (s 거리만으로는 스침을 못 거른다)
    cz = np.array(tr["collapse"]["centers_s"])
    cz_xy = np.array(tr["collapse"]["centers_xy"])
    sig_s = tr["collapse"]["width"] / 2.355
    cand = np.linspace(tl + 0.8, L_arc - tl - 0.8, 25)
    reg_st = []
    for s0 in cand:
        _k, p0, nrm0 = _station_frame(cl, s0)
        wline = np.linspace(-3.0, 3.0, 121)
        line = p0[None, :] + wline[:, None] * nrm0[None, :]
        dmin = np.min(np.linalg.norm(line[:, None, :] - cz_xy[None, :, :],
                                     axis=2))
        if dmin > 2.0 * sig_s:
            reg_st.append(float(s0))
    widths = [_measure_top_width(tr, s) for s in reg_st]

    # 사행 실측: 중심선 y의 편차와 제로크로싱 파장
    cy = cl["y"] - cl["y"].mean()
    zc = np.nonzero(np.diff(np.signbit(cy)))[0]
    if len(zc) >= 2:
        wl_meander = 2.0 * float(np.mean(np.diff(cl["s"][zc])))
    else:
        wl_meander = float("nan")

    # 붕괴: 립 카빙량 (붕괴 중심 vs 참조 station)
    ref_lip = float(np.median([_measure_lip_carve(tr, s) for s in reg_st]))
    cz_lip = [_measure_lip_carve(tr, s) for s in cz]

    fc = tr["face_class"]
    tot = fc.size
    band_tw, n_tw = _boundary_band(tr, 0, 1)
    band_wb, n_wb = _boundary_band(tr, 1, 2)

    nrm = tr["normals"]
    nlen = np.linalg.norm(nrm, axis=-1)

    depth_int = cl["depth_s"][interior]

    metrics = dict(
        grid=dict(shape=list(h.shape), cell=p["terrain"]["cell"],
                  size_m=p["terrain"]["size"]),
        height=dict(min=float(h.min()), max=float(h.max())),
        base_relief=dict(
            low_freq_amp_measured=float(np.abs(tr["base_low"]).max()),
            low_freq_p2p=float(tr["base_low"].max() - tr["base_low"].min()),
            micro_amp_measured=float(np.abs(tr["micro"]).max()),
            spec="amp 0.2~0.3m / micro 0.01~0.03m"),
        ditch_depth=dict(
            max_along_centerline=float(depth_cl.max()),
            mean_interior=float(depth_cl[interior].mean()),
            spec="1.2m +-20%"),
        depth_modulation=dict(
            depth_s_min_interior=float(depth_int.min()),
            depth_s_max_interior=float(depth_int.max()),
            ratio_range=[float(depth_int.min() / p["ditch"]["depth"]),
                         float(depth_int.max() / p["ditch"]["depth"])],
            spec="+-20%"),
        top_width=dict(
            stations_s=[round(float(s), 2) for s in reg_st],
            widths=[round(float(w), 3) for w in widths],
            mean=float(np.mean(widths)), min=float(np.min(widths)),
            max=float(np.max(widths)),
            note="carve>2cm 지표 교차폭 실측 — 판정 A2/A5 대응으로 립 라운딩 "
                 "스커트가 공칭 상단반폭 밖 lip_round(0.2m)까지 확장되므로 "
                 "공칭 2.2보다 양쪽 ~0.3m씩 넓게 읽히는 것이 정상 (사다리꼴 "
                 "본체 공칭 폭은 2.2 유지, 유효 벽각 ≈60°)",
            spec="2.2m 기반 +-20% 변조 + 립 노이즈"),
        meander=dict(
            amp_measured=float(np.abs(cy).max()),
            wavelength_measured=wl_meander,
            spec="+-1.0m / 5~8m"),
        collapse=dict(
            centers_s=[round(float(c), 2) for c in cz],
            zone_width=tr["collapse"]["width"],
            lip_carve_at_collapse=[round(float(v), 3) for v in cz_lip],
            lip_carve_reference=round(ref_lip, 3),
            lip_drop_measured=[round(float(v - ref_lip), 3) for v in cz_lip],
            spec="2곳, 립 0.1~0.2m 낮아짐"),
        face_class=dict(
            top_pct=float((fc == 0).sum() / tot * 100),
            wall_pct=float((fc == 1).sum() / tot * 100),
            bottom_pct=float((fc == 2).sum() / tot * 100),
            n_faces=int(tot)),
        dither_band=dict(
            top_wall_band_m=round(band_tw, 3), top_wall_n_faces=n_tw,
            wall_bottom_band_m=round(band_wb, 3), wall_bottom_n_faces=n_wb,
            spec="0.2~0.4m"),
        normals=dict(
            max_len_error=float(np.abs(nlen - 1.0).max()),
            min_z=float(nrm[..., 2].min()),
            all_upward=bool((nrm[..., 2] > 0).all())),
        reproducibility=dict(
            same_seed_identical=bool(
                np.array_equal(tr["heights"], tr2["heights"]) and
                np.array_equal(tr["face_class"], tr2["face_class"]) and
                np.array_equal(tr["normals"], tr2["normals"]))),
    )
    return metrics, reg_st


# ---------------------------------------------------------------------------
# 플롯 데이터 준비 (numpy만 사용 → npz로 직렬화 가능)
# ---------------------------------------------------------------------------
def build_plotdata(tr, reg_st):
    cl = tr["centerline"]
    L_arc = cl["arc_length"]
    ldir = np.array([-0.5, 0.5, 0.75])
    ldir /= np.linalg.norm(ldir)
    shade = np.clip(np.einsum("ijk,k->ij", tr["normals"], ldir), 0, 1)

    # 도랑 확대 크롭 범위
    y_lo, y_hi = cl["y"].min() - 2.5, cl["y"].max() + 2.5
    x_lo, x_hi = cl["x"].min() - 1.5, cl["x"].max() + 1.5
    xs, ys = tr["xs"], tr["ys"]
    ix = np.nonzero((xs >= x_lo) & (xs <= x_hi))[0]
    iy = np.nonzero((ys >= y_lo) & (ys <= y_hi))[0]

    # 단면 5곳: 일반 3 + 붕괴 2
    cz = list(tr["collapse"]["centers_s"])
    st5 = [reg_st[0], reg_st[len(reg_st) // 2], reg_st[-1]] + cz
    labels, secs = [], []
    for s0 in st5:
        w, h, cv, b0 = _cross_section(tr, s0)
        secs.append(np.stack([w, h - b0]))
        labels.append("s=%.1fm%s" % (s0, " (collapse)" if s0 in cz else ""))

    from negobs_terrain import bilinear_sample
    depth_cl = bilinear_sample(tr["carve"], tr["xs"], tr["ys"],
                               cl["x"], cl["y"])
    lip_s = np.linspace(0.3, L_arc - 0.3, 240)
    lip_carve = np.array([_measure_lip_carve(tr, s) for s in lip_s])

    return dict(
        shade=shade.astype(np.float32),
        xs=xs, ys=ys,
        zoom_ix=np.array([ix[0], ix[-1]]), zoom_iy=np.array([iy[0], iy[-1]]),
        cl_x=cl["x"], cl_y=cl["y"], cl_s=cl["s"],
        face_class_A=tr["face_class"][..., 0].astype(np.int8),
        secs=np.array(secs), sec_labels=np.array(labels),
        depth_cl=depth_cl, cz=np.array(cz),
        lip_s=lip_s, lip_carve=lip_carve,
        heights=tr["heights"].astype(np.float32),
    )


# ---------------------------------------------------------------------------
# 렌더러 1: matplotlib
# ---------------------------------------------------------------------------
def render_matplotlib(pd):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    from matplotlib.patches import Patch

    xs, ys = pd["xs"], pd["ys"]
    ext = [xs[0], xs[-1], ys[0], ys[-1]]

    # 1. 힐셰이드 탑뷰 (전체)
    fig, ax = plt.subplots(figsize=(8, 8), dpi=110)
    ax.imshow(pd["shade"], cmap="gray", origin="lower", extent=ext)
    ax.plot(pd["cl_x"], pd["cl_y"], "r--", lw=0.7, alpha=0.6,
            label="ditch centerline")
    ax.set_title("Hillshade top view (full 30x30 m)")
    ax.set_xlabel("x [m]"); ax.set_ylabel("y [m]"); ax.legend(loc="upper right")
    fig.tight_layout(); fig.savefig(PREVIEWS["hillshade"]); plt.close(fig)

    # 2. 도랑 확대 탑뷰
    i0, i1 = pd["zoom_ix"]; j0, j1 = pd["zoom_iy"]
    fig, ax = plt.subplots(figsize=(10, 5), dpi=120)
    ax.imshow(pd["shade"][j0:j1 + 1, i0:i1 + 1], cmap="gray", origin="lower",
              extent=[xs[i0], xs[i1], ys[j0], ys[j1]])
    ax.plot(pd["cl_x"], pd["cl_y"], "r--", lw=0.8, alpha=0.6)
    ax.set_xlim(xs[i0], xs[i1]); ax.set_ylim(ys[j0], ys[j1])
    ax.set_title("Ditch zoom (hillshade) — meander, ragged lip, collapse zones")
    ax.set_xlabel("x [m]"); ax.set_ylabel("y [m]")
    fig.tight_layout(); fig.savefig(PREVIEWS["zoom"]); plt.close(fig)

    # 3. 횡단면 5곳 겹쳐그리기
    fig, ax = plt.subplots(figsize=(9, 5), dpi=120)
    for k in range(len(pd["secs"])):
        w, hrel = pd["secs"][k]
        lab = str(pd["sec_labels"][k])
        ls = "--" if "collapse" in lab else "-"
        ax.plot(w, hrel, ls, lw=1.4, label=lab)
    ax.axhline(0, color="k", lw=0.5, alpha=0.4)
    ax.set_title("Cross sections (aligned to local base) — trapezoid + rounded lip")
    ax.set_xlabel("offset from centerline [m]")
    ax.set_ylabel("height rel. base [m]")
    ax.legend(fontsize=8); ax.set_aspect("equal")
    fig.tight_layout(); fig.savefig(PREVIEWS["cross"]); plt.close(fig)

    # 4. face_class 컬러맵 (디더링 경계)
    cmap = ListedColormap(["#7aa661", "#a07850", "#4a3b2a"])
    fcA = pd["face_class_A"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 6), dpi=120)
    axes[0].imshow(fcA, cmap=cmap, origin="lower", vmin=0, vmax=2,
                   extent=ext, interpolation="nearest")
    axes[0].set_title("face_class full")
    fx = np.linspace(xs[0], xs[-1], fcA.shape[1])
    fy = np.linspace(ys[0], ys[-1], fcA.shape[0])
    ii = np.nonzero((fx >= xs[pd["zoom_ix"][0]]) & (fx <= xs[pd["zoom_ix"][1]]))[0]
    jj = np.nonzero((fy >= ys[pd["zoom_iy"][0]]) & (fy <= ys[pd["zoom_iy"][1]]))[0]
    axes[1].imshow(fcA[jj[0]:jj[-1] + 1, ii[0]:ii[-1] + 1], cmap=cmap,
                   origin="lower", vmin=0, vmax=2, interpolation="nearest",
                   extent=[fx[ii[0]], fx[ii[-1]], fy[jj[0]], fy[jj[-1]]])
    axes[1].set_title("zoom — dithered boundaries (no ruler lines)")
    handles = [Patch(color="#7aa661", label="TOP (grass)"),
               Patch(color="#a07850", label="WALL (dry soil)"),
               Patch(color="#4a3b2a", label="BOTTOM (wet mud)")]
    axes[1].legend(handles=handles, fontsize=8, loc="upper right")
    for a in axes:
        a.set_xlabel("x [m]"); a.set_ylabel("y [m]")
    fig.tight_layout(); fig.savefig(PREVIEWS["faces"]); plt.close(fig)

    # 5. 종단 프로파일 (붕괴 지점 표시)
    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=120)
    ax.plot(pd["cl_s"], pd["depth_cl"], "b-", lw=1.4,
            label="carve depth along centerline")
    ax.plot(pd["lip_s"], pd["lip_carve"], "r-", lw=1.2,
            label="carve at lip line (collapse -> raised)")
    for c in pd["cz"]:
        ax.axvline(c, color="k", ls=":", lw=1.0)
        ax.text(c, ax.get_ylim()[1] * 0.02 + pd["depth_cl"].max() * 0.9,
                " collapse", rotation=90, fontsize=8, va="top")
    ax.set_title("Longitudinal profile along centerline")
    ax.set_xlabel("arc length s [m]"); ax.set_ylabel("carve depth [m]")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(PREVIEWS["long"]); plt.close(fig)

    return [PREVIEWS[k] for k in ("hillshade", "zoom", "cross", "faces", "long")]


# ---------------------------------------------------------------------------
# 렌더러 2: PIL 폴백 (matplotlib이 어디에도 없을 때)
# ---------------------------------------------------------------------------
def render_pil(pd):
    from PIL import Image, ImageDraw

    def save_gray(arr, path, scale=1):
        img = Image.fromarray((np.flipud(arr) * 255).astype(np.uint8), "L")
        if scale != 1:
            img = img.resize((img.width * scale, img.height * scale),
                             Image.NEAREST)
        img.save(path)

    save_gray(pd["shade"], PREVIEWS["hillshade"])
    i0, i1 = pd["zoom_ix"]; j0, j1 = pd["zoom_iy"]
    save_gray(pd["shade"][j0:j1 + 1, i0:i1 + 1], PREVIEWS["zoom"])

    pal = np.array([[122, 166, 97], [160, 120, 80], [74, 59, 42]], np.uint8)
    rgb = pal[np.flipud(pd["face_class_A"])]
    Image.fromarray(rgb, "RGB").save(PREVIEWS["faces"])

    def polyline_png(series, path, size=(900, 450)):
        img = Image.new("RGB", size, "white")
        dr = ImageDraw.Draw(img)
        allx = np.concatenate([s[0] for s in series])
        ally = np.concatenate([s[1] for s in series])
        x0, x1 = allx.min(), allx.max()
        y0, y1 = ally.min(), ally.max()
        colors = ["blue", "red", "green", "orange", "purple", "black"]
        for k, (sx, sy) in enumerate(series):
            px = (sx - x0) / max(x1 - x0, 1e-9) * (size[0] - 40) + 20
            py = size[1] - 20 - (sy - y0) / max(y1 - y0, 1e-9) * (size[1] - 40)
            dr.line(list(zip(px, py)), fill=colors[k % len(colors)], width=2)
        img.save(path)

    polyline_png([(pd["secs"][k][0], pd["secs"][k][1])
                  for k in range(len(pd["secs"]))], PREVIEWS["cross"])
    polyline_png([(pd["cl_s"], pd["depth_cl"]),
                  (pd["lip_s"], pd["lip_carve"])], PREVIEWS["long"])
    return [PREVIEWS[k] for k in ("hillshade", "zoom", "cross", "faces", "long")]


# ---------------------------------------------------------------------------
def render_all(pd):
    """matplotlib(현 env) → base python3 matplotlib → PIL 순서로 시도."""
    try:
        import matplotlib  # noqa: F401
        paths = render_matplotlib(pd)
        print("[plot] matplotlib (current env)")
        return paths
    except ImportError:
        pass

    # base python3 폴백: 데이터 npz 저장 후 서브프로세스로 --plot-only 실행
    np.savez_compressed(NPZ_PATH, **pd)
    for base_py in ("/usr/bin/python3", "python3"):
        try:
            r = subprocess.run(
                [base_py, os.path.abspath(__file__), "--plot-only"],
                capture_output=True, text=True, timeout=300,
                env={k: v for k, v in os.environ.items()
                     if k not in ("PYTHONPATH", "VIRTUAL_ENV", "CONDA_PREFIX")})
            if r.returncode == 0 and all(os.path.exists(p)
                                         for p in PREVIEWS.values()):
                print("[plot] base python3 matplotlib fallback")
                return [PREVIEWS[k] for k in
                        ("hillshade", "zoom", "cross", "faces", "long")]
        except Exception:
            continue

    print("[plot] PIL fallback")
    return render_pil(pd)


def main_plot_only():
    pd = dict(np.load(NPZ_PATH, allow_pickle=False))
    render_matplotlib(pd)


def main():
    from negobs_terrain import PARAMS, build_terrain
    print("[selftest] building terrain (seed=%d) ..."
          % PARAMS["terrain"]["seed"])
    tr = build_terrain(PARAMS)
    print("[selftest] rebuilding for reproducibility check ...")
    tr2 = build_terrain(PARAMS)

    metrics, reg_st = compute_metrics(tr, tr2)
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    print("[selftest] metrics ->", METRICS_PATH)
    print(json.dumps(metrics, indent=2, ensure_ascii=False))

    pd = build_plotdata(tr, reg_st)
    paths = render_all(pd)
    for p in paths:
        print("[selftest] preview ->", p,
              "(%.1f KB)" % (os.path.getsize(p) / 1024.0))

    assert metrics["reproducibility"]["same_seed_identical"], "seed 재현성 실패"
    assert metrics["normals"]["max_len_error"] < 1e-6, "노멀 정규화 실패"
    print("[selftest] OK")


if __name__ == "__main__":
    if "--plot-only" in sys.argv:
        main_plot_only()
    else:
        main()
