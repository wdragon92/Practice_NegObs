# T1 재질층(표면 미세구조) 실행 사양 **v1.1**

작성 2026-07-29 · 개정 2026-07-29 · NegObs 사실화 W1 · MDL `assets/NegObsGround.mdl` v1.8.0
대상 코드 `scene_common.py` @ **`c751acd` + 미커밋 작업트리**(병행 에이전트가 `VEG_DEBRIS oakfall2`·
창 리세스 2건을 수정 중 — 본 개정이 인용한 `LOOK_V1` 24개 행번호는 **개정 시점 작업트리에서 재검증
완료·전부 불변**이나, 행번호는 스냅샷이며 **정본은 §1.7.2 의 R-5 어서션**이다)
전제 문서: `Docs/surveys/realism_gap_2026-07-28/ZZ_synthesis.md` §1·§6·§10 / `Docs/reports/realism_phase1.md` /
`Docs/reports/realism_phase2.md` / `Docs/reports/realism_v1_final.md` / `Docs/reports/const_color_texture_map.md` /
`Docs/reports/redteam_verification_v1.md` / `Docs/audit_v4/fixlog_X1.md`
**v1.1 신규 전제**: `Docs/reports/redteam_w1_design.md` §2.5·§2.6·§2.7·§3·§5·§8 /
`Docs/reports/t0_spike_report_v1.md` §1·§2·§5 / `Docs/briefs/ground_kit_spec_v1.md` §1.2·§4.4·§9.3 /
`Docs/surveys/props_audit_w1/B_groundcover_debris.md` §8·§10-b·§12

모든 수치에 근거 태그. GPU·렌더·Isaac 미실행 — 기존 PNG 판독 + numpy/PIL + 정적 분석 + 공개 API 조회만.

## 개정 이력

| 판 | 일자 | 변경 | 사유 |
|---|---|---|---|
| v1 | 2026-07-29 | 최초 | — |
| **v1.1** | **2026-07-29** | **9건 개정**(아래) | 레드팀 반증 3건 + T0 스파이크 실측 5건 + ground_kit 이관 4건 |

**v1.1 변경 목록** — 각 항목은 본문에 `[v1.1]` 로 표시된다.

| # | 절 | 변경 | 근거 |
|---|---|---|---|
| R1 | §1.7 | **"기하 8곳 열거" 방식 폐기.** `LOOK_V1` 참조 **24건 전수 분류표**(§1.7.1) + "치환 후 잔존 `LOOK_V1` 참조 0" 어서션으로 대체. 누락 2곳(`:2143` 창 행 상한 · `:2187` 저층 파사드 킷) 편입 | `redteam_w1_design.md` §2.5 · 본 개정 [실측] 재검증 |
| R2 | §1.2·§3.1·§3.4 | **`macro%`/`hf%` 지표 정의를 재현 가능하게 재작성** + 측정기 `scripts/norm_spec.py` 사양 신설. 문턱 재캘리브레이션. **v1 의 macro%/hf% 수치는 전부 폐기** | 동 §2.6 (6개 변형 전부 재현 실패) · 본 개정 [재현] |
| R3 | §0 | `r2_on` 라운드 **1,529컷 → 452컷** 수치 정정 | 동 §2.7 · 본 개정 [실측] `ls look_check/*/r2_on/*.png \| wc -l` = 452 |
| G1 | §1.8① | `_ground_skin` **P-A 스위치**(`SKIN_EXCLUDE`/`skin_exclude`) 수용 | `ground_kit_spec_v1.md` §1.2·§9.3 (차단 항목) |
| G2 | §1.8②·§5.2 | `plaza_light` **`scale_m` 교정** 수용 — 톤 ×0.72 와 **동시 적용·동시 재렌더**(9씬) | 동 §4.4·§9.3 |
| G3 | §1.8③ | MDL 에 **`unit_cell_m`·`unit_albedo_sigma`(0.10)·강조유닛 7 %** 입력 추가 | 동 §4.4 ("전 포장 프로파일 σ_LF 주성분") |
| G4 | §1.8④·§2.1 | `LOOK_CLASS["veg"]["tex_alts"]` 에서 **`leaf_ground` 제거** + `grass` 텍스처 **1.4 m 교체** | `B_groundcover_debris.md` §8(24씬 가을 낙엽 오염)·§12 A1·A2 |
| T1 | §6·§7 | **게이트 지표를 `flat%` → `flat_gnd`(하단 2/3)** 로 전환. `flat%` 개선은 하늘 가림으로 달성 가능 | `t0_spike_report_v1.md` §1.3 [실측] |
| T2 | §7.2 | **A/B 기준선 교체** — `leaf3d` 는 `LOOK_V1=1` 렌더였다. 기준선은 `look_check/_t0_spike/c2_A_base/` 규약 | 동 §1.5 [실측] |
| T3 | §7.5 | **MDL 비용 실측 +13~55 %** 를 파일럿 예산에 반영. 렌더 프로파일 **`NEGOBS_PT_FAST=1`**(0.95 s/컷) | 동 §1.7·§5.1 [실측] |
| T4 | §6.1 | **베벨 GO** — 단 A/B 는 **같은 프림·셰이더 입력 토글만**. 재질 클래스별 반경 사양 명문화 | 동 §2.2·§2.3 [실측] (위치 다른 A/B 는 +44 LSB 허위효과) |
| T5 | §6.2·§7.3 | **MDL 적용 대상 원칙 = "h0.3 프레임을 실제로 채우는 표면"**(어느 재질이냐가 아니다). 파일럿 3씬을 이 원칙으로 재검증 | 동 §1.4 [실측] (sceneC2 효과 0 = 식생 지배 프레임) |

---

## 0. 착수 전 정정 — 임무서의 전제 2건이 이미 낡았다

| 임무서 전제 | 실태 | 근거 |
|---|---|---|
| "해법(NegObsGround.mdl)은 저장소 안에 있는데 **33씬 중 0곳 사용**" | **이식 완료**. `NEGOBS_LOOK_V1=1` 이면 지면 10클래스가 전부 이 MDL 을 경유한다 | [실측] `scene_common.py:975-1018`(분기) · `:1099-1204`(`_make_ground_pbr`) · **r2_on 라운드 452컷**이 이 경로로 렌더됨 `[v1.1 R3 정정 — v1 의 "1,529컷"은 출처 불명. `ls look_check/*/r2_on/*.png` = **452**, `look_check/*/*_on/*.png` 전체 합산도 814]` |
| "`NegObsGround.mdl` **438줄**" | **787줄 / v1.8.0**. 웨더링 18파라미터·상수색 모드·`patch_mix`·`round_edges` 가 이미 들어 있다 | [실측] `wc -l assets/NegObsGround.mdl` = 787 · 헤더 v1.6.0 이력 · `anno::version(1,8,0)` |
| 임무서 (4) "절차 웨더링 마스크(약 30줄)" | **구현 완료**(v1.6.0). 단 4마스크 중 **2개(grime·splash)가 치명 C4 로 전면 비활성** 상태 | [실측] `NegObsGround.mdl:428-506` · `scene_common.py:215-229` 주석 |

→ **이 문서는 "이식 계획"이 아니라 "이식된 층의 결손 보수 + 확장 사양"이다.** 남은 결손은 5건이고,
그중 **1건(디테일 노멀)은 33씬 전 지면에서 설정이 죽어 있다** — 아래 §1.1.

---

## 1. 이식 경로 — 현행 구조와 결손 5건

### 1.0 현행 데이터 흐름 [실측 · 코드 정독]

```
씬 파일(33개, 무수정)
  └ sc.make_pbr(stage, f"{ROOT}/Looks/<Name>", diff=..., diffuse_color=..., …)
      └ LOOK_V1 && !uv_mode && !emission  →  _look_spec(path)  # 경로 이름 → 클래스
          ├ [ground 클래스 + 텍스처]      → _make_ground_pbr(...)            # NegObsGround.mdl
          ├ [ground 클래스 + 상수색]      → _promote_const_to_texture() 성공 → _make_ground_pbr(텍스처 승격)
          │                                실패 → _make_ground_pbr(base_color 상수색 모드)
          └ [omni 클래스]                → OmniPBR + round_edges + detail_normalmap_texture
```

역할 분류기는 정확일치 → 접미변형 → 키워드 규칙 → `misc` 4단이며, 33씬 `Looks/` 이름 **663개(중복 포함
클래스 배분 완료, 미상 `misc` 3종뿐)** 를 흡수한다 [실측 — 33씬 정적 스캔, §2.1 표].

### 1.1 결손 ① (최우선) — 디테일 노멀이 지면 10클래스에서 **설정만 있고 코드 경로가 없다**

`LOOK_CLASS` 는 `paving/concrete/brick/stone/soil/gravel/asphalt/nosing/curb/snow` 10클래스에
`detail=True` 를 달아 두었다 [실측 `scene_common.py:238-294`]. 그런데 이 10클래스는 전부 `mdl="ground"` 이고,
`make_pbr` 는 ground 분기에서 **`_make_ground_pbr` 로 즉시 `return`** 한다 [실측 `:980`·`:999`·`:1007`].
`detail_normalmap_texture` 를 바인딩하는 코드는 그 `return` **뒤**에 있는 OmniPBR 블록뿐이다 [실측 `:1084-1090`].
그리고 `NegObsGround.mdl` 에는 **디테일 노멀 입력이 아예 없다**(787줄 전수 — `detail` 문자열 0건).

⇒ **33씬 지면·구조물 전부에서 `detail=True` 는 죽은 설정이다.** 실제로 걸리는 곳은
`metal`·`wood` 중 **텍스처를 가진 호출**뿐이다(상수색 금속은 `diff is None` 이라 `:1084` 조건 탈락).

이건 단순 누락이 아니라 **ZZ §6 T1-3 "detail_normalmap 즉시 사용 [로컬검증됨]" 항목이 프로덕션에
도달하지 못했다**는 뜻이다. Phase1 E3 이 "OmniPBR 전용 기능이라 MDL 쪽엔 없다(§4에서 처방)" 라고
적고 처방을 미이행한 채 닫혔다 [실측 `realism_phase1.md:99-102`].

### 1.2 결손 ② — 현행 디테일 노멀 소스가 "디테일"이 아니다

`_DETAIL_NOR = assets/scene01/concrete_wall_nor_dx.jpg` [실측 `:176`], 8 cm 주기·`detail_bump_factor 0.45`.

> **[v1.1 R2 — 지표 재정의]** v1 의 `macro%`/`hf%` 열은 **폐기한다.** 레드팀이 v1 이 적은 방법
> ("네이티브 1024² 중앙 크롭·창함수 FFT·방사평균·f<f_nyq/32 파워비")을 그대로 **6개 변형으로
> 재현 시도해 전부 실패**했고(파워비 4.1 vs 주장 39.8 등), 측정기 `scratchpad/norm_spec.py` 는
> 세션 소멸로 부재다 [레드팀 `redteam_w1_design.md` §2.6]. 아래 표는 **§3.4 에 새로 고정한 정의**로
> 본 개정이 재측정한 값이다. `slope_n`·`RMS` 는 v1 과 소수점까지 일치(재현 성공)하고,
> `macro%`·`hf%` 만 새 정의값이다.

노멀맵 접선성분(R,G) 스펙트럼 — **§3.4 고정 정의**로 재측정:

| 맵 | 해상도 | slope_n | **macro%**(1≤r<N/32) | hf%(N/4≤r≤N/2) | **접선 RMS** |
|---|---|---:|---:|---:|---:|
| **`concrete_wall_nor_dx` (현행)** | 4096² | **−0.71** | 4.1 | 18.9 | **0.056** |
| `concrete_floor_nor_dx` | 4096² | −1.09 | 5.8 | 8.8 | 0.304 |
| **`plaster_nor_dx`** | 4096² | **−0.89** | **3.9** | 16.6 | **0.159** |
| **`asphalt_nor_dx`** | 4096² | **−0.66** | **3.2** | 13.3 | **0.294** |
| `gravel_nor_dx` | 4096² | −1.39 | 6.2 | 6.2 | 0.546 |
| `dirt_park_nor_dx` | 4096² | −1.07 | 8.7 | 27.7 | 0.270 |
| `granite_dark_nor_dx` | 4096² | −1.19 | 6.4 | 10.3 | 0.093 |
| `metal_rust_nor_dx` | 4096² | −1.54 | 11.9 | 5.7 | 0.167 |
| `sandstone_nor_dx` | 4096² | −1.52 | 16.7 | 11.6 | 0.157 |
| `snow_nor_dx` | 4096² | −1.83 | 31.0 | 11.2 | 0.495 |
| `wood_dark_nor_dx` | 4096² | −1.85 | 26.3 | 12.7 | 0.202 |
| `paving_interlock_nor` | 2048² | −1.98 | **52.3** | 4.8 | 0.449 |
| `stone_worn_nor_dx` | 4096² | −2.32 | 49.1 | 2.8 | 0.428 |
| `marble_light_nor_dx` | 4096² | −2.45 | 47.6 | 4.8 | 0.036 |
| `stone_flag_nor_dx` | 4096² | −2.46 | **58.4** | 2.5 | 0.192 |
| `brick_red_nor_dx` | 4096² | −2.61 | **80.3** | 2.6 | 0.371 |

[실측 2026-07-29 · 재현 절차 §3.4 · numpy+PIL · GPU 0 · N=1024 중앙 크롭 · 리샘플 0]

**정의를 바꾼 결과 순위가 한 곳에서 뒤집혔다(정직 고지)**: v1 은 `concrete_wall`(39.8)을
**매크로 최악**으로 지목했으나, 고정 정의에서는 **4.1 로 오히려 최저군**이다. 레드팀이
"순위는 모든 변형에서 보존" 이라 적은 것과도 다르다 — 본 개정의 변형(창 가중 평균 제거 +
링 총합 가중 정규화)에서는 보존되지 않는다. **결손 ②의 결론은 그래도 유지된다**: 근거가
"매크로"에서 **"진폭"** 으로 바뀔 뿐이다.

따라서 결손 ②의 사유를 **정정**한다:
1. **너무 약하다 (주 사유 — 유지)** — 접선 RMS 0.056 은 라이브러리 내 최저군이며
   `asphalt`(0.294)의 **1/5.3** [재현 — 레드팀이 소수점까지 독립 재현].
   여기에 `detail_bump_factor 0.45` 가 곱해지면 실효 섭동은 0.025 = 기울기 약 1.4°. **보일 수 없다.**
2. ~~매크로가 40%~~ → **[v1.1 철회]** 고정 정의에서 `concrete_wall` 의 macro 는 4.1 이다.
   매크로 격자 논거는 이 맵에 대해 **성립하지 않는다.** (그 논거가 실제로 성립하는 맵은
   `brick_red` 80.3 · `stone_flag` 58.4 · `paving_interlock` 52.3 = **모듈형 타일 맵**이며,
   §3.1 의 `macro%` 게이트는 그것들을 걸러내는 것이 진짜 역할이다.)
3. **대신 신규 사유** — `slope_n −0.71` 자체는 나쁘지 않으나 **RMS 가 문턱(0.12) 아래**라
   `detail_rough_gain` 을 얹어도 회복 불가다. 교체 판정은 **RMS 단독으로 이미 확정**이다.

부수 지적: `metal` 클래스(115종·31씬)에 **콘크리트 벽 그레인**이 얹힌다 — 재질 정체성 오류다 [실측 `:1084`].

### 1.3 결손 ③ — 헥스 타일링 부재 · 모듈형 포장에 반복파괴가 0이다

`patch_mix`(90° 회전 패치 혼합)는 모듈 방향성을 부수므로 `paving/concrete/brick/nosing/curb` 는
**0.0 으로 꺼져 있다** [실측 `LOOK_CLASS`]. 이 5클래스가 지면 프레임의 주력이다.
즉 **가장 넓은 표면에 반복 파괴가 macro 변조(파장 14 m)와 tri_dither(0.15 m)뿐**이고,
타일 주기(1.0~1.5 m) 대역에는 **아무 것도 없다**.

육안 확인(h0.3 판정 시점, 필수 3컷 열람 완료):
`look_check/scene19/r2_on/pt_noon_preset_h0.3_d2.png` — 동일한 균열 문양이 세로줄로 **등간격 반복**한다.
`look_check/scene01/r2_on/pt_noon_preset_h0.3_d5.png` — 같은 증상(같은 `plaza_light` 텍스처).
Phase1 §4.3 이 "헥스 타일링은 patch 혼합과 중복이라 강등" 이라고 판정했는데 [실측 `realism_phase1.md:250`],
**그 patch 혼합을 모듈형 포장에서 0으로 끈 순간 그 논거가 무효가 된다.** 재승격한다(§4.2).

### 1.4 결손 ④ — 웨더링 4마스크 중 2개가 비활성(정당한 비활성, 재활성 통로 없음)

`grime`(기단 오염)·`splash` 는 **월드 Z 절대 기준**이라 지면(z≈0)이 밴드 안에 통째로 들어가고,
sceneD3 측구(인버트 −1.05)처럼 **낙차가 깊을수록 어두워지는 결정론적 알베도 규칙**이 되어
**GT 낙차와 상관된 합성 지름길**을 만든다 [실측 — `scene_common.py:215-226` 치명 C4 기록].
현행 `_W_STRUCT/_W_STONE/_W_EDGE` 는 `streak`·`dust`만 켜져 있다(0.08~0.12 / `wrough` 0.10~0.15).
**비활성 판단은 옳다.** 필요한 건 되돌리기가 아니라 **프림 발치 z 를 전달하는 통로**다(§4.1).

### 1.5 결손 ⑤ — 재질 캐시 부재 + 파라미터 우선순위가 암묵적

- 같은 역할·같은 인자로 만든 재질이 씬마다·호출마다 별개 `UsdShade.Material` 로 정의된다
  (33씬 `make_pbr` 호출 **661회** [실측 `const_color_texture_map.md` §1]). 렌더 비용 병목은 아니지만
  (씬당 평균 20개) **헥스 타일링 도입 후에는 MDL 인스턴스 컴파일 수에 직결**되고,
  더 중요하게 **같은 역할이 씬 안에서 서로 다른 파라미터를 받는 사고**를 막을 수 없다.
- `spec.get("bump", bump)` 처럼 **클래스 사양이 호출자 인자를 조용히 덮는** 자리가 있다 [실측 `:1153`].
  `spec` 우선 / 호출자 우선이 항목마다 다르고 문서화돼 있지 않다.

### 1.6 이식 사양 — 무엇을 어떻게 고치는가

#### (a) MDL: 디테일 노멀 입력 추가 (약 35줄)

`NegObsGround.mdl` 에 파라미터 4개 + 함수 1개를 추가한다. **radius/bump=0 이면 완전 무영향**
(기존 씬 픽셀 동일) — v1.6.0 웨더링과 같은 회귀 0 설계를 따른다.

```mdl
// [T1] 미세 그레인 디테일 노멀 — 지배 평면 1장만 샘플한다.
// 왜 1장인가: 등방 고주파 그레인이라 평면 전환 경계에 결맞은 패턴이 없다.
// 3평면 전부 샘플하면 텍스처 페치가 +3회 되는데 얻는 것이 없다(비용만 3배).
float3 negobs_detail_normal(
    uniform texture_2d det_tex, uniform float det_scale,
    uniform float det_bump, uniform bool flip_u, uniform bool flip_v)
{
    if (det_bump <= 0.0 || !tex::texture_isvalid(det_tex))
        return state::normal();                       // 컴파일 타임 접힘
    float3 pw = state::transform_point(state::coordinate_internal,
                                       state::coordinate_world, state::position());
    float3 nw = math::normalize(state::transform_normal(
        state::coordinate_internal, state::coordinate_world, state::normal()));
    float3 an = math::abs(nw);
    // 지배 축 선택(하드 스위치 허용 — 등방 그레인이라 이음매가 안 보인다)
    float2 uv = (an.z >= an.x && an.z >= an.y) ? float2(pw.x, pw.y)
              : ((an.x >= an.y)               ? float2(pw.y, pw.z)
                                              : float2(pw.x, pw.z));
    float3 tu = (an.z >= an.x && an.z >= an.y)
        ? state::transform_vector(state::coordinate_world,
                                  state::coordinate_internal, float3(1,0,0)) : …;
    float3 tv = …;                                    // 위와 동일 규칙의 제2축
    base::texture_coordinate_info ci = base::texture_coordinate_info(
        position: float3(uv.x * det_scale, uv.y * det_scale, 0.0),
        tangent_u: tu, tangent_v: tv);
    return base::tangent_space_normal_texture(
        texture: det_tex, factor: det_bump,
        flip_tangent_u: flip_u, flip_tangent_v: flip_v, uvw: ci);
}
```

(위 코드의 `…` 는 지배 축이 X·Y 일 때의 **대칭 분기**다 — Z 분기와 동일 규칙으로 두 접선축을 고른다.
MDL 은 삼항 연산자 안에서 `float3` 을 반환할 수 있으므로 분기 3개를 그대로 펼쳐 쓴다.)

머티리얼 파라미터(추가 4개):

| 이름 | 형 | 기본값 | 의미 |
|---|---|---|---|
| `detail_normalmap_texture` | `texture_2d` | `texture_2d()` | 미세 그레인 노멀. 미지정 = 무영향 |
| `detail_bump_factor` | `float` | **0.0** | 강도. **0 = 완전 무영향(회귀 0 보장)** |
| `detail_texture_scale` | `float` | 12.5 | 1/타일[m] — 12.5 = 8 cm 주기 |
| `detail_rough_gain` | `float` | 0.0 | 그레인 대비를 roughness 로도 소량 전달(선택) |

합성 지점 — `let` 블록의 베벨 합성과 **같은 방식으로 편차 가산**(§`nrm` 계산부, 현행 759줄):

```mdl
float3 nd  = negobs_detail_normal(detail_normalmap_texture, detail_texture_scale,
                                  detail_bump_factor, flip_tangent_u, flip_tangent_v);
float3 nrm = math::normalize(nrm_tex + (rc - state::normal())
                                     + (nd - state::normal()));
```

근거: `state::rounded_corner_normal` 합성과 동일한 1차 가산 규칙을 재사용하면
`radius=0`·`bump=0` 두 항이 모두 정확히 0 벡터가 되어 **부동소수점 항등**이 유지된다
[실측 — 현행 `NegObsGround.mdl:748-759` 가 이미 이 규약을 쓰고 그 근거를 주석에 남김].

#### (b) `scene_common.py`: 디테일 노멀을 3단 정책 **양쪽**에 건다 (약 25줄)

```python
# 역할 계열별 디테일 노멀 (§3 조달표). 파일 부재 시 조용히 생략.
#   1순위 = 절차 생성(§3.3, β 파워규약 2.0) / 폴백 = 저장소 보유분(§3.2, 조달 0)
_DETAIL_MAP = {                                   # (파일, bump, 1/타일[m])
    "mineral":  ("detail_grain_mineral_nor.png",  0.85, 12.5),  # 포장·콘크리트·석재·연석·노징
    "granular": ("detail_grain_granular_nor.png", 0.70,  8.0),  # 흙·자갈·아스팔트·눈
    "metal":    ("detail_grain_brushed_nor.png",  0.55, 25.0),  # 금속(이방 스크래치)
    "wood":     (None, 0.0, 0.0),                               # 목재는 결이 방향성 — 디테일 금지
}
_DETAIL_FALLBACK = {                              # [v1.1] 절차 생성 실패 시 — 조달 0
    "mineral":  ("scene01/plaster_nor_dx.jpg", 0.85, 12.5),   # macro 3.9 · slope −0.89 · RMS 0.159
    "granular": ("scene01/asphalt_nor_dx.jpg", 0.70,  8.0),   # macro 3.2 · slope −0.66 · RMS 0.294
    "metal":    (None, 0.0, 0.0),                             # 보유분 전멸 — 절차 외 대안 없음(§3.2)
}
_DETAIL_FAMILY = {"paving": "mineral", "concrete": "mineral", "brick": "mineral",
                  "stone": "mineral", "curb": "mineral", "nosing": "mineral",
                  "soil": "granular", "gravel": "granular", "asphalt": "granular",
                  "snow": "granular", "metal": "metal"}
```

`_make_ground_pbr` 끝부분(웨더링 블록 뒤)에 6줄, OmniPBR 블록(`:1084`)의 `_DETAIL_NOR` 를 위 표로 교체.
**`veg`·`water`·`glass`·`paint`·`sign`·`misc` 는 유지(디테일 금지)** — 도색·사인은 균일해야 단서로 기능한다(v5.1 §4).
**`[v1.1]` `sceneC2` 계열(과잉 HF)에는 디테일을 걸지 않는다** — §2.2 처방 열 "디테일 금지" 준수.

#### (c) 재질 캐시 (약 20줄)

```python
_MTL_CACHE = {}      # 스테이지별로 리셋 — key: (kind, 정규화 파라미터 튜플)
def _mtl_key(kind, path, **kw):
    # 경로는 키에 넣지 않는다 — 같은 사양이면 같은 재질을 공유하는 것이 목적.
    return (kind,) + tuple(sorted((k, _round6(v)) for k, v in kw.items()))
```
- 히트 시 기존 `UsdShade.Material` 반환, `LOOK_STATS["mtl_cache_hit"] += 1`.
- **주의(회귀 위험)**: 씬 코드가 `M["x"]` 를 받아 **재질 프림 경로를 직접 참조**하는 곳이 있으면
  공유가 경로를 바꾼다 → 캐시는 `NEGOBS_MTL_CACHE=1` **별도 플래그로 기본 OFF**, 파일럿 3씬에서
  `regression_check.py` FAIL 0 확인 후 승격. **우선순위 최하** (렌더 병목 아님 — §1.5).

#### (d) 파라미터 표준화 규약 (문서 + 어서션 5줄)

1. **호출자 명시 인자가 항상 이긴다.** 클래스 사양은 **호출자가 주지 않은 값만** 채운다.
   현행 `spec.get("bump", bump)` 는 반대로 동작하므로 `bump if bump != 1.0 else spec.get("bump", 1.0)` 로 교정.
2. 클래스 사양 키는 4계열로 고정: **기하계**(`bevel`) · **재질계**(`mdl`,`patch`,`tex`,`tex_alts`,`max_gain`) ·
   **광학계**(`sat`,`spec`,`bump`) · **웨더링계**(`weather`,`detail`).
3. 새 키 추가 시 `LOOK_CLASS` 전 클래스에 **기본값 명시**(누락 = 조용한 무영향 = §1.1 재발원).
4. 부팅 시 1회 `assert set(spec) <= _ALLOWED_KEYS` — 오타 키가 조용히 무시되는 것을 막는다.

### 1.7 게이트 배치와 **대조군 규칙** (치명 C3 유형 예방) `[v1.1 R1 — 전면 개정]`

#### 문제 — 현행 `LOOK_V1` 단일 플래그로는 재질 A/B 가 불가능하다

`NEGOBS_LOOK_V1` 은 재질뿐 아니라 **기하도 바꾼다.** ⇒ "LOOK_V1=0 vs 1" 을 재질층 A/B 로 쓰면
기하 변화가 섞여 재질 효과를 분리할 수 없다. 이것이 재발 2회를 기록한 치명 C3(대조군 오염)의
구조적 원인이다 [실측 — `redteam_verification_v1.md` R3: "수정 8분 뒤에 재발"].

#### **v1 의 처방이 그 C3 을 재생산할 뻔했다 — 열거 방식 폐기**

v1 은 "기하 8곳(`:735` … `:2275`)을 `LOOK_GEO` 로 치환" 이라는 **열거**를 산출물로 삼았다.
레드팀이 24개 참조를 전수 분류해 **2곳 누락**을 확인했다 [`redteam_w1_design.md` §2.5] —
본 개정이 현행 `c751acd` 에서 재검증했고 **일치**한다 [실측 — `grep -n LOOK_V1 scene_common.py`]:

| 누락 지점(v1 기준) | 현행 행 | 내용 | 문자대로 이행 시 결과 |
|---|---|---|---|
| `:2140` | **`:2143`** | `if LOOK_V1:` → `fk.window_rows_visible(...)` = **창 행 수 상한**(안 보이는 층 창 생략) | 창·SillBand **프림 개수** 변화 |
| `:2184` | **`:2187`** | `if not LOOK_V1: return prims` — 이 뒤의 **기단 석재 띠·에어컨 실외기·저층부 파사드 킷 전체**가 게이트 안 | **건물 저층부 기하 통째 소실** |

A/B 프로토콜(R-2)은 `NEGOBS_LOOK_MTL`/`GEO` 만 설정하므로, 두 곳이 `LOOK_V1` 을 계속 보면
**양팔 모두에서 `LOOK_V1=False`** 가 된다 → 창 상한 해제 + 저층 파사드 소실.
파일럿 렌더가 §2.2 측정 기반(r2_on, `LOOK_V1=1`)과 **다른 기하**로 찍히고,
**R-4(기하 불변 검사)는 MTL 0/1 비교라 이 회귀를 원리적으로 못 잡는다**(양팔이 똑같이 틀리므로).
직격 대상은 **파일럿 scene14**(파라펫·건물셸 지배, `flat_gnd` 31.3)다 — `build_building` 호출 씬
**현역 24씬**(main 16 + batch1 8; 그 외 `archive_v3` 3건은 33씬 밖) 전부가 영향권이다
[실측 — `grep -rln build_building scenes/`].

⇒ **열거를 산출물로 삼지 않는다.** 아래 §1.7.1 전수 분류표 + §1.7.2 잔존 참조 0 어서션이
단계 2의 **통과 조건**이다.

#### 1.7.1 `LOOK_V1` 참조 전수 분류표 — **24건 / 100 %** [실측 2026-07-29 · `c751acd`]

분류 기준: **GEO** = 프림 집합·타입·xform·points·extent 를 바꾼다 · **MTL** = 셰이더 입력/
`UsdShade.Material` 정의만 바꾼다 · **META** = 로깅·통계·정의 · **주석** = 코드 아님.

| # | 행 | 코드 | 분류 | 치환 대상 |
|---:|---:|---|---|---|
| 1 | `:156` | 섹션 헤더 주석 | 주석 | 문구 갱신 |
| 2 | `:172` | `LOOK_V1 = os.environ.get("NEGOBS_LOOK_V1","")=="1"` | **META(정의)** | **유지** — 상위 플래그 |
| 3 | `:360` | `look_report()` 조기 반환 | META | `LOOK_MTL or LOOK_GEO` |
| 4 | `:735` | `if LOOK_V1 and _skin_wanted(...)` — 변위 스킨 **메시 신설** | **GEO** | `LOOK_GEO` |
| 5 | `:968` | `make_pbr` docstring | 주석 | 문구 갱신 |
| 6 | `:975` | `if LOOK_V1 and not uv_mode and emission_color is None:` — 룩 사양 진입 | **MTL** | `LOOK_MTL` |
| 7 | `:1018` | `elif LOOK_V1: LOOK_STATS["skipped"] += 1` | META | `LOOK_MTL` |
| 8 | `:1331` | 주석 | 주석 | — |
| 9 | `:1334` | 주석(치명 C3 경위) | 주석 | — |
| 10 | `:1337` | `rail_h = 1.1 if LOOK_V1 else 0.9` | **GEO** | `LOOK_GEO` |
| 11 | `:1339` | `spacing = 2.0 if LOOK_V1 else 1.2` (포스트 개수) | **GEO** | `LOOK_GEO` |
| 12 | `:1366` | 주석 | 주석 | — |
| 13 | `:1367` | `if LOOK_V1 and baluster_r > 0:` — 세로 간살 신설 | **GEO** | `LOOK_GEO` |
| 14 | `:1409` | `if LOOK_V1 and handrail and run > 0.3:` — 손잡이 신설 | **GEO** | `LOOK_GEO` |
| 15 | `:1911` | `add_vegetation` docstring | 주석 | — |
| 16 | `:1920` | `if LOOK_V1 and veg_available():` — 실물 나무 USD | **GEO** | `LOOK_GEO` |
| 17 | `:2031` | `if LOOK_V1 and veg_available():` — 화단 관목 | **GEO** | `LOOK_GEO` |
| 18 | `:2080` | `build_building` docstring | 주석 | — |
| 19 | `:2100` | `ins = float(wd.get("inset",0.0)) if LOOK_V1 else 0.0` — 창 리세스 | **GEO** | `LOOK_GEO` |
| 20 | `:2117` | 주석 | 주석 | — |
| 21 | **`:2143`** | `if LOOK_V1:` → `fk.window_rows_visible(...)` — **창 행 상한** | **GEO ★v1 누락** | `LOOK_GEO` |
| 22 | `:2182` | `par_h = 1.20 if LOOK_V1 else 0.5` | **GEO** | `LOOK_GEO` |
| 23 | **`:2187`** | `if not LOOK_V1: return prims` — **저층 파사드 킷 전체** | **GEO ★v1 누락** | `LOOK_GEO` |
| 24 | `:2278` | `if not (LOOK_V1 and veg_available()): return 0` — 산포 관목/생울타리 | **GEO** | `LOOK_GEO` |

**집계**: 주석 8 · META 3(정의 1 + 로깅 2) · **MTL 1** · **GEO 12**.
v1 이 "8곳" 이라 부른 표는 마지막 행에 3곳을 묶어 실제로는 10곳을 가리켰고, **`:2143`·`:2187` 2곳이 빠져 있었다.**

> **이 표는 산출물이 아니라 감사 흔적이다.** 행번호는 병행 편집으로 언제든 밀린다
> (실제로 개정 중 다른 에이전트가 `scene_common.py` 를 2건 수정했고, 재검증 결과 24개 행은
> 우연히 전부 불변이었다 [실측 2026-07-29]). **구현자는 이 표를 신뢰하지 말고
> `grep -n "LOOK_V1" scene_common.py` 를 다시 돌린 뒤 §1.7.2 R-5 로 잔존 0 을 증명하라.**
> 표와 실제가 어긋나도 R-5 가 통과하지 못하므로 열거 누락은 구조적으로 불가능하다 —
> 이것이 v1 의 "8곳 열거"를 폐기하고 어서션으로 갈아탄 이유의 전부다.

**킷 파일·씬 파일의 동종 게이트도 같은 표에 포함한다** [실측 — `grep -rn "LOOK_V1" --include=*.py`]:

| 파일 | 행 | 코드 | 분류 | 치환 |
|---|---:|---|---|---|
| `scenes/batch1/sceneC2_leaf_stairs.py` | `:552` | `if sc.LOOK_V1 and sc.veg_available():` — 3D 낙엽 산포 | **GEO** | `sc.LOOK_GEO` |
| `scenes/batch1/sceneN4_downhill_ramp.py` | `:723` | `if sc.LOOK_V1:` — 옹벽 배수공·신축이음 `infra_kit` | **GEO** | `sc.LOOK_GEO` |
| `facade_kit.py` | `:33` | 규약 주석 "호출부에서 `LOOK_V1` 게이트 안에서만" | 주석 | 문구를 `LOOK_GEO` 로 갱신 |
| `building_kit.py` | `:1635` | 자기검사 docstring | 주석 | — |

> **중요**: `sceneC2:552`·`sceneN4:723` 은 **씬 파일이 모듈 전역 `sc.LOOK_V1` 을 직접 읽는** 자리다.
> 여기를 놓치면 `sceneC2`(상시 대조군 씬)의 3D 낙엽 845개가 A/B 양팔에서 사라져
> **§7.1 판정 문턱표를 뽑은 렌더와 다른 씬**이 된다. 씬 파일 수정은 "코드 수정"이지만
> **대조군 순도에 필수**이므로 단계 2에 포함한다.

#### 1.7.2 처방 — 2단 플래그 + 잔존 참조 0 어서션 + 대조군 4규칙

```python
LOOK_V1  = os.environ.get("NEGOBS_LOOK_V1", "") == "1"          # 상위(종전 호환)
LOOK_MTL = os.environ.get("NEGOBS_LOOK_MTL", "1" if LOOK_V1 else "0") == "1"
LOOK_GEO = os.environ.get("NEGOBS_LOOK_GEO", "1" if LOOK_V1 else "0") == "1"
```
- 기존 `LOOK_V1=1` 호출은 둘 다 ON → **종전 동작 완전 보존**.
- **T1 재질층 신규 항목(디테일 노멀·헥스 타일링·유닛 지터·톤·채도·`scale_m`)은 전부 `LOOK_MTL` 안.**

**잔존 참조 0 어서션 (`geom_invariance_check.py` 가 검사 — 단계 2 통과 조건)**

```python
# scripts/geom_invariance_check.py --assert-no-residual-lookv1
_ALLOW = {("scene_common.py", 172)}           # 정의 1줄만 허용
_SRC   = ["scene_common.py", "facade_kit.py", "building_kit.py", "infra_kit.py",
          "stair_kit.py", "ground_kit.py", *glob("scenes/*/*.py")]
# 주석·docstring 을 제거한 뒤(tokenize) 남는 LOOK_V1 / NEGOBS_LOOK_V1 토큰을 센다.
# _ALLOW 밖에 1건이라도 남으면 exit 1 + 파일:행 출력.
```
- **주석은 세지 않는다**(tokenize 로 `COMMENT`·docstring 제거) — 경위 기록은 남겨야 하므로.
- 이 어서션이 **§1.7.1 표를 "산출물"이 아니라 "감사 흔적"으로 강등**시킨다.
  표가 틀려도 어서션이 통과하지 못하므로 열거 누락이 구조적으로 불가능해진다.

**대조군 규칙(위반 시 레드팀 킬)**

| # | 규칙 | 검사 방법 |
|---|---|---|
| **R-1** | 재질층은 **프림 집합·타입·xform·points·extent 를 바꾸지 않는다.** 셰이더 입력과 `UsdShade.Material` 정의만 만든다 | 자동 (아래 R-4) |
| **R-2** | 재질 A/B 의 대조군은 `LOOK_MTL=0, LOOK_GEO=<실험군과 동일>` 이다. **`LOOK_V1=0` 전체 OFF 를 대조군으로 쓰지 않는다** | 라운드 스크립트에 환경변수 명시 + 로그에 각인 |
| **R-3** | 함수 **기본 인자값**을 플래그로 분기할 때는 `x = A if LOOK_GEO else B` 형태로 **게이트 안**에서만. 기본값 자체를 바꾸지 않는다 | 코드 리뷰 + R-4 |
| **R-4** | **자동 기하 불변 검사**: `scripts/geom_invariance_check.py` — `pxr/omni/carb/isaacsim` 을 MagicMock 으로 대체하고 `add_box/add_cylinder/add_sphere/_oriented_box/Mesh.Define` 을 기록 스텁으로 갈아끼운 뒤 각 씬 `main()` 을 `LOOK_MTL=0/1` 두 번 실행 → **프림 인벤토리 해시**(경로·타입·중심·치수·회전, 소수 6자리 반올림) 비교. 불일치 1건이라도 exit 1 | GPU 0 · 33씬 약 3분. 하네스는 `const_color_texture_map.md` §0-2 가 이미 33/33 성공으로 검증한 방식 |
| **R-5** `[v1.1]` | **잔존 `LOOK_V1` 참조 0** — §1.7.2 어서션. 같은 스크립트가 `--assert-no-residual-lookv1` 로 검사하며, **R-4 보다 먼저** 돈다 | 자동 · GPU 0 · 1초 |
| **R-6** `[v1.1]` | **GEO 팔 고정 검증** — `LOOK_MTL=0/1` 두 팔의 프림 인벤토리 해시가 서로 같을 뿐 아니라, **`LOOK_V1=1` 단독 실행의 해시와도 같아야** 한다. R-4 만으로는 "양팔이 똑같이 틀린" §2.5 유형을 못 잡는다 | 3회 실행 비교(`V1=1` / `MTL=0,GEO=1` / `MTL=1,GEO=1`) · 33씬 약 5분 |

R-4 는 **웨더링 primvar 예외**를 허용한다(§4.1의 `foot_z`): primvar 저작은 위 해시 항목에 포함되지 않으며,
별도로 "primvar 이름·interpolation 만 diff" 하는 보조 리포트를 낸다.

### 1.8 `ground_kit` → T1 **이관 4건 수용** `[v1.1 G1~G4 — 신설]`

레드팀 §3 이 "두 스펙이 같은 날 병렬 작성되어 **이관 계약이 편도로만 존재**한다 — T1 스펙 내
존재 **0건**" 으로 지적한 항목이다 [실측 — `grep -c "unit_cell\|scale_m\|leaf_ground" t1_material_layer_spec_v1.md` = 0].
**4건 전부 T1 소유로 수용한다.** 정의 기준은 레드팀 보고서 + `ground_kit_spec_v1.md` v1 본문이다
(동 문서는 병행 개정 중이므로 v1.1 본문을 참조하지 않는다).

#### ① `_ground_skin` **P-A 스위치** 수용 — `SKIN_EXCLUDE` / `skin_exclude` (코드 4줄)

`ground_kit` §9.3 이 "**전부 — 차단**" 으로 표시한 유일한 항목이다. `scene_common.py` 소유이므로 T1 이 집행한다.

```python
SKIN_EXCLUDE = set()          # 모듈 전역. 씬이 ground_kit 적용 전에 등록한다.

def skin_exclude(*paths):     # 공개 API — ground_kit 은 이 함수를 '주입'받는다
    SKIN_EXCLUDE.update(str(p) for p in paths)

# _skin_wanted() 첫 줄에 추가
    if str(path) in SKIN_EXCLUDE or any(str(path).startswith(p) for p in SKIN_EXCLUDE):
        return False
```
- `_SKIN_DENY` 에 토큰 **`"gkit"`** 1개 추가 — `{ROOT}/GKit/...` 산출물이 2차 스킨을 뒤집어쓰는 사고를 구조적으로 차단.
- **T1 관점의 성질 판정**: `_skin_wanted` 는 `LOOK_GEO` 게이트 안(`:735`, §1.7.1 #4)이다.
  `SKIN_EXCLUDE` 가 비어 있으면 **동작 완전 동일**이므로 **회귀 0**이고, R-4/R-6 도 통과한다
  (등록은 씬 코드가 하며, 등록 자체가 기하 변경이므로 **`LOOK_GEO` 팔의 사건**이다).
- **주의**: 이 스위치는 **T1 A/B 의 대조군 정의를 건드리지 않는다** — 양팔 모두 `LOOK_GEO=1` 이고
  `SKIN_EXCLUDE` 도 양팔 동일. 단 **파일럿 씬(19·07·14)에는 등록 0** 을 유지한다
  (등록은 ground_kit 파일럿 N5·15·13 소관).

#### ② `plaza_light` **톤 ×0.72 + `scale_m` 교정** — 9씬 동시 `[v1.1 G2]`

톤(T-1)은 v1 에 이미 있었으나 **`scale_m` 이 없었다**. 두 값은 **같은 재질 호출의 인자**이므로
**분리 집행이 불가능**하다(같은 `make_pbr` 줄을 두 번 만지면 그 사이의 렌더가 무의미해진다).

**v1 의 "0.75→1.80" 일괄 문구는 부정확하다 — 현행이 두 값으로 갈려 있다** [실측 2026-07-29, 9씬 전수]:

| 씬 | 현행 `scale_m` | 파일:행 |
|---|---:|---|
| scene01 | 0.75 | `scenes/main/scene01_campus_stairs.py:187` |
| scene05 | 0.75 | `scenes/main/scene05_amphitheater.py:369` |
| **scene14** | **0.8** | `scenes/main/scene14_grandstair_illusion.py:171` |
| scene16 | 0.75 | `scenes/main/scene16_canopy_shadow.py:155` |
| scene18 | 0.75 | `scenes/main/scene18_wavy_artstair.py:247` |
| scene19 | 0.75 | `scenes/main/scene19_fan_winder.py:159` |
| scene20 | 0.75 | `scenes/main/scene20_diagonal_oblique.py:136` |
| **scene21** | **0.8** | `scenes/main/scene21_monumental_selfocclude.py:165` |
| sceneN3 | 0.75 | `scenes/batch1/sceneN3_trompe_loeil.py:168` |

⇒ 지시는 **"현행값과 무관하게 9씬 전부 `1.80` 으로 통일"** 이다(0.75→1.80 은 ×2.40, 0.8→1.80 은 ×2.25).
값의 출처는 `ground_kit` 원장 `GROUND_DIMENSIONS["module_*"]` 이며, ground_kit 이 이 원장의 소유자다.

**집행 규칙 (회귀)**
- **9씬 동시 적용 + 동시 재렌더.** 톤과 스케일을 **같은 커밋·같은 라운드**로 묶는다.
- `scale_m` 은 **`LOOK_MTL` 게이트 밖**이다(씬 파일의 `make_pbr` 인자). 즉 **A/B 양팔에 동일하게 걸린다** —
  A/B 로 검증할 수 있는 항목이 아니라 **before/after 라운드로만** 검증된다. §7.2 프로토콜에 별도 취급.
- **§7.1 판정 문턱표는 `scale_m` 변경 후 무효**가 될 수 있다(같은 씬의 텍스처 주기가 2.25~2.40배 바뀐다).
  ⇒ **실행 순서상 `scale_m` 교정은 파일럿 A/B **뒤**에 둔다**(§8 순 7).

#### ③ MDL **유닛 셀 해시 알베도 지터** 입력 추가 `[v1.1 G3]`

`ground_kit` §4.4 가 "**전 포장 프로파일의 σ_LF 주성분**" 으로 지정한 항목. 기하로 하면 셀당 프림
1개라 폭증하므로 MDL 소관이다. §1.6(a) 디테일 노멀과 **같은 MDL 개정(v1.9.0)에 함께 넣는다.**

머티리얼 파라미터(추가 3개):

| 이름 | 형 | 기본값 | 의미 |
|---|---|---|---|
| `unit_cell_m` | `float2` | `float2(0.0)` | 유닛(모듈) 치수 [m]. **0 = 완전 무영향(회귀 0)**. 값의 출처는 ground_kit `GROUND_DIMENSIONS` |
| `unit_albedo_sigma` | `float` | **0.10** | 셀별 알베도 로그정규 지터의 σ. 켜지는 것은 `unit_cell_m > 0` 일 때뿐 |
| `unit_accent_frac` | `float` | **0.07** | 강조 유닛 비율(7 %). 이 셀은 지터를 ×2.5 로 준다 — 실제 포장의 "색 다른 블록 한두 장" |

```mdl
// [T1·G3] 유닛 셀 해시 알베도 지터 — 지배 평면 좌표를 셀로 양자화해 셀당 스칼라 1개.
// 텍스처 페치 0. `negobs_hash2` 를 재사용하므로 헥스와 해시 함수를 공유한다.
float negobs_unit_gain(float2 pw, float2 cell, float sigma, float accent)
{
    if (cell.x <= 0.0 || cell.y <= 0.0 || sigma <= 0.0) return 1.0;   // 컴파일 타임 접힘
    float2 c  = math::floor(float2(pw.x / cell.x, pw.y / cell.y));
    float2 h  = negobs_hash2(c);                       // h.x = 지터, h.y = 강조 추첨
    float  g  = (h.x - 0.5) * 2.0;                     // −1..1 균등
    float  s  = (h.y < accent) ? sigma * 2.5 : sigma;  // 강조 유닛 7 %
    return math::exp(g * s);                           // 로그정규 = 알베도 비율 지터
}
```
- **합성 지점**: `base_color` 에 **곱**한다. 알베도 비율 지터이므로 `sigma=0` 이면 정확히 `exp(0)=1` — **부동소수점 항등**.
- **셀 경계 = 유닛 경계**여야 한다. `unit_cell_m` 은 ground_kit 의 음각 줄눈 격자와 **같은 원점·같은 주기**를 써야
  "지터 경계"와 "줄눈"이 어긋나 이중 격자가 보이는 사고를 막는다. ⇒ ground_kit 이 `unit_cell_m` 과 함께
  **격자 원점 오프셋**도 넘겨야 한다 — **`unit_cell_origin` (`float2`, 기본 0) 을 4번째 파라미터로 추가**하고
  이 요구를 ground_kit 에 회신한다(계약 역방향 1건).
- **지름길 안전성**: 셀 지터는 **평면 좌표(x,y)의 해시**이고 z 를 읽지 않는다 ⇒ **GT 낙차와 상관 0.**
  (§4.1 의 `grime_z0` 이 겪은 C4 와 성질이 다르다.)
- **`patch_mix`/헥스와의 관계**: 유닛 지터는 **알베도 스칼라 곱**이라 3샘플 블렌드보다 **뒤**에 걸린다.
  헥스 블렌드가 분산 보존을 하고 그 위에 셀 지터가 얹히는 순서 — 상호 배타가 아니다.

#### ④ `veg` 클래스 정리 — `leaf_ground` 제거 + `grass` 1.4 m 교체 `[v1.1 G4]`

**목적: `LOOK_V1` 승격 로직의 24씬 가을 낙엽 오염 차단.** B조 감사가 코드 시뮬레이션으로 확정했다
[실측 — `B_groundcover_debris.md` §8]:

- 현행 `LOOK_CLASS["veg"] = dict(tex="grass", tex_alts=("grass","leaf_ground"), max_gain=7.0)` [실측 `scene_common.py:277-281`].
- `_promote_const_to_texture` 채택 조건은 `max(ratio) ≤ max_gain` **그리고** `spread = max/min ≤ 4.0` [실측 `:576-579`].
- `grass`(aerial_grass_rock) 선형 평균 RGB **(0.1688, 0.1210, 0.0240)** — 적/청 비 **7.03**, 청 채널이 비었다.
  초록 수관 상수색(`canopy_a = (0.025,0.045,0.015)`)에서 `spread = 4.22 > 4.0` → **grass 탈락**.
- `leaf_ground` 선형 평균 (0.0614,0.0386,0.0150), 적/청 4.09 → `spread = 2.86` → **`leaf_ground` 채택**.
- **전 33씬 전수 시뮬레이션 결과: `leaf_ground` 승격 50건 / 24씬** (모든 씬의 `canopy_a`·`canopy_b`,
  scene04·07·10 `shrub`, C4 `shrub_color`). 승격 `scale_m` 은 `spec.get("tex_scale",1.2)` = 1.2 m 이므로
  **원본 2.3 m 낙엽이 52 % 크기로 나무 수관 위에 붙는다.**
- **규약 위반**: `forest_leaves_03` 은 PolyHaven 태그 `leaves/autumn/dry`, 픽셀은 갈적 낙엽(선형 0.050, 색상 34.5°).
  "계절/이벤트 특정 요소 금지 — 잎 텍스처 픽셀을 직접 열어 판정" 규약에 정면으로 걸린다.

**수용안 = B 감사 A1 + A2 를 일원화(한 라운드에 둘 다)**

| 순 | 조치 | 코드 | 근거 |
|---|---|---|---|
| **A2**(즉시 차단) | `LOOK_CLASS["veg"]["tex_alts"]` 에서 **`leaf_ground` 제거** → `("grass",)` | `scene_common.py:279` 1줄 | B §12 A2 |
| **A1**(근본) | `TEX["grass"]` 를 ambientCG **`Grass001`** (실측 타일 **1.40×1.40 m**, CC0, 태그 `lawn/park/short/dense`) 로 교체 + 전 씬 `scale=dict(grass=…)` 를 **1.4** 로 | `scene_common.py:59-61` + 씬 상수 | B §10-b·§12 A1 |

- **A1 이 A2 를 대체하지 않는다 — 둘 다 한다.** A1 만 하면 `spread` 가 4.0 아래로 내려가 `grass` 가
  의도대로 채택되지만, `leaf_ground` 가 `tex_alts` 에 남아 있는 한 **`grass` 가 `max_gain` 을 넘는
  어두운 상수색에서는 여전히 `leaf_ground` 로 떨어진다.** A2 는 그 경로를 물리적으로 없앤다.
- **A1 의 부수 효과(반드시 인지)**: `aerial_grass_rock` 273 px/m → `Grass001` **2926 px/m (×10.7)**.
  들잔디 잎 나비 4~7 mm 가 12~20 px 로 **실제 해상**된다. 이는 §3-a "자연 지피가 원본의 1/3~1/6 로
  축소돼 있다" 도 동시에 해소한다. **단 28씬의 지면 픽셀이 바뀐다** — `scale_m` 교정(②)과 같은
  성질의 **before/after 항목**이지 A/B 항목이 아니다.
- **`veg` 클래스의 `detail=False` 는 유지**(§2.1) — 잎은 실물 USD 담당.
- **의존 해소**: `ground_kit` §9.3 이 "03·04·07·09·12 의 잔디↔포장 경계 파쇄가 이 교체에 의존" 으로 표시한 항목이 풀린다.
- **조달**: `https://ambientcg.com/view?id=Grass001` → `Grass001_1K-JPG.zip`. 대안 `Grass004`(동 1.40 m).
  CC0 1.0 · AI 학습 허용 [ZZ §10.6]. **`sceneC2` 는 예외** — 가을 낙엽 씬이므로 `leaf_ground` 를
  **씬 파일이 명시 인자로** 계속 쓴다(클래스 승격 경로만 끊는 것이지 텍스처를 지우는 게 아니다).

---

## 2. 적용 대상 표 — 씬 × 표면 × 현행 → 목표

### 2.1 클래스 마스터 표 (33씬 정적 전수)

`이름` = 33씬 `Looks/<Name>` 고유 이름 수, `씬` = 등장 씬 수 [실측 — 33씬 정규식 스캔 + `_look_spec` 분류].
`누적 gnd%p` = 상수색 재질의 하단 2/3 프레임 점유율 33씬 합 [실측 — `const_color_texture_map.md` §1, 레이캐스트].

| 클래스 | 이름 | 씬 | 누적 gnd%p | 현행 재질 | 현행 디테일 | 현행 반복파괴 | **목표** | 우선 |
|---|---:|---:|---:|---|---|---|---|---|
| **concrete** | 94 | 29 | 77.8 | MDL(ground) + `concrete_floor` 승격 | **죽음** | patch 0 | 디테일(mineral) + **헥스(오프셋)** + 밝은 계열 `plaster` 분기 | **1** |
| **paving** | 26 | 18 | ~1 | MDL + `paving_interlock` | **죽음** | patch 0 | 디테일(mineral) + **헥스(오프셋)** + 톤 0.72 | **1** |
| **metal** | 115 | 31 | **87.9** | OmniPBR, 텍스처 없음 | 콘크리트 그레인(**오적용**) | — | `metal_galv` 조달 + brushed 디테일 | **2** |
| **veg** | 107 | 30 | 44.5 | OmniPBR/MDL(상수색) + `grass` | 없음(의도) | patch 1 | **`tex_alts` 에서 `leaf_ground` 제거 + `grass`→`Grass001`(1.4 m)** `[v1.1 G4 — §1.8④]`. 디테일은 계속 금지. 잎은 실물 USD 담당(P3) | **2** |
| paint | 77 | 29 | 18.2 | OmniPBR 상수색 | 없음 | — | **불가침**(도색은 균일해야 단서) | — |
| wood | 56 | 31 | 46.5 | OmniPBR + `wood_dark` | 콘크리트 그레인(**오적용**) | — | 디테일 **끔**(결이 방향성) | 3 |
| sign | 43 | 21 | 14.3 | OmniPBR uv_mode | 없음 | — | 불가침 | — |
| glass | 29 | 26 | 17.2 | OmniPBR | 없음 | — | 불가침 | — |
| brick | 22 | 20 | ~1 | MDL + `brick_red` | **죽음** | patch 0 | 디테일(mineral) + 헥스(오프셋) | 2 |
| stone | 22 | 16 | 11.0 | MDL + `stone_flag` | **죽음** | patch 1 | 디테일(mineral) + 헥스(오프셋+회전) | 2 |
| asphalt | 14 | 12 | **131.2** | MDL + `asphalt` | **죽음** | patch 1 | 디테일(granular) + 헥스(오프셋+회전) | **1** |
| soil | 13 | 10 | ~1 | MDL + `dirt_park` | **죽음** | patch 1 | 디테일(granular) + 헥스 | 3 |
| water | 12 | 8 | **89.5** | OmniPBR 상수색 | 없음 | — | 절차 잔물결 노멀(별건 — 재질층 밖) | 3 |
| **curb** | 12 | 12 | **23.8** | MDL, **승격 텍스처 없음** | **죽음** | patch 0 | `tex="plaster"` 추가 + 디테일 | **2** |
| **nosing** | 9 | 7 | 4.8 | MDL, **승격 텍스처 없음** | **죽음** | patch 0 | `tex="concrete_floor"` + 디테일. **GT 에지라 기하 불변 필수** | 3 |
| gravel | 8 | 7 | ~1 | MDL + `gravel` | **죽음** | patch 1 | 디테일(granular) | 4 |
| snow | 1 | 1 | 89.8(misc) | MDL + `snow` | **죽음** | patch 1 | 알베도 0.72→**0.58** + 디테일 | **1**(C1 단독 88.5%) |
| misc | 3 | 3 | — | OmniPBR 최소 | 없음 | — | 유지(보수적) | — |

### 2.2 씬별 현황과 처방 (h0.3 3컷 중앙값 실측)

측정: `look_check/<scene>/r2_on/pt_noon_preset_h0.3_d{2,5,10}.png`, `scripts/imgstats.py` 지표 정의 그대로,
`w80` = 하단 2/3 에서 **min(R,G,B) > 0.80** 인 픽셀 비율(**sRGB 표시값 0~1 기준 — 선형화하지 않는다**;
= 순백 대면적 지표, 규약 "순백(>0.8) 대면적 금지").
[실측 2026-07-29 · 33씬 × 3컷 = 99컷 · numpy+PIL · GPU 0]

> **`[v1.1 T1]` 게이트 지표 선언 — `flat%` 가 아니라 `flat_gnd`(하단 2/3) 다.**
> T0 스파이크가 sceneC2 에서 `LOOK_V1` 전량 ON 시 `flat% 20.391 → 2.227` 로 "통과"하는 것을
> 실측했는데, 같은 조건에서 **`flat_sky` 가 60.78 → 5.05 로 무너지고 `flat_gnd` 는 오히려
> 0.196 → 0.817 로 악화**했다 [실측 — `t0_spike_report_v1.md` §1.2·§1.3]. 원인은 실물 USD
> 수목 6주 + 3D 산포물 845개가 무운 하늘(`qwantani_noon_puresky`)을 가린 것이다.
> ⇒ **`flat%` 개선은 "나무를 심으면 통과"라는 무관한 경로를 허용한다.** 본 문서의 모든
> 합격/불합격 판정은 **`flat_gnd` 단독**으로 내린다. `flat%`·`flat_sky` 는 참고 열로만 남긴다.
> (`imgstats.py` 는 이미 `GATE_GND = dict(flat_gnd=(None, 3.0))` 를 갖고 있다 [실측 `:77`];
> 라운드 스크립트가 `GATE` 대신 이것을 쓰도록 바꾸는 것이 단계 0 작업이다.)
> **정의**: `flat_gnd = 100 · mean(local_std(luma, 5×5)[h//3:] < 1/255)` [실측 `imgstats.py:203`].
> **실사 기준 n=54**: `flat_gnd 3.881 ± 5.005`(중앙값 **1.79**) [실측 `imgstats.py:67-69`].

| 씬 | slope | flat% | **flat_gnd** | sat | **w80** | 지배 표면 | 처방(우선순위 순) |
|---|---:|---:|---:|---:|---:|---|---|
| scene01 | −2.39 | 8.5 | 1.0 | **0.098** | **88.2** | plaza_light 포장 80% [실측 §2 보고서] | **톤 0.72** · 헥스 · 디테일 |
| scene02 | −1.99 | 8.8 | 0.0 | 0.083 | 0.9 | 지하도 콘크리트 | 디테일 · 헥스 |
| scene03 | −2.00 | 9.0 | 0.0 | 0.309 | 1.7 | 제방 초지·흙 | 채도 하향(0.31→0.22) |
| scene04 | −1.99 | 16.9 | 0.0 | **0.437** | 0.0 | 잔디·흙 | **채도 하향 최우선** · 디테일(granular) |
| scene05 | −2.55 | 5.8 | 1.6 | **0.066** | **95.0** | plaza_light 광장·티어 | **톤 0.72**(X-1 WAIVED 해소) · 헥스 |
| scene06 | −2.39 | 14.7 | 5.6 | 0.179 | 0.0 | 콘크리트 나선램프 | 디테일 · 헥스 |
| scene07 | −2.38 | 6.1 | 1.7 | 0.254 | 0.3 | 석재 판석·흙(경사) | 디테일 · 채도 · **MDL 경사 검증 씬** |
| scene08 | −2.10 | 11.2 | 1.4 | 0.192 | 4.8 | 침상광장 포장 | 디테일 · 헥스 |
| scene09 | −2.62 | 26.7 | 2.1 | 0.152 | **41.9** | 석재 가트 + 수면 | 톤(석재 tint 이미 0.64) · 디테일 |
| scene10 | −1.99 | 1.2 | 0.4 | **0.394** | 0.0 | 목재 데크·초지 | 채도 하향 |
| scene11 | −2.33 | 12.2 | **10.4** | 0.179 | 0.0 | 금속 데크·난간 | **`metal_galv` 조달** · 디테일(metal) |
| scene12 | −1.97 | 22.1 | 1.9 | 0.226 | 0.0 | 데크 + 수면 | 잔물결(별건) · 디테일 |
| scene13 | −2.58 | 15.2 | **12.1** | 0.137 | 0.0 | 지하주차 콘크리트 | 디테일 · 헥스 · `plaster` 분기 |
| scene14 | −1.97 | 31.9 | **31.3** | 0.110 | 5.4 | 파라펫·건물셸(밝은 콘크리트) | **`plaster` 분기**(현행 `concrete_wall` 클램프) · 디테일 · 톤 T-1(공유) |
| scene15 | −2.30 | 12.7 | 2.9 | 0.270 | 0.0 | 골목 회벽·포장 | 채도 · 디테일 |
| scene16 | −2.19 | 6.0 | 0.1 | 0.078 | 0.8 | 수관 그늘 포장(무틴트 plaza_light) | 디테일 · 헥스 · 톤 T-1(공유) |
| scene17 | −1.85 | 7.1 | 0.0 | 0.154 | 3.9 | 아스팔트 자전거도로 + 수면 | 디테일(granular) |
| scene18 | −2.21 | 24.9 | 1.1 | **0.068** | **97.1** | 곡면 계단 포장 | **톤 0.72** · 헥스 · 디테일 |
| scene19 | −2.66 | 18.7 | **10.0** | **0.028** | **97.7**(w87 **72.3**) | 부채꼴 계단 + 파라펫 0.90 | **톤 0.72 + 파라펫 0.90→0.70** · 최우선 |
| scene20 | −2.25 | 8.7 | 0.7 | 0.103 | **79.2** | plaza_light 축소판 | **톤 0.72** · 헥스 |
| scene21 | −2.25 | 32.5 | **40.4** | 0.171 | 1.4 | 기념비 석재·파라펫 | `plaster` 분기 · 디테일 · 헥스 · 톤 T-1(공유) |
| sceneC1 | −2.67 | 71.5 | **98.3** | 0.125 | **99.8** | **눈 88.5%** | **알베도 0.72→0.58** + 디테일. 단일 최대 항목 |
| sceneC2 | −1.65 | 1.6 | 0.0 | **0.302** | 0.0 | 낙엽 지면 | **디테일 금지**(이미 과잉 HF) · 채도 하향. **A/B 기준선 씬** |
| sceneC4 | −2.40 | 13.4 | **19.6** | 0.177 | 0.0 | 젖은 석재 + 수면 | 잔물결(별건) · 디테일 |
| sceneD1 | −1.83 | 6.2 | 2.5 | 0.227 | 0.0 | 하역장 아스팔트 | 디테일(granular) |
| sceneD2 | −1.90 | 4.2 | 0.0 | 0.260 | 0.0 | 바닥 개구부·자갈 | 채도 · 디테일 |
| sceneD3 | −1.54 | 7.1 | 0.4 | 0.280 | 1.0 | 측구 아스팔트 | **slope 과소(−1.54)** — 디테일 강도 하향 대상 |
| sceneD4 | −1.91 | 25.9 | 7.4 | **0.450** | 0.0 | 승강장 콘크리트·사인 | **채도 하향 최우선** · 디테일 |
| sceneN1 | −2.60 | 4.7 | 0.8 | 0.111 | **67.2** | 그림자 밴드 포장 | 톤 · 헥스 |
| sceneN2 | −1.57 | 4.6 | 0.0 | 0.100 | 0.2 | 아스팔트 패치 | 디테일 소폭 |
| sceneN3 | −1.58 | 6.7 | 0.0 | 0.105 | 1.0 | 트롱프뢰유 포장(LightStone 무틴트) | 디테일 소폭 · 톤 T-1(공유) |
| sceneN4 | −2.29 | 10.9 | 2.1 | 0.132 | 4.2 | 내리막 램프·옹벽 | 디테일 · 헥스 |
| sceneN5 | −1.86 | 3.5 | 0.7 | 0.090 | **79.6** | 그레이팅 + 밝은 포장 | 톤 · **`metal_galv`** |

**33씬 중앙값**: slope −2.19 · flat% 9.0 · flat_gnd 1.4 · grad_k 22.3 · sat 0.154 · w80 **0.97**(왜도 극단).

---

## 3. `detail_normalmap_texture` 소스 조달 — CC0 한정

### 3.1 합격 기준 — **`[v1.1 R2]` §3.4 정의로 재캘리브레이션**

| 지표 | **v1.1 기준** | (v1 기준) | 이유 |
|---|---|---|---|
| `macro%` (1 ≤ r < N/32) | **< 10** | ~~< 15~~ | **모듈형 타일 맵 배제**가 진짜 역할이다. 관측 간격이 넓다 — 통과군 최대 8.7(`dirt_park`) vs 탈락군 최소 11.9(`metal_rust`) [실측 §1.2 표]. 문턱 10 은 그 간격 안 |
| `slope_n` **하한** | **> −0.9** | (동일) | 0 에 가까울수록 백색잡음 = 진짜 미세 그레인 |
| `slope_n` **상한** `[v1.1 신설]` | **≤ +0.3** | ~~없음~~ | v1 은 상한이 없어 **순수 텍셀 해시(slope +1.4)를 통과시킨다.** 그런 맵은 8 cm 타일·4K 에서 원경 반짝임·앨리어싱을 만든다. 실사 미세 그레인은 백색잡음(0) 근방이 상한 |
| 접선 RMS | **0.12 ~ 0.35** | (동일) | 0.056(현행)은 안 보이고, 0.5 이상은 지면이 자갈처럼 튄다 |
| `hf%` (N/4 ≤ r ≤ N/2) | **≥ 10** (보조) | ~~없음~~ | `macro%` 의 거울상이라 **판정용 아님 — 교차 확인용**. 통과군 13.3~27.7 vs 타일 맵 2.5~4.8 |
| 라이선스 | **CC0 only** | (동일) | Quixel(NoAI)·Isaac Environments(수정금지) 금지 [ZZ §10.6] |

> **`macro%` 와 `slope_n` 은 강하게 결합돼 있다**(스펙트럼이 가파를수록 저주파 비중이 커진다).
> 두 지표를 독립 증거처럼 세지 말 것. **1차 판정은 RMS → slope_n, `macro%` 는 타일 맵 배제 필터.**

### 3.2 후보 판정 — **`[v1.1]` 저장소 보유분이 이미 두 계열을 통과한다**

**§3.4 정의로 재측정한 결과, `mineral`·`granular` 두 계열 모두 조달 0 으로 충족 가능하다:**

| 계열 | **v1.1 채택** | macro% | slope_n | RMS | 판정 |
|---|---|---:|---:|---:|---|
| **mineral** | **`assets/scene01/plaster_nor_dx.jpg`** (보유) | **3.9** | **−0.89** | **0.159** | **통과 — 조달 0.** 단 `slope_n` 이 문턱 −0.9 에 **0.01 차로 붙어 있다**(경계 통과) ⇒ **절차 생성이 1순위, 이것은 폴백** |
| **granular** | **`assets/scene01/asphalt_nor_dx.jpg`** (보유) | **3.2** | **−0.66** | **0.294** | **통과 — 조달 0.** 여유 있는 합격. v1 판정 유지 |
| **brushed(metal)** | **없음** | — | — | — | **미해결.** 보유분 전멸: `metal_rust` slope −1.54 ✗ · `granite_dark` RMS 0.093 ✗ · `sandstone` macro 16.7 ✗ ⇒ **절차 생성(이방성) 또는 별도 조달 웨이브** |

**v1 §3.2 의 CC0 후보표는 판정을 보류한다** — 표의 macro% 수치(Plaster001 14.4 / Concrete034 72.6 등)는
**폐기된 정의로 측정**됐고, 다운로드본이 scratchpad 소멸로 **재측정 불가**다. URL·라이선스·zip 내용물
확인은 유효하므로 **조달 경로로만 승계**한다:

| 에셋 | URL | 승계 항목 | v1.1 상태 |
|---|---|---|---|
| Plaster001 | `https://ambientcg.com/get?file=Plaster001_1K-JPG.zip` (7.41 MB) → `Plaster001_1K-JPG_NormalDX.jpg` | CC0 1.0 · zip 내용물 확인됨 | **재측정 대기**(§3.4 정의로) |
| Plaster004 | `https://ambientcg.com/get?file=Plaster004_1K-JPG.zip` | 동 | 재측정 대기 |
| SurfaceImperfections017 | `https://ambientcg.com/view?id=SurfaceImperfections017` (40×40 cm) | 동 | 재측정 대기. v1 의 "RMS 0.011 = 단독 불가" 판정은 **RMS 가 정의 변경 무관**이라 유효 |
| Concrete034 | `https://ambientcg.com/view?id=Concrete034` | **Color 가 선형 (0.482,0.482,0.482) 완전 중성** | 디테일 노멀로는 재측정 대기 / **§5 밝은 콘크리트 승격용으로는 1순위 유지**(색 판정은 정의 무관) |
| Grass001 `[v1.1 G4]` | `https://ambientcg.com/view?id=Grass001` → `Grass001_1K-JPG.zip` | 실측 타일 **1.40 m** · CC0 | **조달 확정**(§1.8④) |

Poly Haven 경로(대안): `https://api.polyhaven.com/files/brushed_concrete` 가 `nor_dx` 를 1k/2k/4k/8k · jpg/png/exr 로
제공함을 API 로 확인 [실측 2026-07-29]. CC0 + AI 학습 명시 허용. 다만 물리 타일이 2.5 m 라 매크로가 실릴 위험이 있어
**도입 전 §3.1 기준 측정 필수**.

### 3.3 권고 — 1순위는 **절차 생성**이다 (라이선스 0 · 스펙트럼 조정 가능)

우리의 진짜 결손은 "그레인이 없다"가 아니라 **`slope` 가 −2.19 로 실사(−2.033±0.184)보다 가파르다**는 것이다
[실측 §2.2 · `imgstats.py:67` 실사 n=54]. 사진 유래 디테일맵은 스펙트럼을 **고를 수 없지만**, 절차 생성은 고를 수 있다.

**`[v1.1 R2]` β 규약 정정 — v1 의 β 표는 폐기한다.**
v1 은 β 를 **진폭 지수**(amplitude ∝ f^−β)로 썼고 본 개정은 **파워 지수**(power ∝ f^−β)로 고정한다.
두 규약은 **2배 차이**가 나며, v1 의 "β=0.5 권고" 를 파워 규약으로 읽으면 전혀 다른 맵이 나온다.
**고정 규약: `power ∝ f^−β` · 노멀 = 높이장의 그래디언트 ⇒ `slope_n ≈ 2 − β`.**

대역제한 백색잡음 → 높이장 → 노멀 (numpy+PIL, 시드 고정, 약 30줄) — **§3.4 정의로 실측**:

| β (파워 규약) | 실측 slope_n | macro% | hf% | RMS | §3.1 판정 |
|---:|---:|---:|---:|---:|---|
| 0.0 | **+1.83** | 0.0 | 77.7 | 0.200 | ✗ slope 상한 초과 |
| 0.5 | **+1.36** | 0.0 | 71.7 | 0.200 | ✗ (v1 이 권고한 값 — **상한 초과**) |
| 1.0 | +0.87 | 0.1 | 64.4 | 0.200 | ✗ 상한 초과 |
| 1.5 | +0.37 | 0.3 | 55.7 | 0.200 | ✗ 근소 초과 |
| **2.0** | **−0.13** | **1.0** | **45.7** | **0.200** | **✔ 전 항목 통과 — 채택** |

[실측 2026-07-29 · 1024² 생성 후 §3.4 파이프라인 측정 · numpy+PIL · GPU 0 · seed 7 · `nyq_cut 0.45`]

- **채택: β = 2.0**(권장 대역 **1.7 ~ 2.3**, 즉 `slope_n` −0.3 ~ +0.3).
  v1 의 β=0.5 는 파워 규약에서 `slope_n +1.36` = 극단적 청색잡음이라 **신설 상한에 걸린다.**
- **완전 타일러블**(FFT 합성이라 경계 연속) · **등방** · **매크로 ≤ 1 %** · **RMS 를 진폭으로 직접 지정**
  (위 표는 전부 `rms_target=0.20` 으로 고정했고 5개 β 전부 정확히 0.200 이 나왔다 — 제어 가능성 실증).
- 나이퀴스트 근방(`f > 0.45`) 컷으로 **앨리어싱 방지** — 현행 변위 스킨이 M4 로 겪었던 문제의 재발 차단.
- 산출: `assets/detail_grain_{mineral,granular,brushed}_nor.png` + 생성 스크립트 `assets/gen_detail_normal.py`(재현 가능·시드 고정).
  - `mineral`: β=2.0 · RMS **0.18** (`plaster_nor_dx` 0.159 근방, 등방)
  - `granular`: β=1.8 · RMS **0.28** (`asphalt_nor_dx` 0.294 근방)
  - `brushed`: β=2.0 **이방(u 축 ×0.25 스케일 이방 필터)** · RMS **0.14** — 보유분 전멸이라 **절차 외 대안 없음**
- `gen_detail_normal.py` 는 **생성 직후 `scripts/norm_spec.py` 를 import 해 §3.1 자가검증**하고,
  불통과 시 **exit 1**(파일을 남기지 않는다). 이것이 §3.4 스크립트가 선행 조건인 이유다.
- **결정 필요**: 절차 단독 / 보유분 단독(`plaster`+`asphalt`) / 혼합. **파일럿 3씬에서 3안 A/B** 권고.
  v1 이 적은 "Plaster001 × 0.3 혼합안"은 **재측정 전까지 후보에서 뺀다**(수치 근거가 폐기됨).

---

### 3.4 **측정 스크립트 3종 재작성 사양** `[v1.1 R2 — 신설 · W2 선결]`

레드팀 §5·§8-1: "**측정기 소멸 — 양 스펙 공통 구멍.** `near_ground_stats.py`·`norm_spec.py`·`skyline.py`
모두 scratchpad 소멸이고 **재작성 작업이 어느 실행 순서에도 없다**." [실측 재확인 2026-07-29 —
`ls scripts/` 에 3개 전부 부재, `rt_assets/` 디렉터리 자체가 없음]

**3종 전부 `scripts/` 에 저작한다.** 정의가 문서가 아니라 **코드로 고정**되는 것이 목적이다.
공통 규약: numpy+PIL 만 · GPU 0 · **stdout 표 + `--json` 옵션** · 인자는 glob 패턴 · **부작용 0**.

#### (a) `scripts/norm_spec.py` — 노멀맵 접선 스펙트럼 (**§1.2·§3.1·§3.3 의 유일한 정의 원천**)

```
사용: python3 scripts/norm_spec.py 'assets/**/*_nor*.jpg' [--json out.json] [--n 1024]

1) 로드      PIL → RGB uint8 → float32/255.  **sRGB 역감마 적용 금지**(노멀맵은 선형 데이터)
2) 접선 성분 nx = 2R − 1 ,  ny = 2G − 1        (B/nz 는 쓰지 않는다 ⇒ DX/GL 구분 불요)
3) 크롭      네이티브 해상도에서 **중앙 정사각 N=1024** 크롭. **리샘플·다운샘플 금지**(계단 0단).
             원본 변이 1024 미만이면 N = min(변) 로 낮추고 N 을 출력에 각인.
4) 창함수    분리형 Hann  w = np.hanning(N) ,  W = outer(w, w)
             **창 가중 평균을 먼저 뺀다**:  x' = (x − Σ(W·x)/ΣW) · W        ← 재현 실패의 주 분기점
5) FFT       F = fftshift(fft2(x'))  ,  P = |F_nx|² + |F_ny|²    (두 접선 성분 파워 합)
6) 방사 링   r = rint(hypot(dy, dx))  (중심 기준 정수 픽셀) ,  r_nyq = N/2
             cnt[r] = 링 화소 수 ,  sm[r] = 링 파워 총합 ,  prof[r] = sm[r]/cnt[r]
7) 정규화    T = Σ_{r=1..N/2} sm[r]        ← **링 총합 가중**(링 평균 가중 아님). DC(r=0) 제외
8) 지표      macro%  = 100 · Σ_{r=1..N/32−1} sm[r] / T          (N=1024 → r ∈ [1, 31])
             hf%     = 100 · Σ_{r=N/4..N/2}  sm[r] / T          (N=1024 → r ∈ [256, 512])
             slope_n = log10 prof[r] vs log10 r 최소제곱, **구간 3 ≤ r < N/4** (prof>0 만)
             RMS     = sqrt(mean(nx² + ny²))  — **크롭 원본 기준**(창·평균제거 이전)
9) 판정      --gate 옵션 시 §3.1 문턱으로 PASS/FAIL. 종료코드 = FAIL 수
```
**검증 앵커(재작성본이 반드시 재현해야 하는 값)** — 아래와 소수점 1자리까지 일치해야 정본이다:

| 앵커 맵 | slope_n | macro% | hf% | RMS |
|---|---:|---:|---:|---:|
| `assets/scene01/concrete_wall_nor_dx.jpg` | −0.71 | 4.1 | 18.9 | 0.056 |
| `assets/scene01/asphalt_nor_dx.jpg` | −0.66 | 3.2 | 13.3 | 0.294 |
| `assets/scene01/stone_flag_nor_dx.jpg` | −2.46 | 58.4 | 2.5 | 0.192 |
| `assets/paving_interlock_nor.jpg` (2048²) | −1.98 | 52.3 | 4.8 | 0.449 |

#### (b) `scripts/near_ground_stats.py` — 근경 밴드 지표 (**ground_kit §7.1 렌더 후 게이트의 측정기**)

`ground_kit_spec_v1.md` §7.1·부록 B 가 인용하는 도구. 게이트 값이 이 도구의 정의에 걸려 있다.

```
사용: python3 scripts/near_ground_stats.py 'look_check/scene15/*/pt_noon_preset_h0.3_d*.png'

밴드   B45 = 하단 45 % (rows[int(0.55·H):])   ·   B30 = 하단 30 % (rows[int(0.70·H):])
휘도   Y   = 0.2126R + 0.7152G + 0.0722B  on **sRGB 표시값 0~255**(선형화 금지 — 게이트가 표시값 기준)
지표
  sd      = Y.std()                                  on B45   게이트 ≥ 32 (WARN), 목표 45
  mean    = Y.mean()                                 on B45   게이트 ≤ 170
  p99     = percentile(Y, 99)                        on B45   보고만
  >224%   = 100·mean(Y > 224)                        on B45   게이트 ≤ 5
  wht%    = 100·mean(min(R,G,B)/255 > 0.80)          on B30   게이트 < 2  (= §2.2 w80 과 같은 정의)
  flat%   = 100·mean(local_std(Y/255, 5) < 1/255)    on B45   게이트 < 8
  **σ_LF** = 100 · std( box_downsample(Y/255, 64) )  on B30   게이트 ≥ 5.0 (WARN), 목표 11.0
  edge    = mean(|∇Y|)  (Sobel)                      on B45   보고만
σ_LF 규약: **64× 박스 평균 다운샘플**(reshape-mean, 보간 금지). H,W 가 64 로 안 나눠떨어지면
           **우/하단을 잘라내고**(패딩 금지) 다운샘플한다 — 패딩은 가장자리에 가짜 저주파를 만든다.
```
> **경고 승계**: σ_LF·sd 문턱은 실사 n=8·n=10 유도값이다. `ground_kit` §7.1 이 **"W2 에서는 WARN 만,
> FAIL 로 올리지 않는다"** 로 못박았고(imgstats flat%/slope 게이트가 n=2 로 정해졌다 n=54 에서
> 뒤집힌 전례), T1 도 이 규약을 그대로 승계한다.

#### (c) `scripts/skyline.py` — 스카이라인/중경 지표 (E조 조사가 의존)

```
사용: python3 scripts/skyline.py 'look_check/scene19/*/pt_noon_preset_h0.3_d*.png'

하늘 판정  픽셀이 하늘 = (B > R) and (B > G) and (min(R,G,B)/255 > 0.35)   ← 무운 puresky 전용 규칙.
           **HDRI 가 바뀌면 이 규칙을 재검증할 것**(정의 고정의 대가).
지표
  sky%      = 100 · mean(sky mask)                         전 프레임
  horizon[c]= 각 열 c 의 **최초 비하늘 행**(위→아래). 전부 하늘이면 H
  edge_std  = std(horizon)                                 스카이라인 요철
  runmax    = horizon 이 **±2행 이내로 평탄한 최장 연속 열 수**   목표 ≤ 320 px
  flat%     = 100·mean(local_std(Y/255,5) < 1/255)         상단 1/3(= imgstats flat_sky 와 동일)
거리대 라벨링은 프림 거리가 필요하므로 **본 스크립트 범위 밖** — `--bands L,M,R` 로 열 구간 3분할만 제공.
```

> **T1 의 의존도**: (a) 는 §3.1·§3.3 자가검증의 **전제**라 **단계 3 착수 전 필수**.
> (b) 는 ground_kit 게이트용이지만 T1 §7.3 파일럿의 근경 판정에도 쓴다 — **단계 5 전 필수**.
> (c) 는 T1 직접 의존 없음(중경 웨이브용) — **W2 중 여유 시**. 3종 다 GPU 0 · 반나절.

---

## 4. 절차 웨더링 · 헥스 타일링 사양

### 4.1 웨더링 — 구현은 끝났고, 남은 것은 `grime_z0` 통로 (약 30줄)

현행(무영향 기본값·조기 반환 설계) [실측 `NegObsGround.mdl:428-506`]:

| 마스크 | 상태 | 현행 값 |
|---|---|---|
| ① 기단 오염 밴드 + 접지 AO (월드 Z) | **비활성**(치명 C4) | `grime_strength=0` |
| ② 스플래시 존 0.15~0.50 m | **비활성**(동상) | `splash_strength=0` |
| ③ 상향면 먼지 `normal.z>0.6` | 활성 가능 — **현재 클래스 값 0** | `dust_strength` 미설정 |
| ④ 하향 줄무늬(수직면) | **활성** | `streak` 0.08~0.12 · `wrough` 0.10~0.15 |

**추가 사양 A — `foot_z` primvar 통로 (약 20줄)**
- `add_box`/`_oriented_box`/`add_cylinder` 가 프림 생성 시 **constant primvar `foot_z` = center.z − size.z/2** 를 저작.
- MDL 은 `scene::data_lookup_float("foot_z", 0.0)` 로 읽어 `grime_z0` 를 **프림별로** 대체
  (기존 `blend_tw` 조회와 동일 패턴이라 신규 위험 없음 [실측 `:690`]).
- **지름길 안전성 논증(필수 기록)**: 밴드는 "그 프림의 발치 기준 0~0.35 m" 로 정의되므로
  **낙차 깊이와 무관**하다. 1 m 옹벽과 3 m 옹벽이 **동일한 밴드**를 받는다 → GT 낙차와 상관 0.
  (C4 가 지적한 "깊을수록 어두워짐"은 월드 Z 절대 기준일 때만 발생한다.)
- 재활성 후 **검증 필수**: sceneD3(측구 깊이 0.80·인버트 −1.05)에서 인버트 바닥과 노면의
  평균 휘도 차가 재활성 전후로 **±2% 이내**여야 한다(밴드가 깊이를 인코딩하지 않음의 증거).

**추가 사양 B — dust 활성화 (약 10줄)**
`_W_STRUCT/_W_STONE` 에 `dust=0.10, dust_desat=0.20` 추가. 상향면(normal.z>0.6)만 걸리므로
수직 파사드에는 무영향이고, **h0.3 시점에서 화면의 55~75%가 상향면**이라 프레임 점유율 기준 최대 효과.
지면 계열(`paving/asphalt/soil/gravel`)은 **dust 도 0 유지** — 이미 텍스처가 있고, 균일 암화는 flat% 를 되돌린다.

### 4.2 헥스 타일링 (약 45줄) — 모듈형 포장의 반복 파괴

**근거 재승격**: Phase1 §4.3 이 "patch 혼합과 중복" 으로 강등했으나, 그 patch 를 모듈형 포장에서
0 으로 끈 것이 현행이다(§1.3). 헥스 타일링은 **회전 없이 오프셋만**으로 반복을 깰 수 있어
"모듈 방향성 보존"과 "반복 파괴"를 동시에 만족하는 유일한 수단이다.

```mdl
// [T1] 헥스 격자 3샘플 블렌드 (Heitz & Neyret 2018 의 격자 + 분산보존 블렌딩)
//  · 모듈형 포장: rot=0 (오프셋만) — 블록 방향 보존
//  · 자연 지면  : rot=1 (오프셋 + 셀별 90/180/270° 회전)
struct NegObsHex { float3 w; float2 o1; float2 o2; float2 o3; };

float2 negobs_hash2(float2 p) {                       // 결정적 해시(셀 → 오프셋)
    float n1 = math::frac(math::sin(p.x * 127.1 + p.y * 311.7) * 43758.5453);
    float n2 = math::frac(math::sin(p.x * 269.5 + p.y * 183.3) * 43758.5453);
    return float2(n1, n2);
}

NegObsHex negobs_hex_cells(float2 uv) {
    // 정삼각 격자로 스큐 → 삼각형 무게중심 좌표가 곧 블렌드 가중치
    float2 s = float2(uv.x + uv.y * 0.5, uv.y * 0.8660254);
    float2 fl = math::floor(s);
    float2 fr = s - fl;
    NegObsHex H;
    float2 v1, v2, v3;
    if (fr.x + fr.y < 1.0) {
        H.w = float3(1.0 - fr.x - fr.y, fr.y, fr.x);
        v1 = fl;  v2 = fl + float2(0.0, 1.0);  v3 = fl + float2(1.0, 0.0);
    } else {
        H.w = float3(fr.x + fr.y - 1.0, 1.0 - fr.x, 1.0 - fr.y);
        v1 = fl + float2(1.0, 1.0);  v2 = fl + float2(1.0, 0.0);  v3 = fl + float2(0.0, 1.0);
    }
    H.o1 = negobs_hash2(v1);  H.o2 = negobs_hash2(v2);  H.o3 = negobs_hash2(v3);
    return H;
}

// 분산 보존 블렌드: 평균을 빼고 w/||w|| 로 섞은 뒤 평균을 되돌린다.
// 단순 가중평균은 3장을 섞는 순간 국소대비가 1/√3 로 줄어 **flat% 를 되돌린다**.
// tex_mean 은 Python 쪽 `_texture_mean()` 실측값을 파라미터로 넘긴다(선형).
color negobs_hex_blend(color c1, color c2, color c3, float3 w, color tex_mean) {
    float3 wn = w / math::max(w.x + w.y + w.z, 1e-6);
    float  k  = math::sqrt(wn.x * wn.x + wn.y * wn.y + wn.z * wn.z);
    return tex_mean + ((c1 - tex_mean) * wn.x + (c2 - tex_mean) * wn.y
                     + (c3 - tex_mean) * wn.z) / math::max(k, 1e-6);
}
```

**적용 규칙 (비용 통제 — 이것이 없으면 성능 사고가 난다)**

| 항목 | 값 | 이유 |
|---|---|---|
| 적용 평면 | **지배 평면 1장만** (triplanar 3평면 전부 X) | 3평면 × 3샘플 = 9배. 지배 평면만이면 3배 |
| 적용 조건 | `hex_strength > 0` **그리고** 지배 평면 가중치 > 0.9 | 경사 전이대는 tri_dither 가 이미 담당 |
| 맵 | **albedo + normal 만**. roughness 는 단일 샘플 유지 | roughness 는 저주파 — 반복이 안 보인다 |
| `patch_mix` 와의 관계 | **상호배타**. `hex>0` 이면 `patch_mix` 를 0 으로 강제 | 둘 다 켜면 6샘플. 자연 지면은 헥스(회전 ON)로 통합 |
| 셀 크기 | `hex_scale` = 타일 3~5개분(모듈형은 정수배 필수 — 반칸 어긋남 방지) | 블록 줄눈이 셀 경계에서 끊기지 않게 |
| 기본값 | `hex_strength = 0.0` | **회귀 0 보장** — 기존 씬 픽셀 동일 |

**예상 비용**: 현행 `patch_mix=0` 경로가 재질당 최대 9 페치(3맵×3평면) [실측 — MDL v1.8.0 조기 탈출 주석].
헥스 도입 시 albedo·normal 만 지배 평면에서 3배 → 9 + 4 = 13 페치, **약 1.45배**.
v1.8.0 이 patch 조기 탈출로 7.6배를 벌어 둔 예산 안이다 [실측 `realism_phase2.md` §3.2].
단 **파일럿에서 s/컷 실측 후 전 씬 확대** — sceneD3 가 22s → 404s(18배) 로 터진 전례가 있다.

---

## 5. 순백 하향 + 채도 캘리브레이션

### 5.1 핵심 발견 — 순백과 저채도는 같은 현상이다 [실측]

33씬 h0.3 에서 **w80(순백 면적) vs sat_mu 스피어만 = −0.630** (n=33).
w80 > 60% 인 8씬(01·05·18·19·20·C1·N1·N5)의 sat 중앙값 **0.094**, 나머지 25씬 **0.179**.

원인은 명확하다 — 표시값이 상단에서 클리핑되면 채널 간 차이가 함께 죽는다.
scene19 가 극단: **w80 97.7% · w87 72.3% · sat 0.028 · flat_gnd 10.0**.

⇒ **채도를 올리려 손대면 안 된다. 알베도를 내리면 채도·국소대비가 함께 돌아온다.**
전역 채도 하향은 정반대로 위험하다 — 33씬 중 **15씬이 이미 목표 하한(0.15) 미만**이다(§2.2).

### 5.2 톤 하향 — 확정 · 이월 · 신규

| # | 대상 | 현행 | 목표 | 근거 | 상태 |
|---|---|---|---|---|---|
| T-1 | **전역 `plaza_light` 틴트** — **무틴트 사용 씬은 5개가 아니라 9개다**(아래 정정) | 무틴트, 선형 알베도 **0.469** | **×0.72 → 0.338** (예상 표시 235→**203**) | X-1 §12 감독 결정 "차기 전역 라운드 이월" | **이월 확정 — 이번에 집행** |
| **T-1b** `[v1.1 G2]` | **동 `scale_m`** — 같은 `make_pbr` 호출의 인자라 T-1 과 **분리 집행 불가** | **0.75(7씬) / 0.8(14·21)** | **1.80 (9씬 통일)** | `ground_kit` §4.4·§9.3 이관. 값 출처 = `GROUND_DIMENSIONS["module_*"]` | **신규 — T-1 과 동일 커밋·동일 라운드**(§1.8②) |
| T-2 | scene19 `Parapet` | 0.90,0.90,0.87 | **0.70** | v5.1 §4 순백 대면적 위반. w87 72.3% | 신규(X-1 이 09/12 만 처리) |
| T-3 | sceneC1 `Snow` | 0.72,0.74,0.78 | **0.58** | `LOOK_CLASS` snow 주석의 TODO. 텍스처 조달 완료(선형 0.474) | 신규 |
| T-4 | scene14/21 `Parapet`·`Bldg` | 0.62/0.72 | 유지 + **`plaster` 승격 분기** | 색이 아니라 결이 문제(flat_gnd 31.3/40.4) | 신규 |

**물리 근거**: 회색 포틀랜드 콘크리트 포장의 태양반사율은 **신설 0.35~0.40 · 노후 0.20~0.30**,
백색 시멘트라야 0.70~0.80 [논문/통계 — LBNL Heat Island Group / ACPA RT3.05].
현행 0.469 는 **신설 회색 콘크리트보다 밝아 백색 시멘트 대역**이다. 0.338 은 신설 회색의 하단에 착지한다.
(더 내려 0.60~0.65 틴트 = 0.28~0.30 이면 "노후 포장"으로 물리적으로 더 정확하지만,
**0.72 는 감독이 승인한 이월값**이므로 임의 변경하지 않는다. 파일럿에서 0.72/0.65 두 값 A/B 를 권고.)

**정정 — T-1 대상 씬 목록 [실측 2026-07-29, 33씬 전수 grep]**
X-1 §12 는 "01/05/14/18/19 가 무틴트 `plaza_light` 를 공유" 라고 적었으나 **불완전하다.**

| 무틴트(= T-1 대상, **9씬**) | 이미 틴트 적용(대상 아님) |
|---|---|
| **01**(PlazaLight·PlazaLower) · **05**(PlazaLight·Stage) · **14**(PlazaLight) · **16**(Stair) · **18**(Upper) · **19**(Upper·Step) · **20**(Upper) · **21**(Plaza) · **N3**(LightStone) | N1 `plaza_tint` · N2 `walk_tint` · N5 `pave_tint` · N3 `Podium` `podium_tint` |

[실측 — `grep -n -A4 'tex_path("plaza_light", "diff")'` 전 33씬. 예: `scene16:296`·`scene20:266`·`scene21:358`·`sceneN3:761` 에 `tint=` 인자 없음]

**주의(회귀)**: 9씬 공유이므로 **9씬 동시 적용 + 동시 재렌더**가 조건이다(X-1 §12 사유 그대로).
5씬만 내리면 나머지 4씬(16·20·21·N3)과 톤이 갈라져 21씬 시트 정합이 오히려 더 깨진다.
h0.3 w80 이 낮은 씬(16=0.8 · 21=1.4 · N3=1.0 · 14=5.4)도 **재질 공유가 이유**이지 면제 사유가 아니다.
[재현 2026-07-29 — 본 개정이 w80 을 독립 재측정(하단 2/3 · **sRGB 표시값** min(R,G,B)>0.80 · 3컷 중앙값):
19 = **97.7**(w87 **72.3**) · 01 = 87.6 · 14 = 5.3 · 21 = 1.4 · 07 = 0.8 · C2 = 0.0.
§2.2 표(각각 97.7 / 88.2 / 5.4 / 1.4 / 0.3 / 0.0)와 **±0.6 pp 내 일치** — 측정 파이프라인 교차 검증 성립]

**`[v1.1 G2]` 톤과 `scale_m` 은 한 몸이다** — 둘 다 같은 `sc.make_pbr(..., sca["plaza_light"], tint=…)`
호출의 인자다. 톤만 먼저 내리고 다음 라운드에 스케일을 바꾸면 **그 사이 라운드의 9씬 렌더가 통째로
버려진다.** 집행 단위는 **{9씬} × {톤 ×0.72, scale_m 1.80}** 하나다.
**A/B 대상이 아니다** — 씬 파일 인자라 `LOOK_MTL` 게이트 밖이고 양팔에 동일하게 걸린다.
검증은 **before/after 라운드 + `regression_check`** 로만 한다(§7.2-7).

### 5.3 채도 — 전역 금지, 3구간 처방

현행 자기교정(`_effective_sat`, knee 0.18, `scene_common.py:485-499`)은 **하향 전용**이다. 유지하되:

| 구간 | 씬 | 처방 |
|---|---|---|
| **과채도** (sat > 0.25) | 04(0.437) · D4(0.450) · 10(0.394) · 03(0.309) · C2(0.302) · D3(0.280) · 15(0.270) · D2(0.260) · 07(0.254) | 현행 knee 유지 + `veg`(0.76)·`soil`(0.74)에 이미 계수 있음. **`sign`·`paint` 계열도 점검**(D4 의 0.450 은 사인 다수 — §2.1 sign 4종) |
| **목표대** (0.15~0.22) | 09 · 17 · 12 · D1 · 06 · 11 · 21 · C4 | 손대지 않는다 |
| **저채도**(sat < 0.15, **15씬**) | 19(0.028) · 05 · 18 · 16 · 02 · N5 · 01 · N2 · N3 · 20 · 14 · N1 · C1 · N4 · 13 | **채도로 접근 금지.** §5.2 톤 하향 → 자동 회복. 톤 대상이 아닌 씬(02·16·13·N2·N3)은 **디테일 노멀·헥스**로 국소대비를 먼저 회복시키고 재측정 |

**금지**: 전역 채도 상수 곱, `saturation_a > 1.0`(과포화 주입). 채도는 결과 지표이지 조작 대상이 아니다.

---

## 6. T0 스파이크 의존 항목 — **`[v1.1 T1~T5]` 실측 보고로 전면 갱신**

`Docs/reports/t0_spike_report_v1.md`(2026-07-29 · Isaac Sim 4.5.0 / RTX 4090)가 실제로 돌았다.
v1 이 "Phase1 문서 인용" 으로 적었던 칸이 **실측으로 대체**됐고, **2칸이 뒤집혔다.**

| 항목 | ZZ §6 T0 요구 | **v1.1 상태(T0 실측)** | 근거 | T1 의존성 |
|---|---|---|---|---|
| `round_edges_radius` | 최고 ROI·미검증 | **GO · 채택.** RT·PT 양쪽 작동, 밴드폭이 `px ≈ 24·(r/d)·57.3` 를 실측 재현 | [실측] `t0_spike_report_v1.md` §2.3 | **있음** — §6.1 A/B 방법론 제약 신설 |
| `subdivisionScheme=catmullClark` | 미검증 | **기각 유지**(기본 `refinementLevel=0` = 세분 없음; 1 이상에서만 진짜 세분, crease 는 존중) + **신규 규약**: 새 메시는 반드시 `CreateSubdivisionSchemeAttr("none")` — 미저작 = USD 기본 `catmullClark` = **level 0 에서도 조용한 스무스 노멀** | [실측] 동 §3.1·§3.2·§3.3 | **없음**(단 규약 준수 필요) |
| **MDL 효과 정량** | 1씬 바인딩 후 개선폭 | **`[v1.1 뒤집힘]` 단독 바인딩 효과 = 실측 0.** sceneC2 에서 `flat% 20.391 → 20.391`(Δ 0.000 pp) · `slope −1.683 → −1.689`. h0.3 d2 는 **PSNR 60.03 dB · >1 LSB 픽셀 0.01 %** = 사실상 동일 | [실측] 동 §1.2·§1.4 | **있음** — §6.2 적용 대상 원칙 |
| 디테일 노멀 | "즉시 사용" | **OmniPBR 경로만 검증**(E3). **MDL 경로 미구현** | [실측] `realism_phase1.md` §2.3 | **있음** — §1.6(a) 구현 후 A/B |
| 헥스 타일링 | — | **미구현·미검증** | — | **있음** — §4.2 구현 후 A/B |
| **렌더 처리량** | — | **`NEGOBS_PT_FAST=1` 실증 — 13.5 → 0.95 s/컷(14.2배), 회귀 0.** PT 가속이 RT warmup 90 보다도 빠르다 | [실측] `t0_spike_report_v1.md` §5.1·§5.2 | **있음** — §7.5 예산 |
| **재질 비용** | — | **MDL 바인딩만으로 PT 컷당 13.18~13.71 → 15.33~20.97 s = +13~55 %**. `LOOK_V1` 전량은 21.58~31.33 s = **1.6~2.3배** | [실측] 동 §5.1 | **있음** — §7.5 예산 |
| 자동노출 | — | **AE 는 꺼져 있다**(`/rtx/post/histogram/enabled = False`). 기존 밝기 A/B 판정 전부 유효 | [실측] 동 §7.1·§7.3 | **없음** — §5 톤 판정의 전제 확인 |

### 6.1 `[v1.1 T4]` 베벨 — **GO. 단 A/B 방법론에 하드 제약이 붙는다**

**★ 방법론 경고(실측)**: T0 이 기존 랩(`scripts/spike_realism.py` E1)과 5박스 배열로 재봤을 때
0 mm vs 20 mm 에서 **전면 전체 +44 LSB** 라는 거대한 차이가 나왔는데, 이는 베벨 효과가 아니라
**경사 태양 아래 좌우 끝 박스의 조도차**였다 [실측 `t0_spike_report_v1.md` §2.2].

> **규칙 R-7 `[v1.1]`** — 베벨(및 모든 셰이더 입력) A/B 는 **같은 프림·같은 카메라·같은 조명**에서
> **셰이더 입력만 런타임 토글**해 찍는다. **반경별로 다른 프림을 다른 위치에 두는 랩은 금지**한다.
> 이는 §1.7.2 R-1(프림 불변)의 렌더 측 대응물이며, 위반 시 수치는 전량 무효다.

**실측 밴드폭**(화강암 roughness 0.25, `|Δ| > 2 LSB` 유지 행 수) [실측 동 §2.3]:

| 거리 | 프로파일 | r=2 mm | r=5 mm | r=10 mm | r=20 mm | 예측 px |
|---|---|---:|---:|---:|---:|---|
| d≈1.4 m | RT | 2 | 2 | 5 | **16** | 2.0 / 4.9 / 9.8 / 19.6 |
| d≈1.4 m | **PT** | 3 | 6 | 11 | **23** | 〃 |
| d≈2.6 m | PT | 1 | 3 | 5 | 9 | 1.1 / 2.6 / 5.3 / 10.6 |
| d≈5.6 m | PT | 0 | 2 | 2 | 4 | 0.5 / 1.2 / 2.5 / 4.9 |

모서리 최대 휘도차 d1.4 에서 **−33.0 LSB(RT) / −35.4 LSB(PT)** @20 mm.

**적용 사양 — 재질 클래스별 반경(현행 `LOOK_CLASS["<cls>"]["bevel"]`, 단위 m)** [실측 `scene_common.py:238-295`].
T0 이 "현행 값은 이 실측과 정합한다" 로 확인했으므로 **값을 바꾸지 않는다.** 문서화만 한다:

| 클래스 | `bevel` [m] | d=2 m 화면폭 [px] | d=5 m | 근거 |
|---|---:|---:|---:|---|
| **concrete** | **0.020** | 13.8 | 5.5 | 현장타설 모접기 20~30 mm `[시방]` KCS 21 50 05 |
| **nosing** | **0.012** | 8.3 | 3.3 | IBC 1.6~14.3 mm 상단(국내 규정 부재 — 전수 확인) |
| **curb** | **0.010** | 6.9 | 2.8 | 연석 수직형 R=10 `[예규]` 321호 그림 2.17 |
| paving · brick · asphalt | 0.006 | 4.1 | 1.7 | 모듈 모접기 |
| stone · wood | 0.004 | 2.8 | 1.1 | `[근거 없음]` 보수적 하향(현행 주석 그대로) |
| misc | 0.003 | 2.1 | 0.8 | 보수적 |
| metal | 0.002 | 1.4 | 0.6 | 판재 |
| soil · gravel · snow · veg · water · glass · paint · sign | **0.000** | — | — | 모접기 개념 없음 |

화면폭 = `24·(r/d)·57.3` px [실측 재현식, Phase1 §2.1].

- **비용 0 이므로 걸되, 이것으로 지표가 움직일 것을 기대하지 않는다.** 효과 회수는 **근접 컷 전용**이다
  [실측 T0 §2.5]. ⇒ §7.2-4 **근접 크롭 판정이 베벨의 유일한 판정 수단**이다.
- MDL 측 배선은 이미 있다 — `round_edges_radius/roundness/across_materials` [실측 `NegObsGround.mdl:589-593`],
  합성은 `:754-757` 의 `state::rounded_corner_normal` 1차 가산.
- **`bevel` 은 `LOOK_MTL` 소속**(셰이더 입력이지 기하가 아니다). R-1 위반 아님.

### 6.2 `[v1.1 T5]` **MDL 적용 대상 원칙 — "어느 재질"이 아니라 "h0.3 프레임을 실제로 채우는 표면"**

T0-3 이 sceneC2 에서 MDL 단독 효과 0 을 실측했고, **원인을 커버리지로 특정**했다 [실측 §1.4]:

```
c2_B_mdl/t0_timing.json → stat:   ground=4   keep=18
roles = {veg:14, curb:2, soil:2, metal:2, stone:1, wood:1}
```
- `make_pbr` 22개 호출 중 **MDL 이 걸린 것은 4개**(석재 1 · 경계석 2 · 흙 1) = **18 %**.
- **`veg` 가 14개로 최다**인데 `LOOK_CLASS["veg"]["mdl"] == "omni"` 라 MDL 대상이 아니다.
  sceneC2 의 h0.3 화면을 채우는 것은 **낙엽 마운드·낙엽 산포·잔디**이고 전부 여기 속한다.
- 그래서 최근접 컷(h0.3 d2)이 A/B 사실상 동일(PSNR 60.03 dB)이고, **원경 컷만 크게 바뀐다**
  (d5 PSNR 22.58 dB · >8 LSB 42.4 % / d10 21.33 dB · 56.2 %) — "육안 변화는 있는데 지표가 안 움직인다"
  는 Phase1 E9 경고가 프로덕션 씬에서 재현.

> **원칙 P-1 `[v1.1]`** — T1 재질층의 어떤 항목도 **"클래스 커버리지"로 정당화하지 않는다.**
> 정당화 단위는 **그 씬 h0.3 프레임의 하단 2/3 을 실제로 점유하는 표면**이며,
> 측정 원천은 `const_color_texture_map.md` §0-3 레이캐스트 `gnd%`(= `flat_gnd` 와 동일 영역 정의)다.
>
> **원칙 P-2 `[v1.1]`** — 따라서 **T1 최우선 순위는 "MDL 이식"이 아니다.** T0 §1.7-1 의 결론
> ("MDL 이식 = T1 최우선 순위를 내려야 한다. 단독 효과가 실측 0")을 수용한다. 우선순위는
> **① MDL 이 닿는 면적 확대(veg 라우팅 재검토·`tex=` 미연결 클래스 연결) → ② 톤 하향(§5.2) →
> ③ 디테일 노멀(§1.6) → ④ 헥스(§4.2)** 다. 단 §1.1 의 "죽은 `detail=True`" 는 결손 보수라
> ③ 안에서 그대로 최우선이다.
>
> **원칙 P-3 `[v1.1]`** — `veg` 를 MDL 로 옮기는 것은 **본 스펙 범위 밖**이다(`mdl="omni"` 유지).
> `veg` 지배 씬(C2·04·10·03)에서 재질층 효과가 작을 것은 **예측된 결과**이며 실패로 판정하지 않는다.
> 그 씬들의 개선 소유자는 **실물 USD 식생(P3) + ground_kit 경계 파쇄**다.

### 6.3 분기 계획

**성공 분기** (디테일 노멀 MDL 구현 → 파일럿에서 slope 가 −2.19 → −2.10 이내로 이동, 육안 근접 크롭에서 그레인 확인)
→ 3씬 게이트 → 헥스 타일링 A/B → **톤 T-1 ×0.72 + `scale_m` 1.80 동시(9씬)** `[v1.1 정정 — v1 의 "6씬 동시"는 오기]`
→ `grass` 교체 → 전 33씬 라운드 → 재측정.
(v1 은 "33씬 라운드"를 헥스보다 앞에 뒀으나, **검증 없는 확산 금지**(3회 재발 전례) 규율에 따라
확산은 항목이 다 들어간 뒤 1회만 돈다. 렌더 예산이 약 10분이므로 순서 비용은 무시할 수준이다 — §7.5.)

**실패 분기 A — 디테일 노멀이 안 보인다**(Δslope < 0.05 = §7 판정 문턱 미만)
→ ① `detail_bump_factor` 를 0.85 → 1.5 로 올려 재시도(1회) ② 그래도 안 되면 **원인은 텍셀 밀도가 아니라
   조명·톤매핑 상단 클리핑**이라는 가설로 이동 — **톤 하향(§5.2)을 먼저 집행하고 디테일을 재측정**한다.
   (scene19 sat 0.028 이 이 가설을 강하게 지지한다. 클리핑된 표면에서는 어떤 노멀도 대비를 못 만든다.
   **`[v1.1]` AE 오염 가설은 배제됨** — `/rtx/post/histogram/enabled = False` 실측 [T0 §7.1].)
③ **③ 신설** — 그래도 안 되면 **원칙 P-1 로 되돌아가 "그 씬 h0.3 프레임을 채우는 표면이 정말
   `ground` 클래스인가"를 레이캐스트로 재확인**한다. sceneC2 형 실패(식생 지배)는 강도를 올려도 안 풀린다.

**실패 분기 B — 헥스 타일링이 성능을 깬다**(파일럿 s/컷이 1.5배 초과)
→ ① 지배 평면 조건을 0.9 → 0.98 로 좁힘 ② albedo 만 적용(normal 제외) ③ 그래도 초과 시
   **근경 전용 적용**(카메라 거리 기반 분기는 MDL 에 없으므로, 대신 **큰 슬래브 프림에만** 클래스 사양으로 켬).

**실패 분기 C — R-4 기하 불변 검사가 실패**
→ **즉시 중단.** 재질층에 기하 부작용이 섞였다는 뜻이고, 이 상태의 A/B 수치는 전부 무효다.
   원인 프림을 특정해 `LOOK_GEO` 로 옮긴 뒤 재실행.

---

## 7. 검증 계획

### 7.1 판정 문턱 — sceneC2 라운드 간 실측 [실측 2026-07-29]

`sceneC2` 세 라운드의 h0.3 3컷 동일 파일명끼리 |Δ| (r2_on ↔ balust = 소규모 기하 변경만):

| 지표 | r2_on↔balust 평균/최대 | r2_on↔leaf3d 평균/최대 | **채택 문턱**(= balust 최대의 3배) |
|---|---|---|---|
| slope | 0.011 / **0.015** | 0.191 / 0.291 | **≥ 0.05** |
| flat_gnd | 0.001 / **0.002** | 0.830 / 1.881 | ≥ 0.10 |
| flat_pct | 0.107 / **0.214** | 0.487 / 1.175 | ≥ 0.65 |
| sat_mu | 0.003 / **0.005** | 0.051 / 0.087 | **≥ 0.015** |
| chroma_sd | 0.002 / **0.004** | 0.009 / 0.017 | ≥ 0.011 |
| grad_k | 2.20 / **2.76** | 3.94 / 7.95 | ≥ 8.3 (**판별력 약함 — 보조로만**) |

주: r2_on↔balust 는 **실제 기하 차이를 포함**하므로 이 값은 렌더 노이즈 플로어의 **상한**이다.
따라서 위 문턱은 보수적이다. (Phase2 §4.1 "노이즈 플로어는 씬마다 다르다"와 정합.)

> **`[v1.1 T2]` 이 표의 `leaf3d` 열은 "무처리 기준선"이 아니다.**
> T0 이 픽셀로 확정했다 — `look_check/sceneC2/leaf3d` 는 **이미 `NEGOBS_LOOK_V1=1` 로 렌더된 결과**다.
> 무처리(A) 대비 meanΔ 27.99/34.95/19.14 LSB 인데 **`LOOK_V1` 전량(C) 대비는 4.14/3.94/1.88 LSB**
> [실측 `t0_spike_report_v1.md` §1.5]. 잔차 1.9~4.2 LSB 는 이후 커밋(`5191e3c`·`0addc56`·`c0cef87`)과
> 산포 시드 차이로 설명된다.
> ⇒ 위 표에서 `r2_on↔leaf3d` 열은 **"LOOK_V1 계열 내부의 커밋 드리프트"** 를 잰 것이지
> "룩 ON/OFF 효과"가 아니다. **문턱 산출(= `r2_on↔balust` 열)에는 영향이 없으므로 문턱은 유지**하되,
> `leaf3d` 를 **기준선으로 인용하는 것을 전면 금지**한다.

**`[v1.1 T2]` 기준선 규약 — 3층 구조**

| 기준선 | 정의 | 용도 |
|---|---|---|
| **`look_check/_t0_spike/c2_A_base/`** | **진짜 무처리**(`LOOK_V1=0`, MDL 미바인딩) | "룩 레이어 전체가 무엇을 했는가" 를 묻는 절대 기준선 |
| `r2_on` (452컷) | 현행 프로덕션(`LOOK_V1=1`, MDL v1.8.0, 디테일 미배선) | §2.2 표의 출처. **T1 before/after 의 before** |
| `t1_mtl_off` (신규) | `LOOK_MTL=0 LOOK_GEO=1` | **T1 A/B 의 대조군**(규칙 R-2) |

- **`r2_on` 과 `t1_mtl_off` 는 같지 않다** — 전자는 `LOOK_MTL=1` 이다. 혼동 시 A/B 부호가 뒤집힌다.
- ground_kit 파일럿(N5·15·13)과의 교락 방지: **파일럿 렌더의 재질 상태 = `r2_on` 과 동일
  (MDL v1.8.0 · 디테일 미배선)** 을 라운드 스크립트에 각인한다 [레드팀 §3 권고].

### 7.2 A/B 프로토콜

1. 대조군 = `NEGOBS_LOOK_MTL=0 NEGOBS_LOOK_GEO=1`, 실험군 = `MTL=1 GEO=1`. **기하는 양쪽 동일**(규칙 R-2).
2. **`NEGOBS_PT_FAST=1` — 단일 프로파일로 확정** `[v1.1 T3]`.
   T0 실측: PT 가속 **0.90~0.99 s/컷**(평균 0.95) vs PT legacy 13.18~13.71 = **14.2배**.
   화질 동등성 **PSNR 41.2~43.9 dB · meanΔ 1.0~1.6 · >8 LSB 0.22~0.66 % · `regression_check` FAIL 0**
   [실측 `t0_spike_report_v1.md` §5.1·§5.2]. RT32 도 가능하나 **잔차가 3배 크다**(meanΔ 3.0 vs 1.3)
   — **판정에는 PT 가속만 쓴다.**
   주의: `set_render_mode()` 가 매번 `spp=1,totalSpp=512` 로 되돌리므로 **PT_FAST 분기는 씬 콜백 뒤에
   덮어써야 한다**(코드에 이미 주석으로 명시) [실측 동 §5.3-1].
3. 컷: `pt_noon_preset_h0.3_d{2,5,10}` **필수 3컷** + 씬 미장센 1컷.
4. **근접 크롭 판정 필수** — d2 컷의 하단 중앙 512×512 를 4분할 비교(before/after × d2/d5).
   근거: E1 에서 광각만 보고 "미작동" 오판했다가 근접 크롭에서 뒤집힌 전례 [실측 `realism_phase1.md` §2.1].
   **§6.1 베벨은 이 크롭이 유일한 판정 수단이다.**
5. 매 라운드 `scripts/regression_check.py` 실행(STATUS.md 작업 규율). FAIL 0 · 신규 WARN 사유 기재.
   **`manifest.json` 의 `ok` 플래그를 신뢰해 재렌더하지 말 것** — T0 에서 6컷이 `ok=False` 로 찍혔으나
   **6컷 전부 정상 디코딩**됐다(PNG 크기 안정 판정의 오탐) [실측 동 §5.3-2].
6. `scripts/geom_invariance_check.py` **R-5(잔존 참조 0) → R-4(MTL 0/1 해시) → R-6(V1 3자 해시)** 순으로
   통과하는 것이 **수치 판정보다 선행**한다.
7. **A/B 가 아닌 항목의 검증** `[v1.1]` — `scale_m`(§1.8②) · `grass` 교체(§1.8④ A1) · 톤 T-1 은
   **씬 파일 인자**라 `LOOK_MTL` 게이트 밖이고 양팔에 동일하게 걸린다.
   ⇒ **before/after 라운드 + `regression_check` + h0.3 3컷 육안**으로만 판정한다.
   A/B 표에 섞어 적으면 대조군 오염과 같은 유형의 오판이 된다.
8. **동시 렌더는 처리량 레버가 아니다** — N=2 는 +7.0 % 뿐이고 N=3 은 이 머신(RAM 31.9 GB)에서
   **결정론적 OOM**(인스턴스당 anon-RSS 13.7 GB; VRAM 은 12.9/24 GB 로 병목 아님) [실측 동 §6.2].
   큐는 **단일 인스턴스 + PT 가속**으로 짠다.

### 7.3 파일럿 3씬 게이트 — **`[v1.1 T5]` 원칙 P-1 로 재검증**

**재검증 절차**: 각 후보 씬의 h0.3 하단 2/3 을 **실제로 채우는 표면**이 `mdl="ground"` 계열인지를
레이캐스트 `gnd%`(`const_color_texture_map.md` §0-3·§2) + 본 개정의 픽셀 재측정으로 확인했다.
sceneC2 를 효과 0 으로 만든 **식생 지배**가 재현되는 씬은 파일럿에서 뺀다.

| 후보 | h0.3 지배 표면 | 클래스 | MDL 도달? | 식생 점유 | **판정** |
|---|---|---|---|---|---|
| **scene19** | `PlazaLight` 포장 + `Parapet`(gnd% **10.0**, 상수색 concrete) | paving·concrete | **✔ 전부 ground** | **0.0 %** | **유지** |
| **scene07** | 석재 판석 + 흙(경사). 상수색 총 10.1 %(`Ridge_near` 4.3 원경 능선 · `Wood` 3.7 · `Canopy` 2.8) ⇒ **나머지 ~90 %가 텍스처 지면** | stone·soil | **✔** | **0.6 %** | **유지** |
| **scene14** | `Parapet` gnd% **11.1** + `Bldg` **9.6** = concrete 상수색 20.7 % | concrete | **✔** | 0.0 % | **조건부 유지 — 아래 ★** |
| (대안) scene21 | 기념비 석재·파라펫, `flat_gnd` **40.4**(전 씬 최악) | stone·concrete | ✔ | 0.0 % | **예비 1순위** |
| (반례) sceneC2 | 낙엽 마운드·낙엽 산포·잔디 | **veg(omni)** | **✗ 4/22** | — | 파일럿 부적격(상시 대조군으로만) |

[실측 2026-07-29 — `gnd%` 는 `const_color_texture_map.md` §2 표 / 식생 점유는 본 개정이
`look_check/<scene>/r2_on/pt_noon_preset_h0.3_d*.png` 하단 2/3 에서 녹채널 지배(G>1.06R ∧ G>1.06B)
∧ 채도>0.18 마스크로 재측정, 3컷 중앙값 · numpy+PIL · GPU 0]

> **판정 결론: 3씬 선정을 유지한다(변경 없음).** 세 씬 모두 h0.3 프레임을 `ground` 클래스가 채우며
> 식생 점유는 0.0~0.6 % 다 — sceneC2 의 실패 기전(식생 지배)이 **재현되지 않는다.**
> P-1 원칙으로 재검증한 결과 **v1 의 선정 근거가 사후적으로 강화**됐다.

**★ scene14 의 조건부 — 미해결 선결 1건**

레드팀 §5 가 파일럿 적격성에 이의를 제기했다: scene14 측면 파라펫에 **V자 톱니 코드-렌더 모순**이
미해결이다 — v7_pt `lower_lookup` 렌더에 **V자 지그재그가 실재**(감사 레드팀 육안 확정)하는데,
코드 docstring 은 v5.1 에서 "사선 헌치+참 수평"으로 재작·v6 에서 봉합 완료라고 주장하고,
C4 이력은 "14·18 폐기 완료, 19만 잔존" 이라고 적는다 — **3자 불일치**
[실측 `redteam_w1_assets.md` §5 · `C3_scene_props_11-16.md`:176 `_rake_segments` 계단식 캡].

판정 지표(`flat_gnd < 20`)가 **미해명 기하 이상 위에서** 측정된다.

| 분기 | 조건 | 조치 |
|---|---|---|
| **A** | M6(`NEGOBS_SMOKE` 실행 허가)가 T1 파일럿 **전에** 결재됨 | SMOKE 1씬 검산으로 V자 원인 확정 → **scene14 유지** |
| **B** | M6 미결 또는 V자가 코드 버그로 확인 | **scene14 → scene21 로 교체.** 근거: `flat_gnd` 40.4(더 나쁜 케이스) · **동일한 `plaster` 분기를 검증**(§5.2 T-4 가 14·21 을 한 항목으로 묶고 있다) · `plaza_light` 무틴트 9씬에 포함 · V자 이슈 없음 |

**분기 B 가 기본값이다** — M6 는 감독 결재 항목이고 본 스펙이 통제할 수 없다.
착수 시점에 M6 가 미결이면 **묻지 말고 scene21 로 간다.**

**게이트 조건 — `[v1.1 T1]` `flat%` 열 삭제, `flat_gnd` 단독 판정**

| 씬 | 선정 이유 | 통과 조건(전부 h0.3 3컷 중앙값) |
|---|---|---|
| **scene19** | 최악 순백(w80 **97.7**, w87 72.3)·최저 채도(0.028)·slope 최급(−2.66). 톤+디테일+헥스가 전부 걸린다 | w80 **< 40** · sat **> 0.10** · slope **> −2.45** · **`flat_gnd` 10.0 에서 악화 없음** |
| **scene07** | 자연 석재·흙 + **경사면**(MDL 트라이플래너의 존재 이유). 채도 0.254 | slope **−2.38 → −2.25 이상** · sat **< 0.24** · 경사면 스트레치 육안 없음 · `flat_gnd` 1.7 악화 없음 |
| **scene14** (또는 **scene21**) | `flat_gnd` **31.3**(21 은 **40.4**) 최악급 · 밝은 파라펫 `plaster` 분기 검증 | **`flat_gnd` < 20**(21 이면 **< 26**) · slope 목표대 이동 · 색편향(채널배율 클램프) 0건 |
| (상시) **sceneC2** | **과잉 HF 대조군**(slope −1.65, sat 0.302). 디테일을 넣으면 **안 되는** 씬 | slope **−1.75 이하로 더 가팔라지지 않을 것** · sat 악화 없음. **재질 효과가 작게 나오는 것은 실패가 아니다**(원칙 P-3) |

**3씬 전부 통과 + C2 무해 확인 + R-4·R-5·R-6 통과 + regression FAIL 0** → 전 33씬 라운드.

### 7.4 산출물

- `look_check/<scene>/t1_mtl_{off,on}/` (3씬 × 2조건 × 4컷)
- `Docs/reports/t1_material_gate_v1.md` — 판정표 + 근접 크롭 시트 + s/컷 예산 + R-4/R-5/R-6 로그
- `scripts/geom_invariance_check.py` · `scripts/norm_spec.py` · `scripts/near_ground_stats.py` ·
  `assets/gen_detail_normal.py` (**신규 4개** — v1 의 2개 + §3.4 측정기 2종)

### 7.5 `[v1.1 T3]` 렌더 예산 — MDL 비용 실측 반영

T0 실측 [`t0_spike_report_v1.md` §5.1] · 씬당 부팅+조립 **9 s**(프림 1,340개 기준):

| 조건 | PT s/컷 | 배수 |
|---|---:|---|
| PT legacy 무처리(A) | 13.18 ~ 13.71 | 1.00 |
| PT legacy + **MDL 바인딩**(B) | **15.33 ~ 20.97** | **+13 ~ 55 %** |
| PT legacy + `LOOK_V1` 전량(C) | 21.58 ~ 31.33 | 1.6 ~ 2.3배 |
| **PT 가속**(`NEGOBS_PT_FAST=1`, 무처리) | **0.90 ~ 0.99** (평균 0.95) | 1/14.2 |

주: "+13~55 %" 는 A 평균 13.5 s 기준. T0 본문은 하한을 13.18 로 잡아 "+16~55 %" 로 표기한다 — 같은 실측이다.

**파일럿 예산(§7.3, 3씬 × 2조건 × 4컷 = 24컷)**

| 항목 | 산식 | 값 |
|---|---|---|
| 렌더 | 24컷 × 0.95 s × (1 + MDL 오버헤드 0.13~0.55) | **26 ~ 35 s** `[추정 — 상대 오버헤드가 PT 가속에서도 유지된다는 가정. 첫 파일럿에서 실측해 갱신할 것]` |
| 부팅 | 6회 실행 × 9 s | 54 s |
| **합계** | | **약 1.5분** (v1 의 "1시간" 은 PT legacy 전제 — **대폭 하향**) |
| 전 33씬 라운드 | 33씬 × 4컷 × 1.2 s + 33 × 9 s | **약 7분** (v1 "30분" 대비) |

- **디테일 노멀·헥스의 추가 비용은 위에 포함돼 있지 않다.** §4.2 가 헥스를 **약 1.45배**로 추정했으므로
  33씬 라운드 상한은 **약 10분**으로 본다. **파일럿에서 s/컷 실측 후 확정** — sceneD3 가
  22s → 404s(18배)로 터진 전례가 있다.
- **예산이 작다는 것이 결론이다**: 렌더 비용은 더 이상 T1 의 제약이 아니다.
  제약은 **판정 품질**(근접 크롭·R-4~R-6·게이트 지표 정합)이다.

---

## 8. 실행 순서 (다음 웨이브) — **`[v1.1]` 재작성**

| 순 | 작업 | 산출 | 비용 | GPU |
|---|---|---|---|---|
| **0a** | **`scripts/norm_spec.py` 재작성**(§3.4a) — §1.2 앵커 4맵 재현 검증 | 스크립트 | 2시간 | 0 |
| **0b** | **`scripts/near_ground_stats.py` 재작성**(§3.4b) | 스크립트 | 2시간 | 0 |
| **0c** | 라운드 스크립트의 게이트를 `GATE` → **`GATE_GND`(`flat_gnd`)** 로 전환 `[T1]` | `imgstats` 호출부 | 30분 | 0 |
| **0d** | **`_ground_skin` P-A 스위치 4줄 + `_SKIN_DENY += ("gkit",)`** `[G1]` — ground_kit 의 **차단 항목** | `scene_common.py` | 30분 | 0 |
| 1 | `scripts/geom_invariance_check.py` 작성(**R-4 + R-5 + R-6**) + 33씬 현행 기준선 해시 확보 | 스크립트 + 기준선 JSON | 반나절 | 0 |
| **2** | `LOOK_MTL`/`LOOK_GEO` 2단 플래그 분리 — **§1.7.1 전수 분류표 기준**(GEO 12곳 + 씬 파일 2곳 + META 2곳). **통과 조건 = R-5 잔존 참조 0 + R-6 3자 해시 일치** | `scene_common.py` + `sceneC2` + `sceneN4` + 킷 주석 | 3시간 | 0 |
| **2b** | **`veg` 클래스 정리** `[G4]` — `tex_alts` 에서 `leaf_ground` 제거(A2) | `scene_common.py:279` | 10분 | 0 |
| 3 | `assets/gen_detail_normal.py` + 3종 생성(**β 파워 규약 2.0**) · §3.1 자가검증(불통과 시 exit 1) | PNG 3 + 스크립트 | 2시간 | 0 |
| 4 | **MDL v1.9.0** — 디테일 노멀 입력(§1.6a) **+ 유닛 셀 지터 입력**(§1.8③ `[G3]`) + `scene_common` 배선(§1.6b) | MDL v1.9.0 | 4시간 | 0 |
| **5** | **파일럿 3씬 A/B**(§7.3) — **scene14 는 M6 결재 확인 후, 미결이면 scene21** | 렌더 + 판정 보고 | **약 1.5분 렌더** | **필요** |
| 6 | 헥스 타일링(§4.2) → 파일럿 재판정 | MDL v1.10.0 | 4시간 + 렌더 | 필요 |
| **7** | **톤 T-1 ×0.72 + `scale_m` 1.80 동시 집행** `[G2]` — **9씬 동시**(01·05·14·16·18·19·20·21·N3), 한 커밋·한 라운드. T-2~T-4 병행 | 씬 파라미터 | 1시간 + 렌더 | 필요 |
| **7b** | **`grass` → `Grass001`(1.4 m) 교체** `[G4 A1]` + 전 씬 `scale=dict(grass=1.4)` | 조달 + 28씬 상수 | 2시간 + 렌더 | 필요 |
| 8 | 웨더링 `foot_z` 통로(§4.1) + D3 지름길 검증 | MDL + `add_box` | 3시간 + 렌더 | 필요 |
| 9 | 전 33씬 라운드 + `imgstats` 전수 재측정(**`flat_gnd` 기준**) | `t1_material_gate_v1.md` | 약 10분 | 필요 |
| **10** | **`scripts/skyline.py` 재작성**(§3.4c) — 중경 웨이브 선결. T1 직접 의존 없음 | 스크립트 | 2시간 | 0 |

**순서 근거 3건 `[v1.1]`**
1. **0a 는 3 의 하드 선행조건**이다 — `gen_detail_normal.py` 의 자가검증이 참조할 정의가 그 전엔 없다.
2. **7(`scale_m`)은 5(파일럿 A/B) 뒤여야 한다** — `scale_m` 2.25~2.40배 변경은 9씬의 텍스처 주기를 바꿔
   §7.1 판정 문턱과 §2.2 기준값을 무효화한다. 파일럿 판정을 먼저 끝내고 집행한다.
3. **0d 를 맨 앞에 둔다** — `ground_kit` W2-0 의 **차단 항목**이고, `SKIN_EXCLUDE` 가 비면 회귀 0 이라
   T1 작업과 충돌하지 않는다. 이것 하나 때문에 ground_kit 웨이브 전체가 대기하는 상태를 먼저 푼다.

**착수 금지**: `metal_galv` 조달(§2.1 우선 2)은 CC0 후보 실측이 아직 없다 — 별도 조달 웨이브.
`brushed` 디테일 노멀도 보유분 전멸이라 **절차 생성 외 경로 없음**(§3.2).
수면 잔물결 노멀은 재질층 밖(셰이딩 담당)으로 이관.

### 8.1 `[v1.1]` W2 착수에 남은 전제 — **본 스펙이 통제하지 못하는 3건**

| # | 전제 | 소유자 | 미충족 시 |
|---|---|---|---|
| **P1** | **M6 — `NEGOBS_SMOKE` 실행 허가** (scene14 V자 원인 확정) | 감독 결재 | **파일럿을 scene21 로 교체**(§7.3 분기 B, 기본값) |
| **P2** | `ground_kit` 이 **`unit_cell_m` + 격자 원점 오프셋**을 원장으로 제공 | ground_kit | §1.8③ 유닛 지터는 **기본값 0(무영향)으로 배선만** 하고 값 주입은 대기. MDL v1.9.0 자체는 진행 가능 |
| **P3** | `ground_kit` 파일럿(N5·15·13)을 **T1 병합 전** 실행하거나, 파일럿 렌더 재질 상태를 `r2_on` 과 동일로 각인 | 감독 순서 결정 | 교락 발생 — N5 합격선 `\|∇\|p99 0.079→≥0.30` 이 **디테일 노멀만으로도 부분 충족**될 수 있다 [레드팀 §3] |

**추가로 회신할 계약 1건(역방향)**: §1.8③ 이 `unit_cell_origin`(격자 원점 오프셋)을 요구한다 —
ground_kit 원장에 없으면 지터 셀 경계와 음각 줄눈이 어긋나 **이중 격자**가 보인다.
`ground_kit` v1.1 이 `GROUND_DIMENSIONS` 에 이 항목을 추가해야 한다.

**통합 게이트 권고 수용** [레드팀 §3]: ground_kit 확산 1차(01·04·12) 중 **scene01 을
"기하 + 재질 통합 게이트"** 로 지정한다 — 01 은 `plaza_light` 톤 T-1·`scale_m`·헥스가 모두 걸리는
유일한 씬이라 줄눈 음각 × 디테일 노멀 × 헥스의 간섭(모아레·s/컷 합산)이 여기서 처음 드러난다.
**나머지 26씬은 01 재판정 통과 후 진행.**

---

## 부록 A — 측정 재현 절차 (GPU 0)

```bash
cd /home/vislab/Desktop/work_sy/Practice_NegObs

# 씬별 h0.3 현재값 (§2.2 표) — 게이트는 GATE 가 아니라 GATE_GND(flat_gnd) 로 본다 [v1.1 T1]
python3 scripts/imgstats.py @render 'look_check/scene19/r2_on/pt_noon_preset_h0.3_d*.png'

# 노멀맵 스펙트럼 (§1.2 / §3.1 / §3.3) — **정의는 §3.4(a) 가 유일 원천**
#   v1.1 재작성 후:  python3 scripts/norm_spec.py 'assets/**/*_nor*.jpg' --gate
#   재작성 전 앵커(반드시 재현):  concrete_wall −0.71/4.1/18.9/0.056 · asphalt −0.66/3.2/13.3/0.294
#                                stone_flag −2.46/58.4/2.5/0.192 · paving_interlock −1.98/52.3/4.8/0.449

# r2_on 컷 수 (§0 R3 정정 근거)
ls look_check/*/r2_on/*.png | wc -l          # → 452

# LOOK_V1 전수 분류 (§1.7.1) — 24건. 치환 후에는 정의 1줄(:172)만 남아야 한다
grep -n "LOOK_V1" scene_common.py
grep -rn "LOOK_V1" --include=*.py . | grep -v scene_common.py     # 씬·킷 파일 4건

# plaza_light scale_m 현행 (§1.8② — 0.75/0.8 혼재 확인)
grep -rn "plaza_light=" scenes/main scenes/batch1

# T0 실측 원자료 (렌더 재실행 불요)
#   look_check/_t0_spike/{stats_*.json,regr_*.json,rtx_settings.json}
#   기준선은 c2_A_base/ — leaf3d/ 를 기준선으로 쓰지 말 것 [v1.1 T2]

# CC0 후보 조회
curl -s "https://ambientcg.com/api/v2/full_json?id=Plaster001&include=downloadData"
curl -s "https://ambientcg.com/api/v2/full_json?id=Grass001&include=dimensionsData,tagData"
curl -s "https://api.polyhaven.com/files/brushed_concrete"
```

## 부록 B — 이 문서가 지킨 확정 규약

계절/이벤트 요소 도입 0(눈은 기존 sceneC1 의 알베도 교정만) · 대기원근 도입 0 · 전주 언급 0 ·
자연 씬 도시 인프라 0 · 순백 대면적은 **하향 처방 대상** · 볼라드/점자블록/경고 팻말 변경 0 ·
생울타리 각진 상자 유지 · 사람·차량 배치 0 · 판정 시점은 전부 h0.3.

**`[v1.1]` 추가로 지킨 것**
- **계절 규약** — §1.8④ 의 `leaf_ground` 승격 제거는 24씬 수관에 **가을 낙엽 픽셀**이 칠해지던
  규약 위반을 끄는 조치다(계절 요소를 **넣는** 것이 아니라 **빼는** 것). `sceneC2` 의 명시적
  낙엽 사용은 그 씬 고유 설정이므로 유지.
- **GT 낙차 맵 착수 금지 유지** — §1.8③ 유닛 지터는 평면 좌표 해시라 z 를 읽지 않고,
  §4.1 `foot_z` 는 프림 발치 상대라 낙차 깊이와 무관하다. **둘 다 GT 상관 0** 을 논증했다.
- **씬 기하 무수정** — 본 개정이 추가한 코드 변경은 전부 재질층(`LOOK_MTL`) 또는 게이트 배선이며,
  `sceneC2:552`·`sceneN4:723` 의 씬 파일 수정은 **`sc.LOOK_V1` → `sc.LOOK_GEO` 토큰 치환뿐**으로
  기하 산출이 동일함을 R-6 이 검사한다.

## 부록 C — `[v1.1]` 본 개정이 수용하지 **않은** 것 (정직 고지)

| 항목 | 출처 | 미수용 사유 |
|---|---|---|
| ground_kit 이관 **⑤ N5 포장 알베도 0.672 → 0.38~0.45** | 레드팀 §3 표 5행 "소유자 미정" | 임무서 이관 4건에 없다. **T-1(`plaza_light` 무틴트 9씬)의 대상이 아니고**(N5 는 `pave_tint` 로 이미 틴트 적용), ground_kit 자체 요소 알베도 클램프(≤0.30)와도 다른 값이다. **소유자 지정이 먼저** — §8.1 P 목록에 넣지 않고 감독 결재로 남긴다 |
| `VEG_DEBRIS` 수치 정정(B 감사 A3) | `B_groundcover_debris.md` §12 A3 | 임무서 이관 4건에 없다(④는 `tex_alts`+`grass` 만). 산포 개수 정확도 항목이라 재질층이 아니다 |
| ground_kit **C-1 트렌치 이설·GT-E2 16행** | 레드팀 §9-1·§9-2 | ground_kit 스펙 소관. 본 문서 범위 밖 |
| `macro%` 문턱의 **CC0 후보 재판정** | §3.2 | 다운로드본 소멸로 재측정 불가. **§3.4(a) 재작성 후 조달 시점에** 판정한다 |
| `metal_galv` · `brushed` 디테일 조달 | §2.1·§3.2 | CC0 후보 실측 없음 — 별도 조달 웨이브(착수 금지 유지) |
