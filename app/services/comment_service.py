# app/services/comment_service.py
from typing import List, Optional
from app.models.comment import Comment
from app.models.post import Post
from tortoise.expressions import F

async def create_comment(user_id: int, post_id: int, content: str, parent_id: Optional[int] = None) -> Comment:
    """
    创建评论（支持楼中楼回复）
    """
    # 开启事务（Tortoise 默认自动处理，如需原子性可用 in_transaction）
    comment = await Comment.create(
        user_id=user_id,
        post_id=post_id,
        content=content,
        parent_id=parent_id
    )
    
    # 更新帖子的评论数（原子操作）
    await Post.filter(id=post_id).update(comment_count=F("comment_count") + 1)
    
    return comment

async def delete_comment(comment_id: int, user_id: int) -> bool:
    """
    删除评论（仅限原作者）
    """
    comment = await Comment.get_or_none(id=comment_id, user_id=user_id).prefetch_related("post")
    if comment:
        post_id = comment.post.id
        await comment.delete()
        # 更新帖子的评论数
        await Post.filter(id=post_id).update(comment_count=F("comment_count") - 1)
        return True
    return False

async def get_paged_comments(post_id: int, page: int = 1, page_size: int = 20) -> List[Comment]:
    """
    获取帖子的顶级评论（及其子回复）
    """
    offset = (page - 1) * page_size
    return await Comment.filter(
        post_id=post_id,
        parent=None
    ).prefetch_related("user", "replies__user").limit(page_size).offset(offset).order_by("-created_at")

async def get_replies(comment_id: int) -> List[Comment]:
    """
    获取指定评论的子回复
    """
    return await Comment.filter(parent_id=comment_id).prefetch_related("user").order_by("created_at")
