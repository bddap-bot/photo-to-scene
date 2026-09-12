import subprocess
import tempfile
import unittest
from pathlib import Path


class PipelineControlTest(unittest.TestCase):
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
run_detail() {{ calls=$((calls+1)); if [ "$SUPPRESS_BUILDER_GOTO" -eq 1 ]; then SUPPRESS_BUILDER_GOTO=0; log "GOTO cap request ignored origin=builder requested=detail reason=builder $calls"; return 0; fi; if [ "$calls" -le 7 ]; then REQUEST_STAGE=detail; REQUEST_REASON="builder $calls"; return 42; fi; return 0; }}
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
        self.assertIn("GOTO count=1 origin=critic stage=detail reason=late critic", result.stdout)


if __name__ == "__main__":
    unittest.main()
