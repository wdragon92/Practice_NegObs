# 내가 직접 해 보기 — Isaac Sim 렌더 · 격자 오버레이 · 갤러리 · GUI

최종 갱신 2026-08-27 · **아래 명령을 전부 실제로 돌려서 확인했다**(경로·출력은 진짜) · 대장 D103

소유자 질문(08-24) "**내가 직접 IsaacSim에서 시뮬레이션 해보려면?**" 에 대한 답. 용어: **컷** = 사진 1장 ·
**라운드** = 렌더 실행 한 번의 묶음(=폴더 이름) · **씬** = 3D 장면 33개 중 하나.

## 0. 공통 준비 (매번 이 5줄로 시작)

```bash
cd /home/vislab/Desktop/work_sy/Practice_NegObs
unset PYTHONPATH VIRTUAL_ENV                       # 다른 파이썬이 섞이면 Isaac이 안 뜬다
source ~/miniconda3/etc/profile.d/conda.sh && conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1       # 이 저장소에서는 필수
source scripts/lib/negobs_paths.sh                 # negobs_round: 라운드를 이름으로 찾아 준다
```

GPU는 한 번에 하나만 써야 해서 GPU 명령은 늘 `flock`(락 = 순서표)으로 감싼다(`-w 3600` 최대 1시간 대기 ·
`-E 201` 락이 잡혀 있으면 종료코드 201).

## 1. 씬 하나를 직접 렌더하기

```bash
python3 scripts/run_data_render.py --plan --run 260827_handson \
      --scenes scene01 --conds L0 --cams 2 --seed 20260827      # ① 예상만 (GPU 안 씀)

flock -o -w 3600 -E 201 /tmp/negobs_gpu.lock nice -n 5 \
  python3 scripts/run_data_render.py --run 260827_handson \
      --scenes scene01 --conds L0 --cams 2 --seed 20260827      # ② 진짜 렌더
```

`--run` 라운드 이름(**오늘 날짜 6자리 + 용도**, 미래 날짜 금지 = D96) · `--scenes` 씬(쉼표로 여럿) ·
`--conds` 조명(`L0` = 기준 정오) · `--cams` 컷 수. 실측(08-27, 위 명령 그대로): **2컷 25초**(부팅 포함,
컷당 12.3초). **직접 할 때는 `--run` 을 오늘 날짜로 바꿀 것** — 이미 있는 이름을 다시 쓰면 이어찍기로
보고 `[skip] scene01 — all 1 conditions already done` 만 찍고 끝난다. 결과:

```
dataset/misc/260827_handson/manifest.json                        ← 라운드 기록 (렌더 직후엔 dataset/260827_handson 에 생기고, 정리 후 misc/ 로 옮겼다)
dataset/misc/260827_handson/val/scene01/L0__s20260827__0000.png  ← 1920x1080, 0001 도 같이
dataset/misc/260827_handson/val/scene01/variation.json           ← 그 컷의 카메라 값
```

**빨간 에러가 지나가도 놀라지 말 것.** 끝에 `UnboundLocalError: local variable 'math'` 가 뜨는데
**이미 알려진 무해한 결함**이다(`scripts/run_data_render.py:603`, 바로 위 594행 주석이 설명 — 산출물이
전부 디스크에 쓰인 뒤에 터진다). 정상 신호는 종료코드 0 과 `manifest.json` 의 `"exit": 0, "cuts": 2`.

**라운드 정리(파일링).** 갓 찍은 라운드는 `dataset/` 바로 밑에 평평하게 놓이고, 정리할 때만 목적 폴더로
한 칸 들어간다. 이 실습본은 `dataset/misc/260827_handson` 으로 옮겼다. 옮길 때 같이 손보는 3곳:
`dataset/ROUNDS.json` 에 `"260827_handson": "misc"` · `Docs/reorg_0827/dataset_moves.tsv` 한 행 ·
`dataset/README.md` 의 `misc/` 줄. 그 뒤로는 **위치를 외울 필요가 없다**:

```bash
negobs_round 260827_handson                                          # 셸
python3 -c "import variation_kit as vk; print(vk.round_dir('260827_handson'))"   # 파이썬
```

## 2. 20칸 폴라 격자를 그 사진 위에 얹기

```bash
python3 experiments/v3_0823/code/view_overlay.py \
    "$(negobs_round 260827_handson)/val/scene01/L0__s20260827__0000.png"
```

실측 출력 그대로:
```
[view_overlay] L0__s20260827__0000.png · 칸 20 그림
[view_overlay] cam d=1.90 m · h_rel=1.10 m · yaw=3.34° · pitch=-5.87° · hfov=62.48° · ground_z=-0.000
[view_overlay] → dataset/misc/260827_handson/val/scene01/L0__s20260827__0000_grid.png
```

옆 `variation.json` 에서 카메라를 읽어, 라벨을 만든 그 코드(`labeler.py`)로 지면에 쐐기를 그린다.
칸 이름 = **섹터 A~E**(화면 왼→오) + **밴드 1**(0–2 m) **2**(2–5 m) **3a**(5–8 m) **3b**(8–12 m).
`--cells B3b,C3a` 칸 강조 · `--gt <라벨 manifest.json>` 정답 칸 강조 · `-o` 출력 경로. GPU/락 불필요.

## 3. 검수 갤러리 열기

갤러리 = 라운드 하나에서 **씬당 4컷**(근경·중경·원경·전경)만 600 px JPEG로 줄여 모은 폴더.

```bash
ls look_check/_review/                              # w2 / w3 / w4 (작업 물결)
eog look_check/_review/w4/260816_w4_final33/ &      # 이미지 뷰어로 통째로
```

폴더마다 `meta.json` 에 씬 이름·판정(`WARN`/`FAIL`)·대체한 뷰가 적혀 있다. **아직 검수 안 된 갤러리 4개**(08-16 자율주행 산출물, 소유자 확인 대기): `w4/` 아래
`260814_w4_r1r2pilot` · `260815_w4_r4batch` · `260815_w4_hzbatch` · `260816_w4_final33`.
새로 만들려면 `python3 scripts/make_review_gallery.py --round <라운드> --out look_check/_review/w4`.

## 4. Isaac Sim **GUI**로 씬을 열어 직접 돌아다니기 — 된다 (08-27 확인)

```bash
export DISPLAY=:1                    # 이 PC 본체 화면
flock -o -w 3600 -E 201 /tmp/negobs_gpu.lock \
  python scenes/main/scene01_campus_stairs.py
```

환경변수 `NEGOBS_CAPTURE` 를 **주지 않으면** GUI 모드다(`scenes/main/scene01_campus_stairs.py:1602`
의 `headless=capture_mode`). 주면 창 없이 자동 촬영 모드. 08-27에 실제로 띄워 확인: 약 10초 만에
창 제목 **`Isaac Sim Python 4.5.0`** 이 뜨고 씬이 다 올라온다(창 존재를 `wmctrl -l` 로 확인, 종료 뒤
GPU 메모리 원복 확인). 창이 뜨면 터미널에 조작법이 같이 찍힌다(실제 출력):

```
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
※ 키가 안 먹으면 Isaac Sim 창을 한 번 클릭해서 포커스를 줘!
```

씬마다 **무엇을 봐야 하는지 체크리스트 7줄**도 함께 나온다. 다른 씬도 같은 방법
(`ls scenes/main/*.py` 로 목록). 끝낼 때는 창을 닫으면 되고, 락은 프로세스가 끝나면 자동으로 풀린다.
GUI도 **GPU를 잡으니** 학습·렌더가 도는 중이면 `flock` 이 기다리게 두거나 끝난 뒤에 열 것.

## 5. 자주 겪는 것

| 증상 | 원인 · 대처 |
|---|---|
| 종료코드 **201** | GPU 락을 남이 쓰는 중 — 기다렸다 다시. |
| `ModuleNotFoundError: isaacsim` · 엉뚱한 패키지 | 0절 5줄 누락(특히 `conda activate env_isaaclab`, `PYTHONNOUSERSITE=1`). |
| 라운드 폴더를 못 찾겠다 | 외우지 말고 `negobs_round <이름>` / `vk.round_dir("<이름>")`. |
| GUI 창은 떴는데 키가 안 먹음 | 창을 한 번 클릭해 포커스를 줄 것. |

같이 볼 것: `dataset/README.md`(라운드 지도) · `Docs/campaign/status/PROJECT_STATE.md`(현재 상황) ·
`experiments/README.md`(실험 사이클 지도) · `Docs/briefs/process_spec_v1.md`(렌더 규약).
