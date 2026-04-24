import json
from typing import Any

import httpx

from ..config import settings


def unwrap_source(source: str) -> str:
    """Etherscan returns multi-file contracts in one of two wrapper formats:
    a double-braced Standard JSON Input ({{ ... }}) or a plain JSON object
    with a `sources` key. Both wrap a dict of path -> {content}. Flatten them
    into concatenated Solidity text so downstream chunkers see real code, not
    JSON. Single-file contracts (raw .sol) pass through unchanged.
    """
    if not source:
        return source

    stripped = source.strip()
    if not (stripped.startswith("{") and stripped.endswith("}")):
        return source
    if stripped.startswith("{{") and stripped.endswith("}}"):
        stripped = stripped[1:-1]

    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        return source
    if not isinstance(parsed, dict):
        return source
    sources = parsed.get("sources")
    if not isinstance(sources, dict):
        return source

    return _flatten_sources(sources) or source


def _flatten_sources(sources: dict) -> str:
    parts = []
    for path, blob in sources.items():
        content = blob.get("content") if isinstance(blob, dict) else None
        if content:
            parts.append(f"// === {path} ===\n{content}")
    return "\n\n".join(parts)


class EtherscanClient:
    BASE = "https://api.etherscan.io/v2/api"
    CHAIN_ID = 1

    def __init__(self, api_key: str | None) -> None:
        self.api_key = api_key
        self._client = httpx.Client(timeout=30.0)

    def _require_key(self) -> str:
        if not self.api_key:
            raise RuntimeError(
                "ETHERSCAN_API_KEY is not set — "
                "get one at https://etherscan.io/apis and add it to .env"
            )
        return self.api_key

    def _get(self, params: dict[str, Any]) -> dict:
        params = {
            **params,
            "chainid": self.CHAIN_ID,
            "apikey": self._require_key(),
        }
        resp = self._client.get(self.BASE, params=params)
        resp.raise_for_status()
        data = resp.json()
        status = data.get("status")
        message = data.get("message") or ""
        if status == "0" and message not in ("No records found", "OK"):
            raise RuntimeError(f"Etherscan error: {data.get('result') or data}")
        return data

    def get_source(self, address: str) -> dict | None:
        """Return {name, compiler, source, abi, optimization} for a verified
        contract, or None if the contract isn't verified."""
        data = self._get({
            "module": "contract",
            "action": "getsourcecode",
            "address": address,
        })
        results = data.get("result") or []
        if not results:
            return None
        entry = results[0]
        source = entry.get("SourceCode") or ""
        if not source.strip():
            return None
        return {
            "name": entry.get("ContractName"),
            "compiler": entry.get("CompilerVersion"),
            "source": unwrap_source(source),
            "abi": entry.get("ABI"),
            "optimization": entry.get("OptimizationUsed") == "1",
            "proxy": entry.get("Proxy") == "1",
            "implementation": entry.get("Implementation") or None,
        }


etherscan = EtherscanClient(settings.etherscan_api_key)
