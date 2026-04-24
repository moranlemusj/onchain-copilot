import os

import pytest

from copilot.tools.decode import decode_transaction


pytestmark = pytest.mark.skipif(
    not os.environ.get("ALCHEMY_API_KEY"),
    reason="live Alchemy calls require ALCHEMY_API_KEY",
)


def _fetch_real_tx_hash() -> str:
    from copilot.providers.alchemy import alchemy
    # Uniswap V3 Router sees tx every block; grab a recent one.
    transfers = alchemy.get_asset_transfers(
        to_address="0xE592427A0AEce92De3Edee1F18E0157C05861564",
        max_count=1,
    )
    if not transfers:
        pytest.skip("no recent transfers found to sample a hash from")
    return transfers[0]["hash"]


def test_rejects_bad_hash():
    result = decode_transaction.invoke({"tx_hash": "0x1234"})
    assert "error" in result


def test_unknown_hash_returns_error():
    fake = "0x" + "0" * 64
    result = decode_transaction.invoke({"tx_hash": fake})
    assert "error" in result


def test_decodes_real_transaction():
    tx_hash = _fetch_real_tx_hash()
    result = decode_transaction.invoke({"tx_hash": tx_hash})
    assert result["hash"] == tx_hash
    assert result["status"] in {"success", "failed", "pending"}
    assert result["from"].startswith("0x")
    assert result["block"] is not None
    assert result["called"] is not None
