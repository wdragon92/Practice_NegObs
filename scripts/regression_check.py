#!/usr/bin/env python3
"""렌더 라운드 회귀 자동 검사기 — 이미지 + manifest.json 만으로 동작.

`Docs/briefs/multi_scene_brief_v3.md` §A 회귀 방지 체크리스트 중
**렌더 산출물만으로 판정 가능한 항목**을 자동화한다. GPU·Isaac 불요.

동기 (프로젝트 교훈, `Docs/audit_v4/fixlog_W7.md` §0):
  "신설 기하가 프리셋 카메라를 삼키는 회귀가 4회 재발했다
   (scene19 d5 암흑 · scene17 성토 매몰 · scene05 화단 매몰 · scene19 skyline 접선 차폐).
   눈으로 한 차폐 검산은 차폐 주체 자체를 오진한다."
  "프레이밍 검산은 앵커 **개수**가 아니라 **픽셀 점유율**로 걸 것"
   (`Docs/audit_v4/judge_v8_rt.md` §376)

검사 6종
  [DARK]  암흑 프레임        — 평균 휘도·암부 비율 (카메라가 기하에 삼켜짐의 주 증상)
  [BLOWN] 과노출·255 클리핑
  [WHITE] 순백 대면적        — v5.1 §4 금지 규약 (절대치는 참고, 증가분이 판정)
  [OCCL]  카메라 차폐 회귀   — 이전 라운드 대비 **신규 암부**와 그 최대 연결 덩어리
  [FRAME] 프레임 점유율 급변 — 전역 톤 정규화 후 16×9 블록 점유율 이동
  [GRAZE] grazing 은닉 의심  — h0.3 로봇 시점(판정 1순위) 지면대 구조량 변화

사용법
  # 단일 씬 A/B
  python scripts/regression_check.py --before look_check/scene07/p2g2_off \
                                     --after  look_check/scene07/p2g2_on

  # 전 33씬 (라운드 이름은 쉼표 폴백 — 먼저 존재하는 것을 씀)
  python scripts/regression_check.py --scenes 'look_check/scene*' \
      --before-round final_pt_r2,final_pt,ctx2_pt,ctx2 --after-round v9_look \
      --json Docs/reports/regr_v9.json

  # 씬별로 라운드가 제각각이면 목록 파일 (씬경로 TAB 이전 TAB 이후, # 주석)
  python scripts/regression_check.py --list rounds.tsv

의존성: numpy + PIL 뿐 (scipy·opencv 금지 — 배포 환경 가정).
같은 계열 도구: `scripts/imgstats.py` (사실성 저수준 통계). 본 도구는 **회귀** 전용이다.
"""
import argparse
import glob
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from PIL import Image

# ===========================================================================
# 임계값 — 전부 여기 모아 둔다. 각 값의 근거를 주석으로 남긴다.
#
# 근거의 출처는 3가지다.
#   (a) 감독 판정문의 실측 대역 — `Docs/audit_v4/judge_v7_rt_A.md`,
#       `judge_v8_rt.md` 는 프리셋 9컷을 "mean / dark<25 / 255 클리핑" 으로
#       전수 측광했다. 본 도구는 **같은 정의**를 쓴다(호환).
#   (b) 대조군 실측 — 룩 레이어 A/B 페어 4쌍(scene07/sceneD3 p2g1·p2g2 off↔on,
#       총 56컷) + 소폭 수정 라운드(sceneD3 r2→r3) + 렌더 모드 교체
#       (scene07 v8_rt→v8_pt). **회귀가 없어야 정상인 페어들**의 잡음 상한.
#   (c) 실회귀 실측 — scene07 v6→v7, v7→v8 (판정문이 실제 차폐·암흑으로
#       지적한 컷들)의 값.
# 임계는 (b)의 상한과 (c)의 하한 사이에 둔다.
# ===========================================================================

# --- [DARK] 절대 암흑 -------------------------------------------------------
# judge_v7_rt_A §128: mean 26.3 · dark 81.3 % 를 "사실상 판정 불능" 으로 판정.
# judge_v8_rt §78 : 합격 그리드는 mean 127~185 · dark 1.8~10.4 %.
# judge_v8_rt §240: mean 49.4 · dark 53.4 % 를 "여전히 씬 최암부" 로 잔여 지적.
DARK_MEAN_FAIL = 30.0
DARK_MEAN_WARN = 55.0
DARK_PCT_FAIL = 70.0
DARK_PCT_WARN = 45.0
DARK_LEVEL = 25          # 암부 정의 — 감독 측광과 동일 (0~255 휘도 < 25)

# --- [BLOWN] 과노출 ---------------------------------------------------------
# 합격 33씬 최종 라운드 412컷 전수 실측(본 도구): mean p95 = 188, max = 238.3
# (scene14 h0.3_d10 — 실제로 정보가 죽은 백판 프레임). 255 클리핑은 max 0.35 %
# 로 사실상 전무하므로 클리핑 임계는 낮게 잡아도 과탐지가 없다.
BLOWN_MEAN_FAIL = 235.0
BLOWN_MEAN_WARN = 210.0
CLIP_PCT_FAIL = 1.0
CLIP_PCT_WARN = 0.2
CLIP_LEVEL = 254         # 채널 최대값이 254 이상 = 255 클리핑

# --- [WHITE] 순백 대면적 (v5.1 §4 "순백(>0.8) 대면적 금지") -----------------
# 픽셀값 > 0.8 은 **알베도 > 0.8 과 같지 않다**(정오광+ACES 톤매핑에서
# 알베도 0.5 콘크리트도 쉽게 넘는다). 합격 33씬 중 12씬이 절대치로 걸린다.
# → 절대치는 참고(WARN)로만 쓰고, **판정은 이전 라운드 대비 증가분**으로 한다.
WHITE_LEVEL = 204        # = 0.8 × 255, 채널 최소값 기준(= 무채색 순백)
WHITE_PCT_WARN = 60.0    # 하단 2/3 기준. 33씬 중앙값 0.97 %, p95 88.6 % (이봉분포)
WHITE_DELTA_FAIL = 25.0  # 증가 pp. 대조군 A/B 최대 증가 +2.4 pp
WHITE_DELTA_WARN = 10.0

# --- [OCCL] 카메라 차폐 회귀 ------------------------------------------------
# newdark = (이전 휘도 >= 60) & (신규 휘도 < 25) 인 픽셀 비율.
#   대조군 56컷 최대 0.67 % / 소폭 수정 0.26 % / 모드 교체 0.00 %
#   실회귀     : 8.2 · 14.0 · 14.5 · 17.3 · 23.0 · 26.5 · 39.3 · 47.7 %
OCCL_NEWDARK_FAIL = 8.0
OCCL_NEWDARK_WARN = 2.0
# 최대 **연결** 신규암부(대면적 판정). 대조군 최대 0.05 %, 실회귀 2.3~41.6 %.
OCCL_BLOB_FAIL = 5.0
OCCL_BLOB_WARN = 1.5
OCCL_BRIGHT_BEFORE = 60  # "원래 밝았다" 의 하한
NEAR_BAND = 0.60         # 프레임 하단 40 % = 근거리대(카메라를 삼키는 기하가 앉는 곳)

# --- [FRAME] 프레임 점유율 급변 --------------------------------------------
# 전역 톤(밝기·대비·하늘 교체·RT↔PT)을 백분위 매칭으로 제거한 뒤 16×9 블록
# 평균을 비교한다. 톤 정규화가 없으면 **의도한 룩 변경만으로 전 컷이 경보**가 된다
# (실측: scene07 v8_rt→v8_pt 는 정규화 전 변화픽셀 55 %, 정규화 후 블록이탈 0 %).
#   대조군 A/B  : blk_shift 0.0~25.0 % (최대는 scene07 side_slope — 룩 레이어가
#                 실제로 사면을 바꾼 컷이라 WARN 이 나는 게 맞다)
#   소폭 수정   : 0.0~4.2 %
#   모드 교체   : 0.0 %
#   실회귀      : 36.8 ~ 97.9 %
FRAME_SHIFT_FAIL = 40.0
FRAME_SHIFT_WARN = 20.0
FRAME_BLOCK_DELTA = 10.0   # 블록 평균이 이만큼(0~255) 어긋나면 "이동한 블록"
# 최대 블록 편차. 룩레이어 A/B 대조군 최대 32.7 / 실회귀 78.8~207.
# 배치1 ctx 라운드에서 46~64 대역이 무해하게 나오므로 WARN 을 55 로 둔다
# (대조군의 1.7배, 실회귀 하한 78.8 아래).
FRAME_MAXBLK_FAIL = 100.0
FRAME_MAXBLK_WARN = 55.0
BLOCKS_Y, BLOCKS_X = 9, 16

# --- [PHOTO] 휘도 분포 급변 (절대 mean/dark 의 변화량) ----------------------
#   대조군 |Δmean| <= 7.0 · Δdark <= +0.0 pp
#   모드 교체 |Δmean| <= 8.8
#   실회귀 Δmean -25.0 / Δdark +15.8, +11.8 pp
# 어두워지는 방향만 FAIL 로 본다(밝아지는 것은 회귀가 아니라 개선 방향이 대부분).
PHOTO_DMEAN_FAIL = -45.0
PHOTO_DMEAN_WARN = -20.0
PHOTO_DMEAN_UP_WARN = 25.0     # 밝아짐 — 급변이므로 알리되 FAIL 로 올리지 않는다
PHOTO_DDARK_FAIL = 25.0
PHOTO_DDARK_WARN = 12.0

# --- [GRAZE] grazing 은닉 의심 (h0.3 로봇 시점 = 판정 1순위) ---------------
# 완전 자동 판정은 불가하다. "낙차가 드러나면 지면대에 구조가 늘고, 과잉
# 은닉·매몰이면 구조가 준다" 는 **근사**만 쓴다. 세 지표 중 2개 이상이
# 대조군 밴드를 벗어날 때만 의심 플래그를 올린다.
#   ① vgrad : 지면대(하단 55 %)를 **거시화(박스 블러)한 뒤** 세로 그래디언트
#             평균 = 큰 구조량. 대조군(룩 A/B·모드 교체·소폭 수정 16컷)
#             비율 0.94~1.05, 미세 텍스처만 크게 바뀐 라운드도 0.88~1.17.
#             실구조 변화는 2.0~32.2.
#   ② step_n: 행평균 단차 > 4 인 행의 비율 = 수평 에지(단코·낙차선) 밀도.
#             대조군 |Δ| <= 1.7 pp / 실구조 변화 +22 ~ +81 pp
#   ③ erow  : 최강 단차 행의 상대 위치. 대조군 |Δ| <= 0.01 (거의 완전 고정)
# 전부 **전역 톤 정규화 후** 측정한다(재질만 밝아져도 흔들리지 않게).
GRAZE_VG_WARN = (0.72, 1.40)
GRAZE_VG_STRONG = (0.50, 2.00)
GRAZE_STEPN_WARN = 5.0
GRAZE_STEPN_STRONG = 15.0
GRAZE_EROW_WARN = 0.12
GRAZE_BAND_TOP = 0.45      # 지면대 = 프레임 하단 55 %
GRAZE_ROWSTEP = 4.0        # 행평균 단차 "강함" 기준(0~255)
GRAZE_BLUR_Y = 9           # 거시화 커널 (384 px 축소본 기준 ≈ 원본 45 px)
GRAZE_BLUR_X = 25

# --- 이월 결함 판정 ---------------------------------------------------------
# 절대 결함(DARK/BLOWN)이 이전 라운드에도 있었으면 회귀가 아니다. 이만큼
# 더 나빠졌을 때만 등급을 유지한다. 값은 대조군 A/B 잡음(|Δmean| <= 7.0,
# Δdark <= 0.0 pp)의 약 1.5배.
CARRY_DMEAN = 10.0
CARRY_DDARK = 10.0

# --- [UNCHANGED] 무변화 감지 -----------------------------------------------
# PT 표본 노이즈 상한. realism_phase1 §3.2 실측: PT legacy↔fast 의 평균차
# 0.6~0.7/255. 최대차는 노이즈 한 픽셀로도 튀므로(무변화 컷 실측 max 89 LSB)
# 최대치가 아니라 **평균차 + 유의차 픽셀 비율**로 본다.
#   무변화 실측 : 평균차 0.017~0.235 · 4 LSB 초과 0.000~0.012 %
#   룩레이어 변화: 평균차 15.3      · 4 LSB 초과 55.3 %
IDENTICAL_MEAN = 0.5     # 평균 절대차 (0~255)
IDENTICAL_FRAC = 0.1     # 4 LSB 초과 픽셀 비율 (%)

# --- 처리 해상도 ------------------------------------------------------------
SMALL_LONG = 384     # 구조 비교용 축소 (BOX = 면적 평균 → 평균값 보존)
BLOB_LONG = 192      # 연결성분용 (대면적만 보므로 더 성겨도 된다)

SEV = {"PASS": 0, "INFO": 1, "WARN": 2, "FAIL": 3}
SEV_NAME = ["PASS", "INFO", "WARN", "FAIL"]


# ===========================================================================
# [1] 기본 측정
# ===========================================================================
def _lum(a):
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def _load(path):
    """전해상도 RGB + 축소본 2종을 한 번에 만든다."""
    im = Image.open(path).convert("RGB")
    w, h = im.size
    full = np.asarray(im).astype(np.float32)

    def rs(n):
        s = n / max(w, h)
        return np.asarray(im.resize((max(1, int(w * s)), max(1, int(h * s))),
                                    Image.BOX)).astype(np.float32)
    return full, rs(SMALL_LONG), rs(BLOB_LONG)


def photometry(full):
    """감독 판정문과 동일 정의의 절대 측광 (전해상도에서)."""
    g = _lum(full)
    h = g.shape[0]
    return dict(
        mean=float(g.mean()),
        dark=100.0 * float((g < DARK_LEVEL).mean()),
        dark_near=100.0 * float((g[int(h * NEAR_BAND):] < DARK_LEVEL).mean()),
        clip=100.0 * float((full.max(-1) >= CLIP_LEVEL).mean()),
        white=100.0 * float((full.min(-1)[h // 3:] > WHITE_LEVEL).mean()),
        w=int(g.shape[1]), h=int(h),
    )


def tone_match(src, ref):
    """src 를 ref 의 휘도 분포에 백분위 매칭 — 전역 톤 변화를 제거한다.

    이것이 이 도구의 핵심 전제다. 룩 레이어 라운드는 **전 씬의 밝기·채도·
    하늘이 동시에 바뀐다.** 정규화 없이 픽셀을 비교하면 의도한 변경이
    전부 경보가 되어 도구가 무용지물이 된다(실측: 정규화 전 변화픽셀 55 % →
    정규화 후 블록이탈 0 %, scene07 v8_rt→v8_pt).
    """
    qs = np.linspace(0.0, 100.0, 33)
    xs = np.percentile(src, qs)
    ys = np.percentile(ref, qs)
    xs = np.maximum.accumulate(xs) + np.arange(33) * 1e-6   # 단조 증가 보장
    return np.interp(src, xs, ys)


def block_means(l):
    h, w = l.shape
    return np.array([[l[y * h // BLOCKS_Y:(y + 1) * h // BLOCKS_Y,
                        x * w // BLOCKS_X:(x + 1) * w // BLOCKS_X].mean()
                      for x in range(BLOCKS_X)] for y in range(BLOCKS_Y)])


def largest_blob_pct(mask):
    """4-이웃 최대 연결성분의 화면 비율 (%). 스캔라인 union-find, 순수 파이썬."""
    if not mask.any():
        return 0.0
    H, W = mask.shape
    parent = [0]
    lab = np.zeros((H, W), np.int32)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    nxt = 1
    m = mask
    for y in range(H):
        row = m[y]
        if not row.any():
            continue
        prev_row = lab[y - 1] if y else None
        cur = lab[y]
        for x in np.flatnonzero(row):
            up = prev_row[x] if y else 0
            left = cur[x - 1] if x else 0
            if up and left:
                cur[x] = min(up, left)
                union(up, left)
            elif up or left:
                cur[x] = up or left
            else:
                parent.append(nxt)
                cur[x] = nxt
                nxt += 1
    flat = lab.ravel()
    nz = flat[flat > 0]
    if nz.size == 0:
        return 0.0
    roots = np.array([find(int(v)) for v in np.unique(nz)])
    remap = dict(zip(np.unique(nz).tolist(), roots.tolist()))
    counts = {}
    for v, c in zip(*np.unique(nz, return_counts=True)):
        r = remap[int(v)]
        counts[r] = counts.get(r, 0) + int(c)
    return 100.0 * max(counts.values()) / mask.size


def _boxblur(a, ky, kx):
    """적분영상 박스 평균. 미세 텍스처를 지우고 거시 구조만 남기는 용도."""
    py, px = ky // 2, kx // 2
    p = np.pad(a, ((py, py), (px, px)), mode="edge")
    c = np.pad(np.cumsum(np.cumsum(p, 0), 1), ((1, 0), (1, 0)))
    H, W = a.shape
    return (c[ky:ky + H, kx:kx + W] - c[0:H, kx:kx + W]
            - c[ky:ky + H, 0:W] + c[0:H, 0:W]) / float(ky * kx)


def graze_feat(l):
    """지면대(하단 55 %) **거시** 구조 지표. 톤 정규화된 휘도를 넣을 것.

    거시화(박스 블러)가 핵심이다. 원본 그래디언트를 그대로 쓰면 룩 레이어가
    넣는 **미세 텍스처(정점 변위·디테일 노멀)만으로 지표가 ×8.7 튀어**
    전 씬이 오경보가 된다(실측: scene07 v8_pt→final_pt h0.3_d5,
    raw ×8.72 vs 거시 ×0.88). 낙차 노출은 수십 픽셀 규모의 거시 구조다.
    """
    h = l.shape[0]
    gb = l[int(h * GRAZE_BAND_TOP):]
    if gb.shape[0] < 4:
        return dict(vgrad=0.0, step_n=0.0, erow=0.0)
    macro = _boxblur(gb, GRAZE_BLUR_Y, GRAZE_BLUR_X)
    r = gb.mean(1)
    d = np.abs(np.diff(r))
    return dict(
        vgrad=float(np.abs(np.diff(macro, axis=0)).mean()),
        step_n=100.0 * float((d > GRAZE_ROWSTEP).mean()),
        erow=float(np.argmax(d)) / float(d.size),
    )


# ===========================================================================
# [2] 뷰 인덱싱 — manifest.json 우선, 없으면 파일명 규약
# ===========================================================================
def index_round(d, root):
    """라운드 폴더 → {view: dict(path, mode, ok)}.

    manifest.json 은 `scene_common.capture_pipeline` 이 쓴 구조를 가정한다
    (views/shots, shots[i] = file·mode·sky·view·ok). file 경로는 저장소
    루트 기준 상대경로로 기록되므로 root 를 붙여 푼다. manifest 가 없거나
    깨졌으면 파일명 `{mode}_{sky}_{view}.png` 규약으로 폴백한다.
    """
    out = {}
    mf = os.path.join(d, "manifest.json")
    if os.path.isfile(mf):
        try:
            j = json.load(open(mf))
            for s in j.get("shots", []):
                f = s.get("file", "")
                p = f if os.path.isabs(f) else os.path.join(root, f)
                if not os.path.isfile(p):
                    p2 = os.path.join(d, os.path.basename(f))
                    p = p2 if os.path.isfile(p2) else p
                if os.path.isfile(p):
                    out[s["view"]] = dict(path=p, mode=s.get("mode", "?"),
                                          ok=bool(s.get("ok", True)))
        except Exception as e:                       # manifest 파손 → 폴백
            print(f"[경고] manifest 판독 실패 {mf}: {e}", file=sys.stderr)
    for p in sorted(glob.glob(os.path.join(d, "*.png"))):
        parts = os.path.basename(p)[:-4].split("_", 2)
        if len(parts) == 3 and parts[2] not in out:
            out[parts[2]] = dict(path=p, mode=parts[0], ok=True)
    return out


def is_graze_view(view):
    """grazing 판정 대상 뷰 = h0.3 프리셋(판정 1순위) + grazing 계열 미장센.

    manifest 의 eye z 는 **월드 절대 z** 라 지면이 하강하는 씬에서는 로봇
    눈높이의 지표가 되지 못한다(scene07 side_slope 의 eye z 는 −2.67).
    그래서 grid_views 가 만드는 이름 규약(`preset_h0.3_*`)으로 고른다.
    """
    v = view.lower()
    return ("h0.3" in v) or ("graz" in v)


# ===========================================================================
# [3] 컷 1개 판정
# ===========================================================================
def _add(iss, sev, code, msg):
    iss.append(dict(sev=sev, code=code, msg=msg))


def check_view(scene, view, before, after):
    """(scene, view) 1건 판정. before/after 는 index_round 의 값 dict."""
    r = dict(scene=scene, view=view, verdict="PASS", issues=[], metrics={})
    iss = r["issues"]

    if before is None:
        _add(iss, "INFO", "NEW-VIEW", "이전 라운드에 없던 뷰 — 비교 불가")
    if after is None:
        _add(iss, "FAIL", "MISSING", "신규 라운드에 이 뷰가 없다 — 렌더 누락")
        r["verdict"] = "FAIL"
        return r
    if not after.get("ok", True):
        # `Docs/reports/realism_baseline.md` §알려진 무해한 현상 — capture_pipeline
        # 의 파일 크기 안정화 폴링(40회)이 성급히 끝난 것으로, 파일 자체는 정상.
        # 그래서 INFO 로만 남긴다.
        _add(iss, "INFO", "CAPTURE",
             "manifest ok=false — 캡처 폴링 조기 종료(파일은 정상인 경우가 대부분)")

    fullB, smallB, blobB = _load(after["path"])
    pb = photometry(fullB)
    r["metrics"].update({("after_" + k): v for k, v in pb.items()})

    # ---- 절대 검사 -------------------------------------------------------
    pa = None
    if before is not None:
        fullA, smallA, blobA = _load(before["path"])
        pa = photometry(fullA)
        r["metrics"].update({("before_" + k): v for k, v in pa.items()})
        if before.get("mode", "?") != after.get("mode", "?"):
            _add(iss, "INFO", "MODE",
                 f"렌더 모드 상이 {before['mode']}→{after['mode']} — "
                 f"톤 정규화로 흡수하지만 절대 측광 비교는 주의")

    def grade(bad, warn, was_bad, worsened):
        """이 도구는 **회귀** 검사기다. 같은 결함이 이전 라운드에도 있었다면
        (= 이월) 등급을 낮춘다. 그러지 않으면 원래 어두운 씬(scene06 나선
        내부·scene13 지하·sceneD4 터널 등 합격 33씬 중 4씬)이 매 라운드
        같은 경보를 쏟아내 표를 못 읽게 된다. 다만 **더 나빠졌으면** 유지한다."""
        sev = "FAIL" if bad else ("WARN" if warn else None)
        if sev is None or not was_bad:
            return sev, "[신규]"
        if worsened:
            return ("WARN" if bad else "INFO"), "[이월 — 악화]"
        return "INFO", "[이월 — 변화 없음, 회귀 아님]"

    # [DARK]
    dark_bad = pb["mean"] < DARK_MEAN_FAIL or pb["dark"] > DARK_PCT_FAIL
    dark_warn = pb["mean"] < DARK_MEAN_WARN or pb["dark"] > DARK_PCT_WARN
    if dark_bad or dark_warn:
        was = pa is not None and (pa["mean"] < DARK_MEAN_WARN
                                  or pa["dark"] > DARK_PCT_WARN)
        wor = pa is not None and (pb["mean"] < pa["mean"] - CARRY_DMEAN
                                  or pb["dark"] > pa["dark"] + CARRY_DDARK)
        sev, tag = grade(dark_bad, dark_warn, was, wor)
        if sev:
            _add(iss, sev, "DARK",
                 f"암흑 mean {pb['mean']:.1f} · dark {pb['dark']:.1f} %  {tag}")

    # [BLOWN]
    blown_bad = pb["mean"] > BLOWN_MEAN_FAIL or pb["clip"] > CLIP_PCT_FAIL
    blown_warn = pb["mean"] > BLOWN_MEAN_WARN or pb["clip"] > CLIP_PCT_WARN
    if blown_bad or blown_warn:
        was = pa is not None and (pa["mean"] > BLOWN_MEAN_WARN
                                  or pa["clip"] > CLIP_PCT_WARN)
        wor = pa is not None and (pb["mean"] > pa["mean"] + CARRY_DMEAN
                                  or pb["clip"] > pa["clip"] + 0.2)
        sev, tag = grade(blown_bad, blown_warn, was, wor)
        if sev:
            _add(iss, sev, "BLOWN",
                 f"과노출 mean {pb['mean']:.1f} · 255클리핑 {pb['clip']:.2f} %  {tag}")

    # [WHITE] — 절대치는 참고, 증가분이 판정
    if pa is not None:
        dw = pb["white"] - pa["white"]
        r["metrics"]["d_white"] = dw
        if dw > WHITE_DELTA_FAIL:
            _add(iss, "FAIL", "WHITE",
                 f"순백(>0.8) 대면적 증가 {pa['white']:.1f}→{pb['white']:.1f} % "
                 f"(+{dw:.1f} pp) — v5.1 §4 금지 규약")
        elif dw > WHITE_DELTA_WARN:
            _add(iss, "WARN", "WHITE",
                 f"순백 면적 증가 {pa['white']:.1f}→{pb['white']:.1f} % (+{dw:.1f} pp)")
        elif pb["white"] > WHITE_PCT_WARN:
            _add(iss, "INFO", "WHITE",
                 f"순백 대면적 {pb['white']:.1f} % [이월 — 픽셀>0.8 은 알베도>0.8 이 "
                 f"아니다. 절대치는 참고값]")
    elif pb["white"] > WHITE_PCT_WARN:
        _add(iss, "WARN", "WHITE", f"순백 대면적 {pb['white']:.1f} %")

    # ---- 회귀 검사 (before 있을 때만) ------------------------------------
    if before is not None:
        la, lb = _lum(smallA), _lum(smallB)
        if la.shape != lb.shape:
            _add(iss, "WARN", "SIZE",
                 f"해상도 불일치 {pa['w']}×{pa['h']} → {pb['w']}×{pb['h']} — 구조 비교 생략")
        else:
            # PT 는 표본 노이즈로 ±1~2 LSB 가 항상 흔들린다. 그 이상 아무것도
            # 안 바뀌었다면 **재렌더·토글이 반영되지 않은 것**이다. 실제로
            # scene01 은 자체 캡처 블록을 쓰느라 공용 토글이 안 먹는 전례가 있다
            # (`Docs/reports/realism_phase1.md` §3.4).
            if fullA.shape == fullB.shape:
                d = np.abs(fullA - fullB)
                dmu = float(d.mean())
                dfr = 100.0 * float((d > 4).mean())
                r["metrics"].update(diff_mean=dmu, diff_frac=dfr)
                if dmu < IDENTICAL_MEAN and dfr < IDENTICAL_FRAC:
                    _add(iss, "WARN", "UNCHANGED",
                         f"이전 라운드와 사실상 동일(평균차 {dmu:.2f} LSB · "
                         f"4 LSB 초과 픽셀 {dfr:.3f} %) — 재렌더·룩 토글이 "
                         f"이 컷에 반영되지 않았을 가능성")

            # [PHOTO] 휘도 분포 급변
            dmean = pb["mean"] - pa["mean"]
            ddark = pb["dark"] - pa["dark"]
            r["metrics"].update(d_mean=dmean, d_dark=ddark)
            if dmean <= PHOTO_DMEAN_FAIL or ddark >= PHOTO_DDARK_FAIL:
                _add(iss, "FAIL", "PHOTO",
                     f"휘도 급락 mean {pa['mean']:.1f}→{pb['mean']:.1f} "
                     f"({dmean:+.1f}) · dark {ddark:+.1f} pp")
            elif dmean <= PHOTO_DMEAN_WARN or ddark >= PHOTO_DDARK_WARN:
                _add(iss, "WARN", "PHOTO",
                     f"휘도 하락 mean {dmean:+.1f} · dark {ddark:+.1f} pp")
            elif dmean >= PHOTO_DMEAN_UP_WARN:
                _add(iss, "WARN", "PHOTO",
                     f"휘도 급상승 mean {pa['mean']:.1f}→{pb['mean']:.1f} "
                     f"({dmean:+.1f}) — 밝아지는 방향(대개 개선). 의도 확인")

            # [OCCL] 신규 암부 = 카메라 차폐의 직접 증거
            nd = (la >= OCCL_BRIGHT_BEFORE) & (lb < DARK_LEVEL)
            nd_pct = 100.0 * float(nd.mean())
            H = nd.shape[0]
            nd_near = 100.0 * float(nd[int(H * NEAR_BAND):].mean())
            ga, gb = _lum(blobA), _lum(blobB)
            blob = largest_blob_pct((ga >= OCCL_BRIGHT_BEFORE) & (gb < DARK_LEVEL))
            r["metrics"].update(newdark=nd_pct, newdark_near=nd_near, newdark_blob=blob)
            if nd_pct > OCCL_NEWDARK_FAIL or blob > OCCL_BLOB_FAIL:
                _add(iss, "FAIL", "OCCL",
                     f"신규 암부 {nd_pct:.1f} % (근거리대 {nd_near:.1f} %) · "
                     f"최대 연결 덩어리 {blob:.1f} % — 신설 기하가 카메라를 삼켰을 가능성")
            elif nd_pct > OCCL_NEWDARK_WARN or blob > OCCL_BLOB_WARN:
                _add(iss, "WARN", "OCCL",
                     f"신규 암부 {nd_pct:.1f} % (근거리대 {nd_near:.1f} %) · "
                     f"덩어리 {blob:.1f} %")

            # [FRAME] 전역 톤 정규화 후 블록 점유율 이동
            lbn = tone_match(lb, la)
            bA, bB = block_means(la), block_means(lbn)
            dblk = np.abs(bA - bB)
            shift = 100.0 * float((dblk > FRAME_BLOCK_DELTA).mean())
            mx = float(dblk.max())
            r["metrics"].update(blk_shift=shift, blk_max=mx)
            if shift > FRAME_SHIFT_FAIL or mx > FRAME_MAXBLK_FAIL:
                _add(iss, "FAIL", "FRAME",
                     f"프레임 점유율 급변 — 이동 블록 {shift:.0f} % "
                     f"(최대 편차 {mx:.0f}/255). 톤 정규화 후 값이므로 "
                     f"밝기 변경이 아니라 **화면 구성**이 바뀐 것")
            elif shift > FRAME_SHIFT_WARN or mx > FRAME_MAXBLK_WARN:
                _add(iss, "WARN", "FRAME",
                     f"프레임 점유율 이동 {shift:.0f} % (최대 편차 {mx:.0f}/255)")

            # [GRAZE] h0.3 로봇 시점 은닉 의심
            if is_graze_view(view):
                fa = graze_feat(la)
                fb = graze_feat(lbn)
                ratio = fb["vgrad"] / max(fa["vgrad"], 1e-6)
                dstep = fb["step_n"] - fa["step_n"]
                derow = abs(fb["erow"] - fa["erow"])
                r["metrics"].update(gz_vgrad_ratio=ratio, gz_dstep=dstep,
                                    gz_derow=derow)
                hits, strong = [], 0
                if not (GRAZE_VG_WARN[0] <= ratio <= GRAZE_VG_WARN[1]):
                    hits.append(f"지면 구조량 ×{ratio:.2f}")
                    if not (GRAZE_VG_STRONG[0] <= ratio <= GRAZE_VG_STRONG[1]):
                        strong += 1
                if abs(dstep) > GRAZE_STEPN_WARN:
                    hits.append(f"수평 단차 행 {dstep:+.1f} pp")
                    if abs(dstep) > GRAZE_STEPN_STRONG:
                        strong += 1
                if derow > GRAZE_EROW_WARN:
                    hits.append(f"최강 단차 위치 {derow:+.2f}")
                if len(hits) >= 2:
                    up = ratio > 1.0 or dstep > 0
                    why = ("지면대 구조가 늘었다 → 숨어 있어야 할 낙차가 "
                           "드러났을 가능성" if up else
                           "지면대 구조가 줄었다 → 낙차가 과도하게 은폐·매몰됐을 가능성")
                    sev = "FAIL" if (strong >= 2 or len(hits) == 3) else "WARN"
                    _add(iss, sev, "GRAZE",
                         f"[의심] h0.3 은닉 — {' · '.join(hits)}. {why}. "
                         f"**육안 확인 필요**(자동 확정 불가)")

    worst = max((SEV[i["sev"]] for i in iss), default=0)
    r["verdict"] = SEV_NAME[worst] if worst >= 2 else ("INFO" if worst else "PASS")
    return r


def _job(args):
    try:
        return check_view(*args)
    except Exception as e:                          # 한 컷 실패로 전체가 죽지 않게
        scene, view = args[0], args[1]
        return dict(scene=scene, view=view, verdict="FAIL", metrics={},
                    issues=[dict(sev="FAIL", code="ERROR", msg=f"검사 예외: {e}")])


# ===========================================================================
# [4] 씬 페어 수집
# ===========================================================================
def resolve_round(scene_dir, spec):
    """`final_pt_r2,final_pt,ctx2` 처럼 쉼표 폴백을 받아 존재하는 첫 폴더를 준다."""
    for name in [s.strip() for s in spec.split(",") if s.strip()]:
        d = name if os.path.isabs(name) else os.path.join(scene_dir, name)
        if os.path.isdir(d) and glob.glob(os.path.join(d, "*.png")):
            return d
    return None


def collect_pairs(args, root):
    """[(scene명, before_dir, after_dir)] 을 만든다."""
    pairs = []
    if args.list:
        for ln in open(args.list, encoding="utf-8"):
            ln = ln.split("#")[0].strip()
            if not ln:
                continue
            f = [c.strip() for c in ln.replace("\t", " ").split() if c.strip()]
            if len(f) < 3:
                print(f"[경고] 목록 행 무시(3열 필요): {ln}", file=sys.stderr)
                continue
            sd = f[0] if os.path.isabs(f[0]) else os.path.join(root, f[0])
            b, a = resolve_round(sd, f[1]), resolve_round(sd, f[2])
            pairs.append((os.path.basename(sd.rstrip("/")), b, a))
    elif args.scenes:
        for sd in sorted(glob.glob(args.scenes)):
            if not os.path.isdir(sd):
                continue
            b = resolve_round(sd, args.before_round or "")
            a = resolve_round(sd, args.after_round or "")
            if a is None:
                continue                     # 신규 라운드가 아직 없는 씬은 건너뛴다
            pairs.append((os.path.basename(sd.rstrip("/")), b, a))
    else:
        a = args.after
        b = args.before
        name = os.path.basename(os.path.dirname(a.rstrip("/"))) or "scene"
        pairs.append((name, b, a))
    return pairs


# ===========================================================================
# [5] 출력
# ===========================================================================
MARK = {"PASS": "  ", "INFO": "· ", "WARN": "! ", "FAIL": "✗ "}


def print_scene(scene, b, a, rows):
    tag = f"{scene}  [{os.path.basename(b) if b else '(이전 없음)'} → " \
          f"{os.path.basename(a)}]"
    print(f"\n{'='*100}\n{tag}\n{'-'*100}")
    print(f"{'':2}{'view':<22}{'판정':<6}{'mean':>7}{'dark%':>7}{'신규암부':>9}"
          f"{'덩어리':>8}{'블록이동':>9}  사유")
    for r in rows:
        m = r["metrics"]
        def g(k, f="{:.1f}"):
            return f.format(m[k]) if k in m else "-"
        head = (f"{MARK[r['verdict']]}{r['view'][:22]:<22}{r['verdict']:<6}"
                f"{g('after_mean'):>7}{g('after_dark'):>7}{g('newdark'):>9}"
                f"{g('newdark_blob'):>8}{g('blk_shift','{:.0f}'):>9}")
        # FAIL/WARN 사유는 전부 보여 주고, INFO 는 개수만 (경보 피로 방지 —
        # 전부 나열하면 우선순위를 못 읽는다. 전문은 --json 에 남는다).
        loud = [i for i in r["issues"] if SEV[i["sev"]] >= SEV["WARN"]]
        quiet = [i for i in r["issues"] if SEV[i["sev"]] < SEV["WARN"]]
        if not loud:
            note = ("· " + ", ".join(i["code"] for i in quiet)) if quiet else "—"
            print(head + "  " + note)
            continue
        first = True
        for i in sorted(loud, key=lambda i: -SEV[i["sev"]]):
            print((head if first else " " * 70) + f"  [{i['code']}] {i['msg']}")
            first = False
        if quiet:
            print(" " * 70 + "  · " + ", ".join(i["code"] for i in quiet))


def print_summary(all_rows):
    order = {"FAIL": 0, "WARN": 1, "INFO": 2, "PASS": 3}
    bad = [r for r in all_rows if r["verdict"] in ("FAIL", "WARN")]
    n = len(all_rows)
    cnt = {k: sum(1 for r in all_rows if r["verdict"] == k) for k in SEV_NAME}
    print(f"\n{'='*100}\n총평 — {n} 컷 중 "
          f"FAIL {cnt['FAIL']} · WARN {cnt['WARN']} · INFO {cnt['INFO']} · "
          f"PASS {cnt['PASS']}\n{'='*100}")
    # 이월 결함 — 회귀는 아니지만 감독이 알아야 하는 절대 상태
    carry = {}
    for r in all_rows:
        for i in r["issues"]:
            if i["sev"] == "INFO" and i["code"] in ("DARK", "BLOWN", "WHITE"):
                carry.setdefault(i["code"], {}).setdefault(r["scene"], 0)
                carry[i["code"]][r["scene"]] += 1
    if carry:
        print("\n이월 결함 (이전 라운드에도 있던 절대 상태 — 회귀 아님, 참고):")
        for code, sc in sorted(carry.items()):
            tot = sum(sc.values())
            top = ", ".join(f"{s}×{n}" for s, n in
                            sorted(sc.items(), key=lambda kv: -kv[1])[:6])
            print(f"  {code:<6} {tot:>3} 컷 — {top}")

    if not bad:
        print("\n회귀 없음.")
        return
    print("\n우선순위 (FAIL → WARN, 씬순):")
    for r in sorted(bad, key=lambda r: (order[r["verdict"]], r["scene"], r["view"])):
        codes = ",".join(sorted({i["code"] for i in r["issues"]
                                 if i["sev"] in ("FAIL", "WARN")}))
        print(f"  {r['verdict']:<5} {r['scene']:<10} {r['view']:<24} {codes}")
    scenes = {}
    for r in all_rows:
        s = scenes.setdefault(r["scene"], {"FAIL": 0, "WARN": 0})
        if r["verdict"] in s:
            s[r["verdict"]] += 1
    worst = sorted(scenes.items(), key=lambda kv: (-kv[1]["FAIL"], -kv[1]["WARN"]))
    print("\n씬 우선순위:")
    for s, c in worst:
        if c["FAIL"] or c["WARN"]:
            print(f"  {s:<12} FAIL {c['FAIL']:>2} · WARN {c['WARN']:>2}")


# ===========================================================================
def main(argv=None):
    ap = argparse.ArgumentParser(
        description="렌더 라운드 회귀 검사기 (이미지 + manifest.json 만 사용)")
    ap.add_argument("--before", help="이전 라운드 폴더 (단일 씬 모드)")
    ap.add_argument("--after", help="신규 라운드 폴더 (단일 씬 모드)")
    ap.add_argument("--scenes", help="씬 폴더 글롭 (예: 'look_check/scene*')")
    ap.add_argument("--before-round", help="씬 안의 이전 라운드 이름. 쉼표 폴백 가능")
    ap.add_argument("--after-round", help="씬 안의 신규 라운드 이름. 쉼표 폴백 가능")
    ap.add_argument("--list", help="씬별 라운드 목록 파일 (씬경로 이전 이후)")
    ap.add_argument("--json", help="기계 판독용 JSON 출력 경로")
    ap.add_argument("--only", help="뷰 이름 부분일치 필터 (쉼표)")
    ap.add_argument("--fail-only", action="store_true", help="FAIL/WARN 컷만 출력")
    ap.add_argument("--jobs", type=int, default=min(8, os.cpu_count() or 1))
    ap.add_argument("--root", default=os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))),
        help="저장소 루트 (manifest 의 상대경로 해석 기준)")
    a = ap.parse_args(argv)

    if not (a.list or a.scenes or (a.before and a.after)):
        ap.error("--before/--after, 또는 --scenes + --after-round, 또는 --list 중 하나가 필요합니다.")
    if a.scenes and not a.after_round:
        ap.error("--scenes 모드에는 --after-round 가 필요합니다.")

    root = a.root
    pairs = collect_pairs(a, root)
    if not pairs:
        print("[에러] 비교할 씬을 못 찾았습니다.")
        return 2
    only = [s.strip() for s in a.only.split(",")] if a.only else None

    jobs, meta = [], []
    for scene, bdir, adir in pairs:
        if adir is None or not os.path.isdir(adir):
            print(f"[경고] {scene}: 신규 라운드 폴더 없음 — 건너뜀", file=sys.stderr)
            continue
        A = index_round(adir, root)
        B = index_round(bdir, root) if bdir else {}
        if bdir is None:
            print(f"[경고] {scene}: 이전 라운드 폴더 없음 — 절대 검사만 수행",
                  file=sys.stderr)
        views = sorted(set(A) | set(B))
        if only:
            views = [v for v in views if any(o in v for o in only)]
        for v in views:
            jobs.append((scene, v, B.get(v), A.get(v)))
        meta.append((scene, bdir, adir, views))

    if not jobs:
        print("[에러] 비교할 컷이 없습니다.")
        return 2

    if a.jobs > 1 and len(jobs) > 1:
        with ProcessPoolExecutor(max_workers=a.jobs) as ex:
            results = list(ex.map(_job, jobs, chunksize=1))
    else:
        results = [_job(j) for j in jobs]

    by = {}
    for r in results:
        by.setdefault(r["scene"], {})[r["view"]] = r
    for scene, bdir, adir, views in meta:
        rows = [by[scene][v] for v in views if v in by.get(scene, {})]
        if a.fail_only:
            rows = [r for r in rows if r["verdict"] in ("FAIL", "WARN")]
            if not rows:
                continue
        print_scene(scene, bdir, adir, rows)
    print_summary(results)

    if a.json:
        os.makedirs(os.path.dirname(os.path.abspath(a.json)) or ".", exist_ok=True)
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(dict(
                pairs=[dict(scene=s, before=b, after=c) for s, b, c, _ in meta],
                results=results), f, indent=2, ensure_ascii=False)
        print(f"\n[JSON] {a.json}")

    # 종료코드: FAIL 있으면 1 (배치 스크립트에서 게이트로 쓸 수 있게)
    return 1 if any(r["verdict"] == "FAIL" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
