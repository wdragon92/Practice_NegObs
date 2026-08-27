# TOL_CANDIDATES — 선(線) 채점 허용오차 후보 기준 (**2차 확정판**)

- 1차 작성 2026-08-28 · **2차 갱신 2026-08-28** · 실행 [클로드 코드] · 브리프 `relwork_survey_brief_v4.md` §2 축 C · §5-3
- **P1 준수**: 이 문서는 **후보를 모아 원문 그대로 인쇄**할 뿐이다. 채택은 승용 결재이고, 브리프 §2-C에 따라 **채택 시점은 모델 단계 차기 브리프**다.
- **기억-작성 금지 준수**: 아래 원문 인용은 전부 **내가 실제로 연 원문 PDF 또는 공식 저장소 코드**에서 그대로 옮겼다. 열지 못한 것은 §6에 서지만 남겼다.
- **2차 변경 요약**: ① **열린 단일 선분용 관례를 찾아 후보 2로 신설**(L-CNN sAP) ② **후보 1의 "대각선 비율" 정의를 저자 코드 원전으로 확정**(❓-C3 종결) ③ **StairNet `dth` 단위는 저자 코드까지 갔으나 死코드라 미해결 → 수치 인용 금지로 확정** ④ 후보 3(띠 IoU)에 **문헌상 반대 근거**가 붙었다 ⑤ TuSimple·StairNet을 '참고' 등급으로 내렸다.

---

## 승용 요약 (6문장)

1. 선을 채점할 때 "얼마나 빗나가면 틀린 것인가"를 문헌은 네 가지로 정한다 — ⓐ **이미지 대각선 비율** ⓑ **끝점 거리(인스턴스 1:1 매칭)** ⓒ **선을 띠로 만들어 IoU** ⓓ 점 단위 고정 픽셀 거리.
2. **2차의 가장 큰 수확: 우리 대상(열린 폴리라인 1개)에 형태가 맞는 관례를 찾았다** — **L-CNN의 structural AP(sAP)**. 끝점 거리로 재고, **정답 선분당 1회만 매칭**을 강제하며, **임계 3값(ϑ=5·10·15)을 나란히 인쇄**한다.
3. **인용력이 가장 센 것은 여전히 BSDS 계열**이고, 2차에서 **정의의 원전을 확정**했다: 저자 코드 주석이 *"as a fraction of the image diagonal"* 이라고 직접 적어 두었다. 더는 2차 자료를 인용할 필요가 없다.
4. **후보 3(CULane 띠 IoU)에는 문헌상 반대 근거가 생겼다** — L-CNN 원문이 *"선이 여러 토막으로 끊겨도 히트맵은 정답과 거의 같다"* 며 이 방식의 결함을 지적한다. **병기하되 정본으로 삼는 것은 재고 대상.**
5. **StairNet `dth = 1`은 결국 인용하지 않기로 했다.** 저자 코드가 공개돼 있어 확인했으나, 그 값이 쓰이는 함수가 **어디서도 호출되지 않는 死코드**였다. 게다가 **코드 식이 논문 식과 다르다**(코드는 0~1 정규화, 논문은 비정규화). 단위 미상 → **수치 인용 금지**.
6. **Martin 2004의 "1% = 2.88 px" 불일치는 결재 지시대로 그대로 인쇄한다**(§후보 1 검산). 2차에 얻은 새 수치(코드 기본값 0.0075, 문서주석 기본값 0.01)도 이 불일치를 풀어 주지는 못했다.

---

## 후보 1 — BSDS 경계 벤치마크: **이미지 대각선 비율** 【1순위 · 인용력】

| 항목 | 내용 |
|---|---|
| 출처(원 논문) | Martin, D., Fowlkes, C., Malik, J. — *Learning to Detect Natural Image Boundaries Using Local Brightness, Color, and Texture Cues*, IEEE TPAMI **26(5):530–549 (2004)** |
| 출처(정의의 원전 — **2차 확정**) | `BIDS/BSDS500` 공식 저장소 · `bench/benchmarks/correspondPixels.m` 헤더(**David Martin, January 2003**) · `bench/source/correspondPixels.cc` |
| 수집 경로 | 논문: 프린스턴 강의 사본 PDF → `pdftotext` [코드·정독, 1차] · 코드: raw.githubusercontent.com 원문 [코드·원본, 1·2차] |
| **원문 정의 ① (논문, 그대로)** | **"Each of the curves in Figure 3 uses a fixed distance tolerance d_max = 1% of the image diagonal (2.88 pixels)."** |
| **원문 정의 ② (저자 코드 주석, 그대로 — ❓-C3의 답)** | **"[maxDist=0.01]  Maximum distance allowed between matched pixels, as a fraction of the image diagonal."** · **"[outlierCost=100]  Cost of not matching a pixel, as a multiple of maxDist."** · 함수 설명: **"Compute minimum-cost correspondance between two boundary maps. The cost of corresponding two pixels is equal to their Euclidean distance. Two pixels with dist>maxDist cannot be corresponded, with cost equal to outlierCost."** |
| **원문 정의 ③ (구현이 실제로 하는 일)** | `correspondPixels.cc`: `static const double maxDistDefault = 0.0075;` · `const double idiag = sqrt( rows*rows + cols*cols );` · `const double oc = outlierCost*maxDist*idiag;` · 그리고 `match(..., maxDist*idiag, oc, ...)` — **비율에 대각선을 곱해 픽셀로 바꾼 뒤** 매칭에 넘긴다 |
| 허용오차를 두는 **이유**(원문) | "this approach would not tolerate any localization error, and would consequently over-penalize algorithms ... since even the ground truth data contains boundary localization errors" |
| 수치 | 논문 본문 **1%** · 코드 문서주석 기본값 **0.01** · 코드 컴파일 기본값 **0.0075** · 부수: `nthresh = 99`, `thinpb = true`(채점 전 형태학적 세선화), `outlierCost = 100` |
| 민감도 관례 | 원문 Fig.14가 **허용오차를 바꿔 가며 F-measure 변화를 인쇄**한다("Panel (e) shows how the F-measure changes as a function of d_max") → 우리 CONST_LEDGER의 '2~3값 민감도' 관행과 **동일한 문헌 선례** |
| 우리에게 쓸 때 | 해상도 의존이다. 우리 렌더 해상도의 대각선을 곱해 픽셀로 환산하고, 그 환산값을 상수 대장에 **[문헌]** 으로 올려야 한다. `thinpb=true`는 **[도구기본값]** 태그가 정확하다 |

### ⚠ 검산 (침묵 수리 금지 — 결재 ❓-T1 지시대로 **두 숫자 다 인쇄**)

내가 계산한 값:

```
BSDS 표준 해상도 321 × 481  →  대각선 578.28 px
   1%    (논문 본문·코드 문서주석) = 5.78 px
   0.75% (코드 컴파일 기본값)      = 4.34 px
   논문 괄호값                      = 2.88 px
"1% = 2.88 px"가 성립하려면 대각선 = 288 px 이어야 한다
```

원문 괄호값 **2.88 px**은 BSDS 표준 해상도의 1%(**5.78 px**)와도, 코드 기본값 0.75%(**4.34 px**)와도 **맞지 않는다.** 원인은 확인하지 못했다(다운샘플 평가 가능성 등은 **추측이라 적지 않는다**).
**결재 처분(❓-T1, 승용)**: 지시에 따라 **비율(1%)을 인용하고 괄호 픽셀값은 불일치 표기와 함께 병기**한다. 2차에서 얻은 코드 기본값 두 개도 이 불일치를 해소하지 못했음을 함께 적어 둔다.

---

## 후보 2 — **L-CNN structural AP (sAP)**: 끝점 거리 + 인스턴스 1:1 매칭 【1순위 · **형태 적합성**, 2차 신설】

| 항목 | 내용 |
|---|---|
| 출처 | Zhou, Y., Qi, H., Ma, Y. — *End-to-End Wireframe Parsing*, **ICCV 2019** (arXiv 1905.03246) |
| 수집 경로 | arXiv PDF → `pdftotext`로 평가절(4.3 Evaluation Metric) 원문 확인 [코드·정독, 2차] |
| **원문 정의 (그대로)** | **"A detected line segment L_j = (p̃1_j, p̃2_j) is considered to be a true positive (correct) if and only if  min_{(u,v)∈E} ‖p̃1_j − p_u‖²₂ + ‖p̃2_j − p_v‖²₂ ≤ ϑ,  where ϑ is a user-defined number represents the strictness of the metric."** |
| **임계 (그대로)** | **"In this experiment section, we evaluate the structural AP at ϑ = 5, ϑ = 10, and ϑ = 15 under the resolution of 128×128. We abbreviate them as sAP5, sAP10, and sAP15, respectively."** — **3값 병기가 원문 관례** |
| **1:1 매칭 (그대로)** | **"each ground truth line segment is not allowed to be matched more than once in order to penalize double-predicted lines"** |
| 지표 정의 | "Structural AP is defined to be the area under the precision recall curve computed from a scored list of the detected line segments on all test images." |
| 부수 관례 | junction mAP은 **"average over 0.5, 1.0, and 2.0 thresholds under 128 × 128 resolution"** — 여러 임계의 평균이 또 하나의 관례 |
| ⚠ 단위 주의 | ϑ는 **끝점 거리의 제곱합**이며 **128×128 해상도 기준**이다. 거리 단위가 아니라 제곱 단위이므로 픽셀 거리로 옮기려면 별도 환산이 필요하다 — **원문이 환산식을 주지 않으므로 내가 만들지 않는다(P1)**. 입력 이미지는 512×512로 리사이즈하고 128×128 bin에서 평가한다고 원문에 적혀 있다 |
| **왜 우리에게 1순위인가** | 우리 대상은 **인스턴스별 열린 선분**이다. sAP는 ⓐ 픽셀 집합이 아니라 **선분 인스턴스**를 단위로 하고 ⓑ **1:1 매칭**을 강제하며 ⓒ **임계를 여러 값으로 인쇄**한다 — 세 성질이 모두 우리 요구와 맞는다 |
| 한계 | **끝점 2개**로만 재므로 폴리라인 중간의 굽음을 못 잰다(후보 5 StairNet과 같은 한계). 우리 edge가 곡선이면 그대로는 못 쓴다 |

### 후보 2가 덤으로 준 것 — **후보 3에 대한 문헌상 반대 근거**

L-CNN이 히트맵/띠 기반 채점(APH)을 비판하며 원문에 적은 문장:

> **"For example, if a long line is broken into several short line segments, the resulted heat map is almost the same as the ground truth heat map ... they do not properly evaluate the connectivity of the wireframe."**

→ **선을 띠로 만들어 IoU로 재는 방식(후보 3)은 '끊김'에 둔감하다**는 지적이다. 우리 edge는 **가림으로 끊기는 것이 본질적 현상**이므로 이 지적은 우리에게 특히 무겁다. **결재 재료로 그대로 올린다.**

---

## 후보 3 — CULane / SCNN: 선을 띠로 만들어 IoU 【2순위 · 단, 위 반대 근거 참조】

| 항목 | 내용 |
|---|---|
| 출처 | Pan, X., Zhan, X., Shi, J., Luo, P., Wang, X., Tang, X. — *Spatial As Deep: Spatial CNN for Traffic Scene Understanding*, **AAAI 2018** (arXiv 1712.06080) |
| 수집 경로 | arXiv PDF → `pdftotext`로 평가절 원문 확인 [코드·정독, 1차] |
| **원문 정의 (그대로)** | **"In order to judge whether a lane marking is successfully detected, we view lane markings as lines with widths equal to 30 pixel and calculate the intersection-over-union (IoU) between the ground truth and the prediction. Predictions whose IoUs are larger than certain threshold are viewed as true positives (TP)."** |
| 임계 | **"Here we consider 0.3 and 0.5 thresholds corresponding to loose and strict evaluations."** — 원문이 **느슨/엄격 2값을 나란히 보고**한다 |
| 지표 | `F-measure = (1+β²)·P·R/(β²P+R)`, `Precision = TP/(TP+FP)`, `Recall = TP/(TP+FN)`, **β=1** |
| 부수 상수 | 학습 시 **타깃 선 두께 16 px**, 입력 리사이즈 **800×288** (평가 두께 30 px과 **다른 값**임에 주의) |
| 우리에게 쓸 때 | **선 → 띠 → IoU**는 폴리라인 채점에 그대로 옮길 수 있는 형태다. 단 ⓐ 30 px은 800×288 기준이라 **재환산 필요** ⓑ `edge_relabel_brief_v6.md`가 정본 라벨을 **폴리라인(띠 아님)**으로 못 박았으므로 띠 두께는 **채점용 파생값**으로만 쓸 수 있다 ⓒ **위 §후보 2의 끊김 둔감성 지적을 함께 검토해야 한다** |

---

## 참고 A — TuSimple: 점 거리 고정값 + 각도 보정 【참고 등급으로 하향(2차)】

| 항목 | 내용 |
|---|---|
| 출처 | `TuSimple/tusimple-benchmark` 공식 평가 코드 `evaluate/lane.py` (클래스 `LaneEval`) [코드·원본, 1차] |
| **원문 정의 (코드 그대로)** | `pixel_thresh = 20` · `pt_thresh = 0.85` · `threshs = [LaneEval.pixel_thresh / np.cos(angle) for angle in angles]` · `np.sum(np.where(np.abs(pred - gt) < thresh, 1., 0.)) / len(gt)` |
| 해석(코드가 말하는 그대로) | ⓐ 점 하나는 **가로 거리 20 px 이내**면 정답 ⓑ 그 임계를 **선의 기울기로 나눠(1/cos θ) 보정** ⓒ 한 차선은 **점의 85% 이상**이 맞아야 매칭 성공 |
| 왜 하향했나 | 라벨이 **고정 y 표본에서의 x 값**이라는 전제가 우리와 근본적으로 다르다. 우리 edge는 가로로 뻗어 표본축을 뒤집어야 한다 |
| **그래도 살려 둘 것 하나** | **각도 보정 `1/cos θ`**. grazing angle에서 edge가 거의 수평이 되면 세로 오차와 가로 오차의 의미가 달라지므로, **거리 임계를 선 방향으로 보정하는 발상 자체**는 우리에게 유효한 문헌 선례다 |

---

## 참고 B — StairNet 끝점 거리 신뢰도 【**수치 인용 금지**로 확정(2차)】

| 항목 | 내용 |
|---|---|
| 출처 | Wang, Pei, Qiu, Tang — *Deep Leaning-Based Ultra-Fast Stair Detection* (Sci Rep 2022 / arXiv 2201.05275) [코드·정독, 1차] |
| **원문 정의 (그대로)** | **"where c(x) is the confidence and DT(x) is defined as the 2D Euclidean distance in the image space. dth is the distance threshold and is set to 1. The sharpness of the exponential function is defined by the parameter α. To achieve precise localization with this function, α is set to 2."** |
| 판정 규칙 (원문) | "a TP cell must meet the following two conditions: 1) the cell is a positive sample and is correctly predicted as a positive sample; 2) in the cell, the **location error between the predicted location of the line and the corresponding ground truth is within a certain threshold**" |
| 계승 | StairNetV2가 **"The confidence calculation is the same as that of StairNet"** 로 그대로 이월 |
| **2차 — 저자 코드 확인 결과 (❓-C2/T2)** | 저자 저장소 **`MrChenWang/StairNet-DepthOut`·`MrChenWang/StairNet-DepthIn`** 이 공개돼 있고 `utils.py`에 실물이 있다: `def dis2conf(dis, dth): alpha = 2; if dis <= dth: conf = (math.exp(alpha * (1 - dis / dth)) - 1) / (math.exp(alpha) - 1) ...` 그리고 유일한 사용처가 `calculate_cross_line`의 `return dis2conf(D1, 1) / 2 + dis2conf(D2, 1) / 2`. **그런데 `calculate_cross_line`은 두 저장소 어느 파일에서도 호출되지 않는다(死코드)** — 따라서 `D1`,`D2`가 어느 좌표계인지 코드로도 결정되지 않는다 |
| **2차 — 추가로 발견한 불일치** | **코드 식 ≠ 논문 식.** 코드는 `(e^{α(1−d/dth)} − 1)/(e^α − 1)` 로 **0~1 정규화**, 논문 식 5는 `e^{α(1−D_T/d_th)}` 로 **비정규화**(거리 0에서 e²≈7.39). 논문이 "confidence 0.5"에서 보고하므로 어느 식을 쓰느냐가 판정에 영향을 준다 |
| **2차 — 원전 대조** | 이 c(x)의 원 출처인 **Tekin, Sinha, Fua (CVPR 2018)** 은 같은 문장을 쓰면서 값을 **명시적으로 픽셀로** 준다: **"we set the sharpness of the confidence function α to 2 and the distance threshold to 30 pixels."** 즉 **원전은 픽셀, StairNet은 값만 1로 바꾸고 좌표계는 셀 정규화** — 계승 여부가 원문·코드 어느 쪽으로도 확정되지 않는다 |
| **처분** | **단위 미상 · `dth=1`을 수치로 인용하지 않는다.** 승용 결재(2026-08-28)의 "공개면 코드 확인, 아니면 단위 미상 + 수치 인용 금지" 중 **후자로 귀결**. 인용한다면 **구조(거리 → 신뢰도 → 임계)만** 인용한다 |
| 그래도 유용한 점 | **거리 → 연속 신뢰도 → 나중에 임계 스윕**이라는 3단 구조는 브리프의 *store raw, bin later* 원칙과 철학이 같다. `mFWIOU`(c=0.05~0.95, 0.05 간격 19값 평균)도 다임계 평균 관례의 사례다 |

---

## 4. 이 관례들을 우리 문제에 그대로 못 쓰는 이유 (정직 표기 · 2차 갱신)

| 관례 | 그쪽 전제 | 우리 전제 | 어긋나는 지점 |
|---|---|---|---|
| **후보 1** BSDS | 이미지당 **폐곡선 경계 다발**, 사람 GT 여러 장 | edge **인스턴스별 열린 폴리라인**, GT 1개(씬 기하 유도) | 매칭 단위가 픽셀 집합 대 인스턴스로 다르다 |
| **후보 2** sAP | **끝점 2개**로 표현되는 직선 선분, 128×128 평가 | 임의 길이·굽음 가능한 폴리라인 | 끝점만으로는 중간 굽음을 못 잰다. ϑ가 **제곱 단위**라 환산 필요 |
| **후보 3** CULane | 차선 최대 4개, 세로로 뻗음, 두께 30 px | 개수 가변, **가로로 뻗음**, 거리에 따라 화면 길이 급변 | 두께가 해상도·거리 종속. **끊김에 둔감**(§후보 2 인용) |
| 참고 A TuSimple | **고정 y 표본에서 x를 읽는** 라벨 | 자유 폴리라인 | 표본축을 뒤집어야 옮겨진다 |
| 참고 B StairNet | 셀 격자 안의 선분 끝점 2개 | 임의 길이 폴리라인 | 끝점 한계 + **단위 미상** |

### → **제안 [클로드] (채택 아님 — 승용 결재 사항임을 명기)**

승용 결재(2026-08-28)가 "계산·인쇄 제안은 좋다, **채택은 승용 몫**"이라 정했으므로 아래는 **제안으로만** 올린다.

- **❓-T3 제안(갱신)**: 정본 후보를 **후보 1(대각선 비율) + 후보 2(sAP식 끝점 1:1 매칭)** 두 축으로 **병기 계산**하고, 후보 3(띠 IoU)은 **비교용으로만** 인쇄한다. 1차 제안(후보 1 + 후보 3 병기)에서 **후보 3 → 후보 2로 교체**하는 것이 2차의 변경점이며, 이유는 ⓐ 형태 적합성(인스턴스·열린 선분) ⓑ L-CNN 원문의 끊김 둔감성 지적이다.
- **❓-T5 제안(유지)**: 후보 1의 `thinpb=true`(채점 전 세선화)를 이월한다면 **[도구기본값]** 태그로 상수 대장에 등재.
- **❓-T6 제안(2차 신설)**: 임계는 **단일값으로 정하지 말고 3값을 나란히 인쇄**한다 — 이것이 후보 1(Fig.14 민감도)·후보 2(ϑ=5·10·15)·후보 3(IoU 0.3/0.5)·참고 B(mFWIOU 19값)의 **공통 관례**다. 어느 3값인지는 우리 해상도가 정해진 뒤 결정.

---

## 5. 축 C에서 **2차에 종결된 것**

| 항목 | 처분 | 근거 |
|---|---|---|
| ❓-C3 (대각선 비율의 서술 출처) | **종결** — `correspondPixels.m` 헤더를 정본으로 인용 | 저자 코드 주석에 문구가 그대로 있다(§후보 1 원문 정의 ②) |
| ❓-T4 (선분/wireframe 계열 조사 착수) | **종결** — 조사 실시, **후보 2로 승격** | 승용 결재로 절차 항목은 자율 처리 |
| ❓-C2 / ❓-T2 (`dth` 단위) | **종결(부정형)** — 단위 미상 확정 · **수치 인용 금지** | 저자 코드가 死코드(§참고 B) |

---

## 6. 열지 못해 후보에 못 올린 것 (승용 이관)

| 대상 | 왜 필요한가 | 상태 |
|---|---|---|
| Arbeláez, Maire, Fowlkes, Malik — *Contour Detection and Hierarchical Image Segmentation* (PAMI 2011) | BSDS**500** 벤치마크의 정본 논문 | **미개봉**(Berkeley 사본 fetch 타임아웃, `SEARCH_LOG` F8) — ※ **다만 ❓-C3은 코드 원전으로 이미 해결됐으므로 우선순위가 내려갔다** |
| Vu 외 2020 (PRL, A-15) 전문 | **단안 선 그룹**을 어떤 허용오차로 채점했는지 — 우리와 형태가 가깝다 | **미개봉**(Elsevier 유료) → **축 C 신규 1순위 이관** |

---

## 7. 결재란 ❓ (승용 몫만)

| 번호 | 항목 | 담당 |
|---|---|---|
| ❓-T1 | **Martin 2004 "1% = 2.88 px" 불일치 처분** — 지시대로 두 숫자를 다 인쇄했다(§후보 1 검산). 논문 인용 시 ⓐ 비율만 쓸지 ⓑ 괄호값까지 병기할지 ⓒ 원인 확인까지 갈지 | 승용 |
| ❓-T3 | **정본 후보 조합 변경 제안** — 1차 "후보 1 + 후보 3(띠 IoU)" → 2차 "**후보 1 + 후보 2(sAP)**", 후보 3은 비교용. 채택 여부 | 승용 |
| ❓-T5 | `thinpb=true`(채점 전 세선화) 이월 여부 — 이월 시 **[도구기본값]** 태그 등재 | 승용 |
| ❓-T6 | **(2차 신설)** "임계 단일값 금지·3값 병기"를 우리 채점 규율로 고정할지 (문헌 4종의 공통 관례) | 승용 |
