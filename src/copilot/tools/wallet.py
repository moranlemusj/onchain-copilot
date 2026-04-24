from langchain_core.tools import tool

from ..providers.alchemy import alchemy


@tool
def get_wallet_overview(address: str) -> dict:
    """Return a high-level summary of an Ethereum wallet: native ETH balance,
    the number of distinct ERC-20 tokens held (non-zero balances), and the
    timestamp of the most recent outbound transfer.

    Call this FIRST whenever a user asks about any wallet address — it gives
    you enough context to decide which deeper tools to call next. The address
    must be a 0x-prefixed 42-character hex string. ENS names must be resolved
    before calling this tool.
    """
    eth_balance = alchemy.get_balance_wei(address) / 1e18

    token_balances = alchemy.get_token_balances(address)
    nonzero = [
        t for t in token_balances
        if t.get("tokenBalance") and int(t["tokenBalance"], 16) > 0
    ]

    recent = alchemy.get_asset_transfers(from_address=address, max_count=1)
    last_activity = (
        recent[0].get("metadata", {}).get("blockTimestamp") if recent else None
    )

    return {
        "address": address,
        "eth_balance": round(eth_balance, 6),
        "erc20_token_count": len(nonzero),
        "last_outbound_activity": last_activity,
    }
