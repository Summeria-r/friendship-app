from fastapi import APIRouter, Form, Request
from fastapi.templating import Jinja2Templates
from datetime import datetime

from app.security import get_current_user

personal_info_router = APIRouter()
templates = Jinja2Templates(directory="templates")


   

# 保存个人资料
@personal_info_router.post("/save_personal_info")
async def save_personal_info(
    request: Request,
    nickname: str = Form(...),
    gender: str = Form(...),
    bio: str = Form(...),
    birthday: str = Form(None),
    department: str = Form(...),
    major: str = Form(...),
    student_id: str = Form(...),
    phone: str = Form(...),
    interest_names: str = Form(...)
    ):
    # 获取当前登录用户
    user = await get_current_user(request)
    
    # 处理数据类型转换
    user.nickname = nickname
    user.gender = gender
    user.bio = bio
    
    # 处理生日字段的类型转换
    if birthday:
        try:
            user.birthday = datetime.strptime(birthday, "%Y-%m-%d").date()
        except ValueError:
            user.birthday = None
    else:
        user.birthday = None
    
    user.department = department
    user.major = major
    user.student_id = student_id
    user.phone = phone
    
    await user.save()
    
    # 处理兴趣爱好的ManyToMany关系
    if interest_names:
        interest_name_list = [name for name in interest_names.split(",") if name]
        # 先清除现有的兴趣关系
        await user.interests.clear()
        # 然后添加新的兴趣关系
        from app.models.interest import Interest
        for interest_name in interest_name_list:
            # 使用枚举成员名称查找兴趣
            try:
                interest_enum_member = Interest.InterestEnum[interest_name]
                interest = await Interest.filter(name=interest_enum_member).first()
                if interest:
                    await user.interests.add(interest)
            except KeyError:
                continue
    
    # 获取更新后的兴趣爱好列表
    updated_interests = await user.interests.all()
    # 返回给模板的是枚举成员的名称，以便 HTML 中的 checkbox 匹配
    updated_interest_names = [interest.name.name for interest in updated_interests]
    
    return templates.TemplateResponse(
        "personal_info.html", 
        {"request": request,
         "nickname": nickname,
         "gender": gender,
         "bio": bio,
         "birthday": birthday,
         "department": department,
         "major": major,
         "student_id": student_id,
         "phone": phone,
         "interest_names": updated_interest_names,
         "success": "资料保存成功"
        })