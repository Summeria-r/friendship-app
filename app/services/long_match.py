# 匹配服务
# app/services/match.py
from datetime import datetime, timedelta
from app.models import MatchRecord, LongTermMatchWait, User, Interest
from tortoise import timezone as dt_timezone
from tortoise.transactions import in_transaction
from app.services.notification import send_match_notification

async def handle_long_term_match(user_id: int, interest_id: int):
    """处理长期匹配请求"""
    # 1. 检查是否已经存在正在匹配中的相同记录
    existing_record = await MatchRecord.filter(
        user1_id=user_id,
        interest_id=interest_id,
        status=MatchRecord.MatchStatus.MATCHING.value
    ).first()
    if existing_record:
        return existing_record

    # 2. 查找具有相同兴趣的其他用户
    potential_matches = await User.filter(
        interests__id=interest_id,
        id__not=user_id,
        account_status=User.AccountStatus.ACTIVE.value
    ).all()

    async with in_transaction():
        if potential_matches:
            # 3. 匹配成功
            match_user = potential_matches[0]
            
            # 创建已匹配记录
            match_record = await MatchRecord.create(
                user1_id=user_id,
                user2=match_user,
                interest_id=interest_id,
                match_type=MatchRecord.MatchType.LONG_TERM.value,
                status=MatchRecord.MatchStatus.MATCHED.value
            )
            
            # 重新获取记录并加载关联关系
            match_record = await MatchRecord.get(id=match_record.id).prefetch_related('interest', 'user1', 'user2')
            
            # 发送匹配通知
            await send_match_notification(match_record)
            
            return match_record
        else:
            # 4. 匹配中，进入等待队列
            expire_at = dt_timezone.now() + timedelta(minutes=20)
            
            # 创建匹配中记录
            match_record = await MatchRecord.create(
                user1_id=user_id,
                user2=None,
                interest_id=interest_id,
                match_type=MatchRecord.MatchType.LONG_TERM.value,
                status=MatchRecord.MatchStatus.MATCHING.value,
                expire_at=expire_at
            )
            
            # 插入长期匹配等待表
            await LongTermMatchWait.create(
                user_id=user_id,
                interest_id=interest_id,
                expire_at=expire_at
            )
            
            return match_record

async def periodic_match_check():
    """定期查询匹配（通常由定时任务调用）"""
    now = dt_timezone.now()
    
    # 1. 处理过期的记录
    expired_waits = await LongTermMatchWait.filter(expire_at__lte=now).all()
    for wait in expired_waits:
        async with in_transaction():
            # 更新匹配记录为过期
            match_record = await MatchRecord.filter(
                user1_id=wait.user_id,
                interest_id=wait.interest_id,
                status=MatchRecord.MatchStatus.MATCHING.value
            ).first()
            
            if match_record:
                match_record.status = MatchRecord.MatchStatus.EXPIRED.value
                await match_record.save()
                # 重新获取记录并加载关联关系
                match_record = await MatchRecord.get(id=match_record.id).prefetch_related('interest', 'user1')
                # 发送过期通知
                await send_match_notification(match_record)
            
            # 删除等待记录
            await wait.delete()
    
    # 2. 处理正在匹配中的记录
    active_waits = await LongTermMatchWait.filter(expire_at__gt=now).all()
    for wait in active_waits:
        # 查找是否有新用户更新了兴趣
        potential_matches = await User.filter(
            interests__id=wait.interest_id,
            id__not=wait.user_id,
            account_status=User.AccountStatus.ACTIVE.value
        ).all()
        
        if potential_matches:
            match_user = potential_matches[0]
            async with in_transaction():
                # 更新匹配记录为成功
                match_record = await MatchRecord.filter(
                    user1_id=wait.user_id,
                    interest_id=wait.interest_id,
                    status=MatchRecord.MatchStatus.MATCHING.value
                ).first()
                
                if match_record:
                    match_record.status = MatchRecord.MatchStatus.MATCHED.value
                    match_record.user2 = match_user
                    await match_record.save()
                    # 重新获取记录并加载关联关系
                    match_record = await MatchRecord.get(id=match_record.id).prefetch_related('interest', 'user1', 'user2')
                    # 发送匹配成功通知
                    await send_match_notification(match_record)
                
                # 删除等待记录
                await wait.delete()