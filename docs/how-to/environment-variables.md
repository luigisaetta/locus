# Environment variables

Locus configures itself from environment variables. The notebook harness in
`examples/config.py` reads them with a consistent fallback chain; the SDK
itself reads provider API keys directly.

This page is the answer when an example prints *"skipped — missing env
vars"*.

## Minimum set for a notebook run

```bash
export LOCUS_MODEL_PROVIDER=openai
export LOCUS_MODEL_ID=gpt-4o
export OPENAI_API_KEY=sk-...

python examples/notebook_02_basic_agent.py
```

`LOCUS_MODEL_PROVIDER` is the switch. **Unset, it defaults to `mock`** and
the notebooks run offline against a bundled model — setting only
`LOCUS_MODEL_ID` still gives you the mock.

## Model selection

| Variable | Used by |
|---|---|
| `LOCUS_MODEL_PROVIDER` | `examples/config.py:get_model` — `oci` (auto-detected when `~/.oci/config` has a usable profile), `mock` (default otherwise), `openai`, `anthropic` |
| `LOCUS_MODEL_ID` | Model id for the selected provider (e.g. `gpt-4o`, `claude-sonnet-5-5`) |
| `LOCUS_MODEL_ID_B` | Secondary "model B" slot — comparison notebooks |
| `LOCUS_MODEL_ID_C` | Tertiary "model C" slot |
| `LOCUS_RESEARCH_MODEL` | Overrides the model for the research/eval scripts |
| `LOCUS_NOTEBOOK_BOOT` | Set by the notebook harness during boot; not user-facing |

### OCI Generative AI

Every `LOCUS_OCI_*` variable falls back to its `OCI_*` equivalent (the OCI
CLI convention), so a shell that already has `OCI_PROFILE` exported works
unchanged. See [OCI GenAI models](oci-models.md).

| Variable | Used by |
|---|---|
| `LOCUS_OCI_PROFILE` / `OCI_PROFILE` | `~/.oci/config` profile; when neither is set the notebooks pick `[DEFAULT]` or the only named profile |
| `LOCUS_OCI_AUTH_TYPE` / `OCI_AUTH_TYPE` | `api_key` (default), `security_token`, `instance_principal`, `resource_principal` |
| `LOCUS_OCI_REGION` / `OCI_REGION` | GenAI region, e.g. `us-chicago-1` |
| `LOCUS_OCI_COMPARTMENT` / `OCI_COMPARTMENT` | Compartment OCID; derived from the profile's tenancy when unset |
| `LOCUS_OCI_ENDPOINT` / `OCI_ENDPOINT` | Service endpoint override — SDK transport (`OCIModel`) only |
| `LOCUS_OCI_TRANSPORT` / `OCI_TRANSPORT` | Force `v1` or `sdk` instead of routing by model id |
| `OCI_DAC_ENDPOINT_OCID`, `OCI_DAC_COMPARTMENT_ID`, `OCI_DAC_REGION` | Dedicated AI Cluster — notebook 35 |

## Provider keys

Per-provider setup, with the model string for each, is in
[Configure a model provider](configure-providers.md).

| Variable | Used by |
|---|---|
| `OPENAI_API_KEY` | `OpenAIModel`, `OpenAIEmbeddings` |
| `OPENAI_BASE_URL` | OpenAI-shaped endpoint override — points the notebooks at a proxy or the LiteLLM gateway |
| `ANTHROPIC_API_KEY` | `AnthropicModel` |
| `COHERE_API_KEY` | `CohereEmbeddings`, `CohereReranker` |

### OpenAI-compatible providers

Every prefix in the [compatible-provider table](../concepts/providers/openai-compatible.md)
reads its own key variable — `GROQ_API_KEY`, `TOGETHER_API_KEY`,
`OPENROUTER_API_KEY`, `DEEPSEEK_API_KEY`, `MISTRAL_API_KEY`, `XAI_API_KEY`,
`FIREWORKS_API_KEY`, `CEREBRAS_API_KEY`, `PERPLEXITY_API_KEY`,
`NVIDIA_API_KEY` — and each accepts a `LOCUS_<PREFIX>_BASE_URL` override for
self-hosted deployments and proxies. Local servers (`ollama`, `vllm`,
`lmstudio`, `llamacpp`) need no key.

## Storage backends

| Variable | Used by |
|---|---|
| `REDIS_URL` | Redis checkpointer — notebook 65 |
| `S3_BUCKET` | S3 checkpointer — notebook 50 |
| `ORACLE_DSN` | Oracle Database 26ai — tnsnames alias or `host:port/service` — notebooks 10, 41-44, 53-54, 88 |
| `ORACLE_USER` / `ORACLE_PASSWORD` | Oracle Database 26ai credentials |
| `ORACLE_WALLET` / `ORACLE_WALLET_PASSWORD` | Autonomous Database wallet directory and password (empty string for auto-login wallets) |
| `S3_ENDPOINT_URL` | S3-compatible endpoint (MinIO, R2) — notebook 50 |

## Serving

| Variable | Used by |
|---|---|
| `LOCUS_SERVER_API_KEY` | `AgentServer` bearer token — notebook 65 |
| `LOCUS_A2A_API_KEY` | `A2AServer.__init__` bearer token |

## LiteLLM gateway

Notebooks 71 and 72. See [the gateway how-to](litellm-gateway.md).

| Variable | Used by |
|---|---|
| `LITELLM_GATEWAY_URL` | Gateway base URL |
| `LITELLM_GATEWAY_KEY` | Virtual key the agent presents |
| `LITELLM_GATEWAY_MODEL` | Model id as the gateway names it |
| `LITELLM_MASTER_KEY` | Admin key — `/key/generate` and `/spend/*` (needs Postgres) |

## Cloud and security domain

| Variable | Used by |
|---|---|
| `LOCUS_AWS_PROFILE` | AWS cloud-posture tools — notebook 81 |
| `LOCUS_AWS_REGION` | AWS cloud-posture tools — default `us-east-1` |
| `AWS_ACCESS_KEY_ID` | Standard AWS credential chain |
| `AWS_SECRET_ACCESS_KEY` | Standard AWS credential chain |
| `SCANNER_API_KEY` | Vulnerability-scanner adapter — notebook 80 |
| `DATAMAP_URL` | Data-map adapter — notebook 80 |
| `DATAMAP_API_KEY` | Data-map adapter — notebook 80 |
| `DATAMAP_TOKEN` | Data-map adapter — notebook 80 |

## Model fingerprinting

Notebook 88. See [cloud posture](../concepts/cloud-posture.md).

| Variable | Used by |
|---|---|
| `FINGERPRINT_MODEL` | Model id under test |
| `FINGERPRINT_ASSET` | Asset label recorded on the finding |
| `FINGERPRINT_SAMPLES` | Number of timing samples to collect |

## Other

| Variable | Used by |
|---|---|
| `OPENCLAW_DIR` | OpenClaw workspace root — the red-team example |
