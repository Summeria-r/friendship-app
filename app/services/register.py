# app/services/auth_service.py
import re
from app.models.users import User
from app.security import get_password_hash
from app.exceptions import UserAlreadyExistsException, InvalidParameterException

# 手机号正则校验
PHONE_PATTERN = r'^1[3-9]\d{9}$'

async def register_user(username: str, password: str, phone: str, confirm_password: str) -> User:
    """
    用户注册业务逻辑：
    1. 参数校验（手机号格式、密码长度）
    2. 账号/手机号唯一性校验
    3. 密码加密
    4. 创建用户并保存到数据库
    """
    # -------------------------- 1. 参数校验 --------------------------
    # 手机号格式校验
    if not phone or len(phone) != 11 or not phone.isdigit() or not re.match(PHONE_PATTERN, phone):
        raise InvalidParameterException(detail="手机号格式错误")
    
    # 密码长度校验
    if len(password) < 6 or len(password) > 20:
        raise InvalidParameterException(detail="密码长度需在6-20字符之间")

    # -------------------------- 2. 唯一性校验 --------------------------
    # 检查账号是否已存在
    existing_user = await User.filter(username=username).first()
    if existing_user:
        raise UserAlreadyExistsException(detail="账号已存在")
    
    # 检查手机号是否已存在
    existing_phone = await User.filter(phone=phone).first()
    if existing_phone:
        raise UserAlreadyExistsException(detail="手机号已存在")
    #检查两次输入的密码是否一致
    if password != confirm_password:
        raise InvalidParameterException(detail="两次输入的密码不一致")

    # -------------------------- 3. 创建用户、加密密码 --------------------------
    hashed_pwd = get_password_hash(password)
    user = await User.create(
        username=username,
        phone=phone,
        password=hashed_pwd  # 直接传入加密后的密码
    )

    return user
