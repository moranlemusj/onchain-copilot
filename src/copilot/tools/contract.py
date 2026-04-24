from langchain_core.tools import tool

from ..providers.alchemy import alchemy
from ..providers.etherscan import etherscan
from ..registry import lookup_known
from ..validation import validate_eth_address


def _is_contract(address: str) -> bool:
    return alchemy.classify_address(address)["is_contract"]


@tool
def identify_contract(address: str) -> dict:
    """Identify a contract address. First checks a curated registry of
    well-known contracts (Uniswap, Aave, USDC, Lido, Seaport, etc.) for an
    instant hit. If not recognized, checks whether the address has code
    deployed and, when possible, returns the verified contract name from
    Etherscan.

    Use this whenever the user asks "what is this contract" or "is this
    contract X" before reaching for the full source.
    """
    try:
        address = validate_eth_address(address)
    except ValueError as e:
        return {"error": str(e)}

    known = lookup_known(address)
    if known:
        return {"address": address, "is_contract": True, "known": True, **known}

    if not _is_contract(address):
        return {
            "address": address,
            "is_contract": False,
            "known": False,
            "note": "this address has no deployed code — it's an EOA",
        }

    source = etherscan.get_source(address) if etherscan.api_key else None
    if source:
        return {
            "address": address,
            "is_contract": True,
            "known": False,
            "name": source["name"],
            "compiler": source["compiler"],
            "proxy": source.get("proxy", False),
            "implementation": source.get("implementation"),
            "verified": True,
        }

    return {
        "address": address,
        "is_contract": True,
        "known": False,
        "verified": False,
        "note": "contract bytecode exists but source is unverified on Etherscan",
    }


@tool
def get_contract_source(address: str) -> dict:
    """Fetch the verified Solidity source code for a contract from Etherscan.

    Use this when the user wants to see or understand the code of a contract,
    OR as a prerequisite before calling search_contract_context (which RAGs
    over this source).

    Returns contract name, compiler version, proxy/implementation info, and
    a size summary. The full source is not returned inline — use
    search_contract_context to query it.
    """
    try:
        address = validate_eth_address(address)
    except ValueError as e:
        return {"error": str(e)}

    if not _is_contract(address):
        return {"error": f"{address} has no deployed code — it's an EOA, not a contract"}

    source = etherscan.get_source(address)
    if not source:
        return {
            "address": address,
            "verified": False,
            "error": "source is not verified on Etherscan",
        }

    raw = source["source"]
    return {
        "address": address,
        "verified": True,
        "name": source["name"],
        "compiler": source["compiler"],
        "optimization": source["optimization"],
        "proxy": source.get("proxy", False),
        "implementation": source.get("implementation"),
        "source_chars": len(raw),
        "source_lines": raw.count("\n") + 1,
        "hint": (
            "source is now available for retrieval — call "
            "search_contract_context(address, question) to ask about it"
        ),
    }
