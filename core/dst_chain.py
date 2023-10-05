#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : dst_chain.py
@Time    : 2023/07/15 19:47
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
        self.src_tx_group = src_txs.groupby([
            'args.srcChain', 'args.dstChain'
        ])

        chains = set()
        for group in self.src_tx_group:
            src_chain, dst_chain = group[0]
            chains.add(src_chain)
            chains.add(dst_chain)

        self.decimal_dict = dict()
        for chain in chains:
            _dict = pd.read_csv(Config().TOKEN_FILE[chain]).set_index('address')['decimal'].to_dict()
            _dict = {str(k).lower(): v for k, v in _dict.items()}
            self.decimal_dict[chain] = _dict

    def _match_receiver(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[df['args.receiver'].str.lower() == df['to'].str.lower()].copy()

    def _match_tx_type(self, df: pd.DataFrame) -> pd.DataFrame:
        df_1 = df[(df['args.asset_s'] == '') & (df['contractAddress'] == '')].copy()
        df_2 = df[(df['args.asset_s'] != '') & (df['contractAddress'] != '')].copy()

        return pd.concat([df_1, df_2], axis=0)

    def _match_amount(self, df: pd.DataFrame, src_chain: str, dst_chain: str, threshold: float) -> pd.DataFrame:
        df.loc[:, 'value'] = pd.to_numeric(df['value'], errors='coerce').fillna(0)
        df.loc[:, 'args.amount'] = pd.to_numeric(df['args.amount'], errors='coerce').fillna(0)

        df.loc[:, 'value'] = df.apply(
            lambda x: x['value'] / pow(10, self.decimal_dict[dst_chain][str(x['contractAddress']).lower()])
            if str(x['contractAddress']).lower() in self.decimal_dict[dst_chain]
            else x['value'], axis=1
        )

        df.loc[:, 'args.amount'] = df.apply(
            lambda x: x['args.amount'] / pow(10, self.decimal_dict[src_chain][x['args.asset_s'].lower()])
            if x['args.asset_s'].lower() in self.decimal_dict[src_chain]
            else x['args.amount'], axis=1
        )

        df = df[(df['value'] > 0) & (df['args.amount'] > 0)].copy()

        if not df.empty:
            df.loc[:, 'amount_diff'] = df['args.amount'] - df['value']
            df = df[df['amount_diff'] >= 0].copy()

            if not df.empty:
                df.loc[:, 'threshold'] = df.apply(
                    lambda x: x['amount_diff'] / x['args.amount'], axis=1
                ).drop(columns=['amount_diff'])

                while df[df['threshold'] <= threshold].empty and threshold < 1:
                    threshold *= 2

                df = df[df['threshold'] <= threshold].copy()

        return df

    def _match_timestamp(self, df: pd.DataFrame, threshold: float, key: str) -> pd.DataFrame:
        df.loc[:, 'timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce').fillna(0)
        df.loc[:, 'timeStamp'] = pd.to_numeric(df['timeStamp'], errors='coerce').fillna(0)

        df = df[df['timestamp'] < df['timeStamp']].copy()

        if not df.empty:
            df.loc[:, 'time_diff'] = df.apply(
                lambda x: x['timeStamp'] - x['timestamp'], axis=1
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

    def _match_asset_type(self, df: pd.DataFrame) -> pd.DataFrame:
        if 'args.asset_d' in df.columns:
            return df[(df['args.asset_d'].str.lower() == df['contractAddress'].str.lower())].copy()
        return df

    def search_withdraw(self, fulloutput=False) -> list:
        res_df = pd.DataFrame()
        for group in self.src_tx_group:
            src_chain, dst_chain = group[0]
            src_txs = group[1].reset_index(drop=True)

            # 交叉拼接
            tmp_df = src_txs.merge(
                self.dst_txs, how='cross'
            )
            if tmp_df.empty:
                tmp_df.insert(loc=len(tmp_df.columns), column='hash', value='')
            else:
                tmp_df['contractAddress'] = tmp_df['contractAddress'].fillna('')

            # Rule 0: Match receiver
            if not tmp_df.empty:
                tmp_df = self._match_receiver(tmp_df)

            # Rule 1: Match transaction type
            if not tmp_df.empty:
                tmp_df = self._match_tx_type(tmp_df)

            # Rule 2: Match asset type
            if not tmp_df.empty:
                tmp_df = self._match_asset_type(tmp_df)

            # Rule 3: Match timeStamp
            if not tmp_df.empty:
                # polygon = 60 * 60 = 3600
                # other = 30 * 60 = 1800
                TIME_THRESHOLD = 1800  # In 30 mins
                tmp_df = self._match_timestamp(tmp_df, threshold=TIME_THRESHOLD, key='txhash')

            # Rule 4: Match amount
            if not tmp_df.empty:
                FEE_THRESHOLD = 0.03
                tmp_df = self._match_amount(tmp_df, src_chain, dst_chain, threshold=FEE_THRESHOLD)

            # Optional Rule: identify function name
            # ...

            # Save unique result
            tmp_df = tmp_df.drop_duplicates(subset=['txhash'], keep='first')
            tmp_df = src_txs[['txhash']].merge(
                tmp_df, left_on='txhash',
                right_on='txhash', how='left'
            )
            res_df = pd.concat([res_df, tmp_df], ignore_index=True)

        # (4) Save tx pair arr
        res_df = res_df[['args.srcChain', 'txhash', 'args.dstChain', 'hash']]
        res_df = res_df.rename(columns={
            'args.srcChain': 'srcnet',
            'txhash': 'srcTxHash',
            'args.dstChain': 'dstnet',
            'hash': 'dstTxHash'
        })

        return res_df.to_dict('records')