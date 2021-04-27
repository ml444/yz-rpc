# [Yz-RPC](https://github.com/ml444/yz-rpc)
--------------

## Introduction
A gRPC framework for automatically generating protobuf files.
一个自动生成protobuf文件的grpc框架。

The purpose of `yzrpc` is to write code in a development method similar 
to http WEB when developing back-end RPC services. The command line generates 
protobuf with one click without paying attention to the writing on the protobuf file. 
At the same time, it provides a code structure specification reference.

yzrpc 目的为了开发后端RPC服务时，能够以类似http WEB的开发方式编写代码，
命令行一键生成protobuf，而不必过关注protobuf协议文件上的编写，
同时提供一种代码结构规范参考。


## Quick start
可以通过`createproject`和`createtapp`两个命令快速创建工程和内部的接口应用模块。
**安装模块**
```shell
$ pip install yzrpc
```
示例：
1. 创建工程：
    ```shell
    $ yzrpc createproject myproject
    ```
    **注意：** *创建项目时会检测当前目录是否与项目名同名，
    如果同名默认已经创建工程根目录，会询问是否覆盖该工程。*

2. 创建工程内部应用：
    ```shell
    $ yzrpc createapp myapp01 -D ./myproject/src
    
    # 或者
    $ cd myproject
    $ yzrpc createapp myapp01
    ```
    
    经过`createproject` 和 `createapp`两个命令后，会产生如下的代码结构：
    ```
    .
    ├── docs		        说明文档、接口文档等文档的存放目录
    ├── migrations		    数据表迁移文件存放目录
    ├── src
    │   ├── apps 接口应用程序的主目录
    │   │   ├── __init__.py
    │   │   ├── myapp01
    │   │       ├── __init__.py
    │   │       ├── controllers.py  控制层：封装数据交互操作
    │   │       ├── models.py       模型层：实现数据表与模型的定义
    │   │       ├── schemas.py      模式层：定义接口数据参数
    │   │       ├── tests.py        单元测试文件
    │   │       └── views.py        视图层：接口定义层
    │   ├── __init__.py
    │   ├── conf/		    配置文件的存放目录
    │   ├── const/		    公共常量存放目录
    │   ├── protos/		    protobuf文件存放目录
    │   ├── services/		通过grpc-tools生成的服务调用模块的存放目录
    │   ├── utils/		    抽离出的公共代码模块存放目录
    │   ├── settings.py	程序的设置文件
    │   └── main.py		程序的入口文件
    ├── .gitignore
    ├── requirements.txt
    └── README.md
    ```
    
    生成的MVCS(`models`,`views`, `controllers`, `schemas`)模版中，
    需要注意`schemas.py`和`views.py`，因为它们是生成protobuf的关键。
    
    在生成的代码模版中，已经提供相关的示例：
    `schemas.py`:
    ```python
    from enum import Enum
    from typing import (
        Optional, Any, List, Tuple, Dict,
        Mapping, Union, Sequence, Iterable
    )
    from yzrpc.schema import SchemaBase
    
    
    class CommonBase(SchemaBase):
        class Config:
            orm_mode = True
    
    
    class EnumExample(Enum):
        A = 1
        B = 2
        C = 3
    
    
    class EmbedInfo(CommonBase):
        name: str
        age: int
    
    
    class SchemaExample(CommonBase):
        int_exa: int
        str_exa: str
        bool_exa: bool
        float_exa: float
        bytes_exa: bytes
        tuple_exa: tuple
        list_exa: list
        dict_exa: dict
        enum_exa: EnumExample
        embed_exa: EmbedInfo
    
        exa_any: Any
        exa_list: List
        exa_tuple: Tuple
        exa_dict: Dict[str, int]
        exa_mapping: Mapping[str, int]
        exa_list_embed: List
        exa_sequence: Sequence[int]
        exa_iterable: Iterable[str]
        exa_list_multi: List[EmbedInfo]
        exa_union: Union[int, EmbedInfo, EnumExample, str]  # 不推荐
        exa_optional: Optional[EmbedInfo]                   # 不推荐
        exa_optional_multi: Optional[EmbedInfo]             # 不推荐
        exa_optional_multi_l: Optional[list]                # 不推荐
 
    ```
    `schemas.py`是继承于`pydantic`这个库来进行类型检测的，
    在`schemas.py`中定义rpc接口的请求类型和响应类型。
    **注意：** 请求类型和响应类型必须继承于`SchemaBase`这个基类。
    
    `views.py`:
    ```python
    from typing import Iterable, Iterator
    from yzrpc.servicer import ServicerBase, GRPCMethod
    
    # from src.services import myapp01_pb2
    # from src.services import myapp01_pb2_grpc
    
    from .schemas import SchemaExample
    
    
    class Myapp01Servicer(ServicerBase):
        @GRPCMethod(before_requests=[], after_responses=[])
        def get_one(self, request: SchemaExample, context) -> SchemaExample:
            return request
    
        @GRPCMethod()
        def get_some(self, request: Iterator[SchemaExample], context) -> Iterable[SchemaExample]:
            return request
    
        @GRPCMethod()
        def list_some(self, request: SchemaExample, context) -> Iterable[SchemaExample]:
            pass
    
        @GRPCMethod()
        def update_some(self, request: Iterator[SchemaExample], context) -> SchemaExample:
            pass
    ```
    需要变成RPC接口的方法用`GRPCMethod()`封装，可传入`before_requests`和`after_responses`参数，作为该接口的预处理操作。
    **注意：** 请求参数的和返回参数的类型标注不可忽略不写，该类型标注是生成protobuf协议的service数据的关键。
    
3. 在app的MVCS模块编写相关的业务代码后，运行命令生成protobuf文件:
    ```shell
    $ yzrpc generateproto
    ```
    ```shell
    $ tree ./src/protos 
    ./src/protos
    └── myapp01.proto
    ```

4. 根据protobuf文件生成pb模块：
    ```shell
    $ yzrpc generatemodule
    
    $ tree ./src/services 
    ./src/services
    ├── __init__.py
    ├── myapp01_pb2.py
    └── myapp01_pb2_grpc.py
    ```

5. 编写单元测试
    在`myproject/src/apps/myapp01/tests.py`中，提供了单元测试模版：
    ```python
    import pytest
    from yzrpc.tests import *
    
    
    from src.services.myapp01_pb2 import SchemaExample
    
    
    @pytest.fixture(scope='module')
    def grpc_add_to_server():
        from src.services.myapp01_pb2_grpc import add_Myapp01Servicer_to_server
        return add_Myapp01Servicer_to_server
    
    
    @pytest.fixture(scope='module')
    def current_servicer():
        from .views import Myapp01Servicer
        return Myapp01Servicer
    
    
    @pytest.fixture(scope='module')
    def grpc_stub(grpc_channel):
        from src.services.myapp01_pb2_grpc import Myapp01Stub
    
        return Myapp01Stub(grpc_channel)
    
    # 测试用例
    def test_get_one(grpc_stub):
        request = SchemaExample(int_exa=1, str_exa='test')
        context = MockContext()
        response = grpc_stub.get_one(request, context)
        assert isinstance(response, SchemaExample)
        assert response.int_exa == 1
        assert response.str_exa == 'test'
    ```
    开发人员只需关注最下面的测试用例即可，之上的是根据app不同自动导入的模块。无需理会。
    开发人员根据需要扩展测试用例。
    该测试模块是基于`pytest`构建的，运行测试时，需要安装`pytest`。
    
    运行测试：
    ```shell
    $ yzrpc runtest
    ```
    该命令会自动搜索项目下的所有`tests.py`文件。
    
6. 启动服务
    ```shell
    $ python src/main.py
    ===>当前环境为：dev!导入的配置文件为：config_dev.ini

         _  _  ____  ____  ____   ___ 
        ( \/ )(_   )(  _ \(  _ \ / __)
         \  /  / /_  )   / )___/( (__ 
         (__) (____)(_)\_)(__)   \___)
        
    Starting server at 2021-04-23 11:35:28.902143
    Server is listening port 50051
    Registered handlers:
    ===> -------------->myapp01<---------------
    ===> Myapp01: get_one(SchemaExample) -> SchemaExample
    ===> Myapp01: get_some(SchemaExample) -> SchemaExample
    ===> Myapp01: list_some(SchemaExample) -> SchemaExample
    ===> Myapp01: update_some(SchemaExample) -> SchemaExample
    ```
    服务的启动参数有:
    - --host=localhost
    - --port=50051
    - --max_workers=1   # 最大线程数
    - --autoreload      # 自动重载功能，开发阶段使用
    - --async           # 该参数启动异步协程方式
    
    这些参数都封装在settings里，可以根据需要修改配置。
    
7. 客户端调用
    ```python
    from yzrpc.client import Client
    from src.apps.myapp01.schemas import SchemaExample

    with Client('localhost:50051', 'myapp01', 'Myapp1') as client:
        request = SchemaExample(str_exa='testing', ...)
        response = client.call('get_one', request)
        print(response)
        print(type(response))
        print(response.str_exa)
    ```
    或者：
    ```python
    from yzrpc.client import Client
    from src.apps.myapp01.schemas import SchemaExample

    client = Client('localhost:50051', 'myapp01', 'Myapp1')
    request = SchemaExample(str_exa='testing', ...)
    response = client.call('get_one', request)
    print(response)
    print(type(response))
    print(response.str_exa)
    client.close()
    ```
    根据具体业务开发需求进行二次封装。

## Documentation

[暂无](https://github.com/ml444/yz-rpc/README.md).

