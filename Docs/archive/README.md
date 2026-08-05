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
