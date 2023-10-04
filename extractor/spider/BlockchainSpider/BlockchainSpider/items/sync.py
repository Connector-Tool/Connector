import scrapy


class SyncSignalItem(scrapy.Item):
    done = scrapy.Field()  # str
