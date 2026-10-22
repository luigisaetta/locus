# Add a checkpointer backend

`BaseCheckpointer` is the contract. Subclass it, implement three
methods — `save`, `load`, `list_checkpoints` — and override the
`capabilities` property to advertise what your storage actually
supports (every flag defaults to `False`). `delete` and `exists`
ship defaults: `exists` works out of the box on top of your
`load` / `list_checkpoints`, while `delete` raises
`NotImplementedError` until you override it. No adapter layer —
you pass your instance directly to `Agent`.

## Minimal implementation

```python
from typing import Any
from uuid import uuid4

from locus.memory.checkpointer import BaseCheckpointer
from locus.core.protocols import CheckpointerCapabilities
from locus.core.state import AgentState

# from your_storage import connect  ← replace with your actual import


class MyCustomBackend(BaseCheckpointer):
    """Stores checkpoints in <your-storage-here>."""

    def __init__(self, conn_string: str) -> None:
        self._conn = connect(conn_string)

    @property
    def capabilities(self) -> CheckpointerCapabilities:
        return CheckpointerCapabilities(
            list_threads=True,
            persistent_checkpoint_ids=True,
        )

    async def save(
        self,
        state: AgentState,
        thread_id: str,
        checkpoint_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        cp_id = checkpoint_id or uuid4().hex
        payload = state.to_checkpoint()
        await self._conn.put(f"{thread_id}/{cp_id}", payload)
        await self._conn.put(f"{thread_id}/latest", cp_id)
        return cp_id

    async def load(
        self,
        thread_id: str,
        checkpoint_id: str | None = None,
    ) -> AgentState | None:
        cp_id = checkpoint_id or await self._conn.get(f"{thread_id}/latest")
        if cp_id is None:
            return None
        data = await self._conn.get(f"{thread_id}/{cp_id}")
        if data is None:
            return None
        return AgentState.from_checkpoint(data)

    async def list_checkpoints(self, thread_id: str, limit: int = 10) -> list[str]:
        return await self._conn.list_keys(f"{thread_id}/", limit=limit)
```

## Plug it in

```python
agent = Agent(
    ...,
    checkpointer=MyCustomBackend("my://connection"),
)
```

## Advertise capabilities honestly

If your storage supports full-text search, flip `search=True` and
implement `search()`. Same for `branching` (→ `copy_thread`), `vacuum`,
`metadata_query`, `ttl`, `list_with_metadata`.

Consumers inspect `checkpointer.capabilities` before calling optional
methods:

```python
if checkpointer.capabilities.search:
    hits = await checkpointer.search("error handling")
```

## Test the contract

Model your suite on `tests/integration/test_checkpoint_backends.py` —
`TestBackendCompatibility` checks the save/load round-trip every backend
must satisfy, and the per-backend classes (`TestMemoryCheckpointer`,
`TestRedisBackend`, `TestPostgreSQLBackend`, `TestMySQLBackend`,
`TestOpenSearchBackend`) show how to exercise list, delete, and
capabilities against a live store. Adapt the fixtures to your backend's
connection config and you have a complete test suite.
