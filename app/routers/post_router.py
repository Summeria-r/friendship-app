# app/routers/post_router.py
from fastapi import APIRouter, Request, HTTPException, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.services import post_service
from app.security import get_current_user
from typing import Optional

post_router = APIRouter()

# 1. 帖子中心 (列表页) - 支持 /posts 和 /post_center 两个路由
@post_router.get("/posts", response_class=HTMLResponse)
async def list_posts(
    request: Request,
    category: Optional[str] = None,
    page: int = 1,
    keyword: Optional[str] = None
):
    """
    显示帖子列表中心，支持分类和搜索
    """
    from jinja2 import ChoiceLoader, FileSystemLoader
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")
    templates.env.loader = ChoiceLoader([FileSystemLoader("templates")])
    templates.env.cache = {}
    if keyword:
        posts = await post_service.search_posts(keyword, page)
        # 跳转到搜索结果页面
        return templates.TemplateResponse(
            "search_results.html",
            {
                "request": request,
                "posts": posts,
                "keyword": keyword,
                "page": page
            }
        )
    else:
        posts = await post_service.get_paged_posts(category, page)
        
        # 获取热门帖子（侧边栏热搜榜前10）
        hot_posts = await post_service.get_hot_posts(limit=10)
        
        return templates.TemplateResponse(
            "post_center.html",
            {
                "request": request,
                "posts": posts,
                "hot_posts": hot_posts,
                "current_category": category,
                "keyword": keyword,
                "page": page
            }
        )

# 2. 帖子中心 (列表页) - 支持 /post_center 路由
@post_router.get("/post_center", response_class=HTMLResponse)
async def post_center(
    request: Request,
    category: Optional[str] = None,
    page: int = 1
):
    """
    显示帖子列表中心，支持分类
    """
    from jinja2 import ChoiceLoader, FileSystemLoader
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")
    templates.env.loader = ChoiceLoader([FileSystemLoader("templates")])
    templates.env.cache = {}
    posts = await post_service.get_paged_posts(category, page)
    
    # 获取热门帖子（侧边栏热搜榜前10）
    hot_posts = await post_service.get_hot_posts(limit=10)
    
    return templates.TemplateResponse(
        "post_center.html",
        {
            "request": request,
            "posts": posts,
            "hot_posts": hot_posts,
            "current_category": category,
            "page": page
        }
    )

# 2. 帖子详情页 - 支持 /posts/{post_id} 和 /post_detail/{post_id} 两个路由
@post_router.get("/posts/{post_id}", response_class=HTMLResponse)
@post_router.get("/post_detail/{post_id}", response_class=HTMLResponse)
async def post_detail(request: Request, post_id: int):
    """
    显示帖子详情和评论列表
    """
    from jinja2 import ChoiceLoader, FileSystemLoader
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")
    templates.env.loader = ChoiceLoader([FileSystemLoader("templates")])
    templates.env.cache = {}
    post = await post_service.get_post_detail(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")
    
    # 在 Router 层获取根评论，Service 层处理楼中楼逻辑
    # 这里只获取根评论
    comments = await post.comments.filter(parent=None).prefetch_related("user", "replies__user")
    
    return templates.TemplateResponse(
        "post_detail.html",
        {
            "request": request,
            "post": post,
            "comments": comments
        }
    )

# 3. 发帖页面
@post_router.get("/post", response_class=HTMLResponse)
async def create_post_page(request: Request):
    """
    显示发帖页面
    """
    from jinja2 import ChoiceLoader, FileSystemLoader
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")
    templates.env.loader = ChoiceLoader([FileSystemLoader("templates")])
    templates.env.cache = {}
    # 权限检查
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    
    return templates.TemplateResponse("post.html", {"request": request})

# 4. 处理发帖提交
from fastapi import File, UploadFile
import os
import uuid

@post_router.post("/posts/create")
async def create_post_action(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    category: str = Form(...),
    is_sticky: bool = Form(False),
    files: list[UploadFile] = File(None)
):
    """
    处理发帖请求
    """
    from jinja2 import ChoiceLoader, FileSystemLoader
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")
    templates.env.loader = ChoiceLoader([FileSystemLoader("templates")])
    templates.env.cache = {}
    user_data = request.session.get("user")
    if not user_data:
        raise HTTPException(status_code=401, detail="请先登录")

    # 处理图片上传
    image_urls = []
    if files:
        upload_dir = "static/uploads"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        allowed_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')

        for file in files:
            if not file or not file.filename:
                continue

            if not file.filename.lower().endswith(allowed_extensions):
                print(f"DEBUG: 跳过非图片文件: {file.filename}")
                continue

            filename = f"{uuid.uuid4()}_{file.filename}"
            file_path = os.path.join(upload_dir, filename)

            try:
                file_content = await file.read()
                if not file_content:
                    print(f"DEBUG: 文件内容为空: {file.filename}")
                    continue

                with open(file_path, "wb") as buffer:
                    buffer.write(file_content)

                image_url = f"/static/uploads/{filename}"
                image_urls.append(image_url)
                print(f"DEBUG: 保存文件成功: {file_path}")
                print(f"DEBUG: 添加图片URL: {image_url}")
            except Exception as e:
                print(f"DEBUG: 保存文件失败: {e}")
    print(f"DEBUG: 最终图片URL列表: {image_urls}")

    
    await post_service.create_post(
        user_id=user_data["id"],
        title=title,
        content=content,
        category=category,
        is_sticky=is_sticky,
        image_urls=image_urls
    )
    return templates.TemplateResponse("post.html", {"request": request, "success": True})

# 5. 编辑帖子
@post_router.get("/post/edit/{post_id}", response_class=HTMLResponse)
async def edit_post_page(request: Request, post_id: int):
    """
    显示编辑帖子页面
    """
    from jinja2 import ChoiceLoader, FileSystemLoader
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")
    templates.env.loader = ChoiceLoader([FileSystemLoader("templates")])
    templates.env.cache = {}
    user_data = request.session.get("user")
    if not user_data:
        return RedirectResponse(url="/login", status_code=303)
    
    post = await post_service.get_post_detail(post_id)
    if not post or post.user.id != user_data["id"]:
        raise HTTPException(status_code=403, detail="无权编辑该帖子")
    
    return templates.TemplateResponse("post.html", {"request": request, "post": post})

# 6. 删除帖子
@post_router.post("/post/delete/{post_id}")
async def delete_post_action(request: Request, post_id: int):
    """
    处理删除帖子请求
    """
    user_data = request.session.get("user")
    if not user_data:
        raise HTTPException(status_code=401, detail="请先登录")
    
    success = await post_service.delete_post(post_id, user_data["id"])
    if not success:
        raise HTTPException(status_code=403, detail="删除失败")
    
    return RedirectResponse(url="/my_posts", status_code=303)

# 8. 更新帖子
@post_router.post("/posts/update/{post_id}")
async def update_post_action(
    request: Request,
    post_id: int,
    title: str = Form(...),
    content: str = Form(...),
    category: str = Form(...),
    is_sticky: bool = Form(False),
    files: list[UploadFile] = File(None)
):
    """
    处理更新帖子请求
    """
    from jinja2 import ChoiceLoader, FileSystemLoader
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")
    templates.env.loader = ChoiceLoader([FileSystemLoader("templates")])
    templates.env.cache = {}
    user_data = request.session.get("user")
    if not user_data:
        raise HTTPException(status_code=401, detail="请先登录")

    # 处理图片上传
    image_urls = []
    if files:
        upload_dir = "static/uploads"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        allowed_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')

        for file in files:
            if not file or not file.filename:
                continue

            if not file.filename.lower().endswith(allowed_extensions):
                print(f"DEBUG: 跳过非图片文件: {file.filename}")
                continue

            filename = f"{uuid.uuid4()}_{file.filename}"
            file_path = os.path.join(upload_dir, filename)

            try:
                file_content = await file.read()
                if not file_content:
                    print(f"DEBUG: 文件内容为空: {file.filename}")
                    continue

                with open(file_path, "wb") as buffer:
                    buffer.write(file_content)

                image_url = f"/static/uploads/{filename}"
                image_urls.append(image_url)
                print(f"DEBUG: 保存文件成功: {file_path}")
                print(f"DEBUG: 添加图片URL: {image_url}")
            except Exception as e:
                print(f"DEBUG: 保存文件失败: {e}")
    print(f"DEBUG: 最终图片URL列表: {image_urls}")

    # 更新帖子
    post = await post_service.update_post(
        post_id=post_id,
        user_id=user_data["id"],
        title=title,
        content=content,
        category=category
    )
    
    # 如果有新上传的图片，更新图片URLs
    if image_urls:
        post.image_urls = image_urls
        await post.save()
    
    return templates.TemplateResponse("post.html", {"request": request, "post": post, "success": True})

# 7. 我的帖子
@post_router.get("/my_posts", response_class=HTMLResponse)
async def my_posts(request: Request, page: int = 1):
    """
    显示当前用户的帖子列表
    """
    from jinja2 import ChoiceLoader, FileSystemLoader
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")
    templates.env.loader = ChoiceLoader([FileSystemLoader("templates")])
    templates.env.cache = {}
    
    # 获取当前登录用户
    user_data = request.session.get("user")
    if not user_data:
        return RedirectResponse(url="/login", status_code=303)
    
    # 查询当前用户的帖子
    from app.models.post import Post
    posts = await Post.filter(user_id=user_data["id"]).prefetch_related("user").order_by("-created_at")
    
    # 分页处理
    page_size = 10
    total = len(posts)
    start = (page - 1) * page_size
    end = start + page_size
    paged_posts = posts[start:end]
    
    return templates.TemplateResponse(
        "my_post.html",
        {
            "request": request,
            "posts": paged_posts,
            "page": page,
            "total": total,
            "page_size": page_size
        }
    )