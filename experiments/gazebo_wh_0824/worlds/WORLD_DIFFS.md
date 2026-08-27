# WORLD_DIFFS -- what each variant changes, line by line

source (read-only): `/home/vislab/Desktop/work_sy/Baseline_NegObs/src/negativeobstacleavoidandance/bumperbot_description/worlds/smallest_world.world`
source sha256[:16]: `5c88e743b07eb8f6`  (66182 bytes, 1923 lines)

Every variant is produced by ONE text splice: a block inserted immediately before
`<light name='Warehouse_CeilingLight_003'>`.  Nothing else in the paper's file is
touched -- `diff` against the source shows a single added hunk and zero deletions.

## measured hazard (from large_holed_floor.stl, 1 cm raster, state pose applied)

| opening | x [-4.28, -3.48] | y [-1.37, -0.57] | 0.80 x 0.80 m | plate top z = 0.1243 |
|---|---|---|---|---|
| approach | y = -0.970 | looking -x (yaw pi) | near rim x = -3.48 | |

## camera rig (identical in all four worlds -- instrumentation, not a variant)

| view | key | eye (x,y,z) | standoff from near rim | pitch | hfov | res |
|---|---|---|---|---|---|---|
| `rs_d0.5` | `d05` | (-2.980, -0.970, 0.249) | 0.5 m | 15.0 deg down | 69.00 deg | 1280x720 |
| `rs_d0.7` | `d07` | (-2.780, -0.970, 0.249) | 0.7 m | 15.0 deg down | 69.00 deg | 1280x720 |
| `rs_d0.9` | `d09` | (-2.580, -0.970, 0.249) | 0.9 m | 15.0 deg down | 69.00 deg | 1280x720 |
| `rs_d1.1` | `d11` | (-2.380, -0.970, 0.249) | 1.1 m | 15.0 deg down | 69.00 deg | 1280x720 |
| `rs_d1.5` | `d15` | (-1.980, -0.970, 0.249) | 1.5 m | 15.0 deg down | 69.00 deg | 1280x720 |
| `rs_d2` | `d2` | (-1.480, -0.970, 0.249) | 2.0 m | 15.0 deg down | 69.00 deg | 1280x720 |
| `rs_d2.6` | `d26` | (-0.880, -0.970, 0.249) | 2.6 m | 15.0 deg down | 69.00 deg | 1280x720 |
| `rs_d3.4` | `d34` | (-0.080, -0.970, 0.249) | 3.4 m | 15.0 deg down | 69.00 deg | 1280x720 |
| `overview` | `ov` | (-2.000, -0.970, 7.000) | - | 80.2 deg down | 108.86 deg | 1280x720 |

The approach cameras copy the paper's own robot camera verbatim (RealSense D435 sim: 1280x720, hfov 1.2043 rad, 0.261 rad nose-down, eye 0.125 m).

## per-variant added geometry

| world | tier | box models added | added lines | sha256[:16] |
|---|---|---|---|---|
| `wh0.world` | control (V, as published) | 0 | 203 | `7e32a0afe1560db2` |
| `wh_e.world` | E (edge-only) | 1 | 220 | `7689a11c91aee888` |
| `wh_h.world` | H (hidden) | 1 | 220 | `468d270139bcef8c` |
| `wh_hc.world` | H-ctrl (hazard removed twin of wh_h) | 2 | 237 | `f4589074f9438ba5` |

### box specs

| model | world(s) | size (x,y,z) m | centre (x,y,z) m | material | why |
|---|---|---|---|---|---|
| `wh_pallet_cover` | wh_e | 0.62, 1.20, 0.144 | -3.970, -0.970, 0.1963 | Gazebo/Wood | WH-E: one pallet laid over the FAR 0.62 m of the 0.80 m opening, resting on the plate at both y overhangs.  A 0.18 m strip of void survives at the near rim -> the drop is present as an EDGE only. |
| `wh_pallet_stack` | wh_h, wh_hc | 0.30, 1.20, 0.45 | -3.330, -0.970, 0.3493 | Gazebo/Wood | WH-H: three stacked pallets parked at the near rim of the opening. 0.45 m tall vs a 0.125 m eye height -> the opening subtends 0 px from every approach pose. |
| `wh_floor_patch` | wh_hc | 0.90, 0.90, 0.1243 | -3.880, -0.970, 0.0621 | Gazebo/Grey | WH-Hc: fills the opening flush with the floor plate (top at z=0.1243). This is the ONLY difference from wh_h -- the hazard is gone, the scene is not. |

**Unchanged in every variant**: the floor plate and its pose, all 24 AWS RoboMaker
warehouse assets and their poses, `aws_robomaker_warehouse_WallB_01_001`, the single
`Warehouse_CeilingLight_003` point light (pose 0 0 9, diffuse 0.5), `<scene>` ambient
0.4 / background 0.7 / shadows 1, `<physics>`, and the whole `<state>` block.
