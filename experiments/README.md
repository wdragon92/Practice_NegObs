# experiments/ — 한 폴더 = 한 실험 사이클

날짜 순으로 쌓인 캠페인 기록이다. **폴더 이름은 절대 바꾸지 않는다** — 저장소 곳곳의
보고서가 이 경로를 재현 증거로 인용한다. 사이클 안의 모양은 늘 같다: `STATUS.md`(진행 로그) ·
`code/`(스크립트) · `logs/`(저널) · `runs/`(학습 산출) · `annotations/`(라벨) ·
`render_configs/`(렌더 입력), 그리고 사이클 루트의 대문자 `.md` 가 그 사이클의 보고서다.

| 사이클 | 날짜 | 무엇을 했나 | 여기부터 | 크기 |
|---|---|---|---|---:|
| `mainrun_0819/` | 08-19 → 08-20 | 33씬 라이브러리를 처음으로 전부 렌더하고 학습까지 돌린 1차 사이클. 카메라 규약·하네스·첫 split 이 여기서 정해졌다 | `STATUS.md` → `MORNING_REPORT.md` → `RESULTS_DRAFT.md`; 무엇이 어디 있는지는 `PATHS.md`, 결정 원장은 **`DECISIONS.md`** | 795 MB |
| `dayrun_0820/` | 08-20 → 08-23 | P1~P4: 라벨 재작성, 불변성 게이트, 진단 3종, boost 렌더, YOLO 검출 트랙. 디스크로 가장 큰 사이클 | `STATUS.md` → `DAYRUN_REPORT.md`; 게이트 `GATES_REPORT_v1grid.md`·`v2full.md`, split `SPLIT_PROPOSAL_v2*.md`, 검출 트랙은 `code/yolo/README_YOLO.md` 한 편으로 끝난다 | 2.1 GB |
| `nightrun_0820/` | 08-20 → 08-21 | GPU 없이 돌린 야간 분석 레인 — straddle(경계 걸침) 분석, 트윈 층화, τ 곡선. 렌더 없음 | `STATUS.md` → `MORNING_REPORT_0821.md`, `STRADDLE_REPORT.md`, `TWIN_STRATIFICATION.md` | 4.9 MB |
| `probe_holes_0820/` | 08-20 | 구멍 유형 zero-shot 프로브. **준비만 하고 실행하지 않았다** — 평가 전용이라 이 프레임은 학습에 넣지 않는다 | `README.md` → `PROBE_TABLE.md`, `TIER_TABLE.md` | 34 MB |
| `weekend_0823/` | 08-23 | V2S 재실행, 새 모델 계열, CUE-OFF(단서 제거) 개입, 광학·시점 감사, Gazebo 교차검증 | `STATUS.md` → `MORNING_REPORT_0823.md`; 하위 트랙 `cue_audit/`(PREREG_CUEOFF.md → CUEOFF_RESULT_v2.md) · `v2s/` · `newmodels/` · `gazebo/GAZEBO_TRACK.md` · `fusion/` · `rt_response/` · `redteam/` | 3.3 GB |
| `v3_0823/` | 08-23 → 08-26 | v3 본실험 창 — 사전등록 동결, 코퍼스 v3, W0~W3 라이브러리 파도, v3-A 학습, 판정. **본실험의 현재 창** | `STATUS.md` → `PREREG_V3.md` → `MORNING_REPORT_V3.md` → `VERDICT_V3.md`; 라운드 이름↔실제 렌더 날짜 대조는 `ROUND_LEDGER.md` | 1.0 GB |
| `gazebo_wh_0824/` | 08-24 | Gazebo 창고 월드 변형 실험(`weekend_0823/gazebo/` 후속). **마감(08-27, D102)** — readout 에 '우리 모델' 열 12개 완성, 결론 보고서 `WAREHOUSE_VARIANT.md` | `make_wh_worlds.py` · `capture_run.sh` · `infer_ours.sh`; 남은 일은 `Docs/campaign/status/PROJECT_STATE.md` §1 | 25 MB |

처음 오는 사람의 순서: `Docs/campaign/status/PROJECT_STATE.md`(지금 어디까지 됐나) →
`Docs/campaign/NEGOBS_STUDY_0823.md`(개념을 쉬운 말로) → `mainrun_0819/PATHS.md`(무엇이 어디 있나)
→ `v3_0823/PREREG_V3.md`(지금 무엇을 검증 중인가).

## 규약

- **`DECISIONS.md` 가 결정 원장이다** — `mainrun_0819/DECISIONS.md` 한 파일에 D1부터 이어 적는다.
  사이클이 바뀌어도 원장은 옮기지 않는다.
- `runs/**/*.pt`, `*.png`, `events.out*` 은 gitignore 대상이다. 반대로 `runs/` 안의 **텍스트
  산출물은 일부러 추적**한다(D35/R3) — GitHub 에서 결과를 그냥 읽을 수 있게.
- `dayrun_0820/venv_yolo/` 는 **08-27에 지웠다**(5.2 GB). 이 사이클 전용 파이썬이며 `env_isaaclab`
  과 다르다. 다시 만들 때:
  `python3.10 -m venv experiments/dayrun_0820/venv_yolo && experiments/dayrun_0820/venv_yolo/bin/pip install -r experiments/dayrun_0820/code/yolo/requirements_yolo.txt`
  (python **3.10.12**, 목록은 추적되는 파일이다). 그 뒤 `weights/yolov8n.pt` 를 다시 받는다.
- `dayrun_0820/yolo_ds/` 는 `code/yolo/make_yolo_dataset.py` 가 만드는 **심링크 데이터셋**이다.
  PNG 는 `dataset/` 에만 있고 여기엔 링크만 있다. 08-27 재편 뒤 링크는 **상대경로**라서
  저장소를 통째로 옮겨도 깨지지 않는다.
- 라운드 폴더를 이름으로 찾을 때는 경로를 외우지 말고 `dataset/ROUNDS.json` 또는
  `variation_kit.round_dir("<라운드이름>")`(셸은 `negobs_round`)을 쓴다.
- 모든 실행 스크립트는 `PYTHONNOUSERSITE=1` 을 켠다.
