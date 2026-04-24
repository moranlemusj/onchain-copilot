from functools import lru_cache

from langchain_core.tools import tool

from ..providers.alchemy import alchemy
from ..providers.coingecko import coingecko
from ..validation import validate_eth_address


_MAX_TOKENS_IN_OUTPUT = 20
_MAX_TOKENS_TO_PRICE = 75


@lru_cache(maxsize=10000)
def _metadata(contract: str) -> dict:
    return alchemy.get_token_metadata(contract)


@tool
def get_token_holdings(address: str) -> dict:
    """Return a wallet's ETH balance and its most valuable ERC-20 holdings,
    priced in USD via Coingecko where available.

    Output includes native ETH (with USD value), the top tokens by USD value,
    and a portfolio total. Tokens that Coingecko doesn't price are listed
    with usd_value=null.

    Use this when the user wants to know what a wallet actually holds or what
    it's worth, not just how many distinct tokens there are.
    """
    try:
        address = validate_eth_address(address)
    except ValueError as e:
        return {"error": str(e)}

    eth_balance = alchemy.get_balance_wei(address) / 1e18
    eth_price = coingecko.eth_price_usd()
    eth_value = round(eth_balance * eth_price, 2) if eth_price else None

    raw_balances = alchemy.get_token_balances(address)
    nonzero: list[tuple[str, int]] = []
    for t in raw_balances:
        bal_hex = t.get("tokenBalance")
        if not bal_hex:
            continue
        bal = int(bal_hex, 16)
        if bal > 0:
            nonzero.append((t["contractAddress"].lower(), bal))

    to_price = nonzero[:_MAX_TOKENS_TO_PRICE]
    prices = coingecko.token_prices_usd([c for c, _ in to_price])

    entries: list[dict] = []
    for contract, raw_bal in to_price:
        meta = _metadata(contract)
        decimals = meta.get("decimals") or 0
        symbol = meta.get("symbol")
        name = meta.get("name")
        balance = raw_bal / (10 ** decimals) if decimals else raw_bal
        price = prices.get(contract)
        usd_value = round(balance * price, 2) if price else None
        entries.append({
            "contract": contract,
            "symbol": symbol,
            "name": name,
            "balance": round(balance, 6),
            "usd_value": usd_value,
        })

    entries.sort(key=lambda e: (e["usd_value"] is None, -(e["usd_value"] or 0)))
    shown = entries[:_MAX_TOKENS_IN_OUTPUT]
    hidden = entries[_MAX_TOKENS_IN_OUTPUT:]
    hidden_value = sum(e["usd_value"] for e in hidden if e["usd_value"])

    token_total = sum(e["usd_value"] for e in entries if e["usd_value"])
    portfolio_total = round(
        (eth_value or 0) + token_total, 2
    ) if (eth_value is not None) else None

    return {
        "address": address,
        "eth_balance": round(eth_balance, 6),
        "eth_value_usd": eth_value,
        "tokens": shown,
        "tokens_not_shown": {
            "count": len(hidden),
            "approx_usd_value": round(hidden_value, 2) if hidden_value else None,
        } if hidden else None,
        "portfolio_value_usd": portfolio_total,
    }
