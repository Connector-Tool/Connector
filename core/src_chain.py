#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   src_chain.py
@Time    :   2023/06/17 09:36:25
@Author  :   zzYe
'''
import numpy as np
import pandas as pd

from joblib import load
from trained_model.structure_embedding import TxStructureVector
from trained_model.word_embedding import TxWordVector
from config import Config


class DepositLocator:
    def __init__(self, bridge: str, srcnet: str, txlist: list) -> None:
        self.bridge = bridge
        self.srcnet = srcnet
        
        self.txlist = txlist
        
        self.STRUCTURE_EMBED_SIZE = 16
        self.SENTENCE_EMBED_SIZE = 36
        
    def filter_deposit(self) -> dict:
        txlist = pd.DataFrame(self.txlist).rename(
            columns={'tx_hash': 'hash', 'from_address': 'address_from', 'to_address': 'address_to'})
        # Get sturcture vectors
        structure_vecs = TxStructureVector(
            raw_tx=txlist
        ).count_motif()

        txlist = pd.DataFrame(txlist).rename(
            columns={'hash': 'srcTxhash'})

        # Get sentences vectors
        sentence_vecs = TxWordVector(
            txlist=txlist
        ).wordembedd()

        feature = []
        for key, val in structure_vecs.items():
            structure_feat = [val[i] if i in val else 0.0 for i in range(self.STRUCTURE_EMBED_SIZE)]
            sentence_feat = [i for arr in sentence_vecs[key] for i in arr]
            sentence_feat = sentence_feat + [0.0 for _ in range(self.SENTENCE_EMBED_SIZE - len(sentence_feat))]

            feature.append(structure_feat + sentence_feat)
        
        feature = np.array(feature)

        # 加载模型
        loaded_model = load(Config.MODEL_DIR + "/model.pkl")

        # 使用模型进行预测
        y_pred = loaded_model.predict(feature)
        idx = np.where(y_pred == 1)[0]
        return [x for i, x in enumerate(self.txlist) if i in idx]

    
