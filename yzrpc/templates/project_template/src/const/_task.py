#!/usr/bin/python3.6.8+
# -*- coding:utf-8 -*-
"""
@auth: cml
@date: 2020-12-2
@desc: ...
"""
from enum import Enum


class TaskType(str, Enum):
    MODEL = 'model'
    TEXTURE = 'texture'
    CUBEMAP = 'cubemap'
    SCENE = 'scene'
    UI = 'ui'
    FILE = 'file'


class TaskAction(str, Enum):
    CONVERT = 'convert'
    PROCESS = 'process'
    PACKAGE = 'package'
    DOWNLOAD = 'download'
    PUBLISH = 'publish'
    REPLACE = 'replace'
