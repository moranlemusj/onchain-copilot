from langchain_core.tools import tool

from ..providers.alchemy import alchemy
from ..registry import lookup_known
from ..validation import validate_eth_address


@tool
def get_address_overview(address: str) -> dict:
    """Return a lightweight overview of any Ethereum address — EOA or contract.

    The `is_contract` flag tells you what kind of address it is:
      - false: this is a wallet (EOA). Prefer wallet tools next:
          get_token_holdings, get_recent_transactions, get_top_counterparties.
      - true: this has deployed code. Prefer contract tools next:
          identify_contract, get_contract_source, search_contract_context.

    Call this FIRST whenever you're investigating an unknown 0x address.
    """
    try:
        address = validate_eth_address(address)
    except ValueError as e:
        return {"error": str(e)}

    classification = alchemy.classify_address(address)
    is_contract = classification["is_contract"]
    eth_balance = alchemy.get_balance_wei(address) / 1e18
    known = lookup_known(address)

    result: dict = {
        "address": address,
        "is_contract": is_contract,
        "eth_balance": round(eth_balance, 6),
    }
    if classification["delegation"]:
        result["eip7702_delegation"] = classification["delegation"]
    if known:
        result["known"] = known

    if not is_contract:
        token_balances = alchemy.get_token_balances(address)
        nonzero = [
            t for t in token_balances
            if t.get("tokenBalance") and int(t["tokenBalance"], 16) > 0
        ]
        recent = alchemy.get_asset_transfers(from_address=address, max_count=1)
        result["erc20_token_count"] = len(nonzero)
        result["last_outbound_activity"] = (
            recent[0].get("metadata", {}).get("blockTimestamp") if recent else None
        )

    return result
