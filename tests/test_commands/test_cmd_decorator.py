import unittest
from yzrpc.commands import CmdDecorator


class TestCmdDecorator(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cmd = CmdDecorator()

        @cmd.run('runtest')
        @cmd.attribute(description='This is a description.')
        @cmd.attribute(epilog='This is an epilog.')
        @cmd.argument('name')
        @cmd.argument('sub')
        def handle(**kwargs):
            # print(kwargs)
            return kwargs

        cls._func = lambda cls, *args: handle(*args)  # 函数直接赋值给变量会变成方法
        cls.cmd = cmd

    def test_subcmd(self):
        self.assertEqual(self.cmd.subcmd, 'runtest')

    def test_attribute(self):
        self.assertTrue(hasattr(self.cmd._cmd_ins, 'description'))
        self.assertTrue(hasattr(self.cmd._cmd_ins, 'epilog'))
        self.assertEqual(getattr(self.cmd._cmd_ins, 'description'), 'This is a description.')
        self.assertEqual(getattr(self.cmd._cmd_ins, 'epilog'), 'This is an epilog.')

    def test_func(self):
        res = self._func('namexxx', 'subxxx')
        expect_dict = {'name': 'namexxx', 'sub': 'subxxx'}
        self.assertDictEqual(res, expect_dict)



