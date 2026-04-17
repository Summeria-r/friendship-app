from tortoise import Model, fields


class Comment(Model):
    
    """评论模型(为null表示顶级评论)"""
    id = fields.IntField(pk=True, index=True)
    created_at = fields.DatetimeField(auto_now_add=True, null=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, null=True, description="更新时间")
    content = fields.TextField(description="评论内容")
    user = fields.ForeignKeyField("models.User", related_name="comments", description="评论用户")
    post = fields.ForeignKeyField("models.Post", related_name="comments", description="评论帖子")
    parent = fields.ForeignKeyField("models.Comment", related_name="replies", null=True, description="父评论")

    class Meta:
        table = "comments"
        description = "评论表"
        # 给创建时间加一个索引
        indexes = [
            ["created_at"],
        ]
        # 按创建时间降序排序
        ordering = ["-created_at"]