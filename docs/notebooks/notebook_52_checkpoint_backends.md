# Checkpoint Backends

The checkpointer contract is backend-agnostic. This notebook drives it
against `S3Backend` — S3 / MinIO / Cloudflare R2 via boto3 — a durable
store with `list_threads`, `vacuum`, branching, and metadata-query
capabilities over a single bucket, so a customer-support case outlives
any one process. (Full-text `search` is not part of the S3 capability
set — a checkpointer built on `OpenSearchBackend` (`opensearch_checkpointer`)
is the only bundled one that reports `capabilities.search`. The SQL
backends offer exact-match lookups
instead: `query_by_metadata` and, on the backend itself, `search_data`,
a JSON-containment match on a top-level state field.) Portable SQL
deployments can use PostgreSQL or MySQL through the same adapter shape;
key/value deployments can use Redis. The basic agent notebook covers the
checkpointer contract itself.

- Save and load a support case's `AgentState` via `S3Backend`.
- Inspect the reported capabilities.
- Walk thread history with `list_threads` / `list_checkpoints`.
- Vacuum old checkpoints with `S3Backend.vacuum`.

Run it (requires an S3-compatible endpoint + a bucket):

    export S3_ENDPOINT_URL=http://localhost:9000   # MinIO / R2 endpoint
    export S3_BUCKET=locus-checkpoints
    export AWS_ACCESS_KEY_ID=minioadmin
    export AWS_SECRET_ACCESS_KEY=minioadmin
    python examples/notebook_52_checkpoint_backends.py

Without the env vars the notebook prints what's missing and exits
cleanly so CI stays green. The in-memory checkpointer covered in
[agent memory](notebook_08_agent_memory.md) is the developer default;
S3 / object storage is a production default. A support case round-trips
through `save` → `load` → `save` across shift handoffs, so multi-day
continuity is just the checkpointer contract in a loop.

## Source

````python
--8<-- "examples/notebook_52_checkpoint_backends.py"
````
