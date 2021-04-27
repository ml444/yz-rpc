#!/usr/bin/python3.7+
# -*- coding:utf-8 -*-
from typing import Tuple

from pydantic.main import BaseModel
from yzrpc.proto import __proto_meta__, Protobuf


class SchemaMeta(type):
    def __new__(cls, cls_name: str, bases: Tuple, cls_dict: dict):
        if not bases or object in bases:
            return super().__new__(cls, cls_name, bases, cls_dict)

        _meta = {
            k: v
            for k, v in cls_dict.get("__annotations__", {}).items()
            if not k.startswith('_')
        }
        if _meta:
            # 'src.apps.appname.schemas'
            _module = cls_dict.get("__module__", '')
            # TODO: validate_module_path
            app_name = _module.split('.')[-2]
            if app_name not in ['src', 'apps']:
                if app_name in __proto_meta__:
                    package_meta = __proto_meta__.get(app_name)
                else:
                    package_meta = Protobuf()
                package_meta.messages[cls_name] = _meta

                __proto_meta__[app_name] = package_meta
        return super().__new__(cls, cls_name, bases, cls_dict)


def metaclass_resolver(*classes):
    metaclass = tuple(set(type(cls) for cls in classes))
    metaclass = metaclass[0] if len(metaclass) == 1 else type(
        "_".join(mcls.__name__ for mcls in metaclass), metaclass, {})   # class M_C
    return metaclass("_".join(cls.__name__ for cls in classes), classes, {})


class _SchemaBase(metaclass=SchemaMeta):
    pass


class SchemaBase(metaclass_resolver(BaseModel, _SchemaBase)):
    pass


# class ModelSchemaMeta(ModelMetaclass, SchemaMeta):
#     pass
#
# from pydantic.main import ModelMetaclass
# class SchemaBase(BaseModel, metaclass=ModelSchemaMeta):
#     """"""

