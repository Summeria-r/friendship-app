# app/services/post_service.py
from typing import List, Optional
from app.models.post import Post
from app.models.users import User
from tortoise.expressions import F, Q

async def create_post(user_id: int, title: str, content: str, category: str, is_sticky: bool = False, image_urls: list = None) -> Post:
    """
    创建新帖子
    """
    post = await Post.create(
        user_id=user_id,
        title=title,
        content=content,
        category=category,
        is_sticky=is_sticky,
        image_urls=image_urls or []
    )
    return post

async def update_post(post_id: int, user_id: int, title: str, content: str, category: str) -> Optional[Post]:
    """
    更新帖子
    """
    post = await Post.get_or_none(id=post_id, user_id=user_id)
    if post:
        post.title = title
        post.content = content
        post.category = category
        await post.save()
    return post

async def delete_post(post_id: int, user_id: int) -> bool:
    """
    删除帖子
    """
    post = await Post.get_or_none(id=post_id, user_id=user_id)
    if post:
        await post.delete()
        return True
    return False

async def get_paged_posts(category: Optional[str] = None, page: int = 1, page_size: int = 10) -> List[Post]:
    """
    分页查询帖子
    """
    query = Post.all().prefetch_related("user")
    if category:
        query = query.filter(category=category)
    
    # 分页逻辑
    offset = (page - 1) * page_size
    return await query.limit(page_size).offset(offset).order_by("-is_sticky", "-created_at")

async def get_latest_posts(limit: int = 6) -> List[Post]:
    """
    按发布时间倒序获取最新帖子，不受置顶影响
    """
    return await Post.all().prefetch_related("user").order_by("-created_at").limit(limit)

async def get_post_detail(post_id: int) -> Optional[Post]:
    """
    获取帖子详情（包含作者和评论）
    """
    return await Post.get_or_none(id=post_id).prefetch_related("user")

async def get_hot_posts(limit: int = 10) -> List[Post]:
    """
    获取热搜榜前10(基于 综合热度 = 点赞 + 收藏 + 评论)
    """
    # 使用 annotate 计算综合热度
    return await Post.all().annotate(
        hot_score=F("like_count") + F("collect_count") + F("comment_count")
    ).prefetch_related("user").order_by("-hot_score", "-created_at").limit(limit)

async def search_posts(keyword: str, page: int = 1, page_size: int = 10) -> List[Post]:
    """
    搜索帖子
    """
    offset = (page - 1) * page_size
    return await Post.filter(
        Q(title__icontains=keyword) | Q(content__icontains=keyword)
    ).prefetch_related("user").limit(page_size).offset(offset).order_by("-created_at")
