# 匹配记录路由
# app/routers/match_record.py
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.security import get_current_user
from app.models.match_record import MatchRecord
from tortoise import timezone as dt_timezone
from tortoise.expressions import Q
from datetime import datetime

match_record_router = APIRouter()
templates = Jinja2Templates(directory="templates")

# 显示匹配记录页面
@match_record_router.get("/match_record", response_class=HTMLResponse)
async def show_match_record_page(request: Request, success: str = None, error: str = None):
    # 1. 校验用户登录
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")

    # 2. 修复查询条件：包含作为发起者和被匹配者的所有记录
    match_records = await MatchRecord.filter(
        Q(user1_id=user.id) | Q(user2_id=user.id)
    ).prefetch_related('interest', 'user1', 'user2').order_by('-id').all()

    
    # 3. 构建响应数据，增加异常处理
    records = []
    for record in match_records:
        try:
            
            # 确定匹配对象 - 修复这里的逻辑
            if record.user1_id == user.id:
                partner = record.user2
                current_user_info = record.user1
            elif record.user2_id == user.id:
                partner = record.user1
                current_user_info = record.user2
            else:
                # 这种情况不应该发生，但为了安全起见添加检查
                print(f"Warning: Record {record.id} does not belong to user {user.id}")
                continue
                
            partner_nickname = "暂无"
            if partner:
                partner_nickname = partner.nickname if getattr(partner, 'nickname', None) else partner.username

            # 构建匹配编号
            created_time = record.created_at
            created_time_str = created_time.strftime('%Y%m%d') if created_time else "00000000"
            match_id = f"MATCH{created_time_str}{record.id:03d}"

            # 转换状态
            status_map = {"matching": "匹配中", "matched": "已匹配", "expired": "已过期"}
            raw_status = record.status
            status_val = raw_status.value if hasattr(raw_status, 'value') else str(raw_status)
            status_display = status_map.get(status_val, status_val)

            # 转换匹配类型（增加容错）
            type_map = {"long_term": "长期匹配", "instant": "即时匹配"}
            raw_match_type = getattr(record, 'match_type', None)
            if raw_match_type:
                type_val = raw_match_type.value if hasattr(raw_match_type, 'value') else str(raw_match_type)
                match_type_display = type_map.get(type_val, type_val)
            else:
                match_type_display = "未知类型"

            # 获取兴趣名称 换成兴趣名称比如：运动、四级等汉字
            interest_name = "未知兴趣"
            if record.interest:
                if hasattr(record.interest, 'name'):
                    try:
                        # 处理枚举类型，确保显示汉字
                        interest_name = record.interest.name
                        # 检查是否是枚举类型
                        if hasattr(interest_name, 'value'):
                            interest_name = interest_name.value
                        # 确保是字符串
                        interest_name = str(interest_name)
                    except Exception as e:
                        print(f"获取兴趣名称出错: {e}")
                        interest_name = "未知兴趣"
                else:
                    interest_name = "未知兴趣"

            # 组装数据
            records.append({
                "id": record.id,
                "match_id": match_id,
                "nickname": (current_user_info.nickname 
                           if hasattr(current_user_info, 'nickname') and current_user_info.nickname 
                           else current_user_info.username) if current_user_info else user.nickname or user.username,
                "interest": interest_name,
                "status": status_display,
                "match_type": match_type_display,
                "create_time": created_time.strftime('%Y-%m-%d %H:%M:%S') if created_time else "未知",
                "partner_id": partner.id if partner else None,
                "partner_nickname": partner_nickname
            })
        except Exception as e:
            print(f"处理记录 {record.id} 时出错: {e}")
            continue

    print(f"Returning {len(records)} processed records")
    return templates.TemplateResponse("match_record.html", {
        "request": request, 
        "records": records,
        "success": success,
        "error": error
    })


# 取消匹配
@match_record_router.post("/match_record/cancel")
async def cancel_match(request: Request, id: int = Form(...)):
    # 获取当前登录用户
    user = await get_current_user(request)
    
    # 查找匹配记录
    match_record = await MatchRecord.filter(
        id=id,
        user1_id=user.id,
        status="matching"
    ).first()
    
    if not match_record:
        return JSONResponse({"error": "匹配记录不存在或已不能取消"})
    
    # 更新匹配记录状态
    match_record.status = "expired"
    await match_record.save()
    
    return JSONResponse({"message": "匹配已取消"})