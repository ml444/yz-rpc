#!/usr/bin/python3.7+
# -*- coding:utf-8 -*-
"""
@auth: cml
@date: 2021-04-20 18:17
@desc: ...
"""
import unittest

if __name__ == "__main__":
    target_dir = './'
    discover = unittest.defaultTestLoader.discover(target_dir, pattern='test_*.py')

    runner = unittest.TextTestRunner()
    runner.run(discover)


'''
class TestExample(unittest.TestCase):
    @unittest.skip("原因：心情不好")
    def test_1(self):
        pass

    @unittest.skipIf(sys.platform.startswith('linux'), "No requires Linux")
    def test_2(self):
        pass

    @unittest.skipUnless(sys.platform.startswith('win'), "requires Windows ")
    def test_3(self):
        pass


def main1():
    """用例的指定顺序执行(默认执行顺序是根据用例名称升序进行)"""
    tests = [TestExample('test_3'), TestExample('test_2'), TestExample('test_1')]
    suite = unittest.TestSuite()
    suite.addTests(tests)

    runner = unittest.TextTestRunner()
    runner.run(suite)


def main2():
    """
    生成html格式的测试报告
    pip install html-testRunner
    """
    from HtmlTestRunner import HTMLTestRunner

    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExample))

    runner = HTMLTestRunner(output='result')
    runner.run(suite)


if __name__ == '__main__':
    main1()
'''