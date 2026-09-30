# Working on photo-to-scene

Edit by subtraction: resolve a problem by deleting code; a tactical patch over a symptom is not accepted. One implementation per thing, never two alive.

Delete code comments; keep only a why the code cannot show.

Use attributed public-domain photographs for examples. Keep private-run scene data,
photographs and renders out of the repository; results tables contain numbers.
Keep [README.md](README.md) for users: workflow, usage, results and limits.

Landing tests assert outcomes and derived lower bounds, not wall-time upper bounds,
so they pass under host load. After changing `model()` or `tree_ticks()`, measure
wall time separately on an idle host with
`python3 tools/test-pipeline-control.py benchmark`.

## Boundaries

Keep this project independent. Reference other projects only as declared, versioned
dependencies, exposing names and versions rather than internals. Give shared services
neutral project-owned names. Exclude deployment-specific paths, addresses, service
or queue names, credentials, camera frames and private renders. Before landing,
inspect the diff for undeclared project references and deployment details.
