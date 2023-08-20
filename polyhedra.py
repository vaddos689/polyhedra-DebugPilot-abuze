from eth_account.messages import encode_defunct
from utils import logger
from pyuseragents import random as random_useragent
from web3 import Web3
import tls_client
import tls_client.sessions
from random import choice
from abis.config import DEBUG_PILOT_ABI
from client import Client
from models import TokenAmount


headers = {
    'accept': '*/*',
    'accept-language': 'ru,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://zkbridge.com',
    'referer': 'https://zkbridge.com/',
    'user-agent': random_useragent()
}


class Polyhedra:
    def __init__(self,
                 client: Client):
        self.client = client

    def get_signature(self, session: tls_client.sessions.Session):
        public_key = Web3.to_checksum_address(self.client.w3.eth.account.from_key(private_key=self.client.private_key).address)

        url = "https://api.zkbridge.com/api/signin/validation_message"

        json = {
            'publicKey': public_key.lower(),
        }

        try:
            response = session.post(
                url=url,
                headers=headers,
                json=json,
            )

            if response.status_code == 200:
                message = encode_defunct(text=response.json()["message"])

                signed_message = self.client.w3.eth.account.sign_message(message, self.client.private_key)

                signature = self.client.w3.to_hex(signed_message.signature)

                logger.success(f"{self.client.address} | Signature recieved")

                return signature

        except Exception as e:
            logger.exception(f"{self.client.address} | Exception occurred when generating a signature: {e}")

    def get_session(self) -> tls_client.sessions.Session:
        session = tls_client.Session(client_identifier=choice(['chrome_103',
                                                               'chrome_104',
                                                               'chrome_105',
                                                               'chrome_106',
                                                               'chrome_107',
                                                               'chrome_108',
                                                               'chrome109',
                                                               'Chrome110',
                                                               'chrome111',
                                                               'chrome112',
                                                               'firefox_102',
                                                               'firefox_104',
                                                               'firefox108',
                                                               'Firefox110',
                                                               'opera_89',
                                                               'opera_90']),
                                     random_tls_extension_order=True)
        session.headers.update(headers)

        return session

    def get_bearer_token(self, session: tls_client.sessions.Session, signature: str) -> str:
        url = "https://api.zkbridge.com/api/signin"

        json = {
            'publicKey': self.client.address.lower(),
            'signedMessage': signature,
        }

        try:
            response = session.post(
                url=url,
                headers=headers,
                json=json,
            )

            if response.status_code == 200:
                auth_token = str(f'Bearer {response.json()["token"]}')

                logger.success(f"{self.client.address} | bearer token recieved")

                return auth_token

        except Exception as e:
            logger.exception(f"{self.client.address} | Exception occurred with the bearer token: {e}")

    def get_my_nfts_tbnb(self, session: tls_client.sessions.Session) -> str:
        url = "https://api.zkbridge.com/api/nfts?ERC721=true&pageStart=0&pageSize=8&chainId=97"

        try:
            response = session.get(
                url=url,
                headers=headers,
            )

            if response.status_code == 200:
                if response.json()['data'] == None:
                    return None

                else:
                    nft_ids = []

                    for nft in response.json()['data']:
                        if nft['tokenDetail']['name'] == 'Pandra: DebugPilot':
                            nft_id = nft['tokenDetail']['contractTokenId']
                            nft_ids.append(nft_id)

                    logger.success(f"{self.client.address} | successfully extracted information about nft`s on wallet")

                    data = {
                        'total': f'{response.json()["total"]}',
                        'nft_ids': nft_ids
                    }

                return data

        except Exception as e:
            logger.exception(f"{self.client.address} | Exception occurred with the get nft`s on wallet: {e}")

    def approve_debugpilot_pandra(self, nft_id: str) -> str:
        debug_pilot_contract_address = '0x95a44287a6d208fa723a899d971d3976ca985ba6'

        spender = Web3.to_checksum_address('0x5b2d3EcA3D64CE47A675317D1D290D9B8E87E8Dc')

        tx_hash = self.client.approve(token_address=debug_pilot_contract_address, spender=spender, nft_id=nft_id)

        return tx_hash

    def check_approved(self, contract_address: str, nft_id: str) -> bool:
        approved_wallet = self.client.get_apprroved(contract_address=contract_address, nft_id=nft_id)
        if approved_wallet == '0x0000000000000000000000000000000000000000':
            return False

        else:
            return True

    def bridge_nft(self, contract_address: str, nft_id: str):
        contract = self.client.w3.eth.contract(
            abi=self.client.bridge_abi,
            address=Web3.to_checksum_address(contract_address)
        )

        recipientChain = 116
        first_two_characters = self.client.address[:2]
        rest_of_string = self.client.address[2:]
        recipient = f'{first_two_characters}000000000000000000000000{rest_of_string}'

        value = Web3.to_wei(0.01, 'ether')

        token_contract = Web3.to_checksum_address('0x95A44287A6D208FA723A899D971d3976cA985ba6')

        tx_hash_bytes =  self.client.send_transaction(
            to=contract_address,
            data=contract.encodeABI('transferNFT',
                                    args=(
                                        token_contract,
                                        nft_id,
                                        recipientChain,
                                        recipient
                                    )),
            value=value
        )

        tx_hash = Web3.to_hex(tx_hash_bytes)

        return tx_hash

    def bridge_bnb_to_opbnb(self, contract_address: str):
        contract = self.client.w3.eth.contract(
            abi=self.client.bridge_opbnb,
            address=Web3.to_checksum_address(contract_address)
        )

        dstChainId_ = 116
        recipient_ = self.client.address
        amount_ = Web3.to_wei(0.01, 'ether')

        tx_hash_bytes = self.client.send_transaction(
            to=contract_address,
            data=contract.encodeABI('l2BridgeETH',
                                    args=(
                                        dstChainId_,
                                        amount_,
                                        recipient_,
                                    )),
            value=amount_
        )

        tx_hash = Web3.to_hex(tx_hash_bytes)

        return tx_hash

    def get_mpt_proof_and_block_hash(self, bridge_tx_hash: str, session: tls_client.sessions.Session) -> dict:
        url = "https://api.zkbridge.com/api/v2/receipt_proof/generate"

        json = {
            'tx_hash': bridge_tx_hash,
            'chain_id': 103,
        }

        try:
            response = session.post(
                url=url,
                headers=headers,
                json=json,
            )

            if response.status_code == 200:
                mpt_proof = response.json()['proof_blob']
                block_hash = response.json()['block_hash']

                data = {
                    'mpt_proof': f'{mpt_proof}',
                    'block_hash': f'{block_hash}',
                }

                logger.success(f"{self.client.address} | mpt_proof and block_hash successful recieved")

                return data

        except Exception as e:
            logger.exception(f"{self.client.address} | Exception occurred when generating a signature: {e}")

    def claim_bridged_nft(self, contract_address: str, mpt_proof: str, block_hash: str, client):
        contract = client.w3.eth.contract(
            abi=self.client.opbnb_claim_nft_abi,
            address=Web3.to_checksum_address(contract_address)
        )

        srcChainId = 103
        srcBlockHash = block_hash
        logIndex = 1
        mptProof = mpt_proof

        tx_hash_bytes = client.send_transaction(
            to=contract_address,
            data=contract.encodeABI('validateTransactionProof',
                                    args=(
                                        srcChainId,
                                        srcBlockHash,
                                        logIndex,
                                        mptProof,
                                    )),
        )

        tx_hash = Web3.to_hex(tx_hash_bytes)

        return tx_hash
