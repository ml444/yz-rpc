#!/usr/bin/python3.7+
# -*- coding:utf-8 -*-
"""
@auth: cml
@date: 2021-04-20 18:14
@desc: ...
"""

import unittest
from os.path import join

from yzrpc.commands import CommandUtility
from yzrpc.client import Client
# from yzrpc.schema import SchemaBase
#
# # from unittest.mock import Mock, patch
# class SchemaExample(SchemaBase):
#     str_exa: str


class TestClient(unittest.TestCase):
    """"""
    # @unittest.skipIf()
    @classmethod
    def setUpClass(cls) -> None:
        cls.cmd = CommandUtility()
        cls.project_name = 'myproject'
        cls.app_name = 'myapp1'
        cls.target_path = join(cls.project_name, 'src')
        cls.destination = join(cls.target_path, 'protos')
        cls.output = join(cls.target_path, 'services')
        cls.default_target = './src'
        # cls.template_path = './app_tmp'
        cls.cmd.run_from_argv(['yzrpc', 'createproject', cls.project_name])
        cls.cmd.run_from_argv(
            ['yzrpc', 'createapp', cls.app_name, '-D', cls.target_path])
        cls.cmd.run_from_argv(
            ['yzrpc', 'generateproto', '-D', cls.destination])
        cls.cmd.run_from_argv(
            ['yzrpc', 'generatemodule', '-I', cls.destination, '-O',
             cls.output])

    @classmethod
    def tearDownClass(cls) -> None:
        del cls.cmd
        import shutil
        # 删除创建的工程
        try:
            shutil.rmtree(cls.project_name)
        except FileNotFoundError:
            pass
        try:
            shutil.rmtree(cls.default_target)
        except FileNotFoundError:
            pass

    def test_search_request_name_of_method(self):
        client = Client('localhost:50051', self.app_name, 'Myapp1')
        s = client._search_request_name_of_method(
            'get_one', path=join(self.destination, f'{self.app_name}.proto'))
        self.assertEqual(s, "SchemaExample")
        s = client._search_request_name_of_method(
            'get_some', path=join(self.destination, f'{self.app_name}.proto'))
        self.assertEqual(s, "SchemaExample")
        s = client._search_request_name_of_method(
            'list_some', path=join(self.destination, f'{self.app_name}.proto'))
        self.assertEqual(s, "SchemaExample")
        s = client._search_request_name_of_method(
            'update_some', path=join(self.destination, f'{self.app_name}.proto'))
        self.assertEqual(s, "SchemaExample")

    # def test_call(self):
    #     import sys, os
    #     sys.path.append(os.path.join(os.getcwd(), "myproject/src"))
    #     from src.apps.myapp1.schemas import SchemaExample
    #
    #     with Client('localhost:50051', self.app_name, 'Myapp1') as client:
    #         request = SchemaExample(str_exa='testing')
    #         response = client.call('get_one', request)
    #         print(response)
    #         print(type(response))
    #         print(response.str_exa)