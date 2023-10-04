import scrapy


class TransactionItem(scrapy.Item):
    transaction_hash = scrapy.Field()  # str
    transaction_index = scrapy.Field()  # int
    block_hash = scrapy.Field()  # str
    block_number = scrapy.Field()  # int
    timestamp = scrapy.Field()  # int
    address_from = scrapy.Field()  # str
    address_to = scrapy.Field()  # str
    value = scrapy.Field()  # int
    gas = scrapy.Field()  # int
    gas_price = scrapy.Field()  # int
    nonce = scrapy.Field()  # int
    is_create_contract = scrapy.Field()  # bool
    is_error = scrapy.Field()  # bool
    input = scrapy.Field()  # str


class EventLogItem(scrapy.Item):
    transaction_hash = scrapy.Field()  # str
    log_index = scrapy.Field()  # int
    block_number = scrapy.Field()  # str
    timestamp = scrapy.Field()  # int
    address = scrapy.Field()  # str
    topics = scrapy.Field()  # [str]
    data = scrapy.Field()  # str
    removed = scrapy.Field()  # bool


class TraceItem(scrapy.Item):
    transaction_hash = scrapy.Field()  # str
    trace_type = scrapy.Field()  # str
    trace_id = scrapy.Field()  # str
    block_number = scrapy.Field()  # int
    timestamp = scrapy.Field()  # int
    address_from = scrapy.Field()  # str
    address_to = scrapy.Field()  # str
    value = scrapy.Field()  # int
    gas = scrapy.Field()  # int
    gas_used = scrapy.Field()  # int
    input = scrapy.Field()  # str
    output = scrapy.Field()  # str


class ContractItem(scrapy.Item):
    address = scrapy.Field()  # str
    code = scrapy.Field()  # str


class Token20TransferItem(scrapy.Item):
    transaction_hash = scrapy.Field()  # str
    log_index = scrapy.Field()  # int
    block_number = scrapy.Field()  # int
    timestamp = scrapy.Field()  # int
    contract_address = scrapy.Field()  # str
    address_from = scrapy.Field()  # str
    address_to = scrapy.Field()  # str
    value = scrapy.Field()  # int


class Token721TransferItem(scrapy.Item):
    transaction_hash = scrapy.Field()  # str
    log_index = scrapy.Field()  # str
    block_number = scrapy.Field()  # int
    timestamp = scrapy.Field()  # int
    contract_address = scrapy.Field()  # str
    address_from = scrapy.Field()  # str
    address_to = scrapy.Field()  # str
    token_id = scrapy.Field()  # int


class Token1155TransferItem(scrapy.Item):
    transaction_hash = scrapy.Field()  # str
    log_index = scrapy.Field()  # int
    block_number = scrapy.Field()  # str
    timestamp = scrapy.Field()  # int
    contract_address = scrapy.Field()  # str
    address_operator = scrapy.Field()  # str
    address_from = scrapy.Field()  # str
    address_to = scrapy.Field()  # str
    token_ids = scrapy.Field()  # [int]
    values = scrapy.Field()  # [int]


class TokenApprovalItem(scrapy.Item):
    transaction_hash = scrapy.Field()  # str
    log_index = scrapy.Field()  # int
    block_number = scrapy.Field()  # str
    timestamp = scrapy.Field()  # int
    contract_address = scrapy.Field()  # str
    address_from = scrapy.Field()  # str
    address_to = scrapy.Field()  # str
    value = scrapy.Field()  # int


class TokenApprovalAllItem(scrapy.Item):
    transaction_hash = scrapy.Field()  # str
    log_index = scrapy.Field()  # int
    block_number = scrapy.Field()  # str
    timestamp = scrapy.Field()  # int
    contract_address = scrapy.Field()  # str
    address_from = scrapy.Field()  # str
    address_to = scrapy.Field()  # str
    approved = scrapy.Field()  # bool


class TokenMetadataItem(scrapy.Item):
    address = scrapy.Field()  # str
    name = scrapy.Field()  # str
    token_symbol = scrapy.Field()  # str
    decimals = scrapy.Field()  # int
    total_supply = scrapy.Field()  # int


class NFTMetadataItem(scrapy.Item):
    transaction_hash = scrapy.Field()  # str
    log_index = scrapy.Field()  # int
    block_number = scrapy.Field()  # str
    timestamp = scrapy.Field()  # int
    contract_address = scrapy.Field()  # str
    token_id = scrapy.Field()  # [int]
    uri = scrapy.Field()  # str
    data = scrapy.Field()  # str
