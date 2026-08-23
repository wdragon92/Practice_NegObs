# TWIN_TOL_RESOLUTION — 트윈 페어링 허용오차 3자 불일치 해소

- **작성**: Claude Code · 2026-08-23 · **과업**: ACCOUNTING §4.3 1번 처분 (원장 결함 ① / `LAB-13` / N-1)
- **자원**: CPU 전용, GPU 미사용, git 미사용. 동결된 확률 덤프 재사용(`PYTHONNOUSERSITE=1`).
- **성격**: 출하물 편집 없음. 본 문서는 **판정 + 각주 초안**만 제공한다.

---

## 0. 결론 한 줄

**공표된 v2 트윈 숫자는 전부 `--tol 0.15`(D20 허용오차)로 생성되었다.** 재현으로
`twin_pairs.csv`가 **바이트 동일(md5 일치)** 확인 — rgb_s42·depth_s42 2개 체크포인트.
그리고 **헤더 버그는 존재하지 않는다**: 출하된 v2 산출물의 헤더는 `tol 0.15`로 정확히 찍혀 있다.

> **원장 결함 ①의 다리 ②("출하물 헤더가 `1e-06`")는 오인용이다.** 원장이 가리킨
> `runs/{rgb,depth}_s42/twin/twin_analysis.md:4`는 **`mainrun_0819/runs/`(v1 야간 산출물)** 이고,
> `METRICS.md:966`의 "`--tol 1e-6`"는 **구멍 프로브(`probe_holes_0820`)** 를 가리킨다.
> 둘 다 v2 공표 트윈 산출물이 아니다. **3자 불일치는 실재하지 않는다.**

---

## 1. 세 다리 재검증 — 각각 무엇을 말하는가

| 다리 | 실제 내용 | 판정 |
|---|---|---|
| **문서** `mainrun_0819/DECISIONS.md:148` (D20) | "v2 평가부터 트윈 페어링에 `\|Δground_z\|≤0.15m` 허용오차 채택 … **mainrun V0 수치는 불변 보존**" | v2에만 적용, v1은 명시적으로 보존 — 모순 없음 |
| **큐** `mainrun_0819/code/run_queue_v2.sh:126` | `--n-boot $NBOOT --grid $GRID --tol 0.15` (v2 전용 큐) | v2 산출물과 일치 |
| **출하물(v2)** `dayrun_0820/runs/v2/*/twin/twin_analysis.md:5` | **10개 파일 전부 `tol 0.15`** (mtime 08-20 19:20~20:47, 큐 mtime 08-20 18:21보다 뒤) | 큐와 일치 |
| **(오인용) v1 산출물** `mainrun_0819/runs/{rgb,depth}_s42/twin/twin_analysis.md:4` | `tol 1e-06` · manifest `dataset_manifest_v1.json` · **168쌍** · mtime 08-20 02:15 (**D20 16:00 이전**) · `grid:` 줄 자체가 없음(gridspec 도입 이전 코드) | **D20 이전 v1 산출물**. `METRICS.md` §7이 "tol 1e-6"이라 정확히 명기 |
| **(오인용)** `mainrun_0819/METRICS.md:966` | "**Twin analysis** ran at the DEFAULT `--tol 1e-6` … per `PROBE_TABLE.md` §4; files at `probe_holes_0820/eval/<ckpt>/twin/`" | **구멍 프로브 트랙** 서술. `eval_probe.py:240`이 `--tol 1e-6`를 **의도적으로 하드코딩**(PROBE_TABLE §4: "허용오차로 고칠 문제가 아니다") |

원장이 인용한 **`:4`라는 행 번호 자체가 결정적 증거**다. v1 파일은 `grid:` 줄이 없어 tol 줄이 4행,
v2 출하물은 `grid:` 줄이 있어 tol 줄이 **5행**이다. `:4` 인용은 v1 파일만 가리킬 수 있다.

### 1.1 코드 경로 — 헤더는 인자를 찍는다 (하드코딩 아님)

`mainrun_0819/code/twin_analysis.py`:

- `:170` `p.add_argument("--tol", type=float, default=1e-6)` — 기본값 1e-6
- `:179` `build_pairs(..., a.pose_keys.split(","), a.tol, grid)` — **인자가 그대로 페어링 술어로 전달**
- `:56` `[q for q in keys if abs(float(a[q]) - float(b[q])) > tol]` — 술어에서 실제 사용
- `:123` `f"pose keys: \`{a.pose_keys}\` · tol {a.tol:g} · …"` — **헤더도 `a.tol`(인자)을 찍는다**

즉 헤더 값 = 술어 값 = CLI 인자. **헤더가 기본값을 찍는 버그도, 인자가 술어에 도달하지 못하는
경로도 없다.** 헤더에 `1e-06`이 찍힌 파일은 실제로 1e-6으로 돌린 파일이다(= v1 산출물, 프로브 산출물).

---

## 2. 재현 실험 — 출하물은 어느 tol의 산물인가

**입력**: 원본 구-GT 매니페스트 `dayrun_0820/dataset_manifest_v2_full.json` +
원본 점수 덤프 `dayrun_0820/runs/v2/<ckpt>/eval_test/per_frame_{on,off}.csv`
(v2corr 교정 매니페스트가 아니라 **공표 당시 입력**을 사용).

```bash
env CUDA_VISIBLE_DEVICES= PYTHONNOUSERSITE=1 OMP_NUM_THREADS=8 \
  $PYBIN mainrun_0819/code/twin_analysis.py \
  --per-frame-on  dayrun_0820/runs/v2/rgb_s42/eval_test/per_frame_on.csv \
  --per-frame-off dayrun_0820/runs/v2/rgb_s42/eval_test/per_frame_off.csv \
  --manifest dayrun_0820/dataset_manifest_v2_full.json \
  --out <tmp>/tol_{1e-6|0.15} --n-boot 10000 --grid gridspec_v1.json --tol {1e-6|0.15}
```

### 2.1 바이트 대조 (`twin_pairs.csv` md5)

| 체크포인트 | 출하물 | 재현 `--tol 0.15` | 재현 `--tol 1e-6` |
|---|---|---|---|
| rgb_s42 | `5e1a51ae…50b5` | **`5e1a51ae…50b5` ✅ 동일** | `e4354d44…1415` ✗ |
| depth_s42 | `788a1ad3…7f1e` | **`788a1ad3…7f1e` ✅ 동일** | `04f52e3e…6cf7` ✗ |

`twin_analysis.md`도 `--tol 0.15` 재현본과 **출력 경로 1줄을 제외하고 전부 동일**(diff 1 hunk,
`per-pair rows:` 경로 줄만). `--tol 1e-6` 재현본은 **7개 hunk 불일치**.

→ **공표 v2 트윈 산출물의 생성 설정 = `--tol 0.15`. 확정.**

### 2.2 두 tol의 실제 차이 (rgb_s42, 408쌍)

| 항목 | **tol 0.15 (= 출하)** | tol 1e-6 | Δ |
|---|---|---|---|
| kept / excluded | **366 / 42** | 312 / 96 | −54 / +54 |
| GT 보유 kept | 312 | 279 | −33 |
| **V** n · Δ_score | 165 · **0.4422** | 132 · 0.4071 | −33쌍 · **−0.0351** |
| **E** n · Δ_score | 45 · **0.1637** | 45 · 0.1637 | 0쌍 · **±0.0000** |
| **H** n · Δ_score | 96 · **0.1701** | 96 · 0.1701 | 0쌍 · **±0.0000** |
| **all** n · Δ_score | 366 · **0.3103** | 312 · 0.2782 | −54쌍 · **−0.0321** |
| all Δ_frame | **0.3283** | 0.2659 | −0.0624 |
| band1 `[0,2)` | 27 · 0.0883 | 24 · 0.0769 | −0.0114 |
| band2 `[2,5)` | 93 · 0.3675 | 72 · 0.3647 | −0.0028 |
| band3a `[5,8)` | 201 · 0.3504 | 171 · 0.3189 | −0.0315 |
| band3b `[8,12)` | 312 · 0.3133 | 279 · 0.2837 | −0.0296 |
| **band3a H** | 33 · **−0.0486** | 33 · −0.0486 | **±0.0000** |
| **band3b H** | 96 · **0.1850** | 96 · 0.1850 | **±0.0000** |
| scene05 / scene07 / sceneC2 kept | 72 / 30 / 24 | 66 / 6 / **0** | −6 / −24 / −24 |

depth_s42 교차확인: V 0.7756→0.8015(+0.0259, **부호 반대**) · E 0.5741 동일 · **H 0.4131 동일** ·
all 0.6206→0.6145(−0.0061) · all Δ_frame 0.5734→0.5517.

> H·E의 **점추정치가 4소수점까지 동일**한 것은 우연이 아니라 항등이다(§3). CI만 미세하게 다른데
> (H rgb `[0.1237,0.2176]` vs `[0.1243,0.2181]`), 이는 부트스트랩 재추출 인덱스가 kept 길이
> (366 vs 312) 위에서 뽑히기 때문이며 **통계적 결론에 영향 없음**(둘 다 0 배제).

---

## 3. 주장 영향 — D27 항등의 독립 재검증

`DECISIONS.md:199` **D27**: "트윈 허용오차 층(54쌍)에 **H·E 티어 쌍이 0개**".
본 과업에서 매니페스트 원자료로 **독립 재계산**(408쌍 전수, `cam` 5키 직접 대조):

| stratum | n | V | E | **H** | H_weak/none | 씬 |
|---|---|---|---|---|---|---|
| EXACT (`≤1e-6`) | 312 | 132 | 45 | **96** | 39 | s05 66·s07 6·s14 72·s15 72·s18 72·N3 24 |
| **TOL** (`(1e-6, 0.15]`) | **54** | 33 | **0** | **0** | 21 | s05 6 · s07 24 · **C2 24** |
| EXCL (`>0.15`) | 42 | 15 | 0 | 0 | 27 | s07 42 (`\|Δz\|` 3.57 / 4.02 m = 씬 데이텀 변경) |

TOL층 실측 `|Δground_z|` = {0.0012, 0.0015, 0.003, 0.004, 0.0163, 0.0164, 0.1137} m.
**METRICS §N.1 표와 완전 일치** — 재현성 확인.

### 3.1 움직이는 숫자 / 움직이지 않는 숫자

| 공표 주장 | tol 의존성 |
|---|---|
| **H 티어 트윈 Δ** (rgb .285 / depth .407 / b2 .110, METRICS §N.1·N.2, SEED_TABLE §2, RESULTS_DRAFT §N.2) | **tol 무관 — 항등**. TOL층에 H쌍 0개 ⇒ 어떤 tol을 써도 동일한 96쌍. 실측 4소수점 동일 |
| **H 밴드 분해** (3a −0.031 / 3b +0.293, METRICS §N.2) | **tol 무관** (3a 33쌍·3b 96쌍 불변, Δ 동일) |
| **E 티어 Δ** | **tol 무관** (45쌍 불변) |
| RT.2 twin-conditional recall, RT.6 H 픽셀차 감사 (96 H쌍) | **tol 무관** (전량 EXACT층) |
| **all-tier Δ** (SEED_TABLE §2 "twin delta (all)" rgb 0.314 / depth 0.608 / b2 0.234) | **tol 의존**. exact-only 대비 s42 기준 rgb **+0.032** · depth **+0.006**. METRICS §N.1이 3시드 평균 **rgb +0.041 · depth +0.001 · b2 +0.037**로 이미 공표·정량화함 |
| 씬별 트윈 표 (s05/s07/C2 행) | **tol 의존** (C2는 1e-6에서 kept 0 ⇒ n/a) |
| METRICS §7 (v1, 117 kept, tol 1e-6) | 해당 없음 — v1 트랙, 본문이 tol 1e-6로 정확히 명기 |
| METRICS:966 / PROBE_TABLE §4 (구멍 프로브) | 해당 없음 — 설계상 1e-6, 본문이 그렇게 명기 |

**⇒ 움직이는 공표 숫자는 0건.** all-tier 의존성은 이미 METRICS §N.1에 정량 공표되어 있고,
헤드라인(H 티어)은 항등적으로 tol 무관이다. **논문 주장 수정 불필요.**

---

## 4. 잔존 진짜 결함 — per-key 허용오차 부재 (원장 결함 ① 다리 ①은 유효)

`twin_analysis.py:56`은 **스칼라 1개를 5키 전부**에 건다. `--tol 0.15`는 `d`·`h_rel`(m)뿐 아니라
`yaw`·`pitch`(**deg**)에도 0.15를 허용한다 — 단위가 섞인 잠재 결함.

**본 코퍼스에서의 실측 영향 = 정확히 0.**

| 키 | 408쌍 최대 `\|Δ\|` | `>1e-6`인 쌍 수 |
|---|---|---|
| `d` | **0.0** | 0 |
| `h_rel` | **0.0** | 0 |
| `yaw` | **0.0** | 0 |
| `pitch` | **0.0** | 0 |
| `ground_z` | 4.0186 | 96 |

`d/h_rel/yaw/pitch`는 "0.15 미만"이 아니라 **정확히 0.0**이다(같은 카메라 바이트).
따라서 스칼라 tol이 이 4키에 허용을 부여해도 **회복되는 쌍이 구조적으로 없다** —
결함은 **잠재적(latent)**이며 공표 숫자에 관여하지 않는다. 단, v3에서 카메라 재추첨을
도입하면 즉시 실효 결함이 된다.

---

## 5. 시정 조치

| # | 조치 | 대상 | 상태 |
|---|---|---|---|
| **A** | **원장 정정**: `ASSUMPTION_LEDGER.md` 결함 ① / `LAB-13` / N-1의 "출하물 헤더 `1e-06`" 다리는 **오인용**(v1 산출물·프로브 산출물을 v2 출하물로 오독). "생성 설정 확정 불가" 서술 철회 → **`--tol 0.15` 확정, 바이트 재현 완료**로 교체 | `v3_0823/ASSUMPTION_LEDGER.md` | **필요 · 본 과업 범위 밖(원장 소유 트랙이 반영)** |
| **B** | **per-key 허용오차 도입** — v3 `twin_analysis.py`에서 `--tol`을 `key=value` 목록으로 파싱(`ground_z=0.15`, 나머지 `1e-6`). 구 코퍼스 재현성은 `--tol 0.15` 단일값 하위호환 유지 | v3 코드 | 권고 |
| **C** | **산출물 헤더에 출처 각인 추가** — 현재 헤더에는 manifest·grid·tol·seed는 있으나 **코드 버전/실행 시각이 없어** v1/v2 산출물이 경로로만 구분된다. 이번 오인용의 직접 원인. v3 헤더에 `code rev` + `generated at` 추가 | v3 코드 | 권고 |
| **D** | **각주 1건**(선택) — `SEED_TABLE.md` §2 "twin delta (all)"이 kept의 정의(tol)를 명시하지 않는 유일한 공표 표. 아래 초안 삽입 권고. **숫자 변경 아님** | `dayrun_0820/runs/v2/SEED_TABLE.md` §2 | 초안 제공, **본 과업에서 편집 안 함** |

### 5.1 각주 Z 초안 (SEED_TABLE §2 / 트윈 all-tier 인용부, 한국어)

> **각주 Z.** 본 표의 `twin delta (all)`은 D20 포즈 허용오차 `|Δground_z| ≤ 0.15 m`로 페어링한
> **kept 366쌍** 기준이다(출하 산출물 `runs/v2/<ckpt>/twin/twin_analysis.md` 헤더 `tol 0.15`;
> 08-23 재현에서 `twin_pairs.csv` 바이트 동일 확인, `v3_0823/TWIN_TOL_RESOLUTION.md`).
> 허용오차 층 54쌍은 전부 V(33)·H_weak/none(21)이므로 **H·E 티어 값은 tol과 무관하며**,
> exact-only(1e-6, 312쌍) 재계산에서 H Δ가 4소수점까지 동일하다(s42: rgb 0.1701 · depth 0.4131).
> 반면 `all` 열은 허용오차 층을 포함하므로 exact-only 대비 3시드 평균 rgb +0.041 · depth +0.001 ·
> b2 +0.037 높다(METRICS §N.1). `mainrun_0819/runs/*/twin/twin_analysis.md`(헤더 `tol 1e-06`)는
> **D20 이전 v1 산출물**, `probe_holes_0820/eval/*/twin/`(동일 표기)은 **설계상 1e-6인 구멍 프로브**로,
> 둘 다 본 표와 무관하다.

### 5.2 Footnote Z draft (English, for the paper)

> **Footnote Z.** `twin delta (all)` is computed over the **366 pairs kept under the D20 pose
> tolerance `|Δground_z| ≤ 0.15 m`** (shipped headers read `tol 0.15`; byte-identical reproduction
> 2026-08-23). The 54 tolerance-rescued pairs are all V (33) or H_weak/none (21), so **the H- and
> E-tier values are tolerance-invariant** — recomputed exact-only (1e-6, 312 pairs) the H-tier Δ is
> identical to four decimals. The `all` column is not: it exceeds the exact-only value by
> rgb +0.041 / depth +0.001 / b2 +0.037 (3-seed means, §N.1). Artifacts stamped `tol 1e-06` under
> `mainrun_0819/runs/` are the **pre-D20 v1 run**, and those under `probe_holes_0820/eval/` are the
> **hole probe, which uses 1e-6 by design**; neither feeds this table.

---

## 6. 재현 산출물

- 재현 출력(임시, 비영구): `<scratch>/twin_tol/{tol_1e-6, tol_0.15, d_tol_1e-6, d_tol_0.15}/`
- 재현 명령 §2 · 층화 감사 스크립트 로직 §3(매니페스트 `cam` 5키 직접 대조, 408쌍 전수)
- 대조 대상(무편집): `dayrun_0820/runs/v2/{rgb,depth}_s42/twin/twin_{analysis.md,pairs.csv}`
