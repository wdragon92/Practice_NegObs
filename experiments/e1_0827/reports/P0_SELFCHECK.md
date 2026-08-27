# P0_SELFCHECK — 자기 검산 7문항 자답

- 작성 2026-08-28 · 근거: `Docs/briefs/edge_relabel_brief_v6.md` §2 (자기 검산 7문항) · Phase 0 항목 5
- 규칙: 답만 적지 않는다. **답마다 "그 답을 실제로 만들어 내는 코드 경로"와, 가능한 경우 스모크 3프레임의 실측 수치**를 붙인다.
  코드가 그렇게 동작하지 않으면 그건 자답이 아니라 희망이기 때문이다.

---

## 0. 승용 요약 (5문장)

1. 7문항 **7/7** 자답했고, 전부 코드의 특정 함수 한 줄까지 짚어 두었다.
2. 가장 중요한 함정(Q6 자기가림)은 **이름으로 짐작하지 않는 구조**로 막았다 — 가림 prim 분류표를 비워서 배포했고,
   분류가 안 되면 `occluder.flag = null` 로 남기고 미해결 목록으로 보낸다.
3. 그 결과 스모크에서 실제로 잡힌 가림 prim 은 3개다: `/World/Scene01/UpperPlaza`(184표본) · `/World/Scene03/Bollard_0`,
   `Bollard_1`(각 7표본). 앞의 것은 브링크(=E), 뒤의 둘은 볼라드(=H)로 **보이지만**, 그 판정은 승용 결재다(❓B-4).
4. Q5(V/E 경계)는 코드 차원에서 못 하게 막았다 — `tier_final` 이 비어 있지 않으면 검증기가 그 레코드를 **불합격 처리**한다.
5. Q3(NEG)은 스모크에서 실제로 나왔다: scene02 = `tier_now NEG`, edges 0.

---

## Q1. 가드레일 틈으로 구멍이 조금 보인다 → ?

**답: H_cand.** 그리고 **보이는 부분은 원시 기록으로 그대로 남긴다.**

- 왜: 티어를 가르는 질문은 "왜 안 보이는가"다. 가리는 물체가 있으면, 조금 비치든 말든 H다(§2 표 H행 "틈새로 속이 일부 비쳐도 H").
- 코드 경로:
  - `e1_visibility.visibility_of()` 가 점마다 `visible / blocked / no_surface` 를 나눈다.
  - `e1_visibility.occluder_of()` 가 `blocked` 점이 찍힌 픽셀의 prim id 를 `idseg` 사이드카에서 읽고,
    승인된 규칙으로 `external` 이 하나라도 나오면 `flag = True` + `occl_frac = 외부에 막힌 점 / 화면 안 점`.
  - `e1_schema.derive_tier_now()` 가 `any(flag is True)` → `H_cand` (§5 문면 그대로).
  - 보이는 부분은 같은 인스턴스가 `e1_geometry.visible_runs()` 로 `polyline_px` 에 남고, 속 마스크도 그대로 계산된다
    — **라벨층이 티어에 따라 달라지지 않는다**(§2 공통 규칙).
- 지금 상태: 규칙표가 비어 있어(❓B-4) 스모크에서는 `flag = null` 이다. 즉 **아직 H_cand 를 찍지 않는다.**
  대신 `unresolved_occluders.txt` 와 `prim_blocker_census.json` 에 원자료를 남긴다.

## Q2. 선만 보이고 다음 칸은 안 보인다 → ?

**답: VE_raw 로 원시 기록.** 문턱이 채택되면 E로 확정될 가능성이 높지만, **지금 가르지 않는다.**

- 코드 경로: `e1_geometry.route_a()` 가 보이는 edge 점이 있으면 인스턴스를 `kept` 에 넣는다 →
  `int_area_px` 는 0 이 되고(`e1_geometry.mask_stats`), 가림이 없으면 `derive_tier_now` 가 `VE_raw`.
- 실측(이 케이스가 스모크에 실제로 있다): `scene01` 컷0 의 **e00** — `dist_m` min 3.29 / median 3.45 m,
  `int_area_px = 0`, `int_h_px = 0`, `int_w_px = 0`, `(a)–(b)` 이탈 mean 0.90 / median 1.00 / p90 1.00 px,
  `occluder.flag = False`. 선은 잡혔고 속은 0인, 교과서적인 E 후보다.

## Q3. 낙차가 프레임 밖에 있다 → ?

**답: NEG.** 단, 이 골격에서 NEG 는 "가시 edge 길이 0 **그리고** 보이는 속 픽셀 0"이라는 계산 결과다(§2 규칙 2).

- 코드 경로: `route_a()` 는 `n_visible > 0 or int_area_px > 0` 인 인스턴스만 `edges[]` 에 넣는다 →
  하나도 없으면 `edges[]` 가 비고 `derive_tier_now` 가 `NEG`.
- 실측: `scene02` 컷0 = `tier_now NEG`, edges 0.
  ⚠ **다만 이 NEG 는 정직하게 말해 틀린 NEG일 수 있다.** scene02 는 화면에 지하도 구덩이가 명백한데,
  그 씬 높이장의 `z_min` 이 **−0.0136 m** 라 route (a) 가 볼 낙차 자체가 없다(AABB 포락면이 개구부를 덮었다).
  "프레임 밖이라 NEG"와 "높이장이 못 봐서 NEG"를 구분하는 것이 ❓B-1 이다.
- 프레임 안이지만 **전부 가려서** 아무것도 안 보이는 경우도 이 규칙상 NEG 가 된다. 그런 인스턴스는 버리지 않고
  `notes.diag.blocked_only_instances` 에 가림 prim 과 함께 남긴다(스모크 실측: scene01 1건, scene03 36건).
  이걸 H_cand 로 볼지 NEG 로 둘지는 ❓B-8.

## Q4. edge 라인의 절반만 수풀에 가려졌다 → ?

**답: 보이는 구간은 원시 기록 + H_cand 표시.** 최종 티어는 브리프 §9-❓1(승용 결재).

- 코드 경로: 가시성 판정이 **점 단위**라, 한 인스턴스가 화면에서 여러 토막으로 끊긴다 →
  `polyline_px` 를 **"가시 구간들의 목록"**(list of runs)으로 저장한다. 평평한 점 목록 하나로 저장하면
  가려진 구멍을 선으로 이어 버려서, 나중에 "여기는 안 보였다"를 복원할 수 없다.
- 가려진 비율은 `occl_frac` 으로 그대로 실측된다(외부 가림 점 / 화면 안 점) — §7 가림축 실험의 입력이 이 값이다.
- 우리는 최종 티어를 찍지 않는다: `tier_final` 은 항상 `""`.

## Q5. V/E 경계 픽셀 수를 네가 정해도 되는가 → ?

**답: 아니오.** §3-P1.

- 코드에 그 계산 자체가 없다. `int_area_px / int_h_px / int_w_px` 는 **원시 수치로 저장만** 하고,
  어떤 모듈도 그 값을 **크기 문턱과 비교하지 않는다.** `grep -n "int_area_px" code/*.py` 를 돌리면 비교는 전부 `> 0`(존재 여부)뿐이다 — `e1_geometry.route_a`(인스턴스를 남길지), `e1_label_frame`(마스크 PNG 를 쓸지), `e1_schema.validate`(면적 0 인데 마스크 경로가 있으면 불합격), `e1_overlay`(윤곽을 그릴지).
- 강제 장치: `e1_schema.validate()` 에 `tier_final must stay empty until G3 (§5)` 규칙이 있다.
  누가 나중에 V/E 를 찍어 넣으면 그 레코드는 **검증에서 떨어진다**.
- 이 원칙은 상수 전체로 확장돼 있다: `code/e1_selftest.py --scan-consts` 가 e1 코드의 모든 수치 리터럴을 훑어서
  대장에 없는 상수 **0건**임을 매번 재측정한다.

## Q6. 계단 앞 지면(브링크)에 가려 다음 칸이 안 보인다 — 가림물인가 → ?

**답: 아니오. 자기가림 = E의 정의다. H_cand 아니다.**

- 이 문항이 구 라벨러를 죽인 함정이고, 이 골격에서 **가장 조심해서 설계한 지점**이다.
- 코드 경로: `occluder_of()` 는 막은 물체의 **prim 경로**를 읽고, `PrimClassifier` 가
  `self`(지면·계단·위험 기하 = 가림 아님) / `external`(가림물 = H) / `unknown` 으로 나눈다.
  `self` 만 나오면 `flag = False`(=가림 없음), `external` 이 하나라도 있으면 `flag = True`.
- **그런데 그 분류표를 우리가 채우지 않았다.** `code/prim_class_rules.json` 은 `rules: []` 로 비어 있다.
  이름에 'plaza' 가 들어가면 지면일 것 같다는 식의 추정이 바로 P1 위반이기 때문이다.
  분류가 안 되면 `flag = null`, `prim` 에 실제 경로를 적고, 프레임을 미해결 목록으로 보낸다.
- 실측(=승용이 결재할 원자료): 스모크에서 실제로 시선을 막은 prim 은 셋뿐이다.

  | prim 경로 | 막은 표본 수 | 우리 짐작(채택 아님) |
  |---|---:|---|
  | `/World/Scene01/UpperPlaza` | 184 | 브링크로 보인다 → `self` 후보 |
  | `/World/Scene03/Bollard_1` | 7 | 볼라드 → `external` 후보 |
  | `/World/Scene03/Bollard_0` | 7 | 볼라드 → `external` 후보 |

  이 표가 그대로 ❓B-4 다. 승용이 `self`/`external` 을 찍어 주면 규칙표에 넣고 재실행한다.

## Q7. 창고 렌더 프레임을 계단 corpus(E 라벨 본대)에 넣어도 되는가 → ?

**답: 아니오.** §7 전용이고 매니페스트가 따로다(브리프 §9-❓6).

- 코드 경로: 레코드에 `domain ∈ {stair, warehouse}` 가 필수 필드로 있고(`e1_schema.validate` 가 값 검사),
  `e1_schema.MANIFEST_STEM` 이 도메인 → 파일 이름을 고정한다:
  `stair → edge_manifest_v1.{json,csv}` · `warehouse → vth_manifest_v1.{json,csv}`.
- `e1_run.py` 는 실행의 `--domain` 으로 파일 이름을 **고르지 않고 결정**하며, 한 매니페스트에 두 도메인이 섞이면
  `[e1] ! frames from more than one domain in one manifest` 를 인쇄한다.
- 현재 Phase 0 산출물은 전부 `domain = stair` 다(스모크 3프레임).

---

## 결재란

| 번호 | 항목 | 담당 |
|---|---|---|
| ❓B-4 | 위 Q6 표의 3개 prim 을 `self` / `external` 로 확정 (→ `prim_class_rules.json`) | 승용 |
| ❓B-8 | 프레임 안이지만 **전부 가려진** 인스턴스(scene01 1건 · scene03 36건)를 NEG 로 둘지 H_cand 로 올릴지 | 승용 |
| 브리프 §9-❓1 | edge 일부만 가려진 혼합 프레임의 최종 티어 (지시는 "원시 기록 + H_cand 표시"까지) | 승용 |
