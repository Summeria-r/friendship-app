# 即时匹配路由
# app/routers/instant_match.py
import logging

from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.security import get_current_user
from app.services.instant_match import handle_instant_match

instant_match_router = APIRouter()
templates = Jinja2Templates(directory="templates")


# 处理即时匹配请求
@instant_match_router.post("/instant_match")
async def create_instant_match(request: Request, interest_id: int = Form(...)):
    try:
        # 先把请求体打出来，看看前端传了什么
        body = await request.json()
        logging.info(f"收到的请求体: {body}")
    # 获取当前登录用户
        user = await get_current_user(request)
    
    # 处理即时匹配
        match_record = await handle_instant_match(user.id, interest_id)
    
    # 构建响应
        if match_record.status == "matched":
            # 匹配成功
            partner_nickname = match_record.user2.nickname if match_record.user2 else "未知用户"
            return JSONResponse({
                "status": "success",
                "message": "匹配成功",
                "data": {
                    "match_id": match_record.id,
                    "partner_nickname": partner_nickname
                }
            })
        elif match_record.status == "matching":
            # 匹配中
            return JSONResponse({
                "status": "matching",
                "message": "正在匹配中，请等待..."
            })
        else:
            # 其他状态
            return JSONResponse({
                "status": "error",
                "message": "匹配失败"
            })
    except Exception as e:
        # 把错误信息打出来，包括栈追踪
        logging.error(f"接口报错了！错误详情: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=400,
            content={"detail": str(e)}
        )
