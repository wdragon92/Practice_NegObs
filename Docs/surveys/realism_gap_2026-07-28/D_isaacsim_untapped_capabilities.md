# D. Isaac Sim 미활용 역량 전수 조사 — "현 스택 유지 시 도달 가능한 천장"

- 작성: 2026-07-28
- 대상 런타임: **Isaac Sim 4.5.0.0 (pip) / Omniverse Kit 106.5.0.162521**, conda env `env_isaaclab`
- 조사 방법: (a) 로컬 설치본 전수 검사 (b) 공식 문서 WebFetch (c) 프로젝트 자체 렌더 로그 실측
- 표기 규약:
  - **[로컬검증]** — 이 머신의 4.5.0 설치본에서 파일/문자열/심볼을 직접 확인. 절대경로 병기.
  - **[웹검증]** — 공식 문서/포럼에서 확인. URL 병기.
  - **[실측]** — 프로젝트 자체 산출물의 타임스탬프/로그에서 계산.
  - **[추정]** — 위 근거로부터의 추론. 반드시 검증 필요.
  - **[미검증]** — 설정 키/API의 *존재*는 확인했으나 실제 동작은 확인 못 함.

---

## §0. 조사 전제 — 우리 런타임의 정확한 좌표

| 항목 | 값 | 근거 |
|---|---|---|
| Isaac Sim | `4.5.0-rc.36+release.19112.f59b3005` | **[로컬검증]** `…/site-packages/isaacsim/VERSION` |
| Kit | `omniverse_kit-106.5.0.162521` | **[로컬검증]** `…/site-packages/omniverse_kit-106.5.0.162521.dist-info` |
| Replicator | `omni.replicator.core-1.11.35+106.5.0` | **[로컬검증]** `…/isaacsim/extscache/omni.replicator.core-1.11.35+106.5.0.lx64.r.cp310` |
| Python | 3.10 (conda `env_isaaclab`) | **[로컬검증]** |
| 실행 경로 | conda site-packages (standalone `/media/vislab/ssd1_4tb1/isaac/isaacsim_test` 은 **동일 빌드**의 별도 사본, 미사용) | **[로컬검증]** `run_v5_keep_pt.sh` 가 `conda activate env_isaaclab` |

> **버전 주의**: Isaac Sim 5.0 이상 문서에는 `RealTimePathTracing`(RTX Real-Time 2.0), `MinimalRendering`
> 렌더 모드와 `/rtx/minimal/*` 설정이 등장하지만, **우리 4.5.0 에는 없다**.
> `simulation_app.py` 가 인식하는 값은 `RaytracedLighting` / `PathTracing` 2종뿐이다.
> **[로컬검증]** `…/isaacsim/exts/isaacsim.simulation_app/isaacsim/simulation_app/simulation_app.py:451-456`
> 아래 문서의 모든 API·설정 키는 4.5.0 기준으로만 검증했다.

### 현재 우리가 쓰고 있는 API의 전부

`scene_common.py` 전수 확인 결과 사용 중인 Isaac/USD API는 다음이 **전부**다:

- 부팅: `SimulationApp({"headless":…, "width":1920, "height":1080})` — **나머지 20여 개 config 키 전부 기본값**
- carb 설정: `/rtx/post/dlss/execMode=2`, `/rtx/post/aa/op=3`, 뷰포트 그리드 4개 — **RTX 설정 567개 중 2개 사용**
- 지오메트리: `UsdGeom.Cube` / `Cylinder` / `Sphere` — **`UsdGeom.Mesh` 0건, `PointInstancer` 0건**
- 재질: `OmniPBR.mdl` 단일 — 입력 16종 사용 (**OmniPBR 전체 입력의 약 1/4, Base MDL 18개 중 1개**)
- 조명: `UsdLux.DomeLight`(HDRI) + `UsdLux.DistantLight` — **2종. Sphere/Rect/Disk/Cylinder/IES/shaping 0건**
- 카메라: 뷰포트 카메라 위치만 조작 — **`focalLength`/`fStop`/`focusDistance`/`horizontalAperture` 0건**
- 캡처: `omni.kit.viewport.utility.capture_viewport_to_file` + 수동 `sim_app.update()` 루프
  — **Replicator(`omni.replicator.core`) 0건, annotator 0건, writer 0건**

---

## §1. 결론 요약 — 현 스택 유지 시 도달 가능한 천장

### 1-1. 한 줄 결론

> **"장난감 수준"의 원인은 Isaac Sim 의 한계가 아니라, Isaac Sim 의 약 10% 만 쓰고 있기 때문이다.
> 렌더러 교체·상용 에셋 구매 없이, 현 스택(Isaac Sim 4.5 + Python USD 스크립트)만으로
> 선행 연구급 사실성에 도달할 수 있다. 다만 그 경로는 "설정을 조금 더 켜는" 것이 아니라
> **지오메트리 표현을 프리미티브에서 Mesh/PointInstancer 로 바꾸고, 에셋을 외부에서 들여오고,
> 캡처를 Replicator 로 이관하는** 3개의 구조 변경이다.**

### 1-2. 천장의 위치 (평가)

| 축 | 현재 | 현 스택 천장 | 병목 |
|---|---|---|---|
| 재질 | OmniPBR 3맵 | OmniSurface(SSS)+ClearCoat+Opacity cutout+데칼+커스텀 MDL | **없음 — 순수 미사용** |
| 조명·하늘 | HDRI 2종 + 수동 태양 캡 | NVIDIA 물리 하늘(위경도/절기/시각 구동) + 구름 6종 + 대기 산란/포그 | **없음 — 순수 미사용** |
| 카메라·센서 | 기본 핀홀, 포스트 0 | 물리 렌즈(fStop/focus) + DoF + 모션블러 + 비네팅/그레인/수차/블룸 | **없음 — 순수 미사용** |
| 지오메트리 | 프리미티브 ~10² prim | Mesh + subdiv + PointInstancer 10⁵~10⁷ 인스턴스 | **코드 재작성 필요(중)** |
| 에셋 | 외부 0건 | NVIDIA 무료 12,689개 + CC0 외부 | **파이프라인 신설 필요(중)** |
| 변위(displacement) | 없음 | **미확정** — 설정 키·MDL 배선은 존재, 실동작 미검증 | **30분 실험으로 확정 (§2-4)** |
| GT·대량생성 | 없음 | Replicator annotator + writer | **신설 필요(중)** |
| 처리량 | PT 14 s/컷 | RT 0.4 s/컷 ~ PT 64spp 0.9 s/컷 | **물리적 한계 (§8)** |

**즉 8개 축 중 6개는 "못 하는" 게 아니라 "안 한" 것이다.**
확정된 엔진 한계는 **POM(시차 매핑) 부재**와 **정적 씬 모션블러 불가** 둘뿐이고,
변위는 미확정이며 어느 쪽이든 대체 경로(실지오메트리 하이트필드 + subdivision)가 있다.

### 1-3. 가장 중요한 6가지 발견

1. **NVIDIA 가 무료 에셋 281 GB 를 인증 없는 평문 HTTPS 로 공개하고 있고, 우리는 0개를 쓰고 있다.**
   Nucleus 도 Omniverse Launcher 도 계정도 필요 없다. `curl` 로 바로 받아진다.
   Isaac 카탈로그 12,689개(볼라드·안전난간·벤치·가로등 40종·쓰레기통·화단·표지판 493종·
   보행자 20종+의상변형 220+애니메이션 24·**잔디 타일 지오메트리**·연석/노면 재질) —
   그리고 **`Assets/Vegetation/` 에 나무 44종·관목 37종·잎 클러스터 5·낙엽 5·바위 15**.
   (§4-1, §4-1b, **[로컬검증]+[웹검증: HTTP 200 직접 확인]**)

2. **"구 3개 나무" 문제는 이미 풀려 있었다.**
   `Japanese_Cherry`(벚나무), `Japanese_Maple`(단풍), `Forsythia`(개나리), `Boxwood`(회양목) —
   **한국 도시 조경 대표종이 그대로 있고, 계절 변종(`_Fall`)이 8종 이상**이다.
   35 MB 짜리 실메시 트리다(빌보드 아님). 다만 **알파 컷아웃 설정(§4-3b)을 놓치면
   잎이 전부 불투명 판때기로 렌더링된다** — 이게 첫 실험에서 확인할 1번 항목이다.

3. **`ensure_noon_lookfix()` 의 numpy HDRI 수술은 불필요했을 가능성이 높다.**
   정식 해법은 `/rtx/domeLight/upperLowerStrategy = 0`(고주파 IBL 정확 샘플링)이고,
   더 나아가 NVIDIA 는 **위경도·절기·시각으로 태양을 배치하고 구름·헤이즈·대기포그를
   파라미터로 주는 물리 하늘(ProceduralSky MDL)** 을 6종 프리셋으로 공개하고 있다.
   Hosek-Wilkie 하늘 MDL 은 **로컬에 이미 설치돼 있다**. (§6-1, §6-2)

4. **우리 PT 워밍업 572회 루프는 약 70배 낭비다.**
   `/rtx/pathtracing/spp` 기본값이 **1** 이라 512 spp 를 512 프레임에 걸쳐 누적하고 있었다.
   `spp=16, totalSpp=64, rt_subframes=8` 로 바꾸면 **8 프레임**이면 된다.
   NVIDIA 공식 권고도 "Replicator + PT 에서는 totalSpp 를 16 정도로 낮추라"이다. (§8-0)

5. **PT 512spp 는 데이터셋 설정이 아니라 논문 그림 설정이다.**
   실측 13.99 s/컷 → 2만 장에 **70시간**. RT 는 1.12 s/컷(워밍업 90→32 면 ~0.4 s)
   → 2만 장에 **1.3~2.5시간**. 그리고 NVIDIA 공식 벤치마크가 말하는 더 중요한 사실:
   **annotator 를 전부 켜면 처리량이 40배 붕괴하고 그 값은 GPU 와 무관하다.**
   → RGB+depth+semantic+camera_params 4개만 켤 것. (§9)

6. **GT 낙차 맵은 렌더러로 못 만든다 — 그리고 그게 오히려 낫다.**
   "보이지 않는 낙차"는 정의상 어떤 render pass 에도 안 나온다. 게다가 **4.5 의 직교 카메라는
   조용히 틀린 값을 내므로** 탑다운 직교 depth 계획은 폐기해야 한다.
   대신 **PhysX 하향 레이캐스트로 씬당 1회 2.5D 높이장을 굽고, 프레임마다
   `distance_to_camera` + `camera_params` 로 픽셀을 역투영해 조회**하면 된다.
   씬당 1회만 비싸고, 연속값 라벨이며, §2-4 의 Mesh 하이트필드 지형과 데이터를 공유한다. (§8-5)

---

## §2. 지오메트리 고도화

### 2-1. USD Mesh 직접 생성 — 가능, 비용 낮음

**[로컬검증]** `pxr.UsdGeom.Mesh` 는 표준 USD 스키마이며 Isaac Sim 4.5 RTX 가 지원한다.
RTX 렌더러 지원 지오메트리는 공식적으로 **"Triangle Meshes, Subdivision Surfaces (OpenSubdiv),
Basis Curves, Points"**. **[웹검증]** https://docs.omniverse.nvidia.com/materials-and-rendering/latest/rtx-renderer.html

우리가 `UsdGeom.Cube` 만 쓰는 것의 실질적 손해는 4가지다:

1. **UV 를 만들 수 없다** → 그래서 월드 트라이플래너 투영에 갇혀 있다. 계단 노징·난간 같은
   곡면/경사면에서 투영 이음매가 생기고, 텍스처가 물체를 "감싸지" 못한다.
2. **정점 컬러/마스크를 만들 수 없다** → 재질 블렌딩(젖음·이끼·마모 그라데이션) 불가.
3. **베벨/챔퍼가 불가능하다** → 모든 모서리가 수학적으로 완벽히 날카롭다. 이것이
   "게임 같다"는 인상의 가장 큰 단일 원인이다(§2-3).
4. **데칼을 붙일 수 없다** → Replicator 의 `create_mesh_decal()` 이 `UsdGeom.Mesh(prim)` 를
   요구한다. **[로컬검증]** `…/omni/replicator/core/scripts/utils/mesh_decal.py:295-297`

최소 코드 경로:

```python
from pxr import UsdGeom, Vt, Gf
mesh = UsdGeom.Mesh.Define(stage, "/World/Step_00")
mesh.CreatePointsAttr(Vt.Vec3fArray([...]))              # 정점
mesh.CreateFaceVertexCountsAttr(Vt.IntArray([4,4,...]))  # 면당 정점 수
mesh.CreateFaceVertexIndicesAttr(Vt.IntArray([...]))
mesh.CreateExtentAttr(...)                                # 필수 (없으면 컬링 오작동)
# UV
pv = UsdGeom.PrimvarsAPI(mesh).CreatePrimvar(
        "st", Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.faceVarying)
pv.Set(Vt.Vec2fArray([...]))
# 정점 컬러 (재질 마스크로 활용)
UsdGeom.PrimvarsAPI(mesh).CreatePrimvar(
        "displayColor", Sdf.ValueTypeNames.Color3fArray, UsdGeom.Tokens.vertex).Set([...])
mesh.CreateSubdivisionSchemeAttr(UsdGeom.Tokens.none)     # 명시 권장 (기본은 catmullClark!)
```

> **함정 [로컬검증 아님, USD 스펙]**: `UsdGeom.Mesh` 의 `subdivisionScheme` **기본값은
> `catmullClark`** 이다. 명시하지 않으면 RTX 가 우리 각진 계단을 둥글게 만들 수 있다.
> 각지게 두려면 `none`, 부드럽게 하려면 `catmullClark` + refinementLevel(아래).

### 2-2. Subdivision Surface — **지원됨. 우리는 끄고 쓰는 중**

**[로컬검증]** `simulation_app.py` 의 런처 config 에 `"subdiv_refinement_level": 0` 이 있고,
이는 carb 설정 `/rtx/hydra/subdivision/refinementLevel` 로 매핑된다.
`…/isaacsim/exts/isaacsim.simulation_app/isaacsim/simulation_app/simulation_app.py:70, 478`

```python
# 전역 (부팅 시)
sim_app = SimulationApp({"headless": True, "width":1920, "height":1080,
                         "subdiv_refinement_level": 2})
# 또는 런타임
carb.settings.get_settings().set("/rtx/hydra/subdivision/refinementLevel", 2)
```

**[로컬검증]** 프림 단위 오버라이드도 있다 — Kit 테스트 USD 에서 확인:
```
custom bool refinementEnableOverride = 1
custom int  refinementLevel = 2
```
(`…/extscache/omni.kit.property.usd-4.2.16+d02c707b/data/tests/usd/sphere.usda:17-18`)

```python
prim.CreateAttribute("refinementEnableOverride", Sdf.ValueTypeNames.Bool).Set(True)
prim.CreateAttribute("refinementLevel", Sdf.ValueTypeNames.Int).Set(2)
```

**[웹검증]** Kit 106.4 에서 "subdivision refinement 결과를 캐시하여 씬 로드 시간 단축",
Kit 106.1 에서 "스켈레탈 디포메이션 메시의 subdivision 지원 추가" — 즉 106.x 계열에서
subdivision 은 활발히 지원·개선되는 기능이다.
https://docs.omniverse.nvidia.com/dev-guide/latest/release-notes/106_4.html

- **사실성 기여**: 중~상. 프리미티브의 완벽한 직각 모서리를 없애는 가장 저렴한 방법.
- **도입 비용**: 낮음 (전역 설정 1줄) ~ 중 (Mesh 로 전환 후 crease 지정).
- **리스크**: refinementLevel 을 전역으로 올리면 **폴리곤이 4^level 배**로 늘어 계단·박스가
  둥글어지고 메모리·로드시간이 늘어난다. **프림 단위 오버라이드를 권장**한다.

### 2-3. 베벨/챔퍼 — 실용적 방법 4가지

Isaac Sim 에는 "베벨 모디파이어"가 없다. 현실적 선택지:

| 방법 | 사실성 | 비용 | 비고 |
|---|---|---|---|
| **(A) 절차적 Mesh 생성 시 모서리에 챔퍼 링 추가** | 상 | 중 | 계단 노징·연석·난간에 3~5 mm 챔퍼. 우리 빌더가 이미 수학적으로 좌표를 계산하므로 확장 가능 |
| **(B) subdivisionScheme=catmullClark + creaseSharpness** | 상 | 중 | `CreateCornerIndicesAttr`/`CreateCreaseSharpnessesAttr` 로 "어디를 날카롭게 둘지" 지정. 나머지가 자연스럽게 둥글어짐 |
| **(C) 별도 얇은 챔퍼 프림 덧대기** | 중 | 낮 | 계단 코 부분에 반경 3 mm 실린더. 우리 `build_nosing()` 이 이미 유사한 일을 함 |
| **(D) Blender 에서 베벨 후 USD 익스포트** | 최상 | 중~상 | 절차성 상실. 변주 씬에 부적합 |

> **[추정]** 우리 씬에서 사실성 대비 비용이 가장 좋은 것은 **(C)+(A) 조합**이다.
> 특히 **계단 노징(코)의 3~5 mm 챔퍼 + 미세 마모**는 실사진과 렌더를 구별하는
> 가장 두드러진 단서인데, 우리 낙차 연구에서 계단 모서리는 **라벨이 걸리는 바로 그 위치**다.

USD crease API:
```python
mesh.CreateSubdivisionSchemeAttr(UsdGeom.Tokens.catmullClark)
mesh.CreateCreaseIndicesAttr(Vt.IntArray([...]))       # 날카롭게 유지할 엣지 체인
mesh.CreateCreaseLengthsAttr(Vt.IntArray([...]))
mesh.CreateCreaseSharpnessesAttr(Vt.FloatArray([...])) # 10 = 완전 날카로움, 2~4 = 챔퍼 느낌
```
**[미검증]** — crease 속성이 RTX Hydra 에서 실제로 반영되는지는 이 머신에서 렌더 확인하지 않았다.
OpenSubdiv 표준 기능이고 RTX 가 OpenSubdiv 를 쓴다고 문서화돼 있으므로 **[추정] 동작할 것**.

### 2-4. 변위(Displacement) / 테셀레이션 — **판정 보류. 30분 실험으로 확정할 것**

**[웹검증]** NVIDIA 직원(VickNV) 공식 답변, 2024-09-29:
> "RTX in Isaac Sim does not currently support displacement, regardless of MDL capabilities.
> Displacement support for RTX is in development and will be implemented in a future release."

https://forums.developer.nvidia.com/t/bug-isaac-sim-render-does-not-listen-to-mdl-material-geometry-displacement/305411

**[로컬검증]** 그러나 4.5.0 에는 반증 증거가 3개 있다. 위 답변은 **Isaac Sim 4.1 시점**이다.

1. `/rtx/material/enableMDLDisplacement` 설정이 **툴팁까지 붙어 존재**한다:
   > "Enable MDL material displacement. Enabling it can negatively impact stage load time when
   >  there are many materials with displacement support (**like OmniSurface**) in a stage.
   >  Requires stage reload."
   (`…/extscache/omni.rtx.settings.core-0.6.3+d02c707b/omni/rtx/settings/core/widgets/common_widgets.py:73`)
2. `OmniSurfaceBase.mdl:876-877` 이 실제로 `material_geometry(displacement: geometry_displacement, …)`
   로 MDL `geometry.displacement` 에 **연결돼 있다.**
3. `OmniSurface.mdl` 에 변위 입력 5개가 노출돼 있다:
   `geometry_displacement`, `geometry_displacement_mode`(0=Height / 1=Vector-tangent / 2=Vector-object),
   `geometry_displacement_image`, `geometry_displacement_scale`, `geometry_displacement_scalar_zero_value`

```python
carb.settings.get_settings().set("/rtx/material/enableMDLDisplacement", True)  # 스테이지 리로드 필요
carb.settings.get_settings().set("/rtx/hydra/subdivision/refinementLevel", 3)  # 테셀레이션 공급
# 재질: OmniSurface + geometry_displacement_image + geometry_displacement_scale
# 대상: UsdGeom.Mesh (subdivisionScheme=catmullClark) — 프리미티브 Cube 는 안 될 가능성 높음 [추정]
```

> **판정: [미검증] — 30분짜리 실험 1회로 확정할 것 (§11 P0-3).**
> 되면 지면 요철·마모·침하 표현의 판이 바뀌고, 안 되면 아래 대체 경로로 간다.
> 어느 쪽이든 §3-3·§11 의 다른 항목보다 우선순위가 높지는 않다.

**대체 경로 (권장)**:
- **지면 요철·침하·웅덩이** → 실제 Mesh 정점을 노이즈로 변위시켜 굽는다(bake).
  우리는 절차 생성이므로 numpy 로 하이트필드 만들어 `UsdGeom.Mesh` 정점에 그대로 넣으면 된다.
  이게 displacement 보다 오히려 낫다: GT 낙차 맵 계산에도 같은 하이트필드를 재사용할 수 있다.
- **자갈·거친 표면** → PointInstancer 로 실제 자갈 인스턴스(§2-5).
- **미세 요철** → 노멀맵 + detail 노멀 (§3).

**RTX 미지원 확정 목록** (사실성 논의에서 아예 빼야 하는 것):
- **POM(시차 폐색 매핑)** — `AperturePBR_*.mdl`(RTX Remix 재질)이 **Isaac Sim 4.5 에 미탑재** **[로컬검증]**

> **대체 경로가 오히려 나은 이유**: 우리는 절차 생성이라 하이트필드를 numpy 로 만들 수 있고,
> **같은 하이트필드를 §8-5 의 GT 낙차 맵 계산에 그대로 재사용할 수 있다.**
> displacement 는 렌더 전용이라 GT 에 기여하지 못한다.

### 2-5. `UsdGeom.PointInstancer` — **식생·자갈·군중의 유일한 해답**

이것이 §2 에서 가장 중요하다.

**현재 우리 씬의 지오메트리 밀도** **[로컬검증]**: `scene04_parktrail.py` 는
`add_box` 9회, `add_cylinder` 7회, `add_sphere` 2회, `build_tree` 1회(내부 5 프림),
`build_hedge` 1회, `build_bench` 1회 — 루프 포함해도 **수십~수백 프림 규모**다.
사진급 공원 씬은 잔디·잎·자갈만으로 **10⁵~10⁷ 요소**가 필요하다. 3~5 자릿수 차이다.

**PointInstancer 는 이 격차를 메우기 위해 설계된 스키마다.**
**[웹검증]** "The PointInstancer schema is designed to scale to billions of instances."
"Leafs and twigs in vegetation assets are a good example for point instancers."
https://openusd.org/dev/api/class_usd_geom_point_instancer.html ,
https://docs.omniverse.nvidia.com/usd/latest/learn-openusd/independent/modularity-guide/instancing.html

**[로컬검증]** Isaac Sim 4.5 내부에서 실사용 예가 있다:
`…/isaacsim/exts/isaacsim.asset.importer.heightmap/isaacsim/asset/importer/heightmap/block_world.py:147-163`

```python
from pxr import UsdGeom, Gf, Vt
pi = UsdGeom.PointInstancer(stage.DefinePrim("/World/GrassScatter", "PointInstancer"))
# 프로토타입(원본 메시)들을 자식으로 두고 관계로 연결
pi.CreatePrototypesRel().SetTargets(["/World/GrassScatter/Proto/blade_a",
                                     "/World/GrassScatter/Proto/blade_b"])
pi.CreatePositionsAttr(Vt.Vec3fArray(positions))       # (N,3) float32
pi.CreateProtoIndicesAttr(Vt.IntArray(proto_idx))      # (N,)  int
pi.CreateOrientationsAttr(Vt.QuathArray(quats))        # (N,)  half quaternion — 랜덤 yaw
pi.CreateScalesAttr(Vt.Vec3fArray(scales))             # (N,3) 크기 산포
# 선택: 특정 인스턴스 숨기기
pi.CreateInvisibleIdsAttr(Vt.Int64Array([...]))
```

핵심 이점:
- 프로토타입 지오메트리는 **1회만 GPU 에 올라간다**. N 개 인스턴스는 위치/회전/스케일만 차지.
- **[웹검증]** "position, orientation, scales 로 분리 저장해 4×4 행렬보다 바이트 수가 적고
  선택적 애니메이션이 가능하다."
- **중첩 가능**: 잎이 PointInstancer 인 나무 프로토타입을, 다시 숲 PointInstancer 의
  프로토타입으로 쓸 수 있다. **[웹검증]** 동일 문서.

**성능 (RTX 4090 24GB)**:
- **[로컬검증]** 관련 설정 키가 존재한다:
  `/rtx/sceneDb/maxInstances`, `/rtx/hydra/geometrystreaming/instanceBudget`,
  `/rtx/hydra/geometrystreaming/gpuBudgetPriority`
- **[추정 — 반드시 실측 필요]** 24GB / 4090 에서의 실무적 감:
  - 인스턴스 변환 데이터 자체는 인스턴스당 약 40 B (pos 12 + quat 8 + scale 12 + idx 4 + 여유)
    → **100만 인스턴스 ≈ 40 MB**. 즉 **변환 데이터는 병목이 아니다.**
  - 진짜 병목은 **BLAS/TLAS(레이트레이싱 가속구조) 빌드 시간과 메모리**, 그리고
    **프로토타입의 폴리곤 수 × 화면 내 가시 인스턴스 수**.
  - 실무 감각: 저폴리 프로토타입(200~2,000 tri) 기준 **10⁵ 오더는 안전, 10⁶ 오더는
    프로토타입 수를 3~8종으로 제한하면 가능, 10⁷ 은 위험**.
  - **반드시 우리 씬으로 스케일 테스트할 것.** 잔디 10만 → 50만 → 200만 순으로 올리며
    `omni.hydra.engine.stats` 로 VRAM·프레임타임을 찍으면 30분 안에 우리 숫자가 나온다.
    (**[로컬검증]** `omni.hydra.engine.stats-1.0.3` 확장이 설치돼 있다.)

**주의점**:
- **[웹검증]** Replicator 의 `bounding_box_3d` annotator 와 중첩 PointInstancer 가
  충돌하는 버그 리포트가 있다.
  https://forums.developer.nvidia.com/t/bug-bounding-box-3d-and-nested-pointinstancer-conflict/333679
  → 우리는 3D bbox 를 안 쓸 가능성이 높지만, semantic segmentation 과의 상호작용은 검증 필요.
- **[로컬검증]** `create_mesh_decal()` 는 `prim.IsInstanceable()` 이면 인스턴싱을 해제한다
  (`mesh_decal.py:291-292`). 즉 **데칼과 인스턴싱은 같은 프림에 함께 못 쓴다.**

**사실성 기여: 최상.** "구 3개 나무"를 "잎 카드 3,000장 나무"로 바꾸는 유일한 실행 가능 경로.
**도입 비용: 중.** 프로토타입 지오메트리(잎 카드·잔디 클럼프·자갈)를 만들어야 하는데,
이건 §3/§4 의 에셋 확보와 묶인다.

### 2-6. `UsdGeom.BasisCurves` — 미검토 옵션

**[웹검증]** RTX 지원 지오메트리 목록에 "Basis Curves" 가 포함된다.
잔디·잔가지·전선·케이블에 쓸 수 있다. `/rtx/hydra/curves/splits` 설정 키도 로컬에 존재한다 **[로컬검증]**.
`OmniHair.mdl` 이 함께 설치돼 있다 **[로컬검증]** (`omni/mdl/core/Base/OmniHair.mdl`).
**[추정]** 잔디를 커브로 하는 것보다 카드+PointInstancer 가 비용 대비 낫지만,
전선·케이블(도시 골목 씬의 큰 사실성 단서)에는 커브가 정답이다.

---

## §3. 재질 고도화 (MDL)

### 3-0. 먼저 — 우리가 재질에 대해 **잘못 알고 있던 2가지**

이 조사에서 나온 가장 즉각적인 소득은 새 기능이 아니라 **기존 코드의 오해 2건**이다.

#### 오해 ① `project_uvw=True, world_or_object=True` 는 "월드 트라이플래너"가 아니다

**[로컬검증]** `omni/mdl/core/Base/OmniPBR_ClearCoat.mdl:528-538` (OmniPBR 이 상속하는 구현):

```mdl
uvw = project_uvw ? base::coordinate_projection(
        coordinate_system: world_or_object ? base::texture_coordinate_world
                                           : base::texture_coordinate_object,
        texture_space: uv_space_index,
        projection_type: base::projection_cubic )   // ← 큐빅(박스) 투영
      : base::coordinate_source(base::texture_coordinate_uvw, uv_space_index);
```

`projection_cubic` 은 **주 법선축을 하나 골라 평면 투영**한다. 삼평면 블렌딩(triplanar blend)이 아니다.
결과: **축과 정렬되지 않은 면 — 경사 램프, 도랑 벽, 자연석 비탈, 경사 계단 측면 — 에서 이음매(seam)와
스트레치가 생긴다.** 우리 `scene_common.py:341-345` 주석("월드 스페이스 투영(축정렬 박스 → 늘어남 없음)")은
**축정렬 박스에 한해서만** 맞는 말이었고, `build_slope()` / `build_helix_ramp()` / `build_worn_stone_stairs()` 가
만드는 경사면에는 해당하지 않는다.

→ 조치: (a) 경사면은 실제 UV 를 가진 `UsdGeom.Mesh` 로, 또는 (b) 커스텀 삼평면 MDL 작성(§3-6).

#### 오해 ② `texture_scale` 은 `project_uvw` 와 무관하게 항상 적용된다

**[로컬검증]** 같은 파일 L540-547 — `base::transform_coordinate` 호출이 분기 **밖**에 있다.
MDL 의 `anno::enable_if("project_uvw == true")` 는 **UI 회색처리 힌트일 뿐 런타임 동작이 아니다.**
우리 `make_pbr(uv_mode=True)` 경로(사인 패널)는 `texture_scale` 을 설정하지 않으므로 기본값(1,1)이
적용되어 결과적으로는 의도대로 동작한다. 문제는 없지만 전제는 틀렸다.

### 3-1. 설치된 MDL 전량 (18개) — 우리는 1개 쓰는 중

**[로컬검증]** `…/site-packages/omni/mdl/core/Base/` (standalone 사본과 바이트 동일)

| `mdl:sourceAsset` | subIdentifier | 우리 용도 후보 |
|---|---|---|
| `OmniPBR.mdl` | `OmniPBR` | **현재 유일 사용** (입력 47개 중 16개만) |
| `OmniPBR_Opacity.mdl` | `OmniPBR_Opacity` | **잎·풀 알파 컷아웃, 데칼, 철망 펜스** |
| `OmniPBR_ClearCoat.mdl` | `OmniPBR_ClearCoat` | **젖은 노면, 도장 금속, 광택 타일** |
| `OmniPBR_ClearCoat_Opacity.mdl` | 〃 `_Opacity` | 젖은 잎 |
| `OmniPBRBase.mdl` | `OmniPBRBase` | uvw 를 인자로 받음 → 커스텀 래퍼 베이스 |
| `OmniSurface.mdl` | `OmniSurface` | **272 파라미터 우버셰이더 — SSS/이방성/코트/투과/변위** |
| `OmniSurfaceLite.mdl` | `OmniSurfaceLite` | 경량판 |
| `OmniSurfaceBlend.mdl` | `OmniSurfaceBlend` | **마스크 기반 2재질 블렌딩** |
| `OmniSurfacePresets.mdl` | `OmniSurface_Skin_1..4`, `_BrushedMetal`, `_Velvet`, `_Jade`, `_ClearWater`, `_DeepWater`, `_Wax`, `_Foam` 등 37개 | **`_ClearWater`/`_DeepWater` = 하천·웅덩이** |
| `OmniGlass.mdl` / `OmniGlass_Opacity.mdl` | 동명 | **건물 창, 물** |
| `OmniHair.mdl` / `OmniHairPresets.mdl` | `OmniHair` 외 5 | BasisCurves 용 |
| `OmniEmissive.mdl` | `OmniEmissive` | 사인 발광 |
| `SimPBR*.mdl` (3) | 동명 | RTX 센서/DriveSim 계열 |

**미탑재 확정 [로컬검증]**: `AperturePBR_Opacity.mdl` / `AperturePBR_Translucent.mdl` (RTX Remix 재질)
→ **POM(시차 폐색 매핑) 불가.** `vegetation`/`foliage`/`leaf` 이름의 MDL 도 없다.

### 3-2. OmniPBR 미사용 파라미터 — 47개 중 31개를 안 쓰고 있다

**[로컬검증]** `Base/OmniPBR.mdl` L49-355 전량:

```
[Albedo]       diffuse_color_constant★ diffuse_texture★ albedo_desaturation
               albedo_add albedo_brightness diffuse_tint★
[Reflectivity] reflection_roughness_constant★ reflection_roughness_texture_influence★
               reflectionroughness_texture★ metallic_constant★
               metallic_texture_influence metallic_texture specular_level★
[ORM]          enable_ORM_texture ORM_texture
[AO]           ao_to_diffuse ao_texture
[Emissive]     enable_emission★ emissive_color★ emissive_color_texture
               emissive_mask_texture emissive_intensity★
[Opacity]      enable_opacity opacity_texture opacity_constant
               enable_opacity_texture opacity_mode opacity_threshold
[Normal]       geometry_normal_roughness_strength bump_factor★ normalmap_texture★
               detail_bump_factor detail_normalmap_texture
               flip_tangent_u flip_tangent_v
[UV]           project_uvw★ world_or_object★ uv_space_index
               texture_translate texture_rotate texture_scale★
               detail_texture_translate detail_texture_rotate detail_texture_scale
[Geometry]     round_edges_radius round_edges_roundness round_edges_across_materials
```
(★ = 현재 사용 중, 16개)

**가치 순 미사용 파라미터 3개:**

1. **`round_edges_radius` / `round_edges_roundness` / `round_edges_across_materials`**
   — **우리 프로젝트에 가장 중요한 단일 파라미터.** 지오메트리를 전혀 건드리지 않고
   셰이딩 단계에서 모서리를 둥글게 만든다(노멀을 라운딩). 우리는 씬 전체가
   `UsdGeom.Cube`/`Cylinder` 이고 **모든 모서리가 수학적으로 완벽한 직각**인데,
   이것이 "게임 같다"는 인상의 최대 단일 원인이다. 파라미터 1줄로 계단 코·연석·볼라드에
   실물 같은 스펙큘러 하이라이트가 생긴다.
   ```python
   sh.CreateInput("round_edges_radius", Sdf.ValueTypeNames.Float).Set(0.004)  # 4 mm
   sh.CreateInput("round_edges_roundness", Sdf.ValueTypeNames.Float).Set(1.0)
   ```
   **[미검증]** — 이 머신에서 렌더 확인은 하지 않았다. MDL `::base::rounded_corner_normal` 표준 기능이므로
   **[추정] 동작할 것**이나, 레이트레이싱에서는 실루엣이 아니라 음영만 바뀐다는 점을 유의(실루엣까지
   원하면 §2-3 실지오메트리 챔퍼).

2. **`detail_normalmap_texture` + `detail_bump_factor`(기본 0.3) + `detail_texture_scale`**
   — 베이스 노멀과 **독립적인 UV 변환**을 가진다 **[로컬검증]** (`detail_transformed_uvw`,
   `OmniPBR_ClearCoat.mdl:549-556, 585-590`). 이미 가진 노멀맵을 8~16배 스케일로 재활용하면
   근접 촬영(우리 `edge_closeup` 뷰)에서 텍셀이 뭉개지는 문제가 즉시 개선된다.
   ```python
   sh.CreateInput("detail_normalmap_texture", A).Set(nor_path)      # 같은 파일 재사용 가능
   sh.CreateInput("detail_bump_factor", F).Set(0.4)
   sh.CreateInput("detail_texture_scale", F2).Set(Gf.Vec2f(8.0, 8.0))
   ```

3. **`enable_ORM_texture` / `ORM_texture` / `ao_texture` / `ao_to_diffuse`**
   — AO 맵을 물리면 크레비스(줄눈·이음매) 음영이 살아난다. PolyHaven/ambientCG 세트는
   대부분 AO 맵을 함께 제공하는데 우리는 받아놓고도 안 쓰고 있을 가능성이 크다.

### 3-3. 기능별 가능/불가 판정표

| 기능 | 판정 | MDL / 설정 | 사실성 기여 | 비용 |
|---|---|---|---|---|
| **클리어코트** | ✅ | `OmniPBR_ClearCoat.mdl`, `enable_clearcoat=True` + `clearcoat_weight/tint/reflection_roughness/ior(1.56)/bump_factor/normalmap_texture` (13개) | 중 (젖은 노면·도장) | 낮 |
| **SSS / 잎 투과** | ✅ **RT 모드에서도 동작** | `OmniSurface` + `enable_diffuse_transmission=True` + `subsurface_weight` + `thin_walled=True`; 렌더 토글 `/rtx/raytracing/subsurface/enabled`, `/rtx/raytracing/subsurface/transmission/enabled` | **상** (역광 수관 = 우리 스케일 앵커) | 중 |
| **이방성** | ✅ | `OmniSurface.specular_reflection_anisotropy` + `_rotation` | 하 (금속 난간에만) | 낮 |
| **변위(displacement)** | ⚠️ **가능성 있음 — 반드시 실측** | `OmniSurface.geometry_displacement` + `_image` + `_scale` + `_mode`(0=Height/1=Vector-tangent/2=Vector-object) + carb `/rtx/material/enableMDLDisplacement` + `/rtx/hydra/subdivision/refinementLevel` | 상 | 중~상 |
| **디테일 노멀** | ✅ | 위 §3-2 | 중 | **최저** |
| **타일링 반복 제거** | ❌ 기성 없음 / ✅ 커스텀 가능 | `stochastic`/`hex`/`bombing` MDL **0건**. 표준 `::base` 노이즈로 자작 가능 | 중 | 상 |
| **데칼** | ❌ 전용 없음 / ✅ 우회 | 판 + `OmniPBR_Opacity`(§3-5) | **상** | 중 |
| **버텍스컬러 구동** | ⚠️ 커스텀 MDL 필수 | `::scene::data_lookup_float3()` 는 지원되나 OmniPBR/OmniSurface 가 노출 안 함 | 중 | 상 |
| **마스크 재질 블렌딩** | ⚠️ 커스텀 MDL 필수 | `OmniSurfaceBlend.mdl` 은 `material` 타입 인자라 `UsdShade` 에서 직접 지정 불가 | 상 | 상 |
| **UDIM** | ✅ | `<UDIM>` 토큰 지원 (`rtx.mdltranslator` 경로 + 전용 테스트 스테이지 존재) | 하 (우리는 불필요) | — |
| **POM / 시차매핑** | ❌ | AperturePBR 미탑재 | — | — |

> **변위에 대한 최종 입장**:
> - **[웹검증]** NVIDIA 공식 답변(2024-09, Isaac Sim 4.1 시점): "RTX in Isaac Sim does not
>   currently support displacement." https://forums.developer.nvidia.com/t/bug-isaac-sim-render-does-not-listen-to-mdl-material-geometry-displacement/305411
> - **[로컬검증]** 그러나 4.5.0 에는 `/rtx/material/enableMDLDisplacement` 설정이 툴팁까지 붙어
>   존재하고("Enabling it can negatively impact stage load time when there are many materials
>   with displacement support (like OmniSurface)"), `OmniSurfaceBase.mdl:876-877` 이
>   `material_geometry(displacement: geometry_displacement, …)` 로 실제 연결돼 있다.
> - **판정: [미검증] — 30분짜리 실험 1회로 확정할 것.** 프리미티브(`Cube`)에는
>   `subdivisionScheme` 이 없으므로 **`UsdGeom.Mesh`(catmullClark) 로 교체해야 할 가능성이 높다 [추정]**.
> - 실험 실패 시 대체 경로는 §2-4(실지오메트리 하이트필드)이며, 그쪽이 GT 낙차 맵 재사용 측면에서
>   오히려 유리하다.

### 3-4. 알파 컷아웃 — 식생의 필수 관문

잎·풀·철망을 카드(판)로 표현하려면 알파 컷아웃이 반드시 필요하다.

```python
sh.CreateInput("enable_opacity",         B).Set(True)
sh.CreateInput("enable_opacity_texture", B).Set(True)
sh.CreateInput("opacity_texture",        A).Set(Sdf.AssetPath("/tex/leaf_alpha.png"))
sh.CreateInput("opacity_mode",           Sdf.ValueTypeNames.Int).Set(0)    # 0=mono_alpha [추정]
sh.CreateInput("opacity_threshold",      F).Set(0.5)   # >0 = 바이너리 컷아웃(빠름)
```
`opacity_threshold=0` 으로 두면 **부분 불투명(fractional)** 처리가 되는데, 이때는 렌더 토글이 필요하다
**[로컬검증]**:
```python
s.set("/rtx/raytracing/fractionalCutoutOpacity",  True)   # RT
s.set("/rtx/pathtracing/fractionalCutoutOpacity", True)   # PT
```
> **[추정]** 대량 식생에는 `opacity_threshold=0.5`(바이너리)가 압도적으로 빠르다.
> fractional 은 유리·반투명 천막에만 쓸 것.

### 3-5. 데칼 — 전용 기능 없음, 두 가지 우회 경로

**[로컬검증]** 설치본 전체에서 데칼 전용 MDL·프림 타입·확장·깊이 바이어스 설정을 찾지 못했다.

**경로 A (수동, 권장)**: 표면에서 살짝 띄운 얇은 `UsdGeom.Mesh` quad + `OmniPBR_Opacity`
```python
# 지면 z=0 위에 오염 얼룩 데칼
quad = make_quad_mesh(stage, "/World/Decal_Stain_01", w=1.2, h=0.8, z=0.003)
mtl  = make_pbr_opacity(stage, "/World/Looks/Stain01",
                        diff="stain_diff.png", opac="stain_alpha.png", threshold=0.5)
```
Z-fighting 은 깊이 바이어스가 아니라 **물리적 오프셋(2~5 mm)** 으로 해결한다.
레이트레이서라 래스터라이저식 z-fighting 은 덜하지만, 자기교차는 `/rtx/raytracing/rayOffset`(기본 0=auto)로
조정 가능하다 **[로컬검증]**.

**경로 B (자동, Replicator)**: `rep.utils.mesh_decal.create_mesh_decal()`
**[로컬검증]** `…/omni/replicator/core/scripts/utils/mesh_decal.py:264-280`
```python
from omni.replicator.core.utils.mesh_decal import create_mesh_decal
create_mesh_decal(
    prim_path="/World/Ground",            # ★ UsdGeom.Mesh 여야 한다 (Cube 불가)
    decal_path="/World/Decals/crack_01",
    diffuse="/tex/crack_d.png", normal="/tex/crack_n.png",
    roughness="/tex/crack_r.png", opacity="/tex/crack_a.png",
    semantics=[("class", "crack")],       # ★ 세그멘테이션 라벨까지 붙는다
    position=Gf.Vec3d(2.0, 0.5, 0.0), rotation=Gf.Vec3d(0,0,37),
    scale=Gf.Vec3d(0.8,0.8,1.0),
    offset_normal=0.1, offset_depth=0.0)
```
이건 표면 메시를 클리핑해 **표면에 완전히 밀착된 데칼 지오메트리를 GPU(warp)로 생성**한다.
평면 판보다 훨씬 좋다 — 곡면·경사면·계단 모서리를 타고 감긴다.

**두 가지 제약 [로컬검증]**:
- 대상은 반드시 `UsdGeom.Mesh` — `mesh_decal.py:295-297` 이 `UsdGeom.Mesh(prim)` 로 캐스팅한다.
  **우리 `UsdGeom.Cube` 는 못 쓴다.** → §2-1 Mesh 전환의 또 하나의 동기.
- `prim.IsInstanceable()` 이면 인스턴싱을 **해제해 버린다**(`mesh_decal.py:291-292`).
  **데칼과 인스턴싱은 같은 프림에 공존 불가.**

**사실성 기여: 상.** 균열·오염·페인트 마킹·타이어 자국·물때는 실사진과 CG 를 가르는 결정적 요소다.
특히 우리 연구에서 **계단 코의 마모·미끄럼방지 테이프·경계 페인트**는 낙차 단서 그 자체다.

### 3-6. 커스텀 MDL — 절차 확인됨

**[로컬검증]** `…/extscache/omni.usd.config-1.0.5+d02c707b/omni/usd_config/extension.py:12-13`,
`omni.kit.material.library-1.5.15/…/material_path_widget.py:43-44, 236`

검색경로 carb 설정 3개 (환경변수 `MDL_SYSTEM_PATH`/`MDL_USER_PATH` 는 Kit `.kit` 어디에도 없다):
```
/renderer/mdl/searchPaths/required     # 코어. 건드리지 말 것
/renderer/mdl/searchPaths/templates    # 템플릿
/renderer/mdl/searchPaths/custom       # ← 여기에 추가
```
```python
# ★ 스테이지 로드 전에 (부팅 직후) 설정할 것
paths = s.get("/renderer/mdl/searchPaths/custom") or ""
s.set("/renderer/mdl/searchPaths/custom", paths + ";/abs/path/to/negobs_mdl")
# 이후
sh.SetSourceAsset(Sdf.AssetPath("NegObsTriplanar.mdl"), "mdl")
sh.SetSourceAssetSubIdentifier("NegObsTriplanar", "mdl")
```
Kit 은 런타임에 MDL 을 컴파일한다. 표준 `::base`(노이즈·투영·변환), `::scene`(primvar 조회),
`::nvidia::core_definitions`, `::nvidia::support_definitions` 전부 사용 가능 **[로컬검증]**
(`omni/mdl/core/mdl/base.mdl` 등은 31줄 스텁이고 실체는 컴파일러 내장).

**커스텀 MDL 로 풀 수 있는 것 3가지** (전부 순정으로는 불가):
1. **진짜 삼평면 블렌딩** — §3-0 오해① 해결
2. **스토캐스틱/헥스 타일링** — 4K 텍스처의 격자 반복 제거. 우리 지면·잔디에 직접적
3. **`primvars:displayColor` 구동 2텍스처 블렌딩** — 젖음/이끼/마모 그라데이션
   (`::scene::data_lookup_float3("displayColor", …)` 또는
   `::nvidia::support_definitions::data_lookup_float3`)

**비용: 상** (MDL 문법 학습 + 셰이더 디버깅). **[추정]** 우선순위는 §3-2/§3-4/§3-5 를 다 쓴 뒤.

### 3-7. 텍스처 메모리 — `.dds` 변환 불필요

**[로컬검증]** RTX 가 **런타임 블록압축**을 하므로 사전 `.dds` 변환이 필수가 아니다. 관련 키:
```
/rtx-transient/resourcemanager/enableTextureStreaming            (씬 리로드 필요)
/rtx-transient/resourcemanager/texturestreaming/memoryBudget     (0~1, GPU 메모리 비율)
/rtx-transient/materialdb/blockCompression/quality               0=Fastest 1=Normal 2=Production 3=Highest
/rtx-transient/resourcemanager/maxMipCount                       13=4096 12=2048 11=1024
/rtx-transient/resourcemanager/genMipsForNormalMaps              (씬 리로드 필요)
/rtx-transient/resourcemanager/createNormalRoughness             (노멀맵 밉의 스펙큘러 개선)
```
**[추정]** 외부 에셋을 대량 들여올 때(§4~§5) 24GB 를 넘길 위험이 생기면
`maxMipCount=12`(2048) 또는 텍스처 스트리밍을 켜면 된다. 최종 렌더는 `blockCompression/quality=2`.

---

## §4. 외부 에셋 임포트 파이프라인

### 4-1. 【최우선】 NVIDIA Isaac 4.5 공식 에셋 — 12,689개, 무료, 평문 HTTPS

**이 조사 전체에서 가장 즉시 실행 가능하고 효과가 큰 발견이다.**

#### 발견 경위 및 검증

**[로컬검증]** Isaac Sim 4.5 는 에셋 브라우저 캐시를 로컬에 갖고 있다:
`…/site-packages/isaacsim/exts/isaacsim.asset.browser/cache/isaacsim.asset.browser.cache.json` (3.87 MB)

이 JSON 을 파싱하면 **전체 카탈로그 12,689개 파일**과 각 루트 URL 이 나온다:

```
Robots       https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.5/Isaac/Robots
Environments https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.5/Isaac/Environments
People       https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.5/Isaac/People
Props        https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.5/Isaac/Props
Samples      https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.5/Isaac/Samples
Sensors      https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.5/Isaac/Sensors
IsaacLab     https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.5/Isaac/IsaacLab
```

**[웹검증 — 이 세션에서 `curl` 로 직접 확인, 전부 HTTP 200/206]**
```
$ curl -sI ".../Isaac/4.5/Isaac/Environments/Outdoor/Rivermark/rivermark.usd"          → 200, 2,858 B
$ curl -sI ".../Isaac/4.5/Isaac/Environments/Terrains/stairs.usd"                      → 200, 8,912 B
$ curl -sI ".../Isaac/4.5/Isaac/People/Characters/original_male_adult_construction_01/
             male_adult_construction_01.usd"                                            → 200, 544,468 B
$ curl -sI ".../props_general/bollard_01/bollard_01.usd"                                → 200, 43,658 B
$ curl -sI ".../Isaac/4.5/Isaac/Environments/Simple_Warehouse/full_warehouse.usd"       → 200, 6,724,555 B
```

> **Nucleus 서버 불필요. Omniverse Launcher 불필요. 계정·로그인 불필요. `curl`/`wget` 로 바로 받아진다.**
> Range 요청(206)도 동작하므로 부분 다운로드·병렬 다운로드가 가능하다.

#### 우리에게 직접 쓸모 있는 것 — 카테고리별

**[로컬검증]** 카탈로그 JSON 파싱 결과.

**① `Environments/Outdoor/Rivermark/` — 미국 도시 광장 씬 (3,129 파일)**
DriveSim 계열 자산으로, 우리 프로젝트에 없는 것 대부분이 여기 있다:

| 하위 카테고리 | 개수 | 우리 용도 |
|---|---|---|
| `props_general` | **27종** | **`bollard_01`, `safety_railing_01`**, `bench_curved_01`, `bench_wrought_iron_02`, `planter_round_02`, `trashcan_cylinder_01`, `trashcan_square_01`, `bike_rack_01`, `dumpster_lrg_01/02`, `concrete_block_01/02`, **`crosswalk_button_01`, `crosswalk_signal_01`**, `firehydrant01/04`, `patio_umbrella_01`, `table01`, `shopping_cart_corral_01` |
| `props_poles` | **238종** | 가로등 40+종(`streetlamp_*`, `st_lamp_pole_*`, `luminaire_*`), 표지판 기둥 20+종, `fence_post_6ft_01`, **`walkway_*` 22종(보행 통로/육교 구조)**, `truss_*` 30+종(오버헤드 갠트리) |
| `props_signage` | 17종 | 상점 사인 15종 |
| `props_structures` | 16종 | `apt_complex_assembly`(아파트 단지!), `bldg_modern_library`, `kasa_house_01~03`, `rivermark_plaza_bldg_01~08`, `sanjose_rivermark_wyatt_parking`(**주차 건물**) |
| `country_signs` | **493종** | 미국 표지판. 한국용은 아니지만 형태 참조·랜덤 배경 소품 |
| `traffic_lights` | 147+ | 신호등 하우징·전구 |
| `scene_assets/grass/island_tiles` + `reduced_grass/tiles` | **16 타일** | **실제 잔디 지오메트리 타일** — 우리 "텍스처만 있는 잔디" 문제의 직접 해답 |
| `nv_core/materials/` | 130+ | `drivable_surfaces/`(아스팔트·콘크리트 노면), `surrounding_surfaces/island_curb`(**연석 22종**), `island_planter`, `markings_road`, `vehicles/general`(차체·유리·라이트), `signs/general` |
| `common_procedural_assets/` | — | `terrain_roads/rigs`(도로 절차 리그), `curbs_gutters/templates`(**연석·측구 템플릿**) |
| `animals/pedestrians/Reallusion/` | 89 | Reallusion 보행자 + 애니메이션 리소스(`DanceCard_DS` 에 걷기/조깅 take 다수) |

**② `People/` — 사람 (288 파일)**

| 그룹 | 내용 |
|---|---|
| `People/Characters/` | 기본 캐릭터 **약 20종**: `male/female_adult_construction_01~05`, `_police_01~04`, `_medical_01`, `_business_02`, `biped_demo` |
| `People/DH_Characters/` | Digital Human **22종** (UUID 명명) |
| `People/DH_Characters_Extended/` | 위 22종 × **의상/외형 변형 10종 = 약 220 USD** |
| `People/Animations/` | **애니메이션 24종** (걷기·서기 등) |
| `People/Characters/Biped_Setup.usd` | 리깅 셋업 |

> **한계**: 전부 서양인 체형·미국식 복장(경찰/건설/의료/비즈니스)이다.
> 한국인 보행자로는 부정확하다. **그러나 우리 용도는 "스케일 앵커"** — 5~30 m 거리에서
> 상반신이 눈높이 이하인지를 보는 것이므로 **실루엣과 키가 맞으면 충분하다 [추정]**.
> 인종·복장 편향이 학습에 영향을 줄 위험은 있으므로, 데이터셋 문서에 명시하고
> 필요하면 §5 의 다른 소스로 보강한다.

**③ `Environments/` 기타**

| 경로 | 내용 | 실내/외 |
|---|---|---|
| `Environments/Terrains/` | `flat_plane.usd`, `rough_plane.usd`, `slope.usd`, **`stairs.usd`** | 외 |
| `Environments/Simple_Warehouse/full_warehouse.usd` (6.7 MB) | 창고 전체 | 내 |
| `Environments/Digital_Twin_Warehouse/small_warehouse_digital_twin.usd` | 창고 디지털트윈 | 내 |
| `Environments/Hospital/hospital.usd` + Props 294개 | 병원 | 내 |
| `Environments/Office/office.usd` + Props 543개 | 사무실 | 내 |
| `Environments/Modular_Warehouse/Props/` | 창고 모듈 9종(높이 4.5 m / 10 m 코너·직선) | 내 |
| `Environments/Grid/` | `default_environment.usd`, `gridroom_black/curved.usd` | — |

**④ `Props/`** — `YCB`(물체 인식 표준 세트), `Blocks`, `Shapes`, `Pallet`, `KLT_Bin`,
`Forklift`, `Conveyors`, `Food`, `Mugs`, `SektionCabinet` 등. 실내 로보틱스 위주.

**⑤ `Samples/`** — `DR`(도메인 랜덤화 예제), `Replicator`, `Scene_Blox`, `PeopleDemo`,
`OmniGraph`, `NvBlox`. **`Samples/DR` 과 `Samples/Replicator` 는 §8 학습 자료로 직접 유용.**

#### `Assets/Isaac/**` 안에 **없는 것**

**[로컬검증]** 카탈로그 파일명 전수 검색:
- 나무·관목 0건 (`Office/Props/SM_Plant01~03` 실내 화분이 전부) → **그러나 다른 루트에 있다. §4-1b 참조.**
- 한국식 요소 0건 (점자블록·한국형 볼라드·한글 표지판) → §5 또는 자체 제작
- 자연 지형(하천·제방·암반) 0건 → `Assets/Vegetation/Rocks` 로 일부 보완 가능

---

### 4-1b. 【결정적】 `Assets/Vegetation/` — 나무 44종·관목 37종, **별도 루트에 존재**

**이것이 이 조사의 두 번째 큰 발견이다.** Isaac 에셋 브라우저 캐시(§4-1)에는 없지만,
**두 번째 에셋 브라우저 확장**이 완전히 다른 S3 루트를 가리킨다.

**[로컬검증]** `…/extscache/omni.kit.browser.asset-1.3.11/config/extension.toml` ("NVIDIA Assets" 창):
```toml
exts."omni.kit.browser.asset".folders = [
  ".../Assets/Vegetation",
  ".../Assets/ArchVis/Commercial",  ".../Assets/ArchVis/Industrial",  ".../Assets/ArchVis/Residential",
  ".../Assets/DigitalTwin/Assets/Warehouse/{Equipment,Safety,Shipping,Storage}",
]
```
이 확장은 `apps/isaacsim.exp.full.kit` 에만 등록돼 있고 `isaacsim.exp.base.python.kit`
(우리 standalone 경로)에는 없어 **GUI 에서도 우리 눈에 띄지 않았다.**
하지만 폴더 URL 은 그냥 S3 경로이므로 직접 참조하면 된다.

#### 실제 목록 — **[웹검증: S3 익명 리스팅으로 이 세션에서 직접 확인]**

`https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Vegetation/`

| 폴더 | 개수 | 목록 |
|---|---|---|
| **`Trees/`** | **44 USD** | American_Beech, Black_Oak(+_Fall), Blue_Berry_Elder, Chinese_Juniper, Colorado_Spruce, Common_Apple, Dogwood, Douglas_Fir, Eastern_Hemlock, Elm_Sapling, Fraxinus, Golden_Chain, Gray_Birch(+_fall), Hawthorn, Honey_Locust(+_Fall), Italian_Cypress, **Japanese_Cherry**, **Japanese_Maple**(+_Fall), Kousa_Dogwood, Largetooth_Aspen, Lombardy_Poplar(+_Fall), Norway_Spruce, Orange_Tree, Red_Ash(+_Fall), Red_Cedar, Red_Maple, Red_Oak, Scarlet_Oak(+_fall), Service_Berry, Shumard_Oak(+_Fall), Siberian_Crab_Apple, Sugar_Maple, Sycamore, White_Ash, White_Pine, Yellow_Pine |
| **`Shrub/`** | **37 USD** | Acacia, Barberry, Boxwood, Burning_Bush, Cedar_Shrub, Century, Daphne, **Forsythia**, … |
| **`Leaves/`** | 5 USD | `cluster_1`, `cluster_2`, `maple`, `oak_1`, `oak_2` — **잎 클러스터 = PointInstancer 프로토타입** |
| **`Debris/`** | 5 USD | `fallcluster1/2`, `maplefall1`, `oakfall1/2` — **낙엽 더미** |
| **`Rocks/`** | 15 USDA | `rock_small_01~08` 외 — 자갈·돌 |
| **`Plant_Tropical/`** | 17 USD | Agave, Australian_Tree_Fern, Buddha_Belly_Bamboo, Crane_Lily, Cuban_Royal_Palm, Dagger, Fan_Palm, Golden_Malay_Palm, … |
| `Trees/materials/` | — | 종별 MDL + 썸네일. 잎/수피 재질이 종·계절별로 분리 (`*_leaf_Mat`, `*_leaf_fall_Mat`, `*_Bark_Mat`) |

**[웹검증]** `Japanese_Cherry.usd` = **35,517,515 B (35.5 MB), USD crate, `Mesh` 프림 + `.mdl` 재질**.
즉 **실제 폴리곤 메시 트리**다(임포스터/빌보드가 아님). 4.22 GB 전체 규모.

#### 우리 프로젝트에 대한 의미 — **"구 3개 나무" 문제의 완전한 해결**

- **`Japanese_Cherry`(벚나무)** = 한국 가로수·공원의 대표종. **`Japanese_Maple`(단풍)**,
  **`Forsythia`(개나리)**, `Boxwood`(회양목, 한국 조경 관목 1위) — **한국 도시 조경에 그대로 쓸 수 있다.**
- **`_Fall` 변종이 8종 이상** → 계절 변주가 공짜로 생긴다 (현재 batch1 의 낙엽 조건 C2 를 대폭 강화).
- **`Leaves/cluster_*`** 는 §2-5 PointInstancer 의 프로토타입으로 바로 쓸 수 있다.
- **`Debris/*fall*`** 은 낙엽 더미 소품 엔트로피에 직결.
- **`Rocks/rock_small_*`** 는 하천·제방·산사 씬의 자갈/사석에 직결.

**단, 반드시 확인할 것 [미검증]**:
1. **알파 컷아웃이 제대로 켜져 오는가** — §4-5 의 `opacityThreshold` 함정. 잎이 불투명 판때기로
   렌더링되면 아무 소용이 없다. **트리 1개 로드 + RT 1장 렌더로 즉시 확인.**
2. **폴리곤 수와 24GB 예산** — 35 MB USD 는 대략 수십만 폴리곤 [추정]. 씬당 20~50 그루면
   수백만~수천만 폴리곤. **`UsdGeom` instanceable 참조 또는 PointInstancer 로 배치할 것**(§2-5).
3. **스케일 단위** — `metersPerUnit` 확인 필요.

### 4-1c. 그 밖의 NVIDIA S3 루트

**[웹검증 — S3 익명 리스팅 확인]** 버킷 최상위:
```
Assets/{AnimGraph, ArchVis, Audio2Face, Characters, Configurator, DigitalTwin,
        Extensions, Isaac, Machinima, OmniGraph, Particles, Scenes, Skies,
        Terrain, Vegetation, XR, simready_content}/
```
- **`Assets/Isaac/`** 버전 폴더가 `2022.1 … 4.5, 5.0, 5.1, 6.0` 까지 존재
  → **4.5 설치본에서도 URL 만 바꾸면 6.0 에셋을 참조할 수 있다 [추정]**(스키마 호환성 확인 필요).
- **`Assets/simready_content/`** — 37,336 objects / **78.4 GB**.
  `asset_info.json`(전체 매니페스트: 상대경로·썸네일·PhysicsVariant·Extent(m)·Wikidata Q코드),
  `project_config.toml`(카테고리 스키마: `asset = ["humans","animals","props","vegetation"]`,
  `countries = ["china","germany","japan","usa","uk"]`, `material.basename = "SimPBR"`).
  **공개 SimReady 팩은 warehouse / containers&shipping / furniture&misc 뿐이고
  city·vehicles·road signs 는 없다.** 도시 자산은 SimReady 가 아니라 Rivermark 쪽이다.
- **`Assets/Scenes/Templates/Outdoor/`** — `Puddles.usd`, `waco_tarmac.usd` 2개(룩데브 소규모).
- **`Assets/Terrain/`**, **`Assets/ArchVis/{Commercial,Industrial,Residential}`** — 미조사.

**[웹검증]** 전체 규모: `Assets/Isaac/4.5/` = **275,368 objects / 281.7 GB**.
그 중 `Environments/Outdoor/Rivermark/` = **10.83 GB**, `Environments/` 전체 16.9 GB,
`Robots/` 5.6 GB, `Props/` 4.2 GB, `Skies/` 3.2 GB, `Vegetation/` 4.2 GB.

**오프라인 zip [웹검증]** (에어갭용, 총 86 GB):
```
https://download.isaacsim.omniverse.nvidia.com/isaac-sim-assets-1-4.5.0.zip  (33.5 GB)
https://download.isaacsim.omniverse.nvidia.com/isaac-sim-assets-2-4.5.0.zip  (28.6 GB)
https://download.isaacsim.omniverse.nvidia.com/isaac-sim-assets-3-4.5.0.zip  (24.1 GB)
```

**Omniverse 다운로드 팩 (Launcher 폐지 후에도 cloudfront 링크 생존, 2026-07-28 HEAD 200 확인)**
**[웹검증]**:

| 팩 | URL (`https://d4i3qtqj3r0z5.cloudfront.net/` +) | 크기 | 우리 관련성 |
|---|---|---|---|
| **Architectural Brownstone** | `AECDemo_NVD%4010012.zip` | 2.08 GB | **NYC 브라운스톤 97개 — 현관 계단(stoop)·난간·연석. 우리 주제 직결** |
| **City Tower Demo** | `AECO_CityTowerDemoPack_NVD%4010011.zip` | 2.80 GB | 도시 컨텍스트 + 타워 |
| **City Demo** | `AECO_CityDemoPack_NVD%4010011.zip` | 197 MB | ArcGIS CityEngine 도시 모델 |
| City Massing Demo | `AECO_CityMassingDemoPack_NVD%4010011.zip` | ~193 MB | 공원 + 매싱 |
| Sample Scenes (441 에셋) | `Sample_Scenes_NVD%4010013.zip` | 26.7 GB | Attic/Marbles 등 |
| Environments Skies (HDR 32개) | `Environments_NVD%4010012.zip` | 9.03 GB | **HDRI 32종 — 시간대·기상 변주** |
| **vMaterials 2.4 (MDL 1,854종)** | `vMaterials_2_4_0_NVD%40020240.zip` | 2.22 GB | **재질 라이브러리 대폭 확장** |
| Base Materials (MDL 161종) | `Base_Materials_NVD%4010013.zip` | ~8.2 GB | 재질 |
| Rigged Characters (Reallusion 7) | `Characters_NVD%4010012.zip` | ~891 MB | 보행자 |

### 4-1d. 라이선스 — **3층 구조. 반드시 구분할 것**

**[웹검증 — 라이선스 원문 직접 확보]**
`https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.5/Isaac/Environments/environment-supplement-LICENSE.txt` (v.2021-11-18):

> "SUPPLEMENT TO SOFTWARE LICENSE AGREEMENT FOR CERTAIN 3D ASSETS WITH **LIMITED USE RIGHTS** …
> The terms in this supplement govern your use of certain NVIDIA Omniverse USD assets in the
> **/Isaac/Environments** ("Limited Use Content") … NVIDIA grants you a non-exclusive,
> non-transferable, non-sublicensable license to install and use copies of the Limited Use Content
> **for your use only, without modifications** … The license grant for Content as described in
> the Agreement **does not apply to** Limited Use Content."

| 층 | 대상 | 조건 |
|---|---|---|
| **① MIT-0 (완전 자유)** | `github.com/NVIDIA-Omniverse/PhysicalAI-SimReady-Materials` — **PBR 재질 1,705종**, UsdShade + MaterialX + OpenPBR 1.1, 16 카테고리 (Carpet/Ceramic/**Concrete**/Fabric/Glass/**Ground**/Leather/Liquids/**Masonry**/Metal/Paint/Paper/Plastic/Skin/Stone) | 수정·재배포 무제한 |
| **② CC-BY-4.0** | `huggingface.co/datasets/nvidia/PhysicalAI-SimReady-Warehouse-01` — 753 OpenUSD 에셋, ~15 GB, Isaac 4.x 호환 명시. 형제: `PhysicalAI-DigitalCousin-Assets`(862), `PhysicalAI-Robotics-PhysicalAssets-VoMP`(507) | 출처 표기 시 수정·재배포 자유 |
| **③ NVIDIA Omniverse License / Limited Use** | S3 `Assets/Isaac/**/Environments/**` (**Rivermark 포함**), cloudfront zip 팩 | 사용 가능, **수정 금지**, 재배포 불가 |

**[웹검증]** Isaac Sim 자체 라이선스(https://docs.isaacsim.omniverse.nvidia.com/6.0.0/common/license-faq.html):
소스코드 Apache-2.0, Kit SDK + 3D 모델/텍스처는 별도 "NVIDIA Isaac Sim Additional Software and
Materials License". **내부 R&D 무료**, 제3자 재배포/서비스 제공은 AI Enterprise 필요.
**시뮬레이션 산출물(영상/데이터셋/리포트)만 배포하는 것은 AI Enterprise 불필요**
→ **연구용 합성 데이터셋 생성·논문 발표는 문제없다.**

> **우리 프로젝트에 대한 실무 결론:**
> - **렌더링해서 이미지 데이터셋을 만드는 것: 전부 OK** (①②③ 모두).
> - **USD 를 편집해 파생 씬을 만드는 것: `/Isaac/Environments`(Rivermark) 는 문언상 불가(③).**
>   → Rivermark 는 **통째로 로드해 카메라만 옮기는 배경**으로 쓰고,
>     낱개 소품(볼라드·난간·벤치)은 `/Isaac/Props`·`Assets/Vegetation` 쪽(supplement 없음)에서 가져오거나
>     ①②층으로 대체하는 편이 안전하다.
> - **`Assets/Vegetation/` 에는 LICENSE 파일이 없다** **[웹검증 — S3 리스팅에 licen/readme 파일 0건]**
>   → 상위 Omniverse License 적용으로 보이며 `/Isaac/Environments` 의 "수정 금지" supplement 대상은 아니다 **[추정]**.
> - **데이터셋을 공개 배포할 계획이면 ①(MIT-0)·②(CC-BY) 중심으로 구성하는 것이 가장 안전하다.**

#### 다운로드 레시피

```bash
BASE="https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.5/Isaac"
DEST="$HOME/Desktop/work_sy/Practice_NegObs/assets/nvidia"
mkdir -p "$DEST"

# 낱개 (의존 USD·텍스처가 상대참조라 함께 받아야 함)
curl -L "$BASE/Environments/Outdoor/Rivermark/dsready_content/nv_content/common_assets/\
props_general/bollard_01/bollard_01.usd" -o "$DEST/bollard_01.usd"
```

**권장 방법 — Isaac Sim 내부에서 참조만 하기 (다운로드 불필요)**:
USD 는 HTTPS URL 을 그대로 참조할 수 있고, Kit 의 `omni.client` 가 캐싱한다.
```python
from pxr import Usd, UsdGeom, Gf
BASE = ("https://omniverse-content-production.s3-us-west-2.amazonaws.com"
        "/Assets/Isaac/4.5/Isaac")
ref = stage.DefinePrim("/World/Bollard_01", "Xform")
ref.GetReferences().AddReference(
    f"{BASE}/Environments/Outdoor/Rivermark/dsready_content/nv_content/"
    f"common_assets/props_general/bollard_01/bollard_01.usd")
UsdGeom.Xformable(ref).AddTranslateOp().Set(Gf.Vec3d(1.2, 0.0, 0.0))
```
**[추정]** 첫 실행은 네트워크 지연이 있지만 이후 로컬 캐시를 탄다.
대량 렌더에서는 **미리 로컬에 받아두는 편이 안전**하다(네트워크 실패 시 렌더 중단 위험).

Isaac Sim 공식 API 로도 루트를 얻을 수 있다 **[로컬검증]**
(`…/isaacsim/exts/isaacsim.storage.native/isaacsim/storage/native/nucleus.py:452`):
```python
from isaacsim.storage.native import get_assets_root_path
root = get_assets_root_path()        # carb 설정 /persistent/isaac/asset_root/default 참조
```

### 4-2. NVIDIA Skies 라이브러리 (별도 루트)

**[웹검증 — HTTP 200 확인]** §6-2 참조.
```
https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Skies/2022_1/Skies/
    Dynamic/{ClearSky,CumulusLight,CumulusHeavy,Cirrus,Overcast,NightSky}.usd
    Sky_Elements/SphereInverseLow.usd
    Sky_Elements/materials/procedural/*.mdl
```

### 4-3. 파일 포맷 변환 (glTF / FBX / OBJ → USD)

**[로컬검증]** `omni.kit.asset_converter-2.8.3+106.5.0` 가 설치돼 있다.
`…/isaacsim/extscache/omni.kit.asset_converter-2.8.3+106.5.0.lx64.r.cp310/config/extension.toml:3`
> "The asset converter API for converting assets. It supports conversion between assets
>  like OBJ, GLTF, FBX and USD."

**[로컬검증]** 백엔드 바이너리가 **이미 동봉**돼 있다:
`asset_converter_native_bindings/libs/libfbxsdk.so` (Autodesk FBX SDK),
`libassimp.so.5.4.3` (폴백) → **FBX SDK 별도 설치·라이선스 취득 불필요.**

**지원 범위 [로컬검증]** (`docs/Overview.md §1.3`): OBJ / FBX / glTF ↔ USD **양방향**,
미인식 포맷은 Assimp 폴백. glTF text/binary, 텍스처 embed 유무 모두.
mesh · camera · point/sphere/distant/rect light · rigid+skeletal 애니메이션.
**glTF 재질 → MDL 변환** 확장 지원: `KHR_materials_pbrSpecularGlossiness`, `_clearcoat`,
`_volume`, `_emissive_strength`, `_ior`, `_sheen`, `_transmission`,
`KHR_draco_mesh_compression`, `KHR_texture_transform`, `NV_materials_mdl`.
제약: glTF 재귀 스켈레톤 미지원. USD→타포맷 익스포트는 OmniPBR/OmniGlass/UsdPreviewSurface/gltf.mdl 만.

**재질 파라미터 지원 매트릭스 [로컬검증]**

| | ASSIMP | FBX | glTF | OBJ |
|---|---|---|---|---|
| DIFFUSE / EMISSIVE / **OPACITY** / NORMAL | O | O | O | O |
| SPECULAR | O | O | O | – |
| OCCLUSION | O | O | O | – |
| ROUGHNESS / METALLIC | O | O | O | O |
| CLEARCOAT / TRANSMISSION / SHEEN | O | – | O | – |

**헤드리스 변환 스크립트 [로컬검증 — 시그니처·옵션명 소스 확인, 실행은 미검증]**

```python
import asyncio
from isaacsim import SimulationApp
kit = SimulationApp({"headless": True})
from isaacsim.core.utils.extensions import enable_extension
enable_extension("omni.kit.asset_converter")
import omni.kit.asset_converter as converter

async def convert(src, dst):
    ctx = converter.AssetConverterContext()
    ctx.ignore_materials = False
    ctx.export_preview_surface = False        # False = MDL 임포트 (RTX 최상 품질)
    ctx.use_meter_as_world_unit = True        # metersPerUnit = 1.0
    ctx.create_world_as_default_root_prim = True
    ctx.convert_stage_up_z = True             # Isaac 기본 Z-up
    ctx.convert_fbx_to_z_up = True            # FBX 소스일 때
    ctx.smooth_normals = True
    ctx.keep_all_materials = False
    ctx.single_mesh = False                   # 인스턴싱 유지
    task = converter.get_instance().create_converter_task(src, dst, None, ctx)
    ok = await task.wait_until_finished()
    if not ok:
        print("FAILED", task.get_status(), task.get_error_message())
    return ok

asyncio.get_event_loop().run_until_complete(convert("/in/model.glb", "/out/model.usd"))
kit.close()
```

**주요 옵션 [로컬검증]** (`omni/kit/asset_converter/impl/context.py`, 총 28개)

| 옵션 | 기본 | 의미 |
|---|---|---|
| `export_preview_surface` | **False** | False = MDL 임포트(권장). True = UsdPreviewSurface |
| `use_meter_as_world_unit` | False | True = metersPerUnit 1.0, cm 모델 자동 스케일 |
| `create_world_as_default_root_prim` | True | `/World` 루트 |
| `convert_stage_up_z` / `convert_fbx_to_z_up` | False | up-axis 강제 |
| `single_mesh` / `merge_all_meshes` | False | False = 인스턴싱 유지 |
| `baking_scales` | False | FBX 스케일을 메시에 굽기 |
| `keep_all_materials` | False | 미참조 재질 제거 |

**[로컬검증]** `omni.kit.asset_converter` 는 `omni.ui` 의존이 **전혀 없다** → **순수 헤드리스 안전**.
반면 `omni.kit.tool.asset_importer` / `omni.kit.window.file_importer` 는 `omni.ui`·`filepicker`
의존 GUI 확장이므로 배치 스크립트에서 쓰지 말 것.

### 4-3b. 【치명적 함정】 알파 컷아웃 — 놓치면 모든 나무가 판때기가 된다

**[로컬검증]** RTX 는 UsdPreviewSurface 를 만나면 네이티브 MDL 구현으로 인스턴스화한다
(`omni/mdl/rtx/UsdPreviewSurface*.mdl` 5종 동봉). 실제 컷아웃 로직:
```mdl
line 359:  uniform bool  enable_opacity   = false
line 376:  uniform float opacityThreshold = 0.0        // 기본 0
line 430:  float cutout_opacity = (enable_opacity && (opacityThreshold > opacity)) ? 0.0 : 1.0;
```
→ **컷아웃이 발동하려면 `enable_opacity == true` AND `opacityThreshold > 0` 이어야 한다.**
기본값이 0.0 이므로 아무것도 안 하면 **마스킹이 전혀 적용되지 않는다.**
**[웹검증]** OpenUSD 스펙 동일: https://openusd.org/release/spec_usdpreviewsurface.html

| 재질 타입 | 설정 |
|---|---|
| **UsdPreviewSurface** (외부 임포트 산출) | `inputs:opacity` → 텍스처 알파 연결 + **`inputs:opacityThreshold = 0.5`** |
| **MDL OmniPBR** (직접 작성) | `enable_opacity=True`, `enable_opacity_texture=True`, `opacity_texture=<알파맵>`, `opacity_mode=mono_alpha`, **`opacity_threshold=0.5`** |
| 렌더 설정 | 부분 투명 필요 시 `/rtx/{raytracing,pathtracing}/fractionalCutoutOpacity` |

> **§4-1b 의 NVIDIA 나무 44종을 로드했을 때 잎이 불투명 사각형이면 원인은 100% 이것이다.**

### 4-3c. UsdPreviewSurface 는 RTX 에서 제대로 렌더되는가 — **된다**

**[웹검증]** Omniverse 재질 문서: *"Materials in Omniverse are supported using MDL,
and MaterialX using an MDL backend."* → MDL 이 유일한 실행 백엔드이고
UsdPreviewSurface·MaterialX 는 모두 MDL 로 내려간다. 별도 변환 불필요.

- **정확히 재현**: baseColor / metallic / roughness / normal / occlusion / emissive / opacity / clearcoat
  → **지면·콘크리트·아스팔트·보도블록·식생 등 우리 소재는 전부 표준 PBR 이므로 충분하다.**
- **손실**: SSS, thin-film, anisotropy, sheen, 정확한 유리 굴절, 다층 코팅
  → 필요하면(§3-3 잎 SSS) **임포트 후 MDL 로 재바인딩**.

### 4-3d. Blender 4.5 → USD — Z-up·미터가 그대로 맞는 최적 경로. 단 함정 1개

**[로컬검증]** `Blender 4.5.4 LTS (2025-10-28)`. `bpy.ops.wm.usd_export` 프로퍼티 전량 introspection 확인.

**결정적 이점**: Blender 네이티브 **Z-up + METERS/1.0** 이 Isaac Sim 기본
(`apps/isaacsim.exp.base.kit:250` `app.stage.upAxis = "Z"`)과 **정확히 일치** → 축·단위 변환 불필요.

**최대 함정 [로컬검증]**: **`export_textures` 기본값이 `False`** — 끄면 텍스처가 Blender 원본
경로를 참조해 Isaac Sim 에서 전부 깨진다.

**[로컬검증]** 스톡 Blender 4.5 에는 **MDL export 옵션이 없다**(프로퍼티 전체에 `mdl` 문자열 전무).
→ Blender 산출물은 **UsdPreviewSurface(+선택적 MaterialX)** 뿐이며, 위 4-3c 에 따라 우리 소재에는 충분.

```bash
/home/vislab/blender-4.5.4-linux-x64/blender --background scene.blend --python-expr "
import bpy
bpy.ops.wm.usd_export(
    filepath='/abs/out/scene.usd',
    selected_objects_only=False, visible_objects_only=True, evaluation_mode='RENDER',
    export_meshes=True, export_normals=True, export_uvmaps=True, export_mesh_colors=True,
    export_subdivision='TESSELLATE',    # RTX subdiv 비용 회피 — 미리 굽기
    use_instancing=True,                # 나무 대량 배치에 필수
    export_curves=False, export_points=False, export_volumes=False, export_hair=False,
    export_materials=True, generate_preview_surface=True, generate_materialx_network=False,
    export_textures=True,               # 기본 False! 반드시 True
    export_textures_mode='NEW', overwrite_textures=True, relative_paths=True,
    convert_world_material=False,
    convert_orientation=False, convert_scene_units='METERS', meters_per_unit=1.0,
    root_prim_path='/World', xform_op_mode='TRS', merge_parent_xform=True,
    export_custom_properties=False, author_blender_name=False,
    export_animation=False, export_armatures=False, export_shapekeys=False,
    export_lights=False, export_cameras=False)
"
```

**역방향 팁 [로컬검증 — 옵션 존재 확인, 동작 미검증]**: NVIDIA USD(Rivermark, Vegetation)를
Blender 로 열 때 `mtl_purpose` 기본값 `MTL_FULL` 은 MDL 바인딩을 우선 선택하는데
**Blender 는 MDL 을 읽지 못한다** → `bpy.ops.wm.usd_import(..., mtl_purpose='MTL_PREVIEW')`.

### 4-3e. MaterialX — 인프라는 있으나 신뢰도 미검증

**[로컬검증]** `extscache/omni.materialx.libs-1.0.6` = **MaterialX 1.38.9 + OpenPBR**.
`libMaterialXGenMdl.so`(MaterialX → MDL 코드 생성기)가 렌더 메커니즘.
USD 플러그인 등록 확인(`UsdMtlxFileFormat`, `libhdMtlx.so`, `libusdBakeMtlx.so`).
**그러나** `omni/materialx/libs/tests/rtx.py` 의 `MtlxRenderTestRtx` 본문이 `pass` 로 비어 있다
→ 4.5 시점 테스트 커버리지 사실상 0. **[추정] MaterialX 로 오는 에셋은 UsdPreviewSurface
또는 MDL 로 재바인딩하는 편이 안전하다.**

### 4-3f. 임포트 실무 함정 체크리스트

| 항목 | 4.5 기준 | 조치 |
|---|---|---|
| metersPerUnit | Isaac 1.0(m). FBX/OBJ 는 대개 cm | 컨버터 `use_meter_as_world_unit=True` |
| up-axis | Isaac Z-up. glTF/FBX 는 Y-up. Blender 는 Z-up(일치) | `convert_stage_up_z=True` + `convert_fbx_to_z_up=True` |
| **텍스처 경로** | Blender `export_textures=False` 기본 | `export_textures=True, mode='NEW', relative_paths=True` |
| **알파 컷아웃** | `opacityThreshold` 기본 0.0 = 마스킹 없음 | §4-3b |
| 노멀맵 그린채널 | MDL/UPS 모두 **OpenGL(Y+)**. Substance/UE 출력(DirectX)은 뒤집힘 | OpenGL 로 굽거나 G 반전. Blender→USD 는 안전 |
| 인스턴싱 | Blender `use_instancing=False` 기본 → 나무 수백 그루가 전부 유니크 메시 | `use_instancing=True` |
| 서브디비전 | RTX subdiv 렌더 비용 큼 | Blender `export_subdivision='TESSELLATE'` |
| 루트 프림 | Isaac 관례 `/World`, Blender 기본 `/root` | `root_prim_path='/World'` |
| 텍스처 VRAM | 4090 24GB | §3-7 스트리밍/밉 제한 |

### 4-3g. 【간과된 발견】 `isaacsim.replicator.scene_blox` — 절차적 씬 생성기

**[로컬검증]** `…/isaacsim/exts/isaacsim.replicator.scene_blox/` (v1.0.2, **기본 활성**).
Wave-Function-Collapse 계열 **타일 기반 절차 씬 생성기**. YAML 로 타일 인접규칙·제약을 정의.
warehouse / labyrinth 프리셋 포함:
```bash
python tools/scene_blox/src/scene_blox/generate_scene.py <out_folder> \
  --grid_config .../parameters/warehouse/tile_config.yaml \
  --generation_config .../parameters/warehouse/tile_generation.yaml \
  --constraints_config .../parameters/warehouse/constraints.yaml \
  --cols 15 --rows 11 --variants 1 --units_in_meters 1.0 --collisions
```
→ 타일 정의를 실외(보도·연석·계단참·도랑·난간)로 교체하면 낙차 씬을 대량 절차 생성할 수 있다.
**[로컬검증]** 다만 진입 스크립트 `tools/scene_blox/` 는 **pip 휠에 없고 라이브러리만 있다**
(standalone 배포본에 존재). **[추정]** 우리는 이미 자체 USD 스크립팅이 성숙해서
도입 필요성은 중간 — 다만 "33씬을 손으로 쓰는" 현 구조의 대안으로 검토 가치가 있다.

### 4-4. 그 외 설치된 변환기

**[로컬검증]** `…/isaacsim/extscache/` 목록:
```
omni.kit.asset_converter-2.8.3          OBJ / glTF / FBX ↔ USD
omni.kit.converter.cad-202.2.0          CAD
omni.kit.converter.hoops-504.4.3        HOOPS (CATIA/SolidWorks/NX 등)
omni.kit.converter.jt-503.2.2           Siemens JT
omni.kit.converter.dgn-503.3.1          Bentley MicroStation DGN
omni.importer.onshape-0.8.1             Onshape
isaacsim.asset.importer.urdf-2.3.10     URDF (로봇)
isaacsim.asset.importer.mjcf-2.3.3      MuJoCo MJCF
isaacsim.asset.importer.heightmap       하이트맵 → 블록 월드
omni.kit.tool.asset_importer-2.12.2     임포터 UI
omni.materialx.libs-1.0.6               MaterialX 라이브러리
omni.mdl.usd_converter-1.0.24           MDL ↔ USD
```
**[로컬검증]** `omni.materialx.libs` 가 있으므로 **MaterialX 도 어느 정도 경로가 있다**.
다만 RTX 가 MaterialX 셰이딩 그래프를 네이티브로 렌더하는지는 **[미검증]**.
외부 CC0 에셋 상당수가 MaterialX 를 함께 배포하므로 확인 가치가 있다.

---

## §5. 무료/CC0 에셋 소스

NVIDIA 카탈로그(§4-1, §4-1b)가 도시 인공물·사람·나무를 채워주지만,
**한국 특유 요소·재질 다양성·라이선스가 깨끗한 공개 배포용 에셋**은 외부에서 와야 한다.

### 5-0. 결론 3줄

1. **Poly Haven 과 ambientCG 는 USD 를 네이티브로 제공한다** — 변환 0. 그리고 **CC0**.
2. **Poly Haven 은 "AI 학습 허용"을 공식 FAQ 에 명시** — 우리 프로젝트에 법적으로 가장 안전한 1순위.
3. **Quixel Megascans 는 쓰면 안 된다** — 무료분이 2.3K 로 줄었고, 확인한 Megascans 자산이
   **전부 `Allows usage with AI: No`(NoAI 태그)** 다.

### 5-1. 【1순위】 Poly Haven — CC0 + 네이티브 USD + AI 학습 명시 허용

**[웹검증 — API 직접 호출, 2026-07-28 실측]** `https://api.polyhaven.com` (키 불필요, 고유 UA 헤더 필요)

| 엔드포인트 | 용도 |
|---|---|
| `GET /types` | `["hdris","textures","models"]` |
| `GET /assets?t=hdris\|textures\|models` | 전체 목록 + 메타데이터 |
| `GET /files/{id}` | **다운로드 URL + md5 + size + 의존 텍스처 목록** |

**실측 자산 수**: HDRI **980** / Texture **786** / Model **521**

**USD 직접 제공 — YES [웹검증]**: 모델 12개 전수 확인 시 **12/12 가 `usd` 키 보유**(1k/2k/4k/8k),
식생 40개 샘플도 **40/40**.
```
Model  파일 키: usd, fbx, gltf, blend  (각 1k/2k/4k/8k)
Texture 키: Diffuse, nor_dx, nor_gl, Displacement, Rough, AO, arm, rough_ao
          + blend / gltf / mtlx(MaterialX)   (jpg/png/exr)
HDRI  키: hdri → 1k/2k/4k/8k/16k, hdr + exr 양쪽
```

**Isaac Sim 적합성 — [웹검증: `fir_tree_01` 실제 다운로드 후 pxr 로 검사]**
- **Z-up, metersPerUnit=1.0** → Isaac Sim 기본과 정확히 일치, 변환 불필요
- 재질 = **UsdPreviewSurface** (RTX 완전 지원, §4-3c)
- **`opacity` 입력이 알파 텍스처에 이미 CONNECTED** → 알파 컷아웃 잎이 그대로 동작
- MaterialX 노드그래프 동시 포함, 78개 모델이 LOD 제공

**라이선스 [웹검증]** — https://docs.polyhaven.com/en/faq :
> "We release all our assets under the CC0 license… which allows you to do whatever you want
>  with them, **including training AI models**."

→ **AI 학습 명시적 허용. 데이터셋 공개까지 고려하면 이게 가장 안전한 소스다.**

**HDRI 시간대·기상 분류 [웹검증 — 프로그래매틱 집계]**

| 카테고리 | 수 |
|---|---|
| natural light 807 / outdoor 691 / nature 522 / **urban 492** | |
| morning-afternoon 326 / partly cloudy 320 / **skies 295** | |
| clear 235 / sunrise-sunset 218 / midday 203 / **overcast 130** | |
| **pure skies 59** / night 59 | |
| 교차: outdoor+urban 206, outdoor+overcast 120, **urban+overcast 51** | |

> **한국 씬을 위한 실전 팁**: 한국 HDRI 는 없다(중국 5, 일본 1). 그러나 **pure skies 59개**는
> 하늘만 있어 지리적 특징이 전혀 없다 → 한국 씬에 지리적으로 중립.
> 시간대 분포: 부분흐림 28 / 일출일몰 28 / 맑음 26 / 아침오후 15 / 정오 11 / **흐림 8** / 밤 5.
> **우리가 이미 쓰는 `qwantani_noon_puresky`, `kloofendal_overcast` 가 전부 이 세트라 방향은 이미 옳다.**
> 여기에 §6-2 NVIDIA 물리 하늘을 더하면 조명 변주 축이 사실상 무한해진다.

**식생 모델 113개** (nature 110 / plants 57 / rocks 37 / ground cover 32 / **trees 20** / grass 4)
- **폴리곤 주의 [웹검증]**: `pine_tree_01` **17.4M tri**, `pine_sapling_medium` 9.8M,
  `fir_tree_01` 7.9M (26.7×6.5×19.3 m). **Isaac Sim 투입 전 데시메이션/인스턴싱 필수.**
- 관목·잔디는 훨씬 가볍다: `shrub_03` 17K, `fern_02` 6.2K, `shrub_sorrel_01` 3.3K
- 알파맵 보유율 29/40

**보도·도시 텍스처**: floor 259, terrain 129, brick 104, concrete 79, cobblestone 36,
road 36, paving 31, asphalt 20, bark 23
- **`anti_slip_concrete`** — 설명 원문 *"weathered anti-slip concrete with **raised tactile dots**"*
  → **점자블록 유사 표면. CC0 라 알베도 노란 틴트만 하면 된다.**
- `anti_skid_tiles`(돌출 스터드), `brick_crosswalk`, `concrete_pavers_02/03`(인터록킹)

**도시 소품 모델**: `street_lamp_01/02`, `concrete_road_barrier_01/02`,
`modular_chainlink_fence`, `water_manhole_cover`, `metal_trash_can`, `modular_street_seating`,
`fire_hydrant`, `modular_electricity_poles`, **`modular_fire_escape`(계단!)**, `painted_wooden_bench`

```bash
curl -H "User-Agent: NegObs/1.0" "https://api.polyhaven.com/files/fir_tree_01" \
  | jq -r '.usd["4k"].usd.url'
# → https://dl.polyhaven.org/file/ph-assets/Models/usd/4k/fir_tree_01/fir_tree_01_4k.usdc
# .usd[res].usd.include 에 필요 텍스처 URL/크기/md5 전부 포함
```
> **우리 `assets/download_assets.py` 가 이미 이 API 를 쓰고 있다 → 모델(USD) 지원만 추가하면 된다.**

### 5-2. 【2순위】 ambientCG — CC0, zip 안에 `.usdc` 동봉, 잎 아틀라스 38종

**[웹검증 — API 직접 호출]** `https://ambientcg.com/api/v2/full_json` (키 불필요)
```bash
curl "https://ambientcg.com/api/v2/full_json?id=PavingStones151&include=downloadData"
curl -L -o m.zip "https://ambientcg.com/get?file=Ground037_1K-JPG.zip"
```

**실측 총 2,872개**: Material **2004** / HDRI **416** / Substance 209 / Decal **126** /
**Atlas 60** / 3DModel 34 / Terrain 5. 최신 릴리스 2026-07-22 — 매우 활발.

**zip 안에 `.usdc` [웹검증 — 실제 압축 해제 확인]**:
```
Ground037_1K-JPG.usdc                  ← USD
Ground037_1K-JPG_Color.jpg
Ground037_1K-JPG_Displacement.jpg      ← 변위맵 (Mesh 정점 변위용, §2-4)
Ground037_1K-JPG_NormalDX.jpg / _NormalGL.jpg   ← 양쪽 규약 제공
Ground037_1K-JPG_Roughness.jpg / _AmbientOcclusion.jpg
Ground037_1K-JPG.mtlx                  ← MaterialX
```
해상도 1K / 2K / 4K / 8K / 12K (JPG·PNG). 12K-PNG 는 2.4 GB.

**잎 알파 아틀라스 [웹검증]** — **`LeafSet001~030`(30종) + `Foliage001~008`(8종)** + `PineNeedles001`
zip 내용: `_Color.png / _Opacity.png / _NormalDX / _NormalGL / _Displacement / _Roughness / .usdc / .mtlx`
→ **CC0 알파 컷아웃 잎 카드가 USD 까지 붙어서 즉시 사용 가능.**
§2-5 PointInstancer 의 크로스플레인 프로토타입을 여기서 만든다.

**우리 씬 관련**: Paving Stones **155** / Tiles 164 / Ground 121 / Road Lines 69 /
Concrete 61 / Asphalt 46 / Gravel 44 / Road 31 / Sign 26 / Snow 23
**Decal 126종** — §3-5 데칼 파이프라인의 소재.
**Terrain 5종** — 500m×500m×200m, OBJ + EXR 하이트맵(2K~8K).

**라이선스 [웹검증]**: CC0 1.0 (https://ambientcg.com/license), 크레딧 불필요.

### 5-3. 【쓰지 말 것】 Fab / Quixel Megascans — NoAI 태그

**[웹검증 — Fab EULA 전문 + 리스팅 페이지 실측]**

- 2024년 "전원 무료" 프로모션 **종료**. 무료로 남은 것은 **2.3K개**
  (3D 1.6K: Nature&Plants 461 / Materials 492 / Decals 204).
- 포맷은 좋다: `UEFN, fbx, glb, usdz, gltf` — **USDZ 제공 = USD 변환 난이도 0**
- **(a) Unreal 밖 사용**: 명시적으로 **가능** ("usage is not limited to Unreal Engine")
- **(c) 재배포**: 단독 재배포 금지. 단 §4(b) 는 **렌더링된 이미지 배포를 명시적으로 허용**
- **(b) ML 학습**: ⚠️ **NoAI 태그 자산은 금지**. §6(b)(vii):
  > use NoAI Content (i) in datasets utilized by Generative AI Programs; (ii) in the development
  > of Generative AI Programs; or (iii) as training inputs to Generative AI Programs.
- §16(l)(i) 정의에 예외가 있다:
  > Programs do not meet this definition … where they … **(b) generate tags to classify visual
  > input content**; or (c) generate instructions to arrange existing content, without creating new content.

**결정적 [웹검증 — 리스팅 실측]**: 확인한 Megascans 자산이 **전부 `Allows usage with AI: No`**
(Forest Terrain, European Beech 등). 반면 **CC-BY 4.0 자산은 `Allows usage with AI: Yes`** —
Epic 정책상 **CC-BY 에는 NoAI 태그를 붙일 수 없다**
(https://dev.epicgames.com/documentation/fab/licenses-and-pricing-in-fab).

> **판단**: U-Net 낙차 추정은 "새 콘텐츠 생성"이 아니라 dense 분류/회귀이므로
> §16(l)(i)(b) 예외를 **주장할 여지는 있다.** 그러나 image-to-image 출력이라 회색지대이고,
> **논문 공개까지 가는 프로젝트에서 이 리스크를 질 이유가 없다.**
> → **Fab 을 쓴다면 CC-BY 필터로만** (AI 허용 보장 + 재배포 가능 + usdz).
>   Fab UI 좌측 "Licenses" 패싯 사용 — **URL 쿼리 파라미터로는 필터가 안 걸린다**(실측).

### 5-4. Sketchfab — 살아있지만 CC0 풀이 얕다

**[웹검증]** sketchfab.com 정상 운영, 무료 다운로드 티어 유지, Fab 으로 이관되지 않음.
`is_ai=0/1` AI생성 필터 신설. Data API v3 작동(키 불필요):
```bash
curl "https://api.sketchfab.com/v3/search?type=models&downloadable=true&licenses=cc0&q=tree&count=24"
```
- 라이선스 파라미터는 uid 가 아니라 **slug**: `cc0, by, by-sa, by-nd, by-nc, …`
- `totalCount` 필드 없음 — `next` 커서 페이지네이션 필요

**CC0 다운로드 가능 실측**: tree 109, park 55, stairs 11, bench 5, curb 1, fence 1
— **bollard / handrail / streetlight / bus stop / guardrail / manhole / traffic sign 전부 0**
그나마 tree 109 도 박물관 스캔(개구리·그림)이 상위.
> **냉정한 평가: Sketchfab CC0 로 포토리얼 식생·가로시설물 조달은 불가능.**

### 5-5. 저폴리 CC0 — 전부 부적합 (확인 완료)

| 소스 | 실측 | 판정 |
|---|---|---|
| **Poly Pizza** | 10,600+ 무료. API 키 필요 | ❌ 명시적으로 low-poly 전용 |
| **Quaternius** | CC0 확인, 크레딧 불필요 | ❌ 저폴리 스타일 |
| **Kenney** | 14페이지 팩 | ❌ 저폴리/스타일라이즈드 |

**추가 CC0 텍스처 소스 [웹검증]**: **cgbookcase.com**(566개, CC0 1.0),
**sharetextures.com**(CC0 텍스처+모델+아틀라스), **texture.ninja**(퍼블릭도메인).

### 5-6. 식생 — 소스별 정리

| 도구 | 라이선스 | 포맷 | 알파 잎카드 | 판정 |
|---|---|---|---|---|
| **NVIDIA `Assets/Vegetation`** (§4-1b) | Omniverse License | **네이티브 USD** | 확인 필요 | 🥇 **나무 44 + 관목 37 + 잎클러스터 5 + 낙엽 5** |
| **Poly Haven** 나무 20 / 식물 57 / 지피 32 | **CC0, AI학습 명시 허용** | **네이티브 USD** | 29/40 | 🥇 **공개 배포 안전** |
| **ambientCG** LeafSet 30 + Foliage 8 | **CC0** | usdc + Opacity PNG | 전용 채널 | 🥇 **크로스플레인 제작용** |
| **Sapling Tree Gen** v0.3.7 | GPL-3.0 무료 | Blender | 직접 준비 | 🥈 **⚠️ 아래 정정** |
| Modular Tree v5.5.2 / IvyGen / Scatter Objects | GPL 무료 | Blender | 직접 준비 | 🥈 절차적 |
| **BlenderKit** 무료티어 | Royalty Free 또는 CC0 | Blender | 자산별 | 🥈 CC0 서브셋만 |
| **SpeedTree** | **무료 티어 없음**, Indie $19/월 | FBX/OBJ/ABC/USD | O | 부적합 |
| **The Grove 3D** | 유료. ⚠️ **무료 프리뷰 출력물은 written consent 없이 사용 불가** | Blender | O | 부적합 |
| Tree It | 무료, **Windows 전용** | fbx/obj | 불명확 | 보조 |
| Arbaro | GPL-2.0, ★17 | — | X | 사실상 사장 |

**중요 정정 [로컬검증]**: **Sapling Tree Gen 은 Blender 4.5 에 기본 탑재돼 있지 않다.**
`/home/vislab/blender-4.5.4-linux-x64` 의 `addons_core` 에는 15개만 있고 `add_curve_sapling` 이 없다
(4.2+ 에서 레거시 애드온이 Extensions 플랫폼으로 이전). 설치:
```bash
# Sapling Tree Gen v0.3.7, GPL-3.0, 최소 Blender 4.4.0
wget https://extensions.blender.org/download/sha256:27a478262e1c86612a9c3daffe7f4dce2802f5bc2294033462e5adc6d9c0080f/add-on-sapling-tree-gen-v0.3.7.zip
```

**학술/CC0 나무 모델 세트는 없다 [웹검증 — negative]**: HuggingFace·Zenodo 조사 결과
렌더링 가능한 3D 나무 에셋 세트 없음(생태 GIS·포인트클라우드뿐). **이 경로는 포기.**

**실전 권고 [추정]**
1. **원거리 배경 나무** → NVIDIA `Assets/Vegetation/Trees` 44종 (또는 Poly Haven CC0 20종 + 데시메이션)
2. **중거리 관목/잔디** → Poly Haven 관목(3K~50K tri, 가벼움) + NVIDIA `Shrub` 37종, 인스턴싱
3. **근거리·대량 잎** → **ambientCG LeafSet/Foliage 아틀라스로 크로스플레인 카드 제작 → PointInstancer**
   (가장 저렴하고 CC0 라 가장 안전)
4. **수종 다양화** → Sapling Tree Gen + 위 아틀라스

### 5-7. 사람 / 차량

**[웹검증]** **Mixamo — 2026년에도 무료** (https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html)
> "Mixamo is available free for anyone with an Adobe ID and does not require a subscription."
> "You can use both characters and animations **royalty free for personal, commercial, and
>  non-profit projects**."
이족보행 휴머노이드 전용. 종료 공지 없음.
**[로컬검증]** **이미 이 머신에 있다** — `/home/vislab/Desktop/Isaac_assets/mixamo_com.usda`
(SkelAnimation, Z-up), `testmovingpeople.usd`.

**[웹검증]** RenderPeople 무료 샘플 페이지 존재하나 개수·조항이 로그인 벽 뒤 — **미검증**.
**[미검증]** MakeHuman 출력물 라이선스, SMPL/SMPL-X 조항, BEDLAM/AGORA 배포 여부,
SimReady 차량 목록, 한국 차량(현대/기아) 무료 모델 유무.

> **권고 [추정]**: 우리 용도는 **5~30 m 거리의 스케일 앵커**다.
> **NVIDIA `People/`(§4-1) 20종 + 의상변형 220 + 애니메이션 24** 로 이미 충분하고,
> Mixamo 가 이미 파이프라인에 있으므로 보강도 쉽다.
> **한국 차량은 의장권/상표 리스크가 있어 논문 공개용으로는 오히려 피하는 편이 낫다.**

### 5-8. 지리공간 3D + 한국 데이터

#### 최대 수확: NGII 정밀도로지도 = 실측 3D 연석 데이터
**[웹검증]** https://map.ngii.go.kr/ms/pblictn/preciseRoadMap.do
공식 정의에 **`도로경계선`(연석선), `중앙분리대`, 노면표시를 3차원으로 제작**한다고 명시.
**"민·관 기관, 기업 무상 제공"**. 전국 고속국도·지방도 + **판교제로시티·세종 행복도시 +
자율주행 시범지구 ~40곳**.
- 벡터(SHP 계열)는 **로그인 + 실명인증** 후 다운로드
- 로그인 없이: `curl -o las_index.zip "https://map.ngii.go.kr/static/download/ms/pblictn/preciseRoadMap/las_index.zip"` (HTTP 200)
- **라이선스**: 공공누리 **제1유형**(상업·2차저작 허용, **출처표시 필수**) —
  단 **공공누리 마크가 실제로 붙은 자료에 한함**, 공간정보는 별도 법령 적용.
  → 다운로드 시 마크 확인, 없으면 **사전 협의 서면 확보 권장**.

#### V-World 3D 는 다운로드 불가 [웹검증]
총 737개 중 3D 72개가 **전부 "지도조회"(뷰어 전용)**. 3차원 시설물 LoD1/3/4, 정밀도로지도 모두 불가.
- **대안 수확**: `GIS건물통합정보`(SHP, 건축물대장 속성 결합, 갱신 2026-07-27) —
  **한국판 OSM 푸트프린트지만 훨씬 정확**. `연속지적도형정보`(EPSG:5186)도 옹벽/단차 사전정보로 유용.

#### Google Photorealistic 3D Tiles — **절대 사용 금지 (4중 차단)** [웹검증]
1. Map Tiles API policies: *"You may not use Map Tiles API for any non-visualization use cases,
   such as: Image analysis · Machine interpretation · **Object detection** · Geodata extraction · **Offline uses**"*
2. Maps Platform Terms §3.2.3(c)(vii): *"**use Google Maps Content to improve machine learning
   and artificial intelligence models, including to train, test, validate or fine-tune the models**"*
   금지. **연구/학술 예외 없음**
3. §3.2.3(a)/(b) 스크래핑·캐싱 금지 (USD 변환 = 영구 저장)
4. 오버레이 허용 조항조차 *"3D objects aren't extracted, traced, or otherwise derived …
   from Photorealistic 3D Tiles"* 단서
> **회색지대가 아니라 명백한 금지다. Blosm 의 Google 3D Tiles 경로도 켜지 말 것.**

#### 사용 가능한 지리 도구 [웹검증]
- **Blosm**(구 blender-osm) — 무료판 존재(€0 pay-what-you-want), `bl_info` = Blender **4.5.0 타깃**,
  2026-06-26 푸시, GPL. 무료판 = 무텍스처 건물 + 지형 + 도로 커브.
  ⚠️ **도로가 평평한 리본 커브라 연석 단면이 없다** — 낙차 지오메트리는 직접 저작해야 함.
- **BlenderGIS** — v2.2.15(2025-12-20), ★9,221, GPL-3.0, Blender 2.83~5.x.
  **GeoTIFF DEM + SHP 네이티브 임포트** → 한국 정부 데이터 투입 경로로 최적.
- **Cesium OSM Buildings** — 3.5억 건물, ODbL, 벌크 다운로드 없음(ion 스트리밍) → Blosm 과 중복, 스킵.

**⚠️ OSM ODbL 주의 [웹검증]**: 렌더링된 **이미지/라벨은 "Produced Work"** 라 자유 배포 가능.
그러나 **OSM 파생 USD/메시 씬 파일을 함께 공개하면** Derivative Database 가 되어 ODbL 전염 +
§4.6 에 따라 원본 DB 공개 의무 발생. → **이미지+라벨만 배포하고 씬 파일은 신중히.**

### 5-9. 스캔 데이터셋 — 1개만 쓸모 있다

#### 【중요】 SANPO (Google Research) — CC-BY 4.0, 우리 연구와 어휘가 겹친다
**[웹검증]** https://google-research-datasets.github.io/sanpo_dataset/ (WACV 2025)
- **(S)cene understanding, (A)ccessibility, (N)avigation, (P)athfinding, (O)bstacle avoidance**
  — *"outdoor scenes from **urban, park, and suburban** settings"*
- 라이선스 원문: *"**You are free to share and adapt this data for any purpose**"*
  → **CC-BY 4.0, 등록·서명·클릭랩 전부 불필요**
- **31 클래스 중**: `road`, **`curb`**, `sidewalk`, `guard rail`, `crosswalk`, **`hand rail`**,
  **`stairs`**, **`inaccessible surface`**, `other walkable surface`, `bus stop`, `pole`, `traffic sign`…
  → **우리 연구의 낙차 어휘가 이미 정의·주석되어 있다. 스키마를 그대로 채택할 수 있다.**
- 내용: **1인칭 시점**(눈높이·가슴높이) 스테레오 영상, SANPO-Real + **SANPO-Synthetic 113K 프레임**,
  dense depth(CREstereo) + sparse depth, 카메라 포즈, 시간일관 panoptic 세그멘테이션
- ⚠️ 2025-06-05 변경: **`fixed_camera_poses.csv` 를 쓸 것**(원본 포즈는 좌표계 불일치)
```bash
gcloud storage rsync gs://gresearch/sanpo_dataset/v0 . --recursive \
  --exclude=".*/right|.*/zed_depth_maps"
```
> **활용법**: 3D 씬이 아니라 2D 영상이라 Isaac Sim 에 못 넣는다. 대신
> **(a) 31클래스 택소노미 채택 → WACV 벤치마크와 직접 비교 가능,
> (b) SANPO-Real 을 sim2real 검증 세트로.** CC-BY 라 그림·수치 공개 자유.
> **합성데이터 논문에 정확히 필요한 조각이다.**

#### 실내 씬 데이터셋 6종 — 전부 부적합 [웹검증]

| 데이터셋 | 실외 | 계단 | 파생물 공개 |
|---|---|---|---|
| ScanNet | 없음 | 드묾 | 비상업 연구, 수령자 동의 필요 |
| ScanNet++ | 없음 | 드묾 | *"Sharing the data otherwise is **strictly prohibited**"* |
| Matterport3D | 없음 | 계단실 있음 | 클릭랩 + 수령자 기록 의무. **"Derived Information"에 학습된 모델 가중치까지 포함** |
| HM3D | 없음 | 있음 | 동일 |
| Replica | 실내 18 | 없음 | 비상업, 수령자 사전동의 |
| 3D-FRONT | 없음 | 없음 | HF 미러가 cc-by-nc-4.0, 원본 404 |

> **결론: 전부 실내 + 전부 재배포 제약. 이 카테고리는 통째로 시간 낭비.
> 한국식 계단/연석은 절차 생성하거나 Blender 로 만드는 게 빠르고 공개도 자유롭다.**

#### GSO (Google Scanned Objects) — 라이선스는 깨끗하나 무용
**[웹검증]** `X-Total-Count: 1033`, **CC-BY 4.0**, Gazebo Fuel 서비스 중(2026-07-27 갱신), SDF+OBJ.
❌ **1,033개 전부 탁상용 소비재**(신발·장난감·주방용품). 실외 가치 ~2/10.

#### Objaverse — 유일하게 쓸 만한 오브젝트 데이터셋 (6/10)
**[웹검증]** 1.0 ~800K / XL 10M+ (단 **2023-10-31 이후 갱신 없음**).
라이선스 분포: **CC-BY 721K**, CC-BY-NC-SA 52K, CC-BY-NC 25K, CC-BY-SA 16K, **CC0 3.5K**.
데이터셋 자체는 ODC-By 1.0.
**필터 필드는 `license`, 값은 짧은 슬러그** — `"CC-BY 4.0"` 같은 문자열로 필터하면 **조용히 0건**:
```python
PERMISSIVE = {"cc0", "by"}
lvis = objaverse.load_lvis_annotations()
uids = [u for c in ["bench","trash_can","streetlight","fire_hydrant","bollard"]
        for u in lvis.get(c, [])]
ann = objaverse.load_annotations(uids)
clean = [u for u, m in ann.items() if m["license"] in PERMISSIVE]
paths = objaverse.load_objects(uids=clean)
```
- 큐레이션 서브셋: **Objaverse-LVIS**(~46K, 1,156 카테고리, 사람 검증) +
  **Objaverse++**(2025, arXiv 2504.07334, `cindyxl/ObjaversePlusPlus`) — 사람이 매긴 품질 라벨
- **[로컬검증] 이 머신의 체크아웃에 버그가 있다**: `/media/vislab/ssd1_4tb1/objaverse-xl/` 의
  HEAD 가 `objaverse/xl/thingiverse.py` 를 삭제했는데 `__init__.py` 는 여전히 임포트
  → **`import objaverse.xl` 가 ModuleNotFoundError 로 죽는다.** `pip install objaverse` 재설치 필요.
- 품질 현실: **20~50개 봐야 1개 건진다.**

### 5-10. 한국 가로시설물 — 절차 생성이 사실상 유일한 길

**[웹검증 — negative]** Sketchfab CC0 에 볼라드·난간·점자블록 **0건**.
NVIDIA 카탈로그도 미국식(§4-1). 한국 3D 에셋 커뮤니티에서도 확보 경로를 찾지 못했다.

**[미검증 — 남은 공백]** law.go.kr 이 JS 렌더링 + DRF API 가 OC 키를 요구해
**점자블록 KS 치수(300×300 mm 로 알려짐), 볼라드 설치기준, 계단 챌판/디딤판 규격을
직접 검증하지 못했다.** 브라우저 또는 law.go.kr OC 키 발급 후
「장애인·노인·임산부 등의 편의증진 보장에 관한 법률 시행규칙 별표」와
「보도 설치 및 관리 지침」을 확인해야 한다.

**부분 위안**: Poly Haven `anti_slip_concrete` 가 *"raised tactile dots"* 표면이라
**CC0 로 점자블록 알베도(노란 틴트)에 바로 전용 가능**하다.
→ **점자블록은 지오메트리보다 텍스처 문제라는 우리 가정이 맞다.**
우리는 이미 `build_tactile()` 과 `assets/signs/gen_signs.py` 로 절차 생성 경로를 갖고 있으므로,
**치수 검증 + 텍스처 품질 향상**이 실질 과제다.

### 5-11. 실제로 쓸 소스 TOP 8 (순위 + 첫 액션)

| # | 소스 | 이유 | **첫 액션** |
|---|---|---|---|
| **1** | **NVIDIA `Assets/Vegetation` + `Assets/Isaac/4.5`** (§4-1, §4-1b) | 12,689 + 나무 44 + 관목 37 + 사람 20 + 가로시설 265종. 인증 불필요 HTTPS | `curl` 로 `Japanese_Cherry.usd` 1개 받아 Isaac Sim RT 렌더 1장 → **알파 컷아웃 확인**(§4-3b) |
| **2** | **Poly Haven** | CC0 + **AI학습 명시 허용** + **네이티브 USD**(Z-up/미터/UPS/알파 연결). 변환 0 | `assets/download_assets.py` 에 **models+USD 지원 추가**. `shrub_01~04`, `fern_02` 등 저폴리부터 |
| **3** | **ambientCG** | CC0, zip 에 `.usdc` 동봉, Displacement, **LeafSet 30 + Foliage 8 + Decal 126** | `curl -L -o LeafSet014_2K-PNG.zip "https://ambientcg.com/get?file=LeafSet014_2K-PNG.zip"` → 크로스플레인 잎 카드 프로토타입 1개 |
| **4** | **SANPO (CC-BY 4.0)** | 실외 urban/park, **curb·stairs·hand rail·inaccessible surface 클래스 기정의**, 재배포 자유 | `labelmap.json` 받아 **31클래스 택소노미를 우리 GT 스키마에 매핑**. SANPO-Real 을 sim2real 검증셋으로 |
| **5** | **PhysicalAI-SimReady-Materials (MIT-0)** | 재질 1,705종, **법적으로 완전 자유**. Concrete/Ground/Masonry | `curl -s https://api.github.com/repos/NVIDIA-Omniverse/PhysicalAI-SimReady-Materials/releases/latest` |
| **6** | **NGII 정밀도로지도** | **실측 3D 도로경계선(연석)**, 판교/세종, 무상 | 회원가입+실명인증 → 판교제로시티 벡터 신청. **동시에 공공누리 마크 확인 / 사전협의** |
| **7** | **Blender 무료 트리 툴체인** | Sapling(GPL) + Modular Tree + Scatter Objects | **Sapling 이 4.5 에 없다는 점 유의** — v0.3.7 zip 설치 후 ambientCG LeafSet 으로 텍스처링 |
| **8** | **Objaverse-LVIS + Objaverse++** | 가로시설물 소품 대량 소스 | **로컬 `thingiverse` 임포트 버그 수정** → `license ∈ {'cc0','by'}` + 품질라벨로 200개 추출 후 육안 검수 |

**제외 권고**:
🚫 **Megascans**(NoAI) · 🚫 **Google 3D Tiles**(ToS 4중 위반) ·
🚫 ScanNet/ScanNet++/Matterport3D/HM3D/Replica/3D-FRONT(실내+재배포 제약) ·
🚫 GSO(탁상 잡화) · ⚠️ Poly Pizza/Quaternius/Kenney(저폴리) · ⚠️ Cesium OSM Buildings(중복)

---

## §6. 하늘·조명 고도화

여기가 **투입 대비 회수율이 가장 높은 영역**이다. 우리는 HDRI 2장으로 33개 씬 전부를 조명하고 있고,
태양 원반 문제를 numpy 로 손수 고쳤는데, **그 문제를 위한 정식 해법이 3개 존재한다.**

### 6-1. `ensure_noon_lookfix()` 는 필요 없었다 — 태양 원반 문제의 정식 해법

우리 코드 `scene_common.py:1077-1131` 은 EXR 을 numpy 로 읽어 태양 원반(각반경 1.5°)을
서컴솔라 링 p90 휘도로 클램프하고 지평 아래를 리프트한다. 그 이유는 "RTX 돔 샘플링의 태양 블러"였다.

**정식 해법 [로컬검증]** — `omni.rtx.settings.core-0.6.3` 의 툴팁이 그대로 처방이다:
```
/rtx/domeLight/upperLowerStrategy
   0 = Image-Based Lighting                ← "고주파 돔 텍스처에도 가장 정확"
   4 = Approximated Image-Based Lighting   ← "저주파 텍스처 전용. 태양 원반이 없고
                                              태양은 별도 DistantLight 인 하늘에 적합"
   3 = Environment Mapped IBL              ← 반사/굴절 전용. 가장 빠르고 부정확
/rtx/domeLight/baking/resolution   16…8192   (★ 돔 소스가 MDL 일 때만 적용)
```

3가지 선택지:
- **(A) `upperLowerStrategy = 0`** — HDRI 원본을 그대로 쓰고 고주파를 정확히 샘플링.
  1줄. `ensure_noon_lookfix()` 전체를 삭제할 수 있는지 실험 1회로 확인 가능.
- **(B) HDRI 에서 태양 제거 + `DistantLight(angle=0.53°)` 분리 + `upperLowerStrategy = 4`**
  — NVIDIA 권장 패턴. 우리가 이미 절반은 하고 있다(DistantLight 를 이미 씀). lookfix 의
  "태양 캡"을 "태양 완전 제거"로 바꾸면 되고, 오히려 지금보다 단순해진다.
- **(C) 절차적 물리 하늘로 전환** — 아래 §6-2. HDRI 자체를 버린다.

> **주의 [로컬검증]**: `baking/resolution` 은 **돔 소스가 MDL 일 때만** 적용된다.
> 일반 `.hdr`/`.exr` 파일 텍스처에는 영향이 없다. 우리가 손으로 고쳐야 했던 이유가 바로 이것일 수 있다.
> → 즉 (A) 또는 (B) 가 실질 해법이다.

### 6-2. 절차적 물리 하늘 — **2가지가 이미 설치돼 있다**

#### (i) Hosek-Wilkie 하늘 MDL — 로컬 탑재

**[로컬검증]** `…/site-packages/omni/mdl/rtx/nvidia/iray/hosek_wilkie_sky.mdl:367+`
함수 `sun_and_sky`, 파라미터:
```
turbidity (1~10, 기본 2)          ← 대기 혼탁도 = 헤이즈/미세먼지. 한국 대기질 재현 가능
ground_albedo (0.5)
sun_direction (float3)            ← 방위·고도 직접 지정
sun_disk_scale                    ← ★ 태양 원반 크기 직접 제어
sun_disk_intensity_multiplier     ← ★ 태양 원반 밝기 직접 제어
sky_intensity_multiplier
horizon_height, horizon_blur (0.1)
mode (0=raw 1=total 2=sun_sky)
illuminance_total (100000 lux), illuminance_sun (80000), illuminance_sky (20000)
y_is_up (true)                    ← ★ 우리는 Z-up 이므로 False 로 둘 것
```
**HDRI 없이 실측 lux 단위의 태양+하늘을 생성한다.** 우리가 손으로 하던 태양 캡/헤이즈 리프트를
`sun_disk_scale` / `turbidity` 파라미터로 직접, 물리적으로 제어할 수 있다.
관련 모듈: `omni/mdl/rtx/iray/environment.mdl`, `usd_dome.mdl` **[로컬검증]**

#### (ii) NVIDIA Dynamic Sky USD — 평문 HTTPS 로 공개, **6종 프리셋 확인**

**[웹검증 — HTTP 200 직접 확인]**
```
https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Skies/2022_1/Skies/Dynamic/
    ClearSky.usd  CumulusLight.usd  CumulusHeavy.usd  Cirrus.usd  Overcast.usd  NightSky.usd
https://…/Skies/Sky_Elements/SphereInverseLow.usd                        (200)
https://…/Skies/Sky_Elements/materials/procedural/CumulusLight.mdl        (200)
```
**[로컬검증]** 확장 `omni.kit.environment.core-1.3.15` 가 설치돼 있고, 그 `extension.toml:44` 에
동일 URL 계열이 하드코딩돼 있다. API:
```python
# omni/kit/environment/core/sky/sky_helper.py:120-155
SkyHelper.create_dynamic_sky(url)     # 또는 커맨드 "CreateDynamicSkyCommand"
SkyHelper.create_hdri_sky(url)        #        "CreateHdriSkyCommand"
```

**내부 구조 [웹검증 — 파일 직접 다운로드해 확인]**:
`CumulusLight.usd` 를 열어보면 다음으로 구성된다.
- 최상위 `World` Xform 에 **`Latitude`(51.426) / `Longitude`(-0.985) / `NorthOrientation` /
  `DayOfYear`(100) / `TimeOfDay`(6.93)** 속성
- 이 값들이 `AxisNorth → AxisLatitude → AxisSHA(태양시각) → AxisDeclination` 변환 체인을 구동하고
  그 끝에 `DistantLight (angle=1, intensity=5000, ShapingAPI)` 가 달려 있다
  → **위경도·절기·시각으로 태양이 천문학적으로 배치된다**
- 반경 10000 의 역구(`SphereInverseLow.usd`)에 `ProceduralSky::ProceduralSky` MDL 바인딩
- 하늘 MDL 파라미터(직접 확인):
  ```
  [대기]  HorizonGlow, SkySaturation, SkyTint, SunSaturation, SunTint,
          haze, sun_disk_intensity, sun_disk_scale, sun_glow_intensity
  [적운]  CumulusEnabled, CloudAltitude, CloudCoverage, CloudDensity*, CloudHeight,
          CumulusLevels(6), CumulusBaseShaper, CloudScaleExp …
  [권운]  CirrusEnabled, CirrusAltitude, CirrusCoverage, CirrusDensity, CirrusLevels …
  [포그]  CloudAmbientFog, CloudFogDensityExp, CloudFogEnabled …
  [좌표]  Latitude, Longitude, NorthOrientation, DayOfYear, TimeOfDay,
          SunPositionFromTOD(bool), TimeOfDaySpeed, Azimuth, Elevation, Declination, SHA
  ```
- USD 레벨 settings: `SunIntensity`(5000), `SunColorA/B/C`(고도별), `DomeColorA/B/C`,
  `AmbientColor*`, **`FogColorA/B/C`, `FogDensityA/B`, `FogFactorDistance`, `FogFactorHeight`,
  `FogElevationA/B`**

**우리에게 무엇을 주는가:**
- **시간대 변주가 파라미터 2개**(`TimeOfDay`, `DayOfYear`)로 된다. HDRI 를 시간대별로 모을 필요가 없다.
- **한국 위경도**(서울 37.57N / 126.98E)로 설정하면 태양 고도·방위가 실제와 일치한다.
  → 우리 씬의 그림자 방향이 "한국 어느 계절 몇 시"인지 논문에 적을 수 있다. **sim2real 주장의 근거가 된다.**
- **구름 6종**(맑음/약한적운/강한적운/권운/흐림/야간)이 도메인 랜덤화 축이 된다.
- 현재 본편 21씬이 **정오 맑음 단일 조건**인 문제를 근본적으로 푼다.

**도입 비용: 낮~중.** `Dynamic/*.usd` 를 로컬에 받아(§4 방식) 참조하고 5개 속성만 세팅하면 된다.
**리스크**: `metersPerUnit=0.01` 로 저작돼 있어 우리 미터 스테이지와 스케일 정합이 필요하다
**[웹검증 — 파일 헤더 직접 확인]**. 참조 프림에 스케일 100 을 주거나 `UsdGeom` 단위 변환 필요.

### 6-3. Sun Study (위경도/날짜/시각 슬라이더) — 설치돼 있으나 **Isaac 앱에서 비활성**

**[로컬검증]** `omni/kit/environment/core/sunstudy_player/player.py`, `core/constants.py:19-21`
```
USD 속성:  /Environment.location:latitude
           /Environment.location:longitude
           /Environment.location:north_orientation
carb 설정: /persistent/app/stage/northOrientation
Player:    latitude, longitude, north_orientation,
           current_time, start_time, end_time, current_date, start(), stop()
```
**[로컬검증]** `grep "omni.kit.environment" isaacsim/apps/*.kit` → **히트 0**.
즉 Isaac Sim 의 `.kit` 앱 정의에서 이 확장이 켜져 있지 않다. 수동 활성화가 필요하다:
```python
import omni.kit.app
omni.kit.app.get_app().get_extension_manager().set_extension_enabled_immediate(
    "omni.kit.environment.core", True)
```
**[미검증]** — headless standalone 에서 이 확장이 정상 동작하는지는 확인하지 않았다.

### 6-4. `UsdLux` — 6종 중 2종만 쓰는 중

**[로컬검증]** Replicator 가 공식 지원하는 라이트 타입
(`…/omni/replicator/core/scripts/create.py:1478`):
```python
["cylinder", "disk", "distant", "dome", "rect", "sphere"]
```
공통 속성: `inputs:color`, `inputs:intensity`, `inputs:exposure`,
`inputs:colorTemperature` + `inputs:enableColorTemperature`(1000~10000K), `inputs:texture:file`

우리는 `dome` + `distant` 만 쓴다. 미사용 중 유용한 것:

| 타입 | 우리 용도 | 사실성 기여 |
|---|---|---|
| `RectLight` | 지하도·주차장 천장 형광등, 상점 쇼윈도 | **상** — 실내 낙차 씬(D 계열)의 결정적 요소 |
| `SphereLight` | 가로등 구체, 볼라드 조명 | 중 |
| `DiskLight` | 다운라이트, 계단 벽면 조명 | 중 |
| `inputs:exposure` | 노출 스톱 단위 강도 제어 | 중 — intensity 를 손으로 튜닝하는 것보다 물리적 |
| `enableColorTemperature` | 나트륨등(2000K)·수은등(4000K)·LED(5000K) 구분 | **상** — 한국 가로등 색온도 재현 |
| `shaping:cone:angle` / `shaping:focus` | 스포트라이트 | 중 |
| `shaping:ies:file` | **IES 실측 광도분포** — `/rtx/directLighting/units/correctIES` 설정 존재 **[로컬검증]** | 상 (야간 씬 한정 → 우리 스코프 외) |

**[추정]** 주간 스코프에서는 RectLight(지하도·터널) + colorTemperature 두 개가 실질 이득이고,
IES/스포트는 야간 스코프 제외로 우선순위가 낮다.

### 6-5. 대기 산란 / 안개 — **완전 미사용, 야외 깊이감의 최대 무기**

**[로컬검증]** 3계층이 존재한다.

```
[1] 단순 안개 (RT/PT 공통, 가장 저렴)
/rtx/fog/enabled
/rtx/fog/fogColor, fogColorIntensity
/rtx/fog/fogDistanceDensity, fogStartDist, fogEndDist, fogDistanceBased/enabled
/rtx/fog/fogHeightDensity, fogHeightFalloff, fogStartHeight, fogZup/enabled   ← Z-up 필수!

[2] 체적 산란 (RT 모드, 복셀 기반)
/rtx/raytracing/globalVolumetricEffects/enabled                    ← 마스터
/rtx/raytracing/inscattering/atmosphereHeight, maxDistance, densityMult,
   anisotropyFactor, singleScatteringAlbedo, transmittanceColor,
   transmittanceMeasurementDistance, depthSlices(16~1024), pixelRatio(4~64),
   useDetailNoise, detailNoiseScale, noiseNumOctaves, …

[3] Rayleigh 물리 대기 (PT 전용, 가장 정확)
/rtx/pathtracing/ptvol/enabled
/rtx/pathtracing/ptvol/raySky            ← "Rayleigh Atmosphere"
/rtx/pathtracing/ptvol/raySkyScale, raySkyDomelight, maxBounces, transmittanceMethod
```

**우리 프로젝트에서의 의미**: 에어리얼 퍼스펙티브(멀수록 흐려지고 푸르게 뜨는 현상)는
**단안 깊이 추정의 강력한 단서**이고, 우리 U-Net 이 "이 낙차가 얼마나 먼가/깊은가"를
판단하는 데 직결된다. 현재 우리 렌더는 100 m 앞 건물도 3 m 앞 계단과 동일한 콘트라스트로
찍히는데, 실사진은 절대 그렇지 않다. **sim2real 갭의 정량적 원인 중 하나일 가능성이 높다 [추정].**

```python
# Z-up 스테이지 필수 설정 포함
s.set("/rtx/fog/enabled", True)
s.set("/rtx/fog/fogZup/enabled", True)              # ★ 우리는 Z-up
s.set("/rtx/fog/fogDistanceBased/enabled", True)
s.set("/rtx/fog/fogColor", (0.72, 0.78, 0.86))
s.set("/rtx/fog/fogColorIntensity", 1.0)
s.set("/rtx/fog/fogStartDist", 20.0)
s.set("/rtx/fog/fogEndDist", 400.0)
s.set("/rtx/fog/fogDistanceDensity", 0.35)
```
**도입 비용: 최저(설정 6줄).** **사실성 기여: 상.** **[추정] 즉시 적용 TOP 3 안에 든다.**

### 6-6. 렌더모드별 하늘·대기 기능 매트릭스

**[로컬검증]** RTX 설정 UI 스택 구성에서 도출
(`rt_widgets.py:236-251`, `pt_widgets.py:231-246`, `common_widgets.py:620-633`):

| 기능 | RaytracedLighting | PathTracing |
|---|---|---|
| SSS | ✅ `/rtx/raytracing/subsurface/*` | ✅ `maxVolumeBounces` |
| 코스틱스 | ✅ 포톤맵 | ❌ |
| DLSS / DLAA | ✅ | ❌ (PT 는 `aa/op` 샘플 패턴) |
| 체적 안개 | ✅ inscattering (복셀 근사) | ✅ ptvol (정확) |
| Rayleigh 물리 대기 | ❌ | ✅ `ptvol/raySky` |
| OptiX 디노이저 | ❌ | ✅ |
| 모션블러(포스트) | ✅ | ❌ (서브프레임 방식) |
| 적응 샘플링 | ❌ | ✅ |
| AO / IndirectDiffuse 근사 | ✅ | ❌ (실제 GI) |
| 포스트 전체(톤맵/블룸/DoF/그레인) | ✅ | ✅ 공통 |

→ **§9 의 "RT 로 데이터를 뽑아도 되나" 판단에 직결된다.** RT 는 GI 를 근사하지만
SSS·안개·포스트는 전부 지원한다. 빠지는 건 정확한 다중바운스 GI 와 Rayleigh 대기다.

---

## §7. 카메라·센서 사실성

우리는 카메라 **위치만** 옮기고 있다. 렌즈·노출·포스트를 하나도 안 쓴다.
이 영역은 **전부 carb 설정 몇 줄**이므로 비용 대비 회수가 극단적으로 좋다.

### 7-1. 물리 카메라 파라미터 — `UsdGeom.Camera` 로 직접 세팅

**[로컬검증]** `…/isaacsim/exts/isaacsim.sensors.camera/isaacsim/sensors/camera/camera.py:1070-1116`

```python
from pxr import UsdGeom
cam = UsdGeom.Camera.Define(stage, "/World/Cam")
cam.CreateFocalLengthAttr().Set(24.0)          # ★ 단위 주의 (아래)
cam.CreateHorizontalApertureAttr().Set(20.955) # 35mm 풀프레임 가로 = 36.0, APS-C ≈ 23.5
cam.CreateVerticalApertureAttr().Set(11.78)
cam.CreateFStopAttr().Set(2.8)                 # ★ 0.0 이면 DoF 꺼짐
cam.CreateFocusDistanceAttr().Set(5.0)         # 스테이지 단위 (우리는 m)
cam.CreateClippingRangeAttr().Set(Gf.Vec2f(0.05, 1000.0))
```

**단위 함정 [로컬검증]**: Isaac 래퍼 `Camera.set_focal_length(v)` 는 내부에서 **`v * 10`** 을 저장한다.
USD `focalLength` 는 "10분의 1 스테이지 단위" 관례를 쓴다. 즉 `set_focal_length(2.4)` → USD `24.0` → 24 mm.
USD 속성을 직접 쓸 때는 이 변환을 우리가 해야 한다.

**우리 프로젝트 관점의 중요성**: 우리는 TurtleBot3 Waffle Pi 를 보유하고 있고 실측 촬영이 가능하다.
**실물 카메라(Raspberry Pi Camera 계열)의 초점거리·센서 크기·FOV 를 USD 카메라에 정확히 옮기면
sim2real 갭의 기하학적 성분이 사라진다.** 이건 논문에서 방어 가능한 구체 조치이며 비용은 3줄이다.

### 7-2. 피사계심도(DoF) — **지원됨. 카메라 구동이 기본, 오버라이드도 가능**

**[로컬검증]** 패널명이 "Depth of Field **Camera Overrides**" 다:
```
/rtx/post/dof/enabled          ← 꺼지면 카메라 fStop 도 무시됨
/rtx/post/dof/overrideEnabled  ← 켜면 아래 값이 카메라 값을 덮어씀
/rtx/post/dof/subjectDistance
/rtx/post/dof/focalLength      (mm)
/rtx/post/dof/fNumber
/rtx/post/dof/anisotropy       (-1~1; -0.5 = 아나모픽 보케)
/rtx/post/dof/viewUIEnabled
```
→ **기본 경로는 USD 카메라가 DoF 를 구동하고**, `/rtx/post/dof/*` 는 그것을 덮어쓰는 오버라이드다.

**[미검증 — 실험 1회로 확정]**: PathTracing 에서 나오는 흐림이
(a) 실제 물리 렌즈 조리개 샘플링인지 (b) 포스트 처리 DoF 인지는 로컬 파일만으로 확정 못 했다.
Replicator 문서 문자열은 DoF 를 "PostProcess Render Settings" 로 분류한다 **[로컬검증]**.
→ **fStop=1.4 로 PT 1장 렌더하면 즉시 판별된다** (물리 조리개면 경계가 자연스럽고 하이라이트가
보케 모양을 띤다; 포스트면 깊이 경계에 헤일로가 생긴다).

**우리 프로젝트에서의 판단 [추정]**:
- DoF 는 **양날의 검**이다. 사실성은 올라가지만 **낙차 단서가 있는 원경(난간·수관·차 지붕)을
  흐리게 만들면 라벨-이미지 정합이 나빠질 수 있다.**
- 로봇 카메라는 대개 심도가 깊다(작은 센서 + 큰 f값). **실물 TurtleBot 카메라 f값을 그대로 쓰면
  DoF 는 거의 안 생기고, 그게 오히려 sim2real 정합에 맞다.**
- → **강한 DoF 는 "논문 그림용"으로만, 데이터셋에는 실물 f값 그대로.** 다만 소량(5~10%)
  DoF 변주를 도메인 랜덤화 축으로 넣는 건 유효하다.

### 7-3. 모션블러 — **정적 캡처에서는 나오지 않는다 (확정)**

**[로컬검증]**
```
/rtx/post/motionblur/enabled, maxBlurDiameterFraction(0~0.5), exposureFraction, numSamples(4~32)
```
Replicator 설정 문서 문자열이 **"Motion Blur (RealTime render mode)"** 로 명시하고,
`settings.py:284-285` 에:
```
/omni/replicator/captureMotionBlur
    RealTime  → /rtx/post/motionblur/enabled 와 동일
    PathTrace → 타임스텝을 N 개 서브프레임으로 분할
/omni/replicator/pathTracedMotionBlurSubSamples
```
→ **실제 시간축 모션(트랜스폼 타임샘플)이 있어야 한다.**

**우리에게 필요한가? [추정] — 필요하다, 그러나 우선순위는 중간.**
로봇 주행 중 촬영한 실사진에는 반드시 모션블러가 있다. 이걸 학습 데이터에 넣지 않으면
sim2real 에서 블러가 도메인 시프트로 작용한다. 다만 구현 비용이 있다(카메라에 타임샘플 궤적을 부여).
**대안 [추정]**: Replicator 의 후처리 augmentation(§8) 으로 방향성 블러를 GPU 커널로 걸면
훨씬 싸다. 물리적으로는 덜 정확하지만 학습 데이터로는 충분할 가능성이 높다.

### 7-4. 렌즈 왜곡 / 어안 — **LUT 방식만 지원**

**[로컬검증]**
```
/rtx/post/lensDistortion/distortionMap        ← 텍스처(LUT)
/rtx/post/lensDistortion/undistortionMap
/rtx/post/lensDistortion/lensFocalLengthArray
/rtx/fishEye/useCubemap
```
→ **계수(k1,k2,p1,p2) 직접 입력이 아니라 왜곡 맵 텍스처 방식이다.**
OpenCV 로 실물 카메라를 캘리브레이션해서 왜곡 맵을 생성한 뒤 텍스처로 넣는 흐름이 된다.

**[추정] 우리 판단**: TurtleBot 카메라의 왜곡을 재현하는 건 이상적이지만, 더 싸고 확실한 길은
**학습 파이프라인에서 실사진 쪽을 언디스토트**하거나 **Replicator augmentation 으로 왜곡을 추가**하는 것이다.
렌더 단계에서 할 이유가 약하다. 우선순위 하.

### 7-5. 포스트 이펙트 — 검증된 설정 키 전량

**[로컬검증]** 전부 `omni.rtx.settings.core-0.6.3` 위젯 소스에서 추출.

#### 톤매핑 (⚠️ 흔히 인용되는 `cameraFStop`/`cameraISO` 는 **106.5 에 없다**)
```
/rtx/post/tonemap/op          0=Clamp 1=Linear(Off) 2=Reinhard 3=ModifiedReinhard
                              4=HejlHableAlu 5=HableUc2 6=Aces 7=Iray     ← ACES = 6
/rtx/post/tonemap/filmIso           (50~1600)
/rtx/post/tonemap/exposureTime      (초, 0~2)   ← "Camera Exposure"
/rtx/post/tonemap/fNumber           (1~20)
/rtx/post/tonemap/whitepoint        (color3)
/rtx/post/tonemap/colorMode         0=sRGBLinear 1=ACEScg
/rtx/post/tonemap/dither            (0~0.02) — 밴딩 제거
/rtx/post/tonemap/enableSrgbToGamma, wrapValue, cm2Factor, whiteScale, maxWhiteLuminance
/rtx/post/tonemap/irayReinhard/{crushBlacks,burnHighlights,…}   (op=7 일 때)
```

#### 자동 노출 (⚠️ 데이터셋 생성에는 **꺼야 한다**)
```
/rtx/post/histogram/enabled, filterType(0=Median 1=Average), tau(0.5~10),
   whiteScale(0.01~80; 낮을수록 밝음), useExposureClamping, minEV, maxEV, minloglum, loglumrange
```
**[추정]** 켜두면 프레임마다 노출이 흔들려 **라벨-이미지 일관성이 깨진다.**
도메인 랜덤화로 노출을 흔들고 싶다면 자동 노출이 아니라 `filmIso`/`exposureTime` 을
명시적 분포로 샘플링해야 재현 가능하다.

#### 블룸 = **FFT Bloom**. `/rtx/post/bloom/*` 는 **존재하지 않는다**
```
/rtx/post/lensFlares/enabled, flareScale, cutoffPoint(double3), cutoffFuzziness,
   alphaExposureScale, energyConstrainingBlend, physicalSettings(bool)
 physicalSettings=1 → apertureShapeCircular, blades(3~10), apertureRotation,
    sensorDiagonal, sensorAspectRatio, fNumber, focalLength,
    noiseStrength, dustStrength, scratchStrength,
    spectralBlurSamples, spectralBlurIntensity, spectralBlurWavelengthRange
 physicalSettings=0 → haloFlareRadius/Falloff/Weight, anisoFlareFalloffX/Y,
    anisoFlareWeight, isotropicFlareFalloff/Weight
```
> `dustStrength`/`scratchStrength` 는 **렌즈 오염**을 시뮬레이션한다.
> 실외 로봇 카메라는 항상 먼지가 있다 — sim2real 에 직접적이다 **[추정]**.

#### 비네팅 / 필름그레인 = `/rtx/post/tvNoise/*`
```
/rtx/post/tvNoise/enabled              ← 마스터 (켜야 아래가 동작)
   enableVignetting, vignettingSize(0~255), vignettingStrength(0~2), enableVignettingFlickering
   enableFilmGrain, grainAmount(0~0.2), colorAmount(0~1), lumAmount(0~1), grainSize(1.5~2.5)
   enableScanlines/scanlineSpread, enableScrollBug, enableGhostFlickering,
   enableWaveDistortion, enableVerticalLines, enableRandomSplotches   ← 전부 끌 것(TV 노이즈 연출용)
```

#### 색수차
```
/rtx/post/chromaticAberration/{enabled, strengthR/G/B(-1~1), modeR/G/B(0=Radial 1=Barrel),
   enableLanczos, mirroredRepeat, boundaryBlendRegionSize, boundaryBlendFalloff}
```

#### 색보정 / 컬러그레이딩
```
/rtx/post/colorcorr/{enabled, mode(0=ACES Pre-Tonemap 1=Standard Post),
   outputMode(0=sRGBLinear 1=ACEScg), saturation, contrast, gamma, gain, offset}   (전부 color3)
/rtx/post/colorgrad/{enabled, mode, outputMode, blackpoint, whitepoint, contrast,
   lift, gain, multiply, offset, gamma}
```
→ **화이트밸런스 변주를 여기서 만들 수 있다.** 실물 카메라의 AWB 편차는 sim2real 도메인 시프트의
큰 축인데, `colorcorr/gain` 을 색온도 분포로 샘플링하면 재현 가능하다 **[추정]**.

#### AA (⚠️ 우리 설정이 최적이 아니다)
```
/rtx/post/aa/op          3 = DLSS,  4 = DLAA
/rtx/post/dlss/execMode  0=Performance 1=Balanced 2=Quality 3=Auto
```
**우리는 `aa/op=3`(DLSS) + `dlss/execMode=2`(Quality) 를 쓴다** (`scene_common.py:188-189`).
**DLSS 는 저해상도에서 렌더해 업스케일한다.** 1920×1080 최종 산출물을 오프라인으로 뽑는 상황에서
업스케일할 이유가 없다. **`aa/op=4`(DLAA) 가 네이티브 해상도로 AA 만 수행하므로 화질이 명확히 우월하다.**

```python
s.set("/rtx/post/aa/op", 4)      # DLAA — 1줄, 화질 즉시 상승
```
**[추정]** 속도는 DLSS Quality 대비 다소 느려지겠지만(네이티브 해상도 셰이딩), RT 1.12 s/컷 →
1.4~1.8 s/컷 수준일 것으로 본다. **[반드시 실측할 것.]**
데이터셋 대량 생성 단계에서 속도가 중요해지면 그때 DLSS 로 되돌리면 된다.

### 7-6. 오프라인 렌더에서 반드시 끌 것

```python
s.set("/rtx/ecoMode/enabled", False)          # 유휴 시 렌더 품질을 떨어뜨림 [로컬검증]
s.set("/rtx/post/histogram/enabled", False)   # 자동 노출 → 프레임간 불일치
```

### 7-7. 종합 — 카메라·센서 "오늘 바로" 스니펫

```python
import carb.settings
s = carb.settings.get_settings()

# --- 화질 ---
s.set("/rtx/post/aa/op", 4)                              # DLAA (기존 3=DLSS)
s.set("/rtx/ecoMode/enabled", False)

# --- 톤매핑 (물리 노출, 자동노출 OFF) ---
s.set("/rtx/post/tonemap/op", 6)                         # ACES
s.set("/rtx/post/tonemap/colorMode", 0)                  # sRGBLinear
s.set("/rtx/post/tonemap/filmIso", 100.0)
s.set("/rtx/post/tonemap/exposureTime", 1.0/500.0)       # 주간 야외
s.set("/rtx/post/tonemap/fNumber", 8.0)
s.set("/rtx/post/tonemap/dither", 0.004)
s.set("/rtx/post/histogram/enabled", False)

# --- 렌즈 사실성 (약하게) ---
s.set("/rtx/post/tvNoise/enabled", True)
s.set("/rtx/post/tvNoise/enableFilmGrain", True)
s.set("/rtx/post/tvNoise/grainAmount", 0.02)
s.set("/rtx/post/tvNoise/enableVignetting", True)
s.set("/rtx/post/tvNoise/vignettingStrength", 0.35)
for k in ("enableScanlines","enableScrollBug","enableGhostFlickering",
          "enableWaveDistortion","enableVerticalLines","enableRandomSplotches",
          "enableVignettingFlickering"):
    s.set(f"/rtx/post/tvNoise/{k}", False)               # ★ TV 연출 항목 전부 OFF

s.set("/rtx/post/chromaticAberration/enabled", True)
for c in "RGB":
    s.set(f"/rtx/post/chromaticAberration/strength{c}", 0.0015 * (1 if c!="G" else 0))
    s.set(f"/rtx/post/chromaticAberration/mode{c}", 0)   # Radial

s.set("/rtx/post/lensFlares/enabled", True)
s.set("/rtx/post/lensFlares/physicalSettings", True)
s.set("/rtx/post/lensFlares/blades", 7)
s.set("/rtx/post/lensFlares/fNumber", 8.0)
s.set("/rtx/post/lensFlares/dustStrength", 0.15)         # 실외 로봇 카메라 = 항상 먼지
s.set("/rtx/post/lensFlares/flareScale", 0.4)            # 과하지 않게

# --- 대기 (§6-5) ---
s.set("/rtx/fog/enabled", True)
s.set("/rtx/fog/fogZup/enabled", True)
s.set("/rtx/fog/fogDistanceBased/enabled", True)
s.set("/rtx/fog/fogColor", (0.72, 0.78, 0.86))
s.set("/rtx/fog/fogStartDist", 20.0); s.set("/rtx/fog/fogEndDist", 400.0)
s.set("/rtx/fog/fogDistanceDensity", 0.35)
```
**총 비용: 40줄. 사실성 기여: 상.** 이것만으로도 "렌더 티"의 상당 부분이 사라진다 **[추정]**.

---

## §8. Replicator

**우리는 Replicator 를 0% 쓰고 있다.** 캡처는 `capture_viewport_to_file` + 수동 `sim_app.update()`
루프이고, annotator·writer·랜덤화·GT 파이프라인이 전부 없다. 그런데 **GT 낙차 맵과 대량 생성은
Replicator 없이는 사실상 불가능하다.** 이 절이 본 조사에서 실행 우선순위가 가장 높다.

로컬 버전 **[로컬검증]**: `omni.replicator.core-1.11.35+106.5.0.lx64.r.cp310`
(standalone 사본과 **바이트 동일** — md5 대조 확인).

### 8-0. 【최대 발견】 우리 572회 update 루프는 약 70배 낭비다

**[로컬검증]** `…/omni/replicator/core/scripts/orchestrator.py:312-330`
```python
return total_spp // max(1, spp)      # 누적에 필요한 프레임 수
```
`/rtx/pathtracing/spp` **기본값이 1**, `/rtx/pathtracing/totalSpp` 기본값이 512다.
즉 **프레임당 1샘플씩 512프레임을 누적**하는 구조이고, 우리 `warm=572` 는 이 512 + 여유였다.

**spp 를 올리면 필요 프레임이 그만큼 줄어든다.**
```python
rep.settings.carb_settings("/rtx/pathtracing/spp", 16)      # 프레임당 16샘플 (유효 1~32)
rep.settings.set_render_pathtraced(samples_per_pixel=64)    # totalSpp=64 → 누적 4프레임
rep.orchestrator.step(rt_subframes=8, delta_time=0.0)       # 572 → 8
```
⚠️ **`set_render_pathtraced(samples_per_pixel=N)` 은 `/rtx/rendermode` 와 `/rtx/pathtracing/totalSpp`
딱 2개만 쓴다. `spp` 는 건드리지 않으므로 carb 으로 직접 설정해야 한다**
**[로컬검증]** `settings.py:363-375`.

**[웹검증]** NVIDIA 공식 권고도 같은 방향:
Replicator + PT 일 때 totalSpp 를 512가 아니라 **16 정도로 낮추라**, 안 그러면
"서브프레임에 더해 각 프레임을 과다샘플링해서 매우 오래 걸린다".
https://docs.omniverse.nvidia.com/extensions/latest/ext_replicator/subframes_examples.html
그리고 OptiX 디노이저는 켜둘 것 — "목표 화질 대비 렌더 시간을 **한 자릿수 배수**로 줄인다".
https://docs.omniverse.nvidia.com/materials-and-rendering/latest/rtx-renderer_pt.html

> **주의**: `rt_subframes=N` 은 PT 샘플 설정을 **전혀 건드리지 않는다.** 타임라인을 얼린 채
> `app.update()` 를 N번 돌리고 **N번째에만 캡처**한다 — 즉 우리 수동 루프와 기능적으로 동일하되
> **캡처/랜덤화 동기화가 보장된다**. **[로컬검증]** `orchestrator.py:406-422`.
> 이 차이는 재질/돔 변경 직후 캡처 시 **덜 로드된 프레임을 잡는 사고**를 막아준다.

### 8-1. 【함정】 헤드리스 SDG 프레임 유실

**[웹검증]** `isaacsim.core.throttling` 확장이 타임라인 정지 시 `/app/asyncRendering=True` 를 켜는데
Replicator 는 STARTED 상태로 남아 되돌리지 않는다 → **스케줄된 프레임이 조용히 유실된다.**
NVIDIA 4.5 known issues 등재 항목. 공식 해결 플래그:
```bash
--/exts/isaacsim.core.throttling/enable_async=false
```
https://docs.isaacsim.omniverse.nvidia.com/latest/replicator_tutorials/troubleshooting.html

### 8-2. 기존 저작 프림 랜덤화 — **된다. 공식 예제 패턴 존재**

우리 씬은 Replicator 가 만든 게 아니라 자체 USD 스크립트가 프림을 Define 한다.
이게 가장 큰 걱정거리였는데, 4.5.0 에 정확히 그 예제가 있다.
**[로컬검증]** `…/isaacsim/exts/isaacsim.replicator.examples/…/tests/test_sdg_ur10_palletizing.py:368,387,391`

```python
bins_node = rep.get.prim_at_path(bin_paths)          # 이미 저작된 프림 경로 리스트
with rep.trigger.on_frame():
    with bins_node:
        rep.randomizer.materials(mats)

pallet_node = rep.get.prim_at_path(PALLET_MESH_PATH)
with rep.trigger.on_frame(interval=4):
    with pallet_node:
        rep.randomizer.texture(texture_paths, texture_rotate=rep.distribution.uniform(80, 95))
        rep.modify.pose(...)
```

**`rep.get.prims` 실측 시그니처 [로컬검증]** (`get.py:53`):
```python
rep.get.prims(path_pattern=None,          # 정규식
              path_match=None,            # 단순 문자열 매칭 — 정규식보다 빠름
              path_pattern_exclusion=None,
              prim_types=None, prim_types_exclusion=None,
              semantics=None, semantics_exclusion=None,     # [("class","ground")]
              cache_result=True,          # ★ 주의
              ignore_case=True, name=None)
rep.get.prim_at_path(path, name=None)     # str | List[str] | ReplicatorItem
```
⚠️ **`cache_result=True` 가 기본**이다. 씬을 교체하며 같은 그래프를 재사용하려면 `False` 로 두거나
씬마다 그래프를 다시 만들어야 한다.
타입별 편의 함수: `get.camera / light / material / mesh / shape / xform / renderproduct / …`

### 8-3. 랜덤화 API 전수 (4.5.0 실측)

**`rep.randomizer` — 빌트인 정확히 7개 [로컬검증]** (`randomizer.py`)

| 함수 | 시그니처 |
|---|---|
| `scatter_2d` | `(surface_prims, no_coll_prims=None, min_samp, max_samp, seed=None, offset=0, check_for_collisions=False, input_prims=None, name=None)` |
| `scatter_3d` | `(volume_prims=None, no_coll_prims=None, volume_excl_prims=None, min_samp, max_samp, resolution_scaling=1.0, voxel_size=0.0, check_for_collisions=False, prevent_vol_overlap=True, …)` |
| `materials` | `(materials, seed=None, max_cached_materials=0, input_prims=None, name=None)` |
| `instantiate` | `(paths, size, weights=None, mode="scene_instance", with_replacements=True, seed=None, name=None, use_cache=True, semantics=None)` |
| `rotation` | `(min_angle=(-180.,)*3, max_angle=(180.,)*3, seed=None, input_prims=None)` |
| `texture` | `(textures, texture_scale=None, texture_rotate=None, per_sub_mesh=False, project_uvw=False, seed=None, input_prims=None)` |
| `color` | `(colors, per_sub_mesh=False, seed=None, input_prims=None)` |

`rep.randomizer.register(fn, override=True, fn_name=None)` 으로 커스텀 등록 가능.
**`rep.randomizer.light()` 는 없다** — 조명 랜덤화는 `rep.create.light(...)` 인자에 distribution 을
직접 넣거나 기존 조명을 `rep.get.prims` 로 잡아 `rep.modify.attribute()` 로 바꾼다.

> **성능 노트 (소스 docstring 원문)**: *"binding materials is a relatively expensive operation.
> It is generally more efficient to modify materials already bound to prims."*
> → **5만 장 규모에서는 `randomizer.materials()` 보다 `modify.attribute()` 로
> 이미 바인딩된 재질 파라미터를 흔드는 게 유리하다.**

**`rep.distribution` — 6개 전부 존재 [로컬검증]**
```python
uniform(lower, upper, num_samples=1, seed=None, name=None)
sequence(items, ordered=True, seed=-1, name=None)
normal(mean, std, num_samples=1, seed=None, name=None)
choice(choices, weights=None, num_samples=1, seed=-1, with_replacements=True, name=None)
combine(distributions, name=None)
log_uniform(lower, upper, num_samples=1, seed=None, name=None)
```
> **`name=` 을 주면 샘플된 값이 Writer 페이로드로 전달된다** — 프레임별 랜덤화 파라미터를
> 메타데이터로 저장할 때 유용하다. **재현성·논문 부록용으로 반드시 쓸 것.**

**`rep.modify` 공개 함수 [로컬검증]** (`modify.py`)
```python
semantics(semantics=None, input_prims=None, mode="add")     # add|replace|clear
pose(position, position_x/y/z, rotation, rotation_x/y/z, rotation_order="XYZ",
     scale, size, pivot, look_at, look_at_up_axis, input_prims, name)
pose_camera_relative(...)   attribute(name, value, attribute_type=None, input_prims=None)
visibility(value=None, input_prims=None, name=None)   variant(...)   material(...)
timeline(...)  time(...)  animation(...)  projection_material(...)  pose_orbit(...)
```
`attribute()` 의 `attribute_type` 은 속성이 아직 없을 때 필수.

**`rep.create.light` 실측 [로컬검증]** (`create.py:1418`)
```python
rep.create.light(position=None, scale=None, rotation=None, look_at=None, look_at_up_axis=None,
                 light_type="Distant",       # cylinder|disk|distant|dome|rect|sphere
                 color=(1,1,1), intensity=1000.0, exposure=None, temperature=6500,
                 texture=None,               # ★ dome light HDRI 슬롯
                 count=1, name=None, parent=None)
```
intensity / temperature(1000~10000K) / color / exposure(2의 거듭제곱 배율) **전부 distribution 수용**.
HDRI 랜덤화는 `light_type="dome", texture=rep.distribution.choice(hdri_paths)`.

**`rep.create.camera` 실측 [로컬검증]** (`create.py:850`)
```python
rep.create.camera(position, rotation, look_at, look_at_up_axis,
                  focal_length=24.0, focus_distance=400.0, f_stop=0.0,
                  horizontal_aperture=20.955, horizontal_aperture_offset=0.0,
                  vertical_aperture_offset=0.0, clipping_range=(1.0, 1000000.0),
                  projection_type="pinhole",
                  fisheye_nominal_width/height, fisheye_optical_centre_x/y, fisheye_max_fov,
                  fisheye_polynomial_a..f, fisheye_p0/p1, fisheye_s0..s3,
                  count=1, parent=None, name=None)
```
**`f_stop=0.0` 이 기본이며 DOF 를 끈다** — 심도를 원하면 1.4~5.6.
`VALID_PROJECTIONS` 하드코딩 **[로컬검증]** (`create.py:944-951`):
`fisheyePolynomial, fisheyeSpherical, fisheyeKannalaBrandtK3, fisheyeRadTanThinPrism,
omniDirectionalStereo, pinhole` — **`orthographic` 은 없고 `ValueError` 가 난다.**

**`rep.trigger` [로컬검증]**
```python
on_frame(interval=1, num_frames=0, name="on_frame", rt_subframes=1, max_execs=0)
on_time(...)  on_time_end(...)     # ★ on_time_interval() 이라는 이름은 없다
on_custom_event(event_name)        # 발사: rep.utils.send_og_event(event_name)
on_condition(condition, max_execs=0, rt_subframes=1)
on_key_press(key, modifier=None, name=None)
```
`num_frames` 는 deprecated → `max_execs` 사용.

### 8-4. Semantics — **4.5 는 레거시 `Semantics.SemanticsAPI` 다**

**결론: `UsdSemantics.LabelsAPI` 가 아니다.** Kit 106.5 전체가 pxr `Semantics` 모듈을 쓴다.
**[로컬검증]** `ogn/python/_impl/nodes/OgnWriteSemantics.py:18,46`,
`scripts/utils/utils.py:1066,1716-1727`, `isaacsim/core/utils/semantics.py:17`
전환은 Isaac Sim **5.0 / Kit 107.3** 에서 일어났다(`add_update_semantics` → `add_labels`).

```python
# (a) USD 직접 — 우리 씬 스크립트가 프림 Define 직후 부르기 좋음
from isaacsim.core.utils.semantics import add_update_semantics
add_update_semantics(prim, semantic_label="ground", type_label="class", suffix="")
# ★ 4.5 에서는 프림당 라벨 1개만 (5.0부터 리스트)

# (b) Replicator 그래프 안에서
rep.modify.semantics(semantics=[("class","ground")], mode="add")   # add|replace|clear
```

⚠️ annotator 에 `semanticTypes=[...]` 를 넘기면 노드 속성이 아니라 **전역** instance-mapping
semantic filter 를 덮어쓴다(그리고 `carb.log_warn` 발생) **[로컬검증]** `annotators.py:426-449`.
`SemanticFilterPredicate` 클래스나 `rep.settings.set_semantic_filter_predicate` 는 **존재하지 않는다.**
실제 API 는 `SyntheticData.Get().set_instance_mapping_semantic_filter(predicate)` 이고
술어 문법은 `"typeA : labelA & !labelB | labelC , typeB: labelA ; typeC: labelD"` **[로컬검증]**.
Writer 레벨에서는 `BasicWriter(semantic_filter_predicate="class:*")`.

### 8-5. Annotator 전수 — 그리고 GT 낙차 맵

**이름 해석 규칙 [로컬검증]** (`annotators.py:1334-1357`): 유효 namespace 가 2개
(`AnnotatorRegistry._annotators` + `SyntheticData._ogn_templates_registry` 폴백)이고,
`get_registered_annotators()` 는 `hidden=False` 인 것만 반환한다 → **동작하지만 목록에 안 나오는
annotator 가 있다.**

| 이름 | 존재 | dtype / shape | 비고 |
|---|---|---|---|
| `rgb` / `LdrColor` | ○ | `(H,W,4) uint8` | |
| `HdrColor` | ○ | `(H,W,4) float16` | |
| `distance_to_camera` | ○ | `(H,W) float32` | **미터**, 무충돌 = inf/거대값 |
| `distance_to_image_plane` | ○ | `(H,W) float32` | **미터** |
| `DistanceToCamera`(대문자) | **X** | — | 미등록, 예외 발생 |
| `depth` / `Depth` | **X** | — | rendervar 일 뿐 annotator 아님 |
| `normals` | ○ | `(H,W,4) float32` | |
| `SmoothNormal` | ○ | `(H,W,4) float32` | **RT 모드 전용** |
| `motion_vectors` | ○ | `(H,W,4) float32` | |
| `semantic_segmentation` | ○ | `(H,W) uint32` + `info.idToLabels` | init `colorize=False` |
| `instance_segmentation` / `_fast` | ○ | `(H,W) uint32` + idToLabels/idToSemantics | |
| `instance_id_segmentation` | ○ (hidden) | `(H,W) uint32` | docstring: "개발/디버깅용" |
| `bounding_box_2d_tight` / `_loose` (+`_fast`) | ○ | structured + `occlusionRatio` | **GPU 불가** |
| `bounding_box_3d` / `_fast` / `_360` | ○ | structured + `transform (4,4)` | **GPU 불가** |
| `pointcloud` | ○ | `(N,3) float32` + normals/rgb/semantic/instance | |
| `camera_params` | ○ | **dict** | ★ 아래 |
| `occlusion` | ○ | 1-D structured `(instanceId, semanticId, occlusionRatio)` | |
| `cross_correspondence` | ○ | `(H,W,4) float32` | 양쪽 카메라 `fisheyePolynomial` 필요 |
| `skeleton_data` | ○ | dict (27 keys) | |
| `motion_blur` | **X** | — | annotator 아님(렌더 설정 + `MotionBlur` augmentation) |
| `Attribute` | ○ | 1-D flattened | init `prims: list`, `attribute: str` — **임의 USD 속성을 프레임마다 덤프** |
| PT 전용 AOV 21종 | ○ | 전부 `float16 ×4` | `PtDirectIllumation`(오타 그대로), `PtGlobalIllumination`, `PtWorldPos`, `PtZDepth`, `PtMultiMatte0..7` |

**`camera_params` 반환 키 [로컬검증]** (역투영에 필요한 전부):
`cameraViewTransform`(16), `cameraProjection`(16), `cameraFocalLength`, `cameraAperture`,
`cameraApertureOffset`, `cameraFStop`, `cameraFocusDistance`, `cameraNearFar`, `cameraModel`,
`metersPerSceneUnit`, `renderProductResolution` + fisheye 파라미터.

#### 【정정】 depth 의 "빈 픽셀" 값은 0 이 아니다

**[로컬검증]** 공식 문서 `annotators_details.rst:94-97` 은 "0이 무한대"라고 하지만 **stale 이다.**
동봉 테스트가 반증한다: `assert data.max() > 1000`, `data[data != np.inf].max()`
(`omni.syntheticdata/.../tests/sensors/test_distance_to_camera.py:73,195`).
단위는 스테이지 단위와 무관하게 **미터**다.
→ **마스킹은 `np.isinf(depth) | (depth >= depth.max())` 로. `depth == 0` 은 틀렸다.**

#### 【중요】 직교(orthographic) 카메라는 쓰면 안 된다

탑다운 직교 depth 로 heightmap 을 만드는 계획은 **폐기해야 한다.** 근거 4가지 **[로컬검증]**:
1. `rep.create.camera()` 가 `orthographic` 을 `ValueError` 로 거부 (`create.py:944-978`)
2. SDG 플러그인 바이너리에 하드 에러 문자열:
   `"OgnSdPostSemanticBoundingBox : unimplemented camera model (current supported models are
   PinHole and FisheyePolynomial)"` — **모든 `bounding_box_*` annotator 가 이 노드를 쓴다**
3. Python 투영 헬퍼 `get_view_params()` 가 `cameraProjectionType` 만 읽고 `UsdGeom.Camera.projection`
   은 안 읽는다 → **직교 카메라가 pinhole 로 위장되어 에러 없이 틀린 결과를 낸다** (`helpers.py:489,559-564`)
4. `Camera.set_projection_mode("orthographic")` 은 존재하나 **검증·경고가 없고 해당 테스트가 주석 처리**돼 있다
**[웹검증]** NVIDIA 직원도 4.5.0 포럼에서 기본 clipping range 로 직교가 깨진다고 확인, 티켓 오픈:
https://forums.developer.nvidia.com/t/orthographic-projection-fails-for-default-parameters/325868

#### GT 낙차 맵 — 구체적 레시피

직접적인 답: **기성 annotator 만으로는 안 된다.** "보이지 않는 낙차"라는 정의상 낙차 바닥은
카메라에서 안 보이므로 **어떤 render pass 에도 나타나지 않는다.**
그러나 **씬이 정적이라는 점을 이용해 렌더러 밖에서 정확히 만들 수 있다.**

**권장안 A — PhysX 레이캐스트 heightfield + 픽셀 역투영 (렌더러 미사용)**

```python
# ── 씬당 1회: 하향 레이캐스트로 2.5D 높이장 구축 ──────────────────────
from omni.physx import get_physx_scene_query_interface
import numpy as np
# 지형 메시에 UsdPhysics.CollisionAPI 필요
# 헬퍼: isaacsim.replicator.behavior.utils.scene_utils.add_colliders(prim)

CELL = 0.02                                    # 2 cm 그리드
xs = np.arange(x_min, x_max, CELL); ys = np.arange(y_min, y_max, CELL)
H = np.full((len(xs), len(ys)), np.nan, np.float32)
for i, x in enumerate(xs):
    for j, y in enumerate(ys):
        hit = get_physx_scene_query_interface().raycast_closest(
            (float(x), float(y), z_top), (0.0, 0.0, -1.0), z_top - z_bottom)
        if hit["hit"]:
            H[i, j] = hit["position"][2]

# ── 낙차 = 보폭 반경 내 최대 하강량 ──────────────────────────────────
from scipy.ndimage import minimum_filter
r = int(round(STEP_RADIUS_M / CELL))           # 예: 0.30 m
DROP = H - minimum_filter(H, size=2 * r + 1)   # (X,Y) → 낙차[m], 평지는 0

# ── 프레임마다: depth + camera_params → 픽셀별 낙차 라벨 ─────────────
depth = depth_anno.get_data()                  # (H,W) float32, 미터
cp    = camparams_anno.get_data()
view  = np.array(cp["cameraViewTransform"]).reshape(4, 4)
proj  = np.array(cp["cameraProjection"]).reshape(4, 4)
# NDC 격자 → view ray → world 점 P = cam_origin + ray * depth (표준 역투영)
label = DROP[np.clip(((P[...,0]-x_min)/CELL).astype(int), 0, len(xs)-1),
             np.clip(((P[...,1]-y_min)/CELL).astype(int), 0, len(ys)-1)]
label[np.isinf(depth)] = 0.0                   # 하늘 마스킹 (0 아님! inf 체크)
label[seg != GROUND_ID] = 0.0                  # 지면 클래스만
```

**장점**: 렌더러 투영 버그와 무관, 헤드리스 안전, **씬당 1회만 비쌈**(프레임마다 아님),
**연속값 라벨**, 그리고 **§2-4 의 Mesh 하이트필드 지형과 같은 데이터를 재사용**할 수 있다.
PhysX 대신 `omni.kit.mesh.raycast` 도 가능.

**권장안 B — 마커 지오메트리 2-pass (교차검증용)**
낙차 구간에 얇은 "위험 볼륨" 프림을 낙차 bin 별 semantic 으로 저작해두고 프레임당 2회 캡처:
```python
with marker_node: rep.modify.visibility(False)
rep.orchestrator.step(rt_subframes=8, delta_time=0.0)   # → rgb
with marker_node: rep.modify.visibility(True)
rep.orchestrator.step(rt_subframes=1, delta_time=0.0)   # → semantic_segmentation
```
비용 2배, 라벨이 이산(bin)으로 양자화되지만 구현이 단순. **A안의 sanity check 로 권장.**

**하지 말 것**: 탑다운 직교 depth pass / `distance_to_image_plane` 만으로 낙차 추론
(보이지 않는 바닥은 depth 에 애초에 없다).

### 8-6. Writer — 커스텀 낙차 맵을 rgb 와 함께 저장

**`BasicWriter.__init__` 전체 [로컬검증]** (`writers_default/basicwriter.py:137`)
```python
BasicWriter(output_dir=None, s3_bucket=None, s3_region=None, s3_endpoint=None,
            semantic_types=None,
            rgb=False, bounding_box_2d_tight=False, bounding_box_2d_loose=False,
            semantic_segmentation=False, instance_id_segmentation=False, instance_segmentation=False,
            distance_to_camera=False, distance_to_image_plane=False, bounding_box_3d=False,
            occlusion=False, normals=False, motion_vectors=False, camera_params=False,
            pointcloud=False, pointcloud_include_unlabelled=False,
            image_output_format="png",
            colorize_semantic_segmentation=True, colorize_instance_id_segmentation=True,
            colorize_instance_segmentation=True, colorize_depth=False,
            skeleton_data=False, frame_padding=4,
            semantic_filter_predicate=None, use_common_output_dir=False, backend=None)
```

**커스텀 writer [로컬검증]** (`basicwriter.py:409,421` 패턴 그대로)
```python
import omni.replicator.core as rep
from omni.replicator.core.scripts import functional as F

class DropHeightWriter(rep.Writer):
    def __init__(self, output_dir):
        self.version = "1.0.0"
        self.backend = rep.BackendDispatch(output_dir=output_dir)
        self.annotators = ["LdrColor",
                           rep.annotators.get("distance_to_camera"),
                           rep.annotators.get("semantic_segmentation"),
                           rep.annotators.get("camera_params")]
        self.data_structure = "annotator"       # legacy | annotator | renderProduct
        self._frame_id = 0

    def write(self, data):
        rgb   = data["annotators"]["LdrColor"][rp_key]["data"]
        depth = data["annotators"]["distance_to_camera"][rp_key]["data"]
        drop  = compute_drop_map(depth, data["annotators"]["camera_params"][rp_key])
        self.backend.schedule(F.write_image, data=rgb,  path=f"rgb_{self._frame_id:06}.png")
        self.backend.schedule(F.write_np,    data=drop, path=f"drop_{self._frame_id:06}.npy")
        self._frame_id += 1

rep.WriterRegistry.register(DropHeightWriter)
w = rep.WriterRegistry.get("DropHeightWriter"); w.initialize(output_dir="_out"); w.attach([rp])
```
관련 API **[로컬검증]**: `rep.WriterRegistry.register(writer, category=None)` (`writers.py:537`),
`Writer.attach(render_products, trigger="omni.replicator.core.OgnOnFrame")` (`:460`;
`trigger=None` 이면 `writer.schedule_write()` 로 수동 제어),
`Writer.add_annotator(...)`, `Writer.augment_annotator(annotator_name, augmentation, **kwargs)`.

**I/O 성능 노브 [웹검증]** (생성자 인자가 아니라 carb 설정):
`/omni/replicator/backend/writeThreads`(기본 4), `/omni/replicator/backend/queueSize`(기본 1000).
NVIDIA 벤치마크: Titan RTX, 3840×2160, 100프레임에서 writeThreads 1→16 이 **3.0 → 6.5 FPS**.
그리고 **PNG 는 JPEG 보다 인코딩에 "거의 한 자릿수 배" 더 걸린다.**
https://docs.omniverse.nvidia.com/extensions/latest/ext_replicator/io_guidelines.html

### 8-7. Orchestrator

**[로컬검증]** (`orchestrator.py`)
```python
run(num_frames=None, start_timeline=False)                      # rt_subframes 인자 없음
run_until_complete(num_frames=None, start_timeline=False)
step(rt_subframes=-1, pause_timeline=True, delta_time=None)     # ★ 이걸 쓴다
step_async(...) / stop() / resume() / pause() / preview()
wait_until_complete()  set_next_rt_subframes(n)  set_minimum_next_rt_subframes(n)
set_capture_on_play(value: bool)  get_is_started() / get_status()
```
⚠️ `step()`, `wait_until_complete()`, `run_until_complete()` 는 `_verify_is_standalone_workflow()`
를 호출해 `builtins.ISAAC_LAUNCHED_FROM_TERMINAL` 이 아니면 raise 한다 — SimulationApp 스크립트면 문제없다.

`step()` 은 **렌더가 실제로 도착할 때까지 블록**한다(SDGPipeline 의 참조 시각이 예약 시각에
도달할 때까지 스핀, 상한 `MAX_STEP_ATTEMPTS=1000`) → **우리 수동 update 루프보다 정확하다.**
**[로컬검증]** 공식 4.5 SDG 튜토리얼도 전부 `run()` 이 아니라 `step()` 루프를 쓴다.

### 8-8. 렌더 모드 API

**[로컬검증]** `rep.settings` 공개 함수는 정확히 6개:
```python
carb_settings(setting, value)                                  # distribution 도 수용 → 설정 자체를 랜덤화
set_physx_timestep(dt)
set_render_rtx_realtime(antialiasing="FXAA")                   # off:0 taa:1 fxaa:2 dlss:3 dlaa:4
set_render_pathtraced(samples_per_pixel=64)                    # totalSpp 만 설정
set_stage_meters_per_unit(v)   set_stage_up_axis(axis)
```
docstring: *"FXAA is recommended for non-sequential data generation as it does not accumulate
samples across frames."* → **프레임마다 씬이 바뀌는 랜덤화 데이터셋에서는 DLSS/TAA 의 시간 누적이
오히려 해가 된다.** (§7-5 의 DLAA 권고는 **정적 룩체크 샷** 기준이다. 목적에 따라 갈린다.)

### 8-9. Augmentation — 이름이 통념과 다르다

**[로컬검증]** `annotators.py:197-330`, `augmentations_default.py`
```python
Augmentation.from_function(fn_or_warp_kernel, data_out_shape=None, **kwargs)
Augmentation.from_node(node_type_id, attributes_mapping=None, ...)
Annotator.augment(augmentation, data_out_shape=None, name=None, device=None, **kwargs)
Annotator.augment_compose(augmentations: List[...], name=None)
rep.annotators.register_augmentation(name, augmentation)
```
warp kernel → GPU 노드, 순수 python/numpy → CPU 노드. **warp 는 Isaac Sim 에 번들돼 있어 별도 설치 불필요.**

⚠️ **`rep.augmentations_default.gaussian_noise` 는 없다.** 모듈 레벨 `Augmentation` 객체가 아예 없고
**문자열 키 레지스트리**다. 실재하는 빌트인 전체:
`RgbaToRgb`, `AdjustSigmoid`, `Brightness`, `SpeckleNoise`, `ShotNoise`, `RgbToHsv`, `HsvToRgb`,
`GlassBlur`, `BackgroundRand`, `Contrast`, `Conv2d`, `CropResize`, `CutMix`, `ImageBlend`,
**`MotionBlur`**(motionAngle, strength, kernelSize), `Pixellate`, `Rotate`.

**없는 것**: gaussian_noise, salt_and_pepper, 렌즈 왜곡, flip, hue/saturation shift.
→ 렌즈 왜곡은 augmentation 이 아니라 **카메라 레벨**
(`projection_type="fisheyeRadTanThinPrism"`, `fisheye_p0/p1`, `fisheye_s0..s3`).
가우시안 노이즈는 warp 커널 직접 작성 (동봉 테스트에 그대로 있음, `tests/test_augmentations.py:664-683`):
```python
import warp as wp
@wp.kernel
def gaussian_noise_wp(data_in: wp.array2d(dtype=wp.float32),
                      data_out: wp.array2d(dtype=wp.float32), sigma: float, seed: int):
    i, j = wp.tid()
    state = wp.rand_init(seed, wp.tid())
    data_out[i, j] = data_in[i, j] + sigma * wp.randn(state)

rep.annotators.register_augmentation("depth_noise",
    rep.annotators.Augmentation.from_function(gaussian_noise_wp, sigma=0.01, seed=None))
writer.augment_annotator("distance_to_camera", "depth_noise")
```
⚠️ BasicWriter 는 annotator **이름으로 라우팅**하므로(`if name == "rgb" or name.startswith("Aug")`)
augment 시 `name="rgb"` 로 원래 키를 유지하거나 커스텀 writer 를 쓸 것.

### 8-10. `isaacsim.replicator.*` 확장 전수

**[로컬검증]**

| 확장 | 버전 | 기본 활성 | 내용 |
|---|---|---|---|
| `isaacsim.replicator.writers` | 1.0.1 | ○ | DOPE/Pose/Pytorch/YCBVideo/DataVisualization writer — 우리와 무관 |
| `isaacsim.replicator.domain_randomization` | 1.0.2 | ○ | **RL 물리 DR 전용. 시각/외형 랜덤화 전혀 없음** — 우리와 무관 |
| **`isaacsim.replicator.behavior`** | 1.0.8 | ○ | **프림 부착형 behavior script 랜덤화 — 우리에게 유용** |
| `isaacsim.replicator.examples` | 1.1.2 | X | **참조 구현 보고**(아래) |
| `isaacsim.replicator.scene_blox` | 1.0.2 | ○ | WFC 절차 씬 생성(§4-3g) |
| `isaacsim.replicator.synthetic_recorder` | 2.2.3 | ○ | 헤드리스 클래스 `SyntheticRecorder` 포함 |
| **`isaacsim.replicator.agent.{core,ui,camera_calibration}`** | 0.5.x | X | **IRA — 사람 시뮬레이션** |
| `isaacsim.replicator.object` | 0.3.21 | X | YAML 선언형 객체검출 SDG (자산이 창고 계열) |
| `isaacsim.replicator.metropolis.utils` | 0.0.6 | X | IRA + omni.anim.people 공통 유틸 |

**`behavior` 확장 [로컬검증]** — 프림에 붙이는 8개 스크립트:
`LightRandomizer`(minColor/maxColor/intensity range), `TextureRandomizer`(textures csv,
projectUvwProbability, textureScaleRange, textureRotateRange), `LocationRandomizer`,
`RotationRandomizer`, `LookAtBehavior`, `VolumeStackRandomizer`(물리 낙하 적재) 등.
```python
await add_behavior_script_with_parameters_async(prim, inspect.getfile(LookAtBehavior),
        {f"exposedVar:{LookAtBehavior.BEHAVIOR_NS}:targetPrimPath": target_path})
```
동봉된 `tests/test_behaviors_sdg_scenario.py` 가 **이 설치본에서 가장 잘 만들어진 SDG 예제**다 —
기존 저작 USD 스테이지를 열어 behavior 로 랜덤화하고 캡처한다.

**참조 구현으로 읽을 것 [로컬검증]** (pip 휠에는 `standalone_examples/` 가 없고 테스트에 인라인):
- **`test_sdg_ur10_palletizing.py`** — 기존 저작 씬 랜덤화 + PT 전환(spp=32) + 카메라 랜덤화 전부 포함.
  **우리 프로젝트의 참조 구현으로 삼을 것.**
- `test_sdg_getting_started.py:84` — 커스텀 writer 정의
- `test_sdg_useful_snippets.py:301` — PT + motion blur 설정

### 8-11. 사람 채우기 — IRA vs 경량 경로

**[로컬검증]** `omni.anim.people-0.6.7` + anim 스택 20여 개가 **conda 설치본에 번들돼 있다**
(standalone 에는 없음). IRA 가 이를 하드 의존.
**[웹검증]** NVIDIA: *"Omni.Anim.People is being replaced by Isaacsim.Replicator.Agent (IRA)"*, 상태 **beta**.

- **헤드리스 CLI**: `./python.sh tools/agent_sdg/sdg_scheduler.py -c <config.yaml>`
  (단 이 스크립트는 **pip 휠에 없고 standalone 배포판에만 있다**)
- **Python 진입점 [로컬검증]**: `isaacsim.replicator.agent.core.simulation.SimulationManager`
  → `load_config_file(path)` → `set_up_simulation_from_config_file()` →
  `await run_data_generation_async(will_wait_until_complete=True)`. **`main()`/argparse 는 휠에 없다.**
- **자산 위치**: `[Isaac Assets Root]/Isaac/People/Characters/` (§4-1). 휠에는 캐릭터 USD 가 하나도 없다.

**⚠️ 야외 절차 씬의 큰 장벽 [로컬검증]** (`simulation.py:645`): 셋업이 `NavmeshVolume` 을 요구하고
없으면 *"NavMesh building failed. Please check whether the stage has a valid NavmeshVolume."* 로 중단된다.
즉 **계단·강둑·지하도 씬마다 navmesh 볼륨을 저작해야 한다.**
게다가 IRA 데이터 생성부는 해상도가 **1920×1080 하드코딩**이고 writer 도
`IRABasicWriter`/`TaoWriter`/`StereoWriter` 로 고정이라 **커스텀 낙차 GT writer 와 결합할 수 없다.**

> **권고 [추정]**: 사람이 필요한 이유가 "사람이 없다"는 도메인 갭 해소라면 IRA 전체 파이프라인 대신
> **(a)** 캐릭터 USD 를 `rep.randomizer.instantiate(paths, size, mode="scene_instance")` 로 스폰,
> **(b)** `rep.randomizer.scatter_2d(surface_prims=<보행가능 지면>)` 로 배치,
> **(c)** 애니메이션은 정지 포즈 또는 `rep.modify.animation()` 프레임 오프셋만 랜덤화.
> **navmesh 와 커맨드 파일이 불필요해지고, 우리 낙차 GT writer 를 그대로 쓸 수 있다.**
> 스케일 앵커 용도에는 이걸로 충분하다.

### 8-12. 최소 실행 가능 파이프라인

```python
# run:  python sdg.py --/exts/isaacsim.core.throttling/enable_async=false
from isaacsim import SimulationApp
sim_app = SimulationApp({"headless": True, "width": 1280, "height": 720})

import omni.replicator.core as rep
from isaacsim.core.utils.stage import open_stage
from isaacsim.core.utils.semantics import add_update_semantics   # 4.5 = Semantics.SemanticsAPI

# (a) 우리 자체 USD 스크립트가 저작한 스테이지 로드 + 사후 semantics 부착
open_stage("/path/to/scene01_campus_stairs.usd")
for prim in ground_prims:
    add_update_semantics(prim, semantic_label="ground", type_label="class")

# (b) 카메라 + render product
cam = rep.create.camera(focal_length=18.0, f_stop=0.0, clipping_range=(0.05, 500.0))
rp  = rep.create.render_product(cam, resolution=(1280, 720), name="Main")

# (c) 태양 + HDRI + 기존 프림 재질 랜덤화
sun    = rep.create.light(light_type="Distant")
dome   = rep.create.light(light_type="dome", texture=hdri_paths[0])
ground = rep.get.prims(path_pattern=".*/Terrain/.*", prim_types=["Mesh"], cache_result=False)

with rep.trigger.on_frame():
    with sun:
        rep.modify.attribute("inputs:intensity", rep.distribution.log_uniform(500.0, 8000.0))
        rep.modify.attribute("inputs:colorTemperature", rep.distribution.normal(6500.0, 1200.0))
        rep.modify.pose(rotation=rep.distribution.uniform((-70,-180,0), (-20,180,0)))
    with dome:
        rep.modify.attribute("inputs:texture:file",
                             rep.distribution.choice(hdri_paths), attribute_type="asset")
    with cam:
        rep.modify.pose(position=rep.distribution.uniform((-4,-4,0.6), (4,4,1.8)),
                        rotation=rep.distribution.uniform((-25,0,-180), (5,0,180)))
    with ground:
        rep.randomizer.texture(ground_textures,
                               texture_rotate=rep.distribution.uniform(0, 360), project_uvw=True)

# (d) writer — rgb + semantic + depth + camera_params (낙차 맵 계산 입력)
writer = rep.WriterRegistry.get("BasicWriter")     # 최종에는 DropHeightWriter 로 교체
writer.initialize(output_dir="_out/scene01", rgb=True, semantic_segmentation=True,
                  distance_to_camera=True, camera_params=True,
                  colorize_semantic_segmentation=False,   # raw uint32 id 유지
                  image_output_format="jpeg",             # png 는 인코딩 ~10배 느림
                  semantic_filter_predicate="class:*")
writer.attach([rp])

# (e) 렌더 모드 + 서브프레임 — 572회 루프를 8회로
rep.settings.carb_settings("/omni/replicator/backend/writeThreads", 16)
rep.settings.set_render_rtx_realtime(antialiasing="FXAA")   # 대량 생성 = RT/FXAA (§9-4)
# (PT 홀드아웃일 때만)
# rep.settings.carb_settings("/rtx/pathtracing/spp", 16)
# rep.settings.set_render_pathtraced(samples_per_pixel=64)
rep.orchestrator.set_capture_on_play(False)
for _ in range(NUM_FRAMES):
    rep.orchestrator.step(rt_subframes=8, delta_time=0.0)
rep.orchestrator.wait_until_complete()
sim_app.close()
```

---

## §9. 성능 현실성 — RTX 4090 24GB 1대로 무엇이 가능한가

### 9-1. 실측 — 우리 자신의 로그에서

**[실측]** `look_check/scene*/…/*.png` 의 mtime 간격을 계산했다(이상치 = 씬 전환 제외).
2026-07-27 실행, RTX 4090, 1920×1080, DLSS Quality.

| 구성 | 설정 | 샷당 시간 | 표본 |
|---|---|---|---|
| **PathTracing** | totalSpp=512, maxBounces=8, OptiX denoiser, warmup 572 update | **13.99 s** (범위 11.6~16.0) | v5_pt 15씬 195샷 |
| 〃 | 동일 | 13.47 s | final_pt 26디렉터리 |
| 〃 | 동일 | 13.12 s | v8_pt 8씬 |
| **RaytracedLighting** | warmup 90 update | **1.12 s** (범위 0.96~1.32) | v5_rt/v7_rt/r1 60+ 디렉터리 |
| 〃 | warmup 90, 단순 씬 | 0.82 s | v6_rt scene01~11 |

**프로세스 오버헤드 [실측]**: 씬 전환 간격(마지막 샷 → 다음 씬 첫 샷)
- RT 배치: 중앙값 **11.5 s** (첫 샷 1.1 s 포함) → **SimulationApp 부팅 + USD 조립 ≈ 10 s**
- PT 배치: 중앙값 22.9 s (첫 샷 13.5 s 포함) → 동일하게 ≈ 9~10 s

**파생 지표 [실측→계산]**
- PT: 572 update / 13.99 s = **40.9 update/s**. `totalSpp=512` 에서 누적이 멈추므로
  실효 **≈ 41 spp/s @1080p·8바운스 ⇒ 샘플패스당 24.4 ms**
- RT: 90 update / 1.12 s = **80 frame/s ⇒ 12.5 ms/frame**
  → **워밍업 90회는 과잉이다.** RT 의 시간적 누적/디노이저는 통상 8~32 프레임이면 수렴한다 **[추정]**.
  `NEGOBS_WARMUP=32` 로 낮추면 **≈0.40 s/샷** 이 되어 2.8배 빨라진다. **실험 1회로 확인 가능.**

### 9-1b. NVIDIA 공식 SDG 벤치마크 — 결정적 시사점 1개

**[웹검증]** https://docs.isaacsim.omniverse.nvidia.com/4.5.0/reference_material/benchmarks.html
측정법: *"두 개의 720p 카메라, 빈 씬, 프레임당 500개 객체 생성"*.
지표 MP/s = `FPS × 2 × 1280 × 720 / 1e6`.

| GPU | Simple (RGBD만) MP/s | Complex (전 annotator) MP/s |
|---|---|---|
| RTX 3070 | 81.3 / 79.4 | 3.7 / 5.0 |
| **RTX 4080** | **163.4 / 162.7** | **3.6 / 5.3** |
| RTX 6000 Ada | 208.0 / 212.8 | 3.6 / 5.2 |

> **가장 중요한 시사점: 전 annotator 를 켜면 약 40배 붕괴하고, 그 값은 GPU 와 무관하다**
> (3070/4080/6000Ada 전부 3.6~5.3). **annotator 개수가 단일 최대 레버다.**
> → **RGB + depth + semantic + camera_params 4개만 켜라.** bounding_box 계열은
> CPU 바운드이고(GPU 불가) 우리에게 불필요하다.

**RTX 4090 추정 [추정]**: 4080 의 약 1.2~1.3배 → ~200 MP/s.
여기에 실제 야외 절차 씬(식생·다중 재질) 페널티와 `rt_subframes` 배수를 곱해야 한다.

**공식 튜닝 지침 [웹검증]**
- **subframes**: "32부터 시도하고 용도에 따라 조정". 재질 로딩 문제 방지를 위해 **최소 2** 필요.
  (4.5 공식 튜토리얼 실사용값은 4~32)
- **캡처하지 않는 프레임에는 render product 비활성화** — 공식 최적화로 명시
- **멀티GPU: "렌더링하는 카메라 수만큼 GPU 를 추가하되 그 이상은 안 됨."**
  → **4090 1장이면 카메라 1~2개가 상한**. GPU 물리는 GPU 개수와 무관하게 1장만 쓴다
- 텍스처 스트리밍 예산 `/rtx-transient/resourcemanager/texturestreaming/memoryBudget` 기본 0.6
- CPU 스레드는 가상코어 수보다 적게 제한 권장
- **[웹검증]** **RTX 4090 전용 SDG 벤치마크는 존재하지 않는다.** 위는 4080 외삽이며
  실제 야외 씬 페널티는 직접 재봐야 한다. 공식 측정 스크립트는
  `standalone_examples/benchmarks/benchmark_sdg.py` (pip 휠에 없음, GitHub 에 있음).

**Replicator 도입 시 우리 실측(§9-1)과의 관계 [추정]**
- 현재 PT 13.99 s/샷 = `spp=1 × 572프레임`. §8-0 대로 `spp=16, totalSpp=64, rt_subframes=8` 로 바꾸면
  **PT 도 8프레임/샷**이 되어 **[추정] 1~3 s/샷 수준**까지 내려갈 수 있다.
  → 아래 §9-3 의 시나리오 D/E 가 더 좋아질 여지가 크다. **반드시 실측할 것.**
- RT 는 `set_render_rtx_realtime(antialiasing="FXAA")` 를 쓴다(§8-8: 프레임마다 씬이 바뀌는
  랜덤화 데이터셋에서는 DLSS/TAA 의 시간 누적이 오히려 해가 된다).
### 9-2. 스케일링 모델 (추정)

**[추정 — 선형 가정, 반드시 실측 검증]**

```
T_PT(spp, W, H)  ≈  0.0244 s × spp × (W·H / 2,073,600)
T_RT(warm, W, H) ≈  0.0125 s × warm × (W·H / 2,073,600)
```

| spp | 1920×1080 | 1280×720 (0.444×) | 960×540 (0.25×) |
|---|---|---|---|
| 512 | 12.5 s | 5.6 s | 3.1 s |
| 256 | 6.2 s | 2.8 s | 1.6 s |
| 128 | 3.1 s | 1.4 s | 0.78 s |
| 64 | 1.6 s | 0.69 s | 0.39 s |
| 32 | 0.78 s | 0.35 s | 0.20 s |

| RT warmup | 1920×1080 | 1280×720 |
|---|---|---|
| 90 (현재) | 1.12 s | 0.50 s |
| 32 | 0.40 s | 0.18 s |
| 16 | 0.20 s | 0.09 s |

### 9-3. 데이터셋 규모별 소요 시간

**[추정]** 프로세스 오버헤드는 "프로세스당 이미지 수"에 따라 상각된다.
현재 구조(13샷/프로세스)면 10 s / 13 = **0.77 s/이미지** 가 얹힌다 — RT 렌더 자체와 맞먹는다.
Replicator 로 한 프로세스에서 200~2,000장을 뽑으면 **0.05 s/이미지 이하**로 떨어진다.
아래 표는 **프로세스당 200장 이상(오버헤드 0.05 s/장)** 을 가정한다.

| 시나리오 | 설정 | 장당 | **1만 장** | **2만 장** | **5만 장** |
|---|---|---|---|---|---|
| **A. RT 고속** | RT, 1280×720, warm=32 | 0.23 s | **38분** | **1.3 h** | **3.2 h** |
| **B. RT 표준** | RT, 1920×1080, warm=32 | 0.45 s | 1.3 h | **2.5 h** | 6.3 h |
| **C. RT 현행 워밍업** | RT, 1920×1080, warm=90 | 1.17 s | 3.3 h | 6.5 h | 16.3 h |
| **D. PT 경량** | PT 64spp, 1280×720 | 0.74 s | 2.1 h | **4.1 h** | 10.3 h |
| **E. PT 중간** | PT 128spp, 1920×1080 | 3.15 s | 8.8 h | 17.5 h | 43.8 h |
| **F. PT 현행** | PT 512spp, 1920×1080 | 12.55 s | **34.9 h** | **69.7 h** | **174 h (7.3일)** |

**여기에 GT 라벨 패스가 추가된다.** 다만 depth/semantic annotator 는 RT 모드에서 거의 공짜다
**[추정]** — 셰이딩이 아니라 지오메트리·ID 를 읽는 패스이므로 RGB 대비 10~20% 수준.

### 9-4. 판단 — RT 로 데이터를 뽑아도 되는가

**결론: 뽑아도 된다. 단, 3가지 조건을 붙여야 한다.**

#### 근거 (a) — 렌더 사실성은 실제로 학습 성능에 유의미하다

**[웹검증]** Hodaň, Vineet, Gal, Shalev, Hanzelka, Connell, Urbina, Sinha, Guenter,
"Photorealistic Image Synthesis for Object Instance Detection", arXiv:1902.03334 (2019).
https://arxiv.org/abs/1902.03334
> 물리기반 렌더링(PBR)을 쓴 합성 데이터가 단순 렌더링 기준선 대비
> **Rutgers APC 에서 mAP@.75IoU +24%p**, **LineMod-Occluded 에서 mAP +11%p** 향상.

→ "렌더 품질은 학습에 상관없다"는 통념은 **틀렸다.** 사실성은 중요하다.

#### 근거 (b) — 그러나 이 논문의 "단순 렌더링" 기준선은 RTX RT 가 아니다

Hodaň et al. 의 비교 대상은 **OpenGL 래스터화 + 조악한 조명**이다.
우리의 `RaytracedLighting` 은 **직접광을 실제로 레이트레이싱**하고,
`/rtx/indirectDiffuse/*`(간접 확산), `/rtx/reflections/*`, `/rtx/ambientOcclusion/*`,
`/rtx/raytracing/subsurface/*` 를 지원하며, 포스트 스택은 PT 와 **완전히 동일**하다(§6-6).
**RT 와 PT 의 격차는 OpenGL 과 PT 의 격차보다 훨씬 작다.** 그 논문 결과를
"RT 로 데이터를 뽑으면 안 된다"의 근거로 쓰는 것은 과잉 일반화다.

#### 근거 (c) — 우리 과제에서 PT 가 실제로 사는 지점은 **딱 하나**다

우리 연구의 맥락단서 4계열 중 ④ **조명(암부·그림자)** 은 확증 전용 단서다.
그리고 낙차 하부의 **가려진 어두운 영역의 밝기**는 정확히 **다중바운스 간접광**이 결정한다.
RT 는 이 부분을 근사한다(`indirectDiffuse/maxBounces` 기본값이 낮음).

→ **낙차 하부 암부의 휘도 분포가 RT 와 PT 사이에서 체계적으로 다르면**,
RT 로 학습한 모델이 실사진의 암부 밝기를 오독할 위험이 있다.

#### 그래서 붙일 3가지 조건

1. **RT 를 GI 쪽으로 밀어올린다** (비용 거의 없음)
   ```python
   s.set("/rtx/indirectDiffuse/enabled", True)
   s.set("/rtx/indirectDiffuse/maxBounces", 4)          # 기본보다 높게
   s.set("/rtx/indirectDiffuse/fetchSampleCount", 4)    # 최대
   s.set("/rtx/directLighting/sampledLighting/enabled", True)
   s.set("/rtx/directLighting/sampledLighting/samplesPerPixel", 4)
   s.set("/rtx/reflections/enabled", True)
   s.set("/rtx/ambientOcclusion/enabled", True)
   s.set("/rtx/raytracing/subsurface/enabled", True)
   ```
   **[추정]** 이 설정으로 RT 샷당 시간은 1.5~2.5배 늘어나지만(0.4 s → 0.7~1.0 s)
   여전히 PT 대비 15~30배 빠르다.

2. **RT↔PT 정합성 검증을 명시적 실험으로 넣는다** (논문에 실릴 표 1개)
   - 대표 뷰 300~500장을 **RT 와 PT 양쪽으로** 렌더한다 (PT 쪽 비용: 500 × 12.5 s ≈ 1.7 h. 감당 가능).
   - 측정: ① 낙차 하부 ROI 의 휘도 히스토그램 거리 ② 동일 모델의 예측 맵 차이(IoU/MAE).
   - 차이가 작으면 → RT 로 대량 생성해도 된다는 **정량 근거**가 생긴다.
   - 차이가 크면 → 하이브리드(아래 3)로 간다.

3. **PT 홀드아웃을 데이터셋에 5~10% 섞는다**
   - 학습셋의 5~10%(예: 2만 장 중 1,000~2,000장)를 PT 로 뽑는다. 비용 3.5~7 h.
   - 효과 (i) 모델이 RT 특유의 아티팩트에 과적합하지 않게 막는다
     (ii) **검증셋을 PT 로 두면 "RT 로 학습 → PT 에서도 성능 유지" 를 논문에서 주장할 수 있다.**
     이건 sim2real 논증의 미니어처 버전이다.

**한 줄 처방**: **주력 = RT(GI 강화) 1280×720 또는 1920×1080, warm=32 → 2만 장 1.3~2.5시간.
PT 512spp 는 (i) 논문 그림 (ii) 5% 홀드아웃 (iii) RT↔PT 정합성 실험 전용.**

### 9-5. PT 를 꼭 써야 한다면 — 검증되지 않은 가속 카드 3장

**[로컬검증 — 키 존재 확인 / 미검증 — 실효 미확인]**

1. **적응 샘플링**
   ```python
   s.set("/rtx/pathtracing/adaptiveSampling/enabled", True)
   s.set("/rtx/pathtracing/adaptiveSampling/targetError", 0.01)
   ```
   수렴한 픽셀에 샘플을 안 쓴다. 하늘·평탄 지면이 많은 우리 씬에서 **[추정] 1.5~3배 이득 가능**.
2. **Neural Radiance Cache** — `/rtx/pathtracing/nrc/enabled`
   **[추정]** 간접광을 신경망 캐시로 대체. 켜지면 큰 폭 가속이 예상되나 4.5 에서 실험적일 수 있다.
3. **캐시 계열** — `/rtx/pathtracing/cached/enabled`, `/rtx/pathtracing/lightcache/cached/enabled`,
   `/rtx/pathtracing/lightcache/spatialCache/enabled`

**추가로 반드시 켤 것**: `/rtx/pathtracing/fireflyFilter/enabled` (반딧불 노이즈 억제 →
같은 spp 에서 체감 품질 상승) **[로컬검증 존재]**.

### 9-6. 메모리 예산 (24GB)

**[추정 — 실측 필요]**
- 현재 씬: 프림 수십~수백, 4K 텍스처 20~30세트 → VRAM 여유 대단히 큼.
- 외부 에셋 도입 후(§4~§5): 텍스처가 병목이 된다. 4K RGBA jpg 1장 ≈ 압축 후 5~11 MB VRAM.
  200세트(diff/nor/rough/ao 4장) = 800장 → **4~9 GB**. 아직 여유.
- PointInstancer 100만 개 ≈ **40 MB**(변환 데이터). 프로토타입 지오메트리와 BLAS 가 실제 부담.
- **위험 신호**: 인스턴스 10⁶ 초과 + 고폴리 프로토타입 조합. 이때 `/rtx-transient/resourcemanager/
  maxMipCount=12`, `enableTextureStreaming=True`, `/rtx/hydra/geometrystreaming/instanceBudget` 조정.
- **[로컬검증]** `omni.hydra.engine.stats-1.0.3` 확장이 설치돼 있어 VRAM·프레임타임 계측이 가능하다.
  **스케일 테스트를 반드시 먼저 할 것.**

---

## §10. 즉시 적용 가능한 상위 10개

"오늘 코드에 넣을 수 있는" 순으로. **비용은 사람-시간, 효과는 사실성 기여 추정치.**

---

#### ① `/rtx/post/aa/op = 4` (DLSS → DLAA) — 비용 1줄, 효과 중

**[로컬검증]** 우리는 `aa/op=3`(DLSS) + `dlss/execMode=2`(Quality)를 쓴다
(`scene_common.py:188-189`). DLSS 는 **저해상도에서 렌더해 업스케일**한다.
1920×1080 최종 산출물을 오프라인으로 뽑는 상황에서 업스케일할 이유가 없다.
```python
settings.set("/rtx/post/aa/op", 4)     # DLAA — 네이티브 해상도 AA
settings.set("/rtx/ecoMode/enabled", False)
```
> **단, 대량 랜덤화 데이터셋 생성 단계에서는 FXAA(2)가 낫다** — §8-8 참조.
> **룩체크/논문 그림 = DLAA, 데이터셋 = FXAA** 로 갈라 쓸 것.

---

#### ② `round_edges_radius` — 비용 3줄, 효과 **상** (우리 씬에 가장 특화된 항목)

**[로컬검증]** OmniPBR 에 있고 우리가 안 쓰는 파라미터. 우리 씬은 전부
`UsdGeom.Cube`/`Cylinder` 라 **모든 모서리가 수학적으로 완벽한 직각**이고,
이것이 "게임 같다"는 인상의 최대 단일 원인이다. 지오메트리를 안 건드리고 셰이딩 단계에서 해결한다.
```python
# scene_common.make_pbr() 에 인자 추가
sh.CreateInput("round_edges_radius",   F).Set(0.004)   # 4 mm
sh.CreateInput("round_edges_roundness", F).Set(1.0)
sh.CreateInput("round_edges_across_materials", B).Set(True)
```
**[미검증]** 렌더 확인은 안 했다. MDL `::base::rounded_corner_normal` 표준 기능이라
**[추정] 동작할 것.** 실루엣이 아니라 음영만 바뀌는 점 유의.

---

#### ③ 대기 안개 — 비용 6줄, 효과 **상** (야외 깊이감)

**[로컬검증]** 완전 미사용. 에어리얼 퍼스펙티브는 **단안 깊이 추정의 강력한 단서**이고
우리 U-Net 이 "이 낙차가 얼마나 먼가"를 판단하는 데 직결된다.
```python
s.set("/rtx/fog/enabled", True)
s.set("/rtx/fog/fogZup/enabled", True)              # ★ 우리는 Z-up
s.set("/rtx/fog/fogDistanceBased/enabled", True)
s.set("/rtx/fog/fogColor", (0.72, 0.78, 0.86))
s.set("/rtx/fog/fogStartDist", 20.0); s.set("/rtx/fog/fogEndDist", 400.0)
s.set("/rtx/fog/fogDistanceDensity", 0.35)
```

---

#### ④ 톤매핑 ACES + 자동노출 OFF — 비용 7줄, 효과 중

**[로컬검증]** 우리는 톤맵을 전혀 건드리지 않고 있다.
```python
s.set("/rtx/post/tonemap/op", 6)             # 6 = Aces
s.set("/rtx/post/tonemap/colorMode", 0)      # sRGBLinear
s.set("/rtx/post/tonemap/filmIso", 100.0)
s.set("/rtx/post/tonemap/exposureTime", 1.0/500.0)
s.set("/rtx/post/tonemap/fNumber", 8.0)
s.set("/rtx/post/tonemap/dither", 0.004)     # 밴딩 제거
s.set("/rtx/post/histogram/enabled", False)  # ★ 자동노출 OFF = 프레임간 라벨 일관성
```

---

#### ⑤ 디테일 노멀 — 비용 재질당 3줄, 효과 중 (근접 뷰에서 상)

**[로컬검증]** 이미 가진 노멀맵을 8~16배로 재활용. 베이스와 독립 UV 변환.
```python
# make_pbr() 내부, nor 가 있을 때
sh.CreateInput("detail_normalmap_texture", A).Set(nor)     # 같은 파일 재사용 가능
sh.CreateInput("detail_bump_factor", F).Set(0.4)
sh.CreateInput("detail_texture_scale", F2).Set(Gf.Vec2f(8.0, 8.0))
```

---

#### ⑥ 돔라이트 전략 변경 → `ensure_noon_lookfix()` 제거 — 비용 1줄 + 실험, 효과 중

**[로컬검증]** `/rtx/domeLight/upperLowerStrategy` 툴팁이 그대로 처방이다.
```python
s.set("/rtx/domeLight/upperLowerStrategy", 0)   # 0 = Image-Based Lighting (고주파 정확)
```
우리 `ensure_noon_lookfix()`(numpy EXR 수술, `scene_common.py:1077-1131`)가
**불필요해질 가능성이 높다.** 실험 1회로 확인.
대안: HDRI 에서 태양 완전 제거 + `DistantLight(angle=0.53°)` + `upperLowerStrategy=4` (NVIDIA 권장 패턴).

---

#### ⑦ 렌즈 사실성 (그레인·비네팅·수차·먼지) — 비용 20줄, 효과 중

**[로컬검증]** 전부 미사용. §7-7 스니펫 참조. 핵심만:
```python
s.set("/rtx/post/tvNoise/enabled", True)
s.set("/rtx/post/tvNoise/enableFilmGrain", True); s.set("/rtx/post/tvNoise/grainAmount", 0.02)
s.set("/rtx/post/tvNoise/enableVignetting", True); s.set("/rtx/post/tvNoise/vignettingStrength", 0.35)
for k in ("enableScanlines","enableScrollBug","enableGhostFlickering","enableWaveDistortion",
          "enableVerticalLines","enableRandomSplotches","enableVignettingFlickering"):
    s.set(f"/rtx/post/tvNoise/{k}", False)          # ★ TV 연출 항목 전부 OFF
s.set("/rtx/post/chromaticAberration/enabled", True)
s.set("/rtx/post/lensFlares/enabled", True)
s.set("/rtx/post/lensFlares/physicalSettings", True)
s.set("/rtx/post/lensFlares/dustStrength", 0.15)    # 실외 로봇 카메라 = 항상 먼지
s.set("/rtx/post/lensFlares/flareScale", 0.4)
```

---

#### ⑧ NVIDIA 나무 1그루 참조 임포트 — 비용 10줄, 효과 **최상** (씬 04 "구 뭉치" 직결)

**[웹검증 — HTTP 200 확인]** 다운로드도 필요 없다. USD 참조만 걸면 된다.
```python
VEG = "https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Vegetation"
p = stage.DefinePrim("/World/Tree_Cherry_01", "Xform")
p.GetReferences().AddReference(f"{VEG}/Trees/Japanese_Cherry.usd")
UsdGeom.Xformable(p).AddTranslateOp().Set(Gf.Vec3d(cx, cy, gz))
UsdGeom.Xformable(p).AddScaleOp().Set(Gf.Vec3f(1.0, 1.0, 1.0))   # metersPerUnit 확인 후
p.SetInstanceable(True)                                           # 다수 배치 시 필수
```
**첫 실험에서 반드시 확인**: (a) 잎 알파 컷아웃(§4-3b) (b) 스케일 단위 (c) 폴리곤/VRAM.
`build_tree()`(구 3개 + 원기둥)를 이걸로 교체하는 것이 **씬 04 지적에 대한 직접적 응답**이다.

---

#### ⑨ NVIDIA 가로시설물 참조 임포트 — 비용 20줄, 효과 상

**[웹검증 — HTTP 200 확인]** `bollard_01`, `safety_railing_01`, `bench_curved_01`,
`trashcan_cylinder_01`, `planter_round_02`, 가로등 40여 종.
우리 `build_bollard()`(원기둥 1개), `build_bench()`(박스 3개), `build_railing_line()` 을
**단계적으로** 교체한다.
```python
RM = ("https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.5/Isaac"
      "/Environments/Outdoor/Rivermark/dsready_content/nv_content/common_assets")
p = stage.DefinePrim("/World/Bollard_01", "Xform")
p.GetReferences().AddReference(f"{RM}/props_general/bollard_01/bollard_01.usd")
```
> **⚠️ 라이선스**: `/Isaac/Environments` 는 **"수정 금지" Limited Use Content**(§4-1d).
> **참조해서 렌더링하는 것은 OK, USD 를 편집하는 것은 문언상 불가.** 배치·스케일만 하고
> 내부를 고치지 말 것. 데이터셋을 공개 배포할 계획이면 CC0 대체(§5-1 Poly Haven
> `street_lamp_01`, `concrete_road_barrier_01`, `metal_trash_can`, `water_manhole_cover`)를 쓸 것.

---

#### ⑩ Replicator PT 서브프레임 — 비용 파이프라인 재작성, 효과 **처리량 수십 배**

**[로컬검증]** 우리 572회 update 루프는 `spp=1 × 512프레임` 이다(§8-0).
```python
rep.settings.carb_settings("/rtx/pathtracing/spp", 16)    # 프레임당 16샘플
rep.settings.set_render_pathtraced(samples_per_pixel=64)  # totalSpp=64 → 누적 4프레임
rep.orchestrator.step(rt_subframes=8, delta_time=0.0)     # 572 → 8
```
그리고 **반드시** `--/exts/isaacsim.core.throttling/enable_async=false` (§8-1 프레임 유실 방지).

---

### 보너스 — 즉시 확인만 하면 되는 실험 3개 (각 30분)

| # | 실험 | 확인할 것 |
|---|---|---|
| A | `subdiv_refinement_level=2` + `Cube` 1개 | RTX subdivision 이 프리미티브에 먹히는지 (§2-2) |
| B | `/rtx/material/enableMDLDisplacement=True` + `OmniSurface.geometry_displacement_image` | **변위가 4.5 에서 실제로 되는지** (§3-3). 되면 판이 바뀐다 |
| C | `Japanese_Cherry.usd` 참조 + RT 1장 | 알파 컷아웃·스케일·VRAM (§4-3b) |

---

## §11. 실행 함의

### 11-1. 우선순위 작업 목록

난이도: ★=수 시간 / ★★=1~3일 / ★★★=1~2주
효과: 사실성 기여 추정 (상/중/하). **선행조건**은 반드시 먼저 해야 하는 것.

#### P0 — 이번 주 (검증 실험, 각 30분~반나절)

| # | 작업 | 예상 효과 | 난이도 | 소요 | 선행조건 |
|---|---|---|---|---|---|
| P0-1 | **NVIDIA 나무 1그루 참조 임포트 + RT 1장** — 알파 컷아웃(§4-3b)·스케일·VRAM 확인 | 판단 근거 | ★ | 30분 | 없음 |
| P0-2 | **RT 워밍업 90 → 32 실험** — 화질 저하 없는지 확인 | 처리량 2.8배 | ★ | 30분 | 없음 |
| P0-3 | **`/rtx/material/enableMDLDisplacement` 실험** — 4.5 에서 변위가 되는지 | 되면 판이 바뀜 | ★ | 30분 | 없음 |
| P0-4 | **`subdiv_refinement_level=2` 실험** — 프리미티브에 먹히는지 | 중 | ★ | 30분 | 없음 |
| P0-5 | **§10 ①③④⑦ 설정 일괄 적용** 후 대표 3씬 RT 재렌더·육안 비교 | 중~상 | ★ | 반나절 | 없음 |
| P0-6 | **`round_edges_radius` 적용** 후 계단 근접 뷰 비교 | 상 | ★ | 1시간 | 없음 |
| P0-7 | **`upperLowerStrategy=0` vs `ensure_noon_lookfix()`** 비교 | 중 (+코드 삭제) | ★ | 1시간 | 없음 |

> **P0 전체가 하루 안에 끝난다.** 그리고 이 7개 결과가 아래 P1~P3 의 설계를 좌우한다.

#### P1 — 2주 이내 (사실성 본체)

| # | 작업 | 예상 효과 | 난이도 | 소요 | 선행조건 |
|---|---|---|---|---|---|
| P1-1 | **식생 교체**: `build_tree()`/`build_hedge()` → NVIDIA Trees 44 + Shrub 37 참조, `instanceable=True` | **최상** (씬 04 지적 직결) | ★★ | 2~3일 | P0-1 |
| P1-2 | **가로시설물 교체**: `build_bollard`/`build_bench`/`build_railing_line` → NVIDIA props_general + Poly Haven CC0 | 상 | ★★ | 2~3일 | P0-1, 라이선스 판단 |
| P1-3 | **NVIDIA Dynamic Sky 도입** — 위경도(서울 37.57/126.98)·절기·시각 구동, 구름 6종 | **상** (조건 변주 축 신설) | ★★ | 2일 | 스케일 정합(metersPerUnit 0.01) |
| P1-4 | **`UsdGeom.Mesh` 전환 (지면부터)** — UV·정점컬러·데칼·하이트필드 기반 | **상** | ★★★ | 1주 | P0-3, P0-4 |
| P1-5 | **데칼 파이프라인** — `create_mesh_decal()` + ambientCG Decal 126종 (균열·오염·마킹) | **상** | ★★ | 2~3일 | P1-4 (Mesh 필수) |
| P1-6 | **잎 SSS** — 식생 재질을 `OmniSurface` + `enable_diffuse_transmission` + `thin_walled` | 중~상 (역광 수관) | ★★ | 1~2일 | P1-1 |
| P1-7 | **사람/차량 스케일 앵커** — NVIDIA `People/` 20종 참조 배치 (IRA 안 씀, §8-11) | 상 (스케일 앵커 = 단서 ③) | ★★ | 2일 | P0-1 |

#### P2 — 1개월 이내 (파이프라인 전환)

| # | 작업 | 예상 효과 | 난이도 | 소요 | 선행조건 |
|---|---|---|---|---|---|
| P2-1 | **Replicator 이관** — `capture_pipeline()` → `rep.orchestrator.step()` + BasicWriter | **처리량 수십 배** | ★★★ | 1주 | P0-2 |
| P2-2 | **GT 낙차 맵 파이프라인** — PhysX 레이캐스트 heightfield + 픽셀 역투영 (§8-5 권장안 A) | **연구 성립 조건** | ★★★ | 1~2주 | P2-1, P1-4 |
| P2-3 | **도메인 랜덤화 축 정의** — 태양 고도/방위, HDRI, 재질, 카메라 포즈, 노출, 소품 배치 | **sim2real 핵심** | ★★★ | 1주 | P2-1 |
| P2-4 | **PointInstancer 스케일 테스트** — 잔디 10만 → 50만 → 200만, VRAM·프레임타임 계측 | 상 (밀도 3자릿수) | ★★ | 2~3일 | P1-4 |
| P2-5 | **RT↔PT 정합성 실험** — 대표 300~500뷰 양쪽 렌더, 낙차 하부 ROI 휘도 히스토그램 비교 | **논문 표 1개** | ★★ | 2일 (렌더 1.7 h) | P2-1 |
| P2-6 | **SANPO 택소노미 채택** — 31클래스를 우리 GT 스키마에 매핑, SANPO-Real 을 검증셋으로 | **논문 비교 가능성** | ★★ | 2~3일 | 없음 |

#### P3 — 조건부 / 장기

| # | 작업 | 조건 |
|---|---|---|
| P3-1 | 커스텀 MDL (삼평면 · 스토캐스틱 타일링 · displayColor 블렌딩) | P1-4 완료 후, 타일링 반복이 실제로 문제일 때 |
| P3-2 | Rivermark 배경 씬 활용 (도시 맥락) | 라이선스 "수정 금지" 판단 확정 후 |
| P3-3 | NGII 정밀도로지도 실측 연석 데이터 | 공공누리 마크 확인 / 사전협의 완료 후 |
| P3-4 | `scene_blox` 절차 씬 생성 | 33씬 수작업이 한계에 부딪힐 때 |
| P3-5 | 모션블러 (카메라 궤적 타임샘플 또는 Replicator `MotionBlur` augmentation) | P2-1 완료 후 |
| P3-6 | Isaac Sim 5.x/6.x 업그레이드 검토 | 우리 4.5 는 3 메이저 뒤짐. 단 API 파괴적 변경(semantics 등) 주의 |

### 11-2. 라이선스 결정이 먼저 필요한 것

**데이터셋을 공개 배포할 계획이 있는지**가 여러 선택을 가른다.

| 계획 | 권장 에셋 구성 |
|---|---|
| **논문 + 이미지 예시만 공개** | NVIDIA 전체(Vegetation·Rivermark·People) 사용 가능. 가장 품질 높음 |
| **데이터셋(이미지+라벨) 공개** | NVIDIA 사용 가능 **[웹검증: 시뮬레이션 산출물 배포는 AI Enterprise 불필요]**. 단 `/Isaac/Environments` USD 를 **편집하지 말 것** |
| **씬 USD 까지 공개** | **CC0(Poly Haven/ambientCG) + MIT-0(PhysicalAI-Materials) + CC-BY 로만 구성.** NVIDIA Limited Use Content·OSM 파생 제외 |

**절대 금지 [웹검증]**: Quixel Megascans(NoAI 태그), Google Photorealistic 3D Tiles(ToS 4중 위반).

### 11-3. 남은 공백 (이 조사가 답하지 못한 것)

| 항목 | 상태 | 해소 방법 |
|---|---|---|
| 변위(displacement)가 4.5 에서 실제로 되는가 | **[미검증]** — 설정 키는 존재, 2024 포럼 답변은 "미지원"(4.1 시점) | P0-3 실험 |
| `round_edges_radius` 실렌더 효과 | **[미검증]** | P0-6 실험 |
| PT DoF 가 물리 조리개인가 포스트인가 | **[미검증]** | fStop=1.4 로 PT 1장 |
| PointInstancer 4090 실한계 | **[추정]** 10⁵ 안전 / 10⁶ 조건부 | P2-4 스케일 테스트 |
| RTX 4090 SDG 실측 처리량 | **[웹검증: 공식 벤치 없음]** | `benchmark_sdg.py` (GitHub) |
| NVIDIA Vegetation 라이선스 세부 | **[추정]** `/Isaac/Environments` supplement 대상 아님 | LICENSE 파일 재확인 / NVIDIA 문의 |
| 한국 KS 점자블록·볼라드·계단 규격 치수 | **[미검증]** law.go.kr 접근 실패 | 브라우저 또는 OC 키 발급 |
| MakeHuman / SMPL-X / BEDLAM 라이선스 | **[미검증]** | 필요 시 별도 조사 (NVIDIA People 로 충분할 가능성 높음) |
| MaterialX 가 RTX 에서 신뢰성 있게 렌더되는가 | **[미검증]** — 4.5 테스트 커버리지 0 | 실험, 또는 회피(UPS/MDL 재바인딩) |
