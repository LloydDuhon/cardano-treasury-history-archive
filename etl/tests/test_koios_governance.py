"""Tests for Koios on-chain treasury withdrawal fetch and normalization."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import respx

from fetchers.koios_governance import (
    API_BASE,
    FetcherConfig,
    KoiosGovernanceClient,
    fetch_treasury_withdrawal_snapshot,
)
from normalizers.onchain_treasury_withdrawals import normalize_onchain_treasury_withdrawals


def _sample_proposal() -> dict[str, object]:
    return {
        "block_time": 1778849533,
        "proposal_id": "gov_action1example",
        "proposal_tx_hash": "9a020ea7a6a0d813ff08c92bd8300b26077ae69a4b827c4d432ac665120325d7",
        "proposal_index": 0,
        "proposal_type": "TreasuryWithdrawals",
        "proposal_description": {"tag": "TreasuryWithdrawals"},
        "deposit": "100000000000",
        "return_address": "stake1uexample",
        "proposed_epoch": 631,
        "ratified_epoch": None,
        "enacted_epoch": None,
        "dropped_epoch": None,
        "expired_epoch": None,
        "expiration": 638,
        "meta_url": "ipfs://QmExample",
        "meta_hash": "abc123",
        "meta_json": {
            "body": {
                "title": "Example Treasury Withdrawal",
                "abstract": "Maintain useful infrastructure.",
                "rationale": "Cardano needs this work.",
            }
        },
        "meta_is_valid": True,
        "withdrawal": [
            {
                "stake_address": "stake1uwithdrawal",
                "amount": "1680000000000",
            }
        ],
    }


@respx.mock
def test_fetch_treasury_withdrawal_snapshot_caches_raw_response(tmp_path: Path) -> None:
    route = respx.get(f"{API_BASE}/proposal_list").mock(
        return_value=httpx.Response(200, json=[_sample_proposal()])
    )
    cfg = FetcherConfig(user_agent="test/1.0", data_root=tmp_path / "data")

    with KoiosGovernanceClient(cfg) as client:
        target = fetch_treasury_withdrawal_snapshot(output_root=tmp_path / "data", client=client)

    assert route.call_count == 1
    raw = json.loads(target.read_text(encoding="utf-8"))
    assert raw["source"] == "koios_governance_api"
    assert raw["query"] == {"proposal_type": "eq.TreasuryWithdrawals"}
    assert raw["proposals"][0]["proposal_id"] == "gov_action1example"


def test_normalize_onchain_treasury_withdrawals_outputs_historical_dataset(
    tmp_path: Path,
) -> None:
    raw_path = (
        tmp_path / "data" / "_raw" / "koios_governance" / ("treasury-withdrawal-proposals.json")
    )
    raw_path.parent.mkdir(parents=True)
    raw_path.write_text(
        json.dumps(
            {
                "source": "koios_governance_api",
                "source_url": f"{API_BASE}/proposal_list",
                "fetched_at": "2026-05-15T14:00:00Z",
                "query": {"proposal_type": "eq.TreasuryWithdrawals"},
                "proposals": [_sample_proposal()],
            }
        ),
        encoding="utf-8",
    )

    counters = normalize_onchain_treasury_withdrawals(
        data_root=tmp_path / "data",
        raw_path=raw_path,
    )

    assert counters == {"withdrawal_actions": 1}
    output_dir = tmp_path / "data" / "historical" / "cardano-treasury-withdrawals"
    records = json.loads((output_dir / "withdrawals.json").read_text(encoding="utf-8"))
    meta = json.loads((output_dir / "_meta.json").read_text(encoding="utf-8"))

    assert records[0]["withdrawal_action_id"] == "gov_action1example"
    assert records[0]["title"] == "Example Treasury Withdrawal"
    assert records[0]["status"] == "active"
    assert records[0]["block_time_iso"] == "2026-05-15T12:52:13Z"
    assert records[0]["total_withdrawal_ada"] == 1_680_000.0
    assert records[0]["withdrawals"][0]["stake_address"] == "stake1uwithdrawal"
    assert meta["records"] == 1
    assert meta["total_withdrawal_ada"] == 1_680_000.0
