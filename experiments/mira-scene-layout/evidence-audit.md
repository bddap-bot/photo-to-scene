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
