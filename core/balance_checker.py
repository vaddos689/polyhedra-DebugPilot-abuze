from utils import logger
from web3 import Web3
from data.data import DATA


class BalanceChecker:
    def __init__(
            self,
            private_key: str,
    ):
        self.private_key = private_key
        self.w3 = Web3(Web3.HTTPProvider(endpoint_uri=DATA['bsc_testnet']['rpc']))
        self.address = Web3.to_checksum_address(self.w3.eth.account.from_key(private_key=private_key).address)

    def check_balance(self) -> str:
        wallet_address = Web3.to_checksum_address(self.address)
        balance = self.w3.eth.get_balance(account=wallet_address)
        ether_balance = balance / 10 ** 18

        logger.info(f'{wallet_address} | balance: {ether_balance}')

        data = str(f'{wallet_address}:{ether_balance}')

        return data