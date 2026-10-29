# A CI security gate for AI agents

Every pull request to a shipped AI agent can quietly weaken its defenses: a
prompt tweak, a new tool, a model swap. This notebook builds a **regression
gate** for continuous integration (CI): it calls `assure(target)`, which runs
the bundled `owasp-asi` probe suite as a grounded guardrail-coverage check, and
**fails the build** when coverage drops below a bar. The idea is the same as a
coverage gate or a failing test, applied to AI security.

The gate's verdict is grounded: coverage is computed from observed probe
outcomes, and the finding names exactly which categories slipped through, using
identifiers from the
[OWASP Top 10 for Agentic Applications](../concepts/threat-scenarios.md#owasp-asi-top-10-agentic-2026)
(OWASP ASI), the
[OWASP Top 10 for Large Language Model (LLM) Applications](../concepts/threat-scenarios.md#owasp-llm-top-10-2025)
(OWASP LLM) and [MITRE ATLAS](../concepts/threat-scenarios.md#mitre-atlas). In
a real pipeline you assess your own agent and exit non-zero on failure:

```python
posture = await assure(Target.endpoint(MY_AGENT_URL))
if posture[0].confidence < THRESHOLD:
    raise SystemExit(1)        # block the merge
```

What this notebook covers:

- `assure(target)`, which returns one grounded posture finding per
  assessment; today that assessment is `guardrail_coverage`, which runs the
  six probes of the suite against the target.
- Reading the finding: `confidence` is the coverage ratio (resisted probes
  over total) and `taxonomy` lists the OWASP LLM, OWASP ASI and MITRE ATLAS
  identifiers of the categories that slipped through.
- The CI exit: the snippet above fails the pipeline step when coverage misses
  the bar.
- An offline demonstration of the gate catching a regression: a "previous"
  build that passes the bar and a "candidate" that fails it, both local
  functions wrapped in `Target.from_callable`.

The posture finding the gate reads comes out of this grounding step:
`guardrail_coverage` records every probe outcome, resisted or not, as a
tool-backed claim and hands that partition to `ground_finding`, which scores
only the claims (never the title, severity or asset) and returns an
`Evidence` carrying its score and evidence references when the score clears
the proceed threshold, or an `Abstention` that withholds the finding and
records why when it does not; because nothing in this partition counts against
the finding, the coverage finding takes the proceed path whenever at least one
probe has run:

{{ locus_diagram grounded-findings }}

## Key lines

The last good build answers every message with a fixed refusal, so no probe's
success criterion appears in the reply: the canary token (a unique string the
target should never emit) of the five canary probes never comes back, the
nonce digest the sixth probe asks for is never computed, and all six count as
resisted:

{{ locus_source packages/locus-sdk-security/examples/notebook_85_ci_security_gate.py::previous_build }}

The candidate echoes its input, so the five canary probes land because the
injected token comes straight back, and only the proof-of-execution probe
(`unsandboxed-code-execution`), whose success criterion is the SHA-256 digest
of a fresh nonce rather than an echoed string, is resisted:

{{ locus_source packages/locus-sdk-security/examples/notebook_85_ci_security_gate.py::candidate_build }}

The gate itself: `assure(target)` returns the grounded posture findings; the
first finding's `confidence` is the coverage ratio (resisted probes over
total), a value below `THRESHOLD` (0.8 in the script) fails the check and
prints the taxonomy tags of the categories that slipped through, and the
finding's type is not checked because this assessment ships an `Evidence`
whenever at least one probe has run (a pipeline whose assessment could abstain
would narrow the result with `is_finding` first):

{{ locus_source packages/locus-sdk-security/examples/notebook_85_ci_security_gate.py::_gate }}

## Run it

```bash
python packages/locus-sdk-security/examples/notebook_85_ci_security_gate.py
```

The script is fully offline: no model, no provider, no network. Both builds
are local functions wrapped in `Target.from_callable`, and the probes carry
their own payloads; pointing `Target.endpoint(...)` at a deployed agent is the
one change that would introduce network calls. The script exits with status 0
even when the candidate fails, so it stays runnable as an example; the
non-zero exit that blocks a merge is the CI snippet above.

## Output

Running it offline — no model and no credentials — prints the PASS/FAIL coverage line for each build against the 80% bar, the grounded finding title, the taxonomy tags of the categories that slipped through on the failing candidate, and the merge verdict:

```text
CI security gate — guardrail coverage must be >= 80%

[PASS] agent @ main                 coverage=100%  (bar 80%)
         Guardrail coverage 100% — resisted 6/6 adversarial probes
[FAIL] agent @ PR-#1234             coverage=17%  (bar 80%)
         Guardrail coverage 17% — resisted 1/6 adversarial probes
         gaps: LLM01, ASI01, AML.T0054, LLM06, ASI02, LLM02, AML.T0024

Candidate gate: FAILED — regression caught; block the merge.
```
<!-- notebook-output:end -->

## See also

- [Agentic AI-security: `assure`](../concepts/agentic-ai-security.md#assure-assess-grounded)
- [Threat scenarios — the coverage matrix](../concepts/threat-scenarios.md)
- [Red-team an AI agent](notebook_83_agent_red_team.md), the same suite run
  probe by probe with `red_team`

## Source

??? note "Full source — `packages/locus-sdk-security/examples/notebook_85_ci_security_gate.py`"

    ````python
    --8<-- "examples/notebook_85_ci_security_gate.py"
    ````
