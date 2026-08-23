#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w1c_seg_stale_test.py — REPAIR 1 (D79 ③) 의 순수-파이썬 증명.

`scripts/run_data_render.py` 의 per-cut ID-mask stale 가드를 **GPU 없이** 전부
구동한다. 실제 경합(0.15-0.37 %)을 기다리지 않고도 다음을 증명한다:

  1. 술어 `_seg_verdict` 진리표 — "마스크 반복 ∧ 프레임 이동" 만 stale
  2. 재페치 루프가 실제로 N회 돈다 (`NEGOBS_SEG_RETRY` 로 N 조정 가능)
  3. 잔여 실패 시 `.idseg.npz` 는 **쓰이지 않고** `.idseg.STALE` 마커가 쓰인다
  4. 거부된 컷은 비교 기준을 **재기준화하지 않는다** (다음 컷도 계속 거부)
  5. 동일 프레임(마스크 동일 ∧ 목격자 동일)은 정상으로 통과한다
  6. depth 가 없으면 pose 목격자로 폴백한다

실행:
    cd /home/vislab/Desktop/work_sy/Practice_NegObs
    python3 experiments/v3_0823/code/w1c_seg_stale_test.py

`_seg_fetch` 만 가짜로 바꾸고(어노테이터/Isaac 불필요) 나머지 — 해시, 목격자,
술어, 재시도 루프, 마커 기록 — 는 전부 **정본 코드 그대로** 돈다.
"""
from __future__ import annotations

import os
import sys
import json
import shutil
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, REPO)

import numpy as np                                              # noqa: E402
import run_data_render as R                                     # noqa: E402

FAILS = []
NCHK = 0


def chk(name, cond, detail=""):
    global NCHK
    NCHK += 1
    print(f"  [{'ok ' if cond else 'FAIL'}] {name}" + (f" — {detail}" if detail
                                                       else ""))
    if not cond:
        FAILS.append(name)


def mask(seed, h=8, w=8):
    """A deterministic fake id mask."""
    r = np.random.RandomState(seed)
    return r.randint(0, 40, size=(h, w)).astype(np.uint16)


def depth(seed, h=8, w=8):
    r = np.random.RandomState(1000 + seed)
    return r.rand(h, w).astype(np.float32)


class FakeFetch:
    """Stands in for `_seg_fetch`. Yields the scripted (array, id2l, how)."""

    def __init__(self, script):
        self.script = list(script)
        self.calls = 0

    def __call__(self, ann, sim_app, subframes):
        self.calls += 1
        a = self.script[min(self.calls - 1, len(self.script) - 1)]
        if a is None:
            return None, None, "empty"
        return a, {"1": "/World/Fake"}, "orch"


def guarded(script, depth_arr, tmp, fname="L0__s1__0000.png",
            cam=None, cond="L0"):
    """Drive the real `_seg_fetch_guarded` over a scripted fetch sequence."""
    fake = FakeFetch(script)
    old = R._seg_fetch
    R._seg_fetch = fake
    try:
        out = R._seg_fetch_guarded(
            object(), object(), 8, depth_arr,
            cam or dict(eye=[1.0, 2.0, 3.0], yaw=10.0, pitch=-5.0, hfov=70.0),
            "scene04", cond, fname, os.path.join(tmp, fname))
    finally:
        R._seg_fetch = old
    return out, fake


def reset():
    R._seg_prev().clear()


# --------------------------------------------------------------------- 1
print("\n[1] pure predicate `_seg_verdict` (no numpy, no GPU)")
A = ("maskA", "depth", "d0")
B = ("maskB", "depth", "d1")
chk("first cut is never stale", R._seg_verdict(A, None) == (False, "first-cut"))
chk("mask changed -> not stale",
    R._seg_verdict(B, A) == (False, "mask-changed"))
chk("mask repeat + witness moved -> STALE",
    R._seg_verdict(("maskA", "depth", "d9"), A)
    == (True, "mask-repeat-while-frame-moved"))
chk("mask repeat + witness identical -> not stale (genuinely same frame)",
    R._seg_verdict(A, A) == (False, "identical-frame"))
chk("witness kinds differ -> refuse to conclude, keep the mask",
    R._seg_verdict(("maskA", "pose", "p0"), A)
    == (False, "witness-kind-mismatch"))

# --------------------------------------------------------------------- 2
print("\n[2] content hash and witness")
chk("same content -> same sha", R._seg_sha(mask(1)) == R._seg_sha(mask(1)))
chk("different content -> different sha",
    R._seg_sha(mask(1)) != R._seg_sha(mask(2)))
chk("dtype is inside the digest (no reinterpretation collision)",
    R._seg_sha(np.zeros(4, np.uint16)) != R._seg_sha(np.zeros(4, np.uint32)))
chk("depth present -> depth witness",
    R._seg_witness(depth(1), {"yaw": 1})[0] == "depth")
chk("depth absent -> pose witness",
    R._seg_witness(None, {"yaw": 1})[0] == "pose")
chk("pose witness moves with the pose",
    R._seg_witness(None, {"yaw": 1})[1] != R._seg_witness(None, {"yaw": 2})[1])

# --------------------------------------------------------------------- 3
print("\n[3] happy path — every cut fresh, 0 retries, 0 markers")
tmp = tempfile.mkdtemp(prefix="w1c_seg_")
reset()
seen = []
for i in range(8):
    (a, id2l, how, n, bad), fk = guarded([mask(i)], depth(i), tmp,
                                         fname=f"L0__s1__{i:04d}.png")
    seen.append((a is not None, n, bad, fk.calls))
chk("8/8 accepted", all(s[0] for s in seen))
chk("0 retries anywhere", all(s[1] == 0 for s in seen))
chk("no stale info", all(s[2] is None for s in seen))
chk("exactly one fetch per cut", all(s[3] == 1 for s in seen))
chk("no .STALE marker written",
    not [f for f in os.listdir(tmp) if f.endswith(".STALE")])

# --------------------------------------------------------------------- 4
print("\n[4] recovery — annotator returns the previous mask twice, then the "
      "real one")
reset()
guarded([mask(10)], depth(10), tmp, fname="L0__s1__0000.png")   # baseline
(a, id2l, how, n, bad), fk = guarded([mask(10), mask(10), mask(11)],
                                     depth(11), tmp,
                                     fname="L0__s1__0001.png")
chk("mask accepted after retries", a is not None)
chk("2 retries reported", n == 2, f"n={n}")
chk("3 fetches issued (1 + 2 retries)", fk.calls == 3, f"calls={fk.calls}")
chk("fetch rung still reported as 'orch'", how == "orch", how)
chk("no stale info / no marker", bad is None and not [
    f for f in os.listdir(tmp) if f.endswith(".STALE")])
chk("baseline advanced to the accepted mask",
    R._seg_prev()["prev"][0] == R._seg_sha(mask(11)))

# --------------------------------------------------------------------- 5
print("\n[5] residual failure — .idseg.STALE marker instead of a bad .npz")
tmp2 = tempfile.mkdtemp(prefix="w1c_seg_")
reset()
guarded([mask(20)], depth(20), tmp2, fname="L5__s1__0002.png")  # baseline
(a, id2l, how, n, bad), fk = guarded([mask(20)], depth(21), tmp2,
                                     fname="L5__s1__0003.png", cond="L5")
chk("mask REFUSED (returns None like an absent mask)", a is None)
chk("default retry budget is 3", n == 3, f"n={n}")
chk("4 fetches issued (1 + 3 retries)", fk.calls == 4, f"calls={fk.calls}")
chk("stale info returned to the caller", isinstance(bad, dict))
mk = os.path.join(tmp2, "L5__s1__0003.idseg.STALE")
chk(".idseg.STALE marker exists next to the PNG stem", os.path.isfile(mk))
chk("NO .idseg.npz was written for the refused cut",
    not os.path.isfile(os.path.join(tmp2, "L5__s1__0003.idseg.npz")))
if os.path.isfile(mk):
    j = json.load(open(mk, encoding="utf-8"))
    print("        marker:", json.dumps(j, sort_keys=True)[:220])
    chk("marker records scene / file / cond",
        j["scene"] == "scene04" and j["file"] == "L5__s1__0003.png"
        and j["cond"] == "L5")
    chk("marker records retries and reason",
        j["retries"] == 3 and j["reason"] == "mask-repeat-while-frame-moved")
    chk("marker records prev and current mask sha",
        j["prev_idseg_sha"] == R._seg_sha(mask(20))
        and j["idseg_sha"] == R._seg_sha(mask(20)))
    chk("marker records the witness that moved",
        j["witness"] == "depth" and j["prev_witness_sha"] != j["witness_sha"])

# --------------------------------------------------------------------- 6
print("\n[6] a refused cut does NOT re-baseline onto its own bad output")
(a2, _, _, n2, bad2), _ = guarded([mask(20)], depth(22), tmp2,
                                  fname="L5__s1__0004.png", cond="L5")
chk("the NEXT cut with the same stuck mask is refused too", a2 is None)
chk("and it is compared against the last ACCEPTED mask",
    bad2 is not None and bad2["prev_idseg_sha"] == R._seg_sha(mask(20)))
chk("its own marker exists",
    os.path.isfile(os.path.join(tmp2, "L5__s1__0004.idseg.STALE")))

# --------------------------------------------------------------------- 7
print("\n[7] a genuinely identical frame is accepted, not refused")
tmp3 = tempfile.mkdtemp(prefix="w1c_seg_")
reset()
d = depth(30)
guarded([mask(30)], d, tmp3, fname="L0__s1__0000.png")
(a, _, _, n, bad), fk = guarded([mask(30)], d, tmp3,
                                fname="L0__s1__0001.png")
chk("same mask + same depth -> accepted", a is not None)
chk("no retry burnt", n == 0 and fk.calls == 1)
chk("no marker", not os.path.isfile(
    os.path.join(tmp3, "L0__s1__0001.idseg.STALE")))

# --------------------------------------------------------------------- 8
print("\n[8] pose fallback when the depth fetch came back empty")
reset()
guarded([mask(40)], None, tmp3, fname="L0__s1__0002.png",
        cam=dict(eye=[1.0, 0.0, 0.0], yaw=0.0, pitch=0.0, hfov=70.0))
(a, _, _, n, bad), fk = guarded([mask(40)], None, tmp3,
                                fname="L0__s1__0003.png",
                                cam=dict(eye=[9.0, 0.0, 0.0], yaw=0.0,
                                         pitch=0.0, hfov=70.0))
chk("mask repeat while the POSE moved -> refused", a is None)
chk("marker names the pose witness",
    bad is not None and bad["witness"] == "pose")

# --------------------------------------------------------------------- 9
print("\n[9] NEGOBS_SEG_RETRY overrides the budget")
os.environ["NEGOBS_SEG_RETRY"] = "1"
chk("_seg_retries() honours the env", R._seg_retries() == 1)
tmp4 = tempfile.mkdtemp(prefix="w1c_seg_")
reset()
guarded([mask(50)], depth(50), tmp4, fname="L0__s1__0000.png")
(a, _, _, n, bad), fk = guarded([mask(50)], depth(51), tmp4,
                                fname="L0__s1__0001.png")
chk("1 retry only (2 fetches)", n == 1 and fk.calls == 2,
    f"n={n} calls={fk.calls}")
os.environ["NEGOBS_SEG_RETRY"] = "not-a-number"
chk("garbage env falls back to the default, never raises",
    R._seg_retries() == R.SEG_RETRY_DEFAULT)
os.environ.pop("NEGOBS_SEG_RETRY")
chk("unset env -> default 3", R._seg_retries() == 3)

# -------------------------------------------------------------------- 10
print("\n[10] an EMPTY fetch is passed straight through (absent != stale)")
reset()
guarded([mask(60)], depth(60), tmp4, fname="L0__s1__0002.png")
base = dict(R._seg_prev())
(a, _, how, n, bad), fk = guarded([None], depth(61), tmp4,
                                  fname="L0__s1__0003.png")
chk("returns (None, ..., None) — caller logs 'no idseg'",
    a is None and bad is None and how == "empty")
chk("no retry loop on an absent mask", n == 0 and fk.calls == 1)
chk("baseline untouched", dict(R._seg_prev()) == base)
chk("no marker for an absent mask", not os.path.isfile(
    os.path.join(tmp4, "L0__s1__0003.idseg.STALE")))

# -------------------------------------------------------------------- 11
print("\n[11] default-path inertness (the sidecar-off contract)")
os.environ.pop("NEGOBS_SEG_SIDECAR", None)
chk("_seg_on() False with the env unset", R._seg_on() is False)
chk("_seg_attach returns None before touching replicator",
    R._seg_attach(object(), object()) is None)
os.environ["NEGOBS_SEG_SIDECAR"] = "1"
chk("_seg_attach still returns None without a render product",
    R._seg_attach(None, object()) is None)
os.environ.pop("NEGOBS_SEG_SIDECAR")
if hasattr(R._seg_prev, "st"):
    del R._seg_prev.st
chk("guard state is not allocated until the opt-in path calls it",
    not hasattr(R._seg_prev, "st"))

for d_ in (tmp, tmp2, tmp3, tmp4):
    shutil.rmtree(d_, ignore_errors=True)

print(f"\n{'=' * 62}\n{NCHK - len(FAILS)}/{NCHK} checks passed"
      + (f" — FAILED: {FAILS}" if FAILS else " — ALL PASS"))
sys.exit(1 if FAILS else 0)
