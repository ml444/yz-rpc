import os
from typing import AnyStr


__all__ = [
    "mkdir_if_not_exist", "get_abspath"
]


def mkdir_if_not_exist(path: str):
    """不存在就创建目录"""
    if not os.path.exists(path):
        os.makedirs(path)


def get_abspath(path: AnyStr):
    return os.path.abspath(os.path.expanduser(path))