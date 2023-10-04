from collections import AsyncGenerator, Iterator

import scrapy

from BlockchainSpider.items import TransactionMotifItem, ExternalTransactionItem, \
    InternalTransactionItem, ERC20TokenTransferItem, ERC721TokenTransferItem, ERC1155TokenTransferItem
from BlockchainSpider.spiders.blocks.meta import MetaWeb3BlocksSpider
from BlockchainSpider.strategies.blocks import BLOCK_MOTIF_COUNTER
from BlockchainSpider.tasks.synchronize import SyncMotifCounterTask
from BlockchainSpider.utils.enum import ETHDataTypes


class Web3BlocksSpider(MetaWeb3BlocksSpider):
    name = 'blocks.web3'
    custom_settings = {
        'ITEM_PIPELINES': {
            'BlockchainSpider.pipelines.BlockSemanticPipeline': 297,
            **MetaWeb3BlocksSpider.custom_settings['ITEM_PIPELINES'],
        },
        'PROVIDERS_BUCKET': MetaWeb3BlocksSpider.custom_settings['PROVIDERS_BUCKET']
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # transaction motif counter configure
        self.mcounter = kwargs.get('mcounter')
        self.motif_size = int(kwargs.get('motif_size', 4))
        assert self.mcounter is None or self.mcounter in BLOCK_MOTIF_COUNTER.keys()

        # task map
        self.task_map = dict()

    async def parse_eth_get_block_by_number(self, response: scrapy.http.Response, **kwargs):
        edges = list()
        async for item in super(Web3BlocksSpider, self).parse_eth_get_block_by_number(
                response, **kwargs
        ):
            if self._is_transfer(item):
                edges.append(item)
            yield item

        # generate motif items
        async for item in self._gen_motif_items(
                task_key=kwargs.get('block_number'),
                edges=edges
        ):
            yield item

    async def parse_trace_block(self, response: scrapy.http.Response, **kwargs):
        edges = list()
        for item in super(Web3BlocksSpider, self).parse_trace_block(response, **kwargs):
            if self._is_transfer(item):
                edges.append(item)
            yield item

        # generate motif items
        async for item in self._gen_motif_items(
                task_key=kwargs.get('block_number'),
                edges=edges
        ):
            yield item

    async def parse_eth_get_logs(self, response: scrapy.http.Response, **kwargs):
        edges = list()
        async for item in super(Web3BlocksSpider, self).parse_eth_get_logs(response, **kwargs):
            if self._is_transfer(item):
                edges.append(item)
            yield item

        # generate motif items
        async for item in self._gen_motif_items(
                task_key=kwargs.get('block_number'),
                edges=edges
        ):
            yield item

    async def handle_request_error(self, failure):
        for item in super(Web3BlocksSpider, self).handle_request_error(failure):
            yield item

        # generate motif items if the request failed
        kwargs = failure.request.cb_kwargs
        async for item in self._gen_motif_items(
                task_key=kwargs.get('block_number'),
                edges=list()
        ):
            yield item

    async def _gen_motif_items(self, task_key: str, edges: [list]):
        if self.mcounter is None:
            return

        # get task
        if self.task_map.get(task_key) is None:
            self.task_map[task_key] = self._create_task()
        task = self.task_map[task_key]

        # compute semantics
        rlt = task.count(edges)
        if rlt is None:
            return

        # delete task and generate semantic item
        self.task_map.pop(task_key)
        if isinstance(rlt, AsyncGenerator):
            async for item in rlt:
                yield TransactionMotifItem(
                    transaction_hash=item.get('transaction_hash'),
                    frequency=item.get('frequency'),
                )
        if isinstance(rlt, Iterator):
            for item in rlt:
                yield TransactionMotifItem(
                    transaction_hash=item.get('transaction_hash'),
                    frequency=item.get('frequency'),
                )

    def _create_task(self):
        dtypes = set(self.data_types)
        task = SyncMotifCounterTask(
            strategy=BLOCK_MOTIF_COUNTER[self.mcounter](
                motif_size=self.motif_size,
            )
        )
        for _dtypes in [
            {ETHDataTypes.EXTERNAL.value},
            {ETHDataTypes.TRACE.value},
            {ETHDataTypes.ERC20.value,
             ETHDataTypes.ERC721.value,
             ETHDataTypes.ERC1155.value},
        ]:
            if len(dtypes.intersection(_dtypes)) > 0:
                task.wait()
        return task

    @staticmethod
    def _is_transfer(item) -> bool:
        return any([
            isinstance(item, ExternalTransactionItem),
            isinstance(item, InternalTransactionItem),
            isinstance(item, ERC20TokenTransferItem),
            isinstance(item, ERC721TokenTransferItem),
            isinstance(item, ERC1155TokenTransferItem),
        ])
