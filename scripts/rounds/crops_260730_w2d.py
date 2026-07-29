#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""W2-D 판정 라운드 확대 크롭 — 눈 검증 에이전트에게 넘길 증거 컷.

각 크롭은 **한 가지 질문에만** 답하도록 잘랐다. 프레임 전체를 주면 사람은 가장 큰
대비에 눈이 가고, 정작 물어본 0.1 mm 단차·2 mm 판재 틈은 못 본다.

크롭 목록과 그 질문 (`w2d_kitfix_v1.md` §9 · `redteam_w2d_edits.md` §7 · 임무 A4)
  10/12 deck_plank   판재 틈이 2~3 mm 로 읽히는가 (R1 이 매몰을 풀었다)
  07/10 stain_overlap R3 데칼 사다리의 최소단(stain kind 간 0.1 mm)이 깜빡이는가
  N5/13/15 gate      각 씬의 게이트 지표 대상 (N5 맨홀 팔각 · 13 램프 연석 · 15 맨홀 알베도)
  14 lower_lookup    V-notch (D11) — 양쪽 사전 분석이 붙은 채로 재확인
  05 charcoal d10    씬 소유 전폭 횡단선이 d10 E 대역에서 립과 융합하는가
  tactile Ø35        점자 돌기 지름 재결재 결과 (D10)
  19/21 w80          톤 목표 씬의 백색 수준
출력: look_check/_experiments/gates/w2d_crops/  (README §1 — 크롭은 씬 루트에 넣지 않는다)

사용:  python3 scripts/rounds/crops_260730_w2d.py [--round 260730_w2d_judge]
GPU 0 · PIL 만 필요.
"""
from __future__ import annotations

import argparse
import json
import os

from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = os.path.join(REPO, "look_check")
OUT = os.path.join(BASE, "_experiments", "gates", "w2d_crops")
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"

# (name, scene, view, (x0,y0,x1,y1) as fractions of the frame, zoom, question)
CROPS = [
    # --- R1: deck plank gaps must read 2-3 mm -----------------------------
    ("s10_deck_plank_d2", "scene10", "preset_h0.3_d2", (0.20, 0.62, 0.80, 1.00), 2.0,
     "판재 틈 2~3 mm 로 읽히는가 (R1 매몰 해제 후)"),
    ("s12_deck_plank_d2", "scene12", "preset_h0.3_d2", (0.20, 0.62, 0.80, 1.00), 2.0,
     "판재 틈 2~3 mm 로 읽히는가 (120 gap plan)"),
    # --- R3: the smallest step in the decal ladder is 0.1 mm --------------
    ("s07_stain_overlap_d2", "scene07", "preset_h0.3_d2", (0.15, 0.60, 0.85, 1.00), 2.0,
     "R3 잔여 — stain kind 간 0.1 mm 단차가 깜빡이는가"),
    ("s10_stain_overlap_d2", "scene10", "preset_h0.3_d2", (0.15, 0.55, 0.85, 0.95), 2.0,
     "R3 잔여 — 같은 질문, 데칼 겹침 최대 씬"),
    # --- D-5: the rock pool is rubble, not pea gravel (kitfix §9-2) --------
    ("s04_rock_scale_d5", "scene04", "preset_h0.3_d5", (0.05, 0.50, 0.95, 1.00), 1.6,
     "D-5 산포 스케일 — φ 0.16~0.24 m 실암석이 자갈로 읽히는가 (04 field 250)"),
    ("s07_rock_scale_d5", "scene07", "preset_h0.3_d5", (0.05, 0.45, 0.95, 1.00), 1.6,
     "D-5 산포 스케일 — 마사토 안뜰에 왕자갈로 읽히는가 (07 field+edge 223)"),
    ("s10_rock_scale_d5", "scene10", "preset_h0.3_d5", (0.05, 0.50, 0.95, 1.00), 1.6,
     "D-5 산포 스케일 — 데크 갓길 (10 field+edge 118) · LeafRing 은 의도적 낙엽"),
    # --- gate metrics ------------------------------------------------------
    ("sN5_manhole_d2", "sceneN5", "preset_h0.3_d2", (0.10, 0.55, 0.95, 1.00), 1.8,
     "D4 — 맨홀 디스크가 눈에 보이는 팔각인가 · 근창 66 % 폭"),
    ("s01_manhole_d5", "scene01", "preset_h0.3_d5", (0.00, 0.45, 0.60, 0.95), 2.0,
     "D4+D5 동시 사례 — 팔각 실루엣 + 선언 알베도 0.10 대비 근백색 렌더"),
    ("s13_ramp_curb_entry", "scene13", "entry_approach", (0.10, 0.45, 0.95, 1.00), 1.8,
     "게이트 13-1(재정의) — 램프 양측 연석이 벽면 밝은 띠로 읽히는가"),
    ("s15_manhole_d5", "scene15", "preset_h0.3_d5", (0.10, 0.50, 0.95, 1.00), 1.8,
     "D5 — 맨홀이 포장과 구분되는가(선언 알베도 0.10 대 렌더 근백색)"),
    ("s15_weed_cube_d5", "scene15", "preset_h0.3_d5", (0.00, 0.20, 0.30, 0.60), 2.6,
     "D3 — 경계 잡초가 올리브색 정육면체로 렌더되는가(프록시 기하)"),
    # --- D11 scene14 V-notch ----------------------------------------------
    ("s14_vnotch_lower_lookup", "scene14", "lower_lookup", (0.00, 0.10, 1.00, 0.75), 1.4,
     "D11 — 측면 파라펫 톱니(V-notch)가 여전한가 (기저 기하, T1 무관)"),
    # --- scene05 charcoal bands in the d10 E band --------------------------
    ("s05_charcoal_d10", "scene05", "preset_h0.3_d10", (0.05, 0.55, 0.95, 0.95), 1.8,
     "차콜 밴드가 d10 E 대역에서 보울 립과 융합하는가 (레드팀 라이더 2)"),
    ("s05_nearfield_d2", "scene05", "preset_h0.3_d2", (0.05, 0.55, 0.95, 1.00), 1.6,
     "P1 클램프 해제 — 근경 1.4 m 에 표면요소가 실제로 들어왔는가"),
    # --- tactile Ø35 -------------------------------------------------------
    ("sC4_tactile_d2", "sceneC4", "preset_h0.3_d2", (0.15, 0.55, 0.85, 1.00), 2.2,
     "점자 돌기 Ø35 mm — 36개 6×6 · 피치 50 mm 로 읽히는가"),
    ("sN5_tactile_band", "sceneN5", "beauty_oblique", (0.10, 0.45, 0.90, 0.95), 1.8,
     "점자 띠 — 같은 질문, 무낙차 씬의 무조건 설치 사례"),
    # --- new this round: dead-flat near-field plates (flat_gnd blow-ups) ----
    ("s11_flat_plate_d2", "scene11", "preset_h0.3_d2", (0.05, 0.50, 0.95, 1.00), 1.6,
     "신규 — 데크 근경의 무텍스처 회색 판 (flat_gnd 10.4 → 53.1)"),
    ("s11_shrub_grey", "scene11", "preset_h0.3_d2", (0.30, 0.20, 0.80, 0.50), 2.4,
     "신규 — 관목이 회백색 덩어리로 (Rhododendron Flowers 비활성 후 잔여 기하?)"),
    ("s19_flat_membrane_d2", "scene19", "preset_h0.3_d2", (0.00, 0.45, 1.00, 1.00), 1.4,
     "신규 — 옥상 방수막이 상수색 평면 (w80 97.7 → 0.0 · flat_gnd 10.0 → 94.8)"),
    ("s16_bloom_planter", "scene16", "preset_h0.3_d5", (0.55, 0.00, 1.00, 0.35), 2.4,
     "계절성 — 화단에 남은 분홍 개화(Rhododendron 꽃 프림 경로별 비활성 여부)"),
    # --- tone targets ------------------------------------------------------
    ("s19_tone_d2", "scene19", "preset_h0.3_d2", (0.00, 0.55, 1.00, 1.00), 1.4,
     "톤 목표 — 옥상 방수막 w80 (목표 <40, W2-C 실측 87.5)"),
    ("s21_tone_d2", "scene21", "preset_h0.3_d2", (0.00, 0.55, 1.00, 1.00), 1.4,
     "톤 목표 — 기념관 화강석 w80"),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--round", default="260730_w2d_judge")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    try:
        f = ImageFont.truetype(FONT, 22)
    except Exception:
        f = ImageFont.load_default()

    idx, missing = [], []
    for name, scene, view, box, zoom, q in CROPS:
        src = os.path.join(BASE, scene, a.round, f"pt_noon_{view}.png")
        if not os.path.isfile(src):
            missing.append((name, src))
            continue
        im = Image.open(src).convert("RGB")
        W, H = im.size
        x0, y0, x1, y1 = (int(box[0] * W), int(box[1] * H),
                          int(box[2] * W), int(box[3] * H))
        c = im.crop((x0, y0, x1, y1))
        c = c.resize((int(c.width * zoom), int(c.height * zoom)), Image.LANCZOS)
        strip = Image.new("RGB", (c.width, c.height + 34), (18, 18, 22))
        strip.paste(c, (0, 0))
        ImageDraw.Draw(strip).text(
            (10, c.height + 6), f"{scene} {view}  ×{zoom}  — {q}", font=f,
            fill=(225, 225, 230))
        fp = os.path.join(a.out, f"{name}.png")
        strip.save(fp)
        idx.append(dict(name=name, scene=scene, view=view, box=list(box),
                        zoom=zoom, question=q, file=os.path.basename(fp),
                        src_size=[W, H], crop_px=[x0, y0, x1, y1]))
        print(f"  {name:<28} {scene}/{view}  {c.size}")
    with open(os.path.join(a.out, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(dict(round=a.round, crops=idx, missing=missing), fh,
                  ensure_ascii=False, indent=1)
    print(f"크롭 {len(idx)}장 → {a.out}"
          + (f"  · 원본 없음 {len(missing)}: {[m[0] for m in missing]}" if missing else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
