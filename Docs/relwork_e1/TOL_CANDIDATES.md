# TOL_CANDIDATES — 선(線) 채점 허용오차 후보 기준

- 작성 2026-08-28 · 실행 [클로드 코드] · 브리프 `relwork_survey_brief_v4.md` §2 축 C · §5-3
- **P1 준수**: 이 문서는 **후보를 모아 원문 그대로 인쇄**할 뿐이다. 채택은 승용 결재이고, 브리프 §2-C에 따라 **채택 시점은 모델 단계 차기 브리프**다.
- **기억-작성 금지 준수**: 아래 4건은 전부 **내가 실제로 연 원문 PDF 또는 공식 저장소 코드**에서 그대로 옮겼다. 열지 못한 것은 §5에 서지만 남겼다.

---

## 승용 요약 (5문장)

1. 선을 채점할 때 "얼마나 빗나가면 틀린 것인가"를 문헌은 **네 가지 방식**으로 정한다 — ⓐ 이미지 대각선 비율 ⓑ 선을 띠로 만들어 IoU ⓒ 픽셀 거리 고정값 ⓓ 끝점 거리의 지수 신뢰도.
2. **가장 인용력이 센 것은 ⓐ BSDS 계열**이다: 원 논문(Martin 2004)이 `d_max = 이미지 대각선의 1%`, 공식 벤치마크 코드가 `maxDist = 0.0075`(=0.75%)를 기본값으로 박아 두었다. 둘 다 내가 직접 확인했다.
3. **가장 우리 형태에 가까운 것은 ⓓ StairNet의 `dth = 1`** 이다 — 계단 선 끝점 거리로 채점한다. 다만 **단위가 원문에 안 적혀 있다**(픽셀인지 셀 정규화 단위인지). 고쳐 쓰지 않고 그대로 인쇄한다.
4. **주의할 계산 하나**: Martin 2004는 "대각선의 1% = 2.88 픽셀"이라 적었는데, BSDS 이미지(321×481)의 대각선은 578.28 px이라 1%는 **5.78 px**이다. 2.88 px은 대각선 288 px짜리 이미지에 해당한다. **숫자를 고치지 않고 불일치 그대로 올린다** → ❓-T1.
5. 우리 대상은 **열린 폴리라인 1개**라 BSDS(폐곡선 다발)·CULane(고정 4차선)·TuSimple(고정 y 표본)과 전제가 다르다. 그대로 가져오면 안 되는 이유를 §4에 적었다.

---

## 후보 1 — BSDS 경계 벤치마크 (원 논문) 【축 C 1순위】

| 항목 | 내용 |
|---|---|
| 출처 | Martin, D., Fowlkes, C., Malik, J. — *Learning to Detect Natural Image Boundaries Using Local Brightness, Color, and Texture Cues*, IEEE TPAMI **26(5):530–549 (2004)** |
| 수집 경로 | 프린스턴 강의 사본 PDF를 열어 `pdftotext`로 본문 확인 [코드·정독] |
| **원문 정의 (그대로)** | **"Each of the curves in Figure 3 uses a fixed distance tolerance d_max = 1% of the image diagonal (2.88 pixels)."** |
| 보조 원문 | "this approach would not tolerate any localization error, and would consequently over-penalize algorithms ... since even the ground truth data contains boundary localization errors" — **허용오차를 두는 이유**를 원문이 직접 밝힌 문장 |
| 수치 | `d_max = 이미지 대각선의 1%` · 원문 괄호값 **2.88 px** |
| 민감도 관례 | 원문 Fig.14가 **허용오차를 바꿔 가며 F-measure 변화를 인쇄**한다("Panel (e) shows how the F-measure changes as a function of d_max"). → **우리 CONST_LEDGER의 '2~3값 민감도' 관행과 동일한 문헌 선례**다 |
| 우리에게 쓸 때 | 해상도 의존적이다. 우리 렌더 해상도의 대각선을 곱해 픽셀로 환산해야 하고, 그 환산값을 상수 대장에 [문헌]으로 올려야 한다 |

### ⚠ 검산 (침묵 수리 금지 — 있는 그대로)

내가 계산한 값:

```
321 × 481  → 대각선 578.28 px
  1%  = 5.78 px      0.75% = 4.34 px
"1% = 2.88 px"가 성립하려면 대각선 = 288 px 이어야 한다
```

원문 괄호값 **2.88 px**과 BSDS 표준 해상도의 1%(**5.78 px**)가 **맞지 않는다.** 원인은 내가 확인하지 못했다(다운샘플 평가 가능성 등은 **추측이라 적지 않는다**). 어느 쪽을 인용할지는 결재 → ❓-T1.

---

## 후보 2 — BSDS500 공식 벤치마크 코드 (도구 기본값) 【축 C 1순위·짝】

| 항목 | 내용 |
|---|---|
| 출처 | `BIDS/BSDS500` 공식 저장소 · `bench/benchmarks/boundaryBench.m`, `bench/benchmarks/evaluation_bdry_image.m` (헤더: "based on boundaryBench by David Martin and Charless Fowlkes ... Pablo Arbelaez") |
| 수집 경로 | raw.githubusercontent.com에서 소스 원문을 그대로 받아 확인 [코드·원본] |
| **원문 정의 (그대로)** | 주석: **`%   MaxDist : For computing Precision / Recall.`**  ·  기본값: **`if nargin<6, maxDist = 0.0075; end`** (두 파일 모두) |
| 함께 박힌 기본값 | `nthresh = 99` (PR 곡선 점 개수) · `thinpb = true` (채점 전 형태학적 세선화) |
| 수치 | **`maxDist = 0.0075`** = 0.75% |
| 주의 | **이 두 파일 어디에도 "이미지 대각선 비율"이라는 문구는 없다.** 그 해석의 출처는 별도 확인이 필요하다 → 표 ❓-C3 |
| 우리에게 쓸 때 | 태그는 **[도구기본값]**이 정확하다([문헌] 아님). `thinpb=true`가 기본이라는 점 — **예측 선을 1픽셀로 세선화한 뒤 채점**하는 관례 — 도 함께 이월 대상이다 |

---

## 후보 3 — CULane / SCNN (선을 띠로 만들어 IoU) 【축 C 2순위】

| 항목 | 내용 |
|---|---|
| 출처 | Pan, X., Zhan, X., Shi, J., Luo, P., Wang, X., Tang, X. — *Spatial As Deep: Spatial CNN for Traffic Scene Understanding*, **AAAI 2018** (arXiv 1712.06080) |
| 수집 경로 | arXiv PDF를 받아 `pdftotext`로 평가절 원문 확인 [코드·정독] |
| **원문 정의 (그대로)** | **"In order to judge whether a lane marking is successfully detected, we view lane markings as lines with widths equal to 30 pixel and calculate the intersection-over-union (IoU) between the ground truth and the prediction. Predictions whose IoUs are larger than certain threshold are viewed as true positives (TP)."** |
| 임계 | **"Here we consider 0.3 and 0.5 thresholds corresponding to loose and strict evaluations."** — 원문이 **느슨/엄격 2값을 나란히 보고**한다(우리 민감도 관행과 같은 형태) |
| 지표 | `F-measure = (1+β²)·P·R/(β²P+R)`, `Precision = TP/(TP+FP)`, `Recall = TP/(TP+FN)`, **β=1** |
| 부수 상수 | 학습 시 **타깃 선 두께 16 px**, 입력 리사이즈 **800×288** (평가 두께 30 px과 다른 값임에 주의) |
| 우리에게 쓸 때 | **선 → 띠 → IoU**는 우리 edge 폴리라인 채점에 그대로 옮길 수 있는 형태다. 단 30 px은 800×288 기준이라 **우리 해상도로 재환산**해야 하고, 브리프 §5가 "정본 라벨은 폴리라인(띠 아님)"이라 못 박았으므로 띠 두께는 **채점용 파생값**으로만 쓸 수 있다 |

---

## 후보 4 — TuSimple 차선 벤치마크 (점 거리 고정값 + 각도 보정) 【축 C 2순위】

| 항목 | 내용 |
|---|---|
| 출처 | `TuSimple/tusimple-benchmark` 공식 평가 코드 `evaluate/lane.py` (클래스 `LaneEval`) |
| 수집 경로 | raw.githubusercontent.com 소스 원문 [코드·원본] |
| **원문 정의 (코드 그대로)** | `pixel_thresh = 20` · `pt_thresh = 0.85` · `threshs = [LaneEval.pixel_thresh / np.cos(angle) for angle in angles]` · `np.sum(np.where(np.abs(pred - gt) < thresh, 1., 0.)) / len(gt)` |
| 해석(코드가 말하는 그대로) | ⓐ 점 하나는 **가로 거리 20 px 이내**면 정답 ⓑ 그 임계를 **선의 기울기로 나눠(1/cos θ) 보정** ⓒ 한 차선은 **점의 85% 이상**이 맞아야 매칭 성공 |
| 데이터 전제 | 라벨이 **고정 y 표본(h_samples)에서의 x 값** 폴리라인 |
| 우리에게 쓸 때 | **각도 보정(1/cos θ)** 이 우리에게 특히 중요하다 — grazing angle에서 edge 라인이 거의 수평이 되므로 세로 오차와 가로 오차의 의미가 달라진다. 다만 TuSimple은 "차선은 세로로 뻗는다"를 전제하므로 **축을 뒤집어(우리 edge는 가로) 옮겨야 한다** — 그 전환 자체가 결재 대상이다 |

---

## 후보 5 (참고) — StairNet 끝점 거리 신뢰도 【우리 대상과 가장 형태가 가까움】

| 항목 | 내용 |
|---|---|
| 출처 | Wang, Pei, Qiu, Tang — *Deep Leaning-Based Ultra-Fast Stair Detection* (arXiv 2201.05275 / Sci Rep 2022) |
| 수집 경로 | arXiv PDF 정독 [코드·정독] |
| **원문 정의 (그대로)** | **"where c(x) is the confidence and DT(x) is defined as the 2D Euclidean distance in the image space. dth is the distance threshold and is set to 1. The sharpness of the exponential function is defined by the parameter α. To achieve precise localization with this function, α is set to 2."** |
| 판정 규칙 (원문) | "a TP cell must meet the following two conditions: 1) the cell is a positive sample and is correctly predicted as a positive sample; 2) in the cell, the **location error between the predicted location of the line and the corresponding ground truth is within a certain threshold**" |
| 수치 | `dth = 1` · `α = 2` · 보고는 **c(x)=0.5**에서 · 그리고 **mFWIOU = c(x)=0.05~0.95를 0.05 간격 19개 값의 평균** |
| 계승 | StairNetV2(A-2)가 **"The confidence calculation is the same as that of StairNet"** 로 그대로 이월 → 이 계보의 사실상 표준 |
| ⚠ 단위 미상 | 원문은 `DT(x)`를 "in the image space"라 적었지만, 같은 논문이 위치 라벨을 **"the normalized coordinates"**(셀 단위 정규화)로 정의한다. 512×512 입력에 64×64 셀이므로 셀 하나가 8×8 px이다. **`dth=1`이 1 px인지 1 셀(=8 px)인지 원문만으로는 결정 불가** — 내가 정하지 않는다(P1) → ❓-T2 |
| 우리에게 쓸 때 | **거리 → 신뢰도 → 임계**라는 3단 구조가 유용하다. 이진 합격/불합격 대신 **연속 신뢰도로 저장하고 임계는 나중에 스윕**하는 방식이라 브리프의 *store raw, bin later* 원칙과 정확히 같은 철학이다 |

---

## 4. 이 관례들을 우리 문제에 그대로 못 쓰는 이유 (정직 표기)

| 관례 | 그쪽 전제 | 우리 전제 | 어긋나는 지점 |
|---|---|---|---|
| BSDS (후보 1·2) | 이미지당 **폐곡선 경계 다발**, 사람 GT 여러 장 | edge **인스턴스별 열린 폴리라인**, GT 1개(씬 기하 유도) | 매칭 단위가 픽셀 집합 대 인스턴스로 다르다. 이분매칭 비용이 우리에겐 과할 수 있다 |
| CULane (후보 3) | 차선 **최대 4개**, 세로로 뻗음, 두께 30 px | edge 인스턴스 개수 가변, **가로로 뻗음**, 거리에 따라 화면 길이 급변 | 30 px 두께가 해상도·거리 종속. 우리 dist_m 구간별로 다른 두께가 필요할 수 있다 |
| TuSimple (후보 4) | **고정 y 표본에서 x를 읽는** 라벨 | 자유 폴리라인 | 표본축을 뒤집어야(고정 x에서 y) 옮겨진다 |
| StairNet (후보 5) | **셀 격자 안의 선분 끝점 2개** | 임의 길이 폴리라인(끝점만으로 표현 불가) | 끝점 거리만으로는 폴리라인 중간의 굽음을 못 잰다 |

→ **제안 [클로드]**: 후보 1·2(대각선 비율)와 후보 3(띠 IoU)을 **둘 다 계산해 병기**하고, 어느 것을 정본 지표로 삼을지는 모델 단계 브리프에서 결재. 이 병기 자체는 채택이 아니므로 P1 위반이 아니다. → ❓-T3

---

## 5. 열지 못해 후보에 못 올린 것 (승용 이관)

| 대상 | 왜 필요한가 | 상태 |
|---|---|---|
| Arbeláez, Maire, Fowlkes, Malik — *Contour Detection and Hierarchical Image Segmentation* (PAMI 2011) | BSDS**500** 벤치마크의 정본 논문. `maxDist=0.0075`의 서술적 정의가 여기 있을 가능성이 높다 | **미개봉 — 승용 이관** |
| Tekin, Sinha, Fua (CVPR 2018) | StairNet 신뢰도 함수 c(x)의 원 출처 [StairNet ref 39] | **미개봉 — 승용 이관** |
| 선분 검출(line segment / wireframe) 계열의 채점 관례 | **열린 단일 선분**에 맞는 관례가 따로 있을 수 있다 — 우리 대상과 형태가 가장 가깝다 | **미조사** → ❓-T4 |

---

## 6. 결재란 ❓

| 번호 | 항목 | 담당 |
|---|---|---|
| ❓-T1 | Martin 2004의 "1% = 2.88 px" 불일치 처분 — 비율(1%)만 인용할지, 괄호 픽셀값까지 인용할지, 원인 확인 후 결정할지 | 승용 |
| ❓-T2 | StairNet `dth=1`의 단위 확정 방법 (저자 코드 확인 / 저자 문의 / 인용 포기) | 승용 |
| ❓-T3 | "대각선 비율 + 띠 IoU **병기**" 제안 채택 여부 (채택 아님, 계산·인쇄만) | 승용 |
| ❓-T4 | 선분/wireframe 검출 계열의 채점 관례 추가 조사 착수 승인 (축 C 확장 = 브리프 ❓-2 범위) | 승용 |
| ❓-T5 | 후보 2의 `thinpb=true`(채점 전 세선화)를 우리 파이프라인에도 이월할지 — 이월 시 [도구기본값] 태그로 상수 대장 등재 | 승용 |
