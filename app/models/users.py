from enum import Enum

from tortoise import Model, fields


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
    nickname = fields.CharField(max_length=50, null=True, description="昵称")
    password = fields.CharField(max_length=100, description="密码哈希值")
    gender = fields.CharField(max_length=10, null=True, description="性别")
    birthday = fields.DateField(null=True, description="生日")
    bio = fields.TextField(null=True, description="个性签名")
    introduction = fields.TextField(null=True, description="个人介绍")
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