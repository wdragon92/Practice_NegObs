"""CPU self-test for the OPTIONAL amodal-mask pixel-BCE aux loss (DAYRUN_BRIEF_0820 Phase 6).

Piggybacks mainrun_0819/code/smoke_test.py: same fake-frame fabricator, same subprocess runner,
same CUDA_VISIBLE_DEVICES="" discipline — this file only adds what the aux path introduces.

    PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES="" \
    /home/vislab/miniconda3/envs/env_seg/bin/python experiments/dayrun_0820/code/smoke_aux.py

What it proves
  1. model_factory.build(use_mask_head=True) -> (logits, mask_logits) and the state_dict is
     key-for-key identical to the default build (so eval_polar/infer_photo need no flag).
  2. polar_dataset.aux_mask_stem == yolo/common.stem_of (the mask filename contract).
  3. PolarGridDataset(aux_mask_dir=...) yields a 4-tuple; a MISSING PNG is an all-zero mask;
     a present PNG round-trips; hflip flips the mask together with the image.
  4. train_polar --aux-mask-dir --aux-lambda: finite train_loss_cell / train_loss_aux per epoch,
     total == cell + lambda*aux, aux fields in config.json, and the aux checkpoint still loads
     into the unmodified eval_polar.py.
  5. DEFAULT-OFF REGRESSION: a no-aux run reproduces the pre-change metrics.csv header and the
     pre-change config.json key set (checked against the real runs/v2/rgb_s42 artefacts too).

Exit 0 = green.
"""
from __future__ import annotations

import csv
import json
import math
import os
import shutil
import sys
import tempfile

import numpy as np
import torch
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))                      # dayrun_0820/code
DAYRUN = os.path.dirname(HERE)
EXPS = os.path.dirname(DAYRUN)
MAINRUN_CODE = os.path.join(EXPS, "mainrun_0819", "code")
sys.path.insert(0, MAINRUN_CODE)

import gridspec  # noqa: E402
import model_factory  # noqa: E402
import smoke_test as SM  # noqa: E402  (the piggyback: fake_frames + run + ENV)
from polar_dataset import PolarGridDataset, aux_mask_path, aux_mask_stem  # noqa: E402

BASE_HEADER = ["epoch", "train_loss", "val_loss", "val_f1", "val_recall", "val_fpr",
               "lr", "sec", "val_h_recall", "sel_score"]
AUX_CFG_KEYS = {"aux_mask_dir", "aux_lambda", "aux_enabled", "aux_masks_found",
                "aux_masks_missing_as_empty", "aux_loss", "aux_val_note"}
LAM = 0.5
REAL_RUN = os.path.join(DAYRUN, "runs", "v2", "rgb_s42")     # the run this ablation twins with


def hdr(t):
    print(f"\n=== {t}")


# --------------------------------------------------------------------- 1. model
def check_model(nc):
    plain = model_factory.build("rgb", encoder_weights=None, classes=nc).eval()
    aux = model_factory.build("rgb", encoder_weights=None, classes=nc, use_mask_head=True).eval()
    with torch.no_grad():
        o = plain(torch.randn(2, 3, 64, 64))
        lo, mk = aux(torch.randn(2, 3, 64, 64))
    assert not isinstance(o, tuple) and tuple(o.shape) == (2, nc), "default build must stay 1-out"
    assert tuple(lo.shape) == (2, nc) and tuple(mk.shape) == (2, 1, 64, 64), (lo.shape, mk.shape)
    assert list(plain.state_dict()) == list(aux.state_dict()), "state_dict keys must not move"
    assert sum(p.numel() for p in plain.parameters()) == sum(p.numel() for p in aux.parameters())
    aux.load_state_dict(plain.state_dict())            # both directions must be loadable
    plain.load_state_dict(aux.state_dict())
    print(f"    [MODEL] use_mask_head -> logits{tuple(lo.shape)} + mask{tuple(mk.shape)}; "
          f"state_dict identical ({len(list(plain.state_dict()))} tensors) and cross-loadable")


# --------------------------------------------------------------------- 2. stem contract
def check_stem():
    cases = ["on/scene01/L0__s20260819__0000.png",
             "off/scene09/L0__s20260820__0003.png::boost_h",
             "on/scene14/L2__s20260820__0011.png::boost_e2"]
    want = ["on__scene01__L0__s20260819__0000",
            "off__scene09__L0__s20260820__0003__boost_h",
            "on__scene14__L2__s20260820__0011__boost_e2"]
    got = [aux_mask_stem(c) for c in cases]
    assert got == want, (got, want)
    try:                                    # the owner of the rule (imports labeler.py)
        sys.path.insert(0, os.path.join(HERE, "yolo"))
        import common as YC
        assert [YC.stem_of(c) for c in cases] == got, "aux_mask_stem drifted from common.stem_of"
        src = "== yolo/common.stem_of"
    except Exception as e:                                                  # noqa: BLE001
        src = f"(common.py not importable here: {type(e).__name__}) — table-checked only"
    real = os.path.join(DAYRUN, "annotations", "amodal")
    hit = os.path.exists(aux_mask_path(real, cases[0])) if os.path.isdir(real) else None
    print(f"    [STEM] {got[0]}.png  {src}  real-corpus hit={hit}")


# --------------------------------------------------------------------- fabrication
def build_ws(tmp, grid):
    """3 scenes x 2 cuts x 2 arms; train=sceneA -> exactly 4 train frames, 2 of them masked."""
    rng = np.random.default_rng(0)
    img = os.path.join(tmp, "img")
    os.makedirs(img, exist_ok=True)
    frames = []
    for s in ("sceneA", "sceneB", "sceneC"):
        frames += SM.fake_frames(s, img, rng, grid, n_cuts=2)
    man = os.path.join(tmp, "manifest.json")
    json.dump(dict(meta=dict(source="smoke_aux", grid_version=grid.version), frames=frames),
              open(man, "w"))
    sp = os.path.join(tmp, "split.json")
    json.dump(dict(train=["sceneA"], val=["sceneB"], test=["sceneC"]), open(sp, "w"))

    # 4 train frames: on/off x cut{0,1}. Write a mask PNG for the two ON frames only, so both
    # OFF frames exercise the missing-file -> zeros path (exactly the real corpus's shape:
    # 1104 PNGs for 2832 frames; every off-arm frame and every 'none_in_fov' on-arm frame).
    mdir = os.path.join(tmp, "amodal")
    os.makedirs(mdir, exist_ok=True)
    written = []
    for j in range(2):
        fid = f"on/sceneA/L0__s0__{j:04d}.png"
        a = np.zeros((540, 960), np.uint8)
        a[300:400, 100 + 300 * j:300 + 300 * j] = 255      # ASYMMETRIC -> a flip is detectable
        Image.fromarray(a, mode="L").save(aux_mask_path(mdir, fid))
        written.append(aux_mask_stem(fid) + ".png")
    return man, sp, mdir, written


# --------------------------------------------------------------------- 3. dataset
def check_dataset(man, sp, mdir, grid):
    S = 64
    off = PolarGridDataset(man, sp, "train", "rgb", img_size=S, grid=grid)
    assert len(off[0]) == 3, "no aux_mask_dir must keep the 3-tuple contract"
    assert off.aux_mask_dir is None and off.n_aux_found == 0

    ds = PolarGridDataset(man, sp, "train", "rgb", img_size=S, grid=grid, aux_mask_dir=mdir)
    assert (ds.n_aux_found, ds.n_aux_missing) == (2, 2), (ds.n_aux_found, ds.n_aux_missing)
    seen_pos = seen_zero = 0
    for i in range(len(ds)):
        item = ds[i]
        assert len(item) == 4, "aux_mask_dir must yield (x, y, meta, mask)"
        x, y, meta, m = item
        assert tuple(m.shape) == (1, S, S) and m.dtype == torch.float32, (m.shape, m.dtype)
        assert set(torch.unique(m).tolist()) <= {0.0, 1.0}, torch.unique(m)
        assert tuple(x.shape) == (3, S, S) and tuple(y.shape) == (grid.n_cells,)
        exists = os.path.exists(aux_mask_path(mdir, meta["frame_id"]))
        if exists:
            assert float(m.sum()) > 0, f"{meta['frame_id']}: masked frame came back empty"
            seen_pos += 1
        else:
            assert float(m.sum()) == 0.0, f"{meta['frame_id']}: missing PNG must be all zeros"
            seen_zero += 1
    assert (seen_pos, seen_zero) == (2, 2)

    # hflip: the mask must flip with the image, on the SAME coin, and never permute
    base_x, _by, _bm, base_m = ds[0]
    dh = PolarGridDataset(man, sp, "train", "rgb", img_size=S, grid=grid, aux_mask_dir=mdir,
                          train_hflip=True)
    torch.manual_seed(0)
    combos = set()
    for _ in range(40):
        x, _y, _meta, m = dh[0]
        fx, fm = not torch.equal(x, base_x), not torch.equal(m, base_m)
        assert fx == fm, "image and mask must flip together"
        if fm:
            assert torch.equal(m, torch.flip(base_m, dims=[-1])), "mask flip must be a plain flip"
        combos.add(fx)
    assert combos == {True, False}, f"both hflip outcomes must be reachable: {combos}"

    try:                                          # a wrong dir must fail loudly, not silently
        PolarGridDataset(man, sp, "train", "rgb", img_size=S, grid=grid,
                         aux_mask_dir=os.path.join(os.path.dirname(mdir), "img"))
        raise SystemExit("[RED] a stem-mismatched aux_mask_dir was accepted")
    except RuntimeError as e:
        assert "matches 0 of" in str(e), e
    print(f"    [DATA] 4 train frames: {seen_pos} masked / {seen_zero} missing-as-zeros; "
          f"mask {tuple(base_m.shape)} in {{0,1}}; hflip couples x<->mask; empty dir rejected")


# --------------------------------------------------------------------- 4/5. train runs
def train(tmp, man, sp, grid_arg, tag, extra):
    out = os.path.join(tmp, f"run_{tag}")
    log = SM.run(f"train_polar [{tag}]",
                 ["train_polar.py", "--manifest", man, "--split", sp, "--input", "rgb",
                  "--out", out, "--smoke", 10, "--img-size", 64, "--batch", 2, "--workers", 0,
                  "--max-epochs", 5, "--patience", 5, "--hflip", "on",
                  "--bias-init", "prior"] + grid_arg + extra)
    for f in ("best.pt", "last.pt", "config.json", "metrics.csv"):
        assert os.path.exists(os.path.join(out, f)), f"{tag}: missing {f}"
    return out, log, json.load(open(os.path.join(out, "config.json")))


def main():
    tmp = tempfile.mkdtemp(prefix="polar_aux_smoke_")
    print(f"[smoke-aux] workdir {tmp}")
    ok = False
    try:
        fake = os.path.join(tmp, "gridspec_v1_fake.json")
        json.dump(SM.FAKE_V1, open(fake, "w"), indent=1)
        grid, garg = gridspec.load(fake), ["--grid", fake]
        assert grid.n_cells == 20

        hdr("1. model_factory use_mask_head")
        check_model(grid.n_cells)
        hdr("2. mask filename contract")
        check_stem()
        man, sp, mdir, written = build_ws(tmp, grid)
        print(f"    [FIXTURE] masks written: {written}")
        hdr("3. PolarGridDataset(aux_mask_dir=...)")
        check_dataset(man, sp, mdir, grid)

        hdr("4. train_polar WITH aux")
        aout, alog, acfg = train(tmp, man, sp, garg, "aux",
                                 ["--aux-mask-dir", mdir, "--aux-lambda", LAM])
        assert "[aux] pixel BCE ON" in alog and "masks 2 found / 2 missing-as-empty" in alog, alog
        arows = list(csv.DictReader(open(os.path.join(aout, "metrics.csv"))))
        ahead = open(os.path.join(aout, "metrics.csv")).readline().strip().split(",")
        assert ahead == BASE_HEADER + ["train_loss_cell", "train_loss_aux"], ahead
        for r in arows:
            c, x, t = (float(r["train_loss_cell"]), float(r["train_loss_aux"]),
                       float(r["train_loss"]))
            assert all(math.isfinite(v) for v in (c, x, t)), r
            assert c > 0 and x > 0, r
            assert abs(t - (c + LAM * x)) < 1e-5, (t, c, x, "total != cell + lambda*aux")
        assert acfg["aux_enabled"] is True and acfg["aux_lambda"] == LAM
        assert acfg["aux_masks_found"] == 2 and acfg["aux_masks_missing_as_empty"] == 2
        assert acfg["aux_mask_dir"] == mdir and "CELL-ONLY" in acfg["aux_val_note"]
        assert math.isfinite(float(acfg["best_sel_score"]))
        print(f"    [AUX] rows={len(arows)} ep1 total {arows[0]['train_loss']} = cell "
              f"{arows[0]['train_loss_cell']} + {LAM}*aux {arows[0]['train_loss_aux']}; "
              f"sel={acfg['best_sel_score']:.4f}")

        hdr("4b. the aux checkpoint loads into the UNCHANGED eval path")
        ev = os.path.join(tmp, "eval_aux")
        SM.run("eval_polar [aux ckpt]",
               ["eval_polar.py", "--manifest", man, "--split", sp, "--subset", "test",
                "--ckpt", f"{aout}/best.pt", "--input", "rgb", "--out", ev, "--tau-op", 0.5,
                "--tau-star", "auto", "--img-size", 64, "--batch", 2, "--workers", 0,
                "--n-boot", 50] + garg)
        M = json.load(open(f"{ev}/metrics.json"))
        assert M["counts"]["n_cells"] == grid.n_cells
        print(f"    [EVAL] aux best.pt -> cell_f1={M['point']['op']['cell_f1']:.4f} "
              f"frame_det_rate={M['point']['op']['frame_det_rate']:.4f} (no eval_polar change)")

        hdr("5. DEFAULT-OFF regression: same command WITHOUT the aux flags")
        nout, nlog, ncfg = train(tmp, man, sp, garg, "noaux", [])
        assert "[aux]" not in nlog, "an aux line leaked into a non-aux run"
        nhead = open(os.path.join(nout, "metrics.csv")).readline().strip().split(",")
        assert nhead == BASE_HEADER, nhead
        assert not (set(ncfg) & AUX_CFG_KEYS), sorted(set(ncfg) & AUX_CFG_KEYS)
        assert set(acfg) - set(ncfg) == AUX_CFG_KEYS, sorted(set(acfg) - set(ncfg))
        assert set(ncfg) - set(acfg) == set(), sorted(set(ncfg) - set(acfg))
        print(f"    [OFF] config keys: aux \\ no-aux == {sorted(AUX_CFG_KEYS)} and nothing else; "
              f"metrics.csv header unchanged ({len(nhead)} cols)")

        real_cfg = os.path.join(REAL_RUN, "config.json")
        real_csv = os.path.join(REAL_RUN, "metrics.csv")
        if os.path.exists(real_cfg) and os.path.exists(real_csv):
            rk = set(json.load(open(real_cfg)))
            assert rk == set(ncfg), f"drift vs the real v2 run: {sorted(rk ^ set(ncfg))}"
            assert open(real_csv).readline().strip().split(",") == nhead
            print(f"    [OFF] byte-identical key set / csv header vs the REAL pre-change run "
                  f"{os.path.relpath(REAL_RUN, EXPS)} ({len(rk)} keys)")
        else:
            print(f"    [OFF] (skipped: {REAL_RUN} has no config.json/metrics.csv to compare)")
        ok = True
    finally:
        if ok:
            shutil.rmtree(tmp, ignore_errors=True)
            print("\n[SMOKE-AUX GREEN] model + dataset + train(aux) + train(no-aux) all pass")
        else:
            print(f"\n[SMOKE-AUX RED] artefacts kept at {tmp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
