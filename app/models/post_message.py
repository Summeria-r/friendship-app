from enum import Enum

from tortoise import Model, fields


class Post_message(Model):
    
    """帖子消息模型"""
    id = fields.IntField(pk=True, index=True)
    created_at = fields.DatetimeField(auto_now_add=True, null=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, null=True, description="更新时间")
    # 通知类型枚举（严格对应所有场景，类型安全）
    class NotificationType(str, Enum):
        # 帖子相关
        POST_COMMENT = "post_comment"       # 有人评论了我的帖子
        POST_LIKE = "post_like"             # 有人点赞了我的帖子
        POST_COLLECT = "post_collect"       # 有人收藏了我的帖子
        # 评论相关
        COMMENT_REPLY = "comment_reply"     # 有人回复了我的评论
        COMMENT_LIKE = "comment_like"       # 有人点赞了我的评论
    # 通知接收者（谁收到这条通知 = 帖子/评论的作者）
    user = fields.ForeignKeyField("models.User",related_name="notifications",on_delete=fields.CASCADE,description="通知接收者")
    # 通知发送者（谁触发了这条通知 = 点赞/评论/收藏的用户）
    sender = fields.ForeignKeyField("models.User",related_name="sent_notifications",on_delete=fields.CASCADE,description="通知发送者")
    # 通知类型（用枚举严格限制，避免非法值）
    type = fields.CharEnumField(NotificationType,description="通知类型: 帖子评论/点赞/收藏、评论回复/点赞")
    # 关联的目标（二选一，通过type区分）
    # 目标1：关联帖子（通知来自帖子）
    post = fields.ForeignKeyField(
        "models.Post",
        related_name="notifications",
        null=True,
        on_delete=fields.CASCADE,
        description="关联的帖子"
    )
    # 目标2：关联评论（通知来自评论）
    comment = fields.ForeignKeyField(
        "models.Comment",
        related_name="notifications",
        null=True,
        on_delete=fields.CASCADE,
        description="关联的评论"
    )
    # 通知内容（冗余存储，用于前端直接展示，避免联表查询）
    content = fields.CharField(
        max_length=200,
        description="通知展示内容（如：XX评论了你的帖子）"
    )
    # 已读状态（前端「一键置为已读」的核心字段）
    is_read = fields.BooleanField(
        default=False,
        description="是否已读"
    )
    class Meta:
        table = "notification"
        # 按时间倒序排序，最新通知在最前
        ordering = ["-created_at"]
        # 索引
        indexes = [
            ("user", "is_read"),  # 按用户和已读状态查询
        ]

