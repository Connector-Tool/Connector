import asyncio
import json
import logging
import random
import sys
import time

import scrapy
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import TCPTimedOutError, DNSLookupError

from BlockchainSpider import settings
from BlockchainSpider.spiders.trans.web3 import Web3TransactionSpider
from BlockchainSpider.utils.enum import ETHDataTypes


class Web3BlockSpider_v2(Web3TransactionSpider):
    name = 'block.web3'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_block = int(kwargs.get('start_blk', '0'))
        self.end_block = kwargs.get('end_blk', None)

        # extract data types
        self.data_types = kwargs.get('types', 'meta,transaction').split(',')
        for data_type in self.data_types:
            assert ETHDataTypes.has(data_type)

        # block receipt method
        self.block_receipt_method = kwargs.get('block_receipt_method', 'eth_getBlockReceipts')

        # sync key
        self.sync_signal_key = '_sync_key'

    def start_requests(self):
        yield scrapy.Request(
            url=random.choice(self.provider_bucket.items),
            method='POST',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({
                "jsonrpc": "2.0",
                "method": self.block_receipt_method,
                "params": ["0x0"],
                "id": 1,
            }),
            callback=self._start_requests,
            errback=self._start_requests,
            cb_kwargs={'timestamp': time.time()}
        )

    async def _start_requests(self, response: scrapy.http.Response, **kwargs):
        # check block receipt method is available or not
        block_receipt_method = self.block_receipt_method
        try:
            data = json.loads(response.text)
            if data.get('result') is None:
                self.block_receipt_method = None
        except:
            self.block_receipt_method = None

        # output tips
        if self.block_receipt_method is None:
            self.log(
                message="`%s` is not available, " % block_receipt_method +
                        "using `eth_getBlockByNumber` and `eth_getTransactionReceipt` instead.",
                level=logging.INFO,
            )
        self.log(
            message="Check over, %s is starting." % getattr(settings, 'BOT_NAME'),
            level=logging.INFO,
        )

        # waiting CD of apikey
        interval = 1 / self.provider_bucket.qps
        using_time = time.time() - kwargs['timestamp']
        if using_time < interval:
            await asyncio.sleep(interval - using_time)

        # generate the requests
        if self.end_block is None:
            yield self.get_request_eth_block_number()
            return
        end_block = self.end_block + 1
        for blk in range(self.start_block, end_block):
            if self.block_receipt_method is None:
                yield self.get_request_eth_block_by_number(
                    block_number=blk,
                    priority=end_block - blk,
                    cb_kwargs={
                        self.sync_signal_key: blk,
                        'block_number': blk
                    },
                )
            yield self.get_request_eth_blcok_receipt()

    async def parse_eth_block_number(self, response: scrapy.http.Response, **kwargs):
        func_name = '%s.%s' % (self.__class__.__name__, sys._getframe().f_code.co_name)
        self.log(message='On {}, with {}'.format(func_name, str(kwargs)), level=logging.DEBUG)
        result = json.loads(response.text)
        result = result.get('result')

        # generate more requests
        if result is not None:
            end_block = int(result, 16) + 1
            for blk in range(self.end_block, end_block):
                if self.block_receipt_method is None:
                    yield self.get_request_eth_block_by_number(
                        block_number=blk,
                        priority=end_block - blk,
                        cb_kwargs={
                            self.sync_signal_key: blk,
                            'block_number': blk
                        },
                    )
                yield self.get_request_eth_blcok_receipt()
            self.end_block = end_block
        else:
            self.log(
                message="Result field is None on {} with {}, ".format(func_name, kwargs) +
                        "please ensure that whether the provider is available.",
                level=logging.ERROR
            )

        # next query of block number
        self.log(
            message="Query the latest block number after 5 seconds...",
            level=logging.INFO
        )
        await asyncio.sleep(5)
        yield self.get_request_eth_block_number()

    def get_request_eth_block_number(self) -> scrapy.Request:
        return scrapy.Request(
            url=self.provider_bucket.get(),
            method='POST',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({
                "method": "eth_blockNumber",
                "params": [],
                "id": 1,
                "jsonrpc": "2.0"
            }),
            callback=self.parse_eth_block_number,
        )

    def get_request_eth_block_by_number(
            self, block_number: int, priority: int, cb_kwargs: dict
    ) -> scrapy.Request:
        return scrapy.Request(
            url=self.provider_bucket.get(),
            method='POST',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({
                "jsonrpc": "2.0",
                "method": "eth_getBlockByNumber",
                "params": [
                    hex(block_number) if isinstance(block_number, int) else block_number,
                    True
                ],
                "id": 1
            }),
            callback=self.parse_eth_get_block_by_number,
            priority=priority,
            cb_kwargs=cb_kwargs,
        )

