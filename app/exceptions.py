# 自定义异常类
# app/exceptions.py
from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from tortoise.exceptions import DoesNotExist, IntegrityError, OperationalError
from config import TEMPLATES_DIR

# 初始化模板引擎（用于渲染错误页面）
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# ==================== 1. 自定义业务异常类 ====================
class BusinessException(HTTPException):
    """自定义业务异常基类，所有业务异常继承此类"""
    def __init__(self, status_code: int = 400, detail: str = "业务异常"):
        super().__init__(status_code=status_code, detail=detail)


class UserNotExistsException(BusinessException):
    """用户不存在异常"""
    def __init__(self, detail: str = "用户不存在"):
        super().__init__(status_code=404, detail=detail)


class UserAlreadyExistsException(BusinessException):
    """用户已存在异常（如注册时用户名重复）"""
    def __init__(self, detail: str = "用户名已被注册"):
        super().__init__(status_code=400, detail=detail)


class PasswordErrorException(BusinessException):
    """密码错误异常"""
    def __init__(self, detail: str = "用户名或密码错误"):
        super().__init__(status_code=401, detail=detail)


class PermissionDeniedException(BusinessException):
    """权限不足异常"""
    def __init__(self, detail: str = "无权限访问此资源"):
        super().__init__(status_code=403, detail=detail)


class ResourceNotFoundException(BusinessException):
    """资源不存在异常（如帖子/消息不存在）"""
    def __init__(self, detail: str = "请求的资源不存在"):
        super().__init__(status_code=404, detail=detail)


class InvalidParameterException(BusinessException):
    """参数错误异常"""
    def __init__(self, detail: str = "请求参数错误"):
        super().__init__(status_code=400, detail=detail)


# ==================== 2. 全局异常处理器 ====================
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    统一处理HTTP异常：
    - 401未登录：前后端不分离场景自动跳转到登录页
    - 其他异常：返回错误页面/JSON
    """
    # 401 未登录：跳转到登录页（前后端不分离核心逻辑）
    if exc.status_code == 401:
        return RedirectResponse(url="/login", status_code=302)
    
    # 其他异常：返回友好的错误页面
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": exc.status_code,
            "detail": exc.detail
        },
        status_code=exc.status_code
    )


async def tortoise_exception_handler(request: Request, exc: Exception):
    """
    统一处理Tortoise-ORM数据库异常：
    - DoesNotExist：数据不存在
    - IntegrityError：数据完整性错误（如唯一约束冲突）
    - OperationalError：数据库连接/操作错误
    """
    if isinstance(exc, DoesNotExist):
        return await http_exception_handler(
            request,
            ResourceNotFoundException(detail="请求的数据不存在")
        )
    elif isinstance(exc, IntegrityError):
        return await http_exception_handler(
            request,
            InvalidParameterException(detail="数据操作失败，可能存在重复或关联错误")
        )
    elif isinstance(exc, OperationalError):
        return await http_exception_handler(
            request,
            HTTPException(status_code=500, detail="数据库操作失败，请稍后重试")
        )
    # 其他未知数据库异常
    return await http_exception_handler(
        request,
        HTTPException(status_code=500, detail="服务器内部错误")
    )


async def global_exception_handler(request: Request, exc: Exception):
    """
    全局兜底异常处理器：捕获所有未处理的异常，避免服务器崩溃
    """
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": 500,
            "detail": "服务器内部错误，请稍后重试"
        },
        status_code=500
    )


async def not_found_handler(request: Request, exc: StarletteHTTPException):
    """
    404页面不存在异常处理
    """
    return templates.TemplateResponse(
        "404.html",
        {"request": request},
        status_code=404
    )