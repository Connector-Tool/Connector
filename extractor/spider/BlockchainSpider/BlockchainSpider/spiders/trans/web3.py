import json
import logging
import re
import sys
from collections.abc import Iterator

import scrapy

from BlockchainSpider import settings
from BlockchainSpider.items import TransactionItem, EventLogItem, TraceItem
from BlockchainSpider.utils.bucket import AsyncItemBucket
from BlockchainSpider.utils.web3 import hex_to_dec


class Web3TransactionSpider(scrapy.Spider):
    name = 'trans.web3'
    custom_settings = {
        'ITEM_PIPELINES': {
            'BlockchainSpider.pipelines.TransPipeline': 299,
            **getattr(settings, 'ITEM_PIPELINES', dict())
        },
        'SPIDER_MIDDLEWARES': {
            'BlockchainSpider.middlewares.trans.ContractItemMiddleware': 542,
            'BlockchainSpider.middlewares.trans.TokenItemMiddleware': 541,
            'BlockchainSpider.middlewares.trans.MetadataItemMiddleware': 540,
            **getattr(settings, 'SPIDER_MIDDLEWARES', dict())
        },
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # output dir and transaction hash
        self.out_dir = kwargs.get('out')
        self.txhashs = [
            item for item in kwargs.get('hash', '').split(',')
            if re.search(r"(0x[0-9a-f]{64})", item, re.IGNORECASE | re.ASCII)
        ]

        # provider settings
        assert kwargs.get('providers') is not None, "please input providers separated by commas!"
        self.provider_bucket = AsyncItemBucket(
            items=kwargs.get('providers').split(','),
            qps=getattr(settings, 'CONCURRENT_REQUESTS', 3),
        )

    def start_requests(self):
        self.log(
            message="Checking %s now, please wait for a minute." % getattr(settings, 'BOT_NAME'),
            level=logging.INFO,
        )
        yield scrapy.Request(
            url='http://test4%s.please.ignore' % getattr(settings, 'BOT_NAME'),
            errback=self._start_requests,
            callback=self._start_requests,
        )

    async def _start_requests(self, response: scrapy.http.Response, **kwargs):
        self.log(
            message="Check over, %s is starting." % getattr(settings, 'BOT_NAME'),
            level=logging.INFO,
        )
        for txhash in self.txhashs:
            yield await self.get_request_eth_transaction(
                txhash=txhash,
                cb_kwargs={'txhash': txhash},
            )

    async def parse_transaction(self, response: scrapy.http.Response, **kwargs):
        func_name = '%s.%s' % (self.__class__.__name__, sys._getframe().f_code.co_name)
        self.log(message='On {}, with {}'.format(func_name, str(kwargs)), level=logging.DEBUG)
        result = json.loads(response.text)
        result = result.get('result')

        # parse external transaction
        item = TransactionItem(
            transaction_hash=result.get('hash', ''),
            transaction_index=hex_to_dec(result.get('transactionIndex')),
            block_hash=result.get('blockHash', ''),
            block_number=hex_to_dec(result.get('blockNumber')),
            timestamp=hex_to_dec(result.get('timestamp')),
            address_from=result['from'] if result.get('from') else '',
            address_to=result['to'] if result.get('to') else '',
            is_create_contract=False,
            value=hex_to_dec(result.get('value')),
            gas=hex_to_dec(result.get('gas')),
            gas_price=hex_to_dec(result.get('gasPrice')),
            nonce=hex_to_dec(result.get('nonce')),
            input=result.get('input', ''),
        )

        # generate receipt request
        yield await self.get_request_eth_transaction_receipt(
            txhash=kwargs['txhash'],
            cb_kwargs={'item_external_transaction': item, **kwargs},
        )

        # generate debug request
        yield await self.get_request_debug_transaction(
            txhash=kwargs['txhash'],
            cb_kwargs={'item_external_transaction': item, **kwargs},
        )

    def parse_transaction_receipt(self, response: scrapy.http.Response, **kwargs):
        func_name = '%s.%s' % (self.__class__.__name__, sys._getframe().f_code.co_name)
        self.log(message='On {}, with {}'.format(func_name, str(kwargs)), level=logging.DEBUG)
        result = json.loads(response.text)
        result = result.get('result')

        # generate external transaction
        item = kwargs.get('item_external_transaction')
        if result.get('contractAddress'):
            item['is_create_contract'] = True
            item['address_to'] = result['contractAddress']
        item['is_error'] = True if result.get('status') == '0x0' else False
        yield item

        # generate logs
        for log in result['logs']:
            yield EventLogItem(
                transaction_hash=log.get('transactionHash', ''),
                log_index=hex_to_dec(log.get('logIndex')),
                block_number=hex_to_dec(log.get('blockNumber')),
                timestamp=item['timestamp'],
                address=log.get('address', '').lower(),
                topics=log.get('topics', list()),
                data=log.get('data', ''),
                removed=log.get('removed', False),
            )

    def parse_debug_transaction(self, response: scrapy.http.Response, **kwargs):
        func_name = '%s.%s' % (self.__class__.__name__, sys._getframe().f_code.co_name)
        self.log(message='On {}, with {}'.format(func_name, str(kwargs)), level=logging.DEBUG)
        result = json.loads(response.text)
        result = result.get('result')

        # recover the raw external transaction item
        external_transaction = kwargs['item_external_transaction']

        # parse trance item (skip the first call)
        for item, depth, order in self._retrieve_mapping_tree('calls', result):
            if depth == 0 and order == 0:
                continue
            yield TraceItem(
                transaction_hash=external_transaction['transaction_hash'],
                trace_type=item.get('type', ''),
                trace_id='%d_%d' % (depth, order),
                block_number=external_transaction['block_number'],
                timestamp=external_transaction['timestamp'],
                address_from=item.get('from', ''),
                address_to=item.get('to', ''),
                value=hex_to_dec(item.get('value')),
                gas=hex_to_dec(item.get('gas')),
                gas_used=hex_to_dec(item.get('gasUsed')),
                input=item.get('input', ''),
                output=item.get('output', ''),
            )

    async def get_request_eth_transaction(self, txhash: str, cb_kwargs: dict = None) -> scrapy.Request:
        return scrapy.Request(
            url=await self.provider_bucket.get(),
            method='POST',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({
                "jsonrpc": "2.0",
                "method": "eth_getTransactionByHash",
                "params": [txhash],
                "id": 1
            }),
            callback=self.parse_transaction,
            cb_kwargs=cb_kwargs if cb_kwargs else dict(),
        )

    async def get_request_eth_transaction_receipt(self, txhash: str, cb_kwargs: dict = None) -> scrapy.Request:
        return scrapy.Request(
            url=await self.provider_bucket.get(),
            method='POST',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({
                "jsonrpc": "2.0",
                "method": "eth_getTransactionReceipt",
                "params": [txhash],
                "id": 1
            }),
            callback=self.parse_transaction_receipt,
            cb_kwargs=cb_kwargs if cb_kwargs else dict(),
        )

    async def get_request_debug_transaction(self, txhash: str, cb_kwargs: dict = None) -> scrapy.Request:
        return scrapy.Request(
            url=await self.provider_bucket.get(),
            method='POST',
            headers={'Content-Type': 'application/json'},
            body=json.dumps({
                "jsonrpc": "2.0",
                "method": "debug_traceTransaction",
                "params": [txhash, {"tracer": "callTracer"}],
                "id": 1
            }),
            callback=self.parse_debug_transaction,
            cb_kwargs=cb_kwargs if cb_kwargs else dict(),
        )

    def _retrieve_mapping_tree(self, key: str, item: dict, depth: int = 0, order: int = 0) -> Iterator:
        yield item, depth, order
        if not item.get(key):
            return
        for idx, child in enumerate(item[key]):
            yield from self._retrieve_mapping_tree(key, child, depth + 1, idx)
