# Vendor integrations

The earlier notebooks used inline mock tools to keep the focus on agent
mechanics. Real privacy work calls real systems: a data-classification
feed to score an identifier, a data catalog to pull the records behind a
subject request, a scanning cloud to run a personally identifiable
information (PII) discovery probe over a data store. This notebook works
through three vendor integrations and hands two of them to STEWARD, a
data-subject-request (DSAR) triage agent built as a single `Specialist`.

All three integrations follow one convention: read the vendor credential
from the environment and take the live path when it is set; otherwise
return a deterministic, synthetic sample so the notebooks run offline with
no account. The offline sample uses the return shape the live call is
meant to produce, so the agent code does not change when you replace a
stub with the real vendor call.

In this release `Specialist.execute` is a single model turn: the tool
schemas go to the model, and a tool call it returns is kept on the
result's `state` but is not run (see
[Orchestrator + Specialists](../concepts/multi-agent/orchestrator.md)).
STEWARD's result therefore carries the model's reply and a heuristic
confidence score rather than tool-backed evidence.

What this notebook covers:

- `scan_for_pii` — identifier classification against a data-classification
  API (`DATAMAP_API_KEY`).
- `query_data_map` — data-catalog search for the records that hold a
  subject's data (`DATAMAP_URL` + `DATAMAP_TOKEN`).
- `scan_dataset_reference` — PII-discovery scan over a named data store
  (`SCANNER_API_KEY`); the live version is meant to send the scan to a
  classification cloud and return the same category map.

## Prerequisites

- [Agent with tools](notebook_03_agent_with_tools.md).
- [Specialist agents](notebook_23_specialist_agents.md) — the `Specialist`
  deep-dive; the STEWARD triage agent here is built on the same class. In
  [the orchestrator pattern](notebook_22_orchestrator_pattern.md) STEWARD
  is the privacy officer that routes work to specialists; here the name
  belongs to a single specialist.

## Key lines

`scan_for_pii` carries the convention every integration follows: when
`DATAMAP_API_KEY` is set it takes the live path (here a stub awaiting the
vendor call); otherwise it returns a deterministic sample in the live
call's return shape:

{{ locus_source examples/notebook_80_vendor_integrations.py::scan_for_pii }}

`query_data_map` returns the catalog records behind a subject, each with
the system that holds it and a sensitivity grade — the evidence STEWARD's
system prompt tells it to cite for a handling priority:

{{ locus_source examples/notebook_80_vendor_integrations.py::query_data_map }}

A thin `@tool` wrapper hands an integration to the agent; its docstring
becomes the description in the schema the model reads when deciding
whether to call it:

{{ locus_source examples/notebook_80_vendor_integrations.py::scan_for_pii_tool }}

## Run it

```bash
python examples/notebook_80_vendor_integrations.py
```

Model choice comes from `examples/config.py`: OCI Generative AI when
`~/.oci/config` has a usable profile, otherwise the bundled mock model, so the
example also runs offline with no credentials. Set `LOCUS_MODEL_PROVIDER`
(`oci`, `openai`, `anthropic` or `mock`) to force one.

Every vendor tool falls back to its offline sample, so the script runs end to
end without a vendor account. Set `DATAMAP_API_KEY`, `DATAMAP_URL` together
with `DATAMAP_TOKEN`, or `SCANNER_API_KEY` to move the matching tool onto its
live path; in this notebook each live path is a stub that raises
`NotImplementedError` until you add the vendor call.

Offline, the mock answers the tool-bearing request with a synthesized tool
call and no text, and `Specialist.execute` is single-turn, so Part 2 prints
no `disposition:` line; the estimator finds no hedging or certainty markers
in the empty reply, so the confidence sits at its 50% baseline.

## Output

Running it offline — no credentials, bundled mock model — prints the offline sample each integration returns: the risk verdict for three identifiers, the two catalog records that hold the subject's data with their sensitivity, and the four PII categories a scan of `crm.customers` finds, then the STEWARD triage result:

```text
============================================================
Notebook 80: Live vendor integrations
============================================================

Model Provider: mock
Using mock model (no API calls)

=== Part 1: Vendor Tools (offline sample path) ===

PII classification:
  9f86d081884c7d659a2feaa0 -> high-risk (sensitive=True)
  jane.doe@example.com     -> high-risk (sensitive=True)
  unsubscribed@example.net -> minimal (sensitive=False)

Data-map query ('jane.doe@example.com', scope=all):
  2 record(s) from data-catalog (sample)
    [high] crm.customers: row matches 'jane.doe@example.com': email, billing_address retained 5y
    [medium] marketing.events: row matches 'jane.doe@example.com': open/click events, no consent flag set

PII-discovery scan dispatch (offline sample path):
  categories (4/6 found): {'email': '1 column (customers.email)', 'phone': '1 column (customers.phone)', 'payment_card': '1 column (billing.card_last4)', 'location': '2 columns (customers.city, customers.country)'}

=== Part 2: A DSAR triage agent with vendor tools ===

Specialist: STEWARD  tools=['scan_for_pii_tool', 'query_data_map_tool']
  success=True  confidence=50%

============================================================
Each vendor tool reads its credential from the environment — set
the matching credential to route it to the live stub you fill in.
============================================================
```
<!-- notebook-output:end -->

## Source

??? note "Full source — `examples/notebook_80_vendor_integrations.py`"

    ````python
    --8<-- "examples/notebook_80_vendor_integrations.py"
    ````
