#!/usr/bin/python3.7+
# -*- coding:utf-8 -*-
"""
@auth: cml
@date: 2021-04-20 14:32
@desc: ...
"""
import re
import os
from typing import Union

import grpc

from yzrpc.utils import get_module_attr
from yzrpc.schema import SchemaBase
from yzrpc.config import settings


class ManageServicer():
    """"""
    def __init__(self, exclude):
        """"""
        # 加载服务


class Client:
    """
    Usage:
        >>> cd project_dir

        >>> with Client('localhost:50051', 'my_app1', 'MyApp1') as client:
        >>>     request = SchemaExample(str_exa='test', ...)
        >>>     response = client.call('get_one', request)
        >>>     print(response)
        >>>     print(type(response))
        >>>     print(response.str_exa)
    """
    def __init__(self, address: str, package_name: str, service_name: str):
        self.pkg_name = package_name
        self.svc_name = self._processing_servicer_name(service_name)
        self.channel = grpc.insecure_channel(address, )
        self.stub = self._get_stub_cls()(self.channel)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.channel.close()

    def call(self, method_name: str, request: Union[SchemaBase, dict]):
        # 校验参数类型
        pb_request = self._processing_request(method_name, request)

        try:
            method = getattr(self.stub, method_name)
        except AttributeError as e:
            raise e
        else:
            return method(pb_request)

    @staticmethod
    def _processing_servicer_name(service_name):
        """去除后缀"""
        if service_name.endswith('Servicer'):
            service_name = service_name.replace('Servicer', '')
        return service_name

    def _get_stub_cls(self):
        """获取stub类"""
        return get_module_attr(
            f"src.services.{self.pkg_name}_pb2_grpc.{self.svc_name}Stub")

    def _processing_request(self, method_name, request: Union[SchemaBase, dict]):
        """
        验证请求类型是否与rpc方法要求一致
        把请求类型转换为pb模块所需的类型
        # TODO 暂未处理跨proto文件的类型调用
        """
        t_name = self._search_request_name_of_method(method_name)
        if isinstance(request, SchemaBase):
            if request.__class__.__name__ != t_name:
                raise TypeError(
                    f"The {method_name} method only accept {t_name} type.")
            request = request.dict()
        if not isinstance(request, dict):
            raise TypeError(
                f"'request' must belong to dict and SchemaBase types, "
                f"not {type(request)} types")
        req_cls = get_module_attr(
            f"src.services.{self.pkg_name}_pb2.{t_name}"
        )
        return req_cls(**request)

    def _search_request_name_of_method(self, method_name: str, path: str=None):
        _p = "service %s [\{\}\(\).\n\s\w]*?%s.*(?<=\()([ \w.]*)?\) returns"%(
            self.svc_name, method_name)
        _compile = re.compile(_p)
        if path is None:
            # print(settings.src_path)
            path = os.path.join(
                settings.src_path, 'protos', f"{self.pkg_name}.proto")
        with open(path, 'r') as f:
            _s = _compile.search(f.read())
            if not _s:
                return ''
            s = _s.group(1).strip().replace('stream ', '')
            return s



