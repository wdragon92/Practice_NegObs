# RELWORK_TABLE — 관련연구 비교표 (E 초점, 1차 패스)

- 작성 2026-08-28 · 실행 [클로드 코드] · 정본 브리프 `Docs/briefs/relwork_survey_brief_v4.md` §4 스키마
- 열 규약은 브리프 §4 그대로. **기억-작성 금지**: 내용 열(가시 상태·출력·지표·허용오차·데이터)은 **내가 실제로 연 원문/초록/코드에서만** 채웠다. 열지 못한 것은 내용 열 공란 + `승용 이관`.
- 조사 수단·접근 실패는 `SEARCH_LOG.md`에 전건 기록.

---

## 승용 요약 (5문장)

1. 총 **28행**을 적재했다 — 정독(원문 전문 확보) **9편**, 초록 수준 **8편**, 서지만(미개봉·유료벽) **11편**. 정독 상한 12편(브리프 ❓-1) 안이다.
2. **축 A(계단)**: 선(line)을 출력하는 계보는 StairNet 한 뿌리에서 갈라져 나왔고, 그 계보는 전부 **V형 전제**(디딤판이 보이는 상태 — concave line 라벨이 그 증거)다. 내리막을 개선했다고 주장하는 최신판(StairNetV3·StairNetV2)은 **예외 없이 depth를 함께 쓴다**.
3. **축 B(낙차)**: E 상황의 물리를 가장 정확히 서술한 문헌을 찾았다 — JPL Rankin 2007이 *"멀리서 보면 얕은 함몰인지 깊은 도랑인지 알 수 없다"* 고 원문에 적었고, 해법으로 **RGB가 아닌 열화상**을 붙였다. Goodin 2021은 낙차가 화면에서 차지하는 각도가 **1/R²** 로 줄어든다고 원문에 적었다.
4. **가장 위험한 반례는 Hesch 2010(IROS)** — 단안 RGB + 자이로로 **내리막 계단의 leading edge 선**을 검출·추적한다. 우리와 입력·대상·상황이 거의 같다. 다만 학습 기반이 아니고 **정량 평가·허용오차가 원문에 전혀 없다**(내가 PDF 전문을 열어 확인).
5. 브리프가 `OccluRoads`를 낙차 위협 후보로 적었는데, **원문을 열어 보니 낙차가 아니라 '가려진 보행자'** 논문이다(§D-3). 위협이 아니라 *존재 판정 방법*의 선행으로 자리를 옮겨야 한다 → ❓-C1.

---

## 표 읽는 법

- **가시 상태**: V형=낙차/계단의 '속'이 보이는 전제 · E형=선만 보이는 전제 · 무관 · **판단보류**=원문에 명시가 없어 내가 정하지 않음(P1).
- **수집 경로 태그**: `기존`=과거 조사분 선적재 · `코드`=이번에 클로드 코드가 열어 확인 · `승용`=접근 실패, 승용 이관.
- **정독/초록/서지**: 정독=전문 확보, 초록=초록 페이지만, 서지=제목·서지만.

---

## 축 A — 계단 검출

| # | 논문 | 연도 | 입력 | 가정한 가시 상태 | 출력 형태 | 평가 지표 · 허용오차(원문 수치) | 데이터 | 내리막 명시 | 우리와의 관계 | 출처 | 태그 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A-1 | Wang, Pei, Qiu, Tang — **StairNet**: Deep Leaning-Based Ultra-Fast Stair Detection | 2022 | 단안 RGB 512×512 | **V형** (원문에 가시 전제 서술은 없음 / 근거: 라벨이 convex line + **concave line** 2종이며 concave line = 디딤판·챌면 접합선이라 속이 보여야 존재. 내 해석임을 명기) | 64×64 셀 격자 × 선분 끝점 회귀 (**선**) | accuracy · recall · FWIOU (c(x)=0.5) · mFWIOU(c=0.05~0.95, step 0.05). **허용오차: 끝점 거리 임계 `dth = 1`, 지수 신뢰도 α=2** (원문 식 5). "DT(x) is defined as the 2D Euclidean distance in the image space. dth is the distance threshold and is set to 1." **단위 원문 미명시** → ❓-C2 | 실사 3,094장 (train 2,670 / val 424) — 베이항대·만리장성 촬영 + 인터넷 수집 + [22] 재라벨 | 자기 방법 △ (관련연구에서 [16] upstairs/downstairs SVM, [24] 오르막/내리막 분류만 인용) | **평가 관례** + 배경(선 출력 계보의 뿌리) | [arXiv 2201.05275](https://arxiv.org/pdf/2201.05275) · DOI 10.1038/s41598-022-20667-w | 코드 · **정독** |
| A-2 | Wang, Pei, Qiu, Tang — **StairNetV2** / RGB-D-Based Stair Detection and Estimation | 2022(arXiv)·2023(Sensors) | **RGB + depth** (RealSense D435i) | **V형** (동일 구조 + 디딤판 기하 파라미터 산출) | 선 + 계단 폭·높이 기하 파라미터 + 점군 | accuracy · recall · IOU (confidence 0.5). **"The confidence calculation is the same as that of StairNet"** → dth=1 이월. 기하 파라미터 RMSE **오르막 15 mm / 내리막 25 mm** | 실사 5,992장 (train 4,776 / val 1,216, RGB+depth 쌍) | **O — 핵심 인용**: *"the edges of stairs in an RGB map are clear when ascending stairs but fuzzy when descending, which is the opposite in a depth map"* | **배경 + 우리 문제의 문헌 근거** (내리막에서 RGB 선 단서가 흐려진다는 원문 진술) | [arXiv 2212.01098](https://arxiv.org/pdf/2212.01098) · DOI 10.3390/s23042175 | 코드 · **정독** |
| A-3 | Wang, Pei, Qiu, Wang, Tang — **StairNetV3**: Depth-aware Stair Modeling | 2023 | 단안 RGB + depth 예측(joint task) + depth 센서 | **V형** (tread surface·riser surface를 직접 예측) | convex/concave 선 + 디딤판·챌면 면 + 점군 재구성 | "we use precision, recall, and IOU with a confidence level of 0.5" — **허용오차 정의 원문에 없음**. IOU 종전 최고 단안 대비 +3.4% | 실사 RGB-D 2,276 train / 556 val / 154 test 쌍 (Mendeley 공개) | **O** — *"StairNetV3 has better performance in environments with fuzzy visual cues compared to StairNet, such as night and descending stairs."* | **위협 후보(약)** — 내리막 개선을 명시 주장. 단 **depth 의존** | [arXiv 2308.06715](https://arxiv.org/html/2308.06715v1) | 코드 · **정독**(서론·평가절) |
| A-4 | Hesch, Mariottini, Roumeliotis — **Descending-stair detection, approach, and traversal with an autonomous tracked vehicle** | 2010 | **단안 RGB + 3축 자이로** | **E형에 가장 근접** — far-approach(P1)에서는 속이 안 보여 **texture energy로 가설만** 세우고, near-approach(P2)에서 optical flow + line으로 *"the depth discontinuity at the leading stair edge"* 를 특정 | 계단 위치 가설(영역) → **leading edge 직선** + 3-DOF 자세 | **정량 지표·허용오차 원문에 없음** — Experiment 1/2의 정성 데모(실기 iRobot Packbot)만. Laws texture-energy 창 p=7 등 구현 상수만 기재 | 실사(실내 계단, 실기 주행) | **O — 제목부터 내리막 전용** | **최강 반례 후보 (위협)** | [UMN OA PDF](http://www-users.cs.umn.edu/~stergios/papers/IROS-2010-Stair-Descend.pdf) · DOI 10.1109/IROS.2010.5649411 | 코드 · **정독** |
| A-5 | Wozniak, Penar, Bielecki — RGB-Based Staircase Detection for Quadrupedal Robots | 2025 | RGB 2시점(전방·전방하단), Unitree Go1 | 판단보류 (원문에 가시 전제 서술 없음) | **박스** (YOLOv11n) | mAP@50 **87.56%**(전체) / **51.30%**(계단만), mAP@75 79.88, IoU 0.5는 NMS용 | 실사 18 시퀀스 21,000+ 장 | X — *"When descending the stairs, the robot was carried to prevent possible damage."* | 배경(박스 출력 계열 최신) | [PMC12693958](https://pmc.ncbi.nlm.nih.gov/articles/PMC12693958/) · DOI 10.3390/s25237247 | 코드 · 초록+본문 일부 |
| A-6 | Kurbis, Kuzmenko, Ivanyuk-Skulskiy, Mihailidis, Laschowski — StairNet(동명이인 주의): Visual Recognition of Stairs for Human-Robot Locomotion | 2023/2024 | egocentric RGB | 무관(이미지 수준) | **이미지 수준 분류** (픽셀 위치 없음) | 분류 정확도 최대 **98.8%**, 추론 2.8 ms(모바일 GPU) | 실사 **515,000+ 장** 수동 라벨 | 초록에 "transitions to and from stairs" (내리막 포함 시사, 클래스 명단은 미확인) | 배경 — 위치 없음이라 우리 1단계엔 불충분 | [arXiv 2310.20666](https://arxiv.org/abs/2310.20666) · DOI 10.1186/s12938-024-01216-0 | 코드 · 초록 |
| A-7 | Kim, Jung, Kim, Kim, Agha-mohammadi — Staircase Localization for Autonomous Exploration in Urban Environments | 2024 | **단일 RGB-D** | 판단보류 | 계단 위치·방향 + **up/down 방향**; 3단 캐스케이드(객체검출 → line segment detection → 위치추정) | 초록에 **정량 지표 없음** ("accurate stair detection and localization") | 실사 | **O** — "various structured and unstructured **upstairs and downstairs**" | 위협 인접 — 내리막 명시 + 선분 사용, 단 **depth 사용** | [arXiv 2403.17330](https://arxiv.org/abs/2403.17330) | 코드 · 초록 |
| A-8 | Gîngu, Spînu — TRISTAR: Triple-Signal Stair Recognition ... Micro-UAVs | 2026-07 | **단안 RGB** + Depth Anything V2(단안 깊이 추정) | 판단보류 | 검출/인식(형식 미명시) | 문 검출 precision 0.93 / F1 0.91; 깊이 보정 상대오차 27.4%→10% 미만 | 실사(실내 비행) | X — 오르막만 | 배경(단안 깊이추정 접목 최신) | [arXiv 2607.03818](https://arxiv.org/abs/2607.03818) | 코드 · 초록 |
| A-9 | Stairdepth: staircase detection through depth maps generated by Depth Anything V2 | 2025 | | | | | | | 미개봉 — **승용 이관** | DOI 10.1007/s41870-025-02438-8 | 승용 · 서지 |
| A-10 | Saliency-guided stairs detection on wearable RGB-D devices ... Swin-Transformer | 2023 | | | | | | | 미개봉(유료) — **승용 이관** | DOI 10.1016/j.patrec.2023.11.022 | 승용 · 서지 |
| A-11 | Patil 외 — Deep learning based stair detection and statistical image filtering for autonomous stair climbing (IRC) | 2019 | | | | | | | 미개봉 — **승용 이관**. (StairNet 참고문헌 [22]이자 StairNet 데이터셋의 원본 출처) | DOI 10.1109/IRC.2019.00035 (StairNet [22]) | 승용 · 서지 |
| A-12 | Ilyas 외 — Staircase Recognition and Localization using CNN for Cleaning Robot | 2018 | | | | | | | 미개봉 — **승용 이관** (StairNet [23]) | preprints201812.0296.v1 | 승용 · 서지 |
| A-13 | Ramteke, Parabattina, Das — A neural network based technique for staircase detection using smart phone images (WiSPNET) | 2021 | | | | | | | 미개봉 — **승용 이관**. StairNet 본문 기술: *"whether the ROI is upstairs or downstairs [24]. Such a classification method does not achieve pixel-level stair localization."* | DOI 10.1109/WiSPNET51692.2021.9419425 (StairNet [24]) | 승용 · 서지 |
| A-14 | Khaliluzzaman 외 — Stairways detection ... three connected point / Comparative analysis RGB vs RGB-D | 2016·2018 | | | | | | | 미개봉 — **승용 이관** (StairNet [15][16]; [16]은 upstairs/downstairs SVM 분류) | DOI 10.1109/HSI.2016.7529653 · 10.1109/ICISET.2018.8745624 | 승용 · 서지 |

---

## 축 B — negative obstacle · drop-off

| # | 논문 | 연도 | 입력 | 가정한 가시 상태 | 출력 형태 | 평가 지표 · 허용오차(원문 수치) | 데이터 | 내리막/낙차 명시 | 우리와의 관계 | 출처 | 태그 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B-1 | Rankin, Huertas, Matthies (JPL) — **Nighttime negative obstacle detection for off-road autonomous navigation** | 2007 | **열화상 스테레오 + 스테레오 거리** | **E형을 원문이 정면으로 서술** — *"the visible portion of a negative obstacle rapidly shrinks with range"* · *"it is hard to see into a depression far enough to distinguish it from terrain self occlusions"* · *"Looking at the trench from a distance, one can not tell if there is a slight depression that is traversable, or a deep trench that is non-traversable. **An additional cue is needed**"* | 열 신호 폐곡선 + 기하 필터 → 낙차 후보 영역 | 정확도 곡선 아님. **거리 수치**: 0.6 m 도랑을 ladar 9.5 m / FLIR 스테레오 7.3 m / narrow-FOV CCD 스테레오 11.0 m에서 탐지 — 24 kph 정지거리 11.9 m(보수적으로 17.8 m)에 **미달**. 필터 상수: 연결성분 길이 0.67~80 m | 실사(Demo-III, Ft. Knox 등) | **O** | **배경 + E 상황의 1순위 문헌 근거** ("추가 단서가 필요하다"까지 원문에 있음 — 그들의 답은 열화상, 우리의 물음은 RGB) | [JPL SPIE 2007 PDF](https://www-robotics.jpl.nasa.gov/media/documents/spie2007-rankin-6561-2.pdf) | 기존+코드 · **정독** |
| B-2 | Goodin, Carrillo, Monroe, Carruth, Hudson — An Analytic Model for Negative Obstacle Detection with Lidar | 2021 | 라이다(해석 모델 + 물리 시뮬 검증) | **E형의 물리 근거** — *"the angle subtended by a positive obstacle at a range R from the sensor ∝1/R, whereas the angle subtended by a negative obstacle ∝1/R²"* · *"the difficulty associated with detecting negative obstacles is primarily geometric"* | 탐지 거리 예측 모델 | **UGV(2 m 마운트): 전 구성에서 10 m 미만**, 대부분의 시뮬에서 탐지 실패. UAV(40 m): VLP-16 60–80 m / HDL-32E 65–84 m / OS1 71–97 m | 물리 기반 시뮬 | **O** | 배경 + **"왜 E 상황이 필연인가"의 정량 근거** | [Sensors 21(9):3211](https://pmc.ncbi.nlm.nih.gov/articles/PMC8125519/) | 기존+코드 · 정독(해당 절) |
| B-3 | Heckman, Lalonde, Vandapel, Hebert — Potential Negative Obstacle Detection by **Occlusion Labeling** | 2007 | 라이다(3D 누적) | 속 비가시를 전제 — 관측된 데이터가 아니라 **결측(가림) 데이터를 해석**해 낙차 후보를 세운다 (초록: *"based on missing data interpretation"*) | 3D occlusion 라벨(점유/가림 분류) | 초록에 정량 지표 없음 — **전문 미개봉** | 실사(Demo-III XUV 실기) | O | 배경·계보의 직계 조상 | [CMU RI 페이지](https://publications.ri.cmu.edu/potential-negative-obstacle-detection-by-occlusion-labeling) | 기존+코드 · 초록 (전문 **승용 이관**) |
| B-4 | Singhani — Real-Time Freespace Segmentation on Autonomous Robots for Detection of Obstacles and **Drop-Offs** | 2019 | **단안 RGB 단독** | 판단보류 — 초록에 가시 전제 서술 없음 | **영역**(freespace map) — 선 아님 | 초록에 지표·허용오차 없음 (55 fps @ 임베디드 GPU). **전문 미개봉** | 초록에 명시 없음 | **O** — *"negative obstacles (e.g. dropoffs, ledges, **downward stairs**)"* | **반례 후보(중)** — RGB 단독 + drop-off 명시. 단 출력이 영역이고 edge 선이 아니며 E형 전제 미확인 | [arXiv 1902.00842](https://arxiv.org/abs/1902.00842) | 기존+코드 · 초록 (전문 **승용 이관**) |
| B-5 | Esuga-Mopah, Shonde, Maiti, DasMahapatra, Santra — Negative obstacle detection and avoidance using YOLOv8 and depth profile analysis | 2026 | **RGB(YOLOv8n) + RealSense depth + 2D laser scan**, ROS2 | **V형** (구멍 내부가 박스로 잡히는 크기 전제 — §7 실험의 근거) | **박스** → laser scan 변환 → ROS2 nav 융합 | 초록에 수치 없음. **Springer 로그인 벽 → 본문 미개봉**. 브리프 §1.2가 인용한 수치(일관 탐지 0.3–0.8 m, 원거리 세로 스트립 매몰, 이미지 수준 70/20/10 split)는 **승용 보유 PDF 근거** — 이 표에서는 재확인 못 함 | **시뮬 전용**(Gazebo, 자체 제작 데이터셋) | O | **베이스라인 (브리프 §7 A트랙)** | DOI 10.1007/s42452-026-08326-5 · [S2 API 초록](https://api.semanticscholar.org/graph/v1/paper/DOI:10.1007/s42452-026-08326-5) | 코드 · 초록 (본문 **승용 이관** — 승용이 PDF 보유) |
| B-6 | Feng, Feng, Guo, Sun — Adaptive-Mask Fusion Network for Segmentation of Drivable Road and Negative Obstacle **With Untrustworthy Features** | 2023 | **RGB + depth** | 판단보류 — 다만 *"untrustworthy features"* = 깊이가 무효(0)인 영역이 세그를 혼란시킨다는 문제의식은 우리의 E 상황과 인접 | **세그멘테이션 마스크** | 초록에 수치 없음 — 전문 미개봉 | **실사 대규모** — NPO 기반 RGB-D 데이터셋(DRNO) | O | 배경/위협 인접 — negative obstacle을 픽셀 세그로 푸는 최신 계열 | [arXiv 2304.13979](https://arxiv.org/abs/2304.13979) | 코드 · 초록 |
| B-7 | Jiao 외 — LuSeg: Efficient Negative and Positive Obstacles Segmentation ... on the Lunar | 2025 | RGB-D | 판단보류 | 세그멘테이션 마스크 | 초록: SOTA 성능, 약 57 Hz | LunarSeg(합성/실사 미확인) + 공개 실사 NPO | O | 배경 | [arXiv 2503.11409](https://arxiv.org/abs/2503.11409) | 코드 · 초록 |
| B-8 | Murarka, Sridharan, Kuipers — Detecting obstacles and drop-offs using stereo and motion cues (IROS) | 2008 | | | | | | | 미개봉 — **승용 이관** | [UT Austin PDF 링크](https://www.cs.utexas.edu/~ai-lab/pubs/Murarka-iros-08.pdf) | 기존 · 서지 |
| B-9 | Larson & Trivedi — Lidar based off-road negative obstacle detection and analysis (ITSC) | 2011 | | | | | | | 미개봉 — **승용 이관** (chaytonmin 표 확인) | DOI 10.1109/ITSC.2011.6083105 | 기존 · 서지 |
| B-10 | Mind the gap: detection and traversability analysis of terrain gaps using LIDAR (Robotica) | 2013 | | | | | | | 미개봉 — **승용 이관** (chaytonmin 표) | Robotica 2013 | 기존 · 서지 |
| B-11 | High Fidelity Day/Night Stereo Mapping with Vegetation and Negative Obstacle Detection (IROS) | 2013 | | | | | | | 미개봉 — **승용 이관** (chaytonmin 표) | IROS 2013 | 기존 · 서지 |
| B-12 | Stereo Vision based Negative Obstacle Detection (ICCA) | 2017 | | | | | | | 미개봉 — **승용 이관** (chaytonmin 표) | ICCA 2017 | 기존 · 서지 |
| B-13 | Matthies & Rankin (JPL) — Negative Obstacle Detection by Thermal Signature | 2003경 | | | | | | | 미개봉 — **승용 이관** (B-1의 선행) | [JPL PDF 링크](https://www-robotics.jpl.nasa.gov/media/documents/matthies-negobs.pdf) | 기존 · 서지 |
| B-14 | Min 외 — Autonomous Ground Robots in Unstructured Environments: How Far Have We Come? (JFR) | 2025/26 | — | — | 서베이 | — | — | Perception 절에 negative obstacle 5편(B-3·B-9·B-10·B-11·B-12) 수록. **stair/drop-off/ditch 전용 항목은 표에 없음** | **평가 관례 아님 · 배경 지도** — 재조사 금지, 표만 재사용 | [arXiv 2410.07701](https://github.com/chaytonmin/Survey-Autonomous-Driving-in-Unstructured-Off-Road-Environments) | **기존** · README 확인 |

---

## 축 C — 경계(선) 평가 관례 *(수치 상세는 `TOL_CANDIDATES.md`)*

| # | 논문/코드 | 연도 | 입력 | 가시 상태 | 출력 형태 | 평가 지표 · **허용오차(원문 수치)** | 데이터 | 내리막 | 우리와의 관계 | 출처 | 태그 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C-1 | Martin, Fowlkes, Malik — Learning to Detect Natural Image Boundaries Using Local Brightness, Color, and Texture Cues (PAMI 26(5)) | 2004 | RGB | 무관 | 경계 확률맵(pb) | 이분매칭 대응 후 P/R/F. **"Each of the curves in Figure 3 uses a fixed distance tolerance d_max = 1% of the image diagonal (2.88 pixels)."** Fig.14에서 허용오차를 바꿔가며 F 변화를 인쇄 | BSDS(실사) | 무관 | **평가 관례 1순위** | [PDF(프린스턴 사본)](https://www.cs.princeton.edu/courses/archive/fall09/cos429/papers/martin_et_al.pdf) | 코드 · **정독** |
| C-2 | Arbeláez 외 — **BSDS500 공식 벤치마크 코드** (`boundaryBench.m` / `evaluation_bdry_image.m`) | 2011~ | — | — | — | 코드 기본값 **`maxDist = 0.0075`**, `nthresh = 99`, `thinpb = true`. 주석은 `"MaxDist : For computing Precision / Recall."` 뿐 — **"이미지 대각선 비율"이라는 문구는 이 두 파일에 없음** → ❓-C3 | BSDS500 | — | **평가 관례 1순위(도구 기본값)** | [BIDS/BSDS500 코드](https://github.com/BIDS/BSDS500/blob/master/bench/benchmarks/boundaryBench.m) | 코드 · **원본 코드 확인** |
| C-3 | Pan, Zhan, Shi, Luo, Wang, Tang — Spatial As Deep: Spatial CNN (AAAI) / **CULane** | 2018 | RGB | 무관 | 차선 곡선 | **"we view lane markings as lines with widths equal to 30 pixel and calculate the intersection-over-union (IoU) between the ground truth and the prediction."** IoU 임계 **0.3(loose)·0.5(strict)**, 최종 지표 F-measure(β=1). 학습 시 타깃 선 두께는 **16 px**, 입력 800×288 | 실사 133,235 프레임 | 무관 | **평가 관례** — 선을 '띠'로 만들어 IoU로 채점하는 관례 | [arXiv 1712.06080](https://arxiv.org/pdf/1712.06080v1) | 코드 · **정독(평가절)** |
| C-4 | **TuSimple Lane Detection Benchmark 공식 평가 코드** (`evaluate/lane.py`) | 2017 | RGB | 무관 | 폴리라인(고정 y 표본) | **`pixel_thresh = 20`**, **`pt_thresh = 0.85`**. 실제 임계는 각도 보정: `thresh = pixel_thresh / cos(angle)`. 점 정답 = `abs(pred - gt) < thresh`, 차선 매칭 = 점 정확도 ≥ 0.85 | 실사 3,626 프레임 라벨 | 무관 | **평가 관례** — 점 단위 거리 허용오차 관례 | [TuSimple 코드](https://github.com/TuSimple/tusimple-benchmark/blob/master/evaluate/lane.py) | 코드 · **원본 코드 확인** |
| C-5 | Tekin, Sinha, Fua — Real-Time Seamless Single Shot 6D Object Pose Prediction (CVPR) | 2018 | RGB | 무관 | 6D 포즈 꼭짓점 | StairNet의 지수 신뢰도 c(x)(A-1)가 인용한 원 출처 [StairNet ref 39]. **미개봉 — 승용 이관** | — | — | 평가 관례(간접) | DOI 10.1109/CVPR.2018.00038 | 승용 · 서지 |

---

## 축 D — 유사선 혼동 · 존재 판정 선행

| # | 논문 | 연도 | 입력 | 가시 상태 | 출력 형태 | 평가 지표 · 허용오차 | 데이터 | 내리막 | 우리와의 관계 | 출처 | 태그 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D-1 | Wang & Tian — Detecting stairs and pedestrian crosswalks for the blind by RGBD camera (BIBM-W) | 2012 | | | | | | | **초록이 출판사에 의해 비공개(S2 API: `abstract: null`, openAccessPdf CLOSED)** — 내용 열 공란, **승용 이관**. *간접 근거*(내가 연 StairNetV3 서론): *"extract corresponding one-dimensional depth features in depth images to distinguish between stairs and pedestrian crosswalks"* [27,28] | DOI 10.1109/BIBMW.2012.6470227 | 승용 · 서지 |
| D-2 | Wang, Pan, Zhang, Tian — RGB-D image-based detection of stairs, pedestrian crosswalks and traffic signs (JVCIR 25(2):263–272) | 2014 | | | | | | | 동일 — 초록 비공개, **승용 이관**. 간접 근거 동일 [StairNetV3 ref 27] | DOI 10.1016/j.jvcir.2013.11.005 | 승용 · 서지 |
| D-3 | Melo Castillo, Martin Serrano, Salinas, Sotelo — Prediction of Occluded Pedestrians ... **OccluRoads** Dataset | 2024 | 도로 장면 이미지 | 완전 비가시 대상 | **존재 판정**(presence prediction) — KG + KGE + 베이즈 추론 | **F1 0.91** (전통 ML 대비 최대 +42%) | 실사 + 가상 혼합 | — | **⚠ 브리프의 '낙차 위협 후보' 표기는 사실과 다름** — 낙차·계단·구멍 언급이 원문에 전혀 없다(내가 초록 전문 확인). 자리 이동: **존재 판정 방법의 선행(배경)** → ❓-C1 | [arXiv 2412.06549](https://arxiv.org/abs/2412.06549) | 코드 · 초록 |
| D-4 | Research on Negative Road Obstacle Detection Based on Multimodal Feature Enhancement and Fusion | 2025 | | | | | | | 미개봉 — **승용 이관** (검색 중 발견, ResearchGate 벽) | ResearchGate 388441052 | 승용 · 서지 |

---

## 이 표에서 아직 못 채운 칸 (정직 표기)

- **B-5(베이스라인) 수치 열 전체** — Springer 로그인 벽. 승용 보유 PDF로만 채울 수 있다.
- **B-4(Singhani) 지표·데이터 열** — 초록만 열었다. RGB 단독 + drop-off라 **반례 판정에 직결**되므로 우선 확보 대상.
- **A-4(Hesch) 정량 열** — 원문에 없는 것이 확인된 결과다(공란이 아니라 '없음').
- **A-1 `dth=1`의 단위** — 원문이 "image space"라 적었는데 좌표는 셀 단위 정규화값이다. 내가 정하지 않는다(P1) → ❓-C2.

---

## 결재란 ❓

| 번호 | 항목 | 담당 |
|---|---|---|
| ❓-C1 | 브리프 §2 축 B 시드의 `OccluRoads` 표기 정정 — 낙차 위협 후보 ✗ / 존재 판정 방법 선행 ○. 브리프 차기판에 반영할지 | 승용 |
| ❓-C2 | StairNet `dth=1`의 단위 해석(픽셀 vs 셀 정규화 단위). 우리 채점에 인용하려면 확정 필요 — 저자 코드 확인 또는 저자 문의 | 승용 |
| ❓-C3 | BSDS500 `maxDist=0.0075`의 "이미지 대각선 비율" 서술을 어느 원전으로 인용할지 (코드 주석엔 없음, Martin 2004 본문엔 `1% of the image diagonal` 표현이 있음) | 승용 |
| ❓-C4 | 정독 상한 12편(브리프 ❓-1) 확정 — 현재 9편 사용, 3편 여유 | 승용 |
| ❓-C5 | 인용 1홉 범위(브리프 ❓-2) — 지금은 A축(StairNet 앞·뒤 1홉)과 B축(Singhani 앞 1홉)만 완주. C·D는 상한 안에서 부분 | 승용 |
| ❓-C6 | 유료벽 11건(태그 `승용`)의 수집 우선순위 — 내 제안: B-4 → B-5 본문 → D-1/D-2 → A-11 | 승용 |
