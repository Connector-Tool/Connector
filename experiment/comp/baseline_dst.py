#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : baseline_dst.py
@Time    : 2023/09/08 19:24
@Author  : zzYe

"""
import pandas as pd
from config import Config


class WithdrawLocator:
    """withdrawal transaction tracking class
    """

    def __init__(self, src_txs: pd.DataFrame, dst_txs: pd.DataFrame) -> None:
        self.src_txs = src_txs
        self.dst_txs = dst_txs

    def _match_amount(self, df: pd.DataFrame, threshold: float) -> pd.DataFrame:
        df.loc[:, 'value'] = pd.to_numeric(df['value'], errors='coerce').fillna(0)
        df.loc[:, 'srcValue'] = pd.to_numeric(df['srcValue'], errors='coerce').fillna(0)

        df = df[(df['value'] >= 0) & (df['srcValue'] > 0)].copy()

        if not df.empty:
            df.loc[:, 'amount_diff'] = df['srcValue'] - df['value']
            df = df[df['amount_diff'] >= 0].copy()

            if not df.empty:
                df.loc[:, 'threshold'] = df.apply(
                    lambda x: x['amount_diff'] / x['srcValue'], axis=1
                ).drop(columns=['amount_diff'])

                while df[df['threshold'] <= threshold].empty and threshold < 1:
                    threshold *= 2

                df = df[df['threshold'] <= threshold].copy()

        return df

    def _match_timestamp(self, df: pd.DataFrame, threshold: float, key: str) -> pd.DataFrame:
        df.loc[:, 'srcTimestamp'] = pd.to_numeric(df['srcTimestamp'], errors='coerce').fillna(0)
        df.loc[:, 'timeStamp'] = pd.to_numeric(df['timeStamp'], errors='coerce').fillna(0)

        df = df[df['srcTimestamp'] < df['timeStamp']].copy()

        if not df.empty:
            df.loc[:, 'time_diff'] = df.apply(
                lambda x: x['timeStamp'] - x['srcTimestamp'], axis=1
            )

            # df = df[df['time_diff'] <= threshold].copy()

            cur_threshold = threshold
            while df[df['time_diff'] <= cur_threshold].empty and cur_threshold < threshold * 2:
                cur_threshold += cur_threshold * 0.1

            df = df[df['time_diff'] <= cur_threshold].copy().groupby(key).apply(
                lambda x: x.sort_values(by='time_diff')
            )

            df = df.drop(columns='time_diff').reset_index(drop=True)

        return df

    def search_withdraw(self, fulloutput=False) :
        res_df = pd.DataFrame()
        # for group in self.src_tx_group:
        #     src_chain, dst_chain = group[0]
        #     src_txs = group[1].reset_index(drop=True)

        # 交叉拼接
        tmp_df = self.src_txs.merge(
            self.dst_txs, how='cross'
        )
        if tmp_df.empty:
            if 'hash' not in tmp_df.columns:
                tmp_df.insert(loc=len(tmp_df.columns), column='hash', value='')
        else:
            tmp_df['contractAddress'] = tmp_df['contractAddress'].fillna('')

        # Rule 1: Match timeStamp
        if not tmp_df.empty:
            TIME_THRESHOLD = 1800  # In 30 mins
            tmp_df = self._match_timestamp(tmp_df, threshold=TIME_THRESHOLD, key='txhash')

        # Rule 2: Match amount
        if not tmp_df.empty:
            FEE_THRESHOLD = 0.03
            tmp_df = self._match_amount(tmp_df, threshold=FEE_THRESHOLD)

        # Save unique result
        tmp_df = tmp_df.drop_duplicates(subset=['txhash'], keep='first')
        tmp_df = self.src_txs[['txhash']].merge(
            tmp_df, left_on='txhash',
            right_on='txhash', how='left'
        )
        res_df = pd.concat([res_df, tmp_df], ignore_index=True)

        # (4) Save tx pair arr
        res_df = res_df[['srcChain', 'txhash', 'dstChain', 'hash']]
        res_df = res_df.rename(columns={
            'args.srcChain': 'srcnet',
            'txhash': 'srcTxHash',
            'args.dstChain': 'dstnet',
            'hash': 'dstTxHash',
        })

        return res_df.to_dict('records')