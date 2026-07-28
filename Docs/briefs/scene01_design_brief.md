# Scene01 캠퍼스 광장 하행계단 — 설계 브리프 (구현용, Fable 감독)

작성 2026-07-24 · 감독 Claude Fable 5 · 구현 Claude Opus 에이전트
원 지시서: `Docs/NegObs_인공씬1호_계단_구현지시서.md` (편향 교정본이 이 문서. 충돌 시 **이 문서가 우선**)

## 0. 지시서 대비 변경점 (편향 교정)

참고 사진 2장(`Docs/1784886529634.jpg`, `Docs/everytime-1784886395380.jpg` — 캠퍼스 광장, 두 번째 사진의 빨간 원이 위험 지점)을 기준으로:

1. "좁은 보도(3m) + 6단 계단 + 아스팔트 하부" → **넓은 화강암 광장 + 광폭 저단차 계단(4단) + 같은 계열 화강암 하부 광장**. 사진의 위험 본질은 "상·하부가 같은 재질이라 낮은 시점에서 단차가 완전히 소실"되는 것.
2. 상부 보도블록/하부 아스팔트 → **화강암 판재 포장 + 차콜 밴드 줄무늬**(사진 1의 스트라이프 패턴).
3. "박스 덩그러니 + 벽 힌트" → **광장 드레싱 풀셋**: 화단(짙은 화강암 경계석 + 잔디 + 어린 나무 + 지지대), 앰피시어터 계단(사진 1 우측), 벽돌 건물 파사드 2동(창문 그리드), 가로등.
4. 외부 에셋 금지 → **PolyHaven/ambientCG CC0 텍스처 허용** (기존 look_check v1도 PolyHaven 사용, 확립된 관행). 대용량 메시 에셋은 여전히 금지.
5. 유지되는 [고정]: 총 낙차 ≥ 0.3 m / 카메라 밴드 높이 0.3~2.0 m·피치 −15°~+5° / cue 토글이 위험 기하를 바꾸지 않는 불변 규칙 / Isaac Sim 4.5 `isaacsim.*` API / 실행 시퀀스.

## 1. 좌표·레이아웃 (Z-up, m, 진행축 +X, 계단 상단 모서리 = x=0)

| 구역 | 범위 | 내용 |
|---|---|---|
| 상부 광장 | x −16→0, y −8→+8, z=0 | 밝은 화강암 판재 + 차콜 밴드(폭 0.45 m, 간격 2.7 m, Y방향으로 달림) |
| 계단 | x 0→1.52, y −5.5→+5.5 | 하행 4단, RISER 0.15 / TREAD 0.38 → 총 낙차 0.6 m. 상부와 **같은 밝은 화강암** |
| 계단 측벽 | y ±5.5 바깥 0.5 m | 짙은 화강암 로우월(상부면 z=0 유지, 하부까지 내려감) |
| 앰피시어터 | x 0→2.7, y +6.0→+8.0 | 좌면 3단(단높이 0.3, 깊이 0.9) 밝은 화강암, 사진 1 우측 모티프 |
| 하부 광장 | x 1.52→14, y −8→+8, z=−0.6 | 회청 판석(PavingStones111) + 웜 틴트 → 명도차·패턴 불연속 단서 |
| 화단 A/B | 중심 (−5, −6), (−9, +6), 3×3 | 경계석 h 0.45(짙은 화강암, 캡 5cm 오버행) + 잔디 상면 + 나무 1그루 + 지지대 3본 |
| 화단 C | 중심 (7, −5.5), 3×3 | 하부 광장에 동일 구성 |
| 건물 R | y +9.5→+14, x −18→+12, h 14 | 벽돌 파사드 + 창문 그리드(4층×n열, 짙은 유리 인셋 0.15) + 상단 백색 파라펫 밴드 |
| 건물 L | y −10.5→−15, x −20→+4, h 10 | 동일 구성(3층), 약간 다른 톤 |
| 가로등 | (−6, +6.8) | 원기둥 폴 h 6 + 쌍암 + 백색 램프 헤드(주간이므로 발광 불필요) |

전 지면·계단·측벽·앰피시어터에 static 콜라이더(UsdPhysics CollisionAPI) 부착.

## 2. SCENE_CONFIG 토글 (지시서 §7 구조 유지)

```python
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False → 계단 구간을 상부와 같은 평지로 (기하 토글 유일 예외)
    "cue_railing":        True,   # 중앙 + 양측 스테인리스 핸드레일 (h 0.9, 계단 구간 + 상단 1 m 연장)
    "cue_tactile":        True,   # 점형 점자블록 띠: 상단 모서리 0.3 m 앞, 계단 폭, 깊이 0.3 m
    "cue_material_break": True,   # False → 하부 광장을 상부와 동일 재질·톤으로
    "cue_sign":           False,  # [선택] 미구현 시 config 키만 예약
    "cue_scene_dressing": True,   # 화단·나무·건물·가로등·앰피시어터 일괄
}
```

**불변 규칙 [고정]**: `hazard_stairs` 외 어떤 토글도 계단·광장 기하(트랜스폼/메시)를 바꾸지 않는다. 단서 자산의 존재/재질만 변경.

## 3. 재질 (전부 `assets/scene01/` 하위, canonical 파일명)

| 역할 | 소스 | 파일명 프리픽스 |
|---|---|---|
| 상부 광장·계단 밝은 화강암 | ambientCG **Tiles038** 4K-JPG | `plaza_light_{diff,nor,rough}.jpg` |
| 차콜 밴드·짙은 바닥 | ambientCG **PavingStones127** 4K-JPG | `band_dark_{diff,nor,rough}.jpg` |
| 하부 광장 판석 | ambientCG **PavingStones111** 4K-JPG | `plaza_lower_{diff,nor,rough}.jpg` |
| 경계석·측벽·앰피 캡 | PolyHaven **granite_tile** 4k jpg | `granite_dark_{diff,nor_dx,rough}.jpg` |
| 건물 벽돌 | PolyHaven **brick_wall_001** 4k jpg | `brick_red_{diff,nor_dx,rough}.jpg` |
| 잔디 | 기존 `assets/aerial_grass_rock_*` 재사용 | — |
| 점자블록 | PIL 절차 생성 (§4) | `tactile_yellow_{diff,nor}.png` |
| HDRI | 기존 `assets/qwantani_noon_puresky_4k*.exr` (+lookfix 파이프라인 재사용) | — |

- ambientCG: `https://ambientcg.com/get?file={ID}_4K-JPG.zip` → 압축 해제 → `_Color/_NormalDX/_Roughness`를 canonical로 rename. NormalDX 사용(OmniPBR flip_tangent_v 기본 true = DX 규약).
- PolyHaven: 기존 `assets/download_assets.py`의 API 패턴 재사용 (User-Agent 필수).
- 재질 셰이더는 **OmniPBR**(MDL 경로: `~/miniconda3/envs/env_isaaclab/lib/python3.10/site-packages/omni/mdl/core/Base/OmniPBR.mdl`, v1 clay 모드에서 검증된 경로) + `project_uvw=True, world_or_object=True(=월드 스페이스, MDL 원문 확인: "When enabled, uses world space")` 프로젝션 — False(오브젝트)로 두면 xform 스케일에 텍스처가 끌려 늘어남. 계단·바닥은 전부 축정렬 박스라 월드 큐빅 투영으로 늘어남 없음 (v1의 트라이플래너 MDL은 경사면용이었음 — 여기선 불필요).
- 타일 스케일: 광장 판재 실측 느낌 0.6~0.9 m 슬래브 기준으로 `texture_scale` 조정. 틴트: OmniPBR `diffuse_tint`로 하부 광장 웜 틴트(예: 1.06, 1.0, 0.94), cue_material_break=False면 상부와 동일 재질+틴트 1.
- 금속 난간: OmniPBR metallic 0.9 / roughness 0.35 / 밝은 회색.
- 유리창: 어두운 청회색, roughness 0.08, metallic 0.0 인셋 박스 (OmniGlass 금지 — 단순하게).

## 4. 점자블록 텍스처 (PIL 생성, 다운로드 스크립트에 포함)

- 1024² PNG. KS 표준 점형: 6×6 원형 돌기 격자(돌기 지름 ≈ 타일의 1/8, 정격자).
- diff: 채도 있는 안전 황색(#F5C400 근방) + 약한 노이즈·모서리 마모 톤 변조.
- nor: 돌기를 반구로 보고 DX 규약 노멀맵 생성(numpy로 높이맵 → 소벨 → 노멀).
- 물리 크기 0.3×0.3 m/타일 기준 texture_scale 지정.

## 5. 조명 (v1 검증 상수 이식)

- `_ensure_noon_lookfix()` 함수와 noon 상수 블록을 v1에서 **그대로 복사** (태양 캡 + 헤이즈 리프트 + DistantLight 0.53°, elev 49.79, intensity 2450, color (1, 0.969, 0.935), `hdri_sun_rotz_offset=233.5`, dome intensity 1000, noon_dome_rot −110).
- 태양 방위 기본값: 계단 노징(단 모서리)에 **사선 그림자**가 지고 하부 광장에 상부 모서리 그림자가 드리우도록 돔 회전 사용자 오프셋 파라미터 `SUN_AZ_OFFSET`(기본 0, 룩 반복에서 조정 예정).
- dawn 프리셋은 [선택] — 시간 남으면 v1 dawn 블록 이식, 아니면 생략 가능.

## 6. 카메라 프리셋 + 캡처 파이프라인 (v1 패턴 이식)

- 실행: 기본 GUI 모드(뷰포트 유지 + C 캡처 + P PT 토글 키). `NEGOBS_CAPTURE=1` 헤드리스 자동 캡처 모드, `NEGOBS_CAPTURE_DIR`(기본 `look_check/scene01`), `NEGOBS_CAPTURE_MODE=rt|pt|both`, `NEGOBS_VIEWS` 필터 — v1 §자동캡처 블록(워밍업, 파일 크기 안정화 대기, manifest.json 병합)을 그대로 이식.
- 프리셋 (전부 y=0 중심선, +X를 봄, 피치 −10°, 지시서 §9 매트릭스):
  - `preset_h{0.3,0.9,1.8}_d{2,5,10}` : eye (−d, 0, 0+h) — 9장
  - `beauty_overview` : eye (−11, −6.5, 4.2) → target (1.5, 1.5, −0.5) — 광장·계단·앰피·건물·화단이 모두 담기는 보도용 미장센
  - `lower_lookback` : eye (6, 1.5, −0.6+1.6) → target (−2, 0, 0.4) — 하부에서 계단 올려다봄
  - `edge_closeup` : eye (−1.2, −1.0, 0.55) → target (0.8, 0.3, −0.45) — 노징·점자블록 클로즈업
  - `amphi_view` : eye (−3, 3.5, 1.6) → target (2.2, 7, −0.1)
- PT 모드: totalSpp 512, maxBounces 8, denoiser on (v1 값).
- SimulationApp 설정: v1과 동일 (1920×1080, DLSS execMode 2, aa op 3, 뷰포트 오버레이 전부 off).

## 7. 코드 구조 (지시서 §10 준수)

- 단일 파일 `scene01_campus_stairs.py`. 상단: SCENE_CONFIG + PARAMS(치수 전부) + NEGOBS_PARAMS_OVERRIDE 환경변수 머지(v1 패턴).
- 함수: `build_upper_plaza / build_stairs / build_lower_plaza / build_flank_walls / build_amphitheater / build_planters / build_buildings / build_streetlight / build_cues(railing·tactile) / setup_materials / setup_lighting / setup_cameras / capture_presets`.
- 지오메트리는 `UsdGeom.Cube` 스케일 또는 커스텀 쿼드 메시. 모든 프림은 `/World/Scene01/...` 아래 계층화. 밴드 포장은 **밴드별 별도 박스**(재질 분리)로.
- 랜덤화 로직 금지(파라미터 구조만). Replicator/GT 라벨링 착수 금지. 구버전 `omni.isaac.core` 금지.
- 주석 한국어 간단히.

## 8. 검수 기준 (Fable이 렌더로 직접 판정)

1. beauty_overview가 참고 사진의 "새로 조성된 캠퍼스 광장" 인상으로 읽힘 (포장 줄무늬·화단·건물·앰피시어터 식별).
2. h0.3·d5~10 프리셋에서 계단 디딤면 완전 소실(grazing 은닉), h1.8·d2에선 명확히 보임.
3. cue 전부 ON vs 전부 OFF에서 계단·광장 프림 트랜스폼 동일 (스테이지 덤프 diff로 확인).
4. 타일 반복 무늬·텍스처 늘어남·Z-파이팅·앨리어싱 없음.
5. §2 실행 시퀀스 한 번에 GUI 로드.
