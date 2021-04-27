#!/usr/bin/python3.7+
# -*- coding:utf-8 -*-
import os
import sys
from importlib import import_module
from functools import wraps
from os.path import join, isdir
from inspect import isfunction, signature
from typing import List, Tuple, Callable, Iterable

from yzrpc._types import SchemaType
from yzrpc.schema import SchemaBase
from yzrpc.proto import Protobuf, __proto_meta__
from yzrpc import exceptions as exp


class _Method:
    __slots__ = (
        "name", "func", "typ",
        "request_typ", "response_typ",
        "request_cls", "response_cls",
    )

    def __init__(
            self,
            *,
            name: str,
            func: Callable,
            request_typ: str,
            response_typ: str,
            request_cls: SchemaType,
            response_cls: SchemaType,
    ):
        self.name = name
        self.func = func
        self.request_typ = request_typ
        self.response_typ = response_typ
        self.request_cls = request_cls
        self.response_cls = response_cls

    @classmethod
    def from_obj(cls, func, name=None):
        sig = signature(func)
        if len(sig.parameters) >= 3:
            request_streaming = False
            response_streaming = False

            request_cls = getattr(sig.parameters.get("request"), "annotation")
            response_cls = sig.return_annotation

            request_origin = getattr(request_cls, "__origin__", None)
            if request_origin:
                if issubclass(request_origin, Iterable):
                    request_cls = request_cls.__args__[0]
                    request_streaming = True

            response_origin = getattr(response_cls, "__origin__", None)
            if response_origin:
                if issubclass(response_origin, Iterable):
                    response_cls = response_cls.__args__[0]
                    response_streaming = True
            if all(
                    [
                        SchemaBase not in [request_cls, response_cls],
                        issubclass(request_cls, SchemaBase),
                        issubclass(response_cls, SchemaBase),
                    ]
            ):
                if request_streaming:
                    request_typ = "stream"
                    response_typ = 'stream' if response_streaming else ''
                else:
                    request_typ = ''  # "unary"
                    response_typ = 'stream' if response_streaming else ''

                return cls(
                    name=name if name else func.__name__,
                    func=func,
                    request_typ=request_typ,
                    response_typ=response_typ,
                    request_cls=request_cls,
                    response_cls=response_cls,
                )
        raise exp.InvalidRPCMethod(
            """
            The RPC method is invalid.

            The correct signature is blow:
                # schemas.py
                class InputSchema(SchemaBase):
                    ...
                class OutputSchema(SchemaBase):
                    ...

                # views.py
                from .schemas import InputSchema, OutputSchema

                @GrpcMethod
                def get_feature(self, request: InputSchema, context: Context) -> OutputSchema:
                    ...
            """
        )


class GRPCMethod:
    """
    rpc接口方法装饰器
    用法示例：
    class MyApp1Servicer(ServicerBase):
        @GRPCMethod()
        def get_one(self, request: SchemaExample, context) -> SchemaExample: ...

        @GRPCMethod(before_requests=[do_func], after_responses=[do_func])
        def list_some(self, request: SchemaExample, context) -> Iterable[SchemaExample]: ...
    """
    def __init__(self, before_requests: List[Callable] = None, after_responses: List[Callable] = None):
        self.before_requests = before_requests
        self.after_responses = after_responses

    def __call__(self, func):
        _method_inst = _Method.from_obj(func)

        @wraps(func)
        def rpc_method(_self, request, context, *args, **kw):
            h = func
            if self.before_requests:
                for m in self.before_requests:
                    h = m(_self, request, context, *args, **kw)

            result = h(_self, request, context, *args, **kw)

            if self.after_responses:
                for m in self.after_responses:
                    result = m(result)
            return result
        rpc_method.__is_rpc__ = True
        rpc_method.__rpc_method__ = _method_inst
        return rpc_method


RPCMethodDictType = List[_Method]


class ServiceInfo:
    def __init__(self, name: str, module: str, methods: RPCMethodDictType):
        self.name = self._processing_name(name)
        self.path = '.'.join((module, name))
        self.methods: List[_Method] = methods

    def _processing_name(self, name: str):
        if name.endswith('Servicer'):
            name = name.replace('Servicer', '')
        return name


class ServicerMeta(type):

    def __new__(mcs, cls_name: str, bases: Tuple, cls_dict: dict):
        if not bases or object in bases:
            return super().__new__(mcs, cls_name, bases, cls_dict)
        _methods = list()
        for key, _method in filter(
                lambda x: not x[0].startswith("_"), cls_dict.items()):
            # if isfunction(_method) and _method.__name__ == 'rpc_method':
            if isfunction(_method) and hasattr(_method, '__is_rpc__'):
                _m_instance = getattr(_method, '__rpc_method__')
                _methods.append(_m_instance)
        _module = cls_dict.get("__module__", '')  # 'src.apps.appname.views'
        # TODO: validate_module_path
        app_name = _module.split('.')[-2]
        package_meta = Protobuf.get_obj(name=app_name)
        package_meta.services.append(ServiceInfo(cls_name, _module, _methods))

        __proto_meta__[app_name] = package_meta
        return super().__new__(mcs, cls_name, bases, cls_dict)


class ServicerBase(metaclass=ServicerMeta):
    """服务接口基类"""


def match_servicer_cls(item):
    if not item[0].startswith('_') and issubclass(item[1], ServicerBase):
        return True
    else:
        return False


def load_services(*args, flag='apps'):
    """遍历加载app模块"""
    cur_path = os.getcwd()
    sys.path.append(cur_path)
    flag_path = join(cur_path, *args)
    if not flag_path.endswith(flag) or not os.path.exists(flag_path):
        # 从当前位置的路径开始寻找
        parent_path = cur_path
        for path, dirnames, filenames in os.walk(parent_path):
            if path.endswith('src') and 'apps' in dirnames:
                flag_path = join(path, 'apps')
                break
        else:
            raise exp.PathNotExist(f"{flag_path}: 路径不存在。")
    
    project_name = os.path.split(
        flag_path.split(join(os.sep, 'src', 'apps'))[0])[-1]
    for fileordir in os.listdir(flag_path):
        if isdir(join(flag_path, fileordir)) and not fileordir.startswith('_'):
            try:
                _module = import_module(f'src.apps.{fileordir}.views')
            except ModuleNotFoundError:
                _module = import_module(f'{project_name}.src.apps.{fileordir}.views')
            # for srv in filter(match_servicer_cls, _module.__dict__.items()):
            #     pass






