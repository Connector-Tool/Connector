#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : item.py
@Time    : 2023/07/25 14:27
@Author  : zzYe

"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class BridgeEnum(Enum):
    CELER = "Celer"
    MULTI = "Multi"
    Poly = "Poly"


class ChainEnum(Enum):
    ETH = "ETH"
    BNB = "BNB"
    Polygon = "Polygon"


class EventLog(BaseModel):
    data: dict


class Transaction(BaseModel):
    chain: ChainEnum
    hash: str
    value: float
    timestamp: int

    cross_event_log: Optional[EventLog] = None


