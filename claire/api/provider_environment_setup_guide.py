"""Provider environment setup guide payload.

S34R14 gives operator-visible setup guidance only.
"""

from __future__ import annotations

from typing import Any, Dict, List


WINDOWS_POWERSHELL_EXAMPLES: List[str] = [
    '$env:CLAIRE_SEARCH_PROVIDER="manual_stub"',
    '$env:CLAIRE_ALLOW_CONTROLLED_HEAD_PROBE="true"',
    '$env:CLAIRE_ALLOW_ONE_SHOT_METADATA_PROBE="true"',
]

WINDOWS_CMD_EXAMPLES: List[str] = [
    'set CLAIRE_SEARCH_PROVIDER=manual_stub',
    'set CLAIRE_ALLOW_CONTROLLED_HEAD_PROBE=true',
    'set CLAIRE_ALLOW_ONE_SHOT_METADATA_PROBE=true',
]


def get_provider_environment_setup_guide() -> Dict[str, Any]:
    return {
        "version": "v19.89.8-S34R14",
        "status": "provider_environment_setup_guide_visible",
        "purpose": "Prepare explicit provider gates for first metadata-only probe.",
        "recommended_first_provider": "manual_stub",
        "powershell_examples": WINDOWS_POWERSHELL_EXAMPLES,
        "cmd_examples": WINDOWS_CMD_EXAMPLES,
        "warnings": [
            "Set variables only in the backend launch shell for controlled testing.",
            "Do not enable response body reads.",
            "Do not enable browser execution.",
            "Do not enable automatic updates.",
            "Do not enable autonomous runtime mutation.",
        ],
        "network_request": "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
    }
