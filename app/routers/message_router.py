# app/routers/message_router.py
from fastapi import APIRouter, Request, HTTPException, Form, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.models.users import User
from app.services import notification_service, private_message_service
from typing import Optional, Dict, List
import json
import os
import uuid
import mimetypes

# 尝试导入pydub来计算音频时长
try:
    from pydub import AudioSegment
except ImportError:
    # 如果没有安装pydub，使用默认值
    AudioSegment = None

message_router = APIRouter()


# 0. 实时聊天 WebSocket 管理
class ConnectionManager:
    def __init__(self):
        # 存储 active connections: {user_id: WebSocket}
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)

manager = ConnectionManager()

@message_router.websocket("/ws/chat/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """
    实时聊天 WebSocket 端点
    """
    await manager.connect(user_id, websocket)
    try:
        while True:
            # 接收前端发送的消息内容
            data = await websocket.receive_text()
            message_data = json.loads(data)
            receiver_id = int(message_data.get("receiver_id"))
            content = message_data.get("content")

            # 1. 持久化到数据库
            msg = await private_message_service.send_message(
                sender_id=user_id,
                receiver_id=receiver_id,
                content=content
            )

            # 2. 如果对方在线，实时推送
            await manager.send_personal_message({
                "sender_id": user_id,
                "content": content,
                "created_at": str(msg.created_at),
                "type": "chat",
                "message_type": msg.message_type
            }, receiver_id)
            
            # 3. 给发送者自己也回传一个确认消息（用于前端渲染）
            await manager.send_personal_message({
                "sender_id": user_id,
                "content": content,
                "created_at": str(msg.created_at),
                "type": "self",
                "message_type": msg.message_type
            }, user_id)

    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(f"WebSocket Error: {e}")
        manager.disconnect(user_id)

# ========================
# 1. 通知中心 (Notification)
# ========================

# 1.1 通知中心页面
@message_router.get("/notifications", response_class=HTMLResponse)
async def list_notifications(request: Request, page: int = 1):
    """
    显示用户的社区互动通知列表
    """
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")
    templates.env.cache = None  # 完全禁用缓存
    user_data = request.session.get("user")
    if not user_data:
        return RedirectResponse(url="/login", status_code=303)
    
    notifications = await notification_service.get_user_notifications(user_data["id"], page)
    
    return templates.TemplateResponse(
        "post_message.html",
        {
            "request": request,
            "notifications": notifications,
            "page": page
        }
    )

# 1.2 一键已读通知
@message_router.post("/notifications/read-all")
async def mark_all_notifications_read(request: Request):
    """
    业务：一键清空未读通知
    """
    user_data = request.session.get("user")
    if not user_data:
        raise HTTPException(status_code=401, detail="请先登录")
    
    await notification_service.mark_all_as_read(user_data["id"])
    return RedirectResponse(url="/notifications", status_code=303)

# 1.3 删除单条通知
@message_router.post("/notifications/delete/{notification_id}")
async def delete_notification_action(request: Request, notification_id: int):
    """
    删除单条通知记录
    """
    user_data = request.session.get("user")
    if not user_data:
        raise HTTPException(status_code=401, detail="请先登录")
    
    success = await notification_service.delete_notification(user_data["id"], notification_id)
    if not success:
        raise HTTPException(status_code=403, detail="删除失败")
    
    return RedirectResponse(url="/notifications", status_code=303)


# ========================
# 2. 私聊消息 (Private Message)
# ========================

# 2.1 消息中心 - 最近联系人列表
@message_router.get("/messages", response_class=HTMLResponse)
async def chat_list_page(request: Request):
    """
    显示私聊人员列表（最近聊天的人）
    """
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")
    templates.env.cache = None  # 完全禁用缓存
    user_data = request.session.get("user")
    if not user_data:
        return RedirectResponse(url="/login", status_code=303)
    
    recent_users = await private_message_service.get_recent_chat_list(user_data["id"])
    
    # 计算未读消息总数
    unread_count = sum(user.unread_count for user in recent_users if hasattr(user, 'unread_count'))
    
    return templates.TemplateResponse(
        "message.html",
        {
            "request": request,
            "recent_users": recent_users,
            "unread_count": unread_count
        }
    )

# 2.2 聊天对话详情页
@message_router.get("/messages/chat/{receiver_id}", response_class=HTMLResponse)
async def chat_detail_page(request: Request, receiver_id: int):
    """
    显示与特定用户的对话历史
    """
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")
    templates.env.cache = None  # 完全禁用缓存
    
    user_data = request.session.get("user")
    if not user_data:
        return RedirectResponse(url="/login", status_code=303)
    
    # 获取接收者信息
    receiver = await User.get_or_none(id=receiver_id)
    if not receiver:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 获取对话历史记录
    history = await private_message_service.get_chat_history(user_data["id"], receiver_id)
    
    # 获取最近联系人列表
    recent_users = await private_message_service.get_recent_chat_list(user_data["id"])
    
    # 业务：进入对话页后，将对方发给我的消息设为已读
    await private_message_service.mark_chat_as_read(user_id=user_data["id"], sender_id=receiver_id)
    
    return templates.TemplateResponse(
        "message_detail.html",
        {
            "request": request,
            "history": history,
            "receiver": receiver,
            "recent_users": recent_users,
            "user": user_data
        }
    )

# 2.3 发送消息接口
@message_router.post("/messages/send")
async def send_message_action(
    request: Request,
    receiver_id: int = Form(...),
    content: str = Form(...),
    message_type: str = Form("text"),
    audio: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None)
):
    """
    处理发送私聊消息请求
    """

    
    user_data = request.session.get("user")
    if not user_data:
        raise HTTPException(status_code=401, detail="请先登录")
    
    # 处理图片消息
    if message_type == "image":
        if not image or not image.filename:
            return JSONResponse({"status": "error", "error": "未检测到图片文件"}, status_code=400)

        image_dir = "static/uploads/message_images"
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)

        allowed_image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        image_ext = os.path.splitext(image.filename)[1].lower()
        if image_ext not in allowed_image_extensions:
            return JSONResponse({"status": "error", "error": "暂不支持该图片格式"}, status_code=400)

        filename = f"{uuid.uuid4()}_{image.filename}"
        file_path = os.path.join(image_dir, filename)

        try:
            image_bytes = await image.read()
            if not image_bytes:
                return JSONResponse({"status": "error", "error": "图片文件为空"}, status_code=400)

            with open(file_path, "wb") as buffer:
                buffer.write(image_bytes)

            image_url = f"/static/uploads/message_images/{filename}"
            content = f'<img src="{image_url}" class="message-img" alt="聊天图片" onclick="viewImage(\'{image_url}\')">'
        except Exception as e:
            print(f"保存图片文件失败: {e}")
            return JSONResponse({"status": "error", "error": "图片消息发送失败"}, status_code=500)

    # 处理语音消息
    if message_type == "voice":
        if not audio or not audio.filename:
            return JSONResponse({"status": "error", "error": "未检测到语音文件"}, status_code=400)

        # 创建音频存储目录
        audio_dir = "static/uploads/audio"
        if not os.path.exists(audio_dir):
            os.makedirs(audio_dir)
        
        allowed_extensions = {".webm", ".wav", ".mp3", ".m4a", ".ogg", ".aac", ".mp4"}
        original_ext = os.path.splitext(audio.filename)[1].lower()
        if original_ext not in allowed_extensions:
            return JSONResponse({"status": "error", "error": "暂不支持该语音格式"}, status_code=400)

        filename = f"{uuid.uuid4()}_{audio.filename}"
        file_path = os.path.join(audio_dir, filename)
        
        try:
            audio_bytes = await audio.read()
            if not audio_bytes:
                return JSONResponse({"status": "error", "error": "语音文件为空"}, status_code=400)

            with open(file_path, "wb") as buffer:
                buffer.write(audio_bytes)
            
            audio_url = f"/static/uploads/audio/{filename}"
            audio_type = audio.content_type or mimetypes.guess_type(audio.filename)[0] or "audio/webm"
            
            # 计算语音时长
            duration = 5  # 默认值
            
            # 方法1: 使用pydub计算音频时长
            if AudioSegment:
                try:
                    # 使用pydub计算音频时长
                    print(f"开始计算音频时长，文件路径: {file_path}")
                    print(f"文件存在: {os.path.exists(file_path)}")
                    if os.path.exists(file_path):
                        print(f"文件大小: {os.path.getsize(file_path)} bytes")
                    audio_segment = AudioSegment.from_file(file_path)
                    duration = int(audio_segment.duration_seconds)
                    # 确保时长至少为1秒
                    duration = max(1, duration)
                    print(f"使用pydub计算的时长: {duration}秒")
                except Exception as e:
                    print(f"计算音频时长失败: {e}")
                    # 如果pydub失败，尝试使用方法2
                    try:
                        file_size = os.path.getsize(file_path)
                        print(f"文件大小: {file_size} bytes")
                        # 假设平均比特率为128kbps
                        # 128kbps = 16KB/s
                        duration = int(file_size / (16 * 1024))
                        # 确保时长在合理范围内
                        duration = max(1, min(duration, 60))
                        print(f"使用文件大小估算的时长: {duration}秒")
                    except Exception as e2:
                        print(f"使用文件大小估算时长失败: {e2}")
                        duration = 5
            else:
                # 方法2: 不依赖pydub的简单计算（基于文件大小估算）
                try:
                    file_size = os.path.getsize(file_path)
                    print(f"文件大小: {file_size} bytes")
                    # 假设平均比特率为128kbps
                    # 128kbps = 16KB/s
                    duration = int(file_size / (16 * 1024))
                    # 确保时长在合理范围内
                    duration = max(1, min(duration, 60))
                    print(f"使用文件大小估算的时长: {duration}秒")
                except Exception as e:
                    print(f"使用文件大小估算时长失败: {e}")
                    duration = 5
            print(f"最终音频时长: {duration}秒")
            
            # 根据时长计算语音条的宽度（最小60px，最大200px）
            min_width = 60
            max_width = 200
            width = min_width + (max_width - min_width) * min(duration / 60, 1)
            
            content = (
                f'<div class="voice-message-item" data-src="{audio_url}" '
                f'data-duration="{duration}" onclick="playVoice(this)" style="width: {width}px;">'
                f'<span class="voice-icon"><i class="fa fa-volume-up"></i></span>'
                f'<span class="voice-time">{duration}″</span>'
                f'</div>'
            )
        except Exception as e:
            print(f"保存音频文件失败: {e}")
            return JSONResponse({"status": "error", "error": "语音消息发送失败"}, status_code=500)
    
    # 发送消息并获取消息对象
    msg = await private_message_service.send_message(
        sender_id=user_data["id"],
        receiver_id=receiver_id,
        content=content,
        message_type=message_type
    )
    
    # 实时推送消息给接收方
    await manager.send_personal_message({
        "sender_id": user_data["id"],
        "content": content,
        "created_at": str(msg.created_at),
        "type": "chat",
        "message_type": message_type
    }, receiver_id)
    
    # 给发送者自己也回传一个确认消息（用于前端渲染）
    await manager.send_personal_message({
        "sender_id": user_data["id"],
        "content": content,
        "created_at": str(msg.created_at),
        "type": "self",
        "message_type": message_type
    }, user_data["id"])
    
    # 业务：通常发送后异步刷新页面或 AJAX 局部刷新
    # 对于语音消息，返回JSON响应，前端会自动刷新
    if message_type == "voice":
        return JSONResponse({"status": "success", "message": "语音消息发送成功"})
    if message_type == "image":
        return JSONResponse({"status": "success", "message": "图片消息发送成功"})
    return RedirectResponse(url=f"/messages/chat/{receiver_id}", status_code=303)

# 2.4 私聊确认页面
@message_router.get("/to_chat/{user_id}", response_class=HTMLResponse)
async def to_chat_page(request: Request, user_id: int):
    """
    显示与特定用户的私聊确认页面
    """
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")
    templates.env.cache = None  # 完全禁用缓存
    
    user_data = request.session.get("user")
    if not user_data:
        return RedirectResponse(url="/login", status_code=303)
    
    # 获取目标用户信息
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return templates.TemplateResponse(
        "to_chat.html",
        {
            "request": request,
            "user": user
        }
    )

# 2.5 获取未读消息数量
@message_router.get("/messages/unread-count")
async def get_unread_count(request: Request):
    """
    获取未读消息数量
    """
    user_data = request.session.get("user")
    if not user_data:
        return JSONResponse({"unread_count": 0})
    
    # 获取最近联系人列表
    recent_users = await private_message_service.get_recent_chat_list(user_data["id"])
    
    # 计算未读消息总数
    unread_count = sum(user.unread_count for user in recent_users if hasattr(user, 'unread_count'))
    
    return JSONResponse({"unread_count": unread_count})