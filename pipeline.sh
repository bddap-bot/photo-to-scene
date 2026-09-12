#!/usr/bin/env bash
set -uo pipefail
PIPELINE_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
ROOT=${PHOTO_TO_SCENE_ROOT:-$PWD/work}
STATE="$ROOT/state"
PROMPTS="$PIPELINE_DIR/prompts"
ASSETS="$ROOT/assets"
TEXTURES="$ROOT/textures"
INPUT=$(realpath "${1:?usage: pipeline.sh PHOTO}")
SCHEMA="$PIPELINE_DIR/verdict.schema.json"
ARTIFACTS=${BOTQ_ARTIFACTS_DIR:-$ROOT/artifacts}
mkdir -p "$STATE/crops" "$STATE/verdicts" "$STATE/attempts" "$ASSETS" "$TEXTURES" "$ARTIFACTS"
[ -f "$ASSETS/generic.py" ] || cp "$PIPELINE_DIR/builders/generic.py" "$ASSETS/generic.py"
touch "$ROOT/log.md" "$STATE/records.tsv" "$STATE/progress.md"
STAGES=(floorplan blockout identify detail)
[ ! -f "$STATE/objects.json" ] || while IFS= read -r stage_id; do STAGES+=("object:$stage_id"); done < <(jq -r '.[].id' "$STATE/objects.json")
STAGES+=(integrate materials)
VALID_STAGE_TEXT="floorplan blockout identify detail object:<id> integrate materials"
LEGACY_GOTOS=$(cat "$STATE/goto_count" 2>/dev/null || printf 0)
BUILDER_GOTOS=$(cat "$STATE/builder_goto_count" 2>/dev/null || printf '%s' "$LEGACY_GOTOS")
CRITIC_GOTOS=$(cat "$STATE/critic_goto_count" 2>/dev/null || printf 0)
BEST_S6=$(cat "$STATE/best_s6_score" 2>/dev/null || printf '%s' -1)
[ -n "$BEST_S6" ] || BEST_S6=-1
ATTEMPT_SEQ=$(cat "$STATE/attempt_seq" 2>/dev/null || printf 0)
declare -A INVALID_RETRIES=()
SUPPRESS_BUILDER_GOTO=0
log() { printf '%s %s\n' "$(date -Is)" "$*" | tee -a "$ROOT/log.md"; }
inbox() { command -v botq >/dev/null 2>&1 && botq inbox | tee -a "$ROOT/log.md" || true; }
next_attempt() { ATTEMPT_SEQ=$((ATTEMPT_SEQ+1)); printf '%s' "$ATTEMPT_SEQ" > "$STATE/attempt_seq"; }
score_of() { jq -r '.score // 0' "$1"; }
record() { printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$5" "$6" "${7:-}" >> "$STATE/records.tsv"; }
valid_stage() { local candidate=$1 known id; for known in "${STAGES[@]}"; do [ "$candidate" = "$known" ] && return 0; done; case "$candidate" in object:*) id=${candidate#object:}; [ -f "$STATE/objects.json" ] && jq -e --arg id "$id" 'any(.id == $id)' "$STATE/objects.json" >/dev/null ;; *) return 1 ;; esac; }
spatial_validate() { nix-shell -p python3 --run "python3 '$PIPELINE_DIR/tools/spatial-contract.py' '$STATE/objects.json' --ids '$1' ${2:-}"; }
builder() {
  local prompt=$1 feedback=${2:-}
  shift 2
  rm -f "$STATE/goto.json"
  { cat "$PROMPTS/$prompt"; if [ -n "$feedback" ]; then printf '\nOne-reentry correction context follows:\n%s\n' "$feedback"; fi; } | codex exec --ephemeral --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox -C "$ROOT" "$@" -
  local command_rc=$?
  [ "$command_rc" -eq 0 ] || return "$command_rc"
  if [ -f "$STATE/goto.json" ]; then
    REQUEST_STAGE=$(jq -r '.stage // ""' "$STATE/goto.json")
    REQUEST_REASON=$(jq -r '.reason // ""' "$STATE/goto.json")
    rm -f "$STATE/goto.json"
    if [ "$SUPPRESS_BUILDER_GOTO" -eq 1 ]; then SUPPRESS_BUILDER_GOTO=0; log "GOTO cap request ignored origin=builder requested=$REQUEST_STAGE reason=$REQUEST_REASON"; return 0; fi
    return 42
  fi
  SUPPRESS_BUILDER_GOTO=0
}
critic() { local prompt=$1 output=$2; shift 2; codex exec --ephemeral --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox -C "$ROOT" --output-schema "$SCHEMA" -o "$output" "$@" - < "$PROMPTS/$prompt"; }
detail_attempts() { awk -F '\t' -v stage="object:$1" -v contract="$2" '$1==stage && $7==contract {n++} END {print n+0}' "$STATE/records.tsv"; }
detail_best() { awk -F '\t' -v stage="object:$1" -v contract="$2" '$1==stage && $7==contract && $3+0>best {best=$3+0} END {print best+0}' "$STATE/records.tsv"; }
integrate_attempts() { awk -F '\t' '$1=="integrate" {n++} END {print n+0}' "$STATE/records.tsv"; }
integrate_best() { awk -F '\t' '$1=="integrate" && (!seen || $3+0>=best) {seen=1; best=$3+0; path=$6} END {if (seen) {sub(/^.*_/,"",path); sub(/\.json$/,"",path); print best " " path} else print "-1 "}' "$STATE/records.tsv"; }
verify_detail() {
  local id=$1 marker=$2 asset="$ASSETS/$1.py" other ref
  DETAIL_FAILURE=
  if [ ! -f "$asset" ]; then DETAIL_FAILURE="asset check failed: assets/$id.py does not exist"; return 1; fi
  if cmp -s "$asset" "$ASSETS/generic.py"; then DETAIL_FAILURE="asset check failed: assets/$id.py is byte-identical to generic.py"; return 1; fi
  while IFS= read -r other; do [ "$other" = "$asset" ] && continue; [ "$other" = "$ASSETS/generic.py" ] && continue; if cmp -s "$asset" "$other"; then DETAIL_FAILURE="asset check failed: assets/$id.py is byte-identical to ${other##*/}"; return 1; fi; done < <(find "$ASSETS" -maxdepth 1 \( -type f -o -type l \) -name '*.py' | sort)
  if ! grep -Eq '^def[[:space:]]+build\(' "$asset"; then DETAIL_FAILURE="asset check failed: assets/$id.py does not define build(entry, collection=None)"; return 1; fi
  if grep -Eq '(/home/|/Users/)|(^|[^A-Za-z])\.\./' "$asset"; then DETAIL_FAILURE="asset check failed: texture reference escapes ROOT/textures"; return 1; fi
  while IFS= read -r ref; do case "$ref" in "$TEXTURES"/*) ;; *) DETAIL_FAILURE="asset check failed: texture reference $ref is outside ROOT/textures"; return 1 ;; esac; done < <(grep -Eo '/[^"'"'"'[:space:]]+\.(jpg|jpeg|png|exr|hdr|tif|tiff)' "$asset" || true)
  if [ ! -f "$STATE/detail_$id.png" ] || [ ! "$STATE/detail_$id.png" -nt "$marker" ]; then DETAIL_FAILURE="asset check failed: state/detail_$id.png is not a fresh render from this builder attempt"; return 1; fi
}
write_check_verdict() { local path=$1 id=$2 failure=$3; jq -n --arg summary "$failure" --arg stage "object:$id" '{score:0,summary:$summary,corrections:[$summary],top_stage:$stage,wrong_labels:[],missing_objects:[]}' > "$path"; }
write_stage_check_verdict() { local path=$1 stage=$2 failure=$3; jq -n --arg summary "$failure" --arg stage "$stage" '{score:0,summary:$summary,corrections:[$summary],top_stage:$stage,wrong_labels:[],missing_objects:[]}' > "$path"; }
run_floorplan() {
  local feedback=${1:-} best=-1 bestdir='' start score a verdict
  for a in 1 2 3; do next_attempt; start=$(date +%s); log "ENTER floorplan attempt=$a sequence=$ATTEMPT_SEQ"; builder floorplan_builder.md "$feedback" -i "$INPUT" || return $?; verdict="$STATE/verdicts/floorplan_${ATTEMPT_SEQ}.json"; critic floorplan_critic.md "$verdict" -i "$INPUT" "$STATE/floorplan.png" || return $?; score=$(score_of "$verdict"); record floorplan "$a" "$score" "$(( $(date +%s)-start ))" "$feedback" "$verdict"; log "SCORE floorplan attempt=$a score=$score"; cp "$STATE/floorplan.json" "$STATE/attempts/floorplan_${ATTEMPT_SEQ}.json"; cp "$STATE/floorplan.png" "$STATE/attempts/floorplan_${ATTEMPT_SEQ}.png"; if [ "$score" -gt "$best" ]; then best=$score; bestdir=$ATTEMPT_SEQ; fi; [ "$score" -ge 8 ] && break; feedback=$(jq -r '.corrections | join("; ")' "$verdict"); done
  cp "$STATE/attempts/floorplan_${bestdir}.json" "$STATE/floorplan.json"; cp "$STATE/attempts/floorplan_${bestdir}.png" "$STATE/floorplan.png"; inbox
}
run_blockout() {
  local feedback=${1:-} best=-1 bestdir='' start score a verdict
  for a in 1 2 3; do next_attempt; start=$(date +%s); log "ENTER blockout attempt=$a sequence=$ATTEMPT_SEQ"; builder blockout_builder.md "$feedback" -i "$INPUT" || return $?; spatial_validate "$(jq -r 'map(.id)|join(",")' "$STATE/objects.json")" || { log "FAIL blockout spatial contract declaration invalid"; return 44; }; verdict="$STATE/verdicts/blockout_${ATTEMPT_SEQ}.json"; critic blockout_critic.md "$verdict" -i "$INPUT" "$STATE/blockout.png" "$STATE/blockout_overlay.png" || return $?; score=$(score_of "$verdict"); record blockout "$a" "$score" "$(( $(date +%s)-start ))" "$feedback" "$verdict"; log "SCORE blockout attempt=$a score=$score"; mkdir -p "$STATE/attempts/blockout_${ATTEMPT_SEQ}"; cp "$STATE/objects.json" "$STATE/blockout.py" "$STATE/blockout.png" "$STATE/blockout_overlay.png" "$STATE/attempts/blockout_${ATTEMPT_SEQ}/"; if [ "$score" -gt "$best" ]; then best=$score; bestdir=$ATTEMPT_SEQ; fi; [ "$score" -ge 8 ] && break; feedback=$(jq -r '.corrections | join("; ")' "$verdict"); done
  cp "$STATE/attempts/blockout_${bestdir}/"* "$STATE/"; inbox
}
run_identify() {
  local feedback=${1:-} best=-1 bestdir='' start score a verdict
  for a in 1 2; do next_attempt; start=$(date +%s); log "ENTER identify attempt=$a sequence=$ATTEMPT_SEQ"; builder identify_builder.md "$feedback" -i "$INPUT" || return $?; verdict="$STATE/verdicts/identify_${ATTEMPT_SEQ}.json"; critic identify_critic.md "$verdict" -i "$INPUT" "$STATE/objects_sheet.png" || return $?; score=$(score_of "$verdict"); record identify "$a" "$score" "$(( $(date +%s)-start ))" "$feedback" "$verdict"; log "SCORE identify attempt=$a score=$score"; mkdir -p "$STATE/attempts/identify_${ATTEMPT_SEQ}"; cp "$STATE/objects.json" "$STATE/objects_sheet.png" "$STATE/attempts/identify_${ATTEMPT_SEQ}/"; if [ "$score" -gt "$best" ]; then best=$score; bestdir=$ATTEMPT_SEQ; fi; [ "$score" -ge 8 ] && break; feedback=$(jq -r '((.corrections + .wrong_labels + .missing_objects) | join("; "))' "$verdict"); done
  cp "$STATE/attempts/identify_${bestdir}/objects.json" "$STATE/objects.json"; cp "$STATE/attempts/identify_${bestdir}/objects_sheet.png" "$STATE/objects_sheet.png"; command -v botq >/dev/null 2>&1 && botq notify-hub "photo-to-scene: objects sheet ready $STATE/objects_sheet.png" || true; inbox
}
run_one_detail() {
  local id=$1 feedback=${2:-} force=${3:-0} entry="$STATE/entry_$1.json" best bestseq start score a verdict attempts marker limit contract_hash
  jq --arg id "$id" '.[] | select(.id==$id)' "$STATE/objects.json" > "$entry"
  contract_hash=$(jq -cS '.spatial_contract' "$entry" | sha256sum | cut -d ' ' -f1)
  attempts=$(detail_attempts "$id" "$contract_hash"); best=$(detail_best "$id" "$contract_hash")
  if [ "$force" -eq 0 ] && { [ "$best" -ge 8 ] || [ "$attempts" -ge 2 ]; }; then printf '%s best=%s attempts=%s\n' "$id" "$best" "$attempts" >> "$STATE/progress.md"; inbox; return 0; fi
  if [ "$attempts" -gt 0 ] && [ -z "$feedback" ]; then
    local latest_verdict
    latest_verdict=$(awk -F '\t' -v stage="object:$id" -v contract="$contract_hash" '$1==stage && $7==contract {path=$6} END {print path}' "$STATE/records.tsv")
    [ -f "$latest_verdict" ] && feedback=$(jq -r '.corrections | join("; ")' "$latest_verdict")
  fi
  bestseq=$(awk -F '\t' -v stage="object:$id" -v contract="$contract_hash" '$1==stage && $7==contract && $3+0>=best {best=$3+0; path=$6} END {if(path!="") {sub(/^.*_/,"",path); sub(/\.json$/,"",path); print path}}' "$STATE/records.tsv")
  limit=2; [ "$force" -eq 1 ] && limit=$((attempts+2))
  for ((a=attempts+1; a<=limit; a++)); do
    ACTIVE_STAGE="object:$id"
    next_attempt; start=$(date +%s); marker="$STATE/detail_${id}_${ATTEMPT_SEQ}.started"; touch "$marker"; log "ENTER object:$id attempt=$a sequence=$ATTEMPT_SEQ"; [ -L "$ASSETS/$id.py" ] && unlink "$ASSETS/$id.py"
    builder detail_builder.md "Object entry:\n$(cat "$entry")\n$feedback" -i "$STATE/crops/$id.png" || return $?
    verdict="$STATE/verdicts/object_${id}_${ATTEMPT_SEQ}.json"
    if verify_detail "$id" "$marker"; then { cat "$PROMPTS/detail_critic.md"; printf '\nThe supplied object stage tag is object:%s.\n' "$id"; } | codex exec --ephemeral --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox -C "$ROOT" --output-schema "$SCHEMA" -o "$verdict" -i "$STATE/crops/$id.png" "$STATE/detail_$id.png" - || return $?; else write_check_verdict "$verdict" "$id" "$DETAIL_FAILURE"; fi
    score=$(score_of "$verdict"); record "object:$id" "$a" "$score" "$(( $(date +%s)-start ))" "$feedback" "$verdict" "$contract_hash"; log "SCORE object:$id attempt=$a score=$score contract=$contract_hash"
    [ -f "$ASSETS/$id.py" ] && cp "$ASSETS/$id.py" "$STATE/attempts/object_${id}_${ATTEMPT_SEQ}.py"; [ -f "$STATE/detail_$id.png" ] && cp "$STATE/detail_$id.png" "$STATE/attempts/object_${id}_${ATTEMPT_SEQ}.png"
    if [ "$score" -gt "$best" ] || [ -z "$bestseq" ]; then best=$score; bestseq=$ATTEMPT_SEQ; fi
    [ "$score" -ge 8 ] && break; feedback=$(jq -r '.corrections | join("; ")' "$verdict")
  done
  [ -n "$bestseq" ] && [ -f "$STATE/attempts/object_${id}_${bestseq}.py" ] && cp "$STATE/attempts/object_${id}_${bestseq}.py" "$ASSETS/$id.py"
  [ -n "$bestseq" ] && [ -f "$STATE/attempts/object_${id}_${bestseq}.png" ] && cp "$STATE/attempts/object_${id}_${bestseq}.png" "$STATE/detail_$id.png"
  attempts=$(detail_attempts "$id" "$contract_hash"); best=$(detail_best "$id" "$contract_hash"); printf '%s best=%s attempts=%s contract=%s\n' "$id" "$best" "$attempts" "$contract_hash" >> "$STATE/progress.md"; inbox
}
run_detail() { local only=${1:-} id; local -a detail_ids=(); if [[ "$only" == object:* ]]; then run_one_detail "${only#object:}" "${2:-}" 1; return $?; fi; mapfile -t detail_ids < <(jq -r 'sort_by(-(.crop_bbox[2] * .crop_bbox[3])) | .[].id' "$STATE/objects.json"); for id in "${detail_ids[@]}"; do run_one_detail "$id" || return $?; done; }
run_integrate() {
  local feedback=${1:-} best bestseq start score a verdict failure completed
  [ -f "$STATE/integrate_start_epoch" ] || date +%s > "$STATE/integrate_start_epoch"
  completed=$(integrate_attempts); read -r best bestseq <<< "$(integrate_best)"
  for ((a=completed+1; a<=3; a++)); do next_attempt; start=$(date +%s); log "ENTER integrate attempt=$a sequence=$ATTEMPT_SEQ"; builder integrate_builder.md "$feedback" -i "$INPUT" || return $?; verdict="$STATE/verdicts/integrate_${ATTEMPT_SEQ}.json"; if spatial_validate "$(jq -r 'map(.id)|join(",")' "$STATE/objects.json")" "--observed '$STATE/spatial_observed.json'"; then critic integrate_critic.md "$verdict" -i "$INPUT" "$STATE/integrate.png" "$STATE/integrate_overlay.png" || return $?; else failure="integration spatial contract gate failed; repair measured geometry and relationships before critic review"; log "FAIL integrate spatial contract did not round-trip attempt=$a"; write_stage_check_verdict "$verdict" integrate "$failure"; fi; score=$(score_of "$verdict"); record integrate "$a" "$score" "$(( $(date +%s)-start ))" "$feedback" "$verdict"; log "SCORE integrate attempt=$a score=$score"; mkdir -p "$STATE/attempts/integrate_${ATTEMPT_SEQ}"; cp "$STATE/assemble.py" "$STATE/integrate.png" "$STATE/integrate_overlay.png" "$STATE/spatial_observed.json" "$STATE/attempts/integrate_${ATTEMPT_SEQ}/"; if [ "$score" -gt "$best" ]; then best=$score; bestseq=$ATTEMPT_SEQ; fi; [ "$score" -ge 8 ] && break; REQUEST_STAGE=$(jq -r '.top_stage // "integrate"' "$verdict"); REQUEST_REASON=$(jq -r '.corrections[0] // ""' "$verdict"); [ "$REQUEST_STAGE" != integrate ] && return 43; feedback=$(jq -r '.corrections | join("; ")' "$verdict"); done
  cp "$STATE/attempts/integrate_${bestseq}/"* "$STATE/"; inbox
}
run_materials() {
  local feedback=${1:-} start score verdict failure
  next_attempt; start=$(date +%s); log "ENTER materials attempt=1 sequence=$ATTEMPT_SEQ"; builder materials_builder.md "$feedback" -i "$INPUT" || return $?; verdict="$STATE/verdicts/materials_${ATTEMPT_SEQ}.json"; if spatial_validate "$(jq -r 'map(.id)|join(",")' "$STATE/objects.json")" "--observed '$STATE/spatial_observed.json'"; then critic materials_critic.md "$verdict" -i "$INPUT" "$STATE/materials.png" || return $?; else failure="materials spatial contract gate failed; preserve the rendered attempt and validation evidence"; log "FAIL materials invalidated spatial contract"; write_stage_check_verdict "$verdict" materials "$failure"; fi; score=$(score_of "$verdict"); record materials 1 "$score" "$(( $(date +%s)-start ))" "$feedback" "$verdict"; log "SCORE materials score=$score"
  if [ "$score" -gt "$BEST_S6" ]; then BEST_S6=$score; printf '%s' "$score" > "$STATE/best_s6_score"; cp "$STATE/materials.png" "$STATE/best_materials.png"; cp "$STATE/materials.blend" "$STATE/best_materials.blend"; cp "$verdict" "$STATE/best_materials_verdict.json"; fi
  if [ "$score" -lt 8 ]; then REQUEST_STAGE=$(jq -r '.top_stage // "materials"' "$verdict"); REQUEST_REASON=$(jq -r '.corrections[0] // ""' "$verdict"); [ "$REQUEST_STAGE" != materials ] && return 43; fi; inbox
}
within_s56_budget() { [ ! -f "$STATE/integrate_start_epoch" ] && return 0; [ "$(( $(date +%s) - $(cat "$STATE/integrate_start_epoch") ))" -lt 12600 ]; }
write_report() {
  local report="$STATE/scores.md" stage attempt score seconds changed verdict binding
  binding=$(jq -r '.top_stage // "unknown"' "$STATE/best_materials_verdict.json")
  { printf '# Staged reconstruction report\n\n| Stage | Attempt | Score | Seconds | What changed |\n|---|---:|---:|---:|---|\n'; while IFS=$'\t' read -r stage attempt score seconds changed verdict contract_hash; do changed=${changed//$'\n'/ }; changed=${changed//|/\\|}; [ -n "$changed" ] || changed='Initial stage entry or forward rebuild from accepted contracts.'; printf '| %s | %s | %s/10 | %s | %s |\n' "$stage" "$attempt" "$score" "$seconds" "$changed"; done < "$STATE/records.tsv"; printf '\n## GOTO history\n\n'; grep ' GOTO ' "$ROOT/log.md" 2>/dev/null || printf 'No GOTO was taken.\n'; printf '\n## Scale contract\n\n- Anchor: %s\n- Assumed television width: %s m\n' "$(jq -r '.scale_anchor.description // .scale_anchor // "recorded visual anchor"' "$STATE/floorplan.json")" "$(jq -r '.assumed_tv_width_m // .scale_anchor.width_m // "not used"' "$STATE/floorplan.json")"; printf '\n## Critic verdicts, verbatim\n\n'; while IFS=$'\t' read -r stage attempt score seconds changed verdict contract_hash; do printf '### %s attempt %s\n\n```json\n' "$stage" "$attempt"; cat "$verdict" 2>/dev/null || printf '{"score":%s,"summary":"verdict file unavailable"}' "$score"; printf '\n```\n\n'; done < "$STATE/records.tsv"; printf '## Honest assessment\n\nThe final score was %s/10. The binding stage was %s, identified by the best final critic as the source of its highest-priority remaining defect.\n' "$(cat "$STATE/best_s6_score")" "$binding"; } > "$report"
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
    if ! valid_stage "$REQUEST_STAGE"; then key="$origin:$ACTIVE_STAGE"; log "GOTO rejected origin=$origin requested=$REQUEST_STAGE reason=target is not in canonical stage set"; if [ "$origin" = builder ]; then SUPPRESS_BUILDER_GOTO=1; feedback="Your GOTO target $REQUEST_STAGE is not a stage. Valid stages: $VALID_STAGE_TEXT. Re-raise with a valid one or continue."; continue; fi; if [ "${INVALID_RETRIES[$key]:-0}" -eq 0 ]; then INVALID_RETRIES[$key]=1; feedback="Your GOTO target $REQUEST_STAGE is not a stage. Valid stages: $VALID_STAGE_TEXT. Re-raise with a valid one or continue."; continue; fi; log "GOTO rejected origin=$origin requested=$REQUEST_STAGE reason=second invalid target from same stage ignored"; current=$next; feedback=; continue; fi
    key="$origin:$ACTIVE_STAGE:$REQUEST_STAGE"
    if { [ "$origin" = builder ] && [ "$BUILDER_GOTOS" -ge 5 ]; } || { [ "$origin" = critic ] && [ "$CRITIC_GOTOS" -ge 5 ]; }; then log "GOTO cap reached origin=$origin requested=$REQUEST_STAGE reason=$REQUEST_REASON"; if [ "$origin" = builder ]; then SUPPRESS_BUILDER_GOTO=1; feedback="The builder GOTO cap is reached. Continue and complete the current stage without another GOTO."; continue; fi; log "GOTO cap request ignored origin=$origin requested=$REQUEST_STAGE reason=$REQUEST_REASON"; current=$next; feedback=; [ "$current" = 'done' ] && break; continue; fi
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
builder final_builder.md "" || exit $?
write_report
cp "$STATE/best_render.png" "$STATE/side_by_side.png" "$STATE/objects_sheet.png" "$STATE/scores.md" "$STATE/floorplan.json" "$STATE/objects.json" "$PIPELINE_DIR/pipeline.sh" "$ARTIFACTS/"
cp "$STATE/floorplan.json" "$ROOT/floorplan.json"
cp "$STATE/objects.json" "$ROOT/objects.json"
log "COMPLETE artifacts=$ARTIFACTS"
