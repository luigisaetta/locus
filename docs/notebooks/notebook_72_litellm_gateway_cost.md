# LiteLLM AI Gateway — per-team cost tracking

Companion to the [LiteLLM AI Gateway notebook](notebook_71_litellm_gateway.md) for the
enterprise piece: **who spent what on which model**.

Issues virtual keys for two pretend payments teams, drives traffic on each,
then walks the gateway's full spend surface:

- `/spend/logs` — per-request rows (model, tokens, USD cost, team metadata)
- `/global/spend/keys` — aggregate per virtual key
- `/global/spend/models` — aggregate per upstream model

All three endpoints are SQL-backed (Postgres sidecar from the sample
`docker-compose.yml`) and require zero Locus integration glue —
the gateway is the source of truth.

## What enterprises use this for

- **Charge-back / showback to business units.** Finance pulls a monthly
  report; the fraud-ops and dispute-ops teams see what they cost.
- **"What did Cohere Command cost across all teams this week?"** Drill
  per upstream model.
- **"Who's about to blow their budget?"** Aggregate-per-key view +
  `max_budget` field. A runaway fraud-scoring loop hits its $5 cap, not
  your invoice.
- **Audit.** Append-only spend log keyed by virtual key + metadata,
  one place for PCI-DSS / SOC-2 review.

See the [LiteLLM AI Gateway how-to](../how-to/litellm-gateway.md#cost-tracking)
for the curl-level API and the [enterprise patterns
section](../how-to/litellm-gateway.md#how-enterprises-use-this-pattern)
for the deployment shape.

## Prerequisites

The Postgres-backed gateway from
[`examples/litellm-gateway/`](https://github.com/oracle/locus/tree/main/examples/litellm-gateway).
The stateless gateway from the LiteLLM AI Gateway notebook won't work for this notebook —
`/key/generate` and `/spend/*` both require Postgres.

```bash
cd examples/litellm-gateway/
export LITELLM_MASTER_KEY="sk-master-$(openssl rand -hex 16)"
export LITELLM_DB_PASSWORD="$(openssl rand -hex 16)"
docker compose up -d

export LITELLM_GATEWAY_URL="http://localhost:4000"
export LITELLM_MASTER_KEY="$LITELLM_MASTER_KEY"
python examples/notebook_72_litellm_gateway_cost.py
```

## See also

- [LiteLLM AI Gateway](notebook_71_litellm_gateway.md) —
  the gateway happy path Locus consumers see.
- [LiteLLM AI Gateway how-to](../how-to/litellm-gateway.md) — when to
  use the gateway, auth boundary, scope, and the enterprise patterns
  the cost surface unlocks.

## Source

````python
--8<-- "examples/notebook_72_litellm_gateway_cost.py"
````
