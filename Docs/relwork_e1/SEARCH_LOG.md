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

---
---

# 【2차 패스】 조사 기록 (2026-08-28 · 승용 결재 반영판)

- 승용 결재(2026-08-28)로 **정독 상한 철회 · 1홉 고정 완화 · 절차 항목 자율 처리**가 정해진 뒤의 기록이다.
- 기록 원칙은 1차와 같다: **성공도 실패도 지우지 않는다.**

## 2-0. 2차 승용 요약 (4문장)

1. 검색 질의 **2건**(WebSearch) · GitHub API **3건** · Semantic Scholar Graph API **4건**(❓-S4 결재로 **정식 수단 등재**) · 문서/코드 열기 **21건**.
2. **인용 홉 3회를 새로 돌았다** — Hesch 앞 **54편**, Rankin 앞 **31편**, Wang&Tian 2014 앞 **100편**. 1차의 "미실시" 항목(❓-S3)이 전부 해소됐다.
3. **전문 정독 4편 신규**(Singhani · Murarka 2008 · Tekin · L-CNN) + **저자 코드 2계열 확인**(StairNet 저자 저장소 · BSDS500 `correspondPixels` 원본).
4. 실패는 **3종**: Berkeley 사본 타임아웃 1건, S2 초록 `null` 다수(제목만 남음), ugrep 정규식 오류 1건(도구 문제, 우회).

---

## 2-1. 검색 질의 (수단: WebSearch)

| # | 날짜 | 수단 | 질의 | 성과 |
|---|---|---|---|---|
| Q14 | 2026-08-28 | WebSearch | `StairNet stair detection Wang Pei Qiu Tang github code repository "Ultra-Fast Stair Detection" dataset` | **저장소 링크가 검색 결과에 없었다** → 수단 전환(GitHub API 직접 조회)으로 해결. 검색만 믿었으면 "코드 비공개"로 잘못 결론 낼 뻔한 지점이라 남긴다 |
| Q15 | 2026-08-28 | WebSearch | `"sTetro-D" deep learning autonomous descending-stair cleaning robot abstract RGB-D detection SSD MobileNet` | **2차 자료 요약만 확보**. 원문·초록을 열지 못했으므로 **기억-작성 금지 규칙에 따라 표 A-17의 내용 열을 비웠다**(요약에서 본 수치를 옮기지 않았다) |

## 2-2. GitHub API (수단: `api.github.com`)

| # | 대상 | 질의 | 결과 |
|---|---|---|---|
| G1 | StairNet 저자 코드 유무 | `/search/repositories?q=stairnet+stair+detection` | **2건 발견** — `MrChenWang/StairNet-DepthOut`, `MrChenWang/StairNet-DepthIn` (MrChenWang = 제1저자 Chen Wang). **❓-C2/T2의 전제(“코드가 공개인가”)가 참으로 확인됨** |
| G2 | 두 저장소 파일 트리 | `/repos/{r}/git/trees/main?recursive=1` | 각 28·30개 파일. 평가 스크립트가 **없다**(train/detect/loss/utils/label_transfer만) |
| G3 | BSDS500 벤치마크 원본 | `/repos/BIDS/BSDS500/git/trees/master?recursive=1` | `bench/source/correspondPixels.cc`·`match.cc`, `bench/benchmarks/correspondPixels.m` 경로 확보 |

## 2-3. Semantic Scholar Graph API (❓-S4 결재로 **정식 수단 등재**)

- **속도 제한 준수**: 호출을 연속으로 몰지 않고 사이에 다른 작업을 끼워 분산했다. **2차에서는 429가 한 번도 나지 않았다**(1차 F6과 대비).

| # | 시드 | 방향 | 결과 |
|---|---|---|---|
| **H5** | Hesch 2010 (DOI 10.1109/IROS.2010.5649411) | **앞(citing) 1홉** — ❓-G1 결재 실시 | **54편 전수 열거.** 내리막 전용 후속 분류: RGB-D 박스(sTetro IROS 2022 / sTetro-D EAAI 2023) · 이미지 수준 분류(Utaminingrum 2021) · ToF·저전력 센서(2014·2015) · 단안 언급(2015 monoscopic, 초록 null). **단안 RGB × 선 출력 × 정량 평가 후속은 0편** |
| **H6** | Rankin 2007 — 제목 검색으로 paperId `cdb2a598…` 확정 후 | **앞(citing) 1홉** — ❓-S3 결재 실시 | **31편 열거.** 새 수확 2건: **Dodge & Yilmaz 2023 T-IV**(비전 기반 낙차 — 그러나 수직 베이스라인 **스테레오**) · **Hu 2011 ICDIP "Negative obstacle detection from image sequences"**(초록 null → 승용 이관). Murarka 2008/2009도 여기서 재확인 |
| **H7** | Wang & Tian 2014 (DOI 10.1016/j.jvcir.2013.11.005) | **앞(citing) 1홉** — 축 D | **100편 열거.** 후속이 **횡단보도 검출기**와 **계단 검출기** 두 무리로 갈라져 있고 서로 안 섞인다. **depth 없이 둘을 가른 후속은 제목 수준에서 미확인**(초록을 다 열지는 않았으므로 '없다'가 아니다). 신규 시드 2건: **Vu 2020 PRL**(단안 선 그룹) · **단일 카메라 모션 스테레오 계단 2019** |
| H8 | sTetro-D (DOI 10.1016/j.engappai.2023.105844) | 단건 조회 | `abstract: null`, `openAccessPdf: 없음` → **미개봉 확정** |

## 2-4. 문서·코드 열기 — 성공

| # | 대상 | 수단 | 결과 |
|---|---|---|---|
| S20 | **arXiv 1902.00842 (Singhani) 전문** | `curl` → `pdftotext -layout` (424줄) | **정독.** 구조·평가·데이터 확인 + **전문 grep으로 stair/drop-off 출현 위치를 전수 확인**(방법·데이터·평가 절 0회). ❓-G2 결재 실시 |
| S21 | **UT Austin `Murarka-iros-08.pdf` 전문** | `curl` → `pdftotext -layout` (438줄) | **정독.** 모션 단서 원리·safety map 채점·오탐 7건·FP 계산 불가 진술 확보 |
| S22 | UT Austin `Murarka-iros-09.pdf` | `curl` → `pdftotext` (491줄) | **내려받았으나 읽지 않았다.** 표에 내용 열을 채우지 않았다 — 정직 표기 |
| S23 | **arXiv 1711.08848 (Tekin CVPR 2018) 전문** | `curl` → `pdftotext -layout` (656줄) | **정독.** `c(x)` 정의 + **"distance threshold to 30 pixels"** 확보 → ❓-C2/T2의 원전 대조 |
| S24 | **arXiv 1905.03246 (L-CNN ICCV 2019)** | `curl` → `pdftotext -layout` (586줄) | **평가절 정독.** sAP 정의·ϑ=5/10/15·1:1 매칭·APH 비판 문장 확보 → 축 C 후보 2 신설 |
| S25 | **StairNet 저자 코드** (`StairNet-DepthOut` 7파일 + `DepthIn` utils.py) | raw.githubusercontent 원문 | `dis2conf`·`calculate_cross_line`·`label_transfer`의 정규화 좌표·`config.py`(64×32, stride 8×16) 확인. **두 저장소의 utils.py는 완전히 동일**(diff 무차이) |
| S26 | **BSDS500 `correspondPixels.m` / `.cc` / `match.cc`** | raw.githubusercontent 원문 | **❓-C3 종결** — `.m` 헤더의 *"as a fraction of the image diagonal"* 와 `.cc`의 `maxDist*idiag` 확인 |
| S27 | 로컬 `Docs/briefs/edge_relabel_brief_v6.md` | `grep` | **1차의 출처 오기 발견·정정** — 베이스라인 수치의 실제 출처가 이 문서 §1.2·§7임을 확인(relwork_survey_brief_v4에는 §7이 없다) |
| S28 | S2 초록 (본문 아님) | Graph API 응답의 `abstract` 필드 | **초록 확보 4건**: sTetro IROS 2022 · Utaminingrum 2021 · Dodge & Yilmaz 2023 · Vu 2020 |

## 2-5. 문서 열기 — **실패** (전건)

| # | 대상 | 수단 | 실패 내용(그대로) | 우회 | 처분 |
|---|---|---|---|---|---|
| F8 | Arbeláez 외 PAMI 2011 (Berkeley TR `EECS-2010-83.pdf` · `amfm_pami2011.pdf`) | `curl` | **배치 명령이 2분 타임아웃 → HTTP 000, 파일 미생성** | — | **승용 이관 유지. 단 우선순위 하락** — ❓-C3이 저자 코드로 이미 해결돼 이 논문이 더는 필수가 아니다 |
| F9 | sTetro-D (EAAI 2023) 초록 | S2 API + WebSearch | **`abstract: null` · OA PDF 없음**. 검색은 2차 자료 요약만 반환 | ✗ | **승용 이관** — 표 A-17 내용 열 공란 유지 |
| F10 | S2 `abstract: null` 다발 | S2 API | Hu 2011(image sequences) · 단일카메라 모션스테레오 2019 · Murarka 2008/2009 · monoscopic 2015 · low-power sensors 2014 등 **제목만 반환** | 일부는 OA PDF로 우회(Murarka) | 나머지 **승용 이관** |
| F11 | (도구) `grep -E` 정규식 | 셸 | **`ugrep: error: error at position 56 ... mismatched ( )`** — 이 환경의 `grep`이 ugrep이라 `\b`·유니코드가 섞인 ERE에서 실패 | ✅ 패턴 단순화로 재시도 성공 | 해소. **다음 사람 주의**: 복잡한 ERE는 ugrep에서 깨진다(1차 S18의 `--ignore-files` 문제와 같은 뿌리) |

---

## 2-6. `승용 이관` 우선순위 — **2차 갱신판** (❓-C6/S2 자율 처리 결과)

**정렬 기준**: 갭 진술을 뒤집을 수 있는 힘 > 축 C 채점 근거 > 계보 보강.

| 우선 | 대상 | 왜 필요한가 | 벽 |
|---|---|---|---|
| **1** | **Hu 외 — Negative obstacle detection from image sequences (ICDIP 2011)** [B-16] | **제목이 곧 반례 조건**(영상 시퀀스만으로 낙차). 갭 진술을 직접 위협할 수 있는 유일한 미개봉 | 유료 · S2 초록 null |
| **2** | **Stairway Detection Based on Single Camera by Motion Stereo (2019)** | **단일 카메라** 명시 + 계단. 위와 같은 이유 | Springer · S2 초록 null |
| **3** | 베이스라인 원문 (Esuga-Mopah 2026) [B-5] | 표 B-5 수치 열. ※ ❓-G3 결재로 **브리프 경유 인용은 이미 채웠다** — 이 건은 검증용 | Springer 로그인 (**승용 PDF 보유**) |
| **4** | **Vu 외 2020 (PRL) 전문** [A-15] | **단안 × 선 그룹**의 채점 허용오차 — 축 A(최근접 선례)와 축 C(관례) 양쪽에 걸린다 | Elsevier 유료 |
| 5 | sTetro-D (EAAI 2023) [A-17] | 내리막 딥러닝 계열의 최신 실체 확인 | Elsevier 유료 |
| 6 | Wang & Tian 2012 · 2014 [D-1·D-2] | 축 D 직계 선행 | 출판사 초록 비공개 |
| 7 | Heckman 2007 전문 [B-3] | occlusion labeling의 조작적 정의 | SSL 오류(F5) / IEEE |
| 8 | Arbeláez 외 PAMI 2011 | ~~`maxDist` 정의~~ **해결됨** → 참고용으로만 | IEEE (F8) |
| 9 | Murarka 2008 후속 IROS 2009 | 내려받았으나 미독(S22) — 필요 시 내가 읽으면 된다 | **벽 없음** |
| 10 | 나머지(A-9~A-14, B-9~B-13, D-4 등) | 계보 보강 | 유료/미시도 |

---

## 2-7. **자율 처리한 절차 항목과 그 이유** (승용 결재 2026-08-28: "절차 항목은 네가 정하고 이유를 로그에 남겨라")

| 번호 | 내 결정 | 이유 |
|---|---|---|
| **❓-C2 / ❓-T2** (StairNet `dth` 단위) | **단위 미상 유지 · `dth=1`을 수치로 인용하지 않는다** | 결재가 준 경로("저자 코드 공개면 확인, 아니면 단위 미상")를 끝까지 따라갔다. 코드는 **공개였다**(G1). 그러나 `dth=1`이 나오는 `calculate_cross_line`이 **두 저장소 어디서도 호출되지 않는 死코드**라 좌표계가 결정되지 않는다. 추가로 **코드 식이 논문 식과 다름**(코드는 0~1 정규화)을 발견해 함께 인쇄했다. 원전(Tekin)은 **30 px**로 픽셀 명시지만, StairNet이 그 단위를 계승했는지는 **원문·코드 어느 쪽으로도 증명되지 않는다** → P1(임의로 정하지 않는다)에 따라 인용 포기 |
| **❓-C3** (BSDS 대각선 비율의 서술 출처) | **`correspondPixels.m` 헤더 + `.cc` 구현을 정본 출처로 확정 · 종결** | 2차 자료를 인용할 필요가 없어졌다. 저자(David Martin) 주석에 문구가 그대로 있고, `.cc`가 `maxDist*idiag`로 실제 곱한다 — **문서와 구현이 일치**하므로 인용 안전 |
| **❓-C4 / ❓-C5** | **소멸 처리** | 정독 상한 철회·홉 완화로 질문 자체가 사라졌다 |
| **❓-C6 / ❓-S2** (수집 순서) | **위 §2-6으로 재정렬** | 1차 제안(B-4 → B-5 → D-1/D-2 → A-11)은 B-4가 해소돼 무효가 됐다. 새 기준은 "갭을 뒤집을 힘" |
| **❓-S1** (판본 인용) | **게재본 서지로 인용하고, 접근에 쓴 arXiv id를 함께 표기** | 결재 지시 그대로 적용. 표의 출처 열에 `DOI ... · arXiv ...` 병기 형식을 유지 |
| **❓-S3** (미실시 1홉) | **실시 완료** — H5(Hesch 앞)·H6(Rankin 앞) | 결재 지시 |
| **❓-S4** (S2 API 등재) | **정식 수단으로 등재** · 속도 제한은 호출 분산으로 준수 | 2차에서 429 발생 0회. 출판사 벽 우회에 3회 결정적이었다 |
| **❓-T3 / ❓-T4 / ❓-T5** | **T4는 조사 실시 후 후보 2로 승격(종결). T3·T5는 "제안"으로만 표기하고 채택은 승용 몫임을 문서에 명기** | 결재가 "계산·인쇄 제안은 좋다, 채택은 승용"이라 정했다 |
| **❓-G3** (베이스라인 수치) | **브리프 경유 인용 + 출처 오기 정정** | 결재 지시대로 브리프를 인용하되, 그 브리프가 `relwork_survey_brief_v4`가 아니라 **`edge_relabel_brief_v6` §1.2·§7**임을 확인해 정정했다(v4에 §7이 없다) |
| **(신설) 1차 계수 오류** | **표 행 수를 실계수로 정정**(28 → 44, 1차분만 37) | 1차 요약의 "총 28행"이 1차 표 자체(37행)와 맞지 않았다. 파일을 다시 세어 고쳤다 — **침묵 수리 금지 원칙에 따라 오류가 있었다는 사실을 남긴다** |
| **(신설) 2차 자료 취급** | **검색 요약에서 본 수치를 표에 옮기지 않았다**(A-17 sTetro-D) | 기억-작성 금지의 취지는 "직접 열지 않은 내용을 채우지 말라"이며, 검색 엔진 요약은 원문이 아니다 |

---

## 2-8. 2차가 **하지 않은 것** (정지 조건)

- **축 D의 100편 초록을 다 열지 않았다** — 제목 수준 판정에 그쳤고, 문서에 "**제목 수준에서 미확인**"으로 명시했다(‘없다’로 쓰지 않았다).
- **Murarka 2009(S22)를 내려받고도 읽지 않았다** — 표에 내용 열을 채우지 않았다.
- **음성 세트 설계로 넘어가지 않았다** — 브리프 §2-D 준수, 문헌만 적재.
- **승용 문헌 지도를 기다리지 않았다** — 결재 지시(❓-3: 대기 금지). 도착 후 대조가 필요하다.
- **2홉 이상으로 확장하지 않았다** — 결재의 "필요 기반"에 따라 필요한 곳(Hesch·Rankin·Wang&Tian 앞 1홉, StairNet→Tekin 뒤 1홉)만 갔다.
