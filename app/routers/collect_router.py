# app/routers/collect_router.py
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services import collect_service, notification_service

collect_router = APIRouter()

# 1. 收藏/取消收藏帖子 (AJAX 调用)
@collect_router.post("/collects/post/{post_id}")
async def toggle_post_collect_action(request: Request, post_id: int):
    """
    收藏帖子切换接口
    """
    user_data = request.session.get("user")
    if not user_data:
        raise HTTPException(status_code=401, detail="请先登录")
    
    # 切换业务逻辑
    is_collected = await collect_service.toggle_post_collect(user_data["id"], post_id)
    
    # 核心：收藏时触发通知
    if is_collected:
        await notification_service.create_collect_notification(user_data["id"], post_id)
    
    return JSONResponse({
        "status": "success",
        "is_collected": is_collected,
        "message": "收藏成功" if is_collected else "已取消收藏"
    })

# 2. 个人主页 - 我的收藏列表
@collect_router.get("/my/collections", response_class=HTMLResponse)
async def my_collections_page(request: Request, page: int = 1):
    """
    显示用户的收藏列表页面
    """
    user_data = request.session.get("user")
    if not user_data:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/login", status_code=303)
    
    # 获取收藏的帖子
    posts = await collect_service.get_user_collects(user_data["id"], page)
    
    from fastapi.templating import Jinja2Templates
    jinja_templates = Jinja2Templates(directory="templates")
    jinja_templates.env.cache = None  # 完全禁用缓存
    
    return jinja_templates.TemplateResponse(
        "my_collection.html",
        {
            "request": request,
            "posts": posts,
            "page": page
        }
    )
