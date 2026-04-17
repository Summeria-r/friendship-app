from datetime import datetime, timedelta

from tortoise import Model, fields
from tortoise import fields, timezone as dt_timezone


class InstantMatchWait(Model):
    """即时匹配等待模型"""
    id = fields.IntField(pk=True, index=True)
    clicked_at = fields.DatetimeField(auto_now_add=True, description="点击时间")
    updated_at = fields.DatetimeField(auto_now=True, null=True, description="更新时间")
    
    # 谁发起的即时匹配
    user = fields.ForeignKeyField(
        "models.User",
        related_name="instant_waits",
        on_delete=fields.CASCADE
    )

    # 要匹配哪个兴趣 ✅ 关联兴趣表
    interest = fields.ForeignKeyField(
        "models.Interest",
        related_name="instant_waits"
    )

    # 是否已匹配成功（成功了就从队列移除）
    is_matched = fields.BooleanField(default=False)

    class Meta:
        table = "instant_match_wait"
        description = "即时匹配等待表"
        # 添加索引以提高查询效率
        indexes = [
            ["interest_id", "is_matched", "clicked_at"],
        ]
        ordering = ["-clicked_at"]

    @property
    def is_expired(self) -> bool:
        """判断是否超时(20 分钟)"""
        # 获取当前 UTC 时间（和 Tortoise 自动存储的时间一致）
        now = datetime.now(dt_timezone.utc)
        # 超时时间 = 点击时间 + 20 分钟
        expire_time = self.clicked_at + timedelta(minutes=20)
        # 当前时间 > 超时时间 → 已超时
        return now > expire_time