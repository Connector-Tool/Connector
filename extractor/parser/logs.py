#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   logs.py
@Time    :   2023/06/19 16:56:39
@Author  :   Kaixin, zzYe
'''
import os

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)
# 上三级目录的路径
parent_path = os.path.dirname(os.path.dirname(os.path.dirname(script_path)))
# 根目录的路径
root_path = os.path.abspath(parent_path)

import sys
sys.path.append(root_path)

import json
import requests
from web3 import Web3

from config import Config


class LogDecoder:
    def __init__(self, mainnet: str='ETH') -> None:
        self.mainnet = mainnet
        self.api_key = Config().SCAN[mainnet].API_KEY[0]
        self.provider = Config().NODE[mainnet][0].API
        self.web3 = Web3(Web3.HTTPProvider(self.provider))
    
    def decode_log(self, tx_hash_arr: list) -> list:
        abi_dict = dict()

        # result_dict = defaultdict(list)
        result = []
        for tx_hash in tx_hash_arr:
            # Get transaction receipt
            receipt = self.web3.eth.get_transaction_receipt(tx_hash)

            tmp_logs = []
            for log in receipt["logs"]:
                # Get smart contract address where log was initiated
                smart_contract = log["address"]
                if smart_contract not in abi_dict:
                    # Get ABI of contract
                    abi_endpoint = f"https://api.etherscan.io/api?module=contract&action=getabi&address={smart_contract}&apikey={self.api_key}"
                    abi = json.loads(requests.get(abi_endpoint).text)
                    abi_dict[smart_contract] = abi

                # Create contract object
                contract = self.web3.eth.contract(smart_contract, abi=abi_dict[smart_contract]["result"])

                # Get event signature of log (first item in topics array)
                receipt_event_signature_hex = self.web3.toHex(log["topics"][0])

                # Find ABI events
                abi_events = [abi for abi in contract.abi if abi["type"] == "event"]

                # Determine which event in ABI matches the transaction log you are decoding
                for event in abi_events:
                    # Get event signature components
                    name = event["name"]
                    inputs = [param["type"] for param in event["inputs"]]
                    inputs = ",".join(inputs)
                    # Hash event signature
                    event_signature_text = f"{name}({inputs})"
                    event_signature_hex = self.web3.toHex(self.web3.keccak(text=event_signature_text))
                    # Find match between log's event signature and ABI's event signature
                    if event_signature_hex == receipt_event_signature_hex:
                        # Decode matching log
                        decoded_logs = contract.events[event["name"]]().processReceipt(receipt)
                        new_decoded_logs = self._del_decoded_logs(decoded_logs)
                        
                        tmp_logs.append(new_decoded_logs)
            result.append(tmp_logs)
        return result

    def _del_decoded_logs(self, decoded_logs):
        new_log = {}
        for log in decoded_logs:
            for key, item in dict(log).items():

                if isinstance(item, type(decoded_logs[0])):
                    item2 = dict(item)
                    for key2, args in item2.items():
                        if isinstance(args, bytes):
                            args2 = self.web3.toHex(args)
                            item2[key2] = args2

                elif isinstance(item, type(decoded_logs[0]['transactionHash'])):
                    item2 = self.web3.toHex(item)
                elif isinstance(item, bytes):
                    item2 = self.web3.toHex(item)
                else:
                    item2 = item
                    
                new_log[key] = item2

        return new_log



