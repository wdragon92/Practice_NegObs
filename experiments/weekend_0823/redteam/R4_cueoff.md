# R4_cueoff — 레드팀 4파 (주말 중심 결과 = CUE-OFF 개입 공격)

작성 2026-08-23 · 감사자 RED TEAM R4 (Opus, 독립 재계산) · 작업방 `experiments/weekend_0823/redteam/`

읽은 것: `cue_audit/{CUEOFF_RESULT.md, PREREG_CUEOFF.md + A1, GATES_CUEOFF.md, readout_cueoff.py,
gates_cueoff.py, SMOKE_CUEOFF.json, split_cueoff.json, CKPT_HASHES.json}` ·
`cue_audit/scenes_cueoff/scene12_riverside_deck.py`(팔 C 포팅 전문) ·
`mainrun_0819/DECISIONS.md` D36·D42·D44·D46(+D48) · `gazebo/GAZEBO_TRACK.md` ·
`rt_response/F7_HPAIR_PIXDIFF.md`

**감사 방식**: 문서를 옮겨 적지 않았다. `cue_audit/labels/*.json` 30개와
`cue_audit/eval/*/per_frame.csv` 270개를 직접 재집계했고, **사전등록 §3의 픽셀 질량 주장을
실제 렌더 프레임에서 다시 쟀다**(`redteam/r4_pixdiff.py`, 456컷 전수, CPU 4분).
사전등록이 CPU AABB 상한값으로 매긴 등급을 실물이 뒷받침하는지가 이 감사의 축이다.

---

## 0. 한 줄 결론

> **판정(SHORTCUT / UNDECIDED)은 살아남는다. 그 판정을 떠받치는 논증은 살아남지 못한다.**
>
> 사전등록 §3이 플라시보에 매긴 정합성 등급 **4개가 4개 다 실측과 어긋나고**, 그중 3개는
> **반보수 방향**이며, 하나(scene20)는 **멀쩡히 존재하는 최적 정합 대조군을 "0 px"이라며 버렸다**.
> 개입의 대전제인 "strict-H = 위험이 안 보인다"는 실측이 부정한다 — **위험만 지워도
> 프레임의 6.6–13.6 %가 바뀐다**(잡음 바닥의 1.7만–13.7만 배). 그리고 주말 헤드라인인
> **arm-C FA 1.000은 단서 어휘 수가 아니라 씬별 arm-C 수술의 광학 크기를 정확히 따라간다**
> (36.6 % → FA 1.00 · 13.1 % → 0.36 · 1.0 % → 0.04).
>
> 반대로, 이 감사에서 **더 강해진 것도 있다**: 계보 off 라운드의 FA가 `per_frame.csv` 안에
> 이미 들어 있고(scene12 rgb **.028** / b2 **.000**), 그것을 실으면 H2의 scene12 대비가
> **.028 → 1.000** 으로 훨씬 선명해진다. 문서가 그걸 안 실었을 뿐이다.

---

## 1. 실측 근거표 — 팔 간 실제 픽셀 질량 (전수 24컷, 임계 ≥32/255)

임계는 F7 결론을 그대로 따랐다(`F7_HPAIR_PIXDIFF.md` §0: 2/255는 렌더러 잡음이라
동일 기하 두 렌더에서 프레임의 44 %가 뒤집힌다). 재현: `python3 redteam/r4_pixdiff.py 24`.

**잡음 바닥 (팔 A vs 계보 정본 on — 같은 기하, 다른 렌더 호출)**

| 씬 | px ≥32 | 프레임 비 |
|---|---|---|
| scene12 | **8** | 0.0004 % |
| scene17 | **272** | 0.013 % |
| scene20 | **1** | 0.00005 % |

> **게이트 G0은 훌륭하게 통과한다.** 격리 사본은 결백하고, 아래 모든 비율은 이 바닥 위에서
> 최소 1,000배 이상이므로 전부 실신호다. 이건 이 개입에서 가장 잘 된 부분이니 논문에 써도 된다.

**팔별 광학 질량 (판정에 쓰인 프레임 한정 · scene20은 strict-H 6컷)**

| 씬 | A vs B1 | A vs B2 | A vs P | A vs C |
|---|---|---|---|---|
| scene12 | 721,912 (**34.81 %**) | 110,667 (5.34 %) | 64,012 (3.09 %) | 137,588 (6.64 %) |
| scene17 | 616,553 (**29.73 %**) | — (팔 없음) | 342,269 (16.51 %) | 281,017 (13.55 %) |
| scene20 | 671,123 (**32.37 %**) | 173,690 (8.38 %) | **157,834 (7.61 %)** | 232,132 (11.19 %) |

**팔 vs 계보 off 라운드 (전 24컷)**

| 씬 | A vs off | B1 vs off | **C vs off** |
|---|---|---|---|
| scene12 | 39.58 % | 44.23 % | **36.60 %** |
| scene17 | 12.72 % | 34.55 % | **1.02 %** |
| scene20 | 24.89 % | 23.36 % | **13.09 %** |

---

## 2. 발견 — 심각도순

### F1 [CRITICAL] 사전등록 §3의 플라시보 정합성 등급 4/4가 실측과 어긋난다 (3건 반보수)

| 씬·레그 | PREREG §3 주장 | 실측 비(≥32/255) | 판정 |
|---|---|---|---|
| s12 P vs B2 | "플라시보가 **12–30× 크다 → 보수적**" (§3.1) | 64,012 / 110,667 = **0.58×** | **역전**. 플라시보가 1.7× **작다** |
| s12 P vs B1 | "플라시보가 ~3.2× 작다 → 반보수" (§3.1) | 64,012 / 721,912 = **0.089×** | 반보수가 **3.5× 더 심함**(11.3× 작다) |
| s17 P vs B1 | "플라시보가 ~**18× 크다 → 강하게 보수적**" (§3.2, A1.2-2가 이걸 근거로 s17을 **1차 다리로 승격**) | 342,269 / 616,553 = **0.56×** | **역전**. 플라시보가 1.8× **작다** |
| s20 P | "메사 가구 전부 화면 밖, **6/6 H 프레임에서 0 px** → 플라시보 불능"(§3.3) | 같은 6컷에서 **157,834 px (7.61 %)** | **사실 아님.** 그리고 P/B2 = **0.91×** = 본 연구 **최고 정합** |

**왜 틀렸나.** `pixel_mass.py`는 월드 AABB를 카메라로 투영한 **실루엣 면적 상한**이다.
제거된 물체가 만들던 **그림자·AO·GI 바운스·셰이딩**을 세지 않는다 — F7 §0이 이미
"트윈은 자기 실루엣보다 훨씬 많이 지운다"고 코퍼스에서 실증했는데, 그 교훈이 이 사전등록에
반영되지 않았다. s12 난간은 실루엣 6.3 k px로 추정됐지만 실물은 **110.7 k px**을 바꾼다(17.6×).

s20은 셰이딩만으로 설명이 안 된다(7.61 %). **조명 조건 분해로 확인했다**:
L0 8.62 % · L5 9.21 % · L7 8.85 % — 조명 의존이 없다(전부 주간, 평균 휘도 152–184).
즉 발광체 제거가 아니라 **불투명체가 실제로 화면 안에 있다**. `pixel_mass.py`의 s20
카메라 기저/부호가 의심된다(D39가 `sites.csv` azimuth 부호 반전을 이미 잡은 전례).

**영향 범위 (정직하게).** SHORTCUT 가지는 판정식에 플라시보가 **들어가지 않으므로**
(§4.3: `Δ_cue < 0.10 ∧ 3/3 동부호`) **어떤 SHORTCUT 판정도 뒤집히지 않는다.**
무너지는 것은 (a) "보수적으로 통제했다"는 **서술 전체**, (b) 1차/2차 레그 선택의 근거(§8-3이
잠근 것이 지금 거짓 전제 위에 서 있다), (c) **s20 배제 결정**(→ F14).

---

### F2 [CRITICAL] 개입의 대전제가 실측에 의해 부정된다 — strict-H 프레임에서 위험만 지워도 6.6–13.6 %가 바뀐다

`A vs C`는 이 코퍼스가 가진 **가장 깨끗한 "위험만 제거" 대비**다(팔 C = 위험 off, 나머지 유지).

| 씬 | A vs C, px ≥32 | 프레임 비 | 그 씬 잡음 바닥의 배수 |
|---|---|---|---|
| scene12 | 137,588 | **6.64 %** | ×17,199 |
| scene17 | 281,017 | **13.55 %** | ×1,033 |
| scene20 | 232,132 | **11.19 %** | ×232,132 |

그런데 이 프레임들은 **전부 strict-H**로 라벨돼 있다(`per_frame.csv` tier 집계:
scene12 24/24 H · scene17 24/24 H · scene20 6 H). strict-H의 정의는
`int_px == 0 ∧ edge_vis == 0` — **위험 프리즘이 0픽셀로 재투영된다**는 뜻이다.

> **위험이 0픽셀인데 위험을 지우면 프레임의 13.5 %가 바뀐다.** 이건 모순이 아니라
> F7이 이미 말한 것(§1 "strict-H는 이 코퍼스에서 광학적으로 비어 있던 적이 없다",
> test 셋 중앙값 4.51 %)의 **CUE-OFF 판이며, 크기가 2.8–3.0× 더 크다.**

**왜 치명적인가.** CUE-OFF의 논리 전체가 "strict-H에서는 위험이 안 보이니, 발화한다면
그건 단서를 읽은 것"이라는 전제 위에 서 있다(`PREREG_CUEOFF.md` §0). 그 전제가 틀렸으면
- 팔 C는 "보이지 않는 것 하나를 뺀 같은 그림"이 아니라 **다른 그림**이고,
- 팔 C의 FA는 "단서만으로 발화"가 아니라 **"내용의 6.6–13.6 %를 잃은 그림에서의 발화"**이며,
- 반대로 **SHORTCUT 판정은 오히려 더 강해진다** (→ §5 반론에서 쓴다).

---

### F3 [CRITICAL] arm-C FA는 단서 어휘가 아니라 arm-C 수술의 광학 크기를 따라간다

| 씬 | C vs off 광학 질량 | **FA(off) rgb/b2** | **FA(C) rgb/b2** | 사전등록 H2 임계 0.40 |
|---|---|---|---|---|
| scene12 | **36.60 %** | .028 / .000 | **1.000 / 1.000** | 통과 |
| scene20 | **13.09 %** | .250 / .125 | **.361 / .181** | 불통과 |
| scene17 | **1.02 %** | .014 / .014 | **.042 / .056** | 불통과 |

세 점이 질량에 대해 완전 단조다. 단서 어휘 수는 이 순서를 만들지 않는다 —
scene17의 팔 C도 **드레싱 어휘를 전부 보존**한다(가로등 폴·km 표지·far_side).

**원인은 포팅 구현이다.** 세 씬의 팔 C는 서로 **다른 세 가지 수술**이다(사전등록 §6이 정직하게
그렇게 적어 뒀다 — 데이텀 보존 때문에 불가피했다):

| 씬 | 팔 C가 부르는 채움 | 결과 |
|---|---|---|
| scene12 | **전용 `build_cueoff_fill`** — 데크·지형·ground_kit을 팔 A와 **똑같이** 부르고 x ≥ 0만 채움 | C가 **A에서 6.6 %밖에 안 떨어져 있다** (off에서는 36.6 %) |
| scene17 | **정본 `build_flat_fill` 그대로**(§6.2) — off 라운드와 **같은 채움** | C가 **off에서 1.0 %밖에 안 떨어져 있다** |
| scene20 | `build_flat_fill` + 밴드 재건(§6.3) | 중간 (13.1 %) |

즉 **scene12 팔 C ≈ 팔 A** (`A vs C` 6.64 %), **scene17 팔 C ≈ off 라운드** (`C vs off` 1.02 %).
모델이 A에서 recall 1.000으로 발화하므로 C에서 1.000이 나오는 것은 **동어반복에 가깝고**,
scene17에서 off와 구별 못 하는 것도 마찬가지다. **FA 1.000이 측정한 것은 단서 어휘가 아니라
"scene12의 팔 C가 팔 A와 거의 같은 그림"이라는 사실이다.**

추가로 **scene12 팔 C의 드레싱은 1.36 m 들어 올려진다**
(`scene12_riverside_deck.py:2066` `lz = 0.0 if KEEP_DRESSING else lo["z_top"]`):
자전거도로·**백선 2줄**·하부 벤치·**갈대 3·5번 밴드**가 z=0으로 올라오고, 갈대 1·2·4번 밴드는
호안(−1.75)에 남는다 → **갈대 스탠드가 두 높이로 쪼개진, 어떤 팔·어떤 훈련 프레임에도 없는 배치**다.
백선은 `lz + 0.005`, 즉 **카메라 눈높이 지면에 5 mm 띄운 고대비 백색 선**이 되는데,
이건 매트릭스가 `signage_or_marking` 단서로 읽는 바로 그 형태의 **팔 A보다 더 가깝고 더 강한 판**이다.
"같은 단서 어휘를 보존했다"는 서술은 이 팔에 대해 성립하지 않는다.

**H2 판정 정정.** 사전등록 §4.4는 "FA ≥ 0.40이면 비-test 재현으로 인정"이라 했고,
3씬 중 **scene12만** 통과한다. 그리고 scene12는 (i) GT가 50셀 조각(A1.1), (ii) G2 규정 위반
3건(F4), (iii) `_solid_at` 오라클을 손으로 고친 씬(§6.1), (iv) 팔 C가 유일하게 전용 채움을
쓰는 씬이다. **H2의 근거는 이 연구에서 계측이 가장 오염된 단 하나의 씬이다.**

---

### F4 [CRITICAL] 사전등록 무효조건 §4.5-2 위반 — G2 8건 실패인데 s12·s20을 판정했다

`GATES_CUEOFF.md`: **FAIL 8**, 전부 G2 (`heightmap.npy differs — a cue_* toggle moved the hazard
geometry. REGULATION BREACH`) — s12 B1/B2/P × 2밴드, s20 B1/B2.
`PREREG_CUEOFF.md` §4.5-2: **"`polar_gt` 바이트 동일성(G2) 실패 → 그 씬은 판정하지 않는다."**

- **`CUEOFF_RESULT.md`는 G2를 단 한 번도 언급하지 않는다** (`grep -n "G2\|breach\|위반"` → 0건).
- 진행 근거는 **D44 하나**인데, D44가 검사한 것은 **8건 중 1건**(s12 P-vs-A, 42셀,
  소품 자리 ±2 mm)이다. 나머지 7건 — 특히 **s20 B2**(치크월 절제 = 위험에 인접한 구조물,
  사전등록 §4.2가 "계단 픽셀 노출 가능성"을 예견한 바로 그 팔) — 은 **개별 근거 없이
  같은 판정을 상속받았다.**
- **라벨 파일이 D44를 직접 반박한다.** `labels/lineage__260823_cueoff_*__scene20.json`
  프레임당 평균 양성 셀:

  | 팔 | A | P | **B1** | **B2** |
  |---|---|---|---|---|
  | scene20 | 1.50 | 1.50 | **1.62** | **1.62** |

  **B1·B2가 A보다 GT 양성 셀이 8 % 많다.** 즉 `recall_H(A)`와 `recall_H(B)`는
  **서로 다른 채점표로 계산됐다.** §4.5-2가 존재하는 이유가 정확히 이것이다.
  (s12는 lineage 4팔 모두 1.31로 동일 → s12 G2는 D44 말대로 오탐일 가능성이 높다.
  문제는 s20이다.)

---

### F5 [HIGH] 게이트 G4·G5·G7이 실행된 적이 없다 (그런데 결과표는 그 산출물을 인쇄한다)

타임스탬프:

```
GATES_CUEOFF.md                          05:24:12
labels/lineage__260823_cueoff_A__s12.json 05:51:27
EVAL_DONE / CUEOFF_RESULT.md              06:03:26
```

`GATES_CUEOFF.md` 노트: `G4: labels for ... absent -- skipped` ×10 ·
`G5: labels for ..._C absent -- skipped` ×2 · `G7: no label file yet`.
**게이트는 라벨보다 27분 먼저 돌았고, 다시 돌지 않았다.**

- **G5**(팔 C polar_gt 전영)는 §6.1이 손으로 고친 `_solid_at` hazard-blind 함정을
  **기계로 확인하는 유일한 장치**였다. 미실행.
  (내가 라벨에서 대신 확인했다: 팔 C 평균 양성 셀 = 0.00, 3씬 2세트 전부 → **G5는 사후적으로 통과**.
  단, `twin` 세트의 C는 자기 자신이 기준면이라 0이 **구성적**이므로 공허하다.)
- **G4**(티어 재도출 + **H→E 이동 프레임 수 보고**)는 §4.2가 **의무**로 못 박은 항목이다.
  미실행인데 `CUEOFF_RESULT.md`의 모든 행에 `tier migration | none`이 인쇄돼 있다.
- **G7**(발자국 건전성 + `cells_raw < 1000` **DEGENERATE 딱지를 보고서 상단에 인쇄**, A1.2-3)
  미실행. 보고서 상단에 딱지가 없다(섹션별 캐비앗만 있다).

사전등록 §5: "하나라도 실패 = **중단·기록·롤백**". 3개는 실패도 통과도 아닌 **미평가** 상태로
평가 체인이 진행됐다.

---

### F6 [HIGH] SHORTCUT 가지에 검정력이 없다 — 5건 전부 D = (0, 0, 0)

`CUEOFF_RESULT.md`의 SHORTCUT 판정 5건(lineage 1차)은 **예외 없이 Δ = +0.000, +0.000, +0.000**이다.
그 셀들의 `R_A`도 대부분 **1.000**(포화)이다.

- paired-H **24프레임에서 0회 뒤집힘**의 단측 95 % 상한 = `1 − 0.05^(1/24)` = **0.117**.
  사전등록 SHORTCUT 임계는 **0.10**. **데이터가 자기 임계를 분해하지 못한다.**
  시드는 같은 24프레임을 세 모델로 볼 뿐이라 프레임 정보를 늘리지 않는다(풀링 부적절).
- 즉 SHORTCUT 5건은 "H0을 지지하는 증거"가 아니라 **"이 표본으로는 0.117 이하 효과를 못 잰다"**이다.
  사전등록 §4.3이 선언한 최소검출효과 0.10보다 **실제 분해능이 나쁘다**.
- `readout_cueoff.py:184` `same_sign()`은 `all(x == 0)`을 **True**로 돌린다. 즉 **(0,0,0)이
  "3/3 시드 동부호"로 계상된다.** 0은 부호가 아니다. 이 구현 결정은 사전등록에 없고,
  **SHORTCUT 5건 전부가 이 결정에 의존한다.**

---

### F7 [HIGH] 결정적 대조군이 데이터 안에 이미 있는데 보고서에 한 줄도 없다

`eval/*/260823_cueoff_C/<scene>/<model>_s<seed>/per_frame.csv`에는 `toggle_state = off` 행 24개가
**같이 들어 있다** — 계보 off 라운드(위험 off + **드레싱도 off**)다. 이게 팔 C의 진짜 바닥이다.
내가 직접 집계했다(τ=0.5, GT 전음 프레임에서 어떤 셀이든 발화):

| 씬 | model | **FA(off)** s42/s43/s44 | **FA(C)** s42/s43/s44 | 차 |
|---|---|---|---|---|
| scene12 | rgb | 1/24 · 1/24 · 0/24 (**.028**) | 24/24 · 24/24 · 24/24 (**1.000**) | **+0.972** |
| scene12 | b2 | 0/24 · 0/24 · 0/24 (**.000**) | 24/24 · 24/24 · 24/24 (**1.000**) | **+1.000** |
| scene12 | depth | 0/24 (**.000**) | 12/24 · 12/24 · 0/24 (**.333**) | +0.333 |
| scene17 | rgb | 0/24 · 1/24 · 0/24 (**.014**) | 0/24 · 3/24 · 0/24 (**.042**) | +0.028 |
| scene17 | b2 | 1/24 · 0/24 · 0/24 (**.014**) | 3/24 · 0/24 · 1/24 (**.056**) | +0.042 |
| scene20 | rgb | 0/24 · **16/24** · 2/24 (**.250**) | 2/24 · 24/24 · 0/24 (**.361**) | +0.111 |
| scene20 | b2 | 5/24 · 1/24 · 3/24 (**.125**) | 11/24 · 2/24 · 0/24 (**.181**) | +0.056 |

**두 방향으로 중요하다.**
① **보고서에 유리한 쪽**: scene12의 H2 대비가 "FA 1.000"이 아니라 **".028 → 1.000"**이 된다.
   훨씬 강한 문장이고, "모델이 원래 아무 데나 발화한다"는 리뷰어 반론을 즉사시킨다. 왜 안 실었나.
② **불리한 쪽**: scene17에서 **전 단서 어휘를 보존해도 FA가 .014 → .042**, 즉 **효과 없음**.
   그리고 scene20 rgb의 FA는 **off 라운드에서도 s43만 16/24**로 튀는 **시드 43의 개성**이다.
   → H2는 3씬 중 1씬에서만 성립한다(F3과 같은 결론에 독립 경로로 도달).

---

### F8 [HIGH] B1 붕괴는 질량과 분리되지 않는다 — 어떤 씬에도 B1에 정합된 플라시보가 없다

최대 정합비가 **s17의 0.56×**다. 사전등록 §3의 요건("비슷한 픽셀 질량")을 **B1에 대해서는
세 씬 어디서도 충족하지 못한다.**

rgb의 ΔR을 제거 질량에 대해 늘어놓으면:

| 팔 | 제거 질량 (≥32) | rgb mean ΔR |
|---|---|---|
| s12 P | 3.09 % | +0.000 |
| s12 B2 | 5.34 % | +0.000 |
| s17 P | 16.51 % | +0.000 |
| s17 B1 | 29.73 % | +0.111 |
| s12 B1 | 34.81 % | **+0.375** |

**단조다.** 30 % 부근에서 문턱이 열리고, 그 아래는 전부 0이다. b2도 같은 모양이다
(s12 P 3.09 % → +0.222 · s12 B1 34.81 % → +0.972).
"단서라서 무너졌다"를 지지하려면 **같은 질량의 비단서 제거가 무너뜨리지 않음**을 보여야 하는데,
그 실험(≈600 k px 비단서 플라시보)은 **존재하지 않는다**.

잔차는 있다: s17 B1(29.73 %)이 +0.111인데 s12 B1(34.81 %)은 +0.375다(3.4× 차이).
그러나 그 잔차는 **"씬"과 "어느 단서"가 완전 교란**돼 있어 귀속 불가다.
→ **사전등록 §3.1의 "B1 레그는 결정적 증거로 승격 금지"는 옳았다. D46의 헤드라인 문장이
그 규율을 어겼다**(→ F11 계열, §4-5 참조).

---

### F9 [MEDIUM] 인과 주장 전체가 모델이 적합된 씬 위에 서 있다

사전등록 §2.1: scene12 **train** · scene17 **train** · scene20 **val**. **test 씬 0.**
(s14가 유일한 test 후보였으나 가드가 구조물이라 토글 불가 — D36.)
동결 모델은 s12·s17을 학습했다. "훈련 씬의 외양을 크게 흔들면 recall이 무너진다"는
**암기 붕괴로도 똑같이 설명된다.** `CUEOFF_RESULT.md`에는 이 문장이 없다.
(부수적으로 `split_cueoff.json`은 3씬을 전부 `"test"`로 적어 놓아, 산출물 경로가
`260823_cueoff_A/test/scene12/`가 됐다. 추론에는 무해하나 독자를 오도한다.)

### F10 [MEDIUM] scene12가 판정 census에 두 번 계상된다
`260823_cueoff`(boost_e)와 `260823_cueoff2`(boost_e2)는 **같은 씬의 두 밴드**인데
결과 문서에서 **독립된 두 행**으로 취급된다. lineage 1차 12셀 중 **6셀이 scene12**다.
"UNDECIDED 다수"라는 census는 이 중복 위에서 계산됐다.

### F11 [MEDIUM] A1.2-1("두 라벨 세트 결론이 갈리면 판정 불가") 미적용
s12 rgb: `lineage` **SHORTCUT** vs `twin` **UNDECIDED**(2밴드 모두). 두 세트가 갈렸는데
lineage 쪽 SHORTCUT이 그대로 서 있다. (UNDECIDED를 "결론 없음"으로 보면 방어 가능하나,
그 해석을 **문서에 명시**해야 한다.)

### F12 [MEDIUM] Gazebo 교차-시뮬 "재현" 주장은 성립하지 않는다 (→ §4-4에서 상술)

### F13 [LOW · 긍정] G0 / 격리 / 동결은 결백하다
A vs 정본 on = **8 / 272 / 1 px** ≥32. `CKPT_HASHES.json` 9개 sha256 기록됨.
정본 씬 파일 무접촉, 격리 사본만 수정. **이 부분은 방어 가능하고 논문에 써도 된다.**

### F14 [MEDIUM · 건설적] scene20을 되살리면 이 연구 유일의 정당한 CUE EVIDENCE 후보가 나온다
F1대로 s20의 플라시보는 **존재하고**(7.61 %) **B2에 0.91× 정합**된다 — 본 연구 최고 정합.
그 값을 §4.3 판정식에 넣으면 s20 **b2**:

```
Δ_cue(A,B2)   = +1.000, +0.667, +0.667
Δ_placebo(A,P)= +0.000, +0.000, +0.333
Δ−Δ           = +1.000, +0.667, +0.334   mean +0.667 ≥ 0.15, 3/3 동부호  → CUE EVIDENCE
```

**막는 것은 단 하나, paired-H = 6 < 10 (§4.5-3 VOID)뿐이다.**
→ **최우선 후속: scene20을 `--cams` 확대(또는 조건 추가)로 재렌더해 paired-H ≥ 10을 만든다.**
GPU 20분이면 이 연구가 **사전등록 1차 판정에서 처음으로 CUE EVIDENCE를 낼 수 있다.**

---

## 3. 판정 census 재집계 (독립 재계산)

| 라벨 세트 | CUE EVIDENCE | SHORTCUT | UNDECIDED | (그중 VOID) |
|---|---|---|---|---|
| `lineage` 1차 (12셀) | **0** | 5 | 7 | 3 |
| `twin` 1차 (12셀) | **0** | 3 | 9 | 9 |
| 2차 B1 레그(승격 금지) | 3 (전부 scene12) | — | — | — |

> **사전등록된 1차 판정식에서 CUE EVIDENCE는 0건이다.** 3건의 CUE EVIDENCE는 전부
> (a) 2차 레그이고 (b) 반보수 정합이며 (c) scene12(퇴화 GT)에서 나왔다. 규칙대로 비승격 처리된 것은
> **옳다.** D46이 그것을 지킨 것은 이 연구의 가장 큰 미덕이다.

---

## 4. 공격선별 답변

### 4-1. arm-C FA 1.000은 keep_dressing 구현 아티팩트인가? — **상당 부분 그렇다**

**아티팩트 쪽 증거**: ① 3씬의 팔 C는 **세 가지 다른 수술**이고 FA는 수술의 광학 크기와
완전 단조다(F3). ② scene12 팔 C는 **팔 A에서 6.64 %밖에 떨어져 있지 않다** — A에서 recall 1.000인
모델이 C에서 1.000을 내는 건 놀랍지 않다. ③ 팔 C가 드레싱을 **1.36 m 들어 올려**
갈대 스탠드를 두 높이로 쪼개고 백선을 눈높이 지면에 올린다 = **훈련 분포에 없는 배치**.
④ 팔 C를 검증할 유일한 게이트 **G5가 실행되지 않았다**(F5).
⑤ 데이텀 논증(§6.1)은 **카메라 z만** 보장한다 — 그림 내용의 동일성은 보장하지 않는다.

**아티팩트가 아닌 쪽 증거(정직하게)**: ① 계보 off 대비 **.028 → 1.000**은 실재하고 크다(F7).
② 팔 C의 GT는 3씬 2세트 전부 **평균 양성 셀 0.00** — 하자드가 정말로 남지 않았다(사후 G5 통과).
③ 잡음 바닥이 8 px이므로 계측 자체는 신뢰할 수 있다.

**결론**: "**단서 어휘만으로 발화한다**"는 **증명되지 않았다**. 증명된 것은
"**scene12에서 위험을 제거해도 모델은 100 % 발화한다 — 위험 제거가 프레임을 6.6 %밖에
바꾸지 않기 때문에**"다. 이건 여전히 좋은 결과지만 **다른 문장**이고, 논문은 그 문장을 써야 한다.

### 4-2. B1 붕괴는 픽셀 질량 교란인가? s12는 해석 가능한가? — **분리 불가. s12는 해석 불가**

s17은 **18× 보수적이 아니라 0.56× 반보수적**이다(F1) → "s17이 질량을 통제한다"는 방어선이
**사라진다**. s12는 원래부터 반보수 선언(3.2×)이었고 실측은 **11.3×**로 더 나쁘다.
rgb·b2 모두 ΔR이 제거 질량의 단조 함수로 설명 가능하고(F8), 질량 정합된 반증 실험이 없다.

> **s12 B1 효과는 현재 설계에서 해석 불가다.** 사전등록이 그렇게 선언했고, 그 선언이 옳다.
> 다만 **`Δ_placebo`가 두 씬에서 정확히 0.000이라는 사실**은 별개의 가치가 있다 —
> **프레임의 16.5 %(s17 P)를 지워도 recall_H가 한 프레임도 안 바뀐다**는 것은
> 이 지표의 **질량 무감성**을 보여주는 강한 관측이다. 이건 살릴 수 있다(→ §5 반론).

### 4-3. UNDECIDED 다수 = 출판 불가인가? — **아니다. 단, 지금의 중심 문장으로는 불가**

→ §5에 리뷰어 문단과 반론 문단을 각각 최강으로 썼다.

### 4-4. Gazebo 교차-렌더러 수렴은 건전한가? — **아니다 (주장 축소 필요)**

| # | 문제 | 근거 |
|---|---|---|
| a | **단서-무 대조 월드가 없다** | ctrl 4종 전부 "위험만 제거 + 단서 보존". FA에 **바닥이 없다**. CUE-OFF는 바닥이 있는데(계보 off, F7) Gazebo는 없다 → 두 트랙이 같은 결함을 공유. **같은 교란을 두 번 재현한 것은 독립 확증이 아니다** |
| b | **단서-용량 반응이 없다** | 내가 `out/gazebo_zeroshot.csv` 432행을 재집계: ctrl 팔 발화율 b2 = drop1 **.714** / drop2 **.857** / drop3 **.905** / drop4 **.810**, rgb = .333 / .381 / .524 / .381. **경고블록이 없는 drop2(.857)와 전 단서 보유 drop3(.905) 차이가 1프레임(21컷 중)**이다. 반면 시드 간 산포는 rgb .214–.571 → **시드 산포 > 월드(단서) 산포** |
| c | **비교 상대를 최대값으로 골랐다** | §4.4가 대는 CUE-OFF 대조선은 **scene12의 1.000**뿐이다. scene17(.042)·scene20(.361)을 나란히 놓으면 "방향이 같다"가 성립하지 않는다 |
| d | **문서 내부가 모순** | §0은 "다른 시뮬레이터에서 **독립적으로 재현**", §7-2는 "트윈 Δ 붕괴를 **전부** 단서로 돌리면 안 된다 · Gazebo 피트는 균일한 검은 면이라 기하 증거 자체가 빈약". D48은 §0 쪽을 채택했다 |
| e | 표본 | 월드당 팔당 **21프레임**, 뷰당 3장 중 **1장만** 사용, 불확실성은 시드 3개뿐 |

**살아남는 Gazebo 문장(이것만 써야 한다)**:
> "위험 기하가 **0픽셀**인 `gz_drop3`에서 rgb는 절반, b2는 열에 아홉 프레임에서 발화한다
> (§3의 누수 검사로 0픽셀을 실증했다). 그리고 티어 사다리가 6/6 모델에서 뒤집힌다."
**쓰면 안 되는 문장**: "단서-단독 발화가 교차-렌더러로 재현됐다"(= b·c에 의해 지지되지 않음).

### 4-5. 사전등록 위반 목록 (승격/강등 절차)

| # | 조항 | 위반 내용 | 심각도 |
|---|---|---|---|
| V1 | §4.5-2 | G2 실패 8건 중 7건이 **개별 근거 없이** D44의 1건 판정을 상속. s20 라벨은 A(1.50) vs B1/B2(1.62)로 **실제로 다르다** | **CRITICAL** |
| V2 | §5 (G4·G5·G7) | 라벨보다 27분 먼저 게이트가 돌고 재실행 없음 → 3개 게이트 **미평가**. 그런데 `tier migration: none`은 인쇄됨 | **HIGH** |
| V3 | §3 / §8-3 | 씬별 1차 Δ_cue 선택의 **유일한 근거(질량 정합 등급)가 4/4 오류**. 잠금 자체는 지켜졌으나 전제가 거짓 | **CRITICAL** |
| V4 | §3.3 / §8-6 | s20 플라시보 배제가 **틀린 측정(0 px)** 위에 있음. 실제로는 최고 정합(0.91×) | **HIGH** |
| V5 | A1.2-1 | 두 라벨 세트 결론 갈림(s12 rgb) 시 "판정 불가" 미적용 | MEDIUM |
| V6 | §4.3 (구현) | `same_sign((0,0,0)) = True` — 사전등록에 없는 조작적 정의, **SHORTCUT 5건 전부가 여기 의존** | HIGH |
| V7 | §4.4 4행 / D46 | 문서 내부에서는 트윈-조건부 우선 규칙을 지켰으나, **결재 헤드라인(D46)이 raw recall과 2차 레그 수치를 중심 문장으로 승격** | MEDIUM |
| V8 | A1.2-3 | G7 **DEGENERATE 딱지 보고서 상단 인쇄** 미이행(섹션별 캐비앗만) | MEDIUM |

> **없는 위반도 적어 둔다(누명 방지)**: ① 결과를 본 뒤 B1↔B2를 바꾼 흔적 **없음**.
> ② 플라시보 오브젝트 집합을 다시 고른 흔적 **없음**. ③ 렌더가 사전등록보다 늦다(03:55 vs 05:01) —
> **사전등록 시각 주장은 참**. ④ 체크포인트 무수정. ⑤ G1 스모크는 3씬 전부 rc 0 · ground_z Δ = 0.
> **절차적 정직성 자체는 이 연구의 강점이다. 무너진 건 정직성이 아니라 계측이다.**

---

## 5. 리뷰어 거절 문단 / 저자 반론 문단

### 5-1. 최강 REVIEWER REJECTION (AISP, reject)

> **Reject.** The paper's causal claim rests on an intervention whose core premise is falsified by
> the authors' own renders. The design assumes that in *strict-H* frames the hazard contributes
> zero pixels, so that any surviving detection must be a response to contextual cues. We measured
> the authors' released frames: deleting the hazard alone (their arm A vs arm C) changes
> **6.6 %–13.6 % of every judged frame** at a conservative 32/255 threshold — 10^3–10^5 times the
> renderer noise floor the authors themselves establish. Arm C is therefore not "the same image
> minus something invisible"; it is a different image, and its false-alarm rate measures that
> difference. Consistently, arm-C FA is **monotone in how much each scene's keep-dressing surgery
> perturbed the frame** (36.6 % → FA 1.00; 13.1 % → 0.36; 1.0 % → 0.04) and is *not* ordered by cue
> inventory — scene17 retains the full cue vocabulary and shows FA 0.042. The headline
> "FA = 1.000 from cues alone" thus holds in exactly one of three scenes, and that scene is the one
> the authors themselves flag as having a degenerate 50-cell ground truth, a hand-patched
> hazard-blind sidecar oracle, three logged geometry-invariance gate failures, and the only bespoke
> arm-C fill in the study. The placebo controls do not rescue this: every pixel-mass admissibility
> grade in the pre-registration is contradicted by the renders, three of them in the
> anti-conservative direction, including the 18× conservatism claim that motivated promoting
> scene17 to the primary leg (measured: 0.56×, i.e. the placebo is *smaller* than the manipulation).
> Finally, the pre-registered primary rule returns **zero** CUE-EVIDENCE verdicts; the five
> SHORTCUT verdicts are all exactly (0, 0, 0) on 24 paired frames, whose one-sided 95 % bound
> (0.117) does not even resolve the authors' own 0.10 threshold. Two of the three scenes are
> training scenes. What is presented as a causal demonstration is an underpowered null on
> memorised scenes, with the one positive result confined to the most instrument-compromised
> condition in the study.

*(KR 요약: 개입의 전제가 실측에 의해 부정되고, 헤드라인은 3씬 중 계측이 가장 오염된 1씬에서만
나오며, 사전등록 1차 판정의 결론은 0건 CUE EVIDENCE + 검정력 없는 널이다.)*

### 5-2. 최강 AUTHOR REBUTTAL

> We accept two of the reviewer's factual corrections and they **strengthen**, not weaken, the
> paper — because our claim was never "the model reads cues", it is the strictly weaker and more
> alarming **"the model does not read the drop."**
>
> **1. The reviewer's own number is our result.** Deleting the hazard changes 6.6–13.6 % of the
> frame — and **recall does not move** (arm A vs arm C twin-conditional Δ ≈ 0; scene12 rgb/b2 fire on
> 24/24 hazard-free frames). A detector that is asked to find a 1.36 m drop, is shown a scene where
> that drop and a tenth of the image are gone, and answers "drop" at 100 % is not a detector. That
> statement needs no cue taxonomy, no placebo, and no pixel-mass matching. It survives the
> reviewer's critique intact.
>
> **2. The metric is mass-insensitive, which is why the null is informative.** Removing **16.5 %**
> of the frame (scene17 placebo) moves strict-H recall by **exactly 0.000 across 3 models × 3 seeds**;
> removing **29.7 %** (scene17 B1) moves rgb by +0.111 and depth/b2 by 0.000. The reviewer's
> "underpowered null" reading requires that our measurement be unable to see a third of the image
> disappearing. It sees it — and the model does not. The correct reading of the SHORTCUT cells is
> **invariance to massive appearance change**, not absence of power.
>
> **3. We pre-registered the demotion the reviewer asks for, and we executed it.** The three
> CUE-EVIDENCE results the reviewer would attack are in the *secondary, anti-conservative* leg and
> we refused to promote them — before seeing them. Zero primary CUE EVIDENCE is what we report.
> A field in which negative-obstacle detectors are published on scene-level recall needs exactly
> this: a pre-registered intervention that **fails to find** cue reasoning and says so.
>
> **4. Corrections we adopt.** We replace all AABB-estimated pixel masses with rendered
> ≥32/255 measurements (Table R-1), withdraw every "conservative placebo" claim, restore
> scene20's placebo (which is in fact our best-matched control at 0.91×), re-run the geometry gate
> at hazard-footprint scope, and re-title H2 from "firing on cue vocabulary" to
> **"firing on a hazard-free twin of the same scene"**. We add the lineage-off floor
> (FA .028 → 1.000) that makes the scene12 contrast auditable rather than absolute.
>
> **What the paper claims, restated:** *association, not inference — and the intervention apparatus
> is itself the contribution.* We ship the pre-registration, the five arms, the placebo protocol,
> the datum-preservation argument, and the gate suite as a reusable instrument for the
> negative-obstacle community, together with an honest report of the three places it broke in our
> own hands. A method paper whose headline result is "our own strongest scene is the one we trust
> least, here is why, here is the gate that should have caught it" is more useful to AISP than a
> fourth detector with a better AUC.

### 5-3. 이 심판의 판정

**'연합 ≠ 추론 + 개입 장치 자체가 기여'는 방어 가능하다 — 단, 아래 3개를 고쳐야만.**

1. 중심 문장을 **"단서 연합"에서 "위험 무반응(hazard-invariance)"으로 옮긴다.**
   현재 데이터가 지지하는 것은 후자뿐이고, 후자가 안전 함의는 **더 크다**.
2. **F1의 질량표를 논문에 싣고** 사전등록의 AABB 등급을 **철회 부기**한다(D41이 SEED_TABLE §5.2에
   한 것과 같은 처분). 숨기면 리뷰어가 30초 만에 잡는다(내가 4분 걸렸다).
3. **scene20 재렌더로 paired-H ≥ 10을 만든다**(F14). 그러면 사전등록 1차에서 **처음으로**
   CUE EVIDENCE가 나온다 — 그게 있어야 "연합 ≠ 추론"의 대조군이 성립한다.

이걸 안 하면: **workshop/short paper는 가능, full paper는 §5-1에서 죽는다.**

---

## 6. 수정 지시 (비용순)

| # | 조치 | 비용 | 막는 것 |
|---|---|---|---|
| **A1** | `redteam/r4_pixdiff.py` 결과를 `CUEOFF_RESULT.md` 상단 **Table R-1**로 삽입 + §3 AABB 등급 **철회 부기** | 10분 | F1 · V3 · 리뷰어 5-1 |
| **A2** | 계보 off FA 열(F7 표)을 arm-C 절에 **병기** — 이미 `per_frame.csv` 안에 있다 | 20분 | F7 · 4-1 |
| **A3** | `gates_cueoff.py` **재실행**(G4·G5·G7) 후 `GATES_CUEOFF.md` 갱신, `tier migration` 열의 출처 명시 | 15분 | F5 · V2 |
| **A4** | G2를 **hazard footprint + 카메라 스트립 스코프**로 재실행(D44 권고 그대로) 하고 **s20 B1/B2를 개별 판정**. s20 라벨의 1.50 vs 1.62 차이를 셀 단위로 귀속 | 30분 | F4 · V1 |
| **A5** | `readout_cueoff.py`의 `same_sign` 0-케이스를 **문서화**하고, SHORTCUT 셀마다 **0-flip 95 % 상한(0.117)을 병기** | 20분 | F6 · V6 |
| **A6** | s20 플라시보 **복원** — §3.3 철회, §4.3 판정식에 편입, `pixel_mass.py`의 s20 투영 **버그 감사** | 45분 | F1 · V4 |
| **A7** | 팔 C 절 제목·본문을 "단서 어휘 발화"에서 **"무위험 트윈에서의 발화"**로 재프레임 + `lz=0.0` 드레싱 리프트(1.36 m)와 백선/갈대 배치 변경을 **한계로 명기** | 30분 | F3 · 4-1 |
| **A8** | scene12 2밴드를 census에서 **1씬으로 접기** + "3씬 중 2씬이 train, test 0" 문장 추가 | 15분 | F9 · F10 |
| **A9** | `GAZEBO_TRACK.md` §0·D48을 §7-2 수준으로 **축소**, ctrl 월드 발화율 표(4-4 b) 삽입 | 20분 | F12 · 4-4 |
| **A10** | **scene20 재렌더**(`--cams` 확대 또는 조건 추가)로 paired-H ≥ 10 확보 | GPU ~20분 | F14 — **유일한 정당 CUE EVIDENCE 경로** |
| **A11** | (다음 창) **질량 정합 플라시보** 신설: s12에서 ≈600 k px 비단서 제거 팔 | GPU ~15분 | F8 — B1 붕괴의 유일한 해석 경로 |

---

## 7. 무엇이 살아남는가 (방어선)

1. **격리·동결·사전등록 시각**: 전부 검증된다(F13, V-없음 목록). 이건 자산이다.
2. **A vs C 무반응**: strict-H 프레임에서 위험을 지워도 recall이 안 움직인다 — **재프레임하면
   이 연구의 가장 강한 문장**이고 리뷰어의 공격을 그대로 흡수한다(5-2 §1).
3. **Δ_placebo = 0.000의 질량 무감성**: 16.5 %를 지워도 한 프레임도 안 뒤집힌다(5-2 §2).
4. **2차 레그 비승격을 실제로 지킨 것**: 사전등록 규율의 실증. 논문 §Method의 판매 포인트.
5. **Gazebo 0픽셀 발화 + 사다리 역전**: §7-2 범위 안에서는 유효.
6. **A1.1 코퍼스 결함 발견**(boost 라운드 미융합 → s12 GT 50셀): CUE-OFF보다 큰 발견일 수 있다.
   결재란 최우선.

---

## 8. 재현

```bash
# 실측 픽셀 질량 (Table R-1)
python3 experiments/weekend_0823/redteam/r4_pixdiff.py 24

# 계보 off FA 바닥 (F7 표) — per_frame.csv 재집계, GPU 불요
#   toggle_state == 'off' 행만 골라 GT 전음 프레임에서 max(p_*) >= 0.5 비율

# s20 GT 셀 차이 (F4)
#   labels/lineage__260823_cueoff_{A,P,B1,B2}__scene20.json 의 frames[*].gt 합 평균
#   → A/P 1.50 vs B1/B2 1.62
```
