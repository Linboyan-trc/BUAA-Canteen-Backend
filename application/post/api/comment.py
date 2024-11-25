# 作者: toryn
# 时间: 2024/11/25
from django.views.decorators.http import require_POST, require_http_methods, require_GET
from django.core.paginator import Paginator
from django.db.models import Count

from ...user.models import User
from ..models import Post, Comment
from ...user.api.user_auth import jwt_auth
from ...utils import *


################################################################################
# 1. 主评论
@response_wrapper
@require_POST
@jwt_auth()
def comment_main(request: HttpRequest):
    # 1.1 解析request body
    data = parse_request_data(request)

    # 1.2 获取request body中的键:'post_id', 'content'
    post_id = data.get('post_id')
    content = data.get('content')

    # 1.3 要求'post_id', 'content'必填
    if not post_id or not content:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGUMENT_ERROR, "缺少必要的参数")

    # 1.4 检查帖子是否存在
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGUMENT_ERROR, "帖子不存在")

    # 1.5 根据jwt_auth()获取当前用户
    user = request.user

    # 1.6 创建评论
    comment = Comment.objects.create(refer_post=post, content=content, author=user)
    return success_api_response({
        "info": "评论已发送！",
        "id": comment.id
    })


# 2. 回复评论
@response_wrapper
@require_POST
@jwt_auth()
def comment_reply(request: HttpRequest):
    # 1.1 解析request body
    data = parse_request_data(request)

    # 1.2 获取request body中的键:'post_id', 'parent_comment_id', 'content'
    post_id = data.get('post_id')
    comment_id = data.get('parent_comment_id')
    content = data.get('content')

    # 1.3 要求'post_id', 'parent_comment_id', 'content'必填
    if not post_id or not comment_id or not content:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGUMENT_ERROR, "缺少必要的参数")

    # 1.4 检查帖子是否存在
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGUMENT_ERROR, "帖子不存在")

    # 1.5 检查评论是否存在
    try:
        parent_comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGUMENT_ERROR, "父评论不存在")

    # 1.6 根据jwt_auth()获取当前用户
    user = request.user

    # 1.7 创建评论
    comment = Comment.objects.create(refer_post=post, refer_to=parent_comment, content=content, author=user)
    return success_api_response({
        "info": "回复已发送！",
        "id": comment.id
    })


################################################################################
@response_wrapper
@require_POST
def get_main_comments(request: HttpRequest):
    data = parse_request_data(request)

    post_id = data.get('id')
    offset = int(data.get('offset', 0))

    offset = int(offset)
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGUMENT_ERROR, "帖子不存在")

    comments = Comment.objects.filter(refer_post=post, refer_to__isnull=True).order_by('-created_at')
    comments = comments[offset:offset + 10]

    comment_list = []
    for comment in comments:
        reply_count = Comment.objects.filter(refer_to=comment).count()
        comment_list.append({
            "id": comment.id,
            "content": comment.content,
            "createTime": comment.created_at.strftime('%Y-%m-%d %H:%M'),
            "user": {
                "id": comment.author.id,
                "username": comment.author.username,
                "avatar": comment.author.avatar.url
            },
            "replyCount": reply_count,
        })

    return success_api_response({
        "info": comment_list
    })


@response_wrapper
@require_POST
def get_reply_comments(request: HttpRequest):
    data = parse_request_data(request)

    main_comment_id = data.get('id')
    offset = data.get('offset', 0)

    offset = int(offset)

    try:
        main_comment = Comment.objects.get(id=main_comment_id)
    except Comment.DoesNotExist:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGUMENT_ERROR, "主评论不存在")

    replies = Comment.objects.filter(refer_to=main_comment).order_by('-created_at')
    replies = replies[offset:offset + 10]

    reply_list = []
    for reply in replies:
        reply_list.append({
            "id": reply.id,
            "content": reply.content,
            "createTime": reply.created_at.strftime('%Y-%m-%d %H:%M'),
            "user": {
                "id": reply.author.id,
                "username": reply.author.username,
                "avatar": reply.author.avatar.url
            }
        })

    return success_api_response({
        "info": reply_list,
        "count": len(reply_list)
    })
