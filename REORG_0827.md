# 2026-08-27 저장소 정리 — 무엇이 어디로 갔나

날짜별로 흩어져 있던 폴더를 **목적별**로 다시 묶었다. 원칙 셋: **① 라운드·실험 폴더 이름은
하나도 바꾸지 않았다**(보고서가 인용하는 재현 증거라서), **② 삭제는 승인받은 목록만**,
**③ 옮긴 것은 전부 원장에 적었다**(`Docs/reorg_0827/`). 브랜치 `chore/reorg-0827`, 렌더·학습 없음.

## 1. dataset/ — 196칸 → 9칸

`dataset/` 바로 밑에 196개 라운드가 늘어서 있던 것을 목적별 9칸으로 넣었다(정리 뒤 실습 렌더 1개가 더해져 지금은 197개).
**이름은 그대로, 앞에 그룹 폴더 한 칸이 생겼을 뿐**이다.
`260819_main_on` → `dataset/v2_corpus/260819_main_on`.

`v2_corpus`(16) · `v2_probes`(3) · `cueoff`(15) · `v3_scene_build`(22) · `v3_library`(29) ·
`v3_test_ext`(16) · `v3_aux`(10) · `misc`(2) · `_archive`(84 — 그 안 `_delete_candidates` 19개
0.7 GiB 는 지워도 된다). 자세한 설명은 **`dataset/README.md`**.

## 2. look_check/ — 현역과 보관을 분리

현역·고정 라운드 **377개는 있던 자리 그대로**, 역할이 끝난 **262개**(10.17 GiB)는
`look_check/_archive/<웨이브>/<씬>/<라운드>` 로 물렸다. 라운드 총수는 639개로 보존.
검수 갤러리는 `_review/{w2,w3,w4}/`, 루트에 굴러다니던 로그 12개는 `logs/` 로 모았다.
전수 색인 `look_check/INDEX.md` 는 이제 **생성물**이다 — 손으로 고치지 말고
`python3 scripts/make_lookcheck_index.py` 로 다시 만든다(0.15초).

## 3. Docs/

- `Docs/` 아래 `legacy/`(규칙 없는 두 번째 보관함) **폐지** → 실파일 5건은 `Docs/archive/legacy/`.
  그 안에 있던 "현행 문서를 가리키는 심링크" 2개는 삭제.
- `Docs/` 최상위 **호환 심링크 7개 + `surveys/real_reference_expansion.md` 심링크 삭제**.
  이것들을 인용하던 47파일 62곳을 실경로로 고쳤다(씬 코드 32개의 docstring 포함).
- **`Docs/` 아래 `experiment/` → `campaign/`**(그리고 `Status/` → `status/`).
  루트 `experiments/` 와 한 글자 차이라 계속 헷갈리던 것을 끝냈다. 인용 45파일 83곳 갱신.
- **현황 문서는 하나로.** `Docs/campaign/status/PROJECT_STATE.md`(날짜 없는 파일,
  맨 위 "최종 갱신" 줄만 고친다). 날짜판 4건은 `Docs/archive/campaign_status/`.
- 새 지도 문서: `dataset/README.md` · `experiments/README.md` · 이 파일.

## 4. 저장소 최상위

- 루트에 있던 `run_*.sh` **5개 전부 `scripts/rounds/` 로** — 상설 드라이버
  `scripts/rounds/run_p2_all33.sh` 도 포함. 내용은 한 줄도 안 바꿨으므로 줄 번호 인용(`:36`)은 유효.
- 루트 `__pycache__/` 삭제. `*_kit.py` 8개 + `scene_common.py` 는 **루트 고정**(씬 심링크 34개가 가리킴).
- `README.md` 를 "어디서부터 보나 + 최상위 폴더 한 줄 설명" 지도로 다시 썼다.

## 5. 지운 것 (전부 사전 승인, 합계 10.73 GiB)

| 지운 것 | 크기 | 되살리는 법 |
|---|---:|---|
| `experiments/dayrun_0820/venv_yolo/` | 5.19 GiB | `python3.10 -m venv …` + 추적되는 `code/yolo/requirements_yolo.txt` (python 3.10.12) |
| `look_check/_experiments/gates/lighting_spikes/` | 5.26 GiB | 07-30 이후 안 쓰인 처리량 스파이크 하네스. 재렌더 외 방법 없음(문서 인용만 존재) |
| `experiments/v3_0823/reselect/rgb_s42_repro/{ep9,ep10,last}.pt` | 280 MB | `best.pt`·`metrics.csv` 는 남겼다. 필요하면 재현 학습 |
| `__pycache__/` 20곳 | 6.9 MB | 자동 재생성 |
| `look_check/` 빈 폴더 11개 | 0 | 없어도 된다(오히려 검사 글롭을 오염시켰다) |

## 6. 라운드를 이름으로 찾는 법 (경로를 외우지 않는다)

```bash
python3 -c 'import variation_kit; print(variation_kit.round_dir("260819_main_on"))'
source scripts/lib/negobs_paths.sh && negobs_round 260819_main_on
```
`dataset/ROUNDS.json` 이 `{라운드이름: 그룹폴더}` 대조표다(197줄). 룩체크 라운드는
`look_check/INDEX.md` §6 의 옛경로→새경로 지도에서 찾는다.

## 7. 원장·되돌리는 법

전부 **`Docs/reorg_0827/`** 에 있다. 단계별 보고서 `S1~S6_report.md` + 독립 검증 `S8_verification.md`, 이동 원장
`dataset_moves.tsv` · `lookcheck_moves.tsv` · `docs_moves.tsv`, 치환 원장
`rewrite_apply.tsv` · `lookcheck_citation_edits.tsv` · `docs_citation_edits.tsv`,
삭제 원장 `deletions.tsv`, 이동 전 스냅샷 `snapshot_before/`.
추적 파일의 되돌리기 경로는 `git diff` 다(이 정리는 아직 커밋되지 않은 상태로 넘긴다).

## 8. 일부러 안 건드린 것

- **`experiments/<사이클>/` 폴더 구조** — 이름을 바꾸면 네 자리 수의 인용을 고쳐야 하고,
  그 인용이 재현 증거다. 대신 지도(`experiments/README.md`)를 새로 썼다.
- **봉인 문서** `experiments/v3_0823/PREREG_V3.md` · `weekend_0823/cue_audit/PREREG_CUEOFF.md`
  — sha256 으로 얼려 둔 사전등록이라 **바이트를 안 고쳤다.** 그래서 그 안의 옛 경로 표기는
  옆의 `*_PATHMAP_0827.md` 대조표로 푼다.
- **라운드 이름·실험 폴더 이름·`assets/` 구조·`submission_0830/`** — 전부 그대로.
- 완료된 렌더 드라이버(`scripts/rounds/run_*.sh`)가 적어 둔 옛 출력 경로 — 그때 어디에
  썼는지의 기록이라 고치지 않았다. 다시 돌리면 보관본 옆에 새 폴더가 하나 더 생긴다.
