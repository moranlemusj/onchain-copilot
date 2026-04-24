import os

import pytest

from copilot.tools.transaction import get_recent_transactions
from copilot.tools.wallet import get_wallet_overview


pytestmark = pytest.mark.skipif(
    not os.environ.get("ALCHEMY_API_KEY"),
    reason="live Alchemy calls require ALCHEMY_API_KEY",
)


VITALIK = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"


def test_wallet_overview_returns_expected_shape():
    result = get_wallet_overview.invoke({"address": VITALIK})
    assert isinstance(result, dict)
    assert result["address"] == VITALIK.lower()
    assert isinstance(result["eth_balance"], (int, float))
    assert result["eth_balance"] >= 0
    assert isinstance(result["erc20_token_count"], int)
    assert result["erc20_token_count"] >= 0


def test_wallet_overview_rejects_bad_address():
    result = get_wallet_overview.invoke({"address": "vitalik.eth"})
    assert "error" in result


def test_recent_transactions_returns_list():
    result = get_recent_transactions.invoke({"address": VITALIK, "limit": 5})
    assert isinstance(result, list)
    assert len(result) <= 5
    for tx in result:
        assert tx["hash"].startswith("0x")
        assert tx["direction"] in {"in", "out", "self"}


def test_recent_transactions_sorted_desc():
    result = get_recent_transactions.invoke({"address": VITALIK, "limit": 10})
    timestamps = [tx["timestamp"] for tx in result if tx["timestamp"]]
    assert timestamps == sorted(timestamps, reverse=True)


def test_recent_transactions_rejects_bad_address():
    result = get_recent_transactions.invoke({"address": "not-an-address", "limit": 5})
    assert isinstance(result, dict)
    assert "error" in result


def test_recent_transactions_clamps_limit():
    result = get_recent_transactions.invoke({"address": VITALIK, "limit": 500})
    assert len(result) <= 50
