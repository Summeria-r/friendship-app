# app/services/private_message_service.py
from typing import List, Optional
from app.models.private_message import Private_message
from app.models.users import User
from tortoise.expressions import Q

async def send_message(sender_id: int, receiver_id: int, content: str, message_type: str = "text") -> Private_message:
    """
    发送私聊消息
    """
    message = await Private_message.create(
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=content,
        message_type=message_type
    )
    return message

async def get_chat_history(user_a: int, user_b: int, limit: int = 50) -> List[Private_message]:
    """
    获取两个用户之间的聊天历史记录
    """
    # 核心：查询 (A->B OR B->A) 的所有记录并按时间排序
    messages = await Private_message.filter(
        Q(sender_id=user_a, receiver_id=user_b) | Q(sender_id=user_b, receiver_id=user_a)
    ).prefetch_related("sender", "receiver").order_by("-created_at").limit(limit)
    
    # 返回前反转列表（按时间正序排列以便对话流展示）
    return sorted(messages, key=lambda x: x.created_at)

async def mark_chat_as_read(user_id: int, sender_id: int):
    """
    将来自指定发送者的消息全部设为已读
    """
    await Private_message.filter(receiver_id=user_id, sender_id=sender_id, is_read=False).update(is_read=True)

async def get_unread_count(user_id: int) -> int:
    """
    查询用户未读消息总数
    """
    return await Private_message.filter(receiver_id=user_id, is_read=False).count()

async def get_recent_chat_list(user_id: int) -> List[dict]:
    """
    获取最近聊天的人员列表（去重并按最新消息排序）
    """
    # 获取用户所有收发的消息，提取对方 ID 并去重
    sent_to = await Private_message.filter(sender_id=user_id).values_list("receiver_id", flat=True)
    received_from = await Private_message.filter(receiver_id=user_id).values_list("sender_id", flat=True)
    
    other_user_ids = list(set(sent_to) | set(received_from))
    
    # 获取用户信息、最后一条消息和未读消息数量
    recent_users = []
    for user_id_other in other_user_ids:
        user = await User.get_or_none(id=user_id_other)
        if user:
            # 获取最后一条消息
            last_message = await Private_message.filter(
                Q(sender_id=user_id, receiver_id=user_id_other) | Q(sender_id=user_id_other, receiver_id=user_id)
            ).order_by("-created_at").first()
            
            # 获取未读消息数量
            unread_count = await Private_message.filter(
                sender_id=user_id_other, receiver_id=user_id, is_read=False
            ).count()
            
            # 构建用户信息字典
            user_dict = {
                "id": user.id,
                "nickname": user.nickname,
                "avatar": user.avatar,
                "major": user.major,
                "last_message": last_message.content if last_message else None,
                "unread_count": unread_count
            }
            recent_users.append(user_dict)
    
    return recent_users
