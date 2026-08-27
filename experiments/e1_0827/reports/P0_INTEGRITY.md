# P0-0 작업 사본 무결성 검사 — dfeb9f3(08-24) → HEAD(544ed0b)

- 작성 2026-08-28 · 저장소 `Practice_NegObs` · 브랜치 `feat/realism-v1` · 브리프 `Docs/briefs/edge_relabel_brief_v6.md` §4 Phase 0-0
- 성격: **읽기 전용 감사.** 커밋·되돌리기·파일 이동을 하지 않았다. 모든 수치는 부록 A의 명령으로 재현된다.

---

## 승용 요약 (5문장)

1. **P2(씬 파일·카메라 규격·위험 기하 불변)는 침해되지 않았다.** 씬 모듈 35개 전부가 독스트링(문서 인용 경로) 한 줄만 바뀌었고, 코드는 구문 트리 수준에서 **완전히 동일**하다.
2. 카메라 규격도 무사하다 — `scene_common.py`는 독스트링 2줄만, `variation_kit.py`는 **라운드 이름→경로 해석 헬퍼가 새로 붙었을 뿐** 카메라·조명·시드 함수는 한 줄도 바뀌지 않았다.
3. 바뀐 코드 71개 파일은 **전부 08-27 정리의 경로 해석 전환** 한 가지다: 평평한 `dataset/<라운드>` → 그룹이 한 칸 낀 구조를 이름으로 푸는 `round_dir()` / `negobs_round`. 여기에 로그 경로 `look_check/*.log → look_check/logs/*.log`, 문서 인용 경로 정정이 붙는다.
4. 지금 작업 트리는 **깨끗하다** — `git status --porcelain` 0줄(수정·미추적 파일 없음).
5. 결재 필요: 이 08-27 변경분을 **승인된 것으로 확정**해 주시거나(정리 계획을 이미 승인하셨으므로 [클로드]는 승인을 제안), 되돌릴 항목을 지정해 주십시오 — ❓I-1.

---

## 1. 무엇을 어떻게 판정했나 [방법]

`git diff --stat dfeb9f3..HEAD` 로 바뀐 파일을 뽑고, 파일마다 **구버전과 현버전의 파이썬 구문 트리(AST)에서 독스트링을 제거한 뒤 문자열로 비교**했다. 두 트리가 같으면 `주석/독스트링만`, 다르면 `코드`다. 셸 스크립트는 `#` 로 시작하는 줄과 빈 줄을 지운 뒤 비교했다.

이 방식을 쓴 이유: "diff 줄을 눈으로 본다"는 카메라 파라미터 한 줄을 놓칠 수 있지만, **AST가 같다는 것은 실행 의미가 같다는 것**이라 위험 기하·카메라 상수가 바뀌지 않았음의 기계적 증거가 된다. 도구: `experiments/e1_0827/code/`가 아닌 스크래치 스크립트(부록 A-1에 전문 경로).

판정 결과 총계 — **140개 파일**:

| 분류 | 파일 수 |
|---|---:|
| 주석/독스트링만 | 43 |
| 코드 | 71 |
| 신규 파일(추가) | 26 |

---

## 2. 결론 표 — 그룹별

### A. 씬 모듈 (`scenes/`) — 35개 파일, **전부 주석/독스트링만**

| 파일군 | 파일 수 | 훅 | 분류 | 무엇이 바뀌었나 | P2 영향 |
|---|---:|---:|---|---|---|
| `scenes/main/*.py` | 14 | 각 1 | 주석/독스트링만 | 독스트링 `Spec :` 줄의 문서 경로 정정 (`Docs/multi_scene_brief_v3.md` → `Docs/briefs/multi_scene_brief_v3.md` 등) | **없음** |
| `scenes/batch1/*.py` | 11 | 각 1 | 주석/독스트링만 | 같음 (`Docs/nanobanana_batch1_geometry_map.md` → `Docs/archive/legacy/…`) | **없음** |
| `scenes/probe/*.py` | 3 | 각 1 | 주석/독스트링만 | 같음 | **없음** |
| `scenes/archive_v3/*.py` | 7 | 각 1 | 주석/독스트링만 | 같음 | **없음** (기본 제외 대상) |

씬 diff에 등장한 변경 줄은 **전부 문서 인용 줄**이다 — 실측: `git diff dfeb9f3..HEAD -- scenes/` 의 +/- 줄 **74줄** 중 54줄이 `Spec :` 로, 14줄이 `사양서 :`(archive_v3 한국어판)로 시작하고, 나머지 6줄은 그 인용 블록의 이어지는 줄이다(부록 A-3에 전문). 카메라 파라미터·계단 리서/트레드·낙차 깊이·프림 좌표가 든 줄은 **0줄**.

### B. 공용 라이브러리 — 2개 파일

| 파일 | 훅 | 분류 | 무엇이 바뀌었나 | P2 영향 |
|---|---:|---|---|---|
| `scene_common.py` | 2 | 주석/독스트링만 | 인용 경로 2줄(`Docs/multi_scene_brief_v2.md`, `Docs/stair_typology_survey_v2.md` → `Docs/briefs/`, `Docs/surveys/`). AST 동일 | **없음** |
| `variation_kit.py` | 4 | **코드** (+196/−1) | ① `import fnmatch` 추가 ② `rounds_index` / `round_candidates` / `round_dir` / `round_dir_or_flat` / `has_round` / `rounds_matching` **신규 함수 6개** ③ `data_root(run_stamp)` 의 본문 1줄이 `os.path.join(REPO,"dataset",run_stamp)` → `round_dir_or_flat(run_stamp)` 로 교체 | **없음** — 카메라·조명·시드·AZ_LEDGER 함수는 훅에 포함되지 않는다. `data_root` 는 *새* 스탬프에 대해 예전과 같은 평평한 경로를 돌려주고, *기존* 스탬프만 그룹 아래에서 찾아 준다 |
| `stair_kit.py`·`ground_kit.py`·`building_kit.py`·`infra_kit.py`·`props_kit.py`·`urban_kit.py`·`facade_kit.py` | 0 | — | **diff에 등장하지 않음(무변경)** | **없음** |

### C. 정본 스크립트 (`scripts/`) — 56개 파일

| 파일군 | 파일 수 | 훅 합 | 분류 | 무엇이 바뀌었나 | P2 영향 |
|---|---:|---:|---|---|---|
| `scripts/run_data_render.py` | 1 | 2 | 주석/독스트링만 | 독스트링에 "0827 경로 규약" 문단 추가. **AST 동일 — 렌더 로직 무변경** | **없음** |
| `scripts/sensor_augment.py` · `harvest_refs.py` · `make_allview_sheet.py` · `shortcut_audit.py` | 4 | 5 | 주석/독스트링만 | 사용법 독스트링의 경로 예시 | **없음** |
| `scripts/make_review_gallery.py` · `spike_realism.py` | 2 | 3 | 코드 | 갤러리 출력 경로 `look_check/_review_w2` → `look_check/_review/w2`, 출력 디렉터리 `makedirs` 1줄 추가 | **없음** |
| `scripts/rounds/run_*.sh` (기존) | 22 | 46 | 코드 | ⓐ `local outdir` + `negobs_round` 로 출력 라운드 해석 ⓑ 로그 경로 `look_check/*.log` → `look_check/logs/*.log` ⓒ `bash run_p2_all33.sh` → `bash scripts/rounds/run_p2_all33.sh` | **없음** (렌더 인자·씬 목록·조건 목록 불변) |
| `scripts/rounds/run_260805_w3_hedgeswap.sh` | 1 | 1 | 주석/독스트링만 | 주석 경로 | **없음** |
| `scripts/lib/negobs_paths.sh` · `scripts/reorg/*.py`(18) · `scripts/tests/test_round_dir.py` · `scripts/make_lookcheck_index.py` | 21 | — | 신규 파일 | 08-27 정리 도구 일체 + 라운드 해석 셸 함수 + 그 회귀 시험 | **없음** (씬·렌더에 관여하지 않음) |
| 루트 → `scripts/rounds/` 이동 5건 | 5 | — | 이동 | `run_260814_w4_d4iter.sh` 등 4건은 **R100(바이트 동일)**, `run_p2_all33.sh` 만 R094(위 ⓒ 1줄) | **없음** |

### D. 구 사이클 `experiments/*/code/` — 47개 파일

| 파일군 | 파일 수 | 훅 합 | 분류 | 무엇이 바뀌었나 | P2 영향 |
|---|---:|---:|---|---|---|
| `experiments/v3_0823/code/*.py`·`*.sh` (45) + `experiments/dayrun_0820/code/run_phase1.sh` | 46 | 175 | 코드 | 전부 같은 전환: `os.path.join(DATA, rnd, …)` → `round_dir(rnd)`, `glob(DATA/<pat>)` → `rounds_matching(pat)`, 셸의 `$D/$1` → `negobs_round $1`. 문서 인용 경로 1건(`Docs/experiment/` → `Docs/campaign/`) | **없음** (이 사이클 코드는 신규 파이프라인에서 사용 금지) |
| `experiments/v3_0823/code/h67_yield.py` | 1 | 1 | 주석/독스트링만 | 주석 경로 | **없음** |
| `experiments/v3_0823/code/view_overlay.py` | 1 | — | 신규 파일 | 08-27 실습 가이드용 오버레이 뷰어 | **없음** |
| `experiments/mainrun_0819/code` | 0 | — | — | **diff에 등장하지 않음(무변경)** — 구 `labeler.py` 포함 | **없음** |

**비주석 변경이 발견된 파일의 정확한 목록 = 위 71개** (전문: 부록 A-2 `codelines.txt`). 그중 **씬 파일·카메라 규격·위험 기하에 해당하는 파일은 0개**다.

---

## 3. 현재 작업 트리 상태

```
$ git status --porcelain | wc -l
0
```

수정된 추적 파일 0건, 미추적 파일 0건. (`dataset/`·`look_check/` 는 `.gitignore` 대상이라 여기 잡히지 않는다 — 데이터 쪽 실측은 `P0_CENSUS.md`.)

> 주의: 이 검사 **이후** 본 세션이 `experiments/e1_0827/` 와 `legacy/codex_0827/` 디렉터리를 새로 만들었다(브리프 §8). 그 시점 이전의 상태가 위 0줄이다.

---

## 4. ❓ 결재란

| 번호 | 항목 | 담당 |
|---|---|---|
| **❓I-1** | 위 08-27 변경분(경로 해석 전환 71파일 + 문서 인용 정정 43파일 + 신규 도구 26파일)을 **승인된 변경으로 확정**하는가? [클로드 제안: 승인 — 씬·카메라·위험 기하에 대한 코드 변경이 0건임이 AST 비교로 확인됐고, 정리 계획 자체는 이미 결재된 건이다.] 되돌릴 항목이 있으면 파일명을 지정해 주십시오 | 승용 |
| **❓I-2** | `variation_kit.data_root()` 의 동작 변경(기존 스탬프는 그룹 아래에서 찾고, 새 스탬프는 평평하게 생성)을 **정본 동작으로 확정**하는가? 신규 렌더가 `dataset/<스탬프>` 에 평평하게 떨어진 뒤 사람이 그룹으로 옮기는 절차가 전제된다 | 승용 |
| **❓I-3** | `scenes/archive_v3/` 7개 씬도 독스트링이 수정됐다. 브리프는 이 폴더를 **기본 제외**로 두는데, 정본 렌더 스크립트(`scripts/run_data_render.py:60`)는 애초에 `scenes/main`·`scenes/batch1` 만 색인하므로 archive_v3 는 **렌더로 도달 불가능**하다. 이 사실을 근거로 archive_v3 를 모집단에서 완전 배제해도 되는가? | 승용 |

---

## 부록 A. 실측 명령

**A-1. 분류 스크립트** (스크래치, 저장소 밖):
`/tmp/claude-1000/-home-vislab-Desktop-work-sy/15df50ca-11be-4545-a9e5-5c8c56211ca8/scratchpad/p0/classify.py`
— 각 파일의 `git show dfeb9f3:<path>` 와 `git show HEAD:<path>` 를 `ast.parse` → 독스트링 노드 제거 → `ast.dump` 비교.

```bash
cd /home/vislab/Desktop/work_sy/Practice_NegObs
git diff --stat dfeb9f3..HEAD -- scenes/ scene_common.py '*_kit.py' scripts/ \
    experiments/mainrun_0819/code experiments/dayrun_0820/code experiments/v3_0823/code
# -> 140 files changed, 5231 insertions(+), 220 deletions(-)

git diff --name-status dfeb9f3..HEAD -- scenes/ scene_common.py '*_kit.py' scripts/ \
    experiments/mainrun_0819/code experiments/dayrun_0820/code experiments/v3_0823/code \
  | awk '{print $1}' | sort | uniq -c
# ->  26 A   114 M

python3 <scratchpad>/p0/classify.py <scratchpad>/p0/classify.json
# -> Counter({'CODE': 71, 'COMMENT-ONLY': 43, 'NEW-FILE': 26})
```

**A-2. 비주석 변경 줄 전문**: `<scratchpad>/p0/codelines.txt`
(생성: `<scratchpad>/p0/codelines.py` — CODE 분류 파일의 `git diff -U0` 에서 주석·빈 줄을 뺀 +/- 줄 전부를 인쇄하고, 경로 관련 패턴(`round_dir|negobs_round|ROUNDS.json|dataset/|look_check|Docs/`)에 걸리지 않는 줄을 따로 표시한다. 걸러진 잔여 줄은 전부 `local outdir` 선언·`LOG=look_check/logs/…`·`import sys`·`makedirs` 같은 구조 줄이었다.)

**A-3. 씬 diff 줄 검사**:
```bash
git diff dfeb9f3..HEAD -- scenes/ | grep -E '^[+-]' | grep -vE '^(\+\+\+|---)' | wc -l
# -> 74
git diff dfeb9f3..HEAD -- scenes/ | grep -E '^[+-]' | grep -vE '^(\+\+\+|---)' \
  | sed 's/^[+-]//' | grep -cE '^\s*Spec'          # -> 54  (나머지 20줄: '사양서' 14 + 이어지는 줄 6)
```

**A-4. 개별 확인 예시**:
```bash
git diff dfeb9f3..HEAD -- scripts/run_data_render.py   # 독스트링 2훅
git diff dfeb9f3..HEAD -- scene_common.py              # Spec 인용 2줄
git diff dfeb9f3..HEAD -- variation_kit.py | grep -E '^@@'
# -> @@ -30,6 +30,7 (import) / @@ -104,6 +105,114 (신규 함수) / @@ -111,8 +220,94 (data_root)
git status --porcelain | wc -l                          # -> 0
git diff --name-status -M -C dfeb9f3..HEAD | grep -E '^R' | grep 'scripts/rounds'
# -> R100 x4 (바이트 동일 이동), R094 run_p2_all33.sh
```
