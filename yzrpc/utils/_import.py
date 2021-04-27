#!/usr/bin/python3.7+
# -*- coding:utf-8 -*-
"""
@auth: cml
@date: 2021/3/31
@desc: ...
"""
import sys
from importlib import import_module

__all__ = [
    "get_module_attr"
]


def get_module_attr(dotted_path):
    """
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError as err:
        raise ImportError(
            "%s doesn't look like a module path" % dotted_path) from err

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError as err:
        raise ImportError(
            'Module "%s" does not define a "%s" attribute/function/class' % (
                module_path, class_name)
        ) from err


def import_string(import_name):
    import_name = str(import_name).replace(':', '.')
    try:
        __import__(import_name)
    except ImportError:
        if '.' not in import_name:
            raise
    else:
        return sys.modules[import_name]

    module_name, obj_name = import_name.rsplit('.', 1)
    module = __import__(module_name, None, None, [obj_name])
    try:
        return getattr(module, obj_name)
    except AttributeError as e:
        raise ImportError(e)