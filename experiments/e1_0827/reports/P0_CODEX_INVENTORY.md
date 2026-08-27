# P0-1 코덱스 작업분 목록화 — `Practice_NegObs_edge/experiments/edge_seg_0825`

- 작성 2026-08-28 · 브리프 `Docs/briefs/edge_relabel_brief_v6.md` §4 Phase 0-1 · 부록 B
- 성격: **목록화만.** 파일을 하나도 옮기거나 지우지 않았다. 처분은 ❓C-1 결재 뒤.

---

## 승용 요약 (5문장)

1. 코덱스 작업분은 **전량이 별도 워크트리 `Practice_NegObs_edge/` 안에만** 있고, 본 저장소 `Practice_NegObs/` 에는 코덱스가 만든 파일이 **0건**이다(08-25 13:00~18:00 창의 mtime·ctime 검색 결과 0건 — 실측).
2. 크기는 **2.5 GiB · 파일 2,875개**, 그중 2.4 GiB가 검수용 오버레이 PNG 2,448장이다. 실제 라벨 산출물(마스크)은 1.5 MB밖에 안 된다.
3. 그 라벨은 **구 티어 규칙 그대로**다 — 코덱스가 쓴 `code/labeler.py` 는 정본 `experiments/mainrun_0819/code/labeling/labeler.py` 와 **바이트 동일한 복사본**이고, manifest의 판정값은 `V / E / H / H_weak / none_in_fov` 다. 브리프 §1이 폐기한 바로 그 규칙이라 **라벨 원천으로 재사용 불가**다.
4. 워크트리는 **커밋 0건**(브랜치 `exp/edge-seg-0825` 가 `dfeb9f3` 에 그대로 있고 `git status` 는 미추적 디렉터리 1줄뿐)이라, 삭제해도 git 이력에서 잃는 것이 없다.
5. 결재 필요: **(i) `legacy/codex_0827/` 로 격리** vs **(ii) 삭제**(08-27 구두 지시) — ❓C-1.

---

## 1. 워크트리 상태 (실측)

```
$ git -C /home/vislab/Desktop/work_sy/Practice_NegObs_edge status --porcelain | wc -l
1
$ git -C /home/vislab/Desktop/work_sy/Practice_NegObs_edge status --porcelain
?? experiments/edge_seg_0825/
$ git -C .../Practice_NegObs_edge rev-parse --abbrev-ref HEAD   -> exp/edge-seg-0825
$ git -C .../Practice_NegObs_edge log --oneline -1              -> dfeb9f3 (V2S 패널 D101)
$ git -C .../Practice_NegObs_edge log --oneline feat/realism-v1..HEAD | wc -l   -> 0
```

- 브랜치 `exp/edge-seg-0825` 는 **커밋 0건** — 08-24 커밋 `dfeb9f3` 을 그대로 가리킨다.
- 워크트리에 남은 변경은 **미추적 디렉터리 `experiments/edge_seg_0825/` 하나**뿐. 씬·정본 스크립트 수정 0건.
- 워크트리 루트의 씬·kit 파일 mtime은 전부 `2026-08-25 13:42`(체크아웃 시각) — 편집 흔적 없음.

## 2. 산출물 목록 (파일 종류·크기·수정시각)

전체: **2,875 파일 · 2.5 GiB** · mtime 범위 **2026-08-25 13:42 → 17:16**.

### 2.1 확장자별

| 확장자 | 파일 수 | 합계 크기 |
|---|---:|---:|
| `.png` | 1,656 | 2,565.9 MB |
| `.jpg` | 70 | 31.8 MB |
| `.json` | 1,130 | 1.6 MB |
| `.py` | 7 | 0.1 MB |
| `.pyc` | 6 | 0.1 MB |
| `.csv` | 4 | 0.6 MB |
| `.md` | 2 | 0.0 MB |

### 2.2 하위 트리별

| 경로 | 파일 수 | 크기 | 무엇 |
|---|---:|---:|---|
| `baseline_all/` | 2,484 | 2.4 GiB | `260819_main_on/off` 792프레임에 대한 전량 실행 — `overlays/` 792장(2.4 GiB) · `auto_masks/` 1,584 · `all_scene_gallery/` 66 · `final/` 36 · `manifest.{json,csv}` · `final_index.csv` |
| `auto_masks/` | 348 | 1.5 MB | `260820_boost_e_on/off` 336프레임의 자동 마스크 |
| `overlays/` | 12 | 30 MB | 같은 세트의 검수 오버레이(12장만) |
| `code/` | 13 | 160 KB | 아래 2.3 |
| `final/` | 12 | 108 KB | 확정 마스크 12장 |
| `gallery/` | 1 | 320 KB | `e_overlay_page_01_of_01.jpg` |
| `logs/`, `manual/` | 0 | — | 빈 디렉터리 |
| 루트 파일 5개 | 5 | 545 KB | `manifest.csv`(337줄) · `manifest.json` · `final_index.csv`(13줄) · `README.md` · `RENDER_REQUIRED.md` |

### 2.3 코드 7개 (`code/`)

| 파일 | 크기 | mtime(08-25) | 비고 |
|---|---:|---|---|
| `labeler.py` | 40,676 | 13:42 | **정본 `experiments/mainrun_0819/code/labeling/labeler.py` 와 바이트 동일**(`diff -q` 결과 차이 없음) — 구 티어 규칙 그대로 |
| `build_edge_dataset.py` | 7,820 | 16:15 | 페어 라운드(ON/OFF)를 읽어 자동 마스크·manifest 생성 |
| `export_edge_mask.py` | 14,420 | 16:37 | 마스크 추출 |
| `edit_edge_mask.py` | 4,582 | 14:17 | 수동 수정 도구 |
| `make_overlay_gallery.py` | 3,614 | 14:36 | 갤러리 |
| `finalize_edge_masks.py` | 1,964 | 14:18 | auto/manual 병합 |
| `extract_labels.py` | 3,682 | 17:16 | 라벨 추출 |

외부 의존: `cv2`(OpenCV) · `numpy`. 저장소 정본 모듈은 `labeler.py` 복사본을 통해서만 쓴다.

## 3. 이 산출물이 새 파이프라인에서 쓸 수 없는 이유 (실측)

| 근거 | 실측치 |
|---|---|
| 판정 규칙이 **구 티어**다 | `baseline_all/manifest.csv` 792행: `V 438 · none_in_fov 261 · H 45 · E 36 · H_weak 12`. 루트 `manifest.csv` 336행: `V 147 · H 81 · none_in_fov 81 · H_weak 15 · E 12`. `H_weak`·`none_in_fov` 는 브리프 §1이 이름으로 폐기한 규칙이다 |
| 라벨러가 **정본 복사본**이다 | `diff -q code/labeler.py <정본>` → 차이 없음 |
| **E 라벨이 극소수**다 | 두 실행 합쳐 최종 마스크 **48장**(`final/` 12 + `baseline_all/final/` 36). 브리프의 새 정의에서 E는 훨씬 넓은 집합이 되므로 이 48장은 대표성이 없다 |
| 경로가 **08-27 재편으로 깨졌다** | 루트 `manifest.csv` 는 절대경로 `…/Practice_NegObs/dataset/260820_boost_e_on/…` 를 적어 두었는데 그 경로는 이제 없다(`ls` 실패 — 라운드는 `dataset/v2_corpus/260820_boost_e_on` 로 이동). `baseline_all/manifest.csv` 의 상대경로 `../../../Practice_NegObs/dataset/260819_main_on/…` 도 같은 이유로 깨졌다 |

## 4. 본 저장소(`Practice_NegObs`) 안의 코덱스 파일 — **0건**

```bash
cd /home/vislab/Desktop/work_sy/Practice_NegObs
find . -path ./.git -prune -o -newermt "2026-08-25 13:00" ! -newermt "2026-08-25 18:00" -type f -print | wc -l
# -> 0
find . -path ./.git -prune -o -newerct "2026-08-25 13:00" ! -newerct "2026-08-25 18:00" -print | wc -l
# -> 0
```

문자열 검색으로도 **코드·산출물 참조는 없다** — `edge_seg_0825` / `Practice_NegObs_edge` 를 언급하는 파일 11개는 전부 **문서**(`DECISIONS.md`, `Docs/reorg_0827/S1~S8 리포트`, `PROJECT_STATE.md`)이고, 파이프라인 코드는 한 건도 참조하지 않는다.

> 방법 주의: mtime/ctime 휴리스틱은 **파일을 복사하면서 타임스탬프를 보존한 경우를 잡지 못한다.** 다만 (a) `git status` 가 0줄이고 (b) 어떤 코드도 그 산출물을 참조하지 않으므로, 실행 경로에 코덱스분이 섞여 들어갈 통로는 없다.

---

## 5. 처분안 두 가지 — ❓ 결재

| 안 | 내용 | 장점 | 단점 |
|---|---|---|---|
| **(i) 격리** | `Practice_NegObs_edge/experiments/edge_seg_0825/` 를 `Practice_NegObs/legacy/codex_0827/` 로 이동(브리프 §8·부록 B) | 나중에 §6-⑥ 신구 대조표를 만들 때 구 티어 판정 1,128행(792+336)을 그대로 대조 자료로 쓸 수 있다 | 본 저장소가 **2.5 GiB** 늘어난다. 그중 2.4 GiB는 오버레이 PNG로, 대조표에 필요 없다 |
| **(ii) 삭제** | 워크트리째 지운다(승용 08-27 구두 지시) | 디스크 2.5 GiB 회수, 백지 재시작이 물리적으로 보장된다 | 구 티어 판정표를 잃는다 — §6-⑥(신구 대조표, ❓-3)을 채택하면 **재계산이 필요**하다(구 `labeler.py` 로 다시 돌려야 함) |
| **(iii) 절충** [클로드 제안] | `manifest.csv`·`manifest.json`·`final_index.csv`·`README.md`·`RENDER_REQUIRED.md`·`code/`(160 KB) = **총 약 0.7 MB만** `legacy/codex_0827/` 로 옮기고, 오버레이·마스크 PNG 2.5 GiB는 삭제 | 대조 자료를 지키면서 용량은 사실상 0 | 마스크 이미지 자체는 잃는다(단 브리프가 라벨 원천 사용을 금지했으므로 손실 아님) |

| 번호 | 항목 | 담당 |
|---|---|---|
| **❓C-1** | 처분 (i)/(ii)/(iii) 중 무엇인가? [클로드 제안: (iii)] | 승용 |
| **❓C-2** | ❓-3(§6-⑥ 신구 대조표 채택)이 **아니오**로 결정되면 (ii) 삭제가 자동으로 맞다. ❓-3을 먼저 정해 주시겠습니까? | 승용 |
| **❓C-3** | 워크트리 `Practice_NegObs_edge` 자체(브랜치 `exp/edge-seg-0825`, 커밋 0건)를 `git worktree remove` 로 정리해도 되는가? 본 세션은 지시에 따라 **목록화만** 했고 손대지 않았다 | 승용 |

---

## 부록. 실측 명령

```bash
E=/home/vislab/Desktop/work_sy/Practice_NegObs_edge
git -C $E status --porcelain | wc -l                       # 1
git -C $E log --oneline feat/realism-v1..HEAD | wc -l      # 0
find $E/experiments/edge_seg_0825 -type f | wc -l          # 2875
du -sh $E/experiments/edge_seg_0825                        # 2.5G
diff -q $E/experiments/edge_seg_0825/code/labeler.py \
        /home/vislab/Desktop/work_sy/Practice_NegObs/experiments/mainrun_0819/code/labeling/labeler.py   # (동일)
python3 -c "import csv,collections;print(collections.Counter(r['tier'] for r in csv.DictReader(open('$E/experiments/edge_seg_0825/baseline_all/manifest.csv'))).most_common())"
ls -d /home/vislab/Desktop/work_sy/Practice_NegObs/dataset/260819_main_on   # No such file (재편으로 이동)
```
확장자·하위트리 집계 스크립트는 `<scratchpad>/p0/` 에 인라인으로 실행했다(파이썬 `os.walk` + `collections.Counter`).
