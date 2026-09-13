import subprocess
import tempfile
import unittest
from pathlib import Path


class PipelineControlTest(unittest.TestCase):
    def test_valid_builder_goto_survives_invalid_target_correction(self):
        pipeline = Path(__file__).parents[1].joinpath("pipeline.sh").read_text()
        builder = pipeline.split("builder() {", 1)[1].split("\n}\ncritic()", 1)[0]
        builder = "builder() {" + builder + "\n}"
        loop = pipeline.split("feedback=\n", 1)[1].split("done\nif [ ! -f", 1)[0]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / "state"
            prompts = root / "prompts"
            state.mkdir()
            prompts.mkdir()
            (prompts / "builder.md").write_text("build")
            script = f'''set -uo pipefail
ROOT={root!s}; STATE={state!s}; PROMPTS={prompts!s}; SUPPRESS_BUILDER_GOTO=0; REQUEST_STAGE=; REQUEST_REASON=; BUILDER_GOTOS=4; CRITIC_GOTOS=0
STAGES=(floorplan blockout identify detail integrate materials)
VALID_STAGE_TEXT="floorplan blockout identify detail integrate materials"
declare -A INVALID_RETRIES=()
calls="$STATE/calls"
printf 0 > "$calls"
printf 0 > "$STATE/detail_records"
log() {{ :; }}
valid_stage() {{ local candidate=$1 known; for known in "${{STAGES[@]}}"; do [ "$candidate" = "$known" ] && return 0; done; return 1; }}
codex() {{ local call; cat >/dev/null; call=$(( $(cat "$calls") + 1 )); printf '%s' "$call" > "$calls"; if [ "$call" -eq 1 ]; then printf '%s\n' '{{"target":"blockout","reason":"invalid field"}}' > "$STATE/goto.json"; else printf '%s\n' '{{"stage":"blockout","reason":"valid retry"}}' > "$STATE/goto.json"; fi; }}
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
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blockout=1 detail_records=0 builder_gotos=5 calls=2", result.stdout)

    def test_second_invalid_builder_goto_is_ignored(self):
        pipeline = Path(__file__).parents[1].joinpath("pipeline.sh").read_text()
        builder = pipeline.split("builder() {", 1)[1].split("\n}\ncritic()", 1)[0]
        builder = "builder() {" + builder + "\n}"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / "state"
            prompts = root / "prompts"
            state.mkdir()
            prompts.mkdir()
            (prompts / "builder.md").write_text("build")
            script = f'''set -uo pipefail
ROOT={root!s}; STATE={state!s}; PROMPTS={prompts!s}; SUPPRESS_BUILDER_GOTO=0; REQUEST_STAGE=; REQUEST_REASON=
STAGES=(floorplan blockout identify detail integrate materials)
VALID_STAGE_TEXT="floorplan blockout identify detail integrate materials"
calls="$STATE/calls"
printf 0 > "$calls"
log() {{ printf '%s\n' "$*"; }}
valid_stage() {{ local candidate=$1 known; for known in "${{STAGES[@]}}"; do [ "$candidate" = "$known" ] && return 0; done; return 1; }}
codex() {{ local call; cat >/dev/null; call=$(( $(cat "$calls") + 1 )); printf '%s' "$call" > "$calls"; printf '%s\n' '{{"target":"blockout","reason":"invalid field"}}' > "$STATE/goto.json"; }}
{builder}
rc=0
builder builder.md '' || rc=$?
printf 'rc=%s calls=%s\n' "$rc" "$(cat "$calls")"
'''
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("rc=0 calls=2", result.stdout)
        self.assertIn("second invalid target from same stage ignored", result.stdout)

    def test_detail_builder_references_entry_file_without_embedding_it(self):
        pipeline = Path(__file__).parents[1].joinpath("pipeline.sh").read_text()
        run_one_detail = pipeline.split("run_one_detail() {", 1)[1].split("\n}\nrun_detail()", 1)[0]
        self.assertIn('Object entry file: state/entry_$id.json', run_one_detail)
        self.assertIn("Read the complete JSON file before editing.", run_one_detail)
        self.assertNotIn('$(cat "$entry")', run_one_detail)

    def test_materials_gate_failure_is_scored_and_saved(self):
        pipeline = Path(__file__).parents[1].joinpath("pipeline.sh").read_text()
        run_materials = pipeline.split("run_materials() {", 1)[1].split("\n}\nwithin_s56_budget()", 1)[0]
        run_materials = "run_materials() {" + run_materials + "\n}"
        stage_verdict = "\n".join(line for line in pipeline.splitlines() if line.startswith("write_stage_check_verdict()") or line.startswith("write_spatial_check_verdict()"))
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory, "state")
            (state / "verdicts").mkdir(parents=True)
            (state / "objects.json").write_text('[{"id":"one"}]')
            (state / "spatial_observed.json").write_text("{}")
            (state / "materials.png").write_text("render")
            (state / "materials.blend").write_text("scene")
            (state / "records.tsv").write_text("")
            script = f'''set -uo pipefail
STATE={state!s}; INPUT=input.jpg; ATTEMPT_SEQ=0; BEST_S6=-1; REQUEST_STAGE=; REQUEST_REASON=
next_attempt() {{ ATTEMPT_SEQ=$((ATTEMPT_SEQ+1)); }}
log() {{ printf '%s\n' "$*"; }}
builder() {{ return 0; }}
spatial_validate() {{ printf '%s\n' '{{"valid":false,"errors":["one: material footprint mismatch"]}}' > "$3"; return 1; }}
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
        pipeline = Path(__file__).parents[1].joinpath("pipeline.sh").read_text()
        run_integrate = pipeline.split("run_integrate() {", 1)[1].split("\n}\nrun_materials()", 1)[0]
        run_integrate = "run_integrate() {" + run_integrate + "\n}"
        stage_verdict = "\n".join(line for line in pipeline.splitlines() if line.startswith("write_stage_check_verdict()") or line.startswith("write_spatial_check_verdict()"))
        integrate_helpers = "\n".join(line for line in pipeline.splitlines() if line.startswith("integrate_attempts()") or line.startswith("integrate_best()"))
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
spatial_validate() {{ printf '%s\n' '{{"valid":false,"errors":["one: footprint did not round-trip"]}}' > "$3"; return 1; }}
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

    def test_integration_attempt_budget_resumes_from_records(self):
        pipeline = Path(__file__).parents[1].joinpath("pipeline.sh").read_text()
        run_integrate = pipeline.split("run_integrate() {", 1)[1].split("\n}\nrun_materials()", 1)[0]
        run_integrate = "run_integrate() {" + run_integrate + "\n}"
        functions = "\n".join(line for line in pipeline.splitlines() if line.startswith("write_stage_check_verdict()") or line.startswith("write_spatial_check_verdict()") or line.startswith("integrate_attempts()") or line.startswith("integrate_best()"))
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
STATE={state!s}; INPUT=input.jpg; ATTEMPT_SEQ=9; REQUEST_STAGE=; REQUEST_REASON=
next_attempt() {{ ATTEMPT_SEQ=$((ATTEMPT_SEQ+1)); }}
log() {{ :; }}
builder() {{ return 0; }}
spatial_validate() {{ printf '%s\n' '{{"valid":false,"errors":["one: resumed mismatch"]}}' > "$3"; return 1; }}
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

    def test_integration_attempt_number_survives_capped_builder_redirect(self):
        pipeline = Path(__file__).parents[1].joinpath("pipeline.sh").read_text()
        run_integrate = pipeline.split("run_integrate() {", 1)[1].split("\n}\nrun_materials()", 1)[0]
        run_integrate = "run_integrate() {" + run_integrate + "\n}"
        functions = "\n".join(line for line in pipeline.splitlines() if line.startswith("write_stage_check_verdict()") or line.startswith("write_spatial_check_verdict()") or line.startswith("integrate_attempts()") or line.startswith("integrate_best()"))
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory, "state")
            (state / "verdicts").mkdir(parents=True)
            (state / "attempts").mkdir()
            for name in ("assemble.py", "integrate.png", "integrate_overlay.png", "spatial_observed.json"):
                (state / name).write_text("{}" if name.endswith(".json") else "")
            (state / "objects.json").write_text('[{"id":"one"}]')
            (state / "records.tsv").write_text("")
            script = f'''set -uo pipefail
STATE={state!s}; INPUT=input.jpg; ATTEMPT_SEQ=0; REQUEST_STAGE=; REQUEST_REASON=; SUPPRESS_BUILDER_GOTO=0; builder_calls=0; critic_calls=0
next_attempt() {{ ATTEMPT_SEQ=$((ATTEMPT_SEQ+1)); }}
log() {{ :; }}
builder() {{ builder_calls=$((builder_calls+1)); if [ "$SUPPRESS_BUILDER_GOTO" -eq 0 ]; then REQUEST_STAGE=integrate; REQUEST_REASON=capped; return 42; fi; SUPPRESS_BUILDER_GOTO=0; printf 'builder-%s' "$builder_calls" > "$STATE/assemble.py"; return 0; }}
spatial_validate() {{ return 0; }}
critic() {{ critic_calls=$((critic_calls+1)); if [ "$critic_calls" -eq 1 ]; then score=7; else score=$critic_calls; fi; if [ "$critic_calls" -lt 3 ]; then target=detail; else target=integrate; fi; jq -n --argjson score "$score" --arg target "$target" '{{score:$score,corrections:["redirect"],top_stage:$target}}' > "$2"; }}
score_of() {{ jq -r '.score // 0' "$1"; }}
record() {{ printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$5" "$6" "${{7:-}}" >> "$STATE/records.tsv"; }}
inbox() {{ :; }}
{functions}
{run_integrate}
for expected in 1 2 3; do
  rc=0
  run_integrate || rc=$?
  [ "$rc" -eq 42 ] || exit 90
  SUPPRESS_BUILDER_GOTO=1
  rc=0
  run_integrate || rc=$?
  if [ "$expected" -lt 3 ]; then [ "$rc" -eq 43 ] || exit 91; else [ "$rc" -eq 0 ] || exit 92; fi
done
printf 'attempts=%s numbering=%s calls=%s restored=%s\n' "$(integrate_attempts)" "$(cut -f2 "$STATE/records.tsv" | paste -sd, -)" "$builder_calls" "$(cat "$STATE/assemble.py")"
'''
            result = subprocess.run(["bash", "-c", script], text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("attempts=3 numbering=1,2,3 calls=6 restored=builder-2", result.stdout)

    def test_report_preserves_empty_fields_and_reports_missing_verdict(self):
        pipeline = Path(__file__).parents[1].joinpath("pipeline.sh").read_text()
        parse_record = next(line for line in pipeline.splitlines() if line.startswith("parse_record()"))
        write_report = pipeline.split("write_report() {", 1)[1].split("\n}\nfeedback=", 1)[0]
        write_report = "write_report() {" + write_report + "\n}"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / "state"
            state.mkdir()
            verdict = state / "exact.json"
            missing = state / "missing.json"
            verdict.write_text('{"score":7,"summary":"exact verdict"}')
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
        self.assertIn("| integrate | 1 | 7/10 | 4 | Initial stage entry or forward rebuild from accepted contracts. |", result.stdout)
        self.assertEqual(result.stdout.count(f"Verdict absent: `{missing}`"), 1)
        self.assertNotIn("verdict file unavailable", result.stdout)

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
run_detail() {{ calls=$((calls+1)); if [ "$SUPPRESS_BUILDER_GOTO" -eq 1 ]; then SUPPRESS_BUILDER_GOTO=0; log "GOTO cap request ignored origin=builder requested=$REQUEST_STAGE reason=builder $calls"; return 0; fi; if [ "$calls" -le 6 ]; then REQUEST_STAGE=detail; REQUEST_REASON="builder $calls"; return 42; fi; return 0; }}
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
        self.assertIn("builder=5 critic=1 calls=8", result.stdout)
        self.assertIn("GOTO cap request ignored origin=builder", result.stdout)
        self.assertIn("GOTO cap reached origin=builder requested=detail reason=builder 6", result.stdout)
        self.assertIn("GOTO count=1 origin=critic stage=detail reason=late critic", result.stdout)


if __name__ == "__main__":
    unittest.main()
