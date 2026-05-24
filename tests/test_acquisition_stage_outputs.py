from __future__ import annotations

from datetime import datetime, timezone


def _stage_input(payload: dict) -> dict:
    return {
        "stage_id": 27,
        "source_stage": "portfolio_creation_optimization",
        "payload": payload,
        "metadata": {"route": "acquisition_package"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def test_stage_28_identifies_named_acquirers_from_portfolio_context():
    from runtime_core.acquisition.acquirer_identification import AcquirerIdentification

    stage = AcquirerIdentification()
    result = stage.execute(
        _stage_input(
            {
                "candidate_id": "portfolio-secure-autonomy",
                "domain": "defense",
                "category": "secure autonomous mission intelligence",
                "portfolio_thesis": "Defense autonomy platform with AI, autonomous, aerospace and command workflow signals.",
                "keywords": ["autonomous", "defense", "aerospace"],
            }
        )
    )

    assert result["stage_id"] == 28
    assert result["status"] == "completed"
    assert result["confidence"] > 0
    payload = result["payload"]
    assert payload["status"] == "acquirer_candidates_identified"
    assert payload["acquirer_count"] >= 1
    top = payload["acquirer_matches"][0]
    assert top["name"] == "Lockheed Martin"
    assert top["ticker"] == "LMT"
    assert top["acquirer_category"] == "strategic_defense_prime"
    assert top["strategic_fit_rationale"]
    assert top["capability_gap_narrative"]
    assert top["timing_signal"] in {"near_term_review_window", "watchlist_timing_window", "early_signal_only"}
    assert payload["manual_review_required"] is True
    assert payload["runtime_truth_write"] == "blocked"


def test_stage_29_generates_fit_rationale_from_stage_28_output():
    from runtime_core.acquisition.acquirer_identification import AcquirerIdentification
    from runtime_core.acquisition.fit_rationale import FitRationale

    stage_28 = AcquirerIdentification().execute(
        _stage_input(
            {
                "domain": "technology",
                "category": "enterprise AI governance platform",
                "portfolio_thesis": "AI cloud platform governance opportunity for enterprise buyers.",
                "keywords": ["ai", "cloud", "platform"],
            }
        )
    )

    stage_29 = FitRationale().execute(
        {
            "stage_id": 28,
            "source_stage": "acquirer_identification",
            "payload": stage_28["payload"],
            "metadata": {"route": "acquisition_package"},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )

    assert stage_29["stage_id"] == 29
    assert stage_29["status"] == "completed"
    assert stage_29["confidence"] > 0
    payload = stage_29["payload"]
    assert payload["status"] == "acquisition_fit_ready"
    assert payload["fit_count"] >= 1
    assert payload["top_fit"]["name"] in {"Microsoft", "Google", "Amazon"}
    assert payload["top_fit"]["strategic_fit_rationale"]
    assert payload["top_fit"]["capability_gap_narrative"]
    assert payload["top_fit"]["deal_readiness"] in {
        "package_review_candidate",
        "strategic_watchlist",
        "needs_more_evidence",
    }
    assert payload["manual_review_required"] is True
    assert payload["runtime_truth_write"] == "blocked"
