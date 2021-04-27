#!/usr/bin/python3.7+
# -*- coding:utf-8 -*-
"""
@auth: xxx
@date: 2020-9-
@desc: ...
"""
from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy import String, Integer, DateTime, Float
# from sqlalchemy.orm import relationship
# from datetime import datetime

from yzcore.db.sqlalchemy_crud_base import Base


class Permissions(Base):
    __tablename__ = 'permissions'
    id = Column(Integer, primary_key=True)