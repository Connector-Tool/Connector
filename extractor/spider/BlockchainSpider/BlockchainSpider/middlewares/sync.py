import asyncio
import logging
from typing import Callable, Union, AsyncGenerator, Generator

import scrapy

from BlockchainSpider.items.sync import SyncSignalItem
from BlockchainSpider.middlewares._meta import LogMiddleware


class SyncMiddleware(LogMiddleware):
    def __init__(self):
        self._sync_signals = dict()
        self._lock = asyncio.Lock()

    async def process_spider_output(self, response, result, spider):
        if getattr(spider, 'sync_signal_key') is None:
            async for item in result:
                yield item
            return

        # add sync signal for request
        async for item in result:
            if isinstance(item, scrapy.Request):
                sync_signal = item.cb_kwargs[spider.sync_signal_key]
                self._sync_signals[sync_signal] = self._sync_signals.get(sync_signal, 0) + 1
                yield item.replace(
                    cb_kwargs={
                        spider.sync_signal_key: sync_signal,
                        **item.cb_kwargs,
                    },
                    errback=self.make_errback(item.errback, spider.sync_signal_key),
                )
                continue

            # output other items
            yield item

        # generate sync signal item (when the response successes)
        kwargs = response.request.cb_kwargs
        sync_signal = kwargs.get(spider.sync_signal_key)
        if self._sync_signals.get(sync_signal, 0) > 0:
            self._sync_signals[sync_signal] -= 1
            if self._sync_signals[sync_signal] == 0:
                del self._sync_signals[sync_signal]
                yield SyncSignalItem(done=sync_signal)

    def make_errback(self, old_errback, sync_signal_key: str) -> Callable:
        async def new_errback(failure):
            # wrap the old error callback
            old_results = old_errback(failure)
            if isinstance(old_results, Generator):
                for rlt in old_results:
                    yield rlt
            if isinstance(old_results, AsyncGenerator):
                async for rlt in old_results:
                    yield rlt

            # reload context data and log out
            request = failure.request
            kwargs = request.cb_kwargs
            self.log(
                message='Get error when fetching {} with {}, callback args {}'.format(
                    request.url, request.body, str(kwargs)
                ),
                level=logging.WARNING
            )

            # generate sync signal item (when the response fails)
            yield await self.generate_sync_signal_item(
                cb_kwargs=kwargs,
                sync_signal_key=sync_signal_key,
            )

        return new_errback

    async def generate_sync_signal_item(self, cb_kwargs: dict, sync_signal_key: str) -> Union[SyncSignalItem, None]:
        await self._lock.acquire()
        sync_signal = cb_kwargs.get(sync_signal_key)
        if self._sync_signals.get(sync_signal, 0) > 0:
            self._sync_signals[sync_signal] -= 1
            if self._sync_signals[sync_signal] == 0:
                del self._sync_signals[sync_signal]
                yield SyncSignalItem(done=sync_signal)
        self._lock.release()
