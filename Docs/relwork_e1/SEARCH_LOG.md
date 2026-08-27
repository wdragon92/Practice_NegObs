# SEARCH_LOG — 조사 수단·질의·접근 실패 전건 기록

- 작성 2026-08-28 · 실행 [클로드 코드] · 브리프 `relwork_survey_brief_v4.md` §1.2("어떤 수단으로 찾았는지 보고서에 기록") · §3(접근 실패는 서지+`승용 이관`)
- **조사일은 전건 2026-08-28 (KST)**. 아래 표의 날짜 열은 전부 같은 날이므로 생략하지 않고 명시한다.
- 기록 원칙: **성공도 실패도 지운 것이 없다.** 우회에 성공한 실패도 실패로 남긴다(다음 사람이 같은 벽을 다시 치지 않게).

---

## 승용 요약 (4문장)

1. 검색 질의 **13건**, 문서 열기 시도 **31건** — 성공 25 / 실패 6.
2. 실패 6건의 정체는 **유료·로그인 벽 3건**(Nature, MDPI, Springer), **SSL 인증서 오류 1건**(Laval 대학 서버), **URL 부재 1건**(arXiv HTML v3), **API 일시 차단 2건**(Semantic Scholar 429, 재시도로 해소).
3. **유료 벽 3건 중 2건은 arXiv 프리프린트로 우회 성공**했다 — 다만 프리프린트와 게재본은 판본이 다를 수 있어 인용 시 주의가 필요하다 → ❓-S1.
4. **끝내 못 연 것은 13건**이고 전부 `승용 이관` 태그를 달았다. 그중 갭 확정에 직결되는 건 **Singhani 2019 전문(표 B-4)** 과 **베이스라인 본문(표 B-5)** 두 건이다.

---

## 1. 검색 질의 기록 (수단: WebSearch)

| # | 날짜 | 수단 | 질의 | 성과 |
|---|---|---|---|---|
| Q1 | 2026-08-28 | WebSearch | `StairNet monocular vision stair line detection Scientific Reports 2022 s41598-022-20667-w PMC` | arXiv 2201.05275 프리프린트 경로 확보(Nature 벽 우회) |
| Q2 | 2026-08-28 | WebSearch | `BSDS500 boundary benchmark maxDist 0.0075 image diagonal tolerance correspondPixels definition` | BIDS/BSDS500 공식 코드 경로 확보 |
| Q3 | 2026-08-28 | WebSearch | `CULane evaluation metric "30 pixel" line width IoU 0.5 F1 SCNN Spatial As Deep official definition` | 2차 설명만 나옴 → **원문 확인으로 전환**(브리프 규칙 8 준수) |
| Q4 | 2026-08-28 | WebSearch | `Martin Fowlkes Malik 2004 PAMI "Learning to Detect Natural Image Boundaries" localization tolerance maxDist fraction of image diagonal definition` | 프린스턴 공개 PDF 사본 경로 확보 |
| Q5 | 2026-08-28 | WebSearch | `OccluRoads occluded road negative obstacle detection paper 2025` | **브리프 시드의 오분류 발견** — OccluRoads는 보행자 논문 |
| Q6 | 2026-08-28 | WebSearch | `negative obstacle detection RGB monocular camera 2025 2026 deep learning road pothole ditch dataset` | 포트홀 계열 다수 — 낙차 edge와는 다른 문제로 판단, 표 미적재 |
| Q7 | 2026-08-28 | WebSearch | `descending stair detection monocular RGB "downstairs" robot visually impaired 2024 2025 edge line` | **핵심 문장 단서**(RGB는 오르막에서 선명·내리막에서 흐림) + Hesch 계열 실마리 |
| Q8 | 2026-08-28 | WebSearch | `"descending stair" detection autonomous tracked vehicle monocular camera inertial texture energy optical flow stairwell` | **최강 반례 후보 A-4(Hesch 2010) 확정** |
| Q9 | 2026-08-28 | WebSearch | `"negative obstacle" detection dataset RGB thermal "NPO" road negative obstacles benchmark 2024 2025 semantic segmentation` | NPO/DRNO 데이터셋 계열(B-6·B-7) 확보 |
| Q10 | 2026-08-28 | WebSearch | `Wang Tian "detecting stairs and pedestrian crosswalks for the blind" RGBD 2012 abstract concave convex depth` | 축 D 시드 서지 확정(내용은 벽) |
| Q11 | 2026-08-28 | WebSearch | `monocular RGB "drop-off" edge detection mobile robot "cliff" vision deep learning 2024 2025 dataset boundary line output` | **성과 없음** — 우리 조합(단안 RGB × 낙차 edge 선)의 직접 선행이 검색 상위에 안 나온다는 사실 자체가 갭 근거 보강 |
| Q12 | 2026-08-28 | WebSearch | `"negative obstacle" detection "grazing angle" OR "shallow viewing angle" OR "only the edge is visible" interior not observable camera geometry` | **B-1(JPL Rankin 2007)·B-2(Goodin 2021) 확보 — E 상황 문헌 근거의 핵심** |
| Q13 | 2026-08-28 | WebSearch | `negative obstacle detection 2026 arXiv monocular vision robot hole ditch existence` | 신규 없음 — 2026 신작은 베이스라인(B-5) 외 미발견 |

**인용 1홉 추적(수단: Semantic Scholar Graph API `/citations`)**

| # | 날짜 | 시드 | 방향 | 결과 |
|---|---|---|---|---|
| H1 | 2026-08-28 | StairNet (DOI 10.1038/s41598-022-20667-w) | **앞(citing) 1홉** | 20편 열거 → A-2·A-3·A-5·A-6·A-7·A-9·A-10 적재 |
| H2 | 2026-08-28 | StairNet | **뒤(references) 1홉** | 정독본 참고문헌에서 [15][16][22][23][24][39] 추출 → A-11~A-14·C-5 적재 |
| H3 | 2026-08-28 | Singhani 2019 (arXiv 1902.00842) | **앞(citing) 1홉** | **4편뿐** — MOSTS(2023·2025), 지능형 휠체어 freespace(2022), 점군 세그(2021). 낙차 edge 계열 후속 **없음** → 갭 근거 보강 |
| H4 | 2026-08-28 | StairNetV3 서론 | 뒤 1홉(부분) | 축 D 시드 [27][28] = Wang & Tian 2014 / 2012 확정 |
| — | — | B-1(Rankin 2007)·A-4(Hesch 2010)의 앞 1홉 | **미실시** | 정독 상한·시간 제약 → `GAP_DRAFT.md` ❓-G1 |

---

## 2. 문서 열기 — 성공 (수단·경로 명시)

| # | 대상 | 수단 | 결과 |
|---|---|---|---|
| S1 | chaytonmin off-road 서베이 repo README | WebFetch(GitHub) | Perception 절의 negative obstacle 5행 확보. **재조사 금지 규칙대로 표만 재사용** |
| S2 | arXiv **2201.05275** (StairNet) | WebFetch → PDF 바이너리 → `pdftotext` | **전문 정독**. 평가식·dth=1·데이터셋·참고문헌 확보 |
| S3 | arXiv **2212.01098** (StairNetV2/Sensors 2023) | WebFetch → PDF → `pdftotext` | **전문 정독**. 오르막/내리막 문장·15/25 mm·평가 계승 확보 |
| S4 | arXiv **2308.06715v1** (StairNetV3) | WebFetch(arXiv HTML) | 서론 인용 [27][28]·평가 문구·데이터셋 규모 확보 |
| S5 | arXiv **1902.00842** (Singhani) | WebFetch(abs) | **초록만** |
| S6 | arXiv **1712.06080v1** (SCNN/CULane) | WebFetch → PDF → `pdftotext` | **평가절 원문 확보**(30 px·IoU 0.3/0.5·F-measure) |
| S7 | **Martin et al. 2004** PDF (프린스턴 공개 사본) | WebFetch → PDF → `pdftotext` | **d_max = 1% of the image diagonal (2.88 pixels)** 원문 확보 |
| S8 | **BIDS/BSDS500** `boundaryBench.m`·`evaluation_bdry_image.m` | WebFetch + `curl` raw | `maxDist=0.0075`·`nthresh=99`·`thinpb=true` 원본 코드 확인 |
| S9 | **TuSimple** `evaluate/lane.py`·`doc/lane_detection/readme.md` | `curl` raw | `pixel_thresh=20`·`pt_thresh=0.85`·각도보정 원본 코드 확인 |
| S10 | **JPL SPIE 2007** (Rankin 외) PDF | WebFetch → PDF → `pdftotext` | **E 상황 원문 서술 + 탐지거리 9.5/7.3/11.0 m** 확보 |
| S11 | **PMC8125519** (Goodin 2021) | WebFetch(PMC) | `∝1/R²` 원문 + UGV <10 m 확보 |
| S12 | **UMN OA PDF** (Hesch 2010) | `curl` → `pdftotext` | **전문 정독**. 정량 평가 부재를 원문에서 확인 |
| S13 | CMU RI 페이지 (Heckman 2007) | WebFetch | **초록만** |
| S14 | PMC12693958 (Wozniak 2025) | WebFetch(PMC) | 초록 + mAP 수치 |
| S15 | arXiv 2403.17330 / 2310.20666 / 2607.03818 / 2304.13979 / 2503.11409 / 2412.06549 | WebFetch(abs) | 각 **초록** |
| S16 | Semantic Scholar Graph API — DOI 10.3390/s23042175 · 10.1007/s42452-026-08326-5 | WebFetch(API) | **초록 전문 확보**(출판사 벽 우회) |
| S17 | Semantic Scholar Graph API — DOI 10.1109/IROS.2010.5649411 | WebFetch(API) | 서지 + **GREEN OA PDF 경로**(→ S12) |
| S18 | 로컬 repo 전수 스캔 (베이스라인 PDF 소재 확인) | `python3 os.walk` | repo에 논문 PDF **없음** 확인. ※ 셸 grep이 ugrep(`--ignore-files`)이라 gitignore 트리를 건너뛰므로 지시대로 Python 사용 |
| S19 | 기존 조사분 선적재 | 로컬 `cat` | `Project_NegObs/Docs/negobs_context_scenario_survey_v1.md`(2026-07-24) 전문 — 축 B 시드(Heckman·Murarka·Larson·JPL·Goodin·Singhani)와 인지과학 근거를 `기존` 태그로 적재 |

---

## 3. 문서 열기 — **실패** (전건 · 승용 이관 판정 포함)

| # | 대상 | 수단 | 실패 내용(그대로) | 우회 | 처분 |
|---|---|---|---|---|---|
| F1 | `nature.com/articles/s41598-022-20667-w` (StairNet 게재본) | WebFetch | **HTTP 303 → `idp.nature.com/authorize?...`** (로그인 리다이렉트) | ✅ arXiv 2201.05275 프리프린트 정독 | 게재본 대조는 **승용 이관**(판본 차이 확인용) → ❓-S1 |
| F2 | `mdpi.com/1424-8220/23/4/2175` (Sensors 2023 게재본) | WebFetch | **HTTP 403 Forbidden** | ✅ arXiv 2212.01098 정독 + S2 API 초록 | 게재본 대조 **승용 이관** → ❓-S1 |
| F3 | `link.springer.com/article/10.1007/s42452-026-08326-5` (**베이스라인 본문**) | WebFetch | **HTTP 303 → `idp.springer.com/authorize?...`** | △ S2 API로 **초록만** 확보 | **승용 이관** — 승용이 PDF 보유(브리프 §1.2). 표 B-5의 수치 열 공란 |
| F4 | `arxiv.org/html/2308.06715v3` | WebFetch | **HTTP 404 Not Found** | ✅ v1 HTML 성공 | 해소 |
| F5 | `vision.gel.ulaval.ca/.../heckman_iros_07.pdf` (**Heckman 2007 전문**) | WebFetch | **`unable to verify the first certificate`** (SSL 인증서 검증 실패) | △ CMU RI 페이지 초록만 | **승용 이관** — 전문 필요 시 |
| F6 | Semantic Scholar API (2회) | WebFetch | **HTTP 429 Too Many Requests** | ✅ 시간 두고 재시도 성공 | 해소(일시적 속도 제한) |
| F7 | `xingangpan.github.io/projects/CULane.html` | WebFetch | 실패는 아님 — **페이지에 평가 정의가 없음**("you may use evaluation code in this repo") | ✅ arXiv 원문 평가절에서 확보 | 해소 |

---

## 4. 끝내 못 연 문헌 — **승용 이관 목록** (13건)

| 우선 | 대상 | 왜 필요한가 | 벽의 종류 |
|---|---|---|---|
| **1** | **Singhani 2019 전문** (arXiv 1902.00842) | **갭 확정의 1순위 열쇠** — RGB 단독 × drop-off. 출력이 영역인지 경계인지, 내리막 프레임 유무, 평가 지표 | ※ arXiv PDF는 **공개** — 벽이 아니라 **정독 상한(12편) 잔여분 결재** 문제 → ❓-G2 |
| **2** | 베이스라인 본문 (Esuga-Mopah 2026) | 표 B-5 수치 열 전체 | Springer 로그인 (F3) |
| 3 | Wang & Tian 2012 (BIBM-W) | 축 D 직계 선행 | 출판사 초록 비공개 · openAccessPdf CLOSED |
| 4 | Wang, Pan, Zhang, Tian 2014 (JVCIR) | 축 D 직계 선행 | 출판사 초록 비공개 |
| 5 | Heckman 2007 전문 | 축 B 계보의 조상 — occlusion labeling의 조작적 정의 | SSL 오류(F5) / IEEE |
| 6 | Arbeláez 외 PAMI 2011 | `maxDist=0.0075`의 서술적 정의 출처 | 미시도(IEEE) |
| 7 | Murarka 외 IROS 2008 | 스테레오+**모션** drop-off — 모션은 단안에서도 가능 | 미시도 |
| 8 | Tekin 외 CVPR 2018 | StairNet 신뢰도 함수 c(x) 원출처 | 미시도 |
| 9 | Patil 외 IRC 2019 | StairNet 데이터셋의 원본 출처 | 미시도(IEEE) |
| 10 | Ilyas 외 2018 · Ramteke 외 2021 · Khaliluzzaman 2016/2018 | 구세대 2단계·분류 계열 4편 | 미시도(IEEE/preprints) |
| 11 | Saliency-guided stairs (PRL 2023) | 웨어러블 RGB-D 계단 최신 | Elsevier 유료 |
| 12 | Stairdepth (2025) | 단안 깊이추정 기반 계단 | Springer 유료 |
| 13 | Larson 2011 · Mind the gap 2013 · 高fidelity 2013 · Stereo NegObs 2017 · Matthies&Rankin · 다중모달 negative road obstacle 2025 | chaytonmin 표·검색에서 서지만 확보 | 유료/미시도 |

---

## 5. 이 조사가 **하지 않은 것** (정지 조건 명시)

브리프 §5 정지 조건에 따라 아래는 **의도적으로 멈췄다** — 확장은 승용 결재다.

- B-1(Rankin)·A-4(Hesch)의 **앞 1홉(citing) 미실시** → `GAP_DRAFT.md` ❓-G1.
- 축 C·D는 상한 안에서 **부분 수행**(브리프 §2 "C·D는 cap이 허용하는 만큼")·선분/wireframe 검출 계열 **미조사** → `TOL_CANDIDATES.md` ❓-T4.
- 음성 세트(닮은 가짜 선) 설계로 **넘어가지 않았다** — 브리프 §2-D 주의 준수, 문헌만 적재.
- 브리프 §1.2의 **6갈래 문헌 지도·"네 선반"·베이스라인 분석 문서는 repo에 없음을 재확인**했다(`Docs/` 실물 확인). 전달 방법은 브리프 ❓-3 그대로 미해결 → **이 조사는 그 지도 없이 수행된 1차 패스다.**
- 정독 **9편 사용 / 상한 12편**(브리프 ❓-1). 3편 여유를 남겨 두었다.

---

## 6. 결재란 ❓

| 번호 | 항목 | 담당 |
|---|---|---|
| ❓-S1 | 유료 벽을 arXiv 프리프린트로 우회한 2건(A-1·A-2)의 **인용 판본** — 프리프린트로 인용할지, 게재본 서지로 인용하되 수치는 프리프린트에서 확인했다고 밝힐지 | 승용 |
| ❓-S2 | `승용 이관` 13건의 수집 착수 순서 — 내 제안: §4 표의 우선 열 순서 | 승용 |
| ❓-S3 | 미실시 1홉(B-1·A-4 앞 방향) 착수 승인 (브리프 ❓-2 범위) | 승용 |
| ❓-S4 | 검색 수단에 **Semantic Scholar Graph API**를 정식 수단으로 등재할지 — 출판사 벽 우회에 3회 결정적이었다 | 승용 |
