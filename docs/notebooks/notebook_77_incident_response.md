# Incident Response

Models the loop an SRE / infra-devops on-call engineer runs when a production page fires::

    Page fires
      │
      └──> Triage  ──>  scatter to 3 parallel investigators
                          ├── log analyst
                          ├── metric analyst
                          └── trace analyst
                          ▼
                   Synthesizer (root-cause hypothesis)
                          │
                          ▼
            Severity gate ─── critical? ──> page humans (interrupt)
                          │                     │
                          │                  approve mitigation? yes/no
                          │                     │
                          ▼                     ▼
                       Mitigator <──────────────┘
                          │
                          ▼
                       Postmortem (structured)

A bad `v4.12.0` deploy triggers the page: the triage agent classifies
severity, then the workflow scatters to three parallel investigator
Agents — a log analyst, a metric analyst, and a trace analyst — each
inspecting its own signal (pod logs, latency/saturation metrics,
downstream service traces). A synthesizer Agent fuses their reports into
a single root-cause hypothesis, a severity gate decides whether to
auto-remediate or page a human, and the run ends with a structured
postmortem.

- `Send`: fan out to 3 investigator Agents in parallel (logs, metrics,
  traces).
- `add_conditional_edges`: severity-based routing decides
  auto-mitigate (rollback / scale-up / flag toggle) vs escalate to a
  human.
- `interrupt()`: critical severity pauses for explicit human approval
  before any remediation runs.
- `output_schema=Postmortem`: the final report is a typed Pydantic
  instance, ready to file into a reliability-review database.

Run it (defaults to the bundled mock model; set `LOCUS_MODEL_PROVIDER` to `openai` / `anthropic` for a live model):

    python examples/notebook_77_incident_response.py

Offline:

    LOCUS_MODEL_PROVIDER=mock python examples/notebook_77_incident_response.py

Pin a strong-enough model for the structured postmortem schema:

    LOCUS_MODEL_PROVIDER=openai LOCUS_MODEL_ID=gpt-4o python examples/notebook_77_incident_response.py

## Source

````python
--8<-- "examples/notebook_77_incident_response.py"
````
