from langchain_core.tools import tool

from ..rag import ensure_contract_indexed, search_contract
from ..validation import validate_eth_address


@tool
def search_contract_context(address: str, question: str, k: int = 5) -> dict:
    """Search a verified contract's Solidity source for passages relevant to a
    specific question.

    On first use for an address, this automatically fetches the source from
    Etherscan, chunks it Solidity-aware (function/contract-level boundaries),
    embeds each chunk with Google text-embedding-004, and persists the index
    locally. Subsequent calls reuse it.

    Use this whenever you need to reason about actual contract code — e.g.
    "is there a mint function", "who can pause this", "how is the fee
    calculated", "what access-control modifier gates function X".

    Returns top-k most semantically relevant chunks along with metadata.
    """
    try:
        address = validate_eth_address(address)
    except ValueError as e:
        return {"error": str(e)}

    ingest = ensure_contract_indexed(address)
    if ingest["status"] == "error":
        return {"error": ingest["error"], "address": address}

    k = max(1, min(k, 10))
    chunks = search_contract(address, question, k=k)
    return {
        "address": address,
        "question": question,
        "indexed_this_call": ingest["status"] == "indexed",
        "chunks": chunks,
    }
