#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : block.py
@Time    : 2023/07/17 9:24
@Author  : zzYe

"""
import os
import requests
import pandas as pd

from config import Config
from pydantic import BaseModel


class TBMap(BaseModel):
    """
    Timestamp -> BlockNumber
    """
    net: str = ''
    timestamp: int = 0
    block_number: int = 0
    closest: str = 'before'


def init_tb_maps() -> pd.DataFrame():
    data_dir = Config().DATA_DIR

    block_dir = data_dir + '/Block'
    if not os.path.exists(block_dir):
        os.makedirs(block_dir)

    dtype = {attr: type(value) for attr, value in TBMap().__dict__.items()}
    df = pd.DataFrame(columns=[
        attr for attr in TBMap().__dict__.keys()
    ]).astype(dtype)
    for val in Config().BLOCK_FILE.values():
        if not os.path.exists(val.TBMAP):
            pd.DataFrame(columns=[
                attr for attr in TBMap().__dict__.keys()
            ]).astype(dtype).to_csv(val.TBMAP, index=False)
        else:
            df = pd.concat([
                df, pd.read_csv(val.TBMAP, dtype=dtype)
            ], ignore_index=True)

    return df


tb_maps = init_tb_maps()


def add_item_to_tb_maps(item: TBMap):
    global tb_maps

    new_row = pd.Series({attr: value for attr, value in item.__dict__.items()})
    dtype = {attr: type(value) for attr, value in item.__dict__.items()}
    for val in Config().BLOCK_FILE.values():
        if val.NET == item.net:
            tmp = pd.read_csv(val.TBMAP, dtype=dtype)
            tmp = tmp._append(new_row, ignore_index=True)
            tmp.to_csv(val.TBMAP, index=False)
            break

    tb_maps = tb_maps._append(new_row, ignore_index=True)


def get_block_number_by_timestamp(chain: str, timestamp: int, closest='before') -> int:
    global tb_maps

    if not tb_maps[
        (tb_maps['net'] == chain) &
        (tb_maps['timestamp'] == timestamp) &
        (tb_maps['closest'] == closest)
    ].empty:
        return tb_maps[
            (tb_maps['net'] == chain) &
            (tb_maps['timestamp'] == timestamp) &
            (tb_maps['closest'] == closest)].iloc[0, :].loc['block_number']

    api = Config().SCAN[chain].API
    params = {
        'module': 'block', 'action': 'getblocknobytime', 'timestamp': str(timestamp),
        'closest': 'before', 'apikey': Config().SCAN[chain].API_KEY[0]
    }
    headers = Config().REQUEST_HEADERS

    try:
        response = requests.get(api, params=params, headers=headers)
        response.raise_for_status()
        block_number = int(response.json()['result'])
        add_item_to_tb_maps(
            TBMap(
                net=chain,
                timestamp=timestamp,
                block_number=block_number,
                closest=closest
            )
        )
        return block_number
    except requests.exceptions.RequestException as e:
        print(f'Error: {e}')
        return None