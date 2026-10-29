# Checkpoint backends

A customer-support case runs for days and survives restarts, shift
handoffs and redeploys only if its conversation state lives outside any
one process. This notebook drives the checkpointer contract by hand
against `S3Backend`, which keeps every checkpoint as objects under one
bucket prefix: here OCI Object Storage through its S3-compatible API,
and with the same code S3, MinIO or Cloudflare R2, all via boto3.
(`OCIBucketBackend` keeps the same object layout and reports the same
capabilities over the OCI Python SDK; it signs with an OCI configuration
profile, a session token or an instance or resource principal instead of
the Customer Secret Key pair the S3-compatible API uses.) The
[conversation memory](notebook_05_agent_memory.md) notebook covers the
checkpointer contract itself.

The in-memory checkpointer covered there is the developer default;
object storage is the
[production default](../concepts/checkpointers.md#picking-a-backend). A
support case round-trips through `save` → `load` → `save` across shift
handoffs, so multi-day continuity is the checkpointer contract applied
in a loop.

`S3Backend` reports `metadata_query`, `vacuum`, `branching`,
`list_threads`, `list_with_metadata` and `persistent_checkpoint_ids`,
with `search` and `ttl` false. One caveat on `metadata_query`:
`S3Backend` implements only `get_metadata`; `query_by_metadata` falls
through to `BaseCheckpointer`, which raises `NotImplementedError` even
though the descriptor advertises the capability.

What this notebook covers:

- Save and load a support case's `AgentState` via `S3Backend`.
- Inspect the reported capabilities.
- Walk thread history with `list_threads` / `list_checkpoints`.
- Vacuum old checkpoints with `S3Backend.vacuum`.
- Branch on the capability descriptor before calling `search`.

## Prerequisites

- The `s3` extra (`pip install "locus-sdk[s3]"`): boto3 is not a core
  dependency and `S3Backend` imports it lazily, so without it the
  missing-variable path below still exits cleanly, but the first call
  that needs a client, here the first `save`, raises `ImportError`.
- An S3-compatible bucket named in `S3_BUCKET`, a key pair in
  `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`, and `S3_ENDPOINT_URL`
  for any endpoint other than S3 itself. The notebook checks the three
  required variables before it builds the backend, prints the missing
  names and exits.

`S3Backend` is the first of the two checkpointer shapes in the drawing:
it subclasses `BaseCheckpointer` and is passed to an agent unchanged,
as are `OCIBucketBackend` and the native `PgCheckpointer`. Redis,
PostgreSQL, MySQL, OpenSearch and Oracle Database are the second shape,
dict-shaped storage behind `StorageBackendAdapter`; each
`*_checkpointer()` factory does the wrapping, and the adapter derives
its capability descriptor from the methods the storage class defines.

Object storage has no index, so `S3Backend` does not report `search`
and the notebook branches on the descriptor rather than calling and
catching. `opensearch_checkpointer()` and `oracle_checkpointer()` do
report `capabilities.search`: `OpenSearchBackend.search` runs a
`multi_match` query over the indexed checkpoint JSON and
`OracleBackend.search` a case-insensitive `LIKE` over the JSON column.
PostgreSQL and MySQL offer exact matches instead: `query_by_metadata`
through the checkpointer, and `search_data`, a JSON-containment match
on one top-level state field, on the backend object only, so their
adapters report `search` as false.

The notebook calls `save`, `load` and `list_checkpoints` by hand, the
same contract the agent loop exercises at the save points shown:

{{ locus_diagram checkpointer-shapes }}

## Key lines

One `S3Backend` over a bucket and a key prefix is the whole
checkpointer. `endpoint_url` points it at an OCI Object Storage
S3-compatibility endpoint or a local MinIO and is left unset for S3
itself; no key pair is passed, so boto3 resolves credentials from its
default chain, which is where `AWS_ACCESS_KEY_ID` and
`AWS_SECRET_ACCESS_KEY` are read:

{{ locus_source examples/notebook_50_checkpoint_backends.py::_make_backend }}

## Run it

```bash
# OCI Object Storage through its S3-compatible API; the credentials are
# an OCI Customer Secret Key pair created for your user.
export S3_ENDPOINT_URL=https://<namespace>.compat.objectstorage.<region>.oraclecloud.com
export S3_BUCKET=locus-checkpoints
export AWS_ACCESS_KEY_ID=<customer-secret-key-id>
export AWS_SECRET_ACCESS_KEY=<customer-secret-key>
python examples/notebook_50_checkpoint_backends.py
```

The script uses no model. It needs an S3-compatible bucket: `S3_BUCKET`
names it, `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` sign the
requests, and `S3_ENDPOINT_URL` selects any endpoint other than S3
itself. Without the three required variables it prints their names and
exits cleanly, before any client is created, so it makes no network
call.

Any other S3-compatible endpoint works the same way, for example a
local MinIO:

```bash
export S3_ENDPOINT_URL=http://localhost:9000
export S3_BUCKET=locus-checkpoints
export AWS_ACCESS_KEY_ID=minioadmin
export AWS_SECRET_ACCESS_KEY=minioadmin
python examples/notebook_50_checkpoint_backends.py
```

## See also

- [Conversation memory](notebook_05_agent_memory.md) — the checkpointer
  contract on `MemoryCheckpointer`.
- [Oracle 26ai checkpointer](notebook_42_oracle_26ai_checkpointer.md) —
  the second shape, `oracle_checkpointer()`, driven by the agent loop.
- [Agent server](notebook_65_agent_server.md) — `RedisBackend` behind
  `StorageBackendAdapter` under an HTTP API.
- [Checkpointers](../concepts/checkpointers.md) — picking a backend, the
  two shapes and the capability descriptor.
- [How-to: persist conversations](../how-to/persist-conversations.md) —
  `OCIBucketBackend` and the other native checkpointers.

## Source

??? note "Full source — `examples/notebook_50_checkpoint_backends.py`"

    ````python
    --8<-- "examples/notebook_50_checkpoint_backends.py"
    ````
