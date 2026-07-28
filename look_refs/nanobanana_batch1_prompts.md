# 나노바나나 배치1 프롬프트 (2026-07-27)

라이브러리 T1~T21에 없는 축 3계열. 생성 이미지 13장 반입·프롬프트 매칭 및 파일명 정리 완료(07-27). **배경은 낮(주간)으로 고정 — C3 야간은 연구 스코프 제외로 미사용.**

## 이미지 ↔ 프롬프트 매칭 (13장, 07-27 정리)

| 파일명 | ID | 상태 |
|---|---|---|
| `n1_shadow.jpg` | N1 건물 그림자 띠 | OK |
| `n2_asphalt_patch.jpg` | N2 검은 아스팔트 패치 | OK — v2 재생성본(07-27), 평지 조건 충족. v1(실제 구덩이로 생성돼 사용 불가)은 `n2_asphalt_patch_v1_rejected.jpg` |
| `n3_trompe_loeil.jpg` | N3 트롱프뢰유 | OK |
| `n4_ramp.jpg` | N4 내리막 완경사로 | OK (이미지상 오르막처럼도 보임 — 채택 시 시점 확인) |
| `n5_grating.jpg` | N5 그레이팅·맨홀 | OK |
| `c1_snow_stairs.jpg` | C1 눈 덮인 계단 | OK — 단 스텝 엣지가 프롬프트 의도보다 뚜렷하게 남음, 우상단에 차량 일부 |
| `c2_leaf_stairs.jpg` | C2 낙엽 덮인 상단부 | OK — 상단 3단 완전 매몰 조건은 약함(엣지 일부 보임) |
| `c3_night_EXCLUDED.jpg` | C3 야간 | **미사용** — 낮 배경 고정 방침에 따라 스코프 제외 |
| `c4_wet_stairs.jpg` | C4 젖은 석재 계단 | OK — 하늘 반사로 트레드 병합 의도 잘 재현 |
| `d1_loading_dock.jpg` | D1 하역장 플랫폼 엣지 | OK — **v3 최종**(07-27): 온플랫폼 보행 시점, 경고 도색 띠 너머 하부 바닥 완전 비가시(핵심 컨셉 부합). 구조는 **ㄷ자 만입 베이**(좌측에 범퍼·사선 도색 벽이 ㄷ자로 꺾임). 보조: `d1_loading_dock_v2_overview.jpg`(외부 부감 — 기하 역추정용), `d1_loading_dock_v1.jpg` |
| `d2_floor_opening.jpg` | D2 공사장 개구부 | OK |
| `d3_drainage_channel.jpg` | D3 도시 콘크리트 측구 | OK |
| `d4_subway_platform.jpg` | D4 지하철 승강장 연단 | OK |

**유효 12종 전부 채택 가능(07-27 확정).** N2·D1은 v2로 교체 완료. 레퍼런스 수집 종료 — 시점·기하·GT는 Isaac Sim 구현에서 결정하므로 이미지의 시점 편차는 무시(재질·조명·미장센만 번역 대상).

공통 접미사(전 프롬프트 뒤에 부착):
> Photorealistic photograph, shot from a low camera height of about 0.9 meters (waist height), camera perfectly level and horizontal, wide-angle lens around 24mm, overcast or soft daylight, no people, no text or watermarks, documentary style, natural muted colors.

## A. Hard Negative — 낙차처럼 보이지만 평지 (GT = 낙차 없음)

**N1. 건물 그림자 띠**
> A flat empty concrete plaza in front of a tall building. A long, sharp-edged, very dark shadow band cast by the building cuts across the plaza floor, making the dark area look like a sudden drop or pit, but the ground is completely flat and continuous. The pavement texture continues faintly inside the shadow.

**N2. 검은 아스팔트 패치**
> A flat asphalt road where a large rectangular patch of fresh, very dark new asphalt has been laid into the older gray faded asphalt. The new patch is much darker and looks almost like a hole, with a crisp cut line between old and new pavement. Completely flat surface.

**N3. 트롱프뢰유 (바닥 그림 계단)**
> A flat pedestrian street with a large trompe-l'oeil 3D chalk-style painting on the ground that depicts descending stone stairs going down into the ground. The painting is highly convincing from this viewing angle, but subtle cues reveal it is flat: slightly faded paint, no real shadows from the fake steps, pavement joints running straight through the artwork.

**N4. 내리막 완경사로**
> A gently descending straight concrete pedestrian ramp, slope about 5 percent, going downhill for 30 meters between low walls. No steps anywhere. The far end of the ramp disappears below the horizon line, which can be mistaken for a drop-off, but it is only a smooth continuous slope.

**N5. 평면 그레이팅·맨홀**
> A flat sidewalk with a long steel drainage grating strip and two round manhole covers embedded flush into the pavement. The dark slots of the grating look like they could be openings, but everything is flush and walkable. Slight wetness on the metal.

## B. 조건 변주 — 기존 기하 + 환경

**C1. 눈 덮인 계단 (핵심)**
> An outdoor concrete staircase of about 12 steps descending away from the camera, viewed from the top landing. Fresh snow about 5cm deep completely covers the steps, smoothing them into an ambiguous white slope where individual step edges are invisible. Only a handrail on one side and a few faint depressions hint that stairs exist underneath. Overcast winter light, low contrast.

**C2. 낙엽 덮인 상단부**
> A park staircase with stone steps descending into trees, viewed from the approach path at the top. Dense fallen autumn leaves completely bury the first three steps so the top edge of the staircase is invisible; lower steps gradually emerge from the leaves. A metal handrail continues down as the only clear cue.

**C3. (제외 — 야간, 연구 스코프 밖)**

**C4. 비 온 직후 젖은 석재**
> A wide outdoor stone staircase descending away from the camera just after rain. The wet stone treads mirror the bright overcast sky, so the reflective step surfaces visually merge together and the step edges are hard to distinguish. Small puddles on some treads.

## C. 비계단 낙차 — 클래스 확장

**D1. 하역장 플랫폼 엣지**
> A warehouse loading dock viewed from on top of the platform, looking toward the platform edge. The concrete platform ends in a sharp 1.2 meter vertical drop to the truck apron below. Yellow-black warning paint on the edge is faded and half worn away. Rubber dock bumpers visible below the edge.

**D2. 공사장 개구부**
> An unfinished concrete building floor slab under construction with a rectangular floor opening about 1.5 by 2 meters, no cover and no guardrail, dropping to the floor below. Rebar, dust and construction debris around. The opening interior is dark. Viewed from about 4 meters away at walking approach angle.

**D3. 도시 콘크리트 측구**
> A dry concrete drainage channel about 1 meter wide and 0.8 meters deep running alongside a suburban road, parallel to the camera's path. The channel edge is flush with the pavement with no railing. Some dry leaves at the bottom. The near edge is partially obscured by roadside grass.

**D4. 지하철 승강장 연단**
> An empty subway station platform viewed along its length from platform level. The platform edge drops off to the track bed below. Yellow tactile warning tiles run along the edge. The track area is noticeably darker than the lit platform. No train, no people.

## 멀티앵글 편집 프롬프트 (씬 채택 후 grazing 검증용)

> Same exact scene, same lighting and materials, but move the camera: (a) 5 meters further back at the same height / (b) camera height lowered to 0.3 meters / (c) viewed from 30 degrees to the left.

## 다음 단계

1. ~~이미지 13장 ↔ 프롬프트 ID 매칭·파일명 정리~~ (완료 07-27, 위 매칭표 참조)
2. ~~N2·D1 재생성~~ (완료 07-27, v2 교체)
3. 채택 씬 기하 역추정(낙차 깊이·폭·재질) → scene_common 빌더 매핑
4. hard negative 씬은 GT 라벨 "낙차 없음"으로 구성 (기존 21씬 전부 양성이라 첫 반례 세트)
