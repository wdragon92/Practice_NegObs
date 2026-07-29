# T1 재질층(표면 미세구조) 실행 사양 v1

작성 2026-07-29 · NegObs 사실화 W1 · 대상 코드 `scene_common.py` @ `c0cef87` · MDL `assets/NegObsGround.mdl` v1.8.0
전제 문서: `Docs/surveys/realism_gap_2026-07-28/ZZ_synthesis.md` §1·§6·§10 / `Docs/reports/realism_phase1.md` /
`Docs/reports/realism_phase2.md` / `Docs/reports/realism_v1_final.md` / `Docs/reports/const_color_texture_map.md` /
`Docs/reports/redteam_verification_v1.md` / `Docs/audit_v4/fixlog_X1.md`

모든 수치에 근거 태그. GPU·렌더·Isaac 미실행 — 기존 PNG 판독 + numpy/PIL + 정적 분석 + 공개 API 조회만.

---

## 0. 착수 전 정정 — 임무서의 전제 2건이 이미 낡았다

| 임무서 전제 | 실태 | 근거 |
|---|---|---|
| "해법(NegObsGround.mdl)은 저장소 안에 있는데 **33씬 중 0곳 사용**" | **이식 완료**. `NEGOBS_LOOK_V1=1` 이면 지면 10클래스가 전부 이 MDL 을 경유한다 | [실측] `scene_common.py:978-1011`(분기) · `:1099-1204`(`_make_ground_pbr`) · r2_on 라운드 1,529컷이 이 경로로 렌더됨 |
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

노멀맵 접선성분(R,G) 스펙트럼 실측 — 네이티브 1024² 중앙 크롭, 창함수 FFT, 방사평균:

| 맵 | 해상도 | slope_n | **macro%**(f<f_nyq/32) | hf%(f≥f_nyq/4) | **접선 RMS** |
|---|---|---:|---:|---:|---:|
| **`concrete_wall_nor_dx` (현행)** | 4096² | −0.70 | **39.8** | 24.2 | **0.056** |
| `concrete_floor_nor_dx` | 4096² | −1.10 | 18.7 | 9.3 | 0.304 |
| `plaster_nor_dx` | 4096² | −0.90 | 20.4 | 19.7 | 0.159 |
| `asphalt_nor_dx` | 4096² | −0.67 | 12.9 | 18.7 | 0.294 |
| `gravel_nor_dx` | 4096² | −1.39 | 28.0 | 7.9 | 0.546 |
| `stone_flag_nor_dx` | 4096² | −2.46 | 90.2 | 0.7 | 0.192 |
| `paving_interlock_nor` | 2048² | −1.98 | 83.0 | 1.9 | 0.449 |

[실측 — 재현: `scratchpad/norm_spec.py` 방식, numpy+PIL, GPU 0]

두 가지가 동시에 틀렸다:
1. **너무 약하다** — 접선 RMS 0.056 은 라이브러리 내 최저치이며 `asphalt`(0.294)의 **1/5.3**.
   여기에 `detail_bump_factor 0.45` 가 곱해지면 실효 섭동은 0.025 = 기울기 약 1.4°. **보일 수 없다.**
2. **매크로가 40%** — 8 cm 타일에 매크로 얼룩이 40% 실려 있으면 그 얼룩이 **미터당 12.5회 반복되는
   격자**가 된다. 디테일 노멀이 오히려 CG 티를 추가한다.

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
_DETAIL_MAP = {
    "mineral": ("detail_grain_mineral_nor.jpg", 0.85, 12.5),   # 포장·콘크리트·석재·연석·노징
    "granular": ("detail_grain_coarse_nor.jpg", 0.70,  8.0),   # 흙·자갈·아스팔트
    "metal":    ("detail_grain_brushed_nor.jpg", 0.55, 25.0),  # 금속(선형 스크래치)
    "wood":     (None, 0.0, 0.0),                              # 목재는 결이 방향성 — 디테일 금지
}
_DETAIL_FAMILY = {"paving": "mineral", "concrete": "mineral", "brick": "mineral",
                  "stone": "mineral", "curb": "mineral", "nosing": "mineral",
                  "soil": "granular", "gravel": "granular", "asphalt": "granular",
                  "snow": "granular", "metal": "metal"}
```

`_make_ground_pbr` 끝부분(웨더링 블록 뒤)에 6줄, OmniPBR 블록(`:1084`)의 `_DETAIL_NOR` 를 위 표로 교체.
**`veg`·`water`·`glass`·`paint`·`sign`·`misc` 는 유지(디테일 금지)** — 도색·사인은 균일해야 단서로 기능한다(v5.1 §4).

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

### 1.7 게이트 배치와 **대조군 규칙** (치명 C3 유형 예방)

#### 문제 — 현행 `LOOK_V1` 단일 플래그로는 재질 A/B 가 불가능하다

`NEGOBS_LOOK_V1` 은 재질뿐 아니라 **기하도 8곳에서 바꾼다** [실측 — `grep -c LOOK_V1 scene_common.py` = 24회 중]:

| 위치 | 기하 변화 |
|---|---|
| `:735` `_skin_wanted` | 지면 슬래브 위 **변위 스킨 메시 신설** |
| `:1337` `rail_h` | 0.9 → 1.1 m |
| `:1339` `spacing` | 1.2 → 2.0 m (포스트 개수 변화) |
| `:1367` | 난간 세로 간살 신설 |
| `:1409` | 계단 손잡이 신설 |
| `:2091` `window["inset"]` | 창 리세스 |
| `:2179` `par_h` | 파라펫 0.5 → 1.20 m |
| `:1911`·`:2022`·`:2275` | 나무·관목 실물 USD·산포물 |

⇒ **"LOOK_V1=0 vs 1" 을 재질층 A/B 로 쓰면 기하 변화가 섞여 재질 효과를 분리할 수 없다.**
이것이 재발 2회를 기록한 치명 C3(대조군 오염)의 구조적 원인이다
[실측 — `redteam_verification_v1.md` R3: "수정 8분 뒤에 재발"].

#### 처방 — 2단 플래그 + 대조군 4규칙

```python
LOOK_V1  = os.environ.get("NEGOBS_LOOK_V1", "") == "1"          # 상위(종전 호환)
LOOK_MTL = os.environ.get("NEGOBS_LOOK_MTL", "1" if LOOK_V1 else "0") == "1"
LOOK_GEO = os.environ.get("NEGOBS_LOOK_GEO", "1" if LOOK_V1 else "0") == "1"
```
- 기존 `LOOK_V1=1` 호출은 둘 다 ON → **종전 동작 완전 보존**.
- 기하 8곳은 전부 `LOOK_GEO` 로 치환. `make_pbr` / `_make_ground_pbr` / `_promote_*` / 채도교정은 `LOOK_MTL`.
- **T1 재질층 신규 항목(디테일 노멀·헥스 타일링·톤·채도)은 전부 `LOOK_MTL` 안.**

**대조군 규칙(위반 시 레드팀 킬)**

| # | 규칙 | 검사 방법 |
|---|---|---|
| **R-1** | 재질층은 **프림 집합·타입·xform·points·extent 를 바꾸지 않는다.** 셰이더 입력과 `UsdShade.Material` 정의만 만든다 | 자동 (아래 R-4) |
| **R-2** | 재질 A/B 의 대조군은 `LOOK_MTL=0, LOOK_GEO=<실험군과 동일>` 이다. **`LOOK_V1=0` 전체 OFF 를 대조군으로 쓰지 않는다** | 라운드 스크립트에 환경변수 명시 + 로그에 각인 |
| **R-3** | 함수 **기본 인자값**을 플래그로 분기할 때는 `x = A if LOOK_GEO else B` 형태로 **게이트 안**에서만. 기본값 자체를 바꾸지 않는다 | 코드 리뷰 + R-4 |
| **R-4** | **자동 기하 불변 검사**: `scripts/geom_invariance_check.py` — `pxr/omni/carb/isaacsim` 을 MagicMock 으로 대체하고 `add_box/add_cylinder/add_sphere/_oriented_box/Mesh.Define` 을 기록 스텁으로 갈아끼운 뒤 각 씬 `main()` 을 `LOOK_MTL=0/1` 두 번 실행 → **프림 인벤토리 해시**(경로·타입·중심·치수·회전, 소수 6자리 반올림) 비교. 불일치 1건이라도 exit 1 | GPU 0 · 33씬 약 3분. 하네스는 `const_color_texture_map.md` §0-2 가 이미 33/33 성공으로 검증한 방식 |

R-4 는 **웨더링 primvar 예외**를 허용한다(§4.1의 `foot_z`): primvar 저작은 위 해시 항목에 포함되지 않으며,
별도로 "primvar 이름·interpolation 만 diff" 하는 보조 리포트를 낸다.

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
| **veg** | 107 | 30 | 44.5 | OmniPBR/MDL(상수색) + `grass` | 없음(의도) | patch 1 | 유지. 잎은 실물 USD 담당(P3) | 4 |
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
`w80` = 하단 2/3 에서 **min(R,G,B) > 0.80** 인 픽셀 비율(= 순백 대면적 지표, 규약 "순백(>0.8) 대면적 금지").
[실측 2026-07-29 · 33씬 × 3컷 = 99컷 · numpy+PIL · GPU 0]

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

### 3.1 합격 기준 (§1.2 실측에서 유도)

| 지표 | 기준 | 이유 |
|---|---|---|
| `macro%` (f < f_nyq/32) | **< 15** | 8 cm 타일 자체 크기의 에너지 = 화면에 격자로 드러나는 성분 |
| `slope_n` | **> −0.9** | 0 에 가까울수록 백색잡음 = 진짜 미세 그레인 |
| 접선 RMS | **0.12 ~ 0.35** | 0.056(현행)은 안 보이고, 0.5 이상은 지면이 자갈처럼 튄다 |
| 라이선스 | **CC0 only** | Quixel(NoAI)·Isaac Environments(수정금지) 금지 [ZZ §10.6] |

### 3.2 실측 검증 완료 후보 (실제 다운로드 후 측정)

전부 **ambientCG · CC0 1.0** (사이트 라이선스: 전 콘텐츠 CC0, AI 학습 허용 [ZZ §10.6]).
zip 내용물 실측 — `*_NormalDX.jpg` / `NormalGL` / `Color` / `Roughness` / `Displacement` / `.usdc` 포함 확인.

| 순위 | 에셋 | URL / 파일 | 실측 macro% | slope_n | RMS | 판정 |
|---|---|---|---:|---:|---:|---|
| **1** | **Plaster001** | `https://ambientcg.com/view?id=Plaster001` → `https://ambientcg.com/get?file=Plaster001_1K-JPG.zip` (7.41 MB) → `Plaster001_1K-JPG_NormalDX.jpg` | **14.4** | **−0.23** | **0.167** | **채택 — mineral 계열 기본** |
| 2 | Plaster004 | `https://ambientcg.com/get?file=Plaster004_1K-JPG.zip` → `Plaster004_1K-JPG_NormalDX.jpg` | 23.8 | −0.38 | 0.234 | 예비(강한 그레인 필요 시) |
| 3 | SurfaceImperfections017 | `https://ambientcg.com/view?id=SurfaceImperfections017` → `..._1K-JPG_NormalDX.jpg` (40×40 cm) | **4.9** | **+0.16** | **0.011** | **단독 불가**(너무 약함). bump ×8~15 로 2차 레이어에만 |
| ✗ | Concrete034 | `..._1K-JPG_NormalDX.jpg` | **72.6** | −1.43 | 0.115 | **탈락**(매크로 벽) — 단 Color 는 선형 (0.482,0.482,0.482) **완전 중성**이라 §5 밝은 콘크리트 승격용으로는 1순위 |

[실측 2026-07-29 — 1K zip 다운로드 후 네이티브 크롭 FFT. 다운로드본은 scratchpad 에만 두었고 저장소에 넣지 않았다]

보조(검증 완료, 조달 0): **`asphalt_nor_dx`(저장소 보유)** macro 12.9 / slope −0.67 / RMS 0.294 → **granular 계열 기본으로 즉시 사용 가능**.

Poly Haven 경로(대안): `https://api.polyhaven.com/files/brushed_concrete` 가 `nor_dx` 를 1k/2k/4k/8k · jpg/png/exr 로
제공함을 API 로 확인 [실측 2026-07-29]. CC0 + AI 학습 명시 허용. 다만 물리 타일이 2.5 m 라 매크로가 실릴 위험이 있어
**도입 전 §3.1 기준 측정 필수**.

### 3.3 권고 — 1순위는 **절차 생성**이다 (라이선스 0 · 스펙트럼 조정 가능)

우리의 진짜 결손은 "그레인이 없다"가 아니라 **`slope` 가 −2.19 로 실사(−1.97)보다 가파르다**는 것이다
[실측 §2.2 · 실사 n=54 −2.033±0.184]. 사진 유래 디테일맵은 스펙트럼을 **고를 수 없지만**, 절차 생성은 고를 수 있다.

대역제한 백색잡음 → 높이장 → 노멀 (numpy+PIL, `assets/signs/gen_signs.py` 와 동일 방식, 약 25줄):

| 목표 지수 β | 실측 slope_n | macro% | hf% | RMS |
|---|---:|---:|---:|---:|
| 0.0 | +1.28 | 0.3 | 93.5 | 0.652 |
| **0.5** | **+1.07** | **0.6** | 89.3 | 0.641 |
| 1.0 | +0.76 | 1.3 | 82.5 | 0.617 |

[실측 — 1024² 생성 후 동일 파이프라인 측정]

- **완전 타일러블**(FFT 합성이라 경계 연속) · **등방** · **매크로 0.3~1.3%** · RMS 를 진폭으로 직접 지정.
- 나이퀴스트 근방(R>0.45) 컷으로 **앨리어싱 방지** — 현행 변위 스킨이 M4 로 겪었던 문제의 재발 차단.
- 산출: `assets/detail_grain_{mineral,granular,brushed}_nor.png` + 생성 스크립트 `assets/gen_detail_normal.py`(재현 가능·시드 고정).
- **결정 필요**: 절차 단독 / CC0 단독 / 혼합(절차 β=0.5 × 0.7 + Plaster001 × 0.3). **파일럿 3씬에서 3안 A/B** 권고.

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

### 5.3 채도 — 전역 금지, 3구간 처방

현행 자기교정(`_effective_sat`, knee 0.18, `scene_common.py:485-499`)은 **하향 전용**이다. 유지하되:

| 구간 | 씬 | 처방 |
|---|---|---|
| **과채도** (sat > 0.25) | 04(0.437) · D4(0.450) · 10(0.394) · 03(0.309) · C2(0.302) · D3(0.280) · 15(0.270) · D2(0.260) · 07(0.254) | 현행 knee 유지 + `veg`(0.76)·`soil`(0.74)에 이미 계수 있음. **`sign`·`paint` 계열도 점검**(D4 의 0.450 은 사인 다수 — §2.1 sign 4종) |
| **목표대** (0.15~0.22) | 09 · 17 · 12 · D1 · 06 · 11 · 21 · C4 | 손대지 않는다 |
| **저채도**(sat < 0.15, **15씬**) | 19(0.028) · 05 · 18 · 16 · 02 · N5 · 01 · N2 · N3 · 20 · 14 · N1 · C1 · N4 · 13 | **채도로 접근 금지.** §5.2 톤 하향 → 자동 회복. 톤 대상이 아닌 씬(02·16·13·N2·N3)은 **디테일 노멀·헥스**로 국소대비를 먼저 회복시키고 재측정 |

**금지**: 전역 채도 상수 곱, `saturation_a > 1.0`(과포화 주입). 채도는 결과 지표이지 조작 대상이 아니다.

---

## 6. T0 스파이크 의존 항목 — 대부분 이미 닫혔다

| 항목 | ZZ §6 T0 요구 | **현재 상태** | 근거 | T1 의존성 |
|---|---|---|---|---|
| `round_edges_radius` 육안 검증 | 최고 ROI·미검증 | **검증 완료 · 채택** (RT/PT 양쪽 소프트 롤오프 확인, 근접 크롭 판정 필수) | [실측] `realism_phase1.md` §2.1 (E1) | **없음** — 값은 KCS/예규 근거로 확정(§2.1) |
| `subdivisionScheme=catmullClark` | 미검증 | **검증 완료 · 기각**(refinementLevel 기본 0 = 세분 없음. crease 는 존중됨) | [실측] 동 §2.4 (E4) + `scripts/rtx_probe.py` | **없음** |
| MDL 효과 정량 | 1씬 바인딩 후 개선폭 | **부분 완료** — 평면 미미 / **경사면 결정적**. 전 씬 라운드(r2_on) flat_gnd 27/33 개선 | [실측] 동 §2.2 (E2) + `realism_v1_final.md` §1.0 | **없음**(단 §7 재측정으로 갱신) |
| 디테일 노멀 | "즉시 사용" | **OmniPBR 경로만 검증**(E3 통과). **MDL 경로 미구현** | [실측] 동 §2.3 | **있음** — §1.6(a) 구현 후 A/B 필요 |
| 헥스 타일링 | — | **미구현·미검증** | — | **있음** — §4.2 구현 후 A/B 필요 |

### 분기 계획

**성공 분기** (디테일 노멀 MDL 구현 → 파일럿에서 slope 가 −2.19 → −2.10 이내로 이동, 육안 근접 크롭에서 그레인 확인)
→ 3씬 게이트 → 33씬 라운드 → 헥스 타일링 A/B → 톤 하향(6씬 동시) → 재라운드.

**실패 분기 A — 디테일 노멀이 안 보인다**(Δslope < 0.05 = §7 판정 문턱 미만)
→ ① `detail_bump_factor` 를 0.85 → 1.5 로 올려 재시도(1회) ② 그래도 안 되면 **원인은 텍셀 밀도가 아니라
   조명·톤매핑 상단 클리핑**이라는 가설로 이동 — **톤 하향(§5.2)을 먼저 집행하고 디테일을 재측정**한다.
   (scene19 sat 0.028 이 이 가설을 강하게 지지한다. 클리핑된 표면에서는 어떤 노멀도 대비를 못 만든다.)

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

### 7.2 A/B 프로토콜

1. 대조군 = `NEGOBS_LOOK_MTL=0 NEGOBS_LOOK_GEO=1`, 실험군 = `MTL=1 GEO=1`. **기하는 양쪽 동일**(규칙 R-2).
2. `NEGOBS_PT_FAST=1` (출력 PNG 동일성 검증됨 [실측 `realism_phase1.md` §3.2]).
3. 컷: `pt_noon_preset_h0.3_d{2,5,10}` **필수 3컷** + 씬 미장센 1컷.
4. **근접 크롭 판정 필수** — d2 컷의 하단 중앙 512×512 를 4분할 비교(before/after × d2/d5).
   근거: E1 에서 광각만 보고 "미작동" 오판했다가 근접 크롭에서 뒤집힌 전례 [실측 `realism_phase1.md` §2.1].
5. 매 라운드 `scripts/regression_check.py` 실행(STATUS.md 작업 규율). FAIL 0 · 신규 WARN 사유 기재.
6. `scripts/geom_invariance_check.py` (규칙 R-4) 통과가 **수치 판정보다 선행**한다.

### 7.3 파일럿 3씬 게이트

| 씬 | 선정 이유 | 통과 조건 |
|---|---|---|
| **scene19** | 최악 순백(w80 97.7)·최저 채도(0.028)·slope 최급(−2.66). 톤+디테일+헥스가 전부 걸린다 | w80 **< 40** · sat **> 0.10** · slope **> −2.45** · flat_gnd 악화 없음 |
| **scene07** | 자연 석재·흙 + **경사면**(MDL 트라이플래너의 존재 이유). 채도 0.254 | slope **−2.38 → −2.25 이상** · sat **< 0.24** · 경사면 스트레치 육안 없음 |
| **scene14** | flat_gnd 31.3 최악급 · 밝은 파라펫 `plaster` 분기 검증 | flat_gnd **< 20** · slope 목표대 이동 · 색편향(채널배율 클램프) 0건 |
| (상시) **sceneC2** | **과잉 HF 대조군**(slope −1.65, sat 0.302). 디테일을 넣으면 **안 되는** 씬 | slope **−1.75 이하로 더 가팔라지지 않을 것** · sat 악화 없음 |

**3씬 전부 통과 + C2 무해 확인 + R-4 통과 + regression FAIL 0** → 전 33씬 라운드(약 30분 [실측 `realism_v1_final.md` §1.3]).

### 7.4 산출물

- `look_check/<scene>/t1_mtl_{off,on}/` (3씬 × 2조건 × 4컷)
- `Docs/reports/t1_material_gate_v1.md` — 판정표 + 근접 크롭 시트 + s/컷 예산 + R-4 로그
- `scripts/geom_invariance_check.py`, `assets/gen_detail_normal.py` (신규 2개)

---

## 8. 실행 순서 (다음 웨이브)

| 순 | 작업 | 산출 | 비용 | GPU |
|---|---|---|---|---|
| 1 | `scripts/geom_invariance_check.py` 작성 + 33씬 현행 기준선 해시 확보 | 스크립트 + 기준선 JSON | 반나절 | 0 |
| 2 | `LOOK_MTL`/`LOOK_GEO` 2단 플래그 분리(기하 8곳 치환) | `scene_common.py` | 2시간 | 0 |
| 3 | `assets/gen_detail_normal.py` + 3종 생성 · §3.1 기준 자가검증 | PNG 3 + 스크립트 | 2시간 | 0 |
| 4 | MDL 디테일 노멀 입력(§1.6a) + `scene_common` 배선(§1.6b) | MDL v1.9.0 | 3시간 | 0 |
| 5 | **파일럿 3씬 A/B**(§7.3) | 렌더 + 판정 보고 | 1시간 | **필요** |
| 6 | 헥스 타일링(§4.2) → 파일럿 재판정 | MDL v1.10.0 | 4시간 + 렌더 | 필요 |
| 7 | 톤 하향 T-1~T-4(§5.2) — **T-1 은 9씬 동시**(01·05·14·16·18·19·20·21·N3) | 씬 파라미터 | 1시간 + 렌더 | 필요 |
| 8 | 웨더링 `foot_z` 통로(§4.1) + D3 지름길 검증 | MDL + `add_box` | 3시간 + 렌더 | 필요 |
| 9 | 전 33씬 라운드 + `imgstats` 전수 재측정 | `t1_material_gate_v1.md` | 30분 | 필요 |

**착수 금지**: `metal_galv` 조달(§2.1 우선 2)은 CC0 후보 실측이 아직 없다 — 별도 조달 웨이브.
수면 잔물결 노멀은 재질층 밖(셰이딩 담당)으로 이관.

---

## 부록 A — 측정 재현 절차 (GPU 0)

```bash
cd /home/vislab/Desktop/work_sy/Practice_NegObs
# 씬별 h0.3 현재값 (§2.2 표)
python3 scripts/imgstats.py @render 'look_check/scene19/r2_on/pt_noon_preset_h0.3_d*.png'
# 노멀맵 스펙트럼 (§1.2 / §3.2 표) — 네이티브 1024² 중앙 크롭 FFT, 접선 R·G 채널 합산
#   slope_n = log P vs log f 최소제곱(3 ≤ f < n/4), macro% = f<n/32 파워비, RMS = sqrt(mean(x²+y²))
# CC0 후보 조회
curl -s "https://ambientcg.com/api/v2/full_json?id=Plaster001&include=downloadData"
curl -s "https://api.polyhaven.com/files/brushed_concrete"
```

## 부록 B — 이 문서가 지킨 확정 규약

계절/이벤트 요소 도입 0(눈은 기존 sceneC1 의 알베도 교정만) · 대기원근 도입 0 · 전주 언급 0 ·
자연 씬 도시 인프라 0 · 순백 대면적은 **하향 처방 대상** · 볼라드/점자블록/경고 팻말 변경 0 ·
생울타리 각진 상자 유지 · 사람·차량 배치 0 · 판정 시점은 전부 h0.3.
