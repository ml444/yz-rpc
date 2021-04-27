#!/usr/bin/python3.7+
# -*- coding:utf-8 -*-
"""
@auth: cml
@date: 2021/4/8
@desc: ...
"""
import socket
from concurrent import futures

import grpc
import pytest

from ._mock import MockServer, MockChannel


@pytest.fixture(scope='module')
def grpc_address():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 0))
    return 'localhost:{}'.format(sock.getsockname()[1])


@pytest.fixture(scope='module')
def grpc_interceptors():
    return


@pytest.fixture(scope='module')
def current_server(request, grpc_address, grpc_interceptors):
    max_workers = request.config.getoption('grpc-max-workers', default=1)
    try:
        max_workers = max(request.module.grpc_max_workers, max_workers)
    except AttributeError:
        pass
    pool = futures.ThreadPoolExecutor(max_workers=max_workers)
    if request.config.getoption('grpc-fake', default=True):
        server = MockServer(pool)
        yield server
    else:
        server = grpc.server(pool, interceptors=grpc_interceptors)
        yield server
    pool.shutdown(wait=False)


@pytest.fixture(scope='module')
def grpc_server(current_server, grpc_address, grpc_add_to_server, current_servicer):
    grpc_add_to_server(current_servicer, current_server)
    current_server.add_insecure_port(grpc_address)
    current_server.start()
    yield current_server
    current_server.stop(grace=None)


@pytest.fixture(scope='module')
def grpc_create_channel(request, grpc_address, grpc_server):
    def _create_channel(credentials=None, options=None):
        if request.config.getoption('grpc-fake', default=True):
            return MockChannel(grpc_server, credentials)
        if credentials is not None:
            return grpc.secure_channel(grpc_address, credentials, options)
        return grpc.insecure_channel(grpc_address, options)

    return _create_channel


@pytest.fixture(scope='module')
def grpc_channel(grpc_create_channel):
    with grpc_create_channel() as channel:
        yield channel


@pytest.fixture(scope='module')
def grpc_stub(grpc_stub_cls, grpc_channel):
    return grpc_stub_cls(grpc_channel)


def pytest_addoption(parser):
    parser.addoption('--grpc-fake-server', action='store_true', dest='grpc-fake')
    parser.addoption('--grpc-max-workers', type=int, dest='grpc-max-workers', default=1)
