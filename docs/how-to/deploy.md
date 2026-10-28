# Deploy

`AgentServer` is a FastAPI wrapper that deploys anywhere FastAPI runs. The
runnable path below uses OpenAI consistently from application code through the
container and Kubernetes configuration.

| Field | Value |
|---|---|
| Status | Supported server API; deployment manifests are starting points |
| Tested SDK | `locus-sdk` {{ locus_sdk_version }} |
| Execution mode | Live model provider |
| Requirements | Python 3.11+, `locus-sdk[openai,server]` |
| Secrets | `OPENAI_API_KEY` for the provider; `LOCUS_SERVER_API_KEY` for callers |

Those two credentials serve different trust boundaries. The OpenAI key lets
the application call its model provider. The Locus server key is the bearer
token clients send to `/invoke`, `/stream`, and thread routes.

## The shape you ship

{{ locus_model_tabs }}

```python
# server.py
import os

from locus.agent import Agent
from locus.server import AgentServer

agent = Agent(
    model="{{ locus_model }}",
    tools=[],
    system_prompt="Answer concisely.",
)

server = AgentServer(
    agent=agent,
    title="Booking concierge",
    api_key=os.environ["LOCUS_SERVER_API_KEY"],
)

# Module-level ASGI app, so a process manager can serve it directly:
#   uvicorn server:app
app = server.app

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
```

You get out of the box:

- `POST /invoke` — synchronous run, returns the final `message` plus
  run metrics (`success`, `stop_reason`, `iterations`, `tool_calls`,
  `duration_ms`) as JSON.
- `POST /stream` — Server-Sent Events of every typed event.
- `GET / DELETE /threads/{id}` — conversation persistence.
- `GET /health` — liveness probe.

Provider keys are read from the environment. Inject both secrets at runtime;
never bake either into the image. Add a durable checkpointer before relying on
thread continuity across restarts or replicas.

Serving `app` with uvicorn, as the container and VM examples below do, skips
`AgentServer.run()` and with it the check that refuses a non-loopback host
when no key is configured. A `server.app` built without a key only logs a
warning, then serves every route without authentication. Keep `api_key` or
`LOCUS_SERVER_API_KEY` set to a non-empty value: the `os.environ[...]` lookup
above fails at import when the variable is missing, but an empty value turns
authentication off.

## Container — the universal target

The locus-sdk repo ships a multi-stage [`Dockerfile`](https://github.com/oracle/locus/blob/main/Dockerfile)
(non-root user, `HEALTHCHECK` on `/health`). It is the library base image:
built from the locus-sdk repo root, it installs `locus-sdk` with the
`openai`, `server`, and `checkpoints` extras but copies no application code,
and its `CMD` names a placeholder `app:server.app` for you to replace. Build
it once, then derive your own image that adds `server.py`:

```bash
# In a locus-sdk checkout, from the repo root, at the tested release
git checkout v{{ locus_sdk_version }}
docker build -t registry.example.com/locus-sdk:{{ locus_sdk_version }} .
```

```dockerfile
# Dockerfile.app, next to your server.py
FROM registry.example.com/locus-sdk:{{ locus_sdk_version }}
COPY server.py /app/server.py
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
```

`server:app` is the `app = server.app` callable from the top of this page.
Build, push to any registry, and run anywhere that runs containers:

```bash
docker build -f Dockerfile.app -t registry.example.com/locus-concierge:0.1.0 .
docker push    registry.example.com/locus-concierge:0.1.0

docker run -p 8080:8080 \
  -e OPENAI_API_KEY=sk-... \
  -e LOCUS_SERVER_API_KEY=replace-with-a-long-random-token \
  registry.example.com/locus-concierge:0.1.0
```

This single image drops straight into Cloud Run, ECS / Fargate, Fly.io,
Azure Container Apps, or any other container host.

## Serverless — scale to zero

Best for low-frequency or bursty traffic. Wrap the FastAPI app in an
ASGI adapter for your functions platform, or deploy the container image
directly to a scale-to-zero container runtime (OCI Container Instances,
Cloud Run, Container Apps). The adapter wraps `server.app`; the FastAPI
app is built on first access to it. Set the provider key and
`LOCUS_SERVER_API_KEY` as function secrets.

## Kubernetes — for production

Best for multi-replica, autoscaled, multi-region production. A minimal
deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: concierge }
spec:
  replicas: 3
  selector: { matchLabels: { app: concierge } }
  template:
    metadata: { labels: { app: concierge } }
    spec:
      containers:
      - name: concierge
        image: registry.example.com/locus-concierge:0.1.0
        ports: [{ containerPort: 8080 }]
        env:
        - name: OPENAI_API_KEY
          valueFrom: { secretKeyRef: { name: locus-secrets, key: openai-api-key } }
        - name: LOCUS_SERVER_API_KEY
          valueFrom: { secretKeyRef: { name: locus-secrets, key: server-api-key } }
        readinessProbe:
          httpGet: { path: /health, port: 8080 }
        resources:
          requests: { cpu: 500m, memory: 1Gi }
          limits:   { cpu: 2,    memory: 4Gi }
---
apiVersion: v1
kind: Service
metadata: { name: concierge }
spec:
  type: LoadBalancer
  selector: { app: concierge }
  ports: [{ port: 80, targetPort: 8080 }]
```

For SSE streaming, ensure your ingress / load balancer doesn't buffer the
response (`X-Accel-Buffering: no` on nginx, or the buffering-off
equivalent on your load balancer).

## Plain VM — full control

Best when you need raw VM access or run the agent alongside other local
services.

```bash
pip install "locus-sdk[openai,server]"

# Your own server.py — the one from the top of this page. It ends in
# `app = server.app`, which is the ASGI callable uvicorn loads below.
mkdir -p ~/concierge && cd ~/concierge
# ... put server.py here ...

# Launch under systemd
sudo tee /etc/systemd/system/concierge.service <<'EOF'
[Unit]
Description=Locus concierge agent
After=network.target

[Service]
Type=simple
User=app
WorkingDirectory=/home/app/concierge
EnvironmentFile=/etc/concierge.env
ExecStart=/home/app/.local/bin/uvicorn server:app --host 0.0.0.0 --port 8080
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable --now concierge
```

Create `/etc/concierge.env` with permissions readable only by the service
account and define both `OPENAI_API_KEY` and `LOCUS_SERVER_API_KEY` there.

## Sessions — `thread_id` for chat UIs

When the underlying agent has a checkpointer, pass a `thread_id` in the
request body for cross-request continuity. Same browser tab → same
`thread_id` → same context. Omit it, and each request starts fresh.

```http
POST /invoke
Content-Type: application/json

{"prompt": "What were we discussing?", "thread_id": "user-c42-support"}
```

When `api_key` is set, the authenticated principal is prefixed onto the
`thread_id` server-side, so threads are scoped to the caller that owns
the key. The server takes a single shared `api_key`, so this is
single-principal scoping — not per-tenant isolation.

## Observability

Wire `TelemetryHook` to your OTLP collector for traces and metrics.
Set the exporter target via the standard OpenTelemetry environment
variables before the agent starts:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
```

```python
from locus.hooks.builtin import TelemetryHook

agent = Agent(
    ...,
    hooks=[TelemetryHook(service_name="my-agent")],
)
```

Datadog accepts OTLP. So do Honeycomb, Tempo, Grafana Cloud, and
every other backend that speaks the spec. See
[Observability](../concepts/observability.md).

## See also

- [Agent Server](../concepts/server.md) — the FastAPI wrapper in detail.
- [Conversation Management](../concepts/conversation-management.md) —
  how `thread_id` survives across requests and restarts.
- [Model providers](../concepts/models.md) — providers and configuration.
