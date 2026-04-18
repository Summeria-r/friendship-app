# 匹配状态路由
# app/routers/match_status.py
from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from app.security import get_current_user
from app.models.match_record import MatchRecord

match_status_router = APIRouter()

# 检查匹配状态
@match_status_router.post("/check_match_status")
async def check_match_status(request: Request, interest_id: int = Form(...), match_type: str = Form(...)):
    # 获取当前登录用户
    user = await get_current_user(request)
    
    # 查找最新的匹配记录
    match_record = await MatchRecord.filter(
        user1_id=user.id,
        interest_id=interest_id,
        match_type=match_type
    ).prefetch_related('user2').order_by('-id').first()
    
    if not match_record:
        return JSONResponse({"status": "not_found", "message": "匹配记录不存在"})
    
    # 检查匹配状态
    if match_record.status == MatchRecord.MatchStatus.MATCHED.value:
        # 匹配成功
        partner_nickname = "未知用户"
        partner_id = None
        if match_record.user2:
            partner_nickname = match_record.user2.nickname if match_record.user2.nickname else match_record.user2.username
            partner_id = match_record.user2.id
        
        return JSONResponse({
            "status": "matched",
            "partner_nickname": partner_nickname,
            "partner_id": partner_id
        })
    elif match_record.status == MatchRecord.MatchStatus.EXPIRED.value:
        # 匹配过期
        return JSONResponse({"status": "expired", "message": "匹配已过期"})
    else:
        # 匹配中
        return JSONResponse({"status": "matching", "message": "正在匹配中"})
