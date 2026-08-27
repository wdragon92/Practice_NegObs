# REDTEAM_0823 — 지적 → 대응 → 잔여 리스크 원장

작성 2026-08-23 · RED-TEAM RESPONSE (D35 productization) · 작업방 `experiments/weekend_0823/rt_response/`
대상 리포트: `R1_novelty.md` · `R2_method.md` · `R3_repro.md`
결재 근거: `DECISIONS.md` **D34**(V2S 판정식 개정) · **D35**(레드팀 1파 수용 계획)

> **본 문서는 원장이다.** 각 지적에 대해 (a) 무엇을 새로 측정했는지 (b) 수치가 지적을 확증했는지
> 뒤집었는지 (c) 논문 문장을 어떻게 바꾸는지 (d) 그래도 남는 리스크가 무엇인지를 한 행에 적는다.
> 모든 신규 수치는 **CPU 전용 · GPU 0 · 동결 산출물 읽기 전용**으로 나왔고, 정본 파일은
> `METRICS.md` / `RESULTS_DRAFT.md`의 **append 절**로만 갱신했다(in-place 수정 0건).
> V2S GPU 큐는 건드리지 않았다.

---

## 0. 한 페이지 요약

| # | 레드팀 지적 | 재검증 결과 | 주장 처리 | 잔여 리스크 |
|---|---|---|---|---|
| **R1-F1** | RGB의 H 우위는 FA 미보정 산물 | **확증, 그리고 R1의 수치가 4/4 자리까지 정확히 재현됨** | "RGB가 이긴다" → **"RGB도 0이 아니다"** | 낮음 — 표와 그림 모두 산출됨 |
| **R2-F2** | 트윈-조건부로 보면 순위가 뒤집힌다 | **확증** (rgb .375 / depth .438 / b2 .1215) | 부록 표 신설 + 본문 1문장, **긍정형 프레이밍** | 낮음 |
| **R1-F3** | YOLO E/H=0은 어댑터 산물 | **양면 확증** — 어댑터 없이도 H는 0이 아니지만(.066), **위험-맹목 대조군이 .076** → 조건부로는 **−.010** | 문장을 어댑터 한정으로 교체, **패러다임 주장은 트윈-조건부 형태로만 유지** | 중간 — τ_conf .05에서는 조건부 .142로 0이 아님 |
| **R1-F7** | strict-H는 광학 정보를 막지 못한다 | **확증, 강하게** — 96/96 쌍에 잔여 신호, 중앙값 프레임의 4.5 % | "완전 가림" 단어 철회, **"기여 픽셀 0"의 기하 정의로 스코프 축소** | 중간 — 잔여의 상당량은 토글이 함께 지운 구조물 |
| **R1-F4** | none_in_fov 층이 어느 분모에도 없다 | **확증** (rgb .798 / depth .494 / b2 .638) | **4번째 FA 열 신설** + N3 재해석 | 낮음 |
| **R1-F4b** | N3 "behaved as designed"는 오독 | **부분 확증 — 모델별로 다르다** (RGB 포화, **Depth는 진짜로 조용함**) | R.3에 정정 문단, RGB 한정으로 | 낮음 |
| **R2-F3** | 프레임 부트스트랩이 클러스터를 무시 | **확증** (FA CI ×1.7–5.6) | FA는 클러스터 CI로 재계산, **H·E는 CI 철회** | 낮음 |
| **R2-D5** | aux `cell_f1` "barely" 유의는 못 버틴다 | **확증** — [0.0001, 0.0786] → **[−0.258, 0.205]** | 유의 주장 철회 | — |
| **R2-D5+** | (신규) `cell_recall_H` +0.3546 = "최대 확증 효과" | **클러스터 하에서 붕괴** [−0.143, 0.463] | **SEED_TABLE §5.2 문장 정정 필요** | **높음 — 결재 대상** |
| **R3-1.4b** | METRICS §2.4 τ_edge 0.02 표기 오류 | 확증 (코드·매니페스트는 0.05) | append 정정 + 공허성 정직 문장 | — |
| **R3-1.4a** | SPLIT_PROPOSAL `frames` 열이 분할 크기가 아님 | **확증, 재계산 일치** (1536/288/816/2640) | append 정정표 | — |

---

## 1. R1-F1 — FA-matched H recall  ✅ 대응 완료

**지적.** 본 표는 RGB의 H를 FA .359에서, Depth의 H를 FA .042에서 읽어 같은 열에 인쇄한다.
운용점을 맞추면 모든 지점에서 Depth ≥ RGB다.

**재검증.** `rt_response/code/f1_fa_matched.py`. R1의 `r1.py` 규칙(τ 0.01 격자)을 그대로 재현했고
**4개 목표 FA × 3모델 12개 값이 전부 소수점 3자리까지 일치**한다. 추가로 0.01 격자를 없앤
경험분위 τ 규칙(FA 해상도 1/408)으로 다시 계산했다.

| 맞춘 FA | RGB H | Depth H | B2 H | Δ(D−R) |
|---|---|---|---|---|
| 0.359 | 0.729 ±0.135 | **0.781** ±0.078 | 0.399 | +0.052 |
| 0.20 | 0.483 ±0.172 | **0.562** ±0.031 | 0.198 | +0.080 |
| 0.10 | 0.326 ±0.229 | **0.510** ±0.078 | 0.097 | +0.184 |
| 0.05 | 0.243 ±0.208 | **0.479** ±0.094 | 0.031 | +0.236 |

**주장 처리 (D35 승인 하향).** `RESULTS_DRAFT` R.4의 *"the inversion is the finding"* 은
전제가 거짓이므로 삭제 대상이다. 대체 문장은 §2 참조. 핵심은 **하향이 논문을 죽이지 않는다**는 것:
FA 0.10에서 RGB H = 0.326이고, 같은 조건에서 검출기 계열의 조건부 값은 0.038이다.

**산출물.** `rt_response/F1_FA_MATCHED.md` · `f1_fa_matched.json` ·
`figs/fig_f1_recall_vs_fa.png|pdf` (H·E·V 3패널 전곡선, 시드 min–max 띠, τ=0.5 다이아몬드).

**잔여 리스크.** 없음에 가깝다. 단 표가 4행이 되면 "왜 0.10을 대표로 쓰나"가 나온다 →
**4개 지점을 전부 싣고 곡선 그림을 같이 낸다**가 답.

---

## 2. R2-F2 — 트윈-조건부 recall  ✅ 대응 완료

**지적.** 프로젝트 자신의 인과 장치(트윈)를 recall에 적용하면 RGB의 H 우위가 사라진다.

**재검증.** `rt_response/code/f2_twin_conditional.py`, τ=0.5, KEPT 쌍.
`hit = (max_on_gt ≥ τ) ∧ (max_off_gt < τ)`.

| model | H recall (공개값) | **트윈-조건부 H** | H쌍 off팔 발화율 | 발화 중 무조건부 비율 |
|---|---|---|---|---|
| rgb | 0.688 ±0.141 | **0.375 ±0.115** | 0.330 | **0.447** |
| depth | 0.438 ±0.031 | **0.438 ±0.031** | **0.000** | **0.000** |
| b2 | 0.229 ±0.156 | **0.1215 ±0.068** | 0.118 | 0.305 |

R2 공개값 .375 / .438 / .121과 일치(b2는 0.1215의 반올림 차이).
E·V 티어도 같이 냈다 — E: rgb .556→**.207**, depth .600→**.600**; V: rgb .820→**.440**, depth .927→**.873**.

**주장 처리 — 긍정형 프레이밍(D35).** 방어가 아니라 무기로 쓴다:
> **Depth의 H 응답은 전량 위험-조건부다(무조건부 발화 0/96, 3시드 전부). RGB는 H 발화의 45 %가
> 낙차를 지운 쌍둥이 프레임에서도 동일하게 난다.** 두 팔의 H recall이 비슷해 보이는 것은
> 서로 다른 두 가지를 세고 있었기 때문이다.

**산출물.** `rt_response/F2_TWIN_CONDITIONAL.md` · `f2_twin_conditional.json`
(런별·씬별 분해 포함 — scene15에서 rgb의 무조건부 발화가 어디에 몰려 있는지 그대로 보인다).

**잔여 리스크.** 낮음. 헤드라인 표는 무수정(절대선 §3-2), 부록 신설 + 본문 1문장이라는 배치가
**결재 대상**으로 남는다.

---

## 3. R1-F3 — 어댑터 프리 YOLO 지표  ⚠️ 부분 반전 — 문장 교체 필수

**지적.** *"any method whose output is a bounding box … has an identically zero ceiling on E and H,
independent of detector quality"* 는 검출 **패러다임** 주장인데, 실제로 측정된 것은 우리 어댑터의
성질이다. 오라클 박스를 넣어도 E/H가 0이었다는 사실이 그 증거다.

**재검증.** `rt_response/code/f3_adapter_free_yolo.py`. 그리드·투영·det2cell을 전부 제거하고
**이미지 공간에서만** 물었다: "저장된 검출 중 amodal GT 박스와 IoU > t 인 것이 하나라도 있는가".

| tier | n | any detection | **IoU > 0** | IoU > 0.1 | IoU > 0.3 |
|---|---|---|---|---|---|
| V | 180 | 0.393 | **0.378 ±0.086** | 0.356 | 0.317 |
| E | 45 | 0.259 | **0.259 ±0.233** | 0.259 | 0.259 |
| **H** | 96 | 0.167 | **0.066 ±0.036** | 0.052 | 0.031 |

**→ 0이 아니다. 구성적 상한 주장은 지금 형태로는 철회 대상이다.**

그런데 **위험-맹목 대조군**을 붙이면 결론이 다시 선다. 같은 컷의 **off 트윈의 검출**을
**on 프레임의 amodal GT**에 대고 채점하면(장식·조명·포즈 동일, 낙차만 삭제):

| tier | on-arm IoU>0 | off-트윈 IoU>0 (위험 맹목) | on − off | **트윈-조건부** |
|---|---|---|---|---|
| V | 0.378 | 0.041 | **+0.337** | **0.346 ±0.064** |
| E | 0.259 | 0.148 | +0.111 | 0.170 ±0.156 |
| **H** | **0.066** | **0.076** | **−0.010** | **0.038 ±0.010** |

**H에서 위험-맹목 기저율이 on팔보다 오히려 높다.** 즉 어댑터를 걷어내도 검출기는
**숨은 낙차에 조건부인 박스를 내지 않는다**. V에서는 +0.337로 강하게 조건부다 — 대조군이
둔감해서 나온 결과가 아니라는 증거.

**주장 처리 (필수 교체).**
> ~~"any method whose output is a bounding box over visible hazard pixels has an identically zero
> ceiling on the E and H tiers, independent of detector quality"~~
> → **"Two separate bounds apply to row 4 and they must not be conflated. (i) *Our* ground-projection
> adapter cannot map a box to an E- or H-tier cell at all: feeding the amodal GT boxes in as
> conf-1.0 detections yields E = H = 0.000 before any training, so the published 0 is a property of
> the adapter. (ii) Removing the adapter and scoring in image space, the detector does fire near
> hidden hazards at a low rate (H: 0.066 of frames at IoU > 0, τ_conf = 0.25) — but the same rate on
> the hazard-deleted twin of the same cut is 0.076, so the twin-conditional rate is −0.010, i.e.
> indistinguishable from zero, against +0.337 on the V tier. An amodal-box detector trained on this
> corpus produces no hazard-conditional evidence when the hazard contributes no pixels."**

**추가로 반드시 적을 것 (R1-F3-⑤).** 이 YOLO는 visibility-trained가 아니라 **amodal-trained**다
(H 96/96 프레임 전부 비어 있지 않은 GT 박스를 가진다). 완전 가림에서 amodal 박스는 이미지가
결정하지 않는 타깃이며 scene14에서는 파사드를 통째로 덮는다 — **학습 불가능한 타깃을 준 것 자체가
한계**라는 한 줄을 우리가 먼저 쓴다. 측정치도 같이: H 프레임의 최대 GT 박스 면적 평균 **0.193**
(중앙값 0.230), E는 **0.585**.

**V 열 처리(R1-F3-③).** 오라클 천장 frame-det 0.404 / V 0.514 / cell recall 0.074를 표에 병기하거나
V 열을 부록으로 내린다. 파라미터 비대칭(yolov8n 3.2 M vs U-Net 24.4 M vs B2 27 M)도 각주로.

**산출물.** `rt_response/F3_ADAPTER_FREE_YOLO.md` · `f3_adapter_free_yolo.json`.

**잔여 리스크 (중간).** τ_conf를 저장 하한 0.05까지 내리면 H 트윈-조건부가 **0.142**로 올라간다.
"0이다"라고 쓰면 심사자가 conf를 내려서 반박할 수 있다. → **τ_conf 두 값을 모두 인쇄하고,
"운용 conf에서 0, 저장 하한에서 0.14"를 우리가 먼저 쓴다.**

---

## 4. R1-F7 — strict-H 픽셀 차분 감사  ⚠️ 확증 — "완전 가림" 문구 철회

**지적.** strict-H는 기하 정의(`int_px == 0 ∧ edge_vis == 0`)라 그림자·AO·GI·메시 이음매를 막지
못한다. 96쌍의 |on−off|를 재고, 0인 쌍이 있으면 Δ=0이어야 한다(정합성 게이트).

**재검증 — 먼저 문턱을 교정해야 했다.** `rt_response/code/f7b_noisefloor.py`.
sceneN3의 `keep_dressing` off팔은 on팔과 **기하학적으로 동일**하다(heightmap `max|Δ| = 0.000000 m`).
그 두 렌더 사이의 차이는 전부 패스트레이서/디노이저 비결정성이다:

| 기준쌍 | ≥2/255 중앙값 | ≥8/255 | **≥32/255** | 변화 픽셀 평균 크기 |
|---|---|---|---|---|
| **노이즈 바닥** (N3 동일 기하) | 916,841 (**프레임의 44.2 %**) | 27,571 | **50** | 3.19 |
| 낙차만 제거 (C2 keep_dressing) | 1,270,241 | 875,005 | 698,078 | 61.87 |

**브리프가 제안한 2/255는 렌더러 노이즈다.** 따라서 모든 통계를 3단계로 내고 **≥32/255**를
내용 신호 수준으로 쓴다(노이즈 바닥 50 px / 2,073,600 px).

**결과 (`rt_response/code/f7_hpair_pixdiff.py`, 96/96 쌍 포즈 정확 1e-6 검증).**

| 집합 | 차분 0인 쌍 | ≥32/255 중앙값 | 최소 | 프레임 대비 | 노이즈 바닥 대비 |
|---|---|---|---|---|---|
| 전체 96 | **0** | **93,606 px** | 2,211 | 4.51 % | ×1,872 |
| scene14 (60) | 0 | **156,977** | 42,797 | 7.57 % | ×3,140 |
| scene15 (36) | 0 | **7,106** | 2,211 | 0.34 % | ×142 |

**판정: 이 코퍼스에서 strict-H는 광학적으로 결코 비어 있지 않다.** 가장 조용한 쌍조차
노이즈 바닥의 44배를 남긴다. R1이 요구한 "차분 0 정합성 게이트"는 **적용 대상이 0개라 공허**하고,
결론은 게이트가 겨냥한 것의 반대다 — H에서 Δ>0은 설명이 필요한 이상현상이 아니라 **평범한 시각 증거**다.

**s14 vs s15 — 그리고 이것이 R2-F1과 독립적으로 같은 말을 한다.**

| | scene14 | scene15 | 배율 |
|---|---|---|---|
| ≥32/255 중앙값 | 156,977 | 7,106 | **×22.1** |
| 변화 픽셀 평균 크기 | 36.22 | **4.78** | ×7.6 |
| (참고) 노이즈 바닥 평균 크기 | 3.19 | 3.19 | — |

**scene15의 잔여 신호는 크기 면에서 렌더러 노이즈의 1.5배에 불과하다.**
R2 §4.3이 트윈 Δ로 이미 지목한 씬(효과 있는 s14 / 없는 s15)이 **픽셀 증거에서도 같은 방향으로
갈린다.** 두 독립 측정이 일치한다 — 이건 논문에 그대로 쓸 수 있는 강한 문장이다.

**잔여가 모델 응답을 예측하는가.** log10(≥32 잔여 픽셀) vs 그 쌍의 `delta_score` Spearman ρ:
9런 전부 양수(0.27–0.83). 씬 내부로 좁히면 **Depth는 6/6 셀에서 양수(0.08–0.69), s14 조용한
1/3 → 시끄러운 1/3에서 Δ 0.34–0.40 → 0.83–0.93**. RGB는 일관되지 않는다(−0.13 ~ +0.39).
→ **잔여 광학 증거를 추적하는 것은 Depth 팔이고, RGB의 H 응답은 보이는 양에 따라 등급이 매겨지지
않는다** — F2의 무조건부 발화 45 %와 정확히 같은 진단.

**주장 처리 (필수).**
- 헤드라인에서 **"fully occluded"** 를 뺀다. 정확한 표현은
  **"the hazard's own prism contributes zero pixels to the frame"** 이고, 그 정의가 무엇을
  허용하는지(그림자·GI·함께 제거되는 구조물) 한 문장으로 밝힌다.
- **R1-F12 한정어를 반드시 붙인다.** 토글은 `SCENE_CONFIG['hazard_stairs']`이고,
  scene14에서는 shoulder massif · side slopes · stair · step coursing · parapets · cues ·
  autumn litter를 **함께** 제거한다(`scene14_grandstair_illusion.py:1885-1898`).
  따라서 Δ는 {낙차의 간접 광학} ∪ {그 분기 안의 모든 오브젝트}에 대한 민감도다.

**산출물.** `rt_response/F7_HPAIR_PIXDIFF.md` · `f7_hpair_pixdiff.json` · `f7b_noisefloor.json` ·
`panels/h_diff_contact_sheet.png` + 개별 6장 (선정 규칙은 이미지를 보기 **전에** 고정:
씬별 잔여 최소/중앙/최대).

**잔여 리스크 (중간).** amodal 실루엣 포함률(전체 0.812)은 실루엣이 가림물까지 덮기 때문에
자동으로 높아진다 — 이 캐비앗을 표 옆에 붙여 두었다. 그리고 "그림자냐 구조물이냐"의 분해는
아직 안 됐다(§10-② 단서 감사 / F6-B CUE-OFF의 몫).

---

## 5. R1-F4 — none_in_fov 회계 구멍 + N3 재해석  ✅ 대응 완료 (모델별로 정정)

**재검증.** `rt_response/code/f4_none_in_fov.py`. R1의 6개 값 전부 일치.

| model | **`FA_in-scene`** (none_in_fov 발화율) | 보고된 `frame_fa_off` | 배율 |
|---|---|---|---|
| rgb | **0.798 ±0.160** | 0.359 ±0.127 | ×2.2 |
| depth | **0.494 ±0.074** | 0.042 ±0.029 | ×11.9 |
| b2 | **0.638 ±0.228** | 0.238 ±0.143 | ×2.7 |

씬 분해: scene07 (n=51) rgb .725/1.000/.608 · scene14 (n=6) · sceneN3 (n=24) rgb 1.000/.875/.750.

**N3 재해석 — R1보다 한 단계 정밀하게.** R1은 "양팔 모두 포화 발화"라고 했지만, 재계산하면
**모델마다 다르다**:

| run | on팔 발화율 | off팔 발화율 | on 평균 max p |
|---|---|---|---|
| rgb_s42 / s43 / s44 | **1.000 / 0.875 / 0.750** | 1.000 / 0.708 / 0.708 | 0.946 / 0.745 / 0.738 |
| depth_s42 / s43 / s44 | **0.125 / 0.000 / 0.000** | 0.125 / 0.000 / 0.000 | 0.111 / 0.002 / 0.101 |
| b2_s42 / s43 / s44 | 0.458 / 0.917 / 0.208 | 0.375 / 0.917 / 0.208 | 0.468 / 0.789 / 0.230 |

→ **Depth의 N3는 실제로 조용하다.** "behaved as designed"는 Depth에 대해서는 참이고,
**RGB(그리고 부분적으로 B2)에 대해서만 거짓**이다. 정정 문장은 RGB 한정으로 쓴다(§8 append 참조).

**잔여 리스크.** 낮음. 다만 헤드라인 3종이 4종이 되면 표 폭이 늘어난다 — 배치는 결재 대상.

---

## 6. R2-F3 / D5 — 클러스터 부트스트랩  ✅ 대응 완료 + 신규 발견 1건

**재검증.** `rt_response/code/f5_cluster_ci.py`, 10,000회, 재표집 단위 = `scene_id`.
정본 `bootstrap.py`는 **수정하지 않았다**(신규 함수는 격리 스크립트에만 존재).

- **FA (7 클러스터, 보고 가능):** 폭 비 ×1.7–5.6. R2가 공개한 3행 재현 —
  rgb_s42 [0.328,0.422]→[0.162,0.647] ×5.2 (R2 ×5.2) · rgb_s44 ×5.0 (R2 ×5.3) ·
  depth_s42 ×2.6 (R2 ×2.7).
- **H(2 클러스터) · E(1 클러스터): CI 철회.** 2 클러스터에서는 재표집이 3가지 다중집합만
  만들어내므로 반환되는 구간은 추론이 아니라 열거의 산물이다. 대체물 = 씬별 recall과
  **같은 씬 off팔 FA**를 항상 병기(R1-F2-③).
- **aux `cell_f1`: R2 예측대로 죽는다.** `+0.0403 [0.0001, 0.0786]` → **[−0.2580, 0.2054]**.
  `cell_precision` `+0.1291`도 죽는다 → [−0.1620, 0.2458].

**🔴 신규 발견 (레드팀도 못 잡은 것) — 결재 승격 권고.**
`SEED_TABLE.md` §5.2는 `cell_recall_H` **+0.3546**을 *"the single largest confirmed effect in the
table, and the one that matters for this paper's thesis"* 라고 쓴다.
클러스터 재표집에서 **[−0.1429, 0.4625] — 0을 포함한다.** 프레임 CI [0.2768, 0.4302]는
scene14/scene15 두 씬 안의 변동만 재고 있었다. **이 문장은 정정되어야 하고, 그 정정은
R2가 지적한 `cell_f1` "barely" 행보다 훨씬 중요하다** (§5.2가 논문 논지에 직결된다고 스스로 선언했으므로).
`frame_det_rate`(−0.1682)도 클러스터 하에서 0을 포함한다.
`frame_recall_E` / `cell_recall_E`는 지지 표본이 scene18 한 씬이라 CI가 **퇴화**한다
([−0.600, −0.600]) — 유의가 아니라 **보고 불가**로 표기해야 한다.

**산출물.** `rt_response/F5_CLUSTER_CI.md` · `f5_cluster_ci.json`.

---

## 7. R3 — 문서 정정 2건  ✅ append 완료

| 항목 | 확인 | 조치 |
|---|---|---|
| `METRICS.md` §2.4 `τ_edge = 0.02` | 코드 `labeler.py TAU_EDGE_DEF = 0.05` · 매니페스트 `meta.tau_strict.tau_edge = 0.05` | append 정정 + **공허성 정직 문장**(edge_ratio가 {0} ∪ [0.44, 1] 이봉이라 (0, 0.44) 안의 어떤 값도 동일 분할) |
| `SPLIT_PROPOSAL_v2_full.md` `frames` 열 | 재계산 일치: train **1536**(문서 1368) · val **288**(231) · test **816**(729) · 비-HOLD **2640**(2328); 차이 312 = H_weak 30 + none_in_fov 282 | append 정정표 (`frames` → `V+E+H+off`로 개명, 5범주 전열 병기) |

---

## 8. 잔여 리스크 원장 (창 안에서 닫히지 않는 것)

| # | 리스크 | 성격 | 상태 |
|---|---|---|---|
| **RR1** | H 인과 주장의 실효 표본이 **씬 2개, 효과 확인 1개** | 구조적 — test 불가침이라 창 안에 새 씬을 만들 수 없다 | **미해소.** 주장을 씬 단위로 재작성하는 것이 유일한 대응. **결재 대상**(헤드라인 문장 변경) |
| **RR2** | `cell_recall_H` 유의가 클러스터에서 붕괴 | 정본 문장 오류 | **미해소 — 신규.** SEED_TABLE §5.2 정정 필요. **결재 승격 권고** |
| **RR3** | strict-H 잔여의 "그림자 vs 함께 제거된 구조물" 분해 | 측정 미실시 | **미해소.** F6-B CUE-OFF(플라시보 팔 포함)만이 답할 수 있다 |
| **RR4** | YOLO 트윈-조건부 H가 τ_conf 의존 (0.25에서 −0.010, 0.05에서 +0.142) | 운용점 의존 | **부분 해소** — 두 값 병기로 방어 |
| **RR5** | 단안 depth 추정 baseline 부재 (R1-F9) | 비교 누락 | **미해소.** 한계 절 선제 문장이 최소 대응 |
| **RR6** | 관련연구 절 부재 — amodal / BEV layout hallucination (R1-F5) | 집필 | **미해소.** GPU 0, 집필 작업 |
| **RR7** | 단서를 변수로 다룬 실험이 0건 (R1-F6) | 설계 | **미해소.** 갈래 A(주장 축소) 또는 갈래 B(B1 최소판 렌더) 결재 |
| **RR8** | 실측 프로토콜이 폐기된 15칸 V0 그리드 (R3 §3.1) | 차단급 | **미해소.** 파일럿 촬영 전제조건 |
| **RR9** | `runs/` 산출 md·json이 `.gitignore`에 배제 (R3 §2.1) | 배포 | **미해소.** D35가 "즉시 수리" 지시 — 별도 작업 |

---

## 9. 재현

```bash
unset PYTHONPATH VIRTUAL_ENV
export PYTHONNOUSERSITE=1
cd /home/vislab/Desktop/work_sy/Practice_NegObs
PY=/home/vislab/miniconda3/envs/env_seg/bin/python
cd experiments/weekend_0823/rt_response/code
$PY f1_fa_matched.py          # F1  · 초 단위
$PY f2_twin_conditional.py    # F2  · 초 단위
$PY f3_adapter_free_yolo.py   # F3  · 수 분 (검출 txt 3 × 816)
$PY f4_none_in_fov.py         # F4  · 초 단위
$PY f5_cluster_ci.py          # F5  · 수 분 (10k 재표집 × 20 런-지표)
$PY f7b_noisefloor.py         # F7b · 수 분 (PNG 재판독)
$PY f7_hpair_pixdiff.py       # F7  · 수 분 (96쌍 × 2 × 1920×1080)
$PY f7_report.py              # F7 리포트
$PY fig_f1_curves.py          # 그림 1
$PY fig_f7_panels.py          # 패널 6 + 컨택트 시트
```

전부 CPU · 읽기 전용 · 새 훈련/렌더 0 · GPU 큐 무간섭.
입력: `experiments/dayrun_0820/runs/v2/*/eval_test/per_frame.csv` ·
`runs/v2/*/twin/twin_pairs.csv` · `runs/yolo_s*/pred_test/labels/` ·
`annotations/amodal/bboxes.json` · `dataset_manifest_v2_full.json` · `split_v2_full.json` ·
`dataset/v2_corpus/260819_main_{on,off}/` · `dataset/v2_probes/260820_ctrloff/`.
