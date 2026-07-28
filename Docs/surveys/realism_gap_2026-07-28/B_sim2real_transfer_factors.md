# B. RGB 인지 모델의 sim2real 전이를 실제로 좌우하는 요인 — 문헌 근거와 우선순위

작성일: 2026-07-28 · 대상 프로젝트: Practice_NegObs (비가시 낙차 맥락 추정, Isaac Sim → 실환경)
표기 규칙: **[확인]** = 논문에 명시된 수치/주장 · **[해석]** = 확인된 수치로부터의 논리적 추론 · **[추정]** = 직접 근거 없는 저자 판단

---

## §1 결론 요약 — 우리 자원을 어디에 넣어야 하는가

1. **"예쁘게 만들기"는 ROI 1순위가 아니다.** 문헌에서 단일 요인으로 가장 큰 전이 이득을 낸 것은 순서대로 ① **사전학습 비전 파운데이션 백본**(+15~19 mIoU급, [확인] Rein/DINOv2), ② **장면 구성·배치 통계의 구조화**(+21~28 AP, [확인] SDR vs DR), ③ **센서/이미지 형성 시뮬레이션**(+4~7 AP, [확인] Carlson 2018)이며, 이 셋은 모두 **에셋 제작이 아니라 코드 작업**이다.
2. **그럼에도 렌더 사실성은 "무시해도 되는" 수준이 아니다.** 포토리얼 합성(Synscapes)은 게임 렌더(GTA5) 대비 합성단독 학습에서 **+18.2 mIoU**, PBR 레이트레이싱은 OpenGL render&paste 대비 **상대 +25~36% AR**을 냈다 [확인]. 우리 현재 렌더는 GTA5보다도 아래(무텍스처 박스·구 뭉치 식생)이므로 **하한선을 끌어올리는 최소 투자는 필수**다.
3. **가장 위험한 것은 낮은 사실성 자체가 아니라, 낮은 사실성 + 단서-라벨 완전상관이 만드는 지름길 학습이다.** 우리 태스크(맥락 → 비가시 낙차)는 구조적으로 지름길에 극도로 취약하다. 특히 **카메라 높이/피치가 9개 이산값뿐**이라 모델이 "이미지 y좌표 = 낙차"를 학습할 조건이 완비돼 있다 [해석, van Dijk & de Croon 2019 + Islam et al. 2020 근거].
4. **소량 실데이터 파인튜닝이 사실성 격차의 대부분을 지운다.** Synscapes 논문에서 합성단독 성능은 50.35 vs 32.20 mIoU로 18점 차였지만, 실데이터 파인튜닝 후 세 데이터셋 모두 **77~79 mIoU로 수렴**했다 [확인]. TurtleBot3로 실촬영 수백~1000장 확보가 가능하다면 이것이 렌더 개선보다 훨씬 싸고 확실하다.
5. **단, "전이 성능 ROI"와 "논문 설득력 ROI"는 다르다.** 리뷰어는 그림을 본다. 씬 04의 구 뭉치는 성능과 무관하게 논문을 죽일 수 있다. → **식생 에셋 교체만은 성능 논리를 떠나 조기 투자**할 것 [추정].

**한 줄 요약**: 백본 → 카메라/센서 파이프라인 → 배치·단서 상관 설계 → 조명/재질 랜덤화 → 실촬영 파인튜닝 → (그다음에) 에셋 사실성. 단 식생은 예외적으로 앞으로 당긴다.

---

## §2 포토리얼리즘 vs 도메인 랜덤화 — 근거와 현재 컨센서스

### 2.1 DR 진영의 원조 주장

| 논문 | 주장 / 결과 |
|---|---|
| Tobin et al., *Domain Randomization for Transferring Deep Neural Networks from Simulation to the Real World*, IROS 2017 ([arXiv:1703.06907](https://arxiv.org/abs/1703.06907)) | **비사실적** 렌더만으로 실물 물체 위치추정 **1.5 cm 오차**, 방해물·부분가림에 강건 [확인]. "시뮬레이터 변이가 충분히 크면 현실은 모델에게 또 하나의 변이일 뿐" |
| Sadeghi & Levine, *CAD²RL: Real Single-Image Flight without a Single Real Image*, RSS 2017 ([arXiv:1611.04201](https://arxiv.org/abs/1611.04201)) | 실제 이미지 **0장**으로 실내 드론 충돌회피 정책 전이 [확인] |
| Tremblay et al., *Training Deep Networks with Synthetic Data: Bridging the Reality Gap by Domain Randomization*, CVPRW 2018 ([arXiv:1804.06516](https://arxiv.org/abs/1804.06516)) | DR 합성만으로 KITTI 차량 검출 성립. **실데이터 파인튜닝 시 실데이터 단독보다 우수** [확인] |

**중요한 단서**: 위 세 편은 모두 **대상이 명확히 보이는 객체 검출/위치추정**이다. 대상이 화면에 있고, 태스크는 "그것이 어디 있는가"다. 우리 태스크는 **대상이 화면에 없고 주변 맥락에서 추론**하는 것이므로 이 결과를 그대로 이식할 수 없다 [해석].

### 2.2 반대 축 — 사실성이 실제로 점수를 만든다

| 논문 | 정량 결과 |
|---|---|
| Wrenninge & Unger, *Synscapes: A Photorealistic Synthetic Dataset for Street Scene Parsing*, 2018 ([arXiv:1810.08705](https://arxiv.org/abs/1810.08705)) | **합성단독 학습 → Cityscapes val (DeepLab v3+)**: Synscapes **50.35** / GTA-Richter **32.20** / SYNTHIA **32.73** mIoU [확인]. 자기검증 정확도 Synscapes 87% vs Richter 63% vs SYNTHIA 57%. 클래스별 표준편차 8.25 vs 17.51 vs 24.55 → **사실성 높을수록 클래스 간 성능 편차도 작다** [확인] |
| 〃 | 저자 결론: *"신경망이 도메인 시프트를 자연히 추상화한다는 징후는 없다. 정확한 센서 시뮬레이션을 지향하는 소프트웨어는 가능한 한 최고의 사실성을 달성해야 한다"* [확인] |
| Hodaň et al., *BOP Challenge 2020 on 6D Object Localization* ([arXiv:2009.07378](https://arxiv.org/abs/2009.07378)) | PBR(레이트레이싱) 학습 이미지가 OpenGL "render&paste" 대비 **평균 상대 +35.9%(v1) / +25.5%(v2)** [확인]. CosyPose 기준 T-LESS **6.1 → 64.0** AR(+57.9pt), YCB-V +30.9pt, TUD-L +19.0pt [확인] |
| Sundermeyer et al., *BOP Challenge 2022* (CVPRW 2023) | PBR 도입 이후 SOTA가 **56.9 AR(2019) → 69.8(2020) → 83.7(2022)** [확인] |

### 2.3 결정적 중간 지대 — 구조화된 랜덤화(SDR)

Prakash et al., *Structured Domain Randomization*, ICRA 2019 ([arXiv:1810.10093](https://arxiv.org/abs/1810.10093)) — **우리에게 가장 중요한 논문**.

KITTI 차량 검출 AP@0.7 (Table I, 7500장 평가) [확인]:

| 학습 데이터 | 크기 | Easy | Moderate | Hard |
|---|---|---|---|---|
| VKITTI clones | 2.2k | 49.6 | 44.8 | 33.6 |
| VKITTI | 21k | 70.3 | 53.6 | 39.9 |
| Sim 200k | 200k | 68.0 | 52.6 | 42.1 |
| **DR (무구조 랜덤 배치)** | 25k | 56.7 | 38.8 | 24.0 |
| **SDR (맥락 구조 + 랜덤화)** | 25k | **77.3** | **65.6** | **52.2** |

Table III (실데이터 비교, 1500장 평가) [확인]:

| 학습 데이터 | 종류 | 크기 | Easy | Mod | Hard |
|---|---|---|---|---|---|
| DR | 합성 | 25k | 56.8 | 38.0 | 23.9 |
| **SDR** | 합성 | 25k | **69.6** | **65.8** | **52.5** |
| BDD100K | **실제** | 70k | 59.7 | 54.3 | 45.6 |
| KITTI | 실제(동일도메인) | 6k | 85.1 | 88.3 | 88.8 |

**핵심 해석**: 동일 렌더 품질·동일 데이터량(25k)에서 **"배치를 현실 통계에 맞췄다"는 것만으로 Easy +20.6 / Mod +26.8 / Hard +28.2 AP**. 이는 이 조사에서 발견한 **단일 요인 중 가장 큰 효과 중 하나**이며, 픽셀 사실성 개선이 아니라 **씬 조립 스크립트 수정**으로 얻어진다 [확인 + 해석]. 그리고 SDR 합성 25k가 실제 BDD100K 70k를 **모든 난이도에서 능가**했다 [확인].

### 2.4 2026년 현재 컨센서스

- **양자택일이 아니다.** 표준 레시피는 **"물리 기반 사실적 렌더 + 구조화된(맥락 보존) 랜덤화 + 센서 효과 + 소량 실데이터"** 조합이다 [확인 — SDR, BOP2020/2022, Synscapes, 그리고 ACM TOMM 2024 서베이 *Synthetic Data for Object Detection with Neural Networks: SOTA Survey of Domain Randomisation Techniques* ([DOI 10.1145/3637064](https://dl.acm.org/doi/10.1145/3637064))].
- **다양성 > 포토리얼리즘 (동일 예산일 때).** Nowruzi et al., *How much real data do we actually need?* (2019) 결론: **포토리얼리즘보다 합성 데이터의 다양성이 더 중요**하며, **혼합 학습보다 "합성 사전학습 → 소량 실데이터 파인튜닝"이 우월** [확인].
- **사실성이 필요한 지점은 "태스크가 의존하는 채널"이다** [해석]. BOP(6D 포즈)는 재질·반사가 곧 신호라 PBR이 결정적이었다. 얼굴 파싱(Wood et al., *Fake It Till You Make It*, ICCV 2021, [arXiv:2109.15102](https://arxiv.org/abs/2109.15102))은 피부 SSS·헤어 등 고품질 에셋 + 라벨 정확도로 **도메인 적응 없이 실사 전이 성공** [확인]. 즉 "무엇을 사실적으로 만들 것인가"는 태스크가 정한다.

---

## §3 갭 요인별 기여도

효과 크기는 각 논문의 실험 설정에 종속되므로 **절대값이 아니라 상대 순위 참고용**이다 [해석].

| # | 요인 | 보고된 효과 크기 | 출처 | 우리 현황 | 개선 난이도 |
|---|---|---|---|---|---|
| 1 | **사전학습 백본(VFM)** | GTAV→CS/BDD/Mapillary 평균 mIoU: 종전 ResNet 기반 DG SOTA **45.9** → DINOv2 frozen **61.1~63.4** → +Rein **64.3~65.2**. **최대 +19.3pt** | Wei et al., *Stronger, Fewer, & Superior* (Rein), CVPR 2024 ([arXiv:2312.04265](https://arxiv.org/abs/2312.04265)) | 미정 (U-Net 계열 예정, 백본 미확정) | **낮음** (코드) |
| 2 | **장면 구성/배치 통계** | DR→SDR: Easy **+20.6**, Mod **+26.8**, Hard **+28.2** AP | Prakash et al., ICRA 2019 | 절차 조립이나 **배치 통계 근거 없음**, 등간격 반복 | **낮음~중** (스크립트) |
| 3 | **렌더 물리성 (PBR/PT vs OpenGL)** | 상대 **+25.5~35.9%** AR; CosyPose T-LESS +57.9pt | BOP Challenge 2020/2022 | **이미 PT 512spp** — 이 축은 충족 | 해당 없음 |
| 4 | **에셋/텍스처 사실성 전반** | Synscapes vs GTA5: **+18.15 mIoU** (합성단독) | Wrenninge & Unger 2018 | **GTA5보다 아래** (무텍스처 박스, 구 뭉치 식생) | **높음** (에셋/시간) |
| 5 | **센서·이미지 형성 시뮬레이션** | VKITTI 2975장 **+7.28 AP**, GTA 21k **+6.05 AP**. 개별: 색수차 +6.48 / 블러 +5.12 / 노이즈 +4.00 / 색편이 +3.99 / 노출 +2.77 | Carlson et al., *Modeling Camera Effects…*, ECCVW 2018 ([arXiv:1803.07721](https://arxiv.org/abs/1803.07721)) | **전무 (0건)** | **낮음** (후처리) |
| 6 | **씬 밀도/구성 복잡도** | dense vs sparse: **+4.75 mIoU** (Cityscapes, 인스턴스 22.2 vs 11.5/장) | *What Makes Synthetic Data Effective in Image Segmentation*, 2026 ([arXiv:2605.19289](https://arxiv.org/abs/2605.19289)) | **희박** (사람·차량·소품 0) | 중 |
| 7 | **국소 인스턴스 고주파 디테일** | fine vs coarse fidelity: **+1.61 mIoU** | 〃 | 없음 (베벨·변위 0) | 중~높음 |
| 8 | **라벨 정확도/일관성** | 합성 라벨의 완벽성이 실데이터 대비 우위 요인으로 지목 (얼굴 파싱 실사 전이 성공의 핵심) | Wood et al., ICCV 2021 | **GT 파이프라인 미착수** — 리스크 | 중 |
| 9 | **이미지레벨 도메인 적응** | GTA5→CS: **17.5 → 39.5 mIoU (+22)** | Hoffman et al., *CyCADA*, ICML 2018 ([arXiv:1711.03213](https://arxiv.org/abs/1711.03213)) | 없음 | 중~높음 |
| 10 | **소량 실데이터 파인튜닝** | Synscapes/GTA/SYNTHIA 합성단독 50.4/32.2/32.7 → **파인튜닝 후 전부 77~79 mIoU로 수렴** | Wrenninge & Unger 2018 | 미착수 (TurtleBot3 보유) | 중 (촬영+라벨링) |
| 11 | **백본 동결 트릭** | OpenGL 합성만으로 학습해도 특징추출기 동결 시 **실데이터 학습 대비 95% 성능** | Hinterstoisser et al., ECCVW 2018 ([arXiv:1710.10710](https://arxiv.org/abs/1710.10710)) | 미적용 | **최저** |

### 3.1 표에서 읽어야 할 것

- **우리가 이미 잘하는 것**: 렌더 물리성(#3). PT 512spp/8bounce는 BOP가 말하는 PBR 조건을 충족한다. **여기에 더 투자해도 한계효용이 거의 없다** [해석].
- **우리가 통째로 빠뜨린 것 중 싼 것**: #1 백본, #5 센서, #11 동결. 이 셋의 합산 기대효과가 #4(에셋 사실성) 하나보다 크고, 비용은 1/10 이하다 [해석].
- **우리가 통째로 빠뜨린 것 중 비싼 것**: #4 에셋, #6 밀도. 이건 시간이 든다.
- **가장 과소평가되고 있는 것**: #2 배치 통계. 우리는 21씬을 "타당성"으로 검증했지 "실제 한국 도시 공간의 통계"로 검증하지 않았다 [추정].

---

## §4 센서·이미지 형성 시뮬레이션 — 우리가 통째로 빠뜨린 부분

### 4.1 문헌이 말하는 것

Carlson et al. (ECCVW 2018)의 결과는 이 조사에서 가장 실행 가능성 대비 효과가 큰 항목이다 [해석].

**Table 1 (합성단독 → KITTI 차량 AP)** [확인]:

| 소스 | 규모 | 베이스라인 | +센서효과 | 증분 |
|---|---|---|---|---|
| VKITTI | 2975 | 54.60 | 61.88 | **+7.28** |
| VKITTI | 21k | 58.25 | 62.52 | **+4.27** |
| GTA | 2975 | 46.83 | 51.24 | **+4.41** |
| GTA | 21k | 49.80 | 55.85 | **+6.05** |

**Table 2 (일반 증강과의 비교, 이것이 결정적)** [확인]:

| 방법 | VKITTI 증분 | GTA 증분 |
|---|---|---|
| **물리 기반 센서 효과 (제안)** | **+4.27** | **+6.05** |
| PCA color shift | +0.84 | +1.88 |
| Gaussian noise (단순) | **−1.27** | +2.21 |
| Elastic deformation | **−1.69** | +0.14 |
| Spatial transforms | **−3.14** | +0.31 |

→ **"아무 노이즈나 넣기"는 오히려 해롭다. 물리적으로 올바른 이미지 형성 모델이어야 이득이 난다** [확인]. 이 구분은 우리 구현 설계에 직결된다.

Synscapes도 같은 결론을 지지한다: 저자들은 렌더 자체 외에 **광학 산란을 긴 꼬리 PSF로 모델링하고, 리드아웃 노이즈·카메라 응답함수(CRF)·색 특성까지 시뮬레이션**했다 [확인]. 즉 "포토리얼 데이터셋"의 성능 우위에는 **렌더 사실성뿐 아니라 센서 사실성이 섞여 있다** — 이 둘은 Synscapes 논문에서 분리 측정되지 않았다 [확인: 저자도 분리하지 않았음을 명시].

### 4.2 우리 상황 진단

현재 파이프라인 출력(`pt_noon_trail_approach.png`, `pt_noon_levee_walk.png` 직접 확인):

- **OptiX denoiser + DLSS Quality + 512spp** → 픽셀 노이즈 사실상 0. 실사 대비 **비현실적으로 깨끗**.
- **비네팅 없음, 색수차 없음, 렌즈 왜곡 없음, 블룸 없음, DoF 없음, 모션블러 없음**.
- **노출/AWB 없음** → 하늘 그라디언트가 클리핑 없이 완벽. 실제 카메라는 정오 순광에서 하늘이 날아가거나 지면이 뭉개진다.
- **PNG 무손실** → 실제 TurtleBot3 Waffle Pi(Raspberry Pi Camera) 스트림은 **JPEG 압축 아티팩트 + 롤링셔터 + 자동노출 헌팅 + 낮은 다이내믹 레인지**를 갖는다.

### 4.3 예상 영향 [해석 + 추정]

- **[해석]** Carlson의 효과 크기(+4~7 AP)는 이미 GTA/VKITTI 수준의 사실적 렌더를 전제로 측정된 값이다. 우리처럼 **렌더가 더 깨끗하고 더 단순한** 경우, 센서 효과 부재의 상대적 타격은 **동등하거나 더 클 가능성**이 높다.
- **[추정]** 우리 렌더의 "무결점성"은 그 자체가 **도메인 식별자**로 작동한다. 노이즈 없는 평탄 영역, 완벽한 안티에일리어싱 경계, 클리핑 없는 하늘은 실사에 존재하지 않는 통계다. 낮은 레벨 특징 분포가 통째로 이동하면, 우리가 학습시키려는 고수준 단서가 아무리 옳아도 첫 몇 개 conv 층에서 분포 시프트가 발생한다.
- **[해석]** 특히 우리 태스크의 단서 ②(텍스처 절단·도로끝-하늘 접합)는 **에지 통계에 직접 의존**한다. 렌더의 에지는 픽셀 완벽한 반면 실사 에지는 블러 + 색수차 + JPEG 링잉을 갖는다. 이 축의 갭은 우리 태스크에 **선택적으로 치명적**이다.

### 4.4 최소 구현 권고 [추정 — 문헌 기반 설계이나 우리 환경 검증 전]

렌더 후처리 체인(Python/OpenCV 또는 Blender compositor로 오프라인 배치 처리):
1. 선형 HDR 유지 → **노출 랜덤화(±1.5 EV) → 색온도 랜덤화(4500–8000K)** → 톤매핑/CRF
2. **렌즈**: 비네팅(cos⁴ 근사), 반경별 색수차(0.3–1.5 px), 배럴 왜곡 소량
3. **광학 블러**: 이미지 중심/주변 다른 PSF, σ 0.3–1.2 px
4. **센서**: 포아송(샷) 노이즈 + 가우시안 리드아웃 노이즈를 **선형 도메인에서** 주입 (톤매핑 이후가 아님 — 이 순서가 Carlson의 "물리 기반"의 핵심)
5. **ISP**: 디모자이킹 잔여 아티팩트, 샤프닝 오버슛
6. **JPEG q=70–95 랜덤 인코딩/디코딩**
7. (동적 개체 도입 시) 모션블러

> 순서가 중요하다. 톤매핑 후에 가우시안 노이즈를 뿌리는 방식이 Carlson Table 2에서 **−1.27**을 기록한 그 방식이다 [확인 + 해석].

---

## §5 저비용 갭 축소 기법 비교

| 기법 | 보고된 효과 | 우리 비용 | 구현 리스크 | 판정 |
|---|---|---|---|---|
| **VFM 백본(DINOv2/DINOv3) + PEFT 어댑터(Rein류)** | 평균 mIoU 45.9 → 64.3~65.2 (합성단독 DG) [확인, CVPR24] | 낮음 (사전학습 가중치 다운로드 + 어댑터) | 낮음. VRAM 24GB에 ViT-L 학습 가능. 단 U-Net 아키텍처를 ViT+디코더로 바꿔야 함 | **1순위** |
| **백본 동결 / 부분동결** | 합성만으로 실데이터 대비 95% [확인, ECCVW18] | 최저 | 최저 | **1순위 (병행)** |
| **물리 기반 센서효과 증강** | +4.27~7.28 AP [확인] | 낮음 (후처리 스크립트 1~2일) | 낮음. 단 "순서" 틀리면 역효과 [확인] | **2순위** |
| **카메라 파라미터 연속 랜덤화** (높이/피치/롤/FOV/내부파라미터) | 직접 효과크기 논문 없음. 단 단안 깊이망이 피치 변화에 취약함이 확인됨 [확인, van Dijk 2019] | 최저 (씬 스크립트) | 최저 | **2순위** |
| **구조화 도메인 랜덤화 (배치 통계)** | +20.6~28.2 AP [확인, ICRA19] | 중 (스크립트 재설계) | 중. 통계 근거를 어디서 얻을지가 문제 | **3순위** |
| **조명/재질 랜덤화** | SDR 어블레이션에서 saturation 제거가 최대 하락, 이어서 context·scene randomization [확인, 수치는 막대그래프만 제공] | 중 (HDRI 수집 + MDL 파라미터 랜덤화) | 낮음 | **3순위** |
| **스타일 전이 / 텍스처 디바이어싱 증강** (Stylized-ImageNet류) | Faster R-CNN VOC07 70.7 → 75.1 mAP50 [확인, Geirhos et al. ICLR 2019, [arXiv:1811.12231](https://arxiv.org/abs/1811.12231)]. DG 세그멘테이션 whitening/style 계열 **+2.5~7.2 mIoU** [확인, RobustNet CVPR21 계열] | 낮음~중 | 낮음. AdaIN 스타일 증강은 CPU/GPU 부담 적음 | **3순위** |
| **소량 실데이터 파인튜닝** | 합성단독 격차(18.2 mIoU)가 파인튜닝 후 **거의 소멸** [확인, Synscapes]. 혼합학습보다 파인튜닝 우월 [확인, Nowruzi 2019] | 중 (TurtleBot 촬영 + 낙차 라벨링) | 중. **낙차량 GT를 실환경에서 어떻게 얻을지가 병목** (줄자/LiDAR/포토그래메트리) | **4순위 — 단 논문 완성도상 사실상 필수** |
| **GAN 이미지 변환 (CyCADA/MUNIT/CUT)** | GTA5→CS 17.5 → 39.5 mIoU [확인] | 높음 (타깃 실사 데이터셋 필요 + 학습) | **높음**. 라벨-픽셀 정합 붕괴, 구조 hallucination. 우리 태스크는 기하 단서 기반이라 특히 위험 | 보류 |
| **Diffusion 기반 sim→real 리터칭** | 2026 하이브리드(FLUX+REGEN): CMMD 3.734 → **1.781**, VKITTI2 mIoU 52.18 → **55.94** [확인, [arXiv:2605.02291](https://arxiv.org/abs/2605.02291)]. Cosmos-Transfer 2.5는 Transfer1 대비 3.5× 작고 더 높은 충실도 [확인, NVIDIA] | 높음 (모델 가중치 + 추론 시간, GPU 1대) | **높음**. 기하 일관성 보장이 조건입력(depth/seg) 품질에 의존. 우리는 GT 파이프라인이 아직 없음 | **보류 — GT 맵 완성 후 재검토** |
| **Photorealism Enhancement (Richter 2021 계열)** | GTA V → Cityscapes 스타일 실시간 향상 [확인, [프로젝트](https://isl-org.github.io/PhotorealismEnhancement/)]. G-buffer 조건부라 구조 보존이 GAN보다 낫다 | 높음 | 중~높음 | 보류 |

### 5.1 발견 중 가장 반직관적인 것

- **2026년 하이브리드 리터칭 논문의 결론**: *"기하 변형보다 실세계 데이터 분포를 맞추는 것이 더 결정적이었다"* — REGEN(분포 정합) 단독이 FLUX(강한 기하/재질 변형) 단독보다 우수 [확인, arXiv:2605.02291]. 이는 §3 표의 #2(배치 통계) 우선 논리와 같은 방향이다 [해석].
- **일반 증강은 만능이 아니다.** Carlson Table 2에서 공간 변형 증강은 **−3.14 AP** [확인]. sim2real에서는 "무엇을 랜덤화하느냐"가 "얼마나 랜덤화하느냐"보다 중요하다 [해석].

---

## §6 우리 태스크 특이성 — 고수준 단서 의존은 충실도 요구를 낮추는가?

### 6.1 두 가설의 대립

**가설 A (낙관)**: 우리 모델은 난간·수관·텍스처 절단선 같은 고수준 의미/기하 단서에 의존하므로, 저수준 픽셀 사실성 요구가 완화된다.

**가설 B (비관)**: 저수준 사실성이 부족하면 모델이 **sim 특유의 지름길**을 학습해, 고수준 단서를 애초에 배우지 않는다.

**문헌은 가설 B를 강하게 지지한다.** 가설 A를 직접 지지하는 논문은 이 조사에서 발견되지 않았다 [확인: 부재].

### 6.2 가설 B의 근거

| 근거 | 내용 |
|---|---|
| **van Dijk & de Croon, *How Do Neural Networks See Depth in Single Images?*, ICCV 2019** ([arXiv:1905.07005](https://arxiv.org/abs/1905.07005)) | 모든 단안 깊이망이 **알려진 장애물의 겉보기 크기를 무시하고 이미지 내 수직 위치를 사용** [확인]. 수직 위치만 있으면 거리 추정 분산이 커지고, **겉보기 크기만 있으면 어떤 망도 거리를 추정하지 못함** [확인]. 또한 **카메라 피치/롤 변화를 부분적으로만 보정**하며 작은 피치 변화가 거리 추정을 교란 [확인]. MonoDepth가 미학습 장애물에 일반화하려면 **지면 접촉점의 강한 에지가 필요** [확인] |
| **Islam et al., *How Much Position Information Do CNNs Encode?*, ICLR 2020** ([OpenReview](https://openreview.net/forum?id=rJeB36NKvB)) | **제로 패딩이 CNN에 절대 위치 정보를 인코딩**시킨다. 패딩이 없으면 위치 인코딩도 사라짐 [확인]. → U-Net처럼 패딩 conv를 다층으로 쌓는 구조는 **픽셀의 절대 y좌표를 특징으로 쓸 수 있다** [해석] |
| **Xiao et al., *Noise or Signal: The Role of Image Backgrounds*, ICLR 2021** ([arXiv:2006.09994](https://arxiv.org/abs/2006.09994)) | 배경만으로 학습한 모델이 **원본 테스트셋에서 40~50% 정확도** (랜덤 11%) [확인]. 적대적으로 고른 배경을 붙이면 **전경이 정확히 보여도 최대 87.5% 오분류** [확인] |
| **2026, *Early Cue Precision Shapes Visual Shortcut Learning*** ([arXiv:2606.30344](https://arxiv.org/abs/2606.30344)) | 단서-라벨 상관 p를 조작: **p=0.10일 때 conflict accuracy 0.569 → p=1.0일 때 0.114**, 텍스처 선택률 0.049 → **0.855** [확인]. 저자 결론: *"완벽히 상관된 합성 단서는 과도한 초기 예측 신뢰도를 만들어 지름길 학습을 사실상 불가피하게 한다"*, *"단서 탈상관이 아키텍처 선택이나 입력 열화보다 중요하다"* [확인] |
| **Geirhos et al., ICLR 2019 / Nature MI 2020** ([arXiv:1811.12231](https://arxiv.org/abs/1811.12231), [Nature MI](https://www.nature.com/articles/s42256-020-00257-z)) | ImageNet CNN의 텍스처 편향, 그리고 이를 일반화한 shortcut learning 프레임 [확인] |
| **(반론, 균형을 위해) Burgert et al., *ImageNet-trained CNNs are not biased towards texture*, NeurIPS 2025 (Oral)** ([arXiv:2509.20234](https://arxiv.org/abs/2509.20234)) | 통제된 억제 실험에서 CNN은 본질적으로 텍스처 편향이 아니라 **국소 형상(local shape)에 주로 의존**하며, ConvNeXt/ViT 및 현대 학습 전략으로 완화 가능 [확인] |

**두 진영을 종합한 실무 결론** [해석]: "텍스처냐 형상이냐" 논쟁의 승패와 무관하게, **양쪽 모두 "라벨과 완벽히 상관된 가장 단순한 단서를 네트워크가 채택한다"는 점에는 동의**한다. 우리 파이프라인은 절차적 스크립트이므로 **단서-라벨 상관을 우리가 직접 결정**하며, 기본값은 p=1.0(결정론적)이다. 이것이 우리의 최대 리스크다.

### 6.3 사전학습 백본의 완화 효과 [확인]

- Rein/DINOv2: 합성단독 학습 DG에서 종전 SOTA **45.9 → 64.3~65.2 mIoU** 평균 [확인]. DINOv2 frozen 자체가 61.1, 전체 파인튜닝 61.7, +Rein 64.3 → **동결이 전체 파인튜닝과 거의 같다** [확인]. 즉 **백본을 건드리지 않는 것이 sim2real에서 유리**하다.
- UrbanSyn+GTAV+SYNTHIA 합성만으로 Cityscapes **78.4 mIoU** 달성 [확인] — 실도시 데이터 무접근.
- Hinterstoisser et al. 2018: 특징추출기를 실사 사전학습 가중치로 **동결**하면 OpenGL 렌더만으로도 실데이터 학습의 **95%** [확인].

**해석**: 사전학습 백본은 저수준 도메인 시프트를 흡수하는 필터로 작동한다. 우리처럼 저수준 사실성이 낮은 렌더에서는 **완화 효과가 특히 클 것**이며, 반대로 **scratch U-Net은 우리 렌더의 인공적 저수준 통계를 그대로 학습**하게 된다 [해석 + 추정].

### 6.4 우리 씬이 유발할 지름길 목록 — 구체 예측

`scene04/pt_noon_trail_approach.png`, `scene03/pt_noon_levee_walk.png`를 직접 확인한 뒤 작성. 심각도는 [추정], 근거는 각 항목에 표기.

| # | 지름길 | 왜 학습되는가 | 실사에서 왜 깨지는가 | 심각도 |
|---|---|---|---|---|
| **S1** | **이미지 y좌표 / 고정 지평선** | 카메라 높이가 h∈{0.3, 0.9, 1.8}, 거리 d∈{2, 5, 10}의 **9개 이산 조합뿐**. 지평선 y가 씬 전반에 걸쳐 몇 개 값으로 고정. CNN은 제로패딩으로 절대 위치를 인코딩 [Islam 2020]. 단안 깊이망은 이미 수직 위치를 주 단서로 씀 [van Dijk 2019] | 실주행 카메라는 피치가 연속적으로 흔들림. 로봇 서스펜션·경사로·기울어진 지면 | **최상** |
| **S2** | **단색 시안 수면** | scene03에서 물이 채도 높은 단일 청록 + 거의 거울 반사. "이 RGB = 낙차"가 가장 단순한 규칙 | 실제 하천은 탁류 갈색/녹조/파문/부유물/주변 반사. 색으로는 식별 불가 | **최상** |
| **S3** | **재질 팔레트 ↔ 클래스 1:1** | `make_pbr()` 상수 틴트 + 소수의 4K 타일 텍스처. 클래스마다 고유 텍스처 ID가 사실상 부여됨. p≈1.0 상관 [arXiv:2606.30344] | 실세계는 같은 클래스 안에서도 재질 분산이 큼(아스팔트/보도블록/우레탄/석재 등) | **최상** |
| **S4** | **픽셀 완벽 직선 절단선** | 지면이 Cube 슬래브라 낙차 경계가 안티에일리어싱만 있는 완벽한 직선/직각. "완벽한 직선 = 낙차" | 실제 연석·도랑·제방 가장자리는 부서짐·풀 침범·흙 퇴적·그림자 산란·불규칙 | **상** |
| **S5** | **구 뭉치 수관 실루엣** | 나무 = 눌린 구 3개. 단서 ③(수관 높이 앵커)을 배우게 하려 했는데 실제로는 **"구 실루엣의 화면 내 크기·y위치"**만 학습 | 실제 수관은 프랙탈 실루엣 + 반투과 + 가지 구조. 매칭되는 특징이 없음 | **상** — 단서 ③의 전이 실패 직결 |
| **S6** | **설비-낙차 결정론적 상관** | 절차 스크립트가 "낙차가 있는 곳에 난간/볼라드를 놓는" 방식이면 p=1.0. Early cue precision 논문이 예측하는 최악 조건 [확인] | 실세계에는 **난간 없는 낙차**(공사구간, 시골 제방, 폐쇄 계단)와 **낙차 없는 난간**(화단 경계, 주차 방지, 자전거 거치)이 흔함 | **상** — batch1 hard-negative 12씬이 있으나 **비율 설계 근거 없음** |
| **S7** | **렌더 청결도 = 도메인 지문** | 512spp + OptiX denoiser + DLSS → 노이즈 0, 무손실 PNG. 저수준 통계 자체가 sim 식별자 | Pi Camera 스트림은 노이즈 + JPEG + 롤링셔터 + AE 헌팅 | **상** (§4 참조) |
| **S8** | **정오 맑음 단일 조건 · 태양 방위 고정** | 본편 21씬 전부 동일 HDRI + 동일 태양각. 그림자 방향이 상수 → 단서 ④(암부·그림자)가 **정보가 아니라 상수**가 되거나, 특정 명암 패턴에 과적합 | 실촬영은 시간·계절·구름·역광이 변함. 그림자 방향 변화만으로 예측 붕괴 가능 | **상** |
| **S9** | **완전 평탄 지면** | 미세 기복/침하/균열 지오메트리 0. "평탄이 갑자기 끊김"만이 유일한 기하 패턴 | 실제 지면은 항상 미세 그라디언트·요철·물고임. 절단선이 그라디언트에 묻힘 | **중~상** |
| **S10** | **하늘 픽셀 통계 상수** | 단일 HDRI 파생. 단서 ②(도로끝-하늘 접합)를 학습할 때 **하늘의 색/그라디언트 자체가 앵커**가 됨 | 흐린 날/역광/도심 스모그에서 하늘 통계 완전 변화 | **중** |
| **S11** | **등간격 반복 배치** | 헤지가 같은 구 반복, 가로수 등간격. 배치 주기성이 클래스와 상관 | 실세계 배치는 불규칙 | **중** |
| **S12** | **창문 = 파란 사각형 격자** | scene03 건물이 무텍스처 회색 박스 + 균일 파란 사각형. 강한 규칙 주파수가 "건물" 신호로 고착 | 실제 건물은 창틀·반사·에어컨 실외기·발코니·간판 | **중** |
| **S13** | **동적 개체 부재** | 사람·차량 0 → 단서 ③의 "사람 상반신·차 지붕이 눈높이 이하" 앵커를 **학습할 데이터가 아예 없음** | 실환경에는 항상 있음. 이 단서는 전이 이전에 **학습조차 안 됨** | **상** — 논문 주장(단서 4계열) 자체의 결함 |

**S13은 성능 문제가 아니라 논문 주장의 무결성 문제다** [해석]. 맥락 단서 4계열 중 ③(스케일 앵커)이 사람·차량을 명시하는데, 학습 데이터에 사람·차량이 0건이면 그 주장은 데이터로 뒷받침되지 않는다.

### 6.5 지름길 방어 설계 원칙 [추정 — 문헌 기반 도출]

1. **모든 단서를 확률적으로 만들 것.** 낙차 ↔ 난간 상관을 p≈0.6~0.8로 낮추고, "난간 있는 비낙차"와 "난간 없는 낙차"를 명시적 비율로 삽입한다 [근거: arXiv:2606.30344, p=1.0에서 지름길 채택률 0.855].
2. **카메라 파라미터를 이산 프리셋이 아닌 연속 분포에서 샘플링.** 높이 U(0.25, 1.9), 피치 N(0, 4°), 롤 N(0, 1.5°), FOV·주점도 소량 변동 [근거: van Dijk 2019의 피치 취약성].
3. **동일 씬을 다른 조건으로 다중 렌더.** 같은 기하 + 다른 조명/재질/센서 → 모델이 기하·배치에 의존하도록 강제 [근거: SDR + 스타일 디바이어싱].
4. **저수준 단서를 의도적으로 파괴하는 증강.** AdaIN 스타일 증강, 채널 셔플, 색 상수성 파괴 [근거: Geirhos 2019 +4.4 mAP50, DG whitening +2.5~7.2 mIoU].
5. **진단 실험을 데이터 생성과 동시에 설계.** ① 하늘 마스킹, ② 상단/하단 반쪽 마스킹, ③ 그레이스케일, ④ 색 셔플, ⑤ 카메라 피치 ±5° 교란 — 각각에서 성능이 무너지면 해당 지름길을 쓰고 있다는 증거 [근거: Xiao et al. 2021 배경 챌린지 방법론].

---

## §7 우선순위 매긴 실행 함의 (ROI 순)

비용 단위: **S**=1일 이하, **M**=2~5일, **L**=1~3주, **XL**=1개월+

| 순위 | 작업 | 예상 효과 | 근거 | 비용 | 선행조건 | 리스크 |
|---|---|---|---|---|---|---|
| **1** | **백본을 DINOv2(또는 DINOv3) + 경량 어댑터로 전환하고 동결 학습**. U-Net 디코더는 유지 가능(ViT 인코더 + UNet-style 디코더) | **최대**. 합성단독 DG에서 45.9 → 64.3 mIoU 급 | Wei et al. CVPR 2024 (Rein) [확인]; Hinterstoisser ECCVW 2018 동결 95% [확인] | **M** | 없음 (지금 결정 가능) | 아키텍처 변경이 U-Net 서사와 충돌 → "U-Net 계열 디코더" 프레이밍으로 해소 |
| **2** | **카메라 파라미터 연속 랜덤화** (높이/피치/롤/FOV/주점). 이산 9프리셋 폐기 | **큼**. S1(최상위 지름길) 직접 차단 | van Dijk & de Croon ICCV 2019 [확인] | **S** | 씬 스크립트 접근 | 없음. 즉시 가능 |
| **3** | **물리 기반 센서/ISP 후처리 체인 구축** (선형 노이즈 → 렌즈 → 노출/AWB → 톤맵 → JPEG) | **큼**. +4.3~7.3 AP 급 | Carlson et al. ECCVW 2018 [확인]; Synscapes의 PSF/CRF/리드아웃 노이즈 [확인] | **M** | 렌더가 선형 HDR(EXR)로 저장되어야 최적. PNG만 있어도 근사 가능 | **순서를 틀리면 역효과(−1.27~−3.14 AP)** [확인] |
| **4** | **단서-라벨 상관 설계** — 난간/볼라드/점자블록 ↔ 낙차 상관을 p<1로 낮추고 hard-negative 비율을 문서화된 근거로 확정 | **큼**. 논문 주장의 방어선이자 지름길 차단 | arXiv:2606.30344 (p=1.0 → 지름길률 0.855) [확인] | **M** | batch1 12씬 재검토 | 비율 근거를 어디서? → 한국 시설기준 + 실측 조사 필요 |
| **5** | **조명 조건 랜덤화** — HDRI 8~12종(정오/아침/저녁/흐림/역광/반그늘) × 태양 방위 랜덤 | **중~큼**. S8/S10 차단. SDR 어블레이션에서 saturation·scene randomization이 상위 기여 | Prakash ICRA 2019 [확인, 막대그래프]; Synscapes 조건 탈상관 [확인] | **M** (렌더 시간이 병목) | PolyHaven CC0 HDRI 수집 | GPU 1대 → 렌더 시간 N배. **PT 대신 RaytracedLighting으로 조건 변주분을 채우는 하이브리드 검토** |
| **6** | **재질/텍스처 랜덤화** — 틴트·러프니스·타일 스케일·UV 회전·텍스처 풀 확대(클래스당 5~10종) | **중~큼**. S3(클래스↔텍스처 1:1) 직접 차단 | Geirhos ICLR 2019 [확인]; DG whitening +2.5~7.2 mIoU [확인] | **M** | ambientCG/PolyHaven CC0 확장 | 낮음 |
| **7** | **식생 에셋 교체 (구 뭉치 → 실제 메시)** — 단서 ③ 수관 앵커의 전이 가능성 확보 | **중**. 성능 기여는 #1~6보다 작을 것 [추정]. 다만 **단서 ③ 자체의 성립 조건**이자 리뷰어 설득의 핵심 | Synscapes +18.2 mIoU(사실성 전반) [확인]; S5 예측 [추정] | **L** | CC0 식생 에셋 조사(별도 보고서 A/C 참조) | 폴리곤 수 → PT 렌더 시간 증가 |
| **8** | **동적 개체 도입 (사람·차량)** — 단서 ③의 학습 데이터 자체를 생성 | **중**. 씬 밀도 dense화 효과 +4.75 mIoU [확인]. 단서 ③ 주장 무결성 확보 | arXiv:2605.19289 [확인]; S13 [해석] | **L** | 사람/차량 CC0 에셋 + 배치 규칙 | 라이선스 확인 필요 |
| **9** | **소량 실데이터 파인튜닝 루프** — TurtleBot3로 캠퍼스/공원/제방 300~1000장 촬영 + 낙차 라벨 | **큼 (최종 단계에서)**. 사실성 격차 대부분 소멸 (50.4/32.2 → 77~79 수렴) | Wrenninge & Unger 2018 [확인]; Nowruzi 2019 (파인튜닝 > 혼합) [확인] | **L~XL** | **낙차량 GT 취득 방법 확정이 병목** (줄자/RTK/포토그래메트리) | 라벨 비용. 하지만 **논문 성립에는 사실상 필수** |
| **10** | **씬 구성 통계 근거화 (SDR화)** — 21씬 배치를 "타당성"이 아니라 실측 통계(폭·간격·수종·설비 밀도)로 재조정 | **큼 (문헌상)**. +20.6~28.2 AP | Prakash ICRA 2019 [확인] | **L** | 한국 보행공간 실측/도로설계기준 조사 | 조사 비용. **순위는 낮지만 효과 크기는 최상위** — 자원 여유 시 상향 |
| **11** | **지오메트리 디테일 (베벨/변위/데칼/소품 엔트로피)** | **중~소**. 고주파 fidelity +1.61 mIoU [확인] | arXiv:2605.19289 [확인] | **L~XL** | — | 비용 대비 효과 최저 |
| **12** | **Diffusion 리터칭 / GAN 변환** | **중**. mIoU 52.18 → 55.94 [확인] | arXiv:2605.02291 [확인]; Cosmos-Transfer2.5 [확인] | **XL** | **GT 낙차 맵 파이프라인 완성 후** (조건입력으로 depth/seg 필요) | 기하 hallucination이 우리 태스크를 직접 파괴 |

### 7.1 순위에 대한 방어 논리

- **왜 #1이 백본인가**: 이 조사에서 확인한 모든 효과 크기 중 **단일 개입으로 +19.3 mIoU는 최대치**이고, 비용은 며칠이다. 게다가 사전학습 백본은 §6.4의 **S3/S7/S12(저수준 통계 지름길)를 일괄 완화**한다 [해석].
- **왜 사실성(#7, #11)이 뒤인가**: 사실성 개선의 문헌상 근거(+18.2 mIoU, Synscapes)는 **PBR 렌더 여부**와 **에셋 품질**이 뭉쳐진 값이며, 우리는 PBR 축(#3, BOP 기준)은 이미 충족하고 있다 [해석]. 그리고 같은 논문이 **파인튜닝 후 격차 소멸**을 보고했다 [확인] — 즉 사실성 투자는 "실데이터가 전혀 없을 때만" 최고 ROI다.
- **왜 그래도 식생(#7)은 8~11보다 앞인가**: 단서 ③(수관 높이 앵커)이 논문의 4대 단서 중 하나이고, 구 뭉치로는 그 단서가 **물리적으로 성립하지 않는다** [해석]. 성능 ROI가 아니라 **주장의 성립 조건**이기 때문이다. 여기에 사용자 지적("게임 같다")이 정확히 겨냥한 지점이기도 하다.
- **#10을 낮게 둔 이유**: 효과 크기는 최상위(+28 AP)지만, 우리에게는 **"실제 통계"를 제공할 데이터 소스가 없다**. 이것이 확보되면 즉시 #4~5 수준으로 올려야 한다 [추정].

### 7.2 즉시 착수 권고 (이번 주)

1. **[S]** 카메라 파라미터 이산 프리셋 → 연속 샘플링 전환 (S1 차단)
2. **[S]** 렌더 출력을 선형 EXR로도 저장하도록 캡처 경로 수정 (센서 체인의 전제조건)
3. **[M]** 센서/ISP 후처리 스크립트 프로토타입 + 육안 A/B
4. **[M]** 백본 전환 실험 설계 (DINOv2-B frozen + 경량 디코더 vs scratch U-Net) — GT 맵이 없으므로 **더미 라벨로 파이프라인만 먼저 뚫어두기**

### 7.3 반드시 함께 만들어야 할 것 — 지름길 진단 프로토콜

성능 숫자만으로는 §6.4의 지름길을 발견할 수 없다 [해석]. GT 파이프라인 착수와 **동시에** 아래 평가 세트를 설계할 것:

- **A. 마스킹 어블레이션**: 하늘 제거 / 상단 40% 제거 / 하단 40% 제거 → 성능 하락 패턴
- **B. 색 파괴**: 그레이스케일 / 채널 셔플 / 색상 회전 → S2·S3 검출
- **C. 카메라 교란**: 피치 ±5°, 롤 ±3°, 크롭-리사이즈 → S1 검출
- **D. 단서 충돌 세트**: 난간 있는 비낙차 / 난간 없는 낙차 실사 컷 → S6 검출
- **E. 센서 열화**: JPEG q=50, 가우시안 노이즈, 모션블러 → S7 검출

이 다섯 개는 **논문의 분석 섹션 그 자체**가 되며, "우리는 맥락을 쓴다"는 주장을 입증하는 유일한 방법이다 [추정].

---

## 부록: 인용 목록

**포토리얼 vs DR**
- Tobin et al., *Domain Randomization for Transferring Deep Neural Networks from Simulation to the Real World*, IROS 2017 — https://arxiv.org/abs/1703.06907
- Sadeghi & Levine, *CAD²RL: Real Single-Image Flight without a Single Real Image*, RSS 2017 — https://arxiv.org/abs/1611.04201
- Tremblay et al., *Training Deep Networks with Synthetic Data: Bridging the Reality Gap by Domain Randomization*, CVPRW 2018 — https://arxiv.org/abs/1804.06516
- Prakash et al., *Structured Domain Randomization: Bridging the Reality Gap by Context-Aware Synthetic Data*, ICRA 2019 — https://arxiv.org/abs/1810.10093
- Wrenninge & Unger, *Synscapes: A Photorealistic Synthetic Dataset for Street Scene Parsing*, 2018 — https://arxiv.org/abs/1810.08705
- Hodaň et al., *BOP Challenge 2020 on 6D Object Localization*, ECCV 2020 — https://arxiv.org/abs/2009.07378
- Sundermeyer et al., *BOP Challenge 2022*, CVPRW 2023 — https://arxiv.org/abs/2302.13075
- Nowruzi et al., *How much real data do we actually need?*, 2019 — https://www.researchgate.net/publication/334506917
- *Synthetic Data for Object Detection with Neural Networks: SOTA Survey of Domain Randomisation Techniques*, ACM TOMM 2024 — https://dl.acm.org/doi/10.1145/3637064
- Wood et al., *Fake It Till You Make It: Face Analysis in the Wild Using Synthetic Data Alone*, ICCV 2021 — https://arxiv.org/abs/2109.15102

**센서/이미지 형성**
- Carlson et al., *Modeling Camera Effects to Improve Visual Learning from Synthetic Data*, ECCVW 2018 — https://arxiv.org/abs/1803.07721
- Carlson et al., *Sensor Transfer: Learning Optimal Sensor Effect Image Augmentation for Sim-to-Real Domain Adaptation*, RA-L 2019 — https://arxiv.org/abs/1809.06256
- Berlier et al., *Augmenting Simulation Data with Sensor Effects for Improved Domain Transfer*, ECCVW 2022 — https://link.springer.com/chapter/10.1007/978-3-031-25075-0_52

**갭 축소 기법**
- Hoffman et al., *CyCADA: Cycle-Consistent Adversarial Domain Adaptation*, ICML 2018 — https://arxiv.org/abs/1711.03213
- Hinterstoisser et al., *On Pre-Trained Image Features and Synthetic Images for Deep Learning*, ECCVW 2018 — https://arxiv.org/abs/1710.10710
- Wei et al., *Stronger, Fewer, & Superior: Harnessing Vision Foundation Models for Domain Generalized Semantic Segmentation* (Rein), CVPR 2024 — https://arxiv.org/abs/2312.04265
- Choi et al., *RobustNet: Improving Domain Generalization in Urban-Scene Segmentation via Instance Selective Whitening*, CVPR 2021 — https://openaccess.thecvf.com/content/CVPR2021/papers/Choi_RobustNet_...pdf
- Jia et al., *DGInStyle: Domain-Generalizable Semantic Segmentation with Image Diffusion Models*, ECCV 2024 — https://arxiv.org/abs/2312.03048
- Richter et al., *Enhancing Photorealism Enhancement*, 2021 — https://isl-org.github.io/PhotorealismEnhancement/
- *A Hybrid Approach for Closing the Sim2real Appearance Gap in Game Engine Synthetic Datasets*, 2026 — https://arxiv.org/abs/2605.02291
- NVIDIA, *Cosmos-Transfer1: Conditional World Generation with Adaptive Multimodal Control*, 2025 — https://arxiv.org/abs/2503.14492
- Pasios & Nikolaidis, *CARLA2Real: a tool for reducing the sim2real appearance gap in CARLA*, 2024 — https://arxiv.org/abs/2410.18238

**지름길 학습 / 단서 의존**
- Geirhos et al., *ImageNet-trained CNNs are biased towards texture…*, ICLR 2019 — https://arxiv.org/abs/1811.12231
- Geirhos et al., *Shortcut Learning in Deep Neural Networks*, Nature Machine Intelligence 2020 — https://www.nature.com/articles/s42256-020-00257-z
- Burgert et al., *ImageNet-trained CNNs are not biased towards texture: Revisiting feature reliance through controlled suppression*, NeurIPS 2025 (Oral) — https://arxiv.org/abs/2509.20234
- van Dijk & de Croon, *How Do Neural Networks See Depth in Single Images?*, ICCV 2019 — https://arxiv.org/abs/1905.07005
- Islam et al., *How Much Position Information Do Convolutional Neural Networks Encode?*, ICLR 2020 — https://openreview.net/forum?id=rJeB36NKvB
- Xiao et al., *Noise or Signal: The Role of Image Backgrounds in Object Recognition*, ICLR 2021 — https://arxiv.org/abs/2006.09994
- *Early Cue Precision Shapes Visual Shortcut Learning in Controlled Cue-Manipulation Benchmarks*, 2026 — https://arxiv.org/abs/2606.30344

**합성 데이터 효과 요인**
- *What Makes Synthetic Data Effective in Image Segmentation*, 2026 — https://arxiv.org/abs/2605.19289
- Kar et al., *Meta-Sim: Learning to Generate Synthetic Datasets*, ICCV 2019 — https://arxiv.org/abs/1904.11621
- *SADGE: Structure and Appearance Domain Gap Estimation of Synthetic and Real Data*, 2026 — https://arxiv.org/abs/2605.22467
- *Bridging the Sim2Real gap with CARE*, 2023 — https://arxiv.org/abs/2302.04832
