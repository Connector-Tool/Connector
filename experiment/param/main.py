#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : main.py
@Time    : 2023/07/16 13:41
@Author  : zzYe

"""
import json
import numpy as np
import pandas as pd

from tqdm import tqdm

from config import SpiderNetEnum
from core.dst_chain import WithdrawLocator
from extractor import BridgeSpider
from utils import ChainEnum, BridgeEnum
from utils.loader import load_validation_dataset
from utils.str import hash_str
from utils.dict import expand_dict
from utils.block import get_block_number_by_timestamp
from config import Config

if __name__ == '__main__':
    res_arr, case_arr = [], []
    cur_bridge = "Celer"
    interval = int(90 * 60)
    space_size = 0
    src, dst = ChainEnum.ETH, ChainEnum.BNB
    spider_net = SpiderNetEnum.BNB
    res_report = {
        'src': f"{src.value}",
        'dst': f"{dst.value}",
        'bridge': f"{cur_bridge}",
        'timeInterval': interval,
    }

    for bridge in BridgeEnum.__members__.values():
        if bridge.value != cur_bridge:
            continue

        sample, label = load_validation_dataset(
            src_chain=src,
            dst_chain=dst,
            bridge=bridge,
        )

        y_true = {
            e['srcTxhash']: e['dstTxhash'] for e in label
        }

        un_hit_arr = []
        hit_num, total_num = 0., 0.
        # BLOCK_NUMBER_SPACING = int(2048)

        for idx, item in enumerate(tqdm(sample)):
            total_num += 1
            timestamp = item['timestamp']
            try:
                start_dst_blk = get_block_number_by_timestamp(dst.value, timestamp)
                end_dst_blk = get_block_number_by_timestamp(dst.value, timestamp+interval)

                dst_txs = BridgeSpider(
                    net=dst.value,
                    spider_net=spider_net.value,
                    addresses=[item['args']['receiver']],
                    start_blk=start_dst_blk,
                    end_blk=end_dst_blk
                ).search_for_bridge()
                space_size += len(dst_txs)
            except Exception:
                start_dst_blk = 0
                end_dst_blk = 0
                dst_txs = pd.DataFrame()
                case_arr.append({
                    'bridge': bridge.value,
                    'srcTxHash': item['txhash'],
                    'timestamp': item['timestamp']
                })

            src_txs = pd.DataFrame([expand_dict(item, '.')])

            res = WithdrawLocator(
                src_txs=src_txs,
                dst_txs=dst_txs
            ).search_withdraw()

            if y_true[res[0]['srcTxHash']] == res[0]['dstTxHash']:
                hit_num += 1
            else:
                un_hit_arr.append([res[0]['srcTxHash'], y_true[res[0]['srcTxHash']], res[0]['dstTxHash'], hash_str(
                    str(start_dst_blk) + "," + str(end_dst_blk) + " " + ', '.join(
                        [item['args']['receiver']])
                )])

        print(bridge.value + " accuracy: ", hit_num/total_num)
        res_report['accuracy'] = hit_num/total_num
        res_report['spaceSize'] = space_size
        res_arr.append({
            'bridge': bridge.value,
            'accuracy': hit_num/total_num
        })
        # pd.DataFrame(case_arr).to_csv("../data/" + bridge.value + "_case_arr.csv", sep=',',
        #                                           encoding='utf-8', index=False)
        pd.DataFrame(np.array(un_hit_arr)).to_csv(f"{Config().EXPER_DIR}/param/res/{src.value}_{dst.value}_{bridge.value}_unhit_tmp.csv",
                                                  sep=',', encoding='utf-8', index=False)

    with open(f"{Config().EXPER_DIR}/param/res/{src.value}_{dst.value}_{cur_bridge}_{interval}_res_report.json", "w") as f:
        json.dump([res_report], f, indent=4)

    # with open("param_res.json", 'w') as f:
    #     json.dump(res_arr, f, indent=4)






