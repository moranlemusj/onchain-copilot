KNOWN_CONTRACTS: dict[str, dict] = {
    "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": {
        "name": "WETH9",
        "protocol": "Wrapped Ether",
        "kind": "token",
    },
    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": {
        "name": "USDC",
        "protocol": "Circle",
        "kind": "token",
    },
    "0xdac17f958d2ee523a2206206994597c13d831ec7": {
        "name": "USDT",
        "protocol": "Tether",
        "kind": "token",
    },
    "0x6b175474e89094c44da98b954eedeac495271d0f": {
        "name": "DAI",
        "protocol": "MakerDAO",
        "kind": "token",
    },
    "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599": {
        "name": "WBTC",
        "protocol": "Wrapped BTC",
        "kind": "token",
    },
    "0xe592427a0aece92de3edee1f18e0157c05861564": {
        "name": "Uniswap V3 SwapRouter",
        "protocol": "Uniswap V3",
        "kind": "router",
    },
    "0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45": {
        "name": "Uniswap V3 SwapRouter02",
        "protocol": "Uniswap V3",
        "kind": "router",
    },
    "0x7a250d5630b4cf539739df2c5dacb4c659f2488d": {
        "name": "Uniswap V2 Router02",
        "protocol": "Uniswap V2",
        "kind": "router",
    },
    "0x1f98431c8ad98523631ae4a59f267346ea31f984": {
        "name": "Uniswap V3 Factory",
        "protocol": "Uniswap V3",
        "kind": "factory",
    },
    "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2": {
        "name": "Aave V3 Pool",
        "protocol": "Aave V3",
        "kind": "lending",
    },
    "0xae7ab96520de3a18e5e111b5eaab095312d7fe84": {
        "name": "Lido stETH",
        "protocol": "Lido",
        "kind": "lst",
    },
    "0x00000000006c3852cbef3e08e8df289169ede581": {
        "name": "OpenSea Seaport 1.1",
        "protocol": "OpenSea",
        "kind": "marketplace",
    },
    "0x00000000000000adc04c56bf30ac9d3c0aaf14dc": {
        "name": "OpenSea Seaport 1.5",
        "protocol": "OpenSea",
        "kind": "marketplace",
    },
    "0x00000000000001ad428e4906ae43d8f9852d0dd6": {
        "name": "OpenSea Seaport 1.6",
        "protocol": "OpenSea",
        "kind": "marketplace",
    },
    "0x00000000219ab540356cbb839cbe05303d7705fa": {
        "name": "ETH2 Deposit Contract",
        "protocol": "Ethereum",
        "kind": "system",
    },
    "0x00000000000c2e074ec69a0dfb2997ba6c7d2e1e": {
        "name": "ENS Registry",
        "protocol": "ENS",
        "kind": "registry",
    },
    "0xd9a442856c234a39a81a089c06451ebaa4306a72": {
        "name": "EigenLayer StrategyManager",
        "protocol": "EigenLayer",
        "kind": "restaking",
    },
}


def lookup_known(address: str) -> dict | None:
    return KNOWN_CONTRACTS.get(address.lower())
