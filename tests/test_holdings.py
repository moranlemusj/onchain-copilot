import os

import pytest

from copilot.tools.holdings import get_token_holdings


pytestmark = pytest.mark.skipif(
    not os.environ.get("ALCHEMY_API_KEY"),
    reason="live Alchemy + Coingecko calls require ALCHEMY_API_KEY",
)


VITALIK = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"


def test_returns_expected_shape():
    result = get_token_holdings.invoke({"address": VITALIK})
    assert result["address"] == VITALIK.lower()
    assert isinstance(result["eth_balance"], (int, float))
    assert isinstance(result["tokens"], list)


def test_tokens_sorted_by_usd_value_desc():
    result = get_token_holdings.invoke({"address": VITALIK})
    tokens = result["tokens"]
    priced = [t for t in tokens if t["usd_value"] is not None]
    values = [t["usd_value"] for t in priced]
    assert values == sorted(values, reverse=True)


def test_rejects_bad_address():
    result = get_token_holdings.invoke({"address": "not-an-address"})
    assert "error" in result
