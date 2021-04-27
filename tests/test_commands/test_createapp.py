#!/usr/bin/python3.7+
# -*- coding:utf-8 -*-
"""
@auth: cml
@date: 2021/4/6
@desc: 测试创建应用命令
"""
import os
import unittest
from os.path import join, exists
from yzrpc.commands import CommandUtility, CommandError


class TestCreateAppCommand(unittest.TestCase):
    def setUp(self) -> None:
        self.cmd = CommandUtility()
        self.project_name = 'myproject'
        self.app_name = 'myapp1'
        self.target_path = f'{self.project_name}/src'
        self.default_target = './src'
        self.template_path = './app_tmp'
        self.cmd.run_from_argv(['yzrpc', 'createproject', self.project_name])

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

    def _judge_file_exist(self, src_path):
        self.assertTrue(exists(join(src_path, '__init__.py')))
        self.assertTrue(exists(join(src_path, 'controllers.py')))
        self.assertTrue(exists(join(src_path, 'models.py')))
        self.assertTrue(exists(join(src_path, 'schemas.py')))
        self.assertTrue(exists(join(src_path, 'views.py')))
        self.assertTrue(exists(join(src_path, 'tests.py')))

    def test_no_app_name(self):
        try:
            self.cmd.run_from_argv(['yzrpc', 'createapp'])
        except SystemExit as e:
            self.assertEqual(e.args[0], 2)

    def test_app_name_with_path(self):
        expect_raise = "The app name can't have a path; " \
                       "please use the '-D' parameter for the path."
        with self.assertRaises(CommandError) as e:
            self.cmd.run_from_argv(['yzrpc', 'createapp', './my/app1'])
        exp = e.exception
        self.assertEqual(exp.args[0], expect_raise)

    def test_create_project_with_success(self):
        os.mkdir(self.default_target)
        self.cmd.run_from_argv(
            ['yzrpc', 'createapp', self.app_name])
        src_path = join('src', 'apps', self.app_name)
        self._judge_file_exist(src_path)

    def test_target_path_with_not_exist(self):
        expect_raise = "Destination directory {} does not exist, " \
                       "please create it first.".format(
            os.path.abspath(os.path.expanduser('./src'))
        )
        with self.assertRaises(CommandError) as e:
            self.cmd.run_from_argv(
                ['yzrpc', 'createapp', self.app_name])
        exp = e.exception
        self.assertEqual(exp.args[0], expect_raise)

    def test_target_path_with_exist(self):
        self.cmd.run_from_argv(
            ['yzrpc', 'createapp', self.app_name, '-D', self.target_path])
        src_path = join(self.project_name, 'src', 'apps', self.app_name)
        self._judge_file_exist(src_path)

    def test_template_with_path_not_exist(self):
        expect_raise = "The template dir is not exist."
        with self.assertRaises(CommandError) as e:
            self.cmd.run_from_argv(
                ['yzrpc', 'createapp', self.app_name,
                 '-D', self.target_path, '-T', self.template_path])
        exp = e.exception
        self.assertEqual(exp.args[0], expect_raise)

    def test_template_with_path_exist(self):
        expect_txt = "This is template test."
        os.mkdir(self.template_path)
        file_path = join(self.template_path, 'temp_test.txt')
        with open(file_path, 'w') as f:
            f.write(expect_txt)
            f.flush()
        self.cmd.run_from_argv(
            ['yzrpc', 'createapp', self.app_name,
             '-D', self.target_path, '-T', self.template_path]
        )
        proto_path = join(
            self.project_name, 'src', 'temp_test.txt')
        self.assertTrue(exists(proto_path))
        with open(proto_path, 'r') as f:
            content = f.read()
        self.assertEqual(content, expect_txt)

    # def test_render_ext(self):
    #     self.cmd.run_from_argv(['yzrpc', 'createapp'])


if __name__ == '__main__':
    unittest.main()
