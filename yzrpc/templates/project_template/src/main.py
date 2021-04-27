#!/usr/bin/python3.7+
# -*- coding:utf-8 -*-
"""
@auth:
@date: 2020-9-13
@desc: ...
"""
import sys
sys.path.append('.')
sys.path.append('..')

from settings import settings
from yzrpc.commands import CommandUtility


if __name__ == '__main__':
    cmd = CommandUtility()
    cmd.run_from_argv([
        'yzrpc', 'runserver',
        '--host', settings.GRPC_SERVER_HOST,
        '--port', str(settings.GRPC_SERVER_PORT),
        '--max_workers', str(settings.GRPC_SERVER_MAX_WORKERS),
        '--autoreload' if settings.DEBUG else '',
        '--async' if settings.START_ASYNC else '',
    ])



