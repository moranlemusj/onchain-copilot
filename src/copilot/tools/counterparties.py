from collections import defaultdict

from langchain_core.tools import tool

from ..providers.alchemy import alchemy
from ..validation import validate_eth_address


@tool
def get_top_counterparties(address: str, limit: int = 10, window: int = 200) -> list[dict] | dict:
    """Return the addresses this wallet interacts with most frequently.

    Fetches the last `window` transfers in each direction and ranks
    counterparties by number of interactions. Each entry includes the
    counterparty address, the total number of transfers, and how many were
    inbound vs. outbound.

    Use this when the user wants to know who a wallet deals with most.

    Args:
        address: 0x-prefixed Ethereum address.
        limit: how many top counterparties to return (default 10, max 50).
        window: how many transfers per direction to consider (default 200, max 1000).
    """
    try:
        address = validate_eth_address(address)
    except ValueError as e:
        return {"error": str(e)}

    limit = max(1, min(limit, 50))
    window = max(10, min(window, 1000))

    outgoing = alchemy.get_asset_transfers(from_address=address, max_count=window)
    incoming = alchemy.get_asset_transfers(to_address=address, max_count=window)

    stats: dict[str, dict] = defaultdict(lambda: {"in": 0, "out": 0})
    for tx in outgoing:
        to = (tx.get("to") or "").lower()
        if to and to != address:
            stats[to]["out"] += 1
    for tx in incoming:
        frm = (tx.get("from") or "").lower()
        if frm and frm != address:
            stats[frm]["in"] += 1

    ranked = [
        {
            "counterparty": addr,
            "total": counts["in"] + counts["out"],
            "inbound": counts["in"],
            "outbound": counts["out"],
        }
        for addr, counts in stats.items()
    ]
    ranked.sort(key=lambda e: e["total"], reverse=True)
    return ranked[:limit]
