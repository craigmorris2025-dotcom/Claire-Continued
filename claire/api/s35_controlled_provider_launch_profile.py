"""S35 controlled provider launch profile.

This module exposes exact shell launch profiles for controlled testing.
It performs no network request and does not enable execution by itself.
"""

from __future__ import annotations

from typing import Any, Dict, List


POWERSHELL_PROFILE: List[str] = [
    '$env:CLAIRE_SEARCH_PROVIDER="manual_stub"',
    '$env:CLAIRE_ALLOW_CONTROLLED_HEAD_PROBE="true"',
    '$env:CLAIRE_ALLOW_ONE_SHOT_METADATA_PROBE="true"',
    '$env:CLAIRE_ALLOW_CONTROLLED_METADATA_GET="false"',
    'python main.py',
]

CMD_PROFILE: List[str] = [
    'set CLAIRE_SEARCH_PROVIDER=manual_stub',
    'set CLAIRE_ALLOW_CONTROLLED_HEAD_PROBE=true',
    'set CLAIRE_ALLOW_ONE_SHOT_METADATA_PROBE=true',
    'set CLAIRE_ALLOW_CONTROLLED_METADATA_GET=false',
    'python main.py',
]


def get_s35_controlled_provider_launch_profile() -> Dict[str, Any]:
    return {
        "version": "v19.89.8-S35R4",
        "status": "controlled_provider_launch_profile_visible",
        "profile_type": "manual_stub_head_only",
        "powershell_profile": POWERSHELL_PROFILE,
        "cmd_profile": CMD_PROFILE,
        "operator_instruction": (
            "Use these variables only in the backend launch shell for controlled "
            "first-probe testing. They do not enable body reads, browser execution, "
            "runtime truth mutation, autonomous execution, or automatic updates."
        ),
        "network_request": "blocked_until_operator_endpoint_call",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
    }
