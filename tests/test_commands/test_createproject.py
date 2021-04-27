#!/usr/bin/python3.7+
# -*- coding:utf-8 -*-
"""
@auth: cml
@date: 2021/2/22
@desc: 测试创建工程命令
"""
import os
import unittest
from os.path import join, exists
from yzrpc.commands import CommandUtility, CommandError


class TestCreateProjectCommand(unittest.TestCase):
    def setUp(self) -> None:
        self.cmd = CommandUtility()
        self.project_name = 'myproject'
        self.target_path = './tgpath'
        self.template_path = './proj_tmp'
        # self.cmd.run_from_argv(['yzrpc', 'createproject', 'myproject'])

    def tearDown(self) -> None:
        del self.cmd
        import shutil
        # 删除创建的工程
        try:
            shutil.rmtree(self.project_name)
        except FileNotFoundError:
            pass
        try:
            shutil.rmtree(self.template_path)
        except FileNotFoundError:
            pass
        try:
            shutil.rmtree(self.target_path)
        except FileNotFoundError:
            pass

    def _judge_file_exist(self, src_path):
        self.assertTrue(exists(join(src_path, 'main.py')))
        self.assertTrue(exists(join(src_path, 'settings.py')))
        self.assertTrue(exists(join(src_path, 'apps', '__init__.py')))
        self.assertTrue(exists(join(src_path, 'conf', 'config_dev.yaml')))
        self.assertTrue(exists(join(src_path, 'conf', 'config_dev.ini')))
        self.assertTrue(exists(join(src_path, 'const')))
        # self.assertTrue(exists(join(src_path, 'protos')))
        self.assertTrue(exists(join(src_path, 'services', '__init__.py')))

    def test_no_project_name(self):
        try:
            self.cmd.run_from_argv(['yzrpc', 'createproject'])
        except SystemExit as e:
            self.assertEqual(e.args[0], 2)

    def test_project_name_with_path(self):
        expect_raise = "The project name can't have a path; " \
                       "please use the '-D' parameter for the path."
        with self.assertRaises(CommandError) as e:
            self.cmd.run_from_argv(['yzrpc', 'createproject', './myproj/projname'])
        exp = e.exception
        self.assertEqual(exp.args[0], expect_raise)

    def test_create_project_with_success(self):
        self.cmd.run_from_argv(['yzrpc', 'createproject', self.project_name])
        self.assertIn(self.project_name, os.listdir('.'))
        src_path = join(self.project_name, 'src')
        self._judge_file_exist(src_path)

    def test_target_path_with_not_exist(self):
        expect_raise = "Destination directory {} does not exist, " \
                       "please create it first.".format(
            os.path.abspath(os.path.expanduser(self.target_path))
        )
        with self.assertRaises(CommandError) as e:
            self.cmd.run_from_argv(
                ['yzrpc', 'createproject', self.project_name, '-D', self.target_path])
        exp = e.exception
        self.assertEqual(exp.args[0], expect_raise)

    def test_target_path_with_exist(self):
        os.mkdir(self.target_path)
        self.cmd.run_from_argv(
            ['yzrpc', 'createproject', self.project_name, '-D', self.target_path])
        src_path = join(self.target_path, self.project_name, 'src')
        self._judge_file_exist(src_path)

    def test_template_with_path_not_exist(self):
        expect_raise = "The template dir is not exist."
        with self.assertRaises(CommandError) as e:
            self.cmd.run_from_argv(
                ['yzrpc', 'createproject', self.project_name, '-T', self.template_path])
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
            ['yzrpc', 'createproject', self.project_name, '-T', self.template_path]
        )
        proto_path = join(self.project_name, 'temp_test.txt')
        self.assertTrue(exists(proto_path))
        with open(proto_path, 'r') as f:
            content = f.read()
        self.assertEqual(content, expect_txt)

    # def test_render_ext(self):
    #     self.cmd.run_from_argv(['yzrpc', 'createproject', 'myproject'])


if __name__ == '__main__':
    unittest.main()
