from langchain_core.tools import tool

from ..providers.alchemy import alchemy
from ..validation import validate_eth_address


def _direction(tx_from: str, tx_to: str | None, address: str) -> str:
    f = (tx_from or "").lower()
    t = (tx_to or "").lower()
    if f == address and t == address:
        return "self"
    if f == address:
        return "out"
    return "in"


@tool
def get_recent_transactions(address: str, limit: int = 10) -> list[dict] | dict:
    """Return the N most recent transactions involving this wallet, in both
    directions. Each entry includes hash, timestamp, direction (in/out/self),
    counterparty, value, and asset symbol.

    Use this when the user wants to know what a wallet has been doing recently.
    Call get_wallet_overview first if you need a high-level summary.

    Args:
        address: 0x-prefixed 42-char Ethereum address.
        limit: how many transactions to return (default 10, max 50).
    """
    try:
        address = validate_eth_address(address)
    except ValueError as e:
        return {"error": str(e)}

    limit = max(1, min(limit, 50))

    outgoing = alchemy.get_asset_transfers(from_address=address, max_count=limit)
    incoming = alchemy.get_asset_transfers(to_address=address, max_count=limit)

    seen: set[str] = set()
    merged = []
    for tx in outgoing + incoming:
        h = tx.get("hash")
        if not h or h in seen:
            continue
        seen.add(h)
        merged.append(tx)

    merged.sort(key=lambda t: int(t.get("blockNum", "0x0"), 16), reverse=True)

    result = []
    for tx in merged[:limit]:
        direction = _direction(tx.get("from"), tx.get("to"), address)
        counterparty = (
            tx.get("to") if direction == "out" else tx.get("from")
        )
        result.append({
            "hash": tx.get("hash"),
            "timestamp": tx.get("metadata", {}).get("blockTimestamp"),
            "direction": direction,
            "counterparty": counterparty,
            "value": tx.get("value"),
            "asset": tx.get("asset"),
            "category": tx.get("category"),
        })

    return result
