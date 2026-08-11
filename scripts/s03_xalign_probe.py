#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scene03 "x축 정렬안" 측정 프로브 — CPU 전용 · 기하 무변경(읽기 전용).

목적
----
`Docs/STATUS.md`(08-10 2판, commit 0146923) "s03 측정 조사 … 근측 고가 x축 정렬안
(±본교 축 정렬 변형안) — 낙차 에지 교차·산책로/hazard corridor 이격·meander_air 차폐 %·
접지 grade 산출" 을 수치로 답한다.

원칙
----
* **씬 파일을 수정하지 않는다.** `scene03_riverbank.py` 를 모듈로 import 해서 PARAMS·
  `river_dx`·`near_approach_chords`·`build_views` 를 **읽기만** 하고, 변형 정렬안은 이
  스크립트 안에서만 가상 기하로 구성한다.
* 차폐 산출은 씬 자체의 `river_view_selfcheck` 알고리즘(수변선 191점 · 판정컷 투영 ·
  slab 교차)을 그대로 옮겨 쓰되 근측 고가 occluder 만 교체한다. 현행 팔은 씬 출력과
  **동일한 수를 재현**해야 하며(§1 self-test), 재현하지 못하면 스크립트가 실패한다.
* GPU·Isaac 부팅 없음. `--aabb` 를 주면 `geom_invariance_check._FAKE` 하네스로 씬을
  CPU 조립해 실제 프림 world AABB 로 해석 occluder 를 교차검증한다(현행 기하 한정).

사용
----
    python3 scripts/s03_xalign_probe.py            # 해석 측정 (수 초)
    python3 scripts/s03_xalign_probe.py --aabb     # + 프림 AABB 교차검증 (수십 초)
    python3 scripts/s03_xalign_probe.py --json out.json
"""
import argparse
import importlib.util
import json
import math
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True


# ===========================================================================
# [0] 씬 모듈 로드 (순수 수학 경로만 사용 — main() 은 __main__ 가드 안이라 안 돈다)
# ===========================================================================
def load_scene():
    sys.path.insert(0, os.path.join(REPO, "scenes", "main"))
    sys.path.insert(0, REPO)
    path = os.path.join(REPO, "scenes", "main", "scene03_riverbank.py")
    spec = importlib.util.spec_from_file_location("negobs_scene03", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


M = load_scene()
P = M.PARAMS
BG = P["bridge"]
STAG = P["meander"]["z_stagger"]
DECK_HW = (BG["y1"] - BG["y0"]) / 2.0                 # 4.50
HREF = DECK_HW + BG["cope_out"]                       # 4.55  (마이터 기준 반폭)
S_EDGE = 18.2                                         # 유효 수변선 (riprap toe)
TU, TV = math.tan(math.radians(30.0)), math.tan(math.radians(18.0))


def s_of(x, y):
    """world (x, y) → 사행 프레임 횡단좌표 s."""
    return x - M.river_dx(y)


def x_of(s, y):
    return M.river_dx(y) + s


# --- 횡단면 지반고 z(s) : 원장/PARAMS 실값에서 유도 ------------------------
_SL = P["slope"]
_GRAD = _SL["drop"] / _SL["run"]                      # 3.2 / 7.0 = 0.457143


def ground_z(s):
    if s <= 0.0:
        return P["levee"]["z_top"]                    # 둑마루 0.000
    if s <= _SL["run"]:
        return P["levee"]["z_top"] - _GRAD * s        # 제방 사면
    if s <= P["riprap"]["x0"]:
        return P["beach"]["z_top"]                    # 둔치 −3.200
    if s <= S_EDGE:
        return P["riprap"]["z0"] - P["riprap"]["drop"]
    return P["water"]["z"]                            # 수면 −3.350


def zone_of(s):
    """s → 지반 구역 라벨(현실성 판정에 쓰는 분류)."""
    cw, cb = P["crest_walk"], P["crest_band"]
    bp = P["beach_path"]
    if s < cb["x0"]:
        return "둑마루(잔디)"
    if s < cw["x0"]:
        return "둑마루 연석밴드"
    if s < cw["x1"]:
        return "둑마루 산책로(점토블록)"
    if s < 0.0:
        return "둑마루 갓길잔디"
    if s < _SL["run"]:
        return "제방 사면"
    if s < bp["x0"]:
        return "둔치 잔디"
    if s <= bp["x1"]:
        return "둔치 자전거도로"
    if s < P["reeds"]["x0"]:
        return "둔치 잔디"
    if s < P["riprap"]["x0"]:
        return "갈대밴드"
    if s <= S_EDGE:
        return "호안 사석"
    if s < P["far_bank"]["x0"]:
        return "수면"
    if s < P["city"]["A"]["x0"]:
        return "원측 둔치"
    return "원측 시가지"


# ===========================================================================
# [1] 정렬안 구성 — 씬의 `near_approach_chords()` 와 같은 규약으로 가상 폴리라인
# ===========================================================================
def _chords_from_points(pts, brs, deck_top0, grade, vlen, lead):
    """(pts, brs) → 씬과 동일한 현(chord) dict 리스트. z 프로파일도 씬과 동일 규약."""
    def z_of(t):
        if t <= vlen:
            return deck_top0 - grade * t * t / (2.0 * vlen)
        return deck_top0 - grade * (t - vlen / 2.0)

    out, t = [], 0.0
    a0 = brs[0]
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        ln = math.hypot(x1 - x0, y1 - y0)
        d_prev = abs(M._ang(brs[i] - (brs[i - 1] if i else a0)))
        d_next = abs(M._ang(brs[i + 1] - brs[i])) if i + 1 < len(brs) else 0.0
        out.append(dict(
            i=i, brg=brs[i], L=ln, x0=x0, y0=y0, x1=x1, y1=y1,
            mx=(x0 + x1) / 2.0, my=(y0 + y1) / 2.0,
            z0=z_of(t), z1=z_of(t + ln),
            back=(lead if i == 0 else HREF * math.tan(math.radians(d_prev / 2.0))),
            fwd=HREF * math.tan(math.radians(d_next / 2.0))))
        t += ln
    return out


def deck_start(b_yaw=None):
    """근측 교대(고가 기점)의 world 좌표와 출발 방위. b_yaw=None → 현행(사행 접선)."""
    cy = (BG["y0"] + BG["y1"]) / 2.0
    cx = (BG["x0"] + BG["x1"]) / 2.0
    dx0 = M.river_dx(cy)
    yaw = M.river_yaw(cy) if b_yaw is None else b_yaw
    cc, ss = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    pvx, pvy = dx0 + cx, cy
    ex, ey = dx0 + BG["x0"], cy
    p0 = (pvx + (ex - pvx) * cc - (ey - pvy) * ss,
          pvy + (ex - pvx) * ss + (ey - pvy) * cc)
    return p0, 180.0 + yaw, (pvx, pvy), yaw


def align_current():
    """V0 — 현행(GT-83 3차): 좌 90° 곡선 후 사행프레임 s_hold 남향."""
    ch, s_hold = M.near_approach_chords()
    return dict(name="V0 현행(곡선 남향 고가)", chords=ch, s_hold=s_hold,
                b_yaw=None, turn=90.0, curve_len=BG["napp_curve_len"],
                grade=BG["napp_grade"], pier_j=list(BG["napp_pier_j"]))


def _eased(total, n_mid=9):
    """씬의 (4.5, 9×9, 4.5) 완화 스케줄을 total 로 스케일."""
    unit = total / (n_mid + 1.0)
    return tuple([unit / 2.0] + [unit] * n_mid + [unit / 2.0])


def align_turn_to(bearing, curve_len, grade, b_yaw=None, term_x=None,
                  name="", pier_bay=10.4, vlen=8.0):
    """근측 고가를 `bearing` 으로 전이시킨 뒤 그 방위로 직진시키는 가상 정렬안.

    bearing=180.0 → world −X 평행(= x축 정렬).  turn 0 이면 전이 없이 직진.
    term_x: 종점 world x (기본 제방 서단 levee.x0).
    """
    p0, a0, _piv, yaw = deck_start(b_yaw)
    total = M._ang(bearing - a0)
    pts, brs = [p0], []
    b = a0
    if abs(total) > 1e-9:
        dl = _eased(total)
        seg = curve_len / len(dl)
        for d in dl:
            bc = b + d / 2.0
            pts.append((pts[-1][0] + seg * math.cos(math.radians(bc)),
                        pts[-1][1] + seg * math.sin(math.radians(bc))))
            brs.append(bc)
            b += d
    # 직진부: 종점까지 5 m 스테이션
    tx = P["levee"]["x0"] if term_x is None else term_x
    cx, cy = pts[-1]
    run = (tx - cx) / math.cos(math.radians(bearing))
    if run > 0:
        n = max(1, int(math.ceil(run / 5.0)))
        for k in range(1, n + 1):
            d = run * k / n
            pts.append((cx + d * math.cos(math.radians(bearing)),
                        cy + d * math.sin(math.radians(bearing))))
            brs.append(bearing)
    ch = _chords_from_points(pts, brs, BG["deck_top"] - STAG, grade, vlen,
                             BG["napp_lead"])
    # 교각: 기점에서 pier_bay 간격 → 가장 가까운 현 시점
    t, marks, acc = pier_bay, [], 0.0
    for c in ch:
        if acc + c["L"] >= t and t > 0:
            marks.append(c["i"])
            t += pier_bay
        acc += c["L"]
    return dict(name=name, chords=ch, s_hold=None, b_yaw=b_yaw,
                turn=total, curve_len=curve_len if abs(total) > 1e-9 else 0.0,
                grade=grade, pier_j=marks)


# ===========================================================================
# [2] 기하 계측
# ===========================================================================
def chord_boxes(chords):
    """씬 selfcheck 와 동일한 (box, pivot, yaw) 3-튜플 목록."""
    out = []
    for c in chords:
        out.append(((c["mx"] - c["L"] / 2.0 - c["back"],
                     c["mx"] + c["L"] / 2.0 + c["fwd"],
                     c["my"] - DECK_HW, c["my"] + DECK_HW,
                     min(c["z0"], c["z1"]) - BG["deck_thick"],
                     max(c["z0"], c["z1"]) + BG["parapet_h"]),
                    (c["mx"], c["my"]), c["brg"]))
    return out


def deck_corners(chords):
    """상판 외곽(코핑 포함 반폭 DECK_HW) world 코너 — 4점/현."""
    pts = []
    for c in chords:
        x0 = c["mx"] - c["L"] / 2.0 - c["back"]
        x1 = c["mx"] + c["L"] / 2.0 + c["fwd"]
        for xx in (x0, x1):
            for yy in (c["my"] - DECK_HW, c["my"] + DECK_HW):
                q = M._rot_xy((xx, yy, 0.0), (c["mx"], c["my"]), c["brg"])
                pts.append((q[0], q[1], c))
    return pts


def geom_metrics(al):
    """정렬안 1건의 기하 지표 묶음."""
    ch = al["chords"]
    if not ch:
        return dict(n_chords=0, length=0.0, empty=True)
    cor = deck_corners(ch)
    s_list = [s_of(x, y) for x, y, _ in cor]
    y_list = [y for _, y, _ in cor]
    x_list = [x for x, _, _ in cor]
    # R_min: 현 폴리라인의 외접반경 R = c / (2·sin(δ/2)) — 씬이 선언한 7.53 m 와 같은 정의
    rmin, kmax = None, 0.0
    for i in range(1, len(ch)):
        k = abs(M._ang(ch[i]["brg"] - ch[i - 1]["brg"]))
        if k > 1e-6:
            r = ch[i]["L"] / (2.0 * math.sin(math.radians(k / 2.0)))
            rmin = r if rmin is None else min(rmin, r)
            kmax = max(kmax, k)
    d = dict(
        n_chords=len(ch),
        length=round(sum(c["L"] for c in ch), 3),
        s_min=round(min(s_list), 3), s_max=round(max(s_list), 3),
        y_min=round(min(y_list), 3), y_max=round(max(y_list), 3),
        x_min=round(min(x_list), 3), x_max=round(max(x_list), 3),
        z_start=round(ch[0]["z0"], 3), z_end=round(ch[-1]["z1"], 3),
        R_min=(round(rmin, 2) if rmin else None),
        kink_max=round(kmax, 2),
        R_arc=(round(al["curve_len"] / math.radians(abs(al["turn"])), 2)
               if abs(al["turn"]) > 1e-6 else None),
        turn_deg=round(al["turn"], 2), grade_pct=round(al["grade"] * 100.0, 2),
    )
    # --- 낙차 에지(s=0) 교차 ---
    d["crosses_drop_edge"] = bool(min(s_list) < 0.0)
    d["s_margin_to_drop"] = round(min(s_list), 3)       # >0 이면 미횡단 여유
    d["s_margin_to_promenade"] = round(min(s_list) - P["crest_walk"]["x1"], 3)
    # 중심선이 s=0 을 지나는 지점(있으면)
    d["drop_cross"] = None
    for c in ch:
        sa, sb = s_of(c["x0"], c["y0"]), s_of(c["x1"], c["y1"])
        if (sa - 0.0) * (sb - 0.0) < 0.0:
            f = sa / (sa - sb)
            yy = c["y0"] + f * (c["y1"] - c["y0"])
            zz = c["z0"] + f * (c["z1"] - c["z0"])
            d["drop_cross"] = dict(y=round(yy, 2), deck_top=round(zz, 3),
                                   soffit=round(zz - BG["deck_thick"], 3),
                                   over_crest=round(zz - BG["deck_thick"], 3))
            break
    # --- hazard corridor (y ±0.95) 이격 ---
    cy0, cy1 = P["corridor"]["y0"], P["corridor"]["y1"]
    gap = min(max(cy0 - y, y - cy1, 0.0) if not (cy0 <= y <= cy1) else 0.0
              for y in y_list)
    d["corridor_gap"] = round(gap, 3)
    d["corridor_breach"] = bool(gap <= 0.0)
    # --- 낙차 에지 밴드(|s| ≤ 1.0) 를 상판이 덮는 y 연장 ---
    ys_cover = []
    for c in ch:
        for k in range(41):
            f = k / 40.0
            xx = c["x0"] + f * (c["x1"] - c["x0"])
            yy = c["y0"] + f * (c["y1"] - c["y0"])
            for lat in [-DECK_HW + j * DECK_HW / 4.0 for j in range(9)]:
                px = xx - lat * math.sin(math.radians(c["brg"]))
                py = yy + lat * math.cos(math.radians(c["brg"]))
                if abs(s_of(px, py)) <= 1.0:
                    ys_cover.append(py)
    d["drop_edge_cover_m"] = (round(max(ys_cover) - min(ys_cover), 2)
                              if ys_cover else 0.0)
    d["drop_edge_cover_y"] = ((round(min(ys_cover), 2), round(max(ys_cover), 2))
                              if ys_cover else None)
    # --- 구역 점유: 상판 투영이 덮는 s 구역 ---
    zones = {}
    for c in ch:                                        # 현 중심선 20분할 샘플
        for k in range(21):
            f = k / 20.0
            xx = c["x0"] + f * (c["x1"] - c["x0"])
            yy = c["y0"] + f * (c["y1"] - c["y0"])
            zz = c["z0"] + f * (c["z1"] - c["z0"])
            for lat in (-DECK_HW, 0.0, DECK_HW):        # 좌/중/우 3선
                px = xx - lat * math.sin(math.radians(c["brg"]))
                py = yy + lat * math.cos(math.radians(c["brg"]))
                zones.setdefault(zone_of(s_of(px, py)), 0)
                zones[zone_of(s_of(px, py))] += 1
            _ = zz
    tot = sum(zones.values())
    d["zone_share"] = {k: round(100.0 * v / tot, 1)
                       for k, v in sorted(zones.items(), key=lambda kv: -kv[1])}
    # --- 최소 소핏 여유 / 접지 ---
    # 소핏 여유는 **상판 전폭**(±DECK_HW, 좌/중/우 9선)에서 잰다 — 씬 선언 1.40 m 는
    # 중심선이 아니라 연단에서 나온 값이라 중심선만 재면 3.45 m 로 과대평가된다.
    worst = (1e9, None)
    touch = None
    t_acc = 0.0
    for c in ch:
        for k in range(21):
            f = k / 20.0
            xx = c["x0"] + f * (c["x1"] - c["x0"])
            yy = c["y0"] + f * (c["y1"] - c["y0"])
            zz = c["z0"] + f * (c["z1"] - c["z0"])
            for j in range(9):
                lat = -DECK_HW + j * DECK_HW / 4.0
                px = xx - lat * math.sin(math.radians(c["brg"]))
                py = yy + lat * math.cos(math.radians(c["brg"]))
                s = s_of(px, py)
                cl = (zz - BG["deck_thick"]) - ground_z(s)
                if cl < worst[0]:
                    worst = (cl, dict(x=round(px, 2), y=round(py, 2),
                                      s=round(s, 2), zone=zone_of(s),
                                      lat=round(lat, 2)))
            s0c = s_of(xx, yy)
            if touch is None and zz <= ground_z(s0c) + 1e-6:
                touch = dict(x=round(xx, 2), y=round(yy, 2), s=round(s0c, 2),
                             t=round(t_acc + f * c["L"], 2))
        t_acc += c["L"]
    d["min_soffit_clear"] = round(worst[0], 3)
    d["min_soffit_at"] = worst[1]
    d["touchdown"] = touch
    # --- 교각 ---
    piers = []
    for i in al["pier_j"]:
        c = ch[i]
        px, py = c["x0"], c["y0"]
        s = s_of(px, py)
        piers.append(dict(chord=i, x=round(px, 2), y=round(py, 2),
                          s=round(s, 2), zone=zone_of(s),
                          clear=round(c["z0"] - BG["deck_thick"] - ground_z(s), 2)))
    d["piers"] = piers
    return d


def prop_clash(al):
    """기존 프롭/식생과의 평면 이격 [m] — 상판 외곽 폴리곤까지의 최단거리."""
    ch = al["chords"]
    if not ch:
        return [], 0

    def dist_to_deck(px, py):
        best = 1e9
        for c in ch:
            q = M._rot_xy((px, py, 0.0), (c["mx"], c["my"]), -c["brg"])
            x0 = c["mx"] - c["L"] / 2.0 - c["back"]
            x1 = c["mx"] + c["L"] / 2.0 + c["fwd"]
            y0, y1 = c["my"] - DECK_HW, c["my"] + DECK_HW
            dx = max(x0 - q[0], q[0] - x1, 0.0)
            dy = max(y0 - q[1], q[1] - y1, 0.0)
            best = min(best, math.hypot(dx, dy))
        return best

    items = []
    for t in P["trees"]:
        items.append(("수목(둔치)", x_of(t["cx"], t["cy"]), t["cy"]))
    for t in P["trees_extra"]:
        items.append(("수목(추가)", x_of(t["cx"], t["cy"]), t["cy"]))
    for i, b in enumerate(P["benches"]):
        items.append(("벤치%d" % i, x_of(b[0], b[1]), b[1]))
    for b in P["bollards"]:
        items.append(("볼라드", x_of(b["cx"], b["cy"]), b["cy"]))
    pg = P["pergola"]
    pcy = (pg["y0"] + pg["y1"]) / 2.0
    items.append(("퍼걸러", x_of((pg["x0"] + pg["x1"]) / 2.0, pcy), pcy))
    gg = P["gauge"]
    items.append(("수위표", x_of(gg["cx"], gg["cy"]), gg["cy"]))
    out = []
    for nm, px, py in items:
        dd = dist_to_deck(px, py)
        if dd < 8.0:
            out.append(dict(item=nm, x=round(px, 2), y=round(py, 2),
                            s=round(s_of(px, py), 2), dist=round(dd, 2)))
    out.sort(key=lambda r: r["dist"])
    # 갈대밴드 y_gap (s 16..17) — 상판이 지나가면 새 절단이 필요
    rd = P["reeds"]
    hit = [c for c in ch
           if rd["x0"] <= s_of(c["mx"], c["my"]) <= rd["x1"]]
    return out, len(hit)


# ===========================================================================
# [3] 차폐/판독성 — 씬 `river_view_selfcheck` 알고리즘의 파라미터화 사본
# ===========================================================================
def static_boxes():
    """근측 고가를 제외한 모든 occluder(수목·퍼걸러·볼라드·수위표·원측 시가지)."""
    boxes = []
    trees = ([(t["cx"], t["cy"], P["beach"]["z_top"], 2.2) for t in P["trees"]]
             + [(t["cx"], t["cy"], t["gz"], 2.2) for t in P["trees_extra"]]
             + [(t["cx"], t["cy"], P["far_bank"]["z_top"], 4.2)
                for t in P["far_trees"]])
    for cx0, cy0, gz, th in trees:
        cx = M.river_dx(cy0) + cx0
        boxes.append((cx - 1.0, cx + 1.0, cy0 - 1.0, cy0 + 1.0,
                      gz + th * 0.85, gz + th * 1.25 + 1.1))
        boxes.append((cx - 0.12, cx + 0.12, cy0 - 0.12, cy0 + 0.12,
                      gz, gz + th * 0.85))
    pg = P["pergola"]
    pcy = (pg["y0"] + pg["y1"]) / 2.0
    pdx = M.river_dx(pcy)
    boxes.append((pdx + pg["x0"], pdx + pg["x1"], pg["y0"], pg["y1"], 0.0,
                  pg["z_roof"] + pg["roof_t"]))
    for b in P["bollards"]:
        bx = M.river_dx(b["cy"]) + b["cx"]
        boxes.append((bx - 0.09, bx + 0.09, b["cy"] - 0.09, b["cy"] + 0.09,
                      0.0, P["bollard"]["h"]))
    gg = P["gauge"]
    gx = M.river_dx(gg["cy"]) + gg["cx"]
    boxes.append((gx - 0.1, gx + 0.1, gg["cy"] - 0.1, gg["cy"] + 0.1,
                  gg["z0"], gg["z1"]))
    for _k, bd in P["city"].items():
        ccy = (bd["y0"] + bd["y1"]) / 2.0
        cdx = M.river_dx(ccy)
        boxes.append((cdx + bd["x0"], cdx + bd["x1"], bd["y0"], bd["y1"],
                      bd["base_z"], bd["base_z"] + bd["h"]))
    return boxes


def main_span_boxes(b_yaw=None):
    """본교(상판·교각·교대·원측 접속교) rot_boxes 와 그 피벗/요."""
    b_cy = (BG["y0"] + BG["y1"]) / 2.0
    b_xm = (BG["x0"] + BG["x1"]) / 2.0
    bdx = M.river_dx(b_cy)
    b_yawd = M.river_yaw(b_cy) if b_yaw is None else b_yaw
    b_piv = (bdx + b_xm, b_cy)
    b_sof = BG["deck_top"] - BG["deck_thick"]
    b_cap_bot = b_sof - BG["cap_h"]
    b_x2 = BG["x1"] + BG["appr_len"]
    b_top2 = BG["deck_top"] - BG["appr_grade"] * BG["appr_len"]
    rb = [(bdx + BG["x0"], bdx + BG["x1"], BG["y0"], BG["y1"],
           b_sof, BG["deck_top"] + BG["parapet_h"]),
          (bdx + BG["x1"], bdx + b_x2, BG["y0"], BG["y1"],
           b_top2 - BG["deck_thick"], BG["deck_top"] + BG["parapet_h"])]
    cols = [(px, b_cap_bot, b_sof) for px in BG["pier_x"]]
    cols += [(BG["x1"] + pt,
              b_sof - BG["appr_grade"] * pt - BG["cap_h"],
              b_sof - BG["appr_grade"] * pt) for pt in BG["appr_pier_x"]]
    for _px, _cb, _ct in cols:
        rb.append((bdx + _px - BG["pier_r"], bdx + _px + BG["pier_r"],
                   b_cy - BG["pier_r"], b_cy + BG["pier_r"],
                   BG["pier_z0"], _cb))
        rb.append((bdx + _px - BG["cap_t"] / 2.0, bdx + _px + BG["cap_t"] / 2.0,
                   b_cy - BG["cap_w"] / 2.0, b_cy + BG["cap_w"] / 2.0, _cb, _ct))
    for _ax, _atop in ((BG["x0"], b_sof), (BG["x1"], b_sof),
                       (b_x2, b_top2 + BG["parapet_h"])):
        rb.append((bdx + _ax - BG["abut_t"] / 2.0, bdx + _ax + BG["abut_t"] / 2.0,
                   BG["y0"] - BG["abut_over"] / 2.0,
                   BG["y1"] + BG["abut_over"] / 2.0, BG["abut_z0"], _atop))
    return rb, b_piv, b_yawd


def occlusion(napp_boxes, b_yaw=None, extra_static=None):
    """씬 selfcheck 와 동일한 판정: 3컷의 (차폐/전체, 휨%, 종방향 m)."""
    views = M.build_views()
    rot_boxes, b_piv, b_yawd = main_span_boxes(b_yaw)
    boxes = static_boxes() + (extra_static or [])
    res = {}
    for name, judge in (("river_along", False), ("meander_air", True),
                        ("bank_oblique", True)):
        v = views[name]
        eye, tgt = v["eye"], v["tgt"]
        proj = M._cam_basis(eye, tgt)
        pts = []
        for k in range(191):
            y = -47.5 + 95.0 * k / 190.0
            p = (M.river_dx(y) + S_EDGE, y, P["water"]["z"])
            q = proj(p)
            if q is None or abs(q[0]) > TU or abs(q[1]) > TV:
                continue
            pts.append((y, q[0], q[1], p))
        if len(pts) < 3:
            res[name] = dict(n=0)
            continue

        def bow(sub):
            if len(sub) < 3:
                return 0.0, 0.0
            u0, v0 = sub[0][1], sub[0][2]
            u1, v1 = sub[-1][1], sub[-1][2]
            cl = math.hypot(u1 - u0, v1 - v0)
            dv = 0.0
            for _, u, vv, _p in sub:
                dv = max(dv, abs((u1 - u0) * (vv - v0) - (v1 - v0) * (u - u0))
                         / cl if cl > 1e-9 else 0.0)
            return 100.0 * dv / TU, sub[-1][0] - sub[0][0]

        vis, occ = [], 0
        att = dict(static=0, main=0, napp=0)
        for rec in pts:
            p = rec[3]
            h_st = any(M._seg_hits_box(eye, p, b) for b in boxes)
            h_mn = any(M._seg_hits_rot_box(eye, p, b, b_piv, b_yawd)
                       for b in rot_boxes)
            h_np = any(M._seg_hits_rot_box(eye, p, _b, _pv, _br)
                       for _b, _pv, _br in napp_boxes)
            att["static"] += int(h_st)
            att["main"] += int(h_mn)
            att["napp"] += int(h_np)
            if h_st or h_mn or h_np:
                occ += 1
            else:
                vis.append(rec)
        bw, sp = bow(pts)
        bwv, spv = bow(vis)
        res[name] = dict(judge=judge, n=len(pts), occluded=occ,
                         occ_pct=round(100.0 * occ / len(pts), 2),
                         bow_pct=round(bw, 2), y_span=round(sp, 1),
                         vis_n=len(vis), vis_bow_pct=round(bwv, 2),
                         vis_span=round(spv, 1), attrib=att,
                         pass_=bool(not judge or (sp >= 40.0
                                                  and bw / 100.0 >= 0.05
                                                  and occ <= len(pts) * 0.35)))
    return res


def frame_occupancy(chords):
    """각 프리셋에서 근측 고가가 차지하는 u/half·v/half 범위 + 카메라 매몰 여부.

    u/v 범위는 **프레임 안에 든 코너만** 대상으로 한다(뒤쪽·측방 코너의 발산값 배제).
    매몰: 카메라 눈이 어느 현의 상판 박스(소핏~파라펫 상단) 안에 들어가면 True.
    """
    views = M.build_views()
    cor = []
    for c in chords:
        x0 = c["mx"] - c["L"] / 2.0 - c["back"]
        x1 = c["mx"] + c["L"] / 2.0 + c["fwd"]
        for xx in (x0, x1):
            for yy in (c["my"] - DECK_HW, c["my"] + DECK_HW):
                for zz in (min(c["z0"], c["z1"]) - BG["deck_thick"],
                           max(c["z0"], c["z1"]) + BG["parapet_h"]):
                    q = M._rot_xy((xx, yy, zz), (c["mx"], c["my"]), c["brg"])
                    cor.append((q[0], q[1], zz))
    boxes = chord_boxes(chords)

    def buried(eye):
        for (x0, x1, y0, y1, z0, z1), piv, br in boxes:
            q = M._rot_xy(eye, piv, -br)
            if x0 <= q[0] <= x1 and y0 <= q[1] <= y1 and z0 <= q[2] <= z1:
                return True
        return False

    out = {}
    for name, v in views.items():
        proj = M._cam_basis(v["eye"], v["tgt"])
        us, vs = [], []
        for p in cor:
            q = proj(p)
            if q is None or abs(q[0]) > TU or abs(q[1]) > TV:
                continue
            us.append(q[0] / TU)
            vs.append(q[1] / TV)
        out[name] = dict(u=((round(min(us), 2), round(max(us), 2)) if us else None),
                         v=((round(min(vs), 2), round(max(vs), 2)) if vs else None),
                         in_frame=len(us), n=len(cor),
                         cam_buried=buried(v["eye"]))
    return out


# ===========================================================================
# [4] 프림 AABB 교차검증 (현행 기하 한정) — geom_invariance_check._FAKE 하네스
# ===========================================================================
def aabb_check():
    from unittest.mock import MagicMock
    sys.path.insert(0, os.path.join(REPO, "scripts"))
    import geom_invariance_check as gic
    fake = {}
    exec(compile(gic._FAKE, "<fakeusd>", "exec"), fake)
    fake["_install"]()
    import scene_common as sc
    sc.boot = lambda headless=True: MagicMock()
    sc.capture_pipeline = lambda *a, **k: None
    sc.ensure_noon_lookfix = lambda p: p
    sc.check_assets = lambda *a, **k: None
    os.environ["NEGOBS_CAPTURE"] = "1"
    path = os.path.join(REPO, "scenes", "main", "scene03_riverbank.py")
    spec = importlib.util.spec_from_file_location("negobs_s03_fake", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    fake["reset"]()
    import random
    random.seed(0)
    _so, sys.stdout = sys.stdout, open(os.devnull, "w")
    try:
        mod.main()
    finally:
        sys.stdout.close()
        sys.stdout = _so
    prims = fake["_PRIMS"]

    def compose(p):
        """부모 체인의 T/RZ/T 를 합성해 world AABB (RZ 는 회전 사각형의 AABB)."""
        parts = p.split("/")
        chain = ["/".join(parts[:k + 1]) for k in range(2, len(parts))]
        tx = ty = tz = 0.0
        rot = 0.0
        sx = sy = sz = 1.0
        pend = []
        for cp in chain:
            rec = prims.get(cp)
            if rec is None:
                continue
            for k, v in rec["ops"]:
                if k == "T":
                    pend.append(("T", v))
                elif k in ("RZ", "RotZ"):
                    pend.append(("RZ", float(v if not isinstance(v, (tuple, list))
                                             else v[0])))
                elif k == "RY":
                    pend.append(("RY", float(v if not isinstance(v, (tuple, list))
                                             else v[0])))
                elif k == "S":
                    sx, sy, sz = v
        # 좌→우 순서로 누적 (USD xformOp 순서)
        px = py = pz = 0.0
        acc = 0.0
        for k, v in pend:
            if k == "T":
                c, s = math.cos(math.radians(acc)), math.sin(math.radians(acc))
                px += v[0] * c - v[1] * s
                py += v[0] * s + v[1] * c
                pz += v[2]
            elif k == "RZ":
                acc += v
        tx, ty, tz, rot = px, py, pz, acc
        rec = prims[p]
        size = float(rec["attrs"].get("size", 2.0))
        hx, hy, hz = sx * size / 2.0, sy * size / 2.0, sz * size / 2.0
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        corners = [(tx + dx * c - dy * s, ty + dx * s + dy * c)
                   for dx in (-hx, hx) for dy in (-hy, hy)]
        return corners, (tz - hz, tz + hz)     # 정확한 평면 회전 사각형 + z 범위

    def group(p):
        for tag in ("NAppHead", "NAppPier", "NApp_"):
            if "/" + tag in p:
                return "남단 교대" if tag == "NAppHead" else (
                    "교각" if tag == "NAppPier" else "상판 현")
        return "기타"

    recs = []
    for p, r in prims.items():
        if "/NApp" not in p or r["type"] not in ("Cube", "Cylinder"):
            continue
        cor, (z0, z1) = compose(p)
        recs.append((p, group(p), cor, z0, z1))
    if not recs:
        return dict(error="NApp 프림 없음")
    xs = [c[0] for _, _, cor, _, _ in recs for c in cor]
    ys = [c[1] for _, _, cor, _, _ in recs for c in cor]
    zs = [z for _, _, _, z0, z1 in recs for z in (z0, z1)]
    per = {}
    for p, g, cor, _z0, _z1 in recs:
        sm = min(s_of(x, y) for x, y in cor)
        if g not in per or sm < per[g][0]:
            per[g] = (sm, p)
    an = geom_metrics(align_current())
    smin = min(v[0] for v in per.values())
    # 해석 occluder(상판 현 박스)와 같은 대상만 비교
    deck_only = min(v[0] for g, v in per.items() if g == "상판 현")
    return dict(n_prims=len(prims), n_napp=len(recs),
                prim_x=(round(min(xs), 3), round(max(xs), 3)),
                prim_y=(round(min(ys), 3), round(max(ys), 3)),
                prim_z=(round(min(zs), 3), round(max(zs), 3)),
                prim_s_min_all=round(smin, 3),
                prim_s_min_deck=round(deck_only, 3),
                per_group={g: (round(v[0], 3), v[1].split("/")[-2] + "/"
                               + v[1].split("/")[-1]) for g, v in per.items()},
                analytic_s_min=an["s_min"],
                analytic_x=(an["x_min"], an["x_max"]),
                analytic_y=(an["y_min"], an["y_max"]))


# ===========================================================================
# [5] main
# ===========================================================================
def align_mirror_north():
    """V4 — 현행의 완전 거울상: 90° **우**회전 후 도달 s 를 북쪽으로 유지."""
    p0, a0, _piv, _yaw = deck_start(None)
    pts, brs = [p0], []
    b = a0
    seg = BG["napp_curve_len"] / len(BG["napp_deltas"])
    for d in BG["napp_deltas"]:
        bc = b - d / 2.0                                  # 부호만 반전
        pts.append((pts[-1][0] + seg * math.cos(math.radians(bc)),
                    pts[-1][1] + seg * math.sin(math.radians(bc))))
        brs.append(bc)
        b -= d
    s_hold = pts[-1][0] - M.river_dx(pts[-1][1])
    # 직진부 스테이션은 현행의 **간격을 그대로 거울상**으로 (전이 종점 기준 북향)
    v0 = M.near_approach_chords()[0]
    y_turn0 = v0[len(BG["napp_deltas"]) - 1]["y1"]
    steps, prev = [], y_turn0
    for yk in BG["napp_ypar"]:
        steps.append(abs(yk - prev))
        prev = yk
    y_end, ypar = pts[-1][1], []
    for st in steps:
        y_end += st
        ypar.append(y_end)
    for yk in ypar:
        pts.append((M.river_dx(yk) + s_hold, yk))
        brs.append(math.degrees(math.atan2(pts[-1][1] - pts[-2][1],
                                           pts[-1][0] - pts[-2][0])))
    ch = _chords_from_points(pts, brs, BG["deck_top"] - STAG, BG["napp_grade"],
                             BG["napp_vlen"], BG["napp_lead"])
    return dict(name="V4 [대조] 근측 고가 북향 90° 곡선(현행의 거울상)",
                chords=ch, s_hold=s_hold, b_yaw=None, turn=-90.0,
                curve_len=BG["napp_curve_len"], grade=BG["napp_grade"],
                pier_j=list(BG["napp_pier_j"]))


def build_variants():
    """평가 대상 정렬안 묶음. V0=현행, VN=근측 미시공 바닥, V1~V3 = 후보."""
    out = [align_current()]
    # VN — 근측 고가 미시공(참조 바닥: GT-83 3차 이전 상태의 차폐)
    out.append(dict(name="VN 근측 고가 미시공(참조 바닥)", chords=[], s_hold=None,
                    b_yaw=None, turn=0.0, curve_len=0.0,
                    grade=BG["napp_grade"], pier_j=[]))
    # V1 — 근측 고가만 x축(−X) 평행. 전이 13.0 m 유지(현행과 같은 전이 예산).
    out.append(align_turn_to(180.0, 13.0, BG["napp_grade"],
                             name="V1 근측 고가 x축 평행 · 종단 2.0 %(씬 채택값)"))
    # V1b — 같은 평면선형, 착지를 노린 종단 5.0 %
    out.append(align_turn_to(180.0, 13.0, 0.050,
                             name="V1b 근측 고가 x축 평행 · 종단 5.0 %(착지 시도)"))
    # V2 — ±본교 축 정렬: 전이 없이 본교 축 그대로 직진(패스2 거부안)
    out.append(align_turn_to(180.0 + M.river_yaw(-23.0), 0.0, BG["napp_grade"],
                             name="V2 본교 축 직진 연장(전이 0 · 패스2 거부안)"))
    # V3 — 본교까지 x축 정렬(요 0) + 근측 직진
    out.append(align_turn_to(180.0, 0.0, BG["napp_grade"], b_yaw=0.0,
                             name="V3 본교+근측 전부 x축 정렬(하천 사교 25.09°)"))
    # V4 — 대칭 대조: 현행과 완전 대칭인 90° 우회전(북향) + 같은 s_hold 규약.
    out.append(align_mirror_north())
    # V3n — V3 의 분해용: 본교만 요 0, 근측 고가 없음
    out.append(dict(name="V3n [분해] 본교만 요 0 · 근측 고가 없음", chords=[],
                    s_hold=None, b_yaw=0.0, turn=0.0, curve_len=0.0,
                    grade=BG["napp_grade"], pier_j=[]))
    return out


def main_span_metrics(b_yaw=None):
    """본교 자체의 하천 관계 지표: 사교각·경간·교각/교대 착지 구역."""
    b_cy = (BG["y0"] + BG["y1"]) / 2.0
    b_xm = (BG["x0"] + BG["x1"]) / 2.0
    bdx = M.river_dx(b_cy)
    yaw = M.river_yaw(b_cy) if b_yaw is None else b_yaw
    piv = (bdx + b_xm, b_cy)
    skew = abs(M._ang(yaw - M.river_yaw(b_cy)))

    def w(px):
        q = M._rot_xy((bdx + px, b_cy, 0.0), piv, yaw)
        return q[0], q[1], s_of(q[0], q[1])
    out = dict(yaw=round(yaw, 3), skew_to_channel=round(skew, 2), members=[])
    for lbl, px, half in (("근측 벽식교각", BG["x0"], BG["abut_t"] / 2.0),
                          ("교각 P1", BG["pier_x"][0], BG["pier_r"]),
                          ("교각 P2", BG["pier_x"][1], BG["pier_r"]),
                          ("교각 P3", BG["pier_x"][2], BG["pier_r"]),
                          ("원측 벽식교각", BG["x1"], BG["abut_t"] / 2.0),
                          ("원측 교대", BG["x1"] + BG["appr_len"],
                           BG["abut_t"] / 2.0)):
        x, y, s = w(px)
        # 회전 후 부재 코너의 s 폭
        ss = []
        for dxx in (-half, half):
            for dyy in (-DECK_HW, DECK_HW):
                q = M._rot_xy((bdx + px + dxx, b_cy + dyy, 0.0), piv, yaw)
                ss.append(s_of(q[0], q[1]))
        out["members"].append(dict(name=lbl, x=round(x, 2), y=round(y, 2),
                                   s=round(s, 2),
                                   s_span=(round(min(ss), 2), round(max(ss), 2)),
                                   zone=zone_of(s),
                                   zone_lo=zone_of(min(ss)),
                                   zone_hi=zone_of(max(ss))))
    # 유수부(수면 s 18.2…52) 횡단 연장
    out["water_crossing_m"] = round((52.0 - S_EDGE)
                                    / math.cos(math.radians(skew)), 2)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--aabb", action="store_true", help="프림 AABB 교차검증")
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    rep = dict(scene="scene03_riverbank", note="기하 무변경 · CPU 전용")
    print("=" * 78)
    print("scene03 x축 정렬안 프로브 — 기하 무변경 · CPU 전용")
    print("=" * 78)

    # --- self-test: 씬 자체 selfcheck 재현 ---
    cur = align_current()
    base = occlusion(chord_boxes(cur["chords"]))
    ok_v, diag = M.river_view_selfcheck(verbose=False)
    st = all(base[k]["occluded"] == diag[k]["occluded"]
             and base[k]["n"] == diag[k]["n"] for k in diag)
    print(f"\n[self-test] 씬 river_view_selfcheck 재현 = {'PASS' if st else 'FAIL'}")
    for k in diag:
        print(f"    {k:13s} 씬 {diag[k]['occluded']}/{diag[k]['n']}"
              f"  프로브 {base[k]['occluded']}/{base[k]['n']}"
              f"  휨 씬 {diag[k]['bow_pct']} / 프로브 {base[k]['bow_pct']}")
    rep["selftest"] = st
    if not st:
        print("!! 재현 실패 — 이하 수치는 신뢰 불가")

    # --- 정렬안별 ---
    rep["variants"] = []
    for al in build_variants():
        g = geom_metrics(al)
        oc = occlusion(chord_boxes(al["chords"]), b_yaw=al["b_yaw"])
        clash, reed_hit = prop_clash(al)
        fo = frame_occupancy(al["chords"])
        rec = dict(name=al["name"], geom=g, occl=oc, clash=clash,
                   reed_chords=reed_hit,
                   frame={k: v for k, v in fo.items()
                          if v and v["in_frame"] > 0})
        rep["variants"].append(rec)
        print("\n" + "-" * 78)
        print(f"### {al['name']}")
        print("-" * 78)
        if g.get("empty"):
            print("  (근측 고가 없음 — 본교·원측 접속교만)")
        else:
            print(f"  연장 {g['length']:.2f} m · 현 {g['n_chords']} · 회전 "
                  f"{g['turn_deg']}° · 최대 절선각 {g['kink_max']}° · R_min "
                  f"{g['R_min']} m (호 등가 {g['R_arc']}) · 종단 {g['grade_pct']} %")
            print(f"  s 범위 {g['s_min']} … {g['s_max']}   "
                  f"world x {g['x_min']} … {g['x_max']} · y {g['y_min']} … {g['y_max']}")
            print(f"  낙차에지(s=0) 교차 = {g['crosses_drop_edge']} "
                  f"(여유 {g['s_margin_to_drop']} m) · 산책로 외연(s=−1) 여유 "
                  f"{g['s_margin_to_promenade']} m")
            if g["drop_cross"]:
                print(f"    ↳ 중심선 s=0 통과: y {g['drop_cross']['y']} · "
                      f"소핏 {g['drop_cross']['soffit']} m (둑마루 0.000 기준)")
            print(f"    낙차에지 밴드(|s|≤1) 상판 피복 y 연장 "
                  f"{g['drop_edge_cover_m']} m {g['drop_edge_cover_y'] or ''}")
            print(f"  hazard corridor(y±0.95) 이격 {g['corridor_gap']} m "
                  f"(침범 {g['corridor_breach']})")
            print(f"  최소 소핏 여유 {g['min_soffit_clear']} m @ {g['min_soffit_at']}")
            print(f"  접지점 {g['touchdown']}")
            print(f"  구역 점유 % {g['zone_share']}")
            print(f"  교각 {len(g['piers'])}기:")
            for pr in g["piers"]:
                print(f"    - 현{pr['chord']:2d}  s {pr['s']:7.2f}  {pr['zone']:16s}"
                      f"  하부여유 {pr['clear']:.2f} m")
        for k in ("river_along", "meander_air", "bank_oblique"):
            d = oc[k]
            print(f"  {k:13s} 차폐 {d['occluded']:3d}/{d['n']:3d} = "
                  f"{d['occ_pct']:5.2f} %  휨 {d['bow_pct']:5.2f} %  "
                  f"종방향 {d['y_span']:5.1f} m  |  가시표본 {d['vis_n']:3d} "
                  f"휨 {d['vis_bow_pct']:5.2f} % 종 {d['vis_span']:5.1f} m"
                  f"  {'PASS' if d['pass_'] else 'FAIL' if d['judge'] else '—'}"
                  f"  [귀속 정적{d['attrib']['static']}/본교{d['attrib']['main']}"
                  f"/근측{d['attrib']['napp']}]")
        if clash:
            print("  프롭 이격(<8 m · 0.00 = 상판 투영 안에 들어감):")
            for c in clash[:9]:
                print(f"    - {c['item']:12s} s {c['s']:7.2f}  거리 {c['dist']:.2f} m")
        if not g.get("empty"):
            print(f"  갈대밴드(s16–17) 통과 현 수 {reed_hit}")
            bur = [k for k, v in fo.items() if v["cam_buried"]]
            print(f"  카메라 매몰(눈이 상판 내부) = {bur if bur else '없음'}")
            keys = [k for k in ("levee_walk", "stair_down", "beach_lookup",
                                "preset_h0.3_d2", "preset_h0.3_d5",
                                "preset_h0.3_d10", "preset_h1.8_d10",
                                "meander_air", "bank_oblique", "river_along")
                    if rec["frame"].get(k)]
            if keys:
                print("  프레임 점유(프레임 내 코너 한정 u/half, v/half):")
                for k in keys:
                    f = rec["frame"][k]
                    print(f"    {k:15s} u {f['u'][0]:+.2f}…{f['u'][1]:+.2f}  "
                          f"v {f['v'][0]:+.2f}…{f['v'][1]:+.2f}  "
                          f"in {f['in_frame']}/{f['n']}")

    # --- 접지 grade 표 (x축 평행 안 전용) ---
    print("\n" + "-" * 78)
    print("### 접지 grade — 근측 고가가 둑마루(z 0.000)에 내려앉는 데 필요한 종단경사")
    print("-" * 78)
    p0, a0, _pv, _yaw = deck_start(None)
    s0 = s_of(p0[0], p0[1])
    dz = BG["deck_top"] - STAG - P["levee"]["z_top"]
    rows = []
    for tgt_s, lbl in ((0.0, "낙차 에지 s=0"), (-1.0, "산책로 외연 s=−1"),
                       (-5.4, "연석밴드 s=−5.4"), (-20.0, "둑마루 s=−20"),
                       (-42.0, "제방 서단 s≈−42")):
        run = s0 - tgt_s
        g = dz / run if run > 0 else float("inf")
        rows.append(dict(target=lbl, run=round(run, 2), grade_pct=round(100 * g, 2)))
        print(f"  {lbl:20s} 수평연장 {run:6.2f} m → 필요 종단경사 {100*g:6.2f} %")
    print(f"  (기점 s {s0:.3f} · 낙차 {dz:.3f} m · 씬 채택 종단 "
          f"{100*BG['napp_grade']:.1f} % · 원측 접속교 {100*BG['appr_grade']:.1f} %)")
    rep["touchdown_grades"] = rows

    print("\n  둑마루 산책로(s −5.4…−1.0) 상부 통과 시 소핏 여유 [m]:")
    sof0 = BG["deck_top"] - STAG - BG["deck_thick"]
    need = {}
    for gpct in (0.0, 2.0, 5.0, 7.0):
        v = [sof0 - (gpct / 100.0) * (s0 - ss) for ss in (-1.0, -5.4)]
        need[gpct] = (round(v[0], 3), round(v[1], 3))
        print(f"    종단 {gpct:4.1f} % 하향 → s=−1 {v[0]:6.3f} · s=−5.4 {v[1]:6.3f}")
    print(f"    (보행 유효고 2.500 확보에 필요한 상판 상향량: 종단 0 % 기준 "
          f"{2.5 - need[0.0][1]:.3f} m · 종단 2 % 기준 {2.5 - need[2.0][1]:.3f} m)")
    print(f"    (도로 건축한계 4.500 기준 상향량: 종단 0 % "
          f"{4.5 - need[0.0][1]:.3f} m)")
    rep["promenade_clearance"] = need

    print("\n" + "-" * 78)
    print("### 본교 자체 — 하천 관계(현행 vs 요 0)")
    print("-" * 78)
    for lbl, by in (("현행(사행 접선 직교)", None), ("x축 정렬(요 0)", 0.0)):
        ms = main_span_metrics(by)
        rep.setdefault("main_span", {})[lbl] = ms
        print(f"  [{lbl}] 상판 요 {ms['yaw']}° · 하천 축 대비 사교각 "
              f"{ms['skew_to_channel']}° · 유수부 횡단 연장 "
              f"{ms['water_crossing_m']} m")
        for mm in ms["members"]:
            print(f"    - {mm['name']:12s} s {mm['s']:7.2f} "
                  f"[{mm['s_span'][0]:7.2f}…{mm['s_span'][1]:7.2f}]  "
                  f"{mm['zone_lo']} → {mm['zone_hi']}")

    if a.aabb:
        print("\n" + "-" * 78)
        print("### 프림 AABB 교차검증 (현행 기하)")
        print("-" * 78)
        r = aabb_check()
        rep["aabb"] = r
        for k, v in r.items():
            print(f"  {k}: {v}")

    if a.json:
        with open(a.json, "w") as f:
            json.dump(rep, f, ensure_ascii=False, indent=1)
        print(f"\n[json] {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
