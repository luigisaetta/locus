# OpenShell gateway for the Locus harness

`locus.harness.OpenShellBackend` runs the coding harness inside an
[NVIDIA OpenShell](https://github.com/NVIDIA/OpenShell) sandbox. This directory
starts the one piece it needs that Locus does not ship: a gateway. It is the
same shape as `examples/litellm-gateway/`: one `docker compose up -d` on any
machine with Docker Engine 28+, no installer script, no package manager.

```bash
cd examples/openshell-gateway
docker compose up -d                      # init writes sandbox JWT keys, then the gateway starts
curl -sf http://127.0.0.1:8081/readyz     # 200 when ready

export LOCUS_OPENSHELL_ENDPOINT=127.0.0.1:8080
pytest tests/integration/test_harness_openshell_live.py   # the five live harness tests
```

What runs:

- `gateway` — `ghcr.io/nvidia/openshell/gateway`, bound to loopback on 8080
  (gRPC) and 8081 (health). It creates sandboxes as sibling containers through
  the host's Docker socket (Docker-outside-of-Docker, no `--privileged`), using
  `nvcr.io/nvidia/base/ubuntu:24.04` as the default sandbox image and the
  OpenShell `sandbox` and `supervisor` images for its own binaries.
- `init` — one-shot `generate-certs` that writes the sandbox JWT keys under
  `/var/lib/openshell/tls`. Existing keys are kept.

`/var/lib/openshell` is bind-mounted at the same absolute path inside the
container because the gateway hands that path to Docker when it mounts the
supervisor binary into each sandbox.

## Host requirements

The sandbox binary confines itself with
[Landlock](https://docs.kernel.org/userspace-api/landlock.html) and exits at
start-up unless the kernel is 6.2 or newer **and** Landlock is in the active
LSM list:

```bash
cat /sys/kernel/security/lsm        # must contain "landlock"
```

Docker Desktop (macOS, Windows) and Ubuntu 22.04+ already have it. RHEL-family
kernels (Oracle Linux 9, RHEL 9, Rocky, Alma) build Landlock in but leave it
out of the active list, so a sandbox dies with `Landlock ABI probe … not in
active LSM list`. Add it to the boot arguments and reboot:

```bash
sudo grubby --update-kernel=ALL --args="lsm=landlock,lockdown,yama,integrity,selinux,bpf"
sudo reboot
```

SELinux can stay enforcing; the gateway labels its sandbox volumes.

## Using it from Locus

```python
from locus.harness import OpenShellBackend, build_harness

backend = OpenShellBackend.create(workspace="default", endpoint="127.0.0.1:8080")
try:
    harness = build_harness(backend)
    ...
finally:
    backend.close()          # deletes the sandbox it created
```

`endpoint` is `host:port`; a loopback endpoint is a plaintext connection,
which is what this gateway serves. For a TLS gateway pass `tls=` and, when the
gateway requires it, `bearer_token=` or `client_credentials=` through
`client_options`.

## OCI Generative AI through the sandbox proxy

OpenShell ships an `oci-genai` provider profile: the gateway keeps an OCI
Generative AI API key, the sandbox sees `OCI_GENAI_API_KEY` as a placeholder,
and the sandbox proxy swaps in the real key only on requests to
`inference.generativeai.<region>.oci.oraclecloud.com/openai/v1/...` from the
binaries the profile names (`curl`). The key never enters the sandbox.

With the OpenShell CLI:

```bash
openshell provider profile import -f providers/oci-genai.yaml     # from the OpenShell repository
openshell provider create --name oci-genai --type oci-genai --credential OCI_GENAI_API_KEY="$OCI_GENAI_API_KEY"
```

With only the Python package, `provider.py` does the same over the SDK's gRPC
stub; the secret is read from standard input:

```bash
python provider.py import oci-genai.yaml
python provider.py create oci-genai oci-genai OCI_GENAI_API_KEY < key.txt
```

The key is a compartment-scoped Generative AI API key
(`oci generative-ai api-key create ...`), with an IAM policy that allows
`request.principal.type='generativeaiapikey'` to use `generative-ai-family`
in that compartment; the profile's header comments walk through both.

Then a sandbox with the provider attached, in an image that has `curl` (the
default image does not):

```python
backend = OpenShellBackend.create(
    image="docker.io/library/buildpack-deps:noble-curl", providers=["oci-genai"]
)
```

The live test for this path runs with:

```bash
LOCUS_OPENSHELL_PROVIDER=oci-genai \
LOCUS_OPENSHELL_IMAGE=docker.io/library/buildpack-deps:noble-curl \
pytest tests/integration/test_harness_openshell_live.py -k provider
```

## Scope

Loopback only, TLS off and user calls unauthenticated — a developer or CI
box, not a shared host. For a shared gateway use the OpenShell Helm chart
(`oci://ghcr.io/nvidia/openshell/helm-chart`) with TLS and OIDC enabled, and
point `LOCUS_OPENSHELL_ENDPOINT` (and `LOCUS_OPENSHELL_TOKEN`) at it.

Settings live in `gateway.toml`; the compose file only adds the database URL
and the data-directory paths that cannot be expressed there. Both files are
adapted from NVIDIA's `deploy/docker/` reference (Apache-2.0).
