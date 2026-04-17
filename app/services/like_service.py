# app/services/like_service.py
from typing import Optional
from app.models.like import Likes
from app.models.post import Post
from app.models.comment import Comment
from tortoise.expressions import F
from tortoise.exceptions import IntegrityError

async def toggle_post_like(user_id: int, post_id: int) -> dict:
    """
    点赞/取消点赞帖子（切换逻辑）
    返回：{"is_liked": bool, "like_count": int}
    """
    # 查找是否已存在点赞记录
    like = await Likes.get_or_none(user_id=user_id, post_id=post_id, like_type="post")
    
    if like:
        # 1. 如果已点赞，取消点赞并减计数
        await like.delete()
        await Post.filter(id=post_id).update(like_count=F("like_count") - 1)
        # 获取更新后的点赞数
        post = await Post.get_or_none(id=post_id)
        return {"is_liked": False, "like_count": post.like_count if post else 0}
    else:
        # 2. 如果未点赞，创建点赞并加计数
        try:
            await Likes.create(
                user_id=user_id,
                post_id=post_id,
                like_type="post"
            )
            await Post.filter(id=post_id).update(like_count=F("like_count") + 1)
            # 获取更新后的点赞数
            post = await Post.get_or_none(id=post_id)
            return {"is_liked": True, "like_count": post.like_count if post else 0}
        except IntegrityError:
            # 唯一约束拦截（防止极短时间内的重复点赞）
            post = await Post.get_or_none(id=post_id)
            return {"is_liked": True, "like_count": post.like_count if post else 0}

async def toggle_comment_like(user_id: int, comment_id: int) -> dict:
    """
    点赞/取消点赞评论（切换逻辑）
    返回：{"is_liked": bool, "like_count": int}
    """
    like = await Likes.get_or_none(user_id=user_id, comment_id=comment_id, like_type="comment")
    
    if like:
        await like.delete()
        await Comment.filter(id=comment_id).update(like_count=F("like_count") - 1)
        # 获取更新后的点赞数
        comment = await Comment.get_or_none(id=comment_id)
        return {"is_liked": False, "like_count": comment.like_count if comment else 0}
    else:
        try:
            await Likes.create(
                user_id=user_id,
                comment_id=comment_id,
                like_type="comment"
            )
            await Comment.filter(id=comment_id).update(like_count=F("like_count") + 1)
            # 获取更新后的点赞数
            comment = await Comment.get_or_none(id=comment_id)
            return {"is_liked": True, "like_count": comment.like_count if comment else 0}
        except IntegrityError:
            # 唯一约束拦截（防止极短时间内的重复点赞）
            comment = await Comment.get_or_none(id=comment_id)
            return {"is_liked": True, "like_count": comment.like_count if comment else 0}

async def is_liked(user_id: int, target_id: int, target_type: str = "post") -> bool:
    """
    检查用户是否已点赞
    """
    if target_type == "post":
        return await Likes.exists(user_id=user_id, post_id=target_id, like_type="post")
    else:
        return await Likes.exists(user_id=user_id, comment_id=target_id, like_type="comment")
