Examples use public-domain photographs with their attribution.
Scene data, photographs, and renders from private runs never enter this repository.
Results tables carry numbers, not images of private scenes.
Keep README for the reader: what the workflow does, how to run it, results, limits.

## Boundaries

This photo-to-scene repository names only its own components. Name another project only as a declared, versioned dependency, never through its internals. Give a needed shared service a neutral name owned by this project. Do not import the environment of machines running agents: hostnames, addresses, paths outside the repository, service or queue names, credentials, camera frames, or renders of private places. No person's name, schedule or presence enters the repository. Before landing, grep the diff for other projects' names and host details. Remove host details and undeclared project references; dependency declarations expose only the dependency's name and version.
