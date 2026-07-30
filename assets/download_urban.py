#!/usr/bin/env python3
"""Procure W3 urban assets — buildings, Korean signage, street furniture, CC0 props.

Sibling of `download_vegetation.py`; it does **not** touch that file or its tree.
Target roots:

    assets/urban/       NVIDIA Omniverse (dsready_content + simready_content)
                        → **재배포 금지**. gitignored. 재현은 이 스크립트로.
    assets/urban_cc0/   Poly Haven (CC0 1.0) — 재배포 가능하나 용량 때문에 gitignore.

Ledger: `assets/urban_manifest_w3.json` (tracked). It carries the resolved key list,
per-file bytes, and the per-asset **quirks** (metersPerUnit, z origin, tri count,
pixel verdict) that W3 integrators need. Regenerate with `--resolve` / `--verify`.

════════════════════════════════════════════════════════════════════════════
1. LICENCE GUARD — the reason this file exists at all
════════════════════════════════════════════════════════════════════════════
The DriveSim library is published at **two roots with different bytes and
different licences**, and 18,905 relative paths overlap [측정: w3r_asset_map_v1 §2.1,
redteam_w3r §1.2 재검증]:

    Assets/Isaac/4.5/NVIDIA/dsready_content/…                 ← Omniverse **Content**
    Assets/Isaac/4.5/Isaac/Environments/Outdoor/Rivermark/…   ← **Limited Use Content**

`environment-supplement-LICENSE.txt` grants Limited Use Content "for your use only,
**without modifications**" — and our pipeline scales, re-materials and re-parents
everything it loads. So the Rivermark mirror is unusable, and a typo in a key would
silently fetch the wrong bytes. `BANNED_SUBSTRINGS` is therefore a **hard error**
(`LicenceViolation`), not a filter: nothing is skipped quietly.

The same guard carries the supervisor's two declines:
  · `rivermark_plaza_bldg_*` — textually Content, but named for the Limited Use
    environment. Declined; 27 `typical_building_*` cover the same need at zero cost.
  · third-party-supplier rows — `nv_content/manifest.csv`'s `_Supplier` column is
    provenance, not a licence grant, and CGTrader / Hum3D storefront terms often
    carry AI restrictions. Declined by name [측정: manifest.csv 2,124행 파싱]:
        CGTrader           streetlamp_led_03
        Hum3D              vehicles/piaggio/ape_50
        Mathworks_Modified bollard_02 · safety_railing_01 · double_crossarm_* ×5
    (Agility3 / BDesign / SimAction / Kraken / SpeedTree rows are **not** declined.)

════════════════════════════════════════════════════════════════════════════
2. THE FOUR-FILE WRAPPER CHAIN — why `--resolve` is not optional
════════════════════════════════════════════════════════════════════════════
A dsready asset is not one USD [측정]:

    X.usd            sublayer ./X_base.usd   (+ a thumb_rig payload — ignorable)
      └─ X_base.usd  reference ./X_inst.usd  + info:mdl:sourceAsset nv_core/…/SimPBR.mdl
           └─ X_inst.usd       sublayer ./X_inst_base.usd  + **texture path OVERRIDES**
                └─ X_inst_base.usd   the geometry

Pull only `X.usd` and you get 504 tris instead of 21,965 (typical_building_10) [측정].

Trap (a) — **the outer `_inst` layer wins.** `X_inst.usd` points textures at
`../../shared_textures/…` (real); `X_inst_base.usd` points at
`materials/textures/…` (404, every time). Resolve from the composed set, and
expect the inner paths to be dead — that is normal, not a defect.

Trap (b) — **texture names do not follow the asset name.** Prefix-matching
`shared_textures/<asset>_*` gives 6 hits for `typical_building_10` but the layer
only references 4 of them; and it gives **0** for `typical_building_18`, `_106`
and `_109`, whose textures are named `brick_white_01_*`, `opaque_building_106_*`,
`opaque_ceramic_roof_*`. Guessing loses three of the ten buildings. `--resolve`
reads the layers instead [측정: 본 세션에서 세 건 모두 해소].

Trap (c) — **cross-folder relative sublayers.** `bench_park_01.usd` sublayers
`../bench_park_03/bench_park_03.usd`; `concrete_block_02.usd` and `bench_park_05.usd`
are the same shape. Flattening the tree breaks them — mirror `nv_content/` verbatim,
exactly as `assets/vegetation/` already does.

════════════════════════════════════════════════════════════════════════════
3. UNITS AND Z ORIGIN — mixed inside one library
════════════════════════════════════════════════════════════════════════════
`typical_building_10` is `metersPerUnit = 1.0`; `bldgs_01_distant/Building_178` is
**0.01** [측정]. Z origins disagree too. The manifest records `mpu`, `zmin_m` and
`z_advice` per asset; **do not assume a library-wide convention**.

⚠ One correction inherited from the red-team pass: an earlier draft told integrators
to translate `typical_building_10` **+7.904 m** in Z because its bbox zmin is
−7.904. That is wrong — only the foundation mesh reaches −7.90; every wall and
window mesh starts at z ≈ +0.10, so local z = 0 **is** street grade and the lift
would hoist the facade 7.9 m into the air. `--verify` therefore reports both the
whole-stage zmin and a `z_advice` derived from the *non-foundation* mesh spread.

Usage
─────
  python assets/download_urban.py --list
  python assets/download_urban.py --resolve            # 의존 해소 → manifest 갱신
  python assets/download_urban.py                      # manifest 기준 조달(재실행 안전)
  python assets/download_urban.py --only buildings_mid,signs_kr
  python assets/download_urban.py --verify             # usd-core + 픽셀 검증 → manifest
  python assets/download_urban.py --discover nv_content/…/typical_building_18.usd
`--resolve` / `--verify` 는 usd-core 가 필요하다 (Isaac 불필요):
  python3 -m venv /tmp/usdvenv && /tmp/usdvenv/bin/pip install usd-core
"""
import hashlib
import json
import os
import posixpath
import re
import sys
import time
import urllib.request

ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))
URBAN_DIR = os.path.join(ASSETS_DIR, "urban")          # NVIDIA — 재배포 금지
CC0_DIR = os.path.join(ASSETS_DIR, "urban_cc0")        # Poly Haven — CC0
MANIFEST_PATH = os.path.join(ASSETS_DIR, "urban_manifest_w3.json")

S3 = "https://omniverse-content-production.s3.us-west-2.amazonaws.com/"
BASE_DS = S3 + "Assets/Isaac/4.5/NVIDIA/dsready_content/"
BASE_SR = S3 + "Assets/simready_content/"
PH_API = "https://api.polyhaven.com/"
PH_RES = "1k"          # 2k 는 자산당 ~109 MB. 배후·소품에 1k 로 충분하다 [측정].

RETRIES = 3
TIMEOUT = 300
HEADERS = {"User-Agent": "curl/8.5.0"}   # Poly Haven 은 UA 없으면 403 이 난 이력이 있다

# ── 라이선스 가드 ────────────────────────────────────────────────────────────
# 이 문자열이 키/URL 어디에든 들어 있으면 **요청 자체를 하지 않고 예외로 죽는다**.
# 조용히 건너뛰면 매니페스트가 조용히 비어 버리고, 그 사실을 아무도 모른다.
BANNED_SUBSTRINGS = (
    # ① Limited Use 미러 ("without modifications")
    "Environments/",
    "/Rivermark/",
    "rivermark_plaza_bldg_",
    "Isaac/4.5/Isaac/",
    # ② 제3자 공급자 (감독 판정: 제외)
    "streetlamp_led_03",        # _Supplier = CGTrader
    "bollard_02",               # _Supplier = Mathworks_Modified
    "safety_railing_01",        # _Supplier = Mathworks_Modified
    "double_crossarm",          # _Supplier = Mathworks_Modified (5 dirs)
    "/piaggio/",                # _Supplier = Hum3D
    # ③ 사람·차량 (STATUS 규율: 사람·차량 보류) + 브랜드 차량
    "/People/",
    "/Characters/",
    "ncap_",
    "pedestrian_generic_",
    "/vehicles/ford/",
    "/vehicles/volvo/",
    "/vehicles/hero/",
)


class LicenceViolation(RuntimeError):
    """조달 대상이 금지 경로/공급자에 걸렸다. 조용한 skip 이 아니라 중단이다."""


def guard(key):
    """모든 HEAD/GET 앞에서 호출된다. 위반이면 예외."""
    for bad in BANNED_SUBSTRINGS:
        if bad in key:
            raise LicenceViolation(
                f"BANNED_SUBSTRINGS 위반: {bad!r} in {key!r}\n"
                f"  → 이 키는 Limited Use 미러 / 제3자 공급자 / 보류 클래스다. "
                f"조달 금지 (download_urban.py §1 참조).")
    return key


def guard_selftest():
    """가드가 실제로 잡는지 확인한다. 매 실행 첫머리에서 돈다 — 회귀 방지."""
    must_fail = [
        "Assets/Isaac/4.5/Isaac/Environments/Outdoor/Rivermark/dsready_content/"
        "nv_content/common_assets/props_general/bollard_01/bollard_01.usd",
        "nv_content/common_assets/props_structures/rivermark_plaza_bldg_01/"
        "rivermark_plaza_bldg_01.usd",
        "nv_content/common_assets/props_poles/streetlamp_led_03/streetlamp_led_03.usd",
        "nv_content/common_assets/props_general/safety_railing_01/safety_railing_01.usd",
        "nv_content/common_assets/props_general/bollard_02/bollard_02.usd",
        "nv_content/common_assets/props_general/double_crossarm_full_med/"
        "double_crossarm_full_med.usd",
        "nv_content/common_assets/vehicles/piaggio/ape_50/1996/main_with_physx.usd",
    ]
    must_pass = [
        "nv_content/common_assets/props_general/bollard_01/bollard_01.usd",
        "nv_content/common_assets/props_structures/typical_building_10/"
        "typical_building_10.usd",
        "nv_content/korea_mobiltech/country_assets/country_signs/sign_kr101.usd",
        "nv_content/common_assets/props_poles/streetlamp_01/streetlamp_01.usd",
    ]
    for k in must_fail:
        try:
            guard(k)
        except LicenceViolation:
            continue
        raise AssertionError(f"licence guard MISS: {k}")
    for k in must_pass:
        guard(k)          # 예외가 나면 그대로 터진다 — 과잉 차단도 버그다
    return len(must_fail), len(must_pass)


# ════════════════════════════════════════════════════════════════════════════
# 조달 명부 — **루트 키만** 적는다. 종속(_base/_inst/_inst_base/텍스처/MDL)은
# `--resolve` 가 레이어를 읽어서 채운다. 추측 금지 (§2 trap b).
# ════════════════════════════════════════════════════════════════════════════
DS = "nv_content/"
CA = DS + "common_assets/"
KR = DS + "korea_mobiltech/country_assets/"


def _sg(name):      # props_structures 자산 한 개
    return f"{CA}props_structures/{name}/{name}.usd"


def _gen(name):     # props_general
    return f"{CA}props_general/{name}/{name}.usd"


def _pol(name):     # props_poles
    return f"{CA}props_poles/{name}/{name}.usd"


def _veg(name):     # props_vegetation
    return f"{CA}props_vegetation/{name}/{name}.usd"


def _trf(name):     # props_traffic
    return f"{CA}props_traffic/{name}/{name}.usd"


# `nv_core/materials/SimPBR*.mdl` — 모든 dsready 자산의 암묵 종속(9 files / 0.14 MB).
# MDL 은 USD 레이어의 `info:mdl:sourceAsset` 로만 걸리므로 --resolve 가 SimPBR.mdl 은
# 잡지만, 형제 모듈(`SimPBR_Core` 등)은 MDL 내부 `import` 라 안 잡힌다 → 명시 등재.
CORE_MDL = [f"nv_core/materials/SimPBR{s}.mdl" for s in (
    "", "_Core", "_Model", "_Translucent", "_Billboard",
    "_Buildings", "_Buildings_Blending", "_Road", "_RoadPaint")]

# 표지판 재질 라이브러리 — sign_kr* 가 `../../../../nv_core/materials/signs/…` 로 문다.
SIGN_MTL = [
    "nv_core/materials/signs/general/metal/metal__steel_galvanized.usd",
    "nv_core/materials/signs/general/metal/metal__steel_galvanized_green.usd",
    "nv_core/materials/signs/general/metal/metal__steel_galvanized_opacity.usd",
    "nv_core/materials/signs/general/metal/metal__steel_painted_black.usd",
    "nv_core/materials/signs/general/retroreflective/retroreflective__base_mod.usd",
    "nv_core/materials/signs/general/wood/wood__aged.usd",
]

# 한국 표지판 156종은 S3 listing 에서 기계적으로 채운다(--resolve). 아래는 씬타입별
# 우선순위 목록으로, manifest 에 `shortlist: true` 로 표시된다. 의미 번호는
# 도로교통법 시행규칙 별표6 체계 [assumed] — **픽셀 검증으로 판면을 확인한 뒤** 쓸 것.
SIGN_SHORTLIST = {
    "sign_kr321": "보행자전용도로 — D 지하차도/육교 (02·06·11)",
    "sign_kr322": "횡단보도 — D",
    "sign_kr211": "진입금지 — D",
    "sign_kr224": "최고속도제한 — F 아파트 진입 (13)",
    "sign_kr226": "서행 — F",
    "sign_kr320": "자전거주차장 — F",
    "sign_krzone30": "30 존 — F",
    "sign_kr324": "어린이보호구역 — A 캠퍼스/광장 (01·08·14·21)",
    "sign_kr323": "노인보호구역 — A",
    "sign_kr325": "장애인보호구역 — A",
    "sign_kr302": "자전거전용도로 — C 공원/산책로 (04·10·16)",
    "sign_kr303": "자전거·보행자겸용도로 — C·B",
    "sign_kr333": "자전거나란히통행 — C",
    "sign_kr126": "미끄러운도로 — B 하천변 (03·09·12·17)",
    "sign_kr136": "도로공사중 — L 하역/배수 (D1·D3)",
    "sign_krconstruction_50": "공사구간 50 — L",
    "sign_krschoolzone_1": "어린이보호구역 노면/부착형 — A",
    "sign_krroadname": "도로명판 — 전 씬 공통",
}

GROUPS = {
    # ── 배후 건물: 중경 10동 ────────────────────────────────────────────────
    # 08 은 `typical_building_08_railings` 라는 별도 자산이 딸린다(난간만 4 파일).
    # 18·106·109 는 텍스처 이름이 자산명과 무관해 **--resolve 없이는 조달 불가**였다.
    "buildings_mid": [
        (_sg("typical_building_10"), "중경 기준동. 21,965 tri · 34.7×30.2×30.3 m · mpu 1.0"),
        (_sg("typical_building_11"), "중경"),
        (_sg("typical_building_12"), "중경"),
        (_sg("typical_building_13"), "중경"),
        (_sg("typical_building_03"), "중경 소형"),
        (_sg("typical_building_07"), "중경 소형"),
        (_sg("typical_building_08"), "중경 소형"),
        (_sg("typical_building_08_railings"), "08 부속 난간"),
        (_sg("typical_building_109"), "중경 — 텍스처 prefix 불일치(해소됨)"),
        (_sg("typical_building_18"), "저층 백색 플라스터+기와. **근백색 검사 대상**"),
        (_sg("typical_building_106"), "옥상 실외기 3종 포함 — 한국 파사드 신호"),
    ],
    # ── 배후 건물: 원경 7동 (2 파일 체인, mpu 0.01) ─────────────────────────
    "buildings_far": [
        (f"{CA}props_structures/bldgs_01_distant/Building_{n}.usd",
         f"원경 스카이라인 Building_{n} — mpu 0.01, ×0.01 스케일 필요")
        for n in (178, 179, 180, 181, 182, 183, 19, 20)
    ],
    # ── 한국 도로교통법 표지판 (156종 전량 + 재질 라이브러리) ────────────────
    "signs_kr": "AUTO:signs",          # --resolve 가 S3 listing 으로 채운다
    "roadmarks_kr": "AUTO:roadmarks",
    # ── 중경 수직물 ─────────────────────────────────────────────────────────
    "midground": [
        (_veg("veg_shrub_hedge_green_01"), "생울타리 녹색 — build_hedge 박스+블롭 대체"),
        (_veg("veg_shrub_hedge_round_01"), "생울타리 둥근형"),
        (_veg("veg_shrub_hedge_yellow_01"), "생울타리 황색 — **계절 게이트 대상**(이름 자체가 플래그)"),
        (_veg("veg_grass_clump_01"), "풀포기 — σ_LF 게이트 후보"),
        (_veg("veg_grass_clump_02"), "풀포기"),
        (_veg("veg_grass_clump_03"), "풀포기"),
        (_veg("veg_grass_clump_04"), "풀포기"),
        (_veg("veg_grass_clump_med_01"), "풀포기 중 LOD"),
        (_veg("veg_grass_clump_med_02"), "풀포기 중 LOD"),
        (_veg("veg_grass_clump_low_01"), "풀포기 저 LOD"),
        (_gen("ac_unit_04"), "벽부 실외기 — 한국 파사드 서명"),
        (_gen("ac_unit_05"), "벽부 실외기"),
        (_gen("ac_unit_06"), "벽부 실외기"),
        (_gen("strt_fxd_utility_box_sm_01"), "가로 통신함"),
        (_gen("bike_rack_01"), "자전거 거치대"),
        (_gen("bike_rack_02"), "자전거 거치대"),
        (_gen("bikerack_metal03"), "자전거 거치대(경량)"),
    ],
    # ── 가로등·조명두 (C2 재개방 행: 등기구 헤드만 빌려 한국형 테이퍼 폴에 얹는다) ──
    "poles": [
        (_pol("streetlamp_01"), "가로등 전체 — 형태 재판정용"),
        (_pol("streetlamp_02"), "가로등 전체"),
        (_pol("streetlamp_03"), "가로등 전체"),
        (_pol("luminaire_head01"), "**등기구 헤드만** — C2 재개방 경로의 핵심"),
        (_pol("luminaire_head_01"), "등기구 헤드"),
        (_pol("luminaire_head02"), "등기구 헤드"),
        (_pol("luminaire_head03"), "등기구 헤드"),
        (_pol("luminaire_head04"), "등기구 헤드"),
        (_pol("luminaire_arm_6ft"), "브래킷 암 1.8 m"),
        (_pol("luminaire_arm_8ft"), "브래킷 암 2.4 m"),
        (_pol("luminaire_arm_10ft"), "브래킷 암 3.0 m"),
        (_pol("pole_fxd_pedestrian_signage_01"), "보행자 표지 폴 — 표지판 마운트 참조"),
    ],
    # ── 소품 ────────────────────────────────────────────────────────────────
    "props": [
        (_gen("utility_cover_01"), "맨홀 뚜껑 — W2 F5 프로시저럴과 A/B"),
        (_gen("sidewalk_debris_01"), "보도 잔해"),
        (_gen("sidewalk_debris_02"), "보도 잔해"),
        (_gen("cinder_block"), "시멘트 블록"),
        (_gen("concrete_block_01"), "콘크리트 블록"),
        (_gen("concrete_block_02"), "콘크리트 블록 — 1 파일(크로스폴더 서브레이어)"),
        (_veg("sct_debris_leaves_dry_01"), "마른 낙엽 산포 — sct_leaf_pile(352 MB) 대신"),
        (_veg("sct_debris_leaves_dry_02"), "마른 낙엽 산포"),
        (_veg("sct_debris_leaves_dry_03"), "마른 낙엽 산포"),
        (_veg("sct_debris_leaves_dry_04"), "마른 낙엽 산포"),
        (_trf("traf_barrier_mov_type3_4feet_stripe_orange_white_01"), "Type-III 바리케이드 4 ft"),
        (_trf("traf_barrier_mov_type3_6feet_stripe_orange_white_01"), "Type-III 6 ft"),
        (_trf("traf_barrier_mov_type3_8feet_stripe_orange_white_01"), "Type-III 8 ft"),
    ],
    # ── 바위: asset_audit_v1 §2 가 남긴 0.30–1.10 m 공백 ────────────────────
    # 보유 `Vegetation/Rocks/*` 는 최대 0.31 m 라 scene12 호안 대석 대역이 비어 있다.
    "rocks_gap": [
        (_gen("rock_01"), "잡석 대형 — 0.30–1.10 m 공백 후보"),
        (_gen("rock_02"), "잡석 대형"),
        (_gen("rock_03_broken"), "파쇄암"),
    ],
    # ── 물가 ────────────────────────────────────────────────────────────────
    "water": [
        (_gen("bridge_01"), "소교량 — 치수 확인 후 판정(고속도로 규모일 수 있음)"),
        (_gen("obs_water_fountain_01"), "광장 분수"),
    ],
    # ── 라이선스 사유로만 닫혔던 행의 재개방 후보 (Korean-ness 판정은 W3 스펙 소관) ──
    # 목적은 **채택이 아니라 실측**이다. R2 의 반려는 카탈로그 치수(assumed)에 근거한
    # 것이 많아, 실제 bbox 를 재어 두면 W3 스펙이 숫자로 재판정할 수 있다.
    "reopened": [
        (_gen("bollard_01"), "C6 재개방 — 볼라드(한국 기준 h0.8–1.0 / Ø0.1–0.2 대조용)"),
        (_gen("strt_fxd_bollard_01"), "C6 재개방 — 가로 볼라드"),
        (_gen("strt_fxd_bollard_03"), "C6 재개방"),
        (_gen("strt_fxd_bollard_05"), "C6 재개방"),
        (_gen("bench_park_02"), "C1 재개방 — 벤치(한국 등벤치 1600×540×700 대조용)"),
        (_gen("bench_park_03"), "C1 재개방 — 01·05 가 이걸 크로스폴더로 문다"),
        (_gen("bench_park_01"), "C1 — **1 파일 래퍼**, ../bench_park_03 서브레이어 (trap c)"),
        (_gen("bench_park_05"), "C1 — 1 파일 래퍼"),
        (_gen("planter_round_01"), "C5 재개방 — 화분(KS F 4006 150×150 대조용)"),
        (_gen("planter_lrg_01"), "C5 재개방"),
        (_gen("trashcan_cylinder_01"), "C3 재개방 — 휴지통(2분리 Ø450–560 대조용)"),
        (_gen("trashcan_square_01"), "C3 재개방"),
    ],
}

# ── Poly Haven (CC0 1.0 — 재배포 가능) ───────────────────────────────────────
# 값은 (slug, 용도). 1k usd 번들로 받는다. `metersPerUnit` 은 자산마다 다르므로
# add_vegetation 이 이미 하는 대로 **에셋별로 읽을 것** — 0.01 로 가정 금지.
PH_MODELS = [
    ("korean_fire_extinguisher_01", "E1/E4 — 한국 제품 실스캔. 카탈로그 유일의 명시적 KR 소품"),
    ("exterior_aircon_unit", "E4 — 골목 실외기"),
    ("modular_metal_gutter", "E4 — 홈통"),
    ("rollershutter_door", "E4/배후 — 셔터 상가 1층"),
    ("rollershutter_window_01", "E4/배후 — 셔터"),
    ("rollershutter_window_02", "E4/배후 — 셔터"),
    ("utility_box_01", "E1/E4 — 배전함"),
    ("utility_box_02", "E1/E4 — 배전함"),
    ("power_box_01", "E1/E4 — 배전함"),
    ("security_light", "E4 — 보안등"),
    ("old_tyre", "E1/E4"),
    ("Barrel_01", "E1/E4 — 물통"),
    ("barrel_03", "E1"),
    ("plastic_crate_03", "E1"),
    ("cardboard_box_01", "E1"),
    ("hand_truck", "E1 — 손수레(사람·차량 아님)"),
    ("trashbag", "E1/E4"),
    ("metal_trash_can", "C3 — **골목/야적장 한정**, 광장 금지"),
    ("modular_urban_apartments_facade", "배후 CC0 — 51.5×6.7×17.0 m, 재배포 가능"),
    ("modular_fire_escape", "배후 골목"),
    ("modular_chainlink_fence", "E2 — 야적장 경계 한정"),
    ("concrete_road_barrier_02", "P3 — 방호벽"),
    ("rock_moss_set_01", "rocks_gap — 수변 이끼암 8 m 스팬"),
    ("rock_moss_set_02", "rocks_gap"),
    ("stone_01", "rocks_gap — 0.30–1.10 m 대역 후보"),
    ("tree_stump_01", "C 공원/산책로 그루터기"),
    ("tree_stump_02", "C 공원/산책로"),
    ("ocean_buoy", "물가 — 12·18"),
    ("lateral_sea_marker", "물가 — 12·18"),
    ("modular_wooden_pier", "물가 — 09·12 데크"),
    ("planter_pot_clay", "B2d — 골목 화분 참조"),
    ("painted_wooden_bench", "C1 재개방 대조군(630 tri)"),
    ("WetFloorSign_01", "소품 최경량 228 tri"),
]


# ════════════════════════════════════════════════════════════════════════════
# 네트워크
# ════════════════════════════════════════════════════════════════════════════
def open_url(url, method="GET"):
    req = urllib.request.Request(url, headers=HEADERS, method=method)
    return urllib.request.urlopen(req, timeout=TIMEOUT)


def head(url, key_for_guard=None):
    """(size, md5_or_None). ETag 가 멀티파트면 md5 는 None. 404 는 (None, None)."""
    guard(key_for_guard if key_for_guard is not None else url)
    for attempt in range(1, RETRIES + 1):
        try:
            with open_url(url, method="HEAD") as r:
                size = int(r.headers["Content-Length"])
                etag = (r.headers.get("ETag") or "").strip('"')
                md5 = etag if (len(etag) == 32 and "-" not in etag) else None
                return size, md5
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None, None
            if attempt == RETRIES:
                return None, None
            time.sleep(2 * attempt)
        except Exception:
            if attempt == RETRIES:
                return None, None
            time.sleep(2 * attempt)
    return None, None


def md5sum(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url, dest, expected_size, expected_md5, label=None):
    """이미 있고 크기가 맞으면 skip — 재실행 안전(download_vegetation 과 동일 규약)."""
    guard(url)
    name = label or os.path.basename(dest)
    if os.path.exists(dest):
        actual = os.path.getsize(dest)
        if expected_size is None or actual == expected_size:
            return "skip"
        print(f"  [redo] {name} size mismatch ({actual} != {expected_size})")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = dest + ".part"
    for attempt in range(1, RETRIES + 1):
        try:
            with open_url(url) as r, open(tmp, "wb") as f:
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    f.write(chunk)
            actual = os.path.getsize(tmp)
            if expected_size is not None and actual != expected_size:
                raise IOError(f"size mismatch {actual} != {expected_size}")
            if expected_md5 is not None:
                got = md5sum(tmp)
                if got != expected_md5:
                    raise IOError(f"md5 mismatch {got} != {expected_md5}")
            os.replace(tmp, dest)
            return "ok"
        except Exception as e:
            print(f"  [fail] {name} attempt {attempt}/{RETRIES}: {e}")
            if os.path.exists(tmp):
                os.remove(tmp)
            time.sleep(2 * attempt)
    return "fail"


def s3_list(prefix):
    """페이지드 익명 listing → [(key, size)]. prefix 는 버킷 루트 기준 전체 경로."""
    import urllib.parse
    import xml.etree.ElementTree as ET
    ns = "{http://s3.amazonaws.com/doc/2006-03-01/}"
    token, out = None, []
    while True:
        q = {"list-type": "2", "prefix": prefix, "max-keys": "1000"}
        if token:
            q["continuation-token"] = token
        with open_url(S3 + "?" + urllib.parse.urlencode(q)) as r:
            root = ET.fromstring(r.read())
        for c in root.findall(ns + "Contents"):
            out.append((c.find(ns + "Key").text, int(c.find(ns + "Size").text)))
        if (root.findtext(ns + "IsTruncated") or "false") == "true":
            token = root.findtext(ns + "NextContinuationToken")
        else:
            return out


# ════════════════════════════════════════════════════════════════════════════
# 의존 해소 (--resolve / --discover)
# ════════════════════════════════════════════════════════════════════════════
def _sdf():
    try:
        from pxr import Sdf
        return Sdf
    except ImportError:
        print("[resolve] pxr 가 없다. Isaac 은 필요 없다:\n"
              "  python3 -m venv /tmp/usdvenv && /tmp/usdvenv/bin/pip install usd-core\n"
              "  /tmp/usdvenv/bin/python assets/download_urban.py --resolve")
        sys.exit(2)


def _fetch_for_read(key, cache):
    """해소를 위해 레이어 하나를 로컬로 끌어온다(= 최종 조달 위치에 그대로 둔다)."""
    dest = os.path.join(URBAN_DIR, key)
    if key in cache:
        return cache[key]
    size, md5 = head(BASE_DS + key, key)
    if size is None:
        cache[key] = None
        return None
    if download(BASE_DS + key, dest, size, md5, key) == "fail":
        cache[key] = None
        return None
    cache[key] = (dest, size, md5)
    return cache[key]


def _layer_deps(key, local_path, Sdf):
    """레이어 하나가 참조하는 (kind, key) 목록. 상대 경로는 키 기준으로 정규화."""
    lay = Sdf.Layer.FindOrOpen(local_path)
    if lay is None:
        return []
    here = posixpath.dirname(key)
    out = []

    def norm(p):
        if not p or p.startswith("/"):
            return None
        if p.count("/") == 0 and p.endswith(".mdl"):
            return None                       # @OmniPBR.mdl@ 등 검색경로 MDL
        return posixpath.normpath(posixpath.join(here, p))

    for s in lay.subLayerPaths:
        k = norm(s)
        if k:
            out.append(("sublayer", k))

    def walk(spec):
        for a in spec.attributes:
            v = a.default
            vals = ([v] if isinstance(v, Sdf.AssetPath)
                    else list(v) if isinstance(v, Sdf.AssetPathArray) else [])
            for q in vals:
                k = norm(q.path)
                if k:
                    out.append(("asset", k))
        for attr in ("referenceList", "payloadList"):
            try:
                lst = getattr(spec, attr)
                items = (list(lst.prependedItems) + list(lst.appendedItems)
                         + list(lst.explicitItems))
                for it in items:
                    k = norm(it.assetPath)
                    if k:
                        out.append(("reference", k))
            except Exception:
                pass
        for c in spec.nameChildren:
            walk(c)
    for c in lay.rootPrims:
        walk(c)
    return out


CHAIN_SUFFIX = ("", "_base", "_inst", "_inst_base")


def resolve_asset(root_key, cache, verbose=False):
    """루트 USD 하나 → 실제로 존재하는 종속 전체.

    반환: dict(keys=[{key,bytes,md5}], dead=[...], search_mdl=[...])
    - 4 파일 래퍼 체인을 **명시적으로** 시도한다(레이어가 payload 로만 걸어두는
      경우가 있어 참조 그래프만으로는 `_inst_base` 를 놓칠 수 있다).
    - `materials/textures/**` 404 는 정상이다(§2 trap a) — `dead` 로만 기록한다.
    """
    Sdf = _sdf()
    stem = root_key[:-len(".usd")]
    todo, seen, keys, dead = [], set(), [], []
    for suf in CHAIN_SUFFIX:
        todo.append(stem + suf + ".usd")
    while todo:
        key = todo.pop(0)
        if key in seen:
            continue
        seen.add(key)
        got = _fetch_for_read(key, cache)
        if got is None:
            if key.endswith(".usd") and key not in (stem + s + ".usd" for s in CHAIN_SUFFIX):
                dead.append(key)
            elif not key.endswith(".usd"):
                dead.append(key)
            continue
        dest, size, md5 = got
        keys.append({"key": key, "bytes": size, "md5": md5})
        if not key.endswith((".usd", ".usda", ".usdc")):
            continue
        for kind, dep in _layer_deps(key, dest, Sdf):
            if "thumb_rig" in dep or "/.thumbs/" in dep:
                continue                       # 썸네일 리그 payload — 지오메트리 무관
            if dep not in seen:
                todo.append(dep)
        if verbose:
            print(f"    · {key}  {size/1e6:.2f} MB")
    return {"keys": keys, "dead": sorted(set(dead))}


def resolve_polyhaven(slug):
    """Poly Haven 1k usd 번들 → [{url, rel, bytes, md5}]."""
    with open_url(PH_API + f"files/{slug}") as r:
        f = json.load(r)
    u = f.get("usd", {})
    if PH_RES not in u:
        return None
    e = u[PH_RES]["usd"]
    out = [{"rel": f"{slug}/{os.path.basename(e['url'])}", "url": e["url"],
            "bytes": e.get("size"), "md5": e.get("md5")}]
    for rel, v in sorted(e.get("include", {}).items()):
        out.append({"rel": f"{slug}/{rel}", "url": v["url"],
                    "bytes": v.get("size"), "md5": v.get("md5")})
    return out


def auto_group(name):
    """S3 listing 으로 채우는 그룹(표지판 156종·노면표시 9종)."""
    root = "Assets/Isaac/4.5/NVIDIA/dsready_content/"
    if name == "signs":
        pre = root + KR + "country_signs/"
    elif name == "roadmarks":
        pre = root + KR + "traffic/roadmarks/"
    else:
        raise KeyError(name)
    out = []
    for k, _ in s3_list(pre):
        if "/.thumbs/" in k or not k.endswith(".usd"):
            continue
        out.append((k[len(root):], SIGN_SHORTLIST.get(
            os.path.basename(k)[:-4], "")))
    return sorted(out)


# ════════════════════════════════════════════════════════════════════════════
# 매니페스트
# ════════════════════════════════════════════════════════════════════════════
SCHEMA = "negobs_urban_manifest"
VERSION = "w3-r1-v3"


def build_manifest(groups_wanted=None):
    ok, _ = guard_selftest()
    print(f"[guard] BANNED_SUBSTRINGS self-test OK ({ok} banned keys rejected)")
    cache = {}
    man = {
        "schema": SCHEMA, "version": VERSION, "generated": time.strftime("%Y-%m-%d"),
        "scope": "W3 도시 에셋 조달 — 배후 건물·한국 표지판·가로시설·CC0 소품. "
                 "에셋 우선 원칙: 가용 에셋을 최대한 쓰고, 한국 원형을 명백히 깨는 "
                 "경우에만 프로시저럴로 되돌린다.",
        "licence": {
            "nvidia_dsready": "Omniverse Content — ML 학습 ✅ / 렌더 공개 ✅ / "
                              "USD 재배포 ❌. assets/urban/ 는 gitignore.",
            "nvidia_simready": "동일 tier (해당 prefix 에 supplement 파일 없음).",
            "polyhaven": "CC0 1.0 — 재배포 ✅. 용량 때문에 gitignore 할 뿐 법적 제약 없음.",
            "banned_root": "Assets/Isaac/4.5/Isaac/Environments/** = Limited Use "
                           "Content ('without modifications') — 전면 금지.",
            "declined_suppliers": ["CGTrader (streetlamp_led_03)",
                                   "Hum3D (piaggio/ape_50)",
                                   "Mathworks_Modified (bollard_02, safety_railing_01, "
                                   "double_crossarm_* ×5)"],
            "declined_named": ["rivermark_plaza_bldg_* (9 dirs, 06a 포함)"],
        },
        "banned_substrings": list(BANNED_SUBSTRINGS),
        "sources": {"dsready": BASE_DS, "simready": BASE_SR,
                    "polyhaven": PH_API, "polyhaven_res": PH_RES},
        "method": {
            "resolve": "루트 USD 에서 4 파일 래퍼 체인(_base/_inst/_inst_base)을 명시 전개한 뒤 "
                       "Sdf 로 subLayerPaths·references·payloads·AssetPath 속성을 재귀 수집. "
                       "MDL 은 texture_2d() 를 grep. `materials/textures/**` 404 는 정상(§2 trap a).",
            "verify": "usd-core 26.8 (CPU). Σ(faceVertexCount−2); PointInstancer 는 "
                      "protoIndices 전개. bbox 는 스테이지 전체(default+render+proxy). "
                      "mpu 는 UsdGeomGetStageMetersPerUnit.",
            "pixels": "PIL. HSV 색상각 분류(채도>0.15 만 유채색), sRGB→선형 Rec.709 휘도. "
                      "gate_woody / gate_turf 는 veg_manifest_w2.json 과 동일 정의.",
            "gpu": "미사용. 렌더·Isaac 미실행.",
        },
        "groups": {}, "assets": [], "polyhaven": [], "failures": [],
    }

    names = groups_wanted or list(GROUPS)
    for gname in names:
        spec = GROUPS[gname]
        if isinstance(spec, str) and spec.startswith("AUTO:"):
            entries = auto_group(spec.split(":", 1)[1])
            extra = SIGN_MTL if gname == "signs_kr" else []
        else:
            entries = spec
            extra = []
        print(f"\n══ resolve {gname} ({len(entries)} assets) ══")
        gfiles = gbytes = 0
        for root_key, note in entries:
            guard(root_key)
            r = resolve_asset(root_key, cache)
            nb = sum(k["bytes"] for k in r["keys"])
            gfiles += len(r["keys"])
            gbytes += nb
            aid = os.path.basename(root_key)[:-4]
            man["assets"].append({
                "id": aid, "group": gname, "source": "nvidia_dsready",
                "root_key": root_key, "note": note,
                "local_root": "assets/urban/",
                "files": len(r["keys"]), "bytes": nb,
                "keys": r["keys"], "dead_refs": r["dead"],
                "shortlist": bool(note) if gname in ("signs_kr", "roadmarks_kr") else True,
            })
            print(f"  {aid:52s} {len(r['keys']):3d}f {nb/1e6:8.2f} MB"
                  + (f"  (dead {len(r['dead'])})" if r["dead"] else ""))
        for key in extra:
            got = _fetch_for_read(key, cache)
            if got is None:
                man["failures"].append(key)
                continue
            _, size, md5 = got
            gfiles += 1
            gbytes += size
            man["assets"].append({
                "id": os.path.basename(key)[:-4], "group": gname,
                "source": "nvidia_dsready", "root_key": key,
                "note": "표지판 재질 라이브러리(sign_kr* 종속)",
                "local_root": "assets/urban/", "files": 1, "bytes": size,
                "keys": [{"key": key, "bytes": size, "md5": md5}],
                "dead_refs": [], "shortlist": True})
        man["groups"][gname] = {"files": gfiles, "bytes": gbytes}
        print(f"  ── {gname}: {gfiles} files, {gbytes/1e6:.2f} MB")

    # _core (모든 dsready 자산의 암묵 종속)
    print("\n══ resolve _core ══")
    cf = cb = 0
    for key in CORE_MDL:
        got = _fetch_for_read(key, cache)
        if got is None:
            man["failures"].append(key)
            continue
        _, size, md5 = got
        cf += 1
        cb += size
        man["assets"].append({
            "id": os.path.basename(key), "group": "_core", "source": "nvidia_dsready",
            "root_key": key, "note": "SimPBR 계열 — 전 dsready 자산 암묵 종속",
            "local_root": "assets/urban/", "files": 1, "bytes": size,
            "keys": [{"key": key, "bytes": size, "md5": md5}],
            "dead_refs": [], "shortlist": True})
    man["groups"]["_core"] = {"files": cf, "bytes": cb}
    print(f"  ── _core: {cf} files, {cb/1e6:.2f} MB")

    # Poly Haven
    print("\n══ resolve polyhaven_cc0 ══")
    pf = pb = 0
    for slug, note in PH_MODELS:
        files = resolve_polyhaven(slug)
        if not files:
            man["failures"].append(f"polyhaven/{slug} ({PH_RES} usd 번들 없음)")
            continue
        nb = sum(f["bytes"] or 0 for f in files)
        pf += len(files)
        pb += nb
        man["polyhaven"].append({
            "id": slug, "group": "polyhaven_cc0", "source": "polyhaven",
            "licence": "CC0 1.0", "note": note, "res": PH_RES,
            "local_root": "assets/urban_cc0/", "files": len(files), "bytes": nb,
            "keys": files})
        print(f"  {slug:40s} {len(files):3d}f {nb/1e6:8.2f} MB")
    man["groups"]["polyhaven_cc0"] = {"files": pf, "bytes": pb}
    print(f"  ── polyhaven_cc0: {pf} files, {pb/1e6:.2f} MB")

    recompute_totals(man)
    return man


def recompute_totals(man):
    """디스크 실측과 일치하는 **고유** 파일/바이트 합계를 낸다.

    자산별 `keys` 리스트는 일부러 완전판이다 — 공유 종속(`shared_textures/`,
    `nv_core/materials/`)이 여러 자산에 중복해서 들어 있어야 `--only <group>`
    한 그룹만 받아도 그 그룹이 온전히 돈다. 그 대신 **합계를 그냥 더하면 안 된다**:
    그렇게 하면 1,911 MB 가 나오는데 디스크에는 964 MB 밖에 없다 [측정].
    그룹별 `bytes` 는 "이 그룹만 받으면 드는 비용"(공유분 포함)이고,
    `total` 은 "전부 받았을 때 디스크에 남는 것"(공유분 1회)이다. 둘 다 필요하다.
    """
    uniq = {}
    for a in man["assets"]:
        for k in a["keys"]:
            uniq[k["key"]] = k["bytes"] or 0
    puniq = {}
    for a in man.get("polyhaven", []):
        for k in a["keys"]:
            puniq[k["rel"]] = k["bytes"] or 0
    nb, pb = sum(uniq.values()), sum(puniq.values())
    for g, v in man["groups"].items():
        v["cost_if_alone_bytes"] = v.pop("bytes", v.get("cost_if_alone_bytes", 0))
        v["cost_if_alone_files"] = v.pop("files", v.get("cost_if_alone_files", 0))
    man["total"] = {
        "unique_files": len(uniq) + len(puniq),
        "unique_bytes": nb + pb,
        "gb": round((nb + pb) / 1e9, 3),
        "nvidia": {"files": len(uniq), "bytes": nb, "root": "assets/urban/"},
        "polyhaven": {"files": len(puniq), "bytes": pb, "root": "assets/urban_cc0/"},
        "note": "그룹별 합계는 공유 종속을 중복 계상한다(그룹 단독 조달 비용). "
                "디스크 실측과 맞는 값은 이 `unique_*` 쪽이다.",
    }
    return man


def load_manifest():
    if not os.path.exists(MANIFEST_PATH):
        return None
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_manifest(man):
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(man, f, ensure_ascii=False, indent=1)
        f.write("\n")
    t = man["total"]
    print(f"\n매니페스트 → {MANIFEST_PATH} "
          f"(고유 {t['unique_files']} files, {t['unique_bytes']/1e6:.1f} MB "
          f"= {t['gb']:.3f} GB)")


# ════════════════════════════════════════════════════════════════════════════
# 조달 (기본 동작)
# ════════════════════════════════════════════════════════════════════════════
def fetch(man, groups_wanted=None):
    ok, _ = guard_selftest()
    print(f"[guard] BANNED_SUBSTRINGS self-test OK ({ok} banned keys rejected)")
    stats = {"ok": 0, "skip": 0, "fail": 0, "bytes": 0}
    failures = []
    for a in man["assets"]:
        if groups_wanted and a["group"] not in groups_wanted:
            continue
        for k in a["keys"]:
            guard(k["key"])
            dest = os.path.join(URBAN_DIR, k["key"])
            r = download(BASE_DS + k["key"], dest, k["bytes"], k["md5"], k["key"])
            stats[r] = stats.get(r, 0) + 1
            if r == "fail":
                failures.append(k["key"])
            else:
                stats["bytes"] += k["bytes"] or 0
    if not groups_wanted or "polyhaven_cc0" in groups_wanted:
        for a in man.get("polyhaven", []):
            for k in a["keys"]:
                dest = os.path.join(CC0_DIR, k["rel"])
                r = download(k["url"], dest, k["bytes"], k["md5"], k["rel"])
                stats[r] = stats.get(r, 0) + 1
                if r == "fail":
                    failures.append(k["rel"])
                else:
                    stats["bytes"] += k["bytes"] or 0
    print(f"\n조달: ok {stats['ok']} · skip {stats['skip']} · fail {stats['fail']} "
          f"· {stats['bytes']/1e6:.1f} MB")
    return failures


def structural_check(man):
    """헤더 바이트 검사 — usd-core 가 없어도 도는 최소 보증(veg 규약과 동일).

    공유 종속은 여러 자산의 키 목록에 중복해서 들어 있으므로 **경로로 dedupe**
    한다. 안 하면 SimPBR.mdl 한 건이 135 줄로 보고된다 [측정].
    """
    bad, seen = [], set()
    for a in man["assets"] + man.get("polyhaven", []):
        root = URBAN_DIR if a.get("source") != "polyhaven" else CC0_DIR
        for k in a["keys"]:
            rel = k.get("key") or k["rel"]
            if rel in seen:
                continue
            seen.add(rel)
            p = os.path.join(root, rel)
            if not os.path.exists(p):
                bad.append(f"{rel} (없음)")
                continue
            with open(p, "rb") as f:
                h8 = f.read(8)
            low = rel.lower()
            if low.endswith((".usd", ".usda", ".usdc")) and not (
                    h8.startswith(b"PXR-USDC") or h8.startswith(b"#usda")):
                bad.append(f"{rel} (USD 헤더 아님: {h8!r})")
            elif low.endswith(".png") and not h8.startswith(b"\x89PNG\r\n\x1a\n"):
                bad.append(f"{rel} (PNG 헤더 아님: {h8!r})")
            elif low.endswith((".jpg", ".jpeg")) and not h8.startswith(b"\xff\xd8\xff"):
                bad.append(f"{rel} (JPEG 헤더 아님: {h8!r})")
            elif low.endswith(".dds") and not h8.startswith(b"DDS "):
                bad.append(f"{rel} (DDS 헤더 아님: {h8!r})")
            elif low.endswith(".mdl"):
                # NVIDIA MDL 은 **저작권 주석 블록으로 시작한다**(`/****...`).
                # `startswith(b"mdl")` 는 정상 파일을 손상으로 오판한다 —
                # SimPBR.mdl·SimPBR_Translucent.mdl 이 실제로 그렇게 잡혔다.
                # 판정은 선두 4 KB 안에 `mdl <버전>` 프래그마가 있는지로 한다.
                with open(p, "rb") as f:
                    head = f.read(4096)
                if not re.search(rb"(^|\n)\s*mdl\s+[\d.]+", head):
                    bad.append(f"{rel} (MDL 버전 프래그마 없음: {h8!r})")
    return bad


USAGE = """사용법:
  python assets/download_urban.py                       # 매니페스트 기준 조달
  python assets/download_urban.py --only buildings_mid,signs_kr
  python assets/download_urban.py --resolve             # 의존 재해소 → 매니페스트
  python assets/download_urban.py --resolve --only poles
  python assets/download_urban.py --verify              # usd-core+픽셀 검증(별도 모듈)
  python assets/download_urban.py --discover <s3 key>   # 자산 1건 종속 출력
  python assets/download_urban.py --retotal            # 합계만 재계산
  python assets/download_urban.py --list
그룹: """ + ", ".join(list(GROUPS) + ["_core", "polyhaven_cc0"])


def main():
    argv = sys.argv[1:]
    if "-h" in argv or "--help" in argv:
        print(USAGE)
        return
    only = None
    if "--only" in argv:
        i = argv.index("--only")
        if i + 1 >= len(argv):
            print("--only 뒤에 그룹이 필요하다.\n" + USAGE)
            sys.exit(2)
        only = [n.strip() for n in argv[i + 1].split(",") if n.strip()]
        known = set(GROUPS) | {"_core", "polyhaven_cc0"}
        bad = [n for n in only if n not in known]
        if bad:
            print(f"모르는 그룹: {bad}\n" + USAGE)
            sys.exit(2)

    if "--list" in argv:
        man = load_manifest()
        for g in list(GROUPS) + ["_core", "polyhaven_cc0"]:
            spec = GROUPS.get(g)
            n = (len(spec) if isinstance(spec, list) else
                 (len(PH_MODELS) if g == "polyhaven_cc0" else
                  len(CORE_MDL) if g == "_core" else "auto"))
            if man and g in man.get("groups", {}):
                m = man["groups"][g]
                f = m.get("cost_if_alone_files", m.get("files", 0))
                b = m.get("cost_if_alone_bytes", m.get("bytes", 0))
                print(f"  {g:18s} {str(n):>5} assets → {f:5d} files "
                      f"{b/1e6:9.2f} MB  (단독 조달 비용, 공유분 포함)")
            else:
                print(f"  {g:18s} {str(n):>5} assets  (미해소)")
        if man:
            t = man["total"]
            print(f"  {'TOTAL (unique)':18s} {'':>5}         → "
                  f"{t['unique_files']:5d} files {t['unique_bytes']/1e6:9.2f} MB "
                  f"= {t['gb']:.3f} GB")
            print(f"    · NVIDIA   {t['nvidia']['files']:5d} f "
                  f"{t['nvidia']['bytes']/1e6:9.2f} MB → assets/urban/")
            print(f"    · PolyHaven{t['polyhaven']['files']:5d} f "
                  f"{t['polyhaven']['bytes']/1e6:9.2f} MB → assets/urban_cc0/")
        return

    if "--discover" in argv:
        i = argv.index("--discover")
        key = argv[i + 1]
        r = resolve_asset(guard(key), {}, verbose=True)
        print(f"\n# --- {key} 종속 {len(r['keys'])}개 ---")
        for k in r["keys"]:
            print(f'    "{k["key"]}",'.ljust(96) + f"# {k['bytes']/1e6:.2f} MB")
        if r["dead"]:
            print(f"# dead refs ({len(r['dead'])}) — §2 trap a 상 정상:")
            for d in r["dead"]:
                print(f"#   {d}")
        return

    if "--verify" in argv:
        import verify_urban          # 같은 폴더의 검증 모듈
        verify_urban.run(load_manifest() or {}, only)
        return

    if "--retotal" in argv:
        man = load_manifest()
        recompute_totals(man)
        save_manifest(man)
        return

    if "--resolve" in argv:
        man = build_manifest(only)
        if only:                     # 부분 해소는 기존 매니페스트에 병합
            old = load_manifest()
            if old:
                keep = [a for a in old["assets"] if a["group"] not in only]
                man["assets"] = keep + man["assets"]
                for g, v in old.get("groups", {}).items():
                    man["groups"].setdefault(g, v)
                if "polyhaven_cc0" not in only:
                    man["polyhaven"] = old.get("polyhaven", man["polyhaven"])
                recompute_totals(man)
                # 검증 결과는 --verify 가 다시 채운다
        save_manifest(man)
        return

    man = load_manifest()
    if man is None:
        print("매니페스트가 없다. 먼저 `--resolve` 를 돌릴 것.\n" + USAGE)
        sys.exit(2)
    failures = fetch(man, only)
    bad = structural_check(man)
    if bad:
        print(f"\n구조 검증 실패 {len(bad)}건:")
        for b in bad[:40]:
            print(f"  - {b}")
        failures.extend(bad)
    if failures:
        print(f"\nFAILED {len(failures)}건 — 네트워크가 막혔다면 같은 상대 경로로 "
              f"{URBAN_DIR} 아래에 수동 배치할 것.")
        sys.exit(1)
    print("All urban assets downloaded and structurally verified.")


if __name__ == "__main__":
    main()
