# TIER_TABLE — C1 hole probe, label distribution

manifest: `experiments/probe_holes_0820/dataset_manifest_probe.json` · grid **PROVISIONAL-GRID-V1** (20 cells) · rounds {'on': '260821_probe_on', 'off': '260821_probe_off'} · seed 20260822

Tier is a property of the HAZARD-ON frame (V = interior pixels visible, E = rim only, H = the drop contributes no pixel at all). Off-arm rows carry no hazard and are listed only so the pair is visibly complete.

| scene | arm | cond | frames | GT-positive | V | E | H | other |
|---|---|---|---:|---:|---:|---:|---:|---:|
| probeH1 | off | L0 | 8 | 0 | 0 | 0 | 0 | 8 |
| probeH1 | off | L5 | 8 | 0 | 0 | 0 | 0 | 8 |
| probeH1 | off | L7 | 8 | 0 | 0 | 0 | 0 | 8 |
| probeH1 | on | L0 | 8 | 8 | 5 | 1 | 2 | 0 |
| probeH1 | on | L5 | 8 | 8 | 5 | 1 | 2 | 0 |
| probeH1 | on | L7 | 8 | 8 | 5 | 1 | 2 | 0 |
| probeH2 | off | L0 | 8 | 0 | 0 | 0 | 0 | 8 |
| probeH2 | off | L5 | 8 | 0 | 0 | 0 | 0 | 8 |
| probeH2 | off | L7 | 8 | 0 | 0 | 0 | 0 | 8 |
| probeH2 | on | L0 | 8 | 8 | 0 | 8 | 0 | 0 |
| probeH2 | on | L5 | 8 | 8 | 0 | 8 | 0 | 0 |
| probeH2 | on | L7 | 8 | 8 | 0 | 8 | 0 | 0 |
| probeH3 | off | L0 | 8 | 0 | 0 | 0 | 0 | 8 |
| probeH3 | off | L5 | 8 | 0 | 0 | 0 | 0 | 8 |
| probeH3 | off | L7 | 8 | 0 | 0 | 0 | 0 | 8 |
| probeH3 | on | L0 | 8 | 8 | 0 | 0 | 8 | 0 |
| probeH3 | on | L5 | 8 | 8 | 0 | 0 | 8 | 0 |
| probeH3 | on | L7 | 8 | 8 | 0 | 0 | 8 | 0 |

## per scene-arm

| scene | arm | frames | GT-positive | V | E | H | other |
|---|---|---:|---:|---:|---:|---:|---:|
| probeH1 | off | 24 | 0 | 0 | 0 | 0 | 24 |
| probeH1 | on | 24 | 24 | 15 | 3 | 6 | 0 |
| probeH2 | off | 24 | 0 | 0 | 0 | 0 | 24 |
| probeH2 | on | 24 | 24 | 0 | 24 | 0 | 0 |
| probeH3 | off | 24 | 0 | 0 | 0 | 0 | 24 |
| probeH3 | on | 24 | 24 | 0 | 0 | 24 | 0 |

## what to look at first

* **probeH3 should be almost entirely H.** Its occlusion is computed for all eight frozen camera draws (see the scene header); an E or V row there means the render disagrees with the geometry and the occlusion audit needs re-reading before any recall number is quoted.
* **probeH1 should be V-dominant** and should carry band-1 positives on cuts 1 and 2 of every condition (6 frames per arm).
* **A GT-positive count below the frame count on an ON row** means some cut put the hole outside the 12 m grid; those frames are negatives, not misses, and `frame_recall_*` already excludes them.
