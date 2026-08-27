# 저장소 문서·디렉터리 재편 v1 (2026-08-14)

> 계기: 사용자 지시 — "문서가 여러 세션 거치며 뒤죽박죽 … 디렉터리 구조랑 각 내용물들
> 최대한 깔끔하게 정리". 근거: 전 저장소 상호참조 인벤토리(411개 텍스트 파일에서 `Docs/...`
> 인용 378종 전수 grep — Opus 1기, 08-14).
> 원칙: **코드·씬·킷 무수정**(단 `scripts/make_overview.py` 출력 경로 1줄 정정) ·
> 원장(append-only)과 그 인용 경로 불변 · 룰링 원문 보존(추기만, 개서 없음).

## 1. 무엇을 했나

### 1.1 호환 심링크 9종 (Docs/ 최상위 + surveys/)
과거 문서 이동 때 코드 인용을 안 고쳐 **이미 깨져 있던 경로들**을 심링크로 복구.
INDEX 구판이 "심링크가 있다"고 주장했으나 실제로는 없었다 — 주장을 사실로 만드는 방향.

| 심링크 (`Docs/` 아래 파일명) | 실경로 | 깨져 있던 인용처 |
|---|---|---|
| `multi_scene_brief_v3.md` | `briefs/` | archive_v3 7씬 + 8씬 = 15파일 |
| `multi_scene_brief_v2.md` | `briefs/` | scene_common(+심링크 2)·scene02/03/04·다운로더 |
| `nanobanana_batch1_geometry_map.md` | `legacy/` | **batch1 12씬 전부** + 다운로더 |
| `scene01_design_brief.md` | `briefs/` | scene01("the only spec")·다운로더 |
| `stair_typology_survey_v2.md` | `surveys/` | scene_common:2514(+심링크 2) |
| `scene_redesign_v5_proposal.md` | `legacy/` | scene07/10/12 + fixlog N1~N4 |
| `realism_rubric_v1.md` | `reports/` | (INDEX 주장 정합화) |
| `surveys/real_reference_expansion.md` | `../reports/` | `scripts/harvest_refs.py:8` |

> **2026-08-27 추기 (S5 재편).** 위 8개 심링크는 **전부 삭제됐다.** 08-14에는 "코드를 안 고치고
> 깨진 인용을 살린다"가 옳았지만, 그 결과 현행 코드가 옛 경로로 현행 문서를 가리키는 상태가
> 1년치 문서에 굳었다. 08-27 재편에서는 반대로 **인용 47파일 62곳을 실경로로 고치고 심링크를
> 없앴다** — 경로 하나에 답 하나. `legacy/` 는 `archive/legacy/` 로 접혔으므로 위 표의
> `legacy/` 행 2건은 지금 `archive/legacy/` 다. 원장: `Docs/reorg_0827/docs_citation_edits.tsv`.

### 1.2 scripts/ 정돈
- 완료 체인 **17건 → `scripts/rounds/`**: run_finalize_v3 · run_partial_r4 · run_scene19_r5 ·
  run_r2_queued · run_render_batch1_r1~r4 · run_smoke_batch1 · run_v5_keep_rt · run_v7_all_rt ·
  run_v7_pt13 · run_v8_fix8_rt · run_v8_pt7 · run_v8_rt2_scene09 · reorg_scenes_main(1회성).
  전부 07-27 산출·rounds/ 에 같은 날 형제 존재(이동이 시작됐다 중단된 상태였음).
- **`run_v6_all_rt.sh` 삭제** — `run_v7_all_rt.sh` 와 md5 동일(9a7ab694…)한 완전 중복.
- 경로 인용 4곳 동반 갱신: `props_audit_w1/C3:24` · `fixlog_Y1:216` · `cleanup_lookcheck_v1:401` ·
  `legacy/scene_library_v3_status:40`(이미 깨져 있던 것 포함).
- `make_overview.py` 출력 경로를 archive 실위치로 정정(구경로는 08-05 이동으로 이미 불일치).

### 1.3 아카이브 2차 이동 9건 (부분 — archive/README 게이트 준수)
인용 0 실측 **그리고** 활성 큐 씬 무접촉이 확인된 것만. 각 파일 헤더에 ARCHIVED 추기(원문 불변).
- fixlog N3(s08/12)·W0(v6 공통)·W2(s07/10)·Y1(s09) → `archive/audit_v4/`
- w3_cb2·w3_cb3(batch1 종결)·w3_l12(s12)·w3_p09(s09) → `archive/reports/`
- process_revision_proposal_v1(SUPERSEDED 스텁) → `archive/briefs/`
**유보(큐 접촉)**: fixlog N1·W3·W6·X2·X3, w3_cb4(레버4), props C4(s21) — 큐 종료 후 재판정.

### 1.4 문서 재작성 2건 + 신설 3건
- `STATUS.md` — 3중 적층(08-11/08-13/08-14 1·2판)을 현행 단일판으로. 직전 원문은
  `legacy/STATUS_pre_reorg_260814.md` 스냅샷(추기 헤더만). 큐 항목·룰링은 전량 승계(원문 강도 유지).
- `INDEX.md` — 실제 트리 반영: 누락 색인 15+건 추가(critique_intent_map 은 STATUS 필독인데
  색인 부재였음), 유령 서술 정정(캠퍼스 참고사진 2장→1장, 실재하지 않던 심링크 주장),
  이동 금지 앵커 명시(placement_rules·원장 인용 48경로·_dimension_index·run_p2_all33).
- 신설: `scene_audit_realism_survey_v1.md` + `scene_audit_findings_v1.json`(08-14 전수 감사),
  본 문서.

### 1.5 기타
- `.gitignore` 용량 주석 실측 정정(12→33GB) · README 구조 절 정정(루트 run_p2_all33 은 상설
  드라이버 — "진행 중 체인" 서술이 실제와 어긋났음) · `__pycache__` 6곳 삭제(재생성물).

## 2. 이동 금지 앵커 (재편에서 의도적으로 손대지 않은 것)

1. `briefs/placement_rules_v1.yaml` — `placement_lint.py` 가 실행 경로로 읽음(검증 floor 입력).
2. `audit_v4/gt_changes_w3.md` 와 그것이 인용하는 48경로(regr json 26·보고서 17·크롭·사양) —
   append-only 원장의 재현성 증거.
3. 상설 렌더 드라이버 `scripts/rounds/run_p2_all33.sh` — 08-14 당시에는 **저장소 루트**에 있었다.
   `s04_quality_gap_survey_v1.md:690` 이 **`:36` 줄 번호**로 인용하므로 앞에 줄을 추가하는 수정도 금지.
   > **2026-08-27 추기.** 이 앵커는 **해제됐다.** 파일은 `scripts/rounds/run_p2_all33.sh` 로 옮겼다.
   > 금지 사유였던 줄 번호 인용(`:36` 등)은 **파일 내용을 한 줄도 늘리지 않았으므로 그대로 유효**하다
   > (87줄, 사용법 주석의 경로 표기 3곳만 새 경로로 고침). 이 드라이버를 실행하던
   > `scripts/rounds/run_260816_w4_final33.sh:5` 도 같은 줄에서 새 경로를 부르도록 고쳤다.
4. `briefs/w3_execution_spec_v1.md`(RETIRED) — 코드 9곳 + 원장이 조문 인용. 위치 불변.
5. `surveys/_dimension_index.md` — 킷 4종(+심링크)이 인용.
6. look_check(33GB)·dataset(846MB) 미추적 생성물 — **삭제 없음**(§5 판정 대기).

## 3. 유령 인용 대장 (이번에 고치지 않은 알려진 공백 — 기록만)

- `w3_l14_v1.md` — scene14 가 3곳 인용하나 **git 이력에도 없음**. 산출물(`_w3_l14_crops/` 7.9MB ·
  `regr_260731_w3_l14.json`)만 존재 = L14 레인 보고서 미작성. 유사: `w3_l05_v1.md`.
- `material_audit_realism_v1.md`(3곳 인용)·`t1_material_gate_v1.md`·`tonglam_v3.md`·
  `s13_canopy_railfix_v1.md`·`Docs/CORRECTIONS.md` — 부재. 인용측이 전부 보고서·구스펙이라
  실행 영향 없음.
- `briefs/scene01_design_brief.md` 가 인용하는 `Docs/everytime-1784886395380.jpg` 부재
  (INDEX 의 "참고사진 2장"이 이것 — 1장으로 정정함).
- `Docs/reference_photos/quarantine/` — gitignore 규칙만 남고 디렉터리 부재(규칙 잔재).

## 4. 검증

- 심링크 8종 해석 확인(`test -r`) · 이동 후 `git status` 리네임 추적 확인 · md5 중복 확인 후 삭제.
- 커밋 floor: `py_compile`(touched py) · `geom_invariance_check.py` · `placement_lint.py` —
  결과는 커밋 메시지에 기록.

## 5. 판정 대기 (본 재편이 열어 둔 것)

1. **look_check 33GB** — `_experiments/` 8.4GB(단일 최대)·구 라운드류. 검수 대기 갤러리
   (`_review/` 42라운드)는 보존 필수라 **일괄 삭제 불가** — cleanup_lookcheck_v1 규약대로
   선별 정리할지 판정 필요.
2. **dataset/ 846MB**(run 11개) — manifest 로 재현 가능. 정리 여부.
3. 유보한 아카이브 후보(fixlog 5·w3_cb4·props C4) — 해당 큐 종료 시 2차 이동 재판정.
4. `scripts/rounds/` 내부의 구식 명명 5건(run_batch1_ctx* 등) 개명 여부 — 스탬프·로그가
   구명을 인용하므로 **개명하지 않는 쪽을 권고**(기록만).
