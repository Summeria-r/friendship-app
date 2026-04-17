# 通知服务
# app/services/notification.py
from app.models import User, Private_message, MatchRecord

async def init_system_user():
    """初始化系统用户"""
    system_user, created = await User.get_or_create(
        username="system",
        defaults={
            "password": "system_password",  # 实际应用中应该使用加密密码
            "nickname": "系统消息",
            "is_system": True,
            "account_status": User.AccountStatus.ACTIVE.value
        }
    )
    return system_user


async def send_match_notification(match_record: MatchRecord):
    """发送匹配通知"""
    # 确保关联关系已加载
    if not match_record.interest or not match_record.user1 or (match_record.status == MatchRecord.MatchStatus.MATCHED.value and not match_record.user2):
        # 重新从数据库获取完整的记录，包含关联对象
        match_record = await MatchRecord.get(id=match_record.id).prefetch_related('interest', 'user1', 'user2')
    
    # 确保interest是一个对象而不是QuerySet
    if hasattr(match_record.interest, 'name'):
        # interest是一个对象，直接使用
        pass
    else:
        # interest可能是一个QuerySet，尝试获取第一个对象
        try:
            match_record.interest = await match_record.interest.first()
        except Exception as e:
            # 如果获取失败，使用默认值
            interest_name = "未知兴趣"
            # 继续执行，避免中断流程

    # 获取系统用户
    system_user = await init_system_user()
    
    # 构建通知内容
    interest_name = "未知兴趣"
    try:
        if hasattr(match_record.interest, 'name'):
            if hasattr(match_record.interest.name, 'value'):
                interest_name = match_record.interest.name.value
            else:
                interest_name = match_record.interest.name
    except Exception as e:
        # 如果获取失败，使用默认值
        pass
    match_type = "即时" if match_record.match_type == MatchRecord.MatchType.INSTANT.value else "长期"
    
    if match_record.status == MatchRecord.MatchStatus.MATCHED.value:
        # 匹配成功通知
        content = f"您的{match_type}匹配已成功！您与用户【{match_record.user2.nickname or match_record.user2.username}】在【{interest_name}】兴趣上匹配成功。"
        # 向发起者发送通知
        await Private_message.create(
            sender=system_user,
            receiver=match_record.user1,
            content=content,
            message_type=Private_message.MessageType.SYSTEM.value
        )
        # 向被匹配者发送通知
        content_for_partner = f"您的{match_type}匹配已成功！您与用户【{match_record.user1.nickname or match_record.user1.username}】在【{interest_name}】兴趣上匹配成功。"
        await Private_message.create(
            sender=system_user,
            receiver=match_record.user2,
            content=content_for_partner,
            message_type=Private_message.MessageType.SYSTEM.value
        )
    elif match_record.status == MatchRecord.MatchStatus.EXPIRED.value:
        # 匹配过期通知
        content = f"您的{match_type}匹配已过期。未能在规定时间内找到合适的【{interest_name}】兴趣匹配对象。"
        # 向发起者发送通知
        await Private_message.create(
            sender=system_user,
            receiver=match_record.user1,
            content=content,
            message_type=Private_message.MessageType.SYSTEM.value
        )