import os
import re

import pytest

from copilot.tools.counterparties import get_top_counterparties


pytestmark = pytest.mark.skipif(
    not os.environ.get("ALCHEMY_API_KEY"),
    reason="live Alchemy calls require ALCHEMY_API_KEY",
)


VITALIK = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
ADDR_RE = re.compile(r"^0x[0-9a-f]{40}$")


def test_returns_list_of_counterparties():
    result = get_top_counterparties.invoke({"address": VITALIK, "limit": 5})
    assert isinstance(result, list)
    assert len(result) <= 5
    for entry in result:
        assert ADDR_RE.match(entry["counterparty"])
        assert entry["counterparty"] != VITALIK.lower()
        assert entry["total"] == entry["inbound"] + entry["outbound"]


def test_sorted_by_total_desc():
    result = get_top_counterparties.invoke({"address": VITALIK, "limit": 10})
    totals = [e["total"] for e in result]
    assert totals == sorted(totals, reverse=True)


def test_rejects_bad_address():
    result = get_top_counterparties.invoke({"address": "bogus", "limit": 5})
    assert isinstance(result, dict)
    assert "error" in result


def test_clamps_limit_and_window():
    result = get_top_counterparties.invoke(
        {"address": VITALIK, "limit": 500, "window": 5000}
    )
    assert len(result) <= 50
