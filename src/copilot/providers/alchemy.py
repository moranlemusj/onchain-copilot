from typing import Any

import httpx

from ..config import settings


class AlchemyClient:
    def __init__(self, api_key: str, network: str) -> None:
        self.url = f"https://{network}.g.alchemy.com/v2/{api_key}"
        self._client = httpx.Client(timeout=30.0)

    def _rpc(self, method: str, params: list[Any]) -> Any:
        resp = self._client.post(
            self.url,
            json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
        )
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            raise RuntimeError(f"Alchemy RPC error: {data['error']}")
        return data["result"]

    def get_balance_wei(self, address: str) -> int:
        return int(self._rpc("eth_getBalance", [address, "latest"]), 16)

    def get_token_balances(self, address: str) -> list[dict]:
        result = self._rpc("alchemy_getTokenBalances", [address])
        return result.get("tokenBalances", [])

    def get_token_metadata(self, contract: str) -> dict:
        return self._rpc("alchemy_getTokenMetadata", [contract])

    def get_asset_transfers(
        self,
        *,
        from_address: str | None = None,
        to_address: str | None = None,
        order: str = "desc",
        max_count: int = 25,
        categories: list[str] | None = None,
    ) -> list[dict]:
        params: dict[str, Any] = {
            "fromBlock": "0x0",
            "toBlock": "latest",
            "order": order,
            "maxCount": hex(max_count),
            "category": categories or ["external", "erc20", "erc721"],
            "withMetadata": True,
        }
        if from_address:
            params["fromAddress"] = from_address
        if to_address:
            params["toAddress"] = to_address
        result = self._rpc("alchemy_getAssetTransfers", [params])
        return result.get("transfers", [])


alchemy = AlchemyClient(settings.alchemy_api_key, settings.alchemy_network)
