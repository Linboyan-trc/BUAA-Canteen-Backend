# 作者: toryn
# 时间: 2024/11/25
import re
from django.contrib.auth import authenticate, logout
from django.views.decorators.http import require_POST, require_http_methods, require_GET
from django.utils import timezone
from .user_auth import create_access_token, create_refresh_token, jwt_auth
from ..models import User, Auth
from ...utils import *


################################################################################
# 1. 注册
@response_wrapper
@require_POST
def user_register(request: HttpRequest):
    # 1.1 解析request body
    data = parse_request_data(request)

    # 1.2 获取request body中的键:'username', 'email', 'password'
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # 1.3 要求'username', 'email', 'password'必填
    if not username or not password or not email:
        return failed_api_response(ErrorCode.REQUIRED_ARG_IS_NULL_ERROR, '内容未填写完整')

    # 1.4 要求'username'唯一
    if User.objects.filter(username=username).exists():
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGUMENT_ERROR, '用户名已存在')

    # 1.5 要求用户名可以是数字，大小写字母，下划线，长度为[5,15]
    pattern = r'^[0-9a-zA-Z_\-\u4e00-\u9fa5]{3,15}$'
    if not re.match(pattern, username):
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGUMENT_ERROR, '用户名需为5-15位字母、数字或下划线')

    # 1.6 要求'email'唯一
    if User.objects.filter(email=email).exists():
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGUMENT_ERROR, '邮箱已存在')

    # 1.7 创建用户
    User.objects.create_user(username=username, password=password, email=email)

    # 1.8 返回响应
    return success_api_response({'message': '注册成功'})


# 2. 登录
@require_POST
@response_wrapper
def user_login(request: HttpRequest):
    # 2.1 解析request body
    data = parse_request_data(request)

    # 2.2 获取request body中的键:'email', 'password'
    email = data.get('email')
    password = data.get('password')

    # 2.3 要求email', 'password'必填
    if not email or not password:
        return failed_api_response(ErrorCode.REQUIRED_ARG_IS_NULL_ERROR, '内容未填写完整')

    # 2.4 去数据库中检索用户
    print(email, password)
    user = authenticate(username=email, password=password)
    print("...")

    # 2.5.1 检索不存在，但是'email'字段存在，则是密码错误
    # 2.5.1 检索不存在，并且'email'字段不存在，则是邮箱不存在
    # 2.5.2 检索存在，但是'isDelete'字段为true，则是用户已注销
    # 2.5.2 检索存在，并且'isDelete'字段为false，则是登录成功，返回{username, token,refresh_token}
    if user is None:
        if User.objects.filter(email=email).exists():
            return failed_api_response(ErrorCode.CANNOT_LOGIN_ERROR, '密码错误')
        return failed_api_response(ErrorCode.CANNOT_LOGIN_ERROR, '邮箱不存在')

    if user.isDelete:
        return failed_api_response(ErrorCode.CANNOT_LOGIN_ERROR, '用户已注销, 请联系管理员')
    token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    return success_api_response({'message': '登录成功',
                                 'username': user.username,
                                 'token': token,
                                 'refresh_token': refresh_token})


# 3. 登出
# 3.1 jwt_auth()中会在请求中添加键'user',通过request.user.id可以获取当前用户的id
@response_wrapper
@jwt_auth()
@require_POST
def user_logout(request: HttpRequest):
    # 3.1 删除user_auth中的登录记录即可
    Auth.objects.filter(user=request.user).delete()
    return success_api_response({'message': '登出成功'})


# 4. 注销账号
@response_wrapper
@jwt_auth()
@require_http_methods(['DELETE'])
def user_delete(request: HttpRequest):
    # 4.1 根据jwt_auth()获取当前用户id，然后取出用户
    user = User.objects.get(id=request.user.id)

    # 4.2 如果不是默认头像，就删除头像
    if user.avatar != 'media/avatar/default.png':
        user.avatar.delete()

    # 4.3 登出用户
    logout(request)

    # 4.4 重新设置用户的introduction, avatar为默认值，设置isDelete为真
    user.intorduction = '用户已注销'
    user.avatar = 'media/avatar/default.png'
    user.isDelete = True
    user.save()

    # 4.5 删除user_auth中的登录记录
    Auth.objects.filter(user=user).delete()

    # 4.6 返回响应
    return success_api_response({'message': '注销成功'})


################################################################################
# 1. 修改头像
@response_wrapper
@jwt_auth()
@require_POST
def user_change_avatar(request: HttpRequest):
    # 1.1 根据jwt_auth()获取当前用户id，然后取出用户
    user = User.objects.get(id=request.user.id)

    # 1.2 请求体中中的Files没有键'avatar'，则头像未上传
    if 'avatar' not in request.FILES:
        return failed_api_response(ErrorCode.REQUIRED_ARG_IS_NULL_ERROR, '头像未上传')

    # 1.3 获取请求体中新的头像
    new_avatar = request.FILES['avatar']

    # 1.4.1 如果用户当前的头像不是默认头像，就删除头像
    # 1.4.2 设置新头像的文件名为"<username>_<YYYYMMDDHHMMSS>.png"
    # 1.4.2 设置用户的新头像为新文件的路径
    if new_avatar:
        if user.avatar and user.avatar.name != 'avatar/default.png':
            user.avatar.delete(save=False)
        new_avatar.name = f"{user.username}_{timezone.now().strftime('%Y%m%d%H%M%S')}.png"
        user.avatar = new_avatar
        user.save()

    # 1.5 如果从请求体的Files中获取'avatar'键为空，则头像未上传
    else:
        return failed_api_response(ErrorCode.REQUIRED_ARG_IS_NULL_ERROR, '头像未上传')

    # 1.6 返回一个响应{url}
    return success_api_response({'message': '头像修改成功', 'url': user.avatar.url})


# 2. 修改密码
@response_wrapper
@jwt_auth()
@require_POST
def user_change_password(request: HttpRequest):
    # 2.1 根据jwt_auth()获取当前用户id，然后取出用户
    user = User.objects.get(id=request.user.id)

    # 2.2 解析request body
    data = parse_request_data(request)

    # 2.3 获取request body中的键:'old_password', 'new_password'
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    # 2.4 要求'old_password', 'new_password'必填
    if not old_password or not new_password:
        return failed_api_response(ErrorCode.REQUIRED_ARG_IS_NULL_ERROR, '内容未填写完整')

    # 2.5 用'user.email', 'old_password'获取用户
    user = authenticate(username=user.email, password=old_password)

    # 2.6 如果获取为空，则密码错误
    if user is None:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGUMENT_ERROR, '原密码错误')

    # 2.7 设置用户密码为'new_password'
    user.set_password(new_password)
    user.save()

    # 2.8 返回响应
    return success_api_response({'message': '密码修改成功'})


# 3. 修改用户信息
@response_wrapper
@jwt_auth()
@require_http_methods(['PUT'])
def user_change_info(request: HttpRequest):
    # 3.1 根据jwt_auth()获取当前用户id，然后取出用户
    user = User.objects.get(id=request.user.id)

    # 3.2 解析request body
    data = parse_request_data(request)

    # 3.3 获取request body中的键:'username', 'email', 'gender', 'introduction'
    username = data.get('username')
    email = data.get('email')
    gender = data.get('gender')
    introduction = data.get('introduction')

    # 3.4 要求'username'不和其他用户重复
    # 3.4 要求'username'是数字，大小写字母，下划线，长度为[5,15]
    # 3.4 修改用户名
    if username:
        if username != user.username:
            if User.objects.filter(username=username).exists():
                return failed_api_response(ErrorCode.INVALID_REQUEST_ARGUMENT_ERROR, '用户名已存在')
            pattern = r'^[0-9a-zA-Z_\-\u4e00-\u9fa5]{3,15}$'
            if not re.match(pattern, username):
                return failed_api_response(ErrorCode.INVALID_REQUEST_ARGUMENT_ERROR,
                                           '用户名需为5-15位字母、数字或下划线')
            user.username = username

    # 3.5 要求'email'不和其他用户重复
    # 3.5 修改邮箱
    if email:
        if email != user.email:
            if User.objects.filter(email=email).exists():
                return failed_api_response(ErrorCode.INVALID_REQUEST_ARGUMENT_ERROR, '邮箱已存在')
            user.email = email

    # 3.6 修改gender
    if gender:
        user.gender = gender

    # 3.7 修改introduction
    if introduction:
        user.introduction = introduction
    user.save()

    # 3.8 返回响应
    return success_api_response({'message': '信息修改成功'})


################################################################################
# 1. 获取用户信息
@response_wrapper
@jwt_auth()
@require_GET
def user_get_info(request: HttpRequest):
    # 3.1 根据jwt_auth()获取当前用户id，然后取出用户
    user = User.objects.get(id=request.user.id)

    # 3.2 返回响应{id, username, email, gender, introduction, avatar}
    return success_api_response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_superuser': user.is_superuser,
        'gender': user.gender,
        'introduction': user.introduction,
        'avatar': user.avatar.url,
    })


# 2. 获取用户信息
@response_wrapper
@jwt_auth()
@require_GET
def user_get_info_by_id(request: HttpRequest, user_id: int):
    # 2.1 根据url中<int:user_id>获取用户
    target_user = User.objects.filter(id=user_id)

    # 2.2 没有获取到用户，则用户不存在
    if not target_user.exists():
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGUMENT_ERROR, '用户不存在')

    # 2.3 返回响应{id, username, email, gender, introduction, avatar}
    return success_api_response({
        'id': target_user[0].id,
        'username': target_user[0].username,
        'email': target_user[0].email,
        'gender': target_user[0].gender,
        'introduction': target_user[0].introduction,
        'avatar': target_user[0].avatar.url,
    })
