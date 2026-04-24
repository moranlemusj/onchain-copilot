from pathlib import Path

from langchain_chroma import Chroma
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter

from .config import settings
from .providers.embeddings import embeddings
from .providers.etherscan import etherscan


_splitter = RecursiveCharacterTextSplitter.from_language(
    Language.SOL, chunk_size=1500, chunk_overlap=200
)

_stores: dict[str, Chroma] = {}


def _store_for(address: str) -> Chroma:
    if address not in _stores:
        _stores[address] = Chroma(
            collection_name=f"contract_{address[2:14]}",
            embedding_function=embeddings,
            persist_directory=str(Path(settings.vector_store_dir) / address),
        )
    return _stores[address]


def _is_empty(store: Chroma) -> bool:
    try:
        return store._collection.count() == 0
    except Exception:
        return True


def ensure_contract_indexed(address: str) -> dict:
    """Fetch the verified source of `address` if not already indexed, then
    chunk it Solidity-aware, embed via Google's text-embedding-004, and
    persist in a per-contract Chroma collection."""
    address = address.lower()
    store = _store_for(address)

    if not _is_empty(store):
        return {"status": "already_indexed", "address": address}

    source = etherscan.get_source(address)
    if not source:
        return {
            "status": "error",
            "address": address,
            "error": "contract source is not verified on Etherscan",
        }

    docs = _splitter.create_documents(
        [source["source"]],
        metadatas=[{
            "address": address,
            "contract_name": source.get("name") or "",
        }],
    )
    store.add_documents(docs)

    return {
        "status": "indexed",
        "address": address,
        "name": source.get("name"),
        "chunks": len(docs),
    }


def search_contract(address: str, question: str, k: int = 5) -> list[dict]:
    address = address.lower()
    store = _store_for(address)
    hits = store.similarity_search(question, k=k)
    return [
        {"content": h.page_content, "metadata": h.metadata}
        for h in hits
    ]
