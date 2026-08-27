---

## 6. Integrity of the read-only baseline

Checked at the start of the stage and again at the end (`tools/verify_baseline.sh`).

**(a) The published table.** The six world/model hashes in `P0_BASELINE_DIFF.md` all match:

| file | sha256[:16] | start | end |
|---|---|:-:|:-:|
| `worlds/eworld2.world` | `9cb2a2c028cfaace` | OK | OK |
| `worlds/expandedworld.world` | `2a1956d3ea564a4f` | OK | OK |
| `worlds/smallest_world.world` | `5c88e743b07eb8f6` | OK | OK |
| `worlds/eworld.world` | `dc8b7a19f9895a72` | OK | OK |
| `models/large_holed_floor/model.sdf` | `c2751bac52bcd5dd` | OK | OK |
| `models/large_holed_floor/meshes/large_holed_floor.stl` | `ab75bc68feb3adae` | OK | OK |

**(b) A full census.** Six files is a narrow test, so this stage also snapshotted
sha256 of **every** file in the clone before starting
(`logs/BASELINE_SHA256_START.txt`, 769 files) and re-ran it at the end
(`logs/BASELINE_SHA256_END.txt`). **Differing entries: 0.**

**(c) `git` (read-only).** HEAD `408f023`; the only tracked-file modification is the
documented `bumperbot_localization/launch/nav.launch.py` one-word fix from 08-19.

**(d) 42 world copies.** `tools/verify_copies.py` strips the added camera block from every
copy and compares the remaining bytes to the source world: **42 checked, 0 deviations.**

### ⚠ One finding to hand to the owner, not to fix here

`P0_BASELINE_DIFF.md` itself is sitting **inside the baseline clone**, at

    Baseline_NegObs/src/negativeobstacleavoidandance/experiments/e1_0827/reports/P0_BASELINE_DIFF.md

(written 2026-08-28 01:10; it shows up as the untracked `experiments/` in `git status`).
It was clearly meant for `Practice_NegObs/experiments/e1_0827/reports/`, where it does not
exist — which is why the path this stage was handed did not resolve. The document's own
rule is "never edit upstream files in place", so having our report land in that tree is a
hygiene break, and moving or deleting it would itself be a write into the protected tree.
**Left exactly where it is; the owner decides.** It adds no tracked change and does not
affect any render.

