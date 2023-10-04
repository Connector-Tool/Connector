import json

import scrapy

from BlockchainSpider import settings
from BlockchainSpider.items.label import LabelReportItem, LabelAddressItem


class LabelsChainabuseSpider(scrapy.Spider):
    name = 'labels.chainabuse'
    custom_settings = {
        'ITEM_PIPELINES': {
            'BlockchainSpider.pipelines.LabelsPipeline': 299,
            **getattr(settings, 'ITEM_PIPELINES', dict())
        },
        'DOWNLOAD_DELAY': 2,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.out_dir = kwargs.get('out')
        self.request_data = {
            "operationName": "GetReports",
            "variables": {
                "input": {
                    "chains": [],
                    "scamCategories": [],
                    "orderBy": {
                        "field": "CREATED_AT",
                        "direction": "DESC"
                    }
                },
                "first": 50,
                # "after": "YXJyYXljb25uZWN0aW9uOjQ5"
            },
            "query": "query GetReports($input: ReportsInput, $after: String, $before: String, $last: Float, $first: Float) {\n  reports(\n    input: $input\n    after: $after\n    before: $before\n    last: $last\n    first: $first\n  ) {\n    pageInfo {\n      hasNextPage\n      hasPreviousPage\n      startCursor\n      endCursor\n      __typename\n    }\n    edges {\n      cursor\n      node {\n        ...Report\n        __typename\n      }\n      __typename\n    }\n    count\n    totalCount\n    __typename\n  }\n}\n\nfragment Report on Report {\n  id\n  ...ReportPreviewDetails\n  ...ReportAccusedScammers\n  ...ReportAuthor\n  ...ReportAddresses\n  ...ReportCompromiseIndicators\n  __typename\n}\n\nfragment ReportPreviewDetails on Report {\n  createdAt\n  scamCategory\n  categoryDescription\n  biDirectionalVoteCount\n  viewerDidVote\n  description\n  lexicalSerializedDescription\n  commentsCount\n  source\n  __typename\n}\n\nfragment ReportAccusedScammers on Report {\n  accusedScammers {\n    id\n    info {\n      id\n      contact\n      type\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ReportAuthor on Report {\n  reportedBy {\n    id\n    username\n    __typename\n  }\n  __typename\n}\n\nfragment ReportAddresses on Report {\n  addresses {\n    id\n    address\n    chain\n    domain\n    label\n    __typename\n  }\n  __typename\n}\n\nfragment ReportCompromiseIndicators on Report {\n  compromiseIndicators {\n    id\n    type\n    value\n    __typename\n  }\n  __typename\n}\n"
        }

    def start_requests(self):
        yield scrapy.Request(
            url="https://www.chainabuse.com/api/graphql-proxy",
            method='POST',
            headers={'Content-Type': 'application/json'},
            body=json.dumps(self.request_data),
        )

    def parse(self, response: scrapy.http.Response, **kwargs):
        rsp = json.loads(response.text)
        reports = rsp['data']['reports']

        # extract label items
        for report in reports['edges']:
            report = report['node']
            item = LabelReportItem()
            item['labels'] = [
                report['scamCategory'].lower()
                if report['scamCategory'] != 'OTHER'
                else report['categoryDescription'].lower()
            ]
            item['urls'] = list()
            item['addresses'] = list()
            item['transactions'] = list()
            item['description'] = report['description']
            item['reporter'] = report['reportedBy']['username']
            for obj in report['addresses']:
                if obj.get('domain') is not None:
                    item['urls'].append(obj['domain'])
                if obj.get('address') is not None:
                    item['addresses'].append({**LabelAddressItem(
                        net=obj.get('chain'),
                        address=obj['address'].lower(),
                    )})
            yield item

        # generate more requests
        page_info = reports['pageInfo']
        req_body = self.request_data.copy()
        req_body['variables']['after'] = page_info['endCursor']
        yield scrapy.Request(
            url="https://www.chainabuse.com/api/graphql-proxy",
            method='POST',
            headers={'Content-Type': 'application/json'},
            body=json.dumps(req_body),
        )
