# H — 렌더러 능력 근거 조사 (RTX capability verification)

> 작성 2026-07-28 · 대상 런타임 **Isaac Sim 4.5.0 / Kit 106.5.0 / RTX**, conda `env_isaaclab`, RTX 4090
> **GPU 미사용.** 전부 로컬 바이너리·MDL 소스 정독 + 웹 근거. 렌더 실행 0회.
> 태그: `[로컬검증]` 파일을 직접 읽음 · `[웹검증]` 공식 문서/포럼 · `[추정]` 근거 약함

이 문서의 목적은 재확인이 아니라 **판별**이다. 감독이 스파이크 렌더에서 "안 나온다"를 손에 들었을 때
**미지원 / 설정 문제 / 조건 문제** 중 무엇인지 즉시 가릴 수 있게 하는 것.

---

## §0 한 줄 결론표

| # | 항목 | 결론 | 확신도 |
|---|---|---|---|
| 1 | OmniPBR `round_edges_radius` | **RTX에 실제 구현되어 있다 — 106.1에서 추가, RT·PT 양쪽.** MDL 코드 경로도 끊김 없음. 안 보이면 미지원이 아니라 **조건(반경/roughness/조명각/픽셀 크기/`across_materials`)** 문제 | **[로컬검증+웹검증] 매우 높음** |
| 2 | `subdivisionScheme=catmullClark` + crease | **OpenSubdiv 3.4.3로 실제 세분한다.** 단 **기본 refinementLevel=0이라 아무 일도 안 일어난다** — 전형적 설정 문제. crease 지원됨. **adaptiveRefinement은 미구현(로그로 자백함)** | **[로컬검증] 매우 높음** |
| 3 | 정점 변위 메시 노멀 | Hydra는 `normals` 미기재 시 **smooth(정점 평균) 노멀로 폴백한다** — 로그가 명시. 따라서 각져 보이면 노멀 문제가 아니라 **정점 분리(unwelded)** 문제다. 반대로 **날카로워야 할 모서리는 뭉개지므로** 그쪽은 직접 author 필요 | **[로컬검증] 높음** |
| 4 | 알파 컷아웃 | 함정 **4층**: `enable_opacity=false` → `opacity_mode=mono_average` → `opacity_threshold=0.0` → 렌더러 `fractionalCutoutOpacity=**True**(기본)`. **결정적: 블렌딩 상태면 α<1 픽셀이 semantic GT에서 빠진다(공식 문서 확인)** → 하드 컷아웃은 미학이 아니라 **GT 요구사항** | **[로컬+웹검증] 매우 높음** |
| 5 | 톤매핑·노출 | ACES=**6** 확정(양방향 검증). `filmIso`/`exposureTime`/`fNumber`/`whitepoint(float3)`/`cm2Factor`/`colorMode` 전부 존재. `cameraFStop`·`cameraISO`는 없으나 **실제 이름이 `fNumber`**라 노출 3요소 전부 제어 가능. **`histogram/enabled`(자동노출)를 먼저 끄지 않으면 전부 무효**. 톤매핑은 `LdrColor`에 적용, `HdrColor`는 선형 Rec.709 | **[로컬+웹검증] 매우 높음** |
| 6 | NegObsGround.mdl 전역 승격 | **하면 안 된다.** UV 파이프라인 자체가 없고(월드 트라이플래너 강제), opacity·emission·metallic·AO/ORM·detail normal·**round_edges 전부 부재**. 텍스처 페치가 재질당 최대 **72회** | **[로컬검증] 높음** |

**보너스 정정**(§7): MDL displacement는 **RTX 106.1부터 지원된다**(우리 조사 오류 — 공식 릴리스노트로 확인),
카메라 ISP 플러그인은 **로컬에 존재한다**, `opacity_threshold=0.0` 의 의미 정정, `cameraFStop` 결론 상향.

**병렬 웹 조사의 오답 1건 정정**(§1.5): *"OmniPBR에 round edge 파라미터가 없으니 커스텀 MDL을 써야 한다"*
→ **문서에만 없고 실제 MDL 소스에는 있다. 커스텀 MDL 불필요.**

---

## §1 `round_edges_radius` — 최우선 항목

### 1.1 MDL 코드 경로 추적 (끊김 없음)

체인: `OmniPBR` → `OmniPBR_ClearCoat` → `OmniPBRBase` → `material_geometry.normal`

```
OmniPBR.mdl:337-355            round_edges_radius / _roundness / _across_materials 파라미터 선언
OmniPBR.mdl:411-413            → OmniPBR_ClearCoat 로 그대로 전달
OmniPBR_ClearCoat.mdl:498-512  파라미터 재선언
OmniPBR_ClearCoat.mdl:725-727  → OmniPBRBase 로 그대로 전달
OmniPBRBase.mdl:481-488        material_geometry(normal: state::rounded_corner_normal(radius, across_materials, roundness))
```
`[로컬검증]` 경로: `~/miniconda3/envs/env_isaaclab/lib/python3.10/site-packages/omni/mdl/core/Base/`

**중간에 무시되는 지점은 없다.** 3단 전달 모두 리네임 없이 1:1이다.

#### 노멀맵과의 상호작용 — 덮어써지지 않는다
`OmniPBRBase.mdl:367` 의 `geometry_normal` 은 **파라미터**(기본값 `state::normal()`)이며,
`OmniPBR_ClearCoat.mdl:727` 에서 노멀맵으로 섭동된 `diffuse_gloss_normal` 이 주입된다.
그 값이 BSDF 레이어에 `normal:` 인자로 들어간다(`OmniPBRBase.mdl:397/420/429`).

**MDL 언어 사양 §13.3 (Compound types in the fields of the material)** `[웹검증]`
(MDL 1.11.1 Specification, NVIDIA/MDL-SDK `doc/specification/`):
> "The evaluation of the fields in the material_geometry structure though have the potential to change
> the renderer state described in Section 19, for example, **state::normal**, and thus can influence the
> evaluation results of other fields that are evaluated later. The relevant evaluation orders are as
> follows: **The geometry fields are evaluated before all surface fields.** Within the geometry fields,
> **displacement is evaluated first, cutout_opacity second, and normal last.**"

**→ 확정. `geometry.normal`(= rounded corner normal)이 먼저 적용되고, surface 표현식 안의
`state::normal()` 은 이미 rounded 값을 반환한다.** OmniPBR의 노멀맵은 `state::normal()` 을
탄젠트 기저의 Z축으로 쓰므로(`OmniPBRBase.mdl:200-202`) **rounded normal 위에 얹힌다 —
상쇄가 아니라 합성이다.**

레이어 파라미터 쪽 (MDL 사양 §21.6) `[웹검증]`:
> `bsdf weighted_layer(float weight, bsdf layer, bsdf base = bsdf(), float3 normal = state::normal());`
> "normal – Surface normal vector, in internal space, **applied to top layer**."

→ `normal:` 인자는 **해당 top layer에만** 적용된다.
**위험 시나리오:** 노멀맵 노드가 `state::normal()` 에 뿌리를 두지 **않고** 독립적으로 노멀을 계산해
`normal:` 에 꽂으면 **그 레이어에서 rounded corner가 소실**된다 `[추정 — 사양 연역]`.
이것이 "노멀맵을 걸면 무시되더라"는 증상의 실제 메커니즘일 수 있다.
**단 OmniPBR은 안전하다** — `OmniPBRBase.mdl:202` 가 `state::normal()` 을 기저로 쓴다. `[로컬검증]`

동일 패턴이 `mdl/OmniSurface/OmniSurfaceBase.mdl:883-887` 에도 있다 → OmniSurface도 round edges 지원.
`SimPBR.mdl`, `OmniGlass*.mdl` 에는 **없다** (`grep rounded_corner_normal` 결과: `Base/OmniPBRBase.mdl`,
`mdl/OmniSurface/OmniSurfaceBase.mdl`, `mdl/nvidia/core_definitions.mdl`, `VRay/vray_maps.mdl` 4개뿐).

### 1.2 RTX 런타임 구현 — 실재 확인 (핵심 근거)

`[로컬검증]` `isaacsim/extscache/omni.hydra.rtx-1.0.0+d02c707b.lx64.r/bin/deps/librtx.mdltranslator.plugin.so`
의 문자열에서 다음이 나온다:

```
_ZN5state21rounded_corner_normalEU7uniformfU7uniformbU7uniformf=mdlRoundedCornerNormal
mdl::state::rounded_corner_normal
RoundedCornerNormal                        ← state 함수 시맨틱 열거에 포함
                                             (TransformPoint/TransformVector/TransformNormal/
                                              MetersPerSceneUnit/SceneUnitsPerMeter/ObjectID 와 나란히)
export float mdlRoundedCornerRadius(int index, Shading_state_material state)
export bool  mdlRoundedCornerAcrossMaterials(int index, Shading_state_material state)
export float mdlRoundedCornerRoundness(int index, Shading_state_material state)
export int   mdlRoundedCornerCountInUse()
    // Note, number of rounded corners is forced to 1, always eval the first
mdl_rounded_corner_normal_radius_ / _roundness_ / _across_materials_
add_material failed for rounded corner functions of %s.      ← 에러 메시지 = 실제 경로 존재
```
그리고 `librtx.materialdb.plugin.so` 에 셰이더 define:
```
MDL_ROUNDED_CORNER_NORMAL_COUNT
```

**해석:**
1. MDL 컴파일 백엔드가 `state::rounded_corner_normal` 을 **`mdlRoundedCornerNormal` 이라는 렌더러 제공
   내장 함수로 매핑**한다(= 스텁이 아니라 RTX가 직접 구현한 함수로 링크).
2. 번역기는 재질의 round-edge 파라미터를 **argblock에서 읽어 오는 접근자 3개를 별도 셰이더 코드로 생성**하고,
   `mdlRoundedCornerCountInUse()` 로 사용 여부를 알린다.
3. `MDL_ROUNDED_CORNER_NORMAL_COUNT` 는 **PSO 셰이더 define** → 재질에 round edge가 있으면
   파이프라인 자체가 다른 변형으로 컴파일된다.
4. `cutout_opacity`/`displacement` 와 나란히 **standalone 함수 세트**로 추가된다
   (`geometry_cutout_opacity_standalone`, `geometry_displacement_standalone`,
   `add_material failed for rounded corner functions`) → **MDL distilling으로 소실되지 않는다.**
   (distilling은 BSDF만 근사하고 geometry 표현식은 별도 컴파일)

**결론: 미지원이 아니다.** `[로컬검증] 높음`

> 다만 남는 회색지대: `mdlRoundedCornerNormal` 의 **본체**는 RTX 셰이더 라이브러리(SPIR-V/사전컴파일)
> 안에 있어 ASCII 문자열로 안 잡힌다. "함수가 존재하나 상수 반환 스텁"일 가능성을 **문자열만으로는 0으로
> 못 만든다**. 그러나 (a) PSO define, (b) argblock 접근자 생성, (c) count 관리, (d) 전용 에러 경로
> 4가지가 모두 스텁에는 불필요한 장치다 → **스텁일 확률은 낮다.** `[추정]`

### 1.3 가시성 조건 — 감독의 A/B 설계에 직결

`state::rounded_corner_normal` 은 **셰이딩 노멀만** 바꾼다. **실루엣은 각진 채로 남는다.**
따라서 "베벨처럼 보이는" 정체는 **모서리를 따라 생기는 스페큘러 하이라이트 띠**다.
이게 A/B의 전부다.

| 조건 | 요구 | 왜 |
|---|---|---|
| **roughness** | **낮을수록 보인다.** 0.2~0.4 권장, **0.7 이상이면 사실상 안 보임** | 확산 로브가 넓으면 노멀 섭동이 조도에 묻힌다 |
| **specular_level** | 0.5 이상 유지(기본 0.5 OK) | 하이라이트가 효과의 전달 매체 |
| **조명 입사각** | 모서리에 **그레이징(스침각)** 광원 1개 필요. 정면 조명이면 거의 안 보임 | 하이라이트 띠는 grazing에서 최대 |
| **radius vs 픽셀** | 반경이 화면에서 **최소 3~5 px**를 덮어야 육안 판별 | 1 px 미만이면 안티에일리어싱에 소멸 |
| **radius 단위** | **월드 공간 미터.** Isaac Sim은 `metersPerUnit=1` 이라 값 그대로 | `[웹검증]` MDL 사양 §19.3: *"The radius is specified in **meters in world space**. A radius of **0.0 disables** the rounded corners and this function just returns state::normal."* + `[로컬검증]` OmniPBR.mdl:339 |
| **씬 스케일** | **cm 스테이지(metersPerUnit=0.01)를 임포트하면 반경 해석이 100배 어긋난다** | `[웹검증]` 관련 키 **`/rtx/scene/renderMeterPerUnit`** (Float, default **-1.0** = 씬 스케일 따름). *"Some materials depend on scene scale."* 외부 에셋 임포트 후 확인할 것 |
| **인접 지오메트리** | **단독 큐브에서 보인다.** 큐브의 12개 엣지 각각에 이웃 면이 있다. NVIDIA 문서의 비교 이미지 자체가 그 데모 | `[웹검증]` MDL 사양 §19.3: *"changed near surface mesh edges to **blend smoothly into the shading normal of neighboring facets**"*. **이웃 면이 없는 고립된 단일 quad에서는 효과 없음** `[추정]` |
| **`round_edges_across_materials`** | 같은 프림·같은 재질 모서리면 **false로 충분**. **GeomSubset/다중 재질로 쪼갠 지형이면 경계 엣지가 안 둥글어진다 → true 필수** | `[웹검증+로컬검증]` MDL 사양: *"normal smoothing happens **only between facets of equal material**, unless this parameter is set true"*. **우리 씬은 지면을 GeomSubset으로 분할하므로 실제로 물릴 가능성이 높다** |
| **`round_edges_roundness`** | 기본 1.0 유지. **0 = 챔퍼(각진 모따기), 1 = 라운드** | `[웹검증]` MDL 사양: *"A value of 0.0 chamfers the edge and a value of 1.0 gives a rounded edge."* |
| **볼록/오목** | 볼록(convex) 모서리에서 효과가 크다. 오목(concave)은 페이크 필렛으로 보임 | |

**A/B 스파이크 권장 설정** — "보이는지 여부"를 먼저 확정하려면 **가장 유리한 조건**으로 시작:
- 큐브 1개, `reflection_roughness_constant = 0.25`, `metallic_constant = 0`, `specular_level = 0.5`
- `round_edges_radius = 0.02` (2 cm), `roundness = 1.0`, `across_materials = false`
- 큐브 한 변 0.3~0.5 m, 카메라가 모서리를 **화면 폭의 1/3 이상** 채우게 근접
- 광원: 모서리에 대해 60~80° 스침각 distant light 1개, 돔라이트 약하게
- 렌더: 먼저 **PT(Path Tracing)** 로 판정 → 그다음 RT로 재판정 (§1.4)

이 조건에서도 안 보이면 §2 감별표의 "미지원" 쪽으로 강하게 기운다.

### 1.4 웹 교차검증 — **NVIDIA 공식 릴리스노트가 확인해 준다**

`[웹검증]` **Omniverse RTX Renderer 릴리스노트 Kit 106.1** (우리는 106.5 = 그 이후):
> **"Added support for rendering rounded corners driven by MDL rounded corner functions."**

**Kit 106.1 Release Highlights** — 모드 질문에 대한 직답:
> "Of note is also the addition of support for **rounded corners and vertex displacement** driven by
> MDL functions **for both the RTX Real-Time and RTX Interactive (Path Tracing) modes**."

출처: `rtx-renderer-release-notes/106_1.html`, `dev-guide/latest/release-notes/106_1_highlights.html`

보강: 릴리스노트에서 모드 한정 항목은 `RTX Interactive:` / `RTX Real-Time:` 접두사로 명시 구분되는데,
rounded corner 항목은 **공통 `RTX:` 접두사**다.
또 Materials 106.1 릴리스노트에는 **"Rounded Corner Support in RTX Renderers"** 전용 섹션과
공식 MDL 예제(`RoundedCorners` 재질)까지 실려 있다.

**→ 미지원 가설은 소거되었다. RT·PT 양쪽 지원.** 로컬 바이너리 증거(§1.2)와 완전 일치.
**"안 보인다"는 미지원이 아니라 조건/설정 문제다.**

`[미확인]` 106.5에서 프리뷰된 **RTX Real-Time 2.0** 모드에서의 지원 여부는 어떤 문서에도 언급이 없다.
그 모드를 쓸 계획이면 별도 확인 필요.

`[웹검증, 부재확인]` 106.2~106.5 및 107~110 릴리스노트 전수 스캔 결과 **rounded corner 관련 버그
수정 항목 0건**, NVIDIA 스태프 포럼 답변도 없음. 문서상 유일한 경고는
**"Not all materials support rounded corners."** (= 재질이 이 MDL 함수를 호출해야 한다는 뜻)

### 1.5 문서 함정 — **"OmniPBR에는 없으니 커스텀 MDL을 써야 한다"는 결론은 틀렸다**

> ⚠️ **병렬 웹 조사가 여기서 오답에 도달했다. 명시적으로 정정한다.**
> 웹 조사 결론: *"스톡 OmniPBR / OmniSurface / OpenPBR **문서**에 Round Edge Radius 파라미터가
> 존재하지 않는다(세 템플릿 페이지 grep 히트 0) → **커스텀 MDL을 직접 작성해야 한다**."*

**문서에 없다는 관찰은 맞다. 도출한 결론은 틀렸다.** `[로컬검증]`

| 대상 | 공식 문서 페이지 | **우리 설치본의 실제 MDL 소스** |
|---|---|---|
| OmniPBR | Geometry 그룹 **없음** (Albedo/Reflectivity/AO/Emissive/Opacity/Normals/Clearcoat 뿐) | **`OmniPBR.mdl:337-355` 에 3개 전부 존재**, `anno::in_group("Geometry")`, `anno::version(2,1,2)` |
| OmniSurface | 없음 | **`mdl/OmniSurface/OmniSurfaceBase.mdl:883-887` 에 존재** |
| OmniPBR_Opacity | 없음 | **정말 없음** (`anno::version(2,1,0)` 레거시 — §5.5) |

**→ 문서가 뒤처진 것이다. 커스텀 MDL 작성은 불필요하며, 스톡 OmniPBR에 파라미터를 그냥 주면 된다.**
같은 이유로 Kit 106.1 시절 샘플 `.usda` 의 OmniPBR 속성 나열에도 round_edges가 빠져 있다(§2 마지막 행).

**판정 기준 원칙:** 이 프로젝트에서 "기능이 있는가"의 정본은
**① 설치본 MDL 소스 → ② 설치본 바이너리 → ③ 릴리스노트** 순서이며,
**파라미터 레퍼런스 문서 페이지는 근거로 쓰지 않는다**(체계적으로 뒤처져 있음이 확인됨).

---

## §2 `round_edges_radius` 감별 진단표 (렌더 결과 손에 들고 판정)

전제: §1.3 "A/B 스파이크 권장 설정"으로 찍었다고 가정.

| 관찰된 결과 | 판정 | 다음 조치 |
|---|---|---|
| radius=0 vs 0.02 **픽셀 단위로 완전 동일**(diff 이미지가 순수 0), **PT·RT 둘 다** | **미지원 의심 — 그러나 공식 릴리스노트가 지원을 명시하므로(§1.4) 먼저 아래 행들을 전부 소거할 것.** 다 소거하고도 diff=0이면 우리 빌드 고유 결함 | round edges 라인 폐기. **실제 베벨 지오메트리**(chamfer 모델링) 또는 §3 catmullClark+crease로 전환 |
| **PT에서는 보이고 RT에서는 안 보임** | **버그 또는 RT 특이 조건** — 공식적으로는 **양쪽 지원**이므로(§1.4) 미지원 결론 금지 | RT의 조명/노이즈 조건을 바꿔 재시도. 그래도면 데이터 생성 모드 결정에 반영 |
| **재질이 `OmniPBR_Opacity`** 인데 파라미터가 안 보임 | **미지원 — 그 재질에는 파라미터 자체가 없다** | **`OmniPBR` 로 재바인딩** (§5.5) |
| **지면을 GeomSubset/다중 재질로 쪼갠 곳의 모서리만** 안 둥글어짐 | **설정 — `across_materials`** | `round_edges_across_materials = true`. **우리 씬 구조상 실제로 걸릴 가능성이 높은 항목** |
| **cm 단위 외부 에셋**에서만 효과가 이상함(과대/과소) | **설정 — 씬 스케일** | radius는 **월드 미터**. `metersPerUnit` 과 `/rtx/scene/renderMeterPerUnit` 확인 |
| 모서리 근처에 **띠는 생겼는데 너무 약함** | **조건 문제 — roughness** | roughness를 0.25→0.15로, specular_level 0.5→0.7로. 그래도 약하면 radius 2배 |
| 띠가 **너무 뭉개져 면 전체가 흐려짐** | **조건 문제 — radius 과대** | radius를 물체 크기의 3~5% 이하로. 0.02 m는 0.3 m 큐브에 대해 6.7%로 이미 큰 편 |
| **가까이서는 보이나 멀어지면 사라짐** | **정상 동작.** 픽셀 스케일 한계 | 우리 씬의 실제 카메라 거리(2·5·10 m)에서 재판정. 10 m에서 안 보이면 **그 거리대에는 효과 없음**으로 기록하고 근거리 씬에만 사용 |
| **두 프림이 맞닿은 모서리만** 안 둥글어짐 | **설정 문제 — across_materials** | `round_edges_across_materials = true`. 단 이 옵션은 비용이 더 크다 |
| 아예 **재질이 검게/이상하게** 렌더됨 | **설정 문제 — MDL 컴파일 실패** | 콘솔에서 `add_material failed for rounded corner functions of <재질>` / `Failed to generate target code for material` 검색. 나오면 MDL 컴파일 오류 → 재질 재작성 |
| **평면(단일 면)에 걸었는데** 아무 변화 없음 | **정상.** 모서리가 없으면 효과 없음 | 반드시 **모서리가 있는 프림**(큐브/계단 노즈)에서 테스트 |
| 노멀맵을 같이 걸었더니 효과가 사라짐 | **조건 문제 — 노멀맵 강도 과대** | `bump_factor`를 0으로 내려 격리 테스트. §1.1대로 둘은 곱해지므로 상쇄가 아니라 **가려짐**이다 |
| USD에 `inputs:round_edges_radius` 를 썼는데 UI/렌더에 반영 안 됨 | **설정 문제 — MDL 버전/서브아이덴티파이어** | 우리 로컬 OmniPBR은 `anno::version(2,1,2)` 로 round_edges 포함. 그러나 Kit 106.1 시절 테스트 USDA의 OmniPBR 속성 나열에는 round_edges가 **없다** → 오래된 `.mtl.usda` 프리셋을 쓰면 누락. **MDL 파일을 직접 참조**하고 파라미터를 명시 author할 것 |

**한 줄 감별 규칙:**
> 공식 릴리스노트가 **106.1부터 RT·PT 양쪽 지원**을 명시했고 로컬 바이너리도 일치한다(§1.2·§1.4).
> **따라서 "미지원"은 기본 가설이 아니다.**
> **PT + `OmniPBR`(Opacity 아님) + roughness 0.25 + 그레이징 광원 + 화면 큰 모서리 + radius 2 cm +
> `across_materials=true`** 를 전부 만족시키고도 diff가 0일 때에만 미지원을 의심하라.
> 그 전의 모든 "안 보임"은 위 표를 순서대로 소거하는 문제다.

---

## §3 `subdivisionScheme = catmullClark` + crease

### 3.1 결론: 진짜 세분한다. 단 기본값이 0이라 아무 일도 안 일어난다

`[로컬검증]` `librtx.hydra.so` 안에 **OpenSubdiv 3.4.3 심볼이 통째로 링크**되어 있다:

```
OpenSubdiv::v3_4_3::Far::TopologyRefiner::RefineUniform(Far::UniformOptions)
OpenSubdiv::v3_4_3::Far::TopologyRefinerFactory<Far::TopologyDescriptor>::assignComponentTags(...)
OpenSubdiv::v3_4_3::Far::StencilTableFactoryReal<float>::Create(...)
OpenSubdiv::v3_4_3::Far::PatchTable::~PatchTable()
OpenSubdiv::v3_4_3::Sdc::Crease::SHARPNESS_SMOOTH
OpenSubdiv::v3_4_3::Sdc::Crease::DetermineVertexVertexRule(float, int, float const*)
OpenSubdiv::v3_4_3::Sdc::Crease::ComputeFractionalWeightAtVertex(...)
OpenSubdiv::v3_4_3::Sdc::Crease::SubdivideEdgeSharpnessesAroundVertex(int, float const*, float*)
OpenSubdiv::v3_4_3::Vtr::internal::FVarRefinement::getFractionalWeight(...)
OpenSubdiv::v3_4_3::Vtr::internal::FVarLevel::getVertexCreaseEndValues(...)
pxrInternal::PxOsdMeshTopology::PxOsdMeshTopology(TfToken, TfToken, VtArray<int>, ..., PxOsdSubdivTags const&)
pxrInternal::HdChangeTracker::IsSubdivTagsDirty(unsigned, SdfPath const&)
pxrInternal::PxOsdOpenSubdivTokens
```

그리고 소스 파일 경로와 로그 문자열:
```
../../../source/sharedlibs/rtx.geometryprocessing.lib/Mesh/Subdivision.cpp
Hydra Mesh Subdivision (non-streaming)
Mesh '%s' subdivision completed with the following messages:
Loop subdivision scheme requested for non-triangle topology. Falling back to Catmull-Clark.
Subdivision adaptive refinement is enabled but not supported. Reverting to uniform subdivision.
Subdivision Failed. / Failed to subdivide topology.
Subdivision primvar data not float
GPU position update is not supported for subdivided geometries.
```

### 3.2 crease 지원 — 지원됨

`PxOsdSubdivTags` 는 USD의 `creaseIndices`/`creaseLengths`/`creaseSharpnesses` +
`cornerIndices`/`cornerSharpnesses` + `interpolateBoundary` + `faceVaryingLinearInterpolation` +
`triangleSubdivisionRule` 을 담는 컨테이너다. 이게 생성자 인자로 들어가 있고,
`Sdc::Crease::*` 심볼(sharpness rule, fractional weight, edge sharpness subdivision)이
**전부 링크되어 있다** → **crease/corner sharpness가 실제로 적용된다.** `[로컬검증] 높음`
`HdChangeTracker::IsSubdivTagsDirty` 존재 → subdiv tag 변경을 런타임에 추적한다.

`FVarRefinement`/`FVarLevel`/`GetNumFVarValuesTotal` 존재 → **UV(face-varying primvar)도 함께 세분**된다.
`[로컬검증]` (텍스처가 세분 후 뒤틀리지 않는다는 뜻)

### 3.3 설정 키 — 실제 존재하는 것들

| 키 / 속성 | 종류 | 범위 | 기본값 | 근거 |
|---|---|---|---|---|
| `/rtx/hydra/subdivision/refinementLevel` | carb (int) | **0~8 hard range** | **0** (= 세분 안 함) | `[로컬검증]` `common_widgets.py:49` + `[웹검증]` `rtx-renderer_common.html` 이 default 0 명기 |
| `/rtx/hydra/subdivision/adaptiveRefinement` | carb (bool) | — | **False** | `[웹검증]` 기본값. **그러나 아래 ⚠️ 참조 — 우리 빌드에서는 미구현** |
| `refinementEnableOverride` | **USD 프림 custom 속성 (bool)** | — | false | `[로컬검증]` `prim_geometry_widget.py:86`, `omni.usd/tests/test_refinement.py` + `[웹검증]` NVIDIA `usd-exchange-samples/createMaterials` |
| `refinementLevel` | **USD 프림 custom 속성 (int)** | — | 0 | 동상 (`prim_geometry_widget.py:89`) |
| `/rtx/scene/renderMeterPerUnit` | carb (float) | — | **-1.0** | `[웹검증]` "Some materials depend on scene scale." §1.3 참조 |

> ※ 조사 지시서에 있던 `/rtx/hydra/subdivision/adaptive` 는 **틀린 이름**이다. 실제는 `adaptiveRefinement`.

**⚠️ 문서와 바이너리가 충돌한다 — 바이너리를 믿어라**

`[웹검증]` 공식 문서(`rtx-renderer_common.html`)는 `adaptiveRefinement` 를 **작동하는 기능처럼** 설명한다:
> "Feature-adaptive refinement automatically increases or reduces refinement level based on geometric
> features. This reduces the number of polygons used in flat areas for example."

`[로컬검증]` 그러나 **우리 설치본의 `librtx.hydra.so` 는 이렇게 말한다**:
```
"Subdivision adaptive refinement is enabled but not supported. Reverting to uniform subdivision."
```
그리고 링크된 OpenSubdiv 심볼은 `Far::TopologyRefiner::**RefineUniform**` 뿐이며
`RefineAdaptive` / `PatchTableFactory` 는 **없다**.

**→ 106.5에서 adaptive는 켜도 균등으로 되돌아간다. 삼각형 4^N 폭증을 adaptive로 막을 수 없다.**
문서를 믿고 대형 지형에 adaptive를 기대하면 메모리에서 사고가 난다.

**106.4 개선 사항** `[웹검증]`: *"RTX: **Meshes with subdivision refinement are now cached**, speeding up
scene load time."* → refinement이 **씬 로드 시점(scene translation)** 에 수행됨을 재확인. 런타임 테셀레이션 아님.

UI 툴팁 원문 `[로컬검증]`:
> "The refinement level for all primitives with **Subdivision Schema not set to None**.
>  Each increment increases the mesh triangle count by a factor of 4."

**이 한 문장이 §3의 핵심이다.** 전역 refinementLevel은 **subdivisionScheme이 none이 아닌 프림에만**
적용된다. 즉 두 조건이 **동시에** 필요하다:
1. Mesh에 `subdivisionScheme = "catmullClark"` (USD 기본값이 이미 catmullClark이지만, 대부분의
   임포터/우리 생성 코드는 `"none"` 을 명시 author한다 — **확인 필수**)
2. `/rtx/hydra/subdivision/refinementLevel ≥ 1` **또는** 프림에
   `refinementEnableOverride = true` + `refinementLevel = N`

**"catmullClark을 줬는데 각져 보인다"의 압도적 1순위 원인은 refinementLevel=0 이다.** 설정 문제.

### 3.4 비용·제약

- **균등(uniform) 세분만** 지원 → 레벨 N이면 삼각형 수 **4^N 배**. 레벨 2 = 16배, 레벨 3 = 64배.
  대형 지형에 전역으로 걸면 즉사한다. **프림별 override 사용을 권장.**
- CPU 측 OpenSubdiv Far API(`RefineUniform` + `StencilTableFactory`)를 쓴다 →
  **스테이지 로드 시 CPU 비용**, GPU 실시간 테셀레이션이 아니다. `[로컬검증]`
- `"GPU position update is not supported for subdivided geometries."` →
  **세분된 메시는 GPU에서 정점을 갱신할 수 없다**. 애니메이션/디포밍 메시와 조합 금지.
  우리 씬은 정적이므로 무관.
- `"Subdivision primvar data not float"` → float이 아닌 primvar(예: int/bool 블렌드 마스크)는
  세분 대상에서 탈락한다. **`NegObsGround.mdl` 이 읽는 `blend_tw`/`blend_wb` primvar는
  반드시 float으로 author할 것.** (이미 float이면 OK)
- `"Loop subdivision scheme requested for non-triangle topology. Falling back to Catmull-Clark."` →
  scheme=`loop`을 줘도 쿼드 메시면 조용히 catmullClark으로 바뀐다.

### 3.5 감별표 (subdivision이 안 먹을 때)

| 관찰 | 판정 | 조치 |
|---|---|---|
| 삼각형 수가 전혀 안 늘어남 | **설정** | `/rtx/hydra/subdivision/refinementLevel` 확인(기본 0). 프림의 `subdivisionScheme` 이 `"none"`으로 author되어 있는지 확인 |
| 일부 프림만 안 됨 | **설정** | 그 프림에 `refinementEnableOverride=true, refinementLevel=0` 이 걸려 있을 수 있다. `ClearRefinementOverrides` 커맨드로 초기화 |
| crease를 줬는데 무시됨 | **데이터** | `creaseIndices`/`creaseLengths`/`creaseSharpnesses` **3개 배열 길이 정합** 확인. sharpness는 배열이 crease당 1개 또는 edge당 1개 |
| 콘솔에 `Subdivision Failed.` / `Failed to subdivide topology.` | **데이터(비다양체 등)** | 메시 토폴로지 오류. 중복 정점/뒤집힌 면 정리 |
| adaptive를 켰는데 균등으로 나옴 | **미구현 — 정상** | 106.5에서 adaptive는 없다. 로그가 그렇게 말한다 |
| 세분됐는데 UV가 뒤틀림 | **설정** | `faceVaryingLinearInterpolation` 조정 (기본 `cornersPlus1`) |

---

## §4 정점 변위 메시의 노멀

### 4.1 Hydra는 normals를 자체 계산한다 — 두 경로 모두 존재

`[로컬검증]` `librtx.hydra.so` / `librtx.scenedb.plugin.so`:
```
bool omni::usd::hydra::Mesh::recomputeNormals(bool)
recomputeNormalsData
rtx::geometryprocessing::computeSmoothNormals   / computeSmoothNormalsBatch
rtx::geometryprocessing::computeFlatNormals     / computeFlatNormalsBatch
pxrInternal::Hd_SmoothNormals::ComputeSmoothNormals(Hd_VertexAdjacency const*, int, GfVec3f const*)
"Ensure normals are vertex or face varying"
```
`/rtx/hydra/TBNFrameMode` (combo: **Auto / CPU / GPU / Force GPU**) `[로컬검증]`
`omni.rtx.settings.core/.../common_widgets.py:17-21`, 툴팁:
> "Mode selection for vertex **Normals and Tangents generation**. AUTO: selects the mode depending on
>  available data and data update pattern. CPU: uses mikktspace ... GPU: allows normal and tangent
>  basis update on the GPU ... for deforming meshes."

**→ `normals` 를 안 주면 Hydra가 생성한다. "노멀이 아예 없어서 검게 나온다"는 일은 없다.**

### 4.2 폴백은 **smooth** 다 — 각져 보이면 원인은 노멀이 아니라 **정점 분리(welding)** 다

`[로컬검증]` `librtx.hydra.so` 결정적 문자열 2개:
```
Mesh '%s' update topology/point without updating normal, fallback to smooth normal.
```
그리고 메시 처리 파이프라인의 **스테이지 이름 목록**(`rtx.geometryprocessing.lib/Mesh/MeshProcessing.cpp`):
```
Ensure normals  →  Compute smooth normals  →  Compress tangent space  →  Pack Vertex Data
Compute vertex to edge adjacency
rtx::geometryprocessing::ensureVertexOrFaceVaryingAuthoredNormals   (MeshNormals.cpp)
rtx::geometryprocessing::computeVertexToEdgeAdjacencyTable
rtx::geometryprocessing::computeWeldedVertexToFaceVaryingIndicesNormalAdjacencyTable
```

**→ `normals` 를 안 주면 Hydra RTX는 SMOOTH(정점 평균) 노멀을 계산한다.** `[로컬검증] 높음`
`computeFlatNormals` 도 존재하나 **파이프라인 스테이지로 이름이 붙은 것은 "Compute smooth normals"
쪽뿐**이고, 폴백 로그도 명시적으로 *"fallback to **smooth** normal"* 이라고 말한다.

**이건 내 초기 가설(§ZZ 우려)의 정정이다. 평면 그리드를 변위시켜도 기본적으로는 매끈하게 나온다.**

**⚠️ 단, USD 사양은 반대로 말한다** `[웹검증]` — OpenUSD UsdGeomMesh:
> "If a polygonal mesh specifies neither `normals` nor `primvars:normals`, then it should be
> **treated and rendered as faceted, with no attempt to compute smooth normals**."

**사양(faceted) vs 우리 설치본 바이너리(smooth fallback)가 충돌한다.**
NVIDIA 자신의 Asset Requirement가 이 불일치를 인정한다 — *"Missing normals may lead to unrealistic
**faceting or soft edges**. **Automatic generation** of normals may not accurately represent the
intended surface appearance."* (즉 **결과가 예측 불가**라는 뜻).

**→ 결론: 렌더러 폴백에 의존하지 말 것.** 우리 빌드에서는 smooth로 나올 가능성이 높지만
(로컬 로그 문자열이 그렇게 말한다), **사양과 다르고 NVIDIA 스스로 "예측 불가"라 경고한다.**
§4.3의 2번(노멀 직접 author)이 **공식 권고이자 안전한 길**이다.

#### 그럼에도 각져 보인다면 — 진범은 **정점 분리**다
smooth normal은 `computeVertexToEdgeAdjacencyTable` / `...WeldedVertexToFaceVarying...` 로 만든
**인접 테이블**을 따라 평균낸다. 정점이 **분리(split)되어 있으면 인접이 끊겨 평균이 안 된다.**
관련 실체 `[로컬검증]`:
```
/rtx/hydra/weldVertex                                              (carb 설정, bool)
, weldingEnabled=
rtx::geometryprocessing::weldFaceVaryingIndicesAndSplitVertices    (MeshWelding.cpp)
```
즉 **UV 심(seam)·재질 경계·GeomSubset 경계에서 정점이 쪼개지면 그 선을 따라 각진 이음매가 보인다.**
평면 그리드를 코드로 생성하면서 face마다 정점을 새로 찍으면(인덱스 미공유) **전면이 패싯으로 보인다** —
이게 실제 1순위 원인이다.

#### 반대 방향의 함정
자동 smooth는 **모든 모서리를 둥글린다.** 계단 노즈·연석 같은 **날카로워야 할 모서리도 뭉개진다.**
→ **날카로운 모서리가 필요한 프림은 `normals` 를 반드시 직접 author**(또는 해당 에지에서 정점 분리)
해야 한다. 즉 "노멀을 안 주면 된다"는 지면에만 통하는 얘기다.

### 4.3 실무 처방 (변위 지면용)

**권장 순서:**
1. **가장 저렴: `subdivisionScheme="none"` + `normals` 미기재 + 정점 인덱스 공유(welded) 그리드.**
   Hydra가 smooth normal을 만들어 준다. **정점을 공유하는 인덱스 버퍼로 그리드를 만드는 것만
   지키면 된다.** ← **우리 권장 기본값**
2. 더 확실하게: **변위 후 면적 가중 정점 노멀을 직접 계산해 author.** ← **NVIDIA 공식 권고와 일치**
   렌더러 폴백에 의존하지 않으므로 결정론적이고, 이후 날카로운 모서리 제어도 가능해진다.
   - **NVIDIA Asset Requirement VG.027 `usdgeom-mesh-normals-exist`** `[웹검증]`:
     > Summary: **"All non-subdivided meshes must have normals."**
     > "Missing normals may lead to unrealistic **faceting or soft edges**.
     > **Automatic generation** of normals may not accurately represent the intended surface appearance."
   - 인터폴레이션은 **`vertex` 또는 `faceVarying` 만 허용**. `[로컬검증]`
     `"Ensure normals are vertex or face varying"`,
     `"Unsupported normal primvar interpolation mode detected: {}"` →
     **`uniform`/`constant` 는 거부되고 경고가 뜬다.**
     (USD 사양상 `uniform`=face당 1개=flat, `vertex`=smooth, `faceVarying`=hard edge 표현 가능)
   - 배열 길이 불일치도 잡아낸다:
     `"Invalid normal primvar data: buffer size {} does not match expected size {} with interpolation mode {}"`
   - **어느 어트리뷰트에 쓸 것인가 — `primvars:normals` 를 권장** `[웹검증]` (내 초기 서술 정정):
     - OpenUSD: *"If `normals` and `primvars:normals` are both specified, **the latter has precedence**."*
     - NVIDIA VG.027: *"**'primvars:normals' is the preferred representation** as it allows for indexing"*,
       그리고 *"**only one of these representations should exist on each mesh**"* — 둘 다 쓰지 말 것.

**⚠️ 3번째 함정 — `subdivisionScheme` 을 명시하지 않으면 author한 노멀이 무시된다** `[웹검증]`

OpenUSD 사양:
> "...the subdivisionScheme attribute, which is **set to specify Catmull-Clark subdivision by default**,
> so polygonal meshes must always be explicitly declared."
> "**Normals should not be authored on a subdivision mesh**, since subdivision algorithms define their
> own normals. They should only be authored for polygonal meshes (subdivisionScheme = "none")."

NVIDIA Asset Requirement `usdgeom-mesh-subdivision` — Summary: **"Do not subdivide meshes with Normals."**
> "**If this attribute is unset the mesh will be subdivided by default**, so it is important to set the
> value explicitly to 'None' when subdivision is not required."
> "**If the subdivision scheme is set and there are also surface normals, the surface normals will be
> ignored.**"

**→ 변위 그리드에 노멀을 정성껏 계산해 넣어도, `subdivisionScheme` 을 명시 안 했으면
(= 기본 catmullClark) 그 노멀이 통째로 무시된다.**
**반드시 `subdivisionScheme = "none"` 을 명시 author할 것.** 이건 우리 지형 생성 코드에서
**즉시 점검해야 할 항목**이다.
3. **`subdivisionScheme="catmullClark"` + `refinementLevel 1~2`** 는 밀도와 매끈함을 동시에 주지만
   **극한면 평활화가 변위 진폭을 깎는다** `[추정]` — 5~20 mm 미세 변위에는 손해. 지면에는 1·2를 권장.
4. 어느 쪽이든 **변위 후 노멀 상태를 확인할 것.** 위 폴백 로그
   (`update topology/point without updating normal`)가 콘솔에 뜨면 **노멀이 재계산되고 있다는
   확인 신호**이자, 반대로 **author된 옛 노멀을 그대로 쓰고 있지 않다는 증거**다.
5. 마이크로 디테일은 **normal map + `detail_normalmap_texture`** 로 보강
   (ZZ 확인대로 detail normal 사용 가능 — 단 NegObsGround에는 없다. §8 G7).

### 4.4 감별표

| 관찰 | 판정 | 조치 |
|---|---|---|
| 변위 지면이 **격자 전체가 패싯** | **데이터 — 정점 미공유(분리)** | 그리드를 **인덱스 공유** 방식으로 재생성. `/rtx/hydra/weldVertex` 상태 확인 |
| **특정 선(심)을 따라서만** 각짐 | **데이터 — UV심/GeomSubset 경계 정점 분리** | 정상 동작. 심 위치를 조정하거나 해당 구간 노멀을 직접 author |
| 지면이 **완전히 평평하게 조명됨**(변위가 실루엣에만) | **데이터 — 옛 노멀 잔존** | 변위 전 `normals` 를 author해 둔 상태. **`normals` 를 지우거나 재계산** |
| 콘솔에 `Unsupported normal primvar interpolation mode` | **설정 — 인터폴레이션** | `uniform`/`constant` → `vertex` 로 |
| 콘솔에 `Invalid normal primvar data: buffer size ...` | **데이터 — 배열 길이** | vertex면 points 수, faceVarying이면 faceVertexIndices 수와 일치시킬 것 |
| 계단 노즈·연석이 **뭉개져 보임** | **정상 — 자동 smooth의 부작용** | 그 프림만 `normals` 직접 author, 또는 해당 에지에서 정점 분리 |
| 노멀맵 방향이 뒤집혀 보임 | **설정** | `flip_tangent_v` (OmniPBR 기본 **true**). `/rtx/hydra/TBNFrameMode` 를 CPU(mikktspace)로 고정해 교차확인 |
| 세분했더니 변위가 약해짐 | **정상 — 극한면 평활화** | 진폭 상향, 또는 subdivisionScheme=none 경로로 |

---

## §5 알파 컷아웃 (나무 임포트 대비)

### 5.1 함정은 4층이다 (MDL측 3 + 렌더러측 1)

`[로컬검증]` `OmniPBR.mdl:196-229` 및 `OmniPBR_ClearCoat.mdl` 본문:
```mdl
uniform bool  enable_opacity          = false          // ← 1차 함정
uniform bool  enable_opacity_texture  = false          // ← 2차
uniform base::mono_mode opacity_mode  = base::mono_average   // ← 3차 (알파가 아니라 평균!)
uniform float opacity_threshold       = float(0.0)     // ← 4차
float opacity_value  = enable_opacity_texture ? base::file_texture(...).mono : opacity_constant;
float cutout_opacity = enable_opacity
                       ? ((opacity_threshold == 0.0) ? opacity_value
                                                     : (opacity_value >= opacity_threshold ? 1.0 : 0))
                       : 1.0;
```

**우리 조사 §10.2 정정 필요:**
> ZZ §10.2: "`opacityThreshold` 기본값이 0.0 이라 설정하지 않으면 잎이 전부 불투명 판때기가 된다."

**절반만 맞다.** 잎이 불투명 판때기가 되는 **직접 원인은 `enable_opacity = false`(기본값)** 이다.
`opacity_threshold = 0.0` 은 MDL 주석대로 *"use fractional opacity values 'as is'"* — 즉
**컷아웃이 아니라 알파 블렌딩(반투명)** 을 의미한다. 결과는 "불투명 판때기"가 아니라 **"유령처럼 반투명한
잎"** 이거나, 렌더러 설정에 따라 **다시 불투명**이 된다(아래 5.2). 증상이 다르므로 오진하면 시간을 버린다.

또 `opacity_mode` 기본값이 **`mono_average`(RGB 평균)** 다. 잎 텍스처의 알파를 쓰려면
**`mono_alpha` 로 바꿔야 한다.** 안 바꾸면 잎의 **색 밝기**가 알파로 해석되어 어두운 잎이 사라진다.
이건 ZZ에 없던 함정이다.

### 5.2 렌더러측 (4번째 층 — 그리고 기본값이 우리에게 불리하다)

`[로컬검증]` 실존 키:
```
/rtx/raytracing/fractionalCutoutOpacity      (RT Real-Time)
/rtx/pathtracing/fractionalCutoutOpacity     (Path Tracing)
/rtx/shadows/fractionalCutoutOpacity         (그림자 전용)
/rtx/sceneDb/allowDuplicateAhsInvocation     (any-hit 중복 호출)
/rtx/debug/onlyOpaqueRayFlags                ("Hide Geometry That Uses Opacity (debug)")
/rtx/materialDb/perInstanceOpacityToggle
/rtx/material/translucencyAsOpacity  /  /rtx/sceneDb/translucencyAsOpacity
```
Replicator 문서 원문 `[로컬검증]`
(`omni.replicator.core/scripts/settings.py:99, 151`):
> `/rtx/raytracing/fractionalCutoutOpacity` (bool): Enables fractional cutout opacity values
> resulting in a **translucency-like effect similar to alpha-blending**.
> `/rtx/pathtracing/fractionalCutoutOpacity` (bool): If enabled, fractional cutout opacity values are
> treated as a measure of surface **'presence'** resulting in a translucency effect similar to
> alpha-blending. Path-traced mode uses **stochastic sampling** based on these values to determine
> whether a surface hit is valid or should be skipped.

**⚠️ 기본값 정정** `[웹검증]`: `/rtx/pathtracing/fractionalCutoutOpacity` 의 **기본값은 `True`** 이고,
`/rtx/raytracing/fractionalCutoutOpacity` 도 NVIDIA 공식 워크플로 문서와 샘플 USD 덤프에서
`bool "rtx:raytracing:fractionalCutoutOpacity" = 1` 로 나타난다.
**→ 즉 기본 상태가 "fractional(알파 블렌딩 유사)"이다.** 내가 앞서 "꺼져 있으면"으로 적은 가정은 반대였다.

**따라서 아무 설정도 안 하면 (MDL `opacity_threshold=0`) + (렌더러 fractional=True) 조합이 되어
잎은 "반투명 유령"으로 렌더된다.** ZZ §10.2의 "불투명 판때기" 증상은 **`enable_opacity=false`**
(= opacity 경로 자체 미진입) 때문이다. **두 증상은 원인이 다르며 처방도 다르다.**

NVIDIA 스태프(mati-nvidia) `[웹검증]`:
> "You can tell the Opacity attribute to use the alpha channel of an RGBA image...
> For **Real-Time** renderer, you'll need to enable 'Fractional Cutout Opacity'.
> For **Interactive**, it should just work."

(단 이는 *fractional 룩* 기준이다. 하드 컷아웃(threshold>0)에서는 fractional 값이 남지 않으므로
이 설정은 무의미해진다.)

**`/rtx/shadows/fractionalCutoutOpacity` 라는 전용 키가 존재한다는 사실 자체가
"그림자에 알파가 반영된다"의 강한 증거다.** `[로컬검증]` 별도 키가 없다면 그림자용 분기가 없다는 뜻이므로.
보강 정황 `[웹검증]`: RTX Common 디버그 문서 *"**Any Hit shaders are invoked when ray intersections
are not opaque**"* (any-hit = 그림자/2차 광선의 opacity 평가 경로) + `/rtx/debug/onlyOpaqueRayFlags`
의 존재(평시엔 non-opaque ray flag를 쓴다는 뜻).
**공식 단정 문장은 못 찾았다** `[추정(강)]`.

### 5.2b **[최중요] Replicator 세그멘테이션 GT가 알파에 오염된다 — 공식 확인**

`[웹검증]` Replicator 공식 문서 `ext_replicator/annotations_with_transparency.html` **원문**:
> "**`Enable Opacity` must be true**, and the opacity map is what controls the opacity.
> **Segmentation is true for values of 1.0. Values below do not show segmentation.**"
>
> "Controlling whether a mesh with a transparent material appears in segmentation, is done through the
> mesh `Cast Shadows` flag, attribute name of **`primvars:doNotCastShadows`**."

**이것이 이 문서 전체에서 우리 프로젝트에 가장 중요한 발견이다.**

**함의:**
- `opacity_threshold = 0.0`(**기본값**, = 알파 블렌딩)이면 잎 텍스처의 안티에일리어싱된 가장자리 texel은
  α < 1.0 이다 → **semantic / instance 마스크에서 그 픽셀들이 통째로 빠진다.**
  잎 실루엣이 너덜너덜해지고, **얇은 잎은 마스크가 거의 사라질 수 있다.**
- `opacity_threshold > 0` 이면 MDL이 opacity를 **정확히 0 또는 1로 remap**하므로(§5.1 코드)
  **마스크 경계가 RGB 실루엣과 일치한다.**
- 깊이(depth)도 위험하다 `[추정(강)]`: PT 문서의 *"Path-traced mode uses **stochastic sampling** based
  on these values to determine whether a surface hit is valid or should be skipped"* 때문에,
  fractional 상태에서는 **잎 가장자리 픽셀의 `distance_to_camera` 가 프레임마다 잎 앞면과 배경 사이를
  확률적으로 튄다.** 우리는 **낙차(depth discontinuity)를 GT로 만드는** 파이프라인이므로 치명적이다.
  하드 컷아웃이 이 확률성을 제거한다. (공식 확인 문장은 못 찾음)

**→ §5.3의 하드 컷아웃 권장은 "미학적 선호"가 아니라 GT 무결성 요구사항이다.**

### 5.3 잎 알파를 제대로 내리는 정답 조합

**하드 컷아웃(권장 — 학습 데이터용):**
```
enable_opacity            = true          ← 반드시. 기본 false
enable_opacity_texture    = true          ← 반드시. 기본 false
opacity_texture           = <잎 알파/RGBA 텍스처>
opacity_mode              = mono_alpha    ← 반드시. 기본 mono_average(오답)
opacity_threshold         = 0.3 ~ 0.5     ← 0이면 컷아웃이 아니라 블렌딩
```
그리고 렌더러:
```
/rtx/raytracing/fractionalCutoutOpacity   = false   (컷아웃이면 fractional 불필요)
/rtx/pathtracing/fractionalCutoutOpacity  = false
/rtx/shadows/fractionalCutoutOpacity      = false
```

**왜 컷아웃이 블렌딩보다 나은가 (우리 프로젝트 한정):**
1. **GT 무결성 — §5.2b 참조. 공식 문서로 확인된 사항이다.**
   *"Segmentation is true for values of 1.0. Values below do not show segmentation."* `[웹검증]`
   → 블렌딩 잎은 semantic/instance 마스크가 **실루엣과 어긋난다.**
2. **깊이 GT의 확률적 요동 제거** (PT stochastic sampling) `[추정(강)]`.
3. PT의 stochastic sampling은 **spp가 낮으면 노이즈**로 나타난다.
4. 컷아웃은 결정론적이라 RT/PT 정합성이 좋다.

**보조 레버** `[웹검증]`: 특정 메시를 세그멘테이션에서 **의도적으로 빼거나 넣는** 제어는
`primvars:doNotCastShadows` (mesh `Cast Shadows` 플래그)로 한다. 투명 재질 메시의 세그멘테이션
참여 여부가 이 플래그에 묶여 있다는 점을 기억할 것 — **그림자 설정을 만지면 라벨이 바뀐다.**

`[웹검증, 부재]` NVIDIA의 **foliage 전용 `opacity_threshold` 권장값은 공식 문서에 없다.**
가장 근접한 공식 문장은 Replicator의 *"Masked transparency is available using `Enable Opacity` on the
`OmniPBR` material and others. This can be used for objects such as **chain link fences**."* 뿐이다.
커뮤니티 관례(UsdPreviewSurface `opacityThreshold`)는 **0.5**를 "기본 컷아웃 값"으로 쓴다 `[추정]`.

**디버그 팁** `[로컬검증]`: `/rtx/debug/onlyOpaqueRayFlags = true` ("Hide Geometry That Uses Opacity")
를 켜면 **opacity를 쓰는 모든 오브젝트가 사라진다.** 잎이 사라지면 → 알파 경로를 타고 있다는 증거.
안 사라지면 → `enable_opacity` 가 꺼져 있다는 증거. **1분짜리 결정적 감별 도구다.**

### 5.4 성능

- 컷아웃 지오메트리는 **non-opaque BLAS**가 되어 **any-hit 셰이더**를 호출한다.
  `/rtx/sceneDb/allowDuplicateAhsInvocation`, `/rtx/debugView/heatMapMaxAnyHitCount` (any-hit 횟수
  히트맵 디버그뷰) 존재 `[로컬검증]` → any-hit 비용이 실제 병목으로 관리되고 있다는 방증.
- **공식 성능 서술** `[웹검증]` (RTX Common 문서, Any Hit Heat Map 디버그뷰):
  > "Any Hit shaders are invoked when ray intersections are not opaque, which can incur a
  > **high performance cost.** This heat map counts how many Any Hit shaders were invoked in a pixel
  > for the selected pass. It is often used to find materials that have **unwarranted use of translucency**."
  → 나무 44종을 전부 컷아웃으로 깔면 any-hit이 프레임타임을 지배할 수 있다.
  **Any Hit Heat Map 디버그뷰(`/rtx/debugView/heatMapMaxAnyHitCount`)로 먼저 측정할 것.**
  A/B 측정: `/rtx/debug/onlyOpaqueRayFlags = true` 로 opacity 지오메트리를 통째로 숨겨 델타를 본다.
- **OMM(Opacity Micro-Map): 106.5에 없다.** 로컬 문자열 부재(`Shader Feature: Displaced Micro Meshes`
  는 있으나 opacity micromap 상당 문자열 없음) `[로컬검증, 부재]` **+ 웹에서도 105.0~107.x 릴리스노트와
  `/rtx/raytracing/` 하위 어디에도 OMM 언급 없음** `[웹검증, 부재]` → **두 방향으로 부재 확인.
  OMM 가속은 기대하지 말 것.**
- **107.3 이후를 위한 예약 정보** `[웹검증]` — **106.5에는 없다**:
  Kit 107.3에서 `/rtx/material/omniRtxEnableOpacityOverride` 와 Material 프림 속성
  `bool omni:rtx:enableCutoutOpacity = true` 가 추가됐다. 스톡 Kit 재질이 아닌 것(MaterialX 등)이
  non-opaque로 잘못 분류되어 *"causing significant performance degradation"* 하던 문제의 해법이다.
  **우리 106.5에서는 무시하되, 107+ 업그레이드 + MaterialX/OpenPBR 계열 foliage를 쓰면 필수가 된다.**
  (일부 검색 스니펫이 이를 "106.5.6"에 귀속시키나 **오귀속**이다. 원문은 107.3 릴리스노트.)

### 5.5 OmniPBR vs OmniPBR_Opacity

`Base/` 에 `OmniPBR_Opacity.mdl` 이 **별도로 존재**한다(14 KB). `[로컬검증]`
그러나 **`OmniPBR.mdl` 자체가 이미 opacity 파라미터 전체를 갖고 있다**(196-229행) — 설명문도
*"OmniPBR Base with support for clear coat, **opacity** and ORM textures"*.

**파라미터 집합을 기계적으로 diff했다** `[로컬검증]`:

| | `OmniPBR` | `OmniPBR_Opacity` |
|---|---|---|
| `anno::version` | **2, 1, 2** | 2, 1, 0 (구버전) |
| opacity 5종 | 있음 | 있음 |
| **`round_edges_radius` / `_roundness` / `_across_materials`** | **있음** | **없음** |
| `flip_tangent_u` / `flip_tangent_v` | 있음 | **없음** |
| `geometry_normal_roughness_strength` | 있음 | **없음** |
| `ao_texture` | 있음 | **없음** |
| `emissive_color` / `emissive_mask_texture` | 있음 | **없음** |

**→ `OmniPBR` 은 `OmniPBR_Opacity` 의 완전한 상위집합이다. `OmniPBR_Opacity` 는 레거시다.**

**중요한 함정:** 시판/기본 제공 에셋(나무 포함)이 **`OmniPBR_Opacity` 를 바인딩해 오면
그 프림에는 §1의 round edges를 걸 수 없다** — 파라미터가 아예 없다. 임포트 후
`grep -r "OmniPBR_Opacity" <asset>.usd` 로 확인하고, **필요하면 `OmniPBR` 로 재바인딩**할 것.

### 5.6 감별표

| 관찰 | 판정 | 조치 |
|---|---|---|
| 잎이 **불투명 사각 판때기** | **설정 — `enable_opacity=false`** | true로. `onlyOpaqueRayFlags=true` 로 교차검증 |
| 잎이 **반투명·유령** | **설정 — `opacity_threshold=0`** | 0.3~0.5로 |
| **어두운 잎만 사라짐** | **설정 — `opacity_mode=mono_average`** | `mono_alpha` 로 |
| 잎은 보이는데 **그림자가 사각형** | **설정 — 그림자 알파** | `/rtx/shadows/fractionalCutoutOpacity` 확인. 그래도면 그림자 경로 미지원으로 기록 |
| 가장자리 **톱니/지글거림** | **조건 — 밉맵 알파 커버리지** | 알파 밉맵을 coverage-preserving으로 재생성(G팀 지적). threshold 하향도 임시 완화 |
| **semantic/instance 마스크가 RGB 잎 실루엣보다 작거나 너덜너덜** | **설정 — 블렌딩 경로.** α<1 픽셀은 세그멘테이션에서 제외된다 | **`opacity_threshold > 0` 으로 하드 컷아웃. §5.2b — 공식 문서 확인 사항** |
| 특정 메시가 **세그멘테이션에서 통째로 빠짐** | **설정 — `primvars:doNotCastShadows`** | 해당 플래그 확인. 투명 재질의 세그멘테이션 참여가 그림자 플래그에 묶여 있다 |
| PT에서 잎이 **노이즈** | **설정 — fractional + 저 spp** | `pathtracing/fractionalCutoutOpacity=false` |
| depth/semantic GT에서 잎 뒤 배경이 새어나옴 | **블렌딩 경로 사용 중** | 하드 컷아웃으로 전환 (5.3) |

---

## §6 톤매핑·노출

### 6.1 `/rtx/post/tonemap/op` 열거 — **ACES = 6 확정**

`[로컬검증]` `omni.rtx.settings.core/omni/rtx/settings/core/widgets/post_widgets.py:16-24`
(소스 리스트 그대로):

| 값 | 이름 | 비고 |
|---|---|---|
| 0 | Clamp | 노출 조정 자체를 건너뜀. **srgb 변환 안 함** |
| 1 | Linear (Off) | 노출은 적용, 톤커브 없음. Kit 기본 디버그 설정이 이 값 |
| 2 | Reinhard | |
| 3 | Modified Reinhard | `maxWhiteLuminance` 가 이때만 유효 |
| 4 | HejlHableAlu | |
| 5 | HableUc2 | `whiteScale` 가 이때만 유효 |
| **6** | **Aces** | **← 우리가 쓸 값. ZZ 주장 확인됨** |
| 7 | Iray | `irayReinhard/*` 5개 서브키가 이때만 유효 |

### 6.2 실제 존재하는 노출 키 — 우리 조사 부분 정정

`[로컬검증]` `post_widgets.py:56-70` + 바이너리 문자열 추출(`/rtx/*` 키 977개 전수):

| 키 | 타입 | UI 범위 | 판정 |
|---|---|---|---|
| `/rtx/post/tonemap/op` | int | 0~7 | **존재** |
| `/rtx/post/tonemap/filmIso` | float | 50~1600 | **존재** ("Film ISO") |
| `/rtx/post/tonemap/exposureTime` | float | 1e-13 ~ 2.0 | **존재** ("Camera Exposure", **초 단위**) |
| `/rtx/post/tonemap/fNumber` | float | 1~20 | **존재** ("F-stop") ← **여기가 정정 포인트** |
| `/rtx/post/tonemap/whitepoint` | **color3** | — | **존재** (소문자 p! `whitePoint` 아님, 그리고 float 아닌 **컬러**) |
| `/rtx/post/tonemap/cm2Factor` | float | 0~2 | **존재** (씬 단위가 cm가 아닐 때 보정) |
| `/rtx/post/tonemap/colorMode` | int | 0=sRGBLinear, 1=ACEScg | **존재** |
| `/rtx/post/tonemap/enableSrgbToGamma` | bool | — | **존재** (op≠0일 때만 노출) |
| `/rtx/post/tonemap/dither` | float | 0~0.02 | **존재** (밴딩 제거) |
| `/rtx/post/tonemap/maxWhiteLuminance` | float | 0~100 | **존재** (op=3 전용) |
| `/rtx/post/tonemap/whiteScale` | float | 0~100 | **존재** (op=5 전용) |
| `/rtx/post/tonemap/wrapValue` | float | 0~100000 | 존재 |
| `/rtx/post/tonemap/cameraShutter` | ? | — | **바이너리에 존재하나 UI는 `exposureTime` 을 쓴다.** 구버전 USD 덤프에 `rtx:post:tonemap:cameraShutter = 10` 형태로 나타남 `[웹검증]` → **레거시 별칭. 신규 코드는 `exposureTime` 사용** |
| **`/rtx/post/tonemap/enabled`** | — | — | **없음** `[로컬검증, 부재확인]` 977개 키 전수에 미존재. **끄기는 `op=1(Linear)` 또는 `op=0(Clamp)` 으로 표현** |
| **`/rtx/post/tonemap/cameraFStop`** | — | — | **없음** — ZZ 주장 **확인** |
| **`/rtx/post/tonemap/cameraISO`** | — | — | **없음** — ZZ 주장 **확인** |

**병렬 웹 조사가 미해결로 남긴 3건을 로컬 증거가 확정한다** (웹 조사자는 Kit 설치본 접근이 없었다):

| 웹 조사 미해결 항목 | **로컬 확정 답** |
|---|---|
| "f-stop **기능은 존재하나 키 철자 미확인**(`cameraFStop`/`cameraFNumber`/`fNumber` 후보)" | **`/rtx/post/tonemap/fNumber`** — `post_widgets.py:60`, UI "F-stop", 범위 1~20 |
| "`/rtx/post/histogram/enabled` 직접 확인 실패, 추정(강)" | **존재 확정** — `post_widgets.py:76` 이 자동노출 프레임의 마스터 경로로 반환. `auto_exposure.py:14` 도 동일 |
| "`exposureTime` 이라는 키는 찾지 못함, 실제는 `cameraShutter`" | **둘 다 바이너리에 존재하나 UI·현행 경로는 `exposureTime`** (`post_widgets.py:59`, "Camera Exposure", 초 단위) |

**ACES 인덱스 교차검증** `[웹검증]`: NVIDIA "Digital Human Real-Time Rendering Setup" 문서가
*"Set Tone Mapping Operator to 'Linear(Off)'"* 지시문과 저장된 덤프 `int "rtx:post:tonemap:op" = 1` 을
함께 싣는다 → **Linear = 1 확정 = 문서 나열 순서가 그대로 0-base enum** → **ACES = 6.**
로컬 소스 리스트(§6.1)와 완전 일치.

> ⚠️ **오염된 2차 출처 경고** `[웹검증]`: `isaac-sim/IsaacSim` 저장소의
> `skills/isaac-sim-rendering/SKILL.md` 가 `s.set("/rtx/post/tonemap/op", 4) # ACES` 라고 적고 있다.
> **틀렸다** — 4는 HejlHableAlu다. 그 파일은 (a) AI 에이전트가 작성했고 (b) 대상이 Kit 110 / Isaac Sim
> 6.0+ 이며 (c) 같은 블록에서 `whitepoint` 를 스칼라 `6500.0` 으로 설정한다(실제 타입은 **float3 색상**).
> **이 파일을 근거로 삼지 말 것.** `HejlHableAlu` 를 빠뜨린 목록을 쓰면 인덱스가 1칸씩 밀린다.

> **정정:** ZZ §2 상충4의 *"cameraFStop/cameraISO는 106.5에 없음"* 은 **키 이름으로는 맞다**.
> 그러나 그 표기가 *"조리개/ISO 노출 제어를 못 한다"* 로 읽히면 **틀리다** —
> **`filmIso` + `exposureTime` + `fNumber` 3종 세트가 전부 존재**한다.
> 물리 카메라 노출 3요소(ISO·셔터·조리개)를 그대로 구동할 수 있다. Phase 2 캘리브레이션 가능.

### 6.3 자동 노출이 수동 설정을 무력화하는 함정

`[로컬검증]` `post_widgets.py:76` — `AutoExposureSettingsFrame._frame_setting_path()` 가
`"/rtx/post/histogram/enabled"` 를 반환한다. 즉 **`/rtx/post/histogram/enabled` 가 자동 노출 마스터 스위치**다.
그리고 `omni.kit.viewport.menubar.camera/menu_item/auto_exposure.py:14-16`:
```python
SETTING_AUTO_EXPOSURE = "/rtx/post/histogram/enabled"
SETTING_ISO           = "/rtx/post/tonemap/filmIso"
SETTING_WHITE_SCALE   = "/rtx/post/histogram/whiteScale"
```
**뷰포트 메뉴가 이 둘을 한 화면에서 토글한다** → 자동 노출이 켜져 있으면 `filmIso` 조작이
**히스토그램에 덮여 효과가 사라진다.** `[로컬검증]`

**공식 문서가 이를 명문화한다** `[웹검증]` (Kit 103 Post-Processing 문서, Tone Mapping Operator 항):
> "All operators except Clamp apply the exposure adjustment based on the parameters below
> **or the results of the auto-exposure feature.**"

RTX 106.1 릴리스노트도 *"Improved auto-exposure by ignoring pixels with zero alpha in the luminance
histogram."* → 106.x에서 히스토그램 AE가 **활성 경로**임을 확인. `[웹검증]`

**추가 함정 — 카메라 프림의 `exposure` 속성은 배선되어 있지 않다** `[웹검증-NVIDIA 스태프]`
(forums.developer.nvidia.com/t/.../353403, phennings):
> "Kit/RTX still uses a **global** tone-mapping exposure pipeline (auto-exposure, ISO, etc.) accessible
> via render and viewport settings, which is **not per-camera** by default."
> "The 'Exposure' attribute you see on the Camera prim **is not wired into the lighting pipeline**."

**→ 카메라마다 다른 노출을 주는 방법은 없다. 노출은 전역이다.**
다중 카메라 씬에서 카메라별 노출 변주를 계획했다면 **폐기**하고, 렌더 전 전역 설정을 바꿔 별도 패스로
찍거나 학습측 augmentation으로 처리해야 한다. (스태프: *"these settings are global. We offer an
augmentation system for implementing custom per-camera augmentations."*)

관련 키 전량 `[로컬검증]`:
`/rtx/post/histogram/enabled` · `filterType`(0=Median,1=Average) · `tau`(적응 속도 0.5~10) ·
`whiteScale`(0.01~80, **클수록 어두워짐**) · `useExposureClamping` · `minEV` · `maxEV` ·
`minloglum` · `loglumrange`

**Phase 2 채도/색 캘리브레이션 표준 절차 (권장):**
```
/rtx/post/histogram/enabled       = false      ← 제일 먼저. 안 끄면 나머지가 무의미
/rtx/post/tonemap/op              = 6          (Aces)
/rtx/post/tonemap/colorMode       = 0 or 1     (sRGBLinear / ACEScg — A/B할 것)
/rtx/post/tonemap/filmIso         = 100
/rtx/post/tonemap/exposureTime    = 1/250 등 고정
/rtx/post/tonemap/fNumber         = 5.6 등 고정
/rtx/post/tonemap/cm2Factor       = 씬 단위 확인 (Isaac은 m 단위 → 기본값 검토 필요)
/rtx/post/colorcorr/enabled       = false      ← 캘리브레이션 중엔 꺼서 변수 제거
/rtx/post/colorgrad/enabled       = false
```
추가 색 파이프라인 키도 전부 존재 `[로컬검증]`:
`/rtx/post/colorcorr/{enabled,mode,outputMode,saturation,contrast,gamma,gain,offset}`
`/rtx/post/colorgrad/{enabled,mode,outputMode,blackpoint,whitepoint,lift,gain,gamma,contrast,multiply,offset}`
→ **채도(saturation)를 후처리로 직접 만질 수 있다.** 재질을 안 건드리고 전역 채도를 낮추는 저비용 레버.

### 6.4 설정 키를 로컬에서 열거하는 방법 (재현 가능한 레시피)

**A. 바이너리 문자열 추출 (GPU 불필요, 이 문서가 쓴 방법)** `[로컬검증]`
```bash
BASE=~/miniconda3/envs/env_isaaclab/lib/python3.10/site-packages/isaacsim/extscache
for f in $(find $BASE/omni.hydra.rtx-*/ $BASE/omni.gpu_foundation-*/ -name "*.so*"); do
  strings "$f" | grep -oE "/rtx/[A-Za-z0-9_/]*"
done | sort -u
```
→ 이 환경에서 **977개** 키. `/persistent/rtx/...` 도 같은 방법으로.

**B. UI 정의 소스가 사실상의 스키마다 (가장 신뢰도 높음 — 타입·범위·툴팁까지 나온다)** `[로컬검증]`
```
$BASE/omni.rtx.settings.core-0.6.3+d02c707b/omni/rtx/settings/core/widgets/
  ├─ post_widgets.py     톤매핑 / 자동노출 / 컬러코렉션
  ├─ common_widgets.py   지오메트리(TBN·subdivision·curves) / 재질(MDL displacement)
  ├─ rt_widgets.py       RT Real-Time 전용
  ├─ pt_widgets.py       Path Tracing 전용
  └─ rtpt_widgets.py     RTPT(실시간 PT) 전용
```
**이 5개 파일이 "실제 유효한 키" 목록의 사실상 정본이다.** 바이너리에만 있고 여기 없는 키는
내부/디버그용이거나 폐기 예정으로 봐야 한다.

**C. Replicator 문서 문자열** `[로컬검증]`
`$BASE/omni.replicator.core-1.11.35+106.5.0.lx64.r.cp310/omni/replicator/core/scripts/settings.py`
— 각 키의 **의미 설명이 docstring으로 들어 있다**(§5.2에서 인용한 fractionalCutoutOpacity 설명이 여기).

**D. 런타임(GPU 필요, 지금은 금지)**
`carb.settings.get_settings().get_settings_dictionary("/rtx")` → dict 전체 덤프.

### 6.5 Replicator 출력에도 적용되는가 — **`LdrColor` 예 / `HdrColor` 아니오**

`[웹검증]` 근거 3건 수렴:
1. Replicator 공식 문서: *"The **LdrColor** or rgb annotator produces the **low dynamic range** output
   image..."*, *"by default, LdrColor (RGB) is the **final rendered image** automatically created for each
   render product."* → 최종 post-process 결과 = **톤매핑·감마 적용됨**.
2. NVIDIA 스태프(rthaker): *"Isaac Sim uses the Omniverse Kit, which **by default applies a gamma
   correction of 2.2** to the final rendered images."* (sRGB, `colorTransform` 속성으로 해제 가능)
3. NVIDIA 스태프(Richard3D), HdrColor 색공간: *"It is **Rec.709**"* → **scene-linear Rec.709, 톤매핑 이전.**

**→ Phase 2 채도/색 캘리브레이션의 대상은 `LdrColor` 다.** 톤매핑·노출·컬러코렉션이 전부 여기에 반영된다.
**반대로 물리적으로 선형인 값이 필요하면 `HdrColor` 를 뽑아야 하며, 거기엔 톤매핑이 안 걸린다.**

`[추정(강)]` 단일 명시 문장("톤매핑이 annotator 출력에 적용된다")은 못 찾았고 위 3건의 수렴 결론이다.
**스파이크 확인**: 같은 씬을 `filmIso` 100 / 800으로 캡처해 픽셀값 비교(비용 거의 0). §10-3.

⚠️ **107+ 대비** `[웹검증]`: `omni.usd.schema.render_settings.rtx` 문서가 carb 전역 설정을
*"**deprecated** carb-global settings"* 로 지칭한다 — 렌더 설정이 carb 전역에서 **USD RenderSettings
프림으로 이동 중**이다. 106.5에는 영향 없으나 업그레이드 시 이 문서 전체를 재검증해야 한다.

---

## §7 우리 기존 조사에서 정정하는 것

### 7.1 **[정정 — 중요]** MDL displacement는 RTX에서 지원된다 (106.1부터, 우리 106.5 포함)

ZZ §2 상충4:
> | MDL displacement | G·F팀 | **RTX 미지원 명시**(NVIDIA 직원 공식 답변, D팀 인용) | **불가 — 정점 변위 메시로 우회** |

**틀렸다.** 공식 릴리스노트가 직접 반박한다.

`[웹검증]` **RTX Renderer 릴리스노트 Kit 106.1**:
> **"Added support for vertex displacement driven by MDL displacement functions.
> It is **disabled by default** due to impacts on scene load time."**

**Kit 106.1 Release Highlights** — 모드:
> "...support for rounded corners **and vertex displacement** driven by MDL functions
> **for both the RTX Real-Time and RTX Interactive (Path Tracing) modes**."

`[웹검증]` `/rtx/material/enableMDLDisplacement` — Bool, **default False**,
*"Requires stage reload to take effect."*

`[로컬검증]` 추가 근거:

1. **설정 키가 UI에 노출되어 있다** — `omni.rtx.settings.core/.../common_widgets.py:73`:
   ```python
   self._add_setting(SettingType.BOOL, "MDL displacement", "/rtx/material/enableMDLDisplacement",
       tooltip="Enable MDL material displacement. Enabling it can negatively impact stage load time
                when there are many materials with displacement support (like OmniSurface) in a stage.
                Requires stage reload to take effect.")
   ```
2. **번역기가 displacement 셰이더 코드를 생성한다** (`librtx.mdltranslator.plugin.so`):
   `geometry_displacement_standalone`, `generateDisplacementShaderCode failed %s`,
   `add_material failed for displacement of %s.`
3. **재질DB가 displacement PSO를 만든다** (`librtx.materialdb.plugin.so`):
   `geometry.displacement`, `enableMdlDisplacement`, `updateDisplacementProperties`,
   `: PSO: mdl displacement`, **`VertexDisplacement.comp.hlsl`**, `displaceVertices`
4. **씬DB에 GPU 변위 + DMM 하드웨어 경로가 있다** (`librtx.scenedb.plugin.so`):
   `SceneDb: GPU Displacement`, `Initialize MDL displacement`,
   `Shader Feature: Displaced Micro Meshes`, `allocateDisplacedMicromeshArray`,
   `TrianglesDisplacedMicromeshDesc`

**정확한 실태:**
- 구현 방식은 **컴퓨트 셰이더 기반 GPU 정점 변위**(`VertexDisplacement.comp.hlsl`) + 4090의 DMM.
  → **자동 테셀레이션은 안 한다.** 메시가 이미 조밀해야 의미가 있다.
  **즉 §3 catmullClark refinement와 조합해야 쓸 만하다.**
- **기본값 `False`** `[웹검증 확정]`. 그리고 **`Requires stage reload to take effect`** —
  켜고 나서 스테이지를 **다시 로드**해야 한다. **이 두 가지만으로 "안 되더라"의 대부분이 설명된다.**
- **RT·PT 양쪽 지원** `[웹검증]`.
- **결정적 제약: OmniPBR에는 displacement 입력이 아예 없다.** `[로컬검증]`
  `grep displacement OmniPBRBase.mdl OmniPBR.mdl` → **0건**.
  `mdl/OmniSurface/OmniSurfaceBase.mdl:416` 의 `geometry_displacement` 만 존재.
  → **OmniPBR로는 원리적으로 불가.** OmniSurface(무겁다) 또는 **커스텀 MDL에
  `material_geometry(displacement: ...)` 를 직접 노출**해야 한다.

**실무 판정 — 결론은 안 바뀌지만 이유가 바뀐다:**
"RTX 미지원이라 못 쓴다"(X) → **"지원되지만 (a) 설정 off + 스테이지 리로드 필요,
(b) OmniPBR에 입력이 없음, (c) 조밀 메시 선행 필요 — 3중 조건이라 정점 변위 메시가 여전히 저비용"**(O).
`NegObsGround.mdl` 에 displacement를 추가하는 선택지가 **새로 열렸다**는 점은 기록해 둘 가치가 있다.

### 7.2 **[정정]** `opacity_threshold=0.0` 의 의미

ZZ §10.2 "기본값 0.0이라 잎이 전부 불투명 판때기가 된다" → 원인 귀속이 틀렸다. §5.1 참조.
**진짜 1차 원인은 `enable_opacity=false`**, 그리고 **`opacity_mode=mono_average`** 라는
ZZ에 없던 4번째 함정이 있다.

### 7.3 **[보강]** `cameraFStop`/`cameraISO` 부재는 맞으나 결론이 다르다

§6.2 참조. 이름은 없지만 **`fNumber`** 로 존재한다. "노출 3요소 제어 가능"으로 상향.

### 7.4 **[정정 후보]** 카메라 ISP는 로컬에 존재한다

ZZ §2 상충4:
> | `omni.sensors.nv.camera` ISP | G팀 | **확장 자체가 없음**. common/lidar/radar/ultrasonic/materials만 존재 | **불가** |

**확장(extension)은 없는 게 맞다.** 그러나 `[로컬검증]`
`omni.hydra.rtx-1.0.0+d02c707b.lx64.r/bin/deps/**librtx.cameraisp.plugin.so**` 가 **존재하고**,
`config/extension.toml:62` 에 `[[native.plugin]] path = "bin/deps/rtx.cameraisp.plugin"` 로
**정식 로드된다.**
다만 이 플러그인에서 `/rtx/...` 설정 키를 추출하지 못했다 `[로컬검증, 부재]` →
**Python/USD API로 노출되지 않았을 가능성이 높다**(RTX 센서 내부 전용). `[추정]`
**판정은 "불가" 유지**, 단 근거를 *"확장이 없다"* → *"플러그인은 있으나 공개 API가 없다"* 로 정정.
5.x로 올릴 때 열릴 가능성이 있는 항목으로 표시.

### 7.5 **[유지·보강]** OmniPBR `project_uvw` 는 큐빅 투영이 맞다

ZZ §10.5 확인. `[로컬검증]` OmniPBR.mdl:275-292 의 파라미터명(`project_uvw`, `world_or_object`,
`uv_space_index`)과 그룹 구성이 트라이플래너 블렌딩용 가중치 파라미터를 전혀 갖고 있지 않다
(블렌드 지수/샤프니스 파라미터 부재) → 소프트 블렌딩이 아니다. **정정 불필요.**

---

## §8 NegObsGround.mdl 전역 기본 셰이더 승격 판정

`[로컬검증]` `/home/vislab/Desktop/work_sy/Practice_NegObs/assets/NegObsGround.mdl` (438행, v1.3.0) 전문 정독.

### 8.1 판정: **승격하면 안 된다.** 지면 전용으로 유지하라

이 MDL은 **월드 공간 트라이플래너 지면**이라는 단일 목적에 대해 매우 잘 만들어졌다. 그러나
그 설계가 곧 **범용 셰이더로서의 치명적 제약**이다.

### 8.2 OmniPBR 대비 없는 것 (전수)

| # | 부재 기능 | 심각도 | 무엇이 깨지나 | 우회책 |
|---|---|---|---|---|
| **G1** | **UV 파이프라인 자체가 없음** — `project_uvw`/`uv_space_index`/mesh UV 사용 경로 전무. **월드 트라이플래너 강제** (`negobs_sample_tri` 이 `state::position()` 을 월드 변환해 직접 사용, 161-166행) | **치명** | **UV가 author된 모든 에셋이 깨진다.** 나무 잎 아틀라스, 바위 베이크 텍스처, 표지판, 데칼, 계단 논슬립 스트립 — 전부 텍스처가 월드 격자로 재투영되어 **원래 아트가 소실**된다 | 없음. 이 셰이더는 UV 에셋에 쓸 수 없다 |
| **G2** | **`opacity` 전무** — `material_geometry()` 를 **인자 없이** 호출(437행) → `cutout_opacity=1.0` 고정 | **치명** | **잎·철망·펜스·그레이팅 전부 불가.** §5의 나무 임포트와 정면 충돌 | OmniPBR 병행 사용 (지면만 NegObsGround) |
| **G3** | **`round_edges_*` 전무** — 같은 437행. `material_geometry()` 기본값 normal = `state::normal()` | **치명(맥락상)** | **§1의 페이크 베벨을 이 셰이더에 걸 수 없다.** 계단 노즈·연석 모서리가 NegObsGround를 쓴다면 베벨 효과 상실 | MDL에 3파라미터 추가 + `material_geometry(normal: state::rounded_corner_normal(...))`. **약 6줄. 비용 최저, 효과 최대 — 우선 처리 권장** |
| **G4** | **`metallic` 전무** — BSDF가 `custom_curve_layer(diffuse base)` 고정(426-433행) | 중 | 금속 난간·맨홀·볼라드·표지판 지주가 전부 유전체로 보인다 | 금속은 OmniPBR로 |
| **G5** | **`emission` 전무** | 중 | 가로등·신호등·차량 라이트·창문 야간광 불가 | OmniPBR/OmniEmissive |
| **G6** | **AO / ORM 텍스처 전무** (`ao_texture`, `ao_to_diffuse`, `enable_ORM_texture`, `ORM_texture`) | 중 | ORM 팩킹된 시판 에셋(ambientCG/PolyHaven 다수)을 **텍스처 3장으로 분해**해야 한다 | 임포트 시 채널 분리 전처리 |
| **G7** | **detail normal 전무** (`detail_normalmap_texture`, `detail_bump_factor`) | 중 | ZZ가 "즉시 사용 가능"이라 판정한 마이크로 디테일 레버가 **이 셰이더에서만 사라진다** | triplanar 샘플에 detail 레이어 추가 가능하나 **텍스처 페치가 또 2배** (§8.3) |
| **G8** | **clearcoat 전무** | 하 | 젖은 아스팔트/차체 광택 표현 저하 | roughness 노이즈로 근사(이미 `rough_noise` 있음) |
| **G9** | **albedo 보정 파라미터 전무** (`albedo_desaturation`/`albedo_add`/`albedo_brightness`/`diffuse_tint`) | 중 | **Phase 2 채도 캘리브레이션의 주 레버가 없다.** 단 `macro_amp`/`desat_bright` 로 부분 대체됨 | `diffuse_tint` 상당 파라미터 1개 추가 권장(간단) |
| **G10** | **`diffuse_color_constant` 없음** — 텍스처 없으면 `base::file_texture` 무효 lookup | 중 | **텍스처를 안 준 프림은 검게(또는 미정의) 나온다.** OmniPBR은 상수 색으로 폴백 | 상수색 폴백 파라미터 추가 |
| **G11** | **`geometry_normal_roughness_strength` 없음** (노멀맵 유발 roughness) | 하 | 원거리 스페큘러 에일리어싱 | 무시 가능 |
| **G12** | **`enable_opacity`/`emission` 부재로 재질 그룹 UI가 다름** | 하 | 기존 파이프라인 코드가 `inputs:diffuse_texture` 등 OmniPBR 이름을 가정하면 전부 수정 | 파라미터 리네임 매핑 |
| **G13** | **primvar 의존** — `scene::data_lookup_float("blend_tw"/"blend_wb")` (396-397행) | 중 | 해당 primvar가 없는 프림에서는 `blend_default` 로 폴백하므로 크래시는 안 나나, **`use_blend=true` 재질을 primvar 없는 프림에 걸면 조용히 A만 나온다** | `use_blend=false` 기본값 유지 |
| **G14** | **`anno::in_group` 부재** — 파라미터 대부분에 그룹/표시명 어노테이션이 없다 | 하 | Kit 재질 UI에서 파라미터가 **한 덩어리로 평면 나열**되어 사용성 저하 | 어노테이션 추가(순수 노동) |

### 8.3 성능 — 텍스처 페치 비용 실측 계산 `[로컬검증, 코드 카운트]`

호출 트리를 코드에서 직접 세었다:

```
negobs_layer (1회)
 └ negobs_sample_tri × 2            (s1 원본, s2 +90° 회전 패치 — 259-267행)
    └ negobs_sample_basis × 2       (기저0 axis-aligned + 기저1 Z45° — 195-208행)
       └ base::file_texture × 3     (albedo, uvw_x/y/z — 105-107행)
       └ tex::lookup_float3 × 3     (roughness — 110-118행)
       └ tangent_space_normal_texture × 3  (normal — 121-132행, 각각 내부 텍스처 페치)
```

| 구성 | albedo | roughness | normal | **텍스처 페치 합계** |
|---|---|---|---|---|
| 1 레이어 (`use_blend=false`) | 12 | 12 | 12 | **36** |
| 2 레이어 (`use_blend=true`, 경계 대역) | 24 | 24 | 24 | **72** |

비교: **OmniPBR은 albedo/roughness/normal 각 1회 = 3회.**
→ **NegObsGround는 OmniPBR의 12배(단일) / 24배(블렌드) 텍스처 대역폭을 쓴다.**

`perlin_noise_texture` 호출 수 (`negobs_noise`, 36-52행. `noise_levels=2` = 2옥타브 3D Perlin):

| 위치 | 호출 |
|---|---|
| `negobs_sample_tri` 내 d1/d2/d3 + sel | 4 × (sample_tri 2회) = **8** |
| `negobs_layer` 내 patch_m/macro/sat_m/rn | **4** |
| **레이어당 소계** | **12** |
| 2 레이어 | 24 |
| `blend_edge_noise` (401행) | 1 |
| **블렌드 재질 총계** | **25 호출 = 약 50 옥타브** |

**`base::perlin_noise_texture` 는 절차적(procedural) 노이즈라 텍스처 페치가 아니라 ALU 비용**이며,
MDL에서 `noinline` 취급되기 쉬워 인라인 최적화가 잘 안 된다. `[추정]`
**RTX 실시간(RT) 모드에서 픽셀당 50 옥타브 3D Perlin은 무겁다.**
PT에서는 경로당 재평가되므로 더 나쁘다.

**완화 가능 지점** (코드 구조상 확실한 것만):
- `patch_mix` 가 **호출부에서 상수 1.0으로 고정**되어 있다(380·388행) → `s2`(두 번째 회전 샘플)를
  **끌 수 있는 스위치가 없다.** `patch_mix=0` 을 uniform 파라미터로 노출하면 **텍스처 페치가 절반**이 된다.
  **원거리/배경 프림용 경량 변종을 만들 때 첫 번째 손잡이.**
- `tri_dither=0` 이면 d1/d2/d3 노이즈 3개가 상수로 접힐 여지가 있다(uniform 곱). `[추정]`
- 기저1(Z45° 보조 기저)을 끄는 uniform 스위치를 두면 또 절반. 지면 경사가 완만한 씬에서는 손실이 작다.
- `use_blend=false` 는 uniform이므로 **컴파일 타임에 B 레이어 전체가 접힌다** `[로컬검증]`
  (394-410행 전부 `use_blend ? ... : ...`) → 순수 영역 재질은 이미 36 페치. **OK.**

### 8.4 권고 — 승격 대신 3단 재질 정책

| 티어 | 셰이더 | 대상 |
|---|---|---|
| **T1 지면·대형 지형면** | **NegObsGround.mdl** (+§8.5 개선) | 흙·풀·자갈·아스팔트 지면, 옹벽 경사면. UV가 없고 타일 반복이 문제인 표면 |
| **T2 일반 구조물·소품** | **OmniPBR** | 계단·연석·난간·볼라드·표지판·건물·차량. **UV·opacity·metallic·emission·round_edges가 필요한 전부** |
| **T3 식생** | **OmniPBR** (컷아웃 §5.3) | 나무·관목·잎 카드 |

**이유 한 줄:** NegObsGround의 강점(트라이플래너 + 반복 파괴)은 **UV가 없는 큰 면**에서만 의미가 있고,
바로 그 설계가 **UV가 있는 모든 것을 부순다.**

### 8.5 NegObsGround.mdl 개선 우선순위 (승격이 아니라 보강)

| 순위 | 작업 | 분량 | 근거 |
|---|---|---|---|
| **1** | **`round_edges_*` 3파라미터 추가** → `material_geometry(normal: state::rounded_corner_normal(...))` | 약 8줄 | §1이 실증되면 지면-연석 접합부에도 필요. **비용 대비 효과 최대** |
| **2** | **`patch_mix` / 보조기저를 uniform 스위치로 노출** | 약 10줄 | §8.3 — 텍스처 페치 최대 4배 절감. 원거리 LOD 변종 확보 |
| **3** | **`diffuse_color_constant` 폴백 + `diffuse_tint`** 추가 | 약 10줄 | G9·G10. Phase 2 색 캘리브레이션 레버 |
| **4** | `cutout_opacity` 파라미터 추가 | 약 6줄 | 지면에 물웅덩이 마스크/식생 데칼을 얹을 때 |
| **5** | `geometry_displacement` 노출 (§7.1이 실증되면) | 약 6줄 | MDL displacement가 실제로 되면 지면 미세 요철을 메시 없이 |
| **6** | `anno::in_group`/`display_name` 정비 | 노동 | UI 사용성 |

**1·2번은 스파이크 결과와 무관하게 지금 해도 손해가 없다.**

---

## §9 막힌 것 / 확정하지 못한 것

**해결된 것 (조사 중 닫힘):**
- ~~RT vs PT round edges 차이~~ → **양쪽 지원 확정** (§1.4, 106.1 Release Highlights 직접 인용)
- ~~`normals` 부재 시 flat/smooth~~ → **폴백은 smooth** (§4.2). 단 USD 사양은 faceted라 하고
  NVIDIA도 "예측 불가"라 경고 → **직접 author가 정답**
- ~~Replicator 출력에 톤매핑 적용 여부~~ → **`LdrColor` 적용 / `HdrColor` 선형 Rec.709** (§6.5)
- ~~f-stop 키 철자, `histogram/enabled` 존재~~ → **로컬 소스로 확정** (§6.2)
- ~~MDL displacement 지원 여부~~ → **106.1부터 지원, 기본 off** (§7.1)

**남은 것:**
1. **`mdlRoundedCornerNormal` 의 함수 본체.** RTX 셰이더 라이브러리가 사전컴파일 SPIR-V라 ASCII로
   안 잡힌다(셰이더 캐시 3종 전수 grep 히트 0). "존재하는 스텁"일 가능성을 **문자열만으로는** 0으로
   못 만든다. **다만 공식 릴리스노트가 지원을 명시하므로 실질 위험은 낮다.**
   → 최종 판정은 감독의 스파이크 렌더. (§2 감별표)
2. **RTX Real-Time 2.0**(106.5 프리뷰 모드)에서의 round edges / displacement 지원 여부 — 문서 언급 전무.
   그 모드를 쓸 계획이면 별도 확인.
3. **RTX 렌더 델리게이트가 crease/corner를 존중한다는 직접 진술** — 못 찾았다.
   로컬에 OpenSubdiv `Sdc::Crease::*` 심볼과 `PxOsdSubdivTags` 가 링크되어 있어 **[로컬검증]으로는
   강하나**, 공식 문서 문장은 없다. `interpolateBoundary`/`faceVaryingLinearInterpolation`/
   `triangleSubdivisionRule` 존중 여부도 미확인.
4. **`fractionalCutoutOpacity=true(기본)` 상태에서 α의 정확한 처리 곡선** — PT는 stochastic이라고
   문서화됐으나 RT는 미상세. → `opacity_threshold` 를 MDL에서 명시하면 이 변수 자체가 제거된다.
5. **각 `/rtx/*` 키의 기본값(default) 전량.** 일부는 웹으로 확정했으나(refinementLevel=0,
   adaptiveRefinement=False, enableMDLDisplacement=False, pathtracing/fractionalCutoutOpacity=True),
   나머지는 렌더러 C++ 안에 있고 **디스크의 어떤 `.toml`/`.kit` 에도 없다**(Isaac `.kit` 의 rtx 설정은
   `mdlMaterialWarmup`/`dlss.execMode`/`dlssg.enabled` 3개뿐).
   → GPU 세션에서 `carb.settings` 덤프 1회면 전부 해결. **§10-1.**
6. **컷아웃이 그림자 광선에서 존중된다는 명시 문서** — 정황 3건(전용 키 존재, any-hit 문서,
   `onlyOpaqueRayFlags`)으로만 추론 `[추정(강)]`.
7. **알파 재질이 depth annotator를 오염시킨다는 공식 문서** — 없다. 세그멘테이션 오염은 공식 확인,
   depth는 PT stochastic sampling 서술로부터의 연역 `[추정(강)]`.
8. **OMM(Opacity Micro-Map)** — 로컬 부재 + 웹 부재 **양방향 확인**이라 초기보다 확신이 높다.
   그래도 "부재의 증명"은 약한 증명 `[추정]`.

**증거 우선순위 원칙 (이 문서 전반에 적용):**
> ① 설치본 MDL 소스 / 바이너리 → ② 공식 릴리스노트 → ③ 공식 설정·Asset Requirement 문서 →
> ④ NVIDIA 스태프 포럼 답변 → ⑤ 파라미터 레퍼런스 페이지(**체계적으로 뒤처짐 — §1.5**) →
> ⑥ 커뮤니티/AI 생성 문서(**오류 확인됨 — §6.2 경고**)
> 상충 시 낮은 번호가 이긴다. 실제로 §1.5(문서 누락)와 §3.3(adaptive 문서 vs 바이너리)에서
> 이 원칙이 결론을 갈랐다.

---

## §10 감독을 위한 스파이크 추가 요청 (비용 거의 0)

지금 GPU를 쥐고 계신 김에 **1줄~1컷짜리로 끝나는데 이 문서의 불확실성을 크게 줄이는 것들**:

1. **`carb.settings.get_settings().get_settings_dictionary("/rtx")` 를 JSON으로 1회 덤프.**
   (또는 스냅샷이 안전한 `create_dictionary_from_settings("/rtx")`)
   → §9-5 해결. **이후 모든 설정 논쟁이 끝난다. 1순위.**
2. **round edges A/B를 RT와 PT 각각 1컷씩** (총 4컷: {RT,PT} × {radius 0, 0.02}).
   §1.3의 "가장 유리한 조건"으로. → §2 감별표에서 즉시 판정.
3. **`filmIso` 100 / 800 으로 Replicator `LdrColor` 캡처 2장** — 단 **먼저
   `/rtx/post/histogram/enabled = False`** 로 자동노출을 끌 것(안 끄면 둘이 같게 나온다).
4. **`/rtx/debug/onlyOpaqueRayFlags = true` 로 나무 1컷.** → 알파 경로 진입 여부 즉답(§5.3).
5. **subdivision:** 큐브 1개에 `subdivisionScheme="catmullClark"` + 프림 override
   `refinementEnableOverride=true, refinementLevel=3`, 와이어프레임 1컷.
   → §3 전체가 1컷으로 확정된다. crease를 하나 넣으면 §9-3도 같이 닫힌다.
6. **세그멘테이션 GT 검증 (신규 — 우선순위 상)**: 잎 카드 1장을
   `opacity_threshold=0` / `0.5` 두 조건으로 RGB + semantic 캡처.
   → §5.2b의 "α<1 픽셀이 마스크에서 빠진다"를 우리 파이프라인에서 직접 확인.
   **이게 사실이면 기존에 생성한 식생 포함 데이터의 라벨을 재검토해야 한다.**
7. **지형 생성 코드 점검(GPU 불필요)**: 우리 메시에 `subdivisionScheme` 이 명시 author되어 있는지.
   미기재면 USD 기본값이 catmullClark이라 **author한 `normals` 가 무시된다**(§4.3 3번째 함정).
