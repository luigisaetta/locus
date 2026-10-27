# Vendor DPA & Data-Privacy Review

Reviewing a data processor's Data Processing Agreement involves multiple
stakeholders working in parallel, then a back-and-forth negotiation
phase, then sign-off::

    DPA intake
       │
       ▼
    Parser  (extracts clauses)
       │
       ▼
    Scatter to 3 parallel reviewers
       ├── Legal       (lawful basis, data-subject rights, consent, purpose)
       ├── Governance  (minimisation, retention/deletion, residency, sub-processors)
       └── Compliance  (GDPR/CCPA, DPIA, transfer mechanisms, liability for fines)
       ▼
    Synthesizer  (consolidated review report)
       │
       ▼
    Negotiation gate ── any blockers? ── yes ──> Negotiate (interrupt; loop)
                                       │            │
                                       │            └── revised terms ──┐
                                       │                                │
                                       └── no ──┐                       │
                                                ▼                       │
                                          Sign-off  <───────────────────┘
                                                ▼
                                          ContractDecision (typed)

The processor here is a marketing-analytics SaaS that ingests your
customers' personal data, so a weak erasure SLA or a vague
international-transfer mechanism is a real compliance gap, not a
paperwork nit — the breach-notification window should track the GDPR
Art. 33 72-hour timeline. The DPO — the privacy office's data-protection
officer — writes the typed sign-off.

- `Send`: three reviewers run concurrently.
- `add_conditional_edges` with cycles enabled: negotiation can loop
  back to re-review when terms change. Hard cap of 3 rounds.
- `interrupt()`: negotiation step pauses for human counsel to edit terms.
- `output_schema=ContractDecision`: typed terminal artifact.

Run it (defaults to the bundled mock model; set `LOCUS_MODEL_PROVIDER` to `openai` / `anthropic` for a live model):

    python examples/notebook_79_contract_review.py

Offline:

    LOCUS_MODEL_PROVIDER=mock python examples/notebook_79_contract_review.py

Pin a strong-enough model for the structured ContractDecision schema:

    LOCUS_MODEL_PROVIDER=openai LOCUS_MODEL_ID=gpt-4o python examples/notebook_79_contract_review.py

## Source

````python
--8<-- "examples/notebook_79_contract_review.py"
````
