# app/routers/auth.py
from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from app.services.register import register_user
from app.exceptions import InvalidParameterException, UserAlreadyExistsException
from config import TEMPLATES_DIR

register_router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@register_router.post("/do_register")
async def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    phone: str = Form(...)
):
    """
    注册路由：只做参数接收、异常捕获、页面跳转
    所有业务逻辑全部交给auth_service处理
    """
    try:
        # 调用服务层完成注册，只传参数，不做任何逻辑
        await register_user(username, password, phone, confirm_password)
        # 注册成功，跳转到登录页，带成功提示
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "success": "注册成功！请登录"}
        )
    except InvalidParameterException as e:
        # 参数错误（手机号格式/密码长度），返回注册页并提示
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": e.detail}
        )
    except UserAlreadyExistsException as e:
        # 账号/手机号重复，返回注册页并提示
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": e.detail}
        )
    except Exception as e:
        # # 兜底异常，返回通用错误
        # import traceback
        # traceback.print_exc() # 在终端打印完整堆栈信息
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": f"注册失败原因: {str(e)}"}
        )