#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""라운드 스탬프 — 캡처 디렉터리에 `round_stamp.json` 을 남긴다.

`look_check/**` 는 gitignore 라 렌더 산출물 자체는 커밋되지 않는다. 그래서 "이 PNG 는
어느 HEAD·어느 MDL·어느 NEGOBS_* 팔에서 나왔는가" 를 붙여 두지 않으면 6주 뒤 그 라운드는
판독 불가가 된다(`w2c_merge_t1_v1.md` §9 가 라운드마다 이 파일을 요구하는 이유).

W3 K-micro 개정 — 고친 결함 네 가지
-----------------------------------
이 도구는 라운드를 판독 가능하게 만드는 것이 일인데, FANOUT A 출구 검증에서 **판독
불가한 스탬프를 만들어 내고 있었다**는 사실이 세 갈래로 드러났다.

1. **`dirty_files` 가 개수였다** (`redteam_fanout_a.md` RT-A1). "더러운 파일 7개"는
   *어느* 파일인지 말해 주지 않는다. 10개 레인이 한 워크트리를 공유한 창에서 그것은
   "이 라운드가 남의 레인 편집을 렌더에 물고 들어갔는가" 라는 질문에 답하지 못한다는
   뜻이다. → **`dirty_paths` 목록**을 남긴다(`dirty_files` 개수는 하위호환으로 유지).
2. **`env` 가 스탬프 셸에서 잡혔다.** 렌더는 GPU 락 안의 셸에서 돌고 스탬프는 보통
   그 뒤 다른 셸에서 찍힌다. `260731_w3_s06` 의 `env: {}` 가 그 결과물이다 — 그리고
   빈 `{}` 는 "플래그가 없었다" 와 "잡지 못했다" 를 구별해 주지 않는다. →
   `--env-file` / `--capture-env` 로 **렌더 셸의 env 를 잡아** 쓰고, 어디서 잡았는지를
   **`env_source`** 로 항상 밝힌다. 잡지 못했으면 `env_captured: false` 다.
3. **`baseline_of_record` 필드가 아예 없었다.** 여섯 레인이 손으로 키를 덧붙였고
   `260731_w3_s06` 은 빠뜨렸다(RT-A1). → **일급 필드**로 만들고 `--baseline-of-record`
   / `--not-baseline` 으로 쓴다.
4. **키 하나에 뜻이 둘이었다** (RT-A4). 대부분의 레인은 불리언 표지로 썼고 s03 은
   "이 파일럿이 대조한 라운드의 경로" 로 썼다. 둘 다 truthy 라 표지 판독기가 우연히
   통과한다. → 후자는 **`compared_against`** 로 분리한다. **옛 스탬프는 계속 읽힌다**:
   `read_stamp()` 가 문자열 `baseline_of_record` 를 `compared_against` 로 정규화하고
   `schema` 가 없는 파일을 `v0` 로 표시해 준다.

사용:
    python3 scripts/stamp_round.py <capture_dir> <round> [scene] [옵션]
      --baseline-of-record | --not-baseline
      --compared-against <round_dir_or_name>   (RT-A4 분리 키)
      --superseded-by <round>
      --env-file <path>        렌더 셸에서 뜬 env 파일(`env` 출력 또는 JSON)
      --note <text>
    python3 scripts/stamp_round.py --capture-env <capture_dir>
      ↑ **렌더 셸 안에서** 부른다. `.negobs_env.json` 을 캡처 디렉터리에 남기고,
        나중에 어느 셸에서 스탬프를 찍든 그 파일이 자동으로 쓰인다.
    python3 scripts/stamp_round.py --read <capture_dir>      (옛/새 스탬프 정규화 출력)
    python3 scripts/stamp_round.py --self-check

GPU 0 · 저장소 파일 미변경(캡처 디렉터리에만 쓴다).
"""
from __future__ import annotations

import datetime
import glob
import hashlib
import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SCHEMA = "round_stamp/v1"
ENV_SIDECAR = ".negobs_env.json"
ENV_PREFIXES = ("NEGOBS_",)
# Flags that are not `NEGOBS_*` but decide what a frame looks like, so a stamp
# that omits them is not reproducible either.
ENV_EXTRA = ("PT_FAST", "CUDA_VISIBLE_DEVICES", "OMNI_KIT_ACCEPT_EULA",
             "NEGOBS_RENDER_ROLE")


def _git(*a):
    try:
        return subprocess.run(["git", "-C", REPO, *a], capture_output=True,
                              text=True, timeout=30).stdout.strip()
    except Exception:
        return ""


def _mdl():
    p = os.path.join(REPO, "assets", "NegObsGround.mdl")
    if not os.path.isfile(p):
        return None, None
    raw = open(p, "rb").read()
    ver = ""
    for ln in raw.decode("utf-8", "replace").splitlines():
        if "anno::version" in ln:
            ver = ln.strip()
            break
    return hashlib.md5(raw).hexdigest(), ver


def _relevant_env(src):
    """The subset of an environment mapping a round's look actually depends on."""
    return {k: v for k, v in sorted(src.items())
            if k.startswith(ENV_PREFIXES) or k in ENV_EXTRA}


def capture_env(out_dir, src=None):
    """Write the **render shell's** env beside the frames. Call from that shell.

    This is the half of defect (2) that no post-hoc stamping run can do for
    itself: once the render shell is gone its `NEGOBS_*` arm is gone with it, and
    `os.environ` in the stamping shell is a different, quieter process.
    """
    env = _relevant_env(os.environ if src is None else src)
    p = os.path.join(out_dir, ENV_SIDECAR)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(dict(captured_at=datetime.datetime.now()
                       .isoformat(timespec="seconds"),
                       pid=os.getpid(), env=env), f,
                  ensure_ascii=False, indent=1)
    return p, env


def _parse_env_file(path):
    """Accept either the sidecar JSON, a bare JSON dict, or `env` output."""
    raw = open(path, encoding="utf-8", errors="replace").read()
    try:
        obj = json.loads(raw)
        if isinstance(obj, dict):
            return _relevant_env(obj.get("env", obj))
    except Exception:
        pass
    out = {}
    for ln in raw.splitlines():
        if "=" in ln:
            k, v = ln.split("=", 1)
            out[k.strip()] = v
    return _relevant_env(out)


def _resolve_env(out_dir, env_file):
    """(env, env_source, captured) — and **never** a silent empty dict.

    Precedence: explicit `--env-file` > the render shell's sidecar > this
    process. The last one is labelled honestly, because a stamp written in a
    different shell from the render is exactly how `260731_w3_s06` ended up
    with `env: {}`.
    """
    if env_file:
        return _parse_env_file(env_file), f"env_file:{env_file}", True
    side = os.path.join(out_dir, ENV_SIDECAR)
    if os.path.isfile(side):
        return _parse_env_file(side), f"render_shell_sidecar:{ENV_SIDECAR}", True
    env = _relevant_env(os.environ)
    return env, "stamping_shell", bool(env)


def build_stamp(out_dir, round_name, scene="", baseline=None,
                compared_against=None, superseded_by=None, note=None,
                env_file=None):
    md5, ver = _mdl()
    porcelain = [l for l in _git("status", "--porcelain").splitlines() if l]
    # `git status --porcelain` lines are `XY <path>`; keep the status letters,
    # they are what distinguishes a staged edit from an untracked stray.
    dirty_paths = [l[:2].strip() + " " + l[3:] for l in porcelain]
    env, env_source, env_captured = _resolve_env(out_dir, env_file)
    stamp = dict(
        schema=SCHEMA,
        round=round_name, scene=scene,
        git_head=_git("rev-parse", "--short", "HEAD"),
        git_branch=_git("rev-parse", "--abbrev-ref", "HEAD"),
        dirty_files=len(porcelain),          # kept: older readers count this
        dirty_paths=dirty_paths,             # RT-A1: *which* files
        mdl_md5=md5, mdl_version_line=ver,
        cuts=len(glob.glob(os.path.join(out_dir, "*.png"))),
        stamped_at=datetime.datetime.now().isoformat(timespec="seconds"),
        env=env, env_source=env_source, env_captured=env_captured,
    )
    if baseline is not None:
        stamp["baseline_of_record"] = bool(baseline)
    if compared_against:
        stamp["compared_against"] = str(compared_against)
    if superseded_by:
        stamp["superseded_by"] = str(superseded_by)
    if note:
        stamp["note"] = str(note)
    return stamp


def read_stamp(path):
    """Load a stamp of **any** vintage into the v1 shape. Never mutates the file.

    RT-A4 normalisation: a *string* `baseline_of_record` was s03's "the round
    this pilot compared against", not a marker. It becomes `compared_against`
    and the marker is reported as unset — which is the truth, and is what stops
    a marker-reader from passing on it by accident.
    """
    if os.path.isdir(path):
        path = os.path.join(path, "round_stamp.json")
    with open(path, encoding="utf-8") as f:
        s = json.load(f)
    out = dict(s)
    out.setdefault("schema", "round_stamp/v0")
    bor = s.get("baseline_of_record")
    if isinstance(bor, str):
        out["compared_against"] = bor
        out.pop("baseline_of_record", None)
        out["_normalised"] = "baseline_of_record(str) -> compared_against (RT-A4)"
    if "dirty_paths" not in out:
        out["dirty_paths"] = None            # v0: only the count was recorded
    if "env_source" not in out:
        out["env_source"] = "unknown(v0)"
        out["env_captured"] = bool(s.get("env"))
    return out


def _selfcheck():
    import tempfile
    ok = []

    def chk(tag, cond, msg=""):
        ok.append(bool(cond))
        print(f"  [{'PASS' if cond else 'FAIL'}] {tag}" + (f" — {msg}" if msg else ""))

    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "a.png"), "wb").close()
        # (1) the four new fields exist and say what they mean
        s = build_stamp(d, "260731_test", "scene99", baseline=True,
                        compared_against="260730_prev", note="selfcheck")
        chk("schema/dirty_paths/env_source/baseline_of_record 전부 존재",
            s["schema"] == SCHEMA and isinstance(s["dirty_paths"], list)
            and s["env_source"] and s["baseline_of_record"] is True
            and s["compared_against"] == "260730_prev", s["env_source"])
        chk("dirty_paths 길이 == dirty_files (개수와 목록이 같은 사실을 말한다)",
            len(s["dirty_paths"]) == s["dirty_files"],
            f"{len(s['dirty_paths'])} vs {s['dirty_files']}")
        # (2) the render shell's env survives into a stamp taken elsewhere
        capture_env(d, {"NEGOBS_LOOK_MTL": "1", "PT_FAST": "1", "HOME": "/x"})
        s2 = build_stamp(d, "260731_test")
        chk("렌더 셸 사이드카가 스탬프 셸을 이긴다",
            s2["env"] == {"NEGOBS_LOOK_MTL": "1", "PT_FAST": "1"}
            and s2["env_captured"] is True
            and s2["env_source"].startswith("render_shell_sidecar"),
            s2["env_source"])
        chk("무관한 변수는 스탬프에 들어가지 않는다", "HOME" not in s2["env"])
        # (3) an uncapturable env is labelled, not silently empty
        os.remove(os.path.join(d, ENV_SIDECAR))
        keep = {k: os.environ.pop(k) for k in list(os.environ)
                if k.startswith(ENV_PREFIXES) or k in ENV_EXTRA}
        try:
            s3 = build_stamp(d, "260731_test")
            chk("잡지 못한 env 는 env_captured=False 로 **말한다** (s06 의 빈 {} 재발 차단)",
                s3["env"] == {} and s3["env_captured"] is False
                and s3["env_source"] == "stamping_shell")
        finally:
            os.environ.update(keep)
        # (4) old stamps stay readable, and RT-A4's two meanings get split
        v0 = dict(round="260731_w3_s03", scene="scene03", git_head="deadbee",
                  dirty_files=7, env={},
                  baseline_of_record="look_check/scene03/260731_w3_cb2")
        p = os.path.join(d, "round_stamp.json")
        json.dump(v0, open(p, "w", encoding="utf-8"))
        r = read_stamp(d)
        chk("v0 스탬프가 읽힌다 · schema v0 로 표시",
            r["schema"] == "round_stamp/v0" and r["dirty_files"] == 7)
        chk("RT-A4: 문자열 baseline_of_record → compared_against 로 분리",
            r.get("compared_against") == v0["baseline_of_record"]
            and "baseline_of_record" not in r, r.get("_normalised", ""))
        json.dump(dict(v0, baseline_of_record=True),
                  open(p, "w", encoding="utf-8"))
        chk("불리언 표지는 표지로 남는다",
            read_stamp(d)["baseline_of_record"] is True)

    print(f"\n[stamp_round] self-check {sum(ok)}/{len(ok)}")
    return 0 if all(ok) else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--self-check" in argv:
        return _selfcheck()
    if "--capture-env" in argv:
        i = argv.index("--capture-env")
        if i + 1 >= len(argv):
            print("[stamp] --capture-env 에 캡처 디렉터리가 필요하다", file=sys.stderr)
            return 2
        d = argv[i + 1]
        os.makedirs(d, exist_ok=True)
        p, env = capture_env(d)
        print(f"[stamp] 렌더 셸 env {len(env)}건 → {p}")
        return 0
    if "--read" in argv:
        i = argv.index("--read")
        if i + 1 >= len(argv):
            print("[stamp] --read 에 캡처 디렉터리가 필요하다", file=sys.stderr)
            return 2
        print(json.dumps(read_stamp(argv[i + 1]), ensure_ascii=False, indent=1))
        return 0

    opts = {}
    pos = []
    skip = set()
    for i, a in enumerate(argv):
        if i in skip:
            continue
        if a == "--baseline-of-record":
            opts["baseline"] = True
        elif a == "--not-baseline":
            opts["baseline"] = False
        elif a in ("--compared-against", "--superseded-by", "--note",
                   "--env-file"):
            if i + 1 >= len(argv):
                print(f"[stamp] {a} 에 값이 필요하다", file=sys.stderr)
                return 2
            opts[a[2:].replace("-", "_")] = argv[i + 1]
            skip.add(i + 1)
        elif a.startswith("--"):
            print(f"[stamp] 모르는 옵션: {a}", file=sys.stderr)
            return 2
        else:
            pos.append(a)
    if len(pos) < 2:
        print(__doc__)
        return 2
    out_dir, round_name = pos[0], pos[1]
    scene = pos[2] if len(pos) > 2 else ""
    if not os.path.isdir(out_dir):
        print(f"[stamp] 디렉터리 없음: {out_dir}", file=sys.stderr)
        return 2
    stamp = build_stamp(out_dir, round_name, scene, **opts)
    with open(os.path.join(out_dir, "round_stamp.json"), "w",
              encoding="utf-8") as f:
        json.dump(stamp, f, ensure_ascii=False, indent=1)
    print(f"[stamp] {out_dir}/round_stamp.json · cuts {stamp['cuts']} · "
          f"HEAD {stamp['git_head']} · dirty {stamp['dirty_files']} · "
          f"env {len(stamp['env'])} ({stamp['env_source']})"
          + (f" · baseline_of_record={stamp['baseline_of_record']}"
             if "baseline_of_record" in stamp else ""))
    if not stamp["env_captured"]:
        print("[stamp][경고] 렌더 셸 env 를 잡지 못했다 — 렌더 셸에서 "
              "`stamp_round.py --capture-env <dir>` 를 먼저 부르거나 "
              "`--env-file` 을 주면 이 라운드가 재현 가능해진다.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
