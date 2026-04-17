#匹配记录表
from datetime import datetime, timedelta
from enum import Enum

from tortoise import Model, fields
from tortoise import fields, timezone as dt_timezone


class MatchRecord(Model):
    """匹配记录模型"""
    id = fields.IntField(pk=True, index=True)
    created_at = fields.DatetimeField(auto_now_add=True, null=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, null=True, description="更新时间")
    
    class MatchType(str, Enum):
        LONG_TERM = "long_term"
        INSTANT = "instant"
    
    # 匹配双方
    user1 = fields.ForeignKeyField("models.User", related_name="matches_as_user1")
    user2 = fields.ForeignKeyField("models.User", related_name="matches_as_user2", null=True, description="被匹配用户，可为空表示匹配失败")

    # 匹配的兴趣
    interest = fields.ForeignKeyField("models.Interest", related_name="match_records")

    # 类型：长期 / 即时
    match_type = fields.CharEnumField(MatchType)

    #匹配状态 枚举：匹配中，已经匹配，已过期
    class MatchStatus(str, Enum):
        MATCHING = "matching"  # 匹配中
        MATCHED = "matched"    # 已经匹配
        EXPIRED = "expired"    # 已过期
    status = fields.CharEnumField(MatchStatus, default=MatchStatus.MATCHING)
    
    # 过期时间（用于长期匹配）
    expire_at = fields.DatetimeField(null=True, description="过期时间")

    @property
    def is_expired(self) -> bool:
        """判断匹配是否过期"""
        # 即时匹配：20分钟过期
        if self.match_type == self.MatchType.INSTANT.value:
            if not self.created_at:
                return False
            now = datetime.now(dt_timezone.utc)
            expire_time = self.created_at + timedelta(minutes=20)
            return now > expire_time
        # 长期匹配：使用expire_at字段
        elif self.match_type == self.MatchType.LONG_TERM.value:
            if not self.expire_at:
                return False
            now = datetime.now(dt_timezone.utc)
            return now > self.expire_at
        return False

    class Meta:
        table = "match_record"
        description = "匹配记录表"
        # 添加索引以提高查询效率
        indexes = [
            ["interest_id", "match_type", "status"],
            ["user1_id"],
            ["user2_id"],
            ["expire_at"],
        ]