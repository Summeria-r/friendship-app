from tortoise import Model, fields


class Collect(Model):
    
    # 谁收藏的
    id = fields.IntField(pk=True, index=True)
    created_at = fields.DatetimeField(auto_now_add=True, null=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, null=True, description="更新时间")
    user = fields.ForeignKeyField("models.User",related_name="collects",on_delete=fields.CASCADE)

    # 收藏的帖子（可为空）
    post = fields.ForeignKeyField("models.Post",related_name="collects",null=True,on_delete=fields.CASCADE)

    class Meta:
        table = "collect"
        # 唯一约束：不能重复收藏
        unique_together = [
            ("user_id", "post_id")
        ]
        description = "收藏表"