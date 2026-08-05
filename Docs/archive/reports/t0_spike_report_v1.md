# T0 검증 스파이크 — 실측 보고 v1

- 일자 **2026-07-29** · 런타임 **Isaac Sim 4.5.0 / Kit 106.5** · GPU **RTX 4090 24 GB** · 호스트 RAM 31.9 GB
- 지시 근거: `Docs/surveys/realism_gap_2026-07-28/ZZ_synthesis.md` §6 T0 · §10,
  `D_isaacsim_untapped_capabilities.md`, `H_rtx_capability_verification.md`
- 증거 이미지·로그·JSON: `look_check/_t0_spike/` (미추적) · 실행 하네스 사본: `look_check/_t0_spike/_harness/`
- 원칙 준수: git 추적 파일 **무수정**. 스파이크 씬은 미추적 사본
  `scenes/batch1/_t0_c2_mdl.py` 로 만들어 쓰고 **종료 시 삭제**했다. 커밋하지 않았다.

## 0. 한 장 요약

| # | 스파이크 | 결론 1줄 | 성패 |
|---|---|---|---|
| T0-3 | `NegObsGround.mdl` 정량 | **단독 바인딩은 지표를 전혀 못 움직인다** (flat% 20.391 → 20.391, slope −1.683 → −1.689). 게이트 대역 미달 | 실행 성공 / **효과 없음** |
| T0-1 | `round_edges_radius` | **RT·PT 양쪽에서 작동**. 밴드폭이 `px ≈ 24·(r/d)·57.3` 을 실측 재현 | **통과** |
| T0-2 | `catmullClark` + crease | 기본 `refinementLevel=0` 에서는 **세분 없음**(셰이딩만 바뀜). 1 이상에서 진짜 세분 + crease 존중 | **통과(단 채택 부적합)** |
| T0-4 | 나무 USD 잎 알파 | 저장소 전체에 `opacityThreshold` **0건이지만 필요 없다** — 잎이 알파컷아웃이 아니라 **실제 3D 지오메트리** | **문제 없음(확인만)** |
| T0-5 | 렌더 처리량 | RT 90→32 = 1.10→0.57 s/컷(회귀 0). PT 가속 = 13.5→0.95 s/컷 **14.2배**(회귀 0) | **통과** |
| T0-6 | 동시 렌더 | **N=2 가 상한**(+7.0%). N=3 은 **호스트 RAM OOM 으로 1개 사망**. VRAM 은 병목이 아니었다 | **통과(권고 N=2)** |
| SP-1 | 자동노출 | `/rtx/post/histogram/enabled = **False**` — **AE 는 꺼져 있다**. 기존 밝기 A/B 판정 전부 유효 | **통과** |

**감독에게 가장 중요한 두 줄**
1. ZZ §8 이 "해법은 이미 저장소 안(NegObsGround.mdl)에 있다"고 한 전제는 **본편 씬에서 성립하지 않는다.**
   sceneC2 에서 MDL 은 재질 22개 중 4개에만 걸리고, 로봇 시점(h0.3)을 채우는 낙엽·잔디는 클래스 표가
   `veg → OmniPBR` 로 보내 **MDL 이 닿지 않는다.**
2. `look_check/sceneC2/leaf3d` 를 "기준선"으로 쓰면 안 된다 — **이미 `NEGOBS_LOOK_V1=1` 로 렌더된 결과**다
   (§1.4 픽셀 대조). 진짜 무처리 기준선은 이번에 새로 뽑은 `look_check/_t0_spike/c2_A_base/` 다.

---

## 1. T0-3 — `NegObsGround.mdl` 효과 정량 (최우선)

### 1.1 실험 설계

`sceneC2_leaf_stairs.py` 를 미추적 사본으로 복제하고, **지면 계열 텍스처 재질만** MDL 로 바꾸는
`make_pbr` 래퍼를 주입했다. MDL 자체 효과만 남기려고 **베벨 0 · 웨더링 제거 · 채도계수 1.0 ·
bump 는 씬 원값 유지**로 고정했다(그 셋은 각각 T0-1·별도 항목·별도 항목 소관).

| 조건 | 내용 | 출력 |
|---|---|---|
| **A** | 사본 무개입 = 현행 프로덕션 | `look_check/_t0_spike/c2_A_base/` |
| **B** | 지면 계열만 `NegObsGround.mdl` (격리) | `look_check/_t0_spike/c2_B_mdl/` |
| **C** | `NEGOBS_LOOK_V1=1` 전량(참고 상한) | `look_check/_t0_spike/c2_C_lookv1/` |

각 조건 15컷(그리드 9 + 미장센 4 + 나무 근접 2), RT(warmup 90) + PT(legacy spp1/totalSpp512).

### 1.2 [실측] 지표 — PT · h0.3 3컷 (지시서가 지정한 비교)

| 조건 | slope | grad_k | **flat%** | flat_sky | flat_gnd | sat_mu | ori_axis |
|---|---|---|---|---|---|---|---|
| A 원본 | −1.683 | 9.76 | **20.391** | 60.78 | 0.196 | 0.378 | 0.264 |
| **B MDL 단독** | −1.689 | 11.35 | **20.391** | 60.78 | 0.197 | 0.375 | 0.269 |
| C LOOK_V1 전량 | −1.881 | 7.98 | 2.227 | 5.05 | 0.817 | 0.367 | 0.245 |
| (참고) 기준선 leaf3d | −1.892 | 8.12 | 2.467 | 5.70 | 0.849 | 0.367 | 0.244 |

**목표 대역 flat% < 8 · slope −2.0 ~ −2.2 대비**
- B(MDL 단독): flat% **Δ = 0.000 pp**, slope **Δ = −0.006**. 두 목표 **전부 미달**, 개선폭 사실상 0.
- 13컷 전체로 넓혀도 같다: flat% 20.288 → 20.284, slope −1.994 → −2.008.
- C(전량): flat% 2.227 로 목표 통과. **그러나 이것은 지면 개선이 아니다** — §1.3.

### 1.3 flat% 가 떨어진 진짜 원인은 지면이 아니라 **하늘 가림**이다

C 에서 flat% 가 20.4 → 2.2 로 떨어질 때 **flat_sky 가 60.78 → 5.05** 로 같이 무너지고,
**flat_gnd 는 오히려 0.196 → 0.817 로 올라간다.** 실측 원인은 `LOOK_V1` 이 켜면서 들어온
**실물 USD 수목(6주) + 3D 산포물(845개)** 이 상단 프레임의 무운 하늘(`qwantani_noon_puresky`)을
가린 것이다. 즉 헤드라인 지표는 **하늘을 가려서** 통과했다. Phase1 §4.1 이 경고한 실패 모드가
실제로 발생하고 있다 — **게이트는 flat_gnd(하단 2/3)로 걸어야 한다.**

### 1.4 [실측] 왜 MDL 이 안 먹는가 — 커버리지가 4/22 다

사본이 찍은 재질 통계(`c2_B_mdl/t0_timing.json` → `stat`):

```
ground=4  keep=18   roles = {veg:14, curb:2, soil:2, metal:2, stone:1, wood:1}
```

- `make_pbr` 호출 22개 중 **MDL 이 걸린 것은 4개**(석재 1 · 경계석 2 · 흙 1).
- **`veg` 가 14개로 최다**인데 `LOOK_CLASS["veg"]["mdl"] == "omni"` 라 MDL 대상이 아니다.
  sceneC2 의 h0.3 화면을 채우는 것은 **낙엽 마운드·낙엽 산포·잔디**이고, 전부 여기 속한다.
- 그래서 최근접 컷(h0.3 d2)은 A/B 가 **PSNR 60.03 dB · >1 LSB 픽셀 0.01 %** = 사실상 동일하다.

한편 원경 컷은 픽셀이 크게 바뀐다(아래) — **육안 변화는 있는데 지표가 안 움직인다**는
Phase1 E9 의 경고가 프로덕션 씬에서 재현됐다.

| 뷰 | A vs B meanΔ | PSNR | >8 LSB 픽셀 |
|---|---|---|---|
| h0.3 d2 | 0.065 | 60.03 dB | 0.00 % |
| h0.3 d5 | 10.135 | 22.58 dB | 42.39 % |
| h0.3 d10 | 13.202 | 21.33 dB | 56.19 % |

`regression_check` 판정(A→B, PT 15컷): **FAIL 0 · WARN 4(전부 UNCHANGED) · INFO 2 · PASS 9**
→ 회귀는 없고, "바뀌지 않았다"는 경고가 4컷에서 뜬다.

### 1.5 [실측] 기준선 `leaf3d` 의 정체

| 기준선 대비 | h0.3 d2 | h0.3 d5 | h0.3 d10 | approach_walk |
|---|---|---|---|---|
| vs A(무처리) | 27.99 | 34.95 | 19.14 | 21.63 |
| vs B(MDL 단독) | 27.99 | 30.22 | 10.17 | 21.36 |
| **vs C(LOOK_V1)** | **4.14** | **3.94** | **1.88** | **4.19** |

(단위: meanΔ LSB) → `leaf3d` 는 **C 와 같은 계열**이다. 잔차 1.9~4.2 LSB 는 그 뒤에 들어온
커밋(`5191e3c`·`0addc56`·`c0cef87`)과 산포 시드 차이로 설명된다.

### 1.6 재현 명령

```bash
unset PYTHONPATH VIRTUAL_ENV; export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1
conda activate env_isaaclab
cd /home/vislab/Desktop/work_sy/Practice_NegObs/scenes/batch1
# 사본 준비: cp sceneC2_leaf_stairs.py _t0_c2_mdl.py 후
#   look_check/_t0_spike/_harness/_t0_c2_mdl.patch.py 블록을 import 직후에 삽입
NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=both NEGOBS_T0_TIMING=1 NEGOBS_T0_TREEVIEW=1 \
NEGOBS_T0_MDL=0 NEGOBS_CAPTURE_DIR=../../look_check/_t0_spike/c2_A_base python _t0_c2_mdl.py
NEGOBS_T0_MDL=1 ... NEGOBS_CAPTURE_DIR=../../look_check/_t0_spike/c2_B_mdl  python _t0_c2_mdl.py
NEGOBS_LOOK_V1=1 ... NEGOBS_CAPTURE_DIR=../../look_check/_t0_spike/c2_C_lookv1 python _t0_c2_mdl.py

cd /home/vislab/Desktop/work_sy/Practice_NegObs
python scripts/imgstats.py --json look_check/_t0_spike/stats_pt_h03.json \
  @A_base   'look_check/_t0_spike/c2_A_base/pt_noon_preset_h0.3_d*.png' \
  @B_mdl    'look_check/_t0_spike/c2_B_mdl/pt_noon_preset_h0.3_d*.png' \
  @C_lookv1 'look_check/_t0_spike/c2_C_lookv1/pt_noon_preset_h0.3_d*.png' \
  @base_leaf3d 'look_check/sceneC2/leaf3d/pt_noon_preset_h0.3_d*.png'
```

### 1.7 W2 함의

1. **"MDL 이식 = T1 최우선" 순위를 내려야 한다.** 단독 효과가 실측 0 이다.
   대신 MDL 이 **실제로 닿는 면적을 먼저 늘리는 것**(veg/낙엽·잔디의 라우팅 재검토, 또는
   `LOOK_CLASS` 의 `mdl` 배정 재설계)이 선행 조건이다.
2. **게이트 지표를 flat_gnd(하단 2/3)로 바꿔야 한다.** 현행 flat% 는 하늘이 61 %를 지배해서
   "나무를 심으면 통과"가 된다. 사실성 개선과 무관한 통과 경로다.
3. **비용은 실재한다** — MDL 바인딩만으로 PT 컷당 13.5 → 15.3~21.0 s (+16~55 %). 효과 0 인
   현 상태에서 전 33씬 이식은 순손실이다.
4. 기준선 재정의 필요: 앞으로 A/B 는 `c2_A_base`(무처리) 대비로 잡을 것.

---

## 2. T0-1 — `round_edges_radius` (가짜 베벨)

### 2.1 결론

**작동한다. RT·PT 양쪽에서, 그리고 밴드폭이 Phase1 근사식 `px ≈ 24·(r/d)·57.3` 을 실측 재현한다.**

### 2.2 [실측] 방법론 경고 — A/B 는 반드시 "같은 박스·같은 카메라"여야 한다

먼저 기존 랩(`scripts/spike_realism.py` E1)과 자체 5박스 배열로 재봤더니 0 mm vs 20 mm 에서
**전면 전체가 +44 LSB** 밝아지는 거대한 차이가 나왔다. 이는 베벨 효과가 아니라 **경사 태양 아래
좌우 끝 박스의 조도차**였다. 반경별로 다른 박스를 다른 위치에 놓는 설계는 이 오염을 못 막는다.
→ 최종 랩(`_harness/t0_edge_lab2.py`)은 **박스 1개를 고정**하고 셰이더 입력만 런타임에 바꿔 찍는다.

### 2.3 [실측] 모서리 롤오프 밴드 (화강암, roughness 0.25)

밴드폭 = 상단 앞모서리 아래로 `|Δ| > 2 LSB` 가 유지되는 행 수. `edge_y` 는 실측 모서리 행.

| 거리 | 프로파일 | r=2 mm | r=5 mm | r=10 mm | r=20 mm | (예측 px) |
|---|---|---|---|---|---|---|
| d≈1.4 m | RT | 2 px | 2 px | 5 px | **16 px** | 2.0 / 4.9 / 9.8 / 19.6 |
| d≈1.4 m | **PT** | 3 px | 6 px | 11 px | **23 px** | 〃 |
| d≈2.6 m | PT | 1 px | 3 px | 5 px | 9 px | 1.1 / 2.6 / 5.3 / 10.6 |
| d≈5.6 m | PT | 0 px | 2 px | 2 px | 4 px | 0.5 / 1.2 / 2.5 / 4.9 |

모서리 최대 휘도차: d1.4 에서 **−33.0 LSB(RT) / −35.4 LSB(PT)** @20 mm, d5.6 에서 −10.9 LSB(PT).
콘크리트(거친 재질)도 같은 경향(d1.4 RT 밴드 0/3/6/**25** px).
증거: `look_check/_t0_spike/t01_edge_lab2/CROP_{rt,pt}_gran_d08_0_5_20mm.png`(0/5/20 mm 3연),
raw 는 같은 폴더 `{rt,pt}_{gran,conc}_d{08,20,50}_r{00,02,05,10,20}mm.png` 50장.

### 2.4 재현 명령

```bash
# (환경 프리앰블 동일)
cd /home/vislab/Desktop/work_sy/Practice_NegObs
python look_check/_t0_spike/_harness/t0_edge_lab2.py     # 50컷, 약 25 s
python look_check/_t0_spike/_harness/bevel_profile4.py    # 밴드폭 표
# 저장소 정식 랩(참고): python scripts/spike_realism.py --mode both --only e1,e4
```

### 2.5 W2 함의

- `make_pbr` 인자 1개로 33씬 전 모서리에 거는 계획은 **기술적으로 유효**하다.
- 다만 로봇 상시 거리 d=2~10 m 에서 20 mm 는 2~10 px, 10 mm 는 1~5 px 다. **비용 0 이므로 걸되,
  이것으로 지표가 움직일 것을 기대하면 안 된다.** 효과는 근접 컷에서만 회수된다.
- 현행 `LOOK_CLASS` 값(콘크리트 20 mm / 노징 12 mm / 연석 10 mm)은 이 실측과 정합한다.

---

## 3. T0-2 — `subdivisionScheme=catmullClark` + crease

### 3.1 [실측] 런타임 기본값

`scripts/rtx_probe.py` 덤프(`look_check/_t0_spike/rtx_settings.json`):

```
/rtx/hydra/subdivision/refinementLevel   = 0
/rtx/hydra/subdivision/adaptiveRefinement = False
/rtx/pathtracing/spp = 64   /rtx/pathtracing/totalSpp = 64   /rtx/pathtracing/maxBounces = 4
/rtx/post/tonemap/op = 6  filmIso = 100.0  cameraShutter = 50.0  fNumber = 5.0
```

### 3.2 [실측] refinementLevel 스윕 (같은 메시, 같은 카메라)

| refinementLevel | refine0 대비 >8 LSB 픽셀 | 관측 |
|---|---|---|
| 0 (기본) | — | **세분 없음.** 큐브 실루엣 유지. 단 `catmullClark` 메시는 **저작 노멀이 무시되고 스무스 셰이딩**이 걸린다 |
| 1 | **22.31 %** | 진짜 Catmull-Clark — 큐브가 둥근 다면체가 된다 |
| 2 | 23.64 % | 1과 실질 동일(`adaptiveRefinement=False`) |
| 4 | 26.79 % | 〃 |

**crease 는 존중된다**: 12모서리 전부에 `crease 10.0` 을 준 박스는 refinementLevel=1 에서도
**박스 실루엣을 유지**한다. 증거 1장에 3조건이 동시에 들어 있다 —
`look_check/_t0_spike/t01_edge_lab/rt_subdiv_row_refine1.png`
(좌 `none` = 각진 박스 / 중앙 `catmullClark` = 둥근 다면체 / 우 `cc+crease` = 박스 유지).
기본값 대조군은 같은 폴더 `rt_subdiv_row.png`.

### 3.3 W2 함의

- **실제 지오메트리 베벨 경로는 검증됐다**(crease + subdiv). 필요하면 쓸 수 있다.
- 그러나 채택은 권하지 않는다: `refinementLevel` 은 **전역 설정**이라 켜는 순간
  `subdivisionScheme` 을 저작하지 않은 모든 메시가 함께 둥글어진다.
- **규약 유지 필수**: 새 메시는 반드시 `CreateSubdivisionSchemeAttr("none")` 을 저작할 것.
  미저작 = USD 기본값 `catmullClark` = level 0 에서도 **조용한 스무스 노멀**이 걸린다(§3.2 1행).

---

## 4. T0-4 — 나무 USD 잎 알파

### 4.1 [실측] 코드 전수 확인

```
grep -rn "opacityThreshold|opacity_threshold" --include=*.py --include=*.mdl .   → 0 건
grep -rn "enable_opacity" --include=*.py .  → 1 건 (scene_common.py:1689 주석뿐)
```

`scene_common.add_vegetation()`(1709~1747)은 USD 를 reference 로 붙이고 단위·스케일·회전만
처리한다. 재질은 **에셋 자신의 MDL 을 그대로 쓴다.**

### 4.2 [실측] 에셋이 애초에 알파컷아웃이 아니다

| 텍스처 | 모드 | 알파 |
|---|---|---|
| `Trees/materials/textures/cherryblossom.png` | **RGB** 256² | **없음** |
| `Trees/materials/textures/pine_needles.png` | **RGB** 256² | **없음** |
| `Trees/materials/textures/alter49_tree1_basecolor.png` | **RGB** 2048² | **없음** |
| `Trees/materials/textures/alter49_tree10_basecolor.png` | **RGB** 2048² | **없음** |
| `Trees/materials/textures/bark3_basecolor.png` | RGBA 1024×2048 | α 229~255(불투명, 수피) |

잎 재질 MDL(`JapaneseCherry_blossom_Mat.mdl`, `Pine_needles.mdl`)은 **OmniPBR 인스턴스이며
opacity 계열 입력을 하나도 설정하지 않는다**(전체 41줄, 전수 확인).
→ **알파 컷아웃 경로 자체가 없으므로 `opacityThreshold` 기본 0.0 함정(ZZ §10.2)은 적용 대상이 아니다.**

### 4.3 [실측] 실렌더 판정

`look_check/_t0_spike/c2_C_lookv1/pt_noon_t0_tree_near.png` (d≈3.6 m) ·
`..._t0_tree_mid.png` (d≈7.2 m):
꽃잎 하나하나가 **곡면 3D 지오메트리**로 서 있고, 판때기 실루엣·알파 프린지·검은 테두리가 **없다**.
→ **판정: 잎 판때기 아님. 조치 불요.**

### 4.4 그러나 발견된 별건 2가지 (W2 입력)

1. **실물 나무는 `NEGOBS_LOOK_V1=1` 일 때만 로드된다.** 플래그가 꺼진 기본 경로에서는
   `build_tree` 가 여전히 실린더+구 블롭을 만든다(호출 씬 25개).
   `look_check/_t0_spike/c2_A_base/pt_noon_t0_tree_near.png` 가 그 상태다.
2. **계절 불일치.** sceneC2 는 낙엽 매몰(가을) 씬인데 좌표 해시가 뽑은 수종이
   **만개한 벚나무(봄)** 다. `VEG_TREES` 가중치가 벚나무 5/8 이라 가을·겨울 씬에서 반복될 구조다.

---

## 5. T0-5 — 렌더 처리량

측정 대상: sceneC2 사본, 1920×1080, 15컷(그리드 9 + 미장센 4 + 나무 2).
컷당 시간은 사본에 주입한 계측기가 캡처 호출 간격을 직접 잰 값이다(`t0_timing.json`).
부팅+조립 = **9 s**(프림 1340개).

### 5.1 [실측] 컷당 시간

| 프로파일 | 설정 | s/컷 (실측 범위) | 15컷 소요 |
|---|---|---|---|
| RT warmup **90** (현행) | — | **1.03 ~ 1.17** | 16.4 s |
| RT warmup **32** | `NEGOBS_WARMUP=32` | **0.55 ~ 0.61** | 8.5 s |
| PT **legacy**(현행) | spp 1 / totalSpp 512 / warm 572 | **13.18 ~ 13.71** | 200 s |
| **PT 가속** | spp 16 / totalSpp 64 / rtSubframes 8 / warm 8 | **0.90 ~ 0.99** | 13.9 s |
| PT legacy + MDL 바인딩(B) | 〃 | 15.33 ~ 20.97 | — |
| PT legacy + LOOK_V1 전량(C) | 〃 | 21.58 ~ 31.33 | — |

→ **PT 가속 = 14.2 배**(13.5 → 0.95 평균). 그리고 **PT 가속(0.90~0.99)이 RT warmup 90(1.03~1.17)보다
빠르다** — Phase1 이 문서로 남긴 주장(PT-fast 0.7 s vs RT 1.12 s)이 프로덕션 씬에서 **재현됐다.**
`NEGOBS_PT_FAST=1` 경로는 실재하며 정상 동작한다(로그 `[렌더] PT 가속 적용 (totalSpp 64, warmup 8)`).

### 5.2 [실측] 화질 동등성

| 비교 | imgstats(15컷 평균) | 픽셀 | `regression_check` 판정 |
|---|---|---|---|
| **RT90 → RT32** | flat% 28.193→28.152 · slope −2.140→−2.152 · sat 0.407→0.407 | PSNR 34.1~36.6 dB · meanΔ 2.6~3.4 · >8 LSB 8.2~14.7 % | **FAIL 0 · PASS 12 · INFO 3**(GRAZE) |
| **PT512 → PT가속** | flat% 28.292→28.303 · slope −2.126→−2.128 · sat 0.413→0.413 | PSNR 41.2~43.9 dB · meanΔ 1.0~1.6 · >8 LSB 0.22~0.66 % | **FAIL 0 · PASS 12 · INFO 3**(GRAZE) |

두 단축 모두 **게이트 지표 편차 ≤ 0.06 pp** 로, 개선 목표폭(flat% 20 → 8)의 1 % 미만이다.
다만 **잔차는 RT32 쪽이 3배 크다**(meanΔ 3.0 vs 1.3). 판정용으로는 PT 가속이 더 안전하다.

### 5.3 [실측] 부수 발견 2건

1. **"spp 기본 1" 은 런타임 기본값이 아니다.** 부팅 시 실측 `/rtx/pathtracing/spp = 64` 인데,
   **씬 파일의 `set_render_mode()` 가 매번 `spp=1, totalSpp=512` 로 되돌린다.** 즉 512프레임 누적
   낭비는 런타임 결함이 아니라 **우리 코드가 만든 것**이고, `capture_pipeline` 의 PT_FAST 분기가
   "씬 콜백 뒤에 덮어써야 한다"고 주석에 적어 둔 이유가 이것이다.
2. **`capture_pipeline` 의 성공 플래그가 오탐한다.** 40회 update 안에 PNG(5~6 MB) 크기가 안정되지
   않으면 `ok=False` 로 기록하는데, 이번 실행에서 6컷이 FAIL 로 찍혔고 **6컷 전부 정상 디코딩**됐다
   (`_harness/verify_pngs.sh`). `manifest.json` 의 `ok` 를 신뢰해 재렌더하면 순수 낭비다.

### 5.4 W2 함의 — 대량 렌더 권장 프로파일

- **단일 프로파일 = PT 가속(`NEGOBS_PT_FAST=1`)** 을 권고한다. RT 보다 빠르고, 잔차가 작고,
  RT↔PT 룩 불일치 문제가 사라진다(Phase1 §3.4 의 "원칙 4 폐기" 제안을 실측으로 재확인).
- RT 를 쓴다면 warmup 32 로 내려도 무방하다(반복 확인용). 판정에는 PT 가속.
- 2만 장 환산(sceneC2 급): PT 가속 0.95 s/컷 → **약 5.3 시간**(부팅 제외). PT legacy 는 75 시간.
- **재질 비용을 예산에 넣을 것**: LOOK_V1 전량은 컷당 시간을 1.6~2.3배로 올린다.

---

## 6. T0-6 — 동시 렌더 처리량 (감독 추가 지시)

### 6.1 설계

같은 사본 씬·같은 6뷰(`preset_h0.3_d{2,5,10}`, `approach_walk`, `buried_edge`, `beauty_side`)를
RT(warm90) + PT(legacy) = 인스턴스당 12컷. 인스턴스별 `NEGOBS_CAPTURE_DIR=look_check/_t0_spike/conc{N}/i{n}`.
GPU 는 1초 간격 `nvidia-smi` 폴링(`conc{N}/gpu_poll.csv`).

### 6.2 [실측] 결과

| N | wall | 완료 컷 | **처리량(컷/분)** | 피크 VRAM | GPU util 평균 | PT s/컷 | 사고 |
|---|---|---|---|---|---|---|---|
| 1 | 100.4 s | 12 | **7.17** | 6 775 MB | 87 % | 13.3~14.2 | — |
| **2** | 187.8 s | 24 | **7.67 (+7.0 %)** | 11 940 MB | 94 % | 26.4~29.1 | — |
| 3 | 216.0 s | 24 / 36 | **6.67 (−7.0 %)** | 12 853 MB | 86 % | 27.5~55.7 | **1개 사망** |

- **N=3 사망 원인은 GPU 가 아니라 호스트 RAM OOM 이다.** 커널 로그 원문:
  `Out of memory: Killed process 1341197 (python) total-vm:138915260kB, anon-rss:13700276kB`
  → 인스턴스 1개가 **anon-RSS 13.7 GB**. 호스트 31.9 GB 중 데스크톱 등이 7.6 GB 를 이미 쓰고 있어
  3개가 못 들어간다. **VRAM 은 최대 12.9 GB 로 24 GB 카드의 절반도 안 썼다.**
- **PT 컷당 시간이 N=2 에서 정확히 2배**가 된다 = GPU 가 이미 포화라 동시 실행은 시분할일 뿐이다.
  이득은 **부팅(9~13 s)이 다른 인스턴스의 렌더와 겹치는 것뿐**이고, 그게 +7 % 의 정체다.
- **부팅/렌더 중첩은 실제로 일어난다**: 부팅→첫 컷 = 2.23 s(N=1) → 2.74~3.18 s(N=2) → 2.91~2.98 s(N=3).

### 6.3 [실측] 품질·결정성

동시 렌더가 이미지를 바꾸지 않는다:

| 비교 | meanΔ | 4 LSB 초과 픽셀 | `regression_check` |
|---|---|---|---|
| 단독(conc1/i1) → 동시2(conc2/i1) | 0.06~0.09 LSB | **0.000 %** | 6컷 전부 `UNCHANGED` |
| 단독(conc1/i1) → 동시3(conc3/i1) | 0.06~0.09 LSB | **0.000 %** | 6컷 전부 `UNCHANGED` |

OOM 로 죽은 인스턴스 외에 **크래시·품질 이상 0건**.

### 6.4 권고 — **N = 2**

- 근거: (a) 처리량 이득 +7.0 % 뿐 (b) N=3 은 이 머신(32 GB)에서 **결정론적으로 OOM**
  (c) 품질은 N=2 에서 픽셀 동일 (d) VRAM 여유는 충분하나 **호스트 RAM 이 진짜 상한** —
  인스턴스당 약 13.7 GB, 즉 `floor((RAM_total − 8 GB) / 14 GB)`.
- **W2 렌더 큐 설계 결론**: 동시 실행은 처리량 레버가 **아니다**. 큐는 단일 인스턴스 + PT 가속으로
  짜고, 동시 2 는 "부팅이 잦은 짧은 잡(씬 수가 많고 컷 수가 적은 라운드)"에서만 켠다.
  N≥3 은 RAM 48 GB 이상에서만 재검토할 것(그래도 GPU 포화라 이득은 미미할 전망).

### 6.5 재현 명령

```bash
bash look_check/_t0_spike/_harness/run_conc.sh 1   # 이어서 2, 3
python scripts/regression_check.py --before look_check/_t0_spike/conc1/i1 \
                                   --after  look_check/_t0_spike/conc2/i1
```

---

## 7. SP-1 — 자동노출(AE) 실태 (감독 추가 지시)

### 7.1 [실측] 설정값

```
/rtx/post/histogram/enabled              = False      ← AE OFF
/rtx/post/histogram/useExposureClamping  = True
/rtx/post/tonemap/op = 6   filmIso = 100.0   cameraShutter = 50.0   fNumber = 5.0
/rtx/post/colorcorr/enabled = False   /rtx/post/colorgrad/enabled = False
```

### 7.2 [실측] filmIso 스윕 (같은 씬·같은 뷰·RT)

| filmIso | 기본(AE OFF) 평균 | histogram 강제 ON 평균 |
|---|---|---|
| 100 | **127.338** | 86.260 |
| 200 | **164.340** | 86.227 |
| 400 | **192.703** | 86.220 |
| 800 | **213.877** | 86.277 |

- AE OFF: ISO 8배에 평균 휘도 127 → 214 로 **뚜렷이 변한다** → 노출은 설정대로 고정.
- AE 강제 ON: ISO 8배에도 평균이 86.22~86.28 로 **Δ 0.06 LSB** → 완전히 상쇄된다(대조군 성립).

### 7.3 판정

**우리 파이프라인에서 자동노출은 꺼져 있다.** 지금까지의 모든 밝기 A/B 판정(룩 라운드,
`regression_check` 의 DARK/BLOWN, imgstats 채도·flat%)은 **AE 오염 없이 유효**하다.
부수 정보: AE 를 켜면 같은 씬이 평균 127 → 86 으로 어두워진다. 즉 AE 는 "정규화"가 아니라
**다른 룩**이므로, 도입한다면 기준선을 새로 잡아야 한다.

재현: `python look_check/_t0_spike/_harness/sp1_autoexposure.py` (약 27 s)

---

## 8. 산출물 색인 (`look_check/_t0_spike/`, 미추적)

| 경로 | 내용 |
|---|---|
| `c2_A_base/` `c2_B_mdl/` `c2_C_lookv1/` | T0-3 A/B/C 각 30장(RT15+PT15) + `t0_timing.json` |
| `c2_A_rt32/` `c2_A_ptfast/` | T0-5 단축 프로파일 각 15장 |
| `t01_edge_lab2/` | T0-1 확정 랩 50장 + `CROP_{rt,pt}_gran_d08_0_5_20mm.png` |
| `t01_edge_lab/` | T0-1/T0-2 보조 랩 13장(`rt_subdiv_row{,_refine1}.png` 포함) |
| `t01_bevel/` `t02_subdiv/` | `scripts/spike_realism.py`(e1,e4) · `scripts/rtx_probe.py` 산출 사본 |
| `conc1/ conc2/ conc3/` | T0-6 인스턴스별 산출 + `gpu_poll.csv` + `result.json` |
| `sp1_ae/` | SP-1 12장 + `sp1_ae.json` |
| `stats_*.json` `regr_*.json` `rtx_settings.json` | 지표·회귀·설정 실측 원자료 |
| `_harness/` | 이번 스파이크 실행 스크립트 전체 사본(사본 씬 패치 블록 `_t0_c2_mdl.patch.py` 포함) |
| `prev0728_spike_{e1,e4,probe}/` | 07-28 산출물 백업(재실행으로 덮이기 전) |

---

## 9. 실행 위생 — 동시 작업 중 발생한 추적 파일 변경 (측정 영향 검토)

이번 웨이브에서 **다른 에이전트가 같은 저장소의 추적 파일을 병행 수정**했다. 본 스파이크는
추적 파일을 한 줄도 고치지 않았으나, 렌더 구간(14:49~15:33)과 겹친 변경이 있어 오염 여부를 확인했다.

| 파일 | mtime | 내 실행과의 관계 | 측정 영향 |
|---|---|---|---|
| `scene_common.py` | 14:52:47 | **A 실행 중**(A 는 14:51 에 import 완료 → 구코드) / B·C 는 신코드 | **없음** — 근거 아래 |
| `building_kit.py` | 15:02:10 | C 종료 후 | 없음(sceneC2 미사용) |
| `scripts/regression_check.py` | 15:23:51 | 회귀 검사(15:31~) **전** | 없음 — 본 보고의 모든 회귀 판정은 **같은 버전**으로 돌렸다 |
| `Docs/reports/asset_audit_v1.md` | 14:56:58 | 문서 | 없음 |

`scene_common.py` 변경 2건의 영향 범위를 코드로 확인했다:
- `VEG_DEBRIS` 의 `oakfall2` 수치 정정 → sceneC2 는 `pool=[p for p in sc.VEG_DEBRIS if "fallcluster" in p[0]]`
  로 **fallcluster 만 넘긴다**(`sceneC2_leaf_stairs.py:563`) → 산포 결과 불변.
- 창 리세스(T1-10) → `ins = float(wd.get("inset", 0.0)) if LOOK_V1 else 0.0` (`scene_common.py:2097`)
  → **LOOK_V1=0 인 A·B 에는 코드 경로 자체가 없다.**

**따라서 T0-3 의 핵심 비교(A vs B)는 오염되지 않았다.** C(LOOK_V1) 만 신코드로 돌았으며,
§1.5 의 `leaf3d ↔ C` 잔차 1.9~4.2 LSB 중 일부가 여기서 온다.

> 권고: 다음 웨이브부터 **렌더 측정 에이전트가 도는 동안 공유 모듈(`scene_common.py`) 수정을
> 금지**하거나, 측정 에이전트가 워크트리 격리로 돌 것. 이번엔 우연히 무해했다.
