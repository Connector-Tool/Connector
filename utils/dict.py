#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : dict.py
@Time    : 2023/07/16 14:10
@Author  : zzYe

"""


def prefix_dict(dict_, prefix_s='') -> dict:
    """convert dict to prefix dict

    Args:
        dict_ (dict): original dict
        prefix_s (str, optional): prefix symbol. Defaults to ''.

    Returns:
        dict: added prefix symbol dict
    """
    return {prefix_s + k: v for k, v in dict_.items()}


def expand_dict(dict_, linker='.') -> dict:
    """expand multi-layer nested dict by keyword

    Args:
        dict_ (dict): multi-layer nested dict
        linker (str, optional): nested keyword concatenation. Defaults to '.'.

    Returns:
        dict: single-layer dict
    """
    ret_dict = {}
    for k, v in dict_.items():
        if type(v) is dict:
            v = expand_dict(v)
            ret_dict.update(prefix_dict(v, prefix_s=k + linker))
        else:
            ret_dict.update({k: v})
    return ret_dict