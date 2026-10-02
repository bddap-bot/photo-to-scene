#!/usr/bin/env bash
set -uo pipefail
PIPELINE_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(realpath -m "${PHOTO_TO_SCENE_ROOT:-$PWD/work}")
STATE="$ROOT/state"
PROMPTS="$PIPELINE_DIR/prompts"
ASSETS="$ROOT/assets"
TEXTURES="$ROOT/textures"
SOURCE=$(realpath -e "${1:?usage: pipeline.sh PHOTO}") || exit 1
input_reference() { nix-shell -p python3 --run "$(printf '%q ' python3 "$PIPELINE_DIR/tools/input-reference.py" "$1" "$ROOT" "$SOURCE")"; }
INPUT_REF=$(input_reference prepare) || exit 1
INPUT="$ROOT/$INPUT_REF"
SCHEMA="$PIPELINE_DIR/verdict.schema.json"
ARTIFACTS=${BOTQ_ARTIFACTS_DIR:-$ROOT/artifacts}
mkdir -p "$STATE/crops" "$STATE/verdicts" "$STATE/attempts" "$ASSETS" "$TEXTURES" "$ARTIFACTS"
[ -f "$ASSETS/generic.py" ] || cp "$PIPELINE_DIR/builders/generic.py" "$ASSETS/generic.py"
touch "$ROOT/log.md" "$STATE/records.tsv" "$STATE/progress.md"
STAGES=(floorplan blockout identify detail)
[ ! -f "$STATE/objects.json" ] || while IFS= read -r stage_id; do STAGES+=("object:$stage_id"); done < <(jq -r '.[].id' "$STATE/objects.json")
STAGES+=(integrate materials)
VALID_STAGE_TEXT="floorplan blockout identify detail object:<id> integrate materials"
GOTO_LIMIT=5
LEGACY_GOTOS=$(cat "$STATE/goto_count" 2>/dev/null || printf 0)
BUILDER_GOTOS=$(cat "$STATE/builder_goto_count" 2>/dev/null || printf '%s' "$LEGACY_GOTOS")
CRITIC_GOTOS=$(cat "$STATE/critic_goto_count" 2>/dev/null || printf 0)
BEST_S6=$(cat "$STATE/best_s6_score" 2>/dev/null || printf '%s' -1)
[ -n "$BEST_S6" ] || BEST_S6=-1
ATTEMPT_SEQ=$(cat "$STATE/attempt_seq" 2>/dev/null || printf 0)
declare -A INVALID_RETRIES=()
MODEL_SECONDS=2100
MODEL_IDLE_SECONDS=1500
MODEL_BUSY_CPU_TICKS=10
MODEL_FAILURE=
log() { printf '%s %s\n' "$(date -Is)" "$*" | tee -a "$ROOT/log.md"; }
inbox() { command -v botq >/dev/null 2>&1 && botq inbox | tee -a "$ROOT/log.md" || true; }
next_attempt() { ATTEMPT_SEQ=$((ATTEMPT_SEQ+1)); printf '%s' "$ATTEMPT_SEQ" > "$STATE/attempt_seq"; }
score_of() { jq -r '.score // 0' "$1"; }
record() { printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$5" "$6" "${7:-}" "${8:-}" >> "$STATE/records.tsv"; }
valid_stage() { local candidate=$1 known id; for known in "${STAGES[@]}"; do [ "$candidate" = "$known" ] && return 0; done; case "$candidate" in object:*) id=${candidate#object:}; [ -f "$STATE/objects.json" ] && jq -e --arg id "$id" 'any(.id == $id)' "$STATE/objects.json" >/dev/null ;; *) return 1 ;; esac; }
goto_available() {
  local origin=$1 used=$BUILDER_GOTOS
  GOTO_RESERVE=
  [ "$origin" != critic ] || used=$CRITIC_GOTOS
  [ "$used" -lt "$GOTO_LIMIT" ] && return 0
  [ "$REQUEST_STAGE" = blockout ] || return 1
  case "${ACTIVE_STAGE:-}" in
    integrate|materials)
      GOTO_RESERVE="$STATE/${ACTIVE_STAGE}_blockout_goto_used"
      [ ! -f "$GOTO_RESERVE" ] && return 0 ;;
  esac
  GOTO_RESERVE=
  return 1
}

spatial_validate() { local output_arg=; [ -z "${3:-}" ] || output_arg="--output '$3'"; nix-shell -p python3 --run "python3 '$PIPELINE_DIR/tools/spatial-contract.py' '$STATE/objects.json' --ids '$1' ${2:-} $output_arg"; }
tree_ticks() {
  local -a queue=("$1") children stat
  local pid child task line ticks state
  while [ "${#queue[@]}" -gt 0 ]; do
    pid=${queue[0]}
    queue=("${queue[@]:1}")
    { read -r line < "/proc/$pid/stat"; } 2>/dev/null || continue
    read -ra stat <<< "${line##*) }"
    ticks=$((stat[13] + stat[14]))
    [ "$pid" = "$1" ] || ticks=$((ticks + stat[11] + stat[12]))
    state=${stat[0]}
    for task in /proc/"$pid"/task/*; do
      { read -r line < "$task/stat"; } 2>/dev/null && {
        read -ra stat <<< "${line##*) }"
        [ "${stat[0]}" != R ] || state=R
      }
      children=()
      { read -ra children < "$task/children"; } 2>/dev/null
      for child in "${children[@]}"; do
        { read -r line < "/proc/$child/stat"; } 2>/dev/null || continue
        read -ra stat <<< "${line##*) }"
        [ "${stat[1]}" != "$pid" ] || queue+=("$child")
      done
    done
    printf '%s %s %s\n' "$pid" "$ticks" "$state"
  done
}
model() {
  local log="$STATE/model.log" pid echo_pid rc start=$SECONDS last=$SECONDS scanned=0 size grown child child_ticks child_state root_state stopped=
  local samples=0 runnable=0 active busy
  local -A before=() now=()
  local -a victims=()
  MODEL_FAILURE=
  : > "$log"
  codex exec --ephemeral --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox -C "$ROOT" "$@" < <(if [ -n "${INPUT_REF:-}" ]; then printf 'Input photograph: %s, relative to the run root (your working directory). Use this value for input-photo image, source_image, and reference_image fields at every nesting level. Resolve contract image paths from the run root, including contracts in state/ or state/attempts/. Preserve other run-relative image references.\n' "$INPUT_REF"; fi; cat) >> "$log" 2>&1 &
  pid=$!
  tail -c +1 -f --pid="$pid" "$log" &
  echo_pid=$!
  while sleep 1; kill -0 "$pid" 2>/dev/null || { [ -n "$stopped" ] && [ $((SECONDS - stopped)) -lt 20 ] && kill -0 "${victims[@]}" 2>/dev/null; }; do
    busy=0
    size=$(stat -c %s "$log")
    [ "$size" -gt "$scanned" ] && [ "$(tail -c "+$((scanned + 1))" "$log" | head -c "$((size - scanned))" | tr -d '[:space:]' | wc -c)" -gt 0 ] && busy=1
    scanned=$size
    grown=0
    active=0
    root_state=
    now=()
    while read -r child child_ticks child_state; do
      [ "$child_state" != R ] || active=1
      now[$child]=$child_ticks
      grown=$((grown + child_ticks - ${before[$child]:-0}))
      [ "$child" != "$pid" ] || root_state=$child_state
    done < <(tree_ticks "$pid")
    [ "$grown" -ge "$MODEL_BUSY_CPU_TICKS" ] && busy=1
    samples=$((samples + 1))
    runnable=$((runnable + active))
    if [ "$busy" -eq 1 ] || { [ $((SECONDS - last)) -ge "$MODEL_IDLE_SECONDS" ] && [ $((runnable * 2)) -ge "$samples" ]; }; then
      last=$SECONDS; samples=0; runnable=0
    fi
    before=()
    for child in "${!now[@]}"; do before[$child]=${now[$child]}; done
    if [ -n "$stopped" ]; then [ $((SECONDS - stopped)) -lt 10 ] || kill -KILL "${victims[@]}" 2>/dev/null; continue; fi
    [ -n "$root_state" ] && [ "$root_state" != Z ] || continue
    if [ $((SECONDS - start)) -ge "$MODEL_SECONDS" ]; then MODEL_FAILURE="model call exceeded its $MODEL_SECONDS s wallclock bound"
    elif [ $((SECONDS - last)) -ge "$MODEL_IDLE_SECONDS" ]; then MODEL_FAILURE="model call had no non-whitespace output and no busy child process for $MODEL_IDLE_SECONDS s"
    else continue; fi
    stopped=$SECONDS
    mapfile -t victims < <(tree_ticks "$pid" | cut -d ' ' -f 1)
    kill -TERM "${victims[@]}" 2>/dev/null
  done
  wait "$pid"
  rc=$?
  wait "$echo_pid"
  if [ -z "$stopped" ] && [ "$rc" -ne 0 ]; then
    MODEL_FAILURE="model call exited with status $rc"
    if [ -f "$STATE/model_failed" ]; then log "FAIL consecutive model calls exited non-zero; last: $MODEL_FAILURE"; exit 1; fi
    printf '%s\n' "$MODEL_FAILURE" > "$STATE/model_failed"
  else
    rm -f "$STATE/model_failed"
    [ -n "$stopped" ] || return 0
  fi
  log "MODEL CALL FAILED $MODEL_FAILURE"
  return 1
}
builder() {
  local prompt=$1 feedback=${2:-} invalid_retry=0 cap_retry=0
  shift 2
  while :; do
    rm -f "$STATE/goto.json"
    model "$@" - < <(cat "$PROMPTS/$prompt"; if [ -n "$feedback" ]; then printf '\nOne-reentry correction context follows:\n%s\n' "$feedback"; fi) || return 0
    if [ -n "${INPUT_REF:-}" ]; then input_reference normalize || exit 1; fi
    if [ -f "$STATE/goto.json" ]; then
      REQUEST_STAGE=$(jq -r '.stage // ""' "$STATE/goto.json")
      REQUEST_REASON=$(jq -r '.reason // ""' "$STATE/goto.json")
      rm -f "$STATE/goto.json"
      if [ "$cap_retry" -eq 1 ]; then
        if valid_stage "$REQUEST_STAGE"; then log "GOTO cap request ignored origin=builder requested=$REQUEST_STAGE reason=$REQUEST_REASON"; else log "GOTO rejected origin=builder requested=$REQUEST_STAGE reason=cap fallback target is not in canonical stage set"; fi
        return 0
      fi
      if valid_stage "$REQUEST_STAGE"; then
        if goto_available builder; then return 42; fi
        log "GOTO cap reached origin=builder requested=$REQUEST_STAGE reason=$REQUEST_REASON"
        cap_retry=1
        feedback="${feedback:+$feedback$'\n'}The builder GOTO cap is reached. Do not write state/goto.json. Complete within the existing spatial contract, retaining a contract-valid artifact when available so this attempt can be recorded."
        continue
      fi
      log "GOTO rejected origin=builder requested=$REQUEST_STAGE reason=target is not in canonical stage set"
      if [ "$invalid_retry" -eq 1 ]; then log "GOTO rejected origin=builder requested=$REQUEST_STAGE reason=second invalid target from same stage ignored"; return 0; fi
      invalid_retry=1
      feedback="${feedback:+$feedback$'\n'}Your GOTO target $REQUEST_STAGE is not a stage. Valid stages: $VALID_STAGE_TEXT. Re-raise with a valid one or continue."
      continue
    fi
    return 0
  done
}
critic() { local output=$1 stage=$2; shift 2; [ -n "$MODEL_FAILURE" ] || model --output-schema "$SCHEMA" -o "$output" "$@" -; [ -z "$MODEL_FAILURE" ] || write_stage_check_verdict "$output" "$stage" "$MODEL_FAILURE"; }
detail_attempts() { awk -F '\t' -v stage="object:$1" -v contract="$2" '$1==stage && $7==contract {n++} END {print n+0}' "$STATE/records.tsv"; }
detail_best() { awk -F '\t' -v stage="object:$1" -v contract="$2" '$1==stage && $7==contract && $3+0>best {best=$3+0} END {print best+0}' "$STATE/records.tsv"; }
integrate_attempts() { awk -F '\t' '$1=="integrate" {n++} END {print n+0}' "$STATE/records.tsv"; }
integrate_best() { awk -F '\t' -v prefix="$STATE/attempts/integrate_" '$1=="integrate" {seq=$6; sub(/^.*_/,"",seq); sub(/\.json$/,"",seq); if ((!seen || $3+0>=best) && system("test -d \"" prefix seq "\"") == 0) {seen=1; best=$3+0; path=seq}} END {if (seen) print best " " path; else print "-1 "}' "$STATE/records.tsv"; }
parse_record() { local row=$1; stage=${row%%$'\t'*}; row=${row#*$'\t'}; attempt=${row%%$'\t'*}; row=${row#*$'\t'}; score=${row%%$'\t'*}; row=${row#*$'\t'}; seconds=${row%%$'\t'*}; row=${row#*$'\t'}; changed=${row%%$'\t'*}; row=${row#*$'\t'}; verdict=${row%%$'\t'*}; contract_hash=${row#*$'\t'}; }
verify_detail() {
  local id=$1 marker=$2 asset="$ASSETS/$1.py" other ref
  DETAIL_FAILURE=
  if [ ! -f "$asset" ]; then DETAIL_FAILURE="asset check failed: assets/$id.py does not exist"; return 1; fi
  if cmp -s "$asset" "$ASSETS/generic.py"; then DETAIL_FAILURE="asset check failed: assets/$id.py is byte-identical to generic.py"; return 1; fi
  while IFS= read -r other; do [ "$other" = "$asset" ] && continue; [ "$other" = "$ASSETS/generic.py" ] && continue; if cmp -s "$asset" "$other"; then DETAIL_FAILURE="asset check failed: assets/$id.py is byte-identical to ${other##*/}"; return 1; fi; done < <(find "$ASSETS" -maxdepth 1 \( -type f -o -type l \) -name '*.py' | sort)
  if ! grep -Eq '^def[[:space:]]+build\(' "$asset"; then DETAIL_FAILURE="asset check failed: assets/$id.py does not define build(entry, collection=None)"; return 1; fi
  if grep -Eq '(/home/|/Users/)|(^|[^A-Za-z])\.\./' "$asset"; then DETAIL_FAILURE="asset check failed: texture reference escapes ROOT/textures"; return 1; fi
  while IFS= read -r ref; do case "$ref" in "$TEXTURES"/*) ;; *) DETAIL_FAILURE="asset check failed: texture reference $ref is outside ROOT/textures"; return 1 ;; esac; done < <(grep -Eo '["'"'"']/[^"'"'"'[:space:]]+\.(jpg|jpeg|png|exr|hdr|tif|tiff)' "$asset" | cut -c 2- || true)
  if [ ! -f "$STATE/detail_$id.png" ] || [ ! "$STATE/detail_$id.png" -nt "$marker" ]; then DETAIL_FAILURE="asset check failed: state/detail_$id.png is not a fresh render from this builder attempt"; return 1; fi
}
write_stage_check_verdict() { local path=$1 stage=$2 failure=$3; jq -n --arg summary "$failure" --arg stage "$stage" '{scene_change:null,score:0,summary:$summary,corrections:[$summary],top_stage:$stage,wrong_labels:[],missing_objects:[]}' > "$path"; }
write_spatial_check_verdict() { local path=$1 stage=$2 validation=$3 failure="$2 spatial contract gate failed"; if jq -e '.errors | type == "array" and length > 0' "$validation" >/dev/null 2>&1; then jq --arg stage "$stage" '{scene_change:null,score:0,summary:($stage + " spatial contract gate failed: " + ((.errors | length) | tostring) + " validation error(s)"),corrections:.errors,top_stage:$stage,wrong_labels:[],missing_objects:[]}' "$validation" > "$path"; else write_stage_check_verdict "$path" "$stage" "$failure"; fi; }
run_floorplan() {
  local feedback=${1:-} best=-1 bestdir='' start score a verdict
  for a in 1 2 3; do next_attempt; start=$(date +%s); log "ENTER floorplan attempt=$a sequence=$ATTEMPT_SEQ"; builder floorplan_builder.md "$feedback" -i "$INPUT" || return $?; verdict="$STATE/verdicts/floorplan_${ATTEMPT_SEQ}.json"; critic "$verdict" floorplan -i "$INPUT" "$STATE/floorplan.png" < "$PROMPTS/floorplan_critic.md"; score=$(score_of "$verdict"); record floorplan "$a" "$score" "$(( $(date +%s)-start ))" "$feedback" "$verdict"; log "SCORE floorplan attempt=$a score=$score"; cp "$STATE/floorplan.json" "$STATE/attempts/floorplan_${ATTEMPT_SEQ}.json"; cp "$STATE/floorplan.png" "$STATE/attempts/floorplan_${ATTEMPT_SEQ}.png"; if [ -z "$MODEL_FAILURE" ] && [ "$score" -gt "$best" ]; then best=$score; bestdir=$ATTEMPT_SEQ; fi; [ "$score" -ge 8 ] && break; feedback=$(jq -r '.corrections | join("; ")' "$verdict"); done
  [ -n "$bestdir" ] || { log "FAIL floorplan no attempt completed its model calls"; return 1; }; cp "$STATE/attempts/floorplan_${bestdir}.json" "$STATE/floorplan.json"; cp "$STATE/attempts/floorplan_${bestdir}.png" "$STATE/floorplan.png"; inbox
}
run_blockout() {
  local feedback=${1:-} best=-1 bestdir='' start score a verdict validation declared
  for a in 1 2 3; do next_attempt; start=$(date +%s); log "ENTER blockout attempt=$a sequence=$ATTEMPT_SEQ"; builder blockout_builder.md "$feedback" -i "$INPUT" || return $?; verdict="$STATE/verdicts/blockout_${ATTEMPT_SEQ}.json"; validation="$STATE/verdicts/blockout_${ATTEMPT_SEQ}_validation.json"; declared=1; if [ -n "$MODEL_FAILURE" ] || spatial_validate "$(jq -r 'map(.id)|join(",")' "$STATE/objects.json")" "" "$validation"; then critic "$verdict" blockout -i "$INPUT" "$STATE/blockout.png" "$STATE/blockout_overlay.png" < "$PROMPTS/blockout_critic.md"; else declared=; log "FAIL blockout spatial contract declaration invalid attempt=$a"; write_spatial_check_verdict "$verdict" blockout "$validation"; fi; score=$(score_of "$verdict"); record blockout "$a" "$score" "$(( $(date +%s)-start ))" "$feedback" "$verdict"; log "SCORE blockout attempt=$a score=$score"; mkdir -p "$STATE/attempts/blockout_${ATTEMPT_SEQ}"; cp "$STATE/objects.json" "$STATE/blockout.py" "$STATE/blockout.png" "$STATE/blockout_overlay.png" "$STATE/attempts/blockout_${ATTEMPT_SEQ}/"; if [ -z "$MODEL_FAILURE" ] && [ -n "$declared" ] && [ "$score" -gt "$best" ]; then best=$score; bestdir=$ATTEMPT_SEQ; fi; [ "$score" -ge 8 ] && break; feedback=$(jq -r '.corrections | join("; ")' "$verdict"); done
  [ -n "$bestdir" ] || { log "FAIL blockout no attempt completed its model calls with a valid spatial-contract declaration"; return 1; }; cp "$STATE/attempts/blockout_${bestdir}/"* "$STATE/"; inbox
}
run_identify() {
  local feedback=${1:-} best=-1 bestdir='' start score a verdict
  for a in 1 2; do next_attempt; start=$(date +%s); log "ENTER identify attempt=$a sequence=$ATTEMPT_SEQ"; builder identify_builder.md "$feedback" -i "$INPUT" || return $?; verdict="$STATE/verdicts/identify_${ATTEMPT_SEQ}.json"; critic "$verdict" identify -i "$INPUT" "$STATE/objects_sheet.png" < "$PROMPTS/identify_critic.md"; score=$(score_of "$verdict"); record identify "$a" "$score" "$(( $(date +%s)-start ))" "$feedback" "$verdict"; log "SCORE identify attempt=$a score=$score"; mkdir -p "$STATE/attempts/identify_${ATTEMPT_SEQ}"; cp "$STATE/objects.json" "$STATE/objects_sheet.png" "$STATE/attempts/identify_${ATTEMPT_SEQ}/"; if [ -z "$MODEL_FAILURE" ] && [ "$score" -gt "$best" ]; then best=$score; bestdir=$ATTEMPT_SEQ; fi; [ "$score" -ge 8 ] && break; feedback=$(jq -r '((.corrections + .wrong_labels + .missing_objects) | join("; "))' "$verdict"); done
  [ -n "$bestdir" ] || { log "FAIL identify no attempt completed its model calls"; return 1; }; cp "$STATE/attempts/identify_${bestdir}/objects.json" "$STATE/objects.json"; jq 'map(. + {proposed_label: .label, final_label: .label, label_reason: "Root proposal awaiting object review."})' "$STATE/objects.json" > "$STATE/objects.json.next"; mv "$STATE/objects.json.next" "$STATE/objects.json"; cp "$STATE/attempts/identify_${bestdir}/objects_sheet.png" "$STATE/objects_sheet.png"; command -v botq >/dev/null 2>&1 && botq notify-hub "photo-to-scene: objects sheet ready $STATE/objects_sheet.png" || true; inbox
}
write_tiers() { jq -r 'sort_by(-((.spatial_contract.frame.size_xyz[0] // 0) * (.spatial_contract.frame.size_xyz[1] // 0))) | length as $n | to_entries[] | [.value.id, (if .key < (($n + 2) / 3 | floor) then "large" elif .key < ((2 * $n + 2) / 3 | floor) then "medium" else "small" end)] | @tsv' "$STATE/objects.json" > "$STATE/object_tiers.tsv"; }
run_tier_critic() {
  local tier=$1 verdict start score a feedback='' rendered='' calibration='' baseline
  for a in 1 2; do
    next_attempt; start=$(date +%s); verdict="$STATE/verdicts/tier_${tier}_${ATTEMPT_SEQ}.json"
    MODEL_FAILURE=
    if [ -z "$rendered" ]; then
      builder tier_builder.md "Tier: $tier. Object ids: $(awk -F '\t' -v tier="$tier" '$2==tier {printf "%s ",$1}' "$STATE/object_tiers.tsv")${feedback:+$'\n'$feedback}" -i "$INPUT" || return $?
      [ -n "$MODEL_FAILURE" ] || rendered=1
    fi
    critic "$verdict" detail -i "$INPUT" "$STATE/tier_${tier}.png" < <(cat "$PROMPTS/tier_critic.md"; printf '\n%s\n' "$feedback")
    score=$(score_of "$verdict"); record "tier:$tier" "$a" "$score" "$(( $(date +%s)-start ))" "${feedback:-Integrated footprint tier before descending.}" "$verdict" "" "$tier"; log "SCORE tier:$tier attempt=$a score=$score"
    if [ -n "$MODEL_FAILURE" ]; then feedback=$MODEL_FAILURE; continue; fi
    [ "$score" -lt 8 ] || { inbox; return 0; }
    if ! jq -e '
      .scene_change as $c |
      ($c | type == "object") and
      (["move","resize","rotate","add","remove","reshape"] | index($c.action) != null) and
      ([$c.subject,$c.observed,$c.desired] | all(.[]; type == "string" and test("\\S"))) and
      (.corrections[0] | type == "string" and test("\\S") and
        (test("^(floorplan|blockout|identify|detail|integrate|materials|object:[^ ]+)[.!]?$|\\b(retry|rerun|re-run|run again)\\b"; "i") | not)) and
      (.top_stage == "blockout" or .top_stage == "detail" or (.top_stage | startswith("object:")))
    ' "$verdict" >/dev/null; then
      feedback="Rejected tier non-verdict. Give an observable scene_change with action, subject, observed and desired geometry, and an actionable first correction. A comparison retry or a stage name is not a scene change."
      log "REJECT tier:$tier attempt=$a reason=$feedback"
      continue
    fi
    if [ "$(jq -r '.top_stage' "$verdict")" = blockout ]; then
      if [ -z "$calibration" ]; then
        calibration="$STATE/verdicts/tier_${tier}_${ATTEMPT_SEQ}_blockout.json"
        critic "$calibration" blockout -i "$INPUT" "$STATE/tier_${tier}.png" < "$PROMPTS/blockout_critic.md"
      fi
      baseline=$(score_of "$calibration")
      log "CALIBRATE tier:$tier tier_score=$score blockout_score=$baseline verdict=$calibration"
      if [ -n "$MODEL_FAILURE" ] || [ "$((baseline-score))" -ge 5 ] || [ "$((score-baseline))" -ge 5 ]; then
        feedback="Blockout redirect rejected: the blockout critic scored this same tier render $baseline/10 versus your $score/10 (or its call failed). Recompare the supplied render on the shared scale: 8 means composition is ready for smaller work. Explain the observable scene correction; use detail/object for detail defects."
        [ -z "$MODEL_FAILURE" ] || calibration=
        continue
      fi
    fi
    REQUEST_STAGE=$(jq -r '.top_stage' "$verdict")
    REQUEST_REASON=$(jq -r '.corrections[0]' "$verdict")
    inbox
    return 43
  done
  inbox
  log "tier:$tier review unaccepted after one retry; descending without a GOTO"
  return 0
}
restore_detail() {
  local id=$1 bestseq=$2 entry="$STATE/entry_$1.json"
  rm -f "$ASSETS/$id.py" "$STATE/detail_$id.png"
  [ -n "$bestseq" ] && [ -f "$STATE/attempts/object_${id}_${bestseq}.py" ] && cp "$STATE/attempts/object_${id}_${bestseq}.py" "$ASSETS/$id.py"
  [ -n "$bestseq" ] && [ -f "$STATE/attempts/object_${id}_${bestseq}.png" ] && cp "$STATE/attempts/object_${id}_${bestseq}.png" "$STATE/detail_$id.png"
  if [ -n "$bestseq" ] && [ -f "$STATE/attempts/object_${id}_${bestseq}.json" ]; then cp "$STATE/attempts/object_${id}_${bestseq}.json" "$entry"; jq --slurpfile reviewed "$entry" --arg id "$id" 'map(if .id == $id then . + {proposed_label:$reviewed[0].proposed_label,final_label:$reviewed[0].final_label,label:$reviewed[0].final_label,label_reason:$reviewed[0].label_reason} else . end)' "$STATE/objects.json" > "$STATE/objects.json.next" && mv "$STATE/objects.json.next" "$STATE/objects.json"; fi
}
detail_contract_hash() { jq -cS '.spatial_contract | del(.source_evidence, .regions[]?.confidence)' "$1" | sha256sum | cut -d ' ' -f1; }
reuse_detail_records() {
  local id=$1 hash=$2 verdict old_hash snapshot
  while IFS=$'\t' read -r verdict old_hash; do
    snapshot="$STATE/attempts/$(basename "$verdict")"
    [ -f "$snapshot" ] || continue
    [ "$(jq -cS '.spatial_contract' "$snapshot" | sha256sum | cut -d ' ' -f1)" = "$old_hash" ] || continue
    [ "$(detail_contract_hash "$snapshot")" = "$hash" ] || continue
    awk -F '\t' -v OFS='\t' -v stage="object:$id" -v old="$old_hash" -v hash="$hash" '$1==stage && $7==old {$7=hash} {print}' "$STATE/records.tsv" > "$STATE/records.tsv.next" && mv "$STATE/records.tsv.next" "$STATE/records.tsv"
  done < <(awk -F '\t' -v stage="object:$id" -v hash="$hash" '$1==stage && $7!=hash {print $6 "\t" $7}' "$STATE/records.tsv")
}
run_one_detail() {
  local id=$1 feedback=${2:-} force=${3:-0} entry="$STATE/entry_$1.json" best bestseq start score a rc verdict attempts marker limit contract_hash detail_context
  jq --arg id "$id" '.[] | select(.id==$id)' "$STATE/objects.json" > "$entry"
  contract_hash=$(detail_contract_hash "$entry")
  reuse_detail_records "$id" "$contract_hash"
  attempts=$(detail_attempts "$id" "$contract_hash"); best=$(detail_best "$id" "$contract_hash")
  if [ "$force" -eq 0 ] && { [ "$best" -ge 8 ] || [ "$attempts" -ge 2 ]; }; then printf '%s best=%s attempts=%s\n' "$id" "$best" "$attempts" >> "$STATE/progress.md"; inbox; return 0; fi
  if [ "$attempts" -gt 0 ] && [ -z "$feedback" ]; then
    local latest_verdict
    latest_verdict=$(awk -F '\t' -v stage="object:$id" -v contract="$contract_hash" '$1==stage && $7==contract {path=$6} END {print path}' "$STATE/records.tsv")
    [ -f "$latest_verdict" ] && feedback=$(jq -r '.corrections | join("; ")' "$latest_verdict")
  fi
  bestseq=$(awk -F '\t' -v stage="object:$id" -v contract="$contract_hash" -v prefix="$STATE/attempts/object_${id}_" '$1==stage && $7==contract && $3+0>=best {seq=$6; sub(/^.*_/,"",seq); sub(/\.json$/,"",seq); if (system("test -e \"" prefix seq ".py\" -o -e \"" prefix seq ".png\" -o -e \"" prefix seq ".json\"") == 0) {best=$3+0; path=seq}} END {print path}' "$STATE/records.tsv")
  limit=2; [ "$force" -eq 1 ] && limit=$((attempts+2))
  for ((a=attempts+1; a<=limit; a++)); do
    ACTIVE_STAGE="object:$id"
    next_attempt; start=$(date +%s); marker="$STATE/detail_${id}_${ATTEMPT_SEQ}.started"; touch "$marker"; log "ENTER object:$id attempt=$a sequence=$ATTEMPT_SEQ"; [ -L "$ASSETS/$id.py" ] && unlink "$ASSETS/$id.py"
    printf -v detail_context 'Object entry file: state/entry_%s.json\nRead the complete JSON file before editing.' "$id"
    [ -z "$feedback" ] || detail_context+=$'\n'"$feedback"
    builder detail_builder.md "$detail_context" -i "$STATE/crops/$id.png" -i "${INPUT:-$STATE/crops/$id.png}" || { rc=$?; restore_detail "$id" "$bestseq"; return "$rc"; }
    ID_FAILURE=; if ! jq -e '.proposed_label | type == "string" and length > 0' "$entry" >/dev/null || ! jq -e '.final_label | type == "string" and length > 0' "$entry" >/dev/null || ! jq -e '.label_reason | type == "string" and length > 0' "$entry" >/dev/null; then ID_FAILURE="identification check failed: proposed_label, final_label, and label_reason are required"; fi
    verdict="$STATE/verdicts/object_${id}_${ATTEMPT_SEQ}.json"
    if [ -n "$MODEL_FAILURE" ] || { [ -z "$ID_FAILURE" ] && verify_detail "$id" "$marker"; }; then critic "$verdict" "object:$id" -i "$STATE/crops/$id.png" "$STATE/detail_$id.png" "$INPUT" < <(cat "$PROMPTS/detail_critic.md"; printf '\nThe supplied object stage tag is object:%s.\n' "$id"); else write_stage_check_verdict "$verdict" "object:$id" "${ID_FAILURE:-$DETAIL_FAILURE}"; fi
    score=$(score_of "$verdict"); record "object:$id" "$a" "$score" "$(( $(date +%s)-start ))" "$feedback" "$verdict" "$contract_hash" "${ACTIVE_TIER:-}"; log "SCORE object:$id attempt=$a score=$score contract=$contract_hash tier=${ACTIVE_TIER:-none}"
    [ -n "$MODEL_FAILURE" ] || { [ -f "$ASSETS/$id.py" ] && cp "$ASSETS/$id.py" "$STATE/attempts/object_${id}_${ATTEMPT_SEQ}.py"; [ -f "$STATE/detail_$id.png" ] && cp "$STATE/detail_$id.png" "$STATE/attempts/object_${id}_${ATTEMPT_SEQ}.png"; [ -z "$ID_FAILURE" ] && cp "$entry" "$STATE/attempts/object_${id}_${ATTEMPT_SEQ}.json"; }
    if [ -z "$MODEL_FAILURE" ] && { [ "$score" -gt "$best" ] || [ -z "$bestseq" ]; }; then best=$score; bestseq=$ATTEMPT_SEQ; fi
    [ "$score" -ge 8 ] && break; feedback=$(jq -r '.corrections | join("; ")' "$verdict")
  done
  restore_detail "$id" "$bestseq"
  attempts=$(detail_attempts "$id" "$contract_hash"); best=$(detail_best "$id" "$contract_hash"); printf '%s best=%s attempts=%s contract=%s\n' "$id" "$best" "$attempts" "$contract_hash" >> "$STATE/progress.md"; inbox
}
run_detail() {
  local only=${1:-} id tier tier_rc
  local -a detail_ids=()
  if [[ "$only" == object:* ]]; then run_one_detail "${only#object:}" "${2:-}" 1; return $?; fi
  write_tiers
  for tier in large medium small; do
    mapfile -t detail_ids < <(awk -F '\t' -v tier="$tier" '$2==tier {print $1}' "$STATE/object_tiers.tsv")
    for id in "${detail_ids[@]}"; do ACTIVE_TIER=$tier run_one_detail "$id" || return $?; done
    run_tier_critic "$tier"
    tier_rc=$?
    if [ "$tier_rc" -eq 43 ] && ! goto_available critic; then
      log "GOTO cap request ignored within tier=$tier; descending to next footprint tier"
      continue
    fi
    [ "$tier_rc" -eq 0 ] || return "$tier_rc"
  done
}
run_integrate() {
  local feedback=${1:-} best bestseq start score a verdict validation completed
  [ -f "$STATE/integrate_start_epoch" ] || date +%s > "$STATE/integrate_start_epoch"
  completed=$(integrate_attempts); read -r best bestseq <<< "$(integrate_best)"
  for ((a=completed+1; a<=3; a++)); do next_attempt; start=$(date +%s); log "ENTER integrate attempt=$a sequence=$ATTEMPT_SEQ"; builder integrate_builder.md "$feedback" -i "$INPUT" || return $?; verdict="$STATE/verdicts/integrate_${ATTEMPT_SEQ}.json"; validation="$STATE/verdicts/integrate_${ATTEMPT_SEQ}_validation.json"; if [ -n "$MODEL_FAILURE" ] || spatial_validate "$(jq -r 'map(.id)|join(",")' "$STATE/objects.json")" "--observed '$STATE/spatial_observed.json'" "$validation"; then critic "$verdict" integrate -i "$INPUT" "$STATE/integrate.png" "$STATE/integrate_overlay.png" < "$PROMPTS/integrate_critic.md"; else log "FAIL integrate spatial contract did not round-trip attempt=$a"; write_spatial_check_verdict "$verdict" integrate "$validation"; fi; score=$(score_of "$verdict"); record integrate "$a" "$score" "$(( $(date +%s)-start ))" "$feedback" "$verdict"; log "SCORE integrate attempt=$a score=$score"; [ -n "$MODEL_FAILURE" ] || { mkdir -p "$STATE/attempts/integrate_${ATTEMPT_SEQ}"; cp "$STATE/assemble.py" "$STATE/integrate.png" "$STATE/integrate_overlay.png" "$STATE/spatial_observed.json" "$STATE/attempts/integrate_${ATTEMPT_SEQ}/"; }; if [ -z "$MODEL_FAILURE" ] && [ "$score" -gt "$best" ]; then best=$score; bestseq=$ATTEMPT_SEQ; fi; [ "$score" -ge 8 ] && break; REQUEST_STAGE=$(jq -r '.top_stage // "integrate"' "$verdict"); REQUEST_REASON=$(jq -r '.corrections[0] // ""' "$verdict"); [ "$REQUEST_STAGE" != integrate ] && return 43; feedback=$(jq -r '.corrections | join("; ")' "$verdict"); done
  [ -n "$bestseq" ] || { log "FAIL integrate no attempt completed its model calls"; return 1; }; cp "$STATE/attempts/integrate_${bestseq}/"* "$STATE/"; inbox
}
run_materials() {
  local feedback=${1:-} start score verdict validation
  next_attempt; start=$(date +%s); log "ENTER materials attempt=1 sequence=$ATTEMPT_SEQ"; builder materials_builder.md "$feedback" -i "$INPUT" || return $?; verdict="$STATE/verdicts/materials_${ATTEMPT_SEQ}.json"; validation="$STATE/verdicts/materials_${ATTEMPT_SEQ}_validation.json"; if [ -n "$MODEL_FAILURE" ] || spatial_validate "$(jq -r 'map(.id)|join(",")' "$STATE/objects.json")" "--observed '$STATE/spatial_observed.json'" "$validation"; then critic "$verdict" materials -i "$INPUT" "$STATE/materials.png" < "$PROMPTS/materials_critic.md"; else log "FAIL materials invalidated spatial contract"; write_spatial_check_verdict "$verdict" materials "$validation"; fi; score=$(score_of "$verdict"); record materials 1 "$score" "$(( $(date +%s)-start ))" "$feedback" "$verdict"; log "SCORE materials score=$score"
  if [ -z "$MODEL_FAILURE" ] && [ "$score" -gt "$BEST_S6" ]; then BEST_S6=$score; printf '%s' "$score" > "$STATE/best_s6_score"; cp "$STATE/materials.png" "$STATE/best_materials.png"; cp "$STATE/materials.blend" "$STATE/best_materials.blend"; cp "$verdict" "$STATE/best_materials_verdict.json"; fi
  if [ "$score" -lt 8 ]; then REQUEST_STAGE=$(jq -r '.top_stage // "materials"' "$verdict"); REQUEST_REASON=$(jq -r '.corrections[0] // ""' "$verdict"); [ "$REQUEST_STAGE" != materials ] && return 43; fi; inbox
}
within_s56_budget() { [ ! -f "$STATE/integrate_start_epoch" ] && return 0; [ "$(( $(date +%s) - $(cat "$STATE/integrate_start_epoch") ))" -lt 12600 ]; }
write_report() {
  local report="$STATE/scores.md" row stage attempt score seconds changed verdict contract_hash tier binding
  binding=$(jq -r '.top_stage // "unknown"' "$STATE/best_materials_verdict.json")
  { printf '# Staged reconstruction report\n\n| Stage | Tier | Attempt | Score | Seconds | What changed |\n|---|---|---:|---:|---:|---|\n'; while IFS= read -r row; do parse_record "$row"; tier=${row##*$'\t'}; changed=${changed//$'\n'/ }; changed=${changed//|/\\|}; [ -n "$changed" ] || changed='Initial stage entry or forward rebuild from accepted contracts.'; printf '| %s | %s | %s | %s/10 | %s | %s |\n' "$stage" "${tier:-—}" "$attempt" "$score" "$seconds" "$changed"; done < "$STATE/records.tsv"; printf '\n## GOTO history\n\n'; grep ' GOTO ' "$ROOT/log.md" 2>/dev/null || printf 'No GOTO was taken.\n'; printf '\n## Scale contract\n\n- Anchor: %s\n- Assumed television width: %s m\n' "$(jq -r '.scale_anchor.description // .scale_anchor // "recorded visual anchor"' "$STATE/floorplan.json")" "$(jq -r '.assumed_tv_width_m // .scale_anchor.width_m // "not used"' "$STATE/floorplan.json")"; printf '\n## Critic verdicts, verbatim\n\n'; while IFS= read -r row; do parse_record "$row"; printf '### %s attempt %s\n\n' "$stage" "$attempt"; if [ ! -f "$verdict" ]; then printf "Verdict absent: \`%s\`\n\n" "$verdict"; continue; fi; printf '```json\n'; cat "$verdict"; printf '\n```\n\n'; done < "$STATE/records.tsv"; printf '## Honest assessment\n\nThe final score was %s/10. The binding stage was %s, identified by the best final critic as the source of its highest-priority remaining defect.\n' "$(cat "$STATE/best_s6_score")" "$binding"; } > "$report"
}
feedback=
current=${PHOTO_TO_SCENE_STAGE:-floorplan}
ACTIVE_STAGE=$current
while :; do
  rc=0
  next=
  REQUEST_STAGE=
  REQUEST_REASON=
  ACTIVE_STAGE=$current
  if { [ "$current" = integrate ] || [ "$current" = materials ]; } && ! within_s56_budget && [ -f "$STATE/best_materials.blend" ]; then log 'WALLCLOCK cap reached; finalizing best S6'; break; fi
  case "$current" in floorplan) run_floorplan "$feedback"; rc=$?; next=blockout ;; blockout) run_blockout "$feedback"; rc=$?; next=identify ;; identify) run_identify "$feedback"; rc=$?; next=detail ;; detail) run_detail "" "$feedback"; rc=$?; next=integrate ;; object:*) run_detail "$current" "$feedback"; rc=$?; next=integrate ;; integrate) run_integrate "$feedback"; rc=$?; next=materials ;; materials) run_materials "$feedback"; rc=$?; next='done' ;; *) log "FAIL invalid current stage=$current"; exit 2 ;; esac
  if [ "$rc" -eq 42 ] || [ "$rc" -eq 43 ]; then
    origin=$([ "$rc" -eq 42 ] && printf builder || printf critic)
    if ! valid_stage "$REQUEST_STAGE"; then key="$origin:$ACTIVE_STAGE"; log "GOTO rejected origin=$origin requested=$REQUEST_STAGE reason=target is not in canonical stage set"; if [ "${INVALID_RETRIES[$key]:-0}" -eq 0 ]; then INVALID_RETRIES[$key]=1; feedback="Your GOTO target $REQUEST_STAGE is not a stage. Valid stages: $VALID_STAGE_TEXT. Re-raise with a valid one or continue."; continue; fi; log "GOTO rejected origin=$origin requested=$REQUEST_STAGE reason=second invalid target from same stage ignored"; current=$next; feedback=; continue; fi
    if ! goto_available "$origin"; then log "GOTO cap reached origin=$origin requested=$REQUEST_STAGE reason=$REQUEST_REASON"; log "GOTO cap request ignored origin=$origin requested=$REQUEST_STAGE reason=$REQUEST_REASON"; current=$next; feedback=; [ "$current" = 'done' ] && break; continue; fi
    [ -z "$GOTO_RESERVE" ] || printf 'used\n' > "$GOTO_RESERVE" || exit 1
    if [ "$origin" = builder ]; then BUILDER_GOTOS=$((BUILDER_GOTOS+1)); printf '%s' "$BUILDER_GOTOS" > "$STATE/builder_goto_count"; count=$BUILDER_GOTOS; else CRITIC_GOTOS=$((CRITIC_GOTOS+1)); printf '%s' "$CRITIC_GOTOS" > "$STATE/critic_goto_count"; count=$CRITIC_GOTOS; fi
    printf '%s' "$((BUILDER_GOTOS+CRITIC_GOTOS))" > "$STATE/goto_count"
    log "GOTO count=$count origin=$origin stage=$REQUEST_STAGE reason=$REQUEST_REASON"; current=$REQUEST_STAGE; feedback=$REQUEST_REASON; continue
  fi
  if [ "$rc" -ne 0 ]; then log "FAIL stage=$current rc=$rc"; exit "$rc"; fi
  [ "$next" = 'done' ] && break
  current=$next
  feedback=
done
if [ ! -f "$STATE/best_materials.blend" ]; then log 'FAIL no S6 scene exists'; exit 1; fi
MODEL_SECONDS=4800 builder final_builder.md "" || exit $?
[ -z "$MODEL_FAILURE" ] || { log "FAIL final $MODEL_FAILURE"; exit 1; }
write_report
cp "$STATE/best_render.png" "$STATE/side_by_side.png" "$STATE/objects_sheet.png" "$STATE/scores.md" "$STATE/floorplan.json" "$STATE/objects.json" "$PIPELINE_DIR/pipeline.sh" "$ROOT/input.json" "$ARTIFACTS/"
if [ "$(realpath "$ARTIFACTS")" != "$ROOT" ]; then mkdir -p "$ARTIFACTS/input"; cp "$INPUT" "$ARTIFACTS/$INPUT_REF"; fi
cp "$STATE/floorplan.json" "$ROOT/floorplan.json"
cp "$STATE/objects.json" "$ROOT/objects.json"
log "COMPLETE artifacts=$ARTIFACTS"
