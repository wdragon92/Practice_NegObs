# 코드 감사 — 사실화 라운드 v1 (적대적 검토)

- 감사 대상: `git diff pre-realism-v1 HEAD` + 미커밋 변경분
  (`scene_common.py` · `assets/NegObsGround.mdl` v1.3.0→v1.8.0 ·
  `scenes/main/scene01_campus_stairs.py` · `assets/scene01/download_scene01_assets.py`)
- 판정 기준: `Docs/audit_v4/user_feedback_v5_1.md` · `Docs/briefs/realism_brief_v1.md`(rev.1) ·
  `Docs/reports/realism_phase1.md` · `realism_phase2.md`
- 검증 방식: GPU 미사용. `python3 -c "import scene_common"` 이 **pxr 없이 성공**하므로
  분류기·캐시·순수 함수는 전부 **직접 실행해 실측**했다. MDL 은 두 경로 항별 대조.
- 이 문서는 **문제만** 적는다. 잘 된 부분은 생략한다.

---

## 0. 요약

| 심각도 | 건수 |
|---|---|
| **치명** | 4 |
| 중대 | 10 |
| 경미 | 9 |

치명 4건 중 3건은 **`NEGOBS_LOOK_V1=1` 로 렌더한 게이트 3차 결과를 신뢰할 수 없게 만든다.**
1건(#3)은 **`LOOK_V1=0` 에서도 발생**하므로 "회귀 0" 및 A/B 통제 전제가 이미 깨져 있다.

---

## 1. 치명

### C1. `tint` 가 NegObsGround 경로에서 통째로 버려진다 — 30씬, 최대 7배 알베도 오차

`_make_ground_pbr` 은 `tint` 를 받아서 **경고만 출력하고 무시**한다(`scene_common.py:1073-1077`).
OmniPBR 에서는 `diffuse_tint` 가 알베도에 곱해지던 값이다.

실측(전 씬 소스 파싱 + `_look_spec` 실행): **`tint` 를 넘기면서 NegObsGround 로
라우팅되는 `make_pbr` 호출 77건 / 30개 씬 파일.** 편차가 큰 것들:

| 씬 | 재질 | 클래스 | 버려지는 tint | 알베도 오차 |
|---|---|---|---|---|
| sceneD4 | `Facade` | concrete | (0.14, 0.14, 0.15) | **×7.1 밝아짐** |
| sceneD4 | `Ballast` | gravel | (0.155, 0.15, 0.145) | ×6.6 |
| scene13 | `Asphalt` | asphalt | (0.215, 0.21, 0.198) | ×4.7 |
| scene09 | `StoneStain` | stone | (0.299, 0.299, 0.263) | ×3.4 |
| scene02 | `Tunnel` | concrete | (0.32, 0.32, 0.34) | ×3.1 |
| scene15 | `RetWall` | concrete | (0.30, 0.29, 0.27) | ×3.3 |
| sceneD3 | `ChWall` | concrete | (0.55, 0.53, 0.50) | ×1.9 |
| sceneD2 | `LowerFloor` | concrete | (0.52, 0.51, 0.49) | ×2.0 |
| scene01 | `GraniteDark` | stone | (1.25, 1.25, 1.22) | ×0.80 (어두워짐) |

재현:
```bash
python3 - <<'EOF'
import re, glob, scene_common as sc
for f in sorted(glob.glob('scenes/main/scene[0-9]*.py')+glob.glob('scenes/batch1/*.py')):
    src=open(f,encoding='utf-8').read()
    for m in re.finditer(r'Looks/([A-Za-z0-9_]+)', src):
        seg=re.split(r'\n\s{4,8}M\[|\n\s*def ', src[m.end():m.end()+380])[0]
        cls,spec=sc._look_spec('/World/Looks/'+m.group(1))
        ground=(spec['mdl']=='ground') or (cls in sc._CONST_MDL_CLASSES and 'diffuse_color' in seg and 'tex_path' not in seg)
        if ground and re.search(r'\btint\s*=', seg): print(f.split('/')[-1], m.group(1), cls)
EOF
```

- 이건 조용한 실패가 아니라 **시끄러운 실패**다 — 렌더 1회당 `[룩v1][경고] … tint 미지원`
  경고가 77줄 찍힌다. Phase 2 보고서는 이를 한 번도 언급하지 않는다.
  즉 **경고를 보고도 넘겼다.** `ensure_noon_lookfix` 이중 태양 때와 같은 패턴이다.
- 게이트 3차 수치(scene07 27.8→19.6, sceneD3 34.2→30.8)는 이 오차를 포함한 값이다.
- 조치 방향: MDL 에 `diffuse_tint` 입력을 추가해 `base_color` 와 곱하거나
  (`albedo * base_color * tint`), tint 를 `base_color` 에 접어 넣는다.
  **경고로 넘길 사안이 아니다 — 처리 못 하면 해당 재질은 OmniPBR 로 폴백해야 한다.**

### C2. 차선 도색(`Looks/Lane`)이 아스팔트 텍스처로 승격된다 — 상수색 불가침 규약 위반

`_LOOK_RULES` 의 `asphalt` 키워드에 `"lane"` 이 들어 있고, `paint` 규칙에는 없다.
→ `Lane` → **asphalt** → `_CONST_MDL_CLASSES` 포함 → `_promote_const_to_texture`
→ `asphalt_diff.jpg` 바인딩 + `patch_mix=1.0` + macro + rough noise.

용례 확인 — 두 곳 모두 **중앙 파선(도로 표시)** 이다:

- `scenes/main/scene02_underpass.py:691-693` — `# 중앙 파선 (노면에 8 mm 돌출)`,
  `BOX(f"{ROOT}/Road/Dash_{k}", …, M["lane"])`, `lane_color=(0.55,0.55,0.52)  # v4-D2 차선 표시`
- `scenes/batch1/sceneN2_asphalt_patch.py:545,749-759` — `lane=dict(…, dash=3.0, gap=6.0, …)` 파선

v5.1 §4 / Phase2 §2.2 가 못박은 **"차선 도색·반사띠·점자블록은 상수색이 물리적으로 옳다"**
의 정면 위반이다. 차선이 균일하지 않으면 낙차·경계 단서로서의 기능도 무너진다.

미커밋 변경분에서 `asphalt` 텍스처를 실제로 조달했으므로(`download_scene01_assets.py`
POLYHAVEN_V5, 파일 존재 확인됨) **다음 렌더부터 즉시 발현**한다.

재현:
```bash
python3 -c "import scene_common as sc; print(sc._look_spec('/World/Looks/Lane'))"
# ('asphalt', {... 'tex': 'asphalt' ...})
python3 -c "import scene_common as sc; print(sc._promote_const_to_texture(sc.LOOK_CLASS['asphalt'],(0.55,0.55,0.52))[0])"
# .../asphalt_diff.jpg  ← 차선에 아스팔트 텍스처가 붙는다
```

조치: `_LOOK_RULES` 의 `paint` 항에 `"lane"` 추가(단, `"lane"` 만으로는
`Looks/Lane`(표시)과 차로면을 구분 못 함 — 이름 재사용이 문제이므로
`LOOK_ROLE` 정확일치표에 `"Lane": "paint"` 를 넣는 쪽이 안전하다).

### C3. `build_building` 의 `SillBand` 가 LOOK_V1 게이트 **밖**에 있다 — OFF 회귀 0 위반

`scene_common.py:1628-1642, 1654-1659`:

```python
ins = float(wd.get("inset", 0.0))
band_t = min(max(ins, 0.0), 0.15)
...
if band_t > 1e-4:                  # ← LOOK_V1 조건이 없다
    prims.append(add_box(stage, f"{prefix}/SillBand_{f}", …, parapet_mtl))
```

- `build_building` 의 기본 `window` 딕셔너리 자체가 `inset=0.15` 이고
  (`scene_common.py:1605`), 씬들도 전부 `inset=0.15` 를 넘긴다.
- 즉 **`NEGOBS_LOOK_V1=0` 에서도 층마다 새 박스가 생긴다.**
  `build_building` 호출 씬: 02·03·05·06·08·11·12·13·14·16·17·18·19·20·21 ·
  C1·C4·D3·N1·N2·N3·N4·N5 (24곳 확인).
- 결과 ①: 브리프 원칙 "`LOOK_V1=0` 은 종전과 동일" 이 깨졌다.
  결과 ②: 게이트 3차의 `off` 렌더에도 띠가 이미 들어 있으므로 **off/on A/B 가
  이 변경을 통제하지 못한다.** Phase 0 기준선(`realism_baseline.md`)과도 비교 불가.
- 부수 위험: 띠는 파사드에서 0.15 m **돌출**한다. `sceneN3_trompe_loeil.py:141` 은
  포디엄(y 9.55~10.05)과 1층 창(y 9.98~10.01)의 근접 배치를 명시적으로 계산해 둔 씬인데,
  0.15 m 돌출 띠가 그 여유를 먹는다. [추정] 육안 확인 필요.

재현: `NEGOBS_LOOK_V1=0` 으로 scene02 를 렌더해 `/World/Scene02/Building_*/SillBand_*`
프림이 존재하는지 확인. 또는 `git stash` 로 pre-realism 과 프림 수 비교.

조치: `if LOOK_V1 and band_t > 1e-4:` 로 게이트하거나, 감독이 "이건 룩 레이어가 아니라
씬 공용 기하 개선"이라고 판단한다면 **기준선을 다시 잡고 A/B 를 재설계**해야 한다.
지금처럼 둘 다 아닌 상태가 최악이다.

### C4. 웨더링 기단 오염이 **월드 z<0 전면**에 걸린다 — 낙차 깊이와 상관된 인공 알베도 단서

`negobs_weather`(`NegObsGround.mdl:464-467`):

```
hz      = (pw.z - grime_z0) + grime_edge*(noise*2-1)
m_grime = 1 - smoothstep(0, max(grime_height,1e-3), hz)
```

`grime_z0` 기본값 **0.0**(`NegObsGround.mdl:598`)이고, `scene_common` 은
`grime_z0` 를 **한 번도 설정하지 않는다**(`_make_ground_pbr:1056-1068` 은
`grime_strength/desat/height/splash/streak/dust/weather_rough` 만 쓴다).

따라서 **월드 z < 0 인 모든 면에서 `m_grime = 1.0`** → `darken = grime_strength`,
`desat = grime_desat` 가 **균일하게** 걸린다.

| 월드 z | m_grime | concrete(_W_STRUCT, grime 0.35) 알베도 배율 |
|---|---|---|
| −3.0 m | 1.000 | ×0.65 |
| −0.8 m | 1.000 | ×0.65 |
| 0.0 m | 1.000 | ×0.65 |
| +0.20 m | 0.500 | ×0.825 |
| +0.40 m | 0.000 | ×1.00 |

(`grime_height = w["grime_h"] = 0.40`, smoothstep 이므로 z≤0 은 전부 포화)

영향 씬 — **낙차 하부 레벨이 z<0 인 씬 전부**. 코드로 확인한 것:

- `sceneD3_drainage_channel` — 측구 `depth=0.80`, 인버트 z=−1.05
  (`sceneD3:125-127,737`), 채널 벽 재질 `ChWall`/`Conc` = **concrete 클래스**.
  → 채널 내부 전체가 균일하게 ×0.65. **게이트 3씬 중 하나다.**
- `sceneD2_floor_opening` — `LowerFloor`/`LowerWall`/`Skirt` = concrete
- scene02 지하도 · scene08 선큰 광장 · scene09 가트 · scene17 둔치 [추정 — 이름상 명백하나 z 미확인]

왜 치명인가:
1. **연구 타당성**: 이 데이터셋의 목표는 "RGB 맥락 단서로 비가시 낙차를 추정"이다.
   여기에 **"깊을수록 어둡다"는 결정론적 알베도 규칙**을 심으면 네트워크가 기하가
   아니라 밝기로 낙차를 푸는 지름길을 얻는다. GT 낙차와 상관된 합성 단서다.
2. **flat% 역효과**: 균일 곱셈이라 결(고주파)은 0 추가하고 휘도만 낮춘다.
   sceneD3 의 `flat_gnd` 가 28.1 로 거의 안 움직인 이유의 후보다.
3. `scene_common.py:205-208` 주석이 **바로 이 위험을 경고**하면서
   "지면 계열(paving/asphalt/soil/gravel)은 grime 0" 으로만 막았다.
   그러나 실측상 `concrete` 클래스가 215종 중 **46종**을 흡수하고 그 안에
   `Slab`·`ConcreteFloor`·`LowerFloor`·`Lower`·`Stage`·`Trough`·`Skirt` 같은
   **수평 지면**이 들어 있다. 클래스 기반 방어는 실패했다.

조치: ① `grime_z0` 를 씬 지반 z 로 넘기거나, ② `m_grime` 을 `nw.z` 로 게이팅해
**수직면에만** 걸거나(원래 의도: "지면 위에 서 있는 수직 구조물"), ③ 하한
`smoothstep(-h, 0, hz)` 를 추가해 밴드 아래로 무한 확장되지 않게 한다.
**셋 중 무엇이든 하기 전에는 웨더링을 켠 렌더를 판정에 쓰면 안 된다.**

---

## 2. 중대

### M1. 상수색 금속의 `metallic` 이 소실된다

`_CONST_MDL_CLASSES` 에 `metal`·`wood`·`veg` 가 들어 있어 상수색 금속이
`_make_ground_pbr` 로 간다. 그런데 `_make_ground_pbr` 시그니처에 **`metallic` 이 없고**,
NegObsGround 는 헤더에 적힌 대로 `metalness=0` 경로만 이식했다.

실측: `metallic=` 을 넘기면서 NegObsGround 로 가는 호출 **113건**.
금속 이름 37종(`Rail, Pole, Bollard, Steel, Shutter, Galv, Gate, Fence, Rebar,
Mullion, Hvac, Lid, Bin, Wire, Crane, Iron, RailHead, MFrame, …`).
→ **난간·볼라드·셔터·펜스가 전부 비금속으로 렌더된다.**

재현: 위 C1 재현 스크립트에서 `tint` 를 `metallic` 으로 바꿔 실행.

### M2. 3단 재질 정책이 코드와 어긋난다 (`veg`/`metal`/`wood` → NegObsGround)

Phase2 보고서 §2.2 표: *식생·금속·목재 = OmniPBR*.
실제 코드: 이 3클래스가 `_CONST_MDL_CLASSES`(`scene_common.py:765-767`)에 있어
**상수색인 경우 NegObsGround 로 간다.** 실측 대상 이름 59종
(metal 37 · veg 13 · wood 6 · nosing/curb 4).

결과: 수관(`Canopy*`)·잎(`Leaf*`)·갈대(`Reed`)가 지면용 트라이플래너 MDL 로 렌더되고,
동시에 M1(metallic 소실)·C1(tint 소실)을 함께 맞는다.
**보고서가 서술한 정책과 구현이 다르므로 보고서를 근거로 한 판정 전부가 재검토 대상이다.**

또한 `saturation_a` 는 `_make_ground_pbr` 안에서만 세팅되므로,
**텍스처 있는** veg(0.76)·wood(0.88) 는 채도 계수를 전혀 못 받는다 —
같은 클래스인데 상수색이면 탈색되고 텍스처면 안 되는 비일관 동작이다.

### M3. 변위 스킨의 **28%** 가 슬래브 상면 아래로 파고든다

`_ground_skin` 은 `ztop = 슬래브상면 + 1.5 mm` 에서 시작해 3옥타브 노이즈를
**부호 있는 값**(`rng.random()-0.5`)으로 더한다. 진폭 합 = `0.010*(1+0.6+0.36)/2 = ±9.8 mm`
> 부상 1.5 mm 이므로 **음의 변위 구간은 원 Cube 안으로 들어간다.**

실측(`_ground_skin` 의 수치부를 그대로 재현):

| 슬래브 | 격자 | 슬래브 상면 기준 ZZ 범위 | 상면 **아래** 정점 | 최대 침투 |
|---|---|---|---|---|
| 20×20×0.3 | 165×165 | −6.71 ~ +9.80 mm | **28.3 %** | 6.71 mm |
| 8×6×0.2 | 65×49 | −5.80 ~ +9.12 mm | 25.2 % | 5.80 mm |
| 40×30×0.4 | 170×170 | −6.89 ~ +9.79 mm | 28.7 % | 6.89 mm |

증상: 오목부에서 원 Cube 의 **평탄한 상면이 그대로 드러나고**, 교차선에서
하드 컨투어/z-fighting 이 생긴다. 즉 "미세 기복" 의도가 면적의 1/4 이상에서
정확히 반대(완전 평탄 패치 + 인공 등고선)로 나타난다.

재현: 위 표를 만든 스크립트는 `_ground_skin` 본문(scene_common.py:700-733)을
그대로 복사해 pxr 없이 실행한 것. 결정성은 동일 시드 2회 실행 `np.array_equal == True` 로 확인.

조치: `ztop += amp_m * (1+0.6+0.36) / 2` (≈ +9.8 mm) 만큼 더 띄우거나,
변위를 `[0, +2a]` 로 오프셋해 항상 상면 위에 있게 한다.

### M4. 스킨 3옥타브(0.07 m)가 항상 앨리어싱된다

메시 간격은 `spacing=0.12 m`(그리고 `max_n=170` 상한 때문에 큰 슬래브는 0.18~0.24 m)인데
노이즈 격자는 파장 0.07 m 로 만든다 → **노이즈 격자 셀이 메시 샘플보다 촘촘하다.**

| 슬래브 폭 | 메시 간격 | 0.55 m 옥타브 | 0.19 m | 0.07 m |
|---|---|---|---|---|
| 19.9 m | 0.121 m | 격자 37 (ok) | 105 (ok) | **285 → ALIAS** |
| 29.9 m | 0.176 m | 55 (ok) | 158 (경계) | **428 → ALIAS** |
| 5.9 m | 0.120 m | 11 (ok) | 32 (ok) | **85 → ALIAS** |

결과: 3옥타브(진폭 36 %)는 의도한 7 cm 잔결이 아니라 **정점별 난수**가 된다.
게다가 정점 노멀을 그 필드의 `np.gradient` 로 만들므로 **노멀에 고주파 잡음**이 실린다.
"정점 변위가 최대 시각 기여"(Phase1 E9)의 정체가 이 잡음일 가능성이 있다. [추정]

조치: `spacing` 을 최소 옥타브의 1/3 이하로 낮추거나(비용 폭증), 3옥타브를 제거하거나,
`max_n` 상한에 맞춰 옥타브를 동적으로 잘라낸다.

### M5. 채도 자기교정 knee 0.30 이 텍스처 채도 분포 위에 있어 역할 계수가 사문화됐다

`_SAT_KNEE = 0.30`. 실측 — 저장소 전 TEX 역할의 `_texture_sat`:

| 역할 | sat | knee 통과 |
|---|---|---|
| grass | 0.685 | ○ |
| dirt_park | 0.500 | ○ |
| brick_red / gravel | 0.390 / 0.379 | ○ |
| marble_light | 0.315 | ○ (t=0.075 → 계수 2.6 %만 발현) |
| **rock_face / stone_worn / sandstone** | 0.265 / 0.259 / 0.259 | **×** |
| **concrete_wall** | 0.209 | **×** |
| **rock_wall** | 0.179 | **×** |
| **stone_flag / asphalt / granite_dark / paving_interlock** | 0.068 / 0.067 / 0.017 / 0.012 | **×** |

즉 **`stone`(계수 0.66)·`asphalt`(0.90)·`paving`(1.00) 은 사실상 한 번도 발동하지 않는다.**
그런데 Phase2 보고서 §1 은 scene07 sat 0.319→0.282 를
*"석재·자연물 계열 역할별 하향이 의도대로 작동"* 이라고 귀속했다. **그 귀속은 틀렸다** —
실제 원인은 모든 지면 텍스처 재질에 무조건 걸리는 `desat_bright_a=0.30` 과
macro 채도 변조(`sat_m`)일 가능성이 높다. [추정 — GPU 없이 인과 분리 불가]

추가 방법론 문제: `_SAT_KNEE=0.30` 은 **렌더 이미지의 sat_mu**(0.298 vs 실사 0.158) 에서
가져온 값인데, `_effective_sat` 는 이를 **텍스처 알베도 채도**에 적용한다.
두 값은 측정 공간이 다르다(조명·톤매핑 유무). 단위가 다른 임계를 옮겨 쓴 것이다.

재현:
```bash
python3 -c "
import scene_common as sc
for r in sorted(sc.TEX):
    print(r, round(sc._texture_sat(sc.tex_path(r,'diff')),3))"
```

### M6. `_effective_sat` 가 승격 경로에서 **색이 아니라 비율**로 채도를 판정한다

`_make_ground_pbr:1040` → `_effective_sat(spec, diff, base_color)`.
승격 경로에서 `base_color` 는 색이 아니라 **`의도색 / 텍스처평균` 비율 벡터**다
(최대 2.5까지 감). `_rgb_sat` 를 여기에 적용하면 물리적 의미가 없는 수를 knee 와 비교한다.

실측 — 같은 클래스·같은 텍스처인데 씬이 고른 상수색에 따라 결과가 흔들린다:

| 클래스 | 계수 | 상수색 | 적용된 `saturation_a` | 텍스처 채도 기준이면 |
|---|---|---|---|---|
| soil | 0.74 | (0.36,0.35,0.33) | 0.799 | 0.740 |
| soil | 0.74 | (0.55,0.55,0.53) | 0.765 | 0.740 |
| soil | 0.74 | (0.30,0.30,0.30) | 0.740 | 0.740 |
| gravel | 0.78 | (0.36,0.35,0.33) | 0.975 | 0.913 |
| brick | 0.88 | (0.30,0.30,0.30) | 0.939 | 0.946 |

의도(“재질 자신의 채도를 보고 과채도일 때만 낮춘다”)와 다르다.
`base_color` 가 비율일 때는 `diff` 텍스처 채도를 봐야 한다.

### M7. `base_color` 증폭 상한 2.5 → 알베도 > 1 (에너지 비보존)

`_promote_const_to_texture`: `bc = clamp(의도색/텍스처평균, 0.05, 2.5)`.
실측 예 — asphalt 텍스처(평균 ≈0.35)에 상수색 (0.55,0.55,0.53) →
`base_color = (1.55, 1.56, 1.60)`. MDL 은 `albedo = A.albedo * base_color` 를
그대로 `df::diffuse_reflection_bsdf(tint:)` 에 넣는다.
텍스처 밝은 텍셀(≈0.8) × 1.6 = **1.28**, 여기에 `macro`(최대 1.12)까지 곱해 **≈1.43**.
PT 에서 에너지 비보존 알베도는 다중 바운스에서 밝기 폭주·파이어플라이의 원인이다.

조치: `bc` 상한을 1.0/텍스처최대 로 잡거나, 승격 후 albedo 를 clamp 한다.

### M8. 역할 오분류 — 키워드 순서 충돌로 실제 씬 재질이 잘못 간다 (§3 상세)

확정 오분류 중 결과가 실재하는 것:

| 이름 | 실체 | 분류 | 결과 |
|---|---|---|---|
| `WetRock` (scene12) | 젖은 암벽 (텍스처 rock_wall) | **water** (`"wet"` 이 `"rock"` 보다 먼저) | mdl=omni → **경사면 큐빅 투영 늘어남이 그대로 남는다.** MDL 도입의 유일한 목적이 이건데 정작 암벽이 빠졌다 |
| `StoneMoss` (scene09) | 이끼 낀 석재 | **veg** (`"moss"`) | mdl=omni + sat 0.76 |
| `DeckConcrete` (scene06) | 교량 콘크리트 상판 | **wood** (`"deck"`) | mdl=omni + sat 0.88. 대면적 지면인데 지면 처방을 못 받음 |
| `Seam` (scene09) | 석재 줄눈 | **water** (`"sea"`) | 처방 없음 |
| `Container_` (sceneD1) | 골판 강판 컨테이너 | concrete → `concrete_wall` **텍스처 승격** | 강판에 콘크리트 벽 |
| `PavRoof` (scene09) | 지붕 | paving → `paving_interlock` 승격 | 지붕에 보도블록 |
| `Polish` (scene13) | 폴리시 마감 바닥 | stone → `stone_flag` 승격 | 판석 |
| `Joint` (D4/N1~N5) | 신축이음(폭 수 cm) | asphalt → `asphalt` 승격 (1.2 m 타일) | 수 cm 스트립에 1.2 m 텍스처 크롭 |
| `Ridge`/`Crest_`/`Trough` | 지형 능선·골 | concrete → `concrete_wall` 승격 | 지형에 콘크리트 벽 |
| `Far`/`City`/`Dark`/`Bldg` | 원경 실루엣 | concrete → `concrete_wall` 승격 | 원경에 1.2 m 타일 |

### M9. `ensure_noon_lookfix` 캐시가 `NEGOBS_SUN_CAP_DEG` 변경을 무시한다

캐시 판정은 `mtime(out) >= mtime(src)` 뿐(`scene_common.py:1832-1834`).
새로 추가한 `NEGOBS_SUN_CAP_DEG` 를 바꿔도 **기존 `_lookfix.exr` 이 그대로 재사용**되고
경고도 없다. 구름 HDRI 전환 시 "0.6° 로 바꿨는데 잘린 원반이 그대로"가 된다.

또한 `except` 가 여전히 **모든 실패를 삼키고 `src_path` 를 반환**한다 — 이중 태양 실패
모드는 RGBA 트리거 하나만 없어졌을 뿐 구조적으로 그대로다.
조치: 파라미터를 파일명에 넣거나(`_lookfix_cap0.6.exr`), 실패 시 `sys.exit(1)` 옵션 추가.

### M10. PIL 부재/실패 시 룩 레이어가 **조용히** 절반 꺼진다

`_texture_mean` / `_texture_sat` 는 `except Exception: v = None` 으로 **아무것도 출력하지 않고**
`None` 을 캐시한다. `None` 이면:

- `_promote_const_to_texture` → 승격 포기 → 상수색 MDL 모드로 폴백 (경고 없음)
- `_effective_sat` → 1.0 → 채도 계수 전면 무효 (경고 없음)

즉 Isaac 파이썬 환경에 Pillow 가 없으면 **게이트 수치가 조용히 달라진다.**
`check_assets` 같은 하드 체크가 없다. `NEGOBS_LOOK_V1=1` 인데 아무것도 안 걸린 상태를
`look_report()` 로도 구분하기 어렵다(§경미 m4 참조).

---

## 3. 경미

- **m1. 스킨 페이스 와인딩이 −Z**: `idx += [a, a+1, a+ny+2, a+ny+1]` 는 (i,j)→(i,j+1)→(i+1,j+1)→(i+1,j),
  +Z 에서 보면 **시계방향**(shoelace = −2) → USD `rightHanded` 기본에서 **면 노멀이 아래**.
  정점 노멀은 +Z 로 저작돼 있고 RTX 는 기본적으로 프라이머리 레이 백페이스 컬링을 안 하므로
  현재는 보이겠지만, 컬링·`doubleSided` 관련 설정이 바뀌면 스킨이 통째로 사라진다. [추정]
- **m2. `bump_factor_a` 가 호출자 인자를 덮어쓴다**: 미커밋 변경
  `float(spec.get("bump", bump))` — 클래스에 `bump` 키가 있으면 씬이 넘긴 `bump` 가
  **항상 무시**된다(concrete 1.6 / paving 1.4 / stone 1.5 / asphalt 1.4).
  텍스처 재질까지 포함해 전역 적용이므로 씬별 노멀 강도 튜닝이 전부 사라진다.
- **m3. 승격 타일 크기가 1.2 m 고정**: `spec.get("tex_scale", 1.2)` 인데 **어느 클래스도
  `tex_scale` 을 정의하지 않는다.** 조달 노트는 `asphalt_02 = 3.0 m 타일`이라고
  명시했는데 1.2 m 로 깔면 2.5배 축소돼 텍셀 밀도·패턴 크기가 틀린다.
- **m4. `look_report()` 가 `promoted` 카운터를 출력하지 않는다**: `ground/omni_tex/const/
  skipped/bevel/detail/skin/const_mdl/weather` 만 찍는다. 이번 라운드의 핵심 신규 경로가
  몇 번 걸렸는지 로그로 확인할 수 없다.
- **m5. `dust_*` 는 사문**: `_W_STRUCT`/`_W_STONE`/`_W_EDGE` 어디에도 `dust` 키가 없어
  `dust_strength` 는 항상 0. MDL v1.6.0 의 "③ 상향면 먼지"는 구현만 되고 한 번도 안 켜진다.
- **m6. 낙차 에지 베벨이 승인값을 넘는다(셰이딩 한정)**: `build_straight_stairs` 는 한 단을
  **박스 1개**로 만들고 재질 1개를 바인딩하므로, 그 재질의 클래스가 계단 코 베벨을 결정한다.
  실측상 `Stair`/`Riser_`/`Slab`/`Concrete` 는 전부 **concrete = 0.020 m**로,
  승인된 nosing 값 0.012 의 1.67배다. `state::rounded_corner_normal` 은 노멀만 바꾸므로
  **GT 기하·실루엣은 불변**이라 규약 위반은 아니지만, 낙차 에지의 하이라이트 폭이
  씬 이름에 따라 제각각이 된다.
- **m7. MDL 헤더 개정이력이 v1.6.0 에서 멈췄다**: `anno::version(1,8,0)` 인데 파일 상단
  주석 블록에는 v1.7.0(`base_color`)·v1.8.0(조기 탈출) 기록이 없다.
  `_GROUND_SCALE_FIX` 실측 이력처럼 남겨야 한다.
- **m8. `build_sign` 의 `CreateSubdivisionSchemeAttr("none")` 도 게이트 밖**이다.
  `refinementLevel=0` 이라 현재 무해하지만, C3 와 같은 부류의 무게이트 변경이다.
- **m9. 스킨 조립 비용**: 큰 슬래브 1장당 정점 27,556 / 쿼드 27,225.
  `Gf.Vec3f` 생성을 제외한 순수 파이썬 이중 루프만 측정해도 **≈19 ms/장**이고,
  points·normals 두 번 도므로 실제로는 그 수 배다. 씬당 슬래브가 여러 장이면
  조립 시간이 수백 ms~초 단위로 늘고 삼각형도 슬래브당 ≈55 k 증가한다.
  `np.stack`/`tolist()` 로 벡터화 가능.

---

## 4. 항목 3 — 역할 분류기 실측 결과

`scenes/main/scene[0-9]*.py` + `scenes/batch1/*.py` (35파일)에서 `Looks/<이름>` 을
전수 추출 → **215종**(보고서 수치와 일치) → `scene_common._look_spec()` 실측.

```bash
python3 - <<'EOF'
import re, glob, collections, scene_common as sc
names=collections.Counter()
for f in glob.glob('scenes/main/scene[0-9]*.py')+glob.glob('scenes/batch1/*.py'):
    names.update(re.findall(r'Looks/([A-Za-z0-9_]+)', open(f,encoding='utf-8').read()))
by=collections.defaultdict(list)
for n in names: by[sc._look_spec('/World/Looks/'+n)[0]].append(n)
for c in sorted(by): print(c, len(by[c]), sorted(by[c]))
EOF
```

### 4.1 분포

| 클래스 | 수 | 비고 |
|---|---|---|
| concrete | **46** | 가장 넓은 그물. 지면·원경·지형까지 흡수 |
| metal | 35 | |
| paint | 20 | |
| veg | 19 | |
| wood | 16 | |
| paving | 15 | |
| sign | 14 | |
| stone | 11 | |
| glass / water | 6 / 6 | |
| brick / asphalt | 5 / 5 | |
| misc | **4** (Bag, Emit, Rubber, Snow) | 보고서 "잔여 7종"보다 개선 |
| curb / gravel / soil / nosing | 4 / 3 / 3 / 3 | |

### 4.2 **상수색이 물리적으로 옳은 역할이 텍스처 승격 대상으로 샜는가** — 1건 발견

- **샜다: `Lane`(차선 파선) → asphalt → 아스팔트 텍스처 승격.** → **치명 C2**
- 그 외 도색·표지 계열은 전부 `paint` 로 정확히 떨어졌다:
  `Band, BandBlack, BandDark, BandYellow_, BollardBand, CutLine, GaugeBand, Line,
  LineBand, LineWhite, LineYellow, Paint, Paint_, RoadPaint, ShedBand, Tactile,
  Tape, TempTape, WarnR, WarnY` (20종)
- 사인/유리/수면도 누락 없음: `Sign*, Placard*, Panel, Lbox*, Mailbox, SignField,
  SignBar` / `Glass, CityGlass, ShopGlass, GlassEmis, Window, Lens` / `Water, Water_, Sea, Tide`

### 4.3 **낙차 에지가 다른 클래스로 샜는가** — 샜다

`nosing` 에 떨어진 것은 `Nosing, Step, Tread` **3종뿐**이고, `curb` 는
`Curb, Cope, Coping, Verge` 4종뿐이다. 실제 계단·연석 기하를 쓰는 재질 대부분은
`concrete`(46종, `Stair`·`Riser_`·`Slab`·`Lower`·`Upper`·`Fascia`·`Skirt` …)로 간다.
→ 베벨 0.020(승인값 0.012 초과, §m6) + `_W_STRUCT` 웨더링(§C4)을 받는다.

### 4.4 식생/금속/유리 사고

| 이름 | → | 사고 유형 |
|---|---|---|
| `StoneMoss` | veg | 석재 → 식생 |
| `TreePit` | veg | 수목 보호 그레이팅/토양 → 식생 |
| `WetRock` | water | 암벽 → 수면 |
| `Seam` | water | 줄눈 → 수면 |
| `DeckConcrete` | wood | 콘크리트 → 목재 |
| `ContainerDoor_` | wood | 강재 도어 → 목재 |
| `Duck`, `DuckTop`, `Beak` | metal | 오리 조형물 → 금속(+콘크리트 그레인 디테일 노멀) |
| `LboxFrame` | sign | `"lbox"` 가 `"frame"` 보다 먼저 |
| `Valley` | paving | `"alley"` 부분문자열 충돌(concrete 의 `"valley"` 보다 앞) |
| `RoofTile`류 [가정] | paving | `"tile"` 이 `"roof"` 보다 앞 (현 저장소엔 미출현) |

**근본 원인은 규칙 순서다.** `water` 의 `"wet"`/`"sea"`, `veg` 의 `"moss"`,
`wood` 의 `"deck"`/`"door"`, `paving` 의 `"alley"` 가 각각 더 구체적인 뒤쪽 규칙을 가로챈다.
"더 구체적인 것을 먼저" 주석과 실제 순서가 어긋난 지점들이다.

---

## 5. 항목 5 — MDL `patch_mix<=0` 조기 탈출 동치성 판정

**판정: 수학적으로 동치. 감독 주장 성립.** (부동소수점 연산 순서만 다름)

일반 경로에 `patch_mix = 0` 을 대입하면 `patch_m = 0 * smoothstep(...) = 0`.
`math::lerp(a, b, 0) == a` 이므로 `s2` 는 모든 항에서 소거된다.

### 5.1 항별 대조

| 항 | 일반 경로 (`patch_mix=0` 대입) | 조기 탈출(v1.8.0) | 동치 |
|---|---|---|---|
| 기본 샘플 | `s1` | `s1` | ○ |
| `macro` | `clamp(1+macro_amp*(N(mwl,2,0.0)*2−1), 0, 2)` | 동일 식 인라인 | ○ (같은 phase 0.0) |
| `sat_m` | `clamp(1+macro_amp*(N(mwl,2,5.1)*2−1), 0, 1.3)` | 동일 식 인라인 | ○ (phase 5.1) |
| `rn` | `rough_noise*(N(rnwl,2,11.3)*2−1)` | 동일 식 인라인 | ○ (phase 11.3) |
| albedo 기저 | `lerp(s1.alb, s2.alb, 0) * macro` = `s1.alb*macro` | `s1.alb * macro` | ○ |
| `lum` | `luminance(alb)` — **1회 계산 후 3항이 공유** | `lum0` 동일 | ○ |
| 채도 A (`sat_m`) | `lerp(gray, alb, sat_m)` | 동일 | ○ |
| 채도 B (`saturation`) | 2번째 적용 | **3번째 적용** | ○ (아래 5.2) |
| 채도 C (`desat_bright`) | 3번째 적용 | **2번째 적용** | ○ (아래 5.2) |
| rough | `clamp(floor + mult*lerp(s1.r,s2.r,0) + rn, .02, 1)` | `clamp(floor + mult*s1.rough + rn, .02, 1)` | ○ |
| nrm | `normalize(lerp(s1.nrm, s2.nrm, 0))` = `normalize(s1.nrm)` | `s1.nrm` | ○ (`negobs_sample_tri` 가 이미 `normalize` 해서 반환) |
| spec | `spec` | `spec` | ○ |

### 5.2 채도 3단의 순서가 뒤바뀐 건에 대한 증명

세 연산 모두 **동일한 고정점 `gray = color(lum)` 을 향한 아핀 축소**다
(`lum` 은 세 항 사이에서 재계산되지 않는다):

```
A: alb ← lerp(gray, alb, sat_m)        = gray + sat_m       ·(alb−gray)
B: alb ← lerp(gray, alb, saturation)   = gray + saturation  ·(alb−gray)
C: alb ← lerp(alb, gray, d)            = gray + (1−d)       ·(alb−gray),  d = desat_bright·smoothstep(0.45,0.75,lum)
```

`smoothstep` 인자 `lum` 도 두 경로에서 같은 값이므로 `d` 도 같다.
따라서 합성 결과는 어느 순서든 `gray + (sat_m · saturation · (1−d))·(alb−gray)`.
**스칼라 곱의 교환법칙이므로 동치.** 남는 차이는 부동소수점 반올림 순서뿐(≪ 1 LSB).

### 5.3 단, 검증되지 않은 주장 2건

- **"`patch_mix` 는 uniform 이라 이 분기는 컴파일 타임에 접힌다"** — [추정].
  MDL 클래스 컴파일에서는 uniform 파라미터도 런타임 인자로 남을 수 있다.
  다만 그 경우에도 **동적 분기로 페치를 건너뛰므로 성능 이득 자체는 성립**한다
  (실측 404 s → 정상화가 그 증거).
- **레이어 B 는 여전히 무조건 호출된다**(`NegObsGround.mdl:678-684`).
  `scene_common` 은 항상 `use_blend=False` 인데 `patch_mix_b` 기본값이 1.0 이라,
  B 가 DCE 되지 않는 컴파일 모드에서는 **s2 를 포함한 전체 레이어 비용이 그대로 남는다.**
  v1.8.0 의 성능 논리(uniform 분기가 접힌다)가 참이면 `use_blend` 삼항도 접혀 B 가
  소거되므로 문제없고, 거짓이면 v1.8.0 이득의 상당 부분이 B 에서 되돌아온다.
  **둘 중 어느 쪽인지 확인되지 않았다** — `use_blend==false` 일 때 B 를 아예 만들지 않도록
  방어적으로 `patch_mix_b` 를 `use_blend ? patch_mix_b : 0.0` 로 넘기는 것을 권한다.

---

## 6. 항목 1 — `LOOK_V1=0` 무영향 검증 결과

`pre-realism-v1` 과 함수 단위 diff(주석 제외) 후 코드 경로 추적:

| 함수 | 변경줄 | LOOK_V1=0 영향 | 판정 |
|---|---|---|---|
| `make_pbr` | 73 | 신규 코드 전부 `if LOOK_V1 …` / `if _look_omni is not None` 안. `_look_omni` 는 `LOOK_V1` 일 때만 non-None | **무영향 ○** |
| `add_box` | 14 | 전부 `if LOOK_V1 and _skin_wanted(...)` 안(단축평가로 `_skin_wanted` 도 미호출) | **무영향 ○** |
| `build_building` | 24 | **게이트 없음** — `inset` 만 있으면 `SillBand` 생성 | **회귀 ✗ (C3)** |
| `build_sign` | 6 | `CreateSubdivisionSchemeAttr("none")` 무게이트. `refinementLevel=0` 이라 결과는 동일 | 무해하나 무게이트 (m8) |
| `capture_pipeline` | 22 | `print(look_report())` 추가(출력만) + PT 가속은 `NEGOBS_PT_FAST` 게이트 | 무영향 ○ |
| `ensure_noon_lookfix` | 19 | `[...,:3]` 는 3채널 EXR 에서 항등. `cap_deg` 기본 1.5 = 종전 | 무영향 ○ (단 M9) |
| `build_tree` / `build_hedge` | 0 | — | ○ |

**scene01 구조 통일**(사용자 승인분)은 별도로 검증했다:

- 로컬 `make_pbr` → `sc.make_pbr` 위임: 로컬판이 넘기던 인자 집합
  (`diff/nor/rough/scale_m/tint/metallic/roughness_const/diffuse_color/bump`)이
  `sc.make_pbr` 의 같은 이름 인자에 1:1 대응하고, `sc.make_pbr` 의 추가 분기
  (`uv_mode`/`emission_*`/`specular_level`)는 전부 기본값으로 비활성. **동치 ○**
- 자체 캡처 블록 → `sc.capture_pipeline`: 파일명(`{mode}_noon_{vname}.png`),
  manifest 병합 로직, 안정화 대기(40회), 초기 워밍업(30회)까지 문자 단위로 동일.
  워밍업만 확인 필요했는데 `pt_total_spp=512`(scene01:224) → `512+60 = 572` =
  `capture_pipeline` 의 하드코딩 `572`. **동치 ○**
  (단 향후 scene01 의 `pt_total_spp` 를 바꾸면 워밍업이 따라가지 않는다 — 잠재 함정)

---

## 7. 항목 2 — 결정성 검증

| 대상 | 판정 | 근거 |
|---|---|---|
| `_ground_skin` 시드 | **결정적 ○** | `zlib.crc32(str(path).encode()) % 100000`. `hash()` 제거 확인. `PYTHONHASHSEED` 무관 |
| `np.random.default_rng(seed)` | **재현 가능 ○** | 같은 시드 2회 실행 결과 `np.array_equal == True` 실측 |
| `_TEXSAT_CACHE` / `_TEXMEAN_CACHE` | **순서 무관 ○** | 경로 키 → 값이 파일 내용만의 함수. 삽입 순서가 값에 영향 없음. 다만 실패 시 `None` 을 캐시하므로 **일시적 실패가 프로세스 수명 동안 고착**된다 |
| PIL `thumbnail((64,64))` | **환경 의존 [추정]** | 리샘플 필터·`reducing_gap` 기본값이 Pillow 버전에 따라 달라 `base_color` 가 버전 간 미세하게 달라질 수 있다. 같은 환경 안에서는 결정적 |
| `negobs_noise` (MDL) | 결정적 [추정] | 월드 좌표·파장·phase 만의 함수. 코드상 시간·프레임 의존 없음 (GPU 미실행이라 실측 아님) |

---

## 8. 항목 4 — 변위 스킨 안전성

### 8.1 제외 규칙은 **충분하다**

`_skin_wanted` 4중 방어: ① `sx<4 or sy<4` 배제 ② `sz>0.8 or sz>=min(sx,sy)*0.5` 배제
③ 기하 경로·재질 경로 양쪽에 `_SKIN_DENY` 토큰 검사
(`stair, step, tread, riser, nosing, curb, ramp, landing, deck, platform, edge, lip, sill`)
④ `_look_spec` 클래스가 `_SKIN_CLASSES` 인지.

- `build_straight_stairs` 의 단은 `tread`(≈0.3 m) < 4 m → ①에서 배제.
- `build_arc_steps` 는 `add_box` 를 안 쓰고 `UsdGeom.Cube` 직접 정의 → 스킨 경로 자체가 없음.
- `_oriented_box`(경사 슬래브·램프)도 `add_box` 미경유 → 경사면에는 스킨이 절대 안 붙는다.
- **계단·연석·데크가 새어 들어갈 경로는 찾지 못했다.**

### 8.2 그러나 스킨 자체가 원 슬래브를 **가린다** → **M3 참조**

설계 의도("상면보다 아주 살짝 위")가 진폭 계산과 어긋나 있다.
`+1.5 mm` 부상 vs `±9.8 mm` 변위 → 면적의 **25~29 %** 가 슬래브 내부로 침투.
z-fighting 조건은 **정확히 교차선 근방**이며, 오목부 전체에서 원 Cube 상면이 이긴다.

### 8.3 승용 조건② ("낙차 에지 실루엣 보존")은 지켜졌다

- 스킨은 `edge=0.05 m` 안쪽으로 들어가고, 변위에 `taper=0.60 m` 경계 테이퍼가 곱해져
  슬래브 가장자리 0.65 m 이내는 변위 0. 실측 확인.
- 원 Cube 는 삭제·수정되지 않으므로 GT 낙차 기하 불변. **○**

---

## 9. 항목 6 — 예외 처리·실패 모드 (조용한 실패 목록)

| 위치 | 처리 | 위험 |
|---|---|---|
| `_texture_mean` / `_texture_sat` | `except Exception: v=None`, **출력 없음** | **M10 — 승격·채도가 통째로 무음 무효화** |
| `ensure_noon_lookfix` | `except: print(경고); return src_path` | **M9 — 이중 태양 실패 모드 구조 유지** (RGBA 트리거만 제거됨) |
| `_promote_const_to_texture` | `except: print(경고); 원색 반환` | 경고는 나오나 렌더는 계속 → 게이트 수치가 조용히 달라짐 |
| `add_box` 스킨 | `except: print(경고)` | 스킨 없는 씬과 있는 씬이 섞여도 진행됨 |
| `_skin_wanted` | `except: return False` (`mtl.GetPath()`) | 재질 경로 조회 실패 시 조용히 스킨 미적용 |
| `_make_ground_pbr` tint | `print(경고)` 만 하고 **계속 진행** | **C1 — 렌더당 77줄 경고가 무시된 실적이 있다** |
| `make_pbr` `_tex` 컬러스페이스 | `except: pass` | 종전 코드 유지 |

**공통 결론**: 이 프로젝트의 확립된 실패 패턴(`ensure_noon_lookfix` 이중 태양)이
룩 레이어에 **그대로 복제**됐다. "경고만 찍고 계속"은 33씬 배치 렌더에서 사실상 무음이다.
최소한 `capture_pipeline` 시작 시 `look_report()` 옆에 **누적 경고 카운터를 함께 출력**하고,
0 이 아니면 눈에 띄게 표시할 것을 권한다.

---

## 10. 항목 7 — 성능

| 항목 | 평가 |
|---|---|
| `_texture_mean` / `_texture_sat` PIL 로드 | **문제 없음.** 역할 수만큼(≈28회) 호출되고 캐시된다. `thumbnail((64,64))` 는 JPEG draft 축소를 쓰므로 파일당 수 ms |
| `_look_spec` | 캐시 없음 — 재질 1개당 최대 16규칙 × 평균 8키워드 부분문자열 검사. 씬당 재질 수십 개라 무시 가능 |
| **`_ground_skin` 조립** | 슬래브 1장당 정점 27,556 · 쿼드 27,225. 순수 파이썬 이중 루프만 ≈19 ms(측정), `Gf.Vec3f` 생성 포함하면 수 배. 삼각형 +55 k/장 (**m9**) |
| MDL `patch_mix` 조기 탈출 | 의도한 이득 실재 (§5.3의 레이어 B 단서 부기) |
| PT 가속 경로 | `NEGOBS_PT_FAST` 게이트, 씬 `set_render_mode` **뒤에** 덮어쓰는 순서도 정확 |

---

## 11. 확신 없는 것 (`[추정]`)

1. `use_blend=false` 일 때 레이어 B 가 DCE 되는지 — MDL 컴파일 모드 의존. GPU 확인 필요.
2. `patch_mix<=0` 분기가 컴파일 타임에 접히는지 vs 런타임 분기인지 (성능 결론은 불변).
3. 스킨 페이스 와인딩(−Z)이 현 RTX 설정에서 실제로 컬링되는지.
4. M4(3옥타브 앨리어싱)가 "정점 변위가 최대 시각 기여"(E9)의 실제 정체인지.
5. C4 의 영향 씬 목록 중 scene02·08·09·17 은 이름·구조상 z<0 가 명백하나 좌표 미확인.
   sceneD3(−1.05 m)·sceneD2 는 코드로 확인됨.
6. M5 의 "scene07 채도 개선의 실제 원인이 `desat_bright_a` 다"는 인과 분리 미실시.
7. `sceneN3` 포디엄과 `SillBand` 0.15 m 돌출의 간섭 여부.
8. Pillow 가 Isaac 파이썬 환경에 실제로 설치돼 있는지(있다고 가정하고 위 수치를 냈다).

---

## 12. 조치 우선순위 제안

1. **C3 즉시** — 게이트되지 않은 기하 변경. 이걸 두면 이후 모든 A/B 가 무의미.
2. **C1 · C4** — 게이트 3차 수치를 오염시킨다. 고친 뒤 **게이트를 다시 돌려야 한다.**
3. **C2** — 렌더 전에 반드시. 이미 아스팔트 텍스처가 디스크에 있다.
4. M1 · M3 · M6 · M7 — 다음 라운드 전.
5. M5 는 수치가 아니라 **보고서의 인과 귀속**을 정정해야 하는 건이다.
