#!/usr/bin/env python3
"""polar_dataset_v3.py — v2 `PolarGridDataset` 의 **마스크 인지 shim**.

train_polar.py / polar_dataset.py 는 **한 줄도 수정하지 않는다** (P-4 규칙 · 본 웨이브 지시).
본 파일은 `polar_dataset.PolarGridDataset` 을 상속해 아이템마다 **칸 단위 무시 마스크**를
하나 더 내보낼 뿐이며, x·y 의 산출 경로와 **RNG 소비 순서**는 원본과 바이트 동일하다:

  * `_load_x` 를 그대로 호출한다(오버라이드 없음).
  * hflip 동전을 **원본과 같은 자리에서 정확히 한 번** 뽑는다 (`torch.rand(())`).
  * 동전이 맞으면 x 를 뒤집고 y 와 **마스크를 같은 sector permutation** 으로 섞는다
    — 마스크는 칸 라벨이므로 y 와 같이 움직여야 한다(이걸 빠뜨리면 뒤집힌 프레임에서
    마스크가 엉뚱한 칸을 덮는다).

반환 arity:
    aux OFF : (x, y, meta, ign)
    aux ON  : (x, y, meta, ign, mask)      # mask = 아모달 픽셀 마스크(격리 aux 런 전용)

`smoke_v3.py` 가 "마스크 전량 0 -> 원본 클래스와 x·y 바이트 동일" 을 실측으로 확인한다.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import torch

sys.path.insert(0, "/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/mainrun_0819/code")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from polar_dataset import PolarGridDataset, aux_mask_path, load_aux_mask  # noqa: E402

import v3_masks  # noqa: E402


class PolarGridDatasetV3(PolarGridDataset):
    """v2 데이터셋 + 등록 무시 마스크 4채널 (v3_masks.py 가 정본)."""

    def __init__(self, *a, aux_stem_map=None, aux_mask_dir=None, **kw):
        # aux_stem_map: v3 frame_id -> 아모달 PNG stem. 격리 aux 런 전용(§5.6).
        # 원본 __init__ 의 aux census 는 v2 stem 규약을 하드코딩하므로 우회하고 여기서 센다.
        self._aux_stem_map = aux_stem_map
        super().__init__(*a, aux_mask_dir=None, **kw)
        self.aux_mask_dir = str(aux_mask_dir) if aux_mask_dir else None
        if self.aux_mask_dir is not None:
            if not os.path.isdir(self.aux_mask_dir):
                raise FileNotFoundError(f"aux_mask_dir not found: {self.aux_mask_dir}")
            self._census_aux()
            if self.n_aux_found == 0:
                raise RuntimeError(f"aux_mask_dir {self.aux_mask_dir!r} matches 0 of "
                                   f"{len(self.items)} frames — stem 규약 불일치")
        self.ign = [torch.tensor(v3_masks.frame_ignore(r, self.n_cells), dtype=torch.float32)
                    for r in self.items]
        self.mask_census = v3_masks.census(self.items)

    # 원본은 aux_mask_dir 이 있으면 stem 규약으로 census 를 돌린다. v3 frame_id 는
    # 'A/scene01/...' 라 v2 'on__scene01__...' PNG 와 이름이 갈리므로 매핑을 끼운다.
    def _aux_path(self, frame_id: str) -> str:
        if self._aux_stem_map is not None:
            st = self._aux_stem_map.get(frame_id)
            return os.path.join(self.aux_mask_dir, st + ".png") if st else ""
        return aux_mask_path(self.aux_mask_dir, frame_id)

    def _census_aux(self):
        self.n_aux_found = self.n_aux_missing = 0
        for r in self.items:
            p = self._aux_path(str(r["frame_id"]))
            hit = bool(p) and os.path.exists(p)
            self.n_aux_found += hit
            self.n_aux_missing += not hit

    def ignore_matrix(self) -> np.ndarray:
        """[N, n_cells] uint8 — 데이터셋 순서(=shuffle=False 로더 순서) 그대로."""
        return np.stack([m.numpy() for m in self.ign]).astype(np.uint8)

    def gt_matrix(self) -> np.ndarray:
        return np.asarray([r["polar_gt"] for r in self.items], dtype=np.float32)

    def fa_matrix(self) -> np.ndarray:
        """FA 항 모집단 `v3_D_arm_cells`."""
        return np.asarray([v3_masks.fa_cells_v3(r, self.n_cells) for r in self.items],
                          dtype=np.uint8)

    def __getitem__(self, i):
        rec = self.items[i]
        x = self._load_x(rec, i)                                  # 원본 경로 그대로
        gt = rec["polar_gt"]
        assert len(gt) == self.n_cells, \
            f"{rec['frame_id']}: polar_gt has {len(gt)} != {self.n_cells} ({self.grid.version})"
        y = torch.tensor(gt, dtype=torch.float32)
        ign = self.ign[i].clone()
        # ONE coin, drawn exactly where it was before -> v2 와 RNG 소비 순서 동일
        do_flip = self.train_hflip and float(torch.rand(())) < self.hflip_p
        if do_flip:
            x = torch.flip(x, dims=[-1])
            y = y.index_select(-1, self._flip_perm)
            ign = ign.index_select(-1, self._flip_perm)           # 마스크도 칸 라벨이다
        meta = {
            "frame_id": str(rec["frame_id"]),
            "scene_id": str(rec["scene_id"]),
            "tier": str(rec.get("tier") or "none"),
            "toggle_state": str(rec.get("toggle_state") or "none"),
            "arm": str(rec.get("arm") or "none"),
        }
        if self.aux_mask_dir is None:
            return x, y, meta, ign
        m = load_aux_mask(self._aux_path(meta["frame_id"]), self.img_size)
        if do_flip:                      # 아모달 마스크는 이미지다: x 와 같이 뒤집고 permutation 없음
            m = torch.flip(m, dims=[-1])
        return x, y, meta, ign, m
