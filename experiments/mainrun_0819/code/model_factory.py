"""U-Net(any smp encoder, default resnet34) + smp aux classification head -> [B,n_cells] logits.

`classes` comes from the gridspec (15 on V0, 20 on V1) — nothing here hard-codes a cell count.

ENCODER AXIS (0823 D45, `build(..., encoder_name=...)` / `train_polar.py --encoder`):
  the encoder is now a parameter, default "resnet34" so every pre-0823 caller is unchanged
  (identical graph, identical state_dict keys, identical param count). Any smp encoder name
  works, including timm-universal "tu-*" ones — smp maps `encoder_weights="imagenet"` to
  timm's `pretrained=True` (get_encoder: `pretrained=weights is not None`), so the same
  "imagenet" string is correct for both families. CPU-verified 2026-08-23 (smp 0.5.0):
    resnet34         24.447 M   tu-convnext_tiny 31.944 M   resnet50 32.562 M   (classes=20)
  A checkpoint records its encoder in config["encoder"] as f"{name}-unet-aux"; read it back
  with `encoder_from_config()` (eval_polar / infer_photo do) so inference rebuilds the RIGHT
  backbone instead of a resnet34 that would blow up on load_state_dict.

Verified on CPU in env_seg (smp 0.5.0, torch 2.5.1+cu124), 2026-08-19:
  * classification_head == AdaptiveAvgPool2d(1) -> Flatten -> Dropout(0.2) -> Linear(512,C) -> Identity
  * params 24.444 M at C=15 (same as the campaign unet-r34, so its 512^2/batch8 timing+VRAM
    numbers transfer); C=20 adds 5*513 = 2565 params, i.e. nothing.
  * in_channels=1 goes through encoder.set_in_channels(pretrained=True): conv1 weight becomes the
    SUM of the pretrained RGB kernels (checked torch.allclose(w1[:,0], w3.sum(1)) -> True),
    i.e. it is re-weighted, not randomly re-initialised.
"""
from __future__ import annotations

import os
import sys

import segmentation_models_pytorch as smp
import torch.nn as nn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gridspec  # noqa: E402

N_CELLS = gridspec.load(None).n_cells       # V0 default (15) — explicit `classes=` overrides it
ENCODER = "resnet34"
CONFIG_SUFFIX = "-unet-aux"                 # config["encoder"] == f"{encoder_name}{CONFIG_SUFFIX}"


def config_encoder_label(encoder_name: str = ENCODER) -> str:
    """The string train_polar writes to config["encoder"] ("resnet34-unet-aux" on the default)."""
    return f"{encoder_name}{CONFIG_SUFFIX}"


def encoder_from_config(cfg, default: str = ENCODER) -> str:
    """Inverse of config_encoder_label: pull the smp encoder name out of a run/ckpt config.

    Tolerates a bare name, the labelled form, a missing key and a non-dict — anything this
    cannot resolve to a plausible smp encoder name falls back to `default` (resnet34), which
    is exactly the pre-0823 behaviour, so old checkpoints and the b2 bridge are untouched.
    """
    if not isinstance(cfg, dict):
        return default
    v = cfg.get("encoder")
    if not isinstance(v, str) or not v.strip():
        return default
    v = v.strip()
    if v.endswith(CONFIG_SUFFIX):
        v = v[: -len(CONFIG_SUFFIX)]
    return v or default


class PolarNet(nn.Module):
    """Returns ONLY the [B,classes] logits by default; the dense mask output is discarded.

    `use_mask_head=True` (0820 Phase 6, aux pixel loss) keeps that dense output and makes forward
    return the PAIR ``(logits[B,classes], mask_logits[B,1,H,W])``. It flips nothing else: the
    module graph, the parameter count and therefore the state_dict keys are IDENTICAL either way
    (the decoder + segmentation_head are always built, they simply receive no gradient when the
    aux loss is off), so an aux-trained checkpoint loads into the plain logits-only model that
    eval_polar.py / infer_photo.py build, with no flag to thread through.
    """

    def __init__(self, in_channels: int, classes: int = N_CELLS, encoder_weights="imagenet",
                 dropout: float = 0.2, use_mask_head: bool = False, encoder_name: str = ENCODER):
        super().__init__()
        self.in_channels = in_channels
        self.classes = int(classes)
        self.use_mask_head = bool(use_mask_head)
        self.encoder_name = str(encoder_name)
        self.net = smp.Unet(
            self.encoder_name,
            encoder_weights=encoder_weights,
            in_channels=in_channels,
            classes=1,  # dense head kept (the seam the aux pixel target plugs into; see above)
            aux_params=dict(classes=self.classes, pooling="avg", dropout=dropout, activation=None),
        )

    def forward(self, x):
        mask, logits = self.net(x)  # activation=None -> raw logits for BCEWithLogitsLoss
        return (logits, mask) if self.use_mask_head else logits

    def encoder_parameters(self):
        return self.net.encoder.parameters()

    def final_classifier(self):
        """The module whose bias the prior-init writes to (see train_polar.set_prior_bias)."""
        return self.net.classification_head[3]


def build(input_mode: str, encoder_weights="imagenet", dropout: float = 0.2,
          classes: int | None = None, grid=None, use_mask_head: bool = False,
          encoder_name: str = ENCODER) -> PolarNet:
    """classes wins if given; else grid.n_cells; else the V0 default (15).

    use_mask_head=False (default) -> forward(x) -> logits            [every pre-0820 caller]
    use_mask_head=True            -> forward(x) -> (logits, mask_logits)  [aux pixel loss only]
    encoder_name  (default resnet34) -> any smp encoder, incl. timm-universal "tu-*"  [0823 D45]
    """
    if input_mode not in ("rgb", "depth"):
        raise ValueError(f"input_mode must be 'rgb' or 'depth', got {input_mode!r}")
    if classes is None:
        classes = gridspec.load(grid).n_cells if grid is not None else N_CELLS
    return PolarNet(3 if input_mode == "rgb" else 1, classes=int(classes),
                    encoder_weights=encoder_weights, dropout=dropout,
                    use_mask_head=use_mask_head, encoder_name=encoder_name)


if __name__ == "__main__":  # CPU self-check:  python model_factory.py [n_cells] [encoder]
    import torch

    n = int(sys.argv[1]) if len(sys.argv) > 1 else N_CELLS
    enc = sys.argv[2] if len(sys.argv) > 2 else ENCODER
    assert encoder_from_config({"encoder": config_encoder_label(enc)}) == enc, "label round-trip"
    for mode, ch in (("rgb", 3), ("depth", 1)):
        m = build(mode, encoder_weights=None, classes=n, encoder_name=enc).eval()
        out = m(torch.randn(2, ch, 64, 64))
        assert out.shape == (2, n), out.shape
        assert m.final_classifier().out_features == n
        stem = getattr(m.net.encoder, "conv1", None)      # resnet-only attribute
        in_ch = getattr(stem, "in_channels", m.in_channels)
        print(f"{enc} {mode:5s} in_ch={in_ch} out={tuple(out.shape)} "
              f"params={sum(p.numel() for p in m.parameters())/1e6:.3f}M")

        ma = build(mode, encoder_weights=None, classes=n, use_mask_head=True,
                   encoder_name=enc).eval()
        lo, mk = ma(torch.randn(2, ch, 64, 64))
        assert lo.shape == (2, n) and mk.shape == (2, 1, 64, 64), (lo.shape, mk.shape)
        assert list(ma.state_dict()) == list(m.state_dict()), "mask head must not change the graph"
        print(f"{'':5s} use_mask_head=True -> logits{tuple(lo.shape)} + mask{tuple(mk.shape)} "
              f"params={sum(p.numel() for p in ma.parameters())/1e6:.3f}M (state_dict identical)")
