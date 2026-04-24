import pytest

from copilot.validation import validate_eth_address


VITALIK = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"


def test_accepts_valid_address_and_lowercases():
    assert validate_eth_address(VITALIK) == VITALIK.lower()


def test_accepts_already_lowercase():
    assert validate_eth_address(VITALIK.lower()) == VITALIK.lower()


@pytest.mark.parametrize(
    "bad",
    [
        "",
        "vitalik.eth",
        "0xnothex",
        "0x1234",
        "d8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
        "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA9604",
        "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA960455",
    ],
)
def test_rejects_invalid(bad):
    with pytest.raises(ValueError):
        validate_eth_address(bad)


def test_rejects_non_string():
    with pytest.raises(ValueError):
        validate_eth_address(12345)  # type: ignore[arg-type]
