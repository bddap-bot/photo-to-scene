# Mira-Scene feasibility and layout experiment

Decision target: can measured per-object layout improve the existing blockout,
and can generated meshes replace procedural detail builders on an 8 GB GPU?
This is an evaluation dependency, not a workflow dependency. No workflow code changes.

## Design and method (recorded before evaluation)

- Input: only the [public example photograph](../../examples/wilson-house/source.jpg), Library of Congress highsm.17640; [source and rights](../../examples/wilson-house/ATTRIBUTION.md).
- Baseline workflow: `adbd61ae79ce9be1e5839ebaa801fb4d86f6e9a9`.
- Evaluation dependency: Mira-Scene, with its exact source revision and checkpoint IDs to be recorded in the results.
- First settle checkpoint licenses and hardware feasibility for GeForce RTX 2080, 8192 MiB. Inspect the released pipeline and primary model documentation. Clone third-party source into isolated scratch; run any installation or inference through `run-untrusted`. Do not use bundled scene images.
- If a documented binding memory requirement exceeds this GPU and no supported fitting configuration is established, stop at box 1. Record that bound, distinguish it from measured peak memory, and leave inference runtime and candidate scores unmeasured.
- Otherwise run only the public input, retain per-instance transformations, and compare footprint, front and scale with the existing blockout using `tools/spatial-contract.py`. This gate checks contracts and observed invariants, not independent photo ground truth. Keep photo assessment distinct from contract conformity.
- Assess the plugged-in mesh backend separately: version, checkpoint licenses, memory including available FP8/offload modes, output formats and whether its transformations support footprint, front and aperture validation.
- Publish a results table. A demonstrated layout win opens a design issue for seeding `objects.json` without changing builders; failure of hardware feasibility or a measured loss closes #24. Do not claim a visual or spatial loss without inference.

## Results and decision

**Stop at box 1; reject adoption on this GPU.** The released complete pipeline has
no established supported configuration within 8 GB. This is a hardware-feasibility
loss, not a measured layout-quality loss. No candidate inference, generated mesh,
render, or photo-based comparison was performed. No integration design issue is
warranted. Close #24 with the table below; reopen only with a fitting, validated
pipeline configuration or a larger GPU.

| Measure | Existing blockout / procedural detail | Mira-Scene candidate |
|---|---|---|
| Workflow SHA | `adbd61ae79ce9be1e5839ebaa801fb4d86f6e9a9` | Same evaluation baseline |
| Mira-Scene evaluation dependency | — | `653cba6f4ca328797d44fd7357087573b873366a` |
| GPU inventory, checked through the sandbox | — | NVIDIA GeForce RTX 2080, **8192 MiB** |
| Binding published GPU requirement | No new baseline inference | SAM3D **at least 32 GB**; TRELLIS.2 **at least 24 GB**; both exceed 8 GiB even interpreting GB as decimal |
| Fresh existing spatial gate, declaration-only | **99 objects, 0 errors, valid**, exit 0 | Not run: no candidate contracts |
| Gate runtime | **0.559 s**, one declaration-only invocation | Inference runtime **not measured**; 0 inference calls |
| Observed geometry gate | Previously recorded **0/10, 68 errors** | **N/A**, no generated geometry |
| Footprint / region errors | Previously recorded **36 / 26**, plus **6** support errors | **N/A** |
| Front and scale vs photograph | No new independent measurements | **N/A** |
| Layout decision | Retain current workflow; known errors remain | Feasibility loss at box 1; quality undecided |
| Detail-backend decision | Retain procedural builders | No demonstrated replacement on this GPU |

The [fresh declaration result](baseline-contract-check.json) comes from the
unchanged `tools/spatial-contract.py`, all IDs in `examples/wilson-house/objects.json`,
default tolerance 0.03 m, without `--observed`. It does **not** contradict the
[previous final-scene failure](../../examples/wilson-house/report.md): that gate
checked observed geometry. The 68-error result was not rerun here. The source
photograph is the only eligible scene input; no bundled demonstration scene was
used. Source inspection and model metadata reads do not constitute inference.
Third-party source was cloned into isolated scratch; no third-party install or
inference was executed. The sandbox GPU inventory command succeeded.

### Mesh backend assessment

| Evaluation dependency | License | Memory and 8 GB verdict | Output and contract suitability |
|---|---|---|---|
| SAM 3D Objects, source `f91db411c50efee93d8db7aeb323885650f6f722`; default backend | SAM License for code and checkpoints; gated access and its use/redistribution conditions apply | Published minimum **32 GB**. No 8 GB execution established. No FP8/offload control in the inspected Mira-Scene SAM3D entry point | Per-instance **GLB**; downstream scene assembly exports object transforms. Geometry can support footprint/extent measurement after coordinate conversion, but does not supply semantic front or aperture contracts |
| TRELLIS.2, source `75fbf0183001ed9876c8dbb35de6b68552ee08bd`; selectable backend | Core code/model **MIT**; DINOv3 and RMBG retain separate terms | Published minimum **24 GB**. Adapter enables `low_vram` by default, moving stage models between CPU/GPU; this is not a documented 8 GB guarantee. No 8 GB execution established | Per-instance textured **GLB**, using CCM voxels as conditioning. Same downstream transform and semantic-contract limitations |
| TRELLIS.2 FP8 checkpoint, revision `b867be02d3dd9a73f460b576f12d44e9bdd4a370` | Model card says MIT | Inspected metadata only. Mira-Scene's loader has no FP8 selection/dequantization path. A separate quantized/offload implementation may fit; it was not validated and does not establish support for this pipeline or GPU | No output generated or scored |

The published GPU requirements are **documentation bounds, not measured allocation
peaks or proofs that every possible port fails**. The full pipeline has additional
precision/kernel constraints: CCM explicitly selects BF16, while the installed
GPU class is Turing; upstream FlashAttention-2 supports BF16 on Ampere or newer.
A different attention/precision implementation needs validation. Quantization of
a mesh model alone does not validate CCM, segmentation, depth, or assembly.

The scene output includes `scene.glb`, `scene_with_floor.glb`, `scene.ply` and
`scene_optimization.json`. The JSON records per-object 4×4 transforms in initial,
gravity-adjusted and final camera/floor frames, preserving rotation, translation
and scale. Its floor frame is +Y up; the workflow uses XY footprints and Z height.
A consumer would need axis/unit calibration, stable instance-to-contract IDs,
semantic fronts, named regions and aperture observations. A projected mesh
footprint and bounding extents are measurable; front semantics and source-visible
aperture luminance cannot be inferred from a transform alone. Thus these artifacts
are potentially checkable geometry, not drop-in spatial-contract records. No
adapter was implemented.

### Checkpoint inventory and licensing

These are **declared evaluation dependencies**, not installed workflow dependencies.
No checkpoint was loaded. IDs below cover the released configuration and selectable
alternatives inspected; inclusion does not mean the model was executed.

| Role | Model ID / artifact | License or access finding |
|---|---|---|
| Required CCM | `Yang-Tian/Mira-Scene`, `pipeline/`, revision `e0bc99eec6ec6e2a22b81a8af1f323dd07dbdde6` | MIT for original model artifacts; retains third-party component terms. Includes DINOv2-with-registers image encoder; no separate encoder download used |
| Segmentation | `facebook/sam3` | SAM License, gated |
| Default depth | `gangweix/Pixel-Perfect-Depth` | Apache-2.0 model metadata |
| Default depth helper | `Ruicheng/moge-2-vitl-normal` | MIT model metadata |
| Default depth helper | `depth-anything/Depth-Anything-V2-Large` | CC BY-NC 4.0; not an unrestricted commercial workflow dependency |
| Alternative depth | `Ruicheng/moge-vitl` | MIT model metadata |
| Alternative / metric depth | `Ruicheng/moge-2-vitl` | MIT model metadata |
| Default mesh | `facebook/sam-3d-objects`, revision `2e73555018d2741ccd486e56c24fac41155a1dc6` | SAM License; anonymous checkpoint license-file request returned HTTP 401; public source license supplies the terms |
| Alternative mesh | `microsoft/TRELLIS.2-4B`, revision `af44b45f2e35a493886929c6d786e563ec68364d` | MIT |
| Alternative mesh image encoder | `facebook/dinov3-vitl16-pretrain-lvd1689m`, revision `ea8dc2863c51be0a264bab82070e3e8836b02d51` | DINOv3 License, gated |
| Alternative mesh background removal | `briaai/RMBG-2.0`, revision `5df4c9c76d8170882c34f6986e848ee07fd0ba43` | Noncommercial terms; commercial use requires separate agreement |
| Quantized mesh candidate, metadata only | `visualbruno/TRELLIS.2-4B-FP8` | MIT model metadata; unvalidated loader compatibility |

Hosted model IDs in the inspected defaults are `gemini-2.5-pro` (segmentation),
`gemini-3.1-flash-image-preview` (mesh conditioning redraw) and `gpt-image-2`
(optional floor texture/environment). No API was invoked. The upstream TRELLIS.2
full pipeline also references `microsoft/TRELLIS-image-large` for its sparse
structure decoder; the Mira-Scene adapter loads the five shape/texture models
and consumes CCM voxels instead. No such extra checkpoint was downloaded.

The original CCM and core TRELLIS.2 licenses permit use with their license
conditions; this does **not** make the assembled default pipeline wholly MIT.
Noncommercial depth/background-removal terms and gated model agreements remain
separate adoption constraints. This evaluation does not authorize commercial use
of those restricted dependencies.

### Primary evidence

- [Pinned Mira-Scene inference and checkpoint guide](https://github.com/VAST-AI-Research/Mira-Scene/blob/653cba6f4ca328797d44fd7357087573b873366a/infer_scripts/docs/environment.md), [mesh adapter](https://github.com/VAST-AI-Research/Mira-Scene/blob/653cba6f4ca328797d44fd7357087573b873366a/infer_scripts/3_trellis2_mesh.py), [scene output](https://github.com/VAST-AI-Research/Mira-Scene/blob/653cba6f4ca328797d44fd7357087573b873366a/infer_scripts/5_construct_scene.py).
- [Mira-Scene weights and license](https://huggingface.co/Yang-Tian/Mira-Scene/blob/e0bc99eec6ec6e2a22b81a8af1f323dd07dbdde6/README.md).
- [SAM3D hardware requirement](https://github.com/facebookresearch/sam-3d-objects/blob/f91db411c50efee93d8db7aeb323885650f6f722/doc/setup.md), [license](https://github.com/facebookresearch/sam-3d-objects/blob/f91db411c50efee93d8db7aeb323885650f6f722/LICENSE).
- [TRELLIS.2 hardware and licensing](https://github.com/microsoft/TRELLIS.2/blob/75fbf0183001ed9876c8dbb35de6b68552ee08bd/README.md), [offload implementation](https://github.com/microsoft/TRELLIS.2/blob/75fbf0183001ed9876c8dbb35de6b68552ee08bd/trellis2/pipelines/trellis2_image_to_3d.py).
- [RMBG terms](https://huggingface.co/briaai/RMBG-2.0), [DINOv3 terms](https://huggingface.co/facebook/dinov3-vitl16-pretrain-lvd1689m), [depth checkpoint terms](https://huggingface.co/depth-anything/Depth-Anything-V2-Large), [FP8 metadata](https://huggingface.co/visualbruno/TRELLIS.2-4B-FP8).
- [FlashAttention GPU/precision support](https://github.com/Dao-AILab/flash-attention#nvidia-cuda-support), [Mira-Scene paper](https://arxiv.org/abs/2609.23796). Published benchmark gains are not measurements on this photograph.

## Measured layout run: design and stop rule (recorded before execution)

The ruling above rests on published mesh-backend minimums. Mira-Scene's layout
does not use a mesh: `5_construct_scene.py` solves each object's pose and scale
with `solve_similarity_transforms` from the CCM, the depth point map and the
instance masks; meshes enter only later support placement and GLB export. The
stages that produce the layout were never run on this GPU. This run measures
them and then compares the layout with the blockout. The earlier baseline
numbers stand.

**Stages.** Segmentation, depth (released default: Pixel-Perfect Depth with its
MoGe-2 and Depth Anything V2 helpers; `--enable_metric` for metric scale),
CCM (`2_inference_CCM.py` at its released defaults, pinned source above) and the
mesh-free initial layout solve. Every third-party install and inference step runs
through the bubblewrap sandbox on the GeForce RTX 2080 (8192 MiB). The GPU is
shared with resident processes; their memory is recorded at the start of each stage.

**Measures, per stage and scene.** Peak PyTorch allocated and reserved memory
inside the stage process; peak device memory sampled every 0.5 s minus the
pre-stage baseline; wall-clock time with model load reported separately.

**Fitting ladder.** Each stage runs at its released defaults first. On an
out-of-memory failure it retries, in order, with model CPU offload, then the
xformers attention backend (the PyTorch backend if xformers has no build for
compute capability 7.5), then both. If BF16 kernels are unavailable on this
architecture, FP16 and then FP32 are tried and the precision is recorded. CCM
batches every instance of a scene together, so if the full instance set does
not fit at the last rung, the largest instance count that fits is found by
halving and the scene runs in groups of that size, recorded as a deviation.

**Stop rule.** A stage is feasible when some rung completes the Wilson House
input within 8192 MiB of device memory and 60 minutes of wall time. It is
infeasible when every rung fails; the binding number is the failing allocation
or the elapsed time. The layout half is feasible when depth, CCM and the layout
solve are all feasible. A checkpoint behind an access agreement this evaluation
holds no account for is not obtained: its stage is recorded as blocked, not
infeasible, and an ungated model with the same interface substitutes for it. For
segmentation that substitute is SAM 2.1 (`facebook/sam2.1-hiera-large`), box-prompted
with each blockout object's `crop_bbox`, which also carries the blockout's object
IDs through to the comparison. If the layout half is infeasible, box 1 stops
with that number.

**Mesh backend.** TRELLIS.2 runs once on one instance with the adapter's default
`low_vram`, and what happens is recorded: output, peak memory and time, or the
exact failure.

**Comparison.** Objects: every blockout object with a `crop_bbox`, except the
room shell (`floor`, `ceiling`, `wall_w`, `north_*`, `cornice_n`, `baseboard_n`),
which also supplies no instance for CCM. Mira-Scene's camera-space transforms
enter the blockout's room frame through the blockout's own camera
(`floorplan.json`), with no fitting to objects; the canonical front is -Y, the
glTF front after the pipeline's canonical alignment. For each object:

1. *Photo alignment*: IoU between the image-space box of each layout's projected
   3D box, each through its own camera, and the box of the object's mask.
2. *Contract gate*: `tools/spatial-contract.py` on the blockout's contracts, with
   Mira-Scene's footprint, front and body region as the observed record, at the
   default 0.03 m tolerance; errors counted by kind.
3. *Deviation*: footprint-centre distance, front angle and extent ratios.

Photo alignment favours a pixel-aligned method by construction and uses the same
masks and depth Mira-Scene fits to; it measures agreement with the observations,
not ground truth. **Decision rule:** Mira-Scene wins when its median per-object
photo IoU exceeds the blockout's by at least 0.10 and it is higher on at least
60 % of compared objects. A win opens the design issue named in #24; otherwise
#24 closes with the table.
