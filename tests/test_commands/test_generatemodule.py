#!/usr/bin/python3.7+
# -*- coding:utf-8 -*-
"""
@auth: cml
@date: 2021/4/7
@desc: grcp模块生成的测试脚本
"""
import os
import unittest
from os.path import join, exists
from yzrpc.commands import CommandUtility, CommandError


class TestGenerateModuleCommand(unittest.TestCase):
    def setUp(self) -> None:
        self.cmd = CommandUtility()
        self.project_name = 'myproject'
        self.app_name = 'myapp1'
        self.target_path = join(self.project_name, 'src')
        self.destination = join(self.target_path, 'protos')
        self.output = join(self.target_path, 'services')
        self.default_target = './src'
        # self.template_path = './app_tmp'
        self.cmd.run_from_argv(['yzrpc', 'createproject', self.project_name])
        self.cmd.run_from_argv(
            ['yzrpc', 'createapp', self.app_name, '-D', self.target_path])
        self.cmd.run_from_argv(
            ['yzrpc', 'generateproto', '-D', self.destination])

    def tearDown(self) -> None:
        del self.cmd
        import shutil
        # 删除创建的工程
        try:
            shutil.rmtree(self.project_name)
        except FileNotFoundError:
            pass
        try:
            shutil.rmtree(self.default_target)
        except FileNotFoundError:
            pass

    def test_generate_module_with_default(self):
        # expect_raise = "Not found any of proto file."
        with self.assertRaises(SystemExit) as e:
            self.cmd.run_from_argv(['yzrpc', 'generatemodule'])
        exp = e.exception
        self.assertEqual(exp.args[0], 1)

    def test_generate_module_with_success(self):
        os.mkdir(self.default_target)
        self.cmd.run_from_argv(
            ['yzrpc', 'generatemodule', '-I', self.destination, '-O', self.output])
        src_path = join(self.target_path, 'services')
        self.assertTrue(exists(join(src_path, f'{self.app_name}_pb2.py')))
        self.assertTrue(exists(join(src_path, f'{self.app_name}_pb2_grpc.py')))

    def test_proto_path_with_not_exist(self):
        # expect_raise = "Not found any of proto file."
        with self.assertRaises(SystemExit) as e:
            self.cmd.run_from_argv(
                ['yzrpc', 'generatemodule', '-I', self.default_target])
        exp = e.exception
        self.assertEqual(exp.args[0], 1)


if __name__ == '__main__':
    unittest.main()
