# Azure OpenAI

The Azure provider runs OpenAI's models from an Azure OpenAI resource. Use it
when your organisation buys OpenAI capacity through Azure: quota, networking and
billing live there, and requests must go to your resource, not `api.openai.com`.

Azure serves the same models, but not at the same address and not with the same
auth, which is why it is its own provider rather than a row in the
[OpenAI-compatible table](openai-compatible.md). Three things differ:

- **The URL names a deployment, not a model.** Whoever created the deployment
  chose its name, so `gpt4o-prod` is an ordinary name for `gpt-4o`.
- **Auth is an `api-key` header**, or an Entra ID token, not `Authorization: Bearer`.
- **Every request carries an `api-version`.** Azure has no rolling "latest".

Under the hood this is the [OpenAI provider](openai.md) with Azure's client
behind it, so message conversion, tool calls, streaming and structured output
behave exactly as they do there.

## Getting started

### 1. Point at your resource

```bash
export AZURE_OPENAI_ENDPOINT=https://my-resource.openai.azure.com
export AZURE_OPENAI_API_KEY=...
```

It uses the same `openai` extra as the OpenAI provider; there is no new dependency.

### 2. Address a deployment

```python
from locus.agent import Agent

agent = Agent(model="azure:gpt4o-prod", system_prompt="You answer questions about orders.")
```

`azure:` selects the provider; `gpt4o-prod` is the **deployment name** from
your resource, not the underlying model id.

### 3. Or configure it explicitly

```python
from locus.agent import Agent
from locus.models.native.azure import AzureOpenAIModel

model = AzureOpenAIModel(
    model="gpt4o-prod",
    endpoint="https://my-resource.openai.azure.com",
    api_version="2024-10-21",
)
agent = Agent(model=model)
```

## Configuration

| Setting | Argument | Environment | Default |
|---|---|---|---|
| Deployment name | `model` | — | required |
| Resource endpoint | `endpoint` | `AZURE_OPENAI_ENDPOINT` | required |
| API key | `api_key` | `AZURE_OPENAI_API_KEY` | one of key or token required |
| Entra ID token | `azure_ad_token` | — | used instead of a key |
| API version | `api_version` | `AZURE_OPENAI_API_VERSION` | `2024-10-21` |

An argument wins over the environment. `2024-10-21` is a GA version with tool
calling and streaming; set a newer one when a deployment needs a newer feature.

## Common gotchas

| Symptom | Likely cause |
|---|---|
| `Azure OpenAI needs a resource endpoint` | Neither `endpoint=` nor `AZURE_OPENAI_ENDPOINT` is set. |
| `No credentials for Azure OpenAI` | Neither an API key nor `azure_ad_token` is set. |
| 404 `DeploymentNotFound` | `model` is the model id (`gpt-4o`) instead of the deployment name. |
| A parameter is rejected as unsupported | The deployment needs a newer `api_version`. |

## Source

- [`locus/models/native/azure.py`](https://github.com/oracle/locus/blob/main/src/locus/models/native/azure.py)

## See also

- [OpenAI](openai.md) — the provider this one extends
- [Resilience](resilience.md) — failover classification and credential pools
