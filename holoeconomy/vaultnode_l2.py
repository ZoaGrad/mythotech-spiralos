from web3 import Web3
from eth_account import Account
import json

L2_ABI = json.loads('''[{"inputs":[{"internalType":"bytes32","name":"root","type":"bytes32"}],"name":"seal","outputs":[],"stateMutability":"nonpayable","type":"function"}]''')

class VaultNodeL2:
    def __init__(self, rpc: str, contract_addr: str, private_key: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc))
        self.contract = self.w3.eth.contract(address=contract_addr, abi=L2_ABI)
        self.acct = Account.from_key(private_key)

    def seal_on_l2(self, merkle_root: str) -> str:
        tx = self.contract.functions.seal(merkle_root).build_transaction({
            'from': self.acct.address,
            'nonce': self.w3.eth.get_transaction_count(self.acct.address),
            'gas': 200000,
            'gasPrice': self.w3.to_wei('1', 'gwei')
        })
        signed = self.acct.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt.transactionHash.hex()