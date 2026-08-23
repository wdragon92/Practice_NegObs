#!/usr/bin/env python3
"""
p4_retrain_epoch.py — 신선택식이 고른 에폭의 **체크포인트를 물질화**하기 위한 얇은 래퍼.

배경: dayrun_0820/runs/v2/*/ 에는 best.pt / last.pt 만 있고 에폭별 체크포인트가 없다.
      metrics.csv 로 재선택은 가능하지만, 신식이 다른 에폭을 고른 런은 그 에폭의
      가중치가 없어서 test-core 성적을 낼 수 없다.

규칙 준수: train_polar.py 를 **수정하지 않는다**. 여기서 torch.save 를 감싸
      `last.pt` 저장 시점마다 지정 에폭이면 `ep<N>.pt` 를 추가로 떨군다.
      학습 로직·시드·순서는 원본 그대로다(결정론: set_seed + cudnn.deterministic).

사용:
  python p4_retrain_epoch.py --which polar --keep 9,10 -- <train_polar.py 인자 전부>
  python p4_retrain_epoch.py --which b2    --keep 1,8  -- <train_b2_polar.py 인자 전부>
"""
from __future__ import annotations

import argparse
import os
import sys

R = "/home/vislab/Desktop/work_sy/Practice_NegObs"
CODE = f"{R}/experiments/mainrun_0819/code"
B2 = f"{R}/experiments/mainrun_0819/b2_polar"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--which", choices=["polar", "b2"], required=True)
    ap.add_argument("--keep", required=True, help="쉼표 구분 에폭 번호")
    ap.add_argument("rest", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    keep = {int(x) for x in a.keep.split(",") if x.strip()}
    argv = [x for x in a.rest if x != "--"]

    sys.path.insert(0, CODE)
    if a.which == "b2":
        sys.path.insert(0, B2)

    import torch
    _orig_save = torch.save

    def save(obj, f, *args, **kw):
        _orig_save(obj, f, *args, **kw)
        try:
            fs = str(f)
            if isinstance(obj, dict) and "epoch" in obj and os.path.basename(fs) == "last.pt":
                ep = int(obj["epoch"])
                if ep in keep:
                    tgt = os.path.join(os.path.dirname(fs), f"ep{ep}.pt")
                    _orig_save(obj, tgt)
                    print(f"[p4] kept epoch checkpoint -> {tgt}", flush=True)
        except Exception as e:                      # 저장 보조기능이 학습을 죽이면 안 된다
            print(f"[p4] WARN keep-epoch failed: {e}", file=sys.stderr, flush=True)

    torch.save = save

    if a.which == "b2":
        import train_b2_polar as M
    else:
        import train_polar as M
    return M.main(argv)


if __name__ == "__main__":
    sys.exit(main() or 0)
