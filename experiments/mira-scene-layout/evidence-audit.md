# CCM terminal evidence

```text
Audit of original CCM logs; counts are logged OOM events, not configured limits.

ccm-g1fp32.log
co-tenant OOM retry 0: free 20 MiB
co-tenant OOM retry 1: free 19 MiB
co-tenant OOM retry 2: free 36 MiB
co-tenant OOM retry 3: free 34 MiB
co-tenant OOM retry 4: free 62 MiB
RuntimeError: Expected all tensors to be on the same device, but found at least two devices, cpu and cuda:0! (when checking argument for argument mat1 in method wrapper_CUDA_addmm)
rc=1

ccm-g3fp32-oom.log
co-tenant OOM retry 0: free 89 MiB
co-tenant OOM retry 1: free 89 MiB
co-tenant OOM retry 2: free 89 MiB
co-tenant OOM retry 3: free 89 MiB
rc=143

ccm-g3bf-oom.log
co-tenant OOM retry 0: free 1790 MiB
co-tenant OOM retry 1: free 1933 MiB
co-tenant OOM retry 2: free 1913 MiB
co-tenant OOM retry 3: free 1933 MiB
co-tenant OOM retry 4: free 1913 MiB
rc=143
```

## Clean grouped and BF16 attempts

Each attempt used a fresh process, model CPU offload and the expandable allocator,
with no OOM retry. The source and checkpoint revisions remain those in the report.

```text
FP32, 3 instances:
CUDA out of memory. Tried to allocate 226.00 MiB.
Free at failure: 145.62 MiB.
Peak sampled process: 6910 MiB.
Measurement wrapper: 35.349825 s; supervisor: 37.658075 s.
exit=1; timed_out=false

BF16, 1 instance, PyTorch scaled_dot_product_attention:
CUDA out of memory. Tried to allocate 2.67 GiB.
Free at failure: 1.43 GiB; process memory at failure: 5.46 GiB.
Peak sampled process: 5588 MiB.
Measurement wrapper: 19.912642 s; supervisor: 21.849507 s.
exit=1; timed_out=false
```

The FP32 failure remains below the nominal device bound and cannot rule out an
idle card. The BF16 allocation plus reported process memory exceeds 8 GiB for
that configuration; it does not rule out FP32. A separate initial launch exited
127 before inference because its Python interpreter was unavailable; restoring
the exact interpreter resolved that environment failure. It is not a model OOM.

```text
FP32, 2 instances:
CCM_FINITE g00 True VOXELS [3441, 11756]
Done. 1 cases processed.
Measurement wrapper: 346.633235 s; supervisor: 348.834690 s.
Peak allocated: 6396.252441 MiB; reserved: 6770 MiB; process: 6912 MiB.
exit=0; timed_out=false
```

## Three-instance FP32 with 7418 MiB initially free

```text
Expandable allocator:
CUDA out of memory. Tried to allocate 130.00 MiB.
Free at failure: 185.06 MiB.
Peak allocated: 6980.6875 MiB; reserved: 7150 MiB; process: 7232 MiB.
Measurement wrapper: 30.495193 s; supervisor: 32.431023 s.
exit=1; timed_out=false

CUDA asynchronous allocator:
torch.OutOfMemoryError: Allocation on device
Peak allocated: 6339.705952 MiB; reserved: 7136 MiB; process: 7298 MiB.
Measurement wrapper: 16.401055 s; supervisor: 17.923026 s.
exit=1; timed_out=false
```

Neither attempt establishes an 8192 MiB requirement. The expandable allocator
failed even though the reported free bytes exceeded the request. The asynchronous
allocator did not report a requested size. Its raw wrapper label was `error`
because the message lacks the phrase `out of memory`; the recorded `oom` outcome
uses the traceback's exception type. Subsequent measurements classify that type
directly. A launch preceding these attempts exited 127 before inference because
the exact interpreter was missing; restoring it resolved the launch failure.

## Complete fast configuration

FP32, model CPU offload, expandable allocator, explicit xformers CUTLASS,
10 steps and guidance 1; 30 groups of three. Fresh process, no OOM retries.

```text
CCM_FINITE g00 True VOXELS [5343, 1742, 7692]
CCM_FINITE g01 True VOXELS [4391, 6642, 11422]
CCM_FINITE g02 True VOXELS [2630, 1831, 0]
CCM_FINITE g03 True VOXELS [2008, 3227, 1150]
CCM_FINITE g04 True VOXELS [2153, 2763, 2855]
CCM_FINITE g05 True VOXELS [2094, 872, 16669]
CCM_FINITE g06 True VOXELS [3072, 15614, 15220]
CCM_FINITE g07 True VOXELS [2530, 2992, 10601]
CCM_FINITE g08 True VOXELS [849, 2991, 9858]
CCM_FINITE g09 True VOXELS [3688, 1099, 2052]
CCM_FINITE g10 True VOXELS [1529, 2597, 0]
CCM_FINITE g11 True VOXELS [656, 3320, 714]
CCM_FINITE g12 True VOXELS [6688, 5837, 5005]
CCM_FINITE g13 True VOXELS [1211, 8521, 12969]
CCM_FINITE g14 True VOXELS [8807, 3861, 1026]
CCM_FINITE g15 True VOXELS [12445, 17758, 1573]
CCM_FINITE g16 True VOXELS [1140, 5500, 3801]
CCM_FINITE g17 True VOXELS [2375, 4758, 1884]
CCM_FINITE g18 True VOXELS [0, 6968, 6975]
CCM_FINITE g19 True VOXELS [1102, 0, 4325]
CCM_FINITE g20 True VOXELS [0, 5676, 12008]
CCM_FINITE g21 True VOXELS [3440, 0, 0]
CCM_FINITE g22 True VOXELS [4416, 3182, 723]
CCM_FINITE g23 True VOXELS [0, 0, 1906]
CCM_FINITE g24 True VOXELS [2893, 4722, 2746]
CCM_FINITE g25 True VOXELS [9217, 1378, 1277]
CCM_FINITE g26 True VOXELS [3179, 47, 4693]
CCM_FINITE g27 True VOXELS [2232, 4816, 5824]
CCM_FINITE g28 True VOXELS [579, 821, 1432]
CCM_FINITE g29 True VOXELS [5909, 0, 2591]
Done. 30 cases processed.
Wrapper: 2555.592468 s; supervisor: 2557.709845 s.
Peak allocated: 5926.085449 MiB; reserved: 6230 MiB; process: 6372 MiB.
exit=0; timed_out=false
```

Independent saved-array validation: 90 finite CCMs, 80 nonempty voxel arrays;
all 90 saved masks match the same nearest-neighbor resize and center crop of
the original masks. The CPU solve produced 90 finite records, including nine
identity fallbacks. Invalid poses and empty voxel geometry leave 76 usable
candidate observations. All 90 IDs remain in the paired photo denominator.

The 30-step FP32 scene attempt was deliberately interrupted after 1876.873252 s
with return code -15 and timed_out=false. It is not a 60-minute timeout. The
additional fast configuration was registered before photo scoring; its success
does not establish released-default full-scene quality.
