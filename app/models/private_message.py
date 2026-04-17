from enum import Enum

from tortoise import Model, fields


class Private_message(Model):
    """消息模型"""
    id = fields.IntField(pk=True, index=True)
    created_at = fields.DatetimeField(auto_now_add=True, null=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, null=True, description="更新时间")
    sender = fields.ForeignKeyField("models.User", related_name="sent_messages", description="发送者")
    receiver = fields.ForeignKeyField("models.User", related_name="received_messages", description="接收者")
    content = fields.TextField(description="消息内容")
    is_read = fields.BooleanField(default=False, description="是否已读")
    #消息类型
    class MessageType(str, Enum):
        TEXT = "text"  # 文本消息
        IMAGE = "image"  # 图片消息
        SYSTEM = "system"  # 系统消息
        VOICE = "voice"  # 语音消息
        FILE = "file"  # 文件消息

    message_type = fields.CharField(max_length=20, default="text", description="消息类型")
    read_at = fields.DatetimeField(null=True, description="阅读时间")


    class Meta:
        table = "messages"
        description = "消息表"
        # 给创建时间加一个索引
        indexes = [
            ["created_at"],
        ]
        # 按创建时间降序排序
        ordering = ["-created_at"]