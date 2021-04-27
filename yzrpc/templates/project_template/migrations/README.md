## 数据库迁移操作
```
# pip install alembic

alembic init migrations                             # 创建迁移环境
alembic revision --autogenerate -m "commit content" # 自动生成迁移文件
alembic upgrade head                                # 升级到最近版本
alembic upgrade <revision_id>                       # 升级到指定版本
alembic downgrade <revision_id>                     # 回退到指定版本
```