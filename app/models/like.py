from enum import Enum

from tortoise import Model, fields


class Likes(Model):
    
    """点赞模型"""
    #枚举点赞类型
    class LikeType(str, Enum):
        POST = "post"  # 帖子
        COMMENT = "comment"  # 评论
    id = fields.IntField(pk=True, index=True)
    created_at = fields.DatetimeField(auto_now_add=True, null=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, null=True, description="更新时间")
    user = fields.ForeignKeyField("models.User", related_name="likes")
    like_type = fields.CharField(max_length=20,default="post",  description="点赞类型：post=帖子, comment=评论")
    # 点赞帖子（二选一，可为空）
    post = fields.ForeignKeyField("models.Post", related_name="likes",null=True, on_delete=fields.CASCADE)

    # 点赞评论（二选一，可为空）
    comment = fields.ForeignKeyField("models.Comment", related_name="likes",null=True, on_delete=fields.CASCADE)

    class Meta:
        table = "likes"
        # 唯一约束：一个用户不能重复点赞同一个目标
        unique_together = [
            ("user_id", "post_id"),
            ("user_id", "comment_id")
        ]
        description = "点赞表"