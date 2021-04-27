#!/usr/bin/python3.7+
# -*- coding:utf-8 -*-
"""
@auth: cml
@date: 2021/4/1
@desc: ...
"""
import unittest
from unittest.mock import Mock

from yzrpc.server import Server


class TestServer(unittest.TestCase):
    """"""
    project_path = "./myproject"

    @classmethod
    def setUpClass(cls) -> None:
        """"""
        from yzrpc.commands import CommandUtility
        cmd = CommandUtility()
        cmd.run_from_argv(['yzrpc', 'createproject', 'myproject'])
        cmd.run_from_argv(['yzrpc', 'createapp', 'my_app1', "-D", "./myproject/src"])
        cmd.run_from_argv(
            ['yzrpc', 'generateproto', '-D', "./myproject/src/protos"])
        cmd.run_from_argv(
            ['yzrpc', 'generatemodule', '-I', "./myproject/src/protos", '-O',
             "./myproject/src/services"])
        # self.middleware_func = Mock()  # yzrpc.exceptions.InvalidMiddleware

        def middle_func(*args):
            return args
        cls.middleware_func = middle_func
        cls.server = Server(
            host='localhost',
            port=4444,
            max_workers=1,
            # middlewares=[self.middleware_func]
        )
        cls.server.run()
        # self.server.wait_for_termination(timeout=30)

    @classmethod
    def tearDownClass(cls) -> None:
        """"""
        import shutil
        # 删除创建的工程
        try:
            shutil.rmtree(cls.project_path)
        except:
            pass

    # def test_middlewares(self):
    #     self.assertIn(self.middleware_func, self.server._middlewares)

    def test_services(self):
        servicer = self.server._services[0]
        self.assertEqual(servicer.__class__.__name__, 'MyApp1Servicer')

    def test_run(self):
        import grpc
        from src.services import my_app1_pb2, my_app1_pb2_grpc

        with grpc.insecure_channel(f'{self.server._host}:{self.server._port}') as channel:
            stub = my_app1_pb2_grpc.MyApp1Stub(channel)
            req = my_app1_pb2.SchemaExample()
            req_list = [req]
            req_iter = (i for i in req_list)

            # get_one()
            resp = stub.get_one(req)
            self.assertIsInstance(resp, my_app1_pb2.SchemaExample)

            # get_some()
            resps = stub.get_some(req_iter)
            for res in resps:
                self.assertIsInstance(res, my_app1_pb2.SchemaExample)


