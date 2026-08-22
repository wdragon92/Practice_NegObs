# NegObs 주간 실행 브리프 — DAYRUN 0820 (2026-08-20)

**전제**: 어젯밤 mainrun_0819가 완료된 상태에서의 후속 사이클이다. 처음 보는 인스턴스는 반드시
`experiments/mainrun_0819/`의 `MORNING_REPORT.md` → `DECISIONS.md` → `METRICS.md` → SPEC 3부
(`SPEC_EXTRACTED.md`·`SPEC_CONFLICTS.md`·`PIPELINE_NOTES.md`) 순으로 먼저 읽는다.
설계 원칙(V/E/H 정의·대응쌍·가드레일)은 리포의 `OVERNIGHT_BRIEF_0819_v3.md` 부록 A가 법이다
(없으면 STATUS에 질문 남기고 SPEC 3부로 대체).

**오늘의 임무**: ① 그리드 V1(20칸) 전환 ② E/H 보강 렌더 ③ 진단 3종 ④ 레시피 v2로 3모델
재훈련 ⑤ YOLOv8n 트랙 신설 ⑥ aux 픽셀 손실 1런 ⑦ 교수 브리핑 1p ⑧ 실측 파일럿 추론 도구.
마감 맥락: 8/24 실험 동결, 8/30 논문 제출.

**환경 (STATUS 22:10 실측 기준)**: 훈련 = `conda activate env_seg` / 렌더 = `env_isaaclab`
(활성화 전 `unset PYTHONPATH VIRTUAL_ENV`, 후 `export PYTHONNOUSERSITE=1`). GPU 4090 1장,
동시 훈련 잡 1개, 렌더와 훈련 동시 점유 금지(렌더 먼저). WORKDIR = `experiments/dayrun_0820/`.

---

## 확정 사항 (사용자 결정 — 재논의 금지)

- **헤드라인 = H recall + 오경보(FA) + 트윈 Δ** 유지. **E를 제2 기둥으로 승격**(보강 대상).
- **그리드 V1로 전환**: 섹터 5개(±31.1°, 12.44°) 불변, 거리 밴드 4개 **[0,2)/[2,5)/[5,8)/[8,12) m**
  = 20칸. 셀 인덱스 = band*5 + sector. V0의 band3을 정확히 2분할한 **중첩 구조**(비교 가능성 보존).
  전 산출물 `PROVISIONAL-GRID-V1` 태그, `gridspec_v1.json` 파라미터화(롤백 = json 스왑).
- **YOLOv8n을 본 표 4행째로 추가** (재학습 기반, zero-shot은 참고치).
- **amodal 픽셀 GT 파생** → (a) YOLO bbox GT (b) aux 손실 타깃 두 갈래.
- **발전 서사(v1→v2) 채택**: 진단·수정·결과를 논문 재료로 보존.

## 작업 기본값 (아침 결재 대체 — DAYRUN_REPORT에 일괄 승인란으로)

계단 게이트 유지(pregate 보존 그대로) / HOLD 4씬 유지 / G5는 밴드별 참고 지표로 강등
(GATES_REPORT의 "GATE FAILURE" 문구를 참고 판정으로 정정) / 유리 씬(s06·08·12)·C2 육안은
사용자 몫으로 이월 / 광도 증강(예비탄3)은 실측 파일럿 결과 후 결정.

---

## Phase 1 — 그리드 V1 전환 + 무결성 검증 (라벨만, 훈련 전)

1. `gridspec_v1.json` 작성(위 상수) → **전 프레임 재라벨**(렌더 재사용, 원커맨드).
2. **불변량 검증 (필수 게이트)**: V/E/H는 프레임 속성이라 그리드와 무관 — V1 재라벨 후
   **티어 집계가 V0와 완전 동일(V438·E36·H45)해야 한다.** 다르면 라벨러 버그, 즉시 중단·보고.
3. V0 vs V1 비교표: 셀별 양성 수 20칸 히트맵, 프레임당 평균 양성 셀 수, band3a/3b 분해.
   희소 셀(양성 <10) 목록 명시 — 보강 렌더 조준 근거.

## Phase 2 — E/H 보강 렌더 (env_isaaclab, seed 20260820, 라운드 260820_boost_*)

- **양팔(on/off) 모두** 렌더 — 트윈 구조·FA 측정 유지. 사이드카 패치 동일 적용.
- **H 보강**: test의 s14·s15 + train의 H 보유 씬에 가림물 뒤 +8캠 → 목표 test H 21→약 40.
- **E 보강**: 위험 씬(test {05,07,15,18}+s14 및 train 위험 씬)에 원거리(6–12m)·저고도 캠 추가
  → 목표 test E 9→30+.
- 완료 후 Phase 1 파이프라인으로 재라벨·manifest v2·게이트 재실행. 분리는 씬 단위이므로
  신규 프레임은 소속 씬의 분할을 상속(PROOF 재검증 첨부).

## Phase 3 — 진단 3종 (기존 mainrun_0819 산출물 대상, V0 기준 — 발전 서사의 "before" 증거)

① 셀별 train 양성률 히트맵 + off팔 셀별 FA 히트맵(RGB·Depth s42 병렬) — band3 사전확률 실측.
② 트윈 Δ 밴드별 분해(특히 band3) — 발화가 사전인지 증거인지.
③ C2 분해: 씬 정체 확인 + FA 4장의 발화 셀 분석(0.3m 심각도 혼동 가설).
→ `narrative/diag_v1/`에 보존(교수 브리핑·논문 재료).

## Phase 4 — 재훈련 레시피 v2 (3모델 공통 — 표 공정성 원칙)

- **분리 v2**: train의 H 보유 씬 중 **H 수가 가장 적은 씬(≥5) 1개를 val로 이동**(test 불가침,
  s14 강제 test·토글 동반 규칙 불변). PROOF 재실행, 이동 씬과 근거를 REPORT에 명시.
- 체크포인트 선택 지표에 **val H recall 포함**(예: val cell F1과 val H recall의 평균).
- **오버샘플**: strict-H 포함 프레임 ×4 (`train_oversample.py`).
- **bias 초기화**: 폴라 헤드 최종 bias = 셀별 train 양성률의 log-odds (V1 20칸 기준 재계산).
- **hflip + 섹터 순열 ON**(D8 헬퍼, 섹터 역순 [4,3,2,1,0], 밴드 불변).
- LR: U-Net 3e-4 / B2 6e-5(캠페인 확인값). 512², batch 8, patience 15, max 150ep, 수렴 플래그.
- **seed 42/43/44 × {RGB U-Net, Depth U-Net, SegFormer-B2}** = 9런. 표는 평균±범위.
- 평가: V1 20칸 기준 전 지표 + **프레임 단위 검출율(아무 정답 칸 적중) 병기**(V0↔V1 연속성 지표)
  + 밴드별 recall/FA + 트윈 Δ(전체·H·밴드별) + 부트스트랩 CI. τ_op=0.5 + τ*(val 셀 F1 최대) 병기.

## Phase 5 — YOLOv8n 트랙

1. **amodal 마스크 파생**: 높이맵 footprint(게이트 후)를 각 컷 카메라로 투영 — **가림 무시**
  (라벨러 기하 재사용). 저장: `annotations/amodal/`.
2. bbox GT = 마스크 성분별 외접 박스. off팔 = 배경 전용(빈 라벨) 포함.
3. ultralytics 설치(전용 venv 허용, 버전 기록), COCO pretrained yolov8n, 분리 v2 준수, seed 42/43/44.
4. **검출→셀 매핑**: bbox 하단 변 양 끝점을 라벨러 카메라 모델로 지면 투영, 교차 셀에 귀속 —
  규칙·의사코드를 `METRICS.md`에 명문화. conf 기본 0.25 + {0.1~0.5} 스윕 보고.
5. 동일 표에 4행째로: V/E/H recall + FA. **H의 구조적 0이 예상 결과**(낮게 나와도 버그 아님 —
  단 0이 아닌 값이 나오면 매핑 누수 의심, 원인 분석).

## Phase 6 — aux 픽셀 손실 1런 (레시피 v2 완료 후)

RGB U-Net seed 42 한정: loss = 셀 BCE + λ·픽셀 BCE(타깃 = amodal 마스크, λ=0.5 기본).
v2 동조건 대비 ablation 한 줄(H·FA·트윈 Δ). 개선 시 서사 강화, 아니어도 보고.

## Phase 7 — 실측 파일럿 추론 도구 (`code/infer_photo.py`)

폰 사진 입력 → letterbox 512 → RGB 모델 → 20칸 오버레이 PNG. 가정(높이 1.65m, hfov EXIF
우선/기본 69°)은 이미지에 워터마크로 명시, PROVISIONAL. 사용법 3줄 README.

## Phase 8 — 교수 브리핑 1p (`narrative/brief_prof_0820.html` 또는 .md)

구성: ① 과제 한 줄 + V/E/H 그림 ② 트윈 H Δ 표(0.240, CI 0 제외 — "낙차 픽셀이 어느 팔에도
없는데 반응이 떨어진다") ③ s14 히트 패널 ④ v1 진단 히트맵 1장 + "그래서 v2에서 이렇게 고쳤다"
반 단락 ⑤ 표 스켈레톤(4행 × V/E/H/FA, V1 기준·재훈련 후 채움). 장식 최소, 인쇄 1장.

---

## 보고·가드레일

- `STATUS.md` 30분 갱신 / `DECISIONS.md` 이어서 D19부터 / 종료 시 `DAYRUN_REPORT.md`:
  완료표, V0→V1 비교, 재훈련 결과표(9런+YOLO 3런), **승인 대기 일괄란**(그리드 V1·작업 기본값·
  val 이동 씬·보강 렌더 수용), 이상 징후.
- 불변: 원본 무수정 / test 불가침(분리 v2의 val 이동은 train→val만 허용) / 지표 임의 재정의 금지 /
  모든 런 보고 / HOLD 씬 사용 금지 / 코드·데이터가 SPEC과 다르면 코드가 사실(SPEC_CONFLICTS 기록).
- 우선순위(시간 부족 시): Phase 1→2→4가 척추. 5는 그다음, 6·7·8은 밤으로 밀려도 됨.
- 막히면 그 트랙만 보류하고 STATUS에 질문, 유휴 금지.
