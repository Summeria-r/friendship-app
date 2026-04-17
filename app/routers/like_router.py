# app/routers/like_router.py
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from app.services import like_service, notification_service

like_router = APIRouter()

# 1. 帖子点赞/取消点赞接口 (通常为 AJAX 异步请求)
@like_router.post("/likes/post/{post_id}")
async def toggle_post_like_action(request: Request, post_id: int):
    """
    点赞帖子切换（AJAX 调用，返回点赞后的状态和点赞数）
    """
    user_data = request.session.get("user")
    if not user_data:
        raise HTTPException(status_code=401, detail="请先登录")
    
    # 执行业务切换
    result = await like_service.toggle_post_like(user_data["id"], post_id)
    
    # 核心：点赞时生成通知
    if result["is_liked"]:
        await notification_service.create_like_notification(user_data["id"], post_id, target_type="post")
    
    return JSONResponse({
        "status": "success",
        "is_liked": result["is_liked"],
        "like_count": result["like_count"],
        "message": "点赞成功" if result["is_liked"] else "已取消点赞"
    })

# 2. 评论点赞/取消点赞接口
@like_router.post("/likes/comment/{comment_id}")
async def toggle_comment_like_action(request: Request, comment_id: int):
    """
    点赞评论切换（AJAX 调用，返回点赞后的状态和点赞数）
    """
    user_data = request.session.get("user")
    if not user_data:
        raise HTTPException(status_code=401, detail="请先登录")
    
    result = await like_service.toggle_comment_like(user_data["id"], comment_id)
    
    # 点赞评论时生成通知
    if result["is_liked"]:
        await notification_service.create_like_notification(user_data["id"], comment_id, target_type="comment")
    
    return JSONResponse({
        "status": "success",
        "is_liked": result["is_liked"],
        "like_count": result["like_count"],
        "message": "点赞成功" if result["is_liked"] else "已取消点赞"
    })
