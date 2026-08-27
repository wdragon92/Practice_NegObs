# Docs/archive — 종결 기록 보관 (1차, 2026-08-05)

**규칙 하나: 원경로 `Docs/<하위>/<파일>` → `Docs/archive/<하위>/<파일>`.** 파일명은 그대로다.
옛 경로 인용을 만나면 같은 파일명으로 여기서 찾으면 된다 (`grep -r <파일명> Docs/archive/`).

이동 대상은 4-렌즈 검증(스크립트 런타임 의존 · 현행 문서 참조 · 진행 중 웨이브 충돌 ·
선정 타당성)을 전부 통과한 **종결 기록 56건**만이다. 내용 병합·수정 없음 — 위치만 옮겼다.

## 들어있는 것

- `audit_v4/` — v4 세대 전수 감사 4건 + 통합 수정 계획 + **judge v5 판정문 6건** +
  이전 세대 시트 PNG 6장 (scene_overview_v4 · keep15 · 260730_w2d 시트 4장)
- `reports/` — 종결 w2 보고 10건(w2d_edit_g2/g3/gb · translation 3건 · groundkit ·
  materials · pilot_ground · surgeon) + **redteam 14건**(s0710_rebuild 제외 전부) +
  일회성 진단·감사(deadpixel 2 · code_audit_realism · license_audit · doc_consistency ·
  scene_wholeness · fix_small_w1 · t0_spike · lighting_round_impl · leaf_globalization_budget_v2 ·
  const_color_texture_map · multi_scene_completion_report) + realism_compare PNG 2장
- `surveys/` — stair_typology_survey.md (v1 · T1~T8만. **v2는 scene_common §3 수학 정의의
  출처라 현역 잔류**)

## 이번에 옮기지 않은 것 (2차 후보 — 갤러리 개보수 웨이브 종료 후)

검증에서 현역 판정이 나온 파일들. 웨이브가 참조하거나 추기(supersede note)할 수 있다:

- **fixlog 전 계열** — 08-05에 fixlog_VB에 supersede note가 추가된 전례. 대기열 씬
  (01·05·06·10·12·14)의 fixlog들은 추기 대상일 수 있다
- **judge v6·v7·v8** — v6_new7은 scene10/12 코드 헤더의 지배 판정, v7A·v7B·v8은
  regression_check GRAZE 임계값 근거 사슬
- **w2 기반문서 잔류분** — w2c_merge_t1(§7 렌더 인자·§9 round stamp 법) ·
  w2d_round(§3.2 GRAZE 판독 예제) · w2_gate_preflight(§3.4 임계값 근거) ·
  w2_fixbatch(OPEN GT-58이 인용하는 갤러리 복구 명령) · w2_veg_procurement(관목 재검토 대상) ·
  w2_tools · w2d_edit_g1 · w2d_kitfix
- **tonglam_v2** — row 08·10 supersede note 추기 예정(구 spec §X3), 열린 체크리스트가 인용
- **realism_gap_2026-07-28/** — imgstats T1 게이트 근거(ZZ_synthesis §6) + realism_brief 필독
- **era_consistency_survey_v1 · scene_composition_audit · stair_typology_v2** — W4 GT
  재판정·배치 우선 국면의 현역 어휘/근거
- **stair_compliance · scene15_railing_fix · scene01_completion_report · asset_audit ·
  fix_building_kit(GT-12 OPEN) · redteam_s0710_rebuild · lighting_spikes · sky_procurement ·
  real_reference_expansion** — 대기열 씬·열린 ledger 행·라이브 도구가 인용

2차 이동 전에는 위 근거가 해소됐는지(웨이브 종료 · GT-57/58/59 CLOSED · supersede note 착지)
확인할 것.

## 2차 이동 (2026-08-14, 부분)

전 저장소 상호참조 인벤토리(411개 텍스트 파일 전수 grep — `reports/repo_reorg_v1.md`)로
**인용 0 + 활성 큐 씬 무접촉**이 실측 확인된 9건만 이동. 각 파일 헤더에 ARCHIVED 추기.

- `audit_v4/` ← fixlog_N3(s08/12) · fixlog_W0(v6 공통) · fixlog_W2(s07/10) · fixlog_Y1(s09 지붕)
- `reports/` ← w3_cb2_v1 · w3_cb3_v1(batch1 종결) · w3_l12_v1(s12) · w3_p09_v1(s09)
- `briefs/` ← process_revision_proposal_v1.md (SUPERSEDED 스텁 — 정본은 briefs/process_spec_v1.md)

**잔류 유보(큐 접촉)**: fixlog_N1(s06/11)·W3(s13)·W6(s01/09/14)·X2(s06/07/10)·X3(s11/17),
w3_cb4_v1(건물 킷 — 레버4 진행 중), props_audit_w1/C4(s21 재작업 대기). 해당 큐 종료 후 재판정.

## 3차 이동 (2026-08-27, 재편 S5) — `Docs/` 아래 `legacy/` 폴더 폐지

그 폴더(`Docs/` 바로 아래 `legacy/`)는 규칙이 없는 두 번째 보관함이었고, 그 안에 **현행 문서를 가리키는 심링크 2개**
(`multi_scene_brief_v3.md` · `realism_rubric_v1.md`)가 들어 있었다 — "이력 보존" 폴더가 현행을
가리키는 모순. 심링크 2개는 삭제하고, 실파일 5건은 `archive/legacy/` 로 옮겨 보관함을 하나로 합쳤다.
파일명 불변, 내용 무수정. 원장: `Docs/reorg_0827/docs_moves.tsv`.

- `legacy/nanobanana_batch1_geometry_map.md` — 배치1 12씬의 기하 역추정·빌더 매핑 원본(07-27).
  N/C/D 시리즈 원 스펙의 출처라 `critique_intent_map_v1.md` 가 다수 인용한다
- `legacy/scene_redesign_v5_proposal.md` — 본편 21씬을 "범용 무대 × 기하 변형 × 위험"으로
  갈아엎은 v5 재설계 제안(07-27). 현행 21씬 구성의 근거
- `legacy/scene_library_v3_status.md` — v5 이전 v3 라이브러리 21씬 상태 보고(07-25). 이력
- `legacy/STATUS_pre_p4.md` — P4 이전 STATUS 스냅샷(07-28). 이력
- `legacy/STATUS_pre_reorg_260814.md` — 08-14 문서 재편 직전 STATUS 원문 보존본. 이력

옛 인용(`Docs/` + `legacy/<파일>`)은 전부 `Docs/archive/legacy/<파일>` 로 갱신했다 —
저장소 전체에 남은 옛 표기는 0이다(`os.walk` 실측, 08-27).
