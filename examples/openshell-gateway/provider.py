# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/

"""Provider profiles and providers on an OpenShell gateway, over the SDK's gRPC stub.

The ``openshell`` CLI does this with ``openshell provider profile import`` and
``openshell provider create``. Where only the Python package is installed
(``pip install "locus-sdk[openshell]"``), this script does the same against
the gateway in ``docker-compose.yml``::

    python provider.py lint   oci-genai.yaml                 # validate a profile
    python provider.py import oci-genai.yaml                 # make it available
    python provider.py create oci-genai oci-genai OCI_GENAI_API_KEY < key.txt
    python provider.py list
    python provider.py delete oci-genai

``create`` reads the secret from standard input so it never appears in a
shell history or a process list, and points the provider at the workspace's
copy of the profile when ``import`` put it there. Profile files are the YAML the OpenShell
repository ships under ``providers/``; ``oci-genai.yaml`` is its OCI
Generative AI profile. The SDK has no public provider-management client yet,
so this reaches for its gRPC stub and request types.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from typing import Any

import openshell
import yaml
from google.protobuf import json_format
from openshell._proto import datamodel_pb2 as dm
from openshell._proto import openshell_pb2 as pb


# The YAML uses short enum names; the protobuf uses prefixed ones.
_ENUMS: dict[str, Callable[[str], str]] = {
    "category": lambda v: f"PROVIDER_PROFILE_CATEGORY_{v.upper()}",
    "enforcement": lambda v: f"NETWORK_ENFORCEMENT_MODE_{v.upper()}",
    "tls": lambda v: f"NETWORK_TLS_MODE_{v.upper()}",
    "access": lambda v: f"NETWORK_ACCESS_PRESET_{v.upper().replace('-', '_')}",
}


def profile_message(doc: dict[str, Any]) -> pb.ProviderProfile:
    """The ``ProviderProfile`` message for a profile YAML document."""
    doc = dict(doc)
    if "category" in doc:
        doc["category"] = _ENUMS["category"](doc["category"])
    for endpoint in doc.get("endpoints", []):
        for key in ("enforcement", "tls", "access"):
            if key in endpoint:
                endpoint[key] = _ENUMS[key](endpoint[key])
    doc["binaries"] = [{"path": b} if isinstance(b, str) else b for b in doc.get("binaries", [])]
    return json_format.ParseDict(doc, pb.ProviderProfile())


def _workspace_profile(stub: Any, scope: dm.WorkspaceSelector, profile_id: str) -> bool:
    """Whether ``profile_id`` is a profile imported into the workspace (not a built-in)."""
    try:
        found = stub.GetProviderProfile(
            pb.GetProviderProfileRequest(workspace_scope=scope, id=profile_id)
        )
    except openshell.errors.GatewayError:
        return False
    return found.profile.scope == "workspace"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("command", choices=["lint", "import", "create", "list", "delete"])
    parser.add_argument("args", nargs="*")
    parser.add_argument("--endpoint", default="127.0.0.1:8080", help="gateway host:port")
    parser.add_argument("--workspace", default="default")
    opts = parser.parse_args(argv)

    client = openshell.SandboxClient(opts.endpoint)
    stub = client._stub  # noqa: SLF001 - no public provider-management client yet
    scope = dm.WorkspaceSelector(workspace=opts.workspace)

    if opts.command in ("lint", "import"):
        with open(opts.args[0]) as handle:
            item = pb.ProviderProfileImportItem(
                profile=profile_message(yaml.safe_load(handle)), source=opts.args[0]
            )
        if opts.command == "lint":
            response: Any = stub.LintProviderProfiles(
                pb.LintProviderProfilesRequest(workspace_scope=scope, profiles=[item])
            )
        else:
            response = stub.ImportProviderProfiles(
                pb.ImportProviderProfilesRequest(workspace_scope=scope, profiles=[item])
            )
        print(json_format.MessageToJson(response))
    elif opts.command == "create":
        name, kind, variable = opts.args
        secret = sys.stdin.read().strip()
        if not secret:
            print("create: the secret is read from standard input", file=sys.stderr)
            return 2
        provider = dm.Provider(
            metadata=dm.ObjectMeta(name=name), type=kind, credentials={variable: secret}
        )
        # An imported profile is scoped to its workspace; the gateway resolves a
        # provider's type against the built-in profiles unless told the workspace.
        if _workspace_profile(stub, scope, kind):
            provider.profile_workspace = opts.workspace
        response = stub.CreateProvider(
            pb.CreateProviderRequest(workspace_scope=scope, provider=provider)
        )
        print(f"created {response.provider.metadata.name} ({response.provider.type})")
    elif opts.command == "list":
        response = stub.ListProviders(pb.ListProvidersRequest(workspace_scope=scope))
        for provider in response.providers:
            keys = sorted(provider.credentials) or sorted(provider.credential_handles)
            print(provider.metadata.name, provider.type, keys)
    else:
        stub.DeleteProvider(
            pb.DeleteProviderRequest(workspace_scope=scope, name=opts.args[0], allow_missing=True)
        )
        print(f"deleted {opts.args[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
