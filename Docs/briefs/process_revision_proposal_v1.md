# NegObs 운영 프로세스 — 현행 정리 + 개정 제안 v1

> 2026-08-05 · 사용자 요청("현재 운영 방식과 개정 논의를 문서화, wave 독립적인 전체 프로세스로")
> 성격: **논의 자료** — §4 개정안과 §5 미결정 항목은 사용자 결재 전까지 효력 없음.
> 결재되면 본 문서가 wave 독립 상설 규칙(process spec)이 되고, wave spec은 얇아진다(§4-R3).

---

## 1. 전체 파이프라인 (wave 독립 시점)

```
[연구 목표] RGB 맥락단서 기반 비가시 낙차(negative obstacle) 추정 — Project_NegObs (U-Net)
     ↑ 학습 데이터 공급
[본 repo] 한국형 합성 씬 라이브러리 33씬 (main 21 + batch1 12) · Isaac Sim 4.5

W1~W2  룩 레이어·사실화 기반 구축 (완료)
W3     이미지 기반 개보수 — 목표 이미지 12장 = 충실도 기준 (완료, 08-05 독트린 반영)
W4     GT 재판정 (연대: 계단참 06·08, 02 중앙파이프, 05 비위반 등)
W5     hazard-off 팔 + 20k 생산 렌더 (~15 h 예상) → 학습 인계
```

씬 = `scenes/main|batch1/*.py` (PARAMS 선언 + kit 호출). 공유 kit: scene_common ·
ground/stair/infra/facade/building/urban/props/variation_kit.

## 2. 현행 운영 방식 (as-is)

**2.1 변경 루프** — 씬 1렌더 → regression → h0.3 육안 → commit. 검증 없는 확산 금지 ·
같은 프림 A/B · 측정 중 공유모듈 동결.

**2.2 Round 체계** — `look_check/<scene>/<round>/` (`<yymmdd>_<wave>_<purpose>`),
`stamp_round.py`가 HEAD·dirty·env 기록. `regression_check.py` v2.1이 전 round 대비
WHITE/FRAME/OCCL/DARK/UNCHANGED 판정 → `Docs/reports/regr_*.json`.
갤러리: `make_review_gallery.py --round R --out look_check/_review/R`.

**2.3 GT ledger** — `Docs/audit_v4/gt_changes_w3.md`, append-only, §0-1 선신고
(보행면·낙차 에지·collision 변경은 착지 전 행 기재), 쓰기는 `flock /tmp/negobs_ledger.lock`.

**2.4 검증 문서 (W3에서 비대해진 부분)** — 씬별 lane report(`w3_*_v1.md`) ·
red-team fanout(다중 agent 교차검증) · 서사적 ledger 기록.

**2.5 Agent 운영** — Opus5+xhigh 병렬 lane, 파일 소유권 분리, pathspec commit,
GPU `flock /tmp/negobs_gpu.lock`.

**2.6 언어·토큰** — 내부 영어 / 사용자 응답·commit 한국어(기술용어 영어 그대로) ·
08-05 원칙: 실행 전 필요성·효용 검토, 서류 최소화.

**2.7 문서 체계** — 법전: `w3_intake_v2_images.md`(사용자 리뷰 원문·결재) ·
규율: `w3_execution_spec_v1.md` · 원장: `gt_changes_w3.md` · 판정: `redteam_*.md` ·
씬별: `w3_*_v1.md`. **전부 W3 접두 — wave 종속 문서에 상설 규칙이 섞여 있음.**

## 3. 진단

1. **토큰 소모의 주범은 판정이 아니라 서류** — lane report·RT 스윙·서사 ledger가
   주간 리밋 소진의 구조적 원인. 실제 결함 검출은 render+script+육안(싼 부분)이 담당.
2. **상설 규칙과 wave 규칙이 한 문서에** — w3_execution_spec은 W3 전용인데 §6.1 floor,
   flock, 검증 루프 같은 상설 규칙이 그 안에 있어 wave가 끝나도 문서가 은퇴를 못 함.
3. **명명 과잉 주장** — "final" 같은 상태 주장 이름이 실제 상태와 어긋남 (08-05 개칭으로 해소).
4. **구 독트린 잔재** — 파손 난간 전제의 큐(RT 스윙·유보 GRAZE·lane report 마감)가
   08-05 독트린 이후 목적을 상실.

## 4. 개정안 (결재 대상)

- **R1 검증 기본선** — 기본 = ①render ②regression script ③FAIL/WARN cut 육안 ④gallery
  사용자 검수. lane report·RT 스윙은 **사용자 명시 요청 시만**. 판정 해석은 ledger 행
  landing 기록 몇 줄로 갈음.
- **R2 ledger 경량 포맷** — 행 = Authority / Scope(commit) / Re-cache / §4 landing(명령+판정
  요약). 서사 금지. §0-1 선신고 원칙 자체는 **유지** (이번 사후 신고는 예외 기록).
- **R3 문서 체계** — 본 문서가 상설 process spec으로 승격. wave spec은 그 wave의
  scope·순서·특이 규칙만. wave 종료 시 wave 문서는 은퇴(참조용).
- **R4 큐 정리** — 폐기: Lane3 RT 스윙 · 유보 GRAZE 재평가 · L05/L14 lane report 마감
  (260805_w3_doctrine round가 갈음). 유지: KM-F1~L15-O10 등 kit 소견 큐(경량 처리),
  씬 번호 재부여, W4 GT, W5 생산.
- **R5 agent 정책** — 기본 inline 단독. multi-agent는 대규모 병렬 작업(생산 렌더,
  33씬 일괄 sweep)만. effort 상향은 판정·설계 국면만.
- **R6 명명 규칙** — round 이름은 범위·목적만 서술("full", "doctrine"), 상태 주장
  단어("final", "done") 금지.
- **R7 사용자 검수 게이트** — 씬 상태를 바꾸는 round는 gallery(`_review/<round>`)로
  사용자 검수 통과 시 ledger 행 CLOSED. 표준 체크리스트는 §6.

## 5. 미결정 — 사용자 룰링 필요

| # | 질문 | 기본값(제안) |
|---|---|---|
| Q1 | N3 trompe-l'oeil(바닥 그림 계단) 같은 **의도적 함정 씬** — 08-05 독트린("평범한 지형")과 공존? | 유지 (함정은 씬 정체성, 파손과 다름) |
| Q2 | scene06 나선 가드 rail 2본 — 시각적으로 허전하면 3~4본? | gallery 검수에서 판단 |
| Q3 | scene12 edge_void cut — 근접 post가 화면 지배, 재조준? | 검수에서 판단 |
| Q4 | 잔여 "규정미달/열화" 정체성 전 씬 sweep 1회 (grep + 육안) 실행? | 실행 (30분급) |
| Q5 | 씬 번호 재부여 round 시점 (16 횡단보도 HELD 포함) | ~~W4 직전~~ **답변됨(08-05): DEFERRED — 재부여 안 함.** 이후 wave에서도 씬 추가 가능성이 높아 지금 재부여하면 곧 무효화됨. 현행 번호 유지. scene16 재정박 HELD는 별도 판단 대기 |

## 6. Gallery 검수 표준 체크리스트

공통(모든 round): ① 새 요소가 **한 제품군**으로 읽히는가(재질·단면 혼종 금지)
② 접지 — 기둥·살대가 바닥에 닿는가(부유/관통 금지) ③ 대면적 순백/암흑 없음
④ 낙차 은닉 전제(h0.3 cut)가 살아 있는가 ⑤ FRAME/OCCL 플래그 cut은 원본 PNG로 확대 확인.

600 px 썸네일로 부족하면 `look_check/<scene>/<round>/pt_noon_<cut>.png` 원본(1920×1080)을 볼 것.

---
*본 round(260805_w3_doctrine)의 씬별 검수 항목은 채팅 보고 참조. 결재 방식: R1~R7 각각
승인/수정/기각 + Q1~Q5 답변이면 충분하다.*
