---
title: First agent — install and run Locus in five minutes
description: Install Locus, run one complete Python agent, and verify the result before adding tools or policy controls.
---

# First agent

This path does one thing: install Locus and run a complete agent. It uses
OpenAI consistently and ends after the first successful response. The next
guide adds a policy-controlled action.

## Requirements

| Requirement | Tested here |
|---|---|
| Python | 3.11–3.14 |
| Locus | Build-tested SDK {{ locus_sdk_version }} |
| Provider | OpenAI by default; OpenRouter and Together.ai alternatives below |
| Credential | Provider-specific API key |
| Execution mode | Live model call |

For a credential-free run, skip to [try Locus offline](#try-locus-offline).

!!! tip "Using OpenRouter or Together.ai?"
    The same installation works. Set `OPENROUTER_API_KEY` and use
    `model="openrouter:provider/model-id"`, or set `TOGETHER_API_KEY` and use
    `model="together:organization/model-id"`. The suffix must match the exact
    id in the provider's catalog. See [OpenAI-compatible providers](../concepts/providers/openai-compatible.md#openrouter-and-togetherai).

## 1. Create an environment

=== "macOS / Linux"

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install "locus-sdk[openai]"
    export OPENAI_API_KEY="your-key"
    ```

    On Oracle Cloud, install the `oci` extra instead and point at an OCI
    config profile — `python -m pip install "locus-sdk[oci]"`, then use
    `oci:` model ids. See [OCI GenAI models](oci-models.md).

=== "Windows PowerShell"

    ```powershell
    py -3.11 -m venv .venv
    .venv\Scripts\Activate.ps1
    python -m pip install "locus-sdk[openai]"
    $env:OPENAI_API_KEY = "your-key"
    ```

## 2. Save one complete file

Create `first_agent.py`:

```python
from locus import Agent, tool


@tool
def lookup_order(order_id: str) -> dict:
    """Return the current status of an order."""
    return {
        "order_id": order_id,
        "status": "delivered",
        "amount_usd": 42.50,
    }


agent = Agent(
    model="openai:gpt-4o-mini",
    tools=[lookup_order],
    system_prompt="Answer support questions using the order lookup.",
)

result = agent.run_sync("What happened to order ORD-7842?")
print(result.message)
```

## 3. Run it

```bash
python first_agent.py
```

The wording varies because this is a live model call. A successful result
should mention order `ORD-7842`, its `delivered` status, and usually the
`$42.50` amount returned by the tool.

You now have one complete success: the model chose a typed Python tool, Locus
executed it, and `AgentResult.message` returned the final answer.

## Try Locus offline

The repository examples use deterministic test doubles and local stubs. Their
printed results are simulations of control flow, not evidence of live-model
quality or vendor behavior.

```bash
git clone https://github.com/oracle/locus.git
cd locus-sdk
python -m pip install -e .
python examples/notebook_83_payment_refund_gate.py
```

That example needs no API key and demonstrates a local payment stub behind an
admission policy.

## Troubleshooting

| Problem | Check |
|---|---|
| `python` is older than 3.11 | Run `python --version`; create the environment with a newer interpreter |
| `ModuleNotFoundError: locus` | Activate the same virtual environment where you installed the package |
| Provider authentication error | Confirm `OPENAI_API_KEY` exists in the shell running the script |
| Model not available to the account | Replace `gpt-4o-mini` with an OpenAI model your account can use |
| Output does not exactly match this page | Expected: live model wording is nondeterministic; check the returned facts instead |

## Continue

[Put a policy gate around an action →](first-controlled-action.md){ .md-button .md-button--primary }

After that, explore [streaming](../concepts/streaming.md),
[persistence](persist-conversations.md), [multi-agent patterns](../concepts/multi-agent.md),
or [deployment](deploy.md) as separate topics.
