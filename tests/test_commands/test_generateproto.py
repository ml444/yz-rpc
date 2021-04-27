#!/usr/bin/python3.7+
# -*- coding:utf-8 -*-
"""
@auth: cml
@date: 2021/4/7
@desc: 生成protobuf文件命令的测试脚本
"""

import os
import unittest
from os.path import join, exists
from yzrpc.commands import CommandUtility, CommandError


class TestGenerateProtoCommand(unittest.TestCase):
    def setUp(self) -> None:
        self.cmd = CommandUtility()
        self.project_name = 'myproject'
        self.app_name = 'myapp1'
        self.target_path = f'{self.project_name}/src'
        self.destination = f'{self.target_path}/protos'
        self.default_target = './src'
        self.template_path = './proto_tmp'
        self.cmd.run_from_argv(['yzrpc', 'createproject', self.project_name])
        self.cmd.run_from_argv(['yzrpc', 'createapp', self.app_name, '-D', self.target_path])

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
        try:
            shutil.rmtree(self.template_path)
        except FileNotFoundError:
            pass

    def test_generate_proto_with_success(self):
        self.cmd.run_from_argv(['yzrpc', 'generateproto', '-D', self.destination])
        src_path = join(self.project_name, 'src', 'protos', f'{self.app_name}.proto')
        self.assertTrue(exists(src_path))
        with open(src_path, 'r') as f:
            self.assertIn(f'package {self.app_name};\n', f.readlines())

    def test_template_with_path_not_exist(self):
        expect_raise = "The template dir is not exist."
        with self.assertRaises(CommandError) as e:
            self.cmd.run_from_argv(
                ['yzrpc', 'generateproto', '-T', self.template_path])
        exp = e.exception
        self.assertEqual(exp.args[0], expect_raise)

    def test_template_with_path_exist(self):
        expect_txt = "This is template test."
        os.mkdir(self.template_path)
        file_path = join(self.template_path, 'proto.tmpl')
        with open(file_path, 'w') as f:
            f.write(expect_txt)
            f.flush()
        self.cmd.run_from_argv(
            ['yzrpc', 'generateproto', '-D', self.destination, '-T', self.template_path]
        )
        proto_path = join(
            self.project_name, 'src', 'protos', f"{self.app_name}.proto")
        self.assertTrue(exists(proto_path))
        with open(proto_path, 'r') as f:
            content = f.read()
        self.assertEqual(content, expect_txt)


if __name__ == '__main__':
    unittest.main()
