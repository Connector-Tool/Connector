#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : config.py
@Time    : 2023/07/16 12:44
@Author  : zzYe

"""
import os
from enum import Enum
from pydantic_settings import BaseSettings


class BridgeEnum(Enum):
    CELER = "Celer"
    MULTI = "Multi"
    POLY = "Poly"


class ChainEnum(Enum):
    ETH = "ETH"
    BNB = "BNB"
    Polygon = "Polygon"


class SpiderNetEnum(Enum):
    ETH = "eth"
    BNB = "bsc"
    Polygon = "polygon"


class Scan(BaseSettings):
    URL: str
    API: str
    NAME: str
    API_KEY: list


class Node(BaseSettings):
    API: str
    WEIGHT: int


class Block(BaseSettings):
    NET: str
    TBMAP: str


class Config(BaseSettings):
    PROJECT: str = os.path.abspath(os.path.dirname(__file__))
    DATA_DIR: str = PROJECT + "/data"
    EXPER_DIR: str = PROJECT + "/experiment"

    ADDRESSLIST_DIR: str = DATA_DIR + "/AddressList"
    CHAINID_DIR: str = DATA_DIR + "/ChainID"
    KNOWLEDGE_DIR: dict = {
        'event': DATA_DIR + "/Knowledge/Event",
        'func': DATA_DIR + "/Knowledge/Func"
    }
    BLOCK_DIR: str = DATA_DIR + "/Block"
    BRIDGETX_DIR: str = DATA_DIR + "/BridgeTx"
    TOKEN_DIR: str = DATA_DIR + "/Token"
    MODEL_DIR: str = DATA_DIR + "/Model"
    VALIDATION_DIR: str = DATA_DIR + "/Validation"
    FIRST_PHRASE_DIR: str = DATA_DIR + "/FirstPhrase"

    BLOCK_FILE: dict = {
        'ETH': Block(
            NET='ETH',
            TBMAP=BLOCK_DIR + "/ETHTBMap.csv",
        ),
        'BNB': Block(
            NET='BNB',
            TBMAP=BLOCK_DIR + "/BNBTBMap.csv",
        ),
        'Polygon': Block(
            NET='Polygon',
            TBMAP=BLOCK_DIR + "/PolygonTBMap.csv",
        )
    }

    TOKEN_FILE: dict = {
        'ETH': TOKEN_DIR + "/ERC20.csv",
        'BNB': TOKEN_DIR + "/BERC20.csv",
        'Polygon': TOKEN_DIR + "/PERC20.csv",
    }

    SCAN: dict = {
        'ETH': Scan(
            URL='https://cn.etherscan.com/',
            API='https://api-cn.etherscan.com/api/',
            NAME='Etherscan',
            API_KEY=[
                "JCP5B6U5RXI5I7WRC19AZEZPZ21395IJSG",
                "1ICNJCWUMGGHWIT9XE3RGU7KKVY7CHSZ3T",
                "X13EN3W2FERMMVZAENUSVP4DNKTHTXD519"
            ]
        ),
        'BNB': Scan(
            URL='https://bscscan.com/',
            API='https://api.bscscan.com/api/',
            NAME='Bscscan',
            API_KEY=[
                "S7N1S396ZB98XYC5WQ3IWEPDBGJKESXH5B",
                "EGAQYID9BS2H4YC3WJITVZTXDHYSWIUJDS",
                "5H91KBTSSDGWIKDMGMGDY1RXNE4AA136UH"
            ]
        ),
        'Polygon': Scan(
            URL='https://polygonscan.com//',
            API='https://api.polygonscan.com/api/',
            NAME='PolygonScan',
            API_KEY=[
                "7BTFI86WFGAAD91X2AGSF7YWBWC3M4R39S",
            ]
        ),
    }

    NODE: dict = {
        'ETH': [
            Node(API="https://eth-mainnet.alchemyapi.io/v2/AgKT8OzbNsYnul856tenwnsnL3Pm7WRB", WEIGHT=1),
            Node(API="https://eth-mainnet.alchemyapi.io/v2/UOD8HE4CVqEiDY5E_9XbKDFqYZzJE3XP", WEIGHT=1),
            Node(API="https://eth-mainnet.alchemyapi.io/v2/gwlaWGMm1YWliQTvWtEHcjjfNXQ3W0lK", WEIGHT=1)
        ]
    }

    REQUEST_HEADERS: dict = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/58.0.3029.110 Safari/537.3',
    }

    MYSQL: dict = {
        # 'mysql://user:password@127.0.0.1:3306/database_name'
        'SQLALCHEMY_DATABASE_URI': 'mysql://root:123456@127.0.0.1:3306/cross_chain'
    }

    REDIS: dict = {
        'REDIS_HOST': 'localhost',  # Redis Host Ip
        'REDIS_PORT': 6379,         # Redis Post Number
        'REDIS_DB': 0,              # Redis DB Number
        'REDIS_PASSWORD': None      # Redis Password
    }
