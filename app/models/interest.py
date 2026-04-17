from enum import Enum

from tortoise import Model, fields


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
        GRADUATE = "考研"
        EXAM = "考试"
        FOUR = "四级"
        SIX = "六级"
        CODE = "考编"

    name = fields.CharEnumField(InterestEnum,unique=True,max_length=20,description="兴趣名称（枚举值）")


    class Meta:
        table = "interests"
        description = "兴趣表"