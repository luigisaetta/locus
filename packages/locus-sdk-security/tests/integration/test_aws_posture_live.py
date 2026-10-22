# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/

"""Live integration tests for the read-only AWS posture tools.

Auto-skips unless a real AWS identity is reachable (the read-only
``locus-security-audit`` profile, or whatever ``LOCUS_AWS_PROFILE`` /
the boto3 chain resolves to). Runs only describe/list/get calls and
asserts that a write is refused before any API call.
"""

from __future__ import annotations

import os

import pytest


def _aws_available() -> bool:
    try:
        import boto3

        profile = os.environ.get("LOCUS_AWS_PROFILE", "locus-security-audit")
        return boto3.Session(profile_name=profile).get_credentials() is not None
    except Exception:
        return False


skip_without_aws = pytest.mark.skipif(
    not _aws_available(),
    reason="No AWS identity (set LOCUS_AWS_PROFILE or configure locus-security-audit)",
)


@skip_without_aws
def test_describe_aws_lists_real_services() -> None:
    from locus_security.aws import describe_aws

    services = describe_aws()["services"]
    assert {"s3", "ec2", "iam", "sts"} <= set(services)
    assert len(services) > 100  # the full AWS surface


@skip_without_aws
def test_describe_aws_introspects_an_operation() -> None:
    from locus_security.aws import describe_aws

    out = describe_aws("ec2", "DescribeInstances")
    assert out["readonly"] is True
    assert "Filters" in out["parameters"]


@skip_without_aws
def test_use_aws_real_readonly_call() -> None:
    from locus_security.aws import use_aws

    out = use_aws("sts", "GetCallerIdentity")
    assert out["Arn"].startswith("arn:aws:")
    assert len(out["Account"]) == 12
    assert "ResponseMetadata" not in out  # stripped


@skip_without_aws
def test_use_aws_refuses_write_live() -> None:
    from locus_security.aws import use_aws

    with pytest.raises(PermissionError, match="not a read-only"):
        use_aws("iam", "CreateUser", {"UserName": "should-never-run"})
