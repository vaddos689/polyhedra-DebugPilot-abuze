from polyhedra import Polyhedra
from utils import logger
from multiprocessing.dummy import Pool
from utils_json import get_chain_rpc
from client import Client
from web3 import Web3
import json
import time
from core import start_mint_debug_pilot, BalanceChecker


def main(private_key: str):
    client = Client(private_key=private_key, rpc=get_chain_rpc('bsc_testnet'))
    polyhedra = Polyhedra(client=client)
    session = polyhedra.get_session()

    signature: str = polyhedra.get_signature(session=session)
    bearer_token: str = polyhedra.get_bearer_token(session=session, signature=signature)

    session.headers['Authorization'] = f'{bearer_token}'

    nft_ids = polyhedra.get_my_nfts_tbnb(session=session)

    if nft_ids == None:
        logger.error(f'{client.address} | not enough nft`s on wallet')

    else:
        nft_id_for_approve = nft_ids['nft_ids'][0]
        approve_status = polyhedra.check_approved(contract_address='0x95A44287A6D208FA723A899D971d3976cA985ba6', nft_id=nft_id_for_approve)

        if approve_status:
            logger.info(f'{client.address} | nft: {nft_id_for_approve} already approved')

        else:
            tx_hash_bytes = polyhedra.approve_debugpilot_pandra(nft_id=nft_id_for_approve)
            tx_hash = Web3.to_hex(tx_hash_bytes)

            res = client.verif_tx(tx_hash=tx_hash)
            if res:
                logger.success(f'{client.address} | Successful approving nft_id: {nft_id_for_approve} | tx_hash: {tx_hash}')

            else:
                logger.error(f'{client.address} | waiting tx timeout')

        bridge_nft_tx_hash = polyhedra.bridge_nft(contract_address='0x5b2d3EcA3D64CE47A675317D1D290D9B8E87E8Dc', nft_id=nft_id_for_approve)
        res = client.verif_tx(tx_hash=bridge_nft_tx_hash)

        if res:
            logger.success(f'{client.address} | Successful bridge DebugPilot {nft_id_for_approve} to opbnb chain')

        else:
            logger.error(f'{client.address} | waiting tx timeout')

        with open('data.json', 'r') as file:
            data = json.load(file)

        new_dict = {"address": f"{client.address}", "private_key": f"{client.private_key}", "bridge_hash": f"{bridge_nft_tx_hash}"}

        data[0]["data"].append(new_dict)
        with open('data.json', 'w') as file:
            json.dump(data, file)


        logger.info('Start briging tbnb to opbnb')

        tx_hash_bridge_opbnb = polyhedra.bridge_bnb_to_opbnb(contract_address='0x390a91877caad91b675b22888243a25e018e194e')
        res = client.verif_tx(tx_hash=tx_hash_bridge_opbnb)
        if res:
            logger.success(f'{client.address} | Successful bridge DebugPilot {nft_id_for_approve} to opbnb chain')

        else:
            logger.error(f'{client.address} | waiting tx timeout')


        with open('data.json', 'r') as file:
            data = json.load(file)

        search_address = client.address

        for dictionary in data[0]["data"]:
            if dictionary["address"] == search_address:
                bridge_tx_hash = dictionary['bridge_hash']

        mpt_and_block_hash: dict = polyhedra.get_mpt_proof_and_block_hash(bridge_tx_hash=bridge_tx_hash, session=session)
        mpt_proof = mpt_and_block_hash['mpt_proof']
        block_hash = mpt_and_block_hash['block_hash']

        client2 = Client(private_key=client.private_key, rpc='https://opbnb-testnet-rpc.bnbchain.org')

        logger.info('waiting 120 sec for get opbnb tokens on wallet')
        time.sleep(120)

        claim_pandra_on_opbnb_tx_hash = polyhedra.claim_bridged_nft(client=client2, contract_address='0x4cc870c8fdfbc512943fe60c29c98d515f868ebf', mpt_proof=mpt_proof, block_hash=block_hash)
        logger.success(f'{client.address} | successful claim pandra on opbnb | {claim_pandra_on_opbnb_tx_hash}')

        with open('wallets_with_opbnb_pandra.txt', 'a') as file:
            file.write(f'{client.address}\n')


def balance_checker_start(private_key: str) -> str:
    balance_checker = BalanceChecker(private_key=private_key)
    balance_and_wallet: str = balance_checker.check_balance()

    return balance_and_wallet


if __name__ == '__main__':
    with open('private_keys.txt', 'r') as file:
        private_keys = file.read().split('\n')

    logger.info(f'Загружено {len(private_keys)} аккаунтов')

    time.sleep(0.01)

    user_action: int = int(input('\n1. Mint DebugPilot'
                                 '\n2. Bridge and claim on opbnb'
                                 '\n3. Check tbnb balance'
                                 '\nВыберите ваше действие: '))

    time.sleep(0.01)

    threads: int = int(input('Threads: '))
    print('')
    match user_action:
        case 1:
            with Pool(processes=threads) as executor:
                executor.map(start_mint_debug_pilot, private_keys)

        case 2:
            with Pool(processes=threads) as executor:
                executor.map(main, private_keys)

        case 3:
            all_data = []
            for private_key in private_keys:
                data = balance_checker_start(private_key)
                all_data.append(data)

            with open('tbnb_balance.txt', 'w') as file:
                for data in all_data:
                    file.write(f'{data}\n')

        case _:
            pass

    logger.info('Работа успешно завершена')
    input('\nPress Enter To Exit..')