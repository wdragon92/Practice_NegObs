# NegObs Process Spec v1 — 상설 운영 규칙

> 2026-08-05 사용자 결재로 확정 (R1~R7 승인 — R3·R4는 조건부, §7 결재 기록 참조).
> 전신: `process_revision_proposal_v1.md`(제안서) — 본 파일로 승격·개칭.
> **wave 독립 상설 문서.** wave spec은 해당 wave의 scope·순서만 담고 종료 시 은퇴한다.
> `w3_execution_spec_v1.md`의 상설 규칙은 §2~§5로 **전문 이관 완료**(§8 검증) → 해당 문서 RETIRED.

---

## 1. 전체 파이프라인

```
[연구 목표] RGB 맥락단서 기반 비가시 낙차(negative obstacle) 추정 — Project_NegObs (U-Net)
     ↑ 학습 데이터 공급
[본 repo] 한국형 합성 씬 라이브러리 33씬 (main 21 + batch1 12) · Isaac Sim 4.5

W1~W2  룩 레이어·사실화 기반 구축 (완료)
W3     이미지 기반 개보수 (완료, 08-05 독트린 반영)
W4     GT 재판정 (연대: 계단참 06·08, 02 중앙파이프, 05 비위반 등)
W5     hazard-off 팔 + 20k 생산 렌더 (~15 h) → 학습 인계
```

씬 번호 재부여는 **하지 않는다**(Q5, 08-05 — 이후 씬 추가 가능성 때문에 조기 재부여는 곧 무효화됨).

## 2. 운영 규칙 (확정)

### 2.1 검증 기본선 (R1)
코드 변경 → ①render ②regression script ③FAIL/WARN cut 육안 ④gallery 사용자 검수(§2.5, R7 gate).
씬별 장문 report·red-team 다중 검증은 **사용자 명시 요청 시만**. 판정 해석은 ledger 행의
landing 기록 몇 줄로 갈음한다.

### 2.2 커밋 전 검증 floor (구 W3 spec §6.1 — 전문 이관)
모든 작업 단위, 모든 commit, 착지 전에:
```
python3 -m py_compile <건드린 모든 파일>
NEGOBS_SMOKE=1 python scenes/<dir>/<scene>.py            # 건드린 씬마다
python3 scripts/geom_invariance_check.py                 # 레지스트리 vs 기하 대조
python3 scripts/placement_lint.py --scenes <touched> --rules Docs/briefs/placement_rules_v1.yaml
```
**4개 전부 green이 아니면 commit 금지.** 검증 없는 확산 금지.

### 2.3 변경 루프 규율
- 공유 kit 변경은 **씬 1개 렌더로 먼저 확인** 후 확산한다.
- 비교는 **같은 prim끼리 A/B** (다른 요소가 섞인 비교 금지).
- 측정이 도는 동안 공유 모듈 동결(freeze) — 측정 대상 코드를 중간에 바꾸지 않는다.
- 병렬 작업 시 파일 소유권 분리 + pathspec commit (§2.6).

### 2.4 GT ledger (R2 + 구 W3 spec §8 — 전문 이관)
- **선신고(declare-before-land)**: 보행면·낙차 에지·hazard/collision box·GT가 읽는 AABB를
  움직이는 commit은 착지 전에 ledger(`Docs/audit_v4/gt_changes_w3.md`) 행을 먼저 쓴다.
  commit 메시지에 행 번호(GT-n)를 명기. 쓰기는 `flock /tmp/negobs_ledger.lock`.
- **행 포맷(lean)**: Authority / Scope(commit hash) / Re-cache / §4 landing(실행 명령+판정 요약).
  서사 금지. landing 기록이 비면 행은 닫히지 않은 것이다 — **실제 실행한 명령을 기록하고,
  추측으로 적지 않는다.**
- **re-cache 정의** (행마다 필요한 부분집합을 명시):
  R-1 씬 자체 self-check가 변경 기하에서 hazard/drop 레지스트리를 재유도·출력
  R-2 해당 씬 mini data render 재실행 + `scripts/check_data_run.py` 확인
  R-3 OCCL/GRAZE baseline을 다음 `regr_*.json`에서 재스탬프
- 상태 어휘(OPEN/BLOCKED/HELD/PROOF-ONLY)와 세부 규칙은 ledger 문서 §0~§2가 원본(살아있는 문서).
  HELD 행은 준비만 하고 강제하지 않는다. PROOF-ONLY 행의 비어있지 않은 diff는 결함이지
  새 baseline이 아니다.

### 2.5 Round 규약 (R6·R7 + 구 X1~X3 — 전문 이관)
- 명명: `<yymmdd>_<wave>_<purpose>` — 범위·목적만 서술. **상태 주장 단어("final", "done") 금지.**
- **모든 capture 폴더에 `scripts/stamp_round.py` 실행**(X1) — 스탬프 없는 round는 6주 뒤 판독 불가.
- `meta.json`은 정직하게(X2): 대체 view를 쓰면 그 사실을 기재. 숨기면 gallery가 거짓말을 한다.
- 통람류 판정은 **사진(컷) 이름을 명시**(X3) — 사진 없는 판정은 판정이 아니다.
- gallery는 `make_review_gallery.py --round R --out look_check/_review/R`
  (**`--out` 필수** — 기본값이 `_review_w2`를 덮는다).
- **R7 gate**: 씬 상태를 바꾸는 round는 gallery 사용자 검수 통과 시 ledger 행 CLOSED.
- 참고 계기(advisory, gate 아님): `ori_axis`(실측 0.252±0.074, p95 0.371 — 초과 시 "덜 꾸며짐"
  신호이지 재회전 사유 아님) · `sat_mu`/`sat_sd`/`chroma_sd`(분리력 없음 실측).

### 2.6 Agent 정책 (R5)
기본 inline 단독. multi-agent는 대규모 병렬(생산 렌더, 33씬 일괄 sweep)이나 사용자 요청 시만.
쓸 때: Opus 5 + xhigh(red-team은 Fable + xhigh), 파일 소유권 분리, pathspec commit.

### 2.7 잠금·환경 (구 §13 환경 규칙 — 전문 이관)
- **GPU는 배타·순차**: 모든 render는 `flock /tmp/negobs_gpu.lock` 아래에서. 병렬 render 금지.
- render 셸: `unset PYTHONPATH VIRTUAL_ENV` + `conda activate env_isaaclab` + `PYTHONNOUSERSITE=1`.
- `pxr`(usd-core)는 프로젝트 venv에 없다 — USD 검사는 별도 venv:
  `python3 -m venv /tmp/usdvenv && /tmp/usdvenv/bin/pip install usd-core`.
- asset 인벤토리 파일은 조달(procurement) 소유 — 읽기 전용.

## 3. 재현 명령 블록 (구 W3 spec §13 — 갱신 이관)

```bash
# CPU pre-flight (모든 작업, 모든 commit) — §2.2와 동일
python3 -m py_compile <touched files>
NEGOBS_SMOKE=1 python scenes/main/<scene>.py
python3 scripts/geom_invariance_check.py
python3 scripts/placement_lint.py --scenes all --rules Docs/briefs/placement_rules_v1.yaml
python3 building_kit.py                      # 135/135 + 33씬 스캔 + out_max>0 검사

# render (GPU 배타·순차)
flock /tmp/negobs_gpu.lock bash scripts/rounds/run_<round>.sh [sceneNN ...]
python3 scripts/stamp_round.py look_check/<scene>/<round> <round> <scene>

# 판정
python3 scripts/regression_check.py --list <pairs> --json Docs/reports/regr_<round>.json --fail-only
python3 scripts/make_review_gallery.py --round <round> --out look_check/_review/<round> \
        --status-json Docs/reports/regr_<round>.json
```

## 4. 콘텐츠 불변 규칙 (구 W3 spec §12 do-not-touch — 전문 이관 + 08-05 갱신)

"고치면" 그것이 곧 regression인 항목들:

1. 각진 헤지(생울타리) 박스 형태 — 한국 전정 관행, 의도된 것.
2. **scene17 계단 무난간** — 한강 제방 실관행; `cue_railing=False` 유지. (08-05 독트린과 공존:
   난간이 "있으면" 낙차 표지라는 것이지, 실관행상 없는 곳에 세우라는 뜻이 아님.)
3. scene18 볼라드 없음 — 차도가 없으므로 정당.
4. 가로등 등간격은 옳다(광학 설계) — "등간격 금지" 규약은 장식 배치용. 가로수는 법정 4~8 m 간격.
5. scene19 물탱크 없음 유지.
6. **tactile(점자블록) 기본 OFF를 켜지 말 것**, 볼라드 아래 tactile 패드 금지 (P-10·P-12).
7. 계절·이벤트성 요소를 prop에 넣지 말 것; 낙엽류 asset은 낙엽 씬에만.
8. 원경 흐림(대기 원근) 금지 — 서울 실측 소광은 90 m에서 2.6~7 % 대비 손실뿐.
9. 전신주는 15·18만 허용, 17·20 금지(간선·광장, 지중화율 94.16 %).
   *(08-05 GT-59: **13도 금지 목록에 추가** — G13 시그니처였으나 사용자 지시로 제거.)*
10. **사람·차량 금지** (D1의 지게차·트럭 포함).
11. 맨홀 prop 재론 금지 — W3는 위치만 바꿨다. 실루엣·scatter는 W2에서 종결.
    *(08-05 GT-59 예외: 차도류 프로파일 P4/P7/P8 의 맨홀·잡초는 사용자 지시로 **전면
    소거** — 실루엣 재론이 아니라 배치 금지. 본 항과 모순 아님, 원장 GT-59 참조.)*
12. D1 ISO 컨테이너 치수는 정확하다 — 주름·코너캐스팅만 추가, 박스는 손대지 않는다.
13. sceneD4의 낡은 회황토 tactile 띠는 라이브러리 유일의 올바른 "닳은 tactile" 기준 — 청소 금지.
14. **예산은 triangle 수가 아니라 instance 공유다** — instance 수를 이유로 row를 기각하지 말 것
    (실측: +5.13 M tri에 −0.255 s; instancing 복구로 unique data 863× 절감).
15. `build_tree`의 yaw U(0,360)·lean·`jit_tint`는 jitter 폐지의 **명시적 예외** (수관에 정면 없음).
16. scene05 `seat.arcs` 값은 yaw가 아니라 호 스팬(도) (C-30).
17. `rivermark_plaza_bldg_*` 사용 거부는 유지되며 guard로 강제됨 — guard를 고치지 말 것.
18. (08-05 추가) **의도적 함정 씬 유지**(Q1): N3류 "단서는 있는데 hazard는 없는" 씬은 씬 정체성 —
    폐기된 '파손' 개념과 다르다.
19. 라이선스: **CC0/KOGL만**, 로드뷰·유료·NoAI 금지. asset 우선(asset-first), 실측 mm 기준 판단.

## 5. Parked register (구 W3 spec §9 — live 행만 이관)

완성값으로 구현 금지. 각 행은 해제 gate가 있다:

| ID | 항목 | 해제 gate |
|---|---|---|
| P-1 | scene07 archetype 재건(장대석/자연석/hybrid 후보) | 사용자 레퍼런스 이미지 |
| P-2 | scene10 archetype 재건(D1 후보; 낙차 6.60 유지) — ~~broken_landing 보존~~ **08-05 독트린으로 파손 베이 조항은 무효**, 나머지(널 틈·돌구덩이·통나무 펜스 보존)는 유효 | 사용자 레퍼런스 이미지 + KDS 34 00 00 원문 |
| P-3 | S08-B 파라펫 개구부 처리(B-1 폐합 권고) — ~~B-3 파손 난간 옵션~~ 08-05 독트린으로 소멸 | 한국 선큰광장 마감 사진 n≥5 |
| P-4 | 04 마사토 자갈 퇴적(armouring/rill) | 산림청·서울시 정비 매뉴얼 도판 5장 |
| P-6 | 04 관목 군식(groundcover 밴드·3~7주 clump) + scene13 식재 | 산림청 가로수 매뉴얼 도판 |
| P-7 | prop-엣지 규칙 M1~M6 (벤치·등·휴지통·플랜터·표지판 offset) — LINT-9는 그때까지 WARN | Commons 프레임 픽셀 실측 각 ≥5장 |
| P-8 | 빈 archetype 패널 5 + top-up 2 | 이미지 수확 |
| P-9 | 가로수 lean 상한 1.5°(`[assumed]`) | 사진 확인 또는 U(0,4°) 유지 |
| P-10 | RF-4 부착식 tactile 패드 스펙 | 이중 블록(tactile OFF 사용자 소유 + GT-E1′ 등재) — 기록만, 구현 금지 |
| P-11 | sceneD3 전신주(KS F 4304) | supervisor 룰링(§2.13② 미결) |
| P-12 | 볼라드 전면 tactile 12/42 ON | 사용자 소유 — 손대지 않음 |
| P-13 | 03·12·17 무연석(kerbless) 확인 | 한강 제방·자전거도로 실사진 확인 |
| P-14 | 0.5~1.1 m 단일 바위 대역 공백 | 조달 — 블록하지 말 것 |
| P-15 | scene14 D11 파라펫 하단 결손(실기하 버그, 판정컷 비가시) | 구조 수리는 예산 밖 — 유예 |
| P-16 | scene05 무대 검은 쐐기 틈 | 별도 무대 재설계 패키지 |
| P-17 | `sign_kr101` 0.844 m vs 900 mm 표준 | 연대 3요소 gate — 일괄 rescale 금지 |
| P-18 | `bench_park_05`가 미조달 `bench_curved_01` 재수입 | supervisor: 목록 구속력 판단 |
| P-19 | ambientCG 507 decal + SimReady prop | scope 밖 — 원하면 별도 그룹 |

(사멸: P-5 — GT-4 RETIRED로 gate 방면.)

## 6. Gallery 검수 표준 체크리스트

공통: ① 새 요소가 한 제품군으로 읽히는가 ② 접지(부유·관통 금지) ③ 대면적 순백/암흑 없음
④ h0.3 컷에서 낙차 은닉 전제 유지 ⑤ FRAME/OCCL 플래그 컷은 원본 PNG 확대 확인.
600 px 썸네일로 부족하면 `look_check/<scene>/<round>/pt_noon_<cut>.png` 원본.

## 7. 결재 기록 (2026-08-05, 사용자)

| 항목 | 결과 |
|---|---|
| R1 검증 기본선 | 승인 |
| R2 ledger 경량 포맷 | 승인 |
| R3 문서 체계 | **조건부 승인** — W3 spec의 상설 규칙 전문 이관·검증(§8) 후에만 은퇴. 요약 불충분, 본 문서 단독 완결 필수. → 이행 완료 |
| R4 큐 폐기 | **조건부 승인** — 폐기(Lane3 RT 스윙·유보 GRAZE·L05/L14 report 마감)는 `260805_w3_doctrine` gallery 검수(R7) **통과 후 확정**. 검수에서 문제가 나오면 해당 폐기 항목 부활 가능 |
| R5 agent 정책 | 승인 |
| R6 명명 규칙 | 승인 |
| R7 검수 gate | 승인 |
| Q1 함정 씬 | **유지** — N3류 의도적 함정(단서 有·hazard 無)은 씬 정체성, 폐기된 파손 개념과 다름 (§4-18) |
| Q2 scene06 rail 본수 | 보류 — 사용자 검수 후 결정 |
| Q3 scene12 edge_void 재조준 | 보류 — 사용자 검수 후 결정 |
| Q4 잔여 열화 정체성 sweep | **실행** |
| Q5 씬 번호 재부여 | **DEFERRED** — 재부여 안 함(씬 추가 가능성으로 조기 재부여는 곧 무효화). 현행 번호 유지 |

## 8. 이관 검증 체크리스트 (R3 조건 이행)

| 구 W3 spec | 이관처 | 확인 |
|---|---|---|
| §6.1 검증 floor(4 커맨드) | §2.2 | ✔ 전문 |
| §6.3 advisory 계기 | §2.5 말미 | ✔ |
| §8 ledger 법·re-cache 3단계 | §2.4 | ✔ 전문 (ledger 문서 자체는 살아있는 원본) |
| §12 do-not-touch 17항 | §4 (1~17 + 08-05 추가 18·19) | ✔ 전문 |
| §9 parked register | §5 (live 행) | ✔ (사멸 행 명기) |
| §13 재현 블록·환경 | §2.7 + §3 | ✔ 갱신 이관 |
| flock 규약(GPU·ledger) | §2.4 · §2.7 | ✔ |
| 검증 루프(1씬 선행·A/B·freeze) | §2.1~2.3 | ✔ |
| §1 내용 룰링(jitter·species·asset-first 등) | 코드/ledger에 이미 체화 + §4-14·15·19 | ✔ |
| §7 render-gate 계획, §4~5 track/window, §10~11 색인 | **W3 전용 — 이관 대상 아님** | — |

이행 완료 → `w3_execution_spec_v1.md` RETIRED (헤더에 표기, 참조용 보존).
