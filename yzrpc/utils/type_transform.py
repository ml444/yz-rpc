#!/usr/bin/python3.7+
# -*- coding:utf-8 -*-
"""
@auth: cml
@date: 2021/3/31
@desc: ...
"""
from typing import Iterable, List, Union
from inspect import isclass, isfunction
from enum import Enum
from yzrpc.schema import SchemaBase

__all__ = [
    "transform_type"
]


def _typing_union(field_name, value, modules, app_name):
    _set = set()
    for t in value.__args__:
        try:
            _name = t.__name__
        except AttributeError:
            _name = t._name

        _field_name = f"{field_name}__{_name}"
        if _name == "NoneType":
            modules.add("google/protobuf/struct.proto")
            _set.add((_field_name, 'google.protobuf.NullValue'))
        else:
            _result = transform_type(field_name, t, modules, app_name)
            _set.add((_field_name, _result))
    return _set


def _typing_list(field_name, value, modules, app_name) -> Union[list, set]:
    if value._special is True:
        return 'google.protobuf.ListValue'
    if len(value.__args__) == 1:
        _list = []
        for t in value.__args__:  # __parameters__
            try:
                _name = t.__name__
            except AttributeError:
                _name = t._name
            if _name == "NoneType":
                modules.add("google/protobuf/struct.proto")
                _list.append('google.protobuf.NullValue')
            else:
                _result = transform_type(field_name, t, modules, app_name)
                _list.append(_result)
        return _list
    return _typing_union(field_name, value, modules, app_name)


def _typing_set(field_name, value, modules, app_name):
    return _typing_list(field_name, value, modules, app_name)


def _typing_mapping(field_name, value, modules, app_name):
    k, v = value.__args__
    k_typ = transform_type(field_name, k, modules, app_name)
    v_typ = transform_type(field_name, v, modules, app_name)
    return f"map<{k_typ}, {v_typ}>"


typing_data = {
    "Any": ("google/protobuf/any.proto", "google.protobuf.Any"),
    "AnyStr": (None, "bytes"),
    "Set": (None, _typing_set),
    "Dict": (None, _typing_mapping),
    "Mapping": (None, _typing_mapping),
    "Tuple": (None, _typing_list),
    "Sequence": (None, _typing_list),
    "Iterable": (None, _typing_list),
    "List": (None, _typing_list),
    "Union": (None, _typing_union),
    # "Callable": "",
}


def transform_type(field_name, value, modules: set, app_name: str) -> Union[str, list, set]:
    """"""
    if isclass(value):
        if issubclass(value, str):
            return 'string'
        elif issubclass(value, int):
            # TODO int32 & int64
            return 'int64'
        elif issubclass(value, bool):
            return 'bool'
        elif issubclass(value, float):
            # TODO float & double
            return 'float'
        elif issubclass(value, bytes):
            return 'bytes'
        elif issubclass(value, list):
            modules.add("google/protobuf/struct.proto")
            return 'google.protobuf.ListValue'
        elif issubclass(value, tuple):
            modules.add("google/protobuf/struct.proto")
            return 'google.protobuf.ListValue'
        elif issubclass(value, dict):
            modules.add("google/protobuf/struct.proto")
            return 'google.protobuf.Struct'
        elif issubclass(value, Enum):
            modules.add("google/protobuf/type.proto")
            return 'google.protobuf.Enum'
        else:
            # TODO: 处理Schema类未在规定目录下的情况
            if not issubclass(value, SchemaBase):
                raise ValueError(
                    f"[{value.__name__}]该类型不被支持，暂时只能处理继承于'SchemaBase'的类")
            _modules = value.__module__.split('.')
            if len(_modules) >= 2 and _modules[-1] == "schemas":
                _app_name, _schema = _modules[-2:]
                if _app_name != app_name:
                    modules.add(f"src/protos/{_app_name}.proto")
            else:
                raise ValueError(
                    f"[{value.__name__}]该类型未按规定存放在'APP_NAME.schemas.py'文件中")
            return value.__name__
    elif value.__module__ == 'typing':
        try:
            _name = value.__name__
        except AttributeError:
            _name = value._name
            if _name is None and value.__origin__ is Union:
                # print("value.__origin__:", value.__origin__)
                # TODO: Union在传递过程中丢失 '_name'
                _name = "Union"
                value._name = "Union"

        try:
            type_url, _typ = typing_data.get(_name)
        except TypeError as e:
            # import traceback
            # traceback.print_exc()
            print(e.args[0])
            raise TypeError(f"[{value.__name__}]该类型不被支持")
        else:
            if type_url:
                modules.add(type_url)
            if isfunction(_typ):
                return _typ(field_name, value, modules, app_name)
            if _typ:
                return _typ

        # if _name == 'List':     # -> repeated
        #     return _typing_list(value, modules, app_name)
        #     # if value._special is True:
        #     #     return 'google.protobuf.ListValue'
        #     # _list = []
        #     # for t in value.__args__:    # __parameters__
        #     #     if t.__name__ == "NoneType":
        #     #         _list.append('google.protobuf.NullValue')
        #     #     else:
        #     #         # TODO src.apps.ParentInfo
        #     #         _result = transform_type(t, modules, app_name)
        #     #         _list.append(_result)
        #     # return _list
        # elif _name == 'Union':  # -> oneof
        #     return _typing_union(value, modules, app_name)
        #     # _set = set()
        #     # for t in value.__args__:
        #     #     if t.__name__ == "NoneType":
        #     #         _set.add('google.protobuf.NullValue')
        #     #     else:
        #     #         # TODO src.apps.ParentInfo
        #     #         _result = transform_type(t, modules, app_name)
        #     #         _set.add(_result)
        #     # return _set
    else:
        pass

