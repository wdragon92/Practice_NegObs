# Practice_NegObs — Isaac Sim 합성 씬 라이브러리

RGB 맥락단서 기반 **비가시 낙차(negative obstacle)** 추정 연구의 합성 데이터 기반.
계단·단차가 관측 시점에서 보이지 않을 때, 주변 맥락(난간·점자블록·그림자·스케일 앵커 등)으로
낙차를 추정하는 문제를 위한 씬 라이브러리다.

- 스택: Isaac Sim 4.5.0 / Kit 106.5, conda env `env_isaaclab`, RTX RayTracedLighting(반복) + PathTracing(판정)
- 규모: **33씬** — 본편 21씬 + 나노바나나 배치1 12씬 (전 씬 판정 합격)
- 연구 본체: `../Project_NegObs` · 지형 룩데브: `../Practice_TerrainGen`(07-27 분리)

## 어디서부터 보나

| 알고 싶은 것 | 볼 곳 |
|---|---|
| **지금 어디까지 됐고 다음에 뭘 하나** | **`Docs/campaign/status/PROJECT_STATE.md`** — 하나뿐인 현황 문서(날짜 없는 파일, 맨 위에 최종 갱신일) |
| 이 연구가 뭘 하는 건지 쉬운 말로 | `Docs/campaign/NEGOBS_STUDY_0823.md` |
| 렌더한 데이터가 어디 있나 | `dataset/README.md` (라운드를 이름으로 찾는 법 포함) |
| 실험 사이클이 몇 개고 각각 뭐였나 | `experiments/README.md` |
| 씬 룩체크 렌더가 어디 있나 | `look_check/INDEX.md` (**생성물** — 고치지 말고 `python3 scripts/make_lookcheck_index.py` 로 다시 만든다) |
| 논문/제출 묶음 | `submission_0830/INDEX.md` |
| 문서 전체 지도 | `Docs/INDEX.md` |
| 2026-08-27 정리에서 뭐가 어디로 갔나 | `REORG_0827.md` |

## 최상위 폴더 한 줄 설명

| 폴더 | 크기 | 무엇 |
|---|---:|---|
| `scenes/` | 5 MB | 33개 Isaac 씬 코드. `main/` 21씬 · `batch1/` 12씬 · `archive_v3/` 구 씬 · `probe/` 프로브 씬 |
| `*_kit.py` + `scene_common.py` (루트 9개 파일) | 1.1 MB | 씬이 쓰는 공용 라이브러리. **루트 고정** — 씬 폴더의 심링크 34개가 이 위치를 가리킨다 |
| `assets/` | 4.1 GB | 텍스처·HDRI·MDL. 바이너리는 미추적이고 `assets/download_*.py` 로 다시 받는다 |
| `look_refs/` | 16 MB | 배치1 레퍼런스 이미지·프롬프트 |
| `look_check/` | 32 GB | 씬 룩체크 렌더(미추적). 현역 라운드는 `<scene>/<round>/`, 역할 끝난 것은 `_archive/<wave>/` |
| `dataset/` | 99 GB | 학습·평가용 렌더(미추적). 목적별 9칸 + `_archive/` — 라운드 이름은 그대로다 |
| `experiments/` | 7.2 GB | 실험 사이클 7개(mainrun_0819 … gazebo_wh_0824). 폴더 이름 불변 |
| `Docs/` | 351 MB | 문서. `campaign/`(지시서·현황) · `briefs/` · `surveys/` · `reports/` · `audit_v4/` · `archive/` |
| `scripts/` | 1.3 MB | 측정·검증 도구 + `rounds/`(완료된 렌더 드라이버 보관) + `lib/`·`reorg/`·`tests/` |
| `submission_0830/` | 6.3 MB | 08-30 제출 묶음 (INDEX + fragments + panels + tables) |

---

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
look_check/sceneNN/<round>/     현역 룩체크 렌더 (미추적, 32GB — _experiments 3.1GB 포함)
look_check/_archive/<wave>/     역할이 끝난 라운드 (08-27 이동, 목록은 look_check/INDEX.md §3)
look_refs/                      나노바나나 레퍼런스 이미지·프롬프트
scripts/                        측정·검증 도구 + 시트 생성기
scripts/lib/ scripts/tests/     셸 경로 헬퍼 · 헬퍼 테스트
scripts/rounds/                 완료된 렌더 드라이버 보관 (일회성 체인은 종료 후 여기로)
scripts/rounds/run_p2_all33.sh  상설 렌더 드라이버 — 라운드 태그를 인자로 받는다
                                (08-27에 루트에서 여기로 이동. 내용은 한 줄도 안 바뀌어
                                 문서의 줄 번호 인용 `:36` 등은 그대로 유효하다)
dataset/<group>/<round>/        학습·평가 렌더 (미추적, 99GB — 목적별 9칸, dataset/README.md)
experiments/<cycle>/            실험 사이클 (experiments/README.md)
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

## 현 상태

**→ `Docs/campaign/status/PROJECT_STATE.md` 를 먼저 읽으십시오.** 캠페인 전체가 지금 어디에
멈춰 있고 다음에 뭘 하는지가 그 한 문서에 있습니다(날짜 없는 파일 하나, 맨 위에 최종 갱신일).
씬 라이브러리만의 상태판은 `Docs/STATUS.md` 입니다.

- 씬 라이브러리 **33씬** 전부 판정 합격 상태(v5 라운드).
  21씬 컨택트 시트 = `Docs/audit_v4/library21_final_hq.png`
- **사실화 v1 라운드 진행 중** — 6팀 격차 조사에서 실사성 **L1(그레이박스)** 판정을 받은 것에 대한 대응.
  룩 레이어(재질·표면 미세구조)를 `scene_common.py`/MDL/에셋 계층에만 넣어 **씬 파일 무수정**으로 끌어올린다.
  - 켜기: `NEGOBS_LOOK_V1=1` (기본 OFF) · PT 가속: `NEGOBS_PT_FAST=1`
  - 총괄 보고: **`Docs/reports/realism_v1_final.md`**
- 가장 큰 리스크는 미학이 아니라 **지름길 학습**(카메라 9개 이산조합·조명조건 1종·사람/차량 0건)이며,
  이는 다음 지시서 범위다.

## 문서

읽는 순서 (씬 라이브러리 쪽):

1. **`Docs/STATUS.md`** — 씬 라이브러리 상태판 (20줄)
2. **`Docs/reports/realism_v1_final.md`** — 사실화 v1 총괄. 인수인계 1순위
3. `Docs/briefs/realism_brief_v1.md` — 지시서 + **개정 이력 rev.1**(충돌 시 rev.1 우선)
4. `Docs/audit_v4/user_feedback_v5_1.md` — 현실성 규약(계속 유효)
5. `Docs/INDEX.md` — 전체 문서 지도

⚠ `Docs/surveys/realism_gap_2026-07-28/ZZ_synthesis.md` 는 격차 조사 **원안**이며
서술 다수가 이후 정정됐습니다. `realism_v1_final.md` §3(정정 목록)을 먼저 보십시오.

---

## 실험 캠페인 (2026-08-19 ~ 08-26)

씬 라이브러리 위에서 본실험이 **7사이클** 돌았습니다(`experiments/README.md` 가 사이클 지도).
**새로 합류하는 독자(사람/AI)의 판독 순서**:

1. **`Docs/campaign/status/PROJECT_STATE.md`** — 지금 상태·멈춘 자리 (필독 1순위)
2. `Docs/campaign/NEGOBS_STUDY_0823.md` — 이 연구가 뭘 하는지 쉬운 말로
3. `experiments/v3_0823/MORNING_REPORT_V3.md` → `VERDICT_V3.md` — 최신 캠페인 최종 보고와 판정
4. `experiments/mainrun_0819/DECISIONS.md` — 자율 판단 전체 원장 (D1~D104, 사이클이 바뀌어도 한 파일)
5. `Docs/campaign/` — 사이클별 지시서 (설계 의도의 정본)

렌더 산출물(`dataset/` 99GB, `look_check/` 33GB)과 재생성 가능 대용량은 gitignore로 제외돼 있습니다.
데이터를 라운드 **이름**으로 찾는 법은 `dataset/README.md`, 08-27 정리 내역은 `REORG_0827.md`.
