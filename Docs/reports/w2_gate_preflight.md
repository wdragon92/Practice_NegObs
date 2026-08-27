# W2 사전 게이트 3건 — 창 리세스 렌더 게이트 · scene14 파라펫 검산 · GRAZE v2 잔여 WARN 육안

작성 2026-07-29 · GPU 전담(단독 점유) · 렌더 순차 실행 · 저장소 추적 파일 수정 0건 · 커밋 0건
산출물: 본 문서 1건 + `look_check/` 하위 이미지(전부 `.gitignore` 대상)

| 게이트 | 판정 | 한 줄 |
|---|---|---|
| **T1 창 리세스 렌더 게이트** | ✅ **PASS** | 유리 소실 0 · Z-파이팅 0 · GRAZE v2 FAIL 0 → `scene_common.py` 창 리세스 **커밋 가능** |
| **T2 scene14 파라펫 V자 톱니** | ✅ **코드 무결 · 렌더도 최신** | 3D 상단 폴리라인은 **완전 단조**(이음부 Δz = 0.000000 m). 화면의 V자는 **투영 결과**이며 톱니 개수 = 참 3개(구 결함은 40단) |
| **T3 GRAZE v2 잔여 WARN 2건** | ⚠️ **둘 다 진성 변화 · 은닉 회귀 아님** | 두 건 모두 **에지 행 인접 지면 알베도 변화**. 에지선은 두 라운드 모두 존속 → §3.4 임계 재조정안 제시 |

> 임무 지시문의 라운드 지정 1건 정정: T3 scene13 "국소도 15.7 · 에지대역 y131~212" 페어는
> `r1_on→r2_on` 이 아니라 **`v6_rt→v7_rt`** 다 `[실측]`. `scene13 r1_on→r2_on` 의 GRAZE 는
> 세 컷 모두 **판정유보(측광)** 이고 spec 15.7 이 나오지 않는다(§3.1). scene07 은 지시대로
> `r1_on→r2_on` 이 맞다. `graze_recalibration_v1.md` §7 표기와 일치한다.

---

## 0. 실행 환경 (3건 공통)

```bash
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh && conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 NEGOBS_PT_FAST=1
cd /home/vislab/Desktop/work_sy/Practice_NegObs
```

착수 전 `nvidia-smi` 확인 `[실측]`: 컴퓨트 프로세스 0, 점유 1,687 MiB / 24,564 MiB (Xorg·gnome-shell·
브라우저 등 데스크톱만) → 유휴 확정. 렌더 4+2회 전부 **직렬**, 동시 실행 0.

---

## 1. T1 — 창 리세스 렌더 게이트 (본론)

### 1.1 판정 요약

| 판정 기준 | 결과 | 근거 |
|---|---|---|
| ① 파사드 유리 픽셀 소실 없음 | ✅ | 유리 덩어리 수 불변 · 유리화소 −0.6~−1.4 % (실루엣 1px 경계) · IoU 97.0~98.6 % |
| ② Z-파이팅 반짝임 없음 | ✅ | 유리면 **내부 비유리 화소 = 0 개**(18개 조건 전부) · 내부 휘도 std 잡음바닥 이내 |
| ③ `regression_check.py`(GRAZE v2) FAIL 0 | ✅ | **6컷 전부 PASS** (FAIL 0 · WARN 0 · INFO 0) · gz_spec 0.10~3.91 (WARN 임계 8.0) |

**→ T1 PASS. `scene_common.py` 작업 트리의 창 리세스 수정(돌출 20 mm → 5 mm, `/Win_` 2,041 프림)은
커밋 가능하다.** 같은 파일의 `VEG_DEBRIS` oakfall2 행은 `fix_small_w1.md` §1.3 의 코드 증명대로
렌더 무영향이므로 분리 커밋이 불필요해졌다 — **두 변경을 한 번에 커밋해도 안전하다.**

### 1.2 방법 — 게이트를 A/B 로 세운 이유

지시된 비교 대상(`scene02` = `v7_pt`, `sceneN3` = 최신 라운드 `r2_on`)은 **A/B 대조군이 아니다** `[실측]`:

| 라운드 | 렌더 시각 | 그 뒤에 들어온 커밋 |
|---|---|---|
| `scene02/v7_pt` | 07-27 22:26 | `86f195e`(초기) 이후 07-29 커밋 전부 |
| `scene02/r2_on`·`sceneN3/r2_on` | 07-28 22:45 / 23:01 | `1fe3a2e` 식생 USD · `bc87292` build_building 3단 · `dada81c` 난간 간살 · `18c8643` 낙엽 실물 · `fb71420` 관목 실물 · `d8fd7c2` 파사드 저층부 · `8ac024d` 손잡이 · `a9a3b22` 인프라 키트 · `dc88f21` 레드팀 5건 (전부 07-29 00:0x~00:5x) |

이 라운드들과 비교하면 **창 15 mm 이동 외의 변경이 화면 전체를 덮어** ①②를 판정할 수 없다.
그래서 **같은 세션·같은 GPU·같은 설정**으로 두 판을 나란히 렌더했다:

- **base** = `git show HEAD:scene_common.py` (창 리세스 **수정 전**)
- **gate** = 작업 트리 `scene_common.py` (창 리세스 **수정 후**)
- **gate_rep** = gate 와 **완전 동일 코드 2회차** → **PT 샘플러 잡음 바닥** 측정용

base 판은 스크래치패드에 `scene_common.py`(HEAD 사본) + 나머지 키트·assets 심링크로 트리를 만들고
씬 스크립트를 복사해 실행했다(파이썬은 `sys.path[0]` 을 **realpath 로 해석**하므로 씬 스크립트는
심링크가 아니라 복사여야 한다 `[실측]`). **저장소 추적 파일은 읽기(`git show`)만 했다.**

렌더 설정은 `scripts/rounds/run_p2_all33.sh` 의 `r*_on` 과 완전 동일(`NEGOBS_LOOK_V1=1` · `NEGOBS_PT_FAST=1` ·
scene02 만 `NEGOBS_PT_TOTAL_SPP=256` · `NEGOBS_PARAMS_OVERRIDE` 동일 · `pt` 모드).

### 1.3 재현 명령

```bash
S=<스크래치패드>
# base 트리 구성
mkdir -p $S/headtree && git show HEAD:scene_common.py > $S/headtree/scene_common.py
ln -s $PWD/{facade_kit.py,infra_kit.py,stair_kit.py,building_kit.py,assets} $S/headtree/
ln -s $PWD/scenes/batch1/batch1_common.py $S/headtree/
cp scenes/main/scene02_underpass.py scenes/batch1/sceneN3_trompe_loeil.py $S/headtree/

VIEWS=preset_h0.3_d2,preset_h0.3_d5,preset_h0.3_d10
OV='{"render":{"pt_total_spp":64,"pt_max_bounces":8}}'
for pair in "$S/headtree/scene02_underpass.py look_check/scene02/wininset_base 256" \
            "scenes/main/scene02_underpass.py  look_check/scene02/wininset_gate 256" \
            "$S/headtree/sceneN3_trompe_loeil.py look_check/sceneN3/wininset_base" \
            "scenes/batch1/sceneN3_trompe_loeil.py look_check/sceneN3/wininset_gate"; do
  set -- $pair
  env NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1=1 ${3:+NEGOBS_PT_TOTAL_SPP=$3} \
      NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_VIEWS=$VIEWS \
      NEGOBS_CAPTURE_DIR=$2 NEGOBS_PARAMS_OVERRIDE="$OV" python "$1"
done
# 판정 ③
python scripts/regression_check.py --before look_check/scene02/wininset_base \
                                   --after  look_check/scene02/wininset_gate
python scripts/regression_check.py --before look_check/sceneN3/wininset_base \
                                   --after  look_check/sceneN3/wininset_gate
```

실행 결과 `[실측]`: 4회 전부 `EXIT=0 FILES=3`, 소요 38 s / 39 s / 23 s / 23 s.

### 1.4 판정 ① — 유리 픽셀 소실

유리 마스크: `(B−R>20) & (B−G>10) & (L<138)`. 하늘(L>140)·벽돌(R>B)·콘크리트(B−R≈8)를 배제하는
분리선이며, 6컷 전부 청색우세 화소 히스토그램이 **L 110~130(유리) / L 140~160(하늘)** 로 이봉
분포이고 그 사이 골(L 130~140)에 임계를 두었다 `[실측]`. 세 판(base/gate/gate_rep)에 **동일 규칙**을
적용한다.

| 컷 | 유리화소 base→gate | 덩어리(≥50px) base→gate | IoU | **잡음바닥** gate→gate_rep |
|---|---|---|---|---|
| scene02 `h0.3_d2` | 68,914 → 68,259 (−0.95 %) | **24 → 25** | 97.55 % | +0.16 % · 25→25 · IoU 98.32 % |
| scene02 `h0.3_d5` | 65,334 → 64,942 (−0.60 %) | **27 → 29** | 97.89 % | −0.10 % · 29→27 · IoU 98.55 % |
| scene02 `h0.3_d10` | 52,902 → 52,409 (−0.93 %) | **30 → 29** | 97.62 % | +0.05 % · 29→29 · IoU 98.49 % |
| sceneN3 `h0.3_d2` | 44,767 → 44,411 (−0.80 %) | **38 → 38** | 98.59 % | +0.10 % · 38→38 · IoU 99.38 % |
| sceneN3 `h0.3_d5` | 39,922 → 39,661 (−0.65 %) | **35 → 33** | 98.41 % | +0.08 % · 33→33 · IoU 99.01 % |
| sceneN3 `h0.3_d10` | 35,754 → 35,238 (−1.44 %) | **32 → 34** | 96.99 % | +0.18 % · 34→33 · IoU 98.18 % |

- **소실된 창은 하나도 없다.** 창이 셸에 묻혔다면 덩어리 수가 무너지고 IoU 가 급락해야 하는데
  덩어리 수는 ±2 범위이고, 그 ±2 는 **동일 코드 2회차(gate↔gate_rep)에서도 똑같이 나타난다**
  (25→25, 29→27, 34→33) — 잡음에 의한 연결성분 분리/병합이다.
- 유리화소 −0.6~−1.4 % 는 잡음바닥(±0.2 %)보다 크므로 **실재하는 변화**다. 실체는 **창 실루엣
  1픽셀 테두리**다: `base 에만` 화소(881~1,179 px)가 `gate 에만`(139~524 px)보다 많고, 그 차이가
  덩어리 내부가 아니라 경계에 몰린다. 유리가 15 mm 안으로 들어가면 파사드 법선 방향 투영폭이
  미세하게 줄어드는 **기하학적으로 기대되는 결과**이며, 창 1개가 사라지는 것과는 성질이 다르다.

**크롭 이미지** (base / gate / gate_rep / 참고라운드 4단, 3배 확대):

| 경로 |
|---|
| `look_check/scene02/wininset_crop/win_preset_h0.3_d2.png` (crop x608–1120 y96–210) |
| `look_check/scene02/wininset_crop/win_preset_h0.3_d5.png` (crop x641–993 y0–224) |
| `look_check/scene02/wininset_crop/win_preset_h0.3_d10.png` (crop x688–1087 y0–124) |
| `look_check/sceneN3/wininset_crop/win_preset_h0.3_d2.png` (crop x226–866 y0–247) |
| `look_check/sceneN3/wininset_crop/win_preset_h0.3_d5.png` (crop x334–974 y0–249) |
| `look_check/sceneN3/wininset_crop/win_preset_h0.3_d10.png` (crop x443–1058 y26–251) |

육안 `[실측]`: 세 판의 창 사각형이 **개수·위치·모서리·색 전부 동일**. 4단째의 참고 라운드
(scene02 `v7_pt` / sceneN3 `r2_on`)는 창 개수·배치는 같으나 벽돌 텍스처·창대 띠·식생이 달라
§1.2 의 "대조군이 아니다" 를 눈으로 확인시켜 준다.

### 1.5 판정 ② — Z-파이팅

Z-파이팅은 동일평면 깊이 충돌이므로 **유리 사각형 안쪽에 벽색이 섞여 드는 고주파 얼룩**으로 나타난다.
각 유리 덩어리(≥300 px)를 5×5 침식한 **내부**에서 비유리 화소를 센다.

| 컷 | base 내부 비유리 | **gate 내부 비유리** | gate_rep | 내부 휘도 std (base / gate / rep) |
|---|---|---|---|---|
| scene02 `d2` | 0 (0.000 %) | **0 (0.000 %)** | 0 | 2.52 / 2.52 / 2.28 |
| scene02 `d5` | 0 | **0** | 0 | 1.87 / 1.78 / 1.74 |
| scene02 `d10` | 0 | **0** | 0 | 0.98 / 1.15 / 1.19 |
| sceneN3 `d2` | 0 | **0** | 0 | 1.11 / 1.10 / 1.14 |
| sceneN3 `d5` | 0 | **0** | 0 | 1.10 / 1.03 / 1.26 |
| sceneN3 `d10` | 0 | **0** | 0 | 1.57 / 1.51 / 1.65 |

- **18개 조건 전부 내부 비유리 화소 0 개** `[실측]`. 내부 휘도 std 도 gate 가 base·gate_rep 사이에
  들어간다 = 잡음 이상의 얼룩이 없다.
- 기하로도 필연이다 `[계산]`: `recess = min(ins, 0.005 + WIN_T/2 − WIN_EPS) = 0.015` →
  유리 외면 = 파사드면 **+5 mm**. 동일평면(0 mm)이 아니므로 깊이 충돌이 성립할 수 없다.
- 유리영역 전체 |Δ| 도 base↔gate 평균 0.94~1.25 · p99 13~16 로, 40 을 넘는 화소(23~301 px)는
  전부 실루엣 1px 경계다(잡음바닥 gate↔rep 은 |Δ|>40 이 **0 px**).

### 1.6 판정 ③ — `scripts/regression_check.py` (GRAZE v2)

```
scene02 [wininset_base → wininset_gate]   3컷 중 FAIL 0 · WARN 0 · INFO 0 · PASS 3  → 회귀 없음
sceneN3 [wininset_base → wininset_gate]   3컷 중 FAIL 0 · WARN 0 · INFO 0 · PASS 3  → 회귀 없음
```

`gz_spec` `[실측]` (WARN 8.0 / FAIL 20.0):

| 컷 | base→gate | **잡음바닥** gate→gate_rep |
|---|---|---|
| scene02 `d2` / `d5` / `d10` | 3.906 / 1.190 / 1.706 | 3.417 / 1.682 / 1.937 |
| sceneN3 `d2` / `d5` / `d10` | 0.632 / 0.104 / 1.284 | 0.630 / −0.687 / −0.409 |

**base↔gate 의 국소도가 잡음바닥과 사실상 같다** — 창 15 mm 이동은 에지 대역에 측정 가능한
신호를 남기지 않는다. `fix_small_w1.md` §2.7 의 "판정 거리에서 15 mm 는 서브픽셀이라 개선폭이
안 보인다" 는 추정과 정합한다. 게이트의 목적은 개선폭이 아니라 **결함 유무**이므로 이 결과가 합격이다.

DARK/BLOWN/WHITE/OCCL/FRAME/PHOTO 6종도 전부 무발화(`블록이동 0 %` · `신규암부 0.0`).

### 1.7 부수 관찰 (T1 범위 밖 · 레드팀/감독 이관)

**sceneN3 현행 코드에 분홍 개화 벚나무 2본이 들어와 있다** `[실측]`
(`look_check/sceneN3/wininset_gate/pt_noon_preset_h0.3_d{2,5,10}.png`, 프레임 상단 x≈600·1150).
같은 좌표의 `r2_on`(07-28 23:01)에는 없고 녹엽 가로수였다 → **07-29 커밋(`1fe3a2e` 식생 USD 전환
또는 `fb71420` 관목 실물화) 이후 유입**. 확정 규약 *"벚꽃·단풍 등 계절/이벤트 특정 요소 금지"*
후보 위반이며, `graze_recalibration_v1.md` §10 이 sceneC2 에서 보고한 것과 **같은 유형·다른 씬**이다.
33씬 전수 점검이 필요해 보인다(본 임무에서 손대지 않음).

---

## 2. T2 — scene14 파라펫 V자 톱니 코드-렌더 괴리 검산

### 2.1 결론

**둘 다 아니다.** 코드는 톱니를 만들지 않고(3D 상단 폴리라인 **완전 단조**), 렌더도 구본이 아니다
(현행 코드로 렌더된 최신 라운드에 동일 실루엣 존재). 화면의 V자는 **단조 폴리라인을 `lower_lookup`
시점에서 투영한 결과**다 — 즉 C3 의 "V자 지그재그 실재" 관측은 **화면상 사실이지만**, 그로부터
추론된 "v6 봉합 코드에 버그가 살아있다"는 **성립하지 않는다**.

### 2.2 렌더 시차 배제 `[실측]`

| 항목 | 시각 |
|---|---|
| `scenes/main/scene14_grandstair_illusion.py` mtime | **2026-07-27 21:22** (이후 수정 없음) |
| `look_check/scene14/v7_pt/` | 2026-07-27 22:44 (소스 수정 **뒤**) |
| `look_check/scene14/r2_on/` | 2026-07-28 22:54 (가장 최신) |

`v7_pt` 는 이미 현행 scene14 코드로 렌더된 것이고, 하루 뒤 `r2_on` 도 **같은 실루엣**을 낸다
(비교 크롭 `look_check/scene14/parapet_crop/lower_lookup_right.png`, 우측 파라펫 x1240–1920 y420–620 2배).
→ "렌더가 수정 전 것" 가설은 기각.

### 2.3 프림 검산 — 살아있는 코드에서 상단 폴리라인 추출

`NEGOBS_SMOKE=1` 은 계단·레벨 z 표만 출력하고 **파라펫을 다루지 않는다**(`_smoke_report()` 전문 확인).
`_rake_segments` 는 `main()` 안 중첩 함수라 import 로 못 잡으므로, `ast` 로 **원본 소스 노드를 그대로
떼어내 실행**했다(재구현 아님, `scenes/main/scene14_grandstair_illusion.py:599`).

```
[상수] rail_h=0.95  cap_t=1.4  ang=23.806°  lap=0.7151
[헌치 상단 폴리라인]
   rake  x   0.00→  3.40   top  +0.950→ -0.550
   land  x   3.40→  5.80   top  -0.550→ -0.550
   rake  x   5.80→  9.20   top  -0.550→ -2.050
   land  x   9.20→ 11.60   top  -2.050→ -2.050
   rake  x  11.60→ 15.00   top  -2.050→ -3.550
   land  x  15.00→ 17.40   top  -3.550→ -3.550
   rake  x  17.40→ 20.80   top  -3.550→ -5.050
[검사] 3D 상단 폴리라인 단조 하강 = True   이음부 Δz 최대 = 0.000000 m
[검사] 본체(Parapet_*) 상면 = 디딤면 − offset(0.03) → 헌치보다 최소 0.98 m 아래 (실루엣 미기여)
```

**이음부 단차가 부동소수 오차조차 없이 정확히 0 이고, 폴리라인은 엄격히 단조 하강한다.**
v5.1 재작(계단식 → 사선 헌치)과 v6 쐐기 봉합은 **코드상 살아 있고 정상 동작한다.**

### 2.4 그럼 화면의 V자는 무엇인가 — 투영 대조

`lower_lookup`(eye 26,0,−5.2 → tgt 8,0,−2 · hfov 60° · 1920×1080)으로 위 폴리라인을 투영해
`r2_on/pt_noon_lower_lookup.png` 에 겹쳤다.

| x | z(헌치 상면) | 화면 px | **화면 py** |
|---|---|---|---|
| 0.00 | +0.95 | 1274.8 | **446.2** ← 봉 |
| 3.40 | −0.55 | 1324.1 | **495.1** ← 골 |
| 5.80 | −0.55 | 1365.6 | **456.3** ← 봉 |
| 9.20 | −2.05 | 1451.3 | **524.4** ← 골 |
| 11.60 | −2.05 | 1530.1 | **474.4** ← 봉 |
| 15.00 | −3.55 | 1715.2 | **585.0** ← 골 |
| 17.40 | −3.55 | 1919.0 | **517.4** ← 봉 |

오버레이 `look_check/scene14/parapet_crop/overlay_flipp.png` (확대본
`look_check/scene14/parapet_crop/overlay_right_zoom.png`) — **투영선이 렌더 실루엣의 봉·골에
정확히 얹힌다** `[실측]`.

원리 `[기하]`: 카메라가 파라펫 **아래**(z −5.2)에 있고 시선이 계단 축과 거의 나란하다.
- **사선(rake) 구간**: 카메라에서 멀어질수록 z 가 빠르게 올라가 앙각 `Δz/D` 가 **증가**
- **참(land) 구간**: z 가 일정한데 거리 D 만 늘어 앙각이 **감소**

→ 3D 로는 단조 하강인 선이 화면에서는 **참마다 한 번씩 되꺾이는 톱니**로 보인다.
톱니 개수 = **참 개수 3개**이고, 구 결함(계단식 스텝 파라펫)이었다면 **40단 = 40개**여야 한다.
즉 렌더는 v5.1 수정이 **먹혔음을 오히려 증명**한다.

### 2.5 남는 판단 — 이건 결함인가 (감독 결재 사항)

기하·코드는 무결하다. 남는 것은 **설계 취향**이다: 참 구간에서 파라펫 상면을 수평으로 유지할지
(현행 · 한국 계단 난간벽 통상), 아니면 참을 가로질러 레이크를 **연속**시켜 화면에서도 직선으로
읽히게 할지. 후자를 원한다면 `_rake_segments` 의 `land` 항목 상면을 두 인접 사선의 보간선으로
바꾸는 **10줄 안쪽 수정**이고, 계단·참 트랜스폼(위험 기하)은 건드리지 않는다.
`lower_lookup` 은 **미장센 컷**이지 판정 프리셋(h0.3/0.9/1.8 × d2/5/10)이 아니므로,
GT·은닉 판정에는 영향이 없다 — 그래서 본 게이트에서 **추가 렌더는 하지 않았다**(허가된 SMOKE·
프림 검산만으로 규명 완료).

**레드팀 `redteam_w1_assets.md` §4-5 / §8-1 의 조치 요청은 이 문서로 해소된다** —
"봉합 코드에 살아있는 버그" 는 없다. C3 의 관측(화면에 지그재그가 있다)은 유효, C4 의 이력
("14·18 폐기 완료, 19만 잔존")도 유효, 코드 주석도 유효. **셋 다 옳았고 충돌은 없었다.**

### 2.6 재현 명령

```bash
cd scenes/main && NEGOBS_SMOKE=1 python scene14_grandstair_illusion.py   # 계단·레벨 z (파라펫 미포함)
python <스크래치패드>/t2_parapet.py    # ast 로 _rake_segments 추출 → 단조 검사 + 투영 오버레이
```

---

## 3. T3 — GRAZE v2 잔여 WARN 2건 크롭 육안 (CPU만)

### 3.1 대상 페어 확정 `[실측]`

| 지시 | 실제 발화 페어 | gz_spec | 열 일치율 | 에지대역(540) | 낙차행 |
|---|---|---|---|---|---|
| scene13 `h0.3_d5` 15.7 매몰 | **`v6_rt → v7_rt`** | **15.724** (에지 16.465 − 근경 0.741) | 0.968 | 130.6~211.8 | 174.3 |
| scene07 `h0.3_d2` 12.4 노출 | `r1_on → r2_on` ✓ | **12.444** (에지 14.923 − 근경 2.478) | 0.817 | 169.6~312.0 | 248.7 |

참고 — `scene13 r1_on→r2_on` 실행 결과: `d2` FAIL(FRAME+PHOTO, GRAZE 는 **유보**),
`d5` FAIL(PHOTO+DARK+FRAME, GRAZE **유보**), `d10` WARN(DARK). GRAZE 발화 없음.

### 3.2 크롭 산출물

| 페어 | 경로 |
|---|---|
| scene13 `v6_rt→v7_rt` `h0.3_d5` | `look_check/scene13/graze_warn_crop/` — `band_before.png` · `band_after.png` · `band_stack.png`(대역+여유, 2배, 대역/최대변화/낙차행 마커) · `band_diff.png`(부호 히트맵 적=밝아짐/청=어두워짐) · `edge_zoom.png`(x400–1500 y320–400, 4배) · `rowprofile.txt` |
| scene07 `r1_on→r2_on` `h0.3_d2` | `look_check/scene07/graze_warn_crop/` — 동일 6종 (`edge_zoom.png` = x500–1600 y455–535, 4배) |

### 3.3 육안 판정

#### (a) scene13 `v6_rt→v7_rt` `preset_h0.3_d5` — **진성 변화 · 은닉 회귀 아님**

행 프로파일 `[실측]` (전역 톤 정규화 g=1.1279 적용 후, 원본 1080행 기준):

| 행 | 의미 | before | after | Δ |
|---|---|---|---|---|
| 344 | 낙차행 **위**(피트 내부, 5 m 너머) | 23.50 | 25.40 | +1.90 |
| 346 | 〃 | 24.58 | 29.87 | +5.29 |
| **348** | **낙차행**(= `row(5 m, h0.3)`) | **140.47** | **97.67** | **−42.80** |
| 350~370 | 진입 앞마당(5 m 이내) | 136.7~139.6 | 93.1~94.5 | −43 ~ −46 |

- **에지선은 두 라운드 모두 348행에 그대로 있다.** 세로 단차: before `24.6 → 140.5` = **+115.9**,
  after `29.9 → 97.7` = **+67.8**. 즉 **선이 사라진 게 아니라 41 % 약해졌다**.
- 원인은 **낙차 앞쪽 지면의 알베도 교체**다: v6 의 무텍스처 밝은 콘크리트 앞마당(L≈139)이
  v7 에서 **질감 있는 갈색 포장 + 좌우 회색 보도 슬래브**(L≈94)로 바뀌었다
  (`edge_zoom.png` 로 확인). 위험 기하 쪽(피트 내부 암부)은 23.5→25.4 로 **거의 불변**.
- → **은닉이 깊어진 게 아니라 대비의 분모가 바뀐 것.** 지표 발화는 정당(전폭·결맞음 0.968·
  에지 국소 16.5 vs 근경 0.7)하지만, 이 사건은 **회귀가 아니라 사실화 라운드의 의도된 결과**다.

#### (b) scene07 `r1_on→r2_on` `preset_h0.3_d2` — **진성 변화 · 은닉 회귀 아님**

행 프로파일 `[실측]` (g=1.0163):

| 행 | before | after | Δ |
|---|---|---|---|
| 490~492 | 73.9 / 75.0 | 82.2 / 83.8 | +8.3 / +8.8 |
| **494** | **75.30** | **170.21** | **+94.92** |
| **496** | **77.63** | **175.33** | **+97.70** |
| **498** (낙차행) | **187.21** | 176.50 | −10.71 |
| 500~520 | 183.8~187.7 | 175.8~177.2 | −7 ~ −12 |

- **마당(모래) 상단 경계가 498행 → 494행으로 4 px(=540 기준 2행) 올라갔다** = 지면거리로
  2.00 m → 약 2.03 m, **3 cm 상당**. `edge_zoom.png` 로 보면 v1 에 있던 **디딤석 밑 접지 그림자
  띠(4 px)가 v2 에서 사라져** 모래가 디딤석까지 바로 닿는다. 디딤석 자체는 위치·크기 불변이고
  **재질만 따뜻한 회백색 → 녹회색**으로 바뀌었다(관목도 실물 잎으로 교체 — P4 근경 라운드).
- 세로 단차: before `77.6 → 187.2` = **+109.6**(498행), after `83.8 → 170.2` = **+86.4**(494행).
  **선은 두 라운드 모두 존재하고 21 % 약해지며 2행 이동**했다.
- `GRAZE_SLACK = 2`(행 오정합 허용)의 **정확히 경계**다. 대비가 110 계조인 선이 슬랙 한계만큼
  밀리면 잔차가 수십 계조 남아 spec 12.4 가 그대로 나온다.

### 3.4 v2 임계 재조정 근거 (본 절이 T3 의 산출 목적)

두 잔여 WARN 은 **성격이 같다**: *에지 행에 있는 선이 존속하는데, 그 선 양쪽 지면의 알베도가
바뀌었거나 선이 슬랙 한계만큼 밀렸다.* v2 가 재는 `Δcoh` 는 **단차장의 절대 변화량**이라
이 두 경우를 은닉 파괴와 구분할 수단이 없다.

제안 3건 (전부 기존 렌더 재판독으로 임계 재산정 가능 · GPU 불요):

1. **[에지 존속 게이트 — 1순위]** 낙차행 ±슬랙에서 **before / after 각각의 세로 단차 절대값**을
   같이 재고, 둘 다 유의 임계(예: 25 계조) 이상이면 `spec` 초과라도 **정숙(재질 변화)** 으로
   내린다. 본 2건 실측: scene13 `115.9 → 67.8`, scene07 `109.6 → 86.4` — 둘 다 통과 → 발화 0.
   진짜 매몰이면 after 단차가 무너지므로(선이 없어짐) 검출력은 유지된다.
2. **[상대 대비로 전환]** 판정치를 절대 `Δcoh` 대신 **단차비** `step_after / step_before` 로 바꾼다.
   실측 0.585(scene13) · 0.788(scene07). 사실화 라운드의 알베도 교체는 0.5~0.9 대에 몰리고,
   매몰은 0 에 가까워지므로 분리가 선명하다. `graze_recalibration_v1.md` §11-2 의 "방향별 게이트
   분리" 를 이 형태로 구현하면 매몰 방향(§8-7 의 구조적 약점)까지 함께 해결된다.
3. **[`GRAZE_SLACK` 2 → 3]** scene07 은 슬랙 **정확히 경계**(2행)에서 걸렸다. 3 으로 올리면
   본 건은 침묵하고, §6 주입시험의 라이저 0.03 m(≈1행)~0.20 m 검출 대역은 두께가 슬랙보다
   커서 영향이 작다 — 다만 **재조정 전 844컷 주입시험 재실행이 필요**하다(본 임무 범위 밖).

> 두 건 모두 **회귀가 아니었지만 오탐이라 부르기도 부정확하다** — 지표는 "에지 대역에 결맞은
> 변화가 있다" 를 정확히 말했고, 그 변화는 실재했다. 부족한 것은 **그 변화가 은닉을 바꿨는지**를
> 가르는 2차 판별이고, 위 1·2번이 그 자리를 메운다.

### 3.5 재현 명령

```bash
python scripts/regression_check.py --before look_check/scene13/v6_rt --after look_check/scene13/v7_rt --only preset_h0.3
python scripts/regression_check.py --before look_check/scene07/r1_on --after look_check/scene07/r2_on --only preset_h0.3
python <스크래치패드>/make_band_crop.py look_check/scene13/v6_rt/rt_noon_preset_h0.3_d5.png \
       look_check/scene13/v7_rt/rt_noon_preset_h0.3_d5.png 131 212 171 174 \
       look_check/scene13/graze_warn_crop "scene13 v6_rt->v7_rt h0.3_d5"
python <스크래치패드>/make_band_crop.py look_check/scene07/r1_on/pt_noon_preset_h0.3_d2.png \
       look_check/scene07/r2_on/pt_noon_preset_h0.3_d2.png 170 312 245 249 \
       look_check/scene07/graze_warn_crop "scene07 r1_on->r2_on h0.3_d2"
```

---

## 4. 산출물 목록 (전부 `look_check/` = `.gitignore` 대상)

| 경로 | 내용 |
|---|---|
| `look_check/scene02/wininset_base|gate|gate_rep/` | T1 A/B + 잡음바닥 렌더 각 3컷 + manifest |
| `look_check/sceneN3/wininset_base|gate|gate_rep/` | 〃 |
| `look_check/scene02/wininset_crop/win_*.png` | T1 창 영역 3배 확대 4단 비교 |
| `look_check/sceneN3/wininset_crop/win_*.png` | 〃 |
| `look_check/scene14/parapet_crop/lower_lookup_right.png` | T2 v7_pt vs r2_on 우측 파라펫 2배 |
| `look_check/scene14/parapet_crop/overlay_flipp.png` · `overlay_right_zoom.png` | T2 코드 폴리라인 투영 오버레이 |
| `look_check/scene13/graze_warn_crop/` · `look_check/scene07/graze_warn_crop/` | T3 에지 대역 크롭 6종 ×2 |

**본 임무가 쓴 파일은 위 `look_check/**` 과 이 문서뿐이다 — 저장소 추적 파일 수정 0건 · 커밋 0건.**
`scene_common.py`(mtime 16:46:34)는 임무 착수(16:49) 전과 동일한 미커밋 상태 그대로다.

> ⚠️ **동시 세션 경고** — 종료 시 `git status` 에 `Docs/STATUS.md` ·
> `Docs/briefs/ground_kit_spec_v1.md` · `Docs/briefs/t1_material_layer_spec_v1.md` **3건이 추가로
> `M` 으로 잡힌다.** 착수 시점(16:49) `git status` 에는 `scene_common.py` 1건뿐이었고, 세 파일의
> mtime 은 17:11:16 / 17:14:33 / 17:11:19 로 **본 임무 산출 시각과 겹친다** `[실측]`.
> 같은 저장소에서 **다른 Claude Code 세션 2개가 동시 실행 중**이다(PID 713081 · 910911).
> 본 임무는 그 세 파일을 열지도 쓰지도 않았다 — 커밋 시 **작성 주체를 확인하고 분리**할 것.

---

## 5. 다음 수순 (감독 결재 대기)

1. **`scene_common.py` 커밋** — T1 PASS 로 창 리세스가 해제됐고 `VEG_DEBRIS` 행은 렌더 무영향이라
   **분리 커밋 불필요**. `fix_small_w1.md` §5 표의 ⛔ 를 ✅ 로 갱신 필요.
2. **`fix_small_w1.md` §2.6 이월 4건**(scene01 자체 경로 · scene15/21/C1 자체 창 · 출입문 돌출
   50 mm · 잔여 리세스 0.135 m)은 이 게이트가 **덮지 않았다**. T2 `building_kit` 스팬드럴 분해 몫.
3. **scene14 파라펫**: 코드 무결 확정. 참 구간 레이크 연속화는 **취향 결재** 항목(§2.5).
   `redteam_w1_assets.md` §8-1 요청은 해소 — 레드팀에 회신 필요.
4. **GRAZE v2 임계 재조정**: §3.4 의 1·2번을 `regression_check.py` 에 반영 후, 대조군 260컷 +
   주입 844컷 **재실행으로 임계 재산정**(CPU · GPU 불요).
5. **sceneN3 벚나무**(§1.7) 규약 위반 여부 판정 + 33씬 전수 계절 요소 점검.
