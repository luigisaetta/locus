---
title: Build it with Codex
description: Hand OpenAI Codex the prompt in the repository's codex/ directory and it installs Locus, writes a first agent with a typed tool, gates a payment behind admit(), runs the rogue-agent challenge, and reports.
---

# Build it with Codex

[OpenAI Codex](https://developers.openai.com/codex) can do the
[Quickstart](quickstart.md) and the
[first controlled action](first-controlled-action.md) for you. The
repository's [`codex/`](https://github.com/oracle/locus/tree/HEAD/codex)
directory holds a specification and the prompt that drives Codex through it:
install Locus in a fresh environment, write a first agent with a typed tool,
put an admission gate in front of a payment, run the rogue-agent challenge,
and report. The specification is written to be read by a person as well, so
every step has a checkpoint you can follow by hand.

## Requirements

<dl class="locus-facts" markdown="block">
<div markdown="block"><dt>Codex</dt><dd>The Codex CLI, signed in</dd></div>
<div markdown="block"><dt>Python</dt><dd>3.11–3.14</dd></div>
<div markdown="block"><dt>Provider</dt><dd>OCI Generative AI, OpenAI, Anthropic, or none</dd></div>
<div markdown="block"><dt>Credential</dt><dd>An OCI profile, a key in the environment, or none</dd></div>
<div markdown="block"><dt>Execution mode</dt><dd>One live model call; the rest offline</dd></div>
</dl>

## Run it

```bash
git clone https://github.com/oracle/locus.git
cd locus
codex -s workspace-write -c sandbox_workspace_write.network_access=true "$(cat codex/PROMPT.md)"
```

Codex then:

1. runs the preflight of the specification and shows you the table: Python,
   the clone, write access, the network, and the provider's prerequisite;
2. confirms the provider: OCI Generative AI when `~/.oci/config` exists,
   otherwise OpenAI or Anthropic from the key in the environment, otherwise
   offline; and asks, in one message, for anything it could not detect, such
   as which OCI profile to use;
3. creates `.venv`, installs Locus from the clone with the provider's extra,
   and writes `first_agent.py` and `controlled_refund.py` under
   `out/first-agent/`, the files from the two guides above;
4. runs the first agent (one live call), the controlled action and the
   rogue-agent challenge, checking each against the output the specification
   expects;
5. ends with a report: provider, versions, the three results, and where the
   files are.

If a check fails that only you can fix, such as an expired OCI session, Codex
tells you what to run in your own terminal and waits for `done`.

## What Codex loads

| File | Role |
|---|---|
| `AGENTS.md` | Loaded automatically from the repository root: the credential rule, what the agent may write, where things are |
| `codex/SPEC.md` | The specification: inputs, preflight, every step with its checkpoint, acceptance, known behaviour, the report |
| `codex/PROMPT.md` | The prompt: read the two files above, run the steps, report |

## Credentials

On OCI no secret enters the environment. Locus reads the profile you name
from `~/.oci/config`, the OCI SDK signs each request with the key file that
profile points to, and the agent is told to list the file's section names and
read nothing else from it. For OpenAI or Anthropic, export the key in the
shell that starts Codex: Codex passes its environment to the commands it
runs, which is how `first_agent.py` finds `OPENAI_API_KEY`, and the
specification forbids any command whose output would show it.

## The Codex sandbox

`-s workspace-write` lets Codex write inside the clone, which is where
`.venv` and `out/` go, and nowhere else.
`-c sandbox_workspace_write.network_access=true` lets `pip` reach PyPI and
the first agent reach the model; without it the sandbox has no network. To
make the network setting permanent:

```toml
# ~/.codex/config.toml
[sandbox_workspace_write]
network_access = true
```

`codex exec` starts read-only, so the same two flags apply there too.

## Without a conversation

Put your answers in an operator-context block and pipe both into a
non-interactive session:

```bash
cat > operator-context.md <<'EOT'
Operator context. PROVIDER=oci, OCI_PROFILE=DEFAULT, OCI_REGION=us-chicago-1.
Use the default model. If a check fails, report it and stop.
EOT
{ cat operator-context.md; echo; cat codex/PROMPT.md; } | codex exec \
  -s workspace-write -c sandbox_workspace_write.network_access=true -
```

`PROVIDER=offline` runs the controlled action and the rogue-agent challenge
with no credential and skips the live call. A non-interactive session cannot
answer approval requests, so the run has to fit inside the sandbox; the flags
above are enough for every command the specification issues.

## In your own project

Outside a clone, Locus is a package (`pip install "locus-sdk[oci]"`) and Codex
needs to know where the documentation is and what the house rules are. Add to
your project's `AGENTS.md`:

```markdown
## Locus

- Documentation: https://locusagents.ai/llms.txt lists every page;
  https://locusagents.ai/llms-full.txt holds the guides in one file. Read the
  page for an API before using it.
- Models are `oci:<model id>` with `OCI_PROFILE`, `OCI_REGION` and, when
  needed, `OCI_COMPARTMENT_ID` in the environment; `openai:` and `anthropic:`
  ids read `OPENAI_API_KEY` and `ANTHROPIC_API_KEY`.
- Every tool with a side effect runs through `gate_tool()` or `admit()` from
  `locus.control` with a `ControlPolicy`; keep an `AuditTrail` and assert
  `trail.verify()` in tests.
- Never print or store a credential.
```

## What the agent never does

It never sees or shows a credential, never modifies anything git tracks in
the clone, installs nothing outside `.venv`, fetches nothing from the web
(the specification is self-contained; `pip` and the model call are the only
network traffic), and makes one live model call, the first agent's, with at
most one retry.

## Next steps

- [Configure a model provider](configure-providers.md): the ids and the
  environment for every provider.
- [First controlled action](first-controlled-action.md): what the gate
  proves and what it does not.
- [Control-layer architecture](../concepts/control-layer.md): the
  enforcement boundary.
