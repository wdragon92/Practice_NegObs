"""Polar hazard-grid dataset: monocular frame -> 15 binary cells (5 sectors x 3 bands).

Cell ordering (FIXED, matches the manifest contract):
    index = band * 5 + sector ;  band 0=near,1=mid,2=far ; sector 0=leftmost .. 4=rightmost
Human-readable id: sector letter A..E + band number 1..3  (e.g. index 7 -> "C2").

Run everything with PYTHONNOUSERSITE=1 (this machine's ~/.local shadows env_seg).
"""
from __future__ import annotations

import io
import json
import os

import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset

N_SECTORS, N_BANDS = 5, 3
N_CELLS = N_SECTORS * N_BANDS
IMG_SIZE = 512

# campaign common.py:109-110 (matches the smp resnet34 imagenet encoder weights)
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)

# depth normalisation: clip to [0, DEPTH_CLIP_M] metres then divide -> [0,1]
DEPTH_CLIP_M = 10.0
# uint16 PNG depth is assumed to be millimetres (render side decides; change here if not)
DEPTH_PNG16_SCALE = 1e-3

CELL_IDS = ["ABCDE"[i % N_SECTORS] + str(i // N_SECTORS + 1) for i in range(N_CELLS)]
BAND_OF = [i // N_SECTORS for i in range(N_CELLS)]
SECTOR_OF = [i % N_SECTORS for i in range(N_CELLS)]


# --------------------------------------------------------------------------- flip
def flip_perm() -> list:
    """Index map for a horizontal image flip: new[i] = old[flip_perm()[i]] (involution)."""
    return [b * N_SECTORS + (N_SECTORS - 1 - s) for b in range(N_BANDS) for s in range(N_SECTORS)]


def flip_with_permutation(x: torch.Tensor, y: torch.Tensor):
    """Horizontal flip of the image AND the matching sector permutation of the 15-cell label.

    OFF by default (train_aug never calls this) -- kept + unit-tested so a later run can enable it.
    x: [...,C,H,W]  y: [...,15]
    """
    perm = torch.as_tensor(flip_perm(), dtype=torch.long, device=y.device)
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
    """(x, y[15], meta) for one split subset of dataset_manifest_v1.json.

    Resize is a SQUASH to img_size x img_size (aspect not preserved) -- campaign-wide convention.
    train_aug is photometric-only and RGB-only; there is NO horizontal flip (see flip_with_permutation).
    """

    def __init__(self, manifest_path, split_file, subset, input_mode="rgb",
                 train_aug=False, img_size=IMG_SIZE, aug_config=None, seed=42):
        assert input_mode in ("rgb", "depth")
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
        self.aug_cfg = aug_config if isinstance(aug_config, dict) else load_aug_config(aug_config)
        self.seed = seed
        self.n_dropped_no_depth = 0

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

    def __len__(self):
        return len(self.items)

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
        assert len(gt) == N_CELLS, f"{rec['frame_id']}: polar_gt has {len(gt)} != {N_CELLS}"
        y = torch.tensor(gt, dtype=torch.float32)
        meta = {
            "frame_id": str(rec["frame_id"]),
            "scene_id": str(rec["scene_id"]),
            "tier": str(rec.get("tier") or "none"),
            "toggle_state": str(rec.get("toggle_state") or "none"),
        }
        return x, y, meta
