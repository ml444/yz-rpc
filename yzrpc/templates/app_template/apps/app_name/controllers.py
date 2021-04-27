#!/usr/bin/python3.7+
# -*- coding:utf-8 -*-
"""
@auth: xxx
@date: 2020-9-
@desc: ...
"""
from sqlalchemy import text
from sqlalchemy.orm import Session
from yzcore.db.sqlalchemy_crud_base import OrmCRUDBase
from .models import Permissions


class PermissionController(OrmCRUDBase):
    def __init__(self):
        super().__init__(Permissions)

    def get_permission(
            self, db: Session,
            obj_id: int, obj_type: int,
            organiz_id: int, user_id: int
    ):
        """
        获取权限

        :param db:
        :param obj_id:
        :param obj_type:
        :param organiz_id:
        :param user_id:
        :return:
        """
        query = dict(
            object_id=obj_id,
            object_type=obj_type,
            organiz_id=organiz_id,
            user_id=user_id
        )
        pm_obj = self.get_one(db, **query)
        if pm_obj:
            return pm_obj.permission
        return 0