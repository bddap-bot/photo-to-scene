# Photo to Scene

Photo to Scene reconstructs a room from one photograph as a Blender scene. It uses a staged builder/critic pipeline so layout, object identification, detailed geometry, integration, and materials can be evaluated independently. Critic feedback can send execution back to the stage that owns a defect.

Status: the pipeline reaches 5/10 on its first real scene.

## Run a new reconstruction

The pipeline requires Bash, `jq`, Codex CLI, Blender, ImageMagick, and `nix-shell`. From an empty working directory, provide one reference photograph:

```sh
PHOTO_TO_SCENE_ROOT="$PWD/work" ./pipeline.sh /absolute/path/to/photo.jpg
```

The working directory receives durable contracts and intermediate state. The principal outputs are:

- `floorplan.json`: room geometry, camera, fixed features, and scale evidence
- `objects.json`: visible-object inventory, image crops, explicit spatial frames, footprints, relationships, ownership, and contact data
- `assets/<id>.py`: isolated procedural Blender builders
- `state/*.png`: stage and final renders
- `state/scores.md`: critic scores, changes, and GOTO history

Set `PHOTO_TO_SCENE_STAGE` to a stage name to resume from files already on disk. Copy `builders/generic.py` to the work directory as `assets/generic.py` before starting or resuming the detail stage. Optional material maps belong in the work directory's `textures/` directory; `tools/fetch-polyhaven.py` records the remote manifest while downloading selected files.

## Stages

```text
photo
  ↓
S1 floorplan → S2 blockout → S3 identify → S4 detail per object
     ↑              ↑                            ↓
     └──────────── GOTO ← S6 materials ← S5 integrate
                                      ↓
                              final render + scores
```

See [docs/STAGES.md](docs/STAGES.md) for contracts, retries, validation, and resume behavior.

## Spatial invariants

Blockout is the single authority for spatial evidence. Every object carries a machine-checked local-to-room frame, front direction, footprint, semantic regions, relationships, and ownership. Detail assets use a normalized local frame. Integration must round-trip the invariants, and final materials must retain source-visible apertures.
