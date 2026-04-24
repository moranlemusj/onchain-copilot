import os

import pytest

from copilot.tools.ens import resolve_ens


pytestmark = pytest.mark.skipif(
    not os.environ.get("ALCHEMY_API_KEY"),
    reason="live RPC calls require ALCHEMY_API_KEY",
)


VITALIK_ADDR = "0xd8da6bf26964af9d7eed9e03e53415d37aa96045"


def test_forward_resolves_vitalik():
    result = resolve_ens.invoke({"identifier": "vitalik.eth"})
    assert result.get("address", "").lower() == VITALIK_ADDR
    assert result.get("ens") == "vitalik.eth"


def test_reverse_resolves_vitalik():
    result = resolve_ens.invoke({"identifier": VITALIK_ADDR})
    assert result.get("address") == VITALIK_ADDR
    assert result.get("ens") in ("vitalik.eth", None)


def test_unknown_ens_name_returns_error():
    result = resolve_ens.invoke(
        {"identifier": "this-name-is-very-unlikely-to-exist-12345.eth"}
    )
    assert "error" in result


def test_bad_address_returns_error():
    result = resolve_ens.invoke({"identifier": "0xnothex"})
    assert "error" in result
