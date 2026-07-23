# NegObs 룩 체크 v1 — Phase A 완료 보고 (2026-07-23)

지시서 §8 형식. **Phase A 완료 — 사용자 GUI 육안 확인 대기 중. Phase B는 승인 전 미착수.**

## 실행 명령 (③)

```bash
unset PYTHONPATH VIRTUAL_ENV
conda activate env_isaaclab
export PYTHONNOUSERSITE=1
cd ~/Desktop/work_sy/Practice_NegObs
python negobs_look_check_v1.py
```

키: `P` 패스트레이싱 토글 · `S` 캡처(look_check/) · `L` noon↔dawn · `[` `]` 태양 방위 ±15° · 우클릭+WASD 비행.

## 실제 확인된 API 경로 목록 (①) — 전부 설치본(env_isaaclab, isaacsim 4.5.0.0) 실측

| 용도 | 확인된 API |
|---|---|
| 부팅 | `from isaacsim import SimulationApp` (v9 검증 블록: 1920×1080, DLSS execMode 2) |
| 재질 MDL | OmniPBR 입력명: `diffuse_texture` / `normalmap_texture` / `reflectionroughness_texture`(언더스코어 없음) / `reflection_roughness_texture_influence`(기본 0 — 텍스처 쓰려면 >0) / `reflection_roughness_constant` / `project_uvw` / `world_or_object` / `texture_scale`(=반복 횟수, 실세계 T[m] ≈ 1/T) / `texture_rotate`(deg) / `bump_factor` / `flip_tangent_v`(기본 true=DirectX, PolyHaven `_nor_dx`와 정합) |
| roughness 곱 | OmniPBR은 `rough = lerp(constant, tex, influence)` → constant=0, influence=m 으로 §4.4의 "0.6~0.8배 곱" 구현 |
| 셰이더 바인딩 | `UsdShade.Shader.SetSourceAsset(...,'mdl')` + `SetSourceAssetSubIdentifier` + `material.CreateOutput('mdl:surface').ConnectToSource` + `UsdShade.MaterialBindingAPI.Apply(prim).Bind` |
| 면 분류 | `UsdGeom.Subset.CreateGeomSubset(mesh, name, UsdGeom.Tokens.face, Vt.IntArray, UsdShade.Tokens.materialBind)` |
| 조명 | `UsdLux.DomeLight.Define` + `CreateTextureFileAttr`(inputs:texture:file) + `CreateTextureFormatAttr('latlong')` + `AddRotateZOp`(deg, Z-up에서 태양 방위) |
| 캡처 | `omni.kit.viewport.utility.get_active_viewport` / `capture_viewport_to_file` — **비동기**: 파일 크기 안정화까지 `app.update()` 필요 |
| 렌더 설정 | `/rtx/rendermode`('RaytracedLighting'↔'PathTracing'), `/rtx/pathtracing/spp`=1, `/rtx/pathtracing/totalSpp`=512, `/rtx/post/aa/op`=3, `/rtx/post/dlss/execMode`=2 |
| 키 입력 | `carb.input` 구독(v9 패턴), `KeyboardInput.P/S/L/LEFT_BRACKET/RIGHT_BRACKET` 존재 확인 |
| 단위 | `UsdGeom.GetStageMetersPerUnit` == 1.0 확인 후 진행 |

## 에셋 다운로드 결과 (②)

11/11 성공 (`assets/download_assets.py`, 재실행 시 스킵·재시도 3회·크기 검증):
- 텍스처 4K jpg 9장: `aerial_grass_rock`, `brown_mud_dry`, `brown_mud_03` × (diff / nor_dx / rough) — 전부 4096², PIL 검증 통과
- HDRI 4K exr 2장: `qwantani_noon_puresky`, `qwantani_dawn_puresky` (4096×2048, OpenEXR v2)
- 함정: PolyHaven이 기본 python urllib User-Agent를 403 차단 → 스크립트에 UA 헤더 포함
- API 구조: 텍스처 `d['Diffuse'|'nor_dx'|'Rough']['4k']['jpg']['url']`, HDRI `d['hdri']['4k']['exr']['url']`
- **추가 산출**: `assets/NegObsGround.mdl` — 검증 루프에서 OmniPBR 박스 투영의 경사 늘어남·면 단위 경계 톱니를 해결하기 위해 작성된 OmniPBR 호환 커스텀 트라이플래너 재질(노멀 가중 3면 투영 + 경계 크로스페이드 + 반복 파괴 디더)

## 멀티에이전트 검증 요약

워크플로우 3개, 에이전트 총 52개, 판정-수정 루프 누적 8라운드 + A/B 튜닝 3계열.
- 코드리뷰(3중: API 정합·지시서 준수·기하 수학): critical/major 0건 통과
- 실사성 루프: 전담 판정관(형태/재질/조명)이 루브릭(`Docs/realism_rubric_v1.md`)으로 채점 → 수정 → 재렌더 반복
- A/B: 타일 스케일·노출은 기본값 승, `bottom_rough_mult=0.8` 반영
- **최종 종합 판정(512spp, look_check/auto/final_v1/): 합격, 평균 4.08/5.** §7 체크리스트 6항목 중 5항목 합, "근접 0.3m"만 조건부(아래 한계 참조). 강점: 형태 비균일성(사행·붕괴 2곳·압출 티 없음), dawn 사광 품질(5점), 재질 전이·습윤 표현.

## 알려진 한계·타협점 (④)

**Phase A 구조적 한계 (파라미터로 개선 불가, Phase B에서 해소 예상)**
1. 초지가 텍스처 전용 → 근접·저고도에서 풀잎 입체·시차 없음 ("근접 0.3m" 조건부의 주원인) → Phase B 풀 클럼프로 해소
2. 립 실루엣에 드리운 풀·뿌리 없음 → 근경 실루엣이 다소 깔끔 → Phase B
3. 바닥 3D 잔돌·물 없음 → 최심부가 어두운 텍스처 덩어리로 읽히는 구간 존재 → Phase B
4. HDRI 자산 한계: overview 방위 수평선 대역이 구름 없는 회백 헤이즈(+미세 밴딩) — 조명 파라미터로 개선 불가, 필요 시 HDRI 교체
5. 극단적 grazing 각(closeup 모서리)에서 국소 텍스처 스미어 잔존 — 커스텀 MDL로 대부분 해소했으나 완전 제거는 UV 언랩 필요

**구현 타협점**
6. §4.2 "에셋 부재 시 안내 후 대기" → 목록 출력 후 종료(exit 1)로 구현 (재실행 유도 방식)
7. §8 PARAMS 스켈레톤 보존을 위해 파생 상수는 별도 `DERIVED` dict (값은 전부 사양 범위 내, 코드 상단 위치)
8. dawn HDRI의 태양 에너지가 약해 §5 허용 조항대로 dawn 프리셋에만 보조 DistantLight(0.53°, 난색) 추가
9. `NEGOBS_CAPTURE=1` headless 자동 캡처 모드 추가(검증 파이프라인용) — GUI 기본 동작 불변

## 참고 자료
- 최종 캡처 17장: `look_check/auto/final_v1/` (pt noon 10 · pt dawn 4 · rt 3)
- 라운드별 이력: `look_check/auto/r1~r4, deep_r1~r3, ab_*`
- 지형 계측: `terrain_dev/selftest.py` → `metrics.json` + preview 5종 (본 파일 [B] 섹션을 직접 계측)
