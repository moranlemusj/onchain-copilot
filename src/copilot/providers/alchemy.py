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

    def get_code(self, address: str) -> str:
        """Return the deployed bytecode at `address`. '0x' or '0x0' means EOA."""
        return self._rpc("eth_getCode", [address, "latest"])

    def classify_address(self, address: str) -> dict:
        """Return {is_contract, delegation} — treats EIP-7702 delegated EOAs
        as wallets (is_contract=False) but records the delegation target."""
        code = self.get_code(address) or "0x"
        if code in ("0x", "0x0"):
            return {"is_contract": False, "delegation": None}
        if code.startswith("0xef0100") and len(code) == 2 + 6 + 40:
            return {"is_contract": False, "delegation": "0x" + code[8:48].lower()}
        return {"is_contract": True, "delegation": None}

    def get_transaction(self, tx_hash: str) -> dict | None:
        return self._rpc("eth_getTransactionByHash", [tx_hash])

    def get_transaction_receipt(self, tx_hash: str) -> dict | None:
        return self._rpc("eth_getTransactionReceipt", [tx_hash])

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
