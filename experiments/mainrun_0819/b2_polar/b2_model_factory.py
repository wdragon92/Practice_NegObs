"""SegFormer-B2 (MiT-B2 encoder) -> [B,15] polar-cell logits. Drop-in twin of code/model_factory.py.

Same contract as code/model_factory.py so train_polar.py needs no edits:
    build(input_mode) -> nn.Module ; forward([B,C,512,512]) -> [B,15] raw logits (BCEWithLogitsLoss)

Route A (default, HARNESS_NOTES §6 option (ii), verified in env_seg 2026-08-19):
    SegformerForImageClassification.from_pretrained(<hf_local>/nvidia__mit-b2, num_labels=15,
        problem_type="multi_label_classification", ignore_mismatched_sizes=True,
        local_files_only=True)
    = MiT-B2 encoder + mean-pool over tokens + Linear(512,15).  24.204 M params.
    Only classifier.{weight,bias} are re-initialised (ckpt is the 1000-class ImageNet head);
    every encoder tensor loads.  NOTE: the hidden width is 512, not the 768 quoted in
    HARNESS_NOTES §6 — mit-b2's last-stage hidden_sizes entry is 512.

Route B (automatic fallback, HARNESS_NOTES §6 option (i)):
    campaign harness common.build_model("segformer-b2", 15) -> dense [B,15,H,W], then
    logits = seg_logits.mean(dim=(2,3)).  Costs the decode head's FLOPs (27.37 M params).
    Used only if route A's import/from_pretrained raises.  ensure_safetensors() is bypassed
    (it calls list_repo_files -> network); we hand SegformerForSemanticSegmentation the same
    local dir with local_files_only=True.

WEIGHTS ARE LOADED OFFLINE. Both routes pass local_files_only=True and read only
    /home/vislab/Desktop/work_sy/Practice_Segmentation/campaign/data/hf_local/nvidia__mit-b2
transformers 5.15 refuses .bin on torch 2.5.1 (CVE-2025-32434) — that local dir is the
already-converted safetensors copy. DO NOT upgrade torch to "fix" a load error.

input_mode: "rgb" -> 3ch as-is. "depth" -> the 1ch tensor is repeated to 3ch before the stem
(the MiT patch-embed stays pretrained; smp's set_in_channels channel-sum trick has no
transformers equivalent). The B2 arm is an RGB arm; depth is supported only for CLI parity.

Run everything with PYTHONNOUSERSITE=1 (this machine's ~/.local shadows env_seg).
"""
from __future__ import annotations

import os

import torch
import torch.nn as nn

N_CELLS = 15
IMG_SIZE = 512

LOCAL_MIT_B2 = ("/home/vislab/Desktop/work_sy/Practice_Segmentation/campaign/data/hf_local/"
                "nvidia__mit-b2")
CAMPAIGN_HARNESS = "/home/vislab/Desktop/work_sy/Practice_Segmentation/campaign/harness"


class B2PolarNet(nn.Module):
    """Wrapper that returns ONLY the [B,15] logits, whichever route built the backbone."""

    def __init__(self, net, in_channels: int, route: str, pool_dense: bool):
        super().__init__()
        self.net = net
        self.in_channels = in_channels
        self.route = route            # "imgcls" (A) | "semseg-gap" (B)
        self.pool_dense = pool_dense  # route B needs the spatial mean

    def forward(self, x):
        if self.in_channels == 1 and x.shape[1] == 1:
            x = x.expand(-1, 3, -1, -1)
        out = self.net(pixel_values=x)
        logits = out.logits
        if self.pool_dense:
            logits = logits.mean(dim=(2, 3))   # [B,15,H,W] -> [B,15]
        return logits

    def encoder_parameters(self):
        enc = getattr(self.net, "segformer", None)
        return (enc if enc is not None else self.net).parameters()


def _build_imgcls(classes: int, pretrained: bool):
    """Route A."""
    from transformers import SegformerConfig, SegformerForImageClassification

    kw = dict(num_labels=classes, problem_type="multi_label_classification")
    if pretrained:
        net = SegformerForImageClassification.from_pretrained(
            LOCAL_MIT_B2, ignore_mismatched_sizes=True, local_files_only=True, **kw)
    else:
        cfg = SegformerConfig.from_pretrained(LOCAL_MIT_B2, local_files_only=True, **kw)
        net = SegformerForImageClassification(cfg)
    return net


def _build_semseg_gap(classes: int, pretrained: bool):
    """Route B — same construction as campaign common.build_model('segformer-b2', n)."""
    import sys

    if CAMPAIGN_HARNESS not in sys.path:
        sys.path.insert(0, CAMPAIGN_HARNESS)
    from transformers import SegformerConfig, SegformerForSemanticSegmentation

    if pretrained:
        net = SegformerForSemanticSegmentation.from_pretrained(
            LOCAL_MIT_B2, num_labels=classes, ignore_mismatched_sizes=True,
            local_files_only=True)
    else:
        cfg = SegformerConfig.from_pretrained(LOCAL_MIT_B2, num_labels=classes,
                                              local_files_only=True)
        net = SegformerForSemanticSegmentation(cfg)
    return net


def build(input_mode: str = "rgb", encoder_weights="imagenet", dropout: float = 0.0,
          classes: int = N_CELLS, force_route: str | None = None) -> B2PolarNet:
    """encoder_weights: "imagenet" -> load the local mit-b2 checkpoint; None -> config only.

    `dropout` is accepted for signature parity with code/model_factory.py; SegFormer's dropout
    lives in the config (classifier_dropout_prob) and is left at the checkpoint default, so a
    non-zero value here is applied to the classification head's config when > 0.
    """
    if input_mode not in ("rgb", "depth"):
        raise ValueError(f"input_mode must be 'rgb' or 'depth', got {input_mode!r}")
    if not os.path.isdir(LOCAL_MIT_B2):
        raise FileNotFoundError(f"local mit-b2 dir missing: {LOCAL_MIT_B2}")
    in_ch = 3 if input_mode == "rgb" else 1
    pretrained = encoder_weights is not None

    if force_route in (None, "imgcls"):
        try:
            net = _build_imgcls(classes, pretrained)
            if dropout and dropout > 0:
                net.config.classifier_dropout_prob = float(dropout)
            return B2PolarNet(net, in_ch, "imgcls", pool_dense=False)
        except Exception as e:   # noqa: BLE001 - any import/API drift falls through to route B
            if force_route == "imgcls":
                raise
            print(f"[b2_model_factory] route A (SegformerForImageClassification) failed "
                  f"({type(e).__name__}: {e}); falling back to route B (semseg + GAP)")

    net = _build_semseg_gap(classes, pretrained)
    return B2PolarNet(net, in_ch, "semseg-gap", pool_dense=True)


if __name__ == "__main__":  # CPU self-check:  CUDA_VISIBLE_DEVICES="" python b2_model_factory.py
    for mode, ch in (("rgb", 3), ("depth", 1)):
        m = build(mode).eval()
        with torch.no_grad():
            out = m(torch.randn(2, ch, 64, 64))
        assert out.shape == (2, N_CELLS), out.shape
        print(f"{mode:5s} route={m.route} in_ch={ch} out={tuple(out.shape)} "
              f"params={sum(p.numel() for p in m.parameters()) / 1e6:.3f}M")
