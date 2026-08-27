# -*- coding: utf-8 -*-
"""33씬 통람 합성 — 씬별 4뷰 2×2 몽타주(원해상도) + 전체 1장 시트.

뷰별로 `--round` 폴더를 먼저 찾고, 없으면 그 씬의 최신 라운드로 폴백한다.
대체 컷은 타일에 출처 라운드를 명기한다(spec §2.5 X2 — meta 정직성).
출력: --out 폴더에 <scene>_4view.png 33장 + allview33_sheet.png 1장.

사용:
    python3 scripts/make_allview_sheet.py --round 260806_w3_allview4 \
        --out look_check/_review/w3/260806_w3_allview4
"""
import argparse
import os

from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(REPO, "look_check")
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"

NAMES = {
    "scene01": "캠퍼스 계단", "scene02": "지하도", "scene03": "하천 제방",
    "scene04": "공원 침목길", "scene05": "야외공연장", "scene06": "보행육교 나선",
    "scene07": "산사 돌계단", "scene08": "선큰 광장", "scene09": "호수공원 수변",
    "scene10": "공원 데크 갈지자", "scene11": "보도육교", "scene12": "수변 데크길",
    "scene13": "지하주차 진입부", "scene14": "착시 대계단", "scene15": "달동네 골목",
    "scene16": "지하보도 입구", "scene17": "한강 제방", "scene18": "바닷가 벽화계단",
    "scene19": "옥상 winder", "scene20": "대각 사교", "scene21": "기념관 대계단",
    "sceneC1": "C1 적설 계단", "sceneC2": "C2 낙엽 매몰 계단", "sceneC4": "C4 우후 젖은 계단",
    "sceneD1": "D1 하역장 도크", "sceneD2": "D2 슬래브 개구부", "sceneD3": "D3 노변 배수로",
    "sceneD4": "D4 지하철 승강장", "sceneN1": "N1 그림자 띠", "sceneN2": "N2 아스팔트 패치",
    "sceneN3": "N3 트롱프뢰유", "sceneN4": "N4 완경사 램프", "sceneN5": "N5 플러시 그레이팅",
}
ORDER = list(NAMES)

# 씬당 4뷰 — run_260806_w3_allview4.sh 의 VIEWS 와 동일 (소스 대조 검증본)
PICK = {
    "scene01": ["beauty_overview", "lower_lookback", "edge_closeup", "amphi_view"],
    "scene02": ["approach", "pit_edge", "inside_looking_up", "beauty_overview"],
    "scene03": ["levee_walk", "stair_down", "across_river", "bank_oblique"],
    "scene04": ["trail_approach", "step_detail", "below_lookup", "canopy_anchor"],
    "scene05": ["plaza_approach", "rim_view", "stage_lookup", "side_arc"],
    "scene06": ["overview", "spiral_up", "deck_entry", "ground_approach"],
    "scene07": ["gate_frame", "temple_walk", "stone_rhythm", "side_slope"],
    "scene08": ["beauty_overview", "pit_edge", "stair_south", "facade_court"],
    "scene09": ["park_vista", "ghat_walk", "waterline", "across_river"],
    "scene10": ["reversal", "through_treads", "leaf_edge", "from_below"],
    "scene11": ["overview", "deck_walk", "sidewalk_approach", "stair_head"],
    "scene12": ["beauty_overview", "edge_void", "deck_walk", "stair_join"],
    "scene13": ["beauty_overview", "entry_approach", "bollard_walk", "stair_head"],
    "scene14": ["beauty_overview", "terrace_read", "side_reveal", "lower_lookup"],
    "scene15": ["beauty_overview", "top_compress", "bend_landing", "narrow_up"],
    "scene16": ["beauty_overview", "approach", "shadow_band", "under_canopy"],
    "scene17": ["pair_compare", "levee_walk", "ramp_run", "across_river"],
    "scene18": ["color_front", "wave_raking", "oblique_down", "sea_beauty"],
    "scene19": ["roof_skyline", "entry_gate", "upper_approach", "winder_mid"],
    "scene20": ["oblique_overview", "walk_axis_front", "along_diagonal", "low_grazing"],
    "scene21": ["facade_front", "oblique", "crown_graze", "railing_line"],
    "sceneC1": ["approach", "grazing_top", "rail_side", "lower_lookback"],
    "sceneC2": ["approach_walk", "buried_edge", "rail_cue", "beauty_side"],
    "sceneC4": ["approach", "grazing_mirror", "film_closeup", "lower_lookback"],
    "sceneD1": ["beauty_overview", "edge_approach", "bay_corner", "edge_walk"],
    "sceneD2": ["beauty_overview", "approach", "brink", "graze"],
    "sceneD3": ["culvert_far", "channel_reveal", "verge_walk", "oblique_cross"],
    "sceneD4": ["tunnel_vista", "track_reveal", "edge_approach", "edge_graze"],
    "sceneN1": ["beauty_oblique", "approach", "band_grazing", "band_edge_close"],
    "sceneN2": ["beauty_oblique", "approach", "patch_confusion", "patch_grazing"],
    "sceneN3": ["beauty_overview", "design_eye", "off_axis", "joint_cross"],
    "sceneN4": ["beauty_overview", "ramp_head", "wall_run", "landing_lookback"],
    "sceneN5": ["beauty_oblique", "approach", "grating_close", "manhole_pair"],
}


def views_of(scene, rnd):
    """뷰별 (view, path, round). `rnd` 우선, 없으면 최신 라운드 폴백."""
    sdir = os.path.join(BASE, scene)
    fallbacks = sorted(
        (d for d in os.listdir(sdir)
         if d != rnd and os.path.isdir(os.path.join(sdir, d))),
        key=lambda d: os.path.getmtime(os.path.join(sdir, d)), reverse=True)
    out = []
    for v in PICK[scene]:
        for cand in [rnd] + fallbacks:
            p = os.path.join(sdir, cand, f"pt_noon_{v}.png")
            if os.path.isfile(p) and os.path.getsize(p) > 0:
                out.append((v, p, cand))
                break
    return out


def montage(scene, shots, out_dir, main_round, f_head, f_tag):
    """2×2 원해상도(1920×1080 타일) — 뷰 이름 + (대체 컷이면) 출처 라운드."""
    TW, TH, HEAD = 1920, 1080, 72
    im0 = Image.new("RGB", (TW * 2, HEAD + TH * 2), (14, 14, 18))
    dr = ImageDraw.Draw(im0)
    dr.text((20, 8), f"{scene}  {NAMES[scene]}", font=f_head, fill=(238, 238, 238))
    for i, (vname, p, rnd) in enumerate(shots):
        x0, y0 = (i % 2) * TW, HEAD + (i // 2) * TH
        im = Image.open(p).convert("RGB")
        if im.size != (TW, TH):
            im = im.resize((TW, TH), Image.LANCZOS)
        im0.paste(im, (x0, y0))
        tag = vname if rnd == main_round else f"{vname} · {rnd}"
        w = dr.textlength(tag, font=f_tag)
        dr.rectangle([x0, y0, x0 + w + 24, y0 + 46], fill=(0, 0, 0))
        dr.text((x0 + 12, y0 + 4), tag, font=f_tag, fill=(235, 235, 235))
    fp = os.path.join(out_dir, f"{scene}_4view.png")
    im0.save(fp, optimize=True)
    return fp


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--round", default="260806_w3_allview4")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    f_head = ImageFont.truetype(FONT, 48)
    f_tag = ImageFont.truetype(FONT, 30)
    f_row = ImageFont.truetype(FONT, 26)
    f_title = ImageFont.truetype(FONT, 44)

    # 전체 시트: 행=씬, 열=4뷰 (480×270 타일)
    TW, TH, LAB, TOP = 480, 270, 34, 64
    sheet = Image.new("RGB", (TW * 4, TOP + len(ORDER) * (TH + LAB)), (14, 14, 18))
    ds = ImageDraw.Draw(sheet)
    ds.text((16, 8), f"NegObs 33씬 × 4뷰 통람 — round {a.round}",
            font=f_title, fill=(238, 238, 238))

    incomplete, n_fallback, n_mont = [], 0, 0
    for r, scene in enumerate(ORDER):
        shots = views_of(scene, a.round)
        if len(shots) < 4:
            incomplete.append((scene, len(shots)))
        if shots:
            montage(scene, shots, a.out, a.round, f_head, f_tag)
            n_mont += 1
        y0 = TOP + r * (TH + LAB)
        ds.text((16, y0), f"{scene}  {NAMES[scene]}"
                + ("" if len(shots) == 4 else f"  [{len(shots)}/4]"),
                font=f_row, fill=(238, 238, 238))
        for c, (vname, p, rnd) in enumerate(shots):
            if rnd != a.round:
                n_fallback += 1
            im = Image.open(p).convert("RGB").resize((TW - 4, TH - 4),
                                                     Image.LANCZOS)
            sheet.paste(im, (c * TW + 2, y0 + LAB + 2))
            ds.text((c * TW + 10, y0 + LAB + 6),
                    vname if rnd == a.round else f"{vname} · {rnd}",
                    font=f_row, fill=(220, 220, 220))
    fp = os.path.join(a.out, "allview33_sheet.png")
    sheet.save(fp, optimize=True)
    print(f"saved: {fp} {sheet.size}")
    print(f"montages: {n_mont}/33 · fallback cuts: {n_fallback}/132"
          + (f" · incomplete: {incomplete}" if incomplete else ""))


if __name__ == "__main__":
    main()
