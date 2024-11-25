# 作者: toryn
# 时间: 2024/11/25
from django.urls import path
from .api import *

urlpatterns = [
    ################################################################################
    #################### 1. 用户 ####################
    # 1. 登录注册
    path('register/', user_register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('delete/', user_delete, name='delete'),
    #  2. 修改用户信息
    path('change-avatar', user_change_avatar, name='change_avatar'),
    path('change-password', user_change_password, name='change_password'),
    path('change-info', user_change_info, name='change_info'),
    # 3. 获取用户信息
    path('get-info', user_get_info, name='get_info'),
    path('get-info-by-id', user_get_info_by_id, name='get_info_by_id'),

    ################################################################################
    #################### 1. 鉴权 ####################
    path('refresh-token', refresh_token, name='refresh_token'),

    ################################################################################
    #################### 1. 获取收藏 ####################
    path('get-collect-cafeterias-list', get_collect_cafeterias_list, name='get_collect_cafeterias_list'),
    path('get-collect-counters-list', get_collect_counters_list, name='get_collect_counters_list'),
    path('get-collect-dishes-list', get_collect_dishes_list, name='get_collect_dishes_list'),
    path('get-ate-list', get_ate_list, name='get_ate_list'),

    #################### 2. 收藏 ####################
    path('collect-cafeteria', collect_cafeteria, name='collect_cafeteria'),
    path('collect-counter', collect_counter, name='collect_counter'),
    path('ate', eat, name='ate'),
    path('collect-post', collect_post, name='collect_post'),

    #################### 3. 取消收藏 ####################
    path('uncollect-counter', cancel_collect_counter, name='cancel_collect_counter'),
    path('uncollect-cafeteria', cancel_collect_cafeteria, name='cancel_collect_cafeteria'),
    path('no-ate', cancel_eat, name='no_ate'),
    path('uncollect-post', cancel_collect_post, name='cancel_collect_counter'),

    #################### 4. 帖子 ####################
    path('get-post-list', get_post_list, name='get_post_list'),
    path('get-user-action-info', get_user_action_info, name='get_user_action_info'),
]