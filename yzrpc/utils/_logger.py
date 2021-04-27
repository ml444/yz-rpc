#!/usr/bin/python3.7+
# -*- coding:utf-8 -*-
"""
@auth: cml
@date: 2021-04-16 21:08
@desc: ...
"""


__all__ = [
    "logger_has_level_handler",
]


def logger_has_level_handler(logger):
    """Check if there is a handler in the logging chain that will handle the
    given logger's :meth:`effective level <~logging.Logger.getEffectiveLevel>`.
    """
    level = logger.getEffectiveLevel()
    current = logger

    while current:
        if any(handler.level <= level for handler in current.handlers):
            return True

        if not current.propagate:
            break

        current = current.parent

    return False
