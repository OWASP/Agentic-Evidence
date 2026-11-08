# SPDX-License-Identifier: Apache-2.0
"""Smoke test for the M0 package skeleton."""

from importlib.metadata import version

import agentic_evidence


def test_version_matches_distribution_metadata() -> None:
    assert agentic_evidence.__version__ == version("agentic-evidence")
