#!/usr/bin/python3.7+
# -*- coding:utf-8 -*-
"""
@auth: cml
@date: 2021/3/19
@desc: ...
"""
from collections import defaultdict
from typing import DefaultDict, Dict, List, AnyStr, Set

from yzrpc._types import ServiceType


class Protobuf:
    def __init__(self):
        self.modules: Set[str] = set()
        self.messages: Dict[AnyStr, Dict] = dict()
        self.services: List[ServiceType] = list()

    @classmethod
    def get_obj(cls, name=None, module=None):
        # module: 'src.apps.appname.schemas'
        if not any((name, module)):
            raise ValueError("not any((name, module))")
        if name is None:
            # TODO: validate_module_path
            name = module.split('.')[-2]
        if name in __proto_meta__:
            package_meta = __proto_meta__.get(name)
        else:
            package_meta = cls()
        return package_meta


__proto_meta__: DefaultDict[str, Protobuf] = defaultdict(Protobuf)

"""
__proto_meta__: {
    "my_app1": {
        "modules": {"google/protobuf/struct.proto"},
        "messages": {
            'PermissionBase': {
                'object_id': int,
                'object_type': int,
                'parent_id': typing.Union[int, NoneType],
                'parent_type': typing.Union[int, NoneType]
            },
            ...
        },
        "services": [
            object{
                name: "MyApp1",
                module: "src.apps.appname.views",
                methods: [
                    object{
                        name="get_feature",
                        func=func,
                        typ=typ,
                        request_cls=request_type,
                        response_cls=response_type,
                    },
                    object{
                        name="list_features",
                        func=func,
                        request_typ=request_typ,
                        response_typ=response_typ,
                        request_cls=request_type,
                        response_cls=response_type,
                    }
                    ...
                ]
            }
        ]
    }
}
"""



