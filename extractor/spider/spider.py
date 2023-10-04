#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : spider.py
@Time    : 2023/07/16 20:03
@Author  : zzYe

"""

import os
import json
import shutil
import pandas as pd

from config import Config
from utils.str import hash_str


class BridgeSpider:
    def __init__(self, net: str, spider_net: str,
                 addresses: list, start_blk: int, end_blk: int) -> None:
        self.net = net
        self.spider_net = spider_net
        self.addresses = addresses
        self.start_blk = start_blk
        self.end_blk = end_blk

        self._dir = os.path.dirname(os.path.abspath(__file__))
        self._data_dir = Config().DATA_DIR

        self._bridge_tx_dir = self._data_dir + '/BridgeTx'
        if not os.path.exists(self._bridge_tx_dir):
            os.makedirs(self._bridge_tx_dir)

    def search_for_bridge(self) -> pd.DataFrame:
        if not self._is_hash_file_exists():
            self._create_json_file()
            self._search()
            self._merge_tx_file()
            self._remove_tmp_file()
        return pd.read_csv(
            self._bridge_tx_dir + '/' + self._get_hash_file_name()
        )

    def _is_hash_file_exists(self) -> bool:
        file_path = self._bridge_tx_dir + "/" + self._get_hash_file_name()
        return os.path.isfile(file_path)

    def _get_hash_file_name(self, _type='.csv') -> str:
        return hash_str(
            _str=str(self.start_blk) + "," + str(self.end_blk) + " " + ', '.join(self.addresses)
        ) + _type

    def _create_json_file(self):
        self._source_dir = self._data_dir + '/Source'
        if not os.path.exists(self._source_dir):
            os.makedirs(self._source_dir)

        self._tx_output_dir = self._data_dir + '/TxOutput'
        if not os.path.exists(self._tx_output_dir):
            os.makedirs(self._tx_output_dir)

        data = []
        for item in self.addresses:
            data.append({
                "source": item,
                "types": "external,internal,erc20",
                "fields": "id,hash,from,to,value,timeStamp,blockNumber,symbol,contractAddress,input,decimals",
                "start_blk": str(self.start_blk),
                "end_blk": str(self.end_blk),
                "out": self._tx_output_dir,
                "depth": 1,
                # "auto_page": True
            })

        self._json_file = self._source_dir + '/' + self.net + '.json'
        with open(self._json_file, 'w') as f:
            json.dump(data, f)

    def _search(self) -> None:
        try:
            command = 'scrapy crawl txs.' + self.spider_net + '.bfs -a file=' + self._json_file
            os.chdir(self._dir + "/BlockchainSpider")
            os.system(command)
        except Exception as e:
            print(e)

    def _merge_tx_file(self):
        path = self._tx_output_dir
        data_train = pd.DataFrame()
        for i in os.listdir(path):
            if i[-3:] == 'csv':
                data_tmp = pd.read_csv(path + '/' + i, engine='python', encoding='utf-8')
                data_tmp.insert(loc=0, column='Address', value=i[:-4])
            else:
                data_tmp = pd.read_excel(path + '/' + i)
                data_tmp.insert(loc=0, column='Address', value=i[:-4])

            data_train = data_train._append(data_tmp)

        data_train.insert(loc=0, column='Net', value=self.net)
        data_train.to_csv(self._bridge_tx_dir + "/" + self._get_hash_file_name())

    def _remove_tmp_file(self):
        if os.path.exists(self._source_dir):
            shutil.rmtree(self._source_dir)

        if os.path.exists(self._tx_output_dir):
            shutil.rmtree(self._tx_output_dir)

        self._json_file = None
