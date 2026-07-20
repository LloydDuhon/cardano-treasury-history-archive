from scripts.generate_funding_priorities_report import (
    aggregate,
    aggregate_subcategories,
    classify,
    is_delivered,
)


def test_specific_challenge_maps_to_governance() -> None:
    proposal = {"challenge": "F10: dRep improvement and onboarding"}
    pillar, subcategory, confidence, basis = classify(proposal)

    assert pillar == "P3"
    assert subcategory == "governance-systems"
    assert confidence == "high"
    assert basis == "challenge"


def test_open_challenge_uses_proposal_text() -> None:
    proposal = {
        "challenge": "F10: Catalyst Open",
        "title": "Hydra scaling research",
        "summary": "Research paper on Hydra throughput and layer 2 scalability",
    }
    pillar, _, confidence, basis = classify(proposal)

    assert pillar == "P1"
    assert confidence == "medium"
    assert basis == "proposal-text"


def test_unfunded_complete_source_row_is_not_delivered() -> None:
    proposal = {"funding_status": "not_approved", "project_status": "complete"}

    assert not is_delivered(proposal)


def test_aggregate_keeps_currencies_separate() -> None:
    rows = [
        {
            "year": 2024,
            "pillar": "P2",
            "currency": "ADA",
            "amount_requested": 100,
            "amount_received": 90,
            "funded": True,
            "delivered": True,
        },
        {
            "year": 2024,
            "pillar": "P2",
            "currency": "USD",
            "amount_requested": 50,
            "amount_received": 0,
            "funded": False,
            "delivered": False,
        },
    ]

    result = aggregate(rows, "year")

    assert len(result) == 2
    assert result[0]["currency"] == "ADA"
    assert result[0]["delivered_amount"] == 90
    assert result[1]["currency"] == "USD"
    assert result[1]["funded_amount"] == 0


def test_subcategory_rollup_is_preserved() -> None:
    rows = [
        {
            "fund": 10,
            "pillar": "P2",
            "subcategory": "defi-and-payments",
            "currency": "ADA",
            "amount_requested": 100,
            "amount_received": 90,
            "funded": True,
            "delivered": False,
        }
    ]

    result = aggregate_subcategories(rows, "fund")

    assert result[0]["subcategory"] == "defi-and-payments"
