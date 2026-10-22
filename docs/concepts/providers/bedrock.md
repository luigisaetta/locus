# Amazon Bedrock

The Bedrock provider runs any model hosted on Amazon Bedrock — Amazon Nova,
Claude, Llama, Mistral and the rest — with the AWS credentials you already have.
Use it when your organisation standardises on AWS and wants model calls to stay
inside its account, region and IAM policy.

Bedrock speaks its own wire protocol, so it cannot ride the
[OpenAI-compatible table](openai-compatible.md). This provider uses Bedrock's
**Converse API** only. Converse is the unified surface AWS added so one request
shape covers every model, including tool use and streaming, so
`bedrock:us.amazon.nova-micro-v1:0` and a Claude model on Bedrock run the same code.

## Getting started

### 1. Install the extra

```bash
pip install "locus-sdk[bedrock]"
```

`boto3` is imported lazily, so nobody who never names a `bedrock:` model pays for it.

### 2. Use your usual AWS credentials

No key argument is invented. The standard boto3 chain applies: environment
variables, the shared credentials file, a named profile, SSO, an instance role,
or IRSA in EKS.

### 3. Address a model

```python
from locus.agent import Agent

agent = Agent(model="bedrock:us.amazon.nova-micro-v1:0", system_prompt="You summarise tickets.")
```

The part after `bedrock:` is the Bedrock model or inference-profile id.

### 4. Or configure it explicitly

```python
from locus.agent import Agent
from locus.models.native.bedrock import BedrockModel

model = BedrockModel(
    model="us.amazon.nova-lite-v1:0",
    region="us-west-2",
    profile="analytics",
    max_tokens=2048,
)
agent = Agent(model=model)
```

## Configuration

| Setting | Argument | Default |
|---|---|---|
| Model or inference-profile id | `model` | `us.amazon.nova-lite-v1:0` |
| Region | `region` | the boto3 session's region |
| Named profile | `profile` | the default credential chain |
| Explicit credentials | `aws_access_key_id`, `aws_secret_access_key`, `aws_session_token` | not set |
| Endpoint override (VPC endpoint, local mock) | `endpoint_url` | not set |
| Bedrock guardrail | `guardrail_id`, `guardrail_version` | not set |
| Retries for throttling and transient 5xx | `max_retries` | `3`, botocore adaptive mode |
| Per-request timeout, seconds | `request_timeout` | `120.0` |
| Output cap / sampling | `max_tokens`, `temperature`, `top_p` | `4096`, `0.7`, `0.9` |

## What differs from other providers

**No native structured output.** Converse has no `response_format`. It could be
emulated by forcing a single tool, but tool-choice support varies by model on
Bedrock, so the provider does not claim it; the agent falls back to prompted
JSON, which every Bedrock model handles.

## Common gotchas

| Symptom | Likely cause |
|---|---|
| `ImportError` naming `locus-sdk[bedrock]` | The `bedrock` extra is not installed. |
| `AccessDeniedException` | The IAM principal lacks `bedrock:InvokeModel` / `bedrock:InvokeModelWithResponseStream`, or model access is not enabled in the Bedrock console. |
| `ValidationException` about the model id | Some models need an inference-profile id (`us.…`) rather than the base model id. |
| `NoRegionError` | No region from `region=`, the profile, or `AWS_REGION`. |

## Source

- [`locus/models/native/bedrock.py`](https://github.com/oracle/locus/blob/main/src/locus/models/native/bedrock.py)

## See also

- [Resilience](resilience.md) — failover classification and credential pools
- [OpenAI-compatible providers](openai-compatible.md)
