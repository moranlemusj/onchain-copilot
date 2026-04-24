import httpx


class CoingeckoClient:
    BASE = "https://api.coingecko.com/api/v3"
    BATCH_SIZE = 25

    def __init__(self) -> None:
        self._client = httpx.Client(timeout=15.0)

    def _get(self, path: str, params: dict) -> dict | None:
        try:
            resp = self._client.get(f"{self.BASE}{path}", params=params)
            resp.raise_for_status()
            return resp.json()
        except (httpx.HTTPError, ValueError):
            return None

    def eth_price_usd(self) -> float | None:
        data = self._get("/simple/price", {"ids": "ethereum", "vs_currencies": "usd"})
        if not data:
            return None
        return data.get("ethereum", {}).get("usd")

    def token_prices_usd(self, contracts: list[str]) -> dict[str, float]:
        """Return {contract_lowercase: usd_price} for any contracts Coingecko knows.
        Returns what it can — missing batches are silently skipped rather than raising."""
        if not contracts:
            return {}
        prices: dict[str, float] = {}
        for batch in _chunks(contracts, self.BATCH_SIZE):
            data = self._get(
                "/simple/token_price/ethereum",
                {"contract_addresses": ",".join(batch), "vs_currencies": "usd"},
            )
            if not data:
                continue
            for contract, payload in data.items():
                usd = payload.get("usd")
                if usd is not None:
                    prices[contract.lower()] = usd
        return prices


def _chunks(items: list, size: int):
    for i in range(0, len(items), size):
        yield items[i : i + size]


coingecko = CoingeckoClient()
