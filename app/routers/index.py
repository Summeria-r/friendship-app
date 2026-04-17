from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.services import post_service
templates = Jinja2Templates(directory="templates")

index_router = APIRouter()

# 首页路由
@index_router.get("/")
async def index(request: Request):
    posts = await post_service.get_latest_posts(limit=6)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "首页",
            "posts": posts,
        }
    )

#首页跳转到比赛组队页
@index_router.get("/competition_team")
async def team(request: Request):
    return templates.TemplateResponse(
        "competition_team.html",
        {
            "request": request,
            "title": "比赛组队"
        }
    )
#首页跳转到饭搭子页
@index_router.get("/meal_buddy")
async def meal_buddy(request: Request):
    return templates.TemplateResponse(
        "meal_buddy.html",
        {
            "request": request,
            "title": "饭搭子"
        }
    )
#首页跳转到兴趣搭子页
@index_router.get("/interest_buddy")
async def interest_buddy(request: Request):
    return templates.TemplateResponse(
        "interest_buddy.html",
        {
            "request": request,
            "title": "兴趣搭子"
        }
    )

#首页跳转到学习搭子页
@index_router.get("/study_buddy")
async def study_buddy(request: Request):
    return templates.TemplateResponse(
        "study_buddy.html",
        {
            "request": request,
            "title": "学习搭子"
        }
    )

#开始匹配
@index_router.get("/match_center")
async def match_center(request: Request):
    return templates.TemplateResponse(
        "match_center.html",
        {
            "request": request,
            "title": "匹配中心"
        }
    )

#我要发贴
@index_router.get("/post")
async def post(request: Request):
    return templates.TemplateResponse(
        "post.html",
        {
            "request": request,
            "title": "我要发贴"
        }
    )
