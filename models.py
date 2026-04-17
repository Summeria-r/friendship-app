# 数据库模型定义
# app/models.py
from datetime import datetime, timedelta
from enum import Enum

from tortoise.models import Model
from tortoise import fields, timezone as dt_timezone
#1.用户模型
class User(Model):
    """用户模型"""
    #枚举账号状态
    class AccountStatus(str, Enum):
        ACTIVE = "active"    # 正常
        INACTIVE = "inactive"  # 禁用
    id = fields.IntField(pk=True, index=True)
    created_at = fields.DatetimeField(auto_now_add=True, null=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, null=True, description="更新时间")
    username = fields.CharField(max_length=50, unique=True, index=True, description="用户名")
    password = fields.CharField(max_length=100, description="密码哈希值")
    gender = fields.CharField(max_length=10, null=True, description="性别")
    birthday = fields.DateField(null=True, description="生日")
    bio = fields.TextField(null=True, description="个性签名")
    department = fields.CharField(max_length=100, null=True, description="学院")
    major = fields.CharField(max_length=100, null=True, description="专业")
    phone = fields.CharField(max_length=20, null=True, description="联系电话")
    level = fields.IntField(default=1, description="用户等级")
    student_id = fields.CharField(max_length=20, null=True, description="学号")
    avatar = fields.CharField(max_length=200, null=True, description="头像URL")
    account_status = fields.CharField(max_length=20, default=AccountStatus.ACTIVE.value, description="账号状态")
    interests = fields.ManyToManyField("models.Interest", related_name="users", description="用户兴趣")
    last_login_at = fields.DatetimeField(null=True, description=" 最后登录时间")
    is_system = fields.BooleanField(default=False, description="是否为系统用户")


    class Meta:
        table = "users"
        description = "用户表"
        #索引
        indexes = [
            ["created_at"],
            ["last_login_at"],
        ]

#2.帖子模型
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
    #发帖用户 一对多关系
    user = fields.ForeignKeyField("models.User", related_name="posts", description="发帖用户")
    category = fields.CharEnumField(PostCategory,max_length=20,nullable=False,description="帖子分类")
    is_sticky = fields.BooleanField(default=False, description="是否置顶")

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

#3.评论模型
class Comment(Model):
    
    """评论模型（为null表示顶级评论）"""
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

#4.点赞模型
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

#5.收藏模型
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
#6.私聊消息
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

#7.兴趣模型
class Interest(Model):
    """兴趣模型"""
    id = fields.IntField(pk=True, index=True)
    created_at = fields.DatetimeField(auto_now_add=True, null=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, null=True, description="更新时间")
    class InterestEnum(str, Enum):
        THEATER = "看剧"
        MUSIC = "听歌"
        PHOTO = "拍照"
        FOOD = "美食"
        TRAVEL = "旅行"
        SPORTS = "运动"
        DRAW = "画画"
        GAME = "游戏"
        STUDY = "学习"
    name = fields.CharEnumField(InterestEnum,unique=True,max_length=20,description="兴趣名称（枚举值）")


    class Meta:
        table = "interests"
        description = "兴趣表"


#8.帖子消息

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

#9.匹配记录表
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
# 扩展MatchRecord模型的save方法，添加通知功能
original_save = MatchRecord.save

async def save_with_notification(self, *args, **kwargs):
    """保存匹配记录并发送通知"""
    # 检查状态是否变化
    old_status = None
    if self.id:
        old_record = await MatchRecord.get(id=self.id)
        old_status = old_record.status
    
    # 保存记录
    result = await original_save(self, *args, **kwargs)
    
    # 发送通知
    if old_status != self.status and (self.status == MatchRecord.MatchStatus.MATCHED.value or self.status == MatchRecord.MatchStatus.EXPIRED.value):
        # 导入通知服务
        from app.services.notification import send_match_notification
        await send_match_notification(self)
    
    return result

MatchRecord.save = save_with_notification
#10.即时匹配表

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
        """判断是否超时（20 分钟）"""
        # 获取当前 UTC 时间（和 Tortoise 自动存储的时间一致）
        now = datetime.now(dt_timezone.utc)
        # 超时时间 = 点击时间 + 20 分钟
        expire_time = self.clicked_at + timedelta(minutes=20)
        # 当前时间 > 超时时间 → 已超时
        return now > expire_time


#11.长期匹配表
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
    
    # 匹配要求（可选，如具体专业、目标院校等）
    requirements = fields.JSONField(null=True, description="匹配要求")
    
    # 过期时间（如1天）
    expire_at = fields.DatetimeField(description="过期时间")
    
    # 是否已匹配
    is_matched = fields.BooleanField(default=False)
    
    class Meta:
        table = "long_term_match_wait"
        description = "长期匹配等待表"
        indexes = [
            ["interest_id", "is_matched", "expire_at"],
        ]