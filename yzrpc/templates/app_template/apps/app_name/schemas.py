#!/usr/bin/python3.6.8+
# -*- coding:utf-8 -*-
"""
@auth: xxx
@date: 2020-10-18
@desc:

    类型提示typing库使用的相关注意事项：
    1. 尽量不用`typing.Optional` 和 `typing.Union`等多值可选的类型。会引发oneof，导致字段名被重新命名。
    2. 尽量使用`typing.List` 或 `typing.List[int]`，不使用`typing.List[int, str]`这种多选值的形式。理由同上。
    3.
    4.
"""
from enum import Enum
from typing import (
    Optional, Any, List, Tuple, Dict,
    Mapping, Union, Sequence, Iterable
)

from yzrpc.schema import SchemaBase


class CommonBase(SchemaBase):
    class Config:
        orm_mode = True


class EnumExample(Enum):
    A = 1
    B = 2
    C = 3


class EmbedInfo(CommonBase):
    name: str
    age: int


class SchemaExample(CommonBase):
    int_exa: int
    str_exa: str
    bool_exa: bool
    float_exa: float
    bytes_exa: bytes
    tuple_exa: tuple
    list_exa: list
    dict_exa: dict
    enum_exa: EnumExample
    embed_exa: EmbedInfo

    exa_any: Any
    exa_list: List
    exa_tuple: Tuple
    exa_dict: Dict[str, int]
    exa_mapping: Mapping[str, int]
    exa_list_embed: List
    exa_sequence: Sequence[int]
    exa_iterable: Iterable[str]
    exa_list_multi: List[EmbedInfo]
    exa_union: Union[int, EmbedInfo, EnumExample, str]  # 不推荐
    exa_optional: Optional[EmbedInfo]                   # 不推荐
    exa_optional_multi: Optional[EmbedInfo]             # 不推荐
    exa_optional_multi_l: Optional[list]                # 不推荐

    # @validator('object_type')
    # def validate_object_type(cls, value, values):
    #     """object_type in [1,2,3,4]"""
    #     if value not in [1, 2]:
    #         raise exp.RequestParamsError('该类型不能创建')
    #
    #     if value > 2 and not all((values['xx'], values['xxx'])):
    #         raise exp.RequestParamsError('该类型需要传入xxx')
    #     return value
