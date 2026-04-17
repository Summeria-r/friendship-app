from enum import Enum

from tortoise import Model, fields


class Post(Model):
    
    """帖子模型"""
    class PostCategory(str,Enum):
        RECENT = "最近"
        MATCH = "比赛"
        SECONDHAND = "二手"
        LOST_FOUND = "失物寻物"
        CARPOOL = "拼车"
        STUDY = "学习"
        HOBBY = "兴趣"
        FOOD = "吃饭"
        OTHER = "其他"
    id = fields.IntField(pk=True, index=True)
    created_at = fields.DatetimeField(auto_now_add=True, null=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, null=True, description="更新时间")
    title = fields.CharField(max_length=200, description="帖子标题")
    content = fields.TextField(description="帖子内容")
    user = fields.ForeignKeyField("models.User", related_name="posts", description="发帖用户")
    category = fields.CharEnumField(PostCategory,max_length=20,nullable=False,description="帖子分类")
    is_sticky = fields.BooleanField(default=False, description="是否置顶")
    #图片URL列表
    image_urls = fields.JSONField(default=[], description="图片URL列表")
    like_count = fields.IntField(default=0, description="点赞数")
    comment_count = fields.IntField(default=0, description="评论数")
    collect_count = fields.IntField(default=0, description="收藏数")
     
    class Meta:
        table = "posts"
        description = "帖子表"
         # 给创建时间加一个索引 分类加一个索引
        indexes = [
            ["created_at"],
            ["category"],        ]
        #排序按创建时间降序
        ordering = ["-created_at"]