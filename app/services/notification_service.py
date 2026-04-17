# app/services/notification_service.py
from typing import List, Optional
from app.models.comment import Comment
from app.models.post import Post
from app.models.users import User
from app.models.post_message import Post_message as Notification
# async def init_system_user():
#     """初始化系统用户"""
#     system_user, created = await User.get_or_create(
#         username="system",
#         defaults={
#             "password": "system_password",  
#             "nickname": "系统消息",
#             "is_system": True,
#             "account_status": User.AccountStatus.ACTIVE.value
#         }
#     )
#     return system_user

# async def send_match_notification(match_record):
#     """发送匹配通知 """
#     # 获取系统用户
#     system_user = await init_system_user()
    
#     # 构建通知内容
#     interest_name = match_record.interest.name
#     match_type = "即时" if match_record.match_type == "instant" else "长期"
    
#     if match_record.status == "matched":
#         # 匹配成功通知
#         content = f"您的{match_type}匹配已成功！您与用户{match_record.user2.username}在{interest_name}兴趣上匹配成功。"
#         # 向发起者发送通知
#         await Private_message.create(
#             sender=system_user,
#             receiver=match_record.user1,
#             content=content,
#             message_type=Private_message.MessageType.SYSTEM.value
#         )
#         # 向被匹配者发送通知
#         await Private_message.create(
#             sender=system_user,
#             receiver=match_record.user2,
#             content=content,
#             message_type=Private_message.MessageType.SYSTEM.value
#         )
#     elif match_record.status == "expired":
#         # 匹配过期通知
#         content = f"您的{match_type}匹配已过期。未能在规定时间内找到合适的{interest_name}兴趣匹配对象。"
#         # 向发起者发送通知
#         await Private_message.create(
#             sender=system_user,
#             receiver=match_record.user1,
#             content=content,
#             message_type=Private_message.MessageType.SYSTEM.value
#         )

async def create_comment_notification(comment: Comment):
    """
    当有新评论/回复时生成通知
    """
    # 1. 业务逻辑：如果是楼中楼，通知评论作者；如果是根评论，通知帖子作者
    if comment.parent_id:
        parent_comment = await Comment.get(id=comment.parent_id).prefetch_related("user")
        receiver = parent_comment.user#被回复的评论作者
        notification_type = Notification.NotificationType.COMMENT_REPLY
        content_text = f"有人回复了你的评论：{comment.content[:20]}..."
    else:
        post = await Post.get(id=comment.post_id).prefetch_related("user")
        receiver = post.user
        notification_type = Notification.NotificationType.POST_COMMENT
        content_text = f"有人评论了你的帖子：{comment.content[:20]}..."
    
    # 如果是自己评论自己，不发通知
    if receiver.id == comment.user_id:
        return

    # 获取发送者用户对象
    sender = await User.get_or_none(id=comment.user_id)
    if not sender:
        return

    # 2. 数据库插入通知记录
    await Notification.create(
        user=receiver,
        sender=sender,
        type=notification_type,
        post_id=comment.post_id,
        comment_id=comment.id,
        content=content_text
    )

async def create_like_notification(sender_id: int, target_id: int, target_type: str = "post"):
    """
    点赞时生成通知
    """
    if target_type == "post":
        post = await Post.get(id=target_id).prefetch_related("user")
        receiver = post.user
        notification_type = Notification.NotificationType.POST_LIKE
        content_text = "赞了你的帖子"
        post_id = target_id
        comment_id = None
    else:
        comment = await Comment.get(id=target_id).prefetch_related("user")
        receiver = comment.user
        notification_type = Notification.NotificationType.COMMENT_LIKE
        content_text = "赞了你的评论"
        post_id = comment.post_id
        comment_id = target_id
    
    if receiver.id == sender_id:
        return

    # 获取发送者用户对象
    sender = await User.get_or_none(id=sender_id)
    if not sender:
        return

    await Notification.create(
        user=receiver,
        sender=sender,
        type=notification_type,
        post_id=post_id,
        comment_id=comment_id,
        content=content_text
    )

async def create_collect_notification(sender_id: int, post_id: int):
    """
    收藏时生成通知
    """
    post = await Post.get(id=post_id).prefetch_related("user")
    receiver = post.user
    
    if receiver.id == sender_id:
        return

    # 获取发送者用户对象
    sender = await User.get_or_none(id=sender_id)
    if not sender:
        return

    await Notification.create(
        user=receiver,
        sender=sender,
        type=Notification.NotificationType.POST_COLLECT,
        post_id=post_id,
        content="收藏了你的帖子"
    )

async def get_user_notifications(user_id: int, page: int = 1, page_size: int = 20) -> List[Notification]:
    """
    查询用户的通知列表（按时间倒序）
    """
    offset = (page - 1) * page_size
    return await Notification.filter(user_id=user_id).prefetch_related("sender", "post", "comment").limit(page_size).offset(offset).order_by("-created_at")

async def mark_all_as_read(user_id: int):
    """
    一键置为已读
    """
    await Notification.filter(user_id=user_id, is_read=False).update(is_read=True)

async def delete_notification(user_id: int, notification_id: int) -> bool:
    """
    删除通知记录
    """
    notification = await Notification.get_or_none(id=notification_id, user_id=user_id)
    if notification:
        await notification.delete()
        return True
    return False

