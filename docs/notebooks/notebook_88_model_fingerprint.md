# Model and hardware fingerprinting

A Chief Information Security Officer (CISO) is about to sign a $2M/year
contract with a vendor claiming to serve "GPT-4o on H100 clusters". Before
signing, she wants evidence about what the endpoint actually serves — which
model class, which inference engine and which hardware class — and a record of
whether the measurement observed enough to support a verdict at all.

Timing is the cheapest signal a buyer with black-box API access can collect: it
needs no privileged access and no co-located hardware. Stream a completion and
time the token arrivals; model size shows up in inter-token latency, the
inference engine in the cadence, and the hardware shifts the whole profile. The
example measures that profile, classifies it, grounds the verdict so that an
under-observed vector abstains rather than asserting an identity, and records
the probe on a hash-chained `AuditTrail` exported as JSON Lines (JSONL) —
evidence for a service-level agreement (SLA) dispute or a procurement audit.

The classifier the package ships, `default_classifier`, is a deterministic
heuristic: it bins the vector on mean inter-token latency and its coefficient
of variation, and its confidence is derived from feature coverage alone, not
from the fit of the verdict. The library documents it as a placeholder for a
trained classifier, which plugs in through the `classifier=` argument of
`fingerprint_to_finding` and implements the `FingerprintClassifier` protocol.
Read its verdicts as a demonstration of the pipeline, not as an identification
of any vendor's model.

What this notebook covers:

- `measure_endpoint_timing`, which streams timed chat completions from an
  OpenAI-compatible endpoint and returns a feature vector over `FEATURE_KEYS`
  (`ttft_ms_p50`, `itl_ms_mean`, `itl_cv`, `tps_mean`), or a deterministic
  offline sample when no key is set.
- `fingerprint_to_finding`, which classifies the vector and grounds the verdict
  through [GSAR](../concepts/gsar.md): a verdict whose feature coverage clears
  `min_coverage` (0.75 by default) is filed as a tool-backed claim and ships as
  a `FingerprintFinding`; a thinner one is filed as an ungrounded claim, scores
  below the proceed threshold and comes back as an `Abstention`.
- `is_finding`, the split between the two result types, and the fields each
  carries.
- `AuditTrail`: `record` and `record_event` for the probe's three records,
  `verify` for the hash chain and `export_jsonl` for the evidence file.
- The MITRE ATLAS (Adversarial Threat Landscape for Artificial-Intelligence
  Systems) tags the finding carries, `AML.T0040` and `AML.T0024`.

## Key lines

The example keeps the whole probe in `run_fingerprint`; read the calls between
the print statements: `measure_endpoint_timing` and the coverage count over
`FEATURE_KEYS`, `fingerprint_to_finding` with the `is_finding` branch that
prints either the `FingerprintFinding` (its `verdict`, `gsar_score`,
`evidence_refs` and `taxonomy`) or the `Abstention` (its `reason` and score),
and the `AuditTrail` calls — `record` for the session markers, `record_event`
for the result, then `verify` and `export_jsonl`. The interpretation block
compares only the hardware class with the vendor claim, by testing for the
substring `H100`; on the offline sample the heuristic reports `7-8B class` on
`H100/A100 class` hardware, so the script reports the hardware class as
consistent with the claim and leaves the model line, which does not match the
claimed GPT-4o, to the reader:

{{ locus_source packages/locus-sdk-security/examples/notebook_88_model_fingerprint.py::run_fingerprint }}

## Run it

```bash
python packages/locus-sdk-security/examples/notebook_88_model_fingerprint.py
```

The script runs no agent and does not import the `config.py` harness that
notebooks 81 and 82 use, so `LOCUS_MODEL_PROVIDER` has no effect; the only
credential it reads is `OPENAI_API_KEY`. When it is set,
`measure_endpoint_timing` streams `FINGERPRINT_SAMPLES` chat completions
(default 10) for `FINGERPRINT_MODEL` (default `gpt-4o-mini`) from the
OpenAI-compatible endpoint at `TIMING_BASE_URL` (default
`https://api.openai.com/v1`) and times the token arrivals. Without it the
function returns the deterministic sample vector, so the classify-then-ground
pipeline and the audit trail run end to end with no credentials and no network
call.

Two properties of the measurement matter when reading a live result. A request
that fails or yields fewer than two tokens is dropped, and when every request
fails the function returns the same deterministic sample it uses offline, so a
run against an unreachable or rate-limited endpoint prints a grounded finding
for the sample vector rather than an `Abstention`. A live measurement always
fills all four feature keys, so with the shipped classifier the coverage test
in `fingerprint_to_finding` never abstains on its output; an `Abstention` needs
a vector from another source that observed fewer keys, or a custom classifier
that reports a lower coverage. The audit record for the result carries its type
and its scalar fields — the asset of a `FingerprintFinding`, the reason of an
`Abstention` — not the verdict or the score; keep the exported JSONL together
with the printed finding.

To probe a vendor endpoint, point the live path at it and name the model under
test and the asset the finding is about:

```bash
export OPENAI_API_KEY=sk-...
export TIMING_BASE_URL=https://vendor-api.example.com/v1
export FINGERPRINT_MODEL=gpt-4o
export FINGERPRINT_SAMPLES=20
export FINGERPRINT_ASSET='VendorCo-contract-2026'
python packages/locus-sdk-security/examples/notebook_88_model_fingerprint.py
```

## Output

Running it offline — no model and no credentials — prints the probe's model name, sample count and path, the timing feature vector of the deterministic sample with its coverage, the grounded `FingerprintFinding` (GSAR score, model class, engine, hardware class, confidence, coverage, evidence reference and MITRE ATLAS tags) with the script's interpretation of the hardware class against the vendor claim, the audit-trail record count and integrity check, and the command for probing a live endpoint:

```text
== Model / hardware fingerprinting via timing side-channels ==
   model  : 'gpt-4o-mini'
   samples: 10
   path   : offline deterministic sample

Collecting 10 timing samples...

Extracted timing features:
  ttft_ms_p50          38.2000
  itl_ms_mean          11.4000
  itl_cv               0.0700
  tps_mean             87.6000

Feature coverage: 100% (4/4 keys)

Classifying and grounding...

  [FINDING ] Grounded FingerprintFinding
             gsar_score : 1.00
             model      : 7-8B class
             engine     : vLLM (continuous-batching)
             hardware   : H100/A100 class
             confidence : 0.90
             coverage   : 100%
             evidence   : ['tool:measure_endpoint_timing:vendor-inference-api']
             taxonomy   : AML.T0040, AML.T0024

  Interpretation:
    Vendor claims 'GPT-4o on H100 clusters'.
    Timing fingerprint identifies: 7-8B class / vLLM (continuous-batching) / H100/A100 class.
    Hardware class CONSISTENT with H100 claim.

Audit trail: 3 records, integrity OK
(Export JSONL for vendor SLA dispute or procurement audit evidence.)

To probe a real vendor endpoint, run:
  OPENAI_API_KEY=sk-... \
  TIMING_BASE_URL=https://vendor-api.example.com/v1 \
  FINGERPRINT_MODEL=gpt-4o \
  FINGERPRINT_SAMPLES=20 \
  FINGERPRINT_ASSET='VendorCo-contract-2026' \
  python packages/locus-sdk-security/examples/notebook_88_model_fingerprint.py
```
<!-- notebook-output:end -->

## See also

- [Security layer — Inference fingerprinting](../concepts/security.md#inference-fingerprinting)
  — the admit/abstain contract behind `ground_fingerprint` and the
  `FingerprintClassifier` protocol a trained classifier implements.
- [Security — Fingerprinting](../api/security.md#fingerprinting) —
  `measure_endpoint_timing`, `default_classifier` and `fingerprint_to_finding`.
- [Control — The record](../api/control.md#the-record) — `AuditTrail`, what
  `verify()` catches and the `expected_head` anchor that detects truncation.
- [Environment variables — Model fingerprinting](../how-to/environment-variables.md#model-fingerprinting)
  — `FINGERPRINT_MODEL`, `FINGERPRINT_ASSET` and `FINGERPRINT_SAMPLES`.

## Source

??? note "Full source — `packages/locus-sdk-security/examples/notebook_88_model_fingerprint.py`"

    ````python
    --8<-- "examples/notebook_88_model_fingerprint.py"
    ````
