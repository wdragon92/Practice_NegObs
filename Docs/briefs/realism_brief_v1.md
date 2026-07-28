# 사실화 브리프 v1 — 기존 33씬 룩 업그레이드

- 작성: 2026-07-28 claude.ai 설계 세션(승용 검토) → **수행: Claude Code (Opus 5)**
- 배치: `Docs/briefs/realism_brief_v1.md` (INDEX.md에 등록)
- 목표 한 줄: **씬을 늘리지 않는다.** 기존 33씬(본편 21 + 배치1 12)의 표면·재질·식생을 실사 수준으로 끌어올리고, 개선을 수치로 증명한다.
- 이 지시서 다음 일(별도 논의·지시서): 씬 패밀리 확장(유형 조사부터), 점자블록 정책, 사람·차량, 카메라·조명 다변화, GT, 대량 생산. 여기서는 다루지 않는다.
- 필독: ① `Docs/audit_v4/user_feedback_v5_1.md`(현실성 규약 — 계속 유효) ② `Docs/surveys/realism_gap_2026-07-28/ZZ_synthesis.md`(모든 수치·근거의 출처. 세부는 팀 원보고서 00·A~G 직접 참조)
- 참고: `Docs/briefs/multi_scene_brief_v5.md`(공통 레이어 구조), `multi_scene_brief_v3.md` §A(회귀 체크리스트), README(환경·실행 규약 — conda 시퀀스, `NEGOBS_*` env, 렌더 체인은 `cd` 포함 스크립트, 렌더 병렬 금지)

## 원칙 (이 4줄이 전부)

1. **현실 재현이 판단 기준** [승용]: 선택지가 생기면 "한국 보행 환경에서 실제로 흔한 쪽"을 고르고 근거를 보고에 남긴다. 근거가 약하면 [추정] 표기하고 진행 — 멈추지 않는다.
2. **무료만** [승용]: CC0 / MIT-0 / CC-BY(크레딧 기록)만 사용. NoAI·NC 계열(Quixel/Fab, Mixamo, RenderPeople 등)은 라이선스상 불가. 사용 에셋은 `Docs/CREDITS.md`에 기록하고, 재배포 불가 에셋(NVIDIA S3 등)은 .gitignore + 다운로드 스크립트로 재현 가능하게.
3. **불변 3종**: 씬 파일 33개 · 카메라 프리셋(`grid_views`) · 위험 기하(GT 낙차). 모든 수정은 `scene_common.py` / MDL / 에셋 계층에서만 한다. 씬 파일을 고쳐야만 풀리는 문제를 만나면 그건 설계 신호이므로 보고.
4. **렌더 이원화**: 반복 확인 = RT, 판정·게이트 = PT 수정 설정(Phase 1-6에서 확정).

## Phase 0 — 기준선 만들기 (0.5일)

1. 브랜치 `feat/realism-v1`, 시작 태그 `pre-realism-v1`.
2. **측정 도구 확보**: `scratchpad/imgstats.py`는 저장소 미추적. 없으면 `scripts/imgstats.py`로 재구현 — 지표 3종(무디테일 픽셀 비율 flat%, 스펙트럼 기울기 slope, 평균 채도 sat), 정의는 `00_supervisor_direct_diagnosis.md`·`E_realism_measurement_protocol.md` 기준, numpy+PIL만.
3. **기준선 기록**: 대표 3씬(scene01 캠퍼스 / scene07 석재 / sceneD3 측구) × 기존 프리셋을 PT 수정 설정으로 렌더 → 수치를 `Docs/reports/realism_baseline.md`에 기록. 이후 모든 개선폭은 이 수치 대비로 말한다.

## Phase 1 — 검증의 날 (1일)

목적: Phase 2에서 쓸 재료가 **이 환경(Isaac 4.5.0 / RTX)에서 실제로 작동하는지** 하루에 전부 확인. 실험별 산출 = A/B 이미지 + 수치, 위치 `look_check/spike_<이름>/`.

| # | 실험 | 방법 | 통과 기준 |
|---|---|---|---|
| 1 | 가짜 베벨 `round_edges_radius` | 단독 스테이지, 콘크리트 박스, radius 0/2/5/10 mm 스윕, PT 각 1장 | 모서리 하이라이트 라인 발생, 검은 테두리·노이즈 없음 |
| 2 | `NegObsGround.mdl` 1씬 바인딩 | 실험 사본에서 scene03 또는 04 지면에 바인딩 (`../Practice_TerrainGen` 사용례 참조) | flat%·slope가 기준선 대비 개선 |
| 3 | 나무 에셋 임포트 | S3 벚나무 포함 2종 개별 다운로드 → 빈 스테이지 로드 | `opacityThreshold` 설정 전/후 비교 — 잎 알파 컷아웃 정상 (기본 0.0 함정 [ZZ §10.2]) |
| 4 | subdiv `catmullClark`+crease | 박스 1개 | RTX 뷰포트·캡처에 반영 |
| 5 | 정점 변위 지면 | 그리드 메시 유틸, 진폭 5~20 mm | PT에서 미세 기복 확인 (MDL displacement는 RTX 미지원 — 정점 방식만) |
| 6 | **PT 수정 설정 실측** | `capture_pipeline` 워밍업 구조 파악 → `spp=16, totalSpp=64, rt_subframes=8` 적용 [ZZ §10.3] → 3씬 s/컷 | 기존 대비 s/컷 + 화질 육안 동등(A/B) |
| 7 | RT 워밍업 32 실측 | 3씬 s/컷 | 수치 기록 |

보고: 결과 종합 표 + **렌더 예산표**(2만 장 가정, PT수정/RT32 각각 총시간 환산). 실패한 실험은 Phase 2 해당 항목의 대체안을 함께 제시(예: 베벨 실패 → 경량 베벨 메시 유틸 / 나무 실패 → 기존 build_tree v2 + 잎 노멀 트랜스퍼).

## Phase 2 — 룩 레이어 (2~3일)

전부 `scene_common.py` / MDL / 에셋 계층 작업. 우선순위: **필수 = 1, 2, 7, 8, 10** / 권장 = 3, 4, 5, 6, 9 (타임박스 초과 시 권장 항목은 미완으로 보고하고 게이트로).

1. **`NegObsGround.mdl` 지면 전면 이식** — 소프트 트라이플래너로 경사면 이음매 해결 [ZZ §10.5]. 지면 계열 role에 연결.
2. **가짜 베벨 전 모서리** — `make_pbr` 인자화. 기본 radius [클로드 기본값, 스윕으로 확정]: 콘크리트 3 / 석재 5 / 금속 1.5 mm.
3. `detail_normalmap_texture` + `detail_bump_factor` — 근접뷰 텍셀 뭉개짐 개선.
4. 헥스 타일링 MDL(~40줄) — 대면적 role만, 타일 반복 파괴.
5. 접지 AO·오염 링 — 월드 Z 그라디언트 (v5.1 §4 "기단 오염 밴드"의 전면화).
6. 웨더링 마스크(~30줄) — 상향면 먼지(normal.z>0.6), 스플래시존 0.3~0.5 m, 하향 줄무늬.
7. **상수색 재질 전수 교체** — TEX 레지스트리 감사로 상수색 role 목록화 → CC0 텍스처 매핑(`assets/download_assets.py` 확장). flat% 직격 항목.
8. **나무 교체** — `build_tree` 내부 구현을 S3 식생 에셋 인스턴싱으로 (함수 시그니처 불변 → 씬 무수정). 수종은 한국 빈도 순(벚·단풍·소나무 — S3 보유), 은행·느티는 S3에 없음 → CC0 대체 5분 탐색, 없으면 유사 활엽 폴백 후 보고. 클러스터·비정형 배치 규약(v5.1 §1·§3)은 그대로.
9. 채도 캘리브레이션 — 전역 0.298 → 0.15~0.22.
10. **창 리세스 버그 수정** — `build_building`의 `window["inset"]` 정의만 되고 미반영. 수정 후 영향 씬(약 10개) 육안 확인.

**게이트**: 대표 3씬(01/07/D3) PT 렌더 → **flat < 8% · slope −2.0~−2.2 · sat 0.15~0.22** [ZZ T1 목표]를 기준선 대비 표로 보고 → 승용 승인 → 전 33씬 재렌더 체인(`run_*.sh`, 종료 후 `scripts/`로 이동) → 회귀 확인(brief v3 §A: grazing 은닉·클리핑) → 컨택트 시트 갱신(`scripts/make_hq_sheet.py`).

## 보고 (각 Phase 끝)

실행 명령 / 변경 파라미터 표(기본→변경+사유) / A-B 이미지 경로 / 수치(기준선 대비) / 게이트 판정 / 막힌 것·리포트와 다른 실측 / 제안(스펙 외 아이디어는 여기에만) / 다음 Phase 착수 승인 요청. Phase 간 승인은 승용이 한다.

---
*시작 프롬프트 예시: "`Docs/briefs/realism_brief_v1.md`를 읽고, 필독 2종 확인 후 Phase 0부터 진행해줘."*
