# 即时匹配服务
# app/services/instant_match.py
from datetime import datetime, timedelta
from app.models import MatchRecord, InstantMatchWait, User, Interest
from tortoise import timezone as dt_timezone
from tortoise.transactions import in_transaction
from app.services.notification import send_match_notification

async def handle_instant_match(user_id: int, interest_id: int):
    """处理即时匹配请求"""
    # 1. 检查是否已经存在正在匹配中的相同记录
    existing_record = await MatchRecord.filter(
        user1_id=user_id,
        interest_id=interest_id,
        status=MatchRecord.MatchStatus.MATCHING.value,
        match_type=MatchRecord.MatchType.INSTANT.value
    ).first()
    if existing_record:
        return existing_record

    # 2. 查找具有相同兴趣的其他用户（在20分钟内）
    now = dt_timezone.now()
    time_range_start = now - timedelta(minutes=20)
    time_range_end = now + timedelta(minutes=20)
    
    potential_matches = await InstantMatchWait.filter(
        interest_id=interest_id,
        user_id__not=user_id,
        is_matched=False,
        clicked_at__gte=time_range_start,
        clicked_at__lte=time_range_end
    ).all()

    async with in_transaction():
        if potential_matches:
            # 3. 匹配成功
            match_user = await User.get(id=potential_matches[0].user_id)
            match_wait = potential_matches[0]
            
            # 创建已匹配记录
            match_record = await MatchRecord.create(
                user1_id=user_id,
                user2=match_user,
                interest_id=interest_id,
                match_type=MatchRecord.MatchType.INSTANT.value,
                status=MatchRecord.MatchStatus.MATCHED.value
            )
            
            # 查找并更新对方的匹配记录
            other_match_record = await MatchRecord.filter(
                user1_id=match_user.id,
                interest_id=interest_id,
                status=MatchRecord.MatchStatus.MATCHING.value,
                match_type=MatchRecord.MatchType.INSTANT.value
            ).first()
            
            if other_match_record:
                other_match_record.status = MatchRecord.MatchStatus.MATCHED.value
                other_match_record.user2_id = user_id
                await other_match_record.save()
                # 重新获取记录并加载关联关系
                other_match_record = await MatchRecord.get(id=other_match_record.id).prefetch_related('interest', 'user1', 'user2')
                # 发送匹配通知给对方
                await send_match_notification(other_match_record)
            
            # 重新获取记录并加载关联关系
            match_record = await MatchRecord.get(id=match_record.id).prefetch_related('interest', 'user1', 'user2')
            
            # 发送匹配通知
            await send_match_notification(match_record)
            
            # 更新等待记录为已匹配
            match_wait.is_matched = True
            await match_wait.save()
            
            return match_record
        else:
            # 4. 匹配中，进入等待队列
            # 创建匹配中记录
            match_record = await MatchRecord.create(
                user1_id=user_id,
                user2=None,
                interest_id=interest_id,
                match_type=MatchRecord.MatchType.INSTANT.value,
                status=MatchRecord.MatchStatus.MATCHING.value
            )
            
            # 插入即时匹配等待表
            await InstantMatchWait.create(
                user_id=user_id,
                interest_id=interest_id
            )
            
            return match_record

async def periodic_instant_match_check():
    """定期查询即时匹配（通常由定时任务调用）"""
    now = dt_timezone.now()
    time_limit = now - timedelta(minutes=20)
    
    # 1. 处理过期的记录
    expired_waits = await InstantMatchWait.filter(
        is_matched=False,
        clicked_at__lte=time_limit
    ).all()
    for wait in expired_waits:
        async with in_transaction():
            # 更新匹配记录为过期
            match_record = await MatchRecord.filter(
                user1_id=wait.user_id,
                interest_id=wait.interest_id,
                status=MatchRecord.MatchStatus.MATCHING.value,
                match_type=MatchRecord.MatchType.INSTANT.value
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
    active_waits = await InstantMatchWait.filter(
        is_matched=False,
        clicked_at__gt=time_limit
    ).all()
    for wait in active_waits:
        # 查找是否有新用户加入
        time_range_start = now - timedelta(minutes=20)
        time_range_end = now + timedelta(minutes=20)
        
        potential_matches = await InstantMatchWait.filter(
            interest_id=wait.interest_id,
            user_id__not=wait.user_id,
            is_matched=False,
            clicked_at__gte=time_range_start,
            clicked_at__lte=time_range_end
        ).all()
        
        if potential_matches:
            match_user = await User.get(id=potential_matches[0].user_id)
            match_wait = potential_matches[0]
            
            async with in_transaction():
                # 更新当前用户的匹配记录
                match_record = await MatchRecord.filter(
                    user1_id=wait.user_id,
                    interest_id=wait.interest_id,
                    status=MatchRecord.MatchStatus.MATCHING.value,
                    match_type=MatchRecord.MatchType.INSTANT.value
                ).first()
                
                if match_record:
                    match_record.status = MatchRecord.MatchStatus.MATCHED.value
                    match_record.user2 = match_user
                    await match_record.save()
                    # 重新获取记录并加载关联关系
                    match_record = await MatchRecord.get(id=match_record.id).prefetch_related('interest', 'user1', 'user2')
                    # 发送匹配通知
                    await send_match_notification(match_record)
                
                # 更新对方的匹配记录
                other_match_record = await MatchRecord.filter(
                    user1_id=match_user.id,
                    interest_id=wait.interest_id,
                    status=MatchRecord.MatchStatus.MATCHING.value,
                    match_type=MatchRecord.MatchType.INSTANT.value
                ).first()
                
                if other_match_record:
                    other_match_record.status = MatchRecord.MatchStatus.MATCHED.value
                    other_match_record.user2_id = wait.user_id
                    await other_match_record.save()
                    # 重新获取记录并加载关联关系
                    other_match_record = await MatchRecord.get(id=other_match_record.id).prefetch_related('interest', 'user1', 'user2')
                    # 发送匹配通知给对方
                    await send_match_notification(other_match_record)
            
            # 更新等待记录为已匹配
            wait.is_matched = True
            await wait.save()
            match_wait.is_matched = True
            await match_wait.save()