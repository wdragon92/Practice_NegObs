#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w3_manifest.py — test-ext 매니페스트 조립 (**§2-8 재채점 훅의 입력**)

ACCOUNTING §2-8 은 v2 체크포인트 9개를 **test-ext 에 zero-shot 재채점**해서 계기판의
"진짜 before" 를 만들라고 명령한다. 그 재채점 파이프라인(`rescore_v2corr.sh` 계보)이
받는 입력은 정확히 두 개다 — **매니페스트**와 **분할 파일**. 이 스크립트가 둘을 만든다.

**재채점은 여기서 돌리지 않는다.** 본 웨이브의 임무는 렌더·라벨·게이트까지이고,
재채점은 §2-8 소관의 별도 트랙이다. 여기서 하는 일은 *"입력이 준비되었다"* 를
**주장이 아니라 파일로** 만드는 것뿐이다.

밴드라운드가 4개(base/h/lat/b2)이므로 `build_manifest.py` 를 라운드마다 돌리고
**프레임 배열을 이어붙인다.** 이어붙이기가 안전한 이유: `frame_id` 가
`{arm}/{scene}/{file}` 인데 **밴드마다 라운드 디렉터리가 다르므로** 같은 씬·같은
파일명이 서로 다른 라운드에서 나온다 ⇒ 병합 시 **`round` 를 frame_id 에 접두**해
충돌을 없앤다(그러지 않으면 base 밴드의 `L0__…__0000.png` 와 H 밴드의 같은 이름이
겹친다).

쌍 규약은 **(A,C)** — 계기판①의 세대 통일 규약(§2-2 / 계획 §3.4).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

# 0827 reorg: dataset/ is grouped (dataset/<group>/<round>) and a round is
# found by NAME, never by a flat path. See Docs/reorg_0827/S3_report.md.
sys.path.insert(0, REPO)                              # noqa: E402
from variation_kit import round_dir_or_flat   # noqa: E402
V3 = os.path.join(REPO, "experiments", "v3_0823")
ANN = os.path.join(V3, "annotations")
LAB = os.path.join(REPO, "experiments", "mainrun_0819", "code", "labeling")
PY = "/home/vislab/miniconda3/envs/env_seg/bin/python"

ROUNDS = [("base", "260824_v3w3_extbase"), ("h", "260824_v3w3_exth"),
          ("lat", "260824_v3w3_extlat"), ("b2", "260824_v3w3_extb2")]
SCENES = ["sceneH1", "sceneH2", "sceneH3", "sceneL1", "sceneN9", "sceneN11"]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pair", default="ac", choices=["ac", "bd"],
                    help="쌍 규약. 계기판①은 ac (§2-2)")
    ap.add_argument("--out", default=os.path.join(
        V3, "dataset_manifest_v3_textext.json"))
    ap.add_argument("--split-out", default=os.path.join(V3, "split_v3_textext.json"))
    a = ap.parse_args(argv)

    on_arm, off_arm = ("A", "C") if a.pair == "ac" else ("B", "D")
    frames, metas = [], {}
    for tag, stamp in ROUNDS:
        lab = os.path.join(ANN, f"w3_{tag}_{a.pair}_labels.json")
        if not os.path.isfile(lab):
            print(f"[manifest] {tag}: 라벨 없음 — 건너뜀 ({lab})")
            continue
        tmp = os.path.join(ANN, f"_w3_{tag}_{a.pair}_manifest.json")
        cmd = [PY, "build_manifest.py", "--labels", lab,
               "--on-round", round_dir_or_flat(f"{stamp}_{on_arm}"),
               "--off-round", round_dir_or_flat(f"{stamp}_{off_arm}"),
               "--out", tmp]
        r = subprocess.run(cmd, cwd=LAB, capture_output=True, text=True,
                           env={**os.environ, "PYTHONNOUSERSITE": "1"})
        sys.stderr.write(r.stderr)
        if r.returncode != 0:
            print(f"[manifest] {tag}: build_manifest 실패 rc={r.returncode}")
            continue
        m = json.load(open(tmp, encoding="utf-8"))
        metas[tag] = m["meta"]
        for f in m["frames"]:
            # 밴드라운드 접두로 frame_id 충돌 제거 (base/H 가 같은 파일명을 쓴다)
            f["frame_id"] = f"{tag}/{f['frame_id']}"
            f["band_round"] = tag
            frames.append(f)
        print(f"[manifest] {tag}: {len(m['frames'])}프레임")

    if not frames:
        print("[manifest] 프레임 0 — 라벨을 먼저 만들 것")
        return 1

    base_meta = metas.get("base") or next(iter(metas.values()))
    man = dict(meta=dict(
        base_meta,
        doc="v3 test-ext (평가 전용) — ACCOUNTING §2-8 zero-shot 재채점 입력",
        pair=f"({on_arm},{off_arm})",
        band_rounds={t: metas[t]["rounds"] for t in metas},
        n_frames=len(frames),
        scenes=SCENES,
        note="test-ext 는 v2·v3 양 모델 모두 미학습 (AC §2-9). "
             "본 매니페스트는 재채점 입력일 뿐이며 훈련에 절대 넣지 않는다."),
        frames=frames)
    json.dump(man, open(a.out, "w", encoding="utf-8"), indent=1)
    print(f"[manifest] 합계 {len(frames)}프레임 → {a.out}")

    split = dict(train=[], val=[], test=SCENES, hold=[])
    json.dump(split, open(a.split_out, "w", encoding="utf-8"), indent=1)
    print(f"[manifest] split → {a.split_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
