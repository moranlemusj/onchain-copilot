import json
import re

from langchain_core.tools import tool
from web3 import Web3

from ..providers.alchemy import alchemy
from ..providers.etherscan import etherscan
from ..registry import lookup_known


_TX_HASH_RE = re.compile(r"^0x[0-9a-fA-F]{64}$")


def _hex_to_int(x: str | None) -> int | None:
    if x is None:
        return None
    try:
        return int(x, 16)
    except (TypeError, ValueError):
        return None


def _decode_input(to_addr: str, input_data: str) -> dict:
    if not input_data or input_data == "0x" or len(input_data) < 10:
        return {"type": "plain_transfer"}

    selector = input_data[:10]
    result: dict = {"selector": selector}

    if not etherscan.api_key:
        return result

    source = etherscan.get_source(to_addr)
    if not source or not source.get("abi") or source["abi"] == "Contract source code not verified":
        return result

    try:
        abi = json.loads(source["abi"])
        w3 = Web3()
        contract = w3.eth.contract(abi=abi)
        fn, args = contract.decode_function_input(input_data)
        result["function"] = fn.fn_name
        result["args"] = {k: _jsonable(v) for k, v in args.items()}
    except Exception as e:
        result["decode_error"] = str(e)

    return result


def _jsonable(v):
    if isinstance(v, bytes):
        return "0x" + v.hex()
    if isinstance(v, (list, tuple)):
        return [_jsonable(x) for x in v]
    if isinstance(v, dict):
        return {k: _jsonable(x) for k, x in v.items()}
    return v


@tool
def decode_transaction(tx_hash: str) -> dict:
    """Decode an Ethereum transaction into human-readable form.

    Returns: from, to, value (ETH), status (success/fail), gas used,
    and — when the destination's ABI is verified on Etherscan — the
    called function name and its decoded arguments.

    Use this whenever the user asks about a specific transaction hash
    ("what did this tx do?", "why did this tx fail?").
    """
    if not _TX_HASH_RE.match(tx_hash or ""):
        return {"error": f"{tx_hash!r} is not a valid 32-byte transaction hash"}

    tx = alchemy.get_transaction(tx_hash)
    if not tx:
        return {"error": f"no transaction found for {tx_hash}"}
    receipt = alchemy.get_transaction_receipt(tx_hash)

    value_wei = _hex_to_int(tx.get("value")) or 0
    gas_used = _hex_to_int(receipt.get("gasUsed")) if receipt else None
    block_num = _hex_to_int(tx.get("blockNumber"))
    status_hex = receipt.get("status") if receipt else None
    status = "success" if status_hex == "0x1" else "failed" if status_hex == "0x0" else "pending"

    to_addr = (tx.get("to") or "").lower() or None
    called = None
    if to_addr:
        known = lookup_known(to_addr)
        called = {
            "address": to_addr,
            "known": known["name"] if known else None,
        }

    decoded = _decode_input(to_addr, tx.get("input", "0x")) if to_addr else {"type": "contract_creation"}

    return {
        "hash": tx_hash,
        "status": status,
        "from": (tx.get("from") or "").lower(),
        "to": to_addr,
        "value_eth": round(value_wei / 1e18, 6),
        "block": block_num,
        "gas_used": gas_used,
        "called": called,
        "input": decoded,
    }
