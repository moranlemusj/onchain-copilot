import os

import pytest

from copilot.tools.contract import get_contract_source, identify_contract


pytestmark = pytest.mark.skipif(
    not os.environ.get("ALCHEMY_API_KEY"),
    reason="live Alchemy calls require ALCHEMY_API_KEY",
)


VITALIK = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
USDC = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
UNI_V3_ROUTER = "0xE592427A0AEce92De3Edee1F18E0157C05861564"


def test_identify_known_contract():
    result = identify_contract.invoke({"address": USDC})
    assert result["is_contract"] is True
    assert result["known"] is True
    assert result["name"] == "USDC"


def test_identify_eoa():
    result = identify_contract.invoke({"address": VITALIK})
    assert result["is_contract"] is False


def test_identify_unknown_verified_contract_falls_back_to_etherscan():
    if not os.environ.get("ETHERSCAN_API_KEY"):
        pytest.skip("needs ETHERSCAN_API_KEY")
    result = identify_contract.invoke({"address": UNI_V3_ROUTER})
    assert result["is_contract"] is True


def test_identify_rejects_bad_address():
    result = identify_contract.invoke({"address": "nope"})
    assert "error" in result


def test_get_contract_source_rejects_eoa():
    result = get_contract_source.invoke({"address": VITALIK})
    assert "error" in result


@pytest.mark.skipif(
    not os.environ.get("ETHERSCAN_API_KEY"),
    reason="needs ETHERSCAN_API_KEY",
)
def test_get_contract_source_for_usdc():
    result = get_contract_source.invoke({"address": USDC})
    assert result["verified"] is True
    assert result["name"]
    assert result["source_chars"] > 0
    assert result["source_lines"] > 0
