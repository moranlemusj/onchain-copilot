from langchain_core.tools import tool

from ..providers.web3_client import w3
from ..validation import validate_eth_address


@tool
def resolve_ens(identifier: str) -> dict:
    """Resolve an ENS name to an Ethereum address, or an address to its primary
    ENS name.

    - If `identifier` is an ENS name like 'vitalik.eth', returns the address it
      resolves to.
    - If `identifier` is a 0x-prefixed address, returns the primary ENS name for
      that address (or null if none is set).

    Use this to turn ENS names into addresses before calling any other wallet
    or transaction tool.
    """
    s = identifier.strip()
    if s.startswith("0x"):
        try:
            addr = validate_eth_address(s)
        except ValueError as e:
            return {"error": str(e)}
        try:
            name = w3.ens.name(w3.to_checksum_address(addr))
        except Exception as e:
            return {"error": f"reverse ENS lookup failed: {e}"}
        return {"address": addr, "ens": name}

    try:
        addr = w3.ens.address(s)
    except Exception as e:
        return {"error": f"ENS resolution failed: {e}"}
    if addr is None:
        return {"error": f"could not resolve ENS name {s!r}"}
    return {"ens": s, "address": addr.lower()}
