import asyncio
import logging
import typing
from concurrent import futures
from inspect import isfunction

import grpc

from yzrpc import exceptions as exp
from yzrpc.servicer import load_services
from yzrpc.utils import get_module_attr
from yzrpc.proto import __proto_meta__
from yzrpc.config import settings
from yzrpc._types import ServerType


logger = logging.getLogger(__name__)


class Server(typing.Generic[ServerType]):
    def __init__(
            self,
            host: str = None,  # '[::]',
            port: int = None,  # 50051,
            max_workers: int = None,
            middlewares: typing.List = None,
            is_async: bool = False
    ):
        """

        :param host:
        :param port:
        :param middlewares:
        :param max_workers:
        """
        self._host = host if host else settings.GRPC_SERVER_HOST
        self._port = port if port else settings.GRPC_SERVER_PORT
        self._max_workers = max_workers if max_workers else settings.GRPC_SERVER_MAX_WORKERS
        self._middlewares = middlewares

        self.is_async = is_async
        # self.setup_logger()
        self._stopped = False

        self._services = []
        self._init_server()

    def _init_server(self):
        """
        :return: Server()
        """
        # 加载中间件
        self.load_middlewares()

        max_concurrent_rpcs = settings.GRPC_SERVER_MAXIMUM_CONCURRENT_RPCS
        options = settings.GRPC_SERVER_OPTIONS
        if self.is_async:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._server = grpc.aio.server(
                migration_thread_pool=futures.ThreadPoolExecutor(max_workers=self._max_workers),
                interceptors=self._middlewares,
                maximum_concurrent_rpcs=max_concurrent_rpcs,
                options=options
            )
        else:
            self._server = grpc.server(
                thread_pool=futures.ThreadPoolExecutor(max_workers=self._max_workers),
                interceptors=self._middlewares,
                maximum_concurrent_rpcs=max_concurrent_rpcs,
                options=options
            )

        load_services('apps')
        self.register_servicers()
        self._server.add_insecure_port('%s:%s' % (self._host, self._port))

    def load_middlewares(self):
        """
        加载中间件，有两种加载方式：
        方式一：
            通过settings配置中间件的路径
            class Setting(DefaultSetting):
                GRPC_SERVER_MIDDLEWARES=['dotted.path.to.callable_middlewares',]

        方式二：
            在Server()实例化时传入：
            Server(middlewares=[<CALLABLE_MIDDLEWARES>, ...])

        :return:
        """
        middlewares = self._load_middlewares_from_path()
        if self._middlewares:
            self._validate_middles(self._middlewares)
            self._middlewares.extend(middlewares)
        else:
            self._middlewares = middlewares

    def _load_middlewares_from_path(self) -> list:
        """
        通过settings配置中间件的路径
        :return: List[<CALLABLE_MIDDLEWARES>, ...]
        """
        # TODO 中间件优先级排序功能
        result = []
        for middleware_path in settings.GRPC_SERVER_MIDDLEWARES:
            logger.debug("Initializing middleware from %s", middleware_path)
            result.append(get_module_attr(middleware_path)())
        return result

    def _validate_middles(self, middlewares: typing.List):
        """验证中间件的正确性"""
        for middle in middlewares:
            if not isfunction(middle):
                raise exp.InvalidMiddleware(f"{middle} is not callable.")
        # TODO：封装中间件基类

    def register_servicers(self):
        """
        my_app1_pb2_grpc.add_MyApp1Servicer_to_server(MyApp1Servicer(), server)
        :return:
        """
        rpc_module_path = "src.services"
        for app_name, protoinfo in __proto_meta__.items():
            for srv in protoinfo.services:
                service_cls = get_module_attr(srv.path)
                service = service_cls()
                self._services.append(service)
                _path = "{}.{}_pb2_grpc.add_{}Servicer_to_server".format(
                    rpc_module_path, app_name, srv.name)
                rpc_srv = get_module_attr(_path)
                rpc_srv(service, self._server)

    def run(self):
        if self.is_async:
            asyncio.run_coroutine_threadsafe(self.async_run(), self._loop)

        else:
            self._server.start()
        # signals.server_started.send(self)
        # self.register_signal()
        # while not self._stopped:
        #     time.sleep(1)
        # signals.server_stopped.send(self)
        return True

    async def async_run(self):
        return await self._server.start()

    def wait_for_termination(self, timeout: typing.Any=None):
        if self.is_async:
            return self._loop.run_until_complete(self._server.wait_for_termination(timeout=timeout))
        else:
            return self._server.wait_for_termination(timeout=timeout)

    async def async_wait_for_termination(self, timeout):
        return await self._server.wait_for_termination(timeout=timeout)

    def clean_useless_data(self):
        """清除无用数据"""

    # def setup_logger(self):
    #     fmt = self.app.config['GRPC_LOG_FORMAT']
    #     lvl = self.app.config['GRPC_LOG_LEVEL']
    #     h = self.app.config['GRPC_LOG_HANDLER']
    #     h.setFormatter(logging.Formatter(fmt))
    #     logger = logging.getLogger()
    #     logger.setLevel(lvl)
    #     logger.addHandler(h)
    #
    # def register_signal(self):
    #     signal.signal(signal.SIGINT, self._stop_handler)
    #     signal.signal(signal.SIGHUP, self._stop_handler)
    #     signal.signal(signal.SIGTERM, self._stop_handler)
    #     signal.signal(signal.SIGQUIT, self._stop_handler)
    #
    # def _stop_handler(self, signum, frame):
    #     grace = self.app.config['GRPC_GRACE']
    #     self.server.stop(grace)
    #     time.sleep(grace or 1)
    #     self._stopped = True








