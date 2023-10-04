from BlockchainSpider.spiders.txs.eth.haircut import TxsETHHaircutSpider


class TxsPolygonHaircutSpider(TxsETHHaircutSpider):
    name = 'txs.polygon.haircut'
    TXS_API_URL = 'https://api.polygonscan.com/api'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.apikey_bucket = type(self.apikey_bucket)(net='polygon', kps=5)

