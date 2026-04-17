from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from app.security import get_current_user


personal_center_router = APIRouter()
templates = Jinja2Templates(directory="templates")


#跳转到个人资料
@personal_center_router.get("/personal_info")
async def personal_info(request: Request):
     # 获取当前登录用户
    user = await get_current_user(request)
    
    # 获取用户的兴趣爱好列表
    interests = await user.interests.all()
    interest_names = [interest.name.name for interest in interests] # 获取枚举成员的名称 (如 THEATER)
    
    return templates.TemplateResponse(
        "personal_info.html", 
        {
            "request": request,
            "nickname": user.nickname,
            "gender": user.gender,
            "bio": user.bio,
            "birthday": user.birthday.strftime("%Y-%m-%d") if user.birthday else "",
            "department": user.department,
            "major": user.major,
            "student_id": user.student_id,
            "phone": user.phone,
            "interest_names": interest_names
        }
    )
#表单接受用户信息
@personal_center_router.post("/update_info")
async def update_info(
    request: Request,
    nickname: str = Form(...),
    student_id: str = Form(...),
    phone: str = Form(...),
    gender: str = Form(...),
    department: str = Form(...),
    major: str = Form(...),
    introduction: str = Form(...),
   ):
    #获取当前登录用户会话
    user = await get_current_user(request)
     # 简单参数校验（你要的「简单验证」）
    if not phone or len(phone) != 11 or not phone.isdigit():
        return templates.TemplateResponse(
                "personal_info.html",
                {"request": request, "error": "手机号格式错误，请输入11位数字"}
            )
    if len(nickname) > 50:
        return templates.TemplateResponse(
                "personal_info.html",
                {"request": request, "error": "昵称长度不能超过50个字符"}
            )

    #更新用户信息
    user.nickname = nickname
    user.student_id = student_id
    user.phone = phone
    user.gender = gender
    user.department = department
    user.major = major
    user.introduction = introduction
    await user.save()
    #使用Jinja2语法回显页面
    return templates.TemplateResponse(
        "personal_center.html", 
        {"request": request,
         "nickname": nickname,
         "student_id": student_id,
         "phone": phone,
         "gender": gender,
         "department": department,
         "major": major,
         "introduction": introduction}
    )

#跳转到头像页面
@personal_center_router.get("/touxiang")
async def touxiang(request: Request):
    # 获取当前登录用户
    user = await get_current_user(request)
    return templates.TemplateResponse(
        "touxiang.html",
        {
            "request": request,
            "title": "头像设置",
            "avatar": user.avatar
        }
    )

# 上传头像
from fastapi import File, UploadFile
import os
import uuid

@personal_center_router.post("/upload_avatar")
async def upload_avatar(request: Request, file: UploadFile = File(...)):
    # 获取当前登录用户
    user = await get_current_user(request)
    
    # 验证文件类型
    if not file.filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
        return templates.TemplateResponse(
            "touxiang.html",
            {
                "request": request,
                "title": "头像设置",
                "error": "只支持jpg、jpeg、png、gif格式的图片",
                "avatar": user.avatar
            }
        )
    
    # 生成唯一文件名
    filename = f"{uuid.uuid4()}_{file.filename}"
    
    # 确保uploads目录存在
    upload_dir = "static/uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    # 保存文件
    file_path = os.path.join(upload_dir, filename)
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # 更新用户头像URL
    avatar_url = f"/static/uploads/{filename}"
    user.avatar = avatar_url
    await user.save()
    
    # 上传成功后重定向到个人中心页面
    return RedirectResponse(url="/personal_center", status_code=303)

# #跳转到匹配记录页面
# @personal_center_router.get("/match_record")
# async def match_record(request: Request):
#     return templates.TemplateResponse(
#         "match_record.html",
#         {
#             "request": request,
#             "title": "匹配记录"
#         }
#     )
