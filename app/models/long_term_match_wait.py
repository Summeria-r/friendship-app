from datetime import datetime, timedelta
from tortoise import timezone as dt_timezone
from tortoise import Model, fields


class LongTermMatchWait(Model):
    """长期匹配等待模型"""
    id = fields.IntField(pk=True, index=True)
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, null=True, description="更新时间")
    
    # 发起匹配的用户
    user = fields.ForeignKeyField(
        "models.User",
        related_name="long_term_waits",
        on_delete=fields.CASCADE
    )
    
    # 目标兴趣（如考研）
    interest = fields.ForeignKeyField(
        "models.Interest",
        related_name="long_term_waits"
    )
    
    
    # 过期时间 默认时间是20分钟
    expire_at = fields.DatetimeField(
        null=True, 
        default=lambda: datetime.now(dt_timezone.utc) + timedelta(minutes=20), 
        description="过期时间")
    
    # 是否已匹配
    is_matched = fields.BooleanField(
        null=True, 
        default=False,
        description="是否已匹配")
    
    class Meta:
        table = "long_term_match_wait"
        description = "长期匹配等待表"
        indexes = [
            ["interest_id", "is_matched", "expire_at"],
        ]

    