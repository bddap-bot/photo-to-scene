import subprocess
import tempfile
import unittest
from pathlib import Path


class PipelineControlTest(unittest.TestCase):
    def test_integration_gate_failure_is_scored_and_retried(self):
        pipeline = Path(__file__).parents[1].joinpath("pipeline.sh").read_text()
        run_integrate = pipeline.split("run_integrate() {", 1)[1].split("\n}\nrun_materials()", 1)[0]
        run_integrate = "run_integrate() {" + run_integrate + "\n}"
        stage_verdict = next(line for line in pipeline.splitlines() if line.startswith("write_stage_check_verdict()"))
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
REQUEST_STAGE=
REQUEST_REASON=
next_attempt() {{ ATTEMPT_SEQ=$((ATTEMPT_SEQ+1)); }}
log() {{ printf '%s\n' "$*"; }}
builder() {{ return 0; }}
spatial_validate() {{ return 1; }}
critic() {{ return 99; }}
score_of() {{ jq -r '.score // 0' "$1"; }}
record() {{ printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$5" "$6" "${{7:-}}" >> "$STATE/records.tsv"; }}
inbox() {{ :; }}
{stage_verdict}
{run_integrate}
run_integrate
printf 'attempts=%s scores=%s\n' "$ATTEMPT_SEQ" "$(cut -f3 "$STATE/records.tsv" | paste -sd, -)"
'''
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("attempts=3 scores=0,0,0", result.stdout)
        self.assertIn("FAIL integrate spatial contract did not round-trip attempt=3", result.stdout)

    def test_detail_budget_is_keyed_to_contract(self):
        pipeline = Path(__file__).parents[1].joinpath("pipeline.sh").read_text()
        functions = "\n".join(
            line for line in pipeline.splitlines() if line.startswith("detail_attempts()") or line.startswith("detail_best()")
        )
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
        pipeline = Path(__file__).parents[1].joinpath("pipeline.sh").read_text()
        run_detail = next(line for line in pipeline.splitlines() if line.startswith("run_detail()"))
        with tempfile.TemporaryDirectory() as directory:
            objects = Path(directory, "objects.json")
            objects.write_text('[{"id":"one","crop_bbox":[0,0,3,3]},{"id":"two","crop_bbox":[0,0,2,2]},{"id":"three","crop_bbox":[0,0,1,1]}]')
            script = f'''STATE={directory!s}
run_one_detail() {{ printf '%s\n' "$1"; read -r ignored || true; }}
{run_detail}
run_detail
'''
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "one\ntwo\nthree\n")

    def test_critic_budget_is_independent_and_capped_builder_exits(self):
        pipeline = Path(__file__).parents[1].joinpath("pipeline.sh").read_text()
        loop = pipeline.split("feedback=\n", 1)[1].split("done\nif [ ! -f", 1)[0]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = f'''set -uo pipefail
STATE={root!s}
STAGES=(floorplan blockout identify detail integrate materials)
VALID_STAGE_TEXT="floorplan blockout identify detail integrate materials"
BUILDER_GOTOS=0
CRITIC_GOTOS=0
declare -A INVALID_RETRIES=()
declare -A CAP_RETRIES=()
SUPPRESS_BUILDER_GOTO=0
REQUEST_STAGE=
REQUEST_REASON=
calls=0
critic_sent=0
log() {{ printf '%s\n' "$*" >> "$STATE/log"; }}
valid_stage() {{ local value=$1 item; for item in "${{STAGES[@]}}"; do [ "$value" = "$item" ] && return 0; done; return 1; }}
within_s56_budget() {{ return 0; }}
run_floorplan() {{ return 0; }}
run_blockout() {{ return 0; }}
run_identify() {{ return 0; }}
run_detail() {{ calls=$((calls+1)); if [ "$SUPPRESS_BUILDER_GOTO" -eq 1 ]; then SUPPRESS_BUILDER_GOTO=0; log "GOTO request suppressed origin=builder requested=$REQUEST_STAGE reason=builder $calls"; return 0; fi; if [ "$calls" -le 5 ] || [ "$calls" -eq 8 ]; then REQUEST_STAGE=detail; REQUEST_REASON="builder $calls"; return 42; fi; if [ "$calls" -eq 6 ]; then REQUEST_STAGE=; REQUEST_REASON="invalid builder"; return 42; fi; return 0; }}
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
        self.assertIn("builder=5 critic=1 calls=9", result.stdout)
        self.assertIn("GOTO rejected origin=builder requested= reason=target is not in canonical stage set", result.stdout)
        self.assertIn("GOTO request suppressed origin=builder", result.stdout)
        self.assertIn("GOTO cap reached origin=builder requested=detail reason=builder 8", result.stdout)
        self.assertIn("GOTO count=1 origin=critic stage=detail reason=late critic", result.stdout)


if __name__ == "__main__":
    unittest.main()
