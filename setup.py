#!/usr/bin/python3.7+
# -*- coding:utf-8 -*-
"""
rm -rf dist/*
python setup.py sdist bdist_wheel

python3 -m twine uplaod dist/*
python3 -m twine upload --repository testpypi dist/*
python3 -m twine upload --repository-url http://hostname/repository/pypi-hosted/ dist/* -u username -p password
"""
import os
# import re
# import ast
from setuptools import setup, find_packages
from yzrpc import __version__

# _version_re = re.compile(r'__version__\s+=\s+(.*)')
_root = os.path.abspath(os.path.dirname(__file__))

# with open(os.path.join(_root, 'yzrpc/__init__.py')) as f:
#     node = _version_re.search(f.read()).group(1)
#     version = str(ast.literal_eval(node))

with open(os.path.join(_root, 'requirements.txt')) as f:
    requirements = f.readlines()

with open(os.path.join(_root, 'README.md')) as f:
    readme = f.read()

src_dir = os.path.dirname(os.path.realpath(__file__))
if os.name == "nt":
    src_dir = os.path.relpath(src_dir)


def sources(names):
    """ transform a list of sources to be relative to py_dir """
    return ["%s/%s" % (src_dir, n) for n in names]


def find_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return filepaths


setup(
    name='yzrpc',
    version=__version__,
    description='A gRPC framework for automatically generating protobuf files.',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/ml444/yz-rpc',
    author='cml',
    author_email='caimengli0660@gmail.com',
    license='Apache License Version 2.0',
    classifiers=[
        # 发展时期,常见的如下
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",
        'Environment :: Web Environment',
        'Intended Audience :: Developers',  # 开发的目标用户
        "Operating System :: MacOS",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: BSD",
        "Operating System :: POSIX :: Linux",

        "License :: OSI Approved :: Apache Software License",

        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',

        # 属于什么类型
        'Topic :: Internet',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords=['rpc', 'grpc', 'async', 'yzrpc'],
    packages=find_packages(exclude=['tests']),
    package_data={'yzrpc': find_package_data('yzrpc')},
    python_requires='>=3.6',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'yzrpc=yzrpc.__main__:main'
        ],
        'extension_cmds': [
            'async_task=yzrpc.extensions.celery.cmd:async_task',
            'bus=yzrpc.extensions.celery.cmd:bus'
        ]
    },
    zip_safe=True,

    # scripts=sources(
    #     [
    #         "bin/yzrpc",
    #     ]
    # ),

    # 仅在测试时需要使用的依赖，在正常发布的代码中是没有用的。
    # 在执行python setup.py test时，可以自动安装这三个库，确保测试的正常运行。
    test_suite="tests",
    tests_require=[
        # "pytest",
        "grpcio>=1.35.0",
        "grpcio_tools>=1.35.0",
        "uvloop",
    ]
)


"""
# 库包含 C 扩展的模块

import os
import subprocess

from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        extdir = self.get_ext_fullpath(ext.name)
        if not os.path.exists(extdir):
            os.makedirs(extdir)

        # This is the temp directory where your build output should go
        install_prefix = os.path.abspath(os.path.dirname(extdir))
        cmake_args = '-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={}'.format(install_prefix)

        subprocess.check_call(['cmake', ext.sourcedir, cmake_args], cwd=self.build_temp)
        subprocess.check_call(['cmake', '--build', '.'], cwd=self.build_temp)

setup(
    name='name',
    version='0.0.3',
    author='xxx',
    author_email='',
    description='',
    ext_modules=[CMakeExtension('.')],
    py_modules=['纯py模块的名称'],
    cmdclass=dict(build_ext=CMakeBuild),
    zip_safe=False
)
"""
