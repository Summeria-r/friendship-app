# 公共路由
from typing import Optional

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.security import get_current_user
from app.models.users import User
from app.services import comment_service, notification_service, post_service
templates = Jinja2Templates(directory="templates")


common_router = APIRouter()


#跳转到登录页面
@common_router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "title": "登录"
        }
    )

#跳转到注册页面
@common_router.get("/register")
async def register(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "title": "注册"
        }
    )


# 获取用户等级
async def get_user_level(level):
    level_map = {
        1: "萌新",
        2: "活跃用户",
        3: "资深活跃",
        4: "校园达人",
        5: "社交巨星"
    }
    return level_map.get(level, "萌新")

#跳转到个人中心
@common_router.get("/personal_center")
async def personal_center(request: Request):
    #获取用户信息
    user = await get_current_user(request)

    #查询数据库的用户信息
    user_info = await User.get(id=user.id)
    nickname = user_info.nickname if user_info.nickname else ""
    student_id = user_info.student_id if user_info.student_id else ""
    phone = user_info.phone if user_info.phone else ""
    department = user_info.department if user_info.department else ""
    major = user_info.major if user_info.major else ""
    gender = user_info.gender if user_info.gender else ""
    introduction = user_info.introduction if user_info.introduction else ""
    avatar = user_info.avatar if user_info.avatar else ""
    
    # 获取用户等级
    user_level = await get_user_level(user_info.level)
    latest_posts = await post_service.get_latest_posts(limit=5)

    return templates.TemplateResponse(
        "personal_center.html",
        {
            "request": request,
            "nickname": nickname,
            "student_id": student_id,   
            "phone": phone,
            "department": department,
            "major": major,
            "gender": gender,
            "introduction": introduction,
            "avatar": avatar,
            "user_level": user_level,
            "level": user_info.level,
            "latest_posts": latest_posts,
        }
    )
