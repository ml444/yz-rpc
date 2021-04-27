#!/usr/bin/python3.7+
# -*- coding:utf-8 -*-
"""
@auth: cml
@date: 2021/4/8
@desc: ...
"""

import grpc
from grpc._cython.cygrpc import CompositeChannelCredentials, _Metadatum


class MockServer(object):
    def __init__(self, pool):
        self.handlers = {}
        self.pool = pool

    def add_generic_rpc_handlers(self, generic_rpc_handlers):
        from grpc._server import _validate_generic_rpc_handlers

        _validate_generic_rpc_handlers(generic_rpc_handlers)
        self.handlers.update(generic_rpc_handlers[0]._method_handlers)

    def start(self):
        pass

    def stop(self, grace=None):
        pass

    def add_secure_port(self, target, server_credentials):
        pass

    def add_insecure_port(self, target):
        pass


class MockRpcError(RuntimeError, grpc.RpcError):
    def __init__(self, code, details):
        self._code = code
        self._details = details

    @property
    def code(self):
        return self._code

    @property
    def details(self):
        return self._details


class MockContext(object):
    def __init__(self):
        self.code = grpc.StatusCode.OK
        self.details = None
        self._invocation_metadata = None

    def abort(self, code, details):
        raise MockRpcError(code, details)

    def set_code(self, code):
        self.code = code

    def set_details(self, details):
        self.details = details

    def initial_metadata(self, metadata):
        self._invocation_metadata = metadata

    def invocation_metadata(self):
        return self._invocation_metadata


class MockChannel:
    def __init__(self, mock_server, credentials):
        self.server = mock_server
        self._crts = credentials

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def mock_method(self, method_name, uri, *args, **kwargs):
        handler = self.server.handlers[uri]
        real_method = getattr(handler, method_name)

        def mock_handler(request, context):
            def metadata_callbak(metadata, error):
                context._invocation_metadata.extend(
                    (_Metadatum(k, v) for k, v in metadata))

            if self._crts and isinstance(
                    self._crts._credentials,
                    CompositeChannelCredentials
            ):
                for call_cred in self._crts._credentials._call_credentialses:
                    call_cred._metadata_plugin._metadata_plugin(context, metadata_callbak)
            future = self.server.pool.submit(real_method, handler, request, context)
            return future.result()

        return mock_handler

    def unary_unary(self, *args, **kwargs):
        return self.mock_method('unary_unary', *args, **kwargs)

    def unary_stream(self, *args, **kwargs):
        return self.mock_method('unary_stream', *args, **kwargs)

    def stream_unary(self, *args, **kwargs):
        return self.mock_method('stream_unary', *args, **kwargs)

    def stream_stream(self, *args, **kwargs):
        return self.mock_method('stream_stream', *args, **kwargs)


class Stub:
    def __init__(self, servicer=None):
        self.servicer = servicer

    def __getattr__(self, handler):
        return self._handler_wrapper(getattr(self.servicer, handler))

    def _handler_wrapper(self, handler):
        def wrapped(msg, metadata=None):
            self.ctx = MockContext()
            self.ctx.initial_metadata(metadata)
            return handler(msg, self.ctx)
        return wrapped
