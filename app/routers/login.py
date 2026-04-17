from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.exceptions import InvalidParameterException, PasswordErrorException, UserNotExistsException
from app.security import delete_user_session, save_user_session
from app.services.login import login_user
templates = Jinja2Templates(directory="templates")
login_router = APIRouter()

#跳转到注册页面
@login_router.get("/register")
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# 登录路由-post请求 处理表单提交
@login_router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    """
    登录路由：只做参数接收、异常捕获、页面跳转
    所有业务逻辑全部交给 auth_service 处理
    """
    try:
        # 1. 调用服务层完成登录校验（返回用户信息或Token）
        user = await login_user(username, password)
        # 保存用户会话（Session）
        await save_user_session(request, user)

        # 2. 登录成功：跳转首页（或个人中心），携带提示
        # 这里用 RedirectResponse 跳转，因为 POST 请求后通常要重定向到 GET 接口
        return RedirectResponse(url="/personal_center", status_code=302)
        

    except InvalidParameterException as e:
        # 3. 参数异常（账号/密码为空）
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": e.detail}
        )
    except UserNotExistsException as e:
        # 4. 用户不存在（账号错误）
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": e.detail}
        )
    except PasswordErrorException as e:
        # 5. 密码错误
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": e.detail}
        )
    except Exception as e:
        # 6. 兜底异常（未知错误）
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "登录失败，请检查账号密码"}
        )
    
#退出登录
@login_router.get("/logout")
async def logout(request: Request):
    await delete_user_session(request)
    #退出成功后给出提示不用跳转
    return templates.TemplateResponse("personal_center.html", {"request": request, "message": "退出成功"})
