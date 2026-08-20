"""Polar-grid spec loader — the ONE place the training stack learns how many cells there are.

CONTRACT (a `gridspec_*.json`, written by the labeling stack; v0 is the reference instance):

    version          str    e.g. "PROVISIONAL-GRID-V0" / "PROVISIONAL-GRID-V1"
    n_sectors        int    azimuth wedges, index 0 = IMAGE-LEFT (A)
    sector_edges_deg [n_sectors+1] DESCENDING azimuth edges (+az = left of forward)
    sector_names     [n_sectors]   e.g. ["A","B","C","D","E"]
    n_bands          int    range bands, index 0 = nearest
    band_edges_m     [n_bands+1] ASCENDING metres, e.g. [0,2,5,8,12]
    band_names       [n_bands]     e.g. ["1","2","3","4"]
    cell_index       str    "band*<n_sectors>+sector"   (verified against n_sectors)
    hazard_depth_m   float  informational here (the labeler owns it)

Nothing in the training stack may hard-code 15 or 20: everything derives from `n_cells =
n_bands * n_sectors` and from `cell_index = band * n_sectors + sector`.

Default = `labeling/gridspec_v0.json` so every pre-0820 run and report reproduces byte-identically;
pass `--grid gridspec_v1.json` (a bare filename is resolved against the known code/experiment dirs)
to move to the 20-cell V1 grid.

Run everything with PYTHONNOUSERSITE=1 (this machine's ~/.local shadows env_seg).
"""
from __future__ import annotations

import argparse
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
_EXP = os.path.abspath(os.path.join(HERE, os.pardir))                 # experiments/mainrun_0819
_EXPS = os.path.abspath(os.path.join(_EXP, os.pardir))                # experiments/
DEFAULT_GRID = os.path.join(HERE, "labeling", "gridspec_v0.json")

# where a bare "--grid gridspec_v1.json" is looked for, in order
SEARCH_DIRS = [
    os.path.join(HERE, "labeling"), HERE, _EXP, os.path.join(_EXP, "annotations"),
    os.path.join(_EXPS, "dayrun_0820", "code", "labeling"),
    os.path.join(_EXPS, "dayrun_0820", "code"),
    os.path.join(_EXPS, "dayrun_0820", "annotations"),
    os.path.join(_EXPS, "dayrun_0820"),
]


class GridSpecError(ValueError):
    """The json does not satisfy the gridspec contract (fail loudly, never guess)."""


def resolve(path=None):
    """Absolute path of a gridspec json. `None` -> the v0 default. A bare filename is
    searched in SEARCH_DIRS (so `--grid gridspec_v1.json` works from any cwd)."""
    if not path:
        return DEFAULT_GRID
    if os.path.isfile(path):
        return os.path.abspath(path)
    if os.path.dirname(path):                      # an explicit path that does not exist
        raise FileNotFoundError(f"gridspec not found: {path}")
    for d in SEARCH_DIRS:
        cand = os.path.join(d, path)
        if os.path.isfile(cand):
            return cand
    raise FileNotFoundError(
        f"gridspec {path!r} not found in cwd or any of: " + ", ".join(SEARCH_DIRS))


class Grid:
    """Immutable view of a gridspec + every derived index the training stack needs."""

    def __init__(self, spec: dict, path: str | None = None):
        self.spec, self.path = spec, path
        self.version = str(spec.get("version", "UNVERSIONED"))
        try:
            self.n_sectors = int(spec["n_sectors"])
            self.band_edges_m = [float(x) for x in spec["band_edges_m"]]
        except (KeyError, TypeError, ValueError) as e:
            raise GridSpecError(f"{path}: n_sectors / band_edges_m missing or malformed ({e})")
        self.n_bands = int(spec.get("n_bands", len(self.band_edges_m) - 1))
        if self.n_sectors < 1 or self.n_bands < 1:
            raise GridSpecError(f"{path}: n_sectors={self.n_sectors} n_bands={self.n_bands}")
        if len(self.band_edges_m) != self.n_bands + 1:
            raise GridSpecError(f"{path}: band_edges_m has {len(self.band_edges_m)} entries, "
                                f"expected n_bands+1 = {self.n_bands + 1}")
        if any(b <= a for a, b in zip(self.band_edges_m, self.band_edges_m[1:])):
            raise GridSpecError(f"{path}: band_edges_m must ascend, got {self.band_edges_m}")

        ns, nb = self.n_sectors, self.n_bands
        self.n_cells = ns * nb
        self.sector_names = [str(x) for x in (spec.get("sector_names")
                                              or [chr(ord("A") + i) for i in range(ns)])]
        self.band_names = [str(x) for x in (spec.get("band_names")
                                            or [str(b + 1) for b in range(nb)])]
        if len(self.sector_names) != ns:
            raise GridSpecError(f"{path}: {len(self.sector_names)} sector_names != n_sectors {ns}")
        if len(self.band_names) != nb:
            raise GridSpecError(f"{path}: {len(self.band_names)} band_names != n_bands {nb}")

        # cell_index is the load-bearing contract between labeler and model: band*ns + sector
        ci = str(spec.get("cell_index", f"band*{ns}+sector")).replace(" ", "")
        m = re.fullmatch(r"band\*(\d+)\+sector", ci)
        if m and int(m.group(1)) != ns:
            raise GridSpecError(f"{path}: cell_index {ci!r} disagrees with n_sectors={ns}")
        if not m and ci not in ("band*n_sectors+sector", "band*ns+sector"):
            raise GridSpecError(f"{path}: unsupported cell_index {ci!r} "
                                f"(expected 'band*{ns}+sector')")
        self.cell_index = ci

        self.band_of = [i // ns for i in range(self.n_cells)]
        self.sector_of = [i % ns for i in range(self.n_cells)]
        self.cell_ids = [self.sector_names[i % ns] + self.band_names[i // ns]
                         for i in range(self.n_cells)]
        if len(set(self.cell_ids)) != self.n_cells:
            raise GridSpecError(f"{path}: cell ids are not unique: {self.cell_ids}")
        bad = [c for c in self.cell_ids if not re.fullmatch(r"[A-Za-z0-9_.+-]+", c)]
        if bad:                                    # cell ids become CSV column names (p_<id>/g_<id>)
            raise GridSpecError(f"{path}: cell ids unusable as CSV columns: {bad}")

    # ---------------------------------------------------------------- helpers
    def flip_perm(self):
        """new[i] = old[perm[i]] for a horizontal image flip: sectors reversed, bands unchanged."""
        ns = self.n_sectors
        return [b * ns + (ns - 1 - s) for b in range(self.n_bands) for s in range(ns)]

    def band_range(self, b):
        return self.band_edges_m[b], self.band_edges_m[b + 1]

    def band_label(self, b):
        lo, hi = self.band_range(b)
        return f"{self.band_names[b]} [{lo:g},{hi:g})m"

    def band_mask(self, b):
        """Boolean list over cells selecting band b (use np.asarray(...) at the call site)."""
        return [x == b for x in self.band_of]

    def cells_of_band(self, b):
        return [i for i, x in enumerate(self.band_of) if x == b]

    def summary(self):
        return (f"{self.version}: {self.n_bands} bands x {self.n_sectors} sectors = "
                f"{self.n_cells} cells · edges {self.band_edges_m} · {self.cell_ids[0]}.."
                f"{self.cell_ids[-1]}")

    def __repr__(self):
        return f"<Grid {self.summary()}>"

    def as_dict(self):
        return dict(version=self.version, path=self.path, n_sectors=self.n_sectors,
                    n_bands=self.n_bands, n_cells=self.n_cells,
                    band_edges_m=self.band_edges_m, band_names=self.band_names,
                    sector_names=self.sector_names, cell_ids=self.cell_ids)


_CACHE = {}


def load(path=None) -> Grid:
    """Grid from a path / bare filename / None (v0 default). A Grid instance passes through.

    Cached by resolved path: `bundle()` calls this inside a 10k-iteration bootstrap loop."""
    if isinstance(path, Grid):
        return path
    p = resolve(path)
    g = _CACHE.get(p)
    if g is None:
        with open(p) as f:
            spec = json.load(f)
        g = _CACHE[p] = Grid(spec, p)
    return g


def add_grid_arg(parser: argparse.ArgumentParser):
    parser.add_argument("--grid", default=None,
                        help="gridspec json (default: labeling/gridspec_v0.json — the 15-cell V0 "
                             "grid, kept so pre-0820 runs reproduce). Pass gridspec_v1.json for V1.")
    return parser


def from_args(args) -> Grid:
    return load(getattr(args, "grid", None))


def assert_manifest(grid: Grid, manifest_path: str, field="polar_gt"):
    """Loud early failure if a manifest was labelled against a different grid."""
    with open(manifest_path) as f:
        man = json.load(f)
    fr = man.get("frames") or []
    if not fr:
        raise GridSpecError(f"{manifest_path}: no frames")
    n = len(fr[0][field])
    if n != grid.n_cells:
        raise GridSpecError(
            f"GRID MISMATCH: manifest {os.path.basename(manifest_path)} carries {n}-cell "
            f"{field} (meta.grid_version={man.get('meta', {}).get('grid_version')!r}) but "
            f"--grid says {grid.n_cells} cells ({grid.version}). Re-label or pass the right --grid.")
    return man


if __name__ == "__main__":  # self-check:  python gridspec.py [path]
    import sys

    g = load(sys.argv[1] if len(sys.argv) > 1 else None)
    print(g.summary())
    print(f"  path       {g.path}")
    print(f"  band_of    {g.band_of}")
    print(f"  flip_perm  {g.flip_perm()}")
    assert [g.flip_perm()[i] for i in g.flip_perm()] == list(range(g.n_cells)), "flip must involute"
    assert all(g.band_of[i] == g.band_of[g.flip_perm()[i]] for i in range(g.n_cells)), \
        "flip must not move a cell across bands"
    print("  OK")
