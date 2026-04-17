# app/routers/comment_router.py
from fastapi import APIRouter, Request, HTTPException, Form
from fastapi.responses import RedirectResponse
from app.services import comment_service, notification_service
from typing import Optional

comment_router = APIRouter()

# 1. 提交评论
@comment_router.post("/comments/create/{post_id}")
async def create_comment_action(
    request: Request,
    post_id: int,
    content: str = Form(...),
    parent_id: Optional[int] = Form(None)
):
    """
    提交评论（包含根评论和楼中楼回复）
    """
    user_data = request.session.get("user")
    if not user_data:
        raise HTTPException(status_code=401, detail="请先登录")
    
    # 业务：创建评论
    comment = await comment_service.create_comment(
        user_id=user_data["id"],
        post_id=post_id,
        content=content,
        parent_id=parent_id
    )
    
    # 业务：触发通知（发送给帖子作者或被回复的评论作者）
    # 核心：由开发者 A 维护通知生成逻辑
    await notification_service.create_comment_notification(comment)
    
    # 页面：跳转回帖子详情页
    return RedirectResponse(url=f"/posts/{post_id}", status_code=303)

# 2. 删除评论
@comment_router.post("/comments/delete/{comment_id}")
async def delete_comment_action(request: Request, comment_id: int):
    """
    删除评论（仅限作者本人）
    """
    user_data = request.session.get("user")
    if not user_data:
        raise HTTPException(status_code=401, detail="请先登录")
    
    success = await comment_service.delete_comment(comment_id, user_data["id"])
    if not success:
        raise HTTPException(status_code=403, detail="删除失败")
    
    # 获取 Referer 以便跳回来源页，否则回首页
    referer = request.headers.get("referer", "/")
    return RedirectResponse(url=referer, status_code=303)

# 3. 分页查询评论 (通常由前端 JS 调用，也可供模板渲染)
@comment_router.get("/comments/{post_id}")
async def get_comments(post_id: int, page: int = 1):
    """
    获取帖子的评论列表
    """
    comments = await comment_service.get_paged_comments(post_id, page)
    return {"status": "success", "data": comments}
