# 作者: toryn
# 时间: 2024/11/25
"""
采用jwt令牌生成双token，一个用于认证，一个用于刷新
"""

import jwt
from django.utils import timezone
from django.views.decorators.http import require_POST


from ..models import User, Auth
from ...utils import *


@response_wrapper
@require_POST
def refresh_token(request: HttpRequest):
    """
    刷新token
    """
    try:
        # 获取请求头中的refresh_token
        head = request.META.get('HTTP_AUTHORIZATION')
        if not head:
            print('token无效 in refresh_token')
            raise jwt.InvalidTokenError
        # 解析token
        refresh_auth_info = head.split(' ')
        if len(refresh_auth_info) != 2:
            raise jwt.InvalidTokenError
        auth_type, token = refresh_auth_info
        if auth_type != 'Bearer':
            raise jwt.InvalidTokenError
        # 验证token，获得负载
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.InvalidTokenError as exc:
            print('token无效 in refresh_token')
            raise jwt.InvalidTokenError from exc
        # 检查token类型
        if payload.get('type') != 'refresh_token':
            raise jwt.InvalidTokenError
        # 获取用户和认证信息
        user_id = payload.get('user_id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist as exc:
            raise jwt.InvalidTokenError from exc
        auth_id = payload.get('auth_id')
        try:
            auth = Auth.objects.get(id=auth_id)
        except Auth.DoesNotExist as exc:
            raise jwt.InvalidTokenError from exc
        if auth is None or auth.user != user:
            raise jwt.InvalidTokenError
        if auth.expires_at < timezone.now():
            raise jwt.InvalidTokenError
        # 创建新的认证信息
        token = create_access_token(user)
        return success_api_response({'token': token,})
    except jwt.InvalidTokenError:
        return failed_api_response(ErrorCode.INVALID_REFRESH_TOKEN_ERROR, '登陆过期，refresh_token无效，请重新登陆')


def get_user(request) -> User | None:
    head = request.META.get('HTTP_AUTHORIZATION')
    try:
        if not head:
            raise jwt.InvalidTokenError
        auth_info = head.split(' ')
        if len(auth_info) != 2:
            raise jwt.InvalidTokenError
        auth_type, token = auth_info
        if auth_type != 'Bearer':
            raise jwt.InvalidTokenError
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.InvalidTokenError as exc:
            print('token无效 in get_user')
            raise jwt.InvalidTokenError from exc
        if payload.get('type') != 'access_token':
            raise jwt.InvalidTokenError
        user_id = payload.get('user_id')
        user = User.objects.get(id=user_id)
        if user is None:
            raise jwt.InvalidTokenError
        return user
    except jwt.InvalidTokenError:
        return None


def jwt_auth(allow_anonymous=False):
    """
    jwt认证装饰器
    :param allow_anonymous: 是否允许匿名访问
    """
    def decorator(api):
        def wrapper(request, *args, **kwargs):
            user = get_user(request)
            if user is None or user.isDelete:
                if not allow_anonymous:
                    return failed_api_response(ErrorCode.UNAUTHORIZED_ERROR, 'jwt认证失败，请尝试refresh_token或重新登陆')
            request.user = user
            return api(request, *args, **kwargs)
        return wrapper
    return decorator


def create_access_token(user: User, access_token_delta: int = 1) -> str:
    """
    创建access token
    :param user: 用户
    :param access_token_delta: access token有效期  默认1小时
    """

    current_time = timezone.now()
    access_token_payload = {
        'user_id': user.id,
        'type': 'access_token',
        'exp': current_time + timezone.timedelta(hours=access_token_delta)
    }
    access_token = jwt.encode(access_token_payload, settings.SECRET_KEY, algorithm='HS256')
    if isinstance(access_token, bytes):
        access_token = access_token.decode('utf-8')
    return access_token


def create_refresh_token(user: User, refresh_token_delta: int = 7) -> str:
    """
    创建refresh token
    :param user: 用户
    :param refresh_token_delta: refresh token有效期  默认7天
    """
    current_time = timezone.now()

    # 删除旧的refresh token
    Auth.objects.filter(user=user).delete()

    auth = Auth.objects.create(user=user, login_at=current_time,
                               expires_at=current_time + timezone.timedelta(days=refresh_token_delta))
    refresh_token_payload = {
        'user_id': user.id,
        'type': 'refresh_token',
        'auth_id': auth.id,
    }
    refreshed_token = jwt.encode(refresh_token_payload, settings.SECRET_KEY, algorithm='HS256')
    if isinstance(refreshed_token, bytes):
        refreshed_token = refreshed_token.decode('utf-8')
    return refreshed_token
