"""U-Net(resnet34) + smp aux classification head -> [B,15] polar-cell logits.

Verified on CPU in env_seg (smp 0.5.0, torch 2.5.1+cu124), 2026-08-19:
  * classification_head == AdaptiveAvgPool2d(1) -> Flatten -> Dropout(0.2) -> Linear(512,15) -> Identity
  * params 24.444 M (same as the campaign unet-r34, so its 512^2/batch8 timing+VRAM numbers transfer)
  * in_channels=1 goes through encoder.set_in_channels(pretrained=True): conv1 weight becomes the
    SUM of the pretrained RGB kernels (checked torch.allclose(w1[:,0], w3.sum(1)) -> True),
    i.e. it is re-weighted, not randomly re-initialised.
"""
from __future__ import annotations

import segmentation_models_pytorch as smp
import torch.nn as nn

N_CELLS = 15
ENCODER = "resnet34"


class PolarNet(nn.Module):
    """Wrapper that returns ONLY the [B,15] logits; the dense mask output is discarded."""

    def __init__(self, in_channels: int, classes: int = N_CELLS, encoder_weights="imagenet",
                 dropout: float = 0.2):
        super().__init__()
        self.in_channels = in_channels
        self.net = smp.Unet(
            ENCODER,
            encoder_weights=encoder_weights,
            in_channels=in_channels,
            classes=1,  # dense head kept (cheap seam for a later auxiliary dense target), unused
            aux_params=dict(classes=classes, pooling="avg", dropout=dropout, activation=None),
        )

    def forward(self, x):
        _mask, logits = self.net(x)  # activation=None -> raw logits for BCEWithLogitsLoss
        return logits

    def encoder_parameters(self):
        return self.net.encoder.parameters()


def build(input_mode: str, encoder_weights="imagenet", dropout: float = 0.2) -> PolarNet:
    if input_mode not in ("rgb", "depth"):
        raise ValueError(f"input_mode must be 'rgb' or 'depth', got {input_mode!r}")
    return PolarNet(3 if input_mode == "rgb" else 1, encoder_weights=encoder_weights, dropout=dropout)


if __name__ == "__main__":  # CPU self-check
    import torch

    for mode, ch in (("rgb", 3), ("depth", 1)):
        m = build(mode, encoder_weights=None).eval()
        out = m(torch.randn(2, ch, 64, 64))
        assert out.shape == (2, 15), out.shape
        print(f"{mode:5s} in_ch={m.net.encoder.conv1.in_channels} out={tuple(out.shape)} "
              f"params={sum(p.numel() for p in m.parameters())/1e6:.3f}M")
