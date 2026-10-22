# Integrations

Adapters that bridge Locus to external frameworks, clouds, and vendor APIs.
Cloud posture is one worked example domain — the same adapter pattern
applies to any vendor API.

## FastMCP

Expose a Locus agent (or any of its tools) as a Model Context Protocol
server, and consume MCP tools from any compliant client as native
Locus `Tool`s.

::: locus.integrations.fastmcp.LocusMCPServer
::: locus.integrations.fastmcp.create_mcp_server
::: locus.integrations.fastmcp.mcp_tool_to_locus

## AWS cloud-posture (read-only)

Two generic, spec-driven tools driven by botocore's service models — the
agent discovers the shape of AWS from the spec and runs read-only operations
whose responses become grounded-finding evidence. Read-only by construction:
`use_aws` refuses any non-read operation before a call is made. See the
[cloud-posture agent](../concepts/cloud-posture.md) for the full workflow.

Install the extra: `pip install 'locus-sdk[aws]'`.

::: locus_security.aws.describe_aws
::: locus_security.aws.use_aws
::: locus_security.aws.is_readonly_operation
::: locus_security.aws.aws_services

The agent-facing `@tool` wrappers (`describe_aws_tool`, `use_aws_tool`) and the
[`create_soc_analyst`](../concepts/cloud-posture.md) security-operations (SOC)
analyst factory compose these into a grounded posture agent.

## Vendor integration examples

The notebooks ship *worked* vendor integrations in
[`examples/integrations/`][int]. Each is an ordinary Locus `@tool` following
one convention — **bring your own credentials**: read the vendor key from the
environment and call the live API when it's set, otherwise return a
deterministic offline sample so the example runs with no account. The return
shape is identical either way, so the agent's reasoning doesn't change between
the offline demo and a live deployment.

| Tool | Vendor shape | Credential |
|------|--------------|------------|
| [`measure_endpoint_timing`][rt] | Streaming time-to-first-token / cadence probe | none (uses any reachable endpoint) |
| [`dispatch_timing_probe`][gpu] | RunPod / Lambda inference-fingerprint probe | `RUNPOD_API_KEY`, `LAMBDA_API_KEY` |
| [`enrich_indicator`][ti] | VirusTotal / GreyNoise indicator-of-compromise (IOC) reputation | `VT_API_KEY` |
| [`query_siem`][siem] | Splunk / Elastic log/alert search (a SIEM) | `SIEM_URL`, `SIEM_TOKEN` |

Hand these to a triage agent end-to-end in
[live vendor integrations](../notebooks/notebook_70_vendor_integrations.md);
the GPU probe grounds into a fingerprint finding in
[specialist agents](../notebooks/notebook_27_specialist_agents.md). The
bring-your-own-credentials contract is documented in
[`examples/integrations/README.md`][int].

[int]: https://github.com/oracle/locus/tree/main/packages/locus-sdk-security/examples/integrations
[ti]: https://github.com/oracle/locus/blob/main/packages/locus-sdk-security/examples/integrations/threat_intel.py
[siem]: https://github.com/oracle/locus/blob/main/packages/locus-sdk-security/examples/integrations/siem_query.py
[gpu]: https://github.com/oracle/locus/blob/main/packages/locus-sdk-security/examples/integrations/gpu_probe_dispatch.py
[rt]: https://github.com/oracle/locus/blob/main/packages/locus-sdk-security/examples/integrations/remote_timing.py
