# PATHS.md — 경로 자동 탐지 결과 (2026-08-19 밤, brief §0)

## 확정 경로
| 항목 | 경로 | 근거 |
|---|---|---|
| REPO_ROOT | `/home/vislab/Desktop/work_sy/Practice_NegObs` | .git 존재, 씬 파이프라인(scenes/, scene_common.py, scripts/run_data_render.py), branch `feat/realism-v1`, HEAD `8c814db` |
| CAMPAIGN_DIR | `/home/vislab/Desktop/work_sy/Practice_Segmentation/campaign` | REPORT.md + analysis/*.md 7편 동반 |
| 훈련 하네스 | `CAMPAIGN_DIR/harness/` | runner.py, run_experiment.py, common.py, reporting.py — 캠페인이 실제 사용한 모델 정의·학습 스크립트 |
| WORKDIR | `REPO_ROOT/experiments/mainrun_0819/` | 신규 생성 |
| 부트스트랩 코드 후보 | `/home/vislab/Desktop/work_sy/ExProject_SR_HPE` | 8/14 논문(Joint SR-HPE) 리포 — 에이전트 탐지 중 |

## DATA_CANDIDATES 후보 전수 (dataset/ + look_check/)
| 후보 | 내용 | 판정 |
|---|---|---|
| `dataset/_archive/pilots/260816_dataall` | **비어 있음** (4KB) — 커밋 36037ea "dataall 미렌더 정정", 8c814db 큐에 "dataall 재렌더" | 사용 불가 |
| `dataset/_archive/pilots/260815_datapilot` | 5씬(s04,s16,N1,N2,N3) × L0/L2/L7 × 8캠 = 120컷, **RGB만**(depth/GT 없음), variation.json에 컷별 카메라 포즈 완비 | 파일럿 — 형식 참조용 |
| `dataset/_archive/pilots/260815_datapilot_aug` | datapilot의 sensor_augment 파생 | 참조용 |
| `dataset/_archive/scene_dev_2607/2607xx_*` (11개) | 07-30/31 구세대 미니 라운드 — W4~W6 수리 이전 룩 | 스테일, 사용 안 함 |
| `look_check/…260816_w4_final33_on` | 33씬 132컷 판정(judge) 라운드 — 검증용 4컷/씬 | 학습용 아님 (검증 룩 기준) |

## 선택과 근거
**사용 가능한 전체 학습 데이터셋이 존재하지 않음** → 금야 신규 렌더 필요.
사용자 구두 지시(08-19 밤): "컷들도 너가 적당한 위치에서 잡아도 되고" — 컷 배치 자율 승인.
렌더 드라이버: `scripts/run_data_render.py` (scene × cond × random cam, ~2.8–6.3 s/cut 실측 260815).
결정 상세는 `DECISIONS.md`.
