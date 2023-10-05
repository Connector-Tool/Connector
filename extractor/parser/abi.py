#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   abi.py
@Time    :   2023/06/17 19:11:21
@Author  :   Kaixin, zzYe
'''
import json
import requests

# from etherscan.contracts import Contract
from config import RequestConfig
request_config = RequestConfig()


class ABIFetcher:
    def __init__(self, contract_address: str, mainnet: str='ETH') -> None:
        self.contract_address = contract_address
        self.mainnet = mainnet
        
    def abi_fetch(self):
        # Function to fetch the ABI of a contract
        ABI_ENDPOINT = f'https://api.etherscan.io/api?module=contract&action=getabi&address={self.contract_address}&apikey={request_config.API_KEY["eth"][0]}'
        
        response = requests.get(ABI_ENDPOINT)
        response_json = json.loads(response.text)

        # 从响应中获取 ABI 信息
        abi = response_json['result']

        return abi
