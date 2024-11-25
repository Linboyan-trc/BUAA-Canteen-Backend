# 作者: toryn
# 时间: 2024/11/25
import re
from django.views.decorators.http import require_POST, require_http_methods, require_GET

from ...user.models import User, CafeteriaCollection, CounterCollection, PostCollection, EatCollection
from ..models import Cafeteria, Counter, Dish
from ...post.models import Post
from ...user.api.user_auth import jwt_auth
from ...utils import *


################################################################################
# 1. 获取所有食堂
@response_wrapper
@require_GET
def get_all_cafeterias(request: HttpRequest):
    # 1.1 获取所有食堂
    cafeterias = Cafeteria.objects.all()

    # 1.2 组织成[{},{}]
    # 1.2.1 {}:id, name, img, 被收藏的次数collectCount
    cafeterias_info = []
    for cafeteria in cafeterias:
        cafeterias_info.append({
            'id': cafeteria.id,
            'name': cafeteria.name,
            'img': cafeteria.image.url,
            'collectCount': CafeteriaCollection.objects.filter(cafeteria=cafeteria).count(),
        })

    # 1.3 返回响应
    return success_api_response({
        'info': cafeterias_info
    })


# 2. 获取食堂/所有柜台
@response_wrapper
@require_GET
def get_counters(request: HttpRequest):
    # 2.1 解析request body
    data = parse_request_data(request)

    # 2.2 获取request body中的键:'cafeteriaId'
    cafeteria_id = data.get('cafeteriaId')

    # 2.3 要求'cafeteriaId'必填
    if not cafeteria_id:
        return failed_api_response(ErrorCode.REQUIRED_ARG_IS_NULL_ERROR, '为传入食堂名')

    # 2.4 获取cafeteria
    cafeteria = Cafeteria.objects.get(id=cafeteria_id)
    if not cafeteria:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGUMENT_ERROR, '食堂不存在')

    # 2.5 获取所有柜台
    counters = Counter.objects.filter(cafeteria=cafeteria)

    # 2.6 组织成[{},{}]
    # 2.6.1 {}:id, name, img, floor, 被收藏的次数collectCount
    counters_info = []
    for counter in counters:
        counters_info.append({
            'id': counter.id,
            'name': counter.name,
            'img': counter.image.url,
            'floor': counter.floor,
            'collectCount': CounterCollection.objects.filter(counter=counter).count(),
        })

    # 2.7 返回响应
    return success_api_response({
        "info": counters_info
    })


# 3. 获取柜台/所有菜品的管理员帖子
@response_wrapper
@require_GET
def get_dishes(request: HttpRequest):
    # 3.1 解析request body
    data = parse_request_data(request)

    # 3.2 获取request body中的键:'counterId'
    counter_id = data.get('counterId')
    if not counter_id:
        return failed_api_response(ErrorCode.REQUIRED_ARG_IS_NULL_ERROR, '未传入窗口id')

    # 3.3 获取counter
    counter = Counter.objects.get(id=counter_id)
    if not counter:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGUMENT_ERROR, '窗口不存在')

    # 3.4 获取所有菜品
    dishes = Dish.objects.filter(counter=counter)

    # 3.5 获取每道菜品对应的所有帖子，第一个帖子是官方上传的，其他帖子是用户发布的
    # 3.5 组织成[{},{}]
    # 3.5.1 {}:post_id, name, img, 帖子被收藏的次数，帖子被吃过的次数，上传的用户user:{id, username, avatar}
    post_info = []
    for dish in dishes:
        post = Post.objects.filter(dish=dish, author__is_superuser=True).first()
        post_info.append({
            'id': post.id,
            'name': post.title,
            'img': re.split(r'[\s\n\r]+', post.images)[0],
            'collectCount': PostCollection.objects.filter(post=post).count(),
            'ateCount': EatCollection.objects.filter(post=post).count(),
            'user': {
                'id': post.author.id,
                'username': post.author.username,
                'avatar': post.author.avatar.url,
            }
        })

    # 3.6 返回响应
    return success_api_response({
        'info': post_info
    })


# 4. 获取柜台/所有菜品
@response_wrapper
@require_GET
def get_dishes_no_posts(request: HttpRequest):
    # 3.1 解析request body
    data = parse_request_data(request)

    # 3.2 获取request body中的键:'counterId'
    counter_id = data.get('counterId')
    if not counter_id:
        return failed_api_response(ErrorCode.REQUIRED_ARG_IS_NULL_ERROR, '未传入窗口id')

    # 3.3 获取counter
    counter = Counter.objects.get(id=counter_id)
    if not counter:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGUMENT_ERROR, '窗口不存在')

    # 3.4 获取所有菜品
    dishes = Dish.objects.filter(counter=counter)

    # 3.5 获取每道菜品对应的所有帖子，第一个帖子是官方上传的，其他帖子是用户发布的
    # 3.5 组织成[{},{}]
    # 3.5.1 {}:post_id, name, img, 帖子被收藏的次数，帖子被吃过的次数，上传的用户user:{id, username, avatar}
    dishes_info = []
    for dish in dishes:
        dishes_info.append({
            'id': dish.id,
            'name': dish.name,
        })

    # 3.6 返回响应
    return success_api_response({
        'info': dishes_info
    })

################################################################################
@response_wrapper
def get_cafeteria(request: HttpRequest):
    """
    获取食堂信息
    """
    data = parse_request_data(request)

    cafeteria_id = data.get('cafeteriaId')
    if not cafeteria_id:
        return failed_api_response(ErrorCode.REQUIRED_ARG_IS_NULL_ERROR, '未传入食堂id')

    cafeteria = Cafeteria.objects.get(id=cafeteria_id)
    if not cafeteria:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGUMENT_ERROR, '食堂不存在')

    return success_api_response({
        'id': cafeteria.id,
        'name': cafeteria.name,
        'img': cafeteria.image.url,
        'collectCount': CafeteriaCollection.objects.filter(cafeteria=cafeteria).count(),
    })


@response_wrapper
@require_GET
def get_counter(request: HttpRequest):
    """
    获取窗口信息
    """
    data = parse_request_data(request)

    counter_id = data.get('counterId')
    if not counter_id:
        return failed_api_response(ErrorCode.REQUIRED_ARG_IS_NULL_ERROR, '未传入窗口id')

    counter = Counter.objects.get(id=counter_id)
    if not counter:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGUMENT_ERROR, '窗口不存在')

    return success_api_response({
        'id': counter.id,
        'name': counter.name,
        'img': counter.image.url,
        'floor': counter.floor,
        'collectCount': CounterCollection.objects.filter(counter=counter).count(),
    })



