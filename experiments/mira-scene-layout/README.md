# Mira-Scene layout evaluation

**Decision: photo-alignment win for the tested fast configuration.** Opened [design issue #34](https://github.com/bddap-bot/photo-to-scene/issues/34) for seeding `objects.json` from measured layout, keeping procedural builders unchanged.
The 90-instance CCM stage completed on the GeForce RTX 2080 within the registered
8192 MiB / 60-minute stage bound. The earlier hardware rejection is withdrawn.
The candidate fails the existing spatial contracts; this is not an adoption approval.
This evaluates layout only; no workflow code changed and no mesh backend ran.

## Paired result

Only the [public example photograph](../../examples/wilson-house/source.jpg),
Library of Congress highsm.17640, was used ([source and rights](../../examples/wilson-house/ATTRIBUTION.md)).
Workflow baseline: `adbd61ae79ce9be1e5839ebaa801fb4d86f6e9a9`.
Mira-Scene source: `653cba6f4ca328797d44fd7357087573b873366a`.
Both layouts used spatial-contract gate revision
`0359029d68fe96955b0c122cf080816a4273266d`, tolerance 0.03 m.

| Measure, all 90 eligible objects | Stored blockout | Mira-Scene fast configuration |
|---|---:|---:|
| Median projected 3D-box / mask-box IoU | 0.128893 | 0.458870 |
| Median-IoU difference | — | +0.329977 |
| Objects with higher candidate IoU | — | 56/90 (62.22%) |
| Valid candidate transforms and nonempty voxel geometry | — | 76/90 |
| Spatial-contract errors, total | 14 | 431 |
| Objects without gate errors | 82/90 | 0/90 |
| Gate exit code | 1 | 1 |
| Gate runtime (s) | 0.4149 | 0.2649 |
| Median footprint-centre difference (m), valid candidates | — | 1.0215 |
| Median front-angle difference (degrees), valid candidates | — | 31.22 |
| Median X/Y/Z extent ratios, valid candidates | — | 1.001 / 2.055 / 1.078 |

| Gate error category | Stored blockout | Candidate |
|---|---:|---:|
| Declared relationships | 6 | 6 |
| Footprint | 0 | 76 |
| Facing | 0 | 64 |
| Missing named regions | 0 | 184 |
| Region bounds | 0 | 54 |
| Unmeasured aperture luminance | 2 | 2 |
| Missing candidate observation | 0 | 14 |
| Observed relationships | 6 | 31 |

The pre-registered win requires a median-IoU increase of **at least 0.10** and
higher IoU for **at least 60% of all 90 objects**. Missing/invalid transforms and
empty voxel geometry receive zero candidate IoU and remain in the denominator.
[Per-object numbers and categorized gate counts](layout-comparison.json),
[baseline gate output](baseline-layout-gate.json), and
[candidate gate output](candidate-layout-gate.json) contain the complete results.

The gate checks conformity to the stored blockout contracts, not independent
photo ground truth. The baseline input is its stored layout, not newly extracted
rendered geometry. Both records omit unmeasured appearance. The gate's two
baseline aperture errors result from absent luminance fields; they do **not**
establish black rendered apertures. Candidate body bounds do not supply named
semantic regions; those missing regions remain gate errors. Declaration errors
are retained for both layouts. The historical rendered result of **68 errors,
0/10** was not rerun and is separate from this paired layout check. The old gate
at the baseline revision returned **99 objects / 0 declaration errors**;
[that result](baseline-contract-check.json) is not an observed-geometry score.

## Measured execution

GPU: **NVIDIA GeForce RTX 2080**, compute capability 7.5, **8192 MiB nominal,
7782 MiB usable**. Third-party installation and inference ran inside the
bubblewrap `run-untrusted` sandbox. No bundled example image or hosted API was used.

| Stage used for comparison | Configuration | Allocated / reserved / process peak (MiB) | Load-inclusive wrapper time (s) | Supervisor time (s) |
|---|---|---:|---:|---:|
| Segmentation, 90 masks | SAM 2.1 FP32, one stored box prompt per call | 1375.95 / 1812 / 1954 | 107.086 | 111.170 |
| Depth | PPD and helpers, FP16, staged CPU/GPU offload, metric MoGe-2 | 2907.90 / 3060 / 3242 | 756.838 | 766.992 |
| CCM, 90 instances | FP32, CPU model offload, xformers CUTLASS, groups of 3, 10 steps, guidance 1 | 5926.09 / 6230 / 6372 | 2555.592 | 2557.710 |
| Initial similarity solve, 90 records | Pinned RANSAC solver, CPU, seed 42 | No GPU allocation | 29.923 | 32.345 |

All four stages exited 0. These are separate stage measurements, not one continuous
end-to-end run; depth timing includes resource contention. CCM sampling recorded
86 MiB of other compute allocations throughout; it is not a completely idle-device benchmark. Supervisor time includes
process startup and teardown. CUDA peaks are PyTorch allocator measurements;
process peaks are sampled every 0.5 s. SAM loading took 16.217 s; the other wrappers
do not separately instrument model loading. No unavailable load-only time is inferred.
CCM saved **90 finite CCMs**, with **80 nonempty voxel arrays**.
The solve returned **9 identity fallbacks**, which
are treated as invalid, not substituted into the scene. Depth's metric scale was
1.0790084 over 1,829,907 shared valid pixels; saved valid points/depth are finite
and valid depths positive. [All attempts](measured-run.json) retain failures and
interrupted diagnostics separately from completed stages.

![Measured stage memory and paired photo alignment](measured-memory.png)

## Method and deviations

The original fitting ladder and stop rule were recorded in
[`8f3d5c4`](https://github.com/bddap-bot/photo-to-scene/commit/8f3d5c456a906d759283d5139549b212760d728c):
released defaults, model CPU offload, attention fallback, precision fallback, and
smaller instance groups; a stage must complete within 8192 MiB and 60 minutes.
The complete released-default FP32 scene attempt was deliberately interrupted
at 1876.873 s while exploring a faster explicit-attention configuration. That is
**not a timeout, hardware bound, or released-default quality result**.

The additional **10-step / guidance-1** configuration was recorded before quality
scoring in [`a2f1ab9`](https://github.com/bddap-bot/photo-to-scene/commit/a2f1ab9b3b818c9225b72c5043f7735c178d1b0a).
Released defaults are 30 steps / guidance 3. The measured win applies to the
fast configuration; released-default full-scene quality remains unmeasured.
FP16 and mixed-precision diagnostics had non-finite outputs. Their experimental
transformer changes were removed before the FP32 comparison. The retained offload
correction uses the execution device for inputs and sets the model offload order
to image encoder → transformer → VAE. Every clean attempt is a fresh process,
with no retry of a partially offloaded model after OOM. The explicit xformers
CUTLASS operator replaces dense scaled-dot-product attention; sparse-backend
autoselection alone was not treated as proof that this rung ran.

SAM3 was access-gated, so SAM 2.1 used the same 90 stored `crop_bbox` prompts and
object IDs. All eligible IDs remain, excluding only the pre-registered room shell.
Grouping uses seeds 42 through 71. The released shorter-side resize and square
center crop loses 7 masks completely and clips 16 partially. This limitation was
retained, not repaired after observing scores. The cropped 518×518 depth point
map uses bilinear interpolation; validity uses nearest-neighbor interpolation.
The mesh-free initial similarity solver is used directly; no support adjustment,
gravity fit, mesh generation or fit to the blockout's objects is added.

Camera-space transforms enter the room through the stored baseline camera.
Canonical front **−Y is a convention**, not verified semantic front supervision.
The symmetric box convention was fixed before scoring in
[`deda60c`](https://github.com/bddap-bot/photo-to-scene/commit/deda60cfdd9c869cf558823b3b995d3c55f4c754):
both layouts project world-axis-aligned 3D boxes through their own cameras.
Baseline boxes are stored object bounds; candidate bounds and XY footprint hulls
come from transformed occupied 64³ voxel cells, including their half-cell extent.
Candidate body regions use those bounds. The depth principal point is converted
from pixel-center to pixel-edge coordinates for mask-box IoU. No camera is fitted.

Photo IoU compares with the same SAM masks that condition the candidate; this is
agreement with the observations, not independent ground truth. It does not score
appearance, semantic fronts, mesh quality or downstream rendered improvement.
Footprint, front and extent deviations above include valid candidates only, with
their denominator reported; the win metric always includes all 90.

## Correction of the earlier ruling

The original FP32 single-instance log has **5 OOM events then a CPU/CUDA device
mismatch (exit 1)**. The three-instance FP32 log has **4 OOM events then exit 143**;
the three-instance BF16 log has **5 OOM events then exit 143**. A configured limit
of 20 was incorrectly reported as observed retries. [Terminal evidence](evidence-audit.md)
corrects those counts and outcomes. Shared free-memory failures, harness errors
and interrupted attempts do not establish an 8192 MiB requirement. The original
segmentation (326 s, 5628 MiB) and depth (2995 s, 4846 MiB) measurements remain
historical successes; the regenerated outputs above were used for this comparison.

## Executed checkpoints

These are pinned evaluation dependencies, not workflow dependencies. CCM provides
canonical correspondence and voxel geometry; SAM provides object masks; PPD and
its helpers provide the camera-space point map; metric MoGe-2 supplies scale.
The mesh backends are unnecessary for the layout solve and were not installed as
workflow dependencies.

| Role | Model ID | Revision | License finding |
|---|---|---|---|
| CCM, including bundled DINOv2-with-registers | `Yang-Tian/Mira-Scene` | `e0bc99eec6ec6e2a22b81a8af1f323dd07dbdde6` | MIT original artifacts; third-party terms retained |
| Segmentation substitute | `facebook/sam2.1-hiera-large` | `665f8e2ad61cf5f53d65644ff27c8ee525124610` | Apache-2.0 |
| PPD | `gangweix/Pixel-Perfect-Depth` | `be33763bc1bc1c581869a20ffde66c36b304b1a7` | Apache-2.0 metadata |
| Depth helper | `Ruicheng/moge-2-vitl-normal` | `cb0e8bbd6b1e243589717c78e750b1ba4c093acf` | MIT metadata |
| Depth helper | `depth-anything/Depth-Anything-V2-Large` | `cbbb86a30ce19b5684b7a05155dc7e6cbc7685b9` | CC BY-NC 4.0 |
| Metric scale | `Ruicheng/moge-2-vitl` | `39c4d5e957afe587e04eec59dc2bcc3be5ecd968` | MIT metadata |

The noncommercial depth-helper terms prevent treating the evaluated stack as an
unrestricted commercial dependency. No new access agreement was accepted.
PPD source: `427a86f5882aa3f7233c1b94fbdccce87f1c8313`; MoGe source:
`74fbce054ebed49800de42d0ad0e83495065719a`. Runtime: Python 3.11.14,
PyTorch 2.5.1+cu124, torchvision 0.20.1, xformers 0.0.28.post3,
diffusers 0.40.0, transformers 5.17.0, accelerate 1.15.0.

### Mesh backend assessment

| Evaluation dependency | License | Memory and 8 GB verdict | Output and contract suitability |
|---|---|---|---|
| SAM 3D Objects, source `f91db411c50efee93d8db7aeb323885650f6f722`; default backend | SAM License for code and checkpoints; gated access and its use/redistribution conditions apply | Published minimum **32 GB**. No 8 GB execution established. No FP8/offload control in the inspected Mira-Scene SAM3D entry point | Per-instance **GLB**; downstream scene assembly exports object transforms. Geometry can support footprint/extent measurement after coordinate conversion, but does not supply semantic front or aperture contracts |
| TRELLIS.2, source `75fbf0183001ed9876c8dbb35de6b68552ee08bd`; selectable backend | Core code/model **MIT**; DINOv3 and RMBG retain separate terms | Published minimum **24 GB**. Adapter enables `low_vram` by default, moving stage models between CPU/GPU; this is not a documented 8 GB guarantee. No 8 GB execution established | Per-instance textured **GLB**, using CCM voxels as conditioning. Same downstream transform and semantic-contract limitations |
| TRELLIS.2 FP8 checkpoint, revision `b867be02d3dd9a73f460b576f12d44e9bdd4a370` | Model card says MIT | Inspected metadata only. Mira-Scene's loader has no FP8 selection/dequantization path. A separate quantized/offload implementation may fit; it was not validated and does not establish support for this pipeline or GPU | No output generated or scored |

The published mesh requirements are documentation bounds, not measured peaks or proofs against optimized ports. Mesh output can supply geometry, but semantic fronts, named regions and aperture observations still need explicit contracts. No mesh was generated or scored.

### Inspected but unexecuted checkpoints

`facebook/sam3` and `facebook/sam-3d-objects` (revision
`2e73555018d2741ccd486e56c24fac41155a1dc6`) are gated under the SAM License.
TRELLIS.2 core checkpoint `microsoft/TRELLIS.2-4B`
(`af44b45f2e35a493886929c6d786e563ec68364d`) is MIT, but its encoder
`facebook/dinov3-vitl16-pretrain-lvd1689m`
(`ea8dc2863c51be0a264bab82070e3e8836b02d51`) and background remover
`briaai/RMBG-2.0` (`5df4c9c76d8170882c34f6986e848ee07fd0ba43`) refused
anonymous download with “Access denied. This repository requires approval.”
The planned TRELLIS.2 `low_vram` trial therefore stopped at checkpoint access;
no inference time, peak or output is claimed. DINOv3 and RMBG retain their own
terms; RMBG commercial use requires a separate agreement.

`visualbruno/TRELLIS.2-4B-FP8` metadata says MIT; adapter compatibility was not
validated. Alternative `Ruicheng/moge-vitl` and the upstream-only
`microsoft/TRELLIS-image-large` sparse decoder were not downloaded or run.
Inspected hosted defaults `gemini-2.5-pro`, `gemini-3.1-flash-image-preview`
and `gpt-image-2` were not invoked. Mesh licensing and published minimums do
not bind the demonstrated mesh-free layout configuration.

### Primary evidence

- [Pinned Mira-Scene inference and checkpoint guide](https://github.com/VAST-AI-Research/Mira-Scene/blob/653cba6f4ca328797d44fd7357087573b873366a/infer_scripts/docs/environment.md), [mesh adapter](https://github.com/VAST-AI-Research/Mira-Scene/blob/653cba6f4ca328797d44fd7357087573b873366a/infer_scripts/3_trellis2_mesh.py), [scene output](https://github.com/VAST-AI-Research/Mira-Scene/blob/653cba6f4ca328797d44fd7357087573b873366a/infer_scripts/5_construct_scene.py).
- [Mira-Scene weights and license](https://huggingface.co/Yang-Tian/Mira-Scene/blob/e0bc99eec6ec6e2a22b81a8af1f323dd07dbdde6/README.md).
- [SAM3D hardware requirement](https://github.com/facebookresearch/sam-3d-objects/blob/f91db411c50efee93d8db7aeb323885650f6f722/doc/setup.md), [license](https://github.com/facebookresearch/sam-3d-objects/blob/f91db411c50efee93d8db7aeb323885650f6f722/LICENSE).
- [TRELLIS.2 hardware and licensing](https://github.com/microsoft/TRELLIS.2/blob/75fbf0183001ed9876c8dbb35de6b68552ee08bd/README.md), [offload implementation](https://github.com/microsoft/TRELLIS.2/blob/75fbf0183001ed9876c8dbb35de6b68552ee08bd/trellis2/pipelines/trellis2_image_to_3d.py).
- [RMBG terms](https://huggingface.co/briaai/RMBG-2.0), [DINOv3 terms](https://huggingface.co/facebook/dinov3-vitl16-pretrain-lvd1689m), [depth checkpoint terms](https://huggingface.co/depth-anything/Depth-Anything-V2-Large), [FP8 metadata](https://huggingface.co/visualbruno/TRELLIS.2-4B-FP8).
- [FlashAttention GPU/precision support](https://github.com/Dao-AILab/flash-attention#nvidia-cuda-support), [Mira-Scene paper](https://arxiv.org/abs/2609.23796). Published benchmark gains are not measurements on this photograph.
