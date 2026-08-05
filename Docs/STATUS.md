# STATUS — W3 마감 · 08-05 독트린 반영 · 갤러리 재작업 대기 (2026-08-05)

직전 판(W2 마감 스냅샷, 07-30)은 git 이력 참조. 이 판 = W3 마감 + 독트린 + 검수 결과.

## 한 줄
**W3(이미지 기반 사실화 개보수) 33/33 완료.** 08-05 독트린(난간 자체가 낙차 단서 —
파손·열화 가드 개념 은퇴) 반영. 갤러리 검수 결과 **수정 요청** → R7 gate 미통과,
GT-57 OPEN → 당면 작업은 `briefs/gallery_fix_plan_v1.md`.

## 읽는 순서 (신규 합류)
1. 이 파일 → 2. `briefs/process_spec_v1.md`(상설 운영 규칙 — 08-05 결재)
→ 3. `briefs/gallery_fix_plan_v1.md`(당면 실행 계획) → 4. `audit_v4/gt_changes_w3.md`(GT ledger)

## 현재 상태
- 라운드: 독트린 6씬 `260805_w3_doctrine` · 나머지 27씬 `260731_w3_full`(구 `_final`에서 개칭 —
  상태 주장 단어 금지) · scene13 선행 수리 3라운드 `260805_w3_s13fix`(GT-58: 연속 가드 + 전장
  캐노피) → `_s13fix2`(GT-59: 계단 캐노피·전주/차단기/도로 맨홀 소거·**공용 킷 P4/P7/P8
  weed·manhole 소거** — 차도 보유 씬의 다음 라운드 FRAME 회귀는 GT-59 귀속) →
  `_s13fix3`(GT-60: 건물형 유리 구조물) → `_s13fix4`(GT-61: 트렌치 난간 0·유리 전장·
  계단부 rail/glass 모드·A103 그림자 이동·A101 평행 판상형) →
  `_s13fix5`(GT-62: 캐노피 전장 연결·높이바 직결·계단부 유리 랩+하행 핸드레일·
  **헤지 실관목 전환**(Privet 31주 — "too shiny to be called a bush" 답변)) — **사용자 검수 대기**
- 헤지 실자산 확산 `260805_w3_hedgeswap`(GT-63: `place_hedge_row` 공용 헬퍼 + 전경 전정
  밴드 8씬 scene02·05·14·15·16·20·N1·N2, 계 444주 — 원경 매스(FarHedge 계열)·scene05
  backdrop_shrub 는 검토-제외, 원장 참조) — **사용자 검수 대기**
- 검수 총평(08-05, 이후 모든 작업의 표준법): ① **배치 품질 우선 — 재질 작업 동결**
  ② 통행 연속성(길은 씬 끝까지, 길 정면 건물 금지) ③ scene04 = 맥락 배치 모범
- `process_spec_v1.md` 결재 완료(R1~R7, R3·R4 조건부) — `w3_execution_spec_v1.md` RETIRED
- Q4 sweep 완료: scene13 남측 결손·scene15 sub-code 정체성 등은 갤러리 재검수 후 제안
- 단서 토글 확장 조사: `surveys/cue_expansion_survey_v1.md` — **계획 전용, 사용자 결재 대기**
  (코드 무수정; 착수는 갤러리 개보수 완료 후)

## 다음
1. `gallery_fix_plan_v1.md` §2 순서: scene10 → 12 롤백 → 01(삭제→railing→광장) → 06 통일
   → 05·14 → 전 씬 continuity pass → ledger 선신고 → 렌더/회귀/갤러리 → **재검수 요청**
2. 재검수 통과 시: GT-57 CLOSED · R4 큐 폐기 확정 · Q4 후보 제안
3. W4 GT 재판정 → W5 hazard-off 팔 + 20k 생산 렌더(~15 h) → 학습 인계
   (씬 번호 재부여 DEFERRED — spec §1)

## 규율
`process_spec_v1.md` §2가 정본. 요지: 커밋 전 검증 floor 4종 green / 씬1렌더→회귀→육안→커밋 /
검증 없는 확산 금지 / 같은 prim A/B / GT 선신고(ledger) / GPU·ledger flock 배타 /
round 명명에 상태 주장 단어 금지 / gallery `--out` 필수.
