#!/usr/bin/python3.7+
# -*- coding:utf-8 -*-
"""
@auth: cml
@date: 2021-04-16 21:22
@desc: ...
"""
from typing import (
    DefaultDict, Dict, Iterator, List, Tuple,
    Type, TypeVar, TYPE_CHECKING,
    Generic, Any, AnyStr, Union,
    Callable, Iterable,
    Mapping, Set,
)


ServiceType = TypeVar('ServiceType')

SchemaType = TypeVar('SchemaType')    # covariant=True

ServerType = TypeVar('ServerType')
