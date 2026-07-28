# Practice_NegObs — Isaac Sim 합성 씬 라이브러리

RGB 맥락단서 기반 **비가시 낙차(negative obstacle)** 추정 연구의 합성 데이터 기반.
계단·단차가 관측 시점에서 보이지 않을 때, 주변 맥락(난간·점자블록·그림자·스케일 앵커 등)으로
낙차를 추정하는 문제를 위한 씬 라이브러리다.

- 스택: Isaac Sim 4.5.0 / Kit 106.5, conda env `env_isaaclab`, RTX RayTracedLighting(반복) + PathTracing(판정)
- 규모: **33씬** — 본편 21씬 + 나노바나나 배치1 12씬 (전 씬 판정 합격)
- 연구 본체: `../Project_NegObs` · 지형 룩데브: `../Practice_TerrainGen`(07-27 분리)

## 씬 라이브러리

### 본편 21씬 — `scenes/main/`
한국 일상 공간 × 계단 형태 변형 × 규정 미달의 위험. 명소가 아닌 **로봇·보행자가 실제 다니는 무대**로 설계(v5).

| | 씬 | | 씬 |
|---|---|---|---|
| 01 | 캠퍼스 광장 하행계단 | 12 | 수변 데크길 |
| 02 | 지하도 | 13 | 아파트 지하주차 진입부 |
| 03 | 하천 제방 | 14 | 대계단 착시 |
| 04 | 공원 산책로 | 15 | 골목 미로 |
| 05 | 야외 공연장 | 16 | 캐노피 그림자 |
| 06 | 보행육교 나선 | 17 | 한강 제방 램프쌍 |
| 07 | 산사 돌계단 | 18 | 바닷가 벽화계단 |
| 08 | 선큰 광장 | 19 | 부채꼴 winder |
| 09 | 호수공원 수변 | 20 | 사선 경사 |
| 10 | 공원 데크 갈지자 | 21 | 기념비 자기차폐 |
| 11 | 보도육교 | | |

### 배치1 12씬 — `scenes/batch1/`
학습 편향 차단용 대조군. Gemini(나노바나나) 레퍼런스 → 코드 번역 워크플로로 제작.

- **hard negative 5** (`N1`~`N5`, GT = 낙차 없음): 그림자 띠 · 아스팔트 패치 · 트롱프뢰유 · 내림 램프 · 평면 그레이팅
- **조건 변주 3** (`C1`·`C2`·`C4`): 눈 · 낙엽 · 젖음
- **비계단 낙차 4** (`D1`~`D4`): 하역장 · 바닥 개구부 · 측구 · 승강장

`scenes/archive_v3/` 는 v5 재설계로 교체된 구 씬 7종(이력 보존).

## 구조

```
scene_common.py                 공용 라이브러리 — 부팅·TEX 레지스트리·PBR·기하 빌더·조명·캡처 하네스
scenes/main/                    본편 21씬   (+ scene_common.py·assets·look_check 심링크)
scenes/batch1/                  배치1 12씬 (+ batch1_common.py)
scenes/archive_v3/              v5에서 교체된 구 씬
assets/                         텍스처·HDRI·MDL — 바이너리는 미추적, 다운로드 스크립트로 재현
assets/signs/                   표지판 텍스처 + 생성기 gen_signs.py
look_check/sceneNN/<round>/     렌더 산출물 (미추적, ~11GB)
look_refs/                      나노바나나 레퍼런스 이미지·프롬프트
scripts/                        완료된 렌더 체인 스크립트 보관 + 컨택트 시트 생성기
run_*.sh (루트)                 진행/대기 중 렌더 체인 — 종료 후 scripts/로 이동
Docs/                           문서 → Docs/INDEX.md
```

씬 폴더의 `scene_common.py`·`assets`·`look_check` 는 루트를 가리키는 심링크다
(씬을 옮겨도 import 경로 수정이 0이 되는 패턴).

## 셋업

```bash
unset PYTHONPATH VIRTUAL_ENV && conda activate env_isaaclab && export PYTHONNOUSERSITE=1

# 에셋 내려받기 (~800MB, 재실행 가능 — 이미 있으면 skip)
python assets/download_assets.py                  # qwantani HDRI + 룩데브 v1 텍스처
python assets/scene01/download_scene01_assets.py  # 본편/배치1 전 텍스처 + overcast HDRI + 점자블록
```

HDRI 파생본(`*_lookfix.exr`, 태양 캡 + 지평 헤이즈 리프트)은 `scene_common.ensure_noon_lookfix`
가 첫 실행 시 자동 생성·캐시한다. 전 에셋 CC0 (PolyHaven / ambientCG).

## 실행

```bash
python scenes/main/scene01_campus_stairs.py                 # GUI 룩체크
NEGOBS_SMOKE=1 python scenes/main/scene01_campus_stairs.py  # 부팅+조립 자기검증(조기종료)

NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=rt \
NEGOBS_CAPTURE_DIR=look_check/scene01/myrun \
  python scenes/main/scene01_campus_stairs.py               # 오프스크린 캡처 (rt|pt)
```

- **렌더 체인은 반드시 `cd` 를 포함한 스크립트 파일로 실행** (`bash /abs/path.sh`) — 백그라운드 셸의
  cwd 리셋 함정. 렌더 병렬 실행 금지(GPU 1대).
- 씬 규약: `SCENE_CONFIG` 7키(단서 토글 — **위험 기하는 불변**) + `NEGOBS_PARAMS_OVERRIDE` /
  `NEGOBS_SCENE_CONFIG` env 오버라이드.
- 판정 시점 우선순위: `grid_views` 의 **h0.3 로봇 시점**이 1순위.
- 초기 씬(01~04)은 `NEGOBS_SMOKE` 미지원 → 배치 스크립트에서 조건부 생략.
- 그 외 env: `NEGOBS_VIEWS`(캡처 뷰 선택) · `NEGOBS_WARMUP`(PT 수렴 프레임 수, D4는 900) ·
  `NEGOBS_GEOCHECK` / `NEGOBS_SELFCHECK`(기하·보행 연속성 검산).
- 회귀 방지 체크리스트: `Docs/briefs/multi_scene_brief_v3.md` §A.

## 현 상태 (2026-07-28)

**전 33씬 최종 렌더·판정 종료.** 본편 21/21 합격(v6→v7→v8 사이클), 배치1 12/12 합격.
grazing 은닉 회귀 0, 클리핑 0. 21씬 컨택트 시트 = `Docs/audit_v4/library21_final_hq.png`
(생성기 `scripts/make_hq_sheet.py` — 재렌더 후 재실행으로 갱신).

진행 중 과제는 **사실성 격차**다. 6팀 병렬 조사 결과 현 라이브러리는 실사성 L1(그레이박스)로,
SYNTHIA(L2)·GTA5(L3) 아래로 판정됐다. 핵심 원인은 렌더러가 아니라 표면 미세구조의 전면 부재이며,
가장 큰 리스크는 미학이 아니라 **지름길 학습**(카메라 9개 이산조합·조명조건 1종·사람/차량 0건)이다.
전 보고서와 실행계획: `Docs/surveys/realism_gap_2026-07-28/` — `ZZ_synthesis.md` 부터 읽을 것.

## 문서

`Docs/INDEX.md` 참조. 새로 합류하는 경우 읽는 순서:

1. `Docs/audit_v4/user_feedback_v5_1.md` — 현실성 규약(전역 §1~5 + v5.2 원칙 §6~9). **필독 1순위**
2. `Docs/briefs/multi_scene_brief_v5.md` — 본편 구현 사양
3. `Docs/surveys/realism_gap_2026-07-28/ZZ_synthesis.md` — 사실성 격차 종합·실행계획
