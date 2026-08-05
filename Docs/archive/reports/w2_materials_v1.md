# W2-A5 — Materials Infrastructure: Detail-Normal Generation + `NegObsGround.mdl` v1.9.0

Author: W2-A5 (materials infra, MAIN tree) · Date 2026-07-29 · GPU 0 / no render / no Isaac.
Governing spec: `Docs/briefs/t1_material_layer_spec_v1.md` **v1.1** §1.6(a) · §1.8③ · §3.1 · §3.3 · §3.4(a)
Contract counterpart: `Docs/briefs/ground_kit_spec_v1.md` v1.1 §4.5 (unit-cell ledger, reverse contract).

Evidence tags on every number: `[measured]` direct measurement in this session · `[stat]` statistical
result over a stated sample · `[assumed]` modelling assumption stated explicitly · `[law]` statute/standard.

## 0. Deliverables

| # | Path | State |
|---|---|---|
| 1 | `assets/gen_detail_normal.py` | new · 403 lines · `py_compile` OK `[measured]` |
| 2 | `assets/detail_grain_mineral_nor.png` | new · 1024² RGB8 · 2141 KB `[measured]` |
| 3 | `assets/detail_grain_granular_nor.png` | new · 1024² RGB8 · 2433 KB `[measured]` |
| 4 | `assets/detail_grain_brushed_nor.png` | new · 1024² RGB8 · 1881 KB `[measured]` |
| 5 | `assets/NegObsGround.mdl` | v1.8.0 → **v1.9.0** · 787 → 990 lines `[measured]` |
| 6 | `Docs/reports/w2_materials_v1.md` | this file |

**Nothing was wired.** `scene_common.py` is untouched — the worktree agent owns `_DETAIL_MAP`
wiring per §1.6(b). No scene file, kit file, or script outside the list above was modified.

---

## 1. Measurement provenance — the definition is not mine, and I proved it

`scripts/norm_spec.py` **landed mid-session** from the parallel agent. It was absent at the start
(`ls scripts/norm_spec.py` → no such file) and present before this report was finalised `[measured]`,
so both code paths described below were actually exercised.

Per mission rule, `gen_detail_normal.py`:

1. loads `scripts/norm_spec.py` at run time if present (`load_measurer()`, entry points
   `spectrum` / `measure_file` / `measure` / `analyze` / `norm_spec`, with key-name normalisation
   for `macro_pct`/`hf_pct`), and
2. otherwise falls back to an **inline implementation of §3.4(a) steps 1–9 verbatim** —
   native-resolution central N=1024 crop with no resampling, `nx = 2R−1` / `ny = 2G−1` only
   (B unused, so DX/GL is moot), separable Hann with the **window-weighted mean subtracted first**,
   ring-**sum**-weighted normalisation `T = Σ_{r=1..N/2} sm[r]`, `slope_n` least-squares over
   `3 ≤ r < N/4`, RMS on the raw crop before windowing.

The run banner prints which path was used. Final run:
`측정기 = scripts/norm_spec.spectrum (외부 정본)` — **the parallel agent's module is the operative
gate**, with the inline implementation retained as a fallback and as a second opinion.

**Proof that the definition is the canonical one — §3.4 anchor reproduction, 4/4 exact** `[measured]`:

| anchor map | slope_n | macro% | hf% | RMS | §3.4 table | verdict |
|---|---:|---:|---:|---:|---|---|
| `assets/scene01/concrete_wall_nor_dx.jpg` | −0.71 | 4.1 | 18.9 | 0.056 | −0.71 / 4.1 / 18.9 / 0.056 | OK |
| `assets/scene01/asphalt_nor_dx.jpg` | −0.66 | 3.2 | 13.3 | 0.294 | −0.66 / 3.2 / 13.3 / 0.294 | OK |
| `assets/scene01/stone_flag_nor_dx.jpg` | −2.46 | 58.4 | 2.5 | 0.192 | −2.46 / 58.4 / 2.5 / 0.192 | OK |
| `assets/paving_interlock_nor.jpg` (2048²) | −1.98 | 52.3 | 4.8 | 0.449 | −1.98 / 52.3 / 4.8 / 0.449 | OK |

Both implementations reproduce all four. This closes red-team finding `redteam_w1_design.md` §2.6
("six variants, all failed to reproduce"): the ring-**sum**-weighted normalisation and the
window-weighted mean pre-subtraction are the two branch points, and both are now fixed in
executable code in two places.

**Independent cross-validation of the two measurers on the three delivered maps** `[measured]` —
`gen_detail_normal.measure_file` (inline) vs `norm_spec.spectrum` (external), same inputs:

| map | slope_n | macro% | hf% | RMS | agreement | verdict |
|---|---:|---:|---:|---:|---|---|
| mineral | 0.040 / 0.040 | 0.43 / 0.43 | 69.5 / 69.5 | 0.180 / 0.180 | all \|Δ\| < 5·10⁻⁴ | PASS / PASS |
| granular | 0.231 / 0.231 | 0.28 / 0.28 | 72.7 / 72.7 | 0.280 / 0.280 | all \|Δ\| < 5·10⁻⁴ | PASS / PASS |
| brushed | −0.034 / −0.034 | 0.51 / 0.51 | 68.8 / 68.8 | 0.140 / 0.140 | all \|Δ\| < 5·10⁻⁴ | PASS / PASS |

Two implementations written independently on the same day from the same §3.4(a) text agree to
sub-milliunit precision and return the same verdict on every family. This is the strongest
available evidence that §3.4(a) is now unambiguous prose — the exact property red-team §2.6 said
was missing.

The anchor check is a **hard gate inside the generator**: if any anchor mismatches, generation
aborts with exit 1 before any file is written, because the pass/fail numbers would otherwise be
meaningless.

---

## 2. Generation method (§3.3)

- **β is a POWER exponent**: `power(height) ∝ f^(−β)`. This is the v1.1 R2 convention, *not* v1's
  amplitude convention; the two differ by a factor of 2. Normal = gradient of the height field
  ⇒ tangent power `∝ f^(2−β)` ⇒ `slope_n ≈ 2 − β`.
- Synthesis: white Gaussian noise → FFT → amplitude shaped by `f^(−β/2)` → DC zeroed →
  **Nyquist cut, all bins with radial `R > 0.45` cycles/px zeroed** → **spectral differentiation**
  (multiply by `i·2πf`) → inverse FFT.
  Spectral differentiation rather than finite differences, for two reasons: finite differencing is
  itself a low-pass filter that would blur the β ↔ `slope_n` relation, and the spectral form keeps
  periodic boundaries exact, i.e. **the maps are exactly tileable**.
- Amplitude is then rescaled so the tangent RMS hits the target exactly (§3.3's "RMS is directly
  specifiable" property). Encoding is 8-bit RGB with `nz = sqrt(1 − nx² − ny²)`; texels that would
  leave the unit sphere are rescaled to length 0.999 (count reported below).
- Anisotropy (brushed only) is applied as an axis-scaled radius in the shaping step:
  `f_shape = hypot(fx/0.25, fy)`. Dividing `fx` by 0.25 attenuates x-frequencies ⇒ **the grain runs
  long along the u (x) axis** = brushed-metal scratches.
- Seeds are fixed (7 / 17 / 29), so the maps are byte-reproducible — verified by MD5 across two
  independent runs, 3/3 identical `[measured]`.

**The measured values below are taken from the encoded 8-bit result**, not from the float
intermediate — the renderer reads the encoded file, so that is the authoritative object.

---

## 3. Validation — §3.1 gate, all three families PASS

Gate applied: `macro% < 10` (spec §3.1; the mission's relaxed 15 is reported as a reference column
only — the strict value is used because procedural maps have ~20× headroom) · `−0.9 < slope_n ≤ +0.3`
· `RMS ∈ [0.12, 0.35]` · `hf% ≥ 10` (auxiliary, cross-check only, not a verdict input).

| family | β | RMS target | **slope_n** | **macro%** | hf% | **RMS** | clipped texels | aniso ratio | seam ratio | verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| **mineral** | 2.0 | 0.18 | **+0.040** | **0.43** | 69.5 | **0.180** | 0 / 1 048 576 | 1.015 | 1.05 | **PASS** |
| **granular** | 1.8 | 0.28 | **+0.231** | **0.28** | 72.7 | **0.280** | 3 / 1 048 576 | 0.997 | 1.00 | **PASS** |
| **brushed** | 2.0 | 0.14 | **−0.034** | **0.51** | 68.8 | **0.140** | 0 / 1 048 576 | **0.122** | 0.97 | **PASS** |

`[measured 2026-07-29 · numpy 2.2.6 + PIL 12.2.0 · GPU 0 · N=1024 · seeds 7/17/29 · nyq_cut 0.45]`

Margins against the gate `[measured]`: `macro%` uses 0.43–0.51 of a budget of 10 (≥19× headroom);
`slope_n` sits 0.94 / 1.13 / 0.87 above the −0.9 floor and 0.26 / **0.069** / 0.33 below the +0.3
ceiling; RMS sits 0.06–0.16 inside a 0.23-wide window. **The one thin margin is granular's
`slope_n` = +0.231 vs a ceiling of +0.3** — see §7 risk R2.

Two metrics beyond §3.1, added because the radial average of §3.4 destroys direction and says
nothing about tiling:

- **aniso ratio** = mean tangent power in the ±30° wedge around the `fx` axis ÷ the same around
  `fy`, over `3 ≤ r < N/4`. Isotropic ⇒ ≈1. `[measured]` mineral 1.015, granular 0.997 confirm
  isotropy; brushed **0.122** = 8.2× more power across the u axis than along it, i.e. the
  anisotropy the spec asked for is present and quantified. Without this number, brushed is
  indistinguishable from mineral in the §3.1 table.
- **seam ratio** = wrap-around difference energy ÷ interior neighbour difference energy.
  `[measured]` 0.97–1.05, i.e. the tile boundary is statistically indistinguishable from the
  interior ⇒ **exactly tileable**, as the FFT construction predicts.

Encoded-normal sanity `[measured]`: `‖n‖` mean 1.0001–1.0003, min 0.9939, max 1.0062 — the spread is
pure 8-bit quantisation. Quantisation adds white noise of amplitude `(1/255)/√12 · 2 ≈ 0.0023` in
tangent units, i.e. a power ratio of `1.6·10⁻⁴` against RMS 0.18 — negligible, and it is already
inside the measured numbers above since they were taken post-encode.

**License**: zero. The maps are generated from a seeded PRNG by a script in this repository. No
CC0 procurement, no Quixel/NoAI exposure, no Isaac-Environments redistribution clause. This is the
main reason §3.3 ranks procedural first.

### 3.1 Relation to the repository fallbacks

Per t1 v1.1 §3.2 the held assets `plaster_nor_dx` (mineral, macro 3.9 / slope −0.89 / RMS 0.159)
and `asphalt_nor_dx` (granular, macro 3.2 / slope −0.66 / RMS 0.294) already pass and remain the
**fallbacks** — nothing here replaces them. The generated set improves on them in three respects
`[measured]`: mineral's `slope_n` moves from −0.89 (0.01 from the floor, a boundary pass) to +0.040
(0.94 of margin); macro% drops from 3.9/3.2 to 0.43/0.28; and **brushed exists at all**, where §3.2
recorded total loss of held candidates (`metal_rust` slope −1.54 ✗, `granite_dark` RMS 0.093 ✗,
`sandstone` macro 16.7 ✗). Family three was procedural-or-nothing.

---

## 4. Honest deviations from the spec text

| # | Spec text | What I did | Why |
|---|---|---|---|
| D1 | §3.3 table: β=2.0 → `slope_n = −0.13` | My β=2.0 gives **+0.040** (mineral) / **−0.034** (brushed) `[measured]` | Theory says `slope_n = 2 − β = 0`. My generator lands within +0.04 of theory; the spec's tabulated −0.13 implies its (now-lost) generator carried a −0.13 bias, most likely from finite-difference gradients. Both are inside the gate, so no decision changes — but the spec's β→slope_n table should not be used as a calibration curve for this script. Use the printed measurement. |
| D2 | §1.8③ pseudocode: unit jitter hashes "dominant-plane coordinates" | I hash **world (x, y), always** | The same section's shortcut-safety argument is *"the hash reads x,y and never z ⇒ correlation with GT drop = 0"*. On a wall the dominant plane is X or Y, whose second coordinate **is z** — that would break the argument the ruling depends on. Unit jitter's only consumers are horizontal paving profiles in the ground_kit ledger (§4.5 U4 already forbids it on non-modular surfaces), so (x, y) is both the intent and the safe reading. Documented in the MDL comment at the function. |
| D3 | §1.6(a): `detail_rough_gain` "passes grain contrast to roughness" (no formula given) | Grain is defined as the **signed** projection of the normal perturbation onto the first tangent axis, divided by `det_bump`, clamped to [−1, 1] | An unsigned magnitude has a non-zero mean (≈0.16–0.30 for these maps), so `rough += gain·grain` would *shift* mean roughness rather than add contrast. The signed form has mean ≈ 0 because normal-map tangent components have mean 0 ⇒ contrast only. It also costs zero extra texture fetches — it reuses the single sample. |
| D4 | Mission: self-verify `macro% < 15` | Gated at **`< 10`** (spec §3.1), reported both | 15 was v1's threshold; v1.1 R2 re-calibrated to 10. Measured 0.28–0.51 passes either way, so this is a documentation choice, not a substantive one. |

---

## 5. `NegObsGround.mdl` v1.9.0 — what changed

787 → 991 lines · `anno::version(1, 8, 0)` → `anno::version(1, 9, 0)` `[measured]`.

**Added: 3 free functions + 1 struct + 8 material parameters. Removed: nothing. Changed: 5 sites
in the `let` block.** Full comment-stripped diff enumerated in §6.2.

### 5.1 New functions

| symbol | purpose |
|---|---|
| `float2 negobs_hash2(float2)` | deterministic cell hash. Introduced now so §4.2 hex tiling reuses the *same* hash — two different hashes on one surface would produce two mis-phased grids. |
| `float negobs_unit_gain(float2 pw, uniform float2 cell, uniform float2 origin, uniform float sigma, uniform float accent)` | §1.8③ log-normal per-unit albedo jitter. Zero texture fetches. Accent units get σ×2.5. |
| `NegObsDetail negobs_detail_normal(uniform texture_2d, uniform float scale, uniform float bump, uniform bool flip_u, uniform bool flip_v)` | §1.6(a) micro-grain detail normal, **dominant plane, single sample**. Returns `{ nrm, grain }`. |

`negobs_detail_normal` completes the spec's `…` placeholders: dominant-Z uses `(pw.x, pw.y)` with
tangents (worldX, worldY); dominant-X uses `(pw.y, pw.z)` with (worldY, worldZ); dominant-Y uses
`(pw.x, pw.z)` with (worldX, worldZ). Axis selection is a hard switch, which is legitimate here and
not in `negobs_sample_tri`: the grain is isotropic and high-frequency, so there is no coherent
pattern to tear at a plane transition. That is also why one sample suffices — three planes would
triple the fetch count for nothing.

### 5.2 New parameters (all appended at the tail of the signature)

| name | type | default | notes |
|---|---|---|---|
| `detail_normalmap_texture` | `texture_2d` | `texture_2d()` (invalid) | inert by invalidity |
| `detail_bump_factor` | `float` | **0.0** | inert by zero |
| `detail_texture_scale` | `float` | 12.5 | 1/tile [1/m] = 8 cm period |
| `detail_rough_gain` | `float` | **0.0** | inert by zero |
| `unit_cell_m` | `float2` | **`float2(0.0)`** | inert by zero; source = ground_kit ledger |
| `unit_cell_origin` | `float2` | `float2(0.0)` | §4.5 U3 — phase alignment with the joint grid |
| `unit_albedo_sigma` | `float` | 0.10 | only active when `unit_cell_m > 0` |
| `unit_accent_frac` | `float` | 0.07 | accent units get σ×2.5 |

### 5.3 Contract status with `ground_kit` §4.5

`unit_cell_origin` — the reverse-contract item §4.5 flagged as *"passing the period without the
origin is non-performance"* — **is implemented and is the 6th of the 8 new parameters**. The MDL
side of the contract is now complete: ground_kit supplies `(cell_m, (ox, oy))` per profile from
`GROUND_DIMENSIONS["unit_cell"]`, and the material aligns its hash lattice to exactly that.
U1/U2/U3 remain ground_kit-side assertions; **U4** (`unit_cell = None` ⇒ enabling jitter is a T1-side
FAIL) is not yet enforceable in the MDL — the material cannot see the profile name. It has to be
enforced by the wiring agent in `ground_kit`/`scene_common`, and is listed as blocker B3.

---

## 6. Pixel-inertness proof (static analysis — no render available)

**Claim.** With all eight new parameters at their defaults, v1.9.0 emits a material that is
functionally identical to v1.8.0, and produces bit-identical output up to the sign of floating-point
zero in normal components (which has no observable effect).

### 6.1 Argument 1 — the parameter surface for existing callers is untouched

Mechanically diffing the material signature of `HEAD:assets/NegObsGround.mdl` against the working
tree, with comments stripped and each parameter parsed into `(type, name, default)` `[measured]`:

```
v1.8.0 params: 66   v1.9.0 params: 74
first 66 params byte-identical (type, name, default): True
appended (positions 67..74): detail_normalmap_texture, detail_bump_factor,
  detail_texture_scale, detail_rough_gain, unit_cell_m, unit_cell_origin,
  unit_albedo_sigma, unit_accent_frac
```

The new parameters were deliberately appended at the tail rather than grouped thematically in the
middle. Consequence: **both name binding and positional binding of every existing caller are
unchanged.** `scene_common._make_ground_pbr` binds by name (`sh.CreateInput(<name>, T)`,
`scene_common.py:1126–1162` `[measured]`), so unbound inputs fall through to the MDL defaults and
no USD authoring changes at all. Any positional consumer, if one ever appears, also sees an
unchanged prefix.

### 6.2 Argument 2 — exactly five call sites changed, each provably identity at defaults

The complete comment-stripped diff inside the material body is five hunks. Nothing else in the
`let` block, and nothing at all in `negobs_noise`, `negobs_noise_aniso`, `negobs_sample_basis`,
`negobs_sample_tri`, `negobs_layer`, `negobs_weather`, or the BSDF construction, was touched
`[measured]` — verified by `difflib` over the comment-stripped token stream.

| # | site | change | why it is inert at defaults |
|---|---|---|---|
| S1 | hoist | `pw_w` / `nw_w` bound in `let`, then passed to `negobs_weather` instead of the inline expressions | **Pure refactor.** The bound expressions are character-for-character the ones previously inlined. MDL `let` bindings are pure, so the value is identical; the compiled DAG shares one node either way. |
| S2 | albedo | `* base_color` → `* base_color * color(unit_g)` | `unit_cell_m = float2(0)` ⇒ `negobs_unit_gain` hits `if (cell.x <= 0 \|\| cell.y <= 0 \|\| sigma <= 0) return 1.0` ⇒ multiplication by exactly `1.0`, an IEEE-754 identity. |
| S3 | detail call | `NegObsDetail DET = negobs_detail_normal(...)` added | `detail_bump_factor = 0` **and** an invalid default texture ⇒ two independent guards drive the early return, which sets `D.nrm = state::normal()`, `D.grain = 0.0`. No texture fetch occurs. |
| S4 | normal | `normalize(nrm_tex + (rc − n))` → `normalize(nrm_tex + (rc − n) + (DET.nrm − n))` | `DET.nrm` **is** `state::normal()` — the same expression — so `(DET.nrm − n)` is the subtraction of a value from itself = exact zero vector, and `x + 0.0 == x` for every finite `x`. Same first-order-deviation rule the bevel already uses and documents in-file (v1.8.0 `:748–759`, now `:934–943`). |
| S5 | roughness | `rough_sq = rough_w²` → `rough_d = clamp(rough_w + detail_rough_gain·DET.grain, 0.02, 1.0)`; `rough_sq = rough_d²` | `detail_rough_gain = 0` ⇒ `0.0 · grain` is `±0.0` ⇒ `rough_w + ±0.0 == rough_w`. The re-clamp is idempotent: `rough_w` already emerges from `clamp(..., 0.02, 1.0)` at `:931`. |

### 6.3 Argument 3 — the IEEE-754 identities, executed

The three algebraic identities S2/S4/S5 rely on were run in float32 over 2 000 000 random samples
each, including hand-seeded signed-zero cases `[stat, n = 2·10⁶ per site]`:

| site | identity | bitwise equal | value equal |
|---|---|---|---|
| S4 | `normalize(v + 0⃗) == normalize(v)` | **4 rows of 2 000 000** differ | **max \|a−b\| = 0.0** |
| S2 | `c · 1.0 == c` | all | all |
| S5 | `clamp(r + 0.0·g, 0.02, 1.0) == r` for `r ∈ [0.02, 1]` | all | all |

The four S4 rows are exactly the four hand-seeded vectors containing `−0.0`; the differing entries
are `−0.0` vs `+0.0` and nothing else `[measured]`. A signed zero in a normal component changes no
dot product, no BSDF weight and no pixel — it is a bit pattern difference, not a value difference.
**This is the single caveat on the word "bit-identical", and it is stated rather than hidden.**

### 6.4 Argument 4 — cost at defaults is unchanged

All three early-return conditions are functions of `uniform` parameters only, so they fold at
compile time in the same way v1.6.0's `negobs_weather` early return and v1.8.0's `patch_mix <= 0`
early exit already do (both documented in-file). At defaults the material therefore issues:
**0 extra texture fetches, 0 extra noise fetches, 0 extra `state::` queries** (S1 is a shared node,
not a new one). Even in a hypothetical backend that does not fold the branch,
`tex::texture_isvalid` on the default invalid texture is false and no lookup is issued.

### 6.5 What this proof does *not* cover

It is static. It does not exclude a backend-specific effect of enlarging the material signature
(e.g. an argument-block layout change in a specific MDL→HLSL translation). That class of risk can
only be closed by the render-side regression the GPU-owner agent runs (M6). The claim I am making
is at the MDL semantic level, which is the level the mission asked for.

---

## 7. Risks and unresolved items

**R1 (highest) — at the spec's tile scales, the detail normal is a sub-pixel effect at h0.3.**
The h0.3 preset renders 1920×1080 `[measured — look_check/scene19/r2_on/*.png]`, and T0 confirmed
the projection constant `px ≈ 24·(r/d)·57.3` `[measured — t0_spike_report_v1.md §2.3]`, i.e. 24 px
per degree ⇒ one pixel subtends `0.727·d` mm. `detail_texture_scale = 12.5` puts the 1024² map on an
8 cm tile ⇒ 0.078 mm per texel, and because the §3.1 gate *requires* a near-white spectrum
(`slope_n ≈ 0`, `macro% < 10`), 99.5 % of the tangent power sits below 0.3 mm.

Fraction of tangent power at wavelengths ≥ 2 px, and the resulting effective micro-slope after
incoherent sub-pixel averaging `[measured spectra; [assumed] 1/√K mip-averaging model]`:

| map (at its §1.6(b) scale, bump) | d = 2 m | d = 5 m | d = 10 m |
|---|---|---|---|
| mineral gen · 8 cm · 0.85 | 0.32 % → **0.49°** | 0.05 % → 0.19° | 0.01 % → 0.10° |
| granular gen · 12.5 cm · 0.70 | 0.54 % → **0.83°** | 0.07 % → 0.29° | 0.01 % → 0.12° |
| brushed gen · 4 cm · 0.55 | 0.09 % → 0.13° | 0.02 % → 0.06° | 0.00 % → 0.03° |
| plaster fallback · 8 cm · 0.85 | 0.12 % → 0.26° | 0.01 % → 0.06° | 0.00 % → 0.04° |
| asphalt fallback · 12.5 cm · 0.70 | 0.08 % → 0.33° | 0.02 % → 0.15° | 0.01 % → 0.09° |
| `concrete_wall` (current, dead) · 8 cm · 0.45 | 0.84 % → 0.13° | 0.41 % → 0.09° | 0.08 % → 0.04° |

§1.2 declared the current configuration invisible at an effective 1.4°. **Every row here is below
that**, generated and fallback alike. The generated maps are 1.9–2.5× better than the fallbacks and
3.8× better than the current dead configuration at d = 2 m, but "better" is not "visible".

This is not a defect in the maps — they pass every gate the spec defines — it is that §3.1's gates
constrain *shape* and *amplitude* but never *physical scale*, so a map can pass all of them and
still deliver nothing at the judging distance. Tile-size sweep for mineral `[measured spectrum,
[assumed] same averaging model]`:

| tile [m] | `detail_texture_scale` | d = 2 m | d = 5 m | d = 10 m |
|---:|---:|---:|---:|---:|
| 0.08 | 12.5 | 0.49° | 0.19° | 0.10° |
| 0.25 | 4.0 | 1.61° | 0.64° | 0.31° |
| 0.50 | 2.0 | 3.25° | 1.29° | 0.64° |
| 1.00 | 1.0 | 6.50° | 2.60° | 1.29° |

Recommendation for the pilot, **not executed here** (`detail_texture_scale` is a spec default and
the wiring is not mine): A/B the scale, not only the map. Two candidate reframings — (a) treat the
detail normal as a *roughness-variance* channel and give `detail_rough_gain` a non-zero pilot value,
which is the physically correct route for sub-pixel micro-structure and is why S5 exists; or
(b) drop `detail_texture_scale` to the 2–4 range so the dominant band lands at 0.5–3 mm, which is
also where real concrete aggregate lives. Option (b) needs a repetition check, since a 0.5 m tile
repeats visibly — which is precisely the job of §4.2 hex tiling.

**R2 — granular's `slope_n` margin is thin.** +0.231 against a ceiling of +0.3 `[measured]`. β = 1.8
is the spec's value and I kept it. If a future re-measure (different numpy FFT path, or the parallel
`norm_spec.py`) shifts by >0.07 the family fails. β = 1.9 would land near +0.13 and still sit inside
the §3.3 recommended band (1.7–2.3); that is a one-character change if margin is wanted.

**R3 — `negobs_hash2` quantises hard in float32.** Evaluating the hash over cell indices −100..100
in float32 `[stat, n = 40 401]`: mean 0.5009, σ 0.2889 (ideal uniform 0.5 / 0.2887), adjacent-cell
correlation −0.004 (x) / +0.002 (y) — statistically clean — **but only 2 296 distinct values out of
40 401 cells**, because `sin(·)·43758.5453` in float32 leaves ~3 significant decimals. Practically
harmless (a 2 296-level jitter is far finer than the 8-bit output, and repeats are spatially
scattered, not adjacent), but it means the jitter is a discrete draw, not continuous. Worth knowing
before hex tiling reuses the same hash at a finer cell size.

**R4 — the accent mechanism behaves as specified** `[stat, n = 40 401]`: requested 7 % accent →
measured 7.00 %; albedo gain range for normal units [0.905, 1.105] and for accent units
[0.779, 1.284]; overall σ of the gain 0.0677. No clipping risk against the "no large near-white
(>0.8)" rule from a σ = 0.10 jitter on any base below 0.62 linear.

**R5 — file size.** 6.4 MB for the three maps `[measured]`. Near-white-noise PNG is essentially
incompressible; this is inherent, not a settings mistake. If repository size matters, the maps are
regenerable in ~3 s from a 403-line script with fixed seeds, so they could be built rather than
stored.

---

## 8. Reproduction

```bash
# full run: anchor check → generate → gate → write 3 PNGs (exit 1 and writes nothing on any FAIL)
python3 assets/gen_detail_normal.py

# measurement-definition check only (also exercises scripts/norm_spec.py once it lands)
python3 assets/gen_detail_normal.py --verify-anchors

# measure without writing files; machine-readable output
python3 assets/gen_detail_normal.py --dry-run --json /tmp/a5.json

# MDL signature diff used for the inertness proof in §6.1
git show HEAD:assets/NegObsGround.mdl > /tmp/mdl_v180.mdl   # read-only, no checkout
```

Runtime `[measured]`: full run ≈ 3 s wall, CPU only, peak RSS well under 1 GB. No GPU, no Isaac,
no render at any point.

---

## 9. Handover

| to | item |
|---|---|
| wiring agent (`scene_common`) | `_DETAIL_MAP` filenames are `assets/detail_grain_{mineral,granular,brushed}_nor.png`, as §1.6(b) specifies. Bind `detail_normalmap_texture` / `detail_bump_factor` / `detail_texture_scale` on the **ground** branch too — that branch is the whole point of defect ①. Read §7 R1 before choosing `detail_texture_scale`. |
| `ground_kit` agent | `unit_cell_origin` is implemented (§4.5 reverse contract discharged on the MDL side). U4 enforcement has no MDL-side hook — it must live in the ledger consumer. |
| `norm_spec.py` agent | Your module landed mid-session and is now the **operative gate** inside `gen_detail_normal.py` (entry point `spectrum`, key names normalised). Independent cross-validation on the three delivered maps: all metrics agree to <5·10⁻⁴, verdicts identical (§1). No action needed. |
| GPU-owner agent (M6) | v1.9.0 defaults are argued pixel-inert statically (§6). The one thing static analysis cannot close is backend-specific signature-layout effects; a defaults-only A/B against v1.8.0 on a single scene would close it at near-zero cost. |
