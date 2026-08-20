"""Polar hazard-grid dataset: monocular frame -> N binary cells (n_sectors x n_bands).

Cell ordering (FIXED, matches the manifest contract, read from a gridspec json — see gridspec.py):
    index = band * n_sectors + sector ;  band 0 = nearest ; sector 0 = image-left
Human-readable id: sector name + band name  (V0: "C2" = index 7 of 15; V1: "C2" = index 7 of 20).

Nothing here hard-codes the cell count. The module-level N_* constants are the **V0 defaults**,
kept so pre-0820 callers/imports keep working; every class and function takes an explicit
`grid=` (a gridspec.Grid, a path, or a bare "gridspec_v1.json").

Run everything with PYTHONNOUSERSITE=1 (this machine's ~/.local shadows env_seg).
"""
from __future__ import annotations

import io
import json
import os
import sys

import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gridspec  # noqa: E402

DEFAULT_GRID = gridspec.load(None)          # V0 (15 cells) — backwards compatibility only
N_SECTORS, N_BANDS = DEFAULT_GRID.n_sectors, DEFAULT_GRID.n_bands
N_CELLS = DEFAULT_GRID.n_cells
IMG_SIZE = 512

# campaign common.py:109-110 (matches the smp resnet34 imagenet encoder weights)
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)

# depth normalisation: clip to [0, DEPTH_CLIP_M] metres then divide -> [0,1]
DEPTH_CLIP_M = 10.0
# uint16 PNG depth is assumed to be millimetres (render side decides; change here if not)
DEPTH_PNG16_SCALE = 1e-3

CELL_IDS = list(DEFAULT_GRID.cell_ids)
BAND_OF = list(DEFAULT_GRID.band_of)
SECTOR_OF = list(DEFAULT_GRID.sector_of)


# --------------------------------------------------------------------------- flip
def flip_perm(grid=None) -> list:
    """Index map for a horizontal image flip: new[i] = old[flip_perm()[i]] (involution).

    Sectors are reversed inside each band ([4,3,2,1,0] for 5 sectors); the band order is
    unchanged, so the permutation is exactly `band*ns + (ns-1-sector)` for ANY n_bands.
    """
    return (grid if isinstance(grid, gridspec.Grid) else
            (DEFAULT_GRID if grid is None else gridspec.load(grid))).flip_perm()


def flip_with_permutation(x: torch.Tensor, y: torch.Tensor, grid=None):
    """Horizontal flip of the image AND the matching sector permutation of the N-cell label.

    x: [...,C,H,W]  y: [...,n_cells]   (grid=None -> the V0 15-cell default)
    """
    perm = torch.as_tensor(flip_perm(grid), dtype=torch.long, device=y.device)
    if y.shape[-1] != perm.numel():
        raise ValueError(f"label has {y.shape[-1]} cells but the grid has {perm.numel()}")
    return torch.flip(x, dims=[-1]), y.index_select(-1, perm)


# --------------------------------------------------------------------------- depth io
def _load_exr(path: str) -> np.ndarray:
    try:
        import imageio.v3 as iio  # not installed in env_seg as of 08-19
        return np.asarray(iio.imread(path), dtype=np.float32)
    except ImportError:
        pass
    try:
        os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")
        import cv2  # cv2 5.0.0 IS in env_seg; only imported for EXR
        a = cv2.imread(path, cv2.IMREAD_UNCHANGED | cv2.IMREAD_ANYDEPTH)
        if a is None:
            raise RuntimeError(f"cv2 returned None for {path}")
        return np.asarray(a, dtype=np.float32)
    except ImportError:
        pass
    raise NotImplementedError(
        "EXR depth requested but neither imageio nor OpenEXR nor cv2-with-EXR is usable. "
        "Install imageio, or have the render side emit PNG16 / .npy depth instead."
    )


def load_depth_m(path: str) -> np.ndarray:
    """Return HxW float32 depth in METRES. Auto-dispatch on extension."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".npy":
        a = np.load(path).astype(np.float32)
    elif ext == ".exr":
        a = _load_exr(path)
    elif ext in (".png", ".tif", ".tiff"):
        im = Image.open(path)
        a = np.array(im)
        if a.dtype == np.uint16:
            a = a.astype(np.float32) * DEPTH_PNG16_SCALE
        elif a.dtype == np.uint8:
            a = a.astype(np.float32) / 255.0 * DEPTH_CLIP_M  # 8-bit = already range-compressed
        else:  # int32 / float PNG-TIFF
            a = a.astype(np.float32)
            if im.mode in ("I", "I;16", "I;16B", "I;16L"):
                a = a * DEPTH_PNG16_SCALE
    else:
        raise ValueError(f"unsupported depth extension {ext!r} for {path}")
    if a.ndim == 3:
        a = a[..., 0]
    return np.ascontiguousarray(a, dtype=np.float32)


# --------------------------------------------------------------------------- aux mask io
def aux_mask_stem(frame_id: str) -> str:
    """'on/scene04/L0__x__0000.png[::round]' -> 'on__scene04__L0__x__0000[__round]'.

    Byte-for-byte the same rule as `stem_of` in experiments/dayrun_0820/code/yolo/common.py
    (that module is the owner; it is replicated here rather than imported so the mainrun
    training stack keeps ZERO dependency on the dayrun YOLO track, which drags in labeler.py).
    Any change there must be mirrored here — smoke_aux.py asserts the two agree.
    """
    arm, scene, fn = frame_id.split("/", 2)
    fn = fn.split("::", 1)[0]                                   # strip the D24 round token ...
    suf = "__" + frame_id.split("::", 1)[1] if "::" in frame_id else ""   # ... and re-attach it
    return f"{arm}__{scene}__{os.path.splitext(fn)[0]}{suf}"


def aux_mask_path(aux_mask_dir: str, frame_id: str) -> str:
    return os.path.join(aux_mask_dir, aux_mask_stem(frame_id) + ".png")


def load_aux_mask(path: str, size: int) -> torch.Tensor:
    """Amodal mask PNG -> [1,size,size] float 0/1. A MISSING file is the legitimate empty mask
    (off-arm frames and on-arm frames with no hazard in FOV get no PNG) -> zeros."""
    if not path or not os.path.exists(path):
        return torch.zeros(1, size, size, dtype=torch.float32)
    im = Image.open(path).convert("L").resize((size, size), Image.NEAREST)  # NEAREST: keep binary
    a = (np.asarray(im, np.uint8) > 127).astype(np.float32)
    return torch.from_numpy(np.ascontiguousarray(a))[None]


# --------------------------------------------------------------------------- aug
def load_aug_config(path):
    if not path:
        return None
    import yaml
    with open(path) as f:
        cfg = yaml.safe_load(f) or {}
    return cfg


def _apply_photometric(img: Image.Image, cfg, rng: np.random.Generator) -> Image.Image:
    """Mild photometric jitter on a PIL RGB image. cfg=None -> the built-in mild default."""
    from torchvision import transforms as T

    cfg = cfg or {}
    cj = cfg.get("color_jitter", {})
    if cfg and not cj.get("enabled", False):
        jit = None
    else:
        jit = T.ColorJitter(
            brightness=cj.get("brightness", 0.2),
            contrast=cj.get("contrast", 0.2),
            saturation=cj.get("saturation", 0.2),
            hue=cj.get("hue", 0.02),
        )
    if jit is not None:
        img = jit(img)
    gn = cfg.get("gaussian_noise", {})
    if gn.get("enabled", False):
        a = np.asarray(img, np.float32)
        a += rng.normal(0.0, float(gn.get("sigma", 4.0)), a.shape).astype(np.float32)
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    jp = cfg.get("jpeg", {})
    if jp.get("enabled", False):
        q = int(rng.integers(int(jp.get("q_min", 70)), int(jp.get("q_max", 95)) + 1))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=q)
        buf.seek(0)
        img = Image.open(buf).convert("RGB")
    return img


# --------------------------------------------------------------------------- dataset
class PolarGridDataset(Dataset):
    """(x, y[n_cells], meta) for one split subset of a dataset manifest.

    Resize is a SQUASH to img_size x img_size (aspect not preserved) -- campaign-wide convention.
    train_aug   photometric-only, RGB-only (depth is left alone).
    train_hflip horizontal flip + sector permutation, p=0.5, BOTH arms (geometric, so valid for
                depth too). The coin is drawn from torch's per-worker RNG, which the DataLoader
                reseeds every epoch -> genuinely random across epochs and reproducible from
                --seed. Off by default here; train_polar.py turns it on (--hflip on).
    aux_mask_dir 0820 Phase 6, default None = OFF. When set, __getitem__ yields a FOUR-tuple
                (x, y, meta, mask[1,S,S]) instead of the usual three — the extra tensor is the
                amodal mask of the frame (<dir>/<aux_mask_stem>.png, missing file = all-zeros),
                resized to img_size and flipped together with x when hflip fires. The arity is
                conditional on purpose: every pre-0820 caller unpacks `x, y, meta`.
    """

    def __init__(self, manifest_path, split_file, subset, input_mode="rgb",
                 train_aug=False, img_size=IMG_SIZE, aug_config=None, seed=42,
                 grid=None, train_hflip=False, hflip_p=0.5, aux_mask_dir=None):
        assert input_mode in ("rgb", "depth")
        self.grid = grid if isinstance(grid, gridspec.Grid) else (
            DEFAULT_GRID if grid is None else gridspec.load(grid))
        self.n_cells = self.grid.n_cells
        with open(manifest_path) as f:
            man = json.load(f)
        with open(split_file) as f:
            split = json.load(f)
        if subset not in split:
            raise KeyError(f"subset {subset!r} not in split file (have {list(split)})")
        keep = set(split[subset])

        self.meta_global = man.get("meta", {})
        self.input_mode, self.img_size = input_mode, img_size
        self.train_aug = bool(train_aug) and input_mode == "rgb"
        self.train_hflip = bool(train_hflip)
        self.hflip_p = float(hflip_p)
        self._flip_perm = torch.as_tensor(self.grid.flip_perm(), dtype=torch.long)
        self.aug_cfg = aug_config if isinstance(aug_config, dict) else load_aug_config(aug_config)
        self.seed = seed
        self.n_dropped_no_depth = 0
        self.aux_mask_dir = str(aux_mask_dir) if aux_mask_dir else None
        self.n_aux_found = self.n_aux_missing = 0

        self.items = []
        for r in man["frames"]:
            if r["scene_id"] not in keep:
                continue
            if input_mode == "depth" and not r.get("depth"):
                self.n_dropped_no_depth += 1
                continue
            self.items.append(r)
        if not self.items:
            raise RuntimeError(f"empty subset {subset!r} for input_mode={input_mode!r}")
        # fail loudly rather than train against a manifest labelled on another grid
        n0 = len(self.items[0]["polar_gt"])
        if n0 != self.n_cells:
            raise AssertionError(
                f"GRID MISMATCH: manifest polar_gt has {n0} cells "
                f"(meta.grid_version={self.meta_global.get('grid_version')!r}) but the grid "
                f"{self.grid.version} ({self.grid.path}) has {self.n_cells}.")

        if self.aux_mask_dir is not None:
            if not os.path.isdir(self.aux_mask_dir):
                raise FileNotFoundError(f"aux_mask_dir not found: {self.aux_mask_dir}")
            # census up front (workers cannot report counters back to the parent process)
            for r in self.items:
                hit = os.path.exists(aux_mask_path(self.aux_mask_dir, str(r["frame_id"])))
                self.n_aux_found += hit
                self.n_aux_missing += not hit
            if self.n_aux_found == 0:
                raise RuntimeError(
                    f"aux_mask_dir {self.aux_mask_dir!r} matches 0 of {len(self.items)} "
                    f"{subset!r} frames — stem convention mismatch (expected e.g. "
                    f"{aux_mask_stem(str(self.items[0]['frame_id']))}.png)")

    def __len__(self):
        return len(self.items)

    def positive_rate(self):
        """Per-cell positive rate over this subset -> np.float64[n_cells] (bias-prior source)."""
        g = np.asarray([r["polar_gt"] for r in self.items], dtype=np.float64)
        return g.mean(axis=0) if len(g) else np.zeros(self.n_cells)

    def tiers(self):
        return [str(r.get("tier") or "none") for r in self.items]

    def _load_x(self, rec, idx):
        S = self.img_size
        if self.input_mode == "rgb":
            img = Image.open(rec["rgb"]).convert("RGB").resize((S, S), Image.BILINEAR)
            if self.train_aug:
                rng = np.random.default_rng(self.seed * 1_000_003 + idx)
                img = _apply_photometric(img, self.aug_cfg, rng)
            a = np.asarray(img, np.float32) / 255.0
            a = (a - np.array(IMAGENET_MEAN, np.float32)) / np.array(IMAGENET_STD, np.float32)
            return torch.from_numpy(np.ascontiguousarray(a.transpose(2, 0, 1)))
        d = load_depth_m(rec["depth"])
        d = np.asarray(Image.fromarray(d, mode="F").resize((S, S), Image.BILINEAR), np.float32)
        d = np.clip(d, 0.0, DEPTH_CLIP_M) / DEPTH_CLIP_M
        return torch.from_numpy(d)[None]

    def __getitem__(self, i):
        rec = self.items[i]
        x = self._load_x(rec, i)
        gt = rec["polar_gt"]
        assert len(gt) == self.n_cells, \
            f"{rec['frame_id']}: polar_gt has {len(gt)} != {self.n_cells} ({self.grid.version})"
        y = torch.tensor(gt, dtype=torch.float32)
        # ONE coin, drawn exactly where it was before -> the aux path does not perturb the RNG
        do_flip = self.train_hflip and float(torch.rand(())) < self.hflip_p
        if do_flip:
            x = torch.flip(x, dims=[-1])
            y = y.index_select(-1, self._flip_perm)
        meta = {
            "frame_id": str(rec["frame_id"]),
            "scene_id": str(rec["scene_id"]),
            "tier": str(rec.get("tier") or "none"),
            "toggle_state": str(rec.get("toggle_state") or "none"),
        }
        if self.aux_mask_dir is None:
            return x, y, meta
        m = load_aux_mask(aux_mask_path(self.aux_mask_dir, meta["frame_id"]), self.img_size)
        if do_flip:                      # the mask is an image: it flips WITH x, no permutation
            m = torch.flip(m, dims=[-1])
        return x, y, meta, m
