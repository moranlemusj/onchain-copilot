import re

_ETH_ADDRESS_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")


def validate_eth_address(address: str) -> str:
    """Return the address lowercased if valid, else raise ValueError."""
    if not isinstance(address, str):
        raise ValueError(f"address must be a string, got {type(address).__name__}")
    if not _ETH_ADDRESS_RE.match(address):
        raise ValueError(
            f"{address!r} is not a valid Ethereum address — "
            "expected 0x followed by 40 hex characters"
        )
    return address.lower()
