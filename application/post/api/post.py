# 作者: toryn
# 时间: 2024/11/25
import re
import random
from datetime import datetime
from django.views.decorators.http import require_POST, require_http_methods, require_GET
from django.db.models import Count
from django.db import transaction
from django.db.models import Q
from haystack.query import SearchQuerySet

from ...user.models import User, PostCollection, EatCollection
from ..models import Post, Comment
from ...cafeteria.models import Counter, Dish
from ...user.api.user_auth import jwt_auth
from ...utils import *



################################################################################
# 1. 获取帖子
@response_wrapper
@require_GET
def get_detail(request: HttpRequest):
    # 1.1 解析request body
    data = parse_request_data(request)

    # 1.2 获取request body中的键:'id'
    post_id = data.get('id')

    # 1.3 获取帖子
    post = Post.objects.get(id=post_id)

    # 1.4 返回响应{id, author:{id, username, avatar},
    # 1.4 {title, content, imgs}
    # 1.4 {被收藏的次数collectCount, 吃过的次数ateCount, 评论的数量commentCount}
    return success_api_response({
        'id': post.id,
        'user': {
            'id': post.author.id,
            'username': post.author.username,
            'avatar': post.author.avatar.url,
        },
        'title': post.title,
        'content': post.content,
        'createTime': post.created_time.strftime('%Y-%m-%d %H:%M:%S'),
        'imgs': re.split(r'[\s\n\r]+', post.images),
        'collectCount': PostCollection.objects.filter(post=post).count(),
        'ateCount': EatCollection.objects.filter(post=post).count(),
        'commentCount': Comment.objects.filter(refer_post=post).count(),
    })

# 2. 上传帖子
@response_wrapper
@require_POST
@jwt_auth()
def upload_info(request: HttpRequest):
    # 2.1 根据jwt_auth()获取当前用户id，然后取出用户
    user = User.objects.get(id=request.user.id)

    # 2.2 解析request body
    data = parse_request_data(request)

    # 2.3 获取request body中的键:'counter_id'
    # 2.3 获取request body中的键:'dish_name', 'dish_price'
    # 2.3 获取request body中的键:'post_title', 'post_content'
    counter_id = data.get('counter_id')
    post_title = data.get('post_title')
    post_content = data.get('post_content')

    # 2.4 要求'counter_id', 'dish_name', 'dish_price', 'post_title'必填
    if not counter_id or not post_title:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGUMENT_ERROR, '缺少必要的参数')

    # 2.5 获取柜台
    counter = Counter.objects.get(id=counter_id)
    if not counter:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGUMENT_ERROR, '窗口不存在')

    if user.is_superuser:
        dish_name = data.get('dish_name')
        dish_price = data.get('dish_price')
        # 2.6 创建dish，将dish关联到柜台
        dish = Dish.objects.create(name=dish_name, price=dish_price, counter=counter)

        # 2.7 创建post，将post关联到dish
        post = Post.objects.create(dish=dish, title=post_title, content=post_content, author=user)
    else:
        dish_id = data.get('dish_id')
        print(data)
        dish = Dish.objects.get(id=dish_id)

        # 2.7 创建post，将post关联到dish
        post = Post.objects.create(dish=dish, title=post_title, content=post_content, author=user)

    # 2.8 返回响应
    return success_api_response({
        'info': '上传成功',
        'id': post.id
    })


# 3. 上传图片
@response_wrapper
@require_POST
@jwt_auth()
def upload_image(request):
    # 3.1 根据jwt_auth()获取当前用户id，然后取出用户
    user = User.objects.get(id=request.user.id)

    # 3.2 获取request body中的键:'id', 'file'
    post_id = request.POST.get('id')
    image = request.FILES.get('file')

    # 3.3 要求'id', 'file'必填
    if post_id is None or not image:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGUMENT_ERROR, '缺少必要的参数')

    # 3.4 上传file，获取新的图片的img_url
    img_url = upload_img_file(image, folder='post')
    if not img_url:
        return failed_api_response(ErrorCode.SERVER_ERROR, '图片上传失败')

    # 3.5 使用事务确保数据一致性
    with transaction.atomic():
        # 3.5.1 获取帖子
        try:
            post = Post.objects.select_for_update().get(id=post_id)
        except Post.DoesNotExist:
            return failed_api_response(ErrorCode.INVALID_REQUEST_ARGUMENT_ERROR, '帖子不存在')

        # 3.5.2 检查作者
        if post.author != user:
            return failed_api_response(ErrorCode.REFUSE_ACCESS_ERROR, '无权操作')

        # 3.5.3 确保获取最新的 post 实例
        post.refresh_from_db()

        # 3.5.4 加上新的图片img_url
        if post.images:
            post.images += ' ' + img_url
        else:
            post.images = img_url

        print('拼接后的图片URL:', post.images)  # 打印调试信息
        post.save()

    # 3.6 返回响应
    return success_api_response({
        'info': '上传成功',
        'id': post.id,
        'image_url': img_url
    })


# 4. 删除帖子
@response_wrapper
@require_POST
@jwt_auth()
def delete_post(request: HttpRequest):
    # 4.1 根据jwt_auth()获取当前用户id，然后取出用户
    user = User.objects.get(id=request.user.id)

    # 4.2 解析request body
    data = parse_request_data(request)

    # 4.3 获取request body中的键:'id'
    post_id = data.get('id')

    # 4.4 要求'id'必填
    if post_id is None:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGUMENT_ERROR, '缺少必要的参数')

    # 4.5 帖子需要存在
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGUMENT_ERROR, '帖子不存在')

    # 4.6 检查作者
    if post.author != user:
        return failed_api_response(ErrorCode.REFUSE_ACCESS_ERROR, '无权操作')

    # 4.7 删除帖子
    post.delete()

    # 4.8 返回响应
    return success_api_response({'info': '删除成功'})


# 5. 获取所有帖子
@response_wrapper
@require_GET
def get_all_posts(request: HttpRequest):
    posts = Post.objects.exclude(author__is_superuser=True)

    return success_api_response({
        'posts': [{
            'id': post.id,
            'name': post.title,
            'img': re.split(r'[\s\n\r]+', post.images)[0],
            'user': {
                'id': post.author.id,
                'username': post.author.username,
                'avatar': post.author.avatar.url,
            },
            'collectCount': PostCollection.objects.filter(post=post).count(),
            'ateCount': EatCollection.objects.filter(post=post).count(),
        } for post in posts]
    })

################################################################################

def get_recommended_posts(offset=0, limit=10, is_breakfast=False):
    offset = int(offset)
    limit = int(limit)

    # 获取推荐的帖子
    recommended_posts = Post.objects \
        .annotate(collect_count=Count('collected_by'), eat_count=Count('eaten_by')) \
        .annotate(comment_count=Count('comments')) \
        .order_by('-collect_count', '-eat_count', '-comment_count')

    # 将结果转换为列表并根据热度排序
    sorted_recommended_posts = sorted(recommended_posts, key=lambda post: (post.collect_count,
                                                                           post.eat_count,
                                                                           post.comment_count),
                                      reverse=True)

    # 取出高赞的帖子75个，剩下的都是低赞，打乱顺序返回，保证高赞的在低赞前面
    high = []
    if is_breakfast:
        counter = Counter.objects.get(id=36)
        dishes = Dish.objects.filter(counter=counter)
        for dish in dishes:
            posts = Post.objects.filter(dish=dish)
            for post in posts:
                high.append(post)
    else:
        high = sorted_recommended_posts[:75]
    low = sorted_recommended_posts[75:]

    random.shuffle(high)
    random.shuffle(low)

    sorted_recommended_posts = high[:10] + low

    # 返回指定范围内的推荐帖子
    return sorted_recommended_posts[offset:offset + limit]


@response_wrapper
@require_GET
def get_recommend(request: HttpRequest):
    data = parse_request_data(request)
    offset = data.get('offset', 0)

    offset = int(offset)

    limit = 20

    # 如果是早上，则推荐早餐帖子
    if 6 <= datetime.now().hour < 10:
        recommended_posts = get_recommended_posts(offset, limit, True)
    else:
        recommended_posts = get_recommended_posts(offset, limit)

    return success_api_response({
        'posts': [{
            'id': post.id,
            'name': post.title,
            'img': re.split(r'[\s\n\r]+', post.images)[0],
            'user': {
                'id': post.author.id,
                'username': post.author.username,
                'avatar': post.author.avatar.url,
            },
            'collectCount': PostCollection.objects.filter(post=post).count(),
            'ateCount': EatCollection.objects.filter(post=post).count(),
        } for post in recommended_posts]
    })



@response_wrapper
@require_GET
def search(request: HttpRequest):
    query = request.GET.get('query')
    if query:
        posts = Post.objects.filter(Q(content__contains=query) | Q(title__contains=query) | Q(dish__name__contains=query) ).distinct()
        posts_info = []
        for post in posts[0:20]:
            posts_info.append({
                'id': post.id,
                'name': post.title,
                'img': re.split(r'[\s\n\r]+', post.images)[0],
                'user': {
                    'id': post.author.id,
                    'username': post.author.username,
                    'avatar': post.author.avatar.url,
                },
                'collectCount': PostCollection.objects.filter(post=post).count(),
                'ateCount': EatCollection.objects.filter(post=post).count(),
            })

    return success_api_response({'posts': posts_info})
