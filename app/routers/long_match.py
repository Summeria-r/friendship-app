# 长期匹配路由
# app/routers/long_match.py
from fastapi import APIRouter, Form, Request
from fastapi.templating import Jinja2Templates
from app.security import get_current_user
from app.services.long_match import handle_long_term_match, periodic_match_check
from app.models import MatchRecord

long_match_router = APIRouter()
templates = Jinja2Templates(directory="templates")

# 发起长期匹配请求
@long_match_router.post("/long_match/request")
async def create_long_match_request(
    request: Request,
    interest_id: int = Form(...)
):
    # 获取当前登录用户
    user = await get_current_user(request)
    
    # 处理长期匹配请求
    match_record = await handle_long_term_match(
        user_id=user.id,
        interest_id=interest_id
    )
    
    status_msg = "匹配成功！" if match_record.status == MatchRecord.MatchStatus.MATCHED.value else "已进入匹配队列，正在为您寻找搭子..."
    return {"message": status_msg, "status": match_record.status}

# 定期检查匹配（手动触发接口，用于演示/测试）
@long_match_router.get("/long_match/check")
async def trigger_periodic_check():
    await periodic_match_check()
    return {"message": "定时匹配检查已完成"}
