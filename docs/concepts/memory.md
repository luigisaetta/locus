---
title: Memory — short-term and long-term
description: "The three memories of a Locus agent — working memory, thread memory and long-term memory — plus knowledge retrieval, and how Oracle Database 26ai backs each of them."
---

# Memory: short-term and long-term

An agent remembers at three different time scales, and Locus keeps them as
three separate surfaces so you can choose a backend for each. Oracle
Database 26ai can back all of them, in the same database as the business
data the agent acts on.

| Layer | What it holds | Lifetime | Locus surface | Oracle Database 26ai |
|---|---|---|---|---|
| **Working memory** | The messages of the current run: prompt, tool calls, observations | One run | `Agent(conversation_manager=…)`: `SlidingWindowManager`, `SummarizingManager`, `ContextCompactor` | In-process, nothing to persist |
| **Short-term memory** (the thread) | The full state of one conversation: messages, tool results, iteration, so a thread can resume in another process or after a crash | The thread | `Agent(checkpointer=…)` and `thread_id=` on every call | `oracle_checkpointer()` for durable threads; `OracleCheckpointSaver` keeps every version for history and resume-from-any-point |
| **Long-term memory** | Facts that outlive any thread: preferences, standing rules, what was learned handling earlier cases | Until you delete it | `Agent(memory_manager=…)`: `LLMMemoryManager(store=…)` or `OracleAgentMemoryManager` | `OracleStore` as the store; `OracleAgentMemoryManager` over Oracle's `oracleagentmemory` client |
| **Knowledge** (RAG) | Documents the agent retrieves rather than remembers | Your corpus | `RAGRetriever(...).as_tool()` | `OracleVectorStore`, `OracleInDBChunker`, `OracleInDBEmbeddings`, `OracleADBLoader` |

## Working memory

Working memory is the context window. It is not stored anywhere; the
question is what to drop when a long run no longer fits. A
`ConversationManager` decides: `SlidingWindowManager` keeps the last *n*
messages, `SummarizingManager` folds older turns into a summary, and
`ContextCompactor` archives tool output and replaces it with a reference.
See [the agent loop](agent-loop.md) for where it runs.

```python
from locus.agent import Agent
from locus.memory.conversation import SlidingWindowManager

agent = Agent(model="oci:openai.gpt-5.5", conversation_manager=SlidingWindowManager(window_size=20))
```

## Short-term memory: the thread

A checkpointer saves the agent's state under a `thread_id` and loads it back
on the next call, from any process. That is what makes a conversation
survive a restart, a deploy, or a hand-off to the next shift.

```python
import os

from locus.agent import Agent
from locus.memory.backends import oracle_checkpointer

cp = oracle_checkpointer(
    dsn=os.environ["ORACLE_DSN"],
    user=os.environ["ORACLE_USER"],
    password=os.environ["ORACLE_PASSWORD"],
    wallet_location=os.environ["ORACLE_WALLET"],
    wallet_password=os.environ.get("ORACLE_WALLET_PASSWORD", ""),
    table_name="support_threads",
)
agent = Agent(model="oci:openai.gpt-5.5", checkpointer=cp)
agent.run_sync("My name is Alice.", thread_id="case-100")
agent.run_sync("What is my name?", thread_id="case-100")  # another process, same thread
```

`oracle_checkpointer()` keeps the latest state of each thread.
`OracleCheckpointSaver` keeps every version, so you can list a thread's
history and resume from any earlier checkpoint. Ten backends ship in total;
[Checkpointers](checkpointers.md) compares them.

## Long-term memory

Long-term memory is what the agent keeps *across* threads: Alice's
preferences should be known in her next case, not only in this one. A
`MemoryManager` runs two hooks around every run: before the first model
call it retrieves relevant memories into the system prompt; after the run
it extracts durable facts and persists them.

```python
import os

from locus.agent import Agent
from locus.memory import LLMMemoryManager
from locus.memory.store_backends import OracleStore

store = OracleStore(
    dsn=os.environ["ORACLE_DSN"],
    user=os.environ["ORACLE_USER"],
    password=os.environ["ORACLE_PASSWORD"],
    wallet_location=os.environ["ORACLE_WALLET"],
    wallet_password=os.environ.get("ORACLE_WALLET_PASSWORD", ""),
)
agent = Agent(model="oci:openai.gpt-5.5", memory_manager=LLMMemoryManager(store=store))

agent.run_sync("I'm Alice. I always want quotes in EUR, never in USD.", thread_id="case-100")
agent.run_sync("Which currency do I want my quotes in?", thread_id="case-200")  # new thread: EUR
```

Two managers ship. `LLMMemoryManager` works over any `BaseStore`, with
Oracle Database 26ai through `OracleStore`, and lets you scope memories per
user or tenant; out of the box it extracts with a small heuristic (standing
rules such as "always … never …", who the user is, project context, links),
and you pass `extract_fn` to let a model decide what is worth keeping. `OracleAgentMemoryManager` wraps Oracle's own agent-memory
client (`oracleagentmemory`): extraction, context-card summaries and
retrieval scoped by user, agent and thread, all inside the database.
[Long-term memory manager](memory-manager.md) covers both.

## Knowledge is not memory

What the agent should *look up* belongs in retrieval, not in memory: policy
pages, runbooks, past resolutions. [RAG](rag.md) covers embedders, vector
stores and `retriever.as_tool()`; on Oracle Database 26ai the whole pipeline
can run inside the database.

## All three on Oracle Database 26ai

One database holds the threads, the long-term memories and the vectors, and
sits next to the tables the agent reads and writes through its tools.
[Oracle Database 26ai](oracle-26ai.md) lists every primitive;
notebooks 37 to 44 run each one.
