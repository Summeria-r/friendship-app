# 数据库模型基类
from tortoise.models import Model
from tortoise import fields

# 所有数据库模型都继承这个基类
class BaseModel(Model):
    id = fields.IntField(pk=True, index=True)
    created_at = fields.DatetimeField(auto_now_add=True, null=True)
    updated_at = fields.DatetimeField(auto_now=True, null=True)

    class Meta:
        abstract = True  # 抽象基类，不会生成表