"""Tests for Sundae Treasury Fund 1 fetch and normalization."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import respx

from fetchers.sundae_treasury import (
    API_BASE,
    FetcherConfig,
    SundaeTreasuryClient,
    fetch_treasury_fund_1_projects,
)
from normalizers.sundae_treasury import normalize_treasury_fund_1


def _sample_graphql_payload() -> dict[str, object]:
    return {
        "data": {
            "instanceById": {
                "identifier": "instance-1",
                "label": "Intersect Treasury Contracts 1",
                "description": "Treasury Fund 1",
                "projects": [
                    {
                        "identifier": "EC-0001-25",
                        "label": "Example Project",
                        "description": "Build useful things.",
                        "otherIdentifiers": ["ALT-1"],
                        "vendor": {"label": "Example Vendor"},
                        "milestones": [
                            {
                                "identifier": "m-0",
                                "label": "Milestone 1",
                                "description": "Kickoff",
                                "acceptanceCriteria": "Plan delivered",
                                "status": "Matured",
                                "value": [{"assetId": "ada.lovelace", "quantity": "100000000"}],
                                "maturation": {
                                    "format": "2025-08-11T23:00:00Z",
                                    "unixMilli": "1754953200000",
                                },
                            },
                            {
                                "identifier": "m-1",
                                "label": "Milestone 2",
                                "description": "Delivery",
                                "acceptanceCriteria": "Code delivered",
                                "status": "Active",
                                "value": [{"assetId": "ada.lovelace", "quantity": "250000000"}],
                                "maturation": {
                                    "format": "2026-06-29T23:00:00Z",
                                    "unixMilli": "1782774000000",
                                },
                            },
                        ],
                    }
                ],
            }
        }
    }


@respx.mock
def test_fetch_treasury_fund_1_projects_caches_raw_response(tmp_path: Path) -> None:
    route = respx.post(API_BASE).mock(
        return_value=httpx.Response(200, json=_sample_graphql_payload())
    )
    cfg = FetcherConfig(user_agent="test/1.0", data_root=tmp_path / "data")

    with SundaeTreasuryClient(cfg) as client:
        target = fetch_treasury_fund_1_projects(output_root=tmp_path / "data", client=client)

    assert route.call_count == 1
    raw = json.loads(target.read_text(encoding="utf-8"))
    assert raw["source"] == "sundae_treasury_graphql"
    assert raw["response"]["data"]["instanceById"]["projects"][0]["identifier"] == "EC-0001-25"


def test_normalize_treasury_fund_1_outputs_projects_vendors_and_milestones(
    tmp_path: Path,
) -> None:
    raw_path = tmp_path / "data" / "_raw" / "sundae_treasury" / "treasury-fund-01-projects.json"
    raw_path.parent.mkdir(parents=True)
    raw_path.write_text(
        json.dumps(
            {
                "source": "sundae_treasury_graphql",
                "source_url": API_BASE,
                "fetched_at": "2026-05-15T12:00:00Z",
                "instance_id": "instance-1",
                "query": "query",
                "response": _sample_graphql_payload(),
            }
        ),
        encoding="utf-8",
    )

    counters = normalize_treasury_fund_1(data_root=tmp_path / "data", raw_path=raw_path)

    assert counters == {"projects": 1, "vendors": 1, "milestones": 2}
    output_dir = tmp_path / "data" / "historical" / "treasury-fund-01"
    projects = json.loads((output_dir / "projects.json").read_text(encoding="utf-8"))
    vendors = json.loads((output_dir / "vendors.json").read_text(encoding="utf-8"))
    milestones = json.loads((output_dir / "milestones.json").read_text(encoding="utf-8"))

    assert projects[0]["project_id"] == "EC-0001-25"
    assert projects[0]["vendor_label"] == "Example Vendor"
    assert projects[0]["total_contract_ada"] == 350.0
    assert projects[0]["amount_by_milestone_status_ada"] == {
        "Active": 250.0,
        "Matured": 100.0,
    }
    assert vendors[0]["display_name"] == "Example Vendor"
    assert vendors[0]["total_contract_ada"] == 350.0
    assert milestones[0]["amount_ada"] == 100.0
