#!/usr/bin/python3.6.8+
# -*- coding:utf-8 -*-
"""
@auth: cml
@date: 2020-12-2
@desc: ...
"""


class JobStatus(object):
    PENDING = 0  # 任务等待执行

    STARTED = 100  # 任务执行开始
    PROCESS = 110
    POLLING = 120
    CALLBACK = 130

    SUCCESS = 200   # 任务执行成功
    RETRY = 300     # 任务重试
    FAILURE = 400   # 任务执行失败
    REVOKED = 500   # 任务撤销

