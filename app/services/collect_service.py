# app/services/collect_service.py
from typing import List, Optional
from app.models.collect import Collect
from app.models.post import Post
from tortoise.expressions import F
from tortoise.exceptions import IntegrityError

async def toggle_post_collect(user_id: int, post_id: int) -> bool:
    """
    收藏/取消收藏帖子（切换逻辑）
    """
    # 查找是否存在收藏记录
    collect = await Collect.get_or_none(user_id=user_id, post_id=post_id)
    
    if collect:
        # 1. 如果已收藏，取消并减计数
        await collect.delete()
        await Post.filter(id=post_id).update(collect_count=F("collect_count") - 1)
        return False
    else:
        # 2. 如果未收藏，创建并加计数
        try:
            await Collect.create(
                user_id=user_id,
                post_id=post_id
            )
            await Post.filter(id=post_id).update(collect_count=F("collect_count") + 1)
            return True
        except IntegrityError:
            return True

async def get_user_collects(user_id: int, page: int = 1, page_size: int = 10) -> List[Post]:
    """
    获取用户的收藏列表
    """
    offset = (page - 1) * page_size
    # 这里通过反向关联 collect -> post 获得帖子列表
    collects = await Collect.filter(user_id=user_id).prefetch_related("post__user").limit(page_size).offset(offset).order_by("-created_at")
    return [c.post for c in collects if c.post]

async def is_collected(user_id: int, post_id: int) -> bool:
    """
    检查是否已收藏该帖子
    """
    return await Collect.exists(user_id=user_id, post_id=post_id)
