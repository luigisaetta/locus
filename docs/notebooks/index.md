---
title: Examples catalog
---

# Examples

Every example is a runnable `.py` file. Most use the bundled `MockModel` or a
local stub, need no credentials, and print simulated results. Examples that
contact a live provider say so on their page. A mock run demonstrates control
flow; it is not evidence of live-model or vendor behavior.

| Catalog status | Value |
|---|---|
| Tested SDK | `locus-sdk` {{ locus_sdk_version }} |
| Python | 3.11–3.14 |
| Default execution mode | Offline simulation unless the page says **Live** |
| Credentials | None for offline examples; named on live-example pages |
| Source format | Self-contained Python files under `examples/` |

These examples build agents with typed tools, memory, streaming, graphs, RAG,
multi-agent shapes, and the provider and gateway matrix, on everyday work in
payments, customer support, infrastructure, and privacy. Many examples put a
gate you wrote in front of a consequential action: a hook that cancels the tool
call, a graph interrupt that waits for a person, or `admit()` checking a
`ControlPolicy`. The [gate-track examples](#gate-a-high-stakes-action) also
record every decision, allowed or held, on a tamper-evident audit trail.
The tracks below work through those domains; one dedicated track applies that
gate to security operations.

<div class="notebook-filter">
  <input
    type="search"
    id="notebook-filter-input"
    class="notebook-filter__input"
    placeholder="Filter examples (e.g. oracle, oci, rag, hooks)…  press ⌘K"
    autocomplete="off"
    autocorrect="off"
    spellcheck="false" />
</div>

Run any example — each link below opens its file:

```bash
git clone https://github.com/oracle/locus.git
cd locus-sdk
python -m pip install -e .
python examples/<file>.py
```

!!! tip "New to Locus?"
    Start with [Foundations](#foundations) — the agent loop, tools, memory,
    streaming, hooks, and termination. Then pick the domain track that matches
    your work, or go to [Gate a high-stakes action](#gate-a-high-stakes-action)
    for the five-domain gate pattern.

## Oracle Cloud & Database 26ai

Locus is built first-class on **OCI Generative AI** and **Oracle Database
26ai**. These examples run live against your tenancy: pick a transport,
point at a Dedicated AI Cluster, rerank with Cohere on OCI, then put RAG,
durable threads and long-term memory on Oracle Database 26ai — native
`VECTOR(N, FLOAT32)` columns, in-database chunking and embeddings, and a
versioned checkpoint history. **Start here if you ship on Oracle Cloud.**

| Example | What it shows |
|---|---|
| [OCI transports — start here][nb01] | The three OCI transports side by side (V1, Responses, SDK) |
| [OCI v1 chat][nb02] | `OCIChatCompletionsModel` — every OCI model family through `/openai/v1` |
| [OCI Responses][nb03] | `OCIResponsesModel` — opt-in server-stateful path with built-in tools |
| [OCI Dedicated AI Cluster][nb04] | Wiring a private endpoint OCID into the SDK |
| [Cohere reranker on OCI][nb05] | Retrieve-then-rerank with OCI on-demand `rerank-v4.0` |
| [Oracle 26ai RAG][nb41] | `OracleVectorStore` against an Autonomous Database wallet — `VECTOR_DISTANCE` SQL |
| [Oracle ADB document loader][nb42] | `OracleADBLoader` — ingest straight from ADB tables |
| [Oracle in-DB chunker][nb43] | `OracleInDBChunker` — `DBMS_VECTOR_CHAIN.UTL_TO_CHUNKS` inside the database |
| [Oracle in-DB embeddings][nb44] | `OracleInDBEmbeddings` — ONNX embeddings without leaving the database |
| [Oracle 26ai checkpointer][nb53] | `oracle_checkpointer` — resume agent conversations from ADB |
| [Oracle versioned checkpoint saver][nb54] | `OracleCheckpointSaver` — every step preserved, pending writes, time-travel |
| [Oracle store][nb10] | `OracleStore` — the portable `BaseStore` long-term memory path on 26ai |
| [Oracle agent memory][nb88] | `OracleAgentMemoryManager` over Oracle's official `oracleagentmemory` client |
| [OCI tools][nb89] | Agents that drive OCI — `use_oci` / `describe_oci` with read-only guardrails |

## Foundations

The agent loop itself — model, system prompt, tools, memory, streaming, and the
hooks and termination conditions that bound what the loop may do and when it
stops. The examples run on everyday operations — payments triage, a
deployment-readiness check, a support conversation, a GDPR request stream, a
deploy-change gate — but the mechanics are the same whatever the agent does.

| Example | What it shows |
|---|---|
| [Basic agent][nb06] | Model + system prompt; blocking vs streaming run |
| [Agent with tools][nb07] | A deployment-readiness check via `@tool` in a ReAct loop |
| [Conversation memory][nb08] | A conversation saved under a `thread_id` and resumed by a second agent on the same store |
| [A chat loop][nb09] | A REPL where continuity comes from the checkpointer, not your code |
| [Streaming events][nb11] | The typed event stream as the agent runs |
| [SSE streaming][nb13] | Server-sent events for a payments-operations dashboard |
| [Lifecycle hooks][nb12] | Audit + guardrail hooks around every tool call |
| [Hooks — advanced][nb14] | Cancel a destructive call mid-flight — a change gate for a deploy agent |
| [Termination conditions][nb15] | Stop when the ticket is resolved; bound runaway loops |

## Graphs & composition

`StateGraph` and the composition pipelines for multi-step work — conditional
edges that route a cloud alert by severity, reducers that fold parallel payment
checks into one authorization state, an approval interrupt before any
production change, and per-node retries for a flaky provisioning control plane.

| Example | What it shows |
|---|---|
| [Basic graph][nb16] | Nodes, edges, state |
| [Conditional routing][nb17] | Branch on severity; an LLM as the router |
| [State reducers][nb18] | Fold parallel payment checks into one state |
| [Human-in-the-loop][nb19] | Pause for human sign-off before a production change |
| [Command + advanced patterns][nb20] | Dynamic control flow |
| [Composition][nb21] | Sequential / Parallel / Loop pipelines |
| [Graph — advanced][nb22] | Per-node retries and caching; graph diagrams |
| [Functional API][nb23] | `@task` / `@entrypoint` |

## Agent teams

Patterns for more than one agent — a swarm working an outage war room,
L1 → L2 → L3 support escalation with typed handoffs, an orchestrator routing a
data-subject request to specialists, a supervisor/critic loop that grounds a
report before it ships, and a judge that adjudicates an incident-vs-noise
debate.

| Example | What it shows |
|---|---|
| [Swarm][nb24] | Peer-to-peer shared incident context |
| [Agent handoff][nb25] | Sequential L1 → L2 escalation with full transcript |
| [Orchestrator][nb26] | A privacy officer routes a request to parallel specialists |
| [Specialist agents][nb27] | Named domain experts |
| [A2A protocol][nb28] | Cross-process A2A — a payment-risk agent a partner bank can call |
| [DeepAgent][nb29] | Reflexion + grounding + subagents for a fleet reliability review |
| [Map-reduce support triage][nb30] | `Send` fan-out / reduce over support tickets |
| [Supervisor + critic loop][nb31] | Refinement loop that grounds a report before it ships |
| [Adversarial debate + judge][nb32] | Incident vs noise, adjudicated to a typed `Verdict` |
| [Multi-agent + human-in-the-loop][nb33] | Three HITL patterns in one file |
| [Emergent incident routing][nb34] | The model picks the specialist protocol from a fixed set |

## Reasoning & grounding

Typed structured output, Reflexion self-critique, and GSAR grounding —
abstain-by-construction, so no evidence means no claim, never a guessed
conclusion.

| Example | What it shows |
|---|---|
| [Structured output][nb35] | A typed ticket update on `result.parsed` |
| [Reasoning patterns][nb36] | Reflexion, causal chains |
| [GSAR — typed grounding][nb37] | The four-way claim partition + tiered replanning |

## RAG & retrieval

Retrieval as grounding evidence — index a cloud best-practice catalogue, choose
embedding and vector-store providers over a payments runbook, then wire
retrieval into an on-call copilot so its advice cites your runbooks instead of
model memory.

| Example | What it shows |
|---|---|
| [RAG basics][nb38] | Index + retrieve a cloud best-practice catalogue |
| [RAG providers][nb39] | Swappable vector stores and embeddings |
| [RAG agents][nb40] | Retrieval as a tool in an on-call SRE copilot |

## Skills, playbooks & policy

Codify procedure — GDPR data-subject-request playbooks with enforced tool
order, vetted payments-ops skills with progressive disclosure, support-desk
systems wired in over MCP, and LLM-as-policy steering that vetoes a mutating
infra call before it runs.

| Example | What it shows |
|---|---|
| [MCP integration][nb45] | Expose / consume support-desk tools over MCP |
| [Playbooks][nb46] | GDPR request procedures with enforced tool order |
| [Plugins][nb47] | Package and share capabilities |
| [Skills][nb48] | Tool-restricted, multi-step procedures |
| [Steering — LLM-as-policy][nb49] | Veto an unsafe action before it executes |

## Hardening for production

Guardrails over input and output (PII, prompt-injection patterns, tool
allowlists), checkpointers that let a support case survive a restart, and an
evaluation harness that pins agent behaviour as regression tests.

| Example | What it shows |
|---|---|
| [Guardrails & security][nb50] | Injection / PII / allowlist basics |
| [Guardrails — advanced][nb51] | Topic, content, and output-filter policies |
| [Checkpoint backends][nb52] | S3-backed durability; SQL and Redis via the same contract |
| [Evaluation][nb55] | Score a data-access reviewer as regression tests |
| [Model providers][nb56] | The provider matrix |
| [Multi-modal providers][nb57] | Chargeback evidence: web fetch, ledger search, image, transcription |

## Routing & observability

Put every tool call, token, and decision on the EventBus — a replayable ticket
timeline, a telemetry forwarder that spans concurrent rollouts, and an event
catalogue generated from the code.

| Example | What it shows |
|---|---|
| [Cognitive router (PRISM)][nb58] | A typed goal frame picks the protocol; risk decides whether it runs |
| [Observability basics][nb59] | Opt-in EventBus telemetry |
| [Token usage bridge][nb60] | Yield bridge + cost accounting |
| [EventBus subscribers][nb61] | Subscribe shapes; forward rollout telemetry |
| [Event catalogue tour][nb62] | Every canonical event |

## Real-world workflows

End-to-end operations — on-call incident response for an SRE team, risk-tiered
support-concession and vendor-DPA approvals, and voice in / voice out for a
payments support line.

| Example | What it shows |
|---|---|
| [On-call incident response][nb63] | Triage → investigate → mitigate, gated |
| [Support concession approval][nb64] | Risk-tiered approval chain for costly concessions |
| [Vendor DPA & data-privacy review][nb65] | Parse → assess → revise with sign-off |
| [Spoken cloud status advisory][nb66] | Text-to-speech briefing |
| [Payments support voice line][nb67] | Voice in → voice out |

## Serving & gateways

Ship an agent behind FastAPI, run a research pipeline over a support knowledge
base, wire live vendor integrations for privacy work, and route every model
call through a cost-tracked gateway.

| Example | What it shows |
|---|---|
| [Agent server (FastAPI)][nb68] | An on-call triage copilot over SSE, key-scoped threads |
| [Research workflow][nb69] | A support analyst works a known-issue KB end-to-end |
| [Live vendor integrations][nb70] | PII discovery, data map, scan dispatch |
| [LiteLLM gateway][nb71] | Route through a model gateway |
| [LiteLLM gateway — cost tracking][nb72] | Per-team cost tracking and budgets |

## Gate a high-stakes action

One pattern, five domains. The agent proposes an action; `admit()` checks it
against a `ControlPolicy` you wrote; the side effect runs only if the policy
allows it; every decision — allowed or held — lands on a tamper-evident
`AuditTrail`. Fooling the model does not move money, ship to production, or
delete a record, because the gate runs in code before the action, not in the
prompt.

| Example | What it shows |
|---|---|
| [Refund gate (payments)][nb83] | Pay out a small refund automatically; hold a $4,000 reversal for a human |
| [Deploy gate (infrastructure)][nb84] | Ship to staging on the agent's authority; stop every production change for a person |
| [Account-change gate (support)][nb85] | Apply a routine credit; hold a plan upgrade or a large goodwill credit |
| [Data-deletion gate (privacy)][nb86] | Run a GDPR export on the agent's own authority; a DPO signs off before any erasure |
| [Cloud-resource gate (cloud)][nb87] | Resize a dev box on its own; hold terminate-prod-DB and open-IAM for a human |

## Security operations

The most fully worked domain track — point a red-team suite at another AI,
verify a finding before acting on it, gate the containment action by policy,
and investigate across vendors. The same gate as the tracks above, applied to
incident response.

| Example | What it shows |
|---|---|
| [Red-team an AI agent][nb75] | Grounded findings or abstentions across the OWASP-ASI probe suite; findings carry OWASP and MITRE ATLAS tags |
| [Red-team a support chatbot][nb76] | Prompt-injection, jailbreak, and data-leak probes against a live endpoint |
| [Verify findings][nb78] | An independent skeptic refutes a hallucinated "critical" before it drives an action |
| [CI security gate][nb77] | Fail the build when an agent regression ships a vulnerability |
| [SOC alert triage][nb79] | SIEM-grounded verdicts — cite the evidence or abstain |
| [Investigate with SecurityContext][nb82] | One investigation across many vendors, no vendor names in your code |
| [Incident response + audit chain][nb81] | A tamper-evident trail of every decision and action |
| [SOC playbooks][nb74] | NIST 800-61 runbooks over the security toolset |
| [Grounded cloud-posture audit][nb73] | Read-only AWS posture findings that abstain without evidence |
| [Model & hardware fingerprinting][nb80] | Identify a co-tenant's model via timing side-channels |

[nb06]: https://github.com/oracle/locus/blob/main/examples/notebook_06_basic_agent.py
[nb07]: https://github.com/oracle/locus/blob/main/examples/notebook_07_agent_with_tools.py
[nb08]: https://github.com/oracle/locus/blob/main/examples/notebook_08_agent_memory.py
[nb09]: https://github.com/oracle/locus/blob/main/examples/notebook_09_chat_loop.py
[nb11]: https://github.com/oracle/locus/blob/main/examples/notebook_11_agent_streaming.py
[nb12]: https://github.com/oracle/locus/blob/main/examples/notebook_12_agent_hooks.py
[nb13]: https://github.com/oracle/locus/blob/main/examples/notebook_13_sse_streaming.py
[nb14]: https://github.com/oracle/locus/blob/main/examples/notebook_14_hooks_advanced.py
[nb15]: https://github.com/oracle/locus/blob/main/examples/notebook_15_termination.py
[nb16]: https://github.com/oracle/locus/blob/main/examples/notebook_16_basic_graph.py
[nb17]: https://github.com/oracle/locus/blob/main/examples/notebook_17_conditional_routing.py
[nb18]: https://github.com/oracle/locus/blob/main/examples/notebook_18_state_reducers.py
[nb19]: https://github.com/oracle/locus/blob/main/examples/notebook_19_human_in_the_loop.py
[nb20]: https://github.com/oracle/locus/blob/main/examples/notebook_20_advanced_patterns.py
[nb21]: https://github.com/oracle/locus/blob/main/examples/notebook_21_composition.py
[nb22]: https://github.com/oracle/locus/blob/main/examples/notebook_22_graph_advanced.py
[nb23]: https://github.com/oracle/locus/blob/main/examples/notebook_23_functional_api.py
[nb24]: https://github.com/oracle/locus/blob/main/examples/notebook_24_swarm_multiagent.py
[nb25]: https://github.com/oracle/locus/blob/main/examples/notebook_25_agent_handoff.py
[nb26]: https://github.com/oracle/locus/blob/main/examples/notebook_26_orchestrator_pattern.py
[nb27]: https://github.com/oracle/locus/blob/main/examples/notebook_27_specialist_agents.py
[nb28]: https://github.com/oracle/locus/blob/main/examples/notebook_28_a2a_protocol.py
[nb29]: https://github.com/oracle/locus/blob/main/examples/notebook_29_deepagent.py
[nb30]: https://github.com/oracle/locus/blob/main/examples/notebook_30_map_reduce_code_review.py
[nb31]: https://github.com/oracle/locus/blob/main/examples/notebook_31_supervisor_critic_loop.py
[nb32]: https://github.com/oracle/locus/blob/main/examples/notebook_32_debate_with_judge.py
[nb33]: https://github.com/oracle/locus/blob/main/examples/notebook_33_multiagent_human_in_loop.py
[nb34]: https://github.com/oracle/locus/blob/main/examples/notebook_34_emergent_routing.py
[nb35]: https://github.com/oracle/locus/blob/main/examples/notebook_35_structured_output.py
[nb36]: https://github.com/oracle/locus/blob/main/examples/notebook_36_reasoning_patterns.py
[nb37]: https://github.com/oracle/locus/blob/main/examples/notebook_37_gsar_typed_grounding.py
[nb38]: https://github.com/oracle/locus/blob/main/examples/notebook_38_rag_basics.py
[nb39]: https://github.com/oracle/locus/blob/main/examples/notebook_39_rag_providers.py
[nb40]: https://github.com/oracle/locus/blob/main/examples/notebook_40_rag_agents.py
[nb45]: https://github.com/oracle/locus/blob/main/examples/notebook_45_mcp_integration.py
[nb46]: https://github.com/oracle/locus/blob/main/examples/notebook_46_playbooks.py
[nb47]: https://github.com/oracle/locus/blob/main/examples/notebook_47_plugins.py
[nb48]: https://github.com/oracle/locus/blob/main/examples/notebook_48_skills.py
[nb49]: https://github.com/oracle/locus/blob/main/examples/notebook_49_steering.py
[nb50]: https://github.com/oracle/locus/blob/main/examples/notebook_50_guardrails_security.py
[nb51]: https://github.com/oracle/locus/blob/main/examples/notebook_51_guardrails_advanced.py
[nb52]: https://github.com/oracle/locus/blob/main/examples/notebook_52_checkpoint_backends.py
[nb55]: https://github.com/oracle/locus/blob/main/examples/notebook_55_evaluation.py
[nb56]: https://github.com/oracle/locus/blob/main/examples/notebook_56_model_providers.py
[nb57]: https://github.com/oracle/locus/blob/main/examples/notebook_57_multimodal_providers.py
[nb58]: https://github.com/oracle/locus/blob/main/examples/notebook_58_cognitive_router.py
[nb59]: https://github.com/oracle/locus/blob/main/examples/notebook_59_observability_basics.py
[nb60]: https://github.com/oracle/locus/blob/main/examples/notebook_60_agent_yield_bridge.py
[nb61]: https://github.com/oracle/locus/blob/main/examples/notebook_61_eventbus_subscribers.py
[nb62]: https://github.com/oracle/locus/blob/main/examples/notebook_62_event_catalogue.py
[nb63]: https://github.com/oracle/locus/blob/main/examples/notebook_63_incident_response.py
[nb64]: https://github.com/oracle/locus/blob/main/examples/notebook_64_procurement_approval.py
[nb65]: https://github.com/oracle/locus/blob/main/examples/notebook_65_contract_review.py
[nb66]: https://github.com/oracle/locus/blob/main/examples/notebook_66_audio_response.py
[nb67]: https://github.com/oracle/locus/blob/main/examples/notebook_67_audio_chat.py
[nb68]: https://github.com/oracle/locus/blob/main/examples/notebook_68_agent_server.py
[nb69]: https://github.com/oracle/locus/blob/main/examples/notebook_69_research_workflow.py
[nb70]: https://github.com/oracle/locus/blob/main/examples/notebook_70_vendor_integrations.py
[nb71]: https://github.com/oracle/locus/blob/main/examples/notebook_71_litellm_gateway.py
[nb72]: https://github.com/oracle/locus/blob/main/examples/notebook_72_litellm_gateway_cost.py
[nb73]: https://github.com/oracle/locus/blob/main/packages/locus-sdk-security/examples/notebook_73_cloud_posture_agent.py
[nb74]: https://github.com/oracle/locus/blob/main/packages/locus-sdk-security/examples/notebook_74_security_playbooks.py
[nb75]: https://github.com/oracle/locus/blob/main/packages/locus-sdk-security/examples/notebook_75_agent_red_team.py
[nb76]: https://github.com/oracle/locus/blob/main/packages/locus-sdk-security/examples/notebook_76_redteam_support_bot.py
[nb77]: https://github.com/oracle/locus/blob/main/packages/locus-sdk-security/examples/notebook_77_ci_security_gate.py
[nb78]: https://github.com/oracle/locus/blob/main/packages/locus-sdk-security/examples/notebook_78_verify_findings.py
[nb79]: https://github.com/oracle/locus/blob/main/packages/locus-sdk-security/examples/notebook_79_soc_alert_triage.py
[nb80]: https://github.com/oracle/locus/blob/main/packages/locus-sdk-security/examples/notebook_80_model_fingerprint.py
[nb81]: https://github.com/oracle/locus/blob/main/examples/notebook_81_ir_audit_trail.py
[nb82]: https://github.com/oracle/locus/blob/main/packages/locus-sdk-security/examples/notebook_82_investigate_with_ctx.py
[nb83]: https://github.com/oracle/locus/blob/main/examples/notebook_83_payment_refund_gate.py
[nb84]: https://github.com/oracle/locus/blob/main/examples/notebook_84_infra_deploy_gate.py
[nb85]: https://github.com/oracle/locus/blob/main/examples/notebook_85_support_account_gate.py
[nb86]: https://github.com/oracle/locus/blob/main/examples/notebook_86_data_deletion_gate.py
[nb87]: https://github.com/oracle/locus/blob/main/examples/notebook_87_cloud_resource_gate.py
[nb01]: https://github.com/oracle/locus/blob/main/examples/notebook_01_oci_transports.py
[nb02]: https://github.com/oracle/locus/blob/main/examples/notebook_02_oci_openai_chat.py
[nb03]: https://github.com/oracle/locus/blob/main/examples/notebook_03_oci_responses.py
[nb04]: https://github.com/oracle/locus/blob/main/examples/notebook_04_oci_dac.py
[nb05]: https://github.com/oracle/locus/blob/main/examples/notebook_05_cohere_reranker.py
[nb10]: https://github.com/oracle/locus/blob/main/examples/notebook_10_oracle_store.py
[nb41]: https://github.com/oracle/locus/blob/main/examples/notebook_41_oracle_26ai_rag.py
[nb42]: https://github.com/oracle/locus/blob/main/examples/notebook_42_oracle_adb_loader.py
[nb43]: https://github.com/oracle/locus/blob/main/examples/notebook_43_oracle_indb_chunker.py
[nb44]: https://github.com/oracle/locus/blob/main/examples/notebook_44_oracle_indb_embeddings.py
[nb53]: https://github.com/oracle/locus/blob/main/examples/notebook_53_oracle_26ai_checkpointer.py
[nb54]: https://github.com/oracle/locus/blob/main/examples/notebook_54_oracle_versioned_saver.py
[nb88]: https://github.com/oracle/locus/blob/main/examples/notebook_88_oracle_agent_memory.py
[nb89]: https://github.com/oracle/locus/blob/main/examples/notebook_89_oci_tools.py
