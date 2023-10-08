#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : loader.py
@Time    : 2023/07/25 14:59
@Author  : zzYe

"""
import os
import json
import pandas as pd

from config import Config
from typing import Tuple, List, Dict
from utils import ChainEnum, BridgeEnum


def load_validation_dataset(
        src_chain: ChainEnum,
        dst_chain: ChainEnum,
        bridge: BridgeEnum
) -> Tuple[List[Dict], List[Dict]]:
    """
    :param src_chain: Name of chain
    :param dst_chain: Name of chain
    :param bridge: Name of bridge
    :return: (Sample, Label)
    """
    dir_path = Config().VALIDATION_DIR + f"/{src_chain.value}-{dst_chain.value}/{bridge.value}"
    sample_path, label_path = dir_path + "/sample.json", dir_path + "/label.csv"

    if (not os.path.isfile(label_path)) or (not os.path.isfile(sample_path)):
        raise FileNotFoundError(f'sample file or label file does not exist.')

    with open(sample_path, 'r') as f:
        sample = json.load(f)

    label = pd.read_csv(label_path)[['srcTxhash', 'dstTxhash']].to_dict("records")

    return sample, label


def load_first_phrase_dataset(
        src_chain: ChainEnum,
        bridge: BridgeEnum
) -> List[Dict]:
    """
    :param src_chain: Name of chain
    :param bridge: Name of bridge
    :return: Sample
    """
    dir_path = Config().FIRST_PHRASE_DIR
    sample_path = dir_path + f"/{bridge.value}_{src_chain.value}.csv"

    if not os.path.isfile(sample_path):
        raise FileNotFoundError(f'sample file does not exist.')

    sample = pd.read_csv(sample_path)[['Net', 'hash', 'value', 'timeStamp']]
    sample = sample.rename(columns={
        'Net': 'srcChain',
        'hash': 'srcTxhash',
        'value': 'srcValue',
        'timeStamp': 'srcTimestamp'
    }).drop_duplicates(subset='srcTxhash')

    return sample.to_dict("records")


def load_first_phrase_bridge_address(
        bridge: BridgeEnum
) -> List[Dict]:
    """
    :param bridge: Name of bridge
    :return: Sample
    """
    dir_path = Config().FIRST_PHRASE_DIR
    sample_path = dir_path + f"/{bridge.value}.csv"

    if not os.path.isfile(sample_path):
        raise FileNotFoundError(f'sample file does not exist.')

    sample = pd.read_csv(sample_path)[['address', 'srcnet']]

    return sample.to_dict("records")


def load_normalization_map():
    return pd.read_csv(f"{Config().MODEL_DIR}/normalization_map.csv")
