# PANELS_VERDICT — v3-A VERDICT 웨이브 의무 정성 패널 4종

- **작성** Claude Code · 2026-08-24 · **CPU 전용 · 새 렌더 0 · 새 추론 0 · GPU 0 · git 무접촉**
- **생성기** `experiments/v3_0823/code/verdict_panels.py`
  ```bash
  PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES= \
    /home/vislab/miniconda3/envs/env_seg/bin/python \
    experiments/v3_0823/code/verdict_panels.py            # 약 6초 · 4장 전부
  #  --force  이미 있는 PNG 도 다시 그린다 (기본은 이어그리기 · resume-safe)
  #  --only a|b|c|d  한 장만
  ```
- **결정성**: 난수 없음 · 선택 규칙은 모두 전순서 정렬 — 재실행하면 PNG 가 **바이트 동일**하다 (실측).
- **격자** `gridspec_v1.json` (`PROVISIONAL-GRID-V1` · 4밴드 × 5섹터 = **20칸**)
- **시드** `rgb_s42` · `rgb_s43` · `rgb_s44` — 오버레이 확률은 **3시드 평균**, 막대의 오차막대는 **σ(ddof=1, n=3)**
- **동결 규약 준수** (`PREREG_V3.md`): 한국어 라벨 · 패널마다 출처 푸터 · `sceneH3`(완전-은닉 층) 계기판① 풀링 제외 · recall 은 FA 동반 인쇄 · 프레임축·칸축 **동시** 인쇄 · C·D팔 GT 는 사양 상수 전 칸 음성 명시 · PNG ≤ 2 MB

---

## 0. 한눈에

| 파일 | 무엇을 보이나 | 고른 컷 / 키 | 원장 |
|---|---|---|---|
| **`panel_a_fourarm.png`**<br>2082×1099 px · 1507 KB | 한 포즈를 A/B/C/D 네 팔로 재렌더한 바이트-쌍 컷 위에 v2(위)·v3-A(아래)의 20칸 확률 히트를 되투영. GT-양성 칸은 하늘색 이중 윤곽. | `sceneH2` / 밴드 `h` / `L7__s20260823__0007.png` — v3-A 트윈 적중 6칸 · 최대 마진 0.329 | `eval_v3textext/*` · `eval_v3a_textext/*` · `dataset_manifest_v3_textext{,_bd}.json` · `gridspec_v1.json` |
| **`panel_b_dash1_exemplars.png`**<br>2001×1680 px · 1833 KB | 계기판① 대표 짝 — v3-A 는 A팔에서 켜고 C팔에서 끄는데(트윈-조건부 적중) 같은 칸에서 v2 는 A·C 둘 다 켠다. | `sceneH2` / 밴드 `h` / `L5__s20260823__0002.png` → 결정 칸 **C3b** · `sceneH2` / 밴드 `h` / `L5__s20260823__0006.png` → 결정 칸 **D3b** · `sceneH2` / 밴드 `h` / `L0__s20260823__0000.png` → 결정 칸 **D3b** | 위와 동일 |
| **`panel_c_ncue_trap.png`**<br>2011×1669 px · 632 KB | N-cue 함정 — `sceneN9`/`sceneN11` 은 GT 전 칸 음성이라 색칠된 쐐기가 **전부 오경보**. C팔(단서 있음) vs D팔(단서 없음). | `sceneN9` / 밴드 `b2` / `L0__s20260824__0002.png` (v2 C 4칸 · v3 C 2칸) · `sceneN9` / 밴드 `base` / `L0__s20260823__0006.png` (v2 C 4칸 · v3 C 2칸) · `sceneN11` / 밴드 `base` / `L7__s20260823__0004.png` (v2 C 4칸 · v3 C 3칸) | 위와 동일 |
| **`panel_d_before_after.png`**<br>2131×2877 px · 606 KB | 계기판 ①②③ before(v2)/after(v3-A) 막대·산점. ① 트윈-조건부 recall (프레임축+칸축, FA-정합 8지점), ② CUE-OFF 용량-반응 (v3 단독), ③ N-cue 함정 FA_C·FA_D·차 (프레임축+칸축). | 수치 전용 — 컷 선택 없음 | `v2_textext_tables.json` · `v3a_textext_tables.json` · `verdict_dash2.json` · `verdict_core.json`(참고행) |

---

## 1. `panel_a_fourarm.png` — 한 포즈 · 네 팔

- **고른 컷**: `sceneH2` / 밴드 `h` / `L7__s20260823__0007.png`  (A·B·C·D 네 라운드가 같은 밴드라운드·같은 파일 이름을 공유하는 바이트-쌍 포즈)
- **선택 규칙(결정적)**: 풀링 strict-H 층(paired-H ∩ {sceneH1, sceneH2}) 중 v3-A 의 트윈-조건부 적중 칸 수 최대 → GT-양성 칸의 최대 마진 (p_A − p_C) → 키 사전순.
  선택된 컷의 적중 칸 **6칸**, 최대 마진 **0.329**.
- **열 라벨**: `A 팔 (위험 ON · 단서 유지)` · `B 팔 (위험 ON · 단서 제거)` · `C 팔 (위험 OFF · 단서 유지)` · `D 팔 (위험 OFF · 단서 제거)`. 행 라벨: `v2 (레시피 동결 체크포인트)` / `v3-A`.
- **오버레이**: 칸마다 `inferno` 램프로 확률을 칠하고(투명도도 확률에 비례) τ_op 0.5 이상이면 흰 테두리를 두른다. GT-양성 칸은 검정+하늘색 이중 윤곽.
- **A·B팔 GT 는 동일**(VG-01), **C·D팔 GT 는 사양 상수 전 칸 음성**(AC-INSTR-1 C3-2) — C·D 타일에서 보이는 색은 전부 오경보다.

## 2. `panel_b_dash1_exemplars.png` — 계기판① 대표 짝

- **선택 규칙(등록 · 완화 없음)**: 풀링 층(`sceneH1`+`sceneH2`, **`sceneH3` 원천 제외**)의 paired-H 컷에서 τ=0.5·3시드 평균 확률으로
  1. v3-A 가 **GT-양성 칸**에서 **A팔 발화 ∧ C팔 미발화** (트윈-조건부 적중)
  2. **같은 칸**에서 v2 는 **A팔·C팔 둘 다 발화** (무조건 발화)
- **결과**: 규칙을 만족하는 컷 **9개**, (컷,칸) 짝 **14개**. 마진 (p3_A − p3_C) 상위 **3컷**을 인쇄했다.
- **씬 분포 (실측 · 특기)**: 규칙을 만족하는 컷의 씬 분포는 `sceneH2` 9개 이다. 즉 **`sceneH1`(둔덕형, 33프레임)에서는 이 조건을 만족하는 컷이 하나도 없었다** — H1 은 (A,C) 광학차 자체가 작은 층이라(mean|ΔI| 중앙값 H2 7.67 vs H1 2.43, PREREG §2.1 층화 1) v3-A 가 A/C 를 가를 여지가 적다. 패널 3행이 모두 `sceneH2` 인 것은 선택 편향이 아니라 **후보 집합 자체가 그렇기 때문**이다.

| 행 | 컷 | 결정 칸 | v3-A A팔 | v3-A C팔 | v2 A팔 | v2 C팔 |
|---|---|---|---|---|---|---|
| 1 | `sceneH2` / 밴드 `h` / `L5__s20260823__0002.png` | **C3b** | 0.517 (발화) | 0.241 (미발화) | 0.679 (발화) | 0.712 (발화) |
| 2 | `sceneH2` / 밴드 `h` / `L5__s20260823__0006.png` | **D3b** | 0.696 (발화) | 0.424 (미발화) | 0.570 (발화) | 0.540 (발화) |
| 3 | `sceneH2` / 밴드 `h` / `L0__s20260823__0000.png` | **D3b** | 0.537 (발화) | 0.268 (미발화) | 0.536 (발화) | 0.551 (발화) |

- **분모**: paired-H ∩ {sceneH1, sceneH2} = **51프레임 / 393칸** (`sceneH3` 21프레임은 완전-은닉 층이라 제외 — PREREG §2.1 층화 3).
- 열은 `v2·A팔` / `v2·C팔` / `v3-A·A팔` / `v3-A·C팔` 4칸이고 행은 컷이다 (3×4 이미지 격자).

## 3. `panel_c_ncue_trap.png` — N-cue 함정

- **씬**: `sceneN9` · `sceneN11` — **네 팔 모두 GT 전 칸 음성**(실측 0칸). 따라서 이 패널에서 **색칠된 모든 쐐기는 오경보**다.
- **열**: `C 팔 (단서 있음 · 위험 없음)` / `D 팔 (단서 없음 · 위험 없음)` 을 v2·v3-A 각각 (3×4 격자).
- **선택 규칙(결정적)**: τ=0.5·3시드 평균에서 v2 의 C팔 발화 칸 수 내림차순 → C팔 최대확률 내림차순 → 키 사전순, (씬, 밴드라운드) 조합 비중복 탐욕 3컷.

| 행 | 컷 | v2 C팔 발화 | v3-A C팔 발화 | v2 D팔 | v3-A D팔 | v2 C팔 최대 p (칸) |
|---|---|---|---|---|---|---|
| 1 | `sceneN9` / 밴드 `b2` / `L0__s20260824__0002.png` | 4칸 | 2칸 | 0칸 | 0칸 | 0.974 (C3b) |
| 2 | `sceneN9` / 밴드 `base` / `L0__s20260823__0006.png` | 4칸 | 2칸 | 0칸 | 0칸 | 0.714 (C3b) |
| 3 | `sceneN11` / 밴드 `base` / `L7__s20260823__0004.png` | 4칸 | 3칸 | 0칸 | 0칸 | 0.686 (C3b) |

- **분모**: 이 패널은 `sceneN9`+`sceneN11` = 팔마다 **96프레임 / 1,920칸** — 계기판③의 **씬군 분해**다. 등록된 헤드라인 분모는 **C·D팔 전량 288프레임 / 5,760칸** (PREREG §2.3 · AC §4.10, void 버킷 공집합)이며 `panel_d` 가 그것을 주 막대로 인쇄한다.
- `FA_C − FA_D` = **단서-유발 오경보 몫**, `FA_D` = 순수 씬-연합의 직접 게이지 (PREREG §2.3).

## 4. `panel_d_before_after.png` — 계기판 ①②③ before/after

| 블록 | 무엇 | 축 | 원장 키 |
|---|---|---|---|
| **①** | 트윈-조건부 recall, 풀링 H1+H2 (n=51프레임 / 393칸), FA-정합 8지점에서 v2 vs v3-A | **프레임축 + 칸축 둘 다** (각 x눈금 아래에 동반 `FA_D` 를 `v2\|v3` 로 병기 — §6-5 FA 동반 의무) | `v2_textext_tables.json::summary.rgb.ops[].pooled_{frame,cell}_recall_twin` · `v3a_textext_tables.json::raw.summary.v3a_rgb.ops[]` 동일 키 |
| **②** | CUE-OFF 용량-반응 — 살아있는 **4단위**(씬×밴드, `n_paired ≥ 10`) 산점 + 적합선. x = 제거된 단서 키 수 / 광학 `mean\|ΔI\|`, y = `FA_B` | **프레임축(●, 왼쪽 눈금) + 칸축(▲, 오른쪽 눈금)** 동시 | `verdict_dash2.json::unit_static` · `per_run[*].ops[0].units` · `…reg` · `summary.v3a_rgb.ops[]` |
| **③** | N-cue 함정 FA — `FA_C` · `FA_D` 막대(빗금 = D팔)와 별도 행의 `FA_C − FA_D`, τ_op + FA-정합 8지점. **주 막대 = 등록 분모(C·D팔 전량 288프레임 / 5,760칸)**, 그 위에 겹친 표식 = **N9+N11 씬군 분해**(96프레임 / 1,920칸) | **프레임축 + 칸축 둘 다** | 양 표의 `FA_{C,D}_{frame,cell}` · `FA_diff_{frame,cell}` (전량) 와 `ncue_FA_{C,D}_{frame,cell}` (씬군 분해 · 차는 **시드별로 뺀 뒤** mean·σ) |

- **② 에는 v2 팔이 없다** — B팔이 v3 훈련팔이라 v2 체크포인트의 before 가 성립하지 않는다 (`PREREG_V3.md` §2.2 **주의** · `verdict_dash2.json::v2_reference.why_no_v2_arm`). 그래서 ② 는 **v3-A 단독 절대값 + 층별 기울기**이며 before/after 비교가 아니다. 패널에 그대로 인쇄돼 있다.
- `sceneH3|base` 단위는 `n_paired 3 < 10` 으로 **VOID** — 회귀에서 빼고 ✕ 로 표시한 뒤 사유를 붙였다 (VG-void: void ≠ 음성).
- `verdict_core.json` 은 **test-core** 헤드라인이라 계기판 어느 축에도 넣지 않았다 (PREREG §6-11 무대 위반). 머리글에 참고 한 줄로만 적었고, 그 줄도 recall 과 FA 를 프레임축·칸축 모두 병기했다.

---

## 5. 무결성 자기점검

| 규약 | 확인 |
|---|---|
| 한국어 라벨 | 4/4 패널 제목·축·범례 전부 한국어 |
| 출처 푸터 (원장 · 런/시드 · 운용점 · 분모 · 날짜) | 4/4 패널 |
| `sceneH3` 풀링 금지 | 계기판① 풀링 = H1+H2 51프레임 (코드에서 `HIDDEN_SCENE` 을 선택 모집단에서 제외) |
| recall 에 FA 동반 | ① 의 x눈금마다 `FA_D` 병기 + ③ 이 같은 그림 안에 있음 |
| 프레임축·칸축 동시 | ① ② ③ 전부 두 축을 인쇄 |
| C·D팔 GT = 사양 상수 전 칸 음성 | (a)(b)(c) 타일 캡션과 4개 푸터 전부에 명시 |
| PNG ≤ 2 MB | panel_a_fourarm.png 1507 KB · panel_b_dash1_exemplars.png 1833 KB · panel_c_ncue_trap.png 632 KB · panel_d_before_after.png 606 KB |


---

## 6. `panel_e_family_strata.png` — 계기판② FA 5가족 층화 (**V-3 이행 · 08-24 추가**)

- **생성기** `experiments/v3_0823/code/verdict_panel_family.py` (원장 = `verdict_fa_family.json`)
  ```bash
  PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES= \
    python3 experiments/v3_0823/code/verdict_panel_family.py
  ```
- **크기** 2228×1618 px · 407 KB (≤ 2 MB 규율 준수)
- **본문** `VERDICT_V3.md §15` · **의무 출처** `PREREG_V3.md §2.2` 「층화」행 · **P-12**

| 칸 | 무엇을 보이나 | 축 · 규약 |
|---|---|---|
| 상단 3칸 | 팔 **B · C · D 각각**의 5가족 before(v2)/after(v3-A) | 세로축 = **노출 정규화 발화율** `FA(가족) / (그 가족의 위험노출 칸 × 런)` — 가족마다 분모가 다르므로 물량 막대가 아니다. 오차막대 = **σ(ddof=1, 3시드)**. 막대 위 숫자 = Δ (초록 = 감소) |
| 하단 좌·중 | C팔·D팔 「칸/FA프레임」 Δ 의 **shift-share** 분해 | **규모항**(FA 프레임 수 변화) + **조성항**(그 가족의 칸 수 변화) = Δ · 항등 검산 통과. 가족명 아래 = 절대 칸 수 v2 → v3-A (시드 합산 · 배타 귀속) |
| 하단 우 | C팔 밴드 반경 법칙 (log-log) | `FA_CENSUS §3.3` 의 test-core `R^1.98` 이 미학습 무대에서 재현되는가 — v2 **+2.07** / v3-A **+1.62** |

- **층을 절대 합치지 않는다** — B·C·D 는 분모도 의미도 다르다. A팔은 **참고행**이라 패널에 넣지 않았다.
- **세대 비교는 rgb 대 rgb (3런 대 3런)** — v2 9런 풀링은 `§15.8` 에 별도 블록으로만 있다.
- **σ 초과 가족 0/15** 을 부제에 못박았다 — 층화는 **인쇄 의무이지 판정 축이 아니다** (`§6-1`).
- **장식형의 계측기가 test-core 와 다르다**(`[수동]` → `[기계]`, `.idseg.npz` + VG-09 귀속기).
  푸터에 그대로 적었고, 두 무대의 장식형 수치를 잇는 문장은 본문·패널 어디에도 없다.
- **D팔 장식형은 "0" 이 아니라 "노출 0 (정의상 산출 불가)"** 로 칠했다 — D팔은 단서 프림 화소가 실측 0 이다.
