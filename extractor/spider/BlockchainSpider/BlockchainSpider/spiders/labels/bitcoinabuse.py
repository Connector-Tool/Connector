import scrapy

from BlockchainSpider import settings


class LabelsBitchainabuseSpider(scrapy.Spider):
    name = 'labels.bitcoinabuse'
    custom_settings = {
        'ITEM_PIPELINES': {
            'BlockchainSpider.pipelines.LabelsPipeline': 299,
            **getattr(settings, 'ITEM_PIPELINES', dict())
        }
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.out_dir = kwargs.get('out')

    def start_requests(self):
        yield scrapy.Request(
            url="https://www.bitcoinabuse.com/reports",
            method='GET',
            callback=self.parse_index
        )

    def parse_index(self, response, **kwargs):
        # TODO
        pass
