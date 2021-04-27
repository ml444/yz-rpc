#!/usr/bin/python3.6+
# -*- coding:utf-8 -*-
"""
@auth: cml
@date: 2020-9-13
@desc: ...
"""
import os
from typing import Optional, Tuple, List, Union

try:
    import yaml
except:
    yaml = None

from pydantic import BaseSettings, AnyUrl, DirectoryPath


__all__ = [
    "DefaultSetting", "settings", "get_configer",
    "get_ini_section_to_dict"
]


def get_src_path() -> str:
    _path = os.getcwd()
    if 'src' in os.listdir(_path):
        _path = os.path.join(_path, 'src')
    return _path


class DefaultSetting(BaseSettings):
    is_configured: bool = False
    command_path: DirectoryPath = None
    src_path: str = get_src_path()
    # src_path: str = "/Users/cml/cmlpy/xyz/yz-rpc"

    def __init_subclass__(cls, **kwargs):
        """"""
        super().__init_subclass__()
        reload_reload_settings(cls())

    class Config:
        case_sensitive = False  # 是否区分大小写

    DEBUG: bool = False
    # SECRET_KEY: str = get_random_secret_key()

    # ============================================
    PROTO_TEMPLATE_ROOT = ""
    PROTO_TEMPLATE_PATH = "protos"

    # >>>>>>>>>>>>>>>>>>>>>>>>>> GRPC >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # >>>>>>>>>>>>>>>>>>>>>>>>>> GRPC >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # 地址
    GRPC_SERVER_HOST: str = "[::]"
    # 端口
    GRPC_SERVER_PORT: int = 50051

    # 最大线程数
    GRPC_SERVER_MAX_WORKERS: int = None

    # 多进程支持，可以使用`multiprocessing.cpu_count()`
    GRPC_SERVER_PROCESS_COUNT: int = 1

    # RPC Server的中间件导入列表：['dotted.path.to.callable_interceptor', ...]
    GRPC_SERVER_MIDDLEWARES: List = []

    # 键值对的可选列表用于配置通道：[("grpc.max_receive_message_length", 1024*1024*100)]
    GRPC_SERVER_OPTIONS: List[Tuple[str, Union[str, int, bool]]] = []

    # 服务器的最大并发rpcs数
    GRPC_SERVER_MAXIMUM_CONCURRENT_RPCS: Optional[int] = None

    # 启动后是否阻塞
    GRPC_SERVER_RUN_WITH_BLOCK: bool = True

    # 健康检测
    GRPC_HEALTH_CHECKING_ENABLE = True
    GRPC_HEALTH_CHECKING_THREAD_POOL_NUM = 1

    # Server Reflection
    GRPC_SEVER_REFLECTION_ENABLE = False

    # gRPC Service Third-Part Package Support
    GRPC_THIRD_PART_PACKAGES: List[str] = []
    # <<<<<<<<<<<<<<<<<<<<<<<<<<< GRPC <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    # <<<<<<<<<<<<<<<<<<<<<<<<<<< GRPC <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # logger
    # LOGGER_LEVEL = logging.INFO
    # LOGGER_FORMATTER: str = "[PID %(process)d] %(message)s"


settings = DefaultSetting()


def reload_reload_settings(instance):
    # settings = default_setting
    for k, v in settings.__fields__.items():
        val = getattr(instance, k)
        setattr(settings, k, val)
    # 配置已经被加载过的标志
    settings.is_configured = True


def get_configer(ext: str = "ini", import_path=os.curdir):
    profile = os.environ.get('ENV_PROFILE', 'dev')
    if profile == 'production':
        configname = 'config_production'
    elif profile == 'testing':
        configname = 'config_testing'
    else:
        configname = 'config_dev'
    print(f"===>当前环境为：{profile}!导入的配置文件为：{configname}.{ext}")

    base_path = os.path.abspath(import_path)
    _path = os.path.join(base_path, "conf", f"{configname}.{ext}")

    if ext in ["ini", "cfg"]:
        import configparser
        conf = configparser.ConfigParser()
        conf.read(_path)
    elif ext in ["yaml", "yml"]:
        if yaml is not None:
            raise ImportError("Need to install PyYaml")
        conf = yaml.safe_load(open(_path))
    else:
        raise AttributeError(f"暂不支持该文件格式: {ext}")
    return conf


def get_ini_section_to_dict(
        section: str,
        exclude: set = None,
        conf_parser=None
) -> dict:
    """
    获取ini配置文件某个节选的全部数据，转换成字典

    :param section: 节选名称
    :param exclude: 排除的字段
    :param conf_parser: 配置解析器
    :return:
    """
    conf_dict = dict()
    for k in conf_parser.options(section):
        if exclude and k in exclude:
            break
        conf_dict[k] = conf.get(section, k)
    return conf_dict





if __name__ == '__main__':
    conf = get_configer("ini")

