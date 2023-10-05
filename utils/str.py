#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : str.py
@Time    : 2023/07/18 9:06
@Author  : zzYe

"""
import hashlib


def hash_str(_str: str):
    md5 = hashlib.md5()
    md5.update(
        _str.encode('utf-8')
    )
    return md5.hexdigest()
