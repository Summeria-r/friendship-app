from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from tortoise.contrib.fastapi import register_tortoise
from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from tortoise.exceptions import DoesNotExist, IntegrityError, OperationalError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio
from fastapi.middleware.cors import CORSMiddleware
# 导入全局配置
from app.models import comment
from config import SECRET_KEY, SESSION_MAX_AGE, get_tortoise_config

# 导入异常处理器
from app.exceptions import (
    http_exception_handler,
    tortoise_exception_handler,
    global_exception_handler,
    not_found_handler
)

# 导入路由
from app.routers.index import index_router
from app.routers.common import common_router
from app.routers.login import login_router
from app.routers.register import register_router
from app.routers.personal_center import personal_center_router
from app.routers.personal_info import personal_info_router
from app.routers.long_match import long_match_router
from app.routers.match_record import match_record_router
from app.routers.instant_match import instant_match_router
from app.routers.match_status import match_status_router
from app.routers.comment_router import comment_router
from app.routers.post_router import post_router
from app.routers.collect_router import collect_router
from app.routers.like_router import like_router
from app.routers.message_router import message_router


# 导入定时任务函数
from app.services.long_match import periodic_match_check
from app.services.instant_match import periodic_instant_match_check



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建调度器
scheduler = AsyncIOScheduler()

# 启动时的事件处理
@app.on_event("startup")
async def startup_event():
    # 添加定时任务
    # 每1分钟检查一次长期匹配
    scheduler.add_job(
        periodic_match_check,
        trigger=IntervalTrigger(minutes=1),
        id="periodic_match_check",
        name="Check long term match status",
        replace_existing=True
    )
    
    # 每30秒检查一次即时匹配
    scheduler.add_job(
        periodic_instant_match_check,
        trigger=IntervalTrigger(seconds=30),
        id="periodic_instant_match_check",
        name="Check instant match status",
        replace_existing=True
    )
    
    # 启动调度器
    scheduler.start()
    print("Scheduled tasks started")

# 关闭时的事件处理
@app.on_event("shutdown")
async def shutdown_event():
    # 关闭调度器
    scheduler.shutdown()
    print("Scheduled tasks stopped")
# 1.静态资源挂载
app.mount("/static",StaticFiles(directory="static"),name="static")
app.mount("/templates",StaticFiles(directory="templates"),name="templates")

# 2.模板引擎配置
templates = Jinja2Templates(directory="templates")

# 启动时再读取配置
TORTOISE_ORM = get_tortoise_config()
# 3.注册Tortoise-ORM
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True
)

# 4.挂载Session会话中间件
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    max_age=SESSION_MAX_AGE
)

# 5.注册异常处理器（顺序很重要：先具体，后通用）
# 404 页面不存在
app.add_exception_handler(StarletteHTTPException, not_found_handler)
# HTTP 标准异常（含401跳转）
app.add_exception_handler(HTTPException, http_exception_handler)
# Tortoise-ORM 数据库异常
app.add_exception_handler(DoesNotExist, tortoise_exception_handler)
app.add_exception_handler(IntegrityError, tortoise_exception_handler)
app.add_exception_handler(OperationalError, tortoise_exception_handler)
# 全局兜底异常
app.add_exception_handler(Exception, global_exception_handler)


# 挂载路由
app.include_router(index_router, tags=["首页"])
app.include_router(common_router, tags=["公共模块"])
app.include_router(login_router, tags=["登录模块"])
app.include_router(register_router, tags=["注册模块"])
app.include_router(personal_center_router, tags=["个人中心模块"])   
app.include_router(personal_info_router, tags=["个人资料模块"]) 
app.include_router(long_match_router, tags=["长期匹配模块"])
app.include_router(match_record_router, tags=["匹配记录模块"])
app.include_router(instant_match_router, tags=["即时匹配模块"])
app.include_router(match_status_router, tags=["匹配状态模块"])
app.include_router(post_router, tags=["帖子模块"])
app.include_router(comment_router, tags=["评论模块"])
app.include_router(like_router, tags=["点赞模块"])
app.include_router(collect_router, tags=["收藏模块"])
app.include_router(message_router, tags=["消息通知模块"])



# 启动服务
if __name__ == "__main__":
    # 启动应用
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))  # 自动获取云平台分配的端口
    # uvicorn.run(app, host="10.223.98.11", port=8000)  发语音不行
    uvicorn.run(app, host="0.0.0.0", port=port)