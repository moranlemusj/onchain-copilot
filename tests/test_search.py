import os

import pytest

from copilot.tools.search import search_contract_context


pytestmark = pytest.mark.skipif(
    not (os.environ.get("ALCHEMY_API_KEY") and os.environ.get("ETHERSCAN_API_KEY")),
    reason="RAG tests require ALCHEMY_API_KEY and ETHERSCAN_API_KEY",
)


WETH9 = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"


def test_rejects_bad_address():
    result = search_contract_context.invoke(
        {"address": "nope", "question": "what does this do"}
    )
    assert "error" in result


def test_returns_chunks_for_weth():
    result = search_contract_context.invoke(
        {"address": WETH9, "question": "how does deposit work", "k": 3}
    )
    assert result["address"] == WETH9.lower()
    assert "chunks" in result
    assert 1 <= len(result["chunks"]) <= 3
    for chunk in result["chunks"]:
        assert "content" in chunk
        assert chunk["content"]


def test_second_call_reuses_index():
    search_contract_context.invoke(
        {"address": WETH9, "question": "deposit", "k": 2}
    )
    second = search_contract_context.invoke(
        {"address": WETH9, "question": "withdraw", "k": 2}
    )
    assert second["indexed_this_call"] is False


def test_clamps_k():
    result = search_contract_context.invoke(
        {"address": WETH9, "question": "anything", "k": 500}
    )
    assert len(result["chunks"]) <= 10
