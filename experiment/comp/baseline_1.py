#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : baseline_1.py
@Time    : 2023/09/07 21:31
@Author  : zzYe

"""

import json
import pandas as pd

from tqdm import tqdm

from config import SpiderNetEnum
from experiment.comp.baseline_dst import WithdrawLocator
from extractor import BridgeSpider
from utils import ChainEnum, BridgeEnum
from utils.loader import load_validation_dataset, load_first_phrase_dataset, load_first_phrase_bridge_address
from utils.block import get_block_number_by_timestamp
from config import Config

if __name__ == '__main__':
    cur_bridge = "Multi"
    baseline = "baseline01"
    interval = int(120 * 60)
    space_size = 0

    src, dst = ChainEnum.ETH, ChainEnum.BNB
    spider_net = SpiderNetEnum.BNB
    res_report = {
        'src': f"{src.value}",
        'dst': f"{dst.value}",
        'bridge': f"{cur_bridge}",
        'interval': interval
    }

    for bridge in BridgeEnum.__members__.values():
        if bridge.value != cur_bridge:
            continue

        bridge_address_arr = load_first_phrase_bridge_address(
            bridge=bridge
        )

        sample = load_first_phrase_dataset(
            src_chain=src,
            bridge=bridge
        )

        for s in sample:
            if "srcTxhash" in s:
                s["txhash"] = s.pop("srcTxhash")
            s["srcChain"] = src.value
            s["dstChain"] = dst.value

        _, label = load_validation_dataset(
            src_chain=src,
            dst_chain=dst,
            bridge=bridge,
        )

        y_true = {
            e['srcTxhash']: e['dstTxhash'] for e in label
        }

        un_hit_arr = []
        hit_num, total_num = 0., 0.

        for idx, item in enumerate(tqdm(sample)):
            if item['txhash'] not in y_true:
                continue

            total_num += 1
            timestamp = item['srcTimestamp']
            try:
                start_dst_blk = get_block_number_by_timestamp(dst.value, timestamp)
                end_dst_blk = get_block_number_by_timestamp(dst.value, timestamp+interval)
                # end_dst_blk = 99999999

                dst_txs = BridgeSpider(
                    net=dst.value,
                    spider_net=spider_net.value,
                    addresses=[e['address'] for e in bridge_address_arr if e['srcnet'].lower() == dst.value.lower()],
                    start_blk=start_dst_blk,
                    end_blk=end_dst_blk
                ).search_for_bridge()
                space_size += len(dst_txs)
            except Exception:
                start_dst_blk = 0
                end_dst_blk = 0
                dst_txs = pd.DataFrame()

            src_txs = pd.DataFrame([item])

            res = WithdrawLocator(
                src_txs=src_txs,
                dst_txs=dst_txs
            ).search_withdraw()

            if res[0]['srcTxHash'] in y_true and y_true[res[0]['srcTxHash']] == res[0]['dstTxHash']:
                hit_num += 1

        res_report['accuracy'] = hit_num / total_num
        res_report['space_size'] = space_size
        print(bridge.value + " accuracy: ", res_report['accuracy'])
        print("space_size: ", space_size)

        with open(f"{Config().EXPER_DIR}/comp/res/{baseline}_{src.value}_{dst.value}_{cur_bridge}_res_report.json", "w") as f:
            json.dump([res_report], f, indent=4)