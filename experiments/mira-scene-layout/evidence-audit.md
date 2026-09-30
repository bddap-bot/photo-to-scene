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
