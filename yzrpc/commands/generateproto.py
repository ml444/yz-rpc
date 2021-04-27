#!/usr/bin/python3.7+
# -*- coding:utf-8 -*-
import os
import textwrap
from . import CommandBase, CommandError
from grpc_tools import protoc
from jinja2 import Environment, FileSystemLoader

from importlib import import_module
from os.path import dirname, join, isdir, abspath, exists

from yzrpc.servicer import load_services
from yzrpc.proto import __proto_meta__
from yzrpc.utils import mkdir_if_not_exist, transform_type
from yzrpc.exceptions import NonstandardPath


class Command(CommandBase):
    formatter_cls_name = 'RawDescriptionHelpFormatter'
    description = textwrap.dedent('''\
            说明：
            --------------------------------
                示例：
                - 根据继承于服务接口基类的服务接口类，自动生成protobuf文件：
                ```shell
                $ cd my_project
                $ yzrpc generateproto
                或
                $ yzrpc generateproto -D=./path/to/you
                或
                $ yzrpc generateproto --template=./path/to/temps
                ```
            ''')
    missing_args_msg = "Default path: './src/protos/'"

    def add_arguments(self, parser):
        parser.add_argument(
            '-D', '--destination',
            # nargs='?',
            default=join(os.getcwd(), 'src', 'protos'),
            help='Destination directory.')
        parser.add_argument(
            '-T', '--template',
            help='The path or URL to load the template from.')

    @staticmethod
    def _validate_template_dir(temp_dir):
        if not exists(temp_dir):
            raise CommandError("The template dir is not exist.")

    def handle(self, *args, **options):
        # 遍历加载各app模块
        load_services('src', 'apps')

        # 从指定的路径获取模版
        temp_dir = options.get('template')
        if temp_dir:
            self._validate_template_dir(temp_dir)
            self.template_dir = temp_dir
        else:
            self.template_dir = abspath(join(
                dirname(dirname(__file__)), "templates", "proto_template"))

        env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        env.globals = env.make_globals({
            "isinstance": isinstance,
            "set": set,
            "list": list,
        })

        target_path = options.get('destination')
        if not os.path.exists(target_path):
            mkdir_if_not_exist(target_path)

        template = env.get_template("proto.tmpl")
        for app_name, meta in __proto_meta__.items():
            _modules = meta.modules
            _messages = self._process_messages(meta.messages, _modules, app_name)
            self._process_services(meta.services, _modules, _messages)
            _services = meta.services
            print(join(target_path, f"{app_name}.proto"))
            template.stream(
                package_name=app_name,
                modules=sorted(_modules),
                messages=_messages,
                services=_services,
            ).dump(join(target_path, f"{app_name}.proto"))

    @staticmethod
    def _process_messages(messages: dict, modules: set, app_name: str):
        """

        :param messages:
        {
            'Permission': {
                'object_id': int,
                'object_type': str,
                'parent_id': typing.Union[int, NoneType],
                'parent_info': typing.Union[src.apps.my_app1.schemas.ParentInfo, NoneType]
            },
            ...
        }

        :return:
        {
            'Permission': {
                'object_id': int64,
                'object_type': string,
                'parent_id': int64,
                'parent_info': ParentInfo
            },
            ...
        }
        """
        _data = dict()
        for key, item in messages.items():
            for k, v in item.items():
                _data.setdefault(key, dict())
                _data[key][k] = transform_type(k, v, modules, app_name)
        return _data

    @staticmethod
    def _process_services(services: list, modules: set, messages: dict):
        """处理从别的应用导入的类型标注"""
        for obj in services:
            for m in obj.methods:
                if m.request_cls.__name__ not in messages:
                    # TODO: validate_module_path
                    _modules = m.request_cls.__module__.split('.')
                    if len(_modules) >= 2 or _modules[-1] != "schemas":
                        _app_name, _schema = _modules[-2:]
                        modules.add(f"src/protos/{_app_name}.proto")
                    else:
                        NonstandardPath(f"[{m.request_cls}]存放路径不规范。")
                if m.response_cls.__name__ not in messages:
                    _modules = m.response_cls.__module__.split('.')
                    if len(_modules) >= 2 or _modules[-1] != "schemas":
                        _app_name, _schema = _modules[-2:]
                        modules.add(f"src/protos/{_app_name}.proto")
                    else:
                        NonstandardPath(f"[{m.request_cls}]存放路径不规范。")





