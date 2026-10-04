import json
import re
import os
import shlex
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

PIPELINE = Path(__file__).parents[1].joinpath("pipeline.sh").read_text()
BUSY_CPU_TICKS = re.search(r"^MODEL_BUSY_CPU_TICKS=(\d+)$", PIPELINE, re.M).group(1)


def function(name):
    definition = PIPELINE.split(f"\n{name}() {{", 1)[1]
    first_line = definition.split("\n", 1)[0]
    if first_line.endswith("}"):
        result = f"{name}() {{{first_line}"
    else:
        result = f"{name}() {{" + definition.split("\n}\n", 1)[0] + "\n}"
    if name == "run_one_detail":
        result = function("detail_neighbors") + "\n" + function("detail_contract_hash") + "\n" + function("reuse_detail_records") + "\n" + function("protect_textures") + "\n" + result
    if name in ("run_one_detail", "restore_detail"):
        result = 'TEXTURES=${TEXTURES:-$STATE/textures}\n' + result
    if name.startswith("run_") and name != "run_detail":
        result = function("stage_builder") + "\n" + result
    if name in ("builder", "run_detail"):
        result = goto_policy() + "\n" + result
    if name in ("builder", "critic"):
        result = goto_targets() + "\n" + result
    return result


def goto_targets():
    constants = "\n".join(re.search(rf"^{name}=.*$", PIPELINE, re.M).group(0) for name in ("STAGE_NAMES", "GOTO_FORMAT"))
    return constants + "\n" + "\n".join(function(name) for name in ("goto_targets", "goto_target_text", "valid_target", "goto_shape_error"))


def goto_policy():
    return re.search(r"^GOTO_LIMIT=.*$", PIPELINE, re.M).group(0) + "\n" + function("goto_available")


def main_loop():
    return goto_policy() + "\ncurrent=" + PIPELINE.split("\nfeedback=\ncurrent=", 1)[1].split("done\nif [ ! -f", 1)[0]


def model_function(seconds: int = 60, idle: int = 2) -> str:
    return f"MODEL_SECONDS={seconds}; MODEL_IDLE_SECONDS={idle}; MODEL_BUSY_CPU_TICKS={BUSY_CPU_TICKS}; MODEL_FAILURE=; SCHEMA=schema.json\n" + function("tree_ticks") + "\n" + function("model")


def idle_failure(seconds):
    return f"model call had no non-whitespace output and no busy child process for {seconds} s"


def model_calls(*, wall_benchmark: bool = False) -> tuple[subprocess.CompletedProcess[str], dict[str, str]]:
    busy_call = """codex() { timeout 6 bash -c 'while :; do :; done'; printf 'rendered\\n'; }
call busy""" if wall_benchmark else ""
    with tempfile.TemporaryDirectory() as directory:
        script = f"""set -uo pipefail
ROOT={directory}; STATE={directory}
log() {{ printf '%s\\n' "$*"; }}
{model_function(60, 3)}
call() {{ local start=$SECONDS rc; model - <<< prompt; rc=$?; printf '%s rc=%s seconds=%s failure=%s marker=%s\\n' "$1" "$rc" "$((SECONDS - start))" "$MODEL_FAILURE" "$([ -f "$STATE/model_failed" ] && printf set || printf clear)"; }}
codex() {{ cat >/dev/null; printf 'model started\\n'; while :; do printf '\\t \\n'; sleep 0.1; done; }}
call whitespace
codex() {{ cat >/dev/null; while :; do sleep 0.1; done; }}
call silent
codex() {{ trap 'touch "$STATE/graceful_term"; exit 0' TERM; cat >/dev/null; while :; do sleep 0.1; done; }}
call graceful
printf 'graceful_term=%s\\n' "$([ -f "$STATE/graceful_term" ] && printf yes || printf no)"
codex() {{ trap '' TERM; cat >/dev/null; while :; do sleep 0.1; done; }}
call stubborn
{busy_call}
codex() {{ trap 'exit 0' TERM; bash -c 'trap "" TERM; while :; do sleep 0.1; done' & printf '%s' "$!" > "$STATE/orphan"; cat >/dev/null; while :; do sleep 0.1; done; }}
call orphaned
printf 'orphan_alive=%s\\n' "$(kill -0 "$(cat "$STATE/orphan")" 2>/dev/null && printf yes || printf no)"
MODEL_SECONDS=4; MODEL_IDLE_SECONDS=60
codex() {{ cat >/dev/null; while :; do printf 'token '; sleep 0.1; done; }}
call endless
MODEL_SECONDS=60
codex() {{ cat >/dev/null; return 3; }}
call exited
codex() {{ cat >/dev/null; printf 'done\\n'; }}
call recovered
codex() {{ cat >/dev/null; return 3; }}
call again
MODEL_IDLE_SECONDS=3
codex() {{ cat >/dev/null; while :; do sleep 0.1; done; }}
call cut
MODEL_IDLE_SECONDS=60
codex() {{ cat >/dev/null; return 3; }}
call first
call second
printf 'unreachable\\n'
"""
        result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=300)
    return result, {line.split(" ", 1)[0]: line for line in result.stdout.splitlines() if " rc=" in line}


def call_seconds(line: str) -> int:
    return int(line.split(" seconds=", 1)[1].split(" ", 1)[0])


WALL_BOUNDS = {
    "whitespace": "[3-6]", "silent": "[3-6]", "graceful": "[3-6]", "stubborn": "1[2-7]",
    "busy": "[6-8]", "orphaned": "1[2-7]", "endless": "[4-6]", "cut": "[3-6]",
}


def benchmark() -> int:
    result, calls = model_calls(wall_benchmark=True)
    misses = [calls[name] for name, bound in WALL_BOUNDS.items() if not re.search(rf" seconds={bound} ", calls[name])]
    if not re.search(r"rc=0 seconds=\d+ failure= marker=clear", calls["busy"]) or "rendered\n" not in result.stdout:
        misses.append("busy call did not complete successfully")
    print("\n".join(misses or ["model call wall times within bounds"]))
    return 1 if misses else 0


class PipelineControlTest(unittest.TestCase):
    def test_detail_uses_crop_and_whole_photo_and_records_label_review(self):
        self.assertIn('-i "$STATE/crops/$id.png" -i "${INPUT:-$STATE/crops/$id.png}"', PIPELINE)
        self.assertIn("proposed_label:$reviewed[0].proposed_label", PIPELINE)
        self.assertIn("final_label:$reviewed[0].final_label", PIPELINE)
        self.assertIn("label_reason:$reviewed[0].label_reason", PIPELINE)

    def test_footprint_tiers_are_descending_and_each_is_criticized(self):
        self.assertIn("sort_by(-((.spatial_contract.frame.size_xyz[0]", PIPELINE)
        self.assertIn("for tier in large medium small", PIPELINE)
        self.assertIn('run_tier_critic "$tier"', PIPELINE)
        self.assertIn('record "tier:$tier"', PIPELINE)
        self.assertIn('if [ "$score" -lt 8 ]', PIPELINE)
        self.assertIn('return 43', PIPELINE)

    def test_capped_tier_critic_descends_to_next_tier(self):
        with tempfile.TemporaryDirectory() as directory:
            script = f'''set -uo pipefail
STATE={directory}; BUILDER_GOTOS=5; CRITIC_GOTOS=5
ACTIVE_STAGE=detail; REQUEST_STAGE=blockout
log() {{ :; }}
write_tiers() {{ : > "$STATE/object_tiers.tsv"; }}
run_tier_critic() {{ printf '%s\\n' "$1"; return 43; }}
{function("run_detail")}
run_detail
'''
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), ["large", "medium", "small"])

    def test_capped_builder_goto_retries_within_same_stage_attempt(self):
        builder = function("builder")
        run_one_detail = function("restore_detail") + "\n" + function("run_one_detail")
        run_detail = function("run_detail")
        detail_helpers = "\n".join(function(name) for name in ("detail_attempts", "detail_best", "write_stage_check_verdict"))
        loop = main_loop()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / "state"
            prompts = root / "prompts"
            assets = root / "assets"
            (state / "attempts").mkdir(parents=True)
            (state / "verdicts").mkdir()
            (state / "crops").mkdir()
            prompts.mkdir()
            assets.mkdir()
            (prompts / "builder.md").write_text("build")
            (state / "objects.json").write_text('[{"id":"one","crop_bbox":[0,0,1,1],"spatial_contract":{}}]')
            (state / "records.tsv").write_text("")
            (state / "progress.md").write_text("")
            script = f'''set -uo pipefail
ROOT={root!s}; STATE={state!s}; PROMPTS={prompts!s}; ASSETS={assets!s}; REQUEST_STAGE=; REQUEST_REASON=; BUILDER_GOTOS=5; CRITIC_GOTOS=0; ATTEMPT_SEQ=0
printf 0 > "$STATE/calls"
log() {{ printf '%s\n' "$*"; }}
inbox() {{ :; }}
next_attempt() {{ ATTEMPT_SEQ=$((ATTEMPT_SEQ+1)); }}
score_of() {{ jq -r '.score // 0' "$1"; }}
record() {{ printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$5" "$6" "${{7:-}}" >> "$STATE/records.tsv"; }}
codex() {{ local calls; cat >/dev/null; calls=$(( $(cat "$STATE/calls") + 1 )); printf '%s' "$calls" > "$STATE/calls"; case "$calls" in 4) printf '%s\n' '{{"target":"blockout","reason":"malformed fallback"}}' > "$STATE/goto.json" ;; *) printf '%s\n' '{{"stage":"blockout","reason":"fixed-region conflict"}}' > "$STATE/goto.json" ;; esac; }}
{model_function()}
{builder}
{detail_helpers}
verify_detail() {{ DETAIL_FAILURE="asset check failed: no contract-valid asset"; return 1; }}
{run_one_detail}
write_tiers() {{ printf 'one\tlarge\n' > "$STATE/object_tiers.tsv"; }}
run_tier_critic() {{ :; }}
{run_detail}
within_s56_budget() {{ return 0; }}
integrate_calls=0
run_floorplan() {{ return 0; }}
run_blockout() {{ return 0; }}
run_identify() {{ return 0; }}
run_integrate() {{ integrate_calls=$((integrate_calls+1)); }}
run_materials() {{ return 0; }}
PHOTO_TO_SCENE_STAGE=detail
feedback=
{loop}
done
printf 'attempt_seq=%s calls=%s records=%s integrate=%s\n' "$ATTEMPT_SEQ" "$(cat "$STATE/calls")" "$(cut -f1,2 "$STATE/records.tsv" | paste -sd, -)" "$integrate_calls"
'''
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("attempt_seq=2 calls=4 records=object:one\t1,object:one\t2 integrate=1", result.stdout)
        self.assertEqual(result.stdout.count("ENTER object:"), 2)
        self.assertIn("GOTO cap reached origin=builder requested=blockout reason=fixed-region conflict", result.stdout)
        self.assertIn("GOTO cap request ignored origin=builder requested=blockout reason=fixed-region conflict", result.stdout)
        self.assertIn("GOTO rejected origin=builder requested= reason=cap fallback missing field `stage`; unexpected field `target`", result.stdout)

    def test_valid_builder_goto_survives_invalid_target_correction(self):
        builder = function("builder")
        loop = main_loop()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / "state"
            prompts = root / "prompts"
            state.mkdir()
            prompts.mkdir()
            (prompts / "builder.md").write_text("build")
            script = f'''set -uo pipefail
ROOT={root!s}; STATE={state!s}; PROMPTS={prompts!s}; REQUEST_STAGE=; REQUEST_REASON=; BUILDER_GOTOS=4; CRITIC_GOTOS=0
calls="$STATE/calls"
printf 0 > "$calls"
printf 0 > "$STATE/detail_records"
log() {{ :; }}
codex() {{ local call; cat >/dev/null; call=$(( $(cat "$calls") + 1 )); printf '%s' "$call" > "$calls"; if [ "$call" -eq 1 ]; then printf '%s\n' '{{"target":"blockout","reason":"invalid field"}}' > "$STATE/goto.json"; else printf '%s\n' '{{"stage":"blockout","reason":"valid retry"}}' > "$STATE/goto.json"; fi; }}
{model_function()}
{builder}
within_s56_budget() {{ return 0; }}
run_floorplan() {{ return 0; }}
run_blockout() {{ printf 'blockout=1 detail_records=%s builder_gotos=%s calls=%s\n' "$(cat "$STATE/detail_records")" "$BUILDER_GOTOS" "$(cat "$calls")"; exit 0; }}
run_identify() {{ return 0; }}
run_detail() {{ builder builder.md "${{2:-}}" || return $?; printf 1 > "$STATE/detail_records"; }}
run_integrate() {{ return 0; }}
run_materials() {{ return 0; }}
PHOTO_TO_SCENE_STAGE=detail
feedback=
{loop}
done
'''
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blockout=1 detail_records=0 builder_gotos=5 calls=2", result.stdout)

    def test_builder_goto_correction_names_the_field_then_follows_goto_policy(self):
        target_shaped = ["missing field `stage`", "unexpected field `target`"]
        unknown = ["field `stage` names object:foreground_bowl, which is not a valid target"]
        cases = (
            ({"target": "blockout", "reason": "fixed"}, 0, 42, 2, target_shaped),
            ({"target": "blockout", "reason": "fixed"}, 5, 0, 3, target_shaped),
            ({"stage": "object:foreground_bowl", "reason": "fixed"}, 0, 42, 2, unknown),
            ({"stage": "bogus\nblockout", "reason": "fixed"}, 0, 42, 2, ["which is not a valid target"]),
        )
        for first_goto, gotos, rc, calls, corrections in cases:
            with self.subTest(first_goto=first_goto, gotos=gotos), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                state = root / "state"
                state.mkdir()
                (state / "objects.json").write_text('[{"id":"bowl","label":"wooden bowl"}]')
                (root / "builder.md").write_text("Write state/goto.json targeting blockout when the contract conflicts.")
                (state / "first_goto.json").write_text(json.dumps(first_goto))
                script = f'''set -uo pipefail
ROOT={root!s}; STATE={state!s}; PROMPTS={root!s}; REQUEST_STAGE=; REQUEST_REASON=; BUILDER_GOTOS={gotos}; CRITIC_GOTOS=0; ACTIVE_STAGE=object:bowl
printf 0 > "$STATE/calls"
log() {{ printf '%s\\n' "$*"; }}
codex() {{ local call; call=$(( $(cat "$STATE/calls") + 1 )); printf '%s' "$call" > "$STATE/calls"; cat > "$STATE/prompt_$call"; case "$call" in 1) cp "$STATE/first_goto.json" "$STATE/goto.json" ;; 2) printf '%s\\n' '{{"stage":"blockout","reason":"fixed"}}' > "$STATE/goto.json" ;; esac; }}
{model_function()}
{function("builder")}
rc=0
builder builder.md '' || rc=$?
printf 'rc=%s calls=%s stage=%s\\n' "$rc" "$(cat "$STATE/calls")" "$REQUEST_STAGE"
'''
                result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=30)
                first, second = ((state / f"prompt_{n}").read_text() for n in (1, 2))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(f"rc={rc} calls={calls} stage=blockout", result.stdout)
            self.assertIn('state/goto.json holding exactly {"stage": "<target>", "reason": "<why>"}', first)
            self.assertIn("- object:bowl (wooden bowl)", first)
            for correction in corrections:
                self.assertIn(correction, second)
            self.assertEqual(second.count("- object:bowl (wooden bowl)"), 2)
            if gotos:
                self.assertIn("GOTO cap reached origin=builder requested=blockout reason=fixed", result.stdout)

    def test_scene_critic_invalid_route_reasks_only_the_critic_after_final_attempt(self):
        run_integrate = function("run_integrate")
        helpers = "\n".join(function(name) for name in ("critic", "write_stage_check_verdict", "write_spatial_check_verdict", "integrate_attempts", "integrate_best"))
        schema = Path(__file__).parents[1].joinpath("verdict.schema.json")
        cases = (
            ("object:foreground_bowl", "object:bowl", 43, 2, "object:bowl"),
            ("object:foreground_bowl", "object:rocking_chair", 0, 2, "integrate"),
            ("object:D", "object:bowl", 43, 1, "object:D"),
        )
        for first_route, second_route, rc, calls, final_route in cases:
            with self.subTest(first_route=first_route, second_route=second_route), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                state = root / "state"
                (state / "verdicts").mkdir(parents=True)
                for name in ("assemble.py", "integrate.png", "integrate_overlay.png", "spatial_observed.json"):
                    (state / name).write_text("{}")
                (state / "objects.json").write_text('[{"id":"bowl","final_label":"foreground bowl"},{"id":"D","label":"rocking chair"}]')
                (state / "records.tsv").write_text("integrate\t1\t3\t1\t\tv1\t\nintegrate\t2\t4\t1\t\tv2\t\n")
                (root / "integrate_critic.md").write_text("critique")
                script = f'''set -uo pipefail
ROOT={root!s}; STATE={state!s}; PROMPTS={root!s}; INPUT=photo.jpg; ATTEMPT_SEQ=2; REQUEST_STAGE=; REQUEST_REASON=
printf 0 > "$STATE/calls"
builds=0
next_attempt() {{ ATTEMPT_SEQ=$((ATTEMPT_SEQ+1)); }}
log() {{ printf '%s\\n' "$*"; }}
inbox() {{ :; }}
builder() {{ builds=$((builds+1)); }}
spatial_validate() {{ return 0; }}
score_of() {{ jq -r '.score // 0' "$1"; }}
record() {{ printf '%s\\t%s\\t%s\\t%s\\t%s\\t%s\\t%s\\n' "$1" "$2" "$3" "$4" "$5" "$6" "${{7:-}}" >> "$STATE/records.tsv"; }}
codex() {{
  local call output= schema= previous= route
  for arg in "$@"; do [ "$previous" = -o ] && output=$arg; [ "$previous" = --output-schema ] && schema=$arg; previous=$arg; done
  call=$(( $(cat "$STATE/calls") + 1 )); printf '%s' "$call" > "$STATE/calls"
  cat > "$STATE/prompt_$call"; cp "$schema" "$STATE/schema_$call"
  route={first_route}; [ "$call" -eq 1 ] || route={second_route}
  jq -n --arg route "$route" '{{scene_change:null,score:7,summary:"close",corrections:["shrink the bowl"],top_stage:$route,wrong_labels:[],missing_objects:[]}}' > "$output"
}}
{model_function()}
SCHEMA={schema!s}
{helpers}
{run_integrate}
rc=0
run_integrate "" || rc=$?
printf 'rc=%s builds=%s critic_calls=%s request=%s\\n' "$rc" "$builds" "$(cat "$STATE/calls")" "$REQUEST_STAGE"
'''
                result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=30)
                enum = json.loads((state / "schema_1").read_text())["properties"]["top_stage"]["enum"]
                prompt = (state / "prompt_1").read_text()
                retry = (state / "prompt_2").read_text() if calls == 2 else ""
                verdict = json.loads((state / "verdicts" / "integrate_3.json").read_text())
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(f"rc={rc} builds=1 critic_calls={calls}", result.stdout)
            self.assertEqual(verdict["top_stage"], final_route)
            if rc:
                self.assertIn(f"request={final_route}", result.stdout)
            self.assertEqual(set(enum), {"floorplan", "blockout", "identify", "detail", "integrate", "materials", "object:bowl", "object:D"})
            self.assertIn("- object:bowl (foreground bowl)", prompt)
            self.assertIn("- object:D (rocking chair)", prompt)
            if calls == 2:
                self.assertIn("CRITIC route rejected try=1 stage=integrate requested=object:foreground_bowl", result.stdout)
                self.assertIn("top_stage to object:foreground_bowl, which is not a valid target", retry)

    def test_second_invalid_builder_goto_is_ignored(self):
        builder = function("builder")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / "state"
            prompts = root / "prompts"
            state.mkdir()
            prompts.mkdir()
            (prompts / "builder.md").write_text("build")
            script = f'''set -uo pipefail
ROOT={root!s}; STATE={state!s}; PROMPTS={prompts!s}; REQUEST_STAGE=; REQUEST_REASON=
calls="$STATE/calls"
printf 0 > "$calls"
log() {{ printf '%s\n' "$*"; }}
codex() {{ local call; cat >/dev/null; call=$(( $(cat "$calls") + 1 )); printf '%s' "$call" > "$calls"; printf '%s\n' '{{"target":"blockout","reason":"invalid field"}}' > "$STATE/goto.json"; }}
{model_function()}
{builder}
rc=0
builder builder.md '' || rc=$?
printf 'rc=%s calls=%s\n' "$rc" "$(cat "$calls")"
'''
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("rc=0 calls=2", result.stdout)
        self.assertIn("second invalid GOTO from same stage ignored", result.stdout)

    def test_dense_detail_contract_does_not_expand_builder_request(self):
        builder = function("builder")
        run_one_detail = function("restore_detail") + "\n" + function("run_one_detail")
        detail_helpers = "\n".join(function(name) for name in ("detail_attempts", "detail_best", "write_stage_check_verdict"))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / "state"
            prompts = root / "prompts"
            assets = root / "assets"
            (state / "attempts").mkdir(parents=True)
            (state / "verdicts").mkdir()
            (state / "crops").mkdir()
            prompts.mkdir()
            assets.mkdir()
            detail_prompt = Path(__file__).parents[1].joinpath("prompts/detail_builder.md").read_text()
            (prompts / "detail_builder.md").write_text(detail_prompt)
            dense_contract = "x" * 1_100_000
            (state / "objects.json").write_text(
                '[{"id":"dense","crop_bbox":[0,0,1,1],"spatial_contract":{"mesh":"'
                + dense_contract
                + '"}}]'
            )
            (state / "records.tsv").write_text("")
            (state / "progress.md").write_text("")
            script = f'''set -uo pipefail
ROOT={root!s}; STATE={state!s}; PROMPTS={prompts!s}; ASSETS={assets!s}; REQUEST_STAGE=; REQUEST_REASON=; BUILDER_GOTOS=0; ATTEMPT_SEQ=0
log() {{ :; }}
inbox() {{ :; }}
next_attempt() {{ ATTEMPT_SEQ=$((ATTEMPT_SEQ+1)); }}
score_of() {{ printf 8; }}
record() {{ printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$5" "$6" "${{7:-}}" >> "$STATE/records.tsv"; }}
codex() {{
  local arg previous= workdir=
  for arg in "$@"; do
    if [ "$previous" = -C ]; then workdir=$arg; break; fi
    previous=$arg
  done
  [ "$workdir" = "$ROOT" ] || return 91
  [ -s "$workdir/state/entry_dense.json" ] || return 92
  tee "$STATE/request" | wc -m > "$STATE/request_chars"
}}
{model_function()}
{builder}
{detail_helpers}
verify_detail() {{ DETAIL_FAILURE="asset check failed: expected in request-size test"; return 1; }}
{run_one_detail}
run_one_detail dense
printf '%s %s\n' "$(wc -m < "$STATE/entry_dense.json")" "$(cat "$STATE/request_chars")"
'''
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=30)
            request = (state / "request").read_text()
        self.assertEqual(result.returncode, 0, result.stderr)
        entry_chars, request_chars = map(int, result.stdout.split())
        self.assertGreater(entry_chars, 1_048_576)
        self.assertLess(request_chars, 4_096)
        self.assertIn(
            "\nOne-reentry correction context follows:\n"
            "Object entry file: state/entry_dense.json\n"
            "Read the complete JSON file before editing.\n",
            request,
        )
        self.assertNotIn(dense_contract, request)

    def test_detail_gate_accepts_composed_workspace_texture_path(self):
        verify_detail = function("verify_detail")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            assets = root / "assets"
            state = root / "state"
            textures = root / "textures"
            assets.mkdir()
            state.mkdir()
            textures.mkdir()
            (assets / "generic.py").write_text("def build(entry, collection=None): return []\n")
            (assets / "sheer.py").write_text(
                "from pathlib import Path\n"
                "def build(entry, collection=None):\n"
                "    return bpy.data.images.load(str(Path(__file__).resolve().parents[1] / 'textures/lace.png'))\n"
            )
            (textures / "lace.png").write_bytes(b"texture")
            marker = state / "detail_sheer_1.started"
            render = state / "detail_sheer.png"
            marker.write_text("")
            render.write_text("render")
            os.utime(marker, (1, 1))
            os.utime(render, (2, 2))
            script = f'''set -uo pipefail
PIPELINE_DIR={shlex.quote(str(Path(__file__).parents[1]))}
ASSETS={shlex.quote(str(assets))}
STATE={shlex.quote(str(state))}
TEXTURES={shlex.quote(str(textures))}
{verify_detail}
if verify_detail sheer "$STATE/detail_sheer_1.started"; then
  printf 'PASS\\n'
else
  printf 'FAIL: %s\\n' "$DETAIL_FAILURE"
fi
'''
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "PASS\n")

    def test_materials_gate_failure_is_scored_and_saved(self):
        run_materials = function("run_materials")
        stage_verdict = "\n".join(function(name) for name in ("write_stage_check_verdict", "write_spatial_check_verdict"))
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory, "state")
            (state / "verdicts").mkdir(parents=True)
            (state / "objects.json").write_text('[{"id":"one"}]')
            (state / "spatial_observed.json").write_text("{}")
            (state / "materials.png").write_text("render")
            (state / "materials.blend").write_text("scene")
            (state / "records.tsv").write_text("")
            script = f'''set -uo pipefail
STATE={state!s}; INPUT=input.jpg; ATTEMPT_SEQ=0; BEST_S6=-1; REQUEST_STAGE=; REQUEST_REASON=; MODEL_FAILURE=
next_attempt() {{ ATTEMPT_SEQ=$((ATTEMPT_SEQ+1)); }}
log() {{ printf '%s\n' "$*"; }}
builder() {{ return 0; }}
spatial_validate() {{ printf '%s\n' '{{"valid":false,"errors":["one: material footprint mismatch"]}}' > "$2"; return 1; }}
critic() {{ return 99; }}
score_of() {{ jq -r '.score // 0' "$1"; }}
record() {{ printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$5" "$6" "${{7:-}}" >> "$STATE/records.tsv"; }}
inbox() {{ :; }}
{stage_verdict}
{run_materials}
run_materials
printf 'score=%s best=%s png=%s blend=%s error=%s\n' "$(cut -f3 "$STATE/records.tsv")" "$(cat "$STATE/best_s6_score")" "$(cat "$STATE/best_materials.png")" "$(cat "$STATE/best_materials.blend")" "$(jq -r '.corrections[0]' "$STATE/verdicts/materials_1.json")"
'''
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("score=0 best=0 png=render blend=scene", result.stdout)
        self.assertIn("FAIL materials invalidated spatial contract", result.stdout)
        self.assertIn("error=one: material footprint mismatch", result.stdout)

    def test_integration_gate_failure_is_scored_and_retried(self):
        run_integrate = function("run_integrate")
        stage_verdict = "\n".join(function(name) for name in ("write_stage_check_verdict", "write_spatial_check_verdict"))
        integrate_helpers = "\n".join(function(name) for name in ("integrate_attempts", "integrate_best"))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / "state"
            state.mkdir()
            (state / "verdicts").mkdir()
            (state / "objects.json").write_text('[{"id":"one"}]')
            (state / "assemble.py").write_text("")
            (state / "integrate.png").write_text("")
            (state / "integrate_overlay.png").write_text("")
            (state / "spatial_observed.json").write_text("{}")
            (state / "records.tsv").write_text("")
            script = f'''set -uo pipefail
STATE={state!s}
INPUT=input.jpg
ATTEMPT_SEQ=0
MODEL_FAILURE=
REQUEST_STAGE=
REQUEST_REASON=
next_attempt() {{ ATTEMPT_SEQ=$((ATTEMPT_SEQ+1)); }}
log() {{ printf '%s\n' "$*"; }}
builder() {{ return 0; }}
spatial_validate() {{ printf '%s\n' '{{"valid":false,"errors":["one: footprint did not round-trip"]}}' > "$2"; return 1; }}
critic() {{ return 99; }}
score_of() {{ jq -r '.score // 0' "$1"; }}
record() {{ printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$5" "$6" "${{7:-}}" >> "$STATE/records.tsv"; }}
inbox() {{ :; }}
{stage_verdict}
{integrate_helpers}
{run_integrate}
run_integrate
printf 'attempts=%s scores=%s error=%s\n' "$ATTEMPT_SEQ" "$(cut -f3 "$STATE/records.tsv" | paste -sd, -)" "$(jq -r '.corrections[0]' "$STATE/verdicts/integrate_1.json")"
'''
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("attempts=3 scores=0,0,0", result.stdout)
        self.assertIn("FAIL integrate spatial contract did not round-trip attempt=3", result.stdout)
        self.assertIn("error=one: footprint did not round-trip", result.stdout)

    def test_blockout_declaration_failure_is_fed_back_and_never_kept(self):
        stage_verdict = "\n".join(function(name) for name in ("write_stage_check_verdict", "write_spatial_check_verdict", "run_blockout"))
        for valid, expected in (("2", "rc=0 scores=0,5,0 kept=attempt2"), ("", "rc=1 scores=0,0,0")):
            with self.subTest(valid=valid), tempfile.TemporaryDirectory() as directory:
                state = Path(directory) / "state"
                (state / "verdicts").mkdir(parents=True)
                (state / "records.tsv").write_text("")
                (state / "blockout_critic.md").write_text("criticize")
                script = f'''set -uo pipefail
STATE={state!s}; PROMPTS={state!s}; INPUT=input.jpg; ATTEMPT_SEQ=0; MODEL_FAILURE=
next_attempt() {{ ATTEMPT_SEQ=$((ATTEMPT_SEQ+1)); }}
log() {{ printf '%s\n' "$*"; }}
builder() {{ printf '%s\n' "$2" > "$STATE/feedback_$ATTEMPT_SEQ"; printf '[{{"id":"attempt%s"}}]\n' "$ATTEMPT_SEQ" > "$STATE/objects.json"; for name in blockout.py blockout.png blockout_overlay.png; do : > "$STATE/$name"; done; }}
spatial_validate() {{ [ "$ATTEMPT_SEQ" = "{valid}" ] && return 0; printf '%s\n' '{{"valid":false,"errors":["item: declared supported_by floor: raised"]}}' > "$2"; return 1; }}
critic() {{ printf '%s\n' '{{"score":5,"corrections":["sharpen edges"]}}' > "$1"; }}
score_of() {{ jq -r '.score // 0' "$1"; }}
record() {{ printf '%s\t%s\t%s\n' "$1" "$2" "$3" >> "$STATE/records.tsv"; }}
inbox() {{ :; }}
{stage_verdict}
run_blockout; rc=$?
printf 'rc=%s scores=%s kept=%s\n' "$rc" "$(cut -f3 "$STATE/records.tsv" | paste -sd, -)" "$(jq -r '.[0].id' "$STATE/objects.json")"
'''
                result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=10)
                self.assertIn(expected, result.stdout, result.stderr)
                self.assertIn("FAIL blockout spatial contract declaration invalid attempt=1", result.stdout)
                self.assertEqual((state / "feedback_2").read_text().strip(), "item: declared supported_by floor: raised")

    def test_malformed_inventory_shape_reaches_the_next_blockout_builder(self):
        functions = "\n".join(function(name) for name in ("spatial_validate", "write_stage_check_verdict", "write_spatial_check_verdict", "run_blockout"))
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state"
            (state / "verdicts").mkdir(parents=True)
            (state / "records.tsv").write_text("")
            script = f'''set -uo pipefail
STATE={state!s}; PROMPTS={state!s}; PIPELINE_DIR={Path(__file__).parents[1]!s}; INPUT=input.jpg; ATTEMPT_SEQ=0; MODEL_FAILURE=
next_attempt() {{ ATTEMPT_SEQ=$((ATTEMPT_SEQ+1)); }}
log() {{ printf '%s\n' "$*"; }}
builder() {{ printf '%s\n' "$2" > "$STATE/feedback_$ATTEMPT_SEQ"; printf '%s\n' '{{"objects":[{{"id":"floor"}}]}}' > "$STATE/objects.json"; for name in blockout.py blockout.png blockout_overlay.png; do : > "$STATE/$name"; done; }}
critic() {{ printf 'critic ran\n'; }}
score_of() {{ jq -r '.score // 0' "$1"; }}
record() {{ printf '%s\t%s\t%s\n' "$1" "$2" "$3" >> "$STATE/records.tsv"; }}
inbox() {{ :; }}
{functions}
run_blockout; printf 'rc=%s scores=%s\n' "$?" "$(cut -f3 "$STATE/records.tsv" | paste -sd, -)"
'''
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=300)
            self.assertIn("rc=1 scores=0,0,0", result.stdout, result.stderr)
            self.assertNotIn("critic ran", result.stdout)
            self.assertNotIn("Traceback", result.stderr)
            for attempt in (2, 3):
                self.assertEqual((state / f"feedback_{attempt}").read_text().strip(), "objects.json: top level must be a nonempty array of object entries, got dict")

    def test_integration_attempt_budget_resumes_from_records(self):
        run_integrate = function("run_integrate")
        functions = "\n".join(function(name) for name in ("write_stage_check_verdict", "write_spatial_check_verdict", "integrate_attempts", "integrate_best"))
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory, "state")
            (state / "verdicts").mkdir(parents=True)
            (state / "attempts" / "integrate_9").mkdir(parents=True)
            for name in ("assemble.py", "integrate.png", "integrate_overlay.png", "spatial_observed.json"):
                (state / name).write_text("{}" if name.endswith(".json") else "")
                (state / "attempts" / "integrate_9" / name).write_text("{}" if name.endswith(".json") else "")
            (state / "objects.json").write_text('[{"id":"one"}]')
            (state / "verdicts" / "integrate_9.json").write_text('{"score":0}')
            (state / "records.tsv").write_text(f"integrate\t1\t0\t1\t\t{state}/verdicts/integrate_9.json\t\n")
            script = f'''set -uo pipefail
STATE={state!s}; INPUT=input.jpg; ATTEMPT_SEQ=9; REQUEST_STAGE=; REQUEST_REASON=; MODEL_FAILURE=
next_attempt() {{ ATTEMPT_SEQ=$((ATTEMPT_SEQ+1)); }}
log() {{ :; }}
builder() {{ return 0; }}
spatial_validate() {{ printf '%s\n' '{{"valid":false,"errors":["one: resumed mismatch"]}}' > "$2"; return 1; }}
critic() {{ return 99; }}
score_of() {{ jq -r '.score // 0' "$1"; }}
record() {{ printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$5" "$6" "${{7:-}}" >> "$STATE/records.tsv"; }}
inbox() {{ :; }}
{functions}
{run_integrate}
run_integrate
printf 'new_attempts=%s records=%s\n' "$((ATTEMPT_SEQ-9))" "$(awk -F '\t' '$1==\"integrate\" {{n++}} END {{print n+0}}' "$STATE/records.tsv")"
'''
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("new_attempts=2 records=3", result.stdout)

    def test_report_preserves_empty_fields_and_reports_missing_verdict(self):
        parse_record = function("parse_record")
        write_report = function("write_report")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / "state"
            state.mkdir()
            verdict = state / "exact.json"
            missing = state / "missing.json"
            verdict.write_text('{"score":7,"summary":"exact verdict"}')
            (state / "redirects.tsv").write_text("")
            (state / "records.tsv").write_text(
                f"integrate\t1\t7\t4\t\t{verdict}\t\n"
                f"materials\t1\t0\t2\t\t{missing}\t\n"
            )
            (state / "best_materials_verdict.json").write_text('{"top_stage":"integrate"}')
            (state / "best_s6_score").write_text("7")
            (state / "floorplan.json").write_text('{}')
            (root / "log.md").write_text("")
            script = f'''set -uo pipefail
ROOT={root!s}; STATE={state!s}
{parse_record}
{write_report}
write_report
cat "$STATE/scores.md"
'''
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('{"score":7,"summary":"exact verdict"}', result.stdout)
        self.assertIn("| integrate | — | 1 | 7/10 | 4 | Initial stage entry or forward rebuild from accepted contracts. |", result.stdout)
        self.assertEqual(result.stdout.count(f"Verdict absent: `{missing}`"), 1)
        self.assertNotIn("verdict file unavailable", result.stdout)

    def test_detail_reentry_ignores_annotations_but_invalidates_constraints(self):
        original = {
            "source_evidence": {"note": "photo"},
            "frame": {"origin_xyz": [0, 0, 0], "size_xyz": [1, 1, 1],
                      "x_axis_xy": [1, 0], "y_axis_xy": [0, 1]},
            "footprint_xy": [[0, 0], [1, 0], [1, 1]],
            "front_xy": [0, -1],
            "regions": [{"id": "body", "bbox": {"min": [0, 0, 0], "max": [1, 1, 1]}}],
            "ownership": {"children": "external"},
            "relationships": [{"type": "supported_by", "with": "floor", "region": "body", "support_region": "top"}],
            "appearance": {"aperture_background": "source_visible", "minimum_luminance": 0.2},
        }
        variants = {
            "confidence_added": ("regions", [dict(original["regions"][0], confidence=0.5)], False),
            "evidence": ("source_evidence", {"note": "revised annotation"}, False),
            "frame": ("frame", dict(original["frame"], size_xyz=[2, 1, 1]), True),
            "footprint": ("footprint_xy", [[0, 0], [2, 0], [1, 1]], True),
            "facing": ("front_xy", [1, 0], True),
            "bbox": ("regions", [{"id": "body", "bbox": {"min": [0, 0, 0], "max": [2, 1, 1]}}], True),
            "region_id": ("regions", [dict(original["regions"][0], id="seat")], True),
            "ownership": ("ownership", {"children": "included"}, True),
            "relationship": ("relationships", [{"type": "supported_by", "with": "floor", "region": "body", "support_region": "deck"}], True),
            "appearance": ("appearance", dict(original["appearance"], minimum_luminance=0.4), True),
            "material": ("material_note", "dark walnut", True),
        }
        for legacy in (False, True):
            for name, (field, value, changed) in variants.items():
                for score, attempts in ((8, 1), (6, 2)):
                    with self.subTest(legacy=legacy, field=name, score=score):
                        with tempfile.TemporaryDirectory() as directory:
                            state = Path(directory)
                            (state / "attempts").mkdir()
                            (state / "textures").mkdir()
                            saved = state / "attempts" / "object_one_1.json"
                            saved.write_text(json.dumps({"id": "one", "material_note": "plaster", "spatial_contract": original}))
                            current = {"id": "one", "material_note": "plaster", "spatial_contract": original}
                            if field == "material_note":
                                current[field] = value
                            else:
                                current["spatial_contract"] = dict(original, **{field: value})
                            (state / "objects.json").write_text(json.dumps([current]))
                            asset = state / "one.py"
                            asset.write_text("accepted asset")
                            functions = "\n".join(function(n) for n in (
                                "detail_attempts", "detail_best", "run_one_detail"))
                            hash_command = ("jq -cS '.spatial_contract' " + shlex.quote(str(saved))
                                            + " | sha256sum | cut -d ' ' -f1" if legacy
                                            else "detail_contract_hash " + shlex.quote(str(saved)))
                            script = f"""set -euo pipefail
STATE={directory}; ASSETS={directory}; ATTEMPT_SEQ=1
{functions}
hash=$({hash_command})
for a in $(seq 1 {attempts}); do
  printf 'object:one\\t%s\\t{score}\\t1\\taccepted\\t{directory}/verdicts/object_one_1.json\\t%s\\tlarge\n' "$a" "$hash"
done > "$STATE/records.tsv"
before=$(cut -f1-6,8 "$STATE/records.tsv")
inbox() {{ :; }}
log() {{ :; }}
next_attempt() {{ ATTEMPT_SEQ=$((ATTEMPT_SEQ+1)); }}
builder() {{ printf 'REBUILD\n'; return 43; }}
restore_detail() {{ :; }}
run_one_detail one
test "$before" = "$(cut -f1-6,8 "$STATE/records.tsv")"
printf 'REUSED best=%s attempts=%s\n' "$(detail_best one "$(detail_contract_hash "$STATE/entry_one.json")")" "$(detail_attempts one "$(detail_contract_hash "$STATE/entry_one.json")")"
"""
                            result = subprocess.run(["bash", "-c", script], text=True,
                                                    capture_output=True, timeout=10)
                            self.assertEqual(asset.read_text(), "accepted asset")
                        self.assertEqual(result.returncode, 43 if changed else 0, result.stderr)
                        self.assertEqual(result.stdout, "REBUILD\n" if changed else
                                         f"REUSED best={score} attempts={attempts}\n")

    def test_detail_budget_is_keyed_to_contract(self):
        functions = "\n".join(function(name) for name in ("detail_attempts", "detail_best"))
        with tempfile.TemporaryDirectory() as directory:
            records = Path(directory, "records.tsv")
            records.write_text(
                "object:changed\t1\t4\t1\t\told.json\told-hash\n"
                "object:changed\t2\t6\t1\t\told2.json\told-hash\n"
                "object:stable\t1\t7\t1\t\tstable.json\tstable-hash\n"
                "object:stable\t2\t8\t1\t\tstable2.json\tstable-hash\n"
            )
            script = f'''STATE={directory!s}
{functions}
printf 'changed=%s stable=%s best=%s\n' "$(detail_attempts changed new-hash)" "$(detail_attempts stable stable-hash)" "$(detail_best stable stable-hash)"
'''
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "changed=0 stable=2 best=8\n")

    def test_detail_iteration_isolated_from_inbox_stdin(self):
        run_detail = function("run_detail")
        with tempfile.TemporaryDirectory() as directory:
            objects = Path(directory, "objects.json")
            objects.write_text('[{"id":"one","crop_bbox":[0,0,3,3]},{"id":"two","crop_bbox":[0,0,2,2]},{"id":"three","crop_bbox":[0,0,1,1]}]')
            script = f'''STATE={directory!s}
run_one_detail() {{ printf '%s\n' "$1"; read -r ignored || true; }}
write_tiers() {{ printf 'one\tlarge\ntwo\tmedium\nthree\tsmall\n' > "$STATE/object_tiers.tsv"; }}
run_tier_critic() {{ :; }}
{run_detail}
run_detail
'''
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, stdin=subprocess.DEVNULL, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "one\ntwo\nthree\n")

    def goto_scenario(self, root, integrate_origin, materials_origin, target="blockout", expected_rc=0):
        prefix = PIPELINE.split("\nfeedback=\ncurrent=", 1)[0]
        nix_shell = 'nix-shell() { [ "$1 $2 $3" = "-p python3 --run" ] || return 127; bash -c "$4"; }\n'
        script = nix_shell + prefix + f'''
model() {{
  cat > "$STATE/last_prompt"
  jq -n --arg reason "synthetic $ACTIVE_STAGE region lies outside footprint" '{{stage:"blockout",reason:$reason}}' > "$STATE/goto.json"
}}
inbox() {{ :; }}
run_floorplan() {{ :; }}
run_blockout() {{ printf '%s\\n' "$1" >> "$STATE/repairs"; }}
run_identify() {{ :; }}
run_detail() {{
  ACTIVE_STAGE=object:synthetic
  builder detail_builder.md "${{2:-}}" || return $?
  REQUEST_STAGE=blockout; REQUEST_REASON='synthetic tier region mismatch'; return 43
}}
whole_scene() {{
  if [ "$1" = builder ]; then
    builder integrate_builder.md "$2" || return $?
  fi
  REQUEST_STAGE=$3; REQUEST_REASON="synthetic $ACTIVE_STAGE footprint mismatch"; return 43
}}
run_integrate() {{ whole_scene {integrate_origin} "$1" {target}; }}
run_materials() {{ whole_scene {materials_origin} "$1" blockout; }}
within_s56_budget() {{ return 0; }}
PHOTO_TO_SCENE_STAGE=detail
feedback=
''' + main_loop() + '\ndone\n'
        for resource in ("prompts", "builders", "tools"):
            link = root / resource
            if not link.exists():
                link.symlink_to(Path(__file__).resolve().parents[1] / resource)
        driver = root / "driver.sh"
        driver.write_text(script)
        photo = root / "synthetic.jpg"
        photo.write_bytes(b"")
        env = dict(os.environ, PHOTO_TO_SCENE_ROOT=str(root), BOTQ_ARTIFACTS_DIR=str(root / "artifacts"))
        result = subprocess.run(
            ["bash", str(driver), str(photo)],
            env=env, text=True, capture_output=True, timeout=300,
        )
        self.assertEqual(result.returncode, expected_rc, result.stderr)
        return result

    def test_whole_scene_reserves_after_early_exhaustion_and_resume(self):
        for integrate_origin, materials_origin in (("builder", "builder"), ("critic", "critic"),
                                                   ("builder", "critic"), ("critic", "builder")):
            for checkpoint in ("fresh", "split", "legacy"):
                with self.subTest(integrate=integrate_origin, materials=materials_origin, checkpoint=checkpoint):
                    with tempfile.TemporaryDirectory() as directory:
                        root = Path(directory)
                        state = root / "state"
                        state.mkdir()
                        if checkpoint == "split":
                            (state / "builder_goto_count").write_text("5")
                            (state / "critic_goto_count").write_text("5")
                        elif checkpoint == "legacy":
                            (state / "goto_count").write_text("10")
                        result = self.goto_scenario(root, integrate_origin, materials_origin)
                        expected = {"fresh": 12, "split": 2, "legacy": 7}[checkpoint]
                        self.assertEqual(result.stdout.count("GOTO count="), expected, result.stdout)
                        self.assertEqual(len((state / "repairs").read_text().splitlines()), expected)
                        for stage in ("integrate", "materials"):
                            self.assertTrue((state / f"{stage}_blockout_goto_used").exists())
                        repairs = (state / "repairs").read_text()
                        for stage, origin in (("integrate", integrate_origin), ("materials", materials_origin)):
                            reason = f"synthetic {stage} region lies outside footprint" if origin == "builder" else f"synthetic {stage} footprint mismatch"
                            self.assertIn(reason, repairs)
                        self.assertIn("Do not write state/goto.json", (state / "last_prompt").read_text())
                        resumed = self.goto_scenario(root, integrate_origin, materials_origin)
                        self.assertNotIn("GOTO count=", resumed.stdout)
                        self.assertEqual((state / "repairs").read_text(), repairs)
                        self.assertIn("GOTO cap reached", resumed.stdout)

    def test_reserve_is_blockout_only_and_shared_between_origins(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / "state"
            state.mkdir()
            (state / "builder_goto_count").write_text("5")
            (state / "critic_goto_count").write_text("5")
            result = self.goto_scenario(root, "critic", "builder", target="detail")
            self.assertEqual(result.stdout.count("GOTO count="), 1)
            self.assertFalse((state / "integrate_blockout_goto_used").exists())
            self.assertTrue((state / "materials_blockout_goto_used").exists())
            result = self.goto_scenario(root, "builder", "critic")
            self.assertEqual(result.stdout.count("GOTO count="), 1)
            self.assertTrue((state / "integrate_blockout_goto_used").exists())
            self.assertEqual(len((state / "repairs").read_text().splitlines()), 2)

    def test_reserve_write_failure_stops_before_dispatch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / "state"
            state.mkdir()
            (state / "builder_goto_count").write_text("5")
            (state / "critic_goto_count").write_text("5")
            (state / "integrate_blockout_goto_used").mkdir()
            result = self.goto_scenario(root, "builder", "critic", expected_rc=1)
            self.assertNotIn("GOTO count=", result.stdout)
            self.assertFalse((state / "repairs").exists())

    def test_expired_budget_finalizes_saved_s6_before_redirect(self):
        run_materials = function("run_materials")
        budget = function("within_s56_budget")
        loop = main_loop()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / "state"
            (state / "verdicts").mkdir(parents=True)
            (state / "objects.json").write_text('[{"id":"one"}]')
            (state / "integrate_start_epoch").write_text(str(int(time.time()) - 12601))
            (root / "materials_critic.md").write_text("critique")
            script = f'''set -uo pipefail
ROOT={root!s}; STATE={state!s}; PROMPTS={root!s}; INPUT=photo.png; MODEL_FAILURE=; ATTEMPT_SEQ=0; BEST_S6=-1
BUILDER_GOTOS=0; CRITIC_GOTOS=0; REQUEST_STAGE=; REQUEST_REASON=
builds=0
log() {{ printf '%s\n' "$*"; }}
inbox() {{ :; }}
next_attempt() {{ ATTEMPT_SEQ=$((ATTEMPT_SEQ+1)); }}
score_of() {{ jq -r '.score // 0' "$1"; }}
record() {{ :; }}
builder() {{ builds=$((builds+1)); touch "$STATE/materials.png" "$STATE/materials.blend"; }}
spatial_validate() {{ return 0; }}
critic() {{ printf '%s\n' '{{"score":6,"top_stage":"floorplan","corrections":["rebuild floorplan"]}}' > "$1"; }}
{run_materials}
{budget}
run_floorplan() {{ builder; }}
run_blockout() {{ builder; }}
run_identify() {{ builder; }}
run_detail() {{ builder; }}
run_integrate() {{ builder; }}
PHOTO_TO_SCENE_STAGE=materials
feedback=
{loop}
done
printf 'builds=%s critic_gotos=%s best=%s\n' "$builds" "$CRITIC_GOTOS" "$([ -f "$STATE/best_materials.blend" ] && printf saved || printf absent)"
'''
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("WALLCLOCK cap reached; finalizing best S6", result.stdout)
        self.assertIn("builds=1 critic_gotos=1 best=saved", result.stdout)

    def test_critic_budget_is_independent(self):
        loop = main_loop()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = f'''set -uo pipefail
STATE={root!s}
BUILDER_GOTOS=0
CRITIC_GOTOS=0
REQUEST_STAGE=
REQUEST_REASON=
calls=0
critic_sent=0
log() {{ printf '%s\n' "$*" >> "$STATE/log"; }}
within_s56_budget() {{ return 0; }}
run_floorplan() {{ return 0; }}
run_blockout() {{ return 0; }}
run_identify() {{ return 0; }}
run_detail() {{ calls=$((calls+1)); if [ "$calls" -le 5 ]; then REQUEST_STAGE=detail; REQUEST_REASON="builder $calls"; return 42; fi; return 0; }}
run_integrate() {{ if [ "$critic_sent" -eq 0 ]; then critic_sent=1; REQUEST_STAGE=detail; REQUEST_REASON="late critic"; return 43; fi; return 0; }}
run_materials() {{ return 0; }}
PHOTO_TO_SCENE_STAGE=detail
feedback=
{loop}
done
printf 'builder=%s critic=%s calls=%s\n' "$BUILDER_GOTOS" "$CRITIC_GOTOS" "$calls"
cat "$STATE/log"
'''
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("builder=5 critic=1 calls=7", result.stdout)
        self.assertIn("GOTO count=1 origin=critic stage=detail reason=late critic", result.stdout)


    def test_tree_ticks_reads_only_the_call_tree(self) -> None:
        script = function("tree_ticks") + """
io_read() { local key value; while read -r key value; do [ "$key" = rchar: ] && READ=$value; done < "/proc/$BASHPID/io"; }
measure() { ( io_read; local before=$READ; tree_ticks "$tree" > "$1"; io_read; printf '%s\\n' "$((READ - before))" ) }
( sleep 60 & bash -c 'sleep 60 & wait' & "$PYTHON" -c 'import subprocess, threading; threading.Thread(target=subprocess.run, args=(["sleep", "60"],)).start()' & wait ) > /dev/null 2>&1 & tree=$!
until [ "$(tree_ticks "$tree" | wc -l)" -ge 6 ] || [ "$SECONDS" -ge 20 ]; do sleep 0.1; done
alone=$(measure alone.txt)
crowd=()
for _ in $(seq 256); do sleep 60 & crowd+=("$!"); done
crowded=$(measure crowded.txt)
printf 'alone=%s crowded=%s pids=%s same=%s\\n' "$alone" "$crowded" "$(wc -l < alone.txt)" "$(cmp -s <(cut -d ' ' -f 1 alone.txt | sort) <(cut -d ' ' -f 1 crowded.txt | sort) && printf yes || printf no)"
kill "${crowd[@]}" "$tree" $(cut -d ' ' -f 1 alone.txt) 2>/dev/null
"""
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(["bash", "-c", script], cwd=directory, env={**os.environ, "PYTHON": sys.executable}, text=True, capture_output=True, timeout=300)
        self.assertEqual(result.returncode, 0, result.stderr)
        fields = dict(field.split("=") for field in result.stdout.split())
        self.assertEqual(fields["pids"], "6")
        self.assertEqual(fields["same"], "yes")
        self.assertGreater(int(fields["alone"]), 0)
        self.assertLess(int(fields["crowded"]) - int(fields["alone"]), 1024)

    def test_tree_ticks_counts_cpu_the_root_reaped(self) -> None:
        script = function("tree_ticks") + """
bash -c 'bash -c "for ((i = 0; i < 300000; i++)); do :; done"; sleep 60' & root=$!
for _ in $(seq 600); do read -r pid ticks _ < <(tree_ticks "$root"); [ "$ticks" -gt 0 ] && break; sleep 0.1; done
printf 'pid=%s root=%s ticks=%s\\n' "$pid" "$root" "$ticks"
kill "$root"
"""
        result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stderr)
        fields = dict(field.split("=") for field in result.stdout.split())
        self.assertEqual(fields["pid"], fields["root"])
        self.assertGreater(int(fields["ticks"]), 0)

    def test_tree_ticks_detects_demand_with_and_without_contention(self) -> None:
        cpu = str(min(os.sched_getaffinity(0)))
        burn = "while True: pass"
        sleeper = "import time\nwhile True: time.sleep(0.1)"
        threaded = "import threading\nthreading.Thread(target=lambda: exec('while True: pass')).start()\nthreading.Event().wait()"
        for loaded in (False, True):
            competitor = subprocess.Popen(["taskset", "-c", cpu, sys.executable, "-c", burn]) if loaded else None
            try:
                for name, code in (("busy", burn), ("thread", threaded), ("sleep", sleeper)):
                    with self.subTest(loaded=loaded, workload=name):
                        child = subprocess.Popen(["taskset", "-c", cpu, "nice", "-n", "19", sys.executable, "-c", code])
                        try:
                            time.sleep(0.5)
                            samples = []
                            for _ in range(31):
                                result = subprocess.run(["bash", "-c", function("tree_ticks") + f"\ntree_ticks {child.pid}"], text=True, capture_output=True, check=True)
                                pid, ticks, state = result.stdout.split()
                                self.assertEqual(int(pid), child.pid)
                                stat = Path(f"/proc/{child.pid}/stat").read_text().rsplit(") ", 1)[1].split()
                                samples.append((int(stat[11]) + int(stat[12]), state))
                                if len(samples) < 31:
                                    time.sleep(0.08 + (len(samples) % 5) * 0.017)
                            growth = [samples[n + 10][0] - samples[n][0] for n in (0, 10, 20)]
                            runnable = sum(state == "R" for _, state in samples[1:])
                            print(f"demand loaded={loaded} workload={name} cpu_ticks={growth} runnable={runnable}/30", flush=True)
                            if name == "sleep":
                                self.assertLess(max(growth), int(BUSY_CPU_TICKS))
                                self.check_model_demand("".join(state for _, state in samples[1:]), idle_failure(30))
                            else:
                                self.check_model_demand("".join(state for _, state in samples[1:]), "model call exceeded its 90 s wallclock bound")
                                if loaded:
                                    self.assertLess(max(growth), int(BUSY_CPU_TICKS))
                        finally:
                            child.terminate()
                            child.wait(timeout=10)
            finally:
                if competitor is not None:
                    competitor.terminate()
                    competitor.wait(timeout=10)

    def test_model_requires_sustained_runnable_demand(self) -> None:
        for pattern, expected in (("RSSSSS", idle_failure(6)),
                                  ("RRRSSS", "model call exceeded its 18 s wallclock bound"),
                                  ("RRRRRRSSSSSS", idle_failure(6))):
            result = self.check_model_demand(pattern, expected, idle=6)
            if pattern == "RRRRRRSSSSSS":
                self.assertGreaterEqual(int(re.search(r"samples=(\d+)", result.stdout).group(1)), 12)

    def check_model_demand(self, pattern, expected, idle=None):
        idle = idle or len(pattern)
        with tempfile.TemporaryDirectory() as directory:
            script = f"""set -uo pipefail
ROOT={directory}; STATE={directory}
log() {{ printf '%s\\n' "$*"; }}
{model_function(idle * 3, idle)}
SECONDS=0
sleep() {{ command sleep 0.02; SECONDS=$((SECONDS + 1)); }}
printf 0 > "$STATE/samples"
tree_ticks() {{
  local n state pattern={pattern}
  n=$(cat "$STATE/samples"); state=${{pattern:$((n % ${{#pattern}})):1}}
  printf '%s' "$((n+1))" > "$STATE/samples"
  printf '%s 0 %s\\n' "$1" "$state"
}}
codex() {{ exec sleep 60; }}
model - <<< prompt
printf 'rc=%s failure=%s samples=%s\\n' "$?" "$MODEL_FAILURE" "$(cat "$STATE/samples")"
"""
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(f"rc=1 failure={expected}", result.stdout)
            return result

    def test_model_runnable_child_without_cpu_is_busy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            script = f"""set -uo pipefail
ROOT={directory}; STATE={directory}
log() {{ printf '%s\\n' "$*"; }}
{model_function(60, 3)}
tree_ticks() {{ printf '%s 0 S\\n9000000 0 R\\n' "$1"; }}
codex() {{ cat >/dev/null; sleep 6; printf 'rendered\\n'; }}
model - <<< prompt
printf 'rc=%s failure=%s\\n' "$?" "$MODEL_FAILURE"
"""
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=60)
        self.assertIn("rendered\n", result.stdout)
        self.assertIn("rc=0 failure=\n", result.stdout)

    def test_model_busy_counts_growth_per_process(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            script = f"""set -uo pipefail
ROOT={directory}; STATE={directory}
log() {{ printf '%s\\n' "$*"; }}
{model_function(60, 3)}
printf 0 > "$STATE/samples"
tree_ticks() {{ local n b; n=$(( $(cat "$STATE/samples") + 1 )); printf '%s' "$n" > "$STATE/samples"; printf '%s 0 S\\n9000000 %s\\n' "$1" "$((20 * n))"; for ((b = n; b < 12; b++)); do printf '%s 100\\n' "$((9000000 + b))"; done; }}
codex() {{ cat >/dev/null; sleep 6; printf 'rendered\\n'; }}
model - <<< prompt
printf 'rc=%s failure=%s\\n' "$?" "$MODEL_FAILURE"
"""
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=60)
        self.assertIn("rendered\n", result.stdout)
        self.assertIn("rc=0 failure=\n", result.stdout)

    def test_model_idle_deadline_survives_inactive_zombie(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            script = f"""set -uo pipefail
ROOT={directory}; STATE={directory}
log() {{ printf '%s\\n' "$*"; }}
{model_function(60, 3)}
codex() {{ cat >/dev/null; sleep 6; printf 'rendered\\n'; }}
tree_ticks() {{ printf '%s 0 S\\n9000000 0 Z\\n' "$1"; }}
model - <<< prompt
printf 'zombie rc=%s failure=%s\\n' "$?" "$MODEL_FAILURE"
MODEL_SECONDS=2
model - <<< prompt
printf 'bounded rc=%s failure=%s\\n' "$?" "$MODEL_FAILURE"
MODEL_SECONDS=60
tree_ticks() {{ :; }}
model - <<< prompt
printf 'finished rc=%s failure=%s\\n' "$?" "$MODEL_FAILURE"
"""
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=300)
        self.assertEqual(result.stdout.count("rendered\n"), 1)
        self.assertIn(f"zombie rc=1 failure={idle_failure(3)}\n", result.stdout)
        self.assertIn("finished rc=0 failure=\n", result.stdout)
        self.assertIn("bounded rc=1 failure=model call exceeded its 2 s wallclock bound\n", result.stdout)

    def test_model_call_control(self) -> None:
        result, calls = model_calls()
        idle = rf"rc=1 seconds=\d+ failure={idle_failure(3)} marker=clear"
        self.assertEqual(result.returncode, 1, result.stderr)
        for name in ("whitespace", "silent", "graceful", "cut"):
            self.assertRegex(calls[name], idle)
            self.assertGreaterEqual(call_seconds(calls[name]), 3)
        self.assertIn("graceful_term=yes\n", result.stdout)
        for name in ("stubborn", "orphaned"):
            self.assertRegex(calls[name], idle)
            self.assertGreaterEqual(call_seconds(calls[name]), 13)
        self.assertIn("orphan_alive=no\n", result.stdout)
        self.assertRegex(calls["endless"], r"rc=1 seconds=\d+ failure=model call exceeded its 4 s wallclock bound marker=clear")
        self.assertGreaterEqual(call_seconds(calls["endless"]), 4)
        self.assertRegex(calls["exited"], r"rc=1 seconds=\d+ failure=model call exited with status 3 marker=set")
        self.assertRegex(calls["recovered"], r"rc=0 seconds=\d+ failure= marker=clear")
        self.assertRegex(calls["again"], r"rc=1 seconds=\d+ failure=model call exited with status 3 marker=set")
        self.assertRegex(calls["cut"], idle)
        self.assertRegex(calls["first"], r"rc=1 seconds=\d+ failure=model call exited with status 3 marker=set")
        self.assertNotIn("second", calls)
        self.assertIn("FAIL consecutive model calls exited non-zero; last: model call exited with status 3", result.stdout)
        self.assertNotIn("unreachable", result.stdout)

    def test_cut_builder_and_critic_calls_are_scored_attempts_and_the_run_continues(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / "state"
            prompts = root / "prompts"
            (state / "attempts").mkdir(parents=True)
            (state / "verdicts").mkdir()
            prompts.mkdir()
            (prompts / "floorplan_builder.md").write_text("build floorplan")
            (prompts / "floorplan_critic.md").write_text("criticize floorplan")
            (state / "records.tsv").write_text("")
            script = f"""set -uo pipefail
ROOT={root}; STATE={state}; PROMPTS={prompts}; INPUT=photo.jpg; ATTEMPT_SEQ=0; REQUEST_STAGE=; REQUEST_REASON=; BUILDER_GOTOS=0; CRITIC_GOTOS=0
printf 0 > "$STATE/calls"
log() {{ printf '%s\\n' "$*"; }}
inbox() {{ :; }}
next_attempt() {{ ATTEMPT_SEQ=$((ATTEMPT_SEQ+1)); }}
score_of() {{ jq -r '.score // 0' "$1"; }}
record() {{ printf '%s\\t%s\\t%s\\t%s\\t%s\\t%s\\n' "$1" "$2" "$3" "$4" "$5" "$6" >> "$STATE/records.tsv"; }}
codex() {{
  local call output= previous=
  for arg in "$@"; do [ "$previous" = -o ] && output=$arg; previous=$arg; done
  call=$(( $(cat "$STATE/calls") + 1 )); printf '%s' "$call" > "$STATE/calls"
  cat > "$STATE/prompt_$call"
  printf 'call %s\\n' "$call"
  case "$call" in
    1) while :; do printf '\\t'; sleep 0.1; done ;;
    3) while :; do sleep 0.1; done ;;
    2|4) printf 'plan %s' "$call" > "$STATE/floorplan.json"; printf png > "$STATE/floorplan.png" ;;
    5) printf '%s\\n' '{{"score":9,"summary":"ok","corrections":[],"top_stage":"floorplan","wrong_labels":[],"missing_objects":[]}}' > "$output" ;;
  esac
}}
{model_function()}
{function("builder")}
{function("critic")}
{function("write_stage_check_verdict")}
{function("run_floorplan")}
within_s56_budget() {{ return 0; }}
run_blockout() {{ printf 'blockout reached after %s calls\\n' "$(cat "$STATE/calls")"; exit 0; }}
PHOTO_TO_SCENE_STAGE=floorplan
feedback=
{main_loop()}
done
"""
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=60)
            records = [line.split("\t") for line in (state / "records.tsv").read_text().splitlines()]
            first_verdict = json.loads((state / "verdicts" / "floorplan_1.json").read_text())
            second_verdict = json.loads((state / "verdicts" / "floorplan_2.json").read_text())
            second_prompt = (state / "prompt_2").read_text()
            final_plan = (state / "floorplan.json").read_text()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blockout reached after 5 calls", result.stdout)
        self.assertEqual([(row[0], row[1], row[2]) for row in records], [("floorplan", "1", "0"), ("floorplan", "2", "0"), ("floorplan", "3", "9")])
        idle = idle_failure(2)
        self.assertEqual(first_verdict["corrections"], [idle])
        self.assertEqual(first_verdict["top_stage"], "floorplan")
        self.assertEqual(second_verdict["corrections"], [idle])
        self.assertEqual(records[1][4], idle)
        self.assertTrue(second_prompt.endswith(f"\nOne-reentry correction context follows:\n{idle}\n"))
        self.assertEqual(final_plan, "plan 4")

    def test_cut_detail_critic_is_scored_and_the_object_retries(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / "state"
            prompts = root / "prompts"
            (state / "attempts").mkdir(parents=True)
            (state / "verdicts").mkdir()
            (state / "crops").mkdir()
            prompts.mkdir()
            (prompts / "detail_builder.md").write_text("build object")
            (prompts / "detail_critic.md").write_text("criticize object")
            (state / "objects.json").write_text('[{"id":"one","spatial_contract":{}}]')
            (state / "records.tsv").write_text("")
            (state / "progress.md").write_text("")
            script = f"""set -uo pipefail
ROOT={root}; STATE={state}; PROMPTS={prompts}; ASSETS={root}; INPUT=photo.jpg; ATTEMPT_SEQ=0; REQUEST_STAGE=; REQUEST_REASON=; BUILDER_GOTOS=0
printf 0 > "$STATE/calls"
log() {{ printf '%s\\n' "$*"; }}
inbox() {{ :; }}
next_attempt() {{ ATTEMPT_SEQ=$((ATTEMPT_SEQ+1)); }}
score_of() {{ jq -r '.score // 0' "$1"; }}
record() {{ printf '%s\\t%s\\t%s\\t%s\\t%s\\t%s\\t%s\\n' "$1" "$2" "$3" "$4" "$5" "$6" "${{7:-}}" >> "$STATE/records.tsv"; }}
verify_detail() {{ return 0; }}
codex() {{
  local call output= previous=
  for arg in "$@"; do [ "$previous" = -o ] && output=$arg; previous=$arg; done
  call=$(( $(cat "$STATE/calls") + 1 )); printf '%s' "$call" > "$STATE/calls"
  cat > "$STATE/prompt_$call"
  printf 'call %s\\n' "$call"
  case "$call" in
    1|3) jq '. + {{proposed_label:"chair",final_label:"chair",label_reason:"crop"}}' "$STATE/entry_one.json" > "$STATE/entry.next" && mv "$STATE/entry.next" "$STATE/entry_one.json" ;;
    2) while :; do sleep 0.1; done ;;
    4) printf '%s\\n' '{{"score":9,"summary":"ok","corrections":[],"top_stage":"object:one","wrong_labels":[],"missing_objects":[]}}' > "$output" ;;
  esac
}}
{model_function()}
{function("builder")}
{function("critic")}
{function("write_stage_check_verdict")}
{function("detail_attempts")}
{function("detail_best")}
{function("restore_detail")}
{function("run_one_detail")}
run_one_detail one
"""
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=60)
            records = [line.split("\t") for line in (state / "records.tsv").read_text().splitlines()]
            first_verdict = json.loads((state / "verdicts" / "object_one_1.json").read_text())
            critic_prompt = (state / "prompt_4").read_text()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([(row[0], row[1], row[2]) for row in records], [("object:one", "1", "0"), ("object:one", "2", "9")])
        self.assertEqual(first_verdict["corrections"], [idle_failure(2)])
        self.assertEqual(first_verdict["top_stage"], "object:one")
        self.assertTrue(critic_prompt.startswith("criticize object\nThe supplied object stage tag is object:one.\nObject entry: "))
        self.assertIn("each owns its own components: []\n\nValid GOTO targets", critic_prompt)

    def test_failed_build_skips_the_stage_gate_and_is_never_best(self):
        failure = "model call exited with status 1"
        cases = {
            "blockout": ("run_blockout", "blockout_1.json", "blockout", ""),
            "integrate": ("run_integrate", "integrate_1.json", "integrate", "\n".join(function(name) for name in ("integrate_attempts", "integrate_best"))),
            "object": ('run_one_detail one', "object_one_1.json", "object:one", "\n".join(function(name) for name in ("detail_attempts", "detail_best", "restore_detail", "run_one_detail"))),
            "materials": ("run_materials", "materials_1.json", "materials", function("run_materials")),
        }
        for stage, (command, verdict_name, top_stage, helpers) in cases.items():
            with self.subTest(stage=stage), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                state = root / "state"
                prompts = root / "prompts"
                (state / "attempts").mkdir(parents=True)
                (state / "verdicts").mkdir()
                prompts.mkdir()
                for name in ("blockout", "integrate", "detail", "materials"):
                    (prompts / f"{name}_builder.md").write_text("build")
                    (prompts / f"{name}_critic.md").write_text("criticize")
                (state / "objects.json").write_text('[{"id":"one","spatial_contract":{}}]')
                (state / "object_tiers.tsv").write_text("one\tlarge\n")
                (state / "records.tsv").write_text("")
                (state / "progress.md").write_text("")
                function_name = command.split()[0]
                script = f"""set -uo pipefail
ROOT={root}; STATE={state}; PROMPTS={prompts}; ASSETS={root}; INPUT=photo.jpg; ATTEMPT_SEQ=0; BEST_S6=-1; REQUEST_STAGE=; REQUEST_REASON=; BUILDER_GOTOS=0
log() {{ printf '%s\\n' "$*"; }}
inbox() {{ :; }}
next_attempt() {{ ATTEMPT_SEQ=$((ATTEMPT_SEQ+1)); }}
score_of() {{ jq -r '.score // 0' "$1"; }}
record() {{ printf '%s\\t%s\\t%s\\n' "$1" "$2" "$3" >> "$STATE/records.tsv"; [ "$1" = materials ] || exit 0; }}
spatial_validate() {{ printf 'gate ran\\n'; return 1; }}
verify_detail() {{ printf 'gate ran\\n'; DETAIL_FAILURE="asset gate failed"; return 1; }}
codex() {{ cat >/dev/null; return 1; }}
{model_function()}
{function("builder")}
{function("critic")}
{function("write_stage_check_verdict")}
{function("write_spatial_check_verdict")}
{helpers if function_name not in ("run_blockout", "run_integrate") else function(function_name) + chr(10) + helpers}
{command}
printf 'rc=%s request=%s best_s6=%s\\n' "$?" "$REQUEST_STAGE" "$BEST_S6"
"""
                result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=30)
                verdict = json.loads((state / "verdicts" / verdict_name).read_text())
                best_saved = (state / "best_s6_score").exists()
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertNotIn("gate ran", result.stdout)
                self.assertEqual(verdict["corrections"], [failure])
                self.assertEqual(verdict["top_stage"], top_stage)
                self.assertFalse(best_saved)
                if stage == "materials":
                    self.assertIn("rc=0 request=materials best_s6=-1", result.stdout)

    def test_consecutive_model_failures_stop_the_run_without_recording_the_second(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / "state"
            prompts = root / "prompts"
            (state / "attempts").mkdir(parents=True)
            (state / "verdicts").mkdir()
            prompts.mkdir()
            (prompts / "floorplan_builder.md").write_text("build floorplan")
            (prompts / "floorplan_critic.md").write_text("criticize floorplan")
            (state / "records.tsv").write_text("")
            script = f"""set -uo pipefail
ROOT={root}; STATE={state}; PROMPTS={prompts}; INPUT=photo.jpg; ATTEMPT_SEQ=0; REQUEST_STAGE=; REQUEST_REASON=; BUILDER_GOTOS=0
log() {{ printf '%s\\n' "$*"; }}
inbox() {{ :; }}
next_attempt() {{ ATTEMPT_SEQ=$((ATTEMPT_SEQ+1)); }}
score_of() {{ jq -r '.score // 0' "$1"; }}
record() {{ printf '%s\\t%s\\t%s\\n' "$1" "$2" "$3" >> "$STATE/records.tsv"; }}
codex() {{ cat >/dev/null; printf 'usage limit reached\\n'; return 1; }}
{model_function()}
{function("builder")}
{function("critic")}
{function("write_stage_check_verdict")}
{function("run_floorplan")}
run_floorplan
printf 'unreachable\\n'
"""
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=30)
            records = (state / "records.tsv").read_text()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(records, "floorplan\t1\t0\n")
        self.assertEqual(result.stdout.count("ENTER floorplan"), 2)
        self.assertIn("FAIL consecutive model calls exited non-zero", result.stdout)
        self.assertNotIn("unreachable", result.stdout)

    def test_failed_final_build_stops_before_the_report(self):
        final = "if [ ! -f" + PIPELINE.split("done\nif [ ! -f", 1)[1]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "prompts").mkdir()
            (root / "prompts" / "final_builder.md").write_text("finalize")
            (root / "best_materials.blend").write_text("scene")
            script = f"""set -uo pipefail
ROOT={root}; STATE={root}; PROMPTS={root}/prompts; REQUEST_STAGE=; REQUEST_REASON=
log() {{ printf '%s\\n' "$*"; }}
write_report() {{ printf 'report written\\n'; }}
codex() {{ cat >/dev/null; printf 'bound=%s\\n' "$MODEL_SECONDS"; return 3; }}
{model_function()}
{function("builder")}
{final}
"""
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("FAIL final model call exited with status 3", result.stdout)
        self.assertIn("bound=4800\n", result.stdout)
        self.assertNotIn("report written", result.stdout)
    def test_failed_attempt_output_is_never_restored_as_best(self):
        cases = {
            "floorplan": ("run_floorplan", "floorplan.json", ""),
            "blockout": ("run_blockout", "blockout.py", ""),
            "integrate": ("run_integrate", "assemble.py", "\n".join(function(name) for name in ("integrate_attempts", "integrate_best"))),
        }
        for stage, (command, restored, helpers) in cases.items():
            with self.subTest(stage=stage), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                state = root / "state"
                prompts = root / "prompts"
                (state / "attempts").mkdir(parents=True)
                (state / "verdicts").mkdir()
                prompts.mkdir()
                (prompts / f"{stage}_builder.md").write_text("build")
                (prompts / f"{stage}_critic.md").write_text("criticize")
                (state / "records.tsv").write_text("")
                (state / "builds").write_text("0")
                script = f"""set -uo pipefail
ROOT={root}; STATE={state}; PROMPTS={prompts}; INPUT=photo.jpg; ATTEMPT_SEQ=0; REQUEST_STAGE=; REQUEST_REASON=; BUILDER_GOTOS=0
log() {{ printf '%s\\n' "$*"; }}
inbox() {{ :; }}
next_attempt() {{ ATTEMPT_SEQ=$((ATTEMPT_SEQ+1)); }}
score_of() {{ jq -r '.score // 0' "$1"; }}
record() {{ printf '%s\\t%s\\t%s\\t%s\\t%s\\t%s\\n' "$1" "$2" "$3" "$4" "$5" "$6" >> "$STATE/records.tsv"; }}
spatial_validate() {{ return 0; }}
codex() {{
  local output= previous= build file
  for arg in "$@"; do [ "$previous" = -o ] && output=$arg; previous=$arg; done
  cat >/dev/null
  if [ -n "$output" ]; then printf '%s\\n' '{{"score":0,"summary":"weak","corrections":["weak"],"top_stage":"{stage}","wrong_labels":[],"missing_objects":[]}}' > "$output"; return 0; fi
  build=$(( $(cat "$STATE/builds") + 1 )); printf '%s' "$build" > "$STATE/builds"
  for file in floorplan.json floorplan.png objects.json blockout.py blockout.png blockout_overlay.png objects_sheet.png assemble.py integrate.png integrate_overlay.png spatial_observed.json; do printf 'build %s' "$build" > "$STATE/$file"; done
  [ "$build" -ne 1 ]
}}
{model_function()}
{function("builder")}
{function("critic")}
{function("write_stage_check_verdict")}
{function("write_spatial_check_verdict")}
{helpers}
{function(command)}
{command}
printf 'rc=%s\\n' "$?"
"""
                result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=30)
                restored_text = (state / restored).read_text()
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("rc=0", result.stdout)
                self.assertEqual(restored_text, "build 2")

    def test_stage_without_a_completed_attempt_stops_the_run(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / "state"
            prompts = root / "prompts"
            (state / "attempts").mkdir(parents=True)
            (state / "verdicts").mkdir()
            prompts.mkdir()
            (prompts / "floorplan_builder.md").write_text("build floorplan")
            (prompts / "floorplan_critic.md").write_text("criticize floorplan")
            (state / "records.tsv").write_text("")
            script = f"""set -uo pipefail
ROOT={root}; STATE={state}; PROMPTS={prompts}; INPUT=photo.jpg; ATTEMPT_SEQ=0; REQUEST_STAGE=; REQUEST_REASON=; BUILDER_GOTOS=0; CRITIC_GOTOS=0
log() {{ printf '%s\\n' "$*"; }}
inbox() {{ :; }}
next_attempt() {{ ATTEMPT_SEQ=$((ATTEMPT_SEQ+1)); }}
score_of() {{ jq -r '.score // 0' "$1"; }}
record() {{ printf '%s\\t%s\\t%s\\n' "$1" "$2" "$3" >> "$STATE/records.tsv"; }}
codex() {{
  local previous= critic=0
  for arg in "$@"; do [ "$previous" = -o ] && critic=1; previous=$arg; done
  cat >/dev/null
  printf plan > "$STATE/floorplan.json"; printf png > "$STATE/floorplan.png"
  [ "$critic" -eq 0 ]
}}
{model_function()}
{function("builder")}
{function("critic")}
{function("write_stage_check_verdict")}
{function("run_floorplan")}
within_s56_budget() {{ return 0; }}
run_blockout() {{ printf 'blockout reached\\n'; exit 0; }}
PHOTO_TO_SCENE_STAGE=floorplan
feedback=
{main_loop()}
done
"""
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=30)
            records = (state / "records.tsv").read_text()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(records, "floorplan\t1\t0\nfloorplan\t2\t0\nfloorplan\t3\t0\n")
        self.assertIn("FAIL floorplan no attempt completed its model calls", result.stdout)
        self.assertIn("FAIL stage=floorplan rc=1", result.stdout)
        self.assertNotIn("blockout reached", result.stdout)
    def test_builder_goto_leaves_a_timed_redirect_row_and_keeps_scored_budgets(self):
        for stage in ("blockout", "object:one"):
            with self.subTest(stage=stage), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                state = root / "state"
                prompts = root / "prompts"
                (state / "attempts").mkdir(parents=True)
                (state / "verdicts").mkdir()
                (state / "crops").mkdir()
                prompts.mkdir()
                for name in ("blockout", "detail"):
                    (prompts / f"{name}_builder.md").write_text("build")
                (state / "objects.json").write_text('[{"id":"one","spatial_contract":{}}]')
                (state / "progress.md").write_text("")
                for suffix, content in (("py", "best"), ("png", "best render"), ("json", '{"id":"one","spatial_contract":{},"final_label":"best"}')):
                    (state / "attempts" / f"object_one_1.{suffix}").write_text(content)
                (state / "verdicts" / "object_one_1.json").write_text('{"score":6,"corrections":["sharpen"]}')
                (state / "best_materials_verdict.json").write_text('{"top_stage":"materials"}')
                (state / "best_s6_score").write_text("6")
                (state / "floorplan.json").write_text("{}")
                (root / "log.md").write_text("")
                (state / "redirects.tsv").write_text("")
                command = "run_blockout" if stage == "blockout" else "run_one_detail one '' 1"
                script = f"""set -uo pipefail
ROOT={root}; STATE={state}; PROMPTS={prompts}; ASSETS={root}; INPUT=photo.jpg; ATTEMPT_SEQ=1; REQUEST_STAGE=; REQUEST_REASON=; BUILDER_GOTOS=0; CRITIC_GOTOS=0; MODEL_FAILURE=
hash=$(printf '{{"contract":{{}},"material_note":null}}\\n' | sha256sum | cut -d ' ' -f1)
printf 'object:one\\t1\\t6\\t5\\t\\t%s\\t%s\\n' "$STATE/verdicts/object_one_1.json" "$hash" > "$STATE/records.tsv"
log() {{ printf '%s\\n' "$*"; }}
inbox() {{ :; }}
next_attempt() {{ ATTEMPT_SEQ=$((ATTEMPT_SEQ+1)); }}
score_of() {{ jq -r '.score // 0' "$1"; }}
record() {{ printf '%s\\t%s\\t%s\\t%s\\t%s\\t%s\\t%s\\n' "$1" "$2" "$3" "$4" "$5" "$6" "${{7:-}}" >> "$STATE/records.tsv"; }}
critic() {{ printf 'critic ran\\n'; }}
codex() {{ cat >/dev/null; printf 'partial' > "$ASSETS/one.py"; printf '%s\\n' '{{"stage":"identify","reason":"needs | rework"}}' > "$STATE/goto.json"; }}
{model_function()}
{function("builder")}
{function("detail_attempts")}
{function("detail_best")}
{function("restore_detail")}
{function("run_blockout")}
{function("run_one_detail")}
{function("parse_record")}
{function("write_report")}
{command}
printf 'rc=%s attempts=%s best=%s asset=%s\\n' "$?" "$(detail_attempts one "$hash")" "$(detail_best one "$hash")" "$(cat "$ASSETS/one.py")"
write_report
"""
                result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=60)
                redirects = [line.split("\t") for line in (state / "redirects.tsv").read_text().splitlines()]
                records = (state / "records.tsv").read_text().splitlines()
                report = (state / "scores.md").read_text()
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertNotIn("critic ran", result.stdout)
                self.assertEqual(len(records), 1)
                self.assertEqual(len(redirects), 1)
                row_stage, attempt, sequence, seconds, target, reason = redirects[0]
                self.assertEqual((row_stage, attempt, sequence, target, reason), (stage, "1" if stage == "blockout" else "2", "2", "identify", "needs | rework"))
                self.assertGreaterEqual(int(seconds), 1)
                expected_asset = "partial" if stage == "blockout" else "best"
                self.assertIn(f"rc=42 attempts=1 best=6 asset={expected_asset}\n", result.stdout)
                self.assertIn(f"| {stage} | {attempt} | 2 | {seconds} | identify | needs \\| rework |", report)
                self.assertIn(f"Scored attempts took 5 s; redirected builder attempts took {seconds} s; together {5 + int(seconds)} s.", report)

    def test_reentry_best_ignores_attempts_without_a_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / "state"
            prompts = root / "prompts"
            (state / "attempts" / "integrate_5").mkdir(parents=True)
            (state / "verdicts").mkdir()
            (state / "crops").mkdir()
            prompts.mkdir()
            (prompts / "detail_builder.md").write_text("build object")
            (state / "attempts" / "object_one_3.py").write_text("completed")
            (state / "objects.json").write_text('[{"id":"one","spatial_contract":{}}]')
            (state / "progress.md").write_text("")
            script = f"""set -uo pipefail
ROOT={root}; STATE={state}; PROMPTS={prompts}; ASSETS={root}; INPUT=photo.jpg; ATTEMPT_SEQ=6; REQUEST_STAGE=; REQUEST_REASON=; BUILDER_GOTOS=0
hash=$(printf '{{"contract":{{}},"material_note":null}}\\n' | sha256sum | cut -d ' ' -f1)
printf 'integrate\\t1\\t0\\t1\\t\\t%s\\t\\nintegrate\\t2\\t0\\t1\\t\\t%s\\t\\n' "$STATE/verdicts/integrate_5.json" "$STATE/verdicts/integrate_6.json" > "$STATE/records.tsv"
printf 'object:one\\t1\\t5\\t1\\t\\t%s\\t%s\\nobject:one\\t2\\t5\\t1\\t\\t%s\\t%s\\n' "$STATE/verdicts/object_one_3.json" "$hash" "$STATE/verdicts/object_one_4.json" "$hash" >> "$STATE/records.tsv"
log() {{ printf '%s\\n' "$*"; }}
inbox() {{ :; }}
next_attempt() {{ ATTEMPT_SEQ=$((ATTEMPT_SEQ+1)); }}
score_of() {{ jq -r '.score // 0' "$1"; }}
record() {{ printf '%s\\t%s\\t%s\\t%s\\t%s\\t%s\\t%s\\n' "$1" "$2" "$3" "$4" "$5" "$6" "${{7:-}}" >> "$STATE/records.tsv"; }}
codex() {{ cat >/dev/null; printf 'new' > "$ASSETS/one.py"; }}
{model_function()}
{function("builder")}
{function("critic")}
{function("write_stage_check_verdict")}
{function("integrate_best")}
{function("detail_attempts")}
{function("detail_best")}
{function("restore_detail")}
{function("run_one_detail")}
printf 'integrate_best=%s\\n' "$(integrate_best)"
run_one_detail one "" 1
printf 'asset=%s\\n' "$(cat "$ASSETS/one.py")"
"""
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("integrate_best=0 5\n", result.stdout)
        self.assertIn("asset=completed\n", result.stdout)

    def test_tier_non_verdicts_and_score_disagreement_retry_only_the_critic(self):
        change = dict(action="resize", subject="foreground table",
                      observed="right edge at 80% of image width",
                      desired="right edge at 65% of image width")
        actionable = dict(score=2, summary="table too wide",
                          corrections=["Reduce the foreground table's rightward extent to 65%."],
                          top_stage="blockout", wrong_labels=[], missing_objects=[],
                          scene_change=change)
        cases = []
        for correction in ("The comparison needs to be rerun to produce a reliable verdict.",
                           "blockout", "Retry the composition comparison."):
            invalid = dict(actionable, corrections=[correction])
            cases.extend([(correction, invalid, actionable, 3, 43, 2, 1),
                          (correction + " repeated", invalid, invalid, 3, 0, 2, 0)])
        cases.extend([
            ("missing scene change", dict(actionable, scene_change=None), actionable, 3, 43, 2, 1),
            ("empty observation", dict(actionable, scene_change=dict(change, observed=" ")),
             actionable, 3, 43, 2, 1),
            ("five point disagreement", actionable, actionable, 7, 0, 2, 1),
            ("four point difference", actionable, actionable, 6, 43, 1, 1),
            ("recalibrated", actionable, dict(actionable, score=7), 7, 43, 2, 1),
            ("detail correction", dict(actionable, top_stage="detail"), actionable, 8, 43, 1, 0),
            ("passing", dict(actionable, score=8, scene_change=None), actionable, 8, 0, 1, 0),
        ])
        for name, first, second, baseline, rc, reviews, comparisons in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "verdicts").mkdir()
                (root / "object_tiers.tsv").write_text("table\tlarge\n")
                for prompt in ("tier_critic", "blockout_critic"):
                    (root / (prompt + ".md")).write_text(prompt)
                for index, verdict in enumerate((first, second), 1):
                    (root / f"review{index}.json").write_text(json.dumps(verdict))
                (root / "baseline.json").write_text(json.dumps(dict(actionable, score=baseline)))
                script = f"""set -uo pipefail
STATE={root}; PROMPTS={root}; INPUT=reference.png; MODEL_FAILURE=
ATTEMPT_SEQ=0; builds=0; reviews=0; comparisons=0; REQUEST_STAGE=; REQUEST_REASON=
next_attempt() {{ ATTEMPT_SEQ=$((ATTEMPT_SEQ+1)); }}
log() {{ printf '%s\\n' "$*"; }}
inbox() {{ :; }}
record() {{ :; }}
score_of() {{ jq -r '.score // 0' "$1"; }}
builder() {{ builds=$((builds+1)); printf render > "$STATE/tier_large.png"; }}
critic() {{
  cat >> "$STATE/prompts"
  if [ "$2" = blockout ]; then
    comparisons=$((comparisons+1))
    [ "$*" = "$1 blockout -i reference.png $STATE/tier_large.png" ] || exit 99
    cp "$STATE/baseline.json" "$1"
  else
    reviews=$((reviews+1)); cp "$STATE/review$reviews.json" "$1"
  fi
}}
{function("run_tier_critic")}
run_tier_critic large
printf 'rc=%s builds=%s reviews=%s comparisons=%s stage=%s\\n' "$?" "$builds" "$reviews" "$comparisons" "$REQUEST_STAGE"
"""
                result = subprocess.run(["bash", "-c", script], capture_output=True,
                                        text=True, timeout=60)
                self.assertEqual(result.returncode, 0, result.stderr)
                stage = (second if reviews == 2 else first)["top_stage"] if rc == 43 else ""
                self.assertIn(f"rc={rc} builds=1 reviews={reviews} comparisons={comparisons} stage={stage}\n",
                              result.stdout)

    def test_failed_tier_call_is_retried_with_its_failure_text(self):
        failure = "simulated model call failure"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / "state"
            prompts = root / "prompts"
            (state / "verdicts").mkdir(parents=True)
            prompts.mkdir()
            (prompts / "tier_builder.md").write_text("compose tier")
            (prompts / "tier_critic.md").write_text("criticize tier")
            (state / "object_tiers.tsv").write_text("one\tlarge\n")
            script = f"""set -uo pipefail
ROOT={root}; STATE={state}; PROMPTS={prompts}; INPUT=photo.jpg; ATTEMPT_SEQ=0; REQUEST_STAGE=; REQUEST_REASON=; BUILDER_GOTOS=0
log() {{ printf '%s\\n' "$*"; }}
inbox() {{ :; }}
next_attempt() {{ ATTEMPT_SEQ=$((ATTEMPT_SEQ+1)); }}
score_of() {{ jq -r '.score // 0' "$1"; }}
record() {{ printf '%s\\t%s\\t%s\\t%s\\t%s\\t%s\\n' "$MODE" "$1" "$2" "$3" "$5" "$6" >> "$STATE/records.tsv"; }}
# Drive retry policy synchronously; watchdog timing is covered by model-call tests.
SCHEMA=schema.json; MODEL_FAILURE=
model() {{
  MODEL_FAILURE=
  local call output= previous=
  for arg in "$@"; do [ "$previous" = -o ] && output=$arg; previous=$arg; done
  call=$(( $(cat "$STATE/calls") + 1 )); printf '%s' "$call" > "$STATE/calls"
  cat > "$STATE/prompt_${{MODE}}_$call"
  case "$MODE:$call" in
    retry:2) printf png > "$STATE/tier_large.png" ;;
    retry:3) printf '%s\\n' '{{"score":6,"summary":"off","corrections":["move the sofa"],"top_stage":"detail","wrong_labels":[],"missing_objects":[],"scene_change":{{"action":"move","subject":"sofa","observed":"too far right","desired":"left by 10 pixels"}}}}' > "$output" ;;
    *) MODEL_FAILURE={shlex.quote(failure)}; return 1 ;;
  esac
}}
{function("builder")}
{function("critic")}
{function("write_stage_check_verdict")}
{function("run_tier_critic")}
for MODE in retry fail; do
  printf 0 > "$STATE/calls"; REQUEST_STAGE=; REQUEST_REASON=
  run_tier_critic large; printf '%s rc=%s request=%s reason=%s calls=%s\\n' "$MODE" "$?" "$REQUEST_STAGE" "$REQUEST_REASON" "$(cat "$STATE/calls")"
done
"""
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=60)
            records = [line.split("\t") for line in (state / "records.tsv").read_text().splitlines()]
            retried_prompt = (state / "prompt_retry_2").read_text()
            verdicts = [json.loads(Path(row[5]).read_text()) for row in records]
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([row[:4] for row in records], [["retry", "tier:large", "1", "0"], ["retry", "tier:large", "2", "6"], ["fail", "tier:large", "1", "0"], ["fail", "tier:large", "2", "0"]])
        self.assertEqual(records[1][4], failure)
        self.assertEqual([Path(row[5]).name for row in records], [f"tier_large_{sequence}.json" for sequence in range(1, 5)])
        self.assertEqual([verdict["score"] for verdict in verdicts], [0, 6, 0, 0])
        self.assertTrue(retried_prompt.endswith(f"\nOne-reentry correction context follows:\nTier: large. Object ids: one \n{failure}\n"))
        self.assertIn("retry rc=43 request=detail reason=move the sofa calls=3\n", result.stdout)
        self.assertIn("tier:large review unaccepted after one retry; descending without a GOTO\nfail rc=0 request= reason= calls=2\n", result.stdout)
        self.assertEqual([verdict["corrections"] for verdict in verdicts[2:]], [[failure], [failure]])

    def test_best_detail_restores_its_own_textures_after_a_later_overwrite_and_resume(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / "state"
            prompts = root / "prompts"
            assets = root / "assets"
            textures = root / "textures"
            for path in (state / "attempts", state / "verdicts", state / "crops", prompts, assets, textures):
                path.mkdir(parents=True)
            (textures / "lace.png").write_bytes(b"downloaded")
            (prompts / "detail_builder.md").write_text("build object")
            (prompts / "detail_critic.md").write_text("criticize object")
            (state / "objects.json").write_text('[{"id":"one","spatial_contract":{}}]')
            (state / "records.tsv").write_text("")
            (state / "progress.md").write_text("")
            script = f"""set -uo pipefail
ROOT={root}; STATE={state}; PROMPTS={prompts}; ASSETS={assets}; TEXTURES={textures}; INPUT=photo.jpg; ATTEMPT_SEQ=0; REQUEST_STAGE=; REQUEST_REASON=; BUILDER_GOTOS=0
printf 0 > "$STATE/calls"
log() {{ :; }}
inbox() {{ :; }}
next_attempt() {{ ATTEMPT_SEQ=$((ATTEMPT_SEQ+1)); }}
score_of() {{ jq -r '.score // 0' "$1"; }}
record() {{ printf '%s\\t%s\\t%s\\t%s\\t%s\\t%s\\t%s\\n' "$1" "$2" "$3" "$4" "$5" "$6" "${{7:-}}" >> "$STATE/records.tsv"; }}
verify_detail() {{ return 0; }}
codex() {{
  local call output= previous=
  for arg in "$@"; do [ "$previous" = -o ] && output=$arg; previous=$arg; done
  call=$(( $(cat "$STATE/calls") + 1 )); printf '%s' "$call" > "$STATE/calls"
  cat >/dev/null
  case "$call" in
    1|3)
      jq '. + {{proposed_label:"rug",final_label:"rug",label_reason:"crop"}}' "$STATE/entry_one.json" > "$STATE/entry.next" && mv "$STATE/entry.next" "$STATE/entry_one.json"
      mkdir -p "$TEXTURES/one"; printf 'weave %s' "$call" > "$TEXTURES/one/weave.png"
      printf 'overwritten %s' "$call" 2>/dev/null > "$TEXTURES/lace.png" || true
      printf 'def build(entry, collection=None): pass  # %s\\n' "$call" > "$ASSETS/one.py"; printf 'render %s' "$call" > "$STATE/detail_one.png" ;;
    *) printf '%s\\n' '{{"score":7,"summary":"close","corrections":["refine"],"top_stage":"object:one","wrong_labels":[],"missing_objects":[]}}' > "$output" ;;
  esac
}}
{model_function()}
{function("builder")}
{function("critic")}
{function("write_stage_check_verdict")}
{function("detail_attempts")}
{function("detail_best")}
{function("restore_detail")}
{function("run_one_detail")}
run_one_detail one
printf 'after_run=%s|%s|%s\\n' "$(cat "$TEXTURES/one/weave.png")" "$(cat "$STATE/detail_one.png")" "$(grep -o '# [0-9]' "$ASSETS/one.py")"
printf 'interrupted' > "$TEXTURES/one/weave.png"; printf 'stray' > "$TEXTURES/one/stray.png"
run_one_detail one
printf 'after_resume=%s|%s|%s\\n' "$(cat "$TEXTURES/one/weave.png")" "$(ls "$TEXTURES/one" | paste -sd, -)" "$(cat "$STATE/calls")"
"""
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=60)
            shared = (textures / "lace.png").read_text()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("after_run=weave 1|render 1|# 1\n", result.stdout)
        self.assertIn("after_resume=weave 1|weave.png|4\n", result.stdout)
        self.assertEqual(shared, "downloaded")

    def test_detail_builder_can_write_only_its_own_and_new_textures(self):
        with tempfile.TemporaryDirectory() as directory:
            textures = Path(directory) / "textures"
            (textures / "sheer").mkdir(parents=True)
            (textures / "other").mkdir()
            (textures / "lace.png").write_bytes(b"downloaded")
            (textures / "other" / "bark.png").write_bytes(b"neighbour")
            (textures / "sheer" / "weave.png").write_bytes(b"own")
            (textures / "sheer" / "weave.png").chmod(0o444)
            script = f'''set -uo pipefail
TEXTURES={shlex.quote(str(textures))}
{function("protect_textures")}
protect_textures sheer
for path in lace.png other/bark.png sheer/weave.png fetched.png; do
  if printf x 2>/dev/null > "$TEXTURES/$path"; then printf '%s writable\\n' "$path"; else printf '%s read-only\\n' "$path"; fi
done
'''
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=30)
            unchanged = [(textures / name).read_bytes() for name in ("lace.png", "other/bark.png")]
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "lace.png read-only\nother/bark.png read-only\nsheer/weave.png writable\nfetched.png writable\n")
        self.assertEqual(unchanged, [b"downloaded", b"neighbour"])

    def test_cached_read_only_polyhaven_texture_is_reused_without_download(self):
        import contextlib, hashlib, io, runpy, urllib.request
        from unittest import mock
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "textures").mkdir()
            cached = root / "textures" / "wood_diff_2k.jpg"
            cached.write_bytes(b"cached")
            cached.chmod(0o444)
            manifest = {"Diffuse": {"2k": {"jpg": {"url": "https://dl.example/wood_diff_2k.jpg", "md5": hashlib.md5(b"cached").hexdigest()}}}}
            fetched = []
            def urlopen(url):
                fetched.append(url)
                if url.endswith("/files/wood"):
                    return io.BytesIO(json.dumps(manifest).encode())
                raise AssertionError(f"downloaded {url}")
            out = io.StringIO()
            with mock.patch.object(urllib.request, "urlopen", urlopen), mock.patch.object(sys, "argv", ["fetch-polyhaven.py", "wood", "Diffuse.2k.jpg", "--root", str(root)]), contextlib.redirect_stdout(out):
                runpy.run_path(str(Path(__file__).with_name("fetch-polyhaven.py")), run_name="__main__")
            self.assertEqual(cached.read_bytes(), b"cached")
        self.assertEqual(fetched, ["https://api.polyhaven.com/files/wood"])
        self.assertEqual(out.getvalue(), f"{cached}\n")

    def test_detail_object_without_a_completed_attempt_keeps_no_asset(self):
        for mode, expected_rc in (("stopped", "0"), ("goto", "42")):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                state = root / "state"
                prompts = root / "prompts"
                assets = root / "assets"
                (state / "attempts").mkdir(parents=True)
                (state / "verdicts").mkdir()
                (state / "crops").mkdir()
                prompts.mkdir()
                assets.mkdir()
                (prompts / "detail_builder.md").write_text("build object")
                (assets / "one.py").write_text("earlier contract")
                (state / "detail_one.png").write_text("earlier render")
                (state / "objects.json").write_text('[{"id":"one","spatial_contract":{}}]')
                (state / "records.tsv").write_text("")
                (state / "progress.md").write_text("")
                script = f"""set -uo pipefail
ROOT={root}; STATE={state}; PROMPTS={prompts}; ASSETS={assets}; INPUT=photo.jpg; ATTEMPT_SEQ=0; REQUEST_STAGE=; REQUEST_REASON=; BUILDER_GOTOS=0; MODE={mode}
printf 0 > "$STATE/calls"
log() {{ printf '%s\\n' "$*"; }}
inbox() {{ :; }}
next_attempt() {{ ATTEMPT_SEQ=$((ATTEMPT_SEQ+1)); }}
score_of() {{ jq -r '.score // 0' "$1"; }}
record() {{ printf '%s\\t%s\\t%s\\t%s\\t%s\\t%s\\t%s\\n' "$1" "$2" "$3" "$4" "$5" "$6" "${{7:-}}" >> "$STATE/records.tsv"; }}
verify_detail() {{ return 0; }}
codex() {{
  local call
  cat >/dev/null
  call=$(( $(cat "$STATE/calls") + 1 )); printf '%s' "$call" > "$STATE/calls"
  printf 'partial %s' "$call" > "$ASSETS/one.py"; printf 'partial' > "$STATE/detail_one.png"
  if [ "$MODE:$call" = goto:2 ]; then printf '%s\\n' '{{"stage":"blockout","reason":"contract conflict"}}' > "$STATE/goto.json"; return 0; fi
  while :; do sleep 0.1; done
}}
{model_function()}
{function("builder")}
{function("critic")}
{function("write_stage_check_verdict")}
{function("detail_attempts")}
{function("detail_best")}
{function("restore_detail")}
{function("run_one_detail")}
run_one_detail one
printf 'rc=%s request=%s\\n' "$?" "$REQUEST_STAGE"
"""
                result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=60)
                records = [line.split("\t")[:3] for line in (state / "records.tsv").read_text().splitlines()]
                asset_left = (assets / "one.py").exists()
                render_left = (state / "detail_one.png").exists()
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(f"rc={expected_rc} request={'blockout' if mode == 'goto' else ''}\n", result.stdout)
                self.assertEqual(records[0], ["object:one", "1", "0"])
                self.assertEqual(len(records), 2 if mode == "stopped" else 1)
                self.assertFalse(asset_left)
                self.assertFalse(render_left)

    def detail_ownership_run(self, objects, target, critic_verdicts, builder_labels):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / "state"
            prompts = root / "prompts"
            assets = root / "assets"
            for path in (state / "attempts", state / "verdicts", state / "crops", state / "textures", prompts, assets):
                path.mkdir(parents=True)
            (prompts / "detail_builder.md").write_text("build object")
            (prompts / "detail_critic.md").write_text("criticize object")
            (state / "objects.json").write_text(json.dumps(objects))
            (state / "records.tsv").write_text("")
            (state / "progress.md").write_text("")
            for number, verdict in enumerate(critic_verdicts, 1):
                (state / f"critic_{number}.json").write_text(json.dumps({"scene_change": None, "summary": "", "top_stage": f"object:{target}", "missing_objects": [], **verdict}))
            for number, label in enumerate(builder_labels, 1):
                (state / f"label_{number}").write_text(label)
            script = f"""set -uo pipefail
ROOT={root}; STATE={state}; PROMPTS={prompts}; ASSETS={assets}; SCHEMA={Path(__file__).parents[1] / "verdict.schema.json"}; INPUT=photo.jpg; ATTEMPT_SEQ=0; REQUEST_STAGE=; REQUEST_REASON=; BUILDER_GOTOS=0
printf 0 > "$STATE/calls"; printf 0 > "$STATE/builds"; printf 0 > "$STATE/critiques"
log() {{ :; }}
inbox() {{ :; }}
next_attempt() {{ ATTEMPT_SEQ=$((ATTEMPT_SEQ+1)); }}
score_of() {{ jq -r '.score // 0' "$1"; }}
record() {{ printf '%s\\t%s\\t%s\\t%s\\t%s\\t%s\\t%s\\n' "$1" "$2" "$3" "$4" "$5" "$6" "${{7:-}}" >> "$STATE/records.tsv"; }}
verify_detail() {{ return 0; }}
codex() {{
  local output= previous= n
  for arg in "$@"; do [ "$previous" = -o ] && output=$arg; previous=$arg; done
  if [ -n "$output" ]; then
    n=$(( $(cat "$STATE/critiques") + 1 )); printf '%s' "$n" > "$STATE/critiques"
    cat > "$STATE/critic_input_$n"; cp "$STATE/critic_$n.json" "$output"
  else
    n=$(( $(cat "$STATE/builds") + 1 )); printf '%s' "$n" > "$STATE/builds"
    cat > "$STATE/builder_input_$n"
    jq --arg label "$(cat "$STATE/label_$n")" '. + {{proposed_label:.label,final_label:$label,label_reason:"crop"}}' "$STATE/entry_{target}.json" > "$STATE/entry.next" && mv "$STATE/entry.next" "$STATE/entry_{target}.json"
    printf 'def build(entry, collection=None): pass  # %s\\n' "$n" > "$ASSETS/{target}.py"; printf 'render %s' "$n" > "$STATE/detail_{target}.png"
  fi
}}
{model_function()}
{function("builder")}
{function("critic")}
{function("write_stage_check_verdict")}
{function("detail_attempts")}
{function("detail_best")}
{function("restore_detail")}
{function("run_one_detail")}
run_one_detail {target}
[ ! -f "$ASSETS/{target}.py" ] || cp "$ASSETS/{target}.py" "$STATE/asset_after_run"
run_one_detail {target}
[ ! -f "$ASSETS/{target}.py" ] || cp "$ASSETS/{target}.py" "$STATE/asset_after_resume"
"""
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stderr)
            read = lambda pattern: [path.read_text() for path in sorted(state.glob(pattern))]
            return {
                "assets": [(state / name).read_text().split("# ")[-1].strip() if (state / name).exists() else None for name in ("asset_after_run", "asset_after_resume")],
                "builder_inputs": read("builder_input_*"),
                "critic_inputs": read("critic_input_*"),
                "objects": {entry["id"]: entry for entry in json.loads((state / "objects.json").read_text())},
                "scores": [line.split("\t")[2] for line in (state / "records.tsv").read_text().splitlines()],
                "verdicts": [json.loads(path.read_text()) for path in sorted((state / "verdicts").glob("*.json"))],
            }

    def test_detail_builder_and_critic_receive_overlapping_owners(self):
        external = {"children": "external"}
        run = self.detail_ownership_run([
            {"id": "ceiling", "label": "Ceiling slab", "crop_bbox": [0, 0, 400, 60], "spatial_contract": {"ownership": external}},
            {"id": "cornice_rear", "label": "Rear cornice", "crop_bbox": [0, 50, 400, 20], "spatial_contract": {"ownership": external}},
            {"id": "rug", "label": "Rug", "crop_bbox": [0, 400, 400, 60], "spatial_contract": {"ownership": external}},
            {"id": "lamp", "label": "Lamp", "crop_bbox": [400, 0, 50, 60], "spatial_contract": {"ownership": external}},
            {"id": "hidden", "label": "Hidden closure", "spatial_contract": {"ownership": external}},
        ], "ceiling", [{"score": 9, "corrections": ["none"], "wrong_labels": []}], ["Ceiling slab"])
        owner = '{"id":"cornice_rear","label":"Rear cornice","ownership":{"children":"external"}}'
        for prompt in (run["builder_inputs"][0], run["critic_inputs"][0]):
            self.assertIn(f"Other inventory entries whose crops overlap this crop; each owns its own components: [{owner}]\n", prompt)
        self.assertIn('Object entry: {"id":"ceiling","label":"Ceiling slab",', run["critic_inputs"][0])
        self.assertIn('"final_label":"Ceiling slab"', run["critic_inputs"][0])

    def test_relabel_claiming_a_neighbors_component_fails_identification(self):
        included = {"children": "included"}
        objects = [
            {"id": "firebox", "label": "Dark fireplace inset", "crop_bbox": [100, 200, 180, 120], "spatial_contract": {"ownership": included}},
            {"id": "firescreen", "label": "Fireplace screen", "crop_bbox": [110, 210, 150, 110], "spatial_contract": {"ownership": included}},
        ]
        claim = {"score": 7, "corrections": ["sharpen the mesh"], "wrong_labels": ["firescreen: mesh panels, rail and pulls"]}
        clean = {"score": 5, "corrections": ["deepen the inset"], "wrong_labels": []}
        run = self.detail_ownership_run(objects, "firebox", [claim, clean], ["Dark inset with mesh screen panels", "Dark fireplace inset"])
        self.assertEqual(run["scores"], ["0", "5"])
        self.assertIn("identification check failed: the detail claims separately owned geometry: firescreen: mesh panels, rail and pulls", run["builder_inputs"][1])
        self.assertEqual(run["objects"]["firebox"]["final_label"], "Dark fireplace inset")
        self.assertEqual(run["assets"], ["2", "2"])
        self.assertEqual(run["objects"]["firescreen"], objects[1])
        run = self.detail_ownership_run(objects, "firebox", [claim, claim], ["Dark inset with mesh screen panels", "Dark inset with mesh screen panels"])
        self.assertEqual(run["scores"], ["0", "0"])
        self.assertEqual(run["objects"]["firebox"], objects[0])
        self.assertEqual(run["assets"], [None, None])
        run = self.detail_ownership_run(objects, "firebox", [claim, {**clean, "score": 0}], ["Dark inset with mesh screen panels", "Dark fireplace inset"])
        self.assertEqual(run["scores"], ["0", "0"])
        self.assertEqual(run["assets"], ["2", "2"])
        self.assertEqual(run["objects"]["firebox"]["final_label"], "Dark fireplace inset")

if __name__ == "__main__":
    if sys.argv[1:] == ["benchmark"]:
        sys.exit(benchmark())
    unittest.main()
