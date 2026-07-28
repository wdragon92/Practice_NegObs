# E. 사실성 갭 **측정** 프로토콜 설계 — "눈으로 합격" 에서 "숫자로 증명" 으로

작성 2026-07-28 · 대상: NegObs sim2real 논문의 사실성 주장 근거 확보
관련 문서: `_context_for_agents.md`, `Docs/audit_v4/judge_v*.md`(현행 육안 심사), `user_feedback_v5_1.md`

---

## 0. 이 문서가 푸는 문제

현재 우리 파이프라인의 사실성 판정은 `judge_v5_pt_*.md` / `judge_v7_rt_*.md` 형태의
**육안 합격/불합격 심사**뿐이다. 이 방식의 구조적 한계는 셋이다.

1. **개선 효과를 증명하지 못한다.** "v5 → v8 에서 좋아졌다"는 주장이 심사자의 기준 이동
   (criterion shift)과 구분되지 않는다. 같은 이미지를 두 번 보면 두 번째가 더 좋아 보인다.
2. **논문 심사에서 방어 불가.** "사실적이다"는 문장 뒤에 붙일 수 있는 근거가 없다.
3. **어디를 고칠지 지목하지 못한다.** "장난감 같다"는 진단은 방향을 주지만 우선순위를 주지 않는다.

이 문서는 그 자리에 **3층 측정 스택**을 놓는다. 그리고 §3·§7 은 오늘 바로 돌릴 수 있게
실측 절차까지 내려간다. **실제로 오늘 파일럿을 돌려서 얻은 수치를 §3.6 에 실었다.**

> **표기 규약**
> `[확인]` = 논문·문서·URL 근거 있음 / `[측정]` = 이 조사에서 본인이 우리 데이터로 직접 계산 /
> `[추정]` = 근거 없는 판단·설계 제안

---

## §1. 결론 요약 — 권장 측정 스택 3층

| 층 | 이름 | 무엇을 재나 | 비용 | 언제 | 논문에서의 역할 |
|---|---|---|---|---|---|
| **L1 (즉시)** | 저수준 자연이미지 통계 + 도메인 판별기 | 렌더가 **자연 이미지 통계 법칙**에서 얼마나 벗어나 있나 / 얼마나 쉽게 "가짜"로 분류되나 | GPU 0~5분, 설치 0 | **오늘** | 개선 전/후 회귀 감시(regression guard). 본문 아닌 **부록·ablation** 용 |
| **L2 (중기)** | 내용 통제 분포 거리 (FD-DINOv2 / CMMD / KID) | 실사 분포와 특징공간 거리 | 실사 참조셋 확보 + 반나절 | 실사셋 확보 후 | 본문 표 1열. **단독으로는 약한 근거** |
| **L3 (최종)** | 태스크 기반 sim2real 평가 | sim으로 학습 → real 에서 실제로 되는가 | 실사 라벨 필요, 수주 | GT 파이프라인 이후 | **논문 주장의 실질적 근거. 나머지는 전부 보조** |

**핵심 권고 6개**

1. **L3 가 유일한 진짜 심판이다.** L1·L2 는 L3 를 예측하지 못한다는 근거가 반복적으로 보고돼 있다
   `[확인]`(§2.5). L1·L2 를 "사실성 증명"으로 쓰면 심사에서 깨진다. **"개선 방향 진단 도구"** 로만 써라.
2. **FID 를 InceptionV3 로 쓰지 마라.** 2023~2024 권고는 **FD-DINOv2(ViT-L/14)** 또는 **CMMD(CLIP+MMD)** 다 `[확인]`(§2.2).
3. **내용 통제(content control) 없는 FID/KID 는 무의미하다.** 우리 씬(공원·계단·제방)과 실사셋의
   **내용 구성**이 다르면 그 차이가 거리값을 지배한다. §2.6 의 3가지 통제 설계를 반드시 적용.
4. **L1 은 오늘 시작하라. 이미 결정적 진단이 나왔다.** `[측정]` 우리 PT 렌더는 실사 대비
   **고주파(f>128 cyc/img) 에너지가 9.2배 부족**, **평탄영역 노이즈 플로어가 14배 부족**,
   **로컬 RMS 콘트라스트가 4.4배 부족**하다(전부 permutation p<1e-4). §3.6.
   ★ **그리고 통제 실험으로 원인을 특정했다**: 코덱도 아니고 센서 그레인도 아니다.
   **표면 미세구조(mesostructure)의 전면 부재**다 — 실사 사진에서 가장 평탄한 상위 1% 타일조차
   우리 렌더의 가장 평탄한 1% 타일보다 **25배 더 변동한다** `[측정]`. §3.6a.
   → **노이즈·비네팅 같은 후처리로는 이 갭을 못 닫는다.** 변위·디테일 노멀·데칼·베벨·소품 엔트로피가
   필요하다. 반대로 **PT spp 를 올리는 건 무의미하다**(측정 대상이 이미 totalSpp=512 PT 결과다).
5. **실사 참조셋 확보가 전체 스택의 병목이다.** L2·L3 둘 다 실사 없이는 시작조차 못 한다. §5 최우선.
   **결론 먼저**: 로드뷰 3사는 약관상 전부 불가 `[확인]`, 한국 낙차 라벨은 **AI Hub 513/189/159** 가
   유일 `[확인]`, 오늘 즉시 가능한 건 **Wikimedia Commons(검증 완료)** 와 **ADE20K(직링크 동작 확인)** 다.
6. **사람 평가(2AFC)는 지금 하면 안 된다.** 현 상태에서 판별 정확도는 100% 에 붙을 것이고
   그건 논문에 실을 수 없는 결과다 `[추정]`. 개선 후 "정확도가 유의하게 내려갔다"를 보이는 용도로 아껴라(§6).

**논문 주장의 최종 형태 (§4 에서 도출)**

- 메인 수치는 **`Rel. = (합성으로 학습한 mIoU) ÷ (실사로 학습한 oracle mIoU)`** 단 하나다 `[확인, DAFormer CVPR 2022]`.
  *"우리 합성 데이터는 실사 상한의 XX% 를 달성한다"* — 심사위원이 이해하는 유일한 문장.
- 사실성의 **직접 증거**는 **실사 클론 페어**다 `[확인, Virtual KITTI CVPR 2016]`: 실제 낙차 현장을
  Isaac Sim 으로 재현하고 **동일 모델을 실사/렌더 양쪽에 추론**해 성능 차 Δ 를 보고한다.
  Virtual KITTI 는 Δ < 0.5% MOTA 를 사실성 증거로 사용했다. **이게 육안 심사를 대체하는 가장 강한 카드다.**
- ⚠️ **경고** `[확인, Nowruzi et al. ICML-W 2019]`: ***"photo-realism is not as important as the diversity
  of the data."*** 우리 개선이 "사실성"에만 쏠리면 이 논문으로 반박당한다. **조건 변주(계절·기상·시간대·
  재질 다양성)를 함께 늘리고, ablation 에서 사실성 기여분과 다양성 기여분을 분리**해야 한다.
- ⚠️ **씬 수가 33개뿐이라는 공격에 대한 방어** `[확인, Hypersim ICCV 2021]`:
  ***"a small, more photorealistic dataset can be competitive with a large, less photorealistic dataset."***
  Hypersim(0.5K scenes)의 이득이 PBRS(568K img)보다 컸다.

**한 문장 요약**: *오늘 L1 을 baseline 으로 고정하고 → 실사 참조셋 확보(§5)로 L2 를 열고 →
GT 파이프라인이 서면 L3 로 논문 주장을 세운다. L1 은 매 개선 커밋마다 자동 회귀 감시로 돌린다.*

---

## §2. 분포 거리 지표 — 권고와 함정

### 2.1 세 지표의 정의

| 지표 | 정의 | 편향 | 샘플 요구 |
|---|---|---|---|
| **FID** | 특징의 평균·공분산으로 가우시안을 적합하고 Fréchet(=Wasserstein-2) 거리 | **유한 표본에서 편향**, 편향량이 평가 대상 모델에 따라 다름 `[확인]` | 통상 50k 권장 |
| **KID** | 다항 커널 MMD² 의 **불편(unbiased) 추정량** | 불편 `[확인]` | 수백~수천에서 사용 가능 |
| **CMMD** | CLIP 임베딩 + **가우시안 RBF 커널 MMD²**, 불편 추정량 | 불편, 정규성 가정 없음 `[확인]` | **수백 규모에서도 안정** `[확인]` |

**FID 편향의 정확한 문제** `[확인]`: Chong & Forsyth (CVPR 2020) 는 유한 표본 FID 의 기댓값이 참값이
아니며 **편향항이 평가 대상 모델마다 다르다**는 것을 보였다. 결과적으로 *모델 A 가 모델 B 보다 좋은
점수를 받는 이유가 단지 A 의 편향항이 작아서일 수 있다*. 이 문제는 "샘플 수를 고정해서 비교"하는
것으로 해결되지 않는다. 저자들의 처방은 **FID∞**: 서로 다른 표본 수 N 에서 FID 를 K 번 계산 →
1/N 에 대해 선형회귀 → N→∞ 로 외삽.
(Chong & Forsyth, *Effectively Unbiased FID and Inception Score and Where to Find Them*, CVPR 2020,
https://arxiv.org/abs/1911.07023)

**KID** `[확인]`: Bińkowski et al., *Demystifying MMD GANs*, ICLR 2018 (https://arxiv.org/abs/1801.01401).
FID 와 달리 **단순한 불편 추정량이 존재**한다. 또 Inception 표현은 ReLU 출력이라 성분의 약 2% 가
정확히 0 이어서 **밀도조차 갖지 않는다** — FID 의 정규성 가정이 애초에 성립하지 않는 이유다.
사용하는 3차 다항 커널은 평균·분산뿐 아니라 **왜도(skewness)까지** 비교한다.
구현 관례: torchmetrics `KernelInceptionDistance` 기본값 `subsets=100`, `subset_size=1000` `[확인]`
(https://torchmetrics.readthedocs.io/en/v0.10.2/image/kernel_inception_distance.html).
→ **우리 데이터셋이 1000장 미만이면 `subset_size` 를 반드시 낮춰야 한다.** 현재 PT 렌더는 약 493장 `[측정]`.

**CMMD** `[확인]`: Jayasumana et al., *Rethinking FID: Towards a Better Evaluation Metric for Image
Generation*, CVPR 2024 (https://arxiv.org/abs/2401.09603).

- 임베딩: **CLIP ViT-L/14@336px**
- 커널: 가우시안 RBF `k(x,y)=exp(−‖x−y‖²/2σ²)`, **σ = 10**
- 추정량: 불편 MMD² (식 4). 보고값은 **×1000 스케일**
- 논문의 정량 주장: **"FID 를 신뢰성 있게 추정하려면 20,000장 이상이 필요한 반면 CMMD 는 작은
  이미지 집합에서도 일관된 추정치를 준다"**
- Inception 임베딩의 다변량 정규성은 3가지 검정에서 **p 값이 사실상 0** 으로 기각됨

### 2.2 backbone: InceptionV3 는 더 이상 기본값이 아니다

`[확인]` Stein et al., *Exposing flaws of generative model evaluation metrics and their unfair treatment
of diffusion models*, NeurIPS 2023 (https://arxiv.org/abs/2306.04675).

- 정신물리학 프로토콜로 **역대 최대 규모의 인간 사실성 평가**를 수행하고 17개 지표 × 9개 인코더를 비교
- 결론: **기존 어떤 지표도 인간 판단과 강하게 상관하지 않는다.** 특히 확산모델의 지각적 사실성이
  FID 에 전혀 반영되지 않는다
- 대안: **DINOv2-ViT-L/14 특징공간이 InceptionV3 대비 훨씬 풍부한 평가를 가능케 하고 인간 판단과
  더 잘 상관한다**
- 코드: `layer6ai-labs/dgm-eval` (17지표 × 9인코더 모듈러 라이브러리)

**우리에게 특히 중요한 이유** `[확인]`: FID 의 InceptionV3 는 **ImageNet 1000 클래스 분류**로 학습됐다.
평가 대상이 ImageNet 내용에서 멀어질수록(의료·위성·추상) 추출 특징이 관련 속성을 담지 못해
**FID 가 정보량이 없거나 오도할 수 있다**. 우리 대상(보도·계단·제방·지하도의 **지면 텍스처와 미세기하**)은
ImageNet 객체 중심 표현이 가장 못 잡는 축이다 `[추정]`.

**권고 조합** `[추정, 근거는 위 두 논문]`:

| 순위 | 지표 | 이유 |
|---|---|---|
| 1 | **FD-DINOv2 (ViT-L/14)** | 인간 판단 상관 최선, 자기지도라 클래스 편향 없음 |
| 2 | **CMMD (CLIP ViT-L/14@336, σ=10)** | 불편 + 소표본 안정 → **우리처럼 493장뿐인 상황에 딱** |
| 3 | KID (DINOv2 특징 위에서) | 불편, `subset_size` 로 소표본 대응 |
| ✗ | FID (InceptionV3) | **관례상 1줄만 병기**. 리뷰어가 물어볼 때를 위한 것이지 근거가 아님 |

비공식 FD-DINOv2 구현 참고: https://github.com/justin4ai/FD-DINOv2 — 문서상 **각 집합당 2048장 이상**
권장 `[확인]`. 우리 493장은 이 하한 아래다 → **CMMD 우선**이라는 결론을 다시 지지.

### 2.3 함정 1 — 샘플 수 하한

| 지표 | 실무 하한 | 근거 |
|---|---|---|
| FID | 20,000+ (신뢰 가능한 추정), 관례 50,000 | CMMD 논문 `[확인]` |
| FD-DINOv2 | 2,048+ | 구현 문서 `[확인]` |
| KID | subset_size 를 데이터 크기 이하로 낮추면 수백에서도 가능 | torchmetrics `[확인]` |
| CMMD | 수백 `[확인]` |

**우리 상황의 진짜 문제는 장수가 아니라 유효 표본 수다** `[측정]`.
PT 렌더 493장은 **21개 씬 × 씬당 중앙값 26뷰**다. 같은 씬의 26뷰는 통계적으로 독립이 아니다.
**유효 표본 수는 493 이 아니라 21 에 가깝다** `[추정]`.
→ 어떤 분포 거리도 **씬 단위 부트스트랩**으로 신뢰구간을 붙이지 않으면 숫자가 무의미하다.

> **처방**: 씬을 단위로 재표집(scene-level bootstrap, B=1000)해서 CMMD 의 95% CI 를 보고할 것.
> 씬 내부 뷰를 섞어 재표집하면 CI 가 심하게 과소추정된다 `[추정]`.

### 2.4 함정 2 — 해상도 / 리사이즈 / 압축 정책

`[확인]` Parmar, Zhang, Zhu, *On Aliased Resizing and Surprising Subtleties in GAN Evaluation*,
CVPR 2022 (https://arxiv.org/abs/2104.11222), 코드 `GaParmar/clean-fid`.

- **저수준 전처리 차이(리사이즈·압축)만으로 지표가 크게 흔들린다**
- 다운샘플 시 프리필터 폭을 배율에 맞게 조정해야 하는데, OpenCV/TensorFlow/PyTorch **기본 플래그 구현은
  고정폭 프리필터를 써서 심한 에일리어싱 아티팩트를 만든다**
- JPEG 기본 파라미터 저장은 양자화와 저수준 통계 차이를 추가로 주입한다

**우리 상황에 치명적인 이유** `[추정]`: 우리 렌더는 **1920×1080 PNG(무압축)**, 실사 참조는 대부분
**JPEG, 임의 해상도**다. 아무 처리 없이 FID 를 재면 **"PNG vs JPEG" 와 "리사이즈 커널" 이 결과를
지배**하고, 정작 재려던 사실성 차이는 묻힌다.

> **처방 (전처리 계약, 양쪽에 동일 적용)**
> 1. 원본에서 **정사각 센터 크롭 후 리사이즈** — 종횡비 왜곡 금지
> 2. 리사이즈는 **PIL bicubic + antialias=True** 하나로 통일하고 문서에 명시(clean-fid 관례)
> 3. **양쪽 다 동일 품질의 JPEG 로 재인코딩**(예: quality=95) 하거나 **양쪽 다 PNG** 로 통일.
>    섞지 마라
> 4. 처리 후 해상도를 **DINOv2 는 224 또는 518, CLIP@336 은 336** 으로 고정
> 5. 전처리 스크립트를 **결과와 함께 커밋**해서 재현 가능하게

### 2.5 함정 3 — FID 는 downstream 성능을 예측하지 못한다

`[확인]` 이건 우리 논문 전략에 직결되는 사실이다.

- FID 를 낮춰도 세그멘테이션(Dice)·분류(F1) 성능이 개선되지 않고 **반대로 움직이는 경우**가 보고됨
- "FID 개선은 어느 모델에서도 합성 데이터의 증강 효과에 유의한 영향을 주지 않았다 →
  **FID 최적화는 합성 데이터의 유용성을 높이는 좋은 방법이 아니다**"
- FID 가 매우 낮은데 downstream F1 은 압도적으로 최악인 사례 존재
- 권고: **FID 대리 대신 downstream 태스크 영향을 직접 평가하라**

`[확인]` SADGE (*Structure and Appearance Domain Gap Estimation of Synthetic and Real Data*,
https://arxiv.org/html/2605.22467v1) 도 같은 진단에서 출발한다:

- FID·CLIP·LPIPS 는 **의미적 정합만 재고 구조적 일관성을 못 잡는다**
- **"외양이 그럴듯해도 기하 대응이 안 맞으면 downstream 성능을 예측하지 못한다"**
- 제안: 외양 유사도(DINOv3 ViT-L 임베딩 코사인) × 기하 유사도(MASt3R 밀집 대응의 기하검증 inlier 수)를
  이중선형 결합. `SADGE = a·Ĝ + b·Â + c·ĜÂ`
- 결과: downstream 성능과 **Pearson r = 0.879, Spearman ρ = 0.768** (n=15, p≈8.3e-4).
  기하 단독 ρ=0.582, 외양 단독 ρ=0.536 대비 유의하게 우수
- 인코더 스윕에서 **DINOv3(ViT-L) 이 FID·DINOv2·SigLIP·SAM·CLIP·LPIPS 중 최선**으로 선택됨

> **논문 전략 함의** `[추정]`: 우리 논문에서 FID/CMMD 를 **"사실성의 증거"** 로 쓰면 위 논문들을
> 인용한 리뷰어에게 정확히 반박당한다. 대신 이렇게 프레이밍해야 한다 —
> *"분포 거리는 개선의 방향성을 확인하는 진단 지표로만 사용했고, 사실성 주장은 §4 의
> 태스크 기반 전이 성능으로 뒷받침한다."*

### 2.6 함정 4 (가장 중요) — **내용 통제(content-controlled) 비교 설계**

**문제**: FID/CMMD/KID 는 **분포 간 거리**다. 두 분포가 다른 이유가 (a) 렌더 사실성인지
(b) 찍힌 내용이 다른 건지 구분하지 못한다. 우리 씬은 공원·계단·제방인데 참조셋이 Cityscapes(차도)면
**측정값의 대부분은 "공원 vs 차도"** 이지 "렌더 vs 사진" 이 아니다 `[추정, 지표 정의상 자명]`.

**설계 A — 실사 하한(floor)과 상한(ceiling)을 반드시 같이 보고** ★가장 저렴하고 효과 큼

```
floor   = d(Real_A, Real_B)        # 실사셋을 무작위 반분한 두 조각 사이 거리
ceiling = d(Real,  Noise/Shuffle)  # 완전 무관한 분포와의 거리 (예: 실내 데이터셋)
ours    = d(Syn,   Real)
정규화 갭 = (ours − floor) / (ceiling − floor)
```
`[추정, 관례적 실무]` 하한 없이 "CMMD = 1.8" 을 보고하는 것은 해석 불가능하다.
같은 실사셋을 반분한 거리가 1.2 라면 1.8 은 사실 매우 가깝다는 뜻이고,
0.05 라면 1.8 은 참사라는 뜻이다. **하한/상한 정규화는 리뷰어 질문을 미리 막는다.**

**설계 B — 내용 매칭 표집 (semantic layout matching)**
`[확인]` Content-Consistent Matching (CCM) for Domain Adaptive Semantic Segmentation, ECCV 2020
(https://link.springer.com/chapter/10.1007/978-3-030-58568-6_26) 은 **의미 레이아웃 행렬**로
실사 이미지와 유사한 레이아웃의 합성 이미지를 골라내는 방식을 쓴다.

우리 적용 `[추정]`:
1. 양쪽 이미지 전부에 사전학습 세그멘터(예: Mask2Former/SegFormer ADE20K)를 돌려 **클래스 점유율 벡터**
   (예: road/sidewalk/stairs/vegetation/building/sky 6~10차원)를 뽑는다
2. 실사 이미지마다 **점유율 벡터가 가장 가까운 합성 이미지**를 매칭(헝가리안 또는 최근접)
3. **매칭된 부분집합끼리만** 분포 거리를 계산
→ 이러면 "내용 차이" 성분이 크게 제거되고 남는 게 렌더 사실성에 가까워진다

**설계 C — 디지털 트윈 페어링(가장 강력, 가장 비쌈)**
`[확인]` Synscapes (Wrenninge & Unger 2018, https://arxiv.org/abs/1810.08705) 는 Cityscapes 와 **동일한
19 클래스, 유사한 구조·내용**으로 25,000장을 만들었다 — 애초에 내용 통제를 데이터셋 설계에 내장한 것.
`[확인]` KITTI–VirtualKITTI2 매칭 쌍도 "시뮬레이터가 실제 씬을 재현하고, 합성 테스트 결론이 대응하는
실제 상황으로 전이되는지"를 검증하는 clone/regression 체제로 쓰인다.

우리 적용 `[추정]`: **TurtleBot3 로 캠퍼스 계단·연석을 촬영 → 같은 장소를 Isaac Sim 에 재현 → 동일
카메라 위치·자세에서 렌더**. 20~30 쌍이면 충분하다. 이건 §5.6 자체 촬영과 통합하면 추가 비용이 거의 없고,
논문 그림으로도 **"실사 | 우리 렌더" 나란히 배치**가 가능해 설득력이 압도적이다.

**설계 D — 클래스별/조건별 층화 보고**
전체 CMMD 하나가 아니라 **씬 유형별(계단/제방/지하도/공원) × 카메라 높이(0.3/0.9/1.8m)** 로 쪼개
보고한다. 우리 `manifest.json` 에 `eye`/`tgt` 가 이미 저장돼 있어 층화가 공짜다 `[측정]`.
→ "어떤 씬 유형이 가장 갭이 큰가"는 개선 우선순위를 직접 준다.

### 2.7 합성 데이터 논문들의 실제 FID 보고 관행

`[확인]` 조사 결과 **GTA5/SYNTHIA/Synscapes/Hypersim 같은 주요 합성 데이터셋 논문들은 FID 를
자기 데이터셋의 품질 근거로 전면에 내세우지 않는다.** 이들의 핵심 표는 전부
**"합성으로 학습 → 실사에서 mIoU"** 형태의 전이 성능이다.
FID 는 주로 **생성모델(GAN/diffusion) 논문**과 **image-to-image 도메인 적응 논문**에서
"변환 후 실사 도메인에 얼마나 가까워졌나"를 보이는 데 쓰인다.

> **우리에게 주는 교훈** `[추정]`: 선행 연구가 안 하는 방식으로 주장을 세우지 마라.
> **FID 는 부록. 본문은 §4 의 전이 성능 표.**

---

## §3. 저수준 자연이미지 통계 진단 — 실행 가능한 계산 절차

이 절이 **오늘 바로 돌릴 수 있는** 부분이다. 의존성은 **numpy + PIL** 뿐이며,
현재 venv(`/home/vislab/Desktop/work_sy/.venv`, numpy 2.2.6, pillow 12.2.0)에 이미 있다 `[측정]`.
scipy·opencv 는 필요 없다.

### 3.0 왜 이게 진단으로 유효한가

`[확인]` 자연 이미지는 우연이 아니라 **통계적 법칙**을 따른다 — 파워 스펙트럼의 1/f 스케일링,
미분 응답의 heavy-tail, 스케일 불변성 등. 이 법칙에서의 이탈은 **정량화 가능한 "비자연성"** 이다.
(Ruderman & Bialek, *Statistics of Natural Images: Scaling in the Woods*, NIPS 1993 /
Phys. Rev. Lett. 73, 814;
Huang & Mumford, *Statistics of Natural Images and Models*, CVPR 1999;
Field 1987; van der Schaaf & van Hateren, *Modelling the Power Spectra of Natural Images*,
Vision Research 1996)

`[확인 — 단, 원문 초록 직접 확인 실패]` 컴퓨터 그래픽스 쪽에서도 직접 다뤄졌다:
Reinhard, Shirley, Ashikhmin, Troscianko, *Second order image statistics in computer graphics*,
APGV 2004 (https://dl.acm.org/doi/10.1145/1012551.1012568) — 검색 요약 기준 결론은
**"2차 통계는 주로 기하 모델링에서 비롯되며 렌더링 파라미터 선택에는 거의 영향받지 않는다"**.
우리 상황(전부 USD 프리미티브, 베벨 0, 변위 0)에 정확히 들어맞는다 —
**PT 로 spp 를 올려도 2차 통계는 안 고쳐진다는 뜻**이다.
※ ACM DL 403, Semantic Scholar 는 출판사 요청으로 초록이 삭제돼 **원문 문장을 직접 인용하지 못했다.
논문에 인용하기 전 반드시 원문(도서관 접근)으로 확인할 것.**
후속 정리: Pouli, Cunningham, Reinhard, *A Survey of Image Statistics Relevant to Computer Graphics*,
Computer Graphics Forum 30(6), 2011.
※ 다만 이 주장은 **§3.6 의 우리 실측이 독립적으로 지지**한다 — 측정 대상이 `RaytracedLighting` 이 아니라
**totalSpp=512 PathTracing 결과물**인데도 HF 에너지가 9.2배 부족했다 `[측정]`.

`[확인]` 법의학(forensics) 계열이 같은 통계로 **CG vs 사진 판별기**를 만들어 왔다:
Lyu & Farid, *How realistic is photorealistic?*, IEEE TSP 2005; Farid & Lyu, *Higher-order wavelet
statistics and their application to digital forensics*, CVPR Workshop 2003.
→ **저수준 통계로 CG 를 잡아낼 수 있다는 것이 20년간 확립된 사실**이며,
이는 우리 렌더가 그 판별기에 잡힌다면 실제로 비자연적이라는 뜻이다.

### 3.1 지표 1 — 파워 스펙트럼 기울기 (1/f 법칙)

**계산 절차**

```
1) sRGB → 선형 RGB → 휘도 L = 0.2126R + 0.7152G + 0.0722B
2) X = log(L + 1e-4),  X ← X − mean(X)            # 로그 휘도: 스케일 불변성 분석의 표준
3) 2D Hann(또는 Lanczos) 윈도우 W 를 곱한다        # 스펙트럼 누설/wraparound 억제 — 필수
4) P = |fftshift(fft2(X·W))|²
5) 중심에서의 반경 r 로 P 를 **방사 평균(radial average)** → 1D 프로파일 prof(f)
6) log prof(f) 를 log f 에 대해 **최소제곱 직선 적합**, 대역 f ∈ [10, 256] cycles/image
   → 기울기 α  (관례: P(f) ∝ f^α)
```

**기대 수치** `[확인]`

| 대상 | 파워 스펙트럼 기울기 α | 출처 |
|---|---|---|
| 자연 풍경 사진 | **−2.03 ± 0.33** | Koch et al., PLOS ONE 2010, 5(8):e12268 (10–256 cyc/img, lanczos 윈도우) |
| 만화/코믹/망가 | −1.99 ~ −2.08 | 동일 |
| 얼굴 사진(클로즈업) | −3.54 ± 0.15 | 동일 |
| 과학 일러스트 | −1.57 ± 0.32 | 동일 |
| 진폭 스펙트럼 기울기(= α/2) | 평균 −1.2 (범위 −0.8 ~ −1.5) | van der Schaaf & van Hateren 1996 |

> **중요한 주의** `[확인]`: 위 PLOS 연구의 결론은 *"만화·코믹은 1D 방사평균 기울기로는 사진과
> 구분되지 않는다. 구분되는 건 **방위 이방성(isotropy)** 이다"* 였다 — 예술·만화가 사진보다
> **더 등방적**(방위별 평균 파워의 변동이 작음). **따라서 기울기 하나만 보면 안 되고
> 방위별 통계를 반드시 같이 봐야 한다.**

**방위 이방성 계산** `[확인, 위 논문 방식]`: 파워 스펙트럼을 32등분(16개 분석)하고
(a) 섹터별 평균 파워의 표준편차 = *power anisotropy*, (b) 섹터별 기울기의 표준편차 = *slope anisotropy*.

### 3.2 지표 2 — 그래디언트/에지 통계

```
X = log(L + 1e-4)
gx = diff(X, axis=1);  gy = diff(X, axis=0);  g = concat(gx, gy) − mean
표준편차 σ_g,  첨도 κ = E[g⁴]/σ_g⁴
GGD 형상모수 β: 커널 |g|^β 형태로 적합하거나 첨도로부터 역산
```

**기대 수치** `[확인]`

- 자연 이미지 미분 분포는 **heavy-tailed, 고첨도**. 국소적으로 매끄러운 영역(작은 차분) + 에지(큰 차분)의 혼합
- 보고된 첨도: 그래디언트 필터 응답에서 **κ ≈ 6.6**, 로그 히스토그램 기준 수평 미분에서 **κ ≈ 17.4**
- GGD 형상모수 **β ≈ 0.78** 부근 (β=2 가우시안, β=1 라플라시안, β<1 이 더 무거운 꼬리)
- 이 비가우시안 구조는 **스케일에 대해 불변** — 이미지를 줄여도 유지된다

**우리 렌더에서 기대되는 이탈 방향** `[추정 → §3.6 에서 측정으로 확인됨]`:
평면 위 타일 텍스처 + 베벨 없는 하드 에지 = **"거의 평탄한 고원 + 극단적으로 날카로운 소수의 에지"**
→ σ_g 는 작고 κ 는 비정상적으로 크다.

### 3.3 지표 3 — 로컬 콘트라스트

```
16×16(또는 32×32) 비중첩 타일마다  RMS 콘트라스트 c = std(L)/mean(L)
전체 타일에 대한 중앙값·90퍼센타일을 보고
```
`[추정]` 절대 기대치는 콘텐츠 의존이 커서 문헌 단일값이 없다. **반드시 실사 참조셋과의 상대 비교**로 쓴다.

### 3.4 지표 4 — 색도 분포

```
Ruderman 로그 대립색 좌표:
  l = (log R + log G + log B)/√3
  α = (log R + log G − 2 log B)/√6      # 황–청 축
  β = (log R − log G)/√2                # 적–녹 축
보고: std(l), std(α), std(β), 채도 s = max(RGB) − min(RGB) 의 평균/표준편차
추가: 채널 간 상관계수 행렬 (자연 이미지는 R·G·B 상관이 매우 높다)
```
`[확인]` 로그 대립색 공간에서 자연 이미지의 채널이 크게 탈상관된다는 것이 Ruderman et al. 의 결과.
`[추정]` 우리 렌더는 **상수 틴트 기반 OmniPBR** 이라 α·β 의 분산이 실사보다 작고,
반면 채도 평균은 (만화적 초록 등으로) 오히려 높을 수 있다.

### 3.5 지표 5 — 노이즈 파워 / 노이즈 플로어 ★우리 케이스의 핵심

우리 파이프라인은 **OptiX denoiser on** 이고 센서 모델이 전혀 없다 → **평탄 영역에 그레인이 0** 이다.
실사 사진은 반드시 광자 산탄잡음 + 읽기잡음을 갖는다.

```
1) X = log(L + 1e-4)
2) 라플라시안 고역통과: lap = X[+1]+X[−1]+X[:,+1]+X[:,−1] − 4X
3) 8×8 타일로 나눠 타일별 robust sigma:  σ_t = 1.4826·MAD(lap_t) / √20
   (√20 = 라플라시안 커널의 잡음 이득 √(4·1²+(−4)²) = √20)
4) **가장 평탄한 하위 10% 타일의 σ** 를 노이즈 플로어로 보고
   (구조가 없는 영역만 골라야 진짜 잡음만 남는다)
```
`[확인]` 센서 효과 모델링이 sim2real 갭을 실제로 줄인다는 직접 근거:
Carlson, Skinner, Vasudevan, Johnson-Roberson, *Modeling Camera Effects to Improve Visual Learning
from Synthetic Data*, ECCV Workshops 2018 (https://arxiv.org/abs/1803.07721).
**색수차·블러·노출·노이즈·색온도**를 물리 기반으로 랜덤화하는 파이프라인으로 도시 주행 객체 검출의
sim2real 갭을 줄였고, **증강된 2,975장이 미증강 20,000장 이상을 능가**했다.
→ 우리 §7 의 "센서 효과 후처리" 작업 항목의 근거가 바로 이것이다.

### 3.6 ★ 오늘 실측한 파일럿 결과 `[측정]`

**방법**: 각 이미지에서 **네이티브 해상도 1024×1024 센터 크롭**(리샘플 일절 없음 — §2.4 함정 회피),
로그 휘도, Hann 윈도우, 방사 평균, 위 절차 그대로.
**A = 우리 PT 렌더 120장** (`look_check/scene*/v*_pt/pt_*.png`).
**B = 실사 사진 36장** — Wikimedia Commons API 로 수집(보도·옥외계단·제방·지하도·공원길 질의).
유의성은 **20,000회 순열검정(permutation test)**, 양측.

| 지표 | A: 우리 PT 렌더 (n=120) | B: 실사 사진 (n=36) | 차이 | p |
|---|---|---|---|---|
| 파워스펙트럼 기울기 α (10–256 cyc/img) | **−2.70 ± 0.27** | **−1.94 ± 0.62** | −0.76 | **< 1e-4** |
| 기울기 α (256–480, 미세대역) | −3.71 ± 0.43 | −3.17 ± 1.10 | −0.54 | 1e-4 |
| 기울기 α (10–64, 대구조) | −2.54 ± 0.41 | −2.14 ± 0.42 | −0.40 | — |
| **고주파 에너지 비율 (f > 128)** | **0.0039** | **0.0359** | **9.2× 부족** | **< 1e-4** |
| **고주파 에너지 비율 (f > 256)** | **0.0007** | **0.0161** | **23× 부족** | — |
| **노이즈 플로어(평탄 10% 타일)** | **0.0042** | **0.0593** | **14× 부족** | **< 1e-4** |
| 노이즈 플로어(중앙값 타일) | 0.0284 | 0.2216 | 7.8× 부족 | — |
| **로컬 RMS 콘트라스트(16px 중앙값)** | **0.109** | **0.482** | **4.4× 부족** | **< 1e-4** |
| 그래디언트 표준편차 σ_g | 0.206 | 0.653 | 3.2× 부족 | < 1e-4 |
| **그래디언트 첨도 κ** | **96.4** | **18.4** | **5.2× 과다** | — |

보조 실험(1024 리사이즈 버전, 방위 통계 포함):

| 지표 | 우리 PT (n=40) | 실사 (n=44) | 참고: look_refs (nanobanana AI 생성, n=17) |
|---|---|---|---|
| 기울기 α | −2.50 ± 0.21 | **−2.01 ± 0.49** | −2.04 ± 0.38 |
| power anisotropy (섹터 평균파워 SD) | **0.934** | 0.491 | 0.595 |
| slope anisotropy | 0.208 | 0.188 | 0.342 |
| log-휘도 표준편차 | 1.04 | 1.72 | 1.23 |
| 평균 채도 | **0.104** | 0.086 | 0.060 |

**해석**

1. **추정기 검증 통과** `[측정+확인]`. 우리가 수집한 실사 36~44장의 기울기 **−1.94 ~ −2.01** 은
   문헌의 자연 풍경 값 **−2.03 ± 0.33**(PLOS ONE 2010)과 일치한다. 즉 **파이프라인이 옳다.**
2. **우리 렌더의 대표 결함은 "고주파 결손"** 이다. 기울기가 0.76 더 가파르고, f>128 대역 에너지가
   **9.2배**, f>256 대역이 **23배** 부족하다. 원인은 브리프의 진단과 정확히 일치한다 —
   메시 0건, 베벨 0건, 변위/테셀레이션 0건, 잔디 지오메트리 없음, 데칼 없음, 소품 엔트로피 없음.
3. **노이즈 플로어 14배 부족**은 단일 항목으로 가장 고치기 쉬우면서 가장 큰 통계 개선을 줄 항목이다
   `[추정]`. OptiX denoiser 후 **센서 노이즈를 후처리로 재주입**하면 된다(§7-S3).
4. **로컬 콘트라스트 4.4배 부족 + 첨도 5.2배 과다**는 "평탄한 고원 + 하드 에지"의 정량적 지문이다.
   §3.2 에서 예측한 이탈 방향이 그대로 확인됐다.
5. **방위 이방성이 실사의 1.9배**. 축정렬 박스 기하 + 월드 트라이플래너 타일링이 수평·수직 방향에
   에너지를 몰아넣고 있다는 증거 `[추정]`. 흥미롭게도 PLOS 논문의 만화 판별 축(등방성)과는
   **반대 방향**이다 — 우리 문제는 "만화적"이라기보다 **"CAD 적"** 이다.
6. **채도는 실사보다 오히려 높다**(0.104 vs 0.086). "게임 같다"는 사용자 지적의 색채적 근거.

**이 파일럿의 한계** `[추정]`

- 실사 36장은 **내용이 통제되지 않았다**. 실사 쪽에 사람·차량·간판·나뭇잎 같은 고주파 콘텐츠가
  더 많다면 HF 비율 차이의 일부는 사실성이 아니라 **내용 밀도** 차이다.
  → §2.6 설계 B/C 로 통제해야 최종 수치가 된다. **다만 노이즈 플로어(평탄 타일 하위 10%)는
  내용 밀도의 영향을 구조적으로 적게 받으므로 이 항목의 14배 차이는 상대적으로 견고하다.**
- 실사는 JPEG 압축을 거쳤다 — JPEG 은 고주파를 **제거**하는 방향이므로 위 차이는 **보수적**이다
  (압축 없는 원본이면 격차가 더 벌어진다).
- 표본이 작다(실사 36). CI 를 붙여 재보고할 것.

### 3.6a ★★ 통제 실험 — "센서 노이즈만 넣으면 된다"는 가설은 **기각됐다** `[측정]`

§3.6 의 결과를 보고 나오는 자연스러운 결론은 *"OptiX denoiser 때문에 그레인이 없으니 후처리로
노이즈를 넣으면 된다"* 이다. **그 가설을 오늘 직접 검증했고, 기각됐다.** 이건 §7-S3 의 계획을
근본적으로 바꾼다.

#### 통제 1 — JPEG 압축이 원인인가? → **아니다**

우리 렌더는 PNG, 실사는 JPEG 이므로 코덱이 교란요인일 수 있다. 렌더를 q=95 JPEG 으로 재인코딩해 재측정:

| | slope(10–256) | hf_frac_128 | hf_frac_256 | noise_floor_p10 | lc_med | grad_kurt |
|---|---|---|---|---|---|---|
| 렌더 PNG (n=60) | −2.6144 | 0.00520 | 0.00105 | 0.00561 | 0.1066 | 63.7 |
| 렌더 JPEG q95 | −2.6165 | 0.00519 | 0.00106 | 0.00590 | 0.1076 | 61.8 |

→ **모든 지표가 사실상 동일하다. 갭은 코덱 아티팩트가 아니다.**
(오히려 JPEG 은 고주파를 **제거**하므로, 실사 쪽이 JPEG 이라는 사실은 §3.6 의 격차를
**보수적으로 과소평가**하게 만든다.)

#### 통제 2 — 광자 산탄잡음을 넣으면 노이즈 플로어가 메워지는가? → **비현실적 강도에서만**

선형 공간에서 `σ = sqrt(I/K)` 광자 산탄잡음을 주입하며 K(전자 수)를 스윕 (렌더 30장):

| K | 18% 그레이에서의 상대 그레인 σ | noise_floor_p10 | hf_frac_128 |
|---|---|---|---|
| 12,000 | 2.15% | 0.0132 | 0.00413 |
| 3,000 | 4.30% | 0.0201 | 0.00425 |
| 800 | 8.33% | 0.0333 | 0.00471 |
| **200** | **16.67%** | **0.0615** | 0.00650 |
| 50 | 33.33% | 0.1192 | 0.01210 |
| **실사 목표값** | — | **0.0593** | **0.0359** |

**두 가지가 드러난다.**
1. 노이즈 플로어를 실사 수준(0.0593)까지 올리려면 **K ≈ 200, 즉 중간회색에서 16.7% 상대 그레인**이
   필요하다. 주간 옥외 사진(ISO 100~800)의 실제 그레인은 **2% 미만**이다 `[추정, 센서 물리]`.
   **즉 "실사의 노이즈 플로어"는 센서 노이즈가 아니다.**
2. 그 비현실적 강도에서조차 **hf_frac_128 은 0.0065 로, 실사 0.0359 의 5.5분의 1에 그친다.**
   → **노이즈 주입은 고주파 결손을 메우지 못한다.**

#### 통제 3 — 실사 사진에 "평탄한 영역"이 존재하는가? → **존재하지 않는다**

8×8 로그휘도 타일 표준편차의 분위수:

| | p1 | p5 | p10 | p25 | p50 |
|---|---|---|---|---|---|
| **우리 렌더** | 0.00190 | 0.00818 | 0.01515 | 0.02803 | 0.06535 |
| **실사 사진** | 0.04727 | 0.09561 | 0.14150 | 0.26374 | 0.46445 |
| 배율 | **24.9×** | 11.7× | 9.3× | 9.4× | 7.1× |

**실사 사진에서 가장 평탄한 상위 1% 타일조차 우리 렌더의 가장 평탄한 1% 타일보다 25배 더 변동한다.**
→ 실사에는 **평탄한 표면이 없다.** 아스팔트·콘크리트·보도블록·흙·풀 — 모든 표면이 모든 스케일에서
미세 구조를 갖는다. 우리 렌더의 "평탄 슬래브 + 4K 타일링 텍스처"는 그 미세 구조를 **텍스처 해상도
아래에서 완전히 잃는다**.

#### ★ 결론 — 진단이 바뀐다

> **우리 렌더의 결손은 "센서 그레인 부재"가 아니라 "표면 미세구조(mesostructure) 전면 부재"다.**
> 노이즈·비네팅·수차 같은 **후처리는 이 갭을 못 메운다.** 필요한 것은
> **변위/디테일 노멀·머티리얼 미세 러프니스 변조·데칼·소품 엔트로피·지오메트리 자체의 불규칙성**이다.
>
> 이건 Reinhard et al. 2004 의 *"2차 통계는 기하 모델링에서 온다"* 와 정확히 같은 결론이며,
> 이번엔 **우리 데이터로 독립 확인**했다 `[측정]`.

**§7-S3 수정**: 센서 후처리는 여전히 **싸고 무해하며 실사 사진의 저수준 지문(노출/AWB 지터,
약한 비네팅, 색수차, JPEG)을 맞추는 데 유용**하지만, **NIS-Gap 을 닫는 주력이 아니다.**
S3 는 "빠른 이득"이 아니라 **"후처리로 닫을 수 없는 잔차를 정량화해서 기하/재질 작업을
정당화하는 실험"** 으로 재정의한다. 그 잔차가 바로 렌더 파이프라인 개편의 근거가 된다.

### 3.7 지표 6 — 도메인 판별기 (Proxy A-distance) `[측정]`

**근거** `[확인]`: Ben-David et al., *A theory of learning from different domains* (Machine Learning
2010) 의 H-divergence 를 실무에서 근사하는 표준 방법이
**Proxy A-distance: `d_A = 2(1 − 2ε)`** — ε 은 도메인 판별기의 일반화 오차.
d_A 가 낮을수록 두 도메인이 잘 정렬됐다는 뜻.

**오늘 실측** `[측정]`: ImageNet 사전학습 ResNet18 penultimate 특징(512d) + 로지스틱 프로브,
224×224 랜덤 크롭 4개/이미지, **씬/사진 단위 그룹 5-fold 교차검증**(같은 씬이 train/test 에 동시에
들어가지 않도록).

```
balanced accuracy = 0.928 ± 0.069
Proxy A-distance  = 1.71   (0 = 구분 불가, 2 = 완전 분리)
```

→ **거의 완전 분리**. 224px 짜리 작은 크롭만 봐도 ImageNet 백본이 우리 렌더를 92.8% 로 잡아낸다.

**중요한 경고** `[확인]`: proxy A-distance 가 전이 성능과 **상관하지 않는다**는 반례가 보고돼 있다 —
어떤 방법은 가장 낮은 오차율을 달성하면서도 source-only 베이스라인 대비 A-distance 를 유의하게
줄이지 않았고, 전반적으로 A-distance 와 타깃 도메인 성능 사이에 상관이 관찰되지 않았다.
→ **d_A 를 "갭의 크기"로 보고하되 "전이가 될 것"의 근거로 쓰지 마라.** 방향 지표로만.

### 3.8 L1 종합 스코어카드 서식 (논문 부록용)

| 지표 | 실사 참조 | v7 (현재) | v9 (개선 후) | 정규화 갭 |
|---|---|---|---|---|
| 스펙트럼 기울기 α | −1.94 | −2.70 | ? | \|Δα\| |
| HF 비율 (f>128) | 0.0359 | 0.0039 | ? | ratio 9.2× |
| HF 비율 (f>256) | 0.0161 | 0.0007 | ? | ratio 23× |
| 노이즈 플로어(평탄 10%) | 0.0593 | 0.0042 | ? | ratio 14× |
| ★ **평탄 1% 타일 SD** | 0.0473 | 0.0019 | ? | **ratio 24.9×** ← 가장 민감 |
| 로컬 콘트라스트 | 0.482 | 0.109 | ? | ratio 4.4× |
| 그래디언트 첨도 | 18.4 | 96.4 | ? | ratio 5.2× (역방향) |
| power anisotropy | 0.491 | 0.934 | ? | ratio 1.9× (역방향) |
| **Proxy A-distance** | 0 (하한) | **1.71** | ? | 그대로 |

**단일 요약 스칼라 제안** `[추정]`: 위 항목을 각각 `|log(ours/real)|` 로 변환해 평균 →
**NIS-Gap (Natural Image Statistics Gap)**. 개선 커밋마다 이 한 숫자가 내려가는지 감시.
기울기는 `|Δα|` 를 그대로, 역방향 지표(첨도·이방성)는 비율의 로그 절대값을 쓰면 부호가 자동 정리된다.

⚠️ **"평탄 1% 타일 SD" 를 반드시 포함하라** `[측정, §3.6a]`. 24.9배로 **가장 큰 격차**를 보이며,
내용 밀도 차이의 영향을 가장 적게 받는(= 가장 견고한) 지표다. 그리고 이 항목이야말로
**후처리로 위조하기 어렵고 실제 자산 개선에만 반응**한다 — 회귀 감시의 핵심 축으로 삼을 것.

---

## §4. 태스크 기반 평가 프로토콜 설계

**(이 절이 논문 주장의 실질적 근거다. §2·§3 은 전부 이 절의 보조다.)**

### 4.0 이 절의 개념적 출처

`[확인]` "합성으로 학습 → 실사에서 평가"라는 프로토콜에는 공식 명칭이 있다:
Ravuri & Vinyals, *Classification Accuracy Score for Conditional Generative Models*, NeurIPS 2019
(https://arxiv.org/abs/1905.10887). 원문: *"we train a classifier on synthetic data, and evaluate the
performance of the classifier on real data. We call the accuracy the Classification Accuracy Score (CAS)."*
그리고 같은 논문의 결정적 문장 — ***"We find that neither IS, nor FID, nor combinations thereof are
predictive of CAS."*** → §2.5 의 FID 반박 근거 1순위.

### 4.1 표준 프로토콜 — DAFormer 4열 구조를 그대로 가져온다

`[확인]` Hoyer, Dai, Van Gool, *DAFormer: Improving Network Architectures and Training Strategies for
Domain-Adaptive Semantic Segmentation*, CVPR 2022 (https://arxiv.org/abs/2111.14887), Table 1
(GTA5→Cityscapes, Cityscapes val, mIoU %):

| Architecture | Src-Only | UDA | Oracle | **Rel.** |
|---|---|---|---|---|
| DeepLabV2 | 34.3 ±2.2 | 54.2 ±1.7 | 72.1 ±0.5 | 75.2% |
| DeepLabV3+ | 31.0 ±1.4 | 53.7 ±1.0 | 75.6 ±0.9 | 71.0% |
| SegFormer | 45.6 ±0.6 | 58.2 ±0.9 | 76.4 ±0.2 | 76.2% |

캡션 원문: *"Mean and SD are calculated over 3 random seeds."*

**가져와야 할 것 3가지**
1. **Src-Only / UDA / Oracle** 3열 = S→R 무적응 / 적응 후 / 실사 상한
2. **`Rel. = UDA mIoU ÷ Oracle mIoU`** — **sim2real 갭의 단일 스칼라 요약**.
   심사위원에게 *"우리 합성 데이터는 실사 상한의 XX% 를 달성한다"* 를 한 줄로 말할 수 있다
3. 모든 셀에 **±SD (≥3 seed)**

`[확인]` 반드시 지켜야 할 공정성 조건 두 가지가 논문 본문에 명시돼 있다:
- *"the oracle mIoU is generally lower than reported in the literature ... as for UDA the images of
  Cityscapes are downsampled by a factor of two"* → **Oracle 은 S→R 과 완전히 동일한 해상도·증강·
  스케줄로 학습해야 한다.** 그렇지 않으면 Rel. 이 무의미
- *"We do not use the target validation dataset for checkpoint selection in contrast to some other works"*
  → **실사 val 로 체크포인트를 고르면 그건 이미 supervision 이다.** 우리도 이 관행을 논문에 명시할 것
- `[확인]` Src-Only 행의 seed 분산이 가장 크다(±2.2 vs Oracle ±0.5) → **S→R 행은 seed 를 5개 이상** 돌려라

### 4.2 혼합 비율 스윕 — Playing for Data 형식

`[확인]` Richter, Vineet, Roth, Koltun, *Playing for Data: Ground Truth from Computer Games*, ECCV 2016
(https://arxiv.org/abs/1608.02192), Table 2 (CamVid 11 classes):

| real 이미지 | 100% | – | 25% | 33% | 50% | 100% |
|---|---|---|---|---|---|---|
| synthetic (25k 전량) | – | ✓ | ✓ | ✓ | ✓ | ✓ |
| **mean IoU** | **65.0** | **43.6** | 63.9 | **65.2** | 66.5 | **68.9** |

읽어야 할 수치: **S→R 무적응 43.6 vs 실사 oracle 65.0 → 갭 21.4 mIoU, Rel. 67.0%**.
그리고 **합성 + 실사 33%(65.2) > 실사 100% 단독(65.0)** — *"when we train on 1/3 of the CamVid training
set along with the game data, we surpass the accuracy achieved when training on the full CamVid
training set."* → **"실사 라벨을 3배 절약"** 주장. KITTI 에서는 real+synth 가 +2.6 pp.

### 4.3 Few-shot / label-efficiency 곡선 — Hypersim (우리와 아키텍처가 같다)

`[확인]` Roberts et al., *Hypersim*, ICCV 2021 (https://arxiv.org/abs/2011.02523).
**모델이 U-Net + ResNet-34 encoder (ImageNet init), 512×512 평가** — 우리 세팅과 사실상 동일.
**인용 가치 최상.**

| Pre-train | Fine-tune | mIoU (13-class) | mIoU (40-class) |
|---|---|---|---|
| None | NYUv2 100% | 45.2 | 31.4 |
| Hypersim | NYUv2 **25%** | **46.4** | 29.0 |
| Hypersim | NYUv2 50% | 49.1 | **32.7** |
| Hypersim | NYUv2 100% | **51.6** | **36.4** |

13-class 는 실사 **25%** 만으로 실사 100% 초과, 40-class 는 **50%** 로 초과. 총 이득 +6.2 / +5.0 mIoU.

`[확인]` **씬 수가 적다는 지적에 대한 방어 논거**: Hypersim(77K img, **0.5K scenes**) 의 이득 +6.2 가
PBRS(568K img) 의 +1.6 보다 크다 → ***"a small, more photorealistic dataset can be competitive with a
large, less photorealistic dataset."*** 우리 33씬에 대한 예상 공격을 이 문장으로 막는다.

`[확인]` 반대 방향의 중요한 결과도 있다. Nowruzi et al., *How much real data do we actually need*,
ICML-W 2019 (https://arxiv.org/abs/1907.07061):
- ***"Fine-tuning synthetic training model with limited real data provides better results than mixed training."***
  → **혼합 학습보다 합성 사전학습 + 실사 파인튜닝이 낫다**
- ***"It is shown that the photo-realism is not as important as the diversity of the data."***
  → **포토리얼리즘 < 다양성**

> `[추정]` 이 두 번째 문장은 우리에게 양날이다. 우리 개선 방향이 "사실성"에만 쏠려 있으면
> 이 논문으로 반박당한다. **조건 변주(계절·기상·시간대·재질 다양성)를 사실성과 함께 늘려야 하고,
> ablation 에서 "사실성 개선분"과 "다양성 개선분"을 분리해 보여야 한다.**

### 4.4 실사 클론 페어 — Isaac Sim 을 쓰는 우리에게 가장 강력한 카드 ★

`[확인]` Gaidon, Wang, Cabon, Vig, *Virtual Worlds as Proxy for Multi-Object Tracking Analysis*
(Virtual KITTI), CVPR 2016 (https://arxiv.org/abs/1605.06457).

핵심 기여가 정확히 우리가 필요한 것이다 — ***"a practical definition of transferability of experimental
observations across real and virtual worlds."***
방법: 실사 시퀀스를 3D 로 **클론 렌더링**해 페어를 만들고, **실사 사전학습 모델을 양쪽에 그대로 추론**해
성능 차를 잰다.

결과: ***"the real-to-virtual performance gap is minimal ... < 0.5% on average for both trackers"*** (MOTA).
*"The amount of expected 'transferability of conclusions' from real to virtual and back can be quantified
by the difference in the metrics reported in table 1."*

Virtual pre-training 결과:

| 학습 구성 | MOTA | MOTP | MT | ML |
|---|---|---|---|---|
| virtual only | 64.3% | 75.3% | 35.9% | 31.5% |
| real only | 71.9% | 79.2% | 45.0% | 24.4% |
| **virtual → real finetune** | **76.7%** | **80.9%** | **53.2%** | **12.3%** |

**우리 적용** `[추정, 방법론은 확립됨]`: 실제 낙차 현장(계단참·옹벽·도랑·제방) **3~5곳을 TurtleBot3 로
촬영 → Isaac Sim 에 디지털 트윈으로 재현 → 동일 카메라 포즈로 렌더**. 페어별로 **동일 모델을 양쪽에
추론**해 Δ(mIoU) 를 잰다. Δ 가 작을수록 우리 렌더가 사실적이라는 **직접 증거**다.

> 이건 §2.6 설계 C(내용 통제)와 §6(사람 평가) 자극 생성과 **완전히 같은 자산을 공유**한다.
> 한 번 만들면 세 곳에서 쓴다. **투자 대비 효과가 가장 크다.**

### 4.5 갭에 척도를 주는 트릭 — "다른 도메인의 실사" 기준선

`[확인]` Prakash et al., *Structured Domain Randomization*, ICRA 2019 (https://arxiv.org/abs/1810.10093),
Table III (Faster-RCNN, 실사 KITTI 테스트, AP@0.7):

| Dataset | Type | Size | Easy | Moderate | Hard |
|---|---|---|---|---|---|
| DR | synth | 25k | 56.8 | 38.0 | 23.9 |
| **SDR** | synth | 25k | 69.6 | 65.8 | 52.5 |
| **BDD100K (다른 도메인 실사)** | **real** | 70k | 59.7 | 54.3 | 45.6 |
| KITTI (in-domain oracle) | real | 6k | 85.1 | 88.3 | 88.8 |

원문: *"there is not only a reality gap between synthetic and real data, but there are also significant
domain gaps between various real-world datasets ... Significantly, SDR outperforms this real dataset."*

**우리 적용** `[추정]`: *"합성 학습 < 실사 학습"* 은 당연하다는 반론에 대해,
**"다른 현장에서 찍은 실사로 학습한 모델보다 우리 합성이 낫다"** 는 행을 추가하면 갭에 현실적 척도가 생긴다.
구체적으로 **실사 현장 A 로 학습 → 현장 B 테스트**(real→real 갭)를 sim→real 갭 옆에 나란히 놓는다.

`[확인]` 덤으로 **데이터 크기 스윕**도 표준 실험 항목이다 (SDR Table II): SDR 은 **10k 장에서 포화**,
1k 장에서도 AP 43.7. 순수 도메인 랜덤화(DR)는 50k 까지 포화하지 않았다.

### 4.6 negative obstacle 태스크 전용 지표

#### (a) mIoU 만으로 부족한 이유 `[추정, 근거는 아래 (b)~(e)]`

1. **mIoU 는 FN 과 FP 를 대칭 취급한다.** 낙차 FN = 추락, FP = 우회. 비용이 완전히 비대칭
2. **mIoU 는 픽셀 면적 가중이다.** 원거리 낙차는 픽셀이 적어 mIoU 기여가 거의 없지만 **제동거리
   때문에 안전상 가장 중요**하다
3. **mIoU 는 confidence 를 무시한다.** 합성→실사 전이에서 overconfident 오탐이 생겨도 안 드러난다

#### (b) 거리 층화 평가 — 확립된 선례

`[확인]` **Synscapes** (Wrenninge & Unger 2018) — 실사 사전학습 DeepLab v3+ 를 합성에 추론하고
인스턴스를 파라미터별로 binning:
- **깊이 16구간**별 IoU (Fig. 8)
- **가림 4구간** [0,0.25],[0.25,0.5],[0.5,0.75],[0.75,1.0] × 깊이 → **heat map** (Fig. 9)
- 방향 4방위 × 깊이
- 핵심 관찰: segmentation 은 거리에 따라 **선형 열화**, detection(Faster R-CNN)은 **약 50m 에서 절벽처럼
  급락**. 거리 층화 없이는 절대 안 보이는 차이
- ★ ***"we also see an expected correlation between the curb height and the score for Sidewalk, as the
  higher curb makes the edge more distinguishable."*** — **연석 높이(=낙차 크기)별 층화 평가의 직접 선례.**
  우리 태스크에 거의 그대로 대응한다

`[확인]` **Waymo Open Dataset** (Sun et al., CVPR 2020, https://arxiv.org/abs/1912.04838) 의 공식
breakdown: **0–30m / 30–50m / 50m–Inf × LEVEL_1/LEVEL_2**. 예: Vehicle APH 0–30m 90.2 인데 Overall 79.1
— 원거리가 전체를 끌어내림을 구간 표시로 노출. 지역 간 일반화(SF↔SUB) 실험은 **real→real 도메인 갭
기준선**의 좋은 선례.

`[확인]` 반대로 **off-road 벤치마크는 이런 층화를 하지 않는다**: RELLIS-3D (Jiang et al., ICRA 2021,
https://arxiv.org/abs/2011.12954) 는 **표준 mIoU 만** 쓴다.
→ **우리가 거리/깊이 층화 + FN 가중 평가를 도입하면 그 자체가 방법론적 기여로 주장 가능하다.**

#### (c) negative obstacle 선행 연구가 실제로 쓰는 지표

`[확인]` Goodin, Carrillo, Monroe, Carruth, Hudson, *An Analytic Model for Negative Obstacle Detection
with Lidar and Numerical Validation Using Physics-Based Simulation*, Sensors 21(9):3211, 2021
(https://pmc.ncbi.nlm.nih.gov/articles/PMC8125519/).

**이 논문이 우리 연구의 문제의식을 수학적으로 정당화한다. 최우선 인용 후보.**
- ★ ***"the angle subtended by a positive obstacle at a range R from the sensor ∝ 1/R, whereas the angle
  subtended by a negative obstacle ∝ 1/R²"*** → **음의 장애물은 원리적으로 원거리 탐지가 훨씬 어렵다.**
  → **"왜 LiDAR 가 아니라 RGB 맥락단서인가"의 논거로 직접 사용**
- 탐지거리 실측: UGV 탑재 LiDAR **10m 미만**, UAV 탑재 60–110m
- 제동거리 `R_stop = v²/(2μg) + v·T_r + B`
- 결론: **UGV 센서는 어떤 시험 속도에서도 제동거리 이전에 음의 장애물을 탐지하지 못한다**
- 지표: 속도별(2.5–17.5 m/s) 탐지거리 ± 25회 시행의 1σ, 센서별 탐지확률 P_d (VLP-16 0.886, HDL-32E 0.977, OS1 0.909)

`[확인]` Xie et al., *LiDAR-Based Negative Obstacle Detection for Unmanned Ground Vehicles in Orchards*,
Sensors 2024 (https://pmc.ncbi.nlm.nih.gov/articles/PMC11679008/). 프레임 단위 지표:
- 탐지 성공률 `P_success = N₁/N₀`, 오탐률 `P_false = N₂/N₀`, 미탐률 `P_miss = 1 − N₁/N₀`
- \+ **최대 탐지거리 D_max**, **프레임당 처리시간**
- 결과: P_success 92.7%, P_false 5.4%, P_miss 7.3%, D_max 8.0 m, 17.3 ms
- ★ 비대칭 비용 명시: ***"the potential obstacle is allowed to be a little larger than the actual obstacle,
  but the potential obstacle is not allowed to be smaller ... otherwise it will possibly pose a safety
  hazard"*** → **"과탐 허용, 미탐 불허" 원칙의 인용 가능한 직접 근거**

`[확인]` 관련 선행: Larson & Trivedi, *Lidar based off-road negative obstacle detection and analysis*,
IEEE ITSC 2011 (서지 확인, 수치는 DTIC 접근 차단으로 미확인) / Matthies & Rankin, *Negative obstacle
detection by thermal signature*, IROS 2003 (야간 열적외선 — 우리 스코프 밖, related work 언급용).

> **종합** `[확인]`: 이 분야의 사실상 표준은 **프레임 단위 success/false/miss rate + 최대 탐지거리 +
> 처리시간**이며 **mIoU 를 쓰지 않는다.** 우리가 세그멘테이션 논문이면서 이 지표들을 함께 보고하면
> 두 커뮤니티 모두에 소구한다.

#### (d) FN 편중 지표

`[확인]` Dollár, Wojek, Schiele, Perona, *Pedestrian Detection: An Evaluation of the State of the Art*,
IEEE TPAMI 34(4), 2012. **Log-Average Miss Rate (LAMR, MR⁻²)**:

```
Miss Rate–FPPI 곡선에서 x축(FPPI) [10⁻², 10⁰] 을 로그 균등 9점으로 샘플링
MR = exp[ (1/9) · Σ_{i=1}^{9} ln(m_i) ]
```
("Reasonable" 부분집합 관례: 높이 ≥ 50px, 가시성 ≥ 65%)

**우리 적용** `[추정]`:
- 픽셀이 아니라 **낙차 인스턴스 단위**(IoU ≥ 0.5 매칭) 로 MR–FPPI 곡선을 그리면
  *"이미지당 오탐 0.1개를 허용할 때 낙차를 몇 % 놓치는가"* 라는 **운영자가 이해하는 수치**가 나온다.
  mIoU 보다 훨씬 설득력 있다
- **F_β (β=2)**: `F_β = (1+β²)PR / (β²P + R)` — recall 에 4배 가중. 근거로 Xie et al. 2024 의
  "미탐 불허" 문장을 인용
- **고정 작동점 보고**: "FPR 1% 에서의 recall", "이미지당 FP 0.1개에서의 recall" — 단일 F1 보다 방어에 유리

#### (e) 낙차 깊이 회귀 오차

`[확인]` Eigen, Puhrsch, Fergus, NIPS 2014 (https://arxiv.org/abs/1406.2283) 의 깊이 추정 표준 지표군:
`Abs Rel`, `RMSE`, `RMSE(log)`, **threshold accuracy δ_t**: `max(d_gt/d_pred, d_pred/d_gt) < 1.25^t`,
t=1,2,3 (δ₁<1.25, δ₂<1.5625, δ₃<1.953), 그리고 scale-invariant error.

**우리 적용** `[추정]`: 낙차 깊이는 **절대 스케일(m)이 안전에 직결**되므로
- **MAE(m), RMSE(m) 를 주 지표**로, δ₁ 은 보조
- δ 는 비율 기반이라 **얕은 낙차(10cm)에서 지나치게 엄격**해진다 → **절대 임계 정확도**를 함께:
  `|오차| < 10cm 비율`, `|오차| < 20cm 비율`
- **과소추정(위험 과소평가) 과 과대추정을 분리 보고**(signed bias). 안전상 비대칭이다

#### (f) 보정 (calibration)

`[확인]` Guo, Pleiss, Sun, Weinberger, *On Calibration of Modern Neural Networks*, ICML 2017
(https://arxiv.org/abs/1706.04599):
```
ECE = Σ_{m=1}^{M} (|B_m|/n) · | acc(B_m) − conf(B_m) |        (실험에서 M = 15)
MCE = max_m | acc(B_m) − conf(B_m) |
Temperature scaling: p̂ = softmax(z/T), validation NLL 최소화로 T 학습. 정확도 불변
```
현대 신경망은 심하게 **overconfident** 하며 **깊이·너비 증가, weight decay 감소, BatchNorm** 이 모두
miscalibration 을 악화시킨다.

`[확인]` **세그멘테이션에서 plain ECE 를 쓰면 안 되는 이유** — Nixon et al., *Measuring Calibration in
Deep Learning*, CVPR-W 2019 (https://arxiv.org/abs/1904.01685):
- 균등 간격 bin 은 고신뢰 쪽에 데이터가 몰려 ***"only a few bins to contribute the most to ECE—typically
  one or two"***
- 정적 bin 에서는 overconfident/underconfident 예측이 **같은 bin 에서 상쇄되어 ECE 가 0 에 가깝게 나오는
  병리**가 생긴다
- max probability 만 보면 **클래스별 miscalibration 이 은폐**된다
- 대안: `SCE = (1/K) Σ_k Σ_b (n_bk/N)|acc(b,k) − conf(b,k)|` (클래스별 binning),
  **`ACE = (1/(K·R)) Σ_k Σ_r |acc(r,k) − conf(r,k)|`** (**equal-mass** 적응형 binning)

> **우리 적용** `[추정]`: 우리는 **위험 영역이 소수 픽셀인 극심한 불균형** 세그멘테이션이다.
> plain ECE 는 배경 클래스에 지배당한다. 반드시 **ACE(equal-mass) 또는 위험 클래스 class-wise ECE 를
> 병기**하고, bin 수 M 을 바꿔가며 안정성을 보여라.

`[확인]` **합성 val 에서 보정해도 실사에서 깨진다** — Ovadia et al., *Can You Trust Your Model's
Uncertainty?*, NeurIPS 2019 (https://arxiv.org/abs/1906.02530):
***"while temperature scaling achieves low ECE for low values of shift, the ECE increases significantly as
the shift increases, which indicates that calibration on the i.i.d. validation dataset does not guarantee
calibration under distributional shift."***
→ **반드시 실사 테스트셋에서 ECE 를 직접 측정하라.** "합성 val 에서 보정했으니 괜찮다"는 주장은 이 논문에
의해 반박된다. 부가: Deep ensembles 가 shift 전 구간에서 최우수, **앙상블 5개면 대부분의 이득**.
Brier·NLL 은 proper scoring rule 이고 ECE 는 아니므로 **병행 보고**.

`[확인]` 최신 반론: Minderer et al., *Revisiting the Calibration of Modern Neural Networks*, NeurIPS 2021
(https://arxiv.org/abs/2106.07998) — ViT/MLP-Mixer 가 가장 잘 보정되고 shift 에 강건하며,
**shift 하에서는 모델이 클수록 보정이 좋아진다**(in-distribution 추세의 역전).

`[미확인]` **합성→실사에 특화된 보정 붕괴 논문은 확인되지 않았다.**
→ `[추정]` **우리가 직접 측정해 보고하면 그 자체가 작은 기여**가 될 수 있는 공백이다.

### 4.7 갭을 싸게 재는 proxy — 무엇이 실제로 downstream 을 예측하는가

#### (a) Proxy A-distance 의 정확한 수식과 출처

`[확인]` 원 이론: Ben-David, Blitzer, Crammer, Kulesza, Pereira, Vaughan, *A theory of learning from
different domains*, Machine Learning 79(1–2):151–175, 2010.
**"Proxy A-distance" 라는 용어의 원 출처는 Ben-David et al., NIPS 2006** (*Analysis of Representations for
Domain Adaptation*). 계산 관행은 Glorot, Bordes, Bengio (ICML 2011) 및 Chen et al. (2012) 를 따른다.

`[확인]` 수식은 Ganin et al., *Domain-Adversarial Training of Neural Networks*, JMLR 17(59), 2016
(https://arxiv.org/abs/1505.07818) §3.2 원문:

```
경험적 H-divergence (Eq.1):
  d̂_H(S,T) = 2( 1 − min_{η∈H} [ (1/n)Σ_{i=1}^{n} I[η(x_i)=0] + (1/n)Σ_{i=n+1}^{N} I[η(x_i)=1] ] )

데이터 구성 (Eq.2): U = {(x_i, 0)}_{i=1}^{n} ∪ {(x_i, 1)}_{i=n+1}^{N}   (source=0, target=1)

Proxy A-distance (Eq.3):  d̂_A = 2(1 − 2ε)        ε = 도메인 판별 문제의 일반화 오차
이론 보증:  ε_T(h) ≤ ε_S(h) + ½·d_{HΔH}(D_S, D_T) + C
```
원문: *"In Ben-David et al. (2006), the value d̂_A is called the Proxy A-distance (PAD). ... we train
either a linear SVM or a deeper MLP classifier on a subset of U, and we use the obtained classifier
error on the other subset as the value of ε."*

해석: ε=0.5(동전던지기) → **d_A = 0** (갭 없음) / ε=0(완벽 판별) → **d_A = 2** (최대 갭).
정확도로 쓰면 **`d_A = 2(2·acc − 1) = 4·acc − 2`** — §3.7 에서 우리가 쓴 그 식이다.

**두 층위에서 각각 계산하라** `[추정, 방법은 확립됨]`:
- **PAD_raw**: 원본 픽셀/얕은 특징 위 linear SVM (Glorot 방식) → **렌더링 사실성 자체**의 지표
- **PAD_feat**: 학습된 U-Net encoder bottleneck 특징 위 → **모델이 도메인을 얼마나 구분하는가**.
  학습이 진행되며 PAD_feat 이 줄면 도메인 불변 표현을 배웠다는 증거

⚠️ `[확인]` **경고 2건**
1. PAD 는 d_H 의 **하한의 근사**일 뿐이고 **판별기 용량(hypothesis class)에 따라 값이 크게 달라진다.**
   반드시 **판별기 구조를 명시**(예: "frozen DINOv2 특징 위 linear SVM")하고 여러 seed 평균을 보고할 것
2. **PAD 가 전이 성능과 상관하지 않는 반례가 보고돼 있다** — 어떤 방법은 최저 오차율을 달성하면서도
   source-only 대비 A-distance 를 유의하게 줄이지 않았고, 전반적으로 A-distance 와 타깃 성능 사이에
   상관이 관찰되지 않았다. → **"갭의 크기"로 보고하되 "전이가 될 것"의 근거로는 쓰지 마라**

#### (b) 어느 특징 거리가 실제로 downstream 을 예측하는가 ★

`[확인]` SADGE (arXiv:2605.22467) 벤치마크: 5개 sim2real 패밀리(DIMO, Virtual KITTI2, TUD-L, RarePlanes,
ASD), 15개 데이터셋 변형, 약 79,000 이미지 페어, 3개 downstream task.
**downstream 성능과의 Pearson r:**

| 지표 | r |
|---|---|
| PSNR | 0.536 |
| **FID** | **0.635** |
| LPIPS | 0.649 |
| SSIM | 0.755 |
| SAM3 | 0.826 |
| CLIP | 0.832 |
| SigLIP | 0.857 |
| **DINOv2** | **0.878** |
| **DINOv3** | **0.879** |
| **SADGE (외양+기하)** | **r 0.879, ρ 0.768, p≈8.3e-4** |

저자 결론: ***"neither appearance nor geometry alone can reliably predict downstream performance."***

> **결론** `[추정, 위 표 근거]`: **값싼 proxy 를 하나만 쓴다면 FID 가 아니라 DINOv2 특징 거리를 써라**
> (0.878 vs 0.635). 이건 §2.2 의 backbone 권고와 정확히 같은 방향이다.

#### (c) transferability estimation 지표군 — 넣지 마라

`[확인]` OTDD (Alvarez-Melis & Fusi, *Geometric Dataset Distances via Optimal Transport*, NeurIPS 2020,
https://arxiv.org/abs/2002.02923): `T(D_S→D_T) = 100 × [error(D_S→D_T) − error(D_T)] / error(D_T)`,
OTDD vs transferability **ρ = −0.85, p = 1.0e-3** (\*NIST 계열), 10 seed. **학습 불필요, model-agnostic.**
그 외 Task2Vec (ICCV 2019), LEEP (ICML 2020), LogME (ICML 2021), H-score (ICIP 2019).

⚠️ `[확인]` **결정적 한계**: LEEP·LogME·H-score·Task2Vec 은 **모두 분류 태스크용으로 설계·검증**됐고,
**semantic segmentation 의 sim2real 갭 예측에 쓰인 검증된 선례가 없다.**
→ `[추정]` **우리 논문에 억지로 넣으면 오히려 공격받는다. PAD + DINOv2 특징 거리 두 개면 충분하고
방어 가능하다. transferability 지표군은 related work 언급 수준으로.**

### 4.8 통계적 유의성 — 최소 위생 기준

`[확인]` **세그멘테이션 논문의 실제 관행은 3 seed**. DAFormer: *"The reported results are averaged over
three training runs and have a standard deviation of 0.5 mIoU on both benchmarks, which shows that the
training process is stable."* OTDD 논문은 10 seed.

`[확인]` Bouthillier et al., *Accounting for Variance in Machine Learning Benchmarks*, MLSys 2021
(https://arxiv.org/abs/2103.03098) 의 3가지 권고(원문 소제목):
1. ***"Randomize as many sources of variations as possible"*** — weight init, data sampling/order,
   augmentation, data split 을 **모두** 랜덤화. 한 가지만 랜덤화하는 것보다 오차가 빠르게 감소
2. ***"Use multiple data splits"*** — 고정 test set 하나의 분산은 무시할 수 없다
3. ***"Account for variance to detect meaningful improvements"*** — 평균 차이만으로 유의성을 논하지 마라.
   **P(A > B) > 0.75** 기준을 제안. *"We recommend to always highlight not only the best-performing
   procedure, but also all those within the significance bounds."*

정량 근거 `[확인]`: 단일 시행 비교는 거짓양성 ≈10%, **거짓음성 ≈75%**. 평균 비교(문헌 관행)는 보수적이라
거짓양성 <5% 이지만 **거짓음성 ≈90%**. 제안 방식은 거짓양성 ≈5%, 거짓음성 ≈30%.

**우리 최소 기준** `[추정, 위 근거 종합]`
- 모든 주요 행: **seed ≥ 3 (S→R 행은 5), mean ± SD 병기**
- 핵심 비교: **테스트 이미지 bootstrap 95% CI (B=1000)** + **Wilcoxon signed-rank** (같은 테스트 이미지
  위 쌍체 비교이므로 unpaired t-test 는 부적절)
- **체크포인트 선택에 실사 val 을 쓰지 않았음을 논문에 명시**

### 4.9 논문에 실을 표 템플릿

#### 표 A (메인) — Sim2Real 전이 성능 종합

| # | 학습 데이터 | 테스트셋 | mIoU ↑ | 위험영역 IoU ↑ | **위험영역 Recall** ↑ | FPPI | **F₂** ↑ | **LAMR** ↓ | 낙차 MAE(m) ↓ | **ACE** ↓ |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Synth (Isaac Sim) only | **Real test** | | | | | | | | |
| 2 | Real only (100%) — **Oracle** | **Real test** | | | | | | | | |
| 3 | Synth → Real FT (25%) | **Real test** | | | | | | | | |
| 4 | Synth → Real FT (50%) | **Real test** | | | | | | | | |
| 5 | Synth → Real FT (100%) | **Real test** | | | | | | | | |
| 6 | Real 현장 A only | **Real test 현장 B** | | | | | | | | |
| 7 | Synth only | Synth test (self-val) | | | | | | | | |
| — | **Rel. = 행1 ÷ 행2** | | **__%** | | | | | | | |

행별 선례: 1·2·5 = Playing for Data / DAFormer `[확인]` · 3·4 = Hypersim label-efficiency `[확인]` ·
6 = SDR 의 BDD100K 행 `[확인]` · 7 = Synscapes self-validation `[확인]`.
**Rel. 행이 심사위원용 단일 요약 수치.** 모든 셀 mean ± SD over ≥3 seeds.

> `[확인]` Synscapes self-validation 참고 수치: **Synscapes 87.00 / Richter(GTA) 63.05 / Synthia 57.22**
> (DeepLab v3+), 클래스별 σ 는 8.25 / 17.51 / 24.55. 저자들은 낮은 self-val 을 **렌더링 아티팩트
> (폴리곤 엣지 등)로 클래스가 혼동되는 신호**로 해석했다 → **행 7 은 우리 렌더 품질의 내부 일관성
> 지표로도 읽힌다.**

#### 표 B — 혼합 비율 / label-efficiency 스윕

| real 라벨 비율 | 0% | 5% | 10% | 25% | 50% | 100% | 100% |
|---|---|---|---|---|---|---|---|
| synthetic 사용 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – (baseline) |
| mIoU | | | | | | | |
| 위험영역 Recall | | | | | | | |
| 낙차 MAE (m) | | | | | | | |

목표 주장: **"real 라벨 N% + 합성 ≥ real 100% 단독"** 의 손익분기점 N.
(선례 `[확인]`: Playing for Data 33%, Hypersim 25%(13-cls)/50%(40-cls))

#### 표 C — 거리 × 낙차 깊이 층화 Recall

| 낙차 깊이 \ 거리 | 0–3 m | 3–6 m | 6–10 m | >10 m | 전체 |
|---|---|---|---|---|---|
| 10–30 cm | | | | | |
| 30–60 cm | | | | | |
| >60 cm | | | | | |
| **전체** | | | | | |

각 셀 = S→R recall (괄호 안 Oracle recall). Synscapes 방식대로 **heat map 시각화**.
표 하단에 **제동거리 `R_stop = v²/(2μg) + v·T_r + B` 를 만족하는 최소 요구 탐지거리를 세로선**으로 표시하면
Goodin et al. 2021 의 안전 논거와 직결된다. `[확인된 선례]`

#### 표 D — 값싼 proxy vs 실측 task 갭 (렌더 개선 라운드별) ★ 우리 문서의 핵심 산출물

| 렌더 버전 | **NIS-Gap** ↓ (§3.8) | **PAD_raw** ↓ | PAD_feat ↓ | **DINOv2 MMD** ↓ | CMMD ↓ | FID (참고용) | **S→R mIoU** ↑ | **Rel.(%)** ↑ |
|---|---|---|---|---|---|---|---|---|
| v5 (21씬 재설계) | | | | | | | | |
| **v7 (현재)** | baseline | **1.71** `[측정]` | | | | | | |
| v8 (fix 라운드) | | | | | | | | |
| + 센서 후처리 (S3) | | | | | | | | |
| + 기하/재질 개선 | | | | | | | | |

→ **이 표가 `judge_v*.md` 의 육안 합격/불합격을 대체하는 산출물이다.**
마지막 두 열(실측 task 갭)과 앞 열들(값싼 proxy)의 **Spearman ρ 를 보고**하면
*"우리 proxy 가 유효하다"* 까지 주장할 수 있다.
FID 는 **일부러 참고용 열로만** 두고 Ravuri & Vinyals 2019 / SADGE 2026 을 근거로
"주 지표로 쓰지 않는 이유"를 각주로 단다.

#### 표 E — Calibration

| 학습 데이터 | 테스트셋 | Accuracy | ECE (M=15) | **ACE** (equal-mass) | 위험클래스 class-wise ECE | Brier | NLL |
|---|---|---|---|---|---|---|---|
| Synth only | Synth val | | | | | | |
| Synth only | **Real test** | | | | | | |
| Synth + temp. scaling (**synth val** 에서 T 학습) | **Real test** | | | | | | |
| Synth → Real FT | **Real test** | | | | | | |

3행이 2행 대비 개선폭이 작다면 그게 정확히 Ovadia et al. 2019 가 예측한 현상이다.
**인용과 함께 보고하면 오히려 신뢰도가 올라간다.** reliability diagram 2장(synth val vs real test) 병치.

### 4.10 §4 우선순위 요약

| 우선 | 항목 | 근거 |
|---|---|---|
| **최우선** | 표 A 의 **Rel. = S→R ÷ Oracle** 단일 수치를 핵심 주장으로 | DAFormer CVPR 2022 `[확인]` |
| **최우선** | **실사 클론 페어** 3~5곳 → 동일 모델 양쪽 추론 Δ 보고 | Virtual KITTI CVPR 2016 (Δ<0.5% MOTA 를 사실성 증거로 사용) `[확인]` |
| 높음 | **PAD 를 렌더 버전별로 찍어 갭 감소 곡선** (표 D) | Ganin JMLR 2016 수식 `[확인]` |
| 높음 | **거리 × 낙차 깊이 층화 recall** (표 C) | Synscapes / Waymo `[확인]`, off-road 벤치마크가 안 하는 영역 |
| 중간 | **LAMR / F₂ / 고정 FPPI recall** | Dollár TPAMI 2012 + Xie 2024 "미탐 불허" `[확인]` |
| 중간 | ECE 는 **ACE 또는 class-wise ECE 병기** | Nixon CVPR-W 2019 `[확인]` |
| 필수 위생 | seed ≥3 + SD, 테스트 bootstrap CI, 실사 val 미사용 명시 | DAFormer / Bouthillier `[확인]` |
| 방어 | FID 를 주 지표로 쓰지 말 것 | Ravuri & Vinyals 2019, SADGE 2026 `[확인]` |

---

## §5. 실사 참조 데이터 확보 방안

> 표기 추가: `[실증]` = 이 조사에서 **실제로 API 호출·다운로드·전수 분석을 실행해** 검증한 사실.

### 5.0 결론 5줄

1. **한국 씬 + 낙차 라벨을 동시에 만족하는 유일한 소스는 AI Hub** — 특히 `dataSetSn=513`
   "보행 안전을 위한 도로 시설물 데이터"(2021, **102.5만장**)가 **보행자 계단·연석·턱낮추기·경사로·
   점자블럭·방호울타리**를 실제로 라벨링한다. 단 **"내국인만 데이터 신청 가능"** `[확인]`.
2. **로드뷰 3사(구글·네이버·카카오)는 전부 법적으로 막혔다.** 특히 네이버는 약관에
   **"1회 사용만 허용, 별도 저장·DB화 금지"** 가 명문이라 논쟁의 여지가 없다 `[확인]` (§5.2).
3. **오늘 당장 계정 없이 받을 수 있는 것은 ADE20K** — 967MB 직링크가 실제로 열린다 `[실증]`.
   다만 **한국이 아니고 낙차가 주제인 사진이 거의 없다**(§5.4 전수 분석).
4. **"낙차 그 자체"를 이름 붙인 클래스는 전 세계 데이터셋 중 ADE20K full 하나뿐** —
   `cliff, drop, drop-off`(id 524), `embankment`(855) `[확인]`.
5. **Wikimedia Commons 는 오늘 이미 작동을 검증했다** `[실증]` — 45장을 실제로 받았고
   `extmetadata` 로 **라이선스·저작자·촬영일까지** 함께 수집된다(§5.6). 규모는 작지만
   **오늘 L1 을 돌리기에는 충분**했다.

### 5.1 출처별 비교표

| 출처 | 규모 | 라이선스 (핵심 조문) | 접근 난이도 | 우리 씬 적합도 | 낙차 관련 라벨 | 권고 |
|---|---|---|---|---|---|---|
| **AI Hub 513** 도로시설물 | **102.5만장** | 영리·비영리 R&D 가능. **제3자 제공 금지**, 국외반출 별도합의 | 中 (내국인·승인) | ★★★★★ 한국 보도 | **계단·연석·턱낮추기·경사로·점자블럭·방호울타리** | **1순위** |
| **AI Hub 189** 인도보행 | **67만장** (BBox 35만 / Poly 10만 / Surface 5만 / **Depth 17만**) | 동상 | 中 | ★★★★★ | 29종 장애물, 점자블록, 노면상태. 계단·연석 별도 명시 없음 | **2순위** (Depth 17만장 주목) |
| **AI Hub 159** 1인칭 보행 | ~80만장, 주석 757,653 | 동상 | 中 | ★★★★★ 1인칭 | 계단·연석 언급 | 병행 |
| **Mapillary 원본** | 전세계 수억장 | **CC BY-SA 4.0** — 재배포·상업 OK | 低 (무료토큰) | ★★★☆☆ (**한국 커버리지 미검증**) | 라벨 없음(참조분포용) | **커버리지 확인 후 1순위 후보** |
| **Mapillary Vistas** | 25,000 / 124클래스 | **CC BY-NC-SA** 비상업 | 中 (가입) | ★★★☆☆ 해외 | **`Curb`, `Curb Cut`, `Guard Rail`, `Barrier`, `Wall`, `Water`, `Catch Basin`, `Pothole`, `Road Shoulder`** — 연석 최강 | **연석 GT 1순위** |
| **ADE20K** SceneParse150 | 20,210 + 2,000 | 주석 BSD-3 / **이미지 비상업·재배포 불가** | **低 (계정 불필요 직링크)** `[실증]` | ★★☆☆☆ 서구·비주제적 | `stairs`54, `stairway`60, `step`122, `handrail`96, `escalator`97, `railing`39, `water`22, `river`61, `bridge`62 | **오늘 확보용** |
| **ADE20K full** | 27,574 / 3,688클래스 | 이미지 비상업, 신청 필요 | 中 | ★★☆☆☆ | ★ **`cliff, drop, drop-off`(524)**, **`embankment`(855)**, `curb`(682), `footbridge`(1013) | **낙차 GT 유일** |
| **Open Images V7** | 9M | 이미지 **CC BY 2.0**, 주석 **CC BY 4.0** — 상업·재배포 OK | 低 (직링크) | ★★☆☆☆ 전세계 Flickr | 이미지레벨에 `Curb`,`Ditch`,`Stairs`,`Sidewalk`,`Handrail`,`Guard rail`,`Tunnel`,`Escalator`,`Ramp`,`Manhole`,`Bollard` **전부 존재** (박스는 `Stairs`만) | 필터링 참조풀 2순위 |
| **Wikimedia Commons** | 검색 기반, 질의당 수십~수백 | 파일별 상이(**CC BY / CC BY-SA / PD 다수**), API 가 라이선스·저작자 동봉 | **極低 (계정 불필요)** `[실증]` | ★★★☆☆ (한국 질의 가능) | 없음 | **오늘 L1 용, 검증 완료** |
| **IDD** | 10,003 / 34클래스 | **불명** (로그인 후 표시) | 中 | ★★★☆☆ 아시아 | **`curb`(id 19)** — 주행셋 중 유일 픽셀 연석 | 연석 보조 |
| **Cityscapes** | 5,000 fine (~270k raw) | 비상업, **재배포 금지**, 게재 시 익명화 | 中 (기관승인) | ★★☆☆☆ 독일 | **curb·stairs 전무** | 낮음 |
| **BDD100K** | 100K / seg 10K | 연구 OK, 상업은 BAIR 회원, 재배포 허용 | 中 (**문서·미러 DNS 사망**) | ★★☆☆☆ 미국 | `road curb` 는 **차선표시 카테고리**일 뿐 | 낮음 |
| **KITTI / KITTI-360** | 200+200 / 320k | CC BY-NC-SA 3.0 | 低/中 | ★☆☆☆☆ 차량 | 없음 | 제외 |
| **nuScenes** | 1.4M img / nuImages 93k | CC BY-NC-SA 4.0 | 中 | ★★☆☆☆ | LiDAR 엔 "3단 이하 계단" 정의 有, **nuImages 2D 는 surface 2클래스뿐** | 제외 |
| **Waymo Open** | 390k frame | 비상업, **논문 인용 명문 허용** | 中 | ★★☆☆☆ | LiDAR `TYPE_CURB`, 2D 는 sidewalk 흡수 | 낮음 |
| **ACDC** | 4,006 | 비상업, **재배포 전면금지**, **군사용도 금지** | 中 | ★☆☆☆☆ 악천후 | 없음 | 제외 |
| **WildDash2** | 4,256 | CC-BY-NC, 재배포 ✗, **논문엔 익명화판 필수** | 中 | ★★☆☆☆ | curb 분할 라벨 有 | 낮음 |
| **COCO-Stuff** | 164K / 172클래스 | **주석 CC BY 4.0(상업 OK)**, 직링크 | 低 | ★★☆☆☆ | **`stairs`(161)**, `railing`, `bridge`, `river`, `pavement` | 보조 |
| **KartaView** | 한국 = 사실상 없음 | CC BY-SA | 低 | ✗ **실측 탈락** `[실증]` | 없음 | **제외** |
| **Google / Naver / Kakao 로드뷰** | — | **전부 금지** (§5.2) | — | — | — | **사용 금지** |

### 5.2 웹 소스 라이선스 — 조문 근거 (가장 중요)

#### 네이버 — 명백히 불가 `[확인, 약관 원문]`
NCP `AI·NAVER API 서비스 이용약관` 부가조항 「Maps API 서비스」 (2):

> "'고객'은 Maps API의 결과 데이터를 (해당 결과 데이터를 받은 즉시 자신의 서비스에서 사용하는 것이
> 아니라) **별도로 저장해서는 안되며**, 따라서 그와 같은 결과 데이터를 별도로 저장하는 방식으로
> **데이터베이스화하여 이용해서도 안됩니다.** … 즉, 모든 Maps API의 결과 데이터는 값을 리턴 받는
> **즉시 1회** 자신의 서비스에서 사용하는 것만 허용되며, 그렇지 않고 그 결과 값들을 **별도로 저장,
> DB화, 재사용하는 것은 금지**됩니다."

→ 학습셋·FID 참조셋 구축은 정의상 "저장·DB화"이므로 **전면 불가**.

#### 카카오 — 불가 `[확인]`
`developers.kakao.com/terms/ko/site-policies` 제5조(금지된 행동):
- 20호: "앱에서 사용자 환경을 개선하기 위한 목적 외 다른 목적으로 카카오에서 받은 데이터를 캐시하거나"
- 30호: "서비스 및 개발자센터를 이용하여 얻은 정보를 카카오의 사전 승낙 없이, **복사, 복제, 변경,
  번역, 출판** … 기타의 방법으로 사용하거나 이를 타인에게 제공"

#### Google Street View — 불가 `[확인]`
- Maps Platform ToS **3.2.3(a) "No Scraping"**: Maps Content 를 서비스 외부에서 쓰려고
  export/extract/scrape 하는 것 금지
- Street View Static API Policies: ***"Content pre-fetching, indexing, storing, or caching is generally
  prohibited, except for place IDs and panorama IDs"*** — **파노라마 ID 만** 무기한 저장 허용
- 대량 다운로드 명시적 금지

#### Mapillary — **사용 가능** `[확인]`
- 이미지 **CC BY-SA 4.0**. 재배포·상업 이용 가능, **귀속 + 동일조건변경허락(SA)** 필요
- ⚠️ SA 주의: 파생 **데이터셋을 공개**하면 CC BY-SA 로 공개해야 할 수 있다.
  **모델 가중치는 통상 SA 전파 대상이 아니다** `[추정]`
- Graph API v4: 토큰 `MLY|...`, 타일 `https://tiles.mapillary.com/maps/vtp/mly1_public/2/{z}/{x}/{y}`
  (**z=14 고정**), bbox 최대 0.01 제곱도, 타일당 약 2,000장 상한

#### Open Images / COCO — 사용 가능, 재배포까지 가능 `[확인]`
Open Images 이미지 CC BY 2.0 / 주석 CC BY 4.0. COCO 주석 CC BY 4.0(이미지는 Flickr ToU 종속).

### 5.3 자체 촬영의 법적 근거 `[확인]`

- **개인정보보호법 제28조의2**: "개인정보처리자는 **통계작성, 과학적 연구**, 공익적 기록보존 등을 위하여
  정보주체의 **동의 없이 가명정보를 처리할 수 있다**" → 학술연구 근거 확보
- **개인정보보호위원회 자율주행 가이드**: "원칙적으로 특정 개인을 알아볼 수 없도록 **가명처리(얼굴
  모자이크 처리 등)한 후 활용하여야 하며**". 이동형 영상정보처리기기는 **촬영사실 표시 의무**
  (불빛·소리·안내판). 원본(비블러) 활용은 **규제샌드박스 실증특례**를 통해서만 가능
- **실무 권고**: ① 얼굴·차량번호판 자동 블러(Understand.ai anonymizer 등 — Cityscapes 도 동일 처리)
  → ② 촬영 안내 표시 → ③ 논문 figure 는 블러본만 게재 → ④ IRB / 기관 개인정보 담당 사전 협의

### 5.4 ADE20K 전수 분석 `[실증]` — 기대보다 나쁘다

967MB 를 실제로 받아 22,210장 마스크를 전수 분석했다.
(인덱스는 **1-based**, PNG 픽셀값 = Idx 그대로임을 실증 확인)

클래스별 이미지 수(해당 클래스 800px 초과):
```
sidewalk 3220 | fence 1328 | railing 809 | stairs,steps 730 | water 755
stairway,staircase 531 | path 551 | handrail 345 | river 330 | step,stair 248
bridge 244 | hill 279 | escalator 47 | lake 54 | waterfall 83
계단족(54/60/122/96/97/39) 합집합 = 2,240장
물가족 합집합 = 1,247장 | 계단 ∪ 물가 = 3,369장
```
그런데 **씬 필터를 걸면 급감한다**:
```
옥외 보행 씬 화이트리스트     2,991장
옥외 ∩ 계단족                  408장
옥외 ∩ (계단 ∪ 물가)           559장
```
**육안 검수**: 계단족 상위 씬이 `bedroom`(560), `living_room`(549)로 **대부분 실내**.
`bridge` 씬은 포스브리지·타워브리지 같은 **관광 랜드마크 사진**이고, 옥외 계단 샘플도
건물 현관 계단이 우연히 찍힌 서구 거리 사진이었다. **낙차가 주제인 1인칭 시점 사진이 아니다.**

> ⚠️ **FID 참조분포로 쓰면 "한국 보행 낙차"가 아니라 "서구 관광 사진"과의 거리를 재게 된다.**
> 사전학습·보조용으로만.

### 5.5 기타 실측 `[실증]`

- **Open Images V7**: val 41,620장 전수 필터 → Wall 710, Fence 180, **Stairs 91**, Guard rail 31,
  Manhole 14, Tunnel 11, Escalator 10, Sidewalk 4, Canal 3, Handrail 1 → **합집합 1,019장**.
  train(9M) 스케일 시 대략 20만장대 `[추정]`. 단 `Curb`·`Ditch` 는 val 에서 human-verified 양성 **0건**
- **KartaView — 탈락**: 토큰 없이 API 가 열려 8/8장 다운로드까지 성공했으나 한국 커버리지가
  광화문 1000 / 반포 339 / 신촌 343 / 강남 164 → **기여자 단 2명**, 부산·대전·수원·제주 전부 0장.
  내용도 2016년 강변북로 **대시캠 워시실드 너머** + 2016년 **경복궁 실내**뿐. **사용 불가**

### 5.6 Wikimedia Commons — 오늘 검증 완료 `[실증]`

오늘 실제로 45장을 받았고 파이프라인이 동작한다.

```
엔드포인트:
  https://commons.wikimedia.org/w/api.php?action=query&generator=search
    &gsrsearch=<질의>&gsrlimit=6&gsrnamespace=6
    &prop=imageinfo&iiprop=url|extmetadata&iiurlwidth=1600&format=json

주의: 429 (Too Many Requests) 가 쉽게 걸린다 → 질의당 4초, 다운로드당 1.5초 대기,
      User-Agent 에 연구 목적과 연락처 명시 필수
```
`extmetadata` 가 **`LicenseShortName`(예: "CC BY 2.0"), `License`, `UsageTerms`, `Artist`,
`Credit`, `DateTimeOriginal`, `Restrictions`** 를 함께 반환한다 `[실증]` →
**라이선스 대장 CSV 를 자동 생성**할 수 있어 논문 부록 요건을 그대로 충족한다.

한계 `[추정]`: 검색 기반이라 수백~수천 규모가 상한이고, 한국 보행 씬 밀도가 높지 않다.
**L1(저수준 통계)·2AFC 자극 생성에는 충분하지만 L3 학습셋으로는 부족하다.**

### 5.7 1~2일 내 500~2,000장 확보 — 구체 절차

#### Track A — 오늘 즉시, 계정 불필요 `[실증]`
```bash
curl -L -o ade.zip https://data.csail.mit.edu/places/ADEchallenge/ADEChallengeData2016.zip   # 967MB, 동작 확인
unzip -q ade.zip
# 필터: 마스크 PNG 픽셀값 = 클래스 Idx (1-based)
#   계단족 {54,60,122,96,97,39} / 물가족 {22,61,129,114,110}
#   + sceneCategories.txt 로 옥외 보행 씬만 → 559장
```
→ 559~2,240장 + 픽셀 마스크. **이미지 재배포 불가** → 사내 실험용으로만.

#### Track A' — 오늘 즉시, Wikimedia `[실증]`
§5.6 절차. **라이선스가 파일별로 명확하고 대장이 자동 생성**되는 유일한 즉시 경로.

#### Track B — 오늘~내일, 무료 계정 5분 ★ 실질 1순위
```
1. mapillary.com 가입 → Developers → 앱 등록 → 토큰 MLY|...
2. 한국 bbox 타일 질의 (z=14 고정):
   https://tiles.mapillary.com/maps/vtp/mly1_public/2/14/{x}/{y}?access_token=MLY|...
   pip install mercantile vt2geojson mapbox_vector_tile requests
3. image id → https://graph.mapillary.com/{id}?fields=thumb_2048_url
4. 대상 bbox: 캠퍼스(신촌·관악·대전 KAIST), 한강 둔치·제방, 청계천, 지하보도·육교 주변, 주차장, 골목
```
→ **CC BY-SA 4.0 이라 "한국 + 합법 재배포 + 대량 다운로드"가 동시에 되는 유일한 소스.**
⚠️ **가장 먼저 할 일: 토큰 발급 후 서울 bbox 1개로 커버리지 실측.**
KartaView 가 실측에서 무너진 전례가 있으니 **500장 확보 가능 여부부터 확인**할 것.

#### Track C — 1~3일(승인 대기) ★ 최종 정답
```
aihub.or.kr 가입(내국인) → 데이터 활용 신청 → 승인 후 다운로드
  dataSetSn=513  보행 안전을 위한 도로 시설물 (102.5만장, 계단·연석·경사로·점자블럭)
  dataSetSn=189  인도보행 영상 (67만장, Depth 17만장 포함)
  dataSetSn=159  1인칭 시점 보행영상 (80만장)
```
- **국외 반출 별도 합의 필요, 제3자 제공 금지** → 논문 figure 게재를 위해
  **활용신청서에 "학술 논문 게재" 목적을 명시**해 두는 것이 안전 `[추정]`
- **SideGuide = 위 인도보행 데이터의 논문판(IROS 2020)** `[확인]`.
  해외 공동연구자 경로는 `github.com/ChelseaGH/sidewalk_prototype_AI_Hub` 의 신청 폼

#### Track D — 자체 촬영(병행 권장)
연구실 주변 캠퍼스·하천 둔치·지하보도를 **1인칭(로봇 카메라 높이 0.5~1.2 m)** 으로 촬영하면
**도메인이 정확히 일치**한다. 500장은 반나절이면 충분. 얼굴·번호판 블러 필수.

**최소 평가셋 촬영 프로토콜** `[추정]`
1. 우리 `manifest.json` 프리셋과 **동일한 카메라 높이 3단(0.3 / 0.9 / 1.8 m)** 으로 촬영
2. 낙차 경계로부터 **2 / 5 / 10 m** 3단 거리에서 각각 1장 → 씬당 9장
3. 씬 유형 6종(캠퍼스 계단·지하보도·공원 계단·제방·주차장 턱·옹벽) × 현장 3곳 × 9장 ≈ **162장**
4. **낙차 깊이를 줄자로 실측해 파일명·CSV 에 기록** — 이게 §4.6(e) 회귀 평가의 GT 가 된다
5. **동일 위치에서 "낙차 없음" 대조 컷**도 촬영(hard negative)
6. 노출·화이트밸런스 **고정**(자동 금지). RAW 저장 가능하면 RAW + JPEG 동시

**라벨링 부담 축소** `[추정]`
- **SAM 계열(SAM2 / MobileSAM)로 클릭 몇 번 → 마스크 초안** 생성 후 사람이 수정.
  낙차 위험 영역은 경계가 명확해 SAM 이 잘 듣는 유형
- 라벨 스키마를 **2~3 클래스로 최소화**(위험영역 / 안전보행면 / 무시) — mIoU 19클래스 흉내 금지
- 깊이 GT 는 **폴리곤 단위 스칼라 1개**(줄자 실측값)로 충분. 픽셀별 깊이맵 불필요

### 5.8 방법론 경고 ★

**FID/KID 는 참조 분포가 곧 정답 정의다.** ADE20K(서구 관광사진)나 Cityscapes(독일 차량시점)를
참조로 쓰면 *"한국 보행 낙차와의 거리"* 가 아니라 엉뚱한 것을 최적화하게 된다.
→ **참조셋은 Track B(Mapillary 한국) + Track C(AI Hub) + Track D(자체촬영)로 구성하고,
Track A/A' 는 사전학습·L1 진단·보조로만.**
**카메라 높이·화각·노출 특성까지 렌더와 맞춰야 FID 가 의미를 갖는다** (§2.6 설계 D 와 동일 논리).

**미검증으로 남은 3가지 (계획의 최대 불확실성)** `[미확인]`
1. **Mapillary 한국 실제 커버리지** (토큰 필요)
2. **IDD 라이선스 원문** (로그인 필요)
3. **AI Hub 승인 소요일**

---

## §6. 사람 평가 (perceptual study) 설계

### 6.1 기준 프로토콜: HYPE (NeurIPS 2019)

`[확인]` Zhou, Gordon, Krishna, Narcomey, Fei-Fei, Bernstein, *HYPE: A Benchmark for Human eYe
Perceptual Evaluation of Generative Models*, NeurIPS 2019 (https://arxiv.org/abs/1904.01121).
정신물리학 기반으로 설계됐고 **재현성·비용까지 실측 보고**한 유일한 표준 후보다. 우리는 이걸 그대로 베낀다.

**HYPE∞ (권장 — 저비용 변형)** `[확인]`

| 항목 | HYPE 원 설정 |
|---|---|
| 평가자당 이미지 | **100장 (실사 50 + 합성 50)** |
| 모델당 평가자 수 | **30명** (10~120명 비용분석 수행, **CI 가 30명 부근에서 수렴**) |
| 시간 | 평가자당 **약 10분** |
| 보수 | 정답당 $0.02, 시급 환산 **$12/hr**, 자격시험 기본 $1 |
| 모델당 총비용 | **약 $60** |
| 자격 선별 | 사전 자격시험 100장(실사50/합성50)에서 **실사·합성 각각 65% 이상** 정답.<br>무작위 추측으로 통과할 확률 1/1000 |
| 점수 정의 | **오분류 비율**. 50% = 구별 불가(완벽), 50% 초과 = 초현실(hyper-realism) |
| 신뢰구간 | 평가자 30명을 복원추출로 재표집 ×10,000회 → **95% 부트스트랩 CI** |

**HYPE-Time (고비용 변형)** `[확인]`

- **3-up/1-down 적응형 계단법** → 이론상 75% 정답 임계 수렴
- 노출 시간 범위 **100–1000 ms**, 상승 10 ms / 하강 30 ms
- 평가자당 **150장**(합성 50% / 실사 50%), 3블록
- 각 자극 뒤 **지각 마스크 4장을 30 ms 씩** 제시 (잔상 차단 — 반드시 넣어야 함)
- 평가자당 약 60분, 모델당 **약 $360**
- HYPE∞ 대비 시간·비용 6배

### 6.2 우리 실험 설계 (권장안) `[추정, 위 프로토콜 기반]`

**목표를 명확히 하라.** 우리가 증명할 명제는 두 가지 중 하나여야 한다.

| 명제 | 검정 형태 | 실현 가능성 |
|---|---|---|
| (a) "우리 렌더는 실사와 구별 불가하다" | H0: p=0.5 를 **기각하지 못함** + 동등성 구간 | **현 단계에서 불가능** `[추정]` |
| (b) **"개선 v7→v9 로 판별 정확도가 유의하게 감소했다"** | 두 조건 간 **쌍체 비교** | **현실적. 이걸 목표로 하라** |

**표본 수 계산** `[측정, 정규근사 이항검정, α=0.05 양측]`

| 참 판별 정확도 | 검정력 80% 필요 시행수 | 검정력 90% |
|---|---|---|
| 0.55 | 783 | 1047 |
| 0.60 | 194 | 259 |
| 0.65 | 85 | 113 |
| 0.70 | 47 | 61 |
| 0.75 | 29 | 38 |
| 0.90 | 10 | 12 |

**"정확도가 X 이하임"을 보이려는 경우 (동등성/비열등성)의 CI 폭** `[측정]`

| 총 시행수 | 95% CI 반폭 (p≈0.55에서) |
|---|---|
| 100 | ±0.098 |
| 400 | ±0.049 |
| 800 | ±0.035 |
| **1600** | **±0.024** |
| 3200 | ±0.017 |

**권장 규모** `[추정]`:
- **평가자 30명 × 이미지 100장 = 3,000 시행**. HYPE∞ 와 동일 규모이며 CI 반폭 약 ±0.018 로 충분.
- 우리 PT 렌더 493장 중 **씬당 균등 표집으로 50장**, 실사 50장은 §5 참조셋에서
  **씬 유형 매칭**(계단↔계단, 제방↔제방)해 뽑는다 — 내용 단서로 맞히는 걸 막기 위해 필수.
- **전처리를 반드시 통일**하라(§2.4). 해상도·압축·종횡비가 다르면 피험자가 사실성이 아니라
  **JPEG 아티팩트로 판별**한다. 실제로 이게 이런 실험의 가장 흔한 무효화 원인이다 `[추정]`.
- 조명 조건 통일: 우리 본편 21씬은 **정오 맑음 단일 조건**이므로 실사도 **주간 맑음**만 골라야 한다.
- **크롭 조건 병행 권장** `[추정]`: 전체 이미지(구도·내용 단서 포함)와 **256×256 랜덤 크롭**
  (재질·미세기하만 남김) 두 조건. 크롭 조건에서 먼저 50% 에 가까워지는 게 현실적 중간 목표이며,
  §3 의 저수준 지표 개선과 직접 대응하므로 스토리가 깔끔하다.

**통계 검정** `[추정]`
- 조건 내: 이항검정 또는 CI. 평가자 간 변동은 **평가자 단위 부트스트랩**(HYPE 방식) 또는
  **평가자 랜덤효과 혼합 로지스틱 회귀(GLMM)** — 후자가 방법론적으로 더 방어적이다.
- v7 vs v9 비교: 같은 평가자가 두 조건을 다 보면 **McNemar 검정**(쌍체), 다르면 **2-비율 z 검정**.
- 다중비교(씬 유형별로 쪼개 볼 경우) **Holm–Bonferroni** 보정.

**윤리·실무** `[추정]`: 소속 기관 IRB 면제 대상인지 확인 필요(익명 지각 실험은 통상 면제).
Prolific/MTurk 대신 **연구실 내부 + 학부생 피험자**로도 30명은 가능하나, **저자와 라벨을 아는 사람은
반드시 제외**해야 한다.

### 6.3 사람 평가로 무엇을 주장할 수 있고 없는가

`[확인]` Stein et al. 2023 의 결론 — **어떤 자동 지표도 인간 사실성 판단과 강하게 상관하지 않는다**.
이건 양날이다.
- **유리**: 사람 평가가 자동 지표로 대체 불가능하다는 근거가 있으므로, 사람 평가를 넣는 것이 정당화된다.
- **불리**: 반대로 **사람이 사실적이라고 해도 태스크 성능이 좋다는 보장이 없다**.
  → **사람 평가는 §4 전이 성능을 대체하지 못한다.** 보조 증거로만 배치하라.

---

## §7. 지금 당장 실행할 최소 세트 (1~2일)

원칙: **설치 최소, 실사 의존 최소, 결과가 baseline 으로 고정되는 것부터.**
현 환경 `[측정]`: `/home/vislab/Desktop/work_sy/.venv`, Python 3.10.12, numpy 2.2.6, torch 2.6.0+cu124(CUDA 가용),
torchvision 0.21.0, pillow 12.2.0, matplotlib, pandas. **scipy·opencv·sklearn 없음**(불필요).

### S0. 참조 실사셋 부트스트랩 (2~3시간) — **선행 조건**

- **이미 검증됨** `[실증]`: Wikimedia Commons API 로 라이선스가 명확한 실사 사진을 스크립트로 수집 가능.
  오늘 45장을 실제로 받았다. 429(rate limit)가 걸리므로 **질의당 4초, 다운로드당 1.5초 대기** 필요.
  `extmetadata` 가 라이선스·저작자·촬영일을 함께 주므로 **대장 CSV 자동 생성**된다(§5.6).
- 목표: **씬 유형 태그가 붙은 실사 300~500장**. 질의 예: `Seoul sidewalk`, `Korea pedestrian overpass`,
  `park stairway`, `riverside levee path`, `pedestrian underpass`, `retaining wall walkway`,
  `tactile paving`, `dropped kerb`, `loading dock exterior`, `quay wall waterfront`
- 수동 필터: 야간·실내·역사사진·흑백 제거(우리 스코프가 **주간 가시광**이므로 필수)
- 저장: `Docs/surveys/realism_gap_2026-07-28/refset/` + **출처 URL·라이선스·저자 CSV 동봉**
- **병행 착수 권장** `[확인, §5.7]`: ① Mapillary 토큰 발급 후 **서울 bbox 1개로 커버리지 실측**
  (KartaView 가 실측에서 무너진 전례가 있음) ② **AI Hub 513/189 활용신청** 제출 — 승인에 1~3일 걸리므로
  오늘 넣어야 이번 주에 쓴다
- ⚠️ ADE20K 는 **직링크가 열리지만**(967MB) 전수 분석 결과 옥외 보행 씬 ∩ 계단/물가가 **559장뿐이고
  대부분 서구 관광사진**이다 `[실증]`. **L1 진단·사전학습 보조용으로만.**

### S1. 저수준 통계 baseline 고정 (반나절) ★가장 먼저

```
scripts/measure_nis.py                       # 신규. numpy+PIL 만 사용
  --syn  'look_check/scene*/v*_pt/pt_*.png'
  --real 'Docs/surveys/.../refset/*.jpg'
  --out  Docs/surveys/.../nis_v7.json
```
구현 사양(§3.1~3.5 절차 그대로):
- 네이티브 1024 센터 크롭(리샘플 금지). 1024 미만 이미지는 스킵하거나 별도 기록
- 산출: 이미지별 `slope_10_256, slope_lo, slope_mid, slope_hi, hf_frac_128, hf_frac_256,
  noise_floor_p10, noise_floor_med, **tile_sd_p1, tile_sd_p5, tile_sd_p10**, lc_med,
  grad_sd, grad_kurt, power_aniso, slope_aniso, std_l, std_alpha, std_beta, mean_sat`
  (★ `tile_sd_p1` = 8×8 로그휘도 타일 SD 의 1퍼센타일 — §3.6a 에서 **24.9배**로 가장 민감했다)
- 집계: **씬 단위 그룹 부트스트랩**(B=1000)으로 평균과 95% CI
- 검정: 순열검정 20,000회
- 출력물: `nis_v7.json` + 지표별 **박스플롯 PNG**(합성 vs 실사) + §3.8 스코어카드 마크다운
- **JPEG 통제 옵션 내장**: 합성 쪽도 q=95 로 재인코딩한 변형을 함께 측정해
  코덱 교란이 없음을 매 실행마다 확인(§3.6a 통제 1)

**기대 출력** — 이미 파일럿으로 확보 `[측정]`:
기울기 −2.70 vs −1.94 / HF비율 9.2× 부족 / 노이즈 14× 부족 / 평탄 1% 타일 24.9× 부족 /
로컬콘트라스트 4.4× 부족. **이 값들이 v7 baseline 이 된다.**

### S2. 도메인 판별기 baseline (1~2시간)

```
scripts/measure_domain_clf.py
```
- ImageNet ResNet18(또는 ResNet50) penultimate 특징 → 로지스틱 프로브
- 입력: 224×224 랜덤 크롭 4~8개/이미지
- **씬/사진 단위 그룹 5-fold CV 필수** (같은 씬이 train/test 에 동시에 들어가면 수치가 부풀려진다)
- 산출: balanced accuracy ± SD, **Proxy A-distance = 2(2·acc−1)**
- **기대 출력** — 이미 확보 `[측정]`: **acc 0.928 ± 0.069, d_A = 1.71**
- 확장(선택): 판별기의 **Grad-CAM** 을 떠서 "무엇을 보고 가짜라고 하는가"를 시각화 → 개선 항목 직접 도출.
  이건 논문 그림으로도 강력하다 `[추정]`

### S3. 센서 후처리 A/B — **"후처리로 못 닫는 잔차"를 정량화하는 실험** (반나절)

⚠️ **§3.6a 통제 실험 결과에 따라 이 항목의 성격이 바뀌었다.**
당초 "가장 저렴한 실질 개선"으로 기대했으나, **노이즈 주입은 비현실적 강도(중간회색 16.7% 그레인)
에서만 노이즈 플로어를 맞추고 그때조차 고주파 결손은 5.5분의 1에 그친다** `[측정]`.
따라서 S3 는 **개선 수단이 아니라 진단 실험**이다 — *"후처리로 닫을 수 있는 몫"과 "기하/재질을
실제로 고쳐야 하는 몫"을 분해*하는 것이 목적이다. 그 잔차가 렌더 파이프라인 개편의 정량적 근거가 된다.

`[확인]` 센서 효과 모델링 자체는 여전히 유효하다 — Carlson et al. ECCV-W 2018 (§3.5) 은
색수차·블러·노출·노이즈·색온도 랜덤화로 **증강 2,975장이 미증강 20,000장 이상을 능가**했다.
다만 그 논문의 이득은 **저수준 통계를 맞춰서**라기보다 **증강에 의한 불변성 학습**에서 왔을 가능성이
크다 `[추정]` — 즉 S3 는 §3 지표를 고치는 게 아니라 **§4 의 전이 성능을 올리는 수단**으로 봐야 한다.

적용 순서(물리적으로 이 순서여야 함) `[추정]`:
```
선형화 → 렌즈 (비네팅 → 횡색수차 → 약한 디포커스/PSF)
       → 센서 (광자 산탄잡음 √I 비례 + 읽기잡음 가우시안, 현실 범위 K=3,000~30,000)
       → ISP  (약한 샤프닝 → 노출/AWB 지터 → 톤커브 → sRGB → JPEG q≈92 재인코딩)
```
- 파라미터를 3~5 프리셋으로 스윕하되 **NIS-Gap 최소화가 아니라 "현실적 센서 범위 내"로 제약**할 것.
  NIS-Gap 만 보고 최적화하면 K=200 같은 **물리적으로 말이 안 되는 그레인**으로 수렴한다 `[측정]`
- 산출: **후처리 전/후 NIS-Gap 과 PAD** 2×2 표. **후처리 후에도 남는 잔차 = 기하/재질 부채**
- ★ 이 분해 자체가 논문의 좋은 ablation 이다: *"센서 모델링으로 X% 를 닫았고, 나머지 Y% 는
  자산(geometry/material) 수준의 문제였다"*

### S3'. 미세구조(mesostructure) 개선 — **실제 주력** `[추정, §3.6a 근거]`

§3.6a 가 지목하는 실제 부채. S1 의 지표로 각 작업의 효과를 직접 측정할 수 있다.

| 작업 | 겨냥하는 지표 | 비고 |
|---|---|---|
| 지면/벽에 **디테일 노멀 + 미세 러프니스 변조**(고주파 노이즈 텍스처 블렌딩) | hf_frac, noise_floor, lc_med | 가장 싸다. MDL 파라미터만 추가 |
| **변위/테셀레이션** 도입(지면 미세 기복·침하·균열) | slope, lc_med, grad_kurt | 렌더 비용 증가 |
| **데칼**(오염·균열·페인트·이끼·물자국) | hf_frac, aniso, 색도 분산 | 시각적 효과 대비 비용 최저 |
| **베벨/챔퍼**(현재 0건) | grad_kurt (하드 에지 완화) | 첨도 96 → 실사 18 방향 |
| **소품 엔트로피**(낙엽·쓰레기·케이블·맨홀) | hf_frac, lc_med, aniso | 축정렬 이방성(0.93 → 0.49) 완화에도 기여 |
| **식생 지오메트리**(현재 잔디=텍스처, 나무=구 3개) | 전 지표. **씬 04 "게임 같다" 지적의 직접 원인** | 비용 최대 |

### S4. 내용 통제 CMMD (하루, S0 완료 후)

- `pip install open_clip_torch` (또는 `transformers`) → CLIP ViT-L/14@336
- CMMD: σ=10, 불편 MMD², ×1000 스케일 (§2.1 사양 그대로)
- **반드시 함께 보고**: `floor = CMMD(Real_A, Real_B)` (실사 무작위 반분)
- 층화: 씬 유형별 × 카메라 높이별 (`manifest.json` 의 `eye`/`tgt` 활용)
- 전처리 계약(§2.4) 엄수: 양쪽 동일 크롭·동일 리사이즈·동일 JPEG 품질
- 씬 단위 부트스트랩 CI
- 선택: FD-DINOv2 는 2048장 하한 때문에 지금은 부적합. 실사셋이 2000장을 넘으면 추가.

### S5. 회귀 감시 훅 (1시간)

`scripts/nis_report.sh` — 새 렌더 배치가 나올 때마다 S1+S2 를 자동 실행해
`Docs/surveys/.../nis_history.csv` 에 한 줄 append. 컬럼: `날짜, 버전, slope, hf128, noise, lc, kurt, aniso, d_A, NIS-Gap`.
→ **judge_v*.md 의 육안 심사를 대체하는 게 아니라, 그 옆에 객관 수치 열을 하나 붙이는 것.**

### 실행 순서 요약

| 순서 | 작업 | 소요 | 선행 | 산출 |
|---|---|---|---|---|
| 0 | **AI Hub 513/189 활용신청 제출 + Mapillary 토큰 발급** | 30분 | 없음 | 승인 대기 시작(1~3일) |
| 1 | **S1 저수준 통계 baseline** | 반나절 | 없음(실사 45장으로 이미 가능) | `nis_v7.json` + 스코어카드 |
| 2 | **S2 도메인 판별기 baseline** | 1~2h | 없음 | `d_A = 1.71` 고정 |
| 3 | **S0 실사셋 300~500장** | 2~3h | 없음 | `refset/` + 라이선스 CSV |
| 4 | **S3 센서 후처리 A/B (잔차 분해)** | 반나절 | S1,S2 | "후처리로 못 닫는 몫" 정량화 |
| 5 | **S3' 미세구조 개선 착수** | — | S3 | 실제 갭 축소 |
| 6 | S5 회귀 훅 | 1h | S1,S2 | `nis_history.csv` |
| 7 | S4 내용통제 CMMD | 1일 | S0 | 본문 표 후보 |

---

## §8. 우리 프로젝트에 대한 실행 함의 (우선순위)

| 우선 | 작업 | 예상 효과 | 난이도 | 소요 | 선행조건 |
|---|---|---|---|---|---|
| **P0** | S1 저수준 통계 baseline 고정 | 개선 전/후 비교의 **기준선 확보**. 없으면 이후 모든 주장이 무근거 | 하 | 반나절 | 없음 |
| **P0** | S2 도메인 판별기 baseline | 단일 스칼라 갭 지표(d_A=1.71) 확보 | 하 | 1~2h | 없음 |
| **P0** | S0 실사 참조셋 300~500장(Wikimedia) + 라이선스 대장 | **L2·L3 전체의 병목 해소**. 논문 부록 필수 | 하 | 2~3h | 없음 |
| **P0** | **AI Hub 513/189 활용신청 + Mapillary 토큰 발급/커버리지 실측** | 승인 1~3일 대기 → **오늘 넣어야 이번 주에 쓴다**. 한국 낙차 라벨의 유일 경로 | 하 | 30분 | 내국인 계정 |
| **P1** | **S3' 미세구조 개선**(디테일 노멀·미세 러프니스·데칼·베벨·변위) | **§3.6a 가 특정한 진짜 원인.** 후처리로는 못 닫는 갭 | 중~상 | — | S1 |
| **P1** | S3 센서 후처리 A/B (**진단 실험으로 재정의**) | "후처리로 닫는 몫 vs 자산으로 닫을 몫" 분해 → 논문 ablation | 중 | 반나절 | S1,S2 |
| **P1** | **실사 클론 페어 3~5곳** (TurtleBot 촬영 → Isaac Sim 디지털 트윈 → 동일 포즈 렌더) | **§2.6-C 내용통제 + §4.4 사실성 직접증거 + §6 자극생성을 한 자산으로 해결.** 투자 대비 효과 최대 | 중상 | 2~3일 | 실물 촬영 |
| **P2** | S4 내용통제 CMMD(+실사 floor) | 논문 본문 표 1열 확보 | 중 | 1일 | S0 |
| **P2** | **조건 변주 확대**(계절·기상·시간대·재질) | `[확인]` *"photo-realism < diversity"* (Nowruzi 2019). 사실성만 올리면 반박당함 | 중 | — | — |
| **P3** | 태스크 기반 S→R 평가(§4 표 A/B/C) | **논문 주장의 실질 근거** | 상 | 수주 | GT 파이프라인, 실사 라벨 |
| **P3** | 사람 평가 HYPE∞ 30명 × 100장 | 보조 증거. **개선 후**에 실시 | 중 | 1주 | 개선 완료, IRB 확인 |
| **P4** | S5 회귀 감시 훅 | 재발 방지 | 하 | 1h | S1,S2 |

**하지 말아야 할 것**

- ✗ **FID(InceptionV3) 단독 숫자를 사실성 근거로 논문에 싣기** `[확인]` — §2.2/§2.5/§4.7(b) 근거로
  반박당한다 (SADGE 벤치마크에서 FID r=0.635 vs DINOv2 r=0.878)
- ✗ **내용 통제 없이 CMMD/FID 를 Cityscapes·ADE20K 와 비교** `[확인, §5.8]` — 측정값이
  "한국 보행 낙차와의 거리"가 아니라 "독일 차량시점" 또는 "서구 관광사진"과의 거리가 된다
- ✗ **현 상태에서 2AFC 사람 실험 실시** `[추정]` — 판별 정확도가 천장에 붙어 논문에 못 쓴다
  (참고: 오늘 측정한 **기계** 판별 정확도가 이미 92.8% 다 `[측정]`)
- ✗ **PT spp 를 더 올려서 사실성을 개선하려는 시도** — §3.6/§3.6a 의 측정값이 **이미 totalSpp=512
  PathTracing 결과물**에서 나온 것이다 `[측정]`. Reinhard et al. 2004 와 일치
- ✗ **센서 노이즈 후처리만으로 갭을 닫으려는 시도** `[측정, §3.6a]` — 실사 노이즈 플로어를 맞추려면
  중간회색 16.7% 그레인이 필요하고(비물리적), 그때조차 고주파 결손은 5.5분의 1만 회복된다
- ✗ **네이버/카카오/구글 로드뷰 사용** `[확인, §5.2]` — 세 곳 모두 약관상 저장·DB화·스크래핑 금지.
  특히 네이버는 "즉시 1회 사용만 허용"이 명문
- ✗ `look_refs/*.jpg` 를 실사 참조로 사용 — **nanobanana 생성 이미지**다. 파일럿에서 확인했듯
  통계는 실사에 가깝지만(α=−2.04) **논문에서 "실사 참조"로 주장할 수 없다** `[측정]`
- ✗ **사실성만 올리고 다양성을 방치** `[확인]` — *"photo-realism is not as important as the diversity
  of the data"* (Nowruzi et al. ICML-W 2019)

---

## 부록 A. 출처 목록

**분포 거리 지표**
- Jayasumana, Ramalingam, Veit, Glasner, Chakrabarti, Kumar. *Rethinking FID: Towards a Better
  Evaluation Metric for Image Generation*. CVPR 2024. https://arxiv.org/abs/2401.09603
- Stein, Cresswell, et al. *Exposing flaws of generative model evaluation metrics and their unfair
  treatment of diffusion models*. NeurIPS 2023. https://arxiv.org/abs/2306.04675 ·
  코드 https://github.com/layer6ai-labs/dgm-eval
- Bińkowski, Sutherland, Arbel, Gretton. *Demystifying MMD GANs*. ICLR 2018. https://arxiv.org/abs/1801.01401
- Chong, Forsyth. *Effectively Unbiased FID and Inception Score and Where to Find Them*. CVPR 2020.
  https://arxiv.org/abs/1911.07023
- Parmar, Zhang, Zhu. *On Aliased Resizing and Surprising Subtleties in GAN Evaluation*. CVPR 2022.
  https://arxiv.org/abs/2104.11222 · 코드 https://github.com/GaParmar/clean-fid
- *SADGE: Structure and Appearance Domain Gap Estimation of Synthetic and Real Data*.
  https://arxiv.org/html/2605.22467v1
- torchmetrics KID 문서. https://torchmetrics.readthedocs.io/en/v0.10.2/image/kernel_inception_distance.html
- FD-DINOv2 비공식 구현. https://github.com/justin4ai/FD-DINOv2

**자연 이미지 통계**
- Ruderman, Bialek. *Statistics of Natural Images: Scaling in the Woods*. NIPS 1993 / Phys. Rev. Lett. 73, 814 (1994).
- Huang, Mumford. *Statistics of Natural Images and Models*. CVPR 1999.
- van der Schaaf, van Hateren. *Modelling the Power Spectra of Natural Images: Statistics and
  Information*. Vision Research 36(17), 1996.
- Koch, Denzler, Redies. *1/f² Characteristics and Isotropy in the Fourier Power Spectra of Visual Art,
  Cartoons, Comics, Mangas, and Different Categories of Photographs*. PLOS ONE 5(8):e12268, 2010.
  https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0012268
- Reinhard, Shirley, Ashikhmin, Troscianko. *Second order image statistics in computer graphics*.
  APGV 2004. https://dl.acm.org/doi/10.1145/1012551.1012568
- Pouli, Cunningham, Reinhard. *A Survey of Image Statistics Relevant to Computer Graphics*.
  Computer Graphics Forum 30(6), 2011.
- Lyu, Farid. *How realistic is photorealistic?* IEEE Trans. Signal Processing 53(2), 2005.
- Farid, Lyu. *Higher-order wavelet statistics and their application to digital forensics*. CVPR-W 2003.

**센서 효과 / 합성 데이터셋 / sim2real 프로토콜**
- Carlson, Skinner, Vasudevan, Johnson-Roberson. *Modeling Camera Effects to Improve Visual Learning
  from Synthetic Data*. ECCV Workshops 2018. https://arxiv.org/abs/1803.07721
- Wrenninge, Unger. *Synscapes: A Photorealistic Synthetic Dataset for Street Scene Parsing*. 2018.
  https://arxiv.org/abs/1810.08705
- Richter, Vineet, Roth, Koltun. *Playing for Data: Ground Truth from Computer Games*. ECCV 2016.
  https://arxiv.org/abs/1608.02192
- Ros, Sellart, Materzynska, Vázquez, López. *The SYNTHIA Dataset*. CVPR 2016, pp. 3234–3243.
  DOI 10.1109/CVPR.2016.352 (수치는 원문 표 재확인 필요 `[미확인]`)
- Gaidon, Wang, Cabon, Vig. *Virtual Worlds as Proxy for Multi-Object Tracking Analysis* (Virtual KITTI).
  CVPR 2016. https://arxiv.org/abs/1605.06457
- Roberts, Ramapuram, Ranjan, Kumar, Bautista, Paczan, Webb, Susskind. *Hypersim: A Photorealistic
  Synthetic Dataset for Holistic Indoor Scene Understanding*. ICCV 2021. https://arxiv.org/abs/2011.02523
- Prakash, Boochoon, Brophy, Acuna, Cameracci, State, Shapira, Birchfield. *Structured Domain
  Randomization*. ICRA 2019. https://arxiv.org/abs/1810.10093
- Kar, Prakash, Liu, Cameracci, Yuan, Rusiniak, Acuna, Torralba, Fidler. *Meta-Sim: Learning to Generate
  Synthetic Datasets*. ICCV 2019. https://arxiv.org/abs/1904.11621
- Tremblay, To, Birchfield. *Falling Things*. CVPR-W 2018. https://arxiv.org/abs/1804.06534
- Nowruzi, Kapoor, Kolhatkar, Al Hassanat, Laganiere, Rebut. *How much real data do we actually need*.
  ICML-W 2019. https://arxiv.org/abs/1907.07061
- Hoyer, Dai, Van Gool. *DAFormer*. CVPR 2022. https://arxiv.org/abs/2111.14887
- Ravuri, Vinyals. *Classification Accuracy Score for Conditional Generative Models*. NeurIPS 2019.
  https://arxiv.org/abs/1905.10887
- Ben-David, Blitzer, Crammer, Kulesza, Pereira, Vaughan. *A theory of learning from different domains*.
  Machine Learning 79, 2010. (H-divergence) · 용어 원출처 Ben-David et al., NIPS 2006
- Ganin, Ustinova, Ajakan, Germain, Larochelle, Laviolette, Marchand, Lempitsky.
  *Domain-Adversarial Training of Neural Networks*. JMLR 17(59), 2016. https://arxiv.org/abs/1505.07818
  (proxy A-distance 수식 §3.2)
- Alvarez-Melis, Fusi. *Geometric Dataset Distances via Optimal Transport* (OTDD). NeurIPS 2020.
  https://arxiv.org/abs/2002.02923
- Li, Yuan, Vasconcelos. *Content-Consistent Matching for Domain Adaptive Semantic Segmentation*.
  ECCV 2020. https://link.springer.com/chapter/10.1007/978-3-030-58568-6_26

**negative obstacle / 안전 태스크 지표**
- Goodin, Carrillo, Monroe, Carruth, Hudson. *An Analytic Model for Negative Obstacle Detection with
  Lidar and Numerical Validation Using Physics-Based Simulation*. Sensors 21(9):3211, 2021.
  https://pmc.ncbi.nlm.nih.gov/articles/PMC8125519/
- Xie, Wang, Huang, Gao, Bai, Zhang, Ye. *LiDAR-Based Negative Obstacle Detection for Unmanned Ground
  Vehicles in Orchards*. Sensors 2024. https://pmc.ncbi.nlm.nih.gov/articles/PMC11679008/
- Larson, Trivedi. *Lidar based off-road negative obstacle detection and analysis*. IEEE ITSC 2011.
  DOI 10.1109/ITSC.2011.6083105 (수치 `[미확인]` — DTIC 접근 차단)
- Matthies, Rankin. *Negative obstacle detection by thermal signature*. IROS 2003.
  DOI 10.1109/IROS.2003.1250744 (야간 — 우리 스코프 밖)
- Dollár, Wojek, Schiele, Perona. *Pedestrian Detection: An Evaluation of the State of the Art*.
  IEEE TPAMI 34(4):743–761, 2012. (LAMR / MR⁻²)
- Sun, Kretzschmar, Dotiwalla, Chouard, Patnaik, et al. *Scalability in Perception for Autonomous
  Driving: Waymo Open Dataset*. CVPR 2020. https://arxiv.org/abs/1912.04838
- Jiang, Osteen, Wigness, Saripalli. *RELLIS-3D Dataset*. ICRA 2021. https://arxiv.org/abs/2011.12954
- Eigen, Puhrsch, Fergus. *Depth Map Prediction from a Single Image using a Multi-Scale Deep Network*.
  NIPS 2014. https://arxiv.org/abs/1406.2283

**보정 (calibration) / 통계**
- Guo, Pleiss, Sun, Weinberger. *On Calibration of Modern Neural Networks*. ICML 2017.
  https://arxiv.org/abs/1706.04599
- Nixon, Dusenberry, Jerfel, Nguyen, Liu, Zhang, Tran. *Measuring Calibration in Deep Learning*.
  CVPR-W 2019. https://arxiv.org/abs/1904.01685 (SCE / ACE)
- Ding, Han, Liu, Niethammer. *Local Temperature Scaling for Probability Calibration*. ICCV 2021.
  https://arxiv.org/abs/2008.05105
- Ovadia, Fertig, Ren, Nado, Sculley, Nowozin, Dillon, Lakshminarayanan, Snoek. *Can You Trust Your
  Model's Uncertainty?*. NeurIPS 2019. https://arxiv.org/abs/1906.02530
- Minderer, Djolonga, Romijnders, Hubis, Zhai, Houlsby, Tran, Lucic. *Revisiting the Calibration of
  Modern Neural Networks*. NeurIPS 2021. https://arxiv.org/abs/2106.07998
- Bouthillier, Delaunay, Bronzi, Trofimov, Nichyporuk, Szeto, Sepah, Raff, Madan, Voleti, Kahou,
  Michalski, Serdyuk, Arbel, Pal, Varoquaux, Vincent. *Accounting for Variance in Machine Learning
  Benchmarks*. MLSys 2021. https://arxiv.org/abs/2103.03098
- Kornblith, Norouzi, Lee, Hinton. *Similarity of Neural Network Representations Revisited* (CKA).
  ICML 2019. https://arxiv.org/abs/1905.00414

**사람 평가**
- Zhou, Gordon, Krishna, Narcomey, Fei-Fei, Bernstein. *HYPE: A Benchmark for Human eYe Perceptual
  Evaluation of Generative Models*. NeurIPS 2019. https://arxiv.org/abs/1904.01121

**데이터 소스 / 라이선스 (§5)**
- AI Hub. https://aihub.or.kr — `dataSetSn=513` 보행 안전을 위한 도로 시설물 데이터 /
  `dataSetSn=189` 인도보행 영상 / `dataSetSn=159` 1인칭 시점 보행영상
- SideGuide (IROS 2020) 신청 경로. https://github.com/ChelseaGH/sidewalk_prototype_AI_Hub
- NAVER Cloud Platform, *AI·NAVER API 서비스 이용약관* 부가조항 「Maps API 서비스」(2)
- Kakao Developers 운영정책 제5조(금지된 행동) 20호·30호. https://developers.kakao.com/terms/ko/site-policies
- Google Maps Platform Terms of Service §3.2.3(a) "No Scraping" / Street View Static API Policies
- Mapillary 라이선스(CC BY-SA 4.0) 및 Graph API v4 / vector tile 엔드포인트
- ADE20K SceneParse150. https://data.csail.mit.edu/places/ADEchallenge/ADEChallengeData2016.zip
- Open Images V7 (이미지 CC BY 2.0 / 주석 CC BY 4.0), COCO-Stuff (주석 CC BY 4.0)
- Mapillary Vistas, Cityscapes, BDD100K, KITTI/KITTI-360, nuScenes, Waymo Open, ACDC, WildDash2, IDD
- Wikimedia Commons MediaWiki API. https://commons.wikimedia.org/w/api.php
- 개인정보보호법 제28조의2(가명정보의 처리) / 개인정보보호위원회 자율주행 영상정보 가이드

## 부록 B. 파일럿·통제 실험 재현 정보 `[측정]`

**환경** 실행일 2026-07-28. `/home/vislab/Desktop/work_sy/.venv`
(Python 3.10.12, numpy 2.2.6, pillow 12.2.0, torch 2.6.0+cu124, torchvision 0.21.0).
**scipy·opencv·sklearn 없이** 전부 실행됨.

**데이터**
- 합성: `look_check/scene*/v*_pt/pt_*.png` — §3.6 본표 120장, 보조표 40장, 통제실험 30~60장
- 실사: Wikimedia Commons API
  (`action=query&generator=search&gsrnamespace=6&prop=imageinfo&iiprop=url|extmetadata`)
  로 수집한 45장 중 1024px 이상 36~44장. 질의 15종(보도·옥외계단·제방·지하도·공원길 등)

**전처리**
- §3.6 본표·통제실험: **네이티브 1024×1024 센터 크롭, 리샘플 없음** (§2.4 함정 회피)
- 보조표: 센터 정사각 크롭 후 bicubic 1024 리사이즈

**실행한 4개 실험**
1. §3.6 저수준 통계 비교 (합성 120 vs 실사 36), 순열검정 20,000회
2. §3.6a 통제 1 — 렌더 PNG vs JPEG q=95 재인코딩 (n=60)
3. §3.6a 통제 2 — 광자 산탄잡음 K ∈ {12000, 3000, 800, 200, 50} 스윕 (n=30)
4. §3.6a 통제 3 — 8×8 로그휘도 타일 표준편차 분위수 (렌더 30 vs 실사 36)
5. §3.7 도메인 판별기 — ImageNet ResNet18 특징 + 로지스틱 프로브, **그룹 5-fold CV**

**주의** 파일럿 스크립트는 스크래치패드에만 있다. **S1/S2 로 정식 구현할 때
`scripts/measure_nis.py`, `scripts/measure_domain_clf.py` 로 옮겨 커밋할 것.**
실사 참조 36장은 **표본이 작고 내용이 통제되지 않았다** — §2.6 설계 B/C 를 적용해 재측정해야
최종 수치가 된다.
