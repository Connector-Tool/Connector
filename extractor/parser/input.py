#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   input.py
@Time    :   2023/06/17 19:19:00
@Author  :   zzYe, Kaixin
'''
import sys
import json

from functools import lru_cache
from web3 import Web3
from web3.auto import w3
from eth_utils import to_hex

class InputDecoder:
    def __init__(self, input: str, contract_address: str, abi: str, mainnet: str = 'ETH') -> None:
        self.input = input
        self.contract_address = contract_address
        self.abi = abi
        self.mainnet = mainnet
    
    def decode_input(self):
        return decode_tx(self.contract_address, self.input, self.abi)

def decode_tuple(t, target_field):
    output = dict()
    for i in range(len(t)):
        if isinstance(t[i], (bytes, bytearray)):
            output[target_field[i]['name']] = to_hex(t[i])
        elif isinstance(t[i], (tuple)):
            output[target_field[i]['name']] = decode_tuple(t[i], target_field[i]['components'])
        else:
            output[target_field[i]['name']] = t[i]
    return output

def decode_list_tuple(l, target_field):
    output = l
    for i in range(len(l)):
        output[i] = decode_tuple(l[i], target_field)
    return output

def decode_list(l):
    output = l
    for i in range(len(l)):
        if isinstance(l[i], (bytes, bytearray)):
            output[i] = to_hex(l[i])
        else:
            output[i] = l[i]
    return output

def convert_to_hex(arg, target_schema):
    """
    utility function to convert byte codes into human readable and json serializable data structures
    """
    output = dict()
    for k in arg:
        if isinstance(arg[k], (bytes, bytearray)):
            output[k] = to_hex(arg[k])
        elif isinstance(arg[k], (list)) and len(arg[k]) > 0:
            target = [a for a in target_schema if 'name' in a and a['name'] == k][0]
            if target['type'] == 'tuple[]':
                target_field = target['components']
                output[k] = decode_list_tuple(arg[k], target_field)
            else:
                output[k] = decode_list(arg[k])
        elif isinstance(arg[k], (tuple)):
            target_field = [a['components'] for a in target_schema if 'name' in a and a['name'] == k][0]
            output[k] = decode_tuple(arg[k], target_field)
        else:
            output[k] = arg[k]
    return output

@lru_cache(maxsize=None)
def _get_contract(address, abi):
    """
    This helps speed up execution of decoding across a large dataset by caching the contract object
    It assumes that we are decoding a small set, on the order of thousands, of target smart contracts
    """
    if isinstance(abi, (str)):
        abi = json.loads(abi)

    contract = w3.eth.contract(address=Web3.toChecksumAddress(address), abi=abi)
    return (contract, abi)

def decode_tx(address, input_data, abi):
    """
    需要输入address、input_data、abi
    """
    if abi is not None:
        try:
            (contract, abi) = _get_contract(address, abi)
            func_obj, func_params = contract.decode_function_input(input_data)
            target_schema = [a['inputs'] for a in abi if 'name' in a and a['name'] == func_obj.fn_name][0]
            decoded_func_params = convert_to_hex(func_params, target_schema)
            return (func_obj.fn_name, json.dumps(decoded_func_params), json.dumps(target_schema))
        except:
            e = sys.exc_info()[0]
            return ('decode error', repr(e), None)
    else:
        return ('no matching abi', None, None)