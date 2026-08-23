# capture_plan.md — d 준비 (WEEKEND_BRIEF_0823 §6.7-d)

CPU-5가 준비만 한다. **여기 있는 명령은 하나도 실행하지 않았다** — GPU-6 창에서 orchestrator가 돈다.
씬·카메라 사양은 `worlds/README.md`, 환경 근거는 `ISOLATION.md`, baseline 조사는 `STAGE_A_INVENTORY.md`.

---

## 0. 한 눈에

```
[셸 A: neg_env]  gzserver+gzclient (우리 .world)  ──►  /gzcam/*/…/image_raw
[셸 B: neg_env]  tools/grab_frames.py             ──►  frames/<tag>/*.png + manifest.json
[셸 C: env_seg]  infer_photo.py --fit squash      ──►  out/*.png 오버레이 + *.json 확률
```
총 프레임 **216장** (**8월드** × 9뷰 × 3프레임). 1920×1080 PNG 기준 ≈ 500 MB.
월드 8개 = 하자드 4 + 트윈 대조군 4, 티어 커버리지 **V(drop1·drop2) / E(drop4) / H(drop3)**.

> 시간이 빠듯하면 **`-n 1`(뷰당 1프레임, 72장)** 으로 줄여도 정성 패널에는 충분하다.
> 더 줄여야 하면 월드 우선순위는 **drop3 → drop4 → drop1 → drop2** (새 티어가 먼저).

---

## 1. 셸 A — 시뮬 기동

```bash
source /home/vislab/Desktop/work_sy/Baseline_NegObs/setup_env.sh
GZW=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/gazebo/worlds

# 권장(로봇 포함, Nav2 없음).  world_name 은 확장자 없는 절대경로.
ros2 launch bumperbot_description gazebo.launch.py world_name:=$GZW/gz_drop1

# 또는 최소(로봇조차 없음).  이쪽은 world 인자이고 '.world' 를 붙인다.
#   ros2 launch gazebo_ros gazebo.launch.py world:=$GZW/gz_drop1.world
#   gui:=false 를 붙이면 gzclient 없이 서버만 (GPU 절약, DISPLAY 는 그대로 필요)
```

`setup_env.sh` 없이 띄우지 말 것 — `/usr/share/gazebo/setup.sh`가 빠지면 gzserver가
렌더 초기화 중 `Assertion px != 0`으로 죽는다(RUN_GUIDE.md 기록).

기동 확인:
```bash
ros2 topic list | grep gzcam        # 9개 네임스페이스가 보여야 한다
# 아무것도 안 보이면:  ros2 daemon stop   (데몬이 옛 환경의 토픽 목록을 캐싱한다)
```

## 2. 셸 B — 캡처

```bash
source /home/vislab/Desktop/work_sy/Baseline_NegObs/setup_env.sh
cd /home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/gazebo

python3 tools/grab_frames.py --list                       # 살아있는 Image 토픽 먼저 확인
python3 tools/grab_frames.py --tag gz_drop1_on  --outdir frames/gz_drop1_on  -n 3
```

- `-n 3` — **뷰당 3프레임**. 정지 씬이라 프레임 간 차이는 카메라 노이즈뿐이고, 3장은
  "렌더가 안정됐는지" 확인용 여유분이다. 정성 패널에는 `_000`만 쓰면 된다.
- `--settle 3` (기본) — 구독 직후 3초는 버린다. lazy 센서가 깨어난 직후 첫 프레임이
  반쯤 합성된 버퍼일 수 있다. 카메라가 **1 Hz**이므로 3프레임 확보에 ≈ 6초.
- 일부 뷰만: `--views preset_h0.3_d2,preset_h0.9_d5`
- 종료 코드: 0 = 저장됨 / 2 = 토픽 없음 / 3 = 타임아웃까지 한 장도 못 받음.

**8개 월드를 도는 루프** (셸 A를 매번 내렸다 올린다 — 월드 교체는 재기동뿐):

```bash
for W in gz_drop3 gz_drop3_ctrl gz_drop4 gz_drop4_ctrl \
         gz_drop1 gz_drop1_ctrl gz_drop2 gz_drop2_ctrl; do
  # 셸 A: ros2 launch bumperbot_description gazebo.launch.py world_name:=$GZW/$W
  # (뜬 뒤 ~15 s 대기)
  python3 tools/grab_frames.py --tag ${W}_cap --outdir frames/$W -n 3
  # 셸 A: Ctrl-C
done
```
순서는 **새 티어(H·E) 먼저**다 — 창이 잘려도 V는 이미 D31에서 설계가 검증돼 있다.

tmux 한 방으로 돌리고 싶으면 창 2개(`sim`/`cap`)로 위 순서를 그대로 옮기면 된다.
`start_baseline.sh`는 쓰지 말 것 — Nav2·YOLO까지 띄운다.

### 파일명 규약

```
frames/<world>/<tag>_<view>_<idx>.png
  예:  frames/gz_drop1/gz_drop1_cap_preset_h0.3_d2_000.png
       frames/gz_drop1/gz_drop1_cap_extra_h0.3_d1.2_000.png
       frames/gz_drop2/gz_drop2_cap_rs_h0.125_d2_000.png
frames/<world>/<tag>_manifest.json     ← 뷰별 eye/pitch/hfov/res + infer_photo 인자 그대로
```
`view` 토큰은 코퍼스 이름(`preset_h0.3_d2` …)을 그대로 쓴다. `regression_check.is_graze_view()`가
`"h0.3" in v`로 grazing 컷을 고르므로 **문자열 `h0.3`을 유지하는 게 load-bearing**이다.

## 3. 셸 C — infer_photo 제로샷 경로

```bash
export PYTHONNOUSERSITE=1
conda activate env_seg
cd /home/vislab/Desktop/work_sy/Practice_NegObs/experiments/mainrun_0819/code

GZ=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/gazebo
CK=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2

CUDA_VISIBLE_DEVICES="" python3 infer_photo.py \
  --image $GZ/frames/gz_drop1/gz_drop1_cap_preset_h0.3_d2_000.png \
  --ckpt  $CK/rgb_s42/best.pt \
  --grid  labeling/gridspec_v1.json \
  --out   $GZ/out/rgb_s42__gz_drop1__preset_h0.3_d2.png \
  --json  $GZ/out/rgb_s42__gz_drop1__preset_h0.3_d2.json \
  --height 0.3 --pitch -10 --hfov 60 --fit squash --tau 0.5
```

### 반드시 지킬 4가지

1. **`--grid labeling/gridspec_v1.json`** — `gridspec.add_grid_arg`의 기본값은 **V0(15칸)**이다.
   frozen v2 체크포인트는 전부 `n_cells=20 / PROVISIONAL-GRID-V1`(실측 확인함).
   빼먹으면 셀 수가 안 맞아 터지거나, 더 나쁘게는 조용히 엉뚱한 셀에 매핑된다.
2. **`--fit squash`** — 훈련은 `polar_dataset.py`가 1920×1080을 512×512로 **squash**한다
   (종횡비 미보존). 우리 프레임도 16:9(1920×1080, rs는 1280×720)라 squash가
   **훈련 기하를 정확히 재현**한다. `infer_photo`의 기본값 letterbox는 폰 사진용이니 쓰지 말 것.
   letterbox는 회색(128,128,128) 패드를 넣는데, 우리 씬은 회색 콘크리트라 패드가 지면처럼 보인다.
3. **`--height / --pitch / --hfov`는 가정이 아니라 실측이다.** 정지 카메라 모델이라
   포즈가 SDF에 박혀 있다. manifest.json의 `infer_photo_args`를 그대로 복사해 쓰면 된다.
   `--pitch`는 infer_photo 규약상 **음수 = 아래보기**(SDF는 +pitch = 아래보기, 부호가 반대다).
   | view | `--height` | `--pitch` | `--hfov` |
   |---|---|---|---|
   | `extra_h0.3_d1.2`, `preset_h0.3_d*` | `0.3` | `-10` | `60` |
   | `preset_h0.9_d*` | `0.9` | `-10` | `60` |
   | `rs_h0.125_d*` | `0.125` | `-15` | `69` |
4. **EXIF 없음** — Gazebo PNG에는 EXIF가 없으니 `--hfov auto`는 69°(폰 기본값)로 떨어진다.
   위 표대로 **명시**할 것. 워터마크에 `(cli)`로 찍히면 제대로 먹은 것이다.

### 모델 3종 중 무엇이 이 경로로 되는가

| frozen 모델 | cfg `input` | infer_photo로 되는가 |
|---|---|---|
| `v2/rgb_s42/best.pt` | rgb | **된다** |
| `v2/b2_s42/best.pt` | rgb | **된다** (RGB 입력 모델) |
| `v2/depth_s42/best.pt` | depth | **안 된다** — infer_photo는 RGB 전용 |

Depth 팔까지 하려면 두 가지가 더 필요하다(이번 창 범위 밖, 결정 필요):
(a) 월드를 `python3 make_worlds.py --depth`로 재생성 → negobs 카메라가 depth 센서가 되어
    RGB와 32FC1 metric depth를 한 플러그인에서 같이 낸다. `grab_frames.py`가
    `*_depth.npy`(float32 **미터**)로 저장한다 — `polar_dataset.load_depth_m()`이 .npy를
    미터로 그대로 읽으므로 단위 변환 불필요.
(b) depth용 `infer_photo` 등가 도구(현재 없음).

## 4. 무엇을 보면 "전이 신호 있음"인가 — 결과 보기 전에 못박는 판독 기준

§6.8의 사전등록 규약을 이 트랙에도 적용한다. **아래는 캡처 전에 쓴 것이다.**

- **1차(정성)**: hazard 팔에서 확률 상위 셀이 **lip이 실제로 떨어지는 밴드**에 몰리는가.
  기대 밴드는 뷰가 정한다 — d1.2 → 밴드 1, d2 → 밴드 2, d5 → 밴드 3, d10 → 밴드 4
  (`worlds/README.md` §2 표). 엉뚱한 밴드에서 튀면 전이 아님.
- **2차(트윈 Δ)**: 같은 뷰에서 `hazard − ctrl`의 `delta_frame`(전 셀 max p 차) > 0.
  `ctrl`은 난간·경고블록이 **그대로 남은** FA 프로브다. Δ ≈ 0이면서 양쪽 다 높으면
  → 모델이 기하가 아니라 **단서만** 보고 있다는 증거(이게 오히려 본 연구의 논지에 직접 걸린다).
- **3차(비대칭)**: `gz_drop2`는 난간이 `+Y`(화면 오른쪽)에만 있고 카메라 정면은 무방비다.
  섹터 A~E 확률이 오른쪽으로 쏠리면 단서 의존, 중앙~왼쪽에 서면 기하 의존.
- **4차(티어 사다리) — D37로 새로 가능해진 판독**: 같은 카메라·같은 좌표계에서 티어만
  바뀐다. 기대 순서는 `p(drop2) ≳ p(drop1) > p(drop4) > p(drop3)`. 이 순서가 무너지는
  지점이 곧 모델이 **기하를 잃고 단서로 넘어가는 지점**이다.
  - `gz_drop4`의 **E 프리셋 2개(`preset_h0.3_d10`, `preset_h0.9_d10`)** 가 핵심 컷이다.
    나머지 5개는 V이므로 tier 비교에 쓰지 말 것.
  - `gz_drop3`은 **전 프리셋 H**다. 여기서 발화하면 그건 순수 단서 응답이다.
- **부정 결과도 착지다.** 전 셀 p < 0.5로 침묵해도 "Isaac→Gazebo 도메인 갭이 이 정도"라는
  수치로 남긴다. 침묵을 실패로 적지 말 것.

### gz_drop3 전용 사전 검사 — 가림 누수 확인 (무료 QA)

`gz_drop3`은 위험 기하의 기여 픽셀이 0이고, **Gazebo는 결정적 렌더러라 기하가 같은 프레임은 바이트
동일하게 나온다** — 이 두 팔에서 `identical`을 기대하는 근거는 그것뿐이다.
**"기여 픽셀 0"이 "두 프레임이 같다"를 함의하지는 않는다**(F7/RT.6 — Isaac 코퍼스의 strict-H 96쌍은
**전부** 다르고, 중앙값 쌍이 화면의 4.5 %에서 ≥32/255로 갈린다). 위험을 지우는 조작은 그림자·간접광·
같은 브랜치에서 함께 지워지는 구조물 같은 **간접 신호**를 통해 프레임을 바꿀 수 있다. 따라서 아래
검사는 **위험 표면이 직접 새는 가림 누수**를 잡는 도구이지 "두 팔이 광학적으로 동일함"의 증명이 아니며,
`DIFFERS`는 곧바로 누수 판정이 아니라 **직접 누수인지 간접 신호인지 눈으로 확인하라**는 신호다.
추론 전에 먼저 돌릴 것:

```bash
cd /home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/gazebo
for V in extra_h0.3_d1.2 preset_h0.3_d2 preset_h0.3_d5 preset_h0.3_d10 \
         preset_h0.9_d2 preset_h0.9_d5 preset_h0.9_d10; do
  A=frames/gz_drop3/gz_drop3_cap_${V}_000.png
  B=frames/gz_drop3_ctrl/gz_drop3_ctrl_cap_${V}_000.png
  printf "%-20s " "$V"
  cmp -s "$A" "$B" && echo "identical (가림 정상)" || echo "DIFFERS -> 가림 누수 의심"
done
```
- **identical** → 설계대로. 이 쌍의 Δ는 구성상 0이며, 측정하는 것은 *판별력*이 아니라
  **단서만으로 얼마나 발화하는가**다 (08-05 "가드 = 낙차 단서" 교리의 직접 시험).
- **DIFFERS** → 어딘가 위험 기하가 새고 있다. 티어 라벨을 H로 쓰면 안 된다.
  `worlds/README.md` §8.2의 여유 표에서 어느 프리셋이 빡빡한지 보고(최빡빡은
  `preset_h0.9_d2`, 여유 +0.175 m ≈ 60 px) `make_worlds.py --d3-occ`로 벽을 올린다.
  (렌더러 비결정성으로 인한 미세 차이일 수도 있으니, 다른 뷰도 같이 DIFFERS인지 볼 것.)

**주의(과대해석 금지)**: 티어 커버리지는 **V 14컷 / E 2컷 / H 7컷**(negobs 기준)으로
고르지 않다. E는 `d = 10`에서만 성립하고 `d ≤ 2`에서는 어떤 실물 낙차로도 불가능하다
(`worlds/README.md` §8.5의 최대 개구 면적 표 — d2에서는 개구가 1~3 cm여야 한다).
따라서 **E에 대한 결론은 원거리 한정**으로 쓰고, 표본 2컷에 통계를 붙이지 말 것.

## 5. GPU-6 창에서 그대로 붙여 쓸 명령 목록

```bash
# ── 0) 사전 (CPU, 1초)
cd /home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/gazebo
for f in worlds/*.world; do gz sdf -k "$f"; done          # 8/8 "Check complete" 기대

# ── 1) 셸 A: 시뮬  (W 를 바꿔가며 8번. 새 티어부터: drop3 → drop4 → drop1 → drop2)
source /home/vislab/Desktop/work_sy/Baseline_NegObs/setup_env.sh
GZW=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/gazebo/worlds
ros2 launch bumperbot_description gazebo.launch.py world_name:=$GZW/gz_drop3

# ── 2) 셸 B: 캡처 (셸 A가 뜬 뒤 ~15 s)
source /home/vislab/Desktop/work_sy/Baseline_NegObs/setup_env.sh
cd /home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/gazebo
python3 tools/grab_frames.py --list
python3 tools/grab_frames.py --tag gz_drop3_cap --outdir frames/gz_drop3 -n 3
#   … 셸 A 를 Ctrl-C 하고 world_name 만 바꿔 8개 월드 반복:
#      gz_drop3 gz_drop3_ctrl gz_drop4 gz_drop4_ctrl gz_drop1 gz_drop1_ctrl gz_drop2 gz_drop2_ctrl

# ── 2b) gz_drop3 가림 누수 검사 (§4 참조) — 추론 전에 반드시
for V in preset_h0.3_d2 preset_h0.3_d10 preset_h0.9_d2 preset_h0.9_d10; do
  printf "%-20s " "$V"
  cmp -s frames/gz_drop3/gz_drop3_cap_${V}_000.png \
         frames/gz_drop3_ctrl/gz_drop3_ctrl_cap_${V}_000.png \
    && echo "identical (정상)" || echo "DIFFERS -> 가림 누수 의심"
done

# ── 3) 셸 C: 추론
export PYTHONNOUSERSITE=1; conda activate env_seg
cd /home/vislab/Desktop/work_sy/Practice_NegObs/experiments/mainrun_0819/code
GZ=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/gazebo
CK=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2
mkdir -p $GZ/out
for W in gz_drop3 gz_drop3_ctrl gz_drop4 gz_drop4_ctrl \
         gz_drop1 gz_drop1_ctrl gz_drop2 gz_drop2_ctrl; do
  for V in extra_h0.3_d1.2 preset_h0.3_d2 preset_h0.3_d5 preset_h0.3_d10 \
           preset_h0.9_d2 preset_h0.9_d5 preset_h0.9_d10; do
    case $V in *h0.9*) H=0.9;; *) H=0.3;; esac
    IMG=$GZ/frames/$W/${W}_cap_${V}_000.png
    [ -f "$IMG" ] || { echo "skip $IMG"; continue; }
    for M in rgb_s42 b2_s42; do
      CUDA_VISIBLE_DEVICES="" python3 infer_photo.py \
        --image "$IMG" --ckpt $CK/$M/best.pt --grid labeling/gridspec_v1.json \
        --out  $GZ/out/${M}__${W}__${V}.png \
        --json $GZ/out/${M}__${W}__${V}.json \
        --height $H --pitch -10 --hfov 60 --fit squash --tau 0.5
    done
  done
done
```

## 6. 리스크

| 리스크 | 징후 | 대응 |
|---|---|---|
| `gzcam` 토픽 leaf 이름이 예상과 다름 | `--list`에 `/gzcam/...`이 안 뜸 | 스크립트는 **네임스페이스로만** 매칭한다. 그래도 비면 `ros2 daemon stop` 후 재시도 |
| `ROS_LOCALHOST_ONLY=1`인데 셸마다 다르게 설정됨 | 셸 B가 셸 A 토픽을 못 봄 | 두 셸 모두 `setup_env.sh`로 통일 |
| 카메라 9대 렌더가 세그 캠페인 GPU와 충돌 | 훈련 속도 저하 | `update_rate` 이미 1 Hz. 더 필요하면 `make_worlds.py --cams …` 재생성, `flock` 규약 준수 |
| `--grid` 누락 | 셀 수 불일치 / 조용한 오매핑 | 위 루프에 이미 박아 뒀다 |
| `--fit letterbox`(기본값) 사용 | 회색 패드가 콘크리트 지면으로 오인됨 | 항상 `--fit squash` |
| 로봇이 프레임에 등장 | 정성 패널 오염 | 씬을 +12 m 밀어 스폰(0,0)을 최원거리 카메라(x=2.0) **뒤**에 뒀다. (B) 명령을 쓰면 로봇 자체가 없다 |
| `gz_drop3` 가림이 샘 (H 라벨 오염) | hazard/ctrl 프레임이 다름 | §4의 `cmp` 검사를 **추론 전에** 실행. 새면 `make_worlds.py --d3-occ 0.70` 로 재생성 |
| `gz_drop4`의 E가 표본 2컷뿐 | 통계 과신 | E 결론은 `d = 10` 한정으로 서술. 더 필요하면 `--d4-lat 0.45` 로 `preset_h0.3_d5`까지 확보 |
| 월드가 8개로 늘어 창을 넘김 | 캡처 미완 | `-n 1`(72장)로 축소, 월드 우선순위 drop3 → drop4 → drop1 → drop2 |
| `simulated_robot.launch.py` 사용 시 AMCL/map 경고 폭주 | 로그 소음 | 캡처엔 `bumperbot_description gazebo.launch.py` 또는 `gazebo_ros gazebo.launch.py`를 쓴다 |
