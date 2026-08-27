# PANELS — 논문 초안용 정성 패널 큐레이션 (v2 스코프)

- **작성**: Claude Code · 2026-08-23 · **처분 대상**: `submission_0830/INDEX.md` §4 **누락위험 1** = §6-C6
- **무엇을 고쳤나**: `INDEX.md` §4가 「본 표(v2) 런 정성 패널 119장이 `.gitignore:17 **/runs/**/*.png` 로
  전량 비공개 → **논문 헤드라인(v2)의 정성 예시를 공개 리포에서 뽑을 방법이 없다**」고 적은 그 구멍입니다.
  이 디렉터리는 **추적 가능한 경로**(`git check-ignore` 반환 1 = 미차단)에 놓인 **선별 24장**입니다.
- **성격**: **복사·축소 전용.** 새 합성 패널을 만들지 않았고, 새 렌더·추론·GPU 사용이 없습니다.
  원본 픽셀은 그대로이며, 1600 px 초과분만 LANCZOS 축소했습니다(해당 2장, 표에 표기).
- **총량**: 24장 · **6.29 MB** (장당 최대 378 KB). 한도 24장 / 15 MB 이내.

> **인용 규약 (필독)**
> - 이 24장은 전부 **v2 코퍼스**입니다. `s20260819` 는 mainrun 짝, `::boost_h|e|e2` 는 08-20 boost 라운드로
>   **둘 다 v2 코퍼스 구성원**입니다. (`INDEX.md` §4가 경고한 "v1 스코프" 문제는 `mainrun_0819/viz/` 12장의 얘기이고,
>   **여기 24장은 그 문제가 없습니다.**)
> - GT 격자는 `PROVISIONAL-GRID-V1` (4밴드 × 5섹터 = 20칸, `experiments/mainrun_0819/code/labeling/gridspec_v1.json`).
> - 패널 안의 수치는 **구 GT 시점에 그려진 것**입니다. 단 `V2_RESCORE.md` §2 / `EVL12_CELL_AXIS.md` §5 의
>   실측대로 **H 행·off팔은 교정 GT에서 바이트 동일**하므로, **H 컷과 fa_off 컷은 교정 GT 기준으로도 그대로 유효**합니다.
>   본 표의 `max p` · `GT 양성칸` · `발화칸` 열은 **교정 GT 원장**(`experiments/v3_0823/eval_v2corr/<run>/per_frame_{on,off}.csv`)에서
>   다시 읽은 값입니다(aux 행만 예외 — 재채점 범위 밖이라 구 GT 덤프에서 읽음).
> - `F08_dual_axis_obligation.md`: **프레임 축 단독 인쇄 금지.** 이 패널들로 "RGB가 맞혔다/틀렸다"를 말할 때
>   반드시 칸 축 수치를 병기하십시오(`EVL12_CELL_AXIS.md` §4 — τ=0.5에서 프레임 축과 칸 축의 H 우열이 **반대**).
> - `F09_aux_heads_off.md`: **본 표 9런은 aux가 꺼져 있습니다.** aux 행 1장은 `SEED_TABLE.md` §5의
>   **부록 ablation** 런이며 본 표가 아닙니다.

---

## 1. 명명 규약

```
<family>_<scene>_<model>-<seed>_<hit|miss|arm>.png
```

| 필드 | 값 | 뜻 |
|---|---|---|
| `family` | `hitmiss` · `faoff` · `gazebo` | 패널 자산군 |
| `scene` | `scene05/14/15` · `sceneC2` · `drop1` | 씬 ID (Gazebo는 드롭 프리셋 ID) |
| `model` | `rgb` · `depth` · `b2` · `rgbaux` | 입력 모달리티 (`rgbaux` = 부록 ablation) |
| `seed` | `s42/43/44` | 훈련 시드 |
| 말미 | `hit` · `miss` · `arm` | H 성공 / H 실패 / 팔 대조(off팔 또는 ctrl-vs-drop) |

패널 레이아웃은 3분할 공통: **입력 이미지 | GT 격자 | 예측 확률 격자(τ=0.5)** — V3_BRIEF §6-1이 요구하는
"입력 + 그리드 오버레이 + GT" 형식을 원본이 이미 만족합니다. Gazebo 2장만 2분할(그리드 오버레이 | 확률 격자)입니다.

---

## 2. 씬 사전 (캡션 읽기용)

| 씬 | 정체 | 출처 |
|---|---|---|
| `scene14` | **포템킨 시민광장 대계단** — 40단 · 총낙차 6.0 m. 정면에서 계단이 **보이지 않는 것**이 설계 의도. strict-H 60프레임 전부 test | `code/scene_knowledge.json` · `scenes/main/scene14_*.py` |
| `scene15` | **비탈 골목-계단 미로** — 폭 1.2 m 회랑, 25° 굽이 뒤 12+13단, 낙차 4.25 m. strict-H 36프레임 전부 test | 〃 |
| `scene05` | **반원형 야외극장** — 립 0.398 m → 3단 → 무대 −1.6 m. 방사형 화강암 띠(대리선)가 실제 모서리를 이김 | 〃 |
| `sceneC2` | **낙엽에 묻힌 공원 석계단** — 기하는 불변, 단서만 매몰. 좌측 파이프 난간이 유일한 가시 증거 | 〃 |
| `sceneN3` | **트롱프뢰유 페인트 계단 — 하드 네거티브.** 낙차는 페인트 1 mm. 전 픽셀 GT 무낙차 | 〃 |

---

## 3. 패널 색인 24행

### 3.1 H 성공/실패 — 본 표 3모델 × 3시드 (18장)

**읽는 법**: 같은 씬(scene14)에서 `hit`은 `s20260819` 프레임, `miss`는 `::boost_h` 프레임인 짝이 여럿입니다.
**같은 모델·같은 씬·같은 조명(L5)인데 라운드만 다르면 0.98 → 0.007로 무너지는 것**이 이 세트의 요지입니다.

| # | 파일 | 원본 경로 (프로비넌스) | tier · max p · GT칸 · 발화칸 | 무엇을 보여주는가 (한국어 1줄) | 논문 절 |
|---|---|---|---|---|---|
| 1 | `hitmiss_scene14_rgb-s42_hit.png` | `experiments/dayrun_0820/runs/v2/rgb_s42/viz/hitH_01_on__scene14__L5__s20260819__0006.png.png` | H · 0.981 · 10 · 10 | RGB s42가 scene14 대계단을 **3a·3b 10칸 전부** 맞힌 최상 사례 — 계단 자체는 화면에 안 보이고 광장 바닥의 결·그림자만 있다 | §5.2 · §5.3 |
| 2 | `hitmiss_scene14_rgb-s42_miss.png` | `.../rgb_s42/viz/missH_01_on__scene14__L5__s20260820__0006.png::boost_h.png` | H · **0.007** · 5 · **0** | 같은 모델·같은 씬·같은 조명(L5)인데 boost_h 라운드에서는 **20칸 전부 0.00** — 시점이 바뀌어 립이 화면과 거의 평행해지면 신호가 사라진다 | §5.3 · §5.4 |
| 3 | `hitmiss_scene14_rgb-s43_hit.png` | `.../rgb_s43/viz/hitH_02_on__scene14__L5__s20260819__0000.png.png` | H · 1.000 · 10 · 3 | **최고 시드(s43, H .875)**의 성공 컷 — 확신은 1.000이지만 발화는 10칸 중 3칸뿐(칸 축 recall이 프레임 축보다 낮은 이유의 눈으로 보는 판) | §5.2 각주(F08) |
| 4 | `hitmiss_scene15_rgb-s43_miss.png` | `.../rgb_s43/viz/missH_03_on__scene15__L4__s20260820__0000.png::boost_h.png` | H · 0.309 · 2 · 0 | 골목 회랑(scene15)에서 굽이 뒤 계단을 **0.309로 문턱 아래 놓친 사례** — 양성칸이 2칸뿐이라 프레임 축에서 통째로 실패 처리된다 | §5.3 |
| 5 | `hitmiss_scene14_rgb-s44_hit.png` | `.../rgb_s44/viz/hitH_04_on__scene14__L5__s20260819__0000.png.png` | H · 0.992 · 10 · **1** | 성공으로 세지지만 **10칸 중 1칸만 발화** — 프레임 축 any-hit 규칙(`EVL-08`)이 상을 주는 바로 그 행동 | §5.2 각주(F08) |
| 6 | `hitmiss_scene14_rgb-s44_miss.png` | `.../rgb_s44/viz/missH_02_on__scene14__L5__s20260820__0006.png::boost_h.png` | H · **0.000** · 5 · 0 | 시드 s44의 같은 프레임 완전 무발화 — #2와 짝지어 **시드 간 실패 모드가 공통**임을 보인다 | §5.3 · §5.6 |
| 7 | `hitmiss_scene14_depth-s42_hit.png` | `.../depth_s42/viz/hitH_02_on__scene14__L5__s20260820__0004.png::boost_h.png` | H · 1.000 · 10 · **10** | Depth s42가 boost_h 라운드에서 **10칸 전부 발화** — RGB가 같은 라운드에서 0.007로 죽는 프레임군(#2)과 대비 | §5.2 |
| 8 | `hitmiss_scene15_depth-s42_miss.png` | `.../depth_s42/viz/missH_02_on__scene15__L4__s20260820__0001.png::boost_h.png` | H · 0.190 · 1 · 0 | Depth의 실패는 **좁은 골목·양성칸 1칸**의 극소 표적에서 나온다 | §5.3 · §5.4 |
| 9 | `hitmiss_scene14_depth-s43_hit.png` | `.../depth_s43/viz/hitH_02_on__scene14__L5__s20260819__0003.png.png` | H · 1.000 · 10 · 10 | Depth 전 시드 공통의 "맞히면 전면 발화" 패턴 (칸/FA프레임이 RGB의 1.6–2.4배인 행동의 양성면) | §5.2 |
| 10 | `hitmiss_scene14_depth-s43_miss.png` | `.../depth_s43/viz/missH_04_on__scene14__L0__s20260820__0001.png::boost_h.png` | H · **0.000** · 4 · 0 | Depth도 특정 boost_h 시점에서는 완전 침묵 — **실패가 모달리티 특유가 아니라 시점·거리 특유**임을 보이는 컷 | §5.4 · §5.6 |
| 11 | `hitmiss_scene14_depth-s44_hit.png` | `.../depth_s44/viz/hitH_02_on__scene14__L5__s20260819__0000.png.png` | H · 0.999 · 10 · 10 | 시드 3/3 재현 (7·9와 동일 패턴) | §5.2 |
| 12 | `hitmiss_scene14_depth-s44_miss.png` | `.../depth_s44/viz/missH_02_on__scene14__L5__s20260820__0007.png::boost_h.png` | H · 0.026 · 5 · 0 | 〃 실패면의 시드 3/3 재현 | §5.6 |
| 13 | `hitmiss_scene14_b2-s42_hit.png` | `.../b2_s42/viz/hitH_04_on__scene14__L5__s20260819__0001.png.png` | H · 0.711 · 9 · 3 | B2(2-스트림)의 성공은 **확신이 낮고 부분적** — 표의 B2 H .229를 눈으로 확인하는 컷 | §5.2 |
| 14 | `hitmiss_scene14_b2-s42_miss.png` | `.../b2_s42/viz/missH_04_on__scene14__L5__s20260820__0006.png::boost_h.png` | H · 0.000 · 5 · 0 | #2·#6과 **같은 프레임**: RGB·B2가 동시에 죽는다 (FA 비중첩과 달리 **실패는 겹친다**는 반례) | §5.6 |
| 15 | `hitmiss_scene15_b2-s43_hit.png` | `.../b2_s43/viz/hitH_01_on__scene15__L4__s20260820__0000.png::boost_h.png` | H · 0.826 · 2 · **5** | B2가 scene15에서 성공하지만 **GT 2칸에 5칸 발화** — 맞힘과 과발화가 같이 온다 | §5.2 · §5.6 |
| 16 | `hitmiss_scene14_b2-s43_miss.png` | `.../b2_s43/viz/missH_03_on__scene14__L7__s20260820__0006.png::boost_h.png` | H · 0.076 · 5 · 0 | 조명 L7(역광 계열)에서도 같은 실패 — 실패 원인이 조명이 아님을 보이는 대조 | §5.4 |
| 17 | `hitmiss_scene14_b2-s44_hit.png` | `.../b2_s44/viz/hitH_02_on__scene14__L5__s20260820__0007.png::boost_h.png` | H · 0.949 · 5 · 2 | B2도 boost_h에서 성공하는 프레임이 있다 — **라운드 전체가 불가능한 게 아니라 시점 분포 문제** | §5.4 |
| 18 | `hitmiss_scene15_b2-s44_miss.png` | `.../b2_s44/viz/missH_04_on__scene15__L0__s20260820__0000.png::boost_h.png` | H · 0.001 · 2 · 0 | 골목 씬의 B2 완전 실패 | §5.6 |

### 3.2 부록 — aux(픽셀 보조손실) ablation (1장)

| # | 파일 | 원본 경로 | 수치 | 무엇을 보여주는가 | 논문 절 |
|---|---|---|---|---|---|
| 19 | `hitmiss_scene14_rgbaux-s42_hit.png` | `experiments/dayrun_0820/runs/v2/rgb_s42_aux/viz/hitH_02_on__scene14__L5__s20260819__0003.png.png` | H · 0.996 · 10 · 9 | **`SEED_TABLE.md` §5 부록 ablation 런**(aux_enabled=True, λ=0.5, 아모달 마스크 648장). ⚠ **본 표 9런은 aux가 꺼져 있습니다** — `F09_aux_heads_off.md` 준수 필수 | §5.1 부록 |

### 3.3 off팔 오경보 — "낙차가 없는데 발화한다" (3장)

**읽는 법**: off팔은 GT가 전 칸 0입니다(`EVL12 §1` 코드 어서션 `gt.sum()==0`). 그런데도 3b 밴드가 탑니다.
`FA_CENSUS.md` §3에서 **경계칸형 반경(3b) lift 2.71** 로 기계적으로 확인된 그 현상의 육안 판입니다.

| # | 파일 | 원본 경로 | 수치 | 무엇을 보여주는가 | 논문 절 |
|---|---|---|---|---|---|
| 20 | `faoff_scene15_rgb-s42_arm.png` | `.../rgb_s42/viz/fa_off_02_off__scene15__L4__s20260819__0003.png.png` | off · **0.975** · GT 0 · **4칸 발화** | 계단을 뺀 골목에서 RGB가 B3b 0.98 / C3b 0.95로 발화 — **FA 센서스 최고 집중 칸 (scene15, B3b) 181건 / (scene15, C3b) 171건의 대표 컷** | §5.2 · §개입실험 |
| 21 | `faoff_sceneC2_depth-s42_arm.png` | `.../depth_s42/viz/fa_off_01_off__sceneC2__L2__s20260819__0005.png.png` | off · 0.980 · GT 0 · 4칸 발화 | Depth의 희소한 off팔 FA가 **sceneC2(낙엽 매몰 석계단)에 67 % 집중**(147/219건, `fa_events_v2corr.csv`) — 시드-다수결 칸으로 세면 RGB 269칸 대 Depth 42칸인 그 42칸 쪽 | §5.2 |
| 22 | `faoff_scene05_b2-s42_arm.png` | `.../b2_s42/viz/fa_off_01_off__scene05__L5__s20260819__0006.png.png` | off · 0.997 · GT 0 · 3칸 발화 | 야외극장 방사형 화강암 띠(대리선)가 남은 off팔에서 B2가 0.997 발화 | §5.2 · §개입실험 |

### 3.4 Gazebo before/after — 교차-시뮬 (2장)

⚠ `F11_gazebo_claim_boundary.md`: **트윈 붕괴를 단서 증거로 인용 금지.** 안전 주장 2종만(§7-2).
이 2장은 **이미 공개 추적 경로**(`experiments/weekend_0823/gazebo/out/panels/`, `INDEX.md` §4 "제출가능")에 있으며,
여기 사본은 초안 편의용입니다. **구제(rescue)가 아닙니다.**

| # | 파일 | 원본 경로 | 무엇을 보여주는가 | 논문 절 |
|---|---|---|---|---|
| 23 | `gazebo_drop1ctrl_rgb-s42_arm.png` | `experiments/weekend_0823/gazebo/out/panels/rgb_s42__gz_drop1_ctrl__preset_h0.3_d2.png` (1690×650 → **1600×615 축소**) | **before(대조군)** — 낙차 없는 Gazebo 컷 | §교차-시뮬 |
| 24 | `gazebo_drop1_rgb-s42_arm.png` | `.../rgb_s42__gz_drop1__preset_h0.3_d2.png` (1690×650 → **1600×615 축소**) | **after(낙차)** — 같은 프리셋 h0.3/d2에서 B3b 0.82 · C3b 0.73 발화. 요점은 **두 장이 육안으로 거의 구분되지 않는데 확률만 갈린다**는 것 | §교차-시뮬 · §7-2 |

---

## 4. 기록된 구멍 — **재생성 행이지 날조 대상이 아님**

> 아래는 "논문에 필요한데 **기존 산출물이 없어서** 복사할 수 없었던" 항목입니다.
> Part A 규약상 **합성 패널을 지어내지 않았습니다.** 각 행은 다음 GPU/CPU 창의 **재생성 작업 항목**입니다.

| # | 없는 것 | 왜 필요한가 | 로컬에 있는 것 / 왜 못 쓰나 | 처분 |
|---|---|---|---|---|
| G-1 | **CUE-OFF 팔별 비교 스트립** | V3_BRIEF §6-1 필수 패널 목록의 "CUE-OFF 팔별". `§개입실험` 절에 쓸 그림이 **하나도 없다** (`INDEX.md` §4가 이미 기록) | `experiments/weekend_0823/cue_audit/smoke/scene{12,17,20}/` 에 **원본 렌더 1장씩 3장뿐** — 팔(A/B1/B2/C/P) 대조 합성물이 아님. `cue_audit/` 전체에 정성 패널 0장 | **재생성**: `dataset/cueoff/260823_cueoff*_{A,B1,B2,C,P}/` 렌더는 로컬에 존재하므로, 팔별 스트립은 **기존 렌더만으로 합성 가능** (신규 렌더 불요) |
| G-2 | **YOLO 검출기 행의 test-core 정성 예시** | `§5.2 row 4` (F01 어댑터 스코프)의 육안 근거 | `experiments/dayrun_0820/runs/yolo_s{42,43,44}/` 57장은 **전부 학습 곡선·혼동행렬·`val_batch*` 모자이크** — test-core hit/miss 패널이 **애초에 생성된 적 없음**. 게다가 `.gitignore:18 **/runs/**/*.jpg` 로 차단 | **재생성**: `pred_test/labels/` + `eval_test/per_frame.csv` 로 CPU 합성 가능 |
| G-3 | **aux 아모달 마스크 패널 (H 프레임)** | V3_BRIEF §6-1 필수 목록 · GPU-5 (b) | 마스크 전수 추출이 아직 안 됨 (GPU 작업) | **GPU 대기** |
| G-4 | **v3-B 어트리뷰션 패널** | V3_BRIEF §6-1 필수 목록 | v3-B 런 자체가 미착수 | **v3 학습 후** |
| G-5 | **2×2 4팔 한 씬 세트** | V3_BRIEF §6-1 필수 목록 | 2×2 직교화는 v3 설계이며 런 없음 | **v3 학습 후** |
| G-6 | **strict-H 트윈 잔차 패널의 사본** | F04("완전가림 아님")의 시각 증거 | **구멍 아님** — `experiments/weekend_0823/rt_response/panels/` 7장이 **이미 공개 추적 경로**에 있음. 중복 복사 안 함 | 조치 불요 |

---

## 5. 재현

```bash
# 이 디렉터리를 다시 만드는 명령 (CPU · git 무접촉 · 복사/축소 전용, 약 3초)
PYTHONNOUSERSITE=1 python3 experiments/v3_0823/code/curate_panels_0830.py
```

원본 24개 경로는 §3의 "원본 경로" 열이 전부이며, **선별 목록의 정본은 본 문서 §3**입니다
(드라이버의 `SEL` 리스트는 그 사본). 스크립트는 (a) 1600 px 초과 시 LANCZOS 축소,
(b) 그 외에는 `shutil.copy2` 바이트 복사, (c) `experiments/v3_0823/eval_v2corr/<run>/per_frame_{on,off}.csv`
(**교정 GT 정본**)에서 `max p`·GT칸·발화칸을 다시 읽어 본 표의 수치 열을 채웁니다.
단 **aux 행(#19)만** 재채점 범위 밖이라 `runs/v2/rgb_s42_aux/eval_test/per_frame_on.csv`(구 GT 덤프)에서
읽습니다 — H 컷이므로 `V2_RESCORE.md` §2의 "H 행 바이트 동일"에 의해 두 GT에서 같은 값입니다.

**검증**: `git check-ignore submission_0830/panels/*.png` → 종료코드 1(미차단) = **공개 리포에서 추적 가능**.
이것이 `INDEX.md` §4 누락위험 1의 처분 조건이었습니다.
