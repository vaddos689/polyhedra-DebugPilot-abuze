import json
from utils import logger
from web3 import Web3
import time
import random

BNB_TESTNET_RPC = 'https://data-seed-prebsc-1-s2.bnbchain.org:8545'
BNB_TESTNET_PANDRA_CONTRACT = '0x95A44287A6D208FA723A899D971d3976cA985ba6'


class Mint:
    def __init__(self,
                 private_key: str):
        self.private_key = private_key
        self.w3 = Web3(Web3.HTTPProvider(endpoint_uri=BNB_TESTNET_RPC))

    def mint_pandra(self):
        logger.info('start mint_pandra')

        wallet_address = Web3.to_checksum_address(self.w3.eth.account.from_key(private_key=self.private_key).address)

        abi = json.load(open('Debugpilot.json'))

        contract_address = Web3.to_checksum_address(BNB_TESTNET_PANDRA_CONTRACT)
        contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=abi
        )

        while True:
            try:
                mint_txn = contract.functions.mint(
                ).build_transaction({
                    'chainId': self.w3.eth.chain_id,
                    'nonce': self.w3.eth.get_transaction_count(wallet_address),
                    'from': Web3.to_checksum_address(wallet_address),
                    'gasPrice': self.w3.eth.gas_price
                })

                gas_limit = self.w3.eth.estimate_gas(mint_txn)
                mint_txn['gas'] = gas_limit
                signed_swap_txn = self.w3.eth.account.sign_transaction(mint_txn, private_key=self.private_key)
                swap_txn_hash = self.w3.eth.send_raw_transaction(signed_swap_txn.rawTransaction)

                # Check status of TX

                while True:
                    try:
                        if self.w3.eth.get_transaction_receipt(swap_txn_hash)['status'] != 1:
                            time.sleep(random.randint(10, 20))
                        else:
                            time.sleep(random.randint(20, 50))
                            break
                    except Exception as err:
                        time.sleep(random.randint(20, 30))

                logger.success(f"Transaction: https://testnet.bscscan.com/tx/{swap_txn_hash.hex()}")

                tx_receipt = self.w3.eth.get_transaction_receipt(swap_txn_hash)
                transfer_event = contract.events.Transfer()

                transfer_logs = transfer_event.process_receipt(tx_receipt)

                nft_id = transfer_logs[0]['args']['tokenId']

            except Exception as error:
                if not "execution reverted: You have reached the claim limit." in str(error):
                    logger.info('Mint next panda')
                else:
                    logger.success('Successful mint all pandas on testnet bnb')

                    with open('wallets_with_debugpilot.txt', 'r') as file:
                        if f'{wallet_address}' in file.read():
                            pass
                        else:
                            with open('wallets_with_debugpilot.txt', 'a') as file:
                                file.write(f'{wallet_address}\n')

                    break

    def check_balance(self) -> float:
        logger.info('start check_balance')
        wallet_address = Web3.to_checksum_address(self.w3.eth.account.from_key(private_key=self.private_key).address)
        balance = self.w3.eth.get_balance(wallet_address)
        eth_balance = balance / 10 ** 18

        return eth_balance


    def main(self):
        wallet_address = Web3.to_checksum_address(self.w3.eth.account.from_key(private_key=self.private_key).address)
        balance = self.check_balance()

        if balance > 0:
            logger.info(f'{wallet_address} | balance {balance} | начинаю минт')

            self.mint_pandra()

        else:
            logger.error(f'Недостаточный баланс на кошельке {wallet_address}, перехожу к следующему')
            pass


def start_mint_debug_pilot(private_key: str):

    return Mint(private_key=private_key).main()