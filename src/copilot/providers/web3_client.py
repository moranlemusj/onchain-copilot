from web3 import Web3

from ..config import settings

_rpc_url = f"https://{settings.alchemy_network}.g.alchemy.com/v2/{settings.alchemy_api_key}"
w3 = Web3(Web3.HTTPProvider(_rpc_url))
